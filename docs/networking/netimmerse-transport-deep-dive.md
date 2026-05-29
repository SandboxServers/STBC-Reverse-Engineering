> [docs](../README.md) / [networking](README.md) / netimmerse-transport-deep-dive.md

---
title: NetImmerse Transport Layer Deep Dive
type: explanation
audience: re-engineers
status: partial
verified: 2026-05-28
methodology: FUNCTION_DOC_WORKFLOW_V5
binary: stbc.exe (1.0.0.4, base 0x00400000)
supersedes: [2026-02-19]
companions:
  - docs/protocol/transport-layer.md
  - docs/networking/ack-outbox-deadlock.md
  - docs/networking/fragmented-ack-bug.md
  - docs/networking/network-protocol.md
evidence:
  - claim: TGMessage vtable lives at 0x008958d0; slots 0..7 are TGMessage-specific overrides; slots 8..15 inherit from TGBufferStream base.
    address: 0x008958d0
    completeness: n/a
    note: Slot 0..7 verified as TGMessage overrides. Slot 8 (+0x20)=0x006b9c50, slot 9 (+0x24)=0x006b34d0, slot 10 (+0x28)=0x006b34e0, slot 11 (+0x2C)=0x006f1650 confirmed in image bytes — these are base-class slots.
  - claim: Slot 6 = Clone (FUN_006b8610); allocates 0x40 bytes + copy-constructs preserving the vtable pointer.
    address: 0x006b8610
    completeness: n/a
  - claim: Slot 7 = FragmentMessage (FUN_006b8720); calls Clone via vtable[6].
    address: 0x006b8720
    completeness: n/a
  - claim: TGHeaderMessage::WriteToBuffer produces 4-byte non-fragment ACK or 5-byte fragment ACK; wire layout = [type][seq:2][flags][frag_idx?].
    address: 0x006bd190
    completeness: 53.5
    note: v5 plate comment present.
  - claim: ACK factory at 0x006bd1f0 writes msg+0x40 (is_below_0x32) from wire flags bit 1.
    address: 0x006bd1f0
    completeness: n/a
    note: Address is NOT a Ghidra function (get_function_by_address returns "No function found"). Bytes are valid x86; manual disassembly at 0x006bd217 shows `MOV [eax+0x40], cl` where cl = flags>>1 & 1. Resolves prior OQ#1.
  - claim: HandleReliableReceived (FUN_006b61e0) reads msg+0x40 (is_below_0x32), pushes ACKs onto peer+0x9C queue, tracks count at peer+0xB4.
    address: 0x006b61e0
    completeness: 31.6
    note: v5 plate comment present.
  - claim: HandleACK (FUN_006b64d0) uses direct field reads — msg+0x14 (seq), msg+0x39 (frag_idx), msg+0x3c (is_fragmented via piVar+0xf), msg+0x40 (is_below_0x32) — no virtual dispatch.
    address: 0x006b64d0
    completeness: 33.6
  - claim: SendOutgoingPackets (FUN_006b55b0) has a two-pass ACK send — pass 1 gated on `retransmit_count < 3`, pass 2 gated on `retransmit_count > 2` AND (`iStack_28 > 0` OR `peer+0xBC != 0`).
    address: 0x006b55b0
    completeness: 0.0
    note: 271 lines, 22 unrenamed struct accesses, 13 magic numbers. Gate semantics binary-verified; behavioral impact superseded by ack-outbox-deadlock.
  - claim: TGWinsockNetwork::Update calls SendOutgoingPackets → ProcessIncomingMessages → DispatchReceivedMessages in that order.
    address: 0x006b4560
    completeness: n/a
    note: Order confirmed at 2 different state-branches in the function body.
  - claim: Peer expected-seq counter for types <0x32 lives at peer+0x24.
    address: 0x006b6ad0
    completeness: n/a
    note: FUN_006b6ad0 `uVar1 = *(ushort *)(param_3 + 0x24)`.
  - claim: Peer send-seq counter for types <0x32 lives at peer+0x26.
    address: 0x006b5080
    completeness: n/a
    note: FUN_006b5080 `*(short *)(param_3 + 0x26) += 1`.
  - claim: Peer expected-seq counter for types >=0x32 lives at peer+0x28.
    address: 0x006b6ad0
    completeness: n/a
    note: FUN_006b6ad0 `uVar1 = *(ushort *)(param_3 + 0x28)`.
  - claim: Peer send-seq counter for types >=0x32 lives at peer+0x2A.
    address: 0x006b5080
    completeness: n/a
    note: FUN_006b5080 `*(short *)(param_3 + 0x2a) += 1`. Cross-anchored against protocol foundation #3 (transport-layer.md), which previously had +0x98/+0xA8 (now corrected).
  - claim: TGMessage field map — msg+0x14=seq, msg+0x39=frag_idx, msg+0x3a=is_reliable, msg+0x3b=is_ordered, msg+0x3c=is_fragmented, msg+0x40=is_below_0x32.
    address: 0x006b64d0
    completeness: n/a
    note: Layout confirmed via HandleACK + HandleReliableReceived + factory direct reads.
  - claim: Backoff modes 0/1/2 (fixed / linear / exponential) gated by switch on TGMessage retransmit entry +0x2C.
    address: 0x006b8670
    completeness: n/a
    note: 3-way switch in FUN_006b8670 (SetRetransmitCount).
---

# NetImmerse Transport Layer Deep Dive

> [!NOTE]
> **v5 partial pass (2026-05-28)**. Wire-format and field-offset claims (byte-level invariants) byte-confirmed at high confidence; **3 structural corrections** (vtable size, fragment window reasoning, peer-state Section 9 scope) + **2 clarifications** + **1 historical hypothesis demoted**. Notable: this doc had peer seq offsets CORRECT (+0x24/+0x26/+0x28/+0x2A) where protocol foundation #3 had them wrong (corrected in protocol pass). Pattern note: agents reading from static decompilation recover wire claims with fidelity but make more errors on structural reasoning. Original analysis: netimmerse-engine-dev agent, 2026-02-19 (Ghidra not reachable that session).
>
> Sources: `reference/decompiled/11_tgnetwork.c`, `reference/decompiled/12_data_serialization.c`, plus live Ghidra cross-checks during the v5 pass.

---

## 1. TGMessage Vtable — All Slots [v5-validated 2026-05-28]

From call patterns throughout the decompiled source, cross-checked against image bytes at 0x008958d0:

| Slot | Offset | Evidence | Name |
|------|--------|----------|------|
| 0 | +0x00 | Called everywhere as `(*vtable[0])()`; result compared to 0x32 and to type constants | **GetType()** — returns u8 message type (FUN_006b9430) |
| 1 | +0x04 | Called as `(*vtable[4])(1)` to destroy messages | **scalar_deleting_destructor(flag)** |
| 2 | +0x08 | Called as `(*vtable[8])(buf_ptr, remaining_space)` in all three queue send loops | **WriteToBuffer(buf, maxSize)** — returns bytes written, 0 on failure |
| 3 | +0x0C | Called as `(*vtable[0xc])(other_msg)` in `FUN_006b6f30`, returns bool | **Supersedes(other) or IsExpired()** — used to discard stale unreliable messages when a newer reliable arrives |
| 4 | +0x10 | Called in `FUN_006b6ad0` line 4137 as `(*vtable[0x10])()`, non-zero → call `FUN_006b6f30` | **IsOrderedDelivery()** or **HasOrdering()** — triggers the unreliable-queue discard pass |
| 5 | +0x14 | Called everywhere as `(*vtable[0x14])()` to advance the buffer pointer after deserialization | **GetSize()** — returns serialized byte count for this message |
| 6 | +0x18 | Called as `(*vtable[0x18])()` when making per-peer copies | **Clone()** — `FUN_006b8610`, alloc 0x40 bytes + copy-construct |
| 7 | +0x1C | Called as `(*vtable[0x1c])(&count, maxSize)` in SendHelper | **FragmentMessage(&fragCount, maxPayload)** — `FUN_006b8720` |

> [!IMPORTANT]
> **Correction (C1, 2026-05-28)** — The pre-v5 doc claimed "the vtable is 32 bytes total (8 × 4)." That structural claim is wrong. Image bytes at 0x008958f0+ show further slots:
>
> | Slot | Offset | Pointer |
> |------|--------|---------|
> | 8 | +0x20 | 0x006b9c50 |
> | 9 | +0x24 | 0x006b34d0 |
> | 10 | +0x28 | 0x006b34e0 |
> | 11 | +0x2C | 0x006f1650 |
>
> The table continues to at least slot 15. **The TGMessage-specific override slots are 0..7; slots 8..15 inherit from the TGBufferStream base class** and are not involved in message-level dispatch.

The downstream conclusion still holds: **no virtual methods are involved in ACK matching or seq comparison.** HandleACK and HandleReliableReceived both use direct field reads (`piVar + 5` for seq, `+0xf` for is_fragmented, `+0x39` for frag_idx, `+0x40` for is_below_0x32), not virtual dispatch. This eliminates any vtable-based mismatch as a cause.

---

## 2. The Type 0x32 Boundary — Why It Exists and Whether It Causes Mismatches [v5-validated 2026-05-28]

The boundary partitions two completely separate reliable-delivery channels:

**Types 0x00–0x31** (< 0x32): Game message channel. Uses peer+0x24 (expected) and peer+0x26 (send counter). Dispatched through the queue at `TGWinsockNetwork+0x8C`.

**Types 0x32+** (>= 0x32): Session/lobby channel. Uses peer+0x28 (expected) and peer+0x2A (send counter). Dispatched through the queue at `TGWinsockNetwork+0x54`.

The partitioning is confirmed in:
- `FUN_006b5080` (SendHelper) lines 2715–2722: counter selection
- `FUN_006b6ad0` (QueueForDispatch) lines 4117–4124: expected-seq selection
- `FUN_006b6cc0` (ReassembleFragments) lines 4254–4258: queue selection

> [!NOTE]
> Cross-anchor with [transport-layer](../protocol/transport-layer.md): the protocol foundation pass previously cited peer+0x98 / peer+0xA8 for the reliable sequence counters; that was corrected to +0x26 / +0x2A in the protocol family pass. This doc's offsets (+0x24/+0x26/+0x28/+0x2A) were correct from the start.

**Can this cause ACK mismatches?**

In principle, yes. The ACK contains `is_below_0x32` (bit 1 of the flags byte). HandleACK (line 3776) checks that the ACK's `is_below_0x32` matches `msg.GetType() < 0x32`. If the boundary determination differs at creation time vs ACK time, a mismatch would cause every ACK to fail to match.

However, from the decompilation: both `HandleReliableReceived` (FUN_006b61e0 line 3464) and `HandleACK` (FUN_006b64d0 line 3777) call `GetType()` on the same message objects (sender and receiver both use the TGDataMessage vtable). Fragments preserve their original GetType() via Clone(), which copies the vtable pointer. So `GetType()` returns the same value throughout the message lifetime. **The 0x32 boundary does not cause a mismatch in the fragmented message case**, unless the fragmented message is exactly type 0x32 — which is a degenerate edge case.

---

## 3. ACK Serialization Asymmetry — The Deserialization of is_below_0x32 [v5-validated 2026-05-28]

**Serialization** (FUN_006bd190, TGHeaderMessage::WriteToBuffer):
```c
uVar1 = (*(code *)**this)();      // GetType() → 0x01
*param_1 = uVar1;                  // byte[0] = type
*(u16*)(param_1 + 1) = *(u16*)(this + 0x14);  // bytes[1,2] = seq
bVar4 = (*(char*)(this + 0x3c) != 0);          // bit0 = is_fragmented
if (*(char*)(this + 0x40) != 0) bVar4 |= 2;   // bit1 = is_below_0x32
param_1[3] = bVar4;                             // byte[3] = flags
if (*(char*)(this + 0x3c)) {
    param_1[4] = *(u8*)(this + 0x39);          // byte[4] = frag_idx
    return 5;
}
return 4;
```

**Deserialization** (factory at LAB_006bd1f0): Ghidra did not identify this as a named function — it's at address 0x006bd1f0 in the gap between FUN_006bd190 (0x006bd190) and FUN_006bd250 (0x006bd250). The gap is 0xC0 bytes. The factory was registered as `&LAB_006bd1f0`, a raw label at that address.

The agent inferred what it does from the pattern of the type-0 factory (FUN_006bc6a0):

```c
// Type 0 factory pattern (FUN_006bc6a0):
bVar2 = (byte)(uVar1 >> 8);                     // flags byte
*(byte*)(puVar4 + 0x3a) = bVar2 >> 7;           // is_reliable from bit 7
*(byte*)(puVar4 + 0x3b) = bVar2 >> 6 & 1;       // is_ordered from bit 6
```

For the ACK factory, the analogous reads from the wire would be:
- byte[1,2] → seq → msg+0x14
- byte[3] bit0 → is_fragmented → msg+0x3c
- byte[3] bit1 → is_below_0x32 → msg+0x40
- byte[4] (if fragmented) → frag_idx → msg+0x39

**The critical question**: does the ACK factory correctly set `msg+0x40` (is_below_0x32) from the wire?

Looking at the TGHeaderMessage constructor (FUN_006bd120): it sets `*(u8*)(param + 0x10) = 1` which is byte offset `0x10 * 4 = 0x40` → **is_below_0x32 defaults to 1 in every freshly-constructed TGHeaderMessage**. If the factory allocates a TGHeaderMessage via the constructor and then reads the flags byte from wire, it would overwrite this default. But if it fails to read the flags byte, the default of 1 persists.

> [!NOTE]
> **ORCHESTRATOR NOTE — RESOLVED 2026-05-28** (Clar1): Byte-level disassembly at 0x006bd217 confirms the factory writes `MOV [eax+0x40], cl` where cl = (flags >> 1) & 1 = is_below_0x32. The factory DOES correctly populate msg+0x40 from the wire, overwriting the constructor's default of 1. **Factory body remains an unnamed raw label in the current Ghidra DB** (get_function_by_address returns "No function found"); only the address+bytes are validated, not a Ghidra function record.
>
> Disassembled bytes near 0x006bd1f0:
>
> ```
> +0x21  88 50 3c        MOV [eax+0x3c], dl   ; is_fragmented from bit 0
> +0x24  88 48 40        MOV [eax+0x40], cl   ; is_below_0x32 from bit 1
> +0x27  74 06           JZ +6                ; skip frag_idx if not fragmented
> +0x29  8a 56 01        MOV dl, [esi+1]      ; read frag_idx from wire
> +0x2c  88 50 39        MOV [eax+0x39], dl   ; frag_idx → msg+0x39
> ```
>
> The orchestrator's prior OQ#1 (was the factory correctly setting msg+0x40?) is **CLOSED**.

---

## 4. Fragment Message Type Inheritance — Does Clone() Preserve GetType()?

**Yes, unambiguously.** `FUN_006b8720` (FragmentMessage) at line 5391:
```c
piVar6 = (int *)(**(code **)(*this + 0x18))();  // vtable[6] = Clone()
```

And `Clone()` is `FUN_006b8610` → `FUN_006b8550` (CopyConstructor). Line 5207:
```c
*(undefined ***)this = &PTR_LAB_008958d0;  // copies the SAME vtable
```

The copy constructor copies the vtable pointer from the source, preserving it. So fragments have the **identical vtable** as the original message, and `GetType()` returns the identical type.

**No mismatch here.**

---

## 5. The `is_ordered` Flag (+0x3B) and Fragment Queue Ordering

From `SendHelper` (FUN_006b5080), lines 2737–2764:

```c
if (*(char*)(iVar1 + 0x3b) == 0) {   // is_ordered == 0
    // Append to TAIL of first-send queue
    *(int**)(param_2 + 0x68) = piVar3;   // tail = new node
    *(int**)(param_2 + 0x64) = piVar3;   // (when empty: head = new node too)
} else {                                   // is_ordered == 1
    // Insert at HEAD of first-send queue
    piVar3[1] = *(int*)(param_2 + 0x64);  // new.next = old_head
    *(int**)(param_2 + 0x64) = piVar3;    // head = new
}
```

Since Clone() preserves `is_ordered`, if the original message has `is_ordered = 1`, ALL fragments are inserted at the HEAD in reverse order. Fragment 0 is processed first in the loop, inserted at head → [0]. Fragment 1 inserted at head → [1, 0]. Fragment 2 at head → [2, 1, 0]. **They're transmitted in order 2, 1, 0 — reversed.**

At the receiver, the reassembly in `FUN_006b6cc0` uses the `frag_idx` field (not arrival order) to index a 256-element array, so reassembly is correct regardless of arrival order. **This does not cause the ACK bug.**

The sequence counter check in `QueueForDispatch` (FUN_006b6ad0 line 4125) checks each fragment individually against `peer+0x24` (expected seq). All three fragments have the **same seq**. The check is:

```c
iVar5 = incoming_seq - expected_seq;
if ((-0x4001 < iVar5) && (iVar5 < 0 || 0x3fff < iVar5)) {
    destroy and return;  // out-of-window, no ACK
}
```

> [!IMPORTANT]
> **Correction (C2, 2026-05-28)** — The pre-v5 doc reasoned that fragments 2 and 3 arrive with `iVar5 = -1` and "PASS the check too." That reasoning is wrong: `iVar5 = -1` satisfies both subclauses of the discard guard (`-0x4001 < -1` AND `-1 < 0`), so a message with `iVar5 = -1` would be **discarded**.
>
> The conclusion "No blocking here" survives because the real order of operations is different. Reassembly (FUN_006b6cc0) fires **inside** QueueForDispatch and completes **before** the expected counter advances:
>
> 1. **Fragment 0 arrives** — enters QueueForDispatch, `iVar5 = 0` passes the window check, reassembly buffer starts building. Expected counter has **not yet** advanced.
> 2. **Fragments 1 and 2 arrive** (still same seq) — `iVar5 = 0` again, both pass. Reassembly accumulates them.
> 3. **Reassembly completes** — single reassembled message dispatched. **Only then** does the expected counter advance to seq+1.
>
> So in practice the second and third fragments hit the check with `iVar5 = 0`, not `iVar5 = -1`. They pass. The original conclusion ("No blocking here") is correct; the reasoning has been rewritten to match the binary.

---

## 6. Peer Sequence Counter — Receive Side for Fragments

From `DispatchReceivedMessages` (FUN_006b5f70), line 3626:
```c
if (*(char*)((int)piVar2 + 0x3a) != 0) {  // is_reliable
    *(short*)(iVar1 + 0x24) = (short)piVar2[5] + 1;  // expected_seq = fragment.seq + 1
}
```

This sets `expected_seq = seq + 1` for each dispatched reliable message. All three fragments have `seq = 0x0200`. So:

1. Fragment first dispatched: `expected_seq = 0x0200 + 1 = 0x0201`
2. Fragment second dispatched: `expected_seq = 0x0200 + 1 = 0x0201` (same, no change)
3. Fragment third dispatched: `expected_seq = 0x0200 + 1 = 0x0201`

The expected counter ends up at 0x0201 after all three. The ACK matching in HandleACK uses the client's **retransmit queue**, not the receive-side counter.

**No counter mismatch can cause the client to reject its own ACKs.**

---

## 7. Retransmit Queue Ordering — Partial ACK Matching

HandleACK returns after removing ONE entry. For a 3-fragment message, three separate ACK messages must arrive to clear all three retransmit entries.

The retransmit queue is a linked list. HandleACK uses index-based traversal with a cursor (`peer+0x8C`, `peer+0x90`). When an entry is removed, the cursor is updated correctly. **No structural issue with partial removal.**

---

## 8. TGWinsockNetwork::Update — Processing Order [v5-validated 2026-05-28]

From `FUN_006b4560`, lines 2184–2186 (order confirmed at 2 distinct state-branches in the function body):
```c
FUN_006b55b0(param_1);   // 1. SendOutgoingPackets (ACKs + retransmit + first-send)
FUN_006b5c90(param_1);   // 2. ProcessIncomingMessages (receive + ACK creation)
FUN_006b5f70(param_1);   // 3. DispatchReceivedMessages (type dispatch, HandleACK)
```

One tick of latency between receiving fragments and sending ACKs. Normal.

---

## 9. Peer State +0x30 to +0x64 (Non-ACK Range)

From the peer constructor `FUN_006c08d0`:

| Offset | Init Value | Notes |
|--------|-----------|-------|
| +0x2C | DAT_0099c6bc | last_activity_time (current time float) |
| +0x30 | DAT_0099c6bc | last_connect_time |
| +0x34 through +0x60 | 0 | All zeros, no special semantics in ACK path |
| +0x64 | 0 | first-send queue head |

> [!IMPORTANT]
> **Correction (C3, 2026-05-28)** — The pre-v5 doc concluded "No hidden state that could affect ACK processing." That claim was over-broad: it only ruled out the +0x30..+0x64 range and missed the ACK-critical fields living higher in the struct.
>
> Within this range there's no ACK-relevant state. The **ACK-critical fields are higher** in the peer struct:
>
> | Offset | Purpose |
> |--------|---------|
> | peer+0x80 | retransmit queue head |
> | peer+0x84 | retransmit queue tail |
> | peer+0x88..+0x90 | cursor state for HandleACK traversal |
> | peer+0x98 | retransmit count |
> | peer+0x9C | ACK outbox queue head |
> | peer+0xA0..+0xAC | cursor state for ACK outbox |
> | peer+0xB4 | ACK outbox count |
>
> See [ack-outbox-deadlock](ack-outbox-deadlock.md) for analysis of those fields and the deadlock they participate in.

---

## 10. Backoff Mode (TGMessage retransmit entry +0x2C) [v5-validated 2026-05-28]

> [!NOTE]
> **Clarification (Clar2, 2026-05-28)** — The +0x2C offset is on the **TGMessage retransmit entry** (FUN_006b8670's `param_1`), not the peer. Not to be confused with **peer+0x2C** which holds `last_activity_time` (see Section 9). Both objects coincidentally use the same offset for unrelated fields.

From `FUN_006b8670` (SetRetransmitCount), 3-way switch on TGMessage +0x2C:
- Mode 0 = fixed interval
- Mode 1 = linear backoff
- Mode 2 = exponential backoff (clamped to +0x34 max)

From TGMessage constructor: **backoff_mode = 1 (linear backoff)** for regular messages (including fragments via Clone).
From TGHeaderMessage constructor: **backoff_mode = 0 (fixed interval)** for ACKs.

Not the cause — fragments retransmit on their own timer.

---

## Historical (resolved 2026-05-28) — ACK Retransmit Count Exhaustion: Binary-Correct But Behaviorally-Insufficient

> [!NOTE]
> The hypothesis below describes a **real gate** in FUN_006b55b0 (`piVar9[6] < 3` in pass 1; `2 < piVar9[6]` in pass 2 conditional on `iStack_28 > 0 || peer+0xBC != 0`). The binary inspection was correct. But it is **NOT the root cause** of the observed ACK bug. Stock dedi sends StateUpdate routinely, so pass 2 fires normally; observed bug shows identical ACK bytes between stock and OpenBC. The actual root cause is documented in the [ack-outbox-deadlock](ack-outbox-deadlock.md) leaf doc, which supersedes this hypothesis. The text below is retained as a historical sidebar.

The agent hypothesized that `SendOutgoingPackets` (FUN_006b55b0) has a `retransmit_count < 3` limit in the ACK-outbox send pass. After count reaches 3, ACK entries exit the primary send pass and only appear in pass 2 (conditional on prior data traffic). The dedup function refreshes timestamps but not retransmit_count, so entries stay stranded.

Binary verification (v5 pass, 2026-05-28) — gates confirmed in FUN_006b55b0:

```c
// Pass 1 — early ACK send (lines ~2244-2262):
if (0 < *(int *)(iVar2 + 0xb4)) {            // ACK queue has entries
    while (piVar9 != NULL) {
        if ((cVar6 != '\0') && (piVar9[6] < 3)) {    // retransmit_count < 3 GATE
            (**(code **)(*piVar9 + 8))(buf, sz);     // serialize
            FUN_006b8670(piVar9[6] + 1);             // bump retransmit_count
        }
    }
}

// Pass 2 — late ACK send (lines ~2400-2422):
if (((0 < iStack_28) || (*(char *)(iVar2 + 0xbc) != '\0')) && (0 < *(int *)(iVar2 + 0xb4))) {
    while (piVar9 != NULL) {
        if ((cVar6 != '\0') && (2 < piVar9[6])) {    // retransmit_count > 2 GATE
            (**(code **)(*piVar9 + 8))(buf, sz);
            FUN_006b8670(piVar9[6] + 1);
            if (8 < piVar9[6]) { /* remove */ }
        }
    }
}
```

The gate exists and could matter on a quiet link with no other outbound traffic. It does not explain the observed bug, where stock and OpenBC produce identical ACK bytes and the matching-side rejects both. See `ack-outbox-deadlock` for the actual mechanism (two-pass interaction with the dedup timestamp refresh).

---

## Open Questions

- **OQ1 — RESOLVED 2026-05-28**: ACK factory deserialization at 0x006bd1f0 correctly populates `msg+0x40` (is_below_0x32) from wire flags bit 1. Verified by manual disassembly at 0x006bd217 (`MOV [eax+0x40], cl`). See Section 3 Clar1.
- **OQ2 — open**: Field-level mismatch — runtime hooks should log both ACK fields and retransmit-queue entries side-by-side. Any delta reveals the matching bug. Not yet captured.
- **OQ3 — open**: Whether HandleACK is even called for fragment ACKs — if ACK dispatch somehow skips fragment ACKs, runtime call-count hooks will show it. Not yet captured.

---

## Static-Decompilation-Only Validation: Lessons

This doc is the **first foundation-tier doc validated that was created without live Ghidra access** (per its top disclaimer). The v5 validation pass found a recoverable signal: wire-format and field-offset claims (byte-level invariants) survived with high fidelity, while structural and control-flow claims had more errors.

Pattern observed:

- **Reliable**: Wire format, field offsets, function entry addresses, gate constants. Section 3 (wire format) and the peer seq-counter offsets (+0x24/+0x26/+0x28/+0x2A) were correct down to the byte.
- **Less reliable**: Structural claims (Section 1 "vtable is 32 bytes total"), control-flow reasoning (Section 5 fragment-window logic), and scope of hidden state outside the directly-examined snippet (Section 9's "no hidden state" claim missed peer+0x80+ entirely).

Useful heuristic for triaging future "Ghidra-not-reachable" docs: **trust the wire claims more than the narrative reasoning.** When validating, audit reasoning chains and structural enumerations first; wire-byte tables tend to be safe.
