---
name: command-message-triad-render-patterns
description: 8 patterns for rendering a leaf doc when v5 surfaces (a) a command-message-vs-event-message architectural distinction, (b) a physical-constant re-identification (DAT was X, semantically Y), and (c) closure of a §4 cross-doc conflict in the same pass
metadata:
  type: feedback
---

# Command-message-triad leaf render patterns

Learned from `objnotfound-requestobj-enterset-wire-format.md` (protocol leaf #18 — fourth
protocol-family leaf). The validation surfaced 3 categorical findings:

1. The triad uses raw stream primitives only — **bypasses TGFactory_DeserializeObject** — and
   are RPC-style command messages, NOT event-bearing transports. New cross-cutting
   "command-vs-event-message" distinction joining sibling-leaf framing.
2. A data constant (`DAT_008e5c18`) was re-identified from "small positive HP threshold" to
   **`FLT_MAX`** — the DamageableObject **undamaged** sentinel. The gate semantic INVERTS
   (was "reject if below threshold"; truth is "accept only if exactly FLT_MAX, i.e. never
   damaged"). This is a physical-constant re-identification with cascading OpenBC impact.
3. A second data constant (`DAT_008d8ab8`) was re-identified from "default space combat set
   name" to the literal string `"warp"` — the in-warp-tunnel sentinel. Sender gate inverts:
   sender SUPPRESSES emission when in the tunnel (the constant's set), opposite of the pre-v5
   reading.

Plus this pass closed `v5-validation-status.md §4 #1` (the FUN_005a2030 conflict between
`objcreate-serialization.md` and the leaf — binary sided with objcreate-serialization.md)
and `§4 #15` (breadcrumb header added on re-render).

## When this shape applies

- A leaf v5 pass finds the doc has 3 material wire/value corrections + 2 address-mapping
  corrections + 2 clarifications
- One of the corrections is "this constant is FLT_MAX, not threshold" — gate inversion
- One of the corrections is "this constant is literal string X, not the role we thought" —
  semantic inversion of the gate it controls
- The doc cluster has 3 sibling opcodes that share a structural property
  ("command messages — bypass TGFactory") that contrasts cleanly with TGFactory-event-bearing
  sibling-leaf opcodes (0x06 / 0x12 / 0x15 / 0x17)
- The pass closes a §4 cross-doc conflict with binary arbitration

## The 8 patterns

### Pattern 1: NOTE-block triages by **category**, not by severity

For 5 corrections, the NOTE block opens with a bolded count line: **"Three material
wire-format / data-constant corrections" + "two address-mapping corrections"**. Then bullets
in (C1)/(C2)/(C3)/(C4)/(C5) order with a one-line summary each. The 2 clarifications get
(Clar1)/(Clar2) tags after the corrections list. Source evidence memo path is named at
the end of the NOTE so reviewers can drill down.

Rule: don't try to rank corrections by severity in the NOTE; group by **kind** (wire-format
/ data-constant / address-mapping / clarification).

### Pattern 2: Dedicated "Command Messages vs Event Messages" subsection IMMEDIATELY after Overview

When validation surfaces that the doc's opcodes share a structural property that contrasts
with sibling leaves, give it a dedicated `##` subsection AT THE TOP of the doc (between
Overview and the first opcode walkthrough). Carries a per-opcode comparison table:

| Opcode | Style | Deserialization path |
|--------|-------|----------------------|
| 0x06 PythonEvent | Event-bearing | `TGFactory_DeserializeObject` ... |
| **0x1D ObjNotFound** | **Command** | **Raw `stream->vtable[+0x68]` ReadInt only** |
| ... |

The contrast row bolding (the docs's OWN opcodes are bolded, not the contrasting siblings)
makes the categorical distinction visually clear. Use this pattern when 3+ opcodes share a
structural property that contrasts with already-documented siblings.

### Pattern 3: Per-correction `###` subsection placed AT THE CONTEXT, not at the bottom

C1 (string encoding) goes inside the 0x1F Wire Format section — right after the byte table,
before the handler behavior. C3 (FLT_MAX gate) goes inside the 0x1E handler body — right
after the pseudocode, as a "C3 — ..." `###` subsection. C2 ("warp" re-interpretation) gets
its own `###` under the 0x1F handler. C4 / C5 (address corrections) get a SHARED
`## Critical Correction: Function Address Map` section near the bottom.

Rule: place each correction subsection IN the section the correction affects, with `[v5-validated YYYY-MM-DD]` tag. The READER follows the correction to its native context, not to a remote appendix.

### Pattern 4: FLT_MAX / physical-constant gate inversion gets explicit BEFORE/AFTER mechanism trace

When a constant is re-identified from "threshold" to "sentinel", the correction subsection
must spell out the mechanism in 3 bullets:

- The ctor initializes the field at `X`
- Damage application DECREMENTS / MUTATES the field from `X`
- The gate `X <= field` succeeds only when field is exactly `X` — the never-modified state

Then a separate "**OpenBC implication:**" paragraph that names the practical consequence
(e.g., "0x1E does not re-send damaged objects; late-join hydration requires a different
mechanism"). The practical-consequence paragraph is what distinguishes a categorical
correction from a low-stakes typo and is what gets quoted in cross-doc references.

### Pattern 5: "warp" sentinel / string-constant re-identification rewrites the section heading

When a constant was misnamed and its semantic inverts, the SECTION that documented it under
the wrong name gets renamed and rewritten — not appended-to. Pre-v5 doc had `### Set Name:
The "Space" Set`; v5 doc has `### C2 — DAT_008d8ab8 is the literal string "warp", not a
"default space combat set name"`. The new section quotes the old description, then shows
the memory dump (`inspect_memory_content` output bytes), then re-derives the semantic.

Don't preserve the old heading. The "C2 — ..." heading IS the new section title. Body
under it carries the inversion explanation.

### Pattern 6: Address-mapping corrections (C4/C5) collected in ONE shared subsection

Pre-v5 doc has a Function Addresses table with 2 wrong rows. The new doc gets a dedicated
`## Critical Correction: Function Address Map` section near the bottom (just before
OpenBC Implementation Notes) with C4 and C5 as paired `###` subsections under it. Each
sub-section has the "Pre-v5 doc claimed: X" / "Binary truth: Y" form. C4 also cross-links
to the §4 #N closure ("This resolves §4 #1 — binary authority sides with
objcreate-serialization.md").

The corrected Function Addresses table at the doc's bottom carries inline annotations:
`| 0x006a19a0 | GetPlayerSlotFromObjID **(C4 — corrected; was 0x005a2030)** |` and
`| 0x006a7770 | MakeObjIDFromPlayerSlot (INVERSE; **not called by the triad**, C5) |`.

### Pattern 7: §4 closure tagged in the body where it lands, NOT just in tracker

When the leaf closes a §4 conflict, the in-body correction subsection that did the closure
carries a parenthetical: "(This resolves [v5-validation-status.md](v5-validation-status.md)
§4 #N — binary authority sides with [other-doc].md)". The tracker §4 row is also marked
"CLOSED (YYYY-MM-DD, leaf #N): ..." with the binary truth and a back-link to the leaf's
§C# subsection.

Both pointers are needed: the leaf reader knows the §4 conflict was resolved by this pass;
the tracker reader knows where the binary-truth resolution lives.

### Pattern 8: Negative claim for "bypasses TGFactory" as a top-tier evidence row

The "triad uses raw stream primitives only" claim is a NEGATIVE claim — there are no calls
to `FUN_006D6200`. Add it as a frontmatter evidence row with `address: null`, `function:
null`, `confidence: high`, and a `note:` describing what was searched ("Verified by reading
0x006a0490 / 0x006a02a0 / 0x006a05e0 bodies in full — no calls to FUN_006d6200 or to any
TGFactory helper. Contrasts with 0x06 / 0x12 / 0x15 / 0x17 which all go through TGFactory.").

This anchors the categorical claim that drives Pattern 2 (the Command vs Event subsection).
Without the evidence row, the categorical claim is body-only and can't be cited by
downstream docs.

## What NOT to do

- Don't put the "Command vs Event" subsection in an appendix — it's the categorical framing
  that orients the whole doc.
- Don't try to keep the pre-v5 "Space Set" subsection by appending the C2 correction to it —
  rewrite the heading.
- Don't put address-mapping corrections inline in the Function Addresses table only — give
  them their own `## Critical Correction` section so the WHY is captured, not just the new
  row.
- Don't close §4 in the tracker without naming the leaf-doc subsection where the binary
  truth lives — readers need the round-trip pointer.
- Don't downgrade the FLT_MAX-or-threshold correction to LOW severity because the wire
  format doesn't change — the gate semantic inverts, which is HIGH-impact for OpenBC.
- Don't omit the "OpenBC implication" paragraph from a sentinel-re-identification correction
  — that's the load-bearing consequence statement.

## Frontmatter signals when this shape applies

- `status: partial` (5 corrections + 2 clarifications is too many to clear `verified`)
- Evidence row count ~35-45 (large — every triad handler + every cast helper + every constant)
- Multiple `confidence: medium` rows for ctor / damage-application functions that were
  inferred from xref direction not byte-by-byte traced
- One `address: null` evidence row for the bypass-TGFactory negative claim
- `supersedes:` carries the prior validation date
- `companions:` always includes the foundation doc the closed §4 conflict involved
  (objcreate-serialization.md in this case) AND the engine doc the cast-helper IsA tags
  point to (rtti-class-catalog.md)

## Tracker §6.N row shape for command-message-triad validations

The row leads with the explicit "Eighteenth protocol doc — fourth protocol leaf" framing,
then names the LOAD-BEARING corrections. Order:

1. Status line + leaf number + "Does NOT clear `verified` because [reason]"
2. Methodology + anchor inheritance
3. Functions touched table — with "CREATED this pass" annotation in Plate column for newly
   defined functions (e.g., 575-byte sender body + 3-byte stub)
4. Wire-format CONFIRMATION table — separate column for "Verified via" with disasm
   addresses
5. Three material wire/value corrections (C1/C2/C3) — each is a 1-paragraph subsection
   with bold tag + severity assessment + OpenBC implication
6. Two address-mapping corrections (C4/C5) — bold tag + binary truth + §4 closure callout
7. Two clarifications (Clar1/Clar2) — bold tag + practical impact
8. Refinements (R1/R2) — not promoted; one-line each
9. Non-corrections list — what stays correct (always include for partial-status docs)
10. Cross-doc anchor reuse / Cross-doc impacts (batched) / Open questions
11. Verification methods used (named function-by-function)
12. Files touched / Header inputs

## §4 cross-doc disagreement closure format (re-affirming the architectural-discovery pattern)

This pass closes §4 #1 with the same format introduced in leaf #17:

> **CLOSED (YYYY-MM-DD, leaf #N):** binary truth — `0x005a2030` IS `ShipReadSpecies` [...].
> The actual `GetPlayerSlotFromObjID` is at `0x006a19a0` [...].
> objnotfound-requestobj-enterset-wire-format.md table corrected this pass; objcreate-
> serialization.md was correct. See objnotfound-requestobj-enterset-wire-format.md
> "Critical Correction: Function Address Map" section (C4).

The row is NOT deleted — the closure annotation preserves the disagreement trail for future
passes.
