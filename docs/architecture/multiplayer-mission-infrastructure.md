> [docs](../README.md) / [architecture](README.md) / multiplayer-mission-infrastructure.md

# Multiplayer Mission/Gamemode C++ Infrastructure

Comprehensive reverse engineering of the C++ and Python infrastructure that supports
multiplayer mission selection, game initialization, scoring, and game flow.

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [MultiplayerGame Object Layout](#multiplayergame-object-layout)
3. [Game Startup Flow](#game-startup-flow)
4. [Settings Handler (Opcode 0x00)](#settings-handler-opcode-0x00)
5. [CreateMultiplayerGame (Opcode 0x01)](#createmultiplayergame-opcode-0x01)
6. [NewPlayerInGame (Opcode 0x2A)](#newplayeringame-opcode-0x2a)
7. [EnterSet (Opcode 0x1F)](#enterset-opcode-0x1f)
8. [Explosion Handler (Opcode 0x29)](#explosion-handler-opcode-0x29)
9. [HostEventHandler (Event Forwarding)](#hosteventhandler)
10. [ObjectExplodingHandler (Score Trigger)](#objectexplodinghandler)
11. [Python Mission Script Architecture](#python-mission-script-architecture)
12. [Python-Level Messages (0x35-0x39)](#python-level-messages)
13. [Network Groups ("NoMe" and "Forward")](#network-groups)
14. [Complete Event Registration Table](#event-registration-table)
15. [Mission Loading Chain](#mission-loading-chain)
16. [Scoring System](#scoring-system)
17. [EndGame / RestartGame Flow](#endgame--restartgame-flow)
18. [Key Addresses](#key-addresses)

---

## Architecture Overview

The multiplayer mission infrastructure is a **two-layer system**:

1. **C++ Layer** (engine): Handles network transport, object creation/destruction, state
   synchronization, collision detection, event dispatch, and the core game loop. The C++
   layer calls into Python at specific points via `TG_CallPythonFunction`.

2. **Python Layer** (scripts): Handles mission selection UI, scoring logic, game flow
   decisions (time/frag limits, end game, restart), and mission-specific setup (creating
   star systems, placing objects). Python sends custom messages (opcodes 0x2C-0x39) using
   `TGNetwork.SendTGMessage` / `SendTGMessageToGroup`.

The C++ layer is **mission-agnostic** -- it provides the infrastructure for any game mode.
All game-mode-specific logic lives in Python scripts under `scripts/Multiplayer/`.

### Message Flow Diagram

```
Host                                          Client
  |                                              |
  |-- [Checksum exchange, opcodes 0x20-0x28] --->|
  |                                              |
  |-- 0x00 Settings (gameTime, map, slot) ------>|  FUN_00504d30
  |-- 0x01 GameInit (single byte) -------------->|  CreateMultiplayerGame
  |                                              |
  |  (Both sides create MultiplayerGame object)  |
  |  (C++ calls AI.Setup.GameInit)               |
  |  (C++ calls g_kVarManager for mission name)  |
  |  (Episode.py loads the mission script)       |
  |                                              |
  |-- 0x35 MISSION_INIT (system, limits) ------->|  Python: InitNetwork()
  |-- 0x37 SCORE (per-player kills/deaths) ----->|  Python: InitNetwork()
  |-- 0x2A NewPlayerInGame (replicates objects)->|  FUN_006a1e70
  |                                              |
  |  (Client creates ship, enters gameplay)      |
  |                                              |
  |<= 0x06 PythonEvent (game events) ==========>|  Bidirectional via Forward group
  |<= 0x07-0x12 Action events =================>|  Weapons, cloak, repair, etc.
  |<= 0x15 CollisionEffect ===================>|  Host -> all
  |<= 0x29 Explosion =========================>|  Host -> all
  |                                              |
  |-- 0x36 SCORE_CHANGE (kill notification) ---->|  Python: ObjectKilledHandler
  |-- 0x38 END_GAME (reason code) -------------->|  Python: EndGame()
  |-- 0x39 RESTART_GAME ----------------------->|  Python: RestartGameHandler
```

---

## MultiplayerGame Object Layout

The MultiplayerGame class (vtable at `PTR_FUN_0088b480`) inherits from Game. Key fields:

| Offset | Type | Name | Description |
|--------|------|------|-------------|
| +0x00 | vtable* | vtable | Points to 0x0088b480 |
| +0x70 | ptr | episodePtr | Current episode (->+0x3C->+0x14 = mission script name) |
| +0x74 | struct[16] | playerSlots | Array of 16 player slot structs (0x18 bytes each) |
| +0x78 | byte | slot[0].active | 1 if slot is occupied |
| +0x7C | int | slot[0].connID | Connection/peer ID |
| +0x80-0x8B | ... | slot[0].other | Other per-slot data |
| +0x8C | byte | slot[1].active | ... repeats for slots 1-15 |
| +0x1F8 | byte | readyForNewPlayers | 1 = accepting connections |
| +0x1FC | int | maxPlayers | Capped at 16 in constructor |

**Player slot structure** (0x18 bytes per slot, starts at +0x74):
```
+0x00: byte  inGameFlag (at MPGame+0x74 + N*0x18)  -- becomes slot[N].active
+0x04: byte  active
+0x08: int   connID     (at MPGame+0x7C + N*0x18)
+0x0C-0x14: other data
```

The constructor at `FUN_0069e590` initializes all 16 slots via `FUN_006a7770`:
```c
// FUN_006a7770: Initialize player slot
this->inGameFlag = 1;     // +0x14 -- "initialized" marker
this->active = 0;         // +0x04
this->connID = 0;         // +0x08
this->... = 0;            // +0x0C
this->baseObjectID = param_1 * 0x40000 + 0x3FFFFFFF;  // +0x10
```

**Object ID allocation**: Each slot N gets base ID `0x3FFFFFFF + N * 0x40000` (262,143 IDs per slot).

---

## Game Startup Flow

### Phase 1: Checksum Complete -> Settings + GameInit

When checksums pass, `ChecksumCompleteHandler` (0x006a1b10) fires on the host:

```
ChecksumCompleteHandler(this=MultiplayerGame, param_1=event)
  1. Find player slot for connecting peer (FUN_006a19c0)
  2. Load "data/TGL/Multiplayer.tgl" for checksum validation
  3. Check if connecting player's files match existing players
  4. Build Settings packet (opcode 0x00):
     - WriteFloat: gameTime (from g_Clock+0x90)
     - WriteByte:  g_SettingsByte1 (0x008e5f59)
     - WriteByte:  g_SettingsByte2 (UtopiaModule+0xB4)
     - WriteByte:  playerSlotIndex
     - WriteShort: mapName length
     - WriteBytes: mapName (mission script path)
     - WriteByte:  checksumFlag
     - [if flag: checksum match data]
  5. Send Settings to connecting peer (reliable)
  6. Build GameInit packet (opcode 0x01):
     - Single byte: 0x01
  7. Send GameInit to connecting peer (reliable)
```

### Phase 2: Client Processes Settings (0x00)

`FUN_00504d30` (MultiplayerWindow dispatcher):

```c
void __thiscall FUN_00504d30(this=MultiplayerWindow, param_1=messageData)
{
    // Parse stream from message
    float gameTime = ReadFloat(stream);
    g_Clock->gameTime = gameTime;                    // +0x90 = game clock sync

    byte settingsByte1 = ReadByte(stream);
    g_SettingsByte1 = settingsByte1;                 // 0x008e5f59

    byte settingsByte2 = ReadByte(stream);
    this->+0xB4 = settingsByte2;                     // collision setting

    byte playerSlot = ReadByte(stream);
    DAT_0097fa84 = (int)(char)playerSlot;            // My player slot number
    DAT_0097fa8c = playerSlot * 0x40000 + 0x3FFFFFFF; // My base object ID

    short mapNameLen = ReadShort(stream);
    if (mapNameLen > 0) {
        ReadBytes(stream, mapName, mapNameLen);
        mapName[mapNameLen] = '\0';
        // Store mission name as "Multiplayer"/"Mission"/mapName
        FUN_0044b500(&DAT_00980228, "Multiplayer", "Mission", mapName);
    }

    // Load "Synchronizing Game Data" status text from TGL
    TGLManager_LoadFile("data/TGL/Multiplayer.tgl");

    // Update status UI
    FUN_005054b0();  // Updates multiplayer status pane text

    // Handle checksum data if present
    byte checksumFlag = ReadByte(stream);
    if (checksumFlag != 0) {
        // Process checksum match data
        FUN_006b4a50(g_TGWinsockNetwork, checksumMatchData);
    }
}
```

**Key discovery**: The mission name (e.g. "Mission1.Mission1") is communicated via the
Settings packet's map name field. It gets stored via `FUN_0044b500` which calls
`g_kVarManager.SetStringVariable("Multiplayer", "Mission", mapName)`.

### Phase 3: Client Processes GameInit (0x01) -> CreateMultiplayerGame

`CreateMultiplayerGame` (0x00504f10):

```c
void CreateMultiplayerGame(void)
{
    // 1. Call Python: AI.Setup.GameInit()
    //    This preloads all AI scripts (73 modules) to avoid hitching
    TG_CallPythonFunction("AI.Setup", "GameInit", NULL, 0, NULL);

    // 2. Allocate and construct MultiplayerGame object
    //    "Multiplayer.MultiplayerGame" is the Python module path
    void* pMPGame = new MultiplayerGame("Multiplayer.MultiplayerGame", 0x10);

    // 3. If multiplayer, read g_iPlayerLimit from Python config
    if (g_IsMultiplayer) {
        int playerLimit = 0x10;  // default 16
        FUN_006f8650("Multiplayer.MissionMenusShared", "g_iPlayerLimit",
                     &DAT_008d8804, &playerLimit);
        FUN_00753140();          // Additional Python setup
        pMPGame->maxPlayers = playerLimit;  // +0x1FC
    }

    // 4. Load "Connection Completed" status text from TGL
    TGLManager_LoadFile("data/TGL/Multiplayer.tgl");

    // 5. Update status UI
    FUN_005054b0();
}
```

**Key discoveries**:
- `TG_CallPythonFunction("AI.Setup", "GameInit", ...)` is the FIRST Python call during game start
- The `MultiplayerGame` constructor (0x0069e590) is called with module path `"Multiplayer.MultiplayerGame"` and max=0x10 (16)
- The actual player limit is read from `Multiplayer.MissionMenusShared.g_iPlayerLimit` Python variable
- This triggers Python `MultiplayerGame.Initialize(pGame)` which loads the Episode

---

## MultiplayerGame Constructor (0x0069e590)

The constructor performs extensive setup:

```c
MultiplayerGame* __thiscall FUN_0069e590(this, scriptPath, maxPlayers)
{
    FUN_00405c10(this, scriptPath);    // Base Game constructor

    // Initialize 16 player slot arrays
    FUN_00859d64(this+0x74, 0x18, 0x10, FUN_006a7720);

    this->vtable = &PTR_FUN_0088b480;

    if (maxPlayers > 16) maxPlayers = 16;
    this->maxPlayers = maxPlayers;     // +0x1FC

    // Register C++ event handlers with TGEventManager
    // Event ID -> Handler name (all are method pointers on this object)
    RegisterHandler(0x60001, "MultiplayerGame :: ReceiveMessage");       // Network messages
    RegisterHandler(0x60003, "MultiplayerGame :: DisconnectHandler");    // Player disconnect
    RegisterHandler(0x60004, "MultiplayerGame :: NewPlayerHandler");     // New player detected
    RegisterHandler(0x60005, "MultiplayerGame :: DeletePlayerHandler");  // Player deleted
    RegisterHandler(0x008000C8, "MultiplayerGame :: ObjectCreatedHandler"); // Object created

    if (g_IsMultiplayer) {
        g_SettingsByte1 = DAT_008e5f58;    // Initialize settings

        // CREATE NETWORK GROUPS (on TGWinsockNetwork)
        // Group 1: "NoMe" (DAT_008e5528) -- all peers except self
        CreateGroup("NoMe");               // FUN_006b70d0
        // Group 2: "Forward" -- all peers (for relay)
        CreateGroup("Forward");            // FUN_006b70d0

        // Register HOST-ONLY event handlers
        RegisterHandler(0x008000DF, "MultiplayerGame :: HostEventHandler");  // AddToRepairList
        RegisterHandler(0x00800074, "MultiplayerGame :: HostEventHandler");  // Unknown event
        RegisterHandler(0x00800075, "MultiplayerGame :: HostEventHandler");  // Unknown event
        RegisterHandler(0x008000E8, "MultiplayerGame :: SystemChecksumPassedHandler");
        RegisterHandler(0x008000E7, "MultiplayerGame :: SystemChecksumFailedHandler");
        RegisterHandler(0x008000E6, "MultiplayerGame :: ChecksumCompleteHandler");
        RegisterHandler(0x0080005D, "MultiplayerGame :: EnterSetHandler");
        RegisterHandler(0x008000C5, "MultiplayerGame :: ExitedWarpHandler");
    }

    // Register handlers for ALL modes (SP and MP)
    RegisterHandler(0x0080004E, "MultiplayerGame :: ObjectExplodingHandler");
    RegisterHandler(0x008000F1, "MultiplayerGame :: NewPlayerInGameHandler");
    RegisterHandler(0x008000D8, "MultiplayerGame :: StartFiringHandler");
    RegisterHandler(0x008000DA, "MultiplayerGame :: StopFiringHandler");
    RegisterHandler(0x008000DC, "MultiplayerGame :: StopFiringAtTargetHandler");
    RegisterHandler(0x008000DD, "MultiplayerGame :: SubsystemStatusHandler");
    RegisterHandler(0x00800076, "MultiplayerGame :: RepairListPriorityHandler");
    RegisterHandler(0x008000E0, "MultiplayerGame :: SetPhaserLevelHandler");
    RegisterHandler(0x008000E2, "MultiplayerGame :: StartCloakingHandler");
    RegisterHandler(0x008000E4, "MultiplayerGame :: StopCloakingHandler");
    RegisterHandler(0x008000EC, "MultiplayerGame :: StartWarpHandler");
    RegisterHandler(0x008000FE, "MultiplayerGame :: TorpedoTypeChangeHandler");

    if (!g_IsMultiplayer) {
        RegisterHandler(0x00800058, "MultiplayerGame :: ChangedTargetHandler");
    }

    // Initialize all 16 player slots
    FUN_0069efc0(this);  // Loops 0-15, calls FUN_006a7770 per slot

    // If client, send NewPlayerInGame event to self
    if (g_IsMultiplayer && g_IsClient) {
        TGEvent* evt = new TGEvent();
        evt->eventType = 0x008000F1;    // ET_NEW_PLAYER_IN_GAME
        evt->charData = WSN->localID;   // +0x20 = my connection ID
        evt->SetDest(this);
        PostEvent(evt);
        this->+0x78 = 1;               // Mark self as active
        this->+0x7C = WSN->localID;    // Store my connection ID
    }

    this->readyForNewPlayers = 0;       // +0x1F8

    // Reset IsHost flag temporarily to process pending events
    g_IsHost = 0;
    while (DAT_0097FA3C > 0) {
        FUN_0043bbd0(&g_UtopiaModule, 0);  // Process pending actions
    }
    g_IsHost = 1;

    if (g_IsMultiplayer) {
        settingsPane->+0xB4 = g_SettingsByte2;  // Copy collision setting
    }
}
```

**Key discoveries**:
- TWO network groups are created: **"NoMe"** (0x008e5528) and **"Forward"** (0x008d94a0)
- "NoMe" = all peers except self (used for score broadcasts)
- "Forward" = all peers including self (used for event relay)
- Host registers 8 additional event handlers that clients don't get
- The constructor temporarily clears `g_IsHost` to process pending actions, then restores it

---

## NewPlayerInGame (Opcode 0x2A)

`Handler_NewPlayerInGame_0x2A` (0x006a1e70) -- the most complex handler:

```c
void __thiscall Handler_NewPlayerInGame_0x2A(this=MultiplayerGame, param_1=message)
{
    if (!g_TGWinsockNetwork || !g_IsMultiplayer) return;

    int connID = message->+0x0C;           // Source connection ID
    int slotIdx = FindPlayerSlot(this, connID);  // FUN_006a19c0

    // Parse stream
    byte teamByte = ReadByte(stream);
    this->playerSlots[slotIdx].team = teamByte;  // +0x88 + slotIdx*0x18

    // 1. FIRE ET_NEW_PLAYER_IN_GAME EVENT (0x008000F1)
    TGEvent* evt = new TGCharEvent();
    evt->eventType = 0x008000F1;
    evt->charData = connID;
    evt->SetDest(this);
    PostEvent(evt);

    // 2. CALL PYTHON: mission.InitNetwork(connID)
    //    Gets mission script path from: this->+0x70->+0x3C->+0x14
    char* missionScript = *(this->episodePtr->+0x3C->+0x14);
    TG_CallPythonFunction(missionScript, "InitNetwork", &connID, "i");
    //    This is how scores and mission config get sent to new players!

    // 3. REPLICATE ALL EXISTING GAME OBJECTS
    for each set in DAT_0097e9c8 (set list):
        for each object in set:
            if (object->+0xEC != 0):  // Has network data
                // Check if object is alive
                ship = GetShipWrapper(object);
                if (ship == NULL || (ship->health >= threshold && !ship->isDead)):
                    // Build ObjCreate message
                    byte opcode = 2;  // ObjCreate
                    if (HasOwningPlayer(object)):                     // IsLocalPlayerShip-style check
                        opcode = 3;   // ObjCreateTeam (historical name)
                        // Include net_player_id byte from ship->+0x2E4
                        // [v5-correction 2026-05-29: was "team byte"; the
                        //  byte stored at ship+0x2E4 is the owning player's
                        //  NetPlayerID, not a team-membership tag. Stock BC
                        //  has no C++ team field. AI ships have +0x2E4 == 0.
                        //  Source: gamemode-system-validation-20260529 memo.]
                    byte playerSlot = GetSlotFromObjectID(object->objID);
                    // Call object->vtable+0x10C (WriteToStream)
                    int dataLen = object->WriteToStream(buffer+opcode_size, 0x400-opcode_size);

                    // Build and send message
                    TGMessage* msg = new TGHeaderMessage();
                    BufferCopy(msg, buffer, opcode_size + dataLen);
                    msg->reliable = 1;
                    msg->preserveOrder = 0;  // +0x3D = 0 (no ordering)
                    SendTGMessage(g_TGWinsockNetwork, connID, msg, 0);

                // Also check if object has type 0x8007 and send supplements
                if (object->IsTypeOf(0x8007)):
                    FUN_00595c60(object, connID);  // Send supplemental data

    // 4. ADD connID TO "NoMe" GROUP
    //    Binary search for "NoMe" in group list, add connID sorted
    AddToGroup("NoMe", connID);

    // 5. ADD connID TO "Forward" GROUP
    AddToGroup("Forward", connID);
}
```

**Key discoveries**:
- `InitNetwork` is called as a Python function on the **mission script** (e.g. `Multiplayer.Episode.Mission1.Mission1.InitNetwork(connID)`)
- Object replication sends opcode 0x02 or 0x03 depending on whether the object has a team
- After replication, the new player's connID is added to BOTH "NoMe" and "Forward" groups
- Objects are only replicated if they have network data (+0xEC != 0) and are alive
- The `preserveOrder` flag is set to 0 for object replication (not ordered)

---

## EnterSet (Opcode 0x1F)

`FUN_006a05e0` -- handles a player entering a game set (map area):

```c
void FUN_006a05e0(void* param_1)
{
    if (!g_TGWinsockNetwork) return;

    // Parse: objectID (int) + setName (string)
    int objectID = ReadInt(stream);
    char* setName = ReadString(stream, -1);  // FUN_006d2370

    // Find the object
    TGObject* obj = FindObjectByID(NULL, objectID);  // FUN_00434e00

    if (obj == NULL) {
        // Object not found locally -- RELAY the message to all peers
        // Build a new message with opcode 0x1F prepended
        TGMessage* msg = new TGHeaderMessage();
        msg->reliable = 1;
        SendTGMessage(g_TGWinsockNetwork, 0, msg, 0);  // 0 = broadcast
    }
    else {
        // Object found -- perform set transition
        ship = GetShipWrapper(obj);
        if (ship != NULL && ship->+0x2D0 != 0 && *(ship->+0x2D0 + 0xB4) == 0) {
            // Look up set by name in set list (DAT_0097e9c8)
            TGSet* destSet = FindSetByName(setName);

            // Current set
            TGSet* curSet = ship->+0x20;

            if (curSet != destSet) {
                // Remove from current set
                if (curSet != NULL) {
                    curSet->vtable+0x58(ship->objID);  // RemoveObject
                }
                // Add to destination set
                destSet->vtable+0x54(ship, ship->+0x28);  // AddObject
            }
        }
    }

    FreeString(setName);
}
```

**Key discoveries**:
- EnterSet handles map/set transitions for multiplayer
- If the object isn't found locally, the message is **relayed** to all peers (host acts as relay)
- Set transitions involve removing from current set and adding to destination set via vtable calls

---

## Explosion Handler (Opcode 0x29)

`Handler_Explosion_0x29` (0x006a0080) -- server-to-client explosion damage:

```c
void Handler_Explosion_0x29(void* param_1)
{
    // Parse stream
    int objectID = ReadInt(stream);

    // Find target ship
    int* ship = FindShipByID(NULL, objectID);  // FUN_00590a50

    if (ship != NULL) {
        // Read explosion position (compressed 3-vector)
        ReadCompressedVector4(stream, &x, &y, &z, true);

        // Read explosion radius (CF16 encoded)
        ushort rawRadius = ReadShort(stream);
        float radius = DecompressCF16(rawRadius);     // FUN_006d3b30

        // Read explosion damage (CF16 encoded)
        ushort rawDamage = ReadShort(stream);
        float damage = DecompressCF16(rawDamage);     // FUN_006d3b30

        // Create AoE damage object (0x38 bytes)
        AoEDamage* aoe = new AoEDamage(position, radius, damage);

        // Apply damage
        ProcessDamage(ship, aoe);  // Same ProcessDamage as collision/weapon paths
    }
}
```

**Key discoveries**:
- Explosion is a **server-to-client only** message (opcode 0x29)
- Wire format: `[int:targetObjID] [CompressedVec4:position] [CF16:radius] [CF16:damage]`
- Uses the same `ProcessDamage` function (0x00593e50) as collision and weapon damage
- Both radius and damage are CF16-encoded (see `docs/cf16-explosion-encoding.md`)

---

## HostEventHandler

At 0x006a1150, this handler serializes local events and sends them to the "NoMe" group:

```asm
; HostEventHandler (0x006a1150)
; Registered for events: 0x008000DF (AddToRepairList), 0x00800074, 0x00800075
;
; Pseudocode:
;   buffer[0] = 0x06          ; PythonEvent opcode
;   event->WriteToStream(buffer+1, 0x3FF)
;   size = stream.GetPosition()
;   msg = new TGHeaderMessage()
;   BufferCopy(msg, buffer, size+1)
;   msg->reliable = 1
;   SendTGMessageToGroup(WSN, "NoMe", msg)    ; 0x006b4de0
```

The handler:
1. Writes opcode byte 0x06 (PythonEvent) to a buffer
2. Calls the event's `WriteToStream` virtual (vtable+0x34) to serialize the event data
3. Creates a TGHeaderMessage, copies the buffer in
4. Sends to the **"NoMe" group** (all peers except self) via `SendTGMessageToGroup`

---

## ObjectExplodingHandler

At 0x006a1240, handles the ET_OBJECT_EXPLODING event. Has two code paths:

**If IsMultiplayer:**
```
; Same pattern as HostEventHandler:
; buffer[0] = 0x06 (PythonEvent)
; event->WriteToStream(buffer+1, 0x3FF)
; msg->reliable = 1
; SendTGMessageToGroup(WSN, "NoMe", msg)
```

**If NOT IsMultiplayer (single player):**
```
; ship = GetShipWrapper(event->+0x0C)  // destination object
; if (ship != NULL):
;     ship->+0x14C = event->+0x2C      // Copy lifetime from event
;     FUN_005ac250(ship)                 // Trigger explosion visual
```

**Key discovery**: In multiplayer, ObjectExploding is **forwarded as a PythonEvent** to all
peers. This is what triggers the Python-level `ObjectKilledHandler` on the host, which then
computes scores and sends SCORE_CHANGE_MESSAGE.

---

## HostMsg Handler (Opcode 0x13)

`FUN_006a01b0` -- handles host-only messages (e.g., self-destruct):

```c
void FUN_006a01b0(int param_1)
{
    if (g_IsMultiplayer) {
        void* ship = GetShipFromPlayerID(*(param_1 + 0x0C));  // connID from message
        if (ship != NULL) {
            FUN_005af5f0(ship, ship->powerSubsystem);  // +0x2C4 = PowerSubsystem
            // This triggers self-destruct by overloading the power subsystem
        }
    }
}
```

---

## Python Mission Script Architecture

### Module Hierarchy

```
Multiplayer/
  __init__.py
  MultiplayerGame.py          # Game-level script (loaded by C++ constructor)
  MissionShared.py             # Common mission logic (message types, scoring, timers)
  MissionMenusShared.py        # Common UI (ship select, end game dialog, limits)
  SpeciesToShip.py             # Ship species -> model mapping
  SpeciesToSystem.py           # System species -> star system creation
  SpeciesToTorp.py             # Torpedo type mapping
  Modifier.py                 # Damage modifiers between ship classes
  Episode/
    Episode.py                 # Episode loader (reads "Mission" var, loads mission)
    Mission1/                  # Free-for-all deathmatch
      Mission1.py              # Main mission script
      Mission1Menus.py         # Mission-specific UI
      Mission1Name.py          # Display name
    Mission2/                  # Team deathmatch
    Mission3/                  # Cooperative vs AI
    Mission5/                  # Starbase defense
    ...
```

### Script Loading Chain

1. C++ `CreateMultiplayerGame` constructs the Game object with `"Multiplayer.MultiplayerGame"` as the script path
2. This triggers `MultiplayerGame.Initialize(pGame)`:
   - Loads tactical sounds
   - Loads alert sounds
   - Sets up music system
   - Calls `pGame.LoadEpisode("Multiplayer.Episode.Episode")`
3. `Episode.Initialize(pEpisode)`:
   - Reads mission name: `pcMissionScript = g_kVarManager.GetStringVariable("Multiplayer", "Mission")`
   - This returns the map name from the Settings packet (e.g., `"Mission1.Mission1"`)
   - Calls `pEpisode.LoadMission(pcMissionScript, pMissionStartEvent)`
4. The mission script (e.g., `Mission1.py`) `Initialize(pMission)`:
   - Calls `Multiplayer.MissionShared.Initialize(pMission)` for common setup
   - Sets up event handlers (ET_OBJECT_EXPLODING, ET_WEAPON_HIT, etc.)
   - On host: builds mission UI menus
   - Initializes scoring dictionaries

### Python -> C++ Bridge

`TG_CallPythonFunction` (0x006f8ab0) is the primary bridge:

```c
int TG_CallPythonFunction(
    byte* modulePath,      // Dotted module path (e.g., "Multiplayer.Episode.Mission1.Mission1")
    char* functionName,    // Function name (e.g., "InitNetwork")
    byte* formatString,    // Python argument format (e.g., "i" for int)
    int   argPtr,          // Pointer to arguments
    char* typeString       // Optional type validation string
)
{
    FUN_0074bbf0(1);       // Acquire Python GIL

    // Import module and get function attribute
    PyObject* module = ImportModule(modulePath);
    PyObject* func = PyObject_GetAttrString(module, functionName);

    // Build args tuple if typeString provided
    PyObject* args = NULL;
    if (typeString && *typeString) {
        args = Py_BuildValue(typeString, argPtr, ...);
    }

    // Call the function
    int result = CallPythonFunction(func, formatString, argPtr, args, isAISetup, true);

    FUN_0074bbf0(0);       // Release Python GIL
    return result;
}
```

The `FUN_006f8490` helper does the module import + attribute lookup:
```c
PyObject* FUN_006f8490(char* modulePath, char* attrName)
{
    FUN_0074bbf0(1);       // Acquire GIL
    char* simpleName = FUN_006f7a00(modulePath);  // Extract leaf module name
    PyObject* module = TG_ImportModule(simpleName, false);
    PyObject* attr = PyObject_GetAttrString(module, attrName);
    FUN_0074bbf0(0);       // Release GIL
    return attr;
}
```

`FUN_006f8650` is the simpler "get Python variable" wrapper:
```c
void FUN_006f8650(char* modulePath, char* varName, char* format, int* outValue)
{
    PyObject* var = FUN_006f8490(modulePath, varName);
    FUN_006f8580(var, format, outValue);  // Parse Python value into C
}
```

---

## Python-Level Messages

These messages bypass the C++ dispatcher entirely. They are sent via
`TGNetwork.SendTGMessage` from Python and received via `ET_NETWORK_MESSAGE_EVENT`
handler in Python.

### Message Type Constants (from MissionShared.py)

```python
MISSION_INIT_MESSAGE  = App.MAX_MESSAGE_TYPES + 10   # 0x2B + 10 = 0x35
SCORE_CHANGE_MESSAGE  = App.MAX_MESSAGE_TYPES + 11   # 0x36
SCORE_MESSAGE         = App.MAX_MESSAGE_TYPES + 12   # 0x37
END_GAME_MESSAGE      = App.MAX_MESSAGE_TYPES + 13   # 0x38
RESTART_GAME_MESSAGE  = App.MAX_MESSAGE_TYPES + 14   # 0x39
```

Where `App.MAX_MESSAGE_TYPES` = 0x2B (43), matching the C++ jump table size.

### 0x35: MISSION_INIT_MESSAGE

**Sent by**: Host, in `Mission1.InitNetwork(iToID)`
**Sent to**: Specific connecting player
**Purpose**: Tell the client what mission config to use

Wire format:
```
[0x35]                              # 1 byte: message type
[byte: playerLimit]                 # max players
[byte: systemSpecies]              # star system index
[byte: timeLimit or 0xFF=none]     # time limit in minutes, 0xFF = no limit
[if timeLimit != 0xFF: int endTime] # absolute game time when match ends
[byte: fragLimit or 0xFF=none]     # frag limit, 0xFF = no limit
```

### 0x36: SCORE_CHANGE_MESSAGE

**Sent by**: Host, in `ObjectKilledHandler`
**Sent to**: "NoMe" group (all peers except host)
**Purpose**: Notify all players of a kill/death/score change

Wire format:
```
[0x36]                              # 1 byte: message type
[long: firingPlayerID]             # 0 if killed by AI
[if firingPlayerID != 0:
  [long: kills]                    # New kill count for killer
  [long: firingPlayerScore]        # New score for killer
]
[long: killedPlayerID]             # Who died
[long: deaths]                     # New death count for killed player
[byte: scoreUpdateCount]           # Number of additional score entries
[repeat scoreUpdateCount times:
  [long: playerID]
  [long: playerScore]
]
```

### 0x37: SCORE_MESSAGE

**Sent by**: Host, in `Mission1.InitNetwork(iToID)`
**Sent to**: Specific connecting player (one message per player in dictionary)
**Purpose**: Sync full score state to a newly joined player

Wire format:
```
[0x37]                              # 1 byte: message type
[long: playerID]                   # Whose score this is
[long: kills]                      # Kill count
[long: deaths]                     # Death count
[long: score]                      # Total score
```

### 0x38: END_GAME_MESSAGE

**Sent by**: Host, in `MissionShared.EndGame(iReason)`
**Sent to**: All peers (broadcast, targetID=0)
**Purpose**: Signal game over with reason code

Wire format:
```
[0x38]                              # 1 byte: message type
[int: reason]                      # END_ITS_JUST_OVER=0, END_TIME_UP=1,
                                   # END_NUM_FRAGS_REACHED=2, END_SCORE_LIMIT_REACHED=3,
                                   # END_STARBASE_DEAD=4, END_BORG_DEAD=5,
                                   # END_ENTERPRISE_DEAD=6
```

### 0x39: RESTART_GAME_MESSAGE

**Sent by**: Host, in `Mission1.RestartGameHandler`
**Sent to**: All peers (broadcast, targetID=0)
**Purpose**: Signal game restart

Wire format:
```
[0x39]                              # 1 byte: message type (no additional data)
```

---

## Network Groups

### "NoMe" Group (0x008e5528)

- Created by MultiplayerGame constructor
- Contains all peer connection IDs **except** the local player
- Used for score broadcasts (don't send yourself your own score update)
- Players are added in `Handler_NewPlayerInGame_0x2A` after object replication
- Players are removed in the destructor (`FUN_0069ebb0`)

### "Forward" Group (0x008d94a0)

- Created by MultiplayerGame constructor
- Contains **all** peer connection IDs including the local player
- Used by event relay handlers (0x006a1790 StartFiring, 0x006a18d0 StopFiring, etc.)
- Standard pattern: serialize event + send to "Forward" group

The groups are stored in the TGWinsockNetwork object at:
- `WSN+0xF4` = group array pointer
- `WSN+0xF8` = group count
- `WSN+0xFC` = group capacity

Each group is a sorted array of {name, memberList} entries, searched via binary search.

---

## Event Registration Table

Complete list of C++ event handlers registered by MultiplayerGame constructor:

| Event ID | Handler Name | Condition | Purpose |
|----------|-------------|-----------|---------|
| 0x60001 | ReceiveMessage | Always | Network message dispatch |
| 0x60003 | DisconnectHandler | Always | Player disconnect |
| 0x60004 | NewPlayerHandler | Always | New player detected |
| 0x60005 | DeletePlayerHandler | Always | Player removed |
| 0x008000C8 | ObjectCreatedHandler | Always | Object creation notification |
| 0x008000DF | HostEventHandler | MP only | AddToRepairList forwarding |
| 0x00800074 | HostEventHandler | MP only | Event forwarding |
| 0x00800075 | HostEventHandler | MP only | Event forwarding |
| 0x008000E8 | SystemChecksumPassedHandler | MP only | Checksum pass |
| 0x008000E7 | SystemChecksumFailedHandler | MP only | Checksum fail |
| 0x008000E6 | ChecksumCompleteHandler | MP only | All checksums done |
| 0x0080005D | EnterSetHandler | MP only | Set transition |
| 0x008000C5 | ExitedWarpHandler | MP only | Warp complete |
| 0x0080004E | ObjectExplodingHandler | Always | Object death/explosion |
| 0x008000F1 | NewPlayerInGameHandler | Always | Player join handshake |
| 0x008000D8 | StartFiringHandler | Always | Weapon fire start |
| 0x008000DA | StopFiringHandler | Always | Weapon fire stop |
| 0x008000DC | StopFiringAtTargetHandler | Always | Stop fire at target |
| 0x008000DD | SubsystemStatusHandler | Always | Subsystem toggle |
| 0x00800076 | RepairListPriorityHandler | Always | Repair priority |
| 0x008000E0 | SetPhaserLevelHandler | Always | Phaser intensity |
| 0x008000E2 | StartCloakingHandler | Always | Cloak engage |
| 0x008000E4 | StopCloakingHandler | Always | Cloak disengage |
| 0x008000EC | StartWarpHandler | Always | Warp engage |
| 0x008000FE | TorpedoTypeChangeHandler | Always | Torpedo type switch |
| 0x00800058 | ChangedTargetHandler | SP only | Target change (SP only) |

---

## Mission Loading Chain

Detailed call chain from game start to mission execution:

```
1. Host clicks "Start Game" in UI
   -> ET_START_GAME event fired

2. MultiplayerWindow::StartGameHandler
   -> Validates settings
   -> Stores mission name in VarManager: ("Multiplayer", "Mission") = missionName
   -> Sends Settings (0x00) to all connected players
   -> Sends GameInit (0x01) to all connected players

3. Client receives 0x00 (Settings):
   -> FUN_00504d30 stores mission name via FUN_0044b500
   -> Syncs game clock
   -> Assigns player slot and base object ID

4. Client receives 0x01 (GameInit):
   -> CreateMultiplayerGame (0x00504f10)
   -> TG_CallPythonFunction("AI.Setup", "GameInit") -- preload AI scripts
   -> Construct MultiplayerGame("Multiplayer.MultiplayerGame", maxPlayers)
     -> MultiplayerGame ctor: register all C++ event handlers
     -> MultiplayerGame ctor: create "NoMe" and "Forward" groups
     -> Python: MultiplayerGame.Initialize(pGame)
       -> Load sounds, music
       -> pGame.LoadEpisode("Multiplayer.Episode.Episode")
         -> Episode.Initialize(pEpisode)
           -> Read mission name from VarManager
           -> pEpisode.LoadMission(missionScript, startEvent)
             -> Mission1.Initialize(pMission)
               -> MissionShared.Initialize(pMission)
                 -> Load databases
                 -> Setup event handlers (ET_NETWORK_MESSAGE_EVENT)
               -> Setup mission-specific handlers (ET_OBJECT_EXPLODING, ET_WEAPON_HIT)
               -> Initialize scoring dictionaries

5. Host processes NewPlayerInGame (0x2A):
   -> Calls mission.InitNetwork(connID) via Python
     -> Sends MISSION_INIT (0x35) with system/limits
     -> Sends SCORE (0x37) for each player's score state
   -> Replicates all objects via 0x02/0x03 messages
   -> Adds player to "NoMe" and "Forward" groups
```

---

## Scoring System

### Score Flow

1. **Damage tracking** (host only): `DamageEventHandler` records per-player damage to each ship
   in `g_kDamageDictionary[shipObjID][playerID] = [shieldDmg, hullDmg]`

2. **Kill detection** (host only): `ObjectKilledHandler` fires on `ET_OBJECT_EXPLODING`:
   - Awards kill to firing player (from `event.GetFiringPlayerID()`)
   - Awards death to killed player (from `ship.GetNetPlayerID()`)
   - Converts accumulated damage into score: `score = (shieldDmg + hullDmg) / 10.0`
   - Sends `SCORE_CHANGE_MESSAGE` (0x36) to "NoMe" group
   - Checks frag limit: if any player reaches limit, calls `EndGame(END_NUM_FRAGS_REACHED)`
   - If `g_iUseScoreLimit` is set, checks score instead of kills

3. **Score display**: `UpdateScore` -> `Mission1Menus.RebuildPlayerList()` updates the UI

### Score Limit vs Frag Limit

The `g_iUseScoreLimit` flag in MissionMenusShared determines what counts:
- `g_iUseScoreLimit == 0`: Frag limit checks `g_kKillsDictionary[key] >= fragLimit`
- `g_iUseScoreLimit == 1`: Score limit checks `g_kScoresDictionary[key] >= fragLimit * 10000`

---

## EndGame / RestartGame Flow

### EndGame

```python
def EndGame(iReason = END_ITS_JUST_OVER):
    # 1. Build END_GAME_MESSAGE (0x38) with reason code
    # 2. Send to all peers (targetID=0, guaranteed)
    # 3. Set ReadyForNewPlayers = 0 (stop accepting new connections)
```

Client-side `ProcessMessageHandler` (in MissionShared.py) handles receipt:
- Sets `g_bGameOver = 1`
- Calls `ClearShips()` (removes all player ships and torpedoes)
- Displays end game dialog with reason text
- For mission-specific endings (Starbase/Borg/Enterprise dead), sets mission globals

### RestartGame

```python
def RestartGameHandler(pObject, pEvent):
    # Host sends RESTART_GAME_MESSAGE (0x39) to all peers (targetID=0)

def RestartGame():
    # 1. Reset all scoring dictionaries (kills/deaths/scores/damage) to 0
    # 2. Clear g_bGameOver flag
    # 3. Call ClearShips() to remove remaining ships
    # 4. Rebuild player list UI
    # 5. Reset time limit if applicable
    # 6. Show ship selection screen (go back to ship pick phase)
```

---

## Key Addresses

### Functions

| Address | Name | Description |
|---------|------|-------------|
| 0x00504d30 | SettingsHandler | Opcode 0x00: parse game settings |
| 0x00504f10 | CreateMultiplayerGame | Opcode 0x01: create game + load mission |
| 0x005054b0 | UpdateMultiplayerStatusPane | UI text update (headless crash site) |
| 0x0069e590 | MultiplayerGame_ctor | Constructor: slots, groups, handlers |
| 0x0069ebb0 | MultiplayerGame_dtor | Destructor: cleanup groups, handlers |
| 0x0069efc0 | InitializeAllSlots | Loop 0-15, init each player slot |
| 0x0069efe0 | RegisterHandlerNames | Debug name registration for all handlers |
| 0x0069f2a0 | MultiplayerGame_ReceiveMessage | Main opcode dispatcher (jump table) |
| 0x0069f880 | PythonEventHandler_0x06_0x0D | Deserialize + post TGStreamedObject event |
| 0x006a01b0 | HostMsgHandler_0x13 | Self-destruct via power subsystem |
| 0x006a02a0 | RequestObjHandler_0x1E | Respond to object data request |
| 0x006a05e0 | EnterSetHandler_0x1F | Set/map transition |
| 0x006a0080 | ExplosionHandler_0x29 | AoE explosion damage |
| 0x006a1150 | HostEventHandler | Serialize + send to "NoMe" |
| 0x006a1240 | ObjectExplodingHandler | Forward explosion event or apply locally |
| 0x006a1360 | DeletePlayerUIHandler_0x17 | Remove player from scoreboard |
| 0x006a1420 | DeletePlayerEffectHandler_0x18 | "Delete Player" visual effect |
| 0x006a19a0 | GetSlotFromObjectID | `(objID - 0x3FFFFFFF) >> 18` |
| 0x006a19c0 | FindPlayerSlotByConnID | Linear search slots for connID |
| 0x006a1aa0 | GetShipFromPlayerID | Search all sets for ship with connID |
| 0x006a1b10 | ChecksumCompleteHandler | Send Settings + GameInit after checksums |
| 0x006a1e70 | NewPlayerInGameHandler_0x2A | Full player join handshake |
| 0x006a7770 | InitPlayerSlot | Set baseObjID, clear active/connID |
| 0x006b4c10 | TGNetwork_SendTGMessage | Send to specific peer |
| 0x006b4de0 | TGNetwork_SendTGMessageToGroup | Send to named group |
| 0x006b70d0 | TGNetwork_AddGroup | Create/add to named group |
| 0x006f8490 | ImportAndGetAttr | Import Python module, get attribute |
| 0x006f8650 | GetPythonVariable | Read Python variable into C |
| 0x006f8ab0 | TG_CallPythonFunction | Call Python function from C++ |

### Globals

| Address | Type | Name | Description |
|---------|------|------|-------------|
| 0x008e5528 | char[] | "NoMe" | Network group name (all except self) |
| 0x008d94a0 | char[] | "Forward" | Network group name (all peers) |
| 0x008e5f59 | byte | g_SettingsByte1 | Settings byte 1 (game config) |
| 0x008e5f58 | byte | DAT_008e5f58 | Initial value for g_SettingsByte1 |
| 0x0097fa84 | int | playerSlotIndex | This client's player slot (0-15) |
| 0x0097fa8c | int | baseObjectID | This client's base object ID |
| 0x0097fa8b | byte | processingMessage | 1 while handling a message |
| 0x0097e9c8 | int* | setListPtr | Array of game set pointers |
| 0x0097e9cc | int | setListCount | Number of game sets |
| 0x00980228 | struct | missionVarStore | VarManager storage for mission name |
| 0x00959d70 | char[] | "g_iUseScoreLimit" | Python variable name string |
| 0x008e1978 | char[] | "Multiplayer.MultiplayerGame" | Module path for game script |
| 0x008e1948 | char[] | "Multiplayer.MissionMenusShared" | Module path for menu config |
| 0x008e1994 | char[] | "AI.Setup" | Module path for AI preload |
| 0x008e19a0 | char[] | "GameInit" | Function name for AI init |
| 0x0095a354 | char[] | "InitNetwork" | Function name for mission join |

### String References

| Address | String | Used By |
|---------|--------|---------|
| 0x008d9a00 | "Multiplayer.Episode.%s.%s" | Mission path formatting |
| 0x008d9ca8 | "Multiplayer.Episode.Mission1.Mission1" | Default mission path |
| 0x008e1a3c | "Multiplayer.Episode.%s.%sName" | Mission name lookup |
| 0x008e1a78 | "Select Mission" | UI text |
| 0x008e1b68 | "GetMissionDescription" | Python function to get desc |
| 0x008e1a2c | "GetMissionName" | Python function to get name |
| 0x0095a330 | "Delete Player" | TGL string for player removal |

---

## Implications for OpenBC

1. **Mission-agnostic C++ layer**: The C++ code does not know or care what mission is running.
   It provides: object lifecycle, event dispatch, network transport, state synchronization.
   All game mode logic is in Python.

2. **Two-phase join**: New players receive (a) Settings + GameInit (C++ driven), then
   (b) MISSION_INIT + SCORE messages (Python driven via InitNetwork). The OpenBC server
   must replicate both phases.

3. **Network groups are essential**: "NoMe" and "Forward" groups must be maintained for
   correct message routing. Score changes go to "NoMe"; event relay goes to "Forward".

4. **VarManager bridge**: The mission name flows from Settings packet -> VarManager ->
   Episode.py -> LoadMission. OpenBC must replicate this variable storage.

5. **Python calls from C++**: Three specific call points:
   - `AI.Setup.GameInit()` -- during CreateMultiplayerGame
   - `Multiplayer.MissionMenusShared.g_iPlayerLimit` -- variable read
   - `<mission>.InitNetwork(connID)` -- during NewPlayerInGame

6. **Score computation is entirely Python**: The C++ layer only provides the
   `ET_OBJECT_EXPLODING` event. All kill tracking, damage attribution, score calculation,
   and frag limit checking is in Python (Mission1.py).
