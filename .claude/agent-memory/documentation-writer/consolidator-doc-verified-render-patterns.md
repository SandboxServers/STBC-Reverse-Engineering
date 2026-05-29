---
name: consolidator-doc-verified-render-patterns
description: Render patterns for CONSOLIDATOR/HUB mid-tier docs (8-section combat-mechanics-style) reaching `verified` with ZERO material corrections via foundation-doc inheritance + fresh-binary-anchored novel sections + 100% hardpoint-script match. 4th doc this session to clear `verified`.
metadata:
  type: project
---

# Consolidator Doc — `verified` Render Patterns (combat-mechanics-re.md)

Render patterns for the fourth gameplay-family doc to reach `verified` this session, and the first **consolidator/hub doc** (not foundation, not pure leaf) to do so. Key distinction: this is a doc whose value is **consolidation of validated foundation findings + 2 novel sections with their own fresh anchors** — not a standalone wire-format or class-identity doc.

## Distinct from prior `verified` shapes

- alby-rules-cipher-analysis.md (networking #1 verified): standalone leaf, fresh full validation, 2 clar + 2 R refinements
- ack-outbox-deadlock.md (networking verified): bug-doc leaf
- ai-architecture.md (gameplay verified): foundation doc
- **combat-mechanics-re.md** (gameplay mid #7 verified, this pass): **consolidator/hub mid** with mixed inheritance + novel anchoring

## Patterns specific to consolidator/hub verified renders

### Pattern 1: NOTE-block triage names the inheritance vs novel split

> "**v5 verified pass — ZERO material corrections.** Cleanest gameplay-family doc validated to date. 6 of 8 sections inherit from already-validated foundation docs; sections 6 (Tractor Beam) and 7 (Ship Death) freshly binary-anchored this pass. 23 unique addresses verified, 7 constants byte-confirmed, 100% Sovereign hardpoint match against `reference/scripts/ships/Hardpoints/sovereign.py`."

Three counts in the headline:
1. Section split (inheritance vs novel) — sets reader expectation: "this doc isn't redoing everything"
2. Address count (23 anchored)
3. Constant count (7 byte-confirmed)
4. Plus: external-corpus match-rate (100% hardpoint-script match) — when applicable

Clarifications immediately follow as Clar-N bullets in the NOTE.

### Pattern 2: Per-section header tag distinguishes inheritance from fresh anchoring

Sections inheriting foundation findings:
```
## 1. Damage Pipeline [v5-validated 2026-05-28 — cross-anchor: damage-system.md]
```

Sections freshly binary-anchored:
```
## 6. Tractor Beam [v5-validated 2026-05-28 — freshly binary-anchored this pass]
```

Sections inheriting external corpus:
```
## 8. Sovereign Class Reference Values [v5-validated 2026-05-28 — 100% script-match against reference/scripts/ships/Hardpoints/sovereign.py]
```

The reader can tell at a glance whether a section was re-verified independently or borrows authority from a sibling.

### Pattern 3: Negative claims get xref-enumeration treatment

The "tractor beam applies no direct damage" claim is rendered as a separate subsection with explicit xref enumeration:

> This is confirmed by **xref enumeration of DoDamage (`0x00594020`)**: the complete xref set is exactly `{FUN_005952d0, FUN_005af420, FUN_00593650}` (collision multi-contact, weapon hit, collision single-point). Zero tractor mode handler entries. This is a negative-claim verification — the absence of an xref is the proof.

Frontmatter row uses `address: null` + `note:` explaining the absence-of-xref proof method. Pattern established for "X does not happen" claims that don't have a positive address.

### Pattern 4: Clarifications integrate inline at the actual table row

Clar-1 ("ShieldGenerator RepairComplexity = 2.0, was —"): the Section 8 table row is updated with bolded `**2.0**` + an inline `[Clar-1]` tag.

Clar-2 ("CloakTime = 5.0f"): the Section 3 globals table gains a Value column with bolded `**5.0f**` + an inline `[Clar-2]` tag.

The bolded value + inline tag at the point-of-correction lets the reader see WHAT changed without leaving the table. The NOTE block at the top explains WHY.

### Pattern 5: Open Questions section closes the doc when clarifications are low-severity but multiple

When the validation memo carries 3+ OQs (cross-anchor follow-ups, not material), include a brief `## Open Questions (low-priority, deferred)` section. Three-bullet format: OQ-N tag, statement, promotion path (which sibling doc closes it). Different from `partial`-shape OQ section: low-priority framing + verification this didn't block `verified` status.

### Pattern 6: Section 9 OpenBC Corrections Summary preserved verbatim

For consolidator docs that already carry a "what OpenBC got wrong" summary table, do NOT rebuild it during v5 — preserve it. Add a one-line preface noting it still carries forward unchanged. The table is referenced by clean-room implementers and the wire-level facts in it are anchored by the section-1-through-8 evidence above.

### Pattern 7: Companion list spans gameplay + protocol + networking

A consolidator doc's companion list crosses doc families:
- Gameplay foundations (damage-system, shield-system, weapon-firing-mechanics, power-system, cloaking-state-machine, repair-tractor-analysis)
- Protocol leaves (collision-effect-protocol leaf #15, cf16-explosion-encoding leaf #21)
- Networking leaves (ship-death-lifecycle, implicit via Section 7 cross-anchor)

8 companions total — higher than typical leaf (~3-4) or foundation (~2-3). This is the consolidator signature.

## Verified-status criteria for consolidator docs

A consolidator doc qualifies for `verified` when:
1. ZERO material wire/formula/address errors (corrections column empty)
2. All inherited sections trace to foundation docs already validated (not stale)
3. All novel sections (those without a sibling foundation) have FRESH binary anchors this pass
4. External corpus claims (hardpoint scripts, etc.) verified at 100% match rate
5. Clarifications are non-load-bearing (cosmetic table omissions, value-fill-ins for symmetry)
6. OQ items are explicitly low-priority and don't block any reader who treats the doc as authoritative

`partial` would be appropriate if any of: novel section lacks fresh anchor, hardpoint match-rate < 100%, or a clarification touches a wire-format byte.

## Tracker-row shape (for batched update later)

When this doc's row is updated in `docs/gameplay/v5-validation-status.md`:
- Status: `verified`
- Date: 2026-05-28
- Corrections: 0 / Clarifications: 2 / OQ: 3
- Inline: "Consolidator doc; 6/8 inherit, sections 6+7 freshly anchored, 23 addresses verified, 100% sovereign.py match. Clar-1 RepairComplexity table fill, Clar-2 CloakTime value fill."
