---
name: dispatcher-subordinate-render-patterns
description: Five patterns for rendering small dispatcher-subordinate reference docs (e.g., the NetFile opcode catalog beneath the main MultiplayerGame jump table) when v5 validation flips a doc that contained one structural fabrication and one role-swap. From checksum-opcodes.md render — 2 material corrections in a 35-claim doc.
metadata:
  type: feedback
---

# Dispatcher-Subordinate Render Patterns

Five render patterns from the checksum-opcodes.md v5 render. This shape is a **mid-tier dispatcher** doc — small (a few hundred lines), covers one switch table, lives under a foundation hub (wire-format-spec.md, transport-layer.md). Different from a full opcode catalog (game-opcodes.md is ~140 claims with subcatalogs) and different from a leaf wire-format doc (one opcode deep dive). The render task involves a NOTE-block headline of the two material corrections, a missing-handler negative-claim table, and a careful preservation of a wire fact whose binary sender is unlocated.

## Pattern 1: Two-correction headline in the NOTE block

When validation surfaces TWO material corrections (a role-swap + a structural fabrication), surface BOTH in the top NOTE block, each tagged with its short code (C1, C2). Both must be discoverable on first read — a clean-room implementer can otherwise apply only one of two corrections.

Render pattern:
- Single `> [!NOTE]` block at the top, status: partial.
- Sentence 1: dispatcher catalog (opcode set, what's missing).
- Sentence 2: "Two material corrections from the pre-v5 doc:" with (C1) and (C2) inline, each ~one sentence.
- Sentence 3 (if applicable): wire-vs-binary tension — the observation exists on the wire but the binary path is unlocated. This is the open-question seed.
- Final sentence: cross-link to v5-evidence-header.md.

**Why:** A single corrigendum is easy. Two material corrections in one doc creates a "did I see both?" problem — make them both visible at the entrance so a reader doesn't miss one and propagate it. Tagging C1 / C2 lets the body cross-reference back.

**How to apply:** Whenever a single validation pass yields >= 2 material corrections (role-swap, fabricated structure, dropped element, etc.). The C1/C2/... tags appear in the NOTE block AND inline in the body sections where each correction lands.

## Pattern 2: Missing-handler table (the negative-claim catalog)

When a dispatcher's switch is non-contiguous, the v5 standard requires every negative claim ("no handler for 0x24") to have evidence. Render the missing-handler set as its own small table, with one row per missing opcode and a reason column.

Render pattern:
- Below the dispatcher-address citation, a 3-column table: `Opcode | Why it's missing | (Other notes)`.
- Each row says ONE of: "No handler. No sender located in the binary." (dead opcode), "No receive case. Outbound only — sent by FUN_xxxx." (outbound-only opcode), or "Reserved branch — see open question OQ#." (reserved-but-unanchored).
- The negative claim is anchored in the doc's evidence-row frontmatter — the body table makes the catalog scannable.

**Why:** A reader scanning the opcode table sees gaps and asks "is 0x24 documented elsewhere or is it dead?" A dedicated missing-handler subtable answers the question once, definitively, with the evidence behind it. Without this, the gap is ambiguous.

**How to apply:** Any dispatcher reference doc where the switch is non-contiguous. The table goes immediately below the dispatcher-address citation, before the main opcode catalog.

## Pattern 3: Wire-observed but binary-unlocated subsection

When a real wire observation exists (packet trace shows the message) but the in-binary sender is not located by static call-graph analysis, the v5 doc must NOT drop the observation — but it also must NOT pretend the binary anchors it. Render this as a dedicated "X on the wire" subsection that calls out the open question.

Render pattern:
- Subsection title names the phenomenon as a wire fact: "Round 0xFF on the wire (open question)" or "Event 0xNNNN on the wire (open question)".
- First paragraph: state the wire fact with the trace-doc citation tagged `[cross-source-YYYY-MM-DD <trace-doc>]`.
- Second paragraph: state the binary search exhaustively — what was searched (callers of FUN_X, references to constant Y) and what was NOT found.
- Third paragraph: list candidate code paths that might contain the sender + name the open question (OQ#).
- Fourth paragraph: a single load-bearing sentence — "Until OQ# resolves, this doc's status stays partial. Trace evidence is authoritative for the wire fact."

**Why:** This is the v5 standard's hardest case — a fact that's true on the wire but unanchored in the binary. The pattern keeps the wire fact visible (necessary for clean-room implementation), discloses the gap (necessary for evidence-standard integrity), and preserves the doc's promotion path (resolving the OQ flips status to verified).

**How to apply:** Any time packet-trace evidence shows a behavior that the in-binary code path doesn't account for. The subsection sits inline with the related opcode, not buried at the bottom. The OQ # is also listed in the dedicated "Open questions" section at the doc's end.

## Pattern 4: IMPORTANT block on the role-swap section

When a role-swap correction (C1: opcode A and opcode B had their roles swapped in the prior doc) lands on a specific opcode section, mark that section with an `> [!IMPORTANT]` block — not just a generic NOTE.

Render pattern:
- The opcode A section opens with the new, correct mapping in prose.
- A bullet-or-paragraph cite of the decompile evidence (e.g., "FUN_006A4C10 reads opcode into iVar2 and compares `(char)iVar2 == '\"'` (0x22)").
- At the bottom of the opcode A section: `> [!IMPORTANT]` block. One sentence: "Cm from this validation pass: prior doc had this opcode mapped to the X dialog. The binary disagrees — A displays Y. Any clean-room implementation needs the corrected mapping. See also [opcode B](...)."
- The cross-link to the paired opcode (B) is essential — readers landing on either A or B should be guided to confirm the swap.

**Why:** Role-swaps are the easiest correction to under-disclose because the prose flows naturally with whichever mapping the author types. A reader scanning for "what's different from before" needs the explicit "this was swapped" callout. The `IMPORTANT` color is louder than `NOTE` and matches the load-bearing nature of "you'd ship the wrong dialog otherwise".

**How to apply:** Any per-section correction where the prior doc had an inverted mapping. Use IMPORTANT, not NOTE — NOTE is for framing; IMPORTANT is for "this would break a clean-room implementation if missed".

## Pattern 5: Open questions as a numbered section, OQ# tags inline

When the validation pass leaves N open questions and the doc's promotion path depends on resolving them, render the OQs as a dedicated section near the doc's end (before Cross-references), with explicit OQ# numbering. Body text that hits an OQ inline references it by number.

Render pattern:
- `## Open questions` section title.
- Numbered list, one per OQ. Each: `**OQ# — short title.**` followed by the binary state, the wire/trace state if applicable, candidate resolutions, and (if the OQ blocks status promotion) the explicit "Until this resolves, the doc cannot promote to verified" note.
- Inline body references read like "...tracked as open question OQ1" or "see [Round 0xFF on the wire](#round-0xff-on-the-wire-open-question)".
- The tracker row (in v5-validation-status.md §6.N) also enumerates the OQs and explicitly states "Resolving OQ# promotes this doc from partial -> verified."

**Why:** Without a dedicated section, OQs scatter through the doc body and the promotion path isn't visible — the next maintainer can't easily see "what would close this out". The OQ# tags give bidirectional reference (body text -> open-questions list, open-questions list -> body anchor).

**How to apply:** Any v5 doc that ends in `partial` status because of specific open questions (rather than because of pending refinement work). Number the OQs. Cross-reference them inline. Mirror the list in the tracker row.

## When this pattern doesn't apply

A doc with 0 corrections is the [[opcode-catalog-render-patterns]] case — clean-validation precedent. A doc with multi-section structural changes (e.g., when a foundation doc's class identity flips and cascades) is the [[foundation-doc-class-identity-inversion]] case. These patterns are specifically for **small dispatcher-subordinate docs** where the binary work surfaces (a) a role-swap, (b) a structural fabrication, AND (c) a wire-binary tension that survives the pass as an open question.
