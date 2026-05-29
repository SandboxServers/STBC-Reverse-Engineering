---
name: gameplay-mid-ship-navigation-validation-20260528
description: v5 validation of docs/gameplay/ship-navigation.md (gameplay mid #11). Doc is mid-tier accuracy. ZERO targeting-pipeline corrections (event 0x800058 + ID byte-confirmed); 1 H-impact FIELD-OFFSET swap (+0x1F8 is speed scalar, NOT direction; +0x1FC..+0x204 is direction); 1 C convergence-point reversal (TurnTowardDifference 0x005ad4d0 is the SINK not entry — chain is TowardLocation→TowardDirection→FUN_005ad910→TowardDifference); 1 C fabricated field (+0x87 "cycle index" — actually GetNextTarget reads +0x21C target ID directly); 1 C InSystemWarp distance threshold (50.0f at 0x008944b4 — NOT "295"); 1 C event-ID fabrication (no separate "ET_EXITED_WARP" — both engage+disengage fire 0x008000EF).
metadata:
  type: project
---

# Ship Navigation v5 Validation — 2026-05-28

Phase 1-5 validation of `docs/gameplay/ship-navigation.md` (gameplay family, mid-tier #11). 262 lines covering targeting pipeline, turn computation, impulse model, in-system warp, network authority.

## Top-Level Findings

### What's Right (and byte-confirmed)

1. **Targeting event ID `0x800058`** (ET_TARGET_WAS_CHANGED) — confirmed at 0x005ae27a `MOV [ESI+0x10], 0x800058`.
2. **ET_TARGET_SUBSYSTEM_SET `0x80005A`** — confirmed inside FUN_005ae2c0 (Ship__OnTargetChanged).
3. **Ship_SetTarget call chain** (top-level order): wrapper (0x005ae1e0) → inner (0x005ae210) → fires event 0x800058 → calls StopFiringWeapons (0x005b0bb0) → calls OnTargetChanged (0x005ae2c0). All addresses + ordering byte-confirmed via disasm.
4. **StopFiringWeapons (0x005b0bb0)** walks `[+0x284]` linked list; calls `FUN_00583f60` (IsA(0x801D)); on non-NULL calls `vtable[+0x90]`. Doc's "IsA(0x801D)" CONFIRMED.
5. **FUN_00583f60 (Subsystem__AsWeaponSystem)** is precisely a `vtable[8](0x801D)` cast. CONFIRMED.
6. **TGSceneGraph__FindObjectByID (0x00434e70)** uses class ID 0x8003 and walks `DAT_0097e9cc`. CONFIRMED.
7. **TGSceneGraph__GetObjectByID (0x00434e00)** also uses 0x8003. CONFIRMED.
8. **CastToShipClass (0x005ab670)** = IsA(0x8008). CONFIRMED.
9. **Subsystem__GetProperty (0x00560fc0)** returns `+0x18`. CONFIRMED.
10. **Subsystem__IsActive (0x0056c340)** reads `property+0x25`. CONFIRMED.
11. **Subsystem__GetRadius (0x0056b940)** reads `property+0x44` float. CONFIRMED.
12. **PoweredSubsystem__GetEfficiency (0x005822d0)** = `+0xFC / +0xF8`. CONFIRMED.
13. **ImpulseEngineSubsystem_Ctor (0x00561050)** sets vtable to 0x00892d10 (matches power-system memo). CONFIRMED.
14. **GetForwardDirection (0x00434cd0)** reads `DAT_00980df0`. CONFIRMED.
15. **TGObject__SetVelocity (0x005a04c0)** writes NiAVObject+0x98/+0x9C/+0xA0 via ship+0x18. CONFIRMED.
16. **TGObject__SetDirtyFlag (0x006d5e80)** toggles bit 2 of `*(ushort *)(+0x18)`. CONFIRMED.
17. **WeaponSystem__FindTargetEntry (0x00585360)** walks `+0xC4` linked list. CONFIRMED.
18. **WeaponSystem__FindTargetByObjectID (0x00584080)** delegates to FindTargetEntry. CONFIRMED.
19. **WeaponSystem__SetTargetOffset (0x00585580)** updates entry +4/+8/+0xC + clears child subsystem targets. CONFIRMED.
20. **StartGetSubsystemMatch (0x005ac370) / GetNextSubsystemMatch (0x005ac390)** iterator over `+0x284` list filtered by `vtable[8](typeID)`. CONFIRMED.
21. **Ship+0x21C = target object ID; Ship+0x220 = target subsystem ID; Ship+0x228..230 = target offset (TGPoint3); Ship+0x224 = manual aim flag**. All byte-confirmed.
22. **Ship+0x284 = subsystem linked-list head; +0x288 = tail; +0x280 = count** (per AddSubsystemToLists @ 0x005b3e50). CONFIRMED.
23. **InSystemWarp opcode 0x10 IS wired up**: jump-table slot 14 (index 14 × 4 = 0x38 from base 0x0069F534) dispatches to event handler 0x0069fda0 with `PUSH 0x008000ED` (ET_START_WARP). Doc's "exists in opcode table" CONFIRMED.
24. **SetSpeed (0x005ac590)** reads max speed from `ImpulseEngineSubsystem+0xAC`, divides input, delegates to SetImpulse. CONFIRMED.
25. **GetEffectiveSpeed/Acceleration formulas** (0x00561330 / 0x00561230) — high-level "max * health * efficiency" CONFIRMED; actual math is `(1-efficiency_complement) * (base_max - sum(child_damage * max/n)) * ship+0x90` where efficiency is from PoweredSubsystem.

### Corrections (C-level)

1. **C-HIGH (field-offset swap)**: Doc lists `+0x1F8 = direction (float[3])` and `+0x1FC = speed scalar`. **WRONG**. Actual layout (FUN_005ac470 / SetImpulse):
   - `+0x1F8` = **speed scalar (float)** (clamped 0..1)
   - `+0x1FC..+0x200..+0x204` = **direction (TGPoint3)**
   - `+0x208` = coord-space flag (DIRECTION_MODEL_SPACE vs WORLD_SPACE)
   - `+0x1E4` = "command pending" byte flag set to 1
   - Doc's "Ship Velocity Fields" table is reversed. **Material to OpenBC implementation.**

2. **C-HIGH (convergence-point reversal)**: Doc says "All paths converge on `ComputeTurnAngularVelocity` (0x005ad910)". **WRONG direction**. Actual call chain:
   ```
   TurnTowardLocation (0x005ad3a0)
     ↓ (normalizes direction)
   TurnTowardDirection (0x005ad450)
     ↓ (calls vtable[0xAC] = GetOrientationOrInverse)
   FUN_005ad910 (quaternion-orient routine)
     ↓ (calls FUN_005ad4d0)
   TurnTowardDifference (0x005ad4d0)  ← SINK (deepest, iterative bisection on collision/intercept)
   ```
   xrefs confirm: 0x005ad4d0 has exactly ONE caller (0x005ad910). 0x005ad910 has TWO callers (0x005ad450 + one named function). So the actual computation sink is `TurnTowardDifference`, not `FUN_005ad910`. Doc's description of `FUN_005ad910` ("quaternion slerp-style turn with constraints") is essentially right but it's not the bottom of the chain.

3. **C-MEDIUM (fabricated field +0x87 cycle index)**: Doc's "Target Fields on Ship" table lists `+0x87 | byte | Target list cycle index`. **FABRICATED**. The decompiler's `param_1[0x87]` (with param_1 typed as `int*`) resolves to `*(param_1 + 0x21C)` — the SAME target-ID field at +0x21C. Verified at 0x005ae6e0: `MOV EDI, [ESI+0x21C]`. There is no separate cycle index; GetNextTarget seeds the binary search with the current target ID.

4. **C-MEDIUM (wrong warp distance threshold)**: Doc says `"distance exceeds threshold ... default 295 units"` referring to `fInSystemWarpDistance`. The binary constant in InSystemWarp (0x005ac6e0) at `_DAT_008944b4` reads `0x42480000 = 50.0f`. So the C++ engage gate is **fVar7 > 50.0f**, not 295. The "295" value may be from a Python `Intercept.py` script — but C-level claim is wrong.

5. **C-MEDIUM (fabricated event ID `ET_EXITED_WARP`)**: Doc mentions `ET_EXITED_WARP` event as a separate event class. **Fabricated**. Both InSystemWarp engage (FUN_005ac6e0) and StopInSystemWarp (FUN_005acdb0) post the SAME event ID `0x008000EF`. There is one warp-related event, not two.

### Clarifications (Clar-level)

1. **0x005ae430 fires event `0x800059`** (between 0x800058 and 0x80005A) — undocumented in the doc. The function is what doc names `Ship__UpdateWeaponTargets` and after the target-offset write it posts an event with `(iVar3 + 0x10) = &DAT_00800059`. Likely ET_TARGET_OFFSET_CHANGED.

2. **0x005ae210 Ghidra symbol is `Ship_SetTarget`** (single underscore). Doc names this `Ship__SetTargetInternal` and the wrapper `Ship__SetTarget`. Naming is the doc's archaeological choice and is consistent with the C++ pattern; Ghidra's existing rename does not match doc nomenclature. Not a correction — orthography only.

3. **0x005ad910 quaternion-orient routine reads vtable[0xB0]** (GetForwardDirection) and uses TGPoint3 constants `DAT_009a2878/009a287c/009a2880` as zero-vector sentinels. Doc's description ("Uses quaternion-based interpolation (slerp-style)... preserves up axis... forward axis primary alignment") is plausible but the actual decomp doesn't show quaternion slerp — it does linear vector blending with `param_3` (a scalar) and conditional sign-flip. The "slerp-style" framing is speculative.

4. **Ship+0x84 = "warp engaged" flag** (set in InSystemWarp on success). Ship+0x210 = "warp tracking active". Ship+0x214/+0x218 = warp deltas/state. Doc doesn't list these.

5. **Ship+0xE0 = orientation matrix** (read by FUN_005ad4d0 via FUN_0041cbd0 — quaternion-from-matrix). Doc's section 2 doesn't list ship+0xE0 field.

6. **Ship+0xD8/0xDC/0xE0 = NiAVObject ptr / model/world flag / orientation matrix**. Used throughout turn computation.

7. **InSystemWarp obstacle-avoidance class-ID filter**: ignores objects with `IsA() == 0x80E2, 0x80DE, 0x8125, 0x800E`. These are likely fighter, projectile, dynamic-effect, AI-flag classes. Doc mentions obstacle avoidance but doesn't list the exclusion classes.

8. **InSystemWarp arrival threshold**: `cos(15°) ≈ 0.9659f` at `_DAT_008942E0` — when dot(forward, to_target) < this, StopInSystemWarp fires. Not in doc.

### Risks (R-level)

1. **R-NONE — no Tier-3 risks identified.** Doc's narrative architecture (3 entry points → converge to math kernel → physics output) is structurally correct even where the SINK point is misidentified.

### Open Questions (OQ-level)

1. **OQ1**: Doc's claim "Opcode 0x10 (StartWarp) ... unused in stock multiplayer" — is this confirmed by valentines-day-battle-analysis trace? The opcode IS wired (jump table slot 14 dispatches ET_START_WARP event 0x008000ED). Whether it's ACTUALLY sent on the wire in MP play is a usage claim not byte-anchored in code. Need stock-trace cross-check.

2. **OQ2**: Doc says "in-system warp is only triggered by AI scripts in single-player." Are there Python script paths in SP that call SetImpulse(>1.0) or InSystemWarp directly? The C entry point 0x005ac6e0 has only ONE C caller (0x005adb55 inside an unbound function body). Are the AI script paths going through SWIG to this C function, or through a separate higher-level Python intercept system?

3. **OQ3**: `FUN_005ad910`'s param_4 / param_5 (two TGPoint3 ptrs initialized to `DAT_009a2878` ie zero vector) — what semantic do they represent? Doc claims "constrains rotation to preserve ship's up axis" but the decomp shows two separate vector inputs handled by conditional branches. Likely "up override" and "lateral override" but not byte-confirmed.

### Historical (H-level)

1. **H-NONE — no historical-only sections in this doc.** It's net-current architecture.

## Address Anchors (38 functions / 9 constants verified)

### Targeting Pipeline (8)
- 0x005ae1e0 — SetTarget by-name wrapper (Ghidra: FUN_005ae1e0)
- 0x005ae210 — Ship_SetTarget (Ghidra: Ship_SetTarget) — fires event 0x800058
- 0x005ae170 — Ship__GetTarget (returns +0x21C resolved)
- 0x005ae2c0 — Ship__OnTargetChanged — fires event 0x80005A
- 0x005ae430 — Ship__UpdateWeaponTargets — fires event 0x800059 (UNDOC)
- 0x005ae630 — Ship__GetTargetSubsystemObject — reads +0x220, ForwardEvent
- 0x005ae650 — Ship__GetTargetOffset — returns +0x228 or auto-computes
- 0x005ae6d0 — Ship__GetNextTarget — binary search seeded by +0x21C (NOT +0x87)

### Turn Computation (5)
- 0x005ad3a0 — TurnTowardLocation
- 0x005ad450 — TurnTowardDirection
- 0x005ad4d0 — TurnTowardDifference (ACTUAL SINK)
- 0x005ad910 — Quaternion-orient routine (not the sink)
- 0x005ad290 — SetTargetAngularVelocityDirect (writes +0x1E8..+0x1F0)

### Movement (4)
- 0x005ac470 — SetImpulse (writes +0x1F8 speed, +0x1FC..+0x204 dir, +0x208 space, +0x1E4 flag)
- 0x005ac590 — SetSpeed (delegates to SetImpulse via ImpulseEngine+0xAC max)
- 0x00561330 — ImpulseEngineSubsystem__GetEffectiveSpeed
- 0x00561230 — ImpulseEngineSubsystem__GetEffectiveAcceleration

### Warp (2)
- 0x005ac6e0 — InSystemWarp (fires 0x008000EF)
- 0x005acdb0 — StopInSystemWarp (also fires 0x008000EF — same event, not separate)

### Weapon Integration (4)
- 0x00583f60 — Subsystem__AsWeaponSystem (IsA(0x801D))
- 0x00584080 — WeaponSystem__FindTargetByObjectID
- 0x00585360 — WeaponSystem__FindTargetEntry
- 0x00585580 — WeaponSystem__SetTargetOffset

### Scene Graph (5)
- 0x00434e70 — TGSceneGraph__FindObjectByID
- 0x00434e00 — TGSceneGraph__GetObjectByID
- 0x00434cd0 — GetForwardDirection
- 0x005ab670 — CastToShipClass (Ghidra: CastToShipClass)
- 0x005a04c0 — TGObject__SetVelocity
- 0x006d5e80 — TGObject__SetDirtyFlag

### Subsystems (6)
- 0x00560fc0 — Subsystem__GetProperty
- 0x0056c340 — Subsystem__IsActive
- 0x0056b940 — Subsystem__GetRadius
- 0x0056c570 — ShipSubsystem__GetChildSubsystem (Ghidra-named)
- 0x005822d0 — PoweredSubsystem__GetEfficiency
- 0x005ac370 / 0x005ac390 — StartGetSubsystemMatch / GetNextSubsystemMatch
- 0x005b3e50 — Ship__AddSubsystemToLists (Ghidra-named)
- 0x005b0bb0 — Ship__StopFiringWeapons
- 0x00561050 — ImpulseEngineSubsystem_Ctor (Ghidra-named, vtable 0x00892d10)

### Collision Queries (4)
- 0x005a7cf0 — CollisionQuery__Execute (sweep-and-prune build)
- 0x005a8320 — CollisionQuery__GetNextResult
- 0x005a8350 — CollisionQuery__Destroy
- 0x004570d0 — RaySphereIntersect (returns 0/1/2)

### Constants
- `_DAT_008944b4` = 0x42480000 = **50.0f** — InSystemWarp engage distance (NOT 295)
- `_DAT_008944b0` = 0x42960000 = 75.0f — warp velocity multiplier
- `_DAT_008942e0` = 0x3F7746EA = ~0.9659 = cos(15°) — warp arrival dot threshold
- `_DAT_00888b58` = 0x358637BD = ~1e-6 — zero-magnitude epsilon
- `_DAT_00888860` = 1.0f — common unity constant
- `_DAT_00888b54` = 0.0f — common zero constant
- `DAT_009a2878/87c/880` — zero-vector sentinel TGPoint3
- `DAT_00980df0/df4/df8` — global forward direction (X,Y,Z)
- Event IDs: 0x800058 (TARGET_WAS_CHANGED), 0x800059 (TARGET_OFFSET_CHANGED?), 0x80005A (TARGET_SUBSYSTEM_SET), 0x008000EF (IN_SYSTEM_WARP)

### Field Offsets on Ship
- +0x18 — NiAVObject ptr (per power-system memo & SetVelocity)
- +0x20 — TGSet ptr (scene-graph parent)
- +0x84 — warp-engaged byte flag (UNDOC)
- +0x87 — **NOT a cycle index** (doc fabrication; the decomp's int*[0x87] is the +0x21C target ID)
- +0x90 — float (likely impulse efficiency factor; in GetEffectiveSpeed)
- +0xA8 — non-zero gates efficiency math
- +0xD8/0xDC/0xE0 — orientation/matrix block
- +0xE8 — used as physics save value
- +0x1E4 — "impulse command pending" byte flag (SET BY SetImpulse)
- +0x1E5 — "angular-velocity command pending" byte (SET BY SetTargetAngularVelocityDirect)
- +0x1E8..+0x1F0 — explicit angular velocity (TGPoint3)
- +0x1F4 — physics save value (e8 echo)
- +0x1F8 — **speed scalar** (NOT direction as doc claims)
- +0x1FC..+0x204 — **direction (TGPoint3)** (NOT speed scalar)
- +0x208 — coord-space flag
- +0x210 — warp-active byte
- +0x214/+0x218 — warp deltas
- +0x21C — target object ID (and seed for next-target binary search)
- +0x220 — target subsystem ID
- +0x224 — manual aim flag
- +0x228..+0x230 — target offset (TGPoint3)
- +0x280 — subsystem-list count
- +0x284 — subsystem-list head
- +0x288 — subsystem-list tail
- +0x29C/+0x2A0 — weapon sub-list head/tail (separate classification)
- +0x2CC — ImpulseEngineSubsystem ptr (vtable 0x00892d10)
- +0x2D0 — WarpEngineSubsystem ptr (vtable 0x00893040, per power-system memo)

## Completeness Scores (function_completeness)

- 0x005ae210 Ship_SetTarget: effective 19.1, fixable 80.9
- 0x005ad910 (orient routine): effective 0.0, fixable 123.1 (deepest functions hit cap)
- 0x005ad4d0 TurnTowardDifference: effective 0.0, fixable 126.1 (109 lines, 86 undefined vars)
- 0x005ac6e0 InSystemWarp: effective 0.0, fixable 104.9 (202 lines, 17 undefined vars)
- 0x005ac470 SetImpulse: effective 5.1, fixable 94.9
- 0x00561330 GetEffectiveSpeed: effective 0.0, fixable 107.8

None of the doc's load-bearing functions are above 50/100 — but doc's claims are validated by decompilation cross-check, not function-completeness-derived. v5 evidence anchored via direct decomp + disasm spot-checks.

## v5 Status Recommendation

**`partial`** — material C-HIGH field-offset swap (+0x1F8 vs +0x1FC) MUST be corrected before OpenBC implementers wire SetImpulse. Doc is otherwise mostly accurate but has the convergence-point inverted, a fabricated cycle index, a wrong warp distance constant, and a fabricated event ID. Recommend Documentation Writer republish with all 5 C corrections + 8 Clar additions.

## Cross-References

- Pre-anchored offsets from `power-system.md` (ImpulseEngine vtable 0x00892D10 @ +0x2CC, WarpEngine 0x00893040 @ +0x2D0) — both CONFIRMED.
- Pre-anchored from `stateupdate-validation-20260528.md` — position/orientation replication via 0x01/0x02 dirty bits CONFIRMED to be StateUpdate-driven (network authority claim holds).
- Pre-anchored from `objnotfound-triad-validation-20260528.md` — EnterSet wire claim independent; doesn't intersect this doc.

## Pattern Note

**The +0x1F8/+0x1FC swap is the kind of error pre-v5 docs make routinely**: when reading decompiled code that treats ship as `(int *)` and accesses by index, the indices map to BYTE offsets at 4-byte stride. Doc author probably saw `param_1[0x7E] = speed_param_2` (0x7E * 4 = 0x1F8) and wrote it down as `+0x1F8 = direction` because the params were ordered (speed, direction, space) in C calling convention. Always read DISASM to verify offset semantics, not decompiled C field syntax.

**The "+0x87 cycle index" fabrication** is the same trap in a different form: `int *param_1; param_1[0x87]` looks like a separate field but is just `*(param_1+0x21C)` — the integer index multiplies by 4 implicitly. Disasm shows `MOV EDI, [ESI+0x21C]` directly.
