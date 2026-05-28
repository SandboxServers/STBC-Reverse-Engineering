---
name: subsystem-integrity-hash-validation-20260528
description: Validation memo for docs/protocol/subsystem-integrity-hash.md (leaf #19, anti-cheat dead-code analysis) — verdict partial, 6-row slot identity correction
metadata:
  type: project
date: 2026-05-28
---

# subsystem-integrity-hash.md — v5 Evidence Packet (Leaf #19)

## Overview status

**partial** — wire format, hash algorithm, sender/receiver gates, kick path, and all 6 boolean sentinel magic constants byte-by-byte CONFIRMED. ONE material correction: 6 of 12 slot subsystem-identity labels in the doc's slot table are stale pre-correction names; they must be updated to match foundation #1 (wire-format-spec.md) corrected ship-slot table. Hash function reads CORRECT offsets — only the human-readable identity column is wrong.

Recommend re-render to `status: partial` with correction notes; promote to `verified` once slot identities are updated.

## Confirmed claims

### Function existence and addresses (7/7)
- **0x005b6c10** HashFoldFloat — exists, renamed; body 005b6c10..005b6c94. Decompile matches doc: __ftol abs-int + per-byte XOR + ROL by 1.
- **0x005b6170** HashBaseSubsystem — exists, renamed; 11+ HashFoldFloat calls in exact doc order.
- **0x005b5eb0** ComputeSubsystemIntegrityHash — exists, renamed; 12 slots in doc-stated order (+0x48, +0x44, +0x34, +0x4C, +0x50, +0x54, +0x5C, +0x60, +0x38, +0x3C, +0x40, +0x58) all match decompile.
- **0x005b6330** HashWeaponSystem — exists, renamed; step 1-4 sequence matches doc.
- **0x005b6560** HashIndividualWeapon — exists, renamed.
- **0x005b17f0** Ship__WriteStateUpdate (sender) — exists, already named.
- **0x005b21c0** Ship__ReadStateUpdate (receiver) — exists, already named.

### Sender (Ship__WriteStateUpdate disasm 0x005b1d96..0x005b1dc1)
```
005b1d96  TEST BL,BL                  ; BL = bVar19 (set at 005b1906 when CL=DAT_0097fa8a is 0)
005b1d98  JZ 0x005b1dc3               ; if BL=0 (MP), branch to push 0
005b1d9a  PUSH 0x1                    ; has_hash = 1 (SP branch)
005b1d9c  CALL 0x006cf770             ; WriteBit (confirmed via stream-primitives.md)
005b1da5  LEA ECX,[ESI + 0x27c]       ; container = ship+0x27C
005b1dab  CALL 0x005b5eb0             ; ComputeSubsystemIntegrityHash __fastcall via ECX
005b1db0  MOV EDX,EAX
005b1db6  SAR EDX,0x10                ; EDX = hash >> 16 (signed)
005b1db9  XOR EAX,EDX                 ; low 16 bits = (low 16) XOR (high 16)
005b1dbb  PUSH EAX
005b1dbc  CALL 0x006cf7f0             ; WriteShort (low 16 bits only)
005b1dc3  PUSH 0x0                    ; MP branch: has_hash = 0
005b1dc5  CALL 0x006cf770             ; WriteBit
```
Wire encoding `(hash >> 16) ^ (hash & 0xFFFF)` CONFIRMED. Gate is `!isMultiplayer` — hash only emitted in SP.

### Receiver (Ship__ReadStateUpdate decompile + disasm 0x005b22ff..0x005b232c)
```
005b2311  MOV dword ptr [EDI + 0x10], 0x8000f6   ; event_type = ET_BOOT_PLAYER as IMMEDIATE 32-bit constant
005b2318  CALL 0x006d62b0                          ; set event src/dest
005b231d  MOV EAX, dword ptr [ESI + 0x2e4]         ; this->playerSlot
005b2323  PUSH EDI                                  ; push event
005b2324  MOV ECX, 0x97f838                         ; ECX = &DAT_0097f838 (TGEventManager singleton)
005b2329  MOV dword ptr [EDI + 0x28], EAX          ; event+0x28 = playerSlot
005b232c  CALL 0x006da2a0                          ; TGEventManager__PostEvent
```
Hash mismatch path byte-by-byte matches doc except: doc writes `event->eventType = 0x8000F6` (correct value, no offset shown); binary writes 0x8000F6 IMMEDIATELY into event+0x10. Doc claim is functionally accurate — see clarification Clar-1 below.

### Kick path target
**0x00506170** = MultiplayerWindow_BootPlayerHandler — was undefined in Ghidra DB, CREATED this pass. Binary signatures:
- Entry: `MOV AL, [0x0097fa8a]` (reads isMultiplayer gate)
- Allocates 0x44 bytes for TGBootPlayerMessage (PUSH 0x44 at 005061A0; ctor chain FUN_00717b70 → FUN_00718010 → FUN_006bac70)
- Sets `[ESI+0x40] = 0x4` at 0x005061CD (reason=4 = BOOT_REASON_INTEGRITY)
- Cross-confirmed: 04_ui_windows.c line 2027 registers this with name string `MultiplayerWindow__BootPlayerHandler` keyed on `&DAT_008000f6`

### Boolean sentinel magic constants (6/6, byte-exact)

| # | Source | True (hex) | True (float) | False (hex) | False (float) | Verified at |
|---|--------|-----------|--------------|-------------|---------------|-------------|
| 1 | property+0x24 | 0x42800083 | 64.0002f | 0x42993333 | 76.6f | FUN_005b6170 |
| 2 | subsys+0x44 | 0x42c53333 | 98.6f | 0x42c80000 | 100.0f | FUN_005b6170 |
| 3 | property+0x25 | 0x4164cccd | 14.3f | 0x43e40ccd | 456.1f | FUN_005b6170 |
| 4 | property+0x26 | 0x41da6666 | 27.3f | 0x4180cccd | 16.1f | FUN_005b6170 |
| 5 | wsProp+0x50 | 0x3ecccccd | 0.4f | 0x42c63333 | 99.1f | FUN_005b6330 |
| 6 | wsProp+0x51 | 0x42026666 | 32.6f | 0x43f38ccd | 487.1f | FUN_005b6330 |

All match doc table lines 261-272 byte-for-byte.

### Hash function call site
Receiver: `if ((DAT_0097fa8a != '\\0') && (uComputedHash = FUN_005b5eb0(), ...))` — gate is `isMultiplayer == 1` (mirror of sender). Mutually exclusive with sender gate → dead code confirmed.

### Sender PatchSubsystemHashCheck
0x005b22b5 — known existing binary patch at src/proxy/ddraw_main/binary_patches_and_python_bridge.inc.c. Confirmed safe: stock gameplay never reaches the hash mismatch path (sender emits has_hash=0 in MP).

### TGFactory usage
Receiver does NOT use TGFactory_DeserializeObject. It uses:
- FUN_00717b70(0x2C) — TGAlloc 44 bytes
- FUN_00718010 — TGAlloc ctor
- FUN_006bb840 — TGEvent ctor
- FUN_006d62b0 — TGEvent::SetSrcDest
- FUN_006da2a0 — TGEventManager__PostEvent

This is **raw TGEvent allocation + post**, NOT factory-wire-deserialization (as expected for SEND-SIDE event posting). Matches leaf #18 pattern where command/control messages bypass TGFactory.

## Per-correction triage

### C1 — Slot subsystem-identity column (6 of 12 rows wrong)

**Severity**: material (mislabels subsystem class on 6 hash slots) but does NOT affect wire format or hash algorithm — only the human-readable identity column. The hash function reads CORRECT offsets; the doc's offset math is internally consistent. Only the "what is at that offset" labels are stale pre-correction names.

**Root cause**: Doc was written BEFORE foundation #1 corrected the ship-slot table on 2026-05-28. Foundation #1 corrections (wire-format-spec.md C1) added ship+0x2C0 ShieldGenerator (already in this doc) but ALSO corrected ship+0x2C4 (was PowerSubsystem reactor → now HullSubsystem) and added ship+0x2C8 SensorSubsystem + ship+0x2DC CloakDevice. The reactor moved to ship+0x2B0.

**Key archaeological finding**: `ship+0x27C` is a SUB-OBJECT constructor at FUN_005b5d00 with its own vtable at 0x008944c8. The ctor zero-fills offsets [+0x04, +0x60] (param_1[1..0x18]) which **overlap arithmetically** with the named-slot table at ship+0x2B0..0x2DC. So `container+N == ship+0x27C+N`, and after Ship__SetupProperties populates the named-slot table, the hash function reads those same pointers through the container alias. This confirms the container-offset → ship-offset arithmetic in the doc IS correct — only the named-identity column needs correction.

**Reconciliation table** (binary truth from foundation #1 + decompile of FUN_005b5eb0):

| Hash Order | Container Offset | Ship Offset | Doc Says | Foundation #1 (CORRECTED) | Verdict |
|---|---|---|---|---|---|
| 1 | +0x48 | +0x2C4 | Power Reactor | **HullSubsystem** (CT_HULL_PROPERTY 0x8138) | CORRECTION |
| 2 | +0x44 | +0x2C0 | Shield Generator | ShieldGenerator (CT_SHIELD_PROPERTY 0x8137) | OK |
| 3 | +0x34 | +0x2B0 | Powered Master | **PowerSubsystem (reactor/EPS)** (CT_POWER_PROPERTY 0x813E) | rename only (legacy name) |
| 4 | +0x4C | +0x2C8 | Cloak Device | **SensorSubsystem** (CT_SENSOR_PROPERTY 0x8139) | CORRECTION |
| 5 | +0x50 | +0x2CC | Impulse Engine | ImpulseEngineSubsystem (CT_IMPULSE_ENGINE_PROPERTY 0x813C) | OK |
| 6 | +0x54 | +0x2D0 | Sensor Array | **WarpEngineSubsystem** (CT_WARP_ENGINE_PROPERTY 0x813B) | CORRECTION |
| 7 | +0x5C | +0x2D8 | Warp Drive | **RepairSubsystem** (CT_REPAIR_SUBSYSTEM_PROPERTY 0x813F) | CORRECTION |
| 8 | +0x60 | +0x2DC | Crew / Unknown-A | **CloakDevice** (CT_CLOAKING_SUBSYSTEM_PROPERTY 0x813A) | CORRECTION |
| 9 | +0x38 | +0x2B4 | Torpedo System | TorpedoSystem (CT_TORPEDO_SYSTEM_PROPERTY 0x8133) | OK |
| 10 | +0x3C | +0x2B8 | Phaser System | PhaserSystem (CT_WEAPON_SYSTEM iVar4==1) | OK |
| 11 | +0x40 | +0x2BC | Pulse Weapon System | PulseWeaponSystem (CT_WEAPON_SYSTEM iVar4==3) | OK |
| 12 | +0x58 | +0x2D4 | Tractor Beam System | TractorBeamSystem (CT_WEAPON_SYSTEM iVar4==4) | OK |

**Downstream impact**: doc line 129 — "Corrections from prior analysis: ship+0x2C0 was previously misidentified as Repair — it is Shield Generator … The Repair subsystem (ship+0x2C0 in the main container table) does NOT appear in the hash." This needs revision:
- Repair subsystem at ship+0x2D8 **DOES** appear in the hash (slot 7), contradicting the doc's "Repair does not appear" claim.
- The "previously misidentified as Repair" caveat applies to old non-v5 docs.

### Clar-1 — Receiver event-type write offset
Doc shows `event->eventType = 0x8000F6;` without specifying offset. Binary writes the value at event+0x10. Suggested: change to `event->fields[0x10/4] = 0x8000F6  // event_type at offset +0x10` or update the receiver pseudocode to use struct field names that match the verified offsets.

### Clar-2 — Torpedo int product fold (line 190)
Doc: `hash_fold((float)(torpType->field_0x08 * torpType->field_0x00), &hash);`
Binary: `FUN_005b6c10((float)local_4[2] * (float)*local_4, ...)` — casts each int to float SEPARATELY, multiplies as floats. Different precision behavior on overflow but same result for small int values typical of torpedo metadata. Refinement: change to `hash_fold((float)torpType->field_0x08 * (float)torpType->field_0x00, &hash);`.

### Clar-3 — `event+0x10 = &ET_BOOT_PLAYER` vs `event+0x10 = 0x8000F6`
Decompile shows `*(undefined **)(iHashBit + 0x10) = &ET_BOOT_PLAYER;` (symbolic ref), but actual disasm at 005b2311 shows `MOV dword ptr [EDI + 0x10], 0x8000f6` (immediate constant 0x008000F6). Both are identical at runtime because `ET_BOOT_PLAYER` is the **address constant** `0x008000F6` (the address itself is the unique event-type key, not a pointer to a value). This is a Ghidra naming artifact; doc pseudocode using `0x8000F6` directly is more accurate to the bytes.

### Clar-4 — Sender SAR vs LSR
Binary: `SAR EDX, 0x10` (signed). Doc says `(hash >> 16)` which most readers will interpret as unsigned. Equivalent on the low 16 bits (truncated by WriteShort), so wire-identical. Minor pedantic note for re-implementers using signed 32-bit hash type.

## Anchor table (for docwriter frontmatter)

```yaml
binary:
  size: 6394712
  build_id: stbc.exe-2002
  image_base: 0x00400000
evidence:
  - claim: "ComputeSubsystemIntegrityHash at 0x005b5eb0 reads 12 container slots from ship+0x27C in fixed order"
    address: 0x005b5eb0
    completeness: 26.0
    effective: 38.3
    confidence: high
    note: "Verified by full decompile; 12 slot-offset reads match doc table exactly"
  - claim: "HashBaseSubsystem at 0x005b6170 hashes 7 floats + N children + 4 boolean sentinels + optional powered field"
    address: 0x005b6170
    completeness: 10.4
    effective: 25.4
    confidence: high
    note: "Verified by decompile; all 4 boolean magic-constant pairs match doc table"
  - claim: "HashWeaponSystem at 0x005b6330 wraps base + 2 weapon-system booleans + per-child individual_weapon + torpedo extras"
    address: 0x005b6330
    completeness: 7.6
    effective: 25.7
    confidence: high
    note: "Verified by decompile; 2 weapon-system magic constants match doc table"
  - claim: "HashIndividualWeapon at 0x005b6560 dispatches 5-way per weapon type"
    address: 0x005b6560
    confidence: medium
    note: "Function exists; type dispatch (0x802B-0x802F) details not byte-checked this pass"
  - claim: "HashFoldFloat at 0x005b6c10 — abs(__ftol(value)), per-byte XOR, ROL by 1"
    address: 0x005b6c10
    completeness: 29.5
    effective: 40.9
    confidence: high
  - claim: "Sender Ship__WriteStateUpdate 0x005b17f0 emits has_hash bit only when !isMultiplayer; hash wire = (hash>>16)^(hash&0xFFFF)"
    address: 0x005b1d96
    confidence: high
    note: "Disasm confirms BL gate (bVar19), LEA ECX,[ESI+0x27C], CALL ComputeSubsystemIntegrityHash, SAR/XOR/PUSH/WriteShort"
  - claim: "Receiver Ship__ReadStateUpdate 0x005b21c0 validates hash only when isMultiplayer; mismatch posts event_type 0x8000F6"
    address: 0x005b2311
    confidence: high
    note: "Disasm confirms 0x8000F6 immediate at event+0x10, TGEventManager singleton at 0x0097F838, PostEvent at 0x006da2a0"
  - claim: "ET_BOOT_PLAYER kick path: 0x008000F6 -> MultiplayerWindow_BootPlayerHandler (0x00506170) -> TGBootPlayerMessage reason=4"
    address: 0x00506170
    completeness: 17.7
    effective: 33.0
    confidence: high
    note: "Function CREATED this pass (was undefined in DB); reason=4 confirmed via MOV [ESI+0x40], 0x4 at 0x005061CD"
  - claim: "Container at ship+0x27C is a sub-object with own vtable 0x008944c8 (ctor FUN_005b5d00); offsets +0x34..+0x60 alias ship+0x2B0..+0x2DC"
    address: 0x005b5d00
    confidence: high
    note: "Container ctor zero-fills param_1[1..0x18] = ship+0x280..+0x2DC; alignment confirms identity"
status: partial
verified: 2026-05-28
companions:
  - docs/protocol/wire-format-spec.md
  - docs/protocol/stateupdate.md
  - docs/protocol/stateupdate-subsystem-wire-format.md
```

## Open questions (for tracker §4)

- **OQ-1** — Slot 8 (`+0x60 / ship+0x2DC` = CloakDevice per foundation #1): doc says `Crew/Unknown-A` and notes "calls FUN_0055e220 (side-effect getter)". If the actual subsystem at +0x2DC is CloakDevice, what is FUN_0055e220 reading? Hypothesis: cloak-state side-effect (cloak->Refresh / cloak->UpdateState). Needs FUN_0055e220 decompile to confirm.
- **OQ-2** — Slot 7 (`+0x5C / ship+0x2D8` = RepairSubsystem per foundation #1): doc claims "Warp Drive" with `prop+0x4C` extra. If it's actually RepairSubsystem, what is prop+0x4C on RepairSubsystem? Hypothesis: repair team count or queue length. FUN_00564fe0 decompile would confirm.
- **OQ-3** — Slot 6 (`+0x54 / ship+0x2D0` = WarpEngineSubsystem per foundation #1): doc's `base_subsystem_hash | none` matches engine-pair pattern (Impulse at slot 5 has 4 extras via FUN_00560fc0, Warp at slot 6 has none — asymmetric). Confirm via FUN_00560fc0 vs no-helper for WarpEngine.
- **OQ-4** — Decompiled-source line numbers (doc lines 360-371). The reference/decompiled/05_game_mission.c file has not been re-generated since the 2026-05-28 import. Verify the cited line numbers still resolve to the expected functions; if not, update or drop the table.

## Cascade

- **wire-format-spec.md** (foundation #1) — no change needed; this leaf was wrong relative to foundation, not vice versa.
- **stateupdate.md** (mid #8) — no change; the `bVar19 = !isMultiplayer` gate identity is consistent.
- **stateupdate-subsystem-wire-format.md** (mid #11) — no change.

## Ghidra renames / plates / functions created

- 0x005b5eb0: FUN_005b5eb0 → **ComputeSubsystemIntegrityHash** + plate (12-slot order)
- 0x005b6170: FUN_005b6170 → **HashBaseSubsystem** + plate (7+N+4+powered structure, magic constants)
- 0x005b6c10: FUN_005b6c10 → **HashFoldFloat** + plate (abs-ftol + XOR + ROL)
- 0x005b6330: FUN_005b6330 → **HashWeaponSystem** + plate (base + 2 ws-sentinels + children + torpedo)
- 0x005b6560: FUN_005b6560 → **HashIndividualWeapon** (no plate, OQ-3 type-dispatch not byte-checked)
- 0x00506170: **CREATED** function (was raw bytes) → **MultiplayerWindow_BootPlayerHandler** + plate
- Saved Ghidra DB.

## Patterns / lessons

1. **Sub-object aliasing**: `ship+0x27C` is a wrapper class constructed via FUN_005b5d00 that lives in-place over a range overlapping the named-slot table at ship+0x2B0..0x2DC. The container's internal offsets (+0x34..+0x60) ARITHMETICALLY equal ship+0x2B0..0x2DC. When two docs disagree on what's "at offset N", check whether one is using class-internal offsets and the other is using outer-object offsets — they may refer to the same memory through different aliases.

2. **Event-type symbols as address constants**: `&ET_BOOT_PLAYER` and `0x008000F6` are the SAME thing — the address of the symbol literally IS the event-type ID. Ghidra decompiles it as a pointer dereference; disasm shows the bare immediate. Doc pseudocode using `0x8000F6` directly is more accurate to the bytes.

3. **bVar19 in writers**: same caveat as stateupdate-validation-20260528 — anti-cheat hash gates in StateUpdate writers use VAR NAMES (bVar2, bVar19) that look similar in decompile. Always cross-check the SET site with disasm — bVar19 at 005b1906 is set conditionally on (player_match AND !isMultiplayer), then RELOADED into BL at 005b1d96. Decompile may show wrong variable identity if Ghidra confuses lifetimes.

4. **Mostly-already-validated leaves** should still get a full decompile pass — even when foundation docs cross-confirm 90% of claims, the remaining 10% may include load-bearing slot identities (as here) or wire-format details that don't show up in the foundation hub.
