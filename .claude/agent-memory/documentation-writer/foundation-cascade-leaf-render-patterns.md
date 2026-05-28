---
name: foundation-cascade-leaf-render-patterns
description: 7 patterns for rendering a leaf doc when ALL the v5 corrections come from a foundation-doc cascade (no new wire-byte changes) — the foundation already corrected ship-slot identities and this leaf must update its 12-row catalog table to match
metadata:
  type: feedback
---

# Foundation-cascade leaf render patterns

Leaf docs in this protocol family are usually the doc where corrections SHOW UP — they have the per-byte detail and the most surface area to be wrong. **Pattern shift**: when the *foundation* doc was the one that got corrected first (here: `wire-format-spec.md` C1, validated 2026-05-28), the leaf's wire format is bytewise unchanged but the leaf's *human-readable identity column* in a catalog table goes stale.

Learned from `subsystem-integrity-hash.md` (protocol leaf #19) — 1 material correction (6 stale labels in the 12-row hash slot table, cascading from foundation #1) + 4 clarifications, 0 wire-byte changes.

Apply when:
- Doc has a catalog-style table that lists per-row identities (subsystem names, class names, etc.)
- Foundation doc's slot/identity authority was corrected in an earlier v5 pass
- The leaf's offset math is internally consistent but used stale names
- Wire format and algorithm are unchanged

## Pattern 1 — NOTE block leads with cascade framing, not "found N corrections"

The pre-v5 reader's mental model has the **leaf** as the canonical authority for the catalog table. Re-framing the NOTE to say "C1 rewrites the table to match foundation #1's corrected ship-slot identities" makes clear:
- Where binary authority actually lives now (foundation)
- That the leaf's *offsets* were always right
- That the *labels* are what changed

Don't lead with "6 corrections" — lead with "ONE material correction (slot subsystem-identity labels)" and add the explicit qualifier "Hash function reads correct offsets; only the human-readable identity column was stale." Reader needs that disambiguation up front or they will worry about wire-format breakage.

## Pattern 2 — Dedicated `## C1 — ...` section as the SECOND `##` heading (right after Overview)

Place the correction section EARLY because:
- It is the entire point of the v5 pass
- The corrected table is referenced by every downstream section
- Skip-readers (modders, OpenBC implementers) bail after the NOTE + first 2 headings

Body shape:
1. One-paragraph cascade explanation (cite foundation doc + its validation date)
2. **Key archaeological finding** subsection explaining WHY the offsets stayed valid (here: container-aliasing pattern via `FUN_005b5d00` zero-fill range)
3. Corrected table with **bolded rows** indicating which labels changed
4. "Downstream impact" subsection explicitly listing any prose elsewhere in the doc that was wrong AS A CONSEQUENCE of the stale labels (here: line 129 negative claim)

The container-aliasing finding is what justifies the "offsets right, labels wrong" framing. Make that subsection load-bearing.

## Pattern 3 — Bolded-row catalog table with side-by-side "Prior Label" column

For catalog corrections where N of M rows changed, render the table with:
- New canonical column (bolded entries on the changed rows)
- "Prior Label" column listing what the pre-v5 doc said
- Authority citation IMMEDIATELY after the table (one-liner naming the foundation doc + its validation date)

This lets a reviewer scan for differences without reading prose. Don't render the foundation doc's full table here — render the leaf's table with the leaf's column structure, but with corrected identities.

## Pattern 4 — Negative-claim correction must be called out separately

If the catalog correction also invalidates a *negative claim* in the prose ("X does NOT appear in the hash"), give it its own subsection. The negative claim is the thing a clean-room reimplementer would have hardcoded as a skip in their implementation — getting it wrong silently breaks parity.

Format:
```
### Downstream impact — line N negative claim is wrong

The pre-v5 body line N read:
> [verbatim quote]

This statement is wrong on **two** counts:
1. [first wrong assertion]
2. [second wrong assertion]

Corrected statement (replace line N):
> [verbatim replacement]
```

Here the line 129 claim "Repair does not appear in the hash" was wrong because (a) Shield was at +0x2C0, not Repair, and (b) Repair is at +0x2D8 and DOES appear. Two errors in one sentence — call them out separately so a reviewer can verify each independently.

## Pattern 5 — Clarifications as `### Clar-N — ...` headings inline at their context

For non-correction wording refinements (precision details, address-vs-symbol equivalence, signed-vs-unsigned shift), place them as `### Clar-N — short headline` subsections **directly under the section they refine**, not in a centralized "Clarifications" bucket at the bottom.

Examples from this pass:
- **Clar-1** (event-type write offset) -> under the Receiver section
- **Clar-2** (torpedo int-to-float cast) -> directly under the torpedo step in HashWeaponSystem pseudocode
- **Clar-3** (`&ET_BOOT_PLAYER` vs `0x008000F6` equivalence) -> under the Receiver section, after Clar-1
- **Clar-4** (signed SAR) -> under the Sender section

Reader gets the precision detail at the exact point of confusion. Centralized clarification buckets force a re-read.

## Pattern 6 — Container-aliasing pattern deserves its own subsection

When the leaf's offset math is "two aliases for the same memory range", explain the aliasing pattern in a dedicated subsection (here: under "Wire Encoding"). This is the kind of insight that makes future cross-doc reconciliation easier:

> `ship+0x27C` is a sub-object created by `FUN_005b5d00` with vtable `0x008944c8`. The ctor zero-fills `param_1[1..0x18]` — exactly the range `ship+0x280..ship+0x2DC` that overlaps the named-slot table at `ship+0x2B0..0x2DC`. After `Ship__SetupProperties` populates the named slots, the hash function reads those same pointers through the container alias.

Future docs that hit "wait, why does this code use offset +0x34 here but +0x2B0 there?" can be answered by linking to this subsection.

## Pattern 7 — `## Kick Path` section deserves its own heading for action chains

When a leaf documents an event chain that crosses multiple files (receiver -> EventManager -> handler -> message ctor -> broadcast), give it its own `## Kick Path` section with:
- Indented action flow (`->` arrows)
- Each step annotated with its address
- Footnote naming any function CREATED in Ghidra this pass + cross-confirmation source

Here the kick path was a 6-step chain ending at `MultiplayerWindow_BootPlayerHandler` (CREATED this pass, cross-confirmed via `reference/decompiled/04_ui_windows.c` line 2027). Surfacing the "created this pass" disclosure inline at the section keeps the reader from wondering why the doc renamed the function.

## What NOT to do

- Don't restructure the body to reorder per-function sections. Keep the original section order — readers may have inbound links.
- Don't add a centralized "Corrections" section at the top above the NOTE. The NOTE block IS the correction summary.
- Don't promote Clar-N items to body subsections without C-tagging. Reviewers need the C/Clar distinction to triage severity.
- Don't drop the "Decompiled Source Reference" table even if line numbers are stale — flag it as OQ-N pending re-verification instead. Removing the reference loses the breadcrumb for future re-validation.

## Tracker integration shape (when leaf cascades from foundation)

When closing §4 disagreement rows that resolve because of a foundation-pass + leaf-pass combination:

- §4 #X: `**CLOSED (YYYY-MM-DD, leaf #N):** binary truth — [statement]. [Foundation doc] was already corrected in foundation pass §6.M (rationale); [leaf doc] [confirmation/cascade]. Confirmed via [Ghidra method] + ground-truth from [other function]. See [leaf doc] §[section].`

The "binary truth" + "foundation already" + "leaf cascaded" structure makes the closure auditable. Reviewers can verify each pass independently.
