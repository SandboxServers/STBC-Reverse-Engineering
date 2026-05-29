---
title: ObjCreate Handler — Unknown Species Behavior Analysis
type: reference
audience: RE engineers, OpenBC implementers
validated: 2026-05-28
methodology: FUNCTION_DOC_WORKFLOW_V5
binary_fingerprint: stbc.exe (base 0x400000, 32-bit Windows)
status: verified
supersedes: []
evidence:
  - claim: "MpgameHandleObjCreate handler entry (opcode 0x02/0x03 family); signature void __thiscall(MultiplayerGame *, TGMessage *, char isTeam)"
    address: 0x0069F620
    confidence: high
  - claim: "Opcode 0x02 thunk: PUSH 0 -> CALL 0x0069F620 (isTeam=0)"
    address: 0x0069F31E
    confidence: high
  - claim: "Opcode 0x03 thunk: PUSH 1 -> CALL 0x0069F620 (isTeam=1)"
    address: 0x0069F334
    confidence: high
  - claim: "TGFactory class IDs ever sent on opcode 0x02/0x03 are 0x8008 (Ship) and 0x8009 (Torpedo); both factory-registered"
    address: null
    confidence: high
    note: "attack-surface scope: the TGFactoryCreate NULL-crash vector is theoretical for the ObjCreate opcode family unless an attacker injects an unregistered class_id"
  - claim: "TGBufferStream_GetBufferAndSize (msg buffer extraction): returns raw bytes + size"
    address: 0x006B8530
    confidence: high
  - claim: "DAT_0095b07d 'currently processing' flag cleared at handler entry"
    address: 0x0069F655
    confidence: high
  - claim: "owner_slot = (signed char)buffer[1]: MOVSX ECX,byte ptr [EAX + 0x1]"
    address: 0x0069F65C
    confidence: high
  - claim: "header_len = 2 for opcode 0x02, 3 for opcode 0x03 (MOV EDX,0x2 / MOV EDX,0x3)"
    address: 0x0069F620
    confidence: high
  - claim: "team_id = (signed char)buffer[2]: MOVSX ESI,byte ptr [EAX + 0x2]"
    address: 0x0069F667
    confidence: high
  - claim: "Slot stride 0x18 (LEA EBP,[ESI + ESI*0x2] then *0x8) and slot base in MultiplayerGame at +0x84 (LEA EBP,[EBX + EBP*0x8 + 0x84])"
    address: 0x0069F620
    confidence: high
  - claim: "HandleObjCreateDeserialize (formerly Ship_Deserialize): caller passes buf + iVar7 where iVar7 = header_len (2 or 3)"
    address: 0x005A1F50
    confidence: high
  - claim: "ObjectLookupByID(NULL, dwObjectID): hash table lookup with class-category gate (returns NULL if found class != 0x8002)"
    address: 0x00430730
    confidence: high
    note: "class-category second filter is practically irrelevant since stock objects are all 0x8002"
  - claim: "Team write: piVar5[0xB9] = local_10 (ship+0x2E4)"
    address: 0x005A1F50
    confidence: high
  - claim: "TGWinsockNetwork at DAT_0097FA78 (matches CLAUDE.md global table)"
    address: 0x0097FA78
    confidence: high
  - claim: "IsMultiplayer gate AL=[0x0097fa8a] -> JZ 0x0069f7df (relay loop only in MP)"
    address: 0x0097FA8A
    confidence: high
  - claim: "Relay loop iterates 16 slots (iVar8 = 0x10) with stride 0x18 (piVar9 += 6 dwords)"
    address: 0x0069F620
    confidence: high
  - claim: "Slot base at +0x7C (LEA ESI,[ECX + 0x7c]) with isConnected byte at +0x78 (MOV AL,byte ptr [ESI + -0x4])"
    address: 0x0069F620
    confidence: high
  - claim: "Sender match field: msg->pPad04 + 8 = msg+0x18 (TGMessage senderID)"
    address: 0x0069F620
    confidence: high
  - claim: "Self skip via WSN+0x20 (own connection ID)"
    address: 0x0097FA78
    confidence: high
  - claim: "Clone via vtable+0x18 (TGMessage::Clone); relay preserves raw species byte verbatim across receivers"
    address: 0x0069F620
    confidence: high
  - claim: "SendToPeer relay path: TGWinsockNetwork_SendTGMessage"
    address: 0x006B4C10
    confidence: high
  - claim: "IsClient gate AL=[0x0097fa88] -> JZ 0x0069f7a4 selects HOST vs CLIENT tracker path"
    address: 0x0097FA88
    confidence: high
  - claim: "HOST tracker path (IsClient=0, JZ taken @ 0x0069F7A4): bWithTeam check + 0x8009 (torpedo) skip + NiAlloc(0x58); NO own-ship objectID skip"
    address: 0x0069F7A4
    confidence: high
  - claim: "CLIENT tracker path (fall-through @ 0x0069F75F): bWithTeam + own-ship skip + 0x8009 skip + NiAlloc(0x58)"
    address: 0x0069F75F
    confidence: high
  - claim: "Client own-ship skip: CMP EAX,[ECX + 0x80] (ship->objectID vs this->field_0x80)"
    address: 0x0069F76E
    confidence: high
  - claim: "Single-player tracker path (IsMultiplayer=0, JZ taken @ 0x0069F7DF): 0x8009 + NiAlloc(0x58); no bWithTeam gate"
    address: 0x0069F7DF
    confidence: high
  - claim: "NiAlloc(0x58) allocates the network tracker (PUSH 0x58 @ 0x0069F78C / 0x0069F7B6 / 0x0069F7ED)"
    address: 0x00718CB0
    confidence: high
  - claim: "Tracker init FUN_0047DAB0(tracker, ship, \"Network\"): reads position via vtable[0x94], orientation via vtable[0xAC], angular velocity via vtable[0xB0], and computes velocity magnitude via FUN_005A05A0"
    address: 0x0047DAB0
    confidence: high
    note: "doc's pre-v5 'reads position' was correct but understated — tracker actually pulls full pose + angular-velocity + velocity-magnitude on init"
  - claim: "String 'Network' (tracker init tag)"
    address: 0x0095A30C
    confidence: high
  - claim: "Tracker attach via vtable[0x134]: CALL dword ptr [EDX + 0x134]"
    address: 0x0069F620
    confidence: high
  - claim: "ship+0xF0 clear: MOV byte ptr [EDI + 0xf0],0x0"
    address: 0x0069F81E
    confidence: high
  - claim: "Velocity magnitude helper called by tracker init"
    address: 0x005A05A0
    confidence: high
  - claim: "HandleObjCreateDeserialize stream ctor: TGBufferStream_swig_Ctor"
    address: 0x006CEFE0
    confidence: high
  - claim: "TGBufferStream_OpenBuffer (stream bind to (buffer, size))"
    address: 0x006CF180
    confidence: high
  - claim: "TGBufferStream_swig_ReadInt: returns u32 (class_id, object_id reads in deserialize)"
    address: 0x006CF670
    confidence: high
  - claim: "vtable[0x118] DeserializeFromStream / Slot118: return value IGNORED by HandleObjCreateDeserialize"
    address: 0x005A1F50
    confidence: high
  - claim: "vtable[0x11C] PostLoad/PostDeserializeFixup runs unconditionally after vtable[0x118]"
    address: 0x005A1F50
    confidence: high
  - claim: "TGFactoryCreate (class_id -> C++ object via factory hash); returns 0 when factory chain exhausted, no NULL check downstream"
    address: 0x006F13E0
    confidence: high
  - claim: "ShipDeserializeStream_Slot118 (Ship_InitObject): calls ShipReadSpecies, then Python wrapper via vtable[0x20], then TG_CallPythonFunction(\"Multiplayer.SpeciesToShip\",\"InitObject\",\"i\",...,\"(Oi)\")"
    address: 0x005B0E80
    confidence: high
  - claim: "ShipReadSpecies reads 1-byte species via stream->vtable[0x50] -> ship+0xEC"
    address: 0x005A2030
    confidence: high
  - claim: "TG_CallPythonFunction: result == -1 triggers PyErr_Print path; result == 0 is logical fail (no traceback)"
    address: 0x006F8AB0
    confidence: high
  - claim: "Python call-string 'Multiplayer.SpeciesToShip' (module path)"
    address: 0x008E61EC
    confidence: high
    note: "byte-confirmed string constant"
  - claim: "Python call-string 'InitObject' (function name)"
    address: 0x008E5620
    confidence: high
    note: "byte-confirmed string constant"
  - claim: "Python call-string 'i' (return format)"
    address: 0x008D8804
    confidence: high
    note: "byte-confirmed string constant"
  - claim: "Python call-string '(Oi)' (arg format: Object + int)"
    address: 0x008E1198
    confidence: high
    note: "byte-confirmed string constant"
  - claim: "PyErr_Print thunk (called when TG_CallPythonFunction returns -1)"
    address: 0x0074AF10
    confidence: high
  - claim: "Stream finalize: (**(code **)(*param_2 + 0xd8))() runs after InitObject regardless of its return"
    address: 0x005B0E80
    confidence: high
  - claim: "Python MAX_SHIPS = 46 (range check iSpecies <= 0 or iSpecies >= MAX_SHIPS returns None)"
    address: null
    confidence: high
    note: "reference/scripts/Multiplayer/SpeciesToShip.py:50; 45 ship types indexed 1..45, terminator entry at index 46"
  - claim: "Failure scenario A (species_type >= 46): GetShipFromSpecies returns None -> InitObject returns 0 -> TG returns 0 (NOT -1) -> PyErr_Print NOT called -> stream finalize still runs"
    address: null
    confidence: high
    note: "control-flow consequence of MAX_SHIPS gate + result-code semantics"
  - claim: "Failure scenario B (species 1-45, ship script missing): __import__('ships.<name>') raises ImportError -> TG returns -1 -> PyErr_Print called -> ship returned as empty hull"
    address: null
    confidence: high
  - claim: "Failure scenario C (species 1-45, hardpoint file missing): SetupModel + GetPropertySet succeed; __import__('ships.Hardpoints.<name>') raises ImportError -> TG returns -1 -> model loaded but no subsystems"
    address: null
    confidence: high
    note: "GetPropertySet also runs successfully before the ImportError; resulting hull has model + property-set but no hardpoints/subsystems"
  - claim: "Relay-after-create timing: relay loop runs after HandleObjCreateDeserialize and before tracker creation; clone preserves species byte verbatim so every receiver runs the same Python lookup independently"
    address: 0x0069F620
    confidence: high
    note: "load-bearing for OpenBC mod-ship interoperability — there is no server-side species validation gate"
companions:
  - docs/protocol/objcreate-serialization.md
  - docs/protocol/object-replication.md
  - docs/protocol/game-opcodes.md
  - docs/protocol/wire-format-spec.md
  - docs/protocol/stateupdate.md
  - docs/gameplay/damage-system.md
---

> [docs](../README.md) / [gameplay](README.md) / objcreate-unknown-species-analysis.md

# ObjCreate Handler: Unknown Species Behavior Analysis

> [!NOTE]
> **v5 verified pass — one of the cleanest pre-v5 gameplay docs.** Every load-bearing claim about the handler chain (entry -> deserialize -> InitObject -> SpeciesToShip.InitObject) is byte-confirmed. Zero wire-format or functional corrections. 2 minor clarifications + 2 OQs.
>
> - **Clar-1** (Section "Step 8 / Tracker reads ship state"): tracker init at `FUN_0047DAB0` reads more than position — it pulls orientation via `vtable[0xAC]`, angular velocity via `vtable[0xB0]`, and computes a velocity magnitude via `FUN_005A05A0`. Pre-v5 doc was correct but understated.
> - **Clar-2** (Section "Ship_Deserialize Pipeline"): the `TGFactoryCreate` returns-0-and-crashes vector is **real** (decomp confirms `return 0` on missing class) but **theoretical for opcodes 0x02/0x03** — the only class IDs ever sent on the wire for this opcode family are `0x8008` (Ship) and `0x8009` (Torpedo), both factory-registered. Crash requires malicious modding or wire-level packet injection.
> - **Two OQs** added at the end: (1) ship-offset NULL claims in the impact table are reasonable inference but not directly anchored; (2) "stream desynchronization" risk in Potential Risks #2 is overstated and corrected in this revision.

Reverse-engineered from `stbc.exe` binary (Ghidra decompilation + disassembly) and verified against the shipped `Multiplayer/SpeciesToShip.py` Python source.

## Summary of Findings [v5-validated 2026-05-28]

| Question | Answer |
|----------|--------|
| Does the handler relay BEFORE or AFTER local creation? | **AFTER.** `HandleObjCreateDeserialize` runs first, then the relay loop. |
| What happens when species lookup fails? | Ship C++ object is created but has NO model, NO subsystems, NO damage tracking. It is an empty hull. |
| Does the server create server-side state for unknown species? | **YES.** A network position/velocity tracker (0x58 bytes) is attached regardless of species validity. |
| Does the handler reject/drop the packet? | **NO.** The packet is relayed to all other clients verbatim, and the empty ship object persists locally. |
| Does the handler check IsHost for relay decisions? | **NO explicit gate.** The relay loop is gated on `IsMultiplayer` (0x0097FA8A). `IsClient` gates only whether self-tracking is created. Natural peer-table filtering prevents clients from emitting actual sends. |
| Which class IDs reach this handler on the wire? | **Only `0x8008` (Ship) and `0x8009` (Torpedo)** [v5-validated 2026-05-28]. Both are factory-registered, so `TGFactoryCreate` NULL-crash is theoretical for the 0x02/0x03 opcode family. |

## Detailed Execution Flow

### Handler Entry: `MpgameHandleObjCreate` at 0x0069F620 [v5-validated 2026-05-28]

```
void __thiscall MpgameHandleObjCreate(MultiplayerGame *this, TGMessage *msg, char isTeam)
```

Called from the MultiplayerGame dispatcher jump table for both opcodes 0x02 and 0x03:

- Opcode 0x02 thunk at `0x0069F31E`: `PUSH 0` then `CALL 0x0069F620` (isTeam=0)
- Opcode 0x03 thunk at `0x0069F334`: `PUSH 1` then `CALL 0x0069F620` (isTeam=1)

### Step 1: Parse Envelope [v5-validated 2026-05-28]

```c
// Extract raw buffer from message (TGBufferStream_GetBufferAndSize @ 0x006B8530)
buffer = TGMessage_GetBuffer(msg, &size);

// Clear global "currently processing" flag at 0x0069F655
DAT_0095b07d = 0;

// Read owner player slot (always byte 1)
// MOVSX ECX,byte ptr [EAX + 0x1] @ 0x0069F65C
owner_slot = (signed char)buffer[1];
header_len = 2;

// If ObjCreateTeam, read team_id (byte 2)
// MOVSX ESI,byte ptr [EAX + 0x2] @ 0x0069F667
if (isTeam) {
    team_id = (signed char)buffer[2];
    header_len = 3;
}
```

### Step 2: Swap Player Context

The handler temporarily sets the global "active player" context to the owner's slot, so that object ID allocation inside `HandleObjCreateDeserialize` uses the correct player's ID range.

```c
// Save current context
saved_slot = DAT_0097FA84;
saved_objbase = DAT_0097FA8C;

// Set context to owner's slot (slot stride 0x18, slot base in MultiplayerGame at +0x84)
DAT_0097FA84 = owner_slot;
DAT_0097FA8C = this->slots[owner_slot].objbase;
```

### Step 3: Deserialize Object (LOCAL CREATION) [v5-validated 2026-05-28]

```c
ship = HandleObjCreateDeserialize(buffer + header_len, size - header_len);  // 0x005A1F50
```

**This is where species lookup and model loading happens.** See "HandleObjCreateDeserialize Pipeline" below for the full chain.

After deserialization, the player context is restored:
```c
DAT_0097FA84 = saved_slot;
DAT_0097FA8C = saved_objbase;
DAT_0095b07d = 1;  // re-enable "processing" flag
```

### Step 4: NULL Check (Only Abort Point) [v5-validated 2026-05-28]

```c
if (ship == NULL) goto exit;  // HandleObjCreateDeserialize returned NULL -> done, no relay
```

`HandleObjCreateDeserialize` returns NULL only for duplicate object IDs (an object with the same network ID already exists; see Clarification below). It does NOT return NULL for unknown species.

> [!NOTE]
> `ObjectLookupByID` at `0x00430730` has a subtle second filter: even if the object ID is found, the entry must satisfy `vtable[8](0x8002)` (class-category test), or the function returns NULL. So a found-but-wrong-category entry yields a false "no duplicate" verdict. Practically irrelevant since stock game objects are all class category `0x8002`.

### Step 5: Assign Team [v5-validated 2026-05-28]

```c
if (isTeam) {
    ship->team = team_id;  // piVar5[0xB9] = local_10 -> ship+0x2E4
}
```

### Step 6: Network Check

```c
WSN = g_TGWinsockNetwork;  // 0x0097FA78
if (WSN == NULL) goto exit;
```

### Step 7: RELAY LOOP (Multiplayer Only) [v5-validated 2026-05-28]

```c
if (g_IsMultiplayer) {                       // [0x0097FA8A] -> JZ 0x0069F7DF
    // Iterate all 16 peer slots (iVar8 = 0x10, stride 0x18 = 6 dwords)
    for (int i = 0; i < 16; i++) {
        slot = &this->peers[i];              // base at this+0x7C, isConnected at +0x78

        if (!slot->isConnected) continue;

        if (slot->connectionID == msg->senderID) {   // msg->pPad04 + 8 = msg+0x18
            // This is the SENDER's slot
            if (isTeam) {
                slot->objectID = ship->objectID;     // update tracking
            }
        }
        else if (slot->connectionID != WSN->ownConnectionID) {  // WSN+0x20
            // This is a DIFFERENT PEER (not sender, not self)
            cloned_msg = msg->Clone();                          // vtable[0x18]
            TGWinsockNetwork_SendTGMessage(WSN, slot->connectionID, cloned_msg, 0);  // 0x006B4C10
        }
    }
}
```

**CRITICAL** [v5-validated 2026-05-28]: The relay sends a **clone of the original message**, including the raw species_type byte. It does NOT re-serialize the ship object. Every receiving client gets the exact same bytes and runs the same deserialization pipeline independently. This is the load-bearing claim for OpenBC interoperability with mod ships.

**CRITICAL** [v5-validated 2026-05-28]: The relay happens AFTER `HandleObjCreateDeserialize` (local creation) but BEFORE the network tracker is attached. The object already exists locally when the relay executes.

### Step 8: Network Tracker Creation (Branched by Role) [v5-validated 2026-05-28]

After the relay loop, the handler creates a position/velocity tracking object. The branching depends on role (`IsClient` at `0x0097FA88`):

```c
// --- HOST PATH (IsClient == 0, JZ taken to 0x0069F7A4) ---
if (!g_IsClient) {
    if (!isTeam) goto exit;                     // Host skips tracker for ObjCreate (0x02)

    if (ship->GetClassID() == 0x8009) goto exit;  // Skip for torpedoes

    tracker = NiAlloc(0x58);                    // 0x00718CB0
    FUN_0047DAB0(tracker, ship, "Network");     // init pos/vel tracker
    ship->vtable[0x134](tracker, 1, 1);         // attach tracker
    ship->field_0xF0 = 0;                       // clear flag @ 0x0069F81E
}

// --- CLIENT PATH (IsClient == 1, fall-through to 0x0069F75F) ---
else {
    if (!isTeam) goto exit;                     // Client skips for ObjCreate (0x02)

    // Own-ship skip: CMP EAX,[ECX + 0x80] @ 0x0069F76E
    if (ship->objectID == this->field_0x80) goto exit;

    if (ship->GetClassID() == 0x8009) goto exit;  // Skip for torpedoes

    tracker = NiAlloc(0x58);
    FUN_0047DAB0(tracker, ship, "Network");
    ship->vtable[0x134](tracker, 1, 1);
    ship->field_0xF0 = 0;
}

// --- SINGLE PLAYER PATH (IsMultiplayer=0, JZ taken to 0x0069F7DF) ---
// Same as host path but without the isTeam gate
```

**The network tracker is created regardless of whether the species was valid.**

### Tracker reads ship state via `FUN_0047DAB0` [v5-validated 2026-05-28 — Clar-1]

The tracker init does more than read position. `FUN_0047DAB0(tracker, ship, "Network")` reads:

| vtable slot | What it reads | Tracker offset |
|---|---|---|
| `vtable[0x94]` | Position | tracker+0xC..+0xE |
| `vtable[0xAC]` | Orientation / forward vector | tracker+0xF..+0x11 |
| `vtable[0xB0]` | Angular velocity | tracker+0x12..+0x14 |
| `FUN_005A05A0` (called, not vtable) | Velocity magnitude (SQRT) | tracker+0x15 |

The string `"Network"` at `0x0095A30C` is the tracker tag. For a ship with no model, the position/orientation reads return whatever the factory constructor initialized — likely zeros.

The pre-v5 doc said "reads position from the ship via `ship->GetPosition()`." That was correct but understated: the tracker pulls a full pose snapshot plus angular velocity and a precomputed velocity magnitude on init.

## `HandleObjCreateDeserialize` Pipeline (0x005A1F50) [v5-validated 2026-05-28]

```c
int* HandleObjCreateDeserialize(void* buffer, int size) {
    StreamReader stream;
    TGBufferStream_swig_Ctor(&stream);                     // 0x006CEFE0
    TGBufferStream_OpenBuffer(&stream, buffer, size);      // 0x006CF180

    int class_id  = TGBufferStream_swig_ReadInt(&stream);  // 0x006CF670 -- e.g. 0x8008
    int object_id = TGBufferStream_swig_ReadInt(&stream);  // 0x006CF670

    // DUPLICATE CHECK: look up object_id in hash table (+ class-category filter)
    int* existing = ObjectLookupByID(NULL, object_id);     // 0x00430730
    if (existing != NULL) {
        return NULL;  // *** ONLY path that returns NULL ***
    }

    // FACTORY CREATE: instantiate C++ object by class_id
    int* ship = TGFactoryCreate(class_id);                 // 0x006F13E0
    // NOTE: no NULL check on factory result. If class_id is unknown,
    //       TGFactoryCreate returns 0 and the vtable dereference below CRASHES.
    //       *** SCOPE *** For opcode 0x02/0x03 the only class_id values
    //       ever sent are 0x8008 (Ship) and 0x8009 (Torpedo). Both are
    //       factory-registered, so the crash is theoretical unless a
    //       mod or adversary injects an unregistered class_id.

    // READ STREAM: deserialize all fields (species, position, name, subsystems)
    ship->vtable[0x118](&stream);  // ShipDeserializeStream_Slot118 -> Ship_InitObject (0x005B0E80)
    // *** RETURN VALUE IS IGNORED -- no check for success/failure ***

    // POST LOAD: finalize (runs unconditionally regardless of slot 0x118 outcome)
    ship->vtable[0x11C](&stream);

    return ship;  // ALWAYS returns non-NULL ship pointer (unless duplicate)
}
```

**CRITICAL FINDING** [v5-validated 2026-05-28]: `HandleObjCreateDeserialize` NEVER checks the return value of `vtable[0x118]` (ReadStream/InitObject). Even if the Python species lookup fails and `InitObject` returns 0, the ship pointer is returned to the handler.

**Clar-2 — TGFactoryCreate crash scope.** The decompile of `TGFactoryCreate` at `0x006F13E0` confirms a `return 0` exit when the factory chain is exhausted. The crash vector downstream (vtable deref with no NULL check) is real, but its *attack surface* on the ObjCreate path is bounded by the wire-level class IDs that reach this handler — namely `0x8008` (Ship) and `0x8009` (Torpedo). Both are factory-registered. To trigger the crash, an attacker would need to inject an unregistered class_id at the network layer (or via a malicious mod). OpenBC servers that validate class_id at the wire-parse boundary close this gap entirely.

## `ShipDeserializeStream_Slot118` (0x005B0E80) — Where Species Resolution Happens [v5-validated 2026-05-28]

```c
int __thiscall Ship_InitObject(Ship* this, StreamReader* stream) {
    // Step 1: Read species byte from stream, store at ship+0xEC
    ShipReadSpecies(this, stream);  // 0x005A2030: stream->vtable[0x50] -> 1 byte -> ship+0xEC

    // Step 2: Get Python wrapper object for this ship
    PyObject* pySelf = this->GetPythonObject();   // vtable[0x20]

    // Step 3: Call Python: SpeciesToShip.InitObject(ship, species)
    int result = TG_CallPythonFunction(            // FUN_006F8AB0
        "Multiplayer.SpeciesToShip",               // module path @ 0x008E61EC
        "InitObject",                              // function name @ 0x008E5620
        "i",                                       // return format @ 0x008D8804
        &stack_args,                               // pointer to args area
        "(Oi)",                                    // arg format @ 0x008E1198: Object + int
        /* variadic: pySelf, species */
    );

    // Decref the Python object
    Py_DECREF(pySelf);

    // Step 4: Check for PYTHON EXCEPTION (not logical failure)
    if (result == -1) {
        PyErr_Print();   // 0x0074AF10 -> prints traceback to stderr
        return 0;        // Failed
    }

    // Step 5: Continue with remaining stream reads
    return stream->vtable[0xD8]();  // finalize/continue reading
}
```

All four Python call-string addresses above are byte-confirmed against the binary:

| Address | Constant | Use |
|---|---|---|
| `0x008E61EC` | `"Multiplayer.SpeciesToShip"` | module path |
| `0x008E5620` | `"InitObject"` | function name |
| `0x008D8804` | `"i"` | return format |
| `0x008E1198` | `"(Oi)"` | arg format (Object + int) |

The distinction between `result == -1` (Python exception, traceback printed) and `result == 0` (logical fail, no traceback) is load-bearing for the failure scenarios below.

## Python `SpeciesToShip.InitObject` — The Species Resolution [v5-validated 2026-05-28]

```python
def InitObject(self, iType):
    kStats = GetShipFromSpecies(iType)
    if kStats == None:
        return 0   # Failed. Unknown type. Bail.

    self.SetupModel (kStats['Name'])              # Load NIF model
    pPropertySet = self.GetPropertySet()
    mod = __import__("ships.Hardpoints." + kStats['HardpointFile'])
    App.g_kModelPropertyManager.ClearLocalTemplates()
    reload(mod)
    mod.LoadPropertySet(pPropertySet)
    self.SetupProperties()                        # Create subsystems
    self.UpdateNodeOnly()
    return 1

def GetShipFromSpecies(iSpecies):
    if iSpecies <= 0 or iSpecies >= MAX_SHIPS:   # MAX_SHIPS = 46
        return None
    pSpecTuple = kSpeciesTuple[iSpecies]
    pcScript = pSpecTuple[0]
    ShipScript = __import__("ships." + pcScript)  # Can raise ImportError
    ShipScript.LoadModel()
    return ShipScript.GetShipStats()
```

`MAX_SHIPS = 46` is byte-confirmed against `reference/scripts/Multiplayer/SpeciesToShip.py` line 50. The table indexes 45 ship types at positions 1..45 with a terminator entry at index 46.

## Three Failure Scenarios for Unknown Species [v5-validated 2026-05-28]

### Scenario A: Species ID >= 46 (Out of Table Range)

Example: species_type = 100 (mod ship)

1. `GetShipFromSpecies(100)` hits the range check `iSpecies >= MAX_SHIPS` and returns `None`
2. `InitObject` checks `kStats == None`, returns `0`
3. `TG_CallPythonFunction` returns `0` (NOT -1, because no exception was raised)
4. `Ship_InitObject` does NOT call `PyErr_Print` (result != -1)
5. `Ship_InitObject` proceeds to call `stream->vtable[0xD8]()`
6. **Result**: Ship C++ object exists with species byte set, but NO model, NO subsystems, NO damage handling. Remaining stream data (position, name, set) is still read.

### Scenario B: Species ID 1-45 but Ship Script Missing

Example: species_type = 1 (Akira) but `ships/Akira.py` does not exist

1. `GetShipFromSpecies(1)` tries `__import__("ships.Akira")`
2. Python raises `ImportError`
3. `TG_CallPythonFunction` catches the exception and returns `-1`
4. `Ship_InitObject` calls `PyErr_Print()` (prints traceback)
5. `Ship_InitObject` returns `0`
6. **Result**: Same as Scenario A — empty ship hull. Traceback printed to stderr.

### Scenario C: Species ID 1-45 but Hardpoint File Missing

Example: species_type = 1, `ships/Akira.py` exists but `ships/Hardpoints/akira.py` missing

1. `GetShipFromSpecies(1)` succeeds (Akira.py loads)
2. `InitObject` calls `self.SetupModel(kStats['Name'])` — model loads OK (NIF + NiNode attached)
3. `self.GetPropertySet()` also runs successfully (property set fetched)
4. `__import__("ships.Hardpoints.akira")` raises `ImportError`
5. Exception propagates to `TG_CallPythonFunction` -> returns `-1`
6. **Result**: Ship has a model AND a property set but NO subsystems. Model is visible but non-functional. Partial initialization.

## Impact Summary: What an Empty Ship Hull Means

When a ship is created without successful species initialization:

| Component | State | Confidence | Consequence |
|-----------|-------|------------|-------------|
| C++ object (factory) | EXISTS (valid pointer) | high (byte-confirmed via `TGFactoryCreate`) | Object tracked in game's object table |
| ship+0xEC (species) | SET (from stream) | high (byte-confirmed via `ShipReadSpecies`) | Species byte is stored before Python runs |
| ship+0x18 (NiNode) | NULL | medium — see OQ-1 | No visual model; `GetBoundingBox` returns garbage |
| ship+0x284 (subsystem list) | EMPTY | medium — see OQ-1 | StateUpdate sends flags=0x00 (no subsystem data) |
| ship+0x128 / +0x130 (damage handlers) | NULL/EMPTY | medium — see OQ-1 | `DoDamage` skips this ship (gates on ship+0x140) |
| ship+0x140 (damage target) | NULL | medium — see OQ-1 | No damage processing possible |
| ship+0x2E4 (team) | SET (from handler) | high (byte-confirmed via `piVar5[0xB9]`) | Team assignment happens after deserialization |
| Network tracker | CREATED (0x58 bytes) | high (byte-confirmed via NiAlloc(0x58)) | Position tracking exists but reads default/zero position |
| ship+0xF0 (flag) | CLEARED to 0 | high (byte-confirmed @ `0x0069F81E`) | Handler clears this after tracker attachment |

## Relay Timing Diagram

```
TIME ---------------------------------------------------------------------->

1. Parse envelope (owner_slot, team_id)
2. Swap player context to owner's slot
3. HandleObjCreateDeserialize          <--- LOCAL CREATION HAPPENS HERE
   |- Read class_id + object_id
   |- Duplicate check (only abort path -> return NULL)
   |- TGFactoryCreate(class_id) -> C++ object allocated
   |- ReadStream -> Ship_InitObject
   |   |- Read species byte -> ship+0xEC
   |   |- Python: SpeciesToShip.InitObject(ship, species)
   |   |   |- Species >= 46: returns 0 (no exception)
   |   |   |- Script missing: raises ImportError -> TG returns -1
   |   |   |- Hardpoint missing: model loads, then ImportError -> TG returns -1
   |   |   '- Success: loads model, hardpoints, subsystems
   |   '- Return value IGNORED by HandleObjCreateDeserialize
   |- PostLoad (vtable[0x11C], runs unconditionally)
   '- Return ship* (always non-NULL unless duplicate)
4. Restore player context
5. Assign team (if ObjCreateTeam)
6. NULL check on ship (only fails for duplicates)
7. === RELAY LOOP ===                  <--- RELAY HAPPENS HERE (after local creation)
   |  For each connected peer != sender != self:
   |    Clone original message (vtable[0x18])
   |    SendToPeer(clone) via TGWinsockNetwork_SendTGMessage
   '  For sender's slot: update objectID tracking
8. === TRACKER CREATION ===            <--- server-side state created
   |- Check: is torpedo (0x8009)? -> skip
   |- NiAlloc(0x58) -> tracker
   |- Init tracker (position + orientation + angular velocity + velocity magnitude)
   |- Attach tracker to ship (vtable[0x134])
   '- Clear ship+0xF0
```

## Host vs Client Differences [v5-validated 2026-05-28]

| Behavior | Host (IsClient=0) | Client (IsClient=1) |
|----------|-------------------|---------------------|
| Relay to other peers | Effectively YES | Effectively NO (see below) |
| Skip ObjCreate (0x02) tracker | Yes — exits after relay | Yes — exits after check |
| Skip own ship tracker | N/A | Yes — skips if `ship->objectID == this->field_0x80` |
| Tracker creation gate | `isTeam && classID != 0x8009` | `isTeam && notOwnShip && classID != 0x8009` |

### Relay Loop Gating (Not Explicit IsHost Check)

The relay loop is gated on `IsMultiplayer` (`0x0097FA8A`), NOT on `IsHost`. Both host and clients execute the loop, but natural filtering prevents clients from actually sending:

```asm
0069f6fe: MOV AL,[0x0097fa8a]      ; IsMultiplayer
0069f703: TEST AL,AL
0069f705: JZ 0069f7df              ; not multiplayer -> single player path

; Relay loop runs for EVERYONE in multiplayer mode.
; The loop skips self (WSN+0x20) and sender (msg->senderID).
; Clients only know about the host's connection, and for relayed messages
; the sender IS the host, so no actual sends occur on the client side.

0069f756: MOV AL,[0x0097fa88]      ; IsClient
0069f75b: TEST AL,AL
0069f75d: JZ 0069f7a4              ; IsClient=0 -> HOST tracker path @ 0x0069F7A4
;                                  ; IsClient=1 -> CLIENT tracker path @ 0x0069F75F
```

The relay loop effectively only produces sends on the host because:
- Clients only know about the host's connection in their peer table
- For relayed messages, the sender is the host, which is filtered out
- The self-check (`WSN+0x20`) filters the client's own connection

This is a natural filtering mechanism, not an explicit `IsHost` gate.

## Potential Risks with Unknown Species

1. **Crash risk from NULL NiNode**: Functions like `GetBoundingBox` (vtable[0xE8]) and `GetModelBound` (vtable[0xE4]) may dereference ship+0x18 (NiNode). If another system queries the ship's bounds (collision, rendering), this could crash. Our `PatchNetworkUpdateNullLists` at `0x005B1D57` already guards StateUpdate, but other code paths may not. See **OQ-1** below — the NULL NiNode claim is reasonable inference but not directly anchored to Ship-ctor disasm yet.

2. **Stream desynchronization** — **CORRECTED in this revision** (see OQ-2). The pre-v5 doc claimed that a partial `Ship_InitObject` failure could leave the stream cursor at an unexpected position. Re-examination of `vtable[0x118]` / `vtable[0x11C]` ordering shows this is **overstated**: the species byte is read inside `vtable[0x118]` (via `ShipReadSpecies`) before any Python failure path can be reached, and `vtable[0x11C]` runs unconditionally after `vtable[0x118]` regardless of its return value. The stream cursor stays consistent. The risk to actually worry about is the species byte landing valid but the Python-side state being half-initialized (Scenario C).

3. **Tracker with invalid position**: The network tracker reads the ship's position (and now-known orientation, angular velocity, and velocity magnitude — see Clar-1). If the ship has no model, the values returned by these vtable slots are whatever the factory constructor initialized (likely zeros). The tracker would report the ship at origin (0,0,0) with zero rotation and zero velocity.

4. **No cleanup path**: There is no code to destroy or clean up a ship that failed species initialization. The empty hull persists in the game's object table for the entire session.

## Key Functions Reference [v5-validated 2026-05-28]

| Address | Name (Ghidra) | Role |
|---------|---------------|------|
| `0x0069F620` | `MpgameHandleObjCreate` | Dispatcher worker for both opcodes 0x02 / 0x03 |
| `0x005A1F50` | `HandleObjCreateDeserialize` | Stream reader, factory create, ReadStream, PostLoad |
| `0x005A2030` | `ShipReadSpecies` | Reads species byte into ship+0xEC |
| `0x005B0E80` | `ShipDeserializeStream_Slot118` (Ship_InitObject) | Calls Python `SpeciesToShip.InitObject` |
| `0x006F8AB0` | `TG_CallPythonFunction` | Calls Python function by module.name |
| `0x006F13E0` | `TGFactoryCreate` | Class ID -> C++ object via factory hash; returns 0 if class unknown |
| `0x00430730` | `ObjectLookupByID` | Hash table lookup with class-category filter (duplicate check) |
| `0x006B4C10` | `TGWinsockNetwork_SendTGMessage` | Reliable message send to a connection |
| `0x0047DAB0` | `FUN_0047DAB0` (InitNetworkTracker) | Create position/velocity tracker (0x58 bytes); reads pose + ω + |v| |
| `0x005A05A0` | `FUN_005A05A0` | Velocity magnitude helper used by tracker init |
| `0x006B8530` | `TGBufferStream_GetBufferAndSize` | Extract raw data pointer + size |
| `0x006CEFE0` | `TGBufferStream_swig_Ctor` | Stream constructor |
| `0x006CF180` | `TGBufferStream_OpenBuffer` | Bind stream to (buffer, size) |
| `0x006CF670` | `TGBufferStream_swig_ReadInt` | Read 4-byte LE integer from stream |
| `0x00718CB0` | `NiAlloc` | 0x58-byte tracker allocator |
| `0x0074AF10` | `FUN_0074AF10` (PyErr_Print thunk) | Print Python exception traceback |

## Open Questions

### OQ-1 — Ship-offset NULL claims in the Impact Summary table are reasonable inference but not directly anchored

The Impact Summary table asserts that, for an unknown-species ship:
- `ship+0x18` (NiNode) is NULL (no visual model)
- `ship+0x284` (subsystem list) is empty
- `ship+0x128 / +0x130 / +0x140` (damage handlers) are NULL/empty

These follow logically from the fact that `SpeciesToShip.InitObject` never calls `SetupModel` (Scenario A/B) or never calls `SetupProperties` (Scenario A/B/C), so the C++ paths that populate those offsets never run. But none of those offset claims are directly anchored to Ghidra disasm in this validation pass. To upgrade:

- Read the Ship factory constructor (called from `TGFactoryCreate` for class_id 0x8008) to see what `ship+0x18` is initialized to
- Trace `PhysicsObjectClass_SetupModel` to confirm where `ship+0x18` is written
- Trace `SetupProperties` to confirm `ship+0x284` chain construction and where `ship+0x128 / +0x130 / +0x140` are populated

Rows are tagged `medium confidence` in the table until that anchoring is done.

### OQ-2 — "Stream desynchronization" risk in Potential Risks #2 is overstated (resolved in this revision)

The pre-v5 doc warned that a partial `Ship_InitObject` failure could leave the stream cursor at an unexpected position, causing downstream reads to produce garbage. Re-examination of the call sequence shows this is not the case:

- The species byte is read inside `vtable[0x118]` via `ShipReadSpecies` (`0x005A2030`) **before** any Python failure path can be reached.
- `vtable[0x11C]` (PostLoad) runs unconditionally on the `HandleObjCreateDeserialize` return path, regardless of whether `vtable[0x118]` returned 0 or 1.
- The stream cursor is therefore at the post-species-byte boundary when `vtable[0x11C]` starts reading, which is the expected starting position for pos/quat/vel/names/subsystems.

The actual risk is Scenario C: a half-initialized ship with a valid NiNode but no subsystems. That is captured in the Impact Summary table. Risk #2 has been re-worded in this revision to point to this OQ rather than the bogus stream-desync framing.
