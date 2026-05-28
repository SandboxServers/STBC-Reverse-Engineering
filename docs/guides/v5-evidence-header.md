> [docs](../README.md) / [guides](README.md) / v5-evidence-header.md

# v5 Evidence Header Schema

Every reverse-engineering doc that has been validated under the v5 evidence standard carries a YAML frontmatter header that pins the evidence trail. This document defines that header, the per-claim evidence row, and the rules for keeping it honest.

## What the v5 evidence standard is

The methodology comes from `ghidra-mcp/docs/prompts/FUNCTION_DOC_WORKFLOW_V5.md`. The two ideas that matter:

1. **Every factual claim has an address.** A doc cannot say "the collision handler validates the bounding sphere" — it must say "FUN_006a2470+0x14 validates the bounding sphere [evidence: ghidra address, decompiled snippet]". If you cannot point to where in stbc.exe the claim is grounded, the claim does not go in the doc.
2. **Tooling enforces it.** `analyze_function_completeness` in the Ghidra MCP scores documentation completeness. v5 docs are expected to cite addresses whose Ghidra annotations score acceptably under that tool. Bare assertions ("this is the dispatcher") get rejected.

This applies to all docs in `docs/`. Existing pre-v5 docs are treated as **suspect until re-validated** — facts in them must be re-checked against Ghidra before being carried forward.

## Frontmatter header (required)

Every v5-validated doc starts with this YAML block before any markdown:

```yaml
---
validated: 2026-05-28              # ISO date the validation pass completed
methodology: FUNCTION_DOC_WORKFLOW_V5
binary:
  name: stbc.exe
  size: 6182400                    # bytes; sanity check that we're talking about the same build
  base: 0x00400000                 # image base
status: verified                   # verified | partial | stale | disputed
evidence:
  - claim: "Opcode 0x15 dispatches to CollisionEffect handler"
    address: 0x0069f534+0x54       # jump table entry
    function: FUN_006a2470
    completeness: 92               # from analyze_function_completeness
    confidence: high               # high | medium | low
  - claim: "Handler validates bounding sphere gap < 26 units"
    address: 0x006a2484
    function: FUN_006a2470
    completeness: 92
    confidence: high
  - claim: "Server-side recomputation expected but absent in stock dedi"
    address: null                  # negative claim — must cite where it ISN'T
    function: FUN_006a2470
    completeness: 92
    confidence: medium
    note: "Inferred from no STR ECX/EDX, ESI+offset writes in the body"
companions:
  - docs/protocol/collision-effect-protocol.md
  - docs/gameplay/collision-detection-system.md
supersedes:
  - 2026-02-15                     # prior validation date(s) this one replaces
---
```

### Field rules

| Field | Required | Notes |
|-------|----------|-------|
| `validated` | Yes | ISO date. Update on every re-validation. Old date stays in `supersedes`. |
| `methodology` | Yes | Always `FUNCTION_DOC_WORKFLOW_V5` for current pass. If a future v6 lands, the value changes; the schema stays. |
| `binary.name` | Yes | Always `stbc.exe` for this project. |
| `binary.size` | Yes | File size in bytes. Sanity check against build drift. |
| `binary.base` | Yes | Image base, currently `0x00400000`. |
| `status` | Yes | `verified` = every claim has high-confidence evidence. `partial` = some claims still inferred. `stale` = validated previously, evidence is older than 90 days or two annotation passes. `disputed` = a newer finding contradicts this doc. |
| `evidence` | Yes | At least one row. One row per load-bearing claim. |
| `evidence[].address` | Yes (unless negative claim) | Hex address. `null` only for negative claims — and the negative claim must still name what was searched and where. |
| `evidence[].function` | Yes | Ghidra function name (or `FUN_xxxxxxxx` if unrenamed). |
| `evidence[].completeness` | Recommended | Score from `analyze_function_completeness`. Below 50 means the cited function is not v5-documented itself — surface the gap. |
| `evidence[].confidence` | Yes | `high` = evidence is direct (instruction, byte, table). `medium` = inferred from naming/structure. `low` = guess pending verification. |
| `evidence[].note` | Optional | One line. Use for negative claims, caveats, or "this address is the entry but the loop body lives at +0x80". |
| `companions` | Recommended | Doc paths whose claims interlock with this one. The reader's path forward. |
| `supersedes` | Optional | Prior validation dates being replaced. Append, don't overwrite, so we can see the evolution. |

### Negative claims

A negative claim ("the server does NOT validate distance on CollisionEffect") still needs evidence — but the evidence is *absence*. Write the row with `address: null`, set `note:` to describe what was searched and what wasn't found. Negative claims at `confidence: high` require the searcher to have read the full function body — they cannot be `high` from a pattern grep alone.

## Status promotion rules

A doc moves through statuses; it does not skip.

- **No header** → not v5-validated. Treat all claims as suspect.
- **`partial`** → some claims have evidence, others inferred. Allowed during in-progress validation. Must not stay `partial` for more than one validation cycle.
- **`verified`** → every claim has `confidence: high` or `confidence: medium` with a documented reason. No `confidence: low` rows.
- **`stale`** → was `verified`, but `validated` date is more than 90 days old OR two annotation script runs have happened since. Treat content as load-bearing-but-due-for-recheck.
- **`disputed`** → a newer finding (cited by an issue, a PR, or another doc's `supersedes`) contradicts this doc. The contradiction must be named in a `disputed_by:` field. The doc stays readable but every section that references the disputed claim gets a `> [!WARNING]` block at its top.

## Reconciliation when this doc and another disagree

When two v5-validated docs make conflicting claims:

1. Compare `validated` dates. Newer wins by default — but only if it carries higher or equal `confidence` on the conflicting row.
2. If `confidence` ties, the doc with the higher cited `completeness` wins. The lower-scoring doc gets `disputed` status.
3. If the conflict cannot be resolved from the headers alone, file the conflict in a new `docs/analysis/` doc that names both sources and explains the open question. Both originals move to `partial` until resolution.

The point of these rules is that disagreement is a normal, recoverable state — not a quality failure.

## Body conventions

Beyond the header:

- **Section headers cite, too.** A section called `## Handler dispatch` is followed immediately by the relevant `FUN_xxxxxxxx` reference and a line cite, not by prose alone.
- **Magic numbers are explained.** Every hex constant in the body either has a one-line "this is what 0x008000E5 means" gloss or links to a section where the constant is decoded.
- **Decompiled pseudocode is allowed, but cleaned up.** Original Ghidra output is dense and full of `_var1`/`uVar3`. Rename in the body for readability, but keep the address so a reader can find the raw form.
- **Diagrams are Mermaid, not screenshots.** Screenshots rot; the engine evolves; Ghidra updates. Mermaid stays editable.

## Pre-v5 doc handling

When validating a pre-v5 doc:

1. Read the whole doc. List every load-bearing claim.
2. For each claim, decide: keep, modify, drop, or unknown.
3. For "keep" and "modify" claims, get an address. Without an address, the claim is "unknown" and either gets a `confidence: low` row in the new header (with a follow-up task in the campaign tracker) or gets dropped from the body.
4. Write the new header. Set `status: partial` if any `low` rows remain.
5. Update the body. Remove `confidence: low` claims unless they're explicitly flagged. Add address cites to every kept claim.
6. Add a `> [!NOTE]` at the top of the doc on the first re-validation pointing readers at this guide.

After the first complete pass with no `low` rows, the doc becomes `status: verified`.

## See also

- [v5-doc-validation-workflow.md](v5-doc-validation-workflow.md) — orchestrator playbook for the per-doc validation campaign
- `ghidra-mcp/docs/prompts/FUNCTION_DOC_WORKFLOW_V5.md` — per-function workflow upstream of doc-level validation
- [reading-decompiled-code.md](reading-decompiled-code.md) — how to read what the agents cite
- [lessons-learned.md](lessons-learned.md) — debugging techniques that surface evidence
