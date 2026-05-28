> [docs](../README.md) / [guides](README.md) / v5-doc-validation-workflow.md

# v5 Doc Validation Workflow (Orchestrator Playbook)

The per-doc procedure for re-validating an existing pre-v5 document against current Ghidra state, under the constraint that **no annotation scripts are run**. Every cited function gets v5-documented by direct Ghidra MCP analysis before its claims are carried forward.

This document is the operational sibling of [v5-evidence-header.md](v5-evidence-header.md) — the header schema defines what gets written; this defines how to get there.

## Why no annotation scripts

The annotation scripts under `tools/` (`ghidra_annotate_globals.py`, `_nirtti.py`, `_swig.py`, etc.) historically named ~15,134 functions and seeded vtable/RTTI labels. They have not been applied to the current Ghidra import (created 2026-05-28). Prior runs produced multiple known-wrong function names that caused downstream RE churn. The campaign's policy is:

- **No bulk script execution.** Naming is done function-by-function via the v5 per-function workflow.
- **Every named function carries v5 evidence.** No name lands without `analyze_function_completeness` scoring above acceptable and a plate comment grounded in the function body.
- **Findings made via v5 supersede pre-v5 doc claims.** If a doc says "the handler is at 0x006a2470" and v5 analysis of that function disagrees with the doc's description, the doc is wrong and gets updated. No exceptions.

## The agents

| Agent | Role in this workflow |
|-------|----------------------|
| `game-archaeology-specialist` | Primary. Does all Ghidra digging via MCP for the campaign. Produces evidence packets. Exclusive Ghidra MCP access. |
| `game-reverse-engineer` | Secondary Ghidra agent — engaged when archaeology specialist is saturated or when the work is outside the campaign scope (e.g., proxy-DLL implementation questions). |
| `documentation-writer` | Renders evidence packets into v5-headered docs. Updates section READMEs and the Documentation Index. |
| `netimmerse-engine-dev` | Consulted for engine-internals framing — scene graph, NIF format, NetImmerse class semantics. No tool calls. |
| `stbc-original-dev` | Consulted for original Totally Games developer intent — design questions, cut content, "was this a bug or intentional". No tool calls. |
| `network-protocol-analyst` | Consulted for wire-format and packet-trace expertise when validating protocol docs. |
| `python-152-reviewer` | Consulted when validation touches the embedded Python layer. |
| `x86-patch-engineer` | Consulted when validation requires understanding low-level x86 details (calling conventions, code caves, instruction encoding). |
| `win32-crash-analyst` | Consulted when a cited function has known crash sites we're documenting. |

The orchestrator (main conversation) coordinates, commits code/docs, and never makes Ghidra MCP calls directly.

## Per-doc workflow

For each doc being validated, run these phases in order. Each phase produces a tangible artifact; the next phase consumes it.

### Phase 1 — Setup

1. Read the doc top to bottom.
2. Build the **claim manifest**: every load-bearing factual claim, numbered, with its current evidence (address cited or `none`).
3. Identify the doc's **address surface**: every Ghidra address mentioned in the body (functions, vtables, globals, jump tables, strings). De-duplicate.
4. Check the campaign tracker (`docs/engine/v5-validation-status.md` or the per-family equivalent) for the doc's expected status, foundation/leaf position, and pre-noted documentation debt.
5. Identify **companion docs** — anything in `companions:` of related docs, or anything the doc itself links to. These may need batch updates when claims change.

### Phase 2 — Ghidra evidence pass

Hand the address surface to `game-archaeology-specialist` with this brief:

```
Doc: docs/<family>/<name>.md
Address surface (from Phase 1):
  - 0x...
  - 0x...
For each address: apply FUNCTION_DOC_WORKFLOW_V5 to the function/data that lives there.
  - analyze_for_documentation
  - rename + set_function_prototype in parallel (only if behavior + name agree)
  - type audit + Hungarian variable renames
  - batch_set_comments with plate / PRE / EOL
  - analyze_function_completeness — target 80%+ for load-bearing functions
For each: return claim-level findings:
  - confirmed (matches doc): cite address + completeness
  - corrected (doc was wrong): cite address + the actual finding + what the doc said incorrectly
  - missing (doc cites address that doesn't exist or has different semantics): cite + describe
Mandatory: confirm `program: STBC.exe` on every MCP call. SGW.exe is the default and will silently misroute queries.
```

The archaeology specialist returns the **evidence packet**:

- Confirmed claims with citations and completeness scores.
- Corrected claims with old-vs-new wording and the supporting evidence.
- Missing claims that need to be dropped or rewritten.
- Per-function completeness scores for the addresses cited.
- Open questions where evidence is ambiguous.
- Header inputs (the values that go into the doc's v5 frontmatter).

### Phase 3 — Cross-agent consultation (when needed)

If the evidence packet surfaces a question the archaeology specialist can't resolve from binary evidence alone, the orchestrator routes it to the right consult agent:

- "Was this implementation choice intentional or accidental?" → `stbc-original-dev`
- "What did NetImmerse 3.1 expect from this class?" → `netimmerse-engine-dev`
- "Does this wire format match the packet trace?" → `network-protocol-analyst`
- "Is this Python code 1.5.2-compatible?" → `python-152-reviewer`
- "What does this code-cave / calling convention look like at the instruction level?" → `x86-patch-engineer`
- "Is this crash signature documented?" → `win32-crash-analyst`

The orchestrator gathers consult answers, attaches them to the evidence packet as `notes:`, and proceeds to Phase 4.

### Phase 4 — Doc rendering

Hand the evidence packet to `documentation-writer` with this brief:

```
Doc: docs/<family>/<name>.md
Evidence packet from game-archaeology-specialist:
  <full packet>
Render the updated doc under the v5 standard:
  - Frontmatter from header inputs
  - Body: replace pre-v5 claims with corrected ones; drop dropped claims; flag any `confidence: low` rows in-body with `> [!NOTE]`
  - Update companion-doc links if any
  - Update the section README.md
  - Update the campaign tracker row to status: verified (or partial if any low rows remain)
Voice: STBC house style (see docs/architecture/architecture-overview.md, docs/protocol/wire-format-spec.md).
```

The documentation-writer returns the rendered file(s) and a list of what was changed.

### Phase 5 — Commit

The orchestrator:

1. Reviews the rendered doc against the evidence packet (sanity check — did the renderer drop a claim it shouldn't have, etc.).
2. Stages the doc file(s), the section README if updated, and the campaign tracker.
3. Commits with a message naming the doc, the v5 status outcome, and a one-line summary of the most significant correction.
4. Updates the relevant task to `completed`.
5. Identifies any companion docs that now need re-validation because their claims interlock with the freshly-validated one. Files new tasks for those.

### Phase 6 — Campaign tracker update

Append a row to the tracker's "Validation log" section (creating it if absent) with:

- Doc path
- Date
- Status outcome
- Claim count: confirmed / corrected / dropped / pending
- Open questions list (will become follow-up tasks if non-empty)

## Foundation→leaves ordering

Within a doc family, validate in dependency order. The engine family order (per the tracker, with documentation-writer's swap recommendation factored in):

1. function-map.md (Foundation — address-range partition)
2. rtti-class-catalog.md (Foundation — class identity)
3. nirtti-factory-catalog.md (Foundation — depends on RTTI)
4. netimmerse-vtables.md (Mid — depends on factories)
5. tg-hierarchy-vtables.md (Mid — depends on NI vtables)
6. function-mapping-report.md (Mid — depends on totals + vtable counts)
7. gamebryo-cross-reference.md (Mid — depends on NI vtables)
8. event-system-architecture.md (Leaf — depends on TG hierarchy)
9. ui-class-hierarchy.md (Leaf — depends on event system + TG hierarchy)
10. decompiled-functions.md (Leaf — depends on function-map + event system)

A foundation doc must reach `status: verified` before docs that depend on it begin validation. This prevents wasted re-renders when a foundation correction cascades downward.

## Stuck states and how to break them

- **Archaeology specialist returns "address has no function in Ghidra".** Use `create_function` if the prologue is recognizable; if not, route to `x86-patch-engineer` to decode the prologue. The dispatcher recovery at 0x0069f2a0 is the canonical example.
- **Evidence packet contradicts the original developer's likely intent.** Route to `stbc-original-dev` — sometimes the binary is the bug, not the doc, and the doc gets a `> [!WARNING]` rather than a rewrite.
- **Two docs cite the same address with different semantics.** Reconcile per [v5-evidence-header.md](v5-evidence-header.md) reconciliation rules. Both move to `partial` until a third doc anchors the disagreement.
- **Doc cites a function whose v5 pass scores below 50.** The cited function itself needs deeper v5 work before its claim is usable. Create a follow-up task; in the current doc, mark the row `confidence: low` and continue.

## Cross-family considerations

When the engine family completes, the same workflow applies to protocol, networking, gameplay, analysis, architecture, and guides — in roughly that priority order, per the campaign's overall foundation→leaves design. Each family gets its own validation tracker (`docs/<family>/v5-validation-status.md`).

The orchestrator playbook itself is a living document — when a phase change is needed (e.g., a new consult agent becomes the right route for a class of question), update this file and the v5 header schema doc together.

## See also

- [v5-evidence-header.md](v5-evidence-header.md) — the YAML schema for the doc frontmatter
- `ghidra-mcp/docs/prompts/FUNCTION_DOC_WORKFLOW_V5.md` — the per-function workflow this playbook orchestrates
- [docs/engine/v5-validation-status.md](../engine/v5-validation-status.md) — the engine-family campaign tracker
- [reading-decompiled-code.md](reading-decompiled-code.md) — context for reading what evidence packets cite
- [CLAUDE.md](../../CLAUDE.md) — agent roster + project conventions
