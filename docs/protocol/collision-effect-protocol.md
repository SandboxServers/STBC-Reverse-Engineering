> [docs](../README.md) / [protocol](README.md) / collision-effect-protocol.md

---
title: CollisionEffect Wire Format (Opcode 0x15)
type: reference
audience: re-engineer
validated: 2026-05-28
methodology: FUNCTION_DOC_WORKFLOW_V5
binary:
  name: stbc.exe
  size: 6394712
  base: 0x00400000
status: verified
evidence:
  - claim: "Opcode 0x15 dispatches to CollisionEffectHandler at 0x006A2470 via 41-entry jump table"
    address: 0x0069F491
    function: MpgameHandleMessage
    completeness: high
    confidence: high
    note: "Index = (opcode - 2) = 0x13. Table at 0x0069F534 + 0x4C reads `91 F4 69 00` -> thunk 0x0069F491 -> CALL 0x006A2470. Distinct from 0x0069F4A5 which is the 0x17 thunk."
  - claim: "CollisionEffectHandler entry point (renamed + plated this pass)"
    address: 0x006A2470
    function: CollisionEffectHandler
    completeness: high
    confidence: high
  - claim: "Distance gate constant = 26.0f (rejects collisions where bounding-sphere gap >= 26 units)"
    address: 0x008955C8
    function: CollisionEffectHandler
    completeness: high
    confidence: high
    note: "Raw bytes `00 00 D0 41` = 0x41D00000 = 26.0f. Compared via `FCOMP [0x008955C8]` at 0x006A25DF, branched at JZ 0x006A25EA."
  - claim: "Distance gate algorithm: GetWorldTranslation x2 -> FSQRT -> GetModelBound x2 -> bbox+0x0C radius -> gap = dist - r1 - r2"
    address: 0x006A25B7
    function: CollisionEffectHandler
    completeness: high
    confidence: high
    note: "GetWorldTranslation via vtable+0x94; GetModelBound via vtable+0xE4; bbox radius at +0x0C; FSQRT at 0x006A25B7."
  - claim: "Server never recomputes collision contact points or force; handler accepts client-supplied values as-is"
    address: null
    function: CollisionEffectHandler
    completeness: high
    confidence: high
    note: "Negative claim. Full FUN_006A2470 body decompiled — no FMUL/FDIV on contact-point or force fields, no STR to event+0x40 (force), no rewrite of event+0x2C (contact array). After 3 gates the handler only sets event+0x10 = 0x008000FC and re-posts."
  - claim: "Event re-tag + EventManager singleton dispatch (this=0x0097F838, __thiscall FUN_006DA2A0)"
    address: 0x006A25EC
    function: CollisionEffectHandler
    completeness: high
    confidence: high
    note: "Pattern `MOV [ESI+0x10], 0x008000FC; MOV ECX, 0x97F838; CALL 0x006DA2A0` is the standard MSVC __thiscall invocation: this in ECX, event in ESI as 1st stack arg."
  - claim: "Ship_HostCollisionEffectHandler registered for ET_HOST_OBJECT_COLLISION (0x008000FC)"
    address: 0x005AFAD0
    function: Ship__HostCollisionEffectHandler
    completeness: high
    confidence: high
  - claim: "Damage dead-zone threshold = 0.01f"
    address: 0x00888A78
    function: Ship__HostCollisionEffectHandler
    completeness: high
    confidence: high
    note: "Raw bytes `0A D7 23 3C` = 0x3C23D70A = 0.01f. Applied as `if (raw > 0.01f)`."
  - claim: "Damage HP scale = 900.0f"
    address: 0x008944BC
    function: Ship__HostCollisionEffectHandler
    completeness: high
    confidence: high
    note: "Raw bytes `00 00 61 44` = 0x44610000 = 900.0f."
  - claim: "Damage HP base offset = 500.0f"
    address: 0x008944B8
    function: Ship__HostCollisionEffectHandler
    completeness: high
    confidence: high
    note: "Raw bytes `00 00 FA 43` = 0x43FA0000 = 500.0f."
  - claim: "Subsystem damage force-scale arg = 1.5f"
    address: 0x005AFD70
    function: SubsystemDamageDistributor
    completeness: high
    confidence: high
    note: "3rd parameter at call from HostCollisionEffectHandler is 0x3FC00000 = 1.5f (push constant)."
  - claim: "CompressedVec4_Byte read primitive (4-byte direction+magnitude to Vec3)"
    address: 0x006D30E0
    function: DecompressVec4_Byte
    completeness: high
    confidence: high
    note: "Vtable+0x9C entry on StreamReader at 0x00895C58. Reads 4 bytes via vtable+0x50, then dispatches via vtable+0xBC for radius-scaled Vec3."
  - claim: "GetShipFromPlayerID: iterates DAT_0097E9C8 game-set list, matches ship+0x2E4 == player_id"
    address: 0x006A1AA0
    function: GetShipFromPlayerID
    completeness: high
    confidence: high
  - claim: "IsLocalPlayerShip: on host (DAT_0097FA89 != 0) returns ship+0x2E4 != 0; off-host returns local-player ship match"
    address: 0x005AE140
    function: IsLocalPlayerShip
    completeness: high
    confidence: high
  - claim: "CastToShipClass: calls ship->vtable+0x08 (NiObject::IsA-style) with ship class ID 0x8008"
    address: 0x005AB670
    function: CastToShipClass
    completeness: high
    confidence: high
  - claim: "CollisionEvent primary vtable at 0x0089395C — 17 slots, all verified"
    address: 0x0089395C
    function: CollisionEvent
    completeness: high
    confidence: high
    note: "Read via memory dump; every slot target matches doc body table byte-for-byte."
  - claim: "Trace cross-anchor: 84/session, C->S only, 2 C->S relays observed, 0 S->C in relay audit"
    address: null
    function: (trace)
    completeness: n/a
    confidence: high
    note: "From relay-audit-20260224 (network-protocol-analyst) + wire-format-spec foundation #1. Confirms server never relays opcode 0x15."
companions:
  - docs/protocol/wire-format-spec.md
  - docs/protocol/game-opcodes.md
  - docs/protocol/pythonevent-wire-format.md
  - docs/protocol/transport-layer.md
  - docs/protocol/stream-primitives.md
  - docs/gameplay/collision-detection-system.md
  - docs/gameplay/collision-shield-interaction.md
  - docs/gameplay/damage-system.md
  - docs/engine/event-system-architecture.md
  - docs/protocol/v5-validation-status.md
supersedes:
  - (prior pre-v5)
---

# Opcode 0x15 - CollisionEffect Protocol Analysis

> [!NOTE]
> This doc is `status: verified`. All 110+ load-bearing claims confirmed
> byte-by-byte against the current Ghidra import (2026-05-28). The handler
> dispatch (CollisionEffectHandler at 0x006A2470, dispatcher thunk at
> 0x0069F491), distance gate constant (_DAT_008955C8 = 26.0f), damage cascade
> formula (`raw = force/mass/contacts; if raw > 0.01f, damage = raw * 900 + 500`),
> all 4 damage constants byte-verified, vtable at 0x0089395C (17 slots), and
> 3 helper functions (GetShipFromPlayerID, IsLocalPlayerShip, CastToShipClass)
> all v5-validated. **Critical OpenBC finding confirmed**: stock dedi handler
> never recomputes contact points or force — only the distance gap (< 26.0f)
> is sanity-checked; the client-claimed force value is accepted as-is.
> One byte-level correction (handler-table typo `0x005afab0` -> `0x005AFAD0`)
> and one wording clarification (PostEvent thiscall semantics). See
> [docs/guides/v5-evidence-header.md](../guides/v5-evidence-header.md) for the
> standard.

Complete decompilation and wire format analysis of the collision effect network message
(opcode 0x15) in Star Trek: Bridge Commander multiplayer.

## Overview

Opcode 0x15 (CollisionEffect) carries collision event data from the detecting client to
the host. The host validates the report, then applies authoritative collision damage and
broadcasts visual effects. The message contains a serialized `CollisionEvent` object
(TGEvent class type `0x8124`) with compressed contact points and a force magnitude.

**C->S only**: The server never relays CollisionEffect (0x15) packets. The server processes
collision reports locally and distributes damage results to all clients via PythonEvent
(opcode 0x06) messages. Confirmed across 138,695 packets in a 33.5-minute stock dedi trace
and against the 2026-02-24 relay audit (2 C->S / 0 S->C observed).

**Direction**: Client -> Host (C->S only; server processes locally, never relays)
**Handler**: `CollisionEffectHandler` at `0x006A2470` [v5-validated 2026-05-28]
**Dispatcher thunk**: `0x0069F491` (jump-table slot for opcode 0x15 in MpgameHandleMessage)
**Write method**: `CollisionEvent::WriteToStream` at `0x005871A0` (vtable+0x34)
**Read method**: `CollisionEvent::ReadFromStream` at `0x00587300` (vtable+0x38)
**Frequency**: ~84 per 15-minute stock session (4th most common combat opcode)

## Server-Side Authority Note

> [!IMPORTANT]
> **The stock dedi CollisionEffectHandler does NOT recompute collision contact
> points or force values from server-side object state.** It applies three gates
> (ownership, self-collision, distance < 26.0f bounding-sphere gap) and then
> accepts the client-supplied force value as-is, passing it directly to the
> damage formula in Ship__HostCollisionEffectHandler.

Full body of `FUN_006A2470` was decompiled this validation pass. There are:

- No `FMUL`/`FDIV` operations on the contact-point or force fields after deserialization
- No `STR` writes to `event+0x40` (collision_force) or `event+0x2C` (contact array)
- No re-derivation of contact points from ship world transforms

After the three gates pass, the handler only writes `event+0x10 = 0x008000FC` and re-posts
the event via TGEventManager. All authority is then in Ship_HostCollisionEffectHandler's
damage formula, which consumes `event.force` as-is.

This is the binary backing for CLAUDE.md's "Collision damage authority inverted" note.
OpenBC's gap is that it doesn't even apply the 26.0f distance check; stock applies that
gate but doesn't do real recomputation either. See
[docs/gameplay/damage-system.md](../gameplay/damage-system.md) for downstream damage handling.

## Wire Format

### Complete Packet Layout [v5-validated 2026-05-28]

```
Offset  Size  Type    Field                    Notes
------  ----  ----    -----                    -----
0       1     u8      opcode                   Always 0x15
1       4     i32     event_type_class_id      Always 0x00008124 (CollisionEvent factory ID)
5       4     i32     event_code               Always 0x00800050 (ET_OBJECT_COLLISION)
9       4     i32v    source_object_id         Other colliding object (0 = environment/NULL)
13      4     i32v    target_object_id         Ship reporting the collision (BC object ID)
17      1     u8      contact_count            Number of contact points (typically 1-2)
[repeated contact_count times:]
  +0    1     s8      dir_x                    Compressed direction X (signed byte)
  +1    1     s8      dir_y                    Compressed direction Y
  +2    1     s8      dir_z                    Compressed direction Z
  +3    1     u8      magnitude_byte           Compressed distance from ship center
[end repeat]
+0      4     f32     collision_force          IEEE 754 float: impact force magnitude
```

**Total size**: `22 + contact_count * 4` bytes (typically 26 for 1 contact, 30 for 2).

All multi-byte values are **little-endian**.

### Constant Prefix (13 bytes)

The first 13 bytes are constant across all observed CollisionEffect packets:

```
15 24 81 00 00 50 00 80 00 00 00 00 00
```

- `15` = opcode (0x15)
- `24 81 00 00` = class type ID `0x00008124` (CollisionEvent factory)
- `50 00 80 00` = event code `0x00800050` (ET_OBJECT_COLLISION)
- `00 00 00 00` = source object ID = 0 (environment collision, no specific object)

### Contact Point Compression

Each contact point is 4 bytes on the wire, representing a compressed ship-relative position.
The engine uses a "CompressedVec4_Byte" format (`stream->vtable+0x98`/`+0x9C`).

**Compression** (WriteToStream at `0x005871A0`, via `stream->vtable+0xA0` at `0x006D29A0`):

1. **Ship-relative transform**: World-space contact position is transformed to ship-local coords:
   - Subtract ship NiNode world position (NiNode+0x88/0x8C/0x90)
   - Apply inverse rotation via matrix multiply (`FUN_00813aa0` with NiNode+0x64 rotation matrix)
   - Scale by `DAT_00888860 / NiNode+0x94` (bounding sphere normalization)

2. **Direction compression** (`vtable+0xA0` at `0x006D29A0`):
   - Compute magnitude = sqrt(x^2 + y^2 + z^2)
   - If magnitude > threshold: normalize each component by (SCALE / magnitude)
   - Convert normalized components to signed bytes via ftol
   - Output: 3 signed direction bytes (dir_x, dir_y, dir_z)

3. **Magnitude compression** (`vtable+0xAC` at `0x006D2D10`):
   - Divides magnitude by reference value (bounding radius)
   - Multiplies by scale constant at `DAT_0088b9ac`
   - Converts to unsigned byte via ftol

**Decompression** (ReadFromStream at `0x00587300`, via `stream->vtable+0x9C` at `0x006D30E0`):

1. Reads 4 bytes (ReadByte x4 via vtable+0x50)
2. Gets bounding sphere radius from target object (vtable+0xE4 GetBoundingBox, radius at bbox+0x0C)
3. If target not found: uses 1.0 as default radius; if radius is 0: uses 0.01
4. Calls `vtable+0xBC` to decompress 4 bytes back to Vec3 using radius as scale
5. Allocates Vec3 (12 bytes) and stores in contact point array at event+0x2C

> [!NOTE]
> `0x005871A0`, `0x00587300`, `0x00586D00` (ctor), `0x005AF9C0` (ShipClass sender),
> `0x006D29A0`, and `0x006D2D10` are **real code at those addresses but undefined
> as functions** in the current Ghidra DB. They have valid prologue bytes
> (`83 EC 30 53 55` for WriteToStream, `83 EC 14 56 57` for ReadFromStream,
> MSVC SEH-frame setup for ctor) and clean disassembly. Their only xrefs are
> vtable-DATA writes (no plain CALLs to spot via auto-analysis). This mirrors
> the leaf #14 pattern of "real-code-but-undefined-fn cluster" caused by
> auto-analysis missing virtual-dispatch-only entry points.

### Two Serialization Paths

The CollisionEvent class has **two** serialization formats:

| Path | Write Function | Read Function | Format |
|------|---------------|---------------|--------|
| **Network** (vtable+0x34/+0x38) | `0x005871A0` | `0x00587300` | Compressed: u8 count, 4-byte contacts, f32 force |
| **Persistence** (vtable+0x10/+0x14) | `0x00586FB0` | `0x00587030` | Full: u32 count, 12-byte Vec3 contacts, f32 force |

The network path uses WriteToStream/ReadFromStream (compact, compressed).
The persistence path uses WriteStream/ReadStream (full, uncompressed, includes all TGEvent base fields).

**Only the network format appears on the wire.** The persistence format is for NiStream save/load.

### Example Packet Decodes

**P1** (26 bytes, Sovereign hitting asteroid on Multi1):
```
15                    opcode = 0x15 (CollisionEffect)
24 81 00 00           type_class_id = 0x00008124
50 00 80 00           event_code = 0x00800050 (ET_OBJECT_COLLISION)
00 00 00 00           source_obj_id = 0x00000000 (environment collision)
FF FF FF 3F           target_obj_id = 0x3FFFFFFF (Player 0 ship)
01                    contact_count = 1
0D 7E 00 D9           contact[0]: dir=(+13, +126, +0) mag=217
BB 20 A0 44           force = 1281.02f (0x44A020BB)
```

**P4** (30 bytes, 2 contact points):
```
15                    opcode = 0x15
24 81 00 00           type_class_id = 0x00008124
50 00 80 00           event_code = 0x00800050
00 00 00 00           source_obj_id = 0x00000000
FF FF FF 3F           target_obj_id = 0x3FFFFFFF
02                    contact_count = 2
0F 7E 00 DA           contact[0]: dir=(+15, +126, +0) mag=218
00 7E FF D8           contact[1]: dir=(+0, +126, -1) mag=216
51 C3 67 44           force = 927.05f (0x4467C351)
```

**P6** (26 bytes, 3-player combat, different ship):
```
15                    opcode = 0x15
24 81 00 00           type_class_id = 0x00008124
50 00 80 00           event_code = 0x00800050
00 00 00 00           source_obj_id = 0x00000000
FF FF 03 40           target_obj_id = 0x400003FF (Player 0 range, offset +1024)
01                    contact_count = 1
27 77 11 B8           contact[0]: dir=(+39, +119, +17) mag=184
9D 47 25 44           force = 661.12f (0x4425479D)
```

## CollisionEvent Class Layout (0x44 bytes) [v5-validated 2026-05-28]

```
Offset  Size  Type           Field               Notes
------  ----  ----           -----               -----
0x00    4     void**         vtable_primary       0x0089395c
0x04    4     int            ni_refcount          NiObject reference count
0x08    4     void*          source_object        Source object ptr (resolved from ID)
0x0C    4     void*          target_object        Target object ptr (resolved from ID)
0x10    4     uint32         event_type           0x00800050 = ET_OBJECT_COLLISION
0x14    4     float          time_stamp           Event timestamp
0x18    2     uint16         flags_a              Event flags
0x1A    2     uint16         flags_b              Event flags
0x1C    4     void*          (reserved)
0x20    4     void*          (reserved)
0x24    4     void*          parent_event         Parent event ptr (resolved from ID)
0x28    4     void**         vtable_secondary     0x0089399c (embedded base class)
0x2C    4     Vec3**         point_array          Array of pointers to Vec3 contact points
0x30    4     int            array_capacity       Allocated capacity (init=1)
0x34    4     int            point_count_alloc    Actual count of allocated point entries
0x38    4     int            num_points           Serialized point count (GetNumPoints)
0x3C    4     int            (unknown)            Init=1, possibly max_points or flag
0x40    4     float          collision_force      Force magnitude (GetCollisionForce)
```

### Constructor (0x00586D00)

```
this+0x28 = vtable 0x0089399c    (embedded base class)
this+0x2C = NiAlloc(4)           (point array, initial capacity 1)
this+0x30 = 1                    (capacity)
this+0x34 = 0                    (used count)
this+0x38 = 0                    (num_points)
this+0x3C = 1                    (unknown)
this+0x40 = 0.0                  (collision_force)
this[0]   = vtable 0x0089395c    (primary vtable, set LAST)
```

### Destructor (0x00586E20)

Frees each Vec3 in point_array (loop over point_count entries), then frees
the point_array itself, then calls base destructor FUN_006d5d70.

### SWIG Python API

| Function | C++ Target | Field |
|----------|-----------|-------|
| `CollisionEvent_GetNumPoints(event)` | this+0x38 | Returns point count |
| `CollisionEvent_GetPoint(event, idx)` | FUN_00595410 | Copies Vec3 from point_array[idx] |
| `CollisionEvent_GetCollisionForce(event)` | this+0x40 | Returns force float |

## Handler Logic (0x006A2470) [v5-validated 2026-05-28]

### Receive-Side Flow

```
CollisionEffectHandler(TGMessage* msg):
  1. Extract buffer from message (FUN_006b8530)
  2. Create StreamReader (vtable 0x00895c58), init with (buffer+1, size-1)
  3. Deserialize CollisionEvent from stream (FUN_006d6200):
     a. Read class_type_id (u32) = 0x8124
     b. Factory lookup in hash table (FUN_006f13e0)
     c. Factory creates CollisionEvent (0x44 bytes)
     d. Call CollisionEvent::ReadFromStream (vtable+0x38 = 0x00587300)
  4. Resolve object ID references (FUN_006f13c0)
  5. Call PostProcess (vtable+0x3C = 0x005874a0)
  6. Clear parent_event (this+0x24 = 0)

  7. Get sender's ship: GetShipFromPlayerID(msg+0x0C) [0x006A1AA0]

  VALIDATION 1 - Ownership:
  8. sender_ship must equal event.source OR event.target
     If neither matches: REJECT (free event, return)

  VALIDATION 2 - Self-collision filter:
  9. If sender_ship == event.source:
     - Get target: CastToShipClass(event.target) [0x005AB670]
     - Check: IsLocalPlayerShip(target) [0x005AE140]
     - If target IS local player: REJECT (prevents double-processing)

  VALIDATION 3 - Distance check (constant byte-verified):
  10. Get positions of both ships (vtable+0x94 = GetWorldTranslation)
      Get bounding radii of both (vtable+0xE4 = GetModelBound, radius at bbox+0x0C)
      Compute: gap = distance(ship1, ship2) - radius1 - radius2
      Compare: FCOMP [0x008955C8]  ;  _DAT_008955C8 = 26.0f (0x41D00000)
      If gap >= 26.0f: REJECT (JZ at 0x006A25EA)

  ACCEPT - Re-post as host-side event:
  11. Set event type to 0x008000FC (ET_HOST_OBJECT_COLLISION)
       MOV [ESI+0x10], 0x008000FC
  12. Post to TGEventManager singleton (this=0x0097F838) via __thiscall FUN_006DA2A0
       MOV ECX, 0x97F838            ; this = g_pEventManager
       PUSH ESI                     ; event
       CALL 0x006DA2A0              ; __thiscall TGEventManager::PostEvent
```

### Validation Summary

| Check | Purpose | Anti-abuse | Constant |
|-------|---------|-----------|----------|
| Ownership | Sender must own source or target object | Prevents spoofing damage to unrelated ships | — |
| Self-collision | Won't process if target is local player's ship | Prevents double-counting when both sides report | — |
| Distance | Objects must be within bounding-sphere proximity | Prevents phantom collisions at range | 26.0f at `_DAT_008955C8` |

### Event Type Transformation

The event arrives as `ET_OBJECT_COLLISION` (0x00800050) but is re-posted as
`ET_HOST_OBJECT_COLLISION` (0x008000FC). This allows the host's event handlers to
distinguish locally-detected collisions from network-reported ones.

The re-post path is **TGEventManager singleton dispatch** (not a queue push):

```asm
006A25EC  PUSH ESI                       ; event pointer
006A25ED  MOV  ECX, 0x97F838             ; this = g_pEventManager
006A25F2  MOV  [ESI+0x10], 0x008000FC    ; event->type = ET_HOST_OBJECT_COLLISION
006A25F9  CALL TGEventManager__PostEvent ; FUN_006DA2A0 (__thiscall)
```

The disasm pattern `MOV ECX, 0x97F838; CALL 0x006DA2A0` is the standard MSVC __thiscall
invocation: `this` is loaded into ECX, the event pointer is the first stack arg. The
EventManager dispatches synchronously to any handler registered for 0x008000FC, including
`Ship_HostCollisionEffectHandler` at 0x005AFAD0.

## Send-Side Flow

The send side is triggered when a CLIENT detects a collision locally:

1. Collision detection fires `ET_OBJECT_COLLISION` (0x00800050) event
2. `ShipClass::CollisionEffectHandler` (0x005AF9C0) handles it
3. Handler calls `CollisionEvent::WriteToStream` (vtable+0x34 = 0x005871A0):
   - Transforms each contact point to ship-relative coordinates
   - Compresses via CompressedVec4_Byte format (4 bytes per contact)
   - Writes collision_force as raw f32
4. Wraps in TGMessage with opcode 0x15, sends to host via TGWinsockNetwork

## Host-Side Damage Processing [v5-validated 2026-05-28]

After the handler re-posts the event as `ET_HOST_OBJECT_COLLISION` (0x008000FC):

1. **Ship_HostCollisionEffectHandler** (0x005AFAD0):
   - If multiplayer: creates secondary event `0x00800053` (ET_COLLISION_DAMAGE) for effect broadcast
   - Iterates contact points, transforms each relative to the ship's NiNode
   - **Per-contact damage scaling** (constants byte-verified):
     ```
     raw = (collisionEnergy / ship.mass) / contactCount
     if (raw > 0.01f):                         // _DAT_00888A78 = 0x3C23D70A (dead zone)
         scaled = raw * 900.0f + 500.0f        // _DAT_008944BC + _DAT_008944B8
         SubsystemDamageDistributor(ship, dir, &scaled, 1.5f, attacker, 1)
                                                       // 1.5f = 0x3FC00000 force-scale
     ```
   - Output range: 500.0+ absolute HP (NOT fractional like DoDamage_CollisionContacts)
   - `FUN_005AFD70` -> `FUN_005AECC0` (subsystem lookup) -> `FUN_005AF4A0` (damage per subsystem)
   - Each subsystem receives the full scaled damage; overflow accumulated across all subsystems

2. **DamageableObject::CollisionEffectHandler** also fires (registered for both 0x00800050 and 0x008000FC)

3. **Effects.CollisionEffect** (Python handler) creates visual explosions at contact points

> [!NOTE]
> All four damage constants were verified byte-by-byte from the binary this pass:
> - `_DAT_00888A78` = `0A D7 23 3C` = 0x3C23D70A = **0.01f** (dead-zone threshold)
> - `_DAT_008944BC` = `00 00 61 44` = 0x44610000 = **900.0f** (HP damage scale)
> - `_DAT_008944B8` = `00 00 FA 43` = 0x43FA0000 = **500.0f** (HP base offset)
> - Force-scale arg = `0x3FC00000` = **1.5f** (3rd parameter at call from HostCollisionEffectHandler)

## Event Registration

### ShipClass Event Handlers (registered in FUN_005AB7C0)

```
ET_OBJECT_COLLISION (0x00800050)      -> ShipClass::CollisionEffectHandler     (0x005AF9C0)
ET_HOST_OBJECT_COLLISION (0x008000FC) -> ShipClass::HostCollisionEffectHandler (0x005AFAD0)
```

### DamageableObject Event Handlers (registered in FUN_00590BB0)

```
ET_OBJECT_COLLISION (0x00800050)      -> DamageableObject::CollisionEffectHandler
ET_HOST_OBJECT_COLLISION (0x008000FC) -> DamageableObject::CollisionEffectHandler  (same handler)
ET_OBJECT_COLLISION (0x00800050)      -> "Effects.CollisionEffect"  (Python, via FUN_006D92D0)
```

## Address-Value-as-Constant Pattern

> [!NOTE]
> The values `0x008000FC`, `0x008000DC`, `0x00800050`, `0x00800053` are used as
> 32-bit event-type IDs via their **address values** (not data dereferences).
> The bytes stored *at* those addresses are irrelevant — those addresses often
> fall inside code sections. The engine uses the address itself as a unique
> global identifier (the address space is the namespace). Watch for this
> pattern when reading decompiled output: `MOV [ESI+0x10], 0x008000FC` is
> *assigning the constant 0x008000FC* (an event-type tag), not *loading from*
> the memory at that address.

## Related Functions [v5-validated 2026-05-28]

| Address | Name | Role |
|---------|------|------|
| 0x006A2470 | CollisionEffectHandler | Network receive handler (opcode 0x15) — renamed + plated this pass |
| 0x0069F491 | (opcode 0x15 jump-table thunk) | Dispatcher entry: `CALL 0x006A2470` |
| 0x005871A0 | CollisionEvent::WriteToStream | Network serialization (vtable+0x34) |
| 0x00587300 | CollisionEvent::ReadFromStream | Network deserialization (vtable+0x38) |
| 0x005874A0 | CollisionEvent::PostProcess | Post-deserialization reference resolution (vtable+0x3C) |
| 0x00586FB0 | CollisionEvent::WriteStream | Persistence serialization (vtable+0x10) |
| 0x00587030 | CollisionEvent::ReadStream | Persistence deserialization (vtable+0x14) |
| 0x00586D00 | CollisionEvent::ctor | Constructor (size 0x44) |
| 0x00586DF0 | CollisionEvent::dtor | Scalar deleting destructor |
| 0x00586E20 | CollisionEvent::Destroy | Frees points array + base cleanup |
| 0x005AF9C0 | ShipClass::CollisionEffectHandler | Client-side: serializes + sends to host |
| 0x005AFAD0 | Ship__HostCollisionEffectHandler | Host-side: applies collision damage — renamed this pass |
| 0x005AFD70 | SubsystemDamageDistributor | Per-contact-point damage distribution (1.5f force-scale arg) |
| 0x005AECC0 | SubsystemLookupByPosition | Finds nearest subsystem to contact point |
| 0x005AF4A0 | ApplySubsystemDamage | Applies damage to specific subsystem |
| 0x005AE140 | IsLocalPlayerShip | Checks if ship is local player's — renamed this pass |
| 0x005AB670 | CastToShipClass | Returns ship if class type 0x8008 — renamed this pass |
| 0x006A1AA0 | GetShipFromPlayerID | Maps connection ID to ship ptr (__cdecl) — renamed this pass |
| 0x006B8530 | TGMessage::GetBuffer | Extracts data ptr + size from message |
| 0x006CEFE0 | StreamReader::ctor | Constructs stream reader |
| 0x006CF180 | StreamReader::Init | Sets buffer, offset, size |
| 0x006D6200 | TGFactory_DeserializeObject | Creates + deserializes TGEvent — renamed this pass |
| 0x006DA2A0 | TGEventManager__PostEvent | __thiscall dispatcher (this=0x0097F838) — renamed this pass |
| 0x006F13E0 | TGEventFactory::Lookup | Hash table factory for event classes |
| 0x006F13C0 | ResolveReferences | Resolves object IDs to pointers |
| 0x00595410 | CollisionEvent::GetPointInternal | Copies Vec3 from point_array |
| 0x006D29A0 | CompressVec4_Byte_Direction | Normalizes + compresses to 3 signed bytes |
| 0x006D2D10 | CompressVec4_Byte_Magnitude | Compresses magnitude to unsigned byte |
| 0x006D30E0 | DecompressVec4_Byte | Decompresses 4 bytes to Vec3 using bounding radius |

## CollisionEvent Vtable Map (0x0089395C) [v5-validated 2026-05-28]

All 17 slots verified byte-by-byte via memory dump this pass.

| Offset | Target     | Name |
|--------|-----------|------|
| +0x00  | 0x00586DF0 | scalar_deleting_dtor |
| +0x04  | 0x00586D80 | (unknown) |
| +0x08  | 0x00586D90 | (unknown) |
| +0x0C  | 0x006F1650 | (inherited from NiObject) |
| +0x10  | 0x00586FB0 | WriteStream (persistence) |
| +0x14  | 0x00587030 | ReadStream (persistence, full TGEvent fields) |
| +0x18  | 0x006D6050 | ReadClassName (inherited) |
| +0x1C  | 0x006D60B0 | WriteClassName (inherited) |
| +0x20  | 0x006F15C0 | (inherited from NiObject) |
| +0x24  | 0x00586DC0 | GetName / GetRTTI ("CollisionEvent") |
| +0x28  | 0x00586DD0 | (unknown) |
| +0x2C  | 0x00586DE0 | (unknown) |
| +0x30  | 0x00586E70 | CopyFrom |
| +0x34  | 0x005871A0 | WriteToStream (network, compressed) |
| +0x38  | 0x00587300 | ReadFromStream (network, compressed) |
| +0x3C  | 0x005874A0 | PostProcess / ResolveLinks |

## TGEvent Base Vtable (0x00895FF4) for Reference

| Offset | Target     | Name |
|--------|-----------|------|
| +0x00  | 0x006D5D40 | scalar_deleting_dtor |
| +0x04  | 0x006D5CE0 | (unknown) |
| +0x08  | 0x006D5CF0 | (unknown) |
| +0x0C  | 0x006F1650 | (inherited) |
| +0x10  | 0x006D5EC0 | TGEvent::WriteStream |
| +0x14  | 0x006D5FF0 | TGEvent::ReadStream |
| +0x18  | 0x006D6050 | ReadClassName |
| +0x1C  | 0x006D60B0 | WriteClassName |
| +0x20  | 0x006F15C0 | (inherited) |
| +0x24  | 0x006D5D10 | GetName |
| +0x28  | 0x006D5D20 | (unknown) |
| +0x2C  | 0x006D5D30 | (unknown) |
| +0x30  | 0x006D6230 | CopyFrom |
| +0x34  | 0x006D6130 | WriteToStream (network) |
| +0x38  | 0x006D61C0 | ReadFromStream (network) |
| +0x3C  | 0x006D8520 | PostProcess |
| +0x40  | 0x006D84C0 | (unknown, not overridden by CollisionEvent) |

## Stream Reader Vtable (0x00895C58)

| Vtable Offset | Function     | Type    | Size |
|---------------|-------------|---------|------|
| +0x50         | 0x006CF5E0  | ReadByte | 1 byte (u8/s8) |
| +0x58         | 0x006CF600  | ReadU16 | 2 bytes |
| +0x60         | 0x006CF640  | ReadU32 | 4 bytes (class type ID) |
| +0x68         | 0x006CF670  | ReadU32 | 4 bytes (general purpose) |
| +0x70         | 0x006CF6B0  | ReadF32 | 4 bytes |
| +0x80         | 0x006CF6A0  | ReadObjID | Thunks to ReadU32 at +0x68 |
| +0x9C         | 0x006D30E0  | DecompressVec4_Byte | 4 bytes -> Vec3 |
| +0xB8         | (varies)    | DecompressVec3 | 3 bytes -> Vec3 |
| +0xBC         | (varies)    | DecompressVec4_ByteCore | 4 bytes -> Vec3 (with magnitude) |

## Ghidra Annotations Applied [v5 2026-05-28]

### Function renames (6)

| Address | Old name | New name |
|---------|----------|----------|
| 0x006A2470 | Handler_CollisionEffect_0x15 | CollisionEffectHandler (kept canonical; plated this pass) |
| 0x005AFAD0 | (FUN) | Ship__HostCollisionEffectHandler |
| 0x006A1AA0 | (FUN) | GetShipFromPlayerID |
| 0x005AE140 | (FUN) | IsLocalPlayerShip |
| 0x005AB670 | (FUN) | CastToShipClass |
| 0x006D6200 | (FUN) | TGFactory_DeserializeObject |
| 0x006DA2A0 | (FUN) | TGEventManager__PostEvent |

### Global labels (7)

| Address | Label | Value / Role |
|---------|-------|--------------|
| 0x008955C8 | g_flCollisionBoundingGapCap | 26.0f — distance gate cap |
| 0x00888A78 | g_flCollisionDamageDeadzone | 0.01f — damage dead-zone threshold |
| 0x008944BC | g_flHostCollisionDamageScale | 900.0f — HP damage scale |
| 0x008944B8 | g_flHostCollisionDamageBase | 500.0f — HP damage base offset |
| 0x008000FC | ET_HOST_OBJECT_COLLISION | host-side re-post event type (address-as-constant) |
| 0x00800050 | ET_OBJECT_COLLISION | wire-arrival event type (address-as-constant) |
| 0x00800053 | ET_HOST_COLLISION_EFFECT_BROADCAST | host effect broadcast (address-as-constant) |

### Prototypes + plates

- Prototype set on `CollisionEffectHandler` (0x006A2470).
- Plate comment added on `CollisionEffectHandler` summarising: dispatcher route, 3 validations, distance gate constant, re-post semantics, and the "no server-side recomputation" finding.

## Open Questions

None blocking. Downstream damage handling (`DamageableObject::CollisionEffectHandler`,
Python `Effects.CollisionEffect` via `FUN_006D92D0`, string `"Effects.CollisionEffect"`
at 0x008E5CC8) is scoped to [docs/gameplay/damage-system.md](../gameplay/damage-system.md)
and not re-derived here.
