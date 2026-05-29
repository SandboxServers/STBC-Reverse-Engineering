# Validation: docs/protocol/message-trace-vs-packet-trace.md

**Date:** 2026-05-28
**Doc:** Protocol leaf #22 (FINAL leaf — closes the protocol-family v5 campaign at 22/22)
**Source format:** Cross-trace comparison (33.5 min 2026-02-10 stock-dedi session)
**Verdict:** `partial` — content correct; promote ~12 trace claims to v5-validated via cross-references, mark 3 sections as historical, no material wire-format corrections.

---

## Why "partial" not "verified"

Every load-bearing claim in the doc is either (a) now fully anchored in a validated v5 mid/leaf doc, or (b) a meta-claim about runtime instrumentation behavior, or (c) historical (already resolved or now-fixed). The doc itself contains no errors but needs:

- Confidence-tag promotions on ~12 claims (`[cross-source-2026-02-10 trace]` → `[v5-validated 2026-05-28 via <anchor doc>]`)
- 3 sections marked historical (Newly Identified Opcodes, PACKET_TRACE DECODER BUG, Implications for Our Proxy)
- 1 minor clarification (opcode 0x28 column "Unknown" → "ChecksumComplete" with anchor)

Once those touch-ups land it's `verified`. The "partial" tag is for the touch-ups, not for unresolved evidence.

---

## Confirmed claims (all cross-anchored)

| Claim | Anchor doc | Notes |
|-------|------------|-------|
| message_trace = TGMessage factory deserialize hook = inbound-only | foundation #3 transport-layer.md (DAT_009962d4 factory table) + proxy `message_factory_hooks.inc.c` line 22 (`type 0x32: FUN_006b83f0`) | Meta-claim about proxy instrumentation; binary-anchored via factory table address |
| SUB (0x20) C→S NEVER / S→C ALWAYS | mid #8 stateupdate-validation (Ship_WriteStateUpdate 0x005B17F0 host-side emit; flag 0x80/0x20 direction split derives from friendly-fire+player-count gate) | Direction-exclusivity is structural, not coincidental |
| WPN (0x80) S→C NEVER / C→S ALWAYS | mid #8 stateupdate-validation (same gate) | Same anchor |
| 0x1C StateUpdate dirty-bit semantics (8 flags POS/DELTA/FWD/UP/SPD/CLK/SUB/WPN) | mid #8 stateupdate-validation | Byte-by-byte confirmed |
| Round-robin startIdx walks subsystem linked list | mid #11 stateupdate-subsystem-wire-format-validation | startIdx 0/2/6/8/10 reflect specific 2026-02-10 frame layout — keep `[trace]` tag for the specific indices |
| 0x06 PythonEvent / 0x0D PythonEvent2 (S→C only after server-side conversion) | leaf #14 pythonevent-wire-format-validation (FUN_0069F880 handles both, LOCAL-ONLY for receiver) | doc shows 0x0D C→S=12 with S→C=0 — engine converts/relays as 0x06 outbound |
| 0x07/0x08/0x09/0x0A/0x0B/0x11/0x12/0x1B = GenericEventForward (relayed identical) | mid #4 game-opcodes-validation (FUN_0069FDA0 group), leaf #16 set-phaser-level-protocol | Internal consistency of count table confirmed |
| 0x15 CollisionEffect C→S only (no S→C broadcast) | leaf #15 collision-effect-protocol | Count 5/5/0 matches |
| 0x17 DeletePlayerUI S→C only | leaf #17 delete-player-ui-validation | Count -/-/3 matches |
| 0x1D ObjNotFound S→C only | leaf #18 objnotfound-triad-validation | Count -/-/12 matches |
| 0x20/0x21/0x28 = checksum opcodes (ChecksumReq / ChecksumResp / ChecksumComplete) | mid #5 checksum-opcodes-validation | 0x28 = ChecksumComplete (doc says "Unknown") |
| 0x2A NewPlayer C→S only | mid #4 game-opcodes-validation | Count 2/2/0 matches; server reacts with 0x18 DeletePlayerAnim outbound |
| 0x2C ChatMessage via SendTGMessage (Python path) | mid #6 python-messages-validation | doc's 5/5/~15 reflects star-topology relay (each peer receives independently) |
| 0x32 framing: bits 12-0 length, bit 13 fragment, bit 14 ordered, bit 15 reliable | foundation #3 transport-layer-validation | Wire format byte-by-byte verified |
| Fragmented checksum response payload layout: `[fragIdx][totalFrags][innerOpcode][...]` for frag 0, `[fragIdx][continuation]` for frag N | foundation #3 transport-layer (FragmentMessage placement still has the head-vs-tail open question, but the receive-path layout in this doc is consistent with the layout the proxy decoder uses successfully) | Doc's example #32/#36/#37 round-2 trace matches |

---

## Per-section triage

### "Key Discovery: message_trace = RECEIVE path only"
**[Clar]** Currently load-bearing on the proxy hook target. Add anchor:
> *message_trace captures the TGMessage factory dispatch path (factory table at `DAT_009962d4`, TGMessage base at `FUN_006b83f0`); confirmed via `src/proxy/ddraw_main/message_factory_hooks.inc.c` line 22.* `[v5-validated 2026-05-28 via foundation #3 transport-layer.md]`

### "StateUpdate Flag Separation: SUB vs WPN"
**[Promote]** Both direction-exclusivity rules are now byte-anchored. Replace `[cross-source-2026-02-10 trace]` tag with:
> `[v5-validated 2026-05-28 via mid #8 stateupdate.md]`

The flag-distribution histograms (top-5 by direction) stay trace-tagged — they're session-specific occurrence counts.

### "Fragmented Reliable Messages"
**[Promote]** Type 0x32 bit layout and payload layout anchored. Replace tag with:
> `[v5-validated 2026-05-28 via foundation #3 transport-layer.md]`

Example with #32/#36/#37 timestamps stays trace-tagged.

### "PACKET_TRACE DECODER BUG"
**[H — historical]** Bug is **FIXED** in current proxy. Verified at `src/proxy/ddraw_main/packet_trace_and_decode.inc.c` lines 1184-1211 — decoder reads `fragIdx`/`fragTotal` before reading inner opcode, labels continuation fragments. Mark section:
> **Historical (resolved 2026-xx-xx)** — decoder now handles fragmentation correctly; documented here for the historical record. See `packet_trace_and_decode.inc.c` `isFragment` branch.

### "Corrected Opcode Cross-Reference Table"
**[Clar]** The table is internally consistent. Promote tags to `[v5-validated]` per anchor doc per row (see Confirmed claims table above for the mapping). One specific touch-up:
> Row `0x28 Unknown` → `0x28 ChecksumComplete` with anchor `[v5-validated 2026-05-28 via mid #5 checksum-opcodes.md]`

The 11 = 8 + 3 first-frags arithmetic on row 0x21 is internally consistent: message_trace deserializes the reassembled message (counts as 1 opcode each), while packet_trace sees 8 single-frame responses + 3 fragmented round-2 responses where only the first-fragment frames get counted (and were misdecoded — the latter is what produced the bug noted in the historical section above).

### "Newly Identified Opcodes"
**[H — historical, then promote]** All 5 were "newly identified" on 2026-02-10 but are now fully anchored. Mark section:
> **Historical** — these were newly identified during 2026-02-10 trace analysis. All are now anchored:
> - 0x2C ChatMessage → mid #6 python-messages.md
> - 0x11 RepairListPriority → mid #4 game-opcodes.md (GenericEventForward 0x07-0x12, 0x1B group, FUN_0069FDA0)
> - 0x12 SetPhaserLevel → leaf #16 set-phaser-level-protocol.md
> - 0x28 ChecksumComplete → mid #5 checksum-opcodes.md
> - 0x13 HostMsg (self-destruct request, FUN_006A01B0) → mid #4 game-opcodes.md

### "Post-ObjCreateTeam SUB Cycling Pattern"
**[Promote]** The cycling-after-ObjCreate behavior is anchored in mid #11. The specific startIdx 0/2/6/8/10 values reflect a particular linked-list layout for that ship's subsystems at that moment in the trace — they stay `[cross-source-2026-02-10 trace]` for the specific indices, but the algorithm tag is:
> `[v5-validated 2026-05-28 via mid #11 stateupdate-subsystem-wire-format.md]`

### "Implications for Our Proxy"
**[H — historical]** Per CLAUDE.md "Functional Multiplayer" status, proxy now sends `flags=0x20` with real subsystem health data via DeferredInitObject. Mark section:
> **Historical (resolved)** — at the time of this trace analysis, our proxy emitted `flags=0x00` because the headless engine had no subsystem data. This was resolved by DeferredInitObject (Python-driven ship creation that loads NIFs and populates `ship+0x284`). Current proxy sends `flags=0x20` with real subsystem health, matching stock-dedi. The `StateUpdate flags=0x20` line in CLAUDE.md's "What Works" section is the current ground truth.

---

## Cross-source tag promotions (full list)

For docwriter to apply in a single sweep:

| Original tag (or implicit trace claim) | Promote to | Section |
|---|---|---|
| Direction-exclusivity SUB/WPN table | `[v5-validated 2026-05-28 via mid #8 stateupdate.md]` | StateUpdate Flag Separation |
| Type 0x32 flags_len bit layout | `[v5-validated 2026-05-28 via foundation #3 transport-layer.md]` | Fragmented Reliable Messages |
| Fragmented payload layout (frag 0 head, frag N continuation) | `[v5-validated 2026-05-28 via foundation #3 transport-layer.md]` | Fragmented Reliable Messages |
| Opcode 0x07/0x08/0x09/0x0A/0x0B GenericEventForward relay parity | `[v5-validated 2026-05-28 via mid #4 game-opcodes.md, FUN_0069FDA0]` | Corrected Opcode Cross-Reference Table |
| Opcode 0x0D PythonEvent2 C→S-only | `[v5-validated 2026-05-28 via leaf #14 pythonevent-wire-format.md (LOCAL-ONLY at FUN_0069F880)]` | same |
| Opcode 0x11 RepairListPriority relay parity | `[v5-validated 2026-05-28 via mid #4 game-opcodes.md]` | same |
| Opcode 0x12 SetPhaserLevel relay parity | `[v5-validated 2026-05-28 via leaf #16 set-phaser-level-protocol.md]` | same |
| Opcode 0x13 HostMsg C→S-only | `[v5-validated 2026-05-28 via mid #4 game-opcodes.md (FUN_006A01B0 self-destruct)]` | same |
| Opcode 0x15 CollisionEffect C→S-only | `[v5-validated 2026-05-28 via leaf #15 collision-effect-protocol.md]` | same |
| Opcode 0x17 DeletePlayerUI S→C-only | `[v5-validated 2026-05-28 via leaf #17 delete-player-ui-wire-format.md]` | same |
| Opcode 0x19 TorpedoFire / 0x1A BeamFire / 0x1B TorpTypeChange relay parity | `[v5-validated 2026-05-28 via mid #4 game-opcodes.md]` | same |
| Opcode 0x1C StateUpdate direction asymmetry (SUB host-only) | `[v5-validated 2026-05-28 via mid #8 stateupdate.md]` | same |
| Opcode 0x1D ObjNotFound S→C-only | `[v5-validated 2026-05-28 via leaf #18 objnotfound-requestobj-enterset-wire-format.md]` | same |
| Opcode 0x21 ChecksumResp / 0x20 ChecksumReq / 0x28 ChecksumComplete | `[v5-validated 2026-05-28 via mid #5 checksum-opcodes.md]` | same |
| Opcode 0x2A NewPlayer C→S-only | `[v5-validated 2026-05-28 via mid #4 game-opcodes.md (NewPlayerInGameHandler 0x006A1E70)]` | same |
| Opcode 0x2C ChatMessage Python path | `[v5-validated 2026-05-28 via mid #6 python-messages.md]` | same |
| Post-ObjCreateTeam SUB cycling algorithm (startIdx walks linked list) | `[v5-validated 2026-05-28 via mid #11 stateupdate-subsystem-wire-format.md]` | Post-ObjCreateTeam SUB Cycling Pattern |
| Newly Identified Opcodes (entire section) | mark as historical, then per-row anchor as above | Newly Identified Opcodes |

The session-specific count numbers (10,459 C→S StateUpdates; 19,997 S→C StateUpdates; histogram top-5; per-opcode totals) all stay `[cross-source-2026-02-10 trace]` — they are valid observations of one specific 33.5-minute session.

---

## Sections to mark `Historical`

1. **PACKET_TRACE DECODER BUG** — bug fixed; decoder at `packet_trace_and_decode.inc.c` lines 1184-1211 now extracts `fragIdx`/`fragTotal` cleanly before the inner opcode read.
2. **Newly Identified Opcodes** — all 5 are now anchored in mid/leaf docs (per the promotion list above).
3. **Implications for Our Proxy** — proxy now sends `flags=0x20` with real subsystem health via DeferredInitObject; the predicted "direct trigger for client disconnect" was confirmed and then resolved.

---

## Anchor table (for docwriter frontmatter)

```yaml
validated: 2026-05-28
binary:
  fingerprint: STBC.exe (5,894 KB)
status: partial   # promote to verified after tag-promotion + 3 historical-marks land
companions:
  - docs/protocol/wire-format-spec.md           # foundation #1
  - docs/protocol/transport-layer.md            # foundation #3
  - docs/protocol/game-opcodes.md               # mid #4
  - docs/protocol/checksum-opcodes.md           # mid #5
  - docs/protocol/python-messages.md            # mid #6
  - docs/protocol/tgmessage-routing.md          # mid #7
  - docs/protocol/stateupdate.md                # mid #8
  - docs/protocol/stateupdate-subsystem-wire-format.md  # mid #11
  - docs/protocol/pythonevent-wire-format.md    # leaf #14
  - docs/protocol/collision-effect-protocol.md  # leaf #15
  - docs/protocol/set-phaser-level-protocol.md  # leaf #16
  - docs/protocol/delete-player-ui-wire-format.md  # leaf #17
  - docs/protocol/objnotfound-requestobj-enterset-wire-format.md  # leaf #18
evidence:
  - claim: message_trace = TGMessage factory dispatch (inbound-only)
    address: DAT_009962d4 (factory table) + FUN_006b83f0 (type 0x32 TGMessage)
    confidence: high
    via: foundation #3 transport-layer.md
  - claim: SUB (0x20) S→C-only / WPN (0x80) C→S-only direction exclusivity
    address: FUN_005B17F0 (Ship_WriteStateUpdate, host-side SUB emit)
    confidence: high
    via: mid #8 stateupdate.md
  - claim: opcode 0x28 = ChecksumComplete (not "Unknown")
    address: registration string at 0x0095a0cc "MultiplayerGame :: ChecksumCompleteHandler"
    confidence: high
    via: mid #5 checksum-opcodes.md
  - claim: type 0x32 bit layout (13-bit length, bit 13 fragment, bit 14 ordered, bit 15 reliable)
    address: foundation #3 transport-layer.md (byte-by-byte verified)
    confidence: high
    via: foundation #3 transport-layer.md
  - claim: post-ObjCreateTeam SUB cycling algorithm (startIdx walks linked list)
    address: mid #11 stateupdate-subsystem-wire-format.md (round-robin algorithm verified)
    confidence: high
    via: mid #11 stateupdate-subsystem-wire-format.md
```

---

## Open questions

1. **Opcode 0x35 GameState / 0x37 PlayerRoster S→C-only labels** — doc lists these in the S→C-only block (lines 124-125 of the doc). Mid #6 python-messages.md confirms 0x35 = MISSION_INIT_MESSAGE (game config) and 0x37 = SCORE_MESSAGE (full score sync), both via SendTGMessage Python path. The doc's "GameState" / "PlayerRoster" labels are functionally accurate but slightly off from the binary's registration strings. **[Clar]** — recommend docwriter sync these labels to the mid #6 names (MISSION_INIT_MESSAGE / SCORE_MESSAGE) or note as informal labels.

2. **0x21 ChecksumResp count arithmetic** — `11 = 8 + 3 first-frags` works only because the message_trace counted reassembled 0x21 messages while packet_trace counted post-decryption frames. Worth a one-line note: "message_trace sees opcode after reassembly; packet_trace sees opcode after decryption" so readers understand why the counts differ.

3. **0x0D PythonEvent2 path through engine** — doc shows C→S=12 / S→C=0. Game-opcodes-validation memo noted "0x06+0x0D both PythonEvent → FUN_0069f880 LOCAL-ONLY". If FUN_0069F880 is LOCAL-ONLY and the engine doesn't relay 0x0D, what happens to those 12 received events? Either (a) the engine drops them after the local apply step, or (b) they re-emit as 0x06 outbound (which would inflate the S→C 0x06=251 count). Worth a note for future analysis. **[OQ]** — not blocking for this validation.

---

## Cascade to family-close batch

Now that protocol leaf #22 is validated, the protocol family is **22/22 complete**. Suggested CLAUDE.md updates for the family-close commit:

1. Mark all protocol docs as `[v5-validated 2026-05-28]` in the Documentation Index.
2. Add the message-trace-vs-packet-trace.md to the index entry list (it's currently there as "Stock-dedi opcode cross-reference" — confirm wording matches "Cross-source trace analysis" once promoted).
3. Note in the protocol README that message-trace-vs-packet-trace is the **historical cross-check** doc — useful for future trace comparisons but not load-bearing for OpenBC spec because all its findings are now anchored in the per-opcode docs.

No source-code changes needed (proxy decoder bug already fixed; flags=0x20 emission already shipped via DeferredInitObject).

---

## Pattern note (for future cross-trace docs)

This doc demonstrates a useful pattern: **paired-trace differential analysis** (instrumenting two different hook points and diffing the counts to identify direction/routing characteristics). Specifically:

- **Hook A**: TGMessage factory deserialize (catches inbound, post-decrypt, post-reassemble)
- **Hook B**: sendto/recvfrom packet trace (catches both directions, pre-decrypt at wire layer)

Diff (A) vs (B-incoming-direction) catches:
- Server-generated messages (in B-outbound but not A)
- Direction-exclusive opcodes (count differential signals direction asymmetry like SUB/WPN)
- Decoder bugs (B's count off by fragmentation-related amounts when A is reassembled-correct)

This pattern is worth repeating for future protocol validation when both hook points are available. The 2026-02-10 session is the canonical example.
