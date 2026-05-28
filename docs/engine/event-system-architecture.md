> [docs](../README.md) / [engine](README.md) / event-system-architecture.md

---
title: Event System Architecture
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
  - claim: "TGEvent vtable at 0x00896018, struct size 0x28 bytes"
    address: 0x00896018
    function: FUN_006d5d20
    confidence: high
    note: "Size anchored by SWIG `new_TGEvent` at 0x005c5e66: `PUSH 0x28 ; CALL alloc` precedes the ctor. Vtable slot 1 (FUN_006d5d20) returns ptr to '_p_TGEvent' string at 0x0091427c."
  - claim: "TGEventHandlerObject vtable at 0x00896044"
    address: 0x00896044
    function: FUN_006d8f90
    confidence: high
    note: "Ctor FUN_006d8f90 writes `*p = &PTR_0x00896044; p[4] = 0` (lazy InstanceHandlerTable slot at +0x10 initialized NULL). Cross-confirmed in tg-hierarchy-vtables.md as the canonical TGEventHandlerObject vtable in the Ship inheritance chain."
  - claim: "TGCallback vtable at 0x008960f4, struct size 0x14 bytes (5 fields)"
    address: 0x008960f4
    function: FUN_006e09e0
    confidence: high
    note: "Ctor FUN_006e09e0 writes 5 dwords explicitly (vtable, flags, next, sentinel, fn-or-string-ptr). Vtable has 4 slots; slot 3 (FUN_006e0c10) is the sentinel-field accessor."
  - claim: "TGCallback layout: +0x00 vtable / +0x04 flags / +0x08 next / +0x0C sentinel / +0x10 fn-or-string-ptr"
    address: 0x008960f4
    function: FUN_006e09e0
    confidence: high
    note: "All 5 field offsets verified by the ctor body. Sentinel cookie initial value = DAT_0095adf8. Bit semantics for the flags field (bit0=isMethod, bit1=isPython, bit2=active, bit3=pendingDelete) carried from prior doc; not separately re-anchored this pass."
  - claim: "TGConditionHandler vtable at 0x00896104, container size ~0x34 bytes (dual embedded sub-structs)"
    address: 0x00896104
    function: FUN_006e1870
    confidence: high
    note: "Ctor FUN_006e1870 writes the SAME vtable at BOTH param_1[0] AND param_1[6]. Two 6-dword sub-structs (broadcast at +0x00, per-object at +0x18) plus the reentrant flag at +0x30."
  - claim: "TGConditionHandler reentrant 'currently dispatching' flag at +0x30 (param_1[0xc])"
    address: 0x00896104
    function: FUN_006e1870
    confidence: high
    note: "Initialized to 0 by the ctor. The flag gates the deferred add/remove behaviour during dispatch — the architectural property the doc has always claimed, now anchored to a specific field."
  - claim: "TGInstanceHandlerTable vtable at 0x00896030, struct size 0x14 bytes with a 0x94-byte bucket array at +0x0C"
    address: 0x00896030
    function: FUN_006d7b30
    confidence: high
    note: "Init FUN_006d7b30 sets `p[2] = 0x25` (bucket count = 37) and `p[3] = alloc(0x94)`. Two-level pointer indirection: TGEventHandlerObject+0x10 holds a pointer to this struct; the struct holds a pointer to the bucket array."
  - claim: "TGInstanceHandlerTable lives at TGEventHandlerObject+0x10 — LAZY pointer, init NULL"
    address: 0x00896044
    function: FUN_006d8f90
    confidence: high
    note: "TGEventHandlerObject ctor FUN_006d8f90 writes 0 to the +0x10 slot. The struct is allocated on demand via TGEventHandlerObject vtable slot 5 (FUN_006d9160). Not a flat embedding."
  - claim: "TGEventManager singleton pointer at global 0x00991438"
    address: 0x00991438
    function: null
    confidence: high
    note: "Zero in the on-disk image; populated at boot. Found via SWIG wrapper `TGEventManager_AddEvent` at 0x005c8be9, which begins `MOV EAX, [0x00991438]` before invoking the AddEvent method on the dereferenced singleton."
  - claim: "Python dispatch path: TGEventHandlerObject vtable slot 8 (offset +0x20) = FUN_006f15c0 (InvokePythonHandler)"
    address: 0x006f15c0
    function: FUN_006f15c0
    confidence: high
    note: "Universal slot across all TGEventHandlerObject subclasses — 100+ data xrefs. Cross-confirmed in tg-hierarchy-vtables.md (slot 8 inherited unchanged across all 9 vtables in the Ship hierarchy chain). Imports module via FUN_0074d280 against module registry at 0x008d8af0 ('ScriptObject')."
  - claim: "Python-flavored TGCallback subclass vtable at 0x008961ac"
    address: 0x008961ac
    function: FUN_006ec6f0
    confidence: medium
    note: "Ctor FUN_006ec6f0 writes this vtable. Separate from the C++-flavoured TGCallback at 0x008960f4 — runtime distinguishes the two by vtable identity rather than the isPython flag bit alone. Per-slot behaviour not separately decompiled this pass."
  - claim: "Event ID 0x008000E0 = SetPhaserLevel"
    address: 0x00573e82
    function: null
    confidence: high
    note: "Constant xrefs at 0x00573e82 and 0x0069e9c4 (MP dispatcher). See also docs/protocol/set-phaser-level-protocol.md for the wire-format side."
  - claim: "Event ID 0x008000E3 = StartCloak"
    address: null
    function: null
    confidence: high
    note: "Heavy xref cluster in the 0x008631xx cloak handler region (range citation, not a single address — full per-address catalog deferred to docs/gameplay/cloaking-state-machine.md). Companion: docs/gameplay/cloaking-state-machine.md."
  - claim: "Event ID 0x00800058 = TARGET_WAS_CHANGED"
    address: 0x004fe62b
    function: null
    confidence: high
    note: "Constant xrefs at 0x004fe62b and 0x00537d3e. Cross-anchored in docs/gameplay/ship-navigation.md."
  - claim: "Event IDs 0x00030001 / 0x00040001 = input events (mouse/keyboard/gamepad/control)"
    address: null
    function: null
    confidence: high
    note: "Multiple UI region xrefs distributed across the 0x0046-0x004B UI-framework address range (per function-map.md). Specific anchor addresses cataloged in docs/engine/ui-class-hierarchy.md."
  - claim: "TGEvent uses string-pointer RTTI (vtable slot 1 returns ptr to '_p_TGEvent' at 0x0091427c)"
    address: 0x006d5d20
    function: FUN_006d5d20
    confidence: high
    note: "TGEvent slot 1 returns a string-pointer constant, NOT an integer tag. Distinct from the TGObject→TGStreamedObject→TGEventHandlerObject chain (integer-tag RTTI: 0x02 / 0x03 / 0x0102). Two RTTI systems coexist in the TG hierarchy."
  - claim: "Pre-v5 'TGEvent factory ID 0x02' claim is wrong — 0x02 is TGObject's GetTypeID return value"
    address: null
    function: null
    confidence: high
    note: "Per tg-hierarchy-vtables.md, TGObject vtable 0x00896278 slot 1 returns 0x02 via `mov eax, 2 ; ret` (bytes B8 02 00 00 00 C3). TGEvent is not TGObject and does not share the integer tag. The prior doc confused the two."
companions:
  - docs/engine/tg-hierarchy-vtables.md
  - docs/engine/netimmerse-vtables.md
  - docs/engine/function-map.md
  - docs/protocol/python-messages.md
  - docs/engine/v5-validation-status.md
supersedes:
  - 2026-02-24
---

> [!NOTE]
> This doc is `status: partial`. The vtable addresses, struct sizes, layout fields, event ID ranges, and TGEventManager singleton address are v5-validated against the current Ghidra import (2026-05-28). The TGEvent factory-ID 0x02 claim from the prior revision was corrected — 0x02 is TGObject's Type-ID, not TGEvent's (which uses string-pointer RTTI). Several pre-v5 method-name claims (`SaveBroadcastHandlers`, `LoadBroadcastHandlers`, `FixupReferences`, `FixupComplete`, the `TGConditionHandler::AddEntry/InsertSorted/FindFirstByKey/RemoveByName/RemoveAllForObject` family, and the `TGEventHandlerTable::RegisterObject/FindHandlerChain/DispatchToNextHandler` family) were dropped because they had no string anchor in the binary. The anchored SWIG API names are listed in their place where applicable. See [docs/guides/v5-evidence-header.md](../guides/v5-evidence-header.md) for the standard.

# Event System Architecture

Reverse-engineered from `stbc.exe` event dispatch infrastructure. The event system is the backbone of all game logic: every game object registers handlers for event types, and the TGEventManager dispatches events through chained handler structures. This doc covers the singleton, the dispatch path, the per-class layouts, the Python bridge, and the event-ID space.

## Overview

```
TGEventManager (singleton at 0x00991438)
  |
  +-- Global broadcast handler infrastructure
  |     |
  |     +-- TGConditionHandler (dual sorted arrays per event type)
  |           |
  |           +-- TGCallback (wrapper: C++ fn ptr OR Python "module.function" string)
  |
  +-- Event queue (deferred dispatch during game-loop tick)
  |
  +-- TGEvent (event object: type tag, source, destination, type-specific data)

TGEventHandlerObject (per-instance, every UI/scene class)
  |
  +-- +0x10: pointer to TGInstanceHandlerTable (lazy, NULL until needed)
        |
        +-- +0x0C: pointer to 0x94-byte bucket array (37 buckets)
              |
              +-- TGCallback chains (one chain per bucket)
```

## Dispatch Flow

The high-level path. Each step gets its anchored function name where one exists; bare prose where the C++ method name isn't in the binary's string table.

1. **PostEvent** — Caller creates a `TGEvent` (size 0x28, vtable `0x00896018`) and submits it to the singleton. The SWIG wrapper `TGEventManager_AddEvent` at 0x005c8be9 reads the singleton at `[0x00991438]`. The underlying C++ method is bound by the SWIG string `AddEvent`.
2. **Broadcast dispatch** — The event manager walks the global broadcast handler infrastructure, finds the chain for the event type, and visits each registered `TGCallback`.
3. **Per-instance dispatch** — For events with a non-NULL destination, the destination's `TGEventHandlerObject+0x10` is consulted. If non-NULL, the `TGInstanceHandlerTable` is hashed by event type into its 37-bucket array (struct+0x0C) and the matching chain is walked.
4. **Callback invocation** — Each `TGCallback` is invoked according to its flags: a direct C++ function call (when `isPython == 0`), or a Python `module.function` lookup-and-call (when `isPython == 1`). The Python path routes through `FUN_006f15c0` (`InvokePythonHandler`) — see [Python Dispatch](#python-dispatch) below.

The dispatcher is reentrant-safe: the `TGConditionHandler` reentrant flag at +0x30 lets a handler that's currently dispatching enqueue add/remove operations rather than mutating the live list.

## Key Classes

### TGEventManager

The singleton that owns the broadcast handler infrastructure and the event queue.

| Anchor | Value |
|--------|-------|
| Singleton pointer | global `0x00991438` (zero in image, populated at boot) |
| Singleton discovery | SWIG wrapper `TGEventManager_AddEvent` at 0x005c8be9 begins `MOV EAX, [0x00991438]` |

**Anchored API** (from SWIG string table):

- `AddEvent` — submit a `TGEvent` for dispatch
- `RemoveAllBroadcastHandlersForObject` — bulk-remove handlers owned by a destroyed object
- `RemoveBroadcastHandler` — single-handler removal
- `AddBroadcastPythonMethodHandler` — register a Python bound-method handler
- `AddBroadcastPythonFuncHandler` — register a Python free-function handler

Method names beyond this list (e.g., `RegisterObject`, `FindHandlerChain`, `DispatchToNextHandler` as the prior doc had them) had no string anchor and are not carried forward by name. The behaviours those names described still exist — they're listed in [Dispatch Flow](#dispatch-flow) as anchored steps without invented names.

### TGEvent

Base event object. Carries event type, source, destination, and type-specific data.

| Anchor | Value |
|--------|-------|
| Vtable | `0x00896018` |
| Struct size | `0x28` bytes |
| Size anchor | `new_TGEvent` SWIG wrapper at 0x005c5e66: `PUSH 0x28 ; CALL alloc` |
| Slot 1 (RTTI) | `FUN_006d5d20` returns ptr to `_p_TGEvent` at `0x0091427c` |

> [!IMPORTANT]
> **Correction from prior doc.** The prior revision described TGEvent as "factory ID 0x02". That's wrong: 0x02 is **TGObject's** GetTypeID return value (per [tg-hierarchy-vtables.md](tg-hierarchy-vtables.md)). TGEvent uses a different RTTI mechanism — vtable slot 1 returns a string pointer, not an integer constant. See [Two RTTI Systems](#two-rtti-systems) below.

**Anchored API** (from SWIG string table):

- `GetEventType` / `SetEventType`
- `GetSource` / `SetSource`
- `GetDestination` / `SetDestination`
- `Copy` / `Duplicate`
- `GetTimestamp` / `SetTimestamp`
- `GetRefCount` / `IncRefCount` / `DecRefCount`
- `IsLogged` / `SetLogged`
- `IsPrivate` / `SetPrivate`
- `IsNotSaved` / `SetNotSaved`

`TGObjPtrEvent` is an anchored event subclass with `GetObjPtr` / `SetObjPtr` accessors for events that carry an object-pointer payload. See [docs/protocol/tgobjptrevent-class.md](../protocol/tgobjptrevent-class.md).

### TGEventHandlerObject

The base class for every object that can register event handlers. Every UI class, every scene-graph node, and every game object inherits from this somewhere up its chain.

| Anchor | Value |
|--------|-------|
| Vtable | `0x00896044` |
| Ctor | `FUN_006d8f90` |
| Lazy InstanceHandlerTable slot | `+0x10` (init NULL by ctor) |
| Slot 5 (lazy alloc) | `FUN_006d9160` allocates the TGInstanceHandlerTable on first use |
| Slot 8 (Python dispatch) | `FUN_006f15c0` — universal across all 9 vtables in the Ship hierarchy chain |

**Anchored API** (from SWIG string table):

- `AddPythonMethodHandlerForInstance`
- `AddPythonFuncHandlerForInstance`
- `RemoveHandlerForInstance`
- `RemoveAllInstanceHandlers`
- `CallNextHandler`
- `ProcessEvent`

For the full vtable layout and the parent-chain through TGSceneObject → ObjectClass → ... → Ship, see [tg-hierarchy-vtables.md](tg-hierarchy-vtables.md). The slot 8 InvokePythonHandler is the most heavily inherited slot in the codebase (100+ data xrefs cluster around `0x006f15c0`).

### TGInstanceHandlerTable

Per-object handler table. Stored as a lazy pointer; allocated on first registration via vtable slot 5.

| Anchor | Value |
|--------|-------|
| Vtable | `0x00896030` |
| Struct size | `0x14` bytes |
| Pointer location | `TGEventHandlerObject+0x10` (init NULL) |
| Bucket array | `struct+0x0C` → pointer to 0x94-byte block |
| Bucket count | `0x25` (37 — written by init `FUN_006d7b30` as `p[2] = 0x25`) |

This is **two levels of pointer indirection**, not flat embedding. The prior doc said "37-bucket hash at +0x10" — correct in spirit, but the layout is:

```
TGEventHandlerObject*
  + 0x10  ────►  TGInstanceHandlerTable (0x14 bytes, allocated lazily)
                   +0x00  vtable (0x00896030)
                   +0x0C  ────►  37-bucket hash array (0x94 bytes, allocated separately)
                                   bucket[0]  ────►  TGCallback chain head
                                   bucket[1]  ────►  TGCallback chain head
                                   ...
                                   bucket[36] ────►  TGCallback chain head
```

The same 37-bucket / 0x25 pattern shows up in the NiRTTI factory hash table at `DAT_009a2b98` — same constant, same growth model (see [nirtti-factory-catalog.md](nirtti-factory-catalog.md)).

### TGConditionHandler

The sorted-handler-chain container. The architectural property "supports two arrays: broadcast and per-object, reentrant during dispatch" from the prior doc is real, and the layout is now anchored.

| Anchor | Value |
|--------|-------|
| Vtable | `0x00896104` |
| Container size | `~0x34` bytes |
| Ctor | `FUN_006e1870` |

The ctor writes the **same vtable** at both `param_1[0]` and `param_1[6]` — the container holds two embedded sub-structs that each have the shape `{vtable, base_ptr, capacity, count, growth, total}`. This is the dual-array architecture made concrete:

| Offset | Field | Initial value |
|--------|-------|---------------|
| +0x00 | broadcast sub-struct: vtable | `0x00896104` |
| +0x04 | broadcast sub-struct: base_ptr | alloc 8 bytes |
| +0x08 | broadcast sub-struct: capacity | 2 |
| +0x0C | broadcast sub-struct: count | 0 |
| +0x10 | broadcast sub-struct: growth | (set by ctor) |
| +0x14 | broadcast sub-struct: total | 4 |
| +0x18 | per-object sub-struct: vtable | `0x00896104` (same) |
| +0x1C | per-object sub-struct: base_ptr | alloc 4 bytes |
| +0x20 | per-object sub-struct: capacity | 1 |
| +0x24 | per-object sub-struct: count | 0 |
| +0x28 | per-object sub-struct: growth | (set by ctor) |
| +0x2C | per-object sub-struct: total | 1 |
| +0x30 | reentrant "currently dispatching" flag | 0 |

The reentrant flag at +0x30 is what makes mutation-during-dispatch safe: a handler that registers or removes another handler while the dispatcher is walking the array gets its operation deferred instead of corrupting the iteration.

The specific internal method names (`AddEntry`, `InsertSorted`, `FindFirstByKey`, `RemoveByName`, `RemoveAllForObject`) from the prior doc are not in the binary's string table. The behaviours they described still exist — sorted insertion via binary search, key lookup, by-name removal — but the C++ names aren't anchored by this pass.

### TGCallback

The wrapper around a single registered handler. C++ function pointer or Python `module.function` string, chosen by the `isPython` flag bit.

| Anchor | Value |
|--------|-------|
| Vtable | `0x008960f4` |
| Struct size | `0x14` bytes (5 dword fields) |
| Ctor | `FUN_006e09e0` (writes all 5 fields) |
| Vtable slot 3 | `FUN_006e0c10` (sentinel-field accessor) |

**Layout** (all 5 offsets verified by the ctor body):

| Offset | Size | Field | Notes |
|--------|------|-------|-------|
| +0x00 | 4 | vtable pointer | `0x008960f4` |
| +0x04 | 4 | flags | bit0=isMethod, bit1=isPython, bit2=active, bit3=pendingDelete (carried from prior doc) |
| +0x08 | 4 | next | chain pointer |
| +0x0C | 4 | sentinel cookie | initial value `DAT_0095adf8` |
| +0x10 | 4 | function or string ptr | C++ `void*` OR ptr to `"module.function"` string |

When `isPython` is set, +0x10 points to a string of the form `"module.function"`, which is resolved at invocation time via the Python import machinery — see [Python Dispatch](#python-dispatch).

A second TGCallback-shaped vtable lives at `0x008961ac` (ctor `FUN_006ec6f0`). This is a Python-flavoured subclass; the runtime distinguishes the two by vtable identity rather than the flags bit alone. The per-slot semantics of the second vtable weren't decompiled in this pass — flagged as documentation debt.

### TGEvent Queue

The TGEventManager owns a queue of pending events for deferred dispatch during the game-loop tick. The queue is a linked list with head and tail pointers. Specific method names for queue manipulation are not anchored by this pass; the prior doc named them `SaveToStream` / `LoadFromStream`, but those strings are absent from the binary.

## Python Dispatch

The Python bridge is the most heavily-used dispatch path. Engine→Python is how the gameplay scripts in `scripts/` and `scripts/Custom/` see the world.

| Step | Anchor |
|------|--------|
| TGEventHandlerObject vtable slot 8 = InvokePythonHandler | `FUN_006f15c0` at offset `+0x20` |
| Universal across the TGEventHandlerObject hierarchy | Cross-confirmed in [tg-hierarchy-vtables.md](tg-hierarchy-vtables.md) (all 9 vtables in the Ship chain show `0x006f15c0` at +0x20) |
| Module resolution | `FUN_0074d280` against the module registry at `0x008d8af0` ("ScriptObject") |

When a TGCallback has `isPython == 1`, the dispatcher reads its `module.function` string from `+0x10`, splits it on the dot, imports the module via `FUN_0074d280`, gets the function attribute, and calls it with the event payload.

There is also a Python-flavoured TGCallback subclass at vtable `0x008961ac` (ctor `FUN_006ec6f0`) — a separate runtime class for Python callbacks rather than just a flag-bit distinction. The two coexist; the runtime keys off vtable identity for fast classification before reading the flags field.

## Handler Registration Pattern

Every class inheriting from `TGEventHandlerObject` has two virtual methods that register its handler set at construction time:

1. **RegisterHandlerNames** — calls a debug-name registration helper for each handler, attaching a string identifier compiled in from original source. This pattern was identified across 50+ classes in pre-v5 Pass 9C work.
2. **RegisterHandlers** — calls the actual register-event-handler routine, binding each handler function to its event type ID.

The specific vtable slot positions for `RegisterHandlerNames` and `RegisterHandlers` weren't pinned by this validation pass. They live in the TGEventHandlerObject vtable slot range around `HandleEvent` at slot 20 (`FUN_006d9240`) — see [tg-hierarchy-vtables.md](tg-hierarchy-vtables.md). A per-slot validation pass on the TGEventHandlerObject vtable would settle their exact positions; tracked as documentation debt.

## Event Type ID Encoding

Event type IDs follow a hierarchical encoding. Ranges below are anchored by xref clusters at the cited addresses; specific IDs within each range are cataloged in companion docs.

| Range | Category | Anchor |
|-------|----------|--------|
| `0x00030001` – `0x00040001` | Input events (mouse, keyboard, gamepad, control) | Multiple UI region xrefs across 0x0046-0x004B (per [function-map.md](function-map.md)) |
| `0x00800058` – `0x0080005A` | Targeting (TARGET_WAS_CHANGED, TARGET_SUBSYSTEM_SET) | 0x00800058 xrefs at 0x004fe62b, 0x00537d3e |
| `0x008000E0` | SetPhaserLevel | xrefs at 0x00573e82, 0x0069e9c4 (MP dispatcher) |
| `0x008000E3` | StartCloak | heavy xref cluster in the 0x008631xx cloak region |
| `0x008000E5` | StopCloak | grouped with StartCloak in the same cluster |
| `0x008000XX` (general) | Game events | full catalog in [ui-class-hierarchy.md](ui-class-hierarchy.md) and [docs/protocol/game-opcodes.md](../protocol/game-opcodes.md) |

The combat-event IDs (StartFiring, StopFiring, etc.) all live in the `0x008000Dx` and `0x008000Ex` ranges and are anchored at code addresses in the dispatcher recovery — see [docs/protocol/game-opcodes.md](../protocol/game-opcodes.md) for the per-opcode mapping into wire-format opcodes 0x07–0x12.

## Two RTTI Systems

The TG hierarchy uses **two** RTTI mechanisms that coexist. This is structurally important: a reader assuming a single system will read TGEvent's vtable slot 1 as garbage.

**Integer-tag RTTI** (TGObject → TGStreamedObject → TGEventHandlerObject → ... → Ship chain):

- Slot 1 returns an integer constant via `mov eax, <imm32> ; ret` (6 bytes).
- TGObject = `0x02`, TGStreamedObject = `0x03`, TGEventHandlerObject = `0x0102`, TGSceneObject = `0x8002`.
- See the Class Type-ID Constants table in [tg-hierarchy-vtables.md](tg-hierarchy-vtables.md) for the full set.

**String-pointer RTTI** (TGEvent and similar event classes):

- Slot 1 returns a pointer to a `_p_<ClassName>` string in the SWIG type-name region.
- TGEvent slot 1 (`FUN_006d5d20`) returns ptr to `_p_TGEvent` at `0x0091427c`.
- The string itself is the type identity.

The prior revision of this doc conflated the two and described TGEvent as "factory ID 0x02". 0x02 is TGObject's tag. TGEvent's actual type tag is the string-pointer value — and whether the string-pointer or some derived integer is intended as the comparable type-ID is an open question. The slot-1 return value is the only externally-observable identity for TGEvent at this point.

## Anchored vs Inferred Method Names

A v5-honest doc only names a C++ method when there's a string anchor for it in the binary. SWIG wrapper names are the most reliable source — every SWIG-bound method has its name as a constant string in the `.data` segment, retrievable via `search_strings`. Methods that are purely internal to the C++ implementation (never bound to Python, never used in a debug print) won't appear in the string table and aren't anchorable by name.

The prior revision of this doc named several internal methods that have no string anchor: `SaveBroadcastHandlers`, `LoadBroadcastHandlers`, `FixupReferences`, `FixupComplete`, the `TGConditionHandler` insertion/lookup methods, and the `TGEventHandlerTable` chain-management methods. The behaviours those names described are real and the doc still describes them, but the names themselves aren't carried forward. Where the behaviour matters but the name isn't anchored, this revision describes the behaviour by what it does ("the handler-cleanup routine called when objects are destroyed") rather than by an invented C++ name.

This is the same disposition the engine family applies elsewhere — see [docs/guides/v5-evidence-header.md](../guides/v5-evidence-header.md) and the catalog passes in [v5-validation-status.md](v5-validation-status.md) §6.

## Open Questions and Documentation Debt

1. **TGEvent's actual type tag.** Slot 1 returns a string pointer; whether the engine uses the string-pointer value itself as a comparable type-ID or derives an integer from it elsewhere is unverified. Likely settled by decompiling the slot-1 callers.
2. **TGEventManager singleton initialization site.** The pointer at `0x00991438` is populated at boot but the writing instruction wasn't located by this pass. Standard boot-side singleton, likely in UtopiaApp init.
3. **RegisterHandlerNames / RegisterHandlers vtable slot positions.** The pattern is real (50+ classes in pre-v5 Pass 9C) but the specific slot indices in the TGEventHandlerObject vtable weren't pinned this pass. They live near `HandleEvent` at slot 20 (`FUN_006d9240`).
4. **Python-flavoured TGCallback subclass at `0x008961ac`.** Vtable identified, per-slot semantics not decompiled. Likely overrides the invocation method to skip the C++/Python branch and go straight to import-and-call.
5. **TGEvent queue method names.** Anchored to the SWIG `AddEvent` entry point but the queue's internal API (enqueue, dequeue, peek) has no string anchor on the queue side.
6. **Per-array sort key.** The `TGConditionHandler` dual sub-structs are described as "sorted" by the architectural intent; the specific sort key (priority? handler ID? object pointer?) requires decompiling the insertion routine.

Each of these is a `confidence: medium` claim away from `verified` — none blocks the current status.

## See also

- [tg-hierarchy-vtables.md](tg-hierarchy-vtables.md) — TGObject through Ship vtable chain (verified). Anchors the TGEventHandlerObject slot 8 InvokePythonHandler universal pattern that this doc cites.
- [netimmerse-vtables.md](netimmerse-vtables.md) — NetImmerse 3.1 vtable layouts (verified). Voice and structural precedent for this doc.
- [function-map.md](function-map.md) — address-range partition. Anchors the UI-region (0x0046-0x004B) and cloak-region (0x008631xx) xref clusters cited in [Event Type ID Encoding](#event-type-id-encoding).
- [ui-class-hierarchy.md](ui-class-hierarchy.md) — full event-ID catalog for the UI subsystem.
- [docs/protocol/python-messages.md](../protocol/python-messages.md) — the Python-side messaging API that consumes TGEvent payloads.
- [docs/protocol/pythonevent-wire-format.md](../protocol/pythonevent-wire-format.md) — how events leave the C++ event system and travel on the wire.
- [docs/protocol/tgobjptrevent-class.md](../protocol/tgobjptrevent-class.md) — the most heavily-used TGEvent subclass (45% of combat PythonEvents).
- [v5-validation-status.md](v5-validation-status.md) §6 — validation log entry for this doc.
- [docs/guides/v5-evidence-header.md](../guides/v5-evidence-header.md) — the evidence standard.
