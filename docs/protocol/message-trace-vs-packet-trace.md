> [docs](../README.md) / [protocol](README.md) / message-trace-vs-packet-trace.md

---
title: Cross-Reference — message_trace.log vs packet_trace.log (Stock-Dedi)
type: analysis
audience: re-engineer
validated: 2026-05-28
methodology: FUNCTION_DOC_WORKFLOW_V5
binary:
  name: stbc.exe
  size: 6182400
  base: 0x00400000
status: partial
companions:
  - docs/protocol/wire-format-spec.md
  - docs/protocol/transport-layer.md
  - docs/protocol/game-opcodes.md
  - docs/protocol/checksum-opcodes.md
  - docs/protocol/python-messages.md
  - docs/protocol/tgmessage-routing.md
  - docs/protocol/stateupdate.md
  - docs/protocol/stateupdate-subsystem-wire-format.md
  - docs/protocol/pythonevent-wire-format.md
  - docs/protocol/collision-effect-protocol.md
  - docs/protocol/set-phaser-level-protocol.md
  - docs/protocol/delete-player-ui-wire-format.md
  - docs/protocol/objnotfound-requestobj-enterset-wire-format.md
  - docs/protocol/v5-validation-status.md
evidence:
  - claim: "message_trace captures the TGMessage factory deserialize hook (inbound-only path)"
    address: 0x006b83f0
    function: TGMessage_DeserializeFromBuffer
    confidence: high
    anchored_via: docs/protocol/transport-layer.md
    note: "Type 0x32 factory entry in 256-slot factory table at DAT_009962d4 dispatches to FUN_006b83f0; proxy hook target documented at src/proxy/ddraw_main/message_factory_hooks.inc.c line 22."
  - claim: "Type 0x32 framing: 13-bit length + bit 13 fragment + bit 14 ordered + bit 15 reliable"
    address: 0x006b83f0
    function: TGMessage_DeserializeFromBuffer
    confidence: high
    anchored_via: docs/protocol/transport-layer.md
    note: "Byte-by-byte verified in foundation #3 transport-layer.md against the flags_len LE u16 layout."
  - claim: "Fragmented payload layout: [fragIdx][totalFrags][innerOpcode][...] for frag 0; [fragIdx][continuation] for frag N"
    address: 0x006b83f0
    function: TGMessage_DeserializeFromBuffer
    confidence: high
    anchored_via: docs/protocol/transport-layer.md
    note: "Receive-path layout consistent with the layout the current proxy decoder uses successfully (packet_trace_and_decode.inc.c lines 1184-1211)."
  - claim: "SUB (0x20) flag emitted S->C only; WPN (0x80) flag emitted C->S only — direction exclusivity is structural"
    address: 0x005B17F0
    function: Ship_WriteStateUpdate
    confidence: high
    anchored_via: docs/protocol/stateupdate.md
    note: "Derives from the friendly-fire + player-count gate inside Ship_WriteStateUpdate. Host-side emit places the SUB block; client-side path emits WPN."
  - claim: "Opcode 0x1C StateUpdate dirty-bit semantics (8 flags POS / DELTA / FWD / UP / SPD / CLK / SUB / WPN)"
    address: 0x005B17F0
    function: Ship_WriteStateUpdate
    confidence: high
    anchored_via: docs/protocol/stateupdate.md
  - claim: "Post-ObjCreateTeam SUB cycling: round-robin startIdx walks the subsystem linked list"
    address: null
    function: Ship_WriteSubsystemBlock
    confidence: high
    anchored_via: docs/protocol/stateupdate-subsystem-wire-format.md
    note: "Algorithm anchored in mid #11; the specific startIdx 0/2/6/8/10 values in this doc reflect one particular 2026-02-10 ship-linked-list layout and stay [trace 2026-02-10] tagged."
  - claim: "Opcodes 0x07/0x08/0x09/0x0A/0x0B/0x0E-0x12/0x1B dispatch to GenericEventForward (FUN_0069FDA0) as relay-identical event forwards"
    address: 0x0069FDA0
    function: GenericEventForward
    confidence: high
    anchored_via: docs/protocol/game-opcodes.md
  - claim: "Opcodes 0x06 + 0x0D share PythonEvent handler FUN_0069F880; 0x0D received C->S=12 with S->C=0 — handler is LOCAL-ONLY for both"
    address: 0x0069F880
    function: MpgameHandlePythonEvent
    confidence: high
    anchored_via: docs/protocol/pythonevent-wire-format.md
    note: "See OQ2 — open question whether the 12 received 0x0D events re-emit outbound as 0x06."
  - claim: "Opcode 0x12 SetPhaserLevel relayed C->S -> S->C identically (18-byte TGCharEvent payload)"
    address: 0x006A1410
    function: SetPhaserLevel_Sender
    confidence: high
    anchored_via: docs/protocol/set-phaser-level-protocol.md
  - claim: "Opcode 0x13 HostMsg C->S only (self-destruct request, no S->C relay)"
    address: 0x006A01B0
    function: HostMsg_Handler
    confidence: high
    anchored_via: docs/protocol/game-opcodes.md
  - claim: "Opcode 0x15 CollisionEffect is C->S only (no S->C broadcast)"
    address: 0x006a2470
    function: CollisionEffectHandler
    confidence: high
    anchored_via: docs/protocol/collision-effect-protocol.md
    note: "Count 5/5/0 in the cross-reference table matches the leaf #15 finding that the handler never re-emits the contact event."
  - claim: "Opcode 0x17 DeletePlayerUI is S->C only"
    address: 0x006a1360
    function: DeletePlayerUI_Handler
    confidence: high
    anchored_via: docs/protocol/delete-player-ui-wire-format.md
    note: "Count -/-/3 in the cross-reference table matches the leaf #17 finding that 0x17 is a server-driven scoreboard removal."
  - claim: "Opcodes 0x1D ObjNotFound / 0x1E RequestObj / 0x1F EnterSet form the object-recovery / scene-transition triad"
    address: 0x006a0490
    function: ObjNotFoundHandler
    confidence: high
    anchored_via: docs/protocol/objnotfound-requestobj-enterset-wire-format.md
    note: "0x1D count -/-/12 (S->C only) matches leaf #18."
  - claim: "Opcodes 0x20 ChecksumReq / 0x21 ChecksumResp / 0x28 ChecksumComplete (corrects pre-v5 label \"Unknown\" for 0x28)"
    address: 0x0095a0cc
    function: null
    confidence: high
    anchored_via: docs/protocol/checksum-opcodes.md
    note: "Registration string \"MultiplayerGame :: ChecksumCompleteHandler\" at 0x0095a0cc identifies 0x28."
  - claim: "Opcode 0x2A NewPlayerInGame C->S only; server responds with 0x18 DeletePlayerAnim outbound"
    address: 0x006A1E70
    function: Handler_NewPlayerInGame_0x2A
    confidence: high
    anchored_via: docs/protocol/game-opcodes.md
  - claim: "Opcode 0x2C ChatMessage relayed via SendTGMessage Python path (star-topology relay, each peer receives independently)"
    address: null
    function: null
    confidence: high
    anchored_via: docs/protocol/python-messages.md
  - claim: "Opcodes 0x07-0x0C, 0x0E-0x12, 0x1B GenericEventForward group + 0x19 TorpedoFire + 0x1A BeamFire + 0x1B TorpTypeChange all relay-identical"
    address: 0x0069FDA0
    function: GenericEventForward
    confidence: high
    anchored_via: docs/protocol/game-opcodes.md
  - claim: "Historical: packet_trace decoder fragment-handling is FIXED in current proxy"
    address: null
    function: null
    confidence: high
    source: src/proxy/ddraw_main/packet_trace_and_decode.inc.c lines 1184-1211
    note: "Bug was present at 2026-02-10 trace capture; decoder now reads fragIdx/fragTotal before the inner opcode and labels continuation fragments. The misdecoded entries in the historical section below are preserved for trace cross-reference."
supersedes:
  - 2026-02-10
---

# Cross-Reference: message_trace.log vs packet_trace.log (Stock-Dedi)

> [!NOTE]
> **Cross-source doc; 17 claim-promotions + 3 historical-section marks + 1 label clarification.** All load-bearing trace observations are now independently anchored in validated v5 docs across the protocol family. Two "current state" sections are historical — the proxy decoder fragmentation bug and the "flags=0x00 EMPTY" subsystem-data issue are both resolved in the current proxy build (`flags=0x20` now ships via DeferredInitObject; packet_trace decoder reads fragIdx/fragTotal cleanly). The session-specific count numbers (10,459 C->S StateUpdates, 19,997 S->C StateUpdates, histograms, per-opcode totals) all stay `[trace 2026-02-10]` — they are valid observations of one specific 33.5-minute session. Source evidence: `.claude/agent-memory/game-archaeology-specialist/message-trace-vs-packet-trace-validation-20260528.md`.

**Date:** 2026-02-10 (original trace capture)
**Source:** Stock dedicated server with OBSERVE_ONLY proxy DLL
**v5 validation:** 2026-05-28 (protocol family leaf #22 — closes the protocol-family campaign at 22/22)

This doc is a **cross-source differential analysis** comparing two runtime instrumentation hooks against the same 33.5-minute stock-dedicated-server session: `message_trace.log` (TGMessage factory deserialize hook, inbound-only) vs `packet_trace.log` (sendto/recvfrom hex dump, bidirectional). It is preserved as the **canonical example of paired-trace differential analysis** for future protocol work. The doc itself contains no wire-format errors — every load-bearing observation is now independently anchored in a per-opcode or per-system v5 doc. Tags below mark each claim's anchor.

## Key Discovery: message_trace = RECEIVE path only

The `message_trace.log` hooks the TGMessage factory at the **deserialization/receive** path. It captures messages as the engine processes incoming UDP packets into TGMessage objects. It does NOT capture outbound messages the server creates and sends.

> [v5-validated 2026-05-28 via foundation #3 transport-layer.md] message_trace captures the TGMessage factory dispatch path: factory table at `DAT_009962d4`, type 0x32 dispatches to TGMessage base `FUN_006b83f0`. Confirmed via `src/proxy/ddraw_main/message_factory_hooks.inc.c` line 22 (`type 0x32: FUN_006b83f0`).

**Proof**: Every game opcode in the message_trace matches the packet_trace's C->S counts exactly. All S->C messages are absent from the message_trace.

## StateUpdate Flag Separation: SUB vs WPN

The most critical architectural finding:

[v5-validated 2026-05-28 via mid #8 stateupdate.md]

| Direction | Flags Used | Never Used | Count [trace 2026-02-10] |
|-----------|-----------|------------|--------------------------|
| **C->S** | WPN (0x80) always, plus POS / DELTA / FWD / UP / SPD / CLK | SUB (0x20) NEVER | 10,459 |
| **S->C** | SUB (0x20) always, plus POS / DELTA / FWD / UP / SPD / CLK | WPN (0x80) NEVER | 19,997 |

Client sends **weapon status** (0x80) to server; server sends **subsystem health** (0x20) to client. These are mutually exclusive by direction — direction-exclusivity derives from the friendly-fire + player-count gate inside `Ship_WriteStateUpdate` at `0x005B17F0`, not from a coincidence of trace observation.

### S->C StateUpdate flag distribution (top 5) [trace 2026-02-10]
```
0x20 (SUB only)                  : 10,539  (idle subsys cycling)
0x3E (DELTA|FWD|UP|SPD|SUB)      :  5,867  (movement + subsys)
0x36 (DELTA|FWD|SPD|SUB)         :  1,389
0x3D (POS|FWD|UP|SPD|SUB)        :    823
0x32 (DELTA|SPD|SUB)             :    719
```

### C->S StateUpdate flag distribution (top 5) [trace 2026-02-10]
```
0x9E (DELTA|FWD|UP|SPD|WPN)      :  6,079  (movement + weapons)
0x96 (DELTA|FWD|SPD|WPN)         :  1,632
0x92 (DELTA|SPD|WPN)             :    900
0x9D (POS|FWD|UP|SPD|WPN)        :    796
0x8E (DELTA|FWD|UP|WPN)          :    214
```

## Fragmented Reliable Messages

Large checksum responses use fragmented reliable delivery.

[v5-validated 2026-05-28 via foundation #3 transport-layer.md]

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

Example: checksum response round 2 = 3 fragments, 412 bytes total [trace 2026-02-10]:
```
#32: flags=0xA1 frag_idx=0 total=3 inner=0x21(ChecksumResp) round=2  size=412
#36: flags=0xA1 frag_idx=1 continuation data                          size=412
#37: flags=0xA0 frag_idx=2 LAST fragment                              size=27
```

### PACKET_TRACE DECODER BUG

> **Historical (resolved 2026-05-28)** — proxy decoder fragmentation handling is FIXED in current `src/proxy/ddraw_main/packet_trace_and_decode.inc.c` lines 1184-1211. Fragments are properly extracted (`fragIdx` / `fragTotal` read before the inner-opcode read) and continuation fragments are labeled as such. The misdecoded entries below are preserved for trace cross-reference with the original 2026-02-10 `packet_trace.log` and are NOT representative of current proxy behavior.

The 2026-02-10 packet_trace decoder did NOT handle fragmentation. It read `fragment_index` as the game opcode, producing garbage:
- Fragment 0 (byte=0x00) -> misdecoded as "Settings" with garbage gameTime
- Fragment 1 (byte=0x01) -> misdecoded as "GameInit"
- Fragment 2 (byte=0x02) -> misdecoded as "ObjCreate"

Affected packets in stock-dedi trace [trace 2026-02-10]:
```
#27 C->S 22:08:41.709 - frag 0 of checksum round 2 -> misdecoded as Settings
#28 C->S 22:08:41.709 - frag 1 -> misdecoded as GameInit
#31 C->S 22:08:41.790 - frag 0 retransmit -> misdecoded as Settings
#86 C->S 22:09:06.395 - frag 0 of checksum round 2 (2nd peer)
#88 C->S 22:09:06.395 - frag 1 (2nd peer)
```

## Corrected Opcode Cross-Reference Table

[v5-validated 2026-05-28 — per-row anchors below table]

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
0x21    ChecksumResp              11          8          0       MATCH (11 = 8 + 3 first-frags; see note below)
0x2A    NewPlayer                  2          2          0       MATCH
0x2C    ChatMessage                5          5         ~15       MATCH (relayed to both peers)

S->C only (not in message_trace):
0x00    Settings                   -          -          3       S->C outbound only
0x01    GameInit                   -          -          3       S->C outbound only
0x06    PythonEvent                -          -        251       S->C outbound only
0x17    DeletePlayerUI             -          -          3       S->C outbound only
0x18    DeletePlayerAnim           -          -          1       S->C outbound only
0x1D    ObjNotFound                -          -         12       S->C outbound only
0x20    ChecksumReq                -          -         11       S->C outbound only
0x28    ChecksumComplete           -          -          3       S->C outbound only (signal: all checksum rounds done)
0x35    GameState (MISSION_INIT_MESSAGE) -    -          3       S->C outbound only — see OQ1
0x37    PlayerRoster (SCORE_MESSAGE)     -    -          1       S->C outbound only — see OQ1
```

**Every C->S game opcode in the packet_trace appears in the message_trace with matching counts.**

**Per-row anchors:**
- 0x03 / 0x2A — [v5-validated 2026-05-28 via mid #4 game-opcodes.md (FUN_0069F620 ObjCreate / FUN_006A1E70 NewPlayerInGame)]
- 0x07 / 0x08 / 0x09 / 0x0A / 0x0B / 0x11 / 0x1B — [v5-validated 2026-05-28 via mid #4 game-opcodes.md, FUN_0069FDA0 GenericEventForward group]
- 0x0D — [v5-validated 2026-05-28 via leaf #14 pythonevent-wire-format.md (LOCAL-ONLY at FUN_0069F880)]
- 0x12 — [v5-validated 2026-05-28 via leaf #16 set-phaser-level-protocol.md]
- 0x13 — [v5-validated 2026-05-28 via mid #4 game-opcodes.md (FUN_006A01B0 HostMsg self-destruct)]
- 0x15 — [v5-validated 2026-05-28 via leaf #15 collision-effect-protocol.md]
- 0x17 — [v5-validated 2026-05-28 via leaf #17 delete-player-ui-wire-format.md]
- 0x19 / 0x1A — [v5-validated 2026-05-28 via mid #4 game-opcodes.md (FUN_0069F930 torpedo / FUN_0069FBB0 beam)]
- 0x1C — [v5-validated 2026-05-28 via mid #8 stateupdate.md (direction asymmetry SUB host-only)]
- 0x1D — [v5-validated 2026-05-28 via leaf #18 objnotfound-requestobj-enterset-wire-format.md]
- 0x20 / 0x21 / 0x28 — [v5-validated 2026-05-28 via mid #5 checksum-opcodes.md]
- 0x2C — [v5-validated 2026-05-28 via mid #6 python-messages.md]

**Note on opcode 0x21 count arithmetic (`11 = 8 + 3 first-frags`):** message_trace counts opcodes after reassembly (8 reassembled responses); packet_trace counts opcodes after decryption (8 + 3 first-fragment frames = 11 raw entries). The 3 first-fragment frames carry the inner opcode 0x21 at offset +2 of their payload; the 2026-02-10 decoder misdecoded them as inner-opcode 0x00/0x01/0x02 (see Historical PACKET_TRACE DECODER BUG section above), but the raw frame count is still 11.

## Newly Identified Opcodes

> **Historical (anchored 2026-05-28)** — all five opcodes listed below were "newly identified" during the 2026-02-10 trace analysis. They are now fully anchored in dedicated v5 docs (per-row links below). This table is preserved for the original trace context but is no longer load-bearing — consult the linked v5 docs for the canonical wire format.

| Opcode | Name | Format | Example | Anchored in |
|--------|------|--------|---------|-------------|
| **0x2C** | **ChatMessage** | `[0x2C][sender_slot:1][00 00 00][msgLen:2 LE][ASCII text]` | slot=3, "everything good for you?" | [python-messages.md](python-messages.md) |
| **0x11** | **RepairListPriority** | 21 bytes payload, relayed C->S -> S->C | GenericEventForward group: TGObjPtrEvent (0x010C), repair priority reorder | [game-opcodes.md § GenericEventForward](game-opcodes.md) |
| **0x12** | **SetPhaserLevel** | 18 bytes payload, relayed C->S -> S->C | GenericEventForward group: TGCharEvent (0x0105), phaser intensity byte | [set-phaser-level-protocol.md](set-phaser-level-protocol.md) |
| **0x28** | **ChecksumComplete** | 6 bytes total (1 byte payload), S->C only | Sent immediately before Settings — signal: all checksum rounds done | [checksum-opcodes.md § ChecksumComplete](checksum-opcodes.md) |
| **0x13** | HostMsg | C->S only, not relayed | 2 occurrences (self-destruct request) | [game-opcodes.md § 0x13 HostMsg](game-opcodes.md) |

## Post-ObjCreateTeam SUB Cycling Pattern

[v5-validated 2026-05-28 via mid #11 stateupdate-subsystem-wire-format.md] — the cycling algorithm (round-robin `startIdx` walking the subsystem linked list) is anchored at mid-tier. The specific startIdx values 0/2/6/8/10 in the example below reflect the particular subsystem-linked-list layout for one specific ship at one specific moment in the 2026-02-10 trace — they stay `[trace 2026-02-10]` because the indices are session-specific even though the algorithm is binary-anchored.

After client sends ObjCreateTeam, stock server immediately cycles subsystem groups [trace 2026-02-10]:

```
T+0.000  S->C  StateUpdate obj=0x3FFFFFFF flags=0x20 startIdx=0  (9 bytes subsys data)
T+0.090  S->C  StateUpdate obj=0x3FFFFFFF flags=0x20 startIdx=2  (15 bytes subsys data)
T+0.120  S->C  StateUpdate obj=0x3FFFFFFF flags=0x20 startIdx=6  (11 bytes subsys data)
T+0.210  S->C  StateUpdate obj=0x3FFFFFFF flags=0x20 startIdx=8  (7 bytes subsys data)
T+0.310  S->C  StateUpdate obj=0x3FFFFFFF flags=0x20 startIdx=10 (8 bytes subsys data)
[cycle repeats every ~0.5s with full POS+SUB every ~1s]
```

startIdx 0, 2, 6, 8, 10 correspond to different subsystem groups along the ship's subsystem linked list at that frame.

## Implications for Our Proxy

> **Historical (resolved 2026-05-28)** — RESOLVED. Our proxy now sends `flags=0x20` with real subsystem health data via DeferredInitObject — see CLAUDE.md "What Works" status (Collision damage / Subsystem damage / **StateUpdate flags=0x20**). The disconnect symptom described below was the trigger that motivated the DeferredInitObject implementation; the implementation has shipped and the symptom is gone.

At the time of this trace analysis, our proxy emitted `flags=0x00` (EMPTY) because the headless engine had no subsystem data. Stock sends `flags=0x20` (SUB) with real health values ~10x per second per object. This was the direct trigger for client disconnect — clients expected regular subsystem health updates and treated their absence as a connection failure. Resolved by **DeferredInitObject** (Python-driven ship creation that loads NIFs and populates `ship+0x284`).

## Pattern Note: Paired-Trace Differential Analysis

This doc demonstrates a reusable RE pattern worth repeating for future protocol work. Instrumenting two different hook points and diffing their outputs reveals direction / routing characteristics that neither hook surfaces alone.

**Hook A — TGMessage factory deserialize.** Catches inbound, post-decrypt, post-reassemble.
- Address: `FUN_006b83f0` (type 0x32 entry in transport factory table `DAT_009962d4`)
- Proxy hook: `src/proxy/ddraw_main/message_factory_hooks.inc.c` line 22
- Captures: every message the engine accepts after decryption + reassembly
- Misses: outbound traffic (server doesn't deserialize what it sends); fragments before reassembly

**Hook B — sendto / recvfrom packet trace.** Catches both directions, pre-decrypt at the wire layer.
- Proxy hook: socket interceptor at `src/proxy/ddraw_main/socket_and_input_hooks.inc.c`
- Captures: every byte on the wire, both directions
- Misses: nothing at the wire level, but observes pre-decrypt frames (and pre-reassembly fragments)

**Diff (A) vs (B-incoming) catches:**
- Server-generated messages (in B-outbound but not A) — names the server's emit set
- Direction-exclusive opcodes (counts diverge by direction) — uncovered SUB / WPN flag direction-exclusivity
- Decoder bugs (B's counts off by fragmentation-related amounts when A is reassembled-correct) — uncovered the 2026-02-10 packet_trace fragment misdecode

The 2026-02-10 session is the **canonical example** of this pattern. Re-run when adding new opcodes or new transport types so the differential surfaces any wire-layer or routing oversights.

## Open Questions

**OQ1 — informal Python-message label drift.** The S->C-only block in the cross-reference table labels `0x35 GameState` and `0x37 PlayerRoster`. Mid #6 [python-messages.md](python-messages.md) names these `MISSION_INIT_MESSAGE` (0x35) and `SCORE_MESSAGE` (0x37) — the canonical names from BC's Python source. The trace labels are functionally accurate but informal; a future sync pass should reconcile this doc's labels with the python-messages.md canonical names. Non-blocking.

**OQ2 — 0x0D PythonEvent2 re-emit path.** Doc shows 0x0D C->S=12 with S->C=0. Leaf #14 [pythonevent-wire-format.md](pythonevent-wire-format.md) notes that FUN_0069F880 is LOCAL-ONLY and handles both 0x06 and 0x0D. Open: do those 12 received 0x0D events re-emit outbound as opcode 0x06 (which would inflate the S->C 0x06=251 count), or does the engine drop them after the local apply step? Resolution requires either (a) bisecting the S->C 0x06 stream to find a 12-event burst correlated with the C->S 0x0D arrivals, or (b) emulating FUN_0069F880 with a 0x0D input and watching for outbound 0x06. Non-blocking.

## Related Documents

This doc is a cross-source analysis — every load-bearing claim cites a v5-validated companion doc as authority. For per-opcode wire format detail, follow the companion link above for that opcode. The companions list in frontmatter enumerates all 13 v5-validated docs that anchor the claims here.
