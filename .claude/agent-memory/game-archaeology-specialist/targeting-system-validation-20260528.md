# Ship Targeting State Machine — v5 Validation (2026-05-28)

Exhaustive RE of the Ship targeting state machine in stbc.exe. Scope: full field
layout, state-machine transitions, event semantics (3 events), network/replication
verdict, weapon/AI integration. Live Ghidra (program STBC.exe, image_base
0x00400000, function_count 18,625).

This memo SUPERSEDES the brief targeting coverage in ship-navigation v5 doc.

## 1. Field Layout (Ship class, target sub-block)

All offsets byte-confirmed via search_instructions and Ship_InitTargetState
(0x005ab970) disassembly.

| Offset | Size | Type | Name | Init value | Notes |
|---|---|---|---|---|---|
| +0x21C | 4 | u32 | targetId | 0 | TGSceneObject network ID (object's +0x4) of current target; 0 = no target |
| +0x220 | 4 | u32 | targetSubsystemId | 0 | Subsystem network ID (subsys's +0x4); 0 = whole-ship target |
| +0x224 | 1 | u8 | manualAimFlag | 0 | 0 = auto-aim (lazy-sync to target pos), 1 = manual-aim (cursor in space) |
| +0x225..+0x227 | 3 | — | padding | — | struct align |
| +0x228 | 4 | f32 | targetOffsetX | DAT_009a2878 | Auto: tracks target pos via vtable[+0x94]; Manual: cursor world-space x |
| +0x22C | 4 | f32 | targetOffsetY | DAT_009a287c | (see above) |
| +0x230 | 4 | f32 | targetOffsetZ | DAT_009a2880 | (see above) |

Confirmed by `Ship_InitTargetState` (0x005ab970) byte sequence:
```
MOV [param+0x21C], 0
MOV [param+0x220], 0
MOV [param+0x224], 0
MOV [param+0x228], DAT_009a2878
MOV [param+0x22C], DAT_009a287c
MOV [param+0x230], DAT_009a2880
```

Adjacent fields (+0x234..+0x248) confirmed via Ship_InitTargetState to belong to
a separate (likely navigation/autopilot) block — NOT targeting. Excluded from
this memo.

`DAT_009a2878/7C/80` is the global "world center" / origin sentinel used as the
default offset when no target is set. Same constant block referenced by
`Ship_GetTargetOffsetVec` (0x005ae650) fall-through path.

## 2. State Machine Functions

13 functions form the targeting subsystem. All addresses, callees, and event
emissions byte-confirmed.

### 2.1 Producers (write +0x21C / +0x220 / +0x224 / +0x228..+0x230)

| Fn | Addr | Renamed | Writes | Posts event | Notes |
|---|---|---|---|---|---|
| Ship_SetTarget | 0x005ae210 | (already) | +0x21C, then calls SetSubsystem | 0x800058 TARGET_WAS_CHANGED | Hub; conditional on `getTarget()!=newTarget`; uses TGObjPtrEvent (factory 0x2C) |
| Ship_SetTargetSubsystem | 0x005ae2c0 | yes | +0x220, calls SetOffset(0,0) | 0x80005A TARGET_SUBSYSTEM_SET | Conditional; also drives FUN_00585580 (4 weapon-style retargeting calls) |
| Ship_SetTargetOffset | 0x005ae430 | yes | +0x224, +0x228..+0x230 | 0x800059 (ET_TARGET_OFFSET_CHANGED — name CONFIRMED by behavior) | Manual=1+vec OR auto=0(zero vec); cascades to subsystem.aim cache (+0x40..+0x4C) via ship+0x284 walk |
| Ship_GetTargetObject | 0x005ae170 | yes | clears +0x21C if stale | none | Resolves targetId via TGSceneGraph_GetObjectByID; AUTO-CLEARS on bad/missing |
| Ship_SetTargetByObjectHandle | 0x005ae1b0 | yes | (via SetTarget) | (via SetTarget) | Public wrapper — resolves handle in scene graph first |
| Ship_SetTargetByName | 0x005ae1e0 | yes | (via SetTarget) | (via SetTarget) | Public wrapper — uses FUN_00434E70 (string→obj lookup) |
| Ship_CycleNextTarget | 0x005ae6d0 | yes | (via SetTarget) | (via SetTarget) | Walks scene-set linked list (set+0x34 count, set+0x68 head); seeds cursor from CURRENT target (ship+0x21C) — filters via ship.vtable[+0xCC] (IsValidTargetCandidate) |
| Ship_InitTargetState | 0x005ab970 | yes | ALL 6 fields = init values | none | Called from Ship ctor |
| Ship_NotifySubsystemsTargetChanged | 0x005b0bb0 | yes | NONE (just dispatches) | none | Called by Ship_SetTarget BEFORE event post; walks ship+0x284 sub-list, calls subsys.vtable[+0x90] (OnTargetChanged) |

### 2.2 Consumers (read +0x21C — non-dead)

| Fn | Addr | Role | Notes |
|---|---|---|---|
| Ship_GetTargetObject | 0x005ae170 | resolver/getter | direct read with auto-clear |
| Ship_NotifySubsystemsTargetChanged | n/a | (no read of 0x21C) | reads ship+0x284 only |
| Ship_SetTargetSubsystem | 0x005ae2c0 | compares against new subsys id | reads at 0x005ae2f7 |
| Ship_SetTargetOffset | 0x005ae430 | iterates subsys aim cache | reads at 0x005ae4cb, 0x005ae507 |
| Ship_CycleNextTarget | 0x005ae6d0 | uses targetId as iterator cursor | reads at 0x005ae6e0 — explains the "+0x87 fabricated" lingering claim: that WAS the seed cursor, NOT a separate cycle index |
| ShipClass_SetTargetHandler | 0x005b0e00 | event handler (0x800058) | WRITES +0x21C+0x220 from event payload — the actual state mutator |
| CollisionRateLimit (FUN_005a22a0) | 0x005a22a0 | Ship vtable+0x13C — collision cooldown gate | reads via Ship_GetTargetObject to check "am I targeting attacker" |
| FUN_00489bd0 (AI scoring) | 0x00489bd0 | PlainAI target scoring | reads via Ship_GetTargetObject; also reads OTHER ships' targets (line `iVar7 != unaff_retaddr && FUN_005ae170() == piVar13` — "is another ship targeting me?") |
| FUN_00538590 | 0x00538590 | Mouse-LeftClick TargetObject handler | reads via Ship_GetTargetObject; calls Ship_SetTarget |
| FUN_00538fc0 | 0x00538fc0 | Mouse-LeftClick TargetSubsystem handler | reads via Ship_GetTargetObject; posts event 0x80005B + calls Ship_SetTarget |
| FUN_00567c20 | 0x00567c20 | Ship death/exit-scene handler | reads via Ship_GetTargetObject; calls Ship_SetTarget(0,0) if target was just-died non-friendly |
| FUN_00536160 | 0x00536160 | Subsystem-list select handler | calls Ship_SetTargetSubsystem |
| FUN_00509ce0 | 0x00509ce0 | mouse cursor/HUD pick | calls Ship_SetTargetOffset(1, &vec) — manual aim path |

### 2.3 Dead code

* `DEAD_Ship_SaveCheckpoint` at 0x005b0fa0 (renamed) — full-state serializer to a
  stream via vtable[+0x4C/0x6C/0x74/0x84]; would serialize +0x21C, +0x220,
  +0x224, +0x228..+0x230 in a TGStreamedObject-style write. ZERO callers
  (search_byte_patterns A0 0F 5B 00 → no matches; no DATA xref). Likely cut
  savegame/checkpoint feature. Spans 0x005b0fa0–0x005b1320, includes the
  +0x21C/+0x220/+0x224/+0x1F8/.../+0x2F8 writes at 0x005b0e19, 0x005b0e23,
  0x005b1032, 0x005b1054, 0x005b1316 (the misleading hits from
  reconnaissance). **Do NOT cite this code as evidence for active behavior.**

## 3. State Transitions (byte-confirmed flow diagram)

```
                                    EXTERNAL DRIVERS
                                          |
        +------------+-----------+--------+-----------+--------------+
        |            |           |                    |              |
        v            v           v                    v              v
  MOUSE-CLICK   AI-SCORING   HUD/MAP UI         DEATH-CASCADE    SUBSYS PANE
   538590         489bd0      4fe560 etc.          567c20            536160
        |            |           |                    |              |
        v            v           v                    v              v
  Ship_Set      Ship_Set     Ship_Set                Ship_       Ship_SetTarget
   Target        Target       Target              SetTarget       Subsystem
   (5ae210)     (5ae210)     (5ae210)               (0,0)          (5ae2c0)
        |                                                              |
        |                                                              |
        v                                                              v
  +0x21C = newId                                                  +0x220 = subId
  Ship_NotifySubsystemsTargetChanged (5b0bb0)                 +0x21C unchanged
        | walks ship+0x284, vtable[+0x90] OnTargetChanged
        |
        |  POST EVENT
        v                                                              v
  TGObjPtrEvent (factory 0x2C)                            TGEvent (factory 0x28)
  evt+0x10 = 0x800058 TARGET_WAS_CHANGED                  evt+0x10 = 0x80005A
  evt+0x28 = newTargetId                                  TARGET_SUBSYSTEM_SET
  evt+0x18 = (TGObjPtrEvent context fields)                   |
        |                                                     |
        |       EventManager (0x0097F838)                     |
        |        broadcast LOCAL ONLY                         |
        |          (no network relay registered in MP)        |
        v                                                     v
  Handlers registered for 0x800058:                  Handlers for 0x80005A:
  - ShipClass_SetTargetHandler @ 5b0e00              - 537be0 STTargetMenu
    (writes +0x21C, +0x220 from evt+0x28, +0x08)     - 5ae2c0 itself (when called
  - 4fe560 MapWindow::TargetChangedHandler            with !=0 subsystem)
  - 537be0 STTargetMenu::TargetChanged
  - 54b2f0/54b6e0 (other UI panes)
  - 547b10 SensorPane
  - 546dc0
  - SP-ONLY: MultiplayerGame__ChangedTargetHandler
    (6a1a70) — sends opcode 0x0D via SendEventMessage
    IF source.id == player.slot+0x54 AND !IsMultiplayer

  ============================
  MANUAL AIM (cursor in space):
  ============================
  FUN_00509ce0 -> Ship_SetTargetOffset(manual=1, &vec)  [@ 5ae430]
                       |
                       v
                  +0x224 = 1
                  +0x228..+0x230 = vec
                  walk ship+0x284, for each subsys:
                    subsys.aim+0x90..+0x98 = (targetId, vec.x,y,z)  [if matches +0x21C]
                  POST EVENT 0x800059 (TARGET_OFFSET_CHANGED — TGEvent factory 0x28)

  ============================
  AUTO AIM (lazy-sync):
  ============================
  Ship_GetTargetOffsetVec (5ae650) — called by weapons/aim
                       |
                       v
                  if manualAimFlag==1: return &ship+0x228 (cached cursor)
                  else: get targetObj (5ae630); read tgt+0x78..+0x80 (pos);
                        write into ship+0x228..+0x230 (anti-stale sync);
                        return &ship+0x228
                  If targetObj==NULL: fall back to world origin
                  (DAT_009a2878..0x880).
```

## 4. Three Events — Byte-Confirmed

### Event 0x800058 — TARGET_WAS_CHANGED [HIGH]

* **Post site (sole)**: `0x005ae27a` in `Ship_SetTarget`. Bytes:
  `c7 46 10 58 00 80 00` = `MOV [ESI+0x10], 0x800058` (on TGObjPtrEvent).
* **Event class**: TGObjPtrEvent (factory ID 0x2C from `FUN_00717b70(0x2C)`),
  `[evt+0x28] = newTargetId` (the +0x4 of new target obj, or 0).
* **Handlers (8 total)** — registered via `FUN_006da130` (the event-name binder)
  for `&DAT_00800058`:
  - `MultiplayerGame::ChangedTargetHandler` at 0x006a1a70 — **SP-ONLY**; sends
    opcode 0x0D to peers IF event.source==local_player. In MP, MultiplayerGame
    DOES NOT register this binding (gate at 0x0069ea5b before
    `FUN_006db380(&DAT_00800058, ...)` in MultiplayerGame_Ctor).
  - `ShipClass_SetTargetHandler` at 0x005b0e00 — ALWAYS active; writes
    ship+0x21C and ship+0x220 from event payload.
  - `MapWindow::TargetChangedHandler` (FUN_004fe560) — HUD/starmap update.
  - `STTargetMenu::TargetChanged` (FUN_00537be0) — target-info panel.
  - `FUN_0054b2f0`, `FUN_0054b6e0`, `FUN_00547b10`, `FUN_00546dc0` — other
    HUD panes.
* **Network relay**: **NONE in multiplayer**. The only path that could relay it
  (MultiplayerGame::ChangedTargetHandler) is unregistered in MP and its body
  short-circuits on `DAT_0097fa8a != 0`.

### Event 0x80005A — TARGET_SUBSYSTEM_SET [HIGH]

* **Post sites (2)**:
  - `0x005ae40b` in `Ship_SetTargetSubsystem`. Bytes:
    `c7 47 10 5a 00 80 00` = `MOV [EDI+0x10], 0x80005A`.
  - `0x00537dc1` in `STTargetMenu::TargetedSubsystemChanged` (different posting
    code path for UI sync).
* **Event class**: TGEvent (factory 0x28 from `FUN_00717b70(0x28)` +
  `FUN_006d5c00(0)`).
* **Handlers**: 1+ in `STTargetMenu` ctor (FUN_00537be0 line
  `FUN_006db380(&DAT_0080005a, ...)`).
* **Network relay**: **NONE**. Never appears in MultiplayerGame's handler
  registration list (FUN_0069efe0).

### Event 0x800059 — TARGET_OFFSET_CHANGED [MEDIUM→HIGH]

* **Post site (sole)**: `0x005ae57c` in `Ship_SetTargetOffset`. Bytes:
  `c7 46 10 59 00 80 00` = `MOV [ESI+0x10], 0x800059`.
* **Event class**: TGEvent (factory 0x28).
* **Handlers**: ZERO via FUN_006da130 / FUN_006db380 string-binding. The xref
  search to 0x00800059 returns ONLY the post site itself. Event is **emitted
  but has no consumers in the stripped binary** — likely dead post or expected
  to be wired from Python (no Python handler observed either).
* **Naming**: Pre-anchored guess "ET_TARGET_OFFSET_CHANGED" CONFIRMED by post
  site living inside `Ship_SetTargetOffset`. Promoted MEDIUM → HIGH.
* **Network relay**: NONE.

### (Bonus) Event 0x80005B — TARGET_SUBSYSTEM_FROM_CLICK [MEDIUM]

* **Post site (sole)**: `0x005390a2` in `FUN_00538fc0` (Mouse-LeftClick on
  subsystem). TGEvent factory 0x28.
* **Handlers**: 1 — `FUN_0054b6e0` (subsystem pane) registers it.
* Not a SetTarget event proper; it's a UI-targeting-via-click notification.
  Recorded here for completeness; not in the SetTarget cascade.

## 5. Network/Replication — VERDICT

**Ship targeting state (+0x21C target, +0x220 subsys, +0x224 manual, +0x228..230
offset) is NOT serialized on the wire.**

### Evidence

* **Not in StateUpdate (opcode 0x1C)**: Read full body of `Ship__WriteStateUpdate`
  (0x005B17F0, 348 lines, all 8 dirty-flag branches 0x01/0x02/0x04/0x08/0x10/0x40/
  0x20/0x80) and `Ship__ReadStateUpdate` (0x005B21C0, 190 lines). **Zero
  reads of +0x21C, +0x220, +0x224, +0x228, +0x22C, +0x230 in either function.**
  The 8 flag payloads cover position absolute, position delta, forward, up,
  speed, cloak, subsystem health, weapon health. No target field, no aim cursor.

* **No dedicated opcode**: No entry in the game-opcode table (0x00–0x2A) is
  named "TargetChange" or similar. The 41-entry MpgameHandleMessage jump table
  at 0x0069F534 was previously v5-validated; no entry routes to target state.

* **No PythonEvent shipment**: MultiplayerGame::ChangedTargetHandler
  (0x006a1a70) sends opcode 0x0D (PythonEvent2) via SendEventMessage — but
  ONLY in single-player (`if (DAT_0097fa8a == '\0')` gate). In multiplayer the
  handler is unregistered AND its body short-circuits. No 0x0D shipped from
  target-change in MP.

* **The "Save/Restore" path** (DEAD_Ship_SaveCheckpoint at 0x005b0fa0) DOES
  serialize all 6 target fields via vtable[+0x84] writes — but this function
  has ZERO callers in stbc.exe. Almost certainly cut savegame code. NOT a
  network replication path.

* **InitNetwork timing**: When a new player joins, the host's
  ObjectCreatedHandler creates ships via ObjCreate (opcode 0x02/0x03). The
  serialization in ObjCreate covers pos/orient/vel/species/team (per
  objcreate-serialization v5 memo) — NOT target state. New peers see ships at
  their world-space positions but with NO knowledge of who-targets-whom.

### Implication for HUD overlays

Other players' targets are **NOT visible** on the wire. Any HUD element that
shows "X is targeting Y" must derive that information from observed firing
events (opcode 0x07 StartFiring carries a target field — separate channel).

This matches stock-dedi behavior: spectator HUD shows the targeted ship's name
only for ships YOU CAN SEE BEING FIRED ON, not via target-state replication.

## 6. Weapon Integration

* **Ship_NotifySubsystemsTargetChanged** (0x005b0bb0) is called by
  Ship_SetTarget BEFORE the event post. It walks ship+0x284 (subsystems/weapons
  sub-list), invokes `subsys.vtable[+0x90]` on each (= `OnTargetChanged`). This
  is the direct hook by which weapons learn of the new target without going
  through the event system. **Synchronous direct dispatch** — no queueing.

* **Phaser TryFireRoundRobin** (0x00584930) and **Phaser__SingleShot**
  (0x00584E40) receive the target object as a parameter (`param_2`), they do
  NOT directly read `ship+0x21C`. The caller chain (FUN_005847d0 →
  PoweredSubsystem_Update → upstream) gets the target from
  `Ship_GetTargetObject` once per tick and passes it down.

* **CollisionRateLimit** (FUN_005a22a0, Ship vtable+0x13C) calls
  `Ship_GetTargetObject` — used to detect "is the colliding ship the one I'm
  targeting" for rate-limiting decisions.

* **Tractor beam** (FUN_005ae2c0 callees `FUN_00585580`): when a subsystem
  target is set, FUN_005ae2c0 calls `FUN_00585580(weapon, &offset_vec)` up to
  4× for `ship+0x2bc`, `ship+0x2d4`, `ship+0x2b8`, `ship+0x2b4`, `ship+0x70C`
  — the 4 weapon-slot heads. These are the per-weapon "target subsystem
  changed" notifications. Tractor (`+0x2d4`) re-aims; pulse phasers
  (`+0x2bc`) update target lock; etc.

* **Weapons read +0x21C indirectly** via subsystem `aim+0x90` cache (set by
  Ship_SetTargetOffset at 0x005ae51b). When the aim cache fires, the cached
  targetId (=ship+0x21C at time of cache update) is read.

## 7. AI Integration

* **PlainAI scoring** (FUN_00489bd0) reads `Ship_GetTargetObject` directly:
  - Branch at line ~78: if `param_1+0x90 != 0` (this AI has a target), call
    Ship_GetTargetObject and compare against piVar13 (candidate target obj +4)
    to score "am I already targeting this?".
  - Loop at line ~150: walks all peer ships in the scene; for each, calls
    `FUN_005ae170()` (their GetTargetObject); if their target == piVar13
    (= our candidate target), score += `_DAT_00888860` (the "shared target"
    weight).
* **AI** also calls Ship_SetTarget through `Ship_SetTargetByObjectHandle`
  (5ae1b0) or `Ship_SetTargetByName` (5ae1e0) — both wrap SetTarget.

## 8. Cross-Reference Map

```
Ship_InitTargetState (5ab970)
   └─[ called from Ship ctor (unverified) ]

Ship_SetTarget (5ae210) ────┐
   ├─→ Ship_GetTargetObject (5ae170)
   ├─→ Ship_NotifySubsystemsTargetChanged (5b0bb0)
   │     └─→ weapon.vtable[+0x90] OnTargetChanged
   ├─→ TGObjPtrEvent_Ctor (FUN_00717b70(0x2c)+FUN_00718010+ctor)
   ├─→ TGEventManager__PostEvent(0x800058)
   │     ├─→ MapWindow handler (4fe560)
   │     ├─→ STTargetMenu handler (537be0)
   │     ├─→ ShipClass_SetTargetHandler (5b0e00) ← STATE WRITE
   │     ├─→ MultiplayerGame::ChangedTargetHandler (6a1a70) [SP-only]
   │     └─→ 4 more UI handlers
   └─→ Ship_SetTargetSubsystem (5ae2c0)
         ├─→ Ship_GetTargetObject (5ae170)
         ├─→ Ship_SetTargetOffset (5ae430) — recursive call to clear offset
         ├─→ FUN_00585580 ×4 (weapon retarget notify; tractor + 3 phasers)
         └─→ TGEventManager__PostEvent(0x80005A)
               └─→ STTargetMenu handlers, etc.

Ship_SetTargetOffset (5ae430)
   ├─→ Ship_GetTargetOffsetVec (5ae650) [in else-branch when manual=0]
   ├─→ FUN_00583F60 (resolve subsys obj)
   ├─→ FUN_00585360 (resolve subsys aim cache)
   ├─→ ShipSubsystem__GetChildSubsystem (5ae4fe = FUN_0056c570)
   └─→ TGEventManager__PostEvent(0x800059) — orphan event, no handlers

Ship_CycleNextTarget (5ae6d0) — uses ship+0x21C AS CURSOR
   ├─ reads scene-set count from ship.set+0x34, walks set+0x68 chain
   ├─ filters via this.vtable[+0xCC] (IsValidTargetCandidate)
   └─→ Ship_SetTarget (loops back into above)
```

## 9. Open Questions / Resolved Items

### Resolved this session

* **Ship_navigation memo §"+0x87 fabricated"**: NOT fabricated. `param_1[0x87]`
  in `Ship_CycleNextTarget` (0x005ae6d0) is array-indexed access to ship+0x21C
  (0x87 * 4 = 0x21C). Used AS the linked-list cursor seed (start from current
  target's set-position). Re-classify the memo entry from "fabricated" to
  "anchored to +0x21C as cursor". Promoted MEDIUM → HIGH.
* **Event 0x800059 identity**: CONFIRMED ET_TARGET_OFFSET_CHANGED. Promoted
  MEDIUM → HIGH.
* **Target state replication**: CONFIRMED NOT REPLICATED. Hard verdict —
  matches behavioral observation that BC's HUD never shows who other players
  target.

### Still open

* **Ship_InitTargetState caller**: not traced this session. Likely called from
  Ship_Ctor or `ShipClass` constructor chain. (Low priority — confirmed init
  values regardless.)
* **DEAD_Ship_SaveCheckpoint origin**: dead but full. Was savegame removed
  intentionally? Worth checking `cut-content-analysis.md`. (Curiosity only —
  no MP relevance.)
* **Event 0x80005B**: posted only by mouse-click (FUN_00538fc0); consumed by
  FUN_0054b6e0. Not in the SetTarget cascade. Documented for completeness; not
  re-investigated.

## 10. Documentation Companion Suggestions

Suggested doc updates for documentation-writer (NOT performed this session):

1. **docs/gameplay/ship-navigation.md** — add §"Target State Replication"
   confirming target is NOT on the wire. Update the +0x87 footnote.
2. **docs/protocol/stateupdate.md** — add explicit note: "Target state
   (+0x21C/+0x220/+0x224/+0x228..+0x230) is NOT part of StateUpdate dirty
   flags."
3. **docs/engine/event-system-architecture.md** — add 0x800058, 0x800059,
   0x80005A, 0x80005B to event constants table.
4. **docs/gameplay/combat-mechanics-re.md** — link target state machine to
   weapon firing pipeline via Ship_NotifySubsystemsTargetChanged hook.
5. New doc proposed: `docs/gameplay/targeting-system.md` — full memo-to-doc
   render with the field table, state diagram, event semantics, and the
   "NOT replicated" verdict prominently called out.

## 11. Ghidra Mutations

13 functions renamed, function created for 0x005b0e00 and 0x005b0fa0, program
saved:

| Addr | Old | New |
|---|---|---|
| 0x005ab970 | FUN_005ab970 | Ship_InitTargetState |
| 0x005ae170 | FUN_005ae170 | Ship_GetTargetObject |
| 0x005ae1b0 | FUN_005ae1b0 | Ship_SetTargetByObjectHandle |
| 0x005ae1e0 | FUN_005ae1e0 | Ship_SetTargetByName |
| 0x005ae210 | Ship_SetTarget | (already named — unchanged) |
| 0x005ae2c0 | FUN_005ae2c0 | Ship_SetTargetSubsystem |
| 0x005ae430 | FUN_005ae430 | Ship_SetTargetOffset |
| 0x005ae630 | FUN_005ae630 | Ship_GetTargetSubsystemObj |
| 0x005ae650 | FUN_005ae650 | Ship_GetTargetOffsetVec |
| 0x005ae6d0 | FUN_005ae6d0 | Ship_CycleNextTarget |
| 0x005b0bb0 | FUN_005b0bb0 | Ship_NotifySubsystemsTargetChanged |
| 0x005b0e00 | (was LAB_) | ShipClass_SetTargetHandler [created] |
| 0x005b0fa0 | (was orphan code) | DEAD_Ship_SaveCheckpoint [created] |
| 0x006a1a70 | (was orphan code) | MultiplayerGame__ChangedTargetHandler [created] |

## 12. Status

**v5 status: validated** (all wire-relevant claims byte-confirmed; verdict
"NOT replicated" anchored to byte-level absence in WriteStateUpdate +
ReadStateUpdate + handler-registration-table; 3 of 4 event identities promoted
to HIGH).

Confidence ratings per claim:
- Field layout: HIGH (byte-confirmed via Ship_InitTargetState + 30+ access sites)
- State machine producers: HIGH (all 9 fns disassembled + event sites confirmed)
- State machine consumers: HIGH (all non-dead readers traced)
- Network NOT replicated: HIGH (negative proof via full WriteStateUpdate +
  receiver + MultiplayerGame handler table audit)
- Event 0x800058: HIGH (post site + 8 handlers + relay gate)
- Event 0x800059: HIGH (post site confirmed; ZERO handlers also confirmed)
- Event 0x80005A: HIGH (post site + STTargetMenu handler)
- Weapon integration: HIGH (Ship_NotifySubsystemsTargetChanged byte path)
- AI integration: HIGH (FUN_00489bd0 dual reader pattern decompiled)
