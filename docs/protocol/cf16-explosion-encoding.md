> [docs](../README.md) / [protocol](README.md) / cf16-explosion-encoding.md

---
title: CompressedFloat16 (CF16) Encoding — Explosion Damage Wire Format
type: reference + explanation
audience: re-engineer
validated: 2026-05-28
methodology: FUNCTION_DOC_WORKFLOW_V5
binary:
  name: stbc.exe
  size: 6182400
  base: 0x00400000
status: verified
evidence:
  - claim: "CF16 encoder algorithm: [sign:1][scale:3][mantissa:12] with __ftol truncation"
    address: 0x006d3a90
    function: CompressedFloat16_Encode
    completeness: 52.6
    confidence: high
    note: "Plate exists; algorithm pseudocode matches decompile."
  - claim: "CF16 decoder algorithm: iterative range rebuild + float32(1/4095) multiply"
    address: 0x006d3b30
    function: CompressedFloat16_Decode
    completeness: 49.1
    confidence: high
    note: "Plate exists; matches x87 FPU behavior in decompile."
  - claim: "BASE = 0.001f"
    address: 0x00888b4c
    function: null
    confidence: high
    note: "bytes 6F 12 83 3A"
  - claim: "ZERO = 0.0f"
    address: 0x00888b54
    function: null
    confidence: high
    note: "bytes 00 00 00 00"
  - claim: "MULT = 10.0f"
    address: 0x0088c548
    function: null
    confidence: high
    note: "bytes 00 00 20 41"
  - claim: "ENC_SCALE = 4095.0f"
    address: 0x00895f50
    function: null
    confidence: high
    note: "bytes 00 F0 7F 45"
  - claim: "DEC_SCALE = float32(1/4095) approximately 0.000244200258"
    address: 0x00895f54
    function: null
    confidence: high
    note: "bytes 01 08 80 39"
  - claim: "Explosion sender writes opcode 0x29 + objID + CV4 position + CF16 radius + CF16 damage"
    address: 0x00595c60
    function: DamageableObject__SendExplosions_0x29
    confidence: high
    note: "Iterates explosion list at this+0x13C; radius at +0x14, damage at +0x1C."
  - claim: "Explosion receiver decodes inverse of sender, allocates 0x38-byte ExplosionDamage"
    address: 0x006A0080
    function: Handler_Explosion_0x29
    confidence: high
    note: "FUN_00718cb0(0x38) allocator confirms struct size."
  - claim: "ExplosionDamage ctor builds 0x38-byte struct: vtable +0, position +0x08, radius +0x14, radius^2 +0x18, damage +0x1C, bbox min +0x20, bbox max +0x2C"
    address: 0x004bbde0
    function: ExplosionDamage_Ctor
    confidence: high
    note: "Vtable 0x0088c6c4 hardcoded in ctor."
  - claim: "CV4 writer dispatches 5-byte vs 7-byte form based on mag_as_cf16 / param_5; explosion path uses mag_as_cf16=1 (5 bytes)"
    address: 0x006d2f10
    function: CompressedVector4_WriteVirtual
    confidence: high
    note: "param_5 != 0 -> 3 byte writes + 1 short = 5 bytes; param_5 == 0 -> 3 byte writes + 1 float = 7 bytes. Explosion sender calls with literal 1. The opcode 0x29 14-byte total (1+4+5+2+2) is consistent only with CV4=5."
  - claim: "CV4 reader symmetric: 5-byte form for mag_as_cf16=1, 7-byte for mag_as_cf16=0"
    address: 0x006d2fd0
    function: CompressedVector4_ReadVirtual
    confidence: high
    note: "Explosion receiver calls with 1 -> 5-byte path."
  - claim: "RequestObjHandler (0x1E) is a sender caller of explosion replay"
    address: 0x006a02a0
    function: MultiplayerGame__RequestObjHandler
    confidence: high
    note: "Xref to FUN_00595c60."
  - claim: "NewPlayerInGameHandler (0x2A) is a sender caller of explosion replay"
    address: 0x006a1e70
    function: Handler_NewPlayerInGame_0x2A
    confidence: high
    note: "Xref to FUN_00595c60. Replay path for late-join clients."
companions:
  - docs/protocol/cf16-precision-analysis.md
  - docs/protocol/stream-primitives.md
  - docs/protocol/game-opcodes.md
  - docs/protocol/wire-format-spec.md
  - docs/protocol/pythonevent-wire-format.md
  - docs/protocol/v5-validation-status.md
supersedes:
  - 2026-02-15
---

# CompressedFloat16 (CF16) Encoding — Explosion Damage Wire Format

> [!NOTE]
> This doc is `status: verified`. **1 byte-size correction + 1 clarification**. CV4 position field is **5 bytes** (3 direction bytes + CF16 magnitude) for the explosion path, **NOT 7 bytes** — the 14-byte total in the same diagram is only consistent with CV4=5. The 7-byte form is for other CV4 callers using `mag_as_cf16=0`. Algorithm, constants, encoded hex values (15.0→0x50E3, 25.0→0x52AA, 273.0→0x6313, 2063.0→0x71E3), and `round()` match results all byte-confirmed. Sender (FUN_00595c60), receiver (Handler_Explosion_0x29 at 0x006A0080), and the two replay-path callers (RequestObjHandler 0x006a02a0, NewPlayerInGameHandler 0x006a1e70) all xref-confirmed. ExplosionDamage 0x38-byte struct cross-linked to [cf16-precision-analysis.md](cf16-precision-analysis.md). See [v5-evidence-header.md](../guides/v5-evidence-header.md) for the standard. Source evidence: `.claude/agent-memory/game-archaeology-specialist/cf16-batch-validation-20260528.md`.

## Overview

Bridge Commander's explosion event (opcode `0x29`) encodes damage and radius as
**CompressedFloat16** (CF16), a custom 16-bit floating point format used throughout
the engine's network serialization. This document details the exact encoding algorithm,
extracted constants, and precision analysis for mod weapon-type identification.

For algorithm-level deep-dives, scale tables, and the cross-protocol caller list, see the
companion [cf16-precision-analysis.md](cf16-precision-analysis.md). This doc focuses on
the **explosion-specific wire format** and the **mod weapon-type ID round-trip**.

## CF16 Constants (from stbc.exe)

[v5-validated 2026-05-28]

| Symbol | Address | Hex Bytes | Value | Purpose |
|--------|---------|-----------|-------|---------|
| BASE | `DAT_00888b4c` | `6F 12 83 3A` | 0.001 (float32) | First scale boundary |
| ZERO | `DAT_00888b54` | `00 00 00 00` | 0.0 | Negative check / range_lo for scale 0 |
| MULT | `DAT_0088c548` | `00 00 20 41` | 10.0 | Scale multiplier |
| ENC_MULT | `DAT_00895f50` | `00 F0 7F 45` | 4095.0 | Encoder mantissa multiplier |
| DEC_MULT | `DAT_00895f54` | `01 08 80 39` | 1/4095 (float32) | Decoder mantissa divisor |

## Wire Format

[v5-validated 2026-05-28]

```
[sign:1][scale:3][mantissa:12]  = 16 bits total
```

- **sign** (bit 15): 0 = positive, 1 = negative
- **scale** (bits 14-12): 3-bit index selecting the value range (0-7)
- **mantissa** (bits 11-0): 12-bit value within the selected range (0-4095)

## Scale Table

[v5-validated 2026-05-28]

| Scale | Range Low | Range High | Step Size | Notes |
|-------|-----------|------------|-----------|-------|
| 0 | 0.0 | 0.001 | 2.44e-7 | Sub-thousandths |
| 1 | 0.001 | 0.01 | 2.20e-6 | Thousandths |
| 2 | 0.01 | 0.1 | 2.20e-5 | Hundredths |
| 3 | 0.1 | 1.0 | 2.20e-4 | Fractions |
| 4 | 1.0 | 10.0 | 2.20e-3 | Single digits |
| 5 | 10.0 | 100.0 | 2.20e-2 | Tens |
| 6 | 100.0 | 1000.0 | 2.20e-1 | Hundreds |
| 7 | 1000.0 | 10000.0 | 2.20 | Thousands |

Each scale covers one decimal order of magnitude. The 4096 mantissa values (0-4095)
divide the range into equal steps. Mantissa 0 = range_lo, mantissa 4095 = range_hi.

## Encoder Algorithm (FUN_006d3a90)

[v5-validated 2026-05-28]

```c
// __fastcall: float param_3 on stack (x87 convention)
// Returns uint16 in EAX (low 16 bits)
uint16_t CF16_Encode(float value) {
    bool negative = (value < 0.0f);
    if (negative) value = -value;

    uint32_t scale = 0;
    float boundary = BASE;       // 0.001
    float prev_boundary = ZERO;  // 0.0

    while (scale < 8) {
        if (value < boundary) {
            // Found the bin: value is in [prev_boundary, boundary)
            int mantissa = (int)((value - prev_boundary)
                                / (boundary - prev_boundary)
                                * 4095.0f);
            break;
        }
        prev_boundary = boundary;
        boundary *= MULT;  // boundary *= 10.0
        scale++;
    }

    if (scale == 8) {
        // Overflow: clamp to maximum representable
        mantissa = 0xFFF;
        scale = 7;
    }

    if (negative) scale |= 0x8;

    return (uint16_t)((scale << 12) | mantissa);
}
```

**Key detail**: The encoder uses `int()` truncation (x87 `__ftol`), NOT rounding.
This means the encoded value is always <= the original value within the bin.

## Decoder Algorithm (FUN_006d3b30)

[v5-validated 2026-05-28]

```c
// __cdecl: uint16 param_1 on stack
// Returns float (x87 ST0)
float CF16_Decode(uint16_t encoded) {
    uint32_t mantissa = encoded & 0xFFF;
    uint8_t scale_nibble = (encoded >> 12) & 0xF;

    bool negative = (scale_nibble & 0x8) != 0;
    if (negative) scale_nibble &= 0x7;

    float range_lo = 0.0f;    // ZERO
    float range_hi = 0.001f;  // BASE

    for (int i = 0; i < scale_nibble; i++) {
        range_lo = range_hi;
        range_hi = range_lo * 10.0f;  // * MULT
    }

    float result = (range_hi - range_lo) * (float)mantissa * (1.0f/4095.0f) + range_lo;

    if (negative) result = -result;
    return result;
}
```

**Key detail**: The decoder uses `1.0f/4095.0f` (stored as a float32 constant at
`DAT_00895f54`), NOT `1.0f/4096.0f`. This is a proper inverse of the encoder's
4095.0 multiplier.

## Explosion Packet (Opcode 0x29) Wire Format

[v5-validated 2026-05-28]

```
[0x29]                        opcode (1 byte)
[objectID]                    source object ID (uint32, 4 bytes)
[position]                    CompressedVector4 (5 bytes: 3 direction bytes + CF16 magnitude)
[radius: CF16]                explosion radius (uint16, 2 bytes)
[damage: CF16]                explosion damage (uint16, 2 bytes)
                              ============
                              14 bytes total
```

### C1 — CV4 position field is 5 bytes, not 7

The pre-v5 doc rendered the position field as `CompressedVector4 (variable, ~7 bytes)`,
which is internally inconsistent with its own 14-byte total (`1+4+7+2+2 = 16`, not 14).
Binary truth: **5 bytes for the explosion path**.

`CompressedVector4_WriteVirtual` at `0x006d2f10` dispatches on its `mag_as_cf16` / `param_5`
argument:

- `param_5 != 0` → 3 byte writes (vtable+0x54) + 1 short write (vtable+0x5C) = **5 bytes** (used by explosion)
- `param_5 == 0` → 3 byte writes + 1 float write (vtable+0x74) = **7 bytes** (used by other callers)

`DamageableObject__SendExplosions_0x29` (FUN_00595c60) calls CV4 write with `1` → 5-byte path.
The receiver `FUN_006a0080` calls `CompressedVector4_ReadVirtual` with `1` → matching 5-byte
path. The 5-byte form is selected by `mag_as_cf16=1` on the CV4 write. Other CV4 callers
using `mag_as_cf16=0` produce a 7-byte form with a raw float32 magnitude — see
[stream-primitives.md](stream-primitives.md) for the full dispatch.

The 14-byte total `1 + 4 + 5 + 2 + 2 = 14` is consistent only with CV4=5 bytes.

### Sender / Receiver / Callers

**Sender**: `FUN_00595c60` at `0x00595c60` (`__thiscall`)
- Iterates the explosion list at `this+0x13C`
- Reads radius from explosion struct offset `+0x14`
- Reads damage from explosion struct offset `+0x1C`
- Called from: `MultiplayerGame__RequestObjHandler` at `0x006a02a0` (replay on object request)
  and `Handler_NewPlayerInGame_0x2A` at `0x006a1e70` (replay on late-join)

**Receiver**: `Handler_Explosion_0x29` at `0x006A0080`
- Dispatched from `MpgameHandleMessage` jump table (opcode 0x29 row)
- Decodes position, then two CF16 values (radius, damage)
- Allocates a 0x38-byte `ExplosionDamage` struct via `FUN_00718cb0(0x38)`, built by
  `FUN_004bbde0` (vtable hardcoded to `0x0088c6c4`)
- Calls `ProcessDamage` to apply to target ship

### Clar1 — ExplosionDamage struct cross-link

The receiver allocates a 0x38-byte struct with this layout (sourced from the ctor at
`FUN_004bbde0`):

| Offset | Size | Field | Source |
|--------|------|-------|--------|
| +0x00 | 4 | vtable = 0x0088c6c4 | hardcoded in ctor |
| +0x04 | 4 | base class (unused or padding) | parent ctor FUN_007d87a0 |
| +0x08 | 4 | position.x (float) | param_2[0] |
| +0x0C | 4 | position.y (float) | param_2[1] |
| +0x10 | 4 | position.z (float) | param_2[2] |
| +0x14 | 4 | radius (float) | param_3 |
| +0x18 | 4 | radius^2 (float, precomputed) | `param_3 * param_3` |
| +0x1C | 4 | damage (float) | param_4 |
| +0x20..+0x28 | 12 | bbox min (3 floats) | filled by FUN_004bbec0 |
| +0x2C..+0x34 | 12 | bbox max (3 floats) | filled by FUN_004bbec0 |
| Total | **0x38** | | matches `FUN_00718cb0(0x38)` |

> Cross-link: see also [cf16-precision-analysis.md § Explosion Packet](cf16-precision-analysis.md#explosion-packet-opcode-0x29-wire-format) for the same struct table rendered alongside the sender/receiver call graph.

## Precision Analysis: BC Remastered Weapon Type IDs

BC Remastered uses specific damage float values as weapon type identifiers:
**15.0**, **25.0**, **273.0**, **2063.0**

### Round-Trip Results

| Original | Encoded | Scale | Mantissa | Decoded | Error | Rel Error |
|----------|---------|-------|----------|---------|-------|-----------|
| 15.0 | 0x50E3 | 5 | 227 | 14.989012 | 0.011 | 0.073% |
| 25.0 | 0x52AA | 5 | 682 | 24.989013 | 0.011 | 0.044% |
| 273.0 | 0x6313 | 6 | 787 | 272.967056 | 0.033 | 0.012% |
| 2063.0 | 0x71E3 | 7 | 483 | 2061.538623 | 1.461 | 0.071% |

### Uniqueness Check

All four values produce **unique encoded uint16 values** (0x50E3, 0x52AA, 0x6313, 0x71E3).
No two mod values collide. However, the **decoded** values are NOT equal to the originals.

### Can `round(decoded) == original` Work?

| Value | round(decoded) | Matches? |
|-------|---------------|----------|
| 15.0 | 15 | YES |
| 25.0 | 25 | YES |
| 273.0 | 273 | YES |
| 2063.0 | **2062** | **NO** |

**2063.0 FAILS round-trip matching** because at scale 7 (1000-10000), the step size
is ~2.198, meaning 2062 and 2063 map to the **same mantissa** (483). The decoded value
2061.54 rounds to 2062, not 2063.

> Cross-link: the companion [cf16-precision-analysis.md § Mod Damage Value Round-Trip Analysis](cf16-precision-analysis.md#mod-damage-value-round-trip-analysis) shows the same four values with the `int()` truncation strategy instead. Both columns are correct — pick the strategy that fits your mod's matching code.

### Integer Collision at Scale 7

At scale 7, every ~2.2 integer values share the same mantissa:

| Mantissa | Integers | Decoded |
|----------|----------|---------|
| 482 | 2060, 2061 | 2059.34 |
| **483** | **2062, 2063** | **2061.54** |
| 484 | 2064, 2065 | 2063.74 |

### Recommended Matching Strategies

**Strategy 1: Tolerance window (RECOMMENDED)**
```python
def identify_weapon_type(decoded_damage):
    targets = {15.0: "type_A", 25.0: "type_B", 273.0: "type_C", 2063.0: "type_D"}
    for target, name in targets.items():
        if abs(decoded_damage - target) < 1.5:
            return name
    return "unknown"
```
All four values pass with a 1.5 tolerance. The minimum separation between any two
mod values is 10.0 (between 15.0 and 25.0), so a 1.5 tolerance has no overlap risk.

**Strategy 2: Encode target and compare uint16 (EXACT)**
```python
# Pre-compute expected encoded values at mod init
EXPECTED = {0x50E3: "type_A", 0x52AA: "type_B", 0x6313: "type_C", 0x71E3: "type_D"}

def identify_weapon_type(received_cf16_uint16):
    return EXPECTED.get(received_cf16_uint16, "unknown")
```
This is perfectly reliable but requires access to the raw uint16 before decoding,
which is only available via C-level hooks, not Python.

**Strategy 3: Range-based matching**
```python
def identify_weapon_type(decoded_damage):
    if 14.0 < decoded_damage < 16.0: return "type_A"
    if 24.0 < decoded_damage < 26.0: return "type_B"
    if 272.0 < decoded_damage < 274.0: return "type_C"
    if 2060.0 < decoded_damage < 2064.0: return "type_D"
    return "unknown"
```

## Extended Precision Reference

| Value | Encoded | Decoded | round() | Match? |
|-------|---------|---------|---------|--------|
| 0.5 | 0x371B | 0.4998 | 0 | YES |
| 1.0 | 0x3FFE | 0.9998 | 1 | YES |
| 5.0 | 0x471B | 4.9978 | 5 | YES |
| 10.0 | 0x4FFE | 9.9978 | 10 | YES |
| 15.0 | 0x50E3 | 14.9890 | 15 | YES |
| 25.0 | 0x52AA | 24.9890 | 25 | YES |
| 100.0 | 0x5FFE | 99.9780 | 100 | YES |
| 273.0 | 0x6313 | 272.967 | 273 | YES |
| 1000.0 | 0x6FFE | 999.780 | 1000 | YES |
| 1500.0 | 0x70E3 | 1498.90 | 1499 | **NO** |
| 2000.0 | 0x71C6 | 1997.80 | 1998 | **NO** |
| 2063.0 | 0x71E3 | 2061.54 | 2062 | **NO** |
| 5000.0 | 0x771B | 4997.80 | 4998 | **NO** |
| 9999.0 | 0x7FFE | 9997.80 | 9998 | **NO** |

**General rule**: `round(decoded) == original` works reliably for values below ~1000.
Above 1000 (scale 7), the step size of ~2.2 means `round()` frequently fails.

## Assessment

**Can mods reliably use damage values as weapon type identifiers through the explosion
wire protocol?**

**YES**, with caveats:

1. The four specific BC Remastered values (15, 25, 273, 2063) all produce **unique
   CF16 encodings** and can be discriminated.

2. **Simple `round()` matching fails for 2063** and all values >= 1000. Mods MUST
   use tolerance-based matching (`abs(decoded - target) < threshold`) instead of
   exact integer comparison.

3. A tolerance of **1.5** works for all four values with no risk of cross-matching
   (minimum inter-value distance is 10.0).

4. For values in scale 7 (1000-10000), integer-level precision is lost. Two different
   integer damage values that are within ~2.2 of each other will be indistinguishable
   after CF16 round-trip. Mod designers choosing new weapon type IDs in this range
   should space them at least 3 apart.

5. For values below 1000, precision is sufficient that every integer value gets a
   unique CF16 encoding. This is the safe range for weapon type identification.

## Related Documents

- [`cf16-precision-analysis.md`](cf16-precision-analysis.md) — Sibling leaf: full CF16 caller list (5 sites), `int()` match column, and the canonical ExplosionDamage struct table.
- [`stream-primitives.md`](stream-primitives.md) — TGBufferStream primitives + CV4 byte-size dispatch (`mag_as_cf16` flag).
- [`game-opcodes.md`](game-opcodes.md) — Opcode 0x29 row.
- [`wire-format-spec.md`](wire-format-spec.md) — Hub doc.
- [`pythonevent-wire-format.md`](pythonevent-wire-format.md) — Related: PythonEvent transport carrying ObjectExploding events alongside the raw 0x29 path.
- [`v5-validation-status.md`](v5-validation-status.md) — Protocol-family campaign tracker; this leaf is row #21. See §6.21 for the validation log entry.
