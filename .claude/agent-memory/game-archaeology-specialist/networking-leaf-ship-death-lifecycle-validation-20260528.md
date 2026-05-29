---
name: networking-leaf-ship-death-lifecycle-validation-20260528
description: Networking leaf #11 (MP ship death + respawn, FINAL networking leaf). Doc 192 lines, trace-driven verification. Status:partial. ZERO wire/sequence corrections — all 3 handler addresses verified, ObjectExplodingHandler dual-branch logic (SP writes lifetime to ship+0x14c then loads visuals; MP serializes 0x06 PythonEvent to NoMe with guaranteed flag) byte-confirmed. 2 minor C ("TGSubsystemEvent" class name fabricated per leaf #13 — IS TGEvent factory 0x101; SCORE_CHANGE anomaly speculation overreaches binary evidence). 1 Clar (handler at 0x006a1240 was bare-code, now created+named).
metadata:
  type: project
  date: 2026-05-28
  family: networking
  doc-number: 11-leaf
  status: partial
---

# Networking Doc #11 — ship-death-lifecycle.md (LEAF, v5 validation, FINAL networking leaf)

**Doc:** `docs/networking/ship-death-lifecycle.md`
**Scope:** MP ship death sequence (combat + self-destruct) + respawn flow + DestroyObject(0x14) non-use claim
**Verdict:** `partial` — ZERO wire-format corrections, ZERO sequence corrections; 2 minor C (one inherited from leaf #13 nomenclature, one a speculation flag).

## TL;DR

The doc is **trace-driven** (33.5min battle + 6-death self-destruct session) and the binary cross-check confirms every checkable structural claim. ObjectExplodingHandler at 0x006a1240 was bare code (no Ghidra function) — created and named this session, body 283 bytes, dual-branch logic byte-verified. Explosion handler at 0x006a0080 and DestroyObject handler at 0x006a01e0 both confirmed as documented. The "factory 0x8129" / "opcode 0x06" / "NoMe group" / "lifetime in event+0x2c" claims all pass byte-level verification.

## Confirmed Claims (byte/disasm anchors)

| Claim | Evidence | Confidence |
|---|---|---|
| ObjectExplodingHandler registered at &LAB_006a1240 with string "MultiplayerGame :: ObjectExplodingHandler" (0x0095a054) | FUN_0069efe0 disasm at 0x006a1c0..0x006a1cf: `PUSH 0x95a054, PUSH 0x6a1240, MOV ECX, 0x97f838, CALL 0x006da130` | high |
| Function at 0x006a1240 exists as bare code (Ghidra create_function succeeded with body 283 bytes) | session-created MultiplayerGame_ObjectExplodingHandler | high |
| Handler branches on DAT_0097fa8a (IsMultiplayer flag) | disasm 0x006a124e: `MOV AL,[0x0097fa8a]`; 0x006a1260: `TEST AL,AL`; 0x006a1264: `JZ 0x006a131b` (SP branch) | high |
| MP path writes opcode 0x06 byte | disasm 0x006a127f: `MOV byte ptr [ESP+0x3c], 0x6` | high |
| MP path calls event.WriteToStream via vtable+0x34 | disasm 0x006a12af: `PUSH EAX (stream); MOV EDX, [ECX]; CALL [EDX+0x34]` | high |
| MP path uses TGAlloc "UNKNOWN" class allocator (matches leaf #18 pattern) | disasm 0x006a12c0: `PUSH 0x8d858c (s_UNKNOWN)`; 0x006a12c5: `PUSH 0x40 (size)`; 0x006a12cd: `CALL 0x00717b70 (alloc)`; 0x006a12d4: `CALL 0x00718010 (factory)` | high |
| MP path sends to "NoMe" group | disasm 0x006a12f4: `PUSH 0x8e5528` — inspect_memory: "NoMe\0" at 0x008e5528 | high |
| MP path sets guaranteed-delivery flag (msg+0x3a = 1) | disasm 0x006a12fb: `MOV byte ptr [ESI+0x3a], 0x1` | high |
| MP path calls TGWinsockNetwork_SendTGMessageToGroup | disasm 0x006a12ff: `CALL 0x006b4de0` | high |
| SP path writes event.lifetime (event+0x2c) to ship+0x14c (HP slot) | disasm 0x006a1332: `FLD float [ESI+0x2c]`; 0x006a1335: `FSTP [EAX+0x14c]` where EAX=ship from CastToShipClass | high |
| SP path casts via CastToShipClass (FUN_005ab670, IsA 0x8008 per leaf #18) | disasm 0x006a1326: `CALL 0x005ab670` after `PUSH [ESI+0xc]` (event.objectRef → obj+4) | high |
| SP path triggers visual effects via FUN_005ac250 (loads "Effects" + "ObjectExploding" strings) | disasm 0x006a133d; FUN_005ac250 decompile shows string load of s_Effects_008e0ee0 + s_ObjectExploding_008e6198 | high |
| Explosion handler (opcode 0x29) at FUN_006A0080 | disasm: skip opcode byte, ReadInt(objID), FUN_00590a50 (CastToDamageableObject), CV4 position read, CF16 dmg, CF16 radius, FUN_004bbde0 (ExplosionDamage ctor per leaf #20/21), FUN_00593e50 (apply) | high |
| DestroyObject handler (0x14) at FUN_006A01E0 | disasm: skip opcode, ReadInt(objID), TGSceneGraph__GetObjectByID, if obj+0x20 NULL call dtor via vtable[0]; else forward to parent | high |
| ObjCreateTeam handler (0x02/0x03) at FUN_0069F620 = MpgameHandleObjCreate (already renamed per leaf #9) | get_function_by_address returns "MpgameHandleObjCreate" signature with team byte param | high |
| ET_OBJECT_EXPLODING = 0x0080004E (event ID) | cross-anchored in v5-validation-status.md §3564 + pythonevent-wire-format leaf #14 | high (inherited) |
| ET_ADD_TO_REPAIR_LIST = 0x008000DF (event ID) | cross-anchored in multiplayer-mission-infrastructure.md §266+§813 + game-opcodes.md §213 | high (inherited) |
| Factory 0x8129 (ObjectExplodingEvent) | anchored in pythonevent-wire-format leaf #14 (validated): vtable 0x0088A178, ctor 0x0043F8B0, GetFactoryID 0x0043F8E0 | high (inherited) |
| 6 TGSubsystemEvents (4 immediate + 2 late) for self-destruct subsystem repair | cross-anchored in self-destruct-pipeline.md §581-585 with PowerReactor/ShieldGenerator/PhaserController/PulseWeapon immediate + EPS/Repair late | high (inherited via trace) |

## Triage block

### C1 — "TGSubsystemEvent" class name is fabricated [severity: LOW — naming, no wire impact]

**Prior claim (line 153-154):** "Stock self-destruct sends exactly **6 TGSubsystemEvents** (ET_ADD_TO_REPAIR_LIST, event 0x008000DF, factory 0x0101). These route damaged subsystems TO the RepairSubsystem..."

**Binary truth (inherited from leaf #13 / tgobjptrevent-validation memo):** String search for "TGSubsystemEvent" in STBC.exe returns ZERO matches. Factory 0x0101 IS the **TGEvent base class itself** (vtable 0x00895FF4, ctor FUN_006d5c00). There is no separate "TGSubsystemEvent" class — these are bare TGEvent objects with event_type=0x008000DF carrying source+dest object refs to the affected subsystem and the RepairSubsystem.

**Impact:** Cosmetic — the wire data is correct (factory 0x101, event 0x008000DF, two object refs). Doc should rename to "TGEvent (factory 0x101) with event type ET_ADD_TO_REPAIR_LIST" or simply "ET_ADD_TO_REPAIR_LIST events". The 6-count and subsystem identity table remain valid.

### C2 — SCORE_CHANGE anomaly speculation overreaches binary evidence [severity: LOW — speculation]

**Prior claim (line 82-85):** "Weapon kills may NOT trigger SCORE_CHANGE on stock dedicated servers — This may be a stock BC bug — the scoring handler may not be registered for weapon-path destruction events"

**Binary truth:** The Python `ObjectKilledHandler` IS registered for `App.ET_OBJECT_EXPLODING` (0x0080004E) in every Mission*.py — confirmed via:
- `reference\scripts\Multiplayer\Episode\Mission1\Mission1.py:195` AddBroadcastPythonFuncHandler(ET_OBJECT_EXPLODING, pMission, "ObjectKilledHandler")
- Same pattern in Mission2/3/5

So the handler IS registered — it fires on every ObjectExploding event including weapon kills. The Python body at Mission1.py:534+ early-returns on:
- `g_bGameOver != 0`
- `pShip.IsPlayerShip() == 0`
- non-Ship dest object

The "scoring handler not registered" hypothesis is FALSE. The actual SCORE_CHANGE-not-sent-for-weapon-kills observation (CLAUDE.md known issue) likely traces to one of these early-returns AND/OR the firing-player ID being 0/sentinel for weapon kills in some path. Requires Python-side investigation, not binary RE.

**Impact:** Doc should rephrase: "Weapon kills may not trigger SCORE_CHANGE on stock dedicated servers (CLAUDE.md known issue). Root cause is unknown — the Python ObjectKilledHandler IS registered for ET_OBJECT_EXPLODING; investigation should focus on the Python scoring logic's early-return paths or firing-player ID handling." Strike the "scoring handler may not be registered" hypothesis.

### Clar1 — Handler at 0x006a1240 was bare code; now created+named [severity: INFO — Ghidra DB state]

The function body at 0x006a1240 was undefined in Ghidra (auto-analyzer didn't promote — same pattern as ~13 other dispatched handlers per networking foundation #1). This session ran `create_function(0x006a1240, "MultiplayerGame_ObjectExplodingHandler")` successfully — body 283 bytes, dual-branch (SP/MP) decompile clean. Future passes should find this function pre-defined.

(Ghidra DB warnings on naming: "main part is not PascalCase", "contains underscores" — acknowledged; matches established convention used for ObjNotFoundHandler / RequestObjHandler / EnterSetHandler etc. created in leaf #18.)

## TGFactory routing for this opcode family (cross-doc context)

This handler's MP-path goes through the **TGFactory polymorphic dispatch** (leaf #14 pythonevent pattern):
- Allocates 0x40-byte TGMessage via TGAlloc(s_UNKNOWN, 0x40)
- Calls `(*[ECX])(0x40)` to set opcode 0x06 in payload[0]
- Calls vtable+0x34 (WriteToStream) on the event polymorphically — same vtable slot as TGCharEvent / TGObjPtrEvent / TGEvent base
- Copies buffered serialization into TGMessage payload starting at offset +1 (after opcode byte)
- Sends to "NoMe" group (relay-to-all-peers-except-self)

This is the **canonical 0x06 PythonEvent send path** — same code pattern (vtable+0x34, NoMe group, guaranteed flag) appears in HostEventHandler (FUN_006A1150), SetPhaserLevelHandler (FUN_006A1970), and the start/stop firing / subsystem status / repair handlers (FUN_0069FDA0). All produce wire-identical 0x06 frames with different event class payloads.

## OpenBC implication notes

1. **Single-player vs multiplayer branch is purely conditional on DAT_0097fa8a** — OpenBC server runs as host (IsMultiplayer=1), so it always takes the relay branch. The SP-path's ship+0x14c=lifetime write is NOT needed in a dedicated server (the server's host-ship is a dummy, and clients receive the event via 0x06 broadcast and apply their own local death animation).

2. **Server-side death authority**: The dedicated server is responsible for emitting ObjectExplodingEvent when HP reaches 0 server-side (assuming server-side damage authority). This happens via the damage pipeline (collision/weapon/explosion → ShipDeathHandler at 0x005AFEA0 per self-destruct-pipeline) which posts ET_OBJECT_EXPLODING. The local handler chain catches it and emits opcode 0x06.

3. **No DestroyObject (0x14) for ship death**: Verified by trace evidence (0/59 in battle, 0/6 in self-destruct). The handler EXISTS at 0x006a01e0 (binary-confirmed dtor invocation) but is reserved for non-ship-death cleanup. Cross-check with disconnect-flow.md: line 389 contradicts (says "Observed for ship destruction (combat kills)") — but trace evidence here (this doc) is stronger, so 0x14 should NOT be sent for ship death in OpenBC.

4. **Client-initiated respawn**: Server should NEVER spontaneously send ObjCreateTeam(0x03) after death. Wait for client to pick a new ship and send 0x03; relay it. (OpenBC PR#34 self-destruct fix already addresses this.)

5. **The 9.5-second lifetime field**: Hardcoded in the event by the SP/MP sender path? Or driven by event constructor? Worth verifying — if it's set at event-construction time by ShipDeathHandler with a constant 9.5f, OpenBC needs to match this exactly for client animation timing.

## Anchor table (for docwriter frontmatter)

| Item | Address | Confidence |
|---|---|---|
| MultiplayerGame__ObjectExplodingHandler (dual-branch) | 0x006a1240 | high |
| Handler_Explosion_0x29 | 0x006a0080 | high |
| Handler_DestroyObject_0x14 | 0x006a01e0 | high |
| MpgameHandleObjCreate (0x02/0x03 receive) | 0x0069F620 | high (already named, leaf #9) |
| CastToShipClass (IsA 0x8008) | 0x005ab670 | high (inherited leaf #18) |
| CastToDamageableObject (IsA 0x8007) | 0x00590b20 | high (inherited leaf #18) |
| ExplosionDamage ctor | 0x004bbde0 | high (inherited leaf #20/21) |
| FUN_005ac250 (visual-effects loader, SP-only) | 0x005ac250 | high (this session) |
| ShipDeathHandler (per self-destruct chain) | 0x005AFEA0 | high (inherited self-destruct-pipeline) |
| TGAlloc | 0x00717b70 + 0x00718010 | high (cascade) |
| TGWinsockNetwork_SendTGMessageToGroup | 0x006B4DE0 | high (cascade) |
| TGNetwork singleton | DAT_0097fa78 | high (cascade) |
| IsMultiplayer flag | DAT_0097fa8a | high (CLAUDE.md) |
| "NoMe" relay group name | DAT_008e5528 | high (cascade) |
| "UNKNOWN" TGAlloc class name | s_UNKNOWN_008d858c | high (cascade) |
| Factory 0x8129 (ObjectExplodingEvent) | inherited from leaf #14 | high (cross-ref) |
| Event ID 0x0080004E (ET_OBJECT_EXPLODING) | inherited (string at 0x00910ac8) | high (cross-ref) |
| Event ID 0x008000DF (ET_ADD_TO_REPAIR_LIST) | inherited (architecture/multiplayer-mission-infrastructure) | high (cross-ref) |
| Ship HP slot offset | ship+0x14c (FLT_MAX undamaged sentinel per leaf #18) | high (cross-ref) |
| Event lifetime field offset | event+0x2c (set to 9.5f per stock trace) | high (this session) |
| Event objectRef offset | event+0xc (dest_obj, dying ship) | high (this session) |

## Cross-doc cascade

### wire-format-spec.md
- Already covers opcode 0x06 / 0x14 / 0x29 — no row changes needed.

### pythonevent-wire-format.md (leaf #14)
- This doc is the upstream reference for factory 0x8129 / ObjectExplodingEvent class layout. No changes needed.

### self-destruct-pipeline.md
- Cross-references in agreement on 6 TGSubsystemEvents (4+2 split), 9.5s lifetime, source=NULL for self-destruct.

### disconnect-flow.md
- **Cross-doc tension at line 389**: says "0x14 DestroyObject: Observed for ship destruction (combat kills)" — directly contradicts this doc's trace evidence (0/59 in battle). The 0x14 IS sent for disconnect-triggered cleanup (per lines 44/206/214/520 of disconnect-flow), but NOT for combat death. Line 389 should be corrected. Belongs in disconnect-flow.md validation, not here.

### CLAUDE.md
- "SCORE_CHANGE (0x36) not sent for weapon kills on stock dedi — may be a stock BC bug (collision kills work)" — confirmed as a real observation. The "may not be registered for weapon-path" hypothesis in this doc should be struck (C2 above). Actual root cause requires Python investigation.

## Open questions

1. **Why does the Python ObjectKilledHandler not produce SCORE_CHANGE for weapon kills?** Handler IS registered for ET_OBJECT_EXPLODING — needs Python script analysis to identify the early-return path or condition under which weapon kills are skipped. (Original doc Follow-up; refined here.)

2. **Where is event+0x2c (lifetime) set to 9.5f?** ShipDeathHandler (0x005AFEA0) likely constructs the ObjectExplodingEvent and sets lifetime. The 9.5f constant should be findable as a `.rdata` float or immediate. Worth a one-pass check to confirm — important for OpenBC fidelity.

3. **What is event+0xc (object ref / dest_obj)?** This session confirmed `param_1[3]` (which is event+0xc) is the dying ship object reference, passed to CastToShipClass in SP path. For TGEvent layout (per leaf #14): +0x4 = factory_id, +0x8 = event_type, +0xc = source_obj_ref, +0x10 = dest_obj_ref. Re-verify: leaf #14 says source/dest are at +0x6C/+0x70 for ObjectExplodingEvent specifically. The +0xc field on the event in this handler must be... hmm. Could be either the engine's transient object-ID field (not the wire field) OR the SP handler passes a different object than the wire-serialized one. **This is a meaningful semantic-vs-wire layout question that would benefit a dedicated investigation.**

## Ghidra DB changes

### Created functions (session)
- **0x006a1240** → `MultiplayerGame_ObjectExplodingHandler` (283 bytes, dual SP/MP branch verified)

### Already-named in DB (no changes)
- 0x0069F620 → MpgameHandleObjCreate (leaf #9)
- 0x005ab670 → CastToShipClass (leaf #18)
- 0x00590b20 → CastToDamageableObject (leaf #18)

### Save
- save_program for STBC.exe at end of session: completed.

## Memory anchors

- ObjectExplodingHandler dual-branch: SP writes lifetime to ship+0x14c (HP slot) + loads explosion visuals via FUN_005ac250; MP serializes opcode 0x06 PythonEvent to "NoMe" group with guaranteed-delivery flag (msg+0x3a=1).
- Handler is registered via FUN_006da130 (EventManager AddHandler) at 0x0069efe0 with string "MultiplayerGame :: ObjectExplodingHandler" (0x0095a054).
- Factory 0x101 covers the ET_ADD_TO_REPAIR_LIST events — IS the TGEvent base, NOT a separate "TGSubsystemEvent" class (name fabricated; per leaf #13).
- Event field offsets observed in this handler: +0xc (object ref), +0x2c (lifetime float). May or may not align with wire layout (open question 3).
- Stock trace ground truth: 0/59 DestroyObject in battle, 0/6 in self-destruct — DestroyObject (0x14) is NOT used for MP ship death.
- Respawn is always client-initiated: client picks new ship → sends 0x03 → server relays to other peers. NO server-originated 0x03 after any death (62/62 are client-initiated relays).
- SCORE_CHANGE Python handler IS registered for ET_OBJECT_EXPLODING in every Mission*.py — the "not sent for weapon kills" bug is a Python-side issue, not a registration issue.
