> [docs](../README.md) / [networking](README.md) / disconnect-flow.md

---
title: Player Disconnect Flow
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
  - claim: "FUN_006b75b0 is the convergence point for peer deletion: marks peer+0xBC=1 (IsDisconnected), writes peer+0xB8=currentTime, posts ET_NETWORK_DELETE_PLAYER (0x60005)"
    address: 0x006b75b0
    function: FUN_006b75b0
    completeness: 3.17
    effective: 96.8
    confidence: high
    note: "Byte-confirmed via disasm at 0x006b7607 (MOV [ESI+0x10], 0x60005), 0x006b7629 (MOV byte [EDI+0xBC], 1), 0x006b7636 (FSTP [EDI+0xB8]). Allocates 0x2C via FUN_00717b70(0x2C) at 0x006b75e0 (PUSH 0x2C byte-confirmed)."
  - claim: "Detection Path 1 (timeout, ~45s): FUN_006b4560 iterates WSN peer array via WSN+0x2C/+0x30 (array ptr / count), comparing currentTime - peer+0x2C > WSN+0xB8 timeout threshold"
    address: 0x006b48ae
    function: FUN_006b4560
    completeness: 0.0
    effective: 129.9
    confidence: high
    note: "Disasm anchor 0x006b483a..0x006b489e iterates peer array. Timeout site 0x006b48ae compares against peer+0x2C (lastRecvTime), NOT peer+0x30 as prior doc claimed. Calls FUN_006b75b0 at 0x006b4898."
  - claim: "Detection Path 2 (graceful disconnect, transport type 5): FUN_006b6a20 receives TGDisconnectMessage; if peerID == WSN+0x18 or WSN+0x20 set field_0x10d=1 (shutdown flag); always calls FUN_006b75b0; if WSN+0x10E set, broadcasts via FUN_006b51e0"
    address: 0x006b6a20
    function: FUN_006b6a20
    completeness: 10.51
    effective: 89.5
    confidence: high
    note: "C1 — SWAPPED in pre-v5 doc. Decomp-confirmed body has no -1 sentinel; that sentinel belongs to FUN_006b6a70 (boot). Broadcast relay via FUN_006b51e0 was missing from prior doc."
  - claim: "Detection Path 3 (boot reception, transport type 4): FUN_006b6a70 receives TGBootMessage; if peerID == -1 set field_0x10d=1 + field_0x100=msg+0x40 + state=2 (host kicked us); else calls FUN_006b75b0; if peerID == WSN+0x18 also set field_0x10d=1"
    address: 0x006b6a70
    function: FUN_006b6a70
    completeness: 10.51
    effective: 89.5
    confidence: high
    note: "C1 — SWAPPED in pre-v5 doc. Decomp-confirmed -1 sentinel is on the BOOT path (server kicked us), not graceful disconnect."
  - claim: "Detection Path 4 (connect-clobber): TGWinsockNetwork_ProcessIncomingPackets calls FUN_006b75b0 at 0x006b5d97 when an incoming TGConnectMessage (type 3) arrives from an address already in the peer table with a stale connection ID"
    address: 0x006b5d97
    function: TGWinsockNetwork_ProcessIncomingPackets
    confidence: high
    note: "C3 — MISSING from pre-v5 doc. get_xrefs_to(FUN_006b75b0) returns 4 callers, not 3. After FUN_006b75b0 call, dispatches WSN vtable[0x74] (finalize cleanup) at 0x006b5da4."
  - claim: "Dispatcher FUN_006b5f70 routes type 4 → FUN_006b6a70 and type 5 → FUN_006b6a20 via switch table"
    address: 0x006b60c0
    function: FUN_006b5f70
    confidence: high
    note: "Decomp-confirmed switch dispatch at 0x006b60ab..0x006b60c0 region. Case 4 = FUN_006b6a70 (BOOT). Case 5 = FUN_006b6a20 (DISCONNECT)."
  - claim: "TGBootMessage::GetType returns 0x04"
    address: 0x006bb830
    function: TGBootMessage_GetType
    confidence: high
    note: "Byte-confirmed (MOV EAX, 0x4 at function entry)."
  - claim: "TGDisconnectMessage::GetType returns 0x05"
    address: 0x006bfe70
    function: TGDisconnectMessage_GetType
    confidence: high
    note: "Byte-confirmed (MOV EAX, 0x5 at function entry)."
  - claim: "peer+0x2C is lastRecvTime — written on every received packet in ProcessIncomingPackets"
    address: 0x006b5e63
    function: TGWinsockNetwork_ProcessIncomingPackets
    confidence: high
    note: "C2 — SWAPPED in pre-v5 doc. Disasm: *(int *)(iVar11 + 0x2c) = DAT_0099c6bc. Compared at 0x006b48ae against WSN+0xB8 (timeout threshold)."
  - claim: "peer+0x30 is lastSendTime — written on broadcast send in FUN_006b51e0"
    address: 0x006b51e0
    function: FUN_006b51e0
    confidence: high
    note: "C2 — SWAPPED in pre-v5 doc. Disasm: *(undefined4 *)(iVar1 + 0x30) = DAT_0099c6bc. Compared in FUN_006b4560 keepalive loop against _DAT_0088bd58 (5.0f interval)."
  - claim: "Keepalive interval = 5.0f at DAT_0088bd58"
    address: 0x0088bd58
    function: null
    confidence: high
    note: "Bytes 00 00 a0 40 = 0x40A00000 = 5.0f. Trailing 4 bytes 00 00 a0 c0 = -5.0f."
  - claim: "Peer timeout threshold is per-WSN-instance at WSN+0xB8 (45.0s claimed; set in WSN constructor)"
    address: 0x006b48ae
    function: FUN_006b4560
    confidence: medium
    note: "WSN+0xB8 read confirmed at the timeout-comparison site. The 45.0s value is the prior doc's claim — not byte-checked at the WSN ctor in this pass."
  - claim: "FUN_006b75b0 fallback path calls FUN_006b7590 (per-id flag clear at WSN+0x111+peerID, bounds 1 < peerID < 0x7F)"
    address: 0x006b7643
    function: FUN_006b75b0
    confidence: high
    note: "Byte-confirmed CALL 0x006b7590. FUN_006b7590 body writes byte 0 to WSN+0x111+peerID — a per-peer bitmap flag reset, not 'alternative cleanup'. Clar-4."
  - claim: "Peer-array removal happens later via WSN vtable slot 0x74 (FinalizePeerCleanup at 0x006b9e40), which calls RemovePeerAddress (FUN_006b9f40) then FUN_006b7660 (splice)"
    address: 0x006b9e40
    function: WSN_FinalizePeerCleanup_vfn74
    confidence: high
    note: "Clar-3. DATA xref from WSN vtable at 0x00895964 slot 0x74. Dispatched from ProcessIncomingPackets at 0x006b5da4. FUN_006b9f40 is NOT called directly from FUN_006b75b0."
  - claim: "ET_NETWORK_DELETE_PLAYER (0x60005) registered in MultiplayerGame_Ctor via PUSH 0x60005"
    address: 0x0069e66b
    function: MultiplayerGame_Ctor
    confidence: high
    note: "Byte-confirmed (PUSH 0x60005)."
  - claim: "ET_NETWORK_DISCONNECT (0x60003) registered in MultiplayerGame_Ctor via PUSH 0x60003 — handler at 0x006a0a20 (DisconnectHandler, empty stub for full-network shutdown)"
    address: 0x0069e62b
    function: MultiplayerGame_Ctor
    confidence: high
    note: "C4 — Binary-truth supersession. FUN_0069efe0 binds 0x006a0a20 → string 'MultiplayerGame :: DisconnectHandler' at 0x0095a1f0 (DATA xref confirmed at 0x0069eff9). The Ghidra plate added during leaf #18 calling 0x006a0a20 'EnterSetEventHandler' is WRONG."
  - claim: "Actual EnterSetHandler is at 0x006a07d0 (not 0x006a0a20)"
    address: 0x006a07d0
    function: MultiplayerGame_EnterSetHandler
    confidence: high
    note: "C4 — FUN_0069efe0 binds 0x006a07d0 → string 'EnterSetHandler' at 0x0095a0a8."
  - claim: "BootPlayerHandler (FUN_00506170) registered for ET_BOOT_PLAYER (0x8000F6) by MultiplayerWindow ctor FUN_00504770 at 0x005047d9, NOT by MultiplayerGame_Ctor"
    address: 0x005047d9
    function: FUN_00504770
    completeness: 32.99
    effective: 67.0
    confidence: high
    note: "C5 — Pre-v5 doc grouped BootPlayerHandler under MultiplayerGame in Section 6.1. PUSH 0x8000F6 at 0x005047d9 inside FUN_00504770 (MultiplayerWindow ctor)."
  - claim: "DeletePlayerHandler binds 0x006a0ca0 → string 'MultiplayerGame :: DeletePlayerHandler' at 0x0095a1a4"
    address: 0x0069f049
    function: FUN_0069efe0
    confidence: high
    note: "DATA xref confirmed. String at 0x0095a1a4 byte-confirmed."
  - claim: "Opcode 0x14 (DestroyObject) handler FUN_006a01e0 reads object ID via SWIG ReadIntVirtual"
    address: 0x006a01e0
    function: FUN_006a01e0
    confidence: high
    note: "Decomp-confirmed. 0x14 is used for disconnect-triggered ship cleanup; not used for combat death (see ship-death-lifecycle.md battle-trace evidence of 0/59 combat deaths via 0x14)."
  - claim: "Opcode 0x17 (DeletePlayerUI) handler FUN_006a1360 uses TGFactory_DeserializeObject"
    address: 0x006a1360
    function: FUN_006a1360
    confidence: high
    note: "Decomp-confirmed."
  - claim: "Opcode 0x18 (DeletePlayerAnim) handler FUN_006a1420 opens data/TGL/Multiplayer.tgl, alpha=1.25 (0x3FA00000), dur=5.0 (0x40A00000)"
    address: 0x006a1420
    function: FUN_006a1420
    confidence: high
    note: "Decomp-confirmed."
  - claim: "WSN shutdown sender FUN_006b4060 posts ET_NETWORK_DISCONNECT (0x60003) and constructs TGDisconnectMessage via TGMessage_BufferCopy(buf, 5) — 1-byte param_1[6] + 4-byte param_1[7]"
    address: 0x006b4060
    function: FUN_006b4060
    confidence: high
    note: "Decomp-confirmed at tail of FUN_006b4060."
  - claim: "FUN_006b9f40 (RemovePeerAddress) dereferences WSN+0x348 list head; original code crashed when list was empty — patched by PatchRemovePeerAddress"
    address: 0x006b9f40
    function: FUN_006b9f40
    confidence: high
    note: "NULL deref pattern at function entry decomp-confirmed."
  - claim: "ET_NETWORK_DISCONNECT (0x60003) DisconnectHandler stub at 0x006a0a20 is per-event no-op; per-peer cleanup runs only through ET_NETWORK_DELETE_PLAYER (0x60005)"
    address: 0x006a0a20
    function: MultiplayerGame_DisconnectHandler
    confidence: high
    note: "C4. Function body is a single RET — empty stub. Event 0x60003 fires only on full network shutdown."
companions:
  - docs/networking/ack-outbox-deadlock.md
  - docs/networking/fragmented-ack-bug.md
  - docs/networking/network-protocol.md
  - docs/networking/ship-death-lifecycle.md
  - docs/protocol/objnotfound-requestobj-enterset-wire-format.md
supersedes:
  - 2026-02-19
---

# Player Disconnect Flow

> [!NOTE]
> This doc is `status: partial`. **5 material corrections (2 CRITICAL) + 4 clarifications + 2 OQs**. Critical: Section 1.2/1.3 swaps `FUN_006b6a20` ↔ `FUN_006b6a70` throughout (case 4 = BOOT = `FUN_006b6a70`; case 5 = DISCONNECT = `FUN_006b6a20`); peer offsets **+0x2C and +0x30 are swapped** (+0x2C = lastRecvTime, +0x30 = lastSendTime). **4th convergence path** missed (ProcessIncomingPackets connect-clobber at 0x006b5d97). Section 3.2 attribution of 0x006a0a20 as DisconnectHandler is **BINARY-CORRECT** and supersedes a wrong Ghidra plate added during leaf #18 validation; the doc wins, the plate is wrong. Clar-1 names DAT_0088bd58 = 5.0f byte-confirmed; Clar-2 names WSN+0xB8 as the per-instance timeout threshold; Clar-3 fixes the RemovePeerAddress call chain (it's dispatched via WSN vtable[0x74]); Clar-4 clarifies FUN_006b7590 as a per-id flag clear. See [v5-evidence-header.md](../guides/v5-evidence-header.md) for the standard. Source evidence: `.claude/agent-memory/game-archaeology-specialist/networking-leaf-disconnect-flow-validation-20260528.md`.

Reverse-engineered from stbc.exe via Ghidra decompilation and packet trace inspection.
Confidence: **High** for code paths (v5-validated 2026-05-28); **Verified** for graceful disconnect runtime behavior (wire trace captured 2026-02-19, stock-dedi loopback session).

## Overview

Player disconnects follow a **four-path-convergence** architecture [v5-validated 2026-05-28] — three triggered by network conditions and one triggered by peer rendezvous (connect-clobber). All four converge on `FUN_006b75b0`:

```
PATH 1 — TIMEOUT (~45 seconds):
  TGNetwork_Update (FUN_006b4560)
    iterates peer array (WSN+0x2C array ptr, WSN+0x30 count)
    compares currentTime - peer+0x2C > WSN+0xB8
    creates TGBootPlayerMessage (bootReason=1)
    --> FUN_006b75b0 at 0x006b4898 (peer deletion)

PATH 2 — GRACEFUL DISCONNECT (transport type 0x05):
  ProcessIncomingPackets (FUN_006b5c90)
    receives transport message type 0x05
    FUN_006b5f70 switch case 5 dispatches to FUN_006b6a20
    optionally broadcasts via FUN_006b51e0 (WSN+0x10E gate)
    --> FUN_006b75b0 at 0x006b6a46 (peer deletion)

PATH 3 — BOOT RECEPTION (transport type 0x04):
  ET_BOOT_PLAYER event (0x8000F6) fired on host
    BootPlayerHandler (MultiplayerWindow, FUN_00506170)
    sends TGBootMessage (type 4) to target peer
  Target peer's ProcessIncomingPackets
    FUN_006b5f70 switch case 4 dispatches to FUN_006b6a70
    --> FUN_006b75b0 at 0x006b6aaa (peer deletion)

PATH 4 — CONNECT-CLOBBER (peer rendezvous): [v5-validated 2026-05-28]
  ProcessIncomingPackets receives TGConnectMessage (type 3)
    from an address already in peer table
    with a stale connection ID (peer+0x14 == iVar8 && peer+0x20 != iStack_18)
    --> FUN_006b75b0 at 0x006b5d97 (peer deletion)
    --> WSN vtable[0x74] finalize cleanup at 0x006b5da4

ALL FOUR PATHS CONVERGE:
  FUN_006b75b0 (Peer Deletion Entry Point)
    binary-searches WSN peer array (WSN+0x2C)
    posts ET_NETWORK_DELETE_PLAYER (0x60005)
    sets peer+0xBC = 1 (IsDisconnected flag)
    sets peer+0xB8 = currentTime (disconnect timestamp)
    --> event cascade to game layer

EVENT CASCADE (game layer):
  DeletePlayerHandler (FUN_006a0ca0, registered for 0x60005)
    sends 0x14 DestroyObject to remaining clients
    sends 0x17 DeletePlayerUI to remaining clients
    sends 0x18 DeletePlayerAnim to remaining clients
    --> Python DeletePlayerHandler: RebuildPlayerList()
```

## 1. Disconnect Detection Paths

### 1.1 Peer Timeout (~45 seconds) [v5-validated 2026-05-28]

**Location**: `FUN_006b4560` (TGNetwork_Update tick function)

The WSN (TGWinsockNetwork) tick function runs every frame for hosts in state 2 (hosting). It iterates the peer array at `WSN+0x2C` (array pointer) / `WSN+0x30` (count), checking each peer's last-receive timestamp:

```
for each peer in WSN peer array:
    if peer+0x18 != self.peerID:        // skip self
        if peer+0xBC == 0:              // not already disconnected
            if currentTime - peer+0x2C > WSN+0xB8:   // timeout
                create TGBootPlayerMessage (bootReason=1)
                copy peer+0x18 (peerID) as boot target
                FUN_006b75b0(WSN, peer+0x18)    // delete peer at 0x006b4898
                send boot message to all peers
```

The keepalive send interval is **5.0 seconds** at `DAT_0088bd58` [Clar-1: bytes `00 00 a0 40` = 0x40A00000 byte-confirmed]. The peer timeout threshold is per-WSN-instance at **`WSN+0xB8`** [Clar-2] — the prior doc's "45.0s" is the claimed value (set in the WSN constructor; not byte-checked at the ctor in this pass).

**Correction (C2 — peer offsets +0x2C and +0x30 were SWAPPED in pre-v5)**: The timeout comparison is `currentTime - peer+0x2C > WSN+0xB8`, NOT `peer+0x30`. The prior doc's pseudocode said `peer+0x30 > connectionTimeout`, which is wrong. The actual disassembly at `0x006b48ae` reads:

```
*(float *)((int)param_1 + 0xb8) < local_108 - *(float *)(iVar3 + 0x2c)
```

So **peer+0x2C is lastRecvTime** (updated on every received packet at `0x006b5e63` in ProcessIncomingPackets), and **peer+0x30 is lastSendTime** (updated on broadcast send in `FUN_006b51e0`). The two were inverted in the pre-v5 doc.

**Correction (C2.5 — keepalive interval was abstracted as DAT_0088bd58)**: Earlier documentation stated "~12 second keepalive interval" — the actual send interval is 5.0 seconds. The 12-second observation likely reflected traces where keepalives were suppressed because game data was flowing (keepalives only send when no other data has been sent to the peer recently).

**Key peer fields** (peer object layout, corrected):

| Offset | Type | Field |
|--------|------|-------|
| +0x18 | int | Peer ID (network-assigned) |
| +0x1C | int | Peer address (IP) |
| **+0x2C** | float | **Last receive timestamp (lastRecvTime)** — written every recv at `0x006b5e63`, read at `0x006b48ae` timeout check |
| **+0x30** | float | **Last send timestamp (lastSendTime)** — written on send in `FUN_006b51e0`, read against `DAT_0088bd58` 5.0f keepalive interval |
| +0xB8 | float | Disconnect timestamp (set by FUN_006b75b0) |
| +0xBC | byte | IsDisconnected flag (0=active, 1=disconnected) |

### 1.2 Graceful Disconnect (Transport Message 0x05) [v5-correction 2026-05-28]

**Handler**: `FUN_006b6a20` — dispatched from `FUN_006b5f70` case 5 (TGDisconnectMessage, type 0x05 confirmed by `TGDisconnectMessage::GetType` at `0x006bfe70` returning `0x5`).

> [!IMPORTANT]
> **C1 — Section header swap.** The pre-v5 doc named `FUN_006b6a20` here but the pseudocode shown was actually the body of `FUN_006b6a70` (the boot handler with the `-1` sentinel). Binary truth: case 5 = DISCONNECT = `FUN_006b6a20`; case 4 = BOOT = `FUN_006b6a70`. There is NO `-1` sentinel in the graceful disconnect path.

When a client cleanly exits (ALT+F4, menu quit), it sends transport message type 0x05 (TGDisconnectMessage). The handler:

```c
// FUN_006b6a20 — Graceful disconnect handler (case 5, type 0x05)
void __thiscall FUN_006b6a20(WSN *this, TGMessage *param_1)
{
    char *data = FUN_006b8530(param_1, NULL);    // get message payload
    int peerID = (int)*data;                     // first byte = peer ID

    // No -1 sentinel here. Always proceed to deletion.

    if (peerID == this->field_0x18) {
        // The disconnecting peer is our local host pointer
        this->field_0x10d = 1;      // flag shutdown
    }

    FUN_006b75b0(this, peerID);     // peer deletion (always)

    if (peerID == this->field_0x20) {
        // The disconnecting peer is our peer-self pointer
        this->field_0x10d = 1;      // flag shutdown
    }

    // Broadcast relay: forward the disconnect to other peers
    if (this->field_0x10e != 0) {
        FUN_006b51e0(this, param_1);   // broadcast disconnect msg
    }
}
```

**New behavior identified this pass (C1)**: the graceful disconnect handler includes a **broadcast-relay step** at the tail, gated by `WSN+0x10E`. When this fires (typically on the host), the receiving peer forwards the disconnect message to all remaining peers — this is what propagates a graceful disconnect across the mesh.

The graceful disconnect path reaches `FUN_006b75b0` immediately, without the 45-second timeout delay.

### 1.3 Boot Reception (Transport Message 0x04) [v5-correction 2026-05-28]

**Handler**: `FUN_006b6a70` — dispatched from `FUN_006b5f70` case 4 (TGBootMessage, type 0x04 confirmed by `TGBootMessage::GetType` at `0x006bb830` returning `0x4`).

This is the **receiving** side of a boot/kick. The **sending** side (host initiating the kick) is in Section 1.4.

```c
// FUN_006b6a70 — Boot reception handler (case 4, type 0x04)
void __thiscall FUN_006b6a70(WSN *this, TGMessage *param_1)
{
    char *data = FUN_006b8530(param_1, NULL);
    int peerID = (int)*data;

    if (peerID == -1) {
        // Sentinel: host has kicked US (the local node)
        this->field_0x10d = 1;                       // shutdown flag
        this->field_0x100 = param_1->field_0x40;     // reason
        this->field_0x14 = 2;                        // state -> 2
        return;
    }

    FUN_006b75b0(this, peerID);     // peer deletion

    if (peerID == this->field_0x18) {
        // Boot was for our local host pointer
        this->field_0x10d = 1;
        this->field_0x100 = param_1->field_0x40;
    }
}
```

The `-1` sentinel is what flags "the host has kicked **us**" — and that's why it belongs to the BOOT path, not the graceful disconnect path. The pre-v5 doc attributed this sentinel to graceful disconnect; that was wrong.

### 1.4 Boot/Kick Sender (Host-Initiated) [v5-validated 2026-05-28]

**Event**: ET_BOOT_PLAYER (0x8000F6)
**Handler**: MultiplayerWindow `BootPlayerHandler` at `FUN_00506170` — registered by `FUN_00504770` (MultiplayerWindow ctor) at `0x005047d9` via `PUSH 0x8000F6` [C5].

The kick path is triggered by the anti-cheat system (subsystem hash mismatch — see [subsystem-integrity-hash.md](../protocol/subsystem-integrity-hash.md)) or by explicit host action. The flow:

1. `ET_BOOT_PLAYER` event fires with target peer ID.
2. `BootPlayerHandler` (`FUN_00506170`) constructs a `TGBootPlayerMessage`.
3. Message sent to the target peer.
4. Target peer receives the boot message → enters Path 3 (`FUN_006b6a70`).
5. The host-side also calls `FUN_006b75b0` to remove the peer locally.

This path also converges at `FUN_006b75b0` peer deletion.

### 1.5 Connect-Clobber (Peer Rendezvous) [v5-validated 2026-05-28 — C3, MISSING from pre-v5]

**Location**: `TGWinsockNetwork_ProcessIncomingPackets` at `0x006b5d97`.

When an incoming `TGConnectMessage` (transport type 3) arrives from an address already in the peer table but with a **stale connection ID** (the peer is reconnecting with a fresh handshake), the engine deletes the stale peer entry before re-adding:

```c
// In ProcessIncomingPackets, TGConnectMessage handling
if (peer+0x14 == iVar8 && peer+0x20 != iStack_18) {
    // Stale peer entry — clobber it
    FUN_006b75b0(this, peer+0x18);                       // at 0x006b5d97
    (**(code **)(*this + 0x74))(peer+0x18);              // WSN vtable[0x74] finalize cleanup
}
```

This is a **peer-rendezvous clobber** that bypasses both the 45-second timeout and the type-5 graceful path. It exists so that a reconnecting client (whose previous connection died silently) doesn't have to wait out the full timeout before the new connection can complete.

`get_xrefs_to(FUN_006b75b0)` returns **4 callers** — the connect-clobber here, the timeout path in `FUN_006b4560`, the graceful path in `FUN_006b6a20`, and the boot reception path in `FUN_006b6a70`.

## 2. Peer Deletion (Convergence Point) [v5-validated 2026-05-28]

**Function**: `FUN_006b75b0`
**Convention**: `__thiscall(ECX=WSN, int peerID)`

This is the single convergence point for all four disconnect paths. Decompiled logic:

```c
void __thiscall FUN_006b75b0(WSN *this, int peerID)
{
    if (this->peerArray == NULL)         // WSN+0x2C
        goto fallback;

    // Binary search the peer array for peerID
    int idx = FUN_00401cc0(this->peerArray, peerID);
    if (idx < 0)
        goto fallback;

    Peer *peer = this->peerArray[idx];
    if (peer == NULL)
        goto fallback;

    // Create ET_NETWORK_DELETE_PLAYER event
    TGEvent *event = FUN_00717b70(0x2C);   // PUSH 0x2C at 0x006b75e0 — byte-confirmed
    event = FUN_006bb840(event);
    event->eventType = 0x60005;            // MOV [ESI+0x10], 0x60005 at 0x006b7607
    event->field_0x28 = peerID;

    FUN_006d62b0(event, this);             // set event source
    FUN_006d6270(event, this);             // set event destination
    FUN_006da2a0(&eventManager, event);    // post to global event queue

    // Mark peer as disconnected
    peer->isDisconnected = 1;              // MOV byte [EDI+0xBC], 1 at 0x006b7629
    peer->disconnectTime = DAT_0099c6bc;   // FSTP [EDI+0xB8] at 0x006b7636
    return;

fallback:
    FUN_006b7590(this, peerID);            // per-id flag clear (Clar-4)
}
```

**Important**: The peer is NOT immediately removed from the array. It is marked as disconnected (`peer+0xBC = 1`) and given a timestamp. Actual removal from the peer array happens later via **WSN vtable slot 0x74** [Clar-3]:

```
WSN vtable[0x74] = FUN_006b9e40 (FinalizePeerCleanup)
  --> binary-searches for peer-id
  --> calls FUN_006b9f40 (RemovePeerAddress) — removes IP from WSN+0x348 linked list
  --> calls FUN_006b7660 — array splice + dtor
```

The wrapping vfn is dispatched as `(**(code **)(*this + 0x74))(peerID)` from `ProcessIncomingPackets` (`0x006b5da4`) and other tick sites. `FUN_006b9f40` is **NOT** called directly from `FUN_006b75b0` — the pre-v5 doc was approximately right ("Actual removal in FUN_006b7660") but didn't name the wrapping vfn or its DATA xref from the WSN vtable at `0x00895964` slot 0x74.

**Clar-4 — FUN_006b7590 is a per-id flag clear, not "alternative cleanup"**: The fallback function body writes byte 0 to `WSN + 0x111 + peerID` (bounded `1 < peerID < 0x7F`). This clears a per-peer bitmap flag (probably "is-connecting"). It's a narrow state-machine flag reset that always runs when the peer can't be found in the main array — not a parallel cleanup path.

## 3. Event Cascade

### 3.1 Event Routing

The ET_NETWORK_DELETE_PLAYER event (0x60005) is posted to the global event manager at `DAT_0097f838`. Two systems register handlers for this event:

**C++ Handler (MultiplayerGame)**:
- Registered in `MultiplayerGame_Ctor` via `FUN_006db380(&eventMgr, 0x60005, this, "MultiplayerGame::DeletePlayerHandler", ...)`.
- Handler address: `FUN_006a0ca0` (DeletePlayerHandler) — DATA xref from `FUN_0069efe0` at `0x0069f049` paired with the string at `0x0095a1a4`.

**Python Handler (Mission scripts)**:
```python
App.g_kEventManager.AddBroadcastPythonFuncHandler(
    App.ET_NETWORK_DELETE_PLAYER, pMission,
    __name__ + ".DeletePlayerHandler")
```

### 3.2 DisconnectHandler at 0x006a0a20 is EMPTY [v5-validated 2026-05-28]

> [!IMPORTANT]
> **Binary-truth supersession (C4) [v5-validated 2026-05-28]**: `0x006a0a20` **IS** the `DisconnectHandler` (empty stub for the full-network-shutdown event `0x60003` ET_NETWORK_DISCONNECT). The current Ghidra plate at this address (added during leaf #18 / `docs/protocol/objnotfound-requestobj-enterset-wire-format.md` validation) calls it `EnterSetEventHandler` — that is **WRONG**. The actual `EnterSetHandler` is at `0x006a07d0`.
>
> This finding will be propagated as a corrective patch to leaf #18 in a follow-up handoff.

The handler registered for ET_NETWORK_DISCONNECT (0x60003) at address `0x006a0a20` is a **no-op** — it contains only a `RET` instruction. Binary truth:

- `FUN_0069efe0` binds address `0x006a0a20` → string `"MultiplayerGame :: DisconnectHandler"` at `0x0095a1f0` (DATA xref confirmed at `0x0069eff9`).
- `MultiplayerGame_Ctor` at `0x0069e62b` registers event `0x60003` with the `"DisconnectHandler"` string (PUSH 0x60003 byte-confirmed).
- Separately, `FUN_0069efe0` binds `0x006a07d0` → string `"EnterSetHandler"` at `0x0095a0a8` — that's the actual EnterSet handler.

This event type fires only on full network shutdown (all peers lost), not on individual peer disconnects. The game intentionally handles per-peer cleanup exclusively through ET_NETWORK_DELETE_PLAYER (0x60005). The WSN shutdown sender `FUN_006b4060` posts `0x60003` at its tail and constructs a TGDisconnectMessage via `TGMessage_BufferCopy(buf, 5)` — see Section 9 / OQ1 for wire trace.

### 3.3 DeletePlayerHandler (C++ Layer)

**Address**: `FUN_006a0ca0`
**Event**: ET_NETWORK_DELETE_PLAYER (0x60005)

This handler is **undefined in Ghidra** — it exists only as a function pointer stored by the event registration system, making it invisible to auto-analysis. Based on the opcodes it sends and the Python-level behavior, its responsibilities are:

1. Look up the disconnecting player's ship object.
2. Send **opcode 0x14** (DestroyObject) to remaining clients — removes the ship from the game world (disconnect-triggered cleanup only; see Section 7.3 cross-doc note).
3. Send **opcode 0x17** (DeletePlayerUI) to remaining clients — removes the player from the scoreboard.
4. Send **opcode 0x18** (DeletePlayerAnim) to remaining clients — creates "Player X has left" floating text.
5. Clean up the player's slot in the MultiplayerGame player array (`this+0x74`, 16 slots of 0x18 bytes each).
6. Clean up checksum/file transfer state for that player (via NetFile).

## 4. Cleanup Messages to Remaining Clients

### 4.1 DestroyObject (Opcode 0x14)

**Handler**: `FUN_006a01e0`
**Direction**: Server → All Clients

Removes the disconnected player's ship from the game world.

```
Offset  Size  Type    Field
------  ----  ----    -----
0       1     u8      opcode = 0x14
1       4     i32     object_id     (ship object ID)
```

The handler looks up the object by ID (`FUN_00434e00`, type 0x8003). If the object is a ship (type 0x8006), it calls `vtable[0x138](1, 0)` to mark dead/hide, then `vtable[0](1)` as the destructor with cleanup.

### 4.2 DeletePlayerUI (Opcode 0x17)

**Handler**: `FUN_006a1360`
**Direction**: Server → All Clients

Removes the player from the client's scoreboard and player list.

```
Offset  Size  Type    Field
------  ----  ----    -----
0       1     u8      opcode = 0x17
1       var   stream  connection_id + data_length
```

Decompiled behavior:
1. Reads the connection ID from the message stream.
2. Creates a TGEvent with the connection ID.
3. Posts the event to the event queue.
4. Event is consumed by the UI to remove the player entry.

**Trace note**: 0x17 was observed 6 times in the battle trace and 1 time in the stock-dedi trace, but all instances were at **join time**, not disconnect time. This suggests the opcode serves double duty — removing stale entries when a player slot is reused.

### 4.3 DeletePlayerAnim (Opcode 0x18)

**Handler**: `FUN_006a1420`
**Direction**: Server → All Clients

Creates a floating "Player X has left" text notification on clients.

Decompiled behavior:
1. Reads player name from the message stream.
2. Opens `data/TGL/Multiplayer.tgl` resource file.
3. Looks up the `Delete_Player` entry (a format string template).
4. Creates a text animation object (`FUN_0055c790`) with the formatted player name.
5. Sets alpha/duration: `0x3FA00000` (1.25) opacity, `0x40A00000` (5.0) seconds duration.
6. Attaches to the 3D scene via NiNode.

**Trace note**: 0 instances observed in either available trace, consistent with no player disconnects occurring.

## 5. Python Layer Cleanup

All four mission scripts (Mission1-5, excluding Mission4 which doesn't exist) have identical `DeletePlayerHandler` implementations:

```python
def DeletePlayerHandler(TGObject, pEvent):
    import Mission1Menus    # (or Mission2Menus, etc.)

    # We only handle this event if we're still connected.
    # If we've been disconnected, then we don't handle this
    # event since we want to preserve the score list to
    # display as the end game dialog.
    pNetwork = App.g_kUtopiaModule.GetNetwork()
    if (pNetwork):
        if (pNetwork.GetConnectStatus() == App.TGNETWORK_CONNECTED
            or pNetwork.GetConnectStatus() == App.TGNETWORK_CONNECT_IN_PROGRESS):
            # We do not remove the player from the dictionary.
            # This way, if the player rejoins, his score will
            # be preserved.

            # Rebuild the player list since a player was removed.
            Mission1Menus.RebuildPlayerList()
    return
```

**Key design decisions visible in the code:**

1. **Score preservation**: The handler intentionally does NOT remove the disconnected player from score dictionaries. This enables score persistence if the player reconnects.
2. **Connection guard**: The handler only runs if the network is still connected. During game-end scenarios where the network is torn down, it skips cleanup to preserve the final scoreboard display.
3. **Minimal cleanup**: Only `RebuildPlayerList()` is called — the Python layer doesn't need to clean up game objects (the C++ layer handles that via opcodes 0x14/0x17/0x18).

## 6. Event Handler Architecture

### 6.1 Handler Registrations [v5-correction 2026-05-28 — C5]

**MultiplayerGame ctor (`MultiplayerGame_Ctor` at `0x0069e590`)** — registers via `FUN_006db380` (event types) and `FUN_0069efe0` (handler-name binding):

| Event ID | Handler Address | Handler Name |
|----------|----------------|--------------|
| 0x60001 | 0x0069f2a0 | ReceiveMessageHandler (main opcode dispatch) |
| 0x60003 | 0x006a0a20 | DisconnectHandler (**empty — single RET**; binary-true per C4) |
| 0x60004 | 0x006a0a30 | NewPlayerHandler |
| 0x60005 | 0x006a0ca0 | DeletePlayerHandler |
| 0x8000C8 | 0x006a0f90 | ObjectCreatedHandler |
| — | 0x006a1150 | HostEventHandler |
| — | 0x006a1590 | NewPlayerInGameHandler |
| — | 0x006a1790 | StartFiringHandler |
| — | 0x006a17a0 | StartWarpHandler |
| — | 0x006a17b0 | TorpedoTypeChangeHandler |
| — | 0x006a18d0 | StopFiringHandler |
| — | 0x006a18e0 | StopFiringAtTargetHandler |
| — | 0x006a18f0 | StartCloakingHandler |
| — | 0x006a1900 | StopCloakingHandler |
| — | 0x006a1910 | SubsystemStatusHandler |
| — | 0x006a1920 | AddToRepairListHandler |
| — | 0x006a1930 | ClientEventHandler |
| — | 0x006a1940 | RepairListPriorityHandler |
| — | 0x006a1970 | SetPhaserLevelHandler |
| — | 0x006a1a60 | DeleteObjectHandler |
| — | 0x006a1a70 | ChangedTargetHandler |
| — | 0x006a1b10 | ChecksumCompleteHandler |
| — | 0x006a1240 | ObjectExplodingHandler |
| — | 0x006a07d0 | EnterSetHandler (**not 0x006a0a20** — see C4) |
| — | 0x006a0a10 | ExitedWarpHandler |
| — | 0x006a2640 | KillGameHandler |
| — | 0x006a2a40 | RetryConnectHandler |
| 0x8000E9 | 0x006a2640 | KillGameHandler (also registered for ET_KILL_GAME) |
| 0x8000FF | 0x006a2a40 | RetryConnectHandler (also registered for retry event) |

**MultiplayerWindow ctor (`FUN_00504770`)** — registers via `FUN_006db380` [C5]:

| Event ID | Handler Address | Handler Name | Registration Site |
|----------|----------------|--------------|-------------------|
| 0x8000F6 | 0x00506170 | BootPlayerHandler | `0x005047d9` (PUSH 0x8000F6 inside FUN_00504770) |

**C5 correction**: BootPlayerHandler is registered by the MultiplayerWindow ctor, **not** the MultiplayerGame ctor. The pre-v5 doc grouped it under MultiplayerGame in this table; the prose in Section 1.3/1.4 correctly attributed it to MultiplayerWindow but the table was misleading.

**Analysis note**: Only 5 of the MultiplayerGame handlers are defined as functions in Ghidra's auto-analysis (~17%). The remaining are only reachable via function pointers stored by the event system, making them invisible to standard code flow analysis.

### 6.2 Network Event Types

| Event ID | Constant | Description |
|----------|----------|-------------|
| 0x60001 | ET_NETWORK_MESSAGE_EVENT | Incoming game message |
| 0x60002 | (connect established) | Connection established |
| 0x60003 | ET_NETWORK_DISCONNECT | Full network shutdown (handler `0x006a0a20` is empty per C4) |
| 0x60004 | ET_NETWORK_NEW_PLAYER | New peer connected |
| 0x60005 | ET_NETWORK_DELETE_PLAYER | Peer removed (the per-peer cascade) |
| 0x8000C8 | (object created) | Game object created |
| 0x8000E6 | (checksum result) | Individual checksum done |
| 0x8000E7 | ET_SYSTEM_CHECKSUM_FAILED | Checksum mismatch |
| 0x8000E8 | ET_CHECKSUM_COMPLETE | All checksums passed |
| 0x8000E9 | ET_KILL_GAME | Game killed |
| 0x8000F6 | ET_BOOT_PLAYER | Anti-cheat kick (handler `FUN_00506170` registered by MultiplayerWindow per C5) |
| 0x8000FF | (retry connect) | Connection retry |

## 7. Known Issues and Proxy Considerations

### 7.1 PatchRemovePeerAddress (Fix #18)

**Address**: `0x006B9F40` (TGWinsockNetwork::RemovePeerAddress)
**Convention**: `__thiscall(ECX=WSN, DWORD ipAddress)`

During peer cleanup, the engine calls `RemovePeerAddress` to remove the peer's IP from a singly-linked list at `WSN+0x348`. When this list is empty (head == NULL), the original code dereferences NULL:

```asm
006b9f40: MOV EAX,[ECX+0x348]   ; load list head
006b9f46: MOV EDX,[ESP+0x4]     ; load param_1 (IP addr)
006b9f4a: CMP [EAX],EDX         ; CRASH when EAX==0
```

**Fix**: Code cave at function entry adds `TEST EAX,EAX / JZ .early_ret`, returning cleanly via `RET 0x4` when the list head is NULL. This happens during client disconnect when `RemovePeerAddress` is called for a peer that was never fully added to the address list.

**Note (Clar-3)**: `FUN_006b9f40` is NOT called directly from `FUN_006b75b0`. It is dispatched via WSN vtable slot 0x74 (`FUN_006b9e40` FinalizePeerCleanup, DATA xref from `0x00895964`). The pre-v5 doc's Section 2 description ("Actual removal in FUN_006b7660") was approximately right but didn't name the wrapping vfn.

### 7.2 DeletePlayerHandler Not Registered (Headless Server)

In the headless dedicated server, the mission scripts may not register their Python `DeletePlayerHandler` for `ET_NETWORK_DELETE_PLAYER`. This means the Python-level cleanup (rebuilding the player list) may not fire. The C++ DeletePlayerHandler still runs since it's registered by the MultiplayerGame constructor.

**Impact**: Low. The Python handler only rebuilds the UI player list, which is irrelevant for a headless server. Score dictionaries are preserved regardless.

### 7.3 Disconnect Trace Evidence

**Graceful disconnect captured** in the 2026-02-19 stock-dedi loopback trace (22,119 lines, ~91-second session). See Section 9 for full wire trace analysis.

Prior trace evidence:
- **0x17 DeletePlayerUI**: 6 instances in battle trace, 1 in stock-dedi — **all at join time** (reuse of player slots), not disconnect.
- **0x18 DeletePlayerAnim**: 0 instances in either trace.
- **0x14 DestroyObject**: Observed for disconnect-triggered ship cleanup (**NOT for combat kills** — see [ship-death-lifecycle.md](ship-death-lifecycle.md) for the 33.5-min battle trace showing **0/59 combat deaths use 0x14**).
- **Transport 0x05 Disconnect**: 1 instance captured (2026-02-19 trace, packet #1764).

## 8. Key Functions

| Address | Name | Role |
|---------|------|------|
| `FUN_006b4560` | TGNetwork_Update | WSN tick: timeout detection, keepalive, packet processing |
| `FUN_006b5c90` | ProcessIncomingPackets | Receives UDP packets, dispatches transport messages; hosts connect-clobber Path 4 at 0x006b5d97 |
| `FUN_006b5f70` | DispatchReceivedMessages | Switch table: case 4 → FUN_006b6a70 (BOOT), case 5 → FUN_006b6a20 (DISCONNECT) |
| `FUN_006b6a20` | GracefulDisconnectHandler (case 5, type 0x05) | Handles TGDisconnectMessage; relays via FUN_006b51e0 if WSN+0x10E set |
| `FUN_006b6a70` | BootReceptionHandler (case 4, type 0x04) | Handles TGBootMessage; -1 sentinel = host kicked us |
| `FUN_006b75b0` | PeerDeletion | Convergence point: marks peer+0xBC=1, peer+0xB8=time, posts 0x60005 event |
| `FUN_006b7660` | PeerArrayRemove | Splices peer from WSN array, calls destructor; dispatched via vtable[0x74] |
| `FUN_006b7590` | PeerIdFlagClear | Writes 0 to WSN+0x111+peerID (per-peer bitmap reset) |
| `FUN_006b9e40` | FinalizePeerCleanup (WSN vtable[0x74]) | Wrapper: binary-searches, calls RemovePeerAddress + FUN_006b7660 |
| `FUN_006b9f40` | RemovePeerAddress | Removes IP from WSN+0x348 linked list (patched for NULL deref) |
| `FUN_006b51e0` | TGNetwork_Broadcast | Writes peer+0x30 lastSendTime; relays disconnect msg when called from FUN_006b6a20 |
| `FUN_006b4060` | TGNetwork_Shutdown | Sends WSN-shutdown TGDisconnectMessage via TGMessage_BufferCopy(buf, 5); posts 0x60003 |
| `FUN_006a0a20` | DisconnectHandler (0x60003) | **EMPTY** — single RET; full-shutdown event only (C4) |
| `FUN_006a07d0` | EnterSetHandler | Actual EnterSet handler (NOT 0x006a0a20 — C4) |
| `FUN_006a0ca0` | DeletePlayerHandler (0x60005) | Game-level cleanup: sends 0x14, 0x17, 0x18 |
| `FUN_006a01e0` | DestroyObject_Net | Opcode 0x14 handler: removes object from game world |
| `FUN_006a1360` | DeletePlayerUI | Opcode 0x17 handler: removes player from scoreboard |
| `FUN_006a1420` | DeletePlayerAnim | Opcode 0x18 handler: "Player X has left" text |
| `FUN_00506170` | BootPlayerHandler | MultiplayerWindow handler for ET_BOOT_PLAYER (0x8000F6) — registered at 0x005047d9 (C5) |
| `FUN_00504770` | MultiplayerWindow_Ctor | Registers BootPlayerHandler at 0x005047d9 |
| `FUN_00401cc0` | BinarySearchPeerArray | Binary search helper used by FUN_006b75b0 |

## 9. Verified Graceful Disconnect (Wire Trace, 2026-02-19)

**Source**: stock-dedi loopback trace, OBSERVE_ONLY proxy build (zero patches). Session: client connects at 11:37:53, disconnects at 11:39:24 (~91 seconds of gameplay).

### 9.1 Pre-Disconnect Activity

Last game data packets (PythonEvents seq=39, 40) at 11:39:21.416. Client ACKs for seq=39 and seq=40 are retransmitted 3 times (11:39:21.419, 22.085, 22.753) — this is the ACK-outbox accumulation bug (see [fragmented-ack-bug.md](fragmented-ack-bug.md)).

### 9.2 Disconnect Packet (Client → Server)

```
#1764 C->S Peer#0(127.0.0.1:60271) len=20 [Disconnect]
Decrypted:
  0000: 02 03 05 0A C0 02 00 02 0A 0A 0A EF 01 27 00 00  |.............'..|
  0010: 01 28 00 00                                      |.(..|
DECODE: peer=C(2) msgs=3
  [msg 0] Disconnect (0x05) byte1=0x0A
  [msg 1] ACK seq=39
  [msg 2] ACK seq=40
```

**Wire format breakdown**:
- `02` — peer_id (client = 2)
- `03` — msg_count (3 transport messages in this packet)
- `05` — **transport type 0x05 = TGDisconnectMessage** (verified, GetType at 0x006bfe70)
- `0A C0 02 00 02 0A 0A 0A EF` — disconnect payload (9 bytes, content TBD — see OQ1)
- `01 27 00 00` — stale ACK for seq=39 (type 0x01, seq LE 0x0027, flags 0x00, non-fragmented)
- `01 28 00 00` — stale ACK for seq=40

**Key observation**: The disconnect message is **multiplexed** with stale ACKs from the ACK-outbox in a single UDP packet. The ACK-outbox accumulation bug means every outbound packet — including the disconnect — carries all accumulated stale ACKs.

### 9.3 Server ACK Response

Server immediately responds with an ACK for the disconnect (seq=2, low-type):

```
#1765 S->C len=6 [ACK]
  01 01 01 02 00 02
DECODE: peer=S(1) msgs=1
  [msg 0] ACK seq=2
```

The server then **retransmits this ACK 7 times** over ~4 seconds:

| Packet | Time | Content |
|--------|------|---------|
| #1765 | 11:39:24.854 | ACK seq=2 |
| #1766 | 11:39:25.519 | ACK seq=2 |
| #1767 | 11:39:26.187 | ACK seq=2 |
| #1768 | 11:39:26.853 | ACK seq=2 |
| #1769 | 11:39:27.520 | ACK seq=2 |
| #1770 | 11:39:28.188 | ACK seq=2 |
| #1771 | 11:39:28.855 | ACK seq=2 |

Interval: ~0.67 seconds between retransmits. This is the ACK-outbox accumulation bug again — the server's ACK for the disconnect message is never removed from its outbox, so it retransmits until the peer entry is eventually cleaned up. Consistent with leaf #9 ack-outbox-deadlock findings; not re-verified here (OQ2).

### 9.4 GameSpy Heartbeat

Immediately after the disconnect retransmits stop:

```
#1772 S->C Peer#1(81.205.81.173:27900) len=47 GAMESPY_HEARTBEAT
  \heartbeat\0\gamename\bcommander\statechanged\1
```

The `statechanged=1` signals to the master server that the server's player count has changed (player disconnected). This is the **only externally-visible artifact** of a disconnect.

### 9.5 Complete Verified Graceful Disconnect Timeline

```
11:39:21.416  Last game data: PythonEvent seq=39, seq=40 (S->C)
11:39:21.419  Client ACKs seq=39, seq=40 (C->S) — first send
11:39:22.085  Client retransmits ACKs seq=39, seq=40 (stale ACK bug)
11:39:22.753  Client retransmits ACKs again
11:39:24.851  Client sends DISCONNECT (0x05) + stale ACKs (C->S)
11:39:24.854  Server ACKs disconnect (seq=2) (S->C)
11:39:25.519  Server retransmits ACK seq=2
   ... 5 more retransmits at ~0.67s intervals ...
11:39:28.855  Last ACK retransmit
11:39:29.016  GameSpy heartbeat with statechanged=1
```

Total disconnect processing time: **~4.2 seconds** from disconnect message to GameSpy notification. The ~3.3-second gap between the last game data and the disconnect message is the client's shutdown sequence (saving state, closing UI, etc.).

## 10. Open Questions

### OQ1 — 9-byte disconnect payload exceeds 5-byte shutdown copy

`FUN_006b4060` (WSN shutdown sender) constructs the WSN-shutdown TGDisconnectMessage with `TGMessage_BufferCopy(&local_8, 5)` — copies 5 bytes (1-byte `param_1[6]` + 4-byte `param_1[7]`). But the captured packet in Section 9.2 shows **9 bytes** of payload after the type byte (`0A C0 02 00 02 0A 0A 0A EF`).

Possibilities:
- The proxy's transport decoder is interpreting bytes beyond the 5-byte payload as additional transport headers and the decode framing is off.
- The disconnect message has its own framing layered on top of the 5-byte payload (e.g., transport headers carried per-message).
- The 5-byte size applies only to the WSN-shutdown self-sent path; the client's outgoing disconnect uses a different constructor.

Worth a follow-up decode pass against the wire — promote to a correction if the payload semantic is identified.

### OQ2 — Server-side ACK retransmit gating

Section 9.3 shows the server retransmitting the disconnect ACK 7× at ~0.67s intervals. This is consistent with the [ack-outbox-deadlock.md](ack-outbox-deadlock.md) findings (leaf #9), but not re-verified here. If the ACK-outbox cleanup happens when the peer is finally evicted from the WSN array (Section 2 cascade), the retransmit count should match the time-to-eviction.

---

## Appendix: Complete Disconnect Sequence (Timeout Path)

The most common disconnect scenario — a player's network connection drops silently:

```
Time 0s:     Player stops sending packets (network failure, process crash, etc.)
Time 0-45s:  Server continues sending StateUpdates and keepalives to the peer
             peer+0x2C (lastRecvTime) stops advancing       [C2-corrected]
Time ~12s:   Keepalive cycle completes; no response received
Time ~24s:   Second keepalive cycle missed
Time ~36s:   Third keepalive cycle missed
Time ~45s:   TGNetwork_Update detects timeout:
               currentTime - peer+0x2C > WSN+0xB8           [C2-corrected]
             Creates TGBootPlayerMessage (bootReason=1)
             Calls FUN_006b75b0(WSN, peerID) at 0x006b4898:
               - Searches peer array for peerID
               - Sets peer+0xBC = 1 (IsDisconnected)
               - Sets peer+0xB8 = currentTime
               - Posts ET_NETWORK_DELETE_PLAYER (0x60005)
             Sends boot message to remaining peers

Time ~45s+:  Event system delivers 0x60005 to handlers:
             C++ DeletePlayerHandler (FUN_006a0ca0):
               - Sends 0x14 DestroyObject (removes ship)
               - Sends 0x17 DeletePlayerUI (removes from scoreboard)
               - Sends 0x18 DeletePlayerAnim ("Player X has left")
               - Cleans up player slot in MultiplayerGame
             Python DeletePlayerHandler:
               - Calls RebuildPlayerList()
               - Scores preserved in dictionaries

Time ~45s+:  WSN vtable[0x74] (FUN_006b9e40 FinalizePeerCleanup):
               - RemovePeerAddress (FUN_006b9f40) removes IP from WSN+0x348 list
                 (protected by PatchRemovePeerAddress NULL check)
               - FUN_006b7660 splices peer from WSN array
               - Peer object destructed
             Player fully removed from server state.
```
