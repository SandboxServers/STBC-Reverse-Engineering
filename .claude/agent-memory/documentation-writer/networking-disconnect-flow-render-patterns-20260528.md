---
name: networking-disconnect-flow-render-patterns-20260528
description: 9 render patterns for v5 networking-leaf docs with 2 CRITICAL label-swap corrections + missed-convergence-path + cross-doc binary-truth supersession + offset-swap; learned from disconnect-flow.md (networking leaf #10)
metadata:
  type: feedback
---

# Networking Disconnect-Flow Render Patterns (2026-05-28)

Networking leaf #10 = `docs/networking/disconnect-flow.md`. Source memo:
`.claude/agent-memory/game-archaeology-specialist/networking-leaf-disconnect-flow-validation-20260528.md`.

Verdict shape: 5 material corrections (2 CRITICAL) + 4 clarifications + 2 OQs.
This was an unusually shape-rich pass — useful for future leaves where pre-v5 had
function-attribution swaps AND offset swaps AND a missing convergence path.

## P1 — Two-CRITICAL NOTE-block headline ranking

When the pass surfaces 2 CRITICAL corrections, lead the NOTE block with BOTH
critical findings in the first sentence, then summarize medium corrections,
then clarifications.

Pattern:

> 5 material corrections (2 CRITICAL) + 4 clarifications + 2 OQs.
> Critical: Section 1.2/1.3 swaps `FUN_A` ↔ `FUN_B` throughout (case 4 = X = FUN_A; case 5 = Y = FUN_B); peer offsets +0x2C and +0x30 are swapped (...). 4th convergence path missed (...).

The bold-headlined items get verbatim cite addresses up front so a reader who
glances at the NOTE block can fix their mental model in 30 seconds. The
clarifications get a quick one-clause list.

## P2 — Function-attribution swap fix: in-place section header rewrite + IMPORTANT block

When a pre-v5 doc has `FUN_006b6a20` in a section header but the pseudocode in
the body is `FUN_006b6a70`, the swap propagates through prose. Don't try to
patch in-place with footnotes — rewrite the section header, replace the
pseudocode block, and add a top-of-section IMPORTANT block citing the swap:

```markdown
### 1.2 Graceful Disconnect (Transport Message 0x05) [v5-correction 2026-05-28]

**Handler**: `FUN_006b6a20` — dispatched from `FUN_006b5f70` case 5 ...

> [!IMPORTANT]
> **C1 — Section header swap.** The pre-v5 doc named `FUN_006b6a20` here but
> the pseudocode shown was actually the body of `FUN_006b6a70`. Binary truth:
> case 5 = DISCONNECT = `FUN_006b6a20`; case 4 = BOOT = `FUN_006b6a70`.
```

Then split the original "Section 1.3 Boot/Kick" into TWO sections (1.3 receiver
+ 1.4 sender) — the swap also exposed that the original conflated reception
with sending.

## P3 — Offset-swap (+0x2C ↔ +0x30) deserves a corrected field table

When two offset semantics get swapped, render the corrected field table AGAIN
in the doc with bolded changed rows and the disasm anchor sites inline. This
prevents readers from skimming the table without noticing the change:

```markdown
| **+0x2C** | float | **Last receive timestamp (lastRecvTime)** — written every recv at `0x006b5e63`, read at `0x006b48ae` timeout check |
| **+0x30** | float | **Last send timestamp (lastSendTime)** — written on send in `FUN_006b51e0`, ... |
```

The disasm anchor sites in the row body discharge the "is this just
re-arrangement or a real fix?" reader question.

## P4 — Missed 4th convergence path: dedicated new section + xref count rationale

When the original doc listed N convergence paths but the binary has N+1,
add a NEW dedicated section (here: "1.5 Connect-Clobber") AND update the
Overview ASCII diagram. Include the xrefs count rationale prominently:

```markdown
`get_xrefs_to(FUN_006b75b0)` returns **4 callers** — the connect-clobber here,
the timeout path in `FUN_006b4560`, the graceful path in `FUN_006b6a20`, and
the boot reception path in `FUN_006b6a70`.
```

This makes the negative claim falsifiable — anyone can re-run the xref tool
and see 4 entries.

## P5 — Cross-doc binary-truth supersession (this doc wins over a wrong Ghidra plate)

When the doc-being-validated is CORRECT and the project's Ghidra plate
(applied during a prior doc's validation pass) is WRONG, render an
IMPORTANT block BEFORE the section's prose. Frame as "binary-truth
supersession" not "old doc was right by accident":

```markdown
> [!IMPORTANT]
> **Binary-truth supersession (C4) [v5-validated 2026-05-28]**: `0x006a0a20`
> **IS** the `DisconnectHandler` (...). The current Ghidra plate at this
> address (added during leaf #18 / `<other-doc>.md` validation) calls it
> `EnterSetEventHandler` — that is **WRONG**. The actual `EnterSetHandler`
> is at `0x006a07d0`.
>
> This finding will be propagated as a corrective patch to leaf #18 in a
> follow-up handoff.

```

Discharge the conflict by:
1. Naming the wrong-plate doc explicitly.
2. Stating the corrective-patch follow-up commitment.
3. NOT modifying the wrong-plate doc in this pass (out of scope; the user
   instruction set it as a separate handoff). This avoids cross-doc thrash
   when multiple docwriters run concurrently.

## P6 — Cross-doc inline correction (other doc's narrative had a wrong attribution)

When a pre-v5 line says "0x14 DestroyObject: Observed for ship destruction
(combat kills)" but a sibling doc (ship-death-lifecycle.md) has 0/59
battle-trace evidence to the contrary, replace the line inline with the
corrected attribution AND cite the sibling:

```markdown
- **0x14 DestroyObject**: Observed for disconnect-triggered ship cleanup
  (**NOT for combat kills** — see [ship-death-lifecycle.md](ship-death-lifecycle.md)
  for the 33.5-min battle trace showing **0/59 combat deaths use 0x14**).
```

Bolded NOT + the trace count make the correction's evidence weight obvious.

## P7 — Per-correction frontmatter rows over consolidated rows

For 5+ corrections, prefer one frontmatter `evidence:` row per correction
(rather than one row per affected function). Each row's `note:` cites the
correction tag (C1/C2/C3/C4/C5) explicitly. This keeps the frontmatter as a
1:1 mirror of the corrections list so future re-validations can audit by
row.

Example for the offset swap:
- One row for "peer+0x2C is lastRecvTime — written every recv" cite address 0x006b5e63
- One row for "peer+0x30 is lastSendTime — written on send" cite address 0x006b51e0
Both tagged with `note: "C2 — SWAPPED in pre-v5 doc."`

## P8 — Confidence: medium for the timeout 45s value

For partial-evidence values like "45.0s timeout claimed but not byte-checked
at WSN ctor in this pass," use `confidence: medium` with a note explaining
what WAS verified vs what WASN'T. Don't drop the claim — it's still
load-bearing and the memo flagged the verify gap as Clar-2.

```yaml
- claim: "Peer timeout threshold is per-WSN-instance at WSN+0xB8 (45.0s claimed; set in WSN constructor)"
  confidence: medium
  note: "WSN+0xB8 read confirmed at the timeout-comparison site. The 45.0s value is the prior doc's claim — not byte-checked at the WSN ctor in this pass."
```

## P9 — Open Questions section ordering: low-priority promotion-path items last

When OQs are clearly low-priority follow-ups (proxy decode framing, leaf #9
cross-verify), put them in their own `## 10. Open Questions` section near the
END of the doc but BEFORE the appendix. Each OQ gets its own subsection with:
- The question stated.
- A possibilities list (3 bullets max).
- A "promote to a correction if X is identified" closing line.

The appendix (here: complete disconnect sequence walkthrough) follows the OQs.
This keeps the doc's narrative arc intact for readers who skip OQs.

---

## What NOT to do

- DO NOT modify the leaf #18 doc (objnotfound-requestobj-enterset-wire-format.md)
  to fix the wrong Ghidra plate. That's a SEPARATE handoff per the user
  instruction. Doing it here would create a cross-render conflict with
  whatever docwriter handles the leaf #18 update.
- DO NOT modify v5-validation-status.md — that's batched at end of wave.
- DO NOT modify shared MEMORY.md — write a new dated topic file like this one.
- DO NOT promote to `verified` — 2 CRITICAL corrections + 1 medium-confidence
  claim (45.0s value) + 2 OQs means `partial` is the right status.
- DO NOT delete the wire-trace Section 9.x content — it's verified-runtime
  evidence that the corrections preserve, just relabeled (the 0x05 ↔ FUN
  attribution gets fixed at the top of Section 1.2, then Section 9.x flows
  unchanged).

## Pattern summary

This pass is the canonical example for:
- 2 CRITICAL function-label-swap + offset-swap + missed-path combo
- Binary-truth supersession of a wrong-plate from a prior leaf's validation
- Splitting one pre-v5 section into a receiver + sender pair when the swap
  exposes a sender/receiver conflation
