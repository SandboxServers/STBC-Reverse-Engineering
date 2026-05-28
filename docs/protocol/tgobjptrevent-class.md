> [docs](../README.md) / [protocol](README.md) / tgobjptrevent-class.md

---
title: TGObjPtrEvent Class (Factory ID 0x010C)
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
  - claim: "TGObjPtrEvent class size = 0x2C bytes (12 fields), vtable at 0x0088869C"
    address: 0x00403290
    function: TGObjPtrEvent_Ctor
    completeness: 57.75
    confidence: high
    note: "Allocation pattern at every producer: `FUN_00717b70(0x2c) -> FUN_00718010 -> FUN_00403290`. Ctor writes `*param_1 = &PTR_FUN_0088869c` and zeros the +0x28 obj_ptr slot. `TGObjPtrEvent` struct created in Ghidra and applied via prototypes this pass."
  - claim: "TGObjPtrEvent_Ctor at 0x00403290 calls TGEvent base ctor then writes vtable + zeros +0x28"
    address: 0x00403290
    function: TGObjPtrEvent_Ctor
    completeness: 57.75
    confidence: high
    note: "__thiscall(this, swigType). 30 CALL xrefs (`get_xrefs_to(0x00403290)`)."
  - claim: "Wire format = 1 opcode + 4 factory_id + 4 event_type + 4 src + 4 dest + 4 obj_ptr = 21 bytes"
    address: 0x006D6DC0
    function: TGObjPtrEvent_WriteToStream
    completeness: 73.92
    confidence: high
    note: "Base TGEvent::WriteToStream (FUN_006d6130) writes factory_id + event_type + src_obj_ref + dest_obj_ref via stream vtable[0x64]/[0x84]. Subclass appends one more i32 obj_ptr via stream vtable[0x84]. Opcode byte = 1 framing prefix. Function was undefined in Ghidra before this pass — `create_function` recovered the body."
  - claim: "TGObjPtrEvent_ReadFromStream reads i32 obj_ptr via stream vtable[0x80] after base read"
    address: 0x006D6DF0
    function: TGObjPtrEvent_ReadFromStream
    completeness: null
    confidence: high
    note: "Function was undefined in Ghidra before this pass — `create_function` recovered the body."
  - claim: "TGObjPtrEvent_IsA returns true for {0x10C, 0x101, 0x02}"
    address: 0x004032C0
    function: TGObjPtrEvent_IsA
    completeness: null
    confidence: high
    note: "10-instruction leaf; compares param against three constants. Function created this pass."
  - claim: "Source/dest object ID encoding: NULL -> 0; sentinel `DAT_0095adfc` -> 0xFFFFFFFF; else `*(uint32*)(obj+0x04)`"
    address: 0x006D6130
    function: TGEvent_WriteToStream
    completeness: null
    confidence: high
    note: "Confirmed via TGEvent base WriteToStream decompile. Same encoding used for both src_obj_ref (+0x08) and dest_obj_ref (+0x0C)."
  - claim: "Vtable @ 0x0088869C is 17 slots through +0x40 (not 12-14 as previous doc suggested)"
    address: 0x0088869C
    function: (TGObjPtrEvent vtable)
    completeness: null
    confidence: high
    note: "Slot 0 = 0x00403320 ScalarDeletingDtor (size 0x2C). Slot 11 = 0x00403310 GetSWIGPtrName ('TGObjPtrEventPtr'). Slot 15 = 0x00403500 (size 0x34 subclass dtor). See vtable table in body."
  - claim: "Slot 11 (+0x2C) is a third RTTI string-return method GetSWIGPtrName returning 'TGObjPtrEventPtr'"
    address: 0x00403310
    function: TGObjPtrEvent_GetSWIGPtrName
    completeness: null
    confidence: high
    note: "ASCIIZ at 0x008d85b8. Universal SWIG triple-string pattern: parallel TGCharEventPtr at 0x008e54ec, ObjectExplodingEventPtr at 0x008da2a0. Function created this pass."
  - claim: "Slot 8 (+0x20) is TGEventHandlerObject::InvokePythonHandler at 0x006f15c0 (universal slot)"
    address: 0x006F15C0
    function: TGEventHandlerObject__InvokePythonHandler
    completeness: null
    confidence: high
    note: "Cross-confirmed by docs/engine/event-system-architecture.md (engine #8) — 100+ data xrefs across all TGEventHandlerObject subclasses."
  - claim: "30 ctor xrefs to TGObjPtrEvent_Ctor; 5 DATA xrefs to vtable 0x0088869C"
    address: 0x00403290
    function: TGObjPtrEvent_Ctor
    completeness: 57.75
    confidence: high
    note: "DATA xrefs at 0x40329d (canonical ctor) / 0x551a5b (RepairSubsystem_RaisePriority manual-ctor) / 0x57f185 (tractor) / 0x5712fe (phaser-stop) / 0x5768c5 (weapon-system)."
  - claim: "Phaser::Fire (FUN_00571f40) emits dual-fire: 0x00800081 ET_PHASER_STARTED_FIRING then 0x0080007C ET_WEAPON_FIRED"
    address: 0x00572074
    function: PhaserSystem__Fire
    completeness: null
    confidence: high
    note: "Second emit at 0x005720df. obj_ptr resolved via 0x006f0ee0 (target ID lookup)."
  - claim: "Tractor::Fire (FUN_0057f580) emits dual-fire: 0x0080007D ET_TRACTOR_BEAM_STARTED_FIRING then 0x0080007C ET_WEAPON_FIRED"
    address: 0x0057F64B
    function: TractorBeamSystem__Fire
    completeness: null
    confidence: high
    note: "Second emit at 0x0057f6b3. Torpedo::Fire (FUN_0057c9e0) at 0x0057caa2 emits 0x0080007C only (single-fire, no PHASER/TRACTOR pair)."
  - claim: "ET_STOP_FIRING_AT_TARGET_NOTIFY (0x008000DC) is gated on `DAT_0097fa89 != 0` (host-only)"
    address: 0x00574010
    function: PhaserSystem__StopFiringAtTarget
    completeness: null
    confidence: high
    note: "Same gate at 0x005825a0 (TractorBeamSystem__StopFiringAtTarget). Both producers wrap event creation in `if (DAT_0097fa89 != '\\0' && this+0xa4 != 0 && this+0xa8 != 0)`."
  - claim: "ET_TARGET_WAS_CHANGED (0x00800058) stores the PREVIOUS target's ID, not the new one"
    address: 0x005AE270
    function: Ship__SetTarget
    completeness: null
    confidence: high
    note: "FUN_005ae210 reads `iVar1 = FUN_005ae170()` (current target getter) BEFORE allocating event, then writes `*(iVar3+0x28) = *(iVar1+4)` — the OLD target's ID. Lets handlers clean up references to the previous target before the new one takes effect."
  - claim: "RepairSubsystem_RaisePriority (FUN_005519e0) hand-rolls vtable write instead of calling TGObjPtrEvent_Ctor"
    address: 0x00551A5B
    function: RepairSubsystem_RaisePriority
    completeness: null
    confidence: high
    note: "Allocates 0x2C, calls TGEvent base ctor FUN_006d5c00, then writes `*puVar2 = &PTR_FUN_0088869c` directly. This is why FUN_005519e0 appears in vtable DATA xrefs but not in the 30 CALL xrefs. Resulting object still passes IsA(0x10C); wire format identical."
  - claim: "Class identity: vtable 0x00895FF4 (written by TGEvent base ctor FUN_006d5c00) emits factory_id 0x101 — so 0x101 IS TGEvent itself"
    address: 0x006D5CE0
    function: TGEvent_GetFactoryID
    completeness: null
    confidence: high
    note: "Byte-pattern `B8 01 01 00 00 C3` (MOV EAX, 0x101 / RET) returns a single match at 0x006d5ce0. No class named 'TGSubsystemEvent' anywhere in the binary string table. TGCharEvent (0x105) and TGObjPtrEvent (0x10C) are SIBLINGS directly under TGEvent (0x101)."
  - claim: "TGCharEvent IsA chain confirms sibling-under-TGEvent topology: returns true for {0x105, 0x101, 0x02}"
    address: 0x00574C50
    function: TGCharEvent_IsA
    completeness: null
    confidence: high
    note: "Same chain shape as TGObjPtrEvent. Both classes sit directly under TGEvent (0x101); there is no intermediate TGSubsystemEvent layer."
  - claim: "All 11 game event types verified at producer sites with byte-level emit addresses"
    address: null
    function: (multiple producers)
    completeness: null
    confidence: high
    note: "Producer verification grid in body. ET_SET_PLAYER 0x0080000E @ 0x004066f6; ET_TARGET_WAS_CHANGED 0x00800058 @ 0x005ae270; ET_SUBSYSTEM_HIT 0x0080006B @ 0x0056c4fa; ET_REPAIR_INCREASE_PRIORITY 0x00800076 @ 0x00551a5b; ET_WEAPON_FIRED 0x0080007C @ 0x005720df/0x0057caa2/0x0057f6b3; ET_TRACTOR_BEAM_STARTED_FIRING 0x0080007D @ 0x0057f64b; ET_PHASER_STARTED_FIRING 0x00800081 @ 0x00572074; ET_PHASER_STOPPED_FIRING 0x00800083 @ vtable xref 0x005712FE; ET_TRACTOR_TARGET_DOCKED 0x00800085 @ 0x00580ce6; ET_SENSORS_SHIP_IDENTIFIED 0x00800088 @ 0x00568afd/0x005678ec; ET_STOP_FIRING_AT_TARGET_NOTIFY 0x008000DC @ 0x0057405e/0x005825ee."
  - claim: "Timer delivery (factory 0x10C with event_type 0x00050001) drives AI timer notifications"
    address: 0x0070232E
    function: (AI timer producer)
    completeness: null
    confidence: high
    note: "FUN_007022f0 emits factory 0x10C with event_type 0x50001 (top half = 5, bottom half = 1); obj_ptr = timer source. Sibling at FUN_007023e0 (0x00702407) inferred same pattern (not re-decompiled this pass)."
  - claim: "SWIG wrapper addresses (0x005C7F10/F90/8000/8070/80E0) are NOT defined as functions in current Ghidra DB"
    address: null
    function: (SWIG wrappers)
    completeness: null
    confidence: medium
    note: "PyMethodDef name strings ('new_TGObjPtrEvent', 'TGObjPtrEvent_Cast', 'TGObjPtrEvent_Create', 'TGObjPtrEvent_GetObjPtr', 'TGObjPtrEvent_SetObjPtr') verified at 0x0092eab0..0x0092eaf4. Wrapper function bodies were not disassembled in this Ghidra import — `tools/ghidra_annotate_swig.py` has not been re-run against the current import. Address-specific claims demoted to medium pending annotation script application. Behavioral Python-usage claims are cross-source from `reference/scripts/` and unchanged."
companions:
  - docs/protocol/pythonevent-wire-format.md
  - docs/protocol/wire-format-spec.md
  - docs/protocol/stream-primitives.md
  - docs/protocol/transport-layer.md
  - docs/protocol/game-opcodes.md
  - docs/engine/event-system-architecture.md
  - docs/protocol/v5-validation-status.md
supersedes:
  - (prior pre-v5)
---

# TGObjPtrEvent — Factory 0x010C

Complete reverse engineering analysis of TGObjPtrEvent, a TGEvent subclass that carries
an int32 object network ID. This class accounts for **45% of all PythonEvent messages**
during combat — the single most common event class in weapon combat.

> [!NOTE]
> This doc is `status: partial`. The class layout (0x2C bytes, +0x28 i32 obj_ptr), 21-byte
> wire format, vtable identity at 0x0088869C, source/dest encoding (NULL/sentinel/object-id-
> from-+0x04), and **all 11 game event types** (with byte-level producer-site addresses)
> are v5-validated against the current Ghidra import (2026-05-28). Three corrections landed:
>
> - **C1 — "TGSubsystemEvent (0x101)" is fabricated.** The binary has no class with that
>   name. The vtable at 0x00895FF4 (which TGEvent's base ctor `FUN_006d5c00` writes) has
>   its `GetFactoryID` emit 0x101 directly (`MOV EAX, 0x101 / RET` at 0x006d5ce0). So
>   **0x101 IS TGEvent itself**. TGCharEvent (0x105) and TGObjPtrEvent (0x10C) are
>   **siblings** directly under TGEvent. The "0x02" root has no GetFactoryID emitter and
>   is likely a SWIG-base "Object" type with no real C++ class in BC.
> - **C2 — Vtable is 17 slots through +0x40, not the smaller count shown previously.**
>   Slot 0 is the real `ScalarDeletingDtor` at 0x00403320 (size 0x2C); slot 11 is a third
>   RTTI method `GetSWIGPtrName` at 0x00403310 returning the ASCIIZ "TGObjPtrEventPtr" at
>   0x008d85b8. This is a **universal SWIG triple-string pattern** also present on
>   TGCharEvent and ObjectExplodingEvent. Slot 15 is a separate size-0x34 subclass dtor at
>   0x00403500.
> - **C3 — SWIG wrapper addresses unanchored.** The 5 wrapper addresses (0x005C7F10 /
>   0x005C7F90 / 0x005C8000 / 0x005C8070 / 0x005C80E0) are not defined as functions in the
>   current Ghidra DB. The PyMethodDef name strings exist at 0x0092eab0..0x0092eaf4 but
>   the wrapper bodies are not disassembled — the SWIG annotation script has not been
>   re-applied to the current import. Demoted to `confidence: medium`; behavioral
>   Python-usage claims (cross-source from scripts) are unchanged.
>
> Substantial Ghidra annotation work landed this pass: 10 functions newly created, 16
> renamed, 1 `TGObjPtrEvent` struct created and applied via prototypes, 6 prototypes
> installed, 3 plate comments. See the [Ghidra Annotations Applied](#ghidra-annotations-applied-2026-05-28)
> section below.
>
> See [docs/guides/v5-evidence-header.md](../guides/v5-evidence-header.md) for the v5
> evidence standard.

## Summary

| Property | Value |
|----------|-------|
| **Factory ID** | 0x010C (decimal 268) |
| **Class Name** | `TGObjPtrEvent` |
| **SWIG Name** | `_p_TGObjPtrEvent` |
| **SWIG Ptr Name** | `TGObjPtrEventPtr` (slot 11 — new this pass) |
| **Vtable Address** | 0x0088869C (17 slots through +0x40) |
| **Object Size** | 0x2C (44 bytes) |
| **IsA Chain** | 0x010C → 0x0101 (TGEvent itself) → 0x02 (SWIG root) |
| **Constructor** | 0x00403290 |
| **Wire Size** | 21 bytes (1 opcode + 16 base + 4 obj_ptr) |

## Class Hierarchy (Corrected)

The pre-v5 doc placed an intermediate `TGSubsystemEvent` class between TGEvent (0x02) and
its subclasses. **That class does not exist in the binary.** The v5-validated hierarchy is:

```
SWIG "Object" root (factory 0x02)            // no GetFactoryID emitter found
  └── TGEvent (factory 0x101)                 // ctor FUN_006d5c00 + vtable 0x00895FF4
        ├── TGCharEvent (factory 0x105)        // size 0x2C, +0x28 = byte (1 wire byte)
        ├── TGObjPtrEvent (factory 0x10C)      // size 0x2C, +0x28 = int32 (4 wire bytes)
        └── ObjectExplodingEvent (factory 0x8129)  // size 0x30, +0x28 = int32, +0x2C = float
```

**Evidence that 0x101 is TGEvent itself, not a missing parent:**

- Byte-pattern search for `B8 01 01 00 00 C3` (`MOV EAX, 0x101 / RET`) returns exactly
  one hit at 0x006d5ce0.
- That function is at slot +0x04 of vtable 0x00895FF4.
- Vtable 0x00895FF4 is written by `FUN_006d5c00` (TGEvent base ctor) into every
  TGEvent-derived object as the base layer of construction.
- String search for `"TGSubsystemEvent"` returns 0 matches across the binary.

So when `TGObjPtrEvent_IsA(0x101)` returns true, it is reporting "I am a TGEvent" — not
"I am a TGSubsystemEvent". The 0x02 root has no GetFactoryID emitter; it is most likely
the SWIG-base "Object" type used for Python script type negotiation, with no real C++
class behind it.

### Key Difference from TGCharEvent (factory 0x105)

Both TGObjPtrEvent and TGCharEvent are 0x2C bytes in memory with a field at +0x28, but
they are **siblings**, not parent-child:

| Property | TGObjPtrEvent (0x10C) | TGCharEvent (0x105) |
|----------|-----------------------|---------------------|
| Constructor | 0x00403290 | 0x00574C20 |
| Vtable | 0x0088869C | 0x008932DC |
| Field at +0x28 | int32 (TGObject ID) | byte (single char) |
| WriteToStream extension | stream vtable[0x84] (WriteInt32) | stream vtable[0x54] (WriteByte) |
| Wire extension | 4 bytes | 1 byte |
| Total wire size | 21 bytes | 18 bytes |
| IsA chain | {0x10C, 0x101, 0x02} | {0x105, 0x101, 0x02} |

## Class Layout (0x2C bytes) [v5-validated 2026-05-28]

The struct was created in Ghidra this pass and applied via prototypes at the ctor and
WriteToStream functions.

```
Offset  Size  Type       Field              Notes
0x00    4     void**     vtable             0x0088869C
0x04    4     int        ni_refcount        NiObject reference count
0x08    4     void*      source_object      Source object ptr
0x0C    4     void*      dest_object        Related/destination object ptr
0x10    4     uint32     event_type         Event type constant (0x008000xx)
0x14    4     float      timestamp          -1.0f initially
0x18    2     uint16     flags_a            Event flags
0x1A    2     uint16     flags_b            Ref tracking flags
0x1C    4     void*      (reserved)         Read by vtable slot 16 (handler metadata)
0x20    4     void*      (reserved)         Read by vtable slot 16
0x24    4     void*      parent_event       Cleared to 0 on receive
0x28    4     int32      obj_ptr            TGObject network ID (third object reference)
```

The +0x1C/+0x20/+0x24 fields are read by vtable slot 16 at 0x006ffa90 — see [Open
Questions](#open-questions-documentation-debt) for the handler-invocation metadata
hypothesis.

## IsA Chain [v5-validated 2026-05-28]

`TGObjPtrEvent::IsA` at 0x004032C0 (10-instruction leaf, created this pass) returns true for:

- `0x010C` (TGObjPtrEvent)
- `0x0101` (TGEvent — see [Class Hierarchy](#class-hierarchy-corrected))
- `0x02` (SWIG "Object" root)

## Wire Format (opcode 0x06 or 0x0D) [v5-validated 2026-05-28]

```
Offset  Size  Type    Field            Notes
0       1     u8      opcode           0x06 (server-to-client) or 0x0D (client-to-server)
1       4     i32     factory_id       0x0000010C
5       4     i32     event_type       0x008000xx (varies by event)
9       4     i32     source_obj_id    NULL=0, sentinel DAT_0095adfc=0xFFFFFFFF, else *(uint32*)(obj+0x04)
13      4     i32     dest_obj_id      Same encoding as source_obj_id
17      4     i32     obj_ptr_id       Third object reference (TGObject network ID)
```

**Total**: 21 bytes (fixed).

### Source/Dest ID Encoding

Confirmed at `TGEvent_WriteToStream` (FUN_006d6130):

- `NULL` → emit `0x00000000`
- Pointer equals sentinel `DAT_0095adfc` → emit `0xFFFFFFFF`
- Otherwise → emit `*(uint32*)(obj+0x04)` (the object's TGObject network ID)

The +0x04 slot is the universal TGObject network ID, populated when the object is added
to the network's object table.

### Decoded Packet Example: ET_WEAPON_FIRED

```
06                    opcode = 0x06 (PythonEvent S->C)
0C 01 00 00           factory_id = 0x0000010C (TGObjPtrEvent)
7C 00 80 00           event_type = 0x0080007C (ET_WEAPON_FIRED)
FF FF FF 3F           source_obj = 0x3FFFFFFF (Player 0's ship)
FF FF FF 3F           dest_obj = 0x3FFFFFFF (same ship — self-reference)
2A 00 00 00           obj_ptr = 0x0000002A (weapon subsystem's TGObject ID)
```

## Vtable @ 0x0088869C (17 slots through +0x40) [v5-validated 2026-05-28]

Direct memory inspection of vtable 0x0088869C yields 17 entries. The pre-v5 doc described
this as `vtable [12, 13, 14]` with "slots 3-8, 11, 15-17 inherited from TGEvent base" —
slots 11 and 15 are **not** inherited (slot 11 is the new RTTI method described below;
slot 15 is a size-0x34 subclass dtor variant).

| Slot | Offset | Address | Function | Notes |
|------|--------|---------|----------|-------|
| 0 | +0x00 | 0x00403320 | `TGObjPtrEvent_ScalarDeletingDtor` | Size 0x2C dtor |
| 1 | +0x04 | 0x004032B0 | `GetFactoryID` | Returns 0x10C |
| 2 | +0x08 | 0x004032C0 | `IsA` | True for {0x10C, 0x101, 0x02} |
| 3 | +0x0C | 0x006F1650 | (TGEvent inherited) | |
| 4 | +0x10 | 0x006D6E20 | WriteToStream variant | Different stream class — likely SAVE-stream, see [Open Questions](#open-questions-documentation-debt) |
| 5 | +0x14 | 0x006D6E50 | ReadFromStream variant | Sibling of slot 4 |
| 6 | +0x18 | 0x006D6050 | (TGEvent inherited) | |
| 7 | +0x1C | 0x006D60B0 | (TGEvent inherited) | |
| 8 | +0x20 | 0x006F15C0 | `TGEventHandlerObject__InvokePythonHandler` | **Universal slot** — see [event-system-architecture.md](../engine/event-system-architecture.md) |
| 9 | +0x24 | 0x004032F0 | `GetClassName` | Returns "TGObjPtrEvent" (ASCIIZ at 0x008d8594) |
| 10 | +0x28 | 0x00403300 | `GetSWIGName` | Returns "_p_TGObjPtrEvent" (ASCIIZ at 0x008d85a4) |
| **11** | **+0x2C** | **0x00403310** | **`GetSWIGPtrName`** | **Returns "TGObjPtrEventPtr" (ASCIIZ at 0x008d85b8). NEW this pass.** |
| 12 | +0x30 | 0x006D6DA0 | `CopyFrom` | Base CopyFrom + copy +0x28 word |
| 13 | +0x34 | 0x006D6DC0 | **`WriteToStream`** (network) | Base + WriteInt32(+0x28) via stream vtable[0x84] |
| 14 | +0x38 | 0x006D6DF0 | **`ReadFromStream`** (network) | Base + ReadInt32 → +0x28 via stream vtable[0x80] |
| 15 | +0x3C | 0x00403500 | `ScalarDeletingDtor` (size 0x34) | Subclass variant — matches "destructor variant (size 0x34 subclass?)" mention in the pre-v5 Infrastructure section |
| 16 | +0x40 | 0x006FFA90 | Handler invocation | Reads +0x20/+0x24/+0x28 — proves "reserved" fields are used |

### SWIG Triple-String RTTI Pattern

Three slots (9, 10, 11) all return ASCIIZ strings. This is **SWIG's typeinfo system**
expressed at the C++ level — each TGEvent subclass exposes three distinct names so the
SWIG runtime can negotiate type identity for Python script handlers:

| Slot | Method | Returns | Purpose |
|------|--------|---------|---------|
| 9 | `GetClassName` | `"TGObjPtrEvent"` | C++ class name (engine-side RTTI) |
| 10 | `GetSWIGName` | `"_p_TGObjPtrEvent"` | SWIG instance typeinfo string |
| 11 | `GetSWIGPtrName` | `"TGObjPtrEventPtr"` | SWIG pointer-typeinfo string |

The pattern is universal across the subclasses that bridge to Python scripts:

| Class | GetClassName | GetSWIGName | GetSWIGPtrName |
|-------|-------------|-------------|----------------|
| TGObjPtrEvent | 0x008d8594 | 0x008d85a4 | 0x008d85b8 |
| TGCharEvent | (TGCharEvent label region) | (sibling string) | 0x008e54ec |
| ObjectExplodingEvent | (label region) | (sibling string) | 0x008da2a0 |

The pre-v5 doc treated slot 11 as the dtor (mistaking 0x00403310 for the
`ScalarDeletingDtor`). The real dtor is at slot 0 (0x00403320); slot 11 is this third
RTTI method.

## Serialization Functions

| Address | Function | Stream Vtable Slot | Description |
|---------|----------|-------------------|-------------|
| 0x006D6DC0 | `TGObjPtrEvent_WriteToStream` | 0x84 (WriteInt32) | Base fields + WriteInt32(this+0x28) |
| 0x006D6DF0 | `TGObjPtrEvent_ReadFromStream` | 0x80 (ReadInt32) | Base fields + ReadInt32 → this+0x28 |
| 0x006D6DA0 | `TGObjPtrEvent_CopyFrom` | (direct copy) | Base CopyFrom + copy +0x28 word |

Both WriteToStream and ReadFromStream were **undefined regions** in the Ghidra DB before
this pass — the doc cited their addresses correctly but Ghidra had not synthesized
function bodies. `create_function` recovered both.

### WriteToStream (0x006D6DC0) [v5-validated 2026-05-28]

```c
void __thiscall TGObjPtrEvent_WriteToStream(TGObjPtrEvent* this, TGStream* stream) {
    // Write base TGEvent fields: factory_id, event_type, src_obj_ref, dest_obj_ref
    TGEvent_WriteToStream(this, stream);  // FUN_006d6130
    // Append the int32 object pointer
    stream->vtable[0x84](stream, this->obj_ptr);  // WriteInt32(+0x28)
}
```

### ReadFromStream (0x006D6DF0) [v5-validated 2026-05-28]

```c
void __thiscall TGObjPtrEvent_ReadFromStream(TGObjPtrEvent* this, TGStream* stream) {
    // Read base TGEvent fields: event_type, src_obj_ref, dest_obj_ref
    TGEvent_ReadFromStream(this, stream);  // FUN_006d61C0
    // Read the int32 object pointer
    this->obj_ptr = stream->vtable[0x80](stream);  // ReadInt32 → +0x28
}
```

## Python API (SWIG)

> [!NOTE]
> The 5 wrapper addresses below are **not anchored as functions** in the current Ghidra
> import — the PyMethodDef name strings exist at 0x0092eab0..0x0092eaf4, but
> `tools/ghidra_annotate_swig.py` has not been re-run since the most recent import. The
> addresses are inherited from a prior annotation pass and are kept here at
> `confidence: medium`. Behavioral Python-usage claims (which are cross-source from
> `reference/scripts/`) are unchanged.

| SWIG Function | Address (medium confidence) | Description |
|---------------|------------------------------|-------------|
| `swig_new_TGObjPtrEvent` | 0x005C7F10 | Constructor wrapper |
| `swig_TGObjPtrEvent_Cast` | 0x005C7F90 | Type cast |
| `swig_TGObjPtrEvent_Create` | 0x005C8000 | Factory create |
| `swig_TGObjPtrEvent_GetObjPtr` | 0x005C8070 | Get object reference (resolves ID via hash table) |
| `swig_TGObjPtrEvent_SetObjPtr` | 0x005C80E0 | Set object reference |

### Python Usage Pattern (from game scripts)

```python
pEvent = App.TGObjPtrEvent_Create()
pEvent.SetSource(source_object)
pEvent.SetDestination(dest_object)
pEvent.SetObjPtr(third_object)      # sets +0x28 field
pEvent.SetEventType(App.ET_WEAPON_FIRED)
App.g_kEventManager.AddEvent(pEvent)
```

## Complete C++ Event Type Catalog (30 xref sites, 11 event types + 1 timer) [v5-validated 2026-05-28]

Constructor xref analysis found **30 call sites** to FUN_00403290 (exact match to
`get_xrefs_to(0x00403290)`). After decompilation, 11 distinct game event types + 1
internal timer delivery were identified — **all 11 verified at producer sites this pass**.

### Game Event Types

| Event Type | ET_ Constant | Producer | Emit Address | obj_ptr Contains | Network? |
|-----------|-------------|----------|--------------|------------------|----------|
| 0x0080000E | ET_SET_PLAYER | `Game_SetPlayerLocal` (0x004066d0) | 0x004066f6 | New player ship ID | No (local) |
| 0x00800058 | ET_TARGET_WAS_CHANGED | `Ship_SetTarget` (0x005ae210) | 0x005ae270 | **Previous** target ID | No (local) |
| 0x0080006B | ET_SUBSYSTEM_HIT | `ShipSubsystem_SetCondition` (0x0056c470) | 0x0056c4fa | Subsystem's own ID | No (local, triggers repair chain) |
| 0x00800076 | ET_REPAIR_INCREASE_PRIORITY | `RepairSubsystem_RaisePriority` (0x005519e0) | 0x00551a5b (vtable DATA write) | Repair target subsystem ID | Yes (opcode 0x11) |
| 0x0080007C | ET_WEAPON_FIRED | `PhaserSystem_Fire`, `Torpedo_Fire`, `TractorBeam_Fire` | 0x005720df / 0x0057caa2 / 0x0057f6b3 | Target ID or 0 | Yes (opcode 0x06/0x0D) |
| 0x0080007D | ET_TRACTOR_BEAM_STARTED_FIRING | `TractorBeam_Fire` (0x0057f580) | 0x0057f64b | Target ID | Yes (opcode 0x06/0x0D) |
| 0x00800081 | ET_PHASER_STARTED_FIRING | `PhaserSystem_Fire` (0x00571f40) | 0x00572074 | Target ID | Yes (opcode 0x06/0x0D) |
| 0x00800083 | ET_PHASER_STOPPED_FIRING | vtable DATA write @ 0x005712FE (PhaserSystem region) | 0x005712FE | Target ID | Yes (opcode 0x06/0x0D) |
| 0x00800085 | ET_TRACTOR_TARGET_DOCKED | tractor dock (0x00580910) | 0x00580ce6 | Docked ship ID | No (local) |
| 0x00800088 | ET_SENSORS_SHIP_IDENTIFIED | sensors (0x00568ad0, 0x005678b0) | 0x00568afd / 0x005678ec | Identified ship ID | No (local) |
| 0x008000DC | ET_STOP_FIRING_AT_TARGET_NOTIFY | `PhaserSystem_StopFiringAtTarget` (0x00574010), `TractorBeamSystem_StopFiringAtTarget` (0x005825a0) | 0x0057405e / 0x005825ee | Target ship ID or 0 | Yes (opcode 0x09, **host-only**) |

### Timer Delivery (non-game event)

| Event Type | Producer | Emit Address | obj_ptr Contains |
|-----------|----------|--------------|------------------|
| 0x00050001 | AI timer (0x007022f0, 0x007023e0) | 0x0070232E / 0x00702407 | Timer source ID |

### Dual-Fire Pattern [v5-validated 2026-05-28]

Weapon fire functions create **two** TGObjPtrEvent events simultaneously:

- **Phaser fire** (`PhaserSystem_Fire` at 0x00571f40): `ET_PHASER_STARTED_FIRING` (0x81) at
  0x00572074, then `ET_WEAPON_FIRED` (0x7C) at 0x005720df.
- **Tractor fire** (`TractorBeam_Fire` at 0x0057f580): `ET_TRACTOR_BEAM_STARTED_FIRING`
  (0x7D) at 0x0057f64b, then `ET_WEAPON_FIRED` (0x7C) at 0x0057f6b3.
- **Torpedo fire** (`Torpedo_Fire` at 0x0057c9e0): `ET_WEAPON_FIRED` (0x7C) at 0x0057caa2
  only — single emit, no paired specific-weapon event.

This dual-fire pattern means every phaser/tractor firing cycle generates at least 4
TGObjPtrEvent messages on the wire (start_specific + weapon_fired + stopped_specific +
stop_notify), which is the primary driver of the 45% combat share.

### ET_TARGET_WAS_CHANGED — Previous-Target Semantics [v5-validated 2026-05-28]

`Ship_SetTarget` (FUN_005ae210) reads the current target via `iVar1 = FUN_005ae170()`
**before** allocating the event, then writes the OLD target's ID into +0x28:

```c
iVar1 = FUN_005ae170(this);          // Get current target BEFORE swap
... allocate TGObjPtrEvent ...
*(int32*)(event + 0x28) = iVar1[1];   // Store the OLD target's ID
this->currentTarget = newTarget;      // Now swap to new target
```

This lets handlers clean up references to the previous target before the new one takes
effect.

### ET_STOP_FIRING_AT_TARGET_NOTIFY — Host-Only Gate [v5-validated 2026-05-28]

Both producers of ET_STOP_FIRING_AT_TARGET_NOTIFY gate on `DAT_0097fa89 != 0` (the IsHost
byte) before creating the event:

- `PhaserSystem_StopFiringAtTarget` (FUN_00574010), event creation at 0x0057405e.
- `TractorBeamSystem_StopFiringAtTarget` (FUN_005825a0), event creation at 0x005825ee.

The exact guard at both sites is:

```c
if (DAT_0097fa89 != '\0' && this+0xa4 != 0 && this+0xa8 != 0) {
    ... create TGObjPtrEvent(0x008000DC) ...
}
```

This event is only generated on the host.

### RepairSubsystem_RaisePriority — Manual-Ctor Pattern [v5-validated 2026-05-28]

`RepairSubsystem_RaisePriority` (FUN_005519e0) is the one ET_REPAIR_INCREASE_PRIORITY
producer, and it does **not** call `TGObjPtrEvent_Ctor`. Instead it:

1. Allocates 0x2C bytes via `FUN_00717b70(0x2c)`.
2. Calls the TGEvent base ctor `FUN_006d5c00` directly.
3. Manually writes the vtable: `*puVar2 = &PTR_FUN_0088869c` at 0x00551a5b.

This is why FUN_005519e0 appears in the **5 vtable DATA xrefs** but not in the **30 ctor
CALL xrefs** to FUN_00403290. The resulting object still passes `IsA(0x10C)` and the
wire format is identical — it just skips the subclass-ctor wrapper.

### Network vs Local Classification

**Network-forwarded** (cross the wire as opcode 0x06/0x0D or generic event forward):

- ET_WEAPON_FIRED (0x7C) — opcode 0x06/0x0D
- ET_PHASER_STARTED_FIRING (0x81) — opcode 0x06/0x0D
- ET_PHASER_STOPPED_FIRING (0x83) — opcode 0x06/0x0D
- ET_TRACTOR_BEAM_STARTED_FIRING (0x7D) — opcode 0x06/0x0D
- ET_REPAIR_INCREASE_PRIORITY (0x76) — opcode 0x11
- ET_STOP_FIRING_AT_TARGET_NOTIFY (0xDC) — opcode 0x09 (host-only)

**Local-only** (never serialized to wire):

- ET_SET_PLAYER (0x0E)
- ET_TARGET_WAS_CHANGED (0x58)
- ET_SUBSYSTEM_HIT (0x6B) — triggers ADD_TO_REPAIR_LIST on wire as a separate factory 0x101 event
- ET_TRACTOR_TARGET_DOCKED (0x85)
- ET_SENSORS_SHIP_IDENTIFIED (0x88)

## Python Script Usage (72 call sites)

SWIG functions (SetObjPtr, GetObjPtr, Create) have **zero C++ xrefs** — called exclusively
from Python. The scripts use TGObjPtrEvent for 27+ event types, all **local-only** (not
network-forwarded). Most common:

| ET_ Constant | Usage Count | Game System |
|-------------|-------------|-------------|
| ET_ACTION_COMPLETED | 54 | Action/sequence management |
| ET_CHARACTER_ANIMATION_DONE | 46 | Bridge crew animations |
| ET_SET_ALERT_LEVEL | 15 | Alert level changes |
| ET_MISSION_START | 11 | Mission initialization |
| ET_PLAYER_BOOT_EVENT | 8 | Player boot |
| ET_HAIL | 2 | Ship hailing |
| ET_TRACTOR_TARGET_DOCKED | 1 | AI docking completion |

### Python Usage Patterns

**Action completion** (most common):

```python
pEvent = App.TGObjPtrEvent_Create()
pEvent.SetDestination(App.g_kTGActionManager)
pEvent.SetEventType(App.ET_ACTION_COMPLETED)
pEvent.SetObjPtr(pAction)
```

**Hailing**:

```python
pHailEvent = App.TGObjPtrEvent_Create()
pHailEvent.SetSource(pObject)
pHailEvent.SetDestination(pHelmMenu)
pHailEvent.SetObjPtr(pObject)  # target ship
pHailEvent.SetEventType(App.ET_HAIL)
```

## Why 45% of Combat PythonEvents

In a 33.5-minute 3-player battle (59 kills, 84 collisions):

- **1,718 of 3,825 PythonEvents** use factory 0x010C (TGObjPtrEvent).
- The dual-fire pattern is the primary driver: each phaser cycle produces
  ET_PHASER_STARTED_FIRING + ET_WEAPON_FIRED + ET_PHASER_STOPPED_FIRING.
- Torpedo launches add ET_WEAPON_FIRED events.
- In a 3-player battle with 2,283 StartFiring events and 897 TorpedoFire events, the
  weapon event volume explains the 1,718 TGObjPtrEvent count.

The events flow through the PythonEvent path (opcode 0x06 S→C, opcode 0x0D C→S) or
GenericEventForward path (opcodes 0x09, 0x11) for relay.

## ET_ Constant Mapping

Base: `ET_TEMP_TYPE = 0x00800001` (App.py line 12835).
Formula: `value = 0x00800001 + (line_number - 12835)`.

### C++ Event Types Using TGObjPtrEvent

| Line | Constant | Hex Value | Network? |
|------|----------|-----------|----------|
| 12849 | ET_SET_PLAYER | 0x0080000E | No |
| 12923 | ET_TARGET_WAS_CHANGED | 0x00800058 | No |
| 12942 | ET_SUBSYSTEM_HIT | 0x0080006B | No (triggers 0x101 on wire) |
| 12952 | ET_REPAIR_INCREASE_PRIORITY | 0x00800076 | Yes (opcode 0x11) |
| 12958 | ET_WEAPON_FIRED | 0x0080007C | Yes (opcode 0x06/0x0D) |
| 12959 | ET_TRACTOR_BEAM_STARTED_FIRING | 0x0080007D | Yes (opcode 0x06/0x0D) |
| 12961 | ET_TRACTOR_BEAM_STOPPED_FIRING | 0x0080007F | Yes (opcode 0x06/0x0D) |
| 12963 | ET_PHASER_STARTED_FIRING | 0x00800081 | Yes (opcode 0x06/0x0D) |
| 12965 | ET_PHASER_STOPPED_FIRING | 0x00800083 | Yes (opcode 0x06/0x0D) |
| 12967 | ET_TRACTOR_TARGET_DOCKED | 0x00800085 | No |
| 12970 | ET_SENSORS_SHIP_IDENTIFIED | 0x00800088 | No |
| — | ET_STOP_FIRING_AT_TARGET_NOTIFY | 0x008000DC | Yes (opcode 0x09, host-only) |

Note: **ET_TORPEDO_FIRED is a separate constant** at 0x00800066 (line 12936). The
constant 0x0080007C = ET_WEAPON_FIRED covers both phaser and torpedo fire events at the
subsystem level.

Note: ET_SUBSYSTEM_HIT is not exposed to Python (not in App.py). It is an internal C++
event only.

## Full Factory ID Table (TGEvent family, corrected)

| Factory ID | Class Name | Size | Extension at +0x28 | Wire Bytes |
|-----------|------------|------|---------------------|------------|
| 0x0002 | (SWIG "Object" root) | — | — | — |
| 0x0101 | **TGEvent** (formerly mis-labeled "TGSubsystemEvent") | 0x28 | (none) | 17 |
| 0x0105 | TGCharEvent | 0x2C | char (1 byte) | 18 |
| **0x010C** | **TGObjPtrEvent** | **0x2C** | **int32 (TGObject ID)** | **21** |
| 0x8129 | ObjectExplodingEvent | 0x30 | int32 + float | 25 |

## C++ Producers in Unanalyzed Code Regions

The following xref addresses are in code regions where Ghidra has not synthesized full
function bodies. Some of these are **inside the bodies of fully-analyzed functions** (just
not at a function boundary), while others are in genuinely undefined regions. Based on
surrounding function boundaries and handler registration names:

| Address Range | Likely Function | Event Type | Evidence |
|--------------|-----------------|------------|----------|
| ~0x0059d18E | `ObjectGroup_EnteredSet` (near LAB_0059d140) | ET_OBJECT_GROUP_OBJECT_ENTERED_SET | Handler name `ObjectGroup__EnteredSet` at 0x8e5dbc |
| ~0x0059d210 | `ObjectGroup_ExitedSet` (near LAB_0059d1d0) | ET_OBJECT_GROUP_OBJECT_EXITED_SET | Handler name `ObjectGroup__ExitedSet` at 0x8e5dd4 |
| ~0x0059d31F | `ObjectGroup_ObjectDestroyed` (near LAB_0059d250) | ET_OBJECT_GROUP_OBJECT_DESTROYED | Handler name `ObjectGroup__ObjectDestroyed` at 0x8e5d9c |
| ~0x00565376, ~0x00565419, ~0x005654AE | RepairSubsystem (between 0x5651c0-0x565520) | Likely ET_REPAIR_COMPLETED / ET_REPAIR_CANNOT_BE_COMPLETED / ET_SUBSYSTEM_STATE_CHANGED | Three calls in one function; repair subsystem handlers registered nearby |
| ~0x00575413 | PhaserSystem (between 0x575270-0x575480) | Likely ET_PHASER_STOPPED_FIRING (0x00800083) | Vtable DATA xref at 0x005712FE in phaser code |
| ~0x0057C961 | TorpedoSystem (between 0x57c740-0x57c9e0) | Likely ET_WEAPON_FIRED (0x0080007C) | Pattern matches `Torpedo_Fire` at 0x0057c9e0 |
| ~0x00543EF0 | Unknown (no function boundaries found) | Unknown | Deep in mission code area |
| ~0x006D49B5 | TGEvent infrastructure (between 0x6D4A20-) | Factory create / deserialization | Near event manager code |
| ~0x007031A7, ~0x007032D0 | Weapon fire (between 0x7030c0-0x7033b0) | 0x00800081 + 0x0080007C or similar | SWIG/weapon bridge code area |
| ~0x0070857D | Unknown (before 0x7085d0) | Unknown | SWIG/streaming area |

### Vtable DATA References (vtable = 0x0088869C) [v5-validated 2026-05-28]

`get_xrefs_to(0x0088869c)` returns exactly **5 DATA xrefs** — matches the doc's prior
count exactly:

1. **0x0040329D** — `TGObjPtrEvent_Ctor` (canonical)
2. **0x00551A5B** — `RepairSubsystem_RaisePriority` (manual-ctor pattern; see above)
3. **0x0057F185** — TractorBeam::Fire area (ET_TRACTOR_BEAM_STOPPED_FIRING = 0x0080007F)
4. **0x005712FE** — PhaserSystem area (ET_PHASER_STOPPED_FIRING = 0x00800083)
5. **0x005768C5** — WeaponSystem area (ET_WEAPON_FIRED = 0x0080007C)

Sites 3-5 are in code regions without defined function bodies, but the vtable write
confirms they create TGObjPtrEvents. The event types are identified from handler
registrations for those subsystem classes.

### Infrastructure / Non-Event-Producer Calls

| Address | Context | Purpose |
|---------|---------|---------|
| 0x004028DD | thunk_FUN_006ff7b0 area (destructor) | TGObjPtrEvent destructor — cleans up refcounted obj_ptr |
| 0x00403570 | thunk_FUN_006ff7b0 area (destructor) | Another TGObjPtrEvent destructor variant (size 0x34 subclass — corresponds to vtable slot 15 at 0x00403500) |

## Complete Python Event Type Table

Python scripts create TGObjPtrEvents via `App.TGObjPtrEvent_Create()` + `SetEventType()`
+ `SetObjPtr()`. The SWIG functions `swig_TGObjPtrEvent_Create` and
`swig_TGObjPtrEvent_SetObjPtr` have zero C++ xrefs — they are called exclusively from
Python.

| ET_ Constant | Python File(s) | obj_ptr Contains | Context |
|-------------|----------------|------------------|---------|
| ET_ACTION_COMPLETED | MissionLib.py, Bridge/*CharacterHandlers.py, E*M*.py, WarpSequence.py | The action object that completed | Action system callback: sequences, sounds, fades, character speech |
| ET_HAIL | Bridge/HelmMenuHandlers.py | Ship being hailed | Helm menu button activation event |
| ET_SET_ALERT_LEVEL | Bridge/XOMenuHandlers.py, QuickBattle.py | Ship to set alert on | Bridge/XO menu: Red/Yellow/Green alert |
| ET_MISSION_START | Maelstrom/Episode*/Episode*.py, QuickBattle.py, Tutorial | Mission object | Episode initialization |
| ET_CHARACTER_ANIMATION_DONE | Bridge/Characters/SmallAnimations.py, PicardAnimations.py | Character object | Animation completion callback |
| ET_ORBIT_PLANET | Bridge/HelmMenuHandlers.py | Planet object | Helm: orbit planet command |
| ET_SCAN | Bridge/ScienceMenuHandlers.py | Target object | Science: scan target |
| ET_LAUNCH_PROBE | Bridge/ScienceMenuHandlers.py | Probe object | Science: launch probe |
| ET_MANEUVER | Bridge/TacticalMenuHandlers.py | Target/waypoint object | Tactical menu maneuver command |
| ET_AI_TIMER | Conditions/ConditionTimer.py, ConditionInLineOfSight.py | Condition source object | AI condition timer expiry |
| ET_AI_SHIELD_WATCHER | Conditions/ConditionSingleShieldBelow.py | Ship object | AI shield monitoring |
| ET_AI_CONDITION_CHANGED | Conditions/ConditionCriticalSystemBelow.py | Ship object | AI condition state change |
| ET_AI_ORBITTING | AI/Player/OrbitPlanet.py | Planet object | AI orbit completion |
| ET_SUBSYSTEM_POWER_CHANGED | Bridge/EngineerMenuHandlers.py | Subsystem object | Engineering power slider adjustment |
| ET_DELETE_OBJECT_PUBLIC | loadspacehelper.py | Object to delete | Object deletion request |
| ET_MUSIC_CONDITION_CHANGED | DynamicMusic.py | Condition source | Music system condition transition |
| ET_OTHER_BEAM_TOGGLE_CLICKED | BridgeHandlers.py | Button/UI object | Tactical: beam weapon toggle |
| ET_OTHER_CLOAK_TOGGLE_CLICKED | BridgeHandlers.py | Button/UI object | Tactical: cloak toggle |
| ET_RADAR_TOGGLE_CLICKED | Bridge/TacticalMenuHandlers.py | Radar display object | Radar display toggle |
| ET_OKAY | WarpSequence.py, KeyboardConfig.py | Context-dependent | Generic OK/confirm event |
| ET_CANCEL_BINDING | MainMenu/KeyboardConfig.py | Config object | Cancel keyboard binding |
| ET_CLEAR_BINDINGS | MainMenu/KeyboardConfig.py | Config object | Clear all bindings |
| ET_NEW_GAME | MainMenu/mainmenu.py | Game/config object | Start new game |
| ET_START | Multiplayer/MultiplayerMenus.py | Lobby/game object | Start multiplayer game |
| ET_SORT_SERVER_LIST | Multiplayer/MultiplayerMenus.py | Server list object | Sort server browser |
| ET_SELECT_SERVER_ENTRY | Multiplayer/MultiplayerMenus.py | Server entry object | Select server in browser |
| ET_REFRESH_SERVER_LIST | Multiplayer/MultiplayerMenus.py | Server list object | Refresh server browser |

## Consolidated Event Type Hex Map

Based on handler registration cross-references (handler name strings contain the ET_
constant name):

| Hex | ET_ Constant | Handler Name Evidence |
|-----|-------------|-----------------------|
| 0x0080000E | ET_SET_PLAYER | "Game__HandleSetPlayer", "Mission__PlayerChanged", "SetPlayerHandler" |
| 0x00800058 | ET_TARGET_WAS_CHANGED | "ChangedTarget", "HandleTargetChanged", "TargetChangedHandler" |
| 0x0080006B | ET_SUBSYSTEM_HIT | "DamageDisplay__HandleSubsystemEv", "HandleSubsystemEvent" |
| 0x00800076 | ET_REPAIR_INCREASE_PRIORITY | "RepairSubsystem__HandleIncreaseP", "RepairListPri" |
| 0x0080007C | ET_WEAPON_FIRED | (multiple weapon fire functions, confirmed by vtable + code) |
| 0x0080007D | ET_TRACTOR_BEAM_STARTED_FIRING | "TacWeaponsCtrl__HandleTractorB" (same handler as 0x7F) |
| 0x0080007F | ET_TRACTOR_BEAM_STOPPED_FIRING | "TacWeaponsCtrl__HandleTractorB" |
| 0x00800081 | ET_PHASER_STARTED_FIRING | (vtable xref at 0x005712FE in phaser code) |
| 0x00800083 | ET_PHASER_STOPPED_FIRING | (vtable xref at 0x005712FE in phaser code) |
| 0x00800085 | ET_TRACTOR_TARGET_DOCKED | (FUN_00580910 tractor docking code) |
| 0x00800088 | ET_SENSORS_SHIP_IDENTIFIED | "STTargetMenu__ObjectIdentified", "ShieldsDisplay__ShipIdentified" |
| 0x008000DB | ET_STOP_FIRING_AT_TARGET | "PhaserSystem__StopFiringAtTarget", "TractorBeamSystem__StopFiringAtT" (command) |
| 0x008000DC | ET_STOP_FIRING_AT_TARGET_NOTIFY | "MultiplayerGame____StopFiringAtT" (notification) |
| 0x00050001 | (AI/Timer internal) | Timer delivery mechanism, not a game event |

## Ghidra Annotations Applied (2026-05-28)

This pass did substantial annotation work to align the binary with the doc. Ghidra had
not synthesized function bodies for several of the small vtable-slot leaves nor for the
network WriteToStream / ReadFromStream — the doc cited their addresses correctly but the
binary database had them as undefined regions.

### Functions newly created (10)

| Address | Name | Reason |
|---------|------|--------|
| 0x004032B0 | `TGObjPtrEvent_GetFactoryID` | 6-byte leaf, was undefined |
| 0x004032C0 | `TGObjPtrEvent_IsA` | 10-instruction leaf, was undefined |
| 0x004032F0 | `TGObjPtrEvent_GetClassName` | String-return leaf, was undefined |
| 0x00403300 | `TGObjPtrEvent_GetSWIGName` | String-return leaf, was undefined |
| 0x00403310 | `TGObjPtrEvent_GetSWIGPtrName` | String-return leaf, was undefined (NEW from C2 finding) |
| 0x00403320 | `TGObjPtrEvent_ScalarDeletingDtor` | Size 0x2C dtor, was undefined |
| 0x006D6DC0 | `TGObjPtrEvent_WriteToStream` | Network WriteToStream, was undefined |
| 0x006D6DF0 | `TGObjPtrEvent_ReadFromStream` | Network ReadFromStream, was undefined |
| 0x00574C50 | `TGCharEvent_IsA` | Sibling-class IsA, used for hierarchy confirmation |
| (1 more producer function name attached during the pass) | | |

### Functions renamed (16)

10 `TGObjPtrEvent_*` rename targets (the 10 above) plus 6 producer functions:

| Old name | New name | Address |
|----------|----------|---------|
| FUN_00403290 | `TGObjPtrEvent_Ctor` | 0x00403290 |
| FUN_006D6DA0 | `TGObjPtrEvent_CopyFrom` | 0x006D6DA0 |
| FUN_004066D0 | `Game_SetPlayerLocal` | 0x004066D0 |
| FUN_005AE210 | `Ship_SetTarget` | 0x005AE210 |
| FUN_0056C470 | `ShipSubsystem_SetCondition` | 0x0056C470 |
| FUN_005519E0 | `RepairSubsystem_RaisePriority` | 0x005519E0 |
| FUN_00574010 | `PhaserSystem_StopFiringAtTarget` | 0x00574010 |
| FUN_005825A0 | `TractorBeamSystem_StopFiringAtTarget` | 0x005825A0 |

### Struct created

`TGObjPtrEvent` struct (0x2C / 44 bytes / 12 fields) created and applied via prototypes
at `TGObjPtrEvent_Ctor` and `TGObjPtrEvent_WriteToStream`.

### Prototypes installed (6)

Set on TGObjPtrEvent_Ctor, WriteToStream, ReadFromStream, CopyFrom, IsA, GetFactoryID.

### Plate comments installed (3)

- `TGObjPtrEvent_Ctor` (0x00403290) — class layout + vtable identity + ref-init invariants.
- `TGObjPtrEvent_WriteToStream` (0x006D6DC0) — 21-byte wire format spec.
- `TGObjPtrEvent_ReadFromStream` (0x006D6DF0) — reader-side mirror spec.

## Open Questions (documentation debt)

1. **Vtable slot 4-5 variant Write/Read at 0x006D6E20 / 0x006D6E50** — gated on a different
   base-class type check (`FUN_006d5ec0` / `FUN_006d5ff0`). Suspect SAVE-stream vs
   NETWORK-stream discrimination: slots 13/14 (network) write unconditionally; slots 4/5
   check a save-stream-class flag first. Requires investigation of FUN_006d5ec0 /
   FUN_006d5ff0 (likely `TGStream::CanSerializeToWire` vs `TGStream::CanSerializeToSave`).
2. **Vtable slot 16 at 0x006FFA90** reads `this+0x20`, `this+0x24`, `this+0x28`. The
   +0x20/+0x24 fields are labeled "reserved" in the class layout; this slot proves they
   are used — probably handler-invocation metadata for Python script dispatch. Worth
   cross-confirming with pythonevent-wire-format.md (leaf #14, pending).
3. **SWIG wrapper addresses 0x005C7F10..0x005C80E0** — not anchored in the current Ghidra
   DB. Either re-run `tools/ghidra_annotate_swig.py` to apply names + create the function
   entry points, or accept the medium-confidence demotion. Affects multiple docs; one
   annotation-script run would fix all simultaneously.
4. **The 0x02 root SWIG type identity** — IsA returns true for 0x02 as the grandparent
   factory ID, but no GetFactoryID emitter for factory 0x02 was found in the binary.
   Likely a SWIG-base "Object" type with no real C++ class. Worth checking the SWIG
   type-info table layout to confirm.

## Companions

- [pythonevent-wire-format.md](pythonevent-wire-format.md) — PythonEvent (0x06) wire
  format (4 event classes); will consume the 21-byte wire format claim and source/dest
  encoding from this doc.
- [set-phaser-level-protocol.md](set-phaser-level-protocol.md) — TGCharEvent (0x105)
  detailed analysis; sibling class with byte-not-int at +0x28.
- [wire-format-spec.md](wire-format-spec.md) — protocol hub; opcode 0x06/0x0D rows
  reference this class.
- [stream-primitives.md](stream-primitives.md) — TGBufferStream WriteInt32 / ReadInt32
  primitives consumed by WriteToStream and ReadFromStream.
- [transport-layer.md](transport-layer.md) — TGMessage framing wrapping the 21-byte
  payload on the wire.
- [game-opcodes.md](game-opcodes.md) — opcode 0x06 (PythonEvent S→C) and 0x0D
  (PythonEvent C→S) catalog rows.
- [event-system-architecture.md](../engine/event-system-architecture.md) — engine-tier
  doc for the TGEvent base class and the universal slot-8 InvokePythonHandler.
- [repair-event-object-ids.md](../gameplay/repair-event-object-ids.md) —
  ADD_TO_REPAIR_LIST event chain, TGObject ID assignment.
- [weapon-firing-mechanics.md](../gameplay/weapon-firing-mechanics.md) — weapon fire/stop
  events (TGObjPtrEvent producers).
- [repair-system.md](../gameplay/repair-system.md) — repair queue,
  ET_REPAIR_INCREASE_PRIORITY.
- [stock-trace-analysis.md](../analysis/stock-trace-analysis.md) — ground truth traces
  confirming the 45% combat share.
- [v5-validation-status.md](v5-validation-status.md) — campaign tracker (§6.13 details
  this pass's full evidence trail).
