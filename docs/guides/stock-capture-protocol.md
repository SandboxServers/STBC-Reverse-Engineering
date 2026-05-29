# Stock BC Capture Protocol — Closing the 4 Remaining Trace-Coverage Gaps

> **Status**: planning doc for ONE upcoming live stock-dedi session (or a small number of short
> sessions). Authored 2026-05-29 after trace mining of existing stock traces.

## 1. Purpose

Trace mining of the existing stock-dedi corpus (Valentine's Day FFA DM 33.5 min, collision
isolation, self-destruct isolation) answered ~85% of OpenBC's open verification questions
directly from data we already had. See `.claude/agent-memory/network-protocol-analyst/trace-mining-verification-20260529.md`
for the full Q1–Q7 writeup.

**Four narrow gaps remain that the existing data structurally cannot cover.** Each requires a
specific in-game scenario that never occurred in the captured sessions:

| # | Gap | Why existing traces can't cover it | OpenBC issue |
|---|-----|-----------------------------------|--------------|
| 1 | TEAM_DM scoring (0x3F/0x40/0x41) | Valentine's was FFA DM (Mission1) — zero team opcodes on wire | [#200](https://github.com/SandboxServers/OpenBC/issues/200) |
| 2 | Mid-battle late-joiner catch-up (0x1E/0x29 replay) | All 3 Valentine's joins happened in the first ~70 s before state accrued | [#191](https://github.com/SandboxServers/OpenBC/issues/191) |
| 3 | Isolated cloak transition timing | Cloak events present but interleaved with heavy combat — not isolatable | [#192](https://github.com/SandboxServers/OpenBC/issues/192) |
| 4 | Idle/parked ship force-resend interval | No truly idle ship existed in the combat-heavy trace | [#194](https://github.com/SandboxServers/OpenBC/issues/194) |

The goal of this document: a single well-planned ~10–15 minute live session (with efficient
batching — see §7) closes all four gaps with clean, isolatable data.

---

## 2. Capture environment setup

The OBSERVE_ONLY proxy auto-captures everything. You do not interact with the proxy — you just
run the dedi, perform the scripted in-game actions, then stop. All you control is the in-game
behavior of the host and client(s).

### Launch the dedicated server
```bash
make run-server
```
This deploys the proxy DLL + scripts and launches the dedi. Confirm `game/server/ddraw_proxy.log`
shows all 4 bootstrap phases and `ReadyForNewPlayers=1` before connecting any client.

> **IMPORTANT — clean trace per gap.** The trace files are append-or-overwrite per launch.
> For maximum isolatability, **restart the dedi (`make run-server`) between gaps** so each gap
> gets its own fresh `packet_trace.log`. Immediately after stopping each gap, copy the four log
> files into a named folder so they are not clobbered:
> ```bash
> mkdir -p logs/capture-20260529/gapN
> cp game/server/packet_trace.log game/server/message_trace.log \
>    game/server/tick_trace.log game/server/ddraw_proxy.log logs/capture-20260529/gapN/
> ```
> (Batched gaps 3+4 may share one launch — see §7.)

### Connect clients
```bash
make run-client          # primary stock client on the same machine
```
Additional clients connect over LAN with a vanilla `stbc.exe` (GameSpy LAN discovery finds the
host automatically). For gaps 1 and 2 you need **two** clients.

### Where the logs land
| File | Contents | Primary use |
|------|----------|-------------|
| `game/server/packet_trace.log` | Full hex dumps + opcode decode, per datagram | Byte-exact wire formats, timing |
| `game/server/message_trace.log` | Per-TGMessage opcode/direction summary | Fast opcode-frequency grep |
| `game/server/tick_trace.log` | Per-tick CSV (timing, queues, player counts, 15 cols) | StateUpdate cadence / force-resend |
| `game/server/ddraw_proxy.log` | Proxy lifecycle, VEH events | Sanity (confirm clean boot, no patches firing) |

The proxy logs wall-clock timestamps per datagram in `packet_trace.log`; those timestamps are
the measurement basis for all timing gaps (3 and 4 especially).

---

## 3. Per-gap protocol

Each gap below is self-contained: setup, a numbered in-game action sequence (followable without
BC expertise), duration, what to look for, and the OpenBC issue it unblocks.

### Gap 1 — TEAM_DM session (Mission2)

**Unblocks**: OpenBC [#200](https://github.com/SandboxServers/OpenBC/issues/200) — team scoring
wire formats (0x3F SCORE_INIT, 0x40 TEAM_SCORE, 0x41 TEAM_MESSAGE).

**Why needed**: Valentine's was FFA Deathmatch (Mission1). The team-scoring opcodes 0x3F/0x40/0x41
have **zero** occurrences anywhere in our corpus. We do not know their byte layouts, whether
team-kills score differently from cross-team kills, or whether team chat (0x41) echoes to the
sender the way regular chat (0x2C) does (confirmed 1:N broadcast-with-echo — Q6).

**Setup**: Host + **2 clients**. Host a **TEAM_DM game (Mission2)**, NOT FFA.

**In-game action sequence**:
1. Host launches a **Team Deathmatch** game (Mission2 in the multiplayer game-type menu).
2. Client A connects, then in the ship-select / team UI **picks Team 1**.
   → Watch for **0x3F (SCORE_INIT)** emitted on join — this carries the initial per-team score table.
3. Client B connects, **picks Team 2** (the *opposing* team).
4. Both clients spawn ships. Confirm the scoreboard shows two teams.
5. **Cross-team kill**: Client A destroys Client B's ship (phasers + torpedoes).
   → Watch for **0x40 (TEAM_SCORE)** — the team-score delta for the scoring team.
6. Respawn. **Same-team kill (team-kill)**: arrange a 3rd ship on Team 1 if a 3rd client is
   available, OR have Client A self-destruct / be killed by friendly fire from a teammate AI.
   The objective is to observe how a **same-team death** affects the team score (penalty? no change?).
7. **Team chat**: Client A sends a team-chat message (the team-only chat channel, not all-chat).
   → Watch for **0x41 (TEAM_MESSAGE)**. Note whether Client A receives its own message back
   (echo) and whether Client B (other team) receives it at all.

**Duration**: ~3–4 min.

**What to look for in the trace**:
- Byte-exact layouts of 0x3F, 0x40, 0x41 (these are Python-level SendTGMessage opcodes, so
  expect them via the `0x32` GameData transport, reliable).
- Cross-team kill (step 5) vs same-team kill (step 6): compare the 0x40 payloads — does a
  team-kill produce a *negative* delta, a zero delta, or no 0x40 at all?
- 0x41 routing: count C→S vs S→C and per-peer receive. If Client A sees its own message back,
  team chat echoes to sender (like 0x2C). If only the same-team peer receives it, team chat is
  team-scoped (a behavioral difference worth documenting).

---

### Gap 2 — Mid-battle late-joiner (catch-up)

**Unblocks**: OpenBC [#191](https://github.com/SandboxServers/OpenBC/issues/191) — late-join
object catch-up: RequestObj (0x1E) and the "catch-up only" 0x29 Explosion replay path.

**Why needed**: All three Valentine's joins (0x2A NewPlayerInGame) fired in the first ~70 s of
a 33.5-min session, before any meaningful world state existed. We have never seen what the host
sends to a client that joins a game **already in progress** with damaged ships and in-flight
explosions. Specifically: does the joiner ever emit **RequestObj (0x1E)** for an object it
sees referenced but doesn't have? Does the host **replay 0x29 Explosion** as part of catch-up?

**Setup**: Host + **1 client first**, then add a **2nd client mid-battle**.

**In-game action sequence**:
1. Host starts an FFA DM game (Mission1 is fine — team mode not required here).
2. Client A connects and spawns.
3. **Accrue state for 2–3 min**: Client A and a host-side AI (or the host's own ship) fight.
   Take hull damage, knock out subsystems, fire torpedoes, and trigger at least one ship
   destruction so an **explosion** is live/recent and debris exists on the field.
4. **While the battle is still hot**, connect **Client B**.
   → This is the critical moment. Watch the trace from Client B's **0x2A NewPlayerInGame** onward.
5. Let Client B finish loading into the game world (it should see the existing ships and any
   ongoing effects).
6. Have Client B target an existing damaged ship and fire once (forces it to reference an
   object it received during catch-up — may surface a 0x1E if any object was missing).

**Duration**: ~5 min total.

**What to look for in the trace** (filter to Client B's peer IP, from its 0x2A onward):
- The full **ObjCreate / ObjCreateTeam (0x02/0x03)** cascade the host sends to the joiner —
  one per existing ship. Compare against the game-start join cascade to see what's *extra* for
  a mid-game joiner (current damage state in the ObjCreate serialization?).
- **RequestObj (0x1E)** from Client B (C→S). Trace mining recorded **zero** of these; this
  capture confirms whether the opcode is live at all and what triggers it.
- **0x29 Explosion** sent to Client B specifically (S→C to that peer) shortly after join — the
  "catch-up replay" emission path for explosions that were already in flight at join time.
- The relative ordering: 0x2A → 0x03 cascade → (0x1E?) → 0x29 replay? → 0x1C StateUpdate flow begins.

---

### Gap 3 — Isolated cloak transition

**Unblocks**: OpenBC [#192](https://github.com/SandboxServers/OpenBC/issues/192) — cloak
transition duration (CloakTime) and shield-disable/re-enable delay (ShieldDelay).

**Why needed**: Valentine's has cloak events but interleaved with constant combat, so the
shield-disable timing window is impossible to measure against ambient state churn. We need a
clean cloak-up / decloak cycle with nothing else happening, repeated for averaging.

**Binary-truth reference values to confirm** (statically determined — see
`docs/gameplay/cloaking-state-machine.md`):
- **CloakTime = 5.0f** (`DAT_008E4E1C`, raw `00 00 A0 40`) — the cloak/decloak transition duration.
- **ShieldDelay = 1.0f** (`DAT_008E4E20`, raw `00 00 80 3F`) — delay before shields drop after
  cloak start, and before shields return after decloak completes.
> Note: OpenBC's clean-room spec currently says 3.0 s for the transition — that is wrong by 67%.
> Stock is 5.0 s. This capture provides the on-wire confirmation.

**Setup**: Host + **1 client**, both in a **cloaking-capable ship** (Bird of Prey or Warbird).
NO AI, NO other clients, NO combat.

**In-game action sequence** (repeat the cloak cycle **3×** for averaging):
1. Host starts a game; Client A connects in a Bird of Prey (or Warbird).
2. Client A sits stationary. **Engage cloak** (the cloak key).
   → 0x0E StartCloak (C→S) → host posts event **0x008000E3 (ET_START_CLOAKING)**.
   → ~1.0 s later, shields should drop via delayed event **0x0080007B**.
   → ~5.0 s after engage, cloak completes: **0x00800077 (ET_CLOAK_BEGINNING)** → state CLOAKING(2)
     → **0x00800078 (ET_CLOAK_COMPLETED)** → state CLOAKED(3). CLK flag set in StateUpdate.
3. **Wait 10 s fully cloaked.** Do nothing.
4. **Disengage cloak (decloak)**.
   → 0x0F StopCloak (C→S) → host posts event **0x008000E5 (ET_STOP_CLOAKING)**.
   → decloak transition (~5.0 s): **0x00800079 (ET_DECLOAK_BEGINNING)** → state DECLOAKING(5)
     → **0x0080007A (ET_DECLOAK_COMPLETED)** → state 0; shields re-enable after ShieldDelay (~1.0 s).
5. **Wait 10 s fully decloaked.**
6. Repeat steps 2–5 two more times (3 cycles total).

**Duration**: ~2 min.

**What to look for in the trace** (timestamps are the measurement; isolate to Client A's peer):
- Δt from **0x008000E3** to **0x00800078 (cloak completed)** → confirms **CloakTime ≈ 5.0 s**.
- Δt from **0x008000E3** to the **0x0080007B** shield-disable event → confirms **ShieldDelay ≈ 1.0 s**.
- Δt from **0x008000E5** to the shields-active-again signal after decloak → second ShieldDelay (~1.0 s).
- The exact cloak event sequence on the wire: 0x008000E3 → 0x00800077 → 0x00800078 (engage);
  0x008000E5 → 0x00800079 → 0x0080007A (disengage), plus the 0x0080007B shield events.
- Averaging across 3 cycles smooths the ~96 ms StateUpdate quantization (StateUpdate is ~10.4 Hz).

---

### Gap 4 — Idle/parked ship (force-resend interval)

**Unblocks**: OpenBC [#194](https://github.com/SandboxServers/OpenBC/issues/194) — the exact
StateUpdate force-resend (heartbeat) interval.

**Why needed**: Active ships emit StateUpdate continuously at ~10.4 Hz (median 96 ms), so the
force-resend heartbeat is masked by genuine dirty-bit updates. Trace mining of a lower-activity
object showed gap clustering at **450–500 ms** (hinting ~0.5 s, NOT the documented 1.0 s), but
no ship was ever truly idle. With a fully idle ship, **every StateUpdate that fires IS the
force-resend heartbeat** (zero dirty bits), pinning the interval definitively.

**Setup**: Host + **1 client**. NO AI, NO combat, NO other clients.

**In-game action sequence**:
1. Host starts a game; Client A connects and spawns a ship.
2. Client A does **ABSOLUTELY NOTHING** for 60 s:
   - No movement (no impulse, no throttle).
   - No rotation (do not touch the helm/mouse-look).
   - No firing (no phasers, no torpedoes).
   - No target change (do not cycle targets).
   - No subsystem toggles, no cloak, no chat.
3. Let the ship sit parked and untouched for a full **60 seconds**.
4. (Optional) repeat once to confirm the interval is stable.

**Duration**: ~1.5 min.

**What to look for in the trace** (isolate to Client A's ship object ID, S→C and C→S StateUpdate):
- Measure the **inter-StateUpdate interval** for the idle ship. With zero dirty bits, the only
  reason a 0x1C fires is the force-resend timer.
- Expect a clean periodic interval. Confirm whether it is **~0.5 s** (matching the mined
  450–500 ms cluster) or **~1.0 s** (the currently documented value). This pins #194 definitively.
- Cross-check `tick_trace.log` to correlate the heartbeat against tick count (is force-resend
  every N ticks at the ~10 Hz tick rate, e.g. every 5 ticks ≈ 0.5 s?).
- Verify the idle StateUpdate carries **no dirty flags** (flags=0x00 / no SUB / no WPN) — a
  pure position/orientation refresh — which would confirm it is the heartbeat, not a real update.

---

## 4. Post-capture analysis checklist

Run these against each gap's saved `packet_trace.log`. Grep patterns assume the proxy's decoded
opcode lines (`opcode=0xNN`, `dir=`, `peer=`, timestamp prefix). Adjust to the actual log format
if the decode line differs.

### Gap 1 — TEAM_DM
- [ ] `grep -nE "opcode=0x(3F|40|41)" packet_trace.log` — confirm all three opcodes appear.
- [ ] Dump the raw hex for the **first 0x3F** (SCORE_INIT on join) and annotate per-team fields.
- [ ] Dump hex for the 0x40 after the **cross-team** kill (step 5) and after the **same-team**
      kill (step 6); diff the score-delta bytes.
- [ ] Count 0x41 C→S vs S→C and per-peer; determine echo-to-sender and cross-team visibility.

### Gap 2 — Late-joiner
- [ ] Find Client B's **0x2A NewPlayerInGame** line; note its timestamp `T_join`.
- [ ] `grep -nE "opcode=0x(02|03)" packet_trace.log` filtered to `peer=<ClientB IP>` after
      `T_join` — count the ObjCreate cascade; compare to a game-start join cascade.
- [ ] `grep -nE "opcode=0x1E" packet_trace.log` — did RequestObj fire at all? From which side?
- [ ] `grep -nE "opcode=0x29" packet_trace.log` filtered to `peer=<ClientB IP>` near `T_join` —
      explosion replay on catch-up?
- [ ] Establish the ordering: 0x2A → 0x03… → (0x1E?) → (0x29?) → first 0x1C to Client B.

### Gap 3 — Cloak
- [ ] `grep -nE "0080(00E3|00E5|0077|0078|0079|007A|007B)" packet_trace.log` — extract all cloak
      events with timestamps.
- [ ] For each of the 3 cycles: Δt(0x008000E3 → 0x00800078) = CloakTime; expect ≈ 5.0 s.
- [ ] Δt(0x008000E3 → 0x0080007B) = ShieldDelay; expect ≈ 1.0 s.
- [ ] Δt(0x008000E5 → shields-active-after-decloak) = decloak ShieldDelay; expect ≈ 1.0 s.
- [ ] Average the 3 cycles; record min/median/max to bound the ~96 ms StateUpdate quantization.

### Gap 4 — Idle ship
- [ ] Isolate StateUpdate (0x1C) lines for Client A's ship object ID over the 60 s idle window.
- [ ] Compute consecutive inter-packet Δt; build a histogram (50 ms buckets).
- [ ] Identify the dominant interval → force-resend period (~0.5 s vs ~1.0 s).
- [ ] Confirm the idle 0x1C carries no dirty flags (pure heartbeat).
- [ ] Correlate against `tick_trace.log` tick counts to express the interval in ticks.

---

## 5. Sanity checks (run once, any session)
- [ ] `ddraw_proxy.log` shows OBSERVE_ONLY, clean boot, **no binary patches firing** (we want
      stock behavior, not proxy-modified).
- [ ] No VEH events in `ddraw_proxy.log` during the capture window.
- [ ] Datagram header sanity: byte[0]=direction (0x01 S / 0x02 C), byte[1]=msgCount (1–110).
- [ ] Timestamps are monotonic (no log rotation mid-capture).

---

## 6. Combined-session option (batching)

Gaps differ in player count and game type, which dictates what can share a launch:

| Gap | Players | Game type | Special ship |
|-----|---------|-----------|--------------|
| 1 TEAM_DM | Host + 2 clients | **Mission2 (Team DM)** | any |
| 2 Late-joiner | Host + 2 clients (staggered) | Mission1 (FFA) | any |
| 3 Cloak | Host + 1 client | FFA | **cloaking ship** |
| 4 Idle | Host + 1 client | FFA | any |

**Gaps 3 + 4 can and SHOULD be batched into one launch.** Both are Host + 1 client, FFA, no
combat, no AI. If Client A is in a cloaking ship, run cloak first (it ends decloaked, shields up),
then immediately enter the idle window — the ship is already parked and untouched. One client,
one launch, ~4 min of in-game time:

> **Batched 3+4 sequence** (single `make run-server` + `make run-client`):
> 1. Client A spawns a Bird of Prey, sits stationary.
> 2. Run **3 cloak cycles** (Gap 3 steps 2–6) — ~2 min.
> 3. After the final decloak settles (shields back up), **do nothing for 60 s** (Gap 4) — ~1.5 min.
> 4. Stop. The single trace contains both an isolated cloak sequence and an isolated idle window.
>
> The only caveat: when analyzing Gap 4, start the idle-window measurement *after* the last
> cloak event (0x0080007A decloak-complete) so cloak-induced StateUpdates don't pollute the
> heartbeat histogram.

**Gaps 1 and 2 each need their own launch** — Gap 1 requires Mission2 (different game type) and
Gap 2 requires a *staggered* 2-client join (Client B joins mid-battle), which can't coexist with
Gap 1's both-up-front team assignment. Keep them separate for clean isolation.

**Recommended ordering (3 launches, ~12–15 min total in-game):**
1. **Launch 1 — Gaps 3+4 batched** (Host + 1 cloaking client, FFA): cloak cycles → idle park. ~4 min.
2. **Launch 2 — Gap 2** (Host + 1 client, accrue state, then add Client B mid-battle). ~5 min.
3. **Launch 3 — Gap 1** (Host + 2 clients, Mission2 Team DM, scoring + team chat). ~3–4 min.

Restart the dedi between each launch and copy the four log files into `logs/capture-20260529/gapN/`
(per §2) so each gap's trace stays isolated.

---

## 7. Cross-references

### OpenBC issues unblocked
- Gap 1 → [#200 TEAM_DM scoring](https://github.com/SandboxServers/OpenBC/issues/200)
- Gap 2 → [#191 late-join catch-up](https://github.com/SandboxServers/OpenBC/issues/191)
- Gap 3 → [#192 cloak transition timing](https://github.com/SandboxServers/OpenBC/issues/192)
- Gap 4 → [#194 force-resend interval](https://github.com/SandboxServers/OpenBC/issues/194)

### STBC v5 docs (RE side)
- Trace mining writeup that identified these gaps:
  `.claude/agent-memory/network-protocol-analyst/trace-mining-verification-20260529.md`
- Cloak timing / event IDs (CloakTime 5.0f, ShieldDelay 1.0f, event ID table):
  [docs/gameplay/cloaking-state-machine.md](../gameplay/cloaking-state-machine.md)
- Cloak network opcodes 0x0E/0x0F → events 0x008000E3/0x008000E5:
  [docs/protocol/game-opcodes.md](../protocol/game-opcodes.md)
- StateUpdate cadence + dirty-flag format (for Gap 4 heartbeat analysis):
  [docs/protocol/stateupdate.md](../protocol/stateupdate.md)
- Python-level scoring/chat opcodes (0x2C, 0x36, 0x37; the 0x3F–0x41 team variants live here too):
  [docs/protocol/python-messages.md](../protocol/python-messages.md)
- Gamemode / scoring system (team system, end/restart flow):
  [docs/gamemode-system.md](../gamemode-system.md)
- Ship death + Explosion (0x29) lifecycle (for Gap 2 catch-up replay):
  [docs/networking/ship-death-lifecycle.md](../networking/ship-death-lifecycle.md)
- Full reference FFA trace (the corpus these gaps sit beside):
  [docs/analysis/valentines-day-battle-analysis.md](../analysis/valentines-day-battle-analysis.md)
