> [docs](../README.md) / [protocol](README.md) / game-opcodes.md

---
title: Game Opcodes (MultiplayerGame Jump Table)
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
  - docs/protocol/stateupdate.md
  - docs/protocol/object-replication.md
  - docs/protocol/pythonevent-wire-format.md
  - docs/protocol/collision-effect-protocol.md
  - docs/protocol/set-phaser-level-protocol.md
  - docs/protocol/delete-player-ui-wire-format.md
  - docs/protocol/objnotfound-requestobj-enterset-wire-format.md
  - docs/protocol/cf16-explosion-encoding.md
  - docs/engine/decompiled-functions.md
  - docs/protocol/v5-validation-status.md
supersedes:
  - (prior pre-v5 game-opcodes.md)
evidence:
  - claim: "MultiplayerGame ReceiveMessageHandler at 0x0069F2A0 dispatches opcodes 0x02-0x2A via 41-entry jump table at 0x0069F534 (opcode minus 2 indexes the table; entries are 4-byte thunk addresses)"
    address: 0x0069f2a0
    function: MpgameHandleMessage
    completeness: 69.84
    confidence: high
    note: "Jump-table decoded byte-by-byte this pass; 41 entries x 4 bytes = 164 bytes. All 16 distinct thunk addresses spot-checked."
  - claim: "Opcode 0x02 (ObjCreate) thunk at 0x0069F31E calls FUN_0069F620(stream, 0); opcode 0x03 (ObjCreateTeam) thunk at 0x0069F334 calls FUN_0069F620(stream, 1). Same handler, second arg distinguishes team vs non-team object."
    address: 0x0069f620
    function: FUN_0069f620
    completeness: high
    confidence: high
  - claim: "Opcodes 0x04 and 0x05 are DEAD — jump-table entries 2 and 3 both point to default cleanup at 0x0069F525. No case bodies for 0x04/0x05 exist in MpgameHandleMessage."
    address: 0x0069f525
    function: MpgameHandleMessage
    completeness: 69.84
    confidence: high
    note: "Negative claim — confirmed by reading the jump-table bytes and the dispatcher body. Boot/kick lives at the transport layer via TGBootPlayerMessage."
  - claim: "Opcodes 0x06 (PythonEvent) and 0x0D (PythonEvent2) share thunk address 0x0069F3F1, both routing to FUN_0069F880. Handler instantiates TGEvent via FUN_006D6200, resolves refs via FUN_006F13C0, zeroes the preserve field at puVar2[9], and posts via FUN_006DA300."
    address: 0x0069f880
    function: FUN_0069f880
    completeness: high
    confidence: high
  - claim: "Generic event-forward thunks at jump-table slots for opcodes 0x07-0x0C, 0x0E-0x12, 0x1B all call FUN_0069FDA0(stream, event_id_constant). The event_id_constant is PUSHed inline at each thunk."
    address: 0x0069fda0
    function: FUN_0069fda0
    completeness: high
    confidence: high
  - claim: "FUN_0069FDA0 override semantics: line `if (param_2 != 0) puVar7[4] = param_2;` — when the dispatcher PUSHes a non-zero constant it OVERRIDES the wire's event-code field; when PUSH = 0 the wire's value is kept verbatim."
    address: 0x0069fda0
    function: FUN_0069fda0
    completeness: high
    confidence: high
    note: "Load-bearing for OpenBC relay implementations. Distinguishes opcodes 0x07/0x08/0x09/0x0A/0x0B/0x0E/0x0F/0x10/0x1B (override) from 0x0C/0x11/0x12 (keep wire value)."
  - claim: "Opcode 0x13 (HostMsg) thunk at 0x0069F2F6 routes to HostMsgHandler at 0x006A01B0. Used for self-destruct and other host-authority actions."
    address: 0x006a01b0
    function: HostMsgHandler
    completeness: high
    confidence: high
  - claim: "Opcode 0x14 (DestroyObject) handler FUN_006A01E0 wire format `[u8 opcode][i32v object_id]`; branches on owner pointer (puVar3[8]) — NULL = cleanup + destroy, non-NULL = owner->vtable[0x5C](object_id)."
    address: 0x006a01e0
    function: FUN_006A01E0
    completeness: high
    confidence: high
    note: "Decompile shows OpenBuffer(buf+1, len-1) then ReadIntVirtual() for the object id; owner field at +0x20."
  - claim: "Opcode 0x15 (CollisionEffect) handler CollisionEffectHandler at 0x006A2470 re-posts the event with type code 0x008000FC (ET_HOST_OBJECT_COLLISION), distinct from the wire's 0x00800050 (ET_OBJECT_COLLISION). Distance gate reads _DAT_008955C8."
    address: 0x006a2470
    function: CollisionEffectHandler
    completeness: high
    confidence: high
    note: "Re-post anchored at `piVar9[4] = (int)&DAT_008000fc;` near end of handler body."
  - claim: "Opcode 0x16 jump-table entry routes to default cleanup 0x0069F525; opcode is handled by the MultiplayerWindow dispatcher FUN_00504C10 (not MultiplayerGame). Receiver-side handler FUN_00504C70."
    address: 0x0069f525
    function: MpgameHandleMessage
    completeness: 69.84
    confidence: high
    note: "Verified by jump-table read; companion-dispatcher binding documented in wire-format-spec.md."
  - claim: "Opcode 0x17 (DeletePlayerUI) handler FUN_006A1360 walks the TGEvent factory chain and calls FUN_006D62B0(this) where this = MultiplayerGame*. Removes a player's UI elements (scoreboard row)."
    address: 0x006a1360
    function: FUN_006A1360
    completeness: high
    confidence: high
  - claim: "Opcode 0x19 (TorpedoFire) handler FUN_0069F930; opcode 0x1A (BeamFire) handler FUN_0069FBB0. Both subsystem fire paths re-instantiate the projectile / beam locally on the receive side after reading from the stream."
    address: 0x0069f930
    function: FUN_0069F930
    completeness: high
    confidence: high
  - claim: "Opcode 0x1C (StateUpdate) handler FUN_0069FF50 exists at 84 bytes (entry 0x0069FF50 to 0x0069FFEB). Body is a small wrapper that delegates into the StateUpdate machinery — full per-flag wire formats live in stateupdate.md."
    address: 0x0069ff50
    function: FUN_0069ff50
    completeness: high
    confidence: high
    note: "This opcode row was previously missing from CLAUDE.md's game opcode table; campaign-close batch will append it."
  - claim: "Opcode 0x1D/0x1E/0x1F (object recovery triad) handlers at FUN_006A0490 / FUN_006A02A0 / FUN_006A05E0. Wire formats and round-trip semantics deferred to objnotfound-requestobj-enterset-wire-format.md."
    address: 0x006a0490
    function: FUN_006A0490
    completeness: high
    confidence: high
  - claim: "Opcode 0x29 (Explosion) handler FUN_006A0080 wire field order: ReadIntVirtual() (object_id), CompressedVector4_ReadVirtual(..., 1) (impact_pos), then ReadShort -> CompressedFloat16_Decode -> radius, then ReadShort -> CompressedFloat16_Decode -> damage. Constructor signature FUN_004BBDE0(&pos, radius, damage)."
    address: 0x006a0080
    function: FUN_006A0080
    completeness: high
    confidence: high
    note: "Receiver read order pairs with sender FUN_00595C60 writing radius (source+0x14) first, damage (source+0x1C) second. See cf16-explosion-encoding.md."
  - claim: "Opcode 0x2A (NewPlayerInGame) handler NewPlayerInGameHandler at 0x006A1E70. Triggers Python InitNetwork chain and replicates existing objects to the new player."
    address: 0x006a1e70
    function: NewPlayerInGameHandler
    completeness: high
    confidence: high
  - claim: "Opcodes 0x20-0x28 default-cleanup through MpgameHandleMessage because the NetFile dispatcher (FUN_006A3CD0) owns them. Per transport-layer.md correction C2 the NetFile opcode set is non-contiguous: 0x20, 0x21, 0x22, 0x23, 0x25, 0x27 (0x24, 0x26, 0x28 are unused)."
    address: 0x006a3cd0
    function: FUN_006A3CD0
    completeness: high
    confidence: high
    note: "Cross-anchored to transport-layer.md §6.3 (foundation #3) and to checksum-opcodes.md (pending v5 pass)."
---

# Game Opcodes (0x02-0x2A)

> [!NOTE]
> This doc is `status: partial`. All 41 jump-table entries at `0x0069F534` were verified byte-by-byte against the current Ghidra import on 2026-05-28; all handler addresses for active opcodes (0x02-0x2A minus dead 0x04/0x05 and routing-only 0x16) were spot-checked. Cross-anchored to the engine-family dispatcher-recovery work (MpgameHandleMessage at `0x0069F2A0`). One column-header clarification landed: the previous "Recv Event Code" was ambiguous because it conflated the **dispatcher PUSH override** with the **wire-payload event code** — renamed below and a footer paragraph distinguishes the four flavours of event code that exist along this path. Per-opcode wire formats are cross-linked to their leaf docs. Session-frequency counts are tagged `[cross-source]` because they come from packet-trace analysis, not Ghidra. See [docs/guides/v5-evidence-header.md](../guides/v5-evidence-header.md) for the evidence standard.
>
> Open documentation debt: opcode 0x18 (DeletePlayerAnim) has a handler address but no BC-side wire-format leaf doc; OpenBC has the clean-room spec — see `../OpenBC/docs/wire-formats/delete-player-anim-wire-format.md`.

## Dispatch architecture

[v5-validated 2026-05-28] Game opcodes 0x02-0x2A are dispatched by the MultiplayerGame ReceiveMessageHandler at `0x0069F2A0` (Ghidra name: `MpgameHandleMessage`). The first payload byte is the opcode, which indexes a **41-entry jump table at `0x0069F534`** (opcode minus 2). Each table entry is a 4-byte thunk address; multiple opcodes can share a thunk when they invoke the same handler with the same arguments.

**NOTE**: Opcodes 0x00 and 0x01 are NOT in this jump table. They are handled by the MultiplayerWindow dispatcher (`FUN_00504C10`) which processes them on the client side. Opcode 0x16 is also routed through MultiplayerWindow even though it appears at the jump-table position (the table slot points at the default cleanup).

**NOTE**: Opcodes 0x07-0x0F are EVENT FORWARD messages (weapon state changes, cloak, warp), NOT Python messages or combat actions. The actual combat opcodes are 0x19 (TorpedoFire) and 0x1A (BeamFire). Python messages use opcode 0x06/0x0D.

## 0x00 - Settings (Server -> Client, MultiplayerWindow dispatcher)

**Sender**: `FUN_006a1b10` (ChecksumCompleteHandler)
**Client handler**: `FUN_00504d30`

Sent after all 5 checksum rounds pass (rounds 0-3 + 0xFF). Carries game settings and player slot assignment.

```
Offset  Size  Type     Field                    Notes
------  ----  ----     -----                    -----
0       1     u8       opcode = 0x00
1       4     f32      game_time                Current game clock (from DAT_009a09d0+0x90)
2       bit   bool     settings_byte1           DAT_008e5f59 (collision damage toggle)
3       bit   bool     settings_byte2           DAT_0097faa2 (friendly fire toggle)
4       1     u8       player_slot              Assigned player index (0-15)
5       2     u16      map_name_length
7       var   string   map_name                 Mission TGL file path
+0      bit   bool     checksum_result_flag     1 = checksums passed with corrections
[if flag == 1:]
+1      var   data     checksum_correction_data Written by FUN_006f3f30
```

**Stream write sequence** (from FUN_006a1b10):
```c
WriteByte(stream, 0x00);           // opcode
WriteFloat(stream, gameTime);      // from clock+0x90
WriteBit(stream, DAT_008e5f59);    // settings 1
WriteBit(stream, DAT_0097faa2);    // settings 2
WriteByte(stream, playerSlot);     // assigned slot
WriteShort(stream, mapNameLen);    // strlen of map name
WriteBytes(stream, mapName, len);  // map name string
WriteBit(stream, checksumFlag);    // did any checksums need correction?
if (checksumFlag) {
    FUN_006f3f30(checksumData, stream);  // correction data
}
```

See [wire-format-spec.md](wire-format-spec.md) for the bit-pack details and the wire-format-spec §Settings packet bit-pack detail subsection.

## 0x01 - Game Init Trigger (Server -> Client)

**Sender**: `FUN_006a1b10` (sent immediately after opcode 0x00)
**Client handler**: `FUN_00504f10`

```
Offset  Size  Type    Field
------  ----  ----    -----
0       1     u8      opcode = 0x01
```

Single byte, no additional payload. Triggers:
1. `AI.Setup.GameInit` Python call
2. Creates `Multiplayer.MultiplayerGame` Python object (with max 16 players)
3. Reads `g_iPlayerLimit` from `MissionMenusShared`
4. Shows "Connection Completed" UI

## Game Opcode Table (0x02-0x2A) [v5-validated 2026-05-28]

Reading order: opcode -> handler address (Ghidra symbol where available) -> jump-table thunk -> wire-format companion doc. Every row is anchored to the byte-by-byte jump-table decode in §6.4 of [v5-validation-status.md](v5-validation-status.md).

| Opcode | Name | Handler | Thunk | Type / Direction | Leaf doc |
|--------|------|---------|-------|------------------|----------|
| 0x02 | ObjCreate | `FUN_0069F620` (arg2=0) | `0x0069F31E` | Non-team object creation (S->C) | [object-replication.md](object-replication.md), [objcreate-serialization.md](objcreate-serialization.md) |
| 0x03 | ObjCreateTeam | `FUN_0069F620` (arg2=1) | `0x0069F334` | Ship creation with team (S->C) | [object-replication.md](object-replication.md), [objcreate-serialization.md](objcreate-serialization.md) |
| 0x04 | (dead) | DEFAULT | `0x0069F525` | Jump-table default; boot is at transport layer via TGBootPlayerMessage | — |
| 0x05 | (dead) | DEFAULT | `0x0069F525` | Jump-table default | — |
| 0x06 | PythonEvent | `FUN_0069F880` | `0x0069F3F1` | Primary event forwarding (~3432/session) [cross-source-2026-02-XX trace] | [pythonevent-wire-format.md](pythonevent-wire-format.md) |
| 0x07 | StartFiring | `FUN_0069FDA0` (PUSH 0x008000D7) | `0x0069F34A` | Weapon fire begin (2282/session) [cross-source-2026-02-XX trace] | [pythonevent-wire-format.md](pythonevent-wire-format.md), [tgobjptrevent-class.md](tgobjptrevent-class.md) |
| 0x08 | StopFiring | `FUN_0069FDA0` (PUSH 0x008000D9) | `0x0069F363` | Weapon fire end | [pythonevent-wire-format.md](pythonevent-wire-format.md) |
| 0x09 | StopFiringAtTarget | `FUN_0069FDA0` (PUSH 0x008000DB) | `0x0069F37C` | Stop firing at specific target | [pythonevent-wire-format.md](pythonevent-wire-format.md) |
| 0x0A | SubsysStatus | `FUN_0069FDA0` (PUSH 0x0080006C) | `0x0069F395` | Subsystem toggle (shields, etc.) | — |
| 0x0B | AddToRepairList | `FUN_0069FDA0` (PUSH 0x008000DF) | `0x0069F3AE` | Crew repair assignment | — |
| 0x0C | ClientEvent | `FUN_0069FDA0` (PUSH 0) | `0x0069F3C7` (shared) | Generic event forward; **wire event code kept** | — |
| 0x0D | PythonEvent2 | `FUN_0069F880` | `0x0069F3F1` (shared with 0x06) | Alternate Python event path | [pythonevent-wire-format.md](pythonevent-wire-format.md) |
| 0x0E | StartCloak | `FUN_0069FDA0` (PUSH 0x008000E3) | `0x0069F405` | Cloak engage | — |
| 0x0F | StopCloak | `FUN_0069FDA0` (PUSH 0x008000E5) | `0x0069F41E` | Cloak disengage | — |
| 0x10 | StartWarp | `FUN_0069FDA0` (PUSH 0x008000ED) | `0x0069F437` | Warp drive engage | — |
| 0x11 | RepairListPriority | `FUN_0069FDA0` (PUSH 0) | `0x0069F3C7` (shared) | Repair priority ordering; **wire event code kept** | — |
| 0x12 | SetPhaserLevel | `FUN_0069FDA0` (PUSH 0) | `0x0069F3C7` (shared) | Phaser power/intensity (33/session) [cross-source-2026-02-XX trace]; **wire event code kept** | [set-phaser-level-protocol.md](set-phaser-level-protocol.md) |
| 0x13 | HostMsg | `HostMsgHandler @ 0x006A01B0` | `0x0069F2F6` | Self-destruct request (client->host) | [../gameplay/self-destruct-pipeline.md](../gameplay/self-destruct-pipeline.md) |
| 0x14 | DestroyObject | `FUN_006A01E0` | `0x0069F47D` | Object destruction (rare in MP) | (see §0x14 below) |
| 0x15 | CollisionEffect | `CollisionEffectHandler @ 0x006A2470` | `0x0069F491` | Collision damage relay (84/session) [cross-source-2026-02-XX trace] | [collision-effect-protocol.md](collision-effect-protocol.md) |
| 0x16 | UICollisionSetting | `FUN_00504C70` (MultiplayerWindow) | `0x0069F525` (DEFAULT in MpgameHandleMessage) | Collision toggle | [wire-format-spec.md](wire-format-spec.md) |
| 0x17 | DeletePlayerUI | `FUN_006A1360` | `0x0069F4A5` | Remove player from scoreboard | [delete-player-ui-wire-format.md](delete-player-ui-wire-format.md) |
| 0x18 | DeletePlayerAnim | `FUN_006A1420` | `0x0069F4B9` | "Player joined/left" floating text (TGL lookup, crash risk) | (Open debt — see NOTE at top; mirror from [../../../OpenBC/docs/wire-formats/delete-player-anim-wire-format.md](../../../OpenBC/docs/wire-formats/delete-player-anim-wire-format.md)) |
| 0x19 | TorpedoFire | `FUN_0069F930` | `0x0069F4CD` | Torpedo launch (897/session) [cross-source-2026-02-XX trace] | (see §0x19 below) |
| 0x1A | BeamFire | `FUN_0069FBB0` | `0x0069F4E1` | Beam weapon hit | (see §0x1A below) |
| 0x1B | TorpedoTypeChange | `FUN_0069FDA0` (PUSH 0x008000FD) | `0x0069F450` | Torpedo type switch | — |
| 0x1C | StateUpdate | `FUN_0069FF50` | `0x0069F3DD` | Object state replication (8 dirty-flag formats) | [stateupdate.md](stateupdate.md) |
| 0x1D | ObjNotFound | `FUN_006A0490` | `0x0069F4F5` | Object lookup failure | [objnotfound-requestobj-enterset-wire-format.md](objnotfound-requestobj-enterset-wire-format.md) |
| 0x1E | RequestObj | `FUN_006A02A0` | `0x0069F51D` | Request object data | [objnotfound-requestobj-enterset-wire-format.md](objnotfound-requestobj-enterset-wire-format.md) |
| 0x1F | EnterSet | `FUN_006A05E0` | `0x0069F509` | Enter game set (scene change) | [objnotfound-requestobj-enterset-wire-format.md](objnotfound-requestobj-enterset-wire-format.md) |
| 0x20-0x28 | (NetFile) | DEFAULT (`0x0069F525`) | DEFAULT | Handled by NetFile dispatcher `FUN_006A3CD0`; non-contiguous (0x24/0x26/0x28 unused) | [checksum-opcodes.md](checksum-opcodes.md), [transport-layer.md](transport-layer.md) |
| 0x29 | Explosion | `FUN_006A0080` (Handler_Explosion_0x29) | `0x0069F469` | Explosion damage (S->C only) | [cf16-explosion-encoding.md](cf16-explosion-encoding.md) |
| 0x2A | NewPlayerInGame | `NewPlayerInGameHandler @ 0x006A1E70` | `0x0069F30A` | Player join handshake | [delete-player-ui-wire-format.md](delete-player-ui-wire-format.md) |

> Session-frequency counts annotated `[cross-source-2026-02-XX trace]` are derived from packet-trace analysis (primarily [../analysis/valentines-day-battle-analysis.md](../analysis/valentines-day-battle-analysis.md) and [../analysis/stock-trace-analysis.md](../analysis/stock-trace-analysis.md)). They are NOT directly observable in the binary; they are observational ground-truth pinned to a specific trace.

## What "event code" means along this path (post-receive)

The C1 clarification: the prior version of this doc had a single "Recv Event Code" column on the generic event-forward table that papered over four distinct flavours of event code that exist along the send -> wire -> dispatch -> receive path. They are:

| Flavour | Where it lives | Origin |
|---------|----------------|--------|
| **Sender path event code** | The local C++ event the sender posted to its own event manager before serialization | Producer code on the sending peer |
| **Wire event code** | A `u32` field inside the serialized TGEvent / TGObjPtrEvent / TGCharEvent payload | What gets written to the buffer and transmitted |
| **Dispatcher PUSH constant** | An immediate operand baked into each per-opcode jump-table thunk | Hard-coded at jump-table assembly time; passed as the second argument to `FUN_0069FDA0` |
| **Effective event code (post-receive)** | The value the receiver's event manager actually sees | `dispatcher PUSH if non-zero, else wire event code` (see `FUN_0069FDA0` line `if (param_2 != 0) puVar7[4] = param_2;`) |

The opcode table above lists the **dispatcher PUSH** value where it is non-zero (rows 0x07/0x08/0x09/0x0A/0x0B/0x0E/0x0F/0x10/0x1B), and tags rows 0x0C/0x11/0x12 with "wire event code kept" — because for those opcodes the dispatcher PUSHes 0 and the value seen by the receiver is whatever the sender serialized.

The sender/receiver event-code pairing that historically lived under this table (`D8->D7`, `DA->D9`, etc.) is the visible artifact of this asymmetry: the **sender path** uses one code locally, but the **dispatcher PUSH override** swaps it to a paired code on the receive side. The exception is opcode 0x12 (SetPhaserLevel) which uses the same code 0x008000E0 throughout because its dispatcher PUSH is 0.

**Implication for OpenBC**: a relay path that simply forwards opcode bytes byte-for-byte will preserve the wire payload (correct for opcodes with PUSH=0) but may need to generate the correct effective event downstream when implementing the receive-side post-receive event manager. The override is invisible at the wire layer.

## Generic Event-Forward Group (FUN_0069FDA0) [v5-validated 2026-05-28]

`FUN_0069FDA0` is the shared handler for **12 opcodes**: 0x07, 0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0E, 0x0F, 0x10, 0x11, 0x12, 0x1B. Each opcode's jump-table thunk PUSHes a distinct event-ID constant (or 0) before calling the handler. All 12 wire formats share the same shape:

```
Offset  Size  Type    Field
------  ----  ----    -----
0       1     u8      opcode
1       4     i32     object_id         (the ship/object generating the event)
5+      var   data    event-specific payload (variable)
```

Override semantics (see clarification above): when the dispatcher's PUSH constant is non-zero, it OVERRIDES the wire's event code; when PUSH = 0, the wire's value is kept.

Sender/receiver event-code pairing (artifact of the override asymmetry; the **sender** local event code -> the **dispatcher-overridden** received code):
- D8 -> D7 (StartFiring), DA -> D9, DC -> DB, DD -> 6C, E2 -> E3, E4 -> E5, EC -> ED, FE -> FD
- **Exceptions** (PUSH = 0, no pairing): 0x0C, 0x11, 0x12 (the wire value is kept)

## 0x02 / 0x03 - Object Create/Update (Server -> Client)

**Sender**: `FUN_006A1E70` (NewPlayerInGameHandler) — creates and sends to joining player
**Receiver**: `FUN_0069F620` (processes object creation on client)

These carry serialized game objects (ships, torpedoes, asteroids, etc.).

```
Offset  Size  Type    Field
------  ----  ----    -----
0       1     u8      type_tag           2 = standard object, 3 = object with team
1       1     u8      owner_player_slot  Which player owns this object
[if type_tag == 3:]
2       1     u8      team_id            Team assignment
[end if]
+0      var   data    serialized_object  vtable+0x10C serialization output
```

The `type_tag` is determined by checking if the object has a "player controller" (`FUN_005AB670`) with `FUN_005AE140` returning true (team info available).

The `serialized_object` data is produced by calling `obj->vtable[0x10C](buffer, maxlen)` which serializes the full game object state including:
- Object type ID
- Position, rotation
- Health, shields
- Subsystem states
- Weapon loadouts
- AI state

See [object-replication.md](object-replication.md) for the thin handler index and [objcreate-serialization.md](objcreate-serialization.md) for the full deserialization chain + SpeciesToShip map (canonical 45-entry table; this doc previously carried a 15-row subset which is now retired in favour of the leaf).

## 0x04 / 0x05 - Dead Opcodes (jump table default) [v5-validated 2026-05-28]

These opcode slots in the game jump table point to the DEFAULT handler at `0x0069F525` (clears processing flag and returns). They are NOT used for game messages — there is no `case '\x04':` or `case '\x05':` body in MpgameHandleMessage.

**Boot/kick is handled at the transport layer** via `TGBootPlayerMessage` (sent by `FUN_00506170`, the BootPlayerHandler registered for `ET_BOOT_PLAYER`), not as a game opcode. See [transport-layer.md](transport-layer.md) for the TGBootMessage envelope.

## 0x06 / 0x0D - Python Event (Bidirectional) [v5-validated 2026-05-28]

**Handler**: `FUN_0069F880` (dispatches to Python event system; shared between 0x06 and 0x0D via thunk `0x0069F3F1`)

```
Offset  Size  Type    Field
------  ----  ----    -----
0       1     u8      opcode (0x06 or 0x0D)
1       4     u32     event_code        (e.g. MISSION_INIT, SCORE_MESSAGE)
5+      var   data    Python event payload
```

The handler skips the opcode byte, instantiates a `TGEvent` via the factory at `FUN_006D6200`, resolves external references via `FUN_006F13C0`, zeroes the preserve field at `puVar2[9]`, and posts the event via `FUN_006DA300`.

This is the mechanism for `MISSION_INIT_MESSAGE`, `SCORE_MESSAGE`, `PLAYER_ACTION`, and all other Python multiplayer messages.

See [pythonevent-wire-format.md](pythonevent-wire-format.md) for the 4 event classes (factories 0x0101 / 0x0105 / 0x010C / 0x8129) and their serialization.

## 0x13 - Host Message [v5-validated 2026-05-28]

**Handler**: `HostMsgHandler @ 0x006A01B0`

Host-specific message dispatch. Used for self-destruct and other host-authority actions. Processes damage via `obj+0x2C4` subsystem. See [self-destruct-pipeline.md](../gameplay/self-destruct-pipeline.md).

## 0x14 - Destroy Object [v5-validated 2026-05-28]

**Handler**: `FUN_006A01E0`

```
Offset  Size  Type    Field
------  ----  ----    -----
0       1     u8      opcode (skipped)
1       4     i32v    object_id         (ReadIntVirtual)
```

Decompile shows `OpenBuffer(buf+1, len-1)` (skip the opcode byte) followed by `ReadIntVirtual()` for the object id. Then branches on the object's owner pointer at `+0x20` (`puVar3[8]`):
- If owner is NULL (`puVar3[8] == 0`): calls cleanup + destroy
- If owner is non-NULL: calls `owner->vtable[0x5C](object_id)` to notify

> **Stock trace note** [cross-source-2026-02-XX trace]: Not observed in stock MP traces (0 occurrences across 138,695 packets in a 33.5-minute combat session with 59 ship deaths — see [../analysis/valentines-day-battle-analysis.md](../analysis/valentines-day-battle-analysis.md)). Ships die via Explosion (0x29) + ObjCreateTeam (0x03) respawn. DestroyObject may only be used for non-ship objects or player disconnects.

## 0x15 - CollisionEffect (Client -> Server) [v5-validated 2026-05-28]

**Sender**: Collision detection system via `FUN_006A17C0` (event forwarder, event code `0x00800050`)
**Handler**: `CollisionEffectHandler @ 0x006A2470`
**Write method**: `0x005871A0` (CollisionEvent::Write, vtable+0x34)
**Read method**: `0x00587300` (CollisionEvent::Read, vtable+0x38)

Collision damage relay. Client detects a collision locally and sends this to the host for authoritative damage processing. **84 times** in a 15-minute 3-player stock session (4th most common combat opcode) [cross-source-2026-02-XX trace].

The handler re-posts the event with type code **`0x008000FC`** (`ET_HOST_OBJECT_COLLISION`) — distinct from the wire's `0x00800050` (`ET_OBJECT_COLLISION`). This transformation is anchored at `piVar9[4] = (int)&DAT_008000fc;` near the end of the handler body. The handler also reads `_DAT_008955C8` and rejects the event if the distance gap between source and target (minus their radii) exceeds the threshold.

See [collision-effect-protocol.md](collision-effect-protocol.md) for the complete wire format, contact point compression, handler validation chain, and decoded packet examples.

```
Offset  Size  Type    Field                    Notes
------  ----  ----    -----                    -----
0       1     u8      opcode = 0x15
1       4     i32     event_type_class_id      Always 0x00008124 (collision event factory ID)
5       4     i32     event_code               Always 0x00800050 (ET_COLLISION_EFFECT)
9       4     i32v    source_object_id         Other colliding object (0 = environment/NULL)
13      4     i32v    target_object_id         Ship reporting the collision (BC object ID)
17      1     u8      contact_count            Number of contact points (typically 1-2)
[repeated contact_count times:]
  +0    1     s8      dir_x                    Compressed direction X (signed, normalized * scale)
  +1    1     s8      dir_y                    Compressed direction Y
  +2    1     s8      dir_z                    Compressed direction Z
  +3    1     u8      magnitude_byte           Compressed distance from ship center
[end repeat]
+0      4     f32     collision_force          IEEE 754 float: impact force magnitude
```

**Total size**: 22 + contact_count * 4 bytes (typically 26 for 1 contact, 30 for 2)

## 0x16 - UI Settings Update (Server -> Client) [v5-validated 2026-05-28]

**Handler**: `FUN_00504C70` (in MultiplayerWindow dispatcher, NOT MultiplayerGame)

The opcode 0x16 entry in MpgameHandleMessage's jump table is the default cleanup at `0x0069F525`; actual handling lives in the MultiplayerWindow dispatcher `FUN_00504C10` per [wire-format-spec.md](wire-format-spec.md).

```
Offset  Size  Type    Field
------  ----  ----    -----
0       1     u8      opcode = 0x16
1       bit   bool    collision_damage_flag   Stored to DAT_008e5f59
```

Updates the collision button state in the main menu UI.

## 0x17 - Delete Player UI [v5-validated 2026-05-28]

**Handler**: `FUN_006A1360`

Removes a player's UI elements from the game display. Handler walks the TGEvent factory chain (factory ID `0x866` — see open question in tracker §4 #13) and calls `FUN_006D62B0(this)` where `this` is the MultiplayerGame instance.

See [delete-player-ui-wire-format.md](delete-player-ui-wire-format.md) for the complete wire format (join vs disconnect codes, scoreboard population semantics).

## 0x18 - Delete Player Animation

**Handler**: `FUN_006A1420`

Plays the player deletion animation sequence. **Documentation debt**: no BC-side wire-format leaf doc exists for this opcode. The OpenBC clean-room spec at `../OpenBC/docs/wire-formats/delete-player-anim-wire-format.md` documents the wire format and the TGL-lookup crash risk noted in [../analysis/tgl-lookup-crash-analysis.md](../analysis/tgl-lookup-crash-analysis.md); the BC side should mirror that doc.

## 0x19 - Torpedo/Projectile Fire (Owner -> All) [v5-validated 2026-05-28]

**Sender**: `FUN_0057CB10` (TorpedoSystem::SendFireMessage)
**Handler**: `FUN_0069F930`

```
Offset  Size  Type    Field
------  ----  ----    -----
0       1     u8      opcode = 0x19
1       4     i32     object_id         (torpedo subsystem object ID)
+0      1     u8      flags1            (subsystem index / type info)
+0      1     u8      flags2            (bit 0=has_arc, bit 1=has_target)
+0      3     cv3     velocity          CompressedVector3 (torpedo direction, 3 bytes)

if has_target (flags2 bit 1):
  +0    4     i32     target_id         (ReadInt32v)
  +0    5     cv4     impact_point      CompressedVector4 (3 dir bytes + CF16 magnitude)

Then calls FUN_0057d110 to create the torpedo projectile locally.
```

**Observed field values** [cross-source-2026-02-XX trace]:
- `flags1=0x02` for all torpedo types
- `flags2=0x05` for photon torpedoes (has_arc, no target)
- `flags2=0x07` for quantum torpedoes with target lock (has_arc + has_target)
- Dual-spread torpedoes send 2 TorpedoFire messages simultaneously (paired object IDs)
- Torpedoes are also replicated as game objects via 0x02/0x03 and tracked via 0x1C StateUpdate

See [stream-primitives.md](stream-primitives.md) for CV3 vs CV4 wire-format differences (note: CV3 is 3 bytes of direction only; CV4 is 3 dir bytes + CF16 magnitude).

## 0x1A - Beam/Phaser Fire (Owner -> All) [v5-validated 2026-05-28]

**Sender**: `FUN_00575480` (PhaserSystem::SendFireMessage)
**Handler**: `FUN_0069FBB0`

```
Offset  Size  Type    Field
------  ----  ----    -----
0       1     u8      opcode = 0x1A
1       4     i32     object_id         (phaser subsystem object ID)
+0      1     u8      flags             (single byte)
+0      3     cv3     target_position   CompressedVector3 (3 bytes direction)
+0      1     u8      more_flags        (bit 0 = has_target_id)

if has_target_id (more_flags bit 0):
  +0    4     i32     target_object_id  (ReadInt32v)

Then calls FUN_005762b0 to start beam rendering.
```

**Observed field values** [cross-source-2026-02-XX trace]:
- Ships with 2 turrets send 2 BeamFire messages simultaneously (e.g., Klingon BoP)
- `flags=0x02` observed for all beam types

## 0x1C - State Update (Bidirectional) [v5-validated 2026-05-28]

**Handler**: `FUN_0069FF50` (84-byte body, entry `0x0069FF50` to `0x0069FFEB`)

The handler is a small wrapper that delegates into the StateUpdate machinery. Round-robin serialization, dirty-flag layout, and the 8 per-flag field formats live in [stateupdate.md](stateupdate.md). Subsystem health linked-list ordering lives in [stateupdate-subsystem-wire-format.md](stateupdate-subsystem-wire-format.md).

## 0x1D - Object Not Found [v5-validated 2026-05-28]

**Handler**: `FUN_006A0490`

```
Offset  Size  Type    Field
------  ----  ----    -----
0       1     u8      opcode (skipped)
1       4     i32     object_id
```

See [objnotfound-requestobj-enterset-wire-format.md](objnotfound-requestobj-enterset-wire-format.md) for the round-trip pattern between 0x1D / 0x1E / 0x1F.

## 0x1E - Request Object State [v5-validated 2026-05-28]

**Handler**: `FUN_006A02A0`

```
Offset  Size  Type    Field
------  ----  ----    -----
0       1     u8      opcode (skipped)
1       4     i32     object_id         (ReadInt32)
```

Server finds the object, serializes it (like opcode 0x02/0x03), and sends the full object state back to the requesting client.

See [objnotfound-requestobj-enterset-wire-format.md](objnotfound-requestobj-enterset-wire-format.md).

## 0x1F - Enter Set (Change Scene) [v5-validated 2026-05-28]

**Handler**: `FUN_006A05E0`

```
Offset  Size  Type    Field
------  ----  ----    -----
0       1     u8      opcode (skipped)
1       4     i32     object_id         (ReadInt32)
+0      var   data    set_data          (ReadInt32 + raw buffer via FUN_006d2370)
```

Moves an object into a new "Set" (scene region). If the object doesn't exist locally, sends back opcode 0x1D (not found).

See [objnotfound-requestobj-enterset-wire-format.md](objnotfound-requestobj-enterset-wire-format.md) for the warp-state branch in the client-side sender and the "Space" set string constant.

## 0x20-0x28 - NetFile Dispatcher (default in MpgameHandleMessage) [v5-validated 2026-05-28]

These opcodes default-cleanup through MpgameHandleMessage because the **NetFile dispatcher** (`FUN_006A3CD0`) owns them. Per [transport-layer.md](transport-layer.md) §6.3 correction C2, the NetFile case set is **non-contiguous**: `0x20`, `0x21`, `0x22`, `0x23`, `0x25`, `0x27`. Opcodes `0x24`, `0x26`, `0x28` are dead (no handler in either dispatcher).

See [checksum-opcodes.md](checksum-opcodes.md) for the canonical NetFile opcode map and the 5-round checksum sequence.

## 0x29 - Explosion / Torpedo Hit [v5-validated 2026-05-28]

**Sender**: `FUN_00595C60` (iterates explosion list at `this+0x13C`)
**Handler**: `Handler_Explosion_0x29` at `0x006A0080`

```
Offset  Size  Type    Field
------  ----  ----    -----
0       1     u8      opcode = 0x29
1       4     i32v    object_id         (ReadIntVirtual - target ship)
5       5     cv4     impact_position   CompressedVector4 (3 dir bytes + CF16 magnitude)
10      2     u16     radius_compressed CompressedFloat16
12      2     u16     damage_compressed CompressedFloat16
Total: 14 bytes
```

**Field order verified from receiver**: the handler reads `ReadIntVirtual()` (object_id), then `CompressedVector4_ReadVirtual(..., 1)` (impact_pos with CF16 magnitude), then `ReadShort -> CompressedFloat16_Decode -> radius` (into `fStack_50`), then `ReadShort -> CompressedFloat16_Decode -> damage` (into `fStack_54`). The receiver passes `(pos, fStack_50, fStack_54)` to the `ExplosionDamage` constructor at `FUN_004BBDE0`, which stores radius at +0x14, radius^2 at +0x18, and damage at +0x1C. Then calls `ProcessDamage(ship, explosionObj)`.

This pairs with the sender (`FUN_00595C60`) writing radius from `source+0x14` first and damage from `source+0x1C` second.

Both radius and damage are CF16 (lossy). See [cf16-precision-analysis.md](cf16-precision-analysis.md) for precision limits and [cf16-explosion-encoding.md](cf16-explosion-encoding.md) for radius-before-damage field-order anchoring and mod compatibility implications.

## 0x2A - New Player In Game [v5-validated 2026-05-28]

**Handler**: `NewPlayerInGameHandler @ 0x006A1E70`

Signals that a new player has fully joined the game session. Triggers Python InitNetwork handlers and object replication to the new player.

See [delete-player-ui-wire-format.md](delete-player-ui-wire-format.md) for how 0x2A interacts with the join event code `0x008000F1` (`ET_NEW_PLAYER_IN_GAME`) and scoreboard population.
