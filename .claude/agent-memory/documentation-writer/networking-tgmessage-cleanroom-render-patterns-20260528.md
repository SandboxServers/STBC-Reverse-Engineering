---
name: networking-tgmessage-cleanroom-render-patterns-20260528
description: 7 render patterns for clean-room spec docs where v5 surfaces a HIGH-PRIORITY load-bearing C1 (transport-level-relay narrative is false, must be replaced with per-handler model) + 4 clarifications + invalidated speculative explanation. Spec docs need stronger correction framing than RE docs because OpenBC implementers use them as ground truth.
metadata:
  type: feedback
---

# Networking TGMessage cleanroom render patterns (2026-05-28)

Patterns for rendering a clean-room behavioral spec when v5 surfaces 1 HIGH-PRIORITY load-bearing C1 + 4 clarifications + 1 invalidated-speculation footnote. Doc rendered: `docs/networking/tgmessage-routing-cleanroom.md`. Anchor doc: `docs/protocol/tgmessage-routing.md` (protocol mid #7).

## Why clean-room docs need a stronger render shape than RE docs

A clean-room spec is **the spec** for the OpenBC implementers. RE docs document the binary as a forensic record; spec docs hand implementers a contract to satisfy. When v5 corrects an RE doc, readers cross-check against the binary. When v5 corrects a spec doc, readers must change their **implementation**. Two consequences:

1. The C-tagged NOTE at top must call out the **implementation impact** explicitly, not just the binary truth.
2. Behavioral Guarantees and Implementation Considerations sections need per-item v5 tags because each item is a contract clause an implementer reads in isolation.

## Pattern 1: NOTE-block headline = HIGH PRIORITY + impact-named + count

Instead of the usual RE-style "1 material correction + N clarifications" headline, lead with:
- **HIGH PRIORITY for OpenBC implementers** (or equivalent audience callout)
- Named impact ("produces duplicate event delivery for opcodes X / Y / Z — the documented OpenBC parity bug")
- Count of corrections + clarifications + count-change framing ("three routing mechanisms, not two")
- Survival statement ("behavioral contracts all survive — but implementation guidance changes substantially")

Don't bury the OpenBC impact in the body. The NOTE block is the first thing implementers read.

## Pattern 2: Audience field = openbc-implementer (not re-engineer)

Clean-room docs have a different audience than RE docs even when the topic overlaps. Use `audience: openbc-implementer` in the v5 frontmatter (or whatever audience label the project standardizes on). This signals to future docwriters that the doc's tone should be implementation-prescriptive ("MUST", "MUST NOT") rather than descriptive ("the binary does X").

## Pattern 3: Replace-the-section, don't append-a-correction

When C1 invalidates an entire section's framing (here: "Automatic Relay (C++ Layer)"), the wrong move is to leave the section in place with a correction note. Rewrite the section heading too. The new section name should embody the correct model — here, "Per-Handler Relay (C++ Layer)".

Inside the rewritten section, lead with a `> [!WARNING]` block stating:
1. "This section replaces the pre-v5 X claim"
2. One sentence stating what the pre-v5 doc claimed
3. **That is not how the binary works.** (or equivalent verdict)
4. One sentence on the binary truth
5. The OpenBC implementation rule ("MUST NOT implement X")

Then the section body explains the correct model.

## Pattern 4: Per-opcode policy table replaces per-handler trace ratios

The RE-side anchor doc has a column for trace ratios. The clean-room version of the same table drops the ratios and replaces with a "Mechanism" column that names HOW each handler relays (or doesn't). This is the correct adaptation: implementers don't care about historical trace ratios; they need the contract for each opcode.

Keep the table dense (1 row per opcode) — don't split into "relays" vs "doesn't relay" sub-tables. The dense table is easier to scan against an implementation under test.

## Pattern 5: Per-item v5 tags on Behavioral Guarantees + Implementation Considerations

In RE docs, v5 tags at section headers are usually enough. In clean-room docs, each Behavioral Guarantee / Implementation Consideration is its own contract clause. Tag each item individually with either `[v5-validated YYYY-MM-DD via X]` (carried forward) or `[v5-correction YYYY-MM-DD per X]` (changed by C1).

This makes it easy for an OpenBC reviewer to grep through and identify which clauses changed in this validation pass — they're the ones tagged `[v5-correction ...]`.

## Pattern 6: Invalidated speculation gets an "OQ-promoted" treatment

The pre-v5 doc speculated that the chat 1:2 ratio was caused by C++ auto-relay + Python NoMe. With C1, that speculation becomes false. Don't just delete it — promote it to the Open Questions section with three parts:
1. The observation (1:2 ratio)
2. The pre-v5 explanation
3. **Why that hypothesis is now false** (C1 corrected it)
4. The genuine open question (the ratio is still unexplained)

This is important because (a) some reader may still believe the old hypothesis and (b) the observation itself is real and load-bearing for debugging.

## Pattern 7: Count-change clarification (Clar4 = "three mechanisms, not two")

When v5 changes a COUNT (here: 2 routing mechanisms → 3), do three things:
1. Mention it in the NOTE-block headline so readers don't miss it
2. Give the newly-added mechanism its own `##` heading in the body (not a sub-bullet)
3. Add a Behavioral Guarantee for it (here: BG #8 about connect-event broadcast)

The new mechanism needs equal billing with the pre-existing ones, not a footnote treatment. Otherwise readers internalize the old 2-mechanism model and skip the third.

## Cross-doc anchor pattern

When most claims are inherited from a sibling RE doc (here `docs/protocol/tgmessage-routing.md`), the evidence rows can use `note: "Cross-anchored via docs/protocol/X.md row #N"` instead of repeating the full address provenance. Saves bytes, makes provenance explicit, and lets re-validation walks ladder up to the anchor doc cleanly.

Inherit the `status:` from the anchor (here `partial`) unless this doc has its own corrections beyond what the anchor covered. Don't claim `verified` on a clean-room doc if the anchor RE doc is `partial`.
