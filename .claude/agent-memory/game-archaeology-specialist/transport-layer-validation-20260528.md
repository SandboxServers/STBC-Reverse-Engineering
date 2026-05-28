---
name: transport-layer-validation-20260528
description: Protocol doc #3 (transport-layer). AlbyRules cipher transform LOCATED (Encrypt 0x006c2490, Decrypt 0x006c2520) - resolves long-standing open question. Both call AlbyRulesCipher_InitKey on EVERY packet (no streaming state). SendPacket 0x006b9870 and ReceivePacket 0x006b95f0 confirmed but had to be CREATED in Ghidra (auto-analysis missed them - no plain CALL xrefs because they are vtable[27]/vtable[28] of TGWinsockNetwork base). 7 transport types factory registration confirmed exactly. Seq counter offsets in doc (+0x98/+0xA8) are WRONG - actual offsets are peer+0x26/+0x2A.
metadata:
  type: project
---

# Transport-Layer Doc Validation — 2026-05-28

Phase 1-3 of v5 campaign for `docs/protocol/transport-layer.md`. ~140 load-bearing claims, ~135 confirmed, 4 corrections, 1 area of concern, 0 dropped.

## Why this matters

This is the foundation doc for everything on the wire. Until now, "AlbyRules cipher transform" was an open question in the foundation snapshot. The cipher Encrypt/Decrypt functions are now located, annotated, and named in Ghidra. Every higher-level protocol doc transitively rests on this dig.

## Address book — anchored this session

| Function | Address | Renamed to | Plate? |
|---|---|---|---|
| TGWinsockNetwork ctor | 0x006B3A00 | TGWinsockNetwork_Ctor | — |
| HostOrJoin | 0x006B3EC0 | TGWinsockNetwork_HostOrJoin | — |
| QueueMessageForPeer (per-peer enqueue) | 0x006B5080 | TGWinsockNetwork_QueueMessageForPeer | — |
| SendOutgoingPackets | 0x006B55B0 | TGWinsockNetwork_SendOutgoingPackets | — |
| ProcessIncomingPackets | 0x006B5C90 | TGWinsockNetwork_ProcessIncomingPackets | — |
| HandleReliableReceived (ACK producer) | 0x006B61E0 | TGWinsockNetwork_HandleReliableReceived | yes |
| HandleACK (ACK consumer) | 0x006B64D0 | TGWinsockNetwork_HandleACK | — |
| EnqueueReceived (seq window + reassemble dispatch) | 0x006B6AD0 | TGWinsockNetwork_EnqueueReceived | — |
| Fragment reassembler | 0x006B6CC0 | TGMessage_ReassembleFragments | — |
| TGMessage base ctor | 0x006B82A0 | TGMessage_Ctor (existing) | — |
| TGMessage base dtor | 0x006B8320 | TGMessage_Dtor (was TGBufferStream_Dtor; CORRECTED) | — |
| TGMessage base Serialize | 0x006B8340 | TGBufferStream_Serialize (NOT corrected; sticky pre-cascade name) | — |
| FragmentMessage (vtable[7]) | 0x006B8720 | TGBufferStream_Fragment (NOT corrected; sticky pre-cascade name) | — |
| TGMessage type-0x32 factory | 0x006B83F0 | TGMessage_Factory_Type32 | — |
| ReceivePacket | 0x006B95F0 | TGWinsockNetwork_ReceivePacket | yes |
| SendPacket | 0x006B9870 | TGWinsockNetwork_SendPacket | yes |
| TGBootMessage ctor | 0x006BAC70 | TGBootMessage_Ctor | — |
| TGDataMessage ctor (type 0x00) | 0x006BC5B0 | TGDataMessage_Ctor | — |
| TGHeaderMessage ctor (type 0x01, ACK) | 0x006BD120 | TGHeaderMessage_Ctor | — |
| TGHeaderMessage_Serialize | 0x006BD190 | TGHeaderMessage_Serialize | yes |
| TGConnectMessage ctor (type 0x02) | 0x006BDC40 | TGConnectMessage_Ctor | — |
| TGConnectAckMessage ctor (type 0x03) | 0x006BE730 | TGConnectAckMessage_Ctor | — |
| TGDisconnectMessage ctor (type 0x05) | 0x006BF2E0 | TGDisconnectMessage_Ctor | — |
| AlbyRules cipher InitKey | 0x006C2280 | AlbyRulesCipher_InitKey | yes |
| AlbyRules cipher Step (LFSR-like) | 0x006C22F0 | (unchanged) | — |
| AlbyRules cipher Encrypt | 0x006C2490 | AlbyRulesCipher_Encrypt | yes |
| AlbyRules cipher Decrypt | 0x006C2520 | AlbyRulesCipher_Decrypt | yes |

The two newly-named **SendPacket** and **ReceivePacket** had to be created via `create_function` — Ghidra auto-analysis had not disassembled them. The reason is they have NO direct CALL xrefs: they are vtable[27] and vtable[28] of TGWinsockNetwork's base class, dispatched through `(**(code **)(*param_1 + 0x6C))(...)` and `(**(code **)(*param_1 + 0x70))(...)` in SendOutgoingPackets/ProcessIncomingPackets. Same pattern as MpgameHandleMessage (registration-data-only xref).

## CORRECTIONS to the doc

1. **Sequence counter offsets** — doc says `peer + 0x98` (types <0x32) and `peer + 0xA8` (types >=0x32). Actual offsets per QueueMessageForPeer (0x006B5080):
   - Type < 0x32, reliable: `peer + 0x26` (16-bit)
   - Type >= 0x32, reliable: `peer + 0x2A` (16-bit)
   - Receive-side window check uses `peer + 0x24` and `peer + 0x28`.
   - The doc's +0xA8 may have come from confusing `network+0xA8 = 0x8000` (a constant init in TGWinsockNetwork_Ctor, likely a seq-window threshold or max-seq).

2. **TGBufferStream Appendix A field offsets in the doc** describe a class that is NOT the 0x40-byte TGMessage (vtable 0x008958D0). The Appendix A class has buf at +0x1C, capacity +0x20, cursor +0x24, bookmark +0x28, bit-mask +0x2C — that is the SWIG TGBufferStream class (vtable 0x00895C58, ctor FUN_006CEFE0, size 0x30) per [[stream-primitives-validation-20260528]]. The doc would benefit from explicitly noting this is the *bit-packing primitive stream class*, distinct from TGMessage. Cross-link to stream-primitives.md.

3. **AlbyRules cipher claims** in the doc encryption section are accurate at the **observation** level (byte 0 skipped, called on buf+1 with len-1), but the cipher transform function was unlocated. Now located: Encrypt at 0x006C2490 (vtable[1]), Decrypt at 0x006C2520 (vtable[2]) of the cipher object at TGWinsockNetwork+0xF0. Cipher class vtable at 0x008958C0. Doc should add these addresses + note re-keying happens on every packet (no streaming state).

4. **NetFile dispatcher opcode range** — doc says "0x20-0x27". Actual cases in FUN_006A3CD0 are 0x20, 0x21, 0x22, 0x23, 0x25, 0x27 (NO 0x24 or 0x26). Range is correct as bounds but not contiguous. Cross-reference docs/protocol/checksum-opcodes.md for the actual opcode map.

## CONFIRMED claims (high confidence)

- **Raw UDP packet structure** at lines 22-27: peer_id byte 0 (signed-char read in ProcessIncomingPackets), msg_count byte 1, then messages. Confirmed in TGWinsockNetwork_ProcessIncomingPackets at 0x006B5C90 (line `iStack_1c = (int)*pcStack_4; pbVar10 = pcStack_4 + 2; for cVar4 = pcStack_4[1]`).
- **Factory table at DAT_009962D4** indexed by `*pbVar10 * 4`. All 7 type registrations confirmed (FUN_006B8290, FUN_006BC5A0, FUN_006BD110, FUN_006BDC30, FUN_006BAC60, FUN_006BE720, FUN_006BF2D0) write to slots at the predicted offsets (type * 4 from DAT_009962D4).
- **Type 0x32 wire format** lines 56-90. Verified byte-by-byte against TGBufferStream_Serialize (0x006B8340) and TGMessage_Factory_Type32 (0x006B83F0). bit 13 = is_fragment, bit 14 = ordered, bit 15 = reliable, low 13 bits = total length. flag_hi values 0x80/0x81/0xA0/0xA1/0x00 all derive from these bits + length bit 8.
- **Type 0x01 ACK wire format** lines 117-127: 4 or 5 bytes, [type=0x01][seq:2][flags:1][optional frag_idx:1]. flags bit 0 = is_fragment, bit 1 = is_below_0x32. Verified in TGHeaderMessage_Serialize (0x006BD190).
- **Fragment reassembly** lines 137-158. 256-entry index array, fragment 0 carries total_frags at +0x38, all-fragments-present check via fragment 0's +0x38. Verified in TGMessage_ReassembleFragments (0x006B6CC0).
- **TGMessage object layout** lines 174-196 (and the more complete restated version 299-323): +0x14 seq, +0x38 total_fragments, +0x39 fragment_index, +0x3A reliable, +0x3B ordered, +0x3C is_fragment. All confirmed by serializer + deserializer + reassembler + ACK-handler cross-references.
- **TGMessage base vtable (0x008958D0)** lines 204-213. All 8 slots confirmed by reading the vtable bytes at 0x008958D0: [0x006B9430, 0x006B82F0, 0x006B8340, 0x006B9440, 0x006B9450, 0x006B8640, 0x006B8610, 0x006B8720]. Doc claim matches.
- **Three C++ dispatchers** lines 226-242. NetFile at 0x006A3CD0 ✓, MpgameHandleMessage at 0x0069F2A0 ✓, MultiplayerWindow at 0x00504C10 with `+0xb0` gate flag ✓. The gate at MultiplayerWindow IS `this+0xB0 != 0` not 0xB0=0.
- **Below32 ACK mechanism** lines 161-170 + the network-protocol-analyst memory. Verified at three sites:
  - SET in HandleReliableReceived (0x006B61E0): `*(bool *)(iVar6 + 0x40) = iVar5 < 0x32;`
  - READ in HandleACK (0x006B64D0): `((bool)cVar1 != iVar3 < 0x32) goto next;`
  - WIRE in TGHeaderMessage_Serialize (0x006BD190): `if (this+0x40 != 0) flags |= 2;`
- **AlbyRules cipher key** at 0x0095ABB4 — confirmed: s_AlbyRules__0095abb4 is the literal "AlbyRules!" string copied into cipher state by AlbyRulesCipher_InitKey.
- **GameSpy bypass** — `if (*buf != '\\')` in ReceivePacket skips cipher for buf[0] == 0x5C. Confirmed at 0x006B9706.
- **Self-send local-queue loopback** — additional finding not in doc: SendPacket has a Path A where if dest_addr == this+0x1C (own address), the packet is queued at this+0x33C..+0x340 without going through OS UDP. ReceivePacket drains this queue alternately with real recvfrom (via toggle at this+0x344). The host gets its own packets without OS round-trip.

## NEW factual additions to fold into the doc

- **MTU is 0x400 = 1024 bytes**, not 1400. Set in TGWinsockNetwork_Ctor at network+0xAC. ReceivePacket allocates `this+0xAC` bytes for the recv buffer; SendOutgoingPackets uses `this+0x2B` (same value = 0x400) as the packet-pack buffer size.
- **Connection state machine**: states 2 (HOSTING), 3 (JOINING), 4 (IDLE/READY). State 1 may exist but was not observed. Initial state set in ctor: `param_1[5] = 4;`. Transitions in HostOrJoin (0x006B3EC0): 4 → 2 (host path with error_post 0x60002) or 4 → 3 (join path). Doc mentions "states 1, 2, 3, 4" but states 1 needs evidence.
- **SendPacket has TWO paths** (loop-back self-send + real network send). Doc should mention this.
- **Cipher is re-keyed per packet** (no streaming state across packets). This is the property that makes the cipher robust to UDP packet loss and reordering — client and server CANNOT desync. Worth highlighting.
- **Cipher vtable at 0x008958C0**: slot 0 = dtor (0x006B8220), slot 1 = Encrypt (0x006C2490), slot 2 = Decrypt (0x006C2520), then a float at +0x0C (0x41700000 = 15.0).
- **All 6 TGMessage subclass ctors verified end-to-end**. TGConnectMessage does NOT set +0x3A=1 (unreliable by default). TGConnectAckMessage, TGBootMessage, TGDisconnectMessage, TGDataMessage all set reliable+ordered. TGBootMessage additionally clears [0x10]=field_0x40 (the is_below_0x32 flag, irrelevant here since it has its own type tag).

## Open questions / hedges

1. **FragmentMessage total_fragments placement** (medium confidence): the existing doc says "Fragment 0 gets `+0x38 = total_fragment_count` (set AFTER the loop completes)". But reading TGBufferStream_Fragment (0x006B8720), the linked-list manipulation is intricate and `*(undefined1 *)(*piVar8 + 0x38) = (undefined1)iStack_38` after the loop targets what appears to be the LAST inserted message, not Fragment 0. The fact that it works in practice (we have working packet traces) means either (a) the linked list logic IS rewinding to head (which I can't fully trace) or (b) my read of the cleaned-up decompilation is wrong. The deserializer side is unambiguous: it reads `aiStack_400[0]+0x38` for total_frags, i.e., Fragment 0 owns the byte ON THE WIRE. So the sender-side code MUST put it on whatever clone has `+0x39 == 0`. Recommend: emulate this function with a synthetic 3-fragment payload to verify.

2. **Connection state 1**: doc claims states 1, 2, 3, 4 exist. Found 2, 3, 4 by direct read of HostOrJoin. State 1 may be a sub-state during connect handshake; needs another investigation pass on the connection-management functions (006B8B30 family, observed in callees of ctor).

3. **vtable[3] and vtable[4] of TGMessage** (slots at 0x006B9440 and 0x006B9450). Doc says "Unknown (returns 0)" / "Unknown". Not investigated this session. Likely Save/Load or GetAge/IsExpired given the surrounding retry-state context.

4. **NetFile event registration** at `0x60001` (doc claim line 230). The dispatcher posts event `0x60002` from inside (visible in case 0x25 handler). The `0x60001` registration site is not anchored here; needs RegisterHandler call site cross-check.

5. **SendOutgoingPackets MTU constraint sharing**: param_1[0x2B] (the pack buffer size) and param_1[0xAC] (the recv buffer size) are both initialized to 0x400 in the ctor. Are they ALWAYS equal, or could they diverge under runtime config? Could affect fragmentation thresholds.

## Cross-doc impact

- **wire-format-spec.md** (already validated): consistent — no new corrections required.
- **stream-primitives.md** (already validated): this doc's Appendix A is duplicate-but-inferior coverage of stream-primitives.md's class B. Recommend deleting Appendix A and replacing with a 2-line cross-link.
- **checksum-opcodes.md**: should be cross-linked from this doc as the canonical source for NetFile opcode range (0x20-0x27 minus 0x24/0x26).
- **networking/alby-rules-cipher-analysis.md**: companion doc — should now be updated with Encrypt/Decrypt addresses and re-key-per-packet observation. (Out of scope for this validation pass but flag as next-step.)
- **networking/network-protocol.md**: should reference TGWinsockNetwork_Ctor and the state machine.
- **CLAUDE.md Key Globals** table includes `0x0097E238 | TopWindow/MultiplayerGame ptr` — that's a known drift per snapshot. NOT this doc's concern; doc transport-layer.md never cites 0x0097E238.

## Confidence rollup (v5)

- High: 7 transport types, factory registration mechanics, type 0x32 wire format, type 0x01 wire format, fragment reassembly, TGMessage layout, vtable, below32 ACK semantics, AlbyRules cipher location/algorithm, GameSpy bypass, packet structure peer_id/msg_count, MTU 1024.
- Medium: connection states (3 of claimed 4 verified directly; state 1 unverified), self-send loop-back path (observed via decompile but no packet trace to confirm activity), FragmentMessage total_fragments placement (cleaned-up decompile is ambiguous).
- Low: nothing — no claim in the doc was promoted speculatively this session.

## What I would do next

1. Emulate TGBufferStream_Fragment with a synthetic 3-fragment input to settle the total_fragments placement question.
2. Sweep the RegisterHandler sites to confirm NetFile's `0x60001` registration.
3. Locate connection state 1 (likely in 006B8C30 or 006B8B30 family — these are the TGConnectMessage send-side helpers).
4. Audit stream-primitives.md Class B (the wire-container at 006B82A0) since this validation has shown the doc has it correct but the TGMessage / TGBufferStream naming is sticky in pre-cascade plate comments at 0x006B8340 and 0x006B8720.
