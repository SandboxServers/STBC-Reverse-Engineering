---
name: cf16-batch-validation-20260528
description: v5 validation batch of cf16-precision-analysis.md (leaf #20) + cf16-explosion-encoding.md (leaf #21); 5 constants byte-confirmed; CV4=5 bytes (cf16-explosion-encoding's "~7 bytes" wrong); xref count 5 not 4; round vs int columns in two docs are NOT contradictory (different match strategies, both correct).
metadata:
  type: project
---

# CF16 Batch Validation 2026-05-28

Validated `docs/protocol/cf16-precision-analysis.md` (leaf #20) and `docs/protocol/cf16-explosion-encoding.md` (leaf #21) together because they share the same Ghidra anchors and cover overlapping ground.

## Foundation reuse — all verified

5 .rdata constants confirmed byte-for-byte:

| Symbol | Address | Hex (binary) | Value |
|---|---|---|---|
| BASE | DAT_00888b4c | `6F 12 83 3A` | 0.001f |
| ZERO | DAT_00888b54 | `00 00 00 00` | 0.0f |
| MULT | DAT_0088c548 | `00 00 20 41` | 10.0f |
| ENC_SCALE | DAT_00895f50 | `00 F0 7F 45` | 4095.0f |
| DEC_SCALE | DAT_00895f54 | `01 08 80 39` | float32(1/4095) ≈ 0.000244200258 |

Encoder/decoder decompiles match doc pseudocode at FUN_006d3a90 + FUN_006d3b30.

## Per-doc verdicts

### leaf #20 cf16-precision-analysis.md → **partial**
Algorithm + constants + sender/receiver/struct layout correct. Two material issues:
- "4 call sites total" undercounts encoder xrefs (actual = 5)
- Sender claim is fine: doc says `FUN_00595c60` iterates explosion list at `this+0x13C` — confirmed via decompile.

### leaf #21 cf16-explosion-encoding.md → **partial**
Algorithm + constants + encoded hex values for 15/25/273/2063 + round() match results correct. One material wire-format issue:
- CV4 byte size labeled "variable, ~7 bytes" — WRONG for explosion path. Explosion uses CV4 with `mag_as_cf16=1`, total = 5 bytes (3 dir bytes + 2-byte CF16 magnitude). The 7-byte path is for `mag_as_cf16=0` (raw float32 magnitude), which the explosion sender does NOT use.

## Cross-doc disagreement reconciliation

### Disagreement #1 — Round-trip match for 25.0
- **cf16-precision-analysis.md** Mod Damage table: "25.0 → decoded 24.989 → int() Match: FAIL (24)"
- **cf16-explosion-encoding.md** round() table: "25.0 → decoded 24.989013 → round(): 25 → YES"

**Resolution**: Both correct, different questions.
- `int(24.989) = 24` (truncate-toward-zero) — FAIL
- `round(24.989) = 25` (banker's/away-from-zero) — YES

Doc #20 column header is "int() Match"; doc #21 column header is "round() Matches". No conflict. Both columns should be retained; the doc audience can pick the strategy.

Arithmetic verification (25.0):
- scale = 5, range = [10, 100], step = 90/4095 ≈ 0.02198
- frac = 15/90 = 0.16666...
- mantissa = floor(0.16666 * 4095) = floor(682.5) = **682** ✓
- Decoded = 90 * 682 * 0.000244200258 + 10 ≈ 14.9893 + 10 = **24.9893**

### Disagreement #2 — CV4 byte size
- **cf16-precision-analysis.md**: "CV4 = 5 bytes (3 dir bytes + CF16 magnitude)"
- **cf16-explosion-encoding.md**: "CompressedVector4 (variable, ~7 bytes)"

**Resolution**: cf16-precision-analysis.md is right for the explosion path.

`CompressedVector4_WriteVirtual` at 0x006d2f10 dispatches on param_5 (mag_as_cf16 flag):
- `param_5 != 0` → 3 byte writes (vtable+0x54) + 1 short write (vtable+0x5C) = **5 bytes**
- `param_5 == 0` → 3 byte writes + 1 float write (vtable+0x74) = **7 bytes**

`DamageableObject__SendExplosions_0x29` calls `CompressedVector4_WriteVirtual(..., 1)` → 5-byte path. Receiver `FUN_006a0080` calls `CompressedVector4_ReadVirtual(..., 1)` → same.

Full opcode 0x29 frame: 1 + 4 + **5** + 2 + 2 = **14 bytes** total. Both docs claim 14 total — consistent only if CV4=5 bytes.

### Disagreement #3 — encoder xref count
Neither doc explicitly disagrees here, but **cf16-precision-analysis.md** claims "4 call sites total". Actual xrefs to FUN_006d3a90:

| # | From | Function | Field |
|---|---|---|---|
| 1 | 00595d90 | DamageableObject__SendExplosions_0x29 | radius |
| 2 | 00595da1 | DamageableObject__SendExplosions_0x29 | damage |
| 3 | 005b1e38 | Ship__WriteStateUpdate | speed (flag 0x10) |
| 4 | 006d2b8c | CompressedVector3_Write | magnitude |
| 5 | 005a2b3b | (no Ghidra fn defined; gated by TEST BL,0x10) | speed (writer for another object type) |

**5 sites, not 4.** Site #5 is in an undefined function (~0x005a2800-0x005a3000+, also in `04_ui_windows` / `03_game_objects` decompile family — likely a non-Ship `WriteStateUpdate` path; `TEST BL,0x10` is the same flag-0x10 speed bit). The doc text "All callers confirmed via xref analysis (4 call sites)" needs to be updated to "5 call sites including an additional WriteStateUpdate path at 0x005a2b3b in a Ghidra-undefined function".

Decoder symmetry: 5 xrefs to FUN_006d3b30 as well (Ship__ReadStateUpdate, FUN_006a0080 ×2, 0x005a2fb4 paired with the 0x005a2b3b sender, 0x006d2ba5 paired with CV3_Write).

## Confirmed claims (both docs)

**Algorithm**:
- Bit layout `[sign:1][scale:3][mantissa:12]` ✓
- Scale loop: 8 max iterations (try scales 0..7), overflow → scale=7 mantissa=0xFFF ✓
- Encoder mantissa = `__ftol((value-lo)/(hi-lo) * 4095.0)` (truncate-toward-zero) ✓
- Decoder iterative range rebuild matches x87 FPU ✓
- Decoder uses float32(1/4095), NOT 1/4096 ✓
- 4096 discrete levels per scale, mantissa 4095 maps to exactly range_hi ✓

**Scale table** (verified by arithmetic):
- Scales 0-7 cover [0,0.001), [0.001,0.01), …, [1000,10000)
- Step sizes 2.442e-7, 2.198e-6, 2.198e-5, …, 2.198 ✓
- "2.198e-2" / "2.20e-2" (the two docs' rendering of scale 5 step) are the same number rounded — no conflict

**BC Remastered values** (verified by arithmetic + decompile):
| Value | Scale | Mantissa | Encoded | Decoded | int() | round() |
|---|---|---|---|---|---|---|
| 15.0 | 5 | 227 | 0x50E3 | 14.9890 | 14 (FAIL) | 15 (MATCH) |
| 25.0 | 5 | 682 | 0x52AA | 24.9893 | 24 (FAIL) | 25 (MATCH) |
| 273.0 | 6 | 787 | 0x6313 | 272.967 | 272 (FAIL) | 273 (MATCH) |
| 2063.0 | 7 | 483 | 0x71E3 | 2061.539 | 2061 (FAIL) | 2062 (FAIL) |

**Opcode 0x29 wire frame** (14 bytes, verified byte-by-byte in sender + receiver):
```
[0x29]                  opcode (1 byte)
[uint32 objID]          target object ID (4 bytes)
[CV4 with CF16 mag]     impact position (5 bytes)
[CF16 radius]           explosion radius (2 bytes)
[CF16 damage]           explosion damage (2 bytes)
                        ============
                        14 bytes total
```
Field order in sender (DamageableObject__SendExplosions_0x29 @ 0x00595c60):
1. Opcode 0x29 (TGBufferStream_swig_WriteChar)
2. ObjID = `*(int*)(this+4)` (FUN_006cf930)
3. Position = explosion+0x08/+0x0C/+0x10 (CompressedVector4_WriteVirtual)
4. Radius = `*(float*)(explosion+0x14)` (CF16_Encode → WriteShort)
5. Damage = `*(float*)(explosion+0x1C)` (CF16_Encode → WriteShort)

Receiver (FUN_006a0080) reads in same order, then calls `FUN_004bbde0(position, fStack_50=radius, fStack_54=damage)`.

**ExplosionDamage struct** (constructed at FUN_004bbde0, vtable PTR_LAB_0088c6c4):
| Offset | Size | Field | Source |
|---|---|---|---|
| +0x00 | 4 | vtable = 0x0088c6c4 | hardcoded in ctor |
| +0x04 | 4 | base class (unused or padding) | (set by parent ctor FUN_007d87a0) |
| +0x08 | 4 | position.x (float) | param_2[0] |
| +0x0C | 4 | position.y (float) | param_2[1] |
| +0x10 | 4 | position.z (float) | param_2[2] |
| +0x14 | 4 | radius (float) | param_3 |
| +0x18 | 4 | radius² (float, precomputed) | `param_3 * param_3` |
| +0x1C | 4 | damage (float) | param_4 |
| +0x20–+0x28 | 12 | bbox min (3 floats) | filled by FUN_004bbec0 |
| +0x2C–+0x34 | 12 | bbox max (3 floats) | filled by FUN_004bbec0 |
| Total | **0x38** | | matches `FUN_00718cb0(0x38)` allocator call in receiver |

**Sender callers** (cf16-explosion-encoding.md claim):
- `MultiplayerGame__RequestObjHandler @ 0x006a02a0` ✓
- `NewPlayerInGameHandler @ 0x006a1e70` (= "Handler_NewPlayerInGame_0x2A" in doc) ✓

## Triage

### leaf #20 cf16-precision-analysis.md

- **R1**: "All callers confirmed via xref analysis of FUN_006d3a90 (4 call sites total)" → should be **5 call sites**. The 5th is in a Ghidra-undefined function near 0x005a2800-0x005a3000+, gated by `TEST BL,0x10` (flag-0x10 speed bit). Likely a non-Ship state-writer (torpedo/projectile?). Refinement, not correction — claim is approximately right and the docwriter can choose to merge the 5th site into the existing list (StateUpdate / Ship_WriteStateUpdate / CompressedVector3 / Explosion ×2).

- **R2**: "Receiver creates a 0x38-byte ExplosionDamage object" → fully confirmed via FUN_00718cb0(0x38) + FUN_004bbde0 layout. Doc already correct; no change needed.

- **Clar1**: "int() Match" column intent — clarify that this column tracks `int(decoded)` (truncate-toward-zero) FAILures; companion doc #21 shows `round()` MATCHes which are mostly YES for the first 3 mod values. Add a note that pairing with round() lets 3 of the 4 BC Remastered values survive round-trip.

### leaf #21 cf16-explosion-encoding.md

- **C1**: "[position] CompressedVector4 (variable, ~7 bytes)" in the wire format diagram → must be **5 bytes** for the explosion path. The 7-byte variant only applies when CV4 is called with `mag_as_cf16=0` (raw float32 magnitude), and DamageableObject__SendExplosions_0x29 always passes `1`. The total of 14 bytes (which the doc states elsewhere) is only achievable with 5-byte CV4. The "~7 bytes" parenthetical contradicts the 14-byte total.

- **Clar1**: Recommendation to add a note that the in-memory ExplosionDamage struct is 0x38 bytes (allocated via FUN_00718cb0(0x38) in the receiver), separate from the wire format. cf16-precision-analysis.md already has the struct table; doc #21 only mentions `+0x14=radius, +0x18=radius^2, +0x1C=damage` in passing.

- **R1**: Encoder pseudocode `if (scale == 8)` block is correct but the doc shows `mantissa = 0xFFF; scale = 7;` set INSIDE the `if`, which is fine. The actual binary sets `scale = 7` via `(int)flValue` math trick. Both render to the same behavior. No change needed.

## Open questions

- **OQ1**: The Ghidra-undefined function containing the 5th encoder caller at 0x005a2b3b: what object type does it serialize? `TEST BL,0x10` + `FMUL float ptr [0x0088d4e4]` immediately before the encode suggests a speed-like value with a unit-conversion multiplier (DAT_0088d4e4 = 60.0f? or 0.0166...?). Would help to define this Ghidra function and identify which game class uses it. Non-blocking for both CF16 docs — the dispatcher and field-of-call are documented sufficiently as "an additional state-writer path".

- **OQ2**: cf16-explosion-encoding.md "Extended Precision Reference" table includes values not directly observed in stock traces (e.g., 5000.0, 9999.0). These are valid arithmetic projections of the CF16 algorithm but not "field-verified" — they're algorithmically correct given the encoder/decoder confirmed at addresses above. No follow-up needed; the math is sound.

## Anchor table (frontmatter inputs for docwriter)

### leaf #20 cf16-precision-analysis.md

| address | function | role | confidence | completeness | notes |
|---|---|---|---|---|---|
| 0x006d3a90 | CompressedFloat16_Encode | encoder | high | 52.6 effective | plate exists, claims confirmed |
| 0x006d3b30 | CompressedFloat16_Decode | decoder | high | 49.1 effective | plate exists, claims confirmed |
| 0x00595c60 | DamageableObject__SendExplosions_0x29 | sender | high | 0 effective (load-bearing) | claims confirmed via decompile; needs plate |
| 0x006A0080 | Handler_Explosion_0x29 (FUN_006a0080) | receiver | high | 0 effective (load-bearing) | claims confirmed; needs plate + rename |
| 0x004bbde0 | ExplosionDamage_Ctor | struct ctor | high | (not checked) | struct layout matches doc |
| 0x00888b4c | DAT_00888b4c | BASE constant | high | n/a | 6F 12 83 3A = 0.001f |
| 0x00888b54 | DAT_00888b54 | ZERO constant | high | n/a | 00 00 00 00 = 0.0f |
| 0x0088c548 | DAT_0088c548 | MULT constant | high | n/a | 00 00 20 41 = 10.0f |
| 0x00895f50 | DAT_00895f50 | ENC_SCALE constant | high | n/a | 00 F0 7F 45 = 4095.0f |
| 0x00895f54 | DAT_00895f54 | DEC_SCALE constant | high | n/a | 01 08 80 39 = float32(1/4095) |
| 0x005b1e38 | (xref site) | Ship__WriteStateUpdate flag-0x10 speed encoder call | high | n/a | TEST byte [ESP+0x14],0x10 confirms flag |
| 0x006d2b8c | (xref site) | CompressedVector3_Write magnitude encoder call | high | n/a | |
| 0x005a2b3b | (xref site) | undefined function speed encoder call | medium | n/a | function not defined; flag-0x10 path |

### leaf #21 cf16-explosion-encoding.md

Same anchor table as leaf #20 (shared algorithm + explosion path).

Additional anchor specific to leaf #21:
| address | function | role | confidence | notes |
|---|---|---|---|---|
| 0x006d2f10 | CompressedVector4_WriteVirtual | CV4 writer (variable width) | high | param_5 flag controls magnitude encoding (5 vs 7 bytes) |
| 0x006d2fd0 | CompressedVector4_ReadVirtual | CV4 reader | high | symmetric |
| 0x006a02a0 | MultiplayerGame__RequestObjHandler | sender caller | high | xref to FUN_00595c60 |
| 0x006a1e70 | NewPlayerInGameHandler | sender caller | high | xref to FUN_00595c60 |

## Suggested cross-doc cascade

1. **docs/protocol/stream-primitives.md** — already documents CF16, CV3, CV4. Should:
   - Cross-link to both leaves (#20 and #21) for the CF16 deep dive.
   - Reconcile CV4 byte size: explicitly note that CV4 = 5 bytes (CF16 magnitude path, used by explosions, weapons, position diffs) or 7 bytes (raw float magnitude path, used elsewhere — verify which callers). The `mag_as_cf16` param_5 is the discriminator.

2. **docs/protocol/game-opcodes.md** — opcode 0x29 row should reference both CF16 docs for the wire-format details.

3. **docs/protocol/stateupdate.md** — flag 0x10 (speed) cites CF16 encoder; should anchor to leaf #20 for the algorithm.

4. **docs/protocol/collision-effect-protocol.md** — uses CompressedVec4_Byte; cross-link to confirm the 5-byte CV4 interpretation.

5. **OpenBC clean-room specs** — when porting opcode 0x29 spec, MUST use 5-byte CV4 with CF16 magnitude. The OpenBC docwriter should be alerted if they took "~7 bytes" from cf16-explosion-encoding.md.

## Annotations applied

Plate comments on `CompressedFloat16_Encode` and `CompressedFloat16_Decode` already exist (from prior stream-primitives validation). No new annotations added — the docs themselves are the durable artifact for the CF16 leaves.

No Ghidra renames, no struct changes, no function-prototype changes this session — only verification work.

Save state: program saved at end of session.
