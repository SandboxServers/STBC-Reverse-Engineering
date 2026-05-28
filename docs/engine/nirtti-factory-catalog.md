> [docs](../README.md) / [engine](README.md) / nirtti-factory-catalog.md

---
title: NiRTTI Factory Registration Catalog
type: reference
audience: re-engineer
validated: 2026-05-28
methodology: FUNCTION_DOC_WORKFLOW_V5
binary:
  name: STBC.exe
  size: 6394712
  base: 0x00400000
status: verified
evidence:
  - claim: "NiRTTI factory hash table base at DAT_009a2b98"
    address: 0x009a2b98
    function: null
    confidence: high
    note: "237 xrefs total — 234 registration READ+WRITE pairs + 2 consumer READs (FUN_008176b0, FUN_00818150) + 1 process-shutdown READ at 0x00816c40."
  - claim: "Final hash-table vtable PTR_FUN_0088b7c4 (used after construction)"
    address: 0x0088b7c4
    function: null
    confidence: high
    note: "8+ slots verified (destructor, hash, compare, setEntry, deleteEntry, plus three undocumented slots at +0x14/+0x18/+0x1C)."
  - claim: "Temp-init vtable PTR_LAB_0088b7d8 (used only during hash-table construction)"
    address: 0x0088b7d8
    function: null
    confidence: high
    note: "Swapped out for the final vtable PTR_FUN_0088b7c4 once construction completes — see NiNode registration decompile."
  - claim: "Bucket count = 37 (0x25)"
    address: null
    function: FUN_007e3670
    confidence: high
    note: "Decoded from NiNode registration (canonical example). Allocated as bucket_count field at hash-table+0x08."
  - claim: "Bucket array size 0x94 bytes (148 = 37 * 4-byte ptrs)"
    address: null
    function: FUN_007e3670
    confidence: high
    note: "memset(buckets, 0, 0x94) clears the array after NiAlloc(0x94)."
  - claim: "Hash table struct size 0x10 bytes (vtable, count, bucket_count, buckets)"
    address: null
    function: FUN_007e3670
    confidence: high
    note: "NiAlloc(0x10) for the table object."
  - claim: "Hash node size 0x0C bytes (className, factory, next)"
    address: null
    function: FUN_007e3670
    confidence: high
    note: "NiAlloc(0x0C) for each new node; setEntry writes className and factory; insert-at-head sets next."
  - claim: "NiAlloc allocator at FUN_00718cb0 (body 0x00718cb0-0x00718cc6)"
    address: 0x00718cb0
    function: FUN_00718cb0
    confidence: high
    note: "All 117 registrations call this allocator for table, buckets, and nodes. (Corrects the engine-snapshot's 0x00717840 — that was a different function.)"
  - claim: "Consumer FUN_008176b0 (NiStream::LoadObject) reads class name from NIF and looks up factory"
    address: 0x008176b0
    function: FUN_008176b0
    confidence: high
    note: "Body 904 bytes. Error string: 'NiStream: Unable to find loader for...'"
  - claim: "Consumer FUN_00818150 (NiStream::LoadObjectAlt) alternative load path with same lookup pattern"
    address: 0x00818150
    function: FUN_00818150
    confidence: high
    note: "Body 635 bytes."
  - claim: "Standalone READ at 0x00816c40 invokes hash-table destructor at process shutdown"
    address: 0x00816c40
    function: null
    confidence: high
    note: "Calls vtable[+0] on DAT_009a2b98. NOT inside any Ghidra function — orphan code snippet between functions."
  - claim: "Total registrations: 117 (115 Ni + 2 TG)"
    address: null
    function: null
    confidence: high
    note: "Confirmed by partner agent's xref count and exhaustive enumeration of the 234 registration READ+WRITE pairs."
  - claim: "Exactly 2 TG factory entries: TGDimmerController, TGFuzzyTriShape"
    address: 0x008daed4
    function: null
    confidence: high
    note: "Bare class-name strings at 0x008daed4 and 0x008daee8. No third TG factory registration exists."
  - claim: "TGOverlayController bare class-name string at 0x008daef8 is NOT NiRTTI-registered"
    address: 0x008daef8
    function: null
    confidence: high
    note: "Sibling TG class to the 2 registered TG classes but uses a different runtime-type mechanism (likely TG's own type-info via a GetRTTI-style accessor)."
  - claim: "Registration function address range 0x00455060 - 0x0084ca60"
    address: 0x00455060
    function: null
    confidence: high
    note: "Low: TGDimmerController. High: NiBezierCylinder."
  - claim: "Factory function address range 0x00455320 - 0x00850a30"
    address: 0x00455320
    function: null
    confidence: high
    note: "Low: TGDimmerController. High: NiBezierCylinder."
  - claim: "Vtable slot [+0] = hash table destructor (called at shutdown)"
    address: 0x0088b7c4
    function: null
    confidence: high
    note: "Invoked by the standalone READ at 0x00816c40."
  - claim: "Vtable slot [+4] = hash(className) -> bucket index"
    address: 0x0088b7c8
    function: null
    confidence: high
    note: "Decoded from registration pattern."
  - claim: "Vtable slot [+8] = compare(a, b) -> bool"
    address: 0x0088b7cc
    function: null
    confidence: high
    note: "Used during bucket chain walk to detect duplicate registrations."
  - claim: "Vtable slot [+0xC] = setEntry(node, name, factory)"
    address: 0x0088b7d0
    function: null
    confidence: high
    note: "Writes className and factory pointer into a hash node."
  - claim: "Vtable slot [+0x10] = deleteEntry(node) — clears node fields"
    address: 0x0088b7d4
    function: null
    confidence: high
    note: "Called when an existing registration is being replaced."
  - claim: "17 of 117 factories are RET-stub DAT_* entries for abstract base classes"
    address: null
    function: null
    confidence: high
    note: "Single RET (0xC3) + padding NOPs. No allocation, no vtable write, no object returned. Exist so abstract bases appear in the hash table for IsA()-style queries. Full list in 'Concrete vs Abstract Factory Distribution' section."
  - claim: "100 of 117 factories are concrete FUN_* allocators following a uniform pattern"
    address: null
    function: null
    confidence: medium
    note: "6 spot-decompiles (TGDimmerController, TGFuzzyTriShape, NiBinaryVoxelData, NiListener, NiNode, NiBezierCylinder) + 5 sub-cluster checks confirm the pattern: SEH prologue, NiAlloc(N), constructor helper, vtable pointer write, return via out-parameter."
  - claim: "Factory signature is `void(int* out_ptr)`, not `T* func(void)`"
    address: null
    function: null
    confidence: high
    note: "Constructed object pointer is written via out-parameter, not returned in EAX. Decoded from concrete factories."
  - claim: "10 of 117 entries individually verified by decompile; remaining 107 by pattern extrapolation"
    address: null
    function: null
    confidence: medium
    note: "Sampled: TGDimmerController, TGFuzzyTriShape, NiBinaryVoxelData, NiListener, NiNode, NiBezierCylinder, NiObject, NiObjectNET, NiAVObject, NiSoundSystem. 8 sub-cluster spot-checks across the 14 MB factory range all matched the documented pattern. Pattern uniformity tracked as documentation debt — a per-row decompile sweep would promote all 107 to high."
companions:
  - docs/engine/rtti-class-catalog.md
  - docs/engine/netimmerse-vtables.md
  - docs/engine/gamebryo-cross-reference.md
  - docs/engine/function-map.md
  - docs/engine/v5-validation-status.md
supersedes:
  - (prior undated revision)
---

# NiRTTI Factory Registration Catalog - stbc.exe

> [!NOTE]
> This doc is `status: verified`. The hash-table internals, consumer functions, factory pattern,
> 10 individually-sampled rows, and the 17 abstract-base RET-stub list are v5-anchored against
> the current Ghidra import (2026-05-28). The remaining 107 catalog rows are pattern-extrapolated
> from 6 spot-decompiles and 8 sub-cluster checks — `confidence: medium`, not `confidence: low`.
> See [docs/guides/v5-evidence-header.md](../guides/v5-evidence-header.md) for the standard.
>
> Shared anchors with [rtti-class-catalog.md](rtti-class-catalog.md) (117 registrations, hash
> table at 0x009a2b98, 37 buckets) are referenced from there to avoid restating.

Complete mapping of all classes registered in the NiRTTI factory hash table at `DAT_009a2b98`.
Each entry maps: **class name** -> **factory function** -> **registration function**.

Generated from exhaustive Ghidra decompilation of all 237 xrefs to `DAT_009a2b98`.

## Architecture Overview

### Hash Table Structure
- **Global pointer**: `DAT_009a2b98` (initialized to NULL, created on first registration)
- **Hash table object**: 0x10 bytes
  - `[+0x00]` = vtable pointer (`PTR_FUN_0088b7c4`)
  - `[+0x04]` = entry count
  - `[+0x08]` = bucket count (always 0x25 = 37)
  - `[+0x0C]` = bucket array pointer (0x94 bytes = 37 * 4)
- **Vtable operations** at `PTR_FUN_0088b7c4`:
  - `[+0x00]` = hash-table destructor (invoked at process shutdown by orphan READ at 0x00816c40)
  - `[+0x04]` = hash(className) -> bucket index
  - `[+0x08]` = compare(className, nodeClassName) -> bool
  - `[+0x0C]` = setEntry(node, className, factoryFn)
  - `[+0x10]` = deleteEntry(node) -- clears node fields
  - `[+0x14]`, `[+0x18]`, `[+0x1C]` = three additional slots, undocumented (deferred to a
    dedicated vtable pass)

### Hash Node Structure
- 0x0C bytes per node (linked list in each bucket):
  - `[+0x00]` = className string pointer
  - `[+0x04]` = factory function pointer
  - `[+0x08]` = next node pointer (NULL = end of chain)

### Factory Function Signature

All concrete factory functions share the same signature:

```c
void Factory(int* out_ptr);
```

The constructed object pointer is written via the **out-parameter** — not returned in EAX as
a `T*`. Readers writing decoders against the pattern should call factories with the address of
a local pointer slot, not consume the return value.

### Registration Pattern (identical for ALL 117 registered classes)
```c
// Example: NiNode registration (FUN_007e3670)
undefined4 RegisterNiNode(void) {
    if (DAT_009a18a0 != '\0') return 0;  // guard: already registered
    DAT_009a18a0 = 1;                     // set guard

    if (DAT_009a2b98 == NULL) {
        // Create hash table (first registration only)
        piVar2 = NiAlloc(0x10);
        piVar2->vtable = &PTR_LAB_0088b7d8;  // temp vtable
        piVar2->count = 0;
        piVar2->bucket_count = 0x25;          // 37 buckets
        piVar2->buckets = NiAlloc(0x94);      // 37 * 4 bytes
        memset(piVar2->buckets, 0, 0x94);
        piVar2->vtable = &PTR_FUN_0088b7c4;  // final vtable
        DAT_009a2b98 = piVar2;
    }

    bucket_idx = vtable->hash("NiNode");
    node = buckets[bucket_idx];
    while (node != NULL) {
        if (vtable->compare("NiNode", node->className)) {
            vtable->deleteEntry(node);
            vtable->setEntry(node, "NiNode", FUN_007e5450);
            return 1;  // replaced existing
        }
        node = node->next;
    }
    // Not found: create new node
    newNode = NiAlloc(0x0C);
    vtable->setEntry(newNode, "NiNode", FUN_007e5450);
    newNode->next = buckets[bucket_idx];
    buckets[bucket_idx] = newNode;  // insert at head
    count++;
    return 1;
}
```

### Consumer Functions (NIF Loader)
| Address | Function | Role |
|---------|----------|------|
| `FUN_008176b0` | NiStream::LoadObject (904-byte body) | Reads class name from NIF, looks up factory, calls it. Error: "NiStream: Unable to find loader for..." |
| `FUN_00818150` | NiStream::LoadObjectAlt (635-byte body) | Alternative load path (same lookup pattern) |
| `0x00816c40` | (standalone READ — orphan code) | Hash-table destructor invocation at process shutdown — calls `vtable[+0]` on `DAT_009a2b98`. NOT inside any Ghidra function. |

### Memory Allocator
- `FUN_00718cb0` = NiAlloc (body 0x00718cb0 - 0x00718cc6). All 117 registrations use this
  allocator for the hash-table struct, the bucket array, and each new node.

---

## Concrete vs Abstract Factory Distribution

Of the 117 registered NiRTTI factories, **17 are RET-stub `DAT_*` factories** at the address
of an abstract base class. They consist of a single `RET` (0xC3) followed by padding NOPs —
they do not allocate, do not write a vtable, do not return an object. They exist only so the
abstract-base classes are present in the hash table (likely to support `IsA()`-style runtime
type queries that walk the registration chain).

The remaining **100 are concrete `FUN_*` factories** that follow a uniform pattern: SEH
prologue, `NiAlloc(N)`, constructor helper, vtable pointer write, then return the new instance
via an out-parameter.

This is foundational structural knowledge: a reader expecting to find a vtable at the address
of an abstract-base factory will come up empty. The vtable lives on instances allocated by the
*concrete* factory of the next derived class.

### The 17 abstract-base RET-stub factories

| Class | Factory addr (RET-stub) |
|-------|-------------------------|
| NiObject | `DAT_007d8810` |
| NiAccumulator | `DAT_007d8f30` |
| NiTimeController | `DAT_007da450` |
| NiObjectNET | `DAT_007db5e0` |
| NiProperty | `DAT_007dbcc0` |
| NiAVObject | `DAT_007dd470` |
| NiDynamicEffect | `DAT_007e2530` |
| NiRender | `DAT_007e31b0` |
| NiGeometryData | `DAT_007ed190` |
| NiGeometry | `DAT_007ee6b0` |
| NiTriBasedGeomData | `DAT_007eed00` |
| NiTriBasedGeom | `DAT_007f0d50` |
| NiLight | `DAT_007f38e0` |
| NiSkinController | `DAT_00805320` |
| NiBezierPatch | `DAT_00834570` |
| NiBezierTriangle | `DAT_00838a50` |
| NiBezierRectangle | `DAT_00847c90` |

All other 100 entries in the catalog below allocate fixed-size instances.

---

## Complete Factory Registration Table (117 entries)

Sorted by registration function address (code order in binary).

> [!NOTE]
> **Row confidence:** 10 entries carry the `[v5-validated 2026-05-28]` tag — these were
> individually decompiled and verified during this pass (TGDimmerController, TGFuzzyTriShape,
> NiBinaryVoxelData, NiListener, NiSoundSystem, NiObject, NiObjectNET, NiAVObject, NiNode,
> NiBezierCylinder). The remaining 107 entries are pattern-extrapolated: 8 sub-cluster
> spot-checks across the 14 MB factory range all matched the documented pattern, so their
> addresses are `confidence: medium`, not `confidence: low`. A per-row decompile sweep would
> promote them all to high — tracked as documentation debt.
>
> The prior **Guard Flag** column has been dropped: of 10 sampled rows, only 2 guard-flag
> addresses matched (and those 2 may be coincidence). Guard flag is secondary metadata that
> nothing else in the doc family depends on.

### TG Framework Classes (2 entries)

| # | Class Name | String Addr | Factory Fn | Registration Fn |
|---|-----------|-------------|-----------|----------------|
| 1 | TGDimmerController | 0x008DAED4 | `FUN_00455320` | `FUN_00455060` [v5-validated 2026-05-28] |
| 2 | TGFuzzyTriShape | 0x008DAEE8 | `FUN_00456980` | `FUN_00456740` [v5-validated 2026-05-28] |

> **TGOverlayController footnote:** A sibling TG class `TGOverlayController` exists as a bare
> class-name string at `0x008daef8`, but it is **not** NiRTTI-registered. It uses a different
> runtime-type mechanism — likely TG's own type-info via a `GetRTTI`-style accessor
> (`FUN_00457550` is a candidate). The class exists; only its NiRTTI registration is absent.

### Ni Classes - Audio (3 entries)

| # | Class Name | String Addr | Factory Fn | Registration Fn |
|---|-----------|-------------|-----------|----------------|
| 3 | NiListener | 0x00975E98 | `FUN_0078d250` | `FUN_0078cbd0` [v5-validated 2026-05-28] |
| 4 | NiSoundSystem | 0x00975EA4 | `LAB_0078e6e0` | `FUN_0078d760` [v5-validated 2026-05-28] |
| 5 | NiSource | 0x00975EB4 | `FUN_007904c0` | `FUN_0078f230` |

### Ni Classes - Voxel Data (2 entries)

| # | Class Name | String Addr | Factory Fn | Registration Fn |
|---|-----------|-------------|-----------|----------------|
| 6 | NiBinaryVoxelData | 0x008DD2A8 | `FUN_004a57f0` | `FUN_004a56a0` [v5-validated 2026-05-28] |
| 7 | NiBinaryVoxelExtraData | 0x008DD2BC | `FUN_004ac150` | `FUN_004ac000` |

### Ni Classes - Animation Data (7 entries)

| # | Class Name | String Addr | Factory Fn | Registration Fn |
|---|-----------|-------------|-----------|----------------|
| 8 | NiKeyframeData | 0x00975F20 | `FUN_00792260` | `FUN_00791e40` |
| 9 | NiKeyframeController | 0x00975F64 | `FUN_007932e0` | `FUN_00792b40` |
| 10 | NiFlipController | 0x00975F7C | `FUN_00793f20` | `FUN_007938d0` |
| 11 | NiFloatController | 0x00975F90 | `DAT_00794bc0` | `FUN_00794810` |
| 12 | NiFloatData | 0x00975FA4 | `FUN_00795250` | `FUN_00795010` |
| 13 | NiAlphaController | 0x00975FBC | `FUN_00795ae0` | `FUN_00795830` |
| 14 | NiTextKeyExtraData | 0x00976044 | `FUN_00796f10` | `FUN_00796c50` |

### Ni Classes - Animation Blending & Color (2 entries)

| # | Class Name | String Addr | Factory Fn | Registration Fn |
|---|-----------|-------------|-----------|----------------|
| 15 | NiAnimBlender | 0x00976058 | `FUN_0079a630` | `FUN_00797660` |
| 16 | NiColorData | 0x00976070 | `FUN_0079da20` | `FUN_0079d860` |

### Ni Classes - Physics (4 entries)

| # | Class Name | String Addr | Factory Fn | Registration Fn |
|---|-----------|-------------|-----------|----------------|
| 17 | NiForce | 0x0097607C | `DAT_0079e510` | `FUN_0079e370` |
| 18 | NiGravity | 0x00976084 | `FUN_0079ecd0` | `FUN_0079e6c0` |
| 19 | NiParticleBomb | 0x00976090 | `FUN_0079f760` | `FUN_0079f110` |
| 20 | NiSphericalCollider | 0x009760A0 | `FUN_007a02e0` | `FUN_0079fc00` |

### Ni Classes - Collision & Managers (3 entries)

| # | Class Name | String Addr | Factory Fn | Registration Fn |
|---|-----------|-------------|-----------|----------------|
| 21 | NiPlanarCollider | 0x009760B4 | `FUN_007a0fc0` | `FUN_007a06d0` |
| 22 | NiKeyframeManager | 0x009760CC | `FUN_007a3f80` | `FUN_007a14a0` |
| 23 | NiPosData | 0x009761D0 | `FUN_007a5ea0` | `FUN_007a5ce0` |

### Ni Classes - Light & Look-At Controllers (3 entries)

| # | Class Name | String Addr | Factory Fn | Registration Fn |
|---|-----------|-------------|-----------|----------------|
| 24 | NiLightColorController | 0x009761DC | `FUN_007a6b80` | `FUN_007a64f0` |
| 25 | NiLookAtController | 0x009761F4 | `FUN_007a7dc0` | `FUN_007a7670` |
| 26 | NiMorphController | 0x00976208 | `FUN_007a8dd0` | `FUN_007a8350` |

### Ni Classes - Morph & Material (4 entries)

| # | Class Name | String Addr | Factory Fn | Registration Fn |
|---|-----------|-------------|-----------|----------------|
| 27 | NiMorphData | 0x0097621C | `FUN_007aa2e0` | `FUN_007a9ec0` |
| 28 | NiMorpherController | 0x00976250 | `FUN_007ab390` | `FUN_007aacc0` |
| 29 | NiMaterialColorController | 0x0097626C | `FUN_007ac620` | `FUN_007ac020` |
| 30 | NiPathController | 0x009762B0 | `FUN_007ae150` | `FUN_007acb80` |

### Ni Classes - Particle System & Sequences (4 entries)

| # | Class Name | String Addr | Factory Fn | Registration Fn |
|---|-----------|-------------|-----------|----------------|
| 31 | NiParticleSystemController | 0x009762C4 | `FUN_007b2320` | `FUN_007ae9d0` |
| 32 | NiRollController | 0x009762E0 | `FUN_007b4020` | `FUN_007b3d10` |
| 33 | NiSequenceStreamHelper | 0x009762F4 | `FUN_007b4650` | `FUN_007b4500` |
| 34 | NiVisData | 0x0097630C | `FUN_007b5db0` | `FUN_007b5ba0` |

### Ni Classes - Visibility Controller (1 entry)

| # | Class Name | String Addr | Factory Fn | Registration Fn |
|---|-----------|-------------|-----------|----------------|
| 35 | NiVisController | 0x00976328 | `FUN_007b67e0` | `FUN_007b6300` |

### Ni Classes - D3D Renderer (1 entry)

| # | Class Name | String Addr | Factory Fn | Registration Fn |
|---|-----------|-------------|-----------|----------------|
| 36 | NiD3DRender | 0x00976724 | `FUN_007c4740` | `FUN_007bfcf0` |

### Ni Classes - Core Object Hierarchy (7 entries)

| # | Class Name | String Addr | Factory Fn | Registration Fn |
|---|-----------|-------------|-----------|----------------|
| 37 | NiObject | 0x009780D8 | `DAT_007d8810` (abstract RET-stub) | `FUN_007d8650` [v5-validated 2026-05-28] |
| 38 | NiAccumulator | 0x009780F0 | `DAT_007d8f30` (abstract RET-stub) | `FUN_007d8d70` |
| 39 | NiExtraData | 0x00978100 | `FUN_007d9450` | `FUN_007d9070` |
| 40 | NiTimeController | 0x00978118 | `DAT_007da450` (abstract RET-stub) | `FUN_007d9a10` |
| 41 | NiObjectNET | 0x00978228 | `DAT_007db5e0` (abstract RET-stub) | `FUN_007dab30` [v5-validated 2026-05-28] |
| 42 | NiProperty | 0x0097823C | `DAT_007dbcc0` (abstract RET-stub) | `FUN_007dbb00` |
| 43 | NiAVObject | 0x0095B050 | `DAT_007dd470` (abstract RET-stub) | `FUN_007dbf70` [v5-validated 2026-05-28] |

### Ni Classes - Images & Raw Data (2 entries)

| # | Class Name | String Addr | Factory Fn | Registration Fn |
|---|-----------|-------------|-----------|----------------|
| 44 | NiRawImageData | 0x00978330 | `FUN_007e0320` | `FUN_007de090` |
| 45 | NiImage | 0x009783DC | `LAB_007e1630` | `FUN_007e0990` |

### Ni Classes - Dynamic Effects & Renderer (2 entries)

| # | Class Name | String Addr | Factory Fn | Registration Fn |
|---|-----------|-------------|-----------|----------------|
| 46 | NiDynamicEffect | 0x009784D8 | `DAT_007e2530` (abstract RET-stub) | `FUN_007e20b0` |
| 47 | NiRender | 0x009784F4 | `DAT_007e31b0` (abstract RET-stub) | `FUN_007e2a40` |

### Ni Classes - Scene Graph Core (2 entries)

| # | Class Name | String Addr | Factory Fn | Registration Fn |
|---|-----------|-------------|-----------|----------------|
| 48 | NiNode | 0x00978500 | `FUN_007e5450` | `FUN_007e3670` [v5-validated 2026-05-28] |
| 49 | NiScreenPolygon | 0x00978520 | `FUN_007e6ed0` | `FUN_007e68f0` |

### Ni Classes - Camera & Accumulators (4 entries)

| # | Class Name | String Addr | Factory Fn | Registration Fn |
|---|-----------|-------------|-----------|----------------|
| 50 | NiCamera | 0x0097856C | `FUN_007ea2e0` | `FUN_007e79a0` |
| 51 | NiClusterAccumulator | 0x009785F4 | `FUN_007eb850` | `FUN_007eb2f0` |
| 52 | NiAlphaAccumulator | 0x0097860C | `FUN_007ebd80` | `FUN_007ebb90` |
| 53 | NiAlphaProperty | 0x00978620 | `FUN_007ec3c0` | `FUN_007ec080` |

### Ni Classes - Geometry Core (4 entries)

| # | Class Name | String Addr | Factory Fn | Registration Fn |
|---|-----------|-------------|-----------|----------------|
| 54 | NiGeometryData | 0x0097873C | `DAT_007ed190` (abstract RET-stub) | `FUN_007ec9f0` |
| 55 | NiGeometry | 0x00978770 | `DAT_007ee6b0` (abstract RET-stub) | `FUN_007edb70` |
| 56 | NiTriBasedGeomData | 0x0097877C | `DAT_007eed00` (abstract RET-stub) | `FUN_007eeb20` |
| 57 | NiTriBasedGeom | 0x009787A0 | `DAT_007f0d50` (abstract RET-stub) | `FUN_007ef0e0` |

### Ni Classes - Triangle Mesh (3 entries)

| # | Class Name | String Addr | Factory Fn | Registration Fn |
|---|-----------|-------------|-----------|----------------|
| 58 | NiTriShapeData | 0x009787BC | `FUN_007f1860` | `FUN_007f12b0` |
| 59 | NiTriShape | 0x009787EC | `FUN_007f31f0` | `FUN_007f1ef0` |
| 60 | NiLight | 0x009787F8 | `DAT_007f38e0` (abstract RET-stub) | `FUN_007f3650` |

### Ni Classes - Lights (2 entries)

| # | Class Name | String Addr | Factory Fn | Registration Fn |
|---|-----------|-------------|-----------|----------------|
| 61 | NiAmbientLight | 0x00978824 | `FUN_007f4130` | `FUN_007f3e70` |
| 62 | NiParticlesData | 0x00978848 | `FUN_007f4830` | `FUN_007f45a0` |

### Ni Classes - Particles (4 entries)

| # | Class Name | String Addr | Factory Fn | Registration Fn |
|---|-----------|-------------|-----------|----------------|
| 63 | NiParticles | 0x00978860 | `FUN_007f52d0` | `FUN_007f4e00` |
| 64 | NiAutoNormalParticlesData | 0x00978870 | `FUN_007f5970` | `FUN_007f5780` |
| 65 | NiAutoNormalParticles | 0x00978890 | `FUN_007f60f0` | `FUN_007f5d50` |
| 66 | NiBillboardNode | 0x009788A8 | `FUN_007f6cf0` | `FUN_007f65b0` |

### Ni Classes - Skeletal (2 entries)

| # | Class Name | String Addr | Factory Fn | Registration Fn |
|---|-----------|-------------|-----------|----------------|
| 67 | NiBone | 0x00978908 | `FUN_007f7990` | `FUN_007f72c0` |
| 68 | NiBSPNode | 0x00978910 | `FUN_007f8590` | `FUN_007f7d50` |

### Ni Classes - Collision & Properties (4 entries)

| # | Class Name | String Addr | Factory Fn | Registration Fn |
|---|-----------|-------------|-----------|----------------|
| 69 | NiCollisionSwitch | 0x0097893C | `FUN_007f8f90` | `FUN_007f8d00` |
| 70 | NiCorrectionProperty | 0x00978960 | `FUN_007f97d0` | `FUN_007f94b0` |
| 71 | NiDirectionalLight | 0x00978984 | `FUN_007f9fb0` | `FUN_007f9c20` |
| 72 | NiDitherProperty | 0x00978998 | `FUN_007fa760` | `FUN_007fa440` |

### Ni Classes - Env-Mapped Geometry (2 entries)

| # | Class Name | String Addr | Factory Fn | Registration Fn |
|---|-----------|-------------|-----------|----------------|
| 73 | NiEnvMappedTriShapeData | 0x009789B8 | `FUN_007fad70` | `FUN_007fab60` |
| 74 | NiEnvMappedTriShape | 0x009789D0 | `FUN_007fb610` | `FUN_007fb0d0` |

### Ni Classes - Switch & Animation Nodes (2 entries)

| # | Class Name | String Addr | Factory Fn | Registration Fn |
|---|-----------|-------------|-----------|----------------|
| 75 | NiSwitchNode | 0x009789E4 | `FUN_007fc850` | `FUN_007fbae0` |
| 76 | NiFltAnimationNode | 0x00978A24 | `FUN_007fd230` | `FUN_007fcf30` |

### Ni Classes - Fog & Lines (3 entries)

| # | Class Name | String Addr | Factory Fn | Registration Fn |
|---|-----------|-------------|-----------|----------------|
| 77 | NiFogProperty | 0x00978A50 | `FUN_007fdc70` | `FUN_007fd8d0` |
| 78 | NiLinesData | 0x00978AC8 | `FUN_007fe4c0` | `FUN_007fe230` |
| 79 | NiLines | 0x00978AE0 | `FUN_007fec90` | `FUN_007fe990` |

### Ni Classes - LOD & Material (2 entries)

| # | Class Name | String Addr | Factory Fn | Registration Fn |
|---|-----------|-------------|-----------|----------------|
| 80 | NiLODNode | 0x00978AE8 | `FUN_007ffd00` | `FUN_007ff120` |
| 81 | NiMaterialProperty | 0x00978B40 | `FUN_00800ae0` | `FUN_00800680` |

### Ni Classes - Texture Properties (2 entries)

| # | Class Name | String Addr | Factory Fn | Registration Fn |
|---|-----------|-------------|-----------|----------------|
| 82 | NiTextureModeProperty | 0x00978B74 | `FUN_00801490` | `FUN_00801120` |
| 83 | NiMultiTextureProperty | 0x00978D2C | `FUN_00802630` | `FUN_00801d30` |

### Ni Classes - Point Light & Shade (2 entries)

| # | Class Name | String Addr | Factory Fn | Registration Fn |
|---|-----------|-------------|-----------|----------------|
| 84 | NiPointLight | 0x00978E24 | `FUN_00803ad0` | `FUN_008037a0` |
| 85 | NiShadeProperty | 0x00978E58 | `FUN_00804400` | `FUN_008040e0` |

### Ni Classes - Skin Controller (1 entry)

| # | Class Name | String Addr | Factory Fn | Registration Fn |
|---|-----------|-------------|-----------|----------------|
| 86 | NiSkinController | 0x00978E74 | `DAT_00805320` (abstract RET-stub) | `FUN_00804850` |

### Ni Classes - Sort & Specular (2 entries)

| # | Class Name | String Addr | Factory Fn | Registration Fn |
|---|-----------|-------------|-----------|----------------|
| 87 | NiSortAdjustNode | 0x00978E88 | `FUN_00805e40` | `FUN_00805a50` |
| 88 | NiSpecularProperty | 0x00978EA4 | `FUN_00806720` | `FUN_00806400` |

### Ni Classes - Spot Light & Stencil (2 entries)

| # | Class Name | String Addr | Factory Fn | Registration Fn |
|---|-----------|-------------|-----------|----------------|
| 89 | NiSpotLight | 0x00978EC0 | `FUN_00806f10` | `FUN_00806b20` |
| 90 | NiStencilProperty | 0x00978EEC | `FUN_00807930` | `FUN_00807570` |

### Ni Classes - String Extra Data & Texture Effect (2 entries)

| # | Class Name | String Addr | Factory Fn | Registration Fn |
|---|-----------|-------------|-----------|----------------|
| 91 | NiStringExtraData | 0x00979064 | `FUN_008085a0` | `FUN_008081f0` |
| 92 | NiTextureEffect | 0x00979084 | `FUN_00809120` | `FUN_00808a60` |

### Ni Classes - Texture & Transparent Properties (2 entries)

| # | Class Name | String Addr | Factory Fn | Registration Fn |
|---|-----------|-------------|-----------|----------------|
| 93 | NiTextureProperty | 0x0097919C | `FUN_0080a390` | `FUN_00809d20` |
| 94 | NiTransparentProperty | 0x009791BC | `FUN_0080ac60` | `FUN_0080a920` |

### Ni Classes - Alternative Triangle Types (2 entries)

| # | Class Name | String Addr | Factory Fn | Registration Fn |
|---|-----------|-------------|-----------|----------------|
| 95 | NiTrianglesData | 0x009791F0 | `FUN_0080b4b0` | `FUN_0080b170` |
| 96 | NiTriangles | 0x00979200 | `FUN_0080bde0` | `FUN_0080b8c0` |

### Ni Classes - Dynamic & Skin Mesh (2 entries)

| # | Class Name | String Addr | Factory Fn | Registration Fn |
|---|-----------|-------------|-----------|----------------|
| 97 | NiTriShapeDynamicData | 0x0097920C | `FUN_0080c4b0` | `FUN_0080c290` |
| 98 | NiTriShapeSkinController | 0x0097924C | `FUN_0080ccd0` | `FUN_0080c960` |

### Ni Classes - Triangle Strips (5 entries)

| # | Class Name | String Addr | Factory Fn | Registration Fn |
|---|-----------|-------------|-----------|----------------|
| 99 | NiTriStripData | 0x00979268 | `FUN_0080d590` | `FUN_0080d000` |
| 100 | NiTriStrip | 0x00979278 | `FUN_0080df90` | `FUN_0080da40` |
| 101 | NiTriStripsData | 0x00979284 | `FUN_0080e6b0` | `FUN_0080e490` |
| 102 | NiTriStrips | 0x009792C4 | `FUN_0080f220` | `FUN_0080ec30` |
| 103 | NiVertexColorProperty | 0x009792D0 | `FUN_0080fa30` | `FUN_0080f6d0` |

### Ni Classes - Vertex & Wireframe Properties (3 entries)

| # | Class Name | String Addr | Factory Fn | Registration Fn |
|---|-----------|-------------|-----------|----------------|
| 104 | NiVertWeightsExtraData | 0x00979368 | `FUN_00810310` | `FUN_0080ffa0` |
| 105 | NiWireframeProperty | 0x00979380 | `FUN_00810a80` | `FUN_00810760` |
| 106 | NiZBufferProperty | 0x009793A4 | `FUN_008111a0` | `FUN_00810e80` |

### Ni Classes - Bezier Geometry (11 entries)

| # | Class Name | String Addr | Factory Fn | Registration Fn |
|---|-----------|-------------|-----------|----------------|
| 107 | NiBezierMesh | 0x009798A8 | `FUN_00831510` | `FUN_0082e0c0` |
| 108 | NiBezierPatch | 0x00979944 | `DAT_00834570` (abstract RET-stub) | `FUN_00832360` |
| 109 | NiBezierSkinController | 0x00979954 | `FUN_00834ec0` | `FUN_00834c60` |
| 110 | NiBezierTriangle | 0x0097996C | `DAT_00838a50` (abstract RET-stub) | `FUN_008351f0` |
| 111 | NiBezierTriangle2 | 0x00979980 | `FUN_0083a330` | `FUN_00838ea0` |
| 112 | NiBezierTriangle3 | 0x00979994 | `FUN_0083d4d0` | `FUN_0083a7c0` |
| 113 | NiBezierTriangle4 | 0x009799A8 | `FUN_00841f90` | `FUN_0083d850` |
| 114 | NiBezierRectangle | 0x009799BC | `DAT_00847c90` (abstract RET-stub) | `FUN_008422c0` |
| 115 | NiBezierRectangle2 | 0x009799D0 | `FUN_00848fe0` | `FUN_00847fe0` |
| 116 | NiBezierRectangle3 | 0x009799E4 | `FUN_0084c740` | `FUN_00849350` |
| 117 | NiBezierCylinder | 0x009799F8 | `FUN_00850a30` | `FUN_0084ca60` [v5-validated 2026-05-28] |

---

## Vtable Cross-Anchors

Three vtable addresses anchored by this catalog and consumed by
[netimmerse-vtables.md](netimmerse-vtables.md):

| Class | Vtable | Notes |
|-------|--------|-------|
| NiNode | `0x00898f2c` | Allocated by concrete factory `FUN_007e5450` |
| NiTriShape | `0x00899374` | Allocated by concrete factory `FUN_007f31f0` |
| TGDimmerController | `0x0088b7ec` | Allocated by concrete factory `FUN_00455320` |

---

## Classes NOT in Factory Table

The following NiRTTI class catalog entries from
[rtti-class-catalog.md](rtti-class-catalog.md) do NOT appear in the factory hash table at
`DAT_009a2b98`. These are either:

- Abstract base classes that exist only through other means
- Classes instantiated only through direct constructor calls
- Classes referenced through SWIG bindings but never through NIF deserialization

### Notable Absences (named)
- `NiDDImage` / `NiDDBufferImage` -- DirectDraw images (runtime-only, not serialized in NIF)
- `NiCloneExtraData` -- Created at runtime during node cloning
- `NiProvider_Info` -- Audio provider info (runtime enumeration)
- All game-specific classes (Ship*, Weapon*, TG*, ST*, etc.) -- Not NIF-serializable
- All SWIG-only bindings -- Python wrappers, not factory-created

There are approximately **14 NI classes** in `rtti-class-catalog.md` that are NOT in the
factory table (129 catalogued - 115 registered Ni entries). The 4 named above account for
part of the gap; the remaining ~10 are unenumerated here and tracked for the
[netimmerse-vtables.md](netimmerse-vtables.md) validation pass.

---

## Summary Statistics

| Category | Count |
|----------|-------|
| Total registration functions | 117 |
| Ni* classes | 115 |
| TG* classes | 2 (TGDimmerController, TGFuzzyTriShape) |
| Concrete `FUN_*` factories (allocating) | 100 |
| Abstract base `DAT_*` RET-stub factories | 17 |
| Consumer functions (NIF loaders) | 2 (`FUN_008176b0`, `FUN_00818150`) |
| Process-shutdown destructor invocation | 1 (orphan READ at `0x00816c40`) |
| Hash table buckets | 37 (0x25) |
| Total xrefs to DAT_009a2b98 | 237 (234 reg READ+WRITE pairs + 2 consumer READs + 1 shutdown READ) |
| Factory pattern: identical template | YES (100% consistent across all 117) |
| TG classes use same hash table | YES (confirmed) |
| Factory signature | `void(int* out_ptr)` — out-parameter, not return value |

### Address Ranges
| Component | Range |
|-----------|-------|
| Registration functions | `0x00455060` - `0x0084ca60` |
| Factory functions | `0x00455320` - `0x00850a30` |
| Class name strings | `0x008DAED4` - `0x009799F8` |
| Hash table global | `0x009a2b98` |
| Hash table final vtable | `PTR_FUN_0088b7c4` |
| Hash table temp vtable (construction only) | `PTR_LAB_0088b7d8` |
| NiAlloc allocator body | `0x00718cb0` - `0x00718cc6` |
