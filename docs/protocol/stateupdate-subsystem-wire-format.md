> [docs](../README.md) / [protocol](README.md) / stateupdate-subsystem-wire-format.md

---
title: StateUpdate (0x1C) Subsystem Health Wire Format
type: reference
audience: re-engineer
validated: 2026-05-28
methodology: FUNCTION_DOC_WORKFLOW_V5
binary:
  name: stbc.exe
  size: 6394712
  base: 0x00400000
status: partial
evidence:
  - claim: "Round-robin walks ship+0x284 doubly-linked list with 10-byte budget per tick"
    address: 0x005B17F0
    function: Ship__WriteStateUpdate
    completeness: 0
    confidence: high
    note: "10-byte cap at 0x005B1EC0 (`CMP EAX, 0xA`); cursor at iVar5+0x30, index at iVar5+0x34. Inherited from stateupdate.md mid #8."
  - claim: "Receiver reads start_index byte then walks ship+0x284 calling vtable[+0x74] ReadState per node, wrapping at NULL"
    address: 0x005B21C0
    function: Ship__ReadStateUpdate
    completeness: 5
    confidence: high
    note: "Wrap-and-stop loop at 0x005B26B0."
  - claim: "Base ShipSubsystem::WriteState writes one condition byte then recursively walks children at this+0x20"
    address: 0x0056D320
    function: ShipSubsystem__WriteState
    completeness: 10
    confidence: high
    note: "Referenced by 8 vtables (leaf classes Hull/Shield/PhaserBank/TorpedoTube/PulseWeapon/TractorBeamProjector/Engine + base)."
  - claim: "PoweredSubsystem::WriteState calls base then writes 1 bit; if isOwnShip==0 also writes 1 powerPct byte"
    address: 0x00562960
    function: PoweredSubsystem__WriteState
    completeness: 11
    confidence: high
    note: "Decompile: `TEST BL,BL / JNZ skip_power_branch`. Referenced by 11 vtables."
  - claim: "PowerSubsystem::WriteState calls base then writes BOTH battery bytes UNCONDITIONAL"
    address: 0x005644B0
    function: PowerSubsystem__WriteState
    completeness: 25
    confidence: high
    note: "No TEST/JCC on isOwnShip between FUN_0056D320 and the two `CALL [vtable+0x54]` byte writes. Single consumer @ vtable 0x0088A260."
  - claim: "End-of-block trailer calls TGBufferStream_swig_GetPos via stream vtable[+0xD8] (return discarded)"
    address: 0x006CF9B0
    function: TGBufferStream_swig_GetPos
    completeness: 0
    confidence: high
    note: "SWIG TGBufferStream vtable @ 0x00895C58 slot +0xD8 = 0x006CF9B0. Replaces prior misattribution to 0x006CDAE0 (which is a different class's RET stub at vtable+0xB0). See C2 in NOTE block."
  - claim: "Ship subsystem linked list: count at +0x280, head at +0x284, tail at +0x288, free list at +0x28C"
    address: 0x005B3E50
    function: Ship__AddSubsystemToLists
    completeness: 0
    confidence: high
  - claim: "Property type ID → ship-slot mapping decoded from SetupProperties switch"
    address: 0x005B3FB0
    function: Ship__SetupProperties
    completeness: 0
    confidence: high
    note: "Plate comment installed listing all 12 named slot mappings. Material correction C1 sourced here."
  - claim: "Engine parent disambiguation reads property+0x48 (0=EP_IMPULSE → ship+0x2CC, 1=EP_WARP → ship+0x2D0)"
    address: 0x005B5097
    function: Ship__LinkSubsystemToParent
    completeness: 0
    confidence: high
    note: "case 0x813D CT_ENGINE_PROPERTY branch."
  - claim: "Second list at ship+0x29C excludes 8 weapon/engine/cloak type IDs"
    address: 0x005B3E50
    function: Ship__AddSubsystemToLists
    completeness: 0
    confidence: high
    note: "Excluded: 0x801F PhaserSystem, 0x8021 TractorBeamSystem, 0x802C PhaserBank, 0x802F TorpedoTube, 0x802E TractorBeamProjector, 0x802D PulseWeapon, 0x8025 WarpEngine, 0x8024 CloakDevice. Confirmed by 8-deep nested type-ID check at 0x5B3EA0-0x5B3F40."
  - claim: "GetMaxCondition returns property+0x20 or 1.0f fallback when property NULL"
    address: 0x0056C310
    function: ShipSubsystem__GetMaxCondition
    completeness: 0
    confidence: high
    note: "Fallback constant `_DAT_00888860 = 0x3F800000 = 1.0f`."
  - claim: "Battery limits read from property+0x48 (main) and property+0x4C (backup)"
    address: 0x005634C0
    function: PowerSubsystem__GetMainBatteryLimit
    completeness: 0
    confidence: high
    note: "Sibling at 0x005634D0 GetBackupBatteryLimit reads property+0x4C."
  - claim: "Byte-scale multiplier 255.0f, powerPct multiplier 100.0f, powerPct decode scale ~0.01f"
    address: 0x0088B9AC
    function: (global constants)
    completeness: null
    confidence: high
    note: "Raw bytes verified: 0x0088B9AC=0x437F0000 (255.0f), 0x0088CE78=0x42C80000 (100.0f), 0x0088D4E4=0x3C23D70A (~0.01f)."
  - claim: "Subsystem vtable layout: WriteState at +0x70, ReadState at +0x74"
    address: 0x00892D00
    function: (HullSubsystem vtable)
    completeness: null
    confidence: high
    note: "Raw vtable byte read: 0x00892D00+0x70 = 0x0056D320 base WriteState."
  - claim: "Sovereign-class top-level subsystem count = 11 (rest is children); 1-byte-per-node remote cycle ~49 bytes"
    address: null
    function: (sovereign.py hardpoint script, client install only)
    completeness: null
    confidence: medium
    note: "Hardpoint file not in repo; example is observational and cannot be re-anchored without the client install."
companions:
  - docs/protocol/stateupdate.md
  - docs/protocol/per-ship-subsystem-wire-format.md
  - docs/protocol/stream-primitives.md
  - docs/protocol/wire-format-spec.md
  - docs/engine/decompiled-functions.md
  - docs/protocol/v5-validation-status.md
supersedes:
  - 2026-02-18
---

# StateUpdate (0x1C) Subsystem Health Wire Format

> [!NOTE]
> This doc is `status: partial`. The ship+0x284 linked list architecture, three WriteState formats (Base 0x0056D320 / Powered 0x00562960 / Power 0x005644B0), round-robin algorithm with 10-byte budget, engine parent disambiguation via property+0x48, and 8-type exclusion list for ship+0x29C are all v5-validated against the current Ghidra import (2026-05-28). Two material corrections landed:
>
> - **C1 — Named ship-slot table updated.** ship+0x2C4 is `HullSubsystem` (not PowerSubsystem; the reactor is at ship+0x2B0). Added missing rows for ship+0x2C0 `ShieldGenerator` and ship+0x2C8 `SensorSubsystem`. The prior table was a partial enumeration of `Ship__SetupProperties` — the full switch was re-walked this pass.
> - **C2 — EndMarker function attribution corrected.** `stream.vtable[+0xD8]` calls `TGBufferStream_swig_GetPos` at 0x006CF9B0 (return value discarded). The prior doc attributed the trailer to 0x006CDAE0, which IS a RET-only stub but lives at slot +0xB0 of a different vtable (0x00895B80, non-SWIG TGStreamedObject). Wire behavior is unchanged (still effectively no-op); documentation accuracy improved.
>
> One observational claim — the Sovereign-class wire-byte example — is marked `confidence: medium` because its source file (`sovereign.py` hardpoint) lives on the client install only. See [docs/guides/v5-evidence-header.md](../guides/v5-evidence-header.md) for the standard.

## Executive Summary

The StateUpdate flag 0x20 (subsystem health) uses a **round-robin serializer** that walks
the ship's **top-level subsystem linked list** at `ship+0x284`. Each subsystem's `WriteState`
virtual function writes a **variable-length** block: its own condition byte, then recursively
writes all child subsystems. There is **no fixed index table** and **no fixed maximum**.
Wire byte positions are determined entirely by the order subsystems appear in the
ship's linked list, which is determined by the order `AddToSet()` is called in the
hardpoint Python file.

## Answers to Key Questions

### Q1: Fixed index table or per-ship order?

**Per-ship linked list order.** There is no global index mapping table. The serializer walks
ship+0x284 (a doubly-linked list of subsystem pointers) and each subsystem writes its own
state via `vtable+0x70` (WriteState). The linked list order is determined by the Python
hardpoint file's `LoadPropertySet()` function, which calls `AddToSet("Scene Root", prop)`
in a specific order for each ship class.

### Q2: How are missing subsystems handled?

**They simply don't exist in the list.** If a ship doesn't have a cloaking device, there
is no cloak entry in ship+0x284. The serializer only iterates what's present. Both sender
and receiver use the **same** linked list (ship+0x284), built from the **same** hardpoint
file, so they always agree on subsystem count and order.

### Q3: What drives the round-robin count?

The **ship's actual subsystem count** in ship+0x280 (list length). There is no fixed maximum
of 33. The round-robin writes subsystems until either:
- 10 bytes of stream space are consumed (budget limit, `CMP EAX, 0xA` at 0x005B1EC0), or
- It has wrapped back to its starting position (full cycle complete).

### Q4: Is there a mapping array?

**No mapping array.** The wire protocol position is implicitly defined by the linked list
traversal order. Sender and receiver must have identical linked lists (same subsystems in
same order). This is guaranteed because both sides execute the same hardpoint Python file
and the same C++ `SetupProperties` + `LinkAllSubsystemsToParents` functions.

## Detailed Wire Format

### Flag 0x20 Block Structure

```
[startIndex: byte]    // Which subsystem index the round-robin starts from this tick
[subsystem_0 data]    // WriteState output for subsystem at startIndex
[subsystem_1 data]    // WriteState output for subsystem at startIndex+1
...                   // Continues until 10-byte budget exhausted or full wrap
```

### Per-Subsystem WriteState Output

Each subsystem's WriteState is a **virtual function** at `vtable+0x70`. There are three
implementations, all v5-validated 2026-05-28:

#### 1. Base ShipSubsystem::WriteState (0x0056D320) [v5-validated 2026-05-28]

Used by 8 vtables: HullSubsystem, ShieldGenerator, PhaserBank, TorpedoTube, PulseWeapon,
TractorBeamProjector, individual Engine, plus the base class vtable itself.

```
[condition: byte]     // ftol((currentCondition / GetMaxCondition()) * 255.0)
                      //   currentCondition = this+0x30
                      //   GetMaxCondition (0x0056C310) = property+0x20
                      //                                  (or _DAT_00888860 = 1.0f if no property)
                      //   multiplicand 0x0088B9AC = 255.0f
                      //   0xFF = 100% health, 0x00 = destroyed, truncated toward zero
[child_0 WriteState]  // Recursive: each child writes its own block via vtable[+0x70]
[child_1 WriteState]
...
[end-of-block trailer] // stream.vtable[+0xD8] → TGBufferStream_swig_GetPos at 0x006CF9B0
                       // (reads cursor; return discarded — effectively no-op)
```

#### 2. PoweredSubsystem::WriteState (0x00562960) [v5-validated 2026-05-28]

Used by 11 vtables: CloakDevice, ImpulseEngine, RepairSubsystem, SensorSubsystem, WarpEngine,
PhaserSystem, TorpedoSystem, TractorBeamSystem, WeaponSystem, plus intermediate base
vtables.

```
[base WriteState]     // Calls ShipSubsystem::WriteState first (condition + children)
if (isOwnShip == 0):  // Remote ship — include power data
    [hasData: bit=1]              // stream.vtable[+0x4C] WriteBit
    [powerPctWanted: byte]        // ftol(this+0x90 * 100.0)
                                  //   this+0x90 = PowerPercentageWanted (0.0-1.0 ratio)
                                  //   constant 100.0f at 0x0088CE78
                                  //   result range 0-100 (one byte)
    [end-of-block trailer]        // GetPos no-op
else:                 // Own ship — owner has local state, skip power data
    [hasData: bit=0]
    [end-of-block trailer]
```

Branch confirmed in disassembly: `TEST BL,BL / JNZ skip_power_branch`.

#### 3. PowerSubsystem::WriteState (0x005644B0) [v5-validated 2026-05-28]

Used by exactly 1 vtable @ 0x0088A260 (PowerSubsystem, the reactor/EPS).

PowerSubsystem **ALWAYS** writes both battery bytes regardless of isOwnShip. There is
no `TEST/JCC` on isOwnShip between the base call and the two battery writes — confirmed
at disassembly 0x005644B0.

```
[base WriteState]              // Calls ShipSubsystem::WriteState (condition + children)
[mainBatteryPct: byte]         // ftol((mainBatteryPower / GetMainBatteryLimit()) * 255.0)
                               //   mainBatteryPower = this+0xAC
                               //   GetMainBatteryLimit (0x005634C0) → property+0x48
[backupBatteryPct: byte]       // ftol((backupBatteryPower / GetBackupBatteryLimit()) * 255.0)
                               //   backupBatteryPower = this+0xB4
                               //   GetBackupBatteryLimit (0x005634D0) → property+0x4C
[end-of-block trailer]         // GetPos no-op
```

### Receiver (flag 0x20 in Ship__ReadStateUpdate, 0x005B21C0) [v5-validated 2026-05-28]

```c
startIndex = ReadByte(stream);
node = ship->subsystemListHead;  // ship+0x284
// Skip to startIndex position
for (i = startIndex; i > 0; i--) {
    if (node) node = node->next;
}
// Read subsystem data until stream exhausted
while (streamPos < dataLength) {
    if (!node) break;
    subsystem = node->data;
    node = node->next;
    if (!subsystem) break;
    subsystem->ReadState(stream, timestamp);  // vtable+0x74
    if (!node) node = ship->subsystemListHead;  // wrap to beginning
}
```

## Ship+0x284 Linked List Contents

### What's IN the list (top-level subsystems) [v5-validated 2026-05-28]

These subsystems remain in ship+0x284 after `Ship__LinkAllSubsystemsToParents` runs:

| Runtime Type ID | Name | WriteState | Notes |
|----------------|------|------------|-------|
| 0x8027 | HullSubsystem | Base | One or more hulls per ship |
| 0x8028 | ShieldGenerator | Base | Has 6 shield-facing children |
| 0x8023 | SensorSubsystem | Powered | |
| 0x8022 | PowerSubsystem | Power | Writes 2 extra battery bytes |
| 0x8026 | ImpulseEngine | Powered | Children: individual engines |
| 0x8025 | WarpEngine | Powered | Children: individual engines |
| 0x801D | WeaponSystem | Powered | Generic weapon system container |
| 0x801E | TorpedoSystem | Powered | Children: TorpedoTubes |
| 0x801F | PhaserSystem | Powered | Children: PhaserBanks |
| 0x8021 | TractorBeamSystem | Powered | Children: TractorBeamProjectors |
| 0x8024 | CloakDevice | Powered | Only on ships with cloak |
| 0x8029 | RepairSubsystem | Powered | |

### What's REMOVED from the list (linked as children) [v5-validated 2026-05-28]

These are removed from ship+0x284 by `Ship__LinkSubsystemToParent` (FUN_005B5030) and
added as children of parent systems:

| Runtime Type ID | Name | Parent Location | Parent Type |
|----------------|------|----------------|-------------|
| 0x802C | PhaserBank | ship+0x2B8 | PhaserSystem |
| 0x802D | PulseWeapon | ship+0x2BC | PulseWeaponSystem |
| 0x802E | TractorBeamProjector | ship+0x2D4 | TractorBeamSystem |
| 0x802F | TorpedoTube | ship+0x2B4 | TorpedoSystem |
| 0x813D (Engine) | Individual Engine | ship+0x2CC or 0x2D0 | ImpulseEngine (EP_IMPULSE=0) or WarpEngine (EP_WARP=1), determined by `property+0x48` tag |

### What's NEVER in the list

Properties that are not subsystems (handled in `SetupProperties` but never added to 0x284):
- ObjectEmitterProperty (Probe Launcher, Shuttle Bay, Decoy Launcher)
- ShipProperty
- ViewscreenProperty
- FirstPersonProperty
- BridgeProperty_Create creates HullSubsystem — actually IS in the list

## Sovereign-Class Example [confidence: medium]

Based on `sovereign.py` `LoadPropertySet` order, after `Ship__LinkAllSubsystemsToParents`.
This example is **observational** — the hardpoint script lives on the client install only,
so the byte counts can't be re-anchored from the repo. Numbers below are carried over
from the 2026-02-18 validation pass.

| List Index | Subsystem | Children | Bytes per WriteState (remote) |
|-----------|-----------|----------|-------------------------------|
| 0 | Hull (HullSubsystem) | 0 | 1 (condition) |
| 1 | Shield Generator (ShieldGenerator) | 0 visible | 1 (condition; shield facing HP via flag 0x40) |
| 2 | Sensor Array (SensorSubsystem) | 0 | 3 (cond + bit + powerPct) |
| 3 | Warp Core (PowerSubsystem) | 0 | 3 (cond + 2 battery bytes) |
| 4 | Impulse Engines (ImpulseEngine) | 2 (Port + Star) | 5 (cond + 2 children + bit + powerPct) |
| 5 | Torpedoes (TorpedoSystem) | 6 tubes | 9 (cond + 6 children + bit + powerPct) |
| 6 | Repair (RepairSubsystem) | 0 | 3 (cond + bit + powerPct) |
| 7 | Phasers (PhaserSystem) | 8 banks | 11 (cond + 8 children + bit + powerPct) |
| 8 | Tractors (TractorBeamSystem) | 4 projectors | 7 (cond + 4 children + bit + powerPct) |
| 9 | Warp Engines (WarpEngine) | 2 (Port + Star) | 5 (cond + 2 children + bit + powerPct) |
| 10 | Bridge (HullSubsystem) | 0 | 1 (condition) |

**Total top-level subsystems: 11** (not 33 — the "33" count includes individual weapons/engines as children).

## Round-Robin Serializer Algorithm [v5-validated 2026-05-28]

From `Ship__WriteStateUpdate` (0x005B17F0), flag 0x20 section. The pseudocode below
matches the disassembly instruction-for-instruction, including the 10-byte budget cap
at 0x005B1EC0.

```
// Per-object tracking structure at iVar5:
//   +0x30: linked list cursor (current node pointer)
//   +0x34: subsystem index counter (integer)

if (cursor == 0) {           // First time or reset
    cursor = ship->subsystemListHead;  // ship+0x284 = pShip2[0xA1]
    index = 0;
}

initialCursor = cursor;       // Remember starting position for wrap detection
WriteByte(stream, index);     // Write the startIndex

bytesWritten = 0;
while (bytesWritten < 10) {   // 10-byte budget per tick (CMP EAX, 0xA at 0x005B1EC0)
    node = cursor;
    if (node == NULL) { subsystem = NULL; }
    else { subsystem = node->data; cursor = node->next; }

    subsystem->WriteState(stream, isLocalPlayer);  // vtable+0x70
    index++;

    if (cursor == 0) {        // End of list: wrap
        cursor = ship->subsystemListHead;
        index = 0;
    }
    if (cursor == initialCursor) break;  // Full cycle: stop
    bytesWritten = stream.position - startPosition;
}
```

## Key Implementation Details

### Linked List Node Structure [v5-validated 2026-05-28]

```c
struct SubsystemListNode {
    ShipSubsystem* data;       // +0x00: pointer to subsystem object
    SubsystemListNode* next;   // +0x04
    SubsystemListNode* prev;   // +0x08 (doubly-linked, maintained by ship+0x288 tail)
};
```

### Ship Subsystem List Fields [v5-validated 2026-05-28]

The ship has **two** subsystem lists. The first is the round-robin/replication source;
the second is for non-weapon iteration (damage distribution, repair queue, etc.).

```c
// First list (round-robin, replication source for flag 0x20):
// ship+0x280: count (int)         -- number of entries in list
// ship+0x284: head (Node*)        -- first node (round-robin starts here)
// ship+0x288: tail (Node*)        -- last node
// ship+0x28C: free list (Node*)   -- reusable removed nodes

// Second list (non-weapon iteration; HEAD pointer, not first node):
// ship+0x298: count (int)
// ship+0x29C: head (Node*)        -- 8 type IDs are EXCLUDED here (see below)
// ship+0x2A0: tail (Node*)
```

### Named Ship Subsystem Slots [v5-validated 2026-05-28]

**C1 correction applied.** The previous table mislabeled ship+0x2C4 as PowerSubsystem
(the reactor is actually at ship+0x2B0) and was missing ship+0x2C0 ShieldGenerator and
ship+0x2C8 SensorSubsystem. The corrected table is sourced from
`Ship__SetupProperties` (FUN_005B3FB0), a switch on the property type ID. A plate
comment with all 12 mappings is installed in Ghidra.

| Offset | Subsystem | Property type ID | Notes |
|--------|-----------|------------------|-------|
| ship+0x2B0 | PowerSubsystem (reactor / EPS) | 0x813E CT_POWER_PROPERTY | Power distribution; doc previously called this "Powered master (EPS)" |
| ship+0x2B4 | TorpedoSystem | 0x8133 CT_TORPEDO_SYSTEM_PROPERTY | |
| ship+0x2B8 | PhaserSystem | 0x812F + `iVar4==1` | CT_WEAPON_SYSTEM, phaser variant |
| ship+0x2BC | PulseWeaponSystem | 0x812F + `iVar4==3` | CT_WEAPON_SYSTEM, pulse variant |
| **ship+0x2C0** | **ShieldGenerator** | **0x8137 CT_SHIELD_PROPERTY** | **Added 2026-05-28** |
| **ship+0x2C4** | **HullSubsystem (Bridge / secondary hull)** | **0x8138 CT_HULL_PROPERTY** | **Corrected 2026-05-28 (was: PowerSubsystem reactor)** |
| **ship+0x2C8** | **SensorSubsystem** | **0x8139 CT_SENSOR_PROPERTY** | **Added 2026-05-28** |
| ship+0x2CC | ImpulseEngineSubsystem | 0x813C CT_IMPULSE_ENGINE_PROPERTY | EP_IMPULSE engines attach here |
| ship+0x2D0 | WarpEngineSubsystem | 0x813B CT_WARP_ENGINE_PROPERTY | EP_WARP engines attach here |
| ship+0x2D4 | TractorBeamSystem | 0x812F + `iVar4==4` | CT_WEAPON_SYSTEM, tractor variant |
| ship+0x2D8 | RepairSubsystem | 0x813F CT_REPAIR_SUBSYSTEM_PROPERTY | |
| ship+0x2DC | CloakDevice | 0x813A CT_CLOAKING_SUBSYSTEM_PROPERTY | |

Open question: `FUN_005B5240` handles `case 0x812E` and `FUN_005B5280` handles
`case 0x8145` in `Ship__SetupProperties` — neither's slot nor wire-format role is
documented. Surfaced as documentation debt below.

### Key Functions [v5-validated 2026-05-28]

| Address | Name | Role |
|---------|------|------|
| 0x005B17F0 | Ship__WriteStateUpdate | Main serializer (flag 0x20 = subsystems) |
| 0x005B21C0 | Ship__ReadStateUpdate | Main deserializer (flag 0x20 receiver) |
| 0x005B3FB0 | Ship__SetupProperties | Creates ALL subsystems from NIF properties; populates named ship slots via property-type switch |
| 0x005B3E20 | Ship__LinkAllSubsystemsToParents | Iterates ship+0x284 calling LinkSubsystemToParent on each child |
| 0x005B3E50 | Ship__AddSubsystemToLists | Appends to ship+0x284 (always); 8 types excluded from ship+0x29C |
| 0x005B5030 | Ship__LinkSubsystemToParent | Identifies parent, calls AddChild, removes from ship+0x284 |
| 0x0056C5C0 | ShipSubsystem__AddChildSubsystem | Grows child array at +0x20, increments +0x1C |
| 0x0056D320 | ShipSubsystem__WriteState (base) | Writes condition byte + recurses children |
| 0x00562960 | PoweredSubsystem__WriteState | Base + hasData bit + power percentage byte |
| 0x005644B0 | PowerSubsystem__WriteState | Base + 2 battery percentage bytes (UNCONDITIONAL) |
| 0x0056D390 | ShipSubsystem__ReadState (base) | Reads condition byte + recurses children |
| 0x005629D0 | PoweredSubsystem__ReadState | Base + reads hasData bit + power percentage |
| 0x00564530 | PowerSubsystem__ReadState | Base + reads 2 battery bytes (function CREATED this pass — see below) |
| 0x0056C310 | ShipSubsystem__GetMaxCondition | Returns property+0x20 (float max HP), or 1.0f if no property |
| 0x0056C570 | ShipSubsystem__GetChildSubsystem | Returns child array[index] from +0x20 |
| 0x005634C0 | PowerSubsystem__GetMainBatteryLimit | Returns property+0x48 |
| 0x005634D0 | PowerSubsystem__GetBackupBatteryLimit | Returns property+0x4C |
| 0x006CF9B0 | TGBufferStream_swig_GetPos | SWIG stream vtable[+0xD8] — end-of-block trailer (return discarded) |

### Vtable Consumer Counts (Refinement R3)

The doc historically listed 7 + 9 + 1 = 17 leaf subsystem types. The binary shows
8 + 11 + 1 = 20 vtables consuming these WriteState functions. The +1 / +2 deltas are
intermediate base-class vtables (the base classes themselves participating in the
hierarchy), not user-visible leaf subsystem types. The 7 / 9 / 1 leaf enumeration in
the IN/REMOVED tables above is correct.

### CT_ Type Constants (from SWIG constant table)

| Value | Name | Category |
|-------|------|----------|
| 0x801B | CT_SHIP_SUBSYSTEM | Base type |
| 0x801C | CT_POWERED_SUBSYSTEM | Base powered |
| 0x801D | CT_WEAPON_SYSTEM | System-level |
| 0x801E | CT_TORPEDO_SYSTEM | System-level |
| 0x801F | CT_PHASER_SYSTEM | System-level |
| 0x8020 | CT_PULSE_WEAPON_SYSTEM | System-level |
| 0x8021 | CT_TRACTOR_BEAM_SYSTEM | System-level |
| 0x8022 | CT_POWER_SUBSYSTEM | System-level |
| 0x8023 | CT_SENSOR_SUBSYSTEM | System-level |
| 0x8024 | CT_CLOAKING_SUBSYSTEM | System-level |
| 0x8025 | CT_WARP_ENGINE_SUBSYSTEM | System-level |
| 0x8026 | CT_IMPULSE_ENGINE_SUBSYSTEM | System-level |
| 0x8027 | CT_HULL_SUBSYSTEM | System-level |
| 0x8028 | CT_SHIELD_SUBSYSTEM | System-level |
| 0x8029 | CT_REPAIR_SUBSYSTEM | System-level |
| 0x802A | CT_WEAPON | Individual weapon base |
| 0x802B | CT_ENERGY_WEAPON | Individual weapon |
| 0x802C | CT_PHASER_BANK | Individual (child of 0x801F) |
| 0x802D | CT_PULSE_WEAPON | Individual (child of 0x8020) |
| 0x802E | CT_TRACTOR_BEAM_PROJECTOR | Individual (child of 0x8021) |
| 0x802F | CT_TORPEDO_TUBE | Individual (child of 0x801E) |

### Property Type Constants (from SWIG constant table)

| Value | Name | Creates Runtime Type |
|-------|------|---------------------|
| 0x812B | CT_SUBSYSTEM_PROPERTY | Base |
| 0x812C | CT_POWERED_SUBSYSTEM_PROPERTY | Base powered |
| 0x812F | CT_WEAPON_SYSTEM_PROPERTY | PhaserSystem / TorpedoSystem / TractorBeamSystem (variant via iVar4) |
| 0x8132 | CT_PHASER_PROPERTY | PhaserBank |
| 0x8133 | CT_TORPEDO_SYSTEM_PROPERTY | TorpedoSystem |
| 0x8134 | CT_TORPEDO_TUBE_PROPERTY | TorpedoTube |
| 0x8135 | CT_PULSE_WEAPON_PROPERTY | PulseWeapon |
| 0x8136 | CT_TRACTOR_BEAM_PROPERTY | TractorBeamProjector |
| 0x8137 | CT_SHIELD_PROPERTY | ShieldGenerator → ship+0x2C0 |
| 0x8138 | CT_HULL_PROPERTY | HullSubsystem → ship+0x2C4 |
| 0x8139 | CT_SENSOR_PROPERTY | SensorSubsystem → ship+0x2C8 |
| 0x813A | CT_CLOAKING_SUBSYSTEM_PROPERTY | CloakDevice → ship+0x2DC |
| 0x813B | CT_WARP_ENGINE_PROPERTY | WarpEngine → ship+0x2D0 |
| 0x813C | CT_IMPULSE_ENGINE_PROPERTY | ImpulseEngine → ship+0x2CC |
| 0x813D | CT_ENGINE_PROPERTY | Individual Engine (impulse OR warp via property+0x48) |
| 0x813E | CT_POWER_PROPERTY | PowerSubsystem → ship+0x2B0 |
| 0x813F | CT_REPAIR_SUBSYSTEM_PROPERTY | RepairSubsystem → ship+0x2D8 |

### Engine Parent-Child Linking Mechanism [v5-validated 2026-05-28]

Individual engines (`CT_ENGINE_PROPERTY`, 0x813D) are the **only** child subsystem type
that can belong to either of two different parent systems: `ImpulseEngineSubsystem`
(0x8026) or `WarpEngineSubsystem` (0x8025). All other child types have unambiguous
parents (phasers → PhaserSystem, torpedoes → TorpedoSystem, etc.).

The disambiguation mechanism is an **explicit enum tag** stored at `property+0x48`,
set via the Python API `SetEngineType()`. `Ship__LinkSubsystemToParent`
(FUN_005B5030) reads `property+0x48` for `CT_ENGINE_PROPERTY` subsystems at
disassembly 0x005B5097.

| Enum Value | Constant | Meaning |
|-----------|----------|---------|
| 0 | `EP_IMPULSE` | Attach to ImpulseEngineSubsystem (ship+0x2CC) |
| 1 | `EP_WARP` | Attach to WarpEngineSubsystem (ship+0x2D0) |

**Default**: `EP_IMPULSE` (0) — the EngineProperty constructor initializes `property+0x48 = 0`.

#### Python API Usage (from hardpoint scripts)

```python
# Individual engines are created with EngineProperty_Create (CT_ENGINE_PROPERTY)
PortImpulse = App.EngineProperty_Create("Port Impulse")
PortImpulse.SetEngineType(PortImpulse.EP_IMPULSE)   # property+0x48 = 0

PortWarp = App.EngineProperty_Create("Port Warp")
PortWarp.SetEngineType(PortWarp.EP_WARP)             # property+0x48 = 1
```

Note: the *system-level* containers use different property types entirely:
- `App.ImpulseEngineProperty_Create()` → `CT_IMPULSE_ENGINE_PROPERTY` (0x813C)
- `App.WarpEngineProperty_Create()` → `CT_WARP_ENGINE_PROPERTY` (0x813B)

These are never ambiguous — only individual `EngineProperty` children need the tag.

#### Stock Ship Verification

All 16 stock multiplayer ships explicitly call `SetEngineType()` on every individual engine
— no ship relies on the default. However, mods may omit the call, in which case the
engine defaults to `EP_IMPULSE` and attaches to the impulse engine system.

### Subsystem Classification in Ship__AddSubsystemToLists (FUN_005B3E50) [v5-validated 2026-05-28]

After adding ALL subsystems to ship+0x284, the function classifies them. The
classification is enforced by an 8-deep nested type-ID check at 0x5B3EA0-0x5B3F40.

**Types EXCLUDED from ship+0x29C (only in ship+0x284):**

- 0x801F PhaserSystem
- 0x8021 TractorBeamSystem
- 0x802C PhaserBank
- 0x802F TorpedoTube
- 0x802E TractorBeamProjector
- 0x802D PulseWeapon
- 0x8025 WarpEngine
- 0x8024 CloakDevice

**Types that go to BOTH ship+0x284 AND ship+0x29C** (non-weapon iteration: damage
distribution, repair queue, etc.):

- 0x8027 HullSubsystem
- 0x8028 ShieldGenerator
- 0x8023 SensorSubsystem
- 0x8022 PowerSubsystem
- 0x8026 ImpulseEngine
- 0x8029 RepairSubsystem
- 0x801E TorpedoSystem
- 0x801D WeaponSystem
- 0x8029 RepairSubsystem

## Ghidra Annotations Applied (2026-05-28)

This pass renamed 14 functions, created 1 previously-undefined function, and installed
7 plate comments. The annotations make this doc's address citations resolvable directly
in the Ghidra browser without needing the FUN_ alias.

### Functions renamed

| Old name | New name | Address |
|----------|----------|---------|
| FUN_0056D320 | ShipSubsystem__WriteState | 0x0056D320 |
| FUN_0056D390 | ShipSubsystem__ReadState | 0x0056D390 |
| FUN_00562960 | PoweredSubsystem__WriteState | 0x00562960 |
| FUN_005629D0 | PoweredSubsystem__ReadState | 0x005629D0 |
| FUN_0056C310 | ShipSubsystem__GetMaxCondition | 0x0056C310 |
| FUN_0056C570 | ShipSubsystem__GetChildSubsystem | 0x0056C570 |
| FUN_0056C5C0 | ShipSubsystem__AddChildSubsystem | 0x0056C5C0 |
| FUN_005634C0 | PowerSubsystem__GetMainBatteryLimit | 0x005634C0 |
| FUN_005634D0 | PowerSubsystem__GetBackupBatteryLimit | 0x005634D0 |
| FUN_005B3FB0 | Ship__SetupProperties | 0x005B3FB0 |
| FUN_005B3E20 | Ship__LinkAllSubsystemsToParents | 0x005B3E20 |
| FUN_005B3E50 | Ship__AddSubsystemToLists | 0x005B3E50 |
| FUN_005B5030 | Ship__LinkSubsystemToParent | 0x005B5030 |
| FUN_006CF9B0 | TGBufferStream_swig_GetPos | 0x006CF9B0 |

`PowerSubsystem__WriteState` at 0x005644B0 was already named.

### Function created this pass

`PowerSubsystem__ReadState` at **0x00564530** was previously undefined in Ghidra
(only a DATA xref from PowerSubsystem vtable @ 0x0088A264 + 0x74). Ghidra needed an
explicit `create_function` to recover the body. Now named and plated.

### Plate comments installed

- `Ship__SetupProperties` (0x005B3FB0) — full property-type-ID → ship-slot table (12 mappings).
- `Ship__LinkSubsystemToParent` (0x005B5030) — child-type-ID → parent-slot table including the engine EP_IMPULSE/EP_WARP fork.
- `ShipSubsystem__WriteState` (0x0056D320) — wire-format spec.
- `PoweredSubsystem__WriteState` (0x00562960) — wire-format spec including isOwnShip branch.
- `PowerSubsystem__WriteState` (0x005644B0) — wire-format spec including UNCONDITIONAL-battery note.
- `PowerSubsystem__ReadState` (0x00564530) — wire-format spec (post-creation).
- `Ship__WriteStateUpdate` (0x005B17F0) — flag 0x20 round-robin spec inherited from mid #8.

## Implications for Dedicated Server

1. **Ship+0x284 must have identical order on server and client** — both must run the
   same hardpoint file, which they do (checksum-verified).
2. **The server must have real subsystem objects** — DeferredInitObject handles this.
3. **The round-robin ensures all subsystems get updated** — over multiple ticks, every
   subsystem gets its health synchronized.
4. **Variable-length blocks** mean the receiver must read exactly the same WriteState
   format the sender wrote — subsystem vtable must match on both sides.
5. **No need for a fixed 33-slot array** — the wire format is self-describing via the
   startIndex + linked list walk + recursive children.

## Open Questions (documentation debt)

1. **Bridge handler `FUN_005B5240` (case 0x812E in SetupProperties)** — wire format and
   list placement unknown. Property type ID 0x812E is unaccounted for in the catalog above.
2. **`FUN_005B5280` (case 0x8145 in SetupProperties)** — purpose and slot unknown.
   Property type ID 0x8145 is outside the documented 0x812B-0x813F range.
3. **Sovereign-class byte sizes** — require the `sovereign.py` hardpoint file (lives on
   the client install only). Without it the example table cannot be re-anchored.

## Companions

- [stateupdate.md](stateupdate.md) — parent dispatch chain (opcode 0x1C, 8 dirty flags,
  serializer / receiver pair).
- [per-ship-subsystem-wire-format.md](per-ship-subsystem-wire-format.md) — per-ship
  subsystem catalogs (16 stock ships) referencing this doc's WriteState formats and
  named-slot table.
- [stream-primitives.md](stream-primitives.md) — SWIG TGBufferStream WriteBit / WriteByte /
  GetPos primitives consumed by all three WriteState formats.
- [wire-format-spec.md](wire-format-spec.md) — protocol hub; ship subsystem catalog
  cross-references this doc.
- [decompiled-functions.md](../engine/decompiled-functions.md) — engine-family anchor
  table covering Ship__WriteStateUpdate, Ship__ReadStateUpdate, and the WriteState
  vtable functions.
- [v5-validation-status.md](v5-validation-status.md) — campaign tracker (§6.11 details
  this pass's full evidence trail).
