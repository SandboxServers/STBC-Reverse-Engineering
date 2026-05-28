---
name: protocol-hub-doc-render
description: Render patterns for protocol-family hub/index docs (wire-format-spec.md style). Five patterns: bit-pack-correction NOTE block, DATA-only xref disclosure for handler-registration tables, retired-subsection cross-link pattern, dispatcher-row completeness annotation, layout-table correction with IMPORTANT block.
metadata:
  type: feedback
---

# Protocol Hub Doc Render Patterns

Five render patterns that emerged from rendering `docs/protocol/wire-format-spec.md` (the protocol-family hub) under the v5 standard. Hub docs differ from leaf RE docs: they consolidate summary tables and cross-link aggressively; corrections to a hub cascade to every doc that linked the wrong cell.

## Pattern 1: Bit-pack-correction NOTE

When a wire-format claim is corrected from byte-level to bit-level (e.g., a packet documented as `[byte:X]` is actually `WriteBit(X)`), the correction is **load-bearing for any decoder**. Render pattern:

1. In the summary opcode table, replace the `[byte:X]` notation with `**bit:**X` (bold prefix to flag).
2. Add a dedicated subsection (named e.g. `Settings Packet (opcode 0x00) — Bit-Pack Detail`) immediately after the opcode table.
3. The subsection contains: (a) a pseudocode block showing the exact `WriteByte` / `WriteBit` sequence with the producer's address, (b) one paragraph explaining the bit-packing wrapper's `count_prefix + data_tail` format and the "byte writes flush the bit group" rule, (c) one paragraph explaining why the previous byte-form documentation worked "in practice" (zero-padding) but isn't architecturally correct.
4. Pattern enables: a clean-room decoder writer reads the subsection and gets the bit-stream semantic; a casual reader can stop at the opcode-table summary.

**Why:** Bit-pack errors silently work for clients that happen to read byte-aligned but break for any client that uses the formal bit-stream protocol. Calling this out at hub level prevents the error from propagating to clean-room specs.

**How to apply:** Whenever a sender uses `WriteBit` (FUN_006cf770 in STBC) for fields the doc represents as byte writes, render the dedicated subsection. Pseudocode block must cite the producer function's address inline.

## Pattern 2: DATA-only xref disclosure for handler-registration tables

Handler tables built from a registration call site (e.g., `FUN_0069efe0` in STBC) often contain rows where the registered handler has no Ghidra function entry — it's a `LAB_xxxxxxxx` label reached only via DATA xref from the registration table. Future maintainers will spot-check by calling `get_function_by_address` and get "no function" back, then assume the doc is wrong.

Render pattern: prepend the handler-registration table with a `> [!NOTE]` block that:
- Names the pattern ("DATA-only xref pattern")
- Cites the registration function's address (so the maintainer can decompile it themselves)
- Explains the identity-proof method: `decompile_function(REGISTRATION_FN)` returns N calls of the form `register(&LAB_addr, "Name string")` where each table row is one such call
- Names the precedent case for the project (in STBC: MpgameHandleMessage was previously hidden by the same pattern until the dispatcher recovery sweep)
- States explicitly: "If `get_function_by_address` returns 'no function' for an address below, that is the expected state, not a doc error"

**Why:** Without disclosure, maintainers do drive-by edits removing "broken" rows. The DATA-only pattern is real and common in older binaries.

**How to apply:** Any handler table sourced from a registration-callsite walk gets the NOTE prepended. Other tables (jump-table-based, direct-call-based) don't need it.

## Pattern 3: Retired-subsection cross-link

When a hub doc carries a duplicate table that is canonically owned by a dedicated companion doc, **retire the duplicate but keep its anchor**. Don't just delete the section — replace it with a one-line cross-link, because incoming `#anti-cheat-hash-field-offsets` style anchors from other docs need a landing spot.

Render pattern for a retired table:
1. Keep the section heading and a 1-2 sentence summary of what used to live there.
2. Replace the table itself with a `>` blockquote linking to the canonical doc and naming what it contains.
3. End with a parenthetical noting: "(The duplicate N-row table that previously lived in this doc has been retired in favor of `<canonical>.md` as the single source of truth. Resolves protocol v5-validation-status §4 disagreement #N.)"

**Why:** Provenance preserved (next maintainer can see why the section is thin); incoming links don't 404; canonical authority is named.

**How to apply:** Whenever a hub doc and a leaf doc duplicate the same data table. Always make the leaf canonical (it has the per-row decompile evidence the hub doesn't); the hub keeps the cross-link.

## Pattern 4: Dispatcher-row completeness annotation

Hub docs in the protocol family typically list 3-4 message dispatchers in a row table. Their `analyze_function_completeness` scores vary wildly (the main dispatcher gets attention; sibling dispatchers are sub-baseline). Render pattern:

- Show the completeness score next to the dispatcher's address in the row OR in a paragraph immediately under the table heading.
- For sub-baseline scores (<50), append "Flagged for dedicated v5 pass" as the row note.
- The main dispatcher (which the per-doc validation uses) gets a separate paragraph describing what its current-pass completeness means ("named + plated, two hungarian-violations + three type-quality issues remaining").

**Why:** Surfaces documentation debt without dropping addresses. A future per-doc validation pass picks up the sub-baseline functions; the hub doc records they're known to be undocumented.

**How to apply:** Every dispatcher / handler-registration / opcode-jump-table row in a hub gets a completeness annotation. Don't hide low scores — they're the next sweep's targets.

## Pattern 5: Layout-table correction with IMPORTANT block

When correcting a slot-layout / offset table (not just a row update — a swap or cell replacement that changes how readers compute offsets), render the correction with both inline `*** corrected YYYY-MM-DD ***` markers in the code block AND a `> [!IMPORTANT]` block immediately below.

The IMPORTANT block contains:
- The ground-truth evidence (decompile snippet or switch-case listing with the producer function's address)
- A bullet list mapping each corrected cell: "was X → now Y" with the case-ID that proved it
- A statement of what was correct in the doc (so the next reader sees "the vtable map was right, only the slot map was wrong")
- The cross-doc disagreement number that this correction resolves (links back to the protocol tracker)
- A caveat naming what's still un-ground-truthed (e.g., "the +0x2DC row is held at low confidence because FUN_005b5030 only handles 4 weapon classes")

**Why:** Slot-map corrections cascade — every doc that read the wrong slot now needs to update. The IMPORTANT block (a) tells the next reader what evidence to look at if they doubt the correction, (b) tells subsequent re-validators what was left un-anchored.

**How to apply:** Use whenever swapping cells in an offset / slot / field-layout table. Inline `*** corrected ***` markers alone aren't enough — they don't carry the evidence.

## When this pattern doesn't apply

Pure tutorial or how-to docs don't get these patterns — they're for **reference hub** docs with summary tables and cross-doc authority claims. Leaf RE docs (e.g., collision-effect-protocol.md) use the leaf-doc render patterns instead.
