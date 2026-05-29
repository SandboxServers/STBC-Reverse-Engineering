---
name: gameplay-weapon-firing-render-patterns-20260528
description: Render patterns for gameplay foundation #5 (weapon-firing-mechanics.md) — vtable column scrambled correction, inverted-semantics correction, value-direction correction (boost not penalty), Ghidra-unpromoted body inline-tags, 2-field intensity-mode disclosure, and 4 OQs spanning ctor-init + double-fetch artifact
metadata:
  type: feedback
---

# Gameplay foundation #5 (weapon-firing-mechanics.md) — render patterns (2026-05-28)

Validation profile: 798-line pre-v5 doc, 4 corrections (1 HIGH + 1 MED + 2 LOW) + 6 clarifications + 4 OQs + 0 removals. Substantially trustworthy: ZERO formula/wire/constant errors. Status: `partial`.

## Patterns

### P1 — Three-axis correction triage in the NOTE-block headline (HIGH+MED+LOW grouping)

When a foundation doc survives v5 well but has 4 corrections at THREE severity levels (1 HIGH + 1 MED + 2 LOW), the NOTE block opens with **"Substantially trustworthy doc"** and lists the corrections **in severity order with severity tags inline**:

> ZERO formula errors, ZERO wire-format errors, ZERO constant errors. 4 corrections (**C1 HIGH:** ... ; **C2 MEDIUM:** ... ; **C3 LOW:** ... ; **C4 LOW:** ...) + 6 clarifications + 4 OQs.

The triple-zero "ZERO ... ZERO ... ZERO" preamble signals to readers that the underlying mechanical claims are intact — the corrections are addressability/labeling fixes, not algorithm fixes. **Don't bury the severity tags at the bottom of the corrections section** — they belong in the headline so a reader who only reads the NOTE knows what's at stake.

**Why:** Damage-system v5 (gameplay foundation #4) established the "ZERO formula errors" preamble. Weapon-firing builds on it with multi-severity inline tagging. Future foundation docs at the "substantially trustworthy" level should follow this shape.

**How to apply:** When validation produces N corrections spanning multiple severities, count them in the NOTE block, tag each by severity (HIGH/MEDIUM/LOW) in the headline, and order by severity (highest first). Reserve the "ZERO" preamble for docs that genuinely have no algorithm/formula/wire-byte errors.

### P2 — Vtable column scrambled correction: corrected table + WHY this matters section

C1 was a "Part 6 vtable comparison table — TorpedoTube column slot-to-address mapping scrambled by one slot". The render pattern:

1. **Keep Part 6 as-is in document structure** — the section was useful, the data was just wrong. Don't restructure.
2. **Add IMPORTANT block above the table** explaining the prior doc's specific error and that prose semantics for the BODIES are correct — only slot ordinals were misaligned.
3. **Rebuild the table** with byte-confirmed addresses, bolding the rows that changed.
4. **Add a "Why this matters for OpenBC" paragraph** beneath the table explaining which function (TryFireWeapon at 0x00584E40) is the authority on vtable slot semantics and what +0x7C vs +0x80 mean.
5. **Per-row corrections in prose**: for each row that changed, write a one-line "PhaserBank slot 30 correction" / "TorpedoTube slot 30 correction" paragraph naming the prior wrong address and the new correct one.

**Why:** Readers may be linking into Part 6 from outside the doc (e.g., from a power-system or AI agent's notes). Restructuring would break those links. The prose semantics for the function bodies were never wrong — only the slot ordinals — so the prose pages around the table stay intact.

**How to apply:** When v5 finds a slot-to-address scramble in a vtable comparison table, keep the table heading and structure, bold the changed rows, add the IMPORTANT block above with the specific error description, and write a "why this matters" paragraph below the table citing the binary truth function (the dispatcher that actually consumes the vtable slots).

### P3 — Inverted-semantics correction: rename + invert pseudocode body together

C2 was "FUN_0056c350 'IsSubsystemAlive' return semantics are INVERTED — returns 1 when DAMAGED, not when alive". The render pattern:

1. **In Section 1.3 (where the function is consumed)**: keep the caller pseudocode using the function as-is BUT update the variable name (`cVar1`) and the comment (`// FUN_0056c350 — see C2`).
2. **Insert an IMPORTANT block immediately after the caller** that names the function, states the prior doc's mistake (named it `IsSubsystemAlive` and wrote pseudocode that returned 1 for alive), and explains why the narrative outcome was still correct (the caller checks `if (cVar1 != 1)`).
3. **Provide the corrected pseudocode body** of the function in a separate `c` block with the new name (`IsSubsystemDamaged`) and the INVERTED return semantics, also flipping the recursive descent comment to "short-circuit returning 1 (damaged) up the tree".
4. **In Part 5 function table**: rename to `IsSubsystemDamaged` and add a Description that explicitly says "returns 1 if DAMAGED (see C2)" with `[v5-validated]` tag.
5. **In the evidence row**: claim describes the binary behavior (`returns 1 when subsystem is DAMAGED`); note explains the caller's interpretation.

**Why:** Inverted-semantics corrections are the easiest to render wrong because the narrative outcome can stay correct even when the function-level prose is wrong. Readers who skim the pseudocode without reading the caller will internalize the wrong model. The IMPORTANT block + double pseudocode (caller's view + corrected body) makes the inversion impossible to miss.

**How to apply:** When v5 finds an inverted-return-semantics correction on a helper function whose narrative outcome at the caller is still correct, render BOTH the caller pseudocode (preserving the narrative) AND the corrected helper body (showing the inverted semantics) with an IMPORTANT block in between connecting them. Rename the function in the address-reference table and tag with the correction ID.

### P4 — Value-direction correction (BOOST not PENALTY): replace direction word + add OpenBC implication

C3 was "DAT_00890550 = 1.25f is a BOOST not a penalty — AI/remote ships recharge FASTER". The render pattern:

1. **In pseudocode block (Section 1.2 Mode 1)**: replace "Non-owner ship penalty" comment with "AI / non-owner ship BOOST (NOT a penalty — see C3 below)" inline.
2. **Replace the multiplier name** in pseudocode: not `AI/remote recharge multiplier` but `DAT_00890550  // = 1.25f -> AI/remote ships recharge FASTER`.
3. **Replace the recharge formula direction**: prior was `[* AI_multiplier]`, new is `[* 1.25 if non-owner]`.
4. **Insert IMPORTANT block** below the formula naming the prior doc's specific wrong gloss ("slower recharge") and the binary truth ("1.25x is faster, not slower").
5. **Add an OpenBC implication paragraph**: "when porting, the AI multiplier branch must increase delta_charge, not decrease it".
6. **In Part 4 constants table**: rename column from `AI_recharge_mult` to `non_owner_recharge_BOOST` and bold the value `1.25`. Add `(BOOST not penalty — see C3)` in Used In column.

**Why:** Value-direction corrections are the highest-bug-rate corrections to render because the prior wrong direction often "felt right" to readers (a penalty for AI seems gameplay-correct). Making the new direction load-bearing in EVERY place the value appears (pseudocode comment, formula, constants table, OpenBC implication paragraph) prevents the wrong direction from getting copied into OpenBC by readers who skim.

**How to apply:** When v5 finds a value's direction-of-effect inverted in the prior doc, search the whole doc for every occurrence of the value name and update each one (pseudocode, formula gloss, table column header, table description column). Add an OpenBC implication paragraph immediately under the corrected formula. Bold the new direction word ("BOOST" / "FASTER") so skim-readers don't miss the flip.

### P5 — Ghidra-unpromoted function disclosure: inline tag at every site + dedicated row in address table

5 of the load-bearing functions in this doc (PhaserBank::Fire at 0x00570FE0, PhaserBank::CanFire at 0x00571E60, EnergyWeapon::CanFire at 0x0056FA10, TorpedoTube::Fire at 0x0057C770, TorpedoTube::CanFire at 0x0057D780) are real code that Ghidra's auto-analysis did NOT promote. The render pattern:

1. **At first mention in each section**, add inline disclosure: "PhaserBank::Fire at 0x00570FE0 [v5-validated 2026-05-28] (vtable+0x7C — 64 bytes, SEH-wrapped, Ghidra did not auto-promote)" — the **byte size + structural detail** (SEH-wrapped, 3-byte stub, opens with `mov eax,[esi+0xA0]`) makes the byte-verification credible without re-anchoring.
2. **In the evidence row**: claim describes byte-verified opening sequence; note repeats "Real code Ghidra did not auto-promote" and explains the call site that promoted it as a valid anchor.
3. **In Part 5 address table**: add a Description column entry like "vtable+0x7C — bare code, Ghidra unpromoted (see OQ2)" with `[v5-validated]` tag.
4. **If a body decompiled at one address actually lives at a different vtable slot than claimed** (C1 case): add a body cross-link in Part 5 table — e.g., "TorpedoTube::Fire (supplementary) | vtable+0x80 — full body decompiled in Section 2.3".

**Why:** Foundation docs frequently anchor on Ghidra symbols. When the binary truth is "real code, Ghidra didn't promote it", readers need to know that the anchor is byte-verified (not Ghidra-derived) so they trust the OpenBC port. Disclosing the byte count + structural detail (SEH wrap / xor stub / num_ready prologue) is what makes the anchor credible.

**How to apply:** Whenever an evidence row's address is a function that `analyze_function_completeness` could not score because Ghidra didn't promote it, inline-tag the first mention with the function's byte-verifiable structural signature (size + opening sequence type + SEH disposition). Cite it in the evidence row's note. In the address table, mark the Description with "(Ghidra unpromoted)" or "(bare code, Ghidra unpromoted — see OQ#)".

### P6 — Two-field disclosure for "same semantic, two storage locations" pattern (intensity_mode in both this+0xF4 AND parent+0xF0)

Clar1 was "intensity mode lives in BOTH this+0xF4 AND parent+0xF0". The render pattern:

1. **In the object layout table**, name the field at this+0xF4 with a "(see Clar1)" suffix — don't claim it's the only location.
2. **Insert an IMPORTANT block immediately below the table** stating: which function reads this+0xF4 (with address), which function reads parent+0xF0 (with address), the fact that prior doc text conflated them, and the open question about field-sync (cross-link to OQ1).
3. **In every pseudocode block** where the field is read, comment with the actual offset being read — e.g., `// this+0xF4` vs `// reads parent+0xF0`. This makes the two-location pattern visible inline.
4. **In the corresponding Open Question (OQ1)**, name the SetPowerSetting address (vtable+0x90 = 0x00570F60) as the suspected writer-of-both and state the OpenBC criticality ("Critical for OpenBC's opcode 0x12 handler").

**Why:** "Same semantic, two storage locations" patterns are a class of bug that's invisible until SetX writes only one and SomeOtherRead reads the other. Cloaking docs hit this same pattern with cloak_state in ship+0xE8 vs subsystem+0x40. The render pattern keeps the disambiguation load-bearing in the table + IMPORTANT block + pseudocode comments + OQ — four places — so the next implementer sees it at every read site.

**How to apply:** When v5 finds a field that's read from two different anchor offsets across the same function family, name BOTH offsets in the object layout table (or note the duplication explicitly), insert an IMPORTANT block stating the two read sites + addresses + open question about sync, comment each pseudocode read with the actual offset, and define an Open Question pointing to the suspected writer-of-both (with the OpenBC criticality stated).

### P7 — MP-vs-SP two-path serializer disclosure (TGWinsockNetwork_SendTGMessageToGroup vs SendTGMessage)

Clar2 was "TorpedoFire wire format opcode 0x19 sent to 'Forward' group in MP, sent to self in SP — prior doc said only 'If host, send network packet'". The render pattern:

1. **In the wire format section's IMPORTANT block**, lay out BOTH paths verbatim:
   - MP path with the function name AND the group ID address (DAT_008e5528)
   - SP path with the function name AND the self-target argument shape
2. **Name the prior doc's gap explicitly** ("the prior doc said only 'If host, send network packet' and omitted both the group identity and the SP fall-through").
3. **Cross-link the group ID address to other senders** that use it — e.g., "DAT_008e5528 is the same group identifier used by BeamFire (0x0069FBB0) and other event-forwarding paths".
4. **In the evidence row for the sender**: claim names both paths; note explains the prior gap.
5. **In the constants table**: add a row for DAT_008e5528 with "Forward group identifier" name and the sender function as Used In.

**Why:** Wire-format documentation often glosses over the network-send call as "send the packet". Real BC has MP and SP paths that go through different transport functions with different argument shapes. Readers porting to OpenBC need to know both paths exist so they implement the SP fall-through and don't accidentally route SP fire through the MP relay.

**How to apply:** When v5 finds a serializer with both MP and SP send paths, name both with their full function signatures (function + argument shape) in an IMPORTANT block under the wire-format spec. Cross-link the group ID address to other senders that use it. Add the group ID to the constants table.

### P8 — Multi-OQ section spans architectural+structural+init+artifact concerns

4 OQs in this doc — each at a different concern level:

- **OQ1 (architectural)**: Does SetX write to both fields? Critical-for-OpenBC framing.
- **OQ2 (structural)**: What's the full body of a Ghidra-unpromoted vtable entry? Promotion-path framing.
- **OQ3 (init)**: Field init value claim not verified in ctor. Verification-path framing.
- **OQ4 (artifact)**: Possible Ghidra decompile artifact (FCOMP double-fetch). Verification-path framing.

The render pattern:

1. **Each OQ is its own `### OQ#` heading** with a one-line question as the heading text.
2. **Body has two short paragraphs**: first paragraph describes the concern, second paragraph names "Evidence needed" with the specific action (decompile X, read ctor at Y, verify with debugger Z).
3. **Tag cross-links inline**: if OQ1 is referenced from Section 1.6, write "[Open Question 1](#open-questions)" with anchor. If OQ2 is referenced from Section 2.3, the IMPORTANT block at the top of the section says "[Open Question 2](#open-questions)".
4. **OQs grouped at end** under `## Open Questions` heading. No mid-doc OQs.

**Why:** Foundation docs collect debt at multiple levels (algorithm, structure, init, artifact). Keeping the OQs in one section with consistent `### OQ#` shape lets the v5 tracker pick them up for follow-up passes without grepping the whole body. Cross-linking inline lets the reader jump from the consumption site to the open concern.

**How to apply:** Group all OQs at the end of the doc under `## Open Questions`. Number them sequentially. Each gets a `### OQ#:` heading with a question as the text. Inline-cross-link from the consumption section using `[Open Question N](#open-questions)`. Body has two short paragraphs: concern + "Evidence needed".

### P9 — Open question "needs-evidence" inline tag in the offset table for unverified ctor-init claims

OQ3 (TorpedoTube last_fire_time = -1000.0f init) is referenced inline in the object-layout table as `[needs-evidence: -1000.0f init claim not verified this pass — OQ3]`. The render pattern:

1. **Don't remove the unverified claim from the table** — the value 0xC47A0000 = -1000.0f is mathematically correct, and downstream readers may rely on it.
2. **Tag inline in the Description column** with `[needs-evidence: <claim> not verified this pass — OQ#]`.
3. **Cross-link to the OQ** that explains why and what evidence is needed.

**Why:** Removing unverified claims from foundation docs creates risk of cascading deletions when downstream docs cite them. The "needs-evidence" inline tag flags the trust level without losing the data.

**How to apply:** When a prior doc's claim is "probably right but not verified this pass", inline-tag the cell with `[needs-evidence: <claim> not verified — OQ#]` and define the OQ at the end of the doc.

## Summary

Patterns 1-3 (triple-zero NOTE headline, vtable column scrambled correction, inverted-semantics with double pseudocode) are the high-value novel patterns from this pass. Patterns 4-9 generalize value-direction corrections, Ghidra-unpromoted disclosure, two-field disclosure, MP-vs-SP serializer disclosure, multi-concern OQ section, and needs-evidence inline tags — all patterns that will recur in other gameplay/protocol foundation docs.
