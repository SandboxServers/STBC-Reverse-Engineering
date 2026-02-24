# Opcodes 0x1D, 0x1E, 0x1F Wire Format and Handler Analysis

## Overview

These three opcodes form the **object recovery / scene transition** subsystem in Bridge Commander multiplayer. They work as a triad:

- **0x1D ObjNotFound** (OBJECT_NOT_FOUND) — client tells host "I got a message referencing object X but I don't have it"
- **0x1E RequestObj** (SEND_OBJECT_MESSAGE) — host responds with a full serialized copy of the object
- **0x1F EnterSet** (VERIFY_ENTER_SET_MESSAGE) — client tells host "my ship is entering set Y"

All three are handled by `MultiplayerGame__ReceiveMessage` (0x0069f2a0) via the jump table at 0x0069F534.

---

## Opcode 0x1D — ObjNotFound

**Handler:** `MultiplayerGame__ObjNotFoundHandler` @ 0x006a0490
**Python constant:** (none exported — internal opcode)
**Direction:** Client → Host

### Purpose

Sent by the client when it receives a message referencing an object ID that it cannot find in its local TGSceneGraph. Acts as a request: "please resend object X to me."

### Wire Format

```
[0x1D][int32: objectID]
```

| Offset | Size | Type   | Description                     |
|--------|------|--------|---------------------------------|
| 0      | 1    | byte   | Opcode = 0x1D                   |
| 1      | 4    | int32  | Object ID to locate             |

### Handler Behavior

```c
void MultiplayerGame__ObjNotFoundHandler(void *param_1) {
    // Skip opcode byte, read 4-byte object ID
    int objectID = TGBufferStream__ReadInt(stream);

    // Try to find the object locally
    int *obj = TGSceneGraph__GetObjectByID(NULL, objectID);

    if (obj == NULL) {
        // Object is ALSO not found locally — respond with opcode 0x1E (RequestObj)
        // Build: [0x1E][int32: objectID]
        // Send to connectionID 0 (host) via TGNetwork__Send
        // msg->guaranteed = 1
    }
    // If found locally, do nothing — the object exists, no recovery needed
}
```

**Key observation:** The handler only sends 0x1E back if the object is ALSO missing locally. This is correct: on a dedicated server, the host may also not have created the object yet (if it was received in a wrong order), in which case it will relay the request upward. In practice on a client-authoritative server, this is a no-op if the host has the object — the host will just serve the object via opcode 0x1E without this loopback.

**Response it sends:** `[0x1E][int32: objectID]` → sent to connectionID 0 (host), guaranteed.

---

## Opcode 0x1E — RequestObj (SEND_OBJECT_MESSAGE)

**Handler:** `MultiplayerGame__RequestObjHandler` @ 0x006a02a0
**Python constant:** `App.SEND_OBJECT_MESSAGE`
**Direction:** Client → Host, then Host → requesting Client

### Purpose

A client requests that the host resend a full object serialization for a given object ID. The host responds with a full `ObjCreate` (opcode 0x02 or 0x03) packet for that object plus any queued explosions.

### Wire Format (Request)

```
[0x1E][int32: objectID]
```

| Offset | Size | Type   | Description              |
|--------|------|--------|--------------------------|
| 0      | 1    | byte   | Opcode = 0x1E            |
| 1      | 4    | int32  | Object ID to request     |

### Handler Behavior

```c
void MultiplayerGame__RequestObjHandler(void *param_1) {
    int requestorConnID = *(int*)(param_1 + 0x0C);  // sender's connection ID
    int objectID = TGBufferStream__ReadInt(stream);

    // Find the physics object by ID
    int *obj = PhysicsObjectClass__FindByObjectID(NULL, objectID);

    if (obj == NULL) return;             // Object doesn't exist — silently drop
    if (obj[0x3b] == 0) return;          // Object not "networked" — drop

    // Gate: if DamageableObject, only send if HP >= threshold AND not dead
    // (DAT_008e5c18 is the minimum HP threshold constant, ~some small positive float)
    DamageableObject *dobj = DamageableObject__Cast(obj);
    if (dobj != NULL) {
        if (dobj->hp < DAT_008e5c18) return;   // Too damaged — don't bother sending
        if (dobj->dead_flag != 0) return;       // Already dead — don't send
    }

    // Determine opcode: 0x02 (ObjCreate) or 0x03 (ObjCreateTeam, for player ships)
    int opcode = 2;
    int *ship = TGObject__AsShip(obj);
    if (ship != NULL && Ship__IsPlayerShip(ship)) {
        opcode = 3;  // ObjCreateTeam
    }

    // Build response payload:
    // [byte: opcode=0x02/0x03]
    // [byte: player_slot]           (from GetPlayerSlotFromObjID(objID))
    // [byte: species/team]          (only present if opcode==0x03; ship[0xb9] = net type)
    // [... WriteToStream bytes ...]  (via vtable slot 0x43 = WriteToStream)

    int playerSlot = MultiplayerGame__GetPlayerSlotFromObjID(obj[1]);
    // ...

    // Send back to requestor only (not broadcast)
    TGNetwork__Send(network, requestorConnID, msg, 0);
    // msg->guaranteed = 1
    // msg->flag_0x3d = 0  (not guaranteed-receipt-notify)

    // Also replay any stored explosion data for this object
    if (dobj != NULL) {
        DamageableObject__SendExplosions_0x29(dobj, requestorConnID);
    }
}
```

### Response Format

The handler builds a standard `ObjCreate` or `ObjCreateTeam` message on the fly and sends it directly back to the requesting connection ID. The format is identical to how objects are sent during `NewPlayerInGame` (opcode 0x2A):

**Non-player objects (opcode 0x02):**
```
[0x02][byte: player_slot][... PhysicsObjectClass WriteToStream ...]
```

**Player ships (opcode 0x03):**
```
[0x03][byte: player_slot][byte: species/net_type][... PhysicsObjectClass WriteToStream ...]
```

The `WriteToStream` chain is:
```
ObjectClass -> PhysicsObjectClass -> DamageableObject -> Ship
```

This is exactly the same serialization used during initial object creation.

### DamageableObject__SendExplosions_0x29

After sending the object, the handler also replays any pending explosion events (from the `DamageableObject::explosionList` at offset `+0x13c`). These are sent as individual `0x29` (Explosion) packets, one per explosion in the list.

This ensures that if the client missed both the object creation AND its subsequent damage events, it gets a complete picture of the object's state including any in-flight explosions.

### GetPlayerSlotFromObjID

```c
int GetPlayerSlotFromObjID(int objID) {
    return (int)(objID - 0x3FFFFFFF +
                 ((objID - 0x3FFFFFFF >> 31) & 0x3FFFF)) >> 18;
}
```

This is arithmetic right-shift with sign extension — correctly handles the base offset and extracts the 6-bit player slot number. Matches the formula documented in MEMORY.md.

---

## Opcode 0x1F — EnterSet (VERIFY_ENTER_SET_MESSAGE)

**Handler:** `MultiplayerGame__EnterSetHandler` @ 0x006a05e0
**Python constant:** `App.VERIFY_ENTER_SET_MESSAGE`
**Direction:** Client → Host
**Event handler (stub):** `MultiplayerGame__EnterSetEventHandler` @ 0x006a0a20 (empty body, name="Enter game set")

### Purpose

Sent by a client when its player ship is about to enter a new TGSet (i.e., a named scene region — the in-system-warp destination). The host verifies the object exists, then transitions that ship from its current set to the named destination set.

This is part of the in-system warp flow. When a player warps from one region (set) of the game map to another, the client fires this message to notify the host to perform the set transition server-side. All other clients see the ship "disappear" from one set and "appear" in another.

### Wire Format

```
[0x1F][int32: objectID][string: setName]
```

| Offset | Size          | Type    | Description                              |
|--------|---------------|---------|------------------------------------------|
| 0      | 1             | byte    | Opcode = 0x1F                            |
| 1      | 4             | int32   | Object ID of the ship requesting transit |
| 5      | variable      | string  | Destination set name (null-terminated)   |

The string is read with `TGBufferStream__ReadString(stream, -1)` which heap-allocates the string. It is freed with `NiFree_Wrapper` before the function returns.

### Handler Behavior

```c
void MultiplayerGame__EnterSetHandler(void *param_1) {
    int objectID = TGBufferStream__ReadInt(stream);
    char *setName = TGBufferStream__ReadString(stream, -1);

    int *obj = TGSceneGraph__GetObjectByID(NULL, objectID);

    if (obj == NULL) {
        // Object not found — send back opcode 0x1E (RequestObj) to host
        // [0x1E][int32: objectID]
        // Same fallback pattern as ObjNotFound
        TGNetwork__Send(network, 0, msg, 0);  // to host
        goto cleanup;
    }

    int *ship = TGObject__AsShip(obj);
    if (ship == NULL) goto cleanup;
    if (ship[0xb4] == 0) goto cleanup;          // No warp engine subsystem
    if (*(int*)(ship[0xb4] + 0xb4) != 0) goto cleanup;  // Already in transit

    // Find the destination set by name
    int setIndex = TGSetManager__FindSetByName(&DAT_0097e9c8, setName);
    int *destSet = (setIndex >= 0) ? g_kSetManager[setIndex] : NULL;

    int *currentSet = (int*)ship[8];  // ship->currentSet (parent set pointer at +0x20)

    if (currentSet != destSet) {
        // Exit current set
        if (currentSet != NULL) {
            // vtable slot 0x58 = ExitSet (notifies current set of departure)
            (*currentSet->vtable[0x58 / 4])(ship[1]);  // pass ship's object ID
        }
        // Enter destination set
        // vtable slot 0x54 = EnterSet (adds ship to new set)
        (*destSet->vtable[0x54 / 4])(ship, ship[10]);  // ship, ship->placement
    }

cleanup:
    NiFree_Wrapper(setName);
}
```

### Set Name: The "Space" Set

The constant at `0x008d8ab8` appears immediately after `"DeleteAllMissionTimers\0"` in the string table and is referenced in the `RequestObjEventHandler` in a string comparison context. Given the surrounding code (checking if the ship's current set matches this name before sending 0x1F), this constant is the name of the default space combat set — this is the set objects inhabit when NOT inside a named sub-region. From `FUN_00408930` (mission teardown), we can see this set is managed alongside `"bridge"` and the player-specific sets, confirming it is the main space environment set.

### Who Sends 0x1F — The RequestObjEventHandler Path

`MultiplayerGame__RequestObjEventHandler` @ 0x006a07d0 is the **client-side sender** for both 0x1D and 0x1F:

```c
// Triggered by an internal event (ET_?) when a local physics object changes set
void RequestObjEventHandler(int param_1) {
    if (!g_IsMultiplayer) return;

    int *obj = TGObject__AsShip(*(param_1 + 0x0C));  // get ship from event
    if (obj == NULL || obj[0x3b] == 0) return;       // must be networked

    if (obj[0xb4] == 0 || *(obj[0xb4] + 0xb4) == 0) {
        // Ship is NOT in warp — send ObjNotFound (0x1D)
        // [0x1D][int32: shipObjID]
        // Send to "NoMe" group (all except self)
        TGNetwork__SendTGMsgToGroupByName(network, "NoMe", msg);
    } else {
        // Ship IS in warp — check if destination set != default space set
        char *currentSetName = *(char**)(obj[8] + 0x74);  // set name from object
        if (strcmp(currentSetName, DAT_008d8ab8) != 0) {  // if NOT in default space set
            // Send EnterSet (0x1F)
            // [0x1F][int32: shipObjID][string: currentSetName]
            // Send to "NoMe" group
            TGNetwork__SendTGMsgToGroupByName(network, "NoMe", msg);
        }
        // If in default space set, nothing sent — no transition needed
    }
}
```

**The key distinction:** This event handler fires when the ship's set membership changes. The branch on warp state determines WHICH opcode to send:
- Not in warp → `0x1D` (ObjNotFound — the ship teleported unexpectedly, request recovery)
- In warp AND destination is a non-default set → `0x1F` (EnterSet — notify host of warp destination)

### Set Transition Logic

The vtable calls in the EnterSet handler correspond to:
- `vtable[0x58/4]` = ExitSet — called on the ship's CURRENT set to notify departure
- `vtable[0x54/4]` = EnterSet — called on the DESTINATION set to notify arrival

The parameter passed to ExitSet is `ship[1]` (the object ID), not the ship pointer itself. The parameter passed to EnterSet is `(ship, ship[10])` — ship pointer plus placement data.

---

## Relationship Between the Three Opcodes

```
CLIENT                                  HOST
  |                                       |
  | [receives msg with unknown objID]     |
  | --> 0x1D ObjNotFound(objID) --------> |
  |                                       | [if also missing: echo 0x1E to host(0)]
  |                                       | [if found: build ObjCreate packet]
  | <-- 0x1E RequestObj (ObjCreate) ----- |
  |     (opcode 0x02 or 0x03)             |
  |     + any 0x29 explosion replays      |
  |                                       |
  | [ship begins warp to set "Multi1"]    |
  | --> 0x1F EnterSet(objID,"Multi1") --> |
  |                                       | [host: move ship from current->dest set]
```

The three opcodes form a recovery and synchronization path:
1. **0x1D** — "I'm missing an object you referenced"
2. **0x1E** — "Here is the full state of that object" (plus explosion history)
3. **0x1F** — "My ship is entering a new sub-region"

---

## OpenBC Implementation Notes

### ObjNotFound (0x1D)
- Parse: skip opcode byte + read 4-byte objectID
- On receive: look up the object locally. If found, send a full ObjCreate (0x02 or 0x03) packet back to the sender (unicast, guaranteed)
- If also not found locally: this indicates a genuine desync. Log it. Do NOT relay the 0x1D further — just attempt to create/send the object if possible

### RequestObj (0x1E)
- Parse: skip opcode byte + read 4-byte objectID
- On receive (host only): look up the object
  - If not found, drop silently
  - If found, gate on: object must be "networked" (`+0x3b` != 0), HP must be above threshold, not dead
  - Build ObjCreate/ObjCreateTeam and send to requesting connection only (NOT broadcast)
  - Re-send any pending explosion events for that object

### EnterSet (0x1F)
- Parse: skip opcode byte + read 4-byte objectID + read null-terminated string (setName)
- On receive (host): look up ship by objectID
  - If not found: send back 0x1E(objectID) to host (itself)
  - If found: validate ship has warp engine (`+0xb4`) and is not already in transit
  - Look up destination set by name in TGSetManager
  - If ship is already in dest set, no-op
  - Otherwise: call ExitSet on current set (pass objectID), then EnterSet on dest set (pass ship+placement)
- The opcode is sent by each client when its own ship changes set membership during warp
- Guaranteed delivery: yes (warp transition is critical state)

### Set Name Context
- The "default" combat space set name (at `0x008d8ab8`) is what ships inhabit during normal combat
- Named sub-sets (Multi1, Multi2, etc.) are used for in-system warp destinations
- When a ship is in the default space set, no 0x1F is sent — only when entering a non-default named set

---

## Function Addresses

| Address    | Function                                      |
|------------|-----------------------------------------------|
| 0x006a0490 | MultiplayerGame__ObjNotFoundHandler (0x1D)    |
| 0x006a02a0 | MultiplayerGame__RequestObjHandler (0x1E)     |
| 0x006a05e0 | MultiplayerGame__EnterSetHandler (0x1F)       |
| 0x006a07d0 | MultiplayerGame__RequestObjEventHandler (sender for 0x1D/0x1F) |
| 0x006a0a20 | MultiplayerGame__EnterSetEventHandler (stub, empty) |
| 0x005a2030 | GetPlayerSlotFromObjID                        |
| 0x006a7770 | MultiplayerGame__GetPlayerSlotFromObjID       |
