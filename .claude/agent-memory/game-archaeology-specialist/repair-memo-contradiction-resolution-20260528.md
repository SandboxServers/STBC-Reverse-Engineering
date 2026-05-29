---
name: repair-memo-contradiction-resolution-20260528
description: Definitive byte-level resolution of ADD_TO_REPAIR_LIST (0x008000DF) wire-format contradiction between leaf #16 (17B/0x0101) and mid-batch repair (16B/0x0100) memos. Both memos were partially wrong.
metadata:
  type: project
---

# Repair Memo Contradiction Resolution — ADD_TO_REPAIR_LIST Wire Format

**Date:** 2026-05-28  
**Branch:** analysis/authority-audit-20260226  
**Binary:** STBC.exe (image base 0x00400000)  
**Status:** RESOLVED — byte-level evidence captured

## TL;DR Verdict

For PythonEvent (opcode 0x06) carrying event_type 0x008000DF ADD_TO_REPAIR_LIST:

| Field | Value | Anchor |
|-------|-------|--------|
| **Factory ID on wire** | **0x00000101** (i32) | TGEvent vtable slot 1 @ 0x006D5CE0 returns `0x101` |
| **Wire payload size** | **16 bytes** (after the 0x06 opcode byte) | TGEvent::WriteToStream @ 0x006D6130 writes 4×i32 |
| **Class used** | TGEvent base (NOT TGObjPtrEvent, NOT TGCharEvent) | FUN_00565900 (AddToRepairList_MP) calls FUN_006D5C00 (TGEvent_Ctor) directly |
| **In-memory size** | 0x28 bytes (40) | `TGAlloc(0x28, "UNKNOWN", 0)` at 0x0056592C |

**Both prior memos contained errors. Neither was fully correct.**

## Wire Layout (decisive)

```
Offset  Size  Field          Value/Source
+0      1     opcode         0x06 (PythonEvent)
+1      4     factory_id     0x00000101 (TGEvent type ID — vtable slot 1 returns this)
+5      4     event_type     0x008000DF (ADD_TO_REPAIR_LIST — copied from this+0x10)
+9      4     source_obj_id  *(uint*)(this+0x8)->+0x04 or 0 if null
+13     4     dest_obj_id    *(uint*)(this+0xc)->+0x04 or 0 (null) or 0xFFFFFFFF (sentinel)
─────────────────────────────────────────────────────────────────────────
TOTAL: 1 (opcode) + 16 (TGEvent payload) = 17 bytes on the wire
```

The TOTAL packet byte count is 17 (= 1 opcode + 16 payload). The PAYLOAD byte count (excluding opcode) is 16. This dual-framing is the root of the contradiction.

## Byte-Level Evidence Chain

### 1. FUN_00565900 (AddToRepairList_MP) — the producer

Disassembled at `0x00565900` (decompiled signature: `void __thiscall AddToRepairList_MP(target, src)`):

```asm
0056592c: PUSH 0x28               ; TGAlloc size = 40 bytes (TGEvent — NOT 44 for TGObjPtrEvent)
00565927: PUSH "UNKNOWN"          ; string @ 0x008d858c — confirmed via read_memory
00565947: CALL 0x006d5c00         ; TGEvent_Ctor (NOT TGObjPtrEvent_Ctor at 0x006bb840)
0056594c: MOV ESI, EAX
00565955: MOV [ESI+0x10], 0x8000df ; event_type = 0x008000DF (ADD_TO_REPAIR_LIST)
0056595c: CALL 0x006d62b0          ; SetDest(target)
00565964: CALL 0x006d6270          ; SetSource(src)
0056596f: CALL 0x006da2a0          ; TGEventManager::PostEvent(ESI)
```

Decisive: this is a **base TGEvent**, allocated 40 bytes, NOT a TGObjPtrEvent (which would allocate 44 bytes and install vtable 0x00895848).

### 2. TGEvent_Ctor @ 0x006D5C00 — class identity

Disassembled in-memory field init:
```
006d5c2a: MOV [EBP+0x00], 0x00895FF4  ; vtable (TGEvent base vtable)
006d5c31: MOV [EBP+0x10], 0           ; event_type init to 0 (caller overwrites with 0x8000DF)
006d5c34: MOV [EBP+0x08], 0           ; source ptr init
006d5c37: MOV [EBP+0x0c], 0           ; dest ptr init
006d5c3a: MOV [EBP+0x14], 0xBF800000  ; float -1.0f (lifetime / unused)
006d5c41-006d5c4f: zero +0x18..+0x24
```

The factory_id 0x101 is **NOT stored in any in-memory field by the ctor**. It is recovered at serialization time by calling vtable slot 1 (GetTypeId).

### 3. Vtable @ 0x00895FF4 — GetTypeId / IsA / WriteToStream / ReadFromStream

Memory dump @ 0x00895FF4 verified via `read_memory`:
| Slot | Offset | Address | Function |
|------|--------|---------|----------|
| 0 | +0x00 | 0x006D5D40 | dtor |
| **1** | **+0x04** | **0x006D5CE0** | **GetTypeId → returns 0x00000101** |
| 2 | +0x08 | 0x006D5CF0 | IsA (matches 0x101, else falls back to TGObject 0x02) |
| 12 | +0x30 | 0x006D6230 | CopyFrom |
| **13** | **+0x34** | **0x006D6130** | **WriteToStream** |
| **14** | **+0x38** | **0x006D61C0** | **ReadFromStream** |

`GetTypeId` body (5 bytes):
```asm
006d5ce0: B8 01 01 00 00          MOV EAX, 0x00000101
006d5ce5: C3                      RET
```

This is the value written into the network buffer as the factory_id. **CONFIRMED 0x101, NOT 0x100.**

### 4. TGEvent::WriteToStream @ 0x006D6130 — write side

```asm
006d613b: MOV EAX, [EDI]          ; this->vtable
006d613d: CALL [EAX + 0x04]       ; GetTypeId → returns 0x00000101
006d6140: PUSH EAX                ; arg = 0x101
006d6143: CALL [EBX + 0x64]       ; stream->WriteInt(0x101) — 4 bytes  [FIELD 1]
006d6146: MOV EAX, [EDI + 0x10]   ; event_type
006d614b: PUSH EAX
006d614e: CALL [EDX + 0x64]       ; stream->WriteInt(event_type) — 4 bytes  [FIELD 2]
006d6151: MOV EAX, [EDI + 0x08]   ; source ptr
006d6154-006d6156: TEST EAX/JZ    ; if NULL, EAX stays NULL
006d6158: MOV EAX, [EAX + 0x04]   ; else EAX = source->id
006d615d: PUSH EAX
006d6160: CALL [EDX + 0x84]       ; stream->WriteId(source_id) — 4 bytes  [FIELD 3]
006d6166: MOV EDI, [EDI + 0x0C]   ; dest ptr
006d6169: MOV EAX, [0x0095ADFC]   ; broadcast sentinel
006d616e-006d6170: CMP/JZ         ; if EDI==sentinel, write 0xFFFFFFFF
006d6172-006d6174: TEST/JNZ       ; if EDI==NULL, write 0
006d6189: MOV EDI, [EDI + 0x04]   ; else EDI = dest->id
006d6191: CALL [EAX + 0x84]       ; stream->WriteId(dest_id) — 4 bytes  [FIELD 4]
```

**Four fields × 4 bytes each = exactly 16 bytes of payload.** No extra byte. No padding. No alignment.

### 5. TGEvent::ReadFromStream @ 0x006D61C0 — read side mirror

```asm
006d61cc: CALL [EAX + 0x60]       ; stream->ReadInt → event_type (4 bytes)
006d61cf: MOV [EDI + 0x10], EAX
006d61d6: CALL [EDX + 0x80]       ; stream->ReadId → source_id (4 bytes)
006d61dc: MOV [EDI + 0x08], EAX
006d61e3: CALL [EAX + 0x80]       ; stream->ReadId → dest_id (4 bytes)
006d61e9: MOV [EDI + 0x0C], EAX
```

ReadFromStream reads ONLY 3 fields (12 bytes). The 4th field — the factory_id — is read by the **outer** TGFactory_DeserializeObject @ 0x006D6200 **before** ReadFromStream is even called:

```asm
006d620a: CALL [EAX + 0x60]       ; stream->ReadInt → factory_id (4 bytes)
006d620f: PUSH EAX
006d6210: CALL TGFactoryCreate     ; allocate concrete class by factory_id
006d621f: CALL [EDX + 0x38]        ; event->ReadFromStream(stream) — fills body
```

Total wire payload consumed by the inbound path: 4 (outer factory) + 12 (inner ReadFromStream) = **16 bytes**. Symmetric with WriteToStream.

### 6. Cross-check: the v5 plate comment on MpgameHandlePythonEvent

The plate comment on `MpgameHandlePythonEvent @ 0x0069F880` (v5-validated 2026-05-28 per its own footer) already contains the definitive wire layout:

```
Wire layout (after opcode byte 0x06 or 0x0D):
  +0   i32  factory_id     0x00000101 / 0x105 / 0x10C / 0x8129
  +4   i32  event_type     ET_xxx constant (e.g. 0x008000DF for ADD_TO_REPAIR_LIST)
  +8   i32  source_obj_id
  +12  i32  dest_obj_id
  +16  ...  class-specific extension:
              TGEvent (0x101) — none, 16 bytes total
              TGCharEvent (0x105) — +1 byte char_value, 17 bytes
              TGObjPtrEvent (0x10C) — +4 byte obj_ptr_id (i32), 20 bytes
              ObjectExploding (0x8129) — +4 firing_player_id + +4 lifetime, 24 bytes
```

This plate comment was already correct on this exact question. The contradiction was between two derivative archaeology memos that disagreed with each other AND with the plate.

## Verdict on the Two Memos

### Memo A — `gameplay-leaf-repair-event-ids-validation-20260528.md` (leaf #16)
**Claim:** factory 0x0101, **17 bytes** payload  
**Verdict:** Factory ID **CORRECT** (0x0101). Byte count **WRONG** (17 should be 16 for payload, OR 17 should be relabeled as total-wire-including-opcode).

**Likely error mechanism:** Conflated TOTAL on-wire byte count (1 opcode + 16 payload = 17) with PAYLOAD byte count. The memo's "17 bytes — byte-accurate" probably came from counting bytes from the opcode byte forward in a hex dump rather than from the payload start. Alternatively, the memo confused TGEvent (16-byte payload) with TGCharEvent (17-byte payload — the SetPhaserLevel case at factory 0x105).

### Memo B — `gameplay-mid-repair-batch-validation-20260528.md` (mid-batch)
**Claim:** factory **0x0100** (base TGEvent), **16B** payload  
**Verdict:** Byte count **CORRECT** (16). Factory ID **WRONG** (0x0100 should be 0x0101).

**Likely error mechanism:** Off-by-one typo. The "base TGEvent" designation is correct (the producer DOES use plain TGEvent, not a derived class), but the numeric ID 0x0100 is wrong. The TGObject base has class ID 0x02 and TGEvent has class ID 0x101 — there is no 0x100 in this hierarchy. Most likely the author wrote 0x0100 thinking "base = round number" without re-checking the vtable.

### Cross-reference to leaf #13 (TGObjPtrEvent)
The leaf #13 memo correctly states TGObjPtrEvent is factory 0x010C with class size 0x2C (44 bytes). The ADD_TO_REPAIR_LIST class is **NOT** TGObjPtrEvent — it's plain TGEvent (0x101, 0x28 bytes). The classes are distinguished both by allocation size (0x28 vs 0x2C) and by their ctors (FUN_006D5C00 vs FUN_006BB840).

## Implications

**For OpenBC interop:** Send 16-byte payload (4 i32 fields: 0x00000101, event_type, source_id, dest_id) after the 0x06 opcode byte. Wire-total 17 bytes. Do NOT send 17 bytes of payload — that would add an extraneous trailing byte that stock TGFactoryCreate would interpret as the START of a follow-on event.

**For OpenBC implementation guidance:** Factory ID 0x101 is the **base TGEvent**, used for any event_type that doesn't require additional fields (ADD_TO_REPAIR_LIST, REMOVE_FROM_REPAIR_LIST, REPAIR_PRIORITY toggle, and most other "control" events). Factory IDs 0x105 (TGCharEvent) and 0x10C (TGObjPtrEvent) are used when an extra byte or pointer field is needed.

**Corrections required:**
- Leaf #16 (`gameplay-leaf-repair-event-ids-validation-20260528.md`) — clarify "17 bytes" is total-on-wire (including opcode); payload is 16 bytes.
- Mid-batch (`gameplay-mid-repair-batch-validation-20260528.md`) — change "factory 0x0100" to "factory 0x0101".

## Anchored Addresses

| Symbol | Address | Status |
|--------|---------|--------|
| AddToRepairList_MP (producer) | 0x00565900 | Function exists |
| TGEvent_Ctor | 0x006D5C00 | Function exists |
| TGObject_Ctor (parent) | 0x006F0A70 | Function exists |
| TGEvent vtable | 0x00895FF4 | DATA — 21 slots through +0x50 |
| TGEvent::GetTypeId → 0x101 | 0x006D5CE0 | Bare code (5 bytes) |
| TGEvent::IsA | 0x006D5CF0 | Bare code |
| TGEvent::CopyFrom | 0x006D6230 | Function exists |
| TGEvent::WriteToStream | 0x006D6130 | Function exists |
| TGEvent::ReadFromStream | 0x006D61C0 | Bare code |
| TGFactory_DeserializeObject | 0x006D6200 | Function exists |
| MpgameHandlePythonEvent (receiver) | 0x0069F880 | Function exists, v5 plate set |
| TGObjPtrEvent_Ctor (contrast) | 0x006BB840 | Function exists, vtable 0x00895848 |
| TGObjPtrEvent::WriteToStream (contrast) | 0x006BB890 | Bare code, calls base + WriteChar(byte at +0x28) |
| String "UNKNOWN" | 0x008D858C | Used in TGAlloc tag |
| String "TGObjPtrEvent" | 0x008D8594 | Adjacent to above |
| TGFactory registry | DAT_009983A4 | Hash bucket array, separate from NiRTTI |
| Broadcast sentinel | DAT_0095ADFC | Compared in dest_id path |

## Confidence

**high** — byte-level disassembly of both producer (FUN_00565900) and serializer (0x006D6130), with vtable cross-check confirming GetTypeId returns 0x101, write-side symmetric to read-side (0x006D61C0 + 0x006D6200), and plate comment on receiver (0x0069F880) independently corroborates 16-byte payload.

Save: `mcp__ghidra__save_all_programs` called at end of session — no DB mutations performed (read-only investigation).
