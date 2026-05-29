> [docs](../README.md) / [networking](README.md) / network-protocol.md

---
title: Network Protocol — Architecture & Debug Reference
type: reference + explanation
audience: re-engineer
validated: 2026-05-28
methodology: FUNCTION_DOC_WORKFLOW_V5
binary:
  name: stbc.exe
  size: 6182400
  base: 0x00400000
status: partial
evidence:
  - claim: "MpgameHandleMessage (MultiplayerGame ReceiveMessageHandler dispatcher) at 0x0069F2A0 — jump table at 0x0069F534, 41 entries indexed by (opcode - 2), handles opcodes 0x02-0x2A"
    address: 0x0069F2A0
    function: MpgameHandleMessage
    completeness: 69.8
    effective: 94.4
    confidence: high
    note: "Cross-anchor: protocol foundation #1 wire-format-spec.md (v5-validated 2026-05-28). Best-documented function in this doc — custom-named + prototyped."
  - claim: "NetFile dispatcher (NetFile::ReceiveMessageHandler) at 0x006a3cd0 — handles checksum/file opcodes 0x20-0x27, registered for event type 0x60001 (ET_NETWORK_MESSAGE_EVENT)"
    address: 0x006a3cd0
    function: NetFile__ReceiveMessageHandler
    completeness: 0.6
    effective: 81.9
    confidence: high
    note: "Cross-anchor: protocol mid #5 checksum-opcodes.md. Switch-table function — low completeness score but behavior tractable from pseudocode."
  - claim: "MultiplayerWindow dispatcher at 0x00504c10 — handles UI-level opcodes 0x00 (Settings), 0x01 (GameInit), 0x16 (UICollisionSetting); the THIRD dispatcher omitted from prior 'Two Dispatchers' framing"
    address: 0x00504c10
    function: MultiplayerWindow__ReceiveMessageHandler
    completeness: 9.6
    effective: 87.1
    confidence: high
    note: "Cross-anchor: foundation #1 wire-format-spec.md (v5-validated 2026-05-28). See C1 in body."
  - claim: "TGNetwork::Update at 0x006B4560 — three unconditional sub-functions (SendOutgoingPackets / ProcessIncomingPackets / DispatchIncomingQueue); host state 2 dequeue loop posts ET_NETWORK_MESSAGE_EVENT (0x60001)"
    address: 0x006B4560
    function: TGNetwork__Update
    completeness: 0.0
    effective: 83.1
    confidence: high
    note: "Cross-anchor: protocol foundation #3 transport-layer.md. State-2 dequeue posts event_type 0x60001 at +0x10 (verified inline: `*(undefined4 *)((int)pvVar4 + 0x10) = 0x60001`)."
  - claim: "UtopiaModule::InitMultiplayer at 0x00445d90 — Phase-1 init creates TGWinsockNetwork (0x34C bytes at +0x78), NetFile (0x48 bytes at +0x80), GameSpy (0xF4 bytes at +0x7C); sets port on WSN+0x338 via FUN_006b9bb0"
    address: 0x00445d90
    function: UtopiaModule__InitMultiplayer
    completeness: 5.0
    effective: 83.1
    confidence: high
    note: "Cross-anchor: engine decompiled-functions.md (v5-validated 2026-05-28). Standard sub-object allocation pattern."
  - claim: "NetFile ctor at 0x006a30c0 allocates 0x48 bytes; registers NetFile::ReceiveMessageHandler for event type 0x60001 (inline: `FUN_006db380(0x60001, ...)`); initializes 3 hash tables (A/B/C)"
    address: 0x006a30c0
    function: NetFile__Ctor
    completeness: 0.0
    effective: 85.8
    confidence: high
    note: "Cross-anchor: protocol mid #5 checksum-opcodes.md. Hash-table init loops verified inline."
  - claim: "ChecksumCompleteHandler at 0x006a1b10 sends Settings (opcode 0x00) + GameInit (opcode 0x01) packets after all 4 checksum rounds pass"
    address: 0x006a1b10
    function: ChecksumCompleteHandler
    completeness: 0.0
    effective: 81.1
    confidence: high
    note: "Cross-anchor: engine decompiled-functions.md (v5-validated 2026-05-28) — full byte-level confirmation of Settings/GameInit packet writer including 2 WriteBool_Bit settings flags."
  - claim: "RegisterHandlerFunc at 0x006da130 — thin wrapper registering (func_ptr, name_string) pairs in handler-function registry; used by all dispatcher registration calls"
    address: 0x006da130
    function: RegisterHandlerFunc
    completeness: 15.0
    effective: 89.0
    confidence: high
    note: "Thin wrapper; verified inline this pass."
  - claim: "TGEventManager::PostEvent at 0x006da2a0 — forwards to FUN_006de330 which manipulates queue at *param_1; called as PostEvent(&DAT_0097F838, event)"
    address: 0x006da2a0
    function: TGEventManager__PostEvent
    confidence: high
    note: "Direct re-verification this pass. Implicit `this` = &DAT_0097F838 (EventManager queue/dispatcher singleton). See C2 for singleton disambiguation."
  - claim: "ProcessEvents chain FUN_006da2c0 -> FUN_006da300 -> FUN_006db620 — ProcessEvents dequeues, per-event dispatch goes through FUN_006da300 intermediate (NOT direct dispatch as prior doc claimed)"
    address: 0x006da2c0
    function: ProcessEvents
    confidence: high
    note: "See R2 in body. Intermediate FUN_006da300 layer reads registry from this+0x4 + vtable hop before calling FUN_006db620(registry, event)."
  - claim: "ChecksumRequestSender at 0x006a3820 builds 4 checksum requests (App.pyc, Autoexec.pyc, ships/*.pyc, mainmenu/*.pyc), queues all in hash table B, sends index 0 via TGNetwork::Send"
    address: 0x006a3820
    function: ChecksumRequestSender
    confidence: high
    note: "Cross-anchor: protocol mid #5 checksum-opcodes.md (v5-validated 2026-05-28). 4 requests + scripts/Custom/ exemption confirmed."
  - claim: "ChecksumResponseRouter at 0x006a4260 — byte[1] selects between verification path (!= 0xFF, indices 0-3) calling FUN_006a4560, and a separate 0xFF-flagged path that reads filename/dirname/recursive from TGBufferStream"
    address: 0x006a4260
    function: ChecksumResponseRouter
    confidence: high
    note: "See Clar2 in body — prior doc's '(always true)' claim was a misread. Both branches reachable; 0xFF path observed in production traces per protocol mid #5 OQ1."
  - claim: "ChecksumRequestBuilder at 0x006a39b0 — populates queue entries in hash table B"
    address: 0x006a39b0
    function: ChecksumRequestBuilder
    confidence: medium
    note: "Cross-anchor: protocol mid #5 checksum-opcodes.md. Not byte-checked this pass."
  - claim: "ChecksumFail at 0x006a4a00 fires ET_SYSTEM_CHECKSUM_FAILED (event_type 0x008000E7) at event+0x10; sends opcode 0x22 or 0x23 (file mismatch vs reference mismatch)"
    address: 0x006a4a00
    function: ChecksumFail
    confidence: high
    note: "Cross-anchor: protocol leaf subsystem-integrity-hash.md (uses same `*(undefined **)(iVar2 + 0x10) = &DAT_008000e7` immediate-write pattern)."
  - claim: "ChecksumAllPassed at 0x006a4bb0 fires ET_CHECKSUM_COMPLETE (event_type 0x008000E8) when checksum queue empty"
    address: 0x006a4bb0
    function: ChecksumAllPassed
    confidence: high
    note: "Cross-anchor: protocol leaf subsystem-integrity-hash.md (uses same `*(undefined **)(iVar1 + 0x10) = &DAT_008000e8` immediate-write pattern)."
  - claim: "WSN port setter at 0x006b9bb0 stores port at TGWinsockNetwork+0x338; called from UtopiaModule::InitMultiplayer Phase-1"
    address: 0x006b9bb0
    function: TGWinsockNetwork__SetPort
    confidence: high
    note: "Direct re-verification this pass. Cross-anchor: protocol foundation #3 transport-layer.md."
  - claim: "GameSpy QR1 dispatcher entry at 0x006ac1e0 (qr_handle_query) — qr_t struct +0xdc/+0xe0/+0xe8 fields visible in decompile"
    address: 0x006ac1e0
    function: qr_handle_query
    confidence: high
    note: "Direct re-verification this pass. UDP peek-based router in proxy delegates `\\`-prefixed packets here."
  - claim: "Both message dispatchers set re-entry guard DAT_0097fa8b = 1 during processing — MpgameHandleMessage at 0x0069f2be, FUN_006a3cd0 at 0x006a3cd6 (NOT NetFile-exclusive as prior doc claimed)"
    address: 0x0097FA8B
    function: null
    confidence: high
    note: "See Clar3 in body. 36 xrefs to global, including both dispatcher entries. Cleared at end of each dispatch (0x0069f525 and 0x006a3e75 respectively)."
  - claim: "EventManager (queue/dispatcher) singleton at 0x0097F838 — handler registry at +0x2C = 0x0097F864; 140+ xrefs; receives PostEvent calls"
    address: 0x0097F838
    function: null
    confidence: high
    note: "Cross-anchor: engine decompiled-functions.md (byte-level `MOV ECX, 0x97f864` confirms +0x2C registry offset). DISTINCT from TGEventManager at 0x00991438 — see C2."
  - claim: "TGEventManager (SWIG/Python bridge) singleton at 0x00991438 — populated at boot; 2 xrefs at 0x0065b430/0x0065b460; identified via SWIG TGEventManager_AddEvent wrapper at 0x005c8be9 (`MOV EAX, [0x00991438]`)"
    address: 0x00991438
    function: null
    confidence: high
    note: "Cross-anchor: engine event-system-architecture.md (v5-validated 2026-05-28). DISTINCT singleton from 0x0097F838 — see C2."
  - claim: "MultiplayerGame Event Handlers table lists 15 of 30 handlers actually registered by FUN_0069efe0; remaining 14 enumerated in OQ2"
    address: 0x0069efe0
    function: MultiplayerGame__RegisterHandlers
    confidence: high
    note: "See R1 in body. The 15 listed entries are correct address-for-address; the table is a strict subset."
  - claim: "FUN_006a0a20 is MultiplayerGame__EnterSetEventHandler (3-byte stub), NOT a DisconnectHandler as prior doc table claimed"
    address: 0x006a0a20
    function: MultiplayerGame__EnterSetEventHandler
    confidence: high
    note: "Cross-anchor: protocol leaf #18 objnotfound-requestobj-enterset-wire-format.md (v5-validated 2026-05-28). See cross-doc disagreements section."
  - claim: "FUN_006a07d0 is MultiplayerGame__RequestObjEventHandler (sender for opcodes 0x1D ObjNotFound and 0x1F EnterSet), NOT an EnterSetHandler as prior doc table claimed"
    address: 0x006a07d0
    function: MultiplayerGame__RequestObjEventHandler
    confidence: high
    note: "Cross-anchor: protocol leaf #18 objnotfound-requestobj-enterset-wire-format.md (v5-validated 2026-05-28)."
  - claim: "FUN_006a0ca0 sends opcode 0x18 (DeletePlayerAnim) — NOT a generic DeletePlayerHandler as prior doc table claimed"
    address: 0x006a0ca0
    function: DeletePlayerAnimSender
    confidence: high
    note: "Cross-anchor: protocol leaf #17 delete-player-ui-wire-format.md (v5-validated 2026-05-28)."
companions:
  - docs/protocol/v5-validation-status.md
  - docs/protocol/checksum-opcodes.md
  - docs/protocol/transport-layer.md
  - docs/engine/event-system-architecture.md
  - docs/networking/v5-validation-status.md
supersedes:
  - 2026-02-15
---

# Network Protocol — Architecture & Debug Reference

> [!NOTE]
> This doc is `status: partial`. **Structural refresh: 2 corrections + 3 clarifications + 2 refutations + 3 historical-section marks**. 17 protocol-family-anchored claims cross-confirmed at high confidence; 5 new claims independently verified this pass. Major structural: "Two Message Dispatchers" is actually **THREE** (MultiplayerWindow was omitted from the header). **EventManager (0x0097F838) and TGEventManager (0x00991438) are TWO distinct singletons** serving different roles. Handler tables list 15 of 30 registered handlers (subset; full enumeration deferred to OQ2). Three sections describing old game state or proxy instrumentation are now marked historical. See [v5-evidence-header.md](../guides/v5-evidence-header.md) for the standard. Source evidence: `.claude/agent-memory/game-archaeology-specialist/networking-foundation-network-protocol-validation-20260528.md`.

---

## Complete Checksum Protocol (Fully Traced)

[v5-validated 2026-05-28 via [checksum-opcodes.md](../protocol/checksum-opcodes.md)]

### Server-Side Flow:
1. Client connects -> TGNetwork fires ET_NETWORK_NEW_PLAYER
2. NewPlayerHandler (0x006a0a30) assigns player slot
3. Calls FUN_006a3820 on NetFile (0x0097FA80) to start checksum exchange
4. FUN_006a3820 builds 4 requests, queues ALL in hash table B, sends #0 via TGNetwork::Send
5. Client responds with opcode 0x21
6. NetFile::ReceiveMessageHandler (FUN_006a3cd0) dispatches to FUN_006a4260
7. FUN_006a4260: `byte[1]` selects between the verification path (`!= 0xFF`, indices 0-3 for checksum responses) and a separate `0xFF`-flagged retry path. The verification path calls FUN_006a4560. **(Clar2 — prior doc claimed "always true" which was a misread; the 0xFF path is reachable.)**
8. FUN_006a4560 verifies checksum (server hash vs client hash):
   - Match: dequeues from queue, **sends NEXT via TGNetwork::Send**
   - Mismatch: FUN_006a4a00 fires ET_SYSTEM_CHECKSUM_FAILED, sends opcode 0x22/0x23
9. When queue empty: FUN_006a4bb0 fires ET_CHECKSUM_COMPLETE (type 0x8000e8)
10. ChecksumCompleteHandler (0x006a1b10) sends:
    - Opcode 0x00: [gameTime:f32][settings:2bits][playerSlot:u8][mapNameLen:u16][mapName][passFail:bit]
    - Opcode 0x01: 1-byte status

### Client-Side Flow:
1. Receives opcode 0x20 -> FUN_006a5df0 computes file checksums
2. Sends response: opcode 0x21, [index:u8], [hashes...]
3. If FUN_0071f270 returns 0 (no files found), response NOT sent (silent failure!)
4. Receives opcode 0x00 -> gets player slot, map name, settings
5. Proceeds to game setup/ship selection

### Checksum Requests (4 total):
| # | Directory | Filter | Recursive |
|---|-----------|--------|-----------|
| 0 | scripts/ | App.pyc | No |
| 1 | scripts/ | Autoexec.pyc | No |
| 2 | scripts/ships/ | *.pyc | Yes |
| 3 | scripts/mainmenu/ | *.pyc | No |

Note: `scripts/Custom/` directory is EXEMPT from checksums. `scripts/Local.py` is also exempt. [v5-validated 2026-05-28 via [checksum-opcodes.md](../protocol/checksum-opcodes.md)]

### Packet Opcodes (Checksum/NetFile):

[v5-validated 2026-05-28 via [checksum-opcodes.md](../protocol/checksum-opcodes.md)]

| Opcode | Direction | Handler | Purpose |
|--------|-----------|---------|---------|
| 0x20 | Server->Client | FUN_006a5df0 | Checksum request |
| 0x21 | Client->Server | FUN_006a4260->006a4560 | Checksum response |
| 0x22 | Server->Client | FUN_006a4c10 | Checksum fail (file mismatch) |
| 0x23 | Server->Client | FUN_006a4c10 | Checksum fail (reference mismatch) |
| 0x25 | Both | FUN_006a5860/FUN_006a3ea0 | File transfer |
| 0x27 | ? | FUN_006a4250 | File transfer ACK |

---

## C1 — Three Message Dispatchers (not two)

[v5-validated 2026-05-28]

The pre-v5 doc heading "Two Message Dispatchers" was wrong. The binary registers **three** distinct dispatchers, each on a different object, handling disjoint opcode ranges. CLAUDE.md and all 22 protocol-family docs use the three-dispatcher framing; this doc is being brought into line.

1. **NetFile dispatcher** (`FUN_006a3cd0` at UtopiaModule+0x80): Handles **opcodes 0x20-0x27** (checksums + file transfer)
   - Registered for event type `0x60001` (ET_NETWORK_MESSAGE_EVENT)
   - Sets `DAT_0097fa8b = 1` during processing (Clar3 — both dispatchers set this flag)

2. **MultiplayerGame dispatcher** (registered as `ReceiveMessageHandler`, function `MpgameHandleMessage` at `0x0069F2A0`): Handles **game opcodes 0x02-0x2A**
   - Forwards to per-opcode handlers via the **41-entry jump table at 0x0069F534** (indexed by `opcode - 2`)
   - Cross-anchor: protocol foundation #1 [`wire-format-spec.md`](../protocol/wire-format-spec.md) (v5-validated 2026-05-28)

3. **MultiplayerWindow dispatcher** (`FUN_00504c10`): Handles **UI-level opcodes 0x00 (Settings), 0x01 (GameInit), 0x16 (UICollisionSetting)**
   - This was the dispatcher omitted from the pre-v5 framing. The doc separately listed its handler table further down but mis-headed the higher-level architecture.

These are SEPARATE dispatchers on SEPARATE objects. Foundation cross-link: [`wire-format-spec.md`](../protocol/wire-format-spec.md) §dispatcher-summary.

---

## NetFile Object

[v5-validated 2026-05-28 via [checksum-opcodes.md](../protocol/checksum-opcodes.md)]

**UtopiaModule+0x80 (0x0097FA80) is BOTH the ChecksumManager AND the message dispatcher.**

- Created by FUN_006a30c0 (0x48 bytes) during FUN_00445d90 (Phase 1)
- Registers NetFile::ReceiveMessageHandler for event type 0x60001
- Contains 3 hash tables:
  - A (NetFile+0x18 vtable, +0x1C count, +0x20 capacity, +0x24 buckets): Used by FUN_006a4260 for tracking **(Clar1)**
  - B (NetFile+0x28 vtable, +0x2C count, +0x30 capacity, +0x34 buckets): Queued checksum requests (FUN_006a39b0)
  - C (NetFile+0x38 vtable, +0x3C count, +0x40 capacity, +0x44 buckets): Pending file transfers (FUN_006a5860)

### Clar1 — Hash table offset terminology

The pre-v5 doc used the shorthand `vtable+0x18 / buckets+0x24` for table A, etc. Those offsets are correct, but the prefix word "vtable" was ambiguous (these aren't offsets relative to a vtable; they are offsets relative to the **NetFile object base** to fields that happen to include a vtable pointer at the start of each hash-table sub-struct). Corrected wording: `NetFile+0x18 (vtable pointer), NetFile+0x1C (count), NetFile+0x20 (capacity), NetFile+0x24 (buckets)` for table A; analogous for B and C. Offsets are unchanged.

---

## Event System Architecture

[v5-validated 2026-05-28]

### C2 — Two distinct singletons: EventManager vs TGEventManager

The pre-v5 doc treated the event manager as a single global at `0x0097F838`. The binary has **two distinct singletons** serving different roles. Both are correct anchors; they are not the same object.

| Singleton | Address | Role | Xref count | First-seen reference |
|---|---|---|---|---|
| **EventManager** (queue/dispatcher) | `0x0097F838` | C++ event queue + handler-registry root at `+0x2C = 0x0097F864`; receives `PostEvent` calls from C++ paths | 140+ xrefs | `MOV ECX, 0x97f864` byte-level confirmed in [`decompiled-functions.md`](../engine/decompiled-functions.md) |
| **TGEventManager** (SWIG/Python bridge) | `0x00991438` | SWIG-accessible singleton; populated at boot (zero in image); exposed to Python via SWIG wrappers | 2 xrefs (`0x0065b430`, `0x0065b460`) | `MOV EAX, [0x00991438]` in SWIG `TGEventManager_AddEvent` wrapper at `0x005c8be9` (per [`event-system-architecture.md`](../engine/event-system-architecture.md)) |

The doc's existing claims for `0x0097F838` and its `+0x2C` registry remain correct — they refer to the EventManager queue/dispatcher. The TGEventManager at `0x00991438` is the alternate name used by SWIG/Python-facing code. For full disambiguation see [`docs/engine/event-system-architecture.md`](../engine/event-system-architecture.md).

### Event-system call chain

- EventManager object at `0x0097F838`
- Handler registry at `EventManager+0x2C = 0x0097F864`
- ProcessEvents (`FUN_006da2c0`) dequeues from queue, calls **`FUN_006da300` per event**, which then calls **`FUN_006db620(registry, event)`** via `this+0x4` plus a vtable hop **(R2 — pre-v5 doc skipped the intermediate `FUN_006da300` layer; corrected here)**
- Handler registration: `FUN_006db380(&0x0097F864, event_type, target, name, ...)`
- Event posting: `TGEventManager::PostEvent` (`FUN_006da2a0`) with implicit `this = &DAT_0097F838`
- Handler function registration: `FUN_006da130(func_ptr, name_string)` — thin wrapper

### Clar3 — Both dispatchers set DAT_0097fa8b

The pre-v5 doc said "NetFile dispatcher sets DAT_0097fa8b = 1 during processing". Binary truth: **both** dispatchers set this re-entry guard.

- `MpgameHandleMessage` sets at `0x0069f2be`, clears at `0x0069f525`
- `FUN_006a3cd0` (NetFile) sets at `0x006a3cd6`, clears at `0x006a3e75`

`DAT_0097fa8b` is `g_bMpgameInOpcodeDispatch` — a re-entry guard for the whole MP-opcode-dispatch cycle, not NetFile-exclusive. The flag has 36 xrefs including both dispatcher entries.

---

## Key Event Types
| Type | Name | Meaning |
|------|------|---------|
| 0x60001 | ET_NETWORK_MESSAGE_EVENT | Incoming network message — anchored in `FUN_00445d90` and `FUN_006b4560` |
| 0x60002 | (hosting start) | Host session created — `[low-confidence — see OQ1]` |
| 0x8000e6 | (checksum result?) | Individual checksum done — `[low-confidence — see OQ1]` |
| 0x8000e7 | ET_SYSTEM_CHECKSUM_FAILED | Checksum mismatch — anchored at `FUN_006a4a00` |
| 0x8000e8 | ET_CHECKSUM_COMPLETE | All checksums passed — anchored at `FUN_006a4bb0` |
| 0x8000e9 | ET_KILL_GAME | Game killed — `[low-confidence — see OQ1]` |
| 0x8000f6 | ET_BOOT_PLAYER | Anti-cheat kick — anchored at `FUN_005b2311` (subsystem-integrity-hash.md) |
| 0x8000ff | (retry connect) | Connection retry — `[low-confidence — see OQ1]` |

Strings exist in the binary (e.g., `ET_KILL_GAME` at `0x0090fb44`, `ET_CHECKSUM_COMPLETE` at `0x0090fb8c`, `ET_NETWORK_MESSAGE_EVENT` at `0x00953bc4`), but they do not have data xrefs binding them to the numeric event-type constants directly. See **OQ1** for the dig.

---

## R1 — MultiplayerGame Event Handlers (FUN_0069efe0)

> [!IMPORTANT]
> **`[partial — subset of 30 registered handlers; full enumeration deferred to OQ2]`**. The table below lists 15 of the 30 handlers actually registered by `FUN_0069efe0`. Listed entries are address-correct.

| Address | Handler Name |
|---------|-------------|
| 0x0069f2a0 | ReceiveMessageHandler (`MpgameHandleMessage`) |
| 0x006a0a20 | **MultiplayerGame__EnterSetEventHandler** *(was: "DisconnectHandler" — corrected via protocol leaf #18 [objnotfound-requestobj-enterset-wire-format.md](../protocol/objnotfound-requestobj-enterset-wire-format.md))* |
| 0x006a0a30 | NewPlayerHandler |
| 0x006a0c60 | SystemChecksumPassedHandler |
| 0x006a0c90 | SystemChecksumFailedHandler |
| 0x006a0ca0 | **DeletePlayerAnimSender** *(was: "DeletePlayerHandler" — sends opcode 0x18 DeletePlayerAnim per protocol leaf #17 [delete-player-ui-wire-format.md](../protocol/delete-player-ui-wire-format.md))* |
| 0x006a0f90 | ObjectCreatedHandler |
| 0x006a1150 | HostEventHandler |
| 0x006a1590 | NewPlayerInGameHandler |
| 0x006a1790 | StartFiringHandler |
| 0x006a1930 | ClientEventHandler |
| 0x006a1b10 | ChecksumCompleteHandler |
| 0x006a2640 | KillGameHandler |
| 0x006a2a40 | RetryConnectHandler |
| 0x006a07d0 | **MultiplayerGame__RequestObjEventHandler** *(was: "EnterSetHandler" — sender for opcodes 0x1D ObjNotFound and 0x1F EnterSet per protocol leaf #18)* |

---

## MultiplayerWindow Event Handlers (FUN_005046b0)
| Address | Handler Name |
|---------|-------------|
| 0x00504890 | StartGameHandler |
| 0x00504c10 | ReceiveMessageHandler (the MultiplayerWindow dispatcher — see C1) |
| 0x00505040 | ConnectHandler |
| 0x00505110 | DisconnectHandler |
| 0x00505d70 | SetMissionNameHandler |
| 0x00505e00 | RefreshServerListHandler |
| 0x00506200 | SelectServerHandler |
| 0x00506a50 | SortServerListHandler |
| 0x00506170 | BootPlayerHandler |

---

## TGNetwork::Update Internal Flow (0x006B4560)

[v5-validated 2026-05-28 via [transport-layer.md](../protocol/transport-layer.md)]

Three core sub-functions called unconditionally:
1. FUN_006b55b0 - SendOutgoingPackets (checks WSN+0x10C flag, iterates peers)
2. FUN_006b5c90 - ProcessIncomingPackets (recv from socket, deserialize)
3. FUN_006b5f70 - DispatchIncomingQueue (validate sequences, deliver)

For host state 2: dequeue loop at 0x006b4779 fires ET_NETWORK_MESSAGE_EVENT (0x60001). The event_type immediate-write is `*(undefined4 *)((int)pvVar4 + 0x10) = 0x60001`.

---

## Peek-Based UDP Router (Working)
Located in GameLoopTimerProc. Solves the shared socket problem:
- GameSpy and TGNetwork share the SAME UDP socket (WSN+0x194)
- Router uses MSG_PEEK + select() to check first byte without consuming
- `\`-prefixed packets -> qr_handle_query (0x006ac1e0) for GameSpy
- Binary packets -> left in socket buffer for TGNetwork_Update
- qr_t+0xE4 set to 0 to disable GameSpy's own recvfrom loop

---

## Normal Game Initialization (FUN_00445d90)

[v5-validated 2026-05-28 via [decompiled-functions.md](../engine/decompiled-functions.md)]

Called as `__thiscall` on UtopiaModule (0x0097FA00):
1. Creates TGWinsockNetwork (0x34C bytes) -> stored at +0x78 (0x0097FA78)
2. FUN_006b9bb0 sets port on WSN (+0x338 = port)
3. TGNetwork_HostOrJoin (0x006b3ec0) creates socket, sets state
4. Creates NetFile (0x48 bytes) via FUN_006a30c0 -> stored at +0x80 (0x0097FA80)
5. Creates GameSpy (0xF4 bytes) -> stored at +0x7C (0x0097FA7C)

Our Phase 1 calls this function correctly with (this=0x0097FA00, addr=0, pw=empty, port=0x5655).

---

## STATUS: CLIENT DISCONNECTS AFTER SHIP SELECTION

> **Historical (resolved 2026-05-28)** — flags=0x20 with real subsystem health data is now sent by the server via DeferredInitObject. See CLAUDE.md "What Works" status (Collision damage / Subsystem damage / StateUpdate flags=0x20).

Checksums pass, Settings/GameInit/ObjCreateTeam all sent correctly. Client reaches ship
selection screen with ship model visible. Disconnects ~3 sec later due to empty StateUpdate
packets (flags=0x00 instead of flags=0x20 with subsystem data).
See [docs/black-screen-investigation.md](../analysis/black-screen-investigation.md) for current investigation.

---

## Previously Solved Issues

> **Historical (resolved 2026-05-28)** — Black screen, checksum stall, and first-connection timeout are all addressed in the current build. Preserved for trace cross-reference.

- **Black screen** (no cursor, no scoreboard): Fixed by NewPlayerInGame handshake in GameLoopTimerProc
- **Checksum stall** (priority queue stuck at 3): Was a misdiagnosis — actually resolved by
  getting the full checksum exchange working correctly
- **First connection timeout**: Still exists (client must reconnect once), not yet investigated

---

## IAT Hooks (Currently Installed)

> **Historical (proxy instrumentation, not stbc.exe behavior)** — Describes the proxy DLL's diagnostic hooks rather than the game binary itself. Belongs in proxy instrumentation docs; preserved here for cross-reference.

- sendto: HookedSendto logs outbound packets with hex dump
- recvfrom: HookedRecvfrom logs inbound packets (non-PEEK only)
- Both hooked via PatchIATEntry in HookGameIAT

## Peer Send Queue Monitoring

After MainTick: checks peer+0x7C (unreliable), +0x98 (reliable), +0xB4 (priority reliable)
Only logs when queue sizes change. Also in periodic 10-second status log.

---

## Open Questions

- **OQ1** — Event-type numeric values for `0x60002` (hosting start), `0x8000e6` (checksum result?), `0x8000e9` (kill game), `0x8000f6` (boot player), `0x8000ff` (retry connect). The `ET_*` strings exist in the binary (e.g., `ET_KILL_GAME` at `0x0090fb44`) but the strings do not bind to the numeric constants via data xrefs. A focused sweep for the numeric immediates in the code body would resolve them — search for `MOV [reg+0x10], 0x60002` and analogous immediate-writes the way `0x8000e7` was anchored at `FUN_006a4a00`.
- **OQ2** — Full enumeration of MultiplayerGame Event Handlers (15 -> 30). Known unlisted handlers from prior validation memo: `StopFiringHandler` (0x006a18d0), `StopFiringAtTargetHandler` (0x006a18e0), `SubsystemStatusHandler` (0x006a1910), `AddToRepairListHandler` (0x006a1920), `RepairListPriorityHandler` (0x006a1940), `ChangedTargetHandler` (0x006a1a70), `StartCloakingHandler` (0x006a18f0), `StopCloakingHandler` (0x006a1900), `StartWarpHandler` (0x006a17a0), `SetPhaserLevelHandler` (already in Ghidra DB), `ObjectExplodingHandler` (0x006a1240), `ExitedWarpHandler` (0x006a0a10), `TorpedoTypeChangeHandler` (0x006a17b0), `DeleteObjectHandler` (0x006a1a60). Deferred to a focused sweep of `FUN_0069efe0`.

---

## Related Documents

- [`docs/protocol/wire-format-spec.md`](../protocol/wire-format-spec.md) — Protocol-family hub: dispatcher summary, opcode tables. Authority for the C1 three-dispatcher framing.
- [`docs/protocol/checksum-opcodes.md`](../protocol/checksum-opcodes.md) — Opcodes 0x20-0x28, 4 checksum requests, scripts/Custom/ exemption. Anchor for the checksum protocol section above.
- [`docs/protocol/transport-layer.md`](../protocol/transport-layer.md) — TGNetwork::Update internals, TGWinsockNetwork struct layout.
- [`docs/engine/event-system-architecture.md`](../engine/event-system-architecture.md) — Full disambiguation of EventManager (0x0097F838) vs TGEventManager (0x00991438) singletons; handler-registration internals; TGCallback/TGConditionHandler.
- [`docs/engine/decompiled-functions.md`](../engine/decompiled-functions.md) — Per-function deep dives for `UtopiaModule::InitMultiplayer`, `NetFile::ReceiveMessageHandler`, `ChecksumCompleteHandler`, etc.
- [`docs/protocol/subsystem-integrity-hash.md`](../protocol/subsystem-integrity-hash.md) — Anchors ET_BOOT_PLAYER (0x008000F6) event-type and the `*(reg + 0x10) = immediate` event-posting pattern shared with `FUN_006a4a00` and `FUN_006a4bb0`.
- [`docs/protocol/v5-validation-status.md`](../protocol/v5-validation-status.md) — Protocol-family campaign tracker; this networking-family doc cross-references multiple protocol-family anchors.
- [`docs/networking/v5-validation-status.md`](v5-validation-status.md) — Networking-family campaign tracker; this is networking foundation #1.
