---
title: PythonEvent Wire Format (Opcodes 0x06 + 0x0D)
type: reference
audience: re-engineer
validated: 2026-05-28
methodology: FUNCTION_DOC_WORKFLOW_V5
binary:
  name: STBC.exe
  size: 6394712
  base: 0x00400000
status: partial
evidence:
  - claim: "Opcodes 0x06 (PythonEvent) and 0x0D (PythonEvent2) share a single receiver — no opcode-byte branch in the handler body"
    address: 0x0069f880
    function: MpgameHandlePythonEvent
    completeness: 22.14
    confidence: high
    note: "Dispatcher jump table at 0x0069F534 slots 6 and 13 both route here; receiver decompile never reads the opcode byte"
  - claim: "Receiver is LOCAL-ONLY dispatch — no SendToGroup, no relay"
    address: 0x0069f880
    function: MpgameHandlePythonEvent
    completeness: 22.14
    confidence: high
    note: "Confirms tgmessage-routing.md mid #7 LOCAL-ONLY classification. No outbound send call in the body"
  - claim: "TGEvent base wire size = 16-byte payload + 1 opcode byte = 17 bytes (factory_id u32 + event_type u32 + source_ref u32 + dest_ref u32)"
    address: 0x006D6130
    function: TGEvent_WriteToStream
    completeness: 80
    confidence: high
    note: "Decompile: 4 calls × 4-byte writes (vtable+0x64 ×2 for factory_id+event_type, vtable+0x84 ×2 for source+dest refs)"
  - claim: "TGCharEvent wire size = 17-byte payload + 1 opcode = 18 bytes (base + 1-byte char_value via WriteChar at vtable+0x54)"
    address: 0x006D6940
    function: TGCharEvent_WriteToStream
    completeness: 75
    confidence: high
    note: "Disasm shows base call followed by CALL [EAX+0x54] reading from this+0x28"
  - claim: "TGObjPtrEvent wire size = 20-byte payload + 1 opcode = 21 bytes (base + 4-byte obj_id via WriteInt at vtable+0x84)"
    address: 0x006D6DC0
    function: TGObjPtrEvent_WriteToStream
    completeness: 85
    confidence: high
    note: "Cross-anchor from tgobjptrevent-class.md (mid #13); already v5-plated"
  - claim: "ObjectExplodingEvent wire size = 24-byte payload + 1 opcode = 25 bytes (base + WriteInt firing_player + WriteFloat lifetime)"
    address: 0x0043F990
    function: ObjectExplodingEvent_WriteToStream
    completeness: 70
    confidence: high
    note: "Disasm: base call + vtable+0x6C (i32 firing_player from this+0x28) + vtable+0x74 (f32 lifetime from this+0x2C)"
  - claim: "0x101 IS TGEvent itself — no TGSubsystemEvent class exists in the binary"
    address: 0x006D5CE0
    function: TGEvent_GetFactoryID
    completeness: 95
    confidence: high
    note: "Decompile = MOV EAX,0x101; RET. Cascade from mid #13 C1. Vtable address 0x008932A4 (previously attributed to TGSubsystemEvent) has ZERO xrefs in the binary"
  - claim: "ObjectExplodingEvent::IsA returns true for {0x8129, 0x101, 0x02} — three IDs, not two"
    address: 0x0043F8F0
    function: ObjectExplodingEvent_IsA
    completeness: 65
    confidence: high
    note: "Disasm: CMP EAX,0x8129 then CMP EAX,0x101 then CMP EAX,0x2; the 0x101 branch confirms inheritance from TGEvent base"
  - claim: "WriteObjectRef encoding is ASYMMETRIC between source (this+0x08) and dest (this+0x0C) fields"
    address: 0x006D6130
    function: TGEvent_WriteToStream
    completeness: 80
    confidence: high
    note: "SOURCE: 2-case (NULL→0, else *(obj+4)). DEST: 3-case (sentinel→-1, NULL→0, else *(obj+4)). No path writes 0xFFFFFFFF to the source field"
  - claim: "Receiver Step 7 = TGEvent::Dispatch — event self-dispatches via event->dest_obj->vtable[+0x50]"
    address: 0x006DA300
    function: TGEvent_Dispatch
    completeness: 60
    confidence: high
    note: "Decompile shows event reads this+0x0C (dest_obj) and invokes dest_obj->vtable[+0x50](event). Not a global event manager PostEvent"
  - claim: "HostEventHandler (producer for 0x008000DF / 0x00800074 / 0x00800075) at 0x006A1150 serializes as opcode 0x06 to NoMe group"
    address: 0x006A1150
    function: null
    completeness: null
    confidence: high
    note: "Undefined in current Ghidra DB but raw disasm confirms: g_TGWinsockNetwork null-check at 0x97FA78, stack opcode-byte write of 0x06, TGAlloc(0x40), msg+0x3A=1 (reliable), SendTGMessageToGroup at 0x006B4DE0 with NoMe string at 0x008E5528"
  - claim: "ObjectExplodingHandler (producer for 0x0080004E) at 0x006A1240 has dual MP/SP path"
    address: 0x006A1240
    function: null
    completeness: null
    confidence: high
    note: "Undefined in current Ghidra DB. Raw disasm: MP path at 0x006A126A is byte-identical to HostEventHandler. SP path at 0x006A131B does FLD [event+0x2C]; FSTP [ship+0x14C]; CALL FUN_005AC250 (Python Effects.ObjectExploding)"
  - claim: "Event registration in MultiplayerGame_Ctor: HostEventHandler is host-gated; ObjectExplodingHandler is always-on with internal MP check"
    address: 0x0069E590
    function: MultiplayerGame_Ctor
    completeness: 70
    confidence: high
    note: "Decompile: 0x008000DF/0x00800074/0x00800075 → 0x006A1150 (gated on DAT_0097fa8a!=0). 0x0080004E → 0x006A1240 (unconditional registration; handler internally branches on g_IsMultiplayer)"
  - claim: "Stream vtable @ 0x00895C58 slot map confirms +0x60/+0x64/+0x6C/+0x70/+0x74 read/write 4 raw bytes each (NOT bit-packed)"
    address: 0x00895C58
    function: null
    completeness: null
    confidence: high
    note: "Raw memory dump (160 bytes) + per-slot decompile. +0x80/+0x84 are virtual dispatchers that thunk to +0x68/+0x6C in this SWIG class — effectively all int operations write 4 raw bytes"
  - claim: "ObjectExplodingEvent vtable at 0x0088A178 — 18-slot table confirmed"
    address: 0x0088A178
    function: null
    completeness: null
    confidence: high
    note: "Raw memory dump (80 bytes). Key slots: +0x04 GetFactoryID (→0x8129), +0x08 IsA, +0x24 GetClassName (→\"ObjectExplodingEvent\" at 0x008DA270), +0x34 WriteToStream (0x0043F990), +0x38 ReadFromStream (0x0043F9C0)"
companions:
  - docs/protocol/tgobjptrevent-class.md
  - docs/protocol/wire-format-spec.md
  - docs/protocol/transport-layer.md
  - docs/protocol/game-opcodes.md
  - docs/protocol/tgmessage-routing.md
  - docs/engine/event-system-architecture.md
  - docs/protocol/v5-validation-status.md
supersedes:
  - (prior pre-v5)
---

> [docs](../README.md) / [protocol](README.md) / pythonevent-wire-format.md

# Opcode 0x06 — PythonEvent Wire Format

Complete decompilation and wire format analysis of the PythonEvent network message
(opcode 0x06) in Star Trek: Bridge Commander multiplayer.

> [!NOTE]
> This doc is `status: partial`. The receiver dispatch (MpgameHandlePythonEvent at
> FUN_0069F880, shared by opcodes 0x06 + 0x0D), 2 producers (HostEventHandler at
> 0x006A1150 + ObjectExplodingHandler at 0x006A1240), event registration in
> MultiplayerGame_Ctor, and **wire formats byte-by-byte for ALL 4 event classes**
> (TGEvent 17 bytes / TGCharEvent 18 / TGObjPtrEvent 21 / ObjectExplodingEvent 25)
> are v5-validated against the current Ghidra import (2026-05-28). Five corrections
> landed — none change the wire-format byte counts:
>
> - **(C1)** "TGSubsystemEvent (0x101)" was a fabrication — 0x101 IS TGEvent itself
>   (cascade from mid #13). Inheritance hierarchy flattened to 3 siblings under
>   TGEvent.
> - **(C2)** ObjectExplodingEvent IsA chain is `{0x8129, 0x101, 0x02}` (not just
>   `{0x8129, 0x02}`); confirms cascade.
> - **(C3)** Source-vs-Dest WriteObjectRef encoding is ASYMMETRIC — source is 2-case
>   (no sentinel), dest is 3-case (with sentinel).
> - **(C4)** FUN_006DA300 is `TGEvent::Dispatch` (event self-dispatch via
>   dest_obj->vtable[+0x50]), not "EventManager::PostEvent".
> - **(C5)** ObjectExploding "size 0x30" is in-memory class size; "25 bytes" is wire
>   payload — both correct, prose clarified.
>
> See [docs/guides/v5-evidence-header.md](../guides/v5-evidence-header.md) for the
> standard.

## Overview

Opcode 0x06 (PythonEvent) is a **polymorphic serialized-event transport**. It carries
game events from the host to all clients, using a factory-based serialization system
where the first 4 bytes of the payload identify which event class follows. This is the
primary mechanism for broadcasting repair-list changes, explosion notifications, and
forwarded script events.

**Direction**: Host → All Clients (via "NoMe" routing group)
**Reliability**: Sent reliably (ACK required, `msg+0x3A = 1`)
**Frequency**: ~251 per 15-minute 3-player combat session (3,432 total observed in a
34-minute session — the most frequent game opcode)

Two distinct C++ producers generate opcode 0x06 messages
(`HostEventHandler` and `ObjectExplodingHandler`), each triggered by different event
types but using the same serialization pattern. The receiver is a single generic
handler that deserializes based on factory ID and dispatches locally — no relay.

### Opcode 0x0D (PythonEvent2)

Opcode 0x0D shares the same receiver function (`MpgameHandlePythonEvent` at
`0x0069F880`) and has identical wire format. The receiver body never reads the
opcode byte; the dispatcher jump table at `0x0069F534` slots 6 and 13 both route
here. In practice both opcodes are decoded identically. [v5-validated 2026-05-28]

## Inheritance Hierarchy (Corrected)

Five event classes participate in opcode 0x06 dispatch. The pre-v5 hierarchy named an
intermediate parent class `TGSubsystemEvent (factory 0x101)`; v5 validation shows
**0x101 IS TGEvent itself** — there is no `TGSubsystemEvent` class.

The TGEvent base's `GetFactoryID` at `0x006D5CE0` is exactly `MOV EAX, 0x101; RET`.
The vtable address previously attributed to `TGSubsystemEvent` (`0x008932A4`) has
**zero xrefs** in the binary — confirmed via `get_xrefs_to`. There is no constructor,
no RTTI string, no IsA branch, and no factory registration for any
`TGSubsystemEvent`. The pre-v5 doc cascaded the error from tgobjptrevent-class.md
(mid #13 C1).

The corrected hierarchy is flat — three siblings inherit directly from TGEvent base:

```
NiObject
  └── TGEvent (factory 0x101, vtable 0x00895FF4, size 0x28)
        ├── TGCharEvent (factory 0x105, vtable 0x008932DC, size 0x2C)
        │        [+1 byte char_value at this+0x28]
        ├── TGObjPtrEvent (factory 0x10C, vtable 0x0088869C, size 0x2C)
        │        [+4 byte obj_id at this+0x28]
        └── ObjectExplodingEvent (factory 0x8129, vtable 0x0088A178, size 0x30)
                 [+4 byte firing_player at this+0x28]
                 [+4 byte lifetime (float) at this+0x2C]
```

The four sibling IsA chains:

| Class | IsA returns true for | Confirmed at |
|-------|---------------------|--------------|
| TGEvent | `{0x101, 0x02}` | (base; emits factory_id 0x101 at 0x006D5CE0) |
| TGCharEvent | `{0x105, 0x101, 0x02}` | 0x00574C50 |
| TGObjPtrEvent | `{0x10C, 0x101, 0x02}` | 0x004032C0 |
| ObjectExplodingEvent | `{0x8129, 0x101, 0x02}` | 0x0043F8F0 |

ObjectExplodingEvent's IsA branch on `0x101` is the byte the pre-v5 doc missed (C2).
All four classes inherit from TGEvent base; ObjectExplodingEvent is NOT a direct
NiObject child as the pre-v5 diagram implied.

See [tgobjptrevent-class.md](tgobjptrevent-class.md) for the full mid #13
validation including the falsification details on the 0x008932A4 vtable address.

## Wire Format

### Message Structure [v5-validated 2026-05-28]

```
Offset  Size  Type    Field          Notes
------  ----  ----    -----          -----
0       1     u8      opcode         0x06 or 0x0D
1       4     i32     factory_id     Event class factory type ID (determines payload)
5       4     i32     event_type     Event type constant (0x008000xx)
9       4     i32     source_obj_id  Source object (NULL→0, else *(obj+4))
13      4     i32     dest_obj_id    Dest/related object (sentinel→-1, NULL→0, else *(obj+4))
[class-specific extension follows]
```

The first 17 bytes are common to all event classes (1-byte opcode + 16-byte
`TGEvent` base payload). The payload after byte 16 depends on `factory_id`.

All multi-byte values are **little-endian**. All int writes go through stream vtable
`+0x64`/`+0x84` which write 4 raw bytes (NOT bit-packed). See the
[Stream Vtable Slot Map](#stream-vtable-slot-map) below for the slot-by-slot
verification.

### Four Event Classes [v5-validated 2026-05-28]

| Factory ID | Class Name | Base bytes | Extension bytes | Payload total | Wire total |
|-----------|------------|-----------:|----------------:|--------------:|-----------:|
| `0x00000101` | TGEvent | 16 | 0 | 16 | 17 |
| `0x00000105` | TGCharEvent | 16 | 1 | 17 | 18 |
| `0x0000010C` | TGObjPtrEvent | 16 | 4 | 20 | 21 |
| `0x00008129` | ObjectExplodingEvent | 16 | 8 | 24 | 25 |

Each row was confirmed byte-by-byte from the corresponding `WriteToStream`
decompile (`0x006D6130`, `0x006D6940`, `0x006D6DC0`, `0x0043F990`).

### WriteObjectRef Encoding Asymmetry [v5-validated 2026-05-28]

`TGEvent::WriteToStream` at `0x006D6130` does NOT use a single uniform encoder for
both object-reference fields. The source field (`this+0x08`) and dest field
(`this+0x0C`) follow **different** encoding rules:

| Field | Offset (in-memory) | Cases | Wire encoding |
|-------|-------------------:|-------|---------------|
| **source_obj_id** | this+0x08 | 2-case | `NULL → 0`, else `*(obj+4)` |
| **dest_obj_id** | this+0x0C | 3-case | `sentinel ptr → 0xFFFFFFFF`, `NULL → 0`, else `*(obj+4)` |

The sentinel pointer compared in the dest field is at `DAT_0095ADFC` (also the
`0x3FFFFFFF` constant). The disasm of `0x006D6130` shows the source branch tests
only `EAX != 0`, while the dest branch tests `EAX == sentinel` first, then `EAX != 0`.

**Practical impact**: Producers in the binary never set the source field to the
sentinel pointer, so the asymmetry rarely produces a visible difference on the wire.
But the doc's pre-v5 "single 3-case rule for both fields" is wrong — source can never
emit `0xFFFFFFFF` (-1).

On read, the inverse pair `TGEvent::ReadFromStream` at `0x006D61C0` calls
`FUN_006F0EE0` (hash table lookup) for each non-zero, non-sentinel u32 to resolve
back to a pointer.

**Ship IDs**: Player N base = `0x3FFFFFFF + N * 0x40000` (cross-anchor with
objcreate-serialization mid #10; formula not re-verified this pass — see Open
Questions).
**Subsystem IDs**: Auto-assigned from global counter `DAT_0095B078` at construction
time. Subsystem IDs are NOT derived from the ship's base ID — they are sequential
globals. Resolved on the receiving end via the TGObject hash table at `DAT_0099A67C`
(this constant not re-verified this pass).

## Event Class 1: TGEvent (factory 0x101)

[v5-validated 2026-05-28]

The base event class. Used directly for repair-list events in the collision damage
chain — this is the most common event class seen in opcode 0x06 messages (~13 of
every 14 collision-related messages).

Pre-v5 docs called this "TGSubsystemEvent (factory 0x101)" with a separately-named
class layer. See the [Inheritance Hierarchy (Corrected)](#inheritance-hierarchy-corrected)
section above — there is no `TGSubsystemEvent`. 0x101 is TGEvent itself.

### Wire Layout

```
Offset  Size  Type    Field            Notes
------  ----  ----    -----            -----
0       1     u8      opcode           0x06
1       4     i32     factory_id       0x00000101
5       4     i32     event_type       See table below
9       4     i32     source_obj_id    Damaged subsystem (TGObject ID from obj+0x04)
13      4     i32     dest_obj_id      RepairSubsystem that queued it (TGObject ID from obj+0x04)
```

**Total**: 17 bytes (fixed).

### Event Types

| Event Type | Constant | Meaning |
|-----------|----------|---------|
| `0x008000DF` | ET_ADD_TO_REPAIR_LIST | Subsystem damaged, added to repair queue |
| `0x00800074` | ET_REPAIR_COMPLETED | Subsystem condition reached max (repair finished) |
| `0x00800075` | ET_REPAIR_CANNOT_BE_COMPLETED | Subsystem destroyed while in repair queue (condition reached 0.0) |

### TGEvent Class Layout (0x28 bytes in memory)

```
Offset  Size  Type        Field           Notes
------  ----  ----        -----           -----
0x00    4     void**      vtable          0x00895FF4
0x04    4     int         ni_refcount     NiObject reference count
0x08    4     void*       source_object   Source object ptr
0x0C    4     void*       related_object  Related (dest) object ptr
0x10    4     uint32      event_type      Event type constant
0x14    4     float       timestamp       -1.0f initially
0x18    2     uint16      flags_a         Event flags
0x1A    2     uint16      flags_b         Ref tracking flags
0x1C    4     void*       (reserved)
0x20    4     void*       (reserved)
0x24    4     void*       parent_event    Cleared to 0 on receive
```

### Serialization Functions

| Address | Function | Role |
|---------|----------|------|
| 0x006D6130 | TGEvent::WriteToStream | Writes factory_id, event_type, source_ref, dest_ref |
| 0x006D61C0 | TGEvent::ReadFromStream | Reads event_type, source_ref, dest_ref (factory_id already consumed) |
| 0x006D6200 | ReadObjectFromStream | Reads factory_id → factory lookup → construct → call ReadFromStream |

### Example: ADD_TO_REPAIR_LIST (17 bytes)

```
06                    opcode = 0x06 (PythonEvent)
01 01 00 00           factory_id = 0x00000101 (TGEvent)
DF 00 80 00           event_type = 0x008000DF (ET_ADD_TO_REPAIR_LIST)
2A 00 00 00           source_obj = 0x0000002A (damaged subsystem's TGObject ID)
1E 00 00 00           dest_obj = 0x0000001E (RepairSubsystem's TGObject ID)
```

Note: subsystem IDs are small sequential integers from the global counter, not
player-base-derived IDs like ship objects.

## Event Class 2: TGCharEvent (factory 0x105)

[v5-validated 2026-05-28]

Extends TGEvent with a single byte payload. Used by opcodes 0x07-0x12 and
0x1B (weapon/cloak/warp events via GenericEventForward), but NOT typically seen as
opcode 0x06. Documented here for completeness since the polymorphic deserializer can
reconstruct any registered factory type.

### Wire Layout

```
Offset  Size  Type    Field            Notes
------  ----  ----    -----            -----
0       1     u8      opcode           0x06 (if sent as PythonEvent)
1       4     i32     factory_id       0x00000105
5       4     i32     event_type       Depends on specific event
9       4     i32     source_obj_id    Source object
13      4     i32     dest_obj_id      Related object
17      1     u8      char_value       Single-byte payload (via stream vtable+0x54 WriteChar)
```

**Total**: 18 bytes (fixed).

### TGCharEvent Class Layout (0x2C bytes in memory)

```
Offset  Size  Type        Field           Notes
------  ----  ----        -----           -----
0x00    4     void**      vtable          0x008932DC
0x04-0x27     (inherited from TGEvent)
0x28    1     char        char_value      Single-byte payload
0x29-2B 3     -           padding         Struct padding to 0x2C
```

### Serialization Functions

| Address | Function | Role |
|---------|----------|------|
| 0x006D6940 | TGCharEvent::WriteToStream | Base fields + WriteChar(+0x28) |
| 0x006D6960 | TGCharEvent::ReadFromStream | Base fields + ReadChar → +0x28 |

See [set-phaser-level-protocol.md](set-phaser-level-protocol.md) for detailed analysis
of TGCharEvent usage in opcode 0x12.

## Event Class 3: TGObjPtrEvent (factory 0x10C)

[v5-validated 2026-05-28 via cross-anchor with mid #13]

Extends TGEvent with a 4-byte int32 object pointer (TGObject network ID).
This is the **most common event class during weapon combat** — 45% of all PythonEvents
in a 33.5-minute battle trace (1,718 of 3,825). Used by weapon fire/stop events,
tractor beam events, and repair priority events.

Full class layout, vtable, producers, and Python API are in
[tgobjptrevent-class.md](tgobjptrevent-class.md). Summary here:

### Wire Layout

```
Offset  Size  Type    Field            Notes
------  ----  ----    -----            -----
0       1     u8      opcode           0x06 (if sent as PythonEvent)
1       4     i32     factory_id       0x0000010C
5       4     i32     event_type       Depends on specific event
9       4     i32     source_obj_id    Source object
13      4     i32     dest_obj_id      Related object
17      4     i32     obj_ptr_id       Third object reference (TGObject network ID; stream vtable+0x84 WriteInt)
```

**Total**: 21 bytes (fixed).

### Key Difference from TGCharEvent

TGCharEvent (0x105) writes a single **byte** at +0x28 via WriteChar (18 bytes on wire).
TGObjPtrEvent (0x10C) writes a full **int32** at +0x28 via WriteInt (21 bytes on wire).
Both are 0x2C bytes in memory. They are distinct classes with different vtables and
constructors.

### Serialization Functions

| Address | Function | Role |
|---------|----------|------|
| 0x006D6DC0 | TGObjPtrEvent::WriteToStream | Base fields + WriteInt(+0x28) |
| 0x006D6DF0 | TGObjPtrEvent::ReadFromStream | Base fields + ReadInt → +0x28 |

### Producer Encoding Note

The TGObjPtrEvent producer encodes NULL→0 itself before storing into `this+0x28`,
so `WriteToStream` writes the raw u32 with no sentinel handling. Verified at
`RepairSubsystem_RaisePriority` (`0x005519e0`):

```c
if (param_1 == 0) uVar3 = 0;
else              uVar3 = *(undefined4 *)(param_1 + 4);
puVar2[10] = uVar3;  // [10] = +0x28 in 4-byte units
```

This is different from the source/dest fields on TGEvent base, which apply their
own NULL/sentinel logic at write time.

See [tgobjptrevent-class.md](tgobjptrevent-class.md) for full analysis including the
11-row C++ event-type catalog, Python API, vtable layout, and dual-fire pattern.

## Event Class 4: ObjectExplodingEvent (factory 0x8129)

[v5-validated 2026-05-28]

Carries ship destruction notifications. Extends TGEvent with a firing player ID
(who killed the ship) and an explosion lifetime (visual effect duration).

The class size and wire size are easy to confuse:

- **In-memory class size**: `0x30` bytes (48 in decimal) — includes 0x28-byte
  TGEvent base + 4-byte firing_player_id at `+0x28` + 4-byte lifetime float at
  `+0x2C`. (C5 clarification.)
- **Wire payload size**: 24 bytes — 16-byte base payload + 8-byte extension. Add the
  1-byte opcode for **25 bytes total on the wire**.

### Wire Layout

```
Offset  Size  Type    Field              Notes
------  ----  ----    -----              -----
0       1     u8      opcode             0x06
1       4     i32     factory_id         0x00008129
5       4     i32     event_type         Always 0x0080004E (ET_OBJECT_EXPLODING)
9       4     i32     source_obj_id      Object that is exploding
13      4     i32     dest_obj_id        Target (typically NULL or sentinel)
17      4     i32     firing_player_id   Connection ID of the killer (stream vtable+0x6C WriteInt)
21      4     f32     lifetime           Explosion effect duration in seconds (stream vtable+0x74 WriteFloat)
```

**Total**: 25 bytes wire (1 opcode + 24 payload).

The 8-byte extension uses raw int + raw float — no obj-ref encoding, no NULL/sentinel
translation. Different stream slots than the source/dest refs (`+0x6C`/`+0x74` for
the extension, `+0x84` for the refs in the base).

### ObjectExplodingEvent Class Layout (0x30 bytes in memory)

```
Offset  Size  Type        Field              Notes
------  ----  ----        -----              -----
0x00    4     void**      vtable             0x0088A178
0x04    4     int         ni_refcount        NiObject reference count
0x08    4     void*       source_object      Object that is exploding
0x0C    4     void*       dest_object        Target object
0x10    4     uint32      event_type         0x0080004E
0x14    4     float       timestamp          -1.0f initially
0x18    2     uint16      flags_a            Event flags
0x1A    2     uint16      flags_b            Ref tracking flags
0x1C    4     void*       (reserved)
0x20    4     void*       (reserved)
0x24    4     void*       parent_event       Cleared to 0 on receive
0x28    4     int32       firing_player_id   Killer's connection ID
0x2C    4     float       lifetime           Explosion duration (seconds)
```

### Constructor (0x0043F8B0)

```
this = TGEvent::ctor(this, 0)
this->vtable = 0x0088A178
this->firing_player_id = 0
this->lifetime = 0.0f
```

### Serialization Functions

| Address | Function | Role |
|---------|----------|------|
| 0x0043F990 | ObjectExplodingEvent::WriteToStream | Base fields + WriteInt(+0x28) + WriteFloat(+0x2C) |
| 0x0043F9C0 | ObjectExplodingEvent::ReadFromStream | Base fields + ReadInt → +0x28 + ReadFloat → +0x2C |

### IsA Chain

`ObjectExplodingEvent::IsA` (vtable+0x08 at `0x0043F8F0`) returns true for:

- `0x8129` (ObjectExplodingEvent)
- `0x101` (TGEvent) — **was missed in pre-v5 doc; confirms inheritance from TGEvent**
- `0x02` (NiObject root)

(C2 correction.) The 0x101 branch confirms ObjectExplodingEvent is a TGEvent subclass
just like TGCharEvent and TGObjPtrEvent; the pre-v5 hierarchy that placed it as a
direct sibling of "TGSubsystemEvent" was wrong on both counts.

### Example: Ship Destroyed (25 bytes)

```
06                    opcode = 0x06 (PythonEvent)
29 81 00 00           factory_id = 0x00008129 (ObjectExplodingEvent)
4E 00 80 00           event_type = 0x0080004E (ET_OBJECT_EXPLODING)
FF FF FF 3F           source_obj = 0x3FFFFFFF (Player 0's ship, exploding)
FF FF FF FF           dest_obj = sentinel (-1)
02 00 00 00           firing_player_id = 2 (killed by player 2)
00 00 80 3F           lifetime = 1.0f (1 second explosion)
```

## Two Producers

[v5-validated 2026-05-28]

Two distinct C++ producers write opcode 0x06 messages. Both are present in the
binary (raw disassembly is clean and matches the documentation) but are **undefined
as functions in the current Ghidra DB** — they appear as `LAB_006A1150` and
`LAB_006A1240` in xrefs from `MultiplayerGame_Ctor`. The pre-v5 doc's third
"producer" (GenericEventForward at `0x006A17C0`) is NOT a producer of opcode 0x06 —
it writes opcodes 0x07-0x12 and 0x1B for the GenericEventForward group, listed in
the [Two Receiver Paths](#two-receiver-paths) section below.

### 1. HostEventHandler (0x006A1150)

Handles repair-related events in multiplayer. Registered in the `MultiplayerGame`
constructor (`0x0069E590`) for three event types:

| Event Type | Constant | Trigger |
|-----------|----------|---------|
| `0x008000DF` | ET_ADD_TO_REPAIR_LIST | Subsystem added to repair queue |
| `0x00800074` | ET_REPAIR_COMPLETED | Subsystem condition reached max (repair finished) |
| `0x00800075` | ET_REPAIR_CANNOT_BE_COMPLETED | Subsystem destroyed while queued (condition ≤ 0.0) |

**Registration gate**: Only registered when `DAT_0097FA8A != 0` (i.e., `g_IsMultiplayer`
truthy).

**Behavior** (from raw disasm — function is undefined in DB but disasm walks cleanly):

```
HostEventHandler(MultiplayerGame* this, TGEvent* event):
  1. Read g_TGWinsockNetwork from [0x0097FA78]; if NULL, return
  2. TGBufferStream_Ctor(stack, ...) at 0x006CEFE0; OpenBuffer with cap 0x3FF
  3. Store opcode 0x06 byte at stack + 0x3C
  4. Call event->WriteToStream(stream) via vtable+0x34
  5. Get stream position (bytes written)
  6. Allocate TGMessage (0x40 bytes) via TGAlloc
  7. Copy [opcode_byte][stream_data] into message (position + 1 bytes)
  8. Set msg+0x3A = 1 (reliable flag)
  9. SendTGMessageToGroup at 0x006B4DE0 with group name "NoMe" at 0x008E5528
```

### 2. ObjectExplodingHandler (0x006A1240)

Handles ship destruction events. Registered for `0x0080004E` (ET_OBJECT_EXPLODING).

**Dual path** (also from raw disasm):

- **Multiplayer path** (entered at `0x006A126A`): byte-identical to
  HostEventHandler — serialize event with opcode 0x06, send reliably to "NoMe"
  group via `SendTGMessageToGroup` at `0x006B4DE0`.
- **Single-player path** (entered at `0x006A131B`):
  `FLD [event+0x2C]; FSTP [ship+0x14C]` (copies the lifetime float into the ship
  object), then calls `FUN_005AC250` which invokes
  `Effects.ObjectExploding(ship)` via Python.

**Registration gate**: Always registered (not gated on multiplayer at registration).
The handler internally checks `g_IsMultiplayer` (`MOV AL, [0x97FA8A]; TEST AL,AL;
JZ`) to select the path.

## Two Receiver Paths

### Path 1: PythonEvent Handler (MpgameHandlePythonEvent at 0x0069F880) — Opcodes 0x06, 0x0D

[v5-validated 2026-05-28]

Generic event deserializer. Handles both opcode 0x06 (PythonEvent) and 0x0D
(PythonEvent2). Note that the function body never reads the opcode byte — both
opcodes route here from the dispatcher jump table and are processed identically.

```
MpgameHandlePythonEvent(MultiplayerGame* this, TGMessage* msg):
  1. TGBufferStream_swig_GetBufferAndSize(msg) -> (pBuf, length)
     [calls FUN_006B8530 internally]
  2. TGBufferStream_swig_Ctor(stack)
  3. TGBufferStream_swig_OpenBuffer(stack, pBuf+1, length-1)  ; skip opcode byte
  4. event = ReadObjectFromStream(stack)                       ; FUN_006D6200
     a. Read factory_id via stream->vtable[+0x60] (4 raw bytes)
     b. Look up factory for factory_id via TGFactoryCreate (FUN_006F13E0)
     c. Allocate and construct event object of the correct class
     d. Call event->ReadFromStream(stream) via vtable+0x38
  5. ResolveObjectRefs(event)                                  ; FUN_006F13C0
     [invokes event->vtable[+0x18] (source) + event->vtable[+0x1C] (dest)]
  6. event[+0x24] = 0                                          ; clear parent_event
  7. TGEvent::Dispatch(event)                                  ; FUN_006DA300 (see C4)
  8. Refcount drop -> if 0, call event->vtable[+0x00](1)       ; scalar-deleting dtor
```

**Key characteristic**: This handler does NOT relay the message. It only deserializes
and dispatches locally. Collision-damage PythonEvents originate on the host and are
sent directly to clients via "NoMe" — no relay is needed. This confirms the
LOCAL-ONLY classification in [tgmessage-routing.md](tgmessage-routing.md) mid #7.

**Step 7 — what TGEvent::Dispatch actually does (C4 correction)**:
`FUN_006DA300` reads `event->dest_obj` (this+0x0C) and invokes
`dest_obj->vtable[+0x50](event)`. This is **event self-dispatch via the event's
dest object**, not a global event manager `PostEvent`. The pre-v5 doc named this
function `EventManager::PostEvent` based on its caller pattern, but the disasm
shows it's calling through the event's own `dest_obj` vtable — much narrower in
scope than the name suggests.

**Client-originated opcode 0x06**: If a client sends an opcode 0x06 message to the
host (rare — script events), the `MultiplayerGame` dispatcher at `0x0069F2A0` hits
the jump table entry for opcode 0x06 (index 6), which calls a relay function that:

1. Looks up "Forward" group in `WSN+0xF4`
2. Temporarily removes sender from group
3. Forwards message to remaining members
4. Re-adds sender
5. Then falls through to `MpgameHandlePythonEvent` for local dispatch

### Path 2: Generic Event Forward (FUN_0069FDA0) — Opcodes 0x07-0x12, 0x1B

Handles relay + dispatch for the specific event opcodes. These are NOT opcode 0x06
messages, but they share the same TGEvent serialization format.

**Key difference from Path 1**: Path 2 performs host relay (forwards to "Forward" group)
AND applies an event type override before local dispatch. Path 1 does neither.

### Event Type Override Table (Path 2 only)

| Opcode | Name | Sender Event | Receiver Override |
|--------|------|-------------|-------------------|
| 0x07 | StartFiring | 0x008000D8 | 0x008000D7 |
| 0x08 | StopFiring | 0x008000DA | 0x008000D9 |
| 0x09 | StopFiringAtTarget | 0x008000DC | 0x008000DB |
| 0x0A | SubsysStatus | 0x0080006C | 0x0080006C (no change) |
| 0x0B | AddToRepairList | 0x008000DF | 0 (preserve original) |
| 0x0C | ClientEvent | varies | 0 (preserve original) |
| 0x0E | StartCloak | 0x008000E2 | 0x008000E3 |
| 0x0F | StopCloak | 0x008000E4 | 0x008000E5 |
| 0x10 | StartWarp | 0x008000EC | 0x008000ED |
| 0x11 | RepairListPriority | 0x00800076 | 0 (preserve) |
| 0x12 | SetPhaserLevel | 0x008000E0 | 0 (preserve) |
| 0x1B | TorpTypeChange | 0x008000FE | 0x008000FD |

Override value `0` means the event's original type from the wire is preserved.

## Collision Damage → PythonEvent Chain

When two ships collide, the host generates approximately **13-14 PythonEvent
messages** — one per damaged subsystem on each ship. The complete chain:

```
1. ProximityManager detects collision
2. Posts ET_COLLISION_EFFECT (0x00800050)

3. ShipClass::CollisionEffectHandler (0x005AF9C0):
   a. Validates sender is host (checks g_IsHost at 0x0097FA89)
   b. Sends CollisionEffect (opcode 0x15) to "NoMe" group
   c. Falls through to FUN_005AFAD0 (collision damage application)

4. FUN_005AFAD0 → per-contact → FUN_005AF4A0 (per-subsystem damage):
   a. Reads subsystem condition (property+0x30)
   b. Reduces by damage amount
   c. Calls FUN_0056C470 (ShipSubsystem::SetCondition)

5. FUN_0056C470 (SetCondition):
   a. Stores new condition at this+0x30
   b. If newCondition < maxCondition AND ship alive:
      → Posts ET_SUBSYSTEM_HIT (0x0080006B)

6. RepairSubsystem::HandleHitEvent (0x005658D0) catches ET_SUBSYSTEM_HIT:
   a. Calls FUN_00565900 (AddSubsystemToRepairList)
   b. Adds to repair queue (rejects duplicates)
   c. If successful AND g_IsHost!=0 AND g_IsMultiplayer!=0:
      → Posts ET_ADD_TO_REPAIR_LIST (0x008000DF)

7. HostEventHandler (0x006A1150) catches ET_ADD_TO_REPAIR_LIST:
   → Serializes as opcode 0x06, sends to "NoMe" group
```

### Why ~13-14 Messages

- Two ships collide → each takes damage
- Each ship has ~7 top-level subsystems in the damage volume
- Each damaged subsystem → one SUBSYSTEM_HIT → one ADD_TO_REPAIR_LIST → one
  PythonEvent
- 7 subsystems × 2 ships = ~14 PythonEvent messages

The exact count varies with collision geometry and whether subsystems are already
in the repair queue (duplicates are rejected by `FUN_00565520`).

> **Stock trace confirmation**: A 33.5-minute 3-player combat session with 84
> collisions produced 3,825 PythonEvents total. Per-collision event counts of
> 12-14 confirmed.

> [!NOTE] The exact breakdown of "1 ObjectExploding + 11 ADD_TO_REPAIR_LIST +
> 2 delayed = 14" presented in the pre-v5 doc does not arithmetically reconcile
> (11 + 2 = 13). The "Worked Example" below shows 1 ObjectExploding + 13
> ADD_TO_REPAIR_LIST = 14. The per-collision count varies; treat 12-14 as a range
> rather than a fixed sum. Open Question #1 below.

### Worked Example from Stock Dedi Packet Trace

A single collision between two ships produced these 14 messages in sequence:

| # | Factory | Event Type | Meaning |
|---|---------|-----------|---------|
| 1 | 0x8129 | 0x0080004E | ObjectExplodingEvent (ship destroyed) |
| 2-14 | 0x0101 | 0x008000DF | ADD_TO_REPAIR_LIST (13 subsystems) |

When the collision is non-lethal, all 14 are ADD_TO_REPAIR_LIST. The
ObjectExplodingEvent appears only when a ship is destroyed.

## Event Registration

### RepairSubsystem Per-Instance (0x00565220)

Registered per ship instance when the repair subsystem is created. NOT gated on
multiplayer — always active.

| Event | Handler | String Ref |
|-------|---------|-----------|
| 0x0080006B (SUBSYSTEM_HIT) | HandleHitEvent | `0x008E5058` |
| 0x00800074 (REPAIR_COMPLETE) | HandleRepairComplete | `0x008E5030` |
| 0x00800070 (SUBSYSTEM_DAMAGED) | HandleSubsystemDamaged | `0x008E5008` |
| 0x00800075 (REPAIR_CANCELLED) | HandleRepairCancelled | `0x008E4FD8` |

### MultiplayerGame Constructor (0x0069E590) [v5-validated 2026-05-28]

Registered in MultiplayerGame constructor. HostEventHandler rows are gated on
`DAT_0097fa8a != 0` (multiplayer). ObjectExplodingHandler is registered
unconditionally — the handler decides MP vs SP internally.

| Event | Handler | Gate |
|-------|---------|------|
| 0x008000DF (ADD_TO_REPAIR_LIST) | HostEventHandler (0x006A1150) | `g_IsMultiplayer != 0` |
| 0x00800074 (REPAIR_COMPLETED) | HostEventHandler (0x006A1150) | `g_IsMultiplayer != 0` |
| 0x00800075 (REPAIR_CANNOT_BE_COMPLETED) | HostEventHandler (0x006A1150) | `g_IsMultiplayer != 0` |
| 0x0080004E (OBJECT_EXPLODING) | ObjectExplodingHandler (0x006A1240) | (always; handler checks internally) |

### ShipClass Static Registration (0x005AB7C0)

Class-level registration for collision processing (not per-instance).

| Event | Handler |
|-------|---------|
| 0x00800050 (COLLISION_EFFECT) | CollisionEffectHandler |
| 0x008000FC (HOST_COLLISION_EFFECT) | Same handler, alternate path |

## TGEvent Vtable Maps

### TGEvent Base Vtable (0x00895FF4)

| Slot | Offset | Address | Name |
|------|--------|---------|------|
| 0 | +0x00 | 0x006D5D40 | scalar_deleting_dtor |
| 1 | +0x04 | 0x006D5CE0 | GetFactoryID → returns 0x101 (NB: emits 0x101 directly — C1) |
| 2 | +0x08 | 0x006D5CF0 | IsA(id) |
| 3 | +0x0C | 0x006F1650 | (no-op, inherited from NiObject) |
| 4 | +0x10 | 0x006D5EC0 | WriteToStream_Full (persistent) |
| 5 | +0x14 | 0x006D5FF0 | ReadFromStream_Full (persistent) |
| 6 | +0x18 | 0x006D6050 | (init step) |
| 7 | +0x1C | 0x006D60B0 | (init step) |
| 8 | +0x20 | 0x006F15C0 | (no-op, inherited) |
| 9 | +0x24 | 0x006D5D10 | GetClassName → "TGEvent" |
| 10 | +0x28 | 0x006D5D20 | GetSWIGName → "_p_TGEvent" |
| 11 | +0x2C | 0x006D5D30 | GetPtrName → "TGEventPtr" |
| 12 | +0x30 | 0x006D6230 | CopyFrom |
| 13 | +0x34 | 0x006D6130 | **WriteToStream** (network) |
| 14 | +0x38 | 0x006D61C0 | **ReadFromStream** (network) |
| 15 | +0x3C | 0x006D8520 | dtor2 |
| 16 | +0x40 | 0x006D84C0 | (unknown) |
| 17 | +0x44 | 0x006D84D0 | (unknown) |

> [!NOTE] The 18-slot count above is from the pre-v5 doc. Engine doc
> [event-system-architecture.md](../engine/event-system-architecture.md) lists
> a 14-slot baseline; collision-effect-protocol.md lists 16 slots. This is
> §4 #7 in the protocol tracker — slot boundary at 0x00895FF4 needs a v5 spot
> check. Treat slots 15-17 here as `confidence: low` until that conflict
> resolves.

### ObjectExplodingEvent Vtable (0x0088A178) [v5-validated 2026-05-28]

Verified via raw memory dump (80 bytes from 0x0088A178).

| Slot | Offset | Address | Name |
|------|--------|---------|------|
| 0 | +0x00 | 0x0043F950 | scalar_deleting_dtor |
| 1 | +0x04 | 0x0043F8E0 | GetFactoryID → returns 0x8129 |
| 2 | +0x08 | 0x0043F8F0 | IsA(id) → true for `{0x8129, 0x101, 0x02}` (C2) |
| 6 | +0x18 | 0x006D6050 | (inherited from TGEvent — ResolveRefs source) |
| 7 | +0x1C | 0x006D60B0 | (inherited from TGEvent — ResolveRefs dest) |
| 9 | +0x24 | 0x0043F920 | GetClassName → "ObjectExplodingEvent" (string at 0x008DA270) |
| 10 | +0x28 | 0x0043F930 | GetSWIGName → "_p_ObjectExplodingEvent" (string at 0x008DA288) |
| 11 | +0x2C | 0x0043F940 | GetPtrName → "ObjectExplodingEventPtr" |
| 12 | +0x30 | 0x006D6230 | CopyFrom (inherited) |
| 13 | +0x34 | 0x0043F990 | **WriteToStream** (network) |
| 14 | +0x38 | 0x0043F9C0 | **ReadFromStream** (network) |

(Slots 3-5, 8, 15-17 inherited from TGEvent base.)

### TGCharEvent Vtable (0x008932DC)

| Slot | Offset | Address | Name |
|------|--------|---------|------|
| 0 | +0x00 | 0x00574CB0 | scalar_deleting_dtor |
| 1 | +0x04 | 0x00574C40 | GetFactoryID → returns 0x105 |
| 2 | +0x08 | 0x00574C50 | IsA(id) → true for `{0x105, 0x101, 0x02}` |
| 9 | +0x24 | 0x00574C80 | GetClassName → "TGCharEvent" |
| 10 | +0x28 | 0x00574C90 | GetSWIGName → "_p_TGCharEvent" |
| 11 | +0x2C | 0x00574CA0 | GetPtrName → "TGCharEventPtr" |
| 12 | +0x30 | 0x006D6920 | CopyFrom (base + char_value) |
| 13 | +0x34 | 0x006D6940 | **WriteToStream** (network) |
| 14 | +0x38 | 0x006D6960 | **ReadFromStream** (network) |

## Stream Vtable Slot Map

[v5-validated 2026-05-28]

The TGBufferStream SWIG variant vtable at `0x00895C58` was dumped (160 bytes) and
each slot decompile-verified. The key takeaway: in this SWIG class, the
`WriteInt`/`ReadInt` slots all write/read **4 raw bytes** — there is NO bit packing.
Slots `+0x80`/`+0x84` look like polymorphic virtual dispatchers but in practice
thunk through to `+0x68`/`+0x6C`.

| Slot offset | Address | Method | Byte cost |
|-------------|---------|--------|-----------|
| +0x50 | 0x006CF540 | ReadChar | 1 |
| +0x54 | 0x006CF730 | WriteChar | 1 |
| +0x60 | 0x006CF640 | ReadInt (raw 4-byte) | 4 |
| +0x64 | 0x006CF830 | WriteInt (raw 4-byte) | 4 |
| +0x68 | 0x006CF670 | ReadInt (alias) | 4 |
| +0x6C | 0x006CF870 | WriteInt (alias) | 4 |
| +0x70 | 0x006CF6B0 | ReadFloat | 4 |
| +0x74 | 0x006CF8B0 | WriteFloat | 4 |
| +0x80 | 0x006CF6A0 | ReadInt virtual dispatcher (forwards to +0x68) | 4 |
| +0x84 | 0x006CF930 | WriteInt virtual dispatcher (forwards to +0x6C) | 4 |

Mapping back to the wire-format extensions:

- TGCharEvent extension at offset 17 uses **+0x54 WriteChar** → 1 raw byte
- TGObjPtrEvent extension at offset 17 uses **+0x84 WriteInt** → 4 raw bytes
- ObjectExplodingEvent extension at offset 17 uses **+0x6C WriteInt** → 4 raw bytes;
  extension at offset 21 uses **+0x74 WriteFloat** → 4 raw bytes
- TGEvent base source/dest refs use **+0x84 WriteInt** → 4 raw bytes each

## Ghidra Annotations Applied

[v5-validated 2026-05-28]

| Action | Address | Symbol | Notes |
|--------|---------|--------|-------|
| Rename | 0x0069F880 | `FUN_0069F880` → `MpgameHandlePythonEvent` | Receiver for opcodes 0x06 + 0x0D |
| Set prototype | 0x0069F880 | `void __thiscall MpgameHandlePythonEvent(MultiplayerGame *this, TGMessage *msg)` | |
| Set plate comment | 0x0069F880 | v5 plate comment with effective_score 22.14 + the 8-step receiver flow | |

The four event-class serialization functions
(`TGEvent::WriteToStream` / `ReadFromStream` pair at 0x006D6130/0x006D61C0,
`TGCharEvent` pair at 0x006D6940/0x006D6960,
`TGObjPtrEvent` pair at 0x006D6DC0/0x006D6DF0,
`ObjectExplodingEvent` pair at 0x0043F990/0x0043F9C0) and the two producer
functions (`HostEventHandler` 0x006A1150, `ObjectExplodingHandler` 0x006A1240)
were either already named-and-plated by prior validation passes or remain
undefined-in-DB. No incremental v5 edits applied to those addresses this pass.

The undefined-in-DB producers (`LAB_006A1150`, `LAB_006A1240`) emit clean
disassembly that walks fine; only `decompile_function` would fail on them. This
is the same pattern as several other functions referenced from
`RegisterHandlers` callsites — annotation scripts have not been applied to the
current import for these specific labels.

## Traffic Statistics (15-minute 3-player session)

| Direction | Count | Notes |
|-----------|-------|-------|
| PythonEvent S→C | ~251 | Repair list + explosions + script events |
| PythonEvent C→S | 0 | Clients never send 0x06 in the collision path |
| CollisionEffect C→S | ~84 | Client collision reports (opcode 0x15) |

All collision-path PythonEvents are **host-generated, server-to-client only**.

## Open Questions

1. **Collision-event count math**. The "Worked Example" table shows 14 messages
   (1 ObjectExploding + 13 ADD_TO_REPAIR_LIST). The pre-v5 "Collision Chain Event
   Count" section also claims 14 = 1 + 11 + 2-delayed (sums to 14, but 11 + 2 = 13).
   Real ground truth requires packet trace replay against a known collision. Until
   then, treat 12-14 as a range rather than a fixed sum.
2. **Player N base ID formula** `0x3FFFFFFF + N * 0x40000`. The sentinel
   `0x3FFFFFFF` is confirmed at `DAT_0095ADFC`, but the per-player base ID formula
   has not been re-verified in this pass. Cross-anchor with
   [objcreate-serialization.md](objcreate-serialization.md) mid #10 where the
   formula is also cited; resolve next pass.
3. **Subsystem ID counter** `DAT_0095B078` — cited but not verified this pass.
4. **TGObject hash table** `DAT_0099A67C` for ID resolution on receive — cited but
   not verified this pass. May resolve via cross-anchor with mid #10
   (ResolveReferences at `FUN_006F13C0`) if it's the same hash table.
5. **TGEvent base vtable slot count** — pre-v5 table lists 18 slots (0-17); engine
   event-system-architecture.md baseline implies 14 slots; collision-effect-protocol.md
   lists 16. §4 #7 in the protocol tracker — vtable boundary at 0x00895FF4 needs a
   v5 check. Slots 15-17 in the TGEvent base vtable table above are flagged
   `confidence: low` pending that check.

## Related Functions

| Address | Name | Role |
|---------|------|------|
| 0x006A1150 | HostEventHandler | Serializes repair events as opcode 0x06 (raw disasm — undefined in DB) |
| 0x006A1240 | ObjectExplodingHandler | Serializes explosion events as opcode 0x06 (raw disasm — undefined in DB) |
| 0x006A17C0 | SendEventMessage | Generic: serialize event + opcode → TGMessage (writes other opcodes — NOT 0x06) |
| 0x0069F880 | MpgameHandlePythonEvent | Deserialize + dispatch (opcodes 0x06, 0x0D) [v5-validated] |
| 0x0069FDA0 | GenericEventForward | Relay + deserialize (opcodes 0x07-0x12, 0x1B) |
| 0x0069F2A0 | MultiplayerGame::ReceiveMessage | Jump table dispatcher (slots 6, 13 route here) |
| 0x006D6130 | TGEvent::WriteToStream | Base event serialization (4-write asymmetric refs) |
| 0x006D61C0 | TGEvent::ReadFromStream | Base event deserialization |
| 0x006D6200 | ReadObjectFromStream | Factory-based event construction from stream |
| 0x006DA300 | TGEvent::Dispatch | Event self-dispatch via dest_obj->vtable[+0x50] (C4 — was "EventManager::PostEvent") |
| 0x006F13C0 | ResolveReferences | Object ID → ptr (used by receiver step 5) |
| 0x006F13E0 | TGEventFactory::Create | Factory lookup + object allocation |
| 0x0043F990 | ObjectExplodingEvent::WriteToStream | Network serialization |
| 0x0043F9C0 | ObjectExplodingEvent::ReadFromStream | Network deserialization |
| 0x0043F8B0 | ObjectExplodingEvent::ctor | Constructor (0x30 bytes in-memory) |
| 0x006D6940 | TGCharEvent::WriteToStream | Network serialization |
| 0x006D6960 | TGCharEvent::ReadFromStream | Network deserialization |
| 0x00574C20 | TGCharEvent::ctor | Constructor (0x2C bytes in-memory) |
| 0x006D6DC0 | TGObjPtrEvent::WriteToStream | Network serialization |
| 0x006D6DF0 | TGObjPtrEvent::ReadFromStream | Network deserialization |
| 0x00403290 | TGObjPtrEvent::ctor | Constructor (0x2C bytes in-memory) |
| 0x0056C470 | ShipSubsystem::SetCondition | Posts SUBSYSTEM_HIT on damage |
| 0x00565900 | RepairSubsystem::AddToRepairList | Posts ADD_TO_REPAIR_LIST (host+MP gate) |
| 0x005658D0 | RepairSubsystem::HandleHitEvent | Catches SUBSYSTEM_HIT |
| 0x005AF9C0 | ShipClass::CollisionEffectHandler | Collision validation + damage |
| 0x006B4DE0 | SendTGMessageToGroup | Producer outbound (called by both producers) |
| 0x006CEFE0 | TGBufferStream::Ctor | Producer stream setup |

## Event Type Constants

| Code | Name | Producer | Notes |
|------|------|----------|-------|
| 0x008000DF | ET_ADD_TO_REPAIR_LIST | HostEventHandler | Most common in collision chain |
| 0x00800074 | ET_REPAIR_COMPLETED | HostEventHandler | Condition reached max |
| 0x00800075 | ET_REPAIR_CANNOT_BE_COMPLETED | HostEventHandler | Subsystem destroyed while queued |
| 0x0080004E | ET_OBJECT_EXPLODING | ObjectExplodingHandler | Ship destruction |
| 0x0080006B | ET_SUBSYSTEM_HIT | (internal only) | Triggers repair queue add |
| 0x00800050 | ET_COLLISION_EFFECT | (internal only) | Starts collision chain |
| 0x008000FC | ET_HOST_COLLISION_EFFECT | (internal only) | Client-reported collision |
| 0x00800053 | ET_COLLISION_DAMAGE | (internal only) | Auto-repair trigger |
| 0x00800070 | ET_SUBSYSTEM_DAMAGED | (internal only) | Damage tracking |
| 0x0000010C | TGObjPtrEvent (factory ID) | Weapon/tractor/repair events | **45% of all PythonEvents in combat** (1,718 of 3,825 in 33.5-min battle trace). NOTE: 0x010C is a factory_id, not an event_type. Carries ET_WEAPON_FIRED, ET_PHASER_STOPPED_FIRING, ET_TRACTOR_BEAM_STOPPED_FIRING, ET_REPAIR_INCREASE_PRIORITY, ET_SUBSYSTEM_HIT. See [tgobjptrevent-class.md](tgobjptrevent-class.md). |

## Related Documents

- [tgobjptrevent-class.md](tgobjptrevent-class.md) — TGObjPtrEvent (factory 0x10C) class layout, vtable, 5 C++ producers, mid #13 v5 source for C1 cascade
- [collision-effect-protocol.md](collision-effect-protocol.md) — Opcode 0x15 wire format (client collision reports)
- [collision-detection-system.md](../gameplay/collision-detection-system.md) — 3-tier collision detection pipeline
- [set-phaser-level-protocol.md](set-phaser-level-protocol.md) — TGCharEvent (0x105) detailed analysis, GenericEventForward
- [damage-system.md](../gameplay/damage-system.md) — Full damage pipeline: collision, weapon, explosion paths
- [cf16-explosion-encoding.md](cf16-explosion-encoding.md) — CompressedFloat16 format used in opcode 0x29 (Explosion)
- [repair-tractor-analysis.md](../gameplay/repair-tractor-analysis.md) — Repair queue mechanics, no queue limit
- [combat-mechanics-re.md](../gameplay/combat-mechanics-re.md) — Consolidated combat RE
- [event-system-architecture.md](../engine/event-system-architecture.md) — TGEvent base vtable + event manager
- [v5-validation-status.md](v5-validation-status.md) — Protocol family v5 tracker (§6.14)
