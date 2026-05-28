> [docs](../README.md) / [protocol](README.md) / tgmessage-routing.md

---
title: TGMessage Routing (relay rules, broadcast groups, per-handler routing)
type: reference
audience: re-engineer
validated: 2026-05-28
methodology: FUNCTION_DOC_WORKFLOW_V5
binary:
  name: STBC.exe
  size: 6394712
  base: 0x00400000
status: partial
companions:
  - docs/protocol/transport-layer.md
  - docs/protocol/python-messages.md
  - docs/protocol/wire-format-spec.md
  - docs/protocol/game-opcodes.md
  - docs/networking/network-protocol.md
  - docs/engine/decompiled-functions.md
  - docs/protocol/v5-validation-status.md
supersedes:
  - (prior pre-v5 tgmessage-routing.md)
evidence:
  - claim: "Transport factory table at DAT_009962D4 is 256 entries x 4 bytes (BSS, zero-init at load). 7 slots are populated at runtime by TGWinsockNetwork_Ctor at 0x006B3A00 gated by `DAT_00995E60 == 0` (first-time init flag). The 7 registrations: slot 0x00 -> TGDataMessage factory (FUN_006BC6A0); slot 0x01 -> TGHeaderMessage factory (FUN_006BD1F0); slot 0x02 -> TGConnectMessage factory (FUN_006BDD10); slot 0x03 -> TGConnectAckMessage factory (FUN_006BE860); slot 0x04 -> TGBootMessage factory (FUN_006BADB0); slot 0x05 -> TGDisconnectMessage factory (FUN_006BF410); slot 0x32 -> TGMessage factory (FUN_006B83F0)."
    address: 0x009962d4
    function: TGWinsockNetwork_Ctor
    completeness: high
    confidence: high
    note: "Foundation #3 transport-layer C4 confirmed the 0x40-byte type-0x32 class is TGMessage; the other 6 types are subclasses with their own ctors. Cross-anchor with transport-layer.md."
  - claim: "SWIG wrapper `TGNetwork_RegisterMessageType` at 0x005E4860 performs `AND EAX, 0xFF` followed by `MOV [EAX*4 + 0x009962D4], EDX`. The `& 0xFF` mask is the only bounds-check applied to incoming type bytes - a natural byte wrap, not a validation. Stock Python never calls this wrapper; all script messages use the existing type-0x32 transport."
    address: 0x005e4860
    function: (SWIG TGNetwork_RegisterMessageType wrapper)
    completeness: high
    confidence: high
    note: "Format string `bO:TGNetwork_RegisterMessageType` at 0x00938724. The mask + indexed store is byte-level visible in the disassembly."
  - claim: "Type-0x00 factory (FUN_006BC6A0): 14-bit length mask `(uVar2 & 0x3FFF)`, NO fragment support. Header bit 15 = reliable (-> obj+0x3A), bit 14 = ack-required (-> obj+0x3B). Payload starts at byte 5 when header is non-zero, else byte 3. Performs opaque BufferCopy of the payload into the message data buffer - never reads the game-opcode byte that sits at the head of the payload."
    address: 0x006bc6a0
    function: TGDataMessage_Factory
    completeness: high
    confidence: high
  - claim: "Type-0x32 factory (FUN_006B83F0): 13-bit length mask `(uVar2 & 0x1FFF)`, fragment bit at `(uVar2 & 0x2000)`. Header bit 15 = reliable, bit 14 = ack-required, bit 13 = fragment. Fragment metadata at obj+0x38 (sequence-in-chain) and obj+0x39 (total fragments). Same opaque-payload semantics as type-0x00."
    address: 0x006b83f0
    function: TGMessage_Factory_Type32
    completeness: high
    confidence: high
    note: "Foundation #3 transport-layer covers the fragment reassembly path in TGMessage_ReassembleFragments at 0x006B6CC0."
  - claim: "TGWinsockNetwork_SendTGMessage at 0x006B4C10 has THREE modes selected by the `targetID` argument: (1) targetID == -1 -> `LEA ECX, [ESI + 0x28]; CALL FUN_006BB9D0(nOptional)`, which walks the peer array at `network+0x2C` (count `network+0x30`) looking for `peer+0x1C == nOptional`. Returns 0xB if no peer matches. (2) targetID > 0 -> binary-searches the peer array sorted by `peer+0x18`. Hit -> enqueue on that peer; miss but targetID == `network+0x20` (local-player ID) -> FUN_006B7410 creates a local peer; else returns 0xB. (3) targetID == 0 -> broadcast: loops the entire peer array, skips peers with `peer+0xBC == 1` (disconnecting), Clones via vtable[6] for all but the last peer (the last reuses the caller's pMessage)."
    address: 0x006b4c10
    function: TGWinsockNetwork_SendTGMessage
    completeness: 29.07
    confidence: high
    note: "All three modes byte-level verified. The targetID == -1 mode (peer+0x1C key) is what python-messages.md OQ4 was asking about; the function it calls is FUN_006BB9D0."
  - claim: "TGWinsockNetwork_SendTGMessageToGroup at 0x006B4DE0 binary-searches the group table at `network+0xF4` (count `network+0xF8`) sorted by group-name string at `[entry+0x04]` via an unrolled 2-bytes-at-a-time strcmp at 0x006B4E22. On hit it calls TGWinsockNetwork_SendToGroup_Iterate at 0x006B4EC0; on miss it releases the message and returns 0x10."
    address: 0x006b4de0
    function: TGWinsockNetwork_SendTGMessageToGroup
    completeness: 71.27
    confidence: high
  - claim: "TGWinsockNetwork_SendToGroup_Iterate at 0x006B4EC0 iterates the group's member array (group+0x8 base, group+0xC count), looks up each member peer in `network+0x2C` via the binary-search-by-`peer+0x18` lookup, and queues a vtable[6] Clone per member. This is the routing mechanism shared by both the Python `NoMe` group and the C++ `Forward` group."
    address: 0x006b4ec0
    function: TGWinsockNetwork_SendToGroup_Iterate
    completeness: high
    confidence: high
  - claim: "`NoMe` group-name string at 0x008E5528 and `Forward` group-name string at 0x008D94A0 are both built by `MultiplayerGame_Ctor` at 0x0069E590 (string xrefs at 0x0069E6FA for `NoMe`-creation site and 0x0069E716 for `Forward`-creation site). They are NOT created by Python - Python only calls SendTGMessageToGroup against them. Group construction is gated on `DAT_0097FA8A` (g_IsMultiplayer) AND `DAT_0097FA78` (TGWinsockNetwork singleton) being non-zero."
    address: 0x0069e590
    function: MultiplayerGame_Ctor
    completeness: 5.39
    confidence: high
    note: "Pre-v5 doc credited Python with creating `NoMe`. This is C2 correction: C++ ctor creates the groups; Python USES them. Anchor inherited from python-messages.md row #6 validation."
  - claim: "MultiplayerGame dispatcher (FUN_0069F2A0) gates on the wire stream's class tag: `vtable[0]() != 0x32` returns immediately. After the tag check it bias-decodes the game opcode `(opcode - 2)` and bounds-checks `EAX > 0x28` (=== opcodes > 0x2A); out-of-range branches to the default cleanup at 0x0069F525. The jump table at 0x0069F534 has 41 entries covering opcodes 0x02-0x2A."
    address: 0x0069f2a0
    function: MpgameHandleMessage
    completeness: 69.84
    confidence: high
    note: "Foundation cross-anchor with game-opcodes.md (full 41-row decoded jump table) and wire-format-spec.md."
  - claim: "Opcodes 0x06 (PythonEvent) AND 0x0D (PythonEvent2) BOTH route to FUN_0069F880 via the same wrapper at 0x0069F3F1 - they share the same LOCAL-ONLY handler. FUN_0069F880 instantiates a TGEvent via factory FUN_006D6200, resolves refs via FUN_006F13C0, zeroes the preserve field at `puVar2[9]`, and posts via FUN_006DA300. It contains NO SendToGroup or BroadcastToOthers call - the handler never relays."
    address: 0x0069f3f1
    function: FUN_0069F880
    completeness: high
    confidence: high
    note: "Confirms relay-audit-20260224 observation: 31 C->S of 0x0D, 0 S->C. Cross-source [trace] tag below."
  - claim: "Opcodes 0x07, 0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0E, 0x0F, 0x10, 0x11, 0x12, 0x1B all route to FUN_0069FDA0 (GenericEventForward). Inside FUN_0069FDA0 the handler explicitly Clones the message (vtable[6]) and calls TGWinsockNetwork_SendToGroup with the `Forward` group resolved via FUN_006A2FC0(s_Forward_008D94A0). This is the per-handler relay pattern - relay is NOT a property of the transport, it is something each handler chooses to do."
    address: 0x0069fda0
    function: FUN_0069FDA0
    completeness: high
    confidence: high
    note: "Opcode 0x19 TorpedoFire uses FUN_0069F930 with the same Clone + SendToGroup(`Forward`) pattern. The relay-audit ratios (StartFiring 174:172, TorpedoFire 110:110, etc.) match this 1:1 explicitly."
  - claim: "Opcode 0x13 HostMsg routes to FUN_006A01B0 which processes the self-destruct request locally and does NOT call any SendToGroup / Broadcast / Send variant. Confirms relay-audit observation of 3 C->S, 0 S->C. This is the canonical example of a non-relayed game opcode."
    address: 0x006a01b0
    function: HostMsgHandler
    completeness: high
    confidence: high
  - claim: "MultiplayerWindow dispatcher (FUN_00504C10) handles only opcodes 0x00 (Settings), 0x01 (GameInit), 0x16 (UICollision) via explicit byte compares - no jump table. All other game opcodes silently fall through. This dispatcher runs alongside MpgameHandleMessage on the same ET_NETWORK_MESSAGE_EVENT (0x60001)."
    address: 0x00504c10
    function: MultiplayerWindow_Dispatch
    completeness: high
    confidence: high
  - claim: "TGBufferStream_GetBufferAndSize at 0x006B8530 returns `*(void**)(this+4)` and writes the size into the caller-provided `*sizeOut` pointer. This is the function pre-v5 docs called `TGMessage::GetData` - the new name reflects what the disassembly actually does (two-output accessor over the wire-container's data buffer + length)."
    address: 0x006b8530
    function: TGBufferStream_GetBufferAndSize
    completeness: high
    confidence: high
    note: "Foundation #3 transport-layer naming. The behavior is the same; the prior name was inaccurate about the second output."
  - claim: "FUN_006B63A0 is the connect-event handler, NOT a type-0x00 game-data relay. Body: parses the peer ID from the connect message, registers the peer via FUN_006B7410, raises event 0x60007 (ET_NEW_PEER_CONNECTED) via the event manager. The call to FUN_006B51E0 inside it broadcasts the CONNECT EVENT itself so other clients learn about the join - this is a connection-coordination broadcast, not a game-data relay path."
    address: 0x006b63a0
    function: TGWinsockNetwork_HandleConnect
    completeness: high
    confidence: high
    note: "C1 correction. Pre-v5 doc named FUN_006B63A0 the type-0x00 host auto-relay. The misattribution made the doc claim transport-level automatic relay; in reality each game opcode handler chooses whether to relay. FUN_006B6A20 is the symmetric disconnect handler."
companions_resolved:
  - docs/protocol/transport-layer.md (TGMessage envelope, 7 transport-type factories)
  - docs/protocol/python-messages.md (SendTGMessage three-mode routing - shared anchor)
  - docs/protocol/wire-format-spec.md (jump table + 41 opcode rows)
  - docs/protocol/game-opcodes.md (per-opcode handler addresses)
  - docs/networking/network-protocol.md (architecture overview)
  - docs/engine/decompiled-functions.md (dispatcher anchors)
---

# TGMessage Routing in Stock Dedicated Server

How TGMessages are routed, filtered, and dispatched in Bridge Commander (`stbc.exe`). The
focus is on **how the host decides who receives what**: the relay rules, the broadcast
groups, and the per-handler routing decisions that determine whether a client-sent
message ever reaches the other clients.

See also: [tgmessage-routing-cleanroom.md](../networking/tgmessage-routing-cleanroom.md)
for a clean-room behavioral specification (no addresses or decompiled code).

> [!NOTE]
> This doc is `status: partial`. The C++ side (transport factory table, RegisterMessageType,
> Type-0x00 and Type-0x32 factories, SendTGMessage 3-mode routing including
> `targetID == -1` (peer+0x1C lookup via `FUN_006BB9D0`), SendTGMessageToGroup binary
> search, SendToGroup_Iterate, dispatcher boundary, and the per-handler relay pattern) is
> v5-validated against the current Ghidra import (2026-05-28). Three material corrections
> from the pre-v5 doc:
>
> - **C1.** `FUN_006B63A0` is the connect-event handler, not a type-0x00 game-data relay.
>   The true game-data relay is per-handler, via `SendToGroup("Forward")`.
> - **C2.** The `NoMe` group is created by C++ `MultiplayerGame_Ctor` at 0x0069E590, not
>   by Python.
> - **C3.** There are THREE routing mechanisms (per-handler `Forward` + Python `NoMe` +
>   connect-event broadcast), not two.
>
> Plus minor corrections: function name `0x006B8530` is `TGBufferStream_GetBufferAndSize`
> (not "TGMessage::GetData"), and the `SendTGMessage` pseudocode now covers the
> `targetID == -1` branch. Stock-dedi trace observations from the 2026-02-24 relay audit
> (21-min Cady/XFS01 session) are tagged `[cross-source-2026-02-24 trace]`. See
> [v5-evidence-header.md](../guides/v5-evidence-header.md) for the standard.

---

## Executive Summary

| Question | Answer |
|----------|--------|
| Does the server whitelist message types? | **No - relay-all.** |
| Does the server examine the type byte on relay? | **No - payload is opaque.** |
| Is there a maximum message type value? | **No - byte range (0-255) is the only limit.** |
| Can clients send directly to other clients? | **No - star topology, all through host.** |

Custom mod message types (Kobayashi Maru 205/211-214, BC Remastered 53-57, team modes
63-65) work because the transport layer is opaque, the C++ dispatcher silently ignores
unknown opcodes, and Python event handlers process them on `ET_NETWORK_MESSAGE_EVENT`.

---

## Three Routing Mechanisms

[v5-validated 2026-05-28] The headline correction to the pre-v5 doc: there are **three**
routing mechanisms, not two. Each one decides who receives a message; none of them is a
transport-level automatic relay.

| Mechanism | Used by | C++ implementation | Trace evidence |
|-----------|---------|--------------------|----------------|
| Per-handler `Forward` group | C++ game-opcode handlers (the FUN_0069FDA0 pattern) | Each handler explicitly Clones the message and calls `SendToGroup("Forward")` | `[cross-source-2026-02-24 trace]` opcodes 0x07, 0x08, 0x0A, 0x10, 0x11, 0x12, 0x19, 0x1B relayed at ~1:1 |
| Python `NoMe` group | Python script messages (opcodes >= 0x2C) | `SendTGMessageToGroup("NoMe", msg)` from Python; broadcasts to all peers except the host | `[cross-source-2026-02-24 trace]` 0x36 SCORE_CHANGE sent to ALL clients simultaneously (10 S->C for 5 C->S in chat case) |
| Connect-event broadcast | `TGWinsockNetwork_HandleConnect` (FUN_006B63A0) and the symmetric disconnect handler (FUN_006B6A20) | Specific broadcast pattern that raises event 0x60007 (`ET_NEW_PEER_CONNECTED`) and tells other clients about the join/leave | Per-join handshake observation |

**Two ideas to keep separate** when reading this doc:

1. **Routing-by-target** (where the message goes). SendTGMessage / SendTGMessageToGroup /
   SendToGroup_Iterate decide *who* gets the message based on `targetID` or a named group.
2. **Decision-to-relay** (who calls one of the above). The per-handler relay pattern is
   the key insight: a game-opcode handler must *choose* to call SendToGroup("Forward").
   If it doesn't, the message stays local on the host and never reaches other clients.

The pre-v5 doc framed relay as something the transport layer did automatically. The
binary doesn't work that way: the dispatcher routes the message to a per-opcode handler,
and that handler decides whether to clone-and-forward.

---

## Two Independent Type Systems

A common source of confusion: there are **two separate type bytes** in the message stack.

### Transport Type (outer layer)

- First byte of each sub-message within a UDP packet.
- Indexes into a 256-entry factory table at `DAT_009962D4`.
- Only 7 of 256 slots populated (types 0x00-0x05 and 0x32).
- Determines how to deserialize the wire bytes into a TGMessage object.

### Game Opcode (inner layer)

- First byte of the TGMessage **payload** (inside a type-0x00 or type-0x32 transport message).
- Dispatched by three C++ handlers and by Python event handlers.
- This is the byte that `MAX_MESSAGE_TYPES` and mod custom types refer to.

All game messages - stock and modded - use the existing transport types (0x00 or 0x32).
No mod registers a custom transport type. Custom message variety comes from the game-opcode
inner byte.

---

## Transport Layer

### Factory Table (0x009962D4)

[v5-validated 2026-05-28] The table is 256 entries x 4 bytes (BSS, zero-init at load).
`TGWinsockNetwork_Ctor` at `0x006B3A00` populates 7 slots at runtime, gated by
`DAT_00995E60 == 0` (the first-time-init flag).

| Type | Factory | Registration fn | Class | Purpose |
|------|---------|------------------|-------|---------|
| 0x00 | `FUN_006BC6A0` | `FUN_006BC5A0` | TGDataMessage | Game message carrier (14-bit length, no fragments) |
| 0x01 | `FUN_006BD1F0` | `FUN_006BD110` | TGHeaderMessage | ACK / reliable transport |
| 0x02 | `FUN_006BDD10` | `FUN_006BDC30` | TGConnectMessage | Connection request |
| 0x03 | `FUN_006BE860` | `FUN_006BE720` | TGConnectAckMessage | Connection acknowledgement |
| 0x04 | `FUN_006BADB0` | `FUN_006BAC60` | TGBootMessage | Boot / disconnect |
| 0x05 | `FUN_006BF410` | `FUN_006BF2D0` | TGDisconnectMessage | Graceful disconnect |
| 0x32 | `FUN_006B83F0` | `FUN_006B8290` | TGMessage | General-purpose game payload (13-bit length, fragment support) |

Types 0x06-0x31 and 0x33-0xFF are NULL. When the receive processor encounters a NULL
factory entry it silently returns - no crash, no error log.

### Factory Registration

[v5-validated 2026-05-28] The SWIG wrapper `TGNetwork_RegisterMessageType` at `0x005E4860`
implements:

```asm
AND  EAX, 0xFF
MOV  [EAX*4 + 0x009962D4], EDX
```

That `AND EAX, 0xFF` is the only "bounds check" - a natural byte wrap, not a validation.
The format string `bO:TGNetwork_RegisterMessageType` at `0x00938724` confirms the SWIG
binding. Stock Python **never** calls this function - every mod that needs custom message
types reuses the type-0x32 transport with a custom game-opcode byte at the head of the
payload.

### Type-0x00 Factory (FUN_006BC6A0) - Opaque Copy

[v5-validated 2026-05-28]

```c
TGMessage* factory(byte* data) {
    msg = alloc(0x40);                          // TGMessage object
    uint16_t header = *(uint16_t*)(data + 1);   // flags + length
    uint16_t payload_len = (header & 0x3FFF) - 3;
    msg->reliable = (header >> 15) & 1;         // -> obj+0x3A
    msg->ack_required = (header >> 14) & 1;     // -> obj+0x3B
    // payload starts at byte 5 if header != 0, else byte 3
    BufferCopy(msg, payload_data, payload_len); // OPAQUE COPY
    return msg;
}
```

The payload bytes (including the game opcode at `payload[0]`) are copied verbatim. The
factory does not read, validate, or filter the game opcode. Length mask is 14 bits, so
type-0x00 messages cap at 16 KB - 1 of payload. There is **no fragment support** in this
type.

### Type-0x32 Factory (FUN_006B83F0) - Same Pattern, Plus Fragments

[v5-validated 2026-05-28] Same opaque-payload semantics as type-0x00, with two differences:

- Length mask is 13 bits (`uVar2 & 0x1FFF`) - 8 KB - 1 payload cap per fragment.
- Bit 13 is the fragment flag (`uVar2 & 0x2000`).
- Fragment metadata at `obj+0x38` (sequence-in-chain) and `obj+0x39` (total fragments).

Fragment reassembly happens in `TGMessage_ReassembleFragments` at `0x006B6CC0` - see
[transport-layer.md](transport-layer.md) for the 256-entry reassembly index detail.

---

## Packet Receive Path

### Wire -> Factory -> Queue

[v5-validated 2026-05-28] `TGWinsockNetwork_ProcessIncomingPackets` (`FUN_006B5C90`,
called from `TGWinsockNetwork::Update` at `0x006B4560`):

```
1. Read raw UDP payload (after AlbyRules decryption — see transport-layer.md)
2. byte[0] = sender_peer_id
3. byte[1] = sub_message_count
4. For each sub-message:
   a. Read transport_type = first byte
   b. factory = factory_table[transport_type * 4]
   c. If NULL -> return (drop entire remaining packet)
   d. msg = factory(wire_data)         <- deserialize (opaque copy)
   e. msg->from_id = sender_peer_id
   f. If msg->is_reliable -> ACK tracking (FUN_006B61E0)
   g. FUN_006B6AD0 -> queue for dispatch
```

**Key finding (unchanged from pre-v5):** the receive path never examines the game opcode
inside the payload. It only checks the transport type (for factory lookup) and the
reliable flag (for ACK handling). Once a TGMessage object is in the dispatch queue, the
**handler** decides what to do with it - including whether to relay it.

---

## Per-Handler Relay Pattern (replaces "Host Relay Path - Opaque Forwarding")

[v5-validated 2026-05-28] This is the **C1 correction**. The pre-v5 doc described a
single host-side relay mechanism rooted at `FUN_006B63A0` that automatically forwarded
all type-0x00 game messages. That's wrong on two counts: `FUN_006B63A0` is the connect-event
handler (see Connect-Event Broadcast below), and there is no transport-level automatic
relay for game data. Relay is **per-handler**.

### The pattern

A game-opcode handler that wants to forward its message to other clients does so
explicitly:

```c
void GenericEventForward(/* this, */ TGMessage* msg, uint32_t event_code_override) {
    TGEvent* evt = factory.deserialize(msg);
    if (event_code_override != 0) evt->event_code = event_code_override;
    PostLocalEvent(evt);                    // local processing

    // ---- the relay decision ----
    TGMessage* clone = msg->vtable[6](msg); // Clone
    TGGroup* fwd = FindGroup("Forward");    // FUN_006A2FC0 with s_Forward at 0x008D94A0
    SendToGroup_Iterate(this->network, fwd, clone);
}
```

The handler chooses to relay by:

1. **Cloning** the message via `vtable[6]` (so the original can be released after local
   processing).
2. **Looking up** the `Forward` group at `network+0xF4` via `FUN_006A2FC0(s_Forward_008D94A0)`.
3. **Calling** `TGWinsockNetwork_SendToGroup_Iterate` to enqueue per group member.

This is the entire mechanism. A handler that doesn't make these calls doesn't relay. The
audit trace's per-opcode relay ratios fall directly out of which handlers do or don't make
the SendToGroup call.

### Which handlers relay, which don't

[v5-validated 2026-05-28 - dispatcher decode] [cross-source-2026-02-24 trace - audit ratios]

| Opcode | Name | Handler | Relays via? | Trace ratio C:S/S:C |
|--------|------|---------|-------------|---------------------|
| 0x06 | PythonEvent | FUN_0069F880 | NO - LOCAL ONLY | (not observed in audit C->S) |
| 0x07 | StartFiring | FUN_0069FDA0 (push 0x008000D7) | YES - Forward | 174:172 |
| 0x08 | StopFiring | FUN_0069FDA0 (push 0x008000D9) | YES - Forward | 86:87 |
| 0x09 | StopFiringAtTarget | FUN_0069FDA0 (push 0x008000DB) | YES - Forward | — |
| 0x0A | SubsysStatus | FUN_0069FDA0 (push 0x0080006C) | YES - Forward | 60:71 (also server-generated) |
| 0x0B | AddToRepairList | FUN_0069FDA0 (push 0x008000DF) | YES - Forward | — |
| 0x0C | ClientEvent | FUN_0069FDA0 (push 0) | YES - Forward (wire event-code preserved) | — |
| 0x0D | PythonEvent2 | FUN_0069F880 | NO - LOCAL ONLY (same handler as 0x06) | 31:0 |
| 0x0E | StartCloak | FUN_0069FDA0 (push 0x008000E3) | YES - Forward | — |
| 0x0F | StopCloak | FUN_0069FDA0 (push 0x008000E5) | YES - Forward | — |
| 0x10 | StartWarp | FUN_0069FDA0 (push 0x008000ED) | YES - Forward | 2:2 |
| 0x11 | RepairListPriority | FUN_0069FDA0 (push 0) | YES - Forward (wire event-code preserved) | 4:4 |
| 0x12 | SetPhaserLevel | FUN_0069FDA0 (push 0) | YES - Forward (wire event-code preserved) | 5:5 |
| 0x13 | HostMsg | FUN_006A01B0 | NO - self-destruct processed locally | 3:0 |
| 0x14 | DestroyObject | FUN_006A01E0 | (no relay call observed - verify) | 0:0 |
| 0x15 | CollisionEffect | FUN_006A2470 | NO - server processes, generates 0x06 PythonEvent damage instead | 2:0 |
| 0x17 | DeletePlayerUI | FUN_006A1360 | NO | — (server-generated 7 S->C) |
| 0x18 | DeletePlayerAnim | FUN_006A1420 | (no relay call observed - verify) | — |
| 0x19 | TorpedoFire | FUN_0069F930 | YES - Forward (same Clone+SendToGroup pattern) | 110:110 |
| 0x1A | BeamFire | FUN_0069FBB0 | (no relay call observed - verify) | 0:0 |
| 0x1B | TorpTypeChange | FUN_0069FDA0 (push 0x008000FD) | YES - Forward | 1:1 |
| 0x1C | StateUpdate | FUN_0069FF50 | YES - server also generates for all owned objects | 23994:45355 |
| 0x29 | Explosion | FUN_006A0080 | (server-generated only, no client send observed) | 0 obs |
| 0x2A | NewPlayerInGame | FUN_006A1E70 | NO - triggers join handshake locally | 4:0 |

The ratio column tells you which handlers relay (~1:1) vs which absorb (`x:0`). The
`Forward`-relayed group is exactly the set of opcodes routed to `FUN_0069FDA0` or to a
sibling handler that follows the same Clone+SendToGroup pattern.

The 1:0 absorb pattern for 0x0D PythonEvent2 is the clearest demonstration that the relay
decision is per-handler: 0x0D shares `FUN_0069F880` with 0x06 - a handler that contains
no SendToGroup call at all.

---

## SendTGMessage and Group Broadcasts

### SendTGMessage (0x006B4C10) - three modes

[v5-validated 2026-05-28] The router has THREE modes, selected by the `targetID` argument:

```c
int SendTGMessage(this, int targetID, TGMessage* msg, int optionalArg) {
    if (targetID == -1) {
        // MODE A: lookup by peer+0x1C key
        // FUN_006BB9D0 walks peer array at network+0x2C (count network+0x30)
        // looking for peer with peer+0x1C == optionalArg
        peer = FUN_006BB9D0(this->peerSubarray, optionalArg);
        if (!peer) return 0xB;
        QueueForSend(this, msg, peer);
    } else if (targetID > 0) {
        // MODE B: binary search by peer+0x18 (persistent network ID)
        peer = BinarySearchPeerArray(this->peers, targetID);
        if (!peer && targetID == this->localID) {
            peer = FUN_006B7410(this, ...);  // create local peer if missing
        }
        if (!peer) return 0xB;
        QueueForSend(this, msg, peer);
    } else {
        // MODE C: broadcast (targetID == 0)
        for (peer in peer_array):
            if (peer->disconnecting) continue;  // peer+0xBC == 1
            if (last_peer) {
                QueueForSend(this, msg, peer);   // reuse caller's msg
            } else {
                clone = msg->vtable[6](msg);     // Clone
                QueueForSend(this, clone, peer);
            }
    }
}
```

The pre-v5 pseudocode omitted the `targetID == -1` branch entirely. It's the answer to
the `peer+0x1C` lookup mystery that python-messages.md OQ4 flagged: SendTGMessage with
`targetID == -1` uses the 4th argument as a `peer+0x1C` key, and `FUN_006BB9D0` resolves
the peer. The semantics of `peer+0x1C` itself remain open - see Open Questions below.

### SendTGMessageToGroup (0x006B4DE0)

[v5-validated 2026-05-28]

```c
int SendTGMessageToGroup(this, char* group_name, TGMessage* msg) {
    // Binary-search the group table at network+0xF4 (count network+0xF8)
    // sorted by group-name string at [entry+0x04].
    // strcmp is unrolled 2-bytes-at-a-time at 0x006B4E22.
    group = FindGroupByName(this->groups, group_name);
    if (!group) {
        msg->Release();
        return 0x10;  // ERR_GROUP_NOT_FOUND
    }
    return SendToGroup_Iterate(this, group, msg);  // FUN_006B4EC0
}
```

The binary-search-by-name detail matters for clean-room implementations: the group table
must be kept sorted by name, and lookup is `O(log N)`.

### SendToGroup_Iterate (0x006B4EC0)

[v5-validated 2026-05-28] Iterates the group's member array at `group+0x8` (count
`group+0xC`), looks up each member peer in `network+0x2C` via the same
binary-search-by-`peer+0x18` lookup that targetID > 0 uses, and queues a `vtable[6]`
Clone per member. This is the routing primitive shared by **both** the `NoMe` and
`Forward` groups - no payload inspection, purely a routing fan-out.

### The `NoMe` Group

[v5-validated 2026-05-28] **Correction (C2):** the `NoMe` group is created by C++
`MultiplayerGame_Ctor` at `0x0069E590`, not by Python. The pre-v5 doc said Python creates
it; that's wrong - Python only **uses** it.

- Group-name string `NoMe` at `0x008E5528`.
- Group-name string `Forward` at `0x008D94A0`.
- Both built by `MultiplayerGame_Ctor` (string xrefs at `0x0069E6FA` and `0x0069E716`).
- Construction gated on `DAT_0097FA8A` (g_IsMultiplayer) AND `DAT_0097FA78`
  (TGWinsockNetwork singleton) being non-zero.
- Each group is a 0x14-byte struct with vtable `PTR_FUN_00894684`, registered on
  `network+0xF4` via `FUN_006B70D0`.

Python then uses the groups via SWIG `TGNetwork_SendTGMessageToGroup` (wrapper at
`0x005E3B20`, format `OOO:TGNetwork_SendTGMessageToGroup` at `0x0093848C`). For example,
from `MultiplayerMenus.py` (line ~2276):

```python
if (App.g_kUtopiaModule.IsHost()):
    pNewMessage = pMessage.Copy()
    pNetwork.SendTGMessageToGroup("NoMe", pNewMessage)
```

`NoMe` means "Not Me" - all connected peers EXCEPT the host. The group's member array is
maintained by `MultiplayerGame` as peers join and leave. The mechanism is purely a routing
selector: it picks recipients, it does not filter content.

---

## Connect-Event Broadcast (FUN_006B63A0)

[v5-validated 2026-05-28] **Correction (C1):** `FUN_006B63A0` is the **connect-event
handler**, NOT a game-data relay path. The pre-v5 doc misattributed all type-0x00 host
auto-relay to this function. The actual body of `FUN_006B63A0`:

1. Parses the peer ID from the incoming TGConnectMessage.
2. Registers the peer in `network+0x2C` via `FUN_006B7410`.
3. Raises event `0x60007` (`ET_NEW_PEER_CONNECTED`) via the event manager.
4. Calls `FUN_006B51E0` to **broadcast the connect event** so other clients learn about
   the new peer.

That `FUN_006B51E0` call is what the pre-v5 doc was looking at when it called this
function a relay - but the message being broadcast is the **connect event itself**, not
some game-data message the new peer sent. Game data (type-0x32 with a game opcode) does
not pass through this function at all.

The symmetric disconnect handler is `FUN_006B6A20`; it uses the same connect-event
broadcast pattern (gated by `this+0x10E`, the host flag) to tell other clients about a
peer leaving.

This is mechanism #3 of the three. It is reserved for transport-level connection events
(join, leave) and does not relay arbitrary messages.

---

## C++ Dispatchers

### MultiplayerGame Dispatcher (0x0069F2A0)

[v5-validated 2026-05-28]

```c
void MultiplayerGame_ReceiveMessage(this, event) {
    TGMessage* msg = event->message;
    // class-tag gate: must be a type-0x32 wire-container
    if (msg->vtable[0]() != 0x32) return;

    byte* data;
    size_t len;
    data = TGBufferStream_GetBufferAndSize(msg, &len);  // FUN_006B8530
    byte opcode = data[0];

    // bias-decode + bounds: jump table covers 0x02..0x2A
    eax = opcode - 2;
    if (eax > 0x28) goto default_cleanup;          // 0x0069F525
    jmp [jump_table_at_0x0069F534 + eax * 4];

    // ... 41 case bodies ...

  default_cleanup:
    DAT_0097FA8B = 0;  // clear "processing" flag
}
```

The 41-entry jump table at `0x0069F534` covers opcodes 0x02 through 0x2A; the bias is
`-2` because index 0 corresponds to opcode 0x02. Opcodes 0x04, 0x05, 0x16, and 0x20-0x28
share the default cleanup at `0x0069F525` (does no work, just clears the re-entrancy
flag) - they are either dead, routed to a sibling dispatcher, or owned by the NetFile
dispatcher. The full per-row decode lives in
[wire-format-spec.md](wire-format-spec.md) and [game-opcodes.md](game-opcodes.md); the
relay column matches the Per-Handler Relay Pattern table above.

Opcodes outside the switch (0x2C, 0x35, 0xCD, etc.) fail the bias-bounds check and fall
through to the default cleanup. No error log, no rejection - **silently ignored by C++**,
which is precisely what makes Python script messages and mod custom opcodes work.

### MultiplayerWindow Dispatcher (FUN_00504C10)

[v5-validated 2026-05-28] Handles only opcodes 0x00 (Settings), 0x01 (GameInit), 0x16
(UICollision) via explicit byte compares - no jump table. All other opcodes silently
ignored. Runs alongside `MpgameHandleMessage` on the same `ET_NETWORK_MESSAGE_EVENT`
(0x60001).

### NetFile Dispatcher (FUN_006A3CD0)

Handles checksum / file-transfer opcodes 0x20-0x27 (non-contiguous; 0x24 and 0x26 have
no handler). See [checksum-opcodes.md](checksum-opcodes.md) for the canonical opcode map.

### Maximum message type? -> No explicit limit

[v5-validated 2026-05-28]

- The C++ switch has no default case (other than the silent cleanup) and the bias-bounds
  check is `EAX > 0x28` only.
- Unknown opcodes simply fall through silently.
- The game opcode is a single byte (0x00-0xFF), so 256 values maximum by byte width.
- Within that range, any value not handled by C++ is available for Python.

---

## Python Message Dispatch

### Stock Message Type Allocation

See [python-messages.md](python-messages.md) for the canonical MAX_MESSAGE_TYPES table
and SWIG wrapper layout. Summary:

- `MAX_MESSAGE_TYPES = 43` (0x2B), SWIG-registered at `0x00654F31`, value stored at
  `0x0090B490`.
- Python scripts define their message types as `MAX_MESSAGE_TYPES + N`.
- Stock occupies the byte ranges 44-45 (chat), 53-57 (mission lifecycle), 63-65 (team
  modes). 46-52 and 66-255 are available for mods.

### Python Receive Path

Python handlers are registered on `ET_NETWORK_MESSAGE_EVENT` and fire for ALL incoming
TGMessages. They read the first payload byte, compare against known constants, and ignore
unknowns. No bounds check, no rejection of unrecognized types.

```python
# Mission1.py line ~220:
def ProcessMessageHandler(self, pEvent):
    pMessage = pEvent.GetMessage()
    kStream = pMessage.GetBufferStream()
    cType = ord(kStream.ReadChar())     # read game opcode from payload

    if cType == MissionShared.MISSION_INIT_MESSAGE:   # 0x35
        ...
    elif cType == MissionShared.SCORE_CHANGE_MESSAGE: # 0x36
        ...
    elif cType == MissionShared.SCORE_MESSAGE:        # 0x37
        ...
    elif cType == MissionShared.RESTART_GAME_MESSAGE: # 0x39
        ...
```

[python-source: `scripts/MissionShared.py`, `scripts/MultiplayerMenus.py`,
`scripts/Mission*/`] The above pattern is Python-side and cannot be anchored from the
binary alone.

### Chat Relay (Python-level, host-side)

```python
# MultiplayerMenus.py line ~2273:
if (cType == CHAT_MESSAGE):           # 0x2C
    if (App.g_kUtopiaModule.IsHost()):
        pNewMessage = pMessage.Copy()
        pNetwork.SendTGMessageToGroup("NoMe", pNewMessage)
    # then display locally...

elif (cType == TEAM_CHAT_MESSAGE):    # 0x2D
    if (App.g_kUtopiaModule.IsHost()):
        # team routing: determine sender's team, forward only to teammates
        for each player:
            if player in same team:
                pNetwork.SendTGMessage(player.GetNetID(), pMessage.Copy())
```

Chat relay happens in **Python**, on the host, using the `NoMe` group (mechanism #2).
There is no C++ auto-relay for chat - the dispatcher silently drops 0x2C (opcode >= 0x2C
fails the bias-bounds check), and the Python handler is the **only** path that forwards
the message to other clients.

---

## Star Topology - Client-to-Client Routing

```
Client A  <->  HOST  <->  Client B
                ^
Client C  <-----'
```

### Evidence

[v5-validated 2026-05-28 - structural] [cross-source-2026-02-24 trace - peer-map]

1. **Client peer array:** clients have exactly ONE peer entry - the host. When a client
   calls `SendTGMessage(0, msg)` (broadcast), it goes ONLY to the host.
2. **Host peer array:** host has entries for ALL connected clients. When host calls
   `SendTGMessage(0, msg)` (broadcast), it goes to all clients.
3. **No peer-to-peer connections:** the connect-event handler `FUN_006B63A0` only runs on
   the host (gated by `this+0x10E`). Clients never accept incoming connections from other
   clients.
4. **Three routing mechanisms, all centralized on the host:**
   - C++ per-handler `Forward` group relay (mechanism #1) - host runs the dispatcher,
     host's handler does the SendToGroup.
   - Python `NoMe` group relay (mechanism #2) - host's Python `ProcessMessageHandler`
     does the SendTGMessageToGroup.
   - Connect-event broadcast (mechanism #3) - host's `FUN_006B63A0` raises 0x60007 and
     calls `FUN_006B51E0`.

### Broadcast Semantics by Role

| Caller | `SendTGMessage(0, msg)` | `SendTGMessageToGroup("NoMe", msg)` | `SendToGroup("Forward", msg)` (in handler) |
|--------|--------------------------|--------------------------------------|---------------------------------------------|
| Client | -> host only (1 peer) | -> host only (1 peer; client's peer array is just the host) | (not used by clients - relay is host-only) |
| Host | -> all clients | -> all clients (host excluded from group) | -> all clients except the sender |

The `Forward` group's member list is maintained as "all peers except the original
sender", which is what makes per-handler relay produce a clean "to other clients" fan-out
without double-delivery.

---

## Why Mod Custom Types Work

### Kobayashi Maru (types 205, 211-214)

1. KM Python writes `chr(205)` as the first byte of the TGMessage payload.
2. Sends via `SendTGMessage(0, msg)` to broadcast to all peers (which on a client means
   "to the host").
3. Transport layer wraps in a type-0x32 transport message (opaque payload).
4. Host's Python `ProcessMessageHandler` on `ET_NETWORK_MESSAGE_EVENT` reads byte 205
   from the payload - KM's handler matches and processes the message. The C++
   dispatcher's `MpgameHandleMessage` silently drops 205 because 205 > 0x2A fails the
   bias-bounds check.
5. If the host's Python wants to forward to other clients, it calls
   `SendTGMessageToGroup("NoMe", clone)` - mechanism #2.

### BC Remastered (types 53-57)

Same mechanism. Types 53-57 are `MAX_MESSAGE_TYPES + 10` through `+14`, the same values
as stock `MISSION_INIT_MESSAGE` through `RESTART_GAME_MESSAGE`. BCR replaces the stock
Python handlers with its own - no conflict because Python dispatch is by-script-handler,
not by-opcode-registration.

### The Critical Enabler

The C++ dispatcher's **silent fallthrough for unknown opcodes** is what makes all mod
message types work. If `MpgameHandleMessage` had a default case that logged an error or
dropped the message at a higher layer, mods would break. The bias-bounds check
(`EAX > 0x28`) is permissive: it routes anything out of range to a no-op, leaving Python
free to handle it.

---

## PythonEvent 0x06 vs 0x0D: Both Local-Only

[v5-validated 2026-05-28] **Critical finding (unchanged from pre-v5):** neither
PythonEvent (0x06) nor PythonEvent2 (0x0D) is relayed by the server. Both route to the
same handler `FUN_0069F880` at the jump-table wrapper `0x0069F3F1`, and `FUN_0069F880` is
LOCAL-ONLY - it deserializes the event and posts it to the local EventManager. There is
**no SendToGroup call** in the handler body.

The relay handler (`FUN_0069FDA0`) is not involved.

### Dispatcher decode (jump table 0x0069F534)

| Index | Opcode | Wrapper | Real handler | Relay? |
|-------|--------|---------|--------------|--------|
| 0x04 | 0x06 PythonEvent | 0x0069F3F1 | FUN_0069F880 | NO - LOCAL ONLY |
| 0x0B | 0x0D PythonEvent2 | 0x0069F3F1 (same wrapper) | FUN_0069F880 | NO - same handler |

### Trace evidence (Cady/XFS01 21-min, 2 players)

[cross-source-2026-02-24 trace]

| Opcode | C->S | S->C | Ratio | Interpretation |
|--------|------|------|-------|----------------|
| 0x0D PythonEvent2 | 31 | 0 | 1:0 | NOT relayed (absorbed; target-change events) |
| 0x07 StartFiring | 174 | 172 | ~1:1 | Relayed via `Forward` (FUN_0069FDA0) |
| 0x19 TorpedoFire | 110 | 110 | 1:1 | Relayed via `Forward` (FUN_0069F930) |
| 0x13 HostMsg | 3 | 0 | 1:0 | Absorbed (self-destruct trigger) |

The 1:0 absorb pattern for 0x0D confirms it is NOT relayed.

### How Clients Actually Receive PythonEvents (0x06)

Clients receive opcode 0x06 from the server, but these are **freshly constructed
messages**, not relays of anything a client sent:

1. **HostEventHandler** (LAB_006A1150): catches repair events (0x008000DF, 0x00800074,
   0x00800075), creates a NEW opcode 0x06 message, sends to `NoMe` group.
2. **ObjectExplodingHandler** (LAB_006A1240): catches death event (0x0080004E), creates
   a NEW opcode 0x06 message, sends to `NoMe` group.

These are the only two server-side producers of S->C PythonEvent messages.

### OpenBC Parity Bug

OpenBC currently relays 0x0D to all peers. That's WRONG - it causes duplicate events on
receiving clients and leaks events that should be server-private. **Fix:** stop relaying
0x0D. Process locally on the server only, same as 0x06.

---

## Open Questions

1. **OQ1 - peer+0x1C semantics.** SendTGMessage mode A (targetID == -1) uses
   `peer+0x1C` as the lookup key via `FUN_006BB9D0(optionalArg)`. The field is plausibly a
   connection-token / session-ID derived from `FUN_006B7540` (called inside the connect
   handler), but the exact semantics aren't anchored yet. Worth a dedicated FUN_006B7540
   deep-dive. (Inherited from python-messages.md OQ4; this validation closes the *call site*
   - it's `FUN_006BB9D0` doing a peer-array walk against `peer+0x1C` - but not the *meaning*
   of the field.)

2. **OQ2 - Does Python ever call SendTGMessage with targetID == -1?** Stock Python code
   that's been read so far calls SendTGMessage with `0` (broadcast) or with a positive
   peer ID. Whether any stock or mod script invokes the targetID == -1 mode is not
   determined - would require a script-corpus grep over SendTGMessage call sites checking
   the first numeric arg.

3. **OQ3 - Chat echo 1:2 ratio.** The 2026-02-24 audit shows `0x2C CHAT_MESSAGE` at
   5 C->S, 10 S->C - i.e. each chat message reaches **two** receive slots, not the one
   "echo to the other client" you'd expect from the `NoMe`-only model. `NoMe` excludes
   the host, so each chat reaches one OTHER client, not two. Possible explanations:
   - **(a)** Python ALSO displays the chat locally on receive **and** relays it, and the
     audit's "receive" count is inflated by counting the local display as a delivered
     message.
   - **(b)** There's an undiscovered second relay path - maybe a per-handler C++ relay we
     haven't located, or the team-chat code path firing for ordinary chat in some
     condition.
   - Worth a dedicated chat-trace investigation with a single-message-per-test cadence
     to disambiguate.

---

## Key Addresses

| Address | Function | Role |
|---------|----------|------|
| 0x006B3A00 | `TGWinsockNetwork_Ctor` | Initializes factory table, MTU, cipher state |
| 0x006B4560 | `TGWinsockNetwork::Update` | Main network tick; posts TGMessageEvent on 0x60001 |
| 0x006B4C10 | `TGWinsockNetwork_SendTGMessage` | 3-mode router: -1 (peer+0x1C lookup), >0 (binary-search), 0 (broadcast) |
| 0x006B4DE0 | `TGWinsockNetwork_SendTGMessageToGroup` | Binary-search group table by name |
| 0x006B4EC0 | `TGWinsockNetwork_SendToGroup_Iterate` | Iterates group members, Clones per member |
| 0x006B51E0 | (broadcast helper used by connect handler) | Connect-event broadcast (mechanism #3) |
| 0x006B5080 | `TGWinsockNetwork_QueueMessageForPeer` | Per-peer send-queue enqueue |
| 0x006B5C90 | `TGWinsockNetwork_ProcessIncomingPackets` | Wire -> factory -> queue |
| 0x006B63A0 | `TGWinsockNetwork_HandleConnect` | Connect-event handler (NOT a game-data relay) |
| 0x006B6A20 | (symmetric disconnect handler) | Disconnect-event broadcast |
| 0x006B7410 | (peer register) | Creates peer entry; called from connect handler |
| 0x006B7540 | (peer+0x1C source - candidate) | Likely produces connection-token written to peer+0x1C (OQ1) |
| 0x006B82A0 | `TGMessage_Ctor` | Allocates 0x40-byte TGMessage; vtable 0x008958D0 |
| 0x006B83F0 | `TGMessage_Factory_Type32` | Type-0x32 deserialize (13-bit length + fragments) |
| 0x006B8530 | `TGBufferStream_GetBufferAndSize` | Returns `*(void**)(this+4)` + writes size to *out (NOT "TGMessage::GetData") |
| 0x006BB9D0 | (peer+0x1C lookup helper) | Walks peer array; targetID == -1 mode uses this |
| 0x006BC6A0 | `TGDataMessage_Factory` | Type-0x00 deserialize (14-bit length, opaque copy) |
| 0x0069E590 | `MultiplayerGame_Ctor` | Builds `NoMe` and `Forward` groups (C++; not Python) |
| 0x0069F2A0 | `MpgameHandleMessage` | Game opcode switch (0x02-0x2A); jump table at 0x0069F534 |
| 0x0069F3F1 | (PythonEvent wrapper) | Routes 0x06 AND 0x0D to FUN_0069F880 (LOCAL ONLY) |
| 0x0069F525 | (default cleanup) | Silent fallthrough; clears `DAT_0097FA8B` re-entrancy flag |
| 0x0069F880 | `FUN_0069F880` | PythonEvent / PythonEvent2 handler (LOCAL ONLY) |
| 0x0069F930 | `FUN_0069F930` | TorpedoFire handler (relays via `Forward`) |
| 0x0069FDA0 | `FUN_0069FDA0` | GenericEventForward - 12 opcodes share this; relays via `Forward` |
| 0x00504C10 | `MultiplayerWindow_Dispatch` | UI opcodes (0x00 Settings, 0x01 GameInit, 0x16 UICollision) |
| 0x006A3CD0 | `NetFile_Dispatch` | Checksum / file-transfer opcodes (0x20-0x27, non-contiguous) |
| 0x009962D4 | (transport factory table) | 256-entry, 7 populated; indexed by transport-type byte |
| 0x005E4860 | (SWIG `TGNetwork_RegisterMessageType`) | `AND EAX, 0xFF; MOV [EAX*4 + 0x009962D4], EDX` - never called by stock Python |
| 0x008E5528 | (string `NoMe`) | Group-name string; xref at 0x0069E6FA in MultiplayerGame_Ctor |
| 0x008D94A0 | (string `Forward`) | Group-name string; xref at 0x0069E716 in MultiplayerGame_Ctor |
