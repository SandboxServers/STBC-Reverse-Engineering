---
name: v5-named-function-convention
description: How to render pre-v5 annotation-script function names in catalog docs without dropping the addresses
metadata:
  type: feedback
---

When a catalog doc (function-map.md style) carries lots of pre-v5 named functions that the current Ghidra import has reverted to `FUN_xxxxxxxx`, use convention (a) from the v5 evidence header guide:

```
0x0043b4f0  FUN_0043b4f0 (intended: UtopiaApp_MainTick)  [v5: unnamed in current import]
```

**Why:** The campaign rule is "no annotation scripts during v5". Pre-v5 names are aspirational; they retire one-by-one as per-function v5 passes are done. But the addresses are still load-bearing for anyone navigating the binary, so we keep them — we just demote the name with the parenthetical and the trailing tag.

**How to apply:**
- Every per-category "Named/Identified Functions" subsection gets a `> [!NOTE]` block above it explaining the convention.
- Only the per-function passes that have actually happened (v5-validated) keep the bare name. Tag them as `[v5-validated YYYY-MM-DD]` so future readers know which are real.
- Real Ghidra-recognized entries (CRT library functions, Win32/Winsock imports, `Unwind@`, `Catch@`) keep their bare names — they are not pre-v5 cruft. The NOTE block should call out the exceptions.
- In the doc-level frontmatter, add a single `confidence: low` evidence row that names the per-category-list situation. This keeps the doc at `status: partial` until those lists are individually retired.

**Related:** [[v5-foundation-claim-patterns]]
