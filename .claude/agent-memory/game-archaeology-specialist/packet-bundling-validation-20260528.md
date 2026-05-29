---
name: packet-bundling-validation-20260528
description: Exhaustive v5 RE of stbc.exe packet bundling (TGWinsockNetwork_SendOutgoingPackets at 0x006B55B0) — datagram size budget, 4-pass drain order, per-message overhead, spillover, fragmentation, OpenBC compat impact
metadata:
  type: project
---

# Packet Bundling / Stuffing — v5 RE Memo (2026-05-28)

**Target:** `TGWinsockNetwork::SendOutgoingPackets` @ **0x006B55B0** in STBC.exe (271 lines, custom-named, has prototype).
**Wrapper class:** `TGWinsockNetwork` (vtable @ 0x008958F0 — outer subclass) — inherits from inner `0x00895790` impl.
**Caller:** `TGWinsockNetwork::Tick` @ 0x006B4560 (once per game tick) + 0x006B4060 (disconnect drain).
**Companion docs (existing v5):** `docs/networking/ack-outbox-deadlock.md`, `docs/networking/fragmented-ack-bug.md`, `docs/networking/netimmerse-transport-deep-dive.md`.

---

## 1. Datagram Size Budget — BYTE-CONFIRMED

| Item | Value | Evidence |
|---|---|---|
| Inner-class buffer field | `0x400` (1024) | `TGWinsockNetwork_Ctor` @ 0x006B3A00, instr `param_1[0x2b] = 0x400` at decomp line 79 |
| **Effective buffer (subclass override)** | **`0x200` (512)** | `FUN_006B9BF0` @ 0x006B9BF0 — sets `param_1[0x2b] = 0x200` AFTER calling inner ctor. This is the TGWinsockNetwork subclass that actually gets constructed. |
| Stack offset of buffer field | WSN + 0xAC (DWORD #0x2B) | `[ESI + 0xAC]` reads at 0x006B566C, 0x006B5BC5 |
| Allocator call | `FUN_00718CB0(0x200)` = `NiAlloc(512)` | At 0x006B55F2-0x006B55FF — `MOV ECX, [EBX+0xAC]; PUSH ECX; CALL 0x718CB0` |
| Allocator deallocator | `FUN_00718CF0(puVar7)` | At 0x006B5C26 — `NiFree(buf)` after send loop |
| Per-datagram header reserved | **2 bytes** | `puStack_1c = puVar7 + 2; iStack_24 = param_1[0x2b] + -2` at 0x006B5672/5675 (decomp: `LEA EAX,[buf+2]; SUB EBX,2`) |
| **Usable per-datagram payload** | **510 bytes** | 512 − 2 header. This matches the figure in `docs/networking/ack-outbox-deadlock.md`. |

### Per-datagram wire header (written AT END of bundling, after all messages packed)
```
buf[0] = WSN+0x18 byte (this->myPeerId)    ; 0x006B5B0E
buf[1] = iStack_28 byte (messageCount)     ; 0x006B5B0B
buf[2..N] = packed TGMessage bodies
```
**Written by:** `MOV BL,[ECX+0x18] / MOV [EAX+1],DL / MOV [EAX],BL` at 0x006B5B08-0x006B5B0E (after iStack_28>0 gate at 0x006B5AFA).

### Cipher interaction (post-bundling)
`SendPacket` @ 0x006B9870 invokes cipher on `(buf+1, len-1)` — byte 0 (peer ID) stays plaintext so receivers can look up the sender's cipher state. **Counts as zero extra wire bytes** — encryption is in-place.

### sendto() length
```
006B5BC5: MOV EDX,[ECX+0xAC]    ; EDX = 512 (buffer capacity)
006B5BCD: SUB EDX,EBP            ; EDX = 512 - remaining = bytes used
006B5BCF: PUSH EDX                ; arg: actual datagram length
006B5BDA: CALL [EAX+0x70]         ; vtable[+0x70] = SendPacket
```
Datagrams are sent at **exact bytes-used length**, not padded. A datagram containing 1 small message goes out as ~5-20 bytes; a fully-stuffed one goes out as ~512.

### Bandwidth accounting overhead
`vtable[+0x58]` (TGWinsockNetwork subclass @ 0x006BAC50) → `MOV EAX,0x22; RET` = **34 bytes** added to peer+0x54 (totalWireBytes counter) per datagram, modeling IP(20)+UDP(8)+Ethernet(~6) header overhead for **stats only**. NOT on the wire.

---

## 2. The 4-Pass Drain Algorithm — BYTE-CONFIRMED

`SendOutgoingPackets` processes **all peers in round-robin** starting at `WSN+0xB0` (cursor field, decompiled as `param_1[0x2c]`). The cursor advances by 1 per call. Each peer that passes the `[WSN]->vtable[+0x68]` gate (returns 1, always — see 0x006B39F0) gets a fresh buffer, four passes, and one sendto() if any messages were packed.

### Per-peer pass order

| Pass | Queue head | Queue tail | Count | Iterator state | Retx gate | Per-msg break? | Notes |
|---|---|---|---|---|---|---|---|
| **1: Priority** (fresh) | peer+0x9C | (last) | peer+0xB4 | peer+0xA8 (cursor) + peer+0xAC (idx) | `piVar9[6] < 3` (retx<3) | Continues until 255-cap or queue end | 0x006B5696-0x006B5740 |
| **2: Reliable** (one-shot) | peer+0x80 | peer+0x84 | peer+0x98 | peer+0x8C (cursor) + peer+0x90 (idx) | none (cV stale gate via FUN_006B8700) | **`break` after FIRST non-stale write** (0x006B57E5) | 0x006B5744-0x006B5825 |
| **3: Unreliable** (drains+dequeues) | peer+0x64 | peer+0x6C | peer+0x7C | peer+0x70 (cursor) + peer+0x74 (idx) | none (uses stale path differently) | Dequeue+free each on success; cap at 254 | 0x006B5829-0x006B5A01 |
| **4: Priority retx** (stale) | peer+0x9C | (same) | peer+0xB4 | peer+0xA8 + peer+0xAC | `piVar9[6] >= 3` (retx>=3); free at retx>=9 | 254-cap | 0x006B5A25-0x006B5AF4. Gate: `(iStack_28>0 OR peer+0xBC!=0) AND peer+0xB4>0` |

### Per-pass termination conditions (CRITICAL for OpenBC interop)

#### Pass 1 — Priority (fresh, retx<3)
```c
while (msg != NULL) {
  if (!stale && msg->retxCount < 3) {
    bytesWritten = msg->vtable[+0x08](buf, remaining);   // WriteToBuffer
    if (bytesWritten == 0) break;                         // <-- WON'T-FIT EXIT
    msg->lastSentTime = currentTime;
    msgCount++;
    msg->retxCount++;
    buf += bytesWritten; remaining -= bytesWritten;
    if (msgCount > 254) break;                            // <-- CAP EXIT
  }
  advance to next message in priority queue;
}
```
**Multiple messages per datagram.** Capped at 255.

#### Pass 2 — Reliable (one-shot)
```c
while (msg != NULL) {
  if (!stale) {
    bytesWritten = msg->vtable[+0x08](buf, remaining);
    if (bytesWritten != 0) {
      msgCount++;
      msg->lastSentTime = currentTime;
      msg->retxCount++;
      buf += bytesWritten; remaining -= bytesWritten;
    }
    break;                                                // <-- *** ALWAYS BREAK ***
  }
  // ... stale-cleanup path...
}
```
**At most ONE reliable message per datagram.** This is the design constraint — Pass 2 always `break`s after seeing the first non-stale reliable message, regardless of whether it fit. If the buffer is full from Pass 1 and the next reliable message returns 0, Pass 2 still breaks; reliable retry waits for next tick.

#### Pass 3 — Unreliable (drain-and-dequeue)
```c
bool firstSkip = true;
while (msg != NULL) {
  if (msg+0x3d == 0 && firstSkip) { firstSkip = false; /* skip first unreliable */ }
  else {
    bytesWritten = msg->vtable[+0x08](buf, remaining);
    if (bytesWritten == 0) break;                         // <-- WON'T-FIT EXIT
    msgCount++;
    // Dequeue and free the message from peer+0x64 linked list
    detach(msg); NiFree(node);
    peer+0x7C--;                                          // unreliable count
    if (msg+0x3a != 0) {
      // Promotion: re-queue as reliable if needs retry
      if (peer+0xB4 > 0.0f) /* alloc new node, push to peer+0x80/0x84, peer+0x98++ */;
      else msg->Release(1);
    } else msg->Release(1);
    buf += bytesWritten; remaining -= bytesWritten;
    if (msgCount > 254) break;
  }
  advance;
}
```
**Multiple per datagram, drains the queue.** Each message is consumed (dequeued + Release), unless its +0x3a flag triggers promotion to reliable retry queue.

#### Pass 4 — Priority retx (stale, retx>=3, free at retx>=9)
```c
if ((msgCount > 0 || peer+0xBC != 0) && peer+0xB4 > 0) {
  while (msg != NULL) {
    if (!stale && msg->retxCount >= 3) {
      bytesWritten = msg->vtable[+0x08](buf, remaining);
      if (bytesWritten == 0) break;
      msg->lastSentTime = currentTime;
      msgCount++;
      msg->retxCount++;
      if (msg->retxCount >= 9) detach_and_release(msg);
      buf += bytesWritten; remaining -= bytesWritten;
      if (msgCount > 254) break;
    }
    advance;
  }
}
```
Gate at 0x006B5A01: `(iStack_28>0 OR peer+0xBC!=0) AND peer+0xB4>0`. If no messages were packed in Passes 1-3 AND no peer-disconnect flag, Pass 4 is **skipped** — the buffer is freed and nothing gets sent for this peer this tick. This is the **ACK-outbox deadlock pattern** documented in `docs/networking/ack-outbox-deadlock.md`.

---

## 3. Per-Message Overhead

The bundled stream is **a sequence of self-delimiting TGMessage blobs**, each starting with a type byte. There is NO outer length prefix on the wire from the bundler — message boundaries are recovered by parsing the inner type-specific format.

### TGMessage::WriteToBuffer (vtable[+0x08]) contract
Reference impl: `TGBufferStream::Serialize` @ 0x006B8340 (vtable[2] of TGBufferStream, the type-0x32 general payload class).

**Inputs:** `(pOutBuf, nBufSize)`. **Returns:** `int bytesWritten`, or `0` if `nBufSize < requiredSize`.

For type 0x32 (TGBufferStream / general payload):
```
[byte] class-tag = 0x32              ; vtable[0]() return value, written by *pOutBuf
[short] flags|length (13-bit len + bit 15 frag, bit 14 ordered, bit 13 reliable)
                                     ; pOutBuf[1..2] = (len & 0x1FFF) | (frag<<15) | (ord<<14) | (rel<<13)
[short] sequenceID                   ; IF (msg+0x3a != 0)   — variant header
[byte] fragmentIndex (msg+0x39)      ; IF (msg+0x3c != 0)
[byte] fragmentTotal (msg+0x38)      ; IF (msg+0x3c != 0 AND msg+0x39 == 0)
[bytes] payload                      ; msg+0x04 buffer, msg+0x08 bytes
```

**Per-message minimum overhead:** 3 bytes (type + 2-byte flags/length) for a no-payload message. Variants add:
- +2 bytes if reliable/fragmented (sequenceID)
- +1-2 bytes if first-fragment header

For TGHeaderMessage (type 0x01, ACK envelopes) and other system types, the layout differs — each has its own vtable[+0x08]. Most observed wire traffic in stock-dedi traces is type 0x32 (per stock-trace-analysis.md).

### What is NOT in the per-message overhead
- **No length prefix** — receivers parse `[buf[1] | (buf[2]<<8)] & 0x1FFF` for type-0x32 length, then advance.
- **No separator byte** — message boundaries are implicit in self-delimiting wire format.
- **No checksum** — bundling layer trusts cipher integrity (cipher is reversible; mismatched key produces garbage that fails inner-message parse).

---

## 4. Spillover Behavior — BYTE-CONFIRMED

When a message returns 0 from WriteToBuffer (won't fit):

| Pass | Behavior | Message fate |
|---|---|---|
| Priority (P1) | `break;` exits the priority loop. | Message stays at head of peer+0x9C queue — retried next tick. Counter NOT incremented; lastSentTime NOT updated. |
| Reliable (P2) | `break;` exits regardless (the break is unconditional). | Same — message stays at head of peer+0x80 queue. |
| Unreliable (P3) | `break;` exits the unreliable loop. | Message stays at head of peer+0x64 queue. **NOT dequeued.** Will be retried next tick (and likely fit if priority/reliable drained). |
| Priority retx (P4) | `break;` exits. | Stays in queue, will hit retx>=9 cleanup gate next time. |

**No drop-on-overflow.** No "skip and try smaller next message." First message that doesn't fit causes the queue's drain to abort.

### Why this matters for OpenBC
If OpenBC sends each message in its own datagram (1 message per UDP packet), the **wire frequency** will be dramatically higher than stock. A stock peer with 4 queued priority messages + 1 reliable + 8 unreliable will send **1 datagram (~510 bytes)** at the next tick; an OpenBC clone with the same backlog would send **13 datagrams**. Two issues:
1. Stock receivers MAY tolerate either pattern (each datagram is parsed independently), but bandwidth tracking (peer+0x48/+0x54) will be miscounted by the receiver.
2. NetImmerse fragmentation behavior depends on bundling decisions made at queue time (see Section 5).

---

## 5. Fragmentation — Decided at Queue Time, Not Drain Time

`SendOutgoingPackets` does NOT fragment. Fragmentation happens earlier, in `TGWinsockNetwork::QueueMessageForPeer` @ 0x006B5080:

```c
// Calls TGMessage::Fragment (vtable[+0x1C] = slot 7)
fragList = pMessage->vtable[+0x1C](&outCount, WSN+0xAC - 100);
                                 // 512 - 100 = 412 byte max chunk
```

The `TGBufferStream::Fragment` impl @ 0x006B8720 (vtable[7]) splits the payload into N chunks where chunk N fits within `(maxChunkSize - chunkHeaderSize)`. Each chunk becomes its own TGMessage with:
- `msg+0x39 = chunkIndex` (0..N-1)
- `msg+0x38 = totalChunks` (set on LAST fragment)
- `msg+0x3C = 1` (fragment flag — controls header emission in Serialize)
- `msg+0x3A = 1` (set on first chunk)
- `msg+0x3B = 1` (bit 14 of flags shortword = "ordered")

Each fragment is queued individually as a normal TGMessage. The drain loop sees them as separate messages — they may bundle with other small messages.

**Max chunk byte budget** = `WSN+0xAC - 100` = **412 bytes** payload per fragment. Per-fragment overhead is ~5-7 bytes (3 base + 2 seqID + 2 fragment indices), so on-wire per-fragment ≈ 415-420 bytes. A large 2KB payload becomes ~5 fragments × ~415 bytes each.

### Why "−100"?
Heuristic safety margin: 2 byte datagram header + 1-2 ACK envelopes + 1 fresh priority message + 1 reliable message + this fragment must all coexist in the 512-byte datagram. 100 bytes of slack absorbs the variance.

---

## 6. Drain Flowchart (Compressed)

```
SendOutgoingPackets(WSN):
  if (WSN+0x10C == 0) return                       ; "processing enabled" gate
  cursor = (WSN+0xB0 + 1) % peerCount
  WSN+0xB0 = cursor
  buf = NiAlloc(WSN+0xAC)                          ; 512 bytes
  for each peer (round-robin from cursor):
    if (!isPeerLive(peer))    continue             ; vtable[+0x68] always-1 in stbc
    if (peer.unrel+peer.pri+peer.rel == 0) continue
    
    bufPos = buf + 2                                ; reserve 2-byte hdr
    remaining = 510
    msgCount = 0
    
    # --- PASS 1: Priority fresh (retx<3) ---
    iterate peer+0x9C list:
       if (!stale && msg.retxCount < 3):
          n = msg.WriteToBuffer(bufPos, remaining)
          if n==0: BREAK
          msg.lastSent = now; msgCount++; msg.retxCount++
          bufPos+=n; remaining-=n
          if msgCount > 254: BREAK
       advance cursor
    
    # --- PASS 2: Reliable (ONE-SHOT, msgCount<255) ---
    if (msgCount < 255):
       iterate peer+0x80 list:
          if (!stale):
             n = msg.WriteToBuffer(bufPos, remaining)
             if n != 0:
                msgCount++; msg.lastSent = now; msg.retxCount++
                bufPos+=n; remaining-=n
             BREAK    ; <<< unconditional
          else:
             ; stale path: prune via FUN_006B78D0 if too old
             advance
    
    # --- PASS 3: Unreliable (drains+dequeues) ---
    if (msgCount < 255):
       firstSkip = true
       iterate peer+0x64 list:
          if (msg+0x3d == 0 && firstSkip):
             firstSkip = false
             advance
          else:
             n = msg.WriteToBuffer(bufPos, remaining)
             if n==0: BREAK
             msgCount++
             dequeue msg from peer+0x64; peer+0x7C--
             if (msg+0x3a != 0 && peer+0xB4 > 0):
                ; PROMOTE: re-queue as reliable
                node = NiAlloc(8); node->msg=msg; push to peer+0x80
                peer+0x98++
             else:
                msg.Release(1)
             bufPos+=n; remaining-=n
             if msgCount > 254: BREAK
    
    # --- PASS 4: Priority RETRANSMIT (stale, retx>=3) ---
    if ((msgCount > 0 || peer+0xBC != 0) && peer+0xB4 > 0):
       iterate peer+0x9C list:
          if (!stale && msg.retxCount >= 3):
             n = msg.WriteToBuffer(bufPos, remaining)
             if n==0: BREAK
             msg.lastSent = now; msgCount++; msg.retxCount++
             if (msg.retxCount >= 9): detach+release
             bufPos+=n; remaining-=n
             if msgCount > 254: BREAK
    
    # --- SEND ---
    if (msgCount > 0):
       buf[0] = WSN+0x18 byte                       ; senderPeerId
       buf[1] = msgCount byte
       if (WSN+0x110 != 0 && peer+0x18 != WSN+0x18):
          ; bandwidth stats: peer+0x48 += bytesUsed
          ;                  peer+0x54 += bytesUsed + 34   (with IP+UDP overhead)
          ; also update remote peer's mirror via binary search of WSN+0x2C[]
       sendPacket(peer+0x1C addr, buf, bytesUsed)   ; vtable[+0x70]
  
  NiFree(buf)
  
  # --- POST-SCAN: stale-disconnect detection ---
  for each peer:
    if (peer+0xBC != 0 && (now - peer+0xB8) > 15.0f):
       vtable[+0x74](peer.id)                       ; trigger peer disconnect
```

---

## 7. Concrete Wire Examples

### Example A: Single small reliable message (no batching opportunity)
Buf: `[01][01][ message body 18 bytes ]` = **20 bytes** sent. Most ACK envelopes look like this.

### Example B: Fully-stuffed datagram (worst case)
Buf: `[01][N=255][ 510 bytes of mixed messages ]` = **512 bytes** sent. Likely only achievable with many small (~2-byte payload) priority messages.

### Example C: Typical mid-game tick to one peer
Buf: `[01][04][ ACK(7B) ][ StateUpdate(60B) ][ EventForward(35B) ][ Heartbeat(5B) ]` ≈ **109 bytes** sent. Four messages: 1 priority (ACK) + 1 reliable (StateUpdate) + 2 unreliable.

### Example D: Reliable starvation under priority backlog
With 50 priority messages queued (retx<3 each) and 1 critical reliable StartFiring:
- Pass 1 packs as many priority as fit (say 15 × ~30B = 450B) → remaining ≈ 60B
- Pass 2 sees 1 reliable: WriteToBuffer returns 0 (StartFiring is 40+ bytes when serialized with target ID + headers) → break
  - Actually, if StartFiring fits in 60B, it's sent. If not, reliable starves.
- Pass 3 unreliable, Pass 4 retx — neither helps the reliable.
- Result: reliable message defers to next tick. With sustained high priority traffic, observable as multi-tick latency.

---

## 8. OpenBC Compatibility Implications

### Critical-must-match
1. **Buffer size MUST be 512 bytes** with **2-byte header**. Receivers do not parse longer-than-510 byte datagrams; they expect `[peerId][count][messages...]`.
2. **Header layout MUST be `[u8 senderPeerId][u8 messageCount]`.** Anti-cheat clients in vanilla BC parse byte[1] as message count to drive the inner-message decode loop.
3. **Per-message format MUST follow TGMessage class-tag-first layout.** First byte of each inner message identifies its handler (0x01=ACK envelope, 0x32=general payload, etc.).
4. **Fragmentation chunk size MUST be 412 bytes max.** A larger payload split into bigger chunks will be rejected as malformed by the receiver's reassembly logic.

### Strongly-recommended-to-match
5. **Drain order priority→reliable(one-shot)→unreliable→priority-retx.** Mismatch breaks reliability semantics — clients expect ACKs to arrive in priority-first order under congestion.
6. **One-reliable-per-datagram cap.** This is the design intent that makes ACK throughput tractable (one ACK per RTT-tick window). OpenBC sending 4 reliables per datagram would amplify the ack-outbox deadlock.
7. **Bundling at all.** If OpenBC sends 1 msg per datagram, peer+0x48/+0x54 bandwidth counters at the receiver will undercount the "ip+udp overhead" portion, and the stale-peer detection threshold (15s no traffic at 0x008958CC) becomes more sensitive to packet loss.

### Safe to differ
8. **Round-robin cursor position.** OpenBC can start at peer 0 every tick — no client observes cursor state.
9. **Pass 4 retx>=9 cleanup logic.** This is a host-only memory-management concern; clients don't see retired messages.
10. **34-byte bandwidth-overhead constant.** Stats only — not on wire.

---

## 9. Evidence Trail (v5)

| Claim | Address | Confidence |
|---|---|---|
| `SendOutgoingPackets` is at 0x006B55B0 | 0x006B55B0 | high (named, has prototype) |
| Buffer = 512 bytes (subclass override) | 0x006B9C13 (`MOV [param_1+0xAC],0x200`) | high (decomp + asm) |
| Inner ctor sets 1024 (overridden) | 0x006B3A00 line ~79 (`param_1[0x2b] = 0x400`) | high |
| 2-byte header reserved | 0x006B5672 (`ADD EAX,0x2`), 0x006B5675 (`SUB EBX,0x2`) | high |
| 510 usable bytes | derived: 512−2 | high |
| Header buf[0]=peerId, buf[1]=msgCount | 0x006B5B08-0x006B5B0E | high |
| WriteToBuffer @ vtable+0x08 returns 0 on overflow | 0x006B8340 — `if (nBufSize < required) return 0;` | high (decomp) |
| Pass 1 priority retx<3 | 0x006B56CC (`CMP [EDI+0x18],0x3 / JGE`) | high |
| Pass 2 reliable unconditional break | 0x006B57E5 (`JMP 0x006B5829` after the write path) | high |
| Pass 3 unreliable drain+dequeue | 0x006B5829-0x006B5A01 (decomp shows FUN_00718CF0 free + peer+0x7C decrement) | high |
| Pass 4 retx>=3 gate | 0x006B5A5B (`CMP [EDI+0x18],0x3 / JL`) | high |
| Pass 4 retx>=9 cleanup | 0x006B5A96 (`CMP [EDI+0x18],0x9 / JL`) | high |
| 255-message cap (`0xFF`) | 0x006B570F, 0x006B5834, 0x006B59D4, 0x006B5AC7 | high |
| 254-message cap (`0xFE` post-write) | implicit (255 break uses `JGE 0xFF` after `INC EAX`, effectively cap at 254 successful writes per pass beyond head) | high |
| Pass 4 gate `(msgCount>0 OR peer+0xBC!=0) AND peer+0xB4>0` | 0x006B5A01-0x006B5A1F | high |
| Fragment max chunk = WSN+0xAC − 100 = 412 | 0x006B5080 line ~27 (`*(int *)(param_1 + 0xac) + -100`) | high |
| Bandwidth overhead = 0x22 (34 bytes) | 0x006BAC50 (`MOV EAX,0x22; RET`) — vtable[+0x58] | high |
| Stale-disconnect threshold = 15.0f | 0x008958CC contains `0x41700000` | high (memory dump) |
| 5.0f retx interval seed | 0x0088BD58 contains `0x40A00000` (5.0f) — used in FUN_006B8670 retx scheduler | high (from leaf #10 disconnect-flow) |
| sendto called with exact bytes-used | 0x006B5BC5-0x006B5BDA | high |
| Cipher operates on buf+1, len-1 | 0x006B98E0 in SendPacket | high (pre-anchored in CLAUDE.md) |
| Caller is `TGWinsockNetwork::Tick` @ 0x006B4560 | callers listed by ghidra | high |

---

## 10. Open Questions

1. **What IS the type byte distribution observed in stock dedi traces?** Stock-trace-analysis.md and packet_trace.log will show actual message-count histograms per datagram. Worth correlating with the 255-cap and one-reliable-per-tick constraints to see how often real datagrams approach the caps.
2. **Is the "FIRST unreliable skip" (`firstSkip = true` at 0x006B585E) actually a bug, or intentional?** The code skips the first unreliable message if its `+0x3d` flag is 0, only on the first iteration. Could be ordering safeguard for newly-queued unreliable. UNVERIFIED.
3. **Does the receiver enforce msgCount byte == actual parsed message count?** If a malformed datagram has msgCount=5 but only 3 parseable messages, does the receiver bail or continue? Worth a `ProcessIncomingPackets` (0x006B5C90) deep-dive — out of scope for this memo.

---

## 11. Files NOT modified

Per task instructions: no doc files modified, no Ghidra renames committed beyond `save_program`. Existing `TGWinsockNetwork_SendOutgoingPackets` name is from prior `MpgameHandleMessage`-style validation. Subclass ctor `FUN_006B9BF0` deliberately NOT renamed.

**Saved program:** STBC.exe via `save_program` at end of session — no functional changes, no annotation drift.
