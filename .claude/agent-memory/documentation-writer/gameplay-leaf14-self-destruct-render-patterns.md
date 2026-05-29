---
name: gameplay-leaf14-self-destruct-render-patterns
description: 9 patterns for gameplay-leaf docs when v5 surfaces a CASCADE-PENDING flag-attribution finding alongside a vestigial-handler reframe and a sentinel-vs-threshold semantic correction
metadata:
  type: feedback
---

# Gameplay Leaf #14 — Self-Destruct Pipeline render patterns (2026-05-28)

Validated against `docs/gameplay/self-destruct-pipeline.md` (gameplay leaf #14, 680 lines pre-render → ~800 lines post-render). 3 corrections (1 HIGH cascade-pending + 2 medium/low) + 2 clarifications + 3 OQs. 1 function CREATED this pass in Ghidra (`TopWindow__SelfDestructHandler` @ 0x0050D070, 219 bytes).

## P1 — Cascade-pending high-severity correction gets its own top-level section + IMPORTANT block

When a v5 correction is HIGH severity but the fix is **explicitly deferred** to a separate sweep (e.g., CLAUDE.md flag attribution that propagates across many docs), render it as a dedicated `## C3 (CASCADE PENDING)` section **immediately after the NOTE block, before the Executive Summary**. Inside the section use a `> [!IMPORTANT]` block (not `> [!NOTE]` — IMPORTANT communicates that the cascade affects this AND other docs). State:

- The current (wrong) attribution claim explicitly
- The binary truth with the asm anchor (e.g., FUN_0069EB17 / MultiplayerGame_Ctor)
- That the doc body **preserves the wrong labels in narrative** (so the cascade sweep can apply a single find/replace later)
- A note that the behavior described is correct, only the per-flag names are wrong

This makes the cascade flag the FIRST thing a reader sees beyond the NOTE block, which is the point — they need to know to mistrust per-flag claims before reading the 3-path narrative.

**Why:** Cascade-pending corrections are easy to lose. If the only mention is in the NOTE block, readers who skip to "Section 3" miss it. A dedicated `##` heading makes it surface in the doc TOC.

**How to apply:** Use this pattern when (a) a correction is HIGH severity AND (b) the fix is deferred to a separate task AND (c) the body preserves the wrong labels. Don't use it for low/med cascading items.

## P2 — Vestigial-section reframe via IMPORTANT block at top + "Reference: dead-handler body" subsection

When a v5 pass discovers that a section describing a handler is **vestigial** (the handler exists but is never invoked in the relevant code path), don't delete the code listing. Instead:

1. Rename the `##` heading to `... -- **Vestigial in MP** [v5-validated YYYY-MM-DD]`
2. Add a `> [!IMPORTANT]` block at the section top explaining the binary truth (e.g., "0/59 sends in battle trace per ship-death-lifecycle.md")
3. Add a `### Reference: dead-handler body at FUN_XXXXXXXX` subheading
4. Keep the original code listing under that subheading

The reader's mental model gets corrected ("don't send 0x14"), the OpenBC implementer gets the right cross-link to the actual death sequence, and the dead-code reference is preserved for archaeologists who want to know what the unused handler does.

**Why:** Deleting the code listing risks information loss; pretending the handler is never relevant loses context for the engine-evolution discussion. Both extremes are wrong; the rename + IMPORTANT block + subheading-preserved listing is the right shape.

**How to apply:** Use whenever a v5 finding shows that a section describes code that exists but isn't on the hot path.

## P3 — Sentinel-vs-threshold semantic correction gets inline rewrite at the gate description

When a v5 correction flips a "threshold" interpretation to a "sentinel" interpretation (e.g., `DAT_008E5C18 = FLT_MAX` is NOT a damage threshold, it's a dying-sentinel reentrancy guard), don't add a separate `## C2` section — instead:

- Rewrite the gate description inline at the existing numbered-list step where it appears (e.g., "Gate checks: hullHP < FLT_MAX" with an inline `[v5 C2]` tag)
- Cross-anchor to other docs that use the same sentinel pattern (e.g., protocol leaf #18 DamageableObject HP slot)
- Update the Constants table to add the sentinel value with the byte pattern explicit

**Why:** Sentinel-vs-threshold is a semantic difference, not a structural one. The numbered-list step is the right place to fix it because that's where readers look for "what does this gate mean". A separate `## C2` section creates organizational noise.

**How to apply:** Inline when the correction is a single-step semantic flip. Promote to its own section only if it cascades into multiple downstream consequences.

## P4 — Single-arg-vs-multi-arg signature correction gets a blockquote callout above the decompile

When a v5 pass corrects a function signature (e.g., from 2-arg `__thiscall(ship*, powerSS*)` to 1-arg `float10(subsystem*)`), put the correction as a `> Clar1` blockquote **immediately above** the decompile listing. Then update the decompile to show the corrected signature. In the corrected decompile, add a comment explaining where the "missing" param comes from (e.g., `// ship recovered inside _Inner via subsystem+0x40 parent backref`).

**Why:** Signature corrections are easy to miss when buried in a NOTE block. Anchoring them directly above the decompile listing makes them impossible to skip when the reader is studying the function body.

**How to apply:** Use whenever Ghidra's actual signature differs from the prior doc, even if semantics are unchanged.

## P5 — CREATED-this-pass functions get a top-of-section disclosure with size + endpoint

When the archaeology pass had to `create_function` for a previously-bare-code address, the doc's section for that function leads with a callout:

> **Function CREATED this pass.** Prior to this v5 validation, the body at `0xADDRESS` was bare code in Ghidra — no function existed. The archaeology pass created `FUNCTION_NAME` (body size 0xNN = N bytes, ending 0xENDPOINT). The reconstruction below is verified against the live disassembly.

Include the body size in BOTH hex and decimal. The endpoint address is useful for cross-referencing with other tools (e.g., x64dbg sessions). Use the new function name (with double-underscore C++-style) consistently throughout the rest of the doc.

**Why:** Function-creation events change what's discoverable in Ghidra navigation; flagging them helps future readers who try to look up the symbol and find it under a different name than the original FUN_-prefixed bare-code reference.

**How to apply:** Whenever any v5 pass creates a new function in Ghidra.

## P6 — Three-path execution narrative + flag-name caveat IF flag attribution is cascade-pending

If a flow-diagram narrative depends on flag-name interpretations that are correct in behavior but wrong in attribution (the C3 case above), add a paragraph caveat at the top of the reconstruction section explaining that the flag names shown match the CURRENT (wrong) CLAUDE.md labels but the control flow is correct. Do not edit the flow narrative inline — keep the narrative readable with the same names readers see in CLAUDE.md, and rely on the C3 section for the corrected attribution.

**Why:** Editing flag names inline in a multi-paragraph narrative creates inconsistency between this doc and every other doc using the old labels. A caveat at the top + a dedicated C3 section is cleaner.

**How to apply:** When flag-name semantics are inverted but behavior is correct AND the fix is cascade-pending across many docs.

## P7 — Wire-format trace section stays AUTHORITATIVE; in-memory event-field corrections get noted in the ShipDeathHandler step

When a v5 pass finds that the in-memory event-field assignments described in the doc don't quite match the decompile (e.g., "dest = ship" vs. asm-actual "event+0x28 = attacker, event+0x2C = hullHP"), correct the in-memory description in the numbered step (here: ShipDeathHandler step 5) but explicitly note that **the wire-format trace section below is authoritative** on the over-the-wire layout. Then describe what the in-memory event actually holds, and explain that the wire layer resolves correctly even when the in-memory shorthand was hand-wavy.

**Why:** Wire-format trace tables anchor against captured packets; in-memory descriptions anchor against decompiles. The two can disagree slightly when the doc's shorthand is wrong but the wire output is right. Be explicit that wire = ground truth.

**How to apply:** Whenever the v5 pass corrects an in-memory field assignment that doesn't actually change the wire output.

## P8 — Open Questions section is mandatory when corrections are accepted but underlying mechanism is partially unverified

Even if the doc is `partial` (not `verified`), Open Questions list explicit follow-up items:

- **OQ1**: unpromoted call sites whose context labels are inferred, not verified
- **OQ2**: dataflow chains corroborated by trace data but not pinned by promotion (e.g., NULL attacker → event+0x28=0 path)
- **OQ3**: Python-source claims not re-verified against the checked-in script

Each OQ states (a) what's unverified, (b) what evidence corroborates the claim (trace data, plate comments), (c) what work would close the OQ. This makes OQs actionable for future archaeology passes.

**Why:** Without OQs, partial-status docs look "validated" but contain unverified claims that compound across cross-referencing. Explicit OQs let future readers know what's load-bearing-but-soft.

**How to apply:** Always add at least one OQ when status is `partial`. If no OQs come to mind, the doc is probably ready for `verified` status — re-check.

## P9 — Constants table grows with sentinel-byte patterns and exact addresses for FLT_MAX-style globals

When a sentinel correction flips a global's meaning (e.g., DAT_008E5C18 from "some threshold" to "FLT_MAX dying-sentinel"), add the sentinel to the **Constants and Strings** table at the top of the doc, with:

- The raw byte pattern (e.g., `ff ff 7f 7f`)
- The IEEE encoding (e.g., 0x7F7FFFFF)
- A short one-liner naming the semantic role (e.g., "**dying-sentinel reentrancy guard**" in bold)
- A see-NOTE-block reference if the correction is more deeply explained there

**Why:** Constants tables are where readers go to verify byte-level claims. Sentinels deserve table-level visibility, not just inline mention in the prose.

**How to apply:** Every sentinel-correction lands in the Constants table; bare prose mentions are not enough.

---

## Tag set used this pass

- `[v5-validated 2026-05-28]` at section headers for: Constants and Strings, Key Functions, Complete Flow Diagram, Wire Format Opcode 0x13, Sender Code, DoDamageToSelf, ShipDeathHandler, DestroyObject Handler (vestigial), All Callers of DoDamageToSelf, TopWindow__SelfDestructHandler reconstruction, Event Registration, Open Questions
- `**CREATED this pass**` inline marker in Key Functions table for `TopWindow__SelfDestructHandler`
- `[v5 C2]` / `[v5 Clar1]` / `[v5 Clar2]` inline tags inside numbered lists where the correction lands
- Inline `> Clar1 (2026-05-28)` blockquote callouts above corrected decompiles
- HOST SIDE block in flow diagram tagged with `[v5-validated 2026-05-28 — HostMsgHandler reads sender + PowerSubsystem cascade]`

## What NOT to do

- **Don't propagate the C3 cascade fix to other docs in this pass.** The user explicitly said not to. The C3 IMPORTANT block IN THIS DOC is the visibility mechanism; a separate sweep handles propagation.
- **Don't delete the vestigial-handler code listing.** Reframe + keep under `### Reference:` subheading.
- **Don't add a `## C2` for the FLT_MAX sentinel correction.** It's a single-step semantic flip; rewrite the gate description inline.
- **Don't rename flag variables in the flow-diagram narrative.** Keep the wrong names + add the caveat — cascade sweep handles the rename.
