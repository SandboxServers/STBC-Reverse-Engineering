> [docs](../README.md) / [gameplay](README.md) / collision-rate-limiting.md

# Collision Rate Limiting — Reverse Engineering Analysis

Complete analysis of the per-pair collision rate limiter that controls how often collision damage events fire between ships. This is the mechanism responsible for the stock game's ~0.04 collisions/sec (vs our headless server's uncapped ~43/sec).

## Overview

The collision system uses a **per-pair timer cooldown** mechanism. Each ship maintains a hash table keyed by other objects' IDs, tracking the last time each pair was allowed to generate a collision event. A configurable cooldown period (based on player count, game mode, and distance) must elapse before the same pair can collide again.

## Call Chain

```
ProximityManager::Update (0x005a83a0)    [every frame]
  → SortAndDetectOverlaps (3x per axis)
  → ProcessOverlapPairs (0x005a8740)
     → DispatchCollisionByType (0x005a8810)
        → PhysicsObjectClass::CheckCollision (0x005a88e0)
           → [vtable+0x148] CollisionTest_A (bounding mesh)
           → [vtable+0x150] Ship::CheckCollision (0x005af890)
              → [vtable+0x13C] Ship::CheckCollisionRateLimit (0x005a22a0)  ← RATE LIMITER
              If rate limiter returns TRUE:
              → DamageableObject::CheckCollision (0x00594840) (full narrow phase)
                 → Ship::CollisionDamageWrapper (0x005b0060) (damage + MP relay)
```

**Key**: Ship::CheckCollision at 0x005af890 is an unrecognized function in Ghidra (9 bytes past 0x005af887). It calls the rate limiter via vtable+0x13C, and the narrow-phase collision only proceeds if the rate limiter allows it.

## Ship::CheckCollisionRateLimit (0x005a22a0)

### Ship Fields

| Offset | Type | Field | Notes |
|--------|------|-------|-------|
| +0xEC | byte | enableFlag | If 0 → rate limiting disabled, function returns false immediately |
| +0x68 | ptr | hashVtable | Hash table vtable object (hash/compare/insert ops) |
| +0x6C | int | entryCount | Number of tracked pairs |
| +0x74 | ptr | bucketTable | Array of chained entry lists |

### Per-Pair Entry

Each pair entry is **0x50 bytes** allocated via NiAlloc(0x50) + zero-initialized:
- `entry[0]`: key (other object's ID)
- `entry[1]`: float — **last allowed collision timestamp** (seconds, from g_Clock+0x90)
- Remaining fields: (unused/zero)

### Algorithm

```c
bool Ship__CheckCollisionRateLimit(Ship *this, CollisionEvent *ev) {
    if (this->enableFlag == 0) return false;  // +0xEC, rate limiting disabled

    float *lastTime = FindOrCreatePairEntry(this, ev->sourceObjectID);

    // Select base cooldown (seconds) based on player count + mode
    float cooldown = ComputeBaseCooldown(nPlayers, mode, ev);

    float elapsed = g_Clock.gameTime - *lastTime;
    if (elapsed < cooldown) return false;  // Still cooling down

    // Distance-based scaling
    Ship *other = GetObjectByID(ev->destObjectID);
    if (other != NULL) {
        float dist = Distance3D(this->worldPos, other->worldPos);
        cooldown = ScaleCooldownByDistance(cooldown, dist, mode);
        if (targetingAware)
            cooldown *= 1.333f;  // 33% penalty if targeting relationship
        if (cooldown * 1.333f <= 1.0f)
            cooldown *= 1.333f;  // Only apply if won't block entirely
    }

    if (elapsed >= cooldown) {
        *lastTime = (float)truncate(elapsed);  // Round down to integer seconds
        return true;  // Allow collision
    }
    return false;
}
```

## Base Cooldown Table

| Mode | Players | Cooldown (seconds) |
|------|---------|-------------------|
| Any (minimum floor) | — | 0.10 |
| SP, camera mode | 3 | 0.167 |
| SP, camera mode | ≥4 | 0.25 |
| MP standard, collision_enabled | ≥5 | 0.125 |
| MP + flag, host | 2 | 0.167 |
| **MP + flag, host** | **≥3** | **0.50** |
| MP + flag, client | 3 | 0.167 |
| MP + flag, client | ≥4 | 0.50 |

In a typical dedicated-server game (MP + ≥3 players + host), the base cooldown is **0.50 seconds per pair**.

## Distance Gates

| Distance (game units) | Non-camera mode | Camera/MP-flag mode |
|-----------------------|-----------------|---------------------|
| < 114 | base cooldown | base cooldown |
| 114–228 | cooldown × 2 | cooldown × 2 |
| 228–343 | cooldown × 5 | **BLOCKED (FLT_MAX)** |
| ≥ 343 | **BLOCKED (FLT_MAX)** | **BLOCKED (FLT_MAX)** |

Ships at ≥343 game units apart are **completely blocked** from generating collision events.

### Distance Constants

| Address | Value | Role |
|---------|-------|------|
| 0x008942a4 | 114.0 | Near threshold |
| 0x008942ac | 228.0 | Medium threshold (non-camera) |
| 0x008942a8 | 343.0 | Far threshold (non-camera) |
| 0x00892004 | 170.0 | Far threshold (camera/MP mode) |
| 0x0088bd58 | 5.0 | Very-far multiplier |

## Why Stock Gets ~0.04/sec and Headless Gets ~43/sec

### Stock game (3-player MP, host):
- Base cooldown: 0.50s per pair
- Ships at range >114 during combat: cooldown → 1.0s or blocked
- Ships at >343 units: blocked entirely
- Only ships in sustained close contact generate events
- Result: ~84 events / 33 minutes = **~0.04/sec**

### Headless server (our DeferredInitObject path):
- **Most likely root cause**: `ship+0xEC` (enableFlag) is zero
- When enableFlag == 0, CheckCollisionRateLimit immediately returns false
- Ship::CheckCollision then falls through to the full damage path unconditionally
- Every bounding sphere overlap generates a collision event every frame
- Result: ~28,504 events / 11 minutes = **~43/sec**

### Probable Fix

The enableFlag at ship+0xEC needs to be set to non-zero. This field is likely initialized during the normal ship spawn path (SetupProperties or AddToSet), which our DeferredInitObject may not fully replicate. Investigation needed to determine:
1. What C++ code sets ship+0xEC during normal ship creation
2. Whether a SWIG accessor exists to set it from Python
3. Whether the hash table at +0x68/+0x74 also needs initialization

## Key Function Reference

| Address | Name | Purpose |
|---------|------|---------|
| 0x005a22a0 | Ship::CheckCollisionRateLimit | Per-pair timer cooldown + distance gate |
| 0x005af890 | Ship::CheckCollision | Calls rate limiter, gates narrow phase |
| 0x005a83a0 | ProximityManager::Update | Sweep-and-prune overlap detection |
| 0x005a8740 | ProcessOverlapPairs | Dispatches each overlap to type handler |
| 0x005a8810 | DispatchCollisionByType | Routes to the correct CheckCollision vtable |
| 0x005a88e0 | PhysicsObjectClass::CheckCollision | Outer collision entry point |
| 0x00594840 | DamageableObject::CheckCollision | Full narrow-phase collision |
| 0x005b0060 | Ship::CollisionDamageWrapper | Damage + MP relay |
