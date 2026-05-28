---
name: function-mapping-report-validation-20260528
description: V5 validation of docs/engine/function-mapping-report.md — doc is structurally stale; coverage figures wrong, Pass 1-8 narratives describe a prior Ghidra DB that no longer exists. Recommend Option A restructure.
metadata:
  type: project
---

# function-mapping-report.md V5 Validation (2026-05-28)

## Validation outcome
This doc is **structurally obsolete** rather than incrementally wrong. Unlike foundation docs where addresses survive and only names drift, here the *load-bearing content* (coverage stats + Pass narratives) describes work that does not exist in the current Ghidra import. The script-intent table and the per-script "What It Does" sections are accurate and salvageable.

## Three classes of content in this doc

| Section | V5 status | Action |
|---------|-----------|--------|
| Annotation Script Suite table (8 rows) | Accurate description of script INTENT | Keep (with "not currently applied" callout) |
| Coverage Summary (~15,209 / 83%) | WRONG — current state is 4,797 / 25.8% | Replace |
| Pass 1-8 narratives (Feb 2026, ~1,773 renames) | Describes prior Ghidra DB; renames not in current import | Drop or archive |
| "What Each Script Discovers" subsections | Accurate description of script source | Keep |
| NI 3.1 vs Gb 1.2 vtable delta table | Cross-confirmed by netimmerse-vtables.md validation | Keep |

## Spot-checks against current Ghidra (STBC.exe)

Five Pass 7/8 narrative rename claims tested via `search_functions(program=STBC.exe)`:

| Claimed rename | Pass narrative | Current Ghidra |
|----------------|----------------|----------------|
| TGObject__LoadFromStream | Pass 4 ("NiStream save/load pipeline") | No functions matching |
| Game__GetPlayerShip | Pass 7 ("Name normalization: GetPlayerShip → Game__GetPlayerShip") | No functions matching |
| TGEventHandlerTable | Pass 8C ("full event dispatch infrastructure") | No functions matching |
| TGWinsockNetwork__RemovePeerAddress | Pass 7 (explicit normalization example) | No functions matching |
| Ship__AITickScheduler | Pass 5 ("per-ship AI callback") | No functions matching |

Also: `search_functions("swig_")` = 0 matches. The 3,990-function swig annotation script never landed.

Custom-named total in current Ghidra: **4,797** (up from snapshot's 4,781 — minor analysis drift). The doc claims ~15,209. Delta = ~10,400 functions of difference. The 4,797 custom names are auto-analysis artifacts (Catch@addr, Unwind@addr, CRT imports, STL template instantiations) — not project-applied names.

Only v5-applied rename present: `MpgameHandleMessage @ 0x0069f2a0` (1 entry, from foundation #1 dispatcher recovery).

## Why this doc class is different from foundation docs

Foundation docs (function-map.md, rtti-class-catalog.md) cite **addresses** as load-bearing — addresses survive re-imports. This doc cites **counts of named functions** and **narratives about prior rename sessions** as load-bearing. Under v5's "no annotation scripts" policy, both become unanchorable:

- Coverage % depends on names actually existing in Ghidra (they don't, beyond auto-analysis)
- Pass narratives describe historical state of a prior Ghidra DB that was discarded on 2026-05-28 re-import
- Even if the scripts could be re-run, the project's stated policy is they will not be (per CLAUDE.md context: "many issues were found with improperly named functions")

## Recommended action: Option A — Reframe as "Annotation Script Reference (Unapplied)"

Replace coverage stats with current-state truth (25.8% / 4,797 from Ghidra auto-analysis). Drop Pass 1-8 narratives entirely. Keep the script suite table and "What Each Script Discovers" sections as a reference of capabilities not currently exercised. Add explicit v5 policy callout: naming is done function-by-function via FUNCTION_DOC_WORKFLOW_V5.

Option B (archive entirely) is also defensible — the doc's original purpose (coverage progress report) is moot under v5. Option C (hybrid preserving Pass narratives) is weakest: it preserves stale narrative dressed as historical context, conflicting with the user-stated direction to move away from the script-driven approach.

## Companion docs to update on this pass

- `docs/engine/README.md` row for function-mapping-report.md says "~15,209 functions named/excluded (83%)" — must change
- `docs/engine/v5-validation-status.md` §3.10 cites all the stale numbers — must update with this validation log entry
- CLAUDE.md (root) "annotate_globals → 2,348 functions, 393 classes" claim is similarly stale and should be flagged for separate update (out of scope for this validation)

## Header inputs for v5 frontmatter

```yaml
validated: 2026-05-28
methodology: FUNCTION_DOC_WORKFLOW_V5
binary:
  name: STBC.exe
  size: 6394712
  base: 0x00400000
status: partial   # foundation script-intent claims verifiable; coverage/pass claims need removal
companions:
  - docs/engine/function-map.md
  - docs/engine/rtti-class-catalog.md
  - docs/engine/nirtti-factory-catalog.md
  - docs/engine/v5-validation-status.md
  - docs/guides/v5-doc-validation-workflow.md
supersedes:
  - <prior-undated>
```

## Pattern lesson for this campaign

Foundation/mid docs validate by **re-anchoring addresses**. Process-meta docs (coverage reports, naming-pass narratives) validate by **content removal**. The Phase-2 Ghidra effort is light because the question being answered is binary: "did these renames land?" (no), not "what does this function actually do?". Future similar doc classes — anything claiming "X functions named in Pass N" — gets the same treatment.
