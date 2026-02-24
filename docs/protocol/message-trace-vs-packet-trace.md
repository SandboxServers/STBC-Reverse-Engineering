> [docs](../README.md) / [protocol](README.md) / message-trace-vs-packet-trace.md

# Cross-Reference: message_trace.log vs packet_trace.log (Stock-Dedi)

Date: 2026-02-10
Source: Stock dedicated server with OBSERVE_ONLY proxy DLL

## Key Discovery: message_trace = RECEIVE path only

The message_trace.log hooks the TGMessage factory at the **deserialization/receive** path.
It captures messages as the engine processes incoming UDP packets into TGMessage objects.
It does NOT capture outbound messages the server creates and sends.

**Proof**: Every game opcode in the message_trace matches the packet_trace's C->S counts exactly.
All S->C messages are absent from the message_trace.

## StateUpdate Flag Separation: SUB vs WPN

The most critical architectural finding:

| Direction | Flags Used | Never Used | Count |
|-----------|-----------|------------|-------|
| **C->S** | WPN (0x80) always, plus POS/DELTA/FWD/UP/SPD/CLK | SUB (0x20) NEVER | 10,459 |
| **S->C** | SUB (0x20) always, plus POS/DELTA/FWD/UP/SPD/CLK | WPN (0x80) NEVER | 19,997 |

Client sends **weapon status** (0x80) to server; server sends **subsystem health** (0x20) to client.
These are mutually exclusive by direction.

### S->C StateUpdate flag distribution (top 5)
```
0x20 (SUB only)                  : 10,539  (idle subsys cycling)
0x3E (DELTA|FWD|UP|SPD|SUB)      :  5,867  (movement + subsys)
0x36 (DELTA|FWD|SPD|SUB)         :  1,389
0x3D (POS|FWD|UP|SPD|SUB)        :    823
0x32 (DELTA|SPD|SUB)             :    719
```

### C->S StateUpdate flag distribution (top 5)
```
0x9E (DELTA|FWD|UP|SPD|WPN)      :  6,079  (movement + weapons)
0x96 (DELTA|FWD|SPD|WPN)         :  1,632
0x92 (DELTA|SPD|WPN)             :    900
0x9D (POS|FWD|UP|SPD|WPN)        :    796
0x8E (DELTA|FWD|UP|WPN)          :    214
```

## Fragmented Reliable Messages

Large checksum responses use fragmented reliable delivery:

```
Type 0x32 flags_len (LE u16):
  bits 12-0 = total length (13-bit)
  bit 13    = fragment flag
  bit 14    = ordered
  bit 15    = reliable

When the high byte of flags_len is viewed in hex dumps:
  0x80 = reliable (bit 15)
  0x20 = fragmented (bit 13)
  NOTE: bit 0 of high byte is NOT "more fragments" -- it is bit 8 of the 13-bit length

Fragmented payload layout:
  [fragment_index][total_fragments][inner_payload...]  (first fragment, frag_idx=0)
  [fragment_index][continuation_data...]               (subsequent fragments)
Last fragment detected when all indices 0..total_frags-1 collected (no "more" bit).
```

Example: checksum response round 2 = 3 fragments, 412 bytes total:
```
#32: flags=0xA1 frag_idx=0 total=3 inner=0x21(ChecksumResp) round=2  size=412
#36: flags=0xA1 frag_idx=1 continuation data                          size=412
#37: flags=0xA0 frag_idx=2 LAST fragment                              size=27
```

### PACKET_TRACE DECODER BUG

The packet_trace decoder does NOT handle fragmentation. It reads fragment_index as the
game opcode, producing garbage:
- Fragment 0 (byte=0x00) -> misdecoded as "Settings" with garbage gameTime
- Fragment 1 (byte=0x01) -> misdecoded as "GameInit"
- Fragment 2 (byte=0x02) -> misdecoded as "ObjCreate"

Affected packets in stock-dedi trace:
```
#27 C->S 22:08:41.709 - frag 0 of checksum round 2 -> misdecoded as Settings
#28 C->S 22:08:41.709 - frag 1 -> misdecoded as GameInit
#31 C->S 22:08:41.790 - frag 0 retransmit -> misdecoded as Settings
#86 C->S 22:09:06.395 - frag 0 of checksum round 2 (2nd peer)
#88 C->S 22:09:06.395 - frag 1 (2nd peer)
```

## Corrected Opcode Cross-Reference Table

```
Opcode  Name                  msg_trace   pkt C->S   pkt S->C   Status
------  ----                  ---------   --------   --------   ------
0x03    ObjCreateTeam              6          6          6       MATCH
0x07    StartFire                330        330        330       MATCH (relayed)
0x08    StopFire                 161        161        163       MATCH (2 extra S->C = server-gen)
0x0A    SubsysStatus               7          7         11       MATCH (4 extra S->C = server-gen)
0x0D    PythonEvent2              12         12          0       MATCH (C->S only)
0x11    RepairListPriority         2          2          2       MATCH (relayed, GenericEventForward)
0x12    SetPhaserLevel             5          5          5       MATCH (relayed, GenericEventForward)
0x13    HostMsg                    2          2          0       MATCH (C->S only)
0x15    CollisionEffect            5          5          0       MATCH (C->S only)
0x19    TorpedoFire               76         76         76       MATCH (relayed)
0x1A    BeamFire                  68         68         68       MATCH (relayed)
0x1B    TorpTypeChange             2          2          2       MATCH (relayed)
0x1C    StateUpdate           10,459     10,459     19,997       MATCH C->S; S->C has SUB
0x21    ChecksumResp              11          8          0       MATCH (11 = 8 + 3 first-frags)
0x2A    NewPlayer                  2          2          0       MATCH
0x2C    ChatMessage                5          5         ~15       MATCH (relayed to both peers)

S->C only (not in message_trace):
0x00    Settings                   -          -          3       S->C outbound only
0x01    GameInit                   -          -          3       S->C outbound only
0x06    PythonEvent                -          -        251       S->C outbound only
0x17    DeletePlayerUI             -          -          3       S->C outbound only
0x18    DeletePlayerAnim           -          -          1       S->C outbound only
0x1D    ObjNotFound                -          -         12       S->C outbound only
0x20    ChecksumReq               -          -         11       S->C outbound only
0x28    ChecksumComplete           -          -          3       S->C outbound only (signal: all checksum rounds done)
0x35    GameState                  -          -          3       S->C outbound only
0x37    PlayerRoster               -          -          1       S->C outbound only
```

**Every C->S game opcode in the packet_trace appears in the message_trace with matching counts.**

## Newly Identified Opcodes

| Opcode | Name | Format | Example |
|--------|------|--------|---------|
| **0x2C** | **ChatMessage** | `[0x2C][sender_slot:1][00 00 00][msgLen:2 LE][ASCII text]` | slot=3, "everything good for you?" |
| **0x11** | **RepairListPriority** | 21 bytes payload, relayed C->S -> S->C | GenericEventForward group: TGObjPtrEvent (0x010C), repair priority reorder |
| **0x12** | **SetPhaserLevel** | 18 bytes payload, relayed C->S -> S->C | GenericEventForward group: TGCharEvent (0x0105), phaser intensity byte |
| **0x28** | Unknown | 6 bytes total (1 byte payload), S->C only | Sent immediately before Settings |
| **0x13** | HostMsg | C->S only, not relayed | 2 occurrences |

## Post-ObjCreateTeam SUB Cycling Pattern

After client sends ObjCreateTeam, stock server immediately cycles subsystem groups:

```
T+0.000  S->C  StateUpdate obj=0x3FFFFFFF flags=0x20 startIdx=0  (9 bytes subsys data)
T+0.090  S->C  StateUpdate obj=0x3FFFFFFF flags=0x20 startIdx=2  (15 bytes subsys data)
T+0.120  S->C  StateUpdate obj=0x3FFFFFFF flags=0x20 startIdx=6  (11 bytes subsys data)
T+0.210  S->C  StateUpdate obj=0x3FFFFFFF flags=0x20 startIdx=8  (7 bytes subsys data)
T+0.310  S->C  StateUpdate obj=0x3FFFFFFF flags=0x20 startIdx=10 (8 bytes subsys data)
[cycle repeats every ~0.5s with full POS+SUB every ~1s]
```

startIdx 0, 2, 6, 8, 10 correspond to different subsystem groups.

## Implications for Our Proxy

Our proxy sends flags=0x00 (EMPTY) because the headless engine has no subsystem data.
Stock sends flags=0x20 (SUB) with real health values ~10x per second per object.
This is likely the direct trigger for client disconnect -- client expects regular subsystem
health updates and treats their absence as a connection failure.
