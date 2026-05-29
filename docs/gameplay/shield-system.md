> [docs](../README.md) / [gameplay](README.md) / shield-system.md

---
title: Bridge Commander Shield System — RE Analysis
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
  - claim: "ShieldGenerator vtable at 0x00892f34 (xrefs from ctor 0x0056a04b + dtor 0x0056a1ad)"
    address: 0x00892f34
    function: null
    confidence: high
    note: "Vtable. Cross-anchor: rtti-class-catalog.md ShieldGenerator entry, class ID 0x8137."
  - claim: "ShieldProperty vtable at 0x00892fc4 (xrefs from ctor 0x0056b9c6 + dtor 0x0056bbad)"
    address: 0x00892fc4
    function: null
    confidence: high
    note: "Vtable. ShieldProperty inherits from PoweredSubsystemProperty."
  - claim: "ShieldGenerator ctor at 0x0056a000 initializes 6 facings at 1000 HP each, plus THREE float[6] arrays (curShields at +0xA8, shieldPercentage at +0xC0, additional float[6] at +0x130 each = 1.0), plus single float at +0xD8 (= 1.0)"
    address: 0x0056a000
    function: ShieldClass__ctor
    confidence: high
    note: "Disasm confirms additional float[6] @ +0x130 and single float @ +0xD8 — see Clar1. Original doc cites only 2 of the 3 float[6] arrays."
  - claim: "ShieldClass::WriteState at 0x0056ae10 — first instruction calls PoweredSubsystem__WriteState, then loops 0x60..0x78 (maxShields[6]) writing each via vtable[0x54] (write float), then calls vtable[0xd8] EndMarker"
    address: 0x0056ae10
    function: ShieldClass__WriteState
    confidence: high
    note: "C2 — pre-v5 misnamed this as 'ReadStream'. Cross-confirmed at docs/analysis/server-side-computation-model.md:436 which already labels this WriteState. Calls __ftol per float for compact integer storage."
  - claim: "BoostShield at 0x0056a420 — per-facing power-to-HP conversion: `hpGain = (chargePerSecond[facing] * powerAmount) / (NormalPowerWanted * 1/6)`; caps at maxShields[facing]; returns unused power for redistribution"
    address: 0x0056a420
    function: BoostShield
    completeness: 5.87
    effective: 89.0
    confidence: high
    note: "Decomp matches doc pseudocode line-for-line. Reads `property+0x48` as the NormalPowerWanted budget — see C1."
  - claim: "PoweredSubsystem_GetNormalPowerWanted at 0x005623d0 reads `*(float*)(property+0x48)` and returns it as the per-subsystem power requirement"
    address: 0x005623d0
    function: PoweredSubsystem_GetNormalPowerWanted
    confidence: high
    note: "This consumer is what establishes the runtime semantics of ShieldProperty+0x48 — see C1. Ctor at 0x0056b970 seeds the field with a random tick offset, but hardpoint scripts overwrite it at config time."
  - claim: "IsShieldBreached at 0x0056a620 returns NOT_BREACHED when `curShields[facing] >= 1.0 AND shieldDamaged[facing] == 0`; a facing with 0.5 HP is treated as breached"
    address: 0x0056a620
    function: IsShieldBreached
    confidence: high
    note: "C4 — pre-v5 doc implied threshold was 0. Threshold is actually 1.0f."
  - claim: "GetShieldFacingFromRay at 0x0056a690 — ellipsoid-to-sphere normalization using ship NiNode semi-axes at +0x24C/+0x250/+0x254, then ray-sphere intersect at FUN_004570d0, then NormalToFacing"
    address: 0x0056a690
    function: GetShieldFacingFromRay
    completeness: 0.0
    effective: 80.0
    confidence: high
    note: "Ship NiNode semi-axes accessed as piVar1[0x93/0x94/0x95]. FUN_004570d0 is the ray-sphere quadratic solver."
  - claim: "NormalToFacing at 0x0056a8d0 — axis-aligned maximum-component test (NOT a dot-product projection); switch maps dominant index {0,1,2,3,4,5} to facing enum {FRONT=0, TOP=2, RIGHT=5, REAR=1, BOTTOM=3, LEFT=4}"
    address: 0x0056a8d0
    function: NormalToFacing
    completeness: 0.0
    effective: 89.0
    confidence: high
    note: "Switch mapping byte-confirmed in decomp. Input is reordered to {Y,Z,X,-Y,-Z,-X}; the index of the maximum determines the facing via the switch table."
  - claim: "ScheduleShieldEvents at FUN_0056bde0 registers 5 timers — events 0x6d/0x6e use FUN_0056b960 (currentPower at property+0x40) as the interval; events 0x6f/0x70/0x71 use `0x358637bd` (~1e-6, effectively next-tick)"
    address: 0x0056bde0
    function: ScheduleShieldEvents
    confidence: high
    note: "Clar5 — pre-v5 doc said '0x6d-0x71' which is the correct range but glossed the per-tick semantics of 0x6f/0x70/0x71. TWO time bases."
  - claim: "HandleSetShieldState lives in the code-gap at 0x0056a230..0x0056aad0 (LAB_0056aae0); not promoted to a function in the Ghidra DB but is real reachable code, with xrefs invoking BoostShield at 0x0056a2e6 and 0x0056a392"
    address: 0x0056aae0
    function: null
    confidence: medium
    note: "Clar4 — confirmed reachable code. Registration string 'ShieldClass::HandleSetShieldState' at FUN_0056a1f0. OQ4 — needs Ghidra promotion for full analysis."
  - claim: "ProcessDamage at 0x00593e50 iterates the handler array at ship+0x128 (count at ship+0x130), calls FUN_004b1ff0 per handler, then FUN_00593ee0 for residual hull damage, then FUN_00593f30 (notification gate lives inside FUN_00593f30 — cross-anchor to damage-system.md)"
    address: 0x00593e50
    function: ProcessDamage
    confidence: high
    note: "Clar6 — handler-array iteration byte-confirmed. Notification gate inside FUN_00593f30 noted in damage-system memo."
  - claim: "AreaEffectDamage at 0x00593c10 — 6-iteration loop with `fStack_28 * _DAT_0088bacc` (1/6 multiplier); calls SetCurShields 6 times per target; overflow goes to hull via FUN_005afd70"
    address: 0x00593c10
    function: AreaEffectDamage
    completeness: 0.0
    effective: 81.1
    confidence: high
    note: "Per-facing absorption clamps each share independently — NOT all-or-nothing across the 6 facings."
  - claim: "DamageHandler_Process at 0x004b1ff0 — shield gate is `handler+0x20+0x18 != 0`; hull gate is OR of (`handler+0x1C+0x8 != 0`) AND (`handler+0x1C+0x9 != 0`)"
    address: 0x004b1ff0
    function: DamageHandler_Process
    confidence: high
    note: "Clar3 — pre-v5 doc cited only +0x9 byte of the hull gate; actual code is OR of both +0x8 and +0x9."
  - claim: "WeaponHitHandler at 0x005af010 — byte at `weaponHitInfo+0x58` determines shield-vs-hull effect: 0 = shield absorbed (shield visual), nonzero = shields breached (hull hit + DoDamage)"
    address: 0x005af010
    function: WeaponHitHandler
    confidence: high
    note: "Anchor for shield-vs-hull effect dispatch."
  - claim: "CloakShieldHandler at 0x0055f110 — param_2==1 schedules a delayed event 0x00800077 using `_DAT_008e4e20` (1.0s ShieldDelay); param_2!=1 posts event 0x00800079 immediately; writes cloak state at +0xB0 and +0xB4"
    address: 0x0055f110
    function: CloakShieldHandler
    confidence: high
    note: "ShieldDelay is a global at 0x008e4e20 — modifying via SWIG affects ALL ships."
  - claim: "StartCloaking at 0x0055f360 sets `cloakObj+0xAD = 1` (trying to cloak) — single-instruction confirmation"
    address: 0x0055f360
    function: StartCloaking
    confidence: high
    note: "Sibling anchor to CloakShieldHandler."
  - claim: "IsSubsystemDestroyed at 0x0056c350 — recursive check: self HP at +0x34 vs threshold, then iterates children"
    address: 0x0056c350
    function: IsSubsystemDestroyed
    confidence: high
    note: "Guard used by AreaEffectDamage and FUN_00485360 to bypass shield calculation when the subsystem is destroyed."
  - claim: "Random tick seed (ctor-time only) is the PRODUCT of two .rdata constants: `_DAT_00892fc0 = 0.33` (0x3EA8F5C3) and `_DAT_00888dbc = ~3.052e-5` (0x38000100); combined product ≈ 1.007e-5"
    address: 0x00892fc0
    function: ShieldProperty__ctor
    confidence: high
    note: "Clar2 — doc presented as single combined constant; binary uses two separate .rdata constants. ShieldProperty ctor at 0x0056b970 line `param_1[0x12] = fVar2 * _DAT_00888dbc`."
  - claim: ".rdata constant 0x0088bacc holds 0x3E2AAAAB = 1/6 (0.16666667) — per-facing share for AreaEffectDamage"
    address: 0x0088bacc
    function: null
    confidence: high
    note: "Bytes `abaa2a3e` byte-confirmed."
  - claim: ".rdata constant 0x00888b54 holds 0x00000000 = 0.0f — floor for SetCurShields clamp"
    address: 0x00888b54
    function: null
    confidence: high
    note: "Floor sentinel."
  - claim: ".rdata constant 0x00888860 holds 0x3F800000 = 1.0f — generic one constant (also IsShieldBreached threshold)"
    address: 0x00888860
    function: null
    confidence: high
    note: "Byte-confirmed."
  - claim: ".rdata constant 0x008887a8 holds 0x3F000000 = 0.5f — weapon damage radius scale (half constant)"
    address: 0x008887a8
    function: null
    confidence: high
    note: "Byte-confirmed."
  - claim: ".rdata constant 0x008e4e20 holds 0x3F800000 = 1.0f — CloakingSubsystem ShieldDelay (seconds); modifiable via SWIG SetShieldDelay; affects ALL cloaking subsystems"
    address: 0x008e4e20
    function: null
    confidence: high
    note: "Byte-confirmed. Global."
  - claim: ".rdata constant 0x008e4e1c holds 0x40A00000 = 5.0f — Cloak rate"
    address: 0x008e4e1c
    function: null
    confidence: high
    note: "Byte-confirmed."
  - claim: ".rdata constant 0x00888b58 holds 0x358637BD ≈ 9.99e-07 — epsilon / near-zero threshold; ALSO reused by ScheduleShieldEvents as the next-tick interval for events 0x6f/0x70/0x71"
    address: 0x00888b58
    function: null
    confidence: high
    note: "Byte-confirmed. Dual-use constant — see Clar5."
companions:
  - docs/gameplay/damage-system.md
  - docs/gameplay/power-system.md
  - docs/gameplay/cloaking-state-machine.md
  - docs/analysis/server-side-computation-model.md
  - docs/protocol/subsystem-integrity-hash.md
  - docs/protocol/stateupdate-subsystem-wire-format.md
  - docs/engine/rtti-class-catalog.md
supersedes:
  - 2026-02-15
---

# Bridge Commander Shield System — Reverse Engineering Analysis

> [!NOTE]
> This doc is `status: partial`. **v5 partial pass — algorithm, wire format, and constants are byte-confirmed**. 4 corrections (**C1 HIGH**: ShieldProperty +0x48 is `NormalPowerWanted` at runtime, NOT `tickPhaseOffset` — semantic mistake from ctor-time identity; **C2 HIGH**: 0x0056ae10 is `WriteState` not `ReadStream`; **C3 MEDIUM**: "Typical Recharge Values" table fabricated for 4 of 5 ships; **C4 LOW**: `IsShieldBreached` threshold is 1.0 not 0) + 6 clarifications (Clar1 third float[6] array at +0x130 and single float at +0xD8; Clar2 random seed is product of two constants; Clar3 hull gate is OR of two bytes; Clar4 HandleSetShieldState code-gap confirmed reachable; Clar5 ScheduleShieldEvents has two time bases; Clar6 ProcessDamage notification gate cross-reference) + 2 OQs. Per-facing 1/6 split, BoostShield power budget, ray-ellipsoid normalization, max-component facing test, and the cloak ShieldDelay are all byte-confirmed. See [v5-evidence-header.md](../guides/v5-evidence-header.md) for the standard. Source evidence: `.claude/agent-memory/game-archaeology-specialist/gameplay-foundation-shield-system-validation-20260528.md`.

Reverse-engineered from stbc.exe via Ghidra decompilation and binary analysis. High confidence — all addresses and constants verified against the game binary.

## Overview

Bridge Commander ships have 6 shield facings (front, rear, top, bottom, left, right), each with independent HP and recharge rate. The shield subsystem is modeled as an ellipsoidal shell around the ship; incoming damage is projected onto this ellipsoid to determine which facing absorbs it. Each facing can independently absorb damage up to its current HP, with overflow damage passing through to hull and subsystems.

## Shield Facing Enum

```c
enum ShieldFacing {
    NO_SHIELD      = -1,
    FRONT_SHIELDS  = 0,   // +Y axis (forward)
    REAR_SHIELDS   = 1,   // -Y axis (aft)
    TOP_SHIELDS    = 2,   // +Z axis (up)
    BOTTOM_SHIELDS = 3,   // -Z axis (down)
    LEFT_SHIELDS   = 4,   // -X axis (port)
    RIGHT_SHIELDS  = 5,   // +X axis (starboard)
    NUM_SHIELDS    = 6
};
```

Opposite pairs: FRONT(0)<->REAR(1), TOP(2)<->BOTTOM(3), LEFT(4)<->RIGHT(5).

---

## C1 — ShieldProperty +0x48 is NormalPowerWanted at runtime (NOT tickPhaseOffset)

[v5-validated 2026-05-28]

The pre-v5 doc labeled `ShieldProperty +0x48` as `tickPhaseOffset` ("Random phase for staggered event scheduling"). That label is correct only at ctor time and **wrong at runtime**.

**The ctor-time identity** — `ShieldProperty::ctor` at 0x0056b970 line `param_1[0x12] = fVar2 * _DAT_00888dbc` does initialize +0x48 to a random staggering value (`rand() * 0.33 * 3.05e-5`).

**The runtime identity** — hardpoint scripts overwrite this field at config-time with the subsystem's power requirement. Two consumers read +0x48 at runtime as a power budget:

- `PoweredSubsystem_GetNormalPowerWanted` at 0x005623d0 reads `*(float*)(property+0x48)` and returns it as the per-subsystem power requirement.
- `BoostShield` at 0x0056a420 reads `property+0x48` and divides by 6 (`* DAT_0088bacc`) to produce the per-facing power budget.

**Reframe**: the field is `NormalPowerWanted` (per-subsystem power budget). The doc's old "tickPhaseOffset" label captured the ctor-time identity and missed the runtime semantics. The struct table below uses the corrected name.

**OpenBC impact**: implementers building per-facing budgets must label this field `NormalPowerWanted` and expect hardpoint config to overwrite the ctor-time random seed. See [`docs/gameplay/power-system.md`](power-system.md) for the broader PoweredSubsystem power-budget model.

---

## C2 — 0x0056ae10 is WriteState, not ReadStream

[v5-validated 2026-05-28]

The pre-v5 function-reference table labeled `0x0056ae10` as `ShieldClass::ReadStream`. The binary disagrees.

The first instruction of `FUN_0056ae10` calls `PoweredSubsystem__WriteState(param_1, param_2)`. The loop then iterates `property+0x60..0x78` (the maxShields[6] array) calling vtable[0x54] (write float) for each. Then calls vtable[0xd8] (`EndMarker` / `GetPos`). This is unambiguously the **write** path (server → wire). The `__ftol()` call converts each float to int for compact storage.

Cross-doc check: [`docs/analysis/server-side-computation-model.md:436`](../analysis/server-side-computation-model.md) already labels this function `WriteState`. The pre-v5 shield doc carried a stale name.

**Reads** would use a different vtable slot and call `ReadFromStream`. The read path was not analyzed in this pass.

---

## Shield Object Layout

### ShieldClass (vtable at 0x00892f34, size 0x15C)

[v5-validated 2026-05-28]

Inherits from `PoweredSubsystem`. The ShieldClass is the runtime instance that tracks current shield HP per facing.

| Offset | Type | Field | Notes |
|--------|------|-------|-------|
| +0x00 | vtable* | vtable | PTR_FUN_00892f34 |
| +0x18 | ShieldProperty* | property | Pointer to ShieldProperty (max values, charge rates) |
| +0x20 | void* | shipRef | Reference to parent ship |
| +0x38 | byte | hasActiveHits | Set to 1 when any shield zone has pending damage hits |
| +0x40 | void* | shieldZoneList | Linked list of shield zone objects for intersection |
| +0x9C | byte | isEnabled | 0 = shields off (e.g., during cloak), nonzero = shields active |
| +0xA8 | float[6] | curShields | Current HP per facing (indexed by ShieldFacing enum) |
| +0xC0 | float[6] | shieldPercentage | Cached percentage per facing |
| +0xD8 | float | unknownFloat | Init 1.0 (Clar1 — purpose unknown, OQ2) |
| +0xDC | struct[7] | shieldWatchers | 0xC-byte watcher structs (one per facing + 1 overall) |
| +0x124 | void* | overallWatcher | Pointer to overall shield health watcher (points to +0xD8) |
| +0x130 | float[6] | unknownArray | Init 1.0 each (Clar1 — purpose unknown, OQ2) |
| +0x14C | byte[6] | shieldDamaged | Per-facing "damaged" flag |
| +0x154 | float | envDamageRadius | Environmental shield damage radius |
| +0x158 | float | envDamageRate | Environmental shield damage rate |

### ShieldProperty (vtable at 0x00892fc4, size 0x88)

[v5-validated 2026-05-28]

Inherits from `PoweredSubsystemProperty`. Read-only template defining max shield values and charge rates. Set by hardpoint scripts.

| Offset | Type | Field | Notes |
|--------|------|-------|-------|
| +0x00 | vtable* | vtable | PTR_FUN_00892fc4 |
| +0x14 | void* | parent | Parent subsystem property |
| +0x18 | void* | shieldClass | Back-reference to ShieldClass |
| +0x20 | float | maxHP | Maximum HP (subsystem overall health) |
| +0x28-0x2C | ushort[3] | colorIndices | Shield glow color indices (init 0xFFFF) |
| +0x30 | float | colorScale1 | Shield glow scale (init 1.0) |
| +0x34 | float | colorScale2 | Shield glow decay (init 1.0) |
| +0x38 | float | colorScale3 | (init 1.0) |
| +0x3C | float | minPowerThreshold | Minimum power for operation (init 0.001) |
| +0x40 | float | currentPower | Current power level (0.0 = unpowered) |
| +0x44-0x45 | byte[2] | flags | (init 0) |
| +0x48 | float | **NormalPowerWanted** | Per-subsystem power budget. Ctor seeds with `rand() * 0.33 * 3.05e-5` for tick stagger; hardpoint scripts overwrite at config time. Read by `PoweredSubsystem_GetNormalPowerWanted` (0x005623d0) and `BoostShield` (0x0056a420). **See C1.** |
| +0x60 | float[6] | maxShields | Maximum shield HP per facing (set by SetMaxShields) |
| +0x78 | float[6] | chargePerSecond | Shield charge rate per facing (set by SetShieldChargePerSecond) |
| +0x84 | int | (unused) | (init 0) |

Constructor default for maxShields: `0x447a0000` = 1000.0 per facing.

---

## Shield Facing Determination (FUN_0056a8d0 at 0x0056a8d0)

[v5-validated 2026-05-28]

### Algorithm: Maximum Component Projection

The shield facing is determined by finding which of the 6 cardinal directions most closely aligns with the damage impact normal vector, expressed in the ship's local coordinate system.

**Input**: A 3D normal vector in ship-local space (X, Y, Z components)

**Process**:
1. Rearrange components to `{Y, Z, X}` (forward, up, right)
2. Find the maximum positive component among the first 3 values (indices 0-2)
3. Find the maximum negated component among indices 3-5 (equivalent to most-negative of Y, Z, X)
4. The overall maximum determines the dominant direction
5. Map dominant direction to facing via switch table

**Switch mapping**:
```c
// Input reordering: [0]=Y, [1]=Z, [2]=X, [3]=-Y, [4]=-Z, [5]=-X
switch(dominant_index) {
    case 0: return 0;  // +Y (forward)  -> FRONT_SHIELDS
    case 1: return 2;  // +Z (up)       -> TOP_SHIELDS
    case 2: return 5;  // +X (right)    -> RIGHT_SHIELDS
    case 3: return 1;  // -Y (aft)      -> REAR_SHIELDS
    case 4: return 3;  // -Z (down)     -> BOTTOM_SHIELDS
    case 5: return 4;  // -X (left)     -> LEFT_SHIELDS
}
```

This is NOT a dot-product projection in the traditional sense. It is an **axis-aligned maximum component test** (equivalent to finding the dominant face of a cube that encloses the unit normal). This is computationally cheap (no trig, no dot products — just comparisons) and gives correct results for a symmetric shield ellipsoid.

### Full Ray-Ellipsoid Path (FUN_0056a690 at 0x0056a690)

[v5-validated 2026-05-28]

When a weapon fires at a ship, the ray-to-facing calculation is:

1. Transform ray endpoints from world space to the shield ellipsoid's local space
2. Normalize by the ellipsoid semi-axes (making it a unit sphere)
3. Perform ray-sphere intersection test (FUN_004570d0) against the unit sphere
4. Compute the outward normal at the intersection point
5. Un-normalize back to ship-local space
6. Pass the normal to FUN_0056a8d0 to determine the facing

The ellipsoid semi-axes are stored in the ship's NiNode at offsets `+0x24C`, `+0x250`, `+0x254` (accessed as `piVar1[0x93]`, `piVar1[0x94]`, `piVar1[0x95]`).

---

## Shield Absorption

### Two Damage Paths

Bridge Commander has two distinct shield absorption paths:

#### Path 1: Area-Effect Damage (FUN_00593c10 at 0x00593c10)

[v5-validated 2026-05-28]

Used for environmental/explosion damage. Distributes damage equally across all 6 facings.

```
For each target in range:
    totalAbsorbed = 0
    damagePerFacing = totalDamage * (1/6)   // DAT_0088bacc = 0.16667

    For each facing (0..5):
        absorption = min(damagePerFacing, curShields[facing])
        curShields[facing] -= absorption
        totalAbsorbed += absorption

    overflowDamage = totalDamage - totalAbsorbed
    if overflowDamage > 0:
        apply to hull (visual effect + damage)
```

**Per-facing 1/6 split** [v5-validated 2026-05-28]: `_DAT_0088bacc` = `1/6` = `0.16667` (at 0x0088bacc, hex `0x3E2AAAAB`, bytes `abaa2a3e`).

This is NOT all-or-nothing. Each facing independently absorbs up to its current HP for that facing's share. If any facing is depleted, its share of damage passes through. A ship with 5 full facings and 1 empty facing would still lose 1/6 of incoming area damage to hull.

#### Path 2: Directed Damage (ProcessDamage at 0x00593E50)

[v5-validated 2026-05-28]

Used for weapon hits and collisions. Damage is directed at a specific location, hitting specific shield geometry.

1. **ProcessDamage** iterates the handler array at `ship+0x128`, count at `ship+0x130` (Clar6).
2. Per handler, **FUN_004b1ff0** checks:
   - Shield path: `handler+0x20` -> shield zone object, gated on `zone+0x18 != 0` (shield active)
   - Hull path: `handler+0x1C` -> AABB overlap test, gated on the **OR** of `(handler+0x1C+0x8 != 0)` and `(handler+0x1C+0x9 != 0)` (Clar3 — pre-v5 doc cited only +0x9)
3. Shield zone intersection (FUN_004b4b40) finds which shield geometry nodes are hit:
   - Transforms the DamageVolume into the shield ellipsoid's local space
   - Tests intersection using FUN_00464770 (sphere-geometry test)
   - For each hit, looks up the shield facing via FUN_004b8e80 (zone list at `shield+0x40`)
   - Adds the DamageVolume to the facing's hit list
   - Sets dirty flag (`facing[7] |= 1`)
4. Hull overlap test (FUN_004bd9f0) checks AABB intersection for subsystem damage
5. After all handlers, **FUN_00593ee0** applies remaining damage to hull, then **FUN_00593f30** runs the notification gate (Clar6 — notification gate lives inside FUN_00593f30; see [`docs/gameplay/damage-system.md`](damage-system.md))

The shield facing's hit list is processed through the event system, with actual HP decrement happening via FUN_0056a5c0 (`SetCurShields`). The weapon hit handler at FUN_005af010 checks `weaponHitInfo+0x58` to determine if the hit passed through shields:
- `+0x58 == 0`: Shield absorbed the hit (shield visual effect, no hull damage)
- `+0x58 != 0`: Shields breached (hull hit effect + DoDamage to hull)

### Shield Absorption is Per-Facing, Not All-or-Nothing

Shields absorb damage up to the current HP of the specific facing that was hit. If the shield facing's HP is depleted mid-hit, the overflow damage passes through to hull. This is clamp-based absorption:

```c
// FUN_0056a5c0 (SetCurShields)
void SetCurShields(ShieldClass* this, int facing, float newHP) {
    float maxHP = this->property->maxShields[facing];  // property+0x60+facing*4
    if (maxHP < newHP) newHP = maxHP;  // cap at max
    if (newHP < 0.0) newHP = 0.0;     // floor at zero (DAT_00888b54)
    this->curShields[facing] = newHP;  // store at this+0xA8+facing*4
}
```

---

## Shield Recharge (BoostShield at 0x0056a420)

[v5-validated 2026-05-28]

### Recharge Formula (Power-Budget Loop)

```c
float10 BoostShield(ShieldClass* this, int facing, float powerAmount) {
    float normalizedPower = this->property->NormalPowerWanted * (1.0/6.0);
    // property+0x48 * DAT_0088bacc (= 1/6)
    // NormalPowerWanted divided across 6 facings

    if (normalizedPower <= 0.0) return powerAmount;  // no power budget, no recharge

    float chargeRate = this->property->chargePerSecond[facing];
    // property+0x78+facing*4

    float hpGain = (chargeRate * powerAmount) / normalizedPower;
    float newHP = this->curShields[facing] + hpGain;
    this->curShields[facing] = newHP;

    if (newHP > this->property->maxShields[facing]) {
        // Shield full -- calculate and return excess
        float ratio = chargeRate / normalizedPower;
        if (ratio <= 0.0) ratio = 0.0;
        float excess = (newHP - maxShields[facing]) / ratio;
        this->curShields[facing] = maxShields[facing];  // cap at max
        return excess;  // return unused power for redistribution
    }
    return 0.0;  // all power consumed
}
```

**Key details**:
- `powerAmount` is NOT frame time — it is a "power budget" in energy units
- The power budget comes from the PoweredSubsystem's per-tick energy allocation
- `chargeRate` (`chargePerSecond[facing]`) is the conversion factor from power to shield HP
- The `1/6` factor distributes the subsystem's total power equally across 6 facings
- The divisor `NormalPowerWanted` (property+0x48) is the per-subsystem power requirement — see C1
- **Overflow power is returned** to the caller for redistribution to other facings

### Recharge Scheduling (Event System)

[v5-validated 2026-05-28]

Shield recharge runs through the event system, NOT through a direct per-tick call:

1. **ShieldProperty constructor** (FUN_0056b970) seeds `NormalPowerWanted` at `+0x48` with a random tick-staggering value at ctor time:
   ```c
   // Ctor-time only — hardpoint scripts overwrite at config time (see C1)
   this->NormalPowerWanted = rand() * _DAT_00892fc0 * _DAT_00888dbc;
                          //         0.33                ~3.052e-5  (Clar2)
   ```
   The doc previously presented `0.33 * 3.05e-5` as a single multiplier; the binary uses **two separate .rdata constants** (Clar2).

2. **FUN_0056bde0** `ScheduleShieldEvents` (called when power level changes) registers **5 timers with TWO different time bases** (Clar5):
   - Events `0x0080006d`, `0x0080006e`: interval from `FUN_0056b960(property+0x40)` — the subsystem's current power level
   - Events `0x0080006f`, `0x00800070`, `0x00800071`: interval is the constant `0x358637bd` (~1e-6, effectively next-tick)
   - Uses `FUN_0044c2d0` to create periodic timer events

3. **HandleSetShieldState** (registered at LAB_0056aae0, debug string `"ShieldClass::HandleSetShieldState"`) — Clar4:
   - This is the event handler called when shield tick events fire
   - Address range 0x0056a230..0x0056aad0 — real reachable code that Ghidra has NOT promoted to a function in its database
   - Confirmed reachable: xrefs from this region call `BoostShield` (FUN_0056a420) at 0x0056a2e6 and 0x0056a392
   - Handles redistribution of overflow power between facings
   - **OQ4**: needs Ghidra promotion for full analysis

4. **Registration** (FUN_0056a1f0 at 0x0056a1f0):
   ```c
   FUN_006da130(&LAB_0056aae0, "ShieldClass::HandleSetShieldState");
   ```
   Called from the ship event handler registration function (FUN_005ab6a0).

---

## C3 — Per-ship recharge values (binary truth from hardpoint scripts)

[v5-validated 2026-05-28]

The pre-v5 doc carried a "Typical Recharge Values" table whose values were fabricated for **4 of 5 ships**. Only Warbird matched. The corrected table below pulls verified values from `reference/scripts/ships/Hardpoints/`:

| Ship | Front/Top/Bottom MaxShield | L/R/Rear MaxShield | ChargePerSecond | Prior doc claim |
|---|---|---|---|---|
| Sovereign | 11000 | 5500 | 12 (all facings) | "6000 / 15" — WRONG |
| Galaxy | 8000 | 4000 | 11 (all facings) | "5600 / 12" — WRONG |
| Akira | 10000 | 5000 | 11 (all facings) | "3600 / 11" — WRONG |
| Warbird | 4000 | 4000 | 8 | "4000 / 8" — OK (only correct row) |
| Vor'cha | 24000 Front | 6000/3500/3000/4500 | 28 Front / 9/2/2/2/2 others | "2-9" handwaved — WRONG |

**Recharge values are per-ship hardpoint properties, not engine constants.** Source: `reference/scripts/ships/Hardpoints/<ship>.py`. The doc's old table presented these as if they were canonical engine defaults; they're configurable per-hardpoint.

---

## C4 — IsShieldBreached threshold is 1.0, not 0

[v5-validated 2026-05-28]

The pre-v5 doc's gate-conditions summary implied the breach threshold was `curShields[facing] == 0`. The binary (FUN_0056a620) says otherwise:

```c
// IsShieldBreached at 0x0056a620
bool IsShieldBreached(ShieldClass* this, int facing) {
    if (this->curShields[facing] >= 1.0f && this->shieldDamaged[facing] == 0) {
        return false;  // NOT breached
    }
    return true;  // breached
}
```

A facing with `curShields[facing] = 0.5` is treated as **breached**. The effective wire-condition for replication is `curShields < 1.0 OR shieldDamaged != 0`.

Practical effect is identical for normal gameplay (a facing only ends up in the 0.0..1.0 fractional range right at the moment of depletion), but the precise threshold matters for OpenBC replication parity.

---

## Cloak / Shield Interaction

[v5-validated 2026-05-28]

### Shield Disable During Cloak (FUN_0055f110 at 0x0055f110)

When the cloaking subsystem activates:

1. **StartCloaking** (FUN_0055f360) sets `cloakObj+0xAD = 1` (trying to cloak)
2. The cloak handler (FUN_0055f110) schedules a **delayed** shield disable:
   - Creates an event sequence with event `0x00800077` (shield off event)
   - The delay is `DAT_008e4e20` = **1.0 second** (the CloakingSubsystem ShieldDelay value)
   - Sets cloak state to `+0xB0 = 2` (cloaking in progress)
3. After the delay, event `0x00800077` fires, setting `shieldClass+0x9C = 0` (shields disabled)

### Shield Re-enable During Decloak

When the cloaking subsystem deactivates:

1. The handler is called with `param_1 != 1` (decloaking)
2. Posts event `0x00800079` (shield on event) immediately
3. Sets cloak state to `+0xB0 = 5` (decloaking in progress)
4. Shields re-enable: `shieldClass+0x9C` is set back to nonzero

### Shield Recharge While Cloaked

Shield recharge effectively **STOPS** while cloaked because:

1. The `+0x9C` (isEnabled) flag is set to 0
2. Shield absorption checks test `+0x9C != 0` before absorbing damage
3. The BoostShield function at FUN_0056a420 depends on `property+0x48` (`NormalPowerWanted`) — see C1
4. The `FUN_0056c350` (subsystem fully destroyed check) is used as a guard in the shield code

The CloakingSubsystem ShieldDelay (default 1.0 second) controls how long after engaging cloak before shields drop. This creates the classic Trek mechanic: there's a brief window where a ship is cloaking but still has shields.

**Note**: `CloakingSubsystem.SetShieldDelay(n)` modifies the global at `DAT_008e4e20` (0x008e4e20), affecting ALL cloaking subsystems. The default and initial value is `1.0f`.

---

## Gate Conditions Summary

| Condition | Where Checked | Effect |
|-----------|--------------|--------|
| `shieldClass == NULL` | FUN_00593c10 | No shield subsystem -> all damage to hull |
| `shieldClass+0x9C == 0` | FUN_00593c10, FUN_0056a620 | Shields disabled (cloak) -> all damage to hull |
| `FUN_0056c350() == true` | FUN_00593c10, FUN_00485360 | Shield subsystem destroyed -> shields down |
| `handler+0x20+0x18 == 0` | FUN_004b1ff0 | Per-handler shield zone inactive -> skip shield test |
| `(handler+0x1C+0x8 != 0) OR (handler+0x1C+0x9 != 0)` | FUN_004b1ff0 | Hull path gate (Clar3 — OR of two bytes) |
| `curShields[facing] < 1.0 OR shieldDamaged[facing] != 0` | FUN_0056a620 (IsShieldBreached) | Individual facing breached (C4 — threshold is 1.0, not 0) |
| `property+0x48 (NormalPowerWanted) <= 0` | FUN_0056a420 (BoostShield) | No power budget -> no recharge (C1) |

---

## Verified Constants

[v5-validated 2026-05-28]

| Address | Hex | Float | Meaning |
|---------|-----|-------|---------|
| 0x0088bacc | 0x3E2AAAAB | 1/6 (0.16667) | Per-facing share (6 facings) — used in AreaEffectDamage AND BoostShield |
| 0x00888b54 | 0x00000000 | 0.0 | Zero constant (SetCurShields floor) |
| 0x00888860 | 0x3F800000 | 1.0 | One constant (also IsShieldBreached threshold — C4) |
| 0x008887a8 | 0x3F000000 | 0.5 | Half constant (weapon damage radius scale) |
| 0x008e4e20 | 0x3F800000 | 1.0 | CloakingSubsystem ShieldDelay (seconds) — GLOBAL |
| 0x008e4e1c | 0x40A00000 | 5.0 | Cloak rate |
| 0x00892fc0 | 0x3EA8F5C3 | 0.33 | Random phase scale for shield tick stagger (Clar2 — first of two) |
| 0x00888dbc | 0x38000100 | ~3.052e-5 | Random phase fine-scale (Clar2 — second of two; combined product ≈ 1.007e-5) |
| 0x00888b58 | 0x358637BD | ~1e-6 | Epsilon AND next-tick interval for ScheduleShieldEvents events 0x6f/0x70/0x71 (Clar5 — dual-use) |

---

## Key Function Reference

[v5-validated 2026-05-28]

| Address | Name | Purpose |
|---------|------|---------|
| 0x0056a000 | `ShieldClass::ctor` | Constructor — 6 facings at 1000 HP, plus float[6]@+0x130 and float@+0xD8 each init 1.0 (Clar1) |
| 0x0056a190 | `ShieldClass::dtor` | Destructor |
| 0x0056a1f0 | `RegisterShieldEvents` | Registers HandleSetShieldState handler |
| 0x0056a420 | `BoostShield` | Per-facing power-to-HP conversion, returns overflow |
| 0x0056a540 | `GetShieldPercentage` | Returns min(curHP/maxHP) across all 6 facings |
| 0x0056a5c0 | `SetCurShields` | Sets curShields[facing], clamped to [0, max] |
| 0x0056a620 | `IsShieldBreached` | Returns NOT_BREACHED iff `curShields[facing] >= 1.0 AND shieldDamaged[facing] == 0` (C4) |
| 0x0056a670 | `IsAnyShieldBreached` | Checks all 6 facings for breach |
| 0x0056a690 | `GetShieldFacingFromRay` | Ray-ellipsoid intersection, returns facing index |
| 0x0056a8d0 | `NormalToFacing` | Converts ship-local normal to ShieldFacing enum (max-component test) |
| 0x0056a9c0 | `RedistributeShields` | (unanalyzed) Redistributes HP between facings |
| LAB_0056aae0 | `HandleSetShieldState` | Event handler: shield recharge tick (calls BoostShield) — code-gap, Clar4 |
| 0x0056acc0 | `AreAllWatchersTriggered` | Checks if all shield watcher thresholds exceeded |
| 0x0056ae10 | **`ShieldClass::WriteState`** | Network serialization — writes 6 maxShield values via vtable[0x54] (C2 — pre-v5 misnamed `ReadStream`) |
| 0x0056b960 | `GetCurrentPower` | Returns property+0x40 |
| 0x0056b970 | `ShieldProperty::ctor` | Constructor with vtable 0x00892fc4; seeds +0x48 with random tick offset (overwritten at config time — C1) |
| 0x0056bc50 | `SetPower` | Sets power level, triggers event scheduling |
| 0x0056bde0 | `ScheduleShieldEvents` | Creates periodic timer events (0x6d-0x71) — TWO time bases (Clar5) |
| 0x0056c310 | `GetMaxHP` | Returns property+0x20 |
| 0x0056c350 | `IsSubsystemDestroyed` | Recursive check if subsystem is non-functional |
| 0x0056c470 | `SetCurrentHP` | Sets current HP, updates ratio, fires events |
| 0x005623d0 | `PoweredSubsystem_GetNormalPowerWanted` | Reads property+0x48 — establishes NormalPowerWanted semantics (C1) |
| 0x004b1ff0 | `DamageHandler_Process` | Per-handler: shield intersection + hull AABB test (Clar3 — hull gate is OR of two bytes) |
| 0x004b4b40 | `ShieldZone_Intersect` | Shield zone geometry intersection test |
| 0x004b8e80 | `ShieldZone_LookupFacing` | Looks up facing from shield zone's node list |
| 0x004bd9f0 | `HullAABB_Overlap` | AABB overlap test for hull/subsystem damage |
| 0x00593c10 | `AreaEffectDamage` | Environmental/explosion with explicit per-facing absorption |
| 0x00593e50 | `ProcessDamage` | Iterates handler array (ship+0x128/+0x130); notification gate is inside FUN_00593f30 (Clar6) |
| 0x005af010 | `WeaponHitHandler` | Checks shield absorption flag, calls effects + DoDamage |
| 0x0055f110 | `CloakShieldHandler` | Enables/disables shields during cloak state changes |

---

## Dedicated Server Implications

1. **Shield HP is authoritative on the server**: `curShields[6]` at `shieldClass+0xA8` is the ground truth
2. **Shield recharge requires the event system**: The `HandleSetShieldState` event handler must fire for recharge to work. If the PoweredSubsystem doesn't get power, shields won't recharge.
3. **Area-effect damage bypass**: FUN_00593c10 directly calls `SetCurShields`, so shields are always correctly decremented for AOE damage regardless of event system state
4. **Cloaking shield delay is a GLOBAL**: Modifying ShieldDelay via SWIG changes the value for ALL ships (`DAT_008e4e20` at 0x008e4e20)
5. **StateUpdate serialization**: Shield facing HP is serialized via the subsystem linked list at `ship+0x284` (separate from the damage handler array at `ship+0x128`). See [`docs/protocol/stateupdate-subsystem-wire-format.md`](../protocol/stateupdate-subsystem-wire-format.md) for the wire format and [`docs/protocol/subsystem-integrity-hash.md`](../protocol/subsystem-integrity-hash.md) for the additional 12 floats hashed at `property+0x60`/`+0x78`.
6. **NormalPowerWanted is hardpoint-configurable** (C1): OpenBC implementers must label ShieldProperty+0x48 as the per-subsystem power budget, expect hardpoint scripts to overwrite the ctor-time random seed, and divide by 6 inside the BoostShield loop to produce the per-facing budget.

---

## Open Questions

- **OQ1**: Identity of the SWIG setter for `ShieldProperty+0x48` (`NormalPowerWanted`) — likely `SetNormalPowerPerSecond` or `SetNormalPowerWanted`, not investigated this pass. Hardpoint scripts must call this somewhere.
- **OQ2**: Purpose of `ShieldClass+0x130` (third float[6] array) and `ShieldClass+0xD8` (single float) — both initialized to 1.0 by ctor. The `overallWatcher` pointer at `+0x124` points to `+0xD8`, but the runtime use of the value is unknown.
- **OQ3** (carried from validation memo): `HandleSetShieldState` (code-gap at 0x0056a230..0x0056aad0) should be promoted to a function in the Ghidra DB for proper analysis of the overflow-redistribution logic. Currently reachable only via LAB_0056aae0 with xrefs into BoostShield at 0x0056a2e6 and 0x0056a392.
