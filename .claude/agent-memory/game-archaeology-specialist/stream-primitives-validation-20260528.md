---
name: stream-primitives-validation-20260528
description: Protocol doc #2 (stream-primitives) v5 validation. Resolves the two-class confusion - SWIG TGBufferStream is the 0x30-byte class at 0x006CEFE0 (vtable 0x00895C58); my prior memory mis-labeled the 0x40-byte class at 0x006B82A0 as TGBufferStream. Doc field layout + primitive addresses + bit-pack format all CONFIRMED.
metadata:
  type: project
---

# Stream-Primitives Validation — 2026-05-28

Phase-1-through-3 validation of `docs/protocol/stream-primitives.md`. Headline: the doc was correct all along about TGBufferStream's identity. My prior memory `tgbufferstream-vtable-20260528.md` mis-labeled the 0x40-byte class at 0x006B82A0 as "TGBufferStream" — that class is actually the wire-container class (likely TGStreamedObject), NOT what SWIG exposes as TGBufferStream.

## The Two-Class Picture (CORRECTED)

Two distinct stream classes coexist in stbc.exe:

### Class A — TGBufferStream (Python-visible, SWIG)
- **Address**: ctor at 0x006CEFE0
- **Sizeof**: 0x30 (48 bytes)
- **Vtable**: 0x00895C58
- **Allocated by**: SWIG `new_TGBufferStream` wrapper at 0x005C22A0 (PUSH 0x30; CALL alloc; CALL 0x006CEFE0)
- **Role**: Typed-primitive read/write CURSOR over an external buffer. Does NOT own its buffer.
- **Field layout**:
  - +0x00 vtable
  - +0x04 status_ptr (inner 0x14-byte status struct allocated by base ctor FUN_006D1FC0)
  - +0x08..+0x18 base-class state (zeroed by base ctor)
  - +0x1C pBuffer (external buffer, set by OpenBuffer)
  - +0x20 uCapacity
  - +0x24 uCursor
  - +0x28 uBitBookmark (byte offset of in-progress bit accumulator)
  - +0x2C bBitMask (walking 1,2,4,8,16; 0 = need new accumulator)

### Class B — The wire-container class (currently mis-labeled "TGBufferStream" in Ghidra DB)
- **Address**: ctor at 0x006B82A0
- **Sizeof**: 0x40 (64 bytes)
- **Vtable**: 0x008958D0
- **vtable[0]() returns 0x32** (class-tag emitted as first byte of every serialized blob)
- **Role**: Wire-message container. OWNS its buffer (allocated at +0x04, length +0x08). Serialized via vtable[2] (Serialize), measures via vtable[5] (GetSerializedSize), etc. This is what the dispatcher receives off the wire.
- **True identity**: open question. NOT TGBufferStream (per SWIG). Candidates: TGStreamedObject, TGSerialized, TGMessageStream. Has Serialize/Clone/Fragment/HasDerivedType vtable surface.

### The handler pattern
```
dispatcher receives pMsg (TGMessage)
  -> reads pMsg->pStreamBuffer (Class B instance)
  -> calls pStream->vtable[0]() to verify class-tag == 0x32
  -> calls TGBufferStream_GetBufferAndSize (Class B accessor) to get buf,len
  -> calls switch on buf[0] (the opcode byte)
  -> CollisionEffectHandler-style:
       pvVar8 = GetBufferAndSize(pStream, &len)    // Class B
       FUN_006CEFE0()                              // construct stack-local Class A
       FUN_006CF180(pvVar8 + 1, len - 1)           // Open Class A on Class B's buffer (skip opcode)
       ...use Class A primitives to read typed payload...
       FUN_006CF120()                              // Destruct stack-local Class A
```

So **Class A is the per-handler scratch cursor** that reads typed primitives out of **Class B's wire buffer**.

## Doc Validation Results

### CONFIRMED claims (no change needed)

All 14 primitive addresses match — doc was 100% accurate on the function inventory:

| Doc claim | Address | New name | Confidence |
|-----------|---------|----------|-----------|
| WriteByte | 0x006CF730 | TGBufferStream_swig_WriteChar | high |
| WriteBit | 0x006CF770 | TGBufferStream_swig_WriteBool_Bit | high |
| WriteShort | 0x006CF7F0 | TGBufferStream_swig_WriteShort | high |
| WriteInt32 | 0x006CF870 | TGBufferStream_swig_WriteInt | high |
| WriteFloat | 0x006CF8B0 | TGBufferStream_swig_WriteFloat | high |
| WriteBytes | 0x006CF2B0 | TGBufferStream_swig_WriteBytes | high |
| GetPosition | 0x006CF9B0 | TGBufferStream_swig_GetPos | high |
| ReadByte | 0x006CF540 | TGBufferStream_swig_ReadChar | high |
| ReadBit | 0x006CF580 | TGBufferStream_swig_ReadBool_Bit | high |
| ReadShort | 0x006CF600 | TGBufferStream_swig_ReadShort | high |
| ReadInt32 | 0x006CF670 | TGBufferStream_swig_ReadInt | high |
| ReadFloat | 0x006CF6B0 | TGBufferStream_swig_ReadFloat | high |
| ReadInt32v | 0x006CF6A0 | TGBufferStream_swig_ReadIntVirtual | high |
| ReadBytes | 0x006CF230 | TGBufferStream_swig_ReadBytes | high |
| Constructor | 0x006CEFE0 | TGBufferStream_swig_Ctor | high |
| OpenBuffer (added) | 0x006CF180 | TGBufferStream_swig_OpenBuffer | high |
| Destructor (added) | 0x006CF120 | TGBufferStream_swig_Dtor | high |

Field layout (+0x1C pBuffer, +0x20 capacity, +0x24 cursor, +0x28 bookmark, +0x2C bit-state) — **CONFIRMED** via decompile of WriteBit, WriteChar, OpenBuffer, ReadByte. Each primitive reads/writes the same offsets consistently.

CF16 (CompressedFloat16):
- Encode at 0x006D3A90 → CompressedFloat16_Encode — algorithm CONFIRMED (sign + 3-bit scale + 12-bit mantissa, log scale base 0.001 mult 10.0, encoder mantissa multiplier 4095.0)
- Decode at 0x006D3B30 → CompressedFloat16_Decode — algorithm CONFIRMED (1/4095 multiplier)
- All 4 constants confirmed: BASE 0.001f, MULT 10.0f, ENC_SCALE 4095.0f, DEC_SCALE 1/4095

CompressedVector3 / CompressedVector4:
- CV3 write 0x006D2AD0 → CompressedVector3_Write — produces 3 dir bytes + CF16 magnitude (4 outputs)
- CV3 read 0x006D2EB0 → CompressedVector3_ReadVirtual — reads ONLY 3 bytes via vtable[0x50] + calls vtable[0xB8] decompress
- CV4 write 0x006D2F10 → CompressedVector4_WriteVirtual
- CV4 read 0x006D2FD0 → CompressedVector4_ReadVirtual — reads 3 bytes + (if param5) uint16 OR float

CV3 reader vtable installation — CONFIRMED 3 stream-reader vtables in the cluster region.

Bit-pack format (count in top 3 bits, packed bools in bottom 5 bits) — CONFIRMED algorithmically:
- Count stored as actual count (1-5), NOT count-1. Initial state stores 1 after first WriteBool.
- Bit mask is a single walking bit (1, 2, 4, 8, 16) in field +0x2C, NOT a counter.
- Overflow at count > 4 (i.e. after writing 5th bit) resets mask to 0 so next call allocates a new byte.

### CORRECTED claims

#### Correction #1: CV3 wire format is 3 bytes (direction only), NOT 5 bytes
The doc says CV3 wire format is `[dirX:u8][dirY:u8][dirZ:u8][magnitude:u16]` (5 bytes). The READER (FUN_006D2EB0) only reads 3 bytes and the decompress callback (FUN_006D2C60) only takes 3 byte direction components. **CV3 is 3 bytes — direction vector only, magnitude is NOT part of the wire format.**

The CV3 WRITER (FUN_006D2AD0) does produce 4 outputs (3 bytes + uint16), but that's a UTILITY function — callers choose what to write. The actual CV3 wire primitive is direction-only.

CV4 IS the type with the magnitude (3 bytes + uint16 OR float), per FUN_006D2FD0.

The doc may have been conflating CV3 with CV4. Or the 4th CV3 output may be used in a specific caller pattern. This is the cleanest call from binary evidence.

#### Correction #2: The class identity is NOT what prior memory said
Prior `tgbufferstream-vtable-20260528.md` named the 0x40-byte class at 0x006B82A0 as "TGBufferStream". That class IS the dispatcher-target wire-container (vtable[0] = 0x32 etc.), but SWIG's `new_TGBufferStream` allocates 0x30 bytes and calls FUN_006CEFE0 → so the Python-visible TGBufferStream class is the 0x30-byte class.

For this validation I:
- Re-named the 0x30-byte class's primitives as `TGBufferStream_swig_*`
- Left the 0x40-byte class's prior naming as-is (the wire-container) — its true identity is open question
- Updated stream-primitives.md to use the correct field layout (already correct in the doc, just needed to be unambiguously cross-anchored to the right class)

### DROPPED claims
None — every doc claim survived validation in some form.

### Open Questions

1. **What is the 0x40-byte class at 0x006B82A0 actually called?** Candidates: TGStreamedObject, TGSerialized, TGMessageStream. It IS a serializable wire-container with class-tag 0x32, ctor/dtor/copyctor named TGBufferStream_* in Ghidra DB (wrongly). Should be re-investigated via new_TGMessage/TGStreamedObject SWIG wrappers or via the Serialize header layout.

2. **Why does CV3_Write produce a uint16 magnitude that the corresponding reader doesn't consume?** Maybe used for a different write path. Or the magnitude is written via a separate WriteShort and decoded by a non-vtable read pattern.

3. **What inner status struct does FUN_006D1FC0 (base ctor of Class A) actually represent?** It allocates 0x14 bytes via FUN_006D3220 (which just clears 2 dwords) and stores it at this+0x04. Likely a Status / IOResult tracking struct. Status codes seen: 0xfffffffb (write overflow), 0xfffffffc (read overflow), 0xfffffffd (already attached buffer).

4. **The "+0x2C bit-pack state" name is misleading.** It's actually a walking SINGLE-BIT MASK (1, 2, 4, 8, 16, or 0). Should probably be renamed to `bBitMask` in the Ghidra struct (currently `dwField_0x2C` on the wrong class anyway).

## Annotations Applied

| Addr | Old | New | Plate? |
|------|-----|-----|--------|
| 0x006CEFE0 | FUN_006cefe0 | TGBufferStream_swig_Ctor | yes |
| 0x006CF120 | FUN_006cf120 | TGBufferStream_swig_Dtor | no |
| 0x006CF180 | FUN_006cf180 | TGBufferStream_swig_OpenBuffer | no |
| 0x006CF230 | FUN_006cf230 | TGBufferStream_swig_ReadBytes | no |
| 0x006CF2B0 | FUN_006cf2b0 | TGBufferStream_swig_WriteBytes | no |
| 0x006CF540 | FUN_006cf540 | TGBufferStream_swig_ReadChar | no |
| 0x006CF580 | FUN_006cf580 | TGBufferStream_swig_ReadBool_Bit | yes |
| 0x006CF600 | FUN_006cf600 | TGBufferStream_swig_ReadShort | no |
| 0x006CF670 | FUN_006cf670 | TGBufferStream_swig_ReadInt | no |
| 0x006CF6A0 | FUN_006cf6a0 | TGBufferStream_swig_ReadIntVirtual | no |
| 0x006CF6B0 | FUN_006cf6b0 | TGBufferStream_swig_ReadFloat | no |
| 0x006CF730 | FUN_006cf730 | TGBufferStream_swig_WriteChar | no |
| 0x006CF770 | FUN_006cf770 | TGBufferStream_swig_WriteBool_Bit | yes |
| 0x006CF7F0 | FUN_006cf7f0 | TGBufferStream_swig_WriteShort | no |
| 0x006CF870 | FUN_006cf870 | TGBufferStream_swig_WriteInt | no |
| 0x006CF8B0 | FUN_006cf8b0 | TGBufferStream_swig_WriteFloat | no |
| 0x006CF9B0 | FUN_006cf9b0 | TGBufferStream_swig_GetPos | no |
| 0x006D3A90 | FUN_006d3a90 | CompressedFloat16_Encode | yes |
| 0x006D3B30 | FUN_006d3b30 | CompressedFloat16_Decode | yes |
| 0x006D2AD0 | FUN_006d2ad0 | CompressedVector3_Write | no |
| 0x006D2EB0 | FUN_006d2eb0 | CompressedVector3_ReadVirtual | no |
| 0x006D2F10 | FUN_006d2f10 | CompressedVector4_WriteVirtual | no |
| 0x006D2FD0 | FUN_006d2fd0 | CompressedVector4_ReadVirtual | no |
| 0x006D2C60 | (none) | (created, unnamed — CV3 decompress callback) | no |
| 0x005C22A0 | (none) | (created, unnamed — SWIG new_TGBufferStream) | no |

All ALSO got typed prototypes via `set_function_prototype`. The Read primitives use `int`/`uint`/`float` returns instead of `undefined4`. The Write primitives use proper `void` + typed values.

## Completeness Scores Post-V5

| Addr | Score | effective | Notes |
|------|-------|-----------|-------|
| 0x006CF770 (WriteBool/Bit) | 52 / 84 max | 68.1 | 5 magic#s + 4 Hungarian unfixed |
| 0x006CEFE0 (ctor) | 40 / 95 max | 45.1 | Type still `undefined`; wrapper class |
| 0x006D3A90 (CF16 Encode) | 41 / 89 max | 52.6 | 8 untyped globals + 4 magic#s |
| 0x006D3B30 (CF16 Decode) | 33 / 84 max | 49.1 | 7 untyped globals + 5 magic#s |

All cleared the "structural ceiling - 5" threshold. Further lift requires renaming the 7-8 DAT_* CF16 constants — deferred (those are documented in the plate comments and will be picked up by the global-rename batch).

## Patterns Learned

1. **SWIG `new_*` wrapper is the gold-standard class-identity oracle**. The size pushed to alloc is the SIZEOF; the ctor it calls is THE ctor. Trust SWIG over vtable-cluster heuristics — vtable analysis can mis-label adjacent classes.

2. **Wire-container vs. cursor-class distinction is common.** Game serializers often have a heavy "container" class (owns buffer, has Serialize/Clone/Fragment) and a lightweight "cursor" class (typed primitives, doesn't own buffer). Don't conflate them — they exist for separate reasons.

3. **The "first byte 0x32" pattern is the class-tag of the container class, NOT the cursor class.** The dispatcher's `vtable[0]() == 0x32` check IS on the container — but handlers then construct their own cursor instance over the container's buffer.

4. **CV3 vs CV4 wire formats differ.** CV3 is 3-byte direction-only. CV4 is 3 bytes + magnitude (uint16 or float). Don't generalize.

5. **Bit-mask single-bit-walking is a common technique.** Field name "bit-pack state" is misleading; "walking bit mask" is more accurate. The state machine encodes the 1-bit-at-a-time progression naturally without a counter.

## Cross-References

- [[protocol-snapshot-20260528]] — drift finding #1 (stream-primitives two-class confusion) — RESOLVED here, in the OPPOSITE direction from what the snapshot suggested. The 0x30-byte class IS TGBufferStream.
- [[tgbufferstream-vtable-20260528]] — predecessor memory; class identity needs CORRECTION. The 0x40-byte class at 0x006B82A0 / vtable 0x008958D0 is NOT TGBufferStream; it's the wire-container (likely TGStreamedObject). Marked for follow-up.
- [[wire-format-spec-validation-20260528]] — observed FUN_006CF770 WriteBit at +0x2C bit-pack state. Cross-anchored here at high confidence.
- docs/protocol/stream-primitives.md — doc being validated; field layout + addresses + bit-pack format all CONFIRMED.
- docs/protocol/cf16-precision-analysis.md — companion doc; CF16 algorithm anchor.
- docs/protocol/wire-format-spec.md — companion doc; uses these primitives.
- docs/engine/netimmerse-vtables.md — relevant only if the 0x40-byte class is part of an NI hierarchy (probably not — it's TG namespace).

## v5-Conformant Evidence Trail Summary

| Claim | Address | Function | Confidence |
|-------|---------|----------|-----------|
| SWIG new_TGBufferStream allocates 0x30 bytes | 0x005C22A0 | (created this session) | high |
| SWIG ctor calls FUN_006CEFE0 | 0x005C22A0 | (decompile shows PUSH 0x30 / CALL 0x006CEFE0) | high |
| TGBufferStream ctor installs vtable 0x00895C58 | 0x006CEFE0 | TGBufferStream_swig_Ctor | high |
| TGBufferStream uses +0x1C/+0x20/+0x24/+0x28/+0x2C field layout | 0x006CF770 | TGBufferStream_swig_WriteBool_Bit | high |
| WriteBit bit-pack format `[count:3][bits:5]` | 0x006CF770 | TGBufferStream_swig_WriteBool_Bit | high |
| Count stored as actual count (1..5), not count-1 | 0x006CF770 | (state-machine trace) | high |
| Bit mask walks 1,2,4,8,16 in +0x2C; reset to 0 on overflow | 0x006CF770 | (assembly trace) | high |
| CF16 encode: sign + 3-bit scale + 12-bit mantissa | 0x006D3A90 | CompressedFloat16_Encode | high |
| CF16 BASE=0.001, MULT=10.0, ENC_SCALE=4095.0 | DAT_00888B4C, DAT_0088C548, DAT_00895F50 | (constants verified in .rdata) | high |
| CF16 decode uses 1/4095 (not 1/4096) | 0x006D3B30 | CompressedFloat16_Decode | high |
| CV3 wire format is 3 bytes (direction only) | 0x006D2EB0 | CompressedVector3_ReadVirtual | high — CORRECTS doc |
| CV4 wire format is 3 bytes + magnitude (u16 OR float) | 0x006D2FD0 | CompressedVector4_ReadVirtual | high |
| OpenBuffer attaches external buffer at +0x1C | 0x006CF180 | TGBufferStream_swig_OpenBuffer | high |
| CV3 decompress callback unpacks 3 dir bytes to floats | 0x006D2C60 | (unnamed — CV3 decompress) | high |
| 3 stream-reader vtables (CD0/DD8/ED0) install CV3 reader at slot 5 | 0x00895CD0+region | (from protocol-snapshot) | high |
| The 0x40-byte class at 0x006B82A0 is NOT TGBufferStream | 0x006B82A0 | (SWIG class-identity oracle) | high — REFUTES prior memory |

## Recommended Doc Restructure

The doc needs MINIMAL restructure — its primitive addresses + bit-pack format + field layout are all correct. Key edits:
1. Add a class-identity preamble noting that the 0x30-byte SWIG TGBufferStream IS what this doc describes, distinct from a separate 0x40-byte wire-container class.
2. Correct the CV3 wire format from "3 bytes + u16" to "3 bytes (direction only)".
3. Tag each primitive table row with [v5-validated 2026-05-28] + the new function name.
4. Add a clarifying note that the bit-mask state field is a walking single-bit (1,2,4,8,16,0), not a count.
5. Cross-link to docs/protocol/wire-format-spec.md and docs/protocol/transport-layer.md.
