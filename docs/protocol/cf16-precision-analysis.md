> [docs](../README.md) / [protocol](README.md) / cf16-precision-analysis.md

---
title: CompressedFloat16 (CF16) Precision Analysis
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
  - claim: "CF16 encoder has 5 call sites (xrefs to FUN_006d3a90) — 2 in explosion sender, Ship__WriteStateUpdate, CompressedVector3_Write, plus 1 in a Ghidra-undefined function at 0x005a2b3b"
    address: 0x006d3a90
    function: CompressedFloat16_Encode
    confidence: high
    note: "Sites: 0x00595d90 (explosion radius), 0x00595da1 (explosion damage), 0x005b1e38 (Ship StateUpdate speed, flag 0x10), 0x006d2b8c (CV3 magnitude), 0x005a2b3b (undefined fn, speed-like flag 0x10 gate — see OQ1)."
  - claim: "5th encoder caller at 0x005a2b3b is in a Ghidra-undefined function gated by TEST BL,0x10 (same flag-0x10 speed bit as Ship__WriteStateUpdate)"
    address: 0x005a2b3b
    function: null
    confidence: medium
    note: "Function not yet defined in Ghidra DB (body lives ~0x005a2800-0x005a3000). FMUL float ptr [0x0088d4e4] precedes the encode call. Hypothesis: non-Ship state-writer (torpedo/projectile). See OQ1."
companions:
  - docs/protocol/cf16-explosion-encoding.md
  - docs/protocol/stream-primitives.md
  - docs/protocol/game-opcodes.md
  - docs/protocol/stateupdate.md
  - docs/protocol/wire-format-spec.md
  - docs/protocol/v5-validation-status.md
supersedes:
  - 2026-02-15
---

# CompressedFloat16 (CF16) Precision Analysis

> [!NOTE]
> This doc is `status: verified`. **1 refinement + 1 clarification**. Algorithm, constants, and call-site analysis all byte-confirmed. The xref count is **5 not 4** (extra call site at 0x005a2b3b in an undefined function gated by `TEST BL,0x10`, the same flag-0x10 speed bit used by Ship StateUpdate). Cross-reference added to leaf #21 ([cf16-explosion-encoding.md](cf16-explosion-encoding.md)) for the `round()` match strategy alongside the `int()` match column. All 5 .rdata constants byte-exact (`BASE` / `ZERO` / `MULT` / `ENC_SCALE` / `DEC_SCALE`); encoder/decoder pseudocode matches decompile; ExplosionDamage 0x38-byte struct layout and 14-byte opcode 0x29 wire frame byte-by-byte confirmed via sender (FUN_00595c60) + receiver (FUN_006A0080) + ctor (FUN_004bbde0). See [v5-evidence-header.md](../guides/v5-evidence-header.md) for the standard. Source evidence: `.claude/agent-memory/game-archaeology-specialist/cf16-batch-validation-20260528.md`.

Reverse-engineered from stbc.exe encoder (`FUN_006d3a90`) and decoder (`FUN_006d3b30`).
Constants extracted from .rdata section. All findings verified against decompiled code.

## Format

[v5-validated 2026-05-28]

```
Bit layout: [sign:1][scale:3][mantissa:12] = 16 bits total
  Bit 15     = sign (1=negative, 0=positive)
  Bits 14-12 = scale exponent (0-7)
  Bits 11-0  = mantissa (0-4095)
```

## Constants (from stbc.exe .rdata)

[v5-validated 2026-05-28]

| Symbol | Address | Hex Bytes | Value | Role |
|--------|---------|-----------|-------|------|
| BASE | DAT_00888b4c | 6F 12 83 3A | 0.001 (float32) | Scale range base |
| ZERO | DAT_00888b54 | 00 00 00 00 | 0.0 | Negative comparison |
| MULT | DAT_0088c548 | 00 00 20 41 | 10.0 (float32, exact) | Scale multiplier |
| ENC_SCALE | DAT_00895f50 | 00 F0 7F 45 | 4095.0 (float32, exact) | Encoder mantissa scale |
| DEC_SCALE | DAT_00895f54 | 01 08 80 39 | float32(1/4095) = 0.000244200258... | Decoder mantissa inverse |

**Critical finding**: The decoder constant is `1/4095`, NOT `1/4096`. This makes the system symmetric:
- Encoder: `mantissa = floor(fraction * 4095.0)`
- Decoder: `value = range * mantissa * (1/4095) + range_lo`
- Mantissa 4095 decodes to exactly the top of the range (range_hi)
- 4096 discrete levels: 0, 1/4095, 2/4095, ..., 4095/4095

## Encoder Algorithm (FUN_006d3a90)

[v5-validated 2026-05-28]

```c
uint16 CF16_Encode(float value) {
    bool sign = (value < 0.0f);
    if (sign) value = -value;

    uint scale = 0;
    float boundary = BASE;  // 0.001
    while (scale < 8) {
        if (value < boundary) break;
        boundary *= MULT;   // *= 10.0
        scale++;
    }

    if (scale >= 8) {
        // Overflow: clamp to max
        return (sign ? 0xFFFF : 0x7FFF);  // scale=7, mantissa=0xFFF
    }

    // Compute range for this scale
    float lo, hi;
    if (scale == 0) { lo = 0.0; hi = BASE; }
    else { lo = BASE * pow(MULT, scale-1); hi = BASE * pow(MULT, scale); }

    // Fractional position in range, scaled to [0, 4095]
    float frac = (value - lo) / (hi - lo);
    int mantissa = (int)(frac * 4095.0f);  // __ftol: truncate toward zero
    mantissa = min(mantissa, 4095);

    return ((sign << 3) | scale) << 12 | mantissa;
}
```

## Decoder Algorithm (FUN_006d3b30)

[v5-validated 2026-05-28]

```c
float CF16_Decode(uint16 raw) {
    int mantissa = raw & 0xFFF;
    int scale = (raw >> 12) & 0x7;
    bool sign = (raw >> 15) & 1;

    // Rebuild range iteratively (matches x87 FPU behavior)
    float lo = 0.0f;    // starts at DAT_00888b54 = 0.0
    float hi = BASE;    // starts at DAT_00888b4c = 0.001
    for (int i = 0; i < scale; i++) {
        lo = hi;
        hi = lo * MULT;  // *= 10.0
    }

    // Decode: uses float32(1/4095) loaded into x87 extended precision
    float result = (hi - lo) * (float)mantissa * DEC_SCALE + lo;

    if (sign) result = -result;
    return result;
}
```

## Scale Table

[v5-validated 2026-05-28]

| Scale | Range Low | Range High | Step Size | Relative Precision |
|-------|-----------|------------|-----------|-------------------|
| 0 | 0 | 0.001 | 2.442e-7 | ~0.024% |
| 1 | 0.001 | 0.01 | 2.198e-6 | ~0.022% |
| 2 | 0.01 | 0.1 | 2.198e-5 | ~0.022% |
| 3 | 0.1 | 1 | 2.198e-4 | ~0.022% |
| 4 | 1 | 10 | 2.198e-3 | ~0.022% |
| 5 | 10 | 100 | 2.198e-2 | ~0.022% |
| 6 | 100 | 1000 | 2.198e-1 | ~0.022% |
| 7 | 1000 | 10000 | 2.198 | ~0.022% |

Maximum encodable value: ~10000.0 (clamped at scale=7, mantissa=4095).
Dynamic range: 0 to 10000 in 8 logarithmic decades, each with 4096 steps.

## Precision Characteristics

The encoding always introduces error because the mantissa is truncated (floor), not rounded.
Maximum error per scale is one step size (the truncation residual).

For scale S, step size = (range_hi - range_lo) / 4095.

The decoder's `float32(1/4095)` constant introduces a tiny additional bias:
- `float32(1/4095)` = 0.000244200258... vs exact `1/4095` = 0.000244200244...
- Relative error: ~6e-6% (negligible compared to quantization)

## Explosion Packet (Opcode 0x29) Wire Format

[v5-validated 2026-05-28]

**Sender**: `FUN_00595c60` (DamageableObject_SendExplosions_0x29; iterates explosion damage list at `this+0x13C`)
**Receiver**: `Handler_Explosion_0x29` at `0x006A0080`

```
Offset  Size  Encoding     Field
------  ----  -----------  --------------------------------
0       1     byte         opcode = 0x29
1       4     uint32       objectID (target ship)
5       5     CV4          impact_position (3 dir bytes + CF16 magnitude)
10      2     CF16         radius
12      2     CF16         damage
------
Total: 14 bytes
```

**Field order verified**: The sender writes `CF16(source+0x14)` = radius first (xref 0x00595d90),
then `CF16(source+0x1C)` = damage second (xref 0x00595da1). The receiver passes them to the
ExplosionDamage constructor as `(position, radius, damage)`.

The receiver allocates a 0x38-byte ExplosionDamage object via `FUN_00718cb0(0x38)`, built by
`FUN_004bbde0` (vtable hardcoded to `0x0088c6c4`):

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

> Cross-link: the same struct table appears in [cf16-explosion-encoding.md § Explosion Packet](cf16-explosion-encoding.md#explosion-packet-opcode-0x29-wire-format). Either doc is canonical; render is kept in both for in-context reading.

Then calls `ProcessDamage(ship, explosionDamageObj)` to apply the damage.

**ALL float fields in this packet are compressed — there are NO raw float32 values.**

## Mod Damage Value Round-Trip Analysis

BC Remastered mods use specific damage float values as weapon type identifiers.
Client-side scripts check `pEvent.GetDamage()` for these exact values to apply
special visual effects. These values pass through CF16 compression when sent
over the network via opcode 0x29.

| Value | Name | Scale | Mantissa | Decoded | Error | int() Match |
|-------|------|-------|----------|---------|-------|-------------|
| 15.0 | Borg Inversion Pulse | 5 | 227 | 14.989 | 0.011 (0.073%) | FAIL (14) |
| 25.0 | Breen Drain | 5 | 682 | 24.989 | 0.011 (0.044%) | FAIL (24) |
| 273.0 | Hellbore | 6 | 787 | 272.967 | 0.033 (0.012%) | FAIL (272) |
| 2063.0 | Plasma Snare | 7 | 483 | 2061.539 | 1.461 (0.071%) | FAIL (2061) |

**Clar1 — `int()` vs `round()` match strategies.** The `int() Match` column above
truncates toward zero — all four mod values FAIL this test. For the alternative
`round(decoded) == original` strategy (which succeeds for 3 of the 4 BC Remastered
values), see [cf16-explosion-encoding.md § Precision Analysis: BC Remastered Weapon Type IDs](cf16-explosion-encoding.md#precision-analysis-bc-remastered-weapon-type-ids).
Both columns are correct — they answer different questions and the two docs together
give mod authors the full picture.

**None of these values survive the round-trip via `int()` truncation.**

The truncation is always downward (floor), so:
- `int(decoded)` is always `original - 1` for these values
- Values at scale 7 (1000-10000) lose up to 2.2 per step

### Implications for Mods

The stock vanilla `Effects.py` does NOT check `GetDamage()` — it only uses
`GetRadius()` for visual effect sizing. The damage-as-type-identifier pattern
is purely a mod invention.

For mod compatibility, scripts checking damage values must use one of:
1. **Tolerance comparison**: `abs(damage - expected) < step_size`
   - Safe threshold per scale: scale 4=0.003, scale 5=0.03, scale 6=0.3, scale 7=3.0
2. **Round to nearest integer**: `int(damage + 0.5) == expected` (i.e., `round()`)
3. **Range comparison**: `expected - 1 < damage < expected + 1`
4. **Different encoding**: Use a field that doesn't go through CF16

### Integer Values That Nearly Survive

At scale 4 (1-10): all integers decode within 0.003 of original.
At scale 5 (10-100): all integers decode within 0.022 of original.
At scale 6 (100-1000): all integers decode within 0.22 of original.
At scale 7 (1000-10000): all integers decode within 2.2 of original.

No integer value exactly survives a CF16 round-trip via `int()` truncation. The closest
are values at range boundaries (e.g., 1.0, 10.0, 100.0, 1000.0) which decode within
~0.0002 to ~0.002 of the original. With `round()` matching, integers up to ~1000 do
survive — see [cf16-explosion-encoding.md](cf16-explosion-encoding.md) for the full table.

## Other Uses of CF16

[v5-validated 2026-05-28]

CF16 is used throughout the multiplayer protocol. All callers confirmed via xref
analysis of `FUN_006d3a90` (**5 call sites total** — was "4" in the pre-v5 doc).

| # | Caller | Site | Field | Notes |
|---|--------|------|-------|-------|
| 1 | `DamageableObject__SendExplosions_0x29` (FUN_00595c60) | 0x00595d90 | radius | Opcode 0x29 sender |
| 2 | `DamageableObject__SendExplosions_0x29` (FUN_00595c60) | 0x00595da1 | damage | Opcode 0x29 sender |
| 3 | `Ship__WriteStateUpdate` (FUN_005b1e38) | within sender body | speed | StateUpdate flag 0x10 |
| 4 | `CompressedVector3_Write` (FUN_006d2b8c) | within writer body | magnitude | CV3 magnitude field |
| 5 | Undefined function near 0x005a2800-0x005a3000 | 0x005a2b3b | speed-like | StateUpdate flag 0x10 gate confirmed (`TEST BL,0x10`); likely a non-Ship state-writer (torpedo/projectile per OQ1) `[open question — OQ1: function identity]` |

Decoder symmetry: 5 xrefs to `FUN_006d3b30` as well, paired with each of the encoder sites
(`Ship__ReadStateUpdate`, `FUN_006a0080` ×2, `0x005a2fb4` paired with the `0x005a2b3b` sender,
`0x006d2ba5` paired with CV3_Write).

## Open Questions

- **OQ1** — The Ghidra-undefined function at `~0x005a2800-0x005a3000` containing the 5th
  encoder caller (call site 0x005a2b3b): what object type does it serialize? The
  `TEST BL,0x10` gate + `FMUL float ptr [0x0088d4e4]` preceding the encode call suggest a
  speed-like value with a unit-conversion multiplier — hypothesis: a non-Ship state-writer
  (torpedo or projectile). Non-blocking for this doc: the field, gate, and call-site are
  documented; only the parent function identity is open. Would require `create_function` at
  the prologue + decompile to confirm.

## Related Documents

- [`cf16-explosion-encoding.md`](cf16-explosion-encoding.md) — Sibling leaf: opcode 0x29 wire-format detail + mod weapon-type ID round-trip with the `round()` match strategy alongside this doc's `int()` column.
- [`stream-primitives.md`](stream-primitives.md) — TGBufferStream primitives + CF16/CV3/CV4 byte-level dispatch.
- [`game-opcodes.md`](game-opcodes.md) — Opcode 0x29 row; cross-link target for the CF16 fields.
- [`stateupdate.md`](stateupdate.md) — Opcode 0x1C flag 0x10 (speed) cites the CF16 encoder anchored in this doc.
- [`wire-format-spec.md`](wire-format-spec.md) — Hub doc; CF16 used in multiple opcodes summarized here.
- [`v5-validation-status.md`](v5-validation-status.md) — Protocol-family campaign tracker; this leaf is row #20. See §6.20 for the validation log entry.
