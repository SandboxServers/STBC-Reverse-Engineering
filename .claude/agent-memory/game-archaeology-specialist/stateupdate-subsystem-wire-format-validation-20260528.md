---
name: stateupdate-subsystem-wire-format-validation-20260528
description: Protocol doc #11 (mid). Wire formats and round-robin algorithm fully confirmed; named ship-slot table has TWO material corrections (ship+0x2C4=Hull not Power, ship+0x2C0 ShieldGenerator missing); EndMarker function misattribution clarified.
metadata:
  type: project
---

# stateupdate-subsystem-wire-format.md (Protocol Doc #11) v5 Validation Notes

**Date:** 2026-05-28
**Verdict:** partial — wire formats verified byte-by-byte but named-slot table has material errors

## Foundation cascade verified

This doc sits ON TOP of [[stateupdate-validation-20260528]] (mid #8) and inherits its
foundation work cleanly:

- Ship_WriteStateUpdate (0x005B17F0) flag 0x20 round-robin → SAME loop, SAME 10-byte budget cap, SAME tracker layout (iVar5+0x30 cursor, +0x34 index).
- Ship_ReadStateUpdate (0x005B21C0) flag 0x20 receiver → start_index byte + linked-list walk.
- SWIG TGBufferStream vtable @ 0x00895C58 — stream methods at slot +0x4C (WriteBit), +0x54 (WriteByte), +0xD8 (GetPos no-op trailer).

## Wire-format claims CONFIRMED (zero corrections)

The three WriteState formats are 100% verified:

### Format 1 — Base ShipSubsystem (0x0056D320, 8 vtables)
```
condition_byte = ftol((this+0x30 / GetMaxCondition()) * 255.0)  ; vtable[+0x54]
for each child in this+0x20[0..this+0x1C-1]:
    child.vtable[+0x70](stream, isOwnShip)
end: stream.vtable[+0xD8](GetPos discarded)
```
- this+0x30 = currentCondition (float HP)
- GetMaxCondition (0x0056C310) = property+0x20 (or _DAT_00888860 = 1.0f if no property)
- Multiplicand 0x0088B9AC = 255.0f

### Format 2 — PoweredSubsystem (0x00562960, 11 vtables)
```
base ShipSubsystem WriteState body
TEST BL, BL  ; isOwnShip param
JNZ skip_power
    WriteBit(1)
    WriteByte(ftol(this+0x90 * 100.0))  ; powerPctWanted
    GetPos
    RET
skip_power:
    WriteBit(0)
    GetPos
    RET
```
- this+0x90 = PowerPercentageWanted (0.0..1.0 ratio)
- Multiplicand 0x0088CE78 = 100.0f
- Decode scale (ReadState): 0x0088D4E4 = ~0.01f

### Format 3 — PowerSubsystem (0x005644B0, 1 vtable @ 0x0088A260)
```
base ShipSubsystem WriteState body
WriteByte(ftol((this+0xAC / GetMainBatteryLimit()) * 255.0))    ; UNCONDITIONAL
WriteByte(ftol((this+0xB4 / GetBackupBatteryLimit()) * 255.0))  ; UNCONDITIONAL
GetPos
RET
```
- this+0xAC = mainBatteryPower, this+0xB4 = backupBatteryPower
- GetMainBatteryLimit (0x005634C0) = property+0x48
- GetBackupBatteryLimit (0x005634D0) = property+0x4C
- CRITICAL: NO TEST/JCC on isOwnShip before the battery writes — confirmed at disassembly 0x005644B0

## Material corrections found

### C1 — Named ship-slot table has TWO errors (lines 348-360 of doc)

Decoded by reading `Ship__SetupProperties` (FUN_005B3FB0) switch on property type ID:

| Ship slot | Doc says | Binary says (SetupProperties case) |
|-----------|----------|-----------------------------------|
| ship+0x2B0 | Powered master (EPS) | PowerSubsystem (case 0x813E) — SAME thing, doc wording vague |
| ship+0x2C0 | (MISSING) | ShieldGenerator (case 0x8137) |
| ship+0x2C4 | PowerSubsystem (reactor) | HullSubsystem (case 0x8138) |
| ship+0x2C8 | (MISSING) | SensorSubsystem (case 0x8139) |

The doc's "ship+0x2C4 PowerSubsystem (reactor)" is FLAT WRONG. The reactor is at
ship+0x2B0 (already in the doc, just under a different name). Ship+0x2C4 is Hull.

### C2 — EndMarker function misattribution (line 76-77, 90-93, 110)

Doc says: *"EndMarker — No-op (function at 0x006cdae0 is just RET)"*.

Reality:
- The call site is `vtable[+0xD8]` on the stream.
- SWIG TGBufferStream vtable @ 0x00895C58 slot +0xD8 = **0x006CF9B0 = TGBufferStream_swig_GetPos** (reads cursor; return discarded).
- The function at 0x006CDAE0 IS a RET-only stub, but it lives at slot +0xB0 of a DIFFERENT vtable (0x00895B80, the non-SWIG TGStreamedObject vtable).

The wire behavior is unchanged (still effectively no-op), but the source function the doc cites is misattributed.

## Engine parent-child linking — fully confirmed

`Ship__LinkSubsystemToParent` (FUN_005B5030) reads property+0x48 for engines:
- 0 (EP_IMPULSE) → ship+0x2CC (ImpulseEngineSubsystem)
- 1 (EP_WARP) → ship+0x2D0 (WarpEngineSubsystem)

Confirmed at disassembly 0x005B5097 (case 0x813D branch).

Other parent-child mappings (also in FUN_005B5030):
- 0x802C PhaserBank → ship+0x2B8 PhaserSystem
- 0x802D PulseWeapon → ship+0x2BC PulseWeaponSystem
- 0x802E TractorBeamProjector → ship+0x2D4 TractorBeamSystem
- 0x802F TorpedoTube → ship+0x2B4 TorpedoSystem

## Subsystem linked list at ship+0x284 — fully confirmed

- ship+0x280: count (int)
- ship+0x284: head (Node*)
- ship+0x288: tail (Node*)
- ship+0x28C: free list (reusable removed nodes)

Node layout: `+0x00 data*, +0x04 next*, +0x08 prev*`.

Second list at ship+0x29C (used by non-weapon iteration):
- ship+0x298: count
- ship+0x29C: head
- ship+0x2A0: tail

`Ship__AddSubsystemToLists` (FUN_005B3E50) excludes 8 type IDs from the second list:
0x801F (PhaserSystem), 0x8021 (TractorBeamSystem), 0x802C (PhaserBank), 0x802F
(TorpedoTube), 0x802E (TractorBeamProjector), 0x802D (PulseWeapon), 0x8025
(WarpEngine), 0x8024 (CloakDevice).

## Pattern: misattributed function via vtable-slot confusion

The EndMarker correction (C2) illustrates a recurring archaeology trap:

**Doc identifies a vtable[+OFFSET] call by NAME (the actual function pointed to),
but cites the WRONG vtable.** When two different classes use the SAME slot offset
for similar-purpose methods, it's easy to find a no-op function at offset X in
class A and assume it's the one called by code that's actually using class B.

To avoid: ALWAYS verify the vtable address (`*piVar`) before identifying the slot
target. Read the bytes at vtable_addr+slot_offset, then look up that function
address. Don't search for "what function at slot +0xD8 looks like a no-op?".

## Pattern: incomplete switch-case enumeration in property handlers

The doc's ship-slot table (C1) was clearly written from a partial enumeration of
Ship_SetupProperties (FUN_005B3FB0) — it has the slots that the doc-author
checked and misses the ones they didn't. Full audit of the switch is required
when the doc claims to enumerate a "table of slots":

```
for each case in switch(property_type_id):
    record the ship+OFFSET = ... assignment
end
```

This is mechanical and catches all slots.

## Vtable count vs leaf-class count discrepancy

Doc lists 7 base + 9 Powered + 1 Power = 17 leaf-class consumers of these
WriteState functions. Binary shows 8 + 11 + 1 = 20 vtables. The +1 / +2 deltas
are likely intermediate vtables (the base classes themselves), not leaf classes.
This is NOT a correction — doc's list is correct as a leaf enumeration. But
when documenting xref counts, distinguish "vtables using this fn" from
"user-visible leaf subsystem types".

## Functions touched

| Function | Address | Result |
|----------|---------|--------|
| Ship__WriteStateUpdate | 0x005B17F0 | inherited from mid #8 |
| Ship__ReadStateUpdate | 0x005B21C0 | inherited from mid #8 |
| ShipSubsystem__WriteState | 0x0056D320 | renamed + plate |
| ShipSubsystem__ReadState | 0x0056D390 | renamed |
| PoweredSubsystem__WriteState | 0x00562960 | renamed + plate |
| PoweredSubsystem__ReadState | 0x005629D0 | renamed |
| PowerSubsystem__WriteState | 0x005644B0 | plate (already named) |
| PowerSubsystem__ReadState | 0x00564530 | **created** (was undefined; only DATA xref from vtable @ 0x0088A264) + named + plate |
| ShipSubsystem__GetMaxCondition | 0x0056C310 | renamed |
| ShipSubsystem__GetChildSubsystem | 0x0056C570 | renamed |
| PowerSubsystem__GetMainBatteryLimit | 0x005634C0 | renamed |
| PowerSubsystem__GetBackupBatteryLimit | 0x005634D0 | renamed |
| ShipSubsystem__AddChildSubsystem | 0x0056C5C0 | renamed |
| Ship__SetupProperties | 0x005B3FB0 | renamed + plate listing 12 named slot mappings |
| Ship__AddSubsystemToLists | 0x005B3E50 | renamed |
| Ship__LinkSubsystemToParent | 0x005B5030 | renamed + plate documenting 3 classifications |
| Ship__LinkAllSubsystemsToParents | 0x005B3E20 | renamed |

Saved.
