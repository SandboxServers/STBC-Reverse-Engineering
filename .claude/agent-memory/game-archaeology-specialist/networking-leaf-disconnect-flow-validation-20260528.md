---
name: networking-leaf-disconnect-flow-validation-20260528
description: v5 validation of docs/networking/disconnect-flow.md — 4 detection paths (not 3), peer offsets +0x2C/+0x30 SWAPPED, FUN_006b6a20/FUN_006b6a70 SWAPPED labeling, dispatcher resolves type 4=Boot/type 5=Disconnect, cross-doc resolves enterset/disconnect handler mislabeling.
metadata:
  type: project
---

# Networking Leaf #10 — disconnect-flow.md v5 Validation

**Doc**: `docs/networking/disconnect-flow.md` (534 lines)
**Family**: networking leaf (10th in family)
**Validation date**: 2026-05-28
**Program**: STBC.exe (image base 0x00400000)

## Bottom line

Doc is structurally correct (peer-deletion convergence at FUN_006b75b0, three converging paths, cleanup cascade via 0x60005 event) but has **5 material corrections** spanning section header mislabeling, peer-offset swaps, and a missed 4th convergence path. Suggested v5 status: `partial` — needs republication after fixes. Also **resolves a cross-doc inconsistency** between disconnect-flow and the recent v5 objnotfound-requestobj-enterset doc.

## Corrections (C)

### C1 (CRITICAL) — Section 1.2 swaps FUN_006b6a20 ↔ FUN_006b6a70

Doc Section 1.2 header says "**Handler**: FUN_006b6a20 (dispatched from FUN_006b5f70, type 5 case)". But the pseudocode shown is **labeled `FUN_006b6a70` in its own comment block** and matches the **actual body of FUN_006b6a70** (special-case `peerID==-1` → set field_0x10d=1, field_0x14=2; etc.).

**Ground truth** (verified from FUN_006b5f70 disassembly at 0x006b60ab-0x006b60c0 switch dispatch):
- **case 4** (TGBootMessage::GetType returns 0x04 at 0x006bb830) → `FUN_006b6a70(msg, peer)` — handles **host kick/boot reception**
- **case 5** (TGDisconnectMessage::GetType returns 0x05 at 0x006bfe70) → `FUN_006b6a20(msg, peer)` — handles **graceful disconnect**

Bodies differ materially:
- **FUN_006b6a70** (type 4, boot reception): if iVar2==-1 → field_0x10d=1, field_0x100=msg+0x40, field_0x14=2, return; else FUN_006b75b0; if iVar2==field_0x18 → field_0x10d=1, field_0x100=msg+0x40
- **FUN_006b6a20** (type 5, graceful disconnect): if iVar2==field_0x18 → field_0x10d=1; else FUN_006b75b0; if iVar2==field_0x20 → field_0x10d=1; if field_0x10e!=0 → FUN_006b51e0(msg)

**Why this matters**: Doc Section 1.2 attributes the pseudocode behavior (with -1 special case for "host disconnected from us") to the GRACEFUL disconnect path. Actually that -1 sentinel applies to the BOOT path (server kicked us). For genuine graceful disconnect (type 5), there is no -1 sentinel — it just deletes the named peer; if that peer was the local host-pointer (+0x18), also flag shutdown; if it was the peer-self (+0x20), also flag shutdown; then optionally relay (+0x10e gate, calls FUN_006b51e0 broadcast).

The doc's Section 1.2 also misses the FUN_006b6a20-specific **broadcast-on-disconnect relay** via FUN_006b51e0 (gated by `field_0x10e`). When this fires, a graceful disconnect causes the receiving peer to forward the disconnect message to all other peers.

### C2 (CRITICAL) — peer+0x2C and peer+0x30 offsets SWAPPED

Doc Section 1.1 peer field table:
- "+0x2C — Keepalive send timestamp"
- "+0x30 — Last receive timestamp"

**Ground truth**:
- **+0x2C is lastRecvTime**: written `*(int *)(iVar11 + 0x2c) = DAT_0099c6bc` in ProcessIncomingPackets on **every received packet** (0x006b5e63). Compared against `WSN+0xB8` (timeout threshold) in FUN_006b4560 cleanup loop: `local_108 - *(float *)(iVar3 + 0x2c) > WSN+0xB8` (0x006b48ae). The doc's own pseudocode in Section 1.1 says `currentTime - peer+0x30 > connectionTimeout`, but the actual code uses **peer+0x2C** for the timeout check.
- **+0x30 is lastSendTime**: written `*(undefined4 *)(iVar1 + 0x30) = DAT_0099c6bc` in FUN_006b51e0 (broadcast send). Compared against `_DAT_0088bd58` (keepalive interval 5.0f) in FUN_006b4560 connect-send loop: `_DAT_0088bd58 < local_108 - *(float *)(iVar8 + 0x30)`.

So the two offsets are inverted in the doc. This also means the doc's Section 1.1 pseudocode `compares currentTime - peer+0x30 > connectionTimeout` is wrong — actual code compares against **peer+0x2C**.

### C3 — Missed 4th convergence path (ProcessIncomingPackets connect-clobber)

Doc Overview enumerates exactly 3 detection paths. **4th path exists**: `TGWinsockNetwork_ProcessIncomingPackets` at 0x006b5d97 calls `FUN_006b75b0(peer+0x18)` followed by `(**(code **)(*WSN + 0x74))(peer+0x18)` in the TGConnectMessage (type 3) handling — when a new connect-message arrives from an address already in the peer table but with a stale connection ID, the engine deletes the stale peer entry before re-adding. This is a peer-rendezvous clobber that bypasses both the 45s timeout and the type 5 graceful path.

The `xrefs_to FUN_006b75b0` confirms 4 callers (not 3):
1. 0x006b4898 in FUN_006b4560 (timeout path — doc covers)
2. 0x006b6a46 in FUN_006b6a20 (graceful path — doc covers but mislabels)
3. 0x006b6aaa in FUN_006b6a70 (boot path — doc covers but mislabels)
4. **0x006b5d97 in TGWinsockNetwork_ProcessIncomingPackets (connect-clobber — doc MISSES)**

### C4 — Section 3.2 `0x006a0a20` claim is correct, **resolves** cross-doc conflict

Doc Section 3.2 claims 0x006a0a20 is the DisconnectHandler (empty stub for 0x60003). The recent v5 plate comment at 0x006a0a20 (added during objnotfound-requestobj-enterset validation, recorded in memory `objnotfound-triad-validation-20260528.md`) names this `MultiplayerGame__EnterSetEventHandler`.

**Ground truth from MultiplayerGame_Ctor (0x0069e590) and FUN_0069efe0**:
- `FUN_0069efe0` binds address 0x006a0a20 → string `"MultiplayerGame :: DisconnectHandler"` (at 0x0095a1f0)
- `MultiplayerGame_Ctor` at 0x0069e62b registers event 0x60003 with the "DisconnectHandler" string

**Conclusion**: 0x006a0a20 IS the DisconnectHandler (empty stub), and the disconnect-flow doc's Section 3.2 is CORRECT. The earlier v5 plate naming it "EnterSetEventHandler" is **wrong** — it should be reverted. The actual EnterSetHandler is at 0x006a07d0 (also confirmed via FUN_0069efe0 binding 0x006a07d0 → "EnterSetHandler" string at 0x0095a0a8).

This is a **doc-vs-doc conflict resolution** finding: trust disconnect-flow.md Section 3.2 over the recent v5 plate on 0x006a0a20.

### C5 — Doc Section 6.1 "29 Handlers" undercount + several handlers registered in DIFFERENT ctors

The "Registered in the constructor via FUN_006db380" claim in Section 6.1 needs nuance. Per FUN_0069efe0's binding table, 30 handler-string pairs are bound there (not 29). But MultiplayerGame_Ctor (0x0069e590) calls FUN_006db380 with event IDs across many distinct events — and the doc's table mixes them with handlers registered elsewhere (e.g., ET_BOOT_PLAYER 0x8000F6 at 0x005047d9 is in `FUN_00504770`, the MultiplayerWindow ctor — doc DOES correctly attribute this to MultiplayerWindow in Section 1.3).

Specifically the table lists `0x00506170` BootPlayerHandler under MultiplayerGame, but it's actually registered by **MultiplayerWindow** (per 0x005047d9 push of 0x8000F6). The doc's prose in 1.3 says "MultiplayerWindow BootPlayerHandler" — correct — but the Section 6.1 table groups it under MultiplayerGame, which is misleading.

## Clarifications (Clar)

### Clar 1 — DAT_0088bd58 confirmed = 5.0f, next 4 bytes = -5.0f

Doc says keepalive interval is 5.0 seconds (DAT_0088bd58). Bytes at 0x0088bd58: `00 00 a0 40` = 0x40A00000 = **5.0f** (CONFIRMED). The trailing `00 00 a0 c0` = -5.0f. Doc's "Correction: Earlier documentation stated 12 second" note is correct as a clarification.

### Clar 2 — WSN+0xB8 is the timeout threshold (not "connectionTimeout" abstract)

Doc Section 1.1 references "connectionTimeout" abstractly. Actual code at 0x006b48ae: `*(float *)((int)param_1 + 0xb8) < local_108 - *(float *)(iVar3 + 0x2c)`. So **WSN+0xB8 is the per-instance timeout threshold** (45.0s claimed; not directly verified here but stated as set in WSN ctor). Worth naming explicitly in the doc.

### Clar 3 — FUN_006b9f40 (RemovePeerAddress) is NOT directly called from FUN_006b75b0

Doc Section 7.1 covers PatchRemovePeerAddress. RemovePeerAddress is called from **WSN vtable slot 0x74** (the FinalizePeerCleanup vfn at 0x006b9e40, called from ProcessIncomingPackets at 0x006b5da4 and FUN_006b7660-adjacent code), NOT directly from FUN_006b75b0. The actual deletion sequence is:

1. **FUN_006b75b0** marks peer disconnecting (peer+0xBC=1)
2. **WSN vtable[0x74]** (vfn at 0x006b9e40) runs later — binary-searches for peer-id, calls RemovePeerAddress(WSN, peer+0x1C IP), then calls FUN_006b7660 (array splice + dtor)

The 0x006b9e40 vfn is dispatched via `(**(code **)(*param_1 + 0x74))(peerID)`. Doc Section 2's claim "Actual removal from the peer array happens later in FUN_006b7660 (called during the next WSN tick cycle)" is approximately right but doesn't name the wrapping vfn.

### Clar 4 — FUN_006b7590 "fallback" is actually a per-id flag clear

Doc Section 2 names FUN_006b7590 as "alternative cleanup path". Actual body: writes byte 0 to `WSN + 0x111 + peerID` (bounds: 1 < peerID < 0x7F). This clears a **per-peer bitmap flag** (probably "is-connecting"). Not really an "alternative cleanup" — it's a narrow state-machine flag reset that always runs at the fallback path (when peerID can't be found in the main array). Worth a one-liner clarification.

## Removals (R)

None — no claims need outright deletion.

## Open Questions (OQ)

### OQ1 — Wire trace decode in Section 9.2: 9-byte disconnect payload exceeds 5-byte shutdown copy

FUN_006b4060 (WSN shutdown sender) constructs a TGDisconnectMessage with `TGMessage_BufferCopy(&local_8, 5)` — copies 5 bytes (1-byte param_1[6] + 4-byte param_1[7]). But the captured packet (Section 9.2) shows 9 bytes of payload `0A C0 02 00 02 0A 0A 0A EF` after the type byte. The wire trace decoder may be misinterpreting the type byte location, OR the disconnect message header has its own framing layered on top. Worth a follow-up decode.

### OQ2 — Section 9.3 "Server retransmits ACK seq=2" 7 times: gating mechanism unverified here

This is consistent with the ack-outbox-deadlock leaf #9 findings but not re-verified here.

## Hindering Issues (H)

None blocking — all key functions decompile cleanly, all addresses resolve.

## Evidence anchor inventory

| Claim | Address | Status |
|-------|---------|--------|
| FUN_006b75b0 marks peer+0xBC=1, peer+0xB8=currentTime, posts 0x60005 | 0x006b75b0 | BYTE-confirmed via disasm 0x006b7607 (`MOV [ESI+0x10],0x60005`), 0x006b7629 (`MOV byte [EDI+0xBC],1`), 0x006b7636 (`FSTP [EDI+0xB8]`) |
| FUN_006b75b0 allocates 0x2C bytes via FUN_00717b70(0x2C) | 0x006b75e0 | BYTE-confirmed (`PUSH 0x2C`) |
| FUN_006b75b0 fallback to FUN_006b7590 | 0x006b7643-0x006b7646 | BYTE-confirmed (`CALL 0x006b7590`) |
| Dispatcher FUN_006b5f70 case 4 → FUN_006b6a70 | 0x006b60c0 region | DECOMP-confirmed |
| Dispatcher FUN_006b5f70 case 5 → FUN_006b6a20 | 0x006b60c5 region | DECOMP-confirmed |
| TGBootMessage::GetType returns 0x04 | 0x006bb830 | BYTE-confirmed (`MOV EAX,0x4`) |
| TGDisconnectMessage::GetType returns 0x05 | 0x006bfe70 | BYTE-confirmed (`MOV EAX,0x5`) |
| FUN_006b4560 iterates peer array via WSN+0x2C/+0x30 | 0x006b483a-0x006b489e | DECOMP-confirmed |
| FUN_006b4560 timeout check `WSN+0xB8 < currentTime - peer+0x2C` | ~0x006b48ae | DECOMP-confirmed |
| peer+0x2C updated on each recv (lastRecvTime) | 0x006b5e63 | DECOMP-confirmed |
| peer+0x30 updated on send (lastSendTime) | FUN_006b51e0 body | DECOMP-confirmed |
| 0x60003 registration: PUSH 0x60003 at 0x0069e62b | 0x0069e62b | BYTE-confirmed |
| 0x60005 registration: PUSH 0x60005 at 0x0069e66b | 0x0069e66b | BYTE-confirmed |
| String "DisconnectHandler" at 0x0095a1f0 | 0x0095a1f0 | BYTE-confirmed |
| String "DeletePlayerHandler" at 0x0095a1a4 | 0x0095a1a4 | BYTE-confirmed |
| 0x006a0a20 paired with "DisconnectHandler" in FUN_0069efe0 | 0x0069eff9 | DATA-xref confirmed |
| 0x006a0ca0 paired with "DeletePlayerHandler" in FUN_0069efe0 | 0x0069f049 | DATA-xref confirmed |
| DAT_0088bd58 = 5.0f | 0x0088bd58 | BYTE-confirmed (00 00 a0 40) |
| FUN_006a01e0 (0x14 handler) reads ID via SWIG ReadIntVirtual | 0x006a01e0 | DECOMP-confirmed |
| FUN_006a1420 (0x18 handler) opens TGL Multiplayer.tgl, alpha=1.25, dur=5.0 | 0x006a1420 | DECOMP-confirmed |
| FUN_006a1360 (0x17 handler) TGFactory_DeserializeObject | 0x006a1360 | DECOMP-confirmed |
| FUN_006b9f40 NULL deref pattern at start (first deref of WSN+0x348) | 0x006b9f40 | DECOMP-confirmed |
| FUN_006b4060 posts 0x60003 at shutdown | tail of FUN_006b4060 | DECOMP-confirmed |
| 4th call to FUN_006b75b0 from ProcessIncomingPackets | 0x006b5d97 | XREF-confirmed |
| WSN vtable slot 0x74 = FinalizePeerCleanup at 0x006b9e40 | 0x006b9e40 DATA xref from 0x00895964 | DATA-xref confirmed |

## Completeness scores

| Function | effective_score | code_lines | fixable_deductions |
|----------|----------------|------------|---------------------|
| FUN_006b75b0 (PeerDeletion) | 3.17 | 27 | 96.8 |
| FUN_006b6a20 (GracefulDisconnect) | 10.51 | 17 | 89.5 |
| FUN_006b6a70 (BootRecv) | 10.51 | 13 | 89.5 |
| FUN_006b4560 (TGNetwork_Update) | 0.0 | 196 | 129.9 |
| BootPlayerHandler (0x00506170) | 32.99 | 34 | 67.0 |

All have decompilation available; my evidence is solid even at low scores.

## Suggested v5 status

`partial` — doc captures the correct overall architecture and the cleanup cascade, but Section 1.2's pseudocode-vs-prose mismatch on FUN_006b6a20/FUN_006b6a70, the swapped peer+0x2C/+0x30 offsets, and the missed 4th convergence path are material errors that mislead implementers. Headline value (FUN_006b75b0 as convergence, 0x60005 event ID, peer+0xBC/+0xB8 marking semantics) survives intact.

## Pattern note

This doc was substantially trace-supported (graceful disconnect wire capture, retransmit timing) — those sections (9.x) are useful as ground-truth artifacts. The errors cluster in the structural/code-attribution sections (1.x, 6.x), where the author appears to have reverse-engineered correctly but mislabeled function addresses when transcribing. **Future v5 work: always verify the function-to-pseudocode pairing by `disassemble_function` + first-instruction match before publishing.**
