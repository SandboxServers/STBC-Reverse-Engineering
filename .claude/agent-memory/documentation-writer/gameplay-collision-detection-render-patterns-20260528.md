---
name: gameplay-collision-detection-render-patterns-20260528
description: 8 render patterns for gameplay-foundation #4 collision-detection-system.md — strong-pre-v5 doc with 3 detail corrections (HIGH/MED/LOW severity span) + 2 clarifications + 2 OQs, where narrative was right but labels/comments wrong; cross-anchored to protocol leaf #15 + leaf #13 + gameplay foundation #1
metadata:
  type: feedback
---

# Render patterns — gameplay-foundation #4 collision-detection-system.md

Doc: `docs/gameplay/collision-detection-system.md` (664 → ~860 lines post-render)
Validation memo: `.claude/agent-memory/game-archaeology-specialist/gameplay-foundation-collision-detection-validation-20260528.md`
Status: partial
Pre-v5 → post-v5: 3 detail corrections (1 HIGH, 1 MED, 1 LOW) + 2 clarifications + 2 OQs, ~34 function addresses verified, 15 .rdata constants byte-confirmed, all vtable slot conventions intact.

## P1 — "Narrative right, label wrong" framing for HIGH-severity corrections

When pre-v5 doc has the right *operational behavior* described in prose but a wrong *label* in a table/comment, surface the correction by **leading with what stayed correct**, then explain the label fix:

> "Prior doc's Global Variables table called `DAT_00888B54` a 'large float sentinel' used as an 'infinite distance'. That label is **wrong**. Byte-read at 0x00888B54 returns `00 00 00 00` = **0.0f**.
>
> The narrative text in the Global Variables row was wrong, but the doc's logic descriptions were RIGHT — they just got there by accident: [...]"

This treatment matters because OpenBC implementers reading the prose got the correct behavior even from the pre-v5 doc; the C1 correction is about preventing a future implementer from being confused by the wrong sentinel-name label. Don't shame the prior doc — explain why the prose was actually consistent.

**How to apply:** when a HIGH-severity correction lands on a label/identifier but the rest of the doc accidentally still describes the right behavior, lead with "narrative was right" then fix the label, then explain BOTH semantic uses of the global (here: gap-test threshold AND zero-radius-for-dead) so the OpenBC reader sees the unified 0.0f semantic.

## P2 — MED-severity struct-layout correction as a numbered subsection right at the call site

Sweep-and-prune endpoint struct layout (C2) was wrong in the prior doc — claimed `{ float value, int next_ptr, int object_index }`. Real layout: `{ float value @+0, byte is_min_flag @+4, padding, int object_index @+8 }`. No `next_ptr` exists; sorted array is contiguous.

**Render pattern:** insert a `### C2 — Endpoint Struct Layout (CORRECTED)` subsection IMMEDIATELY after the "How It Works" step that mentions the layout. Don't bury the correction in an appendix — readers visit "How It Works" first and need to encounter the right layout there.

Include in the subsection:
- The corrected layout table (offsets + types + names)
- An explicit "There is no `next_ptr` field" negative-claim line
- A pointer to the asm proof: `*(char*)(iVar9 + 4)` reads the is_min flag

This pattern works for any layout-correction where pre-v5 had a phantom field — it surfaces both the truth and the negative claim.

## P3 — LOW-severity comment-only correction as inline `<-- C3` annotation

When the correction is just one word in a comment (FUN_00436130: "clamp" → "union/expand"), don't burn a whole subsection on it. Instead:

1. Fix the comment in place AND tag it inline: `// EXPAND (union) AABB to include custom bounds at +0x40..+0x54   <-- C3`
2. Add a 3-line explainer block immediately under the code block calling out C3 specifically: "Math was correct (min/max), but the word 'clamp' implies clipping to a constraint, when the actual operation expands the AABB."
3. Tag the correction in the NOTE block at top with its severity classification (`C3 LOW`).

**Why:** LOW-severity corrections shouldn't earn the same visual weight as HIGH ones. Inline annotation + short explainer keeps the doc readable.

## P4 — Clarification as numbered `Clar1`/`Clar2` with dedicated subsection AND in-place mention

The two clarifications (Clar1: dual host/client collision-enabled bytes; Clar2: two "CollisionEvent" entities) each got:

1. **Inline mention** at the relevant section (e.g., the HandlePhysicsCollision code block now reads `// Clar1 — dual collision-enabled byte` in the comment, and the Object Type IDs table footnote mentions Clar2)
2. **Dedicated subsection** with a 2-row or 2-column table that disambiguates the two things

For Clar1 (dual bytes), the table is 2-row keyed on address with columns for Path / Notes. The notes column for the HOST byte calls out that it's network-synced (same as Settings byte 1 in opcode 0x00 per CLAUDE.md). For Clar2 (two CollisionEvent entities), the table is 2-row keyed on # with columns for Entity / Address+class / Role.

**Why:** clarifications aren't corrections — they're net-new content. Readers shouldn't have to hunt for them. Inline mention + dedicated subsection is the right two-layer reveal.

## P5 — Open Questions get the "Promotion path" line at end of each OQ

Each OQ ends with: `**Promotion path**: <how to get from open-question to closed-claim>`.

For OQ1 (caller breadth): "full xref enumeration + call-frequency partition" — names the artifacts a future archaeology agent would need to produce.

For OQ2 (semantic question on which SWIG setter writes which byte): "trace SWIG `SetPlayerCollisionsEnabled` callers through Python boot" — names the trace work.

This pattern was learned from protocol mid #12 (large-catalog sampling) where I committed to always making OQs actionable, not just observational. It pays off when family-close batch work needs to enumerate work-items.

## P6 — Cross-anchored constants get `Cross-anchored from <doc>` note in evidence row

For the 5 damage formula constants (DAT_00893F28, DAT_0088BF28, DAT_008887A8, DAT_00888860, 6000.0f inline) AND the 26.0f host-validation gate (DAT_008955C8), the evidence rows include `note: "Cross-anchored from gameplay foundation #1."` or `note: "Cross-anchored from collision-effect-protocol.md (leaf #15)."`.

**Why:** this tells future re-validators that re-confirming these constants requires checking the anchor doc, not just re-reading the binary. When the anchor doc gets re-validated, this doc's claim is automatically supported.

## P7 — "Pattern Note" subsection for Ghidra decompile artifacts

Added `### Pattern Note — Ghidra Decompile Twin-Call Artifact` under the FUN_005A8810 dispatcher. The pattern: when a dispatcher shows `2N sequential (*vtable+8)(typeID)` calls in decompile, it's actually N type-checks × 2 objects.

This is OpenBC-implementer-facing content — the kind of thing a re-engineer reading similar dispatcher decompiles in OTHER files will hit. Surfacing it as a labeled "Pattern Note" gives the reader a name for the phenomenon.

**How to apply:** when validation surfaces a recurring Ghidra-decompile-artifact pattern in a foundation doc, give it a labeled subsection. Foundations are read by every downstream implementer, so the pattern-name pays off across many subsequent reads.

## P8 — "Key Design Decisions" list updated, not replaced

The pre-v5 doc had a 6-item Key Design Decisions list. v5 added a 7th (dual host/client bytes from Clar1) and updated 2 (collision cooldown timer mentions DAT_0089054C = 1.2f explicitly + cross-link to CLAUDE.md ship+0xEC; client-authoritative detection mentions DAT_008955C8 = 26.0f cross-anchored).

**Pattern:** Key Design Decisions lists are LOAD-BEARING — many readers skim them before reading body. When v5 surfaces a new design-level fact (here: the dual-byte split is a design decision, not just an implementation detail), promote it into the list. Don't replace the existing items just because they could be tightened — that risks orphaning inbound links.

---

## What NOT to do

- Don't reorder the section structure. Pre-v5 doc had Architecture Overview → ProximityManager → Tier 1 → Tier 2 → Tier 3 → Collision Result → Energy Calculation → Call Graph → Globals → Events → Type IDs → Key Decisions. Keep that order; readers may have inbound links to specific sections.
- Don't auto-promote LOW-severity to bold prominence. The C3 "clamp vs union" word fix gets inline `<-- C3` annotation + 3-line explainer, not a full subsection.
- Don't drop the prior call graph just because OQ1 shows more callers. Keep the original graph; add the "(NOTE: 12 callers total — see OQ1)" annotation at the relevant node.
- Don't merge Clar1/Clar2 into the corrections list. Clarifications are NEW content, not fixes; they deserve their own labels (`Clar1`/`Clar2`).
- Don't relabel the existing function names. CheckCollision stays CheckCollision, ProximityManager_Ctor stays ProximityManager_Ctor — the verified content from the prior doc is the spine.

## File outputs

- Edited: `docs/gameplay/collision-detection-system.md`
- NOT touched: `docs/gameplay/v5-validation-status.md` (batched), `.claude/agent-memory/documentation-writer/MEMORY.md` (batched), companion docs (separate workstreams)
