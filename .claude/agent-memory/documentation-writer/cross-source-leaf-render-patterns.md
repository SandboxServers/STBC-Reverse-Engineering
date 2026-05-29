---
name: cross-source-leaf-render-patterns
description: Render patterns for cross-source / paired-trace differential analysis docs where v5 validation is "promote tags + mark historical sections" rather than fresh address citations. Learned from protocol leaf #22 message-trace-vs-packet-trace.md (FINAL leaf, closed protocol family at 22/22).
metadata:
  type: project
---

# Cross-source leaf render patterns

Learned from `docs/protocol/message-trace-vs-packet-trace.md` — protocol family leaf #22,
the FINAL leaf to validate, closing the protocol family at 22/22. This is a CROSS-SOURCE
DOC (2026-02-10 stock-dedi trace + TGMessage factory deserialize hook) where v5 validation
becomes "promote `[cross-source-YYYY-MM-DD trace]` tags to `[v5-validated YYYY-MM-DD via
<anchor>]`" rather than fresh address derivation. Zero material wire-format corrections; the
shape of the pass is entirely about cascading downstream anchors back into the source.

## When this pattern applies

- Doc is a cross-trace / cross-source analysis (not a primary RE doc)
- Every load-bearing observation has been independently anchored in a per-opcode / per-system
  v5 doc somewhere else in the campaign
- "Current state" sections in the doc describe runtime instrumentation behavior that may
  have changed since the doc was written (proxy decoder bugs, missing features)
- Pass produces: confidence-tag promotions + historical-section marks + label clarifications,
  NOT new wire-format facts

## Eight render patterns

### P1 — Frontmatter cites the ANCHOR doc, not fresh Ghidra cites

For each evidence row, the `address:` field cites the binary address that anchored the claim
IN THE PRIMARY DOC (or `null` if the claim is structural), and a new `anchored_via:` field
names the v5-validated companion doc that did the actual byte-level proof:

```yaml
evidence:
  - claim: "SUB (0x20) flag emitted S->C only; WPN (0x80) flag emitted C->S only"
    address: 0x005B17F0
    function: Ship_WriteStateUpdate
    confidence: high
    anchored_via: docs/protocol/stateupdate.md
    note: "Derives from the friendly-fire + player-count gate inside Ship_WriteStateUpdate."
```

The `anchored_via:` field is the load-bearing one — readers follow it to the primary doc
for the byte proof. This is different from primary-RE evidence rows where the `address:`
field IS the proof.

### P2 — NOTE-block headline counts promotions, historical marks, clarifications

The headline triages the pass by category, not severity:

> **Cross-source doc; 17 claim-promotions + 3 historical-section marks + 1 label
> clarification.** All load-bearing trace observations are now independently anchored in
> validated v5 docs across the protocol family.

Naming the categories (and the count per category) tells the reader this pass is a tag
promotion pass, not a body-rework pass. Distinct from material-correction NOTE blocks
where C1/C2/C3 lead.

### P3 — Inline `[v5-validated YYYY-MM-DD via <anchor>]` tags at each section header

For sections that promote from trace-only to v5-anchored, add an inline tag on the line
immediately after the section header (or above the table when the section IS a table):

```markdown
## StateUpdate Flag Separation: SUB vs WPN

The most critical architectural finding:

[v5-validated 2026-05-28 via mid #8 stateupdate.md]

| Direction | Flags Used | ... |
```

This makes the tag scan-friendly — readers grepping for `[v5-validated 2026-05-28]` find
every promoted section without reading the body.

### P4 — Per-row anchor table below large opcode tables

For multi-opcode tables (like an opcode cross-reference table), don't try to inline a tag
per row — instead, add a "Per-row anchors:" bullet list below the table that groups opcodes
by anchor doc:

```markdown
**Per-row anchors:**
- 0x03 / 0x2A — [v5-validated 2026-05-28 via mid #4 game-opcodes.md (FUN_0069F620 / FUN_006A1E70)]
- 0x07 / 0x08 / 0x09 / 0x0A / 0x0B / 0x11 / 0x1B — [v5-validated 2026-05-28 via mid #4 game-opcodes.md, FUN_0069FDA0 GenericEventForward group]
- 0x15 — [v5-validated 2026-05-28 via leaf #15 collision-effect-protocol.md]
```

Keeps the table itself readable while still grounding every row.

### P5 — `[trace YYYY-MM-DD]` retained for session-specific counts

Session-specific count histograms, timestamp examples, and per-opcode totals stay tagged
with the original trace date:

```markdown
### S->C StateUpdate flag distribution (top 5) [trace 2026-02-10]
```

The structural / algorithmic claim above the table is `[v5-validated]`; the specific count
numbers are `[trace YYYY-MM-DD]`. This disambiguation matters because a future cross-trace
pass may produce different counts on a different session — the structure is durable; the
counts are session-specific.

### P6 — Historical section marks with one-line resolution explanation

For sections that describe "current state" issues now resolved, add a blockquote at the
TOP of the section (BEFORE the prose):

> **Historical (resolved 2026-05-28)** — proxy decoder fragmentation handling is FIXED in
> current `src/proxy/ddraw_main/packet_trace_and_decode.inc.c` lines 1184-1211. ... The
> misdecoded entries below are preserved for trace cross-reference.

Key points:
- One-line headline (`Historical (resolved YYYY-MM-DD)`) — DON'T just delete the section
- One-line explanation naming the source file or doc where the resolution lives
- Final sentence explains why the now-stale content is preserved
- DO preserve the original prose below — it's still useful for trace cross-reference

Three flavors to keep in mind:
- **Resolved (bug fixed)** — naming the fix's source-code location
- **Anchored (per-row links added)** — when "newly identified opcodes" are now indexed in
  dedicated docs; add per-row anchor links inline in the table
- **Resolved (feature shipped)** — when a missing-feature symptom is now implemented

### P7 — Pattern Note section for canonical-example docs

When a cross-source doc demonstrates a reusable RE technique (paired-trace diff, hook-vs-hook
comparison, etc.), add a `## Pattern Note: <Technique Name>` section near the end of the
doc. Structure:

- Name the technique (1 line)
- Name each hook / data source (address + proxy file + what it captures + what it misses)
- Describe what the diff surfaces (bullet list)
- Tag the source session as the "canonical example"
- Recommend when to repeat it (e.g. "when adding new opcodes or new transport types")

This converts a one-off analysis into a reusable methodology entry.

### P8 — Open Questions section structure

For cross-source docs, the OQ structure differs from primary-RE doc OQs:

- OQs reference COMPANION DOCS as the source of the unanswered question (not Ghidra symbols)
- Each OQ explains WHAT'S OPEN, WHY it's open (cross-anchor doesn't resolve it), and the
  resolution path (re-trace bisect / emulate a specific function / etc.)
- Mark each as "Non-blocking" if it doesn't gate the doc clearing `verified` next pass

Example:
```markdown
**OQ2 — 0x0D PythonEvent2 re-emit path.** Doc shows 0x0D C->S=12 with S->C=0. Leaf #14
[pythonevent-wire-format.md](pythonevent-wire-format.md) notes that FUN_0069F880 is
LOCAL-ONLY and handles both 0x06 and 0x0D. Open: do those 12 received 0x0D events re-emit
outbound as opcode 0x06 (which would inflate the S->C 0x06=251 count), or does the engine
drop them after the local apply step? Resolution requires either (a) bisecting the S->C
0x06 stream to find a 12-event burst correlated with the C->S 0x0D arrivals, or
(b) emulating FUN_0069F880 with a 0x0D input. Non-blocking.
```

## Tracker entry shape (§6.N)

For the FINAL doc in a family campaign, the §6.N entry needs extra weight:

- Standard subsections (Status / Methodology / Functions touched / Confirmed claims) plus...
- "Cross-doc anchor reuse" subsection that names EVERY anchor doc + claim count
- A note that this doc CLOSES THE FAMILY at N/N
- A "Cross-doc impacts" subsection naming the family-close batch work (CLAUDE.md, README,
  OpenBC cascade)
- A trailing `## Campaign close summary` section AFTER the §6.N entry that summarizes
  status distribution (verified count / partial count), §4 disagreement resolutions,
  family-close batch follow-ups, and campaign outcomes

The campaign close summary is what a future reader will cite when asked "did the protocol
family pass?" — make it scannable.

## What NOT to do

- DON'T delete historical sections — they remain useful for trace cross-reference
- DON'T introduce new wire-format facts on a cross-source pass — that's a primary-RE doc's
  job; cite the primary doc instead
- DON'T promote session-specific counts to `[v5-validated]` — counts vary by session; only
  algorithmic/structural claims promote
- DON'T forget to update the §1 campaign overview when closing a family — readers landing
  there need to know the campaign is done
- DON'T leave the §4 cross-doc disagreements list with stale rows — add new OQs at the end
  of §4 rather than mutating the table mid-list (preserves §4 numbering for downstream
  references)

## Cross-references

- [leaf cascade render patterns](leaf-cascade-render-patterns.md) — for primary-RE leaves
  with material corrections (different shape than this)
- [first-verified-leaf render patterns](first-verified-leaf-render-patterns.md) — when a
  primary-RE leaf clears `verified` with minor touch-ups
- [verified-leaf-with-cascade render patterns](verified-leaf-with-cascade-render-patterns.md)
  — when a primary-RE leaf clears `verified` despite cascade corrections from companions
- [architectural discovery render patterns](architectural-discovery-render-patterns.md) —
  when a leaf surfaces a MAJOR architectural finding (different shape entirely)
