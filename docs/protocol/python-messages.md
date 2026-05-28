> [docs](../README.md) / [protocol](README.md) / python-messages.md

---
title: Python Messages (TGMessage script messages bypassing C++ dispatcher)
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
  - docs/protocol/stream-primitives.md
  - docs/protocol/game-opcodes.md
  - docs/protocol/wire-format-spec.md
  - docs/protocol/tgmessage-routing.md
  - docs/engine/decompiled-functions.md
  - docs/protocol/v5-validation-status.md
supersedes:
  - (prior pre-v5 python-messages.md)
evidence:
  - claim: "MAX_MESSAGE_TYPES = 0x2B is registered as a SWIG int constant; the initializer writes the value at runtime via `MOV dword ptr [0x0090B490], 0x2B` (raw bytes `c70590b490002b000000`) at 0x00654F31. The SWIG-globaltable name-slot pointer `0x00952cf8` (the literal `\"MAX_MESSAGE_TYPES\"`) is stored 10 bytes earlier at 0x00654F27."
    address: 0x00654f31
    function: (SWIG init region)
    completeness: high
    confidence: high
    note: "Byte-level verified. Defines the boundary between C++ game opcodes (0x02-0x2A, dispatched by MpgameHandleMessage) and Python script message types (0x2B+, dispatched in Python on ET_NETWORK_MESSAGE_EVENT)."
  - claim: "SWIG wrapper TGNetwork_SendTGMessage at 0x005E3A70 takes (self, targetID:int, message:TGMessage*, optional:int) per format string `OiO|i:TGNetwork_SendTGMessage` at 0x0093846C and calls real function TGWinsockNetwork_SendTGMessage at 0x006B4C10."
    address: 0x005e3a70
    function: (SWIG wrapper; no fn entry)
    completeness: high
    confidence: high
    note: "Located by byte-pattern search for the PUSH of the format-string address; wrapper sits above the PUSH. Ghidra had not auto-decoded an entry for this wrapper before this pass."
  - claim: "SWIG wrapper TGNetwork_SendTGMessageToGroup at 0x005E3B20 takes (self, groupName:string, message:TGMessage*) per format string `OOO:TGNetwork_SendTGMessageToGroup` at 0x0093848C and calls real function TGWinsockNetwork_SendTGMessageToGroup at 0x006B4DE0."
    address: 0x005e3b20
    function: (SWIG wrapper; no fn entry)
    completeness: high
    confidence: high
  - claim: "SWIG wrapper TGMessage_Create at 0x005E13B0 (format `:TGMessage_Create` at 0x00937C30) allocates TGMessage from the heap pool: `PUSH 0x40; CALL 0x00717B70` then `CALL 0x006B82A0` (TGMessage_Ctor). The `PUSH 0x40` is byte-level proof that `sizeof(TGMessage) == 0x40`."
    address: 0x005e13b0
    function: (SWIG wrapper; no fn entry)
    completeness: high
    confidence: high
    note: "Combined with foundation #3 transport-layer C4, this locks TGMessage class identity for the entire protocol family."
  - claim: "SWIG TGMessage_SetGuaranteed wrapper at 0x005E19C0 (format `Oi:TGMessage_SetGuaranteed` at 0x00937D30) writes a boolean to `[TGMessage+0x3A]` via the SETNZ-AL pattern: `SETNZ AL; MOV byte [ECX+0x3A], AL` at 0x005E1A18-0x005E1A21. Byte-level proof of the `+0x3A` boolean field."
    address: 0x005e1a18
    function: (SWIG wrapper; no fn entry)
    completeness: high
    confidence: high
  - claim: "TGWinsockNetwork_SendTGMessage at 0x006B4C10 routes by `targetID`: -1 resolves via FUN_006BB9D0(optional_arg) (returns 0xB on fail); >0 binary-searches the peer array at `[this+0x2C]` (count `[this+0x30]`) sorted by `[peer+0x18]`, falling back to `[this+0x20]` (local-player peer ID) before returning 0xB; ==0 broadcasts by iterating the peer array and queueing a Clone (vtable[6]) per peer, reusing the caller's message on the last peer. Returns 4 (state) on success."
    address: 0x006b4c10
    function: TGWinsockNetwork_SendTGMessage
    completeness: 29.07
    confidence: high
    note: "Pre-v5 completeness 0.00; renamed + typed + plate-commented this pass. Score gated by 8 unresolved magic numbers + 1 unrenamed global + 3 unrenamed struct accesses inside the peer-array walk."
  - claim: "TGWinsockNetwork_SendTGMessageToGroup at 0x006B4DE0 binary-searches the group table at `[this+0xF4]` (count `[this+0xF8]`) sorted by group-name string at `[entry+0x04]` via an unrolled 2-bytes-at-a-time strcmp at 0x006B4E22. On hit it calls TGWinsockNetwork_SendToGroup_Iterate at 0x006B4EC0 to enqueue per member. Returns 0x10 when the group is not found."
    address: 0x006b4de0
    function: TGWinsockNetwork_SendTGMessageToGroup
    completeness: 71.27
    confidence: high
    note: "Pre-v5 completeness 6.62; above the 50 threshold after this pass."
  - claim: "TGMessage_SetDataFromStream at 0x006B8A00 is a 3-call tail-call: `vtable[+0xF4](stream)` (GetBuffer -> [stream+0x1C]), `vtable[+0xD8](stream)` (GetPos -> [stream+0x24]), then `TGMessage_BufferCopy` at 0x006B84D0 to allocate the message data buffer and memcpy the written bytes in."
    address: 0x006b8a00
    function: TGMessage_SetDataFromStream
    completeness: 78.27
    confidence: high
    note: "Pre-v5 completeness 11.93; reaches structural ceiling after rename + prototype + plate."
  - claim: "Group-name strings: `NoMe` at 0x008E5528 and `Forward` at 0x008D94A0. Both built by MultiplayerGame_Ctor at 0x0069E590; each is a 0x14-byte struct with vtable `PTR_FUN_00894684`, registered on TGNetwork's group table at `network+0xF4` via FUN_006B70D0. Group construction is gated on `DAT_0097FA8A` (g_IsMultiplayer) AND `DAT_0097FA78` (TGWinsockNetwork singleton) being non-zero."
    address: 0x0069e590
    function: MultiplayerGame_Ctor
    completeness: 5.39
    confidence: high
    note: "Group strings inspected in-memory. MultiplayerGame_Ctor completeness is low (5.39) because the body is a long sequence of event-handler registrations (~30 calls each with 6 args, most unnamed); a dedicated engine-family ctor pass is the right home for that lift."
  - claim: "ET_NETWORK_MESSAGE_EVENT = 0x60001 confirmed at three independent sites: (1) MultiplayerGame_Ctor at 0x0069E590 registers `FUN_006DB380(0x60001, ..., s_MultiplayerGame____ReceiveMessag_0095A218, 1, 1, ...)`; (2) TGWinsockNetwork::Update at 0x006B4788 sets `MOV EBP, 0x60001` (the event type written at [event+0x10]); (3) TGMessageEvent allocation immediately after at 0x006B4794 does `PUSH 0x2C`, byte-level proof that `sizeof(TGMessageEvent) == 0x2C`."
    address: 0x006b4788
    function: TGWinsockNetwork_Update
    completeness: high
    confidence: high
  - claim: "TGMessageEvent_Ctor at 0x006BFE80 installs vtable `PTR_FUN_0089580C` and zeros the message-ref slot at `[this+0x28]`. TGMessageEvent_AttachMessage at 0x006BFF30 writes the TGMessage* at `[this+0x28]` with release-on-replace via `vtable[1](1)` on the prior reference."
    address: 0x006bfe80
    function: TGMessageEvent_Ctor
    completeness: 38.4
    confidence: high
  - claim: "MpgameHandleMessage at 0x0069F2A0 covers opcodes 0x02-0x2A only. The switch body has no case for any opcode >= 0x2C; Python script messages fall through silently. This is the architectural boundary that makes Python script messages opaque to the C++ game dispatcher."
    address: 0x0069f2a0
    function: MpgameHandleMessage
    completeness: 69.84
    confidence: high
    note: "Negative claim — confirmed by reading the full switch decompile. Engine-family / mid #4 game-opcodes.md owns the same range from the opposite direction."
  - claim: "TGMessage::Serialize at 0x006B8340 is vtable[2] of the TGMessage class (the 0x40-byte wire-envelope at vtable 0x008958D0). Behaviour: writes the class tag byte (0x32) via WriteByte; writes flags_len (16-bit) with bit-15 = reliable flag and bits 0-12 = total message size; if reliable, writes the 16-bit sequence number; then copies the payload via REP MOVSD / MOVSB."
    address: 0x006b8340
    function: TGMessage_Serialize
    completeness: high
    confidence: high
    note: "Per foundation #3 transport-layer C4 cascade. Pre-v5 docs called this method `TGMessage::WriteToBuffer`; renamed per the Ghidra DB and the class-identity adjudication."
  - claim: "TGBufferStream write primitives (the SWIG-visible 0x30-byte typed-cursor class) used by all Python message authoring: WriteByte 0x006CF730, WriteBool 0x006CF7A0, WriteShort 0x006CF7F0, WriteInt 0x006CF830, WriteLong 0x006CF870, WriteFloat 0x006CF8B0, WriteBytes 0x006CF2B0. All match foundation #2 stream-primitives.md."
    address: 0x006cf730
    function: TGBufferStream_swig_WriteChar
    completeness: high
    confidence: high
  - claim: "WriteCString at 0x006CF460 writes a uint32 LE length prefix, NOT uint16 LE. The body is `for(i=0; param_2[i] != 0; i++); vtable[+0x6C](i); vtable[+0x14](param_2, i);` — slot +0x6C is WriteLong (4 bytes), not slot +0x5C (WriteShort)."
    address: 0x006cf460
    function: FUN_006cf460
    completeness: high
    confidence: high
    note: "Corrects a prior 2-byte length-prefix claim. Material for clean-room WriteCString implementations. Stock BC mod code never invokes WriteCString — it uses explicit WriteShort+Write (visible in the CHAT_MESSAGE example below) — so no stock-trace observation is invalidated."
  - claim: "TGWinsockNetwork_ProcessIncomingPackets at 0x006B5C90 is the receive-side entry that reads peer_id + msg_count, dispatches each message through the transport factory table (DAT_009962D4), and feeds the deserialized TGMessage objects forward. Doc rename: prior name `ProcessIncomingMessages` was renamed to `ProcessIncomingPackets` during transport-layer validation."
    address: 0x006b5c90
    function: TGWinsockNetwork_ProcessIncomingPackets
    completeness: high
    confidence: high
---

# Python Message Dispatch

> [!NOTE]
> This doc is `status: partial`. The C++-side machinery (`SendTGMessage` / `SendTGMessageToGroup` / `TGMessage_Create` / `SetGuaranteed` / `SetDataFromStream` / MultiplayerGame group registration / `TGMessageEvent` wrapper / `ET_NETWORK_MESSAGE_EVENT` 0x60001 / `MAX_MESSAGE_TYPES` 0x2B / dispatcher boundary at MpgameHandleMessage opcode 0x2B) is v5-validated against the current Ghidra import (2026-05-28). Material correction: `WriteCString` uses a **uint32 LE** length prefix (4 bytes), not uint16 (2 bytes) — clean-room implementations note that stock BC code never invokes `WriteCString` and uses explicit `WriteShort + Write` instead. Two naming corrections: `FUN_006B8340` is `TGMessage::Serialize` (per foundation #3 cascade), and `FUN_006B5C90` is `ProcessIncomingPackets`. The 10 Python-side message constants and 3 receive-side Python handlers are tagged `[python-source]` — names live in `scripts/` and can't be binary-anchored. Trace-derived routing claims (0x2C echo, 0x36 broadcast, 0x37 per-join roster) carry `[cross-source]` tags. See [docs/guides/v5-evidence-header.md](../guides/v5-evidence-header.md) for the standard.

Two entirely separate mechanisms exist for sending Python-originated data over the network:

## Mechanism 1: Engine Event Forwarding (opcodes 0x06, 0x0D, 0x07-0x12, 0x1B)

These are C++-level messages that forward engine events. The payload is a serialized TGEvent.

**Opcode 0x06 / 0x0D - Python Event**: `FUN_0069F880` strips the opcode byte, creates a stream
from remaining data, constructs a TGEvent via the `FUN_006D6200` factory, posts to the event
manager. Both opcodes route to the same handler.

**Opcodes 0x07-0x0C, 0x0E-0x10, 0x1B - Event Forwarding**: `FUN_0069FDA0` forwards engine-level
events (weapon fire state, cloak, warp, subsystem toggle) to all peers. Each opcode maps to a
hardcoded event code. These are NOT user-level Python messages.

For the full handler catalog see [game-opcodes.md](game-opcodes.md).

## Mechanism 2: TGMessage Script Messages (opcodes 0x2C+)

These are the user-level "script messages" that Python mods create via `TGMessage_Create()` and
send via `SendTGMessage()` or `SendTGMessageToGroup()`. They travel as **standard type 0x32
TGMessage** transport messages on the wire, with the script-defined payload as the message data.

**There is no special C++ dispatcher for these.** They bypass the C++ jump table entirely because
the MultiplayerGame switch only handles opcodes 0x02-0x2A. Instead, ALL type 0x32 TGMessages
arriving from the network are posted as `ET_NETWORK_MESSAGE_EVENT` (event type `0x60001`) to the
engine's event manager. Python handlers registered on this event read the first payload byte
themselves to determine the message type.

## MAX_MESSAGE_TYPES Constant

[v5-validated 2026-05-28] `MAX_MESSAGE_TYPES = 43` (0x2B), stored as a SWIG constant in the
`Appc` module. The SWIG init code at `0x00654F31` does `MOV dword ptr [0x0090B490], 0x2B` (raw
bytes `c70590b490002b000000`); the SWIG-globaltable name-slot pointer to the literal
`"MAX_MESSAGE_TYPES"` is at `0x00952CF8` and is stored 10 bytes earlier (0x00654F27).

This constant defines the boundary between C++ game opcodes and Python script message types.
Python scripts define their message types as `MAX_MESSAGE_TYPES + N`. The values below are
binary-correct as bytes on the wire — the **names** are sourced from Python scripts in
`reference/scripts/` and cannot be anchored from the binary alone.

[python-source: `scripts/MissionShared.py` + `scripts/MultiplayerMenus.py` + `scripts/Mission5/`]

| Constant | Value | Hex | Defined in |
|----------|-------|-----|------------|
| MAX_MESSAGE_TYPES | 43 | 0x2B | Appc (SWIG; binary-anchored) |
| CHAT_MESSAGE | 44 | 0x2C | MultiplayerMenus |
| TEAM_CHAT_MESSAGE | 45 | 0x2D | MultiplayerMenus |
| MISSION_INIT_MESSAGE | 53 | 0x35 | MissionShared |
| SCORE_CHANGE_MESSAGE | 54 | 0x36 | MissionShared |
| SCORE_MESSAGE | 55 | 0x37 | MissionShared |
| END_GAME_MESSAGE | 56 | 0x38 | MissionShared |
| RESTART_GAME_MESSAGE | 57 | 0x39 | MissionShared |
| SCORE_INIT_MESSAGE | 63 | 0x3F | Mission5 |
| TEAM_SCORE_MESSAGE | 64 | 0x40 | Mission5 |
| TEAM_MESSAGE | 65 | 0x41 | Mission5 |

Mods can use any value >= 43 as their message type byte. Since the byte is written via
`WriteChar(chr(N))`, custom types up to 255 are valid.

> [!NOTE]
> The `relay-audit-20260224` packet-trace memory calls byte 0x35 `"GameState"` based on a
> working label. The Python-source constant `MISSION_INIT_MESSAGE` from `MissionShared.py` is
> canonical; both refer to the same byte.

## How Python Scripts Create and Send Messages

The canonical pattern (from `MissionShared.py`):

```python
pMessage = App.TGMessage_Create()       # Allocates TGMessage (0x40 bytes)
pMessage.SetGuaranteed(1)               # Sets +0x3A = 1 (reliable delivery)

kStream = App.TGBufferStream()          # Allocates TGBufferStream (0x30 bytes)
kStream.OpenBuffer(256)                 # Allocates 256-byte write buffer

kStream.WriteChar(chr(END_GAME_MESSAGE))  # Writes 0x38 as first byte
kStream.WriteInt(iReason)                 # Writes 4-byte LE int

pMessage.SetDataFromStream(kStream)     # Copies stream bytes into TGMessage

pNetwork.SendTGMessage(0, pMessage)     # Broadcasts to all peers
kStream.CloseBuffer()                   # Frees stream buffer
```

[v5-validated 2026-05-28] **TGMessage_Create** at `0x005E13B0` allocates 0x40 bytes via the
pool wrapper (`PUSH 0x40; CALL 0x00717B70`) then calls `TGMessage_Ctor` at `0x006B82A0`. The
`PUSH 0x40` is byte-level proof of `sizeof(TGMessage)`.

[v5-validated 2026-05-28] **SetGuaranteed** at `0x005E19C0` writes the boolean via the SETNZ-AL
pattern: `SETNZ AL; MOV byte [ECX+0x3A], AL` (at 0x005E1A18-0x005E1A21). Confirms the `+0x3A`
reliable-flag field.

[v5-validated 2026-05-28] **SetDataFromStream** at `0x006B8A00`: calls `stream.GetBuffer()`
(vtable+0xF4, returns `[stream+0x1C]`) and `stream.GetPos()` (vtable+0xD8, returns
`[stream+0x24]`), then calls `TGMessage_BufferCopy` (`0x006B84D0`) to allocate and memcpy
exactly the written bytes into the TGMessage's data buffer (`+0x04` ptr, `+0x08` length). No
header or framing is added — the stream content IS the TGMessage payload.

## SWIG Wrapper → Real Function Cross-Reference

[v5-validated 2026-05-28] All five Python-facing SWIG wrappers traced from their format-string
PUSH sites. Ghidra had not auto-decoded entries for any of these wrappers before this pass —
they sit as bare disassembly above a `PUSH <fmt_string_addr>` instruction.

| SWIG wrapper | Address | Format string (addr) | Real function | Notes |
|--------------|---------|----------------------|---------------|-------|
| `TGNetwork_SendTGMessage` | 0x005E3A70 | `OiO|i:TGNetwork_SendTGMessage` (0x0093846C) | `TGWinsockNetwork_SendTGMessage` @ 0x006B4C10 | `optional:int` is 4th arg, only used when targetID == -1 |
| `TGNetwork_SendTGMessageToGroup` | 0x005E3B20 | `OOO:TGNetwork_SendTGMessageToGroup` (0x0093848C) | `TGWinsockNetwork_SendTGMessageToGroup` @ 0x006B4DE0 | Indirect via FUN_006BB840 / TGStringResolver chain |
| `TGMessage_Create` | 0x005E13B0 | `:TGMessage_Create` (0x00937C30) | `TGMessage_Ctor` @ 0x006B82A0 (after `PUSH 0x40` alloc) | Byte-level proof TGMessage sizeof = 0x40 |
| `TGMessage_SetGuaranteed` | 0x005E19C0 | `Oi:TGMessage_SetGuaranteed` (0x00937D30) | Inline `SETNZ AL; MOV [ECX+0x3A], AL` | Byte-level proof +0x3A boolean field |
| `TGMessage_SetDataFromStream` | (existing) | — | `TGMessage_SetDataFromStream` @ 0x006B8A00 | 3-call tail-call (GetBuffer / GetPos / BufferCopy) |

## TGBufferStream Write Primitives

All writes are **little-endian** (native x86 store instructions).

[v5-validated 2026-05-28] Foundation #2 confirmed each address and vtable slot.

| Python Method | C++ vtable slot | Size | Format |
|---------------|-----------------|------|--------|
| `WriteChar(chr(N))` | +0x54 (`0x006CF730`) | 1 byte | `uint8` |
| `WriteBool(N)` | +0x58 (`0x006CF7A0`) | 1 byte | `uint8` (0 or 1) |
| `WriteShort(N)` | +0x5C (`0x006CF7F0`) | 2 bytes | `uint16 LE` |
| `WriteInt(N)` | +0x64 (`0x006CF830`) | 4 bytes | `int32 LE` |
| `WriteLong(N)` | +0x6C (`0x006CF870`) | 4 bytes | `int32 LE` (same as WriteInt on Win32) |
| `WriteFloat(N)` | +0x70 (`0x006CF8B0`) | 4 bytes | `float32 LE` (IEEE 754) |
| `Write(buf, len)` | +0x14 (`0x006CF2B0`) | N bytes | raw memcpy |
| `WriteCString(s)` | +0x24 (`0x006CF460`) | **4+N bytes** | `[uint32 LE strlen] [raw chars, NO null]` |

> [!IMPORTANT]
> **Correction (2026-05-28):** `WriteCString` writes a **uint32 LE** length prefix, not uint16 LE
> as the prior doc claimed. The decompile of `FUN_006CF460` calls `vtable[+0x6C]` (WriteLong,
> 4 bytes), NOT `vtable[+0x5C]` (WriteShort, 2 bytes). Stock BC's mod code never invokes
> `WriteCString` — every observed pattern uses explicit `WriteShort(len) + Write(buf, len)`
> (visible in the CHAT_MESSAGE example below), so this correction does not invalidate any
> stock-trace observation. Clean-room implementations of `WriteCString` need the corrected
> width.

## SendTGMessage vs SendTGMessageToGroup

[v5-validated 2026-05-28] `TGWinsockNetwork_SendTGMessage` at `0x006B4C10`, `__thiscall`:

- **SWIG format**: `"OiO|i"` (self, targetID:int, message:TGMessage*, optional:int)
- **`targetID == -1`**: resolves a peer via `FUN_006BB9D0(optional_arg)` and queues the message
  to that peer; returns `0xB` on lookup failure. Exact semantics of `optional_arg` are open
  (see OQ4 below).
- **`targetID > 0`**: **unicast** — binary-searches the peer array at `[this+0x2C]` (count
  `[this+0x30]`) sorted by `[peer+0x18]`; falls back to `[this+0x20]` (local-player peer ID)
  before returning `0xB`.
- **`targetID == 0`**: **broadcast** — iterates the peer array; for each peer with
  `[peer+0xBC] != 1` (not disconnected), Clones the message (vtable[6]) and enqueues; the last
  peer reuses the caller's message rather than cloning.
- Returns `4` (state) on success, `0xB` on peer lookup failure.

[v5-validated 2026-05-28] `TGWinsockNetwork_SendTGMessageToGroup` at `0x006B4DE0`, `__thiscall`:

- **SWIG format**: `"OOO"` (self, groupName:string, message:TGMessage*)
- Binary-searches the group table at `[this+0xF4]` (count `[this+0xF8]`), sorted by group-name
  string at `[entry+0x04]`, via an unrolled 2-bytes-at-a-time strcmp at `0x006B4E22`.
- **Found**: calls `TGWinsockNetwork_SendToGroup_Iterate` at `0x006B4EC0`, which walks the
  group's member list and enqueues per member.
- **Not found**: returns `0x10`.

[v5-validated 2026-05-28] **Built-in groups** (created by `MultiplayerGame_Ctor` at
`0x0069E590`):

- **"NoMe"** (string at `0x008E5528`): All connected peers EXCEPT the local player.
- **"Forward"** (string at `0x008D94A0`): Same membership; used for engine event forwarding
  (opcode 0x06 PythonEvent).

Each group is a 0x14-byte struct with vtable `PTR_FUN_00894684`. The constructor strcpy-style
copies the group name, then calls `FUN_006B70D0` (group register) which inserts into the
TGNetwork group table at `network+0xF4`. Both groups are built **only if** `DAT_0097FA8A`
(g_IsMultiplayer) AND `DAT_0097FA78` (TGWinsockNetwork singleton) are both non-zero.

## Byte-By-Byte Wire Example: CHAT_MESSAGE

Given this Python code:
```python
pMessage = App.TGMessage_Create()
pMessage.SetGuaranteed(1)
kStream = App.TGBufferStream()
kStream.OpenBuffer(256)
kStream.WriteChar(chr(CHAT_MESSAGE))  # 0x2C
kStream.WriteLong(pNetwork.GetLocalID())  # e.g., 0x00000002
kStream.WriteShort(5)  # string length (explicit, NOT via WriteCString)
kStream.Write("hello", 5)  # raw bytes
pMessage.SetDataFromStream(kStream)
pNetwork.SendTGMessage(pNetwork.GetHostID(), pMessage)
```

The TGMessage payload (at `+0x04`, length `+0x08 = 12`) is:
```
2C 02 00 00 00 05 00 68 65 6C 6C 6F
^^                                      message type (CHAT_MESSAGE = 44)
   ^^ ^^ ^^ ^^                         sender ID (uint32 LE = 2)
               ^^ ^^                    string length (uint16 LE = 5)
                     ^^ ^^ ^^ ^^ ^^    "hello" (raw bytes, no null terminator)
```

[v5-validated 2026-05-28] This payload is serialized by `TGMessage::Serialize` (`FUN_006B8340`,
vtable[2] of the 0x40-byte TGMessage class at vtable `0x008958D0`) into a type 0x32 transport
message:
```
32 0F 80 01 00 2C 02 00 00 00 05 00 68 65 6C 6C 6F
^^                                                     transport type (0x32)
   ^^ ^^                                               flags_len (0x800F)
                                                         bits 0-12: 0x0F = 15 (total msg size)
                                                         bit 15: 1 = reliable
         ^^ ^^                                          seq_num (0x0001, reliable sequence #)
               ^^ ^^ ^^ ^^ ^^ ^^ ^^ ^^ ^^ ^^ ^^ ^^  payload (12 bytes)
```

Then in the UDP packet (after AlbyRules! encryption on bytes 1+):
```
01 01 32 0F 80 01 00 2C 02 00 00 00 05 00 68 65 6C 6C 6F
^^                                                           peer_id (0x01 = server)
   ^^                                                        msg_count (1 message)
      ^^ ... (encrypted, but shown decrypted here)           the type 0x32 message
```

## Byte-By-Byte Wire Example: Custom Mod Message (type 205)

Given this mod Python code:
```python
MY_MESSAGE = App.MAX_MESSAGE_TYPES + 162  # = 43 + 162 = 205 = 0xCD
pMessage = App.TGMessage_Create()
pMessage.SetGuaranteed(1)
kStream = App.TGBufferStream()
kStream.OpenBuffer(256)
kStream.WriteChar(chr(MY_MESSAGE))  # 0xCD
kStream.WriteInt(42)
pMessage.SetDataFromStream(kStream)
pNetwork.SendTGMessageToGroup("NoMe", pMessage)
```

TGMessage payload (5 bytes):
```
CD 2A 00 00 00
^^              custom message type (205)
   ^^ ^^ ^^ ^^ int value 42 (uint32 LE)
```

Type 0x32 transport message (10 bytes):
```
32 0A 80 01 00 CD 2A 00 00 00
^^                              transport type
   ^^ ^^                        flags_len: 0x800A (reliable, size=10)
         ^^ ^^                  seq_num: 0x0001
               ^^ ^^ ^^ ^^ ^^  payload (5 bytes)
```

## Receive Side Dispatch

[v5-validated 2026-05-28] End-to-end byte-traced through the six steps below.

1. **`WSN::ReceivePacket`** (`FUN_006B95F0`): `recvfrom`, decrypt bytes 1+ with AlbyRules!.
2. **`TGWinsockNetwork_ProcessIncomingPackets`** (`FUN_006B5C90`): reads `peer_id` and
   `msg_count`; for each message, reads the type byte and dispatches through the transport
   factory table at `DAT_009962D4`. Type 0x32 calls `FUN_006B83F0` (TGMessage factory) which
   deserializes the flags/length/seq/payload into a TGMessage object.
3. **`FUN_006B52B0`**: Dequeues completed messages (handles reliable ordering, fragment
   reassembly).
4. **`TGWinsockNetwork::Update`** (`FUN_006B4560`): For each dequeued message, creates a
   `TGMessageEvent` (`TGMessageEvent_Ctor` at `0x006BFE80`, size 0x2C — proven by `PUSH 0x2C`
   at the allocation site `0x006B4794`), sets the event type to `ET_NETWORK_MESSAGE_EVENT`
   (`0x60001`, proven by `MOV EBP, 0x60001` at `0x006B4788`), attaches the TGMessage via
   `TGMessageEvent_AttachMessage` at `0x006BFF30` (stores at `[this+0x28]`, releases prior
   reference via `vtable[1](1)` on replace), and posts to the event manager via `FUN_006D62B0`.
5. **C++ handlers** (`MultiplayerGame_ReceiveMessage` at `0x0069F2A0`): Checks `GetType() ==
   0x32`, reads the first payload byte, dispatches via switch for opcodes 0x02-0x2A. Opcodes
   outside this range (including all Python script messages 0x2C+) fall through the switch
   and are ignored.
6. **Python handlers**: Registered via
   `AddBroadcastPythonFuncHandler(ET_NETWORK_MESSAGE_EVENT, ...)`. The handler calls
   `pEvent.GetMessage().GetBufferStream()` to get a read view, reads the first byte as message
   type, then dispatches based on value.

Multiple handlers can be registered for `ET_NETWORK_MESSAGE_EVENT`. In stock BC:

| Handler | Source | Handles opcodes |
|---------|--------|-----------------|
| `MultiplayerGame::ReceiveMessageHandler` | C++ @ 0x0069F2A0 (`MpgameHandleMessage`) | 0x02-0x2A |
| `MultiplayerWindow::ReceiveMessageHandler` | C++ @ 0x00504C10 | 0x00, 0x01, 0x16 |
| `NetFile::ReceiveMessageHandler` | C++ @ 0x006A3CD0 | 0x20-0x27 |
| `MissionShared.ProcessMessageHandler` | [python-source] `scripts/MissionShared.py` | 0x35-0x39 |
| `MultiplayerMenus.ProcessMessageHandler` | [python-source] `scripts/MultiplayerMenus.py` | 0x2C-0x2D |
| Mission-specific handlers | [python-source] `scripts/Mission5/`, others | mission-specific types |

All handlers receive the same event. Each reads the first byte and acts on types it
recognizes, ignoring types meant for other handlers.

## Routing semantics observed in traces

The C++ machinery doesn't constrain how Python scripts choose to relay messages — the
following routing patterns come from packet-trace observation of stock dedi runs and are
binary-consistent with the broadcast / group-broadcast / unicast paths in `SendTGMessage` and
`SendTGMessageToGroup`.

[cross-source-2026-02-24 trace]
(`.claude/agent-memory/network-protocol-analyst/relay-audit-20260224.md`, Cady/XFS01 21-min trace)

- **CHAT_MESSAGE (0x2C)** — 1:2 echo. Observed 5 C→S, 10 S→C: the server relays to **all**
  clients **including the original sender**. Confirms the message uses a broadcast send
  (`targetID == 0` or `SendTGMessageToGroup("Forward", ...)`).
- **SCORE_CHANGE_MESSAGE (0x36)** — always paired 1:N broadcast: observed 10 S→C, sent to all
  clients simultaneously whenever a score delta is recorded.
- **SCORE_MESSAGE (0x37)** — per-join roster sync. Observed 6 S→C — full score table is
  re-broadcast each time a new player joins.

See [tgmessage-routing.md](tgmessage-routing.md) for the full routing analysis (deferred to
that doc's own v5 validation pass).

## Guaranteed vs Unreliable

[v5-validated 2026-05-28] `SetGuaranteed(1)` sets `TGMessage+0x3A = 1` (proven by the
`SETNZ AL; MOV byte [ECX+0x3A], AL` pattern at `0x005E1A18-0x005E1A21`), which causes:

- The `reliable` flag (bit 15) to be set in the wire format's `flags_len` field
- A 2-byte sequence number to be included after `flags_len`
- The transport layer to send ACKs (type 0x01) and retransmit on timeout
- The reliable sequence counter (`peer+0x2A` for types >= 0x32; see transport-layer.md C1) to
  be incremented

`SetGuaranteed(0)` (default after `TGMessage_Create`): Message is sent once with no ACK or
retransmit. The `flags_len` has bit 15 = 0 and no sequence number field.

Stock BC scripts **always** call `SetGuaranteed(1)` for script messages. In theory, unreliable
script messages are supported but never used in practice.

## Annotations applied this validation pass

[v5-validated 2026-05-28] 6 function renames + 5 prototypes + 6 plate comments. Plus 2
companion-doc rename cascades absorbed from foundation #2/#3 (`TGMessage::Serialize`,
`ProcessIncomingPackets`).

| Address | Old name | New name | Prototype | Plate |
|---------|----------|----------|-----------|-------|
| 0x006B4C10 | FUN_006B4C10 | `TGWinsockNetwork_SendTGMessage` | `int __thiscall(void*, int, TGMessage*, int)` | yes |
| 0x006B4DE0 | FUN_006B4DE0 | `TGWinsockNetwork_SendTGMessageToGroup` | `int __thiscall(void*, char*, TGMessage*)` | yes |
| 0x006B4EC0 | FUN_006B4EC0 | `TGWinsockNetwork_SendToGroup_Iterate` | — | — |
| 0x006B8A00 | FUN_006B8A00 | `TGMessage_SetDataFromStream` | `void __thiscall(TGMessage*, void*)` | yes |
| 0x006B84D0 | FUN_006B84D0 | `TGMessage_BufferCopy` | — | — |
| 0x006BFE80 | FUN_006BFE80 | `TGMessageEvent_Ctor` | `void* __fastcall(void*)` | yes |
| 0x006BFF30 | FUN_006BFF30 | `TGMessageEvent_AttachMessage` | `void __thiscall(void*, TGMessage*)` | yes |
| 0x0069E590 | FUN_0069E590 | `MultiplayerGame_Ctor` | — | yes |

**Completeness lifts** (effective_score from `analyze_function_completeness`):

| Function | Pre | Post | Notes |
|----------|-----|------|-------|
| `TGWinsockNetwork_SendTGMessage` | 0.00 | 29.07 | Score gated by 8 unresolved magic numbers + 1 unrenamed global + 3 struct accesses |
| `TGWinsockNetwork_SendTGMessageToGroup` | 6.62 | 71.27 | Above the 50 threshold; structural ceiling reached |
| `TGMessage_SetDataFromStream` | 11.93 | 78.27 | Structural ceiling reached |
| `MultiplayerGame_Ctor` | 0.00 | 5.39 | Structural — body is ~30 event-handler registrations with 6 args each; deferred to a dedicated engine-family ctor pass |

## Open questions

1. **OQ1 — `TGMessageEvent` vtable layout.** Vtable installed by `TGMessageEvent_Ctor` is
   `PTR_FUN_0089580C`. Only slot 1 (release / `vtable[1](1)` used by `AttachMessage`) is
   verified this pass. Other slots (`Serialize`, `Clone`, `GetType`, etc.) are unverified.
   Belongs to a `TGMessageEvent` class-layout pass under the engine family.
2. **OQ2 — Python `ProcessMessageHandler` implementations.** The three Python-side handlers
   (`MissionShared.ProcessMessageHandler`, `MultiplayerMenus.ProcessMessageHandler`, and
   mission-specific handlers) live in `reference/scripts/*.py` and are tagged
   `[python-source]` above. Verifying their exact opcode coverage requires Python-corpus
   inspection, which is out of scope for this binary-anchored doc.
3. **OQ3 — 0x35 `MISSION_INIT_MESSAGE` vs "GameState" naming.** The
   `relay-audit-20260224` trace labels byte 0x35 "GameState"; this doc uses the canonical
   Python-source name `MISSION_INIT_MESSAGE` from `MissionShared.py`. Same byte, different
   working labels.
4. **OQ4 — `SendTGMessage` `targetID == -1` semantics.** The dispatch path calls
   `FUN_006BB9D0(optional_arg)` to resolve a peer object, but the exact meaning of
   `optional_arg` (peer-handle ID? in-flight message slot? something else?) needs a follow-up
   under [tgmessage-routing.md](tgmessage-routing.md) validation.

## Companion docs

- [transport-layer.md](transport-layer.md) — TGMessage class identity (size 0x40, vtable
  `0x008958D0`), AlbyRules cipher, the 7 transport factories, fragment reassembly. The
  wire-envelope serialization (`TGMessage::Serialize`) is owned here.
- [stream-primitives.md](stream-primitives.md) — TGBufferStream layout, write primitives, CF16
  encoder/decoder. The `WriteCString` length-prefix correction documented here should
  propagate during that doc's next pass.
- [game-opcodes.md](game-opcodes.md) — the C++ side of the dispatcher boundary; covers
  opcodes 0x02-0x2A. This doc covers the complementary 0x2C+ range.
- [tgmessage-routing.md](tgmessage-routing.md) — full routing analysis (relay-all, star
  topology, NoMe/Forward semantics) — deferred to its own v5 validation pass.
- [wire-format-spec.md](wire-format-spec.md) — hub doc with the cross-family opcode summary.
- [docs/engine/decompiled-functions.md](../engine/decompiled-functions.md) — TGNetwork /
  TGWinsockNetwork base-class anchors.
- [v5-validation-status.md](v5-validation-status.md) — protocol-family tracker; this doc's
  validation log is §6.6.
