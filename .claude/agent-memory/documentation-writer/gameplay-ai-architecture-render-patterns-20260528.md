---
name: gameplay-ai-architecture-render-patterns-20260528
description: Render patterns for THIRD doc to clear `verified` (after alby-rules-cipher-analysis + ack-outbox-deadlock) and FIRST verified doc of the gameplay family. ZERO material corrections + 2 Clar + 1 OQ — distinct shape from prior verified docs because clarifications touch interpretation (vtable slot framing) not wire format. 8 patterns documented.
metadata:
  type: project
---

# Render Patterns — Gameplay AI Architecture (verified-with-clarifications shape)

Source: `docs/gameplay/ai-architecture.md` rendered 2026-05-28. This is the FIRST verified gameplay-family doc and the THIRD doc total to clear `verified` (siblings: networking alby-rules-cipher-analysis, networking ack-outbox-deadlock).

The verdict shape here is distinct from the prior two verified docs:
- alby-rules-cipher-analysis: verified + 2 algorithmic Clar + 2 R (refinements)
- ack-outbox-deadlock: verified (clean, no clarifications)
- **ai-architecture: verified + 2 framing Clar + 1 OQ** — the clarifications affect how a reader interprets the vtable layout and enum, not the algorithm or wire format. Distinct enough to warrant its own pattern set.

## Pattern 1 — NOTE-block triple-headline for ZERO/2/1 (corrections/clarifications/OQ)

The NOTE block must lead with bolded **ZERO material corrections** so the reader knows up front that nothing about the runtime contract changed. Then list Clar1/Clar2 inline (with their one-line subjects) and the 1 OQ — so the reader can decide whether the verified status applies to their interest area.

```
> **v5 verified pass — ZERO material corrections.** All 8 vtable addresses verified via
> 3-DATA-xref pattern; all 8 constructors verified... 2 clarifications (Clar1 vtable slot
> numbering starts at byte offset +0x20; Clar2 UpdateStatus enum has 5 SWIG names...).
> 1 OQ on internal base class identity.
```

Diff from "verified + clean" (ack-outbox-deadlock): there the NOTE is a single sentence. When there are Clar/OQ items, enumerate them in the NOTE so they are not surprises to a reader scrolling past §1.

## Pattern 2 — Clarification as in-section content, not appendix

Both Clar1 and Clar2 in this doc are rendered INLINE inside §2 (Virtual Method Table), each as a `### Clar1 — ...` and `### Clar2 — ...` subsection. They are not at the bottom of the doc.

Why: the clarifications affect the SECTION they sit in. Putting them in an appendix would force the reader to mentally swap them in. Keeping them inline means the §2 content is correct as-read.

Compare to alby-rules-cipher-analysis where Clar-1 and Clar-2 are in the NOTE block at the top (because they affect the entire doc's framing — the cipher algorithm). When the clarification is scoped to one section, put it in that section.

## Pattern 3 — Byte-offset table replaces ordinal-slot table

Original doc said "Slot 0..5" for SetActive..IsDormant. v5 found these are at byte offsets +0x20..+0x34 (slots 8-13). The replacement table is a 4-column "byte offset / slot # / method / default impl" structure. This:
- Shows the offset (what you index to from the vtable pointer)
- Shows the slot # (what some readers want)
- Shows the method (semantic identity)
- Shows the default impl address (what code actually runs if not overridden)

Including all four columns avoids requiring readers to do mental math.

Place the offset table BEFORE the semantic table (`### Method semantics`). Layout first, semantics second. Readers cross-referencing Ghidra need the layout up top.

## Pattern 4 — Enum table cites string addresses, not just values

When v5 finds new enum values via SWIG strings (not via code), the table cites the string address — not just the integer value. This:
- Documents WHERE the evidence came from (SWIG strings in .rdata)
- Lets a re-validator re-anchor in 6 months without re-running the search
- Distinguishes "value asserted from binary string" from "value asserted from default return"

Example: `US_INVALID = 3 (string @ 0x009508c2)` — and the value 3 is corroborated by `MOV EAX, 3` in the default Update at 0x00470740. Two independent anchors.

## Pattern 5 — Cross-link bare-event-IDs to engine docs

`ProcessAITick` posts event `0x800017` on US_DONE. The doc says so AND links to `docs/engine/event-system-architecture.md` with a parenthetical "(ET_DONE — see ...)". This lets readers chase the event constant without forcing them to grep.

Generalize: any time a doc cites an event ID, callback constant, or factory ID, link to the catalog doc. Engine docs catalog these; subsystem docs cite them.

## Pattern 6 — OQ rendered as a section with a table, not a list item

OQ1 here is "what is the internal base class providing slots 0-7?" — the evidence is a table of 8 addresses, one slot's verified behavior (hashtable-insert at +0x14), and 4 supporting globals (`DAT_009816a0`, etc.).

The OQ section is rendered as `## Open Questions` near the bottom of the doc (after §12, before "Related Documents"). OQ1 has its own subsection with:
- The question stated up front
- The evidence table (slot offsets + targets + notes)
- A "not load-bearing" disclaimer so readers know they can ignore it

Diff from minor OQs (one-liner promotion-path questions seen in protocol-family leaves): when the OQ carries data (an evidence table, hypothesis pointers), give it a section. When it's a 1-sentence "should this be confirmed in trace?" question, an inline blockquote suffices.

## Pattern 7 — Inheritance-chain ctor disclosure paragraph

In §1 (Class Hierarchy), the chain is verified via ctor decompilation:
- `PlainAI ctor` calls `BaseAI ctor` first
- `BuilderAI ctor` calls `PreprocessingAI ctor` first

These 4 sentences (one per chain link) prove the inheritance tree from the binary side. Without them, the ASCII tree at the top of §1 is unverified.

Rule: when a doc shows a class hierarchy diagram, the body should name the ctor evidence for each non-root link. Even one or two sentences suffice.

## Pattern 8 — Negative claims with explicit "sampled" list

The "no PlainAI script names in C++" claim is supported by a sampled list: `BasicAttack, FedAttack, InaccurateTorps, SetCircleSpeed, g_lFlagThresholds, FlagThreshold` — all searched, all absent. This naming-of-samples is what makes the negative claim trustworthy.

Render this in the evidence row's `note:` field, then again inline in the body section that asserts the negative ("None of these 27 script names appear as binary strings..."). The repetition is intentional — the frontmatter is the citation, the body is the readable claim.

## Cross-cutting

- Tagged 7 sections with `[v5-validated 2026-05-28]` (§1 §2 §3 §4 §4-Save/Load §10 §11) — every section whose claims were directly verified by the memo.
- Did NOT tag §5-§9 because those are Python-side catalogs (PlainAI scripts, Compound, Fleet, Player, Conditions) — v5 confirmed them indirectly via negative claim (no strings in binary). The negative claim is tagged in §5; the catalogs themselves are Python-evidence not binary-evidence.
- 33 frontmatter evidence rows + 1 negative-claim row = 34 total.
- Companions list expanded from 5 → 7 (added event-system-architecture + rtti-class-catalog).

## Verified-shape comparison table

| Doc | Corrections | Clar | OQ | Distinct shape feature |
|-----|-------------|------|----|--------------------------|
| alby-rules-cipher-analysis | 0 | 2 algorithmic | 0 | Clarifications in NOTE (doc-wide scope) |
| ack-outbox-deadlock | 0 | 0 | 0 | Clean — single-sentence NOTE |
| ai-architecture | 0 | 2 framing | 1 | Clarifications in section (local scope); OQ has its own section with evidence table |

Rule of thumb: NOTE-block enumeration scales with Clar+OQ count. ≤1 → single sentence. 2-3 → enumerated inline. 4+ → break out to a triage subsection.
