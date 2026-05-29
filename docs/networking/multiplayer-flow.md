> [docs](../README.md) / [networking](README.md) / multiplayer-flow.md

---
title: Complete Multiplayer Join Flow
type: reference
audience: RE engineer, OpenBC implementer
status: partial
verified: 2026-05-28
methodology: FUNCTION_DOC_WORKFLOW_V5
binary: STBC.exe (image base 0x00400000)
companions:
  - docs/networking/network-protocol.md
  - docs/protocol/checksum-opcodes.md
  - docs/protocol/game-opcodes.md
  - docs/engine/ui-class-hierarchy.md
evidence:
  - claim: "MultiplayerWindow::StartGameHandler at 0x00504890 routes Join Multiplayer click to UtopiaModule::InitMultiplayer or forwards to PlayWindow vtable+0x68 when already in multiplayer"
    address: "0x00504890"
    function: "FUN_00504890"
    confidence: high
    note: "PlayWindow ref is DAT_0097e238 (NOT TopWindow DAT_009878cc — same function uses both)"
  - claim: "UtopiaModule::InitMultiplayer at 0x00445d90 constructs WSN (0x34C bytes), sets WSN+0x338 port, creates NetFile + GameSpy"
    address: "0x00445d90"
    function: "FUN_00445d90"
    confidence: high
  - claim: "TGNetwork_HostOrJoin at 0x006b3ec0 branches host (WSN+0x10E=1, state=2 at WSN+0x14) vs join (WSN+0x10E=0, WSN+0x10F=1, state=3)"
    address: "0x006b3ec0"
    function: "TGWinsockNetwork_HostOrJoin"
    confidence: high
  - claim: "WSN port-setter at 0x006b9bb0 stores UDP port at WSN+0x338"
    address: "0x006b9bb0"
    function: "FUN_006b9bb0"
    confidence: high
  - claim: "TGWinsockNetwork_ProcessIncomingPackets at 0x006b5c90 uses WSN+0x2C (sorted peer-array ptr) + WSN+0x30 (count); binary search keyed by peer+0x18"
    address: "0x006b5c90"
    function: "FUN_006b5c90"
    confidence: high
    note: "Anchors Phase 5 peer-array detection"
  - claim: "MultiplayerGame::NewPlayerHandler at 0x006a0a30 iterates 16 player slots at MpgameBase+0x78, 0x18-byte stride, slot[0] active byte at +0x78, peer ID at +0x7C"
    address: "0x006a0a30"
    function: "FUN_006a0a30"
    confidence: high
    note: "Computed as (slot*3+0xf)*8; pcVar7 = (char *)(param_1 + 0x78)"
  - claim: "MultiplayerGame ready-flag at MpgameBase+0x1F8 gates accept-or-defer; MaxPlayers at +0x1FC bounds active count"
    address: "0x006a0a30"
    function: "FUN_006a0a30"
    confidence: high
  - claim: "Not-ready retry at MpgameBase+0x1F8=0 schedules timer for gameTime + DAT_00888860 (fixed delay, no backoff)"
    address: "0x006a0a30"
    function: "FUN_006a0a30"
    confidence: high
  - claim: "ChecksumRequestSender at 0x006a3820 queues 4 requests (App.pyc, Autoexec.pyc, ships/, mainmenu/), sends only index 0 immediately"
    address: "0x006a3820"
    function: "FUN_006a3820"
    confidence: high
  - claim: "ChecksumRequestBuilder at 0x006a39b0 emits opcode 0x20 [index][dir_len][dir][filter_len][filter][recursive], sets reliable flag at msg+0x3A"
    address: "0x006a39b0"
    function: "FUN_006a39b0"
    confidence: high
  - claim: "NetFile::ReceiveMessageHandler at 0x006a3cd0 dispatches opcodes 0x20-0x28 (NetFile dispatcher)"
    address: "0x006a3cd0"
    function: "FUN_006a3cd0"
    confidence: high
    note: "Anchored by protocol mid #5 (checksum-opcodes.md)"
  - claim: "Opcode 0x21 entry at 0x006a4260 branches on byte[1]: !=0xFF -> FUN_006a4560 (checksum path); ==0xFF -> FUN_006a4e70 / FUN_006a5570 + FUN_006a5860 (file-transfer path)"
    address: "0x006a4260"
    function: "FUN_006a4260"
    confidence: high
  - claim: "ChecksumResponseVerifier at 0x006a4560 compares client hash vs server hash; index 0 also checks reference string hash PTR_DAT_008d9af4"
    address: "0x006a4560"
    function: "FUN_006a4560"
    confidence: high
  - claim: "ChecksumFail at 0x006a4a00 sends opcode 0x22 (param_4=0, file fail) or 0x23 (param_4=1, ref string fail)"
    address: "0x006a4a00"
    function: "FUN_006a4a00"
    confidence: high
    note: "Anchored by protocol mid #5"
  - claim: "ChecksumAllPassed at 0x006a4bb0 posts event 0x008000e8 (ET_CHECKSUM_COMPLETE)"
    address: "0x006a4bb0"
    function: "FUN_006a4bb0"
    confidence: high
  - claim: "Client checksum request handler at 0x006a5df0 parses opcode 0x20 payload, calls FUN_0071f270 to compute checksums; on zero files found, builds 6-byte placeholder response [0x21][index][optional ref hash sentinel][placeholder file hash+1] and sends via FUN_006b89a0 (unreliable send path)"
    address: "0x006a5df0"
    function: "FUN_006a5df0"
    confidence: high
    note: "Bug-premise correction: not a silent drop — different transport"
  - claim: "ChecksumCompleteHandler at 0x006a1b10 reads slot 0 peer ID at MpgameBase+0x7C, walks slots at +0x7C with 0x18-byte stride, sends opcode 0x00 (Settings) then opcode 0x01 (GameInit)"
    address: "0x006a1b10"
    function: "FUN_006a1b10"
    confidence: high
  - claim: "Settings packet (opcode 0x00) wire format: WriteChar(0) WriteFloat(gameTime) WriteBool_Bit(DAT_008e5f59) WriteBool_Bit(DAT_0097faa2) WriteChar(playerSlot) WriteShort(mapLen) WriteBytes(mapName) WriteBool_Bit(passFail) [if passFail: FUN_006f3f30 hash block]"
    address: "0x006a1b10"
    function: "FUN_006a1b10"
    confidence: high
    note: "Three boolean fields are SINGLE BITS via WriteBool_Bit, not bytes"
  - claim: "FileTransferProcessor at 0x006a5860 sends files or completion message; client queue-empty path sends opcode 0x28 and posts event 0x008000e6"
    address: "0x006a5860"
    function: "FUN_006a5860"
    confidence: high
  - claim: "TGNetwork::Send (SendTGMessage) at 0x006b4c10 queues reliable/unreliable messages for transport"
    address: "0x006b4c10"
    function: "TGWinsockNetwork_SendTGMessage"
    confidence: high
  - claim: "ComputeChecksum at 0x0071f270 scans directory and computes file hashes (called both client and server)"
    address: "0x0071f270"
    function: "FUN_0071f270"
    confidence: medium
    note: "Not validated independently this pass; cited at call sites"
  - claim: "HashString at 0x007202e0 hashes a file/string for comparison"
    address: "0x007202e0"
    function: "FUN_007202e0"
    confidence: medium
    note: "Cited at call sites in FUN_006a4560 and FUN_006a5df0"
  - claim: "Phase 5: GameLoopTimerProc detects new peers by scanning WSN+0x2C (sorted peer array) + WSN+0x30 (count); peer ID at peer+0x18 is the sort key; binary search confirmed in FUN_006b5c90"
    address: "0x006b5c90"
    function: "FUN_006b5c90"
    confidence: high
  - claim: "Event 0x008000e8 = ET_CHECKSUM_COMPLETE (posted by FUN_006a4bb0)"
    address: "0x006a4bb0"
    function: "FUN_006a4bb0"
    confidence: high
  - claim: "Event 0x008000e7 = ET_NETWORK_NEW_PLAYER (consumed by NewPlayerHandler dispatch)"
    address: "0x006a0a30"
    function: "FUN_006a0a30"
    confidence: medium
    note: "Anchored cross-doc by network-protocol.md"
  - claim: "Event 0x008000e6 = posted by client queue-empty path FUN_006a5860"
    address: "0x006a5860"
    function: "FUN_006a5860"
    confidence: high
---

> [!NOTE]
> **v5 validation 2026-05-28** — **3 corrections + 4 clarifications + 2 historical sections**. Zero wire-format errors. Critical: player slot table is at MpgameBase+0x78 (not +0x74 — note `docs/engine/ui-class-hierarchy.md` ALSO has this off-by-4 inheritance); 0x0097e238 is PlayWindow (not TopWindow); client checksum handler does NOT silently drop when no files found — it sends a response via the unreliable transport (FUN_006b89a0).

# Complete Multiplayer Join Flow (Client -> Server -> Ship Selection)

## Phase 1: Client Clicks "Start" on Join Multiplayer

### MultiplayerWindow::StartGameHandler (FUN_00504890)
1. If already in multiplayer (DAT_0097fa8a): passes event to **PlayWindow** vtable+0x68 (DAT_0097e238)
2. Otherwise: calls FUN_00505480 (UI setup), shows "Connecting..." status
3. Reads config: "Multiplayer Options" -> Game_Name, Player_Name, Password
4. Calls **FUN_00445d90** (UtopiaModule::InitMultiplayer) with (server_addr, password, port)

> [!NOTE]
> **C2 — PlayWindow, not TopWindow.** Prior versions of this doc named DAT_0097e238 as "TopWindow". The binary confirms DAT_0097e238 = PlayWindow; DAT_009878cc = TopWindow (FUN_00504890 references BOTH for distinct vtable calls). See `docs/engine/ui-class-hierarchy.md` for the full PlayWindow/TopWindow disambiguation.

### FUN_00445d90 - Network Initialization
Called as __thiscall on UtopiaModule (0x0097FA00):
```
1. new TGWinsockNetwork(0x34C bytes) -> UtopiaModule+0x78
2. FUN_006b9bb0(WSN, port, 0) - stores port at WSN+0x338
3. If UtopiaModule+0x8a is set: force param_1=0, port=0x5655 (forces host path — see OQ2)
4. If password empty: param_2 = NULL
5. TGNetwork_HostOrJoin(WSN, addr_or_0, password)
   - addr=0: HOST mode (sets WSN+0x10E=1, WSN+0x14=2, fires 0x60002 event)
   - addr!=0: JOIN mode (sets WSN+0x10E=0, WSN+0x10F=1, WSN+0x14=3)
   - Calls vtable+0x60 to create UDP socket
   - Calls FUN_006b7070 to set address info
6. new NetFile(0x48 bytes) via FUN_006a30c0 -> UtopiaModule+0x80
   - Creates 3 hash tables (A/B/C) for checksum tracking
   - Registers NetFile::ReceiveMessageHandler for event 0x60001
7. new GameSpy(0xF4 bytes) -> UtopiaModule+0x7C (if not already exists)
```

#### Clar3 — WSN state-field semantics
- WSN+0x10E = **host flag** (1=host, 0=join)
- WSN+0x10F = **join-only flag** (=1 only in join branch)
- WSN+0x14 (= `param_1[5]`) = **state field** (2=hosting, 3=joining, 4=idle)

The "state" and "host flag" are coordinated but distinct: state captures the lifecycle mode; the host flag captures the polarity. Both are set atomically in FUN_006b3ec0.

## Phase 2: Connection Established

### Server Side: TGNetwork_Update processes connection
1. ProcessIncomingPackets (FUN_006b5c90) receives connection packet
2. Internal peer management creates new peer entry
3. ET_NETWORK_NEW_PLAYER event (0x008000e7) fired

### MultiplayerGame::NewPlayerHandler (FUN_006a0a30)
When MpgameBase+0x1F8 = 1 (ready for new players):
1. Iterates player slots (0-15, each 0x18 bytes at **this+0x78**) — slot N active byte at `(N*3+0xf)*8`
2. Counts active players (slot+0x00 != 0)
3. If active < maxPlayers (this+0x1FC):
   - FUN_006a7770 initializes player slot
   - Sets slot active flag, stores peer network ID at slot+0x04 (= MpgameBase+0x78+slot*0x18+0x04, equivalently slot 0 peer ID at MpgameBase+0x7C)
   - **Calls FUN_006a3820(ChecksumManager, peerID)** - starts checksum exchange
4. If full: creates reject message (type 3), sends via TGNetwork::Send

When MpgameBase+0x1F8 = 0 (not ready):
- Creates timer event to retry later (fixed delay, no backoff — adds `_DAT_00888860` to current gameTime at `DAT_009a09d0+0x90`)

> [!NOTE]
> **C1 — Player slot table starts at MpgameBase+0x78, not +0x74.** Binary truth (FUN_006a0a30): `pcVar7 = (char *)(param_1 + 0x78)` for the iteration loop; slot 0 active byte at offset 0x78; slot 0 peer ID at offset 0x7C. Cross-confirmed by FUN_006a1b10: `puVar7 = (undefined4 *)(param_1 + 0x7c)` reads peer ID at slot 0, and `puVar7 + 6` (0x18 stride) advances to slot 1.
>
> **Source of inherited error**: `docs/engine/ui-class-hierarchy.md` still has "+0x74 playerSlots". This is an off-by-4 inherited into multiplayer-flow.md and must be corrected upstream at the family-close engine sweep.

## Phase 3: Checksum Exchange [v5-validated 2026-05-28 via docs/protocol/checksum-opcodes.md]

### Server: FUN_006a3820 (ChecksumRequestSender)
1. Cleans up any existing state for this player (FUN_006a6500)
2. Builds 4 checksum request entries:
   | # | Directory | Filter | Recursive |
   |---|-----------|--------|-----------|
   | 0 | scripts/ | App.pyc | 0 |
   | 1 | scripts/ | Autoexec.pyc | 0 |
   | 2 | scripts/ships/ | *.pyc | 1 |
   | 3 | scripts/mainmenu/ | *.pyc | 0 |
3. For each: calls FUN_006a39b0 which:
   - Creates network message with opcode 0x20 + [index][dir_len][dir][filter_len][filter][recursive]
   - Sets reliable flag (msg+0x3A = 1)
   - **Only for index 0**: also calls TGNetwork::Send immediately
   - Queues message in NetFile hash table B (keyed by player ID)

### Client: FUN_006a5df0 (Checksum Request Handler - opcode 0x20)
1. Parses: skip opcode, read index byte, read dir string, read filter string, read recursive flag
2. If index == 0: calls FUN_006a6630 (initialization for first request)
3. Calls FUN_0071f270 to compute file checksums for the directory
4. If files found (non-zero return):
   - Builds response: `[0x21][index][reference_hash(if idx=0)][dir_hash][file_checksums]`
   - Sends via TGNetwork::Send(WSN, host_peer_id, msg, 0)
   - Shows "Server Found" status
5. **If NO files found**: builds a 6-byte placeholder response and sends via the **unreliable** transport.

#### C3 — Client does not silently drop the "no files found" response
Binary truth (FUN_006a5df0, `cVar1 == '\0'` branch):
- `WriteChar(0x21)` — opcode header
- `WriteChar(bValue)` — request index from the incoming opcode 0x20
- If `bValue == 0`: `WriteInt(FUN_0071aec0(0xffff))` — sentinel hash for the reference string slot
- `WriteInt(FUN_007202e0(local_40c) + 1)` — **placeholder** file hash (offset +1 makes any real hash mismatch)
- Calls **FUN_006b89a0(buf, len)** — raw / unreliable send (NOT TGNetwork::Send)

So the client *does* respond; the server receives a 6-byte placeholder with sentinel hashes via a different transport. Any failure the original investigation observed was a non-matching placeholder reaching the server (or FUN_006b89a0 itself dropping under load) — not silence. See OQ1.

### Server: FUN_006a3cd0 -> FUN_006a4260 -> FUN_006a4560 (Response Handler)
1. NetFile::ReceiveMessageHandler dispatches opcode 0x21
2. FUN_006a4260 branches on byte[1]:
   - `byte[1] != 0xFF` (indices 0-3): calls FUN_006a4560 — **checksum-comparison path** (this doc)
   - `byte[1] == 0xFF`: calls FUN_006a4e70 (hash match → file accept) or FUN_006a5570 (mismatch → file reject), then FUN_006a5860 — **file-transfer path** (see Clar1)
3. FUN_006a4560 (checksum path):
   - Looks up queued request in hash table B for this player
   - Finds the queued message matching the response index
   - Extracts dir/filter/recursive from queued message (FUN_006a4d80)
   - Computes SERVER-SIDE checksum via FUN_0071f270
   - Compares client hash vs server hash (FUN_007202e0):
     - **For index 0**: also checks reference string hash (PTR_DAT_008d9af4)
     - If match: FUN_006a5290 (success), dequeues from queue
     - If mismatch: FUN_006a4a00 (fail - fires event + sends opcode 0x22 for file fail, 0x23 for ref string fail)
   - After successful verification:
     - Checks hash table C for pending file transfers
     - **If more items in queue B**: clones next message, sends via TGNetwork::Send
     - **If queue B empty**: calls FUN_006a4bb0

#### Clar1 — FUN_006a4260 also handles the file-transfer branch
The checksum-comparison path (this doc's primary focus) is the `byte[1] != 0xFF` branch. The complementary `byte[1] == 0xFF` branch is the streamed-file-block protocol:
- Wire: `WriteChar(0x21) WriteChar(0xFF) WriteInt(hash)`
- On hash match: FUN_006a4e70 (file accept)
- On hash mismatch: FUN_006a5570 (file reject)
- Tail: FUN_006a5860 (FileTransferProcessor)

This doc treats only the checksum path because that's what gates the join sequence. The file-transfer path is the post-join asset sync.

### Server: FUN_006a4bb0 (All Checksums Passed)
- Creates event with type **0x008000e8** (ET_CHECKSUM_COMPLETE)
- Posts to EventManager

## Phase 4: Post-Checksum (Server sends game info) [v5-validated 2026-05-28 via docs/protocol/checksum-opcodes.md, docs/protocol/wire-format-spec.md]

### MultiplayerGame::ChecksumCompleteHandler (FUN_006a1b10)
1. Gets player slot index from player ID
2. Looks up peer in WSN peer array (WSN+0x2C / WSN+0x30)
3. Verifies checksums against ALL other connected players' checksums (walks slots at MpgameBase+0x7C with 0x18-byte stride)
4. Builds verification message (opcode 0x00) — **all three boolean fields are bit-packed**:
   - `WriteChar(0x00)` — 1 byte
   - `WriteFloat(gameTime)` — 4 bytes
   - `WriteBool_Bit(DAT_008e5f59)` — **1 BIT** (setting 1)
   - `WriteBool_Bit(DAT_0097faa2)` — **1 BIT** (setting 2)
   - `WriteChar(playerSlot)` — 1 byte
   - `WriteShort(mapLen) WriteBytes(mapName)` — variable
   - `WriteBool_Bit(passFail)` — **1 BIT**
   - `if (passFail): FUN_006f3f30(stream)` — extra hash block
5. Sends via TGNetwork::Send (reliable)
6. Builds status message: `[0x01]` (1 byte)
7. Sends via TGNetwork::Send (reliable)

#### Clar2 — Settings byte fields are bit-packed, not byte-aligned
The prior wire annotation showed `[setting1:u8][setting2:u8]...[passFail:u8]`. Binary truth: all three are **single bits** via `WriteBool_Bit`. Packets remain byte-aligned overall because TGBufferStream's bit accumulator flushes between writes, but on-the-wire these three booleans occupy 3 bits (typically packed into one shared byte). See `docs/protocol/stream-primitives.md` for bit-packing semantics.

### Client: Receives opcode 0x00
- Processed by MultiplayerGame::ReceiveMessageHandler (`MpgameHandleMessage` @ 0x0069f2a0)
- Extracts player slot, map name, game settings
- Transitions to game setup / ship selection screen

### Client: Receives opcode 0x01
- Status confirmation
- Client ready for gameplay

## Key Functions Reference [v5-validated 2026-05-28 via docs/networking/network-protocol.md]

| Address | Name | Role |
|---------|------|------|
| 0x00445d90 | UtopiaModule::InitMultiplayer | Creates WSN + NetFile + GameSpy |
| 0x00504890 | StartGameHandler | UI entry point for join/host |
| 0x006a0a30 | NewPlayerHandler | Assigns player slot (MpgameBase+0x78, 0x18 stride), starts checksums |
| 0x006a3820 | ChecksumRequestSender | Queues 4 requests, sends #0 |
| 0x006a39b0 | ChecksumRequestBuilder | Builds individual request message |
| 0x006a3cd0 | NetFile::ReceiveMessageHandler | Opcode dispatcher (0x20-0x28) |
| 0x006a4260 | Opcode 0x21 entry | Branches checksum (!=0xFF) vs file-transfer (==0xFF) |
| 0x006a4560 | ChecksumResponseVerifier | Compares hashes, sends next request |
| 0x006a4a00 | ChecksumFail | Fires fail event + sends 0x22 (file) / 0x23 (ref string) |
| 0x006a4bb0 | ChecksumAllPassed | Posts event 0x008000e8 (ET_CHECKSUM_COMPLETE) |
| 0x006a5df0 | Client: ChecksumRequestHandler | Computes checksums, sends response (placeholder via FUN_006b89a0 when no files) |
| 0x006a1b10 | ChecksumCompleteHandler | Sends Settings (opcode 0x00) + GameInit (opcode 0x01) to client |
| 0x006a5860 | FileTransferProcessor | Sends files or completion message; client queue-empty sends opcode 0x28 + posts 0x008000e6 |
| 0x006b3ec0 | TGNetwork_HostOrJoin | Socket creation, state setup |
| 0x006b4c10 | TGNetwork::Send (SendTGMessage) | Queue message for sending |
| 0x006b5c90 | TGWinsockNetwork_ProcessIncomingPackets | Receives packets; WSN+0x2C/+0x30 peer array (anchor for Phase 5) |
| 0x006b9bb0 | WSN port setter | Stores UDP port at WSN+0x338 |
| 0x006b89a0 | (OQ1) unreliable send path | Used by client when no files match — not anchored |
| 0x0071f270 | ComputeChecksum | Scans directory, computes file hashes |
| 0x007202e0 | HashString | Computes hash of a file/string |

## Phase 5: Post-Settings (InitNetwork + DeferredInitObject) [v5-validated 2026-05-28]

### Server: InitNetwork Scheduling (GameLoopTimerProc)
After checksums pass and Settings/GameInit are sent, the server must call
`Mission1.InitNetwork(peerID)` to send `MISSION_INIT_MESSAGE` to the client.

**Detection mechanism**: GameLoopTimerProc scans the WSN peer array. Per FUN_006b5c90:
- `WSN+0x2C` (= `param_1[0xb]`) is the **sorted peer-array pointer**
- `WSN+0x30` (= `param_1[0xc]`) is the **peer count**
- Each peer at `peer+0x18` is the peer ID (the sort key for the binary search in FUN_006b5c90)

When a new peer ID appears in the array:
1. Schedule InitNetwork for 30 ticks later (~1 second)
2. Call `Mission1.InitNetwork(peerID)` via RunPyCode
3. This sends `MISSION_INIT_MESSAGE` to the client

**Timing**: ~1.4 seconds after connect (stock is ~2 seconds).

> [!NOTE]
> **Historical (H1) — bc-flag bug at peer+0xBC.** Previously the proxy detected new peers via the `bc` flag at `peer+0xBC`, which took 200+ ticks (or never flipped), causing MISSION_INIT_MESSAGE to arrive 13+ seconds late. **RESOLVED** per CLAUDE.md "What Works": peer-array detection now fires within ~1.4s using the WSN+0x2C / WSN+0x30 binary-confirmed approach above.

### Server: DeferredInitObject (Ship Creation)
After InitNetwork, the client selects a ship and sends ObjCreateTeam. The engine creates
a ship object on the server, but without a NIF model (subsystems are NULL). GameLoopTimerProc
detects this and triggers Python to complete initialization:

1. Poll every 30 ticks: check for ships owned by the new player
2. If ship exists with NULL ShipRef (+0x2E0): call `DeferredInitObject(playerID)`
3. Python determines ship class -> calls `ship.LoadModel(nifPath)`
4. Engine creates 33 subsystem objects, populates ship+0x284 linked list
5. StateUpdate now sends `flags=0x20` with real subsystem health data
6. Collision damage and subsystem damage work

### Timing Summary (Dedicated Server)

| Event | Stock-Dedi | Our Server (Fixed) | Our Server (Broken — historical) |
|-------|-----------|-------------------|----------------------------------|
| Client connects | T+0.0s | T+0.0s | T+0.0s |
| Checksums complete | T+1.1s | T+1.0s | T+1.0s |
| Settings + GameInit sent | T+1.1s | T+1.0s | T+1.0s |
| InitNetwork / MISSION_INIT | T+2.0s | T+1.4s | **T+13.0s** (bc-flag bug) |
| Client selects ship | T+5.5s | T+5.0s | Client already silent |
| DeferredInitObject | N/A (real renderer) | T+8.0s | Never reached |
| Collision damage works | T+5.7s | T+8.0s | Never |

> The "Our Server (Broken)" column reflects the H1 bc-flag bug — kept here for reference against historical log archives. Current behavior matches the "Our Server (Fixed)" column.

## Key offsets verified live (Ghidra MCP, 2026-05-28)

| Offset | Field | Source function |
|--------|-------|-----------------|
| MpgameBase+0x70 | maybe map/level reference (deref'd) | FUN_006a1b10 |
| MpgameBase+0x74 | unknown 4-byte field (NOT slot start) | gap between 0x70 and 0x78 |
| MpgameBase+0x78 | slot[0] active byte | FUN_006a0a30 — `(0*3+0xf)*8 = 0x78` |
| MpgameBase+0x7C | slot[0] peer ID (u32) | FUN_006a0a30 — `param_1 + 0*0x18 + 0x7c`; FUN_006a1b10 cross-confirms |
| MpgameBase+0x1F8 | ready-for-new-players flag (byte) | FUN_006a0a30 |
| MpgameBase+0x1FC | max players (int) | FUN_006a0a30 — `param_2 < *(int *)(param_1 + 0x1fc)` |
| WSN+0x14 (=[5]) | state field (2=hosting, 3=joining, 4=idle) | FUN_006b3ec0 |
| WSN+0x10E | host-or-join flag (1=host, 0=join) | FUN_006b3ec0 |
| WSN+0x10F | join-only flag (=1 in join branch) | FUN_006b3ec0 |
| WSN+0x2C (=[11]) | sorted peer-array pointer (Phase 5 anchor) | FUN_006b5c90, FUN_006a1b10 |
| WSN+0x30 (=[12]) | peer count | FUN_006b5c90 — `param_1[0xc]` in binary search |
| WSN+0x338 | UDP port number | FUN_006b9bb0 |
| Peer+0x18 | peer ID (sort key for WSN+0x2C array) | FUN_006b5c90 binary search |
| Peer+0xBC | "bc flag" (historical detection signal) | FUN_006a1b10 — `*(char *)(iVar4 + 0xbc) != '\0'` |

## Potential Failure Points in Our Server

1. **FUN_0071f270 on server side** — if it can't find/scan script directories, verification fails
2. **Reference string hash** (PTR_DAT_008d9af4) — checked only for index 0, mismatch = immediate fail
3. **DAT_0097f94c** (SkipChecksum flag) — if set, changes behavior completely
4. **(Historical — H2) Client FUN_0071f270 returning 0** — *previously characterized as "client silently drops response"; that premise is wrong per C3.* The client sends a 6-byte placeholder response via FUN_006b89a0 (unreliable transport) with sentinel hashes. The real failure mode (if observed) is a non-matching placeholder reaching the server, or FUN_006b89a0 itself dropping under load. See OQ1.
5. **Opcode 0x00/0x01 not in NetFile dispatcher** — handled by MultiplayerGame dispatcher (`MpgameHandleMessage` @ 0x0069f2a0)

## Open Questions

- **OQ1**: What does FUN_006b89a0 (0x006b89a0 – 0x006b89dd, ~62 bytes) actually do? It's the unreliable-send path the client uses when no files match. Not anchored this pass.
- **OQ2**: What is the `+0x8a` flag on UtopiaModule? FUN_00445d90 treats it as "force host mode" (zeroes addr, forces port 0x5655). Possibly the dedicated-server flag — would explain why headless servers always take the host path.
