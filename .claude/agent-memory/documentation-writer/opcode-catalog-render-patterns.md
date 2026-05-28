---
name: opcode-catalog-render-patterns
description: Five patterns for rendering opcode-catalog reference docs (one per dispatcher / one per jump-table) when the binary is clean and the doc just needs evidence-standard formalization. Born from game-opcodes.md v5 render — cleanest validation in the protocol family (0 binary corrections).
metadata:
  type: feedback
---

# Opcode-Catalog Render Patterns

Five patterns that emerged from rendering `docs/protocol/game-opcodes.md` under v5. This is a different shape from a hub doc (no cross-doc authority claims) and a different shape from a leaf doc (no single deep-dive subject). An opcode catalog is a **flat enumeration** of N opcodes, each anchored to a handler address and a wire format. The render task is mostly typographic and cross-link mechanical — the binary work was already done upstream.

## Pattern 1: Effective-Event-Code clarification (column-header asymmetry)

When a generic-event-forward (or any shared-handler) table has a column whose meaning depends on whether the dispatcher overrides or keeps the wire value, the column name itself is the bug. Render pattern:

1. **Rename** the column to disclose the post-receive semantic (e.g. "Effective Event Code (post-receive)") OR add an explicit "(override)" / "(from stream)" marker per row.
2. **Add a dedicated subsection** below the table with a 4-row taxonomy table naming each flavour of the value (sender path / wire / dispatcher PUSH / effective). This is what makes the row values legible to a clean-room implementer.
3. **State the override rule** in plain language: `effective = dispatcher PUSH if non-zero, else wire value`. Cite the decompile line (e.g., `FUN_0069FDA0` line `if (param_2 != 0) puVar7[4] = param_2;`).
4. **State the OpenBC implication** so clean-room implementers know they need to generate the effective event downstream even though the wire bytes themselves can be relayed verbatim.

**Why:** Without disclosure, a clean-room implementer relays the wire bytes correctly but generates the wrong event on the receive side because they assumed the wire value is what the receiver sees. A column header is not the place to encode "two different meanings depending on row" — disambiguate it explicitly.

**How to apply:** Use whenever a single column carries values whose semantic identity depends on the dispatcher pathway. Pair the rename with a small taxonomy table directly under the main opcode table.

## Pattern 2: Shared-thunk annotation

When multiple opcodes share a single jump-table thunk address (e.g., opcodes 0x06 and 0x0D both pointing to thunk 0x0069F3F1, or 0x0C/0x11/0x12 all pointing to thunk 0x0069F3C7), the opcode table needs to **disclose** the sharing so the reader can see why some rows have identical handler behavior.

Render pattern:
- In the "Thunk" column, append "(shared)" or "(shared with 0xNN)" on the second-and-subsequent rows that reuse the same thunk.
- The shared thunk is the ground truth — list each shared address only once with the full "(shared)" label so readers can cross-reference.
- For opcodes that share a handler but NOT a thunk (e.g., 0x02 and 0x03 both call `FUN_0069F620` but with different arg2), put the arg distinction inline in the Handler column: `FUN_0069F620 (arg2=0)`.

**Why:** A reader scanning the table sees identical addresses on different rows and wonders if it's a doc error. Explicit "(shared)" calls out the binary reality. Distinct-thunk-same-handler cases need the arg2 distinction so the row isn't merely a duplicate.

**How to apply:** Any opcode catalog that consolidates a jump table with shared thunks. The shared-thunk annotation goes in the thunk column; the arg-distinguisher annotation goes in the handler column.

## Pattern 3: Dispatcher-default consolidation row

When N opcodes in the catalog route to the DEFAULT cleanup because they're owned by a sibling dispatcher (e.g., 0x20-0x28 in MultiplayerGame's jump table because NetFile owns them), render them as a **single consolidated row** rather than 9 separate rows.

Render pattern:
- One row with opcode range `0x20-0x28` in the Opcode column
- Handler column: `DEFAULT (0xXXXXXXXX)`
- Notes column: names the owning dispatcher with the cross-link, and discloses the non-contiguous case set if applicable ("0x24/0x26/0x28 unused")
- A dedicated subsection further down (e.g., "0x20-0x28 - NetFile Dispatcher") that names the owning dispatcher's address and cross-links to the canonical opcode-map doc

**Why:** Nine identical rows in the main table is visual noise that obscures the load-bearing fact (these aren't MultiplayerGame's opcodes). Consolidation surfaces the routing fact; the dedicated subsection holds the cross-link to the canonical doc.

**How to apply:** Any catalog row group where N >= 3 opcodes share the DEFAULT thunk because they're owned elsewhere. Always pair the consolidated row with a dedicated subsection.

## Pattern 4: Open-debt inline annotation (for opcodes without a leaf doc)

When an opcode has a verified handler address but **no companion leaf doc** (e.g., opcode 0x18 DeletePlayerAnim), the row needs to surface the documentation debt without pretending the wire format is fully documented.

Render pattern:
- Leaf doc column: parenthetical "(Open debt — see NOTE at top; mirror from `<OpenBC clean-room path>`)"
- Dedicated subsection for the opcode says explicitly: "**Documentation debt**: no BC-side wire-format leaf doc exists for this opcode."
- The opening NOTE block at the top of the doc lists the open debt items as a bullet so a reader scanning the top can see the gap.

**Why:** A row with no companion doc link is invisible debt; a row with "(Open debt)" surfaces it. Without this, the next reader assumes the missing link is an oversight and either adds a wrong one or silently moves on. The OpenBC mirror cross-link gives the next maintainer a starting point.

**How to apply:** Any catalog row where the opcode is shipped (handler exists, traffic observed) but the BC-side wire-format doc doesn't exist. Pair with a top-of-doc NOTE bullet so the debt is surfaced at the entrance.

## Pattern 5: Trace-counts tagged inline, not in a separate column

Session-frequency counts ("84/session", "2282/session") are not Ghidra-anchored — they come from packet-trace analysis. Don't give them their own column (which falsely implies authority); inline-tag them.

Render pattern:
- Counts go in the Notes / Type column inline: `Collision damage relay (84/session) [cross-source-2026-02-XX trace]`
- The `[cross-source-YYYY-MM-DD trace]` tag points at the trace doc that produced the count.
- A footer paragraph below the main opcode table explicitly states the convention: counts so tagged are derived from the named trace analysis, NOT directly observable in the binary.
- Don't give trace data its own column — that visually elevates it to a peer of the handler address, which is misleading because the count is observational not binary-grounded.

**Why:** Binary-anchored facts and trace-observed facts have different epistemic weight. Conflating them visually (same column treatment) makes the trace data look like ground truth from stbc.exe. Inline tagging keeps the trace data visible while disclosing its provenance.

**How to apply:** Whenever a reference doc includes any observational data (packet counts, session frequencies, observed flag values from runtime). Tag every such datum with `[cross-source-YYYY-MM-DD <source>]` and explain the convention in a footer below the table.

## When this pattern doesn't apply

Hub docs use the [[protocol-hub-doc-render]] patterns instead. Leaf docs use the [[leaf-doc-render-patterns]]. These patterns are specifically for **flat opcode catalogs** that enumerate N opcodes/handlers/codes with cross-links to deeper leaves. The shared characteristic: one row per opcode, no deep dive per opcode (those live in the leaves), and the doc's value-add is the **enumeration completeness + cross-link mesh**, not new RE content.
