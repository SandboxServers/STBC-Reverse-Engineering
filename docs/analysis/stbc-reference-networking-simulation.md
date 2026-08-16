> [docs](../README.md) / [analysis](README.md) / stbc-reference-networking-simulation.md

---
title: Networking, Multiplayer and Simulation Learnings from `markward/stbc_reference`
type: explanation + action list
audience: orchestrator, OpenBC server authors
surveyed: 2026-08-16
source: https://github.com/markward/stbc_reference (public, read-only survey)
status: partial — external-corpus survey. Claims sourced to their corpus are verification
        targets; claims marked **verified here** were cross-checked against our own
        `reference/scripts/` or `reference/decompiled/` this pass.
companion: docs/analysis/stbc-reference-corpus-learnings.md
---

# Networking, Multiplayer and Simulation Learnings from `markward/stbc_reference`

Second pass over the external corpus, scoped to the three areas OpenBC actually runs on. The
companion doc covers methodology and the class model; this one covers the transport object layer, the
server tick model, and object replication.

**Headline:** their `spec/PhysicsObjectClass.md` identifies `+0xEC` as `m_netType` and `+0xF1` as
`m_doNetUpdate`. Cross-checking that against our own shipped-script corpus **answers OQ1 in
[docs/gameplay/collision-rate-limiting.md](../gameplay/collision-rate-limiting.md)** and materially
reframes the "collision rate limiting disabled" known issue. See §4.

---

## 1. What their corpus is strong and weak on, for our purposes

| Area | Them | Us | Verdict |
|---|---|---|---|
| Wire format, opcodes, packet traces | thin — no opcode table, no trace corpus | 22 protocol docs, byte-level traces | **we are far ahead** |
| Transport *objects* (`TGMessage`/`TGNetwork`/`TGPlayerList` layouts) | field-by-field with confidence grades | partial, scattered | **they add real detail** |
| Frame pump + cooperative scheduler | fully specified, both levels | `main-loop-timing.md` has the pump address only | **large gap on our side** |
| Kinematics / integration / replication-control fields | specified with dt clamps and field offsets | scattered; the net-control fields absent | **large gap on our side** |
| Object registry (`SetClass` by-id lookup) | byte-exact, three containers | known by name, not by structure | **they add detail** |
| Gameplay systems (shields, power, repair, weapons) | good, but their `ShipClass` doc is thin/address-batched | 16 gameplay docs, deeper | **we are ahead except on shields** |

---

## 2. The server tick model — our biggest structural gap

We have `0x0046F420` in [docs/architecture/main-loop-timing.md](../architecture/main-loop-timing.md)
as the pump address. Their `spec/PythonMethodProcess.md` §7.1–7.2 and
`spec/SupportInfrastructure.md` §1 specify the whole mechanism. None of the supporting addresses
(`0x00981490`, `0x0088BB14`, `0x0046F930`, `0x0046F610`, `0x0046F740`, `0x0046F7D0`, `0x0046F8D0`)
appear anywhere in our docs.

### 2.1 The frame budget (`0x0046F420`)

1. Push the current time into a **16-entry ring** of recent frame timestamps; take the mean with the
   single smallest and single largest **discarded** — an outlier-trimmed average, so one stalled
   frame does not distort the budget.
2. Budget for this frame = that average minus time already spent. If not positive, a **floor of 10 ms**
   is used.
3. **Priority bucket 0 runs to completion every frame and is not budgeted.**
4. Remaining budget is recomputed and floored at zero.
5. A **rotating counter** picks the starting bucket among 1–3, so no bucket is permanently starved by
   the one before it; buckets then run in order until the budget is exhausted.

### 2.2 Running one budgeted bucket (`0x0046F610`)

Round-robin within a bucket is enforced by a has-run-this-round byte: a task runs only when live,
**due**, and its has-run byte is clear. If nothing ran but something was due — i.e. every due task
already ran this round — the byte is cleared across the whole bucket and the walk repeats. **Every due
task in a bucket runs once before any runs twice.**

**Due** (`0x0046F740`): the task's generation field does not match a global sentinel, *and* time since
its last run ≥ its configured delay — measured on the **game clock or the real-time clock according to
the task's own flag**.

### 2.3 `TimeSliceProcess` — the enrolment model (`0x0088BB14`, bucket table `0x00981490`)

Constructing a task **enrols it immediately**; there is no separate start call. Defaults: priority
**2**, delay `0.0`, delay-uses-game-time **on**, a never-run sentinel double
(`0xC415AF1D78B58C40`, ≈ −1.0e20).

Bucket record is `0x18` bytes: `+0x04` items array, `+0x08` capacity, `+0x0C` high-water count,
`+0x10` live count, `+0x14` growth increment. `SetPriority` (`0x0046F720`) must
**withdraw → store → re-enrol** in that order, because the withdraw reads the *old* priority and the
insert reads the *new* one.

### 2.4 Why this matters to OpenBC

Our headless server drives work from `GameLoopTimerProc` and per-tick polling. The original's model is
different in three ways an implementer would not guess:

- **Deadline, not delta.** Scheduled tasks receive `now + remaining_budget` — the wall-clock time by
  which they should have finished. `PythonMethodProcess::Update` (`0x0046F930`) passes that deadline
  straight to the Python method as its only argument. A reimplementation that passes `dt` has changed
  the contract of every scripted background task.
- **Bucket 0 is unbudgeted.** Anything that must run every frame regardless of load belongs there;
  everything else is best-effort under a trimmed-mean budget. That is the original's load-shedding
  policy, and it is what makes frame time degrade gracefully rather than stall.
- **Two clocks.** Per-task choice between game time and real time. A server that pauses or scales game
  time will silently change the cadence of every task whose flag says game-time.

> **Action:** specify this in `../OpenBC/docs/` as the server task model, and reconcile our
> `main-loop-timing.md` against it. Verify the seven addresses on our own binary first.

### 2.5 A published-but-broken class worth knowing about

`PythonMethodProcess` (dispatch table `0x00894688`, 56 bytes) is the **only scheduler task a script
can create**. Their finding: the class calls `getattr(owner, name)`; `SetFunction` sets the *name*, and
**nothing in the entire program ever sets the owner** (`+0x30`, zeroed at construction, written by no
published entry, no wrapper, no engine call site — the pointer type is unpacked at exactly four sites,
all inside its own three wrappers).

Also: `SetFunction` is *declared* to accept `None` or a string, but the `None` path skips the type
check and still takes the length of, and copies from, a null pointer. No shipping caller passes `None`,
so it is latent rather than observed — but "either `None` or a string" is not the real contract.

Relevant to us only if OpenBC exposes this class at all. If it does, decide deliberately whether to
reproduce the defect or fix it, because a fixed version is a different program.

---

## 3. Transport object layer — `spec/Networking.md`

Complementary to our protocol family: we own the wire, they own the objects behind it.

### 3.1 Field layouts we do not have

| Class | Offset | Field |
|---|---|---|
| `TGMessage` | `+0x04` / `+0x08` | payload pointer / length |
| `TGMessage` | `+0x14` | sequence number — **unsigned 16-bit**, zero-extended by the getter |
| `TGMessage` | `+0x18` | retry counter |
| `TGNetwork` | `+0x14` | connect status; **value 2 = connected/ready** |
| `TGNetwork` | `+0x28` | embedded `TGPlayerList` roster |
| `TGNetwork` | `+0xe0` / `+0x110` | password / profiling flag |
| `TGWinsockNetwork` | `+0x338` | UDP port |
| `TGNetPlayer` | `+0x04` / `+0x18` / `+0x1c` | name / **netID (roster sort key)** / net address |
| `TGNetPlayer` | `+0x5c` / `+0x60` | bytes-per-second to / from |
| `TGPlayerList` | `+0x04` / `+0x08` / `+0x0c` | element array / count / capacity |

`TGMessage` vtable slots used by the script surface: `+0x08` Serialize, `+0x14`
GetBufferSpaceRequired, `+0x18` Copy. Message leaves (`TGAckMessage`, `TGBootPlayerMessage`,
`TGConnectMessage`, `TGDisconnectMessage`, `TGDoNothingMessage`, `TGNameChangeMessage`) add **no
fields of their own** — they override virtual behaviour only.

### 3.2 Roster semantics OpenBC must match

- `TGPlayerList` is a growable array **kept sorted ascending by netID**, so `GetPlayer` and
  `TGNetGroup::IsPlayerInGroup` binary-search. `TGNetPlayer::Compare` returns `B.netID − A.netID`.
- **`GetPlayerFromAddress` (`0x006bb9d0`) is a linear scan** because address is not the sort key. A
  reimplementation that indexes players by address gets different behaviour on duplicate addresses:
  the original returns the *first* match in netID order.
- Insert/remove keep the array sorted and compacted (element shift via block move, capacity doubling).

### 3.3 Two concrete constraints

- **`TGWinsockNetwork::SetPortNumber` (`0x006b9bb0`, byte-exact)**: with the validate flag set, the
  accepted port range is **[5000, 49150]** (`port > 0`, `≥ 1023`, `< 49151`, `≥ 5000` — the last
  dominates). Rejection returns false and leaves the port unchanged. OpenBC should reproduce the
  range, including the fact that validation is skippable.
- **`SetData` vs `SetDataNoCopy`** (`0x006b84d0` / `0x006b89a0`): the first deep-copies the caller's
  buffer through `NiArrayAlloc`; the second **takes ownership**. Both free the existing buffer first.
  A `length` of zero on `SetData` leaves the payload pointer null rather than allocating a zero-byte
  buffer. Ownership semantics are the kind of thing a rewrite gets wrong silently.

### 3.4 A recorded engine defect

Four of eight `ServerListEvent` accessors — the **string-returning** ones (`GetServerName`,
`GetVersion`, `GetMissionName`, `GetAddress`) — return the shared `None` singleton on the gated path
**without incrementing its refcount**. The four integer-returning ones build a fresh object and are
correct. The split follows the return type exactly, four and four.

Also structural: all eight are gated twice (a process-global network handle must be non-null **and**
the event must carry a session pointer at `+0x28`), and a failed gate is a **silent empty answer** —
the caller cannot distinguish "networking is down" from "the server did not advertise this". And three
of the eight (`GetPing`, `GetAddress`, `GetPortNumber`) are properties of the *connection*, read
directly, while five are advertised *content* looked up by string key. **A rebuild backing all eight
with one property bag will answer for `GetPing`/`GetAddress` in cases where the original cannot.**

### 3.5 A dedicated-server hook we should look at

`spec/STWindowLeaves.md` lists `MultiplayerWindow_SetDedicatedServerMenu` (`0x00635450`) and
`GetDedicatedServerMenu` (`0x006354F0`) among `MultiplayerWindow`'s 45 published entries — a
**dedicated-server menu slot in the stock lobby window's own script API**. Given how much of our
headless work is spent working around UI paths, it is worth checking what the stock scripts do with
that slot. `MultiplayerWindow` is the class behind our third dispatcher (`FUN_00504c10`, opcodes
`0x00`/`0x01`/`0x16`).

---

## 4. `ship+0xEC` — the correction, and the answer to our own OQ1

### 4.1 What their corpus says

`spec/PhysicsObjectClass.md` §2 gives the replication-control block on `PhysicsObjectClass`
(vtable `0x00894128`, classID `0x8006`) — inherited by every ship, torpedo and shot:

| Offset | Type | Field | Script API |
|---|---|---|---|
| `+0xEC` | **int** | `m_netType` — network object type id | `GetNetType` `0x00607F40` / `SetNetType` |
| `+0xF0` | byte | `m_usePhysics` — physics-integration enabled | `IsUsingPhysics` `0x00608120` / `SetUsePhysics` `0x006080A0` |
| `+0xF1` | byte | `m_doNetUpdate` — **network-update enabled** | `IsDoingNetUpdate` `0x00608020` / `SetDoNetUpdate` `0x00607FA0` |
| `+0x104` | byte | `m_isStatic` — immovable; update snaps motion to zero | `IsStatic` `0x00606E80` / `SetStatic` `0x00606DF0` |

### 4.2 Where our docs disagree with each other

| Our doc | Reading of `ship+0xEC` |
|---|---|
| [gamemode-system.md](../gamemode-system.md) | NetType (species/class enum), int, read via `PhysicsObjectClass_GetNetType` `0x00607F40` |
| [protocol/objcreate-serialization.md](../protocol/objcreate-serialization.md) | `ShipReadSpecies` `0x005A2030` writes the wire species byte into `ship+0xEC` |
| [protocol/objnotfound-requestobj-enterset-wire-format.md](../protocol/objnotfound-requestobj-enterset-wire-format.md) | "the network-enable byte" — opcode `0x1E` gates on `obj+0xec != 0` |
| [gameplay/collision-rate-limiting.md](../gameplay/collision-rate-limiting.md) | "`enableFlag` (**byte**); when 0, rate limiting returns false immediately" |
| `CLAUDE.md` known issues | "Collision rate limiting disabled (ship+0xEC=0)" |

The first two agree with their corpus. The last three describe the same field as a boolean
enable-flag. **It is an int holding the network object type**, and the two "enable" readings are
descriptions of the *effect* of a gate (`netType == 0` → not a networked object → skip), not of the
field's identity.

### 4.3 Verified against our own material this pass

`collision-rate-limiting.md` OQ1 asks: *"What sets `ship+0xEC` to non-zero during normal ship
creation? ... then expose it via SWIG (if not already) so DeferredInitObject can set it."*

It is already exposed, and the shipped scripts already call it:

| Site | Call |
|---|---|
| `reference/scripts/loadspacehelper.py:103` | `pShip.SetNetType(kStats['Species'])` — **the normal ship creation path** |
| `reference/scripts/Multiplayer/SpeciesToShip.py:179` | `pShip.SetNetType(iType)` |
| `reference/scripts/Tactical/Projectiles/*.py` | `pTorp.SetNetType(Multiplayer.SpeciesToTorp.<TYPE>)` — every torpedo type |
| `reference/scripts/Systems/Multi1/Multi1.py:106`, `Systems/Multi6/Multi6_S.py:67` | `pAsteroid.SetNetType(0)` |

`reference/decompiled/07_audio_input.c:277` carries the SWIG registration string
`PhysicsObjectClass_SetNetType` at `0x00940060` with format `"Oi"` (object, int), confirming the
published signature. (Their roster marks this wrapper *unplaced* — we can locate it; a fill going the
other way.)

### 4.4 What this changes

1. **OQ1 is answered.** The write site is Python, not C++: `loadspacehelper.py` on the normal spawn
   path. No new SWIG export is needed and no C++ patch is required — a `SetNetType(species)` call in
   the creation path is sufficient.
2. **`netType == 0` is a legitimate, deliberate value.** Stock multiplayer maps call
   `pAsteroid.SetNetType(0)` on purpose. So `if (+0xEC == 0) return false` in the rate limiter reads as
   *"do not rate-limit non-networked objects"* — a design decision, not a bug.
3. **The stated root cause of the collision storm needs re-testing.** Our `DeferredInitObject`
   (`src/scripts/Custom/DSHandlers.py`) already **reads `GetNetType()` and skips when `<= 0`**, so the
   ships it initialises demonstrably have a non-zero `+0xEC`. Either the 28,504-event storm comes from
   objects that are not those ships, or the cause is elsewhere — `collision-rate-limiting.md` itself
   flags the hash-table fields at `ship+0x68` / `+0x6C` / `+0x74` as also needing initialisation, and
   that is now the more likely candidate.
4. **`+0xF1` (`m_doNetUpdate`) is the actual network-update enable flag, and it appears in none of our
   docs.** `SetDoNetUpdate` / `IsDoingNetUpdate` are script-reachable (`0x00607FA0` / `0x00608020`).
   If OpenBC needs a per-object replication toggle, this is it — not `+0xEC`.

> **Action:** correct the field name and type in `collision-rate-limiting.md` and
> `objnotfound-requestobj-enterset-wire-format.md`, close OQ1 with the `loadspacehelper.py` citation,
> restate the CLAUDE.md known issue, and re-run the collision-storm diagnosis against `+0x68`/`+0x6C`/
> `+0x74`. Document `+0xF0`/`+0xF1`/`+0x104` as the replication-control block.

---

## 5. The integration step — determinism constraints for a server tick

`PhysicsObjectClass::Update` (`0x005A05C0`, vtable slot 21, logic-verified):

1. **Static early-out.** If `m_isStatic` (`+0x104`): write the shared zero-vector as velocity, zero
   acceleration and angular state, run the post-step tick, **return without integrating**.
2. **Clamp the step.** If `m_lastStepTime` (`+0x14`) is below the accumulator floor (`0x00888B54`), use
   a fixed **`0.001`**. Otherwise take `dt − m_lastStepTime`, raise it to the minimum (`0x00888B4C`) if
   below, and if it exceeds the ceiling (`0x00888860`) **snap it to `1.0`**.
3. Build an orientation matrix, capture orientation and velocity, run the 10-argument integration
   kernel `0x005A09D0` over the `+0xa8..+0xe4` block, write the updated velocity back, apply the matrix
   to the scene node transform, store orientation into `sceneNode+0x54`, run the post-step tick
   `0x004351F0(dt)`.

Two properties OpenBC must reproduce:

- **`dur` (the clamped integration delta) is not `dt`.** The post-step tick receives the raw `dt`; the
  integrator receives the sanitised one. Using one value for both changes behaviour under load.
- **The clamp is a snap, not a saturate, at the top end** — a `dt` above the ceiling becomes `1.0`, not
  the ceiling. A long stall therefore produces a full one-second integration step.

Kinematic block (`+0xa8..+0xe4`, 16 contiguous floats): acceleration `+0xa8`, angular acceleration
`+0xb4`, integrator scratch `+0xc0`, **angular-velocity direction** `+0xcc` (unit axis), mass `+0xd8`,
rotational inertia `+0xdc`, **angular-velocity magnitude** `+0xe0`, tail `+0xe4`. Note that angular
velocity is stored **split as direction × magnitude**, and `GetAngularVelocity` multiplies them — a
representation choice a rewrite would not arrive at independently, and one that matters if it ever
crosses the wire.

### 5.1 Velocity does not live on the object — headless implication

`GetVelocityVec` (`0x005A05A0`, **byte-exact**): load the scene node (`+0x18`); if present return
`sceneNode + 0x98`; **if null, return the address of the shared zero-vector global `0x009A2878`** —
never a null pointer.

This is the idiom our `netimmerse-engine-dev` work keeps running into, and it has a direct consequence
for a headless server: **an object with no scene node reads velocity as zero and silently accepts
velocity writes into a shared global.** Any `StateUpdate` path that samples velocity from an object
whose node was never built will ship zeros, with no error anywhere. Worth checking against our
`DeferredInitObject` ships and the flags=0x20 work.

`0x009A2878` appears in our `ship-navigation.md` and `targeting-system.md` but not as "the shared
zero-vector that null-node accessors return".

### 5.2 Client-side prediction

`GetPredictedPosition` (`0x00607CC0`, signature `"OOOOf"` — three `TGPoint3` inputs plus a float time
horizon) and `GetPredictedRotationTG` (`0x00607DF0`, `"Of"` → a `0x24`-byte `TGMatrix3`). Both are
**script-facing**, so BC's dead reckoning is at least partly a Python-level concern, not purely C++.
The numeric kernels (`0x0047F990`, `0x005A0C20`) are unreconstructed on their side and absent from
ours. If OpenBC ever needs to match client-side extrapolation between `StateUpdate` packets, these two
addresses are the targets.

---

## 6. Object identity and lookup — `spec/SetClass.md`

`SetClass::GetObjectByID` (`0x0040fcd0`, **byte-exact**) is a **binary search over a sorted-by-id
array**: null array → null; compare `m_objects[mid]` against `id`; equal → return; greater → move the
high bound down; else move the low bound up.

The set holds its objects **three ways at once**, kept in sync by add/remove:

1. a **sorted-by-id array** (`+0x30`/`+0x34`) — id lookup and ordered iteration
   (`GetObjectByID` / `First` / `Next` / `Previous`);
2. a **plain camera array** (`+0x48`/`+0x4c`) — scanned linearly by the active flag;
3. a **name → object hash map** (`+0x80`) — name lookup and removal.

Two consequences for OpenBC: **object ids are allocation-ordered and iteration order is id order**, so
anything that iterates a set observes objects in creation order — which is observable behaviour if a
mission script or a replication pass depends on it. And a server keeping only a hash map by id has
changed iteration order even though every individual lookup still answers correctly.

We reference `GetObjectByID` by name in `ship-death-lifecycle.md` and
`objnotfound-requestobj-enterset-wire-format.md` but not by address or structure — relevant to
opcode `0x1D` (`ObjNotFound`) and `0x1E` (`RequestObj`), which are exactly id-resolution failures.

---

## 7. Collision — see the companion doc

`spec/ProximityManager.md` is covered in
[stbc-reference-corpus-learnings.md](stbc-reference-corpus-learnings.md) §2.3. The multiplayer-relevant
part in one line: the two collision toggles are **process-global**, they skip a pair **only when either
object is the player's own ship**, and **constructing a `MultiplayerGame` copies the single-player flag
over the multiplayer flag** — so an MP value set before session creation does not survive it. That
remains the most promising untested lead for our collision issues, alongside §4.4 above.

---

## 8. Action list

| # | Action | Why |
|---|---|---|
| 1 | Correct `ship+0xEC` to `m_netType` (int) in `collision-rate-limiting.md`, `objnotfound-requestobj-enterset-wire-format.md` and the CLAUDE.md known-issues list; close OQ1 citing `loadspacehelper.py:103` | Verified this pass; the current text says "byte enableFlag" and sends implementers after a non-existent C++ write site |
| 2 | Re-diagnose the 28,504-event collision storm against `ship+0x68`/`+0x6C`/`+0x74` | `DeferredInitObject` already gates on `GetNetType() > 0`, so the stated root cause cannot be the whole story |
| 3 | Document the replication-control block `+0xEC`/`+0xF0`/`+0xF1`/`+0x104` and its script API | `SetDoNetUpdate` (`0x00607FA0`) is the real per-object replication toggle and appears in none of our docs |
| 4 | Verify and document the scheduler: `0x0046F420`, `0x0046F610`, `0x0046F740`, `0x0046F7D0`, `0x0046F8D0`, `0x0088BB14`, bucket table `0x00981490` | Our `main-loop-timing.md` has the pump address and nothing behind it; deadline-not-delta and unbudgeted-bucket-0 are contract-level facts |
| 5 | Check whether `DeferredInitObject` ships have a scene node before any velocity is sampled | Null node → `GetVelocityVec` returns the shared zero global silently; a candidate for zeroed motion in `StateUpdate` |
| 6 | Extend `docs/protocol/transport-layer.md` with the `TGMessage`/`TGNetwork`/`TGNetPlayer`/`TGPlayerList` field tables and the `[5000, 49150]` port range | Fills a real gap; the netID-sorted-with-linear-address-scan asymmetry is reproducible behaviour |
| 7 | Look at `MultiplayerWindow_SetDedicatedServerMenu` (`0x00635450`) and what stock scripts do with it | A dedicated-server slot in the stock lobby API, on the class behind our third dispatcher |
| 8 | Add the `dt` clamp constants (`0x00888B54` / `0x00888B4C` / `0x00888860`) and the snap-to-`1.0` behaviour to the OpenBC simulation spec | Determinism-relevant; the snap (not saturate) at the ceiling is easy to get wrong |

---

## 9. Cross-references

- [docs/analysis/stbc-reference-corpus-learnings.md](stbc-reference-corpus-learnings.md) — companion: methodology, class model, `ProximityManager`, the `PowerSubsystem` naming correction
- [docs/gameplay/collision-rate-limiting.md](../gameplay/collision-rate-limiting.md) — §4 corrects its `ship+0xEC` field identity and closes its OQ1
- [docs/gamemode-system.md](../gamemode-system.md) — already had `ship+0xEC = NetType` correct
- [docs/protocol/objcreate-serialization.md](../protocol/objcreate-serialization.md) — `ShipReadSpecies` `0x005A2030` → `ship+0xEC`
- [docs/protocol/objnotfound-requestobj-enterset-wire-format.md](../protocol/objnotfound-requestobj-enterset-wire-format.md) — §4 corrects "network-enable byte"; §6 relevant to id resolution
- [docs/architecture/main-loop-timing.md](../architecture/main-loop-timing.md) — §2 extends it
- [docs/protocol/transport-layer.md](../protocol/transport-layer.md) — §3 extends it
- [docs/networking/fragmented-ack-bug.md](../networking/fragmented-ack-bug.md) — already holds the `0x009962d4` factory table
