---
name: pythonevent-wire-format-validation-20260528
description: Protocol doc #14 (first leaf) v5 validation — 0 wire corrections, 5 non-wire refinements, MpgameHandlePythonEvent renamed; key learning is hierarchy-fabrication cascade from mid #13 and source-vs-dest WriteObjectRef asymmetry
metadata:
  type: project
---

# pythonevent-wire-format.md (Protocol doc #14, FIRST LEAF) Validation — 2026-05-28

**Why:** First leaf in the v5 protocol campaign. Doc has ~280 load-bearing claims
covering 4 event classes (TGEvent base / TGCharEvent / TGObjPtrEvent /
ObjectExplodingEvent), polymorphic dispatch via factory ID first, two producer paths
(HostEventHandler + ObjectExplodingHandler) and the LOCAL-ONLY receiver FUN_0069F880.

**How to apply:** When validating leaf docs that wrap a mid-tier class (here, TGObjPtrEvent
in doc #13), DO NOT re-derive the mid-tier content. Cite by reference and focus the dig on:
(1) the polymorphic dispatcher, (2) the producer chain, (3) wire-format byte counts per class.
Each class's WriteToStream decompile gives byte-exact size in 30 seconds.

## Headline outcome

- **Zero wire-format corrections.** All 4 class sizes confirmed byte-by-byte:
  - TGEvent base = 16B payload + 1B opcode = 17B wire (`vtable+0x64` ×2 + `vtable+0x84` ×2)
  - TGCharEvent  = 17B payload + 1B opcode = 18B wire (base + `vtable+0x54` WriteChar)
  - TGObjPtrEvent = 20B payload + 1B opcode = 21B wire (base + `vtable+0x84` WriteInt)
  - ObjectExploding = 24B payload + 1B opcode = 25B wire (base + `vtable+0x6C` WriteInt + `vtable+0x74` WriteFloat)
- Five non-wire corrections (C1 hierarchy fabrication cascade / C2 IsA chain / C3 source-dest
  encoding asymmetry / C4 receiver flow naming / C5 in-memory vs wire size ambiguity)
- Status: validated -> `partial`. Doc remains useful, no wire-format pivot needed.

## Critical pattern — TGEvent base GetFactoryID at 0x006D5CE0

Byte-by-byte: `MOV EAX, 0x101; RET`. **This is TGEvent base itself, NOT "TGSubsystemEvent".**
The mid #13 correction (doc #13 C1) cascades through this doc — anywhere the doc reads
"TGSubsystemEvent (factory 0x101)" it should read "TGEvent (factory 0x101)". The TGSubsystemEvent
vtable address 0x008932A4 has ZERO xrefs in the binary (confirmed). The class doesn't exist.

## Source vs dest WriteObjectRef encoding asymmetry

Doc's "WriteObjectRef" rule is 3-case (NULL / sentinel / valid). Binary FUN_006D6130 disasm shows:
- **SOURCE** field (this+0x08): TWO cases — `NULL -> 0, else *(obj+4)`. NO sentinel branch.
- **DEST** field (this+0x0C): THREE cases — `sentinel -> -1, NULL -> 0, else *(obj+4)`.

Practical impact: minimal (producers don't manually set source-to-sentinel). But the doc's
single rule misrepresents the actual code path. Source field NEVER gets the -1 sentinel.

## Receiver flow — FUN_0069F880 (now MpgameHandlePythonEvent)

8-step receiver, LOCAL-ONLY (no SendToGroup):
1. `TGBufferStream_swig_GetBufferAndSize(msg)` -> `(pBuf, length)`
2. `TGBufferStream_swig_Ctor(stack)`
3. `TGBufferStream_swig_OpenBuffer(stack, pBuf+1, length-1)`  (skip opcode byte)
4. `event = ReadObjectFromStream(stack)`  -> reads factory_id, calls `TGFactoryCreate`,
   invokes `event->vtable[+0x38]` (ReadFromStream)
5. `ResolveObjectRefs(event)`  -> `event->vtable[+0x18]` (source) + `event->vtable[+0x1C]` (dest)
6. `event[+0x24] = 0`  (clear parent_event pointer)
7. `Event::SelfDispatch(event)`  -> `event->dest_obj->vtable[+0x50](event)`  (NOT a global PostEvent)
8. Refcount drop -> if 0, call `event->vtable[+0x00](1)` (scalar-deleting dtor)

Step 7 is what the doc calls `EventManager::PostEvent` at FUN_006DA300, but the decompile
reveals it's actually the event invoking itself on its dest object's vtable+0x50 handler.
"Event self-dispatch" or "TGEvent::Dispatch" is the more accurate name.

## Producer functions ARE byte-confirmed but UNDEFINED in DB

Both HostEventHandler (0x006A1150) and ObjectExplodingHandler (0x006A1240) are NOT defined
as functions in the current Ghidra DB but exist as raw disassembly that produces clean code.
The xrefs from FUN_0069efe0 RegisterHandlers identify them as LAB_006a1150 and LAB_006a1240
(label form). Decompile fails but disasm walks fine.

This is the same pattern observed in earlier validations: annotation scripts not applied to
current import; many `LAB_` xrefs are actually known functions. The doc cites them by address
and the addresses are correct.

## Stream vtable SWIG variant slot map (verified)

vtable @ 0x00895C58 (16-byte alignment, 35+ slots):
- +0x60 (slot 24): 0x006CF640 ReadInt (raw 4-byte)
- +0x64 (slot 25): 0x006CF830 WriteInt (raw 4-byte)
- +0x68 (slot 26): 0x006CF670 ReadInt
- +0x6C (slot 27): 0x006CF870 WriteInt
- +0x70 (slot 28): 0x006CF6B0 ReadFloat
- +0x74 (slot 29): 0x006CF8B0 WriteFloat
- +0x80 (slot 32): 0x006CF6A0 ReadInt-virtual-dispatcher (forwards to +0x68)
- +0x84 (slot 33): 0x006CF930 WriteInt-virtual-dispatcher (forwards to +0x6C)
- +0x50 (slot 20): 0x006CF540 ReadChar 1-byte
- +0x54 (slot 21): 0x006CF730 WriteChar 1-byte

NOTE: +0x80/+0x84 LOOK like polymorphic hooks but in this SWIG class they just thunk to
+0x68/+0x6C. Effectively all int operations write 4 raw bytes.

## ObjectExploding 8-byte extension

Wire-extension uses `vtable+0x6C` (WriteInt — raw 4 bytes for firing_player_id) and
`vtable+0x74` (WriteFloat — raw 4 bytes for lifetime). NOT `vtable+0x84` like the base
TGEvent uses for source/dest refs. The extension is plain raw int + float, no obj-ref
encoding.

## ObjectExplodingEvent IsA returns true for 3 IDs not 2

Doc says "true for 0x8129, 0x02". Binary disasm at 0x0043F8F0:
```
CMP EAX, 0x8129  ; JNZ -> next
CMP EAX, 0x101   ; JNZ -> next  *** doc missed this branch
CMP EAX, 0x2     ; SETZ AL
```
The 0x101 branch confirms ObjectExploding inherits from TGEvent (0x101), not just from the
generic NiObject root. Same chain shape as TGCharEvent and TGObjPtrEvent.

## Pattern reuse signals

- When a doc says "X is the WriteRef encoder", check whether it has separate code paths for
  source field vs dest field. The 2-vs-3 case asymmetry shows up in multiple TGEvent base
  serializers.
- When a doc cites a hierarchy diagram with intermediate class names like "TGSubsystemEvent",
  always GetFactoryID-disasm the base ctor to see what factory ID it actually emits.
  Intermediate classes that only exist on paper get identified this way.
- For PYHONEVENT-style polymorphic transports, the FACTORY_ID byte-position determines the
  whole wire format. Confirmed factory IDs route through `TGFactoryCreate(factory_id, 0)` at
  0x006F13E0; the function looks up the registered factory in a hash table from a global at
  `DAT_0099A578`. The 4 known factories registered: 0x101 (TGEvent), 0x105 (TGCharEvent),
  0x10C (TGObjPtrEvent), 0x8129 (ObjectExplodingEvent).
- "NoMe" group string lives at 0x008E5528 ASCIIZ "NoMe". "Forward" at 0x008D94A0. These are
  the two groups MultiplayerGame_Ctor creates when host (`DAT_0097fa8a != 0`).

## Anchors used (cross-doc)

- [[engine-snapshot-20260528]] — TGEvent vtable 0x00895FF4
- [[event-system-validation-20260528]] — Event system architecture (engine doc #8)
- [[tgobjptrevent-class-validation]] (this conversation's task prompt summary of mid #13) —
  TGObjPtrEvent class layout, factory 0x10C, vtable 0x0088869C
- [[game-opcodes-validation-20260528]] — Dispatcher jump table slots 6 (0x06) and 13 (0x0D)
- [[tgmessage-routing-validation-20260528]] — LOCAL-ONLY dispatch claim
