---
name: v5-foundation-claim-patterns
description: Evidence-row patterns for foundation-tier v5 docs (totals, ranges, partitions)
metadata:
  type: reference
---

Foundation docs (function-map.md, rtti-class-catalog.md, nirtti-factory-catalog.md) make bulk claims about binary structure — totals, address ranges, exhaustive partitions. These don't fit the "address + function + completeness" mold cleanly. Render them like this:

```yaml
- claim: "Total in-body functions in stbc.exe is 18,249"
  address: null
  function: null
  completeness: null
  confidence: high
  note: "From search_functions_enhanced total on STBC.exe; matches .text 0x00401000-0x00887fff."
```

`address: null` is allowed for **measurement** claims, not just negative claims, as long as the `note` explains how the number was derived (which tool, what query). The header guide says `null` is "for negative claims" but the practical reality is foundation totals are also `null`-addressed.

For range-partition claims, cite the **boundary**, not the count:

```yaml
- claim: "20 address-range categories partition the binary exhaustively and non-overlappingly"
  address: null
  function: null
  confidence: high
  note: "All 18,249 in-body functions bin into exactly one category. Boundaries verified at Cat 9↔10 (0x006A3000), Cat 14↔15 (0x006E0000), Cat 19↔20 (0x00870000)."
```

A single high-confidence claim with the three sampled boundary addresses in the note is honest about what was checked.

For status: foundation docs reach `status: partial` when their per-row content (named-function lists, per-class catalog rows) hasn't been individually validated, even if the gross totals are verified. Promote to `verified` only when every row has high or medium evidence.

**Related:** [[v5-named-function-convention]]
