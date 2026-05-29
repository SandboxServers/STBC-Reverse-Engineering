---
name: networking-multiplayer-flow-render-patterns-20260528
description: Render patterns from v5 pass on docs/networking/multiplayer-flow.md (networking mid #7, 5-phase join-flow narrative doc, 3 corrections + 4 clarifications + 2 historical sections + 2 OQs)
metadata:
  type: project
---

# Render patterns — `multiplayer-flow.md` v5 pass

Networking mid #7. Pre-v5 doc was 188 lines, 5-phase narrative with timing table, key-functions table, failure-points list. This doc was the FIRST networking-family doc that combined a multi-phase narrative + key-functions reference + cross-doc inherited-error flag (off-by-4 in ui-class-hierarchy.md). Patterns below cover render shapes specific to that mix.

## Patterns

### P1 — Cross-doc inherited-error flag in NOTE block
When a correction has a *known upstream source* (e.g., `+0x74` slot offset inherited from ui-class-hierarchy.md), the NOTE block names BOTH the local correction AND the upstream doc. Example:
> "Critical: player slot table is at MpgameBase+0x78 (not +0x74 — **note `docs/engine/ui-class-hierarchy.md` ALSO has this off-by-4 inheritance**)"

Then in the C1 in-body NOTE, add an explicit "Source of inherited error" bullet listing the upstream doc and flagging it for family-close engine sweep. This avoids the trap where a downstream doc gets corrected but the upstream source keeps re-propagating the wrong value into future docs.

### P2 — PlayWindow-vs-TopWindow disambiguation references companion doc
When v5 flips a global-pointer identity (DAT_0097e238 = PlayWindow not TopWindow), put the C-correction inline at the section that names the symbol, with a one-line cross-link to the canonical disambiguation doc (`docs/engine/ui-class-hierarchy.md`). Don't re-explain the full PlayWindow/TopWindow split — just delegate. Also note in the NOTE that "the same function uses BOTH" to make clear why a reader could have confused them.

### P3 — Bug-premise correction triple (NOTE + dedicated subsection + historical mark)
C3 ("client does NOT silently drop") is a bug-premise correction — the prior doc's diagnosis was wrong, not just imprecise. Render in three places:
1. NOTE-block headline names the correction
2. Dedicated subsection (`#### C3 — Client does not silently drop...`) shows the binary truth with all 4 wire writes
3. Historical mark in the "Potential Failure Points" section (H2) saying "previously characterized as X; that premise is wrong per C3" with cross-link

The triple gives readers three entry points (top-of-doc skim, body study, failure-points lookup) without duplicating the binary detail.

### P4 — Bit-packed-vs-byte-aligned clarification with stream-primitives cross-link
For wire-format clarifications where the bytes-on-wire are unchanged but the encoding mechanism is misunderstood (Clar2: WriteBool_Bit not WriteByte), don't change the byte layout description — instead add a dedicated Clar subsection that:
1. States the prior annotation
2. Names the binary truth (WriteBool_Bit, 1 bit each)
3. Adds a "packets remain byte-aligned overall because TGBufferStream's bit accumulator flushes between writes" reassurance
4. Cross-links to `docs/protocol/stream-primitives.md` for bit-packing semantics

The reassurance line is critical — readers who care about the wire byte layout shouldn't panic. The semantic clarification matters for OpenBC implementors who'd otherwise allocate 3 bytes instead of bit-packing into 1.

### P5 — Historical section with cross-link to "What Works" CLAUDE.md state
H1 (bc-flag bug timing) marks the broken-column of the timing table as historical. Render shape:
1. Inline note under the timing table: '> The "Our Server (Broken)" column reflects the H1 bc-flag bug — kept here for reference against historical log archives.'
2. NOTE-block inside Phase 5 (where the resolution lives) saying "RESOLVED per CLAUDE.md 'What Works'" with the new binary-confirmed approach

Keep the historical column in the table — don't delete it. Operators reading old log archives need to be able to look up "T+13.0s for InitNetwork" and find it documented.

### P6 — Key-Offsets-Verified-Live table as dedicated section
Foundation docs anchor offsets in evidence rows. Mid-tier narrative docs benefit from a dedicated `## Key offsets verified live (Ghidra MCP, YYYY-MM-DD)` section listing every offset cited in the narrative with its source function. Placement: AFTER Phase N narrative, BEFORE Failure Points and Open Questions. Three columns: Offset / Field / Source function. Include offsets the narrative *implies* but doesn't directly cite (e.g., MpgameBase+0x70, +0x74 gap field) so future RE work has a known-good anchor list.

### P7 — Open Questions section with anchored-vs-unanchored disambiguation
Both OQs in this doc had specific addresses but were "not anchored" (no documented function role). Render:
- **OQ1**: address range (`0x006b89a0 – 0x006b89dd, ~62 bytes`), what it's called from, why it matters (the C3 transport path)
- **OQ2**: the offset (`+0x8a`), the observed behavior (zeroes addr, forces port 0x5655), and the candidate semantic ("Possibly the dedicated-server flag — would explain why headless servers always take the host path")

For OQs that have *concrete suspect semantics*, name the suspect explicitly so the next pass can confirm or refute.

### P8 — Phase-tagging for promotion vs Phase-section tag for newly anchored
Promotion tags `[v5-validated YYYY-MM-DD via <doc>]` go on phases that cross-link to an already-validated companion. Phase 5 ("newly anchored this pass — WSN+0x2C / WSN+0x30 confirmed via FUN_006b5c90") gets `[v5-validated 2026-05-28]` WITHOUT an "via" doc — the validation came from a foundation function (FUN_006b5c90 in network-protocol.md) that didn't need a separate doc citation.

Distinguish:
- `[v5-validated 2026-05-28 via docs/protocol/checksum-opcodes.md]` — content was anchored in a sibling doc
- `[v5-validated 2026-05-28]` — content was newly anchored in this pass (or anchored against a foundation doc that's the same one cited in companions:)

### P9 — Evidence-row count for narrative docs
This doc has 27 evidence rows — higher than typical mid-tier (12-18) because:
- 16 function addresses (key-functions table)
- 3 event IDs (0x008000e6/e7/e8)
- 8 offset/field claims that span multiple functions

When a narrative doc has a structured reference table (key-functions), include each entry as an evidence row even if it has the same address as a flow-step row — readers may grep frontmatter for a specific address.

### P10 — Confidence cascade for cited-but-unvalidated functions
FUN_0071f270 and FUN_007202e0 are cited at multiple call sites but not validated independently this pass. Render: `confidence: medium` with `note: "Not validated independently this pass; cited at call sites"`. This honors the v5 "cite or it didn't happen" rule without dropping the function from the doc.
