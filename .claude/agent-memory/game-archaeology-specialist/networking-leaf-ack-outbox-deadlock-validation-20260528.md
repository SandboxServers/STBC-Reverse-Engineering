---
name: networking-leaf-ack-outbox-deadlock-validation-20260528
description: Networking leaf #9 — ACK-outbox deadlock validation. Mechanism BYTE-CONFIRMED at 0x006b5a01-0x006b5a11 gate. Pass 1/2 filters, cleanup threshold, 510-byte buffer all anchored. ZERO mechanism corrections. 1 Clar (dedup address slightly off). Supersession of retx-exhaustion hypothesis CONFIRMED.
metadata:
  type: project
---

# Networking Leaf #9: ACK-Outbox Deadlock — v5 Validation Memo

**Date**: 2026-05-28
**Doc**: `docs/networking/ack-outbox-deadlock.md` (308 lines)
**Validation status**: ANCHORED — full mechanism byte-confirmed; supersession of retx-exhaustion claim verified.

## Verdict

**STRONG ANCHOR**. The doc is the most rigorously verifiable networking leaf reviewed so far. The deadlock mechanism, two-pass filter ranges, cleanup threshold, buffer sizing, struct offsets, and all 9 function addresses survive byte-level cross-check at the cited disassembly addresses.

The doc correctly **supersedes** netimmerse-transport's "retransmit count exhaustion" hypothesis (which framed the bug as "entries with retx ≥ 3 cannot be incremented past 9"). The actual bug is at the **Pass 2 gate** (0x006b5a01), not the retransmit count logic — the cleanup mechanism at `entry+0x18 ≥ 9` exists and is functional, but it cannot fire when the gate fails (`msg_count == 0 && peer+0xBC == 0`).

## What was validated (byte-level)

### 1. Buffer size (Section 1)
- Base `TGWinsockNetwork_Ctor` (0x006b3a00) sets `param_1[0x2b] = 0x400` — **CONFIRMED**
- WSN override (0x006b9bf0) sets `param_1[0x2b] = 0x200` — **CONFIRMED**
- `006b5672: ADD EAX,0x2` + `006b5675: SUB EBX,0x2` → 510 usable bytes — **CONFIRMED**

### 2. Pass 1 / Pass 2 filters (Section 2)
- Pass 1 filter `entry+0x18 < 3` at `006b56cc: CMP [EDI+0x18],0x3; JGE` — **CONFIRMED**
- Pass 2 filter `entry+0x18 >= 3` at `006b5a5b: CMP [EDI+0x18],0x3; JL` — **CONFIRMED**
- Pass 2 cleanup at `entry+0x18 >= 9` at `006b5a96: CMP [EDI+0x18],0x9; JL` — **CONFIRMED**
- `msg_count >= 255` break at `006b570f` (Pass 1), `006b5acc` (Pass 2), etc. — **CONFIRMED**

### 3. The Pass 2 gate (Section 3 — THE DEADLOCK)
At 0x006b5a01-0x006b5a11:
```
006b5a01: MOV EAX,[ESP+0x14]         # iStack_28 (msg_count)
006b5a05: TEST EAX,EAX
006b5a07: JG  0x006b5a17              # bypass disconnecting check if msg_count > 0
006b5a09: MOV AL,[ESI+0xbc]           # peer+0xBC = is_disconnecting (byte)
006b5a0f: TEST AL,AL
006b5a11: JZ  0x006b5af4              # skip Pass 2 if both zero
006b5a17: MOV EAX,[ESI+0xb4]          # peer+0xB4 = ACK count
006b5a1d: TEST EAX,EAX
006b5a1f: JLE 0x006b5af4              # skip Pass 2 if outbox empty
```
Gate is `(msg_count > 0 OR peer+0xBC != 0) AND (peer+0xB4 > 0)` — **CONFIRMED**.

Doc's Section 2 only mentions the first two predicates; the `peer+0xB4 > 0` predicate is a meaningful additional gate but doesn't affect the deadlock analysis (deadlock requires entries to exist, so peer+0xB4 > 0 is implied).

### 4. Supersession of retx-exhaustion hypothesis
Doc's claim:
> entries with retx 3-8 become stuck: never sent again, never cleaned up, never freed

Mechanism: Pass 1 skips them (retx not < 3); Pass 2 would send them and increment toward 9, BUT Pass 2 only runs when gate passes. When `msg_count == 0` (no Pass 1 hits, retransmit/first-send queues empty) AND peer not disconnecting, Pass 2 is gated off and entries remain at their current retx forever.

This is a strictly different mechanism than netimmerse-transport's "retx count exhaustion" — that doc framed it as a counter problem; the actual bug is a control-flow gate problem. **Supersession is correct and warranted.**

### 5. Peer struct offsets (Section 8)
| Offset | Doc Claim | Confirmed Via |
|--------|-----------|---------------|
| peer+0x64 | first-send head | `006b5842: MOV EAX,[ESI+0x64]` |
| peer+0x80 | retransmit head | `006b5760: MOV EAX,[ESI+0x80]` |
| peer+0x84 | retransmit tail | `006b5981: MOV ECX,[ESI+0x84]` |
| peer+0x9C | ACK-outbox head | `006b5a25: MOV EAX,[ESI+0x9c]` |
| peer+0xA0 | ACK-outbox tail | `006b6344: MOV ECX,[ESI+0xa0]` (HandleReliableReceived append) |
| peer+0xA8 | iteration cursor | `006b56b1: MOV [ESI+0xa8],ECX` |
| peer+0xAC | cursor index | `006b569c: MOV [ESI+0xac],0x0` |
| peer+0xB4 | outbox count | `006b567c: MOV EAX,[ESI+0xb4]` |
| peer+0xBC | disconnecting (u8) | `006b5a09: MOV AL,byte ptr [ESI+0xbc]` |

All **CONFIRMED**.

### 6. TGMessage offsets (Section 8)
| Offset | Doc Claim | Confirmed Via |
|--------|-----------|---------------|
| msg+0x18 | retx count | `006b56cc: CMP [EDI+0x18],0x3` |
| msg+0x1C | retransmit interval (float) | FUN_006b8700 reads `*(float *)(param_1 + 0x1c)` |
| msg+0x20 | last_send_time (float) | `006b56ef: FSTP [EDI+0x20]` writes current time |

All **CONFIRMED**.

### 7. Function addresses (Section 7)
| Address | Doc Name | Verified |
|---------|----------|----------|
| 0x006b55b0 | SendOutgoingPackets | YES — Ghidra symbol `TGWinsockNetwork_SendOutgoingPackets` |
| 0x006b61e0 | HandleReliableReceived | YES — `TGWinsockNetwork_HandleReliableReceived` |
| 0x006b64d0 | HandleACK | YES — `TGWinsockNetwork_HandleACK` |
| 0x006b78d0 | RemoveFromQueue | YES — sig matches: (list, index) → removed value |
| 0x006b8700 | CheckRetransmitTimer | YES — returns true if last_send+interval < now |
| 0x006b8670 | SetRetransmitCount | YES — writes msg+0x18, recomputes msg+0x1C |
| 0x006b9bf0 | TGWinsockNetwork::ctor | YES — sets buffer 0x200 |
| 0x006bd120 | TGHeaderMessage::ctor | YES — sets vtable 0x008959ac |
| 0x006bd190 | TGHeaderMessage::WriteToBuffer | YES — emits 4/5 byte ACK |

## Triage

### Corrections (C)
**None.** ZERO wire/mechanism corrections. The doc's claims pass every byte-level cross-check.

### Clarifications (Clar)

**Clar1** (Section 2, Pass 2 gate): Doc says gate is `msg_count > 0 OR peer+0xBC != 0`. **Actual gate** is `(msg_count > 0 OR peer+0xBC != 0) AND peer+0xB4 > 0`. The `peer+0xB4 > 0` clause means "ACK outbox is non-empty" — which is implicit in the deadlock scenario (if outbox is empty, there's nothing to deadlock). Recommend clarifying for completeness.

**Clar2** (Section 5.3, dedup search address): Doc cites "0x006b6240" as the start of the dedup walk. The actual loop body begins at **0x006b624D** (where `MOV AX,word ptr [ECX+0x14]` reads existing.seq); 0x006b6240-0x006b624B is the init/null-check preamble. Off by ~13 bytes — code is correct, address is approximate.

**Clar3** (Section 2 address ranges): Pass 2 cited as "0x006b5a50 - 0x006b5b90". Actual Pass 2 loop is 0x006b5a50-0x006b5af4; 0x006b5af4-0x006b5b90 is the packet-finalize block (writing peer_id + msg_count to buffer[0..1] and calling sendto via vtable). Range overstates by extending into post-loop finalize.

**Clar4** (Section 2 Pass 1 line 38 "retx_count++"): The pass 1 increment is via `FUN_006b8670(piVar9[6] + 1)` at 0x006b56fe, which calls `SetRetransmitCount` with new count. The function call also **recomputes the retransmit interval** based on the new count (and msg+0x2C mode). The doc's pseudocode `entry.retx_count++` omits this side effect. Minor — affects subsequent retransmit timing but not the deadlock mechanism.

### Open Questions (OQ)
None substantive.

## Cross-references

- **fragmented-ack-bug.md** — listed as related; not validated here, but the ACK-outbox accumulation evidence comes from there.
- **disconnect-flow.md** — relevant because peer+0xBC = 1 is one of the gate exits.
- **netimmerse-transport-deep-dive.md** — the "Section 5 fragment-window" hypothesis was binary-correct but doesn't explain the *observed* bug. This doc (ack-outbox-deadlock.md) is the canonical root cause.

## Verification artifacts saved

Ghidra database saved. No renames or comments applied — all addresses already had custom names (TGWinsockNetwork_*) from prior v5 work.

## Recommendation for documentation-writer

This doc is **publication-ready** with minor `[v5-clarify]` annotations on Section 2's gate (add `AND peer+0xB4 > 0`) and Section 5.3's dedup address (0x006b624D not 0x006b6240). The empirical validation section (Section 6) is well-bounded and honest about projections-vs-observed.

The doc's **status: v5-validated** for the mechanism. The empirical projections retain `[trace]` confidence (Valentine's Day trace observation, not binary-derived).
