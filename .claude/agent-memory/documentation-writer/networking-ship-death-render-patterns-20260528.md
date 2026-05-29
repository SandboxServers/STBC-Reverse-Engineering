---
name: networking-ship-death-render-patterns-20260528
description: Networking leaf #11 (FINAL networking leaf) render patterns — ZERO wire/sequence corrections with 1 cosmetic name-fabrication cascade + 1 falsified-speculation strike + 1 newly-created handler clarification + 1 cross-doc tension flag deferred (DO NOT EDIT companion).
metadata:
  type: project
  date: 2026-05-28
  family: networking
  doc-number: 11-leaf-FINAL
  status: partial
---

# Networking Leaf #11 (ship-death-lifecycle.md) — Render Patterns

7 patterns for FINAL-networking-leaf docs where v5 = "zero wire corrections + cascade-cosmetic + falsified-speculation + new Ghidra fn + cross-doc tension":

## P1 — Zero-wire-corrections NOTE block headline
- Lead with **"Zero wire/sequence corrections"** in bold inside the `> [!NOTE]` block to telegraph that the doc's structural claims survived byte-check
- Enumerate WHAT was byte-checked (3 handler addrs, dual-branch logic, group routing, guaranteed flag, lifetime carry, 6-event 4+2 split) BEFORE listing the corrections — sets the "this doc is mostly right" framing
- Then transition with "**2 minor cosmetic/speculation fixes** plus 1 clarification:" and list C1/C2/Clar-1 as bullets
- Don't promote cosmetic/speculation fixes to severity:HIGH just because the doc was old — the wire is right, the name was wrong

## P2 — Cascade-cosmetic correction (name fabrication from prior leaf)
- When a class name in the prior doc is fabricated and the binary truth was found in a PRIOR LEAF doc, render it as a (C1) bullet citing the leaf number ("per leaf #13")
- DO NOT restructure the body sections that use the name — just rename throughout (e.g., "TGSubsystemEvent" → "TGEvent (factory 0x101) ET_ADD_TO_REPAIR_LIST")
- Keep the substance tables (the 6-count, 4+2 split, subsystem identity) intact — wire data is unchanged
- Add a dedicated `> [!NOTE]` block at the FIRST in-body use of the new name explaining what changed and citing the prior leaf with the discovery
- "Factory 0x0101 IS the TGEvent base class itself" framing — emphasize the IS to invert the prior framing

## P3 — Falsified-speculation correction
- When the prior doc speculated a cause (e.g., "scoring handler may not be registered") and the v5 evidence FALSIFIES it (Python source shows it IS registered), call it out as `[v5-correction YYYY-MM-DD]` at the section header
- Use the pattern: "**Root cause unknown — [the speculated cause IS the opposite of what was claimed]**" with bolded "IS" to invert
- Cite the falsifying evidence with file:line (`Mission1.py:195`) — pythonsource gets file:line, not addresses
- Add explicit **"The prior [hypothesis] is falsified by the [evidence] — strike that line of reasoning."** at end of section
- Reroute the open question to OQ section with refined framing ("investigation should focus on Python early-return paths")

## P4 — Newly-created handler disclosure (Ghidra DB state was "bare code")
- When `create_function` succeeded in this pass (auto-analyzer hadn't promoted), call it out in the headline NOTE as **Clar-1**
- Mention the byte-size (283 bytes), the dual-branch verification, and that "Future passes will find it pre-defined"
- Cite the systematic pattern: "same pattern as ~13 other dispatched handlers per networking foundation #1"
- In the evidence row, use `note: "X bytes, CREATED in Ghidra this pass (was bare code, auto-analyzer hadn't promoted); dual-branch decompile verified"` — preserves the disclosure
- DO NOT separate the created-function into its own subsection; it's a metadata fact, not a body claim

## P5 — Cross-doc tension flag (defer the edit)
- When the validation memo surfaces a cross-doc contradiction in a companion doc that has its own validation pass in flight, render it as a dedicated `> [!IMPORTANT]` block in the relevant body section
- Format: "**Cross-doc tension [YYYY-MM-DD]**: `docs/path/companion.md` (currently ~line N) says X. The [evidence] cited here shows Y. The companion's v5 validation in progress should resolve this — the binary truth is on this doc's side per [evidence]."
- Add explicit parenthetical: "(Cross-doc edit deferred — see family-close batch.)"
- DO NOT modify the companion doc — that's the companion's own pass
- Cite the tension in the body where the contradiction matters (here: "DestroyObject (0x14) is NOT sent for ship death" section)
- ADDITIONALLY add a `companions:` row pointing to the companion so the reconciliation tracking is visible

## P6 — Trace-driven evidence vs Ghidra-byte evidence (mixed-source frontmatter)
- For docs that are PART trace-driven (packet trace counts) and PART byte-anchored (handler disasm), mix the two evidence types in frontmatter:
  - Byte-anchored: `address: 0xNNNNNNNN`, `confidence: high`, `note: "<disasm offset and instruction>"`
  - Trace-driven: `address: null`, `confidence: high`, `note: "<trace session name + observation count>"`
- Inherited claims (from prior leaves): `address: null`, `confidence: high`, `note: "inherited from <leaf-name>"`
- Stock-trace claims (62/62 client-initiated, 0/59 DestroyObject) DESERVE evidence rows even with `address: null` — the trace IS the evidence
- Add a `## Packet Counts from Stock Traces` section with two count tables (collision test + battle) preserving the original numbers — those tables are reference-grade

## P7 — Open Questions framing for falsified-speculation-driven debt
- When C2 falsifies a speculation and the open question is REROUTED (not closed), restate OQ1 with the refined framing: "Handler IS registered ... needs Python script analysis of early-return paths"
- Distinguish "binary RE" vs "Python investigation" in the OQ text — sets reader expectation that this is NOT a future Ghidra pass
- For OQs that ARE Ghidra-able (OQ2: where is 9.5f set?), give a hint about the likely location ("ShipDeathHandler at 0x005AFEA0 likely constructs the ObjectExplodingEvent")
- For OQs that are layout questions (OQ3: event field layout SP vs wire), cross-reference the prior leaf and pose the meaningful semantic question ("Is there an engine 'transient' event view vs the wire-serialized view?")

## Tag set used
- `[v5-validated 2026-05-28]` on: "Key Finding: Stock Server Never Auto-Respawns", "Death Sequence", "Self-Destruct vs Combat Death", "Self-Destruct Repair-Event Detail"
- `[v5-correction 2026-05-28]` on: "SCORE_CHANGE Anomaly" (falsified speculation)
- Inline `(CREATED this pass)` in Key Functions table for `MultiplayerGame_ObjectExplodingHandler`
- Inline `[v5-validated 2026-05-28]` not needed on subsections under tagged parents

## Anti-patterns to avoid
- DON'T downgrade "name was fabricated" to severity-LOW just because wire data is correct — it's still a CASCADE concern across companion docs that referenced the fabricated name
- DON'T delete the speculation that was falsified — convert it to an explicit "X is falsified" statement so future readers understand WHY the section was rewritten
- DON'T modify the companion doc that has its own validation pass — flag the tension and let the companion's pass resolve it
- DON'T promote 9.5f-constant-source to a body section — it's an OQ until found
- DON'T separate created-function disclosure into its own subsection — it's metadata, not body content
