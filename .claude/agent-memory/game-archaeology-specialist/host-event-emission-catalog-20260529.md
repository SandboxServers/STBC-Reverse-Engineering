---
name: host-event-emission-catalog-20260529
description: Catalog of every TGEvent the stock STBC HOST emits during damage / beam / explosion / death sequences, with trigger conditions and wire-relay verdicts. Unblocks OpenBC parity bug for opcodes 0x06 / 0x1A / 0x29.
metadata:
  type: project
---

# Host Event Emission Catalog — Damage / Beam / Explosion / Death

**Investigation date:** 2026-05-29  
**Binary:** STBC.exe (stock dedi, image base 0x00400000)  
**Goal:** map every TGEventManager::PostEvent call in the damage/combat/death pipeline, identify which become wire packets (opcode 0x06/0x1A/0x29 et al.), and produce the OpenBC parity checklist.

## TL;DR

Three wire emit channels:
1. **HostEventHandler relay (FUN_006A1150)** — emits **opcode 0x06 PythonEvent** to NoMe group. Subscribed to event IDs `0x008000DF` (AddToRepairList), `0x00800074` (REPAIR_COMPLETED), `0x00800075` (REPAIR_CANNOT_BE_COMPLETED). Reliable.
2. **MultiplayerGame_ObjectExplodingHandler (FUN_006A1240)** — emits **opcode 0x06 PythonEvent** to NoMe group for event `0x0080004E` (OBJECT_EXPLODING). Reliable.
3. **DamageableObject__SendExplosions_0x29 (FUN_00595C60)** — emits **opcode 0x29 Explosion** to a specific peer. Unreliable. Only called from RequestObj handler (0x006A02A0) and NewPlayerInGameHandler (0x006A1E70). **NOT** called from the per-tick damage simulation.

All non-zero-HP-crossing damage (subsystem hits, repair progress, status toggles) stays **local** to the host's simulation. Clients receive damage results via:
- **Wire: opcode 0x1C StateUpdate** (per-tick subsystem health round-robin via dirty-bit serialization).
- **Wire: opcode 0x06 PythonEvent** (only the 4 events above).
- **Wire: opcode 0x29 Explosion** (only mid-fight join sync).

**OpenBC parity:** to safely STOP relaying 0x06/0x1A/0x29 from client→other-clients, OpenBC must implement HOST-SIDE emitters for the 4 events that DO go on the wire as 0x06 plus the explosion catch-up for new joiners. Beam fire (0x1A) is NEVER originated by the host — relay IS the correct behavior, with the caveat that the host re-broadcasts received beam fires via FUN_0069FBB0 (Forward group).

---

## Section 1 — Damage Path Catalog

Damage path: `WeaponHitHandler @ 0x005AF010` → `ApplyWeaponDamage @ 0x005AF420` → `DoDamage FUN_00594020` → `ProcessDamage FUN_00593E50` → walks subsystem handlers at ship+0x128 → `FUN_004B1FF0` → `FUN_004B4B40` (DamageVolume application) → per-subsystem voxel-grid damage actuation → `ShipSubsystem_SetCondition @ 0x0056C470`.

| Trigger | Event ID | Event class | Where posted | Wire-relayed? |
|---|---|---|---|---|
| Subsystem condition reduced below max (any damage) | **0x80006B SUBSYSTEM_HIT** | TGObjPtrEvent (factory 0x010C, size 0x2C) | `ShipSubsystem_SetCondition @ 0x0056C470` (immediate-MOV at 0x0056C51B) | NO. Local-only. Used by `DamageDisplay::HandleSubsystemEvent` for HUD updates. |
| Subsystem turned ON (status changed) | **0x80006C g_dwTgEvent_SubsystemStatusToggle** | TGEvent (factory 0x101, size 0x28, allocator FUN_004371B0) | `FUN_00562560` (immediate-MOV at 0x005625C3) | NO. Local-only at this hop. Bridges to wire via `0x008000DD` handler subscription below. |
| Subsystem turned OFF (status changed) | **0x80006C g_dwTgEvent_SubsystemStatusToggle** | TGEvent | `FUN_00562630` (immediate-MOV at 0x00562695) | NO. Local-only at this hop. |
| Subsystem status change on a network-linked subsystem (+0xA4 flag, client side) | **0x008000DD** | TGEvent (factory 0x101) | `FUN_00562560` second emit + `FUN_00562630` second emit | YES — host receives 0x008000DD via MultiplayerGame's `_SubsystemStat_` slot (subscribed in MultiplayerGame_Ctor) and relays as opcode 0x0A SubsysStatus via the generic event forwarder (FUN_0069FDA0) when host receives this event back. **Round trip is C→host→other clients**, not host-originated. |
| Object HP crossed death threshold (different from EXPLODING) | **0x0080004F** | Composite event (factory at PTR_FUN_008887AC, size 0x38) | `FUN_00592C00` (immediate-MOV at 0x00592CD0). Gated `param_1+0x53 < DAT_008e5c18` AND `param_1+0x54 == 0`. Sets `+0x54 = 1` to prevent re-fire. | NO. Local-only. Used by damage-display + replay-tracker. Not subscribed for relay. |
| Object physical collision detected | **0x00800050 ET_OBJECT_COLLISION** | Custom event (factory FUN_00586D00, size 0x44) | `FUN_00594840` (immediate-MOV at 0x00594F90). Posted only when collision sweep produces hit. | NO. Local-only at this layer. Host relays collision via opcode **0x15 CollisionEffect** via a separate Python pipeline (CollisionEffectHandler @ 0x006A2470 is a RECEIVE handler). |
| Ship hull HP reached zero | **0x0080004E ET_OBJECT_EXPLODING** | TGEvent (factory 0x101, size 0x30, allocator FUN_0043F8B0) | `ShipDeathHandler @ 0x005AFEA0` (immediate-MOV at 0x005AFF39). Gated `ship+0x14c >= DAT_008e5c18 || ship+0x150 != 0` early-out. | **YES — opcode 0x06 PythonEvent to NoMe** via MultiplayerGame_ObjectExplodingHandler (FUN_006A1240). Reliable. |
| Repair-list add (client side only) | **0x008000DF g_dwTgEvent_AddToRepairList** | TGEvent (factory 0x101, size 0x28) | `AddToRepairList_MP @ FUN_00565900` (gated `DAT_0097fa89 != 0` = CLIENT-side post AND multiplayer). | C→host: opcode 0x06 PythonEvent. Host receives, **relays via HostEventHandler (FUN_006A1150) as opcode 0x06 to NoMe group**. |
| Subsystem fully repaired (condition >= max) | **0x00800074 REPAIR_COMPLETED** | TGObjPtrEvent (factory 0x010C) | `RepairSubsystem::Update FUN_005652A0` (immediate-MOV at 0x00565447). Gated `(curCondition / maxCondition) >= 1.0`. | YES — host-side post → HostEventHandler (FUN_006A1150) → **opcode 0x06 PythonEvent to NoMe**. Reliable. |
| Subsystem destroyed mid-repair (curCondition <= 0) | **0x00800075 REPAIR_CANNOT_BE_COMPLETED** | TGObjPtrEvent | `RepairSubsystem::Update FUN_005652A0` (immediate-MOV at 0x005653A4 AND 0x005654E0; two emit sites — one per branch). Gated `curCondition <= 0`. | YES — host-side post → HostEventHandler → **opcode 0x06 PythonEvent to NoMe**. Reliable. |
| Subsystem damage drop from rebuilt state (re-enabled) | **0x00800070 SUBSYSTEM_REBUILT** | TGEvent | `FUN_0056BDE0` (immediate-MOV at 0x0056BFBA). Scheduled via FUN_0044C2D0 (timer). | NO. Local-only. Timer-driven shield/subsystem state poll. |
| Periodic subsystem state poll | **0x80006D / 0x80006E / 0x80006F / 0x800071** | TGEvent | `FUN_0056BDE0` — scheduled tick events (NOT immediate, NOT instantaneous) | NO. Local-only. Driven by FUN_0056B960 power-budget timing. |
| Subsystem reaches operational threshold | **0x00800072** | TGEvent (factory FUN_004A0EA0) | `FUN_0056BC60` (immediate-MOV at addr in fn body) | NO. Local-only. |
| Subsystem drops below operational threshold | **0x00800073** | TGEvent | `FUN_0056BC60` | NO. Local-only. |

### Damage path notes

- `ProcessDamage` (FUN_00593E50) itself posts NO events. Damage application happens by mutating subsystem damage bitmaps in the voxel grid (`FUN_004B4B40`); events fire only when a damaged subsystem's `SetCondition` is called by the per-subsystem damage actuator (`FUN_004B1B90 → FUN_004C2F80 → ShipSubsystem_SetCondition`).
- `FUN_00593F30` (deferred damage notification scheduler) schedules `LAB_005927E0` (a function-less callback target inside the 0x00592680 dispatcher) gated on `DAT_008e5c1e != 0 && DAT_0097fa89 == 0` (host-only). This deferred callback at `FUN_00592680` walks the per-handler queue and calls `FUN_00592580` per handler, which finds the highest-damage volume and applies it via `FUN_004B1B90 → FUN_004C2F80`. SetCondition only fires inside this chain.
- The "damage gate" 1.0f check in `ProcessDamage` is in `FUN_00593F30`'s scheduler conditions, not in ProcessDamage itself. ProcessDamage applies damage unconditionally; the deferred-callback gates the SetCondition emission.
- `FUN_00591EE0` (called from FUN_00592580 for "over-damaged" volumes) spawns debris particles (rand-based ejection); does NOT post events.

### Subscriptions confirmed via `FUN_006DB380` registration sweep (MultiplayerGame_Ctor @ 0x0069E590):

Host-only (gated `DAT_0097fa8a != 0` && IS_MULTIPLAYER), routed via MultiplayerGame's vtable HostEventHandler slot (effectively FUN_006A1150) — all emit opcode **0x06 PythonEvent NoMe**:
- 0x008000DF AddToRepairList
- 0x00800074 REPAIR_COMPLETED  
- 0x00800075 REPAIR_CANNOT_BE_COMPLETED

Always-on subscriptions (different vtable slot per event, different opcode emit):
- 0x0080004E OBJECT_EXPLODING → ObjectExplodingHandler (FUN_006A1240) → opcode 0x06 NoMe
- 0x008000F1 NewPlayerInGame → NewPlayerInGameHandler (FUN_006A1E70) → opcode 0x2A
- 0x008000D8 StartFiring → StartFiringHandler → opcode 0x07
- 0x008000DA StopFiring → opcode 0x08
- 0x008000DC StopFiringAtTarget → opcode 0x09
- 0x008000DD SubsystemStatusToggle → SubsysStatusHandler → opcode 0x0A
- 0x00800076 RepairListPriority → opcode 0x11
- 0x008000E0 SetPhaserLevel → opcode 0x12
- 0x008000E2 StartCloaking → opcode 0x0E
- 0x008000E4 StopCloaking → opcode 0x0F
- 0x008000EC StartWarp → opcode 0x10
- 0x008000FE TorpedoTypeChange → opcode 0x1B
- 0x00800058 ChangedTarget (CLIENT-only)

---

## Section 2 — Beam Fire Path Catalog

| Trigger | Event ID | Event class | Where posted | Wire-relayed? |
|---|---|---|---|---|
| Local beam impact on target (server-side damage) | None directly | n/a — calls `FUN_006F8AB0` (Python callback for visual effect) with strings "Effects" / "PhaserHullHit" / "TorpedoHullHit" / "TorpedoShieldHit" | `WeaponHitHandler @ FUN_005AF010` | NO wire packet from C++ event. Visual effect goes through embedded Python pipeline. Damage application via `FUN_005AF420 → FUN_00594020 (DoDamage)`. |
| Receive 0x1A from network (FUN_0069FBB0) | None | n/a — direct deserialize + local apply via `FUN_005762B0` | RECEIVE handler at MpgameHandleMessage dispatcher | n/a — receive side. Host forwards the TGMessage to "Forward" group ONLY when received from a NON-self peer in MP. |
| Beam start fire (player input) | n/a | n/a | `FUN_00575480 BeamFireSender` is called from BARE-CODE callers at 0x00575463 and 0x00576914 (no function entry; SP firing path) | YES — `FUN_00575480` emits **opcode 0x1A BeamFire** to NoMe in MP, to host in SP. Reliable. |

### Beam fire notes

- The HOST does NOT autonomously emit BeamFire from simulation. BeamFire is **player-input originated** (via FUN_00575480). When a client fires a beam, it sends 0x1A. The host receives via FUN_0069FBB0, relays to the "Forward" group (everyone except sender), then locally applies via FUN_005762B0.
- The host's own beam fires (if host is a player) ALSO call FUN_00575480 to broadcast to other peers.
- No wire-bound "beam hit" or "target damaged by beam" event. Damage results show up only via opcode 0x1C StateUpdate (subsystem health round-robin).
- WeaponSystem::UpdateWeapons (0x00584930) → TryFireWeapon (0x00584E40) on the host computes auto-fire targeting but does NOT emit a wire BeamFire — only sets ship subsystem state. (Subsystem state then gets serialized via StateUpdate.)

---

## Section 3 — Explosion / Death Path Catalog

| Trigger | Event ID | Event class | Where posted | Wire-relayed? |
|---|---|---|---|---|
| Ship hull HP reaches 0 | **0x0080004E ET_OBJECT_EXPLODING** | TGEvent (factory 0x101, size 0x30, allocator FUN_0043F8B0) | `ShipDeathHandler @ 0x005AFEA0` (immediate-MOV at 0x005AFF39). +0x2C = hullHP value at death, +0x28 = killer ID. | YES — opcode 0x06 PythonEvent to NoMe via MultiplayerGame_ObjectExplodingHandler (FUN_006A1240). |
| Explosion damage volume applied locally (e.g. ship explodes, splash damage) | (no event from this layer) | n/a — direct DamageVolume construction (FUN_004BBDE0) → ProcessDamage (FUN_00593E50) | Explosion_Net handler @ 0x006A0080 (RECEIVE-side, decodes opcode 0x29). | n/a — receive side. The HOST originates explosion DamageVolumes via DamageableObject_GenerateExplosions (in FUN_00595890 deserializer path during ObjCreate, OR computed locally during ship destruction). |
| New player joins mid-fight (or RequestObj) — replay pending explosions | n/a — direct serialize-to-wire | n/a | `DamageableObject__SendExplosions_0x29 @ FUN_00595C60` | YES — opcode 0x29 Explosion **per attached explosion**. Sent to the joining peer's session. UNRELIABLE (TGWinsockNetwork_SendTGMessage flag=0). |
| Subsystem destroyed during repair | 0x00800075 (covered above) | TGObjPtrEvent | RepairSubsystem::Update | YES — opcode 0x06 NoMe via HostEventHandler. |

### Explosion / death notes

- **Opcode 0x29 Explosion is ONLY sent during catch-up replay**, never as per-tick combat damage. The TWO callers of FUN_00595C60 are:
  1. `MultiplayerGame__RequestObjHandler @ 0x006A02A0` — sends all attached explosions to a peer requesting object state.
  2. `NewPlayerInGameHandler @ 0x006A1E70` — sends all attached explosions to a newly joined peer.
- Wire format for 0x29: `[0x29] [u32 originatorObjectID via FUN_006CF930] [CV4 position] [CF16 radius] [CF16 damageRate]`. 
- DamageableObject's explosion list is at object+0x13C (linked list, count at +0x140 per WriteState). Each explosion node has pos at +0x08, radius at +0x14, damage at +0x1C.
- Per-tick damage from explosions runs LOCALLY on each client because the explosion volumes were created by SHIP STATE serialization (StateUpdate opcode 0x1C) or by ObjCreate (opcode 0x02/0x03), which then ticks the explosion locally per simulation frame.
- **ObjectExplodingHandler dual-fire (per leaf #14):** The handler IS subscribed to ET_OBJECT_EXPLODING once. The dual-fire pattern means it (a) locally writes ship+0x14c hullHP and loads destruction visuals via FUN_005AC250 (SP branch), OR (b) serializes to opcode 0x06 NoMe (MP branch). Same handler, two mutually exclusive branches.
- ShipDeathHandler (0x005AFEA0) computes the killer ID via a series of `vtable+8` IsA checks: 0x8009 (Ship), 0x802A (Torpedo), 0x8008 (Weapon). For Torpedo, walks back to torpedo's parent ship.

---

## Section 4 — Repair Completion Verdict (DEFINITIVE)

**REPAIR_COMPLETED (0x00800074) and REPAIR_CANNOT_BE_COMPLETED (0x00800075) DO go on the wire as opcode 0x06 PythonEvent NoMe.**

Subscription proof: `MultiplayerGame_Ctor @ 0x0069E590` registers both event IDs to MultiplayerGame's HostEventHandler vtable slot via `FUN_006DB380(eventID, param_1, "MultiplayerGame::HostEventHandler", ...)` — confirmed at decompile lines:
```
FUN_006db380(&DAT_00800074, param_1, s_MultiplayerGame____HostEventHand_0095a158, 1, 1, DAT_0095adf8);
FUN_006db380(&DAT_00800075, param_1, s_MultiplayerGame____HostEventHand_0095a158, 1, 1, DAT_0095adf8);
```
This block is gated `DAT_0097fa8a != '\0'` (IS_MULTIPLAYER).

Emit proof:
- `RepairSubsystem::Update @ 0x005652A0` posts 0x00800074 at `0x00565447` (success branch) when `currentCondition/maxCondition >= 1.0f`.
- Same function posts 0x00800075 at `0x005653A4` and `0x005654E0` (two failure branches: in-queue and post-queue scan, respectively) when `currentCondition <= 0.0f`.

Wire-emit chain: `RepairSubsystem::Update PostEvent(TGObjPtrEvent)` → TGEventManager dispatches to MultiplayerGame singleton via vtable → HostEventHandler virtual slot resolved to `FUN_006A1150` → serialize event via `vtable[0x34]` into TGBufferStream prefixed with byte 0x06 → wrap in TGMessage (sizeof 0x40), set reliable flag → `TGWinsockNetwork_SendTGMessageToGroup(this, &DAT_008e5528 "NoMe", pMessage)`.

**Wire byte count per packet** (worst case, REPAIR_COMPLETED TGObjPtrEvent):
- `[0x06]` opcode (1)
- TGObjPtrEvent Serialize via vtable[0x34] writes:
  - TGEvent header (factory ID 0x010C as varint, 4-byte source object pointer ID, 4-byte event-type ID per leaf #13)
  - TGObjPtrEvent extension: `+0x20 nObj_ptr` (4 bytes)

So payload = ~16 bytes; wire frame total ~17 bytes plus TGMessage header.

**Status:** Earlier memory hypothesis ("REPAIR_COMPLETED never wire-emitted, OpenBC can omit") is **WRONG**. They ARE emitted on the wire. OpenBC's parity requirement for opcode 0x06 includes implementing host-side repair simulation that emits these.

---

## Section 5 — OpenBC Implementation Checklist

For each over-relayed opcode, the events OpenBC's server-side simulation must emit before the over-relay can be safely removed:

### 0x06 PythonEvent — REMOVABLE WHEN OpenBC EMITS:

#### From OBJECT_EXPLODING (ET_0x0080004E):
- [ ] **Server-side ship-hull-HP tracker.** Per-ship hullHP float (ship+0x14C in stock). Decrement on weapon hit / explosion damage. Sentinel `FLT_MAX` undamaged.
- [ ] **Death detection at hullHP < threshold** (stock: `DAT_008e5c18 = 0.0f`, but check). On crossing, emit ObjectExploding event with killer ID resolved by IsA chain:
  - Torpedo (0x802A) → torpedo owner ship ID (`torpedoObj+0x40 = parentShip`, ship's `+0x4 = objectID`)
  - Ship/Weapon (0x8008/0x8009) → direct sender ID
  - Else: 0 (no killer)
- [ ] **De-dup on +0x150 flag** — once ship is exploding, don't re-emit (stock sets `ship+0x150 = ?` after first death event).
- [ ] **Wire-emit opcode 0x06** with TGEvent factory 0x101, payload `[event_type=0x80004E][source_ptr_id][killer_id][hullHP_at_death]`. Reliable. Target: NoMe.

#### From REPAIR_COMPLETED (ET_0x00800074):
- [ ] **Server-side repair queue tracker.** Per-ship repair list (subsystem reference + accumulated progress).
- [ ] **Per-tick repair progress accumulator**: `progress += repairRate * deltaTime`.
- [ ] **Completion detection**: when `currentCondition/maxCondition >= 1.0f`, emit REPAIR_COMPLETED.
- [ ] **Wire-emit opcode 0x06** with TGObjPtrEvent factory 0x010C, payload `[event_type=0x800074][ship_ptr_id][subsystem_ptr_id]`. Reliable. Target: NoMe.

#### From REPAIR_CANNOT_BE_COMPLETED (ET_0x00800075):
- [ ] **Failure detection during repair**: if subsystem's `currentCondition <= 0.0f` while in repair queue, emit REPAIR_CANNOT_BE_COMPLETED.
- [ ] Same wire format as REPAIR_COMPLETED but event_type=0x800075. Reliable. NoMe.

#### From AddToRepairList (ET_0x008000DF):
- [ ] **Server-side intake of client repair-list-add requests** (received via opcode 0x06 from client).
- [ ] **Validation**: subsystem belongs to client's ship, subsystem damaged enough to merit repair, repair queue has capacity.
- [ ] **Re-emit opcode 0x06** to other clients (NoMe). Reliable.
- [ ] Note: client EMITS this when its own player adds a subsystem to repair list (FUN_00565900 host-only side); host RELAYS to peers.

### 0x1A BeamFire — RELAY-ONLY (NO server-originated emit needed)

Stock host does NOT originate BeamFire packets. Beam fire is exclusively client-input-originated. The host's role is purely:
1. RECEIVE opcode 0x1A from a client (via FUN_0069FBB0).
2. RELAY to "Forward" group (everyone except sender).
3. LOCALLY apply beam effect via FUN_005762B0.

**OpenBC parity: keep the relay.** Just ensure:
- [ ] OpenBC's server-side beam application produces the correct subsystem damage (which feeds StateUpdate 0x1C subsystem health). 
- [ ] OpenBC's server validates the beam fire (range, line-of-sight, can-fire gate) before relaying — same as stock.
- [ ] Visual effects (the "PhaserHullHit"/"TorpedoHullHit" Python callbacks) run on CLIENT, not server. Server-side these are no-ops; client-side they spawn particles. OpenBC clients still need the Python callback to fire — that's downstream of the 0x1A relay.

### 0x29 Explosion — REMOVABLE WHEN OpenBC EMITS:

Stock host emits 0x29 **only during catch-up replay**, never per-tick:

#### From DamageableObject__SendExplosions_0x29 (FUN_00595C60):
- [ ] **Per-DamageableObject explosion list tracker.** Server tracks attached explosions (position, radius, damageRate, lifetime) per object.
- [ ] **Lifetime accumulator**: explosions tick down each frame. Expired explosions removed from list.
- [ ] **On new player join (NewPlayerInGame handshake)** OR **on RequestObj reply**: enumerate all attached explosions on every object the joining peer can see, send opcode 0x29 per explosion targeted at that specific peer's session.
- [ ] **Wire format**: `[0x29] [u32 originatorObjectID] [CV4 position] [CF16 radius] [CF16 damageRate]`.
- [ ] Use `TGWinsockNetwork_SendTGMessage(peerSession, msg, 0)` — UNRELIABLE, direct send (NOT to a group).

**OpenBC parity: remove the over-relay**, replace with the catch-up-replay-only emit on new-player handshake. The per-tick explosion damage is already replicated via opcode 0x1C StateUpdate (subsystem health round-robin) and opcode 0x02/0x03 ObjCreate (initial damageable object state).

### Server-side state OpenBC must maintain (cross-opcode):

- [ ] **Per-ship hullHP** (float, initial FLT_MAX). Damage via weapon-hit, collision, explosion-volume application reduces it. Death detection at threshold.
- [ ] **Per-ship subsystem array** with per-subsystem `currentCondition`, `maxCondition`, `damageBitmap` (voxel grid), `repairQueueRef`. Wire-replicated via StateUpdate 0x1C.
- [ ] **Per-ship attached-explosions list** (linked list, head at +0x13C in stock). For catch-up replay.
- [ ] **Per-ship death state** (+0x150 in stock) to de-dup OBJECT_EXPLODING events.
- [ ] **Repair queue state** per ship: ordered list of (subsystem, accumulatedProgress, priority).
- [ ] **NoMe / Forward group membership tracker** — already exists in OpenBC routing; reuse.

---

## Section 6 — Open Questions

1. **What does `FUN_00591EE0` do for the simulation?** It's the "debris ejection" function. Emits no events but spawns particle effects (random direction velocity ejection with rand-based magnitude). Confirmed local-only. Does OpenBC need a server-side particle emitter? Likely NO — visuals are client-side only.

2. **Does the host ever post ET_OBJECT_COLLISION (0x800050) on the wire?** Checked — the local emit at `FUN_00594840` (collision sweep) is local-only. CollisionEffect opcode 0x15 is a SEPARATE wire packet, emitted via `Ship__HostCollisionEffectHandler @ 0x005AFAD0` (per cascade A docs) which is a HOST-side relay path for client collision events. The 0x800050 event is purely simulation-local.

3. **The "host-only damage notification scheduler" (FUN_00593F30) gate `DAT_008e5c1e != 0`** — what is this global? Likely a multiplayer enable flag separate from `DAT_0097fa8a`. Worth confirming for OpenBC's tick scheduler.

4. **`g_dwTgEvent_SubsystemStatusToggle` (0x80006C) double-emit in FUN_00562560/630** — the second emit posts event 0x008000DD when `DAT_0097fa89 != 0` (client-only) AND `subsystem+0xA4 != 0` (subsystem-linked). This is the CLIENT-→-host SubsysStatus path. Host then relays the resulting 0x008000DD via opcode 0x0A. Worth one more pass to confirm wire emitter for opcode 0x0A.

5. **REPAIR_COMPLETED/CANNOT_BE_COMPLETED gating** — `FUN_005652A0` runs every tick on every ship, but the host-only post is gated `(DAT_0097fa89 == 0) || (DAT_0097fa89 == 1 && DAT_0097fa8a != 0)`. That's "host OR (client + MP)" — meaning **clients also run repair logic and emit these events locally**. The HOST's emit gets wire-broadcast; client's locally-emitted events should be CONSUMED by client UI but NOT looped back. Important for OpenBC: clients should NOT relay their own repair events back to server.

6. **Where does the dispatcher entry for opcode 0x06 in MpgameHandleMessage parse the event-type byte?** PythonEvent handler is `FUN_0069F880`. Worth confirming that wire-side 0x06 byte stream layout matches what HostEventHandler/ObjectExplodingHandler WRITES via vtable[0x34] Serialize. Bytewise round-trip needs validation.

7. **`FUN_00595890` (Explosion deserializer caller) has no listed callers** — but it's called from ship-replication-state path. Probably called via vtable from `Ship_ReadStateUpdate` (per memory). Worth confirming for OpenBC's state-update path: does opcode 0x1C StateUpdate carry explosion data? Per memo this is in the dirty-bit payload formats — worth re-checking.

---

## Cross-references

- Anchored functions: `0x00593E50` (ProcessDamage), `0x00594020` (DoDamage), `0x005AF010` (WeaponHitHandler), `0x005AF420` (ApplyWeaponDamage), `0x005AFEA0` (ShipDeathHandler), `0x0056C470` (ShipSubsystem_SetCondition), `0x005652A0` (RepairSubsystem::Update), `0x00565900` (AddToRepairList_MP), `0x00595C60` (DamageableObject__SendExplosions_0x29), `0x006A0080` (Explosion_Net), `0x006A1150` (HostEventHandler), `0x006A1240` (ObjectExplodingHandler), `0x006A1E70` (NewPlayerInGameHandler), `0x006A02A0` (RequestObjHandler), `0x0069E590` (MultiplayerGame_Ctor), `0x0069EFE0` (handler-name registry), `0x0069FBB0` (BeamFire receive), `0x00575480` (BeamFire wire sender), `0x00584930` (WeaponSystem::UpdateWeapons), `0x00584E40` (TryFireWeapon).
- Event IDs anchored: 0x0080004E, 0x0080004F, 0x00800050, 0x0080006B, 0x0080006C, 0x0080006D, 0x0080006E, 0x0080006F, 0x00800070, 0x00800071, 0x00800072, 0x00800073, 0x00800074, 0x00800075, 0x00800076, 0x008000D8, 0x008000DA, 0x008000DC, 0x008000DD, 0x008000DF, 0x008000E0, 0x008000E2, 0x008000E4, 0x008000EC, 0x008000F1, 0x008000FE.
- Group strings: `DAT_008E5528` "NoMe" (everyone except self), `DAT_008D94A0` "Forward" (same membership, separate dispatch).
- Globals: `DAT_0097FA78` (TGWinsockNetwork), `DAT_0097FA89` (IsClient), `DAT_0097FA8A` (IsMultiplayer), `DAT_008E5C18` (zero-HP threshold), `DAT_008E5C1E` (damage-notification gate).
- Companion memos: [[stateupdate-validation-20260528]], [[ship-death-lifecycle-validation-20260528]], [[ack-outbox-deadlock-validation-20260528]], [[networking-mid-tgmessage-cleanroom-validation-20260528]], [[gameplay-foundation-damage-system-validation-20260528]], [[pythonevent-wire-format-validation-20260528]], [[tgobjptrevent-validation-20260528]].

## Confidence assessment

- **HIGH** (byte-anchored): ShipSubsystem_SetCondition emits 0x80006B; ShipDeathHandler emits 0x80004E; RepairSubsystem::Update emits 0x800074/0x800075; HostEventHandler subscribes to 0x800DF/0x800074/0x800075 and emits opcode 0x06 to NoMe; ObjectExplodingHandler emits opcode 0x06 NoMe for OBJECT_EXPLODING; DamageableObject__SendExplosions_0x29 emits opcode 0x29 only from RequestObj + NewPlayerInGame.
- **MEDIUM** (vtable-resolved): The "HostEventHandler" subscription routes via MultiplayerGame vtable to FUN_006A1150 — confirmed via debug-name registration string match. Direct vtable-slot index not confirmed but immediate code review of MultiplayerGame ctor's vtable installation at 0x0088B480 + slot index could nail this.
- **LOW** (inferred): Event IDs 0x80006D/0x80006E/0x80006F/0x800070/0x800071/0x800072/0x800073 short names (SUBSYSTEM_*); only emit sites confirmed.
