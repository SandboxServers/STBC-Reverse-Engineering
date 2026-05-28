---
name: python-messages-render-patterns
description: 6 patterns from rendering a "cleanest pre-v5" mid-tier doc — one material correction + two name cascades + cross-source + python-source tags. SWIG-wrapper cross-reference table is the load-bearing new section that consolidates scattered wrapper info.
metadata:
  type: feedback
---

# Patterns from python-messages.md v5 render

Lowest-correction pass of the protocol family so far (just 1 material correction + 2 naming corrections + 4 tags). Six patterns surfaced that are reusable when a mid-tier reference doc was already well-anchored but needs class-cascade + provenance tagging.

## Pattern 1 — Three-tag triage in the NOTE block

When the validation pass surfaces three different tag classes (binary-corrected, cross-source-trace, python-source), the NOTE block opens with what is binary-validated, then closes with two short sentences naming the cross-source and python-source tags. Reader gets the trust hierarchy before scrolling.

Why: a single "see the standard" line buries the three classes; explicit enumeration sets expectations that the doc body uses *three* different colored-tag annotations (`[v5-validated]`, `[cross-source-YYYY-MM-DD]`, `[python-source]`).

How to apply: any mid-tier doc whose claims split across binary + trace + script corpora needs the NOTE block to surface that split up front.

## Pattern 2 — SWIG wrapper → real function consolidation table

If a doc covers SWIG-exposed C++ API (Send / Create / Set / Get methods), pre-v5 docs typically scatter the wrapper / format-string / real-function triplets across the prose. v5 render adds a dedicated "SWIG wrapper → real function cross-reference" table that lists all wrappers in one place: wrapper address, format-string + address, real function name + address, one-line note.

Why: clean-room implementers need a single sheet of the SWIG API surface; otherwise they have to grep the doc for `0x005e3...`. Consolidating into one table is the load-bearing addition for usability — even when nothing about the API changed.

How to apply: any reference doc with 3+ SWIG wrappers. Lift them into a table near the implementation pattern that uses them.

## Pattern 3 — Length-prefix correction needs an explicit "stock code does not use this" line

The WriteCString length-prefix correction (uint16 → uint32) sounds material — and it IS material for clean-room implementers — but the stock BC mod code never invokes WriteCString. The IMPORTANT block has to explicitly state both: (a) the correction matters for clean-room, and (b) it does NOT invalidate any stock-trace observation because the stock code uses an explicit `WriteShort + Write` pattern instead.

Why: without the second sentence, a reader will assume every observed CHAT_MESSAGE in stock traces had a 4-byte length prefix that the prior doc misread as 2 — wrong. The byte-by-byte CHAT_MESSAGE example shows `05 00` (uint16), which is binary-correct because the script wrote `WriteShort + Write` explicitly.

How to apply: any width / format correction where the binary primitive disagrees with what stock observations show. Always disambiguate "primitive corrected" from "stock observation invalidated".

## Pattern 4 — Name cascade from foundation (no body rework)

Two name corrections this pass were pure cascades from foundation #2/#3 validation: `FUN_006b8340` → `TGMessage::Serialize` (foundation-3 class identity) and `FUN_006b5c90` → `ProcessIncomingPackets` (transport-layer rename). Neither required rewriting the surrounding behavior walkthrough — only renaming the function reference.

Why: foundation-tier renames cascade to every mid/leaf doc that cites the function. When the cascade is pure renaming (behavior described correctly, only the name changes), don't restructure — just substitute the name and tag the line `[v5-validated 2026-05-28]` so the reader knows the rename has been accepted.

How to apply: any mid-tier doc validating after its foundation. Scan for `FUN_xxxxxxxx` references in the body, check if the foundation's `supersedes:` or §6.X §"Cross-doc consistency check" lists a rename, and substitute. Don't rewrite the prose around the rename.

## Pattern 5 — python-source tagging convention for constants tables

When a constants table's *values* are binary-correct (the byte on the wire) but its *names* come from external Python scripts, the convention is to tag the whole table with `[python-source: scripts/X.py + scripts/Y.py + ...]` once, then keep the table as-is. Don't try to anchor each row individually.

Why: a per-row [python-source] tag clutters the table; the per-row [v5-validated] tag is wrong (only the value is validated, not the name). One header tag captures the provenance cleanly.

How to apply: any table where the column structure mixes one binary-anchored column (e.g., the hex byte) with one corpus-anchored column (the constant name). Tag at the table header, not the rows.

## Pattern 6 — Annotation summary as a near-end section

For mid-tier render where 6+ functions got renamed + 5+ got prototypes + 6+ got plates, the annotation table lands as a dedicated "Annotations applied this validation pass" section near the end of the doc body — after the dispatch walkthrough but before Open Questions. Completeness-lift sub-table follows.

Why: future re-validation passes can diff against this section to see what's been touched in Ghidra; the completeness numbers tell the next pass whether to re-score or trust.

How to apply: any pass with >= 5 annotations. Don't bury annotations in the tracker (they belong in §6.X too); the doc-side section makes the annotation visible to anyone reading the rendered doc.

## What this pass did NOT do

- No body restructure. The mechanism-1 / mechanism-2 split, the wire examples, the receive-side dispatch chain — all preserved verbatim (only `TGMessage::WriteToBuffer` → `TGMessage::Serialize` and `ProcessIncomingMessages` → `ProcessIncomingPackets` substitutions). Lowest-touch render in the protocol family so far.
- No drop. Every prior claim survived. Lesson: when a pre-v5 doc was authored by reading the binary (vs. extrapolating), v5 validation is a relatively light pass — corrections are mechanical, not architectural.

## Cross-references

- [[protocol-hub-doc-render]] — sibling pattern for the hub/index layer
- [[opcode-catalog-render-patterns]] — sibling for the C++ dispatcher mid-tier docs
- [[dispatcher-subordinate-render-patterns]] — sibling for NetFile-style sub-catalogs
- [[transport-foundation-render-patterns]] — foundation-layer pass that cascades the TGMessage naming this pass absorbs
