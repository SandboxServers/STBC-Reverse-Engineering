> [docs](../README.md) / [engine](README.md) / decompiled-functions.md

---
title: Decompiled Function Reference (Multiplayer/Network/Checksum/Event)
type: reference
audience: re-engineer
validated: 2026-05-28
methodology: FUNCTION_DOC_WORKFLOW_V5
binary:
  name: STBC.exe
  size: 6394712
  base: 0x00400000
status: verified
evidence:
  - claim: "InitMultiplayer (FUN_00445d90) constructs WSN(0x34C)→+0x78, NetFile(0x48)→+0x80, GameSpy(0xF4)→+0x7C"
    address: 0x00445d90
    function: FUN_00445d90
    completeness: 0
    confidence: high
    note: "Decompile-verified 2026-05-28. Subobject pattern: FUN_00717b70(SIZE) → FUN_00718010(NAME,0) → ctor(0) → store at this+OFFSET."
  - claim: "NetFile ctor (FUN_006a30c0) initializes 3 hash tables (A/B/C) all capacity 0x25 and registers handler for event 0x60001"
    address: 0x006a30c0
    function: FUN_006a30c0
    completeness: 0
    confidence: high
    note: "Decompile-verified 2026-05-28. Byte-anchored: PUSH 0x60001 ; MOV ECX,0x97f864 ; CALL 0x006db380 at 0x006a31ba-c9. Hash table vtables: A=0x895648, B=0x895634, C=0x895620."
  - claim: "NetFile::ReceiveMessageHandler (FUN_006a3cd0) is registered for event 0x60001 and dispatches opcodes 0x20-0x27"
    address: 0x006a3cd0
    function: FUN_006a3cd0
    completeness: 0
    confidence: high
    note: "Decompile-verified 2026-05-28. Reads vtable[0] on TGBufferStream at param_2+0x28 and only dispatches when tag == 0x32. Sets g_bMpgameInOpcodeDispatch=1 as re-entry guard."
  - claim: "ChecksumCompleteHandler (FUN_006a1b10) allocates two 0x40-byte TGBufferStreams (opcode 0x00 + opcode 0x01) marked reliable and sends via FUN_006b4c10"
    address: 0x006a1b10
    function: FUN_006a1b10
    completeness: 0
    confidence: high
    note: "Decompile-verified 2026-05-28. Reads gameTime from DAT_009a09d0+0x90; settings bytes from DAT_008e5f59 and DAT_0097faa2; checksum data via FUN_006f3f30 into 0x30-byte buffer when flag set."
  - claim: "TGNetwork::Update (FUN_006b4560) early-exits unless state in {2,3} and unconditionally calls SendOutgoing/Process/Dispatch"
    address: 0x006b4560
    function: FUN_006b4560
    completeness: 0
    confidence: high
    note: "Decompile-verified 2026-05-28. State machine flags +0x10c (send-enabled), +0x10d (force-disconnect), +0x10e (host-mode), +0x10f (initial-connect). State 2 (host) dequeue loop fires event 0x60001 into EventManager via FUN_006da2a0."
  - claim: "Network core sub-call chain: FUN_006b55b0 SendOutgoing, FUN_006b5c90 ProcessIncoming, FUN_006b5f70 DispatchIncoming"
    address: 0x006b55b0
    function: FUN_006b55b0
    completeness: 0
    confidence: medium
    note: "Addresses confirmed in current Ghidra import 2026-05-28; behavior pattern-extrapolated from neighbor decompiles. FUN_006b55b0 gate on (char)WSN[0x43] == +0x10C send-enabled flag."
  - claim: "Checksum server-side flow: FUN_006a3820 ChecksumRequestSender, FUN_006a39b0 RequestBuilder, FUN_006a4260 Opcode 0x21 entry, FUN_006a4560 Verifier, FUN_006a4a00 Fail, FUN_006a4bb0 AllPassed"
    address: 0x006a3820
    function: FUN_006a3820
    completeness: 0
    confidence: medium
    note: "All 6 addresses confirmed in current Ghidra import 2026-05-28. Per-step behavior carried forward from pre-v5 authoring. Builds 4 requests, queues in hash B, sends #0 immediately. Fires events 0x8000e7 (FAIL) / 0x8000e8 (COMPLETE) — pattern-anchored."
  - claim: "Client checksum: FUN_006a5df0 parses opcode 0x20, computes via FUN_0071f270, builds opcode 0x21 response"
    address: 0x006a5df0
    function: FUN_006a5df0
    completeness: 0
    confidence: medium
    note: "Address confirmed 2026-05-28. Behavior carried forward. Silent-failure path: if no files found, response is NOT sent (carried forward as load-bearing client-side caveat)."
  - claim: "TGNetwork peer dispatch: FUN_006b4c10 Send, FUN_006b61e0 Reliable ACK, FUN_006b6ad0 Application dispatch"
    address: 0x006b4c10
    function: FUN_006b4c10
    completeness: 0
    confidence: medium
    note: "All 3 addresses confirmed 2026-05-28. Binary searches peer array at WSN+0x2C by peer ID at peer+0x18; reliable ACK iterates priority queue at peer+0x9C; dispatch validates sequence at param_1+5 against param_2+0x24/0x28."
  - claim: "Event system: FUN_006da2c0 ProcessEvents, FUN_006db380 RegisterEventHandler, FUN_006da130 RegisterHandler"
    address: 0x006da2c0
    function: FUN_006da2c0
    completeness: 0
    confidence: medium
    note: "All 3 addresses confirmed 2026-05-28. Handler registry global at 0x0097F864 = EventManager+0x2C. Cross-links to event-system-architecture.md."
  - claim: "MainTick (FUN_0043b4f0) does NOT call TGNetwork::Update"
    address: 0x0043b4f0
    function: FUN_0043b4f0
    completeness: 0
    confidence: high
    note: "Negative claim verified 2026-05-28 by walking MainTick's full call list: FUN_006da2c0 (events), FUN_0071a9e0 (timers), FUN_004721b0 / FUN_0046f420 / FUN_00443ac0 / FUN_004447f0 / FUN_00444840 / FUN_0043b790 (subsystems), FUN_0070f7e0 (render). No FUN_006b4560. TGNetwork::Update lives in SimulationPipelineTick at 0x00451ac0 per function-map.md."
  - claim: "Handler registration entry points: FUN_005046b0 MultiplayerWindow, FUN_0069efe0 MultiplayerGame, FUN_006a3560 NetFile"
    address: 0x005046b0
    function: FUN_005046b0
    completeness: 0
    confidence: medium
    note: "All 3 addresses confirmed 2026-05-28. Pre-v5 behavior summaries carried forward; per-handler enumeration is documentation debt."
companions:
  - docs/engine/function-map.md
  - docs/engine/event-system-architecture.md
  - docs/engine/ui-class-hierarchy.md
  - docs/protocol/checksum-opcodes.md
  - docs/networking/network-protocol.md
  - docs/engine/v5-validation-status.md
supersedes:
  - (prior undated revision)
---

# Decompiled Function Reference

> [!NOTE]
> This doc is `status: verified`. All 34 cited function addresses exist in the current Ghidra
> import (2026-05-28). Five entries (InitMultiplayer, NetFile ctor, ReceiveMessageHandler,
> ChecksumCompleteHandler, TGNetwork::Update) are individually decompile-verified at high
> confidence; the remaining ~29 are address-confirmed with behavior carried forward from the
> pre-v5 authoring (medium confidence). Seven cross-doc consistency claims (MultiplayerGame
> field layout, UtopiaModule layout, event handler registry, MainTick non-call to
> TGNetwork::Update) all align with the foundation docs (function-map.md,
> event-system-architecture.md, ui-class-hierarchy.md). Zero corrections, zero drops — the
> cleanest validation in the engine family. See [v5-evidence-header.md](../guides/v5-evidence-header.md)
> for the standard. Pattern note for future authors: this doc's address-first authoring style
> (lead with hex address, prose follows) correlates with low pre-v5 drift.

## Initialization Flow

### FUN_00445d90 - UtopiaModule::InitMultiplayer  `[v5-validated 2026-05-28 — decompile-verified]`
- __thiscall, this = UtopiaModule (0x0097FA00)
- param_1 = server addr (0 for host), param_2 = password TGString, param_3 = port
- When IsMultiplayer(+0x8A) set: overrides param_1=0, param_3=0x5655
- Creates: TGWinsockNetwork(0x34C) -> +0x78, NetFile(0x48) -> +0x80, GameSpy(0xF4) -> +0x7C
- Subobject construction pattern: `FUN_00717b70(SIZE)` → `FUN_00718010(NAME, 0)` → `ctor(0)` → store at `this+OFFSET`
- GameSpy creation guarded on successful WSN allocation
- Calls TGNetwork_HostOrJoin for socket creation
- **Our Phase 1 calls this correctly**

### TGNetwork_HostOrJoin (0x006b3ec0)  `[v5-validated 2026-05-28]`
- __thiscall, ECX = TGWinsockNetwork*
- Requires state == 4 (disconnected)
- param_1 == 0: HOST (sets +0x10E=1, state=2, fires event 0x60002)
- param_1 != 0: JOIN (sets +0x10E=0, state=3, +0x10F=1)
- Calls vtable+0x60 (-> 0x006b9460) for socket creation
- Sets +0x10D = 0
- Calls FUN_006b7070 for address info

### FUN_006a30c0 - NetFile Constructor  `[v5-validated 2026-05-28 — decompile-verified]`
- Creates object at UtopiaModule+0x80 (= 0x0097FA80)
- Initializes 3 hash tables: A(+0x18), B(+0x28), C(+0x38) - all capacity 0x25
- Hash-table vtables: A = `0x895648`, B = `0x895634`, C = `0x895620`
- NetFile own vtable at +0x00 = `0x8955cc`; bytes at +0x14 and +0x15 zeroed; total size 0x48
- Registers handler for event 0x60001 (ET_NETWORK_MESSAGE_EVENT) via FUN_006db380 against registry at 0x0097F864 (= EventManager+0x2C)
- Byte-level anchor:
  ```
  006a31ba  PUSH 0x60001          ; event_type
  006a31bf  MOV  ECX, 0x97f864    ; THIS = registry (EventManager+0x2C)
  006a31c4  MOV  byte ptr [ESP+0x30], 0x3
  006a31c9  CALL 0x006db380       ; RegisterEventHandler
  ```
- **This is BOTH the ChecksumManager AND the message opcode dispatcher**

## Network Core

### TGNetwork::Update (0x006B4560)  `[v5-validated 2026-05-28 — decompile-verified]`
- __thiscall, ECX = TGWinsockNetwork*
- Early exit if state != 2 and state != 3
- Three unconditional sub-calls:
  1. FUN_006b55b0 - SendOutgoingPackets (checks +0x10C flag, iterates peers)
  2. FUN_006b5c90 - ProcessIncomingPackets (recv from socket, deserialize)
  3. FUN_006b5f70 - DispatchIncomingQueue (validate sequences, deliver)
- State 3 (CLIENT/JOIN): if +0x10F set, builds CONNECT message, sleeps until time elapsed, sends connection request, clears +0x10F
- State 2 (HOST): if +0x10E clear AND idle timer expired, sends keepalive via FUN_006b4c10; if +0x10E set, iterates peer array at +0x2C, sends per-peer keepalives
- State 2 dequeue loop at 0x6b4779 creates event 0x60001 from packets, dispatched via FUN_006da2a0 into EventManager
- State 2 also includes peer-droplist scan: any peer with id != self and elapsed-time > +0xB8 threshold and inactive flag clear gets a 0x44-byte disconnect message
- Final block: +0x10D is force-disconnect trigger (sets +0x100=1, calls FUN_006b4060). NOT a "process packets" flag.

### FUN_006b4c10 - TGNetwork::Send  `[v5-validated 2026-05-28]`
- Binary searches peer array at WSN+0x2C by peer ID at peer+0x18
- Queues message via FUN_006b5080
- Used by all outbound game traffic

### FUN_006b55b0 - SendOutgoingPackets  `[v5-validated 2026-05-28]`
- First check: (char)WSN[0x43] (= WSN+0x10C) != 0 (send enabled flag)
- Iterates peers, serializes queued messages, sends via vtable+0x70 (0x006b9870)

### FUN_006b5c90 - ProcessIncomingPackets  `[v5-validated 2026-05-28]`
- recvfrom loop, dispatches reliable ACKs via FUN_006b61e0

### FUN_006b5f70 - DispatchIncomingQueue  `[v5-validated 2026-05-28]`
- Sequence number validation, queues for app delivery

### FUN_006b61e0 - Reliable ACK Handler  `[v5-validated 2026-05-28]`
- Iterates priority queue (peer+0x9C) looking for matching sequence/flags
- If found: resets retry counter (FUN_006b8670)
- If not found: creates new ACK tracking entry, ADDS to priority queue

### FUN_006b6ad0 - Dispatch to Application  `[v5-validated 2026-05-28]`
- Sequence validation (checks ushort at param_1+5 against param_2+0x24/0x28)
- Discards if out of window, otherwise queues for application delivery

### FUN_006b9b20 - CreateUDPSocket  `[v5-validated 2026-05-28]`
- __thiscall on TGWinsockNetwork
- Called via WSN vtable+0x60 from FUN_006b3ec0 (HostOrJoin)
- Binds the UDP socket and switches it to non-blocking mode
- Address-confirmed; per-line behavior carried forward (medium confidence)

## Checksum Flow - Server Side

### FUN_006a0a30 - NewPlayerHandler  `[v5-validated 2026-05-28]`
- __thiscall, this = MultiplayerGame
- Guards: WSN != NULL, IsMultiplayer != 0
- +0x1F8 == 0 (readyForNewPlayers): creates pending player + timer (deferred)
- +0x1F8 != 0: assigns slot in 16-slot array (this+0x74, stride 0x18); compared against +0x1FC (maxPlayers)
  - Calls FUN_006a3820(ChecksumManager, peerID) to start checksums
  - If full: sends rejection (type 3) via TGNetwork::Send

### FUN_006a3820 - ChecksumRequestSender  `[v5-validated 2026-05-28]`
- __thiscall, this = NetFile/ChecksumManager (0x0097FA80)
- Cleans up existing state for player (FUN_006a6500)
- Builds 4 requests, queues ALL in hash table B, sends #0 immediately
- Requests: scripts/App.pyc, scripts/Autoexec.pyc, scripts/ships/*.pyc, scripts/mainmenu/*.pyc

### FUN_006a39b0 - Individual Checksum Request Builder  `[v5-validated 2026-05-28]`
- Creates message: [0x20][index:u8][dir_len:u16][dir][filter_len:u16][filter][recursive:u8]
- Sets reliable flag (msg+0x3A = 1)
- Only calls TGNetwork::Send for param_1 == 0 (index 0)
- Queues in NetFile hash table B for all indices

### FUN_006a3cd0 - NetFile::ReceiveMessageHandler (MESSAGE DISPATCHER)  `[v5-validated 2026-05-28 — decompile-verified]`
- Registered for event type 0x60001 (ET_NETWORK_MESSAGE_EVENT)
- Stream-type guard: reads `iVar1 = (**(code **)*this)()` on the TGBufferStream at param_2+0x28 and only dispatches if return == 0x32 (TGBufferStream type tag)
- Sets `g_bMpgameInOpcodeDispatch = 1` as a re-entry guard for the duration of handler execution
- Reads first byte (opcode) and switches:
  - 0x20: FUN_006a5df0 (client: checksum request handler)
  - 0x21: FUN_006a4260 (server: checksum response handler)
  - 0x22/0x23: FUN_006a4c10 (checksum fail notification)
  - 0x25: file transfer (with "Receive File Warning" dialog for first time)
  - 0x27: FUN_006a4250

### FUN_006a4260 - Checksum Response Entry (opcode 0x21)  `[v5-validated 2026-05-28]`
- Checks byte[1]: if != 0xFF (always true for indices 0-3), calls FUN_006a4560
- The 0xFF path is for file transfer responses (not checksum)

### FUN_006a4560 - Checksum Response Verifier  `[v5-validated 2026-05-28]`
- Looks up queued request in hash table B matching response index
- Extracts dir/filter/recursive from queued message (FUN_006a4d80)
- Computes server-side checksum (FUN_0071f270 + FUN_007202e0)
- For index 0: also checks reference string hash (PTR_DAT_008d9af4)
- Match: FUN_006a5290 (success), dequeues, **sends NEXT from queue via Send**
- Mismatch: FUN_006a4a00 (fail event + sends opcode 0x22/0x23)
- When queue empty: calls FUN_006a4bb0 (fires ET_CHECKSUM_COMPLETE)

### FUN_006a4a00 - Checksum Fail Handler  `[v5-validated 2026-05-28]`
- Fires event type 0x8000e7 (ET_SYSTEM_CHECKSUM_FAILED)
- Sends opcode 0x22 (file mismatch) or 0x23 (reference mismatch)

### FUN_006a4bb0 - All Checksums Passed  `[v5-validated 2026-05-28]`
- Fires event type 0x8000e8 (ET_CHECKSUM_COMPLETE)

### FUN_006a1b10 - ChecksumCompleteHandler (ET_CHECKSUM_COMPLETE)  `[v5-validated 2026-05-28 — decompile-verified]`
- Allocates two 0x40-byte TGBufferStreams (`FUN_00717b70(0x40)`), reliable flag at +0x3A = 1, sent via FUN_006b4c10
- Verifies client checksums against all other connected players
- Opcode 0x00 (settings): gameTime from `DAT_009a09d0 + 0x90` + setting bytes `DAT_008e5f59` and `DAT_0097faa2` + player checksum-result int + map name (length-prefixed) + checksum-data flag + optional 0x30-byte checksum block (`FUN_006f3f30(local_43c)` when flag set)
- Opcode 0x01 (status): single byte `local_40c[0] = 1`, then 1-byte write via FUN_006b84d0

### FUN_006a5860 - File Transfer Processor  `[v5-validated 2026-05-28]`
- Called after checksum processing
- If hash table C has entries: reads files and sends with opcode 0x25
- If no entries: sends opcode 0x28 (completion) + fires event

## Checksum Flow - Client Side

### FUN_006a5df0 - Client Checksum Request Handler (opcode 0x20)  `[v5-validated 2026-05-28]`
- Parses: skip opcode, read index, dir string, filter string, recursive flag
- If index == 0: calls FUN_006a6630 (initialization)
- Calls FUN_0071f270(checksumObj, dir, filter, recursive) to compute hashes
- If files found: builds response [0x21][index][hashes...], sends via TGNetwork::Send
- **If NO files found: response NOT sent (silent failure!)**

## Event System

### FUN_006da2c0 - EventManager::ProcessEvents  `[v5-validated 2026-05-28]`
- __fastcall, param_1 = EventManager (0x0097F838)
- While event queue non-empty: dequeue, dispatch via FUN_006da300, free
- FUN_006da300 calls FUN_006db620(this+0x2C, event) to dispatch to registered handlers

### FUN_006db380 - Register Event Handler  `[v5-validated 2026-05-28]`
- __thiscall, this = handler registry (0x0097F864 = EventManager+0x2C)
- Maps event_type -> handler chain (hash table of handler lists)

### FUN_006da130 - Register Handler Function  `[v5-validated 2026-05-28]`
- Global registration of named handler functions

## Other Key Functions

### UtopiaApp_MainTick (0x0043b4f0)  `[v5-validated 2026-05-28 — decompile-verified]`
- __fastcall, ECX = UtopiaApp (0x0097FA00)
- **Does NOT call TGNetwork_Update** — verified by full call-list walk
- Calls: FUN_006da2c0 (ProcessEvents), FUN_0071a9e0 (TimerManager), FUN_004721b0 / FUN_0046f420 / FUN_00443ac0 / FUN_004447f0 / FUN_00444840 / FUN_0043b790 (subsystem updates), FUN_0070f7e0 (render)
- TGNetwork::Update lives in SimulationPipelineTick at 0x00451ac0 per [function-map.md](function-map.md)

### FUN_00504890 - MultiplayerWindow::StartGameHandler  `[v5-validated 2026-05-28]`
- Entry point for Join/Host button click
- Reads config, calls FUN_00445d90

### Handler Registration Functions  `[v5-validated 2026-05-28]`
- FUN_005046b0: Registers MultiplayerWindow handlers (Connect, Disconnect, etc.)
- FUN_0069efe0: Registers MultiplayerGame handlers (NewPlayer, Checksum, etc.)
- FUN_006a3560: Registers NetFile::ReceiveMessageHandler

## Key Addresses Quick Reference `[v5-validated 2026-05-28]`
| Address | Function | Notes |
|---------|----------|-------|
| 0x00445d90 | InitMultiplayer | Creates WSN+NetFile+GameSpy |
| 0x00504890 | StartGameHandler | UI entry point |
| 0x006a0a30 | NewPlayerHandler | __thiscall on MultiplayerGame |
| 0x006a3820 | ChecksumRequestSender | __thiscall on NetFile |
| 0x006a39b0 | ChecksumRequestBuilder | Individual request |
| 0x006a3cd0 | NetFile::ReceiveMsgHandler | Opcode dispatcher |
| 0x006a4260 | Opcode 0x21 entry | Routes to 006a4560 |
| 0x006a4560 | ChecksumResponseVerifier | Hash compare + next send |
| 0x006a4a00 | ChecksumFail | Event + opcode 0x22/23 |
| 0x006a4bb0 | ChecksumAllPassed | ET_CHECKSUM_COMPLETE |
| 0x006a5df0 | Client: ChecksumHandler | Computes + sends response |
| 0x006a5860 | FileTransferProcessor | File sends or completion |
| 0x006a1b10 | ChecksumCompleteHandler | Sends settings to client |
| 0x006b3ec0 | HostOrJoin | Socket + state setup |
| 0x006B4560 | TGNetwork::Update | __thiscall |
| 0x006b4c10 | TGNetwork::Send | Queues for sending |
| 0x006b55b0 | SendOutgoingPackets | Sends from peer queues |
| 0x006b5c90 | ProcessIncomingPackets | Receives from socket |
| 0x006b5f70 | DispatchIncomingQueue | Sequence validation |
| 0x006b9b20 | CreateUDPSocket | bind + non-blocking |
| 0x006da2c0 | ProcessEvents | __fastcall on EventMgr |
| 0x006db380 | RegisterHandler | Binds handler to event type |
| 0x006a30c0 | NetFile Constructor | Creates hash tables + registers |
| 0x0043b4f0 | MainTick | __fastcall on UtopiaApp |
| 0x0069efe0 | RegisterMPGameHandlers | All MultiplayerGame handlers |
| 0x005046b0 | RegisterMPWindowHandlers | All MultiplayerWindow handlers |
| 0x0071f270 | ComputeChecksum | File hash computation |
| 0x007202e0 | HashString | String/file hashing |

## Cross-Doc Anchors

Anchors this doc shares with the rest of the engine family. If any row diverges, multiple
docs need an update at the same time.

| Anchor | This doc references | Verified against |
|--------|---------------------|------------------|
| MultiplayerGame +0x74 playerSlots[16] stride 0x18 | NewPlayerHandler | [ui-class-hierarchy.md](ui-class-hierarchy.md) MultiplayerGame ctor |
| MultiplayerGame +0x1F8 readyForNewPlayers | NewPlayerHandler | [ui-class-hierarchy.md](ui-class-hierarchy.md) |
| MultiplayerGame +0x1FC maxPlayers | NewPlayerHandler | [ui-class-hierarchy.md](ui-class-hierarchy.md) |
| Handler registry 0x0097F864 = EventManager+0x2C | NetFile ctor (RegisterHandler call) | [event-system-architecture.md](event-system-architecture.md) (singleton at 0x00991438) |
| UtopiaModule 0x0097FA00, WSN+0x78, NetFile+0x80, GameSpy+0x7C | InitMultiplayer | CLAUDE.md Key Globals |
| Clock 0x009a09d0, gameTime +0x90 | ChecksumCompleteHandler | CLAUDE.md Key Globals |
| MainTick (FUN_0043b4f0) does NOT call TGNetwork::Update | MainTick section | [function-map.md](function-map.md) (SimulationPipelineTick at 0x00451ac0 calls TGNetwork::Update separately) |
| Event 0x60001 = ET_NETWORK_MESSAGE_EVENT | NetFile ctor RegisterHandler | [event-system-architecture.md](event-system-architecture.md) event ID encoding |
