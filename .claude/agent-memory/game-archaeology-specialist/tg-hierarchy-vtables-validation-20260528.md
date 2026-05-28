---
name: tg-hierarchy-vtables-validation-20260528
description: v5 validation of docs/engine/tg-hierarchy-vtables.md — 9-vtable Ship inheritance chain end-to-end confirmed via ctor decompiles; TGObject vtable 0x00896278 correction verified (0x008963BC has ZERO xrefs); universal slot-1 GetTypeID pattern catalog extended; doc upgrades for "NULL stub" → __purecall and "TGHashTable or similar" → "orphan .rdata data".
metadata:
  type: project
---

# TG Hierarchy Vtables Validation — 2026-05-28

Phase 1-3 v5 validation of `docs/engine/tg-hierarchy-vtables.md` (foundation #6 in engine family). Same playbook as [[netimmerse-vtables-validation-20260528]]: vtable inspection + ctor decompile + boundary check + sample slot decompile + universal pattern verification.

## Top-Level Findings

1. **Inheritance chain CONFIRMED end-to-end via 8 constructor decompiles.** Each ctor calls its parent then writes its vtable as `*this = &PTR_FUN_<vtable>`. Chain steps:
   - TGObject ctor 0x006f0a70 writes 0x00896278
   - TGStreamedObject ctor 0x006f31a0 calls TGObject, writes 0x008962F4
   - TGStreamedObjectEx ctor 0x006f2590 calls TGStreamedObject, writes 0x008962A8
   - TGEventHandlerObject ctor 0x006d8f90 calls TGStreamedObjectEx, writes 0x00896044
   - TGSceneObject ctor 0x004308e0 calls TGEventHandlerObject (FUN_006d8f90), writes 0x00889708
   - ObjectClass ctor 0x00435030 calls TGSceneObject, writes 0x00889950
   - PhysicsObjectClass ctor (FUN_0059fd60 / FUN_0059ff50 — dtor at 0x005a0200 writes 0x00894128) chain confirmed via xref
   - DamageableObject ctor 0x00591200 calls PhysicsObjectClass (FUN_0059ff50), writes 0x00893D88
   - Ship ctor 0x005abdc0 calls DamageableObject (FUN_00591410), writes 0x00894340
   - Locked at high confidence.

2. **TGObject vtable correction 0x008963BC → 0x00896278 holds.** 0x008963BC has **ZERO xrefs**; no constructor writes that address. The doc's negative claim ("NOT TGObject's vtable") is correct. The speculative positive claim ("TGHashTable or similar") is **wrong** — there's no class vtable at that address. It's orphan `.rdata` data (probably partial-overlay of a different vtable layout). Tightening the doc text to "orphan .rdata data with no observed runtime use" is recommended.

3. **TGObject vtable full 12-slot map CONFIRMED.** Every slot inspected:
   - Slot 0 (0x006f0b70 scalar_deleting_dtor): MSVC `if (param & 1) FUN_00717b20(8) ; FUN_00718180(this)` ✓
   - Slot 1 (0x006f0b60 GetTypeID): `B8 02 00 00 00 C3` = `mov eax, 2 ; ret` ✓ — returns TGObject type-ID constant 2
   - Slot 2 (0x00518ab0 IsTypeID): `return param_1 == 2` ✓
   - Slot 3 (0x006f1650 DebugPrint): calls FUN_006f1680 (formatter) + FUN_006f14e0 (printer) ✓
   - Slot 4 (0x006f0bc0 WriteToStream): formats "ID:%d Saving:%s [%d] number=%d" using GetTypeID + GetClassName via vtable, then writes via stream vtable+0x64 / +0x84 ✓
   - Slots 5/6/7 (0x00859a0b): **__purecall stub**, NOT "NULL stub" as doc says. Bytes `6A 19 E8 69 13 00 00 59 C3` = `push 0x19 ; call __purecall_thunk ; pop ecx ; ret`. Same stub identified in [[netimmerse-vtables-validation-20260528]]. Doc text correction needed.
   - Slot 8 (0x006f15c0 InvokePythonHandler): looks up Python handler via DAT_008d8af0 dict using class name from vtable+0x2C, dispatches ✓
   - Slot 9 (0x006f1540 GetClassName): `mov eax, 0x0095B05C ; ret` — 0x0095B05C contains string **"TGObject"** ✓
   - Slot 10 (0x006f1550 GetSwigTypeName): `mov eax, 0x009142B0 ; ret` — string **"_p_TGObject"** ✓
   - Slot 11 (0x006f1560 GetObjectPtrTypeName): `mov eax, 0x0095B270 ; ret` — string **"TGObjectPtr"** ✓

4. **Universal TG-class slot-1 GetTypeID pattern extended.** Sampled three additional classes; each implements GetTypeID as 6-byte `mov eax, IMM ; ret` returning a class-identifier constant:
   - TGObject (0x006f0b60) → **0x02**
   - TGStreamedObject (0x006f31c0) → **0x03**
   - TGEventHandlerObject (0x006d8fb0) → **0x0102** (event-domain ID)
   - TGSceneObject (0x00430950) → **0x8002** (game-domain ID)
   This is stronger evidence than the doc currently captures for the "universal pattern" claim. Each class has its own type-ID constant baked into the GetTypeID stub.

5. **Universal slot-0 scalar_deleting_dtor pattern.** Sampled three classes; first 16 bytes always start with `56 8B F1 E8 ?? 00 00 00 F6 44 24 08 01 74 14 56`:
   - TGStreamedObject (0x006f3240): ✓
   - TGEventHandlerObject (0x006d9030): ✓
   - TGSceneObject (0x004309e0): ✓
   - MSVC canonical pattern: `push esi ; mov esi, ecx ; call <dtor body> ; test [esp+8], 1 ; jz +0x14 ; push esi`

6. **Ship vtable size 92 slots / 0x16C bytes CONFIRMED.** Boundary at 0x008944AC. Following 6 dwords are float constants (75.0, 50.0, 500.0, 900.0, 0.8, 0.0049) — Ship class data living adjacent to vtable. Ship does NOT add slots beyond DamageableObject's 92.

7. **Universal inherited slots across all 9 vtables:**
   - Slot 3 (DebugPrint @ 0x006f1650): all 9 vtables show byte sequence `50 16 6F 00` at offset +0x0C ✓
   - Slot 8 (InvokePythonHandler @ 0x006f15c0): all 9 vtables show `C0 15 6F 00` at offset +0x20 ✓
   - Slots 12-15 (TGStreamedObject chain methods): present in TGStreamedObject through Ship — confirms inheritance ordering
   - Slots 16-18 (TGStreamedObjectEx slots): present in TGStreamedObjectEx through Ship

## Sampled Slot Verifications

| Vtable | Slot | Func | Verified |
|--------|------|------|----------|
| TGObject 0x00896278 | 0 | 0x006f0b70 scalar_deleting_dtor | ✓ MSVC pattern |
| TGObject 0x00896278 | 1 | 0x006f0b60 GetTypeID = 2 | ✓ mov eax,2;ret |
| TGObject 0x00896278 | 2 | 0x00518ab0 IsTypeID | ✓ return p==2 |
| TGObject 0x00896278 | 3 | 0x006f1650 DebugPrint | ✓ formatter+printer |
| TGObject 0x00896278 | 4 | 0x006f0bc0 WriteToStream | ✓ ID/name format |
| TGObject 0x00896278 | 8 | 0x006f15c0 InvokePythonHandler | ✓ dict lookup |
| TGObject 0x00896278 | 9 | 0x006f1540 GetClassName | ✓ "TGObject" |
| TGObject 0x00896278 | 10 | 0x006f1550 GetSwigTypeName | ✓ "_p_TGObject" |
| TGObject 0x00896278 | 11 | 0x006f1560 GetObjectPtrTypeName | ✓ "TGObjectPtr" |
| TGStreamedObject 0x008962F4 | 0 | 0x006f3240 scalar_deleting_dtor | ✓ MSVC pattern |
| TGStreamedObject 0x008962F4 | 1 | 0x006f31c0 GetTypeID = 3 | ✓ mov eax,3;ret |
| TGStreamedObject 0x008962F4 | 12 | 0x006f2750 WriteToStreamChain | ✓ chain dispatch |
| TGStreamedObject 0x008962F4 | 14 | 0x006f3400 AddEventHandler | ✓ alloc+dispatch |
| TGEventHandlerObject 0x00896044 | 0 | 0x006d9030 scalar_deleting_dtor | ✓ MSVC pattern |
| TGEventHandlerObject 0x00896044 | 1 | 0x006d8fb0 GetTypeID = 0x102 | ✓ mov eax,0x102;ret |
| TGEventHandlerObject 0x00896044 | 20 | 0x006d9240 HandleEvent | ✓ event dispatch |
| TGSceneObject 0x00889708 | 0 | 0x004309e0 scalar_deleting_dtor | ✓ MSVC pattern |
| TGSceneObject 0x00889708 | 1 | 0x00430950 GetTypeID = 0x8002 | ✓ mov eax,0x8002;ret |
| Ship 0x00894340 | 72 | 0x005b17f0 Ship__WriteStateUpdate | ✓ StateUpdate pipeline |
| Ship 0x00894340 | 85 | 0x005b0060 Ship__CollisionDamageWrapper | ✓ FUN_005afd70 + FUN_00593650 (DamageableObject) |
| Ship 0x00894340 | 91 (boundary) | 0x005abf30 array_dtor + 6 floats follow | ✓ boundary locked |

## Key Addresses To Remember

| Address | What |
|---------|------|
| 0x00896278 | TGObject vtable (12 slots, 0x30 bytes) — runtime |
| 0x008963BC | NOT a vtable — ZERO xrefs, orphan .rdata |
| 0x008962F4 | TGStreamedObject vtable |
| 0x008962A8 | TGStreamedObjectEx vtable (lives BEFORE TGStreamedObject in memory) |
| 0x00896044 | TGEventHandlerObject vtable |
| 0x00889708 | TGSceneObject vtable |
| 0x00889950 | ObjectClass vtable |
| 0x00894128 | PhysicsObjectClass vtable |
| 0x00893D88 | DamageableObject vtable (92 slots, 0x16C bytes) |
| 0x00894340 | Ship vtable (92 slots, 0x16C bytes) — same slot count as DO |
| 0x008944AC | Ship vtable boundary (6 floats follow before next vtable) |
| 0x008958D0 | TGBufferStream vtable (sibling, see [[tgbufferstream-vtable-20260528]]) |
| 0x0088b7ec | TGDimmerController vtable (sibling, NiRTTI-registered, NOT in Ship chain) |
| 0x006f0a70 | TGObject ctor |
| 0x006f31a0 | TGStreamedObject ctor |
| 0x006f2590 | TGStreamedObjectEx ctor |
| 0x006d8f90 | TGEventHandlerObject ctor |
| 0x004308e0 | TGSceneObject ctor |
| 0x00435030 | ObjectClass ctor |
| 0x00591200 | DamageableObject ctor |
| 0x005abdc0 | Ship ctor |
| 0x0095B05C | string "TGObject" (returned by GetClassName slot 9) |
| 0x009142B0 | string "_p_TGObject" (returned by GetSwigTypeName slot 10) |
| 0x0095B270 | string "TGObjectPtr" (returned by GetObjectPtrTypeName slot 11) |
| 0x00859a0b | __purecall stub (NOT "NULL stub") |

## Class Type-ID Constants (Slot 1 GetTypeID Returns)

| Class | Type ID | GetTypeID Addr |
|-------|---------|----------------|
| TGObject | 0x02 | 0x006f0b60 |
| TGStreamedObject | 0x03 | 0x006f31c0 |
| TGEventHandlerObject | 0x0102 | 0x006d8fb0 |
| TGSceneObject | 0x8002 | 0x00430950 |

These constants form a TG class identifier numbering scheme. Bit pattern suggests bit 15 = "game-domain class", bit 8 = "event-handler-derived". Worth follow-up; cross-link to [[dispatcher-recovery-20260528]] which observed similar tag constants on the wire.

## Confirmed Doc Claims (Phase 2 results)

| Claim | Status |
|-------|--------|
| 9-vtable inheritance chain (TGObject through Ship) | CONFIRMED via 8 ctor decompiles |
| TGObject vtable at 0x00896278 | CONFIRMED — both xrefs point to it from ctor+dtor |
| 0x008963BC is NOT TGObject | CONFIRMED — zero xrefs |
| TGObject 12-slot layout | CONFIRMED — all 12 slots match doc |
| Slot 1 = GetTypeID returning class constant | CONFIRMED across 4 classes |
| Slot 0 = scalar_deleting_dtor (MSVC pattern) | CONFIRMED across 4 classes |
| Slot 3 = DebugPrint, universal across hierarchy | CONFIRMED |
| Slot 8 = InvokePythonHandler, universal | CONFIRMED |
| Ship has 92 slots, same as DamageableObject | CONFIRMED at boundary 0x008944AC |
| Ship vtable 0x00894340 | CONFIRMED |
| Slot 72 = Ship__WriteStateUpdate at 0x005b17f0 | CONFIRMED (state-update pipeline) |
| Slot 85 = Ship__CollisionDamageWrapper at 0x005b0060 | CONFIRMED (delegates to FUN_005afd70 + FUN_00593650) |
| GetClassName/SwigTypeName/ObjPtrTypeName strings | CONFIRMED ("TGObject", "_p_TGObject", "TGObjectPtr") |
| Ship does NOT inherit from NiObject | CONFIRMED — separate inheritance ladder |

## Corrected Doc Claims

| Old Claim | Correction |
|-----------|------------|
| Slots 5/6/7 = "NULL stub 0x00859a0b" | NOT a NULL stub — MSVC __purecall stub (matches [[netimmerse-vtables-validation-20260528]] finding) |
| 0x008963BC is "TGHashTable or similar" | 0x008963BC is orphan .rdata data with ZERO xrefs; not a class vtable |
| (impl) Slot 12 0x006f2750 named "WriteToStreamChain" | Confirmed as chained-write dispatch — calls FUN_006f33a0 first, then chains to child via vtable+0x30 |
| (impl) Slot 13 0x006f2790 "Unknown" | Could be locked via decompile in a follow-up pass |
| (impl) Slot 14 0x006f3400 "AddEventHandler" | CONFIRMED — allocates 0x14 (20 bytes) for handler entry, dispatches FUN_006f6830 |

## Open Questions / Documentation Debt

1. **Slot 1 GetTypeID class-ID numbering scheme.** Constants 0x02 / 0x03 / 0x0102 / 0x8002 suggest a structured tag scheme (low byte = sub-class, high byte = domain). Worth cross-classifying against the dispatcher's wire-format class IDs and [[tgbufferstream-vtable-20260528]]'s 0x32 stream-type tag. Likely an enumeration.
2. **0x008963BC's actual purpose.** Zero xrefs in the binary but the byte sequence at +0x10 (0x006f2810 = TGStreamedObjectEx PostDeserialize per the live TGStreamedObjectEx vtable) is suspicious. Could be unused linker artifact (overlapping function-table) or a dead-code class that survived in `.rdata`. Worth a follow-up examination but not blocking.
3. **TGEventHandlerObject vtable slot count.** Doc has slots 16-22 sampled but slots 23-39 (up to size of TGSceneObject) are "varies". Per-slot decompile sweep could lock these.
4. **TGSceneObject "slots 27-47" gap (+0x6C through +0xBC).** Doc says "Scene object management slots". Decompile sweep would name them.
5. **Ship slots 9-11, 16-18, 36-47** marked "(unknown)" or "(stub)" in doc. Decompile sweep could name them.
6. **Ship slot 22 doc inconsistency** — doc says slot 22 (+0x58) = 0x00430d30 "AttachDefaultProperty" but ALSO marks "TGSceneObject__SetScene" in slot 24. The pattern is correct (TGSceneObject's slot 22 = AttachDefaultProperty, slot 24 = SetScene; Ship overrides slot 24 to 0x005b35a0 = Ship__SetScene). The doc captures this correctly but verifying slot 22 = 0x00430d30 decompile would confirm it calls NiAVObject::AttachProperty as claimed.

## Method Notes for Future Validators

- **Two-program Ghidra**: ALWAYS pass `program: "STBC.exe"` explicitly. SGW.exe is currently the active program.
- **Vtable inspection-only approach works** for most pattern verification (read 64-128 bytes at vtable address, slot-decode by index, then decompile only the load-bearing slots).
- **The MSVC scalar-deleting-destructor signature** `56 8B F1 E8 ?? 00 00 00 F6 44 24 08 01 74 14 56` is highly recognizable as raw bytes — useful for boundary detection and class-pattern discovery.
- **The `mov eax, IMM ; ret` (6-byte) GetTypeID stub** is the most reliable way to identify a TG class's type-ID constant. The constants form a meaningful scheme worth cataloging.
- **__purecall stub at 0x00859a0b** appears in BOTH NI and TG hierarchies (for abstract methods or removed slots). Easy to confuse with "NULL stub" because Ghidra doesn't always recognize the call target.
- **Xref check (`get_xrefs_to`)** is the cheapest false-vtable detector. A vtable with zero xrefs is not an instantiated class.
- **Ship vtable size = 92 slots (0x16C bytes)** is verified by both (a) boundary scan: floats appear after slot 91; (b) DamageableObject's documented slot count matches Ship's. Ship truly does NOT add slots beyond its parent's 92.

## Cross-References

- [[netimmerse-vtables-validation-20260528]] — sister doc validation; same playbook; identified the __purecall stub
- [[tgbufferstream-vtable-20260528]] — TGBufferStream vtable 0x008958D0; sibling TG class not in Ship chain; vtable[0]() = 0x32 stream-tag
- [[nirtti-factory-validation-20260528]] — TGDimmerController vtable 0x0088b7ec; sibling TG class with NiRTTI registration
- [[dispatcher-recovery-20260528]] — wire-format class tags that may align with the slot-1 GetTypeID scheme
- docs/engine/netimmerse-vtables.md (verified 2026-05-28) — Ship's parallel NI hierarchy
- docs/engine/rtti-class-catalog.md (partial 2026-05-28) — 28 confirmed TG bare-string addresses including TGObject 0x0095b05c
- docs/protocol/stateupdate.md — Ship slot 72 WriteStateUpdate is the per-tick state-sync pipeline; this validation confirms its slot+address
- docs/gameplay/damage-system.md — Ship slot 85 CollisionDamageWrapper is in the collision damage path
