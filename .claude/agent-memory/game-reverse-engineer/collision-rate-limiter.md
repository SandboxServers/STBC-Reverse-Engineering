# Collision Rate Limiter - Ship__CheckCollisionRateLimit

## Overview (2026-02-24)

**Function**: `Ship__CheckCollisionRateLimit` at `0x005a22a0`
**Vtable slot**: 79 (+0x13C) in the DamageableObject/Ship hierarchy
**Signature**: `bool __thiscall Ship__CheckCollisionRateLimit(void *this, int param_1)`

This is the mechanism that explains the stock game's ~0.04 collisions/sec vs our ~43/sec.

## Where It's Called

The rate limiter is a vtable method called from **Ship__CheckCollision** (vtable slot 84, +0x150) at `0x005af890` (not recognized by Ghidra as a named function). The pipeline is:

```
ProximityManager__Update (0x005a83a0)
  -> ProximityManager__SortAndDetectOverlaps (0x005a8500)  [3x, axes]
  -> ProximityManager__ProcessOverlapPairs (0x005a8740)
     -> ProximityManager__DispatchCollisionByType (0x005a8810)
        -> PhysicsObjectClass__CheckCollision (0x005a88e0)
           calls (*param_1 + 0x148)()  = CollisionTest_A (slot 82)
           calls (*param_1 + 0x150)()  = Ship__CheckCollision (slot 84, at 0x005af890)
              -> Ship__CheckCollisionRateLimit (slot 79, +0x13C)  <- HERE
              If rate limiter returns TRUE:
              -> DamageableObject__CheckCollision (slot 84 base, 0x00594840)
                 -> Ship__CollisionDamageWrapper (slot 85, 0x005b0060)
                    -> Ship__SubsystemDamageDistributor
                    -> DamageableObject__ApplyCollisionDamage
```

## The Rate Limiting Mechanism

### Data Structures (ship fields)

```c
ship + 0x68  = pointer to collision pair hash object (has vtable with hash/compare/insert)
ship + 0x6C  = count of tracked pairs
ship + 0x74  = bucket table pointer (NiAlloc'd array of per-pair entry lists)
ship + 0xEC  = enabled flag (if 0, rate limiter immediately returns false)
```

Each per-pair entry (NiAlloc'd, 0x50 bytes, initialized via FUN_006a8c50):
- `entry[0]` = object ID key (from param_1+8)
- `entry[1]` = last collision time (float, seconds from g_Clock+0x90)
- `entry[2]` = next in chain (linked list in bucket)

### Algorithm

1. **Enable gate**: If `ship+0xEC == 0`, return false immediately.

2. **Per-pair lookup**: Hash `param_1+8` (source object ID) into the ship's pair table.
   - If pair not found: create new entry (lastTime=0), insert it.
   - `pfStack_30` = pointer to `lastCollisionTime` for this pair.

3. **Base cooldown selection** (seconds between allowed collision events per pair):

```
currentTime = g_Clock + 0x90  (game time in seconds)
nPlayers = MultiplayerGame__CountActivePlayers(g_TopWindow)

if IsMultiplayer == 0:  // Single player
  if camera_mode:   // piVar10[0x2d] != 0
    nPlayers < 3:   0.10s
    nPlayers == 3:  0.167s
    nPlayers >= 4:  0.25s
  else:
    SettingsByte2 != 0 and nPlayers > 4:  0.125s (jumps to MP path)
    else:  0.10s

else:  // Multiplayer
  if SettingsByte2 == 0:  // standard MP
    collision_enabled (param_1+0x14 != 0) and nPlayers >= 5:  0.125s
    else:  0.10s
  else:  // collision flag set
    if IsClient == 0 (host):
      nPlayers < 2:  0.10s
      nPlayers == 2:  0.167s, bVar14=true (target-aware)
      nPlayers >= 3:  0.50s, bVar14=true
    else (client):
      nPlayers <= 2:  0.10s
      nPlayers == 3:  0.167s, bVar14=true
      nPlayers >= 4:  0.50s, bVar14=true
```

4. **Time gate**: `elapsed = currentTime - lastCollisionTime[pair]`
   - If `elapsed < cooldown` -> **return false** (rate limited)

5. **Distance scaling** (if other ship exists via `Ship__GetObjectByID`):
   - Skip if: other ship is targeting `this`, or is `this`, or same team mismatch
   - Compute 3D distance between ship world positions

   **Non-camera mode** (standard gameplay):
   ```
   dist < 114:    cooldown unchanged  (close range -- allow)
   114 <= dist < 228:  cooldown *= 2   (medium range -- slow down)
   228 <= dist < 343:  cooldown *= 5   (far range -- rare)
   dist >= 343:   cooldown = FLT_MAX  (INFINITE -- blocked completely)
   ```

   **Camera mode OR MP-SettingsByte2**:
   ```
   dist < 114:   cooldown unchanged
   114 <= dist < 170:  cooldown *= 2
   dist >= 170:  cooldown = FLT_MAX  (blocked)
   ```

   Distance thresholds (all in game units):
   - `_DAT_008942a4` = 114.0 (near)
   - `_DAT_008942ac` = 228.0 (medium, non-camera)
   - `_DAT_008942a8` = 343.0 (far, non-camera)
   - `_DAT_00892004` = 170.0 (far, camera/MP mode) = sensor range max

6. **Target-aware bonus** (when `bVar14=true`, 2+ MP players):
   - `cooldown *= 1.333` (i.e., 33% longer = 25% fewer events)
   - But only if result `< 1.0` (prevents blocking if not truly engaged)

7. **Final decision**:
   - If `elapsed >= finalCooldown`: update `lastCollisionTime = round(elapsed)`, return **true** (allowed)
   - Else: return **false** (suppressed)

## Key Constants

| Address | Value | Role |
|---------|-------|------|
| 0x3dcccccd (immediate) | 0.10s | Base min cooldown |
| 0x3e2b020c (immediate) | 0.167s | 2-player MP cooldown |
| 0x3e800000 (immediate) | 0.25s | 4-player SP cooldown |
| 0x3e000000 (immediate) | 0.125s | 5+ player MP cooldown |
| 0x3f000000 (immediate) | 0.50s | 3+ player MP host cooldown |
| `_DAT_008942a0` = 0x3faaaa8f | 1.333 | Target-aware multiplier |
| `_DAT_008942a4` = 0x42e40000 | 114.0 | Near distance threshold |
| `_DAT_008942a8` = 0x43ab8000 | 343.0 | Far distance threshold (non-camera) |
| `_DAT_008942ac` = 0x43640000 | 228.0 | Medium distance threshold (non-camera) |
| `_DAT_00892004` = 0x43aa0000 | 170.0 | Sensor range / far threshold (camera mode) |
| `_DAT_0088bd58` = 0x40a00000 | 5.0 | Very-far multiplier |
| `_DAT_00888860` = 0x3f800000 | 1.0 | FLT constant = 1.0f (used as "MAX" marker) |

Note: `_DAT_00888860 = 1.0f` is used as `cooldown = FLT_MAX` sentinel (since actual code uses
`pfVar13 = (float *)_DAT_00888860` which is treated as `1.0f` cooldown when directly assigned,
but the subsequent check `pfVar13 * _DAT_008942a0 <= _DAT_00888860` catches this to set
`pfStack_34 = 1.0f` which then blocks the collision since elapsed is never >= 1.0 in that context.
Actually re-reading: _DAT_00888860 = 1.0 is used as the INFINITY sentinel -- once cooldown >= 1.0,
the final check `cooldown <= elapsed` never fires for typical frame times).

## Why Our Server Has ~43/sec

Our headless server is in **IsMultiplayer=1, SettingsByte2=0** mode with collision enabled.
With 2 players (host + 1 client), the base cooldown is **0.10 seconds** per pair.

At 60Hz, the ProximityManager fires every frame. If two ships are continuously overlapping,
the rate limiter allows **at most 10 events/second per pair**. With multiple pairs colliding
simultaneously, this can multiply significantly.

BUT: Our bug was likely that `ship+0xEC` (the enable flag) was being set to 0, making the
rate limiter always return false and bypass (the outer collision check continued anyway due
to the CALLER's logic). OR: the rate limiter was not being called because Ship__CheckCollision
at 0x005af890 was not in the Ghidra database and our DeferredInitObject created ships with
incorrect vtable setup.

## Stock ~0.04/sec Explanation

In stock game with the actual collision rate limiter working:
- 3+ player MP host: 0.5s base cooldown
- Ships typically at range 114+ during combat: cooldown doubles to 1.0s+
- Distance >= 343 units: completely blocked (FLT_MAX)
- Result: ~1 event per pair per second at best, much less during normal gameplay

84 events in 33 minutes = 1 event per 23.6 seconds averaged across all pairs. This matches
ships that only occasionally come close enough (< 114 units) to actually trigger the minimum
cooldown, and spend most of the session at larger distances where collisions are blocked.

## Integration Points for OpenBC

The collision rate limiter is a per-ship, per-pair timer system. OpenBC needs:
1. A hash map from objectID -> lastCollisionTime (per ship instance)
2. The cooldown selection table (mode + playerCount)
3. The distance scaling lookup (4 zones)
4. Clock source: game time in seconds (floating point)

The enable gate at `ship+0xEC` must be set; unclear when/where this is initialized vs cleared.
