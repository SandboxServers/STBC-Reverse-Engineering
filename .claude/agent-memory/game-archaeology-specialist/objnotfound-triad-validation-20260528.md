---
name: objnotfound-triad-validation-20260528
description: Protocol doc #18 (leaf) — objnotfound-requestobj-enterset wire-format validation. Status: partial. 3 material corrections (string encoding length-prefix not null-term, "warp" not "space" set name, DAT_008e5c18 is FLT_MAX not "small threshold"). 2 address-mapping corrections. Foundation cascade holds. 5 functions renamed + 5 plate comments + 2 data plate comments.
metadata:
  type: project
  date: 2026-05-28
  family: protocol
  doc-number: 18-leaf
  status: partial
---

# Protocol Doc #18 — objnotfound-requestobj-enterset-wire-format.md (LEAF, v5 validation)

**Doc:** `docs/protocol/objnotfound-requestobj-enterset-wire-format.md`
**Scope:** 3 opcodes (0x1D / 0x1E / 0x1F) + 1 client-side event sender + 1 stub event handler
**Verdict:** `partial` — material wire-format and address corrections needed; semantic intent is correct everywhere.

## TL;DR for tracker

`partial` because 3 wire/value corrections + 2 address-mapping corrections + 1 vtable terminology clarification + 1 corrected handler interpretation. ZERO opcode-jump-table errors. ZERO routing/relay errors. The doc's "0x1E sends back to requestor, 0x1D loops to host(0), 0x1F two-modes" is structurally correct.

Foundation anchors all hold: dispatcher 0x0069F2A0, jump-table 0x0069F534, "NoMe" group at DAT_008e5528, TGNetwork singleton at DAT_0097fa78, "UNKNOWN" allocator name at 0x008d858c.

## Confirmed Claims (byte-by-byte / address-by-address)

| Claim | Address / Evidence | Confidence |
|---|---|---|
| MpgameHandleMessage jump-table @ 0x0069F534, opcode 0x1D thunk → 0x0069f4f5 → 0x006a0490 | jump-table read; bytes 108..111 = `f5 f4 69 00` (idx 27 = opcode 0x1D - 2) | high |
| Opcode 0x1E thunk → 0x0069f51d → 0x006a02a0 | bytes 112..115 = `1d f5 69 00` (idx 28) | high |
| Opcode 0x1F thunk → 0x0069f509 → 0x006a05e0 | bytes 116..119 = `09 f5 69 00` (idx 29) | high |
| 0x1D wire format `[0x1D][int32 objectID]` | disasm 0x006a04ee=ReadInt, then for relay 0x006a0535=WriteChar(0x1e), 0x006a0540=WriteInt | high |
| 0x1D relay target = connection 0 (host) | disasm 0x006a058b: `PUSH 0, PUSH ESI(msg), PUSH 0(target=host)` → CALL SendTGMessage | high |
| 0x1D allocates 64-byte TGMessage via "UNKNOWN" class | disasm 0x006a0551: `PUSH 0x40, PUSH 0x8d858c` (s_UNKNOWN) | high |
| 0x1D sets `msg+0x3a = 1` (guaranteed flag) | disasm 0x006a0592: `MOV byte ptr [ESI + 0x3a], 0x1` | high |
| 0x1E reads `nTargetID = stream+0xc` | disasm 0x006a02dd: `MOV EAX, dword ptr [ECX + 0xc]` | high |
| 0x1E "is networked" gate uses obj+0xec (NOT +0x3b in bytes — it's piVar4[0x3b] = byte offset 0xec) | disasm 0x006a032f: `MOV EAX, dword ptr [ESI + 0xec]` | high |
| 0x1E HP-sentinel gate: `DAT_008e5c18 <= ship[+0x14c] && ship[+0x150] == 0` | disasm 0x006a034c-0x006a036b: FLD float ptr [EBX + 0x14c]; FCOMP [008e5c18]; FNSTSW; JNZ → cleanup; then byte [EBX + 0x150] != 0 → cleanup | high |
| Cast to Ship via `CastToShipClass` = IsA(0x8008) | FUN_005ab670 calls vtable[+8](0x8008) | high |
| Opcode byte 0x02 (non-player) or 0x03 (player ship) header decision | disasm 0x006a0392/0x006a039e: `MOV byte ptr [ESP + 0x50], 0x3` vs `MOV byte ptr [ESP + 0x50], 0x2` | high |
| `payload[1] = GetPlayerSlotFromObjID(obj+4)` | disasm 0x006a03ab: `CALL 0x006a19a0` after PUSH obj+4 | high |
| 0x03 opcode: `payload[2] = ship+0x2e4` (team/species byte) | disasm 0x006a03b9: `MOV EAX, dword ptr [EBP + 0x2e4]`; 0x006a03bf: `MOV byte ptr [ESP + 0x52], AL` | high |
| Object WriteToStream vtable slot 0x10c (byte) = slot 67 = "0x43/4 method" | disasm 0x006a03d4: `CALL dword ptr [EDX + 0x10c]` (EDX = *ESI = obj vtable) | high |
| 0x1E sends to nTargetID (sender only, NOT broadcast) | disasm 0x006a0596: `PUSH 0, PUSH ESI(msg), PUSH EDI(nTargetID), CALL SendTGMessage`. Note EDI was loaded with sender ID | high |
| 0x1E sets `msg+0x3a = 1` (guaranteed) + `msg+0x3d = 0` (no notify) | disasm 0x006a041a, 0x006a041e | high |
| 0x1E replays explosions via SendExplosions_0x29 only if was-a-DamageableObject | disasm 0x006a042f: `TEST EBX, EBX` (EBX = was-DamageableObject result); `JZ 0x006a043b` (skip); else 0x006a0436: `CALL DamageableObject__SendExplosions_0x29` | high |
| `DamageableObject__SendExplosions_0x29` walks list at obj+0x13c, emits one 0x29 packet per entry | FUN_00595c60 decompile: `iVar1 = *(int *)(*(int *)(param_1 + 0x13c) + 0x14);` then loop writing 0x29 + CompressedVector4 + CF16 + CF16 | high |
| 0x1F wire format `[0x1F][int32 objectID][lenpfx str setName]` | disasm 0x006a0660+: ReadInt then `FUN_006d2370(0xffffffff)` | high |
| 0x1F NULL-found path: relay `[0x1E][int32 objectID]` to host (target=0) | decompile confirmed identical pattern to 0x1D fallback | high |
| 0x1F warp-engine gate: ship+0x2d0 (subsystem ptr) AND *(ship+0x2d0+0xb4) == 0 | decompile of FUN_006a05e0 | high |
| 0x1F set-lookup uses TGSetManager array at `DAT_0097e9c8` | `*(int **)(DAT_0097e9c8 + iVar6 * 4)` | high |
| 0x1F ExitSet vtable slot @ +0x58 (slot 22) on current set, arg = ship+4 (obj ID) | `(**(code **)(*piVar1 + 0x58))(*(undefined4 *)(iVar5 + 4))` | high |
| 0x1F EnterSet vtable slot @ +0x54 (slot 21) on dest set, args = (ship, ship+0x28) | `(**(code **)(*piVar7 + 0x54))(iVar5, *(undefined4 *)(iVar5 + 0x28))` | high |
| Set name heap-freed via NiFree (FUN_00718cf0 = thunk to FUN_00717960) | decompile end of FUN_006a05e0 | high |
| 0x1F client-side sender at 0x006a07d0 sends to "NoMe" group (NOT to host=0) | decompile + DAT_008e5528 = "NoMe" string | high |
| 0x1F sender branch: warp+non-"warp"-setName → 0x1F; not-warp → 0x1D | decompile with strcmp against DAT_008d8ab8 | high |
| MultiplayerGame__EnterSetEventHandler @ 0x006a0a20 IS a single-RET empty stub | created function, body_size=3 (just RETN) | high |
| GetPlayerSlotFromObjID formula `(objID - 0x3FFFFFFF + ((objID - 0x3FFFFFFF >> 31) & 0x3FFFF)) >> 18` | FUN_006a19a0 decompile matches doc exactly | high |
| TGNetwork singleton at DAT_0097fa78 (UtopiaModule+0x78) | all 5 handlers load EDI/EAX from this address | high |

## Triage block (corrections / clarifications / refinements / open questions)

### C1 — String encoding: LENGTH-PREFIXED, NOT null-terminated [severity: HIGH — wire format]

**Prior claim:** Doc § "Wire Format" (line 197): "The string is read with `TGBufferStream__ReadString(stream, -1)` which heap-allocates the string."

Doc § "Wire Format" table (line 195): "`variable | string | Destination set name (null-terminated)`"

**Binary truth:** The string is encoded as `[uint32 length][raw bytes payload]` — NO null terminator on the wire.

**Evidence:** `TGBufferStream__ReadString_HeapAlloc` (FUN_006d2370) decompile:
```c
iVar1 = (**(code **)(*param_1 + 0x68))();    // vtable+0x68 = ReadInt → length
if (iVar1 < 1) return 0;
uVar2 = FUN_00718cb0(iVar1);                 // heap alloc length bytes
(**(code **)(*param_1 + 0x10))(uVar2, iVar1); // vtable+0x10 = ReadBytes raw
return uVar2;
```

Symmetric write side (`TGBufferStream__WriteString_LenPrefixed`, FUN_006d23c0):
```c
// First strlen via DO-WHILE-NULL loop
(**(code **)(*param_1 + 0x6c))(~uVar2);      // vtable+0x6c = WriteInt → length prefix
(**(code **)(*param_1 + 0x14))(param_2, ~uVar2); // vtable+0x14 = WriteBytes raw payload
```

**Impact:** The wire format row in the table needs the size column changed from "variable" to a 2-column row breakdown:
```
| 5      | 4        | uint32 LE | Length of setName (call it N)            |
| 9      | N        | bytes     | setName payload (raw, no null terminator) |
```

Also the heap-alloc length matches the wire-prefix exactly (no off-by-one for null term).

### C2 — DAT_008d8ab8 is "warp", NOT "default space combat set name" [severity: HIGH — semantic]

**Prior claim:** Doc § "Set Name: The 'Space' Set" (line 244-245): "The constant at `0x008d8ab8` ... is the name of the default space combat set — this is the set objects inhabit when NOT inside a named sub-region."

**Binary truth:** `inspect_memory_content` at 0x008d8ab8 returns:
```
"warp\0\0\0\0ShipClass\0\0\0CreateShip\0\0..." 
```
The string IS the literal 5 bytes `"warp\0"`. The next string in the rdata block is "ShipClass" — not "DeleteAllMissionTimers" as the doc claims appears immediately after.

**Impact on doc § "Who Sends 0x1F" (line 266-272):** The logic is INVERTED in meaning:
- Doc text reads: "if currentSetName != 'space-default' → send 0x1F"
- Actual binary: "if currentSetName != 'warp' → send 0x1F"

So 0x1F is sent when the ship is in warp BUT its current set is NOT the default warp-tunnel set ("warp"). I.e., 0x1F is sent during warp transition to/from named warp-target sub-sets. The 0x1D-not-in-warp branch and the 0x1F-in-warp-non-default-set branch are correctly described structurally — only the "default" set's actual name is wrong.

### C3 — DAT_008e5c18 is FLT_MAX, NOT a "small positive threshold" [severity: MEDIUM — value-of-constant, doesn't break wire format]

**Prior claim:** Doc line 97 comment: "`(DAT_008e5c18 is the minimum HP threshold constant, ~some small positive float)`"

**Binary truth:** `read_memory` at 0x008e5c18 returns bytes `ff ff 7f 7f` = float 3.4028235e+38 = **FLT_MAX** (largest finite float).

**Mechanism (confirmed via DamageableObject ctor FUN_00590cb0 + damage app FUN_00592c00):**
- Ctor initializes `dobj+0x14c = DAT_008e5c18` (FLT_MAX) and `dobj+0x150 = 0` (alive).
- Damage application decrements `dobj+0x14c` below FLT_MAX as damage is taken.
- When killed: `dobj+0x14c` is RESET to FLT_MAX simultaneously with `dobj+0x150 = 1`.

**Effective gate semantics:** `(DAT_008e5c18 <= dobj[+0x14c]) AND (dobj[+0x150] == 0)` evaluates true ONLY when the object is at the "full health sentinel" AND not flagged dead. So the gate actually rejects ANY damaged object, not just "below some small threshold". The semantic intent in the doc is CORRECT ("don't send badly damaged objects"), but the threshold is FLT_MAX, meaning the bar is "must be UNDAMAGED" — much stricter than the doc implies.

**Impact:** Replace doc's "if HP < threshold return // Too damaged" with "if HP has been damaged at all OR dead-flag is set, return". For OpenBC implementation, the gate is effectively: "only re-send an object that hasn't taken any damage since creation".

### C4 — Address-mapping table swap: GetPlayerSlotFromObjID is FUN_006a19a0, NOT 0x005a2030 [severity: MEDIUM — address table]

**Prior claim:** Doc § "Function Addresses" (line 359): "`0x005a2030 | GetPlayerSlotFromObjID`"

**Binary truth:**
- 0x005a2030 IS `ShipReadSpecies` (a 2-vtable-call ship setup function; does NOT compute slot from objID).
- 0x006a19a0 IS the actual `GetPlayerSlotFromObjID` (formula `(objID - 0x3FFFFFFF + ((objID - 0x3FFFFFFF >> 31) & 0x3FFFF)) >> 18`). The doc's pseudocode on line 162-166 is correct and matches FUN_006a19a0.

**Impact:** Doc's table row needs `0x005a2030` removed and `0x006a19a0` correctly mapped.

### C5 — `MultiplayerGame__GetPlayerSlotFromObjID` at 0x006a7770 is NOT a slot-extractor — it's the INVERSE [severity: LOW — naming clarification]

**Prior claim:** Doc § "Function Addresses" line 360: `0x006a7770 | MultiplayerGame__GetPlayerSlotFromObjID`. Doc body line 117: `int playerSlot = MultiplayerGame__GetPlayerSlotFromObjID(obj[1]);`

**Binary truth:** FUN_006a7770 is `MakeObjIDFromPlayerSlot` (the INVERSE operation):
```c
*(int *)(param_1 + 0x10) = param_2 * 0x40000 + 0x3fffffff;
```
This constructs an obj ID FROM a player slot (multiplies by 0x40000 = 2^18, adds the 0x3FFFFFFF base). It's used in player-init context, not in objID-decoding.

The 0x1E handler decompile calls `FUN_006a19a0` at 0x006a03ab to compute `payload[1] = playerSlot from obj+4`. That call goes to GetPlayerSlotFromObjID (correctly named in C4), NOT to FUN_006a7770.

**Impact:** Drop the 0x006a7770 row from the doc's "Function Addresses" — it's NOT used by these handlers. Or relabel it `MakeObjIDFromPlayerSlot` and move it to a separate "related but not called" annex.

### Clar1 — Vtable index notation: "0x58/4 = ExitSet" should clarify "byte offset 0x58 = slot 22" [severity: LOW — naming consistency]

Doc § "Set Transition Logic" (line 284-286):
> `vtable[0x58/4] = ExitSet`
> `vtable[0x54/4] = EnterSet`

This is correct math (0x58/4 = 22, 0x54/4 = 21) but inconsistent with the rest of the doc family (e.g., `vtable[+0x10c]` style in 0x1E handler). Recommend standardizing as "vtable byte-offset 0x58 = slot 22" OR "vtable[+0x58]" for consistency.

### Clar2 — IsLocalPlayerShip is "host-mode-aware", not strictly "the local player's ship" [severity: LOW — semantic precision]

Doc § "Handler Behavior" line 107: `if (ship != NULL && Ship__IsPlayerShip(ship)) opcode = 3;`

**Binary truth:** `IsLocalPlayerShip` (FUN_005ae140) branches on `DAT_0097fa89` (IsHost flag):
- On HOST (`DAT_0097fa89 != 0`): returns TRUE for ANY ship with `ship+0x2e4 != 0` (i.e., has a team ID).
- On CLIENT: returns TRUE only if `FUN_004069b0() == param_1` (the local player's own ship).

**Impact:** On the dedicated server, opcode 0x03 is chosen for EVERY player ship in the game (any ship with team_id != 0), not just one "local" ship. The label `IsLocalPlayerShip` is misleading; conceptually it's "is-this-a-team-ship-from-host-perspective". For OpenBC, the relevant heuristic when serving from a dedicated server is "ship+0x2e4 != 0 → emit 0x03 with team byte". The doc's pseudocode is structurally correct; readers just need to understand the host-mode dual behavior.

### R1 — Cast to DamageableObject naming [severity: LOW — code reading aid]

Doc body line 99 reads:
```c
DamageableObject *dobj = DamageableObject__Cast(obj);
```

The actual function in the binary is `CastToDamageableObject` (FUN_00590b20, IsA 0x8007). The decompile name is consistent with the `CastToShipClass` (IsA 0x8008) sibling. Cosmetic — doc's pseudocode is illustrative not literal.

### R2 — "UNKNOWN" allocator string is not a placeholder [severity: LOW — reader confusion]

The string at `0x008d858c` is `"UNKNOWN"` and is used as the class-name argument to the TGAlloc/TGFactory path (`FUN_00717b70(size)` + `FUN_00718010(name, flag)`). It is the LITERAL class name used when allocating a generic TGMessage from a "no-class" pool — not a placeholder for "we don't know the class". The same string is used by 0x1D, 0x1E, 0x1F, 0x29 handlers, and NewPlayerInGameHandler. Worth a one-line note in the doc to prevent reader confusion that "UNKNOWN" means "type still TBD".

### OQ1 — What does the registered SWIG name for FUN_006a0a20 look like? [open]

The empty stub at 0x006a0a20 has a single DATA xref from FUN_0069efe0 at 0x0069eff9 (the SWIG handler registration). The doc names it "Enter game set" but I did not verify the actual registration string. To resolve, decompile FUN_0069efe0 and read the string passed to whatever registration call references 0x006a0a20.

### OQ2 — TGFactory class IDs 0x8003 / 0x8006 / 0x8007 / 0x8008 [open]

`FUN_00434e00` looks up object by ID with class-tag `0x8003`; `FUN_0059fc60` uses `0x8006`; `CastToDamageableObject` checks `0x8007`; `CastToShipClass` checks `0x8008`. The mapping is presumably:
- 0x8003 = generic scene graph object (TGObject?)
- 0x8006 = PhysicsObjectClass
- 0x8007 = DamageableObject
- 0x8008 = Ship
This should be cross-referenced against `docs/engine/rtti-class-catalog.md` to confirm.

## TGFactory vs raw-wire contrast

**These three handlers DO NOT use TGFactory-based deserialization.** Unlike opcodes 0x06 (PythonEvent), 0x12 (SetPhaserLevel), 0x15 (CollisionEffect), 0x17 (DeletePlayerUI) which go through `TGFactory_DeserializeObject` (FUN_006d6200) to construct typed event objects from `[class_id][obj_id]` headers, the 0x1D/0x1E/0x1F triad uses **raw stream primitives only**:

- 0x1D: `ReadInt(objID)` only.
- 0x1E: `ReadInt(objID)` only — the response BUILD side uses `vtable[+0x10c]` (WriteToStream) which is the same chain ObjCreate uses for fresh object serialization.
- 0x1F: `ReadInt(objID) + ReadString_HeapAlloc(setName)`.

This makes them simpler to reimplement in OpenBC — no factory plumbing required. They are "command messages" (RPC-style requests/responses), not "event objects".

## Anchor table (for docwriter frontmatter)

| Item | Address | Confidence |
|---|---|---|
| MultiplayerGame__ObjNotFoundHandler | 0x006a0490 | high |
| MultiplayerGame__RequestObjHandler | 0x006a02a0 | high |
| MultiplayerGame__EnterSetHandler | 0x006a05e0 | high |
| MultiplayerGame__RequestObjEventHandler | 0x006a07d0 | high |
| MultiplayerGame__EnterSetEventHandler (stub) | 0x006a0a20 | high |
| GetPlayerSlotFromObjID (formula) | 0x006a19a0 | high |
| MakeObjIDFromPlayerSlot (inverse) | 0x006a7770 | high (not called by triad) |
| TGSceneGraph__GetObjectByID (factory 0x8003) | 0x00434e00 | high |
| PhysicsObjectClass__FindByObjectID (factory 0x8006) | 0x0059fc60 | high |
| CastToDamageableObject (IsA 0x8007) | 0x00590b20 | high |
| CastToShipClass (IsA 0x8008) | 0x005ab670 | high |
| IsLocalPlayerShip (host-mode dual) | 0x005ae140 | high |
| TGSetManager__FindSetIndexByName (binary search) | 0x004055a0 | high |
| DamageableObject__SendExplosions_0x29 (replay list) | 0x00595c60 | high |
| TGBufferStream__ReadString_HeapAlloc | 0x006d2370 | high |
| TGBufferStream__WriteString_LenPrefixed | 0x006d23c0 | high |
| TGSetManager singleton (array head) | DAT_0097e9c8 | high |
| DamageableObject HP sentinel = FLT_MAX | DAT_008e5c18 = 0x7F7FFFFF | high |
| "warp" string (default warp-tunnel set name) | DAT_008d8ab8 | high |
| "NoMe" relay group name | DAT_008e5528 | high |
| TGAlloc "UNKNOWN" class name (literal) | s_UNKNOWN_008d858c | high |
| TGNetwork singleton ptr | DAT_0097fa78 | high |
| MultiplayerGame jump table base | 0x0069F534 | high |
| Slot 27 (0x1D) thunk | 0x0069f4f5 | high |
| Slot 28 (0x1E) thunk | 0x0069f51d | high |
| Slot 29 (0x1F) thunk | 0x0069f509 | high |

## Suggested cascade

### wire-format-spec.md
- Row update for 0x1D / 0x1E / 0x1F:
  - 0x1D: confirm format `[int32 objectID]` (4 bytes).
  - 0x1E: format `[int32 objectID]` (request) / response builds full ObjCreate 0x02 or 0x03 payload.
  - 0x1F: format `[int32 objectID][uint32 nameLen][nameLen bytes setName]` (LENGTH-PREFIXED — flag as critical correction from earlier passes).

### game-opcodes.md
- Verify the table row 0x1F lists wire format consistent with this doc (length-prefixed not null-term).
- Annotate 0x1D + 0x1E + 0x1F as "command messages — bypass TGFactory" per the contrast above.

### subsystem-integrity-hash.md (or whichever doc handles ship HP field)
- DamageableObject HP field offset is ship+0x14c with sentinel FLT_MAX. Cross-link from this validation.

### docs/engine/rtti-class-catalog.md
- Confirm class IDs 0x8003 / 0x8006 / 0x8007 / 0x8008 → catalog names (likely TGObject / PhysicsObjectClass / DamageableObject / ShipClass).

### docs/protocol/stream-primitives.md
- Confirm vtable layout: byte +0x10 = ReadBytes, +0x14 = WriteBytes, +0x68 = ReadInt, +0x6c = WriteInt. The SWIG TGBufferStream has the same operations at different offsets — these are on the CURSOR vtable @ 0x00895C58.

## Open questions for tracker §4

1. SWIG handler registration string for FUN_006a0a20 — what name was the empty stub registered under?
2. Class-ID table cross-reference: confirm 0x8003=TGObject, 0x8006=PhysicsObjectClass, 0x8007=DamageableObject, 0x8008=Ship against rtti-class-catalog.md.
3. Why does FUN_006a05e0 always call `FUN_006d2370(0xffffffff)` for setName but FUN_006a07d0 uses `WriteString` via vtable+0x6c+0x14? (Verified the encodings are symmetric — both length-prefixed — but the call shape differs).
4. The "ExitSet" / "EnterSet" vtable slot names (+0x58, +0x54) on TGSet — are these confirmed in `docs/engine/tg-hierarchy-vtables.md`? If not, this triad provides the first independent confirmation of those slot meanings.

## Ghidra changes made this session

### Renames (12 functions)
| Old | New |
|---|---|
| FUN_006a0490 | MultiplayerGame__ObjNotFoundHandler |
| FUN_006a02a0 | MultiplayerGame__RequestObjHandler |
| FUN_006a05e0 | MultiplayerGame__EnterSetHandler |
| FUN_006a19a0 | GetPlayerSlotFromObjID |
| FUN_006a7770 | MakeObjIDFromPlayerSlot |
| FUN_00595c60 | DamageableObject__SendExplosions_0x29 |
| FUN_00434e00 | TGSceneGraph__GetObjectByID |
| FUN_0059fc60 | PhysicsObjectClass__FindByObjectID |
| FUN_00590b20 | CastToDamageableObject |
| FUN_004055a0 | TGSetManager__FindSetIndexByName |
| FUN_006d2370 | TGBufferStream__ReadString_HeapAlloc |
| FUN_006d23c0 | TGBufferStream__WriteString_LenPrefixed |

### Created functions (previously undefined-in-DB)
- 0x006a07d0 → MultiplayerGame__RequestObjEventHandler (575 bytes)
- 0x006a0a20 → MultiplayerGame__EnterSetEventHandler (3 bytes, single RET)

### Plate comments (5)
- 0x006a0490, 0x006a02a0, 0x006a05e0, 0x006a07d0, 0x006a0a20 — full behavior descriptions including wire format, gates, and corrections noted

### Data plate-comment attempts (2 failed — addresses are not functions)
- 0x008d8ab8 ("warp") — attempted set_plate_comment failed (data, not code); needs `set_disassembly_comment` instead next session.
- 0x008e5c18 (FLT_MAX) — same.

### Save
- `save_program` for STBC.exe at end of session: completed.

## Memory anchors

- DAT_008d8ab8 = literal C-string `"warp\0"` (5 bytes). Used by 0x1F sender as the "default warp-tunnel set" sentinel — if currentSet.name == "warp" then DON'T send 0x1F.
- DAT_008e5c18 = float FLT_MAX (3.4028235e+38). Used as DamageableObject HP sentinel for "undamaged" state.
- s_UNKNOWN_008d858c = literal C-string `"UNKNOWN"`. The class name passed to `TGAlloc/FUN_00718010` for generic TGMessage allocation throughout MultiplayerGame handlers.
- DAT_008e5528 = literal C-string `"NoMe"`. The relay group name for "all peers except self" used by client-side 0x1D/0x1F senders.
- DAT_0097fa78 = TGWinsockNetwork singleton. Loaded by every MP handler.
- DAT_0097e9c8 = TGSetManager array head (in-game set table; binary searched by FUN_004055a0).
- TGBufferStream cursor vtable @ 0x00895C58: byte +0x10 = ReadBytes, +0x14 = WriteBytes, +0x68 = ReadInt (returns 4 raw LE bytes), +0x6c = WriteInt.
- Class IDs (IsA tags): 0x8003 (scene graph?), 0x8006 (PhysicsObjectClass), 0x8007 (DamageableObject), 0x8008 (Ship).
- DamageableObject layout: +0x13c = explosionList, +0x14c = hullHP (sentinel FLT_MAX), +0x150 = deadFlag (byte).
- Ship layout: +0x20 = currentSet ptr (TGSet*), +0x28 = placement, +0x2d0 = warp engine subsystem ptr, +0x2e4 = team/species byte, +0xec = networked flag.
- Set layout: +0x74 = name (char*); vtable +0x54 = EnterSet (slot 21), vtable +0x58 = ExitSet (slot 22).
- TGMessage flags: +0x3a = guaranteed-delivery, +0x3d = notify-on-receipt.
