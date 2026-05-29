---
name: networking-foundation-gamespy-crypto-validation-20260528
description: v5 validation of docs/networking/gamespy-crypto-analysis.md — networking foundation #4 (challenge-response crypto, sibling of gamespy-discovery). ZERO algorithm corrections. Three corrections: gamever wire literal is "1.6" not "1.1"; ServerList table mis-labels timer (+0x94 not +0x08); +0x9C is a state field, not padding. One clarification: qr_t "SOCKET* arithmetic" narrative doesn't reflect current decompilation (offset is plain byte +0x48).
metadata:
  type: project
---

# gamespy-crypto-analysis.md v5 Validation — 2026-05-28

Networking foundation doc #4 (companion to gamespy-discovery.md). Validated 511 lines covering RC4 cipher, base64-like encoding, character map, secret key storage, and the QR + ServerList parallel paths.

**Validation method:** Algorithm fns decompiled byte-by-byte and cross-checked against the reconstructed pseudocode; struct offsets verified via decompiled callers (gs_list_init, SL_master_connect, qr_send_validate_and_final); wire-format string literals read from .rdata.

## Anchors (all v5-validated, byte-confirmed)

| Address | Symbol | Role | Anchor |
|---|---|---|---|
| 0x006ac050 | gs_rc4_cipher | KSA + modified PRGA | Byte-confirmed: PRGA `i = data[n]+1+i mod 256`, XOR uses `S[(S[j]+S[i]) & 0xFF]` |
| 0x006abf70 | gs_validate_encode | 3→4 base64-like | Byte-confirmed: shifts/masks produce a,b,c,d 6-bit fields exactly as doc |
| 0x006ac020 | gs_encode_char | 6-bit → ASCII | Byte-confirmed: A-Z/a-z/0-9/+// with `(val != 0x3f) - 1 & 0x2f` trick for '/' |
| 0x006ac1c0 | gs_swap | byte swap helper | Byte-confirmed: 3-line tmp swap |
| 0x006ac950 | qr_send_validate_and_final | QR validate path | Confirmed: calls cipher with `param_1+0x48`, then encode, then `\validate\%s` sprintf |
| 0x006aa4c0 | SL_master_connect | ServerList auth path | Confirmed: calls cipher with `(param_1+0x2c, 6, pcVar3+8, 6)`; gamename from +0x4C |
| 0x006aa100 | gs_list_init | ServerList ctor | Confirmed: malloc(0xA0); copies game name → +0x0C, secret → +0x2C, second name → +0x4C |
| 0x0069c3a0 | GameSpy::InitBrowser | "Nm3aZ9" producer | Confirmed: stack-built locals 0x4e/0x6d/0x33/0x61/0x5a/0x39/0x00 = "Nm3aZ9\0" |
| 0x006ad180 | (entry hash ctor) | 0x18-byte hash, 0x40 buckets | Confirmed; stored at ServerList+0x04 |
| 0x006acb30 | (poll/timer ctor) | 0x14-byte timer/poll | Confirmed; stored at ServerList+**0x94** (puVar3[0x25]), NOT +0x08 |

## .rdata anchors

| Address | Bytes | String |
|---|---|---|
| 0x00959c24 | `62636f6d6d616e646572 00` | `"bcommander"` |
| 0x0095a624 | full read | `"\gamename\%s\gamever\%s\location\0\validate\%s\final\\queryid\1.1\"` |
| 0x0095a668 | `31 2e 36 00` | `"1.6"` ← gamever literal at runtime |
| 0x0095a66c | `5c 73 65 63 75 72 65 5c 00` | `"\secure\"` |
| 0x0095a678 | `5c 66 69 6e 61 6c 5c 00` | `"\final\"` |
| 0x0095a8e0 | `5c 76 61 6c 69 64 61 74 65 5c 25 73 00` | `"\validate\%s"` |

## Doc Issues (Corrections + Clarifications)

### C1 — wire example version string

§ "Wire Format Examples" lines 414 shows:
```
Client -> Master (TCP): \gamename\bcommander\gamever\1.1\location\0\validate\XXXXXXXX\final\\queryid\1.1\
```
The `\queryid\1.1\` suffix is correct (format string literal at +0x40 from 0x0095a624). But the `\gamever\1.1\` field is **derived from `DAT_0095a668 = "1.6"`** at runtime. Wire actually emits `\gamever\1.6\`. Doc has the right format template, wrong substituted value.

### C2 — ServerList struct table mis-labels timer slot

§ "Server List Struct Layout" claims:
```
| +0x08 | 4 | Timer/poll struct | FUN_006acb30 |
```
**Wrong.** Decompiled `gs_list_init` writes the FUN_006acb30 result to `puVar3[0x25]` = byte **+0x94**, not +0x08. Nothing is written to +0x08 in the constructor. The doc's row should be:
```
| +0x94 | 4 | Poll/timer struct (FUN_006acb30, 500 entries) | gs_list_init |
```

### C3 — ServerList +0x9C is a state field, not padding

§ same table claims `+0x9C` is "Padding/unused". **Wrong.** SL_master_connect writes 0 to `*(undefined4 *)(param_1 + 0x9c)` in two branches (groups path and info2 path), so it is a state/mode side-channel. Likely related to the +0x90 mode field already in the table.

### Clar1 — qr_t "SOCKET* arithmetic" narrative

§ "Secret Key" and § "qr_t Struct Layout (Corrected)" walk through a `SOCKET*` typing → multiply-by-4 explanation to justify `param_1 + 0x12` → byte 0x48. The current decompilation at FUN_006ac950 actually shows `param_1 + 0x48` as a **plain byte offset** (no SOCKET typing visible). The doc's narrative is harmless and the conclusion (0x48) is correct, but the multiplication storytelling reflects an older Ghidra session's typing that has since been reset. Future readers may be confused — recommend collapsing to "secret key at byte offset +0x48 in the qr_t struct".

### Clar2 — qr_t table is for a different struct than the GameSpy object

The "GameSpy" struct (passed as param_1 to FUN_0069c3a0) and the "qr_t" struct (passed as param_1 to FUN_006ac950) are NOT the same. Offsets like +0xDC (server list ptr), +0xE0 (GameSpy.serverList), +0xED (init guard byte), +0xEE (other flag) are **GameSpy**, not qr_t. The doc's qr_t table contains some plausible offsets but they aren't anchored to FUN_006ac950's actual decompilation — they appear to be carried over from an external source (real GameSpy QR1 SDK source). Marking them as "Corrected" is misleading since this validation pass cannot anchor most rows.

## Algorithm cross-anchors (sibling doc)

These all match `gamespy-discovery.md` validation memo:
- gs_rc4_cipher @ 0x006ac050 ✓
- Secret key "Nm3aZ9" at ctor 0x0069c3a0 ✓
- ServerList +0x2C secret key storage ✓

## Open questions

- **OQ1**: The qr_t struct (param_1 to FUN_006ac950) — we anchored ONLY the +0x48 secret key offset. The full qr_t struct table in the doc lists 13 fields with byte offsets, none verified in this pass. Resolving would require chasing the qr_t initializer (likely FUN_006ac1e0 or a callee that mallocs and populates the qr_t struct via FUN_006ac5f0/006ac7a0/...).
- **OQ2**: gamever string source — "1.6" lives at 0x0095a668. What writes `\gamever\1.6\` to the wire is the SL_master_connect sprintf using literal `&DAT_0095a668`. Is there a code path that uses "1.1" (matching the doc example) for the same template? Unlikely — but worth confirming the doc's "1.1" was a typo, not a real second wire variant.
- **OQ3**: Whether OpenBC's clean-room spec for the master-server validate path uses "1.6" or "1.1" — if OpenBC implementation has "1.1" it will be rejected by stock BC clients that send the literal "1.6". Worth a cross-check against OpenBC docs.

## Recommended doc edits (when documentation-writer engages)

1. Fix wire example `\gamever\1.1\` → `\gamever\1.6\` and add note `(literal at 0x0095a668)`.
2. Replace ServerList table row `+0x08 Timer/poll` with `+0x94 Poll/timer struct (FUN_006acb30)` and remove or re-label +0x08 (nothing observed written there in constructor).
3. Re-label ServerList `+0x9C` row from "Padding/unused" to "Mode-side state field (cleared by SL_master_connect on group/info2 paths)".
4. Collapse the qr_t SOCKET*-arithmetic narrative to a one-line "secret key at byte offset +0x48".
5. Add a margin note that the qr_t struct table beyond +0x48 is **derived from external GameSpy SDK references**, not directly anchored in stbc.exe — marked as `[v5-unanchored]` with `OQ1` referenced.
6. Add v5 frontmatter (`validated`, `binary.size`, evidence rows for the 9 anchored addresses, status: validated-with-corrections).

## Confidence summary

| Section | Confidence | Notes |
|---|---|---|
| Algorithm (RC4 + base64 + char map + swap) | **HIGH** | All bytes confirmed in decompilation |
| Secret key value "Nm3aZ9" | **HIGH** | Six stack-byte literals confirmed |
| ServerList +0x2C key offset | **HIGH** | Confirmed in SL_master_connect call |
| qr_t +0x48 key offset | **HIGH** | Confirmed in qr_send_validate_and_final call |
| ServerList struct table | **MEDIUM** | Multiple rows wrong (timer slot, padding slot); core fields right |
| qr_t struct table (beyond +0x48) | **LOW** | Looks like SDK-derived speculation; not anchored to this binary |
| Wire format examples | **HIGH** for templates / **MEDIUM** for substituted values (gamever drift) |
| Reimplementation code | **HIGH** | Faithful to decompiled algorithm |

## Pattern note

When a doc presents struct-offset tables, the safest v5 anchor is the **decompilation of the function that writes the field** (the constructor or initializer), not the function that reads it. Readers tend to use derived offsets via Ghidra arithmetic that decompiler typing has since shifted. This doc shows both styles: the algorithm section (read by 0x006ac950/0x006aa4c0) used the read path; the ServerList table used the gs_list_init write path — and the read-path-derived table (qr_t) has more drift than the write-path-derived table (ServerList).

## Status

- Validation date: 2026-05-28
- Doc length: 511 lines
- Anchored addresses: 9
- Wire-format literals byte-confirmed: 5
- Corrections: 3 (gamever literal, timer offset, padding label)
- Clarifications: 2 (SOCKET* narrative, GameSpy-vs-qr_t conflation)
- Open questions: 3
- Sibling cross-anchors: 3 (all hold)
