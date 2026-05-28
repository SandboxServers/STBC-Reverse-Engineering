# Game Reverse Engineer Memory

## Project: STBC Dedicated Server (Star Trek: Bridge Commander)
- DDraw proxy DLL (`ddraw_main.c`, ~3600 lines C), cross-compiled from WSL2
- NetImmerse 3.1 engine, Winsock UDP, embedded Python 1.5.2 (SWIG 1.x)
- stbc.exe: 32-bit Windows, base 0x400000, ~5.9MB

## Key Architecture Discoveries (topic files)
- [collision-rate-limiter.md](collision-rate-limiter.md) - COMPLETE: Ship__CheckCollisionRateLimit (0x005a22a0) per-pair timer, cooldown table, distance gates (2026-02-24)
- [architecture.md](architecture.md) - Detailed architecture notes
- [server-computation-model.md](server-computation-model.md) - **CRITICAL**: What server COMPUTES vs RELAYS (2026-02-23)
- [object-recovery-protocol.md](object-recovery-protocol.md) - Opcodes 0x1D/0x1E/0x1F: ObjNotFound/RequestObj/EnterSet (2026-02-24)
- [crash-analysis.md](crash-analysis.md) - InitNetwork crash chain
- [ebp-corruption-crash.md](ebp-corruption-crash.md) - EBP/RunPyCode crash (SOLVED)
- [transport-layer.md](transport-layer.md) - FULL transport layer: 7 factory types, wire formats, fragments
- [complete-opcode-table.md](complete-opcode-table.md) - FULL verified opcode table (41 + Python)
- [main-loop-timing.md](main-loop-timing.md) - Main loop architecture, NiApp vtable, clock sources
- [hardpoint-property-system.md](hardpoint-property-system.md) - COMPLETE: AddToSet, SetupProperties, CT_ type IDs
- [ghidra-naming-passes.md](ghidra-naming-passes.md) - Function naming passes 5-9D (Phase 9D: vtable audit, 3 renames + major doc fixes, ~6973 named, ~38.2%)
- [subsystem-vtable-map.md](subsystem-vtable-map.md) - Phase 8E: subsystem class hierarchy, 19 vtable addresses, 30-slot map
- [weapon-class-hierarchy.md](weapon-class-hierarchy.md) - Phase 8J: weapon/projectile class hierarchy (86 renames)
- [ui-class-hierarchy.md](ui-class-hierarchy.md) - Phase 8D: UI system classes (135 renames)
- [function-map-validation-20260528.md](function-map-validation-20260528.md) - v5 validation: doc partition is exact (+0 in 18/20 cats, +1 in Cat 9 & 17); 18,249 in-body funcs (doc:18,247); Unwind=4692 EXACT

## TGObjPtrEvent System (2026-02-21, COMPLETE)
- See [docs/protocol/tgobjptrevent-class.md](../../docs/protocol/tgobjptrevent-class.md)
- Factory 0x010C, ctor 0x00403290, vtable 0x0088869C, size 0x2C, +0x28 = obj_ptr (TGObject ID)
- Key types: ET_SUBSYSTEM_HIT(0x6B), ET_WEAPON_FIRED(0x7C), ET_STOP_FIRING_NOTIFY(0xDC)

## Hardpoint/Property System (2026-02-21, COMPLETE)
- Properties attached via `AddToSet("Scene Root", prop)` — flat, order-independent
- SetupProperties (0x005b3fb0): switch on CT_ type ID (0x812b-0x813f) creates subsystem objects
- Parent-child is TYPE-BASED not order-based: LinkAllSubsystemsToParents walks list, checks IsA
- Weapons: IsA 0x802a, then GetType -> 0x802c(phaser)->ship+0x2B8, 0x802d(pulse)->+0x2BC, 0x802e(tractor)->+0x2D4, 0x802f(torpedo)->+0x2B4
- WST_ enum: 0=UNKNOWN, 1=PHASER, 2=TORPEDO, 3=PULSE, 4=TRACTOR
- IsPrimary (+0x26): determines if subsystem gets ship primary pointer (last-wins if multiple)
- PowerProperty: one per ship in practice; multiple would overwrite ship+0x2C4

## TGMessage Routing (2026-02-17)
- See [docs/protocol/tgmessage-routing.md](../../docs/protocol/tgmessage-routing.md) for FULL analysis
- TWO SEPARATE TYPE SYSTEMS: Transport types (7 registered, 256 max) vs Game opcodes (payload)
- RELAY-ALL: Host forwards ALL messages opaquely (no whitelist, no type inspection)
- Star topology; MAX_MESSAGE_TYPES=0x2B(43); Python types: CHAT=0x2C, SCORE=0x37, END_GAME=0x38

## RTTI / Type System
- NO MSVC RTTI (/GR-); NiRTTI hash table at DAT_009a2b98; 117 factory registrations; ~670 classes
- Full catalogs: [docs/engine/rtti-class-catalog.md], [docs/engine/nirtti-factory-catalog.md]

## NI 3.1 Vtable Layout (CRITICAL)
- See [docs/engine/netimmerse-vtables.md](../../docs/engine/netimmerse-vtables.md)
- Slot 0 = GetRTTI (NOT dtor); slot 10 = dtor (+0x28)
- NiObject:12 | NiObjectNET:12 | NiAVObject:39 | NiNode:43 | NiGeometry:64 | NiTriShape:68

## TG Hierarchy Vtable Layout (Phase 8B, updated Phase 9D)
- See [docs/engine/tg-hierarchy-vtables.md](../../docs/engine/tg-hierarchy-vtables.md)
- **DIFFERENT from NiObject**: TG slot 0 = scalar_deleting_dtor (NOT GetRTTI)
- Ship does NOT inherit from NiObject; chain: TGObject->TGStreamedObject->TGStreamedObjectEx->TGEventHandlerObject->TGSceneObject->ObjectClass->PhysicsObjectClass->DamageableObject->Ship
- **TGObject vtable at 0x00896278** (NOT 0x008963BC which was wrong — that's TGHashTable or similar)
- Ship vtable at 0x00894340, 92 slots (0x170 bytes), object size 0x328
- **CORRECTED**: DamageableObject ALSO has 92 slots; Ship does NOT add extra slots (both 92)
- TG universal slot pattern: slot 1=GetTypeID(), slot 2=IsTypeID(int), slot 9=GetClassName(), slot 10=GetSwigTypeName(), slot 11=GetObjectPtrTypeName()
- Key slots: 4/5=Write/ReadFromStream, 20=HandleEvent, 21=Update, 70=InitObject (DamageableObject__InitObject=0x005a2030), 72/73=Write/ReadStateUpdate, 80=RayIntersect, 82=CollisionTest_A, 84=CheckCollision, 85=ApplyCollisionDamage(DO)/CollisionDamageWrapper(Ship), 88/89=SetupProperties/LinkSubsystems, 90-91=dtors
- 23 functions renamed across 8 TG hierarchy classes in Phase 8B; major slot corrections in Phase 9D

## CRITICAL FLAGS
- 0x0097FA88=IsClient(0=host), 0x0097FA89=IsHost(1=host), 0x0097FA8A=IsMultiplayer

## Main Loop & Timing (2026-02-20, COMPLETE)
- See [main-loop-timing.md](main-loop-timing.md) for full details
- PeekMessage busy loop (NiApplication pattern), NO Sleep in main loop
- NiClock at 0x0099c6b0: timeGetTime() * 0.001f, optional QPC
- Frame rate limiter (1/60) only gates rendering, NOT game logic
- Stock dedicated = 100% CPU busy loop; our proxy = SetTimer ~60Hz
- Frame budget scheduler (FUN_0046f420): 4 priority tiers, round-robin

## Power Distribution (2026-02-18)
- NO dedicated network message; propagates via StateUpdate 0x1C flag 0x20
- Sign bit encoding: negative byte = subsystem OFF; 1% resolution, 0-125% range
- See [docs/gameplay/power-system.md] for full analysis

## Power Mode Assignments (2026-02-21, COMPLETE)
- PoweredSubsystem+0xA0 = powerMode: 0=main-first, 1=backup-first, 2=backup-only
- CloakingSubsystem: mode 2 (backup-only); TractorBeamSystem: mode 1 (backup-first); all others: mode 0

## 0x1C State Update & Subsystem Wire Format (2026-02-18)
- See [docs/protocol/stateupdate-subsystem-wire-format.md](../../docs/protocol/stateupdate-subsystem-wire-format.md)
- Flag 0x20 = round-robin subsystem health; linked list order (no fixed index)
- 3 WriteState variants: Base(0x0056d320), PoweredSS(0x00562960), PowerSS(0x005644b0)
- 10-byte budget per tick; Sovereign has 11 top-level (not 33)
- OpenBC parity note (2026-02-26): `server_dispatch.c` relays client `0x1C` payload bytes unchanged (unreliable) except pure `dirty==0x20` is dropped; server-auth health `0x20` is regenerated via `bc_ship_build_health_update` from `ser_list`.

## Client Join Sequence
- 0x00 (settings) -> 0x01 (GameInit) -> 0x35 (MISSION_INIT) -> 0x37 (SCORE)

## Multiplayer Mission Infrastructure (2026-02-21, COMPLETE)
- See [docs/architecture/multiplayer-mission-infrastructure.md](../../docs/architecture/multiplayer-mission-infrastructure.md)
- TWO network groups: "NoMe" (all except self) and "Forward" (all)
- MultiplayerGame ctor (0x0069e590): 16 player slots (0x18 bytes each at +0x74)
- Player slot: +0x04=active, +0x08=connID, +0x10=baseObjID (N*0x40000+0x3FFFFFFF)
- maxPlayers at +0x1FC, readyForNewPlayers at +0x1F8

## Memory Allocator
- FUN_00717840=NiAlloc (4-byte size header), FUN_00717960=NiFree, FUN_007179c0=NiRealloc
- Small allocs (<=0x80) use pool; large use CRT malloc; [ptr-4] corruption = fatal

## TGObject ID System (2026-02-20)
- ALL game objects (ships, subsystems, events) inherit from TGObject (FUN_006f0a70)
- `obj+0x04` = unique network object ID, auto-assigned from global counter DAT_0095b078
- `DAT_0099a67c` = global hash table: objectID -> object pointer
- `FUN_006f0ee0` = hash lookup by ID (returns object ptr or NULL)
- Subsystem IDs are NOT derived from ship base ID; they are sequential from global counter
- See [docs/gameplay/repair-event-object-ids.md](../../docs/gameplay/repair-event-object-ids.md)

## TGEvent System (2026-02-20, EXPANDED 2026-02-24)
- TGEvent (0x28 bytes): +0x08=source, +0x0C=dest, +0x10=eventType
- TGCharEvent (0x2C bytes, factory 0x10C): +0x28=charData
- TGEventManager (0x0097f838): singleton, PostEvent -> ProcessEvent + broadcast
- See [ghidra-naming-passes.md](ghidra-naming-passes.md) Pass 8C for complete function table

## Key Functions
| Address | Name | Role |
|---------|------|------|
| 0x006a1b10 | ChecksumCompleteHandler | Sends 0x00 + 0x01 |
| 0x006a1e70 | NewPlayerInGameHandler | InitNetwork + replicates objects |
| 0x00504c10 | MW::ReceiveMessageHandler | Client: dispatches 0x00/0x01/0x16 |
| 0x0069f620 | MP game object processor | Deserializes game objects from network |
| 0x006d1e10 | TGLFile::FindEntry | NULL this -> patched |
| 0x005b17f0 | Ship_WriteStateUpdate | Pos/orient/subsys/weapons to stream |
| 0x005b21c0 | Ship_ReadStateUpdate | Receives state update |
| 0x005b3e20 | Ship_LinkAllSubsystemsToParents | Moves children from 0x284 to parents |
| 0x005b5030 | Ship_LinkSubsystemToParent | Identifies parent, AddChild |
| 0x006b4c10 | TGNetwork::SendTGMessage | __thiscall(this, targetID, msg, opt) |
| 0x006b4560 | TGWinsockNetwork::Update | Main loop: send/receive/events |
| 0x0069e590 | MultiplayerGame ctor | "NoMe"/"Forward" groups, all handlers |
| 0x0043b4f0 | UtopiaApp::MainTick | Clock, timers, events, scheduler, scene |
| 0x006cdd20 | UtopiaApp::OnIdle | UpdateTime, frame limiter, sound, states |
| 0x007b8790 | NiApp::Process | PeekMessage loop (NOT overridden by BC) |
| 0x0071a9e0 | NiClock::Update | timeGetTime/QPC delta computation |
| 0x006dc490 | TGTimerManager::Update | Walk sorted timer list, fire expired |
| 0x0046f420 | FrameBudgetScheduler | 16-sample ring, 4 priority tiers |
| 0x00504d30 | SettingsHandler (0x00) | Parse game settings, mission name, clock sync |
| 0x00504f10 | CreateMultiplayerGame (0x01) | AI.Setup.GameInit + MPGame ctor + mission load |
| 0x0069ebb0 | MultiplayerGame dtor | Cleanup groups, handlers |
| 0x0069efc0 | InitializeAllSlots | Loop 0-15, init player slots |
| 0x0069efe0 | RegisterHandlerNames | Debug names for 29 handlers |
| 0x006a0080 | ExplosionHandler (0x29) | AoE damage: objID+CompVec4+CF16+CF16 |
| 0x006a01b0 | HostMsgHandler (0x13) | Self-destruct via PowerSubsystem |
| 0x0050d070 | TopWindow::SelfDestructHandler | Ctrl+D handler: SP/host=direct, client=send 0x13 |
| 0x005af5f0 | DoDamageToSelf | __thiscall(ship*, powerSS*): maxHP damage to reactor |
| 0x005af4a0 | DoDamageToSelf_Inner | Actual damage: force_kill, GodMode gate, cascade |
| 0x005afea0 | ShipDeathHandler | Fires ET_OBJECT_EXPLODING (0x0080004E) after death |
| 0x0056c310 | GetMaxHP | __fastcall(ss*): reads property+0x20 via ss+0x18 |
| 0x0056c330 | IsDead | __fastcall(ss*): reads death flag at property+0x24 |
| 0x0056c470 | SetCondition | __thiscall(ss*, float): set HP, fire SUBSYSTEM_HIT |
| 0x006a05e0 | EnterSetHandler (0x1F) | Map/set transition |
| 0x006a1150 | HostEventHandler | Serialize event -> "NoMe" group |
| 0x006a1240 | ObjectExplodingHandler | MP: forward to "NoMe"; SP: apply visual |
| 0x006a7770 | InitPlayerSlot | Set baseObjID=N*0x40000+0x3FFFFFFF |
| 0x006b4de0 | SendTGMessageToGroup | Send to named group |
| 0x006b70d0 | TGNetwork_AddGroup | Create/register network group |
| 0x006f8490 | ImportAndGetAttr | Import Python module + getattr |
| 0x006f8650 | GetPythonVariable | Read Python var into C |
| 0x006f8ab0 | TG_CallPythonFunction | Call Python function from C++ |

## Solved Crashes & Fixes (see topic files)
- TGL FindEntry NULL: [tgl-null-crash.md]; Compressed vector: [compressed-vector-crash.md]
- Boot player: [boot-player-analysis.md]; InitNetwork dupes: [initnet-duplicates.md]
- Collision damage: [collision-damage.md]; Ship+0x140 NULL: [ship-0x140-analysis.md]

## Key Pipelines (see topic files)
- Renderer: [renderer-pipeline-analysis.md]; NIF: [nif-loading-pipeline.md]
- Ship creation: [ship-creation-callchain.md]; Subsystems: [subsystem-creation-analysis.md]
- Ship Creation: FUN_0069f620 -> FUN_005a1f50 -> FUN_005b0e80 (vtable, InitObject)

## GameSpy & LAN Discovery (2026-02-16)
- Game "bcommander", key "Nm3aZ9"; LAN: UDP `\status\` to 255.255.255.255:22101-22201
- See [docs/networking/gamespy-discovery.md], [docs/networking/gamespy-crypto-analysis.md]

## Self-Destruct Pipeline (2026-02-21, COMPLETE)
- See [docs/gameplay/self-destruct-pipeline.md](../../docs/gameplay/self-destruct-pipeline.md)
- Ctrl+D -> opcode 0x13 -> DoDamageToSelf(0x005af5f0) -> PowerSubsystem maxHP damage

## Game Flow Class Hierarchy (2026-02-24, COMPLETE)
- PlayWindow = "Game" in SWIG (g_TopWindow), vtable 0x008887e8, +0x54=playerShip, +0x60=godMode
- PlayWindow -> MultiplayerGame (vtable 0x0088b480)
- TWO PlayWindow classes: PlayWindow(0x00405c10)=game state vs PlayViewWindow(0x004fc480)=UI

## Cut Content (2026-02-16)
- See [docs/analysis/cut-content-analysis.md](../../docs/analysis/cut-content-analysis.md)
- TestMenuState=2: debug cheats. Self-destruct (Ctrl+D). Tractor docking (6 modes). Opcodes 0x04/0x05 dead.

## Combat Systems (2026-02-17, see docs/)
- **Repair**: [docs/gameplay/repair-tractor-analysis.md] - NO queue limit (OpenBC wrong); multi-team simultaneous
- **Tractor**: Same doc - multiplicative drag (OpenBC additive WRONG); NO direct damage; 6 modes
- **Weapons**: [docs/gameplay/weapon-firing-mechanics.md] - Phaser charge/discharge; torpedo reload/type-switch
- **Cloak**: [docs/gameplay/cloaking-state-machine.md] - States 0/2/3/5 (not 0/1/2/3); OpenBC WRONG
- **Shields**: [docs/gameplay/shield-system.md] - 6-facing ellipsoid; area vs directed absorption
- **Collision**: [docs/gameplay/collision-detection-system.md] - 3-tier; client-authoritative
- **CF16**: [docs/protocol/cf16-precision-analysis.md] - [sign:1][scale:3][mantissa:12]; BASE=0.001, MULT=10.0

## Fragmented Reliable ACK Bug (2026-02-19)
- See [docs/networking/fragmented-ack-bug.md](../../docs/networking/fragmented-ack-bug.md)
- All static code paths verified correct; bug requires runtime instrumentation
- ACK factory at 0x006bd1f0 (NOT in Ghidra func DB; decompiled via objdump)

## Ghidra Workarounds
- Some vtable entries NOT in Ghidra function DB; use objdump raw disasm
- `i686-w64-mingw32-objdump -d -M intel --start-address=X --stop-address=Y stbc.exe`
- DAT_0088b9c0 = 1.0 as DOUBLE (8 bytes); `fcomp QWORD PTR` reads double not float
- 0x0078xxxx = Python 1.5.2 Parser (NOT NIF): FUN_007840f0=PyNode_AddChild
