---
name: gameplay-foundation-collision-detection-validation-20260528
description: v5 validation of docs/gameplay/collision-detection-system.md — 3-tier collision pipeline. ZERO wire/formula errors in core math; sweep-and-prune endpoint layout corrected, DAT_00888b54 sentinel value corrected, dual collision-enabled bytes (host vs client) clarified, call graph incomplete.
metadata:
  type: project
---

# Gameplay Foundation #4: Collision Detection System — v5 Validation Memo

**Doc**: `docs/gameplay/collision-detection-system.md` (664 lines)
**Date**: 2026-05-28
**Status**: `partial` — material accuracy excellent (formulas/dispatch all match binary), but 3 detail errors + 2 clarifications + 1 incomplete-coverage flag.
**Verdict**: Among the cleanest pre-v5 gameplay docs validated. All function addresses exist, all class IDs (0x8125/0x8009/0x8007), all vtable slots (+0x94 GetWorldTranslation, +0xE4 GetModelBound, +0x140/+0x144 torpedo intersect, +0x148/+0x150 physics intersect, +0xE8 GetBoundingBox), all damage constants byte-confirmed.

## Anchoring summary

- 17 primary function addresses: ALL exist (`FUN_005a7420`, `FUN_005671d0`, `FUN_005a83a0`, `FUN_005a8500`, `FUN_005a8810`, `FUN_005a61c0`, `FUN_005a88e0`, `FUN_00579010`, `FUN_00567640`, `FUN_00567190`, `FUN_005a7890`, `FUN_005a7640`, `FUN_005a8740`, `FUN_005952d0`, `FUN_005856d0`, `FUN_00410570`, `FUN_00436130`).
- 17 secondary addresses: ALL exist except `0x005a7340` (not a function entry; not referenced by doc anyway).
- Class IDs: 0x8125 (Ship/DamageableObject), 0x8009 (Torpedo), 0x8007 (PhysicsObject) — all 3 appear in `FUN_005a8810` dispatcher decomp via `(**(code **)(*param + 8))(typeID)` (vtable slot+8 is IsType).
- Constants byte-confirmed:
  - `0x008942D4` ProximityManager vtable: confirmed (PTR_LAB_008942d4 assigned in `FUN_005a7420`).
  - `0x008942dc` = `33D6BF95` = ~1.0e-7 (velocityThresholdSq).
  - `0x0089054c` = `9A99993F` = 1.2f (collision cooldown timer threshold).
  - `0x00893f28` = `CDCCCC3D` = 0.1f (damageScaleFactor).
  - `0x0088bf28` = `CDCCCC3D` = 0.1f (damageBaseOffset).
  - `0x008887a8` = `0000003F` = 0.5f (maxDamagePerContact).
  - `0x00888860` = `0000803F` = 1.0f (normalizationConstant).
  - `0x008e5f58` = `01` (server-side g_CollisionEnabled).
  - `0x008e5f59` = `01` (client-side g_CollisionEnabled).
  - `DAT_45BB8000` = 6000.0f (damage cap).
- SWIG class strings confirm: "ProximityManager", "ProximityManager_SetPlayerCollisionsEnabled", "CollisionEvent" (with GetCollisionForce, GetPoint, GetNumPoints).

## v5 Triage

### C — Material Corrections (3)

**C1 [HIGH]** — `DAT_00888b54` is **0.0f**, not a "large float sentinel" as doc Global Variables table claims.
  - Address byte-read: `0x00888b54` = `00 00 00 00` = **0.0f**.
  - Usage in `FUN_00567190` (GetCombinedRadius): `if dead return DAT_00888b54` → returns 0.0 when dead/disabled, meaning `combined_radius = 0` → bounding-sphere test `radius < distance` is ALWAYS true → "no collision through this object's sphere" (then walks children). This is the correct semantic: a dead object has zero collision radius.
  - Usage in `FUN_005a61c0` (Ship-Ship): `if (DAT_00888b54 <= gap)` → `if (gap >= 0.0)` → spheres separating; `else` (gap < 0) → PostCollisionEvent. Doc text in `## Ship-Ship Collision` says "If gap < 0 (spheres overlap): post collision event" — that text is CORRECT (because DAT = 0.0). But the doc's Global Variables table calling it `sentinelValue` "Large float used as 'infinite' distance" is WRONG.
  - Fix: rename to `f_Zero_CollisionThreshold` or similar; description = "0.0f comparison threshold for gap (collision when gap < 0) and zero-radius for dead objects in GetCombinedRadius".

**C2 [MED]** — Sweep-and-prune **endpoint struct layout** mis-stated.
  - Doc claims (line 69): `Each endpoint entry is 12 bytes: { float value, int next_ptr, int object_index }`.
  - Actual layout from `FUN_005a8500` and `FUN_005a8cc0`:
    - `+0x00` float `value`
    - `+0x04` byte `is_min_flag` (0 = start/min endpoint, nonzero = end/max endpoint)
    - `+0x05..+0x07` padding
    - `+0x08` int `object_index` (into ProximityManager+0x54 object array)
  - The "next_ptr" field does not exist. Sorted-array is contiguous (no pointer chain); next entry is at `+0xC` in same array.
  - This is also reflected in `FUN_005a8500`'s swap logic: `*(char*)(iVar9 + 4)` is the min/max flag (matches doc's later `endpoint[i].is_max == false && endpoint[i+1].is_min == false` semantics).

**C3 [LOW]** — `FUN_00436130` (GetAABB) field operation is **expansion (union)**, not "clamp".
  - Doc says (line 132): `// Clamp to custom bounds at +0x40..+0x54`.
  - Actual: takes min-of-mins (`if (custom_min_x < computed_min_x) computed_min_x = custom_min_x`) and max-of-maxes (`if (computed_max_x < custom_max_x) computed_max_x = custom_max_x`). That is **union/expand** the AABB to include the custom bounds (which represent an EXTRA bounding box from object's custom field).
  - The math in doc's pseudocode (`out_min->x = min(out_min->x, obj->custom_min_x)` and `max(...)` for max) IS correct.
  - Only the comment word "Clamp" is misleading. Trivial doc fix.

### Clar — Clarifications (2)

**Clar1** — **Dual collision-enabled bytes** at 0x008e5f58 and 0x008e5f59.
  - Doc Global Variables table lists only `0x008e5f58 = g_CollisionEnabled (SetPlayerCollisionsEnabled)`.
  - `FUN_005a88e0` (Physics dispatch) reads:
    ```
    cVar2 = DAT_008e5f59;            // host path
    if (DAT_0097fa89 == 0)            // IsHost == 0 → client
        cVar2 = DAT_008e5f58;        // client path
    if (cVar2 == 0) { /* skip host-checks */ ... }
    ```
  - Both bytes serve as collision-enable toggles; `0x008e5f59` is the host-side flag, `0x008e5f58` is the client-side flag. Probably "host disables collision damage" vs "client disables collision damage" independently — relevant for headless server tuning. Doc should add both bytes.
  - Note: byte at `0x008e5f59` also appears in our Settings packet (per CLAUDE.md "Settings byte 1"), so it's a network-synced game-rule.

**Clar2** — Collision-event payload class is **TGObjPtrEvent**, not "CollisionEvent" at the TGEvent dispatch layer.
  - `FUN_005a63a0` (PostCollisionEvent in doc) allocates 0x30-byte object using SWIG class string at `0x008d858c` = "UNKNOWN" — but the very next string at `0x008d8594` = "TGObjPtrEvent" and `0x008d85a4` = "_p_TGObjPtrEvent". The allocator pattern matches TGObjPtrEvent factory.
  - This is consistent with protocol leaf #15 (collision-effect-protocol.md): event type `0x00800050` carried by class `0x00008124` (CollisionEventClassID) is fired via TGObjPtrEvent (factory 0x010C) per memo `tgobjptrevent-validation-20260528`.
  - The "CollisionEvent" class IS distinct: it's the 88-byte stack struct in `FUN_005a88e0` holding physics contacts. SWIG exposes it (GetCollisionForce/GetPoint/GetNumPoints accessors at 0x0091f7dc..0x0091f818).
  - So there are TWO things called "CollisionEvent":
    1. **CollisionEvent class** (physics struct, 88 bytes, owns contact list) — fed to `FUN_005952d0 DoDamage_CollisionContacts`. Doc covers this correctly.
    2. **Event message** posted to TGEventManager with event-code `0x00800050`, carried by TGObjPtrEvent class wrapper. Doc's `## Event Types` table lists this correctly.
  - No actual correction; just flagging that two distinct concepts share the name "CollisionEvent" in the doc.

### R — Reanchoring (0)

None. All function symbols still resolve.

### OQ — Open Questions (2)

**OQ1** — Doc's `## Call Graph Summary` shows `FUN_005671d0` (CheckCollision) called only from `FUN_005856d0 (BuildCollisionPairsForSets)`. Actual xrefs show **12 callers**:
  - `FUN_005856d0` (BuildCollisionPairsForSets) — confirmed by doc
  - `FUN_005671d0` itself (recursion into children) — confirmed
  - `FUN_00567162` (bare-code xref nearby) — likely vtable slot or inline
  - `FUN_005ae128` (bare-code xref)
  - `FUN_00489910`, `FUN_004fecf0`, `FUN_00501510`, `FUN_00501610` (×2), `FUN_00544200`, `FUN_00538c90`, `FUN_005930a0` — additional callers, likely from AI/script/Python paths
  
  Doc undersells the breadth of CheckCollision use. Worth a follow-up dig: are these AI proximity queries (NavManager calls)? Trace replay can confirm whether SP collision rate (~79,605/15min per doc) matches sum of all callers.

**OQ2** — `0x008e5f58` vs `0x008e5f59` semantics in detail: doc doesn't explain when each is toggled. Need to find SetPlayerCollisionsEnabled callers to determine policy (server-side toggle vs client-side toggle vs both-side). Cross-ref to `docs/protocol/wire-format-spec.md` Settings packet would help.

### H — Historical (0)

No sections in the doc are stale-by-superseding-RE.

## Anchored Inventory (32 items)

### Functions (16 doc-anchored, all exist)
| Doc claim | Address | Status |
|-----------|---------|--------|
| ProximityManager_Ctor | `0x005a7420` | exists, ctor pattern confirmed |
| CheckCollision (ObjectClass::CheckCollision) | `0x005671d0` | confirmed (12 callers, not just 1) |
| ProximityManager::Update | `0x005a83a0` | exists, 1 caller (SimulationTick) |
| SweepAxis | `0x005a8500` | exists; bubble-sort + swap logic confirmed |
| ProcessCollisionPair / Dispatcher | `0x005a8810` | exists; 0x8125/0x8009/0x8007 dispatch confirmed |
| HandleShipShipCollision | `0x005a61c0` | exists; vtable+0xE4 GetModelBound +0xC radius confirmed |
| HandlePhysicsCollision | `0x005a88e0` | exists; vtable+0x148/+0x150 confirmed |
| Torpedo_DetectCollision | `0x00579010` | exists; vtable+0x140/+0x144 confirmed; up-to-2 iters confirmed |
| CheckSphereIntersection | `0x00567640` | exists; vtable+0x94 ×2 + FUN_00410570 + FUN_00567190 confirmed |
| GetCombinedRadius | `0x00567190` | exists; NiNode+0x4C * this+0x98 * this+0x34 confirmed |
| CollisionFlagsCompatible | `0x005a7890` | exists; (b>>1 & a & 0x2A) \| (a>>1 & b & 0x2A) confirmed |
| AddObject (ProximityManager) | `0x005a7640` | exists; AABB compute + 3-axis insert confirmed |
| ProcessAllPairs | `0x005a8740` | exists; walks circular doubly-linked list at +0xC |
| DoDamage_CollisionContacts | `0x005952d0` | exists; formula (force/mass/n) * 0.1f + 0.1f, clamp 0.5, cap 6000.0 confirmed |
| BuildCollisionPairsForSets | `0x005856d0` | exists; 4 set fields +0x2B4/+0x2B8/+0x2BC/+0x2D4 confirmed |
| ComputeDistance | `0x00410570` | exists; sqrt(dx²+dy²+dz²) + modifier loop at +0xF8/+0xFC confirmed |
| GetAABB | `0x00436130` | exists; vtable+0xE8 + custom +0x40..+0x54 union (NOT clamp) confirmed |

### Secondary functions (17 doc-anchored, 16 exist)
- `0x005a8470` AABB endpoint update (per-object refresh) — confirmed
- `0x005a8cc0` Binary-search insert into sorted endpoint array — confirmed
- `0x005a63a0` PostCollisionEvent — confirmed, allocates 0x30-byte TGObjPtrEvent
- `0x0058a1a0` InitCollisionResult — exists (called from FUN_005a88e0)
- `0x0058a1c0` DestroyCollisionResult — exists (called from FUN_005a88e0)
- `0x005946a0` CollisionEligible — confirmed; checks param+0x1A8 + list at +0x194
- `0x00567830` StaticCollisionCheck — exists (called from FUN_005671d0 fall-through)
- `0x005ab670` CastToShipClass — already named — confirmed
- `0x00599290` ExclusionListCheck — confirmed; walks list at +0x90
- `0x005a8c70` FillCollisionData — confirmed; writes 7 DWORDs at param_1 + 4 + param_2 * 0x1C
- `0x005a9250` SwapEndpoints — exists
- `0x005a9850` IncrementOverlap (returns 3 when fully overlapping) — exists
- `0x005a9820` DecrementOverlap (returns 2 when down to 2-axis) — exists
- `0x005a9360` CreateCollisionPair — exists
- `0x005a9390` PairEquals — exists
- `0x0056c350` IsDead check — exists
- `0x00585910` CollectObjectsFromSet — confirmed; per-Set object enumeration
- ~~`0x005a7340`~~ — NOT a function; not actually referenced by doc

### Constants/globals (15 byte-confirmed)
| Addr | Doc name | Actual value | Verdict |
|------|----------|--------------|---------|
| `0x008942D4` | ProximityManager vtable | first slot 0x005A9A20 | confirmed |
| `0x008942dc` | velocityThresholdSq | 1.0e-7f (~near-zero) | confirmed |
| `0x0089054c` | collisionCooldownTime | 1.2f | confirmed |
| `0x00893f28` | damageScaleFactor | 0.1f | confirmed |
| `0x0088bf28` | damageBaseOffset | 0.1f | confirmed |
| `0x008887a8` | maxDamagePerContact | 0.5f | confirmed |
| `0x00888860` | normalizationConstant | 1.0f | confirmed |
| `0x00888b54` | "sentinelValue / Large float" | **0.0f** | **C1 - WRONG** |
| `0x008e5f58` | g_CollisionEnabled | 0x01 | confirmed (client path) |
| `0x008e5f59` | (undocumented) | 0x01 | **Clar1 - host-path mirror** |
| `0x45BB8000` | max damage cap | 6000.0f | confirmed |
| `0x0098d328` | collisionPairCount | 0 in image (.bss) | confirmed (.bss) |
| `0x0098d32c..0x0098d33c` | pair list/free/chunks | 0 in image | confirmed |

### Class IDs / event codes (5 confirmed by use)
- `0x8125` DamageableObject/Ship — `FUN_005a8810` dispatcher confirmed
- `0x8009` Torpedo — `FUN_005a8810` dispatcher confirmed
- `0x8007` PhysicsObject — `FUN_005a8810` + `FUN_00579010` confirmed
- `0x800E` ExclusionList event — `FUN_005671d0` calls FUN_0040afe0(0x800e, ...) confirmed
- `0x00008124` CollisionEvent class ID — cross-ref to protocol leaf #15 (memo `collision-effect-protocol-validation`)
- `0x00800050` ET_OBJECT_COLLISION — same cross-ref

## Patterns Discovered

- **"vtable+slot" naming convention** in this doc is robust and survived every check. Slots:
  - `+0x50` TriggerDestruction (torpedo)
  - `+0x58` per-frame Update (called by `FUN_005a83a0` for ship type 0x8125 with field [8]==0)
  - `+0x94` GetWorldTranslation (returns Vec3*)
  - `+0xE4` GetModelBound (returns NiBound*, radius at +0xC)
  - `+0xE8` GetBoundingBox (writes min/max into params)
  - `+0x140` Torpedo: BeginIntersection (returns bool)
  - `+0x144` Torpedo: RefinementIntersection (returns bool)
  - `+0x148` Physics: BeginIntersectionTest
  - `+0x150` Physics: PerformIntersection (detailed mesh)

- **3-tier collision is genuinely 3-tier** — broad-phase sweep-and-prune yields candidate pairs, CheckCollision applies bounding-sphere hierarchy, narrow-phase dispatcher routes by RTTI. The "tiers" are not marketing — they correspond to distinct call sites.

- **Dispatcher class-ID check has Ghidra-decompile twin-call artifact**: `FUN_005a8810` shows `(*vtable+8)(0x8125)` called TWICE in a row for both obj_a and obj_b. Ghidra collapsed both arguments into one pointer var. Real assembly likely passes obj_a then obj_b. Pattern: when a dispatcher has 6+ "duplicate" virtual calls in decompile, it's actually 3 type-checks against 2 objects.

- **NiBound location**: `NiNode+0x40` is the NiBound struct (4 floats: center xyz, radius). Doc claim at line 297 (`+0x4C` radius field) verified — radius is at `NiBound+0xC` = `NiNode+0x4C`.

## Cross-References

- `collision-effect-protocol-validation-20260528` (protocol leaf #15): wire-format side of opcode 0x15. Doc's "client-authoritative detection" claim (line 652) confirmed there: clients send opcode 0x15, host validates distance (gap < 26.0f at 0x008955C8), applies damage.
- `gameplay-foundation-damage-system-validation-20260528` (gameplay foundation #1): `FUN_005952d0` formula constants (0.1f scale/add, 0.5f cap, 6000.0f max) ALL byte-confirmed there too. Both docs in agreement.
- `tgobjptrevent-validation-20260528` (protocol leaf #13): TGObjPtrEvent class layout (0x2C bytes wire) — Clar2 connects to this.
- CLAUDE.md "Collision rate limiting disabled (ship+0xEC=0)" — NOT covered by this doc; out of scope. Doc's "collision cooldown" at object+0x98 (timer comparison against `DAT_0089054c` = 1.2f) is a SEPARATE mechanism (per-object cooldown timer, not the +0xEC rate-limit enable flag).
