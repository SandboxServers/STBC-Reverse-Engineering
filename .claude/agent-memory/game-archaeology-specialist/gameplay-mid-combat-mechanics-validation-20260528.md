---
name: gameplay-mid-combat-mechanics-validation-20260528
description: Gameplay mid #7 — combat-mechanics-re.md consolidated combat doc validation. 482 lines, mostly anchored cross-references from validated foundation docs.
metadata:
  type: project
---

# Gameplay Mid #7 — combat-mechanics-re.md Validation (2026-05-28)

## Status

`validated` — consolidated doc whose Section 1-5 + 8 inherit from foundation docs already validated; Section 6 (Tractor Beam) and Section 7 (Ship Death) byte-confirmed fresh.

ZERO load-bearing wire/formula corrections found. The doc is the cleanest consolidation in the gameplay family.

## What this doc consolidates

| Section | Topic | Cross-anchor |
|---------|-------|--------------|
| §1 Damage Pipeline | Entry points, gates, formulas, AABB | [[gameplay-foundation-damage-system-validation-20260528]] |
| §2 Shield System | 6-facing, absorption, recharge | [[gameplay-foundation-shield-system-validation-20260528]] |
| §3 Cloaking | 4-state machine, shield/weapon interaction | binary-confirmed this session |
| §4 Weapon Systems | Phaser/torpedo/wire | [[gameplay-foundation-weapon-firing-validation-20260528]] |
| §5 Repair System | Queue, rate formula | repair-system.md (not in family list) |
| §6 Tractor Beam | NEW — modes, force formula, drag | byte-confirmed this session |
| §7 Ship Death | DestroyObject + Explosion | [[networking-leaf-ship-death-lifecycle-validation-20260528]] |
| §8 Sovereign Values | Hardpoint script reference | sovereign.py verified |

## Inheritance of corrections from foundation docs

The following foundation-doc corrections propagate into combat-mechanics-re.md but do NOT require fresh corrections here because this doc consolidates correctly:

- ZERO formula errors propagated. The damage formulas (collision raw, scale 0.1f mult+add, 0.5f cap, 6000.0f radius) all byte-confirmed via gameplay #1.
- Subsystem AABB claim is byte-confirmed at FUN_004bd9f0 (6-axis box-overlap test, NOT distance-based) — this REFUTES the OpenBC "50% overflow" claim section.
- Cloak state machine 0/2/3/5 active and 1/4 ghost — confirmed at FUN_0055e500 byte-by-byte.

## Fresh binary anchors (Sections 6+7)

### Tractor Beam (Section 6) — ALL byte-confirmed

- `FUN_00580f50` Tractor force formula at 0x00580f50, body 0x00580f50-0x00580fb7:
  - `distanceRatio = min(1.0, FUN_0056f940() / param_3)` — cap via `_DAT_0088b9c0=0.0f` threshold (when fVar4/fVar5 > 0)
  - `force = FUN_0056f930() * (fVar1 * fVar2) * distanceRatio` where fVar1 = `*(p1+0x24+0x34)` (system condition), fVar2 = `*(p1+0x34)` (projector condition)
  - Optional target scaling: if `*(p1+0x24+0xf0) != 0`, multiply by `FUN_0056c740()` (target condition)
  - Final: `* param_2` (deltaTime)
  - **Matches doc Section 6 force formula EXACTLY**

- `FUN_005822d0` TractorBeamSystem ratio at 0x005822d0:
  - `if (*(p1+0xf8) <= 0.0) return 0.0`
  - `return *(p1+0xfc) / *(p1+0xf8)` — `forceUsed/totalMaxDamage`
  - **+0xFC / +0xF8 confirmed (doc Section 6 claim).**

- `FUN_00561230` ImpulseEngine drag at 0x00561230:
  - Reads property+0x4C (effectiveSpeed)
  - Per-child-subsystem subtraction: `fVar2 = (1.0 - *(child+0x34)) * (fVar1 / iVar4)` (degradation)
  - If `*(p1+0xA8) != 0` (tractor system attached): `local_c *= (1.0 - FUN_005822d0_ratio)`
  - **Multiplicative drag CONFIRMED. ImpulseEngine+0xA8=TractorBeamSystem ptr confirmed.**
  - Returns `*(p1+0x90) * local_c`

- Vtable addresses: TractorBeamSystem 0x00893794 (slot 0 = 0x00582170 dtor; slot 1 = 0x005820c0); TractorBeamProjector 0x008936f0 (slot 0 = 0x0057ed80 dtor; slot 1 = 0x0057ecd0). Both EXIST at claimed addresses.

- Zero tractor mode handler calls DoDamage_0x00594020 — DoDamage has exactly 3 xrefs (FUN_005952d0, FUN_005af420, FUN_00593650), none from tractor mode handlers. **"Tractor does NOT apply direct damage" CONFIRMED via xref absence.**

### Ship Death (Section 7) — anchored to leaf #11

- Explosion handler 0x006A0080 confirmed:
  - Wire: `[0x29][object_id:i32][impact:cv4][damage:cf16][radius:cf16]` byte-confirmed via decompile (CompressedVector4_ReadVirtual + 2× CompressedFloat16_Decode)
  - Calls FUN_00593E50 (ProcessDamage) DIRECTLY, bypassing DoDamage — matches doc Section 1 claim
- DestroyObject handler 0x006A01E0 confirmed existing
- Both addresses verified in leaf #11 memo

## Already-validated cross-anchor spot-checks (re-confirmed)

- ApplyWeaponDamage at 0x005AF420 byte-confirmed: doubles `*(p1+0x4c)+*(p1+0x4c)`, halves `*(p1+0x54)*_DAT_008887a8` (0.5f confirmed). Weapon type gate `*(p1+0x2c)==0||==1` (phaser/torpedo). Matches doc Section 1.
- Damage notification gate FUN_00593F30 at `DAT_0097fa89 == '\0'` (IsHost==0) — CLIENT ONLY — matches doc Section 1.
- Subsystem handler dispatch FUN_004b1ff0: shield path via handler+0x20+0x18 (FUN_004b4b40), hull path via handler+0x1c+0x9 or +0x8 (FUN_004bd9f0). Byte-confirmed.
- FUN_004bd9f0 AABB overlap (6-axis box test, NOT Euclidean distance) — byte-confirmed:
  - `*(p1+0x14) <= p2[0xb]` AND `p2[8] <= *(p1+0x20)` (X axis)
  - `*(p1+0x18) <= p2[0xc]` AND `p2[9] <= *(p1+0x24)` (Y axis)
  - `*(p1+0x1c) <= p2[0xd]` AND `p2[10] <= *(p1+0x28)` (Z axis)
  - Six conditions, all-AND. **No distance computation, no 50% split — doc claim CONFIRMED.**
- IsCloaked FUN_005AC450 reads ship+0x2DC (cloak subsystem), returns `*(+0xAC) == 1` — confirms doc Section 3 layout.
- SetAmmoType FUN_0057B230: when param_3 (immediate flag) != 0, reload loop SKIPPED; when == 0, reload runs. Matches doc semantics: `immediate=1` (MP) → unload+no-reload → effective lockout = ReloadDelay; `immediate=0` (local) → unload+reload immediately.
- ReloadTorpedo FUN_0057D8A0: increments +0xA0 num_ready, finds slot with LARGEST timer in +0xAC array, sets to -1.0f (0xBF800000). Confirms doc Section 4.

## Sovereign hardpoint values (Section 8) — VERIFIED against reference/scripts/ships/Hardpoints/sovereign.py

All values match EXACTLY:
- Hull 12,000 ✓ (line 515)
- ShieldGenerator 10,000, RepairComplexity 2.0 (doc says "—" — Clar)
- Shield facings 11000/5500/11000/11000/5500/5500 ✓ (lines 542-547)
- SensorArray 8000 ✓, WarpCore 7000 ✓, ImpulseEngines 3000 ✓, Torpedoes 6000 ✓
- ForwardTorpedo1-4 + AftTorpedo1-2 all 2200 ✓
- PortImpulse/StarImpulse 3000 ea ✓, PortWarp/StarWarp 4500 ea ✓
- Repair 8000 / MaxRepairPoints=50 / NumRepairTeams=3 ✓ (lines 874-885)
- Phasers controller 8000 ✓, Tractors 3000 ✓, WarpEngines 8000 ✓, Bridge 10000 ✓
- Per-phaser MaxCondition 1000, MaxCharge 5.0, MaxDamage 300.0, MaxDamageDistance 70.0, MinFiringCharge 3.0, RechargeRate 0.08 ✓ (all 8 phasers match Section 4 table)
- Per-tractor MaxCondition 1500, MaxCharge 5.0, MaxDamage 80, MaxDamageDistance 114, MinFiringCharge 3.0 ✓ (lines 1020-1023)
- Forward tractors RechargeRate=0.5, Aft tractors RechargeRate=0.3 ✓ (lines 1025, 1262)

## Triage

### C — Corrections (material)

NONE. Zero formula, wire, or address errors. This is the cleanest gameplay-family doc validated.

### Clar — Clarifications (non-load-bearing)

- **Clar 1** (LOW, Section 8 table): "Shield Generator | 10,000 | —" — RepairComplexity is actually 2.0 (sovereign.py:534), not "—". Cosmetic table omission.
- **Clar 2** (LOW, Section 3 globals): doc mentions "CloakTime (transition duration, class-level global)" without value. Actual value at 0x008e4e1c = 5.0f. Adding "5.0s default" would symmetrize the ShieldDelay row.

### R — Re-anchors (foundation propagation)

- Section 1 DAT_00893f28 (0.1f mult) — anchor to gameplay-foundation-damage-system-validation memo.
- Section 1 DAT_0088bf28 (0.1f add) — same.
- Section 1 DAT_008887a8 (0.5f weapon radius scale) — re-byte-confirmed this session.
- Section 1 0x45BB8000 (6000.0f radius) — same anchor.
- Section 2 DAT_0088bacc (1/6 area split) — re-byte-confirmed this session.
- Section 6 _DAT_00888860 (1.0f drag baseline) — byte-confirmed this session (also used in FUN_00561230).
- Section 6 _DAT_0088b9c0 (0.0f distance threshold) — byte-confirmed this session.
- Section 6 _DAT_00888b54 (0.0f null/threshold) — cross-anchored to gameplay #4 memo (same constant).

### OQ — Open Questions

- **OQ 1**: Section 3 says "shields re-enable after another ShieldDelay delay" on decloak — not directly verified. The decloak end function CloakDisengageRestoreShield exists at the implied address but its timing was not re-validated this session.
- **OQ 2**: Section 6 enumeration of 6 tractor modes (HOLD/TOW/PULL/PUSH/DOCK_STAGE_1/DOCK_STAGE_2) is not byte-validated from a switch table this session. Doc says "All five mode handlers (HOLD, TOW, PULL, PUSH, DOCK_STAGE_2) only manipulate target velocity" — the mode enumeration source is not anchored.
- **OQ 3**: Section 4 phaser intensity discharge constants DAT_0089317C/80/84 not byte-confirmed this session (cross-anchor to gameplay #5 memo).

### H — Historical

NONE. All sections remain current.

## Header inputs for documentation-writer

- `validated: 2026-05-28`
- status: `validated`
- binary: STBC.exe, image_base=0x00400000, size=6394712
- companions: damage-system.md, shield-system.md, cloaking-state-machine.md, weapon-firing-mechanics.md, repair-system.md, repair-tractor-analysis.md, ship-death-lifecycle.md
- 23 unique addresses anchored (function entries + globals)
- 0 corrections, 2 clarifications

## Cross-doc tension

None observed. Section 7's claim "Server sends DestroyObject (0x14) then Explosion (0x29)" matches networking-leaf-ship-death-lifecycle which notes 0x14 absent in pure combat traces (Python-side suppression) but doc Section 7 is describing the FULL pipeline, which is correct for non-combat paths.
