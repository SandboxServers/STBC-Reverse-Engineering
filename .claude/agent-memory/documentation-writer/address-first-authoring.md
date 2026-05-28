---
name: address-first-authoring
description: Pre-v5 doc drift correlates strongly with prose-first authoring; address-first docs (lead each entry with hex address, prose follows) drift much less and validate cleanly
metadata:
  type: feedback
---

# Address-first authoring is a verified low-drift pattern

**Rule:** When authoring or restructuring a reference doc that catalogs RE'd functions, lead each entry with its hex address; the prose follows. Avoid prose-first entries that bury the address mid-paragraph.

**Why:** During the v5 engine-family campaign, [docs/engine/decompiled-functions.md](../../docs/engine/decompiled-functions.md) (leaf #10, the final engine doc) was the **cleanest validation of the campaign — 0 corrections, 0 drops** out of ~50 entries. The agent's observation: the doc was already address-anchored at every entry, so re-validation only had to confirm existence + spot-check behavior. In contrast, prose-first docs in the same campaign required systematic corrections — event-system-architecture.md (doc #8) dropped ~5 unanchored method-name groups; ui-class-hierarchy.md (doc #9) needed a load-bearing TopWindow/PlayWindow disambiguation; gamebryo-cross-reference.md (doc #7) needed 8 systematic corrections.

**How to apply:**
- New per-function reference docs: prefer the format `### FUN_xxxxxxxx - Name` over `### Name (FUN_xxxxxxxx)`. The address-first form makes drift impossible to hide.
- When migrating prose to a v5 reference doc, the first transformation is "promote addresses to entry leaders".
- Quick Reference tables at the bottom are not a substitute for per-entry address leaders — both should exist; the table is for at-a-glance lookup, the per-entry section is the prose home.
- Pattern is a guideline, not a rule. When the entity is a concept (event ID, struct field offset) rather than a function, the natural lead is the concept name; cite the address inline at first mention.

Related: [[catalog-row-disposition-tree]] (what to do when an entry can't be address-anchored), [[verified-status-criteria]] (the criteria a low-drift doc must clear).
