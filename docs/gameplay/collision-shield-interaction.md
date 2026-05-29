> [docs](../README.md) / [gameplay](README.md) / collision-shield-interaction.md

---
title: Collision-Shield Interaction
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
  - claim: "CollisionDamageWrapper at 0x005B0060 is a 6-arg __thiscall (ECX hidden in decomp); disasm 0x005B0067-0x005B008E confirms PUSH 0x1 (isCollision), PUSH 0x0 (source=NULL), PUSH EDI (radius), PUSH EAX=&damage, PUSH ECX=collider+0x88 (position), MOV ECX=this, CALL FUN_005AFD70, then CALL FUN_00593650; RET 0xC"
    address: 0x005B0060
    function: CollisionDamageWrapper
    confidence: high
    note: "Disasm 0x005B0067-0x005B008E byte-confirmed."
  - claim: "FUN_005AFD70 (SubsystemDamageDistributor) hardcodes its 5th arg ('\\0') to FUN_005AF4A0 — collision and weapon damage take identical per-subsystem path from this point onward"
    address: 0x005AFE3D
    function: FUN_005AFD70
    confidence: high
    note: "PUSH 0x0 instruction at 0x005AFE3D immediately before CALL FUN_005AF4A0."
  - claim: "FUN_005AF4A0 (per-subsystem damage worker) reads curHP at subsystem+0x30, computes overflow = -newHP when newHP<=0, calls ShipSubsystem_SetCondition at FUN_0056C470 (named in Ghidra) after computing maxHP via FUN_0056C310 (GetMaxCondition)"
    address: 0x005AF4A0
    function: FUN_005AF4A0
    confidence: high
  - claim: "Position-normalization wrapper at FUN_00593650 — called from CollisionDamageWrapper at 0x005B008E; transforms damage origin to scene-root-relative coords before invoking the true damage entry at FUN_00594020"
    address: 0x00593650
    function: FUN_00593650
    confidence: high
    note: "C2 correction — the doc previously labeled this 'DoDamage_FromPosition'; that name belongs to FUN_00594020."
  - claim: "DoDamage_FromPosition at FUN_00594020 is the true DamageVolume entry; allocates DamageVolume via FUN_004BBDE0 and calls ProcessDamage via FUN_00593E50"
    address: 0x00594020
    function: FUN_00594020
    confidence: high
  - claim: "ProcessDamage at FUN_00593E50 is the handler-array entry point (cross-anchored from gameplay foundation #1, damage-system.md)"
    address: 0x00593E50
    function: FUN_00593E50
    confidence: high
  - claim: "DamageVolume constructor at FUN_004BBDE0 (cross-anchored from collision-detection-system memo)"
    address: 0x004BBDE0
    function: FUN_004BBDE0
    confidence: high
  - claim: "AoE explosion handler at FUN_00593C10 explicitly walks the 6-facing shield array (curShields[6] at ShieldGenerator+0xA8) and drains each by damage * (1/6) = damage * DAT_0088BACC; then forwards remaining damage to FUN_005AFD70 for hull/subsystem distribution"
    address: 0x00593C10
    function: FUN_00593C10
    confidence: high
    note: "while (iVar8 < 6) loop + DAT_0088BACC byte-confirmed."
  - claim: "Ray-ellipsoid pre-gate at FUN_005AF010 (WeaponHitHandler) reads hitInfo+0x58: if '\\0' → shield-absorbed branch (TorpedoShieldHit visual, no DoDamage); else hull-pass branch calls FUN_005AF420"
    address: 0x005AF010
    function: FUN_005AF010
    confidence: high
    note: "Gate `(char)*(int*)(param_2 + 0x58) == '\\0'` byte-confirmed."
  - claim: "Torpedo type check at FUN_005AF630 reads weapon+8 (weapon_type) — if torpedo (type==1), reads torpedo[0x2B] (= +0xAC byte) to decide isCollision=0 vs =1; controls power subsystem exclusion in FUN_005AFD70"
    address: 0x005AF630
    function: FUN_005AF630
    confidence: high
    note: "weapon[0x2B] = +0xAC matches doc's int-index notation."
  - claim: "FUN_0056C470 (ShipSubsystem_SetCondition, named in Ghidra) creates a TGObjPtrEvent (NOT TGCharEvent) — size 0x2C allocation via FUN_00717B70(0x2C), constructed by TGObjPtrEvent_Ctor, fills dwEvent_type=0x0080006B (SUBSYSTEM_HIT) and nObj_ptr=*(int*)(param_1+4)"
    address: 0x0056C470
    function: FUN_0056C470
    confidence: high
    note: "C1 correction — class identity verified by alloc size 0x2C (= TGObjPtrEvent per protocol leaf #13) NOT 18B (= TGCharEvent per protocol leaf #16). TGObjPtrEvent_Ctor plate-stamped in Ghidra."
  - claim: "TGObjPtrEvent class size = 0x2C bytes; fields dwEvent_type at +0x10 and nObj_ptr at +0x28 (cross-anchored from protocol mid #13, tgobjptrevent-class.md)"
    address: 0x008D8594
    function: TGObjPtrEvent_Ctor
    confidence: high
    note: "SWIG class string 'TGObjPtrEvent' at 0x008D8594."
  - claim: "CastToShipClass at 0x005AB670 (NAMED in Ghidra) uses class ID 0x8008 for the Ship check; appears in collision damage path"
    address: 0x005AB670
    function: CastToShipClass
    confidence: high
  - claim: "Ship+0x2C4 holds the PowerSubsystem pointer; FUN_005AFD70 excludes it from the hit list when isCollision=0 AND hit_count>1 (weapons-only carve-out), keeps it in for collisions"
    address: 0x005AFDCC
    function: FUN_005AFD70
    confidence: high
    note: "TEST AL,AL; JNZ at 0x005AFDCC followed by CMP [ESP+0x10],0x1 hit-count check + EBX+0x2C4 loop. Cross-anchored against power-system.md PowerSubsystem ownership."
  - claim: "Subsystem curHP lives at subsystem+0x30 — used by FUN_005AF4A0 for damage arithmetic and by FUN_0056C470 for the clamp/event-fire path"
    address: 0x0056C470
    function: FUN_0056C470
    confidence: high
  - claim: "ShipSubsystem_SetCondition (FUN_0056C310 = GetMaxCondition) is the named max-HP getter used by per-subsystem damage to clamp the new HP"
    address: 0x0056C310
    function: FUN_0056C310
    confidence: high
  - claim: "Ship[0xB0] = ShieldGenerator pointer at ship+0x2C0 (cross-anchored from shield-system gameplay foundation #2; vtable 0x00892F34)"
    address: 0x005AFD70
    function: FUN_005AFD70
    confidence: high
    note: "Int-index 0xB0 * 4 = byte offset 0x2C0."
  - claim: "ShieldGenerator+0xA8 = curShields[6] — 6 floats, one per facing (cross-anchored from shield-system gameplay foundation #2)"
    address: 0x00593C10
    function: FUN_00593C10
    confidence: high
  - claim: "DAT_0088BACC = 0x3E2AAAAB = 0.16666... = 1/6 — AoE per-facing distribution constant"
    address: 0x0088BACC
    function: FUN_00593C10
    confidence: high
    note: "Byte-confirmed."
  - claim: "DAT_00888B54 = 0.0f — collision damage gate / overflow threshold (re-confirmed; cross-anchored against collision-detection-system C1)"
    address: 0x00888B54
    function: shared
    confidence: high
    note: "Byte-read 00 00 00 00."
  - claim: "FUN_005AFD70 5th-arg `source` is NULL for the collision path; whether it can be non-NULL via any other caller is OQ1"
    address: 0x005B0060
    function: CollisionDamageWrapper
    confidence: medium
    note: "PUSH 0x0 at 0x005B0079 visible; OQ1 — verify via dataflow on other callers of FUN_005AFD70."
companions:
  - docs/gameplay/collision-detection-system.md
  - docs/gameplay/damage-system.md
  - docs/gameplay/shield-system.md
  - docs/protocol/tgobjptrevent-class.md
  - docs/gameplay/collision-rate-limiting.md
supersedes:
  - pre-v5
---

> [!NOTE]
> **Zero formula/wire errors**. 2 corrections (C1 MED: FUN_0056C470 creates **TGObjPtrEvent** not TGCharEvent — verified by alloc size 0x2C; C2 LOW: the DoDamage chain has a wrapper layer at FUN_00593650 between CollisionDamageWrapper and the true DamageVolume entry FUN_00594020) + 2 clarifications (Clar1: 6-arg `__thiscall` signature is correct despite Ghidra rendering 5 args; Clar2: CastToShipClass uses class ID 0x8008) + 1 OQ. AoE 6-facing 1/6 split byte-confirmed at DAT_0088BACC = 0.16666 (0x3E2AAAAB).

# Collision-Shield Interaction

Reverse-engineered from stbc.exe via Ghidra decompilation. The 3-path narrative (collision / weapon / AoE) survives v5 validation; see the NOTE for the two localized corrections and the per-section markers (C1, C2) for the details.

**Corrects** an error in `damage-system.md` line 10, which labels `FUN_005afd70` as "visual/shield effect". It is actually the **SubsystemDamageDistributor** — the primary shield absorption and subsystem damage function for both collision and weapon paths.

## Executive Summary                                           [v5-validated 2026-05-28]

Collision damage does **not** bypass shields. It goes through the same `FUN_005AFD70` (SubsystemDamageDistributor) that weapon damage uses, which walks the ship+0x284 subsystem linked list and applies directional damage to shield facings. Shields absorb collision damage per facing, and only the overflow reaches hull and subsystems.

The key difference between damage paths is **where** shields are checked, not **whether** they are:

| Path | Shield Check Location | Type |
|------|----------------------|------|
| **Weapon** | Pre-DoDamage (ray-ellipsoid gate at FUN_0056A690) + inside FUN_005AFD70 | Binary gate + per-subsystem |
| **Collision** | Inside FUN_005AFD70 only (no pre-gate) | Per-subsystem only |
| **AoE Explosion** | Separate explicit loop (FUN_00593C10, uniform 1/6 per facing) | Area-effect |

## CollisionDamageWrapper (0x005B0060) — Three-Step Process   [v5-validated 2026-05-28]

### C2 — The wrapper chain has a normalization layer

The collision entry point calls three functions **sequentially**, not two:

```c
void __thiscall CollisionDamageWrapper(void *this, int collider, float searchRadius, float damage)
{
    // STEP 1: Subsystem-level damage (includes shield absorption)
    // damage is modified IN-PLACE — reduced by whatever shields/subsystems absorb
    FUN_005AFD70(this, (float*)(collider + 0x88), &damage, searchRadius, NULL, 1);

    // STEP 2: Position-normalization wrapper (NEW — see C2)
    // Transforms world position to scene-root-relative coords
    FUN_00593650(this, collider, searchRadius, damage);
    //     |
    //     +-> STEP 3: Real DamageVolume entry
    //         FUN_00594020 — allocates DamageVolume via FUN_004BBDE0
    //                       and calls ProcessDamage via FUN_00593E50
}
```

**C2 [LOW]** — The prior doc labeled `FUN_00593650` as `DoDamage_FromPosition`. Disasm at 0x005B008E shows `CALL 0x00593650`, but that function is a **position-normalization wrapper** that transforms the world-space origin to scene-root-relative coordinates and then calls `FUN_00594020`. The true `DoDamage_FromPosition` semantics (DamageVolume alloc + ProcessDamage dispatch) live in `FUN_00594020`. The doc's net-effect description ("remaining damage reaches ProcessDamage") was correct — only the function attribution was wrong.

**Critical detail**: `FUN_005AFD70` takes `&damage` (pointer), not `damage` (value). It modifies the damage amount in place. By the time `FUN_00594020` runs, the damage has been reduced by whatever shields and subsystems absorbed.

## FUN_005AFD70 — SubsystemDamageDistributor (0x005AFD70)     [v5-validated 2026-05-28]

This is the **primary shield interaction function** for both collision and weapon damage.

### Signature

```c
void __thiscall FUN_005AFD70(
    void *this,         // ship
    float *position,    // damage origin (world-space 3D point)
    float *damage,      // POINTER to damage amount (modified in place!)
    float searchRadius, // subsystem spatial search radius expansion (1.5 for collisions)
    int *source,        // attacker weapon pointer (NULL for collisions — OQ1)
    int *isCollision    // 0x1=collision, 0x0=weapon (controls power subsystem exclusion)
);
```

**Clar1**: Ghidra's decomp renders the signature as 5 args because `this` (ECX) is hidden by `__thiscall` calling convention. The disasm `RET 0x14` confirms the 6-arg form (4 stack args after `this` + `position`).

### Behavior

1. **Find subsystems in range** via `FUN_005AECC0`:
   - Walks `ship+0x284` linked list (state serialization list)
   - Checks each subsystem's distance from the damage origin point
   - Builds a hit list of subsystems within `searchRadius` × each subsystem's bounding radius
   - **Shield facings ARE in this list** — they are regular subsystems
   - The `searchRadius` value (1.5 for collisions) means "find subsystems within 1.5× their bounding radius from the damage origin" — it is a spatial search expansion factor, NOT a shield absorption multiplier

2. **Power subsystem exclusion** (weapon-only):
   ```c
   if (((char)isCollision == '\0') && (hit_count > 1)) {
       // Find and remove power subsystem (ship+0x2C4) from hit list
   }
   ```
   When `isCollision=0` (weapon) and multiple subsystems are hit, the power subsystem is removed from the list. When `isCollision=1` (collision), power subsystem stays in. Byte-confirmed at 0x005AFDCC (TEST AL,AL; JNZ) → 0x005AFDCE (CMP [ESP+0x10],0x1). This is the **only** behavioral difference between collision and weapon paths through this function. (Ship+0x2C4 PowerSubsystem pointer cross-anchored from `power-system.md`.)

3. **Per-subsystem damage** via `FUN_005AF4A0`:
   ```c
   // 5th arg is HARDCODED '\0' regardless of collision/weapon (at 0x005AFE3D)
   overflow = FUN_005AF4A0(this, subsystem, *damage, source, '\0');
   total_overflow += overflow;
   ```
   The `param_5` passed to the per-subsystem function is always `'\0'` — collision and weapon damage follow identical logic from this point.

4. **Write remaining damage back**:
   ```c
   *damage = total_overflow;  // reduced amount for FUN_00594020
   ```

## FUN_005AF4A0 — Per-Subsystem Damage (0x005AF4A0)            [v5-validated 2026-05-28]

Applies damage to a single subsystem (including shield facings). Returns overflow (damage the subsystem couldn't absorb).

```c
float10 __thiscall FUN_005AF4A0(void *ship, void *subsystem, float damage,
                                 int *source, char param_5)
{
    float curHP  = *(float*)(subsystem + 0x30);     // current HP
    float maxHP  = FUN_0056C310(subsystem);         // max HP (GetMaxCondition)
    float newHP  = curHP - damage;
    float overflow = 0.0f;

    if (newHP <= 0.0f) {
        overflow = -newHP;      // damage exceeded HP
        // ... destruction checks ...
    }

    // Apply new HP
    FUN_0056C470(ship, newHP);  // ShipSubsystem_SetCondition (NAMED) — clamps, fires SUBSYSTEM_HIT event
    return overflow;
}
```

When the subsystem is a shield facing:
- `subsystem+0x30` is the current shield facing HP
- Damage is subtracted directly from facing HP
- Overflow = damage that wasn't absorbed
- `FUN_0056C470` fires SUBSYSTEM_HIT event (0x0080006B)

## FUN_0056C470 — ShipSubsystem_SetCondition (0x0056C470)      [v5-validated 2026-05-28]

### C1 — Event class is TGObjPtrEvent, not TGCharEvent

The prior doc claimed the SUBSYSTEM_HIT event was a `TGCharEvent`. It is not. Decompilation of `ShipSubsystem_SetCondition` (named in Ghidra) shows:

```c
void __thiscall FUN_0056C470(void *this, float newCondition)
{
    *(float*)(this + 0x30) = newCondition;  // set new HP

    // Clamp to max
    float maxHP = FUN_0056C310(this);
    if (*(float*)(this + 0x30) > maxHP)
        *(float*)(this + 0x30) = maxHP;

    // Compute condition ratio
    *(float*)(this + 0x34) = *(float*)(this + 0x30) / maxHP;

    // Fire SUBSYSTEM_HIT event if HP < max AND ship alive
    if (*(float*)(this + 0x30) < maxHP && ship_is_alive) {
        // Allocate 0x2C bytes = TGObjPtrEvent size (NOT TGCharEvent)
        void *event = FUN_00717B70(0x2C);
        FUN_00718010(event, ...);
        TGObjPtrEvent_Ctor(event, 0);

        TGObjPtrEvent *pEvent = (TGObjPtrEvent*)event;
        pEvent->dwEvent_type = 0x0080006B;            // SUBSYSTEM_HIT (at TGObjPtrEvent+0x10)
        pEvent->nObj_ptr     = *(int*)(this + 0x04);  // subsystem object ID (at TGObjPtrEvent+0x28)

        FUN_006DA2A0(&DAT_0097F838, event);  // post to TGEventManager
    }
}
```

**C1 [MEDIUM]** — Class identity verified by allocation size: `FUN_00717B70(0x2C)` allocates 44 bytes, which matches `TGObjPtrEvent` (per protocol leaf #13, `tgobjptrevent-class.md`). `TGCharEvent` is the 18-byte SetPhaserLevel class (per protocol leaf #16, `set-phaser-level-protocol.md`) — wrong layout, wrong size. The constructor name `TGObjPtrEvent_Ctor` is plate-stamped in Ghidra at this call site.

**Impact**: The doc's pseudocode offsets (`event[4]`, `event[10]`) line up correctly with the TGObjPtrEvent layout (`dwEvent_type` at +0x10 = int-index 4; `nObj_ptr` at +0x28 = int-index 10), so any code reading the old text still worked accidentally. But OpenBC implementers naming the event class need the correct identity — TGObjPtrEvent, not TGCharEvent.

## Comparison: Weapon Path                                     [v5-validated 2026-05-28]

### WeaponHitHandler (FUN_005AF010)

Weapons have a **pre-gate** that stops most hits before reaching the subsystem distributor:

```
Projectile flight → ray-ellipsoid intersection test (FUN_0056A690)
  → weaponHitInfo+0x58 = 0 (shield absorbed) or != 0 (passed through)

WeaponHitHandler:
  if (hitInfo+0x58 == 0):       // ~72% of hits
      play shield visual
      RETURN                    // DoDamage is NEVER called

  if (hitInfo+0x58 != 0):       // ~28% pass shields
      play hull hit visual
      ApplyWeaponDamage → DoDamage → ProcessDamage
```

After passing this gate, weapon damage ALSO calls `FUN_005AFD70` (via `FUN_005AF630`), which does the same per-subsystem damage distribution with shield absorption.

### FUN_005AF630 — Weapon Subsystem Damage Caller

```c
// isCollision param for weapons:
int *isCollision = (int*)1;  // default
if (weapon_type == 1) {      // torpedo check at weapon+8
    torpedo = FUN_00570B20(weapon);
    if (torpedo != NULL && torpedo[0x2B] == 0) {   // weapon[0x2B] = +0xAC byte
        isCollision = (int*)0;  // some torpedoes set to 0 → power subsystem excluded
    }
}
FUN_005AFD70(ship, position, &damage, radius, weapon, isCollision);
```

## Comparison: AoE Explosion Path                              [v5-validated 2026-05-28]

### FUN_00593C10 — AoE Shield Drain (0x00593C10)

Explosions use a completely different mechanism — an explicit loop over all 6 shield facings with uniform damage distribution:

```c
void* shieldSubsys = ship[0xB0];  // ship+0x2C0 = ShieldGenerator*
if (shieldSubsys != NULL && shields_enabled && !cloaked) {
    float *shieldHP = (float*)(shieldSubsys + 0xA8);  // curShields[6]
    float perFacing = totalDamage * DAT_0088BACC;     // * 1/6 = 0x3E2AAAAB = 0.16666...

    for (int i = 0; i < 6; i++) {
        float absorbed = min(perFacing, shieldHP[i]);
        shieldHP[i] -= absorbed;
        FUN_0056A5C0(shieldSubsys, i, shieldHP[i]);  // SetCurShields
        totalAbsorbed += absorbed;
    }
    remainingDamage = totalDamage - totalAbsorbed;
}

if (remainingDamage > 0) {
    FUN_005AFD70(ship, pos, &remainingDamage, radius, source, param);
}
```

The AoE path drains shields FIRST (uniformly), THEN passes remaining damage to `FUN_005AFD70` for hull/subsystem distribution. The 1/6 constant `DAT_0088BACC = 0x3E2AAAAB = 0.16666...` is byte-confirmed.

## Summary: Three Damage Paths Through Shields                 [v5-validated 2026-05-28]

```
COLLISION:
  CollisionDamageWrapper (0x005B0060)
    ├─ FUN_005AFD70(&damage)         ← shield facings absorb, damage reduced in-place
    └─ FUN_00593650 (position norm.) ← C2: NEW wrapper layer
         └─ FUN_00594020             ← DamageVolume alloc via FUN_004BBDE0
              └─ FUN_00593E50         ← ProcessDamage (handler array)

WEAPON:
  WeaponHitHandler (FUN_005AF010)
    ├─ ray-ellipsoid gate            ← 72% stopped here (shield absorbed)
    └─ if passed:
         ├─ FUN_005AFD70(&damage)    ← same path as collision
         └─ ApplyWeaponDamage
              └─ DoDamage(damage * 2.0, radius * 0.5)
                   └─ ProcessDamage

AoE EXPLOSION:
  FUN_00593C10
    ├─ explicit 6-facing drain       ← uniform 1/6 (DAT_0088BACC) per facing
    └─ FUN_005AFD70(remaining)       ← hull/subsystem damage with reduced amount
```

## Why Collision Damage Often Appears to Bypass Shields

Several factors create the **perception** that collisions bypass shields:

1. **No pre-gate**: Weapons have the ray-ellipsoid test that stops 72% of hits before any damage function runs. Collisions have no such gate — 100% reach the damage path. This makes collision damage feel more impactful.

2. **Power subsystem stays in hit list**: Collisions with `isCollision=1` do NOT exclude the power subsystem, so collision damage can hit the warp core directly. Weapons exclude it (when `isCollision=0` and multiple subsystems hit).

3. **Multiple contact points**: Multi-contact collisions (`DoDamage_CollisionContacts`, FUN_005952D0) apply damage once per contact point, each going through shield absorption independently. This can overwhelm a single shield facing faster than a single weapon hit.

4. **Stock trace ratios**: In a 15-minute stock combat session:
   - 79,605 collision checks → 229 actual damage events (0.3% trigger rate)
   - 1,939 weapon hits → 536 pass shields (28% pass rate)
   - All 229 collision damage events reach DoDamage (100%)
   - Only 536/1939 weapon hits reach DoDamage (28%)

## Implications for OpenBC

The OpenBC `bc_combat_apply_damage` function currently uses `area_effect=true` for collision damage, which applies `damage/6` uniformly across all 6 shield facings. This is **incorrect** — it matches the AoE explosion path (`FUN_00593C10`), not the collision path.

The stock collision path does **directional** shield absorption via `FUN_005AFD70`, which finds subsystems (including shield facings) within range of the collision point and absorbs damage per facing based on spatial proximity. This means:

- A head-on collision drains **front shields** primarily, not all 6 facings equally
- Front shields can be depleted by collision while other facings remain full
- Once front shields are depleted, overflow hits hull + subsystems immediately

OpenBC should switch collision damage from area-effect to directed shield absorption.

When wiring the SUBSYSTEM_HIT event for hit feedback, allocate as **TGObjPtrEvent** (class size 0x2C, event-type 0x0080006B at +0x10, object pointer at +0x28) — not TGCharEvent (per C1).

## Open Questions

- **OQ1** — `FUN_005AFD70` 5th arg `source` is documented as NULL for the collision path (PUSH 0x0 at 0x005B0079). Whether the same parameter can be non-NULL via any other caller of `FUN_005AFD70` (e.g., AoE explosion, weapon paths) has not been verified by dataflow on all inbound xrefs. **Promotion path**: enumerate all callers of `FUN_005AFD70` and inspect each `source` argument to byte-confirm it's always NULL in practice (or document the exceptions).

## Related Documents

- [collision-detection-system.md](collision-detection-system.md) — Parent foundation: how the engine decides two objects collided
- [damage-system.md](damage-system.md) — Damage pipeline this leaf feeds into
- [shield-system.md](shield-system.md) — ShieldGenerator (ship+0x2C0) and the curShields[6] array
- [collision-rate-limiting.md](collision-rate-limiting.md) — Sibling leaf: per-pair rate limiter (ship+0xEC enable flag)
- [../protocol/tgobjptrevent-class.md](../protocol/tgobjptrevent-class.md) — TGObjPtrEvent class layout (factory 0x010C, size 0x2C) — what wraps the SUBSYSTEM_HIT event posted by FUN_0056C470
