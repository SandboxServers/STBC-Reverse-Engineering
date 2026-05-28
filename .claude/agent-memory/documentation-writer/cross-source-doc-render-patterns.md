---
name: cross-source-doc-render-patterns
description: Render patterns for cross-source docs (claims about external corpora like Gb 1.2 source, MWSE headers, nif.xml). New tag convention + frontmatter rules introduced 2026-05-28 with gamebryo-cross-reference.md.
metadata:
  type: feedback
---

# Cross-source doc render patterns

Cross-source docs make claims about external corpora alongside stbc.exe claims. Examples: gamebryo-cross-reference.md (Gb 1.2 source, MWSE, nif.xml), future SWIG docs (SWIG 1.x source), embedded Python docs (Python 1.5.2 source), GameSpy docs (GameSpy SDK). The v5 evidence model was designed around Ghidra-anchored stbc.exe claims; cross-source docs need an adapted convention.

**Why:** A claim like "nif.xml line 3487 defines NiAVObject Velocity as Vector3 with until=4.2.2.0" has evidence (a file path + line number) but isn't a stbc.exe binary anchor. Tagging it `[v5-validated]` is misleading; dropping it for lack of address is worse. Need a distinct tag.

**How to apply:** When rendering a cross-source doc, apply the two-tag convention:

1. **`[v5-validated YYYY-MM-DD]`** — claims anchored to stbc.exe (Ghidra address, factory FUN_, vtable offset, instruction byte). Standard v5.
2. **`[cross-source-YYYY-MM-DD]`** — claims about external corpora, verified by file:line citation. Treat as `confidence: high` when file existence + content was directly verified (grep/Read). Treat as `confidence: medium` when pattern-extrapolated from successful spot-checks.

In the YAML frontmatter, evidence rows for external-corpus claims use `address: null` and put the file:line citation in `note:`. Example:

```yaml
- claim: "NiAVObject Velocity field present in V3.1 (removed by 4.2.2.0)"
  address: null
  function: null
  confidence: high
  note: "engine/nif.xml:3487 — Vector3, until=4.2.2.0. [cross-source-2026-05-28]"
```

Always introduce the convention in a top-of-doc NOTE block on first cross-source doc the reader encounters. Example phrasing:

> Cross-source convention: external-corpus claims (Gb 1.2 source, MWSE headers, nif.xml) are tagged `[cross-source-YYYY-MM-DD]` since they're verified via file:line citation rather than Ghidra addresses. Stbc.exe-anchored claims use the standard `[v5-validated YYYY-MM-DD]` tag.

**Status rules unchanged:** Cross-source docs still use `verified | partial | stale | disputed`. They can be `verified` if every claim is `confidence: high` or `medium` with a documented reason (pattern extrapolation OK). The convention is about tag provenance, not status.

**Related:** [[v5-foundation-claim-patterns]] for the standard stbc.exe-anchored evidence row patterns. [[verified-status-criteria]] for the pattern-extrapolation rule.

## When to use

Apply this convention whenever the doc makes load-bearing claims about:
- External source code corpora (Gb 1.2, MWSE, Gamebryo 2.6, SWIG, Python 1.5)
- External specs (nif.xml, RFC documents, official SDKs)
- Decompiled-source files in `reference/decompiled/` (these are derived from stbc.exe but cited by file:line in a separate corpus)

Do NOT use for the actual decompiled Ghidra output cited inline — that's stbc.exe-anchored even if quoted as source text. Use the Ghidra address.
