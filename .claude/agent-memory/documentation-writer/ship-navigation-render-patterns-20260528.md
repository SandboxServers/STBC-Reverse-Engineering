---
name: ship-navigation-render-patterns-20260528
description: Render patterns for ship-navigation.md (gameplay mid #11) — 5 corrections (2 HIGH OpenBC-BLOCKING + 3 MEDIUM), 8 clarifications, 3 OQs, ~50 evidence rows. Mid-tier accuracy doc with HIGH-impact field-offset swap (+0x1F8 vs +0x1FC) that's BLOCKING for OpenBC clean-room cascade, plus convergence-point reversal, fabricated cycle index, fabricated event ID, wrong constant.
metadata:
  type: feedback
---

# Ship Navigation Render Patterns — 2026-05-28

Gameplay family mid-tier #11 v5 render pass. 262-line pre-v5 doc, 5 corrections (2 HIGH + 3 MEDIUM), 8 clarifications, 3 OQs.

## Pattern 1 — OpenBC-BLOCKING field-offset swap gets dedicated `## C1` section ABOVE §1

When v5 surfaces a HIGH-severity field-offset swap (e.g., `+0x1F8` and `+0x1FC` reversed) that BLOCKS clean-room cascade, give it a dedicated `## C1` section BEFORE the original `## 1. Targeting Pipeline` heading. The reasoning:
- Reader who skims will hit the swap first
- "OpenBC BLOCKING" tag in the section heading is a flag, not an afterthought
- Inverted prior + corrected layout side-by-side in two tables
- OpenBC clean-room cascade blockquote names the specific implementation impact and links the OpenBC doc that must be updated

**Why:** Field-offset swaps are deterministic implementation bugs — every read/write through the affected struct is wrong. Treating C1 as just-another-table-update would let readers miss it.

**How to apply:** Look for two conditions: (a) HIGH severity, (b) "OpenBC BLOCKING" or equivalent cascade flag. When both hit, give it the C1 prefix slot above the original §1.

## Pattern 2 — Convergence-point reversal renders as IMPORTANT block with arrow-diagram inside

The C2 finding — "all paths converge on FUN_005ad910 / no, the sink is `TurnTowardDifference` at 0x005ad4d0" — gets an `> [!IMPORTANT]` block embedded in the existing `## 2. Turn Computation` section. Inside the block:
- 1-sentence statement of the inversion
- Arrow-diagram showing the actual call chain
- xref counts (deepest function has 1 caller; intermediate has 2 callers) as the evidence
- Note that the SWIG target identification was correct — only the "convergence" framing was wrong

**Why:** Call-graph reversals are common in pre-v5 docs because decomp readers see "function X has body, function Y calls X, conclude X is the sink". Wrong direction. xref count is the discriminator: deepest function has 1 caller; mid functions have 2+ callers. The IMPORTANT block preserves the original section structure (didn't have to renumber §2) while flagging the directional error.

**How to apply:** When v5 inverts a "convergence sink" claim, render the call chain as a 4-line ASCII arrow diagram inside an IMPORTANT block. Don't restructure the section heading.

## Pattern 3 — Fabricated field gets pulled OUT of its table AND replaced by inline IMPORTANT block

Pre-v5 doc's "Target Fields on Ship" table listed `+0x87 | byte | Target list cycle index`. v5 confirms the field doesn't exist — it's a Ghidra `int*[index]` artifact. Render strategy:
- DROP the +0x87 row from the corrected table
- Add a `> [!IMPORTANT]` block immediately ABOVE the corrected table explaining the C3 (MEDIUM) finding
- Inside the block: explain the `param_1[0x87]` (= 0x21C / 4) trap, cite the disasm line at 0x005ae6e0
- Connect to C1 ("same trap as the C1 swap in a different form: integer-index access through `int*` multiplies by 4 implicitly")

**Why:** A fabricated field is worse than a wrong field — readers assume bytes exist at the cited offset. Pulling it from the table without explanation would just leave a hole. The explanatory block teaches the underlying decomp trap so similar fabrications get caught in future passes.

**How to apply:** When v5 identifies a fabricated field, (a) remove the row, (b) add an IMPORTANT block ABOVE the corrected table naming the C-number and explaining the underlying decompiler artifact, (c) cross-link to other corrections that share the same root cause (here: C1 is the same `int*` × 4 stride trap).

## Pattern 4 — Single-event "two events fabricated" correction collapses to one row + IMPORTANT block

The C5 finding — "ET_EXITED_WARP is fabricated; both engage and stop fire 0x008000EF" — renders as:
- One evidence row for the engage function citing the event ID
- A separate row for the stop function noting it fires the SAME event
- An `> [!IMPORTANT]` block IN-SITU at §4 (In-System Warp) explaining the C5 finding
- A note in the block telling listeners to consult ship state (`+0x84` warp-engaged, `+0x210` warp-active) rather than dispatching on event ID
- A separate evidence row with `address: null` for the event constant itself, marked as `function: ET_IN_SYSTEM_WARP_event`

**Why:** Event-ID fabrications are common when pre-v5 docs see two functions and assume two events. v5 reveals one event. The "consult ship state instead" note is load-bearing for OpenBC implementers — without it, listeners would have no way to tell engage from stop.

**How to apply:** When v5 collapses N events to 1, (a) keep the per-function rows (they're still right, just both citing the same event), (b) add a separate evidence row for the event ID with `address: null` and a name like `ET_X_event`, (c) tell readers HOW to discriminate engage/stop without the ID (state-flag inspection).

## Pattern 5 — Constant-value correction (50.0f not 295) renders as IMPORTANT + dedicated Constants table

C4 — InSystemWarp distance 50.0f not 295 — gets:
- An `> [!IMPORTANT]` block stating the value, citing `_DAT_008944b4`, calling out the script-vs-binary disambiguation ("the 295 value may come from a Python `Intercept.py` script")
- A dedicated `### Warp Constants (byte-confirmed)` table including the 50.0f / 75.0f / 0.9659 constants and the single event 0x008000EF
- OpenBC recommendation: "use 50.0 unless deliberately wrapping the Python script's threshold"

**Why:** "C++ binary value vs Python script value" mismatches happen because BC has two scripting layers. Stating both possibilities and recommending the C++ value is the right OpenBC guidance. Embedding the constants in their own table near the IMPORTANT block (rather than scattered through prose) makes them easy to find for clean-room implementers.

**How to apply:** When v5 corrects a constant value that prior doc got from a script: name both possible sources, recommend the binary value, and put the constants in a single byte-confirmed table near the correction.

## Pattern 6 — OQ-flagged speculation gets `> [!IMPORTANT]` block + Open Questions section entry

The "slerp-style" framing for FUN_005ad910 is speculative (real decomp shows linear blending + sign-flip, not slerp). Render strategy:
- Keep the function in the table at its address
- Add an `> [!IMPORTANT]` block flagging the OQ3 finding immediately AFTER the function detail
- Add a numbered entry in the `## Open Questions` section at the bottom of the doc
- Cross-reference: the in-body IMPORTANT block names "see [Open Question 3](#open-questions) below"

**Why:** Mathematical framing claims ("uses quaternion slerp") are common pre-v5 hallucinations — readers see quaternion-style code and pattern-match to slerp. v5 should be skeptical of named-math-algorithm claims without byte-level verification. Marking the framing as speculative WITHOUT removing it preserves the reader's mental model while flagging the unknown.

**How to apply:** When v5 cannot byte-anchor a mathematical algorithm claim, (a) keep the function entry, (b) add IMPORTANT block flagging the OQ, (c) add a numbered OQ at the bottom. Don't remove the framing claim — let the IMPORTANT block do the contextualization work.

## Pattern 7 — Ghidra-symbol orthography differences disclosed in NOTE block right under the call-chain diagram

Ghidra symbol at 0x005ae210 is `Ship_SetTarget` (single underscore). Doc names this `Ship__SetTargetInternal` (double underscore + suffix to distinguish from the wrapper). Render strategy:
- Use the doc's chosen name in headings + tables (doc nomenclature is consistent with C++ pattern)
- Add a `> [!NOTE]` block IMMEDIATELY below the ASCII call-chain diagram disclosing the orthography difference
- Repeat in evidence-row `note:` field with "Ghidra symbol is single-underscore; orthography only, not a correction"

**Why:** Pre-v5 docs often invent disambiguating function names that don't match Ghidra's symbols. v5 should surface this so future Ghidra-driven searches don't bounce off the doc's naming. The NOTE block disclosure prevents the orthography from becoming a "correction" in some future pass — it's intentional doc nomenclature.

**How to apply:** When doc uses one name and Ghidra uses another, disclose in a NOTE block + per-row note. Don't try to flip everything to Ghidra's name — the doc's chosen name may be semantically clearer (here, distinguishing wrapper from inner).

## Pattern 8 — Open Questions section near end (not centralized at top) for 3 separate OQs

This doc has 3 OQs:
- OQ1 — stock-MP wire usage of opcode 0x10 (needs trace cross-check)
- OQ2 — FUN_005ad910 override-param semantics
- OQ3 — "slerp-style" framing speculative

Render strategy: Dedicated `## Open Questions` section near the bottom of the doc, ABOVE Related Documents but BELOW §9 Network Authority. Each OQ:
- Numbered (OQ1, OQ2, OQ3)
- Bolded label naming the question
- 2-3 sentence body
- Cross-link to companion doc where the answer might live (here: valentines-day-battle-analysis for OQ1)
- Connection back to the in-body IMPORTANT blocks via "[Open Question N](#open-questions)" links

**Why:** OQs near the bottom (not centralized at top) match the layout used by other gameplay-mid docs. Top-of-doc NOTE summarizes the OQ count; bottom-of-doc section lists them in detail. This keeps the reader who came for "what's the function address" from being slowed by speculative items.

**How to apply:** When v5 surfaces ≥3 OQs, give them their own `## Open Questions` section near the bottom. Cross-link from in-body IMPORTANT blocks. NOTE-block at top counts them ("3 OQs") but doesn't expand them.

## Pattern 9 — Frontmatter evidence-row grouping by section comments (#---- Section Name ----)

This doc's frontmatter has ~50 evidence rows organized into 8 section blocks via inline comments:
```yaml
  # ---- Targeting pipeline (8 functions) ----
  - claim: ...
  # ---- Turn computation (5 functions) ----
  - claim: ...
  # ---- Impulse movement (4 functions + field layout) ----
```

**Why:** Frontmatter YAML doesn't have a section construct, but inline `# ---- ----` comments scan well for readers + future authors. Grouping by section also makes it obvious when a section is under-evidenced (e.g., only 2 rows for a section that should have 6).

**How to apply:** When evidence-row count > ~20, group with inline `# ---- Section (N items) ----` comments. Mirror the §-number-to-section mapping of the doc body for easy cross-check.

## Pattern 10 — Cross-anchor evidence rows cite the source doc + validation date in `note:` field

`ImpulseEngineSubsystem_Ctor` at 0x00561050 is cross-anchored from `power-system.md`. The evidence row's `note:` field reads:
> "Cross-anchored from power-system.md (validated 2026-05-28). ImpulseEngine+0xAC is used by SetSpeed for the division."

Pattern: when an evidence row is cross-anchored from an already-validated companion doc, the `note:` field cites the doc + validation date as the authority. No need to re-verify in the current pass — the cross-anchor IS the verification.

**Why:** v5 doc-validation is a graph, not a tree. Each doc's evidence rows can be sourced from (a) fresh Ghidra, (b) cross-anchor from a previously-validated companion. Disclosing the source in the `note:` field is the v5 convention for "I trust this because doc X already validated it 2026-05-28".

**How to apply:** Every cross-anchored evidence row gets a `note:` line that names the source doc + its validation date. Don't silently inherit the claim.
