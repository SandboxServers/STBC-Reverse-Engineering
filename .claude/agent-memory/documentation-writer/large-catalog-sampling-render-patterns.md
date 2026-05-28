---
name: large-catalog-sampling-render-patterns
description: 7 patterns for rendering LARGEST-protocol-doc-class catalog docs (~250 claims, 16 parallel entries) with ZERO material corrections via N=4 sampling strategy; learned from per-ship-subsystem-wire-format.md (protocol mid #12)
metadata:
  type: feedback
---

# Large-catalog sampling render patterns (~250 claims, mid #12)

When v5 validation of a large catalog doc (per-ship, per-opcode, per-class) finds zero
binary contradictions via sampled N=4 verification + extrapolation, the doc render is
shaped by the **sampling strategy** itself, not by corrections.

## Pattern 1: Sampling-strategy headline in NOTE block

The NOTE block leads with **"Zero material corrections"** AND the sampled-ship list with
their cycle/byte totals in bold. This makes the doc's confidence model visible at a glance:

> Four ships sampled byte-by-byte against `reference/scripts/ships/Hardpoints/<name>.py`:
> **Sovereign (49 bytes)**, **Bird of Prey (32)**, **Galor (31)**, **Akira (47)**

Then list the 12 remaining as `confidence: medium` extrapolation. Then list R1/R2/R3 with
**bold tags**. This is the only catalog-render shape where readers need to know upfront
"which rows are byte-anchored vs. pattern-derived".

Used when: doc is large catalog + zero corrections + sampling strategy was applied.

## Pattern 2: Dedicated "Validation Sampling Strategy" subsection (NEW, near top)

A standalone subsection right after Overview that:
1. Names the 4-axes check (structural formula, AddToSet ordering, special-case catalog,
   foundation cross-anchors).
2. Explains *why* the 4 sampled ships were chosen for coverage (large Federation cap, no-Phaser
   non-Fed, no-Tractor Cardassian, reversed-ordering Federation mid).
3. Names the promotion path explicitly: status stays `partial` until byte-by-byte of
   remaining 12; promotes to `verified` after.

This is the discoverable form of the sampling rationale; without it, the per-row
`[confidence: medium]` tags look arbitrary.

## Pattern 3: Summary Table gains a "Validation" column

Add a new column at the end of the Summary Table (after Bridge in this case) holding
either `[v5-validated 2026-05-28]` (for sampled rows) or `[confidence: medium]` (for
extrapolated rows). Keep the column to a single tag — long-form prose belongs in the
per-ship sections.

Distinct from inline-tag patterns used for thin mid-tier docs (where every claim gets
prefix tags). At catalog density, a dedicated column is more readable.

## Pattern 4: Per-section header tagging convention

For per-ship/per-X sections, place the validation tag on the **section header line**:

`### Species 5: Sovereign (Sovereign-class) [v5-validated 2026-05-28]`

vs.

`### Species 7: Vor'cha [confidence: medium — pattern-extrapolated from sampled set]`

Always followed by a `Cross-source:` line naming the source-of-truth file (the hardpoint
.py + line range for sampled ships; just the file name for extrapolated). This makes the
file:line evidence anchor browsable inline at each row of the catalog.

## Pattern 5: Refinement blockquotes inserted at the row they refine

R1 (cycle-byte arithmetic precision) and R2 (post-link definition) are inserted as
`> **R1 — ...**` blockquotes IMMEDIATELY after the table or column header they refine.
Don't push them to a generic "Refinements" section at the bottom — readers need them
where the affected column lives.

R3 (silently-dropped templates) gets its own subsection because it isn't tied to a column
— it's a behavior of the underlying machinery. Use a small table listing example dropped
templates with their citation lines.

## Pattern 6: Hand-computed cycle totals embedded in confirmed sections

For each sampled ship, embed the hand-computation under the per-ship table:

> Hand-computed cycle: `1+1+3+3+5+9+3+11+7+5+1 = 49`.

This reproduces the byte-by-byte verification trail so a future reader (or re-validator)
can replay it. Don't do this for extrapolated rows — only for the sampled ones.

## Pattern 7: Open Questions section near end with promotion-path question

Last open question in the OQ list is ALWAYS:

> Byte-by-byte verification for the remaining N hulls. Currently medium confidence;
> promote to high once verified, then promote the doc to `status: verified`.

This makes the promotion path explicit and queueable. Without it, the doc looks stuck
at `partial` for unclear reasons; with it, the next pass knows exactly what to do.

## Foundation cross-anchor inheritance pattern

When a catalog doc cites foundation addresses (mid #11 slot table, mid #8 round-robin)
that did NOT cascade-break despite foundation corrections, document this explicitly:

> Per-ship doc never cites ship+offset directly (operates in terms of the doubly-linked
> list at ship+0x284), so mid #11 corrections do not cascade.

This protects the catalog from spurious re-validation queue churn when foundations
change. Without the explicit non-cascade statement, future tracker passes have to
re-derive the relationship.
