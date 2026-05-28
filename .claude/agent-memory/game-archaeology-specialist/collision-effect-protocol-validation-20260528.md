---
name: collision-effect-protocol-validation-20260528
description: Protocol leaf #15 (collision-effect-protocol.md). Doc is rock-solid. ONE byte-level typo (handler-table 0x005afab0->0x005afad0); jump-table thunk address fix (0x0069F491 not 0x0069F4A5). All wire-format claims confirmed byte-by-byte. Distance gate = 26.0f (0x41D00000) at 0x008955C8 verified. Damage scaling constants 0.01f/900.0f/500.0f all verified. EventManager singleton at 0x0097F838 (thiscall PostEvent at 0x006DA2A0). WriteToStream/ReadFromStream/ctor/dtor ALL undefined-in-DB but real code (mirrors leaf #14 pattern).
metadata:
  type: project
---

# Collision-Effect-Protocol (Leaf #15) — Validation Summary

**Doc:** `docs/protocol/collision-effect-protocol.md` (~110 claims)
**Status:** verified (after 2 minor corrections)
**Date:** 2026-05-28

## Heavy lifters

- `CollisionEffectHandler` at 0x006A2470 (confirmed in dispatcher recovery memory; renamed + prototyped + plate)
- Dispatcher route: opcode 0x15 -> jump-table index 0x13 (= opcode - 2 bias) at 0x0069F534+0x4C -> thunk **0x0069F491** -> `CALL 0x006A2470`
- `Ship__HostCollisionEffectHandler` at 0x005AFAD0 (damage processing; renamed)

## Byte-by-byte confirmations

### Distance gate (Validation 3)
At 0x006A25DF: `FCOMP float ptr [0x008955C8]` reads 26.0f.
- `_DAT_008955C8` = bytes `00 00 D0 41` = 0x41D00000 = 26.0f **CONFIRMED**
- Algorithm:
  - `dist = sqrt((p1-p2).x^2 + (p1-p2).y^2 + (p1-p2).z^2)` via FSQRT at 006A25B7
  - `r1 = ship1->GetModelBound()[+0xC]` via vtable+0xE4 at 006A25BD
  - `r2 = ship2->GetModelBound()[+0xC]` via vtable+0xE4 at 006A25CE
  - `gap = dist - r1 - r2`
  - if `gap >= 26.0f` -> REJECT (JZ at 006A25EA)

### Damage scaling (HostCollisionEffectHandler decompile)
- `_DAT_00888A78` = 0x3C23D70A = **0.01f** (dead-zone) **CONFIRMED**
- `_DAT_008944BC` = 0x44610000 = **900.0f** (HP scale) **CONFIRMED**
- `_DAT_008944B8` = 0x43FA0000 = **500.0f** (HP base) **CONFIRMED**
- `_DAT_00888860` = 0x3F800000 = 1.0f (bounding sphere normalization base)
- Force scale 0x3FC00000 = **1.5f** (5th arg to FUN_005AFD70) **CONFIRMED**

### Event re-tag (006A25EC-006A25F9)
```
PUSH ESI                       ; event
MOV  ECX, 0x97F838             ; this = g_pEventManager
MOV  [ESI+0x10], 0x008000FC    ; event->type = ET_HOST_OBJECT_COLLISION
CALL TGEventManager__PostEvent ; FUN_006DA2A0 (was undocumented, now named)
```
- Confirms doc's "event manager at 0x0097F838" — but the function is __thiscall (ECX=this), not "post to DAT queue". `FUN_006DA2A0` thunks to `FUN_006DE330`.

### Vtable at 0x0089395C (CollisionEvent primary)
All 17 slots (offsets 0x00..0x40) verified byte-by-byte. Doc rows ALL match. Primary slots:
- +0x10 WriteStream (persistence) -> 0x00586FB0
- +0x14 ReadStream (persistence) -> 0x00587030
- +0x30 CopyFrom -> 0x00586E70
- **+0x34 WriteToStream (network) -> 0x005871A0**
- **+0x38 ReadFromStream (network) -> 0x00587300**
- +0x3C PostProcess -> 0x005874A0

## Two material corrections

### C1 — Handler-table 2-byte typo
Doc's "Event Registration" section (line 293):
```
ET_HOST_OBJECT_COLLISION (0x008000FC) -> ShipClass::HostCollisionEffectHandler (0x005afab0)
```
Should be `0x005AFAD0`. The main "Related Functions" table (line 318) has it correct. Just a 2-byte typo in the registration callout.

### C2 — Jump-table thunk address (doc doesn't cite this, but FYI)
The opcode 0x15 thunk is at **0x0069F491**, not 0x0069F4A5 (which is the opcode 0x17 thunk). Index = opcode - 2 = 0x13, offset into 0x0069F534+0x13*4 = 0x0069F580 reads `91 f4 69 00` = 0x0069F491. Disasm confirms `CALL 0x006A2470` inside that thunk.

## Real-code-but-undefined functions (matches leaf #14 SWIG pattern)

These have real prologue bytes but Ghidra auto-analysis never created the function entry. Most have only vtable-DATA xrefs (no plain CALL xrefs):
- 0x005871A0 CollisionEvent::WriteToStream (prologue `83 EC 30 53 55`)
- 0x00587300 CollisionEvent::ReadFromStream (prologue `83 EC 14 56 57`)
- 0x00586D00 CollisionEvent::ctor (prologue `6A FF 68 48 A7 87 00` — SEH frame setup, MSVC C++)
- 0x005AF9C0 ShipClass::CollisionEffectHandler (client-side sender; prologue with `MOV ECX,0x97FA89` IsHost check)
- 0x006D29A0 CompressVec4_Byte_Direction (vtable+0xA0, stream class)
- 0x006D2D10 CompressVec4_Byte_Magnitude (vtable+0xAC, stream class)

Decoded `Vec3 GetPointInternal(idx)` at 0x00595410:
```
this+0x2C = event->point_array (array of Vec3* pointers)
puVar1 = *(Vec3**)(*(int*)(this+0x2C) + idx*4)
*out = *puVar1 ; *(out+4) = puVar1[1] ; *(out+8) = puVar1[2]
```
Confirms doc's "Copies Vec3 from point_array[idx]" + event+0x2C layout.

## Server authority semantics — final word

Stock dedi **does NOT recompute** collision contact points or force magnitude. The only server-side validation:
1. Sender owns source OR target (ownership)
2. NOT (sender is source AND target is local player) (self-collision filter)
3. Bounding-sphere gap < 26.0f (distance sanity check)

All three are GEOMETRY/IDENTITY checks. The collision_force float and contact-point compressed bytes are accepted as-is and passed to `Ship__HostCollisionEffectHandler` which applies damage proportional to the client-claimed force.

This confirms CLAUDE.md's "Collision damage authority inverted — our server accepts client CollisionEffect(0x15) without server-side recomputation." OpenBC's gap is that it doesn't even do the 26.0f gap check, but stock isn't doing real recomputation either.

## v5 patterns applied

- 7 functions renamed (or named-only since pre-existing)
- 7 global labels created (cap, deadzone, scale, base, 3 event-type IDs)
- 1 prototype + plate on CollisionEffectHandler
- Cross-anchored to leaf #14 (PythonEvent) via the damage-PythonEvent cascade (collision -> 0x06 -> ObjectExploding/repair)
- Cross-anchored to dispatcher recovery via opcode-0x15 jump-table thunk

## Open questions

None blocking. The doc's hash-cascade claim "DamageableObject::CollisionEffectHandler" Python handler "Effects.CollisionEffect" via FUN_006D92D0 — string EXISTS at 0x008E5CC8, but DamageableObject vtable layout not re-derived here. Per scope, downstream damage handling lives in `docs/gameplay/damage-system.md`.
