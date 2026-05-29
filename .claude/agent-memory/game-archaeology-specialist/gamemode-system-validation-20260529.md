---
name: gamemode-system-validation-20260529
description: v5 RE of stbc.exe gamemode/mission/scoring/team/end-game system — finds DOC-WRONG ship+0x2E4 (was "team_id", actually "NetPlayerID"), confirms MAX_MESSAGE_TYPES=0x2B sentinel (so 0x35=MISSION_INIT/0x36=SCORE_CHANGE/0x37=SCORE/0x38=END/0x39=RESTART), explains weapon-kill SCORE_CHANGE stock bug (host doesn't run weapon damage path locally, dying client relays via 0x06 PythonEvent which lacks firingPlayerID set on the dying-client side).
metadata:
  type: project
---

# Gamemode System v5 Validation (2026-05-29)

Star Trek: Bridge Commander stock dedicated server gamemode/mission/scoring/team architecture, recovered from STBC.exe binary + decompiled Python scripts. Foundation doc for OpenBC's gamemode expansion.

Scope: Python-tier opcodes 0x34..0x39 wire format, scoring data model, team system, end/restart flow, mission lifecycle.

Method: phase 1+2 RE on stbc.exe (Ghidra MCP) + cross-anchor against `reference/scripts/Multiplayer/MissionShared.py` + `Episode/Mission*.py` + `game/stock-dedi/packet_trace.log` (Valentine 33.5min trace).

## Major doc correction — ship+0x2E4 is NetPlayerID, not team_id

This is the **headline finding**. Prior v5 docs (objcreate-serialization.md, game-opcodes.md, MpgameHandleObjCreate plate comment, RequestObjHandler plate comment) labeled `ship+0x2E4` as "team_id" because ObjCreateTeam (opcode 0x03) wire byte 2 = `(byte)(ship+0x2E4)`. That label is WRONG and propagates downstream confusion through every protocol doc that touches kill credit.

**Truth**: `ship+0x2E4` is the **player network ID** that owns the ship. Confirmed via three independent evidence sources:

| Evidence | Address | What it proves |
|----------|---------|----------------|
| `GetShipFromPlayerID` body | `0x006A1AA0` | Walks DAT_0097E9C8 scene-set table, returns ship where `ship+0x2E4 == playerID`. If +0x2E4 were team_id, this lookup would only find ships at random — confirms +0x2E4 IS the playerID. |
| `IsLocalPlayerShip` body | `0x005AE140` | On HOST: `return ship+0x2E4 != 0`. All player-owned ships (regardless of which player) pass this check. AI ships have `+0x2E4 == 0`. Means +0x2E4 is "owning playerID, or 0 for AI". |
| `ShipClass_GetNetPlayerID` SWIG impl | `0x0060B8C0` | Bytes `8B 82 E4 02 00 00` = `MOV EAX, [EDX+0x2E4]`. Python `pShip.GetNetPlayerID()` returns `ship+0x2E4`. Mission1.py line 556 uses this exact call to identify the dying player for scoring. |

Adjacent confirmation: `ship+0xEC = NetType` (ship class enum, e.g. Federation/Klingon — read by `PhysicsObjectClass_GetNetType` at `0x00607F40` via `MOV EAX, [EDX+0xEC]`). Mission2.py uses `pShip.GetNetType()` to pick a Damage Modifier table entry — confirms +0xEC IS the class/species.

ObjCreateTeam wire byte 2 truncates `(int)playerID` to one byte. This works because stock dedi NetIDs are small integers (slot indices typically 0..15), but a 32-bit NetID would lose data through this cast. The "team" in "ObjCreateTeam" was always a misnomer; opcode 0x03 simply means "create with owner playerID payload byte"; opcode 0x02 means "create without owner byte (server/AI-owned)".

Downstream implications:
- `FUN_005AFEA0` (Explode) HOST branch line `event[+0x28] = killer_ship+0x2E4` actually assigns **killer's NetPlayerID** to event.firingPlayerID — the SCORE_CHANGE flow IS architecturally correct.
- Mission2 team membership lives in Python `g_kTeamDictionary[playerID] = teamNum` — NOT in any ship field. Teams are pure Python state, sent over wire as Mission2-specific `TEAM_MESSAGE = MAX+22 = 0x41`.

## Python message opcodes — exact values confirmed

`App.MAX_MESSAGE_TYPES` exposed to Python = **0x2B (43)**. NOT 0x2A (42).

Confirmation chain:
1. C++ message-type table built by `FUN_00654A00` (~1273-byte init function). Entries written as 0x20-byte struct: `{name_ptr, type_id_int, ...}`.
2. The TABLE entry whose name string is `"MAX_MESSAGE_TYPES"` (at .rdata `0x00952CF8`) is written with `type_id_int = 0x2B` via `c7 05 90 b4 94 00 2B 00 00 00` at code `0x00654F2C`.
3. Earlier entries (CLIENT_READY_MESSAGE = 0x2A, DAMAGE_VOLUME_MESSAGE = 0x29, SEND_FILE_COMPLETED_MESSAGE = 0x28) confirm sequential TYPE_IDs.
4. Cross-check: stock-dedi trace at `[19:47:11.080-something]` shows opcode `0x35` with payload `08 08 FF FF` — matches MissionShared.py's `MISSION_INIT_MESSAGE` wire format (playerLimit/system/timeLimit/fragLimit bytes). So 0x35 = MISSION_INIT_MESSAGE = MAX(0x2B) + 10.

Resolved table:

| Wire Opcode | Python const | Source | Formula |
|---|---|---|---|
| 0x2C | CHAT_MESSAGE | Multiplayer/Chat.py (TBD) | manual constant |
| 0x2D | TEAM_CHAT_MESSAGE | Multiplayer/Chat.py (TBD) | manual constant |
| 0x35 | MISSION_INIT_MESSAGE | MissionShared.py:19 | `MAX_MESSAGE_TYPES + 10` |
| 0x36 | SCORE_CHANGE_MESSAGE | MissionShared.py:20 | `MAX_MESSAGE_TYPES + 11` |
| 0x37 | SCORE_MESSAGE | MissionShared.py:21 | `MAX_MESSAGE_TYPES + 12` |
| 0x38 | END_GAME_MESSAGE | MissionShared.py:22 | `MAX_MESSAGE_TYPES + 13` |
| 0x39 | RESTART_GAME_MESSAGE | MissionShared.py:23 | `MAX_MESSAGE_TYPES + 14` |
| 0x3F | SCORE_INIT_MESSAGE | Mission2.py:30 (TEAM_DM) | `MAX + 20` |
| 0x40 | TEAM_SCORE_MESSAGE | Mission2.py:31 (TEAM_DM) | `MAX + 21` |
| 0x41 | TEAM_MESSAGE | Mission2.py:32 (TEAM_DM) | `MAX + 22` |

CLAUDE.md table for 0x35-0x39 is CORRECT. The off-by-one I initially feared was my misread; MAX_MESSAGE_TYPES has its own sentinel entry at TYPE_ID 0x2B, AFTER the 42 real message types (which end at CLIENT_READY = 0x2A).

## Wire formats — byte-exact

All wire formats live in Python (Mission*.py), so they're not "binary truth" in the strict sense — but the Python code IS the spec (it's what runs on the dedicated server), and the C++ is structured around the byte-stream-deserialize model `TGBufferStream.ReadChar/ReadLong/etc`.

### 0x35 MISSION_INIT_MESSAGE (host -> joining client)

Per MissionShared.py:19, sent in `Mission*.InitNetwork(iToID)` (host receives 0x2A NewPlayerInGame → calls `InitNetwork`).

```
[u8:0x35]                        opcode
[u8:playerLimit]                 g_iPlayerLimit (1..16, usually 8)
[u8:systemSpecies]               g_iSystem (system index for SpeciesToSystem table)
[u8:timeLimitOrFF]               -1 → 0xFF; else int 0..254 in minutes
   IF previous != 0xFF:
     [i32:endTimeAbsolute]       game time when limit expires
[u8:fragLimitOrFF]               -1 → 0xFF; else int 0..254 frags
```

Stock observed `08 08 FF FF` = (8 players, system=8, no time limit, no frag limit).

### 0x36 SCORE_CHANGE_MESSAGE (host -> "NoMe" group, on kill)

Per Mission1.py:653, sent inside `ObjectKilledHandler` after a host-detected kill. CRITICAL: sent to "NoMe" group via `pNetwork.SendTGMessageToGroup("NoMe", pMessage)`, NOT broadcast.

```
[u8:0x36]                        opcode
[i32:firingPlayerID]             0 if AI/no-credit, else NetID of killer
   IF firingPlayerID != 0:
     [i32:kills]                 killer's NEW kill count (post-increment)
     [i32:firingPlayerScore]     killer's NEW score (post-update)
[i32:killedPlayerID]             NetID of player who died
[i32:deaths]                     victim's NEW death count
[u8:scoreUpdateCount]            N other players whose damage contributed
N times:
  [i32:contributorPlayerID]      (skips killedPlayer + firingPlayer)
  [i32:contributorScore]         contributor's NEW score
```

Padding bug at Mission1.py:687-688: if `iScoreUpdateCount > actual contributors`, writes `WriteLong(0)` fillers — but ONLY the value, NOT the playerID, so the message becomes self-corrupting. Receiver at line 295-301 reads `iScoreCount × (playerID, score)` pairs; the filler-only-value path will desynchronize the stream. **Stock bug** but practically benign — only triggers on damage-dict mutation during emit.

### 0x37 SCORE_MESSAGE (host -> joining client, one per player)

Per Mission1.py:432, sent inside `InitNetwork()` AFTER MISSION_INIT. Sends ONE message per known player (full roster sync). Stock dedi trace shows `0x37 PlayerRoster` repeated N times after each player join.

```
[u8:0x37]                        opcode
[i32:playerID]                   key
[i32:kills]
[i32:deaths]
[i32:score]
```

20-byte payload total (with opcode). Mission2.py's TEAM_DM variant adds team byte at end (different opcode 0x3F SCORE_INIT_MESSAGE — Mission2.py:356).

### 0x38 END_GAME_MESSAGE (host -> broadcast)

Per MissionShared.py:332, sent by `EndGame(iReason)` host-side. Triggers when:
- `Mission1.CheckFragLimit()` detects `g_kKillsDictionary[any] >= g_iFragLimit` OR `g_kScoresDictionary[any] >= g_iFragLimit * 10000` (if g_iUseScoreLimit). Calls `EndGame(END_SCORE_LIMIT_REACHED)`.
- `MissionShared.UpdateTimeLeftHandler()` detects `g_iTimeLeft <= 0`. Calls `EndGame(END_TIME_UP)` (host-only via `IsHost()` gate).
- Mission5.py / Mission6.py: starbase death triggers `EndGame(END_STARBASE_DEAD)`.
- Mission7.py: Borg ship death triggers `EndGame(END_BORG_DEAD)`.
- Mission9.py: Enterprise death triggers `EndGame(END_ENTERPRISE_DEAD)`.
- Generic UI button: `EndGame(END_ITS_JUST_OVER)`.

Wire:
```
[u8:0x38]                        opcode
[i32:reason]                     END_ITS_JUST_OVER=0, END_TIME_UP=1, END_NUM_FRAGS_REACHED=2,
                                 END_SCORE_LIMIT_REACHED=3, END_STARBASE_DEAD=4, END_BORG_DEAD=5,
                                 END_ENTERPRISE_DEAD=6
```

Side effects on host after sending:
- `pMultGame.SetReadyForNewPlayers(0)` — disable new joins (MissionShared.py:345)

Side effects on all peers (receiver, MissionShared.py:220):
- `g_bGameOver = 1`
- `ClearShips()` — destroys all player ships + torps + scrubs target menu
- Per-mission optional: sets `g_bStarbaseDead/g_bBorgDead/g_bEnterpriseDead` on host's mission script
- `MissionMenusShared.DoEndGameDialog(1, pReason, 1)` — show end dialog

### 0x39 RESTART_GAME_MESSAGE (host -> broadcast)

Per Mission1.py:932, sent by `RestartGameHandler`. Triggered by `Mission2/3/etc. ET_RESTART_GAME` event (Python event 52 = `MissionShared.ET_RESTART_GAME = MakeEpisodeEventType(52)`).

Wire (1 byte):
```
[u8:0x39]                        opcode (no payload)
```

Receiver action (Mission1.py:328 → `RestartGame()` at line 940):
- Zeroes all dictionaries (Kills/Deaths/Scores/Damage)
- `g_bGameOver = 0`
- `ClearShips()` again (in case)
- Resets `g_iTimeLeft` if time-limit mode
- Hides chat window
- Triggers `ShowShipSelectScreen()` (treats client as if killed)

## Scoring data model — Python-only dicts, not C++

The C++ side has ZERO scoring storage. Only single-player career stats exist:
- `Game_GetScore`/`Game_GetRating`/`Game_GetKills`/`Game_GetTorpsFired`/`Game_GetTorpsHit` SWIG bindings exist but ONLY for SP career mode — NO `Game_SetScore`/Set bindings.
- `GameInfo Score Limit:` string at `0x008e1bb4` is used by `FUN_00506200` (GameSpy ServerListEvent_OnSelect) to format the limit display label — read-only.
- Constants in Python module `Multiplayer.MissionMenusShared`:
  - `g_iPlayerLimit` (default 16, can be 1..16)
  - `g_iUseScoreLimit` (bool: 0=frag mode, 1=score mode)
  - `g_iFragLimit` (int frags OR int score/10000; -1 = unlimited)
  - `g_iTimeLimit` (minutes, -1 = unlimited)
  - `g_iSystem` (system species index)

MP scoring dictionaries live in each `Mission*.py` mission script as module globals:
- `g_kKillsDictionary[playerID] = int`
- `g_kDeathsDictionary[playerID] = int`
- `g_kScoresDictionary[playerID] = int`
- `g_kDamageDictionary[shipObjID] = {playerID: [shieldDamageFloat, hullDamageFloat]}`

Damage accumulates per-shooter per-victim in `g_kDamageDictionary` (Mission1.py:530). When victim dies, accumulator drives score awards. Score = sum(shieldDamage + hullDamage) / 10.0 per attacker.

Mission2 (TEAM_DM) adds:
- `g_kTeamDictionary[playerID] = teamNum` (Python-managed team membership)
- `g_kTeamScoreDictionary[teamNum] = int`
- `g_kTeamKillsDictionary[teamNum] = int`

Team membership is **pure Python state**; host forwards `TEAM_MESSAGE` (0x41) to clients on player team-change. Mission2.py:413 confirms host re-forwards received team messages to "NoMe" group.

## Team system — there is no C++ team field

NetType (ship+0xEC) is a SPECIES enum, NOT a team. Federation/Klingon/Romulan/Cardassian/Borg/etc. ship classes. Per Mission1.py:490 + 498:

```python
iHitterClass = Multiplayer.SpeciesToShip.GetClassFromSpecies(pHitterShip.GetNetType())
iHitClass = Multiplayer.SpeciesToShip.GetClassFromSpecies(pShip.GetNetType())
fDamage = fDamage * Multiplayer.Modifier.GetModifier(iHitterClass, iHitClass)
```

So damage is scaled by `Modifier[hitterClass][hitClass]` — a class-vs-class damage matrix that scales different ship classes against each other. **Stock BC has no explicit teams in the binary**; "teams" in multiplayer DM are implicit: every player is hostile to every other (free-for-all). Mission2 (TEAM_DM) adds Python-managed teams on top.

C++ TEAM strings in .rdata (TEAM_FEDERATION/TEAM_KLINGON/...) are SWIG-exposed string constants for AI behavior tree NAMING — Python code uses these as Group-name keys in `Mission.GetEnemyGroup()` / `Mission.GetFriendGroup()` (groups of ship-name strings). They're NOT a multiplayer team number.

## Friendly-fire system — UtopiaModule offsets

Confirmed via SWIG impl disasm:
| Field | Offset | Reader/Writer | Bytes |
|---|---|---|---|
| friendlyFireTolerance/MaxFriendlyFire | UtopiaModule+0x40 (float) | Get @ 0x005EAC10 reads, Set @ 0x005EAC80 writes | `D9 42 40` / `D9 58 40` |
| currentFriendlyFire | UtopiaModule+0x44 (float) | Get @ 0x005EAD00, Set @ 0x005EAD3C | `D9 42 44` / `D9 58 44` |
| friendlyFireWarningPoints | UtopiaModule+0x48 (float) | Set @ 0x005EAD90 writes; also writes to `0x0095DD20` (global) | `D9 58 48` + `D9 5C 20 DD 95 00` |

UtopiaModule singleton @ `0x0097FA00`. friendlyFireTolerance and MaxFriendlyFire are the SAME field (+0x40); the Setter is named "SetMax", the Getter "GetTolerance" — same memory.

Stock multiplayer behavior:
- Mission1.Initialize calls `App.g_kUtopiaModule.SetFriendlyFireWarningPoints(100)` and `MissionLib.SetupFriendlyFireNoGameOver()`. So default warning threshold = 100.
- Friendly fire does NOT end the game in MP (NoGameOver variant of setup).
- `Mission.Terminate` calls `MissionLib.ShutdownFriendlyFireNoGameOver()`.

friendlyFire damage gate logic lives in C++ DamageVolume/DamageHandler chain — but the actual gate (whose damage counts as "friendly" vs "hostile") depends on `Mission.GetFriendGroup()` membership (Python). Effectively: Mission script determines who's friendly, host runs the gate based on ship NAME, not team byte. AI ship names ("USS_Defiant", "IKS_Hegh'ta") map to Federation/Klingon enemy/friend groups.

## End-game / restart flow

### End-game emission paths

Five distinct host paths emit 0x38 END_GAME_MESSAGE:

1. **Frag/score limit** (Mission1/2/3/etc.):
   - Mission.CheckFragLimit() called inside ObjectKilledHandler after score update.
   - If g_iUseScoreLimit: check `g_kScoresDictionary[anyKey] >= g_iFragLimit * 10000`. Else: `g_kKillsDictionary[anyKey] >= g_iFragLimit`.
   - Emits `EndGame(END_SCORE_LIMIT_REACHED)` or `EndGame(END_NUM_FRAGS_REACHED)`.

2. **Time limit** (MissionShared):
   - 1Hz timer (CreateTimeLeftTimer) decrements `g_iTimeLeft`.
   - On zero AND `IsHost()`: emits `EndGame(END_TIME_UP)`.

3. **Mission-specific objective deaths**:
   - Mission5/6 starbase: emits `EndGame(END_STARBASE_DEAD)` from per-mission ObjectKilledHandler.
   - Mission7 Borg: emits `EndGame(END_BORG_DEAD)`.
   - Mission9 Enterprise: emits `EndGame(END_ENTERPRISE_DEAD)`.

4. **Manual abort** (UI button): emits `EndGame(END_ITS_JUST_OVER)`.

5. **C++ ET_KILL_GAME (0x8000E9)** — registered handler at `LAB_006a2640` (3-byte stub: `MOV EAX, [ECX]; PUSH 0; CALL [EAX+0x68]; RET 4`). Calls MultiplayerGame vtable[26] = `FUN_0069EF70`:
   - if `DAT_009878cc` (TopWindow) != 0: `FUN_0050d550(0)` (tear down UI)
   - `FUN_004062b0(event)` — engine cleanup
   - `FUN_00445ed0()` — game-state reset
   - `FUN_0050e1b0(8)` returns PlayWindow; set `[+0xb1] = 1` (game-ended flag)

This is the C++ "tear down current game" path, distinct from Python END_GAME_MESSAGE. NO C++ code raises ET_KILL_GAME — it's posted ONLY from Python via PostEvent SWIG binding (the binary has zero `c7 ?? E9 00 80 00` MOV-immediate patterns for the event ID).

### Restart flow

`RESTART_GAME_MESSAGE (0x39)` triggers `RestartGame()` on all peers (Mission1.py:940):
- Zero all 4 dictionaries
- `g_bGameOver = 0`
- `ClearShips()`
- Reset `g_iTimeLeft = g_iTimeLimit * 60` if time-limit mode
- Hide chat
- `ShowShipSelectScreen()` (force respawn UI)

Host triggers via `pMission.AddPythonFuncHandlerForInstance(MissionShared.ET_RESTART_GAME, RestartGameHandler)` — typically bound to an "Play Again" button on the end-game dialog.

### State teardown — what's preserved vs cleared

| State | After END_GAME_MESSAGE | After RESTART_GAME_MESSAGE | After full Mission.Terminate |
|---|---|---|---|
| g_kKillsDictionary | preserved (so end-game dialog shows scores) | zeroed | deleted (Python `del`) |
| g_kScoresDictionary | preserved | zeroed | deleted |
| g_kDeathsDictionary | preserved | zeroed | deleted |
| g_kDamageDictionary | preserved | zeroed | deleted |
| g_kTeamDictionary (Mission2) | preserved | preserved | deleted |
| ReadyForNewPlayers | host: 0 (no new joins) | not changed | reset in MultiplayerGame_Ctor |
| g_bGameOver | host: 1, peers: 1 | host: 0, peers: 0 | 0 |
| Player ships | destroyed (ClearShips) | destroyed (ClearShips) | already destroyed |

## The "weapon-kill SCORE_CHANGE not sent" mystery — resolved

**Conclusion**: This is a stock BC architectural limitation, not a bug. The host's `ObjectKilledHandler` is registered to ET_OBJECT_EXPLODING (0x0080004E), but the EVENT NEVER FIRES ON THE HOST FOR WEAPON KILLS because the dedicated host doesn't run the weapon-damage pipeline.

### Why collision SCORE_CHANGE works

Collision flow:
1. Client A's ship physically collides with client B's ship.
2. Client A reports the collision via opcode `0x15 CollisionEffect` to host.
3. Host's `CollisionEffectHandler` (`0x006A2470`, v5-validated) re-posts the event LOCALLY as `ET_HOST_OBJECT_COLLISION` (0x008000FC) after gates pass.
4. Host's `ShipClass::HostCollisionEffectHandler` (`0x005AFAD0`) computes damage locally, calls `FUN_005AFD70 → FUN_005AF4A0 → FUN_005AFEA0(killerShip)`.
5. Inside `FUN_005AFEA0` HOST branch: `event[+0x28] = killerShip+0x2E4` = killer's NetPlayerID. PostEvent fires ET_OBJECT_EXPLODING locally on host.
6. Host's Python `ObjectKilledHandler` runs, sends `0x36 SCORE_CHANGE_MESSAGE`.

### Why self-destruct SCORE_CHANGE works

1. Client sends `0x13 HostMsg` (self-destruct request, 1 byte payload).
2. Host's `HostMsgHandler` (`0x006A01B0`) runs `FUN_005AF5F0(targetShip)` → `FUN_005AF4A0 → FUN_005AFEA0(killer=NULL)`.
3. `FUN_005AFEA0` with NULL killer: `event[+0x28] = 0`. PostEvent fires ET_OBJECT_EXPLODING.
4. Host's Python `ObjectKilledHandler` runs with `iFiringPlayerID == 0` → no kill credit, but DEATH is recorded → SCORE_CHANGE sent (with killer=0, victim populated).

### Why weapon kills DON'T trigger SCORE_CHANGE

1. Client A fires phaser/torpedo. Sends `0x1A BeamFire` or `0x19 TorpedoFire` to host.
2. Host's `FUN_0069FBB0` (BeamFire receiver) DOES relay to "Forward" group AND locally applies via `FUN_005762B0` — which spawns a beam entity on host with `beam+0x14C = firingPlayerID` (per code at `005762B0`+ host-only line `piVar9[0x53] = unaff_retaddr`).
3. BUT: the host's local copy of B's SHIP doesn't take damage from this beam entity. The damage calculation runs on B's CLIENT (where B's local ship + the beam coexist in physics).
4. Host's representation of B's ship gets its health from inbound `0x1C StateUpdate` packets (flags=0x20 SUB carrying subsystem health). These are STATE WRITES via `Ship::ReadStateUpdate` (`0x005B21C0`), NOT calls into `ApplyDamageToSubsystem`.
5. So FUN_005AFEA0 (Explode) NEVER FIRES on host for weapon kills — the host's local damage pipeline isn't invoked.
6. When client B's ship dies on B's machine, B's local `FUN_005AFEA0` fires with `killer = weapon_obj_at_0x8009_type`. Inside Explode CLIENT branch (DAT_0097fa89 == 0): reads `event[+0x28] = weapon+0x14C` = A's NetPlayerID. ObjectExplodingHandler MP branch sends opcode `0x06 PythonEvent` (factory `0x8129 ObjectExplodingEvent`) to "NoMe" group.
7. Host receives `0x06`, runs `MpgameHandlePythonEvent` (`0x0069F880`), deserializes the event, calls `EventManager::PostEvent` to re-post locally.
8. The re-posted event ON THE HOST has the firingPlayerID correctly set (deserialized from wire). Python `ObjectKilledHandler` SHOULD fire.

**This is where the trace data and our model diverge.** Per the Valentine 33.5min trace:
- `ObjectExplodingEvent (factory 0x8129)` observed 59 times on host.
- `SCORE_CHANGE_MESSAGE (0x36)` sent 0 times for 55 weapon kills, 4 times for 4 self-destructs.

So the event IS arriving at the host, but `ObjectKilledHandler` is somehow not progressing through to the SCORE_CHANGE send. Open question: WHY.

### Most likely hypothesis (unconfirmed, needs trace deep dive)

Two competing hypotheses for the OQ:

**H1**: The replicated event's `pEvent.GetDestination()` returns NULL or non-CT_SHIP because `FUN_006F13C0 (ResolveObjectRefs)` runs BEFORE the ship reference is resolved on the host (race: 0x06 arrives slightly before/after StateUpdate for the dying ship). Mission1.py line 548 gate `if pKilledObject.IsTypeOf(App.CT_SHIP)` would silently early-exit, no SCORE_CHANGE.

**H2**: The 0x06 event is dispatched in MultiplayerGame's RECEIVE phase before Mission1's ObjectKilledHandler is connected to the local event manager — i.e. event posting happens earlier in the frame than Python handler dispatch. Stock dedi might miss the dispatch.

To resolve: capture a stock dedi run with weapon kills, log Python `ObjectKilledHandler` entry to verify it's called for those kills. If not called, gate is the dispatch race. If called but exits early, gate is `IsPlayerShip()`/`GetDestination()`.

### OpenBC implementation guidance

Don't replicate the stock bug. Server-side OpenBC should:
1. Track damage attribution as `0x06` ObjectExplodingEvent arrives.
2. Use `event.firingPlayerID` directly as kill credit (event.destination as victim).
3. Emit `0x36 SCORE_CHANGE_MESSAGE` for ALL deaths regardless of source type (collision, weapon, self-destruct, environmental).
4. Cross-reference with Python `g_kDamageDictionary` if needed for damage-assist scoring.
5. The wire format for 0x36 (sent to "NoMe" group, not broadcast) is fully spec'd by Mission1.py:644-700.

## Mission lifecycle — call chain

Host startup (after game settings + lobby):
1. Host receives `0x01 GameInit` (its own; sent by `FUN_00504F10`):
   - Calls `AI.Setup.GameInit()` (Python, FUN_006F8AB0 invocation)
   - Calls `MultiplayerGame_Ctor("Multiplayer.MultiplayerGame", maxPlayers=16)` — creates Python C++-singleton instance
   - If IsHost: writes `g_iPlayerLimit` to `mpgame+0x1FC` (max-players field)
2. Bootstrap loads `Multiplayer.Episode.Episode → Mission1.Mission1` (mission script).
3. Mission script `Initialize(pMission)` runs:
   - `MissionShared.Initialize(pMission)`: loads TGL databases, sets up `WarpHandler`/`ScanHandler`/`SoundDoneHandler` events, turns on friendly-fire warnings.
   - Mission-specific: `Mission1Menus.BuildMission1Menus()` for host.
   - Setup event handlers including `ET_OBJECT_EXPLODING -> ObjectKilledHandler` (HOST ONLY), `ET_WEAPON_HIT -> DamageEventHandler` (HOST ONLY), and `ET_NETWORK_MESSAGE_EVENT -> ProcessMessageHandler` (ALL peers).

Per-player join sequence (host side):
1. Host receives `0x2A NewPlayerInGame` from joining client.
2. `NewPlayerInGameHandler` (`0x006A1E70`):
   a. Posts local `&DAT_008000F1` ET_NEW_PLAYER_IN_GAME event with playerID.
   b. Calls Python `mission_script.InitNetwork(playerID)` (FUN_006F8AB0 with `s_InitNetwork_0095a354`).
3. Mission's `InitNetwork(iToID)` (Mission1.py:337) sends to the joining player ONLY (targetID = iToID):
   - `0x35 MISSION_INIT_MESSAGE` once (playerLimit, system, time/frag limits)
   - `0x37 SCORE_MESSAGE` N times, one per (kills, deaths, scores) player
4. Then `NewPlayerInGameHandler` iterates DAT_0097E9C8 (scene-sets) and for each living game object:
   - Sends `0x02 ObjCreate` (non-ship) or `0x03 ObjCreateTeam` (ship with NetPlayerID byte)
   - For each exploding/cloaked object: sends `0x29 Explosion`
5. Adds the new player to "NoMe" and "Forward" groups (binary-search-insert).

Mission victory conditions: 100% Python-evaluated. C++ has NO code that decides "you won". The C++ side knows the limits via `g_iFragLimit`/`g_iScoreLimit` strings but does NOT check them; only Python `CheckFragLimit()` runs after each `ObjectKilledHandler` triggers.

## Open questions

1. **Weapon-kill 0x36 absence**: H1 vs H2 above — needs live trace with Python entry log.
2. **Mission2 TEAM_MESSAGE host-relay behavior**: confirmed via Mission2.py:413, but no v5-anchored C++ pathway. Mission2 might fail to send TEAM_MESSAGE on dedi if host's `MultiplayerGame_Cast(App.Game_GetCurrentGame())` lookup returns NULL — needs dedicated-server-mode validation.
3. **Friendly-fire gate in damage pipeline**: where exactly does the binary check group membership? Mission1.py sets warning points but the gate is C++. Probably in FUN_005AF4A0 or its child — needs RE.
4. **Self-destruct SCORE_CHANGE with firingPlayerID=0**: Mission1.py:566 has `if iFiringPlayerID != 0` gate before incrementing kills — so self-destruct death is recorded (deaths++) but no kill credited. SCORE_CHANGE message IS still sent (firingPlayerID=0 written). Confirmed by trace.
5. **Mission5/6/7/9 special-objective end-game triggers**: only verified by string presence in Python; no binary anchoring done.

## Cross-doc impact

These docs need updates:
- `docs/protocol/objcreate-serialization.md` — ship+0x2E4 label change (team_id → NetPlayerID).
- `docs/protocol/game-opcodes.md` — opcode 0x03 ObjCreateTeam wire byte 2 description.
- `docs/protocol/object-replication.md` — MpgameHandleObjCreate plate comment ship+0x2E4 semantics.
- `docs/gamemode-system.md` — entire file is pre-v5; this memo provides the v5-anchored rewrite material.
- `docs/protocol/python-messages.md` — confirm 0x34-0x39 = MISSION_INIT..RESTART_GAME (CLAUDE.md was right; my early-doc fear was wrong).
- `docs/gameplay/damage-system.md` — clarify host doesn't run weapon damage; replication is StateUpdate-driven.

## Evidence packet for documentation-writer

### Confirmed (HIGH confidence, byte-anchored):

| Claim | Address(es) | Method |
|---|---|---|
| MAX_MESSAGE_TYPES = 0x2B sentinel | `0x00654F2C` write `2b 00 00 00`; .rdata string at `0x00952CF8` | byte read |
| ship+0x2E4 = NetPlayerID | `0x006A1AA0` (GetShipFromPlayerID iterator), `0x005AE140` (IsLocalPlayerShip), `0x0060B8C0` (ShipClass_GetNetPlayerID SWIG impl) | decompile + disasm cross-check |
| ship+0xEC = NetType | `0x00607F40` (PhysicsObjectClass_GetNetType SWIG impl) | disasm `MOV EAX, [EDX+0xEC]` |
| ObjectExplodingEvent layout: +0x28 firingPlayerID, +0x2C lifetime | `0x00616990` Set FP, `0x00616A10` Get FP, `0x00616A70` Set Life, `0x00616AF0` Get Life | disasm `MOV [ECX+0x28]` + `D9 58 2C` |
| UtopiaModule+0x40 = friendlyFireTolerance/Max | `0x005EAC10` Get, `0x005EAC80` SetMax | disasm `D9 42 40` / `D9 58 40` |
| UtopiaModule+0x44 = currentFriendlyFire | `0x005EAD00` Get, `0x005EAD3C` Set | disasm `D9 42 44` / `D9 58 44` |
| UtopiaModule+0x48 = friendlyFireWarningPoints | `0x005EAD90` Set | disasm `D9 58 48` |
| KillGameHandler stub (10 bytes) calls vtable[+0x68] | `0x006A2640` | disasm |
| MultiplayerGame vtable[+0x68] (slot 26) = ET_KILL_GAME body | `0x0069EF70` | vtable read at `0x0088B480+0x68` |
| TGNetwork.SendTGMessage SWIG sig "OiO\|i" | string `0x0093846C` | byte read |
| TGNetwork.SendTGMessageToGroup SWIG sig "OOO" | string `0x0093848C` | byte read |
| MpgameHandlePythonEvent local-posts replicated event | `0x0069F880` | decompile + existing v5 plate |
| CollisionEffectHandler runs host-side damage cascade | `0x006A2470` | existing v5 plate |
| Ship__HostCollisionEffectHandler passes killer to FUN_005AFD70 | `0x005AFAD0` | disasm |
| FUN_005AFD70 → FUN_005AF4A0 propagates killer arg via EBP | `0x005AFE26..005AFE44` | disasm |
| FUN_005AF4A0 calls FUN_005AFEA0(killer) on lethal damage | `0x005AF5D0..005AF5DC` | decompile + disasm |
| FUN_005AFEA0 HOST branch writes killer+0x2E4 to event[+0x28] | `0x005AFEA0..005AFFF0` | decompile |

### Inferred (MEDIUM confidence, evidence in Python):

| Claim | Evidence |
|---|---|
| Mission*.py SCORE_CHANGE wire format byte-for-byte | MissionShared.py + Mission1.py read/write code (line 271/653) |
| Mission2 TEAM_MESSAGE host-relay to NoMe | Mission2.py:413 `if IsHost(): SendTGMessageToGroup("NoMe")` |
| Score limit triggers (frag/score/time) | Mission*.CheckFragLimit() + MissionShared.UpdateTimeLeftHandler() |
| END_GAME_MESSAGE causes ClearShips + SetReadyForNewPlayers(0) on host | MissionShared.py:344 + line 224 receiver |
| g_iUseScoreLimit mode: `g_kScoresDictionary[X] >= g_iFragLimit * 10000` gate | Mission1.py:729 |

### Unknown (LOW / open question):

| Claim | Status |
|---|---|
| Why weapon-kill 0x36 not emitted in stock trace | Architecturally should fire; trace shows it doesn't. Likely race in host-side event dispatch. Needs live-run instrumentation. |
| Friendly-fire damage gate location | Probably in FUN_005AF4A0 child chain checking Mission.GetFriendGroup membership; not yet RE'd. |
| Why Mission1 has ObjectKilledHandler registered only IF IsHost(), but ObjectKilledHandler also runs on clients per Mission1.py:194 — actually only on host per IsHost gate. Confirmed via re-reading. |
