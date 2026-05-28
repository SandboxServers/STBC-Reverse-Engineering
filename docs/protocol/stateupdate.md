> [docs](../README.md) / [protocol](README.md) / stateupdate.md

---
title: StateUpdate (Opcode 0x1C — Per-Tick Object State Replication)
type: reference
audience: re-engineer
validated: 2026-05-28
methodology: FUNCTION_DOC_WORKFLOW_V5
binary:
  name: STBC.exe
  size: 6394712
  base: 0x00400000
status: partial
companions:
  - docs/protocol/wire-format-spec.md
  - docs/protocol/transport-layer.md
  - docs/protocol/stream-primitives.md
  - docs/protocol/game-opcodes.md
  - docs/protocol/stateupdate-subsystem-wire-format.md
  - docs/protocol/per-ship-subsystem-wire-format.md
  - docs/protocol/subsystem-integrity-hash.md
  - docs/engine/tg-hierarchy-vtables.md
  - docs/engine/decompiled-functions.md
  - docs/protocol/v5-validation-status.md
supersedes:
  - (prior 2026-02 drafts)
evidence:
  - claim: "Opcode 0x1C dispatcher entry: MpgameHandleStateUpdate at 0x0069FF50 is jump-table slot 28 of the MultiplayerGame dispatcher (MpgameHandleMessage at 0x0069F2A0, jump table at 0x0069F534). Body: opens a TGBufferStream over the message payload, reads opcode + 4-byte object_id, looks up the object via FUN_0059FC60(0, object_id), and dispatches to the object's vtable[+0x124] (Ship slot 73)."
    address: 0x0069ff50
    function: MpgameHandleStateUpdate
    completeness: 42.1
    confidence: high
    note: "155-byte body. Renamed + plated this pass. Score gated by undefined struct accesses on the object-lookup chain (TGObject hash table)."
  - claim: "Ship serializer Ship__WriteStateUpdate at 0x005B17F0 is Ship vtable slot 72 (offset +0x120 in the Ship vtable at 0x00894340). It is the per-tick per-peer encoder that emits the 9-byte fixed prefix (opcode + obj_id + gameTime) followed by a dirty_flags byte and the per-flag wire payloads. 2,472-byte body (~348 decompiled lines)."
    address: 0x005b17f0
    function: Ship__WriteStateUpdate
    completeness: 0.0
    confidence: high
    note: "Renamed + typed + plated + 56 inline annotations this pass. effective_score remains 0.0 because the body has extensive undefined-struct accesses (per-peer tracker context, ship+0x88 / +0x90 / +0x9C state cache, animation tracker at iVar3+0x2C..+0x54) that the decompiler can't resolve without deeper class typing. The plate + inline comments capture the wire format and the round-robin algorithm at a depth sufficient for clean-room implementation."
  - claim: "Ship receiver Ship__ReadStateUpdate at 0x005B21C0 is Ship vtable slot 73 (offset +0x124). Called by MpgameHandleStateUpdate (0x0069FF50). Decodes each flag in the same order the sender emits and updates TWO state buffers: the ship kinematic cache at ship+0x88 (pos) / ship+0x90 (orientation accumulator) / ship+0x9C (velocity hint), and the animation tracker at iVar3+0x2C..+0x54 (interpolation state). 1,539-byte body."
    address: 0x005b21c0
    function: Ship__ReadStateUpdate
    completeness: 5.8
    confidence: high
    note: "Renamed + typed + plated + 26 inline annotations this pass."
  - claim: "Dirty flags are emitted/read in a fixed sequence that is NOT numeric order. The order is 0x01 (POS) -> 0x02 (DELTA) -> 0x04 (FWD) -> 0x08 (UP) -> 0x10 (SPEED) -> 0x40 (CLOAK) -> 0x20 (SUBSYSTEMS) -> 0x80 (WEAPONS). Note that 0x40 (CLOAK) comes BEFORE 0x20 (SUBSYSTEMS) on the wire; the bit-value order would put 0x20 first. Order verified by reading sender emit sequence at Ship__WriteStateUpdate body and receiver decode sequence at Ship__ReadStateUpdate body."
    address: 0x005b17f0
    function: Ship__WriteStateUpdate
    completeness: 0.0
    confidence: high
    note: "Wire-bit order is a load-bearing invariant; receivers that decode 0x20 before 0x40 will desynchronize on cloak-state transitions."
  - claim: "Flag 0x01 wire format is `[bit:has_subsystem_hash] [if bit set: ushort:hash]` UNCONDITIONALLY. The sender at Ship__WriteStateUpdate emits the bit=1 path only when `bIsSinglePlayer` is true (loaded from `!DAT_0097FA8A` at disasm site 0x005B1C76 where BL is reloaded from `[ESP+0x23]`). In multiplayer the sender emits bit=0 and no hash bytes. The receiver always reads the bit; if set it reads the 2 hash bytes; only in MP does it then compare-and-kick. The `AND is_multiplayer` part is a validation-gate property, not a wire-format property."
    address: 0x005b1c76
    function: Ship__WriteStateUpdate
    completeness: 0.0
    confidence: high
    note: "Resolves the pre-v5 wire-format-vs-validation conflation. Anti-cheat hash is dead code in stock MP gameplay - see subsystem-integrity-hash.md."
  - claim: "Subsystem WriteState formats (vtable+0x70) are three distinct implementations: Format 1 Base ShipSubsystem at 0x0056D320 (writes a condition byte + recurses children); Format 2 PoweredSubsystem at 0x00562960 (Format 1 + a bit-gated powerPct byte); Format 3 PowerSubsystem at 0x005644B0 (Format 1 + two battery-percentage bytes). Format 3 ALWAYS writes both battery bytes regardless of isOwnShip; Format 2 omits the powerPct byte when isOwnShip == 1."
    address: 0x005644b0
    function: PowerSubsystem__WriteState
    completeness: n/a (created)
    confidence: high
    note: "PowerSubsystem__WriteState at 0x005644B0 was an undefined function in Ghidra before this pass - the doc's address was correct but the function entry did not exist. Created via mcp__ghidra__create_function this validation. Body confirmed: base + (mainBatteryPower / FUN_005634C0() * 255.0) byte + (backupBatteryPower / FUN_005634D0() * 255.0) byte."
  - claim: "Round-robin subsystem budget = 10 bytes per tick on flag 0x20. The serializer carries a persistent per-object cursor at iVar7+0x30 (linked-list pointer) and iVar7+0x34 (start_index byte). On entry it writes the start_index, then loops emitting subsystem WriteState payloads until `streamPos - budgetStart >= 10` or the cursor wraps back to the initial value (full cycle). Disassembly site at 0x005B1EC0: `CMP EAX, 0xA`."
    address: 0x005b1ec0
    function: Ship__WriteStateUpdate
    completeness: 0.0
    confidence: high
  - claim: "Round-robin weapon budget = 6 bytes per tick on flag 0x80. Weapon path iterates the SAME ship+0x284 linked list as the subsystem path, filtered by `vtable[+8](0x801C)` (IsWeaponType). Only nodes returning a match emit a 2-byte (index + health) tuple. Disassembly site at 0x005B1F66: `CMP EAX, 0x6`. The 0x801C constant is the runtime type ID for the weapon-base class hierarchy."
    address: 0x005b1f66
    function: Ship__WriteStateUpdate
    completeness: 0.0
    confidence: high
    note: "Resolves pre-v5 'weapon linked list at ship+0x284' wording. The list is the subsystem list; weapons are a filtered view via the IsWeaponType vtable lookup."
  - claim: "Flags 0x20 (SUB) and 0x80 (WPN) are mutually exclusive in MP per the player-count gate at FUN_006A2650. The sender first decides isMultiplayer (DAT_0097FA8A) and friendlyFire (DAT_0097FAA2); if MP+FF, it then checks (host ? playerCount > 1 : playerCount > 2) - if true, subsystems are skipped. The combination produces 0x20-only on S->C and 0x80-only on C->S in the stock topology. Cross-source: stock-dedi packet traces show 10,459 C->S packets carrying 0x80 / 0 with 0x20, 19,997 S->C packets carrying 0x20 / 0 with 0x80 (100% disjoint)."
    address: 0x006a2650
    function: (subsystem-vs-weapon dispatch gate)
    completeness: high
    confidence: high
    note: "Resolves the pre-v5 'CLIENT-side DAT_0097fa8a differs' speculation. No client/host IsMultiplayer mismatch is required; the player-count gate accounts for the trace ratios naturally."
  - claim: "Speed encoding (flag 0x10): `||vel||` from FUN_005A05A0 (Ship::GetVelocity) computed as sqrt of sum-of-squares; sign-flipped to negative when FUN_005AC4F0 (Ship::IsReversing) returns nonzero (returns 1 when `vel . fwd < 0`); then CF16-encoded to 2 wire bytes. Cloak state (flag 0x40) is a single bit read from `ship[+0x2DC]+0x9C` (the cloak device subsystem status byte)."
    address: 0x005a05a0
    function: Ship::GetVelocity
    completeness: high
    confidence: high
  - claim: "Force-update timing: per-field timestamps stored at trackerObj+0x04..+0x2E (one per dirty flag). A field is force-sent when `DAT_00888860 < (gameTime - lastSentTime)`. The master timestamp at trackerObj+0x04 is updated only when ALL dirty fields are simultaneously emitted."
    address: 0x00888860
    function: (global threshold)
    completeness: low
    confidence: low
    note: "The threshold value itself remains uncited in this pass. Likely ~1.0 seconds. ~934 xrefs project-wide complicate single-source-of-truth pinning. Carried as OQ5."
  - claim: "Per-peer tracker context (pTrackerCtx in plate comment) holds the round-robin cursor at +0x30, the start_index at +0x34, and an inferred per-weapon delta-dedup hash table at +0x40 (entry stride 0xC bytes). Tracker is identified by a pair of fields at +0x08 and +0x0C used as match keys; layout suggests TargetPeerContext."
    address: null
    function: Ship__WriteStateUpdate
    completeness: 0.0
    confidence: low
    note: "Layout fields confirmed by sender's persistent reads/writes; the semantic role (peer vs target peer vs animation tracker) remains OQ2. Per-weapon hash table at +0x40 is OQ3."
---

# State Update (Opcode 0x1C) - The Big One

The highest-volume game message - ~30,000 packets per stock multiplayer session, sent at
roughly 10 Hz per replicated ship. Uses dirty-flags to send only fields that changed since
the last update, plus round-robin chunking for the variable-length subsystem/weapon
payloads.

> [!NOTE]
> This doc is `status: partial`. **Zero material wire-format corrections** in this pass - all
> 8 dirty bits, the round-robin subsystem/weapon algorithm, and the 3 subsystem WriteState
> formats are v5-validated against the current Ghidra import (2026-05-28). The dispatcher
> `MpgameHandleStateUpdate` at 0x0069FF50 (opcode 0x1C entry), the serializer
> `Ship__WriteStateUpdate` at 0x005B17F0 (Ship vtable slot 72, 2,472-byte encoder), and the
> receiver `Ship__ReadStateUpdate` at 0x005B21C0 (Ship vtable slot 73) were all
> v5-documented in Ghidra during this validation. `PowerSubsystem__WriteState` at 0x005644B0
> (Format 3) was newly created in Ghidra (function entry was missing; address was correct).
> Five clarifications applied: wire-format-vs-validation-gate distinction for Flag 0x01
> hash; mutual-exclusion explanation for Flags 0x20/0x80 (player-count gate, no
> IsMultiplayer mismatch); weapon path shares subsystem linked list; PowerSubsystem
> WriteState anchor. See [docs/guides/v5-evidence-header.md](../guides/v5-evidence-header.md)
> for the standard.

## Dispatcher and Function Map

**Dispatcher entry**: `MpgameHandleStateUpdate` at **0x0069FF50** (155-byte body) - jump-table
slot 28 of `MpgameHandleMessage` (0x0069F2A0). Opens a TGBufferStream over the message
payload, reads opcode + 4-byte object_id, resolves the object via `FUN_0059FC60(0, object_id)`,
and dispatches to the object's `vtable[+0x124]` (Ship vtable slot 73 = receiver).
[v5-validated 2026-05-28]

**Serializer**: `Ship__WriteStateUpdate` at **0x005B17F0** - Ship vtable slot 72 (offset
`+0x120` in the Ship vtable at 0x00894340). Per-tick per-peer encoder, called from the
TGNetwork tick loop (caller is vtable-dispatched; see OQ1). 2,472-byte body, ~348
decompiled lines.
[v5-validated 2026-05-28]

**Receiver**: `Ship__ReadStateUpdate` at **0x005B21C0** - Ship vtable slot 73 (offset
`+0x124`). Decodes each flag in the same order the sender emits; updates the ship kinematic
state at `ship+0x88` / `+0x90` / `+0x9C` AND the animation tracker at
`iVar3+0x2C..+0x54`. 1,539-byte body.
[v5-validated 2026-05-28]

## Wire Format

The 9-byte fixed prefix followed by a dirty-flags byte and variable per-flag payloads:

| Offset | Size | Type | Field | Description |
|--------|------|------|-------|-------------|
| 0 | 1 | u8 | opcode | 0x1C [v5-validated 2026-05-28] |
| 1 | 4 | i32 | object_id | Network object ID (looked up via FUN_0059FC60) [v5-validated 2026-05-28] |
| 5 | 4 | f32 | game_time | Current game clock timestamp (sender's gameTime) [v5-validated 2026-05-28] |
| 9 | 1 | u8 | dirty_flags | Bitmask of which payload sections follow [v5-validated 2026-05-28] |
| 10+ | var | data | per-flag payloads | Emitted in fixed order (see Dirty Flags) |

The prefix is written by `swig_WriteChar` / `swig_WriteInt` / `swig_WriteFloat` calls in
the sender; read by `swig_ReadChar` / `swig_ReadInt` / `swig_ReadFloat` in the receiver.
Both sender and receiver use the TGBufferStream class from foundation #2
[stream-primitives.md](stream-primitives.md).

## Dirty Flags Byte

Emit / decode order is **NOT numeric order** - cloak (0x40) comes before subsystems (0x20):

```
Bit 0 (0x01): POSITION_ABSOLUTE   - Full position + optional subsystem hash
Bit 1 (0x02): POSITION_DELTA      - Compressed position delta (CompressedVec4)
Bit 2 (0x04): ORIENTATION_FWD     - Forward vector (CompressedVec3)
Bit 3 (0x08): ORIENTATION_UP      - Up vector (CompressedVec3)
Bit 4 (0x10): SPEED               - Current speed (CompressedFloat16)
Bit 6 (0x40): CLOAK_STATE         - Cloak active bit  <-- emitted BEFORE 0x20
Bit 5 (0x20): SUBSYSTEM_STATES    - Subsystem health round-robin
Bit 7 (0x80): WEAPON_STATES       - Weapon health round-robin (uses ship+0x284 too)
```

A receiver that decodes flags in numeric order will desynchronize on the cloak transition -
the cloak bit gets consumed as if it were the start_index byte for subsystems.

## Flag 0x01 - Absolute Position

```
+0      4     f32      pos_x              World position X
+4      4     f32      pos_y              World position Y
+8      4     f32      pos_z              World position Z
+12     bit   bool     has_subsystem_hash
[if has_subsystem_hash:]
  +0    2     u16      subsystem_hash     XOR-folded 32-bit hash
[else:]
  (nothing additional)
```

The wire format is `[3 floats][1 bit][optional 2 hash bytes]` **unconditionally**. The
sender emits the bit=1 path only when `bIsSinglePlayer == true` (BL reloaded from
`[ESP+0x23]` at disasm site `0x005B1C76`, where the slot holds `!DAT_0097FA8A`). In
multiplayer the sender emits bit=0 and writes no hash bytes; in single-player it emits
bit=1 followed by the 2 hash bytes.

The receiver **always** reads the bit and (if set) the 2 hash bytes. Only when
`DAT_0097FA8A != 0` (multiplayer) does it then compute the local hash via
`ComputeSubsystemHash(this+0x27C)` at `0x005B5EB0` and XOR-fold-compare with the received
hash. On mismatch it posts `ET_BOOT_PLAYER` (0x008000F6) which kicks the player.
[v5-validated 2026-05-28]

In stock MP gameplay the sender always emits bit=0, so this anti-cheat path is dead code.
See [subsystem-integrity-hash.md](subsystem-integrity-hash.md) for the canonical
dead-in-MP analysis.

**Reset semantics**: when the absolute position is sent (flag 0x01 set), the sender
clears the delta-compression reference point:

- `saved_pos = current_pos`
- `delta_dir_bytes = 0,0,0`
- `delta_magnitude = 0`

## Flag 0x02 - Position Delta (Compressed)

```
+0      5     cv4      position_delta     CompressedVector4(dx, dy, dz, param4=1)
                                          dx = current_x - saved_x
                                          dy = current_y - saved_y
                                          dz = current_z - saved_z
                                          uint16 magnitude (last component)
```

Written via `WriteCompressedVector4` at `0x006D2F10`. Sent only when the delta direction
bytes have changed from cached values OR the periodic force-update timer
(`DAT_00888860`) fires.

## Flag 0x04 - Forward Orientation

```
+0      3     cv3      forward_vector     CompressedVector3 (3 signed bytes / 127.0)
```

Written via `WriteCompressedVector3` at `0x006D2AD0`. Forward vector sourced from
`ship->vtable[0xAC](&output)` = `GetForwardVector`.
[v5-validated 2026-05-28]

## Flag 0x08 - Up Orientation

```
+0      3     cv3      up_vector          CompressedVector3 (3 signed bytes / 127.0)
```

Same writer (`0x006D2AD0`). Up vector sourced from `ship->vtable[0xB0](&output)` =
`GetUpVector`.
[v5-validated 2026-05-28]

## Flag 0x10 - Speed

```
+0      2     u16      speed_compressed   CompressedFloat16
```

```c
float* vel = FUN_005A05A0(ship);              // Ship::GetVelocity
float speed = sqrt(vel[0]*vel[0]
                 + vel[1]*vel[1]
                 + vel[2]*vel[2]);
if (FUN_005AC4F0(ship)) speed = -speed;       // IsReversing: returns 1 when vel . fwd < 0
encode_CF16(speed);                            // CF16 encoder at 0x006D3A90
```

The reversing-sign flip is what makes a speed-byte direction-aware on the wire even though
the vector magnitude is unsigned.
[v5-validated 2026-05-28]

## Flag 0x40 - Cloak State

```
+0      bit   bool     cloak_active       0 = decloaked, 1 = cloaked
```

Single bit via `WriteBit` / `ReadBit`. Read from `ship[+0x2DC]+0x9C` (the cloak device
subsystem's status byte). Only sent when the value differs from the sender's cached state.
[v5-validated 2026-05-28]

## Flag 0x20 - Subsystem States (Round-Robin)

S->C only in stock MP (see "Flag 0x20 vs 0x80" below). Subsystems are serialized
round-robin from the ship's top-level subsystem linked list at `ship+0x284`. Each tick
sends a chunk starting where the previous tick left off.

```
+0      1     u8       start_index         Position in subsystem list where this batch begins
+1      var   data     subsystem_data      Per-subsystem WriteState payloads (variable length)
```

No payload-count field is on the wire; the receiver reads subsystem payloads until the
stream is exhausted (`streamPos >= dataLength`).

### Subsystem list ordering

There is no fixed index table. The `start_index` is a position in the ship's serialization
linked list at `ship+0x284`, whose contents and order are determined by the hardpoint
script's `LoadPropertySet()` call order. Only **top-level system containers** remain in the
list after `Ship_LinkAllSubsystemsToParents` (`FUN_005B3E20`) removes children. Individual
weapons (phaser banks, torpedo tubes) and engines are serialized **recursively** within
their parent's WriteState.

### Per-subsystem WriteState formats (vtable+0x70)

Each subsystem writes variable-length data via `vtable+0x70` (WriteState). Three
implementations exist:

**Format 1: Base ShipSubsystem (`0x0056D320`)** - Hull, ShieldGenerator, individual
children:

```
[condition: u8]           // (int)(currentCondition / GetMaxCondition() * 255.0)
                          //   this+0x30 / property+0x20 * 255.0; 0xFF=full, 0x00=destroyed
[child_0 WriteState]      // Recursive: each child writes its own block
[child_1 WriteState]
...
```
[v5-validated 2026-05-28]

**Format 2: PoweredSubsystem (`0x00562960`)** - Sensors, Engines, Weapons, Cloak, Repair,
Tractors:

```
[base WriteState]                 // Format 1 (condition byte + recursive children)
if (isOwnShip == 0):              // Remote ship - include power data
    [hasData: bit=1]              // WriteBit(1)
    [powerPctWanted: u8]          // (int)(powerPercentageWanted * 100.0); this+0x90, 0-100
else:                             // Own ship - owner has local state
    [hasData: bit=0]              // WriteBit(0)
```
[v5-validated 2026-05-28]

**Format 3: PowerSubsystem (`0x005644B0`)** - Reactor / Warp Core only:

```
[base WriteState]                 // Format 1 (condition byte + recursive children)
[mainBatteryPct: u8]              // (int)(mainBatteryPower / mainBatteryLimit * 255.0)
                                  //   this+0xAC / FUN_005634C0() return; 0xFF=full
[backupBatteryPct: u8]            // (int)(backupBatteryPower / backupBatteryLimit * 255.0)
                                  //   this+0xB4 / FUN_005634D0() return; 0xFF=full
```

PowerSubsystem ALWAYS writes both battery bytes regardless of `isOwnShip`. The function at
0x005644B0 was an undefined entry in the Ghidra import before this validation pass; the
doc's address was already correct - it was just not recognized as a function. Created and
decompiled this pass. `FUN_005634C0` and `FUN_005634D0` return `property+0x48` and
`property+0x4C` (the per-ship reactor capacity limits).
[v5-validated 2026-05-28]

### Round-robin algorithm

From `Ship__WriteStateUpdate` (`0x005B17F0`), the per-object tracker fields at `iVar7+0x30`
(cursor) and `iVar7+0x34` (start index) persist across ticks. The byte budget is enforced
at disasm site `0x005B1EC0`: `CMP EAX, 0xA` (10-byte budget including the start_index
byte itself).

```
if cursor == NULL:
    cursor = ship->subsystemListHead   // ship+0x284
    index = 0
initialCursor = cursor
WriteByte(stream, index)               // startIndex

while (streamPos - budgetStart) < 10:  // 10-byte budget including startIndex
    subsystem = cursor->data
    cursor = cursor->next
    subsystem->WriteState(stream, isOwnShip)
    index++
    if cursor == NULL:                 // End of list: wrap
        cursor = ship->subsystemListHead
        index = 0
    if cursor == initialCursor: break  // Full cycle complete
```

### Receiver (Flag 0x20 in `Ship__ReadStateUpdate`)

```
startIndex = ReadByte(stream)
node = ship->subsystemListHead
for i in range(startIndex): node = node->next      // Skip to start position
while streamPos < dataLength:
    subsystem = node->data
    node = node->next
    subsystem->ReadState(stream, timestamp)        // vtable+0x74 (inverse of WriteState)
    if node == NULL: node = ship->subsystemListHead  // Wrap
```

For detailed subsystem type tables, linked list structure, and the Sovereign-class layout
example, see [stateupdate-subsystem-wire-format.md](stateupdate-subsystem-wire-format.md).

## Flag 0x80 - Weapon States (Round-Robin)

C->S only in stock MP. Iterates **the same `ship+0x284` linked list** as flag 0x20, filtered
by `vtable[+8](0x801C)` (IsWeaponType) - only weapon-type nodes are emitted on send /
applied on receive.

```
[repeated while (streamPos - budgetStart) < 6:]
  weapon = list_node->data
  if weapon->vtable[+8](0x801C):  // IsWeaponType
    +0    1     u8       weapon_index
    +1    1     u8       weapon_health_byte   ftol(health * SCALE_FACTOR)
[end repeat]
```

Each weapon entry is `[index:u8][health:u8]` = 2 bytes. Budget = 6 bytes per update
(disasm site `0x005B1F66`: `CMP EAX, 0x6`). `SCALE_FACTOR` is `g_flWeaponHealthScale` at
`0x008944C4`.

The pre-v5 wording "weapon linked list at ship+0x284" was technically correct on the
address but misleading on the structure - it is the **same** linked list as the subsystem
path, with the weapon-type filter applied at iteration time. There is not a separate weapon
list.
[v5-validated 2026-05-28]

## Flag 0x20 vs 0x80 - Direction-Based Split

**Packet trace evidence from stock dedicated server** (verified against 30,000+ packets):

| Direction | Flag Used | Flag Never Used | Packet Count |
|-----------|-----------|-----------------|--------------|
| **C->S** | 0x80 (WPN) always | 0x20 (SUB) never | 10,459 [cross-source-2026-02-22 trace] |
| **S->C** | 0x20 (SUB) always | 0x80 (WPN) never | 19,997 [cross-source-2026-02-22 trace] |

Client sends **weapon status** (0x80) to server. Server sends **subsystem health** (0x20)
to client. These flags are **mutually exclusive by direction** in multiplayer.

**Top C->S flag combinations**: 0x9E (DELTA+FWD+UP+SPD+WPN), 0x96, 0x92, 0x9D, 0x8E

**Top S->C flag combinations**: 0x20 (SUB only), 0x3E (DELTA+FWD+UP+SPD+SUB), 0x36, 0x3D,
0x32

### Why the disjoint usage

The mutual exclusion is a natural consequence of the **friendly-fire + player-count gate**
at `FUN_006A2650`. The sender chooses 0x20 vs 0x80 based on:

```c
bIsSinglePlayer = (DAT_0097FA8A == 0);

if (bIsSinglePlayer) {
    flags |= 0x80;               // SP: always emit weapons
    goto write_packet;
}
// MP path:
if (DAT_0097FAA2 != 0) {         // friendly fire enabled?
    if (DAT_0097FA88 == 0) {     // is host?
        if (playerCount > 1) goto skip_subsystems;   // host with >= 2 players
    } else {                     // is client
        if (playerCount > 2) goto skip_subsystems;   // client with >= 3 players
    }
}
flags |= 0x20;                   // MP default: include subsystems
goto write_packet;
skip_subsystems:
flags |= 0x80;                   // MP fallback: emit weapons instead
```

In stock topology, host has `DAT_0097FA88 == 0` and at least 1 other player, so
`playerCount > 1` is true - the host falls through to `skip_subsystems` only when friendly
fire is off, otherwise it sends 0x20. Clients have `DAT_0097FA88 == 1` and the
`playerCount > 2` gate flips them to 0x80 once a third player is in the game (or any time
they're the only joined client and friendly-fire forces the gate one way).

The traces (10,459 / 19,997 - 100% disjoint) confirm this is a stable steady-state
partition once the session reaches its player count, not a transient artifact.

The pre-v5 doc speculated that "the CLIENT-side value of `DAT_0097FA8A` differs from the
HOST-side value during serialization". That speculation is **dropped** - both endpoints
have `DAT_0097FA8A = 1` during stock MP; the gate explains the trace naturally without
needing endpoint-specific IsMultiplayer inconsistency.

## Receiver Side (Ship__ReadStateUpdate at 0x005B21C0) - Deserialization

The receiver mirrors the serializer's emit order:

```
1. ReadByte -> opcode (0x1C)
2. ReadInt32 -> object_id
3. ReadFloat -> game_time
4. ReadByte -> dirty_flags

if (flags & 0x01): // absolute position
    pos_x = ReadFloat, pos_y = ReadFloat, pos_z = ReadFloat
    has_hash = ReadBit
    if (has_hash):
        received_hash = ReadShort
        if (DAT_0097FA8A != 0):                                 // MP-only validation
            computed_hash = ComputeSubsystemHash(this+0x27C)    // 0x005B5EB0
            if (XOR-fold(received) != XOR-fold(computed)):
                POST ET_BOOT_PLAYER (0x008000F6)                // kicks the player

if (flags & 0x02): // position delta
    ReadCompressedVector4(stream, &dx, &dy, &dz, param4=1)
    new_pos = saved_pos + delta

if (flags & 0x04): // forward orientation
    ReadCompressedVector3(stream, &fwd_x, &fwd_y, &fwd_z)
    apply to scene node

if (flags & 0x08): // up orientation
    ReadCompressedVector3(stream, &up_x, &up_y, &up_z)
    apply to scene node

if (flags & 0x10): // speed
    raw = ReadShort
    speed = DecompressFloat16(raw)                              // 0x006D3B30
    apply to physics

if (flags & 0x40): // cloak state                               // emitted BEFORE 0x20
    cloak = ReadBit
    if cloak: FUN_0055F360(cloak_device)                        // activate
    else:     FUN_0055F380(cloak_device)                        // deactivate

if (flags & 0x20): // subsystem states
    start_idx = ReadByte
    iterate subsystem linked list from start_idx
    while streamPos < total_length:
        subsystem->vtable[+0x74](stream, gameTime)              // ReadState

if (flags & 0x80): // weapon states
    while streamPos < total_length:
        weapon_idx = ReadByte
        health_byte = ReadByte
        navigate to weapon at weapon_idx in linked list
        if weapon->vtable[+8](0x801C):                          // IsWeaponType
            health = health_byte * SCALE_FACTOR (0x008944C4)
            weapon->vtable[+0x84](health, gameTime)
```

The receiver updates **two** state buffers, not one: the ship kinematic cache at
`ship+0x88` (pos), `ship+0x90` (orientation accumulator), `ship+0x9C` (velocity hint), and
the animation tracker at `iVar3+0x2C..+0x54`. The animation tracker pointer at `iVar3` is
obtained via `FUN_005A1720` -> `FUN_0047DE50(type=9)` and holds interpolation state; the
exact semantics of the type-9 node are OQ4.

## Authority and Direction

S->C carries subsystem-health (0x20) updates; C->S carries weapon-state (0x80) updates.
The relay-audit cross-source trace
[`[cross-source-2026-02-24 trace]`] recorded **23,994 C->S** StateUpdate packets and
**45,355 S->C** in a 21-minute Cady / XFS01 session. The S->C count exceeds C->S because
the host serves StateUpdates for **all** replicated ships (including AI and other clients)
to each client - i.e., the host RELAYS state for other clients AND generates its own
ship's S->C stream. The client only sends its own ship.

## Force-Update Timing

The serializer tracks timestamps per-field at `trackerObj+0x04` through `trackerObj+0x2E`.
A field is force-sent if:

```c
DAT_00888860 < (gameTime - lastSentTime)  // global threshold (value pending - OQ5)
```

When ALL dirty fields are sent simultaneously, the master timestamp at `trackerObj+0x04`
is updated.

The exact value of `DAT_00888860` is not pinned this pass (~934 xrefs project-wide
complicate single-source-of-truth pinning). Likely ~1.0 seconds.

## Ghidra Functions Documented in This Validation

| Address | Symbol | Vtable Slot | Body Size | v5 Score |
|---------|--------|-------------|-----------|----------|
| 0x0069FF50 | `MpgameHandleStateUpdate` | (dispatcher slot 28 of 0x0069F2A0) | 155 bytes | 42.1 |
| 0x005B17F0 | `Ship__WriteStateUpdate` | Ship vtable slot 72 (+0x120) | 2,472 bytes | 0.0 |
| 0x005B21C0 | `Ship__ReadStateUpdate` | Ship vtable slot 73 (+0x124) | 1,539 bytes | 5.8 |
| 0x005644B0 | `PowerSubsystem__WriteState` | (Format 3) | (newly created) | n/a |

Total annotation applied this session: 4 renames + 4 plate comments + 82 inline comments
+ 56 + 26 + 5 variable renames. Two globals labeled: `g_flWeaponHealthScale` at
0x008944C4; `ET_BOOT_PLAYER` constant 0x008000F6.

The low effective scores on the sender (0.0) and receiver (5.8) reflect the decompiler's
inability to resolve the per-peer tracker context and per-ship state buffer struct types;
the plate + inline comments capture the wire-format and algorithm semantics required for
clean-room reimplementation.

## Open Questions

These remain at `confidence: low` until resolved (see also frontmatter `evidence` rows):

1. **OQ1 - Ship__WriteStateUpdate caller location.** No direct CALL with FUN_005B17F0
   found (vtable-dispatched at slot 72). Likely the TGNetwork tick loop iterating peers.
   Worth tracking but not blocking for the doc.
2. **OQ2 - pTrackerCtx precise semantic identity.** Has +0x08 (hash key) and +0x0C
   (matching ID). Layout suggests TargetPeerContext. Class typing deferred.
3. **OQ3 - Per-weapon delta-dedup hash table at tracker+0x40.** Entry stride 0xC bytes.
   Layout TBD.
4. **OQ4 - Animation tracker pointer at iVar3.** Obtained via FUN_005A1720 ->
   FUN_0047DE50(type=9). Receiver writes interpolation state at +0x2C..+0x54. Type 9 is
   likely NIAnimationNode or similar.
5. **OQ5 - DAT_00888860 force-resend threshold value.** ~934 xrefs project-wide.
   Likely ~1.0 seconds. Worth pinning.

## Cross-Links

- [stream-primitives.md](stream-primitives.md) - CV3 / CV4 / CF16 wire formats and
  TGBufferStream layout
- [transport-layer.md](transport-layer.md) - TGMessage envelope (type 0x32) that carries
  the 0x1C payload
- [game-opcodes.md](game-opcodes.md) - opcode 0x1C row in the dispatcher jump table
- [wire-format-spec.md](wire-format-spec.md) - protocol hub / index
- [stateupdate-subsystem-wire-format.md](stateupdate-subsystem-wire-format.md) - per-ship
  subsystem catalog + linked list mechanics
- [per-ship-subsystem-wire-format.md](per-ship-subsystem-wire-format.md) - 16 stock-ship
  subsystem layouts
- [subsystem-integrity-hash.md](subsystem-integrity-hash.md) - canonical analysis of the
  anti-cheat hash and its dead-in-MP status
- [docs/engine/tg-hierarchy-vtables.md](../engine/tg-hierarchy-vtables.md) - Ship vtable
  slot 72 / 73 anchors
- [docs/engine/decompiled-functions.md](../engine/decompiled-functions.md) - dispatcher and
  network function anchors
- [v5-validation-status.md](v5-validation-status.md) - validation tracker (this doc is
  protocol-family mid #8)
