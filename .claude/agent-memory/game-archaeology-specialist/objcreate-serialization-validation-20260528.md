---
name: objcreate-serialization-validation-20260528
description: Protocol doc #10 validation. Two MATERIAL wire-format corrections (velocity is CV4 7-byte direction+magnitude not 4-byte speed + 3-byte padding; slot-array base is +0x74 not +0x84). Slot 0x118/0x11C split clarified (species+Python vs body+subsystems).
metadata:
  type: project
---

# objcreate-serialization.md Validation — 2026-05-28

Heaviest pre-existing protocol doc (~80 load-bearing claims) but most of the
weight is the species map (which is in Python scripts) and the trace
examples (which are illustrative, not load-bearing). Two MATERIAL
corrections to the wire format + one structural correction to the slot
layout.

## Material Corrections

### C1. Velocity wire format is CV4 (3 dir bytes + 4 magnitude float), NOT "speed f32 + 3 padding bytes"

The doc shows:
```
37  4 f32   speed       Speed magnitude (usually 0.0 at spawn)
41  3 u8[3] padding     Always 0x00 0x00 0x00
```

Binary reality (FUN_005A2060 = ShipReadStreamBody, at 0x005A2060):
```c
(**(code **)(*param_2 + 0x94))(auStack_340, auStack_33c, auStack_338, 0);
// vtable[+0x94] = CompressedVector4_ReadVirtual (0x006D2FD0)
// with param_5 = 0:
//   vtable[+0x50] ReadChar  x 3   (3 direction bytes)
//   vtable[+0x70] ReadFloat x 1   (magnitude float)
//   vtable[+0xB0]            (rebuild xyz vector from compressed dir + mag)
```

So bytes 37..43 are:
- **off 37-39:  3 bytes compressed direction (signed normalized dir)**
- **off 40-43:  4 bytes magnitude float**

(NOT "off 37-40: f32 speed + off 41-43: 3 padding". The doc has the
field WIDTHS right (4 + 3 = 7) but the SEMANTICS and ORDER wrong.)

The "always 0x00 0x00 0x00" observation at offset 41-43 is consistent with
typical zero-velocity spawns (direction byte 0 = -0.0 means a normalized
direction of (0,0,0) effectively — combined with 0.0 magnitude = no
velocity). The byte order matches because: ships spawn at rest, so all
7 velocity bytes are 0x00.

### C2. MultiplayerGame.playerSlots base is +0x74, NOT +0x84

The doc says "MultiplayerGame+0x84 contains a 16-entry array with stride 0x18".

Binary reality (MultiplayerGame_Ctor at 0x0069E590):
```c
FUN_00859d64(param_1 + 0x1d, 0x18, 0x10, FUN_006a7720, FUN_006a7760);
// param_1 + 0x1d (dword indexed) = byte offset +0x74
// element size 0x18, capacity 0x10
```

So the table is:
- **base @ MultiplayerGame+0x74**
- 16 slots × 24 bytes each
- slot N starts at +0x74 + N*0x18

The "MultiplayerGame+0x84" the doc cites is offset **+0x10 within each
PlayerSlot** (the game-state pointer field). For slot 0, that's:
`+0x74 + 0*0x18 + 0x10 = +0x84`. The doc IS reading the same table, just
naming the base from the GAME-STATE FIELD inside slot 0 rather than the
slot-array base.

Relay loop in MpgameHandleObjCreate confirms structure:
```c
piVar9 = (int *)((int)this + 0x7c);  // = playerSlots[0] + 0x08
do {
    if ((char)piVar9[-1] != '\0') {  // playerSlots[N] + 0x04 = inUse byte
        if (*piVar9 == *(int *)(pMsg->pPad04 + 8)) {  // playerSlots[N] + 0x08 = peer ID
            ...
```

PlayerSlot layout (24 bytes):
- +0x00 (?)
- +0x04 inUse byte
- +0x08 peer/network ID (used in relay)
- +0x0C (?)
- +0x10 game-state pointer (= MultiplayerGame+0x84 for slot 0)
- +0x14 (?)

Use base **+0x74** in the spec; cross-link to struct-skeletons-20260528.

### C3. vtable[+0x118] does NOT read the wire body; vtable[+0x11C] does

The doc's pipeline diagram says:

```
obj->vtable[0x118](stream) → ReadStream
    ├─ FUN_005a2030: ReadByte → ship+0xEC (species)
    ├─ Python: SpeciesToShip.InitObject(ship, species)
    └─ Continue reading: position, orientation, velocity, name, set, subsystems
obj->vtable[0x11C](stream) → PostLoad
```

Binary reality — Ship vtable at 0x00894340:
- vtable[+0x118] = 0x005B0E80 (ShipDeserializeStream_Slot118)
  - Reads ONLY the 1-byte species (FUN_005A2030)
  - Calls Python SpeciesToShip.InitObject (loads NIF + creates subsystems)
  - Calls stream->vtable[+0xD8] (bit-alignment finalize)
  - **Returns. Does NOT read position/quat/velocity/names.**

- vtable[+0x11C] = 0x005B0DC0 (ShipPostDeserializeFixup_Slot11C)
  - Calls FUN_005A2060 (ShipReadStreamBody) which reads:
    - 3 floats position (vtable[+0x70] x 3)
    - 4 floats quaternion (vtable[+0x70] x 4) → matrix via FUN_008162B0
    - CV4 velocity (vtable[+0x94] = 7 bytes)
    - u8 + bytes player_name
    - u8 + bytes set_name (looked up in DAT_0097E9C8 binary-searched registry)
  - Walks ship+0x284 linked list → calls each subsystem's vtable[+0x6c]
  - Calls stream->vtable[+0xD8] (finalize)

So the doc's labels "ReadStream" / "PostLoad" are MISLEADING. The proper
labels are:
- vtable[+0x118] = "ReadSpeciesAndPythonInit"
- vtable[+0x11C] = "ReadBodyAndFixup" (this is where 95% of the wire
                   bytes are consumed)

This is structurally important for OpenBC implementers: the species byte
MUST be processed (with full Python ship setup) BEFORE the body data
arrives, because the body data needs the ship's subsystem chain to exist
(populated by the Python SetupProperties call) to deserialize subsystem
state. So the two-pass scheme is FORCED by data-dependency, not a Ghidra
ordering accident.

## Refinements (not corrections)

### R1. Factory class IDs are correct but documentation needs to note 0x8002 = category tag

The doc says: "factory_class_id is looked up in the TG object factory
(DAT_0099a67c) to instantiate the correct C++ class".

Actually:
- DAT_0099A67C = global object hash table (used for object_id lookup)
- DAT_0099A578 = factory registry vtable (4-slot small object: hash fn, match fn, ?)
- DAT_0099A584 = factory bucket array

FUN_006F13E0 (TGFactoryCreate) walks the factory registry using class_id
as the key. FUN_00430730 (ObjectLookupByID) walks the OBJECT HASH TABLE
(DAT_0099A67C) using object_id as the key. The doc conflates the two.

Also: the duplicate check via FUN_00430730(0, object_id) is NOT a pure
"is this ID used?" check — it's gated by class category 0x8002 (game
object). Lookups for non-game-object IDs return NULL (which the caller
treats as "OK to create"). This is fine in practice because all
ObjCreate'd objects are game objects, but the doc's "if an object with
that ID already exists, deserialization aborts" implies a simple
hash-existence check.

### R2. Orientation IS stored as a quaternion (4 floats), per the open question

The doc's open question:
> Whether orientation is stored as quaternion (4 floats) or Euler angles
> (3 floats) — quaternion is more likely given 4 consecutive floats after
> position

Definitively CONFIRMED quaternion (w, x, y, z) via:
- FUN_00816390 (sender): full matrix → quaternion (classic Shoemake
  algorithm with SQRT + sign-handling)
- FUN_008162B0 (receiver): quaternion → 3x3 matrix expansion

Wire offsets: 21-37 = 16 bytes = 4 floats. Confirmed.

### R3. The "3 padding bytes" open question

Resolved per C1 above: those 3 bytes are the CV4 direction component of
velocity, not padding. The 4-byte preceding "speed" is the CV4 magnitude.
Order on wire: 3 dir bytes FIRST, then 4 magnitude bytes.

So the doc's offsets need to flip:
```
37-39  3 bytes  CV4 direction (compressed normalized velocity dir)
40-43  4 bytes  f32 magnitude (velocity speed in u/s)
```

## Confirmed Claims

- **Handler FUN_0069F620**: confirmed (already validated as #9). Now
  renamed `MpgameHandleObjCreate`.
- **FUN_005A1F50** (now `HandleObjCreateDeserialize`): wraps SWIG
  TGBufferStream, reads u32 class_id + u32 obj_id, runs duplicate
  pre-check, factory-creates via FUN_006F13E0 (now `TGFactoryCreate`),
  invokes vtable[+0x118]+[+0x11C].
- **Factory class IDs 0x8008 / 0x8009**: confirmed in trace examples;
  Ghidra anchors are inside FUN_006F13E0's bucket chain.
- **Species byte at ship+0xEC**: confirmed via FUN_005A2030 (ShipReadSpecies):
  `*(int *)(param_1 + 0xec) = (int)cVar1`.
- **Python SpeciesToShip.InitObject pipeline**: confirmed via decompile
  of FUN_005B0E80 → string ref `s_Multiplayer_SpeciesToShip_008e61ec`
  + `s_InitObject_008e5620`. The pipeline (SetupModel → Hardpoints →
  SetupProperties → UpdateNodeOnly) confirmed by reading the actual
  Python script in `reference/scripts/Multiplayer/SpeciesToShip.py`.
- **Set name binary-search registry**: confirmed at DAT_0097E9C8 / size
  DAT_0097E9CC. FUN_005A2060 does sorted binary search over the registry.
- **SpeciesToShip 1..45**: confirmed exact match against the Python
  script. Doc table is byte-correct.
- **SpeciesToTorp 1..15**: confirmed.
- **SpeciesToSystem 1..9**: confirmed (9 entries = MULTI1..7 + ALBIREA
  + POSEIDON; doc accurately lists all 9; MAX_SYSTEMS = 10).
- **Sender's vtable[+0x10C]**: confirmed (FUN_005A1CF0). The doc says
  "vtable[0x10C] WriteStream" — accurate.
- **Network controller attach (NiAlloc(0x58) + FUN_0047dab0(ship,
  "Network") + vtable[+0x134])**: confirmed at end of MpgameHandleObjCreate.
- **Non-team objects (opcode 0x02) do NOT get a Network controller**:
  confirmed by the `if (bWithTeam == '\0') return;` branches in
  MpgameHandleObjCreate.
- **Torpedo (class_id 0x8009) skips the Network controller**: confirmed
  via `if (iVar8 == 0x8009) { ExceptionList = local_c; return; }`.
- **Active-slot swap pattern**: confirmed (DAT_0097FA84 / DAT_0097FA8C
  / DAT_0095B07D fence).

## Trace examples re-decoded

Trace 1 (Akira, position 88, -66, -73):
```
03  - opcode 0x03 (ObjCreateTeam)
00  - owner_slot = 0 (host)
02  - team_id = 2
[stream begins]
08 80 00 00         - class_id = 0x00008008 (Ship)
FF FF FF 3F         - obj_id = 0x3FFFFFFF (player 0 base)
[vtable+0x118 reads species byte:]
01                  - species = 1 (Akira)
[Python InitObject runs - loads NIF, creates subsystems]
[vtable+0x11C reads body:]
00 00 B0 42         - position_x = 88.0
00 00 84 C2         - position_y = -66.0
00 00 92 C2         - position_z = -73.0
[next 16 bytes = quaternion w, x, y, z]
[next 7 bytes = CV4 velocity: 3 dir + 4 magnitude = 00 00 00 00 00 00 00]
...etc
```

This matches the doc's interpretation of offsets 0-40 but corrects
41-43 (NOT padding, but velocity direction bytes — happens to be
0x00 0x00 0x00 because spawn velocity = 0).

## v5 Annotations Applied

In Ghidra (program: STBC.exe):

| Old Name | New Name | Address | Status |
|----------|----------|---------|--------|
| FUN_005a1f50 | HandleObjCreateDeserialize | 0x005A1F50 | renamed + prototype + plate |
| FUN_005a2030 | ShipReadSpecies | 0x005A2030 | renamed |
| FUN_005a2060 | ShipReadStreamBody | 0x005A2060 | renamed + plate |
| FUN_005a1cf0 | ShipSerializeForObjCreate_Slot10C | 0x005A1CF0 | renamed |
| FUN_005a1d80 | ShipWriteHeader_Slot110 | 0x005A1D80 | renamed |
| FUN_005a1dc0 | ShipWriteStreamBody | 0x005A1DC0 | renamed |
| FUN_005b0d80 | ShipSerializeStream_Slot114 | 0x005B0D80 | created + renamed |
| FUN_005b0dc0 | ShipPostDeserializeFixup_Slot11C | 0x005B0DC0 | created + renamed |
| FUN_005b0e80 | ShipDeserializeStream_Slot118 | 0x005B0E80 | renamed + plate |
| FUN_006f13e0 | TGFactoryCreate | 0x006F13E0 | renamed + prototype |
| FUN_00430730 | ObjectLookupByID | 0x00430730 | renamed + prototype |

HandleObjCreateDeserialize effective_score 32.6 / max 92.5. The cap is
the 3 unrenamed DAT_ globals (factory globals shared across many
handlers; out of scope for THIS doc). Plate substantially documents the
function.

## Open Questions (Genuine, Post-Validation)

- **Sender side of velocity write**: the sender code FUN_005A1DC0
  passes (vx, vy, vz, 0) to vtable[+0x90] WriteCV4. The "0" 5th byte
  param triggers the COMPRESS path (3 bytes + magnitude float). But
  the sender's velocity getter (FUN_005A05A0) returns the actual velocity
  vector — how does CV4 then split direction vs magnitude? Answer:
  vtable[+0xA0] (called inside CV4_WriteVirtual when param_5=0) is
  the compression helper — splits unit-vector direction from magnitude.
  Needs follow-up if precise wire bytes for non-zero velocity are
  needed for trace replay.

- **Subsystem state wire format per ship type**: deferred to
  per-ship-subsystem-wire-format.md validation. The chain at
  ship+0x284 is iterated and per-subsystem vtable[+0x6c] is called,
  but the actual format per CT_ type isn't anchored here.

- **Set/system registry contents**: DAT_0097E9C8 holds a sorted array
  of Set/System objects, binary-searched by name on receive. The
  registration site is unanchored — likely registered during
  Mission.LoadScript() Python sequence.

- **MultiplayerGame.playerSlots field +0x14 (relay context)**: the
  relay loop pre-walks slots via piVar9, but the meaning of +0x14
  isn't explored. Probably "current send sequence counter for this peer".

## Cross-Anchor Validation

- **object-replication.md (mid #9)**: this doc IS the detail
  expansion of mid #9. Consistent — both agree on FUN_005A1F50 as
  receiver dispatch, vtable[+0x10C] as sender, vtable[+0x118]+[+0x11C]
  as receiver pair (with C3 above clarifying the split).
- **stream-primitives.md (foundation #2)**: SWIG TGBufferStream layout
  used inside FUN_005A1F50 — consistent. Read sites match Foundation #2's
  vtable map: ReadChar @ +0x50, ReadFloat @ +0x70, ReadShort @ +0x58,
  ReadInt @ +0x78, ReadCV4 @ +0x94.
- **game-opcodes.md (mid #4)**: opcodes 0x02/0x03 row matches. Handler
  FUN_0069F620 confirmed.
- **struct-skeletons-20260528 (memory)**: MultiplayerGame.playerSlots
  @ +0x74 — MATCHES our finding (the doc's +0x84 is the +0x10 field
  within slot 0).

## Patterns / Lessons

- **Two-pass deserialize forced by data dependency**: vtable[+0x118]
  MUST run before vtable[+0x11C] because the body data references
  subsystems that don't exist until Python's SetupProperties runs.
  This is an interesting design pattern worth documenting for OpenBC.
  Similar patterns may exist in other ObjCreate-class objects (which
  type would need an analogous two-pass scheme).

- **CV4 vs "f32 + 3 padding"**: wire formats that look like simple
  primitives can hide compressed-vector encoding. The 3+4 byte layout
  of velocity is the same TOTAL SIZE as the doc claimed (4+3) but the
  ORDER matters for trace decoding. Stock dedi traces SHOWED zero bytes
  for the spawn case, masking the order.

- **Doc's "MultiplayerGame+0x84" is anchored at a FIELD inside slot 0**,
  not the slot array base. Reading the constructor (MultiplayerGame_Ctor
  at 0x0069E590) is the canonical way to verify these claims —
  it directly tells us the size, stride, and capacity via
  `FUN_00859d64(this+0x1d, 0x18, 0x10, ...)`. Use ctors as authority
  for struct layout.

- **Decompiler FPU register tracking is brittle**: FUN_005A1DC0 (write
  body) decompiles MESS because Ghidra confuses uVar2 vs uVar5 across
  FPU and integer registers. The READ side (FUN_005A2060) decompiles
  CLEANLY (separate floats live in stack slots), so use the RECEIVE side
  to anchor wire format whenever the SEND side is FPU-tangled.

- **Python script + binary cross-anchor**: the species map IS the source
  of truth (Python script). The binary's role is only to READ a byte
  and invoke `SpeciesToShip.InitObject(ship, species)`. So strictly
  speaking, the species enum table is `[cross-source]` not
  binary-anchored. But the byte-position in the wire IS binary-anchored
  (FUN_005A2030 / FUN_005B0E80).

## Status

`partial` — doc body has 3 material corrections (velocity wire format,
slot-array offset, vtable[+0x118]/[+0x11C] split labelling) and 3
refinements. Trace examples should be re-decoded post-correction. After
applying corrections, doc would be `verified` — the foundation claims
(handler, factory, dispatch chain, species map) are rock-solid.
