---
name: gameplay-mid-cloaking-validation-20260528
description: Gameplay mid #8 (cloaking-state-machine.md, 518 lines) v5 validation — 4 corrections + 3 clarifications + 2 hindsight; default CloakTime=5.0f confirmed (NOT 3.0); StopCloaking byte +0xAC NOT +0xAD; ET_CLOAK_BEGINNING is 0x00800077 (doc lists 0x00800078 as ET_CLOAK_BEGINNING but binary names it ET_CLOAK_COMPLETED)
metadata:
  type: project
---

# Gameplay Mid #8 — Cloaking State Machine Validation

## Scope
- Doc: `docs/gameplay/cloaking-state-machine.md` (518 lines)
- Binary: STBC.exe at /C:/Users/Steve/source/projects/STBC-Dedicated-Server/game/stock-dedi/STBC.exe
- All checks against STBC.exe (with SGW.exe also open — passed `program=STBC.exe` to every call)

## Confirmed (high confidence, byte-confirmed)

### State machine (4 active + 2 ghost) — VERIFIED
- States 0/2/3/5 active; states 1/4 are dead code as documented
- Tick fn FUN_0055e500 reads +0xB0 (state) + +0xB4 (timer) and dispatches via `if state==2 || state==5` then `LAB_0055e59e` for state intent checks
- DAT_008e4e1c is the universal CloakTime divisor (read 4 times: tick CLOAK branch, tick DECLOAK branch, BeginDecloak `+0xb4=CloakTime`, RecalcVisibility)
- DAT_0088d4ec is the efficiency threshold for auto-decloak (`*(float*)(param_1 + 0x94) < _DAT_0088d4ec` triggers force-decloak at state 3)

### Ctor (FUN_00566d10) — VERIFIED
NOTE: Ghidra currently calls this `SensorSubsystem_Ctor` — that name is WRONG. Disassembly confirms it is CloakingSubsystem ctor:
- Calls FUN_00562240 (PoweredSubsystem_Ctor — confirmed via `PTR_FUN_00892d98` install)
- Sets +0xC0 = 2 (the "render mode?" field doc speculates)
- Zeros +0xAC, +0xB0, +0xB4, +0xB8, +0xBC, +0xA8, +0xC4, +0xC8
- Sets vtable to 0x00892eac
- Doc's field-layout table at lines 36-44 matches byte-for-byte

### Event ID bindings — VERIFIED
- 0x008000E3 = ET_START_CLOAKING (subsystem-side handler reg at 0x0055e4d0 PUSH 0x8000e3, byte-confirmed)
- 0x008000E5 = ET_STOP_CLOAKING (PUSH 0x8000e5 at 0x0055e4e9)
- 0x008000E2 = ET_START_CLOAKING (MultiplayerGame side, in MultiplayerGame_Ctor reg via `FUN_006db380(&DAT_008000e2, ..., s_MultiplayerGame____StartCloaking_*)`)
- 0x008000E4 = ET_STOP_CLOAKING (MultiplayerGame side)
- 0x00800079 = ET_DECLOAK_BEGINNING (posted in FUN_0055f110 BeginDecloak path)
- 0x0080007A = ET_DECLOAK_COMPLETED (posted in FUN_0055f7f0 + FUN_0055f560)
- 0x0080007B = shield re-enable delayed event (posted in FUN_0055f110 cloak path + FUN_0055f7f0 decloak complete + FUN_0055f3e0 InstantCloak)

### Network handlers — VERIFIED
- 0x00549a50 reads `DAT_0097e238 + 0x54` → ship, then ship+0x2DC for cloak subsystem
- Tests `eventData+0x174 == 0` → StartCloaking, else → StopCloaking
- 0x0055e4d0 registers via FUN_006d92b0 on the SWIG event registry at 0x0098b850
- 0x0055e4a0 registers via FUN_006da130 on the EventManager singleton at 0x0097f838

### StateUpdate cloak serialization — VERIFIED
- Writer FUN_005b17f0: reads `pShip[0xb7]` (= ship+0x2DC cloak ptr), then `(cloak+0x9c)` (isOn byte). Compares against tracker+0x2E (lastCloakState byte). If changed or force: dirty flags |= 0x40.
- Wire emits 1-bit WriteBool_Bit of cloak's isOn at 0x005b1e6a-0x005b1e73 (`CALL 0x006cf770`)
- Reader FUN_005b21c0: if `0x40 & flags && ship+0x2DC != 0`, reads bit; if bit=0 → StopCloaking (FUN_0055f380), else → StartCloaking (FUN_0055f360)

### Default constant values — NEW (RESOLVES OQ from doc)
Read at `0x008e4e1c`: bytes `00 00 a0 40` = **5.0f** (CloakTime default = 5.0 seconds, NOT 3.0)
Read at `0x008e4e20`: bytes `00 00 80 3f` = **1.0f** (ShieldDelay default = 1.0 second)
The doc speculated these could not be verified from static analysis — they CAN, and OpenBC's claim of "3.0 seconds" is binary-WRONG by 67%.

### Visual constants at FUN_0055ee10 — VERIFIED
- DAT_0088c5ac = shimmer threshold
- DAT_00892c94 = random scale factor
- DAT_00892c90 = decloak scale factor
- DAT_0088cb58 = alpha offset
- DAT_0088ba90 = alpha scale (used in FUN_0055e640 for effectNode+0x120)

### ShipClass::IsCloaked — VERIFIED EXACTLY
0x005ac450 reads ship+0x2DC; if NULL → 0; else returns `*(char*)(cloak+0xAC) == 1` (isFullyCloaked byte). Returns true ONLY during state==3 (CLOAKED, not transitions). ✓

### DeathWhileCloaked (FUN_0055f930) — VERIFIED
Reads ship+0x9C (isOn). If non-zero: calls DisableSubsystem (FUN_00562630), then if `state==3 || tryingToCloak(+0xAD)==1`, runs StopCloaking + BeginDecloaking. ✓

## Corrections (C)

### C1 — HIGH — StopCloaking byte check (line 178-179)
**Doc says**:
```c
if (this->state == 1 || this->state == 2 || this->tryingToCloak == 1) {
    BeginDecloaking(this, 0);
}
```
**Binary at 0x0055f393 says**: `CMP byte ptr [ESI + 0xAC], 0x1` — that's **isFullyCloaked** (+0xAC), NOT tryingToCloak (+0xAD).
Disasm-confirmed:
```
0055f383: MOV EAX,dword ptr [ESI + 0xb0]   ; state
0055f389: CMP EAX,0x1                       ; ghost CLOAKING-1
0055f38c: JZ  0055f39c
0055f38e: CMP EAX,0x2                       ; CLOAKING
0055f391: JZ  0055f39c
0055f393: CMP byte ptr [ESI + 0xac],0x1     ; +0xAC = isFullyCloaked
0055f39a: JNZ 0055f3a5
0055f39c: PUSH 0  + CALL BeginDecloaking
0055f3a5: MOV byte ptr [ESI + 0xad],0x0     ; clear tryingToCloak AFTER
```
Semantically: "force decloak if state is in CLOAKING-progress OR we've already fully cloaked". Makes sense — handles the case where StopCloaking arrives while cloak is mid-transition or already complete. Doc's narrative description holds; only the field label is wrong.

### C2 — HIGH — Event 0x00800078 mislabeled
**Doc table** (line 239):
| 0x00800078 | ET_CLOAK_BEGINNING | CloakComplete: state -> CLOAKED(3) |
**Binary string table** at 0x009106a0/0x009106b4:
- `ET_CLOAK_COMPLETED` (no specific ID-string mapping in the data; named in the string block)
- `ET_CLOAK_BEGINNING`

Per xref analysis:
- 0x00800077 ↔ posted ONLY at FUN_0055f275 (BeginCloak path of FUN_0055f110). This is **ET_CLOAK_BEGINNING**.
- 0x00800078 ↔ posted at FUN_0055f538 (InstantCloak), FUN_0055f725 (CloakComplete), FUN_00489470/00489570/00537be0 (downstream handlers). This is **ET_CLOAK_COMPLETED**.

Doc swaps the meaning: it labels 0x00800078 as ET_CLOAK_BEGINNING; it should be ET_CLOAK_COMPLETED. The 0x00800077 ET_CLOAK_BEGINNING event is **missing entirely from the doc's table**.

### C3 — MEDIUM — Default values CAN be verified, and "3.0 seconds" is wrong
**Doc says** (line 516-518): "transition time claim of '3.0 seconds' cannot be verified from static analysis alone since DAT_008e4e1c is a runtime-modifiable global."
**Binary at 0x008e4e1c**: `0x40A00000` = **5.0f**.
**Binary at 0x008e4e20**: `0x3F800000` = **1.0f**.
Both ARE statically determinable from the .rdata section. OpenBC's 3.0-second claim is wrong by 67% — cloaks take 5 seconds in stock STBC. Shield delay is 1 second.

### C4 — LOW — Doc ctor address Ghidra-named "SensorSubsystem_Ctor"
**Doc says** (line 13): "Constructor: FUN_00566d10"
**Ghidra currently calls** 0x00566d10 `SensorSubsystem_Ctor`.
The function's BEHAVIOR matches CloakingSubsystem ctor exactly (sets vtable to 0x00892eac, inits +0xAC/+0xB0/+0xB4/+0xB8/+0xBC/+0xA8/+0xC4/+0xC8, sets +0xC0 = 2). Doc's claim is correct; the Ghidra symbol is mis-named (likely a pre-v5 annotation script error). Worth a rename to `CloakingSubsystem_Ctor` in future Ghidra cleanup work.

## Clarifications (Clar)

### Clar1 — Two event posters in FUN_0055f110 are distinct paths
The doc lists FUN_0055f110 as "BeginCloaking/BeginDecloaking" combined. Confirmed: `param_2 == 1` → cloak path, `param_2 != 1` (called as 0) → decloak path. Cloak path posts 0x00800077 (ET_CLOAK_BEGINNING) NOT 0x00800079 — the doc's "Step 5: Sets state = 2 (CLOAKING), timer = 0; Calls FUN_0055f660" misses the event post for cloak begin. Decloak path correctly posts 0x00800079. So there are two `&DAT_008000XX` events posted in this function, one per direction.

### Clar2 — FUN_0055e6b0 is NOT a generic SetupCloakEffect
Doc lists it as "SetupCloakEffect — Configures NiNode for cloak visual". Decompile shows it does much more:
- Calls FUN_00593270 (which doc claims "manipulates the ship's scene graph" — confirmed; this is the function that disables shield rendering)
- Calls FUN_0055e840 (InitCloakProperties — sets up NiMaterial/NiShade per doc)
- If ship is player's own (FUN_004069b0 = GetPlayerShip), allocates +0x148-byte NiNode if +0xA8 NULL via FUN_00718cb0 + FUN_007f3fc0, then refcount-decrement old + ref-increment new
- Sets effectNode+0x120 = 0 (alpha base reset) and increments +0xD4 (dirty flag)
- Walks parent chain looking for &DAT_009a1870 (probably scene root sentinel)
Doc's role description is roughly correct but underspecified; the function does scene-graph mutation, not just property setup.

### Clar3 — "Cloak" sound at 0x008e42c8 (also confirms "Uncloak" at 0x008e4eb8)
Both string addresses byte-confirmed via search_strings.

## Open Questions (OQ)

### OQ1 — Does 0x00800076 (ET_REPAIR_LIST_PRIORITY) relate to cloak?
Not investigated this session; doc mentions cloak in relation to repair queue but not by event ID. Could be cross-referenced via cloak's xref set.

### OQ2 — Where does ET_CLOAK_BEGINNING (0x00800077) get consumed?
Only one xref: posted at 0x0055f275 in FUN_0055f110. No registered handler found in this validation session. The event may be consumed by UI/Python only, not by C++ subsystems — meaning it serves as a notification for other parts of the game to react to cloak start, without internal C++ behavior depending on it.

### OQ3 — Reader address claim 0x005b2660
Doc references reader code at 0x005b2660. The actual `(uDirtyFlags & 0x40)` cloak-bit branch in FUN_005b21c0 is around 0x005b25xx-0x005b25YY range based on the decomp structure. The exact instruction-level address claim wasn't verified — only the functional path. Worth nailing down the precise address if revisiting.

## Hindsight (H)

### H1 — Doc's "Comparison with OpenBC" section is now actionable
Now that defaults are confirmed (CloakTime = 5.0f, ShieldDelay = 1.0f), the OpenBC spec at `../OpenBC/docs/...` (no cloak doc identified in CLAUDE.md) needs an update. The state-value mapping (0/2/3/5 vs OpenBC's 0/1/2/3) is correctly flagged. Also: OpenBC's "3.0s" should be 5.0s.

### H2 — Ghidra symbol `SensorSubsystem_Ctor` at 0x00566d10 should be renamed
This is one of the annotation-script artifacts CLAUDE.md warns about ("known-wrong function names"). The body's behavior matches CloakingSubsystem ctor exactly, NOT a sensor ctor. Pre-v5 annotation script error.

## Cross-references confirmed/created
- ship+0x2DC = CloakingSubsystem* (consistent with stateupdate.md and tg-hierarchy-vtables)
- cloak+0x9C = isOn (PoweredSubsystem inheritance — used in StateUpdate dirty-bit 0x40)
- cloak+0xAC = isFullyCloaked (ShipClass::IsCloaked dependency)
- cloak+0xAD = tryingToCloak (intent bit)
- cloak+0xB0 = state (state machine value 0/2/3/5)
- cloak+0xB4 = timer
- vtable 0x00892EAC (CloakingSubsystem); parent vtable 0x00892D98 (PoweredSubsystem)
- ship+0x2C0 = ShieldGenerator (also used in CloakDisengageRestoreShield, gameplay foundation #2 alignment)

## Validation status verdict
**`partial`** — doc has 2 high-severity corrections (StopCloaking byte label C1, event 0x00800078 mislabeled C2) plus a recoverable claim (defaults DO exist, doc said they couldn't be verified C3) plus a Ghidra symbol artifact (C4). Wire format / state machine / event posting flow are otherwise SOLID. Recommend re-publication with the 4 corrections; default values noted; ET_CLOAK_BEGINNING (0x00800077) added to table.

## v5 confidence summary
| Claim category | Confidence | Notes |
|----|----|----|
| State machine 4-active + 2-ghost | high | Byte-confirmed in 4 fns |
| Field offsets (+0xAC/+0xAD/+0xB0/+0xB4) | high | Cross-checked across writer/reader/StateUpdate |
| Event IDs E3/E5/79/7A/7B | high | All PUSH-confirmed or xref-confirmed |
| Event 0x00800078 label | **wrong** | Should be ET_CLOAK_COMPLETED not BEGINNING |
| Default CloakTime 5.0f / ShieldDelay 1.0f | high | Raw .rdata bytes confirm |
| FUN_005b17f0 / FUN_005b21c0 ship+0x2DC + 0x40 flag | high | Existing plate comments + this validation |
| Visual constants DAT_0088c5ac/0088cb58/00892c90/00892c94 | high | Decomp confirms |
| Cloak "InstantCloak"/"InstantDecloak" semantics | medium | Decompiled but not deeply checked |
| 0x00800077 (ET_CLOAK_BEGINNING) | high | Single posting xref, doc missed it |
