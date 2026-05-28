---
name: named-slot-table-render-patterns
description: 6 render patterns for mid-tier docs where v5 finds a partial-enumeration error in a named-slot or named-table section, plus a function-misattribution C2 — switch-decoded slot table with property-ID column, missing-row bold-add convention, source-of-truth annotation, "created this pass" Ghidra disclosure, vtable-confusion C2 pattern, refinement-as-numbered-section convention. Learned from stateupdate-subsystem-wire-format.md (protocol mid #11).
metadata:
  type: feedback
---

# Named-slot table render patterns (protocol mid #11)

stateupdate-subsystem-wire-format.md surfaced a recurring pattern: docs that
enumerate a "table of ship slots / named fields / object offsets" are often
written from a partial walk of the source function. Re-walking the full switch
is mechanical and catches all the missing rows. This memo documents the 6
render patterns that came out of this validation pass.

## Pattern 1 — Switch-decoded slot table with property-ID column

When the slot table is sourced from a switch-on-property-type-ID, the rendered
table should include the property-ID column explicitly. This makes the
provenance audit-trivial: a reader can grep `Ship__SetupProperties` for the
property-ID hex and see the exact case branch.

```
| Offset | Subsystem | Property type ID | Notes |
|--------|-----------|------------------|-------|
| ship+0x2B0 | PowerSubsystem (reactor / EPS) | 0x813E CT_POWER_PROPERTY | ... |
| **ship+0x2C0** | **ShieldGenerator** | **0x8137 CT_SHIELD_PROPERTY** | **Added 2026-05-28** |
```

Without the property-ID column, the reader has to take the doc on faith. With it,
the validation chain is short: case 0x8137 → ship+0x2C0 → in-binary line.

## Pattern 2 — Missing-row bold-add convention

When v5 adds rows that were missing in the previous version, bold the entire
row content AND include an inline "Added YYYY-MM-DD" note in the rightmost
column. This makes the row visually scannable in diff review AND in the
rendered Markdown view.

Don't append the added rows at the end of the table — slot them in by offset
order (or whatever the table's natural order is). The location in the table
matters because readers scan by offset adjacency.

## Pattern 3 — Source-of-truth annotation for switch-decoded data

When a section is sourced from a single Ghidra function, name the function
explicitly in the section preamble:

> The corrected table is sourced from `Ship__SetupProperties` (FUN_005B3FB0),
> a switch on the property type ID. A plate comment with all 12 mappings is
> installed in Ghidra.

This is stronger than just citing the address in the evidence row — it tells
the reader where the OTHER 11 slot mappings live, even if the doc only
displays a subset. The "plate comment installed" half is the durability
guarantee: if Ghidra is re-imported, the plate is the persistent artifact.

## Pattern 4 — "Created this pass" Ghidra disclosure

When an evidence-chain function had to be `create_function`-ed in Ghidra (no
auto-recovered body, only DATA xrefs from a vtable slot), call this out
explicitly in a dedicated subsection:

> `PowerSubsystem__ReadState` at **0x00564530** was previously undefined in
> Ghidra (only a DATA xref from PowerSubsystem vtable @ 0x0088A264 + 0x74).
> Ghidra needed an explicit `create_function` to recover the body. Now named
> and plated.

This is a doc-level disclosure of a Ghidra-state change. Future re-validations
will inherit the function; this note explains why the prior doc didn't have
the body anchored.

## Pattern 5 — Vtable-confusion C2 pattern (function misattribution)

This pass had a corrected-attribution C2: prior doc said EndMarker was the
function at 0x006CDAE0 (a RET-only stub), but actually `stream.vtable[+0xD8]`
calls 0x006CF9B0 (TGBufferStream_swig_GetPos). The wrong-attribution arose
because TWO different classes use offset +0xB0 / +0xD8 for similar-purpose
methods — finding a no-op function at the right offset in the WRONG vtable is
an easy mistake.

Render rule for C2 corrections of this shape:

1. In the NOTE block, give BOTH the correct function/address AND the
   incorrect function/address, with WHY the prior was attributable
   ("which IS a RET-only stub but lives at slot +0xB0 of a different
   vtable").
2. In the evidence row, set the function to the correct one; put the prior
   misattribution in the `note:` field.
3. In the body, replace the function citation with the correct one but
   preserve the behavioral claim ("effectively no-op", "trailer") because
   the user-observable behavior didn't change.
4. Don't repeat the C2 explanation in every section that mentions the
   trailer — once in NOTE block + once in the evidence row is enough; body
   sections just use the corrected attribution silently.

This pattern minimizes body noise (the wire format is unchanged) while making
the audit trail explicit (NOTE + evidence row).

## Pattern 6 — Refinement as numbered section

When a refinement (R1, R2, R3) doesn't rise to the level of a correction but
DOES change a count or a phrasing, render it as a small numbered subsection
right after the table it adjusts.

Example: vtable consumer counts of 7+9+1=17 vs 8+11+1=20. The difference is
"intermediate base-class vtables vs user-visible leaves". This is too
substantive for a footnote but too minor for a NOTE block. The right home
is a "Vtable Consumer Counts (Refinement R3)" subsection adjacent to the
IN/REMOVED tables, explaining the discrepancy and noting which number the
table is using and why.

## Cross-doc impact: open-question debt

The 2 open questions (FUN_005B5240 case 0x812E, FUN_005B5280 case 0x8145) are
listed in a dedicated "Open Questions (documentation debt)" section near the
end. These are not OQ#-tagged inline because they're discovered DURING the
slot-table re-walk — they exist at the function-existence level, not at the
claim level. The pattern: re-walking a switch always surfaces 1-2 cases that
weren't in the prior doc; those become open questions, not corrections.
