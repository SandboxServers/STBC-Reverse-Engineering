> [docs](../README.md) / [protocol](README.md) / transport-layer.md

---
title: Transport Layer (UDP packet framing, TGMessage envelope, cipher, fragmentation)
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
  - docs/protocol/wire-format-spec.md
  - docs/protocol/stream-primitives.md
  - docs/protocol/checksum-opcodes.md
  - docs/networking/network-protocol.md
  - docs/networking/alby-rules-cipher-analysis.md
  - docs/networking/fragmented-ack-bug.md
  - docs/networking/ack-outbox-deadlock.md
  - docs/engine/decompiled-functions.md
  - docs/protocol/v5-validation-status.md
evidence:
  - claim: "Raw UDP packet structure: byte 0 = peer_id, byte 1 = msg_count, messages from byte 2; factory dispatch indexed by type * 4 at DAT_009962d4"
    address: 0x006b5c90
    function: TGWinsockNetwork_ProcessIncomingPackets
    completeness: high
    confidence: high
    note: "ProcessIncomingPackets reads peer_id as signed char from buf[0]; loops cVar4 = buf[1] times from buf+2; dispatches via DAT_009962d4[*buf * 4]"
  - claim: "Transport factory table at DAT_009962d4 has 256 type slots; 7 populated (types 0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x32)"
    address: 0x009962d4
    function: DAT_009962d4
    completeness: high
    confidence: high
    note: "Each of 7 registration helpers (FUN_006b8290, FUN_006bc5a0, FUN_006bd110, FUN_006bdc30, FUN_006bac60, FUN_006be720, FUN_006bf2d0) writes its factory function pointer to slot (type * 4) in this table"
  - claim: "Type 0x00 (TGDataMessage) registered via FUN_006bc5a0, ctor FUN_006bc5b0 (TGDataMessage_Ctor), vtable 0x0089598c, factory FUN_006bc6a0"
    address: 0x006bc5b0
    function: TGDataMessage_Ctor
    completeness: high
    confidence: high
  - claim: "Type 0x01 (TGHeaderMessage / ACK) registered via FUN_006bd110, ctor FUN_006bd120 (TGHeaderMessage_Ctor), size 0x44, factory FUN_006bd1f0, serializer FUN_006bd190 (TGHeaderMessage_Serialize)"
    address: 0x006bd120
    function: TGHeaderMessage_Ctor
    completeness: high
    confidence: high
    note: "Plate comment installed at TGHeaderMessage_Serialize this session"
  - claim: "Type 0x02 (TGConnectMessage) registered via FUN_006bdc30, ctor FUN_006bdc40 (TGConnectMessage_Ctor); does NOT set +0x3A=1 (unreliable by default)"
    address: 0x006bdc40
    function: TGConnectMessage_Ctor
    completeness: high
    confidence: high
  - claim: "Type 0x03 (TGConnectAckMessage) registered via FUN_006be720, ctor FUN_006be730 (TGConnectAckMessage_Ctor); sets reliable + ordered"
    address: 0x006be730
    function: TGConnectAckMessage_Ctor
    completeness: high
    confidence: high
  - claim: "Type 0x04 (TGBootMessage) registered via FUN_006bac60, ctor FUN_006bac70 (TGBootMessage_Ctor); clears the is_below_0x32 flag at +0x40"
    address: 0x006bac70
    function: TGBootMessage_Ctor
    completeness: high
    confidence: high
  - claim: "Type 0x05 (TGDisconnectMessage) registered via FUN_006bf2d0, ctor FUN_006bf2e0 (TGDisconnectMessage_Ctor); sets reliable + ordered"
    address: 0x006bf2e0
    function: TGDisconnectMessage_Ctor
    completeness: high
    confidence: high
  - claim: "Type 0x32 (TGMessage base — general game payload) registered via FUN_006b8290, ctor FUN_006b82a0 (TGMessage_Ctor), size 0x40, vtable 0x008958d0, factory FUN_006b83f0 (TGMessage_Factory_Type32)"
    address: 0x006b82a0
    function: TGMessage_Ctor
    completeness: high
    confidence: high
    note: "Pool allocation FUN_00717b70(0x40); SWIG `new_TGMessage` at 0x005e12e0 calls this ctor — confirms class identity"
  - claim: "TGMessage object layout: +0x14 seq, +0x38 total_fragments (fragment 0 only), +0x39 fragment_index, +0x3A reliable, +0x3B ordered, +0x3C is_fragment, +0x40 below32 (is_type_below_0x32)"
    address: 0x006b82a0
    function: TGMessage_Ctor
    completeness: high
    confidence: high
    note: "Each offset verified via cross-reference: serializer (0x006b8340), reassembler (0x006b6cc0), ACK producer (0x006b61e0), ACK consumer (0x006b64d0), TGHeaderMessage_Serialize (0x006bd190)"
  - claim: "TGMessage base vtable at 0x008958d0 has 8 slots: GetType (returns 0x32) 0x006b9430, dtor 0x006b82f0, WriteToBuffer 0x006b8340, slot[3] 0x006b9440 (returns 0), slot[4] 0x006b9450, GetSize 0x006b8640, Clone 0x006b8610, FragmentMessage 0x006b8720"
    address: 0x008958d0
    function: TGMessage_vtable
    completeness: high
    confidence: high
    note: "Vtable bytes read directly from 0x008958d0; slots 3 and 4 remain unidentified (open question)"
  - claim: "Type 0x32 wire format: [type:1][flags_len:LE u16][optional seq:2 if reliable][optional frag_idx:1, total_frags:1 if frag_idx==0 if fragmented][payload]; flags_len bit 13 = is_fragment, bit 14 = ordered, bit 15 = reliable, bits 12-0 = total length"
    address: 0x006b8340
    function: TGMessage_Serialize
    completeness: high
    confidence: high
    note: "Symmetric reader at TGMessage_Factory_Type32 (0x006b83f0)"
  - claim: "Type 0x01 ACK wire format: [type=0x01:1][seq:LE u16][flags:1][optional frag_idx:1 if is_fragment]; flags bit 0 = is_fragment, bit 1 = is_below_0x32. Total 4 or 5 bytes"
    address: 0x006bd190
    function: TGHeaderMessage_Serialize
    completeness: high
    confidence: high
  - claim: "Fragment reassembly uses a 256-entry index array; fragment 0 carries total_frags at +0x38; all-fragments-present check via fragment 0's count byte"
    address: 0x006b6cc0
    function: TGMessage_ReassembleFragments
    completeness: high
    confidence: high
    note: "EnqueueReceived at 0x006b6ad0 dispatches into the reassembler when msg+0x3C (is_fragment) is set"
  - claim: "MTU is 0x400 = 1024 bytes; set in TGWinsockNetwork_Ctor at network+0xAC and the matching pack buffer at network+0x2B"
    address: 0x006b3a00
    function: TGWinsockNetwork_Ctor
    completeness: high
    confidence: high
    note: "ReceivePacket allocates network+0xAC for recv buffer; SendOutgoingPackets uses network+0x2B for pack buffer"
  - claim: "Two per-peer reliable sequence counters: peer+0x26 (16-bit, for transport types < 0x32) and peer+0x2A (16-bit, for transport types >= 0x32)"
    address: 0x006b5080
    function: TGWinsockNetwork_QueueMessageForPeer
    completeness: high
    confidence: high
    note: "CORRECTION (was peer+0x98 / peer+0xA8): direct decompile of QueueMessageForPeer shows +0x26 and +0x2A as the seq-counter slots; receive-side window check uses +0x24 and +0x28. Prior +0xA8 likely came from confusing network+0xA8 = 0x8000 constant set by the ctor"
  - claim: "Below32 ACK semantics: SET in HandleReliableReceived as bool(transport_type < 0x32); READ in HandleACK to match the ACK with the right outbox; WIRE-encoded in TGHeaderMessage_Serialize as flags bit 1"
    address: 0x006b61e0
    function: TGWinsockNetwork_HandleReliableReceived
    completeness: high
    confidence: high
    note: "Three-site agreement: SET 0x006b61e0 `*(bool *)(iVar6+0x40) = iVar5 < 0x32`; READ 0x006b64d0; WIRE 0x006bd190 `if (this+0x40 != 0) flags |= 2`"
  - claim: "AlbyRules cipher: key string 'AlbyRules!' at 0x0095abb4 copied into 0x58-byte cipher state by AlbyRulesCipher_InitKey; vtable at 0x008958c0 (slot[1] Encrypt, slot[2] Decrypt)"
    address: 0x006c2280
    function: AlbyRulesCipher_InitKey
    completeness: high
    confidence: high
    note: "Plate comment installed this session"
  - claim: "Cipher re-keys per packet (no streaming state across packets); SendPacket and ReceivePacket each call AlbyRulesCipher_InitKey before Encrypt/Decrypt. Property makes the cipher robust to UDP packet loss"
    address: 0x006c2490
    function: AlbyRulesCipher_Encrypt
    completeness: high
    confidence: high
    note: "Decrypt at 0x006c2520; both call InitKey on every packet (no continuation state)"
  - claim: "Cipher operates on buf+1 with length-1: byte 0 (peer_id) stays plaintext on the wire. GameSpy packets (first byte = '\\\\' / 0x5C) skip the cipher entirely (uncached)"
    address: 0x006b9706
    function: TGWinsockNetwork_ReceivePacket
    completeness: high
    confidence: high
    note: "Branch `if (*buf != '\\\\')` at 0x006b9706 routes GameSpy heartbeats around the cipher; SendPacket has the symmetric branch at 0x006b98e0"
  - claim: "SendPacket has a self-send loop-back path: if dest_addr == network+0x1C (own address), the packet is queued at network+0x33C / +0x340 with toggle at network+0x344 — never hits the OS UDP stack"
    address: 0x006b9870
    function: TGWinsockNetwork_SendPacket
    completeness: high
    confidence: high
    note: "Function had no direct CALL xrefs (it's vtable[27] of TGWinsockNetwork base) and was CREATED this session via mcp__ghidra__create_function; plate comment installed. Self-send branch at 0x006b9870 + 0x?? matches `if (param_2 == *(int *)(param_1+0x1c))`"
  - claim: "Three C++ message dispatchers: NetFile at 0x006a3cd0 (opcodes 0x20-0x27), MpgameHandleMessage at 0x0069f2a0 (opcodes 0x02-0x2A), MultiplayerWindow at 0x00504c10 (opcodes 0x00/0x01/0x16); MultiplayerWindow gates on this+0xB0 != 0"
    address: 0x0069f2a0
    function: MpgameHandleMessage
    completeness: 69.84
    confidence: high
    note: "Engine-inherited anchor; verified in wire-format-spec.md v5 row §6.1"
  - claim: "NetFile dispatcher opcodes are NON-CONTIGUOUS: 0x20, 0x21, 0x22, 0x23, 0x25, 0x27 (0x24 and 0x26 have no handler)"
    address: 0x006a3cd0
    function: FUN_006a3cd0
    completeness: 0.60
    confidence: high
    note: "CORRECTION (was '0x20-0x27 contiguous'): switch-case decompile of FUN_006a3cd0 shows only 6 cases. See docs/protocol/checksum-opcodes.md for canonical opcode catalog"
  - claim: "Connection state machine: states 2 (HOSTING), 3 (JOINING), 4 (IDLE/READY) directly observed. State 1 may exist (open question — likely a sub-state during connect handshake in 006B8B30 family)"
    address: 0x006b3ec0
    function: TGWinsockNetwork_HostOrJoin
    completeness: high
    confidence: medium
    note: "Initial state = 4 (set in ctor `param_1[5] = 4`); HostOrJoin transitions 4->2 (host path with error_post 0x60002) or 4->3 (join path). State 1 not observed in HostOrJoin"
  - claim: "FragmentMessage at FUN_006b8720 (vtable[7]) splits messages larger than MTU into clones with sequential +0x39 fragment_index; receiver expects fragment 0 to carry +0x38 total_frags"
    address: 0x006b8720
    function: TGBufferStream_Fragment
    completeness: medium
    confidence: medium
    note: "Sender-side placement of total_fragments on whichever clone has frag_idx==0 is ambiguous in the cleaned decompile (the linked-list manipulation after the loop writes +0x38 onto what appears to be the LAST inserted message, not Fragment 0). Receiver side is unambiguous. Open question: needs emulation to settle. Working packet traces confirm reassembly succeeds, so the sender does the right thing on the wire"
companions_changelog:
  - "2026-05-28: AlbyRules cipher fully anchored (InitKey 0x006c2280, Encrypt 0x006c2490, Decrypt 0x006c2520, vtable 0x008958c0, 0x58-byte state, re-key per packet); 4 corrections (sequence counter offsets, NetFile non-contiguous, Appendix A re-attribution to stream-primitives, TGMessage naming cascade); 2 functions newly created in Ghidra (SendPacket, ReceivePacket); 7 v5 plate comments installed"
supersedes:
  - 2026-02-10
---

# Transport Layer

> [!NOTE]
> This doc is `status: partial`. The packet structure, 7 transport types, TGMessage envelope
> layout (vtable `0x008958d0`, ctor `TGMessage_Ctor` at `0x006b82a0`, size `0x40`),
> TGHeaderMessage ACK subclass, fragment reassembly (256-entry index, MTU `1024` bytes),
> AlbyRules cipher (`AlbyRulesCipher_InitKey` `0x006c2280`, `AlbyRulesCipher_Encrypt`
> `0x006c2490`, `AlbyRulesCipher_Decrypt` `0x006c2520`, re-key per packet), connection-state
> transitions, self-send loop-back path, and the below32 ACK semantics are all v5-validated
> against the current Ghidra import (2026-05-28). **Four corrections:** sequence counter
> offsets are at `peer+0x26` / `peer+0x2A` (NOT `+0x98` / `+0xA8`); NetFile dispatcher
> opcodes are non-contiguous (`0x20`, `0x21`, `0x22`, `0x23`, `0x25`, `0x27`); the prior
> Appendix A "TGBufferStream Layout" described the SWIG primitive-cursor class — it is now
> retired in favour of a cross-link to
> [stream-primitives.md](stream-primitives.md); the wire-envelope class is
> **TGMessage** (cascading rename from the prior "wire-container class" placeholder).
>
> Two open questions remain: `FragmentMessage` total_frags placement (medium confidence —
> the linked-list manipulation in the cleaned decompile is ambiguous, but the receiver-side
> read of fragment 0's `+0x38` is unambiguous); connection state 1 unverified.

This is the foundation doc for everything on the UDP wire. Produced by systematic
decompilation of STBC.exe (base `0x00400000`, ~6.1 MB) using Ghidra and validated against
stock dedicated-server packet traces (30,000+ packets).

The transport runs at MTU `1024` bytes, set in `TGWinsockNetwork_Ctor` at `0x006b3a00`
(network+0xAC for the receive buffer, network+0x2B for the pack buffer). Anything larger is
fragmented; anything smaller travels in a single UDP datagram.

## Encryption

All UDP game packets pass through the **AlbyRules! stream cipher**. Send-side and receive-side
re-key the cipher per packet — there is no streaming state carried across packets. That's
the property that makes the cipher robust to UDP packet loss and reordering: the cipher
cannot desync between host and client because every packet's transform is independent.

### Cipher object [v5-validated 2026-05-28]

The cipher lives at `TGWinsockNetwork+0xF0` (a `0x58`-byte state allocated in the
TGWinsockNetwork ctor). Its vtable at `0x008958c0` exposes:

| Slot | Offset | Function | Name |
|------|--------|----------|------|
| 0 | +0x00 | `0x006b8220` | Destructor |
| 1 | +0x04 | `0x006c2490` | `AlbyRulesCipher_Encrypt` |
| 2 | +0x08 | `0x006c2520` | `AlbyRulesCipher_Decrypt` |

A trailing float at offset `+0x0C` of the vtable (`0x41700000` = 15.0) is the per-step
constant the LFSR-like inner step (`0x006c22f0`) uses.

**Key initialization (`AlbyRulesCipher_InitKey` at `0x006c2280`):** copies the literal
`"AlbyRules!"` string at `0x0095abb4` into the cipher state on every packet. Both
`AlbyRulesCipher_Encrypt` (`0x006c2490`) and `AlbyRulesCipher_Decrypt` (`0x006c2520`) call
`InitKey` before they run — no streaming state survives between packets.

### Cipher scope [v5-validated 2026-05-28]

Byte 0 of every packet stays **plaintext** on the wire. The cipher is applied to `buf+1`
with `len-1` in both directions:

- **Send path:** `TGWinsockNetwork_SendPacket` at `0x006b9870` calls `Encrypt(buf+1, len-1)`
  just before pushing the datagram onto the wire.
- **Receive path:** `TGWinsockNetwork_ReceivePacket` at `0x006b95f0` calls
  `Decrypt(buf+1, len-1)` immediately after `recvfrom`.

Byte 0 is the peer_id — the receiver uses it for peer demux *before* dispatching to a
factory, so it has to stay readable. (The first PRNG XOR byte happens to be `0x00` too,
so the plaintext byte would survive even if the cipher covered it, but the engine explicitly
skips it.)

### GameSpy bypass [v5-validated 2026-05-28]

Packets whose byte 0 is `\` (`0x5C`) bypass the cipher entirely — these are GameSpy
heartbeats and query-port traffic, which run on a separate text-based protocol. The branch
sits in `ReceivePacket` at `0x006b9706` (`if (*buf != '\\') decrypt...`); `SendPacket` has
the symmetric branch at `0x006b98e0`.

For full cipher algorithm details, see
[docs/networking/alby-rules-cipher-analysis.md](../networking/alby-rules-cipher-analysis.md)
(scheduled for its own v5 validation pass to absorb these anchors).

## Raw UDP Packet

After the AlbyRules cipher is removed, the decrypted payload has this structure
[v5-validated 2026-05-28]:

```
Offset  Size  Field
------  ----  -----
0       1     peer_id       (0x01=server, 0x02=first client, 0xFF=unassigned/init)
1       1     msg_count     (number of transport messages in this packet, 0x00-0xFF)
2+      var   messages      (sequence of transport messages, each self-describing)
```

The receive processor `TGWinsockNetwork_ProcessIncomingPackets` (`0x006b5c90`) reads
`peer_id` from byte 0 (as a signed char), `msg_count` from byte 1, then loops `msg_count`
times reading a type byte from each message and dispatching through the factory table at
`DAT_009962d4` (indexed by `type * 4`).

## Transport Message Types

The factory table at `DAT_009962d4` is 256 type slots wide. Seven are populated; the
remaining 249 are NULL and a `type` byte that lands in an empty slot drops the message
[v5-validated 2026-05-28]:

| Type | Class | Registration | Constructor | Vtable | Factory |
|------|-------|--------------|-------------|--------|---------|
| 0x00 | `TGDataMessage` | `FUN_006bc5a0` | `TGDataMessage_Ctor` `0x006bc5b0` | `0x0089598c` | `FUN_006bc6a0` |
| 0x01 | `TGHeaderMessage` (ACK) | `FUN_006bd110` | `TGHeaderMessage_Ctor` `0x006bd120` | `0x008959ac` | `FUN_006bd1f0` |
| 0x02 | `TGConnectMessage` | `FUN_006bdc30` | `TGConnectMessage_Ctor` `0x006bdc40` | `0x008959cc` | `FUN_006bdd10` |
| 0x03 | `TGConnectAckMessage` | `FUN_006be720` | `TGConnectAckMessage_Ctor` `0x006be730` | `0x008959ec` | `FUN_006be860` |
| 0x04 | `TGBootMessage` | `FUN_006bac60` | `TGBootMessage_Ctor` `0x006bac70` | `0x0089596c` | `FUN_006badb0` |
| 0x05 | `TGDisconnectMessage` | `FUN_006bf2d0` | `TGDisconnectMessage_Ctor` `0x006bf2e0` | `0x00895a0c` | `FUN_006bf410` |
| 0x32 | `TGMessage` (base) | `FUN_006b8290` | `TGMessage_Ctor` `0x006b82a0` | `0x008958d0` | `TGMessage_Factory_Type32` `0x006b83f0` |

**Type `0x32` is the general-purpose data message** used for ALL game-layer payloads. Types
`0x00`-`0x05` are connection management — they have their own sequence-counter slot
(`peer+0x26`) and dedicated wire formats. The separation matters because:

- Type `0x32` has fragment support and uses a 13-bit length field, while type `0x00` has no
  fragment support and uses a 14-bit length field.
- The two reliable sequence counters are split by category (see "Reliable Delivery" below).

All six TGMessage subclass ctors set reliable+ordered EXCEPT `TGConnectMessage_Ctor`, which
deliberately leaves `+0x3A = 0` (unreliable by default — the connect handshake handles its
own retries). `TGBootMessage_Ctor` additionally clears `+0x40` (the `is_below_0x32` flag).

## Wire Formats

### Type 0x32 — Data Message (game payloads) [v5-validated 2026-05-28]

```
Offset  Size  Field
------  ----  -----
0       1     type          Always 0x32
1       2     flags_len     LE uint16 (see below)
[if reliable:]
3       2     seq_num       LE uint16 reliable sequence number
[if fragmented:]
+0      1     frag_idx      Fragment index (0-based)
[if frag_idx == 0:]
+1      1     total_frags   Total number of fragments
[end if]
+N      var   payload       Game opcode + data

flags_len bit layout (LE uint16):
  bits 12-0 (0x1FFF): total message size (includes the 0x32 type byte)
  bit 13    (0x2000): is_fragment -- fragment metadata follows seq_num
  bit 14    (0x4000): ordered (priority delivery)
  bit 15    (0x8000): reliable (ACK required, has seq_num)
```

**Serializer:** `TGMessage_Serialize` at `0x006b8340` (vtable slot [2])
**Deserializer:** `TGMessage_Factory_Type32` at `0x006b83f0`

When viewed as two separate bytes (as the packet decoder reads them):
- `flags_len_lo` = low byte: bits 7-0 of the 13-bit length
- `flags_len_hi` = high byte: bits 12-8 of length (low 5 bits) + flags (high 3 bits)

Common `flags_len_hi` values observed in traces:

| `flags_len_hi` | Meaning |
|----------------|---------|
| `0x80` | reliable, no fragment, length bits 12-8 = 0 |
| `0x81` | reliable, no fragment, length bit 8 set |
| `0xA0` | reliable + fragment, length bits 12-8 = 0 |
| `0xA1` | reliable + fragment, length bit 8 set |
| `0x00` | unreliable, no fragment |

### Type 0x00 — Control Data Message (small, no fragment support) [v5-validated 2026-05-28]

```
Offset  Size  Field
------  ----  -----
0       1     type          Always 0x00
1       2     flags_len     LE uint16 (see below)
[if reliable:]
3       2     seq_num       LE uint16 reliable sequence number
+N      var   payload       Data

flags_len bit layout (LE uint16):
  bits 13-0 (0x3FFF): total message size (14-bit, max 16383)
  bit 14    (0x4000): ordered
  bit 15    (0x8000): reliable
  (NO fragment bit -- type 0x00 does not support fragmentation)
```

**Serializer:** `FUN_006bc610` (TGDataMessage::WriteToBuffer)
**Deserializer:** `FUN_006bc6a0` (type 0x00 factory)

### Type 0x01 — ACK (TGHeaderMessage) [v5-validated 2026-05-28]

```
Offset  Size  Field
------  ----  -----
0       1     type          Always 0x01
1       2     seq_num       LE uint16 sequence number being ACKed
3       1     flags         bit 0: is_fragment, bit 1: is_below_0x32 (msg type category)
[if is_fragment:]
4       1     frag_idx      Fragment index of the message being ACKed
```

**Serializer:** `TGHeaderMessage_Serialize` at `0x006bd190`
**Deserializer:** `FUN_006bd1f0` (type 0x01 factory)
**Total size:** 4 bytes (non-fragment ACK) or 5 bytes (fragment ACK)

The `is_below_0x32` flag (bit 1) tells the receiver which outbox to look in — there are two
reliable outboxes per peer (one for `< 0x32` connection-management messages, one for
`>= 0x32` game messages) and the flag matches the ACK with the right one.

### Types 0x02-0x05 — Connection Management

These use derived classes with their own serialization. Wire format is:
`[type:1][type-specific data...]`. See the per-class ctors (table above) for details.

## Fragment Reassembly [v5-validated 2026-05-28]

When a message is too large for a single UDP packet, `FragmentMessage` (vtable[7] of
TGMessage at `0x006b8720`) splits it into multiple type `0x32` messages:

1. If the message fits in `max_size`, returns a 1-element array (no fragmentation).
2. If too large, forces `reliable = 1` on the message.
3. Creates clones via vtable[6] (`Clone` at `0x006b8610`), each with:
   - `+0x3C = 1` (is_fragment)
   - `+0x39 = fragment_index` (0, 1, 2, ...)
4. Fragment 0 gets `+0x38 = total_fragment_count` (placed on whichever clone has
   `frag_idx == 0`; sender-side linked-list manipulation is ambiguous in the decompile — see
   Open Questions).
5. Each fragment carries a slice of the original payload.

On the receive side, `TGWinsockNetwork_EnqueueReceived` at `0x006b6ad0` checks `msg+0x3C`
(is_fragment). If set, it calls `TGMessage_ReassembleFragments` at `0x006b6cc0`:

1. Allocates a 256-element array indexed by `fragment_index`.
2. Scans the pending message queue for fragments with matching `seq_num`.
3. Places each fragment into the array by its `+0x39` index.
4. Checks if fragment 0 exists (it carries `total_frags` at `+0x38`).
5. If ALL fragments are collected: allocates a combined buffer, copies each fragment's data
   in order.
6. Replaces the message buffer with the reassembled data via `FUN_006b89a0`.
7. Clears the is_fragment flag (`+0x3C = 0`).
8. Removes consumed fragments from the queue.

The fragment-encoding details (the `0xA1` / `0xA0` flag pattern, length-bit-8 vs fragment
bit) are covered under "Type 0x32" above; the historical note on what `0x01` does NOT mean
is preserved at the bottom of this section.

### Example: Checksum Response (3 fragments) [v5-validated 2026-05-28]

```
Fragment 0: flags_hi=0xA1 -> reliable(0x80) + fragment(0x20) + len_bit8(0x01)
            seq=N, frag_idx=0, total_frags=3, inner_opcode=0x21(ChecksumResp)

Fragment 1: flags_hi=0xA1 -> reliable(0x80) + fragment(0x20) + len_bit8(0x01)
            seq=N, frag_idx=1, continuation payload data

Fragment 2: flags_hi=0xA0 -> reliable(0x80) + fragment(0x20) + len_bit8(0x00)
            seq=N, frag_idx=2, continuation payload data (last fragment)
```

The receiver (`TGMessage_ReassembleFragments` at `0x006b6cc0`) collects all fragments
matching `seq=N` into a 256-entry array indexed by `frag_idx`. Once fragment 0 (with
`total_frags`) and all subsequent fragments are present, it concatenates them in order and
delivers the reassembled message.

### Historical note on flag `0x01`

Previous documentation incorrectly identified `flags_hi & 0x01` as a "more fragments" flag.
In reality, this is bit 8 of the 13-bit total length field. The difference between `0xA1`
and `0xA0` is simply whether the message length has bit 8 set (i.e., total length >= 256 vs
< 256). Fragment detection uses the fragment flag (bit 5 / `0x20`) only.

## Reliable Delivery

When `TGWinsockNetwork_ProcessIncomingPackets` (`0x006b5c90`) processes a received message
with `reliable = 1` (`+0x3A`), it calls `TGWinsockNetwork_HandleReliableReceived`
(`0x006b61e0`) which creates a `TGHeaderMessage` (type `0x01`) ACK. The ACK carries the
sequence number and, if the message was a fragment, the fragment index.

### Two reliable sequence counters per peer [v5-validated 2026-05-28]

> [!IMPORTANT]
> **CORRECTION (was `peer+0x98` / `peer+0xA8`).** Direct decompile of
> `TGWinsockNetwork_QueueMessageForPeer` (`0x006b5080`) shows:
>
> - **`peer + 0x26`** (LE u16): for types `< 0x32` (connection management)
> - **`peer + 0x2A`** (LE u16): for types `>= 0x32` (game data)
>
> Receive-side window check uses `peer + 0x24` and `peer + 0x28`. The prior `+0xA8` claim
> likely came from confusing `network + 0xA8 = 0x8000` (a constant set in
> `TGWinsockNetwork_Ctor`, probably a seq-window threshold or max-seq, but NOT a per-peer
> seq counter).

### `is_below_0x32` flag — three-site agreement

The receiver needs to match each ACK with the right outbox category. The flag is set,
read, and put on the wire at three coordinated sites:

| Site | Address | Function | What it does |
|------|---------|----------|--------------|
| **SET** | `0x006b61e0` | `TGWinsockNetwork_HandleReliableReceived` | `*(bool *)(iVar6+0x40) = iVar5 < 0x32` |
| **READ** | `0x006b64d0` | `TGWinsockNetwork_HandleACK` | `if ((bool)cVar1 != iVar3 < 0x32) goto next` |
| **WIRE** | `0x006bd190` | `TGHeaderMessage_Serialize` | `if (this+0x40 != 0) flags |= 2` |

So the `is_below_0x32` bit on the wire is the same bool the receiver wrote into the
header-message object when it first observed the reliable receive — round-tripped through
the wire, and used by the host to look up the right outbox slot.

## TGMessage Object Layout [v5-validated 2026-05-28]

```
Offset  Size  Type     Field                   Set By
------  ----  ----     -----                   ------
+0x00   4     ptr      vtable                  ctor (= 0x008958d0)
+0x04   4     ptr      data_ptr                SetData / SetDataFromStream / BufferCopy
+0x08   4     int      data_length             SetData / SetDataFromStream / BufferCopy
+0x0C   4     int      from_id                 Set by send path (peer ID of sender)
+0x10   4     int      field_10                (connection context)
+0x14   2     uint16   sequence_number         QueueMessageForPeer (0x006b5080)
+0x18   4     int      field_18                (from address)
+0x1C   4     float    first_resend_time       Retry timing
+0x20   4     float    first_send_time         Retry timing
+0x24   4     float    timestamp               Retry timing
+0x28   4     int      field_28                (to_id on wire)
+0x2C   4     int      num_retries             Retry counter (init 0)
+0x30   4     float    backoff_time            Retry timing (init 1.0)
+0x34   4     float    backoff_factor          Retry multiplier (init 1.0)
+0x38   1     byte     total_fragments         Fragment 0 only: total fragment count
+0x39   1     byte     fragment_index          Which fragment this is (0-based)
+0x3A   1     byte     reliable                0=unreliable, 1=reliable (SetGuaranteed)
+0x3B   1     byte     ordered                 0=normal, 1=priority (SetHighPriority)
+0x3C   1     byte     is_fragment             0=complete, 1=fragment piece
+0x3D   1     byte     field_3D                (init 1, override_old_packets flag)
+0x3E   1     byte     field_3E                (is_multipart flag)
+0x3F   1     byte     field_3F                (is_aggregate flag)
+0x40   1     byte     is_below_0x32           Set per the three-site agreement above
```

**Constructor:** `TGMessage_Ctor` at `0x006b82a0` (allocates `0x40` bytes from pool
`FUN_00717b70`).
**Copy constructor:** `0x006b8550` (copies all fields including fragment metadata).
**SWIG type:** `"_TGMessage_p"` (registered at `puRam00991290`; SWIG `new_TGMessage` at
`0x005e12e0` confirms the class identity by allocating exactly `0x40` and calling
`TGMessage_Ctor`).

## TGHeaderMessage Layout (Type 0x01 ACK) [v5-validated 2026-05-28]

`TGHeaderMessage` is the ACK packet subclass: derived from TGMessage with `+0x40` extra
bytes of header-only state.

- **Size:** `0x44` bytes (`FUN_00717b70(0x44)`)
- **Constructor:** `TGHeaderMessage_Ctor` at `0x006bd120`
- **Serializer:** `TGHeaderMessage_Serialize` at `0x006bd190`
- **Factory:** `0x006bd1f0`
- **Vtable:** `0x008959ac`

On the wire: 4 or 5 bytes total (see "Type 0x01" under Wire Formats). The single `flags`
byte carries `is_fragment` in bit 0 and `is_below_0x32` in bit 1.

## TGMessage Base Vtable (`0x008958d0`) [v5-validated 2026-05-28]

| Slot | Offset | Function | Name |
|------|--------|----------|------|
| 0 | +0x00 | `0x006b9430` | `GetType` (returns `0x32`) |
| 1 | +0x04 | `0x006b82f0` | Destructor |
| 2 | +0x08 | `0x006b8340` | `TGMessage_Serialize` |
| 3 | +0x0C | `0x006b9440` | Unknown (returns 0) — open question |
| 4 | +0x10 | `0x006b9450` | Unknown — open question |
| 5 | +0x14 | `0x006b8640` | `GetSize` |
| 6 | +0x18 | `0x006b8610` | `Clone` |
| 7 | +0x1C | `0x006b8720` | `FragmentMessage` |

## TGDataMessage Vtable (`0x0089598c`, overrides base)

| Slot | Offset | Function | Name |
|------|--------|----------|------|
| 0 | +0x00 | `0x006bd100` | `GetType` (returns `0x00`) |
| 1 | +0x04 | `0x006bc5d0` | Destructor |
| 2 | +0x08 | `0x006bc610` | WriteToBuffer (14-bit length, no fragments) |
| 5 | +0x14 | `0x006bc770` | `GetSize` |
| 6 | +0x18 | `0x006bc740` | `Clone` |

## Send Path

The send path is `TGWinsockNetwork_SendPacket` at `0x006b9870`. It has two paths.

### Real network send

The common case: the cipher encrypts `buf+1` with `len-1`, the result is handed to
`sendto`, and the host's outbox tracking is updated. Fragmentation and reliability are
handled upstream in `TGWinsockNetwork_SendOutgoingPackets` (`0x006b55b0`), which uses
the pack buffer at `network+0x2B` (MTU `1024`).

### Self-send loop-back [v5-validated 2026-05-28]

The host's own packets to itself never hit the OS UDP stack. The branch at `0x006b9870`
checks `if (param_2 == *(int *)(param_1 + 0x1c))` — if the destination address matches the
host's own address (cached at `network+0x1C`), the packet is queued at:

- `network + 0x33C` — local-queue head
- `network + 0x340` — local-queue tail
- `network + 0x344` — toggle flag

The receive side drains this queue *alternately with real `recvfrom`* (using the toggle at
`network+0x344` to decide which source to read on a given call). This means the host gets
its own broadcasts (chat, scoring, ObjCreate) without OS round-trip latency.

> [!NOTE]
> `SendPacket` (`0x006b9870`) and `ReceivePacket` (`0x006b95f0`) had NO direct CALL xrefs
> in stbc.exe because they're `vtable[27]` and `vtable[28]` of `TGWinsockNetwork`'s base
> class — dispatched through `(**(code **)(*p + 0x6C))(...)` and
> `(**(code **)(*p + 0x70))(...)` in `SendOutgoingPackets` / `ProcessIncomingPackets`. Both
> functions were **CREATED** via `mcp__ghidra__create_function` during this v5 pass; auto-
> analysis had not disassembled them. This is the same DATA-only-xref pattern that
> previously hid `MpgameHandleMessage`.

## Connection State Machine [v5-validated 2026-05-28]

States observed directly in `TGWinsockNetwork_HostOrJoin` (`0x006b3ec0`):

| State | Meaning | Entered by |
|-------|---------|------------|
| 1 | (unverified — see Open Questions) | — |
| 2 | HOSTING | Host path of `HostOrJoin` (also posts error_post `0x60002`) |
| 3 | JOINING | Join path of `HostOrJoin` |
| 4 | IDLE / READY | Initial state set in `TGWinsockNetwork_Ctor` (`param_1[5] = 4`) |

Transitions out of `HostOrJoin`: `4 → 2` (host) or `4 → 3` (join). State 1 may exist as a
sub-state during the connect handshake, but it was not observed in `HostOrJoin`. The
TGConnectMessage send-side helpers (`006B8B30` family) are the likely site to investigate.

## Message Dispatchers

Three C++ dispatchers plus a Python-level message path:

1. **NetFile dispatcher** (`FUN_006a3cd0` at `UtopiaModule+0x80`): Handles opcodes
   `0x20`, `0x21`, `0x22`, `0x23`, `0x25`, `0x27` — **NOT contiguous** (0x24 and 0x26 have
   no handler). Registered for event type `0x60001` (`ET_NETWORK_MESSAGE_EVENT`). Sets
   `DAT_0097fa8b = 1` during processing. See
   [checksum-opcodes.md](checksum-opcodes.md) for the canonical opcode catalog.

2. **MultiplayerGame dispatcher** (`0x0069f2a0`, `MpgameHandleMessage`, registered as
   `ReceiveMessageHandler`): Game opcodes `0x02-0x2A`.
   Jump table at `0x0069F534` (41 entries). Forwards to per-opcode handlers based on the
   first byte of payload. Engine-inherited anchor — see
   [wire-format-spec.md](wire-format-spec.md) row 1.

3. **MultiplayerWindow dispatcher** (`FUN_00504c10`): Client-side UI handler.
   Only processes if `this+0xB0 != 0` (gate flag).
   Handles opcodes `0x00`, `0x01`, `0x16`.

4. **Python `SendTGMessage`**: Opcodes `0x2C-0x39` (chat, scoring, game flow).
   Bypass all C++ dispatchers entirely. Handled by Python-level `ReceiveMessage` in
   multiplayer scripts.

## Open Questions

1. **FragmentMessage total_fragments placement** (medium confidence). The doc says
   "Fragment 0 gets `+0x38 = total_fragment_count`". But reading
   `FragmentMessage` (`0x006b8720`), the linked-list manipulation is intricate and the
   `*(undefined1 *)(*piVar8 + 0x38) = (undefined1)iStack_38` after the loop targets what
   appears to be the LAST inserted message, not Fragment 0. Working packet traces confirm
   reassembly succeeds, so either (a) the linked-list logic IS rewinding to head (hard to
   trace in the cleaned decompile) or (b) my read is wrong. The deserializer side is
   unambiguous: it reads `aiStack_400[0]+0x38` for `total_frags`, i.e., Fragment 0 owns the
   byte ON THE WIRE. So the sender-side code MUST put it on whatever clone has
   `+0x39 == 0`. **Resolution:** emulate `FragmentMessage` with a synthetic 3-fragment
   input.

2. **Connection state 1.** States 2, 3, 4 verified directly in `HostOrJoin`. State 1 may
   be a sub-state during connect handshake; needs investigation of the `006B8B30` family
   (TGConnectMessage send-side helpers).

3. **Vtable slots 3 and 4 of TGMessage** (`0x006b9440`, `0x006b9450`). Currently "Unknown
   (returns 0)" and "Unknown". Likely Save/Load or GetAge/IsExpired given the surrounding
   retry-state context, but not investigated this session.

4. **NetFile event registration at `0x60001`**: dispatcher claim is solid; the
   `RegisterHandler` call site for the `0x60001 → FUN_006a3cd0` binding is not yet anchored.

5. **MTU divergence question.** `network+0x2B` (pack buffer size) and `network+0xAC`
   (recv buffer size) are both initialized to `0x400` in the ctor. Are they ALWAYS equal,
   or could they diverge under runtime config? Could affect fragmentation thresholds.

## Cross-doc reconciliation

A few claims in this doc cascade into companion docs that haven't yet been validated under
v5. Those updates are deferred to the companions' own validation passes:

| Doc | Action needed | Why |
|-----|---------------|-----|
| [docs/networking/alby-rules-cipher-analysis.md](../networking/alby-rules-cipher-analysis.md) | Absorb cipher addresses (`InitKey` `0x006c2280`, `Encrypt` `0x006c2490`, `Decrypt` `0x006c2520`, vtable `0x008958c0`) and the re-key-per-packet property | Cipher is now fully anchored — the companion can drop its "transform unknown" caveat |
| [docs/networking/network-protocol.md](../networking/network-protocol.md) | Re-anchor peer-offset claims from `+0x98` / `+0xA8` to `+0x26` / `+0x2A` if cited | Correction C1 in this doc supersedes prior offsets |
| [docs/protocol/checksum-opcodes.md](checksum-opcodes.md) | Canonical for NetFile opcode catalog — this doc just cross-links | NetFile opcodes are non-contiguous (`0x20`, `0x21`, `0x22`, `0x23`, `0x25`, `0x27`) |

## See also

- [docs/protocol/wire-format-spec.md](wire-format-spec.md) — protocol hub: opcode index, handler addresses, subsystem catalog
- [docs/protocol/stream-primitives.md](stream-primitives.md) — TGBufferStream (the SWIG primitive-cursor class — distinct from TGMessage), CF16, CompressedVector3/4
- [docs/protocol/checksum-opcodes.md](checksum-opcodes.md) — NetFile dispatcher opcodes
- [docs/networking/alby-rules-cipher-analysis.md](../networking/alby-rules-cipher-analysis.md) — AlbyRules cipher analysis (pre-v5; absorbs anchors from this doc)
- [docs/networking/fragmented-ack-bug.md](../networking/fragmented-ack-bug.md) — fragmented reliable message ACK bug
- [docs/networking/ack-outbox-deadlock.md](../networking/ack-outbox-deadlock.md) — ACK-outbox deadlock analysis
- [docs/engine/decompiled-functions.md](../engine/decompiled-functions.md) — engine-family anchor table
- [docs/protocol/v5-validation-status.md](v5-validation-status.md) — protocol-family v5 tracker

## Appendix A: TGBufferStream layout — retired

> The "TGBufferStream Layout" appendix that previously lived here described the SWIG
> typed-cursor class (ctor at `0x006cefe0`, vtable `0x00895c58`, sizeof `0x30`) — a
> different class from the wire-envelope `TGMessage` covered in this doc. Both classes
> share `+0x1C` / `+0x20` / `+0x24` offset conventions for buffer / capacity / position,
> but the buffers are independent: `TGBufferStream` is a per-handler scratch cursor that
> reads typed payloads out of a `TGMessage`'s wire buffer.
>
> For the canonical TGBufferStream layout, see
> [stream-primitives.md](stream-primitives.md). The two-class disambiguation pattern is
> documented in that doc's "Class identity" preamble. Resolves protocol
> v5-validation-status §4 reconciliation #2 (the "is the layout in transport-layer.md the
> same as in stream-primitives.md?" question — answer: no, they're different classes).

## Appendix B: Network Object Tracker Layout

Each ship has a per-peer tracking structure (at an offset computed by hash-table lookup):

```
Offset  Size  Type    Field
------  ----  ----    -----
0x00    4     ptr     next (linked list)
0x04    4     f32     last_force_update_time
0x08    4     f32     reserved
0x0C    4     f32     last_speed_value
0x10    4     f32     saved_pos_x (for delta compression)
0x14    4     f32     saved_pos_y
0x18    4     f32     saved_pos_z
0x1C    4     f32     saved_delta_magnitude
0x20    1     u8      saved_delta_dirX
0x21    1     u8      saved_delta_dirY
0x22    1     u8      saved_delta_dirZ
0x24    4     f32     last_orientation_update_time
0x28    1     u8      saved_fwd_dirX
0x29    1     u8      saved_fwd_dirY
0x2A    1     u8      saved_fwd_dirZ
0x2B    1     u8      saved_up_dirX
0x2C    1     u8      saved_up_dirY
0x2D    1     u8      saved_up_dirZ
0x2E    1     u8      saved_cloak_state
0x30    4     ptr     subsystem_list_iterator (for round-robin)
0x34    4     int     subsystem_round_robin_index
0x38    4     ptr     weapon_list_iterator (for round-robin)
0x3C    4     int     weapon_round_robin_index
0x40    4     ptr     weapon_hash_table_vtable (for weapon tracking)
0x44    4     int     weapon_hash_count
0x48    ...   ...     (weapon hash table data)
0x4C    4     ptr     weapon_hash_buckets
```

> [!NOTE]
> Appendix B is StateUpdate per-ship tracking, not transport — it lives here for historical
> reasons. On a future pass this content should move to
> [stateupdate.md](stateupdate.md) or
> [stateupdate-subsystem-wire-format.md](stateupdate-subsystem-wire-format.md).
