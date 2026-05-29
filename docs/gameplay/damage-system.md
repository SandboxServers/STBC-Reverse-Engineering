> [docs](../README.md) / [gameplay](README.md) / damage-system.md

---
title: Bridge Commander Damage System
type: reference + explanation
audience: re-engineer
validated: 2026-05-28
methodology: FUNCTION_DOC_WORKFLOW_V5
binary:
  name: stbc.exe
  size: 6182400
  base: 0x00400000
status: partial
evidence:
  - claim: "DoDamage at 0x00594020 is the central damage dispatcher; gates on this+0x18 != 0 AND this+0x140 != 0; allocates a 0x38-byte DamageVolume via NiAlloc and calls ProcessDamage"
    address: 0x00594020
    function: DoDamage
    completeness: 0.0
    confidence: high
    note: "Binary: `if ((iVar1 != 0) && (*(int *)(param_1 + 0x140) != 0))` matches doc gate exactly. Allocation `FUN_00718cb0(0x38)` is NiAlloc (cross-anchored from nirtti-factory-catalog)."
  - claim: "DoDamage reads target NiNode at this+0x140, then position node+0x88/+0x8C/+0x90 and bounding-sphere radius node+0x94"
    address: 0x00594020
    function: DoDamage
    completeness: 0.0
    confidence: high
    note: "Decompile reads *(float*)(iVar1+0x94) for radius and the three position floats at +0x88..+0x90."
  - claim: "DoDamage uses rotation matrix at node+0x64 (3x3) to transform hit direction world -> source local -> target local"
    address: 0x00594020
    function: DoDamage
    completeness: 0.0
    confidence: high
    note: "FUN_00813aa0 invoked with iVar4+100 (= +0x64); +0x64 is the NiAVObject rotation matrix slot per docs/engine/gamebryo-cross-reference.md."
  - claim: "ProcessDamage at 0x00593E50 has 3 callers: DoDamage (0x00594020), Explosion_Net (0x006A0080), and FUN_00595890 (Explosion TGStreamedObject ReadFromStream walker)"
    address: 0x00593E50
    function: ProcessDamage
    completeness: 3.8
    effective: 8.6
    confidence: high
    note: "get_function_callers(0x00593E50) returns 3 entries. C2 — the doc's ASCII graph said `ALL DAMAGE FLOWS THROUGH DoDamage`; that claim is wrong. The trace ratio `765 = 536 + 122 + 107` applies to DoDamage's contribution only."
  - claim: "ProcessDamage scales damage by this+0x1B8 (radius multiplier) and this+0x1BC (falloff multiplier); the scale step is SKIPPED when the value equals 0x3F800000 (1.0f exactly); 0.0 ZEROES damage via multiply"
    address: 0x00593E50
    function: ProcessDamage
    completeness: 3.8
    effective: 8.6
    confidence: high
    note: "Binary: `if (*(int*)(param_1+0x1b8) != 0x3f800000)`. Clar2 — doc's `0.0 = effectively immune` is true in effect but the mechanism is `zero via multiply`, not `bypass via guard`."
  - claim: "ProcessDamage subsystem-damage loop walks an array at this+0x128 with count at this+0x130; this is a DIFFERENT structure from the +0x284 linked list used by state replication"
    address: 0x00593E50
    function: ProcessDamage
    completeness: 3.8
    effective: 8.6
    confidence: high
    note: "Binary: `*(int*)(*(int*)(param_1+0x128) + uVar1*4)`, loop count `< *(uint*)(param_1+0x130)`. OQ2 — populator not located this pass."
  - claim: "FUN_004B1FF0 per-handler dispatch: shield path via handler+0x20 then +0x18 flag -> FUN_004b4b40 (shield intersection); hull path via handler+0x1C with flags +0x08 or +0x09 -> FUN_004bd9f0 (AABB overlap)"
    address: 0x004B1FF0
    function: FUN_004B1FF0
    confidence: high
    note: "4-line function exactly matches the doc's per-handler table."
  - claim: "ProcessDamage unconditionally invokes FUN_00593F30(1) for damage notification; the IsHost / event-enabled gate is INSIDE FUN_00593F30 at 0x00593F30, not at the call site"
    address: 0x00593F30
    function: FUN_00593F30
    confidence: high
    note: "C5 — Binary at 0x00593F30: `((DAT_008e5c1c != '\\0') && (DAT_0097fa89 == '\\0'))`. Notification callback stored at offset +0x30 of a 0x38-byte object as `&LAB_005927e0`."
  - claim: "DAT_008e5c1c is the global damage-event enable flag; DAT_0097fa89 is the IsHost byte"
    address: 0x00593F30
    function: FUN_00593F30
    confidence: high
    note: "Both globals consulted in the same boolean expression inside the notification gate."
  - claim: "DoDamage_FromPosition at 0x00593650 gates only on this+0x18 != 0 (single gate), computes hit direction from world-position delta, and calls DoDamage"
    address: 0x00593650
    function: DoDamage_FromPosition
    confidence: high
    note: "Single-point collision caller; called by CollisionDamageWrapper (0x005B0060)."
  - claim: "DoDamage_CollisionContacts at 0x005952D0 loops over CollisionResult contact points and calls DoDamage per contact with max_damage=6000.0f (0x45BB8000); per-contact scale = raw * 0.1 + 0.1, hard cap 0.5"
    address: 0x005952D0
    function: DoDamage_CollisionContacts
    confidence: high
    note: "Binary call site `FUN_00594020(&local_30, param_2, 0x45bb8000)`; CollisionResult layout +0x38=count, +0x2C=contacts, +0x40=energy."
  - claim: "DAT_00893F28 = 0.1f (DoDamage_CollisionContacts scale base)"
    address: 0x00893F28
    function: DoDamage_CollisionContacts
    confidence: high
    note: "Byte-confirmed: 0x3DCCCCCD = 0.1f."
  - claim: "DAT_0088BF28 = 0.1f (DoDamage_CollisionContacts scale offset)"
    address: 0x0088BF28
    function: DoDamage_CollisionContacts
    confidence: high
    note: "Byte-confirmed: 0x3DCCCCCD = 0.1f."
  - claim: "DAT_008887A8 = 0.5f (DoDamage_CollisionContacts hard cap; also reused as the 0.5 multiplier for ApplyWeaponDamage radius)"
    address: 0x008887A8
    function: DoDamage_CollisionContacts
    confidence: high
    note: "Byte-confirmed: 0x3F000000 = 0.5f."
  - claim: "DAT_00888860 = 1.0f (reference constant)"
    address: 0x00888860
    function: shared
    confidence: high
    note: "Byte-confirmed: 0x3F800000 = 1.0f."
  - claim: "DAT_00888A78 = 0.01f (HostCollisionEffectHandler dead-zone threshold)"
    address: 0x00888A78
    function: HostCollisionEffectHandler
    confidence: high
    note: "Byte-confirmed: 0x3C23D70A = 0.01f."
  - claim: "DAT_008944BC = 900.0f (HostCollisionEffectHandler host scale)"
    address: 0x008944BC
    function: HostCollisionEffectHandler
    confidence: high
    note: "Byte-confirmed: 0x44610000 = 900.0f."
  - claim: "DAT_008944B8 = 500.0f (HostCollisionEffectHandler host base)"
    address: 0x008944B8
    function: HostCollisionEffectHandler
    confidence: high
    note: "Byte-confirmed: 0x43FA0000 = 500.0f."
  - claim: "max_damage 6000.0f inlined at DoDamage_CollisionContacts as 0x45BB8000"
    address: 0x005952D0
    function: DoDamage_CollisionContacts
    confidence: high
    note: "Binary push of immediate 0x45BB8000 to DoDamage."
  - claim: "shieldScale = 1.5f passed by HostCollisionEffectHandler to SubsystemDamageDistributor"
    address: 0x005AFAD0
    function: HostCollisionEffectHandler
    confidence: high
    note: "Binary: `FUN_005afd70(..., 0x3fc00000, ...)` = 1.5f."
  - claim: "CollisionDamageWrapper at 0x005B0060 is the top-level collision entry; calls SubsystemDamageDistributor(0x005AFD70) with &damage (shields modify in-place), then DoDamage_FromPosition(0x00593650) with reduced damage"
    address: 0x005B0060
    function: CollisionDamageWrapper
    confidence: high
    note: "Disasm sequence: CALL 0x005afd70 then CALL 0x00593650 with shared params; param_3 is by-ref then by-value; RET 0xc confirmed."
  - claim: "HostCollisionEffectHandler at 0x005AFAD0 fires on event ET_HOST_OBJECT_COLLISION (0x008000FC) and reads IsMultiplayer DAT_0097FA8A at entry"
    address: 0x005AFAD0
    function: HostCollisionEffectHandler
    confidence: high
    note: "Binary entry gate: `(DAT_0097fa8a != '\\0') || (DAT_0097fa89 == '\\0')`."
  - claim: "HostCollisionEffectHandler formula: raw = energy / mass / contactCount; if raw > 0.01: scaled = raw * 900.0 + 500.0; calls SubsystemDamageDistributor(ship, dir, &scaled, 1.5, attacker, 1)"
    address: 0x005AFAD0
    function: HostCollisionEffectHandler
    confidence: high
    note: "Distinct from DoDamage_CollisionContacts: different constants (900x+500 vs 0.1x+0.1), no hard cap, output 500+ HP absolute. Avg 6008.7 HP per subsystem in stock-dedi traces."
  - claim: "ApplyWeaponDamage at 0x005AF420 only processes type 0 (phaser) or type 1 (torpedo); doubles damage (hit+0x4C * 2.0) and halves radius (hit+0x54 * 0.5)"
    address: 0x005AF420
    function: ApplyWeaponDamage
    confidence: high
    note: "Binary type filter: `if ((*(int*)(param_1+0x2c) == 0) || (*(int*)(param_1+0x2c) == 1))`; halve uses DAT_008887A8."
  - claim: "WeaponHitHandler at 0x005AF010 dispatches weapon hits; shield gate is precomputed flag param_2+0x58 == 0, NOT a direct ray-test call"
    address: 0x005AF010
    function: WeaponHitHandler
    confidence: high
    note: "Clar3 — the ray-ellipsoid test at 0x0056A690 lives in the shield path but is invoked elsewhere; this handler checks a cached flag."
  - claim: "Explosion_Net at 0x006A0080 (opcode 0x29) reads objectID, CompressedVector4 (sign=1), and 2x CF16 shorts (damage, radius); looks up target via FUN_00590A50 type 0x8007; allocates DamageVolume and calls ProcessDamage directly (BYPASSES DoDamage)"
    address: 0x006A0080
    function: Explosion_Net
    completeness: 0.0
    confidence: high
    note: "C4 — wire format is CV4 + 2x CF16; see docs/protocol/cf16-explosion-encoding.md for the canonical wire spec. Direct call to ProcessDamage is the second of the 3 ProcessDamage callers (see C2)."
  - claim: "DestroyObject_Net at 0x006A01E0 (opcode 0x14) branching is parent-vs-no-parent, NOT ship-vs-non-ship"
    address: 0x006A01E0
    function: DestroyObject_Net
    completeness: 0.0
    confidence: high
    note: "C1 — Binary: `if (puVar3[8] == 0)` tests the parent slot. NO parent: call FUN_0059FD30, then vtable[0x138](1,0), then vtable[0](1). HAS parent: parent->vtable[0x5C](objID). Type 0x8006 is never tested in this function."
  - claim: "DestroyObject_Net looks up objects via TGSceneGraph__GetObjectByID (FUN_00434E00) with param_1=0; type filter is 0x8003 (scene-graph object)"
    address: 0x00434E00
    function: TGSceneGraph__GetObjectByID
    confidence: high
    note: "C3 — function is already named in the Ghidra DB; type filter is 0x8003, not 0x8007 as some leaf docs imply for receiver-side lookups."
  - claim: "DamageVolume (a.k.a. ExplosionDamage in protocol-leaf docs) ctor at FUN_004BBDE0 builds a 0x38-byte struct with layout {vtable +0, ?, pos.x +0x08, pos.y +0x0C, pos.z +0x10, radius +0x14, radius^2 +0x18, sourceRef +0x1C, bbox..+0x38}"
    address: 0x004BBDE0
    function: DamageVolume_Ctor
    confidence: high
    note: "Cross-anchored from protocol leaf #20 (cf16-precision-analysis.md) and leaf #21 (cf16-explosion-encoding.md). vtable at 0x0088C6C4. radius^2 precomputed at field[6]. AABB built inside FUN_004BBEC0."
  - claim: "NiAlloc at 0x00718CB0 is the engine allocator used for DamageVolume (0x38 bytes)"
    address: 0x00718CB0
    function: NiAlloc
    confidence: high
    note: "Cross-anchored from nirtti-factory-catalog.md."
  - claim: "Ship+0x140 is a NiNode reference (target-frame) consumed by DoDamage; reads +0x88/+0x8C/+0x90 (position), +0x94 (radius), +0x64 (rotation matrix)"
    address: 0x00594020
    function: DoDamage
    confidence: high
    note: "Clar4 — calling this a generic 'damage target' obscures that it is a NiAVObject-derived NiNode (probably the ship's own target-frame proxy). OQ1 — populator not located this pass."
  - claim: "Ship+0x1B8 is damage radius multiplier (1.0f = pass-through, 0.0 zeroes damage); Ship+0x1BC is damage falloff multiplier (same semantics)"
    address: 0x00593E50
    function: ProcessDamage
    confidence: high
    note: "Both compared against 0x3F800000 immediate in the scale-skip branch."
  - claim: "DamageableObject HP slot at offset +0x14C (cross-anchored from protocol leaf #18)"
    address: null
    function: DamageableObject
    confidence: medium
    note: "Anchor in docs/protocol/objnotfound-requestobj-enterset-wire-format.md (protocol leaf #18). Not re-read this pass; carried by reference."
  - claim: "Stock-dedi caller-chain trace addresses verified: 0x005857FF (physics tick), 0x005B4E3D (Ship_AddSubsystem in SetupProperties), 0x0069F33E (MPG_ObjectProcessor), 0x006E0D05 (InvokeHandler -> WeaponHitHandler)"
    address: 0x005857FF
    function: trace anchors
    confidence: high
    note: "All four addresses resolve to their parent functions per get_function_callers checks. Trace math 765 = 536 weapon + 122 collision_contacts + 107 collision_position consistent with the 3-caller set on DoDamage (and is DoDamage's contribution to the 3-caller total on ProcessDamage — see C2)."
companions:
  - docs/protocol/collision-effect-protocol.md
  - docs/protocol/objnotfound-requestobj-enterset-wire-format.md
  - docs/protocol/cf16-explosion-encoding.md
  - docs/networking/ship-death-lifecycle.md
  - docs/engine/gamebryo-cross-reference.md
  - docs/gameplay/collision-shield-interaction.md
  - docs/gameplay/collision-detection-system.md
  - docs/gameplay/shield-system.md
---

> [!NOTE]
> **Gameplay-family damage hub doc — survives v5 well**. ZERO formula corrections; every magic constant (10 of them) byte-confirmed; 765-event trace math (= 536 weapon + 122 collision_contacts + 107 collision_position) verified via `get_function_callers`. 5 localized corrections (2 medium + 3 minor) + 4 clarifications. Cross-anchored from protocol leaves #15 / #18 / #20 / #21 + networking leaf #11. Status `partial` — three open questions about populators (Ship+0x140, Ship+0x128/+0x130) and FUN_00595890's run path remain unanswered this pass. See [v5-evidence-header.md](../guides/v5-evidence-header.md) for what the frontmatter means.

# Bridge Commander Damage System

Reverse-engineered from stbc.exe via Ghidra decompilation and runtime function tracing (stock dedi observer build). The core call graph, gate checks, offset table, and magic constants are load-bearing and verified. See the v5 NOTE above for the validation summary and the per-correction sections (C1–C5) for the five localized fixes applied this pass.

## Call Graph Overview

```
COLLISION INPUT:
  CollisionDamageWrapper (0x005B0060)                                [v5-validated 2026-05-28]
    +-> SubsystemDamageDistributor (0x005AFD70)     <- shield absorption + subsystem damage
    |     walks ship+0x284 list, modifies damage     (reduces &damage in-place)
    +-> DoDamage_FromPosition (0x00593650) ---+     <- gets REDUCED damage
                                              |
  DoDamage_CollisionContacts (0x005952D0) ---+
    +-> loops over contact points, calls DoDamage

WEAPON INPUT:
  WeaponHitHandler (0x005AF010)                     [v5-validated 2026-05-28]
    +-> shield gate: param_2+0x58 == 0 (precomputed flag, NOT direct ray-test)
    |     72% stopped here (shield absorbed)
    +-> FUN_005afd70 (same SubsystemDamageDistributor as collision)
    +-> ApplyWeaponDamage (0x005AF420) ----+
          (damage * 2.0, radius * 0.5)     |
                                            |
DAMAGE-MAKER FUNNEL:                        |
  DoDamage (0x00594020) <---DoDamage_FromPosition, DoDamage_CollisionContacts, ApplyWeaponDamage
    +-> ProcessDamage (0x00593E50)

EXPLOSION INPUT (network opcode 0x29):
  Explosion_Net (0x006A0080)                        [v5-validated 2026-05-28]
    +-> reads objectID, CompressedVector4 (sign=1), 2x CF16 (damage, radius)
    +-> looks up target via FUN_00590A50 (type 0x8007)
    +-> calls ProcessDamage DIRECTLY (BYPASSES DoDamage)   <-- see C2

BROADCAST-EXPLOSION DESERIALIZE PATH:
  FUN_00595890 (Explosion ReadFromStream walker)
    +-> loops reading damage records, calls ProcessDamage per record  <-- see C2

THE THREE CALLERS OF ProcessDamage:                 [v5-validated 2026-05-28]
  ProcessDamage (0x00593E50)
    <- DoDamage (0x00594020)         <- 765 calls per stock-dedi session
    <- Explosion_Net (0x006A0080)    <- per-opcode-0x29 receive
    <- FUN_00595890 (deserialize)    <- bulk-replay of explosion damage records

INSIDE ProcessDamage:
  ProcessDamage (0x00593E50)
    +- if this+0x1B8 != 1.0f: damage = damage * this+0x1B8    (scale-skip on exactly 1.0f)
    +- if this+0x1BC != 1.0f: falloff = falloff * this+0x1BC
    +- SUBSYSTEM LOOP: this+0x128 (handler array), this+0x130 (count)
    |   +- per handler (FUN_004b1ff0):
    |       +- shield path: handler+0x20 -> FUN_004b4b40 (shield intersection)
    |       +- hull path: handler+0x1C -> FUN_004bd9f0 (AABB overlap test)
    +- hull damage forwarded through this+0x13C-related path -> FUN_00593ee0
    +- damage notification: calls FUN_00593f30(1) UNCONDITIONALLY
        +- IsHost / event-enabled gate lives INSIDE FUN_00593f30 (NOT at call site, see C5)
        +- gate: (DAT_008e5c1c != 0) && (DAT_0097fa89 == 0)  (event-enabled AND client)
        +- creates 0x38-byte object, callback at +0x30 = &LAB_005927e0

DESTRUCTION (network opcode 0x14):
  DestroyObject_Net (0x006A01E0)                    [v5-validated 2026-05-28]
    +- reads objectID from stream
    +- looks up object via TGSceneGraph__GetObjectByID (FUN_00434E00, type 0x8003)
    +- if obj->parent == 0 (NO parent):              <-- see C1
    |     - call FUN_0059FD30
    |     - vtable[0x138](1, 0)  (mark dead / hide)
    |     - vtable[0](1)         (destructor with cleanup)
    +- else (HAS parent):
          - parent->vtable[0x5C](objectID)
```

## C1 — DestroyObject_Net branching is parent-vs-no-parent

The pre-v5 prose claimed: "If object has parent (`obj+0x20`): calls `parent->vtable[0x5C](objectID)`. If ship (type 0x8006): calls `vtable[0x138](1, 0)` to mark dead/hide. Then calls `vtable[0](1)` = destructor."

That conflates two unrelated tests. The binary at FUN_006A01E0 tests one thing: `if (puVar3[8] == 0)` — the parent slot. The `vtable[0x138](1,0)` then `vtable[0](1)` chain executes when the parent IS NULL, not on a type check. **Type 0x8006 is never tested in this function.**

**Corrected behavior:**

```c
obj = TGSceneGraph__GetObjectByID(0, objectID);    // type 0x8003 filter
if (obj == NULL) return;
if (obj->parent == NULL) {                          // <-- the actual branch test
    FUN_0059FD30(...);                              //     parent-less path
    obj->vtable[0x138](1, 0);                       //     mark dead / hide
    obj->vtable[0](1);                              //     destructor with cleanup
} else {
    obj->parent->vtable[0x5C](objectID);            //     delegate to parent
}
```

**OpenBC implication:** sub-objects (which have a parent — e.g., docked shuttles, weapon attachments) delegate destruction to the parent's slot 0x5C. Top-level objects (ships, free-floating debris — no parent) hit the vtable cleanup chain. Don't gate on type 0x8006; gate on parent presence.

## C2 — ProcessDamage has 3 callers, not 1; Explosion bypasses DoDamage

The pre-v5 ASCII graph said "ALL DAMAGE FLOWS THROUGH: DoDamage" but the body text (Explosion_Net section) said "calls ProcessDamage directly (bypasses DoDamage)". Both claims cannot be true.

The binary truth: `get_function_callers(0x00593E50)` returns **3 callers**:

| Caller | Address | Role |
|---|---|---|
| DoDamage | 0x00594020 | Collision and weapon path. 765 calls/session = 536 weapon + 122 collision_contacts + 107 collision_position. |
| Explosion_Net | 0x006A0080 | Opcode 0x29 receive path. Allocates DamageVolume, calls ProcessDamage directly. |
| FUN_00595890 | 0x00595890 | Explosion `TGStreamedObject` ReadFromStream walker. Loops reading damage records, calls ProcessDamage per record. (See OQ3 for run-path.) |

The "765 always 1:1" trace ratio is correct **for DoDamage's contribution only**. It does NOT cover Explosion_Net's direct calls or FUN_00595890's loop. The call-graph diagram above has been amended to show Explosion_Net + FUN_00595890 branching directly into ProcessDamage.

**OpenBC implication:** if you build a clean-room DoDamage that funnels through gates `+0x18` and `+0x140`, you will NOT trap explosion damage. Explosion_Net and FUN_00595890 build their own DamageVolume and skip both gates.

## C3 — TGSceneGraph__GetObjectByID is already a named function

The pre-v5 doc referenced `FUN_00434e00` as the object lookup. That function is already labelled `TGSceneGraph__GetObjectByID` in the Ghidra DB. With `param_1 == 0`, it walks the scene-graph table and filters via `vtable[+8]` for type `0x8003`. With non-zero `param_1`, it delegates to `FUN_0040FDE0(0x8003, ...)`.

All references to FUN_00434E00 in this doc now use the named symbol.

## C4 — Explosion_Net wire format is CV4 + 2x CF16

The pre-v5 doc said Explosion_Net (opcode 0x29) "decompresses 3D position, reads damage values". The binary uses a more specific format:

```
objectID                     u32                              (lookup target via FUN_00590A50, type 0x8007)
position                     CompressedVector4 (sign=1)       (CompressedVector4_ReadVirtual)
damage                       u16 -> CF16 decode               (TGBufferStream_swig_ReadShort + CompressedFloat16_Decode)
radius                       u16 -> CF16 decode               (TGBufferStream_swig_ReadShort + CompressedFloat16_Decode)
```

See [docs/protocol/cf16-explosion-encoding.md](../protocol/cf16-explosion-encoding.md) for the canonical wire spec and the per-byte breakdown (protocol leaf #21).

## C5 — Notification IsHost gate is INSIDE FUN_00593F30

The pre-v5 doc framing read as if `ProcessDamage` itself checked `IsHost`. Actually `ProcessDamage` calls `FUN_00593F30(1)` unconditionally (the `1` means "send damage event"). The gate lives inside FUN_00593F30 at 0x00593F30:

```c
// inside FUN_00593F30 (called by ProcessDamage)
if ((DAT_008e5c1c != 0) && (DAT_0097fa89 == 0)) {
    // event-enabled AND IsHost == 0 (i.e. client)
    obj = NiAlloc(0x38);
    // ... build object ...
    obj[0x30] = &LAB_005927e0;     // callback (DamageTickUpdate at 0x005927E0)
    // ... post / queue ...
}
```

So the gate is correctly described in this doc as "client only, when global damage events are enabled" — but the **call site** is unconditional; the **gate location** is inside FUN_00593F30, not at the ProcessDamage call site.

**OpenBC implication:** if your damage receiver consults the `(event_enabled && !is_host)` predicate at the call site, you'll match the pre-v5 doc framing but you won't match the binary's flow if you ever decide to fire FUN_00593F30 from a different caller — the gate stays inside the callee. Keep the gate co-located with the notification builder.

## Function Reference

### DoDamage (0x00594020)   [v5-validated 2026-05-28]
- **Convention**: `__thiscall(ECX=ship, float* hitDir, float damage, DWORD radius)`
- **Stack cleanup**: `RET 0x0C` (callee cleans 3 params)
- Central damage dispatcher for collision and weapon paths. NOT a dispatcher for explosions — see C2.
- **Gate checks** (damage silently dropped if either fails):
  - `this+0x18` (NiNode) must be non-NULL — ship must have a loaded model
  - `this+0x140` (target NiNode reference, see Clar4) must be non-NULL
- Allocates a 0x38-byte DamageVolume via `NiAlloc` (`FUN_00718cb0(0x38)`), built by `FUN_004BBDE0`:
  - Transforms hit direction from world space -> source model local -> target model local
  - Uses NiNode bounding sphere radius (`node+0x94`) for scaling
  - Uses rotation matrix at `node+0x64` (3x3) for coordinate transforms
  - Builds AABB via `FUN_004BBEC0`
- Calls ProcessDamage with the DamageVolume.

### ProcessDamage (0x00593E50)   [v5-validated 2026-05-28]
- **Convention**: `__thiscall(ECX=ship, DamageVolume* dmgVol)`
- **Stack cleanup**: `RET 0x04`
- Distributes damage from the DamageVolume to subsystems and hull. **Three callers**, not one (see C2).
- **Resistance scaling** (per-ship multipliers, see Clar2):
  - `this+0x1B8`: damage radius multiplier — compared to `0x3F800000` (1.0f). If not equal, damage is multiplied. Value 0.0 ZEROES the damage via multiply (effect: immune); value 1.0 short-circuits the multiply.
  - `this+0x1BC`: damage falloff multiplier — same semantics
- **Subsystem damage loop**:
  - Array at `this+0x128`, count at `this+0x130`
  - **This is a SEPARATE structure from the subsystem linked list at `this+0x284`** (see OQ2 for the populator)
  - Per handler (`FUN_004b1ff0`):
    - Shield check: `handler+0x20` -> if `+0x18` flag set, `FUN_004b4b40` (shield intersection)
    - Hull/component check: `handler+0x1C` -> if flags `+0x08` or `+0x09` set, `FUN_004bd9f0` (AABB overlap)
  - AABB overlap test checks all 6 planes of the damage volume vs subsystem bounding box
- **Hull damage**: forwarded through `this+0x13C`-related path -> `FUN_00593EE0` (4-line wrapper that increments DamageVolume refcount at `vol+0x04` and calls `FUN_004B2120`)
- **Notification**: calls `FUN_00593F30(1)` unconditionally; gate lives inside the callee (see C5)

### DoDamage_FromPosition (0x00593650) — Collision Caller 1
- **Convention**: `__thiscall(ECX=ship, NiNode* collider, float damage, DWORD radius)`
- **Stack cleanup**: `RET 0x0C`
- Single-point collision damage. Gates only on `this+0x18 != 0` (single gate — distinct from DoDamage's two-gate set).
- Computes hit direction from world-position delta, transforms to local coordinates, calls DoDamage.
- Called by `CollisionDamageWrapper` (0x005B0060).

### DoDamage_CollisionContacts (0x005952D0) — Collision Caller 2
- **Convention**: `__thiscall(ECX=ship, CollisionResult* contacts)`
- **Stack cleanup**: `RET 0x04`
- Multi-contact-point collision damage. Distributes collision energy across contact points.
- **Per-contact damage formula** (constants byte-confirmed):
  ```
  raw    = (collision.energy / ship.mass) / contact_count
  scaled = raw * 0.1 + 0.1       (DAT_00893f28 = 0.1, DAT_0088bf28 = 0.1)
  if (scaled > 0.5) scaled = 0.5  (hard cap: DAT_008887a8 = 0.5)
  ```
- Output range: 0.1 to 0.5 (fractional of max_damage)
- Calls DoDamage once per contact point with `max_damage = 6000.0f` (immediate `0x45BB8000`)
- CollisionResult layout: `+0x38` = contact count, `+0x2C` = contact point array, `+0x40` = total energy

### CollisionDamageWrapper (0x005B0060)
- **Convention**: `__thiscall(ECX=ship, int collider, float energy, float damage)`
- **Stack cleanup**: `RET 0x0C`
- Top-level entry point for collision events.
- **Two-step process**: calls SubsystemDamageDistributor (0x005AFD70) with `&damage` — shield facings absorb damage, reducing it in-place — then calls DoDamage_FromPosition with the **reduced** damage.
- See [collision-shield-interaction.md](collision-shield-interaction.md) for full decompiled flow.

### HostCollisionEffectHandler (0x005AFAD0) — Collision Effect Path
- **Convention**: reads `IsMultiplayer` byte (DAT_0097FA8A) at entry
- Called via event `ET_HOST_OBJECT_COLLISION` (0x008000FC), fired after CollisionEffect opcode 0x15
- **Per-contact damage formula** (constants byte-confirmed):
  ```
  raw = (collisionEnergy / ship.mass) / contactCount
  if (raw > 0.01):                          (DAT_00888a78 = 0.01 dead zone)
      scaled = raw * 900.0 + 500.0          (DAT_008944bc = 900.0, DAT_008944b8 = 500.0)
      SubsystemDamageDistributor(ship, contactDir, &scaled, shieldScale=1.5, attacker, flags=1)
  ```
- Output range: 500.0+ (absolute HP damage — NOT fractional)
- Each subsystem receives the **full** per-contact damage; overflow is accumulated and written back to `*damage` after all subsystems processed
- **Distinct from DoDamage_CollisionContacts**: different constants (900x+500 vs 0.1x+0.1), different output ranges, no hard cap
- Verified via FTrace: avg=6008.7 max=13220.3 per-subsystem in live stock-dedi traces
- See [collision-effect-protocol.md](../protocol/collision-effect-protocol.md) for full handler chain

### ApplyWeaponDamage (0x005AF420) — Weapon Path
- **Convention**: `__thiscall(ECX=ship, WeaponHitInfo* hit)`
- **Stack cleanup**: `RET 0x04`
- Only processes phaser (type 0) and torpedo (type 1)
- **Doubles damage** (`hit+0x4C * 2.0`) and **halves radius** (`hit+0x54 * DAT_008887A8`, where `DAT_008887A8 = 0.5f`)
- WeaponHitInfo layout: `+0x2C` = type, `+0x3C` = direction[3], `+0x4C` = damage, `+0x54` = radius

### WeaponHitHandler (0x005AF010) — Weapon Dispatcher
- Shield gate is a **precomputed flag** at `param_2+0x58 == 0` (see Clar3) — NOT a direct call to the ray-ellipsoid test at 0x0056A690
- 28% of weapon hits pass the shield gate in stock-dedi traces (1939 hits -> 536 ApplyHullDamage calls)
- See [weapon-firing-mechanics.md](weapon-firing-mechanics.md) for the full firing pipeline

### DestroyObject_Net (0x006A01E0) — Opcode 0x14   [v5-validated 2026-05-28]
- **Convention**: `__cdecl(void* stream)`, `RET 0x04`
- Reads objectID from network stream, looks up via `TGSceneGraph__GetObjectByID(0, objID)` (FUN_00434E00, type 0x8003 filter — see C3)
- **Branch test is parent-vs-no-parent** (see C1):
  - If `obj->parent == NULL`: calls `FUN_0059FD30(...)`, then `vtable[0x138](1, 0)` (mark dead / hide), then `vtable[0](1)` (destructor with cleanup)
  - If `obj->parent != NULL`: calls `parent->vtable[0x5C](objectID)` (delegate)
- Type 0x8006 is **NOT** tested in this function — the pre-v5 doc's type test was a misread.

### Explosion_Net (0x006A0080) — Opcode 0x29   [v5-validated 2026-05-28]
- **Convention**: `__cdecl(void* stream)`, `RET 0x04`
- Wire format (see C4): objectID, CompressedVector4 (sign=1), 2x CF16 shorts (damage, radius)
- Looks up target via `FUN_00590A50` (type 0x8007)
- Allocates a 0x38-byte DamageVolume via NiAlloc, builds via `FUN_004BBDE0`
- **Calls ProcessDamage DIRECTLY — bypasses DoDamage** (see C2)
- See [docs/protocol/cf16-explosion-encoding.md](../protocol/cf16-explosion-encoding.md) for the canonical wire spec.

### DamageVolume (a.k.a. ExplosionDamage) — Shared Struct   [v5-validated 2026-05-28]
- 0x38-byte struct, ctor at `FUN_004BBDE0`, vtable at `0x0088C6C4`
- Layout: `{vtable +0, refcount? +4, pos.x +0x08, pos.y +0x0C, pos.z +0x10, radius +0x14, radius^2 +0x18, sourceRef +0x1C, bbox.min +0x20, bbox.max +0x2C}`
- `radius^2` precomputed in field [6] for fast distance-test math
- AABB built inside `FUN_004BBEC0` (called at end of ctor)
- Allocated via NiAlloc (`FUN_00718CB0(0x38)`)
- Cross-anchored from [docs/protocol/cf16-precision-analysis.md](../protocol/cf16-precision-analysis.md) (protocol leaf #20) and [docs/protocol/cf16-explosion-encoding.md](../protocol/cf16-explosion-encoding.md) (protocol leaf #21).

## Ship Object Damage-Related Offsets

| Offset | Type | Description |
|--------|------|-------------|
| `+0x18` | NiNode* | Scene graph root — must be non-NULL for DoDamage to work |
| `+0xD8` | float | Ship mass (used in collision damage formula) |
| `+0x128` | void** | Subsystem damage handler array (for ProcessDamage). OQ2: populator unknown. |
| `+0x130` | int | Subsystem damage handler count |
| `+0x13C` | void* | Hull damage-receiver reference (consumed by the path leading into FUN_00593EE0) |
| `+0x140` | NiNode* | Target-frame NiNode reference — must be non-NULL for DoDamage. OQ1: populator unknown. |
| `+0x14C` | float | DamageableObject HP slot (cross-anchored from protocol leaf #18) |
| `+0x1B8` | float | Damage radius multiplier (1.0 = pass-through; 0.0 zeroes damage via multiply) |
| `+0x1BC` | float | Damage falloff multiplier (same semantics) |
| `+0x1C4` | void* | Active damage notification handler (if non-NULL, one already pending) |
| `+0x280` | int | Subsystem count (linked list, separate from `+0x128` array) |
| `+0x284` | void* | Subsystem linked list HEAD (for state updates, separate from `+0x128`) |

## Conditions That Disable Damage

| Condition | Location | Effect |
|-----------|----------|--------|
| `this+0x18 == NULL` | DoDamage gate | No NiNode -> DoDamage path silently dropped (Explosion_Net path NOT affected — bypasses) |
| `this+0x140 == NULL` | DoDamage gate | No target NiNode -> DoDamage path silently dropped (Explosion_Net path NOT affected) |
| `this+0x128 == NULL` or `+0x130 == 0` | ProcessDamage | No subsystem handlers -> subsystem damage loop is a no-op |
| `this+0x13C == NULL` | ProcessDamage | No hull receiver -> hull damage skipped |
| `this+0x1B8 == 0.0` | ProcessDamage | Damage zeroed via multiply (see Clar2) — not bypassed via guard |
| `this+0x1BC == 0.0` | ProcessDamage | Falloff zeroed via multiply |
| Shield active (`handler+0x20+0x18 != 0`) | Per-subsystem handler | Shields absorb damage before hull |
| Hull damage flags (`+0x08`, `+0x09`) both zero | AABB handler | Subsystem won't take damage |
| `DAT_0097fa89 == 1` (IsHost) | Notification callback gate (inside FUN_00593F30, see C5) | Damage applied but NO event callback fires (by design) |
| `DAT_008e5c1c == 0` | Notification callback gate (inside FUN_00593F30) | Global damage events disabled |

## Dedicated Server Implications

### What Must Be Set for Damage to Work
1. **`ship+0x18` (NiNode)**: Our DeferredInitObject creates ships with NIF models, so this is set. Verified working for collision damage.
2. **`ship+0x140` (target NiNode reference)**: Must verify this is populated by DeferredInitObject. If NULL, the DoDamage path is silently dropped with no error or log message. **NOTE**: Explosion_Net bypasses this gate (see C2) — so server-side explosion damage will still apply even if `+0x140` is NULL.
3. **`ship+0x128`/`+0x130` (subsystem damage handler array)**: This is a DIFFERENT structure from the subsystem linked list at `+0x284`. The `+0x284` list is for state serialization; the `+0x128` array is for damage distribution. Both must be populated. (See OQ2.)
4. **`ship+0xD8` (mass)**: Used in collision damage formula. If zero, division by zero.
5. **`ship+0x1B8` and `+0x1BC` (resistance/falloff)**: Should be 1.0 for normal damage. If our ship creation leaves these as 0.0, the ship is effectively invulnerable (because the value zeroes damage via multiply, see Clar2).

### Damage Notification is Client-Only (By Design)
The damage event callback gate lives inside `FUN_00593F30` (see C5) and predicates on `(DAT_008e5c1c != 0) && (DAT_0097fa89 == 0)` — event-enabled AND IsHost == 0. On the dedicated server (IsHost == 1), `ProcessDamage` still calls `FUN_00593F30(1)`, but the gate inside suppresses the notification builder. Damage is applied to subsystem health values; no notification callback fires. Stock behavior — clients get visual/audio feedback, server stays silent.

## Stock Dedi Trace Data (Baseline)

> Trace observations are time-stamped 2026-era stock-dedi runs. All cited addresses verified this pass via `get_function_callers`; the math `765 = 536 + 122 + 107` is self-consistent. Best treated as **historical evidence for cross-referencing**, not as live-binary facts.

### Session 1: Solo Asteroid Ramming (1 player, ~60s)

Sovereign ramming asteroids at 100% and 125% speed, then switching to Nebula:

```
Ship 1 (Sovereign): Ship_AddSubsystem x33 (from 0x005B4E3D)
Ship 2 (Nebula):    Ship_AddSubsystem x31 (from 0x005B4E3D)

DoDamage callers:
  0x005936E5 (inside DoDamage_FromPosition) — single-point collision
  0x005953E1 (inside DoDamage_CollisionContacts) — multi-contact collision

ProcessDamage callers:
  0x0059418F (inside DoDamage) — only DoDamage's contribution; Explosion_Net path
                                  and FUN_00595890 path did not fire this session
```

### Session 2: Multi-Player Combat (3 players, ~15 min, 11 ship spawns)

Full combat session with weapons fire, collisions, and ship destructions/respawns.

**Verified caller chains (return addresses):** [v5-validated 2026-05-28]
```
Physics tick loop:
  0x005857FF -> CheckCollision (79,605 calls)

Collision damage path:
  0x00608DF2 -> CollisionDamageWrapper (107 calls)
  CollisionDamageWrapper (0x005B0093) -> DoDamage_FromPosition (107, 1:1)
  0x005952BE -> DoDamage_CollisionContacts (122 calls)

Weapon damage path:
  InvokeHandler (0x006E0D05) -> WeaponHitHandler (1,939 calls)
  WeaponHitHandler (0x005AF145) -> ApplyHullDamage (536 calls, 28% pass shields)
  ApplyHullDamage (0x005AF44F) -> DoDamage (536)

Central damage:
  DoDamage total: 765 = 536 weapon + 122 collision_contacts + 107 collision_position
  DoDamage (0x0059418F) -> ProcessDamage (765, always 1:1 — DoDamage's contribution only;
                                            ProcessDamage actually has 3 callers, see C2)

Ship creation:
  0x0069F33E -> MPG_ObjectProcessor (11 calls)
  MPG_ObjectProcessor (0x0069F6B4) -> ObjectFactory (11, always 1:1)
  ObjectFactory (0x005A1FDE) -> TypeFactory (11 of 2498 total)
  0x005B4E3D -> Ship_AddSubsystem (331 total, sole caller)
```

**Key ratios (high confidence):**
- Collision check -> actual damage: **0.3%** (79,605 checks -> 229 damage events)
- Weapon hit -> shield penetration: **28%** (1,939 hits -> 536 pass shields)
- All DoDamage calls produce exactly 1 ProcessDamage call from THAT caller (the 1:1 ratio is per-caller; ProcessDamage's total caller count is 3 — see C2)

**Per-ship subsystem counts (empirical, 11 ships):**
24, 26, 29, 31, 31, 33, 34, 34 observed — varies by ship class, always from single caller 0x005B4E3D.

**Ship lifecycle (11 ObjectFactory calls for ~3 players):**
Ships are destroyed and respawned as entirely new objects through the same ObjectFactory path. No special respawn function exists — it's destroy + create new. See [docs/networking/ship-death-lifecycle.md](../networking/ship-death-lifecycle.md) for the full lifecycle.

**Functions that NEVER fire on the host (by design, observation-based):**
- `Ship_WriteStream` (0x0057A280) — not part of network path, only disk serialization
- `DestroyObject_Net` (0x006A01E0) — host SENDS opcode 0x14, doesn't receive it
- `Explosion_Net` (0x006A0080) — host SENDS opcode 0x29, doesn't receive it
- `CreateNetworkEvent` (0x006A1360) — not used during gameplay
- `FindNetObjByID` (0x006A19FC) — not used during gameplay
- `FireEvent` fires exactly **once** per session (game start), then never again

**Functions that fire rarely on the host:**
- `SendNetworkObject`: 2 calls total (object registration at join)
- `GetPlayerSlot`: 5 calls (during player join flow)
- `FindPlayerByNetID`: 6 calls (during player join flow)

## Upstream Caller Addresses (Not Hooked)

These addresses call into our hooked functions but are not themselves hooked. Important for understanding the full chain. [v5-validated 2026-05-28]

| Address | Calls | Context |
|---------|-------|---------|
| `0x005857FF` | CheckCollision | Physics tick — collision detection loop |
| `0x00608DF2` | CollisionDamageWrapper | Physics collision response handler |
| `0x005952BE` | DoDamage_CollisionContacts | Collision contact processor wrapper |
| `0x005B4E3D` | Ship_AddSubsystem | Inside SetupProperties (sole subsystem creator) |
| `0x0069F33E` | MPG_ObjectProcessor | MultiplayerGame message dispatcher |
| `0x006E0D05` | WeaponHitHandler | InvokeHandler (event system dispatch) |

## Open Questions

- **OQ1**: What writes `Ship+0x140` (the damage-target NiNode)? The doc's Dedicated Server Implications item 2 says "must verify this is populated by DeferredInitObject. If NULL, all damage is silently dropped" — but the binary doesn't reveal the writer. **Needs write-xref search.**
- **OQ2**: What populates `Ship+0x128` / `Ship+0x130` (subsystem damage handler array)? Distinct from the `+0x284` linked list. Both must be populated for damage to work but the constructor is unidentified. **Likely Ship__SetupProperties (0x005B3FB0) or a callee** — needs trace.
- **OQ3**: Does `FUN_00595890` (Explosion ReadFromStream / bulk-ProcessDamage) fire on the dedicated server, or is it client-only? It is a `TGStreamedObject` deserialization hook — likely client receive path. The third ProcessDamage caller's run-path needs trace confirmation.

## Companions

- [docs/protocol/collision-effect-protocol.md](../protocol/collision-effect-protocol.md) — Opcode 0x15 wire format + handler validation (leaf #15)
- [docs/protocol/objnotfound-requestobj-enterset-wire-format.md](../protocol/objnotfound-requestobj-enterset-wire-format.md) — DamageableObject HP slot anchor (leaf #18)
- [docs/protocol/cf16-precision-analysis.md](../protocol/cf16-precision-analysis.md) — CF16 + DamageVolume struct (leaf #20)
- [docs/protocol/cf16-explosion-encoding.md](../protocol/cf16-explosion-encoding.md) — Explosion wire spec, CF16 caller list (leaf #21)
- [docs/networking/ship-death-lifecycle.md](../networking/ship-death-lifecycle.md) — Ship death: Explosion + respawn, DestroyObject NOT used
- [docs/engine/gamebryo-cross-reference.md](../engine/gamebryo-cross-reference.md) — NiAVObject offset table (rotation matrix at +0x64, position +0x88, radius +0x94)
- [docs/gameplay/collision-shield-interaction.md](collision-shield-interaction.md) — Two-step collision-shield damage flow
- [docs/gameplay/collision-detection-system.md](collision-detection-system.md) — Physics tick collision pipeline
- [docs/gameplay/shield-system.md](shield-system.md) — Shield mechanics referenced from the weapon shield gate
