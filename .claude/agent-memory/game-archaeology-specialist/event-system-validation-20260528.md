---
name: event-system-validation-20260528
description: v5 validation of event-system-architecture.md — TGCallback/TGConditionHandler/TGInstanceHandlerTable/TGEvent vtables + sizes verified; TGEvent factory-ID 0x02 claim CORRECTED (it's TGObject's tag, TGEvent uses string-pointer RTTI); InstanceHandlerTable is lazy-allocated 2-level indirection
metadata:
  type: project
---

# Event System Architecture Validation — 2026-05-28 (Doc #8)

Per-doc v5 validation of `docs/engine/event-system-architecture.md` (Phase 8C, 2026-02-24 pre-v5). Status: **partial** — vtable + struct sizes solid, but TGEvent type-ID claim is wrong and several method-name claims unanchored.

## Anchored vtables and struct sizes (high confidence)

| Class | Vtable | Size | Anchor |
|------|--------|------|--------|
| TGEvent | 0x00896018 | **0x28** bytes | SWIG `new_TGEvent` at 0x005c5e66: `PUSH 0x28` |
| TGEventHandlerObject | 0x00896044 | (at least 0x14 inc. +0x10 InstanceHandlerTable slot) | ctor FUN_006d8f90: `*p=vtable; p[4]=0` |
| TGCallback | **0x008960f4** | **0x14** bytes (5 fields) | ctor FUN_006e09e0 writes 5 dwords |
| TGConditionHandler | **0x00896104** | variable (two embedded 6-dword sub-structs + 1 reentrant flag) | ctor FUN_006e1870 writes vtable twice (broadcast + per-object) |
| TGInstanceHandlerTable | 0x00896030 | 0x14 bytes; 0x94-byte bucket array at +0x0C | init FUN_006d7b30: `p[2]=0x25; p[3]=alloc(0x94)` |

## TGCallback layout (CONFIRMED EXACTLY)
- +0x00: vtable (0x008960f4)
- +0x04: flags (bit0=isMethod, bit1=isPython, bit2=active, bit3=pendingDelete) [bit semantics from doc, not separately re-verified]
- +0x08: next pointer
- +0x0C: sentinel cookie (initial value = DAT_0095adf8)
- +0x10: function pointer OR Python "module.function" string pointer

Ctor at FUN_006e09e0 writes all 5 fields explicitly. Vtable has 4 slots; slot 3 (FUN_006e0c10) is the sentinel-field accessor.

## TGConditionHandler layout — DUAL EMBEDDED ARRAYS
Ctor FUN_006e1870 writes the SAME vtable at BOTH param_1[0] AND param_1[6]. This is the "two sorted arrays" architecture:
- +0x00 broadcast sub-struct (6 dwords): vtable, base_ptr (alloc 8 bytes initial), capacity=2, count=0, growth, total=4
- +0x18 per-object sub-struct (6 dwords): vtable, base_ptr (alloc 4 bytes), capacity=1, count=0, growth, total=1
- +0x30 (param_1[0xc]): reentrant "currently dispatching" flag (init 0)

Total struct size ~0x34 bytes for the container.

## TGEvent factory-ID CORRECTION
**Doc says "factory ID 0x02" — WRONG.** Per tg-hierarchy-vtables foundation, 0x02 is TGObject's slot-1 GetTypeID return value. TGEvent's slot-1 at FUN_006d5d20 returns a STRING pointer (`0x0091427c` = "_p_TGEvent"), not an integer. TGEvent uses a different RTTI mechanism than the TGObject→TGStreamedObject→TGEventHandlerObject integer-tag chain.

**Open question:** what IS TGEvent's actual type tag? Probably a separate enum or the string-pointer is itself the identity.

## TGInstanceHandlerTable refinement
- TGEventHandlerObject+0x10 stores a POINTER (lazy, init NULL)
- The 0x14-byte InstanceHandlerTable struct is allocated on demand via TGEventHandlerObject vtable slot 5 (FUN_006d9160)
- 37-bucket hash array is allocated SEPARATELY at struct+0x0C as 0x94 bytes
- So the "37-bucket hash at +0x10" claim is correct in spirit but has TWO levels of pointer indirection, not flat embedding

## Event IDs verified by xref
- 0x008000E0 SetPhaserLevel — xrefs at 0x00573e82, 0x0069e9c4 (MP dispatcher)
- 0x008000E3 StartCloak — heavy cluster in 0x008631xx (cloak handler region)
- 0x00800058 TARGET_WAS_CHANGED — xrefs at 0x004fe62b, 0x00537d3e
- 0x00030001 / 0x00040001 input events — multiple UI region xrefs

Combat IDs from dispatcher-recovery memory all anchored at code addresses (confirmed cross-source).

## TGEventManager singleton
- Global pointer at **0x00991438** (zero in on-disk image, populated at boot)
- Found via SWIG `TGEventManager_AddEvent` wrapper at 0x005c8be9: `MOV EAX, [0x00991438]`

## Python dispatch path
- TGEventHandlerObject vtable slot 8 (offset +0x20) = `FUN_006f15c0` (InvokePythonHandler)
- Universal slot across all TGEventHandlerObject subclasses (100+ data xrefs)
- Imports module via FUN_0074d280 against module registry at 0x008d8af0 ("ScriptObject")
- Separate Python-flavored TGCallback subclasses exist (e.g., vtable 0x008961ac at ctor FUN_006ec6f0)

## Dropped (unverifiable) claims
- "SaveBroadcastHandlers", "LoadBroadcastHandlers" method names — strings absent
- "FixupReferences" / "FixupComplete" — strings absent (two-phase load pattern plausible but unnamed)
- "TGConditionHandler::AddEntry/InsertSorted/FindFirstByKey/RemoveByName/RemoveAllForObject" — no string anchors
- "TGEventHandlerTable::RegisterObject/FindHandlerChain/DispatchToNextHandler" — only RemoveAllBroadcastHandlersForObject has a SWIG anchor

## Anchored SWIG API for TGEvent system
From string table (anchored):
- TGEventManager: AddEvent, RemoveAllBroadcastHandlersForObject, RemoveBroadcastHandler, AddBroadcastPythonMethodHandler, AddBroadcastPythonFuncHandler
- TGEventHandlerObject: AddPythonMethodHandlerForInstance, AddPythonFuncHandlerForInstance, RemoveHandlerForInstance, RemoveAllInstanceHandlers, CallNextHandler, ProcessEvent
- TGEvent: GetEventType, SetEventType, GetSource, SetSource, GetDestination, SetDestination, Copy, Duplicate, GetTimestamp/SetTimestamp, GetRefCount/Inc/Dec, IsLogged/SetLogged, IsPrivate/SetPrivate, IsNotSaved/SetNotSaved
- TGObjPtrEvent: GetObjPtr/SetObjPtr (event subclass for object pointer payload)

## Lessons learned
1. **Pre-v5 docs name methods without anchoring** — when reading the doc, "Save/Load/Fixup" names that don't show in `search_strings` are inferred from behavior, not extracted.
2. **Type-tag scheme is NOT universal** — TGEvent uses string-pointer RTTI (slot 1 returns &"_p_TGEvent"), TGEventHandlerObject uses integer tag (slot 1 returns 0x0102). Two RTTI systems coexist.
3. **Hash tables in this codebase are 2-level indirection** — the "hash table at +X" claim almost always means a pointer to a struct containing the bucket array. See TGInstanceHandlerTable (lazy alloc) and NiRTTI factory tables (same pattern from earlier work).
4. **Vtable adjacency reveals class hierarchies** — TGCallback (0x008960f4) and TGConditionHandler (0x00896104) are 0x10 apart, TGEvent (0x00896018) and TGEventHandlerObject (0x00896044) are 0x2C apart. All cluster in the 0x008960xx region (event subsystem zone).
5. **SWIG wrapper allocator paths give struct sizes for free** — `new_X` SWIG wrappers always end in `PUSH <size>; CALL alloc` before the ctor call. Excellent size anchor when there's no other named ctor.

## Cross-doc consistency
- ✓ Confirms tg-hierarchy TGEventHandlerObject slot 8 = FUN_006f15c0 (InvokePythonHandler universal)
- ✓ Confirms tg-hierarchy TGEventHandlerObject slot 1 = GetTypeID returns 0x0102 (FUN_006d8fb0: MOV EAX,0x102; RET)
- ✗ Conflicts: doc's "TGEvent factory ID 0x02" reuses TGObject's tag — likely confusion in original doc author
