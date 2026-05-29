---
name: load-bearing-correction-disambiguation
description: Render pattern for v5 docs whose primary correction is a "two distinct globals were conflated" disambiguation. Two-row table near top of doc, new dedicated subsection, NOTE block flags the CLAUDE.md batch correction. Established 2026-05-28 with ui-class-hierarchy.md.
metadata:
  type: feedback
---

# Load-bearing global-conflation correction pattern

When the v5 validation reveals that a pre-v5 doc conflated two distinct globals into one (e.g., "TopWindow at 0x0097e238" → actually TopWindow at 0x009878cc + PlayWindow at 0x0097e238), the correction is **load-bearing**: downstream readers may have built on the wrong attribution, and CLAUDE.md or other index docs likely carry the same conflation.

**Why this pattern matters:** A simple "fix the address" inline edit buries the disambiguation. Readers who already know the wrong fact will skim past the correction. The doc has to be loud about *both* globals existing and *which* claims attached to each. Skipping CLAUDE.md in the same pass is intentional (batched at family-close), but flagging the queued correction in the doc body keeps the breadcrumb visible.

## How to apply

When the evidence packet flags a global-conflation correction (typically marked C1 LOAD-BEARING in the packet):

### 1. Top-of-doc NOTE block names the corrected addresses explicitly

The first sentence after `status: partial` should be the disambiguation. Don't lead with the doc's scope or summary — lead with "the prior doc conflated X with Y."

Pattern phrasing: *"The prior doc's most load-bearing error — conflating TopWindow (`0x009878cc`) with PlayWindow (`0x0097e238`) — has been corrected; this also affects CLAUDE.md's Key Globals table (correction batched for engine-family-close)."*

### 2. Dedicated disambiguation subsection near the top

Add a `## TopWindow vs PlayWindow Globals` (or analogous) subsection **before** the main reference content. Two-row table:

| Global | Class | Created by | Singleton write | Role |
|--------|-------|------------|-----------------|------|
| `0x...` | A | FUN_... | `DAT_... = param_1` at 0x... | (role) |
| `0x...` | B | FUN_... | `DAT_... = param_1` at 0x... | (role) |

Follow the table with a "Key consequence:" paragraph that names every downstream-doc claim that was attached to the wrong global. The reader needs the consequences spelled out — they're who's going to fix things.

### 3. Flag the CLAUDE.md batch correction in the doc body

The NOTE block mentions CLAUDE.md's wrong row; the disambiguation subsection should name the specific row text (e.g., "`0x0097e238 TopWindow/MultiplayerGame ptr` should be `0x0097e238 PlayWindow / Game state ptr`") so the family-close batch operator can grep for it. Don't rely on the validation log alone — the doc body is the more durable reminder.

### 4. Cross-doc impacts section in the tracker entry enumerates all touched docs

The §6 tracker entry's "Cross-doc impacts" subsection should list (1) CLAUDE.md row(s) needing correction, (2) any agent-memory files that needed fixing in the same pass (e.g., struct-skeletons-20260528.md's wrong +0x70 offset for MultiplayerGame.playerSlots), (3) companion docs that would benefit from a cross-link addition but are deferred. The QUEUED label on the CLAUDE.md item is important — campaign convention is family-close batch, not per-doc edits.

### 5. Status stays `partial` even when no `confidence: low` rows exist

A load-bearing correction reshapes the doc's foundation; `partial` signals "the correction has landed but downstream catch-up hasn't happened yet." This is the same rule from [[leaf-doc-render-patterns]] §7 — corrections (not just demotions) keep the doc at `partial`. Promotion to `verified` waits for the family-close batch.

## When to use

Apply when:

- A pre-v5 doc collapsed two distinct globals/classes/addresses into one identity.
- Other docs (CLAUDE.md, sibling docs in the same family) likely carry the same conflation.
- The correction changes which class owns which downstream claims (e.g., MultiplayerGame extends PlayWindow, NOT extends TopWindow).
- The pre-v5 doc had labels/sections built around the wrong attribution that need to be retitled or repositioned.

## Related

- [[leaf-doc-render-patterns]] §1 (top-of-doc NOTE block) and §7 (status-partial-on-correction)
- [[verified-status-criteria]] — why this doc stays at `partial`
- [[catalog-row-disposition-tree]] — for the dropped-class rows (STWidget, STRadioGroup as type-0x80EA attribution)

## Sub-pattern: cyclic permutation (addresses right, labels inverted)

A variant of the pattern: instead of two globals being collapsed into one, **N distinct globals at adjacent addresses got their labels rotated**. The addresses are correct; the names are inverted into a cyclic permutation. This is **higher-stakes** because every downstream doc's gate logic still works (the binary uses addresses, not names), so the bug is silent until someone reads a flag-name claim and reasons about it semantically.

**Rendering differences from the canonical pattern:**

1. **Don't restructure the body** — addresses haven't moved, so section anchors are still valid. The fix is a NOTE block + a corrected reference table, full stop.
2. **Place the CRITICAL READING NOTE *above* the table, not below it** — readers grepping for an address need to know the labels are corrected *before* they read the row. A trailing NOTE gets missed.
3. **Add a separate "cascade correction" NOTE *below* the table** that names (a) the binary truth-source function with its address, (b) the count of affected downstream docs, (c) the disposition ("mass-fix DEFERRED to future sweep"), and (d) the verification memo path. The two-NOTE sandwich frames the table as the canonical reference even though the broader doc corpus is stale.
4. **Tracker §4 entry flips from "CASCADE VERIFICATION IN FLIGHT" to "CONFIRMED YYYY-MM-DD" with binary-truth one-liner** — keep the entry, don't delete it (CASCADE markers earn their place in §4 even when CLOSED, because they document the resolution path for the next analyst who hits a similar cyclic-permutation pattern).
5. **Mass downstream fix is explicitly deferred** — DO NOT attempt to fix ~28 docs in the same pass. The cascade-correction NOTE in CLAUDE.md is the durable warning; the future sweep is its own task.

## Examples

- **ui-class-hierarchy.md (2026-05-28):** TopWindow at 0x009878cc vs PlayWindow at 0x0097e238. Pre-v5 doc + CLAUDE.md both said TopWindow lived at 0x0097e238; PlayWindow (the Game state object) was misidentified as "the Game object stored at g_TopWindow." Correction also revealed that PlayWindow is NOT a MainWindow (no type-ID at +0x4C), which reshaped the doc's "TopWindow children" and "MainWindow Type IDs" sections.
- **CLAUDE.md Key Globals flag attributions (2026-05-28, cyclic-permutation sub-pattern):** 0x0097FA88 / 0x0097FA89 / 0x0097FA8A pre-v5 were labeled IsClient / IsHost / IsMultiplayer; binary truth (per MultiplayerGame_Start ~0x00438C70 byte-level disasm in `cascade-verification-flags-20260528.md`) is HasLocalPlayer / GameLive / IsHost — a cyclic permutation. ~28 downstream docs use the wrong labels but correct addresses. Fix applied: CRITICAL READING NOTE above the table + cascade-correction NOTE below the table + v5-validation-status.md §4 entry flipped from "CASCADE VERIFICATION IN FLIGHT" to "CONFIRMED 2026-05-28". Mass downstream label-fix deferred.
