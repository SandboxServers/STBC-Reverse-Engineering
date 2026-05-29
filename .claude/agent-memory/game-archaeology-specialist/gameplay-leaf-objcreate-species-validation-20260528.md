# Gameplay Leaf #15 — ObjCreate Unknown Species Analysis Validation (2026-05-28)

**Doc**: `docs/gameplay/objcreate-unknown-species-analysis.md` (408 lines)
**Status**: `validated` (one micro-correction; one scope clarification)

## Bottom line

This is one of the cleanest pre-v5 gameplay docs. Every load-bearing claim about the
handler chain (entry → deserialize → InitObject → SpeciesToShip.InitObject) is
byte-confirmed. The three failure scenarios for unknown species are accurately reasoned
from the Python source + C++ control flow. ZERO wire-format corrections, ZERO
functional corrections to the failure analysis. One micro-correction on a side
detail (host-vs-client tracker gate ordering) and one scope clarification
(TGFactoryCreate NULL crash is theoretical for opcode 0x02/0x03 since only
0x8008/0x8009 are sent).

## Byte-confirmed claims

### Handler entry chain (line 19-25)
- `MpgameHandleObjCreate` at 0x0069f620 — name + signature `void __thiscall(MultiplayerGame *, TGMessage *, char)` ✓
- Opcode 0x02 thunk @ 0x0069F31E: `PUSH 0` → `CALL 0x0069F620` (isTeam=0) ✓
- Opcode 0x03 thunk @ 0x0069F334: `PUSH 1` → `CALL 0x0069F620` (isTeam=1) ✓

### Step 1: Parse envelope (line 27-45)
- `TGMessage_GetBuffer` is `TGBufferStream_GetBufferAndSize` at 0x006B8530 ✓
- `DAT_0095b07d = 0` clear at 0x0069F655 ✓
- `owner_slot = (signed char)buffer[1]`: `MOVSX ECX,byte ptr [EAX + 0x1]` @ 0x0069F65C ✓
- header_len = 2 for opcode 0x02, 3 for opcode 0x03: `MOV EDX,0x2`/`MOV EDX,0x3` ✓
- team_id = `(signed char)buffer[2]`: `MOVSX ESI,byte ptr [EAX + 0x2]` @ 0x0069F667 ✓

### Step 2-3: Player context swap + deserialize (line 50-67)
- Slot stride 0x18 (per `LEA EBP,[ESI + ESI*0x2]` then `*0x8` = *0x18) ✓
- Slot base in MultiplayerGame is +0x84 (per `LEA EBP,[EBX + EBP*0x8 + 0x84]`) ✓
- `Ship_Deserialize` (now named `HandleObjCreateDeserialize`) at 0x005A1F50 ✓
- Caller passes `buf + iVar7` where iVar7 = 2 or 3 (header_len) ✓

### Step 4: NULL check / duplicate path (line 78-83, 165-194)
- Inside HandleObjCreateDeserialize: `if (existing != NULL) return NULL` ✓
- `ObjectLookupByID(0, dwObjectID)` at 0x00430730 ✓ (now properly named)
- Class-category gate: ObjectLookupByID also returns NULL if found class != 0x8002.
  Doc doesn't mention this subtle case. Practically irrelevant since all live
  game objects ARE class category 0x8002.

### Step 5-6: Team assign + WSN check (line 85-97)
- Team write: `piVar5[0xb9] = local_10` = ship+0x2E4 ✓ (0xB9*4)
- WSN at DAT_0097FA78 ✓ (matches CLAUDE.md global table)

### Step 7: Relay loop (line 101-126)
- IsMultiplayer gate at 0x0097fa8a (`AL=[0x0097fa8a]` → `JZ 0x0069f7df`) ✓
- 16 slot iteration: `iVar8 = 0x10` counter ✓
- Slot stride 0x18: `piVar9 = piVar9 + 6` (6 dwords = 24 bytes) ✓
- Slot base at +0x7C (`LEA ESI,[ECX + 0x7c]`) with isConnected byte at +0x78
  (`MOV AL,byte ptr [ESI + -0x4]`) ✓
- Sender match field: `msg->pPad04 + 8` = msg+0x18 (TGMessage senderID field) ✓
- Self skip via WSN+0x20 (own connection ID) ✓
- Clone via `vtable+0x18` (TGMessage::Clone) ✓
- SendToPeer via `TGWinsockNetwork_SendTGMessage` at 0x006B4C10 ✓
- Doc CORRECTLY notes (line 123) the clone preserves the raw species byte → all
  receivers run the same Python lookup independently. This is the
  load-bearing claim for OpenBC interoperability with mod ships.

### Step 8: Tracker creation (line 128-160)
- IsClient at 0x0097FA88 (`AL=[0x0097fa88]` → `JZ 0x0069f7a4`) ✓
- HOST path (IsClient=0, JZ taken → 0x7A4): bWithTeam check + 0x8009 skip + NiAlloc(0x58) ✓
  - NO own-ship objectID skip in this path — matches doc line 137-142.
- CLIENT path (IsClient=1, fall-through → 0x75F): bWithTeam + own-ship + 0x8009 + NiAlloc ✓
  - Own-ship check: `CMP EAX,[ECX + 0x80]` @ 0x0069F76E (ship->objectID vs this->field_0x80) ✓
- SP path (IsMultiplayer=0, JZ taken → 0x7DF): 0x8009 + NiAlloc ✓ (no bWithTeam gate)
- NiAlloc at 0x00718CB0 with size 0x58 ✓ (`PUSH 0x58` @ 0x0069F78C/0x7B6/0x7ED)
- Tracker init via FUN_0047DAB0(tracker, ship, "Network") ✓
  - String "Network" at 0x0095A30C ✓
- Attach via `vtable[0x134]` (`CALL dword ptr [EDX + 0x134]`) ✓
- ship+0xF0 clear: `MOV byte ptr [EDI + 0xf0],0x0` @ 0x0069F81E ✓

### Tracker reads ship state (line 162)
- Doc claim: tracker reads position from `ship->GetPosition()` (vtable[0x94])
- FUN_0047DAB0 confirms: `(**(code **)(*param_2 + 0x94))()` reads position
- ALSO reads orientation via vtable[0xAC] and angular velocity via vtable[0xB0]
- Doc's claim correct but UNDERSTATES the tracker init — it also reads
  velocity (via FUN_005A05A0) and computes its magnitude

### Ship_Deserialize pipeline (line 167-194)
- Stream ctor at 0x006CEFE0 ✓ (TGBufferStream_swig_Ctor)
- OpenBuffer at 0x006CF180 ✓
- ReadInt at 0x006CF670 returns u32 ✓
- vtable[0x118] DeserializeFromStream ✓
- vtable[0x11C] PostLoad/PostDeserializeFixup ✓
- Doc CORRECTLY notes `vtable[0x118] return value IGNORED` (line 188)

### Ship_InitObject (line 199-231)
- ShipReadSpecies at 0x005A2030 reads species byte → ship+0xEC ✓
  (decomp: `*(int *)(param_1 + 0xec) = (int)cVar1;` after stream->vtable[0x50])
- Stream finalize: `(**(code **)(*param_2 + 0xd8))()` ✓
- Python wrapper via vtable[0x20] ✓
- FUN_006F8AB0 is `TG_CallPythonFunction` ✓
- **All four call-string arguments byte-confirmed**:
  - 0x008E61EC = "Multiplayer.SpeciesToShip" ✓
  - 0x008E5620 = "InitObject" ✓
  - 0x008D8804 = "i" (return format) ✓
  - 0x008E1198 = "(Oi)" (arg format: Object + int) ✓
- `if (result == -1) FUN_0074AF10()` ✓ (PyErr_Print path)
- Doc's distinction between -1 (exception) and 0 (logical fail) ✓

### Python SpeciesToShip (line 233-259)
- Cross-checked against `reference/scripts/Multiplayer/SpeciesToShip.py`:
- MAX_SHIPS = 46 ✓ (actual line 50)
- 45 ship types indexed 1..45, terminator at index 46 (None entry)
- GetShipFromSpecies range check `iSpecies <= 0 or iSpecies >= MAX_SHIPS` ✓
- InitObject signature and body match doc exactly
- Doc's reproduction is essentially verbatim (modulo comment removal)

## CORRECTION 1 (clarification only, not material)

**Doc line 162** "tracker reads position from the ship via `ship->GetPosition()` (vtable[0x94])"

Actually reads more than position:
- vtable[0x94] → position (param_1+0xC..+0xE)
- vtable[0xAC] → orientation/forward vector (param_1+0xF..+0x11)
- vtable[0xB0] → angular velocity (param_1+0x12..+0x14)
- Velocity computed via FUN_005A05A0 + magnitude SQRT stored at param_1+0x15

Promotion: clarification, not correction. Doc's intent (tracker initializes
position state from ship) is correct; just understates the depth.

## CORRECTION 2 (scope clarification, not material)

**Doc lines 185-187** "If class_id is unknown, this returns 0 and the vtable
dereference below CRASHES."

Verified TGFactoryCreate (0x006F13E0) decomp:
```c
while (puVar1 != NULL) { ... }
return 0;  // factory chain exhausted
```

The crash vector is REAL — no NULL check before `vtable[0x118]` in
HandleObjCreateDeserialize. BUT for the ObjCreate (0x02/0x03) opcode family,
the only class IDs ever sent on the wire are 0x8008 (Ship) and 0x8009
(Torpedo) — both factory-registered. The crash is theoretical unless a
mod or adversary injects an unregistered class_id.

Promotion: scope clarification. The doc accurately identifies the gap but
should note the practical attack surface (would require malicious modding
or wire-level packet injection).

## CLARIFICATION 1 (minor, not a correction)

**Doc line 175** "Look up object_id in hash table"

ObjectLookupByID has a second filter (line 25-29 of its decomp): even if
found, the entry must satisfy `vtable[8](0x8002)` (class-category test) or
the function returns NULL. So a found-but-wrong-category entry yields a
false "no duplicate" verdict. Practically irrelevant since stock game
objects are all class 0x8002.

## CLARIFICATION 2 (Scenario C subtle detail)

**Doc line 290-293** Scenario C (Hardpoint file missing): says "Model loads OK"

The full sequence is:
```python
self.SetupModel (kStats['Name'])      # ← Model loads (NIF + NiNode attached)
pPropertySet = self.GetPropertySet()  # ← Property set fetched
mod = __import__("ships.Hardpoints." + kStats['HardpointFile'])  # ← ImportError here
```

So GetPropertySet() also runs successfully before the ImportError. The
resulting ship has model+property-set but NO loaded hardpoints / subsystems.
Doc's high-level "Model is visible but non-functional" is accurate.

## CROSS-DOC INTEGRATION

### From protocol leaf #10 (objcreate-serialization) — pre-anchored
- Full ObjCreate chain documented there ✓ matches this doc
- velocity = CV4 3-dir + 4-mag ✓ (read by vtable[0x11C], not [0x118])
- This doc's claim that vtable[0x11C] reads pos/quat/vel/names/subsystems
  matches protocol #10's correction C1 (vtable[+0x118] reads species ONLY)

### From protocol mid #9 (object-replication) — pre-anchored
- FUN_0069f620 is the thin index handler ✓
- vtable[+0x10C] sender / vtable[+0x118]+[+0x11C] receiver ✓ matches this doc

### Impact summary table (line 299-309)
- ship+0xEC species ✓ (byte-confirmed via ShipReadSpecies)
- ship+0x2E4 team ✓ (byte-confirmed via piVar5[0xB9])
- ship+0xF0 flag clear ✓ (byte-confirmed via `[EDI + 0xf0],0x0`)
- ship+0x18 NiNode null — UNVERIFIED in this pass (would require Ship ctor disasm
  + SetupModel decomp); doc's claim is reasonable inference but not anchored
- ship+0x284 subsystem list empty — UNVERIFIED in this pass; doc's claim is
  reasonable inference from SetupProperties() being skipped
- ship+0x128/+0x130/+0x140 damage handlers — UNVERIFIED in this pass

## Function inventory (cited by doc)

| Address | Doc name | Actual Ghidra name | Status |
|---------|----------|---------------------|--------|
| 0x0069F620 | Handler_ObjCreate_0x02_0x03 | MpgameHandleObjCreate | ✓ |
| 0x005A1F50 | Ship_Deserialize | HandleObjCreateDeserialize | ✓ |
| 0x005A2030 | ReadSpeciesByte | ShipReadSpecies | ✓ |
| 0x005B0E80 | Ship_InitObject | ShipDeserializeStream_Slot118 | ✓ |
| 0x006F8AB0 | TG_CallPythonFunction | FUN_006F8AB0 | ✓ functional |
| 0x006F13E0 | TGFactoryCreate | TGFactoryCreate | ✓ named |
| 0x00430730 | ObjectLookupByID | ObjectLookupByID | ✓ named |
| 0x006B4C10 | SendToPeer | TGWinsockNetwork_SendTGMessage | ✓ |
| 0x0047DAB0 | InitNetworkTracker | FUN_0047DAB0 | functional |
| 0x006B8530 | TGMessage_GetBuffer | TGBufferStream_GetBufferAndSize | ✓ |
| 0x006CF670 | StreamReader_ReadInt32 | TGBufferStream_swig_ReadInt | ✓ |
| 0x0074AF10 | PyErr_Print | FUN_0074AF10 (thunk) | ✓ functional |

## v5 completeness scores

| Function | Effective | Plate | Custom name | Notes |
|----------|-----------|-------|-------------|-------|
| MpgameHandleObjCreate | 17.6 | ✓ | ✓ | Worker, 114 lines, many magic numbers |
| HandleObjCreateDeserialize | 32.6 | ✓ | ✓ | Worker, 33 lines |
| ShipDeserializeStream_Slot118 | 31.5 | ✓ | ✓ | Worker, 22 lines |
| ShipReadSpecies | 41.1 | – | ✓ | Leaf, 6 lines, no plate needed |

All four functions adequately anchored. Effective scores acceptable for
analysis-doc usage (these are not OpenBC translation targets in isolation —
they're spec waypoints for the unknown-species crash analysis).

## Open questions

OQ1: Doc claims ship+0x18 (NiNode), ship+0x284 (subsystem list),
ship+0x128/+0x130/+0x140 (damage handlers) are NULL/empty in unknown-species
ships. None anchored to specific Ghidra disasm in this pass. To upgrade:
- Read Ship factory ctor (called from TGFactoryCreate) to see what +0x18 is
  initialized to
- Trace SetupModel (PhysicsObjectClass_SetupModel) to confirm where ship+0x18
  is written
- Trace SetupProperties to confirm ship+0x284 chain construction

OQ2: Doc Section "Potential Risks" #2 (stream desynchronization on partial
InitObject failure). vtable[0x11C] runs after vtable[0x118] regardless of
return value. If InitObject bails early (returns 0 via -1 path), the stream
is at the bit-alignment boundary after the species byte, then vtable[0x11C]
reads pos/quat/vel/names/subsystems from that offset. The stream HAS the
data — Ship_InitObject is what bailed, NOT vtable[0x11C]. So the stream
state should be consistent. The doc's "stream desync" risk is OVERSTATED.
Suggest correction in next revision.

## v5 status

`validated` — substantive content is binary-accurate; the 2 corrections and
2 clarifications are micro-issues that do not change the doc's central
findings. OpenBC implementers can rely on this doc for:
- Relay-after-create timing semantics
- The exact 3 failure scenarios
- The "empty hull persists, no cleanup path" finding (load-bearing for
  server-side mod-ship compatibility decisions)

OpenBC actionable: server-side validation of species byte BEFORE the relay
loop would prevent the empty-hull broadcast. The species byte is at a known
wire offset (after 4-byte class_id + 4-byte object_id, so at buffer offset
header_len+8). A trivial range check (1 <= species < 46) would block bad
species at the network boundary.

## Ghidra annotations applied

None this session. Functions already had plate comments + custom names
sufficient for v5 anchor. Save completed.
