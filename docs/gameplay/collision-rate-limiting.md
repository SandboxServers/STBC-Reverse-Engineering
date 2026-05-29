> [docs](../README.md) / [gameplay](README.md) / collision-rate-limiting.md

---
title: Collision Rate Limiting
type: reference + explanation
audience: re-engineer
validated: 2026-05-28
methodology: FUNCTION_DOC_WORKFLOW_V5
binary:
  name: stbc.exe
  size: 6182400
  base: 0x00400000
status: partial
evidence:
  - claim: "Ship main vtable starts at 0x00894128; slot +0x13C = 0x005A22A0 (rate limiter), slot +0x148 = 0x005A38C0 (identity-compare stub), slot +0x150 = 0x005A3900 (RET-only no-op stub)"
    address: 0x00894128
    function: Ship_vtable
    confidence: high
    note: "Byte-read of slot +0x13C confirms `a0 22 5a 00`. Slots +0x148 and +0x150 do NOT dispatch to 0x005AF890 — see C1."
  - claim: "Ship vtable +0x150 = 0x005A3900 is an 8-byte RET-only stub: MOV ECX,[ESP+0x04] then RET 0xC. Not Ship::CheckCollision."
    address: 0x005A3900
    function: FUN_005A3900
    confidence: high
    note: "C1 — 8-byte body: 8B 4C 24 04 ... C2 0C 00."
  - claim: "Ship vtable +0x148 = 0x005A38C0 is an identity-compare stub (SETZ AL). Not CollisionTest_A."
    address: 0x005A38C0
    function: FUN_005A38C0
    confidence: high
    note: "C1 — short body terminating in SETZ AL; argument-compare boolean."
  - claim: "Actual rate-limiter caller is an unnamed wrapper at ~0x005A26D0 (Ghidra has NOT promoted it to a function this pass). Disasm 0x005A26E9-0x005A26F7 shows MOV EAX,[EDI] → CALL [EAX+0x13C] → TEST AL,AL → JNZ proceed / XOR EAX,EAX + JMP early-return"
    address: 0x005A26D0
    function: FUN_005A26D0
    confidence: high
    note: "C1 — the only `CALL [E?X+0x13C]` against the Ship vtable in the collision pipeline."
  - claim: "0x005AF890 is NOT Ship::CheckCollision and does NOT call vtable+0x13C — disasm 0x005AF890..0x005AF9B8 shows calls to CastToShipClass (0x005AB670), IsLocalPlayerShip (0x005AE140), FUN_005AC4F0, vtable+0x94 (GetWorldTranslation), vtable+0xB0, FUN_005A05A0, FUN_005A14D0, FUN_00594840 — no rate-limiter call"
    address: 0x005AF890
    function: FUN_005AF890
    confidence: high
    note: "C1 — function body byte-walked. Real code starts past a 9-NOP gap from 0x005AF887. Ghidra has not promoted it."
  - claim: "0x005AF890 first instruction reads DAT_0097FA89 (per self-destruct C3, this is GameLive_MP NOT IsHost)"
    address: 0x005AF890
    function: FUN_005AF890
    confidence: high
    note: "Clar4 — global identity per self-destruct doc C3 cascade; rename pending across docs."
  - claim: "Actual Ship-Ship collision dispatch path: FUN_005A88E0 (PhysicsObjectClass::CheckCollision) → FUN_005A8810 (DispatchCollisionByType, routes class 0x8125) → FUN_005A61C0 (Ship-Ship narrow phase) → FUN_005A63A0 (Ship-Ship event publisher posting TGObjPtrEvent)"
    address: 0x005A88E0
    function: PhysicsObjectClass_CheckCollision
    confidence: high
    note: "C1 — replaces the doc's broken vtable+0x150 → 0x005AF890 narrative. Ship-Ship route confirmed by cross-anchor against collision-detection-system."
  - claim: "Ship+0xEC = enableFlag (byte); when 0, Ship::CheckCollisionRateLimit returns false immediately. CLAUDE.md 'Known Issue: collision rate limiting disabled (ship+0xEC=0)' VERIFIED."
    address: 0x005A22A0
    function: Ship_CheckCollisionRateLimit
    confidence: high
    note: "Decomp: `if (param_1[0x3b] == 0) return false;` and 0x3B * 4 = 0xEC."
  - claim: "Ship+0x68 = hashVtable pointer (vtable for the rate-limiter pair-hash table; provides hash/compare/insert ops)"
    address: 0x005A22A0
    function: Ship_CheckCollisionRateLimit
    confidence: high
    note: "Decomp: `piVar11 = param_1 + 0x1A` and 0x1A * 4 = 0x68."
  - claim: "Ship+0x6C = entryCount (int); number of tracked pairs"
    address: 0x005A22A0
    function: Ship_CheckCollisionRateLimit
    confidence: high
    note: "Decomp: `param_1[0x1B]` and 0x1B * 4 = 0x6C."
  - claim: "Ship+0x74 = bucketTable (ptr); array of chained entry lists"
    address: 0x005A22A0
    function: Ship_CheckCollisionRateLimit
    confidence: high
    note: "Decomp: `param_1[0x1D]` and 0x1D * 4 = 0x74."
  - claim: "Per-pair entry is TWO separate allocations via FUN_00718CB0 (NiAlloc): (a) 12-byte hash node ([0]=key, [4]=value_ptr, [8]=next) and (b) 0x50-byte value object that contains the last-time float at +0x4"
    address: 0x00718CB0
    function: NiAlloc
    confidence: high
    note: "Clar1 — `iVar9 = FUN_00718CB0(0x50)` for the value block; separate `FUN_00718CB0(0xC)` for the hash node. The doc previously implied one 0x50 entry covers both — actually it's two allocations linked through the hash-node value-ptr."
  - claim: "Distance constant DAT_008942A4 = 0x42E40000 = 114.0f (near threshold)"
    address: 0x008942A4
    function: Ship_CheckCollisionRateLimit
    confidence: high
    note: "Byte-confirmed."
  - claim: "Distance constant DAT_008942AC = 0x43640000 = 228.0f (medium threshold, non-camera)"
    address: 0x008942AC
    function: Ship_CheckCollisionRateLimit
    confidence: high
    note: "Byte-confirmed."
  - claim: "Distance constant DAT_008942A8 = 0x43AB8000 = 343.0f (far threshold, non-camera)"
    address: 0x008942A8
    function: Ship_CheckCollisionRateLimit
    confidence: high
    note: "Byte-confirmed."
  - claim: "Distance constant DAT_00892004 = 0x432A0000 = 170.0f (far threshold, camera/MP-flag mode)"
    address: 0x00892004
    function: Ship_CheckCollisionRateLimit
    confidence: high
    note: "Byte-confirmed."
  - claim: "Distance constant DAT_0088BD58 = 0x40A00000 = 5.0f (very-far multiplier)"
    address: 0x0088BD58
    function: Ship_CheckCollisionRateLimit
    confidence: high
    note: "Byte-confirmed."
  - claim: "Targeting-relationship penalty DAT_008942A0 = 0x3FAAAA8F = 1.333...f (multiplied into cooldown when targeting relationship present)"
    address: 0x008942A0
    function: Ship_CheckCollisionRateLimit
    confidence: high
    note: "Byte-confirmed."
  - claim: "DAT_00888860 = 0x3F800000 = 1.0f (anchor / unblocked multiplier; cross-anchored from collision-detection-system)"
    address: 0x00888860
    function: shared
    confidence: high
    note: "Byte-confirmed."
  - claim: "Cooldown constants byte-confirmed in disasm at the rate-limiter cooldown-selection block: 0.1f (0x3DCCCCCD, min floor), 0.125f (0x3E000000), 0.167f (0x3E2B020C, ~1/6), 0.25f (0x3E800000), 0.5f (0x3F000000)"
    address: 0x005A22A0
    function: Ship_CheckCollisionRateLimit
    confidence: high
    note: "All five cooldown values byte-confirmed via inline immediates / DAT references in the cooldown-selection flowchart."
  - claim: "Distance gate has two branches at 0x005A2522: non-camera (170/228/343) vs camera/MP-flag (114/170)"
    address: 0x005A2522
    function: Ship_CheckCollisionRateLimit
    confidence: high
    note: "Clar3 — branch byte-walked; thresholds match the distance constants above."
  - claim: "Ship damage sub-vtable at 0x00894488 holds: +0x0=0x005AF7D0, +0x4=0x005AF830, +0x8=0x005AF890 (host-side gate), +0xC=0x005B0060 (CollisionDamageWrapper)"
    address: 0x00894488
    function: Ship_damage_vtable
    confidence: high
    note: "Cross-reference for where 0x005AF890 and 0x005B0060 live — NOT the main Ship vtable at 0x00894128."
  - claim: "ProximityManager::Update at FUN_005A83A0 invokes ProcessOverlapPairs at FUN_005A8740 (cross-anchored from collision-detection-system)"
    address: 0x005A83A0
    function: ProximityManager_Update
    confidence: high
  - claim: "DamageableObject::CheckCollision at FUN_00594840 is the full narrow-phase entry called from the rate-limiter wrapper after the gate passes"
    address: 0x00594840
    function: DamageableObject_CheckCollision
    confidence: high
  - claim: "What sets ship+0xEC to non-zero during normal ship creation is undocumented — likely SetupProperties or AddToSet path; DeferredInitObject doesn't replicate it. Stated root cause of the 28,504-event collision storm in headless mode but the C++ initialization site is not pinpointed."
    address: null
    function: shared
    confidence: medium
    note: "OQ1 — needs forward-trace from Ship constructor / property initialization paths."
companions:
  - docs/gameplay/collision-detection-system.md
  - docs/gameplay/collision-shield-interaction.md
supersedes:
  - pre-v5
---

> [!NOTE]
> **Zero algorithm/constant errors — all 5 distance constants + 5 cooldown constants byte-confirmed**. 1 HIGH correction (C1: the call chain narrative is materially wrong — Ship vtable +0x150 is a RET-only stub at 0x005A3900, NOT Ship::CheckCollision at 0x005AF890; the actual rate-limiter caller is an unnamed wrapper at ~0x005A26D0. Impact on OpenBC implementers tracing the wrong functions.) + 3 clarifications (Clar1: per-pair storage is TWO allocations — 12-byte hash node + separate 0x50-byte value object; Clar2: cooldown selection covers all 4 mode combinations cleanly; Clar3: distance gate has explicit non-camera vs camera/MP-flag branches; Clar4: byte at 0x0097FA89 read at 0x005AF890 is GameLive_MP NOT IsHost — cross-doc cascade pending from self-destruct C3) + 1 OQ. CLAUDE.md "Known Issue: collision rate limiting disabled (ship+0xEC=0)" VERIFIED. **C1 will mislead OpenBC implementers if not corrected.**

# Collision Rate Limiting — Reverse Engineering Analysis

Complete analysis of the per-pair collision rate limiter that controls how often collision damage events fire between ships. This is the mechanism responsible for the stock game's ~0.04 collisions/sec (vs our headless server's uncapped ~43/sec).

## Overview

The collision system uses a **per-pair timer cooldown** mechanism. Each ship maintains a hash table keyed by other objects' IDs, tracking the last time each pair was allowed to generate a collision event. A configurable cooldown period (based on player count, game mode, and distance) must elapse before the same pair can collide again.

## Call Chain                                                  [v5-validated 2026-05-28]

### C1 — Actual rate-limiter call chain (the prior doc was materially wrong)

The previous doc claimed:

```
PhysicsObjectClass::CheckCollision (0x005a88e0)
   → [vtable+0x148] CollisionTest_A
   → [vtable+0x150] Ship::CheckCollision (0x005af890)
      → [vtable+0x13C] Ship::CheckCollisionRateLimit (0x005a22a0)
```

**Three problems with that chain**:

1. **Ship vtable +0x150 = 0x005A3900**, which is an 8-byte RET-only stub:
   ```
   005a3900: 8B 4C 24 04          MOV ECX, [ESP+0x4]
   005a3904: ...                  ; (short body)
   005a390?: C2 0C 00             RET 0xC
   ```
   It does NOT dispatch to 0x005AF890. Ship vtable +0x148 = 0x005A38C0 is an identity-compare stub (SETZ AL). Neither slot leads to the rate limiter.

2. **FUN_005A88E0 IS PhysicsObjectClass::CheckCollision**, but it routes Ship-class objects (class ID 0x8125) through `FUN_005A8810 → FUN_005A61C0 → FUN_005A63A0` (Ship-Ship dispatch), NOT through Ship vtable +0x150.

3. **0x005AF890 itself does NOT call vtable+0x13C**. Disasm 0x005AF890 - 0x005AF9B8 shows calls to: `CastToShipClass` (0x005AB670), `IsLocalPlayerShip` (0x005AE140), `FUN_005AC4F0`, `FUN_005A05A0`, vtable+0x94 (GetWorldTranslation), vtable+0xB0, `FUN_005A14D0`, then directly to `FUN_00594840` (DamageableObject::CheckCollision). There is **no** `CALL [E?X+0x13C]` instruction in the function body.

The **actual caller** of vtable+0x13C in the collision pipeline is an **unnamed function at ~0x005A26D0** (Ghidra has not promoted it):

```
005a26e9: MOV EAX, [EDI]          ; this->vtable
005a26eb: CALL [EAX+0x13c]        ; rate limiter
005a26f1: TEST AL, AL
005a26f3: JNZ 0x005a26fc          ; rate limiter said yes → proceed
005a26f5: XOR EAX, EAX
005a26f7: JMP 0x005a2bab          ; rate limiter said no → return 0
```

### Corrected Call Chain

```
ProximityManager::Update (0x005A83A0)    [every frame]
  → SortAndDetectOverlaps (3x per axis)
  → ProcessOverlapPairs (0x005A8740)
     → FUN_005A88E0 PhysicsObjectClass::CheckCollision (outer entry)
        → FUN_005A8810 DispatchCollisionByType (routes class 0x8125)
        → FUN_005A61C0 Ship-Ship narrow phase
        → FUN_005A63A0 Ship-Ship event publisher (posts TGObjPtrEvent)
                  ...
  → [separate gate, ~0x005A26D0]  unnamed wrapper
     → CALL [vtable+0x13C] Ship::CheckCollisionRateLimit (0x005A22A0)  ← RATE LIMITER
        If returns TRUE:
        → DamageableObject::CheckCollision (FUN_00594840) (full narrow phase)
           → Ship::CollisionDamageWrapper (FUN_005B0060) (damage + MP relay)
```

The rate-limiter wrapper at `~0x005A26D0` is a **separate gate** from `FUN_005AF890`. The function at `0x005AF890` is a different host-side collision gate (checks GameLive_MP and IsLocalPlayerShip equality — see Clar4) and does not call the rate limiter itself.

**For OpenBC**: the rate limiter EXISTS at Ship vtable +0x13C = 0x005A22A0 — that part of the prior doc is correct. The algorithm, constants, and ship offsets in the sections below are all unchanged. Only the call-chain narrative (who calls it, and how the pipeline gets there) needed correction.

## Ship::CheckCollisionRateLimit (0x005A22A0)                  [v5-validated 2026-05-28]

### Ship Fields

| Offset | Type | Field | Notes |
|--------|------|-------|-------|
| +0xEC | byte | enableFlag | If 0 → rate limiting disabled, function returns false immediately (CLAUDE.md "Known Issue" root cause) |
| +0x68 | ptr | hashVtable | Hash table vtable object (hash/compare/insert ops) |
| +0x6C | int | entryCount | Number of tracked pairs |
| +0x74 | ptr | bucketTable | Array of chained entry lists |

### Per-Pair Entry — Clar1

The prior doc described `entry[0]=key, entry[1]=lastTime` as a single block. Binary reveals **two separate allocations** linked through the hash node:

**Hash node** (12 bytes, via `FUN_00718CB0(0xC)`):
```
+0x00  int     key                  (other object's ID)
+0x04  void*   value_ptr            (points to the 0x50-byte value object)
+0x08  void*   next_ptr             (next hash node in this bucket)
```

**Value object** (80 bytes / 0x50, via `FUN_00718CB0(0x50)`):
```
+0x00  ...
+0x04  float   lastTime             (last allowed collision timestamp; read as
                                      *pfStack_30 = (float)puVar3[1] where puVar3
                                      is hash-node value_ptr dereferenced)
... remainder zero/unused
```

So the doc's `entry[1]` was actually the **pointer from hash-node-to-value-object**, not the timestamp itself. The timestamp lives at value_object+0x4. Both allocations come from `FUN_00718CB0` (NiAlloc).

### Algorithm

```c
bool Ship__CheckCollisionRateLimit(Ship *this, CollisionEvent *ev) {
    if (this->enableFlag == 0) return false;  // +0xEC, rate limiting disabled

    HashNode *node = FindOrCreatePairEntry(this, ev->sourceObjectID);
    float *lastTime = (float*)((char*)node->value_ptr + 0x4);

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
            cooldown *= 1.333f;        // 33% penalty if targeting relationship (DAT_008942A0)
        if (cooldown * 1.333f <= 1.0f)
            cooldown *= 1.333f;        // Only apply if won't block entirely
    }

    if (elapsed >= cooldown) {
        *lastTime = (float)truncate(elapsed);  // Round down to integer seconds
        return true;  // Allow collision
    }
    return false;
}
```

## Base Cooldown Table                                         [v5-validated 2026-05-28]

All cooldown values byte-confirmed at the rate-limiter cooldown-selection flowchart (Clar2 confirms the 4-mode decision tree covers SP/MP × camera-flag/normal × player-count thresholds cleanly):

| Mode | Players | Cooldown (seconds) | Constant |
|------|---------|-------------------|----------|
| Any (minimum floor) | — | 0.10 | 0x3DCCCCCD |
| SP, camera mode | 3 | 0.167 | 0x3E2B020C |
| SP, camera mode | ≥4 | 0.25 | 0x3E800000 |
| MP standard, collision_enabled | ≥5 | 0.125 | 0x3E000000 |
| MP + flag, host | 2 | 0.167 | 0x3E2B020C |
| **MP + flag, host** | **≥3** | **0.50** | **0x3F000000** |
| MP + flag, client | 3 | 0.167 | 0x3E2B020C |
| MP + flag, client | ≥4 | 0.50 | 0x3F000000 |

In a typical dedicated-server game (MP + ≥3 players + host), the base cooldown is **0.50 seconds per pair**.

## Distance Gates                                              [v5-validated 2026-05-28]

Two branches at 0x005A2522 (Clar3): non-camera mode reads 170/228/343 thresholds; camera/MP-flag mode reads 114/170.

| Distance (game units) | Non-camera mode | Camera/MP-flag mode |
|-----------------------|-----------------|---------------------|
| < 114 | base cooldown | base cooldown |
| 114–228 | cooldown × 2 | cooldown × 2 |
| 228–343 | cooldown × 5 | **BLOCKED (FLT_MAX)** |
| ≥ 343 | **BLOCKED (FLT_MAX)** | **BLOCKED (FLT_MAX)** |

Ships at ≥343 game units apart are **completely blocked** from generating collision events.

### Distance Constants

All byte-confirmed:

| Address | Hex Bytes | Value | Role |
|---------|-----------|-------|------|
| 0x008942A4 | 0x42E40000 | 114.0 | Near threshold |
| 0x008942AC | 0x43640000 | 228.0 | Medium threshold (non-camera) |
| 0x008942A8 | 0x43AB8000 | 343.0 | Far threshold (non-camera) |
| 0x00892004 | 0x432A0000 | 170.0 | Far threshold (camera/MP mode) |
| 0x0088BD58 | 0x40A00000 | 5.0 | Very-far multiplier |
| 0x008942A0 | 0x3FAAAA8F | 1.333... | Targeting-relationship penalty |
| 0x00888860 | 0x3F800000 | 1.0 | Anchor / unblocked multiplier |

## Why Stock Gets ~0.04/sec and Headless Gets ~43/sec

### Stock game (3-player MP, host):
- Base cooldown: 0.50s per pair
- Ships at range >114 during combat: cooldown → 1.0s or blocked
- Ships at >343 units: blocked entirely
- Only ships in sustained close contact generate events
- Result: ~84 events / 33 minutes = **~0.04/sec**

### Headless server (our DeferredInitObject path):
- **Verified root cause**: `ship+0xEC` (enableFlag) is zero
- When `enableFlag == 0`, `Ship::CheckCollisionRateLimit` immediately returns false
- The rate-limiter gate wrapper at ~0x005A26D0 then returns 0 → downstream collision processing skipped
- BUT — the doc's prior claim that "Ship::CheckCollision then falls through to the full damage path unconditionally" was based on the broken call chain. The actual mechanism for why headless gets uncapped events lives elsewhere in the dispatch pipeline; see OQ1.
- Result: ~28,504 events / 11 minutes = **~43/sec**

### Probable Fix

The enableFlag at `ship+0xEC` needs to be set to non-zero. This field is likely initialized during the normal ship spawn path (SetupProperties or AddToSet), which our DeferredInitObject may not fully replicate. The hash-table fields at ship+0x68 / +0x6C / +0x74 also need initialization, since `FindOrCreatePairEntry` calls the vtable at ship+0x68 (Clar1).

## Clar4 — Byte at 0x0097FA89 is GameLive_MP, not IsHost

The function at `0x005AF890` (which the prior doc misidentified as `Ship::CheckCollision`) starts with `MOV AL, [0x0097FA89]`. The doc described that byte as the "IsHost gate". Per the self-destruct doc's C3 correction (currently CASCADE PENDING across docs), the byte at `0x0097FA89` is actually `GameLive_MP`, not `IsHost`. **Cross-doc cascade pending** — this name should be revised once self-destruct C3 lands.

## Key Function Reference                                      [v5-validated 2026-05-28]

| Address | Name | Purpose |
|---------|------|---------|
| 0x005A22A0 | Ship::CheckCollisionRateLimit | Per-pair timer cooldown + distance gate (Ship vtable +0x13C) |
| ~0x005A26D0 | (unnamed wrapper) | **Actual rate-limiter gate** — calls vtable+0x13C; Ghidra-unpromoted (C1) |
| 0x005AF890 | (host-side collision gate) | Reads GameLive_MP; does NOT call rate limiter (C1) |
| 0x005A3900 | (RET-only stub) | Ship vtable +0x150 — 8-byte no-op (C1) |
| 0x005A38C0 | (identity-compare stub) | Ship vtable +0x148 — SETZ AL (C1) |
| 0x005A83A0 | ProximityManager::Update | Sweep-and-prune overlap detection (per frame) |
| 0x005A8740 | ProcessOverlapPairs | Walks the active pair list |
| 0x005A8810 | DispatchCollisionByType | Routes pair to type-specific handler via class ID |
| 0x005A88E0 | PhysicsObjectClass::CheckCollision | Outer collision entry point |
| 0x005A61C0 | Ship-Ship narrow phase | Bounding-sphere + post-collision-event |
| 0x005A63A0 | Ship-Ship event publisher | Posts TGObjPtrEvent (event code 0x00800050) |
| 0x00594840 | DamageableObject::CheckCollision | Full narrow phase (called after rate gate) |
| 0x005B0060 | Ship::CollisionDamageWrapper | Damage + MP relay (sibling leaf collision-shield-interaction.md) |
| 0x00718CB0 | NiAlloc | Used for both 0x50 value-object and 0xC hash-node allocations |

## Vtable Anchors                                              [v5-validated 2026-05-28]

| Vtable | Address | Slot | Target | Role |
|--------|---------|------|--------|------|
| Ship main vtable | 0x00894128 | +0x13C | 0x005A22A0 | **Rate limiter (CORRECT)** |
| Ship main vtable | 0x00894128 | +0x148 | 0x005A38C0 | Identity-compare stub (NOT CollisionTest_A) |
| Ship main vtable | 0x00894128 | +0x150 | 0x005A3900 | RET-only stub (NOT Ship::CheckCollision) |
| Ship damage sub-vtable | 0x00894488 | +0x0 | 0x005AF7D0 | — |
| Ship damage sub-vtable | 0x00894488 | +0x4 | 0x005AF830 | — |
| Ship damage sub-vtable | 0x00894488 | +0x8 | 0x005AF890 | Host-side collision gate (NOT Ship::CheckCollision) |
| Ship damage sub-vtable | 0x00894488 | +0xC | 0x005B0060 | CollisionDamageWrapper (sibling doc) |

## Open Questions

- **OQ1** — What sets `ship+0xEC` to non-zero during normal ship creation? This is the stated root cause of the headless ~43 events/sec collision storm (vs stock ~0.04/sec), but the C++ initialization site is not pinpointed. Likely candidates: a `SetupProperties` path during normal ship spawn, or `AddToSet`. DeferredInitObject (our Python-driven ship creation path) does NOT replicate it. **Promotion path**: forward-trace from Ship constructor and `AddToSet` / `SetupProperties` paths to identify the WRITE site for `ship+0xEC`, then expose it via SWIG (if not already) so DeferredInitObject can set it. The hash-table fields at ship+0x68 / +0x6C / +0x74 likely need initialization at the same site.

## Related Documents

- [collision-detection-system.md](collision-detection-system.md) — Parent foundation: the ProximityManager broad phase that feeds candidate pairs into this gate
- [collision-shield-interaction.md](collision-shield-interaction.md) — Sibling leaf: what happens AFTER the rate limiter passes (CollisionDamageWrapper at FUN_005B0060)
