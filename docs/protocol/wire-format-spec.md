> [docs](../README.md) / [protocol](README.md) / wire-format-spec.md

---
title: STBC Multiplayer Wire Format Specification
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
  - docs/protocol/transport-layer.md
  - docs/protocol/stream-primitives.md
  - docs/protocol/game-opcodes.md
  - docs/protocol/checksum-opcodes.md
  - docs/protocol/python-messages.md
  - docs/protocol/stateupdate.md
  - docs/protocol/subsystem-integrity-hash.md
  - docs/protocol/collision-effect-protocol.md
  - docs/protocol/pythonevent-wire-format.md
  - docs/engine/v5-validation-status.md
  - docs/protocol/v5-validation-status.md
evidence:
  - claim: "MpgameHandleMessage dispatcher at 0x0069f2a0 owns game opcodes 0x02-0x2A via 41-entry jump table at 0x0069F534 (opcode-2 indexed)"
    address: 0x0069f2a0
    function: MpgameHandleMessage
    completeness: 69.84
    confidence: high
    note: "Jump table 0x0069F534 verified via plate comment + decompile; 41 entries cover opcodes 0x02..0x2A (0x04/0x05 are jump-table defaults)"
  - claim: "NetFile dispatcher FUN_006a3cd0 handles checksum/file opcodes 0x20-0x28"
    address: 0x006a3cd0
    function: FUN_006a3cd0
    completeness: 0.60
    confidence: high
    note: "Flagged for dedicated v5 pass — function exists, body matches doc but completeness score is sub-baseline"
  - claim: "MultiplayerWindow dispatcher FUN_00504c10 handles UI-level opcodes 0x00 / 0x01 / 0x16"
    address: 0x00504c10
    function: FUN_00504c10
    completeness: 9.64
    confidence: high
    note: "Flagged for dedicated v5 pass"
  - claim: "All 16 dispatched game-opcode handler addresses confirmed via get_function_by_address against STBC.exe"
    address: 0x0069F534
    function: MpgameHandleMessage
    completeness: 69.84
    confidence: high
    note: "Jump table walk; per-handler addresses 0x0069f620, 0x0069f880, 0x0069fda0, 0x006A01B0, 0x006a01e0, 0x006a2470, 0x006a1360, 0x006a1420, 0x0069F930, 0x0069FBB0, 0x0069FF50, 0x006a0490, 0x006a02a0, 0x006a05e0, 0x006A0080, 0x006A1E70 — all bodies exist + sizes match"
  - claim: "6 NetFile handlers (0x20 ChecksumRequest 0x006a5df0, 0x21 ChecksumResponse 0x006a4260, 0x22 VersionMismatch 0x006a4c10, 0x23 SystemChecksumFail 0x006a4c10, 0x25 FileTransfer 0x006a3ea0, 0x27 FileTransferACK 0x006a4250)"
    address: 0x006a3cd0
    function: FUN_006a3cd0
    completeness: 0.60
    confidence: high
  - claim: "3 MultiplayerWindow handlers (0x00 Settings 0x00504D30, 0x01 GameInit 0x00504F10, 0x16 UICollisionSetting 0x00504C70)"
    address: 0x00504c10
    function: FUN_00504c10
    completeness: 9.64
    confidence: high
  - claim: "29 event-handler registrations performed by FUN_0069EFE0; each row is a (LAB_xxxx, string-name) pair"
    address: 0x0069efe0
    function: FUN_0069efe0
    completeness: 0.00
    confidence: high
    note: "Identity proven by registration strings (e.g. s_MultiplayerGame____SetPhaserLeve_00959f1c -> 'MultiplayerGame :: SetPhaserLevelHandler' at LAB_006a1970). 24 of 29 handlers are DATA-only xrefs without Ghidra function entries — same pattern that previously hid MpgameHandleMessage"
  - claim: "Settings packet (opcode 0x00) wire format: opcode byte, gameTime float, DAT_008e5f59 bit, DAT_0097faa2 bit, playerSlot byte, mapLen short, mapName bytes, checksumFlag bit, optional checksum data"
    address: 0x006a1b10
    function: FUN_006a1b10
    completeness: 0.00
    confidence: high
    note: "CORRECTION (was [byte:...]): decompile of FUN_006a1b10 shows WriteBit (FUN_006cf770) for all three settings bits; WriteByte calls flush the bit group. Material for any decoder"
  - claim: "WriteBit primitive at FUN_006cf770 packs up to 5 bits into a byte using a 3-bit count prefix + 5-bit data tail"
    address: 0x006cf770
    function: FUN_006cf770
    completeness: 0.00
    confidence: high
    note: "Stream-primitives ground truth; manipulates TGBufferStream +0x2C bit-pack state"
  - claim: "Anti-cheat subsystem hash is DEAD CODE on the multiplayer path"
    address: 0x005b17f0
    function: FUN_005b17f0
    completeness: 0.00
    confidence: high
    note: "Sender gates hash compute on bVar17 = (DAT_0097fa8a == 0) — i.e. single-player only. MP path WriteBit(0) and skips ComputeSubsystemHash entirely"
  - claim: "Subsystem hash iterates 12 fixed slots from ship+0x27C using +0x34..+0x60 sub-offsets (FUN_005b5eb0 ComputeSubsystemHash)"
    address: 0x005b5eb0
    function: FUN_005b5eb0
    completeness: 0.00
    confidence: high
    note: "Canonical 12-slot table lives in subsystem-integrity-hash.md; this doc keeps a 1-line summary + link (was duplicate table at lines 188-208)"
  - claim: "Ship+0x2BC = Pulse Weapon System parent slot (PulseWeaponSystem; vtable installer at 0x00893794)"
    address: 0x005b5030
    function: FUN_005b5030
    completeness: 6.26
    confidence: high
    note: "CORRECTION (was '(unused) NULL always'): decompile case 0x802D (PulseWeapon class ID) reads ship+700 (= 0x2BC). Resolves cross-doc conflict #4"
  - claim: "Ship+0x2D4 = Tractor Beam System parent slot (TractorBeamSystem; vtable installer at 0x008936F0)"
    address: 0x005b5030
    function: FUN_005b5030
    completeness: 6.26
    confidence: high
    note: "CORRECTION (was 'Pulse 0x00893794'): decompile case 0x802E (TractorBeamProjector class ID) reads ship+0x2D4"
  - claim: "Key globals: UtopiaModule 0x0097FA00, WSN ptr 0x0097FA78, settings bytes DAT_008e5f59 / DAT_0097faa2, Clock obj 0x009a09d0 (gameTime at +0x90)"
    address: 0x0097FA00
    function: (engine-inherited)
    completeness: null
    confidence: high
    note: "Cross-anchored to engine v5-validated decompiled-functions.md / function-map.md; xrefs confirmed via get_xrefs_to"
  - claim: "Ship+0x2DC slot description ('unused NULL') not verified this pass; possible misidentification pending per-ship-subsystem-wire-format.md validation"
    address: null
    function: FUN_005b5030
    completeness: 6.26
    confidence: low
    note: "FUN_005b5030 only handles 4 weapon classes (0x802C/D/E/F); other 9 named-slot rows untraced. Tracked in protocol v5-validation-status §3.1"
supersedes:
  - 2026-02-10
---

# Star Trek: Bridge Commander - Multiplayer Wire Format Specification

> [!NOTE]
> This doc is `status: partial`. The 3-dispatcher overview, opcode jump table (41 entries, 0x02-0x2A), 29 event-handler registrations, key globals, subsystem catalog, and anti-cheat hash dead-code claim are v5-validated against the current Ghidra import (2026-05-28). Settings packet wire layout was corrected to bit-pack form (was previously documented as byte-form — material for any decoder). Subsystem catalog ship+0x2BC and ship+0x2D4 slot identities corrected (cross-doc disagreement #4 resolved; subsystem-integrity-hash.md is canonical). This doc is a **hub** — it consolidates summary tables for the protocol family; per-opcode detail lives in the linked companion docs. See [docs/guides/v5-evidence-header.md](../guides/v5-evidence-header.md) for the v5 standard.

Produced by systematic decompilation of stbc.exe (base 0x400000, ~5.9MB) using Ghidra.
Validated against stock dedicated server packet traces (30,000+ packets).
See also: [message-trace-vs-packet-trace.md](message-trace-vs-packet-trace.md) for packet-trace cross-reference.

## Detailed Sub-Documents

| Document | Contents |
|----------|----------|
| [transport-layer.md](transport-layer.md) | Raw UDP packet, 7 transport types, TGMessage layout/vtable, fragment reassembly, reliable delivery |
| [stream-primitives.md](stream-primitives.md) | TGBufferStream read/write functions, bit packing, CF16 encoding/decoding, CompressedVector3/4 |
| [checksum-opcodes.md](checksum-opcodes.md) | Opcodes 0x20-0x28: checksum request/response, file transfer, 5 checksum rounds |
| [game-opcodes.md](game-opcodes.md) | Opcodes 0x00-0x2A: Settings, GameInit, ObjCreate, PythonEvent, EventForward, CollisionEffect, TorpedoFire, BeamFire, Explosion, etc. |
| [stateupdate.md](stateupdate.md) | Opcode 0x1C: dirty flags, 8 field formats, round-robin subsystem/weapon serialization, force-update timing |
| [object-replication.md](object-replication.md) | FUN_0069f620 object create/update, serialization chain |
| [python-messages.md](python-messages.md) | Opcodes 0x2C+: TGMessage script messages, SendTGMessage API, wire examples, receive dispatch |

## Related Protocol Documents

| Document | Contents |
|----------|----------|
| [pythonevent-wire-format.md](pythonevent-wire-format.md) | PythonEvent (0x06) polymorphic event transport, 4 factory types |
| [tgobjptrevent-class.md](tgobjptrevent-class.md) | TGObjPtrEvent (factory 0x010C): class layout, wire format, 5 C++ producers |
| [set-phaser-level-protocol.md](set-phaser-level-protocol.md) | SetPhaserLevel (opcode 0x12): TGCharEvent wire format |
| [collision-effect-protocol.md](collision-effect-protocol.md) | CollisionEffect (opcode 0x15): contact point compression, handler validation |
| [stateupdate-subsystem-wire-format.md](stateupdate-subsystem-wire-format.md) | Subsystem health wire format: linked list order, WriteState formats |
| [subsystem-integrity-hash.md](subsystem-integrity-hash.md) | Subsystem hash (anti-cheat): dead code in MP — **canonical for 12-slot hash table** |
| [cf16-precision-analysis.md](cf16-precision-analysis.md) | CF16 precision tables and mod compatibility |
| [cf16-explosion-encoding.md](cf16-explosion-encoding.md) | CF16 explosion encoding analysis |
| [delete-player-ui-wire-format.md](delete-player-ui-wire-format.md) | DeletePlayerUI (0x17): TGEvent transport for join/disconnect player list updates |
| [tgmessage-routing.md](tgmessage-routing.md) | TGMessage routing: relay-all, no whitelist, star topology |

---

## Summary: Opcode Table

### MultiplayerWindow Dispatcher (FUN_00504c10, handles 0x00/0x01/0x16) `[v5-validated 2026-05-28]`

| Opcode | Name | Direction | Handler | Payload Summary |
|--------|------|-----------|---------|-----------------|
| 0x00 | Settings | S->C | FUN_00504d30 | gameTime, **bit:**DAT_008e5f59, **bit:**DAT_0097faa2, playerSlot, mapName, **bit:**checksumFlag (see Settings Packet below) |
| 0x01 | GameInit | S->C | FUN_00504f10 | (empty - just the opcode byte) |
| 0x16 | UICollisionSetting | S->C | FUN_00504c70 | collisionDamageFlag (bit) |

### Game Opcodes (MultiplayerGame Dispatcher at 0x0069F2A0, jump table at 0x0069F534, opcodes 0x02-0x2A) `[v5-validated 2026-05-28]`

The dispatcher was recovered as `MpgameHandleMessage` (engine-family v5 pass; see [function-map.md](../engine/function-map.md) and [decompiled-functions.md](../engine/decompiled-functions.md)). Effective completeness 69.84 — named + plated, two hungarian-violations + three type-quality issues remaining.

| Opcode | Name | Direction | Handler | Payload Summary |
|--------|------|-----------|---------|-----------------|
| 0x02 | ObjectCreate | S->C | FUN_0069f620 | type=2, ownerSlot, serializedObject |
| 0x03 | ObjectCreateTeam | S->C | FUN_0069f620 | type=3, ownerSlot, teamId, serializedObject |
| 0x04 | (dead) | -- | DEFAULT | Jump table default; boot handled at transport layer |
| 0x05 | (dead) | -- | DEFAULT | Jump table default |
| 0x06 | PythonEvent | any | FUN_0069f880 | eventCode, eventPayload |
| 0x07 | StartFiring | any | FUN_0069fda0 | objectId, event data (-> event 0x008000D7) |
| 0x08 | StopFiring | any | FUN_0069fda0 | objectId, event data (-> event 0x008000D9) |
| 0x09 | StopFiringAtTarget | any | FUN_0069fda0 | objectId, event data (-> event 0x008000DB) |
| 0x0A | SubsysStatus | any | FUN_0069fda0 | objectId, event data (-> event 0x0080006C) |
| 0x0B | AddToRepairList | any | FUN_0069fda0 | objectId, event data (-> event 0x008000DF) |
| 0x0C | ClientEvent | any | FUN_0069fda0 | objectId, event data (from stream, preserve=0) |
| 0x0D | PythonEvent2 | any | FUN_0069f880 | eventCode, eventPayload (shared receiver with 0x06) |
| 0x0E | StartCloaking | any | FUN_0069fda0 | objectId, event data (-> event 0x008000E3) |
| 0x0F | StopCloaking | any | FUN_0069fda0 | objectId, event data (-> event 0x008000E5) |
| 0x10 | StartWarp | any | FUN_0069fda0 | objectId, event data (-> event 0x008000ED) |
| 0x11 | RepairListPriority | any | FUN_0069fda0 | objectId, event data (-> event 0x00800076) |
| 0x12 | SetPhaserLevel | any | FUN_0069fda0 | objectId, event data (-> event 0x008000E0) |
| 0x13 | HostMsg | C->S | FUN_006A01B0 | host-specific dispatch (self-destruct etc.) |
| 0x14 | DestroyObject | S->C | FUN_006a01e0 | objectId. **Not observed in stock MP ship deaths** — ships die via 0x29+0x03 |
| 0x15 | CollisionEffect | C->S | FUN_006a2470 | typeClassId(0x8124), eventCode(0x800050), srcObjId, tgtObjId, count, count*cv4_byte(dir+mag), force(f32). **C->S only, server never relays** |
| 0x16 | (default) | -- | DEFAULT | Handled by MultiplayerWindow dispatcher, not game jump table |
| 0x17 | DeletePlayerUI | S->C | FUN_006a1360 | Serialized TGEvent (factory 0x866): join=ET_NEW_PLAYER_IN_GAME (0x8000F1), disconnect=ET_NETWORK_DELETE_PLAYER (0x60005). 18 bytes: classID(4), eventCode(4), srcObj(4), tgtObj(4), peerID(1). See [delete-player-ui-wire-format.md](delete-player-ui-wire-format.md) |
| 0x18 | DeletePlayerAnim | S->C | FUN_006a1420 | player deletion animation |
| 0x19 | TorpedoFire | owner->all | FUN_0069f930 | objId, flags, velocity(cv3), [targetId, impact(cv4)] |
| 0x1A | BeamFire | owner->all | FUN_0069fbb0 | objId, flags, targetDir(cv3), moreFlags, [targetId] |
| 0x1B | TorpTypeChange | any | FUN_0069fda0 | objectId, event data (-> event 0x008000FD) |
| 0x1C | StateUpdate | owner->all | FUN_0069FF50 | objectId, gameTime, dirtyFlags, [fields...] — see [stateupdate.md](stateupdate.md) |
| 0x1D | ObjNotFound | S->C | FUN_006a0490 | objectId (0x3FFFFFFF queries are normal) |
| 0x1E | RequestObject | C->S | FUN_006a02a0 | objectId (server responds with 0x02/0x03) |
| 0x1F | EnterSet | S->C | FUN_006a05e0 | objectId, setData |
| 0x20-0x28 | (default) | -- | DEFAULT | Handled by NetFile dispatcher, not game jump table |
| 0x29 | Explosion | S->C | FUN_006a0080 | objectId, impact(cv4), damage(cf16), radius(cf16) |
| 0x2A | NewPlayerInGame | C->S | FUN_006a1e70 | Client sends to server after ship selection. **Direction verified C->S from stock traces** |

> [!NOTE]
> **Factory 0x866 (opcode 0x17)** is flagged in [v5-validation-status.md §4 #13](v5-validation-status.md) — it doesn't appear in the engine factory catalog (0x02 / 0x101 / 0x105 / 0x10C / 0x8124 / 0x8129) and needs dedicated anchoring. The DeletePlayerUI doc names it; the family-level resolution is pending.

### Python-Level Messages (via SendTGMessage, bypass C++ dispatcher)

| Byte | Name | Direction | Handler | Payload Summary |
|------|------|-----------|---------|-----------------|
| 0x2C | CHAT_MESSAGE | relayed | Python ReceiveMessage | senderSlot, padding, msgLen, ASCII text |
| 0x2D | TEAM_CHAT_MESSAGE | relayed | Python ReceiveMessage | same format as 0x2C |
| 0x35 | MISSION_INIT_MESSAGE | S->C | Python ReceiveMessage | game config, sent after ObjCreateTeam |
| 0x36 | SCORE_CHANGE_MESSAGE | S->C | Python ReceiveMessage | score deltas |
| 0x37 | SCORE_MESSAGE | S->C | Python ReceiveMessage | full score sync, sent once during join |
| 0x38 | END_GAME_MESSAGE | S->C | Python ReceiveMessage | game over signal |
| 0x39 | RESTART_GAME_MESSAGE | S->C | Python ReceiveMessage | game restart signal |

### Checksum/NetFile Opcodes `[v5-validated 2026-05-28]`

| Opcode | Name | Direction | Handler | Payload Summary |
|--------|------|-----------|---------|-----------------|
| 0x20 | ChecksumRequest | S->C | FUN_006a5df0 | index, directory, filter, recursive |
| 0x21 | ChecksumResponse | C->S | FUN_006a4260 | index, hashes |
| 0x22 | VersionMismatch | S->C | FUN_006a4c10 | filename |
| 0x23 | SystemChecksumFail | S->C | FUN_006a4c10 | filename |
| 0x25 | FileTransfer | S->C | FUN_006a3ea0 | filename, filedata |
| 0x27 | FileTransferACK | C->S | FUN_006a4250 | (empty) |

Detail in [checksum-opcodes.md](checksum-opcodes.md).

---

## Settings Packet (opcode 0x00) — Bit-Pack Detail `[v5-validated 2026-05-28]`

Producer is `FUN_006a1b10` (the post-checksum sender — engine-family registers it as `ChecksumCompleteHandler`, see [decompiled-functions.md](../engine/decompiled-functions.md)). Wire layout:

```
WriteByte(0x00)                       opcode
WriteFloat(*(DAT_009a09d0 + 0x90))    gameTime (from Clock+0x90)
WriteBit(DAT_008e5f59)                bit-packed setting 1 (collisionDamage)
WriteBit(DAT_0097faa2)                bit-packed setting 2 (friendlyFire)
WriteByte(playerSlot)                 1 byte — closes/breaks the bit group
WriteShort(strlen(mapName))           2 bytes
WriteBytes(mapName, strlen)
WriteBit(checksumFlag)                bit-packed (new group)
if (checksumFlag) FUN_006f3f30(...)   appended checksum data
```

**Bit-packing wrapper** ([stream-primitives.md](stream-primitives.md)): `FUN_006cf770` (WriteBit) accumulates up to 5 bits into a single byte before flushing. The format is a 3-bit count prefix + 5-bit data tail. The intervening `WriteByte(playerSlot)` call flushes whatever bit group was open at that point — so on the wire, the two settings bits appear as a single byte (mostly zero-padded), then playerSlot, then mapLen short, then mapName bytes, then a one-bit byte for checksumFlag.

This matters for any decoder: clients that read bit-by-bit see the correct semantic; clients that read byte-by-byte and assume the field is a `[byte:DAT_008e5f59]` will work in practice only because the high bits of the bit-group byte happen to be zero. The pre-v5 doc described the packet as three sequential `[byte:...]` fields; that representation is the *visible byte on the wire* but not the *architectural format*.

Then opcode 0x01 (`GameInit`, single byte) follows in a separate message.

---

## Event-Handler Registration (from FUN_0069efe0) `[v5-validated 2026-05-28]`

> [!NOTE]
> **DATA-only xref pattern.** Many event-handler functions in this table are reached only through the registration call site inside `FUN_0069efe0`, which means Ghidra's auto-analysis does not promote them to function entries — they appear as `LAB_xxxxxxxx` labels. The v5 dispatcher recovery (2026-05-28) recovered `MpgameHandleMessage` from exactly this pattern. The 29 rows below are **identity-proven by their registration strings**: `decompile_function(0x0069efe0)` returns 29 `FUN_006da130(&LAB_xxxxxxxx, s_MultiplayerGame____<Name>Handler)` calls, and every doc row's name matches its registration-string literal exactly. If `get_function_by_address` returns "no function" for an address below, that is the expected state, not a doc error.

| Address | Name |
|---------|------|
| 0x0069f2a0 | MpgameHandleMessage (main dispatch) |
| 0x006a0a20 | DisconnectHandler |
| 0x006a0a30 | NewPlayerHandler |
| 0x006a0c60 | SystemChecksumPassHandler |
| 0x006a0c90 | SystemChecksumFailHandler |
| 0x006a0ca0 | DeletePlayerHandler |
| 0x006a0f90 | ObjectCreatedHandler |
| 0x006a1150 | HostEventHandler |
| 0x006a1590 | NewPlayerInGameHandler |
| 0x006a1790 | StartFiringHandler |
| 0x006a17a0 | StartWarpHandler |
| 0x006a17b0 | TorpedoTypeChangeHandler |
| 0x006a18d0 | StopFiringHandler |
| 0x006a18e0 | StopFiringAtTargetHandler |
| 0x006a18f0 | StartCloakingHandler |
| 0x006a1900 | StopCloakingHandler |
| 0x006a1910 | SubsystemStatusHandler |
| 0x006a1920 | AddToRepairListHandler |
| 0x006a1930 | ClientEventHandler |
| 0x006a1940 | RepairListPriorityHandler |
| 0x006a1970 | SetPhaserLevelHandler |
| 0x006a1a60 | DeleteObjectHandler |
| 0x006a1a70 | ChangedTargetHandler |
| 0x006a1b10 | ChecksumCompleteHandler |
| 0x006a2640 | KillGameHandler |
| 0x006a2a40 | RetryConnectHandler |
| 0x006a1240 | ObjectExplodingHandler |
| 0x006a07d0 | EnterSetHandler |
| 0x006a0a10 | ExitedWarpHandler |

---

## Key Globals `[v5-validated 2026-05-28]`

Cross-anchored to the engine-family v5-validated globals table (see [decompiled-functions.md](../engine/decompiled-functions.md) and the **Key Globals** section in [CLAUDE.md](../../CLAUDE.md)).

| Address | What | Verified via |
|---------|------|--------------|
| 0x0097FA00 | UtopiaModule base | engine-family anchor; `get_xrefs_to` confirms |
| 0x0097FA78 | TGWinsockNetwork ptr (UtopiaModule+0x78) | 5+ READ xrefs from MP/dispatcher code |
| 0x0097FA88 | IsClient (BYTE) — 0=host, 1=client | engine-family anchor |
| 0x0097FA89 | IsHost (BYTE) — 1=host, 0=client | engine-family anchor |
| 0x0097FA8A | IsMultiplayer (BYTE) — gates anti-cheat hash | FUN_005b17f0 `bVar17 = (DAT_0097fa8a == 0)` |
| 0x008e5f59 | Settings bit 1 (collisionDamage) | WRITE from FUN_00504c70/d30/0069e590; READ from FUN_006a1b10 (Settings sender) |
| 0x0097faa2 | Settings bit 2 (friendlyFire) | READ patterns match (set by MP setup, read by Settings sender) |
| 0x009a09d0 | Clock object ptr (+0x90 = gameTime, +0x54 = frameTime) | multiple READ xrefs match doc claim |

---

## Ship Subsystem Type Catalog `[v5-validated 2026-05-28]`

Subsystem catalog from JMP detour trace (stock dedicated server, 223K lines) cross-anchored against `decompile_function(0x005b5030)` (Ship_LinkSubsystemToParent — switches on weapon-class IDs 0x802C-0x802F to install child weapons into their parent slot).

See [../analysis/subsystem-trace-analysis.md](../analysis/subsystem-trace-analysis.md) for full trace data and [subsystem-integrity-hash.md](subsystem-integrity-hash.md) for the anti-cheat hash slot table (canonical).

### Vtable-to-Type Map

| vtable | Type | Named Slot | Offset | Instances (Sovereign) |
|--------|------|-----------|--------|----------------------|
| 0x0088A1F0 | PoweredSubsystem | Powered | +2B0 | 1 |
| 0x00892C98 | PowerReactor | Power | +2C4 | 1 (+1 secondary in list) |
| 0x00892D10 | LifeSupport | Unk_C | +2CC | 1 |
| 0x00892E24 | WarpDrive | Unk_E | +2D8 | 1 |
| 0x00892EAC | CloakingDevice | Cloak | +2C8 | 1 |
| 0x00892F34 | RepairSubsystem | Repair | +2C0 | 1 |
| 0x00892FC4 | ImpulseEngine | -- | -- | 4 |
| 0x00893040 | SensorArray | Unk_B | +2D0 | 1 |
| 0x00893194 | PhaserEmitter | -- | -- | 8 |
| 0x00893240 | PhaserController | Phaser | +2B8 | 1 |
| 0x00893598 | ShieldGenerator | Shield | +2B4 | 1 |
| 0x00893630 | TorpedoTube | -- | -- | 6 (4 fwd, 2 aft) |
| 0x008936F0 | TractorBeam | Tractor | +2D4 | 4 |
| 0x00893794 | PulseWeapon | Pulse | +2BC | 1 |
| 0x00895340 | ShipRefNiNode | ShipRef | +2E0 | 1 (set separately) |

### Named Slot Layout (ship+0x2B0 to ship+0x2E4)

```
+2B0  Powered      0x0088A1F0   Master powered subsystem
+2B4  Shield       0x00893598   Shield generator
+2B8  Phaser       0x00893240   Phaser controller
+2BC  Pulse        0x00893794   Pulse Weapon System parent  *** corrected 2026-05-28 ***
+2C0  Repair       0x00892F34   Auto-repair
+2C4  Power        0x00892C98   Power reactor
+2C8  Cloak        0x00892EAC   Cloaking device (present on all ships)
+2CC  LifeSupport  0x00892D10   Structural/life support
+2D0  SensorArray  0x00893040   Sensors
+2D4  Tractor      0x008936F0   Tractor Beam System parent  *** corrected 2026-05-28 ***
+2D8  WarpDrive    0x00892E24   Warp drive
+2DC  (unused?)    NULL         Not verified this pass — may be misidentified
+2E0  ShipRef      0x00895340   NiNode scene graph backpointer
```

> [!IMPORTANT]
> **Corrections 2026-05-28** — Ground truth from `decompile_function(0x005b5030)`:
> - `case 0x802C` (PhaserBank) → reads `ship+0x2B8` (Phaser parent)
> - `case 0x802D` (PulseWeapon) → reads `ship+0x2BC` (**Pulse** parent — was previously documented as "(unused) NULL")
> - `case 0x802E` (TractorBeamProjector) → reads `ship+0x2D4` (**Tractor** parent — was previously documented as Pulse)
> - `case 0x802F` (TorpedoTube) → reads `ship+0x2B4` (Torpedo parent)
>
> The vtable-to-type map above is and was correct (0x00893794 is PulseWeapon, 0x008936F0 is TractorBeam). The Named Slot Layout had the Pulse/Tractor *slot offsets* swapped — that's the load-bearing correction. Resolves protocol v5-validation-status §4 disagreement #4.
>
> The `+0x2DC` row is held at low confidence — FUN_005b5030 only handles 4 weapon classes, and the other 9 named-slot rows have not been ground-truthed by a switch decompile. Tracked as an open question in [v5-validation-status.md §6.1](v5-validation-status.md).

### Anti-Cheat Hash Field Offsets

> **Full hash order table:** see [subsystem-integrity-hash.md](subsystem-integrity-hash.md) — canonical 12-slot subsystem hash order with vtable installer addresses, sub-offsets from ship+0x27C, and per-slot hash methods (base / weapon / type-specific extras).
>
> Anti-cheat hash is **dead code on the multiplayer path** (`FUN_005b17f0` gates on `DAT_0097fa8a == 0` — single-player only). MP path emits `WriteBit(0)` and skips `ComputeSubsystemHash` entirely. The Repair subsystem (+0x2C0) is also not part of the hash.

(The duplicate 12-row table that previously lived in this doc has been retired in favor of subsystem-integrity-hash.md as the single source of truth. Resolves protocol v5-validation-status §4 disagreement #5.)
