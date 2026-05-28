> [docs](../README.md) / [protocol](README.md) / stream-primitives.md

---
title: Stream Primitives & Compressed Data Types
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
  - claim: "TGBufferStream is the 0x30-byte SWIG-visible class; ctor at 0x006CEFE0 installs vtable 0x00895C58"
    address: 0x006CEFE0
    function: TGBufferStream_swig_Ctor
    completeness: 45.1
    confidence: high
    note: "SWIG new_TGBufferStream wrapper at 0x005C22A0 (PUSH 0x30; CALL alloc; CALL 0x006CEFE0) is the class-identity oracle"
  - claim: "Field layout +0x1C pBuffer / +0x20 uCapacity / +0x24 uCursor / +0x28 uBitBookmark / +0x2C bBitMask"
    address: 0x006CF770
    function: TGBufferStream_swig_WriteBool_Bit
    completeness: 68.1
    confidence: high
    note: "Layout confirmed by decompile of WriteBit, WriteChar, OpenBuffer, ReadByte — every primitive reads/writes the same offsets"
  - claim: "+0x2C is a walking single-bit mask (1, 2, 4, 8, 16; 0 = need new accumulator byte), NOT a count"
    address: 0x006CF770
    function: TGBufferStream_swig_WriteBool_Bit
    completeness: 68.1
    confidence: high
    note: "Assembly trace shows mask shifts left each WriteBit; resets to 0 after writing the 5th bit"
  - claim: "OpenBuffer attaches external buffer at +0x1C; resets cursor / bookmark / bit-mask"
    address: 0x006CF180
    function: TGBufferStream_swig_OpenBuffer
    completeness: null
    confidence: high
    note: "Used by the handler pattern to construct a stack-local TGBufferStream over a wire-container's buffer"
  - claim: "WriteByte at FUN_006CF730"
    address: 0x006CF730
    function: TGBufferStream_swig_WriteChar
    completeness: null
    confidence: high
  - claim: "WriteBit at FUN_006CF770 — bit-pack format [count:3][bits:5] per byte"
    address: 0x006CF770
    function: TGBufferStream_swig_WriteBool_Bit
    completeness: 68.1
    confidence: high
  - claim: "WriteShort at FUN_006CF7F0"
    address: 0x006CF7F0
    function: TGBufferStream_swig_WriteShort
    completeness: null
    confidence: high
  - claim: "WriteInt32 at FUN_006CF870"
    address: 0x006CF870
    function: TGBufferStream_swig_WriteInt
    completeness: null
    confidence: high
  - claim: "WriteFloat at FUN_006CF8B0"
    address: 0x006CF8B0
    function: TGBufferStream_swig_WriteFloat
    completeness: null
    confidence: high
  - claim: "WriteBytes (memcpy) at FUN_006CF2B0"
    address: 0x006CF2B0
    function: TGBufferStream_swig_WriteBytes
    completeness: null
    confidence: high
  - claim: "GetPosition at FUN_006CF9B0"
    address: 0x006CF9B0
    function: TGBufferStream_swig_GetPos
    completeness: null
    confidence: high
  - claim: "ReadByte at FUN_006CF540; vtable slot 20 (offset 0x50) is ReadByte for class A"
    address: 0x006CF540
    function: TGBufferStream_swig_ReadChar
    completeness: null
    confidence: high
  - claim: "ReadBit at FUN_006CF580 (matches WriteBit format)"
    address: 0x006CF580
    function: TGBufferStream_swig_ReadBool_Bit
    completeness: null
    confidence: high
  - claim: "ReadShort / ReadInt32 / ReadInt32v / ReadFloat / ReadBytes at FUN_006CF600 / 670 / 6A0 / 6B0 / 230"
    address: 0x006CF600
    function: TGBufferStream_swig_ReadShort
    completeness: null
    confidence: high
    note: "Other read addresses: 0x006CF670 ReadInt, 0x006CF6A0 ReadIntVirtual, 0x006CF6B0 ReadFloat, 0x006CF230 ReadBytes"
  - claim: "CompressedFloat16 encoder at FUN_006D3A90; sign(1) + scale(3) + mantissa(12); 8 decades 0..10000"
    address: 0x006D3A90
    function: CompressedFloat16_Encode
    completeness: 52.6
    confidence: high
  - claim: "CompressedFloat16 decoder at FUN_006D3B30; multiplier is 1/4095 (NOT 1/4096)"
    address: 0x006D3B30
    function: CompressedFloat16_Decode
    completeness: 49.1
    confidence: high
  - claim: "CF16 constants in .rdata: BASE 0.001 / MULT 10.0 / ENC_SCALE 4095.0 / DEC_SCALE 1/4095"
    address: 0x00888B4C
    function: null
    completeness: null
    confidence: high
    note: "DAT_00888B4C BASE, DAT_0088C548 MULT, DAT_00895F50 ENC_SCALE, DAT_00895F54 DEC_SCALE — byte-for-byte confirmed in .rdata"
  - claim: "CompressedVector3 wire format is 3 bytes (direction-only); CV3 and CV4 are NOT symmetric"
    address: 0x006D2EB0
    function: CompressedVector3_ReadVirtual
    completeness: null
    confidence: high
    note: "FUN_006D2EB0 calls vtable[0x50] 3x (ReadByte) then vtable[0xB8] (FUN_006D2C60) — NO magnitude read. Corrects prior doc claim of 5 bytes."
  - claim: "CompressedVector4 wire format is 3 bytes + magnitude (u16 if param5 set, else float32)"
    address: 0x006D2FD0
    function: CompressedVector4_ReadVirtual
    completeness: null
    confidence: high
  - claim: "Three stream-reader vtables (0x00895CD0, 0x00895DD8, 0x00895ED0) install CV3 reader at slot 5"
    address: 0x00895CD0
    function: null
    completeness: null
    confidence: high
    note: "Per protocol-snapshot vtable-cluster walk; all three install FUN_006D2EB0 at the CV3 read slot"
  - claim: "Handler pattern: dispatcher passes 0x40-byte wire-container; handler constructs stack-local TGBufferStream over its buffer via GetBufferAndSize + OpenBuffer (skipping opcode byte)"
    address: 0x006A2470
    function: Handler_CollisionEffect
    completeness: null
    confidence: high
    note: "CollisionEffectHandler 0x006A2470 is the canonical example: GetBufferAndSize → FUN_006CEFE0 ctor → FUN_006CF180 OpenBuffer(buf+1, len-1) → typed reads → FUN_006CF120 dtor"
  - claim: "The 0x40-byte wire-container class at FUN_006B82A0 / vtable 0x008958D0 is TGMessage — the base class of the SWIG-visible TGMessage hierarchy"
    address: 0x006B82A0
    function: TGMessage_Ctor
    completeness: null
    confidence: high
    note: "Identified 2026-05-28 via SWIG `new_TGMessage` wrapper at 0x005E12E0: allocates exactly 0x40 bytes, calls FUN_006B82A0 as ctor, then SWIG_NewPointerObj(\"_p_TGMessage\"). 95 SWIG TGMessage_* method strings at 0x0092A098 cross-confirm. Derived classes (TGConnectMessage 0x006BE730, TGAckMessage 0x006BD120 0x44 bytes for +4 seq, TGBootPlayerMessage 0x006BAC70 0x44 bytes for +4 player ID) all call the same base ctor. Prior memory `tgbufferstream-vtable-20260528.md` and engine `netimmerse-vtables.md` mis-labeled this class as TGBufferStream — SUPERSEDED."
companions:
  - docs/protocol/wire-format-spec.md
  - docs/protocol/transport-layer.md
  - docs/protocol/stateupdate.md
  - docs/protocol/cf16-precision-analysis.md
  - docs/protocol/cf16-explosion-encoding.md
  - docs/engine/netimmerse-vtables.md
  - docs/protocol/v5-validation-status.md
supersedes:
  - (prior pre-v5 stream-primitives content)
---

# Stream Primitives & Compressed Data Types

> [!NOTE]
> This doc is `status: partial`. The TGBufferStream class identity (0x30-byte SWIG-visible
> class at FUN_006CEFE0 / vtable 0x00895C58), all 14 read/write primitive addresses, field
> layout, bit-pack format (5-bits-per-byte with 3-bit count prefix), and CF16 algorithm
> with 4 constants are v5-validated against the current Ghidra import (2026-05-28). One
> material correction: **CV3 wire format is 3 bytes (direction-only), not 5 bytes with u16
> magnitude** — CV3 and CV4 are NOT symmetric. **The separate 0x40-byte class at
> FUN_006B82A0 / vtable 0x008958D0 is TGMessage** (the base class of the TGMessage
> hierarchy — identified 2026-05-28 via SWIG `new_TGMessage` allocator at 0x005E12E0).
> The engine-family `netimmerse-vtables.md` doc previously mis-labeled this vtable as
> TGBufferStream; cross-doc corrections batch at protocol-family-close. See
> [docs/guides/v5-evidence-header.md](../guides/v5-evidence-header.md) for the standard.

All typed serialization on the BC protocol goes through a `TGBufferStream` — a small typed
cursor over an external byte buffer. The cursor reads or writes one primitive at a time
(byte / bit / short / int / float / bytes / two compressed vector types) and tracks a
single packed-bit accumulator for boolean fields. It does **not** own the buffer; it just
walks it.

## Two Stream Classes

Before the primitives table, you need to know that stbc.exe has **two distinct stream
classes** that older docs sometimes conflated. They both have constructors in the same
address range, they both have vtables in `.rdata`, and they're both involved in wire
serialization — but they do different jobs.

**Class A — TGBufferStream (this doc's subject).**
- Constructor: `FUN_006CEFE0` (Ghidra name `TGBufferStream_swig_Ctor`)
- Sizeof: 0x30 bytes
- Vtable: `0x00895C58`
- Role: typed-primitive cursor over an external buffer. SWIG-visible (Python wrappers expose
  it as `TGBufferStream`). Does not own its buffer.
- Identity proof: SWIG `new_TGBufferStream` wrapper at `0x005C22A0` decompiles to
  `PUSH 0x30; CALL alloc; MOV ECX,EAX; CALL 0x006CEFE0`. The 0x30 allocation and the ctor
  target are decisive — this is the class Python code sees.

**Class B — TGMessage (NOT covered by this doc).**
- Constructor: `FUN_006B82A0` (Ghidra name `TGMessage_Ctor` as of 2026-05-28)
- Sizeof: 0x40 bytes
- Vtable: `0x008958D0`
- Role: wire-message container. Owns its buffer. Serialize / Clone / Fragment surface.
  `vtable[0]()` returns `0x32` — TGMessage's class tag, emitted as the first byte of every
  serialized blob, which is also how the dispatcher gates incoming messages.
- Identity proof: SWIG `new_TGMessage` wrapper at `0x005E12E0` decompiles to
  `PUSH 0x40; CALL alloc; CALL 0x006B82A0; CALL SWIG_NewPointerObj("_p_TGMessage")`.
  Cross-confirmed by 95 SWIG `TGMessage_*` method strings at 0x0092A098 and the
  hierarchy of derived classes (TGConnectMessage 0x006BE730, TGAckMessage 0x006BD120
  with size 0x44 for +4 seq, TGBootPlayerMessage 0x006BAC70 with size 0x44 for +4
  player ID, TGDisconnectMessage, TGDoNothingMessage, TGNameChangeMessage) — all
  call this base ctor.
- Older Ghidra annotations and the docs that inherited from them named this class
  "TGBufferStream" — that name was wrong. See
  [§ Cross-doc Reconciliation Required](#cross-doc-reconciliation-required) below.

**The handler pattern uses both.** A dispatcher hands a per-opcode handler a Class B
instance off the wire. The handler asks Class B for its buffer pointer and length
(`GetBufferAndSize`), constructs a *stack-local* Class A over that buffer via the
`OpenBuffer` primitive (skipping the leading opcode byte), and then uses Class A's typed
primitives to extract the payload. The canonical example is `Handler_CollisionEffect` at
`0x006A2470`:

```
pBuf = TGBufferStream_GetBufferAndSize(pStream_classB, &len)   // Class B accessor
FUN_006CEFE0()                       // construct stack-local Class A
FUN_006CF180(pBuf + 1, len - 1)      // OpenBuffer Class A on Class B's buffer, skip opcode
... use Class A primitives to read typed payload ...
FUN_006CF120()                       // destruct stack-local Class A
```

So Class A is the per-handler scratch cursor; Class B is the wire envelope. Everything below
describes **Class A**. For Class B's wire framing (the `0x32` class tag, fragment flags,
sequence counters) see [transport-layer.md](transport-layer.md).

---

## TGBufferStream Field Layout (Class A, 0x30 bytes)

| Offset | Field | Description |
|--------|-------|-------------|
| `+0x00` | vtable | Installed by ctor → `0x00895C58` |
| `+0x04` | status_ptr | Pointer to inner 0x14-byte status struct (allocated by base ctor) |
| `+0x08..+0x18` | base-class state | Zeroed by base ctor |
| `+0x1C` | pBuffer | External buffer pointer (set by `OpenBuffer`) |
| `+0x20` | uCapacity | Buffer size in bytes |
| `+0x24` | uCursor | Current read/write byte offset |
| `+0x28` | uBitBookmark | Byte offset of the in-progress bit-accumulator byte |
| `+0x2C` | bBitMask | Walking single-bit mask (1, 2, 4, 8, 16; 0 = need new accumulator byte) |

The `+0x2C` field is **a walking bit mask, not a count.** It shifts left one position per
`WriteBit` / `ReadBit` call and resets to 0 after the 5th bit so the next call starts a
fresh accumulator byte. The doc's prior wording ("bit-packing state, 0 = no active group")
was technically correct but cryptic — the new wording above matches what the binary
actually does.

---

## Read / Write Primitives

Every row is `[v5-validated 2026-05-28]` against the current Ghidra import. The Ghidra
column names are the renames applied in the validation pass.

### Write Functions (Server → Wire)

| Address | Ghidra name | Type | Size | Description |
|---------|-------------|------|------|-------------|
| `FUN_006CF730` | `TGBufferStream_swig_WriteChar` | WriteByte | 1 byte | Writes `uint8` at current position |
| `FUN_006CF770` | `TGBufferStream_swig_WriteBool_Bit` | WriteBit | 0-1 bytes | Packs boolean bits into a shared byte (see [Bit Packing](#bit-packing-format)) |
| `FUN_006CF7F0` | `TGBufferStream_swig_WriteShort` | WriteShort | 2 bytes | Writes `uint16` (little-endian) |
| `FUN_006CF870` | `TGBufferStream_swig_WriteInt` | WriteInt32 | 4 bytes | Writes `int32` / `uint32` |
| `FUN_006CF8B0` | `TGBufferStream_swig_WriteFloat` | WriteFloat | 4 bytes | Writes `float32` (IEEE 754) |
| `FUN_006CF2B0` | `TGBufferStream_swig_WriteBytes` | WriteBytes | N bytes | Writes raw byte array (memcpy) |
| `FUN_006CF9B0` | `TGBufferStream_swig_GetPos` | GetPosition | — | Returns current stream position (`uint32`) |
| `FUN_006CF180` | `TGBufferStream_swig_OpenBuffer` | OpenBuffer | — | Attaches an external buffer: sets `+0x1C` / `+0x20`, resets cursor / bookmark / bit-mask |

### Read Functions (Wire → Client)

| Address | Ghidra name | Type | Size | Description |
|---------|-------------|------|------|-------------|
| `FUN_006CF540` | `TGBufferStream_swig_ReadChar` | ReadByte | 1 byte | Reads `uint8`; this is vtable slot 20 (offset `0x50`) |
| `FUN_006CF580` | `TGBufferStream_swig_ReadBool_Bit` | ReadBit | 0-1 bytes | Reads packed boolean bit |
| `FUN_006CF600` | `TGBufferStream_swig_ReadShort` | ReadShort | 2 bytes | Reads `uint16` (little-endian) |
| `FUN_006CF670` | `TGBufferStream_swig_ReadInt` | ReadInt32 | 4 bytes | Reads `int32` / `uint32` |
| `FUN_006CF6B0` | `TGBufferStream_swig_ReadFloat` | ReadFloat | 4 bytes | Reads `float32` (IEEE 754) |
| `FUN_006CF6A0` | `TGBufferStream_swig_ReadIntVirtual` | ReadInt32v | 4 bytes | Reads via vtable (variant read) |
| `FUN_006CF230` | `TGBufferStream_swig_ReadBytes` | ReadBytes | N bytes | Reads raw byte array |

The constructor and destructor close the surface:

| Address | Ghidra name | Description |
|---------|-------------|-------------|
| `FUN_006CEFE0` | `TGBufferStream_swig_Ctor` | Installs vtable `0x00895C58`, allocates inner status struct, zeroes base-class state |
| `FUN_006CF120` | `TGBufferStream_swig_Dtor` | Frees inner status struct |

Only vtable slot 20 (`ReadByte`) was directly verified against the vtable this pass.
Slots 1-19 of `0x00895C58` are inferred from the SWIG bindings and remain a follow-up
([§ Open Questions](#open-questions)).

---

## Bit Packing Format

`WriteBit` / `ReadBit` (`FUN_006CF770` / `FUN_006CF580`) pack up to 5 boolean values into
a single byte:

```
Byte layout:  [count:3][bits:5]
              MSB          LSB

count (bits 7-5): Number of bits packed (1-5), stored as the ACTUAL count (not count-1)
bits  (bits 4-0): The actual boolean values, one per bit position
```

State machine:

- The first `WriteBit` call allocates a new byte at the current cursor, stores `count=1`
  in the top 3 bits, sets bit 0 if the value is true, and writes `bBitMask = 1` to `+0x2C`.
- Each subsequent call shifts `bBitMask` left one position (1 → 2 → 4 → 8 → 16),
  ORs the new bit into the accumulator at that mask position, and increments the count
  field in the top 3 bits.
- After the 5th bit, `bBitMask` is reset to 0 — the next `WriteBit` call sees zero, allocates
  a new accumulator byte, and starts over.
- Any non-bit write (e.g., `WriteByte`, `WriteShort`) breaks the bit group: subsequent
  `WriteBit` calls allocate a new accumulator at the new cursor position.

`ReadBit` is symmetric: it reads the count from the top 3 bits, walks the `+0x2C` mask
through the bottom 5 bits, and advances the cursor when the mask reaches the count
boundary.

This is the wrapper that the Settings packet (opcode 0x00) actually uses for its three
"boolean" fields — see [wire-format-spec.md](wire-format-spec.md) Settings section.
Documenting those fields as `[byte:X]` only worked because zero-padding made the resulting
bytes look byte-aligned. The bit-stream form is what the binary actually writes.

---

## Compressed Data Types

### CompressedFloat16 (Logarithmic Scale Compression)

Used for: speed values, damage amounts, distances. Full precision tables in
[cf16-precision-analysis.md](cf16-precision-analysis.md).

**Constants** (byte-for-byte verified in `.rdata`):

| Symbol | Address | Value | Role |
|--------|---------|-------|------|
| BASE | `DAT_00888B4C` | `0.001f` (`3A83126F`) | First decade start |
| MULT | `DAT_0088C548` | `10.0f` (`41200000`) | Decade ratio |
| ENC_SCALE | `DAT_00895F50` | `4095.0f` | Encoder mantissa multiplier |
| DEC_SCALE | `DAT_00895F54` | `float32(1/4095)` ≈ `0.000244200258...` | Decoder inverse |

**Encoding** (`FUN_006D3A90`, Ghidra name `CompressedFloat16_Encode`):

```
Input:  float value
Output: uint16

Format: [sign:1][scale:3][mantissa:12]
        Bit 15 = sign, Bits 14-12 = scale exponent (0-7), Bits 11-0 = mantissa (0-4095)

Algorithm:
1. If value < 0: set sign bit, negate
2. Find scale (0-7) such that value < BASE * MULT^scale
   Scale 0=[0, 0.001), Scale 1=[0.001, 0.01), ..., Scale 7=[1000, 10000)
3. frac = (value - range_lo) / (range_hi - range_lo)
4. mantissa = ftol(frac * 4095.0)   // truncate toward zero (x87 __ftol)
5. If scale overflows (>=8): clamp to scale=7, mantissa=0xFFF
6. Result = ((sign << 3) | scale) << 12 | mantissa
```

**Decoding** (`FUN_006D3B30`, Ghidra name `CompressedFloat16_Decode`):

```
Input:  uint16 encoded
Output: float

Algorithm:
1. mantissa = encoded & 0xFFF
2. sign = (encoded >> 15) & 1
3. scale = (encoded >> 12) & 0x7
4. Compute range: lo=0, hi=BASE; for i in 0..scale: lo=hi, hi=lo*MULT
5. result = (hi - lo) * mantissa * float32(1/4095) + lo
6. If sign: result = -result
```

8 logarithmic decades from 0 to 10000, each with 4096 discrete levels (~0.022% relative
precision per level). The decoder uses `1/4095` (not `1/4096`), so mantissa `0xFFF` decodes
to exactly the top of the range. Encoding is **lossy** — values always round down due to
truncation. See [cf16-precision-analysis.md](cf16-precision-analysis.md) for full precision
tables and [cf16-explosion-encoding.md](cf16-explosion-encoding.md) for explosion opcode
analysis and mod weapon-type ID compatibility.

### CompressedVector3 (Direction-Only)

Used for: direction vectors (3-byte normalized).

**Wire format: 3 bytes total — direction only.** CV3 and CV4 are **not symmetric**: CV4
carries a magnitude, CV3 does not. If a caller needs a CV3 direction *and* its magnitude,
the magnitude must be transmitted separately (e.g., as a CF16 short following the 3 bytes).

**Write** (`FUN_006D2AD0`, Ghidra name `CompressedVector3_Write`):

The writer returns four outputs (3 direction bytes + a CF16 magnitude), but the magnitude
return is a *utility* — callers choose whether and how to put it on the wire. The CV3
**wire** primitive is direction-only.

```
Input:  float dx, dy, dz
Output: byte dirX, byte dirY, byte dirZ  (the wire form)
        + uint16 magnitude (utility return; caller decides whether to write)

Algorithm:
1. magnitude = sqrt(dx*dx + dy*dy + dz*dz)
2. If magnitude <= epsilon: magnitude = 0.0
3. dirX = ftol(dx / magnitude * scale)   // normalized direction as byte
4. dirY = ftol(dy / magnitude * scale)
5. dirZ = ftol(dz / magnitude * scale)
6. (optional, caller-driven) magnitude_compressed = CF16_Encode(magnitude)
```

**Read** (`FUN_006D2EB0`, Ghidra name `CompressedVector3_ReadVirtual`):

The reader is the source of truth for the wire format: it reads exactly 3 bytes via
`vtable[0x50]` (ReadByte) and calls `vtable[0xB8]` (`FUN_006D2C60`) to decompress the
3 direction bytes into 3 floats. **No magnitude is read; no `uint16` appears in the
read path.**

```
1. Read 3 bytes via vtable+0x50 (ReadByte)
2. Call vtable+0xB8 (FUN_006D2C60) to decompress: (outX, outY, outZ, byte1, byte2, byte3)
```

Three stream-reader vtables in the cluster install this CV3 reader at slot 5: `0x00895CD0`,
`0x00895DD8`, `0x00895ED0` — every stream-reader subclass that needs CV3 inherits the same
3-byte primitive.

> [!NOTE]
> Why does CV3_Write produce a magnitude that CV3_Read doesn't consume? Either there are
> caller-driven write patterns that emit the magnitude as a separate `WriteShort` (and a
> non-vtable reader picks it up later) or the magnitude output is an analytics hint the
> writer keeps but the wire format doesn't carry. This is open — see
> [§ Open Questions](#open-questions). The wire fact (CV3 = 3 bytes) is unambiguous.

### CompressedVector4 (Direction + Magnitude)

Used for: position + rotation, position + scale, collision contact points (see
[collision-effect-protocol.md](collision-effect-protocol.md)).

**Wire format depends on the `param4` flag.** CV4 carries the magnitude (this is the type
that does).

**Write** (`FUN_006D2F10`, Ghidra name `CompressedVector4_WriteVirtual`):

```
If param4 == 0 (use float for 4th component):
  Compress 3 floats via vtable+0xA0, write 3 bytes via vtable+0x54
  Write float via vtable+0x74
If param4 != 0 (use uint16 for 4th component):
  Compress 3 floats via vtable+0xA4, write 3 bytes via vtable+0x54
  Write uint16 via vtable+0x5C
```

**Read** (`FUN_006D2FD0`, Ghidra name `CompressedVector4_ReadVirtual`):

```
1. Read 3 bytes via vtable+0x50
2. If param4 != 0: read uint16 via vtable+0x58
   Call vtable+0xB4 to decompress with uint16 magnitude
3. If param4 == 0: read float via vtable+0x70
   Call vtable+0xB0 to decompress with float magnitude
```

Wire format `(param4 != 0)`: `[dirX:u8][dirY:u8][dirZ:u8][magnitude:u16]` = **5 bytes**
Wire format `(param4 == 0)`: `[dirX:u8][dirY:u8][dirZ:u8][magnitude:f32]` = **7 bytes**

---

## Cross-doc Reconciliation Required

The class-identity inversion surfaced in this validation pass cascades into other docs
that previously inherited the wrong naming. The wire-container class identity has been
**resolved as TGMessage** (2026-05-28 — see Class B above). The following docs need
patches at protocol-family-close.

| Doc | Current claim | Correction |
|-----|---------------|------------|
| [docs/engine/netimmerse-vtables.md](../engine/netimmerse-vtables.md) | "TGBufferStream vtable at 0x008958D0" | Rename to **TGMessage** vtable at 0x008958D0. The vtable address is correct; the class name is what's wrong. The doc was v5-verified against the engine campaign — apply as a cascade correction. |
| [docs/protocol/wire-format-spec.md](wire-format-spec.md) | "TGBufferStream wire begins with 0x32" | Re-attribute to **TGMessage** wire envelope. The `0x32` is TGMessage's base-class tag. |
| [docs/protocol/transport-layer.md](transport-layer.md) | TGBufferStream layout in Appendix A | Realign to **TGMessage** layout when transport-layer.md is validated. |
| `.claude/agent-memory/game-archaeology-specialist/tgbufferstream-vtable-20260528.md` | Names the 0x40-byte class as TGBufferStream | Superseded — content actually documents TGMessage's vtable surface. Add corrigenda header pointing at this validation. |
| Ghidra plate comment at MpgameHandleMessage (0x0069F2A0) | "TGBufferStream::GetStreamTypeId" | Update to **TGMessage::GetTypeId** — 0x32 is TGMessage's base-class tag. |
| Ghidra plate comments at 0x006B82A0..0x006B9C50 range | "TGBufferStream_*" function names | Rename to **TGMessage_***. The TGBufferStream_swig_* functions at 0x006CEFE0+ are correctly named — they belong to the separate SWIG TGBufferStream. |

The protocol-family tracker logs these impacts at
[v5-validation-status.md §6.2](v5-validation-status.md#62-stream-primitivesmd--2026-05-28-game-archaeology-specialist).

---

## Open Questions

1. ~~**What is the 0x40-byte wire-container class at FUN_006B82A0 / vtable 0x008958D0
   actually called?**~~ **RESOLVED 2026-05-28: TGMessage.** SWIG `new_TGMessage` wrapper
   at 0x005E12E0 allocates 0x40 bytes and calls FUN_006B82A0 (now `TGMessage_Ctor` in
   Ghidra). 95 SWIG `TGMessage_*` method strings at 0x0092A098 cross-confirm. Derived
   classes (TGConnectMessage, TGAckMessage, TGBootPlayerMessage, etc.) all call this
   base ctor. See [Cross-doc Reconciliation Required](#cross-doc-reconciliation-required)
   for cascade impacts.
2. **Why does `CV3_Write` produce a `uint16` magnitude that `CV3_Read` doesn't consume?**
   Possible caller-driven asymmetric pattern (writer emits magnitude as a separate
   `WriteShort`; reader picks it up via a different code path).
3. **What are slots 1-19 of TGBufferStream vtable `0x00895C58`?** Only slot 20 (ReadByte)
   was directly verified against the vtable this pass. Other slots are inferred from
   SWIG bindings.
4. **What is the inner status struct allocated by `FUN_006D1FC0` (the base ctor of class A)?**
   It's 0x14 bytes. Status codes observed: `0xFFFFFFFB` (write overflow), `0xFFFFFFFC`
   (read overflow), `0xFFFFFFFD` (already-attached buffer). Probably a `Status` / `IOResult`
   tracker; deferred to a future engine-side pass.

---

## See also

- [wire-format-spec.md](wire-format-spec.md) — opcode hub; Settings packet (opcode 0x00) uses
  three `WriteBit` calls documented here.
- [transport-layer.md](transport-layer.md) — the TGMessage layer (the 0x40-byte
  class), UDP framing, fragment reassembly.
- [stateupdate.md](stateupdate.md) — uses `CompressedVector4` for position fields.
- [collision-effect-protocol.md](collision-effect-protocol.md) — canonical example of the
  handler pattern: dispatcher gives a wire-container, handler constructs a stack-local
  TGBufferStream over its buffer to extract typed payload.
- [cf16-precision-analysis.md](cf16-precision-analysis.md) — full CF16 precision tables.
- [cf16-explosion-encoding.md](cf16-explosion-encoding.md) — CF16 in opcode 0x29 + mod
  weapon-type ID compatibility.
- [v5-validation-status.md](v5-validation-status.md) — protocol-family validation tracker
  (§6.2 logs this doc's validation).
- [../guides/v5-evidence-header.md](../guides/v5-evidence-header.md) — the v5 evidence header
  schema this doc conforms to.
