---
name: engine-family-close-batch
description: After engine doc #10 lands, four batched tasks must run to close the family — CLAUDE.md two-row globals correction, CLAUDE.md naming-coverage refresh, README index check, netimmerse-vtables.md NiAVObject size reconciliation
metadata:
  type: project
---

# Engine family close batch

**Fact:** With docs/engine/decompiled-functions.md validated 2026-05-28, all 10 engine docs are v5-validated (5 `verified`, 5 `partial`). Four cross-doc impacts have been deferred across the family-close batch — they are documented in the §6 entries of each contributing doc but were not modified in-place to keep companion-doc state stable during the campaign.

**Why:** The campaign convention is "modify only the doc being validated; flag cross-doc impacts for batch resolution at family-close". This prevents the campaign from amplifying drift through eager cascade edits. Family-close is when the cascade lands.

**How to apply:** When the orchestrator begins the engine-family-close commit batch, run these four tasks:

1. **CLAUDE.md Key Globals two-row correction** (source: doc #9 ui-class-hierarchy.md)
   - Existing row `0x0097e238 | TopWindow/MultiplayerGame ptr` → change to `0x0097e238 | PlayWindow / Game state ptr`
   - Add new row: `0x009878cc | TopWindow (root scene container)`
   - Reason: TopWindow and PlayWindow are two distinct globals; the pre-v5 doc conflated them.

2. **CLAUDE.md naming-coverage refresh** (source: doc #6 function-mapping-report.md)
   - "~15,134 functions named/excluded (83%)" → current 25.8% (4,797 of 18,581)
   - "2,348 functions, 393 classes" claim for ghidra_annotate_globals.py outputs → reflect current state (annotation scripts currently unapplied)
   - Affects the Documentation Index row for function-mapping-report.md and the script-output claims in the "Ghidra Annotation Scripts" section.

3. **docs/engine/README.md index check**
   - Verify all 10 engine docs are indexed (tg-hierarchy-vtables, event-system-architecture, ui-class-hierarchy were added during earlier docwriter passes; confirm presence).
   - Refresh captions where v5 validation changed the doc's primary claim (e.g., function-mapping-report.md's "25.8%" was already updated during doc #6 pass).

4. **netimmerse-vtables.md NiAVObject 0xC4 → 0xC8 reconciliation** (source: doc #7 gamebryo-cross-reference.md)
   - netimmerse-vtables.md is `verified` but lists NiAVObject object size as 0xC4 (medium confidence, ctor field-write derivation).
   - gamebryo-cross-reference.md validation found 0xC8 (more rigorous, NiNode 0xE8 minus NiNode-specific 0x20).
   - Resolution: bump netimmerse-vtables.md to 0xC8 with a note that the +4 delta is the helper `FUN_008136c0` call at end of NiAVObject ctor.
   - Both docs already cross-reference each other; this is the canonical reconciliation per v5 reconciliation rules (newer date + higher rigor wins).

Related: [[address-first-authoring]] (campaign-wide pattern note from doc #10), [[verified-status-criteria]] (what kept the 5 partials from reaching verified), [[catalog-row-disposition-tree]] (the four-bucket decision tree used across the campaign).
