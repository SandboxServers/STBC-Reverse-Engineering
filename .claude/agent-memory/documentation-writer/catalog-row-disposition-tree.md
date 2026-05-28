---
name: catalog-row-disposition-tree
description: Decision tree for handling pre-v5 catalog rows during re-validation — keep / demote / move to internal-only / drop
metadata:
  type: feedback
---

When a pre-v5 catalog doc (rtti-class-catalog.md style) has rows that don't survive the evidence packet, sort them into four buckets — don't apply a uniform treatment.

**Bucket 1 — KEEP with `[v5-validated YYYY-MM-DD]` tag.** Row has a confirmed canonical anchor in the evidence packet. Update the address if it changed (e.g., the prior catalog had a `_p_` SWIG substring address but the bare-string address is now known), tag the row.

**Bucket 2 — KEEP-AS-IS (uncertified).** Row's anchor wasn't re-derived this pass but the evidence packet didn't contradict it. Leave the address; do not add a `[v5-validated]` tag. Surface as documentation debt in the validation log under "pending".

**Bucket 3 — MOVE to "Internal C++ classes (no SWIG binding)" subsection.** Row is a real C++ class per the project's other evidence (transport-layer.md, network-protocol.md, vtable docs) but has **no bare class-name string** in the binary because it's not SWIG-bound to Python. The prior catalog's cited address was actually a `_p_<class>` SWIG pointer-type substring, not a class-identity anchor.
- Re-anchor via factory ID, vtable address, or "internal C++ class — no SWIG binding" note.
- Format: `TGBufferStream  (internal C++ class — no SWIG binding) vtable 0x008958D0 [v5-validated 2026-05-28]`
- Do NOT cite the old `_p_` substring address as the row's "RTTI string address" — that's misleading.

**Bucket 4 — DROP entirely.** Row is fictional / speculative-by-analogy. Common patterns:
- UI widgets named after Windows conventions (TGScrollBar, TGProgressBar, TGComboBox) without any matching string.
- Manager-suffixed classes (TGRenderManager, TGAudioManager) pattern-matched on naming convention.
- Misc abstractions (TGdb, TGStringStream) with no xref or string evidence.

Surface the dropped rows in the validation log so future readers see what was scrubbed. **Do not silently delete** — name the dropped rows.

**Why this matters:** The v5 standard says "no claim without an address". A row whose address is a `_p_` substring is technically address-anchored but the claim "this is the class-name location" is wrong. Re-anchor (Bucket 1) or demote to "no bare string" (Bucket 3). A row with no evidence at all is a fictional claim — drop it (Bucket 4), don't carry it as `confidence: low`.

**How to apply:**
- The evidence packet should partition the pre-v5 rows into the four buckets explicitly. If it doesn't, push back to the source agent before publishing.
- The top-of-doc `> [!NOTE]` block should call out the count: "Prior catalog claimed X rows; this pass dropped N as fictional, moved M to internal-only, re-anchored K." Honesty about scope of changes.
- New subsection "Internal C++ classes (no SWIG binding)" is a reusable structural pattern — likely applies to other catalog docs (nirtti-factory-catalog.md may need it; check on its pass).

**Related:** [[v5-named-function-convention]], [[v5-foundation-claim-patterns]]
