---
name: gameplay-foundation-damage-system-validation-20260528
description: v5 validation of docs/gameplay/damage-system.md — first gameplay-family doc. ~95% binary-correct call graph + offsets + constants. 5 corrections (4 minor wire/naming + 1 destruction-branch semantic), 4 clarifications, 2 ProcessDamage callers missing (Explosion deserialize FUN_00595890).
metadata:
  type: project
---

# Gameplay Foundation #1 — damage-system.md validation

**Date:** 2026-05-28
**Doc:** `docs/gameplay/damage-system.md` (285 lines)
**Family position:** Gameplay foundation #1 of N (gameplay = 4th and final v5 family; engine 10/10, protocol 22/22, networking 11/11 done same day).
**v5 status:** `partial` (high-confidence call graph + offsets + constants; 5 small corrections)

## TL;DR

This is the **central damage hub** for the gameplay family — same role as `wire-format-spec.md` for protocol. Doc is extraordinarily binary-faithful for the load-bearing claims (call graph, gate checks, offset table, magic constants, trace caller addresses). The 5 corrections are localized misstatements about destruction branching, lookup naming, and a missing ProcessDamage caller path.

## Verification dossier (per claim)

### Verified — CONFIRMED

| Claim | Address | Evidence |
|---|---|---|
| **DoDamage (0x00594020) gate `+0x18 != 0 && +0x140 != 0`** | 0x00594020 | Binary: `if ((iVar1 != 0) && (*(int *)(param_1 + 0x140) != 0))` — exact match |
| **DoDamage allocates 0x38 bytes via NiAlloc** | 0x00594020:FUN_00718cb0(0x38) | NiAlloc confirmed in nirtti-factory-validation memo |
| **DoDamage uses node+0x94 (radius), node+0x88/+0x8C/+0x90 (position)** | 0x00594020 | Decompile: `*(float*)(iVar1+0x94)`, `*(float*)(iVar1+0x88..0x90)` |
| **DoDamage uses rotation matrix at node+0x64** | 0x00594020:FUN_00813aa0(...,iVar4+100) | 100 decimal = 0x64; matches NiAVObject +0x64 rotation matrix (gamebryo-cross-reference confirmed) |
| **DoDamage_FromPosition (0x00593650) gates only on +0x18 (not +0x140)** | 0x00593650 | Binary: `if (iVar1 != 0)` — single gate; minor difference from DoDamage gate set |
| **DoDamage_CollisionContacts: raw \* 0.1 + 0.1, cap 0.5, max_damage=6000.0 (0x45BB8000)** | 0x005952D0 | Binary call: `FUN_00594020(&local_30, param_2, 0x45bb8000)`; constants 0x00893f28=0x3DCCCCCD=0.1f, 0x0088bf28=0x3DCCCCCD=0.1f, 0x008887a8=0x3F000000=0.5f all byte-confirmed |
| **CollisionResult layout +0x38=count, +0x40=energy** | 0x005952D0 | `*piVar1 = (int)param_2 + 0x38`; `*(float*)((int)param_2 + 0x40) / mass` |
| **CollisionDamageWrapper two-step: SubsystemDamageDistributor with &damage, then DoDamage_FromPosition with reduced damage** | 0x005B0060 | Disasm: `CALL 0x005afd70` then `CALL 0x00593650` with shared params; param_3 is by-ref then by-value; `RET 0xc` confirmed |
| **HostCollisionEffectHandler reads IsMultiplayer at entry** | 0x005AFAD0 | Binary: `(DAT_0097fa8a != '\\0') \|\| (DAT_0097fa89 == '\\0')` |
| **HostCollisionEffectHandler formula raw>0.01: scaled = raw\*900.0 + 500.0** | 0x005AFAD0 | 0x00888a78=0x3C23D70A=0.01f, 0x008944bc=0x44610000=900.0f, 0x008944b8=0x43FA0000=500.0f all byte-confirmed |
| **HostCollisionEffectHandler shieldScale=1.5 to SubsystemDamageDistributor** | 0x005AFAD0 | Binary: `FUN_005afd70(...,0x3fc00000,...)` = 1.5f hex; matches doc exactly |
| **HostCollisionEffectHandler distinct from DoDamage_CollisionContacts (different constants, no cap)** | 0x005AFAD0 vs 0x005952D0 | Confirmed via separate decompile; formulas differ |
| **ApplyWeaponDamage doubles damage (`+0x4C * 2.0`), halves radius (`+0x54 * 0.5`)** | 0x005AF420 | Binary: `*(float*)(param_1+0x4c) + *(float*)(param_1+0x4c)` (= 2x); `*(float*)(param_1+0x54) * _DAT_008887a8` (0.5f) |
| **ApplyWeaponDamage only fires for type 0 or 1 (phaser/torpedo)** | 0x005AF420 | Binary: `if ((*(int*)(param_1+0x2c) == 0) \|\| (*(int*)(param_1+0x2c) == 1))` |
| **WeaponHitInfo +0x2C type, +0x3C dir, +0x4C damage, +0x54 radius** | 0x005AF420 | All offsets touched in decompile |
| **ProcessDamage +0x1B8 and +0x1BC compared to 0x3F800000 (1.0f), SKIPS scale if exactly 1.0** | 0x00593E50 | Binary: `if (*(int*)(param_1+0x1b8) != 0x3f800000)` — important: 0.0 does NOT disable damage, it ZEROES it via multiply |
| **ProcessDamage subsystem loop walks +0x128 array of size +0x130** | 0x00593E50 | Binary: `*(int*)(*(int*)(param_1+0x128) + uVar1*4)`, `< *(uint*)(param_1+0x130)` |
| **FUN_004B1FF0 per-handler dispatch: shield via +0x20+0x18, hull via +0x1C +0x08 or +0x09** | 0x004B1FF0 | Binary: 4-line function exactly matches doc |
| **ProcessDamage hull damage via this+0x13C → FUN_00593EE0** | 0x00593E50 | Doc said hull damage forwarded via this+0x13C; binary calls FUN_00593EE0 unconditionally with the DamageVolume — actually FUN_00593EE0 reads param_2 (vol), not this+0x13C. Doc's framing slightly off but call site correct. |
| **ProcessDamage notification gate `DAT_0097fa89 == 0` (client only) and `DAT_008e5c1c != 0`** | 0x00593F30 | Binary: `((DAT_008e5c1c != '\\0') && (DAT_0097fa89 == '\\0'))` — confirmed |
| **Notification callback at 0x005927E0 stored at offset +0x30 of 0x38-byte object** | 0x00593F30 | Binary: `puVar2[0xc] = &LAB_005927e0` (offset 0xC * 4 = 0x30) |
| **DamageVolume ctor at FUN_004BBDE0 stores pos[2..4], radius[5], radius²[6]** | 0x004BBDE0 | Binary: `param_1[5] = param_3; param_1[6] = param_3 * param_3;` — pre-anchored leaf #20 claim verified |
| **DamageVolume vtable at 0x0088C6C4** | 0x004BBDE0 | Binary: `*param_1 = &PTR_LAB_0088c6c4` |
| **Ship+0xD8 is mass divisor (collision formula)** | 0x005952D0, 0x005AFAD0 | Both functions: `/ *(float*)(param_1+0xd8)` |
| **Explosion_Net reads objectID, looks up via FUN_00590A50 type 0x8007** | 0x006A0080, 0x00590A50 | FUN_00590A50 with param_1=0 filters via vtable[+8] for type 0x8007 |
| **DoDamage RET 0x0C, ProcessDamage RET 0x04, CollisionDamageWrapper RET 0x0C** | various | Doc's stack cleanup annotations match the decompiler signatures |
| **DoDamage callers: DoDamage_FromPosition, DoDamage_CollisionContacts, ApplyWeaponDamage** | get_function_callers(0x594020) | Exactly 3 callers — matches doc trace 765 = 122 + 107 + 536 |
| **Trace upstream addresses 0x005857FF (in FUN_005856D0), 0x005B4E3D (in Ship_SetupProperties)** | various | All resolve correctly to their parent functions |

### Corrections (C)

**C1 (M)** — **DestroyObject_Net branching is parent-vs-no-parent, NOT "ship vs non-ship"**
- Doc says: "If object has parent (`obj+0x20`): calls `parent->vtable[0x5C](objectID)`. If ship (type 0x8006): calls `vtable[0x138](1, 0)` to mark dead/hide. Then calls `vtable[0](1)` = destructor"
- Binary (0x006A01E0): `if (puVar3[8] == 0)` { /* no parent → call FUN_0059FD30 to get ship-like ptr, vtable[0x138](1,0), vtable[0](1) */ } `else` { /* parent != 0 → parent->vtable[0x5C](objID) */ }
- **The IF branch is `parent == 0`, the ELSE branch is `parent != 0`**. Type 0x8006 is not tested anywhere in this function. The `vtable[0x138]` / `vtable[0]` chain only executes when parent IS NULL.
- Object lookup is via `TGSceneGraph__GetObjectByID(0, objID)` — that lookup filters by `0x8003` (per its decompile), not `0x8007`.
- **Impact:** Doc's claim is reversed and conflates parent-presence with type. The actual destruction path: ships (no parent) hit vtable cleanup; sub-objects (have parent) delegate to parent.

**C2 (M)** — **ProcessDamage has 3 callers, not 1**
- Doc says: "all ProcessDamage calls originate from DoDamage" (line 218) and "DoDamage (0x0059418F) → ProcessDamage (765, always 1:1)"
- Binary `get_function_callers(0x00593E50)`: **3 callers** — DoDamage (0x00594020), **FUN_00595890** (explosion-damage deserialize/walker), Explosion_Net (0x006A0080).
- The "765 always 1:1" trace claim is correct **only for DoDamage's contribution**. FUN_00595890 is a TGStreamedObject ReadFromStream path that loops reading damage records and calls ProcessDamage per record — this is the broadcast-explosion side of opcode 0x29 propagation.
- **Impact:** Doc's call-graph diagram (line 32 onward "ALL DAMAGE FLOWS THROUGH: DoDamage") is **wrong as stated** — Explosion_Net bypasses DoDamage and calls ProcessDamage directly. Doc actually says this later in Section "Explosion_Net" (line 156): "Creates DamageVolume and calls ProcessDamage directly (bypasses DoDamage)" — but the ASCII art at the top contradicts it.

**C3 (M)** — **DestroyObject_Net object-lookup function naming**
- Doc says: "looks up object via `FUN_00434e00` (type 0x8003)"
- Binary: `FUN_00434E00` is already named `TGSceneGraph__GetObjectByID`. With param_1=0, it walks the scene-graph table and filters via vtable[+8] for type 0x8003. With non-zero param_1, it delegates to FUN_0040FDE0(0x8003,...).
- **Impact:** Trivial — doc names the address but missed Ghidra's existing label. Type 0x8003 = scene-graph-object filter is correct.

**C4 (m)** — **Explosion_Net wire layout is CompressedVector4 + 2x CF16, not "decompresses 3D position, reads damage values"**
- Doc says: "Reads objectID, decompresses 3D position, reads damage values"
- Binary: `CompressedVector4_ReadVirtual(&uStack_60, &uStack_5c, &uStack_58, 1)` reads CV4 (4-component, sign=1), then 2 CF16 shorts via TGBufferStream_swig_ReadShort + CompressedFloat16_Decode (damage, radius).
- **Impact:** Doc undersells precision — pre-anchored leaf #20/21 already documented this in protocol/cf16-explosion-encoding.md as the canonical wire format.

**C5 (m)** — **ProcessDamage notification call passes hardcoded 1, gate is INSIDE FUN_00593F30**
- Doc reads as if ProcessDamage itself checks IsHost. Actually ProcessDamage unconditionally calls `FUN_00593F30(1)` (param_2=1, meaning "send damage event"). The IsHost / global-enabled gate is inside FUN_00593F30 at 0x00593F30.
- **Impact:** Doc's accountability arrow is on the right function; the gate location was slightly mis-described.

### Clarifications (Clar)

**Clar1** — **DamageVolume layout** is `{vtable, ?, pos.x, pos.y, pos.z, radius, radius², sourceRef}` over 0x38 bytes. The "AABB" the doc mentions is constructed inside FUN_004BBEC0 (called at end of ctor). pre-anchored leaf #20 already covered the radius² precompute.

**Clar2** — **FUN_00593EE0 (hull damage receiver)** is a 4-line wrapper that increments DamageVolume refcount (`*(int*)(param_1+4)++`) and calls FUN_004B2120. The "+0x13C hull receiver" is actually unused inside FUN_00593EE0 — the call is unconditional, takes the volume as param. The doc's framing of "this+0x13C → FUN_00593EE0" is slightly misleading; the +0x13C field may be unused or read elsewhere.

**Clar3** — **WeaponHitHandler (0x005AF010) shield gate** is `param_2+0x58 == 0` (boolean flag), not a direct call to FUN_0056A690. The ray-ellipsoid test at 0x0056A690 IS used elsewhere in the shield path, but WeaponHitHandler itself just checks a precomputed flag.

**Clar4** — **`Ship+0x140` is a target-NiNode reference, not a generic "damage target"** — DoDamage uses it as `iVar4 = *(int*)(param_1+0x140)` then reads `*(float*)(iVar4 + 0x88..0x94)` (position + radius). This is the **ship's own target-reference NiNode** (probably the ship's own root or an attack-frame proxy). Naming "damage target reference" reads ambiguously.

### Risk (R)

**R1** — The ASCII call graph at lines 32-39 claims "ALL DAMAGE FLOWS THROUGH: DoDamage" but Section line 156 directly contradicts this for Explosion_Net. OpenBC implementers reading the graph alone will miss the Explosion direct-to-ProcessDamage path. See C2.

### Open Questions (OQ)

**OQ1** — What populates `ship+0x140` (the damage-target NiNode)? Doc's "Dedicated Server Implications" item 2 says "must verify this is populated by DeferredInitObject. If NULL, all damage is silently dropped" — but the binary doesn't tell us the writer. Need a write-xref hunt.

**OQ2** — What populates `ship+0x128` / `ship+0x130` (subsystem damage handler array)? Distinct from the +0x284 linked list. Doc implies both must be populated for damage to work, but doesn't name the constructor. Likely Ship__SetupProperties at 0x005B3FB0 or a sub-function.

**OQ3** — Does FUN_00595890 (Explosion ReadFromStream that bulk-calls ProcessDamage) fire on the dedicated server, or is it client-only deserialization? It's a TGStreamedObject hook so likely client receive path — but worth confirming via trace.

### Historical (H)

The "Stock Dedi Trace Data" sections (lines 202-272) read like a frozen runtime artifact. All cited functions exist and the math (765 = 536 + 122 + 107) is self-consistent. These trace observations are time-stamped 2026-era stock-dedi runs — best treated as historical evidence for cross-referencing.

The "Functions that NEVER fire on the host" list (lines 261-268) is observation-based, not gate-derived. The conclusion is correct (host SENDS these opcodes, doesn't receive), but it's not a static binary fact — it's a behavioral assertion best validated against the message-trace.

## Completeness scores

All functions tested in worker classification (pre-v5 naming, magic numbers unnamed, struct accesses unresolved):
- DoDamage (0x00594020): score=0.0, fixable=124, struct=15 — high churn potential
- ProcessDamage (0x00593E50): score=3.8, effective=8.6, fixable=91 — closest to v5 baseline
- CollisionDamageWrapper (0x005B0060): score=7.5, effective=15.0 — small function, clean
- HostCollisionEffectHandler (0x005AFAD0): score=0.0, fixable=113 — already named but full of magic constants
- Explosion_Net (0x006A0080): score=0.0, fixable=110
- DestroyObject_Net (0x006A01E0): score=0.0, fixable=113

None promoted to high-completeness state. Doc validation here = anchor-and-verify, not annotation.

## v5 final status

Recommend marking doc as `partial` — the cross-checked call graph, offset table, magic constants, and trace data are LOAD-BEARING and CORRECT. The 2 medium corrections (C1 destruction branching, C2 Explosion direct-to-ProcessDamage) are localized fixes that don't undermine the central architecture. The 4 minor corrections are wire-format precision improvements.

The doc is the **central damage hub** for the gameplay family and survives validation strongly — far better than the equivalent pre-v5 protocol hub (wire-format-spec.md) did. Worth migrating to high-confidence status with C1+C2 patches applied.
