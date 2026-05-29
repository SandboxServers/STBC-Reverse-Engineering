> [docs](../README.md) / [gameplay](README.md) / sensor-subsystem.md

---
title: SensorSubsystem (ship+0x2C8) — RE Analysis
type: reference + explanation
audience: re-engineer
validated: 2026-05-28
methodology: FUNCTION_DOC_WORKFLOW_V5
binary:
  name: stbc.exe
  size: 6182400
  base: 0x00400000
status: verified
evidence:
  - claim: "SensorSubsystem instance lives at ship+0x2C8 (slot 4 of the ship subsystem named-slot table); set by Ship__SetupProperties case 0x8139 (CT_SENSOR_PROPERTY)"
    address: 0x005B3FB0
    function: Ship__SetupProperties
    completeness: 28.2
    effective: 41.4
    confidence: high
    note: "Case 0x8139 allocates 0xCC bytes, calls SensorSubsystem_Ctor, writes pointer into param_1+0x2C8. Cross-anchor: wire-format-spec.md Named Slot Layout (foundation #1) + subsystem-integrity-hash.md slot 4."
  - claim: "Class identity 0x8023 via vtable 0x00892EAC; vtable owns 6 strings 'SensorSubsystem::Handle*' at 0x008E5130..0x008E51EC"
    address: 0x00892EAC
    function: null
    confidence: high
    note: "GetTypeID at 0x00566D70 byte-confirmed: `B8 23 80 00 00 C3` (MOV EAX, 0x8023 ; RET). Six handler strings located via search_strings."
  - claim: "Instance alloc size 0xCC bytes (204)"
    address: 0x005B428B
    function: Ship__SetupProperties
    confidence: high
    note: "`PUSH 0xCC` immediately before FUN_0040F030 (allocator call) for case 0x8139."
  - claim: "IsA chain: 0x8023 -> 0x801C (PoweredSubsystem) -> 0x801B (ShipSubsystem) -> 0x102 (DamageableObject)"
    address: 0x00566D80
    function: SensorSubsystem__IsA
    confidence: high
    note: "Disasm 0x00566D80..0x00566D9F enumerates the type-ID chain with CMP/JE cascade."
  - claim: "SensorSubsystem_Ctor at 0x00566D10 sets vtable 0x00892EAC + powerMode=2 + 8 field zero-inits; calls PoweredSubsystem ctor parent"
    address: 0x00566D10
    function: SensorSubsystem_Ctor
    completeness: 12.5
    effective: 28.6
    confidence: high
    note: "Block 2 B Ghidra plate corrected this pass — function was historically misnamed `CloakingSubsystem_Ctor` from an earlier session rename cascade. Real CloakingSubsystem ctor is at 0x0055E2B0 (sets vtable 0x00892C04, has SEH frame + FUN_0055F930 state-machine init). Body: parent ctor call -> vtable assign -> param_1[0x30]=2 -> zero-fills."
  - claim: "GetSensorRange formula: range = property[+0x4C] * instance[+0x98] * instance[+0x34] = BaseSensorRange * PowerPct * HpPct"
    address: 0x00567190
    function: SensorSubsystem__GetSensorRange
    confidence: high
    note: "Byte-level disasm: FLD [+0x4C] / FMUL [+0x98] / FMUL [+0x34]. Returns `_DAT_00888B54` (likely 0.0) if power-off (this+0x9C == 0)."
  - claim: "IsObjectVisible runs cloak detection + faction-group match + distance-walk over the per-instance visible-object list"
    address: 0x005671D0
    function: SensorSubsystem__IsObjectVisible
    confidence: high
    note: "Reads target[+0x2DC]+0xAC == 1 -> fully cloaked -> invisible regardless of range. Group match via this+0x40 vs target+0x20. Uses 0x800E retry budget loop (FUN_0040AFE0). Distance walk reads list at this+0xB0..+0xBC."
  - claim: "SetProperty at 0x00567080 calls ShipSubsystem::SetProperty(0x0056BDC0) then caches property[+0x50] into instance[+0xC8]"
    address: 0x00567080
    function: SensorSubsystem__SetProperty
    confidence: high
    note: "Vtable slot +0x60. property+0x50 is likely MaxProbes (per SWIG fn SensorProperty_GetMaxProbes at 0x00916098). property+0x4C (BaseSensorRange) is NOT cached on the instance — read live every call to GetSensorRange."
  - claim: "Six event handlers registered by FUN_00566F50 via FUN_006DA130/160: HandlePeriodicScan, HandleShipDecloaked, HandleShipIdentified, HandleExitSet, HandleEnterSet, HandleSetPlayer"
    address: 0x00566F50
    function: SensorSubsystem__RegisterStaticHandlers
    confidence: high
    note: "Handler string anchors: 0x008E5130 (PeriodicScan), 0x008E515C (ShipDecloaked), 0x008E5184 (ShipIdentified), 0x008E51AC (ExitSet), 0x008E51CC (EnterSet), 0x008E51EC (SetPlayer)."
  - claim: "HandlePeriodicScan reschedules next periodic scan via (gameTime + DAT_008E50F4); event_type = 0x80008B"
    address: 0x005680C0
    function: SensorSubsystem__HandlePeriodicScan
    confidence: high
    note: "Reads current gameTime from 0x009A09D0+0x90 and adds DAT_008E50F4 constant. Event ID 0x80008B = ET_SENSORS_PERIODIC_SCAN. Allocates two events via TGAlloc(0x28) + TGAlloc(0x20)."
  - claim: "Instance field +0xAC = visibleObjectCount (uint32); +0xB0..+0xB4 = visibleObjectList head/tail ptrs; +0xB8 = visibleObjectFreeList head ptr"
    address: 0x005671D0
    function: SensorSubsystem__IsObjectVisible
    confidence: medium
    note: "Derived from IsObjectVisible's distance-walk over this+0xB0..+0xBC. Not byte-confirmed against ctor zero-init (the +0xAC..+0xC8 range is populated by SetProperty + HandleShipIdentified, not by the ctor)."
  - claim: "Instance field +0xC0 = powerMode = 2 (set by ctor); +0xC8 = cached property+0x50 (likely MaxProbes, set by SetProperty)"
    address: 0x00566D10
    function: SensorSubsystem_Ctor
    confidence: high
    note: "param_1[0x30] = 2 is the powerMode=2 ctor init. +0xC8 cache is byte-confirmed in SetProperty at 0x0056709E (MOV [ESI+0xC8], EAX after reading [EAX+0x50])."
  - claim: "Wire format via PoweredSubsystem::WriteState (slot +0x70 at vtable 0x00892F1C -> 0x00562960): 1 byte condition + 1 bit hasPowerData + (optional 1 byte powerPctWanted if remote ship)"
    address: 0x00562960
    function: PoweredSubsystem__WriteState
    confidence: high
    note: "condition_byte = ftol((this+0x30 / this+0x34) * 255.0). hasPowerData=0 for own ship, 1 for remote. If 1, emit ftol(this+0x90 * 100.0) as 1 byte."
  - claim: "Sensor visibility decisions are CLIENT-LOCAL — server does not replicate sensor scans; each client independently runs IsObjectVisible and posts ET_SENSORS_SHIP_IDENTIFIED locally"
    address: null
    function: null
    confidence: high
    note: "Per stock-trace and event-system architecture: PeriodicScan reschedule is local-only (uses local gameTime); ET_SENSORS_SHIP_IDENTIFIED is fired client-locally when target enters local sensor range and is NOT replicated."
  - claim: "BaseSensorRange (property+0x4C) is the value hashed by ComputeSubsystemIntegrityHash slot 4 — dead in MP per integrity-hash leaf"
    address: 0x005B5EB0
    function: ComputeSubsystemIntegrityHash
    confidence: high
    note: "Slot 4 (container +0x4C / ship+0x2C8) reads `HashFoldFloat(prop[+0x4C], &acc)` per subsystem-integrity-hash.md C1. Hash is dead code in MP — mod-induced BaseSensorRange mismatch is behaviorally harmless."
  - claim: "DAT_008E50F4 (sensor rescan interval constant) is read by HandlePeriodicScan; exact byte value not read this pass"
    address: 0x008E50F4
    function: null
    confidence: low
    note: "Open question (OQ-2). Likely 0.5f or 1.0f game-time. Symbol used as `FADD ST, dword ptr [0x008E50F4]` after loading current gameTime."
  - claim: "DAT_00888B5C = 4.0f used as fallback constant in GetBaseSensorRange (0x005671C0) — likely dead, real per-ship range uses prop+0x4C via GetSensorRange"
    address: 0x008888B5C
    function: SensorSubsystem__GetBaseSensorRange
    confidence: low
    note: "Open question (OQ-3). GetBaseSensorRange returns const 4.0f unconditionally; no xref into the runtime range computation found."
companions:
  - docs/gameplay/hull-subsystem.md
  - docs/gameplay/power-system.md
  - docs/gameplay/cloaking-state-machine.md
  - docs/protocol/subsystem-integrity-hash.md
  - docs/protocol/stateupdate-subsystem-wire-format.md
  - docs/protocol/per-ship-subsystem-wire-format.md
  - docs/engine/rtti-class-catalog.md
supersedes: []
---

# SensorSubsystem (ship+0x2C8) — Reverse Engineering Analysis

> [!NOTE]
> **SensorSubsystem at ship+0x2C8** (class 0x8023) inherits PoweredSubsystem semantics. The sensor's BaseSensorRange comes from CT_SENSOR_PROPERTY+0x4C (NOT cached on instance — read live each call to GetSensorRange). Visibility computation (`IsObjectVisible`) is CLIENT-LOCAL — the server does not replicate sensor visibility decisions. Per leaf #19, the integrity hash for this slot uses prop+0x4C (BaseSensorRange) which is dead in MP. Mod-induced range mismatch is behaviorally harmless. The ctor at 0x00566D10 was wrongly renamed `CloakingSubsystem_Ctor` in an earlier session; **corrected this pass via Block 2 B Ghidra plate fix** (real CloakingSubsystem ctor is at 0x0055E2B0, sets vtable 0x00892C04, has SEH frame + state-machine init). See `.claude/agent-memory/game-archaeology-specialist/sensor-hull-subsystem-validation-20260528.md` for the binary-truth evidence packet.

---

## Overview

SensorSubsystem is the per-ship system that decides which OTHER ships and objects a player can see. It runs a periodic scan, computes effective sensor range as a product of base range and two multipliers (power and health), and maintains a list of currently-visible target objects. It also fires the events that drive HUD/AI awareness of newly-identified targets, cloaked-target loss, and proximity transitions.

It is fundamentally **client-local** in multiplayer — the server does NOT compute sensor visibility on behalf of clients. Each client runs its own SensorSubsystem against the same world state, and each client independently decides what is visible. This is why a cloaked enemy can be invisible to one player and visible to another at the same instant: the cloak-vs-power-vs-distance computation happens in each client's local SensorSubsystem.

---

## Class Identity

[v5-validated 2026-05-28]

| Attribute | Value | Evidence |
|---|---|---|
| Class name | `SensorSubsystem` | 6 vtable-owned strings `SensorSubsystem::Handle*` at 0x008E5130-0x008E51EC |
| Class ID | `0x8023` | GetTypeID at 0x00566D70 byte-confirmed: `B8 23 80 00 00 C3` |
| IsA chain | 0x8023 -> 0x801C (PoweredSubsystem) -> 0x801B (ShipSubsystem) -> 0x102 (DamageableObject) | IsA disasm 0x00566D80..0x00566D9F |
| vtable | `0x00892EAC` | Owns the 6 handler string references + GetTypeID/IsA/dtor slots |
| Property type | `0x8139` (CT_SENSOR_PROPERTY) | Ship__SetupProperties case 0x8139 |
| Instance alloc size | `0xCC` bytes (204) | `PUSH 0xCC` before allocator call at 0x005B428B |
| Ship slot | `ship+0x2C8` | Ship__SetupProperties writes the new instance pointer there |

### Ctor — historical misname corrected this pass

The instance constructor at **0x00566D10** was historically misnamed `CloakingSubsystem_Ctor` in the Ghidra DB by a session-level rename cascade. This pass corrected the Ghidra plate to `SensorSubsystem_Ctor`. Diagnostic shape of the function body:

- Calls PoweredSubsystem parent ctor
- Sets `*param_1 = 0x00892EAC` (vtable assign)
- Sets `param_1[0x30] = 2` (powerMode = 2 — sensor power-mode enum)
- Zero-fills 8 fields after the vtable slot
- **NO state machine, NO SEH frame** — distinguishes it from the real cloaking ctor

For reference, the real `CloakingSubsystem_Ctor` lives at **0x0055E2B0**: sets vtable `0x00892C04`, installs an SEH frame, calls `FUN_0055F930()` (cloak state-machine init), and sets `param_1[0x28] = 2`. The two ctors are structurally distinct once you read the bytes.

---

## Field Layout (instance, 0xCC bytes)

[v5-validated 2026-05-28]

SensorSubsystem inherits from PoweredSubsystem (which extends ShipSubsystem). Per-instance layout:

| Offset | Field | Source / Use |
|---|---|---|
| +0x00 | vtable ptr = 0x00892EAC | (ctor) |
| +0x04..+0x87 | Inherited ShipSubsystem base | childCount, parent ptr, condition, propertyPtr, watchers — see hull-subsystem.md for the base table |
| +0x88..+0x8C | property+0x40 / property+0x44 mirrors | (PoweredSubsystem watchers) |
| +0x90 | PowerPercentageWanted | float 0..1, init 1.0 (PoweredSubsystem) |
| +0x94 | isMaster | byte init 1 (PoweredSubsystem) |
| +0x98 | PowerPercentage | current actual power — float (PoweredSubsystem) |
| +0x9C | isPowered / isActive | bool — gates many checks |
| +0xA0..+0xA8 | PoweredSubsystem misc / ctor flag | |
| **+0xAC** | **visibleObjectCount** | uint32 (Sensor-specific) |
| **+0xB0** | **visibleObjectList head** | ptr (Sensor-specific) |
| **+0xB4** | **visibleObjectList tail** | ptr (Sensor-specific) |
| **+0xB8** | **visibleObjectFreeList head** | ptr (Sensor-specific) |
| +0xBC..+0xBF | reserved / scratch | |
| **+0xC0** | **powerMode** = 2 | byte/int — set by ctor (Sensor enum) |
| +0xC4 | tracker field | next-event tracker (set by HandlePeriodicScan from event+0x4) |
| **+0xC8** | **cached property+0x50** | float — likely `MaxProbes` (set by SetProperty) |
| +0xCC | end of instance | |

> **Note on +0xC8 cache.** The cached value at `instance+0xC8` is `property+0x50` (per SetProperty disasm at 0x0056709B: `MOV EAX, [EAX+0x50]`). The SWIG binding `SensorProperty_GetMaxProbes` at 0x00916098 maps to this property offset, so the cache is likely the MaxProbes scan budget. **BaseSensorRange (property+0x4C) is NOT cached on the instance** — it is read live every call to GetSensorRange.

The fields +0xAC..+0xB8 (visible-object list + count) are populated by `HandleShipIdentified` (0x00568080) and consumed by `IsObjectVisible` (0x005671D0). They are NOT zeroed by the ctor — the ctor only zeros the lower 8 slots after the vtable assign.

---

## Methods

[v5-validated 2026-05-28]

### `SensorSubsystem::GetSensorRange` @ 0x00567190

```
range = property[+0x4C] * instance[+0x98] * instance[+0x34]
      = BaseSensorRange * PowerPct * HpPct
```

Byte-level disasm: `FLD [EAX+0x4C] / FMUL [ESI+0x98] / FMUL [ESI+0x34]`. Returns `_DAT_00888B54` (likely 0.0) when `instance+0x9C == 0` (power-off / inactive).

- Power-damaged sensor -> reduced range (proportional to PowerPct).
- HP-damaged sensor -> reduced range (proportional to current/max health).
- Powered-off sensor -> range collapses to 0 (the fallback constant).

### `SensorSubsystem::GetBaseSensorRange` @ 0x005671C0

Returns the constant `_DAT_00888B5C` = 4.0f unconditionally. **Likely dead** — the runtime range computation reads `property+0x4C` directly via `GetSensorRange`. Either a default fallback used by an unfound caller, or vestigial code. See Open Question 3.

### `SensorSubsystem::IsObjectVisible` @ 0x005671D0

The visibility decision engine. Pseudocode of the full algorithm:

```c
bool IsObjectVisible(SensorSubsystem* this, Object* target) {
    // 1. Cloak gate
    CloakDevice* tgtCloak = target[+0x2DC];           // target's CloakDevice slot
    if (tgtCloak && tgtCloak[+0xAC] == 1) {
        return false;                                  // fully cloaked -> invisible
    }

    // 2. Faction / group gate
    Group* myGroup = this[+0x40];
    Group* tgtGroup = target[+0x20];
    if (myGroup != tgtGroup) {
        // hostile / unfriendly handling — go to retry-budget loop
        for (int budget = 0x800E; budget > 0; budget--) {
            int probe = FUN_0040AFE0(0x800E, &local_4); // probe-roll
            if (probe_hit_visibility_threshold) break;
        }
    }

    // 3. Distance walk over visible-object list
    for (Node* n = this[+0xB0]; n != NULL; n = n->next) {
        if (n->target == target) {
            return n->visible;
        }
    }

    // 4. Range gate
    return distance(this->ship, target) <= GetSensorRange();
}
```

Key behavioral details:

- The cloak gate at `target+0x2DC+0xAC == 1` reads the **CloakDevice fully-cloaked flag** on the target. This is the gate that makes cloaked ships invisible to the sensor.
- The faction/group match reads `this+0x40` against `target+0x20`. Same-group targets are auto-visible; cross-group targets must pass the probe-roll.
- The `0x800E` retry-budget loop calls `FUN_0040AFE0(0x800E, &local_4)` — likely a probabilistic scan-attempt counter.
- The distance walk reads the per-instance visible-object list at `this+0xB0..+0xBC`. List entries are populated by `HandleShipIdentified` when a target newly enters range.

### `SensorSubsystem::SetProperty` @ 0x00567080

Vtable slot `+0x60`. Calls `ShipSubsystem::SetProperty (0x0056BDC0)` to bind the CT_SENSOR_PROPERTY pointer at `instance+0x18`, then runs Sensor-specific casts and caches `property[+0x50]` -> `instance[+0xC8]`. This is the only "stash a property field on the instance" operation in the Sensor — BaseSensorRange (`property+0x4C`) is NOT cached.

---

## Event Handlers

[v5-validated 2026-05-28]

Six handlers registered by `FUN_00566F50` via `FUN_006DA130/160`. The registration walks 6 handler strings and binds each to its method address:

| Handler | Address | Event String Anchor | Behavior |
|---|---|---|---|
| `HandleSetPlayer` | 0x00567CD0 | 0x008E51EC | Global manager init; posts 0x80008B + 0x80005D via EventManagers 0x0097F838 + 0x0097F864 |
| `HandleEnterSet` | 0x00567F60 | 0x008E51CC | Registers ship in active-Sensor list (FUN_00567440 / FUN_00568AD0) |
| `HandleExitSet` | 0x00568040 | 0x008E51AC | Unregisters ship from active-Sensor list |
| `HandleShipIdentified` | 0x00568080 | 0x008E5184 | Adds identified target to visibility list at this+0xB0..+0xB8 |
| `HandleShipDecloaked` | 0x00568040 (alias path) | 0x008E515C | Re-visibility transition |
| `HandlePeriodicScan` | 0x005680C0 | 0x008E5130 | Recurring per-NPC scan tick |

Two event types are registered by a sibling function `FUN_00566FD0`:

- `0x80000E` (SET_PLAYER) — fires when the local player changes ships
- `0x80008B` (`ET_SENSORS_PERIODIC_SCAN`) — recurring per-tick scan timer

Additional Sensor event types referenced (registered elsewhere, listed for completeness):

| Event ID | Symbol | String Anchor | Use |
|---|---|---|---|
| `0x800086` | `ET_SENSORS_SHIP_NEAR_PROXIMITY` | 0x009104CC | Distance threshold transition |
| `0x800087` | `ET_SENSORS_SHIP_FAR_PROXIMITY` | 0x009104AC | Far distance transition |
| `0x800085` | `ET_SENSORS_SHIP_IDENTIFIED` | 0x009104EC | New target identified |
| `0x800088` | `ET_SENSORS_RANGE_CHANGED` | 0x00910508 | Effective range changed |

---

## Wire Format (StateUpdate flag 0x20)

[v5-validated 2026-05-28]

SensorSubsystem emits via **PoweredSubsystem::WriteState** (vtable slot `+0x70` = 0x00562960):

```
+0    1 byte    condition_byte = ftol((current_condition / max_condition) * 255.0)
                Sensor's own HP byte (full unless damaged in combat)
+1    1 bit     hasPowerData = (0 if isOwnShip else 1)
[if hasPowerData]
+1.x  1 byte    powerPctWanted = ftol(this[+0x90] * 100.0)   // 0..100
```

Per-tick payload sizes:

- **Own ship**: 1 byte (just the condition byte; `hasPowerData=0` and no power byte follows)
- **Remote ship**: 1 byte + 1 bit + 1 byte = effectively 2 bytes + 1 bit straddled into the bitstream

SensorSubsystem has NO children, so no child recursion happens at the end of `WriteState`.

The `BaseSensorRange` (property+0x4C) is NOT on the wire — it is property/config data, not runtime state. Both server and clients load the same value from CT_SENSOR_PROPERTY in the ship NIF via the ObjCreate path. What changes per-tick over the wire are the multipliers (HP%, Power%).

---

## Tick / Update — Event-Driven Scanning

[v5-validated 2026-05-28]

SensorSubsystem has **no dedicated per-frame Update**. Instead it uses a recurring event: `ET_SENSORS_PERIODIC_SCAN` (0x80008B) is scheduled with a delay, and the handler re-schedules itself.

Pseudocode of `HandlePeriodicScan` (0x005680C0):

```c
void HandlePeriodicScan(SensorSubsystem* this, TGEvent* ev) {
    // 1. Run the actual scan tick on the global Sensor singleton
    FUN_00568520(global_sensor_singleton_0x0098C000);

    // 2. Allocate a per-ship scan event (size 0x28) for downstream consumers
    void* shipScan = TGAlloc(0x28);
    FUN_006D5C00(shipScan, /* ship-specific scan args */);

    // 3. Allocate the next periodic scan event (size 0x20)
    TGEvent* nextEv = TGAlloc(0x20);
    nextEv->event_type = 0x80008B;                       // ET_SENSORS_PERIODIC_SCAN

    // 4. Compute next-fire time
    float currentGameTime = *((float*)(0x009A09D0 + 0x90));
    float nextFire = currentGameTime + DAT_008E50F4;     // rescan interval constant

    // 5. Update tracker fields
    this[+0xC4] = nextEv[+0x4];                          // next event tracker

    // 6. Enqueue into global timer queue + release the temporary
    FUN_006DC3F0(0x0097F898, nextEv);                    // EventManager AddTimedEvent
    FUN_006D90E0(shipScan);                              // release temporary event
}
```

The rescan interval constant at `DAT_008E50F4` was not byte-read this pass — see Open Question 2.

---

## Cloak Detection

[v5-validated 2026-05-28]

Cloak detection is the gate that prevents a cloaked enemy from appearing on the local player's sensors. Mechanism:

1. `IsObjectVisible` reads the target's CloakDevice slot at `target+0x2DC` (per foundation #1 — the canonical CloakDevice ship slot).
2. It tests `cloak+0xAC == 1` — the CloakDevice "fully cloaked" flag (set during the cloak state-machine's STEADY_CLOAKED state).
3. If the flag is set, `IsObjectVisible` returns false immediately, regardless of distance or sensor range.

This is the entire client-side enforcement of cloak invisibility. The server does not strip cloaked ships from StateUpdates — they continue to be replicated. Clients individually decide not to render / not to display them on HUD because their local SensorSubsystem says "invisible".

Cross-ref: [docs/gameplay/cloaking-state-machine.md](cloaking-state-machine.md) for the 4-state cloak transition and the `+0xAC` flag set/clear conditions.

---

## OpenBC Implications

Server-side OpenBC implementation notes:

- **Server does NOT need to compute sensor scans.** Visibility is decided client-side. Each client runs its own SensorSubsystem against the same replicated world state.
- **SensorSubsystem MUST appear in the ship+0x284 round-robin subsystem list.** The server's StateUpdate flag 0x20 round-robin will visit Sensor's slot and emit `PoweredSubsystem::WriteState` — 1 byte HP + 1 bit hasPowerData + (optional 1 byte powerPctWanted). Clients use the powerPctWanted byte to update their local PowerPct multiplier so their `GetSensorRange` computation produces the right effective range.
- **BaseSensorRange (property+0x4C) must match across all participants.** This is baked into CT_SENSOR_PROPERTY in the ship NIF — modded ships with different BaseSensorRange WILL desync sensor decisions across clients (one client sees the target, another doesn't). The integrity hash for this slot is dead in MP (per leaf #19), so the mismatch will NOT trigger a kick; it just produces silent gameplay divergence.
- **Periodic scan events (0x80008B) are client-local.** Server does NOT need to fire these on behalf of any client.
- **`ET_SENSORS_SHIP_IDENTIFIED` (0x800085) is client-local.** Server does NOT need to replicate this. Each client independently identifies targets that newly enter range.
- **Cloak detection is client-local.** Server sends StateUpdate normally; client `IsObjectVisible` reads `target+0x2DC+0xAC` and decides invisibility itself.

---

## Open Questions

- **OQ-1** — What syncs the global ship hull HP (`ship+0x14C`) to subsystem condition fields and ultimately into the StateUpdate condition byte? SensorSubsystem's `instance+0x34` (max condition) and `instance+0x30` (current condition) are consumed by `GetSensorRange` and `WriteState` — needs the watcher/mirror function from `ProcessDamage` or `ShipSubsystem::SetCondition` traced. (Same OQ as on `hull-subsystem.md`.)
- **OQ-2** — `DAT_008E50F4` rescan interval constant: 4 bytes at that address need a `read_memory` to confirm whether the period is 0.5f, 1.0f, or other. Used by `HandlePeriodicScan` to schedule the next ET_SENSORS_PERIODIC_SCAN event.
- **OQ-3** — `DAT_00888B5C = 4.0f` returned by `GetBaseSensorRange (0x005671C0)`: dead fallback, or actually called from somewhere we haven't found yet? Searching for xrefs into the function would resolve it. If dead, the constant should be documented in [docs/protocol/subsystem-integrity-hash.md](../protocol/subsystem-integrity-hash.md) clarifications.
- **OQ-4** — The `0x800E` retry-budget loop inside `IsObjectVisible` calls `FUN_0040AFE0(0x800E, &local_4)`. What does this probe-roll function actually do? Likely a probabilistic scan attempt against the cross-group visibility table. Decompile + xref walk would clarify.

---

## Related Documents

- [hull-subsystem.md](hull-subsystem.md) — Sibling subsystem (ship+0x2C4); the simplest ShipSubsystem on the wire.
- [power-system.md](power-system.md) — PoweredSubsystem parent class semantics; PowerPct multiplier feeds `GetSensorRange`.
- [cloaking-state-machine.md](cloaking-state-machine.md) — CloakDevice (ship+0x2DC); `+0xAC` fully-cloaked flag is the gate read by `IsObjectVisible`.
- [docs/protocol/subsystem-integrity-hash.md](../protocol/subsystem-integrity-hash.md) — Slot 4 hashes `property+0x4C` (BaseSensorRange); dead in MP.
- [docs/protocol/stateupdate-subsystem-wire-format.md](../protocol/stateupdate-subsystem-wire-format.md) — Round-robin subsystem encoding; SensorSubsystem participates here.
- [docs/protocol/per-ship-subsystem-wire-format.md](../protocol/per-ship-subsystem-wire-format.md) — Per-ship sensor properties across the 16 stock ships.
- [docs/engine/rtti-class-catalog.md](../engine/rtti-class-catalog.md) — Class IDs 0x8023 (SensorSubsystem) / 0x8139 (CT_SENSOR_PROPERTY).
