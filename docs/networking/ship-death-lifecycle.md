---
title: Ship Death Lifecycle in Multiplayer
type: reference
audience: RE engineers, OpenBC implementers
validated: 2026-05-28
methodology: FUNCTION_DOC_WORKFLOW_V5
binary_fingerprint: stbc.exe (base 0x400000, 32-bit Windows)
status: partial
supersedes:
  - 2026-02-21
evidence:
  - claim: "MultiplayerGame_ObjectExplodingHandler — dual-branch SP/MP handler for ET_OBJECT_EXPLODING"
    address: 0x006a1240
    confidence: high
    note: "283 bytes, CREATED in Ghidra this pass (was bare code, auto-analyzer hadn't promoted); dual-branch decompile verified"
  - claim: "Handler registration via FUN_006da130 (EventManager AddHandler) — pushes string + handler addr"
    address: 0x0069efe0
    confidence: high
    note: "registration block at 0x006a1c0-0x006a1cf: PUSH 0x95a054 (s_MultiplayerGame__ObjectExplodingHandler), PUSH 0x6a1240, MOV ECX,0x97f838, CALL 0x006da130"
  - claim: "Handler MP/SP branch on IsMultiplayer (DAT_0097fa8a)"
    address: 0x006a124e
    confidence: high
    note: "0x006a124e: MOV AL,[0x0097fa8a]; 0x006a1260: TEST AL,AL; 0x006a1264: JZ 0x006a131b (SP branch)"
  - claim: "MP branch writes opcode 0x06 byte at start of payload"
    address: 0x006a127f
    confidence: high
    note: "MOV byte ptr [ESP+0x3c], 0x6"
  - claim: "MP branch serializes event polymorphically via vtable+0x34 (WriteToStream)"
    address: 0x006a12b1
    confidence: high
    note: "PUSH EAX (stream); MOV EDX,[ECX]; CALL [EDX+0x34] — same vtable slot as TGCharEvent/TGObjPtrEvent/TGEvent base"
  - claim: "MP branch allocates 0x40-byte TGMessage via TGAlloc(s_UNKNOWN, 0x40)"
    address: 0x006a12c0
    confidence: high
    note: "0x006a12c0: PUSH 0x8d858c (s_UNKNOWN); 0x006a12c5: PUSH 0x40; 0x006a12cd: CALL 0x00717b70; 0x006a12d4: CALL 0x00718010"
  - claim: "MP branch sends to relay group \"NoMe\" via SendTGMessageToGroup"
    address: 0x006a12f4
    confidence: high
    note: "0x006a12f4: PUSH 0x8e5528 (s_NoMe); 0x006a12ff: CALL 0x006b4de0 (TGWinsockNetwork_SendTGMessageToGroup)"
  - claim: "MP branch sets guaranteed-delivery flag (msg+0x3a = 1)"
    address: 0x006a12fb
    confidence: high
    note: "MOV byte ptr [ESI+0x3a], 0x1"
  - claim: "SP branch writes event.lifetime (event+0x2c) to ship+0x14c (HP slot)"
    address: 0x006a1335
    confidence: high
    note: "0x006a1332: FLD float [ESI+0x2c]; 0x006a1335: FSTP [EAX+0x14c]; EAX = ship from CastToShipClass"
  - claim: "SP branch casts via CastToShipClass (FUN_005ab670, IsA 0x8008)"
    address: 0x006a1326
    confidence: high
    note: "PUSH [ESI+0xc] (event.objectRef); CALL 0x005ab670"
  - claim: "SP branch triggers visual effects via FUN_005ac250 (loads \"Effects\" + \"ObjectExploding\" strings)"
    address: 0x006a133d
    confidence: medium
    note: "FUN_005ac250 decompile shows string load of s_Effects (0x008e0ee0) + s_ObjectExploding (0x008e6198)"
  - claim: "Handler_Explosion_0x29 — receives Explosion opcode (S->C only)"
    address: 0x006a0080
    confidence: high
    note: "skip opcode byte, ReadInt(objID), FUN_00590a50 (CastToDamageableObject), CV4 position, CF16 damage, CF16 radius, FUN_004bbde0 (ExplosionDamage ctor per leaf #20/21), FUN_00593e50 (apply)"
  - claim: "Handler_DestroyObject_0x14 — vtable[0] destructor invocation"
    address: 0x006a01e0
    confidence: high
    note: "skip opcode, ReadInt(objID), TGSceneGraph__GetObjectByID; if obj+0x20 NULL call vtable[0] dtor; else forward to parent. NOT invoked for MP ship deaths per trace"
  - claim: "MpgameHandleObjCreate — receives ObjCreate (0x02) / ObjCreateTeam (0x03)"
    address: 0x0069f620
    confidence: high
    note: "already named per leaf #9; signature has team byte param"
  - claim: "\"NoMe\" relay group name (relay-to-all-peers-except-self)"
    address: 0x008e5528
    confidence: high
    note: "inspect_memory: \"NoMe\\0\" at 0x008e5528"
  - claim: "\"MultiplayerGame :: ObjectExplodingHandler\" registration string"
    address: 0x0095a054
    confidence: high
    note: "pushed at FUN_0069efe0 registration block"
  - claim: "\"UNKNOWN\" TGAlloc class-name string"
    address: 0x008d858c
    confidence: high
  - claim: "TGAlloc allocator + factory dispatch pair"
    address: 0x00717b70
    confidence: high
    note: "0x00717b70 = TGAlloc; 0x00718010 = factory dispatch (cascade pattern from leaf #18)"
  - claim: "TGWinsockNetwork_SendTGMessageToGroup"
    address: 0x006b4de0
    confidence: high
  - claim: "TGWinsockNetwork singleton"
    address: 0x0097fa78
    confidence: high
    note: "MOV ECX,[0x0097fa78] precedes SendTGMessageToGroup call"
  - claim: "IsMultiplayer flag (DAT_0097fa8a, byte)"
    address: 0x0097fa8a
    confidence: high
  - claim: "Factory 0x8129 (ObjectExplodingEvent) — vtable 0x0088A178, ctor 0x0043F8B0, GetFactoryID 0x0043F8E0"
    address: null
    confidence: high
    note: "inherited from pythonevent-wire-format leaf #14"
  - claim: "Factory 0x101 (TGEvent base) — vtable 0x00895FF4, ctor FUN_006d5c00; carries ET_ADD_TO_REPAIR_LIST (0x008000DF) events for self-destruct repair routing"
    address: null
    confidence: high
    note: "inherited from tgobjptrevent leaf #13; \"TGSubsystemEvent\" name was fabricated — no such class exists in stbc.exe"
  - claim: "Event ID ET_OBJECT_EXPLODING = 0x0080004E"
    address: null
    confidence: high
    note: "inherited from pythonevent-wire-format leaf #14; string at 0x00910ac8"
  - claim: "Event ID ET_ADD_TO_REPAIR_LIST = 0x008000DF"
    address: null
    confidence: high
    note: "inherited from architecture/multiplayer-mission-infrastructure.md + game-opcodes.md"
  - claim: "Ship HP slot at ship+0x14c (FLT_MAX undamaged sentinel)"
    address: null
    confidence: high
    note: "inherited from objnotfound-requestobj-enterset leaf #18 (DamageableObject HP slot)"
  - claim: "Event lifetime field at event+0x2c (set to 9.5f per stock trace)"
    address: null
    confidence: high
    note: "byte-confirmed in SP branch FLD/FSTP; constant-source location is OQ2"
  - claim: "Event objectRef field at event+0xc (dest object, dying ship in SP branch)"
    address: null
    confidence: medium
    note: "passed to CastToShipClass at 0x006a1326; layout-vs-wire question is OQ3"
  - claim: "Explosion CF16 encoding (damage, radius)"
    address: null
    confidence: high
    note: "inherited from cf16-explosion-encoding leaf #21"
  - claim: "DestroyObject (0x14) NOT used for MP ship death — 0/59 in 33.5-min battle trace, 0/6 in self-destruct trace"
    address: null
    confidence: high
    note: "trace evidence from packet_trace.log (battle session + self-destruct session); cross-doc tension with disconnect-flow.md line 389 flagged in body"
  - claim: "Stock server never auto-respawns — 62/62 ObjCreateTeam (0x03) are client-initiated relays"
    address: null
    confidence: high
    note: "battle trace: 3 initial + 59 respawn relays; self-destruct trace: 0 server-originated 0x03"
companions:
  - docs/protocol/pythonevent-wire-format.md
  - docs/protocol/cf16-explosion-encoding.md
  - docs/protocol/objnotfound-requestobj-enterset-wire-format.md
  - docs/protocol/tgobjptrevent-class.md
  - docs/networking/disconnect-flow.md
  - docs/gameplay/self-destruct-pipeline.md
  - docs/gameplay/damage-system.md
  - docs/protocol/collision-effect-protocol.md
---

> [docs](../README.md) / [networking](README.md) / ship-death-lifecycle.md

# Ship Death Lifecycle in Multiplayer

> [!NOTE]
> **v5 partial pass — zero wire/sequence corrections.** All 3 handler addresses (0x006a1240 ObjectExplodingHandler, 0x006a0080 Explosion, 0x006a01e0 DestroyObject), the dual-branch SP/MP logic, the "NoMe" group routing, the guaranteed-delivery flag, the 9.5s lifetime carry, and the 6-TGSubsystemEvent 4+2 split all survive byte-level cross-check. **2 minor cosmetic/speculation fixes** plus 1 clarification:
>
> - **C1 (cosmetic)**: "TGSubsystemEvent" class name is fabricated — string returns zero matches in stbc.exe. Factory 0x101 IS the TGEvent base class itself (per leaf #13). Renamed throughout to "TGEvent (factory 0x101) ET_ADD_TO_REPAIR_LIST". The 6-count, 4+2 split, and subsystem identity table are unchanged.
> - **C2 (speculation)**: The Python `ObjectKilledHandler` IS registered for `App.ET_OBJECT_EXPLODING` in every `Mission*.py` (e.g., `Mission1.py:195`). The prior "scoring handler may not be registered" hypothesis is FALSE. Root cause is in the Python early-return paths (`g_bGameOver`, `IsPlayerShip`, dest type) or firing-player ID handling — requires Python investigation, not binary RE.
> - **Clar-1**: Handler at 0x006a1240 was bare code in Ghidra DB (auto-analyzer hadn't promoted — same pattern as ~13 other dispatched handlers per networking foundation #1). Function CREATED in Ghidra this pass (283 bytes, name: `MultiplayerGame_ObjectExplodingHandler`). Future passes will find it pre-defined.

## Overview

When a ship is destroyed in Bridge Commander multiplayer, the stock dedicated server
uses a specific sequence of network messages. Two critical findings:

1. **DestroyObject (0x14) is NOT used** for any ship death (combat or self-destruct)
2. **The server NEVER auto-respawns** — ALL respawns are client-initiated

## Key Finding: Stock Server Never Auto-Respawns [v5-validated 2026-05-28]

**All ObjCreateTeam (0x03) messages in the battle trace are client-initiated relays,
NOT server-originated spawns.** The stock server uses star topology: client messages
are relayed to all other peers. When a client sends ObjCreateTeam after picking a new
ship, the server relays it to all other clients. There are zero server-originated
ObjCreateTeam messages after any death type.

Evidence from battle trace (33.5 min, 3 players, 59 deaths):
- 62 ObjCreateTeam total: 3 initial spawns + 59 respawns
- All 62 are client-initiated (client sends 0x03, server relays to other peers)
- Zero server-originated ObjCreateTeam after any death

Evidence from self-destruct trace (6 deaths, 3 ship types):
- Zero server-originated ObjCreateTeam after any self-destruct
- Client returns to ship selection, picks new ship, sends 0x03

## Death Sequence [v5-validated 2026-05-28]

### 1. Ship HP reaches 0

The damage pipeline (collision, weapon, or explosion path) reduces hull condition to 0.
The engine posts `ET_OBJECT_EXPLODING` (0x0080004E) to the event system.

### 2. ObjectExplodingHandler sends PythonEvent + Explosion

`MultiplayerGame_ObjectExplodingHandler` at `0x006a1240` catches `ET_OBJECT_EXPLODING`.
The handler is registered via `FUN_006da130` (EventManager AddHandler) at `FUN_0069efe0`
(registration block at `0x006a1c0-0x006a1cf` pushes the string
`"MultiplayerGame :: ObjectExplodingHandler"` at `0x0095a054` and handler addr `0x006a1240`).

The handler branches on `DAT_0097fa8a` (IsMultiplayer flag, byte read at `0x006a124e`):

**MP branch (the relay path):**
- Allocates 0x40-byte TGMessage via `TGAlloc(s_UNKNOWN, 0x40)` at `0x006a12c0`-`0x006a12d4`
  (factory dispatch at `0x00718010`)
- Writes opcode `0x06` (PythonEvent) byte to payload at `0x006a127f`
  (`MOV byte ptr [ESP+0x3c], 0x6`)
- Serializes the event polymorphically via vtable+0x34 (`WriteToStream`) at `0x006a12b1`
  — same vtable slot as TGCharEvent/TGObjPtrEvent/TGEvent base
- Sets guaranteed-delivery flag at `0x006a12fb` (`MOV byte ptr [ESI+0x3a], 0x1`)
- Sends to relay group `"NoMe"` (`DAT_008e5528`) via `SendTGMessageToGroup` at
  `0x006a12f4`/`0x006a12ff` (`CALL 0x006b4de0`)

The wire frame carries factory `0x8129` (ObjectExplodingEvent — vtable `0x0088A178`,
ctor `0x0043F8B0` per pythonevent-wire-format leaf #14), with source = killer's
connection ID and dest = dying ship object reference, plus `lifetime` (explosion
duration, 9.5s for stock).

**SP branch (not used in dedicated server, but documented for completeness):**
- Casts `event+0xc` (objectRef) to a ship via `CastToShipClass` at `0x006a1326`
  (`FUN_005ab670`, IsA `0x8008` per leaf #18)
- Writes `event+0x2c` (lifetime) to `ship+0x14c` (HP slot — FLT_MAX undamaged sentinel
  per leaf #18) at `0x006a1332`/`0x006a1335` (`FLD [ESI+0x2c]; FSTP [EAX+0x14c]`)
- Triggers visual effects via `FUN_005ac250` at `0x006a133d` (loads `"Effects"` and
  `"ObjectExploding"` strings)

For combat kills, the engine **also** sends Explosion (opcode `0x29`) which carries:
- Object ID (the dying ship)
- Impact position (compressed Vec4)
- Damage amount (CompressedFloat16 — see cf16-explosion-encoding leaf #21)
- Explosion radius (CompressedFloat16)

For self-destruct, Explosion (`0x29`) is NOT sent — only ObjectExplodingEvent.

### 3. Client returns to ship selection and respawns

After the 9.5-second explosion animation, the client returns to the ship selection
screen. The **client** picks a new ship and sends ObjCreateTeam (`0x03`). The server
relays this to all other clients via `MpgameHandleObjCreate` (`0x0069f620`). The
server does NOT initiate the respawn.

### 4. DestroyObject (0x14) is NOT sent for ship death

**Zero** DestroyObject (`0x14`) packets were observed across 59 combat deaths and
6 self-destruct deaths. The handler exists at `FUN_006A01E0` (binary-confirmed —
skip opcode, ReadInt(objID), `TGSceneGraph__GetObjectByID`, if `obj+0x20` NULL
invoke `vtable[0]` dtor; else forward to parent) but is not invoked for MP ship deaths.

DestroyObject may be reserved for:
- Non-ship object cleanup (torpedoes, projectiles)
- Player disconnect cleanup (removing the ship when a player leaves)
- Single-player object destruction

> [!IMPORTANT]
> **Cross-doc tension [2026-05-28]**: `docs/networking/disconnect-flow.md` (currently
> ~line 389) says `"0x14 DestroyObject: Observed for ship destruction (combat kills)"`.
> The 33.5-min battle trace cited here shows 0/59 combat deaths use opcode `0x14`.
> The `0x14` IS used for disconnect-triggered cleanup (per disconnect-flow lines
> 44/206/214/520) but NOT for combat death. The disconnect-flow v5 validation in
> progress should resolve this — the binary truth is on this doc's side per the
> battle trace evidence. (Cross-doc edit deferred — see family-close batch.)

## SCORE_CHANGE Anomaly [v5-correction 2026-05-28]

In the collision test trace (28s, 2 players, 1 collision kill), a SCORE_CHANGE (`0x36`)
was sent for the kill.

In the battle trace (33.5 min, 3 players, 59 weapon kills), **zero** SCORE_CHANGE
messages were observed. This suggests:
- Collision kills correctly trigger SCORE_CHANGE
- Weapon kills do NOT trigger SCORE_CHANGE on stock dedicated servers (CLAUDE.md
  known issue)

**Root cause unknown — the Python `ObjectKilledHandler` IS registered** for
`App.ET_OBJECT_EXPLODING` in every `Mission*.py` (e.g., `Mission1.py:195`:
`AddBroadcastPythonFuncHandler(App.ET_OBJECT_EXPLODING, pMission, "ObjectKilledHandler")`;
same pattern in Mission2/3/5). The handler fires on every death event including
weapon kills. Investigation should focus on the Python scoring logic's early-return
paths:
- `g_bGameOver != 0`
- `pShip.IsPlayerShip() == 0`
- non-Ship dest object

…or on firing-player ID handling for weapon paths (the killer's connection ID may
be 0/sentinel for some weapon paths but populated for collision). **Requires
Python investigation, not binary RE.** See OQ1.

The prior "scoring handler may not be registered for weapon-path destruction events"
hypothesis is **falsified** by the Python source — strike that line of reasoning.

## Packet Counts from Stock Traces

### Collision Test (28s, 2 players)
| Opcode | Name | Count |
|--------|------|-------|
| 0x29 | Explosion | 1 |
| 0x03 | ObjCreateTeam | 1 (client-initiated relay) |
| 0x14 | DestroyObject | 0 |
| 0x36 | SCORE_CHANGE | 1 |

### Battle of Valentine's Day (33.5 min, 3 players, 59 deaths)
| Opcode | Name | Count |
|--------|------|-------|
| 0x29 | Explosion | 59 |
| 0x03 | ObjCreateTeam | 62 (3 initial + 59 client-initiated respawn relays) |
| 0x14 | DestroyObject | 0 |
| 0x36 | SCORE_CHANGE | 0 |

The 3 extra ObjCreateTeam vs Explosion correspond to initial ship spawns at game start.
All 62 are client-initiated messages relayed through the server's star topology.

## Self-Destruct vs Combat Death [v5-validated 2026-05-28]

Self-destruct and combat kills follow **different** network message sequences on the stock
dedicated server. Verified by comparing stock traces: a self-destruct test session and the
33.5-minute battle session with 59 combat kills.

### Combat Kills

```
Ship HP -> 0 (weapon/collision/explosion damage)
  -> ObjectExplodingEvent (0x06, factory 0x8129)
     source=killer_ship, dest=dying_ship, lifetime=9.5s
  -> Explosion (0x29): position, damage, radius
  -> SCORE_CHANGE (0x36): kill + death credited (collision kills only; weapon kills
     do NOT fire on stock — see SCORE_CHANGE Anomaly above)
  -> Client returns to ship selection, sends ObjCreateTeam (0x03)
```

Battle trace counts: 59 Explosion (`0x29`), 62 ObjCreateTeam (`0x03`, all client relays),
0 DestroyObject (`0x14`).

### Self-Destruct (Opcode 0x13)

```
Client sends HostMsg (0x13, 1 byte)
  -> ObjectExplodingEvent (0x06, factory 0x8129)
     source=NULL (0x00000000), dest=dying_ship, lifetime=9.5s
  -> SCORE_CHANGE (0x36): death counted, no kill credit
  -> 6x TGEvent (factory 0x101) ET_ADD_TO_REPAIR_LIST
  -> 9.5 seconds: explosion animation, StateUpdates continue
  -> Client returns to ship selection (spawn menu)
  -> Client sends ObjCreateTeam (0x03) when player picks new ship
```

**Key differences from combat death:**
- **NO Explosion (`0x29`)** — only ObjectExplodingEvent triggers the animation
- **NO DestroyObject (`0x14`)** — ship exists as wreckage during explosion
- `source=NULL` in ObjectExplodingEvent (no attacker)
- Death counted but no kill credit awarded
- 6 TGEvent (factory `0x101`) ET_ADD_TO_REPAIR_LIST messages for primary subsystems

**Common between both:**
- **NO server-initiated respawn** — client picks a new ship and sends ObjCreateTeam
- **NO DestroyObject (`0x14`)** — ship is never explicitly destroyed

## Self-Destruct Repair-Event Detail (Stock) [v5-validated 2026-05-28]

Stock self-destruct sends exactly **6 ET_ADD_TO_REPAIR_LIST events** (event ID
`0x008000DF`, factory `0x0101`). These route damaged subsystems TO the
RepairSubsystem for crew auto-repair queuing.

> [!NOTE]
> **Factory 0x0101 is the TGEvent base class itself** (vtable `0x00895FF4`,
> ctor `FUN_006d5c00`) — per tgobjptrevent leaf #13. The prior nomenclature
> "TGSubsystemEvent" was fabricated; the string returns zero matches in stbc.exe.
> These are bare TGEvent objects carrying `event_type=0x008000DF` with two object
> refs (source = affected subsystem, dest = RepairSubsystem). The wire data is
> unchanged — only the class name was wrong.

### 4 Immediate (with ObjectExplodingEvent):
| source_obj | dest_obj | Subsystem |
|------------|----------|-----------|
| PowerReactor obj | RepairSubsystem obj | Reactor -> Repair |
| ShieldGenerator obj | RepairSubsystem obj | Shields -> Repair |
| PhaserController obj | RepairSubsystem obj | Phaser -> Repair |
| PulseWeapon obj | RepairSubsystem obj | Pulse Weapon -> Repair |

### 2 Late (at T+9.5s, during debris collision phase):
| source_obj | dest_obj | Subsystem |
|------------|----------|-----------|
| PoweredSubsystem obj | RepairSubsystem obj | EPS -> Repair |
| RepairSubsystem obj | RepairSubsystem obj | Repair -> Repair |

Stock only sends repair events for **primary subsystems** (6 total), NOT for every
individual phaser bank and torpedo tube. This is significant for implementations that
iterate all subsystems — sending 18-25 events (one per subsystem) overflows the reliable
retransmit queue.

## TGFactory Routing for the 0x06 Send Path (Cross-Doc Context)

The MP-branch send pattern in `MultiplayerGame_ObjectExplodingHandler` is the
**canonical 0x06 PythonEvent send path** (leaf #14 pythonevent pattern):
1. Allocate 0x40-byte TGMessage via `TGAlloc(s_UNKNOWN, 0x40)`
2. Set opcode `0x06` byte at start of payload (`[ESP+0x3c] = 0x6`)
3. Call vtable+0x34 (`WriteToStream`) on the event polymorphically
4. Copy buffered serialization into TGMessage payload starting at offset +1
5. Send to `"NoMe"` relay group with guaranteed-delivery flag (`msg+0x3a = 1`)

The same code shape appears in:
- `HostEventHandler` (`FUN_006A1150`)
- `SetPhaserLevelHandler` (`FUN_006A1970`)
- Start/stop firing, subsystem status, repair handlers (`FUN_0069FDA0`)

All produce wire-identical `0x06` frames with different event class payloads
(TGEvent, TGCharEvent, TGObjPtrEvent, ObjectExplodingEvent, etc.).

## OpenBC Implications

1. **SP vs MP branch is purely conditional on `DAT_0097fa8a`.** OpenBC server runs
   as host (IsMultiplayer=1), so it always takes the relay branch. The SP-path
   `ship+0x14c = lifetime` write is NOT needed in a dedicated server (the server's
   host-ship is a dummy; clients receive `0x06` and apply their own local death
   animation).

2. **Server-side death authority.** The dedicated server is responsible for
   emitting ObjectExplodingEvent when HP reaches 0 server-side (assuming
   server-side damage authority). This happens via the damage pipeline
   (collision/weapon/explosion → `ShipDeathHandler` at `0x005AFEA0` per
   `self-destruct-pipeline.md`) which posts `ET_OBJECT_EXPLODING`. The local
   handler chain catches it and emits opcode `0x06`.

3. **No DestroyObject (`0x14`) for ship death.** Verified by trace evidence
   (0/59 in battle, 0/6 in self-destruct). The handler EXISTS at `0x006a01e0`
   (binary-confirmed dtor invocation) but is reserved for non-ship-death cleanup.

4. **Client-initiated respawn.** Server should NEVER spontaneously send
   ObjCreateTeam (`0x03`) after death. Wait for client to pick a new ship and
   send `0x03`; relay it. (OpenBC PR#34 self-destruct fix already addresses this.)

5. **The 9.5-second lifetime field.** Carried in `event+0x2c` and written to
   `ship+0x14c` in the SP branch. The constant-source location (where 9.5f is
   set on the event before posting) is OQ2 below — important for OpenBC fidelity
   to client animation timing.

## Key Functions

| Address | Name | Role |
|---------|------|------|
| 0x006A1240 | MultiplayerGame_ObjectExplodingHandler | Dual-branch SP/MP for `ET_OBJECT_EXPLODING`; MP serializes opcode `0x06` PythonEvent to "NoMe" with guaranteed flag (CREATED this pass) |
| 0x006A0080 | Handler_Explosion_0x29 | Receives Explosion opcode on client; reads CV4 pos + 2x CF16; calls ExplosionDamage ctor |
| 0x006A01E0 | Handler_DestroyObject_0x14 | NOT used for MP ship deaths; vtable[0] dtor invocation |
| 0x0069F620 | MpgameHandleObjCreate | Receives ObjCreate (`0x02`) / ObjCreateTeam (`0x03`) respawn on client; relays via star topology |
| 0x005AB670 | CastToShipClass | IsA `0x8008`; used by SP branch to cast `event+0xc` to ship |
| 0x005AC250 | FUN_005ac250 (visual-effects loader) | SP-only; loads "Effects" + "ObjectExploding" strings |
| 0x005AFEA0 | ShipDeathHandler | Damage pipeline → posts ET_OBJECT_EXPLODING (per self-destruct-pipeline) |
| 0x006B4DE0 | TGWinsockNetwork_SendTGMessageToGroup | MP branch send dispatch |
| 0x00717B70 / 0x00718010 | TGAlloc / factory dispatch | TGMessage allocation pair |
| 0x006DA130 | EventManager AddHandler | Registers `MultiplayerGame_ObjectExplodingHandler` via FUN_0069efe0 |

## Key Globals

| Address | Name | What |
|---------|------|------|
| 0x0097FA78 | TGWinsockNetwork singleton | ECX target for SendTGMessageToGroup |
| 0x0097FA8A | IsMultiplayer (byte) | Drives SP/MP branch at `0x006a124e` |
| 0x008E5528 | s_NoMe | Relay-to-all-peers-except-self group name |
| 0x008D858C | s_UNKNOWN | TGAlloc class-name tag |
| 0x0095A054 | s_MultiplayerGame__ObjectExplodingHandler | Handler registration display string |

## Open Questions

- **OQ1**: Why does the Python `ObjectKilledHandler` not produce SCORE_CHANGE
  for weapon kills? Handler IS registered for `ET_OBJECT_EXPLODING` in every
  `Mission*.py` — needs Python script analysis of early-return paths
  (`g_bGameOver`, `IsPlayerShip()`, dest type) or firing-player ID handling
  for weapon paths. Requires Python investigation, not binary RE.

- **OQ2**: Where is `event+0x2c` (lifetime) set to `9.5f`? `ShipDeathHandler`
  at `0x005AFEA0` likely constructs the ObjectExplodingEvent and sets lifetime.
  The `9.5f` constant should be findable as a `.rdata` float or immediate
  — worth a one-pass check to confirm. Important for OpenBC fidelity to
  client-side animation timing.

- **OQ3**: Event field layout in SP handler vs wire layout. This handler reads
  `event+0xc` as object ref and `event+0x2c` as lifetime. Per pythonevent-wire-format
  leaf #14, ObjectExplodingEvent has source/dest at `+0x6C/+0x70` for the
  wire-serialized view. Is there an engine "transient" event view (with different
  offsets) vs the wire-serialized view? Worth a follow-up investigation —
  meaningful semantic-vs-wire layout question.

## Related Documents

- [pythonevent-wire-format.md](../protocol/pythonevent-wire-format.md) — ObjectExplodingEvent (factory `0x8129`) wire format and class layout (leaf #14)
- [cf16-explosion-encoding.md](../protocol/cf16-explosion-encoding.md) — CompressedFloat16 encoding for damage/radius (leaf #21)
- [objnotfound-requestobj-enterset-wire-format.md](../protocol/objnotfound-requestobj-enterset-wire-format.md) — DamageableObject HP slot at `+0x14c` and FLT_MAX sentinel (leaf #18)
- [tgobjptrevent-class.md](../protocol/tgobjptrevent-class.md) — Factory ID conventions and "TGSubsystemEvent" fabrication finding (leaf #13)
- [collision-effect-protocol.md](../protocol/collision-effect-protocol.md) — Collision damage path (one input to the death pipeline)
- [damage-system.md](../gameplay/damage-system.md) — Complete damage pipeline (HP → 0 → ET_OBJECT_EXPLODING)
- [self-destruct-pipeline.md](../gameplay/self-destruct-pipeline.md) — Full self-destruct pipeline + stock vs OpenBC comparison; ShipDeathHandler at `0x005AFEA0`
- [disconnect-flow.md](disconnect-flow.md) — Player disconnect (`0x14` IS used here, but NOT for combat death — see cross-doc tension above)
