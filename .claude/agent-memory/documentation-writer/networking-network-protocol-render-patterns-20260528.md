---
name: networking-network-protocol-render-patterns-20260528
description: Render patterns for FIRST networking-family foundation doc (architecture hub, 167-line pre-v5) when v5 surfaces 2 corrections + 3 clarifications + 2 refutations + 3 historical-section marks + ~90% claims cross-anchored from protocol family
metadata:
  type: project
---

# Render patterns — networking foundation #1 (network-protocol.md, 2026-05-28)

This was the FIRST doc rendered in the networking family v5 campaign. Doc class: foundation/hub (architecture overview). Special property: ~90% of load-bearing claims were already byte-confirmed by protocol-family work, so the validation memo was cross-reference-heavy rather than fresh-Ghidra-heavy.

## Pattern 1 — Cross-family cross-anchor frontmatter row

When an evidence row is anchored to a doc in **another family** (here: protocol family), the `note:` field carries the explicit cross-anchor tag.

```yaml
- claim: "MpgameHandleMessage (MultiplayerGame ReceiveMessageHandler dispatcher) at 0x0069F2A0 — jump table at 0x0069F534, 41 entries indexed by (opcode - 2), handles opcodes 0x02-0x2A"
  address: 0x0069F2A0
  function: MpgameHandleMessage
  completeness: 69.8
  effective: 94.4
  confidence: high
  note: "Cross-anchor: protocol foundation #1 wire-format-spec.md (v5-validated 2026-05-28). Best-documented function in this doc — custom-named + prototyped."
```

The `note:` field both:
1. Names the originating doc (`protocol foundation #1 wire-format-spec.md`)
2. Carries the validation-date tag `(v5-validated 2026-05-28)` so future readers know the cross-anchor is still in the freshness window.

For evidence rows where the doc IS the original anchor, the `note:` field describes the discovery: e.g., "Direct re-verification this pass."

## Pattern 2 — Inline section header tags reference the anchor doc

For SECTIONS that are wholly cross-anchored to another family doc (e.g., the entire Checksum Protocol section here is anchored to `checksum-opcodes.md`), use:

```markdown
## Complete Checksum Protocol (Fully Traced)

[v5-validated 2026-05-28 via [checksum-opcodes.md](../protocol/checksum-opcodes.md)]
```

The `via [link]` clause makes the cross-anchor visible without forcing readers to consult the frontmatter. This differs from the in-family tag (which is just `[v5-validated YYYY-MM-DD]` with no `via`).

## Pattern 3 — Two-singleton disambiguation table (C2 shape)

When v5 surfaces that what the pre-v5 doc treated as ONE global is actually TWO distinct singletons, render with a 5-column comparison table near the top of the relevant section:

```markdown
| Singleton | Address | Role | Xref count | First-seen reference |
|---|---|---|---|---|
| **EventManager** (queue/dispatcher) | `0x0097F838` | C++ event queue + handler-registry root at `+0x2C = 0x0097F864`; receives `PostEvent` calls from C++ paths | 140+ xrefs | `MOV ECX, 0x97f864` byte-level confirmed in [`decompiled-functions.md`](../engine/decompiled-functions.md) |
| **TGEventManager** (SWIG/Python bridge) | `0x00991438` | SWIG-accessible singleton; populated at boot (zero in image); exposed to Python via SWIG wrappers | 2 xrefs (`0x0065b430`, `0x0065b460`) | `MOV EAX, [0x00991438]` in SWIG `TGEventManager_AddEvent` wrapper at `0x005c8be9` (per [`event-system-architecture.md`](../engine/event-system-architecture.md)) |
```

The **xref count** column is what distinguishes "this is the real one" — 140+ xrefs vs 2 xrefs is structurally diagnostic. The **First-seen reference** column carries the byte-level disambiguation evidence (the actual `MOV` instruction). Pair with explicit text: "Both are correct anchors; they are not the same object."

This is the cross-doc analogue of the `[load-bearing correction disambiguation]` pattern from engine doc #10 (two-globals-conflated case), but for foundation-hub docs that reference both singletons in different sections.

## Pattern 4 — Historical-section blockquote prefix

For sections describing OLD game state or proxy-instrumentation (not stbc.exe behavior), prepend a `> **Historical (resolved YYYY-MM-DD)**` blockquote at the **top** of the section, BEFORE the section content. Three flavors:

```markdown
## STATUS: CLIENT DISCONNECTS AFTER SHIP SELECTION

> **Historical (resolved 2026-05-28)** — flags=0x20 with real subsystem health data is now sent by the server via DeferredInitObject. See CLAUDE.md "What Works" status (Collision damage / Subsystem damage / StateUpdate flags=0x20).
```

```markdown
## Previously Solved Issues

> **Historical (resolved 2026-05-28)** — Black screen, checksum stall, and first-connection timeout are all addressed in the current build. Preserved for trace cross-reference.
```

```markdown
## IAT Hooks (Currently Installed)

> **Historical (proxy instrumentation, not stbc.exe behavior)** — Describes the proxy DLL's diagnostic hooks rather than the game binary itself. Belongs in proxy instrumentation docs; preserved here for cross-reference.
```

The 3 flavors are:
1. **resolved-bug** — bug described in section is fixed; cite where the fix lives in CLAUDE.md
2. **resolved-feature-set** — multiple historical items batched (compact form)
3. **scope-out-of-band** — content is real but doesn't belong in this doc (proxy instrumentation vs stbc.exe behavior)

Critical rule: **do NOT delete historical sections**. They remain useful for trace cross-reference. The blockquote PREFIX is the v5 marker; section body is untouched.

## Pattern 5 — Embedded-correction inline in pre-existing tables

When v5 surfaces that specific rows in a pre-v5 table have wrong identity labels (and we now have authoritative cross-anchors), update **inline** rather than replacing the whole table. Render as:

```markdown
| 0x006a0a20 | **MultiplayerGame__EnterSetEventHandler** *(was: "DisconnectHandler" — corrected via protocol leaf #18 [objnotfound-requestobj-enterset-wire-format.md](../protocol/objnotfound-requestobj-enterset-wire-format.md))* |
```

Three elements per corrected row:
1. **Bolded** corrected name
2. *(was: "Previous Label"* — old name in quotes for inbound-link readers
3. *corrected via [link]* — anchor doc that established the truth

This is more reader-friendly than a separate "corrections" section because readers consulting the handler table will see the correction in-place. Used for 3 corrections in the MultiplayerGame Event Handlers table.

## Pattern 6 — IMPORTANT block above a [partial] table

When a pre-v5 table is INCOMPLETE (lists N of M registered handlers), don't restructure — add an IMPORTANT block above the existing table:

```markdown
## R1 — MultiplayerGame Event Handlers (FUN_0069efe0)

> [!IMPORTANT]
> **`[partial — subset of 30 registered handlers; full enumeration deferred to OQ2]`**. The table below lists 15 of the 30 handlers actually registered by `FUN_0069efe0`. Listed entries are address-correct.
```

The bolded `[partial — ...]` tag at the start of the block doubles as the v5 partial-completeness marker. The "Listed entries are address-correct" reassurance is important — readers should trust the rows that ARE there, just not assume the table is exhaustive.

Pair with explicit OQ entry that enumerates the known-missing handlers as recovery hints for the future sweep:

```markdown
- **OQ2** — Full enumeration of MultiplayerGame Event Handlers (15 -> 30). Known unlisted handlers from prior validation memo: `StopFiringHandler` (0x006a18d0), `StopFiringAtTargetHandler` (0x006a18e0), ... Deferred to a focused sweep of `FUN_0069efe0`.
```

## Pattern 7 — Clar in body section, not top-of-doc

When the pre-v5 doc has a specific factual misread (e.g., "byte[1] != 0xFF (always true)" — the parenthetical was wrong), don't introduce a top-level "Clarifications" section. Instead, weave the correction INTO the procedural narrative where it lives:

```markdown
7. FUN_006a4260: `byte[1]` selects between the verification path (`!= 0xFF`, indices 0-3 for checksum responses) and a separate `0xFF`-flagged retry path. The verification path calls FUN_006a4560. **(Clar2 — prior doc claimed "always true" which was a misread; the 0xFF path is reachable.)**
```

The parenthetical (Clar2 — ...) preserves the v5-pass attribution for tracker purposes without breaking narrative flow. Used for Clar2 (0xFF path) and Clar3 (both dispatchers set flag).

For Clar1 (hash table offset terminology), where the correction needed a dedicated sub-explanation, render as a sub-section under the affected feature:

```markdown
### Clar1 — Hash table offset terminology

The pre-v5 doc used the shorthand `vtable+0x18 / buckets+0x24` for table A, etc. Those offsets are correct, but the prefix word "vtable" was ambiguous (these aren't offsets relative to a vtable; ...). Corrected wording: ... Offsets are unchanged.
```

This says "the binary is unchanged; only the way we describe it is updated" — important for readers cross-referencing existing OpenBC clean-room specs.

## Pattern 8 — R2 (call-chain refutation) gets parenthetical in narrative

For a refutation that adds an intermediate function-call layer (the prior doc skipped a function), embed the corrected chain in the narrative with the R-tag inline:

```markdown
- ProcessEvents (`FUN_006da2c0`) dequeues from queue, calls **`FUN_006da300` per event**, which then calls **`FUN_006db620(registry, event)`** via `this+0x4` plus a vtable hop **(R2 — pre-v5 doc skipped the intermediate `FUN_006da300` layer; corrected here)**
```

Bold the corrected function names AND bold the inline `(R2 — ...)` tag. Reader sees three things at once: the corrected chain, that this is a v5 correction, and the specific layer that was missed.

## Pattern 9 — Cross-doc disagreements get protocol-leaf citations

When the doc's table cites a function with a wrong handler name, and the binary-truth name is anchored by a specific protocol-family leaf, cite the leaf BY NUMBER AND TITLE in the inline correction:

```markdown
| 0x006a0a20 | **MultiplayerGame__EnterSetEventHandler** *(was: "DisconnectHandler" — corrected via protocol leaf #18 [objnotfound-requestobj-enterset-wire-format.md](../protocol/objnotfound-requestobj-enterset-wire-format.md))* |
| 0x006a07d0 | **MultiplayerGame__RequestObjEventHandler** *(was: "EnterSetHandler" — sender for opcodes 0x1D ObjNotFound and 0x1F EnterSet per protocol leaf #18)* |
| 0x006a0ca0 | **DeletePlayerAnimSender** *(was: "DeletePlayerHandler" — sends opcode 0x18 DeletePlayerAnim per protocol leaf #17 [delete-player-ui-wire-format.md](../protocol/delete-player-ui-wire-format.md))* |
```

The "protocol leaf #N" framing (rather than just "see [doc]") signals to the reader that this isn't a one-off — there's a cataloged validation pass that established the correction. Important for tracker-driven cross-reading.

## Pattern 10 — `[low-confidence — see OQ#]` inline tag in tables

For event-type rows where the NAME->NUMERIC binding is unverified but plausible, tag inline rather than dropping the row:

```markdown
| 0x60002 | (hosting start) | Host session created — `[low-confidence — see OQ1]` |
| 0x8000e6 | (checksum result?) | Individual checksum done — `[low-confidence — see OQ1]` |
```

This preserves the row's informational value while flagging the binding as unanchored. Anchored rows in the same table get explicit citations:

```markdown
| 0x60001 | ET_NETWORK_MESSAGE_EVENT | Incoming network message — anchored in `FUN_00445d90` and `FUN_006b4560` |
| 0x8000e8 | ET_CHECKSUM_COMPLETE | All checksums passed — anchored at `FUN_006a4bb0` |
```

Mixed-confidence tables are common in foundation/hub docs that summarize many anchors — this gives per-row provenance without needing to split the table.

## Pattern 11 — Frontmatter row for "the global itself" with address: <hex>, function: null

For a global-state anchor that isn't a function (e.g., `DAT_0097fa8b` re-entry guard), use the global's address as the row's `address:` and set `function: null`:

```yaml
- claim: "Both message dispatchers set re-entry guard DAT_0097fa8b = 1 during processing — MpgameHandleMessage at 0x0069f2be, FUN_006a3cd0 at 0x006a3cd6 (NOT NetFile-exclusive as prior doc claimed)"
  address: 0x0097FA8B
  function: null
  confidence: high
  note: "See Clar3 in body. 36 xrefs to global, including both dispatcher entries. Cleared at end of each dispatch (0x0069f525 and 0x006a3e75 respectively)."
```

Same pattern for singleton globals like 0x0097F838 (EventManager) and 0x00991438 (TGEventManager). Counts and dispatch-site addresses go in the `note:` field as the evidence.

## What NOT to do

- Don't restructure body for cross-anchor-only sections — preserve original section order (readers may have inbound links to the section anchors).
- Don't delete the pre-v5 STATUS / "Previously Solved Issues" sections — historical-prefix them. The historical content is useful trace context.
- Don't promote OQ1 / OQ2 to corrections — they are debt, not errors. The pre-v5 table is incomplete but not wrong; the event-type bindings are plausible but unanchored.
- Don't omit the cross-doc disagreement inline corrections — those THREE handler-name fixes are the most impactful update in this pass and they live in the table the reader already consults.

## Tracker entry shape (for batched close)

The tracker row for this doc should:
- Status: `partial`
- Corrections: 2 (C1 three-dispatchers, C2 two-singletons)
- Clarifications: 3 (Clar1 hash-table terminology, Clar2 0xFF path, Clar3 both dispatchers set flag)
- Refutations: 2 (R1 handler table partial 15/30, R2 ProcessEvents skips intermediate)
- Historical sections: 3 (STATUS, Previously Solved, IAT/Peer monitoring)
- OQ: 2 (event-type numeric bindings, full handler enumeration)
- Cross-anchor inheritance: heavy from protocol family (decompiled-functions, wire-format-spec, checksum-opcodes, transport-layer, subsystem-integrity-hash, delete-player-ui, objnotfound)
- Family role: networking foundation #1 (architecture hub, sets the framing for the rest of the networking family v5 campaign)

[[engine-family-close-batch]] | [[protocol-family-campaign-close]] | [[load-bearing-correction-disambiguation]]
