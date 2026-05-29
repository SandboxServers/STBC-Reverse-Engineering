> [docs](../README.md) / [gameplay](README.md) / ship-navigation.md

---
title: Ship Navigation & Targeting
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
  # ---- Targeting pipeline (8 functions) ----
  - claim: "Ship_SetTarget (by-name wrapper) at 0x005ae1e0 — calls FindObjectByID, delegates to inner Ship_SetTarget at 0x005ae210"
    address: 0x005ae1e0
    function: Ship_SetTarget_wrapper
    confidence: high
    note: "SWIG ShipClass_SetTarget target. Ghidra symbol is FUN_005ae1e0."
  - claim: "Ship_SetTarget (inner) at 0x005ae210 — fires event 0x800058 (ET_TARGET_WAS_CHANGED), calls StopFiringWeapons, calls OnTargetChanged"
    address: 0x005ae210
    function: Ship_SetTarget_inner
    completeness: 19.1
    effective: 80.9
    confidence: high
    note: "Event ID 0x800058 byte-confirmed at 0x005ae27a `MOV [ESI+0x10], 0x800058`. Ghidra symbol is single-underscore `Ship_SetTarget` — doc names this `Ship__SetTargetInternal` (orthography only, not a correction)."
  - claim: "Ship__GetTarget at 0x005ae170 — reads +0x21C (target object ID), validates target alive, returns object or NULL"
    address: 0x005ae170
    function: Ship__GetTarget
    confidence: high
    note: "Byte-confirmed."
  - claim: "Ship__OnTargetChanged at 0x005ae2c0 — post-change hook; calls UpdateWeaponTargets; fires event 0x80005A (ET_TARGET_SUBSYSTEM_SET)"
    address: 0x005ae2c0
    function: Ship__OnTargetChanged
    confidence: high
    note: "Event ID 0x80005A byte-confirmed inside the body."
  - claim: "Ship__UpdateWeaponTargets at 0x005ae430 — walks +0x284 subsystem linked list updating weapon target entries; fires event 0x800059 (likely ET_TARGET_OFFSET_CHANGED, undocumented)"
    address: 0x005ae430
    function: Ship__UpdateWeaponTargets
    confidence: high
    note: "Clar1 — event 0x800059 sits between 0x800058 and 0x80005A in the targeting event range. Post is `(iVar3 + 0x10) = &DAT_00800059` after the target-offset write. Semantic 'TARGET_OFFSET_CHANGED' is hypothesized from positional pattern; not byte-anchored to a string."
  - claim: "Ship__GetTargetSubsystemObject at 0x005ae630 — reads +0x220 (target subsystem ID), resolves via ForwardEvent"
    address: 0x005ae630
    function: Ship__GetTargetSubsystemObject
    confidence: high
  - claim: "Ship__GetTargetOffset at 0x005ae650 — returns +0x228 target offset TGPoint3 (manual aim point) or auto-computes from target bounding box"
    address: 0x005ae650
    function: Ship__GetTargetOffset
    confidence: high
  - claim: "Ship__GetNextTarget at 0x005ae6d0 — binary search in sorted target list SEEDED BY +0x21C (current target ID), NOT by a separate cycle index"
    address: 0x005ae6d0
    function: Ship__GetNextTarget
    confidence: high
    note: "C3 — disasm at 0x005ae6e0 reads `MOV EDI, [ESI+0x21C]` directly. The decompiler's `param_1[0x87]` (int* * 4 = 0x21C) is the SAME field, not a separate cycle index byte."
  # ---- Turn computation (5 functions) ----
  - claim: "Ship__TurnTowardLocation at 0x005ad3a0 — normalizes direction to target point, calls TurnTowardDirection"
    address: 0x005ad3a0
    function: Ship__TurnTowardLocation
    confidence: high
  - claim: "Ship__TurnTowardDirection at 0x005ad450 — gets current orientation via vtable[0xAC] (GetOrientationOrInverse), calls quaternion-orient routine FUN_005ad910"
    address: 0x005ad450
    function: Ship__TurnTowardDirection
    confidence: high
  - claim: "Ship__TurnTowardDifference at 0x005ad4d0 — ACTUAL convergence sink, 109 lines, iterative bisection on collision/intercept; one caller (FUN_005ad910)"
    address: 0x005ad4d0
    function: Ship__TurnTowardDifference
    completeness: 0.0
    effective: 126.1
    confidence: high
    note: "C2 — prior doc said `ComputeTurnAngularVelocity` (FUN_005ad910) was the sink. xrefs show 0x005ad4d0 has ONE caller (0x005ad910); 0x005ad910 has TWO callers. SWIG `ShipClass_TurnTowardDifference` target is correct but it's the DEEPEST function, not just a peer entry. Reads orientation matrix at ship+0xE0 via FUN_0041cbd0 (quaternion-from-matrix)."
  - claim: "FUN_005ad910 quaternion-orient routine — not the convergence sink; reads vtable[0xB0] (GetForwardDirection); uses zero-vector sentinel TGPoint3 DAT_009a2878/87c/880; calls TurnTowardDifference"
    address: 0x005ad910
    function: quaternion_orient_routine
    completeness: 0.0
    effective: 123.1
    confidence: high
    note: "OQ3 — doc's prose 'quaternion slerp-style with up-axis constraint' is plausible-sounding but decomp shows linear vector blending with conditional sign-flip, not slerp math. The slerp framing is speculative."
  - claim: "Ship__SetTargetAngularVelocityDirect at 0x005ad290 — SWIG target, writes explicit angular velocity at +0x1E8..+0x1F0, sets +0x1E5 byte 'angular-velocity command pending'"
    address: 0x005ad290
    function: Ship__SetTargetAngularVelocityDirect
    confidence: high
  # ---- Impulse movement (4 functions + field layout) ----
  - claim: "Ship__SetImpulse at 0x005ac470 — writes +0x1F8 SPEED scalar (clamped 0..1), +0x1FC..+0x204 DIRECTION TGPoint3, +0x208 coord-space flag, +0x1E4 'impulse command pending' byte"
    address: 0x005ac470
    function: Ship__SetImpulse
    completeness: 5.1
    effective: 94.9
    confidence: high
    note: "C1 HIGH OpenBC BLOCKING — prior doc had +0x1F8/+0x1FC SWAPPED. Disasm confirms +0x1F8 is the scalar (single float clamped 0..1) and +0x1FC..+0x204 is the TGPoint3 direction. Author was misled by parameter-order (`speed, direction, space`) in C++ calling convention versus actual struct layout."
  - claim: "Ship__SetSpeed at 0x005ac590 — divides input by ImpulseEngineSubsystem+0xAC (base max speed), delegates to SetImpulse"
    address: 0x005ac590
    function: Ship__SetSpeed
    confidence: high
  - claim: "ImpulseEngineSubsystem__GetEffectiveSpeed at 0x00561330 — max_speed * (child_health_aggregate * power_efficiency); actual formula is (1-efficiency_complement) * (base_max - sum(child_damage * max/n)) * ship+0x90"
    address: 0x00561330
    function: ImpulseEngineSubsystem__GetEffectiveSpeed
    completeness: 0.0
    effective: 107.8
    confidence: high
  - claim: "ImpulseEngineSubsystem__GetEffectiveAcceleration at 0x00561230 — same pattern for acceleration"
    address: 0x00561230
    function: ImpulseEngineSubsystem__GetEffectiveAcceleration
    confidence: high
  - claim: "ImpulseEngineSubsystem_Ctor at 0x00561050 — sets vtable to 0x00892d10 (cross-anchored from power-system.md)"
    address: 0x00561050
    function: ImpulseEngineSubsystem_Ctor
    confidence: high
    note: "Cross-anchored from power-system.md (validated 2026-05-28). ImpulseEngine+0xAC is used by SetSpeed for the division."
  # ---- In-system warp (2 functions + constants) ----
  - claim: "Ship__InSystemWarp at 0x005ac6e0 — engage threshold is **50.0f** (at _DAT_008944b4), NOT 295; obstacle-avoidance ignores classes 0x80E2/0x80DE/0x8125/0x800E; arrival threshold is cos(15°)≈0.9659 at _DAT_008942E0; velocity multiplier is 75.0f at _DAT_008944b0; fires event 0x008000EF"
    address: 0x005ac6e0
    function: Ship__InSystemWarp
    completeness: 0.0
    effective: 104.9
    confidence: high
    note: "C4 — disasm reads _DAT_008944b4 = 0x42480000 = 50.0f. The 295 value may be from Python Intercept.py script — but C-level binary value is 50.0. Sets ship+0x84 warp-engaged byte."
  - claim: "Ship__StopInSystemWarp at 0x005acdb0 — also fires event 0x008000EF (SAME as engage path); clears ship+0x210 warp-active and ship+0x214/+0x218 warp deltas"
    address: 0x005acdb0
    function: Ship__StopInSystemWarp
    confidence: high
    note: "C5 — prior doc referenced a separate `ET_EXITED_WARP` event ID. Fabricated. Both engage and stop paths post 0x008000EF. There is one warp-related event, not two."
  - claim: "InSystemWarp opcode 0x10 IS wired up — MultiplayerGame jump table slot 14 (index 14 × 4 = 0x38 from base 0x0069F534) dispatches to event handler 0x0069fda0 with PUSH 0x008000ED (ET_START_WARP)"
    address: 0x0069F534
    function: opcode_0x10_jump_table_slot
    confidence: high
    note: "Doc text claim 'exists in opcode table' CONFIRMED. Whether opcode 0x10 is actually sent on the wire in stock MP play is OQ1 (usage claim, not byte-anchored)."
  # ---- Constants (9 .rdata) ----
  - claim: "_DAT_008944b4 = 0x42480000 = 50.0f — InSystemWarp engage distance threshold"
    address: 0x008944b4
    function: in_system_warp_engage_distance
    confidence: high
  - claim: "_DAT_008944b0 = 0x42960000 = 75.0f — InSystemWarp velocity multiplier"
    address: 0x008944b0
    function: in_system_warp_velocity_multiplier
    confidence: high
  - claim: "_DAT_008942e0 = 0x3F7746EA ≈ 0.9659 = cos(15°) — InSystemWarp arrival dot-product threshold"
    address: 0x008942e0
    function: in_system_warp_arrival_dot_threshold
    confidence: high
  - claim: "_DAT_00888b58 = 0x358637BD ≈ 1e-6 — zero-magnitude epsilon used in normalization"
    address: 0x00888b58
    function: zero_magnitude_epsilon
    confidence: high
  - claim: "_DAT_00888860 = 0x3F800000 = 1.0f — common unity constant in turn/impulse math"
    address: 0x00888860
    function: unity_constant
    confidence: high
  - claim: "_DAT_00888b54 = 0x00000000 = 0.0f — common zero constant"
    address: 0x00888b54
    function: zero_constant
    confidence: high
  - claim: "DAT_009a2878/87c/880 — TGPoint3 zero-vector sentinel used by FUN_005ad910 for up-override / lateral-override params"
    address: 0x009a2878
    function: zero_vector_sentinel
    confidence: medium
    note: "OQ3 — sentinel use confirmed; semantic 'up override / lateral override' is hypothesized from branch structure but not byte-anchored."
  - claim: "DAT_00980df0/df4/df8 — global forward direction (X,Y,Z) read by GetForwardDirection 0x00434cd0"
    address: 0x00980df0
    function: global_forward_direction
    confidence: high
  - claim: "Event 0x008000EF — single InSystemWarp event posted by BOTH engage (0x005ac6e0) and stop (0x005acdb0) paths"
    address: null
    function: ET_IN_SYSTEM_WARP_event
    confidence: high
    note: "C5 — replaces fabricated `ET_EXITED_WARP`. Only one warp event exists."
  # ---- Weapon integration (4 functions) ----
  - claim: "WeaponSystem__FindTargetEntry at 0x00585360 — walks +0xC4 target linked list by object ID"
    address: 0x00585360
    function: WeaponSystem__FindTargetEntry
    confidence: high
  - claim: "WeaponSystem__FindTargetByObjectID at 0x00584080 — extracts obj+4 ID, delegates to FindTargetEntry"
    address: 0x00584080
    function: WeaponSystem__FindTargetByObjectID
    confidence: high
  - claim: "WeaponSystem__SetTargetOffset at 0x00585580 — updates target entry offset, clears child subsystem targets"
    address: 0x00585580
    function: WeaponSystem__SetTargetOffset
    confidence: high
  - claim: "Subsystem__AsWeaponSystem at 0x00583f60 — IsA(0x801D) cast check; precisely a `vtable[8](0x801D)` cast"
    address: 0x00583f60
    function: Subsystem__AsWeaponSystem
    confidence: high
  - claim: "Ship__StopFiringWeapons at 0x005b0bb0 — walks +0x284 subsystem list, filters via IsA(0x801D), calls vtable[+0x90] StopFiring on each WeaponSystem"
    address: 0x005b0bb0
    function: Ship__StopFiringWeapons
    confidence: high
  # ---- Scene graph (6 functions) ----
  - claim: "TGSceneGraph__FindObjectByID at 0x00434e70 — uses class ID 0x8003; walks DAT_0097e9cc roots"
    address: 0x00434e70
    function: TGSceneGraph__FindObjectByID
    confidence: high
  - claim: "TGSceneGraph__GetObjectByID at 0x00434e00 — hash lookup then IsA(0x8003) cast"
    address: 0x00434e00
    function: TGSceneGraph__GetObjectByID
    confidence: high
  - claim: "GetForwardDirection at 0x00434cd0 — reads DAT_00980df0 (global forward X,Y,Z)"
    address: 0x00434cd0
    function: GetForwardDirection
    confidence: high
  - claim: "CastToShipClass at 0x005ab670 — IsA(0x8008) cast"
    address: 0x005ab670
    function: CastToShipClass
    confidence: high
    note: "Ghidra symbol: CastToShipClass. Doc names this `TGObject__AsShip`."
  - claim: "TGObject__SetVelocity at 0x005a04c0 — writes NiAVObject +0x98/+0x9C/+0xA0 velocity components via ship+0x18"
    address: 0x005a04c0
    function: TGObject__SetVelocity
    confidence: high
  - claim: "TGObject__SetDirtyFlag at 0x006d5e80 — toggles bit 2 of *(ushort*)(ship+0x18) flags (marks for StateUpdate)"
    address: 0x006d5e80
    function: TGObject__SetDirtyFlag
    confidence: high
  # ---- Subsystems (8 functions) ----
  - claim: "Subsystem__GetProperty at 0x00560fc0 — returns +0x18 (SubsystemProperty pointer)"
    address: 0x00560fc0
    function: Subsystem__GetProperty
    confidence: high
  - claim: "Subsystem__IsActive at 0x0056c340 — reads property+0x25 active byte flag"
    address: 0x0056c340
    function: Subsystem__IsActive
    confidence: high
  - claim: "Subsystem__GetRadius at 0x0056b940 — reads property+0x44 float (radius)"
    address: 0x0056b940
    function: Subsystem__GetRadius
    confidence: high
  - claim: "ShipSubsystem__GetChildSubsystem at 0x0056c570 — array bounds check, returns child at index from +0x20"
    address: 0x0056c570
    function: ShipSubsystem__GetChildSubsystem
    confidence: high
    note: "Ghidra symbol. Doc names this `Subsystem__GetChild`."
  - claim: "PoweredSubsystem__GetEfficiency at 0x005822d0 — returns (received_power / wanted_power) = (+0xFC / +0xF8), clamped to [0,1]"
    address: 0x005822d0
    function: PoweredSubsystem__GetEfficiency
    confidence: high
  - claim: "Ship__StartGetSubsystemMatch at 0x005ac370 / Ship__GetNextSubsystemMatch at 0x005ac390 — iterator over +0x284 list filtered by vtable[8](typeID)"
    address: 0x005ac370
    function: Ship__GetSubsystemMatch_iterator
    confidence: high
  - claim: "Ship__AddSubsystemToLists at 0x005b3e50 — adds subsystem to +0x284 head, classifies via IsA checks (weapon-classified entries go to +0x29C/+0x2A0 weapon sub-list)"
    address: 0x005b3e50
    function: Ship__AddSubsystemToLists
    confidence: high
    note: "Ghidra symbol. Doc names this `Ship__AddSubsystem`."
  # ---- Collision queries (4 functions) ----
  - claim: "CollisionQuery__Execute at 0x005a7cf0 — sweep-and-prune query for spatial obstacle search"
    address: 0x005a7cf0
    function: CollisionQuery__Execute
    confidence: high
  - claim: "CollisionQuery__GetNextResult at 0x005a8320 — iterator over collision query results"
    address: 0x005a8320
    function: CollisionQuery__GetNextResult
    confidence: high
  - claim: "CollisionQuery__Destroy at 0x005a8350 — query cleanup/free"
    address: 0x005a8350
    function: CollisionQuery__Destroy
    confidence: high
  - claim: "RaySphereIntersect at 0x004570d0 — line-sphere intersection test, returns 0/1/2 hits"
    address: 0x004570d0
    function: RaySphereIntersect
    confidence: high
  # ---- Targeting events (cross-anchored) ----
  - claim: "Event 0x800058 (ET_TARGET_WAS_CHANGED) — posted by Ship_SetTarget inner (0x005ae210) at 0x005ae27a"
    address: null
    function: ET_TARGET_WAS_CHANGED
    confidence: high
  - claim: "Event 0x800059 (likely ET_TARGET_OFFSET_CHANGED, undocumented) — posted by Ship__UpdateWeaponTargets (0x005ae430)"
    address: null
    function: ET_TARGET_OFFSET_CHANGED_inferred
    confidence: medium
    note: "Clar1 — semantic inferred from positional pattern between 0x800058 and 0x80005A."
  - claim: "Event 0x80005A (ET_TARGET_SUBSYSTEM_SET) — posted by Ship__OnTargetChanged (0x005ae2c0)"
    address: null
    function: ET_TARGET_SUBSYSTEM_SET
    confidence: high
  - claim: "Event 0x008000ED (ET_START_WARP) — posted by opcode 0x10 (StartWarp) jump-table slot dispatching to FUN_0069fda0"
    address: null
    function: ET_START_WARP
    confidence: high
companions:
  - docs/gameplay/ai-architecture.md
  - docs/gameplay/damage-system.md
  - docs/gameplay/power-system.md
  - docs/gameplay/collision-detection-system.md
  - docs/protocol/stateupdate.md
  - ../OpenBC/docs/ship-movement.md
---

> [!NOTE]
> **5 corrections (2 HIGH + 3 MEDIUM) + 8 clarifications + 3 OQs**. **C1 HIGH (OpenBC BLOCKING):** Ship velocity field offsets SWAPPED — `+0x1F8` is the **speed scalar** (NOT direction), `+0x1FC..+0x204` is the **direction TGPoint3** (NOT speed scalar). **C2 HIGH:** turn convergence inverted — `TurnTowardDifference` at 0x005ad4d0 is the ACTUAL sink, not `FUN_005ad910`. **C3 MEDIUM:** Ship `+0x87` "target list cycle index" is FABRICATED — it's a Ghidra `param_1[index]` artifact pointing to the SAME `+0x21C` target ID field. **C4 MEDIUM:** InSystemWarp engage distance is **50.0f** at `_DAT_008944b4`, NOT 295. **C5 MEDIUM:** `ET_EXITED_WARP` is FABRICATED — single warp event `0x008000EF` is posted by BOTH engage and stop paths. All targeting event IDs (0x800058 / 0x80005A), all scene-graph addresses, all subsystem accessors, all collision-query addresses, and the InSystemWarp opcode wiring are byte-confirmed. See [v5-evidence-header.md](../guides/v5-evidence-header.md) for what the frontmatter means.

# Ship Navigation & Targeting

Reverse-engineered implementation details of Bridge Commander's ship targeting pipeline, movement model, turn computation, and in-system warp. These are the C++ functions that AI scripts and player input call to control ship movement.

---

## C1 (HIGH, OpenBC BLOCKING) — Ship velocity field offsets are SWAPPED

The prior version of §3 "Ship Velocity Fields" listed:

| Offset | Type | Field |
|--------|------|-------|
| +0x1F8 | float[3] | Impulse direction |
| +0x1FC | float | Impulse speed scalar |

**This is wrong.** The actual layout, byte-confirmed against `SetImpulse` (`FUN_005ac470` at 0x005ac470 [v5-validated 2026-05-28]):

| Offset | Type | Field |
|--------|------|-------|
| +0x1F8 | float | **Impulse speed scalar** (clamped 0.0–1.0) [v5-validated 2026-05-28] |
| +0x1FC..+0x200..+0x204 | TGPoint3 | **Impulse direction** (model or world space) [v5-validated 2026-05-28] |
| +0x208 | byte | **Coord-space flag** (`DIRECTION_MODEL_SPACE` / `DIRECTION_WORLD_SPACE`) [v5-validated 2026-05-28] |
| +0x1E4 | byte | "Impulse command pending" flag set to 1 by SetImpulse [v5-validated 2026-05-28] |

The author was misled by parameter ordering: SetImpulse's C++ signature is `(speed, direction, space)`, and `param_1[0x7E] = speed_param_2` (0x7E × 4 = 0x1F8) was read as "+0x1F8 = direction". Always read disasm to verify offset semantics, not decompiled C field syntax.

> **OpenBC clean-room cascade BLOCKING (2026-05-28)**: OpenBC clean-room implementations must use the corrected layout. Treating `+0x1F8` as a 3-float direction and `+0x1FC` as a scalar speed will produce undefined behavior on the read/write path (writes will scribble into the direction vector; reads will treat one of the direction components as a scalar speed). See [../OpenBC/docs/ship-movement.md](../../OpenBC/docs/ship-movement.md) for clean-room reconciliation work that must follow.

---

## 1. Targeting Pipeline

### SetTarget → SetTargetInternal → OnTargetChanged

The full call chain when a target is set (by AI, player, or network):

```
Ship_SetTarget_wrapper (0x005ae1e0)                         [v5-validated 2026-05-28]
  ├── TGSceneGraph__FindObjectByID (0x00434e70)             // resolve target name → object
  └── Ship_SetTarget_inner (0x005ae210)                     [v5-validated 2026-05-28]
        ├── Fire ET_TARGET_WAS_CHANGED (0x800058)           // TGObjPtrEvent with old target ID  [v5-validated 2026-05-28]
        ├── Ship__StopFiringWeapons (0x005b0bb0)            // stop current weapon fire          [v5-validated 2026-05-28]
        └── Ship__OnTargetChanged (0x005ae2c0)              [v5-validated 2026-05-28]
              ├── Ship__UpdateWeaponTargets (0x005ae430)    // walk +0x284 subsystem list
              │     └── Fire 0x800059 (likely ET_TARGET_OFFSET_CHANGED, undocumented — Clar1)
              └── Fire ET_TARGET_SUBSYSTEM_SET (0x80005A)   [v5-validated 2026-05-28]
```

> [!NOTE]
> The Ghidra symbol at 0x005ae210 is `Ship_SetTarget` (single underscore). This doc names the inner function `Ship__SetTargetInternal` to disambiguate from the wrapper. Orthography only, not a correction.

### Function Details

| Function | Address | Calling Convention | Description |
|----------|---------|-------------------|-------------|
| Ship_SetTarget (wrapper) | 0x005ae1e0 [v5-validated 2026-05-28] | __thiscall | SWIG `ShipClass_SetTarget` target. Takes target name string, calls FindObjectByID + Ship_SetTarget_inner |
| Ship__GetTarget | 0x005ae170 [v5-validated 2026-05-28] | __thiscall | Reads +0x21C (target object ID), validates target is alive, returns object or NULL |
| Ship_SetTarget (inner) | 0x005ae210 [v5-validated 2026-05-28] | __thiscall | Core implementation. Fires ET_TARGET_WAS_CHANGED (0x800058) at 0x005ae27a, stops weapons, updates subsystems |
| Ship__OnTargetChanged | 0x005ae2c0 [v5-validated 2026-05-28] | __thiscall | Post-change hook. Updates weapon target entries, fires ET_TARGET_SUBSYSTEM_SET (0x80005A) |
| Ship__UpdateWeaponTargets | 0x005ae430 [v5-validated 2026-05-28] | __thiscall | Walks +0x284 subsystem linked list, updates each weapon system's target entry, fires 0x800059 (Clar1) |
| Ship__StopFiringWeapons | 0x005b0bb0 [v5-validated 2026-05-28] | __thiscall | Walks +0x284, finds WeaponSystems via `IsA(0x801D)` via FUN_00583f60, calls vtable[+0x90] on each |
| Ship__GetTargetOffset | 0x005ae650 [v5-validated 2026-05-28] | __thiscall | Returns +0x228 target offset (manual aim point or auto-computed from target bounding box) |
| Ship__GetTargetSubsystemObject | 0x005ae630 [v5-validated 2026-05-28] | __thiscall | Resolves +0x220 target subsystem ID via ForwardEvent |

### Target Cycling

| Function | Address | Description |
|----------|---------|-------------|
| Ship__GetNextTarget | 0x005ae6d0 [v5-validated 2026-05-28] | Binary-search step in sorted target list, **seeded by `+0x21C` (current target ID)** — NOT by a separate cycle index (see C3 below) |

> [!IMPORTANT]
> **C3 (MEDIUM) — Ship `+0x87` "Target list cycle index" is fabricated**. The prior doc listed `+0x87 | byte | Target list cycle index` in the Ship target-fields table. There is no such field. The decompiler's `param_1[0x87]` (with `param_1` typed `int*`) resolves to `*(param_1 + 0x21C)` — the SAME target ID field, accessed via 4-byte-stride indexing. Disasm at 0x005ae6e0 reads `MOV EDI, [ESI+0x21C]` directly. `GetNextTarget` seeds its binary search with the current target ID, not a separate cycle index byte. This is the same trap as the C1 swap in a different form: integer-index access through `int*` multiplies by 4 implicitly.

### Target Fields on Ship

| Offset | Type | Field |
|--------|------|-------|
| +0x21C | int32 | Current target object ID [v5-validated 2026-05-28] (also seeds GetNextTarget binary search) |
| +0x220 | int32 | Target subsystem ID (for precision targeting) [v5-validated 2026-05-28] |
| +0x224 | byte | Manual aim flag [v5-validated 2026-05-28] |
| +0x228..+0x230 | TGPoint3 | Target offset (aim point relative to target origin) [v5-validated 2026-05-28] |

---

## 2. Turn Computation

### Entry Points

Three entry points for directing a ship's rotation:

| Function | Address | Input | Description |
|----------|---------|-------|-------------|
| Ship__TurnTowardLocation | 0x005ad3a0 [v5-validated 2026-05-28] | TGPoint3 (world position) | Normalizes direction to target point, calls TurnTowardDirection |
| Ship__TurnTowardDirection | 0x005ad450 [v5-validated 2026-05-28] | TGPoint3 (unit direction) | Reads current orientation via `vtable[0xAC]` (GetOrientationOrInverse), calls quaternion-orient routine FUN_005ad910 |
| Ship__TurnTowardDifference | 0x005ad4d0 [v5-validated 2026-05-28] | TGPoint3 (direction delta) | SWIG `ShipClass_TurnTowardDifference` target. Also the **deepest sink** of the call chain (see C2 below). |

> [!IMPORTANT]
> **C2 (HIGH) — Turn convergence is inverted**. The prior doc said "All paths converge on `ComputeTurnAngularVelocity` (0x005ad910)". That's the wrong direction. The actual call chain (xref-confirmed) is:
>
> ```
> Ship__TurnTowardLocation (0x005ad3a0)
>   → Ship__TurnTowardDirection (0x005ad450)
>     → FUN_005ad910 (quaternion-orient routine — not the sink)
>       → Ship__TurnTowardDifference (0x005ad4d0)   ← ACTUAL SINK
> ```
>
> `TurnTowardDifference` at 0x005ad4d0 has exactly ONE caller (0x005ad910). `FUN_005ad910` has TWO callers (0x005ad450 and one named function). The SWIG `ShipClass_TurnTowardDifference` target is correct, but `TurnTowardDifference` is the DEEPEST function in the chain, not just a peer entry point. The math kernel (iterative bisection on collision/intercept, ~109 lines) lives at 0x005ad4d0. `FUN_005ad910` reads the orientation matrix at `ship+0xE0` via `FUN_0041cbd0` (quaternion-from-matrix) and the forward axis via `vtable[0xB0]` (GetForwardDirection), then delegates the actual bisection to `TurnTowardDifference`.

### FUN_005ad910 — Quaternion-orient routine (not the sink)

| Function | Address | Description |
|----------|---------|-------------|
| FUN_005ad910 | 0x005ad910 [v5-validated 2026-05-28] | Reads forward axis via `vtable[0xB0]`; uses TGPoint3 zero-vector sentinel `DAT_009a2878/87c/880` for two override params; calls `TurnTowardDifference` (0x005ad4d0) for the actual angular-velocity computation. |

Key behaviors of `FUN_005ad910`:
- Reads ship orientation matrix at `ship+0xE0`
- Forward axis is the primary alignment target (sourced via `vtable[0xB0]` GetForwardDirection)
- Has two TGPoint3 override params (`param_4`, `param_5`) initialized to a zero-vector sentinel — likely "up override" and "lateral override" but the semantic is not byte-anchored (OQ3)
- Delegates the actual blending math to `TurnTowardDifference`

> [!IMPORTANT]
> **OQ3 — "slerp-style" framing is speculative**. The prior doc described `FUN_005ad910` as "quaternion slerp-style turn with constraints". Actual decomp shows linear vector blending with a scalar (`param_3`) and conditional sign-flip — not true quaternion slerp math. The angular-velocity output is plausibly correct but the math kernel is not slerp.

### SetTargetAngularVelocityDirect

| Function | Address | Description |
|----------|---------|-------------|
| Ship__SetTargetAngularVelocityDirect | 0x005ad290 [v5-validated 2026-05-28] | SWIG target. Bypasses turn computation. Writes explicit angular velocity at +0x1E8..+0x1F0 and sets +0x1E5 "angular-velocity command pending" byte. |

Used by AI scripts that compute their own rotation (e.g., manual maneuver patterns).

### Supporting Math

| Function | Address | Description |
|----------|---------|-------------|
| NiMatrix3__TransformVector | 0x00813a40 | 3x3 matrix * vec3 (rotation transform) |
| NiMatrix3__TransposeTransformVector | 0x00813aa0 | Transpose multiply (inverse rotation for world→model) |
| TGPoint3__Cross | 0x0045c1a0 | Cross product |
| TGPoint3__UnitCross | 0x00581e60 | Normalized cross product |
| TGPoint3__MultMatrix | 0x0045e8d0 | Point * matrix transform |
| GetForwardDirection | 0x00434cd0 [v5-validated 2026-05-28] | Returns global forward direction vector (from `DAT_00980df0/df4/df8`) |

---

## 3. Impulse Movement Model

### SetImpulse / SetSpeed

| Function | Address | Calling Convention | Description |
|----------|---------|-------------------|-------------|
| Ship__SetImpulse | 0x005ac470 [v5-validated 2026-05-28] | __thiscall | Clamps speed scalar to 0.0–1.0; stores at `ship+0x1F8`; writes direction TGPoint3 at `+0x1FC..+0x204`; coord-space flag at `+0x208`; sets `+0x1E4` "command pending" byte to 1 |
| Ship__SetSpeed | 0x005ac590 [v5-validated 2026-05-28] | __thiscall | Reads ImpulseEngineSubsystem+0xAC (base max speed), divides input by it, delegates to SetImpulse |

`SetImpulse` takes a normalized speed (0.0 = stop, 1.0 = full impulse), a direction vector, and a coordinate space flag (`DIRECTION_MODEL_SPACE` or `DIRECTION_WORLD_SPACE`).

`SetSpeed` is a convenience wrapper: it takes an absolute speed value, divides by the impulse engine's base max speed (`ImpulseEngineSubsystem+0xAC`), and delegates to `SetImpulse`. Used by AI scripts that compute speed in absolute units.

### Effective Speed

The actual speed a ship achieves depends on impulse engine health and power efficiency:

| Function | Address | Description |
|----------|---------|-------------|
| ImpulseEngineSubsystem__GetEffectiveSpeed | 0x00561330 [v5-validated 2026-05-28] | max_speed * (child_health_aggregate * power_efficiency) |
| ImpulseEngineSubsystem__GetEffectiveAcceleration | 0x00561230 [v5-validated 2026-05-28] | Same pattern for acceleration |
| ImpulseEngineSubsystem_Ctor | 0x00561050 [v5-validated 2026-05-28] | Constructor; sets vtable to `0x00892d10` (cross-anchored from power-system.md) |

Effective speed formula:
```
effective_max_speed = base_max_speed * health_factor * power_efficiency
```

Where:
- `base_max_speed` comes from the ship's impulse engine property (ImpulseEngineSubsystem+0xAC)
- `health_factor` = aggregate health of impulse engine child subsystems
- `power_efficiency` = `PoweredSubsystem__GetEfficiency` (0x005822d0) = `(+0xFC / +0xF8)` (received / wanted), clamped to [0, 1]

The actual decomp shows the math as `(1 - efficiency_complement) * (base_max - sum(child_damage * max/n)) * ship+0x90` — high-level "max × health × efficiency" is correct.

A damaged or under-powered impulse engine directly reduces maximum achievable speed and acceleration.

### Ship Velocity Fields (corrected)

| Offset | Type | Field |
|--------|------|-------|
| +0x1E4 | byte | "Impulse command pending" flag (set to 1 by SetImpulse) [v5-validated 2026-05-28] |
| +0x1E5 | byte | "Angular-velocity command pending" flag (set by SetTargetAngularVelocityDirect) [v5-validated 2026-05-28] |
| +0x1E8..+0x1F0 | TGPoint3 | Explicit angular velocity (written by SetTargetAngularVelocityDirect) [v5-validated 2026-05-28] |
| +0x1F8 | float | **Impulse speed scalar (0.0–1.0)** [v5-validated 2026-05-28] |
| +0x1FC..+0x200..+0x204 | TGPoint3 | **Impulse direction (model or world space)** [v5-validated 2026-05-28] |
| +0x208 | byte | **Coord-space flag** (DIRECTION_MODEL_SPACE / DIRECTION_WORLD_SPACE) [v5-validated 2026-05-28] |

These are the *commanded* values. Actual velocity is on the NiAVObject at the standard NI offsets (+0x98/+0x9C/+0xA0 via `ship+0x18` NiNode).

See **C1** at the top of this doc for the full swap analysis and OpenBC cascade.

---

## 4. In-System Warp

| Function | Address | Description |
|----------|---------|-------------|
| Ship__InSystemWarp | 0x005ac6e0 [v5-validated 2026-05-28] | SWIG `ShipClass_InSystemWarp` target. Pathfinding + obstacle avoidance. Fires event 0x008000EF. |
| Ship__StopInSystemWarp | 0x005acdb0 [v5-validated 2026-05-28] | Clears warp state, fires the **same** event 0x008000EF, restores velocity |

In-system warp moves a ship at very high speed to a distant object within the same set. Used by the Intercept AI when the target is farther than the engage threshold.

> [!IMPORTANT]
> **C4 (MEDIUM) — Engage distance is 50.0f, NOT 295**. The prior doc claimed "default 295 units" referring to `fInSystemWarpDistance`. The binary constant in InSystemWarp (0x005ac6e0) at `_DAT_008944b4` reads `0x42480000 = 50.0f`. The C-level engage gate is `fVar7 > 50.0f`. The "295" value may come from a Python `Intercept.py` script — but the C++ binary value is 50.0. OpenBC implementations should use 50.0 unless deliberately wrapping the Python script's threshold.

> [!IMPORTANT]
> **C5 (MEDIUM) — There is only one warp event, not two**. The prior doc referenced a separate `ET_EXITED_WARP` event ID. Fabricated. Both `InSystemWarp` (engage, 0x005ac6e0) and `StopInSystemWarp` (0x005acdb0) post the SAME event ID `0x008000EF`. Listeners that care about engage-vs-stop must consult ship state (`+0x84` warp-engaged byte, `+0x210` warp-active byte) rather than dispatching on event ID alone.

### Warp Constants (byte-confirmed)

| Constant | Address | Value | Meaning |
|----------|---------|-------|---------|
| `_DAT_008944b4` | 0x008944b4 [v5-validated 2026-05-28] | `0x42480000` = **50.0f** | InSystemWarp engage distance threshold |
| `_DAT_008944b0` | 0x008944b0 [v5-validated 2026-05-28] | `0x42960000` = 75.0f | InSystemWarp velocity multiplier |
| `_DAT_008942e0` | 0x008942e0 [v5-validated 2026-05-28] | `0x3F7746EA` ≈ 0.9659 | Warp arrival dot-product threshold = `cos(15°)`. When `dot(forward, to_target) < this`, StopInSystemWarp fires. |
| Event `0x008000EF` | n/a [v5-validated 2026-05-28] | — | Single InSystemWarp event posted by BOTH engage and stop paths (see C5) |

### Warp State Fields on Ship

| Offset | Type | Field |
|--------|------|-------|
| +0x84 | byte | Warp-engaged flag (set by InSystemWarp on success) [v5-validated 2026-05-28] |
| +0x210 | byte | Warp-active tracking flag [v5-validated 2026-05-28] |
| +0x214 | (varies) | Warp delta state [v5-validated 2026-05-28] |
| +0x218 | (varies) | Warp delta state [v5-validated 2026-05-28] |

### Obstacle Avoidance (Clar — class-ID exclusion list)

`InSystemWarp`'s obstacle-avoidance pass IGNORES objects whose `IsA()` returns any of the following class IDs (likely fighter, projectile, dynamic-effect, AI-flag classes):

| Class ID | Likely Class | Reason ignored |
|----------|--------------|----------------|
| 0x80E2 | (fighter-like) | Too small to be a navigation obstacle [v5-validated 2026-05-28] |
| 0x80DE | (projectile-like) | Transient — would jitter avoidance [v5-validated 2026-05-28] |
| 0x8125 | (dynamic-effect-like) | Visual-only [v5-validated 2026-05-28] |
| 0x800E | (AI-flag-like) | Not a physical object [v5-validated 2026-05-28] |

These are not in the Python `Intercept.AdjustDestinationForLargeObstacles` path — they're C-level filters inside the warp engage routine.

### Network Opcode

| Opcode | Address | Meaning |
|--------|---------|---------|
| 0x10 (StartWarp) | jump table at 0x0069F534 slot 14 [v5-validated 2026-05-28] | Dispatches to event handler `0x0069fda0` with `PUSH 0x008000ED` (ET_START_WARP) |

The opcode IS wired up — it's a slot in the MultiplayerGame jump table (slot 14 = index 14 × 4 = 0x38 from base 0x0069F534), and the handler posts event `0x008000ED` (ET_START_WARP). Whether opcode 0x10 is actually sent on the wire in stock multiplayer play is [Open Question 1](#open-questions) — the C-level wiring exists but stock-trace verification is pending.

---

## 5. Weapon System Integration

When a target changes, the targeting pipeline updates all weapon systems:

| Function | Address | Description |
|----------|---------|-------------|
| WeaponSystem__FindTargetEntry | 0x00585360 [v5-validated 2026-05-28] | Searches +0xC4 target list by object ID |
| WeaponSystem__FindTargetByObjectID | 0x00584080 [v5-validated 2026-05-28] | Extracts obj+4 ID, delegates to FindTargetEntry |
| WeaponSystem__SetTargetOffset | 0x00585580 [v5-validated 2026-05-28] | Updates target entry offset, clears child subsystem targets |
| Subsystem__AsWeaponSystem | 0x00583f60 [v5-validated 2026-05-28] | `IsA(0x801D)` cast check (precisely `vtable[8](0x801D)`) |

The weapon target list at WeaponSystem+0xC4 maps object IDs to aim data. When `Ship__UpdateWeaponTargets` runs (after target change), it walks all subsystems via the +0x284 linked list and updates weapon entries.

### Weapon-Classified Subsystem Sub-list

`Ship__AddSubsystemToLists` at `0x005b3e50` [v5-validated 2026-05-28] classifies each added subsystem via IsA checks. Weapon-classified entries are additionally threaded onto a separate sub-list:

| Offset | Field |
|--------|-------|
| +0x29C | Weapon-classified subsystem sub-list head [v5-validated 2026-05-28] |
| +0x2A0 | Weapon-classified subsystem sub-list tail [v5-validated 2026-05-28] |

---

## 6. Scene Graph Lookups

| Function | Address | Description |
|----------|---------|-------------|
| TGSceneGraph__FindObjectByID | 0x00434e70 [v5-validated 2026-05-28] | Searches by ID across scene roots (`DAT_0097e9cc`); uses class ID 0x8003 |
| TGSceneGraph__GetObjectByID | 0x00434e00 [v5-validated 2026-05-28] | Hash lookup then IsA(0x8003) cast |
| TGObjectTree__FindByHashAndTrack | 0x0040fe00 | Hash bucket walk + tracking call |
| TGObjectTree__GetNextSorted | 0x0040fe80 | Binary search in sorted array, wraps on boundary |
| CastToShipClass | 0x005ab670 [v5-validated 2026-05-28] | IsA(0x8008) cast, returns NULL if not ship (Ghidra symbol: `CastToShipClass`; doc previously named `TGObject__AsShip`) |
| TGObject__SetVelocity | 0x005a04c0 [v5-validated 2026-05-28] | Sets NiAVObject+0x98/+0x9C/+0xA0 velocity via +0x18 |
| TGObject__SetDirtyFlag | 0x006d5e80 [v5-validated 2026-05-28] | Sets/clears bit 2 of `*(ushort*)(+0x18)` flags (marks for state update) |

`Ship_SetTarget` calls `FindObjectByID` to resolve a target name to an object pointer before passing it to the inner `Ship_SetTarget`.

---

## 7. Subsystem Helpers

| Function | Address | Description |
|----------|---------|-------------|
| Ship__StartGetSubsystemMatch | 0x005ac370 [v5-validated 2026-05-28] | Allocates iterator for type-matching subsystem traversal |
| Ship__GetNextSubsystemMatch | 0x005ac390 [v5-validated 2026-05-28] | Returns next subsystem matching requested type ID (filters via `vtable[8](typeID)`) |
| Ship__AddSubsystemToLists | 0x005b3e50 [v5-validated 2026-05-28] | Adds to +0x284 list, classifies by IsA checks (weapon-classified entries → +0x29C/+0x2A0) |
| Subsystem__IsActive | 0x0056c340 [v5-validated 2026-05-28] | Reads property+0x25 active byte flag via +0x18 |
| Subsystem__GetRadius | 0x0056b940 [v5-validated 2026-05-28] | Reads property+0x44 (radius float) |
| ShipSubsystem__GetChildSubsystem | 0x0056c570 [v5-validated 2026-05-28] | Array bounds check, returns child at index from +0x20 (Ghidra symbol; doc previously named `Subsystem__GetChild`) |
| Subsystem__GetProperty | 0x00560fc0 [v5-validated 2026-05-28] | Returns +0x18 (SubsystemProperty pointer) |
| PoweredSubsystem__GetEfficiency | 0x005822d0 [v5-validated 2026-05-28] | Returns +0xFC / +0xF8 (received/wanted), clamped |

### Subsystem List Fields on Ship

| Offset | Field |
|--------|-------|
| +0x280 | Subsystem list count [v5-validated 2026-05-28] |
| +0x284 | Subsystem list head [v5-validated 2026-05-28] |
| +0x288 | Subsystem list tail [v5-validated 2026-05-28] |
| +0x29C | Weapon-classified sub-list head [v5-validated 2026-05-28] |
| +0x2A0 | Weapon-classified sub-list tail [v5-validated 2026-05-28] |
| +0x2CC | ImpulseEngineSubsystem ptr (vtable `0x00892d10`) [v5-validated 2026-05-28 — cross-anchored from power-system.md] |
| +0x2D0 | WarpEngineSubsystem ptr (vtable `0x00893040`) [v5-validated 2026-05-28 — cross-anchored from power-system.md] |

---

## 8. Collision Queries

Used by AI obstacle avoidance (`Intercept.AdjustDestinationForLargeObstacles` and InSystemWarp internal):

| Function | Address | Description |
|----------|---------|-------------|
| CollisionQuery__Execute | 0x005a7cf0 [v5-validated 2026-05-28] | Sweep-and-prune collision query for spatial search |
| CollisionQuery__GetNextResult | 0x005a8320 [v5-validated 2026-05-28] | Iterator over collision results |
| CollisionQuery__Destroy | 0x005a8350 [v5-validated 2026-05-28] | Cleanup/free |
| RaySphereIntersect | 0x004570d0 [v5-validated 2026-05-28] | Line-sphere intersection test, returns 0/1/2 hits |

The proximity manager (`pSet.GetProximityManager()`) provides `GetLineIntersectObjects()` for line-of-sight and obstacle detection.

---

## 9. Network Authority

Position and orientation are **client-authoritative** in stock Bridge Commander multiplayer. Each client controls its own ship's movement; the host does not validate or simulate other players' physics.

Replication path:
1. Client runs AI/player input → calls SetImpulse/TurnTowardLocation → physics updates position
2. Client serializes position/orientation/velocity into StateUpdate (opcode 0x1C, dirty flag bits 0x01 + 0x02)
3. Host receives StateUpdate → forwards to all other clients (relay-all architecture)
4. Other clients apply received position/orientation to remote ship objects

There is no server-side movement simulation or desync correction in stock BC.

### Relevant Opcodes

| Opcode | Name | Relevance |
|--------|------|-----------|
| 0x1C | StateUpdate | Position (flag 0x01) + orientation (flag 0x02) replication |
| 0x10 | StartWarp | In-system warp — wiring confirmed (jump table slot 14 → event 0x008000ED). Stock-MP wire usage is OQ1. |
| 0x07 | StartFiring | Weapon fire begin (movement-adjacent) |
| 0x08 | StopFiring | Weapon fire end |

---

## Open Questions

1. **OQ1 — Stock-MP wire usage of opcode 0x10 (StartWarp)**: The opcode IS wired up at the C-level (jump-table slot 14 dispatches to event `0x008000ED`), but whether it actually appears on the wire in stock multiplayer play needs cross-check against [valentines-day-battle-analysis.md](../analysis/valentines-day-battle-analysis.md) or similar full-session traces. The prior doc's claim "unused in stock multiplayer" is a usage assertion, not a binary one.

2. **OQ2 — FUN_005ad910 override params**: The quaternion-orient routine takes two TGPoint3 ptrs (`param_4`, `param_5`) that are initialized to a zero-vector sentinel (`DAT_009a2878/87c/880`). The conditional branches inside the body suggest these are "up override" and "lateral override" inputs, but the semantic is not byte-anchored to any string or comment. The C entry point 0x005ac6e0 has only one named C caller (0x005adb55), so most callers are AI Python scripts going through SWIG.

3. **OQ3 — "Slerp-style" framing is speculative**: The prior doc described `FUN_005ad910` as "quaternion-based interpolation (slerp-style) ... preserves ship's up axis". Actual decomp shows linear vector blending with a scalar (`param_3`) and conditional sign-flip — not true quaternion slerp. The output (an angular velocity vector applied to the physics object) is plausible, but the math kernel is not slerp. The "preserves up axis" claim may be a downstream side effect of one of the two override params, but that's tied to OQ2.

---

## Related Documents

- [ai-architecture.md](ai-architecture.md) — AI behavior tree that drives these navigation functions
- [damage-system.md](damage-system.md) — Damage affecting impulse engine efficiency
- [power-system.md](power-system.md) — Power delivery affecting engine performance; cross-anchor for `ImpulseEngineSubsystem_Ctor` (0x00561050, vtable 0x00892d10) and WarpEngineSubsystem vtable
- [collision-detection-system.md](collision-detection-system.md) — Collision system that obstacle avoidance queries
- [../protocol/stateupdate.md](../protocol/stateupdate.md) — StateUpdate wire format for position/orientation replication (dirty bits 0x01 + 0x02)
- **OpenBC clean-room cascade**: [`../../OpenBC/docs/ship-movement.md`](../../OpenBC/docs/ship-movement.md) — must be updated for C1 velocity-field swap (BLOCKING) and C4 warp distance 50.0f
