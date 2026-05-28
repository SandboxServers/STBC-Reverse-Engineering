---
name: batched-sibling-render-patterns
description: 8 patterns for rendering TWO sibling docs in a single pass when they share the same Ghidra anchors and the v5 evidence packet is combined; both clear `verified` after small fixes; learned from cf16-precision-analysis.md (leaf #20) + cf16-explosion-encoding.md (leaf #21) rendered as a batch on 2026-05-28
metadata:
  type: feedback
---

# Batched Sibling Render Patterns

Learned from rendering `cf16-precision-analysis.md` (leaf #20) and `cf16-explosion-encoding.md`
(leaf #21) as a single pass on 2026-05-28. The two docs cover overlapping ground (same
algorithm, same constants, same struct, same wire frame), share a single combined evidence
packet from `game-archaeology-specialist`, and both cleared `status: verified` after small
non-load-bearing fixes (1 byte-size correction + 1 xref count refinement + 2 cross-link
clarifications across the pair).

This is the **third pattern in the protocol family** for siblings: leaves #20 and #21 are
both `verified` (after leaves #15 + #16 separately), but unlike them, these two share so
much surface area that doing them in separate passes would have duplicated the entire
evidence packet read. Batching is the right call when:

- The Ghidra anchor set overlaps ≥ 70%.
- Both docs cite the same constants, the same algorithm, and the same wire frame.
- The pre-v5 cross-doc disagreement #N in §4 calls out "doc overlap" as the open item.
- The archaeology specialist's memo explicitly says "validated together" in the description.

## P1 — Single shared evidence packet, two NOTE blocks with category-grouped headlines

The combined memo has a single shared anchor table. Render both NOTE blocks against the
same packet, but the headline of each NOTE describes its OWN doc's fixes only — not the
sibling's. Reader landing on doc #20 doesn't need to know doc #21 had a different
correction; cross-link to the sibling in the body, not in the headline.

Doc #20 headline pattern:
> "1 refinement + 1 clarification. Algorithm, constants, and call-site analysis all byte-confirmed. The xref count is **5 not 4** (extra call site at 0x005a2b3b in an undefined function...). Cross-reference added to leaf #21 ([cf16-explosion-encoding.md](...)) for the `round()` match strategy alongside the `int()` match column."

Doc #21 headline pattern:
> "1 byte-size correction + 1 clarification. CV4 position field is **5 bytes** (3 direction bytes + CF16 magnitude) for the explosion path, **NOT 7 bytes** — the 14-byte total in the same diagram is only consistent with CV4=5..."

## P2 — Shared frontmatter rows + per-doc extras

Both docs get the same 10-row shared anchor block (encoder + decoder + 5 constants + sender
+ receiver + struct ctor). Doc #21 then adds 4 additional rows (CV4 writer + reader + 2
replay-path callers) because they're specific to the explosion wire format. The
archaeology specialist's memo flagged this with an "Additional anchor specific to leaf #21"
sub-table; render exactly that.

Tag convention: `[v5-validated 2026-05-28]` on every algorithm section heading and every
table that was confirmed byte-by-byte. Do NOT tag every paragraph — that's noise.

## P3 — In-context full-render of shared structures with explicit cross-link headers

When two docs share a struct table (e.g., the 0x38-byte ExplosionDamage layout), DON'T
choose one as canonical and link the other. Instead, render the full table in BOTH and add
a cross-link header explicitly naming the sibling as a co-canonical source:

```markdown
> Cross-link: see also [cf16-precision-analysis.md § Explosion Packet](...) for the same struct table rendered alongside the sender/receiver call graph.
```

Reasoning: each doc must be self-sufficient at the reader's chosen entry point. A reader who
landed on the explosion-encoding doc shouldn't have to chase a link to learn the struct
layout. The cross-link tells them the canonical view exists in the sibling; the in-context
render lets them keep reading.

This is the convention that **closes the "doc overlap" §4 disagreement WITHOUT a merge**.
The pre-v5 §4 #8 ("Merge: precision-analysis = algorithm/constants; explosion-encoding =
wire-format + mod ID only") suggested merging; the v5 close annotation explains that
cross-linking is the right answer when both docs cover the same subject from different
angles.

## P4 — Two strategies, two columns, each in its own doc + cross-link

When the same underlying math (e.g., CF16 round-trip) admits two different success
criteria (`int()` truncation vs `round()` to nearest), put each strategy's table in its OWN
doc and cross-link to the sibling for the alternative. Both columns are correct; they
answer different questions.

Doc #20 has the `int() Match` column with FAIL rows. Doc #21 has the `round() Matches`
column with YES/NO rows. A one-line note next to each table directs readers to the sibling
for the other strategy. This is cleaner than putting both columns in one doc (which would
imply one is canonical and the other is a footnote).

Use the Clar1 cross-link pattern:
> "**Clar1 — `int()` vs `round()` match strategies.** The `int() Match` column above truncates toward zero — all four mod values FAIL this test. For the alternative `round(decoded) == original` strategy (which succeeds for 3 of the 4 BC Remastered values), see [cf16-explosion-encoding.md § Precision Analysis](...). Both columns are correct — they answer different questions and the two docs together give mod authors the full picture."

## P5 — Internal-inconsistency correction trumps external-inconsistency

Doc #21's C1 was "CV4 is 5 bytes not ~7 bytes". The signal that pre-v5 was wrong came from
the doc's OWN 14-byte total: `1 + 4 + 7 + 2 + 2 = 16`, not 14. The wire frame total and the
field size were inconsistent WITHIN THE SAME DIAGRAM.

When you see this in a pre-v5 doc, **the total is usually right and the field size is wrong**
(because totals get cited more often and across more docs, so they're more cross-checked).
Render the C1 by:

1. Calling out the internal inconsistency in the NOTE headline: "the 14-byte total in the same diagram is only consistent with CV4=5".
2. A dedicated sub-section (`### C1 — CV4 position field is 5 bytes, not 7`) under the wire-format diagram.
3. The 2-row dispatch table showing the `param_5 != 0` (5-byte) vs `param_5 == 0` (7-byte) paths.
4. A naming-the-caller sentence: "The 5-byte form is selected by `mag_as_cf16=1` on the CV4 write. Other CV4 callers using `mag_as_cf16=0` produce a 7-byte form... see [stream-primitives.md] for the dispatch."
5. The arithmetic line: "The 14-byte total `1 + 4 + 5 + 2 + 2 = 14` is consistent only with CV4=5 bytes."

## P6 — Enumerate the xref table when narrative says "N call sites total"

Doc #20's R1 was "5 call sites not 4" — but the pre-v5 doc said "4 call sites total" with
ONLY 4 bullet-list callers. Replacing the narrative with an enumerated table is the right
call for verified-tier docs:

```markdown
| # | Caller | Site | Field | Notes |
|---|--------|------|-------|-------|
| 1 | DamageableObject__SendExplosions_0x29 (FUN_00595c60) | 0x00595d90 | radius | Opcode 0x29 sender |
| 2 | DamageableObject__SendExplosions_0x29 (FUN_00595c60) | 0x00595da1 | damage | Opcode 0x29 sender |
| 3 | Ship__WriteStateUpdate (FUN_005b1e38) | within sender body | speed | StateUpdate flag 0x10 |
| 4 | CompressedVector3_Write (FUN_006d2b8c) | within writer body | magnitude | CV3 magnitude field |
| 5 | Undefined function near 0x005a2800-0x005a3000 | 0x005a2b3b | speed-like | `[open question — OQ1: function identity]` |
```

Inline-tag the open-question row with `[open question — OQ1: function identity]` so the
reader knows the address is solid but the parent is open. Promote OQ1 to the tracker §4 as a
new row.

## P7 — Batch close in tracker §4 with "addressed via cross-links rather than merge"

When the pre-v5 §4 row suggests a merge and the v5 conclusion is "cross-link instead",
write the closure annotation that way:

> **CLOSED (2026-05-28, leaves #20+#21):** addressed via cross-links rather than merge. Both docs retain the constants table + scale table + algorithm pseudocode for in-context reading (each doc must be self-sufficient at the reader's chosen entry point), but `int()` vs `round()` match strategies are split cleanly — #20 carries the `int() Match` column with FAIL rows; #21 carries the `round() Matches` column with YES/NO rows. Each doc cross-links to the other for the alternative strategy. ExplosionDamage 0x38-byte struct is rendered in both with explicit cross-link headers naming the sibling as the canonical source for the call-graph context. No merge needed — both docs `verified`.

This annotation makes the future docwriter understand WHY there's still overlap and that
the overlap is intentional, not debt.

## P8 — §6 entries are paired but each names the OTHER as batch partner

Both §6 entries (6.20 and 6.21) start with the same disclosure:

> "Rendered as a single batch with leaf #21" / "Rendered as a single batch with leaf #20"

And both list the same shared anchor packet path. Each §6 entry's "Functions touched" table
includes the shared anchors plus doc-specific extras. The "Cross-doc impacts" section lists
the SAME cross-doc impacts (because both docs share them) but is OK to be duplicated —
readers landing on §6.20 don't need to re-read §6.21 to learn the family-close batch.

## What NOT to do (anti-patterns we avoided)

- **Don't render one doc and link the other as canonical.** That creates a "primary +
  secondary" relationship which is wrong when both docs are leaves with their own audience
  entry points.
- **Don't merge** unless the docs genuinely cover the same topic from the same angle. Two
  audience entry points = two docs. The CF16 family has both an "algorithm + precision"
  audience (mod authors choosing weapon IDs, OpenBC implementers picking constants) and an
  "explosion wire format" audience (OpenBC opcode 0x29 implementers, packet trace decoders).
  Different audiences = keep separate.
- **Don't downgrade C1 to LOW severity just because the algorithm is unchanged.** A
  wire-format byte-size error is HIGH severity for OpenBC — an implementer reading the
  pre-v5 "~7 bytes" would produce 16-byte opcode 0x29 packets that no stock client could
  parse. Severity rides on impact-to-clean-room-reimpl, not on whether the algorithm itself
  is right.
- **Don't promote the R1 xref count refinement to a body subsection.** Just replace the
  narrative bullet with an enumerated table and call it out in the NOTE. Refinements that
  don't change algorithm or wire format get inline treatment, not body restructure.

## Tracker bookkeeping (verified-tier shape for batched siblings)

Each §2 row contains:

1. The status flip with date.
2. "Rendered as batch with leaf #N" — names the sibling.
3. Number of corrections + clarifications.
4. A 1-line summary of each fix.
5. A 1-line summary of confirmed byte-by-byte claims.
6. Open questions tracked (OQ1 → §4 #19).
7. The §6.N back-link.

This is shorter than `partial`-tier rows (which need full correction summaries) but longer
than the engine-tracker style (which was 1 line). Verified leaves with batched siblings need
enough text to make the batch context discoverable without reading §6.

## Apply when

- Two sibling leaves cover overlapping subjects.
- The archaeology specialist's combined memo says "validated together".
- The §4 cross-doc disagreement names them as a doc-overlap pair.
- Both docs would clear `verified` after small non-load-bearing fixes.
- The shared anchor packet would otherwise be duplicated across two separate passes.

Don't apply when:
- One doc is partial (e.g., needs body restructure) and the other is verified.
- The shared anchor set is <70% overlap.
- The two docs have materially different audiences (e.g., a reference + a tutorial).
