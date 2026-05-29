---
name: networking-foundation-netimmerse-transport-validation-20260528
description: Networking foundation #5 (NetImmerse transport deep dive). Doc written WITHOUT live Ghidra, but most claims survived. Wire format CORRECT. Peer seq offsets +0x24/+0x26/+0x28/+0x2A CONFIRMED (foundation #3 had wrong +0x98/+0xA8). ACK factory at 0x006bd1f0 IS bare code (not a function) but DOES correctly set msg+0x40. Agent's "ACK retransmit count exhaustion" hypothesis CONFIRMED at binary level (pass1<3, pass2>2) but orchestrator was right it doesn't explain stock dedi behavior.
metadata:
  type: project
---

# Networking Foundation #5 — netimmerse-transport-deep-dive.md validation (2026-05-28)

## Top line

Doc carries explicit "Ghidra not reachable" disclaimer + orchestrator confidence flags. Most wire and field claims SURVIVE live binary verification. Few corrections, all minor. The ACK retransmit-count-exhaustion hypothesis is REAL in the binary (the gate exists) but orchestrator was correct that it doesn't explain observed stock-dedi behavior.

## Verified anchors (high confidence)

| Doc claim | Address / value | Status |
|---|---|---|
| TGMessage vtable @ 0x008958d0 | bytes `30946b00...` (slot 0..7) | CONFIRMED |
| Slot 0 = GetType @ 0x006b9430 | byte read | CONFIRMED |
| Slot 6 = Clone @ 0x006b8610 | TGBufferStream_Clone | CONFIRMED |
| Slot 7 = FragmentMessage @ 0x006b8720 | TGBufferStream_Fragment | CONFIRMED |
| HandleACK reads msg+0x40 (is_below_0x32) | FUN_006b64d0 line `cVar1 = *(char*)(param_1 + 0x40);` | CONFIRMED |
| HandleACK reads msg+0x14 (seq) | line `*(short *)(puVar8 + 5) != *(short *)(param_1 + 0x14)` | CONFIRMED |
| HandleACK reads msg+0x39 (frag_idx) | line `*(char *)((int)puVar8 + 0x39) == *(char *)(param_1 + 0x39)` | CONFIRMED |
| HandleACK reads msg+0x3c (is_fragmented) | line `*(char *)(puVar8 + 0xf)` (0xf*4=+0x3c) | CONFIRMED |
| TGHeaderMessage_Serialize wire format | FUN_006bd190 (already has v5 plate comment) | CONFIRMED |
| 4 byte non-fragment ACK / 5 byte fragment ACK | wire `[type][seq:2][flags][frag_idx?]` | CONFIRMED |
| TGHeaderMessage_Ctor sets is_below_0x32=1 default | FUN_006bd120 `*(undefined1*)(param_1 + 0x10) = 1` (DWORD idx 0x10 = byte +0x40) | CONFIRMED |
| ACK factory at 0x006bd1f0 IS bare code (no function) | `get_function_by_address` returns "No function found" | CONFIRMED |
| ACK factory writes msg+0x40 from wire bit1 | byte-disassembly: `884840` MOV [eax+0x40], cl | **NEWLY VERIFIED** |
| Send seq counter peer+0x26 (<0x32) | FUN_006b5080 `*(short *)(param_3 + 0x26) += 1` | CONFIRMED |
| Send seq counter peer+0x2A (>=0x32) | FUN_006b5080 `*(short *)(param_3 + 0x2a) += 1` | CONFIRMED |
| Expected seq peer+0x24 (<0x32) | FUN_006b6ad0 `uVar1 = *(ushort *)(param_3 + 0x24)` | CONFIRMED |
| Expected seq peer+0x28 (>=0x32) | FUN_006b6ad0 `uVar1 = *(ushort *)(param_3 + 0x28)` | CONFIRMED |
| HandleReliableReceived sets is_below_0x32 | FUN_006b61e0 (already has v5 plate) | CONFIRMED |
| HandleReliableReceived ACK queue head = peer+0x9C | line `piVar7 = *(int **)(param_3 + 0x9c)` | CONFIRMED |
| HandleReliableReceived ACK queue count = peer+0xB4 | line `*(int *)(param_3 + 0xb4) > 0` | CONFIRMED |
| FragmentMessage preserves vtable via Clone | FUN_006b8720 calls vtable[6] | CONFIRMED |
| Clone allocates 0x40 bytes | FUN_006b8610 calls FUN_00717b70(0x40) | CONFIRMED |
| Backoff modes 0/1/2 in SetRetransmitCount | FUN_006b8670 (3-way switch on +0x2C) | CONFIRMED |
| Section 8: Update calls Send→Process→Dispatch in that order | FUN_006b4560 — confirmed at 2 different state-branches | CONFIRMED |

## Cross-foundation reconciliation

**Foundation #3 (transport-layer.md)** previously cited peer+0x98 and peer+0xA8 for "the two reliable sequence counters." This was ALREADY corrected in protocol foundation #3 validation memo to +0x26 and +0x2A. Foundation #5 (this doc) cites the correct offsets: +0x24/+0x26 (<0x32 expected/send) and +0x28/+0x2A (>=0x32 expected/send). **Foundation #5 wins this reconciliation — its offsets are right.**

Peer+0x98 and peer+0xA8 ARE used in the binary, but for the **retransmit queue** (peer+0x80 head, peer+0x84 tail, peer+0x88 cursor mid, peer+0x8C cursor next, peer+0x90 cursor index, peer+0x98 retransmit count). They are NOT the send-seq counters foundation #3 claimed.

## Corrections required (C-class)

**C1 — Vtable size claim (Section 1)**
Doc says: "There are no additional vtable slots beyond these 8. The vtable is 32 bytes total (8 × 4)."
Reality: bytes at 0x008958f0+ show slots 8-15 exist:
- Slot 8 (+0x20) = 0x006b9c50
- Slot 9 (+0x24) = 0x006b34d0
- Slot 10 (+0x28) = 0x006b34e0
- Slot 11 (+0x2C) = 0x006f1650
- (continues to at least slot 15)

These appear to be base-class slots (TGBufferStream extends further). The vtable layout extends past 8 slots. The TGMessage-specific overrides ARE in slots 0-7, so the doc's downstream conclusion ("No virtual methods are involved in ACK matching or seq comparison") remains correct. But the structural claim "32 bytes total" is wrong.

**C2 — Section 5 reasoning on fragment seq-window**
Doc says: "If `incoming_seq == expected_seq`, iVar5 = 0, which passes the check. After the first fragment is dispatched and the expected counter advances to seq+1, the second and third fragments with the same seq arrive with `incoming_seq - expected_seq = -1`. **Since -1 is between -0x4001 and 0, this PASSES the check too.**"

Reality: the window check in FUN_006b6ad0 is `(iVar5 > -0x4001) AND (iVar5 < 0 OR iVar5 > 0x3fff)` → DISCARD. So iVar5=-1 matches the DISCARD condition.

Why fragments still work: reassembly (FUN_006b6cc0) is called INSIDE QueueForDispatch BEFORE the expected counter advances. By the time the expected counter advances, the message has been reassembled to a single object. Subsequent fragments arriving in the SAME packet pass with iVar5=0 (same seq, no advance has happened yet). Subsequent fragments arriving in LATER packets would be rejected — but in practice all fragments of one message arrive in one packet sequence before dispatch fires.

Section 5's CONCLUSION ("No blocking here") happens to be correct, but the cited REASONING is wrong.

**C3 — Section 9 hidden state under-specification**
Doc says: "+0x34 through +0x60: All zeros, no special semantics in ACK path. No hidden state that could affect ACK processing."

Reality: peer struct extends to at least +0xC0. ACK-relevant fields at higher offsets include:
- peer+0x80 = retransmit queue head
- peer+0x84 = retransmit queue tail
- peer+0x88..+0x90 = cursor state for HandleACK traversal
- peer+0x98 = retransmit count
- peer+0x9C = ACK outbox queue head (used in HandleReliableReceived)
- peer+0xA0..+0xAC = cursor state for ACK outbox
- peer+0xB4 = ACK outbox count

The doc's "no hidden state in ACK path" is materially WRONG. The ACK path uses substantial peer state at +0x80+. Section 9 should be retitled/scoped to "peer state between +0x30 and +0x64" (which is what it actually documents).

## Clarifications (Clar-class)

**Clar1 — Section 3 "factory at LAB_006bd1f0" status**
Doc characterizes the ACK factory as a "raw label" because Ghidra hadn't created a function. STILL TRUE in current Ghidra DB: `get_function_by_address(0x006bd1f0)` returns "No function found." But: the bytes ARE valid x86 (verified by manual disassembly) and the function IS reachable from the type-1 factory dispatch table. The doc's inference about what it does was CORRECT — verified by reading the raw bytes:
```
+0x21 (in fn)  88 50 3c           MOV [eax+0x3c], dl  ; is_fragmented from bit 0
+0x24          88 48 40           MOV [eax+0x40], cl  ; is_below_0x32 from bit 1
+0x27          74 06              JZ +6              ; skip frag_idx if not fragmented
+0x29          8a 56 01           MOV dl, [esi+1]    ; read frag_idx from wire
+0x2c          88 50 39           MOV [eax+0x39], dl ; frag_idx → msg+0x39
```
So the orchestrator's "open question" about the ACK factory is RESOLVED: it DOES correctly read is_below_0x32 from the wire and overwrite the constructor's default of 1. **The orchestrator note at end of Section 3 can be promoted to "resolved — factory does set the field correctly."**

**Clar2 — Section 10 "Backoff Mode (+0x2C)" location**
Section 10 heading says "Backoff Mode (+0x2C) for Fragmented Messages" without specifying object. The +0x2C offset is on the **TGMessage** (the retransmit entry), NOT the peer. FUN_006b8670's param_1 is the message; param_1+0x2C is read as mode. The peer also has things at +0x2C (last_activity_time per Section 9) — these are unrelated.

## Open questions raised by the orchestrator that are now resolvable

**OQ "does the ACK factory correctly set msg+0x40 from the wire"** — YES. Verified by reading raw bytes at 0x006bd217: `MOV [eax+0x40], cl` where cl = (flags >> 1) & 1 = is_below_0x32 bit. **OQ #1 in doc's "Remaining Open Questions" is RESOLVED.**

## The "ACK Retransmit Count Exhaustion" hypothesis (Section "Agent's Root Cause Hypothesis")

The orchestrator note flagged this as LOW CONFIDENCE because:
- ACKs are on the wire in stock dedi
- Stock dedi sends plenty of StateUpdate so pass-2 would fire

After reading FUN_006b55b0 (SendOutgoingPackets), the agent's CODE INSPECTION was CORRECT:

```c
// Pass 1 — early ACK send (lines ~2244-2262):
if (0 < *(int *)(iVar2 + 0xb4)) {  // ACK queue has entries
    while (piVar9 != NULL) {
        if ((cVar6 != '\0') && (piVar9[6] < 3)) {  // <-- retransmit_count < 3 GATE
            (**(code **)(*piVar9 + 8))(buf, sz);  // serialize
            FUN_006b8670(piVar9[6] + 1);  // bump retransmit_count
        }
    }
}

// (then retransmit queue, then first-send queue)

// Pass 2 — late ACK send (lines ~2400-2422):
if (((0 < iStack_28) || (*(char *)(iVar2 + 0xbc) != '\0')) && (0 < *(int *)(iVar2 + 0xb4))) {
    while (piVar9 != NULL) {
        if ((cVar6 != '\0') && (2 < piVar9[6])) {  // <-- retransmit_count > 2 GATE
            (**(code **)(*piVar9 + 8))(buf, sz);  // serialize
            FUN_006b8670(piVar9[6] + 1);
            if (8 < piVar9[6]) { /* remove */ }
        }
    }
}
```

So the gates ARE `< 3` (pass 1) and `> 2` (pass 2), with pass 2 conditional on `iStack_28 > 0` (something else sent this tick) OR `peer+0xBC != 0` (special peer state — probably "client disconnecting"). **The binary-level behavior matches the agent's claim.**

But the orchestrator note's STRATEGIC point still holds:
- On stock dedi, pass 2 fires routinely because StateUpdate keeps `iStack_28 > 0`
- The hypothesis can't explain "ACKs identical between stock and OpenBC" if the gate behavior is identical
- The hypothesis can't explain "client-side matching bug" since the matching is in HandleACK on the receiver side

**Verdict**: hypothesis is BINARY-CORRECT but BEHAVIORALLY-INSUFFICIENT to explain the observed bug. Should be reframed as: "the gate exists and could matter on quiet links, but is NOT the root cause of the ACK-matching bug we're observing." Pre-existing memory has `[[ack-outbox-deadlock]]` analysis that supersedes this.

## Completeness scores

- TGHeaderMessage_Serialize @ 0x006bd190 — effective 53.5 (v5 plate comment present)
- TGWinsockNetwork_HandleReliableReceived @ 0x006b61e0 — effective 31.6 (v5 plate, many unrenamed struct accesses)
- TGWinsockNetwork_HandleACK @ 0x006b64d0 — effective 33.6 (no plate yet, 5 unrenamed labels)
- TGWinsockNetwork_SendOutgoingPackets @ 0x006b55b0 — effective 0.0 (271 lines, 22 unrenamed struct accesses, 13 magic numbers)

## Counterevidence

None. Every wire-format claim in the doc is binary-verifiable. The peer-seq-offset corrections that foundation #3 needed do NOT apply to this doc — this doc had the correct offsets from the start.

## Triage summary (v5 standard)

| Class | Count | Notes |
|---|---|---|
| C (correction needed) | 3 | Vtable size (Section 1), Section 5 reasoning, Section 9 hidden state under-spec |
| Clar (clarification) | 2 | ACK factory raw-label still applies; Section 10 +0x2C location ambiguity |
| R (rewrite) | 0 | |
| OQ resolved | 1 | ACK factory does set msg+0x40 correctly — orchestrator's OQ #1 closed |
| OQ open | 2 | (doc's OQ #2 field-level mismatch, OQ #3 HandleACK call count — both need runtime traces) |
| H (historical) | 1 | The agent's root-cause hypothesis section — binary-correct but doesn't explain observed bug |

## Cross-links

- [[transport-layer-validation-20260528]] — sibling protocol foundation, corrected the peer+0x98/+0xA8 confusion
- [[networking-foundation-network-protocol-validation-20260528]] — parent networking architecture doc
- `.claude/agent-memory/network-protocol-analyst/below32-ack-mechanism.md` — referenced from FUN_006b61e0 plate comment
- The ack-outbox-deadlock doc supersedes the "retransmit count exhaustion" hypothesis with a different mechanism (two-pass + dedup timestamp refresh)

## Pattern note

This is the FIRST doc validated that was created WITHOUT live Ghidra. Pattern: agents reading from `reference/decompiled/*.c` (static dump) can recover SURPRISINGLY ACCURATE wire format and field-offset claims, because those are byte-level invariants. They make MORE errors on:
- Structural claims (vtable size, total slot count)
- Reasoning about control flow (Section 5)
- Hidden state (the parts of the struct the dump doesn't show in their function snippet)

The doc's wire-format claims are MORE reliable than its narrative reasoning. This is a useful heuristic for triaging future "Ghidra-not-reachable" docs.
