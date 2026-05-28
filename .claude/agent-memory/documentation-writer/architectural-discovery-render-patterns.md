---
name: architectural-discovery-render-patterns
description: 9 patterns for rendering a leaf doc where v5 surfaces a MAJOR architectural discovery (e.g., a second class registry) that closes a foundation-level OQ and creates load-bearing anchor material for the entire family
metadata:
  type: feedback
---

# Architectural-discovery leaf render patterns

Learned from `delete-player-ui-wire-format.md` (protocol leaf #17, third protocol-family doc validated as a leaf). The validation surfaced a MAJOR finding — stbc.exe has TWO class registries (NiRTTI + TGFactory) — that closes a long-standing wire-format-spec foundation-level open question (OQ #2). The doc had 3 corrections + 4 clarifications but the headline is the registry discovery, not the per-byte changes.

## When this shape applies

- A leaf v5 pass surfaces an architectural fact that wasn't in any prior doc
- The fact CLOSES a foundation-doc open question (cross-family load-bearing)
- The doc has ordinary corrections (C1/C2/C3) on top, but they're secondary
- Doc status lands `partial` (not `verified`) because the architectural discovery has open enumeration debt downstream

## The 9 patterns

### Pattern 1: NOTE-block leads with architectural discovery, NOT corrections

Standard partial-status NOTE block opens with the discovery in **bold**, THEN lists corrections in (C1)/(C2)/(C3) form. Example:

> **MAJOR ARCHITECTURAL DISCOVERY this pass: stbc.exe has TWO independent class registries** — [...details...]. Three corrections: **(C1)** [...]. **(C2)** [...]. **(C3)** [...]. Plus 4 clarifications including [...].

Rule: the OQ closure is more cross-doc-impactful than per-byte corrections. Lead with it.

### Pattern 2: Dedicated `## Two-Registry Architecture` section as the second `##`

Right after Overview, before Wire Format. Carries an `> [!IMPORTANT]` block: "This section is the load-bearing resolution for [wire-format-spec OQ #2] and is shared anchor material for every protocol doc that references factory IDs in the [...] range."

This is the citable section — downstream docs will link here when they encounter a factory ID outside the NiRTTI catalog.

### Pattern 3: Registry comparison table — 4 columns (Registry / Backing table / Registered via / Class IDs (catalog) / Used by)

Side-by-side, NiRTTI vs TGFactory. Each row gives a developer enough to identify which registry a given class belongs to without re-doing the search.

### Pattern 4: Cluster sub-table for siblings

The 0x86x cluster — 0x865 / 0x866 / 0x867 — gets its own sub-table (Class ID / Vtable / Size / Use). 0x866 is the only well-understood entry; 0x865 and 0x867 are "Unknown — sibling" with explicit promotion to Open Questions. This honors the rule: don't claim what you didn't verify.

### Pattern 5: Per-byte sender-side sourcing table even when wire format is unchanged

Even though 0 byte-level changes, render the per-byte sender source table with [v5-validated YYYY-MM-DD] tag. Each row names: address that writes the byte, vtable slot used, source struct field. This locks the wire format against future drift even though THIS pass didn't change it.

### Pattern 6: Dedicated "Critical correction: FUN_X sends opcode Y, NOT Z" subsection

When C1 is an attribution-flip (function attributed to wrong opcode), give it a dedicated `### Critical correction:` subsection inside Handler Chain. Includes:
- The wrong attribution (pre-v5 statement quoted)
- Disasm bytes showing the actual opcode (e.g., `C6 44 24 48 18` for `MOV byte, 0x18`)
- A consequence table: "This means [...] reach the wire via different mechanisms" — 0x17 / 0x18 / 0x14 each listed with their actual sender

This is the highest-impact correction format because the prior wrong claim is in CLAUDE.md downstream notes and the cross-doc impacts are listed in a closing paragraph.

### Pattern 7: NewPlayerInGameHandler-style name-collision subsection

When two distinct binary addresses register under the same SWIG name string, give it a dedicated `### NewPlayerInGameHandler name collision` subsection (or whatever the colliding name is). 2-row table:
- Address / Type in DB (function vs LAB_) / Role / When it runs

Cite the registration call site that proves the collision (e.g., `FUN_0069efe0` calls `FUN_006da130(&LAB_X, s_SameName)`).

Cross-link to the systemic pattern (leaves #13/#14/#15/#16 already documented the SWIG-callback-vs-function pattern).

### Pattern 8: "Stock trace #N byte-by-byte decode" gets the [v5-validated] tag inline

Even for a packet documented pre-v5, re-tag the decode lines with `[v5-validated YYYY-MM-DD]` after re-verification. This locks the per-byte interpretation in case downstream readers think the OLD decode is what stands.

For decoded fields where the semantic CHANGED (this case: `dst_obj_id` was "ship object ID", now is "TGWinsockNetwork singleton handle"), the decode line carries the corrected interpretation **with bolded emphasis** on what changed.

### Pattern 9: Cross-doc impacts section names the family-close batch

End of doc has `## Open Questions` (always); the tracker §6.N has a dedicated "Cross-doc impacts (no in-this-pass modifications; batched)" subsection. Lists:
- The closed OQ in the foundation doc
- Every companion doc that needs a one-line update at family close
- Every "should cross-link to this section as the canonical source" item

Pattern: do NOT modify companion docs in this pass. Surface the work as batched-at-family-close.

## Frontmatter signals when this shape applies

- `status: partial` (architectural-discovery docs don't reach `verified` because enumeration debt is real)
- Evidence row count ~15 (medium — enough to anchor the discovery but most claims are positive identifications, not corrections)
- One negative-claim evidence row for the "always 0" field (src_obj_id), one for the "always" S->C authority
- `supersedes:` with the prior validation date
- `companions:` always includes the foundation doc that owned the closed OQ

## What NOT to do

- Don't lead the NOTE block with corrections — the architectural finding is the headline
- Don't put the registry comparison table in an appendix — it's the load-bearing section, put it second
- Don't try to enumerate the full TGFactory registry in the same pass — flag it as Open Question, surface to next leaf
- Don't modify companion docs to reflect the OQ closure — batch at family close
- Don't downgrade the LAB_ entries to `confidence: medium` because they have no fn body — the address + disasm IS the evidence

## Tracker §6.N row shape for architectural-discovery validations

The row leads with "**Headline finding:**" instead of jumping to methodology. Order:
1. Status line + "third protocol leaf" / "doesn't clear verified because [reason]"
2. **Headline finding:** dedicated 1-paragraph callout of the architectural discovery + cross-doc closure
3. Standard sections: Methodology / Functions touched / Wire-format CONFIRMATION / Three corrections / Four clarifications / Non-corrections / Cross-doc anchor reuse / Cross-doc impacts (batched) / Open questions / Verification methods / Files touched / Header inputs
4. The "Cross-doc impacts" section is what makes this pattern distinct — it lists family-close work explicitly so the close-batch agent doesn't miss it

## §4 cross-doc disagreement closure format

When this pass closes a §4 disagreement, the row is rewritten as:

> **CLOSED (YYYY-MM-DD, leaf #N):** [resolution one-liner naming the binary truth]. [Confirmed siblings if applicable]. [Deferred work if applicable]. See [leaf doc].[section name].

The §4 row is NOT deleted — it's preserved with the closure annotation so future passes can see the resolution trail.
