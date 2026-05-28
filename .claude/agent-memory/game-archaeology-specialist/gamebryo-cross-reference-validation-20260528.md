---
name: gamebryo-cross-reference-validation-20260528
description: v5 validation of docs/engine/gamebryo-cross-reference.md — confirmed nif.xml version-conditional field claims, refuted the MWSE-equivalence size claim (NI 3.1 NiAVObject = 0xC8, NOT 0x90; NiNode = 0xE8, NOT 0xB0). Cross-source doc methodology distilled.
metadata:
  type: project
---

# Gamebryo Cross-Reference Validation — 2026-05-28

Phase 1-3 v5 validation of `docs/engine/gamebryo-cross-reference.md` (mid #7 in engine family). This is the first **cross-source** doc validated under v5 — most claims are about external corpora (Gb 1.2 source, MWSE 4.0 headers, niftools nif.xml), not stbc.exe. Different validation calculus.

## Top-Level Findings

1. **The MWSE-equivalence size claim is wrong for NiAVObject and NiNode.** Doc states "NI 3.1 sizes confirmed via MWSE static_assert checks (identical to NI 4.0.0.2)". The actual NI 3.1 sizes per stbc.exe allocation evidence:
   - NiObject: **0x08** ✓ matches MWSE
   - NiObjectNET: **0x14** ✓ matches MWSE
   - NiAVObject: **0xC8** (doc claims 0x90) — **+0x38 (56 bytes) larger** than MWSE 4.0
   - NiNode: **0xE8** (doc claims 0xB0) — **+0x38 (56 bytes) larger** than MWSE 4.0
   - NiGeometry: **0xE0** (doc had no row — added)
   - NiTriShape: **0xE4** (doc had no row — added)

   The +0x38 delta lives entirely in the NiAVObject portion (NiNode-specific bytes are 0x20 in both NI 3.1 and MWSE 4.0). This is consistent with nif.xml: V3.1 NiAVObject has Velocity (Vector3, until 4.2.2.0), Has Bounding Volume + Bounding Volume (until 4.2.2.0) — fields removed by NI 4.0. The doc's own nif.xml citations predict this result; the MWSE footnote is the lie.

   **Resolution to the question (a/b/c):** Answer is **(a)** — NI 3.1 and NI 4.0.0.2 have **different** sizes. The MWSE footnote claim is wrong. The MWSE struct sizes match for **NiObject and NiObjectNET only** because those classes did NOT have V3.1-only fields removed. The equivalence is per-class, not universal.

2. **All 7 nif.xml version-conditional field claims verified** by direct file:line citations:
   - line 3364: `Extra Data` Ref, `since="3.0" until="4.2.2.0"` ✓ (NiObjectNET section claim)
   - line 3487: `Velocity` Vector3, `until="4.2.2.0"` ✓ (NiAVObject Velocity claim)
   - line 3492: `Has Bounding Volume` bool, `since="3.0" until="4.2.2.0"` ✓
   - line 3493: `Bounding Volume` cond on Has Bounding Volume ✓
   - line 3494: `Collision Object` ref, `since="10.0.1.0"` ✓ (absent in V3.1)
   - line 3608: `Target` Ptr to NiObjectNET, `since="3.3.0.13"` ✓ (absent in V3.1)
   - line 3609: `Unknown Integer` uint, `until="3.1"` ✓ (V3.1-only)

3. **nif.xml line references all hold.** Spot-checked NiKeyframeData (4327), NiBezierTriangle4 (5319), NiBezierMesh (5333), NiBone (4392) — all match.

4. **NiObjectNET ExtraData "single ptr (NI 3.1) vs array (Gb 1.2)" claim verified.**
   - STBC NiObjectNET ctor (FUN_007dac80) writes 1 ptr at offset +0xC (matches MWSE 4.0 layout)
   - Gb 1.2 NiObjectNET.h declares `NiExtraData** m_ppkExtra` + `unsigned int m_uiExtraDataSize` (lines 143-144) — at least 8 bytes of fields
   - Direction of "+8 bytes" claim is correct

5. **NiAVObject CollisionObject claim verified.**
   - Gb 1.2 NiAVObject.h has `NiCollisionObjectPtr m_spCollisionObject` (line 248) — 4 bytes
   - nif.xml says `Collision Object` `since="10.0.1.0"` — absent in V3.1
   - Direction correct

6. **NiAVObject Velocity field claim verified.**
   - Gb 1.2 NiAVObject.h has NO Velocity field (grep confirmed)
   - nif.xml line 3487: present in NI 3.1 (Vector3, until 4.2.2.0)
   - Direction correct

7. **42 / 21 arithmetic doesn't add up.** Counting the doc table:
   - Bezier subsystem: 11 classes (doc says 11) ✓
   - Old Animation: lists 9 rows (doc title says 8) — **misnumbered by 1**
   - Old Textures: 5 ✓
   - Old Rendering: 8 ✓
   - NI 3.1-Specific Nodes: 3 ✓
   - Audio: 4 ✓
   - Misc: 5 ✓
   - Total = 11+9+5+8+3+4+5 = **45** (doc claims 42)
   - With NiKeyframeManager moved to "matched": 44
   - With-nif.xml count: 2+7+4+2+2+0+3 = 20 (doc claims 21)
   - The 42/21 numbers in the summary don't match the table contents. Documentation drift.

8. **NiKeyframeManager mis-categorized.** The doc lists it under "Misc (5 classes) — Misc" as "Replaced by NiControllerManager. Runtime-only". But `engine/gamebyro-1.2-source/CoreLibs/NiAnimation/NiKeyframeManager.h` EXISTS in Gb 1.2 (preserved as deprecated — file content "NOTICE: This class is deprecated. You should use NiControllerManager instead"). So it should be in the "matched, deprecated" category, not "NI 3.1-only".

9. **The MWSE field-offset table (line 355) is similarly off** for NiAVObject. STBC ctor writes worldBound translation at byte 0x54 (param_1[0x15]); MWSE puts worldBoundOrigin at 0x1C. The MWSE offsets are NOT directly applicable to STBC NiAVObject because every field after the V3.1-removed fields is shifted.

## Per-Section Verdict

| Section | Verdict | Notes |
|---------|---------|-------|
| Compatibility Notes (NiObjectNET) | ✓ direction correct, evidence holds | nif.xml cites verified; Gb 1.2 source verified |
| Compatibility Notes (NiAVObject CollisionObject) | ✓ correct | nif.xml + Gb 1.2 source verified |
| Compatibility Notes (NiAVObject Velocity) | ✓ correct | Same |
| Compatibility Notes (NiTimeController) | ✓ correct | nif.xml lines 3608-3609 verified |
| Core Hierarchy Offset Comparison table | ✗ WRONG for NiAVObject (0x90 → 0xC8) and NiNode (0xB0 → 0xE8) | Stbc.exe allocation evidence + companion doc |
| MWSE-equivalence footnote (line 53) | ✗ WRONG — sizes are NOT identical between NI 3.1 and MWSE 4.0 | Same |
| Matched Classes (87) — list of Gb 1.2 source paths | ✓ spot-checked NiObject/NiNode/NiBSPNode/NiAlphaProperty/NiTriShape — all present in Gb 1.2 | Glob confirmed |
| NI 3.1-Only Classes (42) — Bezier subsystem | ✓ NiBezierMesh + NiBezierTriangle missing from Gb 1.2 (Glob confirmed) | |
| NI 3.1-Only Classes — NiBone, NiCollisionSwitch, NiSkinController | ✓ none in Gb 1.2 (Glob confirmed) | |
| NI 3.1-Only Classes — NiKeyframeManager | ✗ EXISTS in Gb 1.2 (deprecated, NiAnimation/NiKeyframeManager.h) | Mis-categorized; move to matched-deprecated |
| Class count math (42 = 11+8+5+8+3+4+5) | ✗ adds to 45, not 42 (Old Animation has 9 rows, not 8 as header claims) | |
| "21 of 42 have nif.xml" | ✗ recount gives 20 of 45 | |
| 7 nif.xml version-conditional field claims | ✓ all verified line-by-line | |
| MWSE field offsets (line 355) | ✗ NOT directly applicable to STBC — offsets shifted by V3.1-only field presence | |
| Reference Priority table (line 429) | ⚠ misleading — claims MWSE offsets are "Exact" for STBC; actually only true for NiObject/NiObjectNET | |
| Practical Usage Guide | ⚠ "Use MWSE headers for field offsets" advice is dangerous for NiAVObject and derived | |

## Object Size Resolution (Critical)

The doc's table claims:
- NiAVObject NI 3.1 = 0x90, MWSE = 0x90 (identical), Gb 1.2 = ~0x9C
- NiNode NI 3.1 = 0xB0, MWSE = 0xB0 (identical), Gb 1.2 = ~0xC0+

Stbc.exe allocation evidence (FUN_007e5450 NiNode factory, FUN_007f31f0 NiTriShape factory):
- NiAVObject NI 3.1 = **0xC8** (derived from NiNode allocation 0xE8 - NiNode-specific 0x20)
- NiNode NI 3.1 = **0xE8** (direct: `FUN_00718cb0(0xe8)`)
- NiGeometry NI 3.1 = **0xE0** (derived from NiTriShape factory + NiGeometry ctor)
- NiTriShape NI 3.1 = **0xE4** (direct: `FUN_00718cb0(0xe4)`)

Where the +0x38 delta lives (NI 3.1 vs MWSE 4.0 for NiAVObject):
- Velocity (Vector3) = 12 bytes
- Has Bounding Volume (bool) = 1-4 bytes
- Bounding Volume (BoundingVolume) = ~36-40 bytes (sphere or box variant + tag)
- Total ≈ 0x38 ✓ matches the observed delta

Conclusion: **NI 3.1 NiAVObject is LARGER than MWSE 4.0, not equal.** The doc's footnote claim is backwards.

## Methodology Notes for Future Validators of Cross-Source Docs

This is the first **cross-source** doc validated under v5. Different patterns:

1. **External corpus claims need file:line citations** (e.g., `engine/nif.xml:3487`), not Ghidra addresses. Treat these as `confidence: high` when file existence + content is directly verified.
2. **STBC-anchored claims need Ghidra addresses** as usual. In this doc, those are the size/offset rows.
3. **Cross-source disagreements (MWSE says X but STBC says Y) are common.** Default to STBC as authority for STBC docs. The external corpus is a *reference*, not the *spec*.
4. **Categorical claims ("42 NI 3.1-only", "21 of 42") need recounting** — pre-v5 docs tend to drift on these counts.
5. **Inheritance claims about which fields exist in which version need nif.xml `since`/`until` verification** — niftools' XML is the canonical source for serialization-level field presence.

## Key Addresses To Remember

| Address | What |
|---------|------|
| FUN_007d87a0 | NiObject ctor — writes 2 fields, confirms 0x08 size |
| FUN_007dac80 | NiObjectNET ctor — writes 4 fields, confirms 0x14 size |
| FUN_007dc0c0 | NiAVObject ctor — writes up to byte 0xC0; size is 0xC8 (via NiNode delta) |
| FUN_007edd10 | NiGeometry ctor — writes fields up to byte 0xDE; size 0xE0 |
| FUN_007ef260 | NiTriBasedGeom ctor — writes 1 field at 0xE0; size 0xE4 |
| FUN_007e5450 | NiNode factory — `NiAlloc(0xE8)` direct |
| FUN_007f31f0 | NiTriShape factory — `NiAlloc(0xE4)` direct |
| FUN_00718cb0 | NiAlloc (canonical, per nirtti-factory-validation) |

## Open Questions

- The "87 matched + 42 NI 3.1-only = 129" arithmetic is correct (87 + 42 = 129) but the subcategory rollup of 42 doesn't reconcile to its table contents (table sums to 45). One row (NiKeyframeManager) is mis-categorized. Other potential miscategorizations not yet exhaustively audited.
- The actual NiBound / BoundingVolume struct size in NI 3.1 — observable from the NiAVObject ctor's writes to indexes [0x15]-[0x18] (FUN_008136c0 helper). If it's an inline sphere (4 floats = 0x10) or box (more) determines whether the +0x38 delta is fully explained.
- Whether MWSE-claimed field offsets work for any class BEYOND NiObject/NiObjectNET — likely NO for any NiAVObject descendant.

## What Goes In The Header

- validated: 2026-05-28
- methodology: FUNCTION_DOC_WORKFLOW_V5
- binary: STBC.exe, size 6394712, base 0x00400000
- status: `partial` — many claims valid but the headline size table is wrong and the doc's primary "Use MWSE for offsets" advice is misleading for NiAVObject and below
- supersedes: prior undated
- companions: netimmerse-vtables.md (verified — anchor for sizes), nirtti-factory-catalog.md, rtti-class-catalog.md, function-map.md, v5-validation-status.md
