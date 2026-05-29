---
name: authority-ordering-validation-20260529
description: Definitive STOCK server-vs-client AUTHORITY matrix + ORDER-OF-OPERATIONS validation for the MP wire protocol, consolidated from the v5 corpus plus NEW Ghidra digging on the StateUpdate 0x20 round-robin. KEY RESULT for OpenBC #186 flicker/drift — start_idx is a TOP-LEVEL linked-list node index (NOT a flat subsystem index); children are absorbed inline by WriteState/ReadState recursion and do NOT advance the index. ser_list order = Ship__AddSubsystemToLists insertion order (tail-append) = LoadPropertySet/AddToSet order from the ship-class hardpoint .py, deterministic + identical host/client. Receiver apply loop is bounded by stream-exhaustion (payloadLength), not by node count.
metadata:
  type: project
---

# Authority + Order-of-Operations Validation — 2026-05-29

**Verdict:** Q1/Q2 consolidated from v5 corpus (high confidence). **Q3 (the crux) NEWLY
re-derived from binary this session — DEFINITIVE.** Q4 consolidated from packet-bundling
+ transport memos. Ghidra saved (no functional changes).

**Crux answer up front (for OpenBC #186):**
`start_idx` in StateUpdate flag 0x20 is a **TOP-LEVEL linked-list node index**, NOT a flat
subsystem index. The sender increments the index **once per top-level node**; each node's
`WriteState` (vtable +0x70) serializes itself + all children depth-first **inline** without
touching the index. The receiver mirrors this exactly: it walks `start_idx` `node->next`
pointers from the head, then calls each node's `ReadState` (vtable +0x74) which consumes the
node's own + children's bytes inline. **If OpenBC treats start_idx as a flat (children-counted)
index, HP lands on the wrong subsystem → exactly the #186 flicker/wrong-damage symptom.**

---

## Newly-anchored functions (this session)

| Function | Address | What was confirmed |
|---|---|---|
| Ship__WriteStateUpdate | 0x005B17F0 | flag-0x20 loop: index written ONCE pre-loop, INC once per top-level node, child recursion inline. Disasm 0x005B1E73–0x005B1F1F. |
| Ship__ReadStateUpdate | 0x005B21C0 | flag-0x20 apply: walk start_idx × node->next, then ReadState per node bounded by `streamPos < payloadLength`. |
| ShipSubsystem__WriteState | 0x0056D320 | condition byte + `for child in [+0x20][0..+0x1c-1]: child.vtable[+0x70]` recursion. |
| ShipSubsystem__ReadState | 0x0056D390 | condition byte read + identical child recursion via vtable[+0x74]. |
| ShipSubsystem__GetChildSubsystem | 0x0056C570 | reads LOCAL instance+0x1c (count) + instance+0x20 (array) — child count NOT on wire. |
| Ship__AddSubsystemToLists | 0x005B3E50 | TAIL-append to ship+0x284 list (preserves insertion order). Node = [data][next][prev]. |

---

# Section 1 — Originator Matrix

Who ORIGINATES each wire message type, and whether it hits the wire. "Originator" = the peer
that first emits the message onto the wire (before any host relay).

## 1a — StateUpdate 0x1C dirty flags

The whole 0x1C message is originated by BOTH directions, but the flag SET differs by direction
because of the `!IsHost` branch in Ship__WriteStateUpdate (0x005B17F0, disasm 0x005b1c76+):

| Flag | Name | Originator | On wire? | Direction | Evidence |
|---|---|---|---|---|---|
| 0x01 | POSITION_ABSOLUTE | both | yes | C→S and S→C | sender 0x005b1d65; force-resend or delta-overflow sticky |
| 0x02 | POSITION_DELTA (CV4 p=1, 5B) | both | yes | C→S and S→C | sender 0x005b1dce |
| 0x04 | FORWARD (CV3, 3B) | both | yes | C→S and S→C | sender 0x005b1dee |
| 0x08 | UP (CV3, 3B) | both | yes | C→S and S→C | sender 0x005b1e0d |
| 0x10 | SPEED (CF16, 2B) | both | yes | C→S and S→C | sender 0x005b1e2c |
| 0x40 | CLOAK (1 bit) | both | yes | C→S and S→C | sender 0x005b1e4a; only if ship+0x2dc cloak device present |
| **0x20** | **SUBSYSTEMS** | **HOST only** | yes | **S→C only** | gated by `!IsHost` branch at 0x005b1c7a; 19,997/0 captured S→C |
| **0x80** | **WEAPONS** | **CLIENT only** | yes | **C→S only** | set in the `!IsHost` (bVar16) branch at 0x005b1cc8; 10,459/0 captured C→S |

**Why the 0x20/0x80 split (byte-anchored at 0x005b1c76–0x005b1ccd):**
- `bVar16 = !DAT_0097fa8a` (IsHost flag; note cascade-corrected naming — 0x0097FA8A = IsHost).
- If `!IsHost` (i.e. a client, OR a host computing its own ship's outbound-to-self view): take
  branch at 0x005b1cc8 → `bValue |= 0x80` (weapons). **Never sets 0x20.**
- Else (host path): subject to friendly-fire + player-count gate (0x0097FAA2 ff-flag; FUN_006a2650
  active-player count; threshold 2 for dedicated/no-local-player, 3 for host-with-local-player);
  if not skipped → `bValue |= 0x20` (subsystems). **Never sets 0x80.**
- Net: C→S = 0x8x/0x9x (WPN), S→C = 0x2x/0x3x (SUB). Confirmed against 30K+ stock packets and
  the 2026-02-26 authority-boundary trace audit (flags=0xDD C→S, 0x20/0x3E S→C).

## 1b — Game opcodes 0x02–0x2A

| Opcode | Name | Originator | On wire? | Direction | Notes |
|---|---|---|---|---|---|
| 0x00 | Settings | host | yes | S→C | sent after checksums pass (MultiplayerWindow disp FUN_00504c10) |
| 0x01 | GameInit | host | yes | S→C | single byte trigger |
| 0x02 | ObjCreate | host | yes | S→C | host authoritative object spawn |
| 0x03 | ObjCreateTeam | host | yes | S→C | as 0x02 + team |
| 0x04/0x05 | (dead) | — | no | — | jump-table DEFAULT |
| 0x06 | PythonEvent | both | yes | C→S relayed to NoMe; host-generated S→C | primary event transport, 3432/session |
| 0x07 | StartFiring | client | yes | C→S, host relays to "Forward" | weapon fire begin |
| 0x08 | StopFiring | client | yes | C→S, relay | |
| 0x09 | StopFiringAtTarget | client | yes | C→S, relay | |
| 0x0A | SubsysStatus | client | yes | C→S, relay | subsystem on/off toggle |
| 0x0B | AddToRepairList | client | yes | C→S, relay | repair queue add |
| 0x0C | ClientEvent | client | yes | C→S, relay (preserve=0) | |
| 0x0D | PythonEvent2 | both | yes | as 0x06 | alternate Python path |
| 0x0E | StartCloak | client | yes | C→S, relay | event 0x008000E3 |
| 0x0F | StopCloak | client | yes | C→S, relay | event 0x008000E5 |
| 0x10 | StartWarp | client | yes | C→S, relay | |
| 0x11 | RepairListPriority | client | yes | C→S, relay | |
| 0x12 | SetPhaserLevel | client | yes | C→S, relay | TGCharEvent, event 0x008000E0 |
| 0x13 | HostMsg (self-destruct req) | client | yes | C→S | 1-byte, no payload |
| 0x14 | DestroyObject | host | yes | S→C | (NOT used for ship death — see ship-death-lifecycle) |
| 0x15 | CollisionEffect | client (originator detects) | yes | C→S, host validates + may relay | 84/session; client-detected, host proximity-validated |
| 0x16 | UICollisionSetting | host | yes | S→C | MultiplayerWindow disp |
| 0x17 | DeletePlayerUI | host | yes | S→C | scoreboard removal |
| 0x18 | DeletePlayerAnim | host | yes | S→C | "joined/left" float text |
| 0x19 | TorpedoFire | client | yes | C→S, relay + local create | 897/session |
| 0x1A | BeamFire | client | yes | C→S, relay + local apply | |
| 0x1B | TorpTypeChange | client | yes | C→S, relay | event 0x008000FD |
| **0x1C** | **StateUpdate** | **both (see 1a)** | yes | C→S (WPN) + S→C (SUB) | 30K+/session |
| 0x1D | ObjNotFound | both | yes | request/response | |
| 0x1E | RequestObj | client | yes | C→S | |
| 0x1F | EnterSet | host | yes | S→C | enter game set |
| 0x29 | Explosion | host | yes | **S→C only** | host-authoritative AoE damage |
| 0x2A | NewPlayerInGame | host | yes | S→C | join handshake |

## 1c — Python-tier 0x2C–0x39 (via SendTGMessage, bypass C++ dispatcher)

| Byte | Name | Originator | On wire? | Direction |
|---|---|---|---|---|
| 0x2C | CHAT_MESSAGE | both | yes | C→S relayed to all |
| 0x2D | TEAM_CHAT_MESSAGE | both | yes | C→S relayed to team |
| 0x35 | MISSION_INIT_MESSAGE | host | yes | S→C |
| 0x36 | SCORE_CHANGE_MESSAGE | host | yes | S→C (server-authoritative score delta) |
| 0x37 | SCORE_MESSAGE | host | yes | S→C (full score sync) |
| 0x38 | END_GAME_MESSAGE | host | yes | S→C |
| 0x39 | RESTART_GAME_MESSAGE | host | yes | S→C |

---

# Section 2 — Authoritative Source Matrix

Who is the source of truth, how it replicates, and whether the receiver trusts blindly.

| State | Authoritative source | How replicated | Receiver validates? |
|---|---|---|---|
| **Ship position / orientation / velocity** | **OWNER CLIENT** | Owner sends 0x1C (POS/DELTA/FWD/UP/SPEED) C→S; host re-broadcasts S→C as its own shaped 0x1C | **NO** — host does NOT recompute physics; trusts + relays (server-side-computation §8). Receiver gates only on timestamp monotonicity (`this+0x88 < gameTime`). |
| **Subsystem HP (condition)** | **HOST** | Host computes full sim (damage/repair/power), broadcasts via 0x1C flag 0x20 round-robin S→C | **NO** — client blindly applies `ReadState` (condition byte → instance+0x30). No client-side recompute of the received value. |
| **Shield HP (overall subsystem condition)** | **HOST** (overall byte only) | flag 0x20, ShieldGenerator via base ShipSubsystem::WriteState (1 byte) | **NO** — applied blindly. BUT **per-facing shield HP is NOT on the wire** — each peer maintains its own 6-facing distribution; only the overall condition byte syncs (server-side-computation §6). |
| **Hull HP** | **HOST** | flag 0x20, HullSubsystem (ship+0x2C4) emits 1 condition byte (mirrors ship+0x14C) | **NO** — applied blindly. Note: condition byte is a UI/HUD %; the real hull HP is ship+0x14C. |
| **Weapon charge / health** | **OWNER CLIENT** (reports its weapon health upstream) | 0x1C flag 0x80 C→S only: `[idx][health_byte]` pairs | **host applies** via vtable[+0x84] SetWeaponHealth. Damage itself is **peer-computed independently** (server-side-computation §2) — no per-hit damage message. |
| **Cloak state** | **OWNER CLIENT** (intent), replicated both ways | 0x1C flag 0x40 (1 bit); also opcodes 0x0E/0x0F relayed | applied blindly (receiver calls 0055f360/0055f380). |
| **Power / battery levels** | **HOST** (computes), client authors slider intent | PowerSubsystem::WriteState (Format 3, 2 battery bytes) in flag 0x20 S→C; slider intent via 0x0A relay | host computes + broadcasts; client applies blindly. PoweredSubsystem also sends powerPctWanted byte for remote ships. |
| **Collision damage** | **HOST validates + recomputes** | client sends 0x15 (contacts); host validates bounding-sphere proximity (< DAT_008955c8 = 26.0f gap), converts to 0x008000FC, recomputes full damage pipeline | **YES** — only message type with real server-side validation. Contact points trusted; damage distribution recomputed. |
| **Explosion / AoE damage** | **HOST** | opcode 0x29 S→C only | client applies blindly. |
| **Ship death / respawn** | **HOST** | ET_OBJECT_EXPLODING → PythonEvent 0x06 to NoMe; NOT DestroyObject 0x14 | client accepts. |
| **Score** | **HOST** | 0x36/0x37 Python-tier S→C | client accepts. |
| **Repair progress / completion** | **HOST authoritative health**, all peers also tick locally | health via flag 0x20; completion events (ET_REPAIR_COMPLETED 0x800074, etc.) via 0x06 | health applied blindly; events accepted. Both peers run repair for responsiveness; host StateUpdate corrects drift. |

**Resolved contradiction:** server-side-computation §8 ("TRUST CLIENT, no server physics") vs the
summary table's "StateUpdate: SERVER is AUTHORITATIVE." Both are true on different axes —
**position is owner-client-authored** (host relays, does not recompute), while **subsystem/power/HP
state is host-computed** (host runs full sim, broadcasts). 0x1C is a HYBRID message: upstream
carries owner motion+weapon input (0x8x), downstream carries host subsystem state (0x2x). The
2026-02-26 boundary audit is the authoritative reconciliation.

---

# Section 3 — Subsystem Serialization ORDER (the crux)

## 3.1 — The exact ordering rule

The `ser_list` IS the ship's `+0x284` doubly-linked list (head=ship+0x284, tail=ship+0x288,
count=ship+0x280). Order is determined by **insertion order into that list**, which is:

**`Ship__AddSubsystemToLists` (0x005B3E50) TAIL-appends each subsystem as it is created.** New
node: `node[0]=data, node[1]=next=NULL, node[2]=prev=oldTail`; oldTail->next = node; tail = node.
**Tail-append preserves call order** — head→tail reads subsystems in the order they were added.

Add order is driven by `Ship__SetupProperties` / `LoadPropertySet`, which walks the ship-class
**hardpoint `.py` `AddToSet` order**. So:

> **ser_list order = LoadPropertySet/AddToSet order from the ship-class hardpoint file, top-level
> subsystems only (children are nested under their parent's WriteState, not separate list nodes).**

This was validated byte-for-byte for 4 ships in per-ship-subsystem (mid #12); the construction
rule is confirmed here from the AddSubsystemToLists tail-append disasm.

## 3.2 — Stability + host/client symmetry

- **Stable across the session:** the list is built once at ship spawn (DeferredInitObject /
  Ship__SetupProperties) and not reordered. Subsystems are never re-sorted; removal uses a free
  list but stock ships don't remove subsystems mid-game. → start_idx is meaningful tick-to-tick.
- **Identical host vs client:** both peers construct the ship from the **same hardpoint `.py` +
  property files** loaded via ObjCreate (same NIF/property data on both ends). The construction is
  **deterministic from ship class** — same AddToSet order → same insertion order → same list order.
  Child counts come from each instance's own `+0x1c` (GetChildSubsystem reads LOCAL fields), so they
  match too. **Conclusion: for a given ship class, host and client ser_lists are byte-identical in
  order and shape.** (Mod risk: a client with a different hardpoint `.py` for the same species WILL
  desync the order — see Section 5.)

## 3.3 — start_idx semantics — DEFINITIVE: TOP-LEVEL NODE INDEX

**Sender (Ship__WriteStateUpdate 0x005B17F0, disasm 0x005b1e73–0x005b1f1f):**
```
; init (only when cursor==NULL — i.e., first ever 0x20 for this peer):
  cursor = ship[+0x284]   (tracker+0x30)
  index  = 0              (tracker+0x34)
; emit start_index ONCE, before the loop:
  AL = byte(tracker+0x34)         ; low byte of the DWORD index
  WriteChar(AL)                   ; <-- start_index on the wire
; loop while (streamPos - startPos) < 10:
  node = cursor
  cursor = node->next             ; node[1] — advance ONE node
  node->data->vtable[+0x70](stream, isOwnShip)   ; WriteState: self + children INLINE
  index++                         ; tracker+0x34 INC — ONCE per top-level node
  if cursor==NULL: { cursor = head; index = 0 }   ; wrap
  if cursor == startCursor: break  ; full-cycle guard
```

**Receiver (Ship__ReadStateUpdate 0x005B21C0, flag-0x20 block):**
```
start = (int)(char) ReadChar(stream)     ; read start_index (signed char!)
node = ship[+0x284]                       ; head
for (; start != 0; start--) node = node->next   ; skip start_index TOP-LEVEL nodes
while (streamPos < payloadLength) {
    if (node==NULL) break
    subsys = node->data
    node = node->next                     ; advance ONE node
    subsys->vtable[+0x74](stream, gameTime)   ; ReadState: self + children INLINE
    if (node==NULL) node = ship[+0x284]   ; wrap to head
}
```

**Both sides increment by ONE top-level node per WriteState/ReadState call.** Children are
absorbed inside WriteState/ReadState (ShipSubsystem::WriteState/ReadState recurse over
`instance+0x20[0..instance+0x1c-1]` via GetChildSubsystem — see 0x0056D320/0x0056D390). **Children
do NOT advance the top-level index.** Therefore:

> **start_idx counts TOP-LEVEL ser_list nodes, NOT flattened (children-included) subsystems.**

This is the definitive answer to Q3.5. A flat-index interpretation would over-skip on the receiver
and land HP on the wrong subsystem.

## 3.4 — Round-robin window mechanics (byte-by-byte)

| Mechanic | Value | Evidence |
|---|---|---|
| Budget | **10 bytes** for subsystems (`CMP EAX,0xA / JGE` at 0x005b1ebf, 0x005b1f1a) | sender |
| Budget measure | `GetPos(stream) - startPos` (stream cursor delta, NOT a byte count) | 0x005b1e82/1eb8 |
| start_index field | tracker+0x34 (DWORD persisted), **emitted as low byte** via WriteChar | 0x005b1ea0 |
| cursor field | tracker+0x30 (persisted Node*) | 0x005b1e89 |
| Index width on wire | **1 byte**, read as **signed char** by receiver | 0x005b21c0 flag-0x20 `(int)(char)` |
| Per-node advance | cursor = node->next (one node) | 0x005b1ed3/1ed8 |
| Index advance | INC once per node | 0x005b1eec |
| Wrap | cursor==NULL → cursor=head, index=0 | 0x005b1ef4 |
| Stop (sender) | budget hit (≥10) OR full cycle (cursor==startCursor at 0x005b1f0d) | sender |
| Stop (receiver) | **streamPos >= payloadLength** (NOT a node count) | receiver |

**Critical asymmetry (not a bug, but OpenBC must replicate):** the **sender** caps at a 10-byte
budget and guards against a full cycle; the **receiver** has NO node-count limit — it applies
ReadState repeatedly **until the stream payload is exhausted**. The receiver figures out how many
subsystems were sent purely from how many bytes remain. This works because each subsystem's
WriteState/ReadState is self-delimiting (condition byte + known child structure from the local
instance). The receiver does NOT need to know the count — it consumes until empty, advancing the
list cursor per node, wrapping at the tail.

**Implication:** the budget is a per-tick fairness cap; the next tick resumes from the persisted
`tracker+0x30/0x34` cursor (NOT reset). So over several ticks, the round-robin sweeps the whole
list. A typical 10-byte budget fits ~3-6 base subsystems (1 byte each) or fewer Powered ones
(1 byte + 1 bit [+1 byte powerPct for remote]).

**1-byte index wraparound caveat:** tracker+0x34 is a DWORD that only resets on a NULL-cursor
wrap. It is written to the wire as a single byte and read as a **signed char**. For any stock ship
(<=11 top-level subsystems) this never overflows. A mod ship with >127 top-level subsystems would
wrap the signed byte and desync — practically irrelevant but worth noting.

## 3.5 — Sovereign-class worked example

From per-ship-subsystem (mid #12), Sovereign AddToSet/LoadPropertySet top-level order (11 nodes):

| ser_list index (start_idx value) | Top-level subsystem | Ship slot | WriteState format | Wire bytes (own ship) |
|---|---|---|---|---|
| 0 | Hull | +0x2C4 | base | 1 |
| 1 | Shield Generator | +0x2C0 | base | 1 |
| 2 | Sensor | +0x2C8 | Powered | 1 + 1bit |
| 3 | Warp Core (reactor/PowerSubsystem) | +0x2B0 | Power | 1 + 2 battery |
| 4 | Impulse Engines | +0x2CC | Powered (+ children) | 1 + children |
| 5 | Torpedoes | +0x2B4 | weapon (children inline) | 1 + N children |
| 6 | Repair | +0x2D8 | Powered | 1 + 1bit |
| 7 | Phasers | +0x2B8 | weapon (children inline) | 1 + N children |
| 8 | Tractors | +0x2D4 | weapon | 1 + children |
| 9 | Warp Engines | +0x2D0 | base | 1 |
| 10 | Bridge | (no named slot) | base | 1 |

Worked round-robin (10-byte budget, starting fresh):
- Tick 1: start_idx=0 → writes Hull(0), Shield(1), Sensor(2), WarpCore(3)... until ~10 bytes
  consumed; persists cursor at e.g. node 4, index=4.
- Tick 2: start_idx=4 → resumes at Impulse(4), Torpedoes(5)... etc.
- Eventually wraps at node 10→NULL → cursor=head, index=0; next tick start_idx=0 again.

A client receiving `[start_idx=4][impulse bytes][torpedo bytes...]` walks 4 `node->next` hops to
reach Impulse, then applies ReadState per node. Because order is identical, Impulse's bytes land on
Impulse. **If the client mis-walked (flat index, or different order), Impulse's HP would land on
e.g. Torpedoes → flicker.**

---

# Section 4 — Intra-tick Order of Operations

## 4.1 — TGNetwork::Update sequence (per tick)

From netimmerse-transport + packet-bundling: `TGWinsockNetwork::Tick` (0x006B4560) per game tick:
1. **Send** outgoing: `SendOutgoingPackets` (0x006B55B0) — drains per-peer queues, builds datagrams.
2. **Process** incoming: `ProcessIncomingPackets` (0x006B5C90) — reads sockets, reassembles fragments.
3. **Dispatch** to handlers: parsed messages routed to the 3 dispatchers (NetFile / MultiplayerGame
   / MultiplayerWindow) + Python SendTGMessage path.

StateUpdate generation (`FUN_0069ee50` SendStateUpdates, called from MultiplayerGame per-tick
Update FUN_0069edc0) iterates all 16 player slots and calls `ship->WriteStateUpdate(slot)` per
active remote ship, enqueuing each 0x1C as an **unreliable** TGMessage (msg+0x3a=0).

## 4.2 — The 4-pass drain order (per peer, per datagram)

From packet-bundling (0x006B55B0): buffer = 512 bytes, 2-byte header `[peerId][msgCount]`, 510
usable. Four passes in order:
1. **Priority fresh** (retx<3) — multiple per datagram, cap 255.
2. **Reliable** (one-shot) — **at most ONE reliable message per datagram** (unconditional break).
3. **Unreliable** (drain + dequeue) — multiple; StateUpdate 0x1C lives here (unreliable).
4. **Priority retransmit** (stale, retx>=3; free at retx>=9) — gated.

So within one datagram to one peer, ACKs (priority) precede the single reliable message, which
precedes unreliable StateUpdates. StateUpdates for multiple ships to the same peer bundle together
in pass 3, **one full ship's 0x1C per message** (WriteStateUpdate emits a complete self-contained
message per ship — ships are NOT interleaved within a message).

## 4.3 — Client-side ordering dependencies (what must arrive before what)

| Dependency | Required order | Consequence if violated |
|---|---|---|
| **ObjCreate before StateUpdate** | 0x02/0x03 for an object_id must precede any 0x1C for that id | Dispatcher (MpgameHandleStateUpdate 0x0069FF50) looks up the ship by net_id; if not found → ObjNotFound (0x1D) path, StateUpdate dropped. **Hard dependency.** |
| **Settings/GameInit before gameplay** | 0x00 then 0x01 before any 0x1C/events | Client not in playable state; updates ignored until in-set. |
| **EnterSet (0x1F) before set-scoped state** | ship must be in a set for some handlers | Set membership gates rendering/sensor. |
| **SUB block vs subsystem-referencing events** | NO hard ordering | flag-0x20 health and PythonEvents (e.g. REPAIR_COMPLETED) are independent paths; both are eventually-consistent. A SUB block showing a subsystem at partial HP and a later REPAIR_COMPLETED event showing it full will reconcile on the next SUB sweep. **No deadlock**, but transient mismatch is possible (and is itself a flicker source if cadence is uneven — see 2026-02-26 audit). |
| **Per-tick StateUpdate self-consistency** | within one 0x1C, flags read in fixed wire order 0x01,0x02,0x04,0x08,0x10,0x40,0x20,0x80 | Receiver reads strictly in this order; any reorder corrupts the stream cursor. |

## 4.4 — Ordering hazards

1. **start_idx desync** (Section 3) — the #1 hazard. Order mismatch or flat-vs-toplevel index
   mismatch corrupts all subsequent subsystem applications in the batch.
2. **Stream-exhaustion apply** — receiver trusts that the sender packed self-delimiting subsystems.
   If OpenBC's WriteState byte-count for a subsystem differs from stock (e.g., emits an extra byte),
   the receiver's `streamPos < payloadLength` loop mis-frames every following subsystem.
3. **Unreliable 0x1C loss** — StateUpdates are unreliable; a dropped datagram just means the next
   tick's update corrects it. No retransmit. This is by design (eventual consistency at ~10Hz).
4. **Cadence** — 2026-02-26 audit: stock S→C 0x20 ~10Hz (avg 0.101s); OpenBC ~7Hz observed. Slow/
   uneven cadence alone produces visible subsystem-bar flicker even with correct framing.

---

# Section 5 — OpenBC Implications

## 5.1 — ser_list ordering rule OpenBC MUST replicate

Build each ship's subsystem `ser_list` as a **flat, ordered list of TOP-LEVEL subsystems in
hardpoint `AddToSet`/`LoadPropertySet` order** (the same order the hardpoint `.py` registers them).
Children (e.g., individual phaser banks under PhaserSystem, engine pairs under ImpulseEngine) are
**nested under their parent**, NOT separate ser_list entries. The list must be:
- Built once at spawn, never reordered.
- Identical on host and client for a given ship class (load from the same hardpoint definition).

## 5.2 — start_idx semantic OpenBC MUST use

`start_idx` = **index into the TOP-LEVEL ser_list** (children-excluded). On send: write the
top-level index of the first node in this tick's batch. On receive: skip exactly `start_idx`
top-level nodes from the head, then apply each subsystem's ReadState (which itself consumes that
subsystem's + its children's bytes). **Do NOT count children when interpreting start_idx.** This is
the direct fix for #186 if OpenBC currently uses a flat index.

## 5.3 — Receiver loop bound

OpenBC's receive loop must apply subsystems **until the StateUpdate payload is exhausted**, NOT for
a fixed count. There is no count field — the byte budget on the sender and stream-exhaustion on the
receiver are the only bounds. Each subsystem's wire size must EXACTLY match stock per-format
(base=1B; Powered=1B+1bit[+1B remote]; Power=1B+2B battery) or every following subsystem in the
batch mis-frames.

## 5.4 — Cursor persistence + budget

OpenBC must persist a per-peer `(cursor, index)` round-robin state per ship and resume from it each
tick (NOT restart at 0). Apply the 10-byte subsystem budget (and 6-byte weapon budget) measured by
output cursor delta. Wrap to head at the tail, resetting index to 0.

## 5.5 — Authority replication

- **Subsystem/shield/hull/power HP: host-authoritative** — OpenBC server must run the full sim and
  broadcast flag-0x20 S→C. Do NOT expect clients to compute these.
- **Position/velocity: owner-client-authored** — relay, do not recompute (server-side-computation §8).
- **Weapons (flag 0x80): client→server only**; damage is peer-local (no per-hit damage message).
- **Collision (0x15): validate proximity (gap < 26.0f) + recompute damage** — the only validated path.
- **Per-facing shield HP is NOT replicated** — only the overall ShieldGenerator condition byte. Do
  not try to sync 6-facing values; each peer keeps its own.

## 5.6 — Cadence parity

Target ~10Hz per-ship S→C 0x20 cadence (stock avg 0.101s). The 2026-02-26 audit shows OpenBC's
~7Hz contributes to flicker independent of framing correctness. Both must be fixed for clean parity.

## 5.7 — Mod compatibility note

ser_list order is derived from the hardpoint `.py`. If a modded client uses a different hardpoint
for the same species than the host, the ser_lists differ in order → start_idx desync → subsystem
flicker. This is intrinsic to the protocol (no order is transmitted). OpenBC inherits this property.

---

# Evidence Trail (v5)

| Claim | Address | Confidence |
|---|---|---|
| start_idx written once pre-loop, INC once per top-level node | 0x005b1ea0 / 0x005b1eec | high (disasm) |
| sender child recursion inline (no index touch) | 0x0056D320 (WriteState) | high (decompile) |
| receiver skips start_idx × node->next, applies per node | 0x005b21c0 flag-0x20 block | high (decompile) |
| receiver apply bounded by streamPos < payloadLength | 0x005b21c0 | high (decompile) |
| receiver reads start_idx as signed char | 0x005b21c0 `(int)(char)` | high (decompile) |
| child count from LOCAL instance+0x1c (not wire) | 0x0056C570 GetChildSubsystem | high (decompile) |
| ser_list tail-append preserves order; node=[data][next][prev] | 0x005B3E50 | high (decompile) |
| 10-byte subsystem budget; 6-byte weapon budget | 0x005b1ebf / 0x005b1f66 | high (disasm) |
| 0x20=host-only / 0x80=client-only split via !IsHost branch | 0x005b1c76–0x005b1ccd | high (disasm + 30K trace) |
| collision proximity threshold 26.0f | DAT_008955c8 | high (prior memos) |
| 4-pass drain order; 0x1C is unreliable (msg+0x3a=0) | 0x006B55B0 / 0x005b2168 | high (prior + disasm) |

# Cross-References

- [[stateupdate-validation-20260528]] — mid #8, the 8 dirty bits
- [[stateupdate-subsystem-wire-format-validation-20260528]] — mid #11, 3 WriteState formats
- [[per-ship-subsystem-validation-20260528]] — mid #12, 16-ship catalog + AddToSet order
- [[sensor-hull-subsystem-validation-20260528]] — Hull/Sensor slot identities
- [[subsystem-integrity-hash-validation-20260528]] — slot table + dead-in-MP hash
- [[packet-bundling-validation-20260528]] — 4-pass drain, 512/2/510 budget
- [[networking-foundation-netimmerse-transport-validation-20260528]] — Send→Process→Dispatch
- docs/analysis/server-side-computation-model.md — authority model (§1-9)
- docs/analysis/stateupdate-authority-boundary-20260226.md — direction split + cadence audit
- OpenBC issue #186 — StateUpdate flicker/drift (this memo's target)
