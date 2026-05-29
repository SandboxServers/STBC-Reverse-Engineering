> [docs](../README.md) / [gameplay](README.md) / collision-detection-system.md

---
title: Bridge Commander Collision Detection System
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
  - claim: "ProximityManager constructor at 0x005A7420 installs vtable PTR_LAB_008942d4; struct is 0x64 bytes; one ProximityManager per game Set (accessible via Set+0xF4 / GetProximityManager())"
    address: 0x005A7420
    function: ProximityManager_Ctor
    confidence: high
    note: "Ctor pattern confirmed (writes vtable at this+0)."
  - claim: "ProximityManager vtable at 0x008942D4 (first slot 0x005A9A20)"
    address: 0x008942D4
    function: ProximityManager_vtable
    confidence: high
    note: "Byte-confirmed."
  - claim: "ObjectClass::CheckCollision at 0x005671D0 implements the hierarchical bounding-sphere test (Tier 2). 12 callers observed (not 1 as prior doc implied) — see OQ1"
    address: 0x005671D0
    function: CheckCollision
    confidence: high
    note: "get_function_callers returns 12 entries including FUN_005856d0, recursion, FUN_00489910, FUN_004fecf0, FUN_00501510, FUN_00501610 ×2, FUN_00544200, FUN_00538c90, FUN_005930a0."
  - claim: "ProximityManager::Update at 0x005A83A0 runs per frame; single caller is SimulationTick (FUN_0040FFB0)"
    address: 0x005A83A0
    function: ProximityManager_Update
    confidence: high
    note: "Single inbound xref from SimulationTick."
  - claim: "SweepAxis at 0x005A8500 implements bubble-sort incremental update of the sorted endpoint array per axis; uses byte flag at endpoint+0x4 to discriminate min vs max endpoints"
    address: 0x005A8500
    function: SweepAxis
    confidence: high
    note: "Swap logic reads `*(char*)(iVar9 + 4)` — the is_min/is_max byte flag at endpoint+0x4 (see C2 for corrected endpoint layout)."
  - claim: "Dispatcher FUN_005A8810 routes a candidate pair via three IsType (vtable+0x8) checks against class IDs 0x8125 (Ship/DamageableObject), 0x8009 (Torpedo), 0x8007 (PhysicsObject)"
    address: 0x005A8810
    function: DispatchCollisionPair
    confidence: high
    note: "Three sequential `(*(code**)(*ptr + 8))(typeID)` calls in decompile. Pattern Note (see body): the decompile-twin-call artifact means real asm is `check obj_a then obj_b` so 3 type-checks × 2 objects = 6 sequential virtual-call lines in decomp."
  - claim: "HandleShipShipCollision at 0x005A61C0 reads bounding-sphere radii via vtable+0xE4 (GetModelBound, NiBound at returned ptr+0xC); computes gap = distance - radius_a - radius_b; posts collision when gap < 0.0"
    address: 0x005A61C0
    function: HandleShipShipCollision
    confidence: high
    note: "vtable+0xE4 confirmed; comparison is `if (DAT_00888b54 <= gap)` and `DAT_00888b54 = 0.0f` (see C1) — so the test is literally `gap >= 0` (separating) else (gap < 0) PostCollisionEvent."
  - claim: "HandlePhysicsCollision at 0x005A88E0 uses vtable+0x148 (BeginIntersectionTest) and vtable+0x150 (PerformIntersection, detailed mesh); reads two collision-enabled bytes (host vs client) — see Clar1"
    address: 0x005A88E0
    function: HandlePhysicsCollision
    confidence: high
    note: "Both 0x008e5f58 (client path) and 0x008e5f59 (host path) read in the same dispatch — Clar1."
  - claim: "Torpedo_DetectCollision at 0x00579010 invokes vtable+0x140 (BeginIntersection) and vtable+0x144 (RefinementIntersection); refinement loop iterates up to 2 times"
    address: 0x00579010
    function: Torpedo_DetectCollision
    confidence: high
    note: "Up-to-2 iteration loop confirmed; vtable+0x50 TriggerDestruction also called on impact."
  - claim: "CheckSphereIntersection at 0x00567640 calls GetWorldTranslation (vtable+0x94) twice, ComputeDistance (FUN_00410570), and GetCombinedRadius (FUN_00567190); tests `distance < combined_radius`"
    address: 0x00567640
    function: CheckSphereIntersection
    confidence: high
    note: "All four call sites confirmed in decompile."
  - claim: "GetCombinedRadius at 0x00567190 returns NiNode+0x4C (NiBound radius at NiBound+0xC since NiBound starts at NiNode+0x40) × this+0x98 (scale) × this+0x34 (radiusMult); returns DAT_00888b54 = 0.0f when dead/disabled (zero collision radius means broad-phase always rejects this object's sphere)"
    address: 0x00567190
    function: GetCombinedRadius
    confidence: high
    note: "Dead-object path confirmed (also see C1 — DAT_00888b54 was misdocumented as 'large sentinel' but is actually 0.0f; zero-radius semantic still works: bounding-sphere test `radius < distance` is always true for radius=0)."
  - claim: "CollisionFlagsCompatible at 0x005A7890 implements bitmask test: ((b>>1) & a & 0x2A) | ((a>>1) & b & 0x2A); 0x2A = 0b00101010 = mask for 'collides WITH type X' bits (bits 1,3,5)"
    address: 0x005A7890
    function: CollisionFlagsCompatible
    confidence: high
    note: "Bit pattern confirmed; flag byte lives at object+0x3C; Python accessor ObjectClass_GetCollisionFlags reads this byte."
  - claim: "ProximityManager_AddObject at 0x005A7640 computes AABB via FUN_00436130 then inserts 6 endpoints (min/max × 3 axes) into per-axis sorted arrays via FUN_005A8CC0 (binary-search insert)"
    address: 0x005A7640
    function: ProximityManager_AddObject
    confidence: high
  - claim: "ProcessAllPairs at 0x005A8740 walks the circular doubly-linked list of collision pairs at ProximityManager+0xC; dispatches each pair via FUN_005A8810"
    address: 0x005A8740
    function: ProcessAllPairs
    confidence: high
  - claim: "DoDamage_CollisionContacts at 0x005952D0 computes per-contact damage = clamp(((force / mass) / num_contacts) × 0.1 + 0.1, 0, 0.5) × 6000.0 max; calls DoDamage per contact"
    address: 0x005952D0
    function: DoDamage_CollisionContacts
    confidence: high
    note: "Cross-anchored from gameplay foundation #1 (damage-system.md). All 5 constants byte-confirmed (DAT_00893F28=0.1f, DAT_0088BF28=0.1f, DAT_008887A8=0.5f, DAT_00888860=1.0f, 6000.0f=0x45BB8000 inline)."
  - claim: "BuildCollisionPairsForSets at 0x005856D0 enumerates per-Set object lists at +0x2B4/+0x2B8/+0x2BC/+0x2D4 (4 set fields), feeds candidates into CheckCollision"
    address: 0x005856D0
    function: BuildCollisionPairsForSets
    confidence: high
  - claim: "ComputeDistance at 0x00410570 returns sqrt((bx-ax)^2 + (by-ay)^2 + (bz-az)^2) plus per-modifier adjustments looped at set+0xF8 (count) / set+0xFC (array)"
    address: 0x00410570
    function: ComputeDistance
    confidence: high
  - claim: "GetAABB at 0x00436130 fetches object AABB via vtable+0xE8 then UNIONS (expands) the result with the custom-bounds box at this+0x40..+0x54 if this+0x3D flag is set — see C3 (prior doc said 'clamp', actual operation is union/expand)"
    address: 0x00436130
    function: GetAABB
    confidence: high
    note: "Math is `min(out_min, custom_min)` / `max(out_max, custom_max)` — that EXPANDS the AABB to include the custom box, it does not clamp it. The pseudocode was correct; only the inline comment word 'clamp' is wrong (C3)."
  - claim: "PostCollisionEvent at 0x005A63A0 allocates a 0x30-byte TGObjPtrEvent (SWIG class string at 0x008D8594 = 'TGObjPtrEvent', _p_TGObjPtrEvent at 0x008D85A4)"
    address: 0x005A63A0
    function: PostCollisionEvent
    confidence: high
    note: "Cross-anchored from protocol leaf #13 (tgobjptrevent-class.md). The 'CollisionEvent' name applies to TWO distinct things in this doc — see Clar2."
  - claim: "Sweep-and-prune endpoint layout (CORRECTED): { float value @+0, byte is_min_flag @+4, padding @+5..+7, int object_index @+8 } — 12 bytes total. No 'next_ptr' field; sorted array is contiguous (next entry at +0xC)"
    address: 0x005A8500
    function: SweepAxis
    confidence: high
    note: "C2 — prior doc said `{ float value, int next_ptr, int object_index }`. Real layout has byte flag at +0x4 (consumed by `*(char*)(iVar9 + 4)` in SweepAxis). FUN_005A8CC0 binary-search insert confirms same layout."
  - claim: "DAT_00888B54 = 0.0f (NOT 'large float sentinel' as prior doc claimed) — used as both the gap >= 0 separating-spheres test (HandleShipShipCollision) and zero-radius return for dead objects (GetCombinedRadius)"
    address: 0x00888B54
    function: shared
    confidence: high
    note: "C1 [HIGH] — byte-read at 0x00888b54 = 00 00 00 00. Doc's narrative text ('if gap < 0 spheres overlap') was correct; only the Global Variables table row labelling it a 'large float sentinel' was wrong."
  - claim: "DAT_008942DC = 1.0e-7f (~near-zero velocity threshold squared; HandlePhysicsCollision rest-check)"
    address: 0x008942DC
    function: HandlePhysicsCollision
    confidence: high
    note: "Byte-confirmed: 0x33D6BF95 = 1.0e-7f."
  - claim: "DAT_0089054C = 1.2f (per-object collision cooldown timer threshold at object+0x98; in CheckCollision)"
    address: 0x0089054C
    function: CheckCollision
    confidence: high
    note: "Byte-confirmed: 0x3F99999A = 1.2f. Separate mechanism from CLAUDE.md 'collision rate limiting (ship+0xEC)'."
  - claim: "DAT_00893F28 = 0.1f (DoDamage_CollisionContacts damage scale factor)"
    address: 0x00893F28
    function: DoDamage_CollisionContacts
    confidence: high
    note: "Byte-confirmed: 0x3DCCCCCD = 0.1f. Cross-anchored from gameplay foundation #1."
  - claim: "DAT_0088BF28 = 0.1f (DoDamage_CollisionContacts damage base offset)"
    address: 0x0088BF28
    function: DoDamage_CollisionContacts
    confidence: high
    note: "Byte-confirmed: 0x3DCCCCCD = 0.1f. Cross-anchored from gameplay foundation #1."
  - claim: "DAT_008887A8 = 0.5f (DoDamage_CollisionContacts per-contact damage clamp)"
    address: 0x008887A8
    function: DoDamage_CollisionContacts
    confidence: high
    note: "Byte-confirmed: 0x3F000000 = 0.5f. Cross-anchored from gameplay foundation #1."
  - claim: "DAT_00888860 = 1.0f (normalization constant used in contact-point local-coordinate transform)"
    address: 0x00888860
    function: DoDamage_CollisionContacts
    confidence: high
    note: "Byte-confirmed: 0x3F800000 = 1.0f."
  - claim: "max_damage = 6000.0f passed as inline immediate 0x45BB8000 to DoDamage from DoDamage_CollisionContacts"
    address: 0x005952D0
    function: DoDamage_CollisionContacts
    confidence: high
    note: "Cross-anchored from gameplay foundation #1 — same call site `FUN_00594020(&local_30, param_2, 0x45bb8000)`."
  - claim: "DAT_008E5F58 = collision-enabled byte (CLIENT path); read in HandlePhysicsCollision when DAT_0097FA89 (IsHost) == 0"
    address: 0x008E5F58
    function: HandlePhysicsCollision
    confidence: high
    note: "Clar1 — only the client-path byte was documented previously. Set via Python SWIG `ProximityManager_SetPlayerCollisionsEnabled` (SWIG class string at 0x00920074)."
  - claim: "DAT_008E5F59 = collision-enabled byte (HOST path); read in HandlePhysicsCollision when DAT_0097FA89 (IsHost) != 0; same byte as 'Settings byte 1' in opcode 0x00 (network-synced game-rule)"
    address: 0x008E5F59
    function: HandlePhysicsCollision
    confidence: high
    note: "Clar1 — newly documented this pass. `cVar2 = DAT_008e5f59; if (DAT_0097fa89 == 0) cVar2 = DAT_008e5f58; if (cVar2 == 0) skip;`. The host-path byte is what gets sent in Settings packet (per CLAUDE.md 'Settings byte 1')."
  - claim: ".bss collision-pair storage: 0x0098D328 collisionPairCount, 0x0098D32C list head, 0x0098D330 list tail, 0x0098D334 free pool, 0x0098D338 chunk list, 0x0098D33C pool size (init 2)"
    address: 0x0098D328
    function: shared
    confidence: high
    note: "All six addresses byte-confirmed (0 in image since .bss)."
  - claim: "SWIG class string 'CollisionEvent' at 0x008E584C (88-byte physics struct, owns contact list, fed to DoDamage_CollisionContacts) — distinct from the 'CollisionEvent' wire-event posted via TGObjPtrEvent (see Clar2)"
    address: 0x008E584C
    function: shared
    confidence: high
    note: "Clar2 — disambiguates two entities sharing the name."
  - claim: "SWIG class string 'ProximityManager' at 0x00912A18 (exposes AddObject, RemoveObject, Update)"
    address: 0x00912A18
    function: shared
    confidence: high
  - claim: "SWIG class string 'ProximityManager_SetPlayerCollisionsEnabled' at 0x00920074 (Python entry point to toggle DAT_008E5F58/0x59)"
    address: 0x00920074
    function: shared
    confidence: high
    note: "Clar1 cross-link — see OQ2 for the open question on which byte this actually writes."
  - claim: "Class IDs verified by use: 0x8125 (Ship/DamageableObject), 0x8009 (Torpedo), 0x8007 (PhysicsObject), 0x800E (ExclusionList event), 0x00008124 (CollisionEvent class wire-side per protocol leaf #15)"
    address: 0x005A8810
    function: DispatchCollisionPair
    confidence: high
    note: "Dispatcher decomp + cross-anchor from collision-effect-protocol.md (leaf #15)."
  - claim: "Event codes verified by use: 0x00800050 ET_OBJECT_COLLISION, 0x008000FC ET_HOST_OBJECT_COLLISION, 0x00800053 ET_COLLISION_BROADCAST, 0x0000800E exclusion-list event"
    address: 0x005A63A0
    function: PostCollisionEvent
    confidence: high
    note: "0x00800050 cross-anchored from protocol leaf #15."
  - claim: "Vtable slot convention (per-class GetWorldTranslation, GetModelBound, etc.): +0x50 TriggerDestruction (torpedo), +0x58 per-frame Update (ship type 0x8125), +0x94 GetWorldTranslation -> Vec3*, +0xE4 GetModelBound -> NiBound* (radius at +0xC), +0xE8 GetBoundingBox(min,max), +0x140 Torpedo BeginIntersection, +0x144 Torpedo RefinementIntersection, +0x148 Physics BeginIntersectionTest, +0x150 Physics PerformIntersection"
    address: 0x008942D4
    function: shared
    confidence: high
    note: "All slots cross-checked against FUN_005A83A0, FUN_005A61C0, FUN_005A88E0, FUN_00579010, FUN_00567640."
  - claim: "NiBound at NiNode+0x40 with radius at NiBound+0xC (so radius read as NiNode+0x4C); 4 floats: center.xyz then radius"
    address: 0x00567190
    function: GetCombinedRadius
    confidence: high
    note: "Per Gamebryo cross-reference — NiNode+0x40 is the NiBound struct. GetCombinedRadius reads `*(float*)(this->niNode + 0x4C)` for the radius."
  - claim: "Host-side gap < 26.0f threshold (DAT at 0x008955C8) gates server validation of received CollisionEffect (opcode 0x15) — cross-anchored from protocol leaf #15"
    address: 0x008955C8
    function: shared
    confidence: high
    note: "Cross-anchored from collision-effect-protocol.md (leaf #15). Server rejects collision events when reported gap >= 26.0f."
companions:
  - docs/protocol/collision-effect-protocol.md
  - docs/protocol/tgobjptrevent-class.md
  - docs/gameplay/damage-system.md
  - docs/gameplay/collision-shield-interaction.md
  - docs/gameplay/collision-rate-limiting.md
---

> [!NOTE]
> **Among the strongest pre-v5 gameplay docs**. 34 function addresses verified, all class IDs/vtable slots/15 .rdata constants byte-confirmed. 3 detail corrections (C1 HIGH: DAT_00888B54 is 0.0f not "large float sentinel" — narrative was right, only the Global Variables row wrong; C2 MED: sweep-and-prune endpoint struct layout uses byte flag at +0x4 not next-pointer; C3 LOW: FUN_00436130 is union/expand not "clamp") + 2 clarifications (Clar1: dual host/client collision-enabled bytes 0x008E5F58/0x008E5F59; Clar2: two distinct entities share the name "CollisionEvent") + 2 OQs. Cross-anchored against protocol leaf #15 (CollisionEffect) and gameplay foundation #1 (damage-system).

# Collision Detection System - Full Reverse Engineering Analysis

Complete analysis of the physics-level collision detection algorithm in Star Trek: Bridge
Commander. This covers how the engine determines two objects have collided, BEFORE any
damage calculation occurs. The 3-tier architecture (broad-phase sweep-and-prune → hierarchical
bounding sphere → narrow-phase per-type) survives v5 validation cleanly; see the NOTE above
for the five localized fixes applied this pass and the per-correction sections (C1–C3 +
Clar1–Clar2) for the details.

## Architecture Overview                                       [v5-validated 2026-05-28]

Bridge Commander uses a **three-tier collision detection system**:

1. **Broad Phase**: `ProximityManager` -- 3-axis sweep-and-prune (sort-and-sweep) AABB
2. **Hierarchical Bounding Sphere**: `ObjectClass::CheckCollision` (FUN_005671d0) -- recursive bounding sphere tests
3. **Narrow Phase**: Varies by object type -- ship-ship, ship-torpedo, ship-environment

The collision system is NOT part of NetImmerse's built-in collision (NiCollisionSwitch exists
but is only used for toggling). Instead, Bridge Commander implements a completely custom
collision detection pipeline at the game layer. The tiers correspond to distinct call sites
(not marketing language) — sweep-and-prune yields candidate pairs, CheckCollision applies the
bounding-sphere hierarchy, narrow-phase dispatcher routes by RTTI.

## System Manager: ProximityManager                            [v5-validated 2026-05-28]

**Class**: ProximityManager (custom, not NI)
**Size**: 0x64 (100 bytes)
**Vtable**: 0x008942D4
**Constructor**: FUN_005a7420
**Collision-enabled bytes**: DAT_008E5F58 (client path) and DAT_008E5F59 (host path) — see Clar1 below
**SWIG class strings**: "ProximityManager" @ 0x00912A18, "ProximityManager_SetPlayerCollisionsEnabled" @ 0x00920074

### ProximityManager Layout

```
Offset  Size  Type         Field                    Notes
------  ----  ----         -----                    -----
0x00    4     void**       vtable                   0x008942D4
0x04    4     int          (unknown)                Init 0
0x08    1     byte         (flag)
0x0C    4     void*        collision_pairs_list     Circular doubly-linked list of active pairs
0x10    4     int          num_collision_pairs      Active pair count
0x14    20    AxisSort[0]  x_axis_sort              Axis 0 sort structure (5 DWORDs each)
0x28    20    AxisSort[1]  y_axis_sort              Axis 1 sort structure
0x3C    20    AxisSort[2]  z_axis_sort              Axis 2 sort structure
0x50    4     int          object_count             Number of tracked objects
0x54    4     void*        object_table             Array of object entries (0x1C bytes each)
0x58    4     void*        overlap_tracker          Tracks axis overlap counts between pairs
0x5C    4     void*        (reserved)
0x60    4     void*        (reserved)
```

### ProximityManager Ownership

- Each game `Set` holds a ProximityManager at Set+0xF4 (accessed via `GetProximityManager()`)
- Objects are added via `ProximityManager_AddObject` (FUN_005a7640)
- Updated every frame via `ProximityManager_Update` (FUN_005a83a0)

## Tier 1: Broad Phase -- Sweep-and-Prune                      [v5-validated 2026-05-28]

### Overview

The ProximityManager implements **3-axis sweep-and-prune** (also called sort-and-sweep),
a well-known broad-phase collision detection algorithm.

### How It Works

**Initialization** (FUN_005a7640 - AddObject):

1. Compute AABB for the object: calls `FUN_00436130` (GetBoundingBox, vtable+0xE8)
2. The AABB produces 6 floats: min(x,y,z), max(x,y,z)
3. For each of the 3 axes, insert min and max interval endpoints into sorted lists
4. Each endpoint entry is 12 bytes (CORRECTED layout — see C2 below):
   `{ float value @+0, byte is_min_flag @+4, padding @+5..+7, int object_index @+8 }`
5. Insertion uses `FUN_005a8cc0` (binary-search insert) which maintains the sorted order

**Per-Frame Update** (FUN_005a83a0):

1. For each object: recompute AABB (`FUN_005a8470`)
2. Update endpoint values in the sorted lists
3. Call `FUN_005a8500` (SweepAxis) for each of the 3 axes (indices 0, 1, 2)
4. Call `FUN_005a8740` (ProcessCollisionPairs) for all overlapping pairs

### C2 — Endpoint Struct Layout (CORRECTED)

The prior doc claimed `{ float value, int next_ptr, int object_index }` with a "next pointer"
chain. That is wrong. The real layout consumed by `FUN_005A8500` and `FUN_005A8CC0` is:

```
+0x00  float  value
+0x04  byte   is_min_flag   (0 = start/min endpoint, nonzero = end/max endpoint)
+0x05  byte[3] padding
+0x08  int    object_index  (into ProximityManager+0x54 object table)
```

There is no `next_ptr` field. The sorted array is contiguous — the next entry is at +0xC in
the same array. The flag at +0x4 is what `*(char*)(iVar9 + 4)` reads in the SweepAxis swap
logic; it discriminates min-endpoint from max-endpoint so the algorithm can detect
"interval START overlapping END" vs "intervals SEPARATING" during a swap.

### Sweep-and-Prune Algorithm (FUN_005a8500)

The sweep step uses **bubble-sort-like** incremental update:

```c
// Pseudocode for SweepAxis(axis_index)
axis = &manager->axis_sort[axis_index * 5];
repeat {
    swapped = false;
    for (i = 0; i < axis->count - 1; i++) {
        if (axis->endpoints[i+1].value < axis->endpoints[i].value) {
            // Swap the two endpoints
            SwapEndpoints(axis, i, i+1);
            swapped = true;

            // Check if this swap represents an interval START overlapping END
            if (endpoint[i].is_max == false && endpoint[i+1].is_min == false) {
                // Two intervals now overlap on this axis
                // If they overlap on ALL 3 axes (count == 3):
                if (IncrementOverlap(pair) == 3) {
                    // Check collision flags compatibility
                    if (CollisionFlagsCompatible(obj_a, obj_b)) {
                        // Add to collision pairs list
                        AddCollisionPair(obj_a, obj_b);
                    }
                }
            }
            // Check if this swap represents intervals SEPARATING
            else if (endpoint[i].is_max == true && endpoint[i+1].is_min == true) {
                if (DecrementOverlap(pair) == 2) {
                    // No longer overlapping on all 3 axes
                    // Remove from collision pairs list
                    RemoveCollisionPair(obj_a, obj_b);
                }
            }
        }
    }
} while (swapped);
```

**Key insight**: Because objects move incrementally frame-to-frame, the sorted arrays are
*nearly sorted* each frame, making the bubble-sort O(n) in practice (vs O(n^2) for naive
all-pairs testing).

### AABB Computation (FUN_00436130) — C3

```c
void GetAABB(NiAVObject* obj, Vec3* out_min, Vec3* out_max) {
    // First: get bounding box from geometry (vtable+0xE8)
    obj->GetBoundingBox(out_min, out_max);

    // If object has custom extents at +0x3D flag:
    if (obj->byte_0x3D) {
        // EXPAND (union) AABB to include custom bounds at +0x40..+0x54   <-- C3
        out_min->x = min(out_min->x, obj->custom_min_x);  // +0x40
        out_min->y = min(out_min->y, obj->custom_min_y);  // +0x44
        out_min->z = min(out_min->z, obj->custom_min_z);  // +0x48
        out_max->x = max(out_max->x, obj->custom_max_x);  // +0x4C
        out_max->y = max(out_max->y, obj->custom_max_y);  // +0x50
        out_max->z = max(out_max->z, obj->custom_max_z);  // +0x54
    }
}
```

**C3 [LOW]** — Prior doc's inline comment said "Clamp to custom bounds". That word was
misleading. The math (`min(out_min, custom_min)`, `max(out_max, custom_max)`) is correct,
but the operation expands the AABB to include the custom box. It does NOT clamp the AABB
down to the custom box. The custom bounds represent an EXTRA bounding region to merge into
the geometric AABB, not a constraint to clip against.

### Collision Flags Compatibility (FUN_005a7890)

Two objects can only collide if their collision flags at object+0x3C are compatible:

```c
bool CollisionFlagsCompatible(int obj_a, int obj_b) {
    byte flags_a = *(byte*)(obj_a + 0x3C);
    byte flags_b = *(byte*)(obj_b + 0x3C);

    // Check: (a's collision-with mask) & (b's collision-as type) & 0x2A
    if (((flags_b >> 1) & flags_a & 0x2A) != 0) return true;
    if (((flags_a >> 1) & flags_b & 0x2A) != 0) return true;
    return false;
}
```

The flag byte uses a bitmask where:
- Bits 0,2,4 = "collides AS type X" (what this object IS)
- Bits 1,3,5 = "collides WITH type X" (what this object can hit)
- 0x2A = 0b00101010 = mask for "with" bits

Accessible via Python: `ObjectClass_GetCollisionFlags` (reads byte at object+0x3C)

## Tier 2: Hierarchical Bounding Sphere Test                   [v5-validated 2026-05-28]

### CheckCollision (FUN_005671d0)

After sweep-and-prune finds overlapping AABBs, the game performs a **bounding sphere
intersection test** via `FUN_005671d0` (called 79,605 times per 15-min session). See OQ1
for the corrected caller breadth — this function has 12 callers, not the single caller the
prior call graph implied.

```c
// this = ObjectClass checking against, param_1 = other object
bool ObjectClass::CheckCollision(Object* other) {
    // 1. Early-out: already dead/marked
    if (this->IsDead_0x34()) return false;
    if (!this->collision_active_0x9C) return false;

    // 2. Ship-type check: if other is a ship with collision disabled
    Ship* ship = CastToShip(other);
    if (ship && ship->collisionManager_0x2DC && ship->collisionManager_0x2DC->disabled_0xAC)
        return false;

    // 3. Same-set check: both objects must be in same game set
    int this_set = this->gameObject_0x40->set_id_0x20;
    if (this_set != other->set_id_0x20)
        return false;

    // 4. Exclusion list: check event-based exclusion list at this_set+0x14
    //    (objects recently collided are temporarily excluded)
    for each exclusion in GetExclusionList(this_set, 0x800E) {
        if (IsInExclusionList(exclusion, this_gameObject))
            return true;  // Already known collision
        other_gameObj = GetGameObjectFromOther(other);
        if (IsInExclusionList(exclusion, other_gameObj))
            return true;  // Already known collision
    }

    // 5. TIMER CHECK: if collision cooldown expired AND no exclusion hit
    if (this->timer_0x98 > DAT_0089054c && !exclusion_found) {   // DAT_0089054C = 1.2f
        return true;  // Still in cooldown, report collision
    }

    // 6. NARROW PHASE: bounding sphere intersection
    result = CheckSphereIntersection(other);
    if (result) return true;

    // 7. RECURSIVE CHECK: check attached sub-objects
    for each child in this->attached_objects_0xB0 {
        child_obj = LookupObject(child_id);
        if (child_obj && child_obj->collisionData_0x2C8) {
            if (child_obj->collisionData->CheckCollision(other))
                return true;
        }
    }

    // 8. STATIC COLLISION: check against static/terrain geometry
    return CheckStaticCollision(other);
}
```

### Bounding Sphere Distance Test (FUN_00567640)

This is the core geometric test:

```c
bool CheckSphereIntersection(Object* other) {
    NiNode* this_node = this->gameObject_0x40;

    // Same set check
    if (this_node->set_id != other->set_id) return false;

    // Get world positions via vtable+0x94 (GetWorldTranslation)
    Vec3* pos_a = this_node->GetWorldTranslation();
    Vec3* pos_b = other->GetWorldTranslation();

    // Compute Euclidean distance
    float distance = ComputeDistance(this_node->set_id, pos_a, pos_b);
    //   distance = sqrt((bx-ax)^2 + (by-ay)^2 + (bz-az)^2)
    //   + adjustments from child bounding volumes

    // Compute combined collision radius
    float combined_radius = GetCombinedRadius(this);
    //   = NiNode->bound_radius_0x4C * this->scale_0x98 * this->radiusMult_0x34

    // TEST: distance < combined_radius
    if (distance < combined_radius) {
        return false;  // Inside combined sphere = possible collision, check children
    }

    // Recurse into child objects
    for each child in this->attached_objects_0xB0 {
        child_obj = LookupObject(child_id);
        if (child_obj && child_obj->collisionData_0x2C8) {
            if (child_obj->collisionData->CheckSphereIntersection(other))
                return true;
        }
    }
    return true;  // Spheres intersect at leaf level
}
```

### Distance Computation (FUN_00410570)

```c
float ComputeDistance(int set_id, Vec3* pos_a, Vec3* pos_b) {
    float dx = pos_b->x - pos_a->x;
    float dy = pos_b->y - pos_a->y;
    float dz = pos_b->z - pos_a->z;
    float base_distance = sqrt(dx*dx + dy*dy + dz*dz);

    // Apply child bounding volume adjustments
    for (int i = 0; i < set_id->num_modifiers_0xF8; i++) {
        float modifier = set_id->modifiers_0xFC[i]->ComputeAdjustment(base_distance, pos_a, pos_b);
        base_distance += (modifier - base_distance);
    }
    return base_distance;
}
```

### Collision Radius (FUN_00567190) — C1

```c
float GetCombinedRadius(CollisionData* this) {
    if (this->IsDead()) return DAT_00888b54;          // = 0.0f (see C1)
    if (!this->collision_active_0x9C) return DAT_00888b54;  // = 0.0f

    float ni_bound_radius = *(float*)(this->niNode_0x18 + 0x4C);
    float scale_factor = this->scale_0x98;
    float radius_mult = this->radiusMult_0x34;

    return ni_bound_radius * scale_factor * radius_mult;
}
```

**C1 [HIGH]** — Prior doc's Global Variables table called `DAT_00888B54` a "large float
sentinel" used as an "infinite distance". That label is **wrong**. Byte-read at 0x00888B54
returns `00 00 00 00` = **0.0f**.

The narrative text in the Global Variables row was wrong, but the doc's logic descriptions
were RIGHT — they just got there by accident:

- **In GetCombinedRadius**: when an object is dead or has collision disabled, returning 0.0
  means `combined_radius = 0`. Then the bounding-sphere test `distance < combined_radius`
  is always `false` (since distance is non-negative), so the broad-phase always rejects
  this object's sphere. The doc's "no collision through this object's sphere" outcome is
  correct via this zero-radius mechanism.

- **In HandleShipShipCollision** (FUN_005A61C0): the gap test reads
  `if (DAT_00888B54 <= gap)` = `if (gap >= 0.0)` — that's the *separating spheres* branch.
  The `else` branch (gap < 0, i.e. spheres overlap) is what calls PostCollisionEvent. The
  prior doc's narrative `## Ship-Ship Collision` said "If gap < 0 (spheres overlap): post
  collision event" — that text is correct, because `DAT_00888B54` is 0.0.

**Fix**: read `DAT_00888B54` as a 0.0f comparison threshold (not a sentinel). For OpenBC,
treat it as a literal 0.0f in both call sites.

**NiBound layout** (at NiNode + 0x40):
```
+0x00  float  center_x
+0x04  float  center_y
+0x08  float  center_z
+0x0C  float  radius
```

The bounding sphere radius at NiNode+0x4C is the NiBound radius computed from the 3D model.

## Tier 3: Narrow Phase -- Per-Type Collision Resolution       [v5-validated 2026-05-28]

### Collision Pair Dispatch (FUN_005a8810)

After sweep-and-prune identifies overlapping pairs and bounding spheres confirm proximity,
the collision pair is dispatched based on object types via three IsType (vtable+0x8) checks
against class IDs 0x8125, 0x8009, 0x8007:

```c
void ProcessCollisionPair(int* pair_data) {
    int* obj_a = pair_data;
    int* obj_b = pair_data;  // Second object from pair

    // Check object types via vtable RTTI (class ID 0x8125 = DamageableObject/Ship)
    if (IsType(obj_a, 0x8125)) {
        // Ship-to-ship collision (or ship-to-damageable)
        HandleShipShipCollision(obj_a, obj_b);  // FUN_005a61c0
    }
    else if (IsType(obj_a, 0x8009) || IsType(obj_b, 0x8009)) {
        // Torpedo collision (class 0x8009)
        Torpedo_DetectCollision(projectile, target);  // FUN_00579010
    }
    else if (IsType(obj_a, 0x8007) && IsType(obj_b, 0x8007)) {
        // Generic physics object collision
        HandlePhysicsCollision(obj_a, obj_b);  // FUN_005a88e0
    }
}
```

### Pattern Note — Ghidra Decompile Twin-Call Artifact

`FUN_005A8810` shows what looks like 6 sequential virtual calls to `(*vtable+8)(typeID)` in
the Ghidra decompile output. **The real assembly is "check obj_a then obj_b" for three
type-IDs** — 3 type-checks × 2 objects = 6 virtual call lines, but only 3 distinct branches.
Ghidra collapsed both object pointers into one displayed variable.

**When you see this pattern in a dispatcher** (N type-checks rendered as 2N sequential
`(*vtable+8)(typeID)` calls in the decompile), it's almost always the same artifact. Useful
to keep in mind when reading similar Ghidra decompiles in OpenBC implementation work.

### Ship-Ship Collision (FUN_005a61c0)

```c
void HandleShipShipCollision(Ship* ship_a, Ship* ship_b) {
    // Check if overlap is real (hash table lookup)
    if (!CheckOverlap(ship_a, ship_b)) return;

    // Get world positions via vtable+0x94
    Vec3* pos_a = ship_a->GetWorldTranslation();
    Vec3* pos_b = ship_b->GetWorldTranslation();

    // Get bounding radii via vtable+0xE4 (GetModelBound)
    float radius_a = GetBoundRadius(ship_a);  // *(float*)(GetModelBound(a) + 0x0C)
    float radius_b = GetBoundRadius(ship_b);  // (if ship_a->byte_0x7C == 0)

    // Compute gap = distance - radius_a - radius_b
    float gap = sqrt(dist_sq) - radius_a;
    if (!ship_a->byte_0x7C)
        gap -= radius_b;

    // Compare against DAT_00888B54 = 0.0f (see C1)
    if (gap < 0.0) {                                  // spheres overlap
        PostCollisionEvent(ship_a, ship_b);  // FUN_005a63a0
    }
    else if (gap > 0.0 && was_previously_colliding) {
        // Separation: post end-collision event
        PostCollisionEvent(ship_a, ship_b);
    }
}
```

### Physics Object Collision (FUN_005a88e0) — Clar1

For generic physics objects (type 0x8007), the collision includes:

1. **Eligibility check** (FUN_005946a0): both objects must have `collision_enabled_0x1A8` flag set
2. **Collision-enabled gate (dual byte)**: reads DAT_008E5F58 (client path) or DAT_008E5F59 (host path) depending on DAT_0097FA89 (IsHost) — see Clar1 below
3. **Velocity threshold**: both objects must have velocity^2 > DAT_008942DC (1.0e-7f minimum speed for collision)
4. **Angular momentum check**: rotational energy is also checked against threshold
5. **Contact history check**: prevents re-triggering if already in contact
6. **Detailed intersection**: Uses `vtable+0x148` (BeginIntersectionTest) and `vtable+0x150` (detailed mesh test)

```c
void HandlePhysicsCollision(Object* obj_a, Object* obj_b) {
    if (!CollisionEligible(obj_a, obj_b)) return;

    // Clar1 — dual collision-enabled byte
    char enabled = DAT_008E5F59;                  // host path
    if (DAT_0097FA89 == 0)                        // IsHost == 0 -> client
        enabled = DAT_008E5F58;                   // client path
    if (enabled == 0) return;                     // collisions globally disabled this side

    // Velocity threshold check
    Vec3* vel_a = GetVelocity(obj_a);  // FUN_005a05a0 -> NiNode+0x98
    Vec3* vel_b = GetVelocity(obj_b);
    float speed_sq_a = vel_a->x*vel_a->x + vel_a->y*vel_a->y + vel_a->z*vel_a->z;
    float speed_sq_b = vel_b->x*vel_b->x + vel_b->y*vel_b->y + vel_b->z*vel_b->z;

    // Both must be below velocity threshold (rest check)
    if (speed_sq_a <= DAT_008942DC && speed_sq_b <= DAT_008942DC) {
        // Also check angular momentum...
        // If both are essentially stationary: skip
        if (angular_energy_a <= threshold && angular_energy_b <= threshold) {
            if (NotAlreadyInContact(obj_a, obj_b))
                return;  // Both at rest, not already touching
        }
    }

    // Initialize collision result structure
    CollisionResult result;  // 88 bytes (0x58)
    InitCollisionResult(&result);  // FUN_0058a1a0

    // Perform intersection test
    if (obj_a->BeginIntersectionTest()) {
        // Fill result for obj_a
        FillCollisionData(&result, 0, obj_a->frame_0x36, velocity_a, position_a, angular_vel_a);
        // Fill result for obj_b
        FillCollisionData(&result, 1, obj_b->frame_0x36, velocity_b, position_b, angular_vel_b);

        // Execute detailed mesh intersection
        obj_a->PerformIntersection();  // vtable+0x150
        obj_b->PerformIntersection();
    }

    // Cleanup
    DestroyCollisionResult(&result);  // FUN_0058a1c0
}
```

#### Clar1 — Dual Collision-Enabled Bytes

There are **two** collision-enabled bytes, not one:

| Address | Path | Notes |
|---------|------|-------|
| `0x008E5F58` | CLIENT (read when IsHost == 0) | SWIG `ProximityManager_SetPlayerCollisionsEnabled` (0x00920074) |
| `0x008E5F59` | HOST (read when IsHost != 0) | Same byte as **Settings byte 1** sent in opcode 0x00 (network-synced game rule per CLAUDE.md) |

Both bytes serve as collision-damage toggles for their respective side. The HOST byte being
network-synced means a host can disable collision damage globally for the game session and
it propagates to clients via the Settings packet. The CLIENT byte is independent — a client
can disable its own collision-damage processing without telling the host.

For OpenBC: when implementing the dedicated server, both bytes are relevant:
- Read `0x008E5F59` from your Settings packet to know whether the host has collision damage enabled
- Honor `0x008E5F58` for any local (proxy/observer/headless) clients you run

The exact policy on which SWIG setter writes which byte is OQ2 below.

### Torpedo Collision (FUN_00579010)

Torpedoes use a different intersection method (vtable+0x140 / +0x144 instead of +0x148 / +0x150):

```c
void Torpedo_DetectCollision(Torpedo* torpedo, Object* target) {
    if (target == NULL) return;
    if (torpedo->dead_0x24) return;
    if (target->dead_0x24) return;  // target->byte[0x24*4 + 0x24]
    if (target->object_id == torpedo->owner_id_0x128) return;  // Can't hit launcher

    // Branch based on target type
    if (IsType(target, 0x8007)) {
        // Mesh-level intersection test
        Vec3 contact_point, velocity;
        torpedo->GetWorldTranslation(&contact_point, &velocity);

        bool hit = target->TestIntersection(torpedo->collision_shape + 0x150, contact_point);

        if (hit) {
            // Time-of-impact refinement (up to 2 iterations)
            while (iterations < 2) {
                if (contact_distance <= 0.0) {
                    torpedo->dead = true;
                    torpedo->TriggerDestruction();  // vtable+0x50
                    break;
                }
                // Refine time of impact
                torpedo->time_to_impact = contact_distance / speed * torpedo->original_toi;
                hit = target->TestIntersection(torpedo->collision_shape, updated_position);
            }
        }
    }
    else {
        // Simpler check for non-mesh objects
        HandleSimpleTorpedoCollision(torpedo, target);
    }
}
```

## Collision Result Structure (0x58 bytes)

Used by FUN_005a88e0 for physics collisions.

```
Offset  Size  Type         Field                    Notes
------  ----  ----         -----                    -----
0x00    1     byte         initialized              Set by InitCollisionResult
0x04    28    PerObj[0]    object_a_data            7 floats: frame, pos(3), vel(3)
0x20    28    PerObj[1]    object_b_data            Same layout for object B
0x3C    4     int          (unknown)                Init 0
0x40    4     int          contact_count            Number of contact entries
0x44    4     void*        contact_list_head        Linked list of contact nodes
0x48    4     void*        contact_list_tail
0x4C    4     void*        contact_free_pool        Free pool for reuse
0x50    4     void*        contact_chunk_list       Allocated memory chunks
0x54    4     int          mode                     Init 2
```

### Per-Object Collision Data (FUN_005a8c70)

Written at `this + param_1 * 0x1C + 4`:
```
+0x00  int    frame_number          Object's physics frame counter
+0x04  float  position_x            World position X
+0x08  float  position_y            World position Y
+0x0C  float  position_z            World position Z
+0x10  float  velocity_x            Linear velocity X
+0x14  float  velocity_y            Linear velocity Y
+0x18  float  velocity_z            Linear velocity Z
```

## Two Distinct "CollisionEvent" Entities — Clar2

This doc and the binary use the name "CollisionEvent" for **two different things**. They are
distinct objects with distinct purposes, and confusing them will burn an OpenBC implementer.

| # | Entity | Address / class | Role |
|---|--------|-----------------|------|
| 1 | **Physics CollisionEvent struct** (88 bytes, 0x58) | SWIG class string at `0x008E584C` | Stack-allocated by `FUN_005A88E0`; owns the contact list (head/tail/free-pool); fed to `FUN_005952D0` DoDamage_CollisionContacts for per-contact damage. The struct laid out in the "Collision Result Structure" section above. Python accessors GetCollisionForce/GetPoint/GetNumPoints at 0x0091F7DC..0x0091F818. |
| 2 | **Wire-event posted to TGEventManager** | event-code `0x00800050`, class-ID `0x00008124` | Posted by `FUN_005A63A0` (PostCollisionEvent). Wrapped by **TGObjPtrEvent** (factory `0x010C`, SWIG class string "TGObjPtrEvent" at `0x008D8594` and "_p_TGObjPtrEvent" at `0x008D85A4`). This is what flows through TGEventManager dispatch and ends up on the wire as opcode 0x15 (CollisionEffect). |

The relationship between the two: entity #1 (the physics struct) lives inside the collision
detection tick and never goes on the wire. Entity #2 (the TGEvent) is generated as a result
of detection and IS the network-side collision event. Both are referenced in the doc's
`## Event Types` table — see the row for `0x00800050` and `0x00008124`.

Cross-anchored from protocol leaf #15 (collision-effect-protocol.md) and protocol leaf #13
(tgobjptrevent-class.md).

## Collision Energy Calculation                                [v5-validated 2026-05-28]

### DoDamage_CollisionContacts (FUN_005952D0)

The collision energy/force that feeds into the damage system is computed as follows
(cross-anchored from gameplay foundation #1, damage-system.md — all 5 constants
byte-confirmed there too):

```c
void DoDamage_CollisionContacts(Ship* this, CollisionEvent* event) {
    int num_contacts = event->num_points;        // event+0x38
    float total_force = event->collision_force;   // event+0x40
    float mass = this->mass_0xD8;                 // ship mass from property

    // Compute damage per contact point
    float raw_damage = (total_force / mass) / num_contacts;
    float damage = raw_damage * DAT_00893f28 + DAT_0088bf28;
    //                          ^scale = 0.1f  ^offset = 0.1f

    // Clamp to maximum
    if (damage > DAT_008887a8) {              // 0.5f
        damage = 0.5;  // 0x3f000000 = 0.5f
    }

    for (int i = 0; i < num_contacts; i++) {
        Vec3 contact_point = event->GetPoint(i);

        // Transform to ship-local coordinates
        Vec3 local = contact_point - ship->NiNode->world_position;
        float inv_scale = DAT_00888860 / ship->NiNode->bound_radius;   // 1.0f / radius
        Vec3 normalized = MatrixMultiply(local, ship->NiNode->rotation_matrix) * inv_scale;

        // Apply damage at this position
        DoDamage(this, &normalized, damage, DAT_45bb8000);
        //                                  ^6000.0 max damage cap (inline immediate)
    }
}
```

### Damage Formula Summary

```
per_contact_damage = clamp((force / mass / num_contacts) * 0.1 + 0.1, 0, 0.5)
total_damage_per_contact = per_contact_damage * 6000.0 (max damage cap)
```

| Symbol | Source | Value |
|--------|--------|-------|
| `force` | CollisionEvent+0x40 (collision impulse magnitude) | runtime |
| `mass` | ship+0xD8 (from ShipProperty) | runtime |
| `num_contacts` | CollisionEvent+0x38 | runtime |
| `SCALE` | DAT_00893F28 | 0.1f |
| `OFFSET` | DAT_0088BF28 | 0.1f |
| `CLAMP` | DAT_008887A8 | 0.5f |
| `MAX_DAMAGE` | inline immediate 0x45BB8000 | 6000.0f |
| `INV_SCALE` | DAT_00888860 | 1.0f |

### Force Computation in CollisionEvent

The `collision_force` float (event+0x40) is computed by the collision response system
during the physics tick. It represents the magnitude of the impulse applied during the
collision, which depends on:

- **Relative velocity** of the two objects at the contact point
- **Mass** of the objects involved
- **Coefficient of restitution** (bounce factor)

The force is computed in the physics engine's collision response phase (the mesh intersection
handlers at vtable+0x150), which runs AFTER detection confirms overlap.

## Call Graph Summary

```
FUN_0040ffb0 (SimulationTick)
  |
  +-> FUN_005856d0 (BuildCollisionPairsForSets)    <-- 0x005857FF is here
  |     |
  |     +-> FUN_00585910 (CollectObjectsFromSet)     -- per-Set object enumeration
  |     +-> FUN_005671d0 (CheckCollision)             -- 79,605 calls/15-min  (NOTE: 12 callers total — see OQ1)
  |     |     |
  |     |     +-> FUN_0056c350 (IsDead check)
  |     |     +-> FUN_005ab670 (CastToShip)
  |     |     +-> FUN_00599290 (ExclusionListCheck)   -- event 0x800E filter
  |     |     +-> FUN_00567640 (SphereIntersection)   -- bounding sphere test
  |     |     |     |
  |     |     |     +-> vtable+0x94 (GetWorldTranslation) x2
  |     |     |     +-> FUN_00410570 (ComputeDistance)     -- Euclidean + modifiers
  |     |     |     +-> FUN_00567190 (GetCombinedRadius)   -- NiBound * scale * mult
  |     |     |
  |     |     +-> FUN_00567830 (StaticCollisionCheck)  -- terrain/static geometry
  |     |
  |     +-> [Results stored in global collision pair set at 0x0098d328-0x0098d33C]
  |
  +-> FUN_005a83a0 (ProximityManager::Update)
        |
        +-> FUN_005a8470 (UpdateAABBEndpoints)     -- per-object AABB refresh
        +-> FUN_005a8500 (SweepAxis) x3            -- sweep-and-prune per axis
        |     |
        |     +-> FUN_005a9250 (SwapEndpoints)     -- bubble-sort swap
        |     +-> FUN_005a9850/FUN_005a9820 (IncrementOverlap/DecrementOverlap)
        |     +-> FUN_005a7890 (CollisionFlagsCompatible)
        |     +-> FUN_005a9360 (CreateCollisionPair)
        |     +-> FUN_005a9390 (PairEquals)
        |
        +-> FUN_005a8740 (ProcessAllPairs)
              |
              +-> FUN_005a8810 (DispatchCollisionPair)
                    |
                    +-> FUN_005a61c0 (Ship-Ship)      -- class 0x8125
                    +-> FUN_00579010 (Torpedo-Object)  -- class 0x8009
                    +-> FUN_005a88e0 (Physics-Physics) -- class 0x8007
```

## Global Variables                                            [v5-validated 2026-05-28]

| Address | Type | Name | Notes |
|---------|------|------|-------|
| 0x008E5F58 | byte | g_CollisionEnabled_Client | Client-path toggle; SWIG `ProximityManager_SetPlayerCollisionsEnabled` (Clar1) |
| 0x008E5F59 | byte | g_CollisionEnabled_Host | Host-path toggle; same byte as Settings byte 1 in opcode 0x00 (Clar1) |
| 0x0098D328 | int | collisionPairCount | Active collision pair count |
| 0x0098D32C | void* | collisionPairListHead | Linked list head |
| 0x0098D330 | void* | collisionPairListTail | Linked list tail |
| 0x0098D334 | void* | collisionPairFreePool | Free pool for reuse |
| 0x0098D338 | void* | collisionPairChunks | Allocated memory chunks |
| 0x0098D33C | int | collisionPairPoolSize | Init 2 (entries per chunk) |
| 0x008942DC | float | velocityThresholdSq | 1.0e-7f — min speed^2 for physics collision |
| 0x0089054C | float | collisionCooldownTime | 1.2f — timer threshold (object+0x98) for re-collision |
| 0x00893F28 | float | damageScaleFactor | 0.1f — collision damage tuning constant |
| 0x0088BF28 | float | damageBaseOffset | 0.1f — collision damage base threshold |
| 0x008887A8 | float | maxDamagePerContact | 0.5f — clamp value |
| 0x00888860 | float | normalizationConstant | 1.0f — used in contact-point normalization |
| 0x00888B54 | float | f_Zero_CollisionThreshold | **0.0f** (NOT a "large sentinel" — see C1). Used as gap-test threshold and zero-radius for dead objects. |
| 0x008955C8 | float | hostGapValidationThreshold | 26.0f — host-side validation gate for received CollisionEffect (cross-anchored from protocol leaf #15) |
| 0x45BB8000 | float | max_damage (inline) | 6000.0f — passed inline to DoDamage |

## Event Types                                                 [v5-validated 2026-05-28]

| Event Code | Name | Notes |
|------------|------|-------|
| 0x00800050 | ET_OBJECT_COLLISION | Client-detected collision (wrapped in TGObjPtrEvent — see Clar2) |
| 0x008000FC | ET_HOST_OBJECT_COLLISION | Host-validated collision |
| 0x00800053 | ET_COLLISION_BROADCAST | Effect broadcast to clients |
| 0x0000800E | (exclusion event) | Temporary collision cooldown |
| 0x00008124 | CT_COLLISION_EVENT | CollisionEvent class type ID (wire-side; cross-anchored from protocol leaf #15) |

## Object Type IDs (used in collision dispatch)

| Type ID | Name | Collision Behavior |
|---------|------|-------------------|
| 0x8125 | DamageableObject/Ship | Ship-ship: bounding sphere + event |
| 0x8009 | Torpedo/Projectile | Ray/sphere intersection, time-of-impact |
| 0x8008 | ShipClass | Subtype of DamageableObject |
| 0x8007 | PhysicsObject | Full mesh intersection, velocity-based |
| 0x8003 | GenericObject | Basic AABB overlap only |

## Key Design Decisions

1. **No triangle-mesh ship-ship detection**: Ship-to-ship collisions use ONLY bounding
   spheres. The NiBound radius (NiNode+0x4C) determines the collision volume. This is
   why large ships with elongated shapes can collide before they visually touch.

2. **Torpedoes use mesh intersection**: Unlike ships, torpedoes DO use detailed geometry
   tests (vtable+0x140/+0x150) to determine exact impact points.

3. **Sweep-and-prune is the workhorse**: With 79,605 CheckCollision calls per session,
   the broad-phase filtering is critical. The incremental sort means most frames only
   need a handful of swaps.

4. **Collision cooldown timer**: Object+0x98 acts as a cooldown (compared against
   `DAT_0089054C` = 1.2f) to prevent rapid-fire collision events when two ships grind
   against each other. **Separate** mechanism from the CLAUDE.md "collision rate limiting
   (ship+0xEC)" enable flag.

5. **Client-authoritative detection**: Collision detection runs on the CLIENT, not the
   server. Clients send opcode 0x15 to the host, which validates distance against
   `DAT_008955C8` = 26.0f and applies damage. This is why the dedicated server headless
   mode does NOT need to run collision detection itself. (Cross-anchored from protocol
   leaf #15.)

6. **Velocity threshold for physics**: Objects at rest (velocity^2 < DAT_008942DC = 1.0e-7f)
   are excluded from physics collision to avoid constant collision events from resting
   objects.

7. **Dual host/client collision-enabled bytes**: The HOST can disable collision damage
   globally via DAT_008E5F59 (network-synced in Settings packet); the CLIENT can disable
   its own local collision processing via DAT_008E5F58 independently. See Clar1.

## Open Questions

- **OQ1** — Caller breadth of CheckCollision (FUN_005671D0). The prior doc's call graph
  showed `CheckCollision` called only from `BuildCollisionPairsForSets`. Actual xrefs show
  **12 callers**: BuildCollisionPairsForSets, recursion-into-children, plus 10 external
  sites (FUN_00489910, FUN_004FECF0, FUN_00501510, FUN_00501610 ×2, FUN_00544200,
  FUN_00538C90, FUN_005930A0, and bare-code xrefs at FUN_00567162 + FUN_005AE128). These
  are likely AI proximity queries (NavManager paths) or script-driven detection. The
  79,605 calls/session figure represents the SUM of all caller paths; a trace replay
  attributing calls per-caller would let us partition the count. **Promotion path**:
  full xref enumeration + call-frequency partition.

- **OQ2** — Detailed semantics of `0x008E5F58` vs `0x008E5F59`: which SWIG setter writes
  which byte? The doc lists `ProximityManager_SetPlayerCollisionsEnabled` (0x00920074) but
  hasn't yet been traced to confirm whether it touches the client byte, the host byte, or
  both. Settings byte 1 in opcode 0x00 confirms the HOST byte is network-synced — but the
  policy boundary (when is the client byte toggled? by whom?) needs an xref dig on the
  SWIG entry point. **Promotion path**: trace SWIG `SetPlayerCollisionsEnabled` callers
  through Python boot to identify which side flips which byte.

## Related Documents

- [collision-effect-protocol.md](../protocol/collision-effect-protocol.md) -- Network protocol for opcode 0x15 (CollisionEffect); the wire-side of this detection system
- [tgobjptrevent-class.md](../protocol/tgobjptrevent-class.md) -- TGObjPtrEvent (factory 0x010C) class layout; what wraps event-code 0x00800050 on the wire
- [damage-system.md](damage-system.md) -- Damage pipeline (collision -> hull/subsystem damage); shares the 5 constants used in DoDamage_CollisionContacts
- [collision-shield-interaction.md](collision-shield-interaction.md) -- Sibling leaf: shield-side absorption math (directional, two-step damage)
- [collision-rate-limiting.md](collision-rate-limiting.md) -- Sibling leaf: ship+0xEC rate-limit enable flag (separate from the per-object cooldown timer)
- [cut-content-analysis.md](../analysis/cut-content-analysis.md) -- Collision mesh voxelizer (cut debug tool)
