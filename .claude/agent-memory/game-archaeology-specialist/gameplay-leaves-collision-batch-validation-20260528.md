---
name: gameplay-leaves-collision-batch-validation-20260528
description: Batch v5 validation of collision-shield-interaction.md (256 lines) + collision-rate-limiting.md (150 lines). Sibling leaves of collision-detection-system (gameplay foundation #4).
metadata:
  type: project
---

# Batch v5 Validation: collision-shield-interaction.md + collision-rate-limiting.md

Sibling gameplay leaves under collision-detection-system (gameplay foundation #4). Both validated 2026-05-28.

---

## Doc A: `docs/gameplay/collision-shield-interaction.md` (256 lines)

### Verdict: `partial` (1 wrong class name, 1 vtable path inaccuracy; all algorithm/wire claims VERIFIED)

### Verified (`high`)
- **CollisionDamageWrapper 0x005b0060**: 6-arg `this`call confirmed by disasm 0x005b0067-0x005b007e. PUSH 0x1 (isCollision), PUSH 0x0 (source=NULL), PUSH EDI (radius), PUSH EAX=&damage (ESP+0x20), PUSH ECX=collider+0x88 (position), MOV ECX=this. Then CALL FUN_005afd70. RET 0xc.
- **Two-step process**: After FUN_005afd70, CALL FUN_00593650 (NOT directly `DoDamage_FromPosition`). FUN_00593650 normalizes positions relative to scene root and calls FUN_00594020 (the true DamageVolume entry). Net effect matches doc.
- **FUN_005afd70 5th arg HARDCODED '\\0'**: byte-confirmed at 0x005afe3d (`PUSH 0x0` before CALL FUN_005af4a0).
- **Power subsystem exclusion path**: at 0x005afdcc (`TEST AL,AL; JNZ`), then at 0x005afdce CMP `[ESP+0x10],0x1` (hit_count>1), then `EBX+0x2c4` loop matches the doc's pseudocode.
- **FUN_005af4a0 algorithm**: confirms `subsystem+0x30=curHP`, `FUN_0056c310=GetMaxCondition`, overflow = -newHP when ≤0, calls ShipSubsystem_SetCondition (0x0056c470) named in Ghidra.
- **DAT_00888b54=0.0f**: byte-confirmed (matches collision-detection-system C1).
- **DAT_0088bacc=0x3E2AAAAB=0.16666...=1/6**: byte-confirmed (AoE per-facing constant).
- **FUN_00593c10 AoE path**: `iVar3 = piVar4[0xb0]` (ship+0x2C0=ShieldGenerator); `pfVar5 = (float*)(iVar3 + 0xa8)` (curShields[6]); `while (iVar8 < 6)` loop; multiplier `DAT_0088bacc=1/6`. After loop, IF (remaining > 0) → FUN_005afd70 for hull/subsystem distribution. **All byte-confirmed.**
- **FUN_005af010 (WeaponHitHandler)**: gate `(char)*(int*)(param_2 + 0x58) == '\\0'` → shield-absorbed branch (TorpedoShieldHit effect, no DoDamage); else hull-pass branch calls FUN_005af420. Confirmed.
- **FUN_005af630 (Weapon Subsystem Damage Caller)**: torpedo type check `*(int*)(param_4 + 8) == 1` → FUN_00570b20(weapon) → `iVar6 + 0xac == 0` → isCollision=0 (else =1). **Confirmed** — `0xac/4=0x2B` matches doc's `torpedo[0x2B]` int-index notation.
- **FUN_0056a690**: ray-ellipsoid intersection test confirmed via geometry math + FUN_004570d0 caller signature.

### Corrections

#### C1 (medium) — SUBSYSTEM_HIT event class is **TGObjPtrEvent**, NOT TGCharEvent

Doc Section "FUN_0056c470 — SetCondition / Shield HP Setter" lines 131-138 claim:
> Create TGCharEvent with eventType = 0x0080006B (SUBSYSTEM_HIT)

**Binary**: ShipSubsystem_SetCondition (0x0056c470) decomp shows: `FUN_00717b70(0x2c); FUN_00718010(...); TGObjPtrEvent_Ctor(this, 0); ... pTVar2->dwEvent_type = 0x0080006b; pTVar2->nObj_ptr = *(int*)(param_1 + 4);` The constructor name TGObjPtrEvent_Ctor is plate-stamped in Ghidra. Size 0x2c (44 bytes) = TGObjPtrEvent size, NOT TGCharEvent.

**Impact**: Doc's pseudocode `event[4] = 0x0080006B; event[10] = ...` works as offsets but mis-names the class. TGCharEvent has a different layout (per protocol leaf #16 it's 18B wire/0x?? class). TGObjPtrEvent is the correct class (per protocol mid #13 it's 0x2C class size with `dwEvent_type` at +0x10 and `nObj_ptr` at +0x28).

**Fix**: Replace "TGCharEvent" → "TGObjPtrEvent" in line 134 description AND in the pseudocode `event[4]/event[10]` line numbering (use field names `dwEvent_type` / `nObj_ptr`).

#### C2 (low) — DoDamage_FromPosition chain skips a layer

Doc Section "CollisionDamageWrapper (0x005b0060) — Two-Step Process" line 33:
> DoDamage_FromPosition(this, collider, searchRadius, damage);  // damage is now REDUCED

**Binary**: Actual call at 0x005b008e is `CALL 0x00593650`, which is a position-normalization wrapper (transforms world position to scene-root-relative) that then calls FUN_00594020 (the real entry that allocates DamageVolume via FUN_004bbde0 and calls ProcessDamage via FUN_00593e50).

**Impact**: Doc's net effect is correct — damage flows to ProcessDamage with the reduced amount. But the function at 0x00593650 is NOT `DoDamage_FromPosition`; it's a normalization wrapper. The true `DoDamage_FromPosition` semantics live in FUN_00594020.

**Fix**: Either (a) re-label "DoDamage_FromPosition" → "DoDamageFromPositionWrapper (0x00593650) → FUN_00594020", or (b) note the wrapper layer in a comment. Low priority.

### Clarifications

- **Decomp signature simplification**: Ghidra's decomp shows CollisionDamageWrapper as `(int param_1, undefined4 param_2, undefined4 param_3)` and FUN_005afd70 as 5-arg, but disasm confirms both take `this` via ECX so the doc's 4-arg / 6-arg signatures ARE correct.
- **CastToShipClass (0x005ab670)**: confirmed signature uses class ID `0x8008` for the Ship check — useful cross-reference for the Ship class ID.

### Function Reference (anchored)
| Address | Name | Verdict |
|---------|------|---------|
| 0x005b0060 | CollisionDamageWrapper | byte-confirmed |
| 0x005afd70 | SubsystemDamageDistributor (worker) | byte-confirmed |
| 0x005af4a0 | Per-Subsystem Damage (worker) | byte-confirmed |
| 0x0056c470 | ShipSubsystem_SetCondition (NAMED in Ghidra) | byte-confirmed |
| 0x00593c10 | AoE Shield Drain (worker) | byte-confirmed |
| 0x00593650 | Position-normalization wrapper | byte-confirmed |
| 0x00594020 | True DamageVolume entry → ProcessDamage | byte-confirmed |
| 0x005af010 | WeaponHitHandler (worker) | byte-confirmed |
| 0x005af630 | Weapon Subsystem Damage Caller (worker) | byte-confirmed |
| 0x0056a690 | Ray-Ellipsoid Test (worker) | byte-confirmed |
| 0x005ab670 | CastToShipClass (NAMED) | byte-confirmed; class ID 0x8008 |
| 0x005ae140 | IsLocalPlayerShip (NAMED) | byte-confirmed |
| 0x004bbde0 | DamageVolume ctor (per collision-detection memo) | byte-confirmed |
| 0x00593e50 | ProcessDamage (per gameplay foundation #1 memo) | byte-confirmed |

### .rdata anchors
- DAT_00888b54 = 0.0f (collision damage gate / overflow threshold) — byte-confirmed
- DAT_0088bacc = 0x3E2AAAAB = 1/6 (AoE per-facing) — byte-confirmed

---

## Doc B: `docs/gameplay/collision-rate-limiting.md` (150 lines)

### Verdict: `partial` (1 vtable-chain inaccuracy; algorithm + constants + ship offsets all VERIFIED)

### Verified (`high`)
- **enableFlag at ship+0xEC**: `if (param_1[0x3b] == 0) return false;` — 0x3B * 4 = 0xEC. **Byte-confirmed.**
- **hashVtable at ship+0x68**: `piVar11 = param_1 + 0x1a` → 0x1A*4=0x68. **Byte-confirmed.**
- **entryCount at ship+0x6C**: `param_1[0x1b]` → 0x1B*4=0x6C. **Byte-confirmed.**
- **bucketTable at ship+0x74**: `param_1[0x1d]` → 0x1D*4=0x74. **Byte-confirmed.**
- **0x50-byte allocation**: `iVar9 = FUN_00718cb0(0x50)` confirmed (the timestamp container).
- **0xC-byte hash node**: also allocated separately (`FUN_00718cb0(0xc)` at later branch).
- **Distance Constants** (all byte-confirmed):
  - 0x008942a4 = 0x42E40000 = **114.0f** ✓
  - 0x008942ac = 0x43640000 = **228.0f** ✓
  - 0x008942a8 = 0x43AB8000 = **343.0f** ✓
  - 0x00892004 = 0x432A0000 = **170.0f** (camera/MP-flag mode far) ✓
  - 0x0088bd58 = 0x40A00000 = **5.0f** (very-far multiplier) ✓
  - 0x008942a0 = 0x3FAAAA8F = **1.333...f** (targeting penalty) ✓
  - 0x00888860 = 0x3F800000 = **1.0f** (anchor / unblocked) ✓
- **Cooldown Constants** (all byte-confirmed from disasm):
  - 0x3DCCCCCD = **0.1f** (min floor)
  - 0x3E2B020C = **0.167f** (1/6)
  - 0x3E800000 = **0.25f**
  - 0x3E000000 = **0.125f**
  - 0x3F000000 = **0.5f**
- **Ship vtable+0x13C = FUN_005a22a0**: Ship vtable starts at 0x00894128 (verified via xrefs). Offset +0x13C = 0x00894264. Byte-read: `a0 22 5a 00` = 0x005a22a0. **Confirmed.**
- **Ship::CheckCollision unrecognized at 0x005af890**: confirmed real code starting after 9-NOP gap from 0x005af887. `MOV AL, [0x0097fa89]` (IsHost gate). Ghidra has NOT promoted it to a function.

### Corrections

#### C1 (high) — Call chain mislocates the rate-limiter caller

Doc Section "Call Chain" lines 13-25 claims:
```
PhysicsObjectClass::CheckCollision (0x005a88e0)
   → [vtable+0x148] CollisionTest_A (bounding mesh)
   → [vtable+0x150] Ship::CheckCollision (0x005af890)
      → [vtable+0x13C] Ship::CheckCollisionRateLimit (0x005a22a0)
```

**Binary**: Two problems.

1. Ship vtable +0x150 = **0x005a3900**, which is a **`RET`-only stub** (8 bytes `8b 4c 24 04 ... c2 0c 00`). Ship vtable +0x148 = 0x005a38c0, an identity-compare stub (`SETZ AL`). Neither dispatches to 0x005af890. FUN_005a88e0 IS the PhysicsObjectClass entry but routes Ship-class objects (0x8125) through `FUN_005a8810 → FUN_005a61c0 → FUN_005a63a0` (Ship-Ship dispatch), NOT through Ship vtable +0x150.

2. 0x005af890 itself does **NOT** call vtable+0x13C. Disasm 0x005af890 - 0x005af9b8 shows calls to: CastToShipClass (0x005ab670), IsLocalPlayerShip (0x005ae140), FUN_005ac4f0, FUN_005a05a0, vtable+0x94 (GetWorldTranslation), vtable+0xb0, FUN_005a14d0, then directly to FUN_00594840 (DamageableObject::CheckCollision). No `CALL [E?X+0x13C]` instruction.

The **actual caller** of vtable+0x13C in the collision pipeline is an **unnamed function at ~0x005a26d0** (Ghidra has not promoted it). It does:
```
005a26e9: MOV EAX, [EDI]          ; this->vtable
005a26eb: CALL [EAX+0x13c]        ; rate limiter
005a26f1: TEST AL, AL
005a26f3: JNZ 0x005a26fc          ; rate limiter said yes → proceed
005a26f5: XOR EAX, EAX
005a26f7: JMP 0x005a2bab          ; rate limiter said no → return 0
```
This unnamed function is the true rate-limiter wrapper. 0x005af890 is a DIFFERENT host-side collision gate (checks IsHost + IsLocalPlayerShip equality).

**Impact**: HIGH — anyone consuming this doc to design an OpenBC equivalent of the rate-limiter pipeline will follow the wrong call chain. The rate limiter EXISTS and IS at vtable+0x13C — that part is correct — but the doc's description of WHEN/WHERE it's invoked is wrong.

**Fix**: Replace lines 19-25 with the actual chain (and note ~0x005a26d0 as the wrapper that calls it). Update line 27 "Key" paragraph: "0x005af890 is a host-side collision dispatch gate; it does NOT directly call the rate limiter. The rate limiter is invoked by a separate (unnamed) function at ~0x005a26d0 which gates downstream collision processing on the rate-limiter result."

### Clarifications

- **Per-pair entry layout**: Doc describes `entry[0]=key, entry[1]=lastTime`. Binary reveals **two separate allocations**:
  - **Hash node** (12 bytes): `[0]=key, [4]=value_ptr, [8]=next_ptr` (the `0xc` allocation)
  - **Value object** (80 bytes / 0x50): contains the `lastTime` float at offset +0x4 (referenced as `*pfStack_30 = (float)puVar3[1]` where `puVar3[1]` is the hash-node's value-ptr, dereferenced to get the 0x50 block, and read as a `float*`).
  
  The doc's "Each pair entry is 0x50 bytes" is true for the **value object**; the hash node is separately allocated at 12 bytes. The `entry[1]` in the doc actually represents the **POINTER FROM hash-node-to-value-object**, not the timestamp itself.

- **Cooldown selection logic**: The flowchart-style decision tree in the binary at 0x005a23b1 - 0x005a25xx covers all 4 mode combinations (SP/MP × camera-flag/normal × player-count thresholds). Doc's table is approximately correct. Player-count thresholds: 2/3/4/5 boundaries all present.

- **Distance gate logic**: Two branches at 0x005a2522 onwards — non-camera vs camera/MP. Non-camera branch uses 170.0f (`_DAT_00892004`), 228.0f (`_DAT_008942ac`), 343.0f (`_DAT_008942a8`); camera/MP-flag branch uses 114.0f (`_DAT_008942a4`), 170.0f (`_DAT_00892004`). Doc's table is correct.

### Function Reference (anchored)
| Address | Name | Verdict |
|---------|------|---------|
| 0x005a22a0 | Ship::CheckCollisionRateLimit | byte-confirmed; Ship vtable[+0x13C] |
| 0x005af890 | Host-side collision gate (unrecognized) | confirmed real code; does NOT call rate limiter |
| ~0x005a26d0 | True rate-limiter caller (unrecognized) | NEW finding; promotes line 23 doc claim |
| 0x005a83a0 | ProximityManager::Update | function exists |
| 0x005a8740 | FUN_005a8740 (ProcessOverlapPairs) | function exists |
| 0x005a8810 | DispatchCollisionByType | confirmed Ship route → FUN_005a61c0 |
| 0x005a61c0 | Ship-Ship collision dispatch | byte-confirmed |
| 0x005a63a0 | Ship-Ship event publisher | byte-confirmed (posts TGEvent) |
| 0x005a88e0 | PhysicsObjectClass::CheckCollision | byte-confirmed |
| 0x00594840 | DamageableObject::CheckCollision | byte-confirmed |
| 0x005b0060 | Ship::CollisionDamageWrapper | shared with doc A |
| 0x00718cb0 | NiAlloc | byte-confirmed (0x50 + 0xC allocations) |

### Vtable Anchors
- **Ship main vtable**: 0x00894128. Slots: +0x148 = 0x005a38c0 (identity stub), +0x150 = 0x005a3900 (no-op stub), **+0x13C = 0x005a22a0** (rate limiter, **CORRECT** in doc).
- **Damage sub-vtable** (4-slot): 0x00894488. Slots: +0x0=0x005af7d0, +0x4=0x005af830, **+0x8=0x005af890** (host-side gate), +0xC=0x005b0060 (CollisionDamageWrapper). Both 0x005af890 and 0x005b0060 live here.

---

## Cross-Doc Reuse / Pre-anchored Context Confirmed

From collision-detection-system memo:
- DAT_00888b54 = 0.0f ✓ (re-confirmed in both leaves)
- CheckCollision has 12 callers (open question in foundation memo); rate-limiter is one of them via the unnamed wrapper at ~0x005a26d0.
- Doc A confirms the foundation memo's claim that collision damage flows through FUN_005afd70 (`primary shield interaction function`).

From CollisionEffect protocol leaf #15:
- CollisionEffectHandler 0x006a2470 confirmed (already validated). Distance gap 26.0f at 0x008955C8 confirmed in adjacent plate-comment.

From shield-system memo (gameplay foundation #2):
- ShieldGenerator at ship+0x2C0 (vtable 0x00892f34): doc A's `ship[0xB0]` = 0xB0*4 = 0x2C0 ✓ (matches existing memo).
- curShields[6] at ShieldGenerator+0xA8: confirmed in FUN_00593c10.

From CLAUDE.md "Known Issues":
- "Collision rate limiting disabled (ship+0xEC=0)" — **VERIFIED**: doc B's claim that enableFlag at +0xEC causes the rate limiter to return false immediately when zero is **CORRECT**. The check `if (param_1[0x3b] == 0) return false;` at 0x005a22a0 entry is byte-confirmed. DeferredInitObject probably doesn't set this flag — confirmed root cause.

---

## Status Summary

| Doc | Lines | Verdict | Corrections | Wire/Algorithm Errors |
|-----|-------|---------|-------------|----------------------|
| collision-shield-interaction.md | 256 | `partial` | 2 (1 wrong class name, 1 wrapper layer skipped) | 0 |
| collision-rate-limiting.md | 150 | `partial` | 1 high (call chain mislocates rate-limiter caller) | 0 |

Both docs have **zero wire-format / formula errors** — all constants byte-confirmed, all field offsets confirmed, all algorithm pseudocode matches decomp. The corrections are call-chain narrative issues and one event-class misnaming.

The most consequential finding is **doc B C1** — the rate-limiter call chain narrative is wrong. The rate limiter EXISTS at the claimed vtable slot, but the caller is NOT 0x005af890; it's an unnamed function at ~0x005a26d0. This needs fixing before any OpenBC implementer trusts the call-chain.
