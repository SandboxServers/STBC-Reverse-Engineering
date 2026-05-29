---
name: networking-gamespy-render-patterns-20260528
description: Render patterns for networking foundation #3 (gamespy-discovery.md, 975 → ~1180 lines). 4 corrections (3 struct-offset table rewrites + 1 hostname-role disambiguation) + 1 dead-code refinement. Notation-base disambiguation as a first-class pattern.
metadata:
  type: project
---

# Networking Foundation #3 — gamespy-discovery.md v5 Render Patterns

Date: 2026-05-28
Doc: docs/networking/gamespy-discovery.md (largest networking doc, 975 lines pre-v5)
Verdict: partial (algorithms + addresses byte-confirmed; 4 struct-offset notation corrections + 1 dead-code refinement)

This pass is the first networking-family render where the dominant correction category is **DWORD-index-vs-byte-offset notation drift inside struct layout tables** — distinct from prior protocol-family patterns where corrections were typically about wire-byte format or function attribution.

## Pattern 1: NOTE-block headline groups corrections by category, then names mechanism

The headline opens with the strongest evidence-quality claim ("Algorithm + address claims byte-confirmed at high confidence") to anchor reader confidence, THEN lists the corrections grouped by category:

```
> [!NOTE]
> **Algorithm + address claims byte-confirmed at high confidence**.
> 4 struct-offset table corrections needed (qr_t and ServerList layout tables
> mix DWORD indices with byte offsets — clarification).
> Master server hostname mechanism corrected: 0x0095a4fc is the runtime-mutable
> target of masterserver.txt; 0x0095a594 is the immutable canonical source.
> RC4 PRGA modification, secret key Nm3aZ9, heartbeat timing, vtable slots,
> base64 encoder all byte-confirmed.
> C1 ... C2 ... C3 ... C4 ... R1 ...
```

The headline cites SPECIFIC byte-confirmed claim groups (RC4 PRGA, Nm3aZ9, heartbeat timing, vtable, base64) NOT a generic "wire format confirmed". This lets readers who came in skeptical see immediately which load-bearing things passed v5.

## Pattern 2: Notation-base disambiguation as a struct-table correction class

This is the first networking foundation where multiple struct-layout corrections share a **common root cause**: the pre-v5 doc mixed DWORD indices with byte offsets in the SAME table. The fix pattern:

1. Mark the section header with `[v5-validated-corrected]` tag (not just `[v5-validated]`)
2. Open with an `> [!IMPORTANT]` block stating the notation problem
3. Rewrite the table with TWO offset columns: `Byte offset` (primary) and `DWORD idx` (cross-reference)
4. Add a "Field-access evidence" bullet list below the table showing the decompile reads that disambiguate the two notations

The critical insight: `qr_t[0x37]` (when typed as `SOCKET*`) and `qr_t + 0xDC` (byte-indexed) are the SAME byte in the binary — Ghidra just renders the access differently depending on the cast. Pre-v5 docs that quote Ghidra decompiles verbatim absorb this confusion. v5 has to surface it explicitly.

## Pattern 3: Field-with-dual-role disambiguation (qr_t+0xE4)

When a single byte serves as both a flag AND a wire-format field (here: `qr_t+0xE4` = active flag AND heartbeat port number), the pre-v5 doc had it labeled as "packet counter" — guessed semantics from the field's appearance in the heartbeat format string without realizing the same field is the active-flag gate. The render pattern:

1. In the struct table, bold the field row and name BOTH roles in the Field column
2. In the field-access evidence bullets, name the TWO different functions that read the same byte with different semantic intent
3. Add a separate `> [!NOTE]` block in the body section that uses the field — quote the format-string `%d` argument site and the active-flag-gate site side-by-side
4. Add a `C3` correction tag (separate from `C1` which is the table rewrite) so the body-text rename is its own deliverable

This is the same pattern as `command-message-triad render patterns` from protocol leaf #18 (FLT_MAX gate-semantic inversion), but for a flag/field overload rather than a sentinel-vs-threshold inversion.

## Pattern 4: Hostname-role differentiation table (C4)

Pre-v5 listed three master-hostname addresses as "duplicates". v5 truth: two of them are not duplicates — `0x0095a4fc` is the runtime-mutable target overwritten by `masterserver.txt`; `0x0095a594` is the immutable canonical source. Render pattern:

1. Section header `Master Server Addresses [v5-validated 2026-05-28]`
2. `> [!IMPORTANT]` block: "Pre-v5 doc treated the three hostname addresses as identical duplicates. They are not."
3. Table: Address | Role | Evidence — with the third address explicitly marked as "role not fully traced this pass — see OQ3"
4. Body paragraph immediately after the table explains the MECHANISM ("The mechanism is runtime overwrite of 0x0095a4fc — `FUN_006aa100` `strncpy`s the resolved hostname into the original Activision hostname slot with width 0x40")
5. The `_strncpy` width `0x40` is load-bearing — it's the buffer cap that makes the mechanism work safely. Inline it in the prose.

## Pattern 5: Dead-code refinement as a stronger negative claim

Pre-v5 said "Ghidra finds no xrefs to this code block". v5 stronger statement: Ghidra has not disassembled the block at all — `disassemble_function` returns "No function found". The bytes exist as raw data containing dead RVAs. Render pattern:

1. Section header gets the standard `[v5-validated 2026-05-28]` tag
2. Body keeps the original claim language (the original was technically correct)
3. Add a separate `> [!NOTE]` block titled `**R1 — stronger than "no xrefs"**` that quotes the binary-truth observation
4. R1 is a refinement (not a correction) — distinguish in the NOTE-block headline at the top by using `R1` not `C5`

## Pattern 6: Inline-tag promotion for byte-confirmed sub-sections

For a 975-line foundation doc, you can't tag every paragraph. The promotion strategy:

- Tag section HEADERS where v5 confirmed the claims in that section (Wire Format, Heartbeat Timing, Crypto, GameSpy Vtable)
- Tag standalone IMPORTANT or NOTE blocks where the correction lives
- DO NOT tag every code block, every byte sequence, every wire-format string — that produces visual noise

The tagged section count for this 1180-line render: 7 inline tags (Section 2 header, Response Fragmentation subhead, Heartbeat Timing subhead, Section 10 header, RC4 algorithm subhead, GameSpy Vtable subhead, Dead Code subhead) + 2 `[v5-validated-corrected]` table headers (qr_t Layout, ServerList Layout) + 1 hostname-table tag. Total: 10 inline tags for a foundation doc.

## Pattern 7: Open Questions section with HYPOTHESES not just questions

Pre-v5 had a single-line "Open question" about heartbeat sendto rc=-1. v5 expands it into a numbered list of hypotheses:

- The heartbeat socket may not be properly bound when `\heartbeat\` is formatted.
- Firewall may be blocking outbound UDP to port 27900.
- The `\heartbeat\0` port value (`qr_t+0xE4 = 0`) may be rejected by the master.
- Inbound master queries may come from a separate discovery mechanism (cached server from a prior session, or another client's query traffic).

Hypotheses are sequenced from "internal to the binary" to "external/environmental" — gives a follow-up investigator a tractable order to rule things out. Always close with "Unresolved this pass."

## Pattern 8: Companions block uses code-relative paths (Markdown links)

For networking-family docs that cross-link to protocol-family anchors, use relative paths like `[docs/protocol/transport-layer.md](../protocol/transport-layer.md)` rather than absolute repo paths. This matches the existing networking-doc convention from `network-protocol.md` and `multiplayer-flow.md` and survives directory moves better than absolute paths.

## What NOT to do this pass

- DO NOT delete the pre-v5 trace-based Section 8 connection handshake — it's still useful as a forensic timeline even though it's not a fresh v5 anchor. Leave it intact, tag it `[trace 2026-02-16]` if you want lineage clear, but don't restructure.
- DO NOT restructure the doc's section numbering. Reader inbound links target Sections 1-12 by number.
- DO NOT promote OQ1 (callback-table location) to `confidence: high` in the evidence rows just because the body section keeps the addresses. Carry it as `confidence: low` + OQ1 inline tag in the qr_t Layout table.
- DO NOT modify v5-validation-status.md tracker or shared MEMORY.md this pass — those get batched at end of wave.
