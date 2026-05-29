---
name: trace-mining-verification-20260529
description: Stock-dedi trace mining answering 7 OpenBC verification questions (REPAIR byte count, bundling, relay matrix, StateUpdate cadence, force-resend, chat ratio, coverage gaps)
metadata:
  type: project
---

# Trace Mining Verification (2026-05-29)

Mined existing stock BC 1.1 dedi traces (OBSERVE_ONLY, zero patches) to answer OpenBC
verification questions BEFORE deciding on new live captures. 5 of 7 fully ANSWERED from
existing data; 2 partial; 3 genuine new-capture gaps identified.

Primary source: `logs/battle-of-valentines-day/packet_trace.log` (136 MB, 3-player FFA DM,
138,695 datagrams). Corroborated by `logs/collision test/stock-dedi/packet_trace.log`.

Peers: Peer#0=127.0.0.1:56325 (host's own client), Peer#1=98.187.133.199 (remote),
Peer#2=172.59.83.80 (remote), Peer#3=255.255.255.255:27900 (GameSpy broadcast, ignore).

---

## Q1 — REPAIR_COMPLETED / REPAIR_CANNOT byte count — ANSWERED

Both event codes appear ONLY in Valentine's trace (21 total occurrences; absent from
collision + self-destruct traces). Two distinct PythonEvent (0x06) factory forms observed.

**REPAIR_COMPLETED (0x00800074), factory 0x00000101** — `logs/battle-of-valentines-day/packet_trace.log:975008` (datagram #47266 msg 2, S->C):
```
wire: 32 16 80 D5 02 | 06 | 01 01 00 00 | DF 00 80 00 74 00 00 40 85 00 00 40
```
- transport: `32`=GameData, `16 80`=flags_len LE 0x8016 (reliable+totalLen 22), `D5 02`=seq
- TGMessage body (opcode 0x06 .. end) = **17 bytes**
- factory_class_id = 0x00000101 (bytes `01 01 00 00`) — NOT 0x010C
- payload after factory = `DF 00 80 00 74 00 00 40 85 00 00 40` = 12 bytes
- full PythonEvent payload (factory+body) = 16 bytes
- totalLen field (22) counts the full TGMessage INCLUDING transport prefix (5) + body (17)

**REPAIR_CANNOT (0x00800075), factory 0x0000010C (TGObjPtrEvent)** — `logs/battle-of-valentines-day/packet_trace.log:690616` (datagram #33820 msg 0, S->C):
```
wire: 32 1A 80 68 02 | 06 | 0C 01 00 00 | 74 00 80 00 75 00 08 40 68 00 08 40 72 00 08 40
```
- transport: flags_len LE 0x801A (reliable+totalLen 26), seq `68 02`
- TGMessage body (opcode 0x06 .. end) = **21 bytes**
- factory_class_id = 0x0000010C (bytes `0C 01 00 00`)
- payload after factory = 16 bytes; full PythonEvent payload (factory+body) = 20 bytes

### 20-vs-21 contradiction RESOLVED
The contradiction is opcode-inclusive vs payload-only counting for the **TGObjPtrEvent (0x010C)** form:
- **20 bytes** = PythonEvent payload only (factory_id 4 + eventCode 4 + obj_ptr/args 12)
- **21 bytes** = full TGMessage body INCLUDING the leading opcode byte 0x06
The doc `docs/protocol/tgobjptrevent-class.md:198` claim "21 bytes (1 opcode + 16 base + 4 obj_ptr)"
is CORRECT and matches the wire. Use 21 when counting from opcode; 20 for payload-after-opcode.

NOTE: REPAIR events arrive via BOTH factory forms. The 0x101 form (12-byte payload) and the
0x10C form (16-byte payload) both carry eventCode 0x74/0x75 — they are different event classes
(0x101 = subsystem-index event, 0x10C = TGObjPtrEvent with src+tgt obj IDs).

---

## Q2 — Packet bundling (multiple TGMessages per datagram) — ANSWERED

msgs= (messageCount) distribution across all 138,695 datagrams:
- msgs=1: 58,911 | msgs=2: 31,526 | msgs=3: 35,769 | msgs=4: 5,663 | msgs=5: 3,150
- msgs=6: 1,500 | msgs=7..16: tapering | tail up to msgs=110
- **MAX messageCount = 110**

2-byte header confirmed from raw bytes — datagram #136324 (S->C, len=491) at
`logs/battle-of-valentines-day/packet_trace.log:2610644`:
```
0000: 01 6E 32 17 00 1C 0D 01 00 40 ...
```
- byte[0] = `01` = peerId/direction (S=1)
- byte[1] = `6E` = 0x6E = **110** = messageCount
- byte[2+] = first message (`32`=GameData transport type)

Datagrams are VARIABLE length, NOT padded to 512:
- Zero datagrams at exactly 512 bytes; only 1 datagram >= 500 bytes (the 508/491 outliers)
- Confirms 4-pass drain produces real bundling, no fixed-size padding.
Header format `[peerId/dir:1][msgCount:1][messages...]` CONFIRMED from wire.

---

## Q3 — Per-handler relay matrix (3-player data) — ANSWERED

Counts by HEADER direction (unambiguous; 70,431 C->S + 68,266 S->C = 138,695 total).

| Opcode | C->S | S->C | Ratio | Relay behavior |
|--------|------|------|-------|----------------|
| 0x06 PythonEvent | 0 | 3825 | n/a | SERVER-GENERATED only (never client-originated) |
| 0x07 StartFiring | 978 | 1940 | 1:2 | RELAYED to other 2 peers |
| 0x08 StopFiring | 477 | 971 | 1:2 | RELAYED |
| 0x0A SubsysStatus | 21 | 42 | 1:2 | RELAYED |
| 0x0D PythonEvent2 | 75 | 0 | n/a | ABSORBED (not relayed) |
| 0x11 RepairPriority | 3 | 6 | 1:2 | RELAYED |
| 0x12 SetPhaserLevel | 13 | 23 | ~1:2 | RELAYED |
| 0x13 HostMsg | 4 | 0 | n/a | ABSORBED (host-only) |
| 0x14 DestroyObject | 0 | 0 | n/a | NEVER on wire (death=Explosion+respawn) |
| 0x15 CollisionEffect | 317 | 0 | n/a | ABSORBED — host generates 0x06 damage instead |
| 0x19 TorpedoFire | 363 | 726 | 1:2 | RELAYED |
| 0x1A BeamFire | 52 | 104 | 1:2 | RELAYED |
| 0x1B TorpTypeChange | 4 | 8 | 1:2 | RELAYED |
| 0x1C StateUpdate | 58049 | 141490 | ~1:2.4 | RELAYED + server-generated |
| 0x29 Explosion | 0 | 59 | n/a | SERVER-GENERATED only |
| 0x2C ChatMessage | 15 | 42 | 1:N | RELAYED to ALL incl sender (see Q6) |

### Relay PROOF (BeamFire) — `logs/battle-of-valentines-day/packet_trace.log:31026`
- #31026 C->S Peer#0: two BeamFire (obj 0x77, 0x78, target 0x40080068)
- #31027 S->C Peer#1: IDENTICAL two BeamFire
- #31028 S->C Peer#2: IDENTICAL two BeamFire
- #31029 S->C Peer#0: ACK ONLY (sender NOT echoed)
Star topology: 1 inbound -> N-1 outbound to OTHER peers (combat events not echoed to sender).

CollisionEffect absorption corroborated by collision test (2-player):
0x15 = 2353 C->S, 0 S->C; 0x06 = 0 C->S, 200 S->C.

---

## Q4 — StateUpdate cadence — ANSWERED (~10 Hz)

Measured obj=0x40040096 -> Peer#1 over 15,684 samples:
- median inter-packet 96 ms, mean 101.6 ms = **~10.4 Hz per ship per peer**
- dominant buckets: 80-99ms (9268) + 100-119ms (6280) = 99% of samples
Confirms the ~10Hz tick-rate claim.

---

## Q5 — Force-resend at 1.0s for idle ships — PARTIAL / CONTRADICTS #194

Active ships emit continuously at 10Hz (no idle gaps to measure). Lower-activity objects
(obj=0x400801F3, 2058 samples) show gap clustering at **450-500 ms (85 samples)** and
~200ms (84), NOT a clean 1000ms heartbeat. Larger gaps (1-7s) correlate with ship death/
respawn or peer-disconnect windows, not a periodic force-resend.

Suggests stock force-resend interval may be ~0.5s, not 1.0s — but cannot isolate cleanly
because no ship was truly idle (parked) in this combat-heavy trace. NEEDS isolated capture
of a stationary ship to confirm the exact force-resend period.

---

## Q6 — Chat 1:2 ratio — ANSWERED (actually 1:N, echo to ALL)

Aggregate 15 C->S : 42 S->C is NOT 1:2. Per-message trace
(`logs/battle-of-valentines-day/packet_trace.log:49864`, chat "IT WORKS" from Peer#1):
- #3029 C->S Peer#1 (sender)
- #3030 S->C Peer#1 (echoed back to SENDER)
- #3031 S->C Peer#2
- #3032 S->C Peer#0

Host broadcasts each chat to ALL clients INCLUDING the sender = **1 inbound : N outbound**
(N = player count = 3 here). Per-peer receive counts are symmetric: Peer#0/1/2 each got
exactly 14 chats. The "1:2" hypothesis was wrong; true rule is broadcast-to-all-with-echo.
This differs from combat events (0x07/0x1A/0x19) which relay to OTHERS only (no sender echo).

---

## Q7 — Coverage gaps — ANSWERED

- **TEAM_DM opcodes 0x3F/0x40/0x41: ZERO** in Valentine (it was FFA DM). GENUINE GAP.
- **Late-joiner catch-up (RequestObj 0x1E): ZERO.** All 3 joins (0x2A NewPlayerInGame) occurred
  in first ~70s (22:08:36, 22:08:51, 22:09:46) of a 33.5-min session = no mid-battle join.
  No 0x1E + 0x29 replay catch-up captured. GENUINE GAP.
- **Cloak: present but NOT isolated.** StartCloaking (event 0x008000E3) via 0x06 at
  `:1051358`; StopCloak/CLK flag (712x) interleaved with heavy combat. Cannot cleanly measure
  shield-disable timing against ambient state churn. PARTIAL — needs isolated cloak capture.

---

## REMAINING CAPTURE GAPS (what genuinely needs a NEW live session)

1. **TEAM_DM session** — opcodes 0x3F/0x40/0x41 + team scoring wire format. Zero coverage.
2. **Late-joiner catch-up** — a player joining MID-BATTLE to capture RequestObj (0x1E) +
   0x29 Explosion replay + object catch-up cascade. Existing joins were all at game start.
3. **Isolated cloak transition** — 1v1 with a cloaking ship, minimal other combat, to
   measure StartCloak/StopCloak (0x0E/0x0F) + shield-disable timing precisely.
4. **Isolated idle/parked ship** — a stationary ship with no movement to nail down the exact
   force-resend interval (Q5: data hints ~0.5s, not the documented 1.0s).

Everything else (REPAIR byte count, bundling, full combat relay matrix, StateUpdate cadence,
chat broadcast rule) is ANSWERED from existing traces — no new capture needed.
