---
name: leaf-doc-render-patterns
description: Render patterns for leaf docs in the engine family (event system, UI hierarchy, decompiled-function notes). Anchored-vs-inferred methodology section, two-RTTI-systems disclosure, lazy/two-level indirection diagrams. Established 2026-05-28 with event-system-architecture.md.
metadata:
  type: feedback
---

# Leaf doc render patterns

Leaf docs sit on top of validated foundation docs and describe a subsystem's wiring (event dispatch, UI inheritance, etc.). They are typically smaller than catalogs, have fewer addresses, and tend to carry pre-v5 inferred method names ("Save/Load/Fixup", internal C++ method names) that don't anchor to anything in the binary's string table.

**Why these patterns matter:** Leaf docs were written from behavioural observation rather than string-table extraction. Pre-v5 they carried plausible-sounding method names that turn out to be invented. v5 validation either drops them or describes the behaviour without the name. The doc looks smaller-but-truer afterwards; the campaign should expect leaf docs to retain `status: partial` for a release cycle because corrections (not just demotions) reshape the doc's foundation.

## How to apply

When rendering a leaf doc that the evidence packet has corrected (not just confirmed), follow this pattern set:

### 1. Top-of-doc NOTE block lists what was dropped

Don't bury the methodology change in a sub-section. The NOTE block at the top of the body should:
- State `status: partial` and why (corrected claims reshaped the foundation, not just lowered confidence).
- Enumerate the **specific dropped name groups** by name (so a reader searching for "SaveBroadcastHandlers" finds this NOTE telling them it's gone and why).
- Point at the v5 evidence header guide.

Pattern phrasing: *"Several pre-v5 method-name claims (`SaveBroadcastHandlers`, `LoadBroadcastHandlers`, ..., the `TGConditionHandler::AddEntry/InsertSorted/...` family) were dropped because they had no string anchor in the binary. The anchored SWIG API names are listed in their place where applicable."*

### 2. Anchored vs Inferred Method Names methodology section

This is the second-time-we've-explained-this section. Keep it short (2 paragraphs) and link to the v5 evidence header guide. The point is:
- SWIG wrapper names are the most reliable string-table source for method names.
- Methods that are purely internal to C++ (not Python-bound, not in debug prints) won't appear in the string table.
- Behaviour-without-name is the fallback: "the handler-cleanup routine called when objects are destroyed" instead of inventing a name.

This is a methodology section, not a reference section — phrase it as "v5-honest doc only names a method when..." rather than as a list.

### 3. Universal-slot disclosure when applicable

If the evidence packet identifies a vtable slot that's inherited unchanged across many classes (e.g., TGEventHandlerObject slot 8 = `FUN_006f15c0` InvokePythonHandler, universal across 9 vtables in the Ship chain), cross-link to the foundation doc that anchors the slot, not to the slot itself. The foundation doc owns the slot identity; the leaf doc reuses it.

Pattern: "TGEventHandlerObject vtable slot 8 (offset +0x20) = `FUN_006f15c0` — universal across all TGEventHandlerObject subclasses. Cross-confirmed in [tg-hierarchy-vtables.md](tg-hierarchy-vtables.md)."

### 4. Two-level pointer indirection diagram

When the validation reveals an indirection that the pre-v5 doc described as flat embedding (e.g., "37-bucket hash at +0x10" → actually two levels of indirection), use an ASCII diagram in the body. Don't bury it in prose:

```
TGEventHandlerObject*
  + 0x10  ────►  TGInstanceHandlerTable (0x14 bytes, allocated lazily)
                   +0x00  vtable
                   +0x0C  ────►  37-bucket hash array (0x94 bytes, allocated separately)
```

Two-level indirection is a common pattern in this codebase (NiRTTI factory hash table, TGInstanceHandlerTable, likely others). Diagram makes it scannable.

### 5. Dual sub-struct table for shared-vtable containers

When the ctor writes the same vtable at two offsets (e.g., `TGConditionHandler` ctor writes vtable at `param_1[0]` AND `param_1[6]`), the container holds embedded sub-structs of the same shape. Render as an offset table covering both sub-structs and the reentrant flag at the end. Don't try to compress this into prose; the offset table is the evidence.

### 6. Two RTTI Systems sub-section when class hierarchy uses multiple mechanisms

The TG hierarchy uses two RTTI mechanisms: integer-tag (TGObject chain, slot 1 returns `mov eax, IMM ; ret`) and string-pointer (TGEvent, slot 1 returns ptr to "_p_ClassName"). A reader assuming a single system will read slot 1 of the other system as garbage. Surface this as its own subsection when both appear in the doc — don't tuck it into one class's reference section.

### 7. Status partial, not verified, when corrections reshape the foundation

When the validation **corrects** a load-bearing claim (not just confirms or lowers it), the doc becomes `status: partial` even if there are no `confidence: low` rows. Correction = the doc's prior foundation was wrong, which means downstream readers may have built on it. Partial signals "newer than pre-v5 but not yet through the next-cycle review." Promotion to verified comes after the correction has settled and downstream docs have caught up.

Distinguish from: a foundation doc with pattern-extrapolation reaches `verified` at medium confidence per [[verified-status-criteria]]. Leaf docs with corrections do not.

### 8. Open Questions and Documentation Debt section enumerates next-pass targets

Leaf docs end with an explicit list of follow-ups, each phrased as a settled-by-X question. The campaign uses this as the per-doc backlog. 6-ish items is typical (event-system-architecture.md has 6 — TGEvent type-tag, singleton init site, RegisterHandler* slot positions, second TGCallback vtable per-slot semantics, queue API names, sort key).

## When to use

Apply this pattern set when the leaf doc:
- Has pre-v5 method names that mostly didn't survive string-table validation.
- Has at least one load-bearing correction (a claim was demoted from "fact" to "wrong").
- Cross-references foundation docs already at `verified` (so universal-slot disclosures work).
- Was originally written from observation rather than from string extraction.

## Related

- [[v5-named-function-convention]] for the catalog-doc equivalent
- [[verified-status-criteria]] for when leaf docs can promote to `verified`
- [[tg-vtable-render-patterns]] for the foundation-side type-ID constants table that leaf docs cite
