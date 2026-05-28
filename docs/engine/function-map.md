> [docs](../README.md) / [engine](README.md) / function-map.md

---
title: stbc.exe Organized Function Map
type: reference
audience: re-engineer
validated: 2026-05-28
methodology: FUNCTION_DOC_WORKFLOW_V5
binary:
  name: STBC.exe
  size: 6394712
  base: 0x00400000
status: partial
evidence:
  - claim: "Total in-body functions in stbc.exe is 18,249"
    address: null
    function: null
    completeness: null
    confidence: high
    note: "From search_functions_enhanced total on STBC.exe; matches .text 0x00401000-0x00887fff. get_function_count returns 18,576 including 327 EXTERNAL import thunks."
  - claim: "Function entry-address range is 0x004010e0 - 0x008879e0"
    address: 0x004010e0
    function: FUN_004010e0
    confidence: high
    note: "Lowest function 0x004010e0, highest 0x008879e0 (Unwind@008879e0). Exact match to prior claim."
  - claim: "Unwind handler count is 4,692"
    address: null
    function: null
    confidence: high
    note: "search_functions_enhanced(name_pattern='Unwind@') total=4692 on STBC.exe."
  - claim: "Catch handler count is 3"
    address: 0x004168c8
    function: Catch@004168c8
    confidence: high
    note: "Three addresses: 0x004168c8, 0x006f5a8a, 0x00721259."
  - claim: "FUN_xxxxxxxx (unnamed) count is 13,467"
    address: null
    function: null
    confidence: high
    note: "search_functions_enhanced(name_pattern='FUN_') total=13467. +134 vs prior 13,333."
  - claim: "Thunk count is 164"
    address: null
    function: null
    confidence: high
    note: "search_functions_enhanced(is_thunk=true) total=164. +31 vs prior 133, likely improved thunk recognition."
  - claim: "20 address-range categories partition the binary exhaustively and non-overlappingly"
    address: null
    function: null
    confidence: high
    note: "All 18,249 in-body functions bin into exactly one category. Boundaries verified at Cat 9↔10 (0x006A3000), Cat 14↔15 (0x006E0000), Cat 19↔20 (0x00870000)."
  - claim: "Category 9 MultiplayerGame: 45 functions in 0x0069E000-0x006A2FFF"
    address: 0x0069f2a0
    function: MpgameHandleMessage
    confidence: high
    note: "+1 vs prior count 44; the new function is MpgameHandleMessage at 0x0069f2a0 (created via v5 dispatcher recovery 2026-05-28). Prior doc qualifier 'handler addr, not function entry' is now stale."
  - claim: "MultiplayerGame opcode dispatcher is MpgameHandleMessage at 0x0069f2a0, handling opcodes 0x02-0x2A via jump table at 0x0069F534"
    address: 0x0069f2a0
    function: MpgameHandleMessage
    completeness: 69.94
    confidence: high
    note: "v5 dispatcher recovery: __thiscall(MultiplayerGame*, TGMessage*), body 0x0069F2A0-0x0069F530 (657 bytes). 41-entry jump table indexed by opcode-2. Opcodes 0x00 (Settings), 0x01 (GameInit), 0x16 (UICollisionSetting) are handled by MultiplayerWindow dispatcher (0x00504c10), not MultiplayerGame. Completeness score will rise once MultiplayerGame/TGMessage/TGBufferStream struct skeletons land (parallel work)."
  - claim: "Per-category 'Named/Identified Functions' list entries reflect pre-v5 annotation-script output and are not currently applied to the Ghidra import"
    address: null
    function: null
    confidence: low
    note: "Sample of 6 functions confirmed: 5/6 exist as FUN_xxxxxxxx in Ghidra (unnamed); only 0x0069f2a0 has been v5-renamed. Per-function v5 documentation passes will progressively retire 'confidence: low' on these entries."
companions:
  - docs/engine/function-mapping-report.md
  - docs/engine/decompiled-functions.md
  - docs/engine/v5-validation-status.md
  - docs/engine/README.md
---

# stbc.exe Organized Function Map

> [!NOTE]
> This doc is `status: partial`. The foundation claims — total counts, address-range partition, per-category sizes, the MultiplayerGame dispatcher — are v5-verified against the current Ghidra import (2026-05-28). The per-category **"Named/Identified Functions"** lists are pre-v5 annotation-script output and are **not currently applied to the Ghidra import**; addresses are still correct, but the names are aspirational pending per-function v5 documentation passes. Entries known to be unnamed in the current import are tagged `[v5: unnamed in current import]`. See [docs/guides/v5-evidence-header.md](../guides/v5-evidence-header.md) for the standard.

Total: **18,249 functions** in-body (13,467 FUN_, 164 thunks, 86 named imports/CRT, 4,692 Unwind handlers, 3 Catch handlers). `get_function_count` returns **18,576** including 327 EXTERNAL import thunks.
Address range: 0x004010e0 - 0x008879e0
Complete flat listing: [function-map.txt](function-map.txt)

The binary partitions into **20 address-range categories** (verified exhaustive and non-overlapping). Each category gets its own section below.

---

## Quick Reference: Known Handler Tables

### MultiplayerGame Event Handlers (registered by FUN_0069efe0)
```
0x0069f2a0  MpgameHandleMessage          (opcode dispatch for game messages 0x02-0x2A, jump table at 0x0069F534)
0x006a07d0  EnterSetHandler
0x006a0a10  ExitedWarpHandler
0x006a0a20  DisconnectHandler
0x006a0a30  NewPlayerHandler             (assigns slot, starts checksums)
0x006a0c60  SystemChecksumPassedHandler
0x006a0c90  SystemChecksumFailedHandler
0x006a0ca0  DeletePlayerHandler
0x006a0f90  ObjectCreatedHandler
0x006a1150  HostEventHandler
0x006a1240  ObjectExplodingHandler
0x006a1590  NewPlayerInGameHandler
0x006a1790  StartFiringHandler
0x006a17a0  StartWarpHandler
0x006a17b0  TorpedoTypeChangedHandler
0x006a18d0  StopFiringHandler
0x006a18e0  StopFiringAtTargetHandler
0x006a18f0  StartCloakingHandler
0x006a1900  StopCloakingHandler
0x006a1910  SubsystemStateChangedHandler
0x006a1920  AddToRepairListHandler
0x006a1930  ClientEventHandler
0x006a1940  RepairListPriorityHandler
0x006a1970  SetPhaserLevelHandler
0x006a1a60  DeleteObjectHandler
0x006a1a70  ChangedTargetHandler
0x006a1b10  ChecksumCompleteHandler      (sends settings + map to client)
0x006a2640  KillGameHandler
0x006a2a40  RetryConnectHandler
```

### NetFile Opcode Dispatch (via FUN_006a3cd0)
```
Opcode 0x20  ->  FUN_006a5df0  Client: ChecksumRequestHandler
Opcode 0x21  ->  FUN_006a4260  Server: ChecksumResponseEntry -> FUN_006a4560 (verifier)
Opcode 0x22  ->  FUN_006a4c10  ChecksumFail (file mismatch)
Opcode 0x23  ->  FUN_006a4c10  ChecksumFail (reference mismatch)
Opcode 0x25  ->  (inline)      File transfer receive
Opcode 0x27  ->  FUN_006a4250  (unknown)
```

### MultiplayerWindow Handlers (registered by FUN_005046b0)
```
0x00504890  StartGameHandler             (UI entry point for join/host)
0x00504f10  SetupMultiplayerGame         (TopWindow_SetupMultiplayerGame)
```

### Core Tick Functions
```
0x0043b4f0  UtopiaApp_MainTick           (__fastcall on UtopiaApp)
0x006B4560  TGNetwork::Update            (__thiscall on WSN)
0x006da2c0  EventManager::ProcessEvents  (__fastcall on EventMgr)
```

---

## Category 1: Core Engine / Base Objects
**Range:** 0x00401000 - 0x0042FFFF | **Count:** 646 functions

Contains fundamental engine objects, base class vtable methods, TGString operations,
memory management wrappers, and core object hierarchy (BaseObjectClass and derivatives).

### Named/Identified Functions

> [!NOTE]
> Function names in this section are pre-v5 annotation-script output and are **not currently applied to the Ghidra import**. Addresses are correct (verified 2026-05-28); names are aspirational, pending per-function v5 documentation passes. The Catch handler at 0x004168c8 is the one exception — it is real Ghidra output.

```
0x004028a0  thunk_FUN_006ff7b0           (-> Python/SWIG helper)
0x00403350  thunk_FUN_006d5d70           (-> Stream/serialization)
0x00403530  thunk_FUN_006ff7b0           (-> Python/SWIG helper)
0x004041d0  thunk_FUN_00409ed0           (base class method)
0x0040dac0  thunk_FUN_007dad10           (-> NetImmerse)
0x0040db90  thunk_FUN_007dad10
0x004126f0  thunk_FUN_007dad10
0x004127e0  thunk_FUN_007dad10
0x004164d0  thunk_FUN_007dad10
0x00416540  thunk_FUN_007dad10
0x004168c8  Catch@004168c8
0x0041f0d0  thunk_FUN_004271a0           (base class hierarchy)
0x004210a0  thunk_FUN_0041eb70           (repeated - common base method)
0x00421fe0  thunk_FUN_0041eb70
0x00422bc0  thunk_FUN_0041eb70
0x00423c90  thunk_FUN_0041eb70
0x004246f0  thunk_FUN_0041eb70
0x00425160  thunk_FUN_0041eb70
0x00426200  thunk_FUN_0041eb70
0x004269f0  thunk_FUN_0041eb70
0x00426f90  thunk_FUN_0041eb70
0x00427b70  thunk_FUN_0041eb70
```

Notes: FUN_0041eb70 is thunked 10 times, suggesting it is a fundamental virtual method
(likely destructor or type-info) inherited by many game object classes in the 0x0042xxxx range.

---

## Category 2: UtopiaApp / UtopiaModule / Initialization
**Range:** 0x00430000 - 0x0045FFFF | **Count:** 717 functions

The core application class (UtopiaApp) and module system (UtopiaModule). Contains
initialization, main loop, multiplayer setup, and Python embedding entry points.

### Named/Identified Functions

> [!NOTE]
> Function names in this section are pre-v5 annotation-script output and are **not currently applied to the Ghidra import**. Addresses are correct (verified 2026-05-28); names are aspirational, pending per-function v5 documentation passes.

```
0x00430230  thunk_FUN_007dad10           (-> NetImmerse)
0x00430550  thunk_FUN_007dad10
0x00437270  thunk_FUN_006d5d70           (-> Stream)
0x00438280  thunk_FUN_006cdb10           (-> Serialization)
0x0043b4f0  FUN_0043b4f0 (intended: UtopiaApp_MainTick)         [v5: unnamed in current import]
0x0043eca0  thunk_FUN_0072de40           (-> File I/O)
0x0043f870  thunk_FUN_006d5d70
0x0043f980  thunk_FUN_006d5d70
0x00441fa0  thunk_FUN_006d5d70
0x00444460  thunk_FUN_006d2050           (-> TGObject base)
0x00445bb0  thunk_FUN_006d5d70
0x00445d90  FUN_00445d90 (intended: UtopiaModule::InitMultiplayer) [v5: unnamed in current import]
0x00451ac0  FUN_00451ac0 (intended: SimulationPipelineTick)      [v5: unnamed in current import]
0x00455990  thunk_FUN_007949b0           (-> Renderer)
0x0045f660  thunk_FUN_0045f8b0
```

> [!NOTE]
> The "Key addresses" block below is legacy patch tracking carried forward from pre-v5 docs. It records DLL-proxy patch target addresses (and their REMOVED predecessors). It is not function-catalog content and a future patch-changelog refactor may move it out of this doc. Addresses are correct as patch-target locations.

Key addresses:
- 0x0043B1D2: PatchInitAbort target (NOP abort jump) - ACTIVE
- 0x0043B1D7: (was PatchInitSkipPython target - REMOVED)
- 0x00438AE6: (was PatchInitTraversal target - REMOVED)
- 0x004433EA: PatchRenderTick target (JNZ->JMP skip render) - ACTIVE

---

## Category 3: UI Framework / Widget Library
**Range:** 0x00460000 - 0x004BFFFF | **Count:** 1,241 functions

Widget base classes, button/list/text controls, layout management, and UI event routing.
The game uses a custom widget toolkit built on top of the renderer.

### Named/Identified Functions

> [!NOTE]
> Function names in this section are pre-v5 annotation-script output and are **not currently applied to the Ghidra import**. Addresses are correct (verified 2026-05-28); names are aspirational, pending per-function v5 documentation passes.

```
0x0046c280  FUN_0046c280 (intended: CRect)                      [v5: unnamed in current import]
0x00468760  thunk_FUN_004657f0           (UI base class method)
0x00488790  thunk_FUN_006d9060           (-> Timer/event)
0x0048bc40  thunk_FUN_006d9060
0x0049d010  thunk_FUN_004a2950           (UI hierarchy)
0x004a0f60  thunk_FUN_006d5d70           (-> Stream)
```

---

## Category 4: Windows / Dialogs / Screens
**Range:** 0x004C0000 - 0x0051FFFF | **Count:** 1,112 functions

Concrete game windows: main menu, multiplayer lobby, options, ship selection, etc.
Each window class has handler registration, button callbacks, and state management.

### Named/Identified Functions

> [!NOTE]
> Function names in this section are pre-v5 annotation-script output and are **not currently applied to the Ghidra import**. Addresses are correct (verified 2026-05-28); names are aspirational, pending per-function v5 documentation passes.

```
0x004c89f0  thunk_FUN_004cbd60           (window base)
0x004d53d0  thunk_FUN_007e3880           (-> NI renderer)
0x004d98e0  thunk_FUN_007ef280           (-> NI renderer)
0x004db190  thunk_FUN_007949b0           (-> Renderer)
0x004e3440  thunk_FUN_007d9c10           (-> NI scene)
0x004e6e80  thunk_FUN_007e3880
0x004e7d20  thunk_FUN_007ef280
0x004e9fa0  thunk_FUN_007e3880
0x004ee630  thunk_FUN_004eca30           (window hierarchy)
0x004f2d10  thunk_FUN_007d9c10
0x004f5510  thunk_FUN_007e3880
0x004f8850  thunk_FUN_007e3880
0x005046b0  FUN_005046b0 (intended: RegisterMPWindowHandlers)   [v5: unnamed in current import]
0x00504890  FUN_00504890 (intended: StartGameHandler)            [v5: unnamed in current import]
0x00504f10  FUN_00504f10 (intended: TopWindow_SetupMultiplayerGame) [v5: unnamed in current import]
```

---

## Category 5: Game Logic / Ships / AI / Tactical
**Range:** 0x00520000 - 0x005AFFFF | **Count:** 2,073 functions

Ship classes, weapons systems, subsystems, damage model, AI behaviors, tactical
decision-making, formation management, and combat logic. This is the largest
contiguous game-logic section.

### Named/Identified Functions

> [!NOTE]
> Function names in this section are pre-v5 annotation-script output and are **not currently applied to the Ghidra import**. Addresses are correct (verified 2026-05-28); names are aspirational, pending per-function v5 documentation passes.

```
0x005af390  FUN_005af390 (intended: CRect)                      [v5: unnamed in current import]
```

Sub-ranges (estimated by density):
- 0x0052-0x0054: Ship subsystems (shields, weapons, engines)
- 0x0055-0x0056: Ship object classes, hardpoints
- 0x0057-0x0058: AI/tactical decision-making
- 0x0059-0x005a: Math/geometry helpers, collision, targeting

---

## Category 6: Sparse Code / Mission System / Large Objects
**Range:** 0x005B0000 - 0x0065FFFF | **Count:** 201 functions

Very sparse - likely large mission/episode objects, cutscene system, or code that
was compiled separately (possibly third-party libraries or auto-generated code).
The gap from 0x005C to 0x0065 has only ~66 functions total.

### Notable Sub-ranges
- 0x005B: ~97 functions - possibly mission/scenario framework
- 0x005C-0x005F: ~38 functions - very sparse, thunks to 006d5d70 (serialization)
- 0x0060-0x0065: ~66 functions - scattered, large gaps between addresses

---

## Category 7: Scene Graph / 3D Objects
**Range:** 0x00660000 - 0x0068FFFF | **Count:** 527 functions

Scene graph nodes, spatial objects, bounding volumes, visibility culling, and
3D object management. Bridges game logic to the NetImmerse renderer.

---

## Category 8: Game Session / Pre-Multiplayer
**Range:** 0x00690000 - 0x0069DFFF | **Count:** 159 functions

Game session management, player management infrastructure, and setup code that
feeds into MultiplayerGame. Likely contains single-player game session equivalents.

---

## Category 9: MultiplayerGame (CRITICAL)
**Range:** 0x0069E000 - 0x006A2FFF | **Count:** 45 functions

The MultiplayerGame class — handles all multiplayer game state, player slots,
event handling, and coordination between networking and game logic.

The +1 vs the pre-v5 count of 44 is **MpgameHandleMessage at 0x0069f2a0**, which the
v5 dispatcher-recovery pass (2026-05-28) promoted to a full function entry. It was
previously listed as a handler address inside FUN_0069f250.

### All Functions in This Range

> [!NOTE]
> Function names in this section are pre-v5 annotation-script output and are **not currently applied to the Ghidra import**. Addresses are correct (verified 2026-05-28); names are aspirational, pending per-function v5 documentation passes. The dispatcher at 0x0069f2a0 (MpgameHandleMessage) is the one exception — it has been v5-validated and is the current Ghidra name.

```
0x0069e0c0  FUN_0069e0c0                 (MP game class methods)
0x0069e0d0  FUN_0069e0d0
0x0069e100  FUN_0069e100
0x0069e110  FUN_0069e110
0x0069e520  FUN_0069e520
0x0069e530  FUN_0069e530
0x0069e560  FUN_0069e560
0x0069e590  FUN_0069e590
0x0069ebb0  FUN_0069ebb0
0x0069edc0  FUN_0069edc0
0x0069ee50  FUN_0069ee50
0x0069efc0  FUN_0069efc0
0x0069efe0  FUN_0069efe0 (intended: RegisterMPGameHandlers)      [v5: unnamed in current import]
0x0069f250  FUN_0069f250
0x0069f2a0  MpgameHandleMessage          (opcode dispatcher 0x02-0x2A, jump table at 0x0069F534, completeness 69.94) [v5-validated 2026-05-28]
0x0069f620  FUN_0069f620
0x0069f880  FUN_0069f880
0x0069f930  FUN_0069f930
0x0069fbb0  FUN_0069fbb0
0x0069fda0  FUN_0069fda0
0x0069ff50  FUN_0069ff50
0x0069fff0  FUN_0069fff0
0x006a0080  FUN_006a0080
0x006a01b0  FUN_006a01b0
0x006a01e0  FUN_006a01e0
0x006a02a0  FUN_006a02a0
0x006a0490  FUN_006a0490
0x006a05e0  FUN_006a05e0
    0x006a07d0 = EnterSetHandler         (handler addr within FUN_006a05e0 block)
    0x006a0a10 = ExitedWarpHandler       (handler addr)
    0x006a0a20 = DisconnectHandler       (handler addr)
0x006a0a30  FUN_006a0a30 (intended: NewPlayerHandler)             [v5: unnamed in current import]
0x006a1360  FUN_006a1360                 (contains ObjectCreatedHandler, HostEventHandler, etc.)
0x006a1420  FUN_006a1420
0x006a17c0  FUN_006a17c0
0x006a19a0  FUN_006a19a0
0x006a19c0  FUN_006a19c0
0x006a19fc  FUN_006a19fc
0x006a1aa0  FUN_006a1aa0
0x006a1b10  FUN_006a1b10 (intended: ChecksumCompleteHandler)      [v5: unnamed in current import]
0x006a1e70  FUN_006a1e70
0x006a2470  FUN_006a2470
0x006a2650  FUN_006a2650                 (contains KillGameHandler at 0x006a2640)
0x006a2d90  FUN_006a2d90                 (contains RetryConnectHandler at 0x006a2a40)
0x006a2e60  FUN_006a2e60
0x006a2f10  FUN_006a2f10
0x006a2f60  FUN_006a2f60
0x006a2fc0  FUN_006a2fc0
```

Note: Many handler addresses (e.g., 0x006a07d0 EnterSetHandler) are offsets within
larger functions, not separate function entries. They are registered as callback addresses.
The exception is 0x0069f2a0 (MpgameHandleMessage) — formerly listed as a handler offset
inside FUN_0069f250, now confirmed as a separate function entry (its own __thiscall body
spanning 0x0069F2A0-0x0069F530, 657 bytes).

---

## Category 10: NetFile / Checksum Manager (CRITICAL)
**Range:** 0x006A3000 - 0x006A7FFF | **Count:** 58 functions

The checksum/file-transfer system. NetFile serves triple duty: checksum manager,
message opcode dispatcher, and file transfer manager.

### All Functions in This Range

> [!NOTE]
> Function names in this section are pre-v5 annotation-script output and are **not currently applied to the Ghidra import**. Addresses are correct (verified 2026-05-28); names are aspirational, pending per-function v5 documentation passes. Inline parenthetical descriptions reflect prior reverse-engineering notes from [decompiled-functions.md](decompiled-functions.md).

```
0x006a3080  FUN_006a3080                 (NetFile utilities)
0x006a3090  FUN_006a3090
0x006a30c0  FUN_006a30c0 (intended: NetFile_Constructor)         [v5: unnamed in current import]
0x006a3280  FUN_006a3280
0x006a32b0  FUN_006a32b0
0x006a3500  FUN_006a3500
0x006a3560  FUN_006a3560 (intended: RegisterNetFileHandler)      [v5: unnamed in current import]
0x006a3580  FUN_006a3580
0x006a35b0  FUN_006a35b0
0x006a3820  FUN_006a3820 (intended: ChecksumRequestSender)       [v5: unnamed in current import]
0x006a39b0  FUN_006a39b0 (intended: ChecksumRequestBuilder)      [v5: unnamed in current import]
0x006a3cd0  FUN_006a3cd0 (intended: NetFile::ReceiveMessageHandler — opcode dispatcher 0x20-0x27) [v5: unnamed in current import]
0x006a3ea0  FUN_006a3ea0
0x006a4140  FUN_006a4140
0x006a4250  FUN_006a4250                 (opcode 0x27 handler)
0x006a4260  FUN_006a4260 (intended: ChecksumResponseEntry — opcode 0x21) [v5: unnamed in current import]
0x006a4560  FUN_006a4560 (intended: ChecksumResponseVerifier)    [v5: unnamed in current import]
0x006a4a00  FUN_006a4a00 (intended: ChecksumFail — fires event + sends 0x22/0x23) [v5: unnamed in current import]
0x006a4bb0  FUN_006a4bb0 (intended: ChecksumAllPassed)           [v5: unnamed in current import]
0x006a4c10  FUN_006a4c10                 (checksum fail notification handler)
0x006a4d80  FUN_006a4d80                 (extract dir/filter from queued msg)
0x006a4e70  FUN_006a4e70
0x006a5220  FUN_006a5220
0x006a5230  FUN_006a5230
0x006a5260  FUN_006a5260
0x006a5270  FUN_006a5270
0x006a5290  FUN_006a5290                 (checksum success handler)
0x006a5570  FUN_006a5570
0x006a5660  FUN_006a5660
0x006a5860  FUN_006a5860 (intended: FileTransferProcessor)       [v5: unnamed in current import]
0x006a5df0  FUN_006a5df0 (intended: Client_ChecksumRequestHandler — opcode 0x20) [v5: unnamed in current import]
0x006a6190  FUN_006a6190
0x006a62f0  FUN_006a62f0
0x006a63b0  FUN_006a63b0
0x006a6500  FUN_006a6500                 (cleanup existing state for player)
0x006a6630  FUN_006a6630                 (client init for first checksum)
0x006a6670  FUN_006a6670
0x006a67b0  FUN_006a67b0
0x006a6b40  FUN_006a6b40
0x006a6de0  FUN_006a6de0
0x006a6e50  FUN_006a6e50
0x006a6f20  FUN_006a6f20
0x006a6f30  FUN_006a6f30
0x006a6fc0  FUN_006a6fc0
0x006a7070  FUN_006a7070
0x006a7080  FUN_006a7080
0x006a70f0  FUN_006a70f0
0x006a71a0  FUN_006a71a0
0x006a71b0  FUN_006a71b0
0x006a75f0  FUN_006a75f0
0x006a7720  FUN_006a7720
0x006a7740  FUN_006a7740
0x006a7760  FUN_006a7760
0x006a7770  FUN_006a7770                 (initialize player slot)
0x006a77b0  FUN_006a77b0
0x006a77c0  FUN_006a77c0
0x006a77f0  FUN_006a77f0
0x006a7800  FUN_006a7800
```

---

## Category 11: Hash Tables / Containers / Utilities
**Range:** 0x006A8000 - 0x006AFFFF | **Count:** 141 functions

Hash table implementation, linked lists, and container utilities used by NetFile,
event system, and other subsystems. Also includes GetTickCount and WSACleanup imports.

### Named/Identified Functions

> [!NOTE]
> Win32/Winsock import names are correct (resolved by the loader). Other category content is FUN_xxxxxxxx.

```
0x006acd90  GetTickCount                 (Win32 import)
0x006acdd0  WSACleanup                   (Winsock import)
```

### Sample Functions (first 20)
```
0x006a8170  FUN_006a8170
0x006a8290  FUN_006a8290
0x006a82a0  FUN_006a82a0
0x006a82d0  FUN_006a82d0
0x006a82e0  FUN_006a82e0
0x006a8c50  FUN_006a8c50
0x006a8ce0  FUN_006a8ce0
0x006a8e00  FUN_006a8e00
0x006a8e10  FUN_006a8e10
0x006a8e40  FUN_006a8e40
0x006a8e50  FUN_006a8e50
0x006a8fb0  FUN_006a8fb0
0x006a9090  FUN_006a9090
0x006a9930  FUN_006a9930
0x006a9aa0  FUN_006a9aa0
0x006a9af0  FUN_006a9af0
0x006a9b40  FUN_006a9b40
0x006a9b80  FUN_006a9b80
0x006a9c20  FUN_006a9c20
0x006a9cb0  FUN_006a9cb0
```

---

## Category 12: TGNetwork / TGWinsockNetwork (CRITICAL)
**Range:** 0x006B0000 - 0x006BFFFF | **Count:** 225 functions

The entire networking stack: UDP socket management, peer tracking, message queuing,
reliable delivery, packet serialization, and the Winsock implementation.

### Named/Identified Functions

> [!NOTE]
> Function names in this section are pre-v5 annotation-script output and are **not currently applied to the Ghidra import**. Addresses are correct (verified 2026-05-28); names are aspirational, pending per-function v5 documentation passes.

```
0x006b2930  thunk_FUN_006b7720           (internal network method)
0x006b3ec0  FUN_006b3ec0 (intended: TGNetwork_HostOrJoin)        [v5: unnamed in current import]
0x006b4560  FUN_006b4560 (intended: TGNetwork::Update — main network tick) [v5: unnamed in current import]
0x006b4c10  FUN_006b4c10 (intended: TGNetwork::Send)             [v5: unnamed in current import]
0x006b5080  FUN_006b5080                 (queue message to peer)
0x006b55b0  FUN_006b55b0 (intended: SendOutgoingPackets)         [v5: unnamed in current import]
0x006b5c90  FUN_006b5c90 (intended: ProcessIncomingPackets)      [v5: unnamed in current import]
0x006b5f70  FUN_006b5f70 (intended: DispatchIncomingQueue)       [v5: unnamed in current import]
0x006b61e0  FUN_006b61e0 (intended: ReliableACKHandler)          [v5: unnamed in current import]
0x006b6ad0  FUN_006b6ad0 (intended: DispatchToApplication)       [v5: unnamed in current import]
0x006b7070  FUN_006b7070                 (set address info)
0x006b8670  FUN_006b8670                 (reset retry counter)
0x006b9460  [vtable+0x60]               (socket creation - called by HostOrJoin)
0x006b9870  [vtable+0x70]               (socket send - called by SendOutgoing)
0x006b9b20  FUN_006b9b20 (intended: CreateUDPSocket)             [v5: unnamed in current import]
0x006b9bb0  FUN_006b9bb0                 (stores port at WSN+0x338)
```

### Sample Functions (first 50)
```
0x006b0030  FUN_006b0030
0x006b0360  FUN_006b0360
0x006b0380  FUN_006b0380
0x006b03f0  FUN_006b03f0
0x006b0450  FUN_006b0450
0x006b0460  FUN_006b0460
0x006b0490  FUN_006b0490
0x006b04a0  FUN_006b04a0
0x006b0620  FUN_006b0620
0x006b06f0  FUN_006b06f0
0x006b0820  FUN_006b0820
0x006b0860  FUN_006b0860
0x006b08a0  FUN_006b08a0
0x006b0ed0  FUN_006b0ed0
0x006b1010  FUN_006b1010
0x006b10c0  FUN_006b10c0
0x006b1170  FUN_006b1170
0x006b1180  FUN_006b1180
0x006b11b0  FUN_006b11b0
0x006b11c0  FUN_006b11c0
0x006b1af0  FUN_006b1af0
0x006b1b20  FUN_006b1b20
0x006b1ba0  FUN_006b1ba0
0x006b1dd0  FUN_006b1dd0
0x006b1e00  FUN_006b1e00
0x006b1f30  FUN_006b1f30
0x006b2210  FUN_006b2210
0x006b23c0  FUN_006b23c0
0x006b2460  FUN_006b2460
0x006b2530  FUN_006b2530
0x006b2540  FUN_006b2540
0x006b2570  FUN_006b2570
0x006b2590  FUN_006b2590
0x006b2670  FUN_006b2670
0x006b2930  thunk_FUN_006b7720
0x006b2960  FUN_006b2960
0x006b2970  FUN_006b2970
0x006b29a0  FUN_006b29a0
0x006b29b0  FUN_006b29b0
0x006b3300  FUN_006b3300
0x006b3400  FUN_006b3400
0x006b3450  FUN_006b3450
0x006b34b0  FUN_006b34b0
0x006b3590  FUN_006b3590
0x006b35f0  FUN_006b35f0
0x006b3680  FUN_006b3680
0x006b36e0  FUN_006b36e0
0x006b3770  FUN_006b3770
0x006b37d0  FUN_006b37d0
0x006b3860  FUN_006b3860
```

Key addresses:
- WSN+0x10C: send-enabled flag (checked by SendOutgoingPackets)
- WSN+0x10E: IsHost flag (1=host, 0=client)
- WSN+0x10F: join-in-progress flag
- WSN+0x194: UDP socket handle (shared with GameSpy)
- WSN+0x338: port number

> [!NOTE]
> Legacy patch-tracking entry: 0x6B467C was the PatchHostDequeueLoop target (REMOVED). Carried forward from pre-v5 docs for historical reference; future patch-changelog refactor may move it out.

---

## Category 13: Streams / Serialization
**Range:** 0x006C0000 - 0x006CFFFF | **Count:** 246 functions

TGStream, binary serialization, file I/O streams, and data marshalling used by
save/load, network messages, and resource loading.

### Named/Identified Functions

> [!NOTE]
> Function names in this section are pre-v5 annotation-script output and are **not currently applied to the Ghidra import**. Addresses are correct (verified 2026-05-28); names are aspirational, pending per-function v5 documentation passes.

```
0x006cdb10  (target of thunk_FUN from 0x00438280 - serialization base)
```

### Sample Functions (first 20)
```
0x006c08d0  FUN_006c08d0
0x006c09f0  FUN_006c09f0
0x006c0a10  FUN_006c0a10
0x006c0b50  FUN_006c0b50
0x006c0b60  FUN_006c0b60
0x006c0c70  FUN_006c0c70
0x006c0ca0  FUN_006c0ca0
0x006c0cc0  FUN_006c0cc0
0x006c0d90  FUN_006c0d90
0x006c0e30  FUN_006c0e30
0x006c0e60  FUN_006c0e60
0x006c0ec0  FUN_006c0ec0
0x006c0fb0  FUN_006c0fb0
0x006c1080  FUN_006c1080
0x006c10b0  FUN_006c10b0
0x006c1190  FUN_006c1190
0x006c11c0  FUN_006c11c0
0x006c12a0  FUN_006c12a0
0x006c12d0  FUN_006c12d0
0x006c13b0  FUN_006c13b0
```

---

## Category 14: Events / Timers / TGEventManager (CRITICAL)
**Range:** 0x006D0000 - 0x006DFFFF | **Count:** 327 functions

The entire event system: TGEventManager, TGEvent, TGTimer, handler registration,
event dispatch, condition system, and timer management.

### Named/Identified Functions

> [!NOTE]
> Function names in this section are pre-v5 annotation-script output and are **not currently applied to the Ghidra import**. Addresses are correct (verified 2026-05-28); names are aspirational, pending per-function v5 documentation passes.

```
0x006d2050  (target of thunk - TGObject base method)
0x006d4b10  thunk_FUN_006d9060           (timer-related)
0x006d5d70  (target of many thunks - base serialization/stream method)
0x006d9060  FUN_006d9060                 (timer base method, thunked from many places)
0x006da040  FUN_006da040
0x006da0b0  FUN_006da0b0
0x006da130  FUN_006da130 (intended: RegisterHandlerFunction)     [v5: unnamed in current import]
0x006da160  FUN_006da160
0x006da2c0  FUN_006da2c0 (intended: EventManager::ProcessEvents — main event pump) [v5: unnamed in current import]
0x006da300  FUN_006da300                 (dispatch single event)
0x006da370  thunk_FUN_006de310
0x006db380  FUN_006db380 (intended: RegisterEventHandler)        [v5: unnamed in current import]
0x006db620  FUN_006db620                 (dispatch to handler chain)
```

### Sample Functions (first 50)
```
0x006d0320  FUN_006d0320
0x006d0330  FUN_006d0330
0x006d03a0  FUN_006d03a0
0x006d03d0  FUN_006d03d0
0x006d03f0  FUN_006d03f0
0x006d0470  FUN_006d0470
0x006d04f0  FUN_006d04f0
0x006d0520  FUN_006d0520
0x006d0550  FUN_006d0550
0x006d0670  FUN_006d0670
0x006d06d0  FUN_006d06d0
0x006d0750  FUN_006d0750
0x006d07a0  FUN_006d07a0
0x006d08a0  FUN_006d08a0
0x006d08b0  FUN_006d08b0
0x006d08e0  FUN_006d08e0
0x006d08f0  FUN_006d08f0
0x006d11d0  FUN_006d11d0
0x006d12c0  FUN_006d12c0
0x006d17e0  FUN_006d17e0
0x006d18b0  FUN_006d18b0
0x006d1980  FUN_006d1980
0x006d1b90  FUN_006d1b90
0x006d1bb0  FUN_006d1bb0
0x006d1c20  FUN_006d1c20
0x006d1dd0  FUN_006d1dd0
0x006d1e10  FUN_006d1e10
0x006d1e50  FUN_006d1e50
0x006d1ea0  FUN_006d1ea0
0x006d1ef0  FUN_006d1ef0
0x006d1fc0  FUN_006d1fc0
0x006d2050  FUN_006d2050
0x006d2080  FUN_006d2080
0x006d20e0  FUN_006d20e0
0x006d2100  FUN_006d2100
0x006d2150  FUN_006d2150
0x006d21a0  FUN_006d21a0
0x006d21f0  FUN_006d21f0
0x006d22a0  FUN_006d22a0
0x006d22e0  FUN_006d22e0
0x006d2330  FUN_006d2330
0x006d2370  FUN_006d2370
0x006d23c0  FUN_006d23c0
0x006d2400  FUN_006d2400
0x006d2470  FUN_006d2470
0x006d24b0  FUN_006d24b0
0x006d2720  FUN_006d2720
0x006d2770  FUN_006d2770
0x006d28b0  FUN_006d28b0
0x006d2950  FUN_006d2950
```

Key addresses:
- 0x0097F838: EventManager global
- 0x0097F864: Handler registry (EventManager+0x2C)

---

## Category 15: Config / VarManager / Misc
**Range:** 0x006E0000 - 0x006EFFFF | **Count:** 226 functions

Configuration system (TGConfigMapping), variable manager (VarManagerClass),
and miscellaneous utility classes.

---

## Category 16: GameSpy / SWIG Bindings
**Range:** 0x006F0000 - 0x006FFFFF | **Count:** 273 functions

GameSpy SDK integration (query/response, heartbeat, server browser) and SWIG
binding infrastructure for Python<->C++ interop.

### Named/Identified Functions

> [!NOTE]
> The `Catch@...` entry is real Ghidra output. Other category content is FUN_xxxxxxxx; descriptive text reflects pre-v5 RE notes pending per-function v5 documentation passes.

```
0x006f5a8a  Catch@006f5a8a               (exception handler)
0x006fd9f0  thunk_FUN_006ff210
0x006ff7b0  FUN_006ff7b0                 (target of thunks from 0x004028a0, 0x00403530)
```

### Sample Functions (first 30)
```
0x006f0730  FUN_006f0730
0x006f0760  FUN_006f0760
0x006f07f0  FUN_006f07f0
0x006f0820  FUN_006f0820
0x006f08b0  FUN_006f08b0
0x006f08f0  FUN_006f08f0
0x006f09a0  FUN_006f09a0
0x006f09e0  FUN_006f09e0
0x006f0a70  FUN_006f0a70
0x006f0b70  FUN_006f0b70
0x006f0ba0  FUN_006f0ba0
0x006f0bc0  FUN_006f0bc0
0x006f0c40  FUN_006f0c40
0x006f0ee0  FUN_006f0ee0
0x006f0f30  FUN_006f0f30
0x006f0fc0  FUN_006f0fc0
0x006f1080  FUN_006f1080
0x006f1120  FUN_006f1120
0x006f11b0  FUN_006f11b0
0x006f13c0  FUN_006f13c0
0x006f13e0  FUN_006f13e0
0x006f14e0  FUN_006f14e0
0x006f1570  FUN_006f1570
0x006f15c0  FUN_006f15c0
0x006f1650  FUN_006f1650
0x006f1680  FUN_006f1680
0x006f16a0  FUN_006f16a0
0x006f1880  FUN_006f1880
0x006f18e0  FUN_006f18e0
0x006f1950  FUN_006f1950
```

---

## Category 17: Python 1.5 / SWIG Method Tables / Scripting Engine
**Range:** 0x00700000 - 0x0076FFFF | **Count:** 1,620 functions

Embedded Python 1.5 interpreter, SWIG-generated wrapper functions, module initialization
(Py_InitModule4), Python object management, and the Appc/App module method tables.

The +1 vs the pre-v5 count of 1,619 has not been individually traced; it is one of
164 unidentified delta entries across the binary. Flagged as a campaign open question.

### Named/Identified Functions

> [!NOTE]
> The `Catch@...` entry is real Ghidra output. Other function names in this section are pre-v5 annotation-script output and are **not currently applied to the Ghidra import**. Addresses are correct (verified 2026-05-28); names are aspirational, pending per-function v5 documentation passes.

```
0x0071f270  FUN_0071f270 (intended: ComputeChecksum — file hash computation) [v5: unnamed in current import]
0x007202e0  FUN_007202e0 (intended: HashString)                  [v5: unnamed in current import]
0x00721259  Catch@00721259               (exception handler)
0x0072de40  (target of thunk - file I/O)
0x00739e00  FUN_00739e00 (intended: CRect)                       [v5: unnamed in current import]
```

### Sample Functions (first 30 from 0x0070)
```
0x007004c0  FUN_007004c0
0x00700560  FUN_00700560
0x00700590  FUN_00700590
0x00700600  FUN_00700600
0x00700640  FUN_00700640
0x007006a0  FUN_007006a0
0x00700710  FUN_00700710
0x007007f0  FUN_007007f0
0x007008e0  FUN_007008e0
0x00700a70  FUN_00700a70
0x00700af0  FUN_00700af0
0x00700b40  FUN_00700b40
0x00700bc0  FUN_00700bc0
0x00700d00  FUN_00700d00
0x00700da0  FUN_00700da0
0x00700e00  FUN_00700e00
0x00700f10  FUN_00700f10
0x00700f80  FUN_00700f80
0x00700f90  FUN_00700f90
0x00700fc0  FUN_00700fc0
0x00701070  FUN_00701070
0x00701170  FUN_00701170
0x007011e0  FUN_007011e0
0x00701330  FUN_00701330
0x00701350  FUN_00701350
0x007013b0  FUN_007013b0
0x007013d0  FUN_007013d0
0x00701430  FUN_00701430
0x00701460  FUN_00701460
0x007014c0  FUN_007014c0
```

Key address:
- 0x0099EE38: Python nesting counter (must be 0 for PyRun_String)

---

## Category 18: NetImmerse 3.1 / Rendering Engine
**Range:** 0x00770000 - 0x0084FFFF | **Count:** 2,915 functions

The NetImmerse 3.1 rendering engine (predecessor to Gamebryo): scene graph traversal,
NiNode/NiTriShape/NiTexture classes, Direct3D 7 interface, geometry processing,
texture management, animation system, and particle effects.

### Named/Identified Functions

> [!NOTE]
> Win32/DirectInput import names are correct (resolved by the loader). The `CRect` entry is pre-v5 annotation-script output and is **not currently applied to the Ghidra import**. Addresses are correct (verified 2026-05-28); names are aspirational, pending per-function v5 documentation passes.

```
0x0078c8a0  DirectInputCreateEx          (DirectInput import for input handling)
0x007949b0  (target of thunks - renderer base method)
0x007d9c10  (target of thunks - NI scene method)
0x007dad10  (target of many thunks - NI base object method)
0x007e3880  (target of thunks - NI renderer method)
0x007ef280  (target of thunks - NI renderer method)
0x00815920  FUN_00815920 (intended: CRect)                       [v5: unnamed in current import]
```

Sub-ranges (estimated):
- 0x0077-0x0079: NI core classes (NiObject, NiNode, NiAVObject)
- 0x007A-0x007C: Geometry, mesh, texture management
- 0x007D-0x007F: Renderer, Direct3D 7 interface, surfaces
- 0x0080-0x0082: Animation, keyframes, interpolation
- 0x0083-0x0084: Particles, effects, misc NI utilities

Key addresses:
- 0x0055c860: Crash site patched with RET (PatchHeadlessCrashSites) - ACTIVE

> [!NOTE]
> Legacy patch-tracking entry: 0x7CB322 was the PatchNullSurface target (REMOVED with VEH). Carried forward from pre-v5 docs for historical reference; future patch-changelog refactor may move it out.

---

## Category 19: C Runtime Library (CRT) / Standard Library
**Range:** 0x00850000 - 0x0086FFFF | **Count:** 787 functions

MSVC C runtime library: memory allocation (malloc), string operations (strcmp, strlen,
strchr, strstr, strncpy), math functions (ftol, rand, copysign), file I/O (fclose),
exception handling infrastructure, and floating-point support.

### Named/Identified Functions
```
0x00850870  FUN_00850870                 (start of CRT-adjacent code)
0x00855ada  inet_addr                    (Winsock import thunks)
0x00855ae0  inet_ntoa
0x00855ae6  socket
0x00855aec  closesocket
0x00855af2  connect
0x00855af8  gethostbyname
0x00855afe  htons
0x00855b04  send
0x00855b0a  recv
0x00855b10  setsockopt
0x00855b16  sendto
0x00855b1c  ntohs
0x00855b22  recvfrom
0x00855b28  select
0x00855b2e  __WSAFDIsSet
0x00855b3a  bind
0x00855b40  htonl
0x00855b46  WSAStartup
0x00855b4c  WSACleanup
0x00855b52  ioctlsocket
0x00855b58  gethostname
0x00855b5e  WSAGetLastError
0x00855b64  shutdown
0x008563f1  uflow                        (C++ iostream)
0x00856c1e  _Gninc                       (C++ iostream)
0x008573fe  uflow
0x00857ba2  Gninc
0x0085870c  empty
0x00859378  __global_unwind2             (SEH support)
0x008593ba  __local_unwind2
0x00859422  __abnormal_termination
0x00859445  __NLG_Notify1
0x00859a30  _strchr
0x00859af0  _strrchr
0x00859d20  __ftol                       (float to long conversion)
0x00859df3  _rand
0x0085a078  __fclose_lk
0x0085a160  _strstr
0x0085a680  _strncmp
0x0085a750  _strncpy
0x0085a940  __allshl                     (64-bit shift left)
0x0085a960  __allshr                     (64-bit shift right)
0x0085a9bf  __exit
0x0085ac73  entry                        (CRT entry point)
0x0085ad7b  __amsg_exit
0x0085b028  _malloc
0x0085b03a  __nh_malloc
0x0085ba2b  __CxxThrowException@8        (C++ exception throw)
0x0085f310  __aullshr
0x0085f330  __allmul                      (64-bit multiply)
0x008603e0  _memset
0x00860440  _strlen
0x008608d8  operator=                    (string assignment)
0x008608f7  ~exception                   (exception destructor)
0x00860920  _memcmp
0x00861310  __CallSettingFrame@12
0x008617ea  __fassign
0x00861ada  __cfltcvt
0x00862480  __cintrindisp2               (math dispatch)
0x008624be  __cintrindisp1
0x008624fb  __ctrandisp2
0x0086267b  __ctrandisp1
0x008626ae  __fload
0x008626f0  __trandisp1
0x00862757  __trandisp2
0x00863667  __startOneArgErrorHandling
0x008636f5  __fload_withFB
0x0086375b  __math_exit
0x00863a10  __freebuf
0x008650b3  __frnd                       (floating-point round)
0x00867970  __aulldiv                    (unsigned 64-bit divide)
0x00867ce0  _strcmp
0x00868ae0  __aullrem                    (unsigned 64-bit remainder)
0x00868c4a  __mbsnbicoll                 (multibyte string compare)
0x00868e40  __copysign
0x0086dab8  ___add_12
0x0086efe0  DirectDrawEnumerateA         (DDraw import)
0x0086f760  RtlUnwind                    (Windows SEH)
```

Note: Winsock function imports at 0x00855axx are IAT (Import Address Table) entries,
not actual code. They are jump thunks to the real DLL functions.

---

## Category 20: Exception Handling / Unwind Tables
**Range:** 0x00870000 - 0x008879E0 | **Count:** 4,710 functions

MSVC compiler-generated exception handling: structured exception handling (SEH) unwind
handlers, C++ exception infrastructure, and frame-based exception tables. Nearly all
entries are small "Unwind@ADDR" stubs.

### Named/Identified Functions
```
0x008700e8  FUN_008700e8                 (pre-unwind CRT helpers)
0x00870751  GetCurrentProcessId          (Win32 import)
0x00870fc0  Unwind@00870fc0              (first Unwind handler)
...                                      (~4,692 Unwind handlers)
0x008879e0  Unwind@008879e0              (last function in executable)
```

`Unwind@`/`Catch@` are real Ghidra naming for compiler-generated SEH stubs. These are not game logic.

---

## Summary Table

| # | Category | Range | Count | Key Functions |
|---|----------|-------|-------|---------------|
| 1 | Core/Base Objects | 0x0040-0x0042 | 646 | Base class vtables, TGString |
| 2 | UtopiaApp/Module | 0x0043-0x0045 | 717 | MainTick, InitMultiplayer, SimPipeline |
| 3 | UI Framework | 0x0046-0x004B | 1,241 | Widget library, UI events |
| 4 | Windows/Dialogs | 0x004C-0x0051 | 1,112 | StartGameHandler, SetupMPGame |
| 5 | Game Logic/Ships/AI | 0x0052-0x005A | 2,073 | Ship systems, combat, AI |
| 6 | Sparse/Mission | 0x005B-0x0065 | 201 | Mission framework, cutscenes |
| 7 | Scene Graph/3D | 0x0066-0x0068 | 527 | Scene nodes, spatial objects |
| 8 | Game Session | 0x0069-0x0069D | 159 | Session management |
| 9 | **MultiplayerGame** | 0x0069E-0x006A2 | 45 | Handlers, player slots, MpgameHandleMessage dispatcher |
| 10 | **NetFile/Checksums** | 0x006A3-0x006A7 | 58 | Checksum protocol |
| 11 | Containers/Hash | 0x006A8-0x006AF | 141 | Hash tables, utilities |
| 12 | **TGNetwork** | 0x006B0-0x006BF | 225 | UDP stack, reliable delivery |
| 13 | Streams/Serial | 0x006C0-0x006CF | 246 | TGStream, binary I/O |
| 14 | **Events/Timers** | 0x006D0-0x006DF | 327 | EventManager, dispatch |
| 15 | Config/VarMgr | 0x006E0-0x006EF | 226 | TGConfigMapping |
| 16 | GameSpy/SWIG | 0x006F0-0x006FF | 273 | GameSpy SDK, bindings |
| 17 | Python/SWIG | 0x0070-0x0076 | 1,620 | Python 1.5, Appc module |
| 18 | NetImmerse/Render | 0x0077-0x0084 | 2,915 | NI 3.1, D3D7, textures |
| 19 | CRT/stdlib | 0x0085-0x0086 | 787 | malloc, strcmp, Winsock IAT |
| 20 | Exception/Unwind | 0x0087-0x0088 | 4,710 | SEH unwind handlers |
| | **TOTAL (in-body)** | | **18,249** | |
| | **TOTAL (incl. EXTERNAL)** | | **18,576** | 327 import thunks |

---

## Cross-Reference: All Known Function Names

Consolidated from decompiled-functions.md, multiplayer-flow.md, dedicated-server.md:

```
ADDRESS     IDENTIFIER                          CATEGORY
----------- ----------------------------------- --------
0x0043b4f0  UtopiaApp_MainTick                  App
0x00438AE6  [was PatchInitTraversal - REMOVED]    App
0x0043B1D2  [PatchInitAbort target]              App
0x0043B1D7  [was PatchInitSkipPython - REMOVED]  App
0x004433EA  [PatchRenderTick target]             App
0x00445d90  UtopiaModule::InitMultiplayer        App
0x00451ac0  SimulationPipelineTick               App
0x005046b0  RegisterMPWindowHandlers             Window
0x00504890  MultiplayerWindow::StartGameHandler  Window
0x00504f10  TopWindow_SetupMultiplayerGame       Window
0x0055c860  [PatchHeadlessCrashSites target]     Game
0x0069efe0  RegisterMPGameHandlers               MPGame
0x0069f2a0  MpgameHandleMessage                  MPGame  [v5-validated 2026-05-28; opcodes 0x02-0x2A, jump table 0x0069F534]
0x006a07d0  EnterSetHandler (handler addr)       MPGame
0x006a0a10  ExitedWarpHandler (handler addr)     MPGame
0x006a0a20  DisconnectHandler (handler addr)     MPGame
0x006a0a30  NewPlayerHandler                     MPGame
0x006a0c60  SystemChecksumPassedHandler (addr)   MPGame
0x006a0c90  SystemChecksumFailedHandler (addr)   MPGame
0x006a0ca0  DeletePlayerHandler (handler addr)   MPGame
0x006a0f90  ObjectCreatedHandler (handler addr)  MPGame
0x006a1150  HostEventHandler (handler addr)      MPGame
0x006a1240  ObjectExplodingHandler (addr)        MPGame
0x006a1590  NewPlayerInGameHandler (addr)        MPGame
0x006a1790  StartFiringHandler (handler addr)    MPGame
0x006a17a0  StartWarpHandler (handler addr)      MPGame
0x006a17b0  TorpedoTypeChangedHandler (addr)     MPGame
0x006a18d0  StopFiringHandler (handler addr)     MPGame
0x006a18e0  StopFiringAtTargetHandler (addr)     MPGame
0x006a18f0  StartCloakingHandler (handler addr)  MPGame
0x006a1900  StopCloakingHandler (handler addr)   MPGame
0x006a1910  SubsystemStateChangedHandler (addr)  MPGame
0x006a1920  AddToRepairListHandler (addr)        MPGame
0x006a1930  ClientEventHandler (handler addr)    MPGame
0x006a1940  RepairListPriorityHandler (addr)     MPGame
0x006a1970  SetPhaserLevelHandler (handler addr) MPGame
0x006a1a60  DeleteObjectHandler (handler addr)   MPGame
0x006a1a70  ChangedTargetHandler (handler addr)  MPGame
0x006a1b10  ChecksumCompleteHandler              MPGame
0x006a2640  KillGameHandler (handler addr)       MPGame
0x006a2a40  RetryConnectHandler (handler addr)   MPGame
0x006a30c0  NetFile_Constructor                  NetFile
0x006a3560  RegisterNetFileHandler               NetFile
0x006a3820  ChecksumRequestSender                NetFile
0x006a39b0  ChecksumRequestBuilder               NetFile
0x006a3cd0  NetFile::ReceiveMessageHandler        NetFile
0x006a4250  Opcode0x27Handler                    NetFile
0x006a4260  ChecksumResponseEntry                NetFile
0x006a4560  ChecksumResponseVerifier             NetFile
0x006a4a00  ChecksumFail                         NetFile
0x006a4bb0  ChecksumAllPassed                    NetFile
0x006a4d80  ExtractDirFilterFromMsg              NetFile
0x006a5290  ChecksumSuccess                      NetFile
0x006a5860  FileTransferProcessor                NetFile
0x006a5df0  Client_ChecksumRequestHandler        NetFile
0x006a6500  CleanupPlayerState                   NetFile
0x006a6630  ClientChecksumInit                   NetFile
0x006a7770  InitializePlayerSlot                 NetFile
0x006b3ec0  TGNetwork_HostOrJoin                 Network
0x006b4560  TGNetwork::Update                    Network
0x006b4c10  TGNetwork::Send                      Network
0x006b5080  QueueMessageToPeer                   Network
0x006b55b0  SendOutgoingPackets                  Network
0x006b5c90  ProcessIncomingPackets               Network
0x006b5f70  DispatchIncomingQueue                Network
0x006b61e0  ReliableACKHandler                   Network
0x006b6ad0  DispatchToApplication                Network
0x006b8670  ResetRetryCounter                    Network
0x006b9b20  CreateUDPSocket                      Network
0x006b9bb0  SetPortNumber                        Network
0x006da130  RegisterHandlerFunction              Events
0x006da2c0  EventManager::ProcessEvents          Events
0x006da300  DispatchSingleEvent                  Events
0x006db380  RegisterEventHandler                 Events
0x006db620  DispatchToHandlerChain               Events
0x0071f270  ComputeChecksum                      Python
0x007202e0  HashString                           Python
```

---

## Global Memory Map (for reference)

```
0x0097e238  TopWindow/Game ptr       (also MultiplayerGame)
0x0097F838  EventManager
0x0097F864  Handler Registry         (EventManager+0x2C)
0x0097f94c  SkipChecksum flag
0x0097FA00  UtopiaModule base
0x0097FA78  WSN pointer              (UtopiaModule+0x78)
0x0097FA7C  GameSpy pointer          (UtopiaModule+0x7C)
0x0097FA80  NetFile/ChecksumMgr      (UtopiaModule+0x80)
0x0097FA88  IsHost (BYTE)            (UtopiaModule+0x88)
0x0097FA8A  IsMultiplayer (BYTE)     (UtopiaModule+0x8A)
0x0099EE38  Python nesting counter
0x009a09d0  Clock object ptr         (+0x90=gameTime, +0x54=frameTime)
```
