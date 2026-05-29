# STBC Reverse Engineering - Development Context

Reverse engineering Star Trek: Bridge Commander to produce behavioral specifications for [OpenBC](https://github.com/SandboxServers/OpenBC), a clean-room reimplementation. Includes a DDraw proxy DLL for runtime instrumentation, Ghidra annotation scripts, and extensive RE documentation. Cross-compiled from WSL2.

## Repo Layout
- `src/proxy/ddraw_main.c` - Entry point, includes 7 split files (~6260 lines total)
- `src/proxy/ddraw_main/` - Split implementation files:
  - `binary_patches_and_python_bridge.inc.c` - All binary patches, Python bridge (RunPyCode)
  - `game_loop_and_bootstrap.inc.c` - GameLoopTimerProc, bootstrap phases, DeferredInitObject
  - `core_runtime_and_exports.inc.c` - DllMain, COM proxy setup, exports
  - `packet_trace_and_decode.inc.c` - Packet tracing, AlbyRules cipher, opcode decoding
  - `socket_and_input_hooks.inc.c` - sendto/recvfrom hooks, input handling
  - `runtime_hooks_and_iat.inc.c` - IAT hooking, runtime patches
  - `message_factory_hooks.inc.c` - TGMessage factory interception
- `src/proxy/` - Other proxy DLL sources (ddraw7, surface7, d3d7, header, def)
- `src/scripts/Custom/DedicatedServer.py` - Python server config (checksum exempt)
- `src/scripts/Custom/ClientLogger.py` - Client-side diagnostic hooks (checksum exempt)
- `src/scripts/Local.py` - Server custom hook (checksum exempt)
- `src/scripts/ClientLocal.py` - Client custom hook (deployed as Local.py on client)
- `config/dedicated.cfg` - Empty trigger file (presence enables dedicated mode)
- `game/server/` - Live server game install (gitignored except readme.md)
- `game/client/` - Live client game install (gitignored except readme.md)
- `tools/` - Ghidra annotation scripts and analysis utilities
- `engine/gamebyro-1.2-source/` - Gamebryo 1.2 full source (reference for NI class implementations)
- `engine/mwse/` - MWSE reverse-engineered NI 4.0.0.2 headers (identical struct sizes to NI 3.1)
- `engine/nif.xml` - NIF format spec from niftools (V3.1 field definitions for 21 of 42 NI 3.1-only classes)
- `docs/` - Reverse engineering notes, protocol docs, API reference
- `reference/decompiled/` - Ghidra C output (19 files, ~15MB total)
- `reference/scripts/` - Decompiled game Python (~1228 .py files)

## Build & Deploy
```bash
make build          # Cross-compile ddraw.dll
make deploy         # Deploy to BOTH server and client game dirs
make deploy-server  # Deploy proxy DLL + server scripts to game/server/
make deploy-client  # Deploy client logger scripts to game/client/
make run-server     # Deploy + launch server
make run-client     # Deploy client + launch client
make logs-server    # View server logs (proxy, packet trace, dedicated init)
make logs-client    # View client debug log
make clean          # Remove build artifacts
```

## Current Status: FUNCTIONAL MULTIPLAYER (COLLISION + SUBSYSTEM DAMAGE WORKING)
Client connects, checksums pass, reaches ship selection, picks ship, and plays with working
collision damage and subsystem damage. The main multiplayer loop is functional.

### What Works
- Headless boot (all 4 bootstrap phases), Python DedicatedServer.TopWindowInitialized() runs
- MultiplayerGame: ReadyForNewPlayers=1, MaxPlayers=8, ProcessingPackets=1
- GameSpy LAN discovery, checksum exchange (4 rounds), keepalive
- Import hook patches mission handlers for headless mode (func_code replacement)
- Client reaches ship selection screen, player appears on scoreboard
- **DeferredInitObject**: Python-driven ship creation with real NIF models and subsystems
- **InitNetwork timing**: Peer-array detection fires within ~1.4s (matches stock ~2s timing)
- **Collision damage**: Ships take hull and subsystem damage from collisions
- **Subsystem damage**: Individual subsystems (shields, weapons, engines) take and report damage
- **StateUpdate flags=0x20**: Server sends real subsystem health data (was 0x00/empty)
- Packet trace system: full hex dumps to `game/server/packet_trace.log`
- Client-side logging: `game/client/client_debug.log`
- CrashDumpHandler (SetUnhandledExceptionFilter) logs full diagnostics on any crash

### Known Issues
- `scoring dict fix rc=-1` - Python code for SCORE_MESSAGE send has an error
- Server's own ship object (player 0) still sends flags=0x00 (harmless — host's dummy ship)
- Double NewPlayerInGame: engine handler + our GameLoopTimerProc both fire
- SCORE_CHANGE (0x36) not sent for weapon kills on stock dedi — may be a stock BC bug (collision kills work)
- Collision rate limiting disabled (ship+0xEC=0) — DeferredInitObject doesn't set enable flag, 269x excess collision events
- Collision damage authority inverted — our server accepts client CollisionEffect(0x15) without server-side recomputation
- No server-side distance validation on CollisionEffect — stock validates bounding sphere gap < 26 units

### Key Fixes Applied (in ddraw_main.c split files)
1. **TGL FindEntry NULL fix** - code cave at 0x006D1E10, returns NULL when ECX is NULL
2. **Network NULL list guard** - code cave at 0x005B1D57, clears SUB/WPN flags when ship+0x284 NULL
3. **Subsystem hash check fix** - code cave at 0x005B22B5, prevents false anti-cheat kicks
4. **Compressed vector read guard** - validates vtable at 0x006D2EB0/0x006D2FD0
5. **CWD fix** - SetCurrentDirectoryA(g_szBasePath) in DllMain
6. **NewPlayerInGame handshake** - GameLoopTimerProc calls FUN_006a1e70 when player count increases
7. **Scoring dict registration** - adds player to scoring dictionaries after NewPlayerInGame
8. **Renderer pipeline proxy** - D3D7/DDraw7/Surface7 COM proxies provide valid objects to engine
9. **DeferredInitObject** - Python-driven ship creation: loads NIF, creates subsystems, populates ship+0x284
10. **InitNetwork peer-array detection** - detects new peers from WSN peer array (replaces broken bc-flag)

### Diagnostic Logs
- `game/server/ddraw_proxy.log` - Main proxy log (boot, game loop, patches)
- `game/server/packet_trace.log` - Full packet hex dumps with opcode decoding
- `game/server/tick_trace.log` - Per-tick CSV: timing, queues, player counts (15 columns)
- `game/server/crash_dump.log` - Full crash diagnostics (registers, stack, code bytes)
- `game/server/dedicated_init.log` - Python-side boot/runtime log
- `game/client/client_debug.log` - Client-side handler tracing

## Key Architecture

### Engine
- **NetImmerse 3.1** (predecessor to Gamebryo), DirectDraw 7 / Direct3D 7
- **Networking**: Winsock UDP (TGWinsockNetwork), NOT DirectPlay
- **Scripting**: Embedded Python 1.5, SWIG 1.x bindings (App/Appc modules)
- **Executable**: 32-bit Windows (stbc.exe, ~5.9MB, base 0x400000)

### Three Message Dispatchers
1. **NetFile dispatcher (FUN_006a3cd0)**: Checksums/file opcodes 0x20-0x27
2. **MultiplayerGame dispatcher (MpgameHandleMessage at 0x0069f2a0)**: Game opcodes 0x02-0x2A (jump table at 0x0069F534, 41 entries indexed by opcode-2). v5-validated 2026-05-28.
3. **MultiplayerWindow dispatcher (FUN_00504c10)**: Opcodes 0x00, 0x01, 0x16 (UI-level settings)
4. **Python SendTGMessage**: Opcodes 0x2C-0x39 (chat, scoring, game flow) bypass C++ dispatcher

### Game Opcode Table (v5-validated 2026-05-28 from MpgameHandleMessage jump table + packet traces)
| Opcode | Name | Handler | Type |
|--------|------|---------|------|
| 0x00 | Settings | FUN_00504d30 | Game config (gameTime, map, collision) — MultiplayerWindow dispatcher |
| 0x01 | GameInit | FUN_00504f10 | Game start trigger — MultiplayerWindow dispatcher |
| 0x02 | ObjCreate | FUN_0069f620 | Non-team object creation |
| 0x03 | ObjCreateTeam | FUN_0069f620 | Ship creation with team |
| 0x04 | (dead) | DEFAULT | Jump table default; boot sent via TGBootPlayerMessage |
| 0x05 | (dead) | DEFAULT | Jump table default |
| 0x06 | PythonEvent | FUN_0069f880 | **Primary event forwarding** (3432/session) |
| 0x07 | StartFiring | FUN_0069fda0 | Weapon fire begin (2282/session) |
| 0x08 | StopFiring | FUN_0069fda0 | Weapon fire end |
| 0x09 | StopFiringAtTarget | FUN_0069fda0 | Stop firing at specific target |
| 0x0A | SubsysStatus | FUN_0069fda0 | Subsystem toggle (shields, etc.) |
| 0x0B | AddToRepairList | FUN_0069fda0 | Crew repair assignment |
| 0x0C | ClientEvent | FUN_0069fda0 | Generic event forward (preserve=0) |
| 0x0D | PythonEvent2 | FUN_0069f880 | Alternate Python event path |
| 0x0E | StartCloak | FUN_0069fda0 | Cloak engage (event 0x008000E3) |
| 0x0F | StopCloak | FUN_0069fda0 | Cloak disengage (event 0x008000E5) |
| 0x10 | StartWarp | FUN_0069fda0 | Warp drive engage |
| 0x11 | RepairListPriority | FUN_0069fda0 | Repair priority ordering |
| 0x12 | SetPhaserLevel | FUN_0069fda0 | Phaser power/intensity (event 0x008000E0) |
| 0x13 | HostMsg | FUN_006A01B0 | Self-destruct request (client→host, 1-byte, no payload) |
| 0x14 | DestroyObject | FUN_006a01e0 | Object destruction |
| 0x15 | CollisionEffect | FUN_006a2470 | **Collision damage relay** (84/session) |
| 0x16 | UICollisionSetting | FUN_00504c70 | Collision toggle (MultiplayerWindow dispatcher) |
| 0x17 | DeletePlayerUI | FUN_006a1360 | Remove player from scoreboard |
| 0x18 | DeletePlayerAnim | FUN_006a1420 | "Player joined/left" floating text (TGL lookup, crash risk) |
| 0x19 | TorpedoFire | FUN_0069f930 | Torpedo launch (897/session) |
| 0x1A | BeamFire | FUN_0069fbb0 | Beam weapon hit |
| 0x1B | TorpTypeChange | FUN_0069fda0 | Torpedo type switch (event 0x008000FD) |
| 0x1C | StateUpdate | FUN_0069ff50 | **Per-tick object state replication** — see `docs/protocol/stateupdate.md` (v5-validated 2026-05-28) |
| 0x1D | ObjNotFound | FUN_006a0490 | Object lookup failure |
| 0x1E | RequestObj | FUN_006a02a0 | Request object data |
| 0x1F | EnterSet | FUN_006a05e0 | Enter game set |
| 0x29 | Explosion | FUN_006a0080 | Explosion damage (S→C only) |
| 0x2A | NewPlayerInGame | FUN_006a1e70 | Player join handshake |

### Python-Level Messages (via SendTGMessage, bypass C++ dispatcher)
| Byte | Name | Notes |
|------|------|-------|
| 0x2C | CHAT_MESSAGE | We forward this |
| 0x2D | TEAM_CHAT_MESSAGE | We forward this |
| 0x35 | MISSION_INIT_MESSAGE | Game config |
| 0x36 | SCORE_CHANGE_MESSAGE | Score deltas |
| 0x37 | SCORE_MESSAGE | Full score sync |
| 0x38 | END_GAME_MESSAGE | Game over |
| 0x39 | RESTART_GAME_MESSAGE | Game restart |

### Settings Packet (opcode 0x00) - sent after checksums pass
`[0x00] [float:gameTime] [byte:0x008e5f59] [byte:0x0097faa2] [byte:playerSlot] [short:mapLen] [data:mapName] [byte:checksumFlag] [if 1: checksum data]`
Then opcode 0x01 (single byte).

### Key Globals
| Address | What |
|---------|------|
| 0x0097FA00 | UtopiaModule base |
| 0x0097FA78 | TGWinsockNetwork* (UtopiaModule+0x78) |
| 0x0097FA7C | GameSpy ptr (+0xDC=qr_t) |
| 0x0097FA80 | NetFile/ChecksumMgr |
| 0x0097FA88 | IsClient (BYTE) - 0=host, 1=client |
| 0x0097FA89 | IsHost (BYTE) - 1=host, 0=client |
| 0x0097FA8A | IsMultiplayer (BYTE) |
| 0x008e5f59 | Settings byte 1 (sent in opcode 0x00, currently 0x01) |
| 0x0097faa2 | Settings byte 2 (sent in opcode 0x00, currently 0x00) |
| 0x0097e238 | PlayWindow / Game state ptr (NOT TopWindow — corrected 2026-05-28 per docs/engine/ui-class-hierarchy.md) |
| 0x009878cc | TopWindow (root scene/window container — owns 5 MainWindow children) |
| 0x00991438 | TGEventManager singleton (zero in image, populated at boot) |
| 0x009a09d0 | Clock object ptr (+0x90=gameTime, +0x54=frameTime) |

## Python 1.5 Quirks (CRITICAL)
- `print "string"` (no parens), `except Exception, e:` (not `as e`)
- No list comprehensions, no ternary, no `os`/`string` module imports
- **`x in dict` FAILS** - use `dict.has_key(x)`
- **`'sub' in 'string'` FAILS** - use `strop.find(string, sub) >= 0`
- **`__import__('A.B.C')`** returns package A; actual module in `sys.modules['A.B.C']`
- **Always delete .pyc** after editing .py files

## Multiplayer Checksum System
- `scripts/Custom/` directory is EXEMPT from checksums
- `scripts/Local.py` is also exempt - vanilla clients can connect to modded servers

## Decompiled Source Reference
19 organized files in `reference/decompiled/`:
- `01_core_engine.c` - Core engine, memory, containers
- `02_utopia_app.c` - UtopiaApp, game init, Python bridge
- `03_game_objects.c` - Ships, weapons, systems, AI
- `04_ui_windows.c` - UI panes, windows, menus
- `05_game_mission.c` - Mission logic, scenarios
- `09_multiplayer_game.c` - MP game logic, handlers
- `10_netfile_checksums.c` - Checksums, file transfer
- `11_tgnetwork.c` - TGWinsockNetwork, packet I/O

## Documentation Index

### Architecture
- [docs/architecture/architecture-overview.md](docs/architecture/architecture-overview.md) - How the proxy DLL works, COM chain, bootstrap phases
- [docs/architecture/dedicated-server.md](docs/architecture/dedicated-server.md) - Bootstrap sequence, patches, crash handling
- [docs/architecture/multiplayer-mission-infrastructure.md](docs/architecture/multiplayer-mission-infrastructure.md) - Mission scripting infrastructure
- [docs/architecture/main-loop-timing.md](docs/architecture/main-loop-timing.md) - Game loop timing analysis

### Protocol
- [docs/protocol/wire-format-spec.md](docs/protocol/wire-format-spec.md) - Hub: summary opcode tables, subsystem catalog, anti-cheat hash
- [docs/protocol/transport-layer.md](docs/protocol/transport-layer.md) - Raw UDP packet, 7 transport types, TGMessage layout, fragment reassembly
- [docs/protocol/stream-primitives.md](docs/protocol/stream-primitives.md) - TGBufferStream read/write, bit packing, CF16, CompressedVector3/4
- [docs/protocol/checksum-opcodes.md](docs/protocol/checksum-opcodes.md) - Opcodes 0x20-0x28: checksum request/response, file transfer, 5 rounds
- [docs/protocol/game-opcodes.md](docs/protocol/game-opcodes.md) - Opcodes 0x00-0x2A: Settings, GameInit, ObjCreate, PythonEvent, weapons, etc.
- [docs/protocol/stateupdate.md](docs/protocol/stateupdate.md) - Opcode 0x1C: dirty flags, 8 field formats, round-robin subsystem/weapon serialization
- [docs/protocol/object-replication.md](docs/protocol/object-replication.md) - FUN_0069f620 object create/update, serialization chain
- [docs/protocol/python-messages.md](docs/protocol/python-messages.md) - Opcodes 0x2C+: TGMessage script messages, SendTGMessage API, wire examples
- [docs/protocol/pythonevent-wire-format.md](docs/protocol/pythonevent-wire-format.md) - PythonEvent (opcode 0x06) RE: polymorphic TGStreamedObject transport, 4 event classes, collision→repair chain
- [docs/protocol/tgobjptrevent-class.md](docs/protocol/tgobjptrevent-class.md) - TGObjPtrEvent (factory 0x010C): class layout, wire format, 5 C++ producers, 45% of combat PythonEvents
- [docs/protocol/set-phaser-level-protocol.md](docs/protocol/set-phaser-level-protocol.md) - SetPhaserLevel (opcode 0x12) RE: TGCharEvent wire format, generic event forward group
- [docs/protocol/collision-effect-protocol.md](docs/protocol/collision-effect-protocol.md) - CollisionEffect (opcode 0x15) RE: wire format, CompressedVec4_Byte contacts, handler validation
- [docs/protocol/delete-player-ui-wire-format.md](docs/protocol/delete-player-ui-wire-format.md) - DeletePlayerUI (opcode 0x17) RE: TGEvent transport, join/disconnect player list, scoreboard dependency
- [docs/protocol/stateupdate-subsystem-wire-format.md](docs/protocol/stateupdate-subsystem-wire-format.md) - Subsystem health wire format: linked list order, WriteState formats, round-robin
- [docs/protocol/subsystem-integrity-hash.md](docs/protocol/subsystem-integrity-hash.md) - Subsystem integrity hash: dead code in MP
- [docs/protocol/cf16-precision-analysis.md](docs/protocol/cf16-precision-analysis.md) - CF16 precision tables and mod compatibility
- [docs/protocol/cf16-explosion-encoding.md](docs/protocol/cf16-explosion-encoding.md) - CF16 explosion encoding, mod weapon-type ID compatibility
- [docs/protocol/objcreate-serialization.md](docs/protocol/objcreate-serialization.md) - Full object serialization chain
- [docs/protocol/message-trace-vs-packet-trace.md](docs/protocol/message-trace-vs-packet-trace.md) - Stock-dedi opcode cross-reference
- [docs/protocol/tgmessage-routing.md](docs/protocol/tgmessage-routing.md) - TGMessage routing RE: relay-all, star topology, mod compatibility

### Networking
> **v5 validation status (2026-05-28)**: Networking family campaign closed at 11/11 docs validated (2 verified + 9 partial). See [docs/networking/v5-validation-status.md](docs/networking/v5-validation-status.md) for the per-doc tracker.

- [docs/networking/network-protocol.md](docs/networking/network-protocol.md) - Protocol architecture, event system, handler tables
- [docs/networking/multiplayer-flow.md](docs/networking/multiplayer-flow.md) - Complete client/server join flow (connect → play)
- [docs/networking/gamespy-discovery.md](docs/networking/gamespy-discovery.md) - GameSpy LAN/internet discovery, master server, QR1 crypto
- [docs/networking/gamespy-crypto-analysis.md](docs/networking/gamespy-crypto-analysis.md) - GameSpy challenge-response cryptography
- [docs/networking/alby-rules-cipher-analysis.md](docs/networking/alby-rules-cipher-analysis.md) - AlbyRules! packet encryption cipher
- [docs/networking/tgmessage-routing-cleanroom.md](docs/networking/tgmessage-routing-cleanroom.md) - Clean-room TGMessage routing spec
- [docs/networking/netimmerse-transport-deep-dive.md](docs/networking/netimmerse-transport-deep-dive.md) - NetImmerse transport layer internals
- [docs/networking/fragmented-ack-bug.md](docs/networking/fragmented-ack-bug.md) - Fragmented reliable message ACK bug
- [docs/networking/ack-outbox-deadlock.md](docs/networking/ack-outbox-deadlock.md) - ACK-outbox deadlock: two-pass processing, memory leak, data starvation
- [docs/networking/disconnect-flow.md](docs/networking/disconnect-flow.md) - Player disconnect: 3 detection paths, cleanup cascade
- [docs/networking/ship-death-lifecycle.md](docs/networking/ship-death-lifecycle.md) - Ship death in MP: Explosion + respawn, DestroyObject NOT used

### Gameplay
- [docs/gameplay/combat-mechanics-re.md](docs/gameplay/combat-mechanics-re.md) - Consolidated combat RE: shields, cloak, weapons, repair, tractor
- [docs/gameplay/damage-system.md](docs/gameplay/damage-system.md) - Complete damage pipeline: collision, weapon, explosion paths, gate checks
- [docs/gameplay/shield-system.md](docs/gameplay/shield-system.md) - Shield system: 6-facing ellipsoid, absorption, power-budget recharge
- [docs/gameplay/cloaking-state-machine.md](docs/gameplay/cloaking-state-machine.md) - Cloak device: 4 states, shield disable, energy failure auto-decloak
- [docs/gameplay/weapon-firing-mechanics.md](docs/gameplay/weapon-firing-mechanics.md) - Weapons: phaser charge/discharge, torpedo reload, CanFire gates
- [docs/gameplay/power-system.md](docs/gameplay/power-system.md) - Power/reactor system RE: 3-class architecture, battery/conduit model, per-ship tables
- [docs/gameplay/repair-system.md](docs/gameplay/repair-system.md) - Complete repair system RE: queue, rate formula, priority toggle, 7 event handlers
- [docs/gameplay/repair-tractor-analysis.md](docs/gameplay/repair-tractor-analysis.md) - Repair teams + tractor: 6 modes, multiplicative drag, no direct damage
- [docs/gameplay/repair-event-object-ids.md](docs/gameplay/repair-event-object-ids.md) - Repair event object ID analysis
- [docs/gameplay/collision-detection-system.md](docs/gameplay/collision-detection-system.md) - Collision: 3-tier (sweep-and-prune -> bounding sphere -> narrow)
- [docs/gameplay/collision-shield-interaction.md](docs/gameplay/collision-shield-interaction.md) - Collision-shield: directional absorption, two-step damage
- [docs/gameplay/self-destruct-pipeline.md](docs/gameplay/self-destruct-pipeline.md) - Self-destruct: opcode 0x13, 3 execution paths, PowerSubsystem cascade
- [docs/gameplay/objcreate-unknown-species-analysis.md](docs/gameplay/objcreate-unknown-species-analysis.md) - ObjCreate with unknown species: failure modes, crash risks
- [docs/gameplay/ai-architecture.md](docs/gameplay/ai-architecture.md) - AI behavior tree: 8 C++ classes, vtable layouts, Python bridge, tick scheduling, shipped behavior catalog
- [docs/gameplay/ship-navigation.md](docs/gameplay/ship-navigation.md) - Ship targeting pipeline, turn computation, impulse model, in-system warp, network authority
- [docs/gamemode-system.md](docs/gamemode-system.md) - Gamemode/mission system RE: two-layer architecture, scoring, wire formats, team system, end/restart flow

### Engine
- [docs/engine/rtti-class-catalog.md](docs/engine/rtti-class-catalog.md) - 670 classes: 129 NI, 124 TG, ~420 game (RTTI extraction)
- [docs/engine/gamebryo-cross-reference.md](docs/engine/gamebryo-cross-reference.md) - 129 NI classes cross-referenced: Gb 1.2, MWSE, nif.xml
- [docs/engine/nirtti-factory-catalog.md](docs/engine/nirtti-factory-catalog.md) - 117 NiRTTI factory registrations with addresses
- [docs/engine/netimmerse-vtables.md](docs/engine/netimmerse-vtables.md) - Vtable maps for 6 core NI classes
- [docs/engine/event-system-architecture.md](docs/engine/event-system-architecture.md) - TGEventManager dispatch, handler tables, TGCallback/TGConditionHandler internals
- [docs/engine/ui-class-hierarchy.md](docs/engine/ui-class-hierarchy.md) - UI inheritance tree, MainWindow type IDs, event constants, TGDialogWindow buttons
- [docs/engine/function-map.md](docs/engine/function-map.md) - 18K-function organized map
- [docs/engine/function-mapping-report.md](docs/engine/function-mapping-report.md) - Annotation script reference (currently unapplied); current Ghidra naming = 25.8% (4,797/18,581, auto-analysis only)
- [docs/engine/decompiled-functions.md](docs/engine/decompiled-functions.md) - Key function analysis

### Guides
- [docs/guides/developer-workflow.md](docs/guides/developer-workflow.md) - Build, deploy, test workflow
- [docs/guides/reading-decompiled-code.md](docs/guides/reading-decompiled-code.md) - Tips for reading Ghidra output
- [docs/guides/binary-patching-primer.md](docs/guides/binary-patching-primer.md) - Code caves, JMP hooks, calling conventions
- [docs/guides/python-152-guide.md](docs/guides/python-152-guide.md) - Python 1.5.2 compatibility guide
- [docs/guides/swig-api.md](docs/guides/swig-api.md) - SWIG function reference
- [docs/guides/lessons-learned.md](docs/guides/lessons-learned.md) - Debugging techniques, pitfalls, protocol discoveries
- [docs/troubleshooting.md](docs/troubleshooting.md) - Symptom-to-cause quick reference


### Analysis
- [docs/analysis/collision-trace-comparison.md](docs/analysis/collision-trace-comparison.md) - Stock dedi vs OpenBC: byte-level wire format comparison, 6 behavioral gaps
- [docs/analysis/stock-trace-analysis.md](docs/analysis/stock-trace-analysis.md) - Ground truth from stock dedi traces: 10 findings, opcode frequencies
- [docs/analysis/valentines-day-battle-analysis.md](docs/analysis/valentines-day-battle-analysis.md) - Comprehensive 33.5min 3-player stock trace: 59 deaths, full opcode table, parity checklist, authority summary
- [docs/analysis/openbc-collision-test-feb22.md](docs/analysis/openbc-collision-test-feb22.md) - Per-species power failures (species 10-13) + collision rate limiting absent (28,504 packets/11min)
- [docs/analysis/subsystem-trace-analysis.md](docs/analysis/subsystem-trace-analysis.md) - Ship subsystem creation pipeline (from stock trace)
- [docs/analysis/cut-content-analysis.md](docs/analysis/cut-content-analysis.md) - Cut/hidden features: ghost missions, fleet command AI, tractor docking
- [docs/analysis/empty-stateupdate-root-cause.md](docs/analysis/empty-stateupdate-root-cause.md) - Why flags=0x00 happened (RESOLVED)
- [docs/analysis/black-screen-investigation.md](docs/analysis/black-screen-investigation.md) - Client disconnect investigation (RESOLVED)
- [docs/analysis/tgl-lookup-crash-analysis.md](docs/analysis/tgl-lookup-crash-analysis.md) - Client AV at FUN_006f56f0: TGL resource lookup returns near-NULL on player join (0x18/NewPlayerInGameHandler)
- [docs/analysis/veh-cascade-triage.md](docs/analysis/veh-cascade-triage.md) - Why VEH was removed (historical)

### OpenBC Clean-Room Specs
- **OpenBC**: `../OpenBC/docs/collision-shield-interaction.md` - Clean-room collision-shield spec
- **OpenBC**: `../OpenBC/docs/repair-system.md` - Clean-room repair system spec
- **OpenBC**: `../OpenBC/docs/power-system.md` - Clean-room power system spec
- **OpenBC**: `../OpenBC/docs/set-phaser-level-wire-format.md` - Clean-room SetPhaserLevel spec
- **OpenBC**: `../OpenBC/docs/ack-outbox-deadlock.md` - Clean-room ACK-outbox deadlock spec
- **OpenBC**: `../OpenBC/docs/self-destruct-system.md` - Clean-room self-destruct spec
- **OpenBC**: `../OpenBC/docs/pythonevent-wire-format.md` - Clean-room PythonEvent spec
- **OpenBC**: `../OpenBC/docs/ship-death-lifecycle.md` - Clean-room ship death/respawn spec
- **OpenBC**: `../OpenBC/docs/wire-formats/delete-player-ui-wire-format.md` - Clean-room DeletePlayerUI (0x17) wire format
- **OpenBC**: `../OpenBC/docs/wire-formats/delete-player-anim-wire-format.md` - Clean-room DeletePlayerAnim (0x18) wire format + TGL crash risk
- **OpenBC**: `../OpenBC/docs/wire-formats/event-forward-wire-format.md` - Clean-room GenericEventForward (0x07-0x12, 0x1B) group spec
- **OpenBC**: `../OpenBC/docs/gamemode-system.md` - Clean-room gamemode spec: scoring rules, wire formats, team system, end/restart flow, server implementation requirements, state tracking
- **OpenBC**: `../OpenBC/docs/game-systems/ai-system.md` - Clean-room AI behavior tree spec: node types, conditions, compound behaviors, difficulty, fleet commands
- **OpenBC**: `../OpenBC/docs/game-systems/ship-movement.md` - Clean-room ship movement spec: targeting, impulse model, turn computation, in-system warp, network authority

## Ghidra Annotation Scripts (REFERENCE ONLY — NOT CURRENTLY APPLIED)

> **v5 policy**: The 8 annotation scripts in `tools/` are NOT run against the current Ghidra import (created 2026-05-28). Prior runs produced known-wrong function names that caused downstream RE churn. Under v5, naming happens function-by-function via `FUNCTION_DOC_WORKFLOW_V5` with `analyze_function_completeness` scoring. See [docs/guides/v5-doc-validation-workflow.md § "Why no annotation scripts"](docs/guides/v5-doc-validation-workflow.md) for the policy.

The scripts below describe what each WOULD produce if run (script intent verified during v5 doc #6 validation; counts not currently applied):
- `tools/ghidra_annotate_globals.py` - Would label 19 globals, ~2,355 key RE'd functions, 22 Python module tables (~2,396 total)
- `tools/ghidra_annotate_nirtti.py` - Would label 117 NiRTTI factory + 117 registration functions (234 total)
- `tools/ghidra_annotate_swig.py` - Would name 3,990 SWIG wrapper functions from PyMethodDef table
- `tools/ghidra_annotate_python_capi.py` - Would name 113 Python C API functions, 10 module inits, type objects, globals (137 total)
- `tools/ghidra_annotate_pymodules.py` - Would walk 21 Python module method tables, name 266 C implementations
- `tools/ghidra_annotate_vtables.py` - Would auto-discover ~97 vtables from NiRTTI factories: 1,090 virtuals + 96 ctors + 84 dtors (1,270 total)
- `tools/ghidra_annotate_swig_targets.py` - Would trace SWIG wrappers to C++ targets (4 named; 3,986 are inline field accessors)
- `tools/ghidra_discover_strings.py` - Would name 33 functions from debug strings + add 515 comments

**Current Ghidra state** (2026-05-28): 4,797 custom-named (25.8%), all Ghidra auto-analysis artifacts (Catch@, Unwind@, library imports, STL templates). Only project-applied rename: `MpgameHandleMessage` at 0x0069f2a0 (from v5 dispatcher recovery). See [docs/engine/function-mapping-report.md](docs/engine/function-mapping-report.md) for current coverage details.

## Knowledge Preservation

After completing long-form reverse engineering analysis where findings are high-confidence (verified against live game traces or decompiled code), **always**:
1. Write or update a `docs/` markdown file with the findings (function addresses, call graphs, data layouts, gate conditions)
2. Update agent memory files with key discoveries for cross-session continuity
3. Add new docs to the Documentation Index above

This ensures hard-won RE knowledge is never lost between sessions.

## Agent Team

This project uses specialized agents for ALL analysis, research, and investigation work. The orchestrator (main conversation) does NOT perform these tasks directly — it delegates to agents, synthesizes their findings, and writes the actual code.

### Hard Rules
1. **Agents do research and analysis ONLY.** They must NEVER write or modify project source code. Code changes are exclusively the orchestrator's job.
2. **All Ghidra MCP tool usage** (`mcp__ghidra__*`) MUST go through the `game-reverse-engineer` agent. Never call Ghidra tools directly.
3. **Launch agents in parallel** when their tasks are independent. A crash investigation might need `win32-crash-analyst` + `game-reverse-engineer` + `x86-patch-engineer` simultaneously.
4. **Use 1 to all 7 agents** as the situation demands. Simple tasks need one agent; complex issues may need findings from multiple agents combined before writing code.
5. **Agents report findings back.** The orchestrator reads their reports, synthesizes a fix, writes the code, and tests it.

### Agent Roster

| Agent | Domain | Use For |
|-------|--------|---------|
| `game-reverse-engineer` | Binary RE, Ghidra decompilation, code archaeology | Decompiling functions, tracing xrefs, identifying vtable layouts, understanding what code does. **Only agent with Ghidra MCP access.** |
| `netimmerse-engine-dev` | NetImmerse 3.1.1 / Gamebryo engine internals | Scene graph questions, NIF format, renderer pipeline, NiNode hierarchy, engine object lifecycle, headless server architecture |
| `stbc-original-dev` | Design intent, original developer perspective | Ambiguous decompiled code, "was this a bug or intentional?", how features were meant to work, cut content reasoning |
| `python-152-reviewer` | Python 1.5.2 compatibility | Reviewing/writing Python code for BC's embedded interpreter, catching version-incompatible constructs |
| `x86-patch-engineer` | x86-32 instruction encoding, code caves, binary patches | Code cave construction, JMP/CALL displacement calculation, calling convention analysis, VEH handler logic, stack frame layout |
| `win32-crash-analyst` | Crash triage, VEH/SEH, register dumps | Analyzing crash logs, access violations, NULL dereference chains, bad vtable calls, determining root cause from register snapshots |
| `network-protocol-analyst` | UDP protocol, packet traces, handshake flows | Decoding packet_trace.log hex dumps, tracing opcode sequences, identifying where client/server conversations break down |

### Typical Workflows

**Crash investigation:**
1. `win32-crash-analyst` triages the crash log (registers, stack, access pattern)
2. `game-reverse-engineer` decompiles the crashing function and its callers
3. `x86-patch-engineer` designs the binary fix (code cave, EIP skip, or instruction patch)
4. Orchestrator writes the C code in ddraw_main.c

**Client disconnect debugging:**
1. `network-protocol-analyst` decodes the packet trace around the disconnect
2. `game-reverse-engineer` traces the message handler chain
3. `stbc-original-dev` explains expected handshake behavior
4. Orchestrator implements the fix

**New proxy method needed:**
1. `game-reverse-engineer` decompiles the caller to understand expected behavior
2. `netimmerse-engine-dev` explains what the engine expects from the COM interface
3. Orchestrator implements the proxy method

## Ghidra MCP Setup
This project uses a Ghidra MCP server for live decompilation. To set up:
```bash
claude mcp add ghidra --transport stdio -- \
  /path/to/python3 /path/to/GhidraMCP/bridge_mcp_ghidra.py \
  --ghidra-server http://<ghidra-host>:8090/
```
The Ghidra HTTP bridge must be running (GhidraMCP plugin in Ghidra with stbc.exe loaded).
