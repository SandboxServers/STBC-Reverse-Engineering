---
name: objcreate-serialization-render-patterns
description: 8 patterns for rendering mid-tier wire-format docs where v5 surfaces multi-class corrections (wire order, struct anchor, two-pass architecture) and resolves an open question; learned from objcreate-serialization.md
metadata:
  type: feedback
---

Patterns from rendering `docs/protocol/objcreate-serialization.md` (protocol mid #10) when the evidence packet carries 3 material corrections + 4 refinements (including a closed open question and a cross-doc disagreement resolution), plus a Two-Pass architectural finding worth its own section.

## Context
- Doc: full ObjCreate/ObjCreateTeam pipeline (opcodes 0x02/0x03), ~270 lines pre-v5, ~80 load-bearing claims
- Companion sibling: object-replication.md (mid #9 — thin handler-index) just validated 2026-05-28
- 3 corrections: C1 (velocity wire byte order inverted), C2 (struct field offset reframe), C3 (architectural — two-pass scheme)
- 4 refinements: R1 (global ID conflation split), R2 (lookup gate two-part), R3 (open-question closed), R4 (cross-doc disagreement resolved)
- Status: `partial` (4 OQs remain; one is cross-source-only and one inverted-FPU)

## Pattern 1 — three-correction NOTE block with semantic-vs-byte distinction
Lead the NOTE with all three Cn callouts. For wire-format corrections especially, distinguish whether **bytes on the wire change** vs **interpretation changes**:

> **C1** — Velocity wire is `[3-byte CV4 direction][4-byte float magnitude]`, NOT `[f32 speed][u8[3] padding]`. Same total 7 bytes, order **inverted**.

The "same total 7 bytes" callout is essential — without it, readers assume backward-incompatibility. With it, they understand: the bytes are unchanged, only the parse is.

Pair this with a trace-decode note inside the table later explaining WHY this slipped (spawn traces are all-zero in those bytes, so both interpretations produce zero — only the binary disambiguates).

## Pattern 2 — struct-field reframe (anchor swap, not new fact)
For C2-class corrections where the prior doc said "+0x84" and the new says "+0x74" but BOTH describe the same array:

> The +0x84 referenced by the prior doc is **`playerSlots[0]+0x10`** = the game-state pointer field WITHIN slot 0.

Frame it as "both anchor the same array using different field references." Then provide the ctor evidence to make `+0x74` canonical:

```
FUN_00859d64(this + 0x1d, 0x18, 0x10, ...);
// this + 0x1d (int-indexed) = byte offset +0x74
```

This presentation prevents the reader from concluding "the binary changed" when really only the labeling did.

## Pattern 3 — architectural-correction "Two-Pass" dedicated section with Mermaid
When the correction is structural (C3 here: two vtable slots are not "Read then PostLoad" but "Pass 1 reads species + creates chain via Python, Pass 2 reads body + walks chain"), give it its own H2-level section near the top of the body (after the envelope/header tables, before the per-class wire layout). Use a Mermaid `flowchart TD` diagram and **highlight the data-dependency nodes** with `style ... fill:#ffd`:

```mermaid
style P1E fill:#ffd
style P2G fill:#ffd
```

P1E = "SetupProperties → CREATE SUBSYSTEM CHAIN"; P2G = "Walk ship+0x284 list per-subsystem state". The yellow ties the diagram's narrative to the prose ("Pass 2 cannot run until Pass 1's Python step creates the chain").

## Pattern 4 — closed-open-question disposition
For R3 ("orientation IS quaternion" closing a prior Open Question): do NOT leave the old open question in the Open Questions section. Drop it entirely. Add inline `[R3 confirmed]` tags in the wire-layout table rows where the change applies (`orientation_w/x/y/z`). The frontmatter row carries the high-confidence evidence; the body inline tag tells the next reader "we already settled this."

If you want to record the historical decision, drop a single sentence in the rationale near the table: "FUN_00816390 (Shoemake matrix→quat) and FUN_008162B0 (quat→3×3 matrix) settle the format definitively."

## Pattern 5 — cross-doc disagreement resolution with re-check flag
For R4 ("FUN_005A2030 = ShipReadSpecies, NOT GetPlayerSlotFromObjID"): the resolution flag belongs in TWO places:

1. Inline `[R4: not GetPlayerSlotFromObjID]` next to the address in the pipeline diagram body.
2. In the Cross-doc reconciliation section: "**objnotfound-requestobj-enterset-wire-format.md** (mid #18, pending) — may identify FUN_005A2030 as GetPlayerSlotFromObjID. R4 settles this in favor of the present doc's ShipReadSpecies identity; flag for objnotfound-requestobj-enterset validation."

The "may identify" hedge is important — the conflicting doc hasn't been re-checked yet, so don't assert what it currently says. The flag belongs in the dependent doc's next-pass validation, not this one's mod.

## Pattern 6 — global-conflation R1 with split-table presentation
For R1 ("two DAT_ globals were conflated"): place the disambiguation INLINE in the existing factory section as a `> R1 caveat:` block, not as a new section. Two-row split:

> `factory_class_id` is resolved via the **factory registry** at `DAT_0099A578` (factory vtable) + `DAT_0099A584` (bucket array)...
> `object_id` is checked against the **object hash table** at `DAT_0099A67C` via `ObjectLookupByID(0, object_id)`...

This is lighter touch than a dedicated subsection — appropriate when the correction is a wording split, not a binary-semantic change.

## Pattern 7 — gate-refinement R2 with practical-impact note
For R2 ("the duplicate check is a two-part gate, not just 'found'"): include both the binary truth and the practical impact:

> Reality: the function returns the object IFF found AND its class category equals 0x8002 (game object). Returns NULL for non-game-object IDs (which the caller treats as "OK to create"). **In practice this doesn't change observable behavior** — all ObjCreate'd objects are game objects — but the wording should reflect the gate.

The "practical-impact" sentence is essential — without it readers assume the correction is load-bearing; with it, they understand the refinement is a precision improvement, not a behavior change.

## Pattern 8 — cross-companion ahead-of-pass refinement flag
When this doc anchors a fact (`+0x74`) that contradicts a JUST-VALIDATED companion (object-replication.md says `+0x7C`, validated 5 days ago by the same agent), document the impact but DO NOT modify the companion. Use the Cross-doc reconciliation section to flag the next-pass refinement and explicitly batch it:

> **object-replication.md** (mid #9, just validated 2026-05-28) — cites PlayerSlot array base at MultiplayerGame+0x7C in its host-relay loop pseudocode. This doc anchors +0x74 via MultiplayerGame_Ctor directly. **Surface for next-pass refinement** on object-replication.md (do not modify this pass — batched at family close).

The "batched at family close" callout aligns with the protocol-family pass discipline. The companion doc's `validated` date stays fresh; only its next pass will reconcile.

## When to use
- Mid-tier wire-format doc where the V5 packet carries:
  - ≥2 material corrections (wire-order, struct-anchor, architectural)
  - ≥1 refinement that closes a prior open question
  - ≥1 cross-doc disagreement that resolves in the present doc's favor
  - A Two-Pass / forced-by-data-dependency architectural finding

## Why
- Pattern 1 prevents OpenBC implementers from treating a wire-order fix as a wire-content change
- Pattern 2 prevents readers from concluding the binary changed between docs
- Pattern 3's Mermaid + highlighted-node convention surfaces the data dependency at a glance
- Pattern 4 keeps Open Questions section honest (it's a debt list, not a history)
- Pattern 5 splits the resolution evidence (here) from the dependent fix (there) cleanly
- Pattern 6 keeps light-touch refinements inline (don't over-section)
- Pattern 7 prevents alarm-fatigue ("this gate fix doesn't change behavior")
- Pattern 8 respects the family-pass discipline (don't mutate already-validated companions mid-pass)

## How to apply
At the top of the file: 3-correction NOTE block with C1/C2/C3 + 4 refinements summary. Wire-layout table: inline `[Cn]` and `[Rn]` tags in the affected rows. Two-Pass architecture: dedicated H2 section with Mermaid + highlighted data-dependency nodes. R3 closed: drop the question from OQ, add inline tag. R4 cross-doc: flag in Cross-doc reconciliation section, point at the dependent doc's next pass. R1 + R2: light-touch `> R1 caveat:` blocks inline in existing sections. Cross-companion next-pass refinements: list explicitly in Cross-doc reconciliation, mark batched-at-family-close.

## Related
- [[architectural-reframe-render-patterns]] — when the correction is a count-of-mechanisms flip (here it's a within-mechanism architectural split)
- [[thin-handler-index-render-patterns]] — sister doc (object-replication.md) pattern; this doc inherits its dispatch claims
- [[load-bearing-correction-disambiguation]] — when a single correction is the disambiguation of two conflated globals (R1 here is the lightweight version)
- [[cross-source-doc-render-patterns]] — for the SpeciesToShip/Torp/System cross-source-tagged tables
