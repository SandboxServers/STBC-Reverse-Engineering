> [docs](README.md) / gamemode-system.md

---
title: Gamemode / Mission System
type: reference + explanation
audience: re-engineer
validated: 2026-05-29
methodology: FUNCTION_DOC_WORKFLOW_V5
binary:
  name: stbc.exe
  size: 6394712
  base: 0x00400000
status: verified
evidence:
  - claim: "ship+0x2E4 is NetPlayerID (network ID of owning player, 0 for AI). NOT team_id."
    address: 0x006A1AA0
    function: GetShipFromPlayerID
    completeness: high
    confidence: high
    note: "Iterator over DAT_0097E9C8 scene-set list; returns ship where (ship+0x2E4) == playerID arg. If +0x2E4 were team_id, lookup would only succeed at random — confirms +0x2E4 IS the playerID."
  - claim: "IsLocalPlayerShip checks (ship+0x2E4) != 0 on host (i.e. owned by any player)"
    address: 0x005AE140
    function: IsLocalPlayerShip
    completeness: medium
    confidence: high
    note: "AI ships keep +0x2E4 = 0; all player-owned ships (regardless of owner) pass — second-source confirmation that +0x2E4 == owning playerID, not a team byte."
  - claim: "ShipClass_GetNetPlayerID SWIG impl reads ship+0x2E4 (Python pShip.GetNetPlayerID())"
    address: 0x0060B8C0
    function: ShipClass_GetNetPlayerID
    completeness: medium
    confidence: high
    note: "Bytes `8B 82 E4 02 00 00` = MOV EAX, [EDX+0x2E4]. Mission1.py:556 binds this to the dying-player ID for scoring. CREATED this pass (SWIG accessor, never entered by analyzer)."
  - claim: "ship+0xEC is NetType (ship class/species enum). NOT team."
    address: 0x00607F40
    function: PhysicsObjectClass_GetNetType
    completeness: medium
    confidence: high
    note: "Bytes `8B 82 EC 00 00 00` = MOV EAX, [EDX+0xEC]. Mission2.py uses GetNetType() to pick a Modifier table row — species/class, not team."
  - claim: "App.MAX_MESSAGE_TYPES exposed to Python = 0x2B (43) — sentinel after the 42 real C++ message types"
    address: 0x00654F2C
    function: FUN_00654A00
    completeness: medium
    confidence: high
    note: "Bytes `c7 05 90 b4 94 00 2B 00 00 00` = MOV [0x0094B490], 0x2B. .rdata name string `\"MAX_MESSAGE_TYPES\"` at 0x00952CF8 is keyed to TYPE_ID 0x2B. CLIENT_READY_MESSAGE (0x2A) is the last real type. So MISSION_INIT = MAX+10 = 0x35."
  - claim: "C++ message-type table base at 0x0094B48C..0x0094B490 written by FUN_00654A00 (~1273-byte init function)"
    address: 0x0094B48C
    function: FUN_00654A00
    completeness: medium
    confidence: high
    note: "Builder function CREATED this pass. Writes 0x20-byte struct {name_ptr, type_id_int, ...} per entry. The MAX_MESSAGE_TYPES entry is written at code 0x00654F2C; the table itself is the read side."
  - claim: "MISSION_INIT_MESSAGE = 0x35 (MAX_MESSAGE_TYPES + 10) — host -> joining client"
    address: null
    function: null
    confidence: high
    note: "Python const: MissionShared.py:19. Wire-confirmed by stock-dedi trace payload `08 08 FF FF` matching MissionShared.py InitNetwork emit at line 366."
  - claim: "SCORE_CHANGE_MESSAGE = 0x36 (MAX_MESSAGE_TYPES + 11) — host -> 'NoMe' group on kill"
    address: null
    function: null
    confidence: high
    note: "Python const: MissionShared.py:20. Sent inside Mission1.py:653 ObjectKilledHandler. Sent to 'NoMe' string at 0x008E5528 (binary anchor)."
  - claim: "SCORE_MESSAGE = 0x37 (MAX_MESSAGE_TYPES + 12) — host -> joining client, one per existing player"
    address: null
    function: null
    confidence: high
    note: "Python const: MissionShared.py:21. Sent inside Mission1.py:432 (InitNetwork roster sync)."
  - claim: "END_GAME_MESSAGE = 0x38 (MAX_MESSAGE_TYPES + 13) — host -> broadcast"
    address: null
    function: null
    confidence: high
    note: "Python const: MissionShared.py:22. Sent by MissionShared.EndGame() at line 332."
  - claim: "RESTART_GAME_MESSAGE = 0x39 (MAX_MESSAGE_TYPES + 14) — host -> broadcast"
    address: null
    function: null
    confidence: high
    note: "Python const: MissionShared.py:23. Sent by RestartGameHandler at Mission1.py:932."
  - claim: "SCORE_INIT_MESSAGE = 0x3F (MAX_MESSAGE_TYPES + 20) — Mission2 TEAM_DM variant of SCORE_MESSAGE"
    address: null
    function: null
    confidence: high
    note: "Python const: Mission2.py:30. Adds trailing team byte after the 4 score longs."
  - claim: "TEAM_SCORE_MESSAGE = 0x40 (MAX_MESSAGE_TYPES + 21) — Mission2 TEAM_DM team-aggregate"
    address: null
    function: null
    confidence: high
    note: "Python const: Mission2.py:31."
  - claim: "TEAM_MESSAGE = 0x41 (MAX_MESSAGE_TYPES + 22) — Mission2 TEAM_DM team assignment"
    address: null
    function: null
    confidence: high
    note: "Python const: Mission2.py:32. Host re-forwards client team-change messages to 'NoMe' (Mission2.py:413)."
  - claim: "ET_KILL_GAME (0x008000E9) is NEVER raised from C++ — only from Python via PostEvent SWIG"
    address: null
    function: null
    confidence: high
    note: "Negative claim. Searched stbc.exe for `c7 ?? E9 00 80 00` MOV-immediate patterns of the event ID; zero hits. The only consumer is KillGameHandler at 0x006A2640 (registered for the event)."
  - claim: "KillGameHandler stub at 0x006A2640 calls MultiplayerGame vtable[+0x68] (10-byte body)"
    address: 0x006A2640
    function: KillGameHandler
    completeness: medium
    confidence: high
    note: "10-byte stub CREATED this pass: `8B 01 6A 00 FF 50 68 C2 04 00` = MOV EAX, [ECX]; PUSH 0; CALL [EAX+0x68]; RET 4. Standard event-handler stub that delegates to its registered MultiplayerGame instance via vtable."
  - claim: "MultiplayerGame vtable[+0x68] (slot 26) = ET_KILL_GAME body at 0x0069EF70 (UI/game-state teardown)"
    address: 0x0069EF70
    function: MultiplayerGame__OnKillGame
    completeness: medium
    confidence: high
    note: "Body CREATED this pass. Reads DAT_009878cc (TopWindow); if non-NULL, FUN_0050d550(0) tears down UI. Then FUN_004062b0(event) engine cleanup, FUN_00445ed0() game-state reset, FUN_0050e1b0(8) returns PlayWindow and sets [+0xb1] = 1 (game-ended flag). Vtable slot read at 0x0088B480+0x68."
  - claim: "ObjectExplodingEvent factory ID = 0x8129 (TGStreamedObject factory)"
    address: 0x00616990
    function: ObjectExplodingEvent_Ctor
    completeness: medium
    confidence: high
    note: "Set/Get firingPlayerID and lifetime accessors anchored at this site. Wire-side: opcode 0x06 PythonEvent dispatches factory IDs via TGFactory; 0x8129 deserializes back to ObjectExplodingEvent with the layout below."
  - claim: "ObjectExplodingEvent layout: +0x28 = firingPlayerID (int32), +0x2C = lifetime (float)"
    address: 0x00616990
    function: ObjectExplodingEvent_SetFiringPlayerID
    completeness: medium
    confidence: high
    note: "Set FP at 0x00616990 (`MOV [ECX+0x28], arg`), Get FP at 0x00616A10. Set Lifetime at 0x00616A70 (`MOV [ECX+0x2C], arg`), Get Lifetime at 0x00616AF0 (`D9 58 2C` = FSTP [EAX+0x2C])."
  - claim: "FUN_005AFEA0 HOST branch writes (killerShip+0x2E4) into event+0x28 (firingPlayerID)"
    address: 0x005AFEA0
    function: FUN_005AFEA0
    completeness: medium
    confidence: high
    note: "Explode-and-post helper. HOST gate via DAT_0097fa89; reads killer arg's +0x2E4 (now confirmed as NetPlayerID) and stores into the constructed ObjectExplodingEvent's firingPlayerID slot. Confirms SCORE_CHANGE attribution path is architecturally correct."
  - claim: "Collision damage cascade: CollisionEffectHandler -> Ship__HostCollisionEffectHandler -> FUN_005AFD70 -> FUN_005AF4A0 -> FUN_005AFEA0 (with killerShip arg)"
    address: 0x005AFAD0
    function: Ship__HostCollisionEffectHandler
    completeness: medium
    confidence: high
    note: "FUN_005AFD70 at 0x005AFD70 (called from 0x005AFAD0), FUN_005AF4A0 at 0x005AF4A0 (called from 0x005AFD70). FUN_005AF4A0 calls FUN_005AFEA0(killer) on lethal damage at 0x005AF5D0..005AF5DC. killer propagates via EBP through 0x005AFE26..005AFE44."
  - claim: "ShipClass::HandleHit body (CREATED this pass) is the damage callback entry"
    address: 0x005AF4A0
    function: ShipClass__HandleHit
    completeness: medium
    confidence: high
    note: "Function body CREATED this pass during validation. Calls FUN_005AFEA0 on lethal hits with killer carried through arg."
  - claim: "UtopiaModule+0x40 = friendlyFireTolerance / MaxFriendlyFire (SAME float field; Setter named 'SetMax', Getter 'GetTolerance')"
    address: 0x005EAC10
    function: UtopiaModule__GetFriendlyFireTolerance
    completeness: medium
    confidence: high
    note: "Getter at 0x005EAC10 bytes `D9 42 40` = FLD [EDX+0x40]. SetMax at 0x005EAC80 bytes `D9 58 40` = FSTP [EAX+0x40]. UtopiaModule singleton at 0x0097FA00."
  - claim: "UtopiaModule+0x44 = currentFriendlyFire (float, accumulates damage points)"
    address: 0x005EAD00
    function: UtopiaModule__GetCurrentFriendlyFire
    completeness: medium
    confidence: high
    note: "Getter 0x005EAD00 bytes `D9 42 44`; Setter 0x005EAD3C bytes `D9 58 44`."
  - claim: "UtopiaModule+0x48 = friendlyFireWarningPoints (float, configurable threshold)"
    address: 0x005EAD90
    function: UtopiaModule__SetFriendlyFireWarningPoints
    completeness: medium
    confidence: high
    note: "Setter 0x005EAD90 bytes `D9 58 48`; also mirrors to global at 0x0095DD20 (bytes `D9 5C 20 DD 95 00`). Mission1.Initialize calls SetFriendlyFireWarningPoints(100) so default = 100.0f."
  - claim: "TEAM_FEDERATION / TEAM_KLINGON / TEAM_ROMULAN strings at 0x0090f2dc..0x0090f338 are AI behavior-tree group keys, NOT multiplayer team identifiers"
    address: 0x0090F2DC
    function: null
    confidence: high
    note: "Negative claim. These strings are consumed by Python AI scripts via Mission.GetEnemyGroup() / Mission.GetFriendGroup() to look up ship-NAME group memberships (e.g. 'USS_Defiant' is in 'Federation' group). No C++ code maps any of these strings to a numeric team byte on a ship. Mission2 team membership lives in Python g_kTeamDictionary keyed by playerID; teams have no on-ship storage."
  - claim: "Python scoring dictionaries are pure Python state — there is no C++ scoring storage"
    address: null
    function: null
    confidence: high
    note: "Negative claim. SWIG bindings for Game_GetScore/Game_GetRating/Game_GetKills exist but are read-only single-player career accessors. NO Game_SetScore, NO C++ field for per-player MP score on ship or MultiplayerGame. All MP scoring lives in module globals inside Mission*.py: g_kKillsDictionary, g_kDeathsDictionary, g_kScoresDictionary, g_kDamageDictionary."
  - claim: "Mission1 score formula: score = (shieldDamageDone + hullDamageDone) / 10.0 per attacker"
    address: null
    function: null
    confidence: high
    note: "Python anchor: Mission1.py:617 — `iScore = int((fShieldDmg + fHullDmg) / 10.0)`. Applied per attacker entry in g_kDamageDictionary[shipObjID]."
  - claim: "'NoMe' relay group string at 0x008E5528"
    address: 0x008E5528
    function: null
    confidence: high
    note: 'Bytes `4E 6F 4D 65 00` = "NoMe". Multiplayer group: all peers except sender. Receiver of SCORE_CHANGE_MESSAGE forwards; used by Python SendTGMessageToGroup("NoMe", ...).'
  - claim: "'Forward' relay group string at 0x008D94A0"
    address: 0x008D94A0
    function: null
    confidence: high
    note: 'Bytes `46 6F 72 77 61 72 64 00` = "Forward". Multiplayer group: all peers including sender. Used by C++ generic event-forward path FUN_0069FDA0.'
  - claim: "NewPlayerInGameHandler at 0x006A1E70 calls mission_script.InitNetwork(playerID) on host"
    address: 0x006A1E70
    function: NewPlayerInGameHandler
    completeness: medium
    confidence: high
    note: "Opcode 0x2A handler. Posts ET_NEW_PLAYER_IN_GAME (0x008000F1), then calls Python via FUN_006F8AB0 binding s_InitNetwork_0095A354. Then iterates DAT_0097E9C8 (scene-sets) and sends 0x02 ObjCreate / 0x03 ObjCreateTeam / 0x29 Explosion for replication. Finally adds new player to 'NoMe' and 'Forward' groups."
  - claim: "Settings handler (opcode 0x00) at 0x00504D30 stores mission name in VarManager('Multiplayer', 'Mission', mapName)"
    address: 0x00504D30
    function: SettingsHandler
    completeness: medium
    confidence: high
  - claim: "GameInit handler (opcode 0x01) at 0x00504F10 creates MultiplayerGame and triggers AI.Setup.GameInit Python preload"
    address: 0x00504F10
    function: GameInitHandler
    completeness: medium
    confidence: high
  - claim: "TGNetwork.SendTGMessageToGroup SWIG signature 'OOO'"
    address: 0x0093848C
    function: null
    confidence: high
    note: "Bytes spelling SWIG arg-type signature 'OOO\\0' (3 Python objects: group_name, message, sender_token)."
  - claim: "TGNetwork.SendTGMessage SWIG signature 'OiO|i'"
    address: 0x0093846C
    function: null
    confidence: high
    note: "Bytes spelling SWIG arg-type signature: connID (int), message (object), optional priority."
companions:
  - docs/protocol/python-messages.md
  - docs/protocol/game-opcodes.md
  - docs/protocol/pythonevent-wire-format.md
  - docs/gameplay/self-destruct-pipeline.md
  - docs/gameplay/damage-system.md
  - docs/networking/ship-death-lifecycle.md
supersedes: []
---

# Gamemode / Mission System

> [!NOTE]
> **Two-layer architecture**: ALL multiplayer scoring/team logic is **Python-driven** (per-mission `Mission*.py` scripts). C++ provides only field storage (ship+0x2E4 NetPlayerID, ship+0xEC NetType, UtopiaModule+0x40..+0x48 friendly-fire), wire transport (opcodes 0x35-0x39 + Mission2's 0x3F/0x40/0x41), and a single end-game UI-teardown vtable slot. No C++ scoring storage; no C++ team field; no `Game_SetScore` SWIG. The `ET_KILL_GAME (0x008000E9)` event is NEVER raised from C++ — only from Python via `PostEvent` SWIG.
>
> **KEY CORRECTION**: `ship+0x2E4` is **NetPlayerID** (network ID of owning player, 0 for AI), NOT `team_id` as previously documented in `objcreate-serialization.md`, `game-opcodes.md`, the `MpgameHandleObjCreate` Ghidra plate, and the `RequestObjHandler` Ghidra plate. Cross-doc reconciliation is queued for the family-close batch. See [§ ship+0x2E4 disambiguation](#ship0x2e4-disambiguation-netplayerid-not-team_id) below.

## Table of contents

1. [Architecture overview](#1-architecture-overview)
2. [C++ field storage](#2-c-field-storage)
3. [Python scoring data structures](#3-python-scoring-data-structures)
4. [Score formula](#4-score-formula-mission1py617)
5. [Wire formats — byte by byte](#5-wire-formats--byte-by-byte)
6. [End-game flow](#6-end-game-flow)
7. [Restart flow](#7-restart-flow)
8. [Mission lifecycle](#8-mission-lifecycle)
9. [Mission2 TEAM_DM](#9-mission2-team_dm)
10. [The weapon-kill SCORE_CHANGE mystery](#10-the-weapon-kill-score_change-mystery)
11. [TEAM_FEDERATION/KLINGON/ROMULAN — negative claim](#11-team_federationklingonromulan--negative-claim)
12. [OpenBC implementation guidance](#12-openbc-implementation-guidance)
13. [Open questions](#13-open-questions)

---

## 1. Architecture overview

The system is cleanly separated into two layers:

- **C++ layer** — mission-agnostic. Owns network transport (opcodes 0x35-0x39 + 0x3F/0x40/0x41), object lifecycle, event dispatch, the UtopiaModule friendly-fire counters, and the lone end-game UI-teardown vtable slot. The C++ does not know or care what gamemode is running.
- **Python layer** — gamemode-specific. Each `Multiplayer/Episode/Mission*/Mission*.py` script defines its own scoring dictionaries, victory conditions, team rules, and end-game wire emissions.

C++ enters Python at three known call sites:

1. `TG_CallPythonFunction("AI.Setup", "GameInit")` — fired from `GameInitHandler` at `0x00504F10` (opcode 0x01). Preloads AI scripts.
2. `ReadPythonVariable("Multiplayer.MissionMenusShared", "g_iPlayerLimit")` — read from C++ via `FUN_006F8650` to size MultiplayerGame's player slot table.
3. `TG_CallPythonFunction(missionScript, "InitNetwork", connID, "i")` — fired from `NewPlayerInGameHandler` at `0x006A1E70` (opcode 0x2A). The mission script then emits MISSION_INIT + per-player SCORE_MESSAGE to the joining client.

The MultiplayerGame instance is the C++ root of all gameplay state. Its vtable lives at `0x0088B480`. Slot `+0x68` (slot 26) holds `MultiplayerGame::OnKillGame` at `0x0069EF70` — the one C++ slot that participates in gamemode end-game flow, and it does nothing but tear down UI.

### ship+0x2E4 disambiguation — NetPlayerID, not team_id

This is load-bearing for every protocol doc that touches kill credit. `ship+0x2E4` was previously labeled "team_id" because ObjCreateTeam (opcode 0x03) writes `(byte)(ship+0x2E4)` as its second wire byte. That label is **wrong**. Three independent binary anchors confirm `ship+0x2E4 = NetPlayerID`:

| Anchor | Address | What it proves |
|---|---|---|
| `GetShipFromPlayerID` | `0x006A1AA0` | Walks `DAT_0097E9C8` scene-set table and returns the ship where `ship+0x2E4 == playerID`. If `+0x2E4` were a team byte, this lookup would only succeed at random. |
| `IsLocalPlayerShip` (host branch) | `0x005AE140` | Returns `ship+0x2E4 != 0`. All player-owned ships (any owner) pass; AI ships have `+0x2E4 == 0`. The field is "owning playerID, or 0 for AI". |
| `ShipClass_GetNetPlayerID` SWIG impl | `0x0060B8C0` | Bytes `8B 82 E4 02 00 00` (`MOV EAX, [EDX+0x2E4]`). Python `pShip.GetNetPlayerID()` returns `ship+0x2E4`. Mission1.py:556 binds this to the dying player's ID for SCORE_CHANGE emit. |

ObjCreateTeam wire byte 2 truncates `(int)playerID` to one byte. This works only because stock-dedi NetIDs are small slot indices (0..15). A 32-bit NetID would lose data through that cast — relevant to OpenBC if NetID widens. The "team" in "ObjCreateTeam" was always a misnomer: opcode 0x03 means "create with owner playerID byte", and opcode 0x02 means "create without owner byte (server/AI-owned)".

Adjacent confirmation: `ship+0xEC = NetType` (ship class/species enum: Federation/Klingon/Romulan/etc.). Read by `PhysicsObjectClass_GetNetType` at `0x00607F40` via `MOV EAX, [EDX+0xEC]`. Mission2.py uses `pShip.GetNetType()` to pick a damage-modifier table row — species, not team.

---

## 2. C++ field storage

The complete catalog of C++ fields that participate in gamemode state. Outside this list, gamemode state lives in Python.

### Per-ship

| Field | Offset | Type | Reader / Writer | Notes |
|---|---|---|---|---|
| NetPlayerID | `ship+0x2E4` | int32 | Get @ `0x0060B8C0` `ShipClass_GetNetPlayerID` SWIG | 0 = AI / unowned, else NetID of owning player. Used by `GetShipFromPlayerID` (`0x006A1AA0`) for kill-credit lookup. |
| NetType | `ship+0xEC` | int32 | Get @ `0x00607F40` `PhysicsObjectClass_GetNetType` SWIG | Species enum (Federation/Klingon/Romulan/...). Used by Mission2.py Modifier table indexing. |

### UtopiaModule (singleton @ `0x0097FA00`) — friendly-fire counters

| Field | Offset | Type | Reader / Writer | Notes |
|---|---|---|---|---|
| friendlyFireTolerance / MaxFriendlyFire | `+0x40` | float | Get @ `0x005EAC10` (`D9 42 40`); SetMax @ `0x005EAC80` (`D9 58 40`) | **Same memory**. Reader is `GetTolerance`, writer is `SetMax`. Configurable cap. |
| currentFriendlyFire | `+0x44` | float | Get @ `0x005EAD00` (`D9 42 44`); Set @ `0x005EAD3C` (`D9 58 44`) | Accumulator. When exceeded, behavior depends on Python configuration. |
| friendlyFireWarningPoints | `+0x48` | float | Set @ `0x005EAD90` (`D9 58 48`); also mirrors to `DAT_0095DD20` (`D9 5C 20 DD 95 00`) | Warning threshold. Mission1.Initialize calls `SetFriendlyFireWarningPoints(100)`. |

The actual gate that decides "this damage counts as friendly vs hostile" depends on `Mission.GetFriendGroup()` membership (Python). The C++ side reads/writes these floats but does not own the policy. The damage gate location in the C++ damage chain is an open question — see § 13.

### MultiplayerGame (instance — vtable at `0x0088B480`)

| Slot | Offset | Function | Role |
|---|---|---|---|
| 26 | `+0x68` | `MultiplayerGame__OnKillGame` @ `0x0069EF70` | Handler body for `ET_KILL_GAME (0x008000E9)`. UI teardown only — does no scoring or wire emission. CREATED this pass. |

`KillGameHandler` stub at `0x006A2640` (10 bytes, CREATED this pass): `MOV EAX, [ECX]; PUSH 0; CALL [EAX+0x68]; RET 4`. Registered against `ET_KILL_GAME`; delegates to vtable slot 26 above. The event itself is **never raised from C++** — only via Python `PostEvent` SWIG, and the binary contains zero `c7 ?? E9 00 80 00` MOV-immediate patterns for the event ID.

---

## 3. Python scoring data structures

Mission scripts hold all per-game scoring state as module globals. There is no on-ship score field and no SWIG `Game_SetScore`.

### Free-for-all (Mission1)

| Dict | Key | Value |
|---|---|---|
| `g_kKillsDictionary` | `playerID` (int) | kill count (int) |
| `g_kDeathsDictionary` | `playerID` (int) | death count (int) |
| `g_kScoresDictionary` | `playerID` (int) | score (int) |
| `g_kDamageDictionary` | `shipObjID` (int) | `{attackerPlayerID: [fShieldDmg, fHullDmg]}` |

`g_kDamageDictionary` accumulates per-victim, per-attacker damage. When a ship dies, the entry drives kill credit and SCORE_CHANGE emission for every attacker who contributed (Mission1.py:617).

### Team Deathmatch (Mission2)

Mission2 inherits Mission1's four dicts and adds three team-level dicts. Team membership is **pure Python state** keyed by playerID — no ship field encodes a team.

| Dict | Key | Value |
|---|---|---|
| `g_kTeamDictionary` | `playerID` (int) | `teamNum` (int: 0 or 1; `INVALID_TEAM = 255`) |
| `g_kTeamScoreDictionary` | `teamNum` (int) | team score (int) |
| `g_kTeamKillsDictionary` | `teamNum` (int) | team kill count (int) |

Mission2.py:413 confirms host re-forwards inbound `TEAM_MESSAGE (0x41)` to `"NoMe"` so the team-change propagates to all other peers.

---

## 4. Score formula (Mission1.py:617)

Per-attacker score award on kill:

```python
iScore = int((fShieldDmg + fHullDmg) / 10.0)
```

This runs once per attacker entry in `g_kDamageDictionary[shipObjID]`. Total shield damage plus total hull damage accumulated against the dying ship, divided by ten, truncated to int. Class modifier (Mission1.py:490+498) scales `fDamage` per shooter→target species pair *before* it lands in the dictionary, so the modifier is already baked in by the time the formula runs.

---

## 5. Wire formats — byte by byte

All gamemode messages use `TGMessage` with `SetGuaranteed(1)` (reliable). The first byte is always the opcode. All payload integers are little-endian.

The C++ message-type table at `0x0094B48C..0x0094B490` is built by `FUN_00654A00` (CREATED this pass). The sentinel entry `MAX_MESSAGE_TYPES` (`.rdata` name string at `0x00952CF8`) is written with TYPE_ID `0x2B` at code `0x00654F2C` (`c7 05 90 b4 94 00 2B 00 00 00`). The 42 real C++ message types end at `CLIENT_READY_MESSAGE = 0x2A`. Python adds gamemode opcodes as `MAX + offset`:

| Wire | Const | Source | Formula |
|---|---|---|---|
| `0x35` | `MISSION_INIT_MESSAGE` | MissionShared.py:19 | `MAX_MESSAGE_TYPES + 10` |
| `0x36` | `SCORE_CHANGE_MESSAGE` | MissionShared.py:20 | `MAX_MESSAGE_TYPES + 11` |
| `0x37` | `SCORE_MESSAGE` | MissionShared.py:21 | `MAX_MESSAGE_TYPES + 12` |
| `0x38` | `END_GAME_MESSAGE` | MissionShared.py:22 | `MAX_MESSAGE_TYPES + 13` |
| `0x39` | `RESTART_GAME_MESSAGE` | MissionShared.py:23 | `MAX_MESSAGE_TYPES + 14` |
| `0x3F` | `SCORE_INIT_MESSAGE` | Mission2.py:30 (TEAM_DM) | `MAX_MESSAGE_TYPES + 20` |
| `0x40` | `TEAM_SCORE_MESSAGE` | Mission2.py:31 (TEAM_DM) | `MAX_MESSAGE_TYPES + 21` |
| `0x41` | `TEAM_MESSAGE` | Mission2.py:32 (TEAM_DM) | `MAX_MESSAGE_TYPES + 22` |

### 5.1 `0x35` MISSION_INIT_MESSAGE — host → joining client

Emitted from `Mission*.InitNetwork(iToID)` (Mission1.py:337). Sent to the joining player only.

```
[u8:0x35]
[u8:playerLimit]            g_iPlayerLimit (1..16, default 8)
[u8:systemSpecies]          g_iSystem (SpeciesToSystem index)
[u8:timeLimitOrFF]          -1 -> 0xFF (no limit); else minutes 0..254
   IF timeLimitOrFF != 0xFF:
     [i32:endTimeAbsolute]  absolute game-clock when round ends = g_iTimeLeft + int(GetGameTime())
[u8:fragLimitOrFF]          -1 -> 0xFF (no limit); else 0..254
```

Size: 4 bytes (no time limit) or 8 bytes (with time limit). Stock-trace observation `08 08 FF FF` = 8 players, system=8, no time limit, no frag limit.

### 5.2 `0x36` SCORE_CHANGE_MESSAGE — host → `"NoMe"` group, on kill

Emitted from Mission1.py:653 inside `ObjectKilledHandler` after a host-detected kill. Note: sent to `"NoMe"` via `pNetwork.SendTGMessageToGroup("NoMe", pMessage)`, **not** broadcast.

```
[u8:0x36]
[i32:firingPlayerID]                 0 if no kill credit (AI / self-destruct), else NetID of killer
   IF firingPlayerID != 0:
     [i32:firingPlayerKills]         killer's NEW kill count (post-increment)
     [i32:firingPlayerScore]         killer's NEW score (post-update)
[i32:killedPlayerID]                 NetID of player who died
[i32:killedPlayerDeaths]             victim's NEW death count
[u8:scoreUpdateCount]                N = number of other contributors with score deltas
N times:
  [i32:contributorPlayerID]          (excludes killedPlayer and firingPlayer)
  [i32:contributorScore]             contributor's NEW score
```

Minimum 10 bytes (firingPlayerID=0 path). Variable.

> [!NOTE]
> **Stock-bug**: Mission1.py:687-688 — if `iScoreUpdateCount > actual contributors`, the loop writes `WriteLong(0)` filler values **but not the matching playerID**, so the message stream self-corrupts. Receiver (Mission1.py:295-301) reads `iScoreCount × (playerID, score)` pairs; the filler-only path desynchronizes. Triggers only on damage-dict mutation during emit; practically benign in stock. Worth not repeating in OpenBC.

### 5.3 `0x37` SCORE_MESSAGE — host → joining client (one per existing player)

Emitted from Mission1.py:432 inside `InitNetwork`, after MISSION_INIT. Sent once per known player as a full roster sync. Stock-trace shows N copies after each player-join handshake.

```
[u8:0x37]
[i32:playerID]
[i32:kills]
[i32:deaths]
[i32:score]
```

Size: 17 bytes fixed.

### 5.4 `0x38` END_GAME_MESSAGE — host → broadcast

Emitted from `MissionShared.EndGame(iReason)` (MissionShared.py:332).

```
[u8:0x38]
[i32:reason]                END_* enum (see table below)
```

Size: 5 bytes fixed.

End reason enumeration (matches the six host emission paths in § 6):

| Value | Const | Source |
|---|---|---|
| 0 | `END_ITS_JUST_OVER` | Manual UI abort |
| 1 | `END_TIME_UP` | Time limit expired |
| 2 | `END_NUM_FRAGS_REACHED` | Frag count hit |
| 3 | `END_SCORE_LIMIT_REACHED` | Score limit hit |
| 4 | `END_STARBASE_DEAD` | Mission5 starbase destroyed |
| 5 | `END_BORG_DEAD` | Mission7 (cut) Borg destroyed |
| 6 | `END_ENTERPRISE_DEAD` | Mission9 (cut) Enterprise destroyed |

### 5.5 `0x39` RESTART_GAME_MESSAGE — host → broadcast

Emitted from `RestartGameHandler` (Mission1.py:932). Triggered by Python event `ET_RESTART_GAME = MakeEpisodeEventType(52)` — typically the "Play Again" button on the end-game dialog.

```
[u8:0x39]                   no payload
```

Size: 1 byte fixed.

### 5.6 `0x3F` SCORE_INIT_MESSAGE — host → joining client (Mission2 only)

Extended `SCORE_MESSAGE` with trailing team byte. Replaces 0x37 in TEAM_DM mode.

```
[u8:0x3F]
[i32:playerID]
[i32:kills]
[i32:deaths]
[i32:score]
[u8:teamID]                 0 or 1 (255 = INVALID_TEAM)
```

Size: 18 bytes fixed. Anchored at Mission2.py:356.

### 5.7 `0x40` TEAM_SCORE_MESSAGE — host → all (Mission2 only)

Team-aggregate score sync.

```
[u8:0x40]
[u8:teamID]                 0 or 1
[i32:teamKills]
[i32:teamScore]
```

Size: 10 bytes fixed.

### 5.8 `0x41` TEAM_MESSAGE — client → host, then host → `"NoMe"` (Mission2 only)

Client emits when its operator picks a team. Host updates `g_kTeamDictionary[playerID]` and re-forwards to `"NoMe"` so all other peers learn the assignment.

```
[u8:0x41]
[i32:playerID]
[u8:teamID]                 0 or 1
```

Size: 6 bytes fixed. Host re-forward anchored at Mission2.py:413.

---

## 6. End-game flow

### 6.1 Six host emission paths

Each path ends with a call to `MissionShared.EndGame(iReason)` (MissionShared.py:332) which constructs the `0x38` message and broadcasts it.

1. **Frag/score limit** (Mission1 / Mission2 / Mission3) — Mission script's `CheckFragLimit()` runs at the tail of `ObjectKilledHandler`:
   - If `g_iUseScoreLimit`: `g_kScoresDictionary[anyPlayerID] >= g_iFragLimit * 10000` (Mission1.py:729).
   - Else: `g_kKillsDictionary[anyPlayerID] >= g_iFragLimit`.
   - Emits `EndGame(END_SCORE_LIMIT_REACHED)` or `EndGame(END_NUM_FRAGS_REACHED)`.

2. **Time limit** (MissionShared) — `CreateTimeLeftTimer(iTimeLeft)` runs at 1 Hz, decrements `g_iTimeLeft`. When it reaches zero AND `IsHost()`: `EndGame(END_TIME_UP)`.

3. **Mission5 starbase** — per-mission `ObjectKilledHandler` detects starbase death, emits `EndGame(END_STARBASE_DEAD)`.

4. **Mission7 Borg** (cut) — emits `EndGame(END_BORG_DEAD)`. Referenced in MissionShared.py:253; mission script not shipped.

5. **Mission9 Enterprise** (cut) — emits `EndGame(END_ENTERPRISE_DEAD)`. Referenced in MissionShared.py:264; mission script not shipped.

6. **Manual UI abort** — `EndGame(END_ITS_JUST_OVER)` from an end-game dialog button.

### 6.2 What `EndGame()` does on the host

After broadcasting `0x38`:

- `pMultGame.SetReadyForNewPlayers(0)` — disable joins for the rest of the round (MissionShared.py:345).

### 6.3 What `0x38` does on all peers (receiver)

MissionShared.py:220 receiver:

- `g_bGameOver = 1`.
- `ClearShips()` — destroys all player ships + torps, scrubs the target menu.
- Per-mission: sets `g_bStarbaseDead` / `g_bBorgDead` / `g_bEnterpriseDead` on the mission script.
- `MissionMenusShared.DoEndGameDialog(1, pReason, 1)` — show end-game dialog.

### 6.4 The C++ side — `ET_KILL_GAME (0x008000E9)`

The C++ `KillGameHandler` stub at `0x006A2640` (CREATED this pass, 10 bytes) is registered against `ET_KILL_GAME`. It dispatches to `MultiplayerGame` vtable slot 26 — `MultiplayerGame__OnKillGame` at `0x0069EF70` (CREATED this pass):

```pseudo
OnKillGame(event):
  if (DAT_009878cc /* TopWindow */ != 0) FUN_0050d550(0);   // tear down UI
  FUN_004062b0(event);                                       // engine cleanup
  FUN_00445ed0();                                            // game-state reset
  PlayWindow = FUN_0050e1b0(8);                              // returns 0x009878cc-ish
  PlayWindow[+0xb1] = 1;                                     // mark game-ended
```

This is the C++ "tear down current game" path. **It is distinct from Python END_GAME_MESSAGE** — `ET_KILL_GAME` is **never raised from C++**, only via Python `PostEvent` SWIG. Negative claim anchored on absence of `c7 ?? E9 00 80 00` MOV-immediates of the event ID anywhere in the binary.

---

## 7. Restart flow

`RESTART_GAME_MESSAGE (0x39)` triggers `RestartGame()` on all peers (Mission1.py:940):

- Zero all four scoring dictionaries (`Kills`, `Deaths`, `Scores`, `Damage`) — keys preserved, values reset to 0.
- For Mission2: zero `g_kTeamScoreDictionary` and `g_kTeamKillsDictionary`. `g_kTeamDictionary` is preserved (team assignments stick across restart).
- `g_bGameOver = 0`.
- `ClearShips()` — destroys all player ships and torpedoes.
- Reset `g_iTimeLeft = g_iTimeLimit * 60` if time-limit mode.
- Hide chat window.
- `ShowShipSelectScreen()` — force respawn UI on every peer.

Host triggers via `pMission.AddPythonFuncHandlerForInstance(MissionShared.ET_RESTART_GAME, RestartGameHandler)`. The handler then sends `0x39` to all and runs `RestartGame()` locally.

### State teardown — preserved vs cleared

| State | After END_GAME (`0x38`) | After RESTART (`0x39`) | After `Mission.Terminate` |
|---|---|---|---|
| `g_kKillsDictionary` | preserved (end-game dialog shows scores) | zeroed | deleted (Python `del`) |
| `g_kScoresDictionary` | preserved | zeroed | deleted |
| `g_kDeathsDictionary` | preserved | zeroed | deleted |
| `g_kDamageDictionary` | preserved | zeroed | deleted |
| `g_kTeamDictionary` (Mission2) | preserved | preserved | deleted |
| `ReadyForNewPlayers` | host: 0 | not changed | reset in `MultiplayerGame_Ctor` |
| `g_bGameOver` | host: 1, peers: 1 | host: 0, peers: 0 | 0 |
| Player ships | destroyed | destroyed | already destroyed |

---

## 8. Mission lifecycle

### 8.1 Host startup (after settings + lobby)

1. Host receives its own `0x01 GameInit` (sent locally by `GameInitHandler` at `0x00504F10`):
   - `TG_CallPythonFunction("AI.Setup", "GameInit")` — preloads AI scripts.
   - Constructs `MultiplayerGame` (`FUN_0069e590`):
     - Initializes 16 player slots (`0x18` bytes each at `+0x74`).
     - Creates `"NoMe"` group (`0x008E5528`) — all peers except sender.
     - Creates `"Forward"` group (`0x008D94A0`) — all peers including sender.
     - Registers 26 C++ event handlers (8 host-only, including `ObjectKilledHandler` registration if `IsHost()`).
   - Reads `g_iPlayerLimit` from Python via `FUN_006F8650`; writes to `mpgame+0x1FC` (max-players field).

2. Loads `Multiplayer.Episode.Episode → Mission1.Mission1` (or whichever mission VarManager holds).

3. Mission script `Initialize(pMission)` runs:
   - `MissionShared.Initialize(pMission)` — loads TGL databases, sets up `WarpHandler` / `ScanHandler` / `SoundDoneHandler`, turns on friendly-fire warnings via `App.g_kUtopiaModule.SetFriendlyFireWarningPoints(100)`.
   - Mission-specific menu builders (e.g. `Mission1Menus.BuildMission1Menus()` for host).
   - Registers event handlers — `ET_OBJECT_EXPLODING → ObjectKilledHandler` (host only), `ET_WEAPON_HIT → DamageEventHandler` (host only), `ET_NETWORK_MESSAGE_EVENT → ProcessMessageHandler` (all peers).

### 8.2 Per-player join (host side)

1. Host receives `0x2A NewPlayerInGame` from joining client.
2. `NewPlayerInGameHandler` (`0x006A1E70`):
   - Posts local `ET_NEW_PLAYER_IN_GAME (0x008000F1)` event with the playerID.
   - Calls Python `mission_script.InitNetwork(playerID)` via `FUN_006F8AB0` with name-binding `s_InitNetwork_0095A354`.
3. Mission's `InitNetwork(iToID)` (Mission1.py:337) sends to the joining player only:
   - `0x35 MISSION_INIT_MESSAGE` once (playerLimit, system, time/frag limits).
   - `0x37 SCORE_MESSAGE` N times — one per known player (full roster sync).
   - In Mission2: `0x3F SCORE_INIT_MESSAGE` (with team byte) instead of `0x37`, plus `0x40 TEAM_SCORE_MESSAGE` for each team.
4. `NewPlayerInGameHandler` then iterates `DAT_0097E9C8` (scene-set table) and for each living game object:
   - Sends `0x02 ObjCreate` (non-team) or `0x03 ObjCreateTeam` (with NetPlayerID byte for the owning player).
   - For each exploding/cloaked object: sends `0x29 Explosion`.
5. Adds the new player to `"NoMe"` and `"Forward"` groups via binary-search-insert.

Victory conditions are **100% Python-evaluated**. The C++ side knows the limit strings via the SWIG bindings but does not check them; only Python `CheckFragLimit()` runs after each `ObjectKilledHandler`.

---

## 9. Mission2 TEAM_DM

Mission2 extends the FFA model with Python-managed team membership. The C++ binary has zero awareness of teams (see § 1 disambiguation and § 11 negative claim).

| Aspect | Mission1 (FFA) | Mission2 (TEAM_DM) |
|---|---|---|
| Team storage | n/a | `g_kTeamDictionary[playerID] = teamNum` (Python module global) |
| Team join wire | n/a | `0x41 TEAM_MESSAGE` (6 bytes): client → host, host re-forwards to `"NoMe"` |
| Roster sync wire | `0x37 SCORE_MESSAGE` (17 bytes) | `0x3F SCORE_INIT_MESSAGE` (18 bytes, +1 team byte) |
| Team aggregate wire | n/a | `0x40 TEAM_SCORE_MESSAGE` (10 bytes) |
| Friendly fire | always foe (FFA) | same-team damage stored as **negative** in `g_kDamageDictionary` — reduces attacker score on kill |
| Kill credit gate | always credits | only credits if killer.teamID != victim.teamID |
| Team kill counter | n/a | `g_kTeamKillsDictionary[killerTeam] += 1` (also gated on cross-team) |

Mission3 is identical to Mission2 except its team labels come from a localization DB ("Federation Team Name" / "NonFed Team Name") instead of generic "Team N". Team assignment is still player-chosen via `0x41 TEAM_MESSAGE`, not species-derived. Mission3 is NOT auto-assignment by ship class — the faction names are display strings only.

The host-relay path for `0x41` is the only documented one (Mission2.py:413: `if IsHost(): SendTGMessageToGroup("NoMe", pMessage)`). On a dedicated host, this assumes `MultiplayerGame_Cast(App.Game_GetCurrentGame())` returns a non-NULL — see § 13.

---

## 10. The weapon-kill SCORE_CHANGE mystery

Stock-dedi observed behavior: collision kills and self-destruct kills emit `0x36 SCORE_CHANGE_MESSAGE` correctly; **weapon kills do not**. Valentine 33.5min trace: 0 of 55 weapon kills produced `0x36`, while 4 of 4 self-destructs did. The architectural cause is a host-side dispatch gap, not a wire-format bug.

### 10.1 Why collision kills work

Collision damage runs through the host's local damage cascade:

1. Client A's ship physically collides with client B's ship.
2. Client A sends `0x15 CollisionEffect` to host.
3. Host `CollisionEffectHandler` (`0x006A2470`, v5-validated) re-posts locally as `ET_HOST_OBJECT_COLLISION (0x008000FC)` after distance gates pass.
4. Host `ShipClass::HostCollisionEffectHandler` (`0x005AFAD0`) computes damage locally and calls `FUN_005AFD70 → FUN_005AF4A0 → FUN_005AFEA0(killerShip)`.
5. `FUN_005AFEA0` HOST branch: `event[+0x28] = killerShip+0x2E4` (= killer's NetPlayerID). `PostEvent` fires `ET_OBJECT_EXPLODING` locally on host.
6. Host Python `ObjectKilledHandler` runs → `0x36 SCORE_CHANGE_MESSAGE` is sent.

### 10.2 Why self-destruct works

1. Client sends `0x13 HostMsg` (self-destruct request, 1-byte).
2. Host `HostMsgHandler` (`0x006A01B0`) runs `FUN_005AF5F0(targetShip) → FUN_005AF4A0 → FUN_005AFEA0(killer=NULL)`.
3. `FUN_005AFEA0` with NULL killer: `event[+0x28] = 0`. `PostEvent` fires `ET_OBJECT_EXPLODING`.
4. Host Python `ObjectKilledHandler` runs with `iFiringPlayerID == 0` → no kill credit, but DEATH is recorded (`g_kDeathsDictionary[victimID] += 1`) → `0x36 SCORE_CHANGE` IS sent with `firingPlayerID = 0`.

### 10.3 Why weapon kills don't trigger SCORE_CHANGE

Weapon damage does **not** run through the host's local damage cascade because the host's representation of the victim doesn't take weapon damage:

1. Client A fires phaser/torpedo → sends `0x1A BeamFire` or `0x19 TorpedoFire` to host.
2. Host's `FUN_0069FBB0` (BeamFire receiver) relays to `"Forward"` group AND spawns a beam entity locally via `FUN_005762B0` with `beam+0x14C = firingPlayerID`.
3. **But**: the host's local copy of B's ship doesn't take damage from this beam. The actual damage calculation runs on **B's client**, where B's local ship + the beam coexist in physics.
4. The host's representation of B's ship gets its health from inbound `0x1C StateUpdate` packets (flags=0x20 SUB carrying subsystem health). These are STATE WRITES via `Ship::ReadStateUpdate` (`0x005B21C0`), **NOT** calls into `ApplyDamageToSubsystem`.
5. So `FUN_005AFEA0` (Explode) **never fires on host for weapon kills** — the host's local damage pipeline isn't invoked.
6. When B's ship dies on B's machine, B's local `FUN_005AFEA0` fires with `killer = weapon_entity` (factory 0x8009 type). CLIENT branch: reads `event[+0x28] = weapon+0x14C` = A's NetPlayerID. `ObjectExplodingHandler` MP branch sends opcode `0x06 PythonEvent` (factory `0x8129 ObjectExplodingEvent`) to `"NoMe"`.
7. Host receives `0x06`, runs `MpgameHandlePythonEvent` (`0x0069F880`), deserializes the event, calls `EventManager::PostEvent` to re-post locally with `firingPlayerID` correctly carried in `event+0x28`.
8. At this point Python `ObjectKilledHandler` *should* run — but the Valentine trace shows it doesn't progress to the SCORE_CHANGE send.

### 10.4 Two unresolved hypotheses

- **H1 — Object reference race**: The re-posted event's `pEvent.GetDestination()` may return NULL or non-`CT_SHIP` because `FUN_006F13C0 (ResolveObjectRefs)` runs before the StateUpdate that re-anchors the victim ship reference. Mission1.py:548 gate `if pKilledObject.IsTypeOf(App.CT_SHIP)` would silently early-exit, no SCORE_CHANGE.
- **H2 — Dispatch ordering**: The `0x06` event may be dispatched in MultiplayerGame's RECEIVE phase before Mission1's `ObjectKilledHandler` is connected to the local event manager — i.e. event posting happens earlier in the frame than Python handler dispatch on the dedicated server.

Resolution requires live trace with Python entry log on `ObjectKilledHandler`. If not called for weapon kills, gate is H2 (dispatch race). If called but exits early, gate is H1 (`IsPlayerShip()` / `GetDestination()`).

---

## 11. TEAM_FEDERATION/KLINGON/ROMULAN — negative claim

The strings `TEAM_FEDERATION`, `TEAM_KLINGON`, `TEAM_ROMULAN` (and siblings) live in `.rdata` at `0x0090F2DC..0x0090F338`. These are **AI behavior-tree group keys**, NOT multiplayer team identifiers.

- They are passed to Python via SWIG as string constants.
- Python code consumes them as group-name keys in `Mission.GetEnemyGroup("Federation")` / `Mission.GetFriendGroup(...)` — the values returned are sets of ship-NAME strings (e.g. `"USS_Defiant"`, `"IKS_Hegh'ta"`).
- No C++ code maps any of these strings to a numeric team byte on a ship.
- Mission2 team membership lives in Python `g_kTeamDictionary[playerID] = teamNum` and is wired via `0x41 TEAM_MESSAGE`.

This is a common misconception worth pre-empting because the string names suggest C++ team awareness. There is none.

---

## 12. OpenBC implementation guidance

The clean-room OpenBC spec lives at `../OpenBC/docs/gamemode-system.md`. This doc anchors the behavioral specification; the OpenBC spec captures the implementation requirements.

Key implementation notes that fall out of this RE:

1. **Don't replicate the weapon-kill SCORE_CHANGE bug.** Server-side OpenBC should track damage attribution as `0x06` ObjectExplodingEvent (factory `0x8129`) arrives, use `event.firingPlayerID` (event+0x28) directly as kill credit, use `event.destination` as victim, and emit `0x36 SCORE_CHANGE` for ALL deaths regardless of source type (collision, weapon, self-destruct, environmental).
2. **ship+0x2E4 is NetPlayerID, not team_id.** Treat ObjCreateTeam's wire byte 2 as the NetID (one-byte truncated). OpenBC's NetID type should not exceed 8 bits unless the wire format also widens.
3. **Don't add C++ scoring storage.** Stay Python-driven; the four-dict model + per-mission script is the entire architectural surface.
4. **Don't repeat the Mission1.py:687-688 filler bug** — write playerID+score pairs as pairs, never values alone.
5. **The `0x36` destination is `"NoMe"`, not broadcast.** The killer doesn't receive their own SCORE_CHANGE — they update locally from the kill event. (OpenBC must replicate or document deviation.)

---

## 13. Open questions

1. **Weapon-kill `0x36` absence (§ 10.4)**: H1 (object-ref race) vs H2 (dispatch-ordering race). Needs live stock-dedi run with Python entry log on `ObjectKilledHandler`. Until resolved, OpenBC implementation guidance § 12.1 takes the safer "always emit" path.

2. **Mission2 `0x41` host-relay on dedicated server**: Mission2.py:413 is anchored, but the relay assumes `MultiplayerGame_Cast(App.Game_GetCurrentGame())` returns non-NULL on a dedi. Needs dedi-mode validation — if the cast returns NULL, team-change messages would not propagate to peers.

3. **Friendly-fire damage gate location**: The UtopiaModule counters at +0x40..+0x48 are anchored, and Python sets the warning threshold. But the C++ gate that decides "this damage counts as FF vs hostile" is presumably in the `FUN_005AF4A0` child chain — not yet RE'd. The gate probably reads `Mission.GetFriendGroup()` membership; binary anchor pending.

4. **C++ message-type table builder timing**: `FUN_00654A00` writes the `0x094B48C..0x094B490` table during init. Confirmed builder is `~1273` bytes and CREATED this pass. When in the boot sequence it runs (before/after `GameInitHandler`?) is not yet anchored.

5. **Mission5/6/7/9 special-objective end-game triggers**: only verified by string presence in MissionShared.py. Mission5 ships; Mission6/7/9 are cut. Binary anchoring for the cut variants is unavailable; for Mission5, per-mission `ObjectKilledHandler` anchor is pending.

6. **`MultiplayerGame_Cast`**: where exactly the cast lives and whether it tolerates a NULL global game pointer on dedi is needed to close OQ 2.

---

## Source memo

Evidence packet: [`.claude/agent-memory/game-archaeology-specialist/gamemode-system-validation-20260529.md`](../.claude/agent-memory/game-archaeology-specialist/gamemode-system-validation-20260529.md).
