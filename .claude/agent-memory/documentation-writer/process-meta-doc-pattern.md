---
name: process-meta-doc-pattern
description: Process-meta docs (coverage reports, naming-pass narratives, campaign progress trackers) validate by content removal, not by re-anchoring — a different shape than foundation/mid docs
metadata:
  type: feedback
---

# Process-meta doc validation pattern

A class of docs in this repo describe *process state* rather than *binary state*: coverage percentages, pass-by-pass rename counts, annotation-script outputs. Examples include the original `function-mapping-report.md`, anything tracking "X functions named in Pass N", and likely future "campaign progress" snapshots.

**Why:** Foundation docs (function-map.md, rtti-class-catalog.md) cite *addresses* as load-bearing — addresses survive Ghidra re-imports and binary edits. Process-meta docs cite *counts of named functions* and *narratives about prior sessions* as load-bearing. When the project changes its methodology (v5 = no annotation scripts), those counts and narratives become unanchorable.

**How to apply:**

When validating a process-meta doc:

1. **Spot-check the narrative claims via `search_functions`.** If "Pass N renamed function X" is in the doc, look for X in the current Ghidra import. If five randomly chosen claims all fail, the entire narrative section is stale and should be removed (not flagged at `confidence: low`).
2. **Replace the coverage table with current-state truth.** Use the validator's actual Ghidra counts from the evidence packet, not the doc's prior claims. Mark every number explicit about its source ("Ghidra auto-analysis only" vs "project-applied").
3. **Keep script source descriptions if the scripts still exist on disk.** Even when unapplied, the descriptions of what a script *would do* (its source intent) remain accurate reference material. Add a clear "currently unapplied" WARNING callout above them.
4. **Status: `partial`, not `verified`.** Because the doc retains reference material for code not currently applied, the structural ambiguity prevents clean `verified`. The promotion path requires either archiving the unused reference or re-applying the scripts under v5.
5. **Note the restructure prominently in the top NOTE block.** Readers of the prior doc see substantial changes; they need to understand what was removed and why. Two NOTE/WARNING blocks (one for the doc-level v5 caveat, one for the script-suite "not currently applied") works well.

**Three-class section taxonomy** (apply to any process-meta doc under validation):

| Section class | V5 status | Action |
|--------------|-----------|--------|
| Script source descriptions / capability tables | Accurate (describes source code) | Keep with "not currently applied" warning |
| Coverage / progress / pass-narrative sections | Stale (describes prior state) | Drop entirely |
| Cross-confirmed structural claims (e.g., NI/Gb vtable deltas) | Verifiable against foundation docs | Keep with `[v5-validated YYYY-MM-DD]` tag and companion-doc cite |

**Specific pattern for the function-mapping-report.md case (2026-05-28):**

- Removed: "Ghidra MCP Naming Sessions (Passes 1-8)" — full Pass 1-8C narrative, ~75% of doc bulk
- Removed: "Coverage Summary" claiming 83%
- Removed: "Unmappable Functions" section (Pass-era status)
- Removed: "Phase 5 (COM Interfaces) — 0 Yield" (Pass-era status)
- Kept (with WARNING callout): Annotation Script Suite table
- Kept (with same WARNING): "What Each Script Discovers" subsections
- Kept (with v5 cross-link): NI 3.1 vs Gb 1.2 vtable delta table
- Added: "Current Coverage State" (4,797 / 25.8% / 1 project-applied rename)
- Added: "Current Naming Approach Under v5"

The diff ratio was: removed dominate. Lines removed > lines added by roughly 2:1, despite preserving the most useful structural content.

**Related:** [[catalog-row-disposition-tree]], [[verified-status-criteria]], [[v5-foundation-claim-patterns]]
