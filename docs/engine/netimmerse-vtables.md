> [docs](../README.md) / [engine](README.md) / netimmerse-vtables.md

---
title: NetImmerse 3.1 Vtable Map
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
  - claim: "NiObject vtable at 0x00898b94 — 12 slots, 0x30 bytes"
    address: 0x00898b94
    function: FUN_007d87a0
    confidence: high
    note: "Ctor FUN_007d87a0 writes `*this = &PTR_LAB_0x00898b94`. Vtable boundary at 0x00898bc4 (next vtable FUN_007d9960)."
  - claim: "NiObjectNET vtable at 0x00898c48 — 12 slots, 0x30 bytes"
    address: 0x00898c48
    function: FUN_007dac80
    confidence: high
    note: "Ctor FUN_007dac80 writes `*this = &PTR_LAB_0x00898c48`. Vtable boundary at 0x00898c78. Same slot count as NiObject — NiObjectNET adds 0 new virtuals."
  - claim: "NiAVObject vtable at 0x00898ca8 — 39 slots, 0x9C bytes"
    address: 0x00898ca8
    function: FUN_007dc0c0
    confidence: high
    note: "Ctor FUN_007dc0c0 writes `*this = &PTR_LAB_0x00898ca8`. Vtable boundary at 0x00898d44 (an additional vtable, possibly NiCamera). Adds 27 virtuals over NiObjectNET."
  - claim: "NiNode vtable at 0x00898f2c — 43 slots, 0xAC bytes"
    address: 0x00898f2c
    function: FUN_007e5450
    confidence: high
    note: "NiNode factory FUN_007e5450 writes this vtable; child-list helper sub-vtable starts at 0x00898fdc. Adds 4 new virtuals over NiAVObject. Slot 43 ambiguity tracked in open questions."
  - claim: "NiGeometry vtable at 0x00899164 — 64 slots, 0x100 bytes"
    address: 0x00899164
    function: FUN_007edd10
    confidence: high
    note: "Ctor FUN_007edd10 writes this vtable. Boundary at 0x00899264 (NiTriBasedGeom). Adds 25 virtuals over NiAVObject."
  - claim: "NiTriBasedGeom vtable at 0x00899264 — 68 slots, 0x110 bytes (intermediate base)"
    address: 0x00899264
    function: FUN_007ef260
    confidence: high
    note: "PRIOR DOC MISLABELED THIS AS NiTriShape. GetRTTI stub at 0x007f1220 (slot 0) returns 0x009a1af8 = NiTriBasedGeom RTTI ptr. Ctor FUN_007ef260 writes this intermediate vtable; the NiTriShape factory then overwrites it. Adds 4 virtuals over NiGeometry."
  - claim: "NiTriShape canonical vtable at 0x00899374 (~48 slots, ~0xC0 bytes)"
    address: 0x00899374
    function: FUN_007f31f0
    confidence: high
    note: "PREVIOUSLY ABSENT FROM DOC. Factory FUN_007f31f0 OVERWRITES the intermediate NiTriBasedGeom vtable with this final vtable (two-stage construction). GetRTTI stub at 0x004e7d10 (slot 0) returns 0x009a1bb8 = canonical NiTriShape RTTI ptr (28 xrefs from game-code range). Per-slot map TBD."
  - claim: "Constructor chain: NiObject → NiObjectNET → NiAVObject → {NiNode | NiGeometry → NiTriBasedGeom → NiTriShape}"
    address: null
    function: null
    confidence: high
    note: "Each ctor calls parent, initializes fields, writes its vtable. NiTriShape factory FUN_007f31f0 invokes NiTriBasedGeom ctor FUN_007ef260 (writes 0x00899264), then overwrites with 0x00899374."
  - claim: "__purecall stub at 0x00859a0b"
    address: 0x00859a0b
    function: null
    confidence: high
    note: "Bytes `6A 19 E8 69 13 00 00 59 C3` = `push 0x19 ; call 0x0086ad79 ; pop ecx ; ret`. Standard MSVC. Used in NiGeometry slot 49 — confirms NiGeometry IS abstract."
  - claim: "NiObject NiRTTI ptr storage at 0x009a1468"
    address: 0x009a1468
    function: null
    confidence: high
    note: "GetRTTI stub at 0x00458770 is `mov eax, 0x009a1468 ; ret`. Distinct from RTTI string at 0x009780D8."
  - claim: "NiObject global instance counter at 0x009a1478"
    address: 0x009a1478
    function: FUN_007d87a0
    confidence: high
    note: "Ctor FUN_007d87a0 increments; dtor FUN_007d87f0 decrements."
  - claim: "RTTI factory hash table at 0x009a2b98"
    address: 0x009a2b98
    function: null
    confidence: high
    note: "Cross-anchor to nirtti-factory-catalog.md (verified). 237 xrefs total."
  - claim: "Slot 11 universal no-op at 0x0040da50"
    address: 0x0040da50
    function: null
    confidence: high
    note: "Single byte `C3` (ret). Confirmed across NiObject, NiObjectNET, NiAVObject, NiNode — never overridden in any class in the chain."
  - claim: "Per-class NiRTTI ptr storage addresses verified via GetRTTI stubs"
    address: null
    function: null
    confidence: high
    note: "NiObject 0x009a1468; NiObjectNET 0x009a1500; NiAVObject 0x009a1578; NiNode 0x009a1870; NiGeometry 0x009a1a98; NiTriBasedGeom 0x009a1af8; NiTriShape 0x009a1bb8. Each verified via the class's GetRTTI stub `mov eax, IMM ; ret` bytes."
  - claim: "NiObject slot 0 = GetRTTI at 0x00458770"
    address: 0x00458770
    function: null
    confidence: high
    note: "`mov eax, 0x009a1468 ; ret`. Returns NiObject RTTI ptr."
  - claim: "NiObject slot 7 = SaveBinary at FUN_007d8a40"
    address: 0x007d8a40
    function: FUN_007d8a40
    confidence: high
    note: "Calls vtable[0] (GetRTTI), writes RTTI name string then object index to stream."
  - claim: "NiObject slot 11 = 0x0040da50 (no-op ret)"
    address: 0x0040da50
    function: null
    confidence: high
    note: "Single 0xC3. Never overridden across NiObject/NiObjectNET/NiAVObject/NiNode."
  - claim: "NiObjectNET slot 0 = GetRTTI at 0x007dba40"
    address: 0x007dba40
    function: null
    confidence: high
    note: "Returns 0x009a1500 = NiObjectNET RTTI ptr."
  - claim: "NiObjectNET slot 4 = RegisterStreamables at FUN_007db5f0"
    address: 0x007db5f0
    function: FUN_007db5f0
    confidence: high
    note: "Calls parent RegisterStreamables, then FUN_00818a00 (stream hash registration), then vtable writes."
  - claim: "NiAVObject slot 0 = GetRTTI at 0x007ddf90"
    address: 0x007ddf90
    function: null
    confidence: high
    note: "Returns 0x009a1578 = NiAVObject RTTI ptr."
  - claim: "NiAVObject slot 7 = SaveBinary at FUN_007dd6a0"
    address: 0x007dd6a0
    function: FUN_007dd6a0
    confidence: high
    note: "Calls parent SaveBinary then writes ~7 NiAVObject-specific fields."
  - claim: "NiNode slot 0 = GetRTTI at 0x004e3640"
    address: 0x004e3640
    function: null
    confidence: high
    note: "Returns 0x009a1870 = NiNode RTTI ptr."
  - claim: "NiNode slot 39 = AttachChild(NiAVObject*, bool atEnd) at FUN_007e39b0"
    address: 0x007e39b0
    function: FUN_007e39b0
    confidence: high
    note: "Sets parent ptr, adds to child array (NiTArray), increments refcount."
  - claim: "NiNode slot 41 = DetachChildAt(uint index) at FUN_007e3a30"
    address: 0x007e3a30
    function: FUN_007e3a30
    confidence: high
    note: "Bounds-check, nullify child slot, clear parent ptr, decrement refcount."
  - claim: "NiGeometry slot 0 = GetRTTI at 0x007eeaa0"
    address: 0x007eeaa0
    function: null
    confidence: high
    note: "Returns 0x009a1a98 = NiGeometry RTTI ptr."
  - claim: "NiGeometry slot 45 = scalar deleting destructor at FUN_007ef050"
    address: 0x007ef050
    function: FUN_007ef050
    confidence: high
    note: "Calls FUN_007eecd0 (real dtor) then conditionally NiFree (FUN_00718cf0) if (param & 1). Matches MSVC scalar-deleting-dtor canonical form. Prior doc undersold this as '(NiGeometry-specific)'."
  - claim: "NiTriBasedGeom slot 0 = GetRTTI at 0x007f1220 (vtable 0x00899264)"
    address: 0x007f1220
    function: null
    confidence: high
    note: "Returns 0x009a1af8 = NiTriBasedGeom RTTI ptr — confirms vtable 0x00899264 IS NiTriBasedGeom, not NiTriShape."
  - claim: "NiTriShape canonical slot 0 = GetRTTI at 0x004e7d10 (vtable 0x00899374)"
    address: 0x004e7d10
    function: null
    confidence: high
    note: "Returns 0x009a1bb8 = canonical NiTriShape RTTI ptr (28 xrefs from game-code range 0x004xxxxx-0x006xxxxx)."
  - claim: "Two-stage construction pattern (intermediate ctor writes base vtable, derived factory overwrites)"
    address: null
    function: null
    confidence: high
    note: "Documented for NiTriShape: FUN_007ef260 writes 0x00899264, then FUN_007f31f0 overwrites with 0x00899374. NI 3.1 idiom — may apply to other derived chains."
  - claim: "Abstract base classes have vtables — written by constructors, not by factories"
    address: null
    function: null
    confidence: high
    note: "NiObject, NiObjectNET, NiAVObject, NiGeometry, NiTriBasedGeom are abstract per nirtti-factory-catalog (RET-stub factories at DAT_007d8810, DAT_007db5e0, DAT_007dd470, DAT_007ee6b0, DAT_007f0d50). Their vtables are real and runtime-used; they get written when a derived class is built."
companions:
  - docs/engine/nirtti-factory-catalog.md
  - docs/engine/rtti-class-catalog.md
  - docs/engine/gamebryo-cross-reference.md
  - docs/engine/tg-hierarchy-vtables.md
  - docs/engine/function-map.md
  - docs/engine/v5-validation-status.md
supersedes:
  - (prior undated revision)
---

# NetImmerse 3.1 Vtable Map (stbc.exe)

> [!NOTE]
> This doc is `status: verified`. The 7 vtable addresses, constructor chain, `__purecall`
> stub, per-class NiRTTI ptr storage, global counter, factory hash table cross-link,
> universal slot 11 no-op, and 12 individually-decompiled slot samples are v5-anchored
> against the current Ghidra import (2026-05-28). The remaining ~226 of 238 vtable slot
> entries are pattern-extrapolated by inheritance — consistent slot positions relative to
> the parent class, names inferred from decompile rationale — `confidence: medium`, not
> `confidence: low`. A per-slot decompile sweep would promote all 226 to high; tracked as
> documentation debt in [v5-validation-status.md](v5-validation-status.md).
>
> The major correction this pass: **NiTriShape's canonical vtable is at `0x00899374`, NOT
> `0x00899264`** — the prior doc had it backwards. The vtable at `0x00899264` is
> NiTriBasedGeom (intermediate ancestor). See "Two-Stage Construction Pattern" and the new
> "NiTriShape Canonical Vtable" section. See
> [docs/guides/v5-evidence-header.md](../guides/v5-evidence-header.md) for the standard.

## Summary

Systematic mapping of vtable addresses and virtual method slots for the core NetImmerse 3.1
class hierarchy in stbc.exe. Derived from constructor-chain analysis, vtable-boundary
detection (xref scanning), and behavioral decompilation of individual vtable entries. Cross-
anchored with [nirtti-factory-catalog.md](nirtti-factory-catalog.md) (factory addresses) and
[rtti-class-catalog.md](rtti-class-catalog.md) (class strings).

## Abstract Base Classes Have Vtables

Per [nirtti-factory-catalog.md](nirtti-factory-catalog.md), several classes in this chain are
**abstract base classes** registered with RET-stub `DAT_*` factories: NiObject
(`DAT_007d8810`), NiObjectNET (`DAT_007db5e0`), NiAVObject (`DAT_007dd470`), NiGeometry
(`DAT_007ee6b0`), and NiTriBasedGeom (`DAT_007f0d50`). Their factories do nothing but allow
runtime type queries to find them in the hash table.

Their **vtables are still real and runtime-used.** They are written by the abstract base's
**constructor** when a derived class is being instantiated — not by the abstract base's
factory. A reader expecting to find a vtable at the address of an abstract-base factory will
come up empty. The vtable lives at the address its constructor writes into `*this` early in
construction.

## Constructor Chain

Each constructor calls its parent, initializes fields, then writes its own vtable pointer.
The final vtable written before the constructor returns is the one used at runtime —
**unless** a derived factory overwrites it after the inner constructor returns (see
[Two-Stage Construction Pattern](#two-stage-construction-pattern)).

```
FUN_007d87a0 (NiObject ctor)              -> writes vtable 0x00898b94
  FUN_007dac80 (NiObjectNET ctor)         -> writes vtable 0x00898c48
    FUN_007dc0c0 (NiAVObject ctor)        -> writes vtable 0x00898ca8
      NiNode path:
        FUN_007e5450 (NiNode factory)     -> writes vtable 0x00898f2c
      NiGeometry path:
        FUN_007edd10 (NiGeometry ctor)    -> writes vtable 0x00899164
          FUN_007ef260 (NiTriBasedGeom ctor) -> writes vtable 0x00899264
            FUN_007f31f0 (NiTriShape factory)  -> OVERWRITES with vtable 0x00899374
```

## Vtable Addresses and Sizes

| Class | Vtable Address | Slots | Size (bytes) | Constructor | Factory | Validated |
|-------|---------------|-------|--------------|-------------|---------|-----------|
| NiObject | 0x00898b94 | 12 (0-11) | 0x30 | FUN_007d87a0 | `DAT_007d8810` (RET-stub) | [v5-validated 2026-05-28] |
| NiObjectNET | 0x00898c48 | 12 (0-11) | 0x30 | FUN_007dac80 | `DAT_007db5e0` (RET-stub) | [v5-validated 2026-05-28] |
| NiAVObject | 0x00898ca8 | 39 (0-38) | 0x9C | FUN_007dc0c0 | `DAT_007dd470` (RET-stub) | [v5-validated 2026-05-28] |
| NiNode | 0x00898f2c | 43 (0-42) | 0xAC | (via factory) | FUN_007e5450 | [v5-validated 2026-05-28] |
| NiGeometry | 0x00899164 | 64 (0-63) | 0x100 | FUN_007edd10 | `DAT_007ee6b0` (RET-stub) | [v5-validated 2026-05-28] |
| **NiTriBasedGeom** | **0x00899264** | 68 (0-67) | 0x110 | FUN_007ef260 | `DAT_007f0d50` (RET-stub) | [v5-validated 2026-05-28] |
| **NiTriShape** (canonical) | **0x00899374** | ~48 | ~0xC0 | (via factory) | FUN_007f31f0 | [v5-validated 2026-05-28: address + slot 0; per-slot map TBD] |

> **Vtable size vs object size**: the "Size (bytes)" column above is the **vtable** size
> (slot count × 4). For **object/instance** sizes, see [Object Sizes](#object-sizes) below —
> they measure different things and will not match.

### Inheritance Accounting

- NiObjectNET adds **0** new virtual methods over NiObject (same 12 slots, all overridden).
- NiAVObject adds **27** new virtuals over NiObjectNET (slots 12-38).
- NiNode adds **4** new virtuals over NiAVObject (slots 39-42).
- NiGeometry adds **25** new virtuals over NiAVObject (slots 39-63).
- NiTriBasedGeom adds **4** new virtuals over NiGeometry (slots 64-67). Total vtable size
  0x110 / 4 = 68 slots — matches the boundary measurement.
- NiTriShape's canonical vtable at 0x00899374 has approximately **48 slots** by boundary
  heuristic. Full per-slot inheritance accounting is **open question #1** — the canonical
  layout may not be a simple extension of NiTriBasedGeom, and there are anomalous non-pointer
  bytes at offsets +0x9C and +0xA0 (see [NiTriShape Canonical Vtable](#nitrishape-canonical-vtable-0x00899374)).

> Gamebryo 1.2 source says NiNode adds 5 (AttachChild, DetachChild, DetachChildAt, SetAt,
> UpdateUpwardPass); NI 3.1 has 4, suggesting UpdateUpwardPass either does not exist yet or
> is merged into another slot.

## Key Constants

All `[v5-validated 2026-05-28]`:

| Anchor | Address | Notes |
|--------|---------|-------|
| `__purecall` stub | 0x00859a0b | `push 0x19 ; call 0x0086ad79 ; pop ecx ; ret`. Standard MSVC. |
| Universal slot 11 no-op | 0x0040da50 | Single byte `C3` (ret). Never overridden. |
| RTTI factory hash table | 0x009a2b98 | Cross-anchor: [nirtti-factory-catalog.md](nirtti-factory-catalog.md). |
| NiObject global counter | 0x009a1478 | Incremented in ctor, decremented in dtor. |
| NiObject NiRTTI ptr storage | 0x009a1468 | GetRTTI stub at 0x00458770 returns this. |
| NiObjectNET NiRTTI ptr storage | 0x009a1500 | GetRTTI stub at 0x007dba40 returns this. |
| NiAVObject NiRTTI ptr storage | 0x009a1578 | GetRTTI stub at 0x007ddf90 returns this. |
| NiNode NiRTTI ptr storage | 0x009a1870 | GetRTTI stub at 0x004e3640 returns this. |
| NiGeometry NiRTTI ptr storage | 0x009a1a98 | GetRTTI stub at 0x007eeaa0 returns this. |
| NiTriBasedGeom NiRTTI ptr storage | 0x009a1af8 | GetRTTI stub at 0x007f1220 returns this. |
| NiTriShape NiRTTI ptr storage | 0x009a1bb8 | GetRTTI stub at 0x004e7d10 returns this. |

> The **NiRTTI ptr storage** is a `.data` location holding a pointer to the class's NiRTTI
> structure. The pattern `mov eax, IMM ; ret` in the GetRTTI stub identifies it. Do not
> confuse this with the **NiRTTI string** addresses (e.g., 0x009780D8 = "NiObject") which
> live elsewhere — see [rtti-class-catalog.md](rtti-class-catalog.md).

## Two-Stage Construction Pattern

NiTriShape construction reveals a pattern future investigators should watch for in other
derived classes. The intermediate base-class constructor writes a vtable; then the derived
factory **overwrites** that vtable with the canonical runtime vtable before the object is
returned to the caller.

Concretely: `FUN_007ef260` (NiTriBasedGeom ctor) writes `*this = 0x00899264` early in its
body. After it returns, `FUN_007f31f0` (NiTriShape factory) writes `*this = 0x00899374` over
the same slot. A reader observing only the NiTriBasedGeom ctor would (incorrectly) conclude
that `0x00899264` is the runtime vtable for the constructed object.

This is a NI 3.1 idiom. When validating other derived chains where a single factory
allocates and constructs a derived class, check whether the inner constructor's vtable write
survives or gets overwritten. The `0x00899264` vtable is a **transient construction state**
that only exists while `FUN_007ef260` is on the stack — at runtime no instance has it.

## NiObject Vtable (0x00898b94) — 12 slots

All NiObject-derived classes share these first 12 slots in the same order. Slot 0 is
GetRTTI (NOT a destructor) and slot 10 is the scalar deleting destructor — opposite of the
Gamebryo 1.2 layout.

| Slot | Offset | NiObject Impl | NiObjectNET Impl | Name (NI 3.1) | Evidence |
|------|--------|---------------|-------------------|---------------|----------|
| 0 | +0x00 | 0x00458770 | 0x007dba40 | **GetRTTI** | `mov eax, 0x009a1468 ; ret` [v5-validated 2026-05-28] |
| 1 | +0x04 | 0x00458780 | 0x007dae00 | **CreateClone** | Overridden in every derived class; base is likely no-op or abstract |
| 2 | +0x08 | 0x00438ff0 | FUN_007db060 | **ProcessClone** | NiObjectNET impl clones ExtraData (this+0x10) |
| 3 | +0x0C | 0x00439000 | FUN_007db080 | **PostLinkObject** | NiObjectNET impl processes TimeController (this+0xC) |
| 4 | +0x10 | FUN_007d8820 | FUN_007db5f0 | **RegisterStreamables** | NiObjectNET: calls parent, then FUN_00818a00 (stream hash register), then vtable writes [v5-validated 2026-05-28 for NiObjectNET] |
| 5 | +0x14 | FUN_007d8930 | FUN_007db630 | **LoadBinary** | NiObject base is empty `return;`; NiObjectNET reads name + extras |
| 6 | +0x18 | FUN_007d8940 | FUN_007db6c0 | **LinkObject** | Calls FUN_00817170 (stream hash insert); resolves object references post-load |
| 7 | +0x1C | FUN_007d8a40 | FUN_007db700 | **SaveBinary** | NiObject: calls vtable[0] (GetRTTI), writes RTTI name string then object index [v5-validated 2026-05-28] |
| 8 | +0x20 | FUN_007d8a70 | FUN_007db740 | **IsEqual** | Compares RTTI names (calls slot 0 on both objects, strcmp) |
| 9 | +0x24 | FUN_007d8ae0 | FUN_007db860 | **AddViewerStrings** | NiObject adds "m_iRefCount"; NiObjectNET adds name/controllers/extradata |
| 10 | +0x28 | 0x007d87c0 | FUN_007dba50 | **scalar_deleting_dtor** | MSVC pattern: call real dtor, then `if (param & 1) free(this)` |
| 11 | +0x2C | 0x0040da50 | 0x0040da50 | **(no-op, never overridden)** | Single `ret` byte. Same address across NiObject/NiObjectNET/NiAVObject/NiNode [v5-validated 2026-05-28] |

### Slot Order vs Gamebryo 1.2

NI 3.1 slot order differs significantly from Gamebryo 1.2:

| NI 3.1 Slot | NI 3.1 Method | Gb 1.2 Slot | Notes |
|-------------|---------------|-------------|-------|
| 0 | GetRTTI | 1 | Moved to slot 0 (no dtor at slot 0) |
| 1 | CreateClone | 2 | |
| 2 | ProcessClone | 10 | Moved much earlier |
| 3 | PostLinkObject | 11 | Moved much earlier |
| 4 | RegisterStreamables | 5 | |
| 5 | LoadBinary | 3 | |
| 6 | LinkObject | 4 | |
| 7 | SaveBinary | 6 | |
| 8 | IsEqual | 7 | |
| 9 | AddViewerStrings | 9 | Same |
| 10 | scalar_deleting_dtor | 0 | MSVC dtor moved to slot 10 |
| 11 | (no-op, never overridden) | 8? | Possibly GetViewerStrings (base impl) |

The MSVC scalar deleting destructor is at slot 10, NOT slot 0. GetRTTI occupies slot 0
instead. This is the opposite of the Gamebryo 1.2 layout. See
[gamebryo-cross-reference.md](gamebryo-cross-reference.md) for full Gb 1.2 cross-reference.

## NiAVObject Vtable (0x00898ca8) — 39 slots

Slots 0-11 inherited from NiObject (overridden as needed). Slots 12-38 are NiAVObject-specific.

| Slot | Offset | Function | Name (Proposed) | Evidence |
|------|--------|----------|-----------------|----------|
| 0 | +0x00 | 0x007ddf90 | GetRTTI | `mov eax, 0x009a1578 ; ret` [v5-validated 2026-05-28] |
| 1 | +0x04 | 0x007dd2b0 | CreateClone | |
| 2 | +0x08 | FUN_007dd3e0 | ProcessClone | |
| 3 | +0x0C | FUN_007dd3f0 | PostLinkObject | |
| 4 | +0x10 | FUN_007dd480 | RegisterStreamables | |
| 5 | +0x14 | FUN_007dd5f0 | LoadBinary | |
| 6 | +0x18 | FUN_007dd630 | LinkObject | |
| 7 | +0x1C | FUN_007dd6a0 | SaveBinary | Calls parent, writes ~7 NiAVObject-specific fields [v5-validated 2026-05-28] |
| 8 | +0x20 | FUN_007dd7b0 | IsEqual | |
| 9 | +0x24 | FUN_007dda10 | AddViewerStrings | |
| 10 | +0x28 | FUN_007ddfa0 | scalar_deleting_dtor | |
| 11 | +0x2C | 0x0040da50 | (no-op) | Never overridden |
| 12 | +0x30 | 0x004341b0 | UpdateControllers? | Small stub, part of update pipeline |
| 13 | +0x34 | 0x004341c0 | UpdateNodeBound? | Small stub |
| 14 | +0x38 | 0x00434240 | ApplyTransform? | |
| 15 | +0x3C | 0x00434250 | GetObjectByName? | |
| 16 | +0x40 | 0x00434260 | SetSelectiveUpdateFlags? | |
| 17 | +0x44 | 0x00434270 | UpdateDownwardPass? | |
| 18 | +0x48 | 0x00434280 | UpdateSelectedDownwardPass? | |
| 19 | +0x4C | 0x00434290 | UpdateRigidDownwardPass? | |
| 20 | +0x50 | 0x00434180 | UpdatePropertiesDownward? | |
| 21 | +0x54 | 0x004341a0 | UpdateEffectsDownward? | |
| 22 | +0x58 | NiAVObject__GetObjectByName | **GetObjectByName** | Confirmed: strcmp(this->name, searchName), returns this if match. NiNode override recurses children. |
| 23 | +0x5C | 0x00434210 | UpdateWorldBound? | |
| 24 | +0x60 | 0x00434220 | Display? | |
| 25 | +0x64 | FUN_007dc5f0 | PurgeRendererData? | |
| 26 | +0x68 | 0x00456e90 | (unknown) | |
| 27 | +0x6C | 0x007dc7a0 | (unknown) | |
| 28 | +0x70 | 0x007dca60 | (unknown) | |
| 29 | +0x74 | FUN_007dc780 | (unknown) | |
| 30 | +0x78 | FUN_007dca40 | (unknown) | |
| 31 | +0x7C | 0x004341e0 | (unknown) | |
| 32 | +0x80 | 0x004341f0 | (unknown) | |
| 33 | +0x84 | 0x00434200 | (unknown) | |
| 34 | +0x88 | 0x00434230 | (unknown) | |
| 35 | +0x8C | FUN_007dcb50 | (unknown) | |
| 36 | +0x90 | FUN_007dcb70 | (unknown) | |
| 37 | +0x94 | FUN_008201a0 | (unknown) | |
| 38 | +0x98 | 0x004341d0 | (unknown) | |

### Notes on NiAVObject slots 12-38

- Many small stubs (0x0043xxxx range) are base implementations that return quickly.
- NI 3.1 has 27 NiAVObject-specific virtuals; Gamebryo 1.2 declares ~14 NiAVObject virtuals.
- This means NI 3.1 has ~13 additional virtuals not present in Gamebryo 1.2.
- These extra slots may include: collision, picking, sorting, visibility, and BC-specific extensions.

## NiNode Vtable (0x00898f2c) — 43 slots

Slots 0-38 inherited from NiAVObject (many overridden). Slots 39-42 are NiNode-specific.

| Slot | Offset | Function | Name | Evidence |
|------|--------|----------|------|----------|
| 0 | +0x00 | 0x004e3640 | GetRTTI | `mov eax, 0x009a1870 ; ret` [v5-validated 2026-05-28] |
| 1 | +0x04 | FUN_007e4f30 | CreateClone | |
| 2 | +0x08 | FUN_007e5180 | ProcessClone | Iterates children |
| 3 | +0x0C | FUN_007e53e0 | PostLinkObject | |
| 4 | +0x10 | FUN_007e5630 | RegisterStreamables | Registers self + children |
| 5 | +0x14 | FUN_007e57d0 | LoadBinary | Reads child count, loads children |
| 6 | +0x18 | FUN_007e58d0 | LinkObject | Links children by index |
| 7 | +0x1C | FUN_007e5940 | SaveBinary | Writes child array to stream |
| 8 | +0x20 | FUN_007e5a00 | IsEqual | |
| 9 | +0x24 | FUN_007e5b30 | AddViewerStrings | |
| 10 | +0x28 | FUN_007e67d0 | scalar_deleting_dtor | |
| 11 | +0x2C | 0x0040da50 | (no-op) | Never overridden |
| 12 | +0x30 | 0x007e3e30 | UpdateControllers | NiNode override iterates children |
| 13 | +0x34 | 0x004341c0 | (stub) | Inherited from NiAVObject |
| 14 | +0x38 | NiNode__ApplyTransform | **ApplyTransform** | NiNode override |
| 15 | +0x3C | NiNode__vfn15_IterateChildren | **(unknown)** | Iterates children calling +0x3C; purpose unclear in NI 3.1 |
| 16 | +0x40 | NiNode__SetSelectiveUpdateFlags | **SetSelectiveUpdateFlags** | NiNode override |
| 17 | +0x44 | NiNode__UpdateDownwardPass | **UpdateDownwardPass** | NiNode override iterates children |
| 18 | +0x48 | NiNode__UpdateSelectedDownwardPass | **UpdateSelectedDownwardPass** | NiNode override |
| 19 | +0x4C | NiNode__UpdateRigidDownwardPass | **UpdateRigidDownwardPass** | NiNode override |
| 20 | +0x50 | 0x00434180 | (inherited) | Same as NiAVObject |
| 21 | +0x54 | 0x004341a0 | (inherited) | Same as NiAVObject |
| 22 | +0x58 | NiNode__GetObjectByName | **GetObjectByName** | Calls NiAVObject base (name check), then recurses children |
| 23 | +0x5C | NiNode__UpdateWorldBound | **UpdateWorldBound** | NiNode override |
| 24 | +0x60 | NiNode__Display | **Display** | NiNode override iterates children |
| 25 | +0x64 | FUN_007e3ff0 | PurgeRendererData | NiNode override |
| 26 | +0x68 | 0x004d5170 | (override) | |
| 27 | +0x6C | NiNode__UpdatePropertiesDownward | **UpdatePropertiesDownward** | NiNode override |
| 28 | +0x70 | NiNode__UpdateEffectsDownward | **UpdateEffectsDownward** | NiNode override |
| 29 | +0x74 | FUN_007dc780 | (inherited) | Same as NiAVObject |
| 30 | +0x78 | FUN_007dca40 | (inherited) | Same as NiAVObject |
| 31 | +0x7C | FUN_007e46f0 | (override) | |
| 32 | +0x80 | FUN_007e4b00 | (override) | Picks/intersects children recursively using vtable+0x80 |
| 33 | +0x84 | FUN_007e4bd0 | (override) | |
| 34 | +0x88 | FUN_007e4d30 | (override) | |
| 35 | +0x8C | FUN_007dcb50 | (inherited) | Same as NiAVObject |
| 36 | +0x90 | FUN_007dcb70 | (inherited) | Same as NiAVObject |
| 37 | +0x94 | FUN_008201a0 | (inherited) | Same as NiAVObject |
| 38 | +0x98 | 0x007e4170 | (override) | NiAVObject base=0x4341d0, NiNode overrides |
| **39** | **+0x9C** | **FUN_007e39b0** | **AttachChild** | Takes (this, NiAVObject*, bool atEnd); sets parent ptr, adds to child array [v5-validated 2026-05-28] |
| **40** | **+0xA0** | **FUN_007e3b30** | **DetachChild(NiAVObject*)** | Iterates children looking for match, removes |
| **41** | **+0xA4** | **FUN_007e3a30** | **DetachChildAt(uint)** | Bounds-check, nullify child slot, clear parent ptr, decrement refcount [v5-validated 2026-05-28] |
| **42** | **+0xA8** | **FUN_007e3c50** | **SetAt(uint, NiAVObject*)** | Replaces child at index |

### Shared vs Overridden Slots (NiAVObject → NiNode)

| Category | Slots |
|----------|-------|
| Inherited unchanged | 11, 13, 20, 21, 29, 30, 35, 36, 37 |
| Overridden by NiNode | 0-10, 12, 14-19, 22-28, 31-34, 38 |
| New in NiNode | 39-42 |

## NiGeometry Vtable (0x00899164) — 64 slots

NiGeometry adds 25 new virtual methods over NiAVObject's 39 (slots 39-63). This is
substantially more than Gamebryo 1.2 documents, suggesting NI 3.1 had more geometry-specific
virtuals that were later consolidated or removed.

Selected entries:

| Slot | Offset | Function | Notes |
|------|--------|----------|-------|
| 0 | +0x00 | 0x007eeaa0 | GetRTTI — `mov eax, 0x009a1a98 ; ret` [v5-validated 2026-05-28] |
| 1 | +0x04 | 0x007ee660 | CreateClone |
| 2 | +0x08 | FUN_007ee6a0 | ProcessClone |
| 3 | +0x0C | FUN_007dd3f0 | PostLinkObject (inherited from NiAVObject) |
| ... | ... | ... | ... |
| 45 | +0xB4 | FUN_007ef050 | **scalar deleting destructor** — calls FUN_007eecd0 (real dtor) then conditionally NiFree (FUN_00718cf0) if (param & 1). Matches MSVC scalar-deleting-dtor canonical form. [v5-validated 2026-05-28] |
| 46 | +0xB8 | 0x0040da50 | (no-op) |
| 47 | +0xBC | 0x007eda70 | |
| 48 | +0xC0 | 0x007eda80 | |
| 49 | +0xC4 | 0x00859a0b | **`__purecall`** (pure virtual) [v5-validated 2026-05-28] |
| 50 | +0xC8 | 0x004fb450 | |
| 51 | +0xCC | 0x007ef080 | |
| 52 | +0xD0 | 0x007ef090 | |
| ... | ... | ... | ... |

Slot 49 is `__purecall`, confirming NiGeometry IS abstract (cannot be instantiated) — which
matches its RET-stub factory `DAT_007ee6b0` in
[nirtti-factory-catalog.md](nirtti-factory-catalog.md).

## NiTriBasedGeom Vtable (0x00899264) — 68 slots

> **Renamed from "NiTriShape" in the prior doc revision.** The vtable at `0x00899264` is
> NiTriBasedGeom — the intermediate ancestor between NiGeometry and NiTriShape — not
> NiTriShape itself. See [Two-Stage Construction Pattern](#two-stage-construction-pattern).

NiTriBasedGeom adds 4 new virtuals over NiGeometry's 64 (slots 64-67). Total vtable size
0x110 / 4 = 68 slots — matches the boundary measurement (next vtable starts at `0x00899374`).

Selected entries:

| Slot | Offset | Function | Notes |
|------|--------|----------|-------|
| 0 | +0x00 | 0x007f1220 | GetRTTI — `mov eax, 0x009a1af8 ; ret`. Returns **NiTriBasedGeom** RTTI ptr, NOT NiTriShape. [v5-validated 2026-05-28] |
| 1 | +0x04 | 0x007f0d00 | CreateClone |
| 2 | +0x08 | FUN_007f0d40 | ProcessClone |
| 3 | +0x0C | FUN_007dd3f0 | PostLinkObject (inherited from NiAVObject) |

This vtable is **transient at runtime**: it is written by the NiTriBasedGeom constructor
(`FUN_007ef260`) but then overwritten by the NiTriShape factory (`FUN_007f31f0`) before the
allocated object is returned. No live NiTriShape instance has `0x00899264` in its vtable
slot — only intermediate construction state observes this vtable. See
[Two-Stage Construction Pattern](#two-stage-construction-pattern).

If NiTriBasedGeom were instantiable on its own, its instances would carry this vtable. It is
abstract per [nirtti-factory-catalog.md](nirtti-factory-catalog.md) (RET-stub factory
`DAT_007f0d50`), so the only role for this vtable on the wire is the construction window
during NiTriShape (and any future derived class's) allocation.

## NiTriShape Canonical Vtable (0x00899374)

> Previously absent from this doc entirely. The full per-slot map is **documentation debt**
> — only slot 0 is verified at v5-high confidence. The non-slot-0 entries below the boundary
> heuristic carry the doc-level `confidence: medium` from the NOTE block.

| Property | Value |
|----------|-------|
| Vtable base | `0x00899374` |
| Slot 0 | `0x004e7d10` — GetRTTI returns `0x009a1bb8` (canonical NiTriShape RTTI ptr, 28 xrefs from game-code range) [v5-validated 2026-05-28] |
| Approximate slot count | ~48 (boundary heuristic places next vtable near `0x00899434`) |
| Approximate size | ~0xC0 bytes |
| Written by | NiTriShape factory `FUN_007f31f0` (overwrites `0x00899264` from intermediate ctor) |

### Anomaly

Bytes at offsets `+0x9C` (would be slot 39) and `+0xA0` (slot 40) are non-pointer values:

| Offset | Bytes | Decoded as DWORD |
|--------|-------|------------------|
| +0x9C | `80 96 18 4B` | `0x4B189680` |
| +0xA0 | `60 42 A2 0D` | `0x0DA24260` |

Neither value falls in the binary's code range (above `0x008xxxxx` EOF). Two
interpretations, both open questions:

1. **Inline floats stored unusually in vtable space**: `0x4B189680` as IEEE-754 float ≈
   9,985,664.0; `0x0DA24260` ≈ very small magnitude. Unusual to find inline data inside a
   vtable, but it would not be unprecedented for NI 3.1.
2. **Vtable actually ends at slot 38** (~0x9C from start), and the bytes after are
   `.rdata` padding or a different data object that happens to immediately follow.

Promotion to the high-confidence per-slot map requires resolving this anomaly. Tracked as
**open question #1** in [v5-validation-status.md](v5-validation-status.md).

## Vtable Offset Quick Reference

For code that uses `vtable[offset]` patterns:

| Offset | Method (NiObject slots) |
|--------|------------------------|
| +0x00 | GetRTTI() |
| +0x04 | CreateClone() |
| +0x08 | ProcessClone() |
| +0x0C | PostLinkObject() |
| +0x10 | RegisterStreamables() |
| +0x14 | LoadBinary() |
| +0x18 | LinkObject() |
| +0x1C | SaveBinary() |
| +0x20 | IsEqual() |
| +0x24 | AddViewerStrings() |
| +0x28 | scalar_deleting_dtor() |
| +0x2C | (no-op, never overridden) |

For NiNode-specific calls:

| Offset | Method |
|--------|--------|
| +0x9C | AttachChild(NiAVObject*, bool) |
| +0xA0 | DetachChild(NiAVObject*) |
| +0xA4 | DetachChildAt(uint) |
| +0xA8 | SetAt(uint, NiAVObject*) |

For calls via `vtable[0x80]` (seen in NiNode slot 32): slot 32 in NiAVObject/NiNode is a
picking/intersection test method.

For calls via `vtable[0x28]`: slot 10 = scalar_deleting_destructor, called as
`(*vtable[0x28])(1)` to delete.

## Object Sizes

These are **object/instance** sizes (allocation amounts), distinct from the **vtable**
sizes in [Vtable Addresses and Sizes](#vtable-addresses-and-sizes). All sizes derived from
factory allocations where available; abstract bases (no factory allocation) are derived from
constructor field-write offsets and carry medium confidence.

| Class | Size (hex) | Size (dec) | Confidence | Notes |
|-------|-----------|------------|------------|-------|
| NiObject | 0x08 | 8 | medium | Derived from ctor field writes (2 fields). Abstract base, no factory allocation. |
| NiObjectNET | 0x14 | 20 | medium | Derived from ctor field writes (4 fields). Abstract base. |
| NiAVObject | 0xC8 | 200 | high | [v5-validated 2026-05-28; refined by gamebryo-cross-reference doc #7]: derived from NiNode 0xE8 minus NiNode-specific 0x20. Ctor FUN_007dc0c0 writes up to byte 0xC0 with helper FUN_008136c0 completing layout. The +0x38 delta vs MWSE 4.0 (which gives 0x90) lives in V3.1-only fields (Velocity + Has Bounding Volume + Bounding Volume) per nif.xml. Previously listed as 0xC4 medium-confidence (ctor field-write only); refined to 0xC8 via NiNode subtraction + helper-call accounting. |
| NiNode | 0xE8 | 232 | high | [v5-validated 2026-05-28]: confirmed via FUN_007e5450 NiAlloc(0xE8). |
| NiGeometry | 0xE0 | 224 | high | [v5-validated 2026-05-28; refined by doc #7]: derived from NiTriShape 0xE4 minus NiTriBasedGeom field. Ctor FUN_007edd10 writes 6 fields ending at byte 0xDE. |
| NiTriBasedGeom | 0xE4 | 228 | high | [v5-validated 2026-05-28; added by doc #7]: NiGeometry +4 (adds 1 field at byte 0xE0 over NiGeometry). |
| NiTriShape | 0xE4 | 228 | high | [v5-validated 2026-05-28]: confirmed via FUN_007f31f0 NiAlloc(0xE4). No fields beyond NiTriBasedGeom. |

## Open Questions and Documentation Debt

Surfaced to [v5-validation-status.md](v5-validation-status.md) §6 for the next validation
cycle:

1. **NiTriShape canonical vtable per-slot map** at `0x00899374` is missing entirely.
   Approximately 48 slots; only slot 0 is verified. Anomalous non-pointer bytes at
   offsets +0x9C and +0xA0 — either inline data or vtable ends earlier than the boundary
   heuristic suggests. Required to promote NiTriShape claims from sketch to fully mapped.
2. **NiNode 43 vs 44 slot count ambiguity**: the slot at offset +0xAC reads `0x007e4150` —
   a valid pointer that the current count excludes. Inspect `FUN_007e4150` to determine
   whether it is a 44th NiNode-specific virtual or padding before the child-list helper
   sub-vtable at `0x00898fdc`.
3. **NiAVObject object size** was previously listed as 0xC4 (medium confidence) derived from
   ctor field writes alone. **Refined 2026-05-28 to 0xC8** via the gamebryo-cross-reference
   v5 validation (doc #7): NiNode 0xE8 minus NiNode-specific 0x20 = 0xC8. The +4 vs the
   earlier ctor-only estimate is accounted for by the helper call FUN_008136c0 at the end of
   NiAVObject ctor. NiGeometry and NiTriBasedGeom sizes (0xE0 and 0xE4) added in the same
   pass; see Object Sizes table above.
4. **Suspected additional RTTI ptr at 0x009a14b8** (from early notes) is not yet classified.
   Possibly an additional core-class RTTI ptr that should be enumerated.
5. **226 of 238 vtable slot entries are pattern-extrapolated** by inheritance. A per-slot
   decompile sweep would promote them all from `confidence: medium` to `confidence: high`.
6. **NiCamera, NiLight, and additional NI vtables in the `0x00898d44+` region** are scope
   questions for a future expansion of this doc. Currently this doc covers only the
   NiObject → NiTriShape chain.

## Methodology

1. **Constructor chain tracing**: Starting from the known NiNode factory (`FUN_007e5450`),
   traced `__fastcall` constructor calls down to NiObject base. Each constructor writes its
   class vtable as `*this = &vtable_addr`.

2. **Vtable boundary detection**: For each vtable address, checked if nearby addresses are
   used as vtable pointers by other constructors (via `get_xrefs_to`). When an address N
   bytes after a vtable start is used as another class's vtable, the first vtable ends
   before that address.

3. **Slot identification**: Decompiled individual vtable entry functions and matched
   behavior to known NiObject virtual method semantics (GetRTTI returns RTTI pointer,
   SaveBinary writes to stream, IsEqual compares RTTI names, etc.).

4. **Cross-class verification**: Confirmed that slot 11 (`0x0040da50`) is identical across
   NiObject, NiObjectNET, NiAVObject, and NiNode (never overridden), while other slots
   differ (overridden at each level).

5. **Two-stage construction detection** (NiTriShape): Observed that the NiTriBasedGeom
   constructor writes vtable `0x00899264`, but the NiTriShape factory's body — after
   returning from the inner ctor — writes vtable `0x00899374` to the same slot. The final
   write is the runtime vtable.

6. **GetRTTI cross-check** (NiTriShape correction): Each GetRTTI stub returns a NiRTTI ptr
   storage address (`mov eax, IMM ; ret` pattern). Cross-checking which game-code addresses
   xref each NiRTTI ptr storage identifies the canonical runtime type. Vtable `0x00899264`
   slot 0 returns `0x009a1af8` (NiTriBasedGeom); vtable `0x00899374` slot 0 returns
   `0x009a1bb8` (NiTriShape, 28 game-code xrefs). The canonical runtime NiTriShape vtable is
   therefore `0x00899374`, not `0x00899264` as the prior doc revision claimed.
