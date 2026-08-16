> [docs](../README.md) / [analysis](README.md) / stbc-reference-corpus-learnings.md

---
title: What the `markward/stbc_reference` Corpus Offers OpenBC
type: explanation + action list
audience: orchestrator, OpenBC spec authors
surveyed: 2026-08-16
source: https://github.com/markward/stbc_reference (public, read-only survey)
status: partial — survey of an external corpus; every borrowed claim listed here is a
        verification target for our own Ghidra pass, not an accepted fact
---

# What the `markward/stbc_reference` Corpus Offers OpenBC

## 0. What was surveyed

`markward/stbc_reference` is a **clean-side behavioural specification corpus** for Star Trek: Bridge
Commander — 96 spec documents (~1.9 MB), a machine-extracted class model, a mechanically-enforced
clean-room gate, and a designed-but-undeployed question-answering pipeline. It is authored as the
public output of a private analysis workspace that does not cross the wall.

| Path | Contents |
|---|---|
| `spec/` (96 docs) | Per-class behavioural specs: object model, offsets, constants, per-method behaviour |
| `model/CLASS_HIERARCHY_EXTRACTED.md` | Class graph extracted from the program's own SWIG type registry at `0x00900A94` |
| `model/CLASS_HIERARCHY.md` | Older hand-written hierarchy; **superseded and partly wrong** (see §3.2) |
| `ANSWERABILITY.md` | Measured coverage / accuracy / findability of the whole corpus |
| `CLEANROOM-RULE.md` + `tools/check_cleanroom.py` | The description-vs-expression wall and its self-testing gate |
| `PIPELINE.md`, `tools/qa/` | Question routing, evidence-bar-by-label, fixed answer template |

**Related repos observed:** `markward/bc_dauntless` ("Reimplementation of the STBC game engine",
Python) and a fork of this repository. `markward/utopia_re` is private and was **not** readable from
this session.

**On `utopia_re`:** by the corpus's own `CLEANROOM-RULE.md`, the analysis workspace is the *dirty*
side — disassembly, decompiler output, reconstruction source. If OpenBC intends to keep a defensible
clean-room posture, `stbc_reference` is the side we should be consuming, and reading the dirty side
into an OpenBC-authoring context is the thing the wall exists to prevent. Recommend we deliberately
*not* pursue `utopia_re` access for OpenBC spec work, and pursue it only for our own RE side if at all.

---

## 1. The methodology is the biggest single takeaway

Our v5 evidence standard and their corpus converge on the same conclusions, but they have built
things we have not. Five practices are directly portable.

### 1.1 A measured answerability document, not an implicit one

`ANSWERABILITY.md` states, in counted numbers, where the corpus is hollow: 19.8% of the 16,794-function
game-side corpus has no specified behaviour at all; 61.1% byte-exact; 19.1% behavioural clone of which
only ~23% has been differentially tested. It splits by subsystem — the **SWIG/Python API surface is
95.3% covered** while engine and game logic sit at ~75%.

We have `v5-validation-status.md` trackers per doc family, which count *documents validated*. They do
not count *program coverage*. A doc-count tracker cannot tell an OpenBC implementer "the region you
are about to build has no evidence behind it."

> **Action:** add a program-coverage dimension to our v5 trackers — for each subsystem, what fraction
> of the relevant functions we have actually read, not how many docs we have blessed.

### 1.2 "I cannot answer that" as a first-class output

Their originating failure was a published constant table **wrong in 1,186 of 1,263 entries** (an
extractor read the slot before the name). Two standing rules came out of it: every answer cites
re-checkable evidence, and a decline is a valid result. Their spec docs carry explicit
"§0.2 What is NOT established" sections and per-section confidence tags (BE / LV / faithful /
reviewed-not-tested / partial / open).

Our docs carry a `status:` and per-claim `confidence:` in frontmatter, which is close. What we lack is
the **negative space section** — an explicit statement per doc of what the pass failed to establish.

### 1.3 The refuted-route ledger

The most unusual thing in the corpus: they record attribution routes that were *tried and failed*,
with the score that killed them, so nobody re-proposes them. Six vtable-attribution routes were
scored; five refused, each with its agree/conflict counts (e.g. "scan method bodies for a string
matching a class name" — agrees 17, conflicts 16, because a string in a method body evidences a
*reference*, not identity). The refusals are pinned by self-tests so reviving one means re-arguing it.

We have burned real time re-deriving things and re-making the same wrong inferences (the
`0x0097FA88`/`89`/`8A` flag cascade; the hull-vs-power slot flip-flop recorded in
`docs/gameplay/hull-subsystem.md` §"Correction history"). A refuted-route ledger is cheap and would
have caught both.

> **Action:** add `docs/guides/refuted-routes.md` — one row per inference technique we tried and
> rejected, with the evidence that rejected it.

### 1.4 Audit with an instrument that had no part in producing the claim

Every wave, they re-derive at least one already-published claim with a tool that shares no input with
the original. It keeps paying: the `.TGL` verification held every conclusion but corrected the
*population* from 17 tables / 2,271 keys to **57 tables / 7,523 keys** — the original had measured
the top-level directory and missed 47 per-episode tables. Their generalisation is worth adopting
verbatim:

> When an audit disagrees with a published figure, the disagreement has been about **how much of the
> world was looked at**. A verification should state its population and how it was enumerated, not
> only its result.

This is precisely the class of defect behind our own "0 collisions" style checks. Our
subsystem-integrity-hash and slot-table work should each state its enumeration method.

### 1.5 The mechanical clean-room gate — the one we should copy into OpenBC

`tools/check_cleanroom.py` (520 lines) enforces three tiers against every spec file and every outgoing
answer:

| Tier | Meaning | Effect |
|---|---|---|
| T1 | Implementation transcription (function bodies, reconstruction source, disassembly, decompiler-invented identifiers like `uVar3` / `param_1` / `DAT_…`) | blocks |
| T2 | Pointers home — workspace paths, apparatus names | blocks |
| T3 | Fidelity / toolchain commentary | warns, baselined |

`--selftest` asserts **in both directions**: every blocking rule fires on a specimen of what it must
catch, and every legitimate form passes untouched. Their stated principle — *a gate that has never
been shown to reject anything is not evidence* — applies to every validation script we own.

This matters for us structurally. **Our repo has no wall.** `reference/decompiled/` holds ~15 MB of
Ghidra C output in the same tree that our agents author OpenBC-bound specs from, and our OpenBC specs
are written by the same context that just read that output. Their rule is the useful test: *description
crosses, expression does not* — "the tail's next link is pointed at the new node" crosses;
`list.tail.next = node;` does not.

> **Action (highest value in this document):** port a `check_cleanroom.py` equivalent into OpenBC and
> run it over `../OpenBC/docs/`. Ban `FUN_`, `DAT_`, `uVar`, `param_`, `unaff_`, `iVar`, `local_`
> tokens and pasted decompiler bodies from anything OpenBC-bound. Ship it with a two-directional
> self-test. This costs a day and materially changes our legal posture.

---

## 2. Content we can use directly

Ranked by value to OpenBC, with an honest note on what we already have.

### 2.1 The SWIG type-descriptor registry at `0x00900A94` — **we do not have this at all**

`model/CLASS_HIERARCHY_EXTRACTED.md` reads the program's own type model rather than inferring it.
`initAppc` registers an array of SWIG type descriptors; the descriptor for type `B` lists every type
accepted where a `B` is expected — i.e. `B`'s full descendant closure. The direct base→derived relation
is that closure's transitive reduction.

| Measure | Value |
|---|---:|
| registered SWIG types | 348 (334 object classes, 14 non-classes) |
| descriptor records read | 1,806 |
| stored closure edges between object classes | 1,060 |
| **direct base→derived edges (transitive reduction)** | **245** |
| roots | 12 |
| max depth | 9 |
| closure-soundness violations found | **0** |

Every converter body was disassembled rather than assumed: SWIG emits an identity thunk for an
offset-0 base as readily as a real adjustment, so a non-null converter is *not* evidence of a non-zero
base offset. 1,054 edges are identity; **exactly four are genuine multiple inheritance**:

| Base | Derived | Base subobject offset |
|---|---|---:|
| `TGConditionHandler` | `ConditionEventCreator` | `+0x08` |
| `TGConditionHandler` | `ConditionalAI` | `+0x28` |
| `TGConditionHandler` | `TGConditionAction` | `+0x20` |
| `WeaponPayload` | `Torpedo` | `+0x108` |

**Why this beats what we have.** Our `docs/engine/rtti-class-catalog.md` extracts 670 classes from
RTTI — a superset by count, but RTTI gives us type identity, not the *accepted-cast* relation, and it
does not give base subobject offsets. The two sources share no input, which makes them ideal
cross-checks. `0x00900A94` appears nowhere in our docs or decompiled reference.

> **Action:** run our own extraction of `0x00900A94` via `game-reverse-engineer` and cross-check it
> against `rtti-class-catalog.md`. Any disagreement is a real finding on one side or the other. The
> `Torpedo ← WeaponPayload @ +0x108` edge in particular is load-bearing for OpenBC's torpedo model and
> we have no equivalent claim.

### 2.2 `spec/Networking.md` — field offsets we lack, plus a message-type registry

Our protocol family (22 docs) is far stronger on the **wire**; theirs is stronger on the **objects
behind it**. Complementary, not overlapping.

New to us:

- `TGMessage` layout: `+0x04` payload ptr, `+0x08` length, `+0x14` **uint16** sequence number,
  `+0x18` retry count. Vtable slots: `+0x08` Serialize, `+0x14` GetBufferSpaceRequired, `+0x18` Copy.
- `g_TGNetworkList` at `0x00995e48`.

> **Correction (this doc, second pass):** an earlier revision listed `g_msgTypeTable` (`0x009962d4`)
> as a gap on our side. It is not — we have it as `DAT_009962d4` in
> [docs/networking/fragmented-ack-bug.md](../networking/fragmented-ack-bug.md) and
> [docs/networking/tgmessage-routing-cleanroom.md](../networking/tgmessage-routing-cleanroom.md).
> What their doc adds is only the *name* and the writer (`TGNetwork::RegisterMessageType`,
> wrapper `0x005E4860`).
- `TGNetwork+0x14` = connect status, **value 2 = connected/ready**; `+0x28` embedded roster;
  `+0xe0` password; `+0x110` profiling flag. `TGWinsockNetwork+0x338` = UDP port.
- `TGWinsockNetwork::SetPortNumber` (`0x006b9bb0`, byte-exact) validates to the range **[5000, 49150]**
  when the validate flag is set. OpenBC should reproduce that acceptance range.
- `TGPlayerList` is a growable array kept **sorted ascending by netID** so lookups binary-search;
  `GetPlayerFromAddress` (`0x006bb9d0`) is a *linear* scan because address is not the sort key.
  `TGNetPlayer::Compare` returns `B.netID − A.netID`.
- A recorded engine defect: four of eight `ServerListEvent` string-returning accessors return the
  shared `None` singleton **without incrementing its refcount** on the gated path, while the four
  integer-returning ones are correct. Flagged explicitly because a reimplementation will silently
  "fix" it and thereby diverge.

### 2.3 `spec/ProximityManager.md` — directly actionable for our two open collision issues

Our `docs/gameplay/collision-detection-system.md` describes the 3-tier pipeline. Theirs specifies the
data structures (100-byte manager, 20-byte axis records, 12-byte endpoints, 28-byte object-table
entries, 16-byte pair nodes) and, more usefully, the **exact toggle semantics**:

- The broad phase is a repeated adjacent-swap sort per axis; each swap updates a per-pair overlap
  count. Count reaching **3** (overlap on all three axes) admits the pair through a category-mask
  filter and appends a collision node; falling to **2** removes it. Cost is proportional to how much
  the world *moved*, not to object count.
- **The two collision toggles are process-global**, not manager fields — a multiplayer flag used when
  a MP session is in progress, a single-player flag otherwise. When the chosen flag is clear it skips
  the pair **only when either object is the player's own ship**. Two non-player ships collide
  regardless; weapon impacts and proximity checks are never gated.
- **Ordering hazard:** constructing a `MultiplayerGame` **copies the single-player flag over the
  multiplayer flag**, so an MP value set before session creation does not survive it.

That last point is a candidate explanation for behaviour around opcode `0x16`
(`UICollisionSetting`, `FUN_00504c70`) and is worth testing against our
`Collision rate limiting disabled (ship+0xEC=0)` and `Collision damage authority inverted` known
issues.

### 2.4 `spec/ShieldFacingDamage.md` — deepest single overlap, and it extends ours

We already have `NormalToFacing` at `0x0056a8d0` and the facing enum. They add the surrounding path:

- `ShipClass::TestHit` (`0x005AE730`, ShipClass vtable slot 80, overriding `DamageableObject::TestHit`
  at `0x00594310`) is the damage-path facing chooser and it runs at **collision-detection time, not
  damage-application time**. Signature takes a *segment* (previous position → current position), not a
  point or direction.
- The vector handed to the dominant-axis test is the impact in **ellipsoid-normalised body space**
  (divide component-wise by the semi-axes at `+0x24C..+0x254`, after subtracting the centre offset at
  `+0x258..+0x260`), mapping the ellipsoid to a unit sphere. Ellipsoid derivation:
  `ComputeShieldEllipsoid` at **`0x005ABAC0`** — an address absent from our docs.
- A **charge gate at 0.1** (constant `0x0088BF28`): if the chosen facing's normalised fraction is not
  greater than 0.1, the shield does not stop the shot and the hull test runs instead.
- Ship `+0x240` holds the last-hit facing, set to `-1` on entry.
- Scan order for the dominant-axis test is `+y, +z, +x, −y, −z, −x` with **strict** comparison, so ties
  go to the earlier entry — a detail that decides edge-on hits and is exactly the kind of thing a
  reimplementation gets subtly wrong.
- Recorded defect: `GetOppositeShield` (`0x0056AAD0`) is a plain **decrement**, which is wrong for even
  indices given pairing `(0,1)(2,3)(4,5)` — facing `0` returns `-1`. It has no caller but its own SWIG
  wrapper and no part in damage.

### 2.5 Areas where they have documents and we have none

`Serialization.md` (typed archive interface, channel vocabulary, object references as identifiers,
base-first chain where a base failure is a stop) · `SaveFile.md` (`.BCS` container, all eleven channel
encodings, 32-stage chain, walked over three real saves) · `Localization.md` (`.TGL` format, four-lane
permutation hash, verified against all 57 shipping tables / 7,523 keys, **zero true hash collisions**)
· the whole UI widget tree (`TGUIObject`, `TGPane` and 54 descendants, `STMenu`, `STButton`) ·
`CharacterClass.md` (86 KB — bridge characters, lip-sync, the second-largest serializer pair) ·
`AIComposition.md` (how a behaviour tree is *built* from script: the three-move construction grammar).

Save/load and localization are not on OpenBC's multiplayer critical path, but the **serialization
channel vocabulary** is: it is the same archive machinery our `StateUpdate` and `ObjCreate` work sits
next to, and "object references are identifiers, not pointers" with a `0` sentinel terminating lists
is a wire-format-shaped fact.

---

## 3. Conflicts and corrections to run down

Every item here is a *checkable disagreement*, not an accepted fact. Verify on our own binary.

### 3.1 `PoweredMaster` is our invention — the game calls it `PowerSubsystem` — **confirmed this pass**

Our `docs/gameplay/power-system.md` names the class at vtable `0x0088A1F0` (ctor `0x00563530`,
ship slot `+0x2B0`) **`PoweredMaster` / "EPS distributor"**. Their `spec/PowerSubsystem.md` names the
same class — same vtable, same ctor, same `sizeof 0xDC`, same class ID `0x8022`, matching field
layout — **`PowerSubsystem`**, following the program's own published method table.

Verified against our own `reference/scripts/` this pass:

- `PoweredMaster` appears in **zero** shipped game scripts.
- `ShipClass.GetPowerSubsystem()` is called throughout the shipped mission scripts, and the methods
  invoked on its result include **`GetMainBatteryWatcher()` / `GetBackupBatteryWatcher()`** — i.e. the
  battery/conduit class, which is the `0x0088A1F0` one.

The game's own scripting surface therefore binds the name `PowerSubsystem` to the class we call
`PoweredMaster`. Since OpenBC must expose the same Python API surface to stock mission scripts, our
internal name is not merely cosmetic — it invites an OpenBC class named `PowerSubsystem` that is the
*wrong* class.

> **Action:** rename `PoweredMaster` → `PowerSubsystem` across `docs/gameplay/power-system.md`,
> `docs/gameplay/hull-subsystem.md`, `docs/protocol/wire-format-spec.md`,
> `docs/protocol/subsystem-integrity-hash.md`, and the OpenBC power spec. Also reconcile the class-ID
> disagreement *inside our own docs*: `power-system.md` says `0x8022`, `hull-subsystem.md` says
> `0x813E`.

Two further claims from their doc to verify, since our doc disagrees:

1. They state `0x00563530` chains the **`ShipSubsystem`** constructor (`0x0056B970`) with flag 0, i.e.
   the supply is a *sibling* of the consumers, not a `PoweredSubsystem`. Our `power-system.md`
   evidence block says this class "derives from `PoweredSubsystem` base". One of these is wrong.
2. They give `SaveToStream` `0x00563F00` / `LoadFromStream` `0x00564000` as **overrides**, writing the
   dispense list as a **null-terminated run of object ids** (not count-prefixed), with the floats at
   `+0xBC`/`+0xC0` written *after* the list — so stream order is not field order. An id of `0`
   mid-list would truncate. We have no equivalent claim.

### 3.2 Where **we** are right and their corpus is wrong

Their hand-written `model/CLASS_HIERARCHY.md` lists vtable `0x892c98` as `ShipSubsystem`
(ctor `0x560470`, size `0x88`). Our `docs/gameplay/hull-subsystem.md` proves `0x00892C98` is
**`HullClass`** via the vtable's own name-returning entry — the literal strings `HullClass` /
`_p_HullClass` / `HullClassPtr` at `0x008E4EC0` / `EC` / `EDC`.

Notably, that is *their own strongest attribution technique* (`ANSWERABILITY.md`: "entry 9 of a class's
dispatch table returns a pointer to the class's own name"), applied by us independently and reaching a
result their hand-written model contradicts. Their file is explicitly marked superseded by the
extracted one, so this is a stale-doc defect on their side rather than a methodological one — but it
is a concrete case where our binary truth is stronger.

### 3.3 The one number of theirs to treat with suspicion

`ANSWERABILITY.md` reports **162 of 242 reconstruction vtables are wrong** and only 17.8% verified,
and explicitly says any slot→function mapping sourced from their reconstruction is unusable. Their
*attribution* work (which table belongs to which class, read from the original image) is separately
sound at 241 of 334 classes. **Do not take slot numbers from their spec docs without checking** — take
class attributions and field offsets, which rest on different evidence.

---

## 4. What we should not take

- **Anything landing on their 19.8% hollow region** (3,326 functions, stub or never written). The
  address is known; the behaviour is not.
- **Floating-point computation details.** Their own verdict: these bodies are disproportionately
  untested clones. Both our shield/power/damage math and theirs are weakest in the same place, so
  agreement between us is not corroboration — it may be the same reading error twice.
- **Rendering internals.** Deliberately deprioritised on their side; the least reconstructed cluster.
- **The `bc_dauntless` reimplementation source**, if OpenBC is to stay clean-room. Specs cross; another
  project's implementation expression does not.

---

## 5. Action list

Ordered by value per unit of effort.

| # | Action | Owner | Why |
|---|---|---|---|
| 1 | Port a `check_cleanroom.py` equivalent into OpenBC with a two-directional self-test; ban `FUN_`/`DAT_`/`uVar`/`param_`/`iVar`/`local_` and pasted decompiler bodies from `../OpenBC/docs/` | orchestrator | Only structural defence for OpenBC's clean-room posture; we currently have none |
| 2 | Extract the SWIG type registry at `0x00900A94` ourselves; cross-check against `rtti-class-catalog.md` | `game-reverse-engineer` | Independent second source for the class graph; gives base subobject offsets RTTI cannot |
| 3 | Rename `PoweredMaster` → `PowerSubsystem` across our docs + OpenBC power spec; reconcile the `0x8022` vs `0x813E` class-ID disagreement | orchestrator | Confirmed this pass against shipped scripts; wrong name propagates into OpenBC's public API |
| 4 | Verify `0x00563530`'s base ctor (`ShipSubsystem` `0x0056B970` vs `PoweredSubsystem`) | `game-reverse-engineer` | Direct contradiction between our doc and theirs |
| 5 | Test the "MP collision flag is overwritten by the SP flag at `MultiplayerGame` construction" claim | `game-reverse-engineer` + `network-protocol-analyst` | Candidate root cause for our open collision rate-limiting / authority issues |
| 6 | Document `g_msgTypeTable` (`0x009962d4`) and `TGMessage` field offsets in `docs/protocol/transport-layer.md` | `game-reverse-engineer` | Fills a real gap in our transport doc |
| 7 | Extend `docs/gameplay/shield-system.md` with the `TestHit` (`0x005AE730`) path, `ComputeShieldEllipsoid` (`0x005ABAC0`), and the 0.1 charge gate (`0x0088BF28`) | `game-archaeology-specialist` | Our shield doc stops at facing selection; the segment/ellipsoid-normalised path is where a reimplementation diverges |
| 8 | Add a program-coverage dimension to the v5 trackers, and a "what this pass did NOT establish" section per doc | `documentation-writer` | Doc-count validation cannot tell an implementer where the evidence runs out |
| 9 | Create `docs/guides/refuted-routes.md` | `documentation-writer` | Cheap; would have prevented at least two of our own cascades |

---

## 6. Cross-references

- [docs/engine/rtti-class-catalog.md](../engine/rtti-class-catalog.md) — our RTTI-side class model (§2.1 cross-check target)
- [docs/gameplay/power-system.md](../gameplay/power-system.md) — the naming correction in §3.1
- [docs/gameplay/hull-subsystem.md](../gameplay/hull-subsystem.md) — the `0x00892C98` attribution in §3.2
- [docs/gameplay/shield-system.md](../gameplay/shield-system.md) — extension targets in §2.4
- [docs/gameplay/collision-detection-system.md](../gameplay/collision-detection-system.md) — §2.3
- [docs/protocol/transport-layer.md](../protocol/transport-layer.md) — `TGMessage` / `g_msgTypeTable` gap in §2.2
- [docs/guides/v5-doc-validation-workflow.md](../guides/v5-doc-validation-workflow.md) — where §1.1/§1.2 changes land
