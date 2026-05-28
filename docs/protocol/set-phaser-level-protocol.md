> [docs](../README.md) / [protocol](README.md) / set-phaser-level-protocol.md

---
title: SetPhaserLevel Wire Format (Opcode 0x12)
type: reference
audience: re-engineer
validated: 2026-05-28
methodology: FUNCTION_DOC_WORKFLOW_V5
binary:
  name: stbc.exe
  size: 6394712
  base: 0x00400000
status: verified
evidence:
  - claim: "Opcode 0x12 dispatches to FUN_0069FDA0 (generic event-forward) via jump-table slot at 0x0069F3C7"
    address: 0x0069F3C7
    function: MpgameHandleMessage
    completeness: high
    confidence: high
    note: "Index = (opcode - 2) = 0x10. Case body: `PUSH 0; PUSH ESI; MOV ECX,EDI; CALL FUN_0069FDA0`. PUSH 0 = no event-type override (opcode 0x12 keeps its on-wire type 0x008000E0)."
  - claim: "Total wire size = 18 bytes (1 opcode + 16 TGEvent base + 1 char_value)"
    address: 0x006D6940
    function: TGCharEvent__WriteToStream
    completeness: medium
    confidence: high
    note: "WriteToStream body (CREATED this pass) calls base FUN_006D6130 (writes 4B factoryID + 4B eventType + 4B sourceRef + 4B targetRef = 16B), then WriteByte for event+0x28 (1B). 32-byte function body."
  - claim: "Event type 0x008000E0 ET_SET_PHASER_LEVEL — anchored at 3 xref sites"
    address: 0x008000E0
    function: (data constant)
    completeness: high
    confidence: high
    note: "3 xrefs: 0x00573E81 (PhaserSystem handler-table registration), 0x0069E9C3 (MultiplayerGame_Ctor MP-bridge registration), 0x00574247 (PhaserSystem__SetPowerLevel emit site)."
  - claim: "TGCharEvent factory ID = 0x105 (returned by GetFactoryID at vtable+0x04)"
    address: 0x00574C40
    function: TGCharEvent__GetFactoryID
    completeness: medium
    confidence: high
    note: "Body bytes `B8 05 01 00 00 C3` = MOV EAX, 0x105; RET. Still FUN-named (vtable callback, never entered by analyzer)."
  - claim: "TGCharEvent IsA chain returns true for {0x105, 0x101, 0x02}"
    address: 0x00574C50
    function: TGCharEvent__IsA
    completeness: high
    confidence: high
    note: "Three exact branches: `B8 05 01` (0x105 self), `B8 01 01` (0x101 TGEvent), CMP 0x02 (TGObject). 0x101 is TGEvent itself — there is no intermediate `TGSubsystemEvent` (zero string hits binary-wide). 0x02 is TGObject."
  - claim: "TGCharEvent class size = 0x2C bytes; +0x28 = char_value (BYTE, not int)"
    address: 0x00574C20
    function: TGCharEvent__Ctor
    completeness: high
    confidence: high
    note: "Ctor calls TGEvent base ctor, sets vtable = 0x008932DC, writes `(byte)0` to +0x28. Sibling TGObjPtrEvent uses +0x28 as object-pointer (4 bytes); TGCharEvent overlays just 1 byte at the same offset with 3 bytes of struct padding. See [tgobjptrevent-class.md](tgobjptrevent-class.md) for the sibling class."
  - claim: "TGCharEvent vtable at 0x008932DC (16 slots, byte-verified)"
    address: 0x008932DC
    function: (vtable data)
    completeness: high
    confidence: high
    note: "All 16 slots verified bytewise against the doc's vtable table. Slots +0x24/+0x28/+0x2C return SWIG triple-strings; slot +0x34 (WriteToStream) and +0x38 (ReadFromStream) are CREATED this pass."
  - claim: "Sender thunk MultiplayerGame::SetPhaserLevelHandler at 0x006A1970 (CREATED this pass)"
    address: 0x006A1970
    function: MultiplayerGame__SetPhaserLevelHandler
    completeness: medium
    confidence: high
    note: "34-byte body: `8B 54 24 04 8B 42 0C 85 C0 74 14 8B 40 40 56 8B 71 54 3B C6 5E 75 08 6A 12 52 E8 31 FE FF FF C2 04 00`. Gate: event->source (+0x0C) != NULL AND event->source->objectID (+0x40) == this->localPlayerObjID (+0x54), then `PUSH 0x12; PUSH event; CALL SendEventMessage (0x006A17C0)`. Was undefined-in-DB (DATA-only xref from 0x0069F19D)."
  - claim: "Gate compares source->objectID (+0x40) against MultiplayerGame->localPlayerObjID (+0x54)"
    address: 0x006A197D
    function: MultiplayerGame__SetPhaserLevelHandler
    completeness: medium
    confidence: high
    note: "`8B 40 40` (MOV EAX, [EAX+0x40]) reads source objectID; `8B 71 54` (MOV ESI, [ECX+0x54]) reads local player objID; `3B C6` (CMP EAX, ESI) gates the forward."
  - claim: "Applier PhaserSystem::SetPhaserLevelHandler at 0x00574180 (CREATED this pass) does NOT cascade to child EnergyWeapon subsystems"
    address: 0x00574180
    function: PhaserSystem__SetPhaserLevelHandler
    completeness: medium
    confidence: high
    note: "23-byte body: `8B 44 24 04 50 0F BE 50 28 89 91 F0 00 00 00 E8 4C 4F 16 00 C2 04 00`. Sign-extends event+0x28 (`0F BE 50 28` = MOVSX EDX, [EAX+0x28]), stores to this+0xF0, releases via FUN_006D90E0. NO loop, NO vtable+0x90 call on children — asymmetric with sender. Was undefined-in-DB (DATA-only xref from 0x00573E21)."
  - claim: "Sender PhaserSystem::SetPowerLevel at 0x00574200 DOES cascade level to child EnergyWeapon subsystems"
    address: 0x00574200
    function: PhaserSystem__SetPowerLevel
    completeness: medium
    confidence: high
    note: "Allocates 0x2C bytes via FUN_00717b70 + TGCharEvent::ctor, sets event+0x28 = level, posts via TGEventManager__PostEvent. Then loops this+0x1C children: GetChildSubsystem (0x0056C570), dynamic_cast<EnergyWeapon> (0x00570B20), call child->SetPowerSetting via vtable+0x90 (slot 36). Stores level at this+0xF0 last."
  - claim: "SendEventMessage uses 1023-byte stack buffer + TGMessage alloc size 0x40 + reliable flag at msg+0x3A"
    address: 0x006A17C0
    function: MultiplayerGame__SendEventMessage
    completeness: medium
    confidence: high
    note: "Allocates TGMessage(0x40), sets msg+0x3A = 1 (reliable). Branches on DAT_0097fa8a (IsMultiplayer): SendToGroup with `\"NoMe\"` (0x008E5528) vs SendTGMessage to host peer."
  - claim: '"NoMe" relay group string at 0x008E5528'
    address: 0x008E5528
    function: (data string)
    completeness: high
    confidence: high
    note: 'Bytes `4E 6F 4D 65 00` = "NoMe". Used by SendEventMessage when IsMultiplayer to fan out to all peers (sender is excluded by SetTo logic in the group manager).'
  - claim: '"Forward" relay group string at 0x008D94A0 (sender removed before relay, re-added after)'
    address: 0x008D94A0
    function: (data string)
    completeness: high
    confidence: high
    note: 'Bytes `46 6F 72 77 61 72 64 00` = "Forward". Used by FUN_0069FDA0 receiver path: looks up group in TGWinsockNetwork+0xF4, removes sender, forwards, re-adds sender.'
  - claim: "Universal SWIG triple-string pattern: GetClassName/GetSWIGName/GetPtrName"
    address: 0x008E54D0
    function: (data strings)
    completeness: high
    confidence: high
    note: '0x008E54D0 = "TGCharEvent", 0x008E54DC = "_p_TGCharEvent", 0x008E54EC = "TGCharEventPtr". Vtable slots +0x24/+0x28/+0x2C return these in order. Same triple-string convention applies across all SWIG-bound TG classes.'
  - claim: "Bidirectional 1:1 relay (5 C->S / 5 S->C observed in relay-audit-20260224)"
    address: null
    function: (cross-source)
    completeness: high
    confidence: high
    note: "Negative-relay claim. Cross-anchored against network-protocol-analyst relay-audit memory (2026-02-24). Confirms doc's 'bidirectional, relayed by host' classification — host relays to all OTHER clients (sender excluded via Forward group SetTo)."
companions:
  - docs/protocol/tgobjptrevent-class.md
  - docs/protocol/pythonevent-wire-format.md
  - docs/protocol/wire-format-spec.md
  - docs/protocol/game-opcodes.md
  - docs/protocol/tgmessage-routing.md
  - docs/engine/event-system-architecture.md
  - docs/gameplay/weapon-firing-mechanics.md
  - docs/protocol/v5-validation-status.md
supersedes:
  - (prior pre-v5)
---

# Opcode 0x12 — SetPhaserLevel Protocol Analysis

> [!NOTE]
> This doc is `status: verified`. All load-bearing claims confirmed byte-by-byte against
> the current Ghidra import (2026-05-28). Opcode 0x12 routes to `FUN_0069FDA0` via the
> jump table at `0x0069F3C7`; the 18-byte wire format (1 opcode + 16 TGCharEvent base +
> 1 char_value) is verified end-to-end; TGCharEvent class layout matches sibling
> TGObjPtrEvent (size 0x2C, +0x28 = `char` not `int`); event type `0x008000E0`
> ET_SET_PHASER_LEVEL is anchored at 3 xref sites. Three minor corrections in this pass:
> **(C1)** hierarchy cascade from mid #13 / leaf #14 — there is no `TGSubsystemEvent`; 0x101
> IS TGEvent itself. **(C2)** registration-string typography: the binary string is
> `"MultiplayerGame :: SetPhaserLevelHandler"` (single colon-colon with surrounding spaces);
> Ghidra's symbol-name mangler renders the spaces and colons as underscores. **(C3)**
> `FUN_006d6200` is already renamed `TGFactory_DeserializeObject` in the Ghidra DB. Four
> functions were newly created in Ghidra this pass (sender thunk, applier, WriteToStream,
> ReadFromStream — all were undefined because their xrefs are DATA-only from registration
> tables and vtables). See [docs/guides/v5-evidence-header.md](../guides/v5-evidence-header.md)
> for the standard.

Complete decompilation and wire format analysis of the phaser power level network message
(opcode 0x12) in Star Trek: Bridge Commander multiplayer.

## Overview

Opcode 0x12 (SetPhaserLevel) carries a phaser beam intensity change from the originating
player to all other peers. This controls the LOW/MEDIUM/HIGH phaser power toggle — **not**
the engineering power distribution sliders (which use a separate mechanism). The message
contains a serialized `TGCharEvent` (factory ID `0x105`) with a single payload byte
representing the power level.

**Direction**: Bidirectional (any peer → all other peers, relayed by host) [v5-validated 2026-05-28]
**Sender thunk**: `MultiplayerGame::SetPhaserLevelHandler` at `0x006A1970` [v5-validated 2026-05-28]
**Serializer**: `SendEventMessage` at `0x006A17C0` [v5-validated 2026-05-28]
**Receiver**: `FUN_0069fda0` (generic event forward, shared with opcodes 0x07-0x11, 0x1B)
**Applier**: `PhaserSystem::SetPhaserLevelHandler` at `0x00574180` [v5-validated 2026-05-28]
**Frequency**: infrequent (relay-audit observed 10 events in 21min, 2-player) `[low-confidence — session-dependent]`

## Wire Format

### Complete Packet Layout [v5-validated 2026-05-28]

```
Offset  Size  Type    Field                    Notes
------  ----  ----    -----                    -----
0       1     u8      opcode                   Always 0x12
1       4     i32     factory_id               Always 0x00000105 (TGCharEvent factory)
5       4     i32     event_type               Always 0x008000E0 (ET_SET_PHASER_LEVEL)
9       4     i32     source_object_ref        Object ID of the ship (or 0 for NULL)
13      4     i32     target_object_ref        Related object ref (-1 for sentinel, 0 for NULL)
17      1     u8      phaser_level             Power level: 0=LOW, 1=MEDIUM, 2=HIGH
```

**Total size**: 18 bytes (fixed — no variable-length fields).

All multi-byte values are **little-endian**.

### Serialization Detail

The payload is produced by `SendEventMessage` (`0x006A17C0`):

1. Writes the opcode byte (0x12) as a raw byte prefix
2. Calls `TGCharEvent::WriteToStream` (vtable+0x34 at `0x006D6940`), which:
   a. Calls base `TGEvent::WriteToStream` (`0x006D6130`):
      - `WriteInt32(GetFactoryID())` → 0x105
      - `WriteInt32(event+0x10)` → event type `0x008000E0`
      - `WriteObjectRef(event+0x08)` → source object reference
      - `WriteObjectRef(event+0x0C)` → target/related object reference
   b. Appends `WriteByte(event+0x28)` → the phaser level byte

### Object Reference Encoding

The `WriteObjectRef` function handles three cases:

- **NULL object**: writes `0x00000000`
- **Sentinel value** (`0x0095ADFC`): writes `0xFFFFFFFF` (-1)
- **Valid object**: writes the object's ID from `obj+0x40`

### Phaser Power Level Values

| Value | Constant | Python API | Effect |
|-------|----------|------------|--------|
| 0 | PP_LOW | `App.PhaserSystem.PP_LOW` | Low intensity — less damage, lower power draw |
| 1 | PP_MEDIUM | `App.PhaserSystem.PP_MEDIUM` | Medium intensity — balanced |
| 2 | PP_HIGH | `App.PhaserSystem.PP_HIGH` | High intensity — more damage, higher power draw |

These values are stored as a single byte on the wire (`event+0x28`) and as an `int` in the
PhaserSystem object (`PhaserSystem+0xF0`).

### Example Packet Decode

**SetPhaserLevel to HIGH** (18 bytes):

```
12                    opcode = 0x12 (SetPhaserLevel)
05 01 00 00           factory_id = 0x00000105 (TGCharEvent)
E0 00 80 00           event_type = 0x008000E0 (ET_SET_PHASER_LEVEL)
FF FF FF 3F           source_obj_ref = 0x3FFFFFFF (Player 0 ship)
00 00 00 00           target_obj_ref = NULL
02                    phaser_level = 2 (PP_HIGH)
```

**SetPhaserLevel to LOW** (18 bytes):

```
12                    opcode = 0x12 (SetPhaserLevel)
05 01 00 00           factory_id = 0x00000105 (TGCharEvent)
E0 00 80 00           event_type = 0x008000E0 (ET_SET_PHASER_LEVEL)
FF FF 03 40           source_obj_ref = 0x400003FF (Player 1 ship)
00 00 00 00           target_obj_ref = NULL
00                    phaser_level = 0 (PP_LOW)
```

## TGCharEvent Class Layout (0x2C bytes) [v5-validated 2026-05-28]

```
Offset  Size  Type           Field               Notes
------  ----  ----           -----               -----
0x00    4     void**         vtable               0x008932DC
0x04    4     int            ni_refcount          NiObject reference count
0x08    4     void*          source_object        Source object ptr (ship that changed level)
0x0C    4     void*          related_object       Related object ptr (typically NULL)
0x10    4     uint32         event_type           0x008000E0 (ET_SET_PHASER_LEVEL)
0x14    4     float          time_stamp           Event timestamp (-1.0f initially)
0x18    2     uint16         flags_a              Event flags
0x1A    2     uint16         flags_b              Ref tracking flags
0x1C    4     void*          (reserved)
0x20    4     void*          (reserved)
0x24    4     void*          parent_event         Cleared to 0 on receive
0x28    1     char           phaser_level         Power level: 0, 1, or 2
0x29-2B 3     -              padding              Struct padding to 0x2C
```

Fields `+0x14` through `+0x24` are inherited from the TGEvent base and are not modified by
TGCharEvent — these are listed for completeness but were not independently re-anchored this
pass (the byte that matters for SetPhaserLevel is `+0x28`).

### Class Hierarchy (Corrected — C1)

> [!NOTE]
> Previous versions of this doc depicted an intermediate `TGSubsystemEvent (factory 0x101)`
> class. That class **does not exist** — `0x101` is the factory ID of `TGEvent` itself
> (confirmed: zero occurrences of the string `"TGSubsystemEvent"` in stbc.exe). The
> previous "factory 0x02 size 0x28" annotation for TGEvent was also wrong: 0x02 is the
> TGObject class ID (a separate ancestor in the IsA chain), not a factory ID. See mid #13
> [tgobjptrevent-class.md](tgobjptrevent-class.md) and leaf #14
> [pythonevent-wire-format.md](pythonevent-wire-format.md) for the originating fix.

```
NiObject
  └── TGObject (class ID 0x02)
        └── TGEvent (factory 0x101, ~size 0x28)
              ├── TGCharEvent (factory 0x105, size 0x2C)
              └── TGObjPtrEvent (factory 0x10C, size 0x2C)
```

`TGCharEvent` adds a single `char` field at `+0x28` to the base `TGEvent` layout. This
field carries the phaser level value (or any other single-byte event payload — the class
is generic, reused by multiple subsystem events). Its sibling `TGObjPtrEvent` overlays the
same `+0x28` slot with a 4-byte object pointer; the class size is identical (0x2C) because
TGCharEvent reserves 3 bytes of struct padding after the single byte.

### Constructor (`0x00574C20`) [v5-validated 2026-05-28]

```
this = TGEvent::ctor(this, 0)          // base init
this->vtable = 0x008932DC             // TGCharEvent vtable
this->charValue = 0                   // +0x28 = 0 (default)
```

### SWIG Factory Registration

The factory for `TGCharEvent` (ID `0x105`) is registered in the event factory hash table,
allowing `TGFactory_DeserializeObject` (`0x006D6200`, renamed in Ghidra DB; formerly
documented as `ReadObjectFromStream`) to construct it from the factory ID on the wire.

### IsA Chain [v5-validated 2026-05-28]

`TGCharEvent::IsA(id)` (vtable+0x08 at `0x00574C50`) returns true for:

| ID | Class | Source |
|----|-------|--------|
| `0x105` | TGCharEvent | self |
| `0x101` | TGEvent | base — `0x101` is TGEvent's factory ID; there is no intermediate class |
| `0x02` | TGObject | NiObject→TGObject→TGEvent ancestor (class ID, not factory ID) |

Byte evidence at `0x00574C50`: three branches `B8 05 01 00 00` (MOV EAX, 0x105), `B8 01 01 00 00`
(MOV EAX, 0x101), and a `CMP` against `0x02`. No `0x100`-range "subsystem event" check exists.

## Sender Flow

### Local Action: PhaserSystem::SetPowerLevel (`0x00574200`) [v5-validated 2026-05-28]

When the player toggles phaser intensity (key press or UI action):

```
PhaserSystem::SetPowerLevel(int level):
  1. Allocate TGCharEvent (NiAlloc 0x2C bytes via FUN_00717b70)
  2. Call TGCharEvent::ctor (0x00574C20)
  3. Set event+0x28 = (byte)level                    // the power level
  4. Set event source to this PhaserSystem            // FUN_006d62b0
  5. Set event+0x10 = 0x008000E0                      // ET_SET_PHASER_LEVEL
  6. Post event to event system                       // TGEventManager::PostEvent (0x006da2a0)
  7. Loop over child subsystems (this+0x1C = count):
     a. Get child at index i (FUN_0056c570)
     b. dynamic_cast<EnergyWeapon*>(child) via FUN_00570b20
     c. If cast succeeds: call child->SetPowerSetting(level)
        via vtable+0x90 (vtable slot 36)
  8. Store level at PhaserSystem+0xF0
```

The sender **immediately applies** the level to all child EnergyWeapon subsystems and
stores it locally. The event post in step 6 triggers the multiplayer handler (below) to
serialize and send it to other peers.

### Multiplayer Bridge: SetPhaserLevelHandler Thunk (`0x006A1970`) [v5-validated 2026-05-28]

The MultiplayerGame object registers a handler for event `0x008000E0`. When the event
fires (from step 6 above), this 34-byte thunk decides whether to forward it over the
network:

```
MultiplayerGame::SetPhaserLevelHandler(TGCharEvent* event):
  1. If event->source == NULL: return (ignore)
  2. If event->source->objectID != this->localPlayerObjectID: return
     (only forward OUR events — prevents re-broadcasting received events)
  3. Call SendEventMessage(event, 0x12)
```

**Gate check at `this+0x54`**: The handler reads the source object's ID from `source+0x40`
and compares it against `MultiplayerGame+0x54` (the local player's object ID). This
ensures only locally-originated events are sent over the network.

### SendEventMessage (`0x006A17C0`) [v5-validated 2026-05-28]

```
SendEventMessage(TGEvent* event, byte opcode):
  1. Store opcode byte in local buffer
  2. Create TGBufferStream wrapping a 1023-byte stack buffer
  3. Call event->WriteToStream(stream) via vtable+0x34
  4. Get stream position (bytes written)
  5. Allocate TGMessage (NiAlloc 0x40 bytes)
  6. Copy data into message: [opcode_byte][stream_data] (total = position + 1)
  7. Mark message as reliable (msg+0x3A = 1)
  8. If IsMultiplayer (DAT_0097fa8a): SendTGMessageToGroup("NoMe" @ 0x008E5528)
     Else: SendTGMessage to host peer
```

## Receiver Flow

### Jump Table Dispatch [v5-validated 2026-05-28]

The `MultiplayerGame` dispatcher at `0x0069F2A0` reads the opcode byte (0x12), subtracts 2
to get jump table index 0x10, and jumps to case `0x0069F3C7`. This case is shared with
opcodes 0x0B, 0x0C, and 0x11:

```asm
push  0x0              ; event type override = 0 (use event's own type)
push  esi              ; TGMessage*
call  FUN_0069fda0     ; generic event forward
```

**No event type override**: Unlike opcodes 0x07-0x0A (which override the event type on
receive), opcode 0x12 passes `0` for the override parameter. The event arrives and is
posted with its original type `0x008000E0`. This is because `ET_SET_PHASER_LEVEL` has
no sender/receiver code pairing — the same event code is used on both sides.

### Generic Event Forward: FUN_0069fda0

This handler processes all event-forward opcodes (0x07-0x12, 0x1B). For opcode 0x12:

```
FUN_0069fda0(TGMessage* msg, int eventTypeOverride):
  --- HOST RELAY ---
  1. If IsMultiplayer:
     a. Clone/extract message data
     b. Look up "Forward" group in TGWinsockNetwork+0xF4 (string @ 0x008D94A0)
     c. Remove sender from "Forward" group (prevent echo back)
     d. Forward message to all remaining group members
     e. Re-add sender to "Forward" group

  --- LOCAL DISPATCH ---
  2. If sender != self:
     a. Extract message buffer via FUN_006b8530
     b. Create TGBufferStream, init with buffer+1 (skip opcode byte)
     c. Deserialize event from stream via TGFactory_DeserializeObject (0x006D6200):
        - Read factory ID (0x105) → look up TGCharEvent factory
        - Allocate TGCharEvent (0x2C bytes)
        - Call TGCharEvent::ReadFromStream (vtable+0x38 at 0x006D6960)
     d. Resolve object references (FUN_006f13c0)
     e. Clear event+0x24 (parent event pointer)
     f. If eventTypeOverride != 0: set event+0x10 = override
        (For 0x12: override is 0, so event keeps its original 0x008000E0)
     g. Post event to local event system (TGEventManager::PostEvent w/ auto-release, 0x006da300)
```

### Applier: PhaserSystem::SetPhaserLevelHandler (`0x00574180`) [v5-validated 2026-05-28]

The locally-posted event triggers the PhaserSystem's handler. The full 23-byte body:

```
PhaserSystem::SetPhaserLevelHandler(TGCharEvent* event):
  1. Read event+0x28 as signed byte → sign-extend to int (MOVSX EDX, [EAX+0x28])
  2. Store into PhaserSystem+0xF0
  3. Release event (FUN_006D90E0)
```

**Critical asymmetry**: The receiver does **NOT** call `SetPowerSetting()` on child
EnergyWeapon subsystems. It only stores the level value. The actual intensity change on
remote machines propagates through a different mechanism — either the `PhaserSystem::Update()`
tick reads `+0xF0` and applies it, or individual weapon intensity values are carried in
`StateUpdate` (opcode 0x1C) serialization. There is no loop and no vtable+0x90 call in
the applier body (verified bytewise this pass).

## Event Type Codes

| Code | Name | Used By |
|------|------|---------|
| `0x008000E0` | ET_SET_PHASER_LEVEL | Both sender and receiver (no pairing) |

**No event code pairing**: Most event-forward opcodes have a sender/receiver code pair
(e.g., StartFiring uses `0xD8` locally, `0xD7` on receive). SetPhaserLevel is simpler — the
same code `0x008000E0` is used on both sides, and the generic forward handler passes
`override = 0` (no override). The event has exactly 3 xrefs in the binary: the PhaserSystem
handler-table registration (`0x00573E81`), the MultiplayerGame ctor MP-bridge registration
(`0x0069E9C3`), and the `SetPowerLevel` emit site (`0x00574247`).

## Shared Handler Group

Opcode 0x12 shares `FUN_0069fda0` with these other opcodes:

| Opcode | Name | Event Override | Override Code |
|--------|------|----------------|---------------|
| 0x07 | StartFiring | Yes | `0x008000D7` |
| 0x08 | StopFiring | Yes | `0x008000D9` |
| 0x09 | StopFiringAtTarget | Yes | `0x008000DB` |
| 0x0A | SubsystemStatusChanged | Yes | `0x0080006C` |
| 0x0B | AddToRepairList | No | 0 |
| 0x0C | ClientEvent | No | 0 |
| 0x0E | StartCloaking | Yes | `0x008000E3` |
| 0x0F | StopCloaking | Yes | `0x008000E5` |
| 0x10 | StartWarp | Yes | `0x008000ED` |
| 0x11 | RepairListPriority | No | 0 |
| **0x12** | **SetPhaserLevel** | **No** | **0** |
| 0x1B | TorpedoTypeChange | Yes | `0x008000FD` |

Opcodes with `override = 0` use the event's own type code from the wire. Opcodes with an
override replace the deserialized event's type before posting locally — this implements the
sender/receiver event code pairing.

## Event Registration

### PhaserSystem (registered in `FUN_00573DE0` + `FUN_00573E40`) [v5-validated 2026-05-28]

```
Handler: PhaserSystem::SetPhaserLevelHandler (0x00574180)
Trigger: ET_SET_PHASER_LEVEL (0x008000E0)
Registration: FUN_006d92b0 with name "PhaserSystem::SetPhaserLevelHandler" (@ 0x008E5440)
```

The registration string at `0x008E5440` is the exact byte sequence
`"PhaserSystem::SetPhaserLevelHandler"` — no spaces, single double-colon.

### MultiplayerGame (registered in ctor at `0x0069E9C3`) [v5-validated 2026-05-28]

```
Handler: MultiplayerGame::SetPhaserLevelHandler thunk (0x006A1970)
Trigger: ET_SET_PHASER_LEVEL (0x008000E0)
Registration: FUN_006db380 with name "MultiplayerGame :: SetPhaserLevelHandler" (@ 0x00959F1C)
Flags: priority=1, enabled=1
```

> [!NOTE]
> **C2 — registration-string typography.** The binary string at `0x00959F1C` is
> `"MultiplayerGame :: SetPhaserLevelHandler"` — single double-colon with **spaces**
> on both sides. Ghidra's auto-generated symbol name renders this as
> `s_MultiplayerGame____SetPhaserLeve_00959f1c` because the label-name mangler encodes
> spaces and colons as underscores; the underlying string is the spaced form. Previous
> versions of this doc carried the mangled `"MultiplayerGame::__SetPhaserLevelHandler"`
> form — that was the Ghidra symbol, not the binary string.

Both handlers fire for the same event type. The MultiplayerGame handler serializes and sends
over the network; the PhaserSystem handler applies the level locally. On the sender side,
both fire. On the receiver side, only the PhaserSystem handler fires (because the MP handler's
gate check rejects events from non-local sources).

## Related Functions [v5-validated 2026-05-28]

| Address | Name | Role |
|---------|------|------|
| `0x00574200` | `PhaserSystem__SetPowerLevel` | Local action: creates event, applies to weapons, stores level |
| `0x00574180` | `PhaserSystem__SetPhaserLevelHandler` | Receiver: stores level byte from event into +0xF0 (CREATED this pass) |
| `0x006A1970` | `MultiplayerGame__SetPhaserLevelHandler` | MP sender thunk: gates on local player, calls SendEventMessage (CREATED this pass) |
| `0x006A17C0` | `MultiplayerGame__SendEventMessage` | Serializes event + opcode into TGMessage, sends reliably |
| `0x0069fda0` | `MultiplayerGame::GenericEventForward` | Receive-side: relay to "Forward" group + deserialize + post locally |
| `0x0069F2A0` | `MultiplayerGame::ReceiveMessage` | Jump table dispatcher (opcode-2 indexed) |
| `0x006D6940` | `TGCharEvent__WriteToStream` | Network serialization (base + charValue byte) — CREATED this pass |
| `0x006D6960` | `TGCharEvent__ReadFromStream` | Network deserialization (base + charValue byte) — CREATED this pass |
| `0x006D6130` | `TGEvent::WriteToStream` | Base event serialization (factoryID, type, source, target) |
| `0x006D61C0` | `TGEvent::ReadFromStream` | Base event deserialization |
| `0x006D6200` | `TGFactory_DeserializeObject` | Factory-based event construction from stream (formerly documented as `ReadObjectFromStream`) |
| `0x006DA2A0` | `EventManager::PostEvent` | Posts event for handler dispatch |
| `0x006DA300` | `EventManager::PostEvent (auto-release)` | Posts event with automatic reference release |
| `0x006D90E0` | `EventManager::ReleaseEvent` | Releases/frees an event object |
| `0x00574C20` | `TGCharEvent__Ctor` | Constructor (allocates 0x2C bytes, sets vtable) |
| `0x00574CB0` | `TGCharEvent::scalar_deleting_dtor` | Destructor |
| `0x00570B20` | `dynamic_cast<EnergyWeapon>` | IsA check for factory `0x802C` |
| `0x0056C570` | `GetChildSubsystem` | Returns child subsystem at index |

## TGCharEvent Vtable Map (`0x008932DC`) [v5-validated 2026-05-28]

All 16 slots verified bytewise against the table below.

| Offset | Target | Name |
|--------|--------|------|
| +0x00 | `0x00574CB0` | scalar_deleting_dtor |
| +0x04 | `0x00574C40` | GetFactoryID → returns 0x105 |
| +0x08 | `0x00574C50` | IsA(id) → true for 0x105, 0x101, 0x02 |
| +0x0C | `0x006F1650` | (inherited from NiObject) |
| +0x10 | `0x006D6980` | WriteStream (persistence) |
| +0x14 | `0x006D69B0` | ReadStream (persistence) |
| +0x18 | `0x006D6050` | ReadClassName (inherited) |
| +0x1C | `0x006D60B0` | WriteClassName (inherited) |
| +0x20 | `0x006F15C0` | (inherited from NiObject) |
| +0x24 | `0x00574C80` | GetClassName → "TGCharEvent" (`0x008E54D0`) |
| +0x28 | `0x00574C90` | GetSWIGName → "_p_TGCharEvent" (`0x008E54DC`) |
| +0x2C | `0x00574CA0` | GetPtrName → "TGCharEventPtr" (`0x008E54EC`) |
| +0x30 | `0x006D6920` | CopyFrom (copies base fields + charValue) |
| +0x34 | `0x006D6940` | WriteToStream (network — base + WriteByte) — CREATED this pass |
| +0x38 | `0x006D6960` | ReadFromStream (network — base + ReadByte) — CREATED this pass |
| +0x3C | `0x005750E0` | PostProcess / destructor chain |

## Ghidra Annotations Applied [v5-validated 2026-05-28]

This validation pass made the following annotations against the Ghidra DB. The four CREATED
functions all had valid prologues but no defined function in the DB — their xrefs are
DATA-only (vtable slots and handler-table registration entries), so the analyzer never
entered them. This is the same systematic pattern observed on leaves #13, #14, and #15
(TGObjPtrEvent, PythonEvent, CollisionEffect): SWIG vtable callbacks and event-table-registered
handlers stay undefined until manually created.

### Functions Created

| Address | Name | Size | Reason |
|---------|------|------|--------|
| `0x006A1970` | `MultiplayerGame__SetPhaserLevelHandler` | 34 bytes | Undefined-in-DB; xref `0x0069F19D` from MultiplayerGame ctor handler registration was DATA-only |
| `0x00574180` | `PhaserSystem__SetPhaserLevelHandler` | 23 bytes | Undefined-in-DB; xref `0x00573E21` from `FUN_00573DE0` handler-table registration was DATA-only |
| `0x006D6940` | `TGCharEvent__WriteToStream` | 32 bytes | Undefined-in-DB; reached only via TGCharEvent vtable+0x34 (`0x008932DC`+0x34) |
| `0x006D6960` | `TGCharEvent__ReadFromStream` | 31 bytes | Undefined-in-DB; reached only via TGCharEvent vtable+0x38 (`0x008932DC`+0x38) |

### Functions Renamed

| Address | New Name |
|---------|----------|
| `0x00574200` | `PhaserSystem__SetPowerLevel` |
| `0x006A17C0` | `MultiplayerGame__SendEventMessage` |
| `0x00574C20` | `TGCharEvent__Ctor` |
| `0x00574C50` | `TGCharEvent__IsA` |

### Plate Comments

Four plate comments were added — one on each newly created function — tagged
`[v5-validated 2026-05-28]`. Each plate documents the gate logic (or absence thereof),
the vtable slot mapping, the wire-format size contributed by that function, and the
asymmetry between sender and receiver behavior.

## Open Questions

Two low-priority items remain after this pass:

1. **Frequency stat is session-dependent.** The doc previously claimed "~33 per 15-min
   stock session". Relay-audit-20260224 observed 10 events in 21 minutes on a 2-player
   session. These numbers are not contradictory — phaser-level toggles are a player input
   that varies widely by playstyle. The frequency line is now flagged
   `[low-confidence — session-dependent]`. Promotion path: if a multi-session corpus
   becomes available, replace with a min/max/median per minute.
2. **TGEvent base layout fields at `+0x14` / `+0x18` / `+0x1A` / `+0x1C` / `+0x20` / `+0x24`.**
   These are inherited from TGEvent and not modified by TGCharEvent, so they were not
   independently re-anchored this pass. The layout is consistent with the TGEvent class
   layout used by all 4 known subclasses (TGCharEvent, TGObjPtrEvent, PythonEvent, CollisionEvent),
   but a foundation-tier TGEvent doc would tighten the cross-anchor.

## See also

- [tgobjptrevent-class.md](tgobjptrevent-class.md) — sibling class (factory `0x10C`); same `+0x28` slot, different type (object pointer vs. byte)
- [pythonevent-wire-format.md](pythonevent-wire-format.md) — leaf #14; established the "0x101 = TGEvent itself" finding propagated here as C1
- [game-opcodes.md](game-opcodes.md) — hub index of all multiplayer opcodes
- [tgmessage-routing.md](tgmessage-routing.md) — relay topology used by `FUN_0069fda0`
- [event-system-architecture.md](../engine/event-system-architecture.md) — `TGEventManager` dispatch and handler-table internals
- [weapon-firing-mechanics.md](../gameplay/weapon-firing-mechanics.md) — downstream consumer of PhaserSystem+0xF0
- [v5-validation-status.md](v5-validation-status.md) — protocol-family validation tracker (§6.16)
