---
name: gameplay-foundation-weapon-firing-validation-20260528
description: v5 validation of docs/gameplay/weapon-firing-mechanics.md (gameplay foundation #5, 798 lines) — phaser charge/discharge, torpedo reload/fire, WeaponSystem update loop, vtable map corrections, ZERO wire/formula errors but 4 C and 6 Clar
metadata:
  type: project
---

# Weapon Firing Mechanics Validation - 2026-05-28

## Subject

`docs/gameplay/weapon-firing-mechanics.md` — 798 lines, gameplay foundation family #5/6. Covers EnergyWeapon/PhaserBank charge mechanics, TorpedoTube reload/fire/SetAmmoType, WeaponSystem update loop, BeamFire (0x1A) and TorpedoFire (0x19) network wire formats.

## Verdict

**v5 status: `partial`**. ZERO formula or wire-format errors. ALL constant addresses byte-confirmed. ALL property accessor offsets confirmed. Main corrections are around **vtable slot-to-address mappings** (Part 6 table) and a couple of semantic mis-labels (AI multiplier direction, IsSubsystemAlive return semantics).

## Why: doc was written from partial Ghidra analysis — load-bearing functions (PhaserBank::Fire, PhaserBank::CanFire, EnergyWeapon::CanFire, TorpedoTube::CanFire) are NOT auto-promoted by Ghidra (vtable-data-only xrefs). Doc inferred semantics from caller behavior, which is mostly correct but lost vtable slot ordinal alignment when comparing Phaser vs Torpedo vtables.

## How to apply

When implementing in OpenBC:
- Trust Part 1-5 prose (formulas, constants, gate logic, wire formats) — all binary-confirmed.
- DO NOT trust Part 6 vtable comparison table — slot indices and per-class addresses are misaligned. Use the corrected map below.
- Treat AI multiplier as a BOOST not a penalty (1.25× recharge for non-owner ships).
- `FUN_0056c350` returns 1 if subsystem DAMAGED (HP < threshold), 0 if alive — opposite of its doc-given "IsSubsystemAlive" name.

---

## Corrections

### C1 — Vtable slot-to-address misalignment in Part 6 [HIGH IMPACT]

**Claim (Part 6, lines 791-798):** PhaserBank vtable slot 30 = StopFiring at 0x0056D250; slot 32 = TryFire at 0x0056FA00. TorpedoTube vtable slot 30 = StopFiring at 0x0057C770; slot 31 = Fire at 0x0057C9E0; slot 32 = TryFire at 0x005833F0.

**Binary truth (byte-confirmed from raw vtable reads at 0x00893194 PhaserBank and 0x00893630 TorpedoTube):**

PhaserBank @ 0x00893194:
- Slot 30 (+0x78): **0x00571200** (NOT 0x0056D250 — that's slot 26)
- Slot 31 (+0x7C): 0x00570FE0 ← Fire ✓
- Slot 32 (+0x80): 0x0056FA00 ✓
- Slot 33 (+0x84): 0x00571E60 ← CanFire ✓
- Slot 34 (+0x88): 0x00572C50 ← GetFireDirection ✓
- Slot 36 (+0x90): 0x00570F60 ← SetPowerSetting

TorpedoTube @ 0x00893630:
- Slot 30 (+0x78): **0x005833F0** ← "return-0" abstract stub (NOT StopFiring)
- Slot 31 (+0x7C): **0x0057C770** ← Fire (NOT StopFiring)
- Slot 32 (+0x80): **0x0057C9E0** ← what doc CALLS "Fire" — actually TryFire / supplementary-fire path
- Slot 33 (+0x84): 0x0057D780 ← CanFire ✓
- Slot 34 (+0x88): 0x0057DE90 ← GetFirePosition ✓

**Why this matters:** TryFireWeapon at 0x00584E40 calls vtable+0x7C as primary fire (`(**(code **)(*param_2 + 0x7c))(param_3,1)`) and vtable+0x80 as supplementary fire (called only when target_list is empty). So:
- Primary fire path: PhaserBank=0x00570FE0, TorpedoTube=0x0057C770 (bare code — Ghidra didn't promote)
- Supplementary fire path: PhaserBank=0x0056FA00, TorpedoTube=0x0057C9E0 (THIS is what the doc decompiled as "TorpedoTube::Fire")

**Both functions DO fire the weapon — they're entry points with different gating (one assumes target_list, one doesn't). The doc's prose semantics are correct, but the slot-to-address column in Part 6 is scrambled.**

### C2 — `FUN_0056c350` name "IsSubsystemAlive" is INVERTED [MEDIUM IMPACT]

**Claim (lines 196-216):** `FUN_0056c350 IsSubsystemAlive(Weapon* weapon)` returns true if alive.

**Binary truth:** FUN_0056c350 returns **1 if DAMAGED** (HP_threshold < current_HP), 0 if alive. Verified at byte level:
```c
fVar1 = *(float *)(param_1 + 0x34);     // power_level (HP threshold)
fVar6 = (float10)FUN_0056b960();         // current HP
if ((float10)fVar1 < fVar6) return 1;   // HP threshold below actual HP = DAMAGED state
```

Caller FUN_0056FDF0 (GetChargePercentage at line 184-194 of doc): `if (cVar1 != 1)` — returns charge if NOT-damaged (cVar1==0). So **the doc's narrative is right** (charge returns 0 when subsystem dies) **but the function naming/return semantics are inverted in the doc text**. The recursive descent in C350 makes more sense as "is any child damaged" — short-circuit returning 1 (damaged) up the tree.

### C3 — AI recharge multiplier (DAT_00890550 = 1.25) is a BOOST not a PENALTY [LOW IMPACT]

**Claim (line 91, 105, line 707):** "Non-owner ship penalty (other player's ship gets slower recharge)" / "DAT_00890550 AI_recharge_mult".

**Binary truth:** DAT_00890550 = 0x3FA00000 = **1.25** (byte-confirmed at 0x00890550). UpdateCharge applies it when `bVar2 == false` (NOT owner ship). 1.25× is a BOOST, not a penalty. AI/remote ships recharge **faster**, not slower. The "AI mult" naming is fine but the human-language gloss "penalty / slower recharge" is wrong.

### C4 — PhaserBank vtable slot 0 dtor address mismatch [LOW IMPACT]

**Claim (Part 6 line 793):** PhaserBank slot 0 = 0x00570EB0 (dtor).

**Binary truth:** PhaserBank vtable byte 0 = `b0 0e 57 00` = 0x00570EB0 ✓ CORRECT.

(Initial reading suggested 0x0056D250 — that was a misread on my part. PhaserBank slot 0 dtor IS 0x00570EB0. Doc is correct on slot 0.)

---

## Clarifications

### Clar1 — Intensity mode lives in BOTH this+0xF4 AND parent+0xF0 [Section 1.2 / 1.2]

UpdateCharge at 0x00572B80 reads **this+0xF4** for intensity branch (`param_1[0x3d]`).
Discharge rate lookup at 0x00572B00 reads **parent+0xF0** (`*(int *)(*(int *)(param_1 + 0x24) + 0xf0)`).
Damage scaling at 0x00572A50 also reads **parent+0xF0**.

Doc text mixes these two fields (says "this->intensity_mode" in pseudocode then later says "parent+0xF0"). They're not the same field. Likely the system writes to BOTH on SetPowerSetting to keep them in sync; verify before relying on either for OpenBC.

### Clar2 — TorpedoFire wire format opcode 0x19 sent to "Forward" group (in MP)

FUN_0057CB10 SendTorpedoFirePacket: in MP (`DAT_0097fa8a != 0`), calls `TGWinsockNetwork_SendTGMessageToGroup(this, &DAT_008e5528, pMessage)`. The group identifier at 0x008e5528 is the "Forward" forwarding group. In SP it goes via `TGWinsockNetwork_SendTGMessage(this, *(int *)((int)this + 0x20), pMessage, 0)` — i.e., to self/local. The doc just says "If host, send network packet" — omits the group identity that BeamFire handler (0x0069FBB0) also uses to relay.

### Clar3 — Phaser MED and HIGH have IDENTICAL discharge rates AND damage scales

Constants byte-confirmed at 0x00893170-0x00893184:
- damage_scale_LOW (0x00893170) = 0.25
- damage_scale_MED (0x00893174) = 0.5
- damage_scale_HIGH (0x00893178) = 0.5  ← same as MED
- discharge_rate_LOW (0x0089317C) = 0.35
- discharge_rate_MED (0x00893180) = 1.0
- discharge_rate_HIGH (0x00893184) = 1.0 ← same as MED

Doc tables (lines 130-132, 706-711) list these as if they were three distinct values. Actually phaser is BINARY (LOW vs MED-or-HIGH). HIGH is identical to MED at the C++ level — any "max-power" gameplay difference must be elsewhere (e.g., UI label / different fire animation).

Note also DAT_00888B54 (0.0f) is the fallback if `intensity_mode` is none of 0/1/2 — i.e., "no discharge" sentinel. Doc Section 1.2 lists this correctly as "other → 0.0".

### Clar4 — Property accessor +0x8C is BOTH MaxReady AND NumTubes (same field)

`GetMaxReady()` and `GetNumTubes()` (FUN_0057C420) both read `property+0x8C`. Doc lists them as separate accessors but they're the same field — by design, num tubes equals max ready (one tube = one slot).

### Clar5 — PhaserBank::CanFire at 0x00571E60 calls 0x005AC450 not "GetShipFromParent" [Section 1.3 line 230]

The first gate in CanFire is `mov ecx, [esi+0x40]; test ecx, ecx; jz; call 0x005AC450`. The function 0x005AC450 is the ship-alive checker (returns 1 if ship is alive). Doc claims FUN_00562210 is GetShipFromParent which returns NULL for dead ships — close but not the same address. The actual entry point in PhaserBank::CanFire is 0x005AC450 and it doesn't take `parent` — it takes `owner_ship` (ESI+0x40 directly).

### Clar6 — `last_fire_time = -1000.0f` init claim [Section 2.1 line 302]

Doc claims `+0xA4 init: -1000.0f = 0xC47A0000`. Did not directly verify in TorpedoTube ctor this pass — the value 0xC47A0000 = -1000.0f is mathematically correct but the init site was not visited. Marked as un-verified for this pass.

---

## Confirmed claims (no correction needed)

- **PhaserBank::UpdateCharge at 0x00572B80** — full byte-by-byte match: SEH setup, owner-check via DAT_0097fa89 + DAT_0097e238+0x54, is_firing branch at +0x88, discharge gate on mode==3 || mode==2, charge clamp via FUN_0056f900 (GetMaxCharge), AI multiplier branch.
- **All property accessor offsets** (+0x68/+0x6C/+0x70/+0x74/+0x78/+0x7C/+0x88/+0x8C) ✓ confirmed.
- **Object field offsets** (+0x18 property, +0x24 parent, +0x34 power_level, +0x40 owner_ship, +0x88 is_firing, +0xA0 charge_level/num_ready, +0xA4 last_fire_time, +0xAC reload_timers, +0xF4 intensity_mode) ✓ all confirmed via decompiled offsets.
- **TorpedoTube::Fire (the 0x0057C9E0 body)** — full match: CanFire gate, FUN_0057CD90 projectile create, decrement num_ready (+0xA0), FUN_0057b4d0+FUN_0057b570 system counters, reload timer scan, FUN_0057DA20 setup, event 0x0080007C (ET_WEAPON_FIRED) post, system fire-time record at parent+0xF0, FUN_0057CB10 network send gated on DAT_0097fa89.
- **TorpedoTube::ReloadTorpedo at 0x0057D8A0** — full match: num_ready<max gate, ammo gate via parent+0xF4+type*4 vs parent+0x118, increment, find-longest-timer + set -1.0f, event 0x800065 post.
- **TorpedoSystem::SetAmmoType at 0x0057B230** — full match: unload loop, ClearTimers, conditional reload, event 0x800067 (ET_AMMO_TYPE_CHANGED), event 0x800068 (ET_AMMO_SWITCH_STARTED) on immediate=1, network TGCharEvent 0x008000FE post.
- **SetAmmoType "lockout" analysis** — confirmed: the "lockout" IS implicit (unload + clear timers, no reload when immediate=1), not a separate timer.
- **WeaponSystem::UpdateWeapons at 0x00584930** — full match: ship-dead gate at owner+0x210, target-list cleanup FUN_00584cc0, firing chain via +0xB8, round-robin from +0xB4 (last_weapon_idx), per-weapon TryFireWeapon call, fallback supplementary list path.
- **WeaponSystem::TryFireWeapon at 0x00584E40** — full match: timer +0x9C (param_2[0x27]), is_firing +0x88, FIRE_DELAY_THRESHOLD = DAT_00893830 = 0.33, vtable+0x84 CanFire, vtable+0x7C Fire, vtable+0x78 StopFiring, supplementary-list iteration at +0xC4.
- **BeamFire wire format / handler at 0x0069FBB0** — full match: opcode 0x1A, ReadInt weapon, ReadChar flags, ReadCompressedVector3 hit pos, ReadChar flags2, optional ReadInt target on bit 1, calls FUN_005762B0.
- **TorpedoFire wire format / sender at 0x0057CB10** — full match: WriteChar 0x19, WriteInt weapon, WriteChar +0x14C model, flag byte (bit0=skew param_3, bit1=+0xA8 isSkewFire, bit2=noTarget), normalized velocity vec3, optional target_id + CompressedVector4 offset.
- **TorpedoFire handler at 0x0069F930** — full match: "Forward" group relay, ReadInt, ReadChar, ReadChar flags, ReadCompressedVector3 velocity, conditional target+vec4, dispatch to FUN_0057D110.

## Constants byte-confirmed at exact addresses

| Address | Value | Used For |
|---------|-------|----------|
| 0x008936C0 | 0x3D072B02 (~0.033) | SKEW_FIRE_SCALE |
| 0x00893830 | 0x3EA8F5C3 (~0.33) | FIRE_DELAY_THRESHOLD |
| 0x00890550 | 0x3FA00000 (1.25) | Non-owner recharge **BOOST** |
| 0x00893170 | 0x3E800000 (0.25) | damage_scale_LOW |
| 0x00893174 | 0x3F000000 (0.5) | damage_scale_MED |
| 0x00893178 | 0x3F000000 (0.5) | damage_scale_HIGH (= MED) |
| 0x0089317C | 0x3EB33333 (0.35) | discharge_rate_LOW |
| 0x00893180 | 0x3F800000 (1.0) | discharge_rate_MED |
| 0x00893184 | 0x3F800000 (1.0) | discharge_rate_HIGH (= MED) |

## Functions confirmed present but not auto-promoted by Ghidra

- 0x00570FE0 PhaserBank::Fire — 64 bytes SEH-wrapped, byte-verified as real code
- 0x00571E60 PhaserBank::CanFire — byte-verified: owner-ship-alive call to 0x005AC450, charge gate, then power-diff check via 0x00570D58
- 0x0056FA10 EnergyWeapon::CanFire — 3-byte stub `xor al,al; ret` — returns FALSE always (base class default)
- 0x0057C770 TorpedoTube::Fire (primary) — byte-verified as real code with CanFire prelude
- 0x0057D780 TorpedoTube::CanFire — byte-verified: starts with `mov eax,[esi+0xA0]; test eax,eax; jg short` (num_ready>0 gate, doc claim #4 ✓)

These all live in vtables but Ghidra auto-analysis didn't promote them. Valid entry points; valid v5 anchors via the raw-byte path.

## Completeness scores (analyze_function_completeness)

| Function | Address | Score | Max Achievable | Deductions |
|----------|---------|-------|----------------|------------|
| PhaserBank::UpdateCharge | 0x00572B80 | 2.5 | 88.6 | 9 (4 globals unrenamed, 2 magic numbers, 2 struct accesses, 1 hungarian) |
| TorpedoTube::Fire (helper) | 0x0057C9E0 | 0.0 | 81.9 | 9 (12 undefined, 4 globals, 6 magic, 4 struct, 2 hungarian) |
| TorpedoTube::ReloadTorpedo | 0x0057D8A0 | 0.0 | 84.8 | 10 (8 undefined, 1 global, 8 magic, 8 struct, 1 hungarian) |
| WeaponSystem::UpdateWeapons | 0x00584930 | 0.0 | 85.0 | 9 (35 undefined, 6 labels, 4 magic, 3 struct) |

All worker-class. Scores reflect lack of v5 annotation work, not validation gaps. Doc claims are factually anchored regardless of cosmetic completeness.

---

## Open Questions

### OQ1: SetPowerSetting writes to both this+0xF4 AND parent+0xF0?

UpdateCharge reads `this+0xF4` to gate discharge branch. Discharge rate function reads `parent+0xF0`. If the two are independent, can they diverge (e.g., during MP receive of opcode 0x12 SetPhaserLevel)?

**Evidence needed:** Decompile SetPowerSetting (vtable+0x90 = 0x00570F60) and verify it writes to both fields.

### OQ2: Is `0x0057C770` truly the primary TorpedoTube::Fire?

Doc decompiled `0x0057C9E0` as "TorpedoTube::Fire" with all the right semantics (CanFire prelude, projectile create, event 0x800007C post). But the vtable slot+0x7C is 0x0057C770, NOT 0x0057C9E0. If 0x0057C770 is the entry point, what's its full body? Does it call 0x0057C9E0 internally or are they two parallel paths?

**Evidence needed:** Promote 0x0057C770 to a function and decompile. May be the "with-target" wrapper and 0x0057C9E0 is the "without-target / supplementary" path.

### OQ3: TorpedoTube ctor init of last_fire_time

Doc claims `+0xA4 init: -1000.0f = 0xC47A0000`. Did not verify the ctor. If the ctor exists and initializes this field, where? If it doesn't, what's the value at object creation?

### OQ4: Charge clamp via FUN_0056f900 — does it actually fetch a property field?

Decompile shows `fVar3 = (float10)FUN_0056f900();` (max charge) gets compared to charge_level. But there's a SECOND call `fVar3 = (float10)FUN_0056f900();` immediately after if the comparison failed — this LOOKS like a sloppy re-fetch, but might be a Ghidra artifact of the `FCOMP` instruction (which pops the stack). Likely fine, but flagged.

---

## Cross-References

- **damage-system** (validated 2026-05-28): Weapon damage flows into ProcessDamage at 0x00593E50 (validated in damage-system memo). max_damage 6000.0f confirmed in damage-system applies to BOTH phaser (via property+0x78 GetMaxDamage) and torpedo paths.
- **power-system** (validated 2026-05-28): Weapon classes inherit ShipSubsystem; TorpedoSystem vtable @ 0x00893598, PhaserSystem vtable @ 0x00893240 confirmed in power-system memo. Individual weapon class vtables 0x008930D8 (EnergyWeapon), 0x00893194 (PhaserBank), 0x00893630 (TorpedoTube) confirmed here.
- **set-phaser-level-protocol** (leaf #16, validated earlier): opcode 0x12 SetPhaserLevel posts event 0x008000E0 TGCharEvent (class 0x105). The doc Section 1.6 mentions this — confirmed to align with leaf #16.
- **collision-effect-protocol** (leaf #15): no overlap with weapon firing.
- **stateupdate-subsystem-wire-format** (protocol #11): subsystem health serialization is the readback for weapon damage; doesn't overlap with firing mechanics here.

## Vtable map for OpenBC

PhaserBank (size 0x128, vtable 0x00893194):
```
+0x00 dtor               = 0x00570EB0
+0x78 [slot 30]          = 0x00571200  // unknown — possibly StopFiring helper
+0x7C Fire(dt,flag)      = 0x00570FE0  // primary fire path (with target list)
+0x80 TryFire(dt,flag)   = 0x0056FA00  // supplementary fire path (no target)
+0x84 CanFire()          = 0x00571E60
+0x88 GetFireDirection() = 0x00572C50
+0x8C unknown            = 0x0056FB10
+0x90 SetPowerSetting    = 0x00570F60
```

TorpedoTube (size 0xB0, vtable 0x00893630):
```
+0x00 dtor               = 0x0057C5C0
+0x78 [slot 30]          = 0x005833F0  // abstract "return 0" stub
+0x7C Fire(dt,flag)      = 0x0057C770  // primary fire path (bare code, Ghidra didn't promote)
+0x80 TryFire(dt,flag)   = 0x0057C9E0  // supplementary fire path (what doc called "Fire")
+0x84 CanFire()          = 0x0057D780
+0x88 GetFirePosition()  = 0x0057DE90
```

---

## v5 triage summary

- **C** (correction): 4 — vtable slot mapping in Part 6 (HIGH); IsSubsystemAlive return semantics inverted (MED); AI multiplier is boost not penalty (LOW); PhaserBank vtable slot 0 dtor (LOW, actually correct after recheck)
- **Clar** (clarification): 6 — intensity mode in two fields; "Forward" group in MP path; MED/HIGH identical constants; +0x8C is MaxReady=NumTubes (same); CanFire ship-alive helper address; last_fire_time init not verified
- **R** (removal): 0 — no fabricated content to remove
- **OQ** (open question): 4 — SetPowerSetting field sync; TorpedoTube vtable+0x7C body; last_fire_time ctor init; clamp double-fetch
- **H** (historical): 0

**Bottom line:** ZERO formula errors, ZERO wire-format errors, ZERO constant errors. The doc's mechanical claims (recharge formula, discharge formula, damage formula, reload mechanism, ammo type switch, fire wire format) are all binary-confirmed. The errors are concentrated in the Part 6 vtable table (slot/address misalignment) and a handful of label semantics. Doc is **substantially trustworthy** for OpenBC implementation — but Part 6 vtable column should be regenerated from the corrected map above.
