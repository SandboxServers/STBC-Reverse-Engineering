---
title: ADD_TO_REPAIR_LIST Event Object ID Analysis
type: reference
audience: RE engineers, OpenBC implementers
validated: 2026-05-28
methodology: FUNCTION_DOC_WORKFLOW_V5
binary_fingerprint: stbc.exe (base 0x400000, 32-bit Windows)
status: verified
supersedes: []
evidence:
  - claim: "TGObject_Ctor — sets vtable PTR_FUN_00896278; +0x04 = unique network object ID from global counter DAT_0095b078"
    address: 0x006f0a70
    confidence: high
    note: "decomp + assembly confirm auto-increment branch and registration into hash table"
  - claim: "DAT_0095b078 — sole producer/consumer is TGObject_Ctor itself (4 xrefs total: 3 READs + 1 WRITE, all from FUN_006f0a70). Single-writer global ID counter, proven by get_xrefs_to."
    address: null
    confidence: high
    note: "canonical single-writer proof pattern — no other writer exists in stbc.exe"
  - claim: "DAT_0099a67c — global hash table init lazily by TGObject_Ctor at 0x7F7 buckets (2039)"
    address: null
    confidence: high
    note: "hash lookup walks bucket chain via puVar1[2] (next ptr +0x08), returns puVar1[1] (object* +0x04)"
  - claim: "FUN_006f0ee0 — hash table lookup: object_id -> object* (returns NULL if not found)"
    address: 0x006f0ee0
    confidence: high
  - claim: "TGSourceObject_Ctor — calls TGObject; vtable PTR_FUN_008962f4; +0x08 = 0"
    address: 0x006f31a0
    confidence: high
  - claim: "TGDestObject_Ctor — calls TGSourceObject; vtable PTR_FUN_008962a8; +0x0C = 0"
    address: 0x006f2590
    confidence: high
  - claim: "TGHandler_Ctor — calls TGDestObject; vtable PTR_FUN_00896044; +0x10 = 0"
    address: 0x006d8f90
    confidence: high
  - claim: "ShipSubsystem_Ctor — calls TGHandler; vtable PTR_FUN_00892fc4; +0x40 zeroed (SetOwnerShip overwrites later)"
    address: 0x0056b970
    confidence: high
  - claim: "PoweredSubsystem_Ctor — calls ShipSubsystem; vtable PTR_FUN_00892d98"
    address: 0x00562240
    confidence: high
  - claim: "RepairSubsystem_Ctor — calls PoweredSubsystem; vtable PTR_FUN_00892e24"
    address: 0x00565090
    confidence: high
  - claim: "SetOwnerShip — writes ship pointer to subsystem+0x40, then runs additional setup"
    address: 0x0056bc50
    confidence: high
  - claim: "TGEvent_Ctor — size 0x28; vtable PTR_FUN_00895ff4; sets +0x14 = 0xBF800000 (-1.0f); zeros +0x18..+0x24; lazily allocates DAT_009983a4 hash table"
    address: 0x006d5c00
    confidence: high
  - claim: "TGObjPtrEvent_Ctor — size 0x2C; calls TGEvent_Ctor, sets vtable PTR_TGObjPtrEvent_ScalarDeletingDtor_0088869c, zeros +0x28"
    address: 0x00403290
    confidence: high
    note: "IsA returns true for 0x10C, 0x101, 0x02 per existing v5 plate"
  - claim: "TGEvent::SetSource — writes param_2 to event+0x08; manages refcount via DAT_009983a8"
    address: 0x006d6270
    confidence: high
  - claim: "TGEvent::SetDest — writes param_2 to event+0x0C; treats DAT_0095adfc as sentinel (skips refcount, emits -1 on wire)"
    address: 0x006d62b0
    confidence: high
  - claim: "TGEvent::WriteToStream — 4 stream calls emitting factoryType (vtable+0x04), eventType (+0x10), source_obj_id (+0x08->+0x04 or 0 if NULL), dest_obj_id (+0x0C->+0x04, 0 if NULL, -1 if DAT_0095adfc sentinel)"
    address: 0x006d6130
    confidence: high
  - claim: "TGObjPtrEvent::WriteToStream — calls TGEvent::WriteToStream then appends int32 obj_ptr from event+0x28"
    address: 0x006d6dc0
    confidence: high
  - claim: "ShipSubsystem::SetCondition — posts SUBSYSTEM_HIT (0x0080006B) when condition < max AND (ship==NULL OR ship+0x14C >= DAT_008e5c18). Allocates 0x2C bytes (TGObjPtrEvent), factory 0x10C, source=NULL, dest=ownerShip, obj_ptr=this+0x04 (subsystem's own ID)."
    address: 0x0056c470
    confidence: high
  - claim: "FUN_00565900 — RepairSubsystem::AddSubsystemToRepairList. Allocates 0x28 bytes (plain TGEvent, factory 0x101). Disassembly proves thiscall: ECX=RepairSubsystem, EBX=damagedSub. Sets event+0x10 = 0x008000DF directly via MOV; SetDest(repair) writes +0x0C; SetSource(damagedSub) writes +0x08; PostEvent to DAT_0097f838 EventManager singleton."
    address: 0x00565900
    confidence: high
    note: "RET 0x8 pops a 2nd stack arg (dead `1` from HandleHitEvent caller, never read inside FUN_00565900)"
  - claim: "AddToRepairList send gate: AddToList_returns_true AND DAT_0097fa89 (IsHost) AND DAT_0097fa8a (IsMultiplayer)"
    address: null
    confidence: high
    note: "byte-confirmed in FUN_00565900 disassembly"
  - claim: "RepairSubsystem::HandleHitEvent — created in Ghidra DB this pass. Body 0x005658d0-0x005658fe. Looks up damaged subsystem by event+0x28 via hash table, calls FUN_00565900(this, sub, 1)."
    address: 0x005658d0
    confidence: high
  - claim: "Handler registration table FUN_00565d40 — 7 RepairSubsystem handlers; 6 register via FUN_006da130, SetPlayer registers via FUN_006da160 (likely different handler-type ADT)"
    address: 0x00565d40
    confidence: high
  - claim: "HostEventHandler — serializes events as PythonEvent opcode 0x06. Allocates 1023-byte buffer, writes 0x06 at buffer[0], calls event->WriteToStream via vtable+0x34, allocates 0x40-byte TGMessage, sets msg+0x3A = 1 (reliable), broadcasts via FUN_006b4de0 with 'Forward' group string DAT_008e5528."
    address: 0x006a1150
    confidence: high
  - claim: "SUBSYSTEM_HIT wire format: 21 bytes — [byte 0x06][int32 0x010C][int32 0x0080006B][int32 0][int32 ship_obj_id][int32 subsystem_obj_id]"
    address: null
    confidence: high
    note: "byte-confirmed: opcode 1 + factory 4 + eventType 4 + source 4 + dest 4 + obj_ptr 4 = 21"
  - claim: "ADD_TO_REPAIR_LIST wire format: 17 bytes — [byte 0x06][int32 0x0101][int32 0x008000DF][int32 damaged_sub_id][int32 repair_sub_id]"
    address: null
    confidence: high
    note: "byte-confirmed: opcode 1 + factory 4 + eventType 4 + source 4 + dest 4 = 17 (no obj_ptr — plain TGEvent, not TGObjPtrEvent)"
companions:
  - docs/gameplay/repair-system.md
  - docs/gameplay/damage-system.md
  - docs/protocol/tgobjptrevent-class.md
  - docs/protocol/pythonevent-wire-format.md
---

> [docs](../README.md) / [gameplay](README.md) / repair-event-object-ids.md

# ADD_TO_REPAIR_LIST Event Object ID Analysis

> [!NOTE]
> **v5 clean pass — ROCK SOLID on every wire-format and ID-encoding claim.** Zero wire-format corrections; every byte sequence (SUBSYSTEM_HIT 21B, ADD_TO_REPAIR_LIST 17B), every offset, every gate, full 7-step constructor chain binary-confirmed. DAT_0095b078 ID counter proved single-writer via 4-xref result (3 READs + 1 WRITE all from TGObject_Ctor itself). 4 minor cosmetic clarifications applied; no behavior or wire claims changed.
>
> - **Clar-1**: ASCII comment on the factoryType line dropped the stale "TGSubsystemEvent" label (factory 0x101 is plain TGEvent; the in-body note at "TGEvent Layout > Note" already debunks the fabricated class — inherited from protocol leaf #13).
> - **Clar-2**: HandleHitEvent at 0x005658d0 IS in the Ghidra function DB now (created during this validation pass) — stale "NOT in Ghidra func DB" annotation removed.
> - **Clar-3**: FUN_00565900 has a dead 2nd stack arg (`1` passed by HandleHitEvent, never read; `RET 0x8` pops both). Signature updated to reflect the actual 3-arg ABI shape even though the wire output is unaffected.
> - **Clar-4**: SetPlayer handler registers via `FUN_006da160` (the other 6 RepairSubsystem handlers register via `FUN_006da130`). Likely a different handler-type ADT — flagged for follow-up in event-system-architecture.md.

## Summary

The ADD_TO_REPAIR_LIST event (0x008000DF) sent as PythonEvent (opcode 0x06) contains
**subsystem object IDs** in both the source and dest fields — NOT ship IDs. Each subsystem
has its own globally unique network object ID assigned at construction time from a global
auto-increment counter at `DAT_0095b078`.

## TGObject Class Hierarchy (Subsystems) [v5-validated 2026-05-28]

All subsystems inherit from TGObject (the base game object class). The full constructor
chain for a RepairSubsystem is byte-confirmed via the vtable trail
`0x00896278 -> 0x008962F4 -> 0x008962A8 -> 0x00896044 -> 0x00892FC4 -> 0x00892D98 -> 0x00892E24`:

```
FUN_006f0a70  TGObject          — assigns +0x04 = unique network object ID
  FUN_006f31a0  TGSourceObject  — +0x08 = 0  (source ref slot)
    FUN_006f2590  TGDestObject  — +0x0C = 0  (dest ref slot)
      FUN_006d8f90  TGHandler   — +0x10 = 0  (handler flags)
        FUN_0056b970  ShipSubsystem       — +0x40 = 0 (owner ship ptr, set later)
          FUN_00562240  PoweredSubsystem   — +0x88..+0xA0
            FUN_00565090  RepairSubsystem  — +0xA8..+0xBC
```

### TGObject ID Assignment (FUN_006f0a70) [v5-validated 2026-05-28]

```c
// Base game object constructor
void __thiscall TGObject_ctor(void *this, int objectID) {
    if (objectID == 0) {
        // Auto-assign: use global counter, then increment
        *(int*)(this + 0x04) = DAT_0095b078;
        objectID = DAT_0095b078;
    } else {
        *(int*)(this + 0x04) = objectID;
        if (DAT_0095b07d == 0 || objectID < DAT_0095b078) goto skip;
    }
    DAT_0095b078 = objectID + 1;  // increment counter
skip:
    // Register in global hash table DAT_0099a67c for lookup by ID
    FUN_006f0f30(this);
}
```

- `DAT_0095b078` = global auto-increment object ID counter
- `DAT_0099a67c` = global hash table mapping object ID -> object pointer (init lazy at 0x7F7 buckets = 2039)
- `FUN_006f0ee0` = hash table lookup: `objectID -> object*` (walks bucket chain via `puVar1[2]` next-ptr at +0x08; returns `puVar1[1]` object* at +0x04, or NULL if not found)

#### Single-Writer Global Counter Proof Pattern

`DAT_0095b078`'s sole producer/consumer is TGObject_Ctor itself. `get_xrefs_to` returns
exactly 4 references — 3 reads (the auto-assign branch reads it as the new ID, the explicit
branch compares against it, and the increment writes `objectID + 1`) and 1 write (the
increment), **all from FUN_006f0a70**. No other writer exists in stbc.exe.

This is the canonical proof pattern for ID-origin questions: when a doc claims "object X
has ID Y", trace Y back to the single global writer and assert no other writer exists. The
4-xref result for `DAT_0095b078` is the definitive evidence that subsystem IDs come from one
counter, mutated by exactly one function. Worth repeating for future ID-tracking
investigations.

### Subsystem +0x40 = Owner Ship Pointer [v5-validated 2026-05-28]

In Ship_SetupProperties (FUN_005b3fb0), after creating each subsystem:
```c
// vtable+0x58 = SetOwnerShip — at 0x0056bc50
(**(code **)(*subsystem + 0x58))(ship);
```

FUN_0056bc50:
```c
void __thiscall SetOwnerShip(void *this, void *ship) {
    *(void**)(this + 0x40) = ship;  // store ship pointer
    FUN_0056bde0(this);             // additional setup
}
```

All subsystems are created with `param_1=0` (auto-assign ID) in Ship_SetupProperties.

## TGEvent Layout [v5-validated 2026-05-28]

### TGEvent (base, factory type 0x101, size 0x28)

| Offset | Type | Field | Description |
|--------|------|-------|-------------|
| +0x00 | ptr | vtable | TGEvent vtable (0x895ff4) |
| +0x04 | int | objectID | Event's own network object ID (auto-assigned) |
| +0x08 | ptr | source | Source game object pointer (TGObject*) |
| +0x0C | ptr | dest | Dest/related game object pointer (TGObject*) |
| +0x10 | int | eventType | Game event type code (e.g. 0x008000DF) |
| +0x14 | float | timestamp | -1.0f (init via 0xBF800000) |
| +0x18 | short | field_18 | 0 |
| +0x1A | short | field_1A | 0 |
| +0x1C | int | field_1C | 0 |
| +0x20 | int | field_20 | 0 |
| +0x24 | int | field_24 | 0 |

### TGObjPtrEvent (factory type 0x10C, size 0x2C)

Inherits TGEvent, adds:

| Offset | Type | Field | Description |
|--------|------|-------|-------------|
| +0x28 | int32 | obj_ptr | TGObject network ID (int32, NOT a byte — see note below) |

**Note**: TGCharEvent (factory 0x105, ctor 0x00574C20) is a DIFFERENT class that writes
a single byte at +0x28. Factory 0x10C is TGObjPtrEvent (ctor 0x00403290), which writes
a full int32 at +0x28. There is **no class called "TGSubsystemEvent"** in stbc.exe — factory
0x101 is plain TGEvent. The v5 plate on TGObjPtrEvent_Ctor (0x00403290) and the v5
validation of the protocol leaf at `docs/protocol/tgobjptrevent-class.md` both debunk the
fabricated name.

## Setter Functions [v5-validated 2026-05-28]

- **FUN_006d6270**: `event->source (+0x08) = param_1` — sets source object pointer
- **FUN_006d62b0**: `event->dest (+0x0C) = param_1` — sets dest/related object pointer

Both functions also manage reference counting via the object tracking hash table at
`DAT_009983a8`. SetDest treats `DAT_0095adfc` as a sentinel (skips refcount and emits -1 on
the wire instead of an object ID).

## Event Wire Format [v5-validated 2026-05-28]

### TGEvent::WriteToStream (FUN_006d6130)

WriteToStream serializes via the stream (vtable calls):

```
[int32] factoryType      — vtable[+0x04] result (0x101 for TGEvent, 0x10C for TGObjPtrEvent)
[int32] eventType        — event+0x10 (e.g. 0x008000DF)
[int32] source_obj_id    — *(event->source + 0x04), or 0 if source==NULL
[int32] dest_obj_id      — *(event->dest + 0x04), or 0 if NULL, or -1 if DAT_0095adfc sentinel
```

### TGObjPtrEvent::WriteToStream (FUN_006d6dc0)

Calls TGEvent::WriteToStream first, then appends:

```
[int32] obj_ptr          — event+0x28 (TGObject network ID, subsystem's own ID)
```

### WriteObjectRef encoding for dest field [v5-validated 2026-05-28]

The dest field (event+0x0C) has three special cases:
1. **NULL** (dest == 0): writes `0`
2. **Sentinel** (dest == DAT_0095adfc, the "global" marker): writes `0xFFFFFFFF` (-1)
3. **Valid object**: writes `*(dest + 0x04)` — the object's network ID

The source field (event+0x08) has two cases:
1. **NULL** (source == 0): writes `0`
2. **Valid object**: writes `*(source + 0x04)` — the object's network ID

## ADD_TO_REPAIR_LIST (0x008000DF) Event Chain [v5-validated 2026-05-28]

### 1. Damage triggers SUBSYSTEM_HIT

**SetCondition** (FUN_0056c470) — called when a subsystem's condition changes:

```c
void __thiscall SetCondition(ShipSubsystem *this, float newCondition) {
    this->condition = newCondition;  // +0x30
    // Clamp to max
    if (GetMaxCondition(this) < this->condition)
        this->condition = GetMaxCondition(this);
    // Calculate percentage
    this->conditionPct = this->condition / GetMaxCondition(this);  // +0x34

    // If damaged (condition < max) AND owner ship exists AND not too soon:
    Ship *ship = this->ownerShip;  // +0x40
    if (this->condition < GetMaxCondition(this)
        && (ship == NULL || ship->timeSinceSpawn >= DAMAGE_REPORT_THRESHOLD)) {
        // Create TGObjPtrEvent (factory 0x10C)
        TGObjPtrEvent *evt = new TGObjPtrEvent(0);  // auto-assign ID

        // Source = NULL (no source for damage notification)
        SetSource(evt, 0);           // FUN_006d6270: evt+0x08 = NULL

        // Dest = owner ship pointer
        SetDest(evt, this->ownerShip);  // FUN_006d62b0: evt+0x0C = ship ptr

        // Event type = SUBSYSTEM_HIT
        evt->eventType = 0x0080006B;    // evt+0x10

        // ObjPtr = this subsystem's own object ID
        if (this != NULL)
            evt->obj_ptr = this->objectID;  // evt+0x28 = *(this+0x04)
        else
            evt->obj_ptr = 0;

        PostEvent(evt);
    }
}
```

**SUBSYSTEM_HIT wire format** — 21 bytes via HostEventHandler as opcode 0x06:
```
[byte]  0x06              — PythonEvent opcode
[int32] 0x010C            — TGObjPtrEvent factory type (carries int32 obj_ptr at +0x28)
[int32] 0x0080006B        — SUBSYSTEM_HIT event type
[int32] 0                 — source_obj_id (NULL, no source)
[int32] ship_obj_id       — dest_obj_id (*(ownerShip+0x04), the ship's network ID)
[int32] subsystem_obj_id  — obj_ptr (*(subsystem+0x04), the subsystem's own ID)
```

### 2. RepairSubsystem handles SUBSYSTEM_HIT

**RepairSubsystem::HandleHitEvent** at 0x005658d0 (body 0x005658d0-0x005658fe; created
during this v5 pass):

```c
void __thiscall HandleHitEvent(RepairSubsystem *this, TGObjPtrEvent *event) {
    // Look up the damaged subsystem by its object ID
    int subsystemID = event->obj_ptr;  // event+0x28
    ShipSubsystem *sub = LookupObjectByID(subsystemID);  // FUN_006f0ee0

    if (sub != NULL) {
        AddSubsystemToRepairList(this, sub, 1);  // FUN_00565900 (3rd arg is dead, see Clar-3)
    }

    // Forward to base handler
    ForwardEvent(this, event);  // FUN_006d90e0
}
```

### 3. AddSubsystemToRepairList posts ADD_TO_REPAIR_LIST

**FUN_00565900** (RepairSubsystem::AddSubsystemToRepairList) — thiscall confirmed via
disassembly (ECX=RepairSubsystem, EBX=damagedSub from HandleHitEvent caller; 3rd stack arg
is a dead `1` literal never read by the callee; `RET 0x8` pops both stack args):

```c
void __thiscall AddSubsystemToRepairList(RepairSubsystem *this,
                                          ShipSubsystem *damagedSub,
                                          int unused_dead_arg) {
    bool added = AddToList(this, damagedSub);  // FUN_00565520

    if (added && g_IsHost && g_IsMultiplayer) {
        // Create plain TGEvent (factory 0x101) — NOT TGObjPtrEvent
        TGEvent *evt = new TGEvent(0);  // auto-assign ID, allocates 0x28 bytes

        // event+0x10 = 0x008000DF set directly via
        //   MOV dword ptr [ESI + 0x10], 0x8000df
        evt->eventType = 0x008000DF;    // ADD_TO_REPAIR_LIST

        // SetDest(this=RepairSubsystem) — evt+0x0C = repairSub
        SetDest(evt, this);              // FUN_006d62b0
        // NOTE: despite the function name, this sets +0x0C ("dest")

        // SetSource(damagedSub) — evt+0x08 = damagedSub
        SetSource(evt, damagedSub);      // FUN_006d6270
        // NOTE: despite the function name, this sets +0x08 ("source")

        // PostEvent to EventManager singleton at DAT_0097f838
        PostEvent(evt);                  // FUN_006da2a0
    }
}
```

**ADD_TO_REPAIR_LIST wire format** — 17 bytes via HostEventHandler as opcode 0x06:
```
[byte]  0x06              — PythonEvent opcode
[int32] 0x0101            — TGEvent factory type (plain TGEvent, NOT TGCharEvent / NOT TGObjPtrEvent)
[int32] 0x008000DF        — ADD_TO_REPAIR_LIST event type
[int32] damaged_sub_id    — source_obj_id: *(damagedSub+0x04) = damaged subsystem's unique ID
[int32] repair_sub_id     — dest_obj_id: *(repairSubsystem+0x04) = RepairSubsystem's unique ID
```

## Answer to the Core Question

**Both `source_obj_id` and `dest_obj_id` contain subsystem-level unique network object IDs.**
They are NOT ship base IDs. They are NOT subsystem indices.

- **source_obj_id** = the damaged subsystem's own globally unique object ID (from +0x04)
- **dest_obj_id** = the RepairSubsystem's own globally unique object ID (from +0x04)

These IDs are auto-assigned from the global counter `DAT_0095b078` at subsystem construction
time. They are NOT derived from the ship's base ID by any formula. Each subsystem gets the
next sequential value from the counter at the time it is created. The mapping is:

```
Ship created with base ID N (e.g. 0x3FFFFFFF for player 0)
  → subsystem 1 gets ID = counter_at_creation_time
  → subsystem 2 gets ID = counter_at_creation_time + 1
  → subsystem 3 gets ID = counter_at_creation_time + 2
  → ... etc
```

The counter value depends on what other objects were created before the ship's subsystems.
There is NO fixed offset formula from ship base to subsystem ID. The only way to resolve
a subsystem ID on the receiving end is to use the global hash table lookup (FUN_006f0ee0).

## Related Handler Registration [v5-validated 2026-05-28]

From RepairSubsystem_HandleHitEvent_RegisterHandlers (FUN_00565d40), the event handler registrations:

| Address | Handler | Event | Registration fn |
|---------|---------|-------|-----------------|
| 0x005658d0 | HandleHitEvent | SUBSYSTEM_HIT (0x0080006B) | FUN_006da130 |
| 0x00565980 | HandleRepairComplete | REPAIR_COMPLETE | FUN_006da130 |
| 0x00565a10 | HandleSubsystemRepair | SUBSYSTEM_REPAIR | FUN_006da130 |
| 0x00565a80 | HandleRepairCancel | REPAIR_CANCEL | FUN_006da130 |
| 0x00565b50 | HandleIncreasePriority | INCREASE_PRIORITY | FUN_006da130 |
| 0x00565b30 | HandleAddToRepairList | ADD_TO_REPAIR_LIST (0x008000DF) | FUN_006da130 |
| 0x00565cd0 | HandleSetPlayer | SET_PLAYER | **FUN_006da160** (Clar-4) |

The SetPlayer handler is the only one of the 7 that registers via `FUN_006da160` instead of
`FUN_006da130`. Likely a different handler-type ADT (e.g. enter/exit handler vs hit handler).
Resolution belongs in `docs/engine/event-system-architecture.md` follow-up; non-load-bearing
for the wire-format claims in this doc.

## HostEventHandler (0x006a1150) [v5-validated 2026-05-28]

The HostEventHandler is responsible for serializing events to the network. Assembly confirms
every step:

1. Sets buffer[0] = 0x06 (PythonEvent opcode) via `MOV byte ptr [ESP + 0x3c], 0x6`
2. Allocates a TGFlatBufferStream with a 1023-byte buffer (`PUSH 0x3ff`)
3. Calls `event->WriteToStream(stream)` via `vtable[+0x34]`
4. Gets the stream size, allocates a TGMessage (`PUSH 0x40` — TGMessage size 0x40 bytes)
5. Copies the buffer to the message via FUN_006b84d0 (buffer copy)
6. Sets msg+0x3A = 1 (reliable flag) via `MOV byte ptr [ESI + 0x3a], 0x1`
7. Pushes "Forward" group string (`PUSH 0x8e5528`)
8. Sends via TGNetwork::BroadcastTGMessage at FUN_006b4de0

This means ALL events serialized through HostEventHandler become opcode 0x06 PythonEvent
messages on the wire, regardless of the event type. The event type is INSIDE the payload.

## Key Addresses [v5-validated 2026-05-28]

| Address | Symbol | Description |
|---------|--------|-------------|
| 0x006f0a70 | TGObject::ctor | Assigns +0x04 = network object ID |
| 0x0095b078 | g_NextObjectID | Global auto-increment object ID counter (single-writer, 4 xrefs) |
| 0x0099a67c | g_ObjectHashTable | Hash table: object ID -> object pointer (lazy-init, 2039 buckets) |
| 0x006f0ee0 | LookupObjectByID | Hash table lookup by ID |
| 0x006d6130 | TGEvent::WriteToStream | Serializes event to network stream (4 fields) |
| 0x006d6dc0 | TGObjPtrEvent::WriteToStream | Appends +0x28 obj_ptr (int32) after base |
| 0x006d5c00 | TGEvent::ctor | Event constructor (size 0x28) |
| 0x00403290 | TGObjPtrEvent::ctor | ObjPtrEvent constructor (size 0x2C) |
| 0x006d62b0 | TGEvent::SetDest | Sets event+0x0C (dest object ptr); DAT_0095adfc = -1 sentinel |
| 0x006d6270 | TGEvent::SetSource | Sets event+0x08 (source object ptr) |
| 0x00565900 | RepairSubsystem::AddToRepairList | Creates ADD_TO_REPAIR_LIST event (dead 2nd arg) |
| 0x005658d0 | RepairSubsystem::HandleHitEvent | Catches SUBSYSTEM_HIT; calls AddToRepairList |
| 0x00565d40 | RepairSubsystem::RegisterHandlers | Registers all 7 handlers (1 via FUN_006da160) |
| 0x0056c470 | ShipSubsystem::SetCondition | Posts SUBSYSTEM_HIT when damaged |
| 0x0056bc50 | ShipSubsystem::SetOwnerShip | Sets subsystem+0x40 = ship ptr |
| 0x006a1150 | HostEventHandler | Serializes events as opcode 0x06 |
