---
name: gameplay-leaf-repair-event-ids-validation-20260528
description: Gameplay leaf #16 ADD_TO_REPAIR_LIST event object ID analysis (317 lines). ZERO wire-format corrections. Constructor chain confirmed end-to-end. 2 minor Clar (TGSubsystemEvent fabrication carryover + HandleHitEvent IS in DB).
metadata:
  type: project
---

# Gameplay Leaf #16 — `docs/gameplay/repair-event-object-ids.md` v5 validation

**Date**: 2026-05-28 · **Doc**: 317 lines · **Status**: `partial` (clean — 2 carryover non-wire clarifications only)

## Verdict

**ROCK SOLID** on every wire-format and ID-encoding claim. Constructor chain, TGEvent/TGObjPtrEvent layouts, ADD_TO_REPAIR_LIST byte sequence, SUBSYSTEM_HIT byte sequence, HostEventHandler serialization — all binary-confirmed.

Two minor non-wire issues — both inherited from upstream docs, neither breaks any consumer:
1. Carryover of "TGSubsystemEvent" naming for factory 0x101 (doc admits this in note at line 95–98)
2. Stale "NOT in Ghidra func DB" annotation on HandleHitEvent at line 193 (it IS in the DB now)

## Anchors confirmed (Ghidra + assembly, all in STBC.exe)

### Constructor chain (lines 17–25)

| Addr | Symbol | Doc claim | Verified |
|------|--------|-----------|----------|
| 0x006f0a70 | TGObject_Ctor | Sets vtable PTR_FUN_00896278; +0x04 = ID via DAT_0095b078 counter | ✓ decomp + assembly |
| 0x006f31a0 | TGSourceObject_Ctor | Calls TGObject; vtable PTR_FUN_008962f4; +0x08 = 0 | ✓ decomp |
| 0x006f2590 | TGDestObject_Ctor | Calls TGSourceObject; vtable PTR_FUN_008962a8; +0x0C = 0 | ✓ decomp |
| 0x006d8f90 | TGHandler_Ctor | Calls TGDestObject; vtable PTR_FUN_00896044; +0x10 = 0 | ✓ decomp |
| 0x0056b970 | ShipSubsystem_Ctor | Calls TGHandler; vtable PTR_FUN_00892fc4 | ✓ decomp (param_1[0x10]=0 = +0x40, confirms +0x40 zeroed; SetOwnerShip overwrites later) |
| 0x00562240 | PoweredSubsystem_Ctor | Calls ShipSubsystem; vtable PTR_FUN_00892d98 | ✓ decomp |
| 0x00565090 | RepairSubsystem_Ctor | Calls PoweredSubsystem; vtable PTR_FUN_00892e24 | ✓ decomp |

### Global ID counter (lines 47–49)

- `DAT_0095b078` — sole producer/consumer = FUN_006f0a70 (3 READs + 1 WRITE, no other xrefs). **Definitive proof** this is the auto-increment global object ID counter as claimed.
- `DAT_0099a67c` — global hash table (init lazy in TGObject_Ctor at 0x7F7 buckets = 2039). FUN_006f0ee0 walks bucket chain via `puVar1[2]` (next ptr at +0x08 of hash node), returns `puVar1[1]` (object* at +0x04). ✓

### Setters (lines 100–106)

| Addr | Doc name | Actual behavior | Verified |
|------|----------|-----------------|----------|
| 0x006d6270 | SetSource | Writes param_2 to `this+0x08`, manages refcount via DAT_009983a8 | ✓ |
| 0x006d62b0 | SetDest | Writes param_2 to `this+0x0C`, treats DAT_0095adfc as sentinel (skips refcount) | ✓ |

### TGEvent / TGObjPtrEvent layout (lines 72–94)

- TGEvent_Ctor at 0x006d5c00: size 0x28, vtable PTR_FUN_00895ff4; sets +0x14 = 0xBF800000 (-1.0f), zeros +0x18..+0x24, allocates DAT_009983a4 hash table lazily. ✓
- TGObjPtrEvent_Ctor at 0x00403290: calls TGEvent_Ctor, sets vtable PTR_TGObjPtrEvent_ScalarDeletingDtor_0088869c, zeros +0x28. Size 0x2C. ✓
- TGObjPtrEvent's IsA returns true for 0x10C, 0x101, 0x02 (per existing v5 plate on TGObjPtrEvent_Ctor).

### WriteToStream (lines 108–127)

- TGEvent::WriteToStream at 0x006d6130 (4 stream calls, ~21 lines decomp):
  - Call 1: `stream->vtable[+0x64](vtable[+0x04](event))` → writes factory_id (0x101)
  - Call 2: `stream->vtable[+0x64](event+0x10)` → writes eventType
  - Call 3: `stream->vtable[+0x84](source_id)` → source_id = 0 if NULL, else `*(source+0x04)`
  - Call 4: `stream->vtable[+0x84](dest_id)` → dest_id = 0 if NULL, **-1 if DAT_0095adfc sentinel**, else `*(dest+0x04)`
- TGObjPtrEvent::WriteToStream at 0x006d6dc0: calls base, then `stream->vtable[+0x84](event+0x28)` → appends int32 obj_ptr.
- All four wire-format lines (factory_id, eventType, source_obj_id, dest_obj_id, +20 bytes for ObjPtrEvent's obj_ptr) byte-confirmed.

### SUBSYSTEM_HIT event creation (lines 141–179 — SetCondition @ 0x0056c470)

Decomp confirms:
- Allocates 0x2C bytes (TGObjPtrEvent size) ✓
- `TGObjPtrEvent_Ctor(this, 0)` — factory 0x10C ✓
- `FUN_006d6270(0)` → SetSource(NULL) — `evt+0x08 = NULL` ✓
- `FUN_006d62b0(*(param_1+0x40))` → SetDest(ownerShip) — `evt+0x0C = ship ptr` ✓
- `pTVar2->dwEvent_type = (uint)&DAT_0080006b` → event type 0x0080006B ✓
- `pTVar2->nObj_ptr = *(int *)(param_1 + 4)` → obj_ptr = subsystem's own ID ✓
- Gate: `condition < max AND (ship==NULL OR ship+0x14C >= DAT_008e5c18)` — matches "DAMAGE_REPORT_THRESHOLD" doc framing.

### ADD_TO_REPAIR_LIST event creation (lines 211–235 — FUN_00565900)

Disassembly (decisive — Ghidra's decomp obscures the thiscall):
- `this` = ECX = RepairSubsystem; `param_1` = EBX = damagedSub; `param_2` = (unused; just dead `1` from HandleHitEvent caller).
- Allocates 0x28 bytes — **plain TGEvent (not TGObjPtrEvent)** ✓
- `FUN_006d5c00(0)` — TGEvent_Ctor, factory 0x101 ✓
- `MOV dword ptr [ESI + 0x10], 0x8000df` — event type = 0x008000DF directly ✓
- `MOV ECX, ESI; PUSH EDI(=RepairSubsystem); CALL 0x006d62b0` → SetDest(event, this=RepairSubsystem) → `evt+0x0C = repairSub` ✓
- `MOV ECX, ESI; PUSH EBX(=damagedSub); CALL 0x006d6270` → SetSource(event, damagedSub) → `evt+0x08 = damagedSub` ✓
- `MOV ECX, 0x97f838; CALL 0x006da2a0` → PostEvent to EventManager singleton ✓
- Gate: `AddToList_returns_true AND DAT_0097fa89 (IsHost) AND DAT_0097fa8a (IsMultiplayer)` ✓

### Handler registration (lines 271–283 — FUN_00565d40)

`RepairSubsystem_HandleHitEvent_RegisterHandlers` confirmed at 0x00565d40:
```
FUN_006da130(FUN_005658d0, "RepairSubsystem__HandleHitEvent")
FUN_006da130(FUN_00565980, "RepairSubsystem__HandleRepairCom...")
FUN_006da130(FUN_00565a10, "RepairSubsystem__HandleSubsystem...")
FUN_006da130(FUN_00565a80, "RepairSubsystem__HandleRepairCan...")
FUN_006da130(FUN_00565b50, "RepairSubsystem__HandleIncreaseP...")
FUN_006da130(FUN_00565b30, "RepairSubsystem__HandleAddToRepa...")
FUN_006da160(FUN_00565cd0, "RepairSubsystem__HandleSetPlayer")   ← note FUN_006da160 (not 130) for SetPlayer
```

Doc lists all 7 correctly, but does NOT note that SetPlayer uses a different registration function (`FUN_006da160` vs `FUN_006da130`). Likely a different registration ADT (e.g. enter/exit handler vs hit handler). Non-load-bearing for the wire-format claim.

### HostEventHandler (lines 285–298 — FUN_006a1150)

Assembly confirms every step:
- `MOV byte ptr [ESP + 0x3c], 0x6` — opcode 0x06 ✓
- `PUSH 0x3ff` — buffer size 1023 ✓
- `vtable[+0x34]` call — WriteToStream ✓
- `PUSH 0x40` — TGMessage size 0x40 ✓
- `MOV byte ptr [ESI + 0x3a], 0x1` — reliable flag at msg+0x3A ✓
- `PUSH 0x8e5528` — "Forward" group string ✓
- `CALL 0x006b4de0` — BroadcastTGMessage ✓

## Material findings

### Wire format
**ZERO** corrections. Both wire diagrams (SUBSYSTEM_HIT 21 bytes, ADD_TO_REPAIR_LIST 17 bytes) are byte-accurate.

### Clarification 1 — "TGSubsystemEvent" carryover (line 95–98 note)

Doc correctly tags factory 0x101 = TGEvent (not TGSubsystemEvent) in the note block, but the ASCII table at line 114 still uses the comment:
```
[int32] factoryType — 0x101 for TGSubsystemEvent, 0x10C for TGObjPtrEvent
```

The v5 plate on TGObjPtrEvent_Ctor (already byte-confirmed last session) **explicitly debunks** "TGSubsystemEvent":
> NOTE: doc names 0x101 as "TGSubsystemEvent" but the binary has NO such class — vtable PTR_FUN_00895ff4 (TGEvent base ctor writes it) emits factory_id 0x101 directly.

Inherited from protocol leaf #13 tgobjptrevent. Document already shows awareness via the note at lines 95–98. **Status: documented contradiction — clarify ASCII comment.**

### Clarification 2 — `FUN_005658d0` HandleHitEvent IS in DB (line 193)

Doc claims `RepairSubsystem::HandleHitEvent` at 0x005658d0 is "NOT in Ghidra func DB". As of this validation pass it IS in the DB (`get_function_by_address` returns body 005658d0–005658fe, signature `undefined FUN_005658d0(void)`). Was likely created in an earlier session. **Status: stale annotation.**

### Clarification 3 — `RET 0x8` quirk in AddSubsystemToRepairList

FUN_00565900 signature on the wire is effectively `(this=RepairSubsystem, damagedSub, dead_arg)` — caller HandleHitEvent passes `1` as the second stack arg, but `FUN_00565900` never reads it (RET 0x8 pops both). Doc shows 2-arg signature `(this, damagedSub)` which is cleaner. **Non-issue for OpenBC implementers — the wire output is unaffected by this dead arg.** Worth a one-line footnote if the doc gets revised.

### Clarification 4 — SetPlayer handler uses different registration fn

Line 282 in doc lists `FUN_00565cd0 | HandleSetPlayer`. Disassembly shows it registers via `FUN_006da160` (not `FUN_006da130` like the other 6 handlers). Possibly different handler-type registration (e.g. enter/exit vs hit). Worth flagging as an open question for the next pass on event-system-architecture.md. **Non-load-bearing for repair wire format.**

## Open questions

1. Why does the `1` literal in `FUN_00565900(damagedSub, 1)` exist? Vestigial debug flag? Worth grepping for other callers of FUN_00565900.
2. What's the semantic difference between FUN_006da130 (handler registration A) and FUN_006da160 (handler registration B)? Resolution belongs in event-system-architecture.md follow-up, not here.
3. The doc's "TGSubsystemEvent" naming originates somewhere upstream — possibly an old vtable label or SWIG type. Worth a grep across `docs/` to clean up consistently.

## v5 status proposal

- Header: `validated: 2026-05-28` · `confidence: high` on all wire-format claims · `status: partial` (because of the TGSubsystemEvent ASCII comment + stale "not in DB" line).
- Companions: `docs/protocol/tgobjptrevent-class.md` (already linked implicitly), `docs/protocol/pythonevent-wire-format.md` (transport carrier), `docs/gameplay/repair-system.md` (consumer), `docs/engine/event-system-architecture.md` (Post/Forward mechanism).
- Block list: nothing blocking. Doc is one of the cleanest gameplay leafs validated.

## Pattern note for future digs

This doc's strength is that it explicitly traces ID origin (DAT_0095b078 counter), not just "subsystem has an ID" — which is exactly the question OpenBC implementers need answered. Pattern to repeat: when a doc claims "object X has ID Y", trace Y back to the **single global writer** and assert no other writer exists. The `get_xrefs_to` 4-line result for DAT_0095b078 is the canonical proof.

Repair-event-object-ids is the first gameplay leaf where the doc author already cross-validated against a v5 plate (the TGObjPtrEvent_Ctor v5-validated note at 0x00403290). That cross-validation is why the note block at lines 95–98 exists. The ASCII tables just didn't get the corresponding pass.
