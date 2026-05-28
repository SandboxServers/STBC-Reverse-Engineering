---
name: verified-leaf-with-cascade-render-patterns
description: 8 render patterns for the SECOND protocol-family doc to reach `verified` when it combines (a) zero wire-format changes, (b) 3 minor non-wire corrections including a cascade from earlier mid-tier docs, and (c) 4 newly-created Ghidra functions. Different shape than first-verified-leaf (collision-effect-protocol.md): minor corrections actually surface as a `> [!NOTE]` correction list AND need inline disambiguation blocks, not just an inline corrections summary.
metadata:
  type: feedback
---

# Verified-Leaf-with-Cascade Render Patterns

Learned from set-phaser-level-protocol.md (protocol leaf #16, second protocol doc to clear
`verified`). Different render constraints from first-verified-leaf
[[first-verified-leaf-render-patterns]] (collision-effect-protocol.md, leaf #15): this one
inherits corrections from earlier docs in the family (cascade from mid #13 / leaf #14)
AND has 4 newly-created functions to disclose. Both fit a `verified` status but produce
different doc shapes.

**Why:** verified-tier ≠ "no corrections" — it means every claim has high or medium
confidence with a documented reason. A doc with 3 minor non-wire corrections + 4 created
functions + 0 wire-byte changes still qualifies, but the render must surface the
corrections cleanly without making it look `partial`.

**How to apply:** when a leaf protocol doc validates clean on the wire but inherits
class-hierarchy / string-typography / helper-name corrections from earlier docs, AND
multiple SWIG-callback functions had to be `create_function`-ed, use this pattern.

## Pattern 1 — Multi-correction NOTE block triage (C1/C2/C3 inline)

When the doc has 2-3 minor corrections, the top-of-doc NOTE lists each by code with a
one-line summary. Don't bury them — but don't promote them to body sections either (that's
what `partial` would look like).

```
> [!NOTE]
> This doc is `status: verified`. ... Three minor corrections in this pass:
> **(C1)** hierarchy cascade from mid #13 / leaf #14 — there is no `TGSubsystemEvent`;
> 0x101 IS TGEvent itself.
> **(C2)** registration-string typography: the binary string is `"... :: ..."` (single
> colon-colon with surrounding spaces); Ghidra's symbol-name mangler renders the spaces
> and colons as underscores.
> **(C3)** `FUN_xxxxxxxx` is already renamed `TGFactory_DeserializeObject` in the Ghidra DB.
```

**Why:** the NOTE is the "what changed since the last validation" log; a verified-tier
reader needs to know what was wrong before. Putting each correction inline (no separate
"Corrections Applied" section) keeps the doc's body structure intact.

**How to apply:** if corrections are minor (no wire byte changed, no behavior gate flipped),
list them in the NOTE with (C1)/(C2)/(C3) tags. If they're material, escalate to dedicated
body sections (use [[load-bearing-correction-disambiguation]] instead).

## Pattern 2 — Cascade-correction has its OWN NOTE block in body

When a correction comes from cascade (an earlier doc was wrong, this doc was wrong the same
way), insert a `> [!NOTE]` block at the section where the wrong claim was. Don't just
silently fix it — name the cascade source. Future readers + sibling-doc maintainers need to
see the trail.

For set-phaser-level-protocol.md:

```
### Class Hierarchy (Corrected — C1)

> [!NOTE]
> Previous versions of this doc depicted an intermediate `TGSubsystemEvent (factory 0x101)`
> class. That class **does not exist** — `0x101` is the factory ID of `TGEvent` itself
> (confirmed: zero occurrences of the string `"TGSubsystemEvent"` in stbc.exe). The
> previous "factory 0x02 size 0x28" annotation for TGEvent was also wrong: 0x02 is the
> TGObject class ID (a separate ancestor in the IsA chain), not a factory ID. See mid #13
> [tgobjptrevent-class.md](tgobjptrevent-class.md) and leaf #14
> [pythonevent-wire-format.md](pythonevent-wire-format.md) for the originating fix.
```

**Why:** the cascade source matters for traceability. If another doc later re-introduces
the same wrong claim, the in-body NOTE points back to the chain that fixed it.

**How to apply:** for every cascade correction, mark the section header with
`(Corrected — Cn)` AND insert an in-body NOTE block citing the originating docs.

## Pattern 3 — String-typography correction gets its own in-body NOTE block (C2 pattern)

C2-style corrections (the binary string is X, the Ghidra symbol is Y) need explanation
because future readers will see the Ghidra symbol and re-introduce the error. Don't bury
this in the NOTE block at top — repeat it in body at the section the symbol appears.

For set-phaser-level-protocol.md `### MultiplayerGame (registered in ctor at ...)`:

```
> [!NOTE]
> **C2 — registration-string typography.** The binary string at `0x00959F1C` is
> `"... :: ..."` — single double-colon with **spaces** on both sides. Ghidra's
> auto-generated symbol name renders this as `s_..._..._..._00959f1c` because the
> label-name mangler encodes spaces and colons as underscores; the underlying string is
> the spaced form. Previous versions of this doc carried the mangled `"...::..."`
> form — that was the Ghidra symbol, not the binary string.
```

**Why:** Ghidra's symbol-name mangling is non-obvious; future agents AND humans will
re-introduce the mangled form if the body doesn't explain it.

**How to apply:** for every Ghidra-symbol-vs-binary-string conflict, add an in-body NOTE
block at the section that cites the string. Include the address of the string, the binary
form, the Ghidra symbol form, and one sentence about why they differ.

## Pattern 4 — "CREATED this pass" inline tag in Related Functions table

When 4 functions were `create_function`-ed during validation, the Related Functions table
gets a per-row `CREATED this pass` note (not a separate column — that would dilute the
table). Same for renames: `(formerly documented as ...)`.

```
| 0x00574180 | PhaserSystem__SetPhaserLevelHandler | Receiver: stores level byte from event into +0xF0 (CREATED this pass) |
| 0x006D6940 | TGCharEvent__WriteToStream | Network serialization (base + charValue byte) — CREATED this pass |
| 0x006D6200 | TGFactory_DeserializeObject | Factory-based event construction from stream (formerly documented as `ReadObjectFromStream`) |
```

**Why:** the reader needs to know which addresses are now newly anchored in Ghidra — those
become reliable cross-references for later docs.

**How to apply:** "CREATED this pass" suffix in the Role column for newly-created
functions; "(formerly documented as `X`)" for renames where the doc body might still cite
the old name elsewhere.

## Pattern 5 — Ghidra Annotations section split: Functions Created + Renamed + Plates

When 4+ functions were created in a single pass (vs. first-verified-leaf's 3 simple
subsections), the Ghidra Annotations Applied section needs three subsections:

```
### Functions Created
| Address | Name | Size | Reason |
| ... | ... | 34 bytes | Undefined-in-DB; xref X from Y was DATA-only |

### Functions Renamed
| Address | New Name |

### Plate Comments
Four plate comments were added — one on each newly created function — tagged
`[v5-validated 2026-05-28]`. Each plate documents the gate logic ...
```

**Why:** the verified-leaf #15 pattern (3 short subsections, plates one-liner) doesn't
scale when there are 4 distinct creations with different reasons. Adding a `Reason` column
discloses *why* each was undefined (vtable slot? handler-table reg? both?).

**How to apply:** for 4+ created functions, use the `Reason` column. For 1-3 created
functions, the simpler verified-leaf #15 shape (no table, just inline mentions) is fine.

## Pattern 6 — Universal-pattern systematic disclosure

When the same "undefined SWIG/handler-table functions" pattern keeps recurring across leaf
docs (#13, #14, #15, #16 all hit it), name the pattern in the Ghidra Annotations
preamble. Don't restate it from scratch every time:

```
This validation pass made the following annotations against the Ghidra DB. The four CREATED
functions all had valid prologues but no defined function in the DB — their xrefs are
DATA-only (vtable slots and handler-table registration entries), so the analyzer never
entered them. This is the same systematic pattern observed on leaves #13, #14, and #15
(TGObjPtrEvent, PythonEvent, CollisionEffect): SWIG vtable callbacks and event-table-registered
handlers stay undefined until manually created.
```

**Why:** the pattern is now established across 4 protocol leaves. Future leaves
(#17 DeletePlayerUI, #18 ObjNotFound/RequestObj/EnterSet) will likely hit it again.
Cross-naming the pattern lets readers (+ future doc authors) recognize it.

**How to apply:** when the same observation appears in 3+ leaf-tier docs, write a one-line
"this is the systematic X pattern" disclosure that names the prior occurrences. Don't
re-derive it.

## Pattern 7 — Open Questions section with promotion-path framing

Verified-tier docs CAN have Open Questions — they just can't be load-bearing. Frame each as
"low-priority + promotion path":

```
## Open Questions

Two low-priority items remain after this pass:

1. **Frequency stat is session-dependent.** The doc previously claimed "~33 per 15-min
   stock session". Relay-audit observed 10 events in 21 minutes on a 2-player session.
   These numbers are not contradictory — phaser-level toggles are a player input that
   varies widely by playstyle. The frequency line is now flagged
   `[low-confidence — session-dependent]`. Promotion path: if a multi-session corpus
   becomes available, replace with a min/max/median per minute.
2. **TGEvent base layout fields at +0x14 / +0x18 / +0x1A / +0x1C / +0x20 / +0x24.**
   These are inherited from TGEvent and not modified by TGCharEvent, so they were not
   independently re-anchored this pass. ... but a foundation-tier TGEvent doc would
   tighten the cross-anchor.
```

**Why:** first-verified-leaf [[first-verified-leaf-render-patterns]] said "no Open
Questions blocking section". That rule was for collision-effect-protocol.md which had
zero open items. When verified-tier DOES have open items, surface them — just frame the
promotion path so they don't read as blockers.

**How to apply:** if 0 open items, follow first-verified-leaf (no Open Questions section).
If 1-3 low-priority open items, add the section with promotion-path framing. If 4+,
consider whether the doc should be `partial` instead.

## Pattern 8 — Inline `[low-confidence — session-dependent]` flag on Overview line

A frequency stat that varies wildly by session shouldn't be dropped — it should be tagged
inline so the reader knows not to rely on it for math:

```
**Frequency**: infrequent (relay-audit observed 10 per 21min, 2-player) `[low-confidence — session-dependent]`
```

**Why:** verified-tier requires "confidence: high or medium with documented reason". A
session-dependent stat is medium confidence at best — but rather than promoting it to a
full evidence row, an inline tag in the body suffices when the stat is descriptive (not
load-bearing).

**How to apply:** for stats that vary by playstyle / session / map, tag inline rather
than dropping. Frame the confidence reduction explicitly: `[low-confidence — X]` where X
names the variability source.

## What NOT to do

- Don't give each correction its own body subsection — that's a `partial` doc pattern. Use
  inline NOTE blocks at the section the correction applies to.
- Don't re-derive the "undefined SWIG callback" pattern from scratch — name it as
  systematic if it appears in 3+ prior leaves.
- Don't drop session-dependent stats — tag them inline with `[low-confidence — X]`.
- Don't pad evidence rows. ~15 rows for an 18-byte wire-format leaf is right; more rows
  means you're padding inherited claims (TGEvent base layout). Cross-anchor inherited
  claims to companion docs instead.
- Don't update CLAUDE.md mid-family-pass for a single doc — batched at family close.

## Pattern cross-refs

- [[first-verified-leaf-render-patterns]] — alternative shape for `verified` leaf with
  inline-corrections-summary instead of NOTE-block triage
- [[leaf-cascade-render-patterns]] — the doc that ESTABLISHED the cascade this doc
  CONSUMES (PythonEvent leaf #14 set the "0x101 = TGEvent" precedent)
- [[load-bearing-correction-disambiguation]] — escalation pattern for MATERIAL corrections
  (not the minor ones this doc handles)
- [[v5-named-function-convention]] — naming-script-drift convention used here for C3
  (FUN-name → renamed-in-DB)
