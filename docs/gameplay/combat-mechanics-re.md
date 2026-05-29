---
title: Combat Mechanics — Consolidated Reverse Engineering
type: reference
audience: RE engineers, OpenBC implementers
validated: 2026-05-28
methodology: FUNCTION_DOC_WORKFLOW_V5
binary_fingerprint: stbc.exe (base 0x400000, 32-bit Windows)
status: verified
supersedes: []
evidence:
  - claim: "Damage pipeline entry: CollisionDamageWrapper → DoDamage_FromPosition (single-point collision path)"
    address: 0x005B0060
    confidence: high
    note: "chains to 0x00593650"
  - claim: "Damage pipeline entry: DoDamage_FromPosition (collision single-point)"
    address: 0x00593650
    confidence: high
  - claim: "Damage pipeline entry: DoDamage_CollisionContacts (multi-contact collision path)"
    address: 0x005952D0
    confidence: high
  - claim: "Damage pipeline entry: WeaponHitHandler"
    address: 0x005AF010
    confidence: high
    note: "chains to ApplyWeaponDamage at 0x005AF420"
  - claim: "Damage pipeline entry: ApplyWeaponDamage doubles damage (p1+0x4c+p1+0x4c), halves radius (p1+0x54*0.5f), gates weapon type to 0 (phaser) or 1 (torpedo)"
    address: 0x005AF420
    confidence: high
  - claim: "DoDamage convergence point — 3 xrefs total: FUN_005952d0, FUN_005af420, FUN_00593650"
    address: 0x00594020
    confidence: high
    note: "xref count is load-bearing: zero tractor mode handlers call this, confirming tractor-no-damage claim"
  - claim: "ProcessDamage — DoDamage's downstream + direct call from Explosion handler"
    address: 0x00593E50
    confidence: high
  - claim: "Explosion handler (opcode 0x29): wire format [0x29][object_id:i32][impact:cv4][damage:cf16][radius:cf16]; bypasses DoDamage and calls ProcessDamage directly"
    address: 0x006A0080
    confidence: high
    note: "byte-confirmed via CompressedVector4_ReadVirtual + 2x CompressedFloat16_Decode in handler decompile"
  - claim: "DestroyObject handler (opcode 0x14)"
    address: 0x006A01E0
    confidence: high
  - claim: "Damage notification CLIENT-ONLY gate: DAT_0097fa89 == '\\0' (IsHost==0)"
    address: 0x00593F30
    confidence: high
  - claim: "Subsystem handler dispatch: shield path via handler+0x20+0x18 (calls FUN_004b4b40 shield geometry), hull path via handler+0x1c flags +0x08/+0x09 (calls FUN_004bd9f0 AABB overlap)"
    address: 0x004B1FF0
    confidence: high
  - claim: "FUN_004bd9f0 subsystem damage = 6-axis AABB overlap test (NOT Euclidean distance, NOT 50% overflow): (p1+0x14<=p2[0xb] && p2[8]<=p1+0x20) for X, equivalents for Y/Z"
    address: 0x004BD9F0
    confidence: high
    note: "six conditions all-AND; no distance computation anywhere in body"
  - claim: "Shield facing determination: maximum component projection (rearrange {X,Y,Z}->{Y,Z,X}, find max positive in {+Y,+Z,+X}, find max negated in {-Y,-Z,-X}, dominant axis -> facing via switch); NOT dot products"
    address: 0x0056A8D0
    confidence: high
  - claim: "Ray-to-facing full path: transform to shield ellipsoid local space, normalize by semi-axes (NiNode+0x24C/0x250/0x254), call ray-unit-sphere intersect, NormalToFacing"
    address: 0x0056A690
    confidence: high
  - claim: "Shield recharge (BoostShield): hpGain = (chargePerSec[facing] * powerBudget) / (currentPower/6); event-driven (events 0x0080006d-0x00800071), NOT per-tick"
    address: 0x0056A420
    confidence: high
  - claim: "Cloak tick FUN_0055e500: CLOAKING increments timer by dt, DECLOAKING decrements by dt; progress = timer / CloakTime; thresholds 1.0 -> state 3, 0.0 -> state 0"
    address: 0x0055E500
    confidence: high
  - claim: "IsCloaked: reads ship+0x2DC (cloak subsystem), returns +0xAC == 1 (state==3 only, not during transitions)"
    address: 0x005AC450
    confidence: high
  - claim: "Phaser charge formula (recharge): charge += recharge_rate * power_level * dt * power_multiplier; non-owner ships multiplied by DAT_00890550 (AI/remote penalty)"
    address: 0x00572B80
    confidence: high
  - claim: "SetAmmoType (torpedo type switch): when immediate=1 (MP path), unload loop runs but reload loop SKIPPED -> implicit lockout = ReloadDelay; when immediate=0 (local), reload runs immediately"
    address: 0x0057B230
    confidence: high
  - claim: "ReloadTorpedo: increments +0xA0 num_ready, finds slot with LARGEST timer in +0xAC array, sets to -1.0f (0xBF800000)"
    address: 0x0057D8A0
    confidence: high
  - claim: "Torpedo Fire FUN_0057C9E0: calls CanFire, creates projectile, decrements num_ready, marks timer slot 0.0f, sends opcode 0x19 if host"
    address: 0x0057C9E0
    confidence: high
  - claim: "Repair rate formula FUN_005652a0: rawRepair = MaxRepairPoints * conditionPct * dt; divisor = min(queueCount, NumRepairTeams); perSub = raw/divisor; gain = perSub/RepairComplexity"
    address: 0x005652A0
    confidence: high
  - claim: "Tractor force formula FUN_00580f50: distanceRatio = min(1.0, maxDamageDistance/beamDistance); force = maxDamage * (systemCondPct * projectorCondPct) * distanceRatio; optional target condition multiply if (p1+0x24+0xf0)!=0; * dt"
    address: 0x00580F50
    confidence: high
  - claim: "TractorBeamSystem ratio FUN_005822d0: if (p1+0xF8) <= 0.0 return 0.0; else return (p1+0xFC) / (p1+0xF8) = forceUsed/totalMaxDamage"
    address: 0x005822D0
    confidence: high
  - claim: "ImpulseEngine drag FUN_00561230: if (p1+0xA8 != 0) tractor system attached, local_c *= (1.0 - ratio); returns (p1+0x90) * local_c; multiplicative drag confirmed"
    address: 0x00561230
    confidence: high
  - claim: "TractorBeamSystem vtable: slot 0 = 0x00582170 dtor, slot 1 = 0x005820c0"
    address: 0x00893794
    confidence: high
  - claim: "TractorBeamProjector vtable: slot 0 = 0x0057ed80 dtor, slot 1 = 0x0057ecd0"
    address: 0x008936F0
    confidence: high
  - claim: "Tractor beam applies no direct damage: DoDamage (0x00594020) xref-set is {FUN_005952d0, FUN_005af420, FUN_00593650} — zero tractor mode handler entries"
    address: null
    confidence: high
    note: "negative claim via complete xref enumeration of DoDamage"
  - claim: "Weapon radius scale constant DAT_008887a8 = 0.5f"
    address: 0x008887A8
    confidence: high
  - claim: "Collision damage cap constant: 0.5f hard cap per contact"
    address: null
    confidence: high
    note: "embedded in DoDamage_CollisionContacts at 0x005952D0"
  - claim: "Collision damage radius constant: 6000.0f (0x45BB8000) fixed"
    address: null
    confidence: high
    note: "embedded immediate in DoDamage_CollisionContacts"
  - claim: "Area-damage 1/6 split constant DAT_0088bacc = 0.16667f (1/6 per facing)"
    address: 0x0088BACC
    confidence: high
  - claim: "CloakTime class-level global = 5.0f (transition duration)"
    address: 0x008E4E1C
    confidence: high
  - claim: "ShieldDelay class-level global = 1.0f (post-cloak shield visual hide delay)"
    address: 0x008E4E20
    confidence: high
  - claim: "Drag baseline DAT_00888860 = 1.0f (FUN_00561230 reference)"
    address: 0x00888860
    confidence: high
  - claim: "Tractor distance-threshold DAT_0088b9c0 = 0.0f (FUN_00580f50 reference)"
    address: 0x0088B9C0
    confidence: high
  - claim: "Sovereign hardpoint values 100% match: Hull 12000, ShieldGenerator 10000 (RepairComplexity 2.0), shields {11000/5500/11000/11000/5500/5500}, Sensors 8000, WarpCore 7000, Impulse 3000, Torpedoes 6000, Forward torpedoes (x4) 2200 each, Aft torpedoes (x2) 2200 each, Phasers (x8) per-tube 1000/MaxCharge 5.0/MaxDamage 300.0/MaxDamageDistance 70.0/MinFiringCharge 3.0/RechargeRate 0.08, Repair 8000/MaxRepairPoints 50/NumRepairTeams 3, Tractor 3000 (per-projector 1500, MaxCharge 5.0, MaxDamage 80, MaxDamageDistance 114, MinFiringCharge 3.0, Forward RechargeRate 0.5 / Aft 0.3), WarpEngines 8000, Bridge 10000"
    address: null
    confidence: high
    note: "reference/scripts/ships/Hardpoints/sovereign.py lines 515, 534, 542-547, 874-885, 1020-1023, 1025, 1262"
companions:
  - docs/gameplay/damage-system.md
  - docs/gameplay/shield-system.md
  - docs/gameplay/weapon-firing-mechanics.md
  - docs/gameplay/power-system.md
  - docs/gameplay/cloaking-state-machine.md
  - docs/gameplay/repair-tractor-analysis.md
  - docs/protocol/collision-effect-protocol.md
  - docs/protocol/cf16-explosion-encoding.md
---

> [docs](../README.md) / [gameplay](README.md) / combat-mechanics-re.md

# Combat Mechanics — Consolidated Reverse Engineering

> [!NOTE]
> **v5 verified pass — ZERO material corrections.** Cleanest gameplay-family doc validated to date. 6 of 8 sections inherit from already-validated foundation docs; sections 6 (Tractor Beam) and 7 (Ship Death) freshly binary-anchored this pass. 23 unique addresses verified, 7 constants byte-confirmed, 100% Sovereign hardpoint match against `reference/scripts/ships/Hardpoints/sovereign.py`.
>
> - **Clar-1** (Section 8 table): Shield Generator `RepairComplexity` is `2.0`, not "—" (sovereign.py:534). Cosmetic table omission corrected.
> - **Clar-2** (Section 3 globals table): `CloakTime` (DAT_008E4E1C) has a concrete value — `5.0f` (5.0 seconds) — symmetrizing the row with `ShieldDelay` (1.0s).
> - Negative claim re-confirmed via xref enumeration: tractor beam applies no direct damage. DoDamage (0x00594020) has exactly 3 xrefs, none of which are tractor mode handlers.

Comprehensive RE analysis of Bridge Commander's combat systems. All findings verified against the stbc.exe binary via Ghidra decompilation, raw disassembly (objdump), and cross-referenced against shipped hardpoint scripts and live packet traces.

This document consolidates findings from:
- [damage-system.md](damage-system.md) — Damage pipeline, DoDamage/ProcessDamage
- [shield-system.md](shield-system.md) — Shield facing, absorption, recharge
- [cloaking-state-machine.md](cloaking-state-machine.md) — Cloak state machine, shield/weapon interactions
- [weapon-firing-mechanics.md](weapon-firing-mechanics.md) — Phaser charge, torpedo reload, fire gates
- [repair-tractor-analysis.md](repair-tractor-analysis.md) — Repair queue, tractor beam drag

---

## 1. Damage Pipeline [v5-validated 2026-05-28 — cross-anchor: damage-system.md]

### Entry Points

| Path | Entry Function | Address |
|------|---------------|---------|
| Collision (single-point) | CollisionDamageWrapper → DoDamage_FromPosition | 0x005B0060 → 0x00593650 |
| Collision (multi-contact) | DoDamage_CollisionContacts | 0x005952D0 |
| Weapon hit | WeaponHitHandler → ApplyWeaponDamage | 0x005AF010 → 0x005AF420 |
| Explosion (opcode 0x29) | Explosion_Net → ProcessDamage (direct) | 0x006A0080 |

All paths converge at **DoDamage** (`0x00594020`) → **ProcessDamage** (`0x00593E50`), except Explosion which bypasses DoDamage and calls ProcessDamage directly. DoDamage's complete xref set is `{FUN_005952d0, FUN_005af420, FUN_00593650}` (three xrefs total) — load-bearing for the negative claim in Section 6 that no tractor handler applies damage.

### Gate Conditions (DoDamage)

| Gate | Offset | Condition | Effect if NULL |
|------|--------|-----------|----------------|
| Scene graph | ship+0x18 | NiNode* must be non-NULL | ALL damage silently dropped |
| Damage target | ship+0x140 | Reference must be non-NULL | ALL damage silently dropped |

### Collision Damage Formula (DoDamage_CollisionContacts at 0x005952D0)

```
raw = (collision.energy / ship.mass) / contact_count
scaled = raw * DAT_00893f28 + DAT_0088bf28
damage = min(scaled, 0.5)    // hard cap at 0.5 per contact
radius = 6000.0              // fixed (0x45BB8000)
```

### Weapon Damage Scaling (ApplyWeaponDamage at 0x005AF420)

- Damage is **doubled**: `hit.damage * 2.0` (computed as `*(p1+0x4c) + *(p1+0x4c)`)
- Radius is **halved**: `hit.radius * 0.5` (via `DAT_008887a8 = 0.5f` at `0x008887A8`)
- Weapon-type gate: only `type == 0` (phaser) or `type == 1` (torpedo) processed (check at `*(p1+0x2c)`)

### Resistance Scaling (ProcessDamage)

| Offset | Type | Effect |
|--------|------|--------|
| ship+0x1B8 | float | Damage radius multiplier (1.0 = normal, 0.0 = immune) |
| ship+0x1BC | float | Damage falloff multiplier (1.0 = normal) |

### Subsystem Damage Distribution

ProcessDamage iterates the **handler array** at ship+0x128 (count at ship+0x130). This is a SEPARATE structure from the subsystem linked list at ship+0x284.

Per handler (`FUN_004b1ff0` at `0x004B1FF0`):
- **Shield path**: handler+0x20 → zone+0x18 flag → `FUN_004b4b40` (shield geometry intersection)
- **Hull path**: handler+0x1C → flags +0x08/+0x09 → `FUN_004bd9f0` at `0x004BD9F0` (**AABB overlap test**, NOT distance-based)

**Important**: Subsystem damage uses AABB (axis-aligned bounding box) overlap testing — six all-AND conditions:
```
(ship+0x14 <= hitbox[0xb]) && (hitbox[8]  <= ship+0x20)   // X axis
(ship+0x18 <= hitbox[0xc]) && (hitbox[9]  <= ship+0x24)   // Y axis
(ship+0x1c <= hitbox[0xd]) && (hitbox[10] <= ship+0x28)   // Z axis
```
NOT Euclidean distance to the nearest subsystem. There is no "50% overflow" mechanic. No distance computation appears anywhere in `FUN_004bd9f0`'s body.

### Damage Notification

`FUN_00593F30` at `0x00593F30` — **CLIENT ONLY** (gated on `DAT_0097fa89 == '\0'`, i.e., IsHost==0). Server applies damage silently; clients get visual/audio feedback.

---

## 2. Shield System [v5-validated 2026-05-28 — cross-anchor: shield-system.md]

### 6 Shield Facings

| Index | Facing | Ship-Local Axis |
|-------|--------|-----------------|
| 0 | FRONT | +Y (forward) |
| 1 | REAR | -Y (aft) |
| 2 | TOP | +Z (up) |
| 3 | BOTTOM | -Z (down) |
| 4 | LEFT | -X (port) |
| 5 | RIGHT | +X (starboard) |

### Facing Determination (FUN_0056a8d0 at 0x0056A8D0)

**Algorithm**: Maximum component projection (NOT dot products).

1. Rearrange impact normal {X,Y,Z} to {Y,Z,X}
2. Find maximum positive value among {+Y,+Z,+X} (indices 0-2)
3. Find maximum negated value among {-Y,-Z,-X} (indices 3-5)
4. Dominant axis → facing via switch table

This is an axis-aligned maximum component test (equivalent to finding dominant face of a cube enclosing the unit normal). Computationally cheap — no trig, no dot products, just comparisons.

Full ray-to-facing path (`FUN_0056a690` at `0x0056A690`) uses ray-ellipsoid intersection:
1. Transform ray to shield ellipsoid's local space
2. Normalize by semi-axes (NiNode+0x24C/0x250/0x254)
3. Ray-unit-sphere intersection (`FUN_004570d0`)
4. Compute outward normal at hit point
5. Pass normal to NormalToFacing

### Shield Data Layout

- **Current HP per facing**: shieldClass+0xA8 (float[6])
- **Max HP per facing**: shieldProperty+0x60 (float[6])
- **Charge per second per facing**: shieldProperty+0x78 (float[6])
- **Shield enabled flag**: shieldClass+0x9C (byte, 0=disabled during cloak)

### Shield Absorption

**Two distinct paths**:

#### Area-Effect Damage (FUN_00593c10)
Distributes damage equally across all 6 facings:
```
damagePerFacing = totalDamage * (1/6)    // DAT_0088bacc = 0.16667 at 0x0088BACC

For each facing (0..5):
    absorption = min(damagePerFacing, curShields[facing])
    curShields[facing] -= absorption
    totalAbsorbed += absorption

overflowToHull = totalDamage - totalAbsorbed
```

NOT all-or-nothing. Each facing independently absorbs its share. A ship with 5 full facings and 1 depleted absorbs 5/6 of damage; 1/6 goes to hull.

#### Directed Damage (via ProcessDamage)
Uses geometry intersection against shield ellipsoid mesh. The weapon hit handler checks `weaponHitInfo+0x58`:
- `== 0`: Shield absorbed the hit (visual effect, no hull damage)
- `!= 0`: Shield breached (hull hit + DoDamage applied)

### Shield Recharge (FUN_0056a420 — BoostShield at 0x0056A420)

```c
float normalizedPower = property->currentPower * (1.0/6.0);
float hpGain = (chargePerSecond[facing] * powerBudget) / normalizedPower;
curShields[facing] += hpGain;
// Overflow returned for redistribution to other facings
```

**Key**: `powerBudget` is NOT frame time — it is an energy budget from the PoweredSubsystem allocation. Recharge runs through the event system (events `0x0080006d-0x00800071`), NOT a direct per-tick call.

### Sovereign Shield HP (from sovereign.py hardpoint script)

| Facing | Max HP | Charge/sec |
|--------|--------|------------|
| Front | 11,000 | 12.0 |
| Rear | 5,500 | 12.0 |
| Top | 11,000 | 12.0 |
| Bottom | 11,000 | 12.0 |
| Left | 5,500 | 12.0 |
| Right | 5,500 | 12.0 |

Shield Generator MaxCondition: 10,000.

---

## 3. Cloaking Device [v5-validated 2026-05-28 — cross-anchor: cloaking-state-machine.md]

### State Machine (4 active states)

| Value | State | Timer Behavior |
|-------|-------|----------------|
| 0 | DECLOAKED | — |
| 2 | CLOAKING | Timer counts UP by dt |
| 3 | CLOAKED | — |
| 5 | DECLOAKING | Timer counts DOWN by dt |

**Ghost states 1 and 4** are checked in IsCloaking/IsDecloaking but NEVER written. Dead code from a planned 6-state design.

### Transition Flow

```
DECLOAKED(0) → CLOAKING(2) → CLOAKED(3) → DECLOAKING(5) → DECLOAKED(0)
```

Energy failure auto-decloak: if efficiency < DAT_0088d4ec while CLOAKED, forces DECLOAKING.

### Key Globals

| Address | Type | Name | Value |
|---------|------|------|-------|
| 0x008e4e1c | float | CloakTime (transition duration, class-level global) | **5.0f** (5.0 seconds) [Clar-2] |
| 0x008e4e20 | float | ShieldDelay (post-cloak shield visual hide delay) | 1.0f (1.0 seconds) |

### Tick Function (FUN_0055e500 at 0x0055E500)

- CLOAKING: `timer += dt`, `progress = timer / CloakTime`, at 1.0 → CloakComplete (state=3)
- DECLOAKING: `timer -= dt`, `progress = timer / CloakTime`, at 0.0 → DecloakComplete (state=0)

### Shield Interaction

**Shields do NOT immediately drop to 0 HP when cloaking.**

1. On cloak start: shields are **functionally disabled** via PoweredSubsystem (shieldClass+0x9C=0). HP is PRESERVED.
2. A delayed event fires after ShieldDelay (1.0s default) to hide shield visuals.
3. On decloak complete: shields re-enable after another ShieldDelay delay.
4. If shield HP was <=0 during cloak, reset to 1.0 HP on decloak.

### Weapon Interaction

Weapons are NOT directly gated by cloak state in C++ weapon code. The gating happens through:
1. **Subsystem disable mechanism**: Cloaking calls PoweredSubsystem::Disable on weapon systems
2. **AI/Python layer**: Scripts check `ShipClass.IsCloaked()` before initiating fire
3. **IsCloaked** (`FUN_005AC450` at `0x005AC450`): reads ship+0x2DC (cloak subsystem), returns `+0xAC == 1` (state==3 only, NOT during transitions)

### Network Serialization

StateUpdate flag 0x40 serializes `isOn` byte (+0x9C), NOT the state machine value. Client receives boolean and runs its own local state machine.

### Object Layout

| Offset | Type | Field |
|--------|------|-------|
| +0x9C | byte | isOn (PoweredSubsystem enable) |
| +0xAC | byte | isFullyCloaked (true only in state 3) |
| +0xAD | byte | tryingToCloak (user intent) |
| +0xB0 | int | state (0/2/3/5) |
| +0xB4 | float | timer |

Ship stores CloakingSubsystem at **ship+0x2DC**.

---

## 4. Weapon Systems [v5-validated 2026-05-28 — cross-anchor: weapon-firing-mechanics.md]

### Class Hierarchy

```
Weapon (vtable 0x00892FC4)
  → EnergyWeapon (vtable 0x008930D8, size ~0xC8)
    → PhaserBank (vtable 0x00893194, size 0x128)
  → TorpedoTube (vtable 0x00893630, size 0xB0)
```

### Phaser Charge Formula (FUN_00572B80 at 0x00572B80)

**Recharging** (not firing):
```
charge += recharge_rate * power_level * dt * power_multiplier
// Non-owner ships: *= DAT_00890550 (AI/remote penalty)
// Clamped to max_charge
```

**Discharging** (firing at intensity HIGH or mode 3):
```
charge -= discharge_rate * dt
// If charge <= 0: stop firing
```

Discharge rate varies by intensity mode:

| Mode | Constant |
|------|----------|
| LOW (0) | DAT_0089317C |
| MED (1) | DAT_00893180 |
| HIGH (2) | DAT_00893184 |

### Phaser CanFire Gate Conditions

1. Ship is alive (FUN_00562210 checks class type 0x801C)
2. Subsystem is alive — HP > 0 (FUN_0056c350 recursive check)
3. Subsystem not disabled (DisabledPercentage threshold)
4. Charge >= MinFiringCharge (property+0x74 vs charge at +0xA0)
5. Weapon can-fire flag (property+0x48)
6. Not cloaked (system-level: ET_START_CLOAKING disables weapon systems)

### Phaser EnergyWeaponProperty Offsets

| Offset | Field | Sovereign Default |
|--------|-------|-------------------|
| +0x68 | MaxCharge | 5.0 |
| +0x6C | RechargeRate | 0.08 |
| +0x70 | NormalDischargeRate | 1.0 |
| +0x74 | MinFiringCharge | 3.0 |
| +0x78 | MaxDamage | 300.0 |
| +0x7C | MaxDamageDistance | 70.0 |

### Torpedo Cooldown

Each tube has independent reload timers at +0xAC (float array, one per max_ready slot):
- `-1.0f` = loaded/ready
- `0.0f` = cooldown just started
- `> 0.0f` = cooling down

**ReloadTorpedo** (`FUN_0057D8A0` at `0x0057D8A0`): checks num_ready < max_ready AND ammo available, increments num_ready (+0xA0), finds slot with **largest** timer in +0xAC array and resets to `-1.0f` (0xBF800000).

**Fire** (`FUN_0057C9E0` at `0x0057C9E0`): calls CanFire, creates projectile, decrements num_ready, marks a timer slot as 0.0f, sends opcode 0x19 if host.

### Torpedo Type Switch (FUN_0057B230 at 0x0057B230)

**No explicit lockout timer.** The "lockout" is implicit:

1. `SetAmmoType(type, immediate=1)` (multiplayer path): unload loop runs, **reload loop SKIPPED** — tubes left empty
2. Tubes must go through normal reload cycle from empty
3. Effective lockout = ReloadDelay (40.0s for Sovereign)
4. `SetAmmoType(type, immediate=0)` (local path): unloads + immediately reloads = no lockout

### Torpedo Wire Format (Opcode 0x19)

```
[0x19] [int32:weapon_obj_id] [byte:torpedo_model_idx] [byte:flags]
[compressed_vec3:velocity] [if has_target: int32 target_id] [compressed_vec4:target_offset]
```

---

## 5. Repair System [v5-validated 2026-05-28 — cross-anchor: repair-system.md]

### RepairSubsystem Layout

| Offset | Type | Field |
|--------|------|-------|
| +0x9C | byte | isOn |
| +0xA8 | int | queue count |
| +0xAC | ptr | queue head (linked list) |
| +0xB0 | ptr | queue tail |

Property: +0x4C = MaxRepairPoints (float), +0x50 = NumRepairTeams (int).

### Repair Rate Formula (FUN_005652a0 at 0x005652A0 — VERIFIED)

```
rawRepairAmount = MaxRepairPoints * repairSystem.conditionPct * deltaTime
divisor = min(queueCount, NumRepairTeams)
perSubsystemRepair = rawRepairAmount / divisor
actualConditionGain = perSubsystemRepair / subsystem.RepairComplexity
```

**Key characteristics**:
1. Repair system's OWN health scales output (damaged repair bay = slower)
2. **Multiple subsystems repaired simultaneously** (up to NumRepairTeams)
3. Repair amount divided equally among min(queueCount, numTeams) items
4. RepairComplexity is a final divisor (higher = slower)
5. Destroyed subsystems (condition <= 0) are SKIPPED (post ET_REPAIR_CANNOT_BE_COMPLETED)

### Queue Rules

- **No maximum queue size** — dynamically growing linked list, no hardcoded limit
- **Duplicates rejected** — walks list to check before adding
- **0 HP subsystems excluded** — explicit `condition > 0.0f` check in AddSubsystem
- **Auto-remove on full repair** — ET_REPAIR_COMPLETED when condition/maxCondition >= 1.0
- **Host/standalone only** — gated on IsHost or not-multiplayer

### Sovereign Repair Values

- MaxRepairPoints: 50.0
- NumRepairTeams: 3
- Repair subsystem MaxCondition: 8,000

---

## 6. Tractor Beam [v5-validated 2026-05-28 — freshly binary-anchored this pass]

### Class Hierarchy

```
WeaponSystem → TractorBeamSystem (vtable 0x00893794, size 0x100)
EnergyWeapon → TractorBeamProjector (vtable 0x008936f0, size 0x100)
```

Vtable byte-confirmed: `TractorBeamSystem` at `0x00893794` (slot 0 = `0x00582170` dtor; slot 1 = `0x005820c0`); `TractorBeamProjector` at `0x008936F0` (slot 0 = `0x0057ED80` dtor; slot 1 = `0x0057ECD0`).

### 6 Tractor Modes

| Value | Mode | Behavior |
|-------|------|----------|
| 0 | HOLD | Zero target velocity |
| 1 | TOW | Move target toward source (default) |
| 2 | PULL | Pull target closer |
| 3 | PUSH | Push target away |
| 4 | DOCK_STAGE_1 | Docking approach |
| 5 | DOCK_STAGE_2 | Final docking alignment |

### Tractor Force Formula (FUN_00580f50 at 0x00580F50)

```c
distanceRatio = min(1.0, maxDamageDistance / beamDistance);
force = maxDamage * (systemCondPct * projectorCondPct) * distanceRatio;
if (targetTracker != NULL)         // *(p1+0x24+0xf0) != 0
    force *= targetCondition;       // FUN_0056c740()
return force * deltaTime;
```

Where `systemCondPct = *(p1+0x24+0x34)`, `projectorCondPct = *(p1+0x34)`. The distance threshold gate uses `DAT_0088b9c0 = 0.0f` (at `0x0088B9C0`).

Features NOT in OpenBC spec:
- **Distance falloff**: linear beyond `maxDamageDistance`
- **Health scaling**: both system and projector condition affect force
- **Target condition** scaling (optional)

### Speed Drag (ImpulseEngineSubsystem, FUN_00561230 at 0x00561230)

**Multiplicative**, not additive:
```
tractorRatio = forceUsed / totalMaxDamage    // FUN_005822d0: (p1+0xFC) / (p1+0xF8)
effectiveSpeed *= (1.0 - tractorRatio)
```

At full tractor output, speed drops to zero. At half output, speed is halved. Same ratio applied to acceleration, angular velocity, and angular acceleration. Drag baseline `DAT_00888860 = 1.0f` (at `0x00888860`).

`FUN_005822d0` at `0x005822D0` guards against divide-by-zero: if `*(p1+0xF8) <= 0.0`, returns 0.0; otherwise returns `*(p1+0xFC) / *(p1+0xF8)`. ImpulseEngine stores TractorBeamSystem pointer at +0xA8.

### Tractor Beam Does NOT Apply Direct Damage

All five mode handlers (HOLD, TOW, PULL, PUSH, DOCK_STAGE_2) only manipulate target velocity/angular velocity. **No damage function is called on the target.**

This is confirmed by **xref enumeration of DoDamage (`0x00594020`)**: the complete xref set is exactly `{FUN_005952d0, FUN_005af420, FUN_00593650}` (collision multi-contact, weapon hit, collision single-point). Zero tractor mode handler entries. This is a negative-claim verification — the absence of an xref is the proof.

### Sovereign Tractor Values (from sovereign.py)

- Per-projector MaxDamage: 80.0
- MaxDamageDistance: 114.0
- MaxCharge: 5.0, MinFiringCharge: 3.0
- RechargeRate: 0.3 (aft), 0.5 (forward)
- 4 projectors (2 forward, 2 aft)

---

## 7. Ship Death and Respawn [v5-validated 2026-05-28 — cross-anchor: networking/ship-death-lifecycle.md]

When hull HP <= 0:
1. Server sends **DestroyObject (0x14)** at `0x006A01E0`: `[0x14][object_id:i32]`
2. Server sends **Explosion (0x29)** at `0x006A0080`: `[0x29][object_id:i32][impact:cv4][damage:cf16][radius:cf16]` — byte-confirmed via `CompressedVector4_ReadVirtual` + 2× `CompressedFloat16_Decode` in handler decompile
3. Ship marked dead via vtable[0x138](1,0)
4. Destructor called via vtable[0](1)

Explosion's damage path is distinctive: it **bypasses DoDamage** and calls ProcessDamage (`0x00593E50`) directly. This is why DoDamage's xref set excludes Explosion despite Explosion still damaging ships.

**No dedicated respawn mechanism.** Destroy old object + create new one (ObjCreateTeam 0x03 with fresh HP).

> [!NOTE]
> See [networking/ship-death-lifecycle.md](../networking/ship-death-lifecycle.md) for the full lifecycle including the observation that DestroyObject (0x14) is suppressed Python-side in pure combat traces — the C++ pipeline above describes the full non-combat path.

---

## 8. Sovereign Class Reference Values [v5-validated 2026-05-28 — 100% script-match against reference/scripts/ships/Hardpoints/sovereign.py]

### Hull
- Hull MaxCondition: **12,000** (sovereign.py:515)

### Subsystem HP

| Subsystem | MaxCondition | RepairComplexity |
|-----------|-------------|------------------|
| Shield Generator | 10,000 | **2.0** [Clar-1] |
| Sensor Array | 8,000 | 1.0 |
| Warp Core (reactor) | 7,000 | 2.0 |
| Impulse Engines (system) | 3,000 | 3.0 |
| Port/Star Impulse (each) | 3,000 | — |
| Torpedo System | 6,000 | — |
| Forward Torpedo (each, x4) | 2,200 | — |
| Aft Torpedo (each, x2) | 2,200 | — |
| Phaser Emitter (each, x8) | 1,000 | — |
| Phaser Controller | 8,000 | — |
| Repair | 8,000 | 1.0 |
| Warp Engines (system) | 8,000 | — |
| Port/Star Warp (each) | 4,500 | — |
| Tractor System | 3,000 | 7.0 |
| Tractor (each, x4) | 1,500 | 7.0 |
| Bridge | 10,000 | 4.0 |
| Hull | 12,000 | 3.0 |

All 17 rows verified against the shipped Sovereign hardpoint script line-by-line. The phaser per-tube values, torpedo per-tube values, and tractor per-projector values match across all eight phasers, six torpedo tubes, and four tractor projectors.

---

## 9. OpenBC Corrections Summary

This section is preserved as the consolidated reference for downstream OpenBC implementation. All entries below carry forward from the foundation docs unchanged — they remain accurate as of this v5 pass.

| OpenBC Claim | Verdict | Actual |
|-------------|---------|--------|
| Cloak states: 0,1,2,3 | **WRONG** | States are 0,2,3,5 (ghost states 1,4 never assigned) |
| Shields drop to 0 on cloak | **WRONG** | HP preserved, subsystem functionally disabled |
| Subsystem damage: 50% overflow to nearest by distance | **WRONG** | AABB overlap test (FUN_004bd9f0), no distance-based selection, no 50% split |
| Shield absorption: all-or-nothing per facing | **PARTIALLY WRONG** | Area damage splits 1/6 per facing; directed damage uses geometry intersection |
| Shield recharge: rate * dt | **WRONG** | Power-budget based: (chargePerSec * powerBudget) / (totalPower/6) |
| Repair queue max 8 | **WRONG** | No limit — dynamically growing linked list |
| Only top-priority repaired | **WRONG** | Up to NumRepairTeams subsystems repaired simultaneously |
| Repair rate: max_repair_points * num_repair_teams * dt | **WRONG** | MaxRepairPoints * healthPct * dt / min(queueCount,numTeams) / RepairComplexity |
| Tractor drag: max_damage * dt * 0.1 | **WRONG** | Multiplicative: effectiveSpeed *= (1.0 - forceUsed/totalMaxDamage) |
| Tractor damage: max_damage * dt * 0.02 | **NOT FOUND** | No damage applied by any tractor mode (xref-verified — DoDamage has 3 xrefs, none tractor) |
| Torpedo type switch = explicit lockout timer | **WRONG** | Implicit: all tubes emptied (reload loop skipped), must reload from scratch |
| Sovereign shield HP: 6,000 uniform | **WRONG** | Front=11,000, Rear=5,500, Top=11,000, Bottom=11,000, Left=5,500, Right=5,500 |
| Sovereign hull HP: 12,011 | **WRONG** | 12,000 |
| Sovereign reactor HP: 12,011 | **WRONG** | Warp Core = 7,000 |
| Sovereign torpedo tube HP: 550 | **WRONG** | 2,200 each |
| Sovereign shield generator HP: 6,000 | **WRONG** | 10,000 |
| Sovereign sensor HP: 1,000 | **WRONG** | 8,000 |
| Phaser charge: recharge_rate * power_level * dt | **MOSTLY CORRECT** | Adds power_multiplier param + AI/remote penalty multiplier |
| Phaser 6 fire gates | **CONFIRMED** | Essentially correct, cloak check at system level not per-CanFire |
| Torpedo per-tube independent cooldown | **CONFIRMED** | Timer array at +0xAC, one per slot |
| 0 HP subsystems not auto-queued | **CONFIRMED** | Explicit condition > 0.0f check |

---

## Open Questions (low-priority, deferred)

The following items were noted during the v5 validation pass but did not block `verified` status. They are session-dependent or rely on side-channel functions that were not the focus of this pass:

- **OQ-1** (Section 3): "Shields re-enable after another ShieldDelay delay" on decloak — the decloak-end function (`CloakDisengageRestoreShield`) exists at the implied address but its timing was not re-validated this session. Promotion path: cloaking-state-machine.md when that foundation doc reaches `verified`.
- **OQ-2** (Section 6): The 6 tractor-mode enumeration (HOLD/TOW/PULL/PUSH/DOCK_STAGE_1/DOCK_STAGE_2) was not byte-validated from a switch table this session. The "five mode handlers (HOLD, TOW, PULL, PUSH, DOCK_STAGE_2) only manipulate target velocity" claim is consistent with the no-damage xref result, but the mode-value enumeration source is not anchored.
- **OQ-3** (Section 4): Phaser intensity discharge constants `DAT_0089317C` / `0x80` / `0x84` were not byte-re-confirmed this session. Cross-anchor: weapon-firing-mechanics.md (already validated this pass).
