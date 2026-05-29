# ACK below32 Flag — Complete Analysis (2026-02-25)

## What is below32?

A 1-bit discriminator in ACK messages (type 0x01) that identifies which of two independent
reliable sequence counter channels the ACK belongs to. Prevents cross-channel seq collisions.

## Two Reliable Channels

| Channel | Transport Types | Send Counter | Expected Counter |
|---------|----------------|-------------|-----------------|
| below32=1 | 0x00-0x05 (DataMsg, Connect, ConnectAck, Boot, Disconnect) | peer+0x26 | peer+0x24 |
| below32=0 | 0x32+ (game data TGMessage) | peer+0x2A | peer+0x28 |

## ACK Wire Format (Type 0x01)

```
[type:0x01][seq:u16 LE][flags:u8]
  flags bit 0 = is_fragment_ack
  flags bit 1 = is_below_0x32 (CRITICAL — OpenBC spec incorrectly says "unused")
[if bit 0: frag_idx:u8]
```

| flags value | Meaning |
|------------|---------|
| 0x00 | ACKing a game-data message (type 0x32), no fragment |
| 0x02 | ACKing a connection-management message (type < 0x32), no fragment |
| 0x01 | ACKing a game-data fragment |
| 0x03 | ACKing a connection-management fragment (rare) |

## How below32 is Set (ACK Creation)

FUN_006b61e0 (HandleReliableReceived), decompiled line 3511:
```c
iVar6 = (**(code **)*param_1)();           // incoming.GetType()
*(bool *)(puVar8 + 0x10) = iVar6 < 0x32;  // ACK.is_below_0x32 = (type < 0x32)
```

## How below32 is Checked (ACK Matching)

FUN_006b64d0 (HandleACK), decompiled line 3776:
```c
cVar1 = *(char *)(param_1 + 0x40);         // ACK.is_below_0x32
iVar3 = (**(code **)*puVar8)();             // retransmit_entry.GetType()
if (((bool)cVar1 != iVar3 < 0x32) || ...)  // MUST match
    goto next;                               // skip if mismatch
```

If below32 doesn't match, the ACK is silently ignored. retxQ entry stays, message retransmits forever.

## OpenBC Bug

Client sends reliable ConnectAck (type 0x03) and DataMsg (type 0x00), both below-0x32.
Server must ACK with flags=0x02 (below32=1). If server ACKs with flags=0x00 (below32=0),
HandleACK CHECK 1 fails: `0 != (0x03 < 0x32)` = mismatch. retxQ never drains.

Stock dedi drains client retxQ to 0 within 12ms. OpenBC leaves it at 2 (190+ retransmits).

## OpenBC Spec Gap

`OpenBC/docs/protocol/transport-layer.md` line 143:
  "bit 1: unused" — WRONG, should be "bit 1: is_below_0x32"

## Key Functions

| Address | Name | Role |
|---------|------|------|
| 0x006b61e0 | HandleReliableReceived | Creates ACK with correct below32 |
| 0x006b64d0 | HandleACK | 4-field match: below32, seq, frag_status, frag_idx |
| 0x006bd190 | TGHeaderMessage::WriteToBuffer | Serializes below32 as flags bit 1 |
| 0x006bd1f0 | TGHeaderMessage::ReadFromBuffer | Deserializes below32 from flags bit 1 |
| 0x006b5080 | SendHelper | Selects seq counter based on GetType() < 0x32 |

## TGHeaderMessage Layout (0x44 bytes)

Inherits TGMessage (0x40 bytes). Additional field:
- +0x40 (u8): is_below_0x32 — constructor defaults to 1, overwritten by factory
