---
name: pass2-correction-render-patterns
description: Render patterns for STBC-side Pass 2 cascade corrections (where Pass 2 archaeology overturns a previously-v5-validated label or semantic that propagated through multiple docs)
metadata:
  type: project
---

# Pass 2 cascade correction render patterns (2026-05-29)

When Pass 2 archaeology produces a definitive correction (e.g. `ship+0x2E4 = NetPlayerID, not team_id`) that propagated through multiple v5-validated docs, the render pattern follows a 7-step playbook. Learned from the team_id -> NetPlayerID cascade (gamemode-system-validation-20260529 memo) that touched 7 docs.

## The 7-step playbook

1. **Find every reference via grep** — search both the old label (`team_id`), the byte offset (`0x2E4`), and any alias notations (`ship+0xb9`, `piVar5[0xB9]` — recognize these as int-indexed aliases for the same memory, not separate fields).

2. **Classify each hit per its current accuracy**:
   - **WRONG label** (says `team_id`): fix it
   - **CORRECT use** (e.g. collision-effect-protocol.md already cited `ship+0x2E4 == player_id`): leave alone, no date bump
   - **CORRECT but using less-precise term** (e.g. power-system.md "foreign player-owned ship"): add inline clarification, no date bump
   - **Ambiguous header** (e.g. "Named Slot Layout (ship+0x2B0 to ship+0x2E4)"): tighten the range to exclude the off-by-one inclusion

3. **In each WRONG doc, write 3 layers of correction**:
   - **NOTE block addition** at the top: numbered Pass 2 paragraph with full reasoning, three binary anchors as citations, memo source path
   - **Evidence row update**: relabel the claim text + add a `note:` line citing the memo
   - **Inline body fixes**: every prose/code-snippet/wire-table cell gets `[v5-correction 2026-05-29 via gamemode-system-validation memo]` tag

4. **Bump `validated:` date** only on docs with HIGH IMPACT corrections (semantic relabel of load-bearing claim). Docs with only clarifying inline notes keep their original date.

5. **Status downgrade rule**: if a `status: verified` doc gets a load-bearing semantic relabel, downgrade to `status: partial` with explicit reasoning in NOTE block. The relabel didn't refute the doc but the field semantics shifted.

6. **Preserve historical opcode/function names** — `ObjCreateTeam` stays as the opcode name even though the byte isn't a team_id. Add a column-cell or row-cell annotation `(name retained for historical compat; field is NetPlayerID not team)`.

7. **Don't touch trackers in v5-validation-status.md** — they accumulate stale labels that get batch-corrected at family-close.

## Sentinel phrase pattern

Every Pass 2 correction adds the same sentinel:

```
[v5-correction 2026-05-29 via gamemode-system-validation memo]
```

Variants by context:
- `[v5-correction YYYY-MM-DD]` — for inline within tables (concise)
- `[v5-clarification YYYY-MM-DD]` — when existing wording was already correct but used a less-precise term
- `[v5-correction YYYY-MM-DD via {memo-name} memo]` — for evidence rows and NOTE blocks (with citation)

## Wire-format byte semantic relabel checklist

For each wire-format doc:
- [ ] Wire-envelope table row updated (field name + Type column note)
- [ ] Pseudocode comments updated (e.g. `WriteByte(controller[0x2E4])  ; net_player_id` not `team_id`)
- [ ] Trace decode annotations updated (e.g. `| 02 | net_player_id | 2 |`)
- [ ] Receiver pseudocode comments updated
- [ ] NOTE block has Pass 2 paragraph

For DOWNSTREAM consumer docs (collision/power/integrity-hash):
- [ ] Decompiled code comments updated to use new field name
- [ ] NO frontmatter date bump if existing wording was correct
- [ ] Add inline `[v5-clarification YYYY-MM-DD]` if the gate/predicate is described

## Categories of files NOT to touch during Pass 2

- `docs/{family}/v5-validation-status.md` — trackers, batch-corrected at family-close
- `../OpenBC/` repo files — clean-room, propagation goes through OpenBC PR process
- Docs where existing wording is already aligned with Pass 2 truth (no churn)

## Categories of files TO touch

- `docs/openbc/` (in this STBC repo) — clean-room spec drafts, propagate corrections
- Any pre-v5 doc surfaced by grep that uses the wrong label
- v5-validated docs whose evidence rows or body use the wrong label

## Cross-link the memo

Every NOTE-block Pass 2 entry should cite the exact memo path:
```
Source: `.claude/agent-memory/game-archaeology-specialist/gamemode-system-validation-20260529.md`
```

Plus name the specific section ("Major doc correction" / "Open Questions" / etc.) so future readers can verify quickly.

## Pending follow-ups to surface in final report

- v5-validation-status.md tracker entries with stale labels (NOT modified)
- Ghidra plate corrections (named functions per the memo)
- CLAUDE.md "Documentation Index" or "Key Globals" entries (if any) — not surfaced in this pass, but worth checking
- Cross-doc batch sweep at family-close
