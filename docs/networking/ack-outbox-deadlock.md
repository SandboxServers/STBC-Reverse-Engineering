---
title: ACK-Outbox Deadlock — Long-Session Degradation Root Cause
type: explanation
audience: RE engineers, OpenBC implementers
validated: 2026-05-28
methodology: FUNCTION_DOC_WORKFLOW_V5
binary_fingerprint: stbc.exe (base 0x400000, 32-bit Windows)
status: verified
supersedes: []
evidence:
  - claim: "SendOutgoingPackets — 2-pass ACK + retransmit + first-send serialization worker"
    address: 0x006b55b0
    confidence: high
    note: "271 LOC, effective_score 0.0 (worker function, no completeness gate)"
  - claim: "Buffer reservation `ADD EAX,0x2; SUB EBX,0x2` reserves 2-byte header from 512-byte buffer (510 usable)"
    address: 0x006b5672
    confidence: high
  - claim: "Pass 1 filter `entry+0x18 < 3` at `CMP [EDI+0x18],0x3; JGE`"
    address: 0x006b56cc
    confidence: high
  - claim: "Pass 2 deadlock gate: `(msg_count > 0 OR peer+0xBC != 0) AND peer+0xB4 > 0` — the bug"
    address: 0x006b5a01
    confidence: high
    note: "0x006b5a01: MOV EAX,[ESP+0x14]; 0x006b5a09: MOV AL,[ESI+0xbc]; 0x006b5a17-0x006b5a1f: TEST EAX (peer+0xB4); JLE bypass"
  - claim: "Pass 2 filter `entry+0x18 >= 3` at `CMP [EDI+0x18],0x3; JL`"
    address: 0x006b5a5b
    confidence: high
  - claim: "Pass 2 cleanup at `entry+0x18 >= 9` — RemoveFromQueue + destructor"
    address: 0x006b5a96
    confidence: high
    note: "CMP [EDI+0x18],0x9; JL skips cleanup branch"
  - claim: "HandleReliableReceived — ACK creation + O(N) dedup scan"
    address: 0x006b61e0
    confidence: high
    note: "effective_score 31.6"
  - claim: "Dedup loop body at MOV AX,word ptr [ECX+0x14] (existing.seq comparison)"
    address: 0x006b624d
    confidence: high
    note: "0x006b6240-0x006b624b is init/null-check preamble"
  - claim: "HandleACK — searches retransmit queue, removes matching entry"
    address: 0x006b64d0
    confidence: high
    note: "89 LOC worker, effective_score 33.6"
  - claim: "RemoveFromQueue — removes node at index from linked list"
    address: 0x006b78d0
    confidence: high
  - claim: "SetRetransmitCount — writes msg+0x18 (retx count) AND recomputes msg+0x1C (interval) as side effect"
    address: 0x006b8670
    confidence: high
  - claim: "CheckRetransmitTimer — returns true if last_send + interval < now (reads msg+0x1C float)"
    address: 0x006b8700
    confidence: high
  - claim: "TGWinsockNetwork base ctor sets param_1[0x2b] = 0x400 (1024 base)"
    address: 0x006b3a00
    confidence: high
  - claim: "TGWinsockNetwork derived ctor overrides param_1[0x2b] = 0x200 (512 actual)"
    address: 0x006b9bf0
    confidence: high
  - claim: "TGHeaderMessage ctor — sets vtable 0x008959ac, 0x44 byte object"
    address: 0x006bd120
    confidence: high
  - claim: "TGHeaderMessage WriteToBuffer — emits 4/5 byte ACK with remaining-space check"
    address: 0x006bd190
    confidence: high
  - claim: "peer+0x9C / peer+0xA0 = ACK-outbox head/tail"
    address: null
    confidence: high
    note: "head read at 0x006b5a25, tail append at 0x006b6344 (HandleReliableReceived)"
  - claim: "peer+0xB4 = ACK-outbox entry count (u32)"
    address: null
    confidence: high
    note: "read at 0x006b567c and 0x006b5a17"
  - claim: "peer+0xBC = is_disconnecting (u8)"
    address: null
    confidence: high
    note: "read at 0x006b5a09 as byte ptr"
  - claim: "msg+0x18 = retransmit_count (u32)"
    address: null
    confidence: high
    note: "Pass 1 filter at 0x006b56cc, Pass 2 filter at 0x006b5a5b, cleanup at 0x006b5a96"
  - claim: "msg+0x1C = retransmit_interval (float), msg+0x20 = last_send_time (float)"
    address: null
    confidence: high
    note: "msg+0x20 written at 0x006b56ef via FSTP [EDI+0x20]"
companions:
  - docs/networking/netimmerse-transport-deep-dive.md
  - docs/networking/fragmented-ack-bug.md
  - docs/networking/network-protocol.md
  - docs/networking/disconnect-flow.md
---

> [docs](../README.md) / [networking](README.md) / ack-outbox-deadlock.md

# ACK-Outbox Deadlock — Long-Session Degradation Root Cause

> [!NOTE]
> **v5 verified pass — zero mechanism corrections.** Most byte-verifiable networking-family doc to date: deadlock model, two-pass filter ranges, cleanup threshold, buffer sizing, struct offsets, and all 9 function addresses survive byte-level cross-check at the cited disassembly. Supersedes netimmerse-transport's "ACK Retransmit Count Exhaustion" hypothesis (binary-correct but behaviorally-insufficient). 4 address-precision clarifications applied; no behavior or wire claims changed.
>
> - **Clar-1**: Pass 2 gate is `(msg_count > 0 OR peer+0xBC != 0) AND peer+0xB4 > 0` — the `peer+0xB4 > 0` predicate at 0x006b5a17-0x006b5a1f is part of the same gate.
> - **Clar-2**: Dedup loop body begins at `0x006b624D` (not 0x006b6240 — preamble is the init/null-check; comparison starts at the `MOV AX,word ptr [ECX+0x14]`).
> - **Clar-3**: Pass 2 loop runs `0x006b5a50-0x006b5af4` (not `-0x006b5b90` — the 0x006b5af4-0x006b5b90 range is the packet-finalize / sendto block).
> - **Clar-4**: Pass 1 `entry.retx_count++` is via `FUN_006b8670(piVar9[6] + 1)` (SetRetransmitCount), which also **recomputes msg+0x1C (retransmit interval)** as a side effect. Doesn't affect the deadlock; matters for OpenBC retransmit timing parity.

Reverse-engineered from stbc.exe via Ghidra decompilation and runtime instrumentation (OBSERVE_ONLY proxy build, 2026-02-19).

**Related docs**:
- [fragmented-ack-bug.md](fragmented-ack-bug.md) — ACK-outbox accumulation evidence, fragment ACK matching failure
- [disconnect-flow.md](disconnect-flow.md) — Disconnect packet carries stale ACKs
- [netimmerse-transport-deep-dive.md](netimmerse-transport-deep-dive.md) — parent foundation doc; this doc supersedes its "ACK Retransmit Count Exhaustion" sidebar (see § "Supersedes netimmerse-transport ACK Retransmit Count Exhaustion Hypothesis" below)

## Summary

The ACK-outbox (`peer+0x9C`) has a cleanup mechanism that removes entries after 9 retransmissions — but a logic deadlock prevents the cleanup pass from executing when no other traffic is flowing. Entries with retransmit count 3-8 become stuck: never sent again, never cleaned up, never freed. This causes memory leaks, game data starvation, and O(N) dedup search degradation. Empirical validation (34-minute battle trace, 3 players) shows the bug is **self-limiting during active gameplay** — the queue peaks at 20-33 entries rather than the hundreds originally projected, with zero observable tick degradation. The bug remains a theoretical concern for very long sessions with extended quiet periods.

---

## 1. Packet Buffer Allocation [v5-validated 2026-05-28]

**Function**: `SendOutgoingPackets` at `0x006b55b0`

The outgoing packet buffer is **heap-allocated** at the top of each call:

```c
buffer = NiAlloc(this[0x2B]);  // this = TGNetwork
```

Buffer size comes from `TGNetwork+0xAC`:
- Base class constructor (`0x006b3a00`) sets `this[0x2B] = 0x400` (1024 bytes)
- **TGWinsockNetwork constructor (`0x006b9bf0`) overrides to `this[0x2B] = 0x200` (512 bytes)**

**Actual buffer size: 512 bytes.** First 2 bytes reserved for header (`[peer_id][msg_count]`) — reservation visible at `0x006b5672: ADD EAX,0x2; 0x006b5675: SUB EBX,0x2` — leaving **510 usable bytes** for transport messages.

---

## 2. Two-Pass ACK Processing [v5-validated 2026-05-28]

SendOutgoingPackets processes the ACK-outbox in **two separate passes** per peer, with different retransmit count filters.

### Pass 1: Fresh ACKs (retx < 3)

```
Location: 0x006b5690 - 0x006b5740
Filter anchor: 0x006b56cc  CMP [EDI+0x18],0x3; JGE  (entry.retx < 3)

for each entry in peer+0x9C (ACK-outbox):
    if CheckRetransmitTimer(entry) AND entry.retx_count < 3:
        bytes = entry.WriteToBuffer(write_ptr, remaining)
        if bytes == 0: break          // buffer full
        entry.last_send_time = now    // FSTP [EDI+0x20] @ 0x006b56ef
        msg_count++
        SetRetransmitCount(entry, entry.retx_count + 1)  // FUN_006b8670 @ 0x006b56fe
                                       // ← also recomputes msg+0x1C (interval)
        write_ptr += bytes
        remaining -= bytes
        if msg_count >= 255: break    // u8 cap @ 0x006b570f
```

Key details:
- **Filter**: `entry+0x18 < 3` (retx count at TGMessage offset +0x18)
- **No removal**: entries stay in the queue after serialization
- **Cursor-based iteration** via `peer+0xA8` / `peer+0xAC` (not destructive dequeue)
- Entries with retx >= 3 are **silently skipped**
- **Side effect** (Clar-4): the `retx_count++` is `SetRetransmitCount(entry, n+1)` at `0x006b8670`, which **also recomputes the retransmit interval at msg+0x1C** based on the new count (and msg+0x2C mode). Doesn't affect the deadlock mechanism, but OpenBC implementations must replicate the interval recomputation for retransmit-timing parity.

### Retransmit Queue + First-Send Queue (between passes)

After Pass 1, the retransmit queue (`peer+0x80`) and first-send queue (`peer+0x64`) are processed normally. Both have the same `msg_count >= 255` and buffer-remaining guards.

### Pass 2: Stale ACKs (retx >= 3) — With Cleanup

```
Location: 0x006b5a50 - 0x006b5af4   (post-loop finalize is 0x006b5af4-0x006b5b90)
Filter anchor: 0x006b5a5b  CMP [EDI+0x18],0x3; JL    (entry.retx >= 3)
Cleanup anchor: 0x006b5a96  CMP [EDI+0x18],0x9; JL  (retx >= 9 removes entry)
Gate anchor:   0x006b5a01-0x006b5a1f                  ← THE DEADLOCK

GATE: (msg_count > 0 OR peer+0xBC != 0) AND (peer+0xB4 > 0)
      └─────────── 0x006b5a01-0x006b5a11 ────────────┘  └ 0x006b5a17-0x006b5a1f ┘
      "either we already sent something this tick,        "and the outbox actually
       or we're tearing the peer down"                     has entries to serialize"

if gate passes:
    for each entry in peer+0x9C (ACK-outbox):
        if CheckRetransmitTimer(entry) AND entry.retx_count >= 3:
            bytes = entry.WriteToBuffer(write_ptr, remaining)
            if bytes == 0: break
            entry.last_send_time = now
            msg_count++
            SetRetransmitCount(entry, entry.retx_count + 1)  // also recomputes msg+0x1C

            if entry.retx_count > 8:              // retx >= 9 @ 0x006b5a96
                RemoveFromQueue(&peer+0x9C, idx)   // FUN_006b78d0
                removed.Destroy(1)                 // free TGHeaderMessage

            write_ptr += bytes
            remaining -= bytes
            if msg_count >= 255: break            // @ 0x006b5acc
```

Key details:
- **Gate condition** (Clar-1): `(msg_count > 0 || peer.is_disconnecting) && peer+0xB4 > 0`. The `peer+0xB4 > 0` clause ("ACK outbox is non-empty") is the third predicate, byte-anchored at `0x006b5a17: MOV EAX,[ESI+0xb4]; 0x006b5a1d: TEST EAX,EAX; 0x006b5a1f: JLE 0x006b5af4`. In the deadlock scenario the outbox is non-empty by construction, so the deadlock analysis below is unaffected — but the full gate matters for OpenBC parity.
- **Filter**: `entry+0x18 >= 3` (opposite of Pass 1)
- **Cleanup at retx >= 9**: entry removed from queue and freed via `RemoveFromQueue` at `0x006b78d0` + destructor
- **Range correction** (Clar-3): the Pass 2 loop body runs `0x006b5a50-0x006b5af4`. The range `0x006b5af4-0x006b5b90` is the **packet-finalize block** (writing `peer_id + msg_count` to `buffer[0..1]` and calling `sendto` via the network vtable). Prior pre-v5 phrasing extended the loop range incorrectly.

---

## 3. The Deadlock [v5-validated 2026-05-28]

The two passes create a deadlock condition for entries in the retx 3-8 range:

```
State: All ACK-outbox entries have retx >= 3
       No new reliable messages to send (retransmit queue empty, first-send empty)

Pass 1: Iterates ackOutQ → skips all entries (retx >= 3 filter)
         → msg_count stays 0

Retransmit queue: Empty → msg_count stays 0
First-send queue: Empty → msg_count stays 0

Pass 2 gate: msg_count == 0 AND peer.is_disconnecting == 0
           → gate FAILS → Pass 2 DOES NOT EXECUTE

Result: Entries with retx 3-8 are stuck forever:
        - Pass 1 won't touch them (retx too high)
        - Pass 2 won't run (msg_count gate fails)
        - No other code path removes them
```

The only exits from deadlock:
1. **New game traffic** generates a retransmit or first-send message → msg_count > 0 → Pass 2 gate opens → stuck entries get incremented toward retx 9 → eventually cleaned up
2. **Peer disconnects** → `peer+0xBC = 1` → Pass 2 gate opens via disconnecting flag
3. **Never** — in a lull between active exchanges, entries remain stuck indefinitely

In practice, active gameplay generates enough traffic that msg_count > 0 most ticks, so entries eventually reach retx 9 and get cleaned. But during quiet periods (lobby, post-combat lulls), the deadlock kicks in and entries accumulate.

### Empirical Behavior (2026-02-19)

Two session traces validate the deadlock mechanism but show it is **self-limiting during active gameplay**:

- **Valentine's Day battle trace** (34 minutes, 3 players, stock dedi): Peak ackOutQ of 20-33 entries, not the hundreds projected. During active combat, game traffic keeps msg_count > 0 most ticks, opening the Pass 2 gate frequently enough to drain stuck entries before they accumulate.
- **Feb 19 instrumented session** (91 seconds, 1 client, ACK-HOOK/ACK-DIAG): Peak ackOutQ of 11-13 entries. 64% of HandleACK calls found retxQ=0 (stale ACKs arriving after retransmit queue already cleared).

The deadlock is **intermittent, not permanent** — it resolves whenever new game traffic flows. Entries accumulate during quiet periods but drain during active play. The queue stabilizes at 10-33 entries rather than growing unboundedly.

---

## 4. Buffer Overflow Analysis

**Result: No buffer overflow vulnerability.**

| Protection | Mechanism |
|-----------|-----------|
| Write bounds | WriteToBuffer checks `remaining < required_size`, returns 0 if insufficient |
| Loop termination | All 4 loops break on WriteToBuffer returning 0 |
| msg_count cap | All 4 loops break at `msg_count >= 255` (`0xFE < iStack_28`) |
| msg_count write | `buffer[1] = (char)msg_count` — but never exceeds 255 due to caps |

Maximum ACK entries before buffer exhaustion:
- Non-fragmented ACKs (4 bytes): 510 / 4 = **127 entries**
- Fragmented ACKs (5 bytes): 510 / 5 = **102 entries**
- The 255 msg_count cap would require 1020+ bytes — buffer fills first

The engine safely stops serializing when the buffer is full. No overflow is possible.

---

## 5. Three Degradation Effects

### 5.1 Memory Leak

Each stuck ACK entry consumes:
- 0x44 bytes (68 bytes) — TGHeaderMessage object (vtable 0x008959ac)
- 8 bytes — queue node (`[msg_ptr:4][next_ptr:4]`)
- **Total: 76 bytes per entry**

Growth rate depends on session activity:
- Each incoming reliable message creates an ACK entry (if not deduped)
- Dedup only matches if an entry with the SAME {seq, is_fragmented, frag_idx, is_below_0x32} exists
- New sequence numbers always create new entries

Estimated vs observed accumulation:

| Session Duration | Originally Projected | Observed (34-min trace) | Memory Impact |
|------------------|---------------------|------------------------|---------------|
| 2 minutes | ~13 entries | 11-13 entries | ~1 KB |
| 30 minutes | ~600 entries | **20-33 entries (peak)** | ~2.5 KB |
| 2 hours | ~2,400 entries | Not measured | Not measured |
| 4 hours | ~5,000-12,000 entries | Not measured | Not measured |

The original projections assumed unbounded growth. In practice, during active gameplay the Pass 2 gate opens frequently (msg_count > 0 most ticks), draining entries before they accumulate. The queue stabilizes at 10-33 entries during active combat sessions. Long-session projections (2+ hours) remain unmeasured — accumulation during extended quiet periods (lobby idle, post-combat lulls) could still be significant.

Not catastrophic for active gameplay sessions, but BC's 32-bit address space and 2002-era memory assumptions mean the theoretical risk at extreme session lengths (hours of intermittent quiet periods) should not be dismissed entirely.

### 5.2 Game Data Starvation

While entries have retx < 3 (first 3 sends), they consume buffer space:
- 38 stale ACKs × 4 bytes = **152 bytes** of the 510-byte budget
- Leaves only **358 bytes** for actual game data (StateUpdates, weapon fire, collisions)
- In burst scenarios (ship explodes, many subsystems damaged), critical game messages may be deferred to the next tick

This is transient — after 3 sends the entries stop consuming buffer space (Pass 1 skips them). But new entries are constantly being created, so some buffer waste is continuous.

**Empirical note**: In the 34-minute battle trace, packets carried up to 33 messages (~132 bytes of ACKs from the ~512-byte budget). This is significant but not catastrophic — approximately 26% of the buffer consumed by stale ACKs at peak, leaving ~378 bytes for game data.

### 5.3 Dedup Search Degradation [v5-validated 2026-05-28]

**Function**: `HandleReliableReceived` at `0x006b61e0`

Called for EVERY incoming reliable message. Walks the ENTIRE ACK-outbox linearly to check for duplicates:

```c
// Preamble (init + null-check): 0x006b6240 - 0x006b624B
// Comparison loop body starts at: 0x006b624D  MOV AX, word ptr [ECX+0x14]   ← reads existing.seq
node = peer+0x9C.head;
while (node != NULL) {
    existing = node->value;
    if (existing.seq == incoming.seq
        && existing.is_below_0x32 == (incoming.type < 0x32)
        && existing.is_fragmented == incoming.is_fragmented
        && existing.frag_idx == incoming.frag_idx) {
        // Match found — refresh timer, don't create new entry
        break;
    }
    node = node->next;
}
```

> **Clar-2 (address precision)**: Pre-v5 phrasing cited the dedup loop at `0x006b6240`. That address marks the start of the init/null-check preamble; the actual comparison loop body begins at **`0x006b624D`** where the existing-entry `seq` is loaded. The mechanism is unchanged.

This is **O(N)** where N = total ACK-outbox entries (including stuck ones). As N grows:

| Session Duration | Originally Projected | Observed (34-min trace) | Dedup Cost per Reliable Msg |
|------------------|---------------------|------------------------|------------------------------|
| 2 minutes | ~13 entries | 11-13 entries | ~13 comparisons (negligible) |
| 30 minutes | ~600 entries | **20-33 entries** | **20-33 comparisons (negligible)** |
| 2 hours | ~2,400 entries | Not measured | Depends on quiet period duration |
| 4 hours | ~6,000 entries | Not measured | Depends on quiet period duration |

At the observed queue sizes (20-33 entries), the dedup cost is negligible: **33 entries × 60 msgs/sec = 1,980 4-field comparisons per second** — trivial even on 2002-era CPUs. Tick timing in the 34-minute battle trace was stable at ~95ms throughout, with zero observable degradation.

The original projection of progressive degradation assumed unbounded queue growth. In practice, the queue self-limits during active gameplay. However, the theoretical risk remains for extreme scenarios: hours-long sessions with extended quiet periods (lobby idle between rounds) where the queue could grow without the Pass 2 gate opening. Such conditions have not been observed in testing.

The dedup scan runs inside `ProcessIncomingMessages` which runs inside the network tick. At observed queue sizes this is not a concern, but if the queue grew to thousands of entries (possible only during sustained quiet periods), the network tick could fall behind.

---

## 6. Empirical Validation (2026-02-19)

Two real session traces were analyzed to validate the deadlock mechanism and impact projections.

### Trace Summary

| Property | Valentine's Day Battle | Feb 19 Instrumented |
|----------|----------------------|---------------------|
| Duration | 34 minutes | 91 seconds |
| Players | 3 (stock dedi host + 2 clients) | 1 client (stock dedi) |
| Trace size | 136 MB / 2.6M lines | 22K lines |
| Instrumentation | Wire-level packet trace only | ACK-HOOK + ACK-DIAG hooks |
| Peak ackOutQ | 20-33 entries | 11-13 entries |
| Tick timing | Stable ~95ms, no degradation | N/A (too short) |
| Session end | Clean exit, no errors | Clean disconnect |
| Fragment ACKs in client packets | Zero observed | N/A |

### Predicted vs Observed

| Metric | Doc Prediction | Observed | Assessment |
|--------|---------------|----------|------------|
| Queue size at 30 min | ~600 entries | 20-33 peak | **Overstated ~20x** |
| Memory leak at 30 min | ~45 KB | ~2.5 KB | **Overstated ~18x** |
| Dedup cost at 30 min | 600 comparisons/msg | 20-33 comparisons/msg | **Negligible in practice** |
| Tick degradation | Progressive | None observed (stable ~95ms) | **Not observed** |
| Long-session crash risk | "Most likely crash vector" | Session ended cleanly | **Not observed in 34 min** |

### Key Finding: Self-Limiting During Active Gameplay

The deadlock mechanism is **confirmed** — entries do get stuck at retx 3-8 when the Pass 2 gate fails. But during active gameplay (combat, movement, events), game traffic keeps msg_count > 0 most ticks, so the Pass 2 gate opens frequently and stuck entries get incremented toward retx 9 and cleaned up. The queue reaches a dynamic equilibrium of 10-33 entries rather than growing unboundedly.

The original projections assumed entries accumulate monotonically. In reality, accumulation and drainage alternate as traffic flows and pauses. The net effect is a small, bounded queue during active play.

### When the Bug Would Be Dangerous

The bug could still cause significant degradation under conditions not covered by our traces:

1. **Extended quiet periods** — hours-long sessions where players idle in lobby between rounds. The Pass 2 gate stays closed during quiet periods, allowing unbounded accumulation.
2. **High player counts** — 8-player sessions generate more reliable messages per tick, creating more ACK entries per quiet period.
3. **Very long sessions** — even with active gameplay draining the queue, a slow net positive accumulation rate over many hours could eventually reach problematic levels.

None of these conditions were present in our 34-minute, 3-player active combat trace. The theoretical risk at extreme session lengths remains, but it is less severe than originally projected.

> **Trace confidence note**: All numeric observations in §5 and §6 (peak queue sizes 11-13 / 20-33, ~95ms tick timing, 64% stale-ACK ratio, packet sizes) are trace-derived `[trace 2026-02-19]` projections, **not** binary derivations. They survive as observation, not as v5-anchored claims.

---

## 7. Supersedes netimmerse-transport ACK Retransmit Count Exhaustion Hypothesis [v5-validated 2026-05-28]

`docs/networking/netimmerse-transport-deep-dive.md` previously identified an "ACK Retransmit Count Exhaustion" sidebar as the root cause of long-session ACK-outbox accumulation. That framing is **binary-correct on its mechanism description but behaviorally insufficient** as the explanation of the observed bug.

### What netimmerse-transport claimed
> Entries with retx ≥ 3 can never be incremented past 9 (the cleanup threshold), so they accumulate forever.

### What the binary actually does
The cleanup at `entry+0x18 >= 9` (anchored at `0x006b5a96`) **does exist and is functional**. Pass 2 will happily walk an outbox of stale entries, increment each via `SetRetransmitCount`, and remove the ones that cross the retx ≥ 9 threshold. The retransmit-count mechanism is sound; it is **not** the bug.

### The actual root cause
The real bug is the **Pass 2 gate** at `0x006b5a01-0x006b5a1f`:

```
(msg_count > 0  OR  peer+0xBC != 0)  AND  peer+0xB4 > 0
```

When `msg_count == 0` (no Pass 1 hits because all outbox entries are at retx ≥ 3, and the retransmit/first-send queues are empty) **and** the peer is not disconnecting, Pass 2 **does not execute at all**. Entries are not "stuck at retx 9" — they are stuck at whatever retx they currently hold (3, 4, 5, 6, 7, or 8), because the loop that would advance them never runs.

This is a **control-flow gate problem**, not a counter problem. The two framings predict the same end-state (entries stuck in the queue) but suggest different fixes:
- netimmerse-transport's framing → "raise the cleanup threshold" or "add a parallel cleanup path"
- This doc's framing → "remove the `msg_count > 0` requirement from the Pass 2 gate" or "drive a dummy message through Pass 1 during quiet periods"

For OpenBC, the correct fix flows from this doc: Pass 2 must run **whenever the outbox is non-empty**, regardless of whether other traffic flowed this tick. The retx-count cleanup logic is already correct and should be carried over as-is.

The netimmerse-transport sidebar should be cross-linked to this doc for historical context but should not be treated as the canonical root-cause explanation.

---

## 8. Key Functions [v5-validated 2026-05-28]

| Address | Name | Role |
|---------|------|------|
| `0x006b55b0` | SendOutgoingPackets | 2-pass ACK + retransmit + first-send serialization (271 LOC worker) |
| `0x006b61e0` | HandleReliableReceived | ACK creation + O(N) dedup scan |
| `0x006b64d0` | HandleACK | Searches retransmit queue, removes matching entry (89 LOC worker) |
| `0x006b78d0` | RemoveFromQueue | Removes node at index from linked list |
| `0x006b8700` | CheckRetransmitTimer | Returns true if retransmit interval expired (reads msg+0x1C) |
| `0x006b8670` | SetRetransmitCount | Writes msg+0x18 **and** recomputes msg+0x1C interval (Clar-4) |
| `0x006b3a00` | TGWinsockNetwork base ctor | Sets `this[0x2B] = 0x400` (1024 base) |
| `0x006b9bf0` | TGWinsockNetwork derived ctor | Overrides `this[0x2B] = 0x200` (512 actual) |
| `0x006bd120` | TGHeaderMessage::ctor | ACK message constructor (0x44 bytes, vtable `0x008959ac`) |
| `0x006bd190` | TGHeaderMessage::WriteToBuffer | ACK serializer with remaining-space check (emits 4 or 5 bytes) |

## 9. Key Offsets [v5-validated 2026-05-28]

| Offset | Object | Field | Byte-anchor |
|--------|--------|-------|-------------|
| peer+0x64 | head | First-send queue head | read at `0x006b5842: MOV EAX,[ESI+0x64]` |
| peer+0x80 | head | Retransmit queue head | read at `0x006b5760: MOV EAX,[ESI+0x80]` |
| peer+0x84 | tail | Retransmit queue tail | read at `0x006b5981: MOV ECX,[ESI+0x84]` |
| peer+0x9C | head | ACK-outbox linked list head | read at `0x006b5a25: MOV EAX,[ESI+0x9c]` |
| peer+0xA0 | tail | ACK-outbox linked list tail | append at `0x006b6344: MOV ECX,[ESI+0xa0]` (HandleReliableReceived) |
| peer+0xA8 | cursor | Iteration cursor (node pointer) | written at `0x006b56b1: MOV [ESI+0xa8],ECX` |
| peer+0xAC | index | Iteration cursor (index counter) | init at `0x006b569c: MOV [ESI+0xac],0x0` |
| peer+0xB4 | count | ACK-outbox entry count (u32) | read at `0x006b567c` and `0x006b5a17` (Pass 2 gate) |
| peer+0xBC | u8 | is_disconnecting flag | read at `0x006b5a09: MOV AL, byte ptr [ESI+0xbc]` |
| msg+0x18 | u32 | retransmit_count | Pass 1 filter `0x006b56cc`, Pass 2 filter `0x006b5a5b`, cleanup `0x006b5a96` |
| msg+0x1C | float | retransmit_interval | recomputed inside `SetRetransmitCount` at `0x006b8670` (Clar-4 side effect) |
| msg+0x20 | float | last_send_time | written at `0x006b56ef: FSTP [EDI+0x20]` |
| TGNetwork+0xAC | u32 | Max packet buffer size | `0x400` from base ctor, overridden to `0x200` by WSN derived ctor |
