> [docs](../README.md) / [networking](README.md) / tgmessage-routing-cleanroom.md

---
title: TGMessage Routing — Clean Room Specification
type: reference
audience: openbc-implementer
validated: 2026-05-28
methodology: FUNCTION_DOC_WORKFLOW_V5
binary:
  name: stbc.exe
  size: 6394712
  base: 0x00400000
status: partial
companions:
  - docs/protocol/tgmessage-routing.md
  - docs/protocol/transport-layer.md
  - docs/protocol/python-messages.md
  - docs/protocol/game-opcodes.md
  - docs/networking/network-protocol.md
supersedes:
  - (prior pre-v5 tgmessage-routing-cleanroom.md)
evidence:
  - claim: "MultiplayerGame dispatcher is the C++ event handler that switches on game opcode 0x02-0x2A via a 41-entry jump table; opcodes outside this range silently fall through. This is the dispatcher whose per-handler relay decisions define the relay policy for game data."
    address: 0x0069F2A0
    function: MpgameHandleMessage
    completeness: 69.84
    confidence: high
    note: "Cross-anchored via docs/protocol/tgmessage-routing.md row #9. Jump table at 0x0069F534, bias `(opcode - 2)`, default cleanup at 0x0069F525."
  - claim: "41-entry game-opcode jump table covering opcodes 0x02-0x2A is the structure that delegates to the per-opcode handlers (FUN_0069F880, FUN_0069FDA0, FUN_0069F930, FUN_006A01B0, etc.). Each handler decides independently whether to relay; relay is NOT a property of the dispatcher or transport."
    address: 0x0069F534
    function: MpgameHandleMessage
    completeness: high
    confidence: high
    note: "Cross-anchored via docs/protocol/tgmessage-routing.md row #9 and docs/protocol/game-opcodes.md."
  - claim: "Opcodes 0x06 (PythonEvent) and 0x0D (PythonEvent2) both route to FUN_0069F880 via the same wrapper at 0x0069F3F1; FUN_0069F880 deserializes the TGEvent, posts to the local EventManager, and contains NO SendToGroup or Clone call. PythonEvent opcodes are LOCAL-ONLY at the handler — there is no relay."
    address: 0x0069F880
    function: MpgameHandlePythonEvent
    completeness: high
    confidence: high
    note: "Cross-anchored via docs/protocol/tgmessage-routing.md row #10. OpenBC implementers MUST NOT relay 0x06 or 0x0D — doing so produces duplicate event delivery (the OpenBC parity bug)."
  - claim: "Opcodes 0x07, 0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0E, 0x0F, 0x10, 0x11, 0x12, 0x1B all route to GenericEventForward, which performs the per-handler relay: vtable[6] Clone of the message, FUN_006A2FC0 lookup of the `Forward` group, and TGWinsockNetwork_SendToGroup_Iterate to fan-out. Relay is gated on `DAT_0097FA8A` (g_IsMultiplayer) AND `DAT_0097FA78` (TGWinsockNetwork singleton) being non-null."
    address: 0x0069FDA0
    function: GenericEventForward
    completeness: high
    confidence: high
    note: "Cross-anchored via docs/protocol/tgmessage-routing.md row #11. This is the canonical per-handler relay helper — implementers MUST replicate this per-opcode pattern, not implement a transport-level relay."
  - claim: "TGWinsockNetwork_HandleConnect is the connect-event handler. Body: parses peer ID from the incoming TGConnectMessage, registers the peer via FUN_006B7410, raises event 0x60007 (ET_NEW_PEER_CONNECTED), and calls FUN_006B51E0 to broadcast the connect event itself to other clients. Gated on `this+0x10E` (host flag). This is connection coordination, NOT game-data relay."
    address: 0x006B63A0
    function: TGWinsockNetwork_HandleConnect
    completeness: high
    confidence: high
    note: "Cross-anchored via docs/protocol/tgmessage-routing.md row #14. The pre-v5 doc misattributed transport-level auto-relay to this function — that was wrong. The symmetric disconnect handler is FUN_006B6A20."
  - claim: "TGWinsockNetwork_SendToGroup_Iterate is the routing primitive shared by both the C++ `Forward` group and the Python `NoMe` group. Iterates the group member array (group+0x8 base, group+0xC count), binary-searches each member peer in `network+0x2C` by `peer+0x18`, and queues a vtable[6] Clone per recipient. Purely a routing fan-out — does not inspect the payload."
    address: 0x006B4EC0
    function: TGWinsockNetwork_SendToGroup_Iterate
    completeness: high
    confidence: high
  - claim: "MultiplayerGame_Ctor creates BOTH the `NoMe` group (used by Python) AND the `Forward` group (used by the per-handler C++ relay). NOT Python. Group construction is gated on `DAT_0097FA8A` (g_IsMultiplayer) AND `DAT_0097FA78` (TGWinsockNetwork singleton) being non-zero."
    address: 0x0069E590
    function: MultiplayerGame_Ctor
    completeness: 5.39
    confidence: high
    note: "Cross-anchored via docs/protocol/tgmessage-routing.md row #8. String xrefs at 0x0069E6F9, 0x0069E715 (`NoMe`) and 0x0069E784, 0x0069E7A0 (`Forward`). OpenBC implementers MUST create these groups during server-side multiplayer init, NOT in Python script init."
  - claim: "`NoMe` group-name string is the literal `NoMe` at address 0x008E5528; the string is referenced from inside MultiplayerGame_Ctor at the two xref sites listed."
    address: 0x008E5528
    function: MultiplayerGame_Ctor
    completeness: high
    confidence: high
    note: "Cross-anchored via docs/protocol/tgmessage-routing.md."
  - claim: "`Forward` group-name string is the literal `Forward` at address 0x008D94A0; the string is referenced from inside MultiplayerGame_Ctor and from inside GenericEventForward (FUN_0069FDA0 at the SendToGroup_Iterate call site)."
    address: 0x008D94A0
    function: MultiplayerGame_Ctor
    completeness: high
    confidence: high
  - claim: "Transport layer factory table is 256 entries x 4 bytes (BSS, zero-init at load). 7 slots are populated at runtime by TGWinsockNetwork_Ctor at 0x006B3A00. Populated slots: 0x00 TGDataMessage, 0x01 TGHeaderMessage, 0x02 TGConnectMessage, 0x03 TGConnectAckMessage, 0x04 TGBootMessage, 0x05 TGDisconnectMessage, 0x32 TGMessage. All other 249 slots are NULL and silently drop on receive."
    address: 0x009962D4
    function: TGWinsockNetwork_Ctor
    completeness: high
    confidence: high
    note: "Cross-anchored via docs/protocol/tgmessage-routing.md row #1 and docs/protocol/transport-layer.md."
  - claim: "MAX_MESSAGE_TYPES = 43 (0x2B) is the count of C++-dispatched game opcodes. Stored at DAT_0090B490, SWIG-registered at 0x00654F31. Python message types are defined as `MAX_MESSAGE_TYPES + N` by convention. There is no technical limit on game-opcode byte value other than byte width (0-255)."
    address: 0x0090B490
    function: (Python module init)
    completeness: high
    confidence: high
    note: "Cross-anchored via docs/protocol/python-messages.md."
  - claim: "TGFactory_DeserializeObject is the polymorphic deserializer used by every type-0x32 TGMessage payload, including PythonEvent. It reads a 2-byte class-tag from the wire stream and dispatches to the matching constructor via the TGFactory registry at DAT_0099A578."
    address: 0x006D6200
    function: TGFactory_DeserializeObject
    completeness: high
    confidence: high
    note: "Cross-anchored via docs/protocol/tgmessage-routing.md row #10 (called from MpgameHandlePythonEvent) and docs/protocol/pythonevent-wire-format.md."
  - claim: "TGWinsockNetwork_SendTGMessage has THREE modes selected by the targetID argument: targetID == -1 uses the 4th argument as a `peer+0x1C` lookup key via FUN_006BB9D0; targetID > 0 binary-searches the peer array sorted by `peer+0x18`; targetID == 0 broadcasts to the entire peer array (Clone-per-peer except for the last, which reuses the caller's pMessage)."
    address: 0x006B4C10
    function: TGWinsockNetwork_SendTGMessage
    completeness: 29.07
    confidence: high
    note: "Cross-anchored via docs/protocol/tgmessage-routing.md row #5. The targetID == -1 mode is what python-messages.md OQ4 was asking about; whether stock Python ever uses this mode is OQ2 below."
companions_resolved:
  - docs/protocol/tgmessage-routing.md (primary anchor — all per-handler relay and routing claims)
  - docs/protocol/transport-layer.md (TGMessage envelope, 7 transport-type factories)
  - docs/protocol/python-messages.md (SendTGMessage 3-mode routing, MAX_MESSAGE_TYPES = 43)
  - docs/protocol/game-opcodes.md (per-opcode handler addresses)
  - docs/networking/network-protocol.md (architecture overview)
---

# TGMessage Routing — Clean Room Specification

Behavioral specification of the Bridge Commander TGMessage routing system, described in
terms of observable behavior and the per-handler relay model. Suitable for clean-room
reimplementation in [OpenBC](https://github.com/SandboxServers/OpenBC).

For the reverse engineering analysis with full decompiled code, see
[tgmessage-routing.md](../protocol/tgmessage-routing.md).

> [!IMPORTANT]
> **HIGH PRIORITY for OpenBC implementers.** This doc has 1 material correction (**C1**:
> relay is **per-handler**, NOT transport-level) plus 4 clarifications. The previously
> documented "Automatic Relay (C++ Layer)" model is factually wrong; following it produces
> **duplicate event delivery for opcodes 0x06 / 0x0D / 0x13** — the documented OpenBC
> parity bug. There are **three** routing mechanisms (not two): per-handler relay via the
> `Forward` group, Python `SendTGMessage` / `SendTGMessageToGroup`, and the connect-event
> broadcast (join/leave). The behavioral contracts (silent fallthrough, no opcode
> whitelist, opaque payload during routing) all survive — but the implementation guidance
> changes substantially.
>
> Anchored by [docs/protocol/tgmessage-routing.md](../protocol/tgmessage-routing.md)
> (validated 2026-05-28). See [v5-evidence-header.md](../guides/v5-evidence-header.md) for
> the validation standard.

> [!NOTE]
> **Pass 1 reshape (2026-05-29) — 2 per-opcode policy refinements.** Host-event-emission
> catalog work (memo `host-event-emission-catalog-20260529`) confirms two policy rows
> previously marked **LOCAL-ONLY** are actually wire-active relays:
>
> - **0x1A BeamFire** — stock host DOES relay client-input BeamFire to the `Forward`
>   group. The receive handler is `FUN_0069FBB0`. The host's own beam fires (when the
>   host is a player) also call `FUN_00575480` to broadcast. The host never **originates**
>   BeamFire from simulation — only relays client-input — so the "no server-generated
>   beam" framing is still correct, but the relay path is real. OpenBC parity: **keep the
>   relay**; do not move 0x1A to local-only.
> - **0x29 Explosion** — server emits opcode 0x29 ONLY in catch-up paths
>   (`RequestObjHandler @ 0x006A02A0` and `NewPlayerInGameHandler @ 0x006A1E70`, both
>   calling `FUN_00595C60`). It is NOT emitted per-tick from combat simulation; per-tick
>   damage replicates via 0x1C StateUpdate and `0x06` PythonEvent (`OBJECT_EXPLODING`).
>   The earlier "(S→C only)" tag was correct as far as direction but did not capture the
>   catch-up-only nuance that OpenBC needs to honor.
>
> Pass 1 also confirms `REPAIR_COMPLETED (0x800074)` and `REPAIR_CANNOT_BE_COMPLETED
> (0x800075)` DO emit as wire opcode 0x06 PythonEvent under the host-only
> `DAT_0097FA8A != 0` gate — see [docs/gameplay/repair-system.md](../gameplay/repair-system.md)
> § Host-side wire emission for the byte anchors.
>
> Source: [.claude/agent-memory/game-archaeology-specialist/host-event-emission-catalog-20260529.md](../../.claude/agent-memory/game-archaeology-specialist/host-event-emission-catalog-20260529.md).

---

## Overview

[v5-validated 2026-05-28 via docs/protocol/tgmessage-routing.md]

Bridge Commander multiplayer uses a two-layer message system:

- **Transport layer**: Handles reliable delivery, fragmentation, connection management.
  Messages at this layer have a **transport type** byte.
- **Application layer**: Game-specific messages carried as opaque payloads inside transport
  messages. The first byte of the payload is the **game opcode**.

The server (host) acts as a hub in a star topology. All client-to-client communication
passes through the host.

---

## Transport Layer

### Transport Message Types

[v5-validated 2026-05-28 via docs/protocol/tgmessage-routing.md]

The transport layer supports up to 256 message types (one byte). Seven are defined:

| Type | Purpose |
|------|---------|
| 0x00 | Game data message (carries application-layer payload) |
| 0x01 | Acknowledgement (reliable delivery tracking) |
| 0x02 | Connection request |
| 0x03 | Connection acknowledgement |
| 0x04 | Boot / forced disconnect |
| 0x05 | Graceful disconnect |
| 0x32 | General-purpose data message (with fragment support) |

All other transport types are undefined. Packets with undefined transport types are
silently dropped — no error, no crash.

### Transport Type Registration

[v5-validated 2026-05-28 via docs/protocol/tgmessage-routing.md]

A registration function exists in the SWIG API (`TGNetwork_RegisterMessageType`) that
allows adding custom transport types at runtime. Stock code never calls it. All game
messages use the existing type 0x00 or 0x32 transports.

### Packet Format

Each UDP packet contains:
1. One byte: sender peer ID
2. One byte: count of sub-messages
3. N sub-messages, each starting with a transport type byte

The entire packet (after byte 0) is encrypted with a stream cipher. GameSpy protocol
packets (starting with `\` / 0x5C) are never encrypted.

---

## Application Layer — Game Opcodes

### Opcode Byte

The first byte of a transport message's payload is the **game opcode**. This determines
how the rest of the payload is interpreted.

### Three C++ Dispatchers

[v5-validated 2026-05-28 via docs/protocol/tgmessage-routing.md]

Game opcodes are processed by three independent C++ event handlers, all triggered by the
same network message event:

| Dispatcher | Opcodes Handled |
|------------|----------------|
| MultiplayerWindow | 0x00 (Settings), 0x01 (GameInit), 0x16 (UICollision) |
| MultiplayerGame | 0x02-0x2A (game objects, events, combat, players) |
| NetFile | 0x20-0x27 (checksums, file transfer) |

Each dispatcher reads the first payload byte, checks if it matches a known opcode, and
processes it. **Unknown opcodes are silently ignored** — no error, no rejection, no log.

**Clar1 — How three dispatchers coexist on one event.** All three C++ dispatchers are
attached to the same event, `ET_NETWORK_MESSAGE_EVENT` (`0x60001`). When a TGMessage
arrives, each dispatcher fires in turn, reads the game-opcode byte from the payload, and
runs its case body if the opcode matches one of its own; otherwise it silently falls
through. This silent fallthrough at the dispatcher boundary — combined with the same
behavior on the Python side — is the mechanism that makes mod custom opcodes work. A
clean-room server MUST preserve this multi-dispatcher fan-out on a single event; do not
collapse the three dispatchers into a single switch with an explicit error case for
unrecognized opcodes.

### Python Event Handlers

[v5-validated 2026-05-28 via docs/protocol/tgmessage-routing.md]

Python scripts register handlers on the same network message event. They fire for ALL
incoming messages, read the opcode byte from the payload, and compare against their own
constants. This is how messages with opcodes > 0x2A are processed.

Stock Python handles these opcodes:

| Opcode | Decimal | Name | Handler |
|--------|---------|------|---------|
| 0x2C | 44 | CHAT_MESSAGE | MultiplayerMenus.ProcessMessageHandler |
| 0x2D | 45 | TEAM_CHAT_MESSAGE | MultiplayerMenus.ProcessMessageHandler |
| 0x35 | 53 | MISSION_INIT_MESSAGE | Mission1.ProcessMessageHandler |
| 0x36 | 54 | SCORE_CHANGE_MESSAGE | Mission1.ProcessMessageHandler |
| 0x37 | 55 | SCORE_MESSAGE | Mission1.ProcessMessageHandler |
| 0x38 | 56 | END_GAME_MESSAGE | MissionShared (via EndGame) |
| 0x39 | 57 | RESTART_GAME_MESSAGE | Mission1.ProcessMessageHandler |
| 0x3F | 63 | SCORE_INIT_MESSAGE | Mission2/3/5.ProcessMessageHandler |
| 0x40 | 64 | TEAM_SCORE_MESSAGE | Mission2/3/5.ProcessMessageHandler |
| 0x41 | 65 | TEAM_MESSAGE | Mission2/3/5.ProcessMessageHandler |

### MAX_MESSAGE_TYPES

[v5-validated 2026-05-28 via docs/protocol/tgmessage-routing.md]

The constant `App.MAX_MESSAGE_TYPES` equals **43 (0x2B)**. It represents the count of
C++-dispatched game opcodes. Python message types are defined as offsets from this value:
```
CHAT_MESSAGE         = MAX_MESSAGE_TYPES + 1   = 44
TEAM_CHAT_MESSAGE    = MAX_MESSAGE_TYPES + 2   = 45
MISSION_INIT_MESSAGE = MAX_MESSAGE_TYPES + 10  = 53
```

This is a convention, not a technical limit. Mods can define types at any value 0-255.

---

## Message Routing

### Network Topology: Star (Hub and Spoke)

[v5-validated 2026-05-28 via docs/protocol/tgmessage-routing.md]

```
Client A  <-->  HOST  <-->  Client B
                  ^
Client C  <-------'
```

- Each client maintains a single connection: to the host.
- The host maintains connections to all clients.
- There are no direct client-to-client connections.

### Sending API

[v5-validated 2026-05-28 via docs/protocol/tgmessage-routing.md]

Two primary send functions are available via Python:

1. **SendTGMessage(target_id, message [, optional])**
   - `target_id = 0`: broadcast to all peers
   - `target_id = N` (positive): unicast to specific peer (binary-searched by `peer+0x18`)
   - `target_id = -1`: lookup peer by the 4th argument used as a `peer+0x1C` key
     (binary-walk via the internal lookup helper). Whether stock Python ever invokes this
     mode is **OQ2** below; a clean-room server should still accept the call shape and
     handle the lookup miss by returning the standard not-found error code.

2. **SendTGMessageToGroup(group_name, message)**
   - Sends to all members of a named group.
   - The `"NoMe"` group contains all peers except the local player (the local player is
     the "Me" the group excludes).

### Broadcast Behavior by Role

| Sender | SendTGMessage(0, msg) | SendTGMessageToGroup("NoMe", msg) |
|--------|----------------------|-----------------------------------|
| Client | Goes to host only (client has 1 peer) | Goes to host only |
| Host | Goes to all clients | Goes to all clients (host excluded) |

### Per-Handler Relay (C++ Layer)

[v5-correction 2026-05-28 per docs/protocol/tgmessage-routing.md]

> [!WARNING]
> **This section replaces the pre-v5 "Automatic Relay (C++ Layer)" claim.** The
> pre-v5 doc claimed the C++ transport layer automatically and unconditionally relayed
> every received game message to all other clients, opaque to the opcode, before
> dispatch. **That is not how the binary works.** Relay is per-opcode, performed inside
> the handler body, after the local effect, and gated on the multiplayer + transport-up
> flags. OpenBC implementers MUST NOT implement a single transport-level relay; doing so
> produces duplicate event delivery for the local-only opcodes (0x06, 0x0D, 0x13, others).

**How relay actually happens.** When the host's MultiplayerGame dispatcher routes a game
opcode to its handler, the **handler decides** whether to forward the message. A relaying
handler does so explicitly:

1. **Local effect first.** The handler runs its normal logic (deserialize event, post to
   the local EventManager, etc.).
2. **Clone.** The handler invokes `vtable[6]` (the message Clone slot) so the original can
   be released after local processing.
3. **Forward group lookup.** The handler looks up the `Forward` group by name in the
   network's group table.
4. **Send-to-group fan-out.** The handler calls the network's per-group iterate primitive,
   which clones-and-enqueues a copy on each group member's send queue.

The whole sequence is gated on the multiplayer flag (server is in multiplayer mode) AND
the transport singleton being non-null. In single-player or before networking is up, the
handler runs the local effect and skips the forward.

**Which opcodes relay, which don't.** This is the canonical per-opcode policy table, taken
from [docs/protocol/tgmessage-routing.md](../protocol/tgmessage-routing.md):

| Opcode | Name | Relay policy | Mechanism |
|--------|------|--------------|-----------|
| 0x06 | PythonEvent | **LOCAL-ONLY** | Handler is MpgameHandlePythonEvent — contains no SendToGroup call |
| 0x07 | StartFiring | Forward | GenericEventForward — Clone + SendToGroup("Forward") |
| 0x08 | StopFiring | Forward | GenericEventForward |
| 0x09 | StopFiringAtTarget | Forward | GenericEventForward |
| 0x0A | SubsysStatus | Forward | GenericEventForward |
| 0x0B | AddToRepairList | Forward | GenericEventForward |
| 0x0C | ClientEvent | Forward | GenericEventForward |
| 0x0D | PythonEvent2 | **LOCAL-ONLY** | Same handler as 0x06 — no SendToGroup |
| 0x0E | StartCloak | Forward | GenericEventForward |
| 0x0F | StopCloak | Forward | GenericEventForward |
| 0x10 | StartWarp | Forward | GenericEventForward |
| 0x11 | RepairListPriority | Forward | GenericEventForward |
| 0x12 | SetPhaserLevel | Forward | GenericEventForward |
| 0x13 | HostMsg | **LOCAL-ONLY** | Self-destruct handler — no SendToGroup |
| 0x14 | DestroyObject | **LOCAL-ONLY** | No relay call observed |
| 0x15 | CollisionEffect | **LOCAL-ONLY** | Server processes; emits 0x06 PythonEvent damage instead |
| 0x17 | DeletePlayerUI | **LOCAL-ONLY** | No relay call |
| 0x18 | DeletePlayerAnim | **LOCAL-ONLY** | No relay call observed |
| 0x19 | TorpedoFire | Forward | TorpedoFireHandler — same Clone+SendToGroup pattern |
| 0x1A | BeamFire | **Forward** (relayed) [Pass 1 refinement 2026-05-29] | Receive handler `FUN_0069FBB0` clones to "Forward" group; host never originates from sim, only relays client-input |
| 0x1B | TorpTypeChange | Forward | GenericEventForward |
| 0x1C | StateUpdate | Forward (server-generated) | Server also generates for owned objects |
| 0x29 | Explosion | **Catch-up only (S→C)** [Pass 1 refinement 2026-05-29] | `FUN_00595C60` emits ONLY from `RequestObjHandler @ 0x006A02A0` and `NewPlayerInGameHandler @ 0x006A1E70`; NOT per-tick combat |
| 0x2A | NewPlayerInGame | **LOCAL-ONLY** | Triggers join handshake locally |

**Implementation rule for OpenBC:** Implement relay **inside each handler**, after the
local effect, gated on `is_multiplayer && transport_up`. Do **NOT** implement a single
transport-level relay that fires on receive — that produces duplicate delivery on the 10+
local-only opcodes listed above. The `Forward` group's member list is maintained as "all
peers except the original sender", so a single SendToGroup call produces a clean
"to other clients" fan-out without manual sender-exclusion.

### Python-Level Relay (Selective)

[v5-validated 2026-05-28 via docs/protocol/tgmessage-routing.md]

Some messages are relayed entirely in Python on the host:

- **CHAT_MESSAGE (0x2C)**: Host's Python handler explicitly forwards via
  `SendTGMessageToGroup("NoMe", copy)`. There is **no C++ auto-relay** for chat — the C++
  dispatcher silently drops 0x2C (out-of-range), and the Python handler is the only
  forwarder. The observed 1:2 send/receive ratio on chat traffic is **OQ3** below — the
  pre-v5 doc speculated it was a "double relay" (C++ + Python), but with C1 corrected
  that hypothesis is false. The ratio remains unexplained.

- **TEAM_CHAT_MESSAGE (0x2D)**: Host's Python handler selectively forwards only to
  teammates via individual `SendTGMessage(player_id, copy)` calls, one per teammate. There
  is no C++ auto-relay for 0x2D either.

### Connect-Event Broadcast (Third Routing Mechanism)

[v5-correction 2026-05-28 per docs/protocol/tgmessage-routing.md]

The third routing mechanism is the **connect-event broadcast** path that tells existing
clients about a new peer joining (and a peer leaving). This is distinct from message-level
relay: it does not forward arbitrary game data, only connect/disconnect events.

**Connect path (TGWinsockNetwork_HandleConnect).** When the host receives a transport-type
0x02 connect message from a new peer, the connect handler:

1. Parses the peer ID from the incoming TGConnectMessage.
2. Registers the peer in the network's peer array.
3. Raises event `0x60007` (`ET_NEW_PEER_CONNECTED`) on the local EventManager so server
   logic (gamemode, scoring, scoreboard) can react.
4. Calls the network's broadcast helper to **send the connect event itself** to other
   already-connected clients. This is what makes existing clients see a new player appear
   in their peer list and scoreboard.

The connect-event broadcast is gated on the host flag (`this+0x10E`): only the host
performs this broadcast. Clients receive connect events about other peers from the host,
not from the joining peer directly.

**Disconnect path.** A symmetric disconnect handler performs the same broadcast pattern
for peer-leaving events, again gated on the host flag.

**Why this matters for a clean-room implementation.** A server that implements only
per-handler game-data relay (mechanism #1) and Python script messaging (mechanism #2) but
omits the connect-event broadcast will produce a multiplayer experience where new players
join successfully but existing clients never see them — no scoreboard entry, no player
list update, no team-roster change. The connect-event broadcast is a required mechanism,
not an optional optimization.

---

## Message Filtering

### What Gets Filtered

[v5-validated 2026-05-28 via docs/protocol/tgmessage-routing.md]

The server has **no message type whitelist**. The filtering that does exist is:

1. **Transport type**: Unknown transport types (unregistered factory entries) cause the
   packet to be silently dropped at the transport layer.

2. **Connection state**: Messages from disconnecting peers are not relayed.

3. **Python-level**: Individual Python handlers only process opcodes they recognize,
   ignoring all others.

### What Does NOT Get Filtered

[v5-validated 2026-05-28 via docs/protocol/tgmessage-routing.md]

- **Game opcode value**: No bounds check, no range validation, no whitelist on the
  receive path. The MultiplayerGame dispatcher's `EAX > 0x28` bias-bounds-check on
  opcode is a jump-table guard, not a security filter — out-of-range opcodes silently
  fall through to the cleanup label rather than triggering an error.
- **Payload content**: Never examined during routing fan-out (SendToGroup operates on
  the message handle, not its bytes).
- **Message size**: Subject only to transport-layer length limits (13-bit or 14-bit
  depending on transport type, with fragmentation support for type 0x32).

---

## Mod Custom Message Types

### How Mods Define Custom Types

[v5-validated 2026-05-28 via docs/protocol/tgmessage-routing.md]

Mods write a custom opcode byte as the first byte of a TGMessage payload:

```python
# Example: Kobayashi Maru
KM_CUSTOM_MESSAGE = 205
kStream.WriteChar(chr(KM_CUSTOM_MESSAGE))
# ... write payload data ...
pMessage.SetDataFromStream(kStream)
pNetwork.SendTGMessage(0, pMessage)    # broadcast to all peers
```

### How Custom Types Survive the Server

[v5-validated 2026-05-28 via docs/protocol/tgmessage-routing.md]

1. Client creates a TGMessage with a custom opcode (e.g., 205) in the payload.
2. Transport layer wraps it in a standard type-0x32 transport message.
3. Host receives the transport message and deserializes the payload opaquely (no opcode
   inspection at the transport layer).
4. Host's C++ MultiplayerGame dispatcher reads opcode 205, fails the `EAX > 0x28`
   bias-bounds check, and silently falls through to the cleanup label.
5. Host's Python `ProcessMessageHandler` on `ET_NETWORK_MESSAGE_EVENT` reads opcode 205
   from the payload — the mod's Python handler matches and processes the message.
6. If the host's Python wants to forward the custom message to other clients, it calls
   `SendTGMessageToGroup("NoMe", clone)` — Python-level relay (mechanism #2).

### Available Opcode Ranges

[v5-validated 2026-05-28 via docs/protocol/tgmessage-routing.md]

| Range | Used By |
|-------|---------|
| 0x00-0x2A (0-42) | C++ dispatchers (stock game opcodes) |
| 0x2C-0x2D (44-45) | Stock Python: chat messages |
| 0x2E-0x34 (46-52) | **Unused** (available for mods) |
| 0x35-0x39 (53-57) | Stock Python: scoring/game flow |
| 0x3A-0x3E (58-62) | **Unused** (available for mods) |
| 0x3F-0x41 (63-65) | Stock Python: team mode scoring |
| 0x42-0xFF (66-255) | **Unused** (available for mods) |

Mods can also reuse stock Python opcodes by replacing the Python handlers.

### Known Mod Allocations

| Mod | Types | Decimal |
|-----|-------|---------|
| Stock team modes | MAX_MESSAGE_TYPES + 20-22 | 63-65 |
| Kobayashi Maru | hardcoded | 205, 211-214 |
| BC Remastered | MAX_MESSAGE_TYPES + 10-14 | 53-57 (replaces stock handlers) |

---

## Behavioral Guarantees

For a clean-room reimplementation, the following behaviors must be preserved:

1. [v5-correction 2026-05-28 per docs/protocol/tgmessage-routing.md; Pass 1 refinement 2026-05-29]
   **The host MUST relay each game message according to its per-opcode relay policy**
   (see the Per-Handler Relay table above). Most game opcodes (movement, weapon fire,
   generic event forwards, **including 0x1A BeamFire**) relay via the per-handler
   `Forward`-group helper. PythonEvent opcodes (0x06, 0x0D) and several others (0x13
   HostMsg, 0x14 DestroyObject, 0x15 CollisionEffect, 0x17 DeletePlayerUI, 0x18
   DeletePlayerAnim) are **LOCAL-ONLY** at the handler and **MUST NOT** be relayed by
   the server. **Opcode 0x29 Explosion is server-emitted ONLY during catch-up paths**
   (RequestObj reply, NewPlayerInGame join): clients never send 0x29 and the host never
   emits 0x29 from per-tick combat — per-tick damage replicates via 0x1C StateUpdate and
   0x06 PythonEvent (OBJECT_EXPLODING). Following the pre-v5 transport-level relay model
   causes duplicate event delivery and is the documented OpenBC parity bug.

2. [v5-validated 2026-05-28 via docs/protocol/tgmessage-routing.md] **The game opcode byte
   MUST NOT be examined during the routing fan-out itself.** The SendToGroup primitive
   operates on the message handle and clones-and-enqueues a copy per recipient without
   inspecting the payload. (Decision-to-relay happens earlier, inside the handler; once
   the handler has decided to call SendToGroup, the routing primitive is opcode-agnostic.)

3. [v5-validated 2026-05-28 via docs/protocol/tgmessage-routing.md] **Unknown game
   opcodes MUST be silently ignored** by C++ dispatchers. No error logging, no
   disconnection, no rejection.

4. [v5-validated 2026-05-28 via docs/protocol/tgmessage-routing.md] **Python event
   handlers MUST fire for all incoming messages**, not just those with known opcodes.
   This allows mods to register handlers for custom types.

5. [v5-validated 2026-05-28 via docs/protocol/tgmessage-routing.md] **The "NoMe" and
   "Forward" groups MUST be routing-only** — they select recipients, they do not filter
   or validate message content.

6. [v5-validated 2026-05-28 via docs/protocol/tgmessage-routing.md] **SendTGMessage(0,
   msg) from a client MUST reach the host**, which then either relays per-handler (for
   game opcodes whose handler chooses to relay) or forwards via Python (for opcodes the
   Python handler chooses to forward). This is the standard mod broadcasting pattern.

7. [v5-validated 2026-05-28 via docs/protocol/tgmessage-routing.md] **No maximum message
   type enforcement beyond byte width** (0-255).

8. [v5-correction 2026-05-28 per docs/protocol/tgmessage-routing.md] **The host MUST
   broadcast connect and disconnect events to existing clients** so other peers learn
   about joins and leaves. This is mechanism #3 (connect-event broadcast) and is distinct
   from per-handler game-data relay; omitting it produces a server where players join but
   nobody sees them.

---

## Implementation Considerations for Dedicated Server

A headless dedicated server reimplementation must:

1. [v5-correction 2026-05-28 per docs/protocol/tgmessage-routing.md; Pass 1 refinement 2026-05-29]
   **Implement per-opcode relay inside each handler, after the local effect.** Do NOT
   implement a single transport-level relay; that produces duplicate delivery on the
   local-only opcodes (0x06 PythonEvent, 0x0D PythonEvent2, 0x13 HostMsg, 0x14, 0x15,
   0x17, 0x18). **Opcode 0x1A BeamFire IS relayed** via the Forward group at handler
   `FUN_0069FBB0` — do not move it to the local-only set. **Opcode 0x29 Explosion is
   emitted only during catch-up paths** (RequestObj, NewPlayerInGame); implement as a
   replay-on-join emitter, not a per-tick relay. The Forward-group fan-out is the
   canonical mechanism for relaying handlers; replicate the
   `Clone -> SendToGroup("Forward")` sequence per handler that should forward.

2. [v5-correction 2026-05-28 per docs/protocol/tgmessage-routing.md] **Create the
   "NoMe" and "Forward" groups during server-side multiplayer initialization**, NOT in
   Python script init. The C++ MultiplayerGame ctor is what creates the groups in stock
   BC; a clean-room server's equivalent server-init path must register both groups
   against the network's group table before any handler can call SendToGroup or before
   any Python script can call SendTGMessageToGroup. Python only **uses** these groups; it
   does not create them.

3. [v5-validated 2026-05-28 via docs/protocol/tgmessage-routing.md] **Broadcast connect
   and disconnect events to existing clients on the host side.** When a new peer's
   transport-type-0x02 connect message arrives, register the peer, post the
   `ET_NEW_PEER_CONNECTED` event locally, AND send a copy of the connect event to all
   other already-connected peers. Apply the symmetric pattern for disconnect.

4. [v5-validated 2026-05-28 via docs/protocol/tgmessage-routing.md] **Not add filtering
   based on game opcode**. Even if the server doesn't understand a custom mod message
   type, the C++ dispatcher must silently fall through and the Python layer must still
   receive the event.

5. [v5-validated 2026-05-28 via docs/protocol/tgmessage-routing.md] **Handle Python-level
   messages** (chat, scoring) if the server needs to participate in game logic (e.g.,
   computing scores, managing game state). Chat relay specifically MUST happen at the
   Python layer; there is no C++ auto-relay for 0x2C / 0x2D.

6. [v5-validated 2026-05-28 via docs/protocol/tgmessage-routing.md] **Preserve the star
   topology** — clients expect to send only to the host, and expect the host to relay (or
   not) to all other clients per the policy table.

7. [v5-validated 2026-05-28 via docs/protocol/tgmessage-routing.md] **Not crash or
   disconnect clients** for sending unrecognized message types. Silent ignore is the
   correct behavior at every layer.

---

## Open Questions

1. **OQ1 — `peer+0x1C` semantics.** SendTGMessage's `targetID == -1` mode uses
   `peer+0x1C` as the lookup key. The field is plausibly a connection-token / session-ID
   set during the connect handshake, but the exact semantics aren't anchored yet.
   Carried from [docs/protocol/tgmessage-routing.md](../protocol/tgmessage-routing.md)
   OQ1. A clean-room server should treat `peer+0x1C` as an opaque token assigned at
   connect time and used for one-off targetID-style lookups; the field's wire-level
   semantics remain open.

2. **OQ2 — Does stock Python ever call SendTGMessage with `targetID == -1`?** Whether
   any stock or mod script invokes the third mode is not determined. A clean-room server
   must accept the call shape regardless and return the standard not-found error on
   lookup miss. Carried from [docs/protocol/tgmessage-routing.md](../protocol/tgmessage-routing.md)
   OQ2.

3. **OQ3 — Chat 1:2 send/receive ratio.** The 2026-02-24 audit observed
   `0x2C CHAT_MESSAGE` at 5 client→server, 10 server→client, despite `NoMe` excluding the
   host (so each chat should reach one OTHER client per send, producing a 1:1 ratio in a
   2-player session). The pre-v5 doc speculated this was a double-delivery from C++
   auto-relay + Python NoMe; with C1 corrected (no C++ auto-relay for 0x2C), that
   hypothesis is **false** and the 1:2 ratio is genuinely unexplained. Carried from
   [docs/protocol/tgmessage-routing.md](../protocol/tgmessage-routing.md) OQ3. Worth a
   dedicated single-message-per-test chat trace to disambiguate.

---

## Related Documentation

- [docs/protocol/tgmessage-routing.md](../protocol/tgmessage-routing.md) — the RE-side
  anchor with full decompiled code, addresses, and trace ratios. This clean-room doc
  inherits its v5 status from there.
- [docs/protocol/transport-layer.md](../protocol/transport-layer.md) — TGMessage envelope,
  7 transport-type factories.
- [docs/protocol/python-messages.md](../protocol/python-messages.md) — SendTGMessage
  3-mode routing, MAX_MESSAGE_TYPES, Python message-type allocations.
- [docs/protocol/game-opcodes.md](../protocol/game-opcodes.md) — per-opcode handler
  addresses.
- [docs/networking/network-protocol.md](network-protocol.md) — broader networking
  architecture overview.
