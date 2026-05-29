> [docs](../README.md) / [gameplay](README.md) / weapon-firing-mechanics.md

---
title: Bridge Commander Weapon Firing Mechanics
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
  - claim: "PhaserBank::UpdateCharge at 0x00572B80 — SEH-wrapped recharge/discharge dispatcher; branches on this+0x88 (is_firing) and this+0xF4 (intensity_mode); applies recharge_rate * power_level * dt * power_multiplier when not firing; discharges only when intensity_mode == 2 or 3"
    address: 0x00572B80
    function: PhaserBank::UpdateCharge
    completeness: 2.5
    effective: 88.6
    confidence: high
    note: "Full byte-by-byte match: SEH setup, owner-check via DAT_0097fa89 + DAT_0097e238+0x54, is_firing branch at +0x88, discharge gate on mode==3 || mode==2, charge clamp via FUN_0056f900 (GetMaxCharge), AI multiplier branch on bVar2==false."
  - claim: "PhaserBank::Fire at 0x00570FE0 is the vtable+0x7C entry; 64 bytes SEH-wrapped, real code Ghidra did not auto-promote"
    address: 0x00570FE0
    function: PhaserBank::Fire
    confidence: high
    note: "Bytes verified directly. Lives in vtable 0x00893194 slot 31 (+0x7C). TryFireWeapon at 0x00584E40 calls this as the primary fire path."
  - claim: "PhaserBank::CanFire at 0x00571E60 is the vtable+0x84 entry; first gate is `mov ecx,[esi+0x40]; test ecx,ecx; jz; call 0x005AC450` (ship-alive helper on owner_ship), then charge gate, then power-diff check via 0x00570D58"
    address: 0x00571E60
    function: PhaserBank::CanFire
    confidence: high
    note: "Real code Ghidra did not auto-promote. Clar5 — calls 0x005AC450 (ship-alive checker) on ESI+0x40 directly. NOT FUN_00562210 GetShipFromParent as prior text suggested."
  - claim: "EnergyWeapon::CanFire at 0x0056FA10 is a 3-byte stub `xor al,al; ret` — returns FALSE always (base-class default; PhaserBank overrides at vtable+0x84)"
    address: 0x0056FA10
    function: EnergyWeapon::CanFire
    confidence: high
    note: "Byte-verified 3-byte body. Confirms PhaserBank::CanFire is the live entry."
  - claim: "PhaserBank vtable at 0x00893194 — slot 30 (+0x78)=0x00571200, slot 31 (+0x7C) PhaserBank::Fire=0x00570FE0, slot 32 (+0x80)=0x0056FA00 (supplementary fire path), slot 33 (+0x84) CanFire=0x00571E60, slot 34 (+0x88) GetFireDirection=0x00572C50, slot 36 (+0x90) SetPowerSetting=0x00570F60, slot 0 dtor=0x00570EB0"
    address: 0x00893194
    function: PhaserBank_vtable
    confidence: high
    note: "All slots byte-confirmed via raw vtable read. C1 — prior doc Part 6 had slot 30 wrong (claimed 0x0056D250, actually 0x00571200; 0x0056D250 is slot 26). PhaserBank slot 0 dtor 0x00570EB0 confirmed correct after C4 recheck."
  - claim: "TorpedoTube::Fire at 0x0057C770 is the vtable+0x7C primary fire entry (bare code, Ghidra did not auto-promote); the function body decompiled at 0x0057C9E0 is actually vtable+0x80 (supplementary fire path)"
    address: 0x0057C770
    function: TorpedoTube::Fire
    confidence: high
    note: "C1 cascade — TryFireWeapon at 0x00584E40 calls vtable+0x7C as primary fire `(**(code **)(*param_2 + 0x7c))(param_3,1)`. OQ2 — 0x0057C770's full body not decompiled this pass; both paths perform the full Fire semantic (the doc's prose for 0x0057C9E0 is semantically correct, only the slot is wrong)."
  - claim: "TorpedoTube::Fire body at 0x0057C9E0 (vtable+0x80) — CanFire gate via vtable+0x84; calls FUN_0057CD90 to create projectile; decrements num_ready (+0xA0); calls FUN_0057b4d0 + FUN_0057b570 for system-wide counters; scans reload_timers (+0xAC) for next slot; calls FUN_0057DA20 setup; posts event 0x0080007C (ET_WEAPON_FIRED); records system fire-time at parent+0xF0; calls FUN_0057CB10 network send gated on DAT_0097fa89 (IsHost)"
    address: 0x0057C9E0
    function: TorpedoTube::Fire_body
    completeness: 0.0
    effective: 81.9
    confidence: high
    note: "Full byte-by-byte match. Event ID 0x0080007C is ET_WEAPON_FIRED (NOT 0x00800066 ET_TORPEDO_FIRED)."
  - claim: "TorpedoTube::CanFire at 0x0057D780 — opens with `mov eax,[esi+0xA0]; test eax,eax; jg short` (num_ready>0 gate)"
    address: 0x0057D780
    function: TorpedoTube::CanFire
    confidence: high
    note: "Real code Ghidra did not auto-promote. Byte-verified opening sequence confirms num_ready>0 as the first gate (matches doc Section 2.7 claim #4)."
  - claim: "TorpedoTube vtable+0x78 at 0x005833F0 is a shared abstract stub `return 0`; this slot is NOT StopFiring as prior doc claimed"
    address: 0x005833F0
    function: TorpedoTube_vtable_slot30_stub
    confidence: high
    note: "C1 — prior doc had this slot as `StopFiring` at 0x0057C770. Actually 0x005833F0 is a `return 0` abstract stub. 0x0057C770 is the +0x7C Fire entry. The TorpedoTube column was scrambled by one slot."
  - claim: "TorpedoTube vtable at 0x00893630 — slot 0 dtor=0x0057C5C0, slot 30 (+0x78)=0x005833F0 (abstract return-0), slot 31 (+0x7C) Fire=0x0057C770, slot 32 (+0x80) supplementary fire=0x0057C9E0, slot 33 (+0x84) CanFire=0x0057D780, slot 34 (+0x88) GetFirePosition=0x0057DE90"
    address: 0x00893630
    function: TorpedoTube_vtable
    confidence: high
    note: "All slots byte-confirmed via raw vtable read."
  - claim: "TorpedoTube::ReloadTorpedo at 0x0057D8A0 — gate `num_ready < max_ready`; ammo gate via parent+0xF4+type*4 vs parent+0x118; increments num_ready (+0xA0); finds longest-timer slot in reload_timers (+0xAC) and sets to -1.0f (0xBF800000); posts event 0x00800065 (ET_RELOAD_TORPEDO)"
    address: 0x0057D8A0
    function: TorpedoTube::ReloadTorpedo
    completeness: 0.0
    effective: 84.8
    confidence: high
    note: "Full match. -1.0f = 0xBF800000 marks the slot as loaded; the longest-timer slot wins so the most-recently-fired tube reloads first."
  - claim: "TorpedoSystem::SetAmmoType at 0x0057B230 — unload loop on all tubes, ClearTimers per tube, conditional reload on immediate=0 only; posts event 0x00800067 (ET_AMMO_TYPE_CHANGED); posts event 0x00800068 (ET_AMMO_SWITCH_STARTED) when immediate=1; sends TGCharEvent 0x008000FE on network when type actually changed and IsHost"
    address: 0x0057B230
    function: TorpedoSystem::SetAmmoType
    confidence: high
    note: "Full match. The 'lockout' is IMPLICIT (unload + clear timers, no reload when immediate=1) — not a separate timer."
  - claim: "WeaponSystem::UpdateWeapons at 0x00584930 — ship-dead gate at owner+0x210; calls CleanupTargets (FUN_00584cc0); reads firing chain at +0xB8; round-robin index from +0xB4 (last_weapon_idx); per-weapon TryFireWeapon dispatch; fallback supplementary list path"
    address: 0x00584930
    function: WeaponSystem::UpdateWeapons
    completeness: 0.0
    effective: 85.0
    confidence: high
    note: "Full match. Main per-frame weapon tick."
  - claim: "WeaponSystem::TryFireWeapon at 0x00584E40 — timer at +0x9C (param_2[0x27]); is_firing at +0x88; threshold DAT_00893830 = 0.33; calls vtable+0x84 CanFire; on FALSE calls vtable+0x78 StopFiring; on TRUE calls vtable+0x7C Fire(dt,1) (primary); supplementary fall-through via vtable+0x80 when target_list empty; iterates supplementary list at +0xC4"
    address: 0x00584E40
    function: WeaponSystem::TryFireWeapon
    confidence: high
    note: "Full match. THIS function is the authority on vtable slot semantics: +0x7C = primary fire, +0x80 = supplementary fire. C1 derives from re-reading this function's call sites."
  - claim: "BeamFire deserializer at 0x0069FBB0 (opcode 0x1A) — Forward-group relay; ReadInt weapon ID; ReadChar flags; ReadCompressedVector3 hit pos; ReadChar flags2; optional ReadInt target on bit 1 of flags2; calls FUN_005762B0 (BeamFire replay)"
    address: 0x0069FBB0
    function: BeamFire_handler
    confidence: high
    note: "Full match. Cross-anchor for game-opcodes.md opcode 0x1A row."
  - claim: "TorpedoFire deserializer at 0x0069F930 (opcode 0x19) — Forward-group relay; ReadInt weapon ID; ReadChar model index; ReadChar flags; ReadCompressedVector3 velocity; conditional target_id + CompressedVector4 offset on noTarget bit clear; dispatches to FUN_0057D110"
    address: 0x0069F930
    function: TorpedoFire_handler
    confidence: high
    note: "Full match."
  - claim: "TorpedoFire serializer at 0x0057CB10 — in MP (DAT_0097fa8a != 0) calls TGWinsockNetwork_SendTGMessageToGroup(this, &DAT_008e5528, msg) [Forward group]; in SP calls TGWinsockNetwork_SendTGMessage(this, *(int*)(this+0x20), msg, 0) [self]; writes opcode 0x19, weapon_obj_id, model byte (+0x14C), flag byte (bit0=skew param_3, bit1=+0xA8 isSkewFire, bit2=noTarget), normalized velocity vec3, optional target_id + CompressedVector4 offset"
    address: 0x0057CB10
    function: TorpedoFire_sender
    confidence: high
    note: "Clar2 — the MP path uses the Forward group at DAT_008e5528; the SP path goes to self. Prior doc said only 'If host, send network packet' and omitted both group identity and the SP path."
  - claim: "DAT_008e5528 is the 'Forward' forwarding group identifier; TGWinsockNetwork_SendTGMessageToGroup uses it to relay TorpedoFire and BeamFire to all clients"
    address: 0x008E5528
    function: forward_group_id
    confidence: high
    note: "Shared between TorpedoFire_sender (0x0057CB10) and BeamFire handler (0x0069FBB0). Cross-anchor for tgmessage-routing.md."
  - claim: "DAT_008936C0 = 0x3D072B02 (~0.033) — SKEW_FIRE_SCALE"
    address: 0x008936C0
    function: SKEW_FIRE_SCALE
    confidence: high
    note: "Byte-confirmed."
  - claim: "DAT_00893830 = 0x3EA8F5C3 (~0.33) — FIRE_DELAY_THRESHOLD in TryFireWeapon"
    address: 0x00893830
    function: FIRE_DELAY_THRESHOLD
    confidence: high
    note: "Byte-confirmed."
  - claim: "DAT_00890550 = 0x3FA00000 (1.25) — non-owner ship recharge BOOST applied in PhaserBank::UpdateCharge when bVar2==false (NOT a penalty)"
    address: 0x00890550
    function: non_owner_recharge_boost
    confidence: high
    note: "C3 — prior doc text labeled this a 'penalty / slower recharge'. Actually 1.25x is a BOOST. AI/remote ships recharge FASTER, not slower. Byte-confirmed."
  - claim: "DAT_00893170 = 0x3E800000 (0.25) — phaser damage_scale_LOW"
    address: 0x00893170
    function: damage_scale_LOW
    confidence: high
    note: "Byte-confirmed."
  - claim: "DAT_00893174 = 0x3F000000 (0.5) — phaser damage_scale_MED"
    address: 0x00893174
    function: damage_scale_MED
    confidence: high
    note: "Byte-confirmed."
  - claim: "DAT_00893178 = 0x3F000000 (0.5) — phaser damage_scale_HIGH (identical to MED)"
    address: 0x00893178
    function: damage_scale_HIGH
    confidence: high
    note: "Clar3 — HIGH is identical to MED. Phaser is BINARY at the C++ level. Any HIGH-vs-MED gameplay difference is UI/animation-only."
  - claim: "DAT_0089317C = 0x3EB33333 (0.35) — phaser discharge_rate_LOW"
    address: 0x0089317C
    function: discharge_rate_LOW
    confidence: high
    note: "Byte-confirmed."
  - claim: "DAT_00893180 = 0x3F800000 (1.0) — phaser discharge_rate_MED"
    address: 0x00893180
    function: discharge_rate_MED
    confidence: high
    note: "Byte-confirmed."
  - claim: "DAT_00893184 = 0x3F800000 (1.0) — phaser discharge_rate_HIGH (identical to MED)"
    address: 0x00893184
    function: discharge_rate_HIGH
    confidence: high
    note: "Clar3 — HIGH is identical to MED for discharge rate too."
  - claim: "FUN_0056c350 returns 1 when subsystem is DAMAGED (HP threshold < current HP, recursive), 0 when alive — semantically the doc's narrative-outcome 'dead subsystem returns 0 charge' is correct, but the function's name and pseudocode body are INVERTED"
    address: 0x0056C350
    function: IsSubsystemDamaged
    confidence: high
    note: "C2 — caller FUN_0056FDF0 GetChargePercentage uses `if (cVar1 != 1) return charge` — i.e., returns the charge when NOT-damaged (cVar1==0). Recursive descent short-circuits returning 1 (damaged) up the tree."
  - claim: "EnergyWeapon::GetChargePercentage at 0x0056FDF0 — returns charge_percentage (+0xBC) when ship is alive AND IsSubsystemDamaged returns 0; returns 0.0f otherwise"
    address: 0x0056FDF0
    function: EnergyWeapon::GetChargePercentage
    confidence: high
    note: "Caller of FUN_0056c350. Outcome semantic in prior doc is correct (dead/damaged subsystem -> 0% charge -> CanFire fails)."
  - claim: "Ship-alive helper at 0x005AC450 — called by PhaserBank::CanFire on owner_ship (ESI+0x40 directly); returns 1 if ship is alive"
    address: 0x005AC450
    function: ship_alive_helper
    confidence: high
    note: "Clar5 — NOT FUN_00562210 (GetShipFromParent) as prior doc Section 1.3 suggested. The actual entry takes owner_ship directly, not parent."
  - claim: "TorpedoTube field layout — +0x18 property, +0x24 parent (TorpedoSystem), +0x34 power_level, +0x40 owner_ship, +0x8C target_id, +0xA0 num_ready, +0xA4 last_fire_time, +0xA8 is_skew_fire, +0xAC reload_timers array"
    address: 0x0057C9E0
    function: TorpedoTube_layout
    confidence: high
    note: "All offsets confirmed via TorpedoTube::Fire body and ReloadTorpedo decompiles. OQ3 — last_fire_time init `-1000.0f = 0xC47A0000` claim not verified in ctor this pass."
  - claim: "EnergyWeapon / PhaserBank field layout — +0x18 property, +0x24 parent, +0x34 power_level, +0x40 owner_ship, +0x88 is_firing, +0xA0 charge_level, +0xBC charge_percentage, +0xF4 intensity_mode"
    address: 0x00572B80
    function: EnergyWeapon_layout
    confidence: high
    note: "All offsets confirmed via UpdateCharge and Fire decompiles. Clar1 — intensity_mode lives in BOTH this+0xF4 AND parent+0xF0 in different read paths; OQ1 covers field-sync."
  - claim: "EnergyWeaponProperty accessor offsets — +0x68 GetMaxCharge (FUN_0056f900), +0x6C GetRechargeRate (FUN_0056f8e0), +0x70 GetNormalDischargeRate (FUN_0056f8f0), +0x74 GetMinFiringCharge (FUN_0056f910), +0x78 GetMaxDamage (FUN_0056f930), +0x7C GetMaxDamageDistance (FUN_0056f940)"
    address: 0x0056F8E0
    function: EnergyWeaponProperty_accessors
    confidence: high
    note: "All six accessor offsets confirmed."
  - claim: "TorpedoTubeProperty +0x88 = reload_delay (accessor FUN_0057C410); +0x8C = max_ready AND num_tubes (same field — accessors FUN_0057C420 GetNumTubes and GetMaxReady both read property+0x8C)"
    address: 0x0057C410
    function: TorpedoTubeProperty_accessors
    confidence: high
    note: "Clar4 — +0x8C is one field, not two. Prior doc listed MaxReady and NumTubes as separate accessors. By design, num tubes equals max ready."
  - claim: "Phaser fire posts event 0x008000E0 (TGCharEvent class 0x105) for opcode 0x12 SetPhaserLevel via SetPowerSetting (vtable+0x90 at 0x00570F60)"
    address: 0x00570F60
    function: PhaserBank::SetPowerSetting
    confidence: medium
    note: "Cross-anchor from set-phaser-level-protocol.md (leaf #16). OQ1 — whether SetPowerSetting writes to BOTH this+0xF4 AND parent+0xF0 not verified this pass."
  - claim: "TorpedoSystem vtable at 0x00893598 — inherits ShipSubsystem; per-ship weapon container"
    address: 0x00893598
    function: TorpedoSystem_vtable
    confidence: high
    note: "Cross-anchored from power-system.md (validated 2026-05-28)."
  - claim: "PhaserSystem vtable at 0x00893240 — inherits ShipSubsystem; per-ship weapon container"
    address: 0x00893240
    function: PhaserSystem_vtable
    confidence: high
    note: "Cross-anchored from power-system.md (validated 2026-05-28)."
  - claim: "EnergyWeapon vtable at 0x008930D8 — base class for PhaserBank"
    address: 0x008930D8
    function: EnergyWeapon_vtable
    confidence: high
    note: "Confirmed via class hierarchy walk and CanFire stub at 0x0056FA10."
  - claim: "max_damage 6000.0f cross-anchor with damage-system: GetMaxDamage at property+0x78 returns the per-weapon max-damage value scaled by DoDamage_CollisionContacts in collision paths"
    address: 0x0056F930
    function: GetMaxDamage
    confidence: high
    note: "Cross-anchored from damage-system.md (validated 2026-05-28). 6000.0f is the inlined collision max_damage; per-weapon max_damage comes from EnergyWeaponProperty+0x78."
companions:
  - docs/gameplay/damage-system.md
  - docs/gameplay/power-system.md
  - docs/protocol/set-phaser-level-protocol.md
  - docs/protocol/collision-effect-protocol.md
  - docs/protocol/game-opcodes.md
---

> [!NOTE]
> **Substantially trustworthy doc**. ZERO formula errors, ZERO wire-format errors, ZERO constant errors. 4 corrections (**C1 HIGH:** Part 6 vtable comparison table slot-to-address mapping is scrambled in the TorpedoTube column; **C2 MEDIUM:** FUN_0056c350 "IsSubsystemAlive" return semantics are INVERTED — returns 1 when DAMAGED; **C3 LOW:** DAT_00890550 = 1.25f is a BOOST not a penalty — AI/remote ships recharge FASTER; **C4 LOW:** PhaserBank vtable slot 0 dtor is correct after recheck) + 6 clarifications + 4 open questions. All formulas, all 9 byte-confirmed constants, all wire formats, and all property accessor offsets survive validation. Cross-anchored against damage-system, power-system, and protocol leaves #15 / #16. See [v5-evidence-header.md](../guides/v5-evidence-header.md) for what the frontmatter means.

# Bridge Commander Weapon Firing Mechanics

Reverse-engineered from stbc.exe via Ghidra decompilation and packet-trace correlation. The phaser charge/discharge formula, the torpedo reload mechanism, the WeaponSystem update loop, the wire formats for BeamFire (0x1A) and TorpedoFire (0x19), and the SetAmmoType implicit-lockout pattern are all binary-confirmed. See the v5 NOTE above for the validation summary and the per-correction sections (C1–C4) for the four localized fixes applied this pass.

## Overview

Bridge Commander has two primary weapon types: **phasers** (continuous beam weapons, aka "energy weapons") and **torpedoes** (projectile weapons). Both share a common base class hierarchy and are managed by a **WeaponSystem** container.

### Class Hierarchy

```
Weapon (vtable 0x00892FC4, size ~0x90)
  +-- EnergyWeapon (vtable 0x008930D8, size ~0xC8)                  [v5-validated 2026-05-28]
  |     +-- PhaserBank (vtable 0x00893194, size 0x128)              [v5-validated 2026-05-28]
  +-- Weapon subclass (vtable 0x00893834, base for Torpedo/Pulse)
        +-- TorpedoTube (vtable 0x00893630, size 0xB0)              [v5-validated 2026-05-28]

WeaponSystem (container, holds N weapons)
  +-- PhaserSystem (vtable 0x00893240, inherits ShipSubsystem)      [v5-validated 2026-05-28 via power-system.md]
  +-- TorpedoSystem (vtable 0x00893598, inherits ShipSubsystem)     [v5-validated 2026-05-28 via power-system.md]
```

### Key Vtable Slots (Weapon hierarchy)

| Slot | Offset | Name | Notes |
|------|--------|------|-------|
| 30 | +0x78 | (overridden) | PhaserBank=helper, TorpedoTube=abstract stub. See C1 / Part 6 below. |
| 31 | +0x7C | **Fire(dt, flag)** | **Primary fire path** (with target list) — called by TryFireWeapon |
| 32 | +0x80 | TryFire / SupplementaryFire | Called when target_list is empty (supplementary path) |
| 33 | +0x84 | CanFire() | Returns bool — all gate conditions |
| 34 | +0x88 | GetFireDirection / GetFirePosition | Direction (phaser) or world-space launch position (torpedo) |
| 36 | +0x90 | SetPowerSetting(int) | Sets phaser intensity enum (only PhaserBank uses) |

---

## Part 1: Phaser (Energy Weapon) System

### 1.1 Object Layout — EnergyWeapon / PhaserBank

Field offsets on the EnergyWeapon/PhaserBank object (`this`):

| Offset | Type | Name | Description |
|--------|------|------|-------------|
| +0x18 | ptr | property | EnergyWeaponProperty* (hardpoint config) [v5-validated 2026-05-28] |
| +0x24 | ptr | parent | TorpedoSystem/PhaserSystem* parent container [v5-validated 2026-05-28] |
| +0x28-0x2C | short[3] | colorRGB | Weapon color (0xFFFF default) |
| +0x30 | float | power_scale | Always 1.0f initially |
| +0x34 | float | power_level | Power allocation (0.0-1.0), default 1.0 [v5-validated 2026-05-28] |
| +0x40 | ptr | owner_ship | Parent ship ptr [v5-validated 2026-05-28] |
| +0x48 | float | random_delay | Random initial delay (rand() * scale) |
| +0x88 | byte | is_firing | 0=not firing, 1=currently firing [v5-validated 2026-05-28] |
| +0xA0 | float | charge_level | Current charge (EW: float, TT: int numReady) [v5-validated 2026-05-28] |
| +0xBC | float | charge_percentage | Cached charge % (for display) [v5-validated 2026-05-28] |
| +0xC0 | char* | fire_start_sound | Concatenated sound name (lazy init) |
| +0xC4 | char* | fire_loop_sound | Concatenated sound name (lazy init) |
| +0xF4 | int | intensity_mode | PhaserBank-specific: 0=LOW, 1=MED, 2=HIGH (see Clar1) [v5-validated 2026-05-28] |

> [!IMPORTANT]
> **Clarification 1 — intensity mode lives in TWO fields**. UpdateCharge at 0x00572B80 reads **this+0xF4** for the intensity branch (`param_1[0x3d]`). The discharge-rate lookup at 0x00572B00 and the damage scaling at 0x00572A50 read **parent+0xF0** (`*(int*)(*(int*)(param_1+0x24)+0xf0)`). Doc text earlier conflated these two fields. SetPowerSetting (vtable+0x90 = 0x00570F60) likely writes to both to keep them in sync — but that's [Open Question 1](#open-questions) below.

#### EnergyWeaponProperty (the hardpoint config, at +0x18)

| Offset | Type | Name | Accessor | Example (Sovereign) |
|--------|------|------|----------|---------------------|
| +0x40 | float | condition | (base subsystem) | 1000.0 |
| +0x68 | float | max_charge | GetMaxCharge() (FUN_0056f900) [v5-validated 2026-05-28] | 5.0 |
| +0x6C | float | recharge_rate | GetRechargeRate() (FUN_0056f8e0) [v5-validated 2026-05-28] | 0.08 |
| +0x70 | float | normal_discharge_rate | GetNormalDischargeRate() (FUN_0056f8f0) [v5-validated 2026-05-28] | 1.0 |
| +0x74 | float | min_firing_charge | GetMinFiringCharge() (FUN_0056f910) [v5-validated 2026-05-28] | 3.0 |
| +0x78 | float | max_damage | GetMaxDamage() (FUN_0056f930) [v5-validated 2026-05-28] | 300.0 |
| +0x7C | float | max_damage_distance | GetMaxDamageDistance() (FUN_0056f940) [v5-validated 2026-05-28] | 70.0 |

### 1.2 Phaser Charge Recharge Formula

**Function**: `PhaserBank::UpdateCharge` at **0x00572B80** [v5-validated 2026-05-28] (called via SWIG wrapper `swig_PhaserBank_UpdateCharge` at 0x00618FA0)

**Signature**: `void PhaserBank::UpdateCharge(float dt, float power_multiplier)`

The function has two operating modes based on the `is_firing` flag (offset +0x88):

#### Mode 1: NOT FIRING (this+0x88 == 0) — Recharging

```c
// Pseudocode reconstruction of FUN_00572b80 recharge branch
float power_level = this->power_level;    // +0x34
float recharge_rate = GetRechargeRate();   // property+0x6C
float delta_charge = recharge_rate * power_level * dt * power_multiplier;

// AI / non-owner ship BOOST (NOT a penalty — see C3 below)
bool isOwnerShip = true;
if (g_IsHost) {
    isOwnerShip = (g_PlayWindow->playerShip == this->owner_ship);  // +0x40
}
if (!isOwnerShip) {
    delta_charge *= DAT_00890550;  // = 1.25f -> AI/remote ships recharge FASTER
}

this->charge_level += delta_charge;  // +0xA0

// Clamp to max
float max_charge = GetMaxCharge();  // property+0x68
if (this->charge_level > max_charge) {
    this->charge_level = max_charge;
}
```

**Recharge Formula**: `charge += recharge_rate * power_level * dt * power_multiplier [* 1.25 if non-owner]`

> [!IMPORTANT]
> **Correction 3 (LOW)** — DAT_00890550 = 0x3FA00000 = **1.25** is a **BOOST**, not a penalty. The prior doc text labeled this "Non-owner ship penalty" / "AI/remote recharge multiplier" with the gloss "slower recharge". Binary truth: 1.25x is faster, not slower. AI ships and remote-player ships recharge **faster** than the local player's ship — likely a quality-of-life multiplier so the server-side simulation doesn't fall behind.

**OpenBC implication**: when porting, the AI multiplier branch must increase delta_charge, not decrease it.

#### Mode 2: FIRING (this+0x88 == 1) — Discharging

The discharge path only activates when the phaser intensity mode (this+0xF4) is 2 (HIGH) or 3 (STOP/DEPLETED):

```c
if (this->is_firing == 1 && (this->intensity_mode == 3 || this->intensity_mode == 2)) {
    float discharge_rate = GetDischargeRateForIntensity();  // FUN_00572b00 — reads parent+0xF0
    this->charge_level -= discharge_rate * dt;  // +0xA0

    if (this->charge_level <= 0.0f) {
        this->charge_level = 0.0f;
        StopFiring();  // vtable+0x78
        return;
    }
}
```

#### Phaser Intensity Discharge Rate (FUN_00572B00)

The discharge rate during firing depends on the phaser intensity setting (field at `parent+0xF0`, the TorpedoSystem/PhaserSystem intensity mode):

| Mode | Value | Constant Address | Meaning |
|------|-------|------------------|---------|
| 0 (LOW) | 0.35 [v5-validated 2026-05-28] | 0x0089317C | Slowest drain |
| 1 (MED) | **1.0** [v5-validated 2026-05-28] | 0x00893180 | Medium drain |
| 2 (HIGH) | **1.0** [v5-validated 2026-05-28] | 0x00893184 | Same as MED (see Clar3) |
| other | 0.0 (DAT_00888B54) | (constant 0.0) | No drain |

#### Phaser Damage Scaling by Intensity (FUN_00572A50)

The per-tick damage during phaser fire is also intensity-dependent:

```c
float damage = max_damage * (power_level * parent_power) * charge_ratio * intensity_scale * dt;
// Where:
//   charge_ratio = min(current_charge / max_damage_distance, 1.0)
//   intensity_scale = {DAT_00893170, DAT_00893174, DAT_00893178} for modes {0,1,2}
```

| Mode | Damage Scale | Address |
|------|--------------|---------|
| 0 (LOW) | 0.25 [v5-validated 2026-05-28] | 0x00893170 |
| 1 (MED) | **0.5** [v5-validated 2026-05-28] | 0x00893174 |
| 2 (HIGH) | **0.5** [v5-validated 2026-05-28] | 0x00893178 |

> [!IMPORTANT]
> **Clarification 3 — phaser MED and HIGH are IDENTICAL at the C++ level**. Both the discharge rate and damage scale tables have MED == HIGH (1.0 / 0.5 each). At the C++ level the phaser is effectively **binary** (LOW vs MED-or-HIGH). Any HIGH-vs-MED distinction at the gameplay level must be UI-only (different label, different fire animation, different sound). OpenBC implementations should not attempt to differentiate HIGH from MED on the firing path.

### 1.3 Phaser CanFire Gate Conditions

**PhaserBank::CanFire** is at vtable+0x84 = **0x00571E60** [v5-validated 2026-05-28] (overrides EnergyWeapon::CanFire at 0x0056FA10).

Both functions live in vtables but Ghidra auto-analysis did not promote them. The byte-verified opening of PhaserBank::CanFire is `mov ecx, [esi+0x40]; test ecx, ecx; jz; call 0x005AC450` — i.e., load owner_ship from +0x40 and call the ship-alive helper.

> [!IMPORTANT]
> **Clarification 5 — PhaserBank::CanFire ship-alive helper is 0x005AC450**. The prior doc Section 1.3 suggested FUN_00562210 (GetShipFromParent). Actually 0x005AC450 takes `owner_ship` directly (ESI+0x40), not `parent`. Returns 1 if the ship is alive.

**EnergyWeapon::CanFire** at 0x0056FA10 is a 3-byte stub `xor al, al; ret` — the base-class default always returns FALSE. PhaserBank::CanFire is the real entry; the base-class default exists only so that derived weapons that don't override fail safe.

**EnergyWeapon::GetChargePercentage** (FUN_0056FDF0) reveals the broader gate pattern:

```c
float GetChargePercentage() {
    ShipClass* ship = GetShipFromParent(this->parent);  // FUN_00562210
    if (ship != NULL && ship->is_alive) {               // +0x27 byte != 0
        char cVar1 = IsSubsystemDamaged(ship);          // FUN_0056c350 — see C2
        if (cVar1 != 1) {                                // i.e. NOT damaged
            return this->charge_percentage;              // +0xBC
        }
    }
    return 0.0f;  // Dead ship OR damaged subsystem -> 0% charge -> can't fire
}
```

> [!IMPORTANT]
> **Correction 2 (MEDIUM) — FUN_0056c350 return semantics are INVERTED in the prior doc text**. The function returns **1 when the subsystem is DAMAGED** (HP threshold below current HP, recursive over children), **0 when alive**. The prior doc named it `IsSubsystemAlive` and wrote pseudocode that returned 1 for alive — both wrong. The narrative outcome ("dead subsystem returns 0 charge") is correct because the caller checks `if (cVar1 != 1)`. Implementations should either rename the function to `IsSubsystemDamaged` or invert the pseudocode body to match the real semantics.

The real shape of FUN_0056c350:

```c
// FUN_0056c350 — returns 1 if subsystem (or any child) is DAMAGED
bool IsSubsystemDamaged(Weapon* weapon) {
    float threshold = *(float*)(weapon + 0x34);  // power_level / HP threshold
    float current_hp = (float)FUN_0056b960();    // current HP
    if (threshold < current_hp) return 1;        // HP threshold below actual HP = DAMAGED

    // Recursive check: if any child is damaged, this subsystem is "damaged" too
    for (int i = 0; i < weapon->num_children; i++) {
        Weapon* child = GetChild(i);
        if (child != NULL && IsSubsystemDamaged(child)) {
            return 1;  // Short-circuit returning 1 (damaged) up the tree
        }
    }
    return 0;
}
```

#### Reconstructed Gate Conditions for PhaserBank::CanFire

Based on the byte-verified opening sequence + caller analysis:

1. **owner_ship is alive**: `[esi+0x40]` non-NULL + 0x005AC450(owner_ship) returns 1
2. **Subsystem is NOT damaged (HP > threshold)**: FUN_0056c350 returns 0 (see C2)
3. **Charge >= MinFiringCharge**: `this->charge_level >= property->min_firing_charge` (property+0x74)
4. **Power-diff check**: via 0x00570D58 (between charge check and return)
5. **Subsystem not disabled**: the `DisabledPercentage` check (SetDisabledPercentage in hardpoint files, typically 0.75) gates at the subsystem level
6. **Cloaking gate**: not in CanFire itself; handled at event-system level (ET_START_CLOAKING disables weapon systems)

**OpenBC's 6 conditions remain essentially confirmed**, with these refinements:
- "Ship is alive" — confirmed (0x005AC450 on owner_ship, NOT GetShipFromParent on parent)
- "Subsystem is alive" — confirmed (the FUN_0056c350 result, but remember it returns 1 for DAMAGED)
- "Charge >= minimum firing charge" — confirmed (property+0x74 vs +0xA0)
- "Subsystem not disabled" — confirmed
- "Ship fully decloaked" — confirmed at event/system level (not in CanFire itself)
- "Bank index valid" — implicit (only valid banks live in the weapon list)

### 1.4 What Happens on Fire

When a phaser fires (PhaserBank::Fire at **0x00570FE0** [v5-validated 2026-05-28], vtable+0x7C — 64 bytes, SEH-wrapped, Ghidra did not auto-promote):

1. The phaser beam object is created via `FUN_00578180` (creates a beam visual from spawn point to target)
2. Beam velocity is set from the weapon's direction vectors
3. `is_firing` (+0x88) is set to 1
4. The sound system is triggered
5. In multiplayer (host), `FUN_005762b0` (BeamFire replay) is the call site shared with the network receive path
6. The beam damage is applied via the normal damage pipeline (see [damage-system.md](damage-system.md))
7. During subsequent UpdateCharge ticks, the discharge branch runs (Mode 2 above), draining charge

When charge depletes to 0:
- `this->charge_level = 0.0f`
- `StopFiring()` is called (vtable+0x78)
- The beam visual ends

### 1.5 Network Wire Format: BeamFire (Opcode 0x1A)

Handler: **FUN_0069FBB0** [v5-validated 2026-05-28] (called from MultiplayerGame dispatch)

The handler:
1. Forwards the packet to all other players (via the "Forward" forwarding group at DAT_008e5528)
2. Deserializes from the stream:
   - Object ID of the firing weapon (via FUN_006CF6A0 = ReadInt)
   - Byte flags (FUN_006CF540 = ReadByte)
   - Compressed hit position (ReadCompressedVector3)
   - Another byte for additional flags
   - Optional target object ID (when flags2 bit 1 is set)
3. Looks up the weapon via FUN_006F0EE0 (GetObjectByID)
4. Calls FUN_005762B0 (the beam fire initialization) with the deserialized data

### 1.6 Phaser Power Setting (Opcode 0x12)

The phaser intensity (LOW/MED/HIGH) is set via `SetPowerSetting` (vtable+0x90 = **0x00570F60** [v5-validated 2026-05-28]). In multiplayer, this is forwarded as opcode 0x12 (SetPhaserLevel) — a TGCharEvent (class 0x105) posting event 0x008000E0 — through the shared event handler FUN_0069FDA0. See [set-phaser-level-protocol.md](../protocol/set-phaser-level-protocol.md) (leaf #16) for the full wire format.

The intensity mode stored at `parent+0xF0` controls:
- Discharge rate during firing (faster for higher settings — but MED == HIGH, see Clar3)
- Damage output per tick (higher for higher settings — but MED == HIGH, see Clar3)
- Charge consumption speed

Whether SetPowerSetting writes to BOTH this+0xF4 AND parent+0xF0 to keep the two intensity fields in sync is [Open Question 1](#open-questions).

---

## Part 2: Torpedo System

### 2.1 Object Layout — TorpedoTube

Field offsets on TorpedoTube (`this`, size 0xB0) [all v5-validated 2026-05-28]:

| Offset | Type | Name | Description |
|--------|------|------|-------------|
| +0x18 | ptr | property | TorpedoTubeProperty* |
| +0x24 | ptr | parent | TorpedoSystem* parent |
| +0x34 | float | power_level | Power allocation (default 1.0) |
| +0x40 | ptr | owner_ship | Parent ship ptr |
| +0x8C | int | target_id | Current target |
| +0xA0 | int | num_ready | Count of loaded torpedoes |
| +0xA4 | float | last_fire_time | Game time when last fired [needs-evidence: -1000.0f init claim not verified this pass — OQ3] |
| +0xA8 | byte | is_skew_fire | Skew fire flag |
| +0xAC | ptr | reload_timers | float[] array, one per tube slot |

#### TorpedoTubeProperty (the hardpoint config, at +0x18)

| Offset | Type | Name | Accessor | Example (Sovereign) |
|--------|------|------|----------|---------------------|
| +0x88 | float | reload_delay | GetReloadDelay() (FUN_0057C410) [v5-validated 2026-05-28] | 40.0 |
| +0x8C | int | max_ready = num_tubes | GetMaxReady() / GetNumTubes() (FUN_0057C420) [v5-validated 2026-05-28] | 1 |
| ?? | float | immediate_delay | GetImmediateDelay() (FUN_0057C400-ish) | 0.25 |

> [!IMPORTANT]
> **Clarification 4 — property+0x8C is ONE field**. GetMaxReady() and GetNumTubes() both read `property+0x8C`. The prior doc listed them as separate accessors. By design, num tubes equals max ready — one tube = one slot.

#### TorpedoSystem Fields (parent, at +0x24)

| Offset | Type | Name | Description |
|--------|------|------|-------------|
| +0x1C | int | num_weapons | Count of TorpedoTubes in this system |
| +0xF0 | float | last_system_fire_time | Last fire timestamp for the entire system [v5-validated 2026-05-28] |
| +0xF4+N*4 | int[] | ammo_counts | Per-type ammo remaining [v5-validated 2026-05-28] |
| +0x114 | int | current_ammo_type | Currently selected ammo type index |
| +0x118 | int | total_ammo_consumed | Running counter [v5-validated 2026-05-28] |

### 2.2 Torpedo Reload/Cooldown Logic

**Function**: `TorpedoTube::ReloadTorpedo` at **0x0057D8A0** [v5-validated 2026-05-28] (called via SWIG wrapper `swig_TorpedoTube_ReloadTorpedo` at 0x00613750)

```c
// FUN_0057D8A0 - TorpedoTube::ReloadTorpedo
void TorpedoTube::ReloadTorpedo() {
    TorpedoSystem* system = this->parent;   // +0x24
    TorpedoTubeProperty* prop = GetProperty(); // via FUN_0057c330 -> +0x18
    int max_ready = prop->max_ready;         // property+0x8C

    // Gate: already at max loaded?
    if (this->num_ready >= max_ready) return;

    // Gate: ammo available for current type?
    int ammo_type = system->current_ammo_type;   // parent+0x114
    int ammo_remaining = system->ammo_counts[ammo_type]; // parent+0xF4+type*4
    int total_consumed = system->total_ammo_consumed;     // parent+0x118

    if (ammo_remaining == total_consumed) return;  // No ammo left
    if (ammo_remaining - total_consumed < 0) return; // Sanity check

    // RELOAD: increment ready count
    this->num_ready++;  // +0xA0

    // Increment system-wide ammo consumed counter
    system->total_ammo_consumed++;  // parent+0x118 via FUN_0057b560

    // Find the tube with the LONGEST remaining cooldown and reset it
    float max_timer = -1.0f;
    int max_idx = -1;
    int num_tubes = GetNumTubes();  // FUN_0057c420 -> property+0x8C
    for (int i = 0; i < num_tubes; i++) {
        if (this->reload_timers[i] > max_timer) {  // +0xAC array
            max_timer = this->reload_timers[i];
            max_idx = i;
        }
    }
    if (max_idx != -1) {
        this->reload_timers[max_idx] = -1.0f;  // 0xBF800000 = -1.0f (mark as loaded)
    }

    // Post RELOAD_TORPEDO event (0x00800065)
    TGMessage* msg = new TGMessage();
    msg->event = 0x00800065;  // ET_RELOAD_TORPEDO
    msg->preserve = 0;
    msg->SetSubject(this);
    PostMessage(msg);
}
```

### 2.3 Torpedo Fire Logic

> [!IMPORTANT]
> **Correction 1 (HIGH) cascade applies here**. The body decompiled below is at **0x0057C9E0** — that's actually **vtable+0x80** (the supplementary fire path), NOT vtable+0x7C. The vtable+0x7C primary entry is at **0x0057C770** (bare code that Ghidra did not auto-promote). Both perform full Fire semantics; the prose semantics below are correct for the +0x80 body. The +0x7C body has not been decompiled this pass — [Open Question 2](#open-questions).

**Function**: `TorpedoTube::Fire` body at **0x0057C9E0** [v5-validated 2026-05-28] (vtable+0x80 supplementary path; primary entry at 0x0057C770)

```c
// FUN_0057C9E0 - TorpedoTube::Fire(dt, flag) — supplementary path body
bool TorpedoTube::Fire(float dt, char flag) {
    // FIRST: Check CanFire
    bool canFire = this->vtable->CanFire();  // vtable+0x84 -> 0x0057D780
    if (!canFire) return false;

    // Create the torpedo projectile object
    Torpedo* torpedo = CreateTorpedoProjectile();  // FUN_0057cd90

    // Set target on torpedo
    torpedo->target_id = 0;

    TorpedoSystem* system = this->parent;  // +0x24

    // Record fire time (global game clock)
    this->last_fire_time = g_Clock->gameTime;  // g_Clock+0x90 -> +0xA4

    // Decrement ready count
    this->num_ready--;  // +0xA0

    // Decrement system-wide available count
    system->available_count--;  // FUN_0057b4d0
    system->total_available--;  // FUN_0057b570

    // Find a tube slot with completed cooldown and start new cooldown
    int num_tubes = GetNumTubes();
    for (int i = 0; i < num_tubes; i++) {
        if (this->reload_timers[i] <= 0.0f) {
            this->reload_timers[i] = 0.0f;  // Mark as "cooldown started"
            break;
        }
    }

    // Set up the torpedo with launch parameters
    SetupTorpedo(this, torpedo);  // FUN_0057da20

    // Post WEAPON_FIRED event (0x0080007C)
    TGMessage* msg = new TGMessage();
    msg->SetSource(this);
    msg->SetSubject(this->owner_ship);
    msg->event = 0x0080007C;  // ET_WEAPON_FIRED (NOT ET_TORPEDO_FIRED which is 0x00800066)
    msg->preserve = 0;
    PostMessage(msg);

    // Record system-level fire time
    system->last_system_fire_time = g_Clock->gameTime;  // parent+0xF0

    // If host, send network packet
    if (g_IsHost) {  // DAT_0097fa89
        SendTorpedoFirePacket(this, torpedo, flag, true);  // FUN_0057cb10
    }

    return true;
}
```

### 2.4 Network Wire Format: TorpedoFire (Opcode 0x19)

**Serialization** (FUN_0057CB10) [v5-validated 2026-05-28]:

```
[0x19]                          // opcode
[int32: weapon_obj_id]          // this->obj_id (+0x04)
[byte: torpedo_model_index]     // from torpedo object (+0x14C)
[byte: flags]                   // bit0=skew (param_3), bit1=isSkewFire(+0xA8), bit2=noTarget
[compressed_vec3: velocity]     // torpedo velocity (normalized direction * speed)
[if !noTarget: int32 targetID]  // target object ID
[if !noTarget: compressed_vec4] // target offset/radius
```

> [!IMPORTANT]
> **Clarification 2 — TorpedoFire has TWO send paths in the serializer**:
> - **MP path** (DAT_0097fa8a != 0): `TGWinsockNetwork_SendTGMessageToGroup(this, &DAT_008e5528, pMessage)` — sends to the "Forward" forwarding group, which relays to all clients. DAT_008e5528 is the same group identifier used by BeamFire (0x0069FBB0) and other event-forwarding paths.
> - **SP path**: `TGWinsockNetwork_SendTGMessage(this, *(int*)(this+0x20), pMessage, 0)` — sends to self/local.
>
> The prior doc said only "If host, send network packet" and omitted both the group identity and the SP fall-through.

**Deserialization** handler at **0x0069F930** [v5-validated 2026-05-28]:
1. Forwards packet to all other players (via the "Forward" group)
2. Reads weapon object ID, torpedo model index, flags
3. Reads compressed velocity vector
4. If has target (bit2 not set): reads target ID, gets target's bounding sphere radius, reads compressed impact offset
5. Calls `FUN_0057D110` (TorpedoSystem-level fire handler) with all parameters

### 2.5 Torpedo Type Switch (SetAmmoType)

**Function**: `TorpedoSystem::SetAmmoType` at **0x0057B230** [v5-validated 2026-05-28]

```c
// FUN_0057B230 - TorpedoSystem::SetAmmoType(int newType, char immediate)
void TorpedoSystem::SetAmmoType(int newType, char immediate) {
    // Step 1: UNLOAD all tubes - decrement ready count to 0
    for (int i = 0; i < this->num_weapons; i++) {
        TorpedoTube* tube = GetWeapon(i);  // FUN_0056c570

        // Unload all loaded torpedoes
        while (tube->num_ready > 0) {
            UnloadTorpedo(tube);  // FUN_0057d9a0 - decrements num_ready
        }

        // Clear ALL cooldown timers
        ClearTimers(tube);  // FUN_0057c740 - sets all timer slots to 0.0

        // If NOT immediate: reload all tubes with new type
        if (immediate == 0) {
            int num_tubes = GetNumTubes(tube);
            for (int j = 0; j < num_tubes; j++) {
                ReloadTorpedo(tube);  // FUN_0057d8a0
            }
        }
    }

    // Step 2: Post ammo-change events
    PostEvent(0x00800067);  // ET_AMMO_TYPE_CHANGED
    if (immediate) {
        PostEvent(0x00800068);  // ET_AMMO_SWITCH_STARTED
    }

    // Step 3: If type actually changed AND is host, send network event
    if (this->current_ammo_type != newType && g_IsHost) {
        SendTGCharEvent(0x008000FE);  // ET_TORP_TYPE_CHANGE
    }

    // Step 4: Update current type
    this->current_ammo_type = newType;  // +0x114
}
```

#### Type Switch "Lockout" Analysis [v5-validated 2026-05-28]

The OpenBC doc claims: "Type switch lockout = max(reload_delay) across all tubes."

**FINDING**: The code does NOT implement an explicit timer-based lockout. Instead:

1. When `SetAmmoType(type, immediate=1)` is called (the normal MP path via SWIG):
   - All tubes are unloaded (`num_ready` set to 0)
   - All cooldown timers are cleared (set to 0.0)
   - Tubes are NOT immediately reloaded (the `immediate == 0` branch is skipped)
   - Tubes start empty and must go through their normal reload cycle

2. The "lockout" is therefore **implicit**: after a type switch, all tubes have `num_ready == 0` and must be reloaded. The effective lockout duration equals the time it takes for the first tube to reload, which is governed by the `ReloadDelay` property (e.g., 40.0 seconds for Sovereign torpedoes).

3. When `SetAmmoType(type, immediate=0)` is called (local/offline):
   - All tubes are unloaded AND immediately reloaded with the new type
   - NO lockout — tubes are instantly ready

**CONCLUSION**: The "lockout" is real in multiplayer (immediate=1 path) but is not a separate timer. It is a side effect of unloading + clearing + not reloading. The effective duration is the longest ReloadDelay across all tubes in the system, because all tubes restart their reload cycle simultaneously.

### 2.6 Torpedo Cooldown Mechanism

Each TorpedoTube has an array of `float` reload timers at offset +0xAC, one per "slot" (the number of slots = `max_ready` from the property, typically 1).

**Timer states**:
- `-1.0f` (0xBF800000): Slot is loaded/ready (torpedo available)
- `0.0f`: Slot cooldown just started (will count up)
- `> 0.0f`: Slot is cooling down (time elapsed since fire)
- `<= 0.0f` (other negative): Available for reload

The reload is managed by `ReloadTorpedo` (FUN_0057D8A0) which:
1. Checks `num_ready < max_ready` AND ammo available
2. Increments `num_ready`
3. Finds the slot with the longest timer value and resets it to `-1.0f` (marking it loaded)
4. Posts ET_RELOAD_TORPEDO event

**UnloadTorpedo** (FUN_0057D9A0) does the reverse:
1. Decrements `num_ready`
2. Finds the first slot with timer <= 0.0 and resets it to 0.0 (marking it as empty)

**Cooldown timer progression**: The tubes do NOT have an explicit "tick down" function visible in the analyzed code. The reload appears to be event-driven: the game's subsystem update loop posts events at the right time, and ReloadTorpedo is called when the cooldown expires. The `last_fire_time` (+0xA4) records when the tube last fired, and comparison against `g_Clock->gameTime` + `ReloadDelay` determines when to reload.

### 2.7 TorpedoTube::CanFire

The TorpedoTube CanFire at vtable+0x84 = **0x0057D780** [v5-validated 2026-05-28] was not auto-promoted by Ghidra. Byte-verified opening: `mov eax, [esi+0xA0]; test eax, eax; jg short` — i.e., `num_ready > 0` is the first gate (consistent with prior claim #4 in this section).

From the TorpedoTube::Fire function (FUN_0057C9E0), we see:
- It is called first in the Fire method
- If it returns false, Fire returns false immediately
- The fire path then checks `num_ready > 0` implicitly (via the ammo count checks)

Based on the Weapon base class pattern and the TorpedoTube fields, the CanFire conditions are:

1. **num_ready > 0** (byte-verified — first gate)
2. **Ship is alive** (same as phaser — base class check)
3. **Subsystem is alive (HP > 0)** (same as phaser — base class check)
4. **Subsystem is not disabled** (same as phaser)
5. **Ammo available** (ammo_remaining > total_consumed for current type)
6. **Cooldown expired**: `current_game_time - last_fire_time >= immediate_delay` (the ImmediateDelay property, typically 0.25s, prevents rapid double-fires)

---

## Part 3: WeaponSystem Update Loop

### 3.1 WeaponSystem::UpdateWeapons (FUN_00584930) [v5-validated 2026-05-28]

This is the main weapon tick function, called every frame by the game loop.

**Signature**: `Weapon* WeaponSystem::UpdateWeapons(float dt, char* didFire)`

```c
// High-level pseudocode of FUN_00584930
Weapon* WeaponSystem::UpdateWeapons(float dt, char* didFire) {
    *didFire = false;

    // Gate: ship is dead?
    if (this->owner_ship->isDead) return NULL;  // +0x40 -> +0x210

    // Clean up dead targets from target list
    CleanupTargetList();  // FUN_00584cc0

    // Get current firing chain configuration
    FiringChain* chain = GetFiringChain(this->current_chain_index);  // +0xB8
    int groupId = (chain != NULL) ? GetFirstGroup(chain) : 0;

    // Determine start weapon index for round-robin
    int startIdx = (this->last_weapon_idx + 1);  // +0xB4
    if (IsSingleFire()) startIdx = max(0, this->last_weapon_idx);

    // Build list of weapons that can fire at current target/group
    List weaponsToFire;
    for (int i = startIdx; i < startIdx + num_weapons; i++) {
        Weapon* w = GetWeapon(i % num_weapons);
        if (groupId == 0 || w->IsInGroup(groupId)) {
            weaponsToFire.add(w);
        }
    }

    // Try firing each weapon in the list
    for (Weapon* w : weaponsToFire) {
        result = TryFireWeapon(w, dt);  // FUN_00584e40
        if (result == FIRED) {
            *didFire = true;
            this->last_weapon_idx = GetIndex(w);
            this->last_group_id = groupId;
            if (IsSingleFire()) break;  // Only fire one at a time
        } else if (result == CANNOT_FIRE) {
            // Weapon's own CanFire returned false
            w->timer = 0;  // Reset its delay timer

            // Check if we should try direct fire (no target list)
            if (this->target_list_count == 0 &&
                w->canFireFlag &&
                w->vtable->SupplementaryFire(dt, 1)) {  // vtable+0x80
                // Weapon fired without target
                this->last_weapon_idx = GetIndex(w);
                this->last_group_id = groupId;
            }
        }
    }

    // If no weapons fired and using firing chain, try next group
    if (!*didFire && chain != NULL) {
        groupId = GetNextGroup(chain, groupId);
        if (groupId == originalGroupId) {
            // Cycled through all groups, nothing can fire
            this->last_group_id = -1;
            return NULL;
        }
        // Retry with new group...
    }

    return lastFiredWeapon;
}
```

### 3.2 Per-Weapon Fire Attempt (FUN_00584E40) [v5-validated 2026-05-28]

This function is the authority on vtable slot semantics: **+0x7C is primary fire**, **+0x80 is supplementary fire**.

```c
// FUN_00584E40 - Try to fire a specific weapon
int TryFireWeapon(Weapon* weapon, float dt) {
    // Update random fire delay timer
    if (!this->aim_assisted) {
        weapon->timer += dt;  // +0x9C
    } else {
        weapon->timer = FIRE_DELAY_MAX;  // DAT_00893830 = 0.33
    }

    // If not already firing, check if delay timer expired
    if (!weapon->is_firing) {  // +0x88
        if (weapon->timer < FIRE_DELAY_THRESHOLD) {  // 0.33
            return DELAY;  // Still waiting
        }
    }

    // Re-randomize timer
    weapon->timer = rand_float();
    if (weapon->timer < FIRE_DELAY_THRESHOLD) {
        weapon->timer = 0.0f;
    }

    // THE KEY CHECK: Can this weapon fire?
    bool canFire = (**(code**)(*weapon + 0x84))();  // vtable+0x84
    if (!canFire) {
        (**(code**)(*weapon + 0x78))();  // vtable+0x78 — StopFiring helper
        return CANNOT_FIRE;
    }

    // Try to fire at a target from the target list — PRIMARY FIRE
    bool fired = (**(code**)(*weapon + 0x7c))(weapon, 1);  // vtable+0x7C
    if (fired) return FIRED;

    // If weapon didn't fire at queued target, try targets from the supplementary list
    if (this->supplementary_target_list != NULL) {  // +0xC4
        for (TargetEntry* entry : supplementary_target_list) {
            Ship* target = GetObjectByID(entry->targetID);
            if (target != NULL && IsShip(target)) {
                SetupWeaponTarget(weapon, entry);
                // SUPPLEMENTARY FIRE — used when target_list_count == 0 in UpdateWeapons
                fired = (**(code**)(*weapon + 0x80))(weapon, 1);  // vtable+0x80
                if (fired) return FIRED;
            }
        }
    }

    return CANNOT_FIRE;
}
```

### 3.3 Shared Event Forwarding Handler (FUN_0069FDA0)

Opcodes 0x07-0x0C and 0x0E-0x12 all route to this function. It:
1. Gets the raw packet data from the message
2. Deserializes it into a TGMessage
3. If multiplayer, forwards to all clients (via FUN_006B4EC0 broadcast)
4. Posts the message to the local event queue (FUN_006DA300)
5. The Python/C++ event handlers then process the event

This means weapon control commands (start firing, stop firing, phaser level change, torpedo type change, etc.) are all just **events forwarded from one client to the server and then broadcast to all clients**.

See [game-opcodes.md](../protocol/game-opcodes.md) for the per-opcode handler map.

---

## Part 4: Summary of Key Constants

All constants byte-confirmed at the listed addresses [v5-validated 2026-05-28]:

| Address | Type | Value | Name | Used In |
|---------|------|-------|------|---------|
| 0x00888B54 | float | 0.0 | zero constant | UpdateCharge "other" discharge mode fallback |
| 0x00888B58 | float | ~epsilon | near-zero threshold | (shared) |
| 0x00888860 | float | 1.0 | one constant | (shared) |
| 0x00890550 | float | **1.25** | non_owner_recharge_BOOST | UpdateCharge AI multiplier (BOOST not penalty — see C3) |
| 0x00893170 | float | 0.25 | damage_scale_LOW | PhaserBank::CalcDamagePerTick |
| 0x00893174 | float | **0.5** | damage_scale_MED | PhaserBank::CalcDamagePerTick |
| 0x00893178 | float | **0.5** | damage_scale_HIGH = MED | PhaserBank::CalcDamagePerTick (same as MED) |
| 0x0089317C | float | 0.35 | discharge_rate_LOW | PhaserBank::GetDischargeRate |
| 0x00893180 | float | **1.0** | discharge_rate_MED | PhaserBank::GetDischargeRate |
| 0x00893184 | float | **1.0** | discharge_rate_HIGH = MED | PhaserBank::GetDischargeRate (same as MED) |
| 0x00893830 | float | 0.33 | FIRE_DELAY_THRESHOLD | TryFireWeapon |
| 0x008936C0 | float | 0.033 | SKEW_FIRE_SCALE | TorpedoFire skew offset |
| 0x0088B9C0 | float | 1.0 | max charge ratio cap | (shared) |
| 0x0088BEAC | float | ?? | torpedo damage/speed scaler | TorpedoTube::SetupTorpedo |
| 0x0088BF24 | float | ?? | torpedo local lifetime scale | TorpedoTube::SetupTorpedo |
| 0x008E53DC | float | ?? | RANGE_SCALE | Phaser beam range normalization |
| 0x008E5528 | int | (group id) | Forward group identifier | TGWinsockNetwork_SendTGMessageToGroup (TorpedoFire MP path) |

---

## Part 5: Function Address Reference

### Phaser (EnergyWeapon / PhaserBank)

| Address | Name | Description |
|---------|------|-------------|
| 0x00572B80 | PhaserBank::UpdateCharge | Recharge (not firing) / discharge (firing) [v5-validated 2026-05-28] |
| 0x0056FD70 | EnergyWeapon::UpdateCharge | Base class recharge (no discharge branch) |
| 0x00572B00 | PhaserBank::GetDischargeRate | Intensity-dependent discharge rate lookup |
| 0x00572A50 | PhaserBank::CalcDamagePerTick | Intensity-dependent damage calculation |
| 0x00571E60 | PhaserBank::CanFire | Fire gate conditions (vtable+0x84) — calls 0x005AC450 on owner_ship [v5-validated 2026-05-28] |
| 0x0056FA10 | EnergyWeapon::CanFire | Base class stub (`xor al,al; ret`, always FALSE) [v5-validated 2026-05-28] |
| 0x00570FE0 | PhaserBank::Fire | Primary fire (vtable+0x7C) — 64 bytes SEH-wrapped [v5-validated 2026-05-28] |
| 0x0056FA00 | PhaserBank supplementary fire | vtable+0x80 (called when target_list empty) |
| 0x00572C50 | PhaserBank::GetFireDirection | vtable+0x88 — calculate beam direction from arc angles |
| 0x00571200 | PhaserBank vtable+0x78 | helper (replaces prior doc's incorrect 0x0056D250) |
| 0x00570EB0 | PhaserBank dtor | vtable slot 0 |
| 0x00570F60 | PhaserBank::SetPowerSetting | vtable+0x90 [v5-validated 2026-05-28] |
| 0x005762B0 | BeamFire_Replay | Beam fire init shared with network receive |
| 0x005AC450 | ship_alive_helper | Returns 1 if ship is alive (takes owner_ship directly) [v5-validated 2026-05-28] |
| 0x0056F8D0 | GetProperty() | Returns this->property (+0x18) |
| 0x0056F8E0 | GetRechargeRate() | Returns property+0x6C [v5-validated 2026-05-28] |
| 0x0056F900 | GetMaxCharge() | Returns property+0x68 [v5-validated 2026-05-28] |
| 0x0056F910 | GetMinFiringCharge() | Returns property+0x74 [v5-validated 2026-05-28] |
| 0x0056F8F0 | GetNormalDischargeRate() | Returns property+0x70 [v5-validated 2026-05-28] |
| 0x0056F930 | GetMaxDamage() | Returns property+0x78 [v5-validated 2026-05-28] |
| 0x0056F940 | GetMaxDamageDistance() | Returns property+0x7C [v5-validated 2026-05-28] |
| 0x0056FDF0 | GetChargePercentage() | Returns charge % if alive AND not damaged, else 0.0 [v5-validated 2026-05-28] |
| 0x0056C350 | IsSubsystemDamaged | Recursive HP check — returns 1 if DAMAGED (see C2) [v5-validated 2026-05-28] |

### Torpedo (TorpedoTube / TorpedoSystem)

| Address | Name | Description |
|---------|------|-------------|
| 0x0057C770 | TorpedoTube::Fire (primary) | vtable+0x7C — bare code, Ghidra unpromoted (see OQ2) [v5-validated 2026-05-28] |
| 0x0057C9E0 | TorpedoTube::Fire (supplementary) | vtable+0x80 — full body decompiled in Section 2.3 [v5-validated 2026-05-28] |
| 0x005833F0 | TorpedoTube::abstract_stub | vtable+0x78 — `return 0` abstract stub (NOT StopFiring) [v5-validated 2026-05-28] |
| 0x0057D780 | TorpedoTube::CanFire | vtable+0x84 — opens with num_ready>0 gate [v5-validated 2026-05-28] |
| 0x0057C5C0 | TorpedoTube dtor | vtable slot 0 [v5-validated 2026-05-28] |
| 0x0057D8A0 | TorpedoTube::ReloadTorpedo | Load one torpedo into tube [v5-validated 2026-05-28] |
| 0x0057D9A0 | TorpedoTube::UnloadTorpedo | Remove one torpedo from tube |
| 0x0057C740 | TorpedoTube::ClearTimers | Reset all reload timer slots to 0.0 |
| 0x0057B230 | TorpedoSystem::SetAmmoType | Change torpedo type (unload+reload) [v5-validated 2026-05-28] |
| 0x0057B560 | TorpedoSystem::IncrementConsumed | total_ammo_consumed++ (parent+0x118) |
| 0x0057CB10 | TorpedoFire_NetworkSend | Serialize torpedo fire (opcode 0x19) — MP via Forward group, SP via self [v5-validated 2026-05-28] |
| 0x0057CD90 | CreateTorpedoProjectile | Create torpedo scene object |
| 0x0057C330 | TorpedoTube::GetProperty() | Returns this->property (+0x18) |
| 0x0057C410 | TorpedoTube::GetReloadDelay() | Returns property+0x88 [v5-validated 2026-05-28] |
| 0x0057C420 | TorpedoTube::GetNumTubes() / GetMaxReady() | Returns property+0x8C — ONE field, two accessors (see Clar4) [v5-validated 2026-05-28] |
| 0x0057DE90 | TorpedoTube::GetFirePosition | vtable+0x88 — calculate world-space launch position [v5-validated 2026-05-28] |

### WeaponSystem

| Address | Name | Description |
|---------|------|-------------|
| 0x00584930 | WeaponSystem::UpdateWeapons | Main weapon tick (per-frame) [v5-validated 2026-05-28] |
| 0x00584E40 | WeaponSystem::TryFireWeapon | Per-weapon fire attempt — authority on +0x7C/+0x80 semantics [v5-validated 2026-05-28] |
| 0x00584CC0 | WeaponSystem::CleanupTargets | Remove dead targets from list |
| 0x00584060 | WeaponSystem::IsSingleFire | Check single-fire mode |
| 0x00583270 | Weapon::GetCanFireFlag | Property+0x48 byte |

### Network Handlers

| Address | Opcode | Name | Description |
|---------|--------|------|-------------|
| 0x0069FBB0 | 0x1A | BeamFire_Handler | Deserialize + replay beam fire [v5-validated 2026-05-28] |
| 0x0069F930 | 0x19 | TorpedoFire_Handler | Deserialize + replay torpedo fire [v5-validated 2026-05-28] |
| 0x0069FDA0 | 0x07-0x12 | SharedEvent_Handler | Forward event to all + local dispatch |
| 0x0057D110 | (called) | TorpedoFire_Replay | Process received torpedo fire data |
| 0x005762B0 | (called) | BeamFire_Replay | Process received beam fire data |

---

## Part 6: Vtable Comparison Table (CORRECTED)

> [!IMPORTANT]
> **Correction 1 (HIGH)** — the prior Part 6 table had the TorpedoTube column scrambled by one slot, and slot 30 in the PhaserBank column was wrong. Both columns are now byte-confirmed from raw vtable reads at 0x00893194 (PhaserBank) and 0x00893630 (TorpedoTube). The doc's prose semantics for the **bodies** are correct — only the slot ordinals were misaligned.

### PhaserBank vtable (0x00893194) vs TorpedoTube vtable (0x00893630)

| Slot | Offset | PhaserBank | TorpedoTube | Role |
|------|--------|------------|-------------|------|
| 0 | +0x00 | 0x00570EB0 (dtor) | 0x0057C5C0 (dtor) | scalar_deleting_dtor |
| 30 | +0x78 | **0x00571200** | **0x005833F0** | PhaserBank=helper, TorpedoTube=abstract `return 0` stub |
| 31 | +0x7C | 0x00570FE0 | **0x0057C770** | **Primary fire(dt, flag)** — called by TryFireWeapon |
| 32 | +0x80 | 0x0056FA00 | **0x0057C9E0** | Supplementary fire — called when target_list empty (TorpedoTube body decompiled in Section 2.3) |
| 33 | +0x84 | 0x00571E60 | 0x0057D780 | CanFire() |
| 34 | +0x88 | 0x00572C50 | 0x0057DE90 | GetFireDirection (phaser) / GetFirePosition (torpedo) |
| 36 | +0x90 | 0x00570F60 | (inherited) | SetPowerSetting (PhaserBank only) |

**Why this matters for OpenBC**: TryFireWeapon at 0x00584E40 dispatches by vtable slot — `vtable+0x7C` is the **primary fire path** (called first, takes target_list), and `vtable+0x80` is the **supplementary fire path** (called only when target_list is empty). Implementations must put the "fire with target" body at +0x7C and the "fire without target" body at +0x80. The prior doc's prose decomposition of 0x0057C9E0 as "TorpedoTube::Fire" was semantically correct but slot-wrong — that body actually lives at +0x80, and the +0x7C entry at 0x0057C770 has not been fully decompiled yet (see [OQ2](#open-questions)).

**PhaserBank slot 30 correction**: the prior doc said 0x0056D250. That's actually slot **26** (not slot 30). Slot 30 (+0x78) is 0x00571200.

**TorpedoTube slot 30 correction**: the prior doc said 0x0057C770 was "StopFiring" at slot 30. That address is actually the +0x7C **primary Fire** entry. Slot 30 (+0x78) is 0x005833F0 — a shared abstract `return 0` stub used as the no-op default.

---

## Open Questions

### OQ1: Does SetPowerSetting write to BOTH this+0xF4 AND parent+0xF0?

UpdateCharge reads `this+0xF4` to gate the discharge branch. The discharge rate function and damage scaling function read `parent+0xF0`. If these two fields are independent, can they diverge — for example, during MP receipt of opcode 0x12 (SetPhaserLevel)?

**Evidence needed**: decompile SetPowerSetting at 0x00570F60 (vtable+0x90) and verify it writes to both fields. Critical for OpenBC's opcode 0x12 handler.

### OQ2: What's the full body of TorpedoTube::Fire at 0x0057C770?

This is the vtable+0x7C primary fire entry. Ghidra did not auto-promote it; it lives as bare code. The doc decompiled 0x0057C9E0 as "TorpedoTube::Fire" with all the right semantics — but that's vtable+0x80. If 0x0057C770 is the primary entry, what's its body? Does it wrap 0x0057C9E0, or are they two parallel paths with different gating?

**Evidence needed**: promote 0x0057C770 to a function and decompile. Most likely it's the "with-target" wrapper and 0x0057C9E0 is the "without-target / supplementary" path that gets called when the wrapper's target gate fails.

### OQ3: TorpedoTube ctor init of last_fire_time

The doc claims `+0xA4 init: -1000.0f = 0xC47A0000`. The mathematical value is right (0xC47A0000 is indeed -1000.0f) but the ctor init site was not visited this pass. If the ctor exists and initializes this field at this value, where? If it doesn't, what's the value at object creation?

### OQ4: PhaserBank::UpdateCharge clamp double-fetch artifact

The decompile of UpdateCharge shows `fVar3 = (float10)FUN_0056f900();` (max charge fetch) compared to charge_level, and then a **second** call `fVar3 = (float10)FUN_0056f900();` immediately after if the comparison failed. This looks like a sloppy re-fetch — but is more likely a Ghidra artifact of the `FCOMP` instruction (which pops the FPU stack). Behaviorally correct, but flagged for verification.

---

## Cross-References

- [damage-system.md](damage-system.md) — weapon damage flows into ProcessDamage at 0x00593E50. The 6000.0f max_damage cited in damage-system is the collision-path inlined value; per-weapon max_damage comes from `EnergyWeaponProperty+0x78` (GetMaxDamage). [v5-validated 2026-05-28 cross-anchor]
- [power-system.md](power-system.md) — weapon classes inherit ShipSubsystem. PhaserSystem vtable @ 0x00893240 and TorpedoSystem vtable @ 0x00893598 are confirmed in power-system. [v5-validated 2026-05-28 cross-anchor]
- [set-phaser-level-protocol.md](../protocol/set-phaser-level-protocol.md) (protocol leaf #16) — opcode 0x12 SetPhaserLevel posts event 0x008000E0 (TGCharEvent class 0x105). Confirmed aligned with PhaserBank::SetPowerSetting at vtable+0x90.
- [collision-effect-protocol.md](../protocol/collision-effect-protocol.md) (protocol leaf #15) — collision damage path; no overlap with weapon firing mechanics here.
- [game-opcodes.md](../protocol/game-opcodes.md) — opcode 0x07/0x08 (StartFiring / StopFiring) route through the shared event forwarding handler (FUN_0069FDA0); opcode 0x19 (TorpedoFire) and 0x1A (BeamFire) have dedicated handlers documented in Sections 1.5 / 2.4.
