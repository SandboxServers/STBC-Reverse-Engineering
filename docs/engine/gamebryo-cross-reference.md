> [docs](../README.md) / [engine](README.md) / gamebryo-cross-reference.md

---
title: Gamebryo 1.2 Source Cross-Reference
type: reference
audience: re-engineer
validated: 2026-05-28
methodology: FUNCTION_DOC_WORKFLOW_V5
binary:
  name: STBC.exe
  size: 6394712
  base: 0x00400000
status: partial
evidence:
  - claim: "NiObject size = 0x08 in NI 3.1"
    address: 0x007d87a0
    function: FUN_007d87a0
    confidence: high
    note: "Ctor writes 2 fields (vtable + counter increment). Matches MWSE 4.0.0.2 size. [v5-validated 2026-05-28]"
  - claim: "NiObjectNET size = 0x14 in NI 3.1"
    address: 0x007dac80
    function: FUN_007dac80
    confidence: high
    note: "Ctor writes 4 fields ending at byte 0x10. Matches MWSE 4.0.0.2 size. Extra Data is a single ptr at +0xC (not array). [v5-validated 2026-05-28]"
  - claim: "NiAVObject size = 0xC8 in NI 3.1 — NOT 0x90"
    address: 0x007dc0c0
    function: FUN_007dc0c0
    confidence: high
    note: "Ctor writes up to byte 0xC0 with helper FUN_008136c0 completing layout; derived from NiNode allocation 0xE8 minus NiNode-specific 0x20. Differs from MWSE 4.0 (0x90) by +0x38 (V3.1-only fields: Velocity + Has Bounding Volume + Bounding Volume). [v5-validated 2026-05-28]"
  - claim: "NiNode size = 0xE8 in NI 3.1 — NOT 0xB0"
    address: 0x007e5450
    function: FUN_007e5450
    confidence: high
    note: "Factory calls NiAlloc(0xE8) directly. Differs from MWSE 4.0 (0xB0) by +0x38 (delta lives entirely in NiAVObject portion). [v5-validated 2026-05-28]"
  - claim: "NiGeometry size = 0xE0 in NI 3.1"
    address: 0x007edd10
    function: FUN_007edd10
    confidence: high
    note: "Derived from NiTriShape factory allocation 0xE4 minus NiTriBasedGeom-specific 4-byte field. [v5-validated 2026-05-28]"
  - claim: "NiTriBasedGeom size = 0xE4 in NI 3.1"
    address: 0x007ef260
    function: FUN_007ef260
    confidence: high
    note: "Ctor adds 1 field at byte 0xE0 over NiGeometry. [v5-validated 2026-05-28]"
  - claim: "NiTriShape size = 0xE4 in NI 3.1"
    address: 0x007f31f0
    function: FUN_007f31f0
    confidence: high
    note: "Factory calls NiAlloc(0xE4) directly. Factory only overwrites the NiTriBasedGeom vtable with the canonical NiTriShape vtable; no additional fields added. [v5-validated 2026-05-28]"
  - claim: "NiObjectNET ExtraData = single Ref (NiExtraData), present 3.0—4.2.2.0"
    address: null
    function: null
    confidence: high
    note: "engine/nif.xml:3364 — Ref to NiExtraData, since=3.0 until=4.2.2.0. Confirms NI 3.1 uses a single ptr, not an array. [cross-source-2026-05-28]"
  - claim: "NiAVObject Velocity field present in V3.1 (removed by 4.2.2.0)"
    address: null
    function: null
    confidence: high
    note: "engine/nif.xml:3487 — Vector3, until=4.2.2.0. Confirms 12 bytes of V3.1-only Velocity layout in NiAVObject. [cross-source-2026-05-28]"
  - claim: "NiAVObject Has Bounding Volume + Bounding Volume present in V3.1 (removed by 4.2.2.0)"
    address: null
    function: null
    confidence: high
    note: "engine/nif.xml:3492 (bool) and 3493 (BoundingVolume variant), since=3.0 until=4.2.2.0. The bool + variant together contribute ~40-44 bytes of V3.1-only NiAVObject layout. [cross-source-2026-05-28]"
  - claim: "NiAVObject Collision Object absent in V3.1 (added 10.0.1.0)"
    address: null
    function: null
    confidence: high
    note: "engine/nif.xml:3494 — Ref, since=10.0.1.0. NI 3.1 stbc.exe has no CollisionObject member. [cross-source-2026-05-28]"
  - claim: "NiTimeController Target ptr absent in V3.1 (added 3.3.0.13)"
    address: null
    function: null
    confidence: high
    note: "engine/nif.xml:3608 — Ptr to NiObjectNET, since=3.3.0.13. NI 3.1 stores target via different mechanism. [cross-source-2026-05-28]"
  - claim: "NiTimeController Unknown Integer present only until 3.1"
    address: null
    function: null
    confidence: high
    note: "engine/nif.xml:3609 — uint, until=3.1. V3.1-only field replaced by the Target ptr in 3.3+. [cross-source-2026-05-28]"
  - claim: "Gamebryo 1.2 NiObjectNET uses ExtraData array (m_ppkExtra)"
    address: null
    function: null
    confidence: high
    note: "engine/gamebyro-1.2-source/CoreLibs/NiMain/NiObjectNET.h:143-144 — `NiExtraData** m_ppkExtra` + `unsigned int m_uiExtraDataSize`. At least 8 bytes more than NI 3.1's single ptr. [cross-source-2026-05-28]"
  - claim: "Gamebryo 1.2 NiAVObject has CollisionObject member"
    address: null
    function: null
    confidence: high
    note: "engine/gamebyro-1.2-source/CoreLibs/NiMain/NiAVObject.h:248 — `NiCollisionObjectPtr m_spCollisionObject`. 4 bytes. [cross-source-2026-05-28]"
  - claim: "Gamebryo 1.2 NiAVObject has no Velocity member"
    address: null
    function: null
    confidence: high
    note: "engine/gamebyro-1.2-source/CoreLibs/NiMain/NiAVObject.h — grep confirmed absent. Aligns with nif.xml `until=4.2.2.0` removal. [cross-source-2026-05-28]"
  - claim: "NiKeyframeManager exists in Gamebryo 1.2 as deprecated (was mis-categorized as NI 3.1-only)"
    address: null
    function: null
    confidence: high
    note: "engine/gamebyro-1.2-source/CoreLibs/NiAnimation/NiKeyframeManager.h:27 — header file comment 'NOTICE: This class is deprecated. You should use NiControllerManager instead.' Moved from NI 3.1-only Misc to Matched (deprecated). [cross-source-2026-05-28]"
  - claim: "5 sampled 'matched' classes confirmed present in Gb 1.2"
    address: null
    function: null
    confidence: high
    note: "Glob-verified: NiObject, NiNode, NiBSPNode, NiAlphaProperty, NiTriShape all have headers under engine/gamebyro-1.2-source/CoreLibs/. [cross-source-2026-05-28]"
  - claim: "5 sampled 'NI 3.1-only' classes confirmed absent from Gb 1.2"
    address: null
    function: null
    confidence: high
    note: "Glob-verified absent: NiBezierMesh, NiBezierTriangle4, NiBone, NiCollisionSwitch, NiSkinController. [cross-source-2026-05-28]"
  - claim: "nif.xml line citations for NI 3.1-only class structs hold"
    address: null
    function: null
    confidence: high
    note: "Spot-checked: NiKeyframeData (line 4327), NiBezierTriangle4 (line 5319), NiBezierMesh (line 5333), NiBone (line 4392). All match doc body. [cross-source-2026-05-28]"
  - claim: "BC NI 3.1 vtable slot 0 = GetRTTI; MWSE NI 4.0.0.2 slot 0 = destructor"
    address: 0x00898b94
    function: null
    confidence: high
    note: "Per netimmerse-vtables.md (verified): NiObject vtable 0x00898b94 slot 0 returns RTTI ptr; scalar_deleting_dtor at slot 10. MWSE headers document opposite layout. [v5-validated 2026-05-28]"
  - claim: "~80 of 87 'matched in Gb 1.2' rows are pattern-extrapolated"
    address: null
    function: null
    confidence: medium
    note: "5 of 5 spot-checks confirmed; remaining 82 follow same Glob-pattern verification approach. Per-row row sweep would promote to high. [cross-source-2026-05-28]"
  - claim: "~30 of 42 'NI 3.1-only' rows are pattern-extrapolated"
    address: null
    function: null
    confidence: medium
    note: "5 of 5 absence spot-checks confirmed; nif.xml line citations for ~20 of 42 directly verified. Remaining rows follow same Glob-confirmed-absent + nif.xml-cited pattern. [cross-source-2026-05-28]"
  - claim: "Subcategory rollup arithmetic does not reconcile (42 claimed; rows sum to 45 or 44)"
    address: null
    function: null
    confidence: medium
    note: "Old Animation header says 8 but lists 9 rows. After moving NiKeyframeManager to matched-deprecated: 44. Documentation debt — full row-by-row audit deferred. [cross-source-2026-05-28]"
  - claim: "nif.xml has field definitions for 20 of 42 NI 3.1-only classes"
    address: null
    function: null
    confidence: medium
    note: "Recount of doc body table. Prior 21-of-42 claim was inconsistent with NiKeyframeManager re-categorization. Full row-by-row audit deferred. [cross-source-2026-05-28]"
companions:
  - docs/engine/netimmerse-vtables.md
  - docs/engine/nirtti-factory-catalog.md
  - docs/engine/rtti-class-catalog.md
  - docs/engine/function-map.md
  - docs/engine/v5-validation-status.md
supersedes:
  - (prior undated revision)
---

# Gamebryo 1.2 Source Cross-Reference

Cross-reference of 129 NetImmerse 3.1 classes found in stbc.exe against Gamebryo 1.2 source
(`engine/gamebyro-1.2-source/`), MWSE reverse-engineered headers (`engine/mwse/`),
and niftools NIF format specification (`engine/nif.xml`).

> [!NOTE]
> This doc is `status: partial`. The core size table (NiObject through NiTriShape) is v5-validated against stbc.exe factory NiAlloc calls. The compatibility notes (NiObjectNET ExtraData direction, NiAVObject Velocity / Collision Object, NiTimeController Unknown Integer / Target) are cross-source-validated via file:line citations on `engine/nif.xml` and `engine/gamebyro-1.2-source/`. The bulk class-by-class match/diff lists (~80 of 87 "matched" rows + ~30 of 42 "NI 3.1-only" rows) carry `confidence: medium` by pattern extrapolation — 5 of 5 matched-class spot-checks and 5 of 5 absent-class spot-checks passed; one (NiKeyframeManager) was mis-categorized as "NI 3.1-only" and has been moved to matched-deprecated. See [docs/guides/v5-evidence-header.md](../guides/v5-evidence-header.md) for the standard.
>
> **Cross-source convention:** external-corpus claims (Gb 1.2 source, MWSE headers, nif.xml) are tagged `[cross-source-2026-05-28]` since they're verified via file:line citation rather than Ghidra addresses. Stbc.exe-anchored claims use the standard `[v5-validated 2026-05-28]` tag. The distinction lets you see provenance at a glance.

## Summary

| Metric | Count | % |
|--------|-------|---|
| NI classes in stbc.exe | 129 | 100% |
| **Match in Gamebryo 1.2** | **~88** | **~68%** |
| NI 3.1-only (no Gb 1.2 source) | ~44 | ~34% |
| — with nif.xml field definitions | 20 (of 42 documented; full audit deferred) | ~48% |
| — runtime-only (no serialization) | ~21 | ~50% |
| Renamed (audio) | 3 | — |

*Counts include the NiKeyframeManager re-categorization (moved from NI 3.1-only Misc to Matched/Deprecated). Subcategory arithmetic is subject to a row-by-row audit; see Open Questions.*

## Compatibility Notes

### NiObjectNET: ExtraData System Changed
- **NI 3.1 (stbc.exe)**: Single `NiExtraData*` pointer (linked list via `m_pNext`) [v5-validated 2026-05-28]
- **Gamebryo 1.2**: Array `NiExtraData** m_ppkExtra` + `m_uiExtraDataSize` + `m_uiMaxSize` [cross-source-2026-05-28: `engine/gamebyro-1.2-source/CoreLibs/NiMain/NiObjectNET.h:143-144`]
- **Impact**: All offsets in NiObjectNET and derived classes shift by +8 bytes in Gb 1.2
- **Confirmed by**: nif.xml field `Extra Data` (single Ref, `since="3.0" until="4.2.2.0"`) vs `Extra Data List` (array, `since="10.0.1.0"`) [cross-source-2026-05-28: `engine/nif.xml:3364`]

### NiAVObject: CollisionObject Added
- **NI 3.1**: No `m_spCollisionObject` member [v5-validated 2026-05-28: ctor FUN_007dc0c0]
- **Gamebryo 1.2**: Added `NiCollisionObjectPtr m_spCollisionObject` [cross-source-2026-05-28: `engine/gamebyro-1.2-source/CoreLibs/NiMain/NiAVObject.h:248`]
- **Impact**: +4 bytes shift at end of NiAVObject (Gb 1.2 direction)
- **Confirmed by**: nif.xml field `Collision Object` has `since="10.0.1.0"` — absent in 3.1 [cross-source-2026-05-28: `engine/nif.xml:3494`]

### NiAVObject: Velocity Field Present in V3.1
- nif.xml: `Velocity` field (Vector3) has `until="4.2.2.0"` — **present** in V3.1 [cross-source-2026-05-28: `engine/nif.xml:3487`]
- nif.xml: `Has Bounding Volume` + `Bounding Volume` have `since="3.0" until="4.2.2.0"` — **present** in V3.1 [cross-source-2026-05-28: `engine/nif.xml:3492`, `3493`]
- These fields were removed by NI 4.0 — see "Why MWSE Sizes Don't Match NI 3.1 for NiAVObject" below for the size implication.

### Why MWSE Sizes Don't Match NI 3.1 for NiAVObject

The +0x38 (56 bytes) delta between MWSE 4.0 NiAVObject (0x90) and NI 3.1 NiAVObject (0xC8) lives entirely in three V3.1-only fields that were removed in the 4.0 transition (and remain absent in MWSE's 4.0.0.2):

- **Velocity** (Vector3, 12 bytes) — `engine/nif.xml:3487`, `until="4.2.2.0"`
- **Has Bounding Volume** (bool, ~4 bytes with alignment) — `engine/nif.xml:3492`, `until="4.2.2.0"`
- **Bounding Volume** (BoundingVolume variant, ~36-40 bytes) — `engine/nif.xml:3493`, `until="4.2.2.0"`

Sum ≈ 0x38, matching the observed delta. NiObject and NiObjectNET match between NI 3.1 and MWSE 4.0 only because neither has V3.1-only fields; the prior doc's "MWSE = NI 3.1" footnote over-generalized this coincidence.

**Practical impact:** the MWSE NiAVObject field-offset comments (worldBound at +0x1C, parentNode at +0x18, etc.) do NOT translate to NI 3.1 stbc.exe. STBC writes worldBound at byte +0x54, not +0x1C, because the V3.1-only Velocity field is inserted between parentNode and worldBound. Use [netimmerse-vtables.md](netimmerse-vtables.md) for NI 3.1-specific NiAVObject field layout instead of MWSE headers.

### NiTimeController: V3.1-Specific Field
- nif.xml: `Unknown Integer` (uint) has `until="3.1"` — present only in V3.1 and earlier [cross-source-2026-05-28: `engine/nif.xml:3609`]
- nif.xml: `Target` (Ptr to NiObjectNET) has `since="3.3.0.13"` — **absent** in V3.1 (stored differently) [cross-source-2026-05-28: `engine/nif.xml:3608`]

### Core Hierarchy Offset Comparison

| Class | NI 3.1 (BC) Size | MWSE (NI 4.0) Size | Gb 1.2 Size | Delta | Source |
|-------|-------------------|---------------------|-------------|-------|--------|
| NiObject | 0x08 [v5-validated 2026-05-28] | 0x08 | 0x08 | match | FUN_007d87a0 |
| NiObjectNET | 0x14 [v5-validated 2026-05-28] | 0x14 | 0x1C | NI3.1/MWSE same; Gb1.2 +8 (extra data array) | FUN_007dac80 |
| NiAVObject | **0xC8** [v5-validated 2026-05-28] | 0x90 | ~0x9C | NI3.1 = MWSE +0x38 (V3.1-only fields) | FUN_007dc0c0 |
| NiNode | **0xE8** [v5-validated 2026-05-28] | 0xB0 | ~0xC0+ | NI3.1 = MWSE +0x38 | FUN_007e5450 NiAlloc(0xE8) |
| NiGeometry | **0xE0** [v5-validated 2026-05-28] | (not in MWSE Morrowind) | (varies) | — | FUN_007edd10 |
| NiTriBasedGeom | **0xE4** [v5-validated 2026-05-28] | (not in MWSE Morrowind) | (varies) | NiGeometry +4 | FUN_007ef260 |
| NiTriShape | **0xE4** [v5-validated 2026-05-28] | (varies) | (varies) | same as NiTriBasedGeom | FUN_007f31f0 NiAlloc(0xE4) |

*MWSE 4.0.0.2 sizes match NI 3.1 **only for NiObject and NiObjectNET**, which had no V3.1-only fields removed in the 4.0 transition. NiAVObject (MWSE 0x90 vs NI 3.1 0xC8) and NiNode (MWSE 0xB0 vs NI 3.1 0xE8) differ by +0x38, with the delta living in V3.1-only fields (Velocity + Has Bounding Volume + Bounding Volume) per `engine/nif.xml:3487`, `3492`, `3493`. Field offsets in MWSE headers do NOT translate to NI 3.1 NiAVObject and its descendants. For NI 3.1 sizes, use this table (verified against stbc.exe factory NiAlloc calls) and [netimmerse-vtables.md](netimmerse-vtables.md) for per-class vtable layout.*

---

## Matched Classes (~88) — Source Available

> [!NOTE]
> ~80 of these rows are pattern-extrapolated from 5 of 5 successful spot-checks (NiObject, NiNode, NiBSPNode, NiAlphaProperty, NiTriShape). Carries `confidence: medium`. A per-row Glob sweep would promote to high.

### Core Hierarchy
| Binary Class | Gb 1.2 Source | Notes |
|-------------|---------------|-------|
| NiObject | CoreLibs/NiMain/NiObject.h | Base identical [cross-source-2026-05-28] |
| NiObjectNET | CoreLibs/NiMain/NiObjectNET.h | ExtraData changed (see above) [cross-source-2026-05-28] |
| NiAVObject | CoreLibs/NiMain/NiAVObject.h | CollisionObject added in Gb 1.2; Velocity removed [cross-source-2026-05-28] |
| NiNode | CoreLibs/NiMain/NiNode.h | API matches, offsets shifted [cross-source-2026-05-28] |
| NiRefObject | CoreLibs/NiMain/NiRefObject.h | Identical |

### Scene Graph Nodes
| Binary Class | Gb 1.2 Source |
|-------------|---------------|
| NiBillboardNode | CoreLibs/NiMain/NiBillboardNode.h |
| NiBSPNode | CoreLibs/NiMain/NiBSPNode.h [cross-source-2026-05-28: Glob-verified] |
| NiLODNode | CoreLibs/NiMain/NiLODNode.h |
| NiSortAdjustNode | CoreLibs/NiMain/NiSortAdjustNode.h |
| NiSwitchNode | CoreLibs/NiMain/NiSwitchNode.h |

### Geometry
| Binary Class | Gb 1.2 Source |
|-------------|---------------|
| NiGeometry | CoreLibs/NiMain/NiGeometry.h |
| NiGeometryData | CoreLibs/NiMain/NiGeometryData.h |
| NiTriBasedGeom | CoreLibs/NiMain/NiTriBasedGeom.h |
| NiTriBasedGeomData | CoreLibs/NiMain/NiTriBasedGeomData.h |
| NiTriShape | CoreLibs/NiMain/NiTriShape.h [cross-source-2026-05-28: Glob-verified] |
| NiTriShapeData | CoreLibs/NiMain/NiTriShapeData.h |
| NiTriShapeDynamicData | CoreLibs/NiMain/NiTriShapeDynamicData.h |
| NiTriStrips | CoreLibs/NiMain/NiTriStrips.h |
| NiTriStripsData | CoreLibs/NiMain/NiTriStripsData.h |
| NiLines | CoreLibs/NiMain/NiLines.h |
| NiLinesData | CoreLibs/NiMain/NiLinesData.h |
| NiScreenPolygon | CoreLibs/NiMain/NiScreenPolygon.h |

### Properties (Render State)
| Binary Class | Gb 1.2 Source |
|-------------|---------------|
| NiProperty | CoreLibs/NiMain/NiProperty.h |
| NiAlphaProperty | CoreLibs/NiMain/NiAlphaProperty.h [cross-source-2026-05-28: Glob-verified] |
| NiDitherProperty | CoreLibs/NiMain/NiDitherProperty.h |
| NiFogProperty | CoreLibs/NiMain/NiFogProperty.h |
| NiMaterialProperty | CoreLibs/NiMain/NiMaterialProperty.h |
| NiShadeProperty | CoreLibs/NiMain/NiShadeProperty.h |
| NiSpecularProperty | CoreLibs/NiMain/NiSpecularProperty.h |
| NiStencilProperty | CoreLibs/NiMain/NiStencilProperty.h |
| NiVertexColorProperty | CoreLibs/NiMain/NiVertexColorProperty.h |
| NiWireframeProperty | CoreLibs/NiMain/NiWireframeProperty.h |
| NiZBufferProperty | CoreLibs/NiMain/NiZBufferProperty.h |

### Lights
| Binary Class | Gb 1.2 Source |
|-------------|---------------|
| NiLight | CoreLibs/NiMain/NiLight.h |
| NiDynamicEffect | CoreLibs/NiMain/NiDynamicEffect.h |
| NiAmbientLight | CoreLibs/NiMain/NiAmbientLight.h |
| NiDirectionalLight | CoreLibs/NiMain/NiDirectionalLight.h |
| NiPointLight | CoreLibs/NiMain/NiPointLight.h |
| NiSpotLight | CoreLibs/NiMain/NiSpotLight.h |
| NiTextureEffect | CoreLibs/NiMain/NiTextureEffect.h |

### Controllers / Animation (matched subset)
| Binary Class | Gb 1.2 Source |
|-------------|---------------|
| NiTimeController | CoreLibs/NiMain/NiTimeController.h |
| NiAlphaController | CoreLibs/NiAnimation/NiAlphaController.h |
| NiFlipController | CoreLibs/NiAnimation/NiFlipController.h |
| NiFloatController | CoreLibs/NiAnimation/NiFloatController.h |
| NiKeyframeManager | CoreLibs/NiAnimation/NiKeyframeManager.h [cross-source-2026-05-28: Gb 1.2 marks DEPRECATED, "use NiControllerManager instead" — moved here from prior NI 3.1-only Misc misclassification] |
| NiLightColorController | CoreLibs/NiAnimation/NiLightColorController.h |
| NiLookAtController | CoreLibs/NiAnimation/NiLookAtController.h |
| NiMaterialColorController | CoreLibs/NiAnimation/NiMaterialColorController.h |
| NiPathController | CoreLibs/NiAnimation/NiPathController.h |
| NiRollController | CoreLibs/NiAnimation/NiRollController.h |
| NiVisController | CoreLibs/NiAnimation/NiVisController.h |

### Animation Data (matched subset)
| Binary Class | Gb 1.2 Source |
|-------------|---------------|
| NiFloatData | CoreLibs/NiAnimation/NiFloatData.h |
| NiColorData | CoreLibs/NiAnimation/NiColorData.h |
| NiPosData | CoreLibs/NiAnimation/NiPosData.h |

### Extra Data
| Binary Class | Gb 1.2 Source |
|-------------|---------------|
| NiExtraData | CoreLibs/NiMain/NiExtraData.h |
| NiStringExtraData | CoreLibs/NiMain/NiStringExtraData.h |
| NiVertWeightsExtraData | CoreLibs/NiMain/NiVertWeightsExtraData.h |
| NiTextKeyExtraData | CoreLibs/NiAnimation/NiTextKeyExtraData.h |

### Physics / Collision
| Binary Class | Gb 1.2 Source |
|-------------|---------------|
| NiGravity | CoreLibs/NiOldParticle/NiGravity.h |
| NiParticleBomb | CoreLibs/NiOldParticle/NiParticleBomb.h |
| NiSphericalCollider | CoreLibs/NiOldParticle/NiSphericalCollider.h |
| NiPlanarCollider | CoreLibs/NiOldParticle/NiPlanarCollider.h |
| NiParticleSystemController | CoreLibs/NiOldParticle/NiParticleSystemController.h |

### Rendering
| Binary Class | Gb 1.2 Source |
|-------------|---------------|
| NiCamera | CoreLibs/NiMain/NiCamera.h |
| NiAccumulator | CoreLibs/NiMain/NiAccumulator.h |
| NiAlphaAccumulator | CoreLibs/NiMain/NiAlphaAccumulator.h |

### Math / Utility
| Binary Class | Gb 1.2 Source |
|-------------|---------------|
| NiPoint2 | CoreLibs/NiMain/NiPoint2.h |
| NiPoint3 | CoreLibs/NiMain/NiPoint3.h |
| NiColor | CoreLibs/NiMain/NiColor.h |
| NiColorA | CoreLibs/NiMain/NiColor.h |
| NiFrustum | CoreLibs/NiMain/NiFrustum.h |

### Template Containers (implementation in headers)
| Binary Class | Gb 1.2 Source |
|-------------|---------------|
| NiTArray | CoreLibs/NiMain/NiTArray.h |
| NiTList | CoreLibs/NiMain/NiTList.h |
| NiTMap | CoreLibs/NiMain/NiTMap.h |

---

## NI 3.1-Only Classes (≈44, subject to row-by-row audit) — No Gamebryo 1.2 Source

These classes exist in stbc.exe but were removed/renamed/reorganized before Gamebryo 1.2.
20 of 42 documented rows have serialization-level field definitions in nif.xml; the remaining
~22 are runtime-only classes (renderers, audio) that never appear in NIF files. The subcategory
sums below total 45 against a "42" headline; one class (NiKeyframeManager) has been moved to
matched-deprecated, bringing the running total to ~44 pending a full audit. See Open Questions.

> [!NOTE]
> ~30 of these rows are pattern-extrapolated from 5 of 5 absent-from-Gb1.2 spot-checks (NiBezierMesh, NiBezierTriangle4, NiBone, NiCollisionSwitch, NiSkinController) plus direct nif.xml line citations for ~20 rows. Carries `confidence: medium`. A full row-by-row audit is tracked as documentation debt.

### Bezier Patch System (11 classes) — Entire subsystem removed
| Class | nif.xml | Notes |
|-------|---------|-------|
| NiBezierMesh | **Yes** (line 5333) [cross-source-2026-05-28] | Full struct: triangle refs, vertex arrays, count fields |
| NiBezierPatch | No | Probably abstract base, never serialized |
| NiBezierRectangle | No | Not in file format |
| NiBezierRectangle2 | No | Not in file format |
| NiBezierRectangle3 | No | Not in file format |
| NiBezierTriangle | No | Only NiBezierTriangle4 documented |
| NiBezierTriangle2 | No | Not in file format |
| NiBezierTriangle3 | No | Not in file format |
| NiBezierTriangle4 | **Yes** (line 5319) [cross-source-2026-05-28] | Full struct: 6 uints, matrix33, vectors, shorts, bytes |
| NiBezierCylinder | No | Not in file format |
| NiBezierSkinController | No | Not in file format |

*Gb 1.2 moved to tessellation-based approach. These are genuine NI 3.x legacy.*

### Old Animation System (9 classes) — Architecture reorganized
*Note: section originally titled "8 classes" but lists 9 rows — the underlying drift that surfaced the 42 vs 45 total mismatch.*

| Class | nif.xml | Gb 1.2 Replacement |
|-------|---------|-------------------|
| NiKeyframeController | **Yes** (line 3651) [cross-source-2026-05-28] | NiTransformController. Data ref to NiKeyframeData |
| NiKeyframeData | **Yes** (line 4327) [cross-source-2026-05-28] | NiTransformData. **Full struct**: rotation keys (quaternion/XYZ), translations, scales |
| NiMorphController | **Yes** (line 3637) | NiGeomMorpherController. Refs NiMorphData |
| NiMorpherController | **Yes** (line 3641) | NiGeomMorpherController. Refs NiMorphData |
| NiMorphData | **Yes** (line 4375) | Partially kept. Full struct: num morphs, vertices, relative targets |
| NiSkinController | No | NiSkinningMeshModifier. Runtime-only |
| NiTriShapeSkinController | **Yes** (line 5085) | Removed. Full struct: bone count, vertex weights, bone refs (Ptr to NiBone) |
| NiVisData | **Yes** (line 5411) | NiBoolData. Keys array (num + key data) |
| NiAnimBlender | No | NiBlendInterpolator. Runtime-only |

### Old Texture Properties (5 classes) — Merged into NiTexturingProperty
| Class | nif.xml | Notes |
|-------|---------|-------|
| NiTextureProperty | **Yes** (line 5221) | Flags (ushort) + NiImage ref |
| NiTextureModeProperty | **Yes** (line 5204) | Flags (ushort) + PS2 L/K shorts (since 3.1) |
| NiMultiTextureProperty | **Yes** (line 5272) | Inherits NiTexturingProperty (no new fields) |
| NiTransparentProperty | **Yes** (line 3520) | 6 unknown bytes |
| NiCorrectionProperty | No | Removed entirely, never in file format |

### Old Rendering / DirectDraw (8 classes) — Abstraction changed
| Class | nif.xml | Notes |
|-------|---------|-------|
| NiRender | No | Runtime-only (renderer base class) |
| NiD3DRender | No | Runtime-only (D3D renderer) |
| NiImage | **Yes** (line 5212) | UseExternal, FileName, ImageData ref, unknown int, unknown float (since 3.1) |
| NiRawImageData | **Yes** (line 5435) | Width, height, image type, RGB/RGBA pixel data arrays |
| NiDDImage | No | Runtime-only (DirectDraw surface wrapper) |
| NiDDBufferImage | No | Runtime-only (DirectDraw buffer) |
| NiClusterAccumulator | No | Runtime-only (rendering accumulator) |
| NiForce | No | Moved/renamed in particle system |

### NI 3.1-Specific Nodes (3 classes) — Domain-specific
| Class | nif.xml | Notes |
|-------|---------|-------|
| NiBone | **Yes** (line 4392) [cross-source-2026-05-28] | Inherits NiNode, no new fields. Used as skeleton bone marker |
| NiCollisionSwitch | **Yes** (line 4396) [cross-source-2026-05-28] | Inherits NiNode, no new fields. Found in Munch's Oddysee |
| NiFltAnimationNode | No | MultiGen Flight format support, never in NIF files |

### Audio System (4 classes) — Renamed
| NI 3.1 Class | nif.xml | Gb 1.2 Class |
|-------------|---------|-------------|
| NiSoundSystem | No | NiAudioSystem (runtime-only) |
| NiSource | No | NiAudioSource (runtime-only) |
| NiListener | No | NiAudioListener (runtime-only) |
| NiProvider_Info | No | Removed (runtime-only) |

### Misc (4 classes — was 5; NiKeyframeManager moved to matched-deprecated)
| Class | nif.xml | Notes |
|-------|---------|-------|
| NiBinaryVoxelData | **Yes** (line 4059) | `until="V3_1"`. Full struct: shorts, 7 floats, byte grid, vectors, bytes, 5 ints |
| NiBinaryVoxelExtraData | **Yes** (line 4054) | `until="V3_1"`. Ref to NiBinaryVoxelData |
| NiCloneExtraData | No | Removed or renamed |
| NiSequenceStreamHelper | **Yes** (line 5057) | Inherits NiObjectNET, no new fields. Animation .kf root |

---

## NIF Format Version-Conditional Fields (V3.1-specific)

nif.xml uses `since` / `until` attributes to tag fields by NIF version. Key V3.1-specific
observations (fields that exist at V3.1 but were changed or removed later):

### NiObjectNET
| Field | Type | Version Range | Notes |
|-------|------|---------------|-------|
| Name | string | always | |
| Extra Data | Ref (NiExtraData) | 3.0 — 4.2.2.0 | **Single linked-list pointer** (not array) [cross-source-2026-05-28: nif.xml:3364] |
| Controller | Ref (NiTimeController) | 3.0+ | |

### NiAVObject
| Field | Type | Version Range | Notes |
|-------|------|---------------|-------|
| Flags | ushort | 3.0+ (BSVER<=26) | |
| Translation | Vector3 | always | |
| Rotation | Matrix33 | always | |
| Scale | float | always | |
| **Velocity** | **Vector3** | **until 4.2.2.0** | **Present in V3.1** — removed in Gb 1.2+ [cross-source-2026-05-28: nif.xml:3487] |
| Num Properties | uint | NI+BS<=FO3 | |
| Properties | Ref[] (NiProperty) | NI+BS<=FO3 | |
| **Has Bounding Volume** | **bool** | **3.0 — 4.2.2.0** | **Present in V3.1** [cross-source-2026-05-28: nif.xml:3492] |
| **Bounding Volume** | **BoundingVolume** | **3.0 — 4.2.2.0** | Conditional on Has Bounding Volume [cross-source-2026-05-28: nif.xml:3493] |
| Collision Object | Ref | 10.0.1.0+ | **Absent in V3.1** [cross-source-2026-05-28: nif.xml:3494] |

### NiTimeController
| Field | Type | Version Range | Notes |
|-------|------|---------------|-------|
| Next Controller | Ref (NiTimeController) | always | |
| Flags | TimeControllerFlags | always | |
| Frequency | float | always | |
| Phase | float | always | |
| Start Time | float | always | |
| Stop Time | float | always | |
| Target | Ptr (NiObjectNET) | 3.3.0.13+ | **Absent in V3.1** [cross-source-2026-05-28: nif.xml:3608] |
| **Unknown Integer** | **uint** | **until 3.1** | **V3.1-only** — replaced by Target ptr [cross-source-2026-05-28: nif.xml:3609] |

### NiDynamicEffect
| Field | Type | Version Range | Notes |
|-------|------|---------------|-------|
| Num Affected Nodes | uint | until 4.0.0.2 | Present in V3.1 |
| Affected Nodes | Ptr[] (NiNode) | until 3.3.0.13 | Present in V3.1 (Ptr, not Ref) |

### NiParticleSystemController (V3.1-specific fields)
| Field | Type | Version Range | Notes |
|-------|------|---------------|-------|
| **Old Speed** | **uint** | **until 3.1** | Replaced by float Speed in 3.3+ |
| **Old Emit Rate** | **uint** | **until 3.1** | Replaced by float Birth Rate in 3.3+ |
| **Particle Velocity** | **Vector3** | **until 3.1** | Per-particle data |
| **Particle Unknown Vector** | **Vector3** | **until 3.1** | |
| **Particle Lifetime** | **float** | **until 3.1** | Per-particle |
| **Particle Link** | **Ref (NiObject)** | **until 3.1** | Per-particle chain |
| **Particle Timestamp** | **uint** | **until 3.1** | |
| **Particle Unknown Short** | **ushort** | **until 3.1** | |
| **Particle Vertex Id** | **ushort** | **until 3.1** | Index |
| **Color Data** | **Ref (NiColorData)** | **until 3.1** | |
| **Unknown Float 1** | **float** | **until 3.1** | |
| **Unknown Floats 2** | **float[]** | **until 3.1** | Length = Particle Unknown Short |

### NiFlipController (V3.1-specific)
| Field | Type | Version Range | Notes |
|-------|------|---------------|-------|
| Images | Ref[] (NiImage) | until 3.1 | Replaced by NiSourceTexture refs in 3.3+ |

### TexDesc (NiTexturingProperty::Map)
| Field | Type | Version Range | Notes |
|-------|------|---------------|-------|
| Image | Ref (NiImage) | until 3.1 | Replaced by NiSourceTexture in 3.3+ |

---

## Additional Engine Sources Evaluated

### MWSE (Morrowind Script Extender) — Useful, But Not Universally Applicable

MWSE (`engine/mwse/`) contains **reverse-engineered C++ headers** for Morrowind's NI 4.0.0.2
engine. The MWSE struct sizes match NI 3.1 **only for NiObject and NiObjectNET** (which had
no V3.1-only fields removed in the 4.0 transition). For NiAVObject and below, MWSE sizes
diverge from NI 3.1 by +0x38 in V3.1-only fields.

| Class | MWSE Size | BC (NI 3.1) Size | Match? |
|-------|-----------|-------------------|--------|
| NiObject | 0x08 | 0x08 [v5-validated 2026-05-28] | **Yes** |
| NiObjectNET | 0x14 | 0x14 [v5-validated 2026-05-28] | **Yes** |
| NiAVObject | 0x90 | **0xC8** [v5-validated 2026-05-28] | **No — +0x38 in V3.1-only fields** |
| NiNode | 0xB0 | **0xE8** [v5-validated 2026-05-28] | **No — +0x38 inherited from NiAVObject** |

**MWSE field offsets confirmed for NiObjectNET only** (4 fields ending at byte 0x14):
- `name` (+0x08), `extraData` (+0x0C, single ptr), `controllers` (+0x10)

**For NiAVObject, MWSE offsets do NOT apply** — STBC writes worldBound at byte +0x54 (not
+0x1C, as MWSE claims) because V3.1-only fields are inserted between parentNode (+0x18) and
worldBound. See [netimmerse-vtables.md](netimmerse-vtables.md) for NI 3.1-specific NiAVObject
field layout (the canonical NI 3.1 reference for this).

**Vtable divergence**: MWSE NI 4.0.0.2 has destructor at vtable slot 0, getRTTI at slot 1.
BC's NI 3.1.1 has GetRTTI at slot 0, destructor at slot 10 [v5-validated 2026-05-28 via
netimmerse-vtables.md NiObject 0x00898b94]. Struct data layouts for NiObject/NiObjectNET
match but vtable ordering does not — use [netimmerse-vtables.md](netimmerse-vtables.md)
for BC vtable slots.

### niftools nif.xml — NIF File Format Specification

The NIF format spec (`engine/nif.xml`) from [niftools/nifxml](https://github.com/niftools/nifxml)
covers all NIF versions from 2.3 through 20.6. It explicitly lists BC:
- `V3_0` (num="3.0"): "Star Trek: Bridge Commander"
- `V3_1` (num="3.1"): "Dark Age of Camelot, Star Trek: Bridge Commander"

Both versions are marked `supported="false"` (NifSkope cannot open them), but the XML still
documents serialized fields with version-conditional `since`/`until` attributes.

**What nif.xml provides:**
- Serialization-level field definitions for ~20 of the ~42 documented NI 3.1-only classes
- Version-conditional field tags that precisely identify V3.1-specific fields (removed in later versions)
- Confirmation of NI 3.1 architectural differences (single ExtraData ptr, no CollisionObject, Velocity field on NiAVObject)
- NiParticleSystemController has 12 V3.1-only fields not present in any later version

**What nif.xml does NOT provide:**
- Runtime-only class layouts (renderers, audio, accumulators)
- C++ class member offsets (it documents serialization order, not memory layout)
- Virtual method tables or function signatures

### Gamebryo 2.6 SDK — Diverged Further from NI 3.1

Gb 2.6 (`engine/gamebyro-2.6-source/`) is a massive expansion (625 → 2,487 headers) that
moved **away** from NI 3.1, making it less useful than Gb 1.2 for stbc.exe annotation:

- Core NI classes preserved but marked **DEPRECATED** (NiGeometry, NiParticles, etc.)
- Modern replacements: NiMesh, NiRenderObject, NiPSParticleSystem
- Virtual method counts are higher than NI 3.1 (more evolution, not convergence)
- **NiBezierMesh, NiBezierTriangle, NiScreenPolygon: absent** — confirms these are NI 3.1-only
- NiRTTI factory system: identical pattern across all versions

**Key confirmation:** The ~44 "NI 3.1-only" classes were not re-added in Gb 2.6.
They are genuinely unique to NI 3.x.

---

## Practical Usage Guide

### For Ghidra Annotation
1. **Use MWSE headers ONLY for NiObject and NiObjectNET** (identical sizes). For NiAVObject and below, use [netimmerse-vtables.md](netimmerse-vtables.md) Object Sizes section (NI 3.1-specific, factory-verified). The MWSE field offsets do NOT translate beyond NiObjectNET due to V3.1-only fields.
2. **Use Gb 1.2 source for method implementations** — algorithm logic, virtual method names
3. **Do NOT trust Gb 1.2 struct offsets** — shifted by +8/+12 due to NiObjectNET/NiAVObject changes
4. **Use nif.xml for NI 3.1-only class fields** — ~20 of ~42 classes have serialization-level field defs
5. **Use BC vtable maps** ([netimmerse-vtables.md](netimmerse-vtables.md)) — MWSE/Gb 1.2 vtable slot ordering differs
6. **For the ~21 runtime-only classes, use Ghidra decompilation** — no external reference available

### Reference Priority (best to worst for struct annotation)
1. **Ghidra binary (NI 3.1 ground truth)** — exact offsets, exact sizes; use [netimmerse-vtables.md](netimmerse-vtables.md) for pre-validated NI 3.1 layouts
2. **MWSE headers** — exact for NiObject and NiObjectNET only; approximate-with-shift (+0x38) for NiAVObject; use Ghidra cross-check for derived classes
3. **nif.xml** — version-conditional field definitions (serialization order, not memory layout)
4. **Gb 1.2 source** — full implementation but shifted offsets (+8/+12 from NI 3.1 due to ExtraData array + CollisionObject)

### Key Source Files for Reference
```
engine/mwse/MWSE/NIObject.h      — NiObject struct + vtable (0x08, 11 vslots) — matches NI 3.1
engine/mwse/MWSE/NIObjectNET.h   — NiObjectNET struct (0x14) — matches NI 3.1
engine/mwse/MWSE/NIAVObject.h    — NiAVObject struct + vtable (0x90 in MWSE; NI 3.1 = 0xC8, offsets DIVERGE)
engine/mwse/MWSE/NINode.h        — NiNode struct + vtable (0xB0 in MWSE; NI 3.1 = 0xE8, offsets DIVERGE)
engine/nif.xml                    — NIF format spec (8563 lines, all versions)
engine/gamebyro-1.2-source/CoreLibs/NiMain/     — Core scene graph, properties
engine/gamebyro-1.2-source/CoreLibs/NiAnimation/ — Animation system
engine/gamebyro-1.2-source/CoreLibs/NiOldParticle/ — Legacy particles (best NI 3.1 match)
engine/gamebyro-1.2-source/SDK/Win32/Include/    — Combined headers (1,014 files)
```

### What Each Source Tells Us About BC's Engine
| Source | Struct Offsets | Method Names | Algorithms | Field Names | Version-Specific |
|--------|---------------|-------------|------------|-------------|-----------------|
| MWSE | Exact for NiObject/NiObjectNET; **diverges** for NiAVObject and below | Some | No | **Yes (with NI 3.1 shift)** | NI 4.0 |
| nif.xml | Serialization order | No | No | **Yes** | **Precise V3.1 tags** |
| Gb 1.2 | Shifted (+8/+12) | **Yes** | **Yes** | Yes | No (Gb 1.2 only) |
| Ghidra | **Exact** | Must RE | Must RE | Must RE | **Ground truth** |

---

## Open Questions and Documentation Debt

- **Subcategory rollup arithmetic.** Headline "42 NI 3.1-only" sums to 45 against the table rows (Old Animation header says "8 classes" but lists 9). After moving NiKeyframeManager to matched-deprecated, running total is ~44. A full row-by-row audit would settle the count.
- **"21 of 42 with nif.xml" recount.** Recount against current table contents gives 20 of 42 documented rows. Full row-by-row audit deferred.
- **NI 129 vs 117 delta.** [rtti-class-catalog.md](rtti-class-catalog.md) lists 129 NI classes; [nirtti-factory-catalog.md](nirtti-factory-catalog.md) has 117 registrations (115 Ni + 2 TG). What are the 12-14 NI classes not registered with the factory? Abstract bases? Stream-only types? Tracked in v5-validation-status.md §6 nirtti-factory-catalog.md entry.
- **NiBound / BoundingVolume struct size.** Observable from NiAVObject ctor's writes to indexes [0x15]-[0x18] via helper FUN_008136c0. If inline sphere (4 floats = 0x10) or box variant determines whether the +0x38 NI 3.1 vs MWSE 4.0 delta is fully accounted for by the three V3.1-only fields.
- **Audit of remaining "NI 3.1-only" rows for mis-categorization.** NiKeyframeManager was found in Gb 1.2 (deprecated). Other potential mis-categorizations not yet exhaustively checked; a full Glob-sweep of all ~44 rows would surface any remaining misclassifications.
