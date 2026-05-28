---
name: netimmerse-vtables-validation-20260528
description: v5 validation of docs/engine/netimmerse-vtables.md — 6 vtable anchors verified, NiTriShape vtable address corrected (canonical is 0x00899374, doc had NiTriBasedGeom's 0x00899264), constructor chain confirmed, 12 slot samples decompiled.
metadata:
  type: project
---

# NetImmerse Vtables Validation — 2026-05-28

Phase 1-3 v5 validation of `docs/engine/netimmerse-vtables.md` (foundation #4 in engine family).

## Top-Level Findings

1. **Constructor chain CONFIRMED.** Every doc-claimed ctor (FUN_007d87a0 → FUN_007dac80 → FUN_007dc0c0 → FUN_007edd10 → FUN_007ef260 + FUN_007e5450 NiNode factory) decompiles cleanly. Each calls its parent then writes its vtable as `*this = &PTR_LAB_XXXXX`. Two-stage pattern confirmed for the factory at FUN_007f31f0: calls FUN_007ef260 (which writes 0x00899264), then OVERWRITES with 0x00899374.

2. **Major correction: NiTriShape vtable address is 0x00899374, not 0x00899264.** The vtable at 0x00899264 is **NiTriBasedGeom** (intermediate ancestor in the `NiGeometry → NiTriBasedGeom → NiTriShape` chain). Evidence:
   - GetRTTI stub at 0x007f1220 (vtable 0x00899264 slot 0) returns `0x009a1af8`. That RTTI ptr is referenced by FUN_007f0db0 which mentions `s_m_pOBBRoot` — characteristic of NiTriBasedGeom.
   - GetRTTI stub at 0x004e7d10 (vtable 0x00899374 slot 0) returns `0x009a1bb8`. That RTTI ptr is referenced by FUN_007f3320 (read after NiAddType call), and has 28 xrefs from the 0x004xxxxx-0x006xxxxx game-code range — the canonical NiTriShape RTTI.
   - The factory FUN_007f31f0 explicitly writes 0x00899374 last; this is the runtime vtable. The 0x00899264 vtable is a transient base-class state observed only during construction.
   - nirtti-factory-catalog.md was right; the netimmerse-vtables.md was wrong.

3. **Inheritance chain order in NI 3.1: NiGeometry → NiTriBasedGeom → NiTriShape.** The doc currently presents it as NiGeometry → NiTriShape, omitting NiTriBasedGeom. rtti-class-catalog.md already lists both NiTriBasedGeom (`0x009787A0`) and NiTriShape (`0x009787EC`) — and the catalog flags NiTriBasedGeom as abstract (RET-stub factory `FUN_007ef0e0`). So the "abstract bases have vtables written by their constructors, not their factories" pattern applies here too: NiTriBasedGeom's factory FUN_007ef0e0 just registers RTTI, but its **constructor** FUN_007ef260 (called by NiTriShape factory) writes vtable 0x00899264.

4. **NiAVObject vtable size (0x9C) vs object size (0xC4)**: no contradiction. 0x9C is the vtable size (39 slots × 4). 0xC4 is the object/instance size from the bottom "Object Sizes" table. The inventory flagged this as a self-disagreement but it's not — they measure different things. The doc could add a clarifying sentence.

5. **NiNode actual slot count: 43**. NiNode vtable boundary verified at 0x00898fdc (= start of an embedded NiTArray vtable). Total NiNode vtable size: 0xB0 = 44 slots × 4. BUT the slot at offset +0xAC (= slot 43) shows `50 41 7E 00` = 0x007e4150, a valid pointer. Then the embedded sub-vtable at 0x00898fdc is for the child-list helper object whose ptr is stored at NiNode field 0x32. Doc's claim of 43 slots is the conservative count that excludes whatever's at offset +0xAC. This is **a 1-slot ambiguity** that would benefit from inspecting FUN_007e4150 (might be a 44th NiNode-specific virtual or might be padding).

6. **__purecall stub at 0x00859a0b CONFIRMED.** Bytes `6A 19 E8 69 13 00 00 59 C3` = `push 0x19 ; call 0x0086ad79 ; pop ecx ; ret`. Standard MSVC. Vast xref count from vtables 0x00898b3c-0x00898f10 confirms.

7. **NiObject RTTI ptr at 0x009a1468 CONFIRMED.** GetRTTI stub at 0x00458770 returns this address. Distinct from the RTTI string at 0x009780D8.

8. **NiObject global counter at 0x009a1478 CONFIRMED.** Direct decompile of FUN_007d87a0 shows `DAT_009a1478 = DAT_009a1478 + 1`. Dtor FUN_007d87f0 decrements.

9. **RTTI factory hash table at 0x009a2b98 CONFIRMED.** Cross-references nirtti-factory-catalog. Every NiRTTI registration factory (FUN_007d8650 for NiObject, FUN_007ef0e0 for NiTriBasedGeom, etc.) uses this as the global hash table.

10. **Slot 11 = 0x0040da50 = `ret` (single byte 0xC3)**. Confirmed across NiObject/NiObjectNET/NiAVObject/NiNode. Doc's "never overridden" claim is correct. The slot is a true no-op placeholder.

## Sampled Slot Verifications (Phase 2.5)

12 slots decompiled and matched to inferred names:

| Vtable | Slot | Func | Expected behavior | Verified |
|--------|------|------|------|------|
| NiObject 0x00898b94 | 0 | 0x00458770 | GetRTTI returns 0x009a1468 | ✓ |
| NiObject 0x00898b94 | 7 | FUN_007d8a40 | SaveBinary calls GetRTTI then writes name | ✓ |
| NiObjectNET 0x00898c48 | 0 | 0x007dba40 | GetRTTI returns 0x009a1500 | ✓ |
| NiObjectNET 0x00898c48 | 4 | FUN_007db5f0 | RegisterStreamables: calls parent, FUN_00818a00, vtable writes | ✓ |
| NiAVObject 0x00898ca8 | 0 | 0x007ddf90 | GetRTTI returns 0x009a1578 | ✓ |
| NiAVObject 0x00898ca8 | 7 | FUN_007dd6a0 | SaveBinary: calls parent, writes ~7 fields | ✓ |
| NiNode 0x00898f2c | 0 | 0x004e3640 | GetRTTI returns 0x009a1870 | ✓ |
| NiNode 0x00898f2c | 39 | FUN_007e39b0 | AttachChild(NiAVObject*, bool atEnd): inserts child + ref | ✓ |
| NiNode 0x00898f2c | 41 | FUN_007e3a30 | DetachChildAt(uint index): bounds-check, nullify, decref | ✓ |
| NiGeometry 0x00899164 | 0 | 0x007eeaa0 | GetRTTI returns 0x009a1a98 | ✓ |
| NiGeometry 0x00899164 | 45 | FUN_007ef050 | NOT just "NiGeometry-specific" — calls FUN_007eecd0 and frees `this` if (param & 1). It's a **scalar deleting dtor**, not an arbitrary virtual. Doc undersells this slot. | ✓ corrected |
| NiTriBasedGeom 0x00899264 (doc misnamed NiTriShape) | 0 | 0x007f1220 | GetRTTI returns 0x009a1af8 (NiTriBasedGeom RTTI) | ✓ |

## NiTriShape Canonical Vtable (0x00899374) — Quick Sketch

Did not exhaustively map. Sketch:
- Slot 0: 0x004e7d10 (GetRTTI returns 0x009a1bb8 = NiTriShape RTTI)
- First 12 slots look like NiObject base overrides
- Slots 12-38: NiAVObject layer
- Slots 39+: NiGeometry → NiTriBasedGeom → NiTriShape additions
- **Anomaly at offset +0x9C (slot 39) and +0xA0 (slot 40)**: bytes `80 96 18 4B` = 0x4B189680 and `60 42 A2 0D` = 0x0DA24260. These are NOT valid code pointers (above EOF). Either inline floats/constants stored unusually in vtable space, or genuine data after vtable end. Boundary heuristic gives ~48 slots (size 0xC0), with new vtable starting at 0x00899434.
- Documentation debt: per-slot map for 0x00899374 is missing from the doc entirely.

## Key Addresses To Remember

| Address | What |
|---------|------|
| 0x00898b94 | NiObject vtable (12 slots, 0x30 bytes) |
| 0x00898c48 | NiObjectNET vtable (12 slots, 0x30 bytes) |
| 0x00898ca8 | NiAVObject vtable (39 slots, 0x9C bytes) |
| 0x00898f2c | NiNode vtable (43 slots verified; possibly 44 — see open Q) |
| 0x00898fdc | NiNode child-list helper sub-vtable (NOT a top-level class vtable) |
| 0x00899164 | NiGeometry vtable (64 slots, 0x100 bytes) |
| 0x00899264 | **NiTriBasedGeom** vtable (68 slots, 0x110 bytes) — doc misnames this NiTriShape |
| 0x00899374 | **NiTriShape** vtable (canonical, ~48 slots) — doc OMITS this |
| 0x0040da50 | Universal no-op slot 11 (`ret`) |
| 0x00859a0b | __purecall stub |
| 0x009a1468 | NiObject NiRTTI ptr storage |
| 0x009a1478 | NiObject global instance counter |
| 0x009a14b8 | (suspected: another RTTI ptr — needs verification) |
| 0x009a1500 | NiObjectNET NiRTTI ptr storage |
| 0x009a1578 | NiAVObject NiRTTI ptr storage |
| 0x009a1870 | NiNode NiRTTI ptr storage |
| 0x009a1a98 | NiGeometry NiRTTI ptr storage |
| 0x009a1af8 | NiTriBasedGeom NiRTTI ptr storage |
| 0x009a1bb8 | NiTriShape NiRTTI ptr storage |
| 0x009a2b98 | RTTI factory hash table head |
| 0x009780D8 | NiObject RTTI **string** "NiObject" (NOT same as ptr storage 0x009a1468) |
| 0x009787A0 | NiTriBasedGeom RTTI string |
| 0x009787EC | NiTriShape RTTI string |
| FUN_00718cb0 | NiAlloc (CORRECT — engine-snapshot's 0x00717840 is wrong) |

## Open Questions / Documentation Debt

- **NiTriShape canonical vtable at 0x00899374 needs full per-slot map.** Currently invisible in the doc.
- **The data anomaly at vtable 0x00899374 offsets +0x9C/+0xA0.** Investigate whether those are inline data or vtable end.
- **NiNode 43 vs 44 slot ambiguity.** Slot at offset +0xAC (= slot 43) is 0x007e4150 — does this complete the doc-described 43 slots (slots 0..42) plus one more, making 44? Or is 0x007e4150 actually slot 43 itself and the doc's "43 slots" means slots 0-42 = 43 entries? Re-count needed.
- **NiGeometry slot 45 (FUN_007ef050) is a scalar deleting dtor**, not an arbitrary "NiGeometry-specific" slot. Doc's evidence column undersells this.
- **NiAVObject as abstract base**: no factory means no direct allocation size measured. Doc's 0xC4 object size is unverified — would need a derived class that doesn't add fields beyond NiAVObject, or careful inspection of FUN_007dc0c0 field-write offsets (the ctor writes up to offset 0xBC = field 0x2f).

## Method Notes for Future Validators

- Two-program Ghidra: ALWAYS pass `program: "STBC.exe"` explicitly. SGW.exe is currently active.
- Vtable-boundary heuristic: read 200+ bytes, scan for first non-pointer value (above 0x008xxxxx EOF or above-EOF garbage). Cross-check with `get_xrefs_to(suspected_next_vtable_addr)` — if it has DATA xrefs from a constructor, it's a real vtable boundary.
- GetRTTI stubs: `B8 XX XX XX 00 C3` pattern (`mov eax, 0x00XXXXXX ; ret`). The address XX is the RTTI ptr storage, NOT the RTTI string. Easy to confuse them.
- The two-stage construction pattern (intermediate ctor writes vtable A, then factory overwrites with vtable B) is real in NI 3.1. Don't assume the first vtable a ctor writes is the runtime vtable — check the call chain.
- Inline `ret` stubs (single 0xC3 byte) are no-op virtuals. Common across NetImmerse — slot 11 is one example.
- Abstract base classes (per nirtti-factory-catalog: NiObject, NiObjectNET, NiAVObject, NiGeometry, NiTriBasedGeom, etc.) DO have vtables — they're just written by their constructors when a derived class is being built, not by their own factories (which are RET-stubs that only register RTTI).
