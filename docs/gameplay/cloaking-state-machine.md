> [docs](../README.md) / [gameplay](README.md) / cloaking-state-machine.md

---
title: Cloaking Device State Machine — Complete Reverse Engineering
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
  - claim: "ship+0x2DC = CloakingSubsystem* (named slot, populated by Ship__SetupProperties)"
    address: 0x005B3FB0
    function: Ship__SetupProperties
    confidence: high
    note: "Cross-anchored with stateupdate-subsystem-wire-format.md and tg-hierarchy-vtables.md."
  - claim: "CloakingSubsystem object layout: +0x9C isOn (byte, PoweredSubsystem inherited), +0xAC isFullyCloaked (byte), +0xAD tryingToCloak (byte), +0xB0 state (int, 0/2/3/5 active, 1/4 ghost), +0xB4 timer (float)"
    address: 0x0055E2B0
    function: CloakingSubsystem_Ctor
    confidence: high
    note: "C4 META-CASCADE REV 2 (2026-05-28): ctor address corrected from 0x00566D10 to 0x0055E2B0 per sensor/hull RE. 0x00566D10 is SensorSubsystem_Ctor. All 5 field offsets remain cross-checked across ctor zero-inits, tick fn, StopCloaking, StateUpdate writer, and ShipClass::IsCloaked."
  - claim: "CloakingSubsystem vtable at 0x00892C04; parent vtable 0x00892D98 (PoweredSubsystem)"
    address: 0x00892C04
    confidence: high
    note: "C4 META-CASCADE REV 2 (2026-05-28): vtable corrected from 0x00892EAC to 0x00892C04 per sensor/hull RE. 0x00892EAC is SensorSubsystem vtable. Parent ctor FUN_00562240 confirmed via PTR_FUN_00892d98 install in genuine CloakingSubsystem ctor body at 0x0055E2B0."
  - claim: "ship+0x2C0 = ShieldGenerator* (cross-anchored from shield-system.md and power-system.md C1 slot table)"
    address: 0x005B3FB0
    function: Ship__SetupProperties
    confidence: high
  - claim: "CloakingSubsystem_Ctor at 0x0055E2B0 sets vtable 0x00892C04, calls FUN_00562240 (PoweredSubsystem base ctor), zeros +0xAC/+0xB0/+0xB4/+0xB8/+0xBC/+0xA8/+0xC4/+0xC8, sets +0xC0=2, delegates state-machine init to FUN_0055F930"
    address: 0x0055E2B0
    function: CloakingSubsystem_Ctor
    confidence: high
    note: "C4 META-CASCADE REV 2 (2026-05-28): genuine CloakingSubsystem_Ctor located at 0x0055E2B0 with vtable 0x00892C04 per sensor/hull RE. Prior rev 1 claim that 0x00566D10 was the cloak ctor (mis-renamed in Ghidra as SensorSubsystem_Ctor) was wrong — 0x00566D10 IS SensorSubsystem_Ctor. Ghidra plates corrected via Block 2 B follow-up."
  - claim: "CloakingSubsystem::Update tick fn at FUN_0055E500 reads +0xB0 (state) and +0xB4 (timer); state 2 counts timer UP, state 5 counts DOWN; energy failure at state 3 triggers force-decloak via efficiency (+0x94) < DAT_0088D4EC"
    address: 0x0055E500
    function: CloakingSubsystem_Update
    confidence: high
  - claim: "BeginCloak path of FUN_0055F110 posts event 0x00800077 (ET_CLOAK_BEGINNING) at 0x0055F275 — sole xref for that event"
    address: 0x0055F275
    function: BeginCloaking
    confidence: high
    note: "C2 — corrects prior doc's missing-from-table 0x00800077 event."
  - claim: "InstantCloak at FUN_0055F538 posts event 0x00800078 (ET_CLOAK_COMPLETED)"
    address: 0x0055F538
    function: InstantCloak
    confidence: high
    note: "C2 — corrects prior doc's labeling of 0x00800078 as ET_CLOAK_BEGINNING."
  - claim: "CloakComplete at FUN_0055F725 posts event 0x00800078 (ET_CLOAK_COMPLETED) when state transitions 2->3"
    address: 0x0055F725
    function: CloakComplete
    confidence: high
    note: "C2."
  - claim: "StopCloaking at 0x0055F393 checks isFullyCloaked at +0xAC (NOT tryingToCloak at +0xAD); semantic meaning correct (force decloak if mid-cloak or fully cloaked), field label was wrong"
    address: 0x0055F393
    function: CloakingSubsystem_StopCloaking
    confidence: high
    note: "C1 — full disasm: CMP byte ptr [ESI + 0xAC],0x1 / JNZ 0055f3a5; then MOV byte ptr [ESI + 0xAD],0x0 clears tryingToCloak AFTER."
  - claim: "SetupCloakEffect at FUN_0055E6B0 calls FUN_00593270 (scene-graph mutation — same fn used to disable shield rendering), InitCloakProperties FUN_0055E840, and allocates +0x148-byte NiNode at +0xA8 (via FUN_00718CB0 + FUN_007F3FC0) if player ship's effectNode is NULL"
    address: 0x0055E6B0
    function: SetupCloakEffect
    confidence: high
    note: "Clar2 — role description correct in prior doc but understated. Function does scene-graph mutation, not just property setup."
  - claim: "DAT_008E4E1C = CloakTime default = 5.0f (raw bytes 00 00 A0 40 at 0x008E4E1C, IEEE 0x40A00000)"
    address: 0x008E4E1C
    confidence: high
    note: "C3 — corrects prior doc's claim that default could not be statically determined. OpenBC clean-room spec uses 3.0s — needs cascade update."
  - claim: "DAT_008E4E20 = ShieldDelay default = 1.0f (raw bytes 00 00 80 3F at 0x008E4E20, IEEE 0x3F800000)"
    address: 0x008E4E20
    confidence: high
    note: "C3 — corrects prior doc's claim that default could not be statically determined."
  - claim: "DAT_0088D4EC = energy-efficiency threshold for state-3 auto-decloak (float)"
    address: 0x0088D4EC
    confidence: high
  - claim: "DAT_0088C5AC = shimmer alpha threshold (UpdateNodeAlpha)"
    address: 0x0088C5AC
    confidence: high
  - claim: "DAT_00892C94 = random scale factor (UpdateNodeAlpha)"
    address: 0x00892C94
    confidence: high
  - claim: "DAT_00892C90 = decloak scale factor (UpdateNodeAlpha)"
    address: 0x00892C90
    confidence: high
  - claim: "DAT_0088CB58 = alpha offset (UpdateNodeAlpha)"
    address: 0x0088CB58
    confidence: high
  - claim: "DAT_0088BA90 = alpha scale (UpdateVisibility writes effectNode+0x120)"
    address: 0x0088BA90
    confidence: high
  - claim: "Event ID 0x00800077 = ET_CLOAK_BEGINNING; string at 0x009106B4"
    address: 0x009106B4
    confidence: high
    note: "C2 — added this pass. Sole posting at 0x0055F275 (BeginCloak)."
  - claim: "Event ID 0x00800078 = ET_CLOAK_COMPLETED; string at 0x009106A0"
    address: 0x009106A0
    confidence: high
    note: "C2 — corrects prior doc's ET_CLOAK_BEGINNING label. Posted at FUN_0055F538 (InstantCloak), FUN_0055F725 (CloakComplete), FUN_00489470, FUN_00489570, FUN_00537BE0."
  - claim: "Event ID 0x00800079 = ET_DECLOAK_BEGINNING; posted in FUN_0055F110 decloak path"
    address: 0x0055F110
    confidence: high
  - claim: "Event ID 0x0080007A = ET_DECLOAK_COMPLETED; posted at FUN_0055F7F0 and FUN_0055F560"
    address: 0x0055F7F0
    confidence: high
    note: "FUN_0055F7F0 = CloakDisengageRestoreShield, cross-anchored from power-system.md."
  - claim: "Event ID 0x0080007B = shield re-enable delayed event; posted at FUN_0055F110 cloak path + FUN_0055F7F0 + FUN_0055F3E0"
    address: 0x0055F7F0
    confidence: high
  - claim: "Event ID 0x008000E3 = ET_START_CLOAKING (subsystem-side handler registered at 0x0055E4D0, PUSH 0x8000e3)"
    address: 0x0055E4D0
    confidence: high
  - claim: "Event ID 0x008000E5 = ET_STOP_CLOAKING (subsystem-side handler registered at 0x0055E4E9, PUSH 0x8000e5)"
    address: 0x0055E4E9
    confidence: high
  - claim: "Event ID 0x008000E2 = ET_START_CLOAKING (MultiplayerGame side, registered in MultiplayerGame_Ctor)"
    address: 0x0069E590
    confidence: high
  - claim: "Event ID 0x008000E4 = ET_STOP_CLOAKING (MultiplayerGame side)"
    address: 0x0069E590
    confidence: high
  - claim: "String \"Cloak\" at 0x008E42C8 (cloak sound effect ID, byte-confirmed)"
    address: 0x008E42C8
    confidence: high
    note: "Clar3."
  - claim: "String \"Uncloak\" at 0x008E4EB8 (decloak sound effect ID, byte-confirmed)"
    address: 0x008E4EB8
    confidence: high
    note: "Clar3."
  - claim: "StateUpdate writer FUN_005B17F0 reads ship+0x2DC (cloak), then cloak+0x9C (isOn); compares to tracker+0x2E (lastCloakState); sets dirty flag 0x40 on change"
    address: 0x005B17F0
    function: StateUpdate_Write
    confidence: high
    note: "Wire emits 1-bit WriteBool_Bit of cloak's isOn at 0x005B1E6A-0x005B1E73 (CALL 0x006CF770)."
  - claim: "StateUpdate reader FUN_005B21C0 — if (0x40 & flags && ship+0x2DC != 0), reads bit; bit=0 -> StopCloaking (FUN_0055F380); bit=1 -> StartCloaking (FUN_0055F360)"
    address: 0x005B21C0
    function: StateUpdate_Read
    confidence: medium
    note: "OQ2 — functional path verified; exact byte address 0x005B2660 cited in prior doc not pinned to a specific instruction."
  - claim: "ShipClass::IsCloaked at 0x005AC450 reads ship+0x2DC; if NULL returns 0; else returns *(char*)(cloak+0xAC) == 1 (isFullyCloaked byte). Returns true ONLY during state==3 (CLOAKED), not during transitions."
    address: 0x005AC450
    function: ShipClass_IsCloaked
    confidence: high
  - claim: "DeathWhileCloaked at FUN_0055F930 reads ship+0x9C (isOn). If non-zero: calls DisableSubsystem (FUN_00562630), then if state==3 || tryingToCloak(+0xAD)==1, runs StopCloaking + BeginDecloaking."
    address: 0x0055F930
    function: DeathWhileCloaked
    confidence: high
companions:
  - docs/gameplay/power-system.md
  - docs/gameplay/shield-system.md
  - docs/protocol/stateupdate-subsystem-wire-format.md
  - docs/engine/tg-hierarchy-vtables.md
  - ../OpenBC/docs/cloaking-system.md
---

> [!NOTE]
> **2026-05-28 (revision 2) — C4 META-CASCADE REVERSAL.** The original C4 correction in this doc renamed the WRONG Ghidra function. Sensor/hull RE (see `.claude/agent-memory/game-archaeology-specialist/sensor-hull-subsystem-validation-20260528.md`) confirmed that **0x00566D10 IS the SensorSubsystem_Ctor** (vtable 0x00892EAC, "SensorSubsystem::Handle*" strings prove identity), and the **genuine CloakingSubsystem_Ctor lives at 0x0055E2B0** (vtable 0x00892C04, state-machine init via FUN_0055F930). The cloaking-cascade pass had mis-renamed 0x00566D10 in Ghidra; the Ghidra plates have since been corrected via the Block 2 B follow-up. All CloakingSubsystem_Ctor address claims in this doc are updated from 0x00566D10 -> 0x0055E2B0 and vtable from 0x00892EAC -> 0x00892C04 where applicable. The state machine, wire format, event IDs (C1/C2/C3) and field offsets remain v5-validated.

> [!NOTE]
> **v5 re-validation 2026-05-28 — 4 corrections (2 HIGH + 1 MED + 1 LOW) + 3 clarifications + 2 OQs**. Core state machine and wire format byte-confirmed. C1 HIGH: StopCloaking field at +0xAC (isFullyCloaked), NOT +0xAD (tryingToCloak); C2 HIGH: Event 0x00800078 is ET_CLOAK_COMPLETED not ET_CLOAK_BEGINNING (and 0x00800077 IS the missing ET_CLOAK_BEGINNING); **C3 MED: CloakTime default is 5.0f (NOT 3.0f) — OpenBC clean-room spec needs cascade update**; C4 LOW: ctor at 0x00566D10 mis-Ghidra-named as SensorSubsystem_Ctor (corrected separately).
>
> - **C1 (HIGH)**: StopCloaking at 0x0055F393 checks `isFullyCloaked` at `+0xAC`, NOT `tryingToCloak` at `+0xAD` as prior doc claimed. Disasm: `CMP byte ptr [ESI + 0xAC],0x1`. Semantic meaning correct ("force decloak if mid-cloak or fully cloaked"); only the field label was wrong.
> - **C2 (HIGH)**: Event 0x00800078 was labeled `ET_CLOAK_BEGINNING` in the prior doc's Event IDs table. Binary truth: string at 0x009106A0 = `ET_CLOAK_COMPLETED`, and the missing 0x00800077 (string at 0x009106B4) IS the real `ET_CLOAK_BEGINNING`. Posted only at FUN_0055F275 (BeginCloak path).
> - **C3 (MED)**: Default `CloakTime = 5.0f` (raw bytes `00 00 A0 40` at 0x008E4E1C) and `ShieldDelay = 1.0f` (raw bytes `00 00 80 3F` at 0x008E4E20) ARE statically determinable from .rdata. Prior doc said they could not be verified from static analysis. **OpenBC clean-room spec uses "3.0 seconds" — that's off by 67%. Cloak transition is 5 seconds in stock STBC.**
> - **C4 (LOW) — REVERSED 2026-05-28 (rev 2)**: The original C4 correction renamed the wrong Ghidra function. Binary truth: **0x00566D10 IS SensorSubsystem_Ctor** (vtable 0x00892EAC), and **CloakingSubsystem_Ctor lives at 0x0055E2B0** (vtable 0x00892C04, state-machine init via FUN_0055F930). All CloakingSubsystem_Ctor address claims in this doc are updated accordingly. See the rev 2 NOTE block at the top. Reference: `.claude/agent-memory/game-archaeology-specialist/sensor-hull-subsystem-validation-20260528.md`.

---

# Cloaking Device State Machine — Complete Reverse Engineering Analysis

## Overview

The CloakingSubsystem is a PoweredSubsystem subclass that manages ship cloaking in STBC. It uses a state machine with a transition timer, interacts with shields through a delayed re-enable mechanism, and controls ship visibility through NiNode alpha manipulation.

**Vtable**: `0x00892C04` (CloakingSubsystem) [v5-validated 2026-05-28 — meta-cascade rev 2; was previously 0x00892EAC which is actually SensorSubsystem]
**Parent vtable**: `0x00892D98` (PoweredSubsystem, set by FUN_00562240) [v5-validated 2026-05-28]
**Constructor**: `FUN_0055E2B0` [v5-validated 2026-05-28 — meta-cascade rev 2; was previously claimed at 0x00566D10 which is actually SensorSubsystem_Ctor — see C4 rev 2 below]
**Destructor**: `FUN_00566E50` (scalar deleting) — pending rev 2 review (the dtor address may also have been mis-attributed by the cloaking-cascade pass)

## Object Layout [v5-validated 2026-05-28]

```
Offset  Size  Type    Field                   Notes
------  ----  ------  ----------------------  -----
+0x00   4     ptr     vtable                  -> 0x00892C04  (meta-cascade rev 2; was 0x00892EAC which is SensorSubsystem)
...           ...     (inherited from PoweredSubsystem via FUN_00562240 -> FUN_0056b970)
+0x18   4     ptr     subsystem property      (inherited)
+0x34   4     float   maxPower                (inherited, used in energy check FUN_0056c350)
+0x3C   4     float   maxCondition(?)         (inherited)
+0x40   4     ptr     ownerShip               Ship* that owns this subsystem
+0x88   4     float   currentPowerDraw        (inherited, managed by FUN_00562470)
+0x8C   4     float   actualPower             (inherited)
+0x90   4     float   powerMultiplier         Init to 1.0f (inherited)
+0x94   4     float   efficiency              ratio = actualPower/maxPower (inherited)
+0x98   4     float   conditionRatio          (inherited)
+0x9C   1     byte    isOn                    PoweredSubsystem::IsOn (Enable/Disable toggle)
+0xA0   4     int     powerMode               0/1/2 (inherited)
+0xA4   1     byte    isNetworkable           (inherited, controls MP event forwarding)
+0xA8   4     ptr     cloakEffectNode         NiNode* for visual cloak effect
+0xAC   1     byte    isFullyCloaked          Set to 1 when state reaches CLOAKED(3) [load-bearing for C1]
+0xAD   1     byte    tryingToCloak           1=player wants cloak on, 0=wants off
+0xB0   4     int     state                   State machine value (see below)
+0xB4   4     float   timer                   Accumulates delta time during transitions
+0xB8   4     ?       (unused, init 0)
+0xBC   4     ?       (unused, init 0)
+0xC0   4     int     (init 2)                Possibly render mode
+0xC4   4     ?       (init 0)
+0xC8   4     ?       (init 0)
```

Ship stores the CloakingSubsystem pointer at **ship+0x2DC** [v5-validated 2026-05-28 — cross-anchored with stateupdate-subsystem-wire-format.md and tg-hierarchy-vtables.md].

### C4 — Ghidra symbol for ctor mis-labeled [REVERSED 2026-05-28 (rev 2)]

> [!IMPORTANT]
> **C4 REV 2 — META-CASCADE REVERSAL.** The original C4 correction (rev 1) renamed the wrong Ghidra function. Sensor/hull RE confirmed:
>
> - **0x00566D10 IS the SensorSubsystem_Ctor** (vtable 0x00892EAC; "SensorSubsystem::Handle*" debug strings prove identity)
> - **Genuine CloakingSubsystem_Ctor lives at 0x0055E2B0** (vtable 0x00892C04, state-machine init via FUN_0055F930)
>
> The cloaking-cascade pass had mis-renamed 0x00566D10 in Ghidra; the Ghidra plates were corrected via the Block 2 B follow-up. This doc's CloakingSubsystem_Ctor address claim has been updated from 0x00566D10 -> **0x0055E2B0** throughout (Vtable / Constructor lines above; Function Address Summary table below).
>
> Genuine CloakingSubsystem ctor at 0x0055E2B0 (the actual constructor):
>
> - Writes vtable `0x00892C04` (CloakingSubsystem — meta-cascade truth)
> - Calls `FUN_00562240` (PoweredSubsystem base ctor, installs parent vtable `0x00892D98`)
> - Zeros the cloak state fields (+0xAC, +0xB0, +0xB4, +0xB8, +0xBC, +0xA8, +0xC4, +0xC8)
> - Sets +0xC0 = 2 (the "render mode?" field)
> - State-machine init delegated to FUN_0055F930
>
> Reference packet: `.claude/agent-memory/game-archaeology-specialist/sensor-hull-subsystem-validation-20260528.md`.

> [!NOTE]
> **Original C4 text (rev 1, SUPERSEDED)** — Ghidra DB currently labels the function at 0x00566D10 as `SensorSubsystem_Ctor`. This is a pre-v5 annotation-script artifact. The function body matches CloakingSubsystem ctor exactly: writes vtable 0x00892EAC (CloakingSubsystem); calls FUN_00562240 (PoweredSubsystem base ctor, installs parent vtable 0x00892D98); zeros +0xAC, +0xB0, +0xB4, +0xB8, +0xBC, +0xA8, +0xC4, +0xC8; sets +0xC0 = 2 (the "render mode?" field). The doc's address claim (FUN_00566d10) is correct. Ghidra rename pending in a separate handoff (target: CloakingSubsystem_Ctor). **(rev 1 reasoning was wrong — both the Ghidra label AND the doc's address claim were wrong, see rev 2 IMPORTANT block above)**

## State Machine [v5-validated 2026-05-28]

### Active States (4 states, verified)

| Value | Name        | Timer Behavior           | Entered From          | Exits To               |
|-------|-------------|--------------------------|----------------------|-------------------------|
| 0     | DECLOAKED   | timer irrelevant         | FUN_0055f7f0         | state 2 (via tick)      |
| 2     | CLOAKING    | timer counts UP by dt    | FUN_0055f110(cloak)  | state 3 (timer full)    |
| 3     | CLOAKED     | timer irrelevant         | FUN_0055f6d0         | state 5 (via tick)      |
| 5     | DECLOAKING  | timer counts DOWN by dt  | FUN_0055f110(declk)  | state 0 (timer empty)   |

### Ghost States (never assigned, dead code)

States 1 and 4 are checked in `IsCloaking()` and `IsDecloaking()` SWIG wrappers and in
the visibility function FUN_0055ee10, but are **never written** to `+0xB0` anywhere in the
binary. They are vestiges of a planned 6-state design that was collapsed to 4 active states.

- State 1: checked alongside state 2 in `IsCloaking` (returns true for 1 or 2)
- State 4: checked alongside state 5 in `IsDecloaking` (returns true for 4 or 5)

### State Transition Diagram

```
  StartCloaking()           timer reaches 1.0        StopCloaking()         timer reaches 0.0
  FUN_0055f360         FUN_0055f6d0              FUN_0055f380          FUN_0055f7f0
       |                     |                        |                     |
  DECLOAKED(0) ---> CLOAKING(2) ---> CLOAKED(3) ---> DECLOAKING(5) ---> DECLOAKED(0)
       ^                                                                    |
       +--------------------------------------------------------------------+

  Also: CLOAKED(3) ---> DECLOAKING(5) via energy failure (efficiency < threshold in tick)
```

## Transition Timer [v5-validated 2026-05-28]

**Global**: `DAT_008e4e1c` = **CloakTime = 5.0f** (default, settable via `CloakingSubsystem_SetCloakTime`)
**Global**: `DAT_008e4e20` = **ShieldDelay = 1.0f** (default, settable via `CloakingSubsystem_SetShieldDelay`)

Both are **class-level globals**, NOT per-instance fields. All cloaking devices in the game share the same CloakTime and ShieldDelay values.

### C3 — Default constants are statically determinable

Prior doc said: "Default values: These are set from the .rdata section. Without runtime Python modification, both remain at their compiled-in defaults." — and then claimed in the OpenBC comparison that "transition time claim of '3.0 seconds' cannot be verified from static analysis alone".

Binary truth from raw .rdata:

| Address | Raw bytes | IEEE 754 | Field | Default |
|---------|-----------|----------|-------|---------|
| 0x008E4E1C | `00 00 A0 40` | 0x40A00000 | CloakTime | **5.0f** |
| 0x008E4E20 | `00 00 80 3F` | 0x3F800000 | ShieldDelay | **1.0f** |

Both ARE statically determinable. `CloakingSubsystem_SetCloakTime` and `SetShieldDelay` SWIG wrappers allow Python overrides at runtime, but in the absence of Python override the cloak transition takes **5 seconds** and the shield re-enable delay is **1 second**.

> **OpenBC clean-room cascade (2026-05-28)**: The OpenBC clean-room spec uses "3.0 seconds" for cloak transition. Binary truth: CloakTime = 5.0f at DAT_008E4E1C. OpenBC clean-room implementations should update to 5.0 seconds for stock parity.

### Tick Function: FUN_0055e500 [v5-validated 2026-05-28]

```c
// FUN_0055e500(this, deltaTime) -- CloakingSubsystem::Update
void CloakingSubsystem_Update(CloakingSubsystem* this, float deltaTime)
{
    // Call parent tick (PoweredSubsystem::Update)
    FUN_00562470(this, deltaTime);

    int state = this->state;  // +0xB0

    if (state == 2) {  // CLOAKING
        // Timer counts UP
        this->timer += deltaTime;                    // +0xB4
        float progress = this->timer / CloakTime;   // DAT_008e4e1c = 5.0f

        if (progress >= 1.0f) {
            progress = 1.0f;
            CloakComplete(this);     // FUN_0055f6d0 -> state=3
        }
    }
    else if (state == 5) {  // DECLOAKING
        // Timer counts DOWN
        this->timer -= deltaTime;                    // +0xB4
        float progress = this->timer / CloakTime;

        if (progress <= 0.0f) {
            progress = 0.0f;
            DecloakComplete(this);   // FUN_0055f7f0 -> state=0
        }
    }
    else {
        goto check_intents;
    }

    // Update visual transparency
    UpdateVisibility(this, progress);   // FUN_0055e640

check_intents:
    // Only if +0x9C (isOn) is true
    if (!this->isOn) {
        // Call parent tick again (energy recalculation)
        FUN_00562470(this, deltaTime);
        return;
    }

    state = this->state;
    bool notInCloakChain = (state != 1 && state != 2 && state != 3);
    bool inCloakChain = (state != 4 && state != 5 && state != 0);
    // Note: effectively notInCloakChain = (state==0||state==4||state==5)
    //                    inCloakChain = (state==1||state==2||state==3)

    if (this->tryingToCloak == 1 && notInCloakChain) {
        // Wants to cloak and not already cloaking
        BeginCloaking(this, 1);    // FUN_0055f110(this, 1) -> state=2
        return;
    }

    if (this->tryingToCloak == 0 || !inCloakChain) {
        if (state != 3) return;     // Not fully cloaked, nothing to do
        if (this->efficiency >= ENERGY_THRESHOLD) return;  // DAT_0088d4ec
        // Energy failure: force decloak
        StopCloaking(this);    // FUN_0055f380
    }

    BeginDecloaking(this, 0);  // FUN_0055f110(this, 0) -> state=5
}
```

### Key Transition Functions

#### FUN_0055f360 - StartCloaking (user-facing)
Address: `0x0055f360`
```c
void CloakingSubsystem_StartCloaking(this) {
    this->vtable[0x7C/4]();   // virtual call (likely base class StartCloaking hook)
    this->tryingToCloak = 1;  // +0xAD = 1
    // Actual state transition happens in next tick via check_intents
}
```

#### FUN_0055f380 - StopCloaking (user-facing) [v5-validated 2026-05-28]

### C1 — StopCloaking gate checks isFullyCloaked (+0xAC), not tryingToCloak (+0xAD)

Address: `0x0055f380`

**Prior doc said**:
```c
if (this->state == 1 || this->state == 2 || this->tryingToCloak == 1) {
    BeginDecloaking(this, 0);
}
```

**Binary truth at 0x0055F393**: `CMP byte ptr [ESI + 0xAC], 0x1` — that's **isFullyCloaked** (+0xAC), NOT tryingToCloak (+0xAD).

Disassembly:

```
0055f383: MOV  EAX,dword ptr [ESI + 0xb0]   ; state
0055f389: CMP  EAX,0x1                       ; ghost CLOAKING-1
0055f38c: JZ   0055f39c
0055f38e: CMP  EAX,0x2                       ; CLOAKING
0055f391: JZ   0055f39c
0055f393: CMP  byte ptr [ESI + 0xac],0x1     ; +0xAC = isFullyCloaked  <-- C1
0055f39a: JNZ  0055f3a5
0055f39c: PUSH 0                              ; call BeginDecloaking(this, 0)
              CALL BeginDecloaking
0055f3a5: MOV  byte ptr [ESI + 0xad],0x0     ; clear tryingToCloak AFTER
```

Corrected pseudocode:

```c
void CloakingSubsystem_StopCloaking(this) {
    if (this->state == 1 || this->state == 2 || this->isFullyCloaked == 1) {  // +0xAC
        BeginDecloaking(this, 0);   // FUN_0055f110(this, 0)
    }
    this->tryingToCloak = 0;        // +0xAD = 0 (cleared AFTER decloak begin)
    this->vtable[0x80/4]();         // virtual call (likely base class StopCloaking hook)
}
```

Semantic meaning ("force decloak if state is in CLOAKING-progress OR we've already fully cloaked") was correct in prior doc — only the field label was wrong. Handles the case where StopCloaking arrives while cloak is mid-transition or already complete.

#### FUN_0055f110 - BeginCloaking/BeginDecloaking (internal) [v5-validated 2026-05-28]
Address: `0x0055f110`

When `param_1 == 1` (cloaking):
1. Checks energy via FUN_0056c350 (recursive power check)
2. If insufficient energy, returns without transition
3. **Posts ET_CLOAK_BEGINNING event (0x00800077)** at 0x0055F275 (Clar1 — sole xref for this event)
4. Creates NiTimeController animation sequences
5. If ship has a shield subsystem (ship+0x2C0), creates a delayed shield-hide event with event 0x0080007B and delay = ShieldDelay (`_DAT_008e4e20`)
6. Creates/starts a "Cloak" sound effect (string "Cloak" at 0x008e42c8 [v5-validated 2026-05-28])
7. Sets state = 2 (CLOAKING), timer = 0
8. Calls FUN_0055f660 -> state=2, plays "Cloak" animation on NiNode

When `param_1 == 0` (decloaking):
1. Posts ET_DECLOAK_BEGINNING event (0x00800079)
2. If state != 2 (not mid-cloak), sets timer = CloakTime (to count down from max)
3. Sets state = 5 (DECLOAKING)
4. Calls FUN_0055f770 -> state=5, plays "Uncloak" animation (string "Uncloak" at 0x008e4eb8 [v5-validated 2026-05-28])

> **Clar1 — both directions of FUN_0055F110 post events**: prior doc documented only the decloak path's 0x00800079 post and missed the cloak path's 0x00800077 (ET_CLOAK_BEGINNING) post. Both directions now documented.

#### FUN_0055f6d0 - CloakComplete (timer finished) [v5-validated 2026-05-28]
Address: `0x0055f6d0` (entry); event post at FUN_0055F725
```c
void CloakComplete(this) {
    this->state = 3;                // CLOAKED
    // Post ET_CLOAK_COMPLETED event (0x00800078) at 0x0055F725  [C2]
    this->isFullyCloaked = 1;       // +0xAC = 1
    // Make ship invisible: ship->sceneNode->vtable[0x50](1)
}
```

#### FUN_0055f7f0 - DecloakComplete (timer finished) [v5-validated 2026-05-28]
Address: `0x0055f7f0` (also referred to as `CloakDisengageRestoreShield` — see [docs/gameplay/power-system.md](power-system.md) C4)
```c
void DecloakComplete(this) {
    this->state = 0;                // DECLOAKED
    // Post ET_DECLOAK_COMPLETED event (0x0080007A)

    // If ship has shield subsystem (ship+0x2C0):
    //   Create delayed event 0x0080007B at time = gameTime + ShieldDelay
    //   This re-enables the shield visual (flag |= 0x01)
    //   If shield HP <= 0, reset shield to 1.0 HP

    RestoreNiNode(this);            // FUN_0055e800
}
```

#### FUN_0055f538 - InstantCloak [v5-validated 2026-05-28]
Address: `0x0055f538` — posts ET_CLOAK_COMPLETED (0x00800078) [C2]. Used by SWIG `InstantCloak` Python wrapper for spawn/test scenarios.

## Event IDs [v5-validated 2026-05-28 — C2 applied]

| ID           | Name                  | String addr | Fired When                          |
|--------------|-----------------------|-------------|-------------------------------------|
| 0x008000E2   | ET_START_CLOAKING (MultiplayerGame request) | — | MultiplayerGame_Ctor registers (different namespace; see Multiplayer Event Registration below) |
| 0x008000E3   | ET_START_CLOAKING     | — | Network opcode 0x0E received (subsystem-side, registered at 0x0055E4D0) |
| 0x008000E4   | ET_STOP_CLOAKING (MultiplayerGame request) | — | MultiplayerGame_Ctor registers |
| 0x008000E5   | ET_STOP_CLOAKING      | — | Network opcode 0x0F received (subsystem-side, registered at 0x0055E4E9) |
| **0x00800077** | **ET_CLOAK_BEGINNING** | **0x009106B4** | **BeginCloaking: state -> CLOAKING(2). Posted at FUN_0055F275, sole xref. [C2 — added this pass]** |
| 0x00800078   | **ET_CLOAK_COMPLETED** [C2] | 0x009106A0 | CloakComplete (FUN_0055F725): state -> CLOAKED(3); also FUN_0055F538 (InstantCloak), FUN_00489470, FUN_00489570, FUN_00537BE0 |
| 0x00800079   | ET_DECLOAK_BEGINNING  | — | BeginDecloaking (FUN_0055F110 decloak path): state -> DECLOAKING(5) |
| 0x0080007A   | ET_DECLOAK_COMPLETED  | — | DecloakComplete (FUN_0055F7F0) and FUN_0055F560 (InstantDecloak): state -> DECLOAKED(0) |
| 0x0080007B   | (shield visibility)   | — | Delayed timer event for shield show/hide |
| 0x0080006C   | ET_SUBSYSTEM_STATUS   | — | Subsystem enabled/disabled |

**C2 reminder**: the event-ID column above used to label 0x00800078 as ET_CLOAK_BEGINNING. Binary truth: 0x00800078's string is `ET_CLOAK_COMPLETED` (at 0x009106A0), and the actual `ET_CLOAK_BEGINNING` is 0x00800077 (string at 0x009106B4). The 0x00800077 row was missing from the prior doc entirely.

## Shield Interaction

### Cloaking (shields go down)

When cloaking begins (FUN_0055f110, param=1):
1. **Shields do NOT immediately drop to 0 HP**
2. Instead, a **delayed event** (0x0080007B) is scheduled with the ship's shield subsystem at `ship+0x2C0` as the target. The delay is `ShieldDelay` ([v5-validated 2026-05-28] = 1.0f at DAT_008E4E20)
3. The event has flag `0xFEFF` (bit 8 cleared = non-persistent), meaning the shield visual element fades out over the ShieldDelay period
4. The shield subsystem itself is **disabled** via the PoweredSubsystem mechanism:
   - FUN_0055e6b0 (called from FUN_0055f3e0/InstantCloak and FUN_0055f660/CloakingComplete) calls `FUN_00593270(ownerShip)` which manipulates the ship's scene graph (Clar2 — same fn that disables shield rendering)
   - This effectively turns off shield rendering and prevents shield recharge

> **Clar2 — SetupCloakEffect (FUN_0055E6B0) does more than property setup**: the function calls FUN_00593270 (scene-graph mutation, same fn used to disable shield rendering), FUN_0055E840 (InitCloakProperties — sets up NiMaterial/NiShade), and if the ship is the player's own (FUN_004069B0 = GetPlayerShip) it allocates a +0x148-byte NiNode via FUN_00718CB0 + FUN_007F3FC0 when the player ship's effectNode (+0xA8) is NULL, then refcount-decrement old + ref-increment new. Sets effectNode+0x120 = 0 (alpha base reset) and increments +0xD4 (dirty flag). Walks parent chain looking for &DAT_009A1870 (probably scene root sentinel). The doc's "SetupCloakEffect" name is correct but understates the side effects.

### Decloaking (shields come back)

When decloaking completes (FUN_0055f7f0):
1. A **delayed event** (0x0080007B) with flag `|= 0x01` (persistent/enable) is created
2. The event fires at `gameTime + ShieldDelay` (= gameTime + 1.0f stock default) — shields don't return instantly
3. If the shield HP was at or below 0, it gets reset to 1.0
4. The shield subsystem re-enables and begins recharging normally

### Summary

- **During cloak**: Shields are functionally disabled (no absorption, no recharge, hidden)
- **Shield HP is NOT zeroed**: The HP value is preserved, but the subsystem is turned off
- **Re-enable delay**: After decloaking completes (state=0), there is an additional `ShieldDelay` (= 1.0f) seconds before shields become active again
- **All logic is in the cloak code**: FUN_0055f110, FUN_0055f3e0, FUN_0055f7f0. The shield code itself does not check cloak state.

## Weapon Interaction

### How weapons are gated by cloak state

Weapon firing is **NOT directly gated by cloak state in C++ weapon code**. Instead:

1. **WeaponSystem::CanFire** (`swig_WeaponSystem_CanFire`) reads a byte at `weaponSystem+0xAB`. This is a simple field read, not a computed check.

2. **Weapon::CanFire** (`swig_Weapon_CanFire`) calls `vtable[0x84/4]` — a virtual function that each weapon type implements.

3. The connection between cloak and weapons happens through **subsystem disable**:
   - When cloaking begins, `FUN_00562630` (DisableSubsystem) is called with event 0x0080006C (ET_SUBSYSTEM_STATUS)
   - This sets `+0x9C = 0` (isOn = false) on affected subsystems
   - The `PoweredSubsystem::StateChangedHandler` (FUN_00562730) propagates this

4. **The critical check is at the AI/Python level**: The game's AI and UI code checks `ShipClass_IsCloaked()` before initiating weapon fire:
   ```python
   # From AI/Preprocessors.py
   pCloakSystem = pShip.GetCloakingSubsystem()
   if pCloakSystem:
       if pCloakSystem.IsCloaked():
           continue  # Skip this target
   ```

5. **ShipClass::IsCloaked** (FUN_005ac450) checks [v5-validated 2026-05-28]:
   ```c
   CloakingSubsystem* cloak = ship->cloakSubsystem;  // ship+0x2DC
   if (cloak == NULL) return false;
   return cloak->isFullyCloaked;  // +0xAC == 1
   ```
   Note: This returns true ONLY when state==3 (CLOAKED), not during transitions.

### Network handling

The multiplayer cloak opcodes go through the same generic event forwarder FUN_0069fda0:
- Opcode 0x0E -> event 0x008000E3 (ET_START_CLOAKING) -> CloakingSubsystem::StartCloakingHandler
- Opcode 0x0F -> event 0x008000E5 (ET_STOP_CLOAKING) -> CloakingSubsystem::StopCloakingHandler

These handlers are registered in FUN_0055e4d0 [v5-validated 2026-05-28]:
```c
RegisterHandler(0x008000E3, "CloakingSubsystem::StartCloakingHandler");  // PUSH at 0x0055e4d0
RegisterHandler(0x008000E5, "CloakingSubsystem::StopCloakingHandler");   // PUSH at 0x0055e4e9
```

The actual handler (FUN_00549a50) is the bridge between events and the subsystem:
```c
void CloakEventHandler(TGEvent* event) {
    Ship* playerShip = GetPlayerShip();
    CloakingSubsystem* cloak = playerShip->cloakSubsystem;  // +0x2DC via offset 0xB7*4
    int eventData = GetEventData(event);  // FUN_005494f0
    if (cloak && eventData) {
        if (eventData->field_0x174 == 0) {
            StartCloaking(cloak);    // FUN_0055f360
        } else {
            StopCloaking(cloak);     // FUN_0055f380
        }
    }
}
```

### Network StateUpdate (0x40 flag) [v5-validated 2026-05-28]

The cloak state is serialized in the StateUpdate packet (FUN_005b17f0) as dirty flag 0x40:

**Writer** (server side, FUN_005B17F0):
```c
CloakingSubsystem* cloak = ship->cloakSubsystem;  // ship+0x2DC
if (cloak != NULL) {
    byte currentState = cloak->isOn;     // +0x9C (PoweredSubsystem::IsOn)
    if (currentState != prevCloakState) {  // tracker+0x2E (lastCloakState byte)
        dirtyFlags |= 0x40;
        prevCloakState = currentState;
    }
}
```

**Serialized** (at 0x005B1E6A-0x005B1E73, `CALL 0x006CF770` WriteBool_Bit):
```c
if (flags & 0x40) {
    if (ship->cloakSubsystem != NULL) {
        WriteBit(stream, cloakSubsystem->isOn);  // +0x9C — 1-bit emit
    }
}
```

**Reader** (client side, FUN_005B21C0):
```c
if ((flags & 0x40) && ship->cloakSubsystem != NULL) {
    bool cloakOn = ReadBit(stream);
    if (cloakOn)  StartCloaking(cloak);   // FUN_0055f360
    else          StopCloaking(cloak);    // FUN_0055f380
}
```

**Important**: The network serializes the `isOn` byte (+0x9C), NOT the state machine value (+0xB0). This means the client receives a boolean cloak on/off and runs its own local state machine transitions, including the visual effects and timer.

> **OQ2** — the reader's specific instruction address 0x005B2660 cited in the prior doc was not pinned to a specific instruction in this validation pass. The functional path (FUN_005B21C0, `(uDirtyFlags & 0x40)` branch dispatching to StartCloaking / StopCloaking) is verified.

## Visual Effect System

### FUN_0055e640 - UpdateVisibility [v5-validated 2026-05-28]
Address: `0x0055e640`

Called with `progress` (0.0 to 1.0) during transitions:
```c
void UpdateVisibility(this, float progress) {
    if (progress < 0.0f || progress > 1.0f) return;

    Ship* ship = this->ownerShip;
    if (ship == GetPlayerShip()) {
        // For the player's own ship, update cloak effect node
        NiNode* effectNode = this->cloakEffectNode;  // +0xA8
        effectNode->field_0x120 = progress * ALPHA_SCALE;  // DAT_0088ba90
        effectNode->field_0xD4++;
    }

    // Update scene graph alpha for all child nodes
    UpdateNodeAlpha(this, 1.0f - progress, ship->sceneNode);  // FUN_0055ee10
}
```

### FUN_0055ee10 - UpdateNodeAlpha (recursive) [v5-validated 2026-05-28]
Address: `0x0055ee10`

This is the visual transparency function. It walks the ship's NiNode tree and adjusts alpha on NiMaterialProperty nodes based on cloak state:

- **States 1/2 or isFullyCloaked**: Cloaking effect
  - If progress <= threshold: alpha = random * progress (shimmer effect)
  - If progress > threshold: alpha = (progress - threshold + random_offset) * progress

- **States 4/5**: Decloaking effect
  - alpha = (progress * scale - threshold + random_offset) * progress
  - Clamped to [0.0, 1.0]

- Uses `rand()` for shimmer/ripple visual effect during transitions

Visual constants (all byte-confirmed [v5-validated 2026-05-28]):

| Address | Name | Used by |
|---------|------|---------|
| 0x0088C5AC | shimmer threshold | UpdateNodeAlpha |
| 0x00892C94 | random scale factor | UpdateNodeAlpha |
| 0x00892C90 | decloak scale factor | UpdateNodeAlpha |
| 0x0088CB58 | alpha offset | UpdateNodeAlpha |
| 0x0088BA90 | alpha scale | UpdateVisibility (effectNode+0x120) |

## Multiplayer Event Registration

From FUN_0069e590 (MultiplayerGame constructor):
```c
RegisterHandler(ET_START_CLOAKING(0x008000E2), "MultiplayerGame::StartCloakingHandler");
RegisterHandler(ET_STOP_CLOAKING(0x008000E4), "MultiplayerGame::StopCloakingHandler");
```

Note: The MultiplayerGame registers for 0x008000E2 and 0x008000E4 (different from the subsystem's 0x008000E3 and 0x008000E5). These are the _notify_ versions:
- 0x008000E2 = ET_START_CLOAKING (request from player)
- 0x008000E3 = ET_START_CLOAKING_NOTIFY (forwarded to subsystem)
- 0x008000E4 = ET_STOP_CLOAKING (request from player)
- 0x008000E5 = ET_STOP_CLOAKING_NOTIFY (forwarded to subsystem)

The MultiplayerGame handlers convert local cloak events into network opcodes 0x0E/0x0F.

## Energy Failure Auto-Decloak

In the tick function, when state == 3 (CLOAKED):
```c
if (this->efficiency < ENERGY_THRESHOLD) {  // DAT_0088d4ec
    StopCloaking(this);                      // FUN_0055f380
    BeginDecloaking(this, 0);                // -> state=5
}
```

The efficiency field (+0x94) is computed by the parent PoweredSubsystem::Update as `actualPower / maxPower`. If the ship's power grid cannot sustain the cloaking device, efficiency drops below the threshold and the cloak automatically fails.

## Collision While Cloaked

The event `ET_CLOAKED_COLLISION` (0x00910A60) exists in the string table but has **0 xrefs** — it is dead/unused content. Collisions while cloaked are handled through the normal collision damage pipeline with no special cloaked-collision logic.

## Function Address Summary [v5-validated 2026-05-28]

| Address    | Name                                    | Role                                |
|------------|-----------------------------------------|-------------------------------------|
| 0x0055e2b0 | CloakingSubsystem::ctor (vtable 0x00892C04) — **meta-cascade rev 2** | Constructor, inits state fields, delegates state-machine init to FUN_0055F930 |
| ~~0x00566d10~~ | **NOT the cloaking ctor** — IS SensorSubsystem_Ctor (vtable 0x00892EAC) per meta-cascade rev 2 | Sensor subsystem constructor (formerly mis-attributed to cloaking in C4 rev 1) |
| 0x00566e50 | CloakingSubsystem::dtor (pending rev 2 review) | Destructor, frees linked lists — address may need re-validation after C4 rev 2 |
| 0x0055e500 | CloakingSubsystem::Update (tick)        | State machine + timer + energy check|
| 0x0055f360 | StartCloaking (user-facing)             | Sets tryingToCloak=1                |
| 0x0055f380 | StopCloaking (user-facing)              | Calls BeginDecloaking when (state==1\|\|2 OR isFullyCloaked) — C1 |
| 0x0055f110 | BeginCloaking/BeginDecloaking           | Creates animations, sets state 2/5; cloak path posts 0x00800077 (Clar1) |
| 0x0055f275 | (BeginCloak event-post site)            | Posts ET_CLOAK_BEGINNING (0x00800077) — sole xref |
| 0x0055f6d0 | CloakComplete                           | State 2->3                          |
| 0x0055f725 | (CloakComplete event-post site)         | Posts ET_CLOAK_COMPLETED (0x00800078) — C2 |
| 0x0055f7f0 | DecloakComplete (CloakDisengageRestoreShield) | State 5->0, posts ET_DECLOAK_COMPLETED (0x0080007A) + 0x0080007B, shield delay |
| 0x0055f660 | PlayCloakAnimation                      | State=2, "Cloak" sound              |
| 0x0055f770 | PlayUncloakAnimation                    | State=5, "Uncloak" sound            |
| 0x0055f3e0 | InstantCloak (FUN_0055F3E0)             | Immediate cloak (no timer)          |
| 0x0055f538 | InstantCloak event-post (FUN_0055F538)  | Posts ET_CLOAK_COMPLETED (0x00800078) — C2 |
| 0x0055f560 | InstantDecloak                          | Immediate decloak (no timer)        |
| 0x0055e640 | UpdateVisibility                        | Sets alpha from progress            |
| 0x0055ee10 | UpdateNodeAlpha                         | Recursive NiNode alpha with shimmer |
| 0x0055e6b0 | SetupCloakEffect                        | Scene-graph mutation + +0x148-byte NiNode allocation (Clar2) |
| 0x0055e800 | RestoreNiNode                           | Undoes cloak visual setup           |
| 0x0055e840 | InitCloakProperties                     | Sets up NiMaterial/NiShade properties|
| 0x0055f930 | DeathWhileCloaked                       | Stops cloak + begins decloak on death|
| 0x0055f5f0 | RecalcVisibility                        | Recomputes alpha from current timer |
| 0x005ac450 | ShipClass::IsCloaked                    | Returns cloak+0xAC (isFullyCloaked) |
| 0x00549a50 | CloakEventHandler                       | Bridges events to Start/StopCloaking|
| 0x0055e4d0 | RegisterCloakHandlers                   | Registers 0xE3/0xE5 event handlers  |
| 0x0056c350 | CheckEnergyRecursive                    | Validates power for cloaking        |

## Global Constants [v5-validated 2026-05-28]

| Address      | Name          | Type  | Default value | Notes                                  |
|-------------|---------------|-------|---------------|----------------------------------------|
| 0x008e4e1c  | CloakTime     | float | **5.0f**      | Transition duration (Set/GetCloakTime). Raw bytes `00 00 A0 40`. **C3 — was claimed unverifiable; OpenBC cascade needed.** |
| 0x008e4e20  | ShieldDelay   | float | **1.0f**      | Shield re-enable delay (Set/GetShieldDelay). Raw bytes `00 00 80 3F`. **C3.** |
| 0x00888860  | FLOAT_1_0     | float | 1.0f          | (used as clamp max)                    |
| 0x00888b54  | FLOAT_0_0     | float | 0.0f          | (used as clamp min)                    |
| 0x0088d4ec  | ENERGY_THRESH | float | —             | Efficiency threshold for auto-decloak  |
| 0x0088c5ac  | SHIMMER_THRESH| float | —             | Alpha threshold for shimmer effect     |
| 0x00892c94  | RANDOM_SCALE  | float | —             | Random multiplier for shimmer          |
| 0x00892c90  | DECLOAK_SCALE | float | —             | Scale factor for decloak alpha         |
| 0x0088cb58  | ALPHA_OFFSET  | float | —             | Base offset for alpha calculation      |
| 0x0088ba90  | ALPHA_SCALE   | float | —             | Multiplier for cloak effect node alpha |
| 0x008e42c8  | "Cloak"       | str   | —             | Sound effect ID string (Clar3, byte-confirmed) |
| 0x008e4eb8  | "Uncloak"     | str   | —             | Sound effect ID string (Clar3, byte-confirmed) |

## Comparison with OpenBC Cleanroom Spec

The OpenBC spec claims 4 states: DECLOAKED=0, CLOAKING=1, CLOAKED=2, DECLOAKING=3.

**Actual findings**: The binary uses states 0, 2, 3, 5 (with ghost states 1, 4 checked but never assigned). The mapping is:

| OpenBC Spec    | Actual Binary | Notes                              |
|----------------|---------------|------------------------------------|
| DECLOAKED=0    | 0             | Correct value                      |
| CLOAKING=1     | 2             | OpenBC wrong: actual value is 2    |
| CLOAKED=2      | 3             | OpenBC wrong: actual value is 3    |
| DECLOAKING=3   | 5             | OpenBC wrong: actual value is 5    |

### C3 — Transition time is 5.0s, not 3.0s

> **OpenBC clean-room cascade (2026-05-28)**: The OpenBC clean-room spec uses "3.0 seconds" for cloak transition. Binary truth: CloakTime = 5.0f at DAT_008E4E1C (raw bytes `00 00 A0 40`). OpenBC clean-room implementations should update to **5.0 seconds** for stock parity. ShieldDelay default is 1.0f (raw bytes `00 00 80 3F` at DAT_008E4E20).

Both defaults are statically determinable from .rdata (prior doc claimed they could not be) — see C3 in the top NOTE block.

## Open Questions

- **OQ1 — Who consumes ET_CLOAK_BEGINNING (0x00800077)?** Posted only once (at FUN_0055F275, sole xref), and no registered C++ handler was found in this validation pass. The event may be consumed by UI/Python only, not by C++ subsystems — meaning it serves as a notification for other parts of the game to react to cloak start, without internal C++ behavior depending on it. Worth a cross-reference search through SWIG handler registries.

- **OQ2 — Reader address claim 0x005B2660 not pinned to a specific instruction.** Prior doc cited 0x005B2660 as the StateUpdate reader's cloak-bit branch. The functional path inside FUN_005B21C0 (`(uDirtyFlags & 0x40)` → ReadBit → StartCloaking/StopCloaking dispatch) is verified, but the exact instruction-level address inside the decompiled body was not nailed down in this pass. Worth a future cross-reference if revisiting.
