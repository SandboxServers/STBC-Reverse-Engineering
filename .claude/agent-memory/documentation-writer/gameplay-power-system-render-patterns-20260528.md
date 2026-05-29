---
name: gameplay-power-system-render-patterns-20260528
description: 9 render patterns for largest-gameplay-foundation v5 render (1221 lines, 5 corrections incl. 1 HIGH-priority class-hierarchy vtable shift across 8 of 11 classes + cascade to prior leaf), with 26 Ghidra renames + 7 byte-confirmed constants + 3-tier of OQs (resolved/partial/script-sourced)
metadata:
  type: feedback
date: 2026-05-28
---

# Gameplay foundation #3 (power-system.md) render patterns

Largest gameplay doc rendered to date (1221 lines, ~50 evidence rows). Validation memo verdict: `partial` with 5 corrections + 1 cascade to already-validated protocol leaf #19. Re-render preserved entire body structure (sections + script-sourced tables) while inserting binary-truth corrections at the right anchor points.

## P1 — HIGH-PRIORITY-and-cascade NOTE block headline

When a foundation doc has BOTH (a) a HIGH-severity local correction AND (b) a cascade to an already-validated companion doc, lead the NOTE block with both facts in the bolded headline:

> **v5 re-validation 2026-05-28 — 5 corrections including 1 HIGH-PRIORITY vtable-to-class table shift across 8 of 11 subsystem classes + cascade to protocol leaf #19 (subsystem-integrity-hash).**

Then bullet-list the corrections with severity tag (HIGH inline). Don't bury the cascade in C1's section body — surface it in the headline so reviewers reading the NOTE know there's downstream work pending. The cascade gets its own IMPORTANT block inside C1's section for the byte-level reconciliation.

## P2 — Vtable-shift correction with side-by-side diff table

When the binary-truth correction is a column-shift across many rows (here: 8 of 11 vtable→class mappings circular-shifted), render a single side-by-side diff table with three relevant columns:

| Slot | Class | Vtable (binary truth) | Vtable (prior doc) | Status |

The `Status` column gets bolded **CORRECTION** for shifted rows, plain "OK" for unchanged. This makes the scale of the shift instantly visible (8 of 11 = lots of bold text). Anchor the table in a sentence above with the source ("extracted from Ship__SetupProperties FUN_005B3FB0 disasm + 12 individual ctor decompiles") so readers know which Ghidra function to verify against.

Also include the corrected tree representation (ASCII art) BELOW the diff table — the diff is the proof, the tree is the new canonical reference shape.

## P3 — Property-class-ID vs instance-class-ID disambiguation subsection

When the prior doc conflated two type-ID namespaces (here: PowerProperty class IDs 0x812F..0x813F vs subsystem instance class IDs 0x8021..0x8029), give the disambiguation its own subsection inside the corrected hierarchy block. Use a 2-row table:

| Namespace | Range | What it identifies | Where stored |

This is a reusable pattern across the codebase — type-ID confusion is a recurring trap (also seen in protocol leaf #19's HullSubsystem-vs-HullProperty mix-up). Future docs touching the 0x80xx range should preemptively cite this disambiguation.

## P4 — Cross-doc cascade IMPORTANT block placed inside originating section

Cross-doc cascade gets a dedicated IMPORTANT block AT THE BOTTOM of the local correction section (not at doc top, not at doc bottom). This places the cascade context next to the binary-truth that triggered it, so a reader patching the companion doc can see WHY they're patching. Include:

- Companion doc path
- What the companion currently says (with quote of the wrong claim)
- What binary truth says
- Which prior corrections in the companion STILL HOLD vs which need reverting
- Statement that the cascade is "being patched separately" (per orchestrator no-modify rule)

## P5 — Inverted-gate correction with truth table

For C2 (gate logic inverted), render the correction with:

1. Block quote of prior wrong claim
2. Binary `if (...)` body shown verbatim
3. English translation of the condition
4. Full 4-row truth table (IsHost × IsMultiplayer × Gate × Effective scenario)
5. Practical observation ("in practice this gate likely never excludes anything")
6. Forward reference to where the REAL host-authority is enforced ("see C3")

Truth tables are the load-bearing artifact for gate corrections — they make the inversion visible and let the reader verify the binary independently. Always include "effective scenario" column to make abstract truth-table rows concrete.

## P6 — Client-side prediction correction with C-preamble verbatim + impact paragraph

For C3 (host-authority gating omitted from pseudocode), render in 3 parts:

1. **Block-headline opener** naming the architectural pattern ("This is fundamental client-prediction architecture that the prior doc completely missed")
2. **Verbatim C preamble** showing the bVar3/bVar5 setup with comments explaining what each branch means
3. **Implication paragraph** translating the pattern for clean-room implementers (what clients DO vs what host does; why the function still returns a value even when not mutating; how reconciliation actually happens)

Then update the pseudocode further down (DrawFromMainBattery body) to include the `if (bVar3) { mutate; }` gates — don't just describe the gating in prose, show it in the code block too. Reader needs both the conceptual frame AND the byte-level details.

## P7 — Mislabel correction reframes section heading and content

For C4 (FUN_0055F7F0 mislabeled as "reactor enable guard" but actually "cloak-decloak shield restore"), the correction REWRITES the section heading itself ("Safety Guard" → "Stage 4: Cloak-Decloak Shield Restore"), not just the prose underneath. Include:

- Block quote of prior wrong description
- "Binary truth:" lead-in
- Numbered list of what the function actually does (call site, body steps, events posted)
- Cross-link to companion (cloaking-state-machine.md) since the function lives in cloak state-machine territory
- Renamed-in-Ghidra inline disclosure ("Renamed in Ghidra to `CloakDisengageRestoreShield` + plate added")

If the section is part of a numbered list (here: 4-stage init), update the numbered diagram at the bottom AND the section heading — both must agree on the new name and purpose.

## P8 — Field-label swap correction with verbatim code + minor-issue framing

For C5 (head/tail labels reversed), render as a > NOTE blockquote inside the runtime layout section rather than a standalone correction subsection. Include:

- Bolded headline naming the swap
- Verbatim C from the binary showing both the first-insert path and subsequent-insert path
- Conclusion sentence ("So inserts grow at +0xCC...")
- "Minor labeling issue; data structure is correctly characterized" framing so readers know the algorithm is right, only the column header swapped

In the per-offset table further up, the swapped offsets get their description column updated with "**C5 CORRECTION**: This is the TAIL..." inline annotations so the table is self-documenting without reference back to the correction section.

## P9 — Three-tier OQ structure (resolved / partial / script-sourced)

Open Questions section uses 3 distinct dispositions for the prior doc's 5 OQs:

1. **Promoted to confirmed claims** with v5 tag (e.g., the 2 cloak events resolved in C4) — these come OUT of the OQ list and become positive claims in the body.
2. **Resolved but partially** — `OQ-1 — Event ID set: partially resolved. CONFIRMED this pass: [list]. STILL UNVERIFIED: [list].` — explicit dispositions for each sub-item.
3. **Discovered this pass** — new OQs (here: OQ-2 vtable 0x008936F0 mystery, OQ-3 watcher class identity, OQ-4 ComputeTotalPowerWanted body) that came up during validation and need future work.
4. **Script-sourced flag** — OQ-5 for content that's NOT stbc.exe binary (here: per-ship hardpoint tables) — explicitly marked "Out of scope for binary RE" so future validation passes don't waste effort.

This 3-tier OQ structure is the right pattern for foundation docs that have substantial script-sourced sections (gameplay docs in particular). Don't drop the script-sourced sections; ADD a NOTE block above them flagging they weren't re-validated this pass, and reference OQ-5 in the NOTE.

## P10 — Stage-numbered init chain with cross-stage correction

When a correction lands inside an N-stage initialization chain (here: Stage 4 was misidentified), keep the stage-numbered structure intact but rewrite the stage's content:

- Stage 4 heading became "Cloak-Decloak Shield Restore" instead of "Safety Guard"
- The closing summary diagram updated to reflect the new Stage 4 role
- A clarifying line added: "Not part of normal ship spawn init" — disclaims the stage's role in the init chain since it's actually called from cloak state-machine

If a "stage" turns out NOT to actually run during init, say so explicitly rather than removing it from the numbered list — readers may have inbound links to "Stage 4".

## Reusable artifacts from this render

- **Side-by-side vtable diff table** (P2): reusable any time a class-hierarchy or struct-layout doc gets corrected by Ghidra binary-truth.
- **Property/instance class ID disambiguation 2-row table** (P3): reusable across all docs that touch the 0x80xx type-ID space.
- **4-row gate truth table** (P5): reusable for any boolean-gate correction (IsHost/IsMultiplayer or any 2-flag combination).
- **Three-tier OQ disposition** (P9): reusable for ANY foundation doc with script-sourced sections + new findings this pass + partially-answered prior OQs.

## What NOT to do

- **Don't strip script-sourced sections** even if they weren't re-validated — add NOTE block flagging the gap, reference an OQ row, and leave the content. Readers and modders depend on those tables.
- **Don't merge multiple corrections into a single mega-section** — each correction (C1/C2/C3/C4/C5) gets its own subsection placed at its content context, not centralized in a bottom appendix. C1 lives in Class Hierarchy, C2/C3 live in their Draw section, C4 lives in Stage 4 init, C5 lives in Consumer Registration.
- **Don't downgrade vtable-table corrections to LOW severity** just because they don't change wire format — they DO change OpenBC's class identity decisions, which IS load-bearing. C1 is HIGH severity even though it's "just" labels.
- **Don't modify cascade-target docs** in the same pass — the orchestrator's no-touch list includes the cascade targets (here: subsystem-integrity-hash.md, wire-format-spec.md). Render the cascade as an IMPORTANT block calling out what needs patching elsewhere, then surface it in the completion summary.
- **Don't add Open Questions for things that are out of scope** without marking them as such — OQ-5 explicitly says "Out of scope for binary RE" so the next pass doesn't try to validate hardpoint scripts via Ghidra.
