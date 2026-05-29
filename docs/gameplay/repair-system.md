> [docs](../README.md) / [gameplay](README.md) / repair-system.md

---
title: Repair System — Complete Reverse Engineering
type: reference + explanation
audience: re-engineer
validated: 2026-05-28
methodology: FUNCTION_DOC_WORKFLOW_V5
binary:
  name: stbc.exe
  size: 6182400
  base: 0x00400000
status: partial
evidence:
  # Class hierarchy + layout
  - claim: "RepairSubsystem vtable at 0x00892e24, size 0xC0, inherits PoweredSubsystem (vtable 0x00892d98, size >= 0xA8) which inherits ShipSubsystem (vtable 0x00892fc4, size >= 0x88)"
    address: 0x00892e24
    function: null
    confidence: high
    note: "Vtable layout cross-confirmed against ShipSubsystem ctor xrefs and class dispatch table."
  - claim: "RepairSubsystem is stored at ship+0x2D8 (one per ship)"
    address: 0x00565cd0
    function: RepairSubsystem__HandleSetPlayer
    confidence: high
    note: "HandleSetPlayer reads `iVar1 + 0x2d8` to fetch the per-ship RepairSubsystem instance."
  # Update function (main repair tick) — created this pass
  - claim: "RepairSubsystem::Update at 0x005652a0, body size 0x277 bytes (631 dec)"
    address: 0x005652a0
    function: RepairSubsystem__Update
    completeness: 64
    confidence: high
    note: "Function created in Ghidra this pass — body was in an undefined region. Vtable slot 25."
  - claim: "Update gate: standalone runs always; multiplayer-host runs; multiplayer-client returns early"
    address: 0x005652a0
    function: RepairSubsystem__Update
    confidence: high
    note: "Reads g_IsHost (0x97FA89) and g_IsMultiplayer (0x97FA8A); see decompile."
  - claim: "Repair rate formula: rawRepair = MaxRepairPoints * conditionPct * dt; divisor = min(queueCount, NumRepairTeams); perSub = rawRepair / divisor; actualGain = perSub / RepairComplexity"
    address: 0x005652a0
    function: RepairSubsystem__Update
    confidence: high
    note: "Byte-confirmed in Update decompile; ShipSubsystem::Repair (0x0056bd90) does the /RepairComplexity divide."
  - claim: "Two-pass loop: first pass repairs up to NumRepairTeams subsystems; second pass walks remaining queue and emits ET_REPAIR_CANNOT_BE_COMPLETED for destroyed entries (no repair)"
    address: 0x005652a0
    function: RepairSubsystem__Update
    confidence: high
    note: "First while loop bounded by teamsUsed<numRepairTeams; second loop unbounded after."
  - claim: "Destroyed-skip (condition <= 0.0): post ET_REPAIR_CANNOT_BE_COMPLETED but do NOT consume a repair team slot"
    address: 0x005652a0
    function: RepairSubsystem__Update
    confidence: high
    note: "The `continue` path bypasses teamsUsed++."
  # Queue management
  - claim: "RepairSubsystem::AddSubsystem at 0x00565520 — internal queue-add with duplicate check + 0-HP rejection"
    address: 0x00565520
    function: RepairSubsystem__AddSubsystem
    confidence: high
    note: "Pool-backed doubly-linked list; no max-queue-size enforced."
  - claim: "AddSubsystem checks condition at subsystem+0x30 (NOT +0x0C as an old comment suggested)"
    address: 0x00565520
    function: RepairSubsystem__AddSubsystem
    confidence: high
    note: "Decompiler shows param_2[0xc] = param_2 + 0xC*4 = +0x30. Layout tables correctly state +0x30 for condition."
  - claim: "AddToRepairList_MP at 0x00565900 wraps AddSubsystem; when added AND host AND multiplayer, posts ET_ADD_TO_REPAIR_LIST"
    address: 0x00565900
    function: RepairSubsystem__AddToRepairList_MP
    confidence: high
    note: "TGAlloc(0x28) + TGEvent ctor (FUN_006d5c00); event uses factory 0x0100 (base TGEvent)."
  - claim: "IsBeingRepaired at 0x00565890 walks first NumRepairTeams nodes"
    address: 0x00565890
    function: RepairSubsystem__IsBeingRepaired
    confidence: high
  # 7 event handlers — six created this pass
  - claim: "HandleHitEvent at 0x005658d0 (47 bytes) auto-adds damaged subsystem to repair queue"
    address: 0x005658d0
    function: RepairSubsystem__HandleHitEvent
    confidence: high
    note: "Created this pass. Reads obj_ptr from TGObjPtrEvent."
  - claim: "HandleRepairCompleted at 0x00565980 removes node from queue + refreshes UI"
    address: 0x00565980
    function: RepairSubsystem__HandleRepairCompleted
    confidence: high
  - claim: "HandleSubsystemRebuilt at 0x00565a10 re-queues if condition < maxCondition"
    address: 0x00565a10
    function: RepairSubsystem__HandleSubsystemRebuilt
    confidence: high
  - claim: "HandleRepairCannotBeCompleted at 0x00565a80 (169 bytes) removes from queue + shows destroyed UI"
    address: 0x00565a80
    function: RepairSubsystem__HandleRepairCannotBeCompleted
    confidence: high
    note: "Created this pass."
  - claim: "HandleAddToRepairList at 0x00565b30 (27 bytes) — SP-only gate"
    address: 0x00565b30
    function: RepairSubsystem__HandleAddToRepairList
    confidence: high
    note: "Created this pass. Returns early if g_IsMultiplayer != 0."
  - claim: "HandleIncreasePriority at 0x00565b50 (383 bytes) — binary toggle (head <-> tail) based on IsBeingRepaired"
    address: 0x00565b50
    function: RepairSubsystem__HandleIncreasePriority
    confidence: high
    note: "Created this pass."
  - claim: "HandleSetPlayer at 0x00565cd0 (85 bytes) reconfigures repair pane for new player ship"
    address: 0x00565cd0
    function: RepairSubsystem__HandleSetPlayer
    confidence: high
    note: "Created this pass. NOT the function that does per-instance event registrations — see RepairSubsystem::SetPlayer at 0x00565220."
  - claim: "RegisterHandlers at 0x00565d40 binds 6 per-instance handlers + 1 static handler (7 named handlers total)"
    address: 0x00565d40
    function: RepairSubsystem__RegisterHandlers
    confidence: high
    note: "Per-instance via FUN_006da130; static via FUN_006da160."
  - claim: "RegisterEventTypes at 0x00565dd0 binds 3 event-type-to-handler-name routes (per-class, not per-instance)"
    address: 0x00565dd0
    function: RepairSubsystem__RegisterEventTypes
    confidence: high
    note: "FUN_006d92b0 registers handler NAME against EventManager (ECX=0x97f864); per-instance binding happens elsewhere."
  - claim: "RepairSubsystem::SetPlayer (around 0x00565220) registers 4 ADDITIONAL per-instance event-type-to-handler bindings via FUN_006db380 (NOT documented in pre-v5)"
    address: 0x00565220
    function: RepairSubsystem__SetPlayer
    confidence: high
    note: "Binds ET_SUBSYSTEM_HIT (0x80006B), ET_REPAIR_COMPLETED (0x800074), ET_SUBSYSTEM_REBUILT (0x800070), ET_REPAIR_CANNOT_BE_COMPLETED (0x800075). Together with RegisterEventTypes 3 bindings = 7 total event-type-to-handler bindings."
  # Network path
  - claim: "HostEventHandler at 0x006a1150 (229 bytes) serializes repair events as opcode 0x06 (PythonEvent)"
    address: 0x006a1150
    function: MultiplayerGame__HostEventHandler
    confidence: high
    note: "Created this pass. PUSHes opcode 0x06, sets reliable msg+0x3A=1, routes to 'NoMe' group (string at 0x008e5528)."
  - claim: "HostEventHandler is bound to 3 event types via FUN_006db380 in MultiplayerGame_Ctor at 0x0069e7d0+ (0x008000DF at +0x18, 0x00800074 at +0x3D, 0x00800075 at +0x5C)"
    address: 0x0069e7d0
    function: MultiplayerGame__Ctor
    confidence: high
  # Wire format (CORRECTED — C1)
  - claim: "ET_ADD_TO_REPAIR_LIST (0x008000DF) on the wire uses factory 0x0100 (base TGEvent), 16-byte payload"
    address: 0x00565900
    function: RepairSubsystem__AddToRepairList_MP
    confidence: high
    note: "CORRECTION C1: prior doc claimed factory 0x0101 'TGSubsystemEvent' (fabricated class). Byte-confirmed: TGAlloc(0x28) + FUN_006d5c00 (TGEvent ctor)."
  - claim: "ET_REPAIR_COMPLETED (0x00800074) on the wire uses factory 0x010C (TGObjPtrEvent), 21-byte payload with obj_ptr = subsystem TGObject ID"
    address: 0x005652a0
    function: RepairSubsystem__Update
    confidence: high
    note: "CORRECTION C1: prior doc claimed factory 0x0101 'TGSubsystemEvent'. Byte-confirmed: TGAlloc(0x2C) + TGObjPtrEvent ctor."
  - claim: "ET_REPAIR_CANNOT_BE_COMPLETED (0x00800075) on the wire uses factory 0x010C (TGObjPtrEvent), 21-byte payload with obj_ptr = subsystem TGObject ID"
    address: 0x005652a0
    function: RepairSubsystem__Update
    confidence: high
    note: "CORRECTION C1: prior doc claimed factory 0x0101 'TGSubsystemEvent'. Byte-confirmed: TGAlloc(0x2C) + TGObjPtrEvent ctor; same posting pattern as 0x00800074."
  # Event constants (CORRECTED — C2)
  - claim: "Event 0x00800070 is ET_SUBSYSTEM_REBUILT (NOT ET_SUBSYSTEM_DAMAGED). String anchored at 0x00910784."
    address: 0x00910784
    function: null
    confidence: high
    note: "CORRECTION C2: prior doc labeled this 'ET_SUBSYSTEM_DAMAGED' — string in binary is 'ET_SUBSYSTEM_REBUILT'. Periodic rebuild timer scheduled in ShipSubsystem ctor with period 0x358637bd (~1e-6, next-tick)."
  # Opcode 0x0B override behavior (Clar1)
  - claim: "Opcode 0x0B handler PUSHes 0x008000DF as event_type override; GenericEventForward (FUN_0069fda0) FORCES puVar7[4] = param_2 when non-zero"
    address: 0x0069f3ae
    function: MpgameHandleMessage
    confidence: high
    note: "Override IS non-zero. Effect: events arrive locally as 0x008000DF regardless of wire payload's type field. Pre-v5 wording 'override: 0 (preserve original)' was inverted but the net effect was right."
  # Tractor cross-references
  - claim: "TractorBeamSystem (vtable 0x00893794) at ship+0x2D4; mode at +0xF4, totalMaxDamage at +0xF8, forceUsed at +0xFC"
    address: 0x00893794
    function: null
    confidence: high
    note: "See repair-tractor-analysis.md for the full tractor RE."
  - claim: "ImpulseEngineSubsystem stores TractorBeamSystem pointer at +0xA8 (multiplicative drag)"
    address: 0x00561230
    function: ComputeEffectiveMaxSpeed
    confidence: high
    note: "FUN_00561230 reads param_1+0xA8 and applies (1.0 - forceRatio) drag."
companions:
  - docs/gameplay/repair-tractor-analysis.md
  - docs/gameplay/repair-event-object-ids.md
  - docs/protocol/pythonevent-wire-format.md
  - docs/protocol/tgobjptrevent-class.md
  - docs/protocol/game-opcodes.md
  - docs/gameplay/combat-mechanics-re.md
  - docs/gameplay/damage-system.md
  - docs/gameplay/v5-validation-status.md
---

# Repair System — Complete Reverse Engineering

> [!NOTE]
> **v5-validated 2026-05-28 — 3 corrections + 2 clarifications.**
> Validated against current stbc.exe Ghidra import per [v5-evidence-header.md](../guides/v5-evidence-header.md).
>
> - **C1 (HIGH, wire format):** All three repair-event factory IDs were wrong. ET_ADD_TO_REPAIR_LIST uses factory **0x0100** (base TGEvent, 16B), not 0x0101. ET_REPAIR_COMPLETED and ET_REPAIR_CANNOT_BE_COMPLETED use factory **0x010C** (TGObjPtrEvent, 21B), not 0x0101. "TGSubsystemEvent (0x0101)" was a known fabrication — factory 0x0101 IS base TGEvent. See [§ Three Network Paths](#three-network-paths-for-repair-events).
> - **C2 (MED, event label):** Event 0x00800070 is **ET_SUBSYSTEM_REBUILT** (string anchored at 0x00910784), not ET_SUBSYSTEM_DAMAGED. See [§ Event Type Constants](#event-type-constants).
> - **C3 (MED, handler count):** RepairSubsystem registers **7** distinct event-type-to-handler bindings, not 3. Four additional per-instance bindings happen in `RepairSubsystem::SetPlayer` (around 0x00565220), separate from `RegisterHandlers`/`RegisterEventTypes`. See [§ Event Handler Registration](#event-handler-registration).
> - **Clar1:** Opcode 0x0B's "event type override: 0 (preserve original)" wording was inverted. Override IS non-zero (0x008000DF); net effect on the wire is the same.
> - **Clar2:** Stray inline comment on AddSubsystem's condition check ("subsystem+0x0C float field check") was using INDEX notation, not OFFSET. Removed.
>
> Six Ghidra function bodies were created this pass (HandleHitEvent, HandleRepairCannotBeCompleted, HandleAddToRepairList, HandleIncreasePriority, HandleSetPlayer, HostEventHandler) plus RepairSubsystem::Update which had an existing body but was undefined to Ghidra's auto-analyzer.
>
> **OpenBC cascade:** wire-format C1 needs propagating to `../OpenBC/docs/repair-system.md` — see [§ OpenBC Clean-Room Cascade](#openbc-clean-room-cascade).

Comprehensive RE of Bridge Commander's repair subsystem: queue data structure, repair rate formula, priority toggle algorithm, event handler chain, Engineering panel UI integration, and all three network paths. Verified against the stbc.exe binary via Ghidra decompilation and live packet traces.

Consolidates findings from:
- [repair-tractor-analysis.md](repair-tractor-analysis.md) — Initial repair queue RE (Update, AddSubsystem, IsBeingRepaired)
- [repair-event-object-ids.md](repair-event-object-ids.md) — TGObject ID assignment, event serialization chain
- [pythonevent-wire-format.md](../protocol/pythonevent-wire-format.md) — PythonEvent (opcode 0x06) wire format, 3 event classes
- [combat-mechanics-re.md](combat-mechanics-re.md) — Repair summary in consolidated combat doc

---

## Class Hierarchy

```
ShipSubsystem (vtable 0x00892fc4, size >= 0x88)
  -> PoweredSubsystem (vtable 0x00892d98, size >= 0xA8)
    -> RepairSubsystem (vtable 0x00892e24, size 0xC0)
```

One RepairSubsystem per ship, stored at ship+0x2D8.

---

## RepairSubsystem Data Layout (0xC0 bytes)

### Inherited from ShipSubsystem

| Offset | Type | Field |
|--------|------|-------|
| +0x00 | ptr | vtable |
| +0x04 | int | TGObject network ID (auto-assigned from global counter) |
| +0x18 | ptr | SubsystemProperty* (RepairSubsystemProperty) |
| +0x1C | int | child subsystem count |
| +0x30 | float | condition (current HP) |
| +0x34 | float | conditionPercentage (condition / maxCondition) |
| +0x38 | float | averagedCondition |
| +0x3C | float | frameTime (set each tick) |
| +0x40 | ptr | parent ship pointer |
| +0x44 | byte | isDisabled flag |
| +0x45 | byte | wasDisabled flag (transition detection) |

### Inherited from PoweredSubsystem

| Offset | Type | Field |
|--------|------|-------|
| +0x9C | byte | isOn (subsystem enabled) |

### RepairSubsystem-specific

| Offset | Type | Field |
|--------|------|-------|
| +0xA8 | int | queue count |
| +0xAC | ptr | queue head (ListNode*) |
| +0xB0 | ptr | queue tail (ListNode*) |
| +0xB4 | ptr | free list (recycled nodes) |
| +0xB8 | ptr | block list (for bulk deallocation) |
| +0xBC | int | pool growth size (default 2) |

---

## RepairSubsystemProperty Layout

Inherits SubsystemProperty. Repair-specific fields:

| Offset | Type | Field |
|--------|------|-------|
| +0x20 | float | MaxCondition (from SubsystemProperty) |
| +0x3C | float | RepairComplexity (from SubsystemProperty) |
| +0x4C | float | MaxRepairPoints (e.g. 50.0 for Sovereign) |
| +0x50 | int | NumRepairTeams (e.g. 3 for Sovereign) |

---

## Queue Data Structure

### Linked List Nodes (12 bytes each)

```
ListNode:
  +0x00: data   (void*)     -- pointer to the queued ShipSubsystem
  +0x04: next   (ListNode*) -- next node toward tail
  +0x08: prev   (ListNode*) -- previous node toward head
```

### Pool Allocator

Nodes are allocated from a pool managed by the linked list struct at +0xA8:
- `FUN_00486be0` — allocate node from pool (grows pool if free list empty)
- `FUN_00486ca0` — free node back to free list
- Pool growth size (default 2): allocates this many nodes when pool exhausted
- No maximum queue size — dynamically growing, no hardcoded limit

---

## Complete Function Table

| Address | Name | Signature |
|---------|------|-----------|
| 0x00565090 | RepairSubsystem::ctor | `__thiscall(void* this, int param)` |
| 0x00565190 | RepairSubsystem::scalar_deleting_dtor | vtable slot 10 |
| 0x005651c0 | RepairSubsystem::dtor | destructor body |
| 0x005652a0 | **RepairSubsystem::Update** | vtable slot 25, main repair tick |
| 0x00565520 | **RepairSubsystem::AddSubsystem** | internal queue-add (duplicate check, 0 HP gate) |
| 0x00565890 | **RepairSubsystem::IsBeingRepaired** | walks first N nodes |
| 0x00565900 | **RepairSubsystem::AddToRepairList_MP** | network-aware wrapper |
| 0x00565980 | **RepairSubsystem::HandleRepairCompleted** | removes from queue |
| 0x00565a10 | **RepairSubsystem::HandleSubsystemRebuilt** | re-queues if condition < max |
| 0x00565a80 | **RepairSubsystem::HandleRepairCannotBeCompleted** | removes from queue + shows destroyed UI |
| 0x00565b30 | **RepairSubsystem::HandleAddToRepairList** | SP-only gate |
| 0x00565b50 | **RepairSubsystem::HandleIncreasePriority** | TOGGLE algorithm |
| 0x005658d0 | **RepairSubsystem::HandleHitEvent** | catches SUBSYSTEM_HIT |
| 0x00565cd0 | **RepairSubsystem::HandleSetPlayer** | UI config on player assignment |
| 0x00565d30 | RepairSubsystem::UpdateRepairPane | updates EngRepairPane if player's ship |
| 0x00565d40 | RepairSubsystem::RegisterHandlers | 7 handler registrations (static init) |
| 0x00565dd0 | RepairSubsystem::RegisterEventTypes | 3 event-to-handler bindings |
| 0x00564fe0 | RepairSubsystem::GetProperty | returns this->property (cast) |

### Related Functions (other classes)

| Address | Name | Notes |
|---------|------|-------|
| 0x0056bd90 | ShipSubsystem::Repair | `condition += repairPoints / RepairComplexity` |
| 0x0056c310 | ShipSubsystem::GetMaxCondition | returns property->+0x20 |
| 0x0056b950 | ShipSubsystem::GetRepairComplexity | returns property->+0x3C |
| 0x0056c470 | ShipSubsystem::SetCondition | posts SUBSYSTEM_HIT when damaged |
| 0x004069b0 | GetPlayerShip | returns local player's ship ptr |
| 0x005666e0 | LinkedList::RemoveNode | removes and frees a node |
| 0x00486be0 | LinkedList::AllocNode | allocate from pool |
| 0x00486ca0 | LinkedList::FreeNode | return to free list |
| 0x006f0ee0 | TGObject::LookupByID | hash table lookup by network ID |
| 0x006d90e0 | TGEventResponder::ForwardEvent | forwards event to next handler |
| 0x006da300 | EventManager::PostEvent | posts event with auto-release |
| 0x006a1150 | HostEventHandler | serializes repair events as opcode 0x06 |

---

## Decompiled Functions

### Update (0x005652a0) — Main Repair Tick

The core repair loop, runs every frame on host/standalone only.

```c
void RepairSubsystem_Update(RepairSubsystem* this, float deltaTime) {
    PoweredSubsystem_Update(this, deltaTime);  // FUN_00562470

    if (!this->isOn)  // +0x9C
        return;

    // Host/multiplayer gate: only process repairs on standalone or host
    byte isHost = g_IsHost;  // 0x97FA89
    if (isHost == 0)
        goto do_repair;  // standalone mode
    if (isHost != 1 || !g_IsMultiplayer)  // 0x97FA8A
        return;

do_repair:
    RepairSubsystemProperty* prop = GetProperty(this);  // FUN_00564fe0

    // THE REPAIR RATE FORMULA
    float maxRepairPoints = prop->MaxRepairPoints;      // prop+0x4C
    float repairHealthPct = this->conditionPercentage;  // +0x34
    float repairAmount = maxRepairPoints * repairHealthPct * deltaTime;

    int numRepairTeams = prop->NumRepairTeams;          // prop+0x50
    int queueCount = this->queueCount;                  // +0xA8
    ListNode* node = this->queueHead;                   // +0xAC
    int teamsUsed = 0;

    if (node == NULL)
        goto done;

    // MAIN REPAIR LOOP: repairs up to NumRepairTeams subsystems
    while (teamsUsed < numRepairTeams && node != NULL) {
        ShipSubsystem* sub = node->data;    // node+0x00
        node = node->next;                   // node+0x04

        // Skip destroyed subsystems (condition <= 0.0)
        if (sub->condition <= 0.0f) {
            // Post ET_REPAIR_CANNOT_BE_COMPLETED (0x800075)
            TGMessage* msg = CreateMessage();
            msg->SetSource(this->parentShip);
            msg->data[10] = sub->subsystemID;
            msg->eventType = 0x800075;
            EventManager_PostEvent(msg);
            continue;  // Does NOT consume a repair team
        }

        // PER-SUBSYSTEM REPAIR AMOUNT
        int divisor = min(queueCount, numRepairTeams);
        float perTeamRepair = repairAmount / (float)divisor;

        // Apply repair (Repair() divides by RepairComplexity internally)
        sub->Repair(perTeamRepair);  // FUN_0056bd90

        // Check if fully repaired
        float ratio = sub->condition / GetMaxCondition(sub);
        if (ratio >= 1.0f) {
            // Post ET_REPAIR_COMPLETED (0x800074)
            TGMessage* msg = CreateMessage();
            msg->SetSource(this->parentShip);
            msg->data[10] = sub->subsystemID;
            msg->eventType = 0x800074;
            EventManager_PostEvent(msg);
        }

        teamsUsed++;
    }

    // Process remaining queue items (beyond team count)
    // Only sends destruction notifications, no repair
    while (node != NULL) {
        ShipSubsystem* sub = node->data;
        node = node->next;
        if (sub->condition <= 0.0f) {
            PostRepairCannotBeCompletedEvent(this, sub);
        }
    }

done:
    // Update UI if this is the player's ship
    int playerShip = GetPlayerShip();  // FUN_004069b0
    if (playerShip != 0 && playerShip == this->parentShip) {
        if (g_EngRepairPane != NULL)  // 0x98B188
            EngRepairPane_Update(g_EngRepairPane);  // FUN_005512e0
    }
}
```

### AddSubsystem (0x00565520) — Internal Queue-Add

```c
bool RepairSubsystem::AddSubsystem(ShipSubsystem* subsystem) {
    // 1. Walk the linked list to check for duplicates
    ListNode* node = this->queueHead;  // +0xAC
    while (node != NULL) {
        ShipSubsystem* existing = node->data;
        node = node->next;
        if (subsystem == existing)
            return false;  // Already in queue, reject duplicate
    }

    // 2. Check if subsystem condition > 0.0 (read at subsystem+0x30)
    if (subsystem->condition > 0.0f) {
        // Allocate a list node from the pool
        ListNode* newNode = AllocListNode(&this->listStruct);  // FUN_00486be0

        // Insert at TAIL of the doubly-linked list
        newNode->data = subsystem;
        newNode->next = NULL;
        newNode->prev = this->listTail;
        if (this->listTail != NULL) {
            this->listTail->next = newNode;
        } else {
            this->listHead = newNode;
        }
        this->listTail = newNode;
        this->listCount++;
        return true;
    } else {
        // Condition is 0.0 (destroyed) -- do NOT add to queue
        // Instead, if this is the player's ship, notify the UI
        if (GetPlayerShipID() == subsystem->parentShipID && g_EngRepairPane != NULL) {
            EngRepairPane_AddDestroyed(g_EngRepairPane, subsystem);
            EngRepairPane_Refresh(g_EngRepairPane);
        }
        return true;  // Returns true (success) even though not queued
    }
}
```

### AddToRepairList_MP (0x00565900) — Network-Aware Wrapper

```c
void RepairSubsystem::AddToRepairList_MP(RepairSubsystem* this, ShipSubsystem* subsystem) {
    bool added = AddSubsystem(this, subsystem);  // FUN_00565520

    if (added && g_IsHost && g_IsMultiplayer) {
        // Create TGEvent — factory 0x0100 (base TGEvent), alloc size 0x28
        // [v5-validated 2026-05-28] Prior doc claimed factory 0x0101 ("TGSubsystemEvent")
        // — that class does not exist; 0x0101 IS base TGEvent. AddToRepairList_MP allocates
        // 0x28 bytes (small for TGObjPtrEvent which is 0x2C) and calls FUN_006d5c00
        // (TGEvent ctor), confirming the base type. Wire payload is 16 bytes.
        TGEvent* evt = TGEvent_ctor(alloc(0x28), 0);  // auto-assign ID

        evt->eventType = 0x008000DF;      // ET_ADD_TO_REPAIR_LIST
        TGEvent_SetDest(evt, this);        // dest = RepairSubsystem (evt+0x0C)
        TGEvent_SetSource(evt, subsystem); // source = damaged subsystem (evt+0x08)

        EventManager_PostEvent(evt);       // FUN_006da2a0
        // HostEventHandler catches this and sends opcode 0x06 to "NoMe" group
    }
}
```

### IsBeingRepaired (0x00565890)

```c
bool RepairSubsystem::IsBeingRepaired(RepairSubsystem* this, ShipSubsystem* target) {
    ListNode* node = this->queueHead;     // +0xAC
    RepairSubsystemProperty* prop = GetProperty(this);  // FUN_00564fe0
    int numTeams = prop->NumRepairTeams;  // prop+0x50
    int checked = 0;

    while (checked < numTeams && node != NULL) {
        ShipSubsystem* sub = node->data;
        node = node->next;
        if (sub == target)
            return true;  // target is within the active repair slots
        checked++;
    }
    return false;  // target is waiting or not in queue
}
```

### HandleRepairCompleted (0x00565980)

Called when a subsystem reaches max HP. Removes from queue and updates UI.

```c
void RepairSubsystem::HandleRepairCompleted(RepairSubsystem* this, TGCharEvent* event) {
    int subsysID = event->charData;  // event+0x28 (subsystem's TGObject network ID)
    ShipSubsystem* subsystem = TGObject_LookupByID(subsysID);  // FUN_006f0ee0
    int playerShip = GetPlayerShip();  // FUN_004069b0

    if (subsystem != NULL) {
        // Walk the queue to find the node
        ListNode* cursor = this->queueHead;  // +0xAC
        ListNode* foundNode = NULL;
        while (cursor != NULL) {
            foundNode = cursor;
            ShipSubsystem* nodeData = cursor->data;
            cursor = cursor->next;
            if (subsystem == nodeData) break;
        }

        // Remove from queue if found
        if (foundNode != NULL) {
            LinkedList_RemoveNode(&this->listStruct, &foundNode);  // FUN_005666e0
        }

        // If this is the player's ship, update the repair pane
        if (playerShip == subsystem->parentShip && g_EngRepairPane != NULL) {
            EngRepairPane_RefreshRepairItem(g_EngRepairPane, subsystem);  // FUN_00551990
        }
    }

    TGEventResponder_ForwardEvent(this, event);  // FUN_006d90e0
}
```

### HandleRepairCannotBeCompleted (0x00565a80)

Called when a subsystem is destroyed while in the repair queue. Removes from queue AND shows the "destroyed" UI indicator (unlike HandleRepairCompleted which only removes).

```c
void RepairSubsystem::HandleRepairCannotBeCompleted(RepairSubsystem* this, TGCharEvent* event) {
    int subsysID = event->charData;  // event+0x28
    ShipSubsystem* subsystem = TGObject_LookupByID(subsysID);  // FUN_006f0ee0
    int playerShip = GetPlayerShip();  // FUN_004069b0

    if (subsystem != NULL) {
        // Walk the queue to find the node
        ListNode* cursor = this->queueHead;  // +0xAC
        ListNode* foundNode = NULL;
        while (cursor != NULL) {
            foundNode = cursor;
            ShipSubsystem* nodeData = cursor->data;
            cursor = cursor->next;
            if (subsystem == nodeData) break;
        }

        // Remove from queue if found
        if (foundNode != NULL) {
            LinkedList_RemoveNode(&this->listStruct, &foundNode);  // FUN_005666e0
        }

        // If this is the player's ship, update UI AND show "destroyed" indicator
        if (playerShip == subsystem->parentShip && g_EngRepairPane != NULL) {
            EngRepairPane_RefreshRepairItem(g_EngRepairPane, subsystem);  // FUN_00551990
            EngRepairPane_ShowDestroyed(g_EngRepairPane, subsystem);      // FUN_00551870
        }
    }

    TGEventResponder_ForwardEvent(this, event);  // FUN_006d90e0
}
```

### HandleSubsystemRebuilt (0x00565a10)

Called when a destroyed subsystem is rebuilt (e.g. via script). Re-queues if not yet at full HP.

```c
void RepairSubsystem::HandleSubsystemRebuilt(RepairSubsystem* this, TGEvent* event) {
    ShipSubsystem* subsystem = GetSubsystemFromEvent(event);  // FUN_0056b8f0(event+0x08)
    int playerShip = GetPlayerShip();  // FUN_004069b0

    if (subsystem != NULL && playerShip != 0) {
        // Refresh UI
        EngRepairPane_RefreshRepairItem(g_EngRepairPane, subsystem);  // FUN_00551990

        // If condition < maxCondition, re-queue for continued repair
        float condition = subsystem->condition;  // +0x30
        float maxCondition = GetMaxCondition(subsystem);  // FUN_0056c310
        if (condition < maxCondition) {
            AddToRepairList_MP(this, subsystem);  // FUN_00565900
        }
    }

    TGEventResponder_ForwardEvent(this, event);  // FUN_006d90e0
}
```

### HandleAddToRepairList (0x00565b30) — Singleplayer-Only Gate

In multiplayer, opcode 0x0B handles AddToRepairList via GenericEventForward. This local handler is only active in singleplayer.

```c
void RepairSubsystem::HandleAddToRepairList(RepairSubsystem* this, TGEvent* event) {
    if (g_IsMultiplayer != 0) return;  // SP-ONLY gate

    ShipSubsystem* subsystem = event->source;  // event+0x08
    AddToRepairList_MP(this, subsystem);        // FUN_00565900
}
```

### HandleIncreasePriority (0x00565b50) — The Toggle Algorithm

This is the priority reordering handler, triggered by opcode 0x11 (RepairListPriority). The algorithm is a **binary toggle**, NOT "move up one position":

- If the subsystem IS currently being actively repaired (within the first `NumRepairTeams` nodes): **demote to TAIL**
- If the subsystem is NOT being actively repaired (waiting area): **promote to HEAD**

```c
void RepairSubsystem::HandleIncreasePriority(RepairSubsystem* this, TGObjPtrEvent* event) {
    int subsysID = event->obj_ptr;  // event+0x28 (int32 TGObject network ID)
    ShipSubsystem* targetSub = TGObject_LookupByID(subsysID);  // FUN_006f0ee0

    if (targetSub == NULL) goto done;

    // Walk the queue to find the node containing this subsystem
    ListNode* head = this->queueHead;  // +0xAC
    if (head == NULL) goto update_ui;

    ListNode* foundNode = head;
    while (true) {
        ShipSubsystem* nodeData = foundNode->data;
        ListNode* nextNode = foundNode->next;
        if (targetSub == nodeData) break;
        if (nextNode == NULL) goto update_ui;
        foundNode = nextNode;
    }

    if (foundNode == NULL) goto update_ui;

    // Check if this subsystem is currently being actively repaired
    bool wasBeingRepaired = IsBeingRepaired(this, targetSub);  // FUN_00565890

    // === REMOVE THE NODE FROM THE DOUBLY-LINKED LIST ===
    LinkedList* list = &this->listStruct;  // this+0xA8

    if (foundNode == list->head) {
        ListNode* newHead = foundNode->next;
        list->head = newHead;
        if (newHead == NULL) list->tail = NULL;
        else newHead->prev = NULL;
    } else if (foundNode == list->tail) {
        ListNode* newTail = foundNode->prev;
        list->tail = newTail;
        if (newTail == NULL) list->head = NULL;
        else newTail->next = NULL;
    } else {
        ListNode* prevNode = foundNode->prev;
        ListNode* nextNode = foundNode->next;
        if (prevNode != NULL) prevNode->next = nextNode;
        if (nextNode != NULL) nextNode->prev = prevNode;
    }

    LinkedList_FreeNode(list, foundNode);  // FUN_00486ca0
    list->count--;

    // === RE-INSERT AT NEW POSITION (THE TOGGLE) ===
    if (wasBeingRepaired) {
        // WAS BEING REPAIRED → INSERT AT TAIL (demote)
        ListNode* newNode = LinkedList_AllocNode(list);
        newNode->data = targetSub;
        newNode->next = NULL;
        newNode->prev = list->tail;
        if (list->tail != NULL) {
            list->tail->next = newNode;
            list->tail = newNode;
        } else {
            list->head = newNode;
            list->tail = newNode;
        }
    } else {
        // WAS NOT BEING REPAIRED → INSERT AT HEAD (promote)
        ListNode* newNode = LinkedList_AllocNode(list);
        newNode->data = targetSub;
        newNode->prev = NULL;
        newNode->next = list->head;
        if (list->head != NULL) {
            list->head->prev = newNode;
        } else {
            list->tail = newNode;
        }
        list->head = newNode;
    }

    list->count++;

update_ui:
    RepairSubsystem_UpdateRepairPane(this);  // FUN_00565d30

done:
    TGEventResponder_ForwardEvent(this, event);  // FUN_006d90e0
}
```

### HandleHitEvent (0x005658d0)

Catches SUBSYSTEM_HIT events and auto-adds the damaged subsystem to the repair queue.

```c
void RepairSubsystem::HandleHitEvent(RepairSubsystem* this, TGObjPtrEvent* event) {
    int subsystemID = event->obj_ptr;  // event+0x28 (int32 TGObject network ID)
    ShipSubsystem* sub = TGObject_LookupByID(subsystemID);  // FUN_006f0ee0

    if (sub != NULL) {
        AddToRepairList_MP(this, sub);  // FUN_00565900
    }

    TGEventResponder_ForwardEvent(this, event);  // FUN_006d90e0
}
```

### HandleSetPlayer (0x00565cd0)

Called when the player's ship changes (e.g. at game start or spectator switch). Reconfigures the Engineering repair pane to track the new ship's repair subsystem.

```c
void RepairSubsystem::HandleSetPlayer(TGEvent* event) {
    void* repairPane = g_EngRepairPane;  // DAT_0098b188
    int playerShip = GetPlayerShip();    // FUN_004069b0
    if (repairPane == NULL) return;

    ShipClass* ship = CastToShipClass(event->source);  // FUN_005ab670

    if (playerShip == ship) return;  // already tracking this ship

    EngRepairPane_ClearAll(repairPane);  // FUN_00551230
    if (playerShip == 0) return;

    RepairSubsystem* newRepairSub = playerShip->repairSubsystem;  // ship+0x2D8
    EngRepairPane_SetRepairSubsystem(repairPane, newRepairSub);    // FUN_00550ef0

    RepairSubsystemProperty* prop = GetProperty(newRepairSub);     // FUN_00564fe0
    int numTeams = prop->NumRepairTeams;                            // prop+0x50
    EngRepairPane_SetNumTeams(repairPane, numTeams);                // FUN_00550ee0
}
```

### ShipSubsystem::Repair (0x0056bd90)

```c
void ShipSubsystem::Repair(float repairPoints) {
    float repairComplexity = GetRepairComplexity(this);  // property->+0x3C
    float newCondition = this->condition + (repairPoints / repairComplexity);
    SetCondition(this, newCondition);  // FUN_0056c470
}
```

---

## Event Handler Registration

> [!IMPORTANT]
> **C3 — Registration happens in THREE places, not two.** The pre-v5 doc listed `RegisterHandlers` (7 named handlers) and `RegisterEventTypes` (3 event-type-to-handler-name routes). A third site lives in `RepairSubsystem::SetPlayer` (around 0x00565220) which binds **4 additional per-instance event-type-to-handler bindings** via FUN_006db380. Total distinct event-type-to-handler bindings: **7**, not 3.

### Layer 1 — Handler Name Registration (RegisterHandlers, 0x00565d40)

Static-init function that publishes 7 handler-name → handler-function mappings. Two registration helpers: `FUN_006da130` for per-instance handlers, `FUN_006da160` for static handlers.

| Address | Handler | Debug String | Registration Type |
|---------|---------|-------------|-------------------|
| 0x005658d0 | HandleHitEvent | `RepairSubsystem::HandleHitEvent` | Per-instance (006da130) |
| 0x00565980 | HandleRepairCompleted | `RepairSubsystem::HandleRepairCompleted` | Per-instance (006da130) |
| 0x00565a10 | HandleSubsystemRebuilt | `RepairSubsystem::HandleSubsystemRebuilt` | Per-instance (006da130) |
| 0x00565a80 | HandleRepairCannotBeCompleted | `RepairSubsystem::HandleRepairCannotBeCompleted` | Per-instance (006da130) |
| 0x00565b50 | HandleIncreasePriority | `RepairSubsystem::HandleIncreasePriorityEvent` | Per-instance (006da130) |
| 0x00565b30 | HandleAddToRepairList | `RepairSubsystem::HandleAddToRepairList` | Per-instance (006da130) |
| 0x00565cd0 | HandleSetPlayer | `RepairSubsystem::HandleSetPlayer` | Static (006da160) |

### Layer 2 — Per-Class Event-Type Routing (RegisterEventTypes, 0x00565dd0)

3 bindings of event-type IDs to handler NAMES, registered against EventManager (ECX=0x97f864). FUN_006d92b0 stores per-class routing; FUN_006db380 stores static routing.

```c
void RepairSubsystem_RegisterEventTypes(void) {
    // Per-class event handlers (FUN_006d92b0)
    RegisterEventHandler(0x00800076, "HandleIncreasePriorityEvent");  // ET_REPAIR_INCREASE_PRIORITY
    RegisterEventHandler(0x008000DF, "HandleAddToRepairList");        // ET_ADD_TO_REPAIR_LIST

    // Static event handler (FUN_006db380)
    RegisterStaticHandler(0x0080000E, "HandleSetPlayer");             // ET_SET_PLAYER
}
```

### Layer 3 — Per-Instance Event-Type Bindings (RepairSubsystem::SetPlayer, 0x00565220)

[v5-validated 2026-05-28] Each RepairSubsystem instance binds 4 ADDITIONAL event-type-to-handler routes via FUN_006db380 when its parent ship's player is set. These bindings are PER-INSTANCE — they're attached to the specific RepairSubsystem object, not the class.

| Event ID | Handler Name | Handler Function | Purpose |
|---------|-------------|------------------|---------|
| 0x0080006B (ET_SUBSYSTEM_HIT) | `s_RepairSubsystem__HandleHitEvent` | 0x005658d0 | Auto-queue damaged subsystem |
| 0x00800074 (ET_REPAIR_COMPLETED) | `s_RepairSubsystem__HandleRepairCom` | 0x00565980 | Remove from queue + UI refresh |
| 0x00800070 (ET_SUBSYSTEM_REBUILT) | `s_RepairSubsystem__HandleSubsystem` | 0x00565a10 | Re-queue if condition < max |
| 0x00800075 (ET_REPAIR_CANNOT_BE_COMPLETED) | `s_RepairSubsystem__HandleRepairCan` | 0x00565a80 | Remove from queue + show destroyed |

The handler-name strings live near 0x008e4fd8/0x008e5008/0x008e5030/0x008e5058 — same string anchors used by RegisterHandlers.

### Total Bindings — 7

- Layer 2 contributes 3 (per-class routing): 0x00800076, 0x008000DF, 0x0080000E.
- Layer 3 contributes 4 (per-instance bindings): 0x0080006B, 0x00800074, 0x00800070, 0x00800075.
- Total: **7 distinct event-type-to-handler bindings.**

The two layers serve different routing scopes — Layer 2 is class-wide static routing (every RepairSubsystem reacts the same way to opcode 0x0B's event), Layer 3 is instance-specific (each ship's RepairSubsystem binds to that specific ship's hit events). Pre-v5 docs conflated these layers.

---

## Event Type Constants

[v5-validated 2026-05-28] — event-name strings verified against binary string table.

| Code | Constant Name | Direction | Description | String Anchor |
|------|--------------|-----------|-------------|---------------|
| 0x008000DF | ET_ADD_TO_REPAIR_LIST | Host → All (opcode 0x06) | Subsystem added to repair queue | — |
| 0x00800074 | ET_REPAIR_COMPLETED | Host → All (opcode 0x06) | Subsystem fully repaired, removed from queue | — |
| 0x00800075 | ET_REPAIR_CANNOT_BE_COMPLETED | Host → All (opcode 0x06) | Subsystem destroyed while queued | — |
| 0x00800076 | ET_REPAIR_INCREASE_PRIORITY | Client → Host (opcode 0x11) | Priority toggle (via GenericEventForward) | — |
| 0x0080006B | ET_SUBSYSTEM_HIT | Internal only | Triggers auto-add to repair queue | — |
| 0x00800070 | **ET_SUBSYSTEM_REBUILT** | Internal only | Periodic rebuild-tick timer (scheduled in ShipSubsystem ctor with period 0x358637bd ≈ next-tick) | 0x00910784 |
| 0x0080000E | ET_SET_PLAYER | Internal only | Player's ship changed | — |

> [!NOTE]
> **C2 — 0x00800070 was previously mislabeled "ET_SUBSYSTEM_DAMAGED".** Binary string at 0x00910784 is `ET_SUBSYSTEM_REBUILT`. This event is the periodic rebuild timer that RepairSubsystem::SetPlayer binds to HandleSubsystemRebuilt for re-queuing partially-rebuilt subsystems.

---

## Repair Rate Formula

[v5-validated 2026-05-28 — byte-confirmed in `RepairSubsystem::Update` decompile at 0x005652a0]

```
rawRepairAmount = MaxRepairPoints * (repairSystem.condition / repairSystem.maxCondition) * deltaTime

divisor = min(queueCount, NumRepairTeams)

perSubsystemRepair = rawRepairAmount / divisor

actualConditionGain = perSubsystemRepair / subsystem.RepairComplexity
```

### Key Characteristics

1. **The repair system's own health scales the output** (damaged repair bay = slower) — `conditionPercentage` is read at this+0x34.
2. **Multiple subsystems repaired simultaneously** (up to NumRepairTeams) — `teamsUsed < numRepairTeams` loop bound.
3. The repair amount is **divided equally** among min(queueCount, numTeams) subsystems.
4. **RepairComplexity** acts as a final divisor inside `ShipSubsystem::Repair` (0x0056bd90): `condition += repairPoints / RepairComplexity`.
5. **Destroyed subsystems** (condition <= 0) are SKIPPED but NOT removed and DO NOT consume a repair-team slot — they generate ET_REPAIR_CANNOT_BE_COMPLETED instead. The `continue` path in Update bypasses `teamsUsed++`.
6. **Two-pass loop**: after the team-bounded first pass, a second unbounded loop walks the rest of the queue and emits ET_REPAIR_CANNOT_BE_COMPLETED for any additional destroyed entries (notify-only, no repair).

### Example (Sovereign class, healthy repair system, 2 items in queue)

```
rawRepair = 50.0 * 1.0 * 0.033 = 1.65 per tick (at 30fps)
divisor = min(2, 3) = 2
perSubsystem = 1.65 / 2 = 0.825
For a phaser (complexity=3.0): conditionGain = 0.825 / 3.0 = 0.275 HP/tick
For a tractor (complexity=7.0): conditionGain = 0.825 / 7.0 = 0.118 HP/tick
```

---

## Three Network Paths for Repair Events

> [!IMPORTANT]
> **C1 — Wire-format factory IDs corrected.** The pre-v5 doc uniformly claimed "Factory: TGSubsystemEvent (0x0101), 17 bytes total" for all three Path 1 events. That was wrong on two counts: (1) "TGSubsystemEvent" is a fabricated class — factory 0x0101 IS base TGEvent; (2) the three events use **two different factories** with different payload sizes.
>
> | Event | Pre-v5 (wrong) | Actual (byte-confirmed) |
> |---|---|---|
> | 0x008000DF ET_ADD_TO_REPAIR_LIST | factory 0x0101, 17B | **factory 0x0100 (base TGEvent), 16B** |
> | 0x00800074 ET_REPAIR_COMPLETED | factory 0x0101, 17B | **factory 0x010C (TGObjPtrEvent), 21B** |
> | 0x00800075 ET_REPAIR_CANNOT_BE_COMPLETED | factory 0x0101, 17B | **factory 0x010C (TGObjPtrEvent), 21B** |
>
> Evidence: AddToRepairList_MP (0x00565900) calls TGAlloc(0x28) + FUN_006d5c00 (TGEvent ctor); RepairSubsystem::Update (0x005652a0) calls TGAlloc(0x2C) + TGObjPtrEvent_Ctor for both 0x00800074 and 0x00800075.

### Path 1a: Opcode 0x06 (PythonEvent) — ET_ADD_TO_REPAIR_LIST as base TGEvent

**Direction**: Host → All Clients (via "NoMe" routing group, string at 0x008e5528)
**Reliability**: Reliable (ACK required, msg+0x3A = 1)
**Factory**: **0x0100 (base TGEvent)**, 16-byte wire payload
**Sender**: `AddToRepairList_MP` at 0x00565900 → posts event → `HostEventHandler` at 0x006a1150 catches and serializes
**Trigger**: Host's repair-queue add (auto from collision, or via opcode 0x0B relay)

**Wire format** (16 bytes after opcode):
```
Offset  Size  Type    Field            Notes
------  ----  ----    -----            -----
0       1     u8      opcode           0x06
1       4     i32     factory_id       0x00000100 (base TGEvent)
5       4     i32     event_type       0x008000DF (ET_ADD_TO_REPAIR_LIST)
9       4     i32     source_obj_id    Damaged subsystem's TGObject ID
13      4     i32     dest_obj_id      RepairSubsystem's TGObject ID
```

### Path 1b: Opcode 0x06 (PythonEvent) — Repair Completion / Cannot-Complete as TGObjPtrEvent

**Direction**: Host → All Clients (via "NoMe" routing group)
**Reliability**: Reliable
**Factory**: **0x010C (TGObjPtrEvent)**, 21-byte wire payload
**Sender**: `RepairSubsystem::Update` at 0x005652a0 → posts event → `HostEventHandler` at 0x006a1150 catches and serializes
**Trigger**: Repair tick reaches completion (ratio ≥ 1.0) or detects destroyed queued subsystem

Used for 2 event types that the host generates during the repair tick:

| Event | Trigger |
|-------|---------|
| ET_REPAIR_COMPLETED (0x00800074) | Subsystem reached max HP |
| ET_REPAIR_CANNOT_BE_COMPLETED (0x00800075) | Subsystem destroyed while queued |

**Wire format** (21 bytes after opcode):
```
Offset  Size  Type    Field            Notes
------  ----  ----    -----            -----
0       1     u8      opcode           0x06
1       4     i32     factory_id       0x0000010C (TGObjPtrEvent)
5       4     i32     event_type       0x00800074 or 0x00800075
9       4     i32     source_obj_id    Parent ship TGObject ID
13      4     i32     dest_obj_id      RepairSubsystem TGObject ID
17      4     i32     obj_ptr          Subsystem TGObject network ID
```

### Path 2: Opcode 0x0B (AddToRepairList) — Client-Initiated Manual Repair

**Direction**: Client → Host → All (via GenericEventForward relay)
**Handler**: FUN_0069fda0 (GenericEventForward)
**Event type override**: **0x008000DF** (FORCED non-zero, see Clar1 below)

> **Clar1 — override is non-zero, not zero.** Pre-v5 doc said "override: 0 (preserve original type 0x008000DF)". Binary truth: opcode 0x0B's dispatch site at 0x0069f3ae PUSHes 0x008000DF as `param_2`; GenericEventForward at FUN_0069fda0 contains `if (param_2 != 0) { puVar7[4] = param_2; }` — i.e. the type IS forced. The net effect on the wire is the same (events arrive as 0x008000DF locally), but "override: 0" was a misread of the mechanism.

Sent when a player manually requests repair of a subsystem from the Engineering panel. The GenericEventForward handler relays to all peers and dispatches locally.

**Wire format**: TGCharEvent serialization (18 bytes total). Note: factory ID for opcode 0x0B is unanchored in current evidence — see [Open Questions](#open-questions) below.
```
Offset  Size  Type    Field            Notes
------  ----  ----    -----            -----
0       1     u8      opcode           0x0B
1       4     i32     factory_id       0x00000105 (TGCharEvent)  [unanchored — see OQ2]
5       4     i32     event_type       0x008000DF (forced by GenericEventForward override)
9       4     i32     source_obj_id    Source object
13      4     i32     dest_obj_id      Related object
17      1     u8      char_value       Extra data byte
```

### Path 3: Opcode 0x11 (RepairListPriority) — Client-Initiated Priority Toggle

**Direction**: Client → Host → All (via GenericEventForward relay)
**Handler**: FUN_0069fda0 (GenericEventForward)
**Event type**: 0x00800076 (ET_REPAIR_INCREASE_PRIORITY)
**Event type override**: 0x00800076 (FORCED non-zero — same mechanism as Path 2)

Sent when a player clicks a subsystem in the repair queue to change its priority. The handler on the receiving end is HandleIncreasePriority (toggle algorithm).

**Wire format**: TGObjPtrEvent serialization (21 bytes total):
```
Offset  Size  Type    Field            Notes
------  ----  ----    -----            -----
0       1     u8      opcode           0x11
1       4     i32     factory_id       0x0000010C (TGObjPtrEvent)
5       4     i32     event_type       0x00800076 (ET_REPAIR_INCREASE_PRIORITY)
9       4     i32     source_obj_id    Source object
13      4     i32     dest_obj_id      Related object
17      4     i32     obj_ptr          Subsystem TGObject network ID
```

---

## Collision → Repair Chain

The complete event chain from collision to repair queue entry:

```
1. ProximityManager detects collision
2. Posts ET_COLLISION_EFFECT (0x00800050)

3. ShipClass::CollisionEffectHandler (0x005AF9C0):
   a. Validates sender is host
   b. Sends CollisionEffect (opcode 0x15) to "NoMe" group
   c. Falls through to collision damage application

4. Collision damage → per-subsystem damage:
   a. Reads subsystem condition
   b. Reduces by damage amount
   c. Calls ShipSubsystem::SetCondition (FUN_0056C470)

5. SetCondition:
   a. Stores new condition
   b. If newCondition < maxCondition AND ship alive:
      → Posts ET_SUBSYSTEM_HIT (0x0080006B) as TGObjPtrEvent (factory 0x10C)
        source = NULL, dest = owner ship, obj_ptr = subsystem object ID

6. RepairSubsystem::HandleHitEvent catches ET_SUBSYSTEM_HIT:
   a. Looks up subsystem by obj_ptr (TGObject ID)
   b. Calls AddToRepairList_MP (FUN_00565900)
   c. AddSubsystem rejects duplicates, rejects 0 HP
   d. If successful AND g_IsHost AND g_IsMultiplayer:
      → Posts ET_ADD_TO_REPAIR_LIST (0x008000DF) as base TGEvent (factory 0x0100, 16B)
        [v5-validated 2026-05-28 — NOT factory 0x0101 as pre-v5 doc claimed]

7. HostEventHandler (0x006A1150) catches ET_ADD_TO_REPAIR_LIST:
   → Serializes as opcode 0x06, sends reliably to "NoMe" group

8. Clients receive opcode 0x06:
   → FUN_0069f880 deserializes factory 0x0100 (base TGEvent)
   → Posts ET_ADD_TO_REPAIR_LIST locally
   → Client's RepairSubsystem::HandleAddToRepairList runs (SP gate blocks it)
   → Instead, the event's source/dest are resolved via hash table and the local
     repair subsystem adds the subsystem to its queue
```

### Why ~14 PythonEvent Messages Per Collision

- Two ships collide → each takes damage
- Each ship has ~7 top-level subsystems in the damage volume
- Each damaged subsystem → SUBSYSTEM_HIT → ADD_TO_REPAIR_LIST → PythonEvent
- 7 subsystems x 2 ships = ~14 PythonEvent messages
- Exact count varies with collision geometry and duplicate rejection

---

## Engineering Panel UI

### Three Display Areas

The Engineering panel (EngRepairPane, global at 0x0098B188) displays repair queue items in three areas:

| Area | Content |
|------|---------|
| REPAIR_AREA | Active repair slots (first NumRepairTeams items from queue head) |
| WAITING_AREA | Queued but not yet being repaired (remaining items after NumRepairTeams) |
| DESTROYED_AREA | Subsystems that are destroyed (condition <= 0.0) |

### UI Update Functions

| Address | Function | Purpose |
|---------|----------|---------|
| 0x005512e0 | EngRepairPane_Update | Full refresh (called each tick from Update) |
| 0x00551990 | EngRepairPane_RefreshRepairItem | Refresh a specific subsystem's display |
| 0x00551870 | EngRepairPane_ShowDestroyed | Move item to DESTROYED_AREA |
| 0x00551230 | EngRepairPane_ClearAll | Clear all items (on player ship change) |
| 0x00550ef0 | EngRepairPane_SetRepairSubsystem | Point pane at a ship's repair subsystem |
| 0x00550ee0 | EngRepairPane_SetNumTeams | Set number of active repair slots |

### Player Interaction

- **Click in REPAIR_AREA**: Sends ET_REPAIR_INCREASE_PRIORITY → HandleIncreasePriority → demotes to tail
- **Click in WAITING_AREA**: Sends ET_REPAIR_INCREASE_PRIORITY → HandleIncreasePriority → promotes to head
- **Click in DESTROYED_AREA**: No action (destroyed subsystems cannot be repaired)

---

## Sovereign-Class Reference Values

### Repair Subsystem

| Property | Value |
|----------|-------|
| MaxRepairPoints | 50.0 |
| NumRepairTeams | 3 |
| MaxCondition | 8,000 |
| RepairComplexity | 1.0 |

### Subsystem HP and RepairComplexity

| Subsystem | MaxCondition | RepairComplexity |
|-----------|-------------|------------------|
| Shield Generator | 10,000 | — |
| Sensor Array | 8,000 | 1.0 |
| Warp Core (reactor) | 7,000 | 2.0 |
| Impulse Engines (system) | 3,000 | 3.0 |
| Port/Star Impulse (each) | 3,000 | — |
| Torpedo System | 6,000 | — |
| Forward Torpedo (each, x4) | 2,200 | — |
| Aft Torpedo (each, x2) | 2,200 | — |
| Phaser Emitter (each, x8) | 1,000 | — |
| Phaser Controller | 8,000 | — |
| Repair | 8,000 | 1.0 |
| Warp Engines (system) | 8,000 | — |
| Port/Star Warp (each) | 4,500 | — |
| Tractor System | 3,000 | 7.0 |
| Tractor (each, x4) | 1,500 | 7.0 |
| Bridge | 10,000 | 4.0 |
| Hull | 12,000 | 3.0 |

---

## Open Questions

These remain pending future RE work — not blockers for the current `partial` verdict.

- **OQ1: What posts the local 0x008000DF event from client UI that becomes wire opcode 0x0B?** `AddToRepairList_MP` at 0x00565900 only fires from the host-auto-queue path (called from HandleHitEvent and HandleSubsystemRebuilt). The manual Repair-button → opcode 0x0B sender path is currently unanchored. Suspect a Python-side sender (likely SendTGMessage in the Engineering panel script), but the C++ entry point is unidentified.
- **OQ2: What factory does opcode 0x0B's wire payload actually use?** The doc claims TGCharEvent (0x105, 18B) — this is inherited from pre-v5 docs and unanchored against the current binary. If only the SP-only HandleAddToRepairList exists for received 0x0B locally, opcode 0x0B may be **dead code in MP**. Verification path: search stock-dedi packet traces for byte 0x0B occurrences to confirm whether MP clients actually send it.

---

## OpenBC Clean-Room Cascade

> **C1 propagation needed.** The factory ID corrections in [§ Three Network Paths](#three-network-paths-for-repair-events) need cascading into the OpenBC clean-room repair spec at `../OpenBC/docs/repair-system.md` if/when that spec is authored. The pre-v5 "TGSubsystemEvent (0x0101), 17 bytes" claim is wire-incompatible with stock BC; OpenBC servers built to that spec would emit packets that stock clients cannot deserialize. Correct values:
>
> - **0x008000DF** → factory 0x0100 (base TGEvent), 16B payload
> - **0x00800074** → factory 0x010C (TGObjPtrEvent), 21B payload
> - **0x00800075** → factory 0x010C (TGObjPtrEvent), 21B payload

---

## Related Documents

- [repair-tractor-analysis.md](repair-tractor-analysis.md) — Repair queue + tractor beam combined RE (initial decompilations) — sibling doc, batched validation 2026-05-28
- [repair-event-object-ids.md](repair-event-object-ids.md) — TGObject ID assignment, event serialization deep-dive
- [pythonevent-wire-format.md](../protocol/pythonevent-wire-format.md) — PythonEvent (opcode 0x06) polymorphic transport
- [tgobjptrevent-class.md](../protocol/tgobjptrevent-class.md) — TGObjPtrEvent class layout (factory 0x010C) — used by Path 1b and Path 3
- [combat-mechanics-re.md](combat-mechanics-re.md) — Consolidated combat RE (shields, cloak, weapons, repair, tractor)
- [damage-system.md](damage-system.md) — Full damage pipeline (collision → ProcessDamage → subsystem distribution)
- [collision-effect-protocol.md](../protocol/collision-effect-protocol.md) — CollisionEffect (opcode 0x15) wire format
- [set-phaser-level-protocol.md](../protocol/set-phaser-level-protocol.md) — GenericEventForward pattern (shared by opcodes 0x0B and 0x11)
- [v5-evidence-header.md](../guides/v5-evidence-header.md) — v5 evidence header schema
