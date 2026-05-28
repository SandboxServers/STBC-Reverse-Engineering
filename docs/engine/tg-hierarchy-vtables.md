> [docs](../README.md) / [engine](README.md) / tg-hierarchy-vtables.md

---
title: TG Hierarchy Vtable Layout
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
  - claim: "TGObject vtable at 0x00896278 — 12 slots, 0x30 bytes (NOT 0x008963BC)"
    address: 0x00896278
    function: FUN_006f0a70
    confidence: high
    note: "TGObject ctor FUN_006f0a70 writes `*this = &PTR_0x00896278`. Confirmed by 2 ctor xrefs (FUN_006f0a70 and FUN_006f0ba0). 0x008963BC has ZERO xrefs (verified via get_xrefs_to) and is not a runtime vtable."
  - claim: "TGStreamedObject vtable at 0x008962F4"
    address: 0x008962F4
    function: FUN_006f31a0
    confidence: high
    note: "TGStreamedObject ctor FUN_006f31a0 calls TGObject parent ctor then writes this vtable. Adds 4 slots (12-15)."
  - claim: "TGStreamedObjectEx vtable at 0x008962A8"
    address: 0x008962A8
    function: FUN_006f2590
    confidence: high
    note: "TGStreamedObjectEx ctor FUN_006f2590 chains through TGStreamedObject and writes this vtable. Overrides slot 7 (PostDeserialize)."
  - claim: "TGEventHandlerObject vtable at 0x00896044"
    address: 0x00896044
    function: FUN_006d8f90
    confidence: high
    note: "TGEventHandlerObject ctor FUN_006d8f90 chains through TGStreamedObjectEx and writes this vtable. Adds event-dispatch slots through slot 22."
  - claim: "TGSceneObject vtable at 0x00889708"
    address: 0x00889708
    function: FUN_004308e0
    confidence: high
    note: "TGSceneObject ctor FUN_004308e0 chains through TGEventHandlerObject and writes this vtable. Adds ~27 scene-graph slots."
  - claim: "ObjectClass vtable at 0x00889950"
    address: 0x00889950
    function: FUN_00435030
    confidence: high
    note: "ObjectClass ctor FUN_00435030 chains through TGSceneObject and writes this vtable. Extends through slot ~66."
  - claim: "PhysicsObjectClass vtable at 0x00894128 — adds slots 67-81"
    address: 0x00894128
    function: null
    confidence: high
    note: "PhysicsObjectClass extends ObjectClass with network serialization and physics integration slots (SerializeToBuffer 0x005a1cf0, InitObject 0x005a2030, etc.)."
  - claim: "DamageableObject vtable at 0x00893D88 — 92 slots, ends at 0x008944AC"
    address: 0x00893D88
    function: FUN_00591200
    confidence: high
    note: "DamageableObject ctor FUN_00591200 chains through PhysicsObjectClass and writes this vtable. 92 slots × 4 bytes = 0x16C; vtable ends at 0x008944AC."
  - claim: "Ship vtable at 0x00894340 — 92 slots, same count as DamageableObject"
    address: 0x00894340
    function: FUN_005abdc0
    confidence: high
    note: "Ship ctor FUN_005abdc0 chains through DamageableObject and writes this vtable. Boundary at 0x008944AC followed by 6 float constants (75.0, 50.0, 500.0, 900.0, 0.8, 0.0049 — Ship-class data adjacent to vtable). Ship does NOT add new slots; it overrides existing slots."
  - claim: "Ship does NOT inherit from NiObject — parallel hierarchy"
    address: null
    function: null
    confidence: high
    note: "Constructor walk from Ship up reaches TGObject (not NiObject). Confirmed by 8 ctor decompiles showing TGObject as the base."
  - claim: "TGObject 12-slot vtable layout: slot 0=scalar_deleting_dtor, slot 1=GetTypeID, slot 3=DebugPrint (NOT GetRTTI at slot 0)"
    address: 0x00896278
    function: null
    confidence: high
    note: "Per-slot byte/decompile verification. Layout differs structurally from NiObject (where slot 0 = GetRTTI and slot 10 = dtor)."
  - claim: "TGObject slot 0 = scalar_deleting_dtor at 0x006f0b70"
    address: 0x006f0b70
    function: null
    confidence: high
    note: "MSVC scalar deleting dtor byte signature `56 8B F1 E8 ?? 00 00 00 F6 44 24 08 01 74 14 56` confirmed across 4 sampled classes (TGObject, TGStreamedObject, TGEventHandlerObject, Ship)."
  - claim: "TGObject slot 1 = GetTypeID at 0x006f0b60, returns 2"
    address: 0x006f0b60
    function: null
    confidence: high
    note: "Bytes `B8 02 00 00 00 C3` = `mov eax, 2 ; ret`. Universal slot-1 pattern across the TG hierarchy."
  - claim: "TGObject slots 5/6/7 are MSVC `__purecall` stub at 0x00859a0b (pure-virtual)"
    address: 0x00859a0b
    function: null
    confidence: high
    note: "Bytes `6A 19 E8 69 13 00 00 59 C3` = `push 0x19 ; call __purecall_thunk ; pop ecx ; ret`. ReadFromStream/ResolveObjectRefs/PostDeserialize are pure-virtual in TG base; derived classes that need stream I/O override them. Same stub cross-anchored from netimmerse-vtables.md."
  - claim: "TGObject slot 3 = DebugPrint at 0x006f1650 (inherited unchanged across all 9 hierarchy vtables)"
    address: 0x006f1650
    function: null
    confidence: high
    note: "Verified that all 9 vtables in the Ship chain show 0x006f1650 at offset +0x0C."
  - claim: "TGObject slot 8 = InvokePythonHandler at 0x006f15c0 (inherited unchanged across all 9 hierarchy vtables)"
    address: 0x006f15c0
    function: null
    confidence: high
    note: "Verified that all 9 vtables in the Ship chain show 0x006f15c0 at offset +0x20."
  - claim: "TGObject slot 9 = GetClassName at 0x006f1540, returns ptr to 'TGObject' string at 0x0095B05C"
    address: 0x006f1540
    function: null
    confidence: high
    note: "Returns address of bare string at 0x0095B05C."
  - claim: "TGObject slot 10 = GetSwigTypeName at 0x006f1550, returns ptr to '_p_TGObject' string at 0x009142B0"
    address: 0x006f1550
    function: null
    confidence: high
    note: "Returns address of SWIG type-encoding string at 0x009142B0."
  - claim: "TGObject slot 11 = GetObjectPtrTypeName at 0x006f1560, returns ptr to 'TGObjectPtr' string at 0x0095B270"
    address: 0x006f1560
    function: null
    confidence: high
    note: "Returns address of SWIG object-ptr type string at 0x0095B270."
  - claim: "Class Type-ID numbering: TGObject=0x02, TGStreamedObject=0x03, TGEventHandlerObject=0x0102, TGSceneObject=0x8002"
    address: null
    function: null
    confidence: high
    note: "All 4 GetTypeID stubs verified by byte inspection (`mov eax, IMM ; ret`). Numbering likely has bit-field semantics (low byte = sub-class, high byte = domain) — open question #1."
  - claim: "Ship slot 72 = Ship__WriteStateUpdate at 0x005b17f0 (StateUpdate pipeline)"
    address: 0x005b17f0
    function: Ship__WriteStateUpdate
    confidence: high
    note: "Decompile confirms the dirty-flags + CompressedVector encoding + round-robin subsystem serialization that produces the opcode 0x1C wire payload. Cross-anchored to docs/protocol/stateupdate.md."
  - claim: "Ship slot 85 = Ship__CollisionDamageWrapper at 0x005b0060"
    address: 0x005b0060
    function: Ship__CollisionDamageWrapper
    confidence: high
    note: "Delegates to FUN_005afd70 + FUN_00593650 (DamageableObject__ApplyCollisionDamage). Cross-anchored to docs/protocol/collision-effect-protocol.md."
  - claim: "TGStreamedObject slot 12 = chained WriteToStream dispatch at 0x006f2750"
    address: 0x006f2750
    function: null
    confidence: high
    note: "Decompile confirms chained-write dispatch (calls vtable+4 then walks dispatch list)."
  - claim: "TGStreamedObject slot 14 = AddEventHandler at 0x006f3400"
    address: 0x006f3400
    function: null
    confidence: high
    note: "Allocates 0x14-byte handler entry and links into the per-instance handler list."
  - claim: "TGEventHandlerObject slot 20 = HandleEvent at 0x006d9240"
    address: 0x006d9240
    function: null
    confidence: high
    note: "Main per-instance event dispatch entry point; consumed by [docs/engine/event-system-architecture.md](event-system-architecture.md)."
  - claim: "Sibling TG vtables outside Ship chain: TGMessage 0x008958D0, TGBufferStream 0x00895C58, TGDimmerController 0x0088b7ec (NiRTTI-registered)"
    address: null
    function: null
    confidence: high
    note: "TGMessage at vtable 0x008958D0 — identified 2026-05-28 via SWIG new_TGMessage allocator (corrects prior mis-identification as TGBufferStream from the precision dig). The actual SWIG TGBufferStream is the 0x30-byte buffer-cursor class at vtable 0x00895C58 (FUN_006CEFE0 ctor). TGDimmerController + TGFuzzyTriShape are the 2 NiRTTI-registered TG classes per docs/engine/nirtti-factory-catalog.md. See docs/protocol/stream-primitives.md § Two Stream Classes."
  - claim: "0x008963BC has ZERO xrefs — not a runtime class vtable"
    address: 0x008963BC
    function: null
    confidence: high
    note: "`get_xrefs_to(0x008963BC)` returns 0. No constructor writes that address. Prior speculation about TGHashTable identity is unsupported; likely orphan .rdata data."
companions:
  - docs/engine/netimmerse-vtables.md
  - docs/engine/nirtti-factory-catalog.md
  - docs/engine/rtti-class-catalog.md
  - docs/engine/function-map.md
  - docs/engine/v5-validation-status.md
supersedes:
  - (prior undated revision)
---

# TG Hierarchy Vtable Layout (stbc.exe)

> [!NOTE]
> This doc is `status: verified`. The 9-vtable Ship inheritance chain, TGObject 12-slot map,
> universal slot patterns (slot-0 dtor, slot-1 GetTypeID, slot-3 DebugPrint, slot-8
> InvokePythonHandler), and 2 sampled Ship slots (72 WriteStateUpdate, 85
> CollisionDamageWrapper) are `confidence: high`. The remaining ~100 of ~140 per-slot rows
> are `confidence: medium` by pattern extrapolation; per-slot decompile sweep is the
> promotion path. See [docs/guides/v5-evidence-header.md](../guides/v5-evidence-header.md)
> for the standard.

## Key Difference from NiObject Hierarchy

The TG class hierarchy (TGObject → TGStreamedObject → ... → Ship) uses a **completely
different** vtable layout from the NiObject hierarchy. The critical structural difference:

- **NiObject**: Slot 0 = `GetRTTI`, slot 10 (+0x28) = scalar_deleting_dtor
- **TGObject**: Slot 0 = `scalar_deleting_dtor`, slot 3 (+0x0C) = DebugPrint

Ship does **NOT** inherit from NiObject. It inherits from TGObject through this chain:

```
TGObject (vtable 0x00896278)
  -> TGStreamedObject (vtable 0x008962F4)
    -> TGStreamedObjectEx (vtable 0x008962A8)
      -> TGEventHandlerObject (vtable 0x00896044)
        -> TGSceneObject (vtable 0x00889708)
          -> ObjectClass (vtable 0x00889950)
            -> PhysicsObjectClass (vtable 0x00894128)
              -> DamageableObject (vtable 0x00893D88)
                -> Ship (vtable 0x00894340)
```

Each constructor calls its parent, initializes fields, then writes its own vtable pointer
to `*this`. The constructor chain has been walked end-to-end (see [Methodology](#methodology)).

> **0x008963BC is NOT TGObject's vtable.** `get_xrefs_to(0x008963BC)` returns ZERO
> references — no constructor writes that address; it is not a runtime class vtable. The
> prior speculation about TGHashTable identity is unsupported and should be dropped. Likely
> orphan `.rdata` data.
>
> **CORRECTED from 0x008963BC** — that was wrong. (Kept as a historical drift marker for
> grep purposes.)

## Vtable Addresses

All `[v5-validated 2026-05-28]` via constructor-chain walk:

| Class | Vtable Address | Constructor | Notes |
|-------|----------------|-------------|-------|
| TGObject | `0x00896278` | FUN_006f0a70 | 12 slots; root of the TG hierarchy |
| TGStreamedObject | `0x008962F4` | FUN_006f31a0 | Adds slots 12-15 (stream chain, AddEventHandler) |
| TGStreamedObjectEx | `0x008962A8` | FUN_006f2590 | Overrides slot 7 (PostDeserialize at 0x006f2810) |
| TGEventHandlerObject | `0x00896044` | FUN_006d8f90 | Adds event-dispatch slots (HandleEvent at slot 20) |
| TGSceneObject | `0x00889708` | FUN_004308e0 | Adds ~27 scene-graph slots |
| ObjectClass | `0x00889950` | FUN_00435030 | Extends through slot ~66 |
| PhysicsObjectClass | `0x00894128` | (via DO ctor) | Adds slots 67-81 (network + physics) |
| DamageableObject | `0x00893D88` | FUN_00591200 | 92 slots total; ends at `0x008944AC` |
| Ship | `0x00894340` | FUN_005abdc0 | 92 slots, same count as DO; overrides existing slots |

> **Vtable boundary verification (Ship/DamageableObject):** the Ship vtable at `0x00894340`
> ends at `0x008944AC` (= `0x00894340 + 92 × 4 = 0x00894340 + 0x16C`). The next 24 bytes are
> 6 float constants (75.0, 50.0, 500.0, 900.0, 0.8, 0.0049) — Ship-class data adjacent to the
> vtable, not vtable continuation. This confirms 92 slots, not "92 + extra".

## TGObject Vtable (0x00896278) — 12 slots

All TGObject-derived classes share these first 12 slots in the same order. The slot-1
`GetTypeID` pattern is universal (each derived class overrides it to return its own
type-ID constant). All rows `[v5-validated 2026-05-28]`.

| Slot | Offset | Name | Address | Notes |
|------|--------|------|---------|-------|
| 0 | +0x00 | scalar_deleting_dtor | `0x006f0b70` | MSVC `56 8B F1 E8 ?? 00 00 00 F6 44 24 08 01 74 14 56` pattern |
| 1 | +0x04 | GetTypeID | `0x006f0b60` | `B8 02 00 00 00 C3` = `mov eax, 2 ; ret` |
| 2 | +0x08 | IsTypeID | `0x00518ab0` | Checks if param == 2 |
| 3 | +0x0C | DebugPrint | `0x006f1650` | Debug print object info; **inherited unchanged across all 9 hierarchy vtables** |
| 4 | +0x10 | WriteToStream | `0x006f0bc0` | Serialize to stream |
| 5 | +0x14 | ReadFromStream | `0x00859a0b` | MSVC `__purecall` stub (pure-virtual); derived classes override |
| 6 | +0x18 | ResolveObjectRefs | `0x00859a0b` | MSVC `__purecall` stub (pure-virtual) |
| 7 | +0x1C | PostDeserialize | `0x00859a0b` | MSVC `__purecall` stub (pure-virtual); TGStreamedObjectEx overrides at 0x006f2810 |
| 8 | +0x20 | InvokePythonHandler | `0x006f15c0` | Call Python event handler; **inherited unchanged across all 9 hierarchy vtables** |
| 9 | +0x24 | GetClassName | `0x006f1540` | Returns ptr to "TGObject" string at `0x0095B05C` |
| 10 | +0x28 | GetSwigTypeName | `0x006f1550` | Returns ptr to "_p_TGObject" string at `0x009142B0` |
| 11 | +0x2C | GetObjectPtrTypeName | `0x006f1560` | Returns ptr to "TGObjectPtr" string at `0x0095B270` |

> Slots 5/6/7 use the MSVC `__purecall` stub at `0x00859a0b` — bytes
> `6A 19 E8 69 13 00 00 59 C3` (`push 0x19 ; call __purecall_thunk ; pop ecx ; ret`).
> This is the **same** stub that NiGeometry slot 49 uses; cross-anchored from
> [netimmerse-vtables.md](netimmerse-vtables.md). The prior doc text "(NULL stub
> 0x00859a0b)" was misleading — it is not a NULL stub, it is the pure-virtual placeholder.

TGEventHandlerObject overrides slots 0-2, 4-5, 9-11 (for its own type ID, names, stream
methods). The pattern is universal across **all** TG hierarchy classes — each class
overrides slots 0-2 and 9-11 to return its own type info.

## Class Type-ID Constants (slot-1 GetTypeID returns)

The slot-1 `GetTypeID` stub is a 6-byte `mov eax, IMM ; ret` returning a class-specific
type ID. Verified by byte inspection:

| Class | Type ID | GetTypeID Addr |
|-------|---------|----------------|
| TGObject | `0x02` | `0x006f0b60` |
| TGStreamedObject | `0x03` | `0x006f31c0` |
| TGEventHandlerObject | `0x0102` | `0x006d8fb0` |
| TGSceneObject | `0x8002` | `0x00430950` |

> Incomplete — extend per-class as the full chain is sampled. The numbering scheme
> (`0x02` / `0x03` / `0x0102` / `0x8002`) suggests bit-field semantics (low byte =
> sub-class, high byte = domain). Open question #1: this likely deserves its own catalog
> doc when other TG-sibling classes (e.g., TGBufferStream's `0x32` tag) are folded in.

## TGStreamedObject Additions (vtable 0x008962F4)

Inherits TGObject's 12 slots. Adds 4 new slots (12-15):

| Slot | Offset | Name | Address | Notes |
|------|--------|------|---------|-------|
| 12 | +0x30 | WriteToStreamChain | `0x006f2750` | Chained serialize dispatch [v5-validated 2026-05-28] |
| 13 | +0x34 | (unknown) | `0x006f2790` | Pattern-extrapolated; per-slot decompile pending |
| 14 | +0x38 | AddEventHandler | `0x006f3400` | Allocates 0x14-byte handler entry [v5-validated 2026-05-28] |
| 15 | +0x3C | (unknown) | `0x006f3500` | Pattern-extrapolated; per-slot decompile pending |

## TGStreamedObjectEx Additions (vtable 0x008962A8)

Inherits TGStreamedObject slots. Overrides:
- Slot 7 (+0x1C): PostDeserialize → `0x006f2810` (replaces the inherited `__purecall` stub)

## TGEventHandlerObject Additions (vtable 0x00896044)

| Slot | Offset | Name | Address | Notes |
|------|--------|------|---------|-------|
| 16 | +0x40 | (unknown) | varies | Pattern-extrapolated |
| 17 | +0x44 | (unknown) | varies | Pattern-extrapolated |
| 18 | +0x48 | (unknown) | varies | Pattern-extrapolated |
| 19 | +0x4C | (unknown) | varies | Pattern-extrapolated |
| 20 | +0x50 | HandleEvent | `0x006d9240` | Main event dispatch entry point [v5-validated 2026-05-28] |
| 21 | +0x54 | Update | (pure?) | Per-tick update; TGSceneObject overrides at 0x00430cf0 |
| 22 | +0x58 | (unknown) | `0x00430d30` | TGSceneObject overrides |

Also adds (non-virtual): `RegisterConditionHandler` at `0x006da4e0`.

## TGSceneObject Additions (vtable 0x00889708)

| Slot | Offset | Name | Address | Notes |
|------|--------|------|---------|-------|
| 21 | +0x54 | Update | `0x00430cf0` | TGSceneObject override |
| 22 | +0x58 | SetScene | `0x00430e20` | |
| 23-25 | +0x5C-64 | (stubs) | `0x00419880`/`0x00419890` | Various small stubs |
| 26 | +0x68 | SetDatabaseName | `0x004315c0` | |
| 27-47 | +0x6C-BC | (varies) | varies | Scene object management slots |
| 48 | +0xC0 | SetModel | `0x00430b70` | Assign NiNode model |

Overrides:
- Slot 6 (+0x18): ResolveObjectRefs → `0x00431e20` (replaces inherited `__purecall` stub)

## ObjectClass (vtable 0x00889950)

Adds slots through ~66. Key additions:
- `CreateCollisionProxy` via `0x004356a0`

## PhysicsObjectClass (vtable 0x00894128)

PhysicsObjectClass extends the hierarchy with network serialization and physics integration
slots. Slots 67-81 are the PhysicsObjectClass-specific additions to the vtable.

| Slot | Offset | Name | Address | Notes |
|------|--------|------|---------|-------|
| 67 | +0x10C | SerializeToBuffer | `0x005a1cf0` | Network buffer serialization |
| 68 | +0x110 | WriteNetworkHeader | `0x005a1d80` | Writes type ID + object ID to stream |
| 69 | +0x114 | WriteNetworkState | `0x005a1dc0` | Writes pos/rot(euler)/vel/name to stream |
| 70 | +0x118 | InitObject | `0x005a2030` | DamageableObject__InitObject: read species byte from stream |
| 71 | +0x11C | DeserializeFromNetwork | `0x005a2060` | PhysicsObjectClass__DeserializeFromNetwork |
| 72 | +0x120 | WriteStateUpdate | `0x005a26c0` | Base state update serialization |
| 73 | +0x124 | ReadStateUpdate | `0x005a2bf0` | Base state update deserialization |
| 74 | +0x128 | SetModel | `0x00591b60` | DamageableObject__SetModel |
| 75 | +0x12C | GetCollisionRadius? | `0x005910d0` | Returns float constant from `[0x00888b54]` |
| 76 | +0x130 | SetVelocityPair | `0x00578500` | Writes 2 floats to this+0xA8/AC |
| 77 | +0x134 | SetTargetObject | `0x005a15a0` | PhysicsObjectClass__SetTargetObject |
| 78 | +0x138 | UpdateAIForTarget | `0x005a16b0` | Ship__UpdateAIForTarget |
| 79 | +0x13C | CheckCollisionRateLimit | `0x005a22a0` | Rate limiting for collision checks |
| 80 | +0x140 | RayIntersect | `0x005a39f0` | PhysicsObjectClass level (DamageableObject overrides) |
| 81 | +0x144 | (unknown) | `0x005a38b0` | Pattern-extrapolated |

Ship overrides (vtable `0x00894340`) for PhysicsObjectClass-added slots:
- Slot 69: `0x005b0d80` Ship__WriteNetworkState (calls parent WriteNetworkState)
- Slot 70: `0x005b0e80` Ship__InitObject (full NIF + subsystem init)
- Slot 71: `0x005b0dc0` Ship__DeserializeFromNetwork (calls parent, also iterates ship+0x284)
- Slot 72: `0x005b17f0` Ship__WriteStateUpdate [v5-validated 2026-05-28]
- Slot 73: `0x005b21c0` Ship__ReadStateUpdate
- Slot 74: `0x005abda0` Ship__SetModel (calls DamageableObject__SetModel + ComputeBounds)
- Slot 77: `0x005ae5a0` Ship slot 77 override

## DamageableObject (vtable 0x00893D88, 92 slots, 0-91)

DamageableObject has 92 slots. Slots 90-91 are destructor variants (scalar_deleting_dtor
and an array destructor). Ship has 92 slots (0-91) — it does NOT add extra slots beyond
DamageableObject's 92.

Key virtual slots:

| Slot | Offset | Name | DO Address | Ship Address | Notes |
|------|--------|------|------------|--------------|-------|
| 70 | +0x118 | InitObject | varies | `0x005b0e80` | Object init |
| 71 | +0x11C | (varies) | varies | `0x005b0dc0` | Ship override, see PhysicsObjectClass row |
| 72 | +0x120 | WriteStateUpdate | varies | `0x005b17f0` | State serialization [v5-validated 2026-05-28] |
| 73 | +0x124 | ReadStateUpdate | varies | `0x005b21c0` | State deserialization |
| 74-77 | +0x128-134 | (varies) | varies | varies | Mixed inherited/override |
| 78 | +0x138 | ClearTargets | varies | `0x005ae600` | Clear targeting |
| 79 | +0x13C | CheckCollisionRateLimit | `0x005a22a0` | `0x005a22a0` | Rate limiting (inherited) |
| 80 | +0x140 | RayIntersect | `0x00594310` | `0x005ae730` | Ray/bounding sphere test |
| 81 | +0x144 | (varies) | `0x00594430` | `0x005aed90` | Very short (zeros struct, returns 1) |
| 82 | +0x148 | CollisionTest_A | `0x00594440` | `0x005af7d0` | Narrow collision test A |
| 83 | +0x14C | CollisionTest_B | `0x005945b0` | `0x005af830` | Narrow collision test B |
| 84 | +0x150 | CheckCollision | `0x00594840` | `0x005af890` | Full collision resolution |
| 85 | +0x154 | ApplyCollisionDamage | `0x00593650` | `0x005b0060` | Damage from collision [v5-validated 2026-05-28 for Ship] |
| 86 | +0x158 | (varies) | `0x005935d0` | `0x005935d0` | Collision notify loop (inherited) |
| 87 | +0x15C | (varies) | `0x00595e40` | `0x005b3480` | Base=RET stub; Ship overrides |
| 88 | +0x160 | SetupProperties | `0x00591190` | `0x005b3fb0` | Property-to-subsystem |
| 89 | +0x164 | LinkAllSubsystemsToParents | `0x005911a0` | `0x005b3e20` | Parent-child link |
| 90 | +0x168 | scalar_deleting_dtor | `0x00596340` | `0x005ac5e0` | Destructor variant |
| 91 | +0x16C | array_deleting_dtor | `0x005962f0` | `0x005abf30` | Destructor variant |

Also identified (non-virtual):
- `RegisterEventHandlers` at `0x00590980`
- `UnregisterEventHandlers` at `0x005909b0`

## Ship Vtable (92 slots, vtable 0x00894340, object size 0x328)

Ship has the same 92-slot layout as DamageableObject. It does **not** add new slots; it
overrides existing slots (including slots 90-91 destructors) with its own implementations.

### Complete Ship Vtable Map

| Slot | Offset | Address | Name | Override? |
|------|--------|---------|------|-----------|
| 0 | +0x00 | `0x005abfe0` | Ship__scalar_deleting_dtor | Override |
| 1 | +0x04 | `0x005abe60` | (unknown dtor variant) | Override |
| 2 | +0x08 | `0x005abe70` | (unknown dtor variant) | Override |
| 3 | +0x0C | `0x006f1650` | TGObject__DebugPrint | Inherited |
| 4 | +0x10 | `0x005b0f00` | Ship__WriteToStream | Override |
| 5 | +0x14 | `0x005b1220` | Ship__ReadFromStream | Override |
| 6 | +0x18 | `0x005b1500` | Ship__ResolveObjectRefs | Override |
| 7 | +0x1C | `0x005b1550` | Ship__PostDeserialize | Override |
| 8 | +0x20 | `0x006f15c0` | TGObject__InvokePythonHandler | Inherited |
| 9 | +0x24 | (unknown) | | |
| 10 | +0x28 | (unknown) | | |
| 11 | +0x2C | (unknown) | | |
| 12 | +0x30 | `0x006f2750` | TGStreamedObject__WriteToStreamChain | Inherited |
| 13 | +0x34 | `0x006f2790` | TGStreamedObject__ReadFromStreamChain? | Inherited |
| 14 | +0x38 | `0x006f3400` | TGStreamedObject__AddEventHandler | Inherited |
| 15 | +0x3C | `0x006f3500` | TGStreamedObject__RemoveEventHandler? | Inherited |
| 16-18 | +0x40-48 | varies | (inherited TG methods) | Inherited |
| 19 | +0x4C | `0x005abf10` | (Ship override, unknown) | Override |
| 20 | +0x50 | `0x006d9240` | TGEventHandlerObject__HandleEvent | Inherited |
| 21 | +0x54 | `0x005adae0` | Ship__Update | Override |
| 22 | +0x58 | `0x00430d30` | TGSceneObject__AttachDefaultProperty? (calls NiAVObject::AttachProperty(this+0x18, 0); NOT SetScene) | Inherited |
| 23 | +0x5C | `0x00419880` | (stub) | Inherited |
| 24 | +0x60 | `0x005b35a0` | Ship__SetScene (stops all sounds via TGSoundManager, then calls PhysicsObjectClass__SetScene) | Override |
| 25 | +0x64 | `0x00419890` | (stub) | Inherited |
| 26 | +0x68 | `0x004315c0` | TGSceneObject__SetDatabaseName | Inherited |
| 27-34 | +0x6C-88 | varies | (TGSceneObject/ObjectClass) | Mixed |
| 35 | +0x8C | `0x005abaa0` | (Ship override, near ComputeBounds) | Override |
| 36-47 | +0x90-BC | varies | (mixed inherited/override) | Mixed |
| 48 | +0xC0 | `0x00430b70` | TGSceneObject__SetModel | Inherited |
| 49-57 | +0xC4-E4 | varies | (mixed) | Mixed |
| 58 | +0xE8 | `0x005abc30` | Ship__GetBoundingBox | Override |
| 59-66 | +0xEC-108 | varies | (mixed) | Mixed |
| 67 | +0x10C | `0x005a1cf0` | PhysicsObjectClass__SerializeToBuffer | Inherited |
| 68 | +0x110 | `0x005a1d80` | PhysicsObjectClass__WriteNetworkHeader (writes type ID + object ID to stream) | Inherited |
| 69 | +0x114 | `0x005b0d80` | Ship__WriteNetworkState (calls PhysicsObjectClass__WriteNetworkState then Ship fields) | Override |
| 70 | +0x118 | `0x005b0e80` | Ship__InitObject | Override |
| 71 | +0x11C | `0x005b0dc0` | Ship__DeserializeFromNetwork (calls PhysicsObjectClass__DeserializeFromNetwork) | Override |
| 72 | +0x120 | `0x005b17f0` | Ship__WriteStateUpdate **[v5-validated 2026-05-28]** | Override |
| 73 | +0x124 | `0x005b21c0` | Ship__ReadStateUpdate | Override |
| 74 | +0x128 | `0x005abda0` | Ship__SetModel (calls PhysicsObjectClass__SetModel then ComputeBoundsFromGeometry) | Override |
| 75 | +0x12C | `0x005abf90` | (Ship override, unknown) | Override |
| 76 | +0x130 | `0x00578500` | (inherited? unknown) | |
| 77 | +0x134 | `0x005ae5a0` | (Ship, unknown) | |
| 78 | +0x138 | `0x005ae600` | Ship__ClearTargets | Override |
| 79 | +0x13C | `0x005a22a0` | Ship__CheckCollisionRateLimit | Inherited |
| 80 | +0x140 | `0x005ae730` | Ship__RayIntersect | Override |
| 81 | +0x144 | `0x005aed90` | (Ship override, unknown) | Override |
| 82 | +0x148 | `0x005af7d0` | Ship__CollisionTest_A | Override |
| 83 | +0x14C | `0x005af830` | Ship__CollisionTest_B | Override |
| 84 | +0x150 | `0x005af890` | Ship__CheckCollision | Override |
| 85 | +0x154 | `0x005b0060` | Ship__CollisionDamageWrapper **[v5-validated 2026-05-28]** | Override |
| 86 | +0x158 | `0x005935d0` | DamageableObject__CollisionNotifyLoop | Inherited |
| 87 | +0x15C | `0x005b3480` | (Ship override; DO base=RET stub 0x595e40) | Override |
| 88 | +0x160 | `0x005b3fb0` | Ship__SetupProperties | Override |
| 89 | +0x164 | `0x005b3e20` | Ship__LinkAllSubsystemsToParents | Override |
| 90 | +0x168 | `0x005ac5e0` | Ship__scalar_deleting_dtor_2 | Override |
| 91 | +0x16C | `0x005abf30` | Ship__array_dtor_wrapper | Override |

### Key Observations

1. **Ship has 92 slots (0-91), same count as DamageableObject** — Ship does NOT "add 2 extra slots". The boundary at `0x008944AC` is followed by float constants, not vtable continuation.
2. **Slot 87 and 91 differ**: slot 87 (`0x005abf30`) is a wrapper; slot 91 is a separate wrapper.
3. **~40 vtable entries** point to addresses Ghidra hasn't recognized as function starts (small stubs/thunks).
4. **Slot 20 (HandleEvent)** is inherited from TGEventHandlerObject, NOT overridden by Ship.
5. **Slots 82-85** form the collision detection/damage pipeline.
6. **Slots 88-89** are the property-to-subsystem setup pipeline.

### Identified Ship Overrides (29 of 92 slots)

Slots where Ship provides its own implementation (vs inheriting from parent):
0, 1, 2, 4, 5, 6, 7, 19, 21, 24, 35, 58, 69, 70, 71, 72, 73, 74, 75, 78, 80, 81, 82, 83, 84, 85, 88, 89, 90

### Network-Critical Slots

| Slot | Name | Role |
|------|------|------|
| 4 | WriteToStream | Full ship serialization for ObjCreate |
| 5 | ReadFromStream | Full ship deserialization from ObjCreate |
| 67 | SerializeToBuffer | Network buffer serialization |
| 70 | InitObject | Ship creation from network data |
| 72 | WriteStateUpdate | Per-tick state sync (opcode 0x1C) — `[v5-validated 2026-05-28]` |
| 73 | ReadStateUpdate | Per-tick state receive |
| 85 | CollisionDamageWrapper | Collision damage relay (opcode 0x15) — `[v5-validated 2026-05-28]` |

## Sibling TG Classes Not in Ship Chain

Other TG vtables exist outside the Ship inheritance chain. Cross-link for completeness:

- **TGMessage** at `0x008958D0` — wire-message envelope base class (size 0x40, ctor
  FUN_006B82A0 → `TGMessage_Ctor`). `vtable[0]()` returns `0x32` class tag, emitted as the
  first byte of every serialized blob (the dispatcher's stream-type gate). Derived
  subclasses: TGConnectMessage, TGDisconnectMessage, TGAckMessage, TGBootPlayerMessage,
  TGDoNothingMessage, TGNameChangeMessage. **Identified 2026-05-28 via SWIG `new_TGMessage`
  allocator at 0x005E12E0** — corrects the prior precision-dig identity (which
  mis-named this class as TGBufferStream).
- **TGBufferStream** at `0x00895C58` — the actual SWIG-visible TGBufferStream is a
  separate 0x30-byte buffer-cursor class (ctor FUN_006CEFE0). It does NOT live at vtable
  0x008958D0 (that's TGMessage). See [docs/protocol/stream-primitives.md](../protocol/stream-primitives.md)
  for the typed-primitive surface and [docs/protocol/stream-primitives.md § Two Stream Classes](../protocol/stream-primitives.md#two-stream-classes-stbcs-streaming-architecture) for the
  handler pattern that uses both classes together.
- **TGDimmerController** at `0x0088b7ec` — NiRTTI-registered. See
  [docs/engine/nirtti-factory-catalog.md](nirtti-factory-catalog.md).
- **TGFuzzyTriShape** — second NiRTTI-registered TG class; factory entry in
  [docs/engine/nirtti-factory-catalog.md](nirtti-factory-catalog.md).
- **TGOverlayController** — bare-string TG class but NOT NiRTTI-registered (uses a
  different runtime-type mechanism per nirtti-factory-catalog).

These four classes are siblings to the Ship hierarchy, not ancestors. Their vtables are not
written by any constructor in the Ship chain.

## Methodology

**Validation methodology (2026-05-28):** constructor-chain walk from Ship up through
TGObject, identifying each ctor's parent call + vtable write. The 9-vtable chain was
end-to-end confirmed by 8 ctor decompiles (TGObject ctor 0x006f0a70 → TGStreamedObject ctor
0x006f31a0 → TGStreamedObjectEx ctor 0x006f2590 → TGEventHandlerObject ctor 0x006d8f90 →
TGSceneObject ctor 0x004308e0 → ObjectClass ctor 0x00435030 → DamageableObject ctor
0x00591200 → Ship ctor 0x005abdc0). Each ctor calls its parent then writes its own vtable
address as `*this = &PTR_<vtable>`.

Universal slot patterns were identified by byte inspection:

- **Slot 0 (scalar_deleting_dtor)** — MSVC byte signature
  `56 8B F1 E8 ?? 00 00 00 F6 44 24 08 01 74 14 56` confirmed across 4 sampled classes.
- **Slot 1 (GetTypeID)** — 6-byte `mov eax, IMM ; ret` pattern returning class-specific
  type ID; verified across 4 classes (TGObject=0x02, TGStreamedObject=0x03,
  TGEventHandlerObject=0x0102, TGSceneObject=0x8002).
- **Slot 3 (DebugPrint)** and **Slot 8 (InvokePythonHandler)** — same single function
  address (`0x006f1650` and `0x006f15c0` respectively) appears in **all 9** hierarchy
  vtables. Inherited unchanged from TGObject.
- **Slots 5/6/7 (`__purecall` stub)** — bytes `6A 19 E8 69 13 00 00 59 C3` at
  `0x00859a0b`. Same stub as NiGeometry slot 49 (cross-anchored from
  netimmerse-vtables.md).

**Vtable boundary verification**: the Ship vtable at `0x00894340` ends at `0x008944AC`
(= 92 × 4 = 0x16C). The next 24 bytes are 6 float constants (75.0, 50.0, 500.0, 900.0,
0.8, 0.0049) — Ship-class data adjacent to the vtable, not vtable continuation.

**Per-slot v5 promotion path**: per-slot decompile sweep is the path to promote the ~100
pattern-extrapolated rows from `confidence: medium` to `confidence: high`. Currently
documentation debt; tracked in [v5-validation-status.md](v5-validation-status.md) §6.

## Open Questions and Documentation Debt

Surfaced to [v5-validation-status.md](v5-validation-status.md) §6 for the next validation
cycle:

1. **Class Type-ID numbering scheme** (`0x02` / `0x03` / `0x0102` / `0x8002`) — likely
   enumeration with bit-field semantics (low byte = sub-class, high byte = domain). Worth
   full cross-cataloging across all TG hierarchy and TG-sibling classes (e.g.,
   TGBufferStream's `0x32` tag). May warrant its own catalog doc.
2. **0x008963BC actual purpose** — ZERO xrefs but plausible vtable-shaped bytes; possibly
   linker artifact or partial overlap with adjacent `.rdata`. Low-stakes.
3. **~100 pattern-extrapolated slot rows** in derived-class vtables — per-slot decompile
   sweep is the promotion path. Tracked as documentation debt.
4. **Ship slot 22 (+0x58) = `0x00430d30` "AttachDefaultProperty"** — doc claim is
   plausible (calls `NiAVObject::AttachProperty(this+0x18, 0)`) but not directly verified
   this pass.
5. **WriteToStream's stream-sink vtable methods at +0x64/+0x84** — likely TGBufferStream
   `Serialize` family. Cross-link candidate when TGBufferStream's vtable is fully mapped.
