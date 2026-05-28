---
name: wire-container-class-identification-20260528
description: Wire-container class at FUN_006B82A0 / vtable 0x008958D0 identified as TGMessage (base of message hierarchy)
metadata:
  type: project
---

# Wire-Container Class Identified: TGMessage

**Date**: 2026-05-28
**Status**: HIGH confidence

## The Answer

The 0x40-byte class at `FUN_006B82A0` / vtable `0x008958D0` is **TGMessage** —
the BASE CLASS of the SWIG-visible TGMessage hierarchy.

It is NOT TGBufferStream. The actual SWIG-visible TGBufferStream is the
SEPARATE 0x30-byte class at FUN_006CEFE0 / vtable 0x00895C58.

## Decisive Evidence

The SWIG `new_TGMessage` Python wrapper at **0x005E12E0** does:

```asm
005E12E4  PUSH 0x937c0c          ; format string ":new_TGMessage"
005E12EA  CALL PyArg_ParseTuple
005E12FE  PUSH 0x40              ; sizeof(TGMessage) = 64 bytes
005E1300  MOV ECX, 0x99c478      ; pool allocator
005E1305  CALL 0x00717b70        ; NiAlloc(0x40)
005E130A  MOV ECX, EAX
005E130C  CALL 0x00718010        ; header init helper
005E1317  CALL 0x006B82A0        ; <<< THE CTOR
005E1324  CALL 0x005BB0E0        ; SWIG_MakePtr → "_p_TGMessage"
```

This proves: when Python calls `App.new_TGMessage()`, SWIG allocates exactly
0x40 bytes and runs FUN_006B82A0 as the constructor.

## Cross-Confirmation: Derived Class Constructors

The SWIG bindings reveal the full TGMessage class hierarchy:

| SWIG Name              | Alloc Size | Ctor Address |
|------------------------|-----------:|-------------:|
| TGMessage (base)       |       0x40 |   0x006B82A0 |
| TGConnectMessage       |       0x40 |   0x006BE730 |
| TGDisconnectMessage    |       0x40 |  0x006BAC10? |
| TGAckMessage           |       0x44 |   0x006BD120 |
| TGBootPlayerMessage    |       0x44 |   0x006BAC70 |
| TGDoNothingMessage     |       0x40 |  0x006BCAF0? |
| TGNameChangeMessage    |       0x40 |  0x006BD7C0? |

Each derived ctor calls `TGMessage_Ctor(this)` to base-init, then overwrites
the vtable with its own subclass vtable. Example: subclass vtable at
0x00895A0C with slot[0] = 0x006BFE70 returns **0x05** (not 0x32) — its own
class-discriminator constant.

## SWIG TGMessage API (95 methods at 0x0092a098+)

Confirms message-routing semantics:
- `TGMessage_GetBufferStream` — returns embedded TGBufferStream view of payload
- `TGMessage_BreakUpMessage` — corresponds to vtable[7] Fragment
- `TGMessage_Serialize`/`UnSerialize` — vtable[2]/[2-equivalent]
- `TGMessage_SetData`/`SetDataNoCopy` — writes [this+0x04]=ptr, [this+0x08]=len
- `TGMessage_GetSequenceNumber`/`Set` — accesses [this+0x14] (short)
- `TGMessage_IsMultiPart`/`Set` — accesses [this+0x3A] (byte flag)
- `TGMessage_IsHighPriority`/`Set` — accesses [this+0x3B]
- `TGMessage_IsAggregate`/`Set` — accesses [this+0x3C]
- `TGMessage_IsGuaranteed`/`Set` — accesses [this+0x3D]
- `TGMessage_SetToID`/`SetFromID`/`GetFromAddress` — routing
- `TGMessage_SetBackoffFactor`/`Type`/`Time` — reliability/retry timing
- `TGMessage_GetNumRetries`/`IncrementNumRetries` — retry counter

These access patterns precisely match the field offsets we observed in the
ctor body and in Serialize/GetSerializedSize/Fragment.

## TGMessage Class Layout (0x40 bytes)

```
+0x00  vtable* (= 0x008958D0)
+0x04  BYTE*    pPayloadData
+0x08  uint     uPayloadLength
+0x0C  uint     uTimeStamp
+0x10  uint     uFirstSendTime
+0x14  ushort   uSequenceNumber       (written by Serialize if IsMultiPart)
+0x18  float    uFirstResendTime
+0x1C  uint     uBackoffTime
+0x20  uint     uNumRetries
+0x24  uint     uToID
+0x28  ???                            (read by MpgameHandleMessage as pStream)
+0x2C  uint     uFromID|nBackoffType
+0x30  float    fBackoffFactor        (default 1.0f from ctor)
+0x34  float    fSomeFactor           (default 1.0f from ctor)
+0x38  byte     uMultiPartCount
+0x39  byte     uMultiPartSeqIdx
+0x3A  byte     bIsMultiPart
+0x3B  byte     bIsHighPriority
+0x3C  byte     bIsAggregate
+0x3D  byte     bIsGuaranteed         (default 1 from ctor)
+0x3E..+0x3F   pad
```

## TGMessage Vtable Layout (0x008958D0, 10 slots)

| Slot | Addr        | Method            | Returns / Behavior                                    |
|------|-------------|-------------------|-------------------------------------------------------|
|  0   | 0x006B9430  | GetTypeId         | Returns 0x32 (base class discriminator)               |
|  1   | 0x006B82F0  | ScalarDeletingDtor| Calls dtor + operator delete(this, 0x40)              |
|  2   | 0x006B8340  | Serialize         | Wire emit: [byte:0x32][short:hdr][optional fields][payload] |
|  3   | 0x006B9440  | HasDerivedType    | Returns false (base default)                          |
|  4   | 0x006B9450  | IsSpecialStream   | Returns false (base default)                          |
|  5   | 0x006B8640  | GetSerializedSize | Returns 3 + payload + optional headers                |
|  6   | 0x006B8610  | Clone             | alloc 0x40 + run CopyCtor                              |
|  7   | 0x006B8720  | Fragment          | Splits payload into multi-part TGMessage chain        |
|  8   | 0x006B9C50  | (TBD)             |                                                       |
|  9   | 0x006B34D0  | (TBD)             |                                                       |

## Open Follow-Ups

1. **Dispatcher field at +0x28**: MpgameHandleMessage at 0x0069F2C5 reads
   `[pMsg + 0x28]` as a TGBufferStream-like object pointer. This is likely the
   incoming TGMessage envelope's "embedded received stream" pointer, but its
   exact semantics need verification (could be related to fragmented-message
   reassembly).

2. **Slots 8/9 of vtable 0x008958D0**: Functions at 0x006B9C50 and 0x006B34D0
   are not yet identified. Likely UnSerialize and Merge (per SWIG bindings).

3. **TGStream parent class**: SWIG string `_p_TGStream` exists at 0x00912794
   suggesting there is a more abstract base. TGMessage may inherit from TGStream
   (which would unify it with TGBufferStream under a common abstract parent).
   The ctor at FUN_006B82A0 does not call any base-class init, but the cleaning
   up of the vtable slot 1 (dtor) directly destroys, so it appears TGMessage
   has no C++ base class with virtuals.

## Cross-Doc Corrections Required

1. **docs/engine/netimmerse-vtables.md**: Remove "TGBufferStream vtable at
   0x008958D0" claim. Replace with: "TGMessage vtable at 0x008958D0; the
   SWIG-visible TGBufferStream class lives at vtable 0x00895C58 (FUN_006CEFE0
   ctor, 0x30 bytes)."

2. **docs/protocol/wire-format-spec.md**: Section on the "TGBufferStream wire
   header" needs to be renamed to "TGMessage wire envelope". The 0x32 first
   byte is the TGMessage class-tag (not a TGBufferStream tag).

3. **docs/protocol/transport-layer.md**: The "TGMessage" section needs to be
   updated. TGMessage is the OUTER wire-container — when documentation talks
   about "TGBufferStream serialization" of the wire envelope, that's actually
   TGMessage. The 0x40-byte struct discussion is TGMessage; the 0x30-byte
   buffer-cursor class is the SWIG-visible TGBufferStream (separate role).

4. **.claude/agent-memory/game-archaeology-specialist/tgbufferstream-vtable-20260528.md**:
   This memory note is wrong about vtable 0x008958D0 being TGBufferStream.
   It should be updated to reflect: vtable 0x008958D0 = TGMessage,
   vtable 0x00895C58 = TGBufferStream (SWIG-visible buffer-cursor class).

5. **MpgameHandleMessage plate comment at 0x0069F2A0**: Currently says
   "TGBufferStream::GetStreamTypeId" but should say "TGMessage::GetTypeId".
   The 0x32 byte is the TGMessage class tag, not a buffer-stream tag.

6. **TGBufferStream_Serialize plate comment at 0x006B8340**: Same — should
   say "TGMessage::Serialize".

7. **All TGBufferStream_* functions in the 0x006B82A0..0x006B9C50 range**:
   Should be renamed to TGMessage_* (slot 0, 1, 2, 3, 4, 5, 6, 7) — the SWIG-
   wrapper names (TGBufferStream_swig_*) at 0x006CEFE0 onwards are correct.

## Pinned in Ghidra

- FUN_006B82A0 renamed to **TGMessage_Ctor**
- Prototype set to `void __thiscall TGMessage_Ctor(void *this)`
- Plate comment installed with class identity, vtable layout, hierarchy, and
  v5-grade evidence

## Confidence Assessment

**HIGH**. The SWIG-binding evidence (new_TGMessage allocates 0x40 + calls
exactly FUN_006B82A0) is irrefutable — it's the explicit Python-to-C++ binding
generated by SWIG's code-gen, with the class name "TGMessage" baked into the
PyMethodDef table. Cross-confirmed by:
- 95 TGMessage_* SWIG method strings matching observed field offsets
- Class hierarchy coherence with TGAck/TGBoot derived classes
- Vtable layout consistent with MSVC C++ ABI (10 slots, scalar deleting dtor
  at slot 1, size baked into operator delete call as 0x40)
- Wire format consistent with TGMessage semantics (sequence, multi-part,
  high-priority flags map to SWIG API)

The PRIOR labeling of FUN_006B82A0 as "TGBufferStream_Ctor" was a class-
identity inversion — the two classes were swapped in someone's earlier
analysis.
