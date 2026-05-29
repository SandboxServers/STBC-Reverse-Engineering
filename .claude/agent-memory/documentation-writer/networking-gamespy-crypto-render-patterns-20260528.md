---
name: networking-gamespy-crypto-render-patterns-20260528
description: Render patterns for gamespy-crypto-analysis.md v5 partial pass — algorithm rock-solid + 3 corrections in secondary documentation + 2 clarifications about stale Ghidra narrative and struct conflation + 3 OQs including OpenBC-impact OQ3 (gamever 1.6 vs 1.1)
metadata:
  type: project
---

# gamespy-crypto-analysis.md render patterns — 2026-05-28

Networking foundation doc #4 (sibling of alby-rules-cipher-analysis.md and gamespy-discovery.md).
The doc is a "rock-solid algorithm + drift in supporting documentation" v5 pattern: the entire
crypto core (KSA, modified PRGA, base64 char map, secret key value) was byte-confirmed with zero
algorithm corrections, but secondary metadata around it had drifted (struct table offsets, wire
example, stale Ghidra-typing narrative).

## Pattern 1 — "Algorithm rock-solid + secondary drift" NOTE-block headline

When the load-bearing claims of a foundation doc all hold but supporting documentation has 2-4
small corrections, the NOTE-block should explicitly call out **what stayed solid** before listing
what drifted. Open with "**algorithm and crypto core are byte-confirmed rock-solid**" so readers
of the index don't mistake `partial` status for "the crypto might be wrong". Reserve `partial` for
the drift in metadata; the algorithm earns `verified`-level confidence even when the doc is
partial overall.

Format used:
```
> [!NOTE]
> **v5 partial pass — algorithm and crypto core are byte-confirmed rock-solid.** N corrections
> in secondary documentation (...) + M clarifications (...) + K OQs.
>
> **Notable**: <the single most-OpenBC-relevant finding>.
>
> - **C1**: <correction>.
> - **C2**: ...
> - **Clar-1**: <clarification>.
```

## Pattern 2 — OpenBC-impact correction promoted in NOTE-block "Notable" line

For corrections that don't change the algorithm but DO change what bytes go on the wire (e.g.,
the gamever literal `1.6` vs `1.1`), promote the finding to a dedicated "**Notable**" line inside
the NOTE block, BEFORE the per-correction list. This is the signal-to-the-reader that "if you
read only the NOTE, read this one line." Pair it with a dedicated OQ flagged as OpenBC-impact
(OQ3 in this doc).

Pattern shape:
```
> **Notable**: the binary emits gamever `\1.6\` from the literal at `0x0095a668`; the pre-v5
> doc's wire example incorrectly showed `\1.1\`. This may affect OpenBC clean-room compatibility
> with strict-version-filter masterservers — flagged as OQ3.
```

## Pattern 3 — Stale-Ghidra-narrative clarification with margin NOTE block

When a pre-v5 doc walks through Ghidra-typing arithmetic (e.g., "SOCKET* → multiply by 4") to
arrive at a byte offset that is now visible directly as a plain offset in current decompilation,
collapse the narrative to a margin NOTE block. The numeric conclusion was always right; only the
storytelling reflected a Ghidra session that has since reset its typing. Do NOT delete the
explanation entirely — readers may have inbound links to the section. Keep the conclusion in the
body, put the explanation in the NOTE block under a `Clar-N` tag.

Pattern shape:
```
The secret key is at byte offset **`+0x48`** within the qr_t struct.

> [!NOTE]
> **Clar-1**: Earlier revisions of this doc walked through a `SOCKET*`-arithmetic explanation...
> The arithmetic was always correct; the narrative was an artifact of a prior Ghidra session
> whose typing has reset.
```

## Pattern 4 — Struct-conflation Clar with cross-doc pointer

When v5 surfaces that two distinct structs were conflated in a single struct-layout table
(here: qr_t vs GameSpy — both are `param_1` to different functions but were treated as one
type), put a NOTE block ABOVE the table marking which rows are anchored vs SDK-derived, then
add a Clar-N entry explaining the distinction and pointing to the companion doc that owns
the OTHER struct's layout.

Pattern shape (used above the qr_t struct layout table):
```
> [!NOTE]
> **Clar-1 + OQ1**: this validation pass anchored only the `+0x48` secret-key offset directly
> against `qr_send_validate_and_final`'s decompilation. The rows beyond `+0x48` are
> `[unanchored — SDK-derived; OQ1 covers a focused dig]`...
>
> **Clar-2**: the "qr_t" struct and the "GameSpy" struct are **different structs**. Offsets
> like `+0xDC` (server list ptr), `+0xE0` (`GameSpy.serverList`), `+0xED`, `+0xEE` belong to
> the **GameSpy** object, not qr_t. Cross-reference [gamespy-discovery.md] for the GameSpy
> object layout.
```

Then in the table itself, add a `Status` column that distinguishes:
- `[unanchored — SDK-derived]` for plausible rows from external SDK source
- `[unanchored — see OQ1]` for rows that have an open question against them
- `**v5-validated YYYY-MM-DD**` (bold) for the directly anchored rows

This avoids deleting plausibly-correct documentation while marking the confidence
discontinuity clearly.

## Pattern 5 — Bolded-row table corrections with inline C-tag

When a struct-layout table has two corrections (here C2 timer offset, C3 padding label), bold
the corrected rows and append the C-tag in the table cell itself:

```
| **+0x94** | 4 | **Poll/timer struct** (...) | `gs_list_init` (`puVar3[0x25]`) **[C2: was +0x08 pre-v5]** |
| **+0x9C** | 4 | **Mode-side state field** (...) **[C3: was labeled padding pre-v5]** | `SL_master_connect` |
```

Then add a short prose paragraph BELOW the table explaining each correction's source-of-truth.
Don't restructure the table — readers may have inbound links to specific row offsets.

## Pattern 6 — Wire-example correction inline with prose explanation

When a wire-example block has the wrong literal value (here: gamever `1.1` → `1.6`), update
the example AND add a short prose paragraph immediately under it explaining:
1. The correction itself (`1.1` → `1.6`)
2. Why the trailing `\queryid\1.1\` is NOT wrong (it's a format-template tail, not a
   substituted value)
3. The OpenBC implication

The "why the trailing 1.1 is correct" disambiguation is critical when the same digit-string
appears twice in the format string — readers will assume they need to change both unless you
explicitly distinguish.

## Pattern 7 — Cross-anchor sibling section with v5-validated tag

For foundation docs that share addresses with a sibling doc (here: gs_rc4_cipher,
"Nm3aZ9" producer, ServerList +0x2C all also covered in gamespy-discovery.md), include a
dedicated `## Sibling cross-references [v5-validated 2026-05-28]` section listing the
shared anchors with bullet entries. The tag at the section header tells the reader that
THIS validation pass cross-checked against the sibling's validation pass. This prevents
the "well, was this re-verified or just copy-pasted?" question.

## Pattern 8 — Three-OQ format with explicit OpenBC-impact flagging

For 3-OQ docs where the OQs have varying weight, structure them as:
- **OQ1**: Internal-structure-anchoring gap (cite the overlap with sibling doc's OQ if any)
- **OQ2**: Doc-typo-vs-real-variant question (the "is this an artifact or a finding?" OQ)
- **OQ3 (OpenBC-impact)**: The cascade-question, explicitly tagged `(OpenBC-impact)` in the
  heading. Include a "**Flag for clean-room cascade**" sentence so the next family-close
  batch picks it up.

## Frontmatter pattern — 18-row evidence block for foundation crypto doc

The frontmatter ran 18 evidence rows: 9 anchored functions + 6 .rdata literal addresses + 2
struct-correction rows (C2 timer at +0x94, C3 +0x9C state field) + 1 negative claim
(qr_t-rows-beyond-+0x48 not anchored). The negative claim row carries `address: null`,
`confidence: low`, and a `note:` field that explicitly names what was searched and what wasn't
found, per the v5 negative-claim rule.

Pattern note: the `completeness:` field is omitted for rows where the validation pass didn't
run `analyze_function_completeness` — only `gs_validate_encode` (11.3) and `gs_encode_char`
(10.4) got scores from the memo. Don't fabricate scores for rows that weren't measured.

## What NOT to do

- Do NOT mark this `verified` despite the algorithm being rock-solid. The struct-table
  corrections and unanchored qr_t rows are material to OpenBC implementation and need
  resolution before promotion.
- Do NOT delete the qr_t struct layout table. The +0x48 row is verified; the others are
  plausibly-correct SDK-derived data. Delete-and-defer would lose information for future RE.
- Do NOT inline the `Clar-1` SOCKET*-arithmetic explanation in the body prose. It clutters
  the narrative and the conclusion (+0x48) is what matters. Margin NOTE block is the right
  shape.
- Do NOT restructure the body for what is largely metadata drift. Preserve original section
  order — readers may have inbound links from the prior validation.

## Status

- Validation date: 2026-05-28
- Doc length: ~520 lines (was 511 pre-v5)
- Frontmatter evidence rows: 18 (17 positive + 1 negative)
- Corrections: 3 (C1 gamever wire literal, C2 timer slot offset, C3 +0x9C state field)
- Clarifications: 2 (Clar-1 stale SOCKET*-narrative, Clar-2 qr_t/GameSpy struct conflation)
- Open Questions: 3 (OQ1 qr_t unanchored rows, OQ2 doc-typo-or-variant, OQ3 OpenBC-impact)
- Promotion tags: 4 sections tagged `[v5-validated 2026-05-28]` (Algorithm, Wire Format
  Examples, Server List Struct Layout, Sibling cross-references)
- Companion links: 3 (alby-rules-cipher-analysis, gamespy-discovery, network-protocol)
- Tracker NOT modified (batched at end of networking wave)
- Shared MEMORY.md NOT modified (batched at end of networking wave)
