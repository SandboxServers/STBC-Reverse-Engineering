> [docs](../README.md) / [gameplay](README.md) / power-system.md

---
title: Power & Reactor System — Complete Reverse Engineering
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
  - claim: "Power system uses 3-class architecture: PowerSubsystem (reactor, vtable 0x00892C98) does NOT inherit PoweredSubsystem; PoweredSubsystem base (vtable 0x00892D98); PoweredMaster EPS distributor (vtable 0x0088A1F0) at ship+0x2B0"
    address: 0x00560470
    function: PowerSubsystem_Ctor
    confidence: high
    note: "Reactor ctor FUN_00560470 calls FUN_0056B970 (ShipSubsystem base ctor) — NOT FUN_00562240 (PoweredSubsystem base ctor) — confirming non-inheritance. Renamed this pass."
  - claim: "Ship__SetupProperties at 0x005B3FB0 installs 12 subsystem slots at ship+0x2B0..+0x2DC with type-ID gate + ctor + vtable per-slot; full slot table v5-validated 2026-05-28"
    address: 0x005B3FB0
    function: Ship__SetupProperties
    confidence: high
    note: "Full disasm of switch body 0x005B402C..0x005B445C decoded; ctor + vtable per slot all byte-confirmed. This is the source of truth for the 12 vtable-to-class-name mappings. Foundation cross-anchor: wire-format-spec.md Named Slot Layout."
  - claim: "PoweredMaster::Update at 0x00563780 (vtable 0x0088A1F0 slot 25) runs main power simulation once per INTERVAL (1.0s constant at 0x00892E20); calls ShipSubsystem::Update, computes elapsed time, runs AddPowerToBatteries + ComputeAvailablePower, updates battery percentages"
    address: 0x00563780
    function: PoweredMaster_Update
    confidence: high
    note: "Renamed this pass."
  - claim: "PoweredSubsystem::Update at 0x00562470 runs every frame; per-frame three-way switch at consumer+0xA0 (powerMode) dispatches to DrawFromMainBattery / DrawFromBackupBattery / DrawFromBackupOnly"
    address: 0x00562470
    function: PoweredSubsystem_Update
    confidence: high
    note: "Decompile confirms three-way switch on param_1[0x28] (= +0xA0). Renamed this pass."
  - claim: "PoweredSubsystem base ctor at 0x00562240 writes vtable 0x00892D98 and initializes consumer state defaults: +0x90=1.0f (powerPercentageWanted), +0x94=1.0f (efficiency), +0x98=1.0f (conditionRatio), +0x9C=1 (isOn), +0xA0=0 (powerMode main-first)"
    address: 0x00562240
    function: PoweredSubsystem_Ctor
    confidence: high
    note: "Stage 1 of init chain confirmed via decompile. Renamed this pass."
  - claim: "PoweredMaster::SetupFromProperty at 0x005636D0 (vtable 0x0088A1F0 slot 22) fills mainBatteryPower=MainBatteryLimit and backupBatteryPower=BackupBatteryLimit at spawn (Stage 2 of init chain)"
    address: 0x005636D0
    confidence: high
    note: "Disasm: CALL 0x005634C0 (GetMainBatteryLimit) -> FSTP [ESI+0xAC]; CALL 0x005634D0 (GetBackupBatteryLimit) -> FSTP [ESI+0xB4]. Function exists at this address but is NOT auto-defined in Ghidra DB; reached via vtable slot 22 pointer at 0x0088A248."
  - claim: "PoweredMaster ctor at 0x00563530 (slot ship+0x2B0, type ID 0x8022) writes vtable 0x0088A1F0 and derives from PoweredSubsystem base"
    address: 0x00563530
    function: PoweredMaster_Ctor
    confidence: high
    note: "Renamed this pass."
  - claim: "12-slot ship subsystem layout binary-truth: +0x2B0 PoweredMaster (0x0088A1F0), +0x2B4 TorpedoSystem (0x00893598), +0x2B8 PhaserSystem (0x00893240), +0x2BC PulseWeaponSystem (0x008933B0), +0x2C0 ShieldGenerator (0x00892F34), +0x2C4 PowerSubsystem reactor (0x00892C98), +0x2C8 SensorSubsystem (0x00892EAC), +0x2CC ImpulseEngineSubsystem (0x00892D10), +0x2D0 WarpEngineSubsystem (0x00893040), +0x2D4 TractorBeamSystem (0x00893794), +0x2D8 RepairSubsystem (0x00892E24), +0x2DC CloakingSubsystem (0x00892C04)"
    address: 0x005B3FB0
    function: Ship__SetupProperties
    confidence: high
    note: "C1 — corrects prior doc Class Hierarchy table which had 8 of 11 vtables paired with WRONG class names. See body Class Hierarchy section."
  - claim: "ShieldGenerator ctor at 0x0056A000 writes vtable 0x00892F34; slot ship+0x2C0; type ID 0x8028"
    address: 0x0056A000
    function: ShieldGenerator_Ctor
    confidence: high
    note: "Renamed this pass."
  - claim: "CloakingSubsystem ctor at 0x0055E2B0 writes vtable 0x00892C04 and at 0x0055E32E sets +0xA0 = 2 (powerMode backup-only); slot ship+0x2DC; type ID 0x8024"
    address: 0x0055E2B0
    function: CloakingSubsystem_Ctor
    confidence: high
    note: "Renamed this pass."
  - claim: "ImpulseEngineSubsystem ctor at 0x00561050 writes vtable 0x00892D10; slot ship+0x2CC; type ID 0x8026"
    address: 0x00561050
    function: ImpulseEngineSubsystem_Ctor
    confidence: high
    note: "Renamed this pass."
  - claim: "RepairSubsystem ctor at 0x00565090 writes vtable 0x00892E24; slot ship+0x2D8; type ID 0x8029"
    address: 0x00565090
    function: RepairSubsystem_Ctor
    confidence: high
    note: "Renamed this pass."
  - claim: "WarpEngineSubsystem ctor at 0x0056DE70 writes vtable 0x00893040; slot ship+0x2D0; type ID 0x8025"
    address: 0x0056DE70
    function: WarpEngineSubsystem_Ctor
    confidence: high
    note: "Renamed this pass."
  - claim: "SensorSubsystem ctor at 0x00566D10 writes vtable 0x00892EAC; slot ship+0x2C8; type ID 0x8023"
    address: 0x00566D10
    function: SensorSubsystem_Ctor
    confidence: high
    note: "Renamed this pass."
  - claim: "TractorBeamSystem ctor at 0x00582080 writes vtable 0x00893794 and at 0x005820B2 sets +0xA0 = 1 (powerMode backup-first); slot ship+0x2D4; type ID 0x8021"
    address: 0x00582080
    function: TractorBeamSystem_Ctor
    confidence: high
    note: "Renamed this pass."
  - claim: "FUN_005638D0 PoweredMaster::AddPowerToBatteries gate is (!IsHost OR IsMultiplayer); recharge runs everywhere EXCEPT the SP-host config — NOT 'HOST-ONLY in multiplayer' as prior doc claimed"
    address: 0x005638D0
    function: PoweredMaster_AddPowerToBatteries
    confidence: high
    note: "C2. Decompile shows: if ((DAT_0097FA89 == 0) || (DAT_0097FA8A != 0)) { recharge }. Renamed + plate this pass."
  - claim: "DrawFromMainBattery (0x00563A70), DrawFromBackupBattery (0x00563BB0), DrawFromBackupOnly (0x00563CB0) all implement host-authority gating (bVar3 mutate-allow, bVar5 early-return-allow); clients CALCULATE projected draws but do NOT mutate authoritative battery state"
    address: 0x00563A70
    function: PoweredMaster_DrawFromMainBattery
    confidence: high
    note: "C3. All three Draw functions start with `bool bVar3=true, bVar5=true; if (DAT_0097FA89!=0) { ... }` host-build conditional that controls subsequent +0xAC/+0xB4 writes. Renamed + plate this pass."
  - claim: "FUN_0055F7F0 is the cloak-decloak shield-restore handler — called only from CloakingSubsystem::Update (FUN_0055E500) at state 5->0 transition; reads ship+0x2C0 (ShieldGenerator) and restores shield power to 1.0 if zeroed; posts events 0x0080007A (cloak status changed) and 0x0080007B (shield enable)"
    address: 0x0055F7F0
    function: CloakDisengageRestoreShield
    confidence: high
    note: "C4 — NOT 'reactor enable guard' as prior doc claimed. Renamed + plate this pass."
  - claim: "Consumer list head/tail labels are REVERSED in prior doc — PoweredMaster+0xC8 is the TAIL (first inserted, untouched) and +0xCC is the HEAD (insertion point, LIFO)"
    address: 0x00563D50
    function: PoweredMaster_SetPowerSource
    confidence: high
    note: "C5. FUN_00563D50: on first insert, param_1[0x32]=local_4 (+0xC8 = first node = tail) and param_1[0x33]=local_4 (+0xCC = head); subsequent inserts back-link old head and update +0xCC. Renamed this pass."
  - claim: "PowerProperty field offsets +0x48 MainBatteryLimit, +0x4C BackupBatteryLimit, +0x50 MainConduitCapacity, +0x54 BackupConduitCapacity, +0x58 PowerOutput — all confirmed via helper functions at 0x005634C0/D0/E0/F0/520"
    address: 0x005634C0
    function: PowerSubsystem_GetMainBatteryLimit
    confidence: high
  - claim: "PoweredSubsystem::SetPowerPercentageWanted at 0x00562430 writes +0x90 (powerPercentageWanted) and rescales +0x8C (powerWanted = powerWanted * pct / oldPct) when oldPct != 0.0"
    address: 0x00562430
    function: PoweredSubsystem_SetPowerPercentageWanted
    confidence: high
    note: "Pure local setter — no network call, no event posting. Renamed this pass."
  - claim: "PoweredSubsystem::GetNormalPowerWanted at 0x005623D0 returns property+0x48 if (!IsDisabled && isOn && property!=NULL) else 0"
    address: 0x005623D0
    function: PoweredSubsystem_GetNormalPowerWanted
    confidence: high
    note: "Renamed this pass."
  - claim: "PoweredMaster::ComputeAvailablePower at 0x00563700 computes per-pool min(battery, capacity*ticks); mainConduitCurrent uses MainConduitCapacity*conditionPct (health-scaled); backupConduitCurrent uses raw BackupConduitCapacity"
    address: 0x00563700
    function: PoweredMaster_ComputeAvailablePower
    confidence: high
    note: "Renamed this pass."
  - claim: "PoweredMaster::SetPowerSource at 0x00563D50 allocates 12-byte node from FUN_0054F720 pool and inserts at head (+0xCC) of consumer linked list (LIFO order)"
    address: 0x00563D50
    function: PoweredMaster_SetPowerSource
    confidence: high
  - claim: "Power mode assignments: TractorBeamSystem sets +0xA0=1 (backup-first) at 0x005820B2; CloakingSubsystem sets +0xA0=2 (backup-only) at 0x0055E32E; all other subsystem ctors do NOT touch +0xA0 and inherit mode 0 from base"
    address: 0x005820B2
    confidence: high
  - claim: "Constant INTERVAL = 1.0f at 0x00892E20 (bytes 0x3F800000) controls PoweredMaster::Update interval"
    address: 0x00892E20
    confidence: high
  - claim: "Constant 0.0f at 0x00888B54 (bytes 0x00000000) used for float comparisons"
    address: 0x00888B54
    confidence: high
  - claim: "Constant 1.0f at 0x00888860 (bytes 0x3F800000) used in GetCombinedConditionPercentage"
    address: 0x00888860
    confidence: high
  - claim: "Constant 1.25f at 0x0088BEC0 (bytes 0x3FA00000) — maximum powerPercentageWanted overload cap (125%)"
    address: 0x0088BEC0
    confidence: high
  - claim: "Constant 100.0f at 0x0088CE78 (bytes 0x42C80000) — WriteState power-byte encoding multiplier (int(pct * 100.0))"
    address: 0x0088CE78
    confidence: high
  - claim: "Constant 0.01f at 0x0088D4E4 (bytes 0x3C23D70A) — ReadState power-byte decoding multiplier (byte * 0.01f)"
    address: 0x0088D4E4
    confidence: high
  - claim: "Constant 255.0f at 0x0088B9AC (bytes 0x437F0000) — condition byte multiplier"
    address: 0x0088B9AC
    confidence: high
  - claim: "FUN_0054E690 posts event 0x0080008C (ET_SUBSYSTEM_POWER_CHANGED) carrying powerPctWanted; event is NOT in MultiplayerGame's network-forwarded list — power slider changes propagate ONLY via StateUpdate (opcode 0x1C) round-robin"
    address: 0x0054E690
    confidence: high
    note: "Decompile confirms event creation writes &DAT_0080008C to event+0x10, payload at +0x28 = source->[+0x90] (powerPctWanted). Cross-anchored to docs/protocol/wire-format-spec.md MultiplayerGame forwarded event table."
  - claim: "PoweredSubsystem::WriteState at 0x00562960 (vtable+0x70, round-robin path) writes hasData bit + powerPctByte gated on isOwnShip; PoweredSubsystem::ReadState at 0x005629D0 (vtable+0x74) gates apply on timestamp newer than lastNetworkUpdate"
    address: 0x00562960
    function: PoweredSubsystem_WriteState
    confidence: high
    note: "Cross-anchored from protocol mid #11 (stateupdate-subsystem-wire-format.md), v5-validated 2026-05-28."
  - claim: "FUN_0055F7F0 posts event 0x0080007A (cloak status changed) and event 0x0080007B (shield enable) when restoring shield power after decloak"
    address: 0x0055F7F0
    function: CloakDisengageRestoreShield
    confidence: high
    note: "Partial resolution of prior doc Open Question #1."
companions:
  - docs/protocol/subsystem-integrity-hash.md
  - docs/protocol/wire-format-spec.md
  - docs/protocol/stateupdate.md
  - docs/protocol/stateupdate-subsystem-wire-format.md
  - docs/gameplay/cloaking-state-machine.md
  - docs/gameplay/shield-system.md
  - docs/gameplay/repair-system.md
  - docs/gameplay/combat-mechanics-re.md
---

> [!NOTE]
> **v5 re-validation 2026-05-28 — 5 corrections including 1 HIGH-PRIORITY vtable-to-class table shift across 8 of 11 subsystem classes + cascade to protocol leaf #19 (subsystem-integrity-hash).** Power model substantively correct (3-class architecture, battery/conduit math, powerMode pools, network propagation, init chain, all 7 constants byte-confirmed). 26 Ghidra functions renamed.
>
> - **C1 (HIGH)**: Class Hierarchy table paired 8 of 11 subsystem vtables with WRONG class names — circular-shifted mapping. Binary truth now rendered from Ship__SetupProperties (FUN_005B3FB0) decompile + 12 individual ctor disassemblies. **Meta-cascade rev 2 (2026-05-28)**: the slot +0x2C4 row was further reverted — vtable 0x00892C98 IS HullSubsystem (class 0x8027 — "HullClass" vtable strings), NOT PowerSubsystem reactor; the actual reactor (PoweredMaster, class 0x813E) is at +0x2B0 with vtable 0x0088A1F0. The 8-of-11 shift framing still stands; only the +0x2C4 row identity was the load-bearing error in rev 1. See the rev 2 IMPORTANT block in the Cross-doc cascade section.
> - **C2**: AddPowerToBatteries gate (FUN_005638D0) is INVERTED. Actual gate is `(!IsHost) || IsMultiplayer` — runs everywhere except SP-host config — NOT "HOST-ONLY in multiplayer".
> - **C3**: Draw functions (FUN_00563A70 / BB0 / CB0) all implement client-side prediction — clients CALCULATE projected draws via bVar3/bVar5 host-auth gating but do NOT mutate authoritative battery state. Prior doc pseudocode entirely omitted this.
> - **C4**: FUN_0055F7F0 is the cloak-decloak shield-restore handler, NOT a reactor enable guard. Called only from CloakingSubsystem::Update at state 5->0 transition.
> - **C5**: Consumer list head/tail labels are REVERSED — +0xC8 is the TAIL (first inserted), +0xCC is the HEAD (LIFO insertion point).

---

# Power & Reactor System — Complete Reverse Engineering

Reverse-engineered from stbc.exe via Ghidra decompilation, SWIG wrapper analysis, and cross-referenced against shipped hardpoint scripts. All addresses verified against the game binary.

For the clean-room behavioral specification (no addresses, suitable for reimplementation), see the OpenBC repository at `../OpenBC/docs/power-system.md`.

---

## Overview

Bridge Commander's power system uses a three-class architecture [v5-validated 2026-05-28]:

1. **PowerSubsystem** — the physical warp core/reactor. A ShipSubsystem that stores HP, can be damaged, and whose condition scales power output. **Does NOT inherit from PoweredSubsystem.** Verified: ctor FUN_00560470 (PowerSubsystem_Ctor) calls FUN_0056B970 (ShipSubsystem base ctor), not FUN_00562240 (PoweredSubsystem base ctor).
2. **PoweredSubsystem** — base class for all power-consuming subsystems (shields, engines, weapons, etc.). Each consumer draws power per-frame from the master distributor.
3. **PoweredMaster** ("Powered" master) — a special PoweredSubsystem instance at ship+0x2B0 that acts as the EPS (Electro-Plasma System) distributor. Manages batteries, conduit limits, and the consumer list. Runs the main power simulation tick once per second.

The power flow is: **Reactor generates → Main battery stores → Powered distributor allocates → Each PoweredSubsystem draws**.

---

## Class Hierarchy [v5-validated 2026-05-28]

### C1 — Vtable-to-class map (CORRECTED 2026-05-28)

The prior doc paired 8 of 11 subsystem vtables with the WRONG class names — a circular-shifted mapping. The slot offsets (which ship offset maps to which subsystem) were mostly correct (foundation #1 had already been corrected for the Pulse/Tractor swap). The **vtable-to-class-name** column within the hierarchy block was the load-bearing error.

Binary truth, extracted from Ship__SetupProperties (FUN_005B3FB0) disassembly + 12 individual ctor decompiles:

| Slot | Class | Vtable (binary truth) | Vtable (prior doc) | Status |
|---|---|---|---|---|
| +0x2B0 | **PoweredMaster (Power Reactor)** — class 0x813E | 0x0088A1F0 | 0x88A1F0 | OK (slot/vtable correct; this IS the PowerSubsystem reactor — meta-cascade rev 2) |
| +0x2B4 | TorpedoSystem | 0x00893598 | 0x893630 | **CORRECTION** |
| +0x2B8 | PhaserSystem (was "PhaserController") | 0x00893240 | 0x893240 | OK (name aligned) |
| +0x2BC | PulseWeaponSystem | 0x008933B0 | 0x893794 | **CORRECTION** |
| +0x2C0 | ShieldGenerator | 0x00892F34 | 0x893598 | **CORRECTION** |
| +0x2C4 | **HullSubsystem** (class 0x8027, vtable 0x00892C98 — "HullClass" strings) `[meta-cascade 2026-05-28 (rev 2)]` | 0x00892C98 | 0x892C98 | **CORRECTION (rev 2)** — vtable address unchanged; identity was PowerSubsystem reactor in rev 1, now HullSubsystem |
| +0x2C8 | SensorSubsystem (was "SensorArray") | 0x00892EAC | 0x893040 | **CORRECTION** |
| +0x2CC | ImpulseEngineSubsystem | 0x00892D10 | 0x892FC4 (= ShipSubsystem base) | **CORRECTION** |
| +0x2D0 | WarpEngineSubsystem | 0x00893040 | 0x892E24 | **CORRECTION** |
| +0x2D4 | TractorBeamSystem | 0x00893794 | 0x8936F0 | **CORRECTION** |
| +0x2D8 | RepairSubsystem | 0x00892E24 | 0x892F34 | **CORRECTION** |
| +0x2DC | CloakingSubsystem | 0x00892C04 | 0x892EAC | **CORRECTION** |

> [!IMPORTANT]
> **Meta-cascade revision (2026-05-28, rev 2)** — Slot +0x2C4 row corrected. Sensor/hull RE (see `.claude/agent-memory/game-archaeology-specialist/sensor-hull-subsystem-validation-20260528.md`) definitively proved via vtable literal strings that:
>
> - **PowerSubsystem reactor (class 0x813E PoweredMaster) is at slot +0x2B0** with vtable PTR_FUN_0088A1F0 (NOT at +0x2C4)
> - **HullSubsystem (class 0x8027 with "HullClass" / "_p_HullClass" / "HullClassPtr" vtable strings) is at +0x2C4** with vtable 0x00892C98
>
> The 8-of-11 vtable-shift framing of C1 still stands; only the slot +0x2C4 identity row needed reversion. The earlier framing "+0x2C4: vtable 0x00892C98 = PowerSubsystem Reactor" was wrong — vtable 0x00892C98 IS HullSubsystem, and PoweredMaster (the actual reactor) has vtable 0x0088A1F0 at +0x2B0. The slot offsets in the table remain correct; only the human-readable identity at +0x2C4 was the load-bearing error in rev 1.

Anchor: extracted from Ship__SetupProperties (FUN_005B3FB0) disasm at 0x005B402C..0x005B445C + 12 individual ctor decompiles. Each ctor's vtable write (`MOV [EDI], &PTR_FUN_00xxxxxx`) is the class-defining write.

### Corrected hierarchy tree

```
ShipSubsystem (vtable 0x00892FC4)              ← Base for ALL ship subsystems
  Ctor: FUN_0056B970
  Update: FUN_0056BC60 (slot 25)
  │
  └── PowerSubsystem (vtable 0x00892C98)        ← Reactor / "Warp Core"
        Ctor: FUN_00560470 (PowerSubsystem_Ctor)
        Named slot: ship+0x2C4
        Instance type ID: 0x8027
        DOES NOT inherit from PoweredSubsystem
        DOES NOT override Update (uses base ShipSubsystem::Update)

PoweredSubsystem (vtable 0x00892D98)           ← Base for all powered consumers
  Ctor: FUN_00562240 (PoweredSubsystem_Ctor)
  Update: FUN_00562470 (PoweredSubsystem_Update, slot 25)
  │
  ├── PoweredMaster (vtable 0x0088A1F0)         ← EPS distributor
  │     Ctor: FUN_00563530 (PoweredMaster_Ctor)
  │     Named slot: ship+0x2B0
  │     Instance type ID: 0x8022
  │     Update override: FUN_00563780 (PoweredMaster_Update — MAIN POWER SIMULATION)
  │     SetupFromProperty: FUN_005636D0 (vtable slot 22)
  │
  ├── ShieldGenerator (vtable 0x00892F34)
  │     Ctor: FUN_0056A000 (ShieldGenerator_Ctor), slot ship+0x2C0, type ID 0x8028
  │
  ├── SensorSubsystem (vtable 0x00892EAC)
  │     Ctor: FUN_00566D10 (SensorSubsystem_Ctor), slot ship+0x2C8, type ID 0x8023
  │
  ├── ImpulseEngineSubsystem (vtable 0x00892D10)
  │     Ctor: FUN_00561050 (ImpulseEngineSubsystem_Ctor), slot ship+0x2CC, type ID 0x8026
  │
  ├── WarpEngineSubsystem (vtable 0x00893040)
  │     Ctor: FUN_0056DE70 (WarpEngineSubsystem_Ctor), slot ship+0x2D0, type ID 0x8025
  │
  ├── RepairSubsystem (vtable 0x00892E24)
  │     Ctor: FUN_00565090 (RepairSubsystem_Ctor), slot ship+0x2D8, type ID 0x8029
  │
  ├── CloakingSubsystem (vtable 0x00892C04)
  │     Ctor: FUN_0055E2B0 (CloakingSubsystem_Ctor), slot ship+0x2DC, type ID 0x8024
  │     powerMode = 2 (backup-only)
  │
  ├── TractorBeamSystem (vtable 0x00893794)
  │     Ctor: FUN_00582080 (TractorBeamSystem_Ctor), slot ship+0x2D4, type ID 0x8021
  │     powerMode = 1 (backup-first)
  │
  ├── TorpedoSystem (vtable 0x00893598)
  │     Ctor: FUN_0057B020, slot ship+0x2B4, type ID 0x801E
  │
  ├── PhaserSystem (vtable 0x00893240)
  │     Ctor: FUN_00573C90, slot ship+0x2B8, type ID 0x801F
  │
  └── PulseWeaponSystem (vtable 0x008933B0)
        Ctor: FUN_005773B0, slot ship+0x2BC, type ID 0x8020
```

**Key architectural insight** `[meta-cascade 2026-05-28 (rev 2) — slot identity refined]`: The reactor and the EPS distributor were originally described as separate objects at separate slots (ship+0x2C4 reactor + ship+0x2B0 distributor). The sensor/hull RE meta-cascade (rev 2) shows the reactor (PoweredMaster, class 0x813E, vtable 0x0088A1F0) is itself at **ship+0x2B0** — i.e., PoweredMaster is both the EPS distributor AND the reactor identity, and ship+0x2C4 is HullSubsystem instead. The 3-class architecture (ShipSubsystem base / PoweredSubsystem base / PoweredMaster reactor-distributor) and the battery/conduit math still stand; only the original "reactor lives at +0x2C4 separately from distributor at +0x2B0" framing was wrong. The 7,000 HP per ship is on the PoweredMaster at +0x2B0; HullSubsystem at +0x2C4 carries a separate HP budget that subordinate subsystems aggregate against. See `.claude/agent-memory/game-archaeology-specialist/sensor-hull-subsystem-validation-20260528.md`.

### Type ID namespaces (clarification)

Prior doc lines 31, 41 cited "type ID: 0x8138" (PowerSubsystem) and "type ID: 0x813E" (PoweredMaster). These are the **PowerProperty / HullProperty class IDs** in the Context Type ID space (0x812F..0x813F) — the read-only hardpoint templates — NOT the subsystem instance class IDs. Subsystem instance IDs are in the 0x8021..0x8029 range (gated by the FUN_005604x0 type-gate functions in Ship__SetupProperties). The doc conflated the two namespaces.

| Namespace | Range | What it identifies | Where stored |
|---|---|---|---|
| Property class IDs | 0x812F..0x813F | Read-only hardpoint template (PowerProperty, HullProperty, etc.) | At PoweredMaster+0x18 (member field) |
| Subsystem instance class IDs | 0x8021..0x8029 | Runtime subsystem class | What GetClassID returns (vtable slot 1) |

### Cross-doc cascade — protocol leaf #19 reconciliation required

> [!IMPORTANT]
> **CASCADE TO PROTOCOL LEAF #19** [2026-05-28, rev 1]: The slot 1 (+0x2C4) attribution in `docs/protocol/subsystem-integrity-hash.md` says HullSubsystem (0x8138). Binary truth: ship+0x2C4 is PowerSubsystem reactor (vtable 0x00892C98, instance class ID 0x8027). The 0x8138 is the **PowerProperty CLASS ID** (a different namespace from subsystem instance class IDs). The pre-correction name "Power Reactor" was right; leaf #19's HullSubsystem rename needs reverting.
>
> Slots 4 (+0x2C8 SensorSubsystem) / 6 (+0x2D0 WarpEngineSubsystem) / 7 (+0x2D8 RepairSubsystem) / 8 (+0x2DC CloakingSubsystem) from leaf #19 STILL HOLD. This cross-doc cascade is being patched separately.

> [!IMPORTANT]
> **CASCADE TO PROTOCOL LEAF #19 (revision 2, 2026-05-28)** — META-CASCADE REVERSION. The rev 1 cascade above is itself superseded. Sensor/hull RE (see `.claude/agent-memory/game-archaeology-specialist/sensor-hull-subsystem-validation-20260528.md`) definitively proved that ship+0x2C4 IS HullSubsystem (vtable 0x00892C98, class 0x8027 — proved by literal vtable strings "HullClass" / "_p_HullClass" / "HullClassPtr"), NOT PowerSubsystem reactor.
>
> Meta-cascade history:
>
> 1. **Leaf #19 originally** — ship+0x2C4 = HullSubsystem **(CORRECT)**
> 2. **Power-system C1 cascade (rev 1, above)** — "corrected" to PowerSubsystem reactor **(WRONG)**
> 3. **Cascade-patch (leaf #19 + wire-format-spec, rev 1)** — reverted to match rev 1 power-system C1 **(PROPAGATED THE ERROR)**
> 4. **Sensor/hull RE (this rev 2)** — definitively reverted to HullSubsystem **(FINAL BINARY TRUTH)**
>
> Binary truth: PowerSubsystem reactor (PoweredMaster, class 0x813E) actually lives at **ship+0x2B0**, via PoweredMaster_Ctor at 0x00563530 with vtable PTR_FUN_0088A1F0. The 8-of-11 vtable-shift framing in this doc's C1 still stands; only the slot 1 (+0x2C4) row of the table above has been corrected (vtable address 0x00892C98 unchanged — only the class identity flipped from PowerSubsystem reactor back to HullSubsystem). Slots 4 / 6 / 7 / 8 from leaf #19 STILL HOLD as before.

---

## PowerProperty Field Offsets [v5-validated 2026-05-28]

PowerProperty is the read-only template created by `App.PowerProperty_Create()` in hardpoint scripts. It stores the 5 core power parameters.

| Offset | Type | Field | Setter Method |
|--------|------|-------|---------------|
| +0x48 | float | MainBatteryLimit | SetMainBatteryLimit() |
| +0x4C | float | BackupBatteryLimit | SetBackupBatteryLimit() |
| +0x50 | float | MainConduitCapacity | SetMainConduitCapacity() |
| +0x54 | float | BackupConduitCapacity | SetBackupConduitCapacity() |
| +0x58 | float | PowerOutput | SetPowerOutput() |

Example (Sovereign): MainBattery=200,000, BackupBattery=100,000, MainConduit=1,450, BackupConduit=250, PowerOutput=1,200.

All 5 offsets confirmed via helper functions at 0x005634C0..0x00563520.

---

## PowerSubsystem (Reactor) Runtime Layout

vtable at 0x00892C98. Named slot: ship+0x2C4. This is the physical reactor — it takes damage and its HP affects power output.

| Offset | Type | Field | Notes |
|--------|------|-------|-------|
| +0x00 | ptr | vtable | 0x00892C98 |
| +0x18 | ptr | property | PowerProperty* (read-only template) |
| +0x30 | float | condition | Current HP (float, not percentage) |
| +0x34 | float | conditionPct | condition / maxCondition (0.0–1.0) |

The reactor itself does NOT store batteries or manage distribution. It serves as a health-scalable proxy — `GetPowerOutput()` returns `property+0x58 * conditionPct`.

---

## PoweredMaster (EPS Distributor) Runtime Layout

vtable at 0x0088A1F0. Named slot: ship+0x2B0. This is the central power management object.

| Offset | Type | Field | Notes |
|--------|------|-------|-------|
| +0x00 | ptr | vtable | 0x0088A1F0 |
| +0x18 | ptr | property | PowerProperty* |
| +0x30 | float | condition | Current HP |
| +0x34 | float | conditionPct | Health ratio (0.0–1.0) |
| +0x40 | ptr | ownerShip | Ship* that owns this subsystem |
| +0x88 | ptr | mainBatteryWatcher | FPU watcher pointer (4 bytes, not 12) |
| +0x94 | ptr | backupBatteryWatcher | FPU watcher pointer (4 bytes, not 12) |
| +0xA0 | float | availablePower | Total power available for consumption |
| +0xA4 | float | mainConduitCurrent | Main conduit power remaining this interval |
| +0xA8 | float | backupConduitCurrent | Backup conduit power remaining this interval |
| +0xAC | float | mainBatteryPower | Current main battery charge level |
| +0xB0 | float | mainBatteryPct | mainBatteryPower / mainBatteryLimit |
| +0xB4 | float | backupBatteryPower | Current backup battery charge level |
| +0xB8 | float | backupBatteryPct | backupBatteryPower / backupBatteryLimit |
| +0xBC | float | powerDispensed | Total power dispensed this tick |
| +0xC0 | float | lastUpdateTime | For elapsed time calculation |
| +0xC4 | int | consumerCount | Number of registered power consumers |
| +0xC8 | ptr | consumerListTail | **C5 CORRECTION**: This is the TAIL (first inserted, untouched). Pre-v5 doc said "Head". |
| +0xCC | ptr | consumerListHead | **C5 CORRECTION**: This is the HEAD (insertion point, LIFO). Pre-v5 doc said "Tail". |
| +0xD0 | ptr | freeListHead | Pool allocator for list nodes |

Consumer list node layout: `[subsystem_ptr (4), prev (4), next (4)]` — 12 bytes each, allocated from pool at FUN_0054F720.

> **Watcher fields clarification (OQ-3)**: prior doc claimed +0x88 / +0x94 are "12 bytes for FPU watcher container". Binary truth: PoweredMaster ctor sets `param_1[0x22] = param_1 + 0x2C` (+0x88 = `&this[+0xB0]`) and `param_1[0x25] = param_1 + 0x2E` (+0x94 = `&this[+0xB8]`). These are 4-byte pointer fields, not 12-byte container regions. The FPU watcher objects ARE associated with the master, but the watcher class itself is not yet identified — see Open Questions.

---

## PoweredSubsystem (Consumer) Field Offsets [v5-validated 2026-05-28]

Base class for all subsystems that consume power. These fields are inherited by shields, engines, weapons, etc.

| Offset | Type | Field | Notes |
|--------|------|-------|-------|
| +0x18 | ptr | property | Subsystem-specific property |
| +0x30 | float | condition | Current HP |
| +0x34 | float | conditionPct | condition / maxCondition |
| +0x40 | ptr | ownerShip | Ship* |
| +0x84 | float | lastNetworkUpdate | Timestamp of last applied StateUpdate (used in ReadState gate) |
| +0x88 | float | powerReceived | Actual power received this tick |
| +0x8C | float | powerWanted | Power demanded this tick |
| +0x90 | float | powerPercentageWanted | User slider (0.0–1.0+) |
| +0x94 | float | efficiency | powerReceived / powerWanted (0.0–1.0) |
| +0x98 | float | conditionRatio | powerReceived / (normalPower * dt) |
| +0x9C | byte | isOn | Enable/disable toggle |
| +0xA0 | int | powerMode | 0=main first, 1=backup first, 2=backup only |
| +0xA4 | byte | isNetworkable | Controls MP event forwarding |

---

## Key Function Table [v5-validated 2026-05-28]

| Address | Name | Signature | Purpose |
|---------|------|-----------|---------|
| 0x00563780 | PoweredMaster_Update | __thiscall(float dt) | **Main power simulation tick** (once per second) |
| 0x00562470 | PoweredSubsystem_Update | __thiscall(float dt) | Per-consumer power draw (every frame) |
| 0x0056BC60 | ShipSubsystem::Update | __thiscall(float dt) | Base: condition tracking |
| 0x00560470 | PowerSubsystem_Ctor | __thiscall(int param) | Reactor constructor |
| 0x00563530 | PoweredMaster_Ctor | __thiscall(int param) | EPS distributor constructor |
| 0x00562240 | PoweredSubsystem_Ctor | __thiscall(int param) | Base consumer constructor |
| 0x005634A0 | PowerSubsystem_GetProperty | — | Returns this+0x18 |
| 0x005634B0 | PowerSubsystem_GetPowerOutput | — | property+0x58 * conditionPct |
| 0x005634C0 | PowerSubsystem_GetMainBatteryLimit | — | property+0x48 |
| 0x005634D0 | PowerSubsystem_GetBackupBatteryLimit | — | property+0x4C |
| 0x005634E0 | PowerSubsystem::GetMaxMainConduitCapacity | — | property+0x50 (raw); function exists but undefined in Ghidra DB |
| 0x005634F0 | PowerSubsystem_GetMainConduitCapacity_Scaled | — | property+0x50 * conditionPct |
| 0x00563520 | PowerSubsystem_GetBackupConduitCapacity | — | property+0x54 (raw, not scaled) |
| 0x00563700 | PoweredMaster_ComputeAvailablePower | __thiscall(float ticks) | Compute conduit limits and available pool |
| 0x005638D0 | PoweredMaster_AddPowerToBatteries | __thiscall(float amount) | Recharge main → overflow to backup (gate: `!IsHost OR IsMultiplayer`) |
| 0x00563A70 | PoweredMaster_DrawFromMainBattery | __thiscall(float wanted) | Mode 0: main first, then backup (host-auth gated) |
| 0x00563BB0 | PoweredMaster_DrawFromBackupBattery | __thiscall(float wanted) | Mode 1: backup first, then main (host-auth gated) |
| 0x00563CB0 | PoweredMaster_DrawFromBackupOnly | __thiscall(float wanted) | Mode 2: backup only (host-auth gated) |
| 0x005623D0 | PoweredSubsystem_GetNormalPowerWanted | vslot 30 | Returns property+0x48 if (!IsDisabled && isOn && property!=NULL), else 0 |
| 0x00562430 | PoweredSubsystem_SetPowerPercentageWanted | __thiscall(float pct) | Writes +0x90, rescales +0x8C (pure local — no network call) |
| 0x00563ED0 | PoweredMaster::ComputeTotalPowerWanted | — | Sums NormalPowerWanted * dt across all consumers (function exists at this address but undefined in Ghidra DB — see OQ-4) |
| 0x00563D50 | PoweredMaster_SetPowerSource | — | Adds consumer to head (+0xCC) of LIFO list |
| 0x005636D0 | PoweredMaster::SetupFromProperty | __thiscall | Fills batteries to limit (slot 22 of vtable 0x0088A1F0; not auto-defined in Ghidra DB) |
| 0x0055F7F0 | CloakDisengageRestoreShield | __thiscall | **CORRECTION** — cloak-decloak shield-restore handler, not "reactor enable guard" |
| 0x005644B0 | PowerSubsystem::WriteState | — | Network serialization |
| 0x00564530 | PowerSubsystem::ReadState | — | Network deserialization |
| 0x00562960 | PoweredSubsystem_WriteState | — | Round-robin (flag 0x20) power byte serialization (cross-anchored from protocol mid #11) |
| 0x005629D0 | PoweredSubsystem_ReadState | — | Round-robin (flag 0x20) power byte deserialization (cross-anchored from protocol mid #11) |

---

## Decompiled Pseudocode

### PoweredMaster_Update (FUN_00563780) — Main Power Simulation [v5-validated 2026-05-28]

```c
// vtable 0x0088A1F0, slot 25
// this = PoweredMaster at ship+0x2B0
// Runs once per INTERVAL (1.0 second, constant at 0x00892E20)
void PoweredMaster_Update(PoweredMaster* this, float deltaTime) {
    // Step 1: Call base ShipSubsystem::Update (condition tracking)
    ShipSubsystem_Update(this, deltaTime);   // FUN_0056BC60

    // Step 2: Compute elapsed game time since last update
    float gameTime = g_Clock->gameTime;       // [0x009A09D0]+0x90
    if (gameTime < this->lastUpdateTime)      // +0xC0
        this->lastUpdateTime = gameTime;

    float elapsed = gameTime - this->lastUpdateTime;
    if (elapsed > INTERVAL) {                 // INTERVAL = 1.0f at 0x00892E20
        this->powerDispensed = 0.0;           // +0xBC = reset per interval
        int ticks = (int)(elapsed / INTERVAL);

        if (!IsDisabled()) {                  // FUN_0056C350
            // Compute power output (scaled by reactor health)
            float powerOutput = GetPowerOutput();   // prop+0x58 * condPct
            float rechargeAmount = powerOutput * ticks;
            AddPowerToBatteries(rechargeAmount);    // FUN_005638D0
        }

        // Compute available power for this interval
        float availPower = ComputeAvailablePower(ticks);   // FUN_00563700
        this->availablePower = availPower;     // +0xA0

        // Update lastUpdateTime (wraps to prevent drift)
        this->lastUpdateTime = gameTime - fmod(elapsed, INTERVAL);
    }

    // Step 3: Update battery percentages for display/network
    this->mainBatteryPct = this->mainBatteryPower;
    if (GetMainBatteryLimit() > 0)
        this->mainBatteryPct /= GetMainBatteryLimit();

    this->backupBatteryPct = this->backupBatteryPower;
    if (GetBackupBatteryLimit() > 0)
        this->backupBatteryPct /= GetBackupBatteryLimit();

    // Step 4: Update watcher containers
    FPUWatcher_Update(&this->mainWatcher);     // +0x88
    FPUWatcher_Update(&this->backupWatcher);   // +0x94
}
```

### PoweredSubsystem_Update (FUN_00562470) — Per-Consumer Draw [v5-validated 2026-05-28]

```c
// Called by each powered subsystem's Update (shields, engines, weapons, etc.)
// Runs EVERY FRAME
void PoweredSubsystem_Update(PoweredSubsystem* this, float deltaTime) {
    // Step 1: Call base ShipSubsystem::Update
    ShipSubsystem_Update(this, deltaTime);

    // Step 2: Compute power wanted
    float pctWanted = this->powerPercentageWanted;          // +0x90
    float normalPower = vtable->GetNormalPowerWanted(this); // vslot 30
    float powerWanted = normalPower * pctWanted * deltaTime;
    this->powerWanted = powerWanted;                        // +0x8C

    // Step 3: Request power from master via ship+0x2B0
    Ship* ship = this->ownerShip;                           // +0x40
    PoweredMaster* master = ship->poweredMaster;            // ship+0x2B0

    // Three modes for power draw:
    switch (this->powerMode) {                              // +0xA0
        case 0: this->powerReceived = master->DrawFromMainBattery(powerWanted);   break;
        case 1: this->powerReceived = master->DrawFromBackupBattery(powerWanted); break;
        case 2: this->powerReceived = master->DrawFromBackupOnly(powerWanted);    break;
    }

    // Step 4: Compute efficiency ratio
    if (this->powerWanted > 0.0)
        this->efficiency = this->powerReceived / this->powerWanted;  // +0x94
    else
        this->efficiency = 0.0;

    // Step 5: Compute conditionRatio
    float fullPower = deltaTime * vtable->GetNormalPowerWanted(this);
    if (fullPower <= 0.0) this->conditionRatio = 1.0;       // +0x98
    else                  this->conditionRatio = this->powerReceived / fullPower;
}
```

### ComputeAvailablePower (FUN_00563700)

```c
// Called once per INTERVAL to compute how much power subsystems can draw
float ComputeAvailablePower(PoweredMaster* this, float ticks) {
    // Main conduit: limited by mainConduitCapacity * conditionPct * ticks
    float mainMax = GetMainConduitCapacity_Scaled() * ticks;  // prop+0x50 * condPct
    float backupMax = GetBackupConduitCapacity_raw() * ticks; // prop+0x54

    // Main conduit current = min(mainBatteryPower, mainMax)
    float mainAvail = min(this->mainBatteryPower, mainMax);   // +0xAC
    this->mainConduitCurrent = mainAvail;                     // +0xA4

    // Backup conduit current = min(backupBatteryPower, backupMax)
    float backupAvail = min(this->backupBatteryPower, backupMax); // +0xB4
    this->backupConduitCurrent = backupAvail;                 // +0xA8

    return mainAvail + backupAvail;
}
```

**Key insight**: Main conduit capacity is health-scaled (`condPct`), backup conduit capacity is NOT. A damaged reactor reduces main power delivery but backup delivery stays constant.

### C2 — AddPowerToBatteries gate is INVERTED (FUN_005638D0) [v5-validated 2026-05-28]

**Prior doc**: "HOST-ONLY in multiplayer (gated on g_IsHost at 0x0097FA89)" — **WRONG**.

**Binary truth** (FUN_005638D0 first line of body):

```c
if ((DAT_0097FA89 == '\0') || (DAT_0097FA8A != '\0')) {
    // recharge logic
}
```

Translated: gate is `(!IsHost) || IsMultiplayer`. Truth table:

| IsHost | IsMultiplayer | Gate value | Effective scenario |
|---|---|---|---|
| 0 | 0 | TRUE | SP-client (impossible config, but truthy) |
| 0 | 1 | TRUE | MP-client RUNS recharge |
| 1 | 0 | FALSE | SP-host SKIPS recharge |
| 1 | 1 | TRUE | MP-host RUNS recharge |

Net effect: recharge runs everywhere EXCEPT the SP-host config. But SP-host doesn't typically exist as a meaningful state (in SP, IsHost is usually 0). In practice this gate likely never excludes anything.

The actual host-authority over battery state is enforced inside the Draw functions (see C3), not here.

```c
// Recharges batteries from reactor output
// Gate: (!IsHost) || IsMultiplayer — runs everywhere except SP-host
void AddPowerToBatteries(PoweredMaster* this, float amount) {
    if ((DAT_0097FA89 == 0) || (DAT_0097FA8A != 0)) {
        float mainSpace = GetMainBatteryLimit() - this->mainBatteryPower;

        if (amount <= mainSpace) {
            this->mainBatteryPower += amount;      // +0xAC
            this->availablePower += amount;        // +0xA0
        } else {
            this->mainBatteryPower = GetMainBatteryLimit();
            this->availablePower += mainSpace;
            float remainder = amount - mainSpace;

            float backupSpace = GetBackupBatteryLimit() - this->backupBatteryPower;
            if (remainder <= backupSpace) {
                this->backupBatteryPower += remainder; // +0xB4
                this->availablePower += remainder;
            } else {
                this->backupBatteryPower = GetBackupBatteryLimit();
                this->availablePower += backupSpace;
                // Excess power is wasted
            }
        }
    }
}
```

### C3 — Client-Side Prediction in Draw Functions [v5-validated 2026-05-28]

This is **fundamental client-prediction architecture** that the prior doc completely missed.

All three Draw functions (FUN_00563A70 DrawFromMainBattery, FUN_00563BB0 DrawFromBackupBattery, FUN_00563CB0 DrawFromBackupOnly) start with the same host-authority preamble:

```c
bool bVar3 = true;       // mutate-allowed flag
bool bVar5 = true;       // early-return-allowed flag

if (DAT_0097FA89 != '\0') {                                  // host build
    iVar4 = FUN_004069B0();                                  // get local player ship
    iVar2 = *(int *)(param_1 + 0x40);                        // consumer->ownerShip

    if (DAT_0097FA8A == '\0') {                              // SP-host
        bVar5 = (iVar2 == iVar4);
        bVar3 = false;                                       // NEVER mutate in SP-host
    } else if ((iVar2 != iVar4)
            && (*(int *)(iVar2 + 0x2E4) != 0)) {             // MP, foreign player-owned ship
                                                             // [v5-clarification 2026-05-29:
                                                             //  ship+0x2E4 = NetPlayerID; 0 = AI/no owner,
                                                             //  nonzero = owned by some player. Anchor:
                                                             //  IsLocalPlayerShip @ 0x005AE140 uses the
                                                             //  same predicate.]
        bVar5 = false;
    }
}

// ...subsequent code uses `if (bVar3) { mutate battery; }` and
// `if (bVar5) { early-return when depleted; }`
```

**Implication for clean-room**: clients CALCULATE what they would have drawn (returning the value to the caller), but do NOT mutate authoritative battery state at `+0xAC` / `+0xB4`. The host's batteries are the source of truth; client-side battery values are predictive only. The Draw function still returns a power amount so the consumer can compute its `efficiency` and `conditionRatio` locally — but the underlying battery levels are reconciled via StateUpdate (see Network Propagation section).

The prior doc's naive `this->mainBatteryPower -= wanted` pseudocode is misleading and must be re-written with the bVar3/bVar5 gating.

### DrawFromMainBattery (FUN_00563A70) — Mode 0 [v5-validated 2026-05-28]

```c
// Returns actual power drawn (may be less than requested)
float DrawFromMainBattery(PoweredMaster* this, float wanted) {
    // [C3 preamble: bVar3, bVar5 set from host-auth gating — see above]

    // Check if mainConduitCurrent can supply
    if (this->mainConduitCurrent >= wanted) {   // +0xA4
        // Fully satisfied from main conduit
        this->mainConduitCurrent -= wanted;
        if (bVar3) this->mainBatteryPower -= wanted;   // +0xAC (host-only mutate)
        this->powerDispensed += wanted;                // +0xBC
        return wanted;
    }

    // Main conduit partially satisfied; try backup
    float fromMain = this->mainConduitCurrent;
    this->mainConduitCurrent = 0;

    float remaining = wanted - fromMain;
    if (this->backupConduitCurrent >= remaining) {     // +0xA8
        this->backupConduitCurrent -= remaining;
        if (bVar3) this->backupBatteryPower -= remaining;  // +0xB4 (host-only mutate)
        this->powerDispensed += wanted;
        return wanted;
    }

    // Both conduits depleted — return partial (unless bVar5 says skip)
    float fromBackup = this->backupConduitCurrent;
    this->backupConduitCurrent = 0;
    this->powerDispensed += fromMain + fromBackup;
    return fromMain + fromBackup;
}
```

### DrawFromBackupBattery (FUN_00563BB0) — Mode 1

Same logic as DrawFromMainBattery but tries backup conduit first, then falls back to main. Same C3 bVar3/bVar5 gating around battery mutations. Used by subsystems that prefer backup power (e.g., tractor beam).

### DrawFromBackupOnly (FUN_00563CB0) — Mode 2

Only draws from backup conduit. If backup is depleted, returns 0 — does NOT fall back to main. Same C3 bVar3/bVar5 gating around `+0xB4` mutations. Used for subsystems that must not touch main power (cloaking device).

---

## Power Flow Diagram

```
Per-second tick (FUN_00563780 PoweredMaster_Update):
  1. GENERATE: powerOutput * condPct  →  add to main battery, overflow to backup
                                         [gated by (!IsHost OR IsMultiplayer)]
  2. COMPUTE:  mainConduit = min(mainBattery, mainCapacity * condPct)
              backupConduit = min(backupBattery, backupCapacity)
              availablePower = mainConduit + backupConduit
  3. (consumers run their own Updates)

Per-frame (FUN_00562470 each PoweredSubsystem_Update):
  1. DEMAND: normalPowerPerSecond * percentageWanted * deltaTime
  2. DRAW:   mode 0 → main first, then backup
            mode 1 → backup first, then main
            mode 2 → backup only
            [bVar3 controls whether battery is mutated — clients calculate, host mutates]
  3. RATIO:  efficiency = received / wanted (0.0–1.0)
  4. EFFECT: subsystem performance scales by efficiency
```

---

## Consumer Registration (SetPowerSource, FUN_00563D50) [v5-validated 2026-05-28]

Each PoweredSubsystem registers itself with the PoweredMaster during `SetupFromProperty` (vtable slot 22). The master maintains a doubly-linked list of all consumers at +0xC4 (count) / +0xC8 (tail) / +0xCC (head). List nodes are 12 bytes: `[subsystem_ptr, prev, next]`, allocated from a pool at FUN_0054F720.

> **C5 — head/tail labels reversed in prior doc.** Per FUN_00563D50:
>
> ```c
> // On first insert (param_1[0x32] == NULL):
> param_1[0x32] = local_4;   // +0xC8 first set = TAIL (first node)
> param_1[0x33] = local_4;   // +0xCC first set = HEAD
>
> // On subsequent inserts (param_1[0x33] != NULL):
> *(undefined4 **)(param_1[0x33] + 4) = local_4;   // old_head->[+4] = new_head — back-link
> param_1[0x33] = local_4;                          // +0xCC = new HEAD (LIFO insertion)
> // node layout: [data:0, prev:4, next:8]
> ```
>
> So inserts grow at +0xCC (the head). +0xC8 remains pointing to the FIRST inserted node = the TAIL. Prior doc's labels were SWAPPED. The data structure is still correctly characterized as a doubly-linked list with pool-allocated nodes; only the head/tail labels needed swapping.

---

## Low-Power Behavior

- **Graceful degradation**: Each PoweredSubsystem gets partial power. The `efficiency` field (+0x94) = `powerReceived / powerWanted`, which scales subsystem performance.
- **No hard cutoff**: Subsystems don't turn off at zero power. They get `efficiency = 0.0` which makes them non-functional through their own logic (shields don't recharge, weapons don't charge, engines provide no thrust).
- **Battery depletion**: When both batteries hit zero, `mainConduitCurrent` and `backupConduitCurrent` both go to zero, so all subsystems receive 0 power.
- **Priority by draw order**: Since consumers draw per-frame and the conduit pools deplete as they draw, the order in which subsystems run their Update determines who gets power first during shortages. This is effectively the linked list insertion order.
- **Health scaling asymmetry**:
  - Reactor `PowerOutput` is scaled by `conditionPct`
  - Main conduit capacity IS scaled by `conditionPct` (via FUN_005634F0)
  - Backup conduit capacity is NOT scaled (via FUN_00563520, returns raw property+0x54)

---

## Power Initialization on Ship Spawn [v5-validated 2026-05-28]

Every ship spawns with all subsystems at 100% power, batteries full, and all consumers enabled. This is established through a four-stage initialization sequence.

### Stage 1: PoweredSubsystem Constructor (FUN_00562240) [v5-validated 2026-05-28]

The constructor chain (FUN_00562240 → FUN_0056B970) initializes every powered subsystem with these defaults:

| Offset | Type | Value | Field | Notes |
|--------|------|-------|-------|-------|
| +0x88 | float | 0.0 | powerReceived | No power received yet |
| +0x8C | float | 0.0 | powerWanted | No demand computed yet |
| +0x90 | float | 1.0 | powerPercentageWanted | 100% slider (IEEE 0x3F800000) |
| +0x94 | float | 1.0 | efficiency | Starts at full efficiency |
| +0x98 | float | 1.0 | conditionRatio | Starts at full condition |
| +0x9C | byte | 1 | isOn | Subsystem enabled |
| +0xA0 | int | 0 | powerMode | Mode 0 (main-first) |

**Key**: `powerPercentageWanted = 1.0f` at construction means every slider defaults to 100% without any explicit setter call.

### Stage 2: SetupFromProperty (FUN_00562390 / FUN_005636D0) [v5-validated 2026-05-28]

When `SetupFromProperty` (vtable slot 22) runs for each PoweredSubsystem, it reads the already-initialized `+0x90` value and computes `powerWanted = normalPower * powerPercentageWanted`. Since `+0x90 = 1.0` from the constructor, this naturally produces `powerWanted = normalPower * 1.0`.

For the PoweredMaster (EPS distributor), `SetupFromProperty` (FUN_005636D0, vtable slot 22 of 0x0088A1F0) fills both batteries to maximum capacity:

- `CALL 0x005634C0` (GetMainBatteryLimit) → `FSTP [ESI+0xAC]` → `mainBatteryPower = MainBatteryLimit`
- `CALL 0x005634D0` (GetBackupBatteryLimit) → `FSTP [ESI+0xB4]` → `backupBatteryPower = BackupBatteryLimit`

Note: FUN_005636D0 is real code at this address but is NOT auto-defined as a function in the current Ghidra DB. It's reached via vtable slot 22 pointer at 0x0088A248. The doc's address is correct; this is a Ghidra-DB artifact, not a doc error.

### Stage 3: Ship::SetupProperties (FUN_005B0110)

After all subsystems are constructed and linked, `SetupProperties` redundantly iterates ALL powered subsystems and calls `SetPowerPercentageWanted(1.0)` on each one. This is a safety net — the constructor already set 1.0, so this is a no-op in normal operation.

### Stage 4: Cloak-Decloak Shield Restore (FUN_0055F7F0) [v5-validated 2026-05-28]

### C4 — FUN_0055F7F0 is the cloak-decloak shield-restore handler, NOT a reactor enable guard

**Prior doc** (line 444): "When the reactor is enabled, a guard check at FUN_0055F7F0 forces `powerPercentageWanted = 1.0` if the current value is `<= 0.0`."

**Binary truth**: FUN_0055F7F0 is called from exactly one place — CloakingSubsystem::Update (FUN_0055E500) at the state-5 → state-0 transition (decloak complete). It is the SHIELDS-COME-BACK-ON-AFTER-DECLOAK mechanism. It is NOT triggered by reactor enable, and it does NOT operate on the reactor.

Body of FUN_0055F7F0:

1. Zeros `consumer->[+0xB0]` (cloak counter)
2. Posts event **0x0080007A** (cloak status changed)
3. Reads `ship+0x2C0` = ShieldGenerator (per binary-truth slot table, C1 above)
4. If `shield->powerPctWanted (+0x90) <= 0`, calls `SetPowerPercentageWanted(1.0)` on the SHIELD (not the reactor)
5. Posts event **0x0080007B** (shield enable)

Renamed in Ghidra to `CloakDisengageRestoreShield` + plate added. See [docs/gameplay/cloaking-state-machine.md](cloaking-state-machine.md) for the cloak state machine itself.

### Initialization Order Summary

```
1. PoweredSubsystem ctor (FUN_00562240)
   └── +0x90=1.0, +0x9C=1, +0xA0=0    ← defaults baked in constructor

2. SetupFromProperty (FUN_00562390 / FUN_005636D0)
   ├── PoweredSubsystem: powerWanted = normalPower * 1.0
   └── PoweredMaster: mainBattery=limit, backupBattery=limit

3. Ship::SetupProperties (FUN_005B0110)
   └── ForEach(subsystem): SetPowerPercentageWanted(1.0)  ← redundant safety

4. CloakDisengageRestoreShield (FUN_0055F7F0)
   └── Called only at cloak state 5→0 transition; restores SHIELD power.
       Not part of normal ship spawn init.
```

**Result**: Ship spawns with 100% power to all subsystems, batteries full, mode 0 (main-first), all enabled. This is what the player sees on the F5 Engineering panel immediately after spawn.

---

## Player Power Adjustment

Players adjust power via the F5 Engineering panel (Power Transmission Grid). Two input paths converge on the same setter function, and the 0%–125% range is enforced client-side.

### Input Paths

#### Path A: C++ Slider (EngPowerCtrl widget)

The mouse-draggable slider bars in the F5 panel are C++ `EngPowerCtrl` widgets. When the player drags a slider:

```
EngPowerCtrl::HandlePowerChange (FUN_0054DDE0)
  → identifies subsystem from slider bar (hash table at +0x58)
  → resolves subsystem group (weapons/engines/single)
  → calls SetPowerPercentageWanted (FUN_00562430) for each subsystem in group
  → posts ET_SUBSYSTEM_POWER_CHANGED (0x0080008C) event
    source = subsystem, destination = ship, float = new percentage
  → calls CallNextHandler (event chain)
```

The C++ slider performs its own range validation in `HandlePowerChange`, preventing values outside the valid range. The maximum of 1.25 comes from a float constant at 0x0088BEC0 (`1.25f`).

#### Path B: Keyboard Hotkeys (Python)

Keyboard shortcuts fire `ET_MANAGE_POWER` events, handled by `EngineerMenuHandlers.ManagePower()`:

```python
# EngineerMenuHandlers.py:376-461
def ManagePower(pObject, pEvent):
    group = int(pEvent.GetInt() / 2)    # 0=weapons, 1=engines, 2=sensors, 3=shields
    direction = pEvent.GetInt() % 2     # 0=decrease, 1=increase

    fPercentWanted += (-0.25 if direction==0 else +0.25)

    # Hard clamp
    if fPercentWanted < 0.0:  fPercentWanted = 0.0
    if fPercentWanted > 1.25: fPercentWanted = 1.25

    SetPowerToSubsystem(pSubsystem, fPercentWanted)
```

### ET_MANAGE_POWER Int Encoding

The `pEvent.GetInt()` value encodes both group and direction:

| Int Value | int/2 → Group | int%2 → Direction | Meaning |
|-----------|---------------|-------------------|---------|
| 0 | 0 → Weapons | 0 → Decrease | Weapons −25% |
| 1 | 0 → Weapons | 1 → Increase | Weapons +25% |
| 2 | 1 → Engines | 0 → Decrease | Engines −25% |
| 3 | 1 → Engines | 1 → Increase | Engines +25% |
| 4 | 2 → Sensors | 0 → Decrease | Sensors −25% |
| 5 | 2 → Sensors | 1 → Increase | Sensors +25% |
| 6 | 3 → Shields | 0 → Decrease | Shields −25% |
| 7 | 3 → Shields | 1 → Increase | Shields +25% |

Values ≥ 8 are ignored (early return at line 377).

### Subsystem Grouping

- **Weapons group** (int/2 == 0): ALL weapon subsystems (phasers, torpedoes, pulse weapons) are set to the same percentage simultaneously
- **Engines group** (int/2 == 1): Impulse AND warp engines are set together
- **Sensors** (int/2 == 2): Standalone
- **Shields** (int/2 == 3): Standalone

### Bounds Enforcement (0.0–1.25)

The valid power range is **0% to 125%** (0.0 to 1.25f). Enforcement occurs at three levels:

| Level | Mechanism | Notes |
|-------|-----------|-------|
| Python keyboard | Explicit `if fPercentWanted < 0.0` / `> 1.25` clamp | EngineerMenuHandlers.py:425-428 |
| C++ slider | HandlePowerChange (FUN_0054DDE0) validates range | Uses constant 1.25f at 0x0088BEC0 |
| Network wire | Power byte encodes `(int)(pct * 100.0)`, range 0-125 | Byte naturally caps at 255, but 125 is practical max |
| Server | **No enforcement** | Host applies whatever the client sends |

The 125% overload mechanic is visible in the F5 panel as an orange/red zone past the 100% mark. Overclocking increases demand above the normal power budget, accelerating battery drain.

### SetPowerToSubsystem Boundary Behavior

The Python `SetPowerToSubsystem()` function (EngineerMenuHandlers.py:442-461) handles the on/off transition at boundaries:

```python
def SetPowerToSubsystem(pSubsystem, fPercentWanted):
    pSubsystem.SetPowerPercentageWanted(fPercentWanted)
    if (not pSubsystem.IsOn() and fPercentWanted > 0.0):
        pSubsystem.TurnOn()       # → fires SubsystemStatus opcode 0x0A
    if (fPercentWanted == 0.0):
        pSubsystem.TurnOff()      # → fires SubsystemStatus opcode 0x0A
```

- Setting to 0% → `TurnOff()` → SubsystemStatus (opcode 0x0A) is network-forwarded immediately
- Setting to >0% on a disabled subsystem → `TurnOn()` → opcode 0x0A forwarded immediately
- The on/off toggle has **instant network propagation** (dedicated opcode), while the power percentage propagates via StateUpdate round-robin (1-2 second delay)

---

## Confirmed Constants [v5-validated 2026-05-28]

All 7 constants byte-confirmed at their cited `.rdata` addresses:

| Address | Bytes | Value | Used As |
|---------|-------|-------|---------|
| 0x00892E20 | 0x3F800000 | 1.0f | INTERVAL — power sim runs once per second |
| 0x00888B54 | 0x00000000 | 0.0f | Zero constant for float comparisons |
| 0x00888860 | 0x3F800000 | 1.0f | Used in GetCombinedConditionPercentage |
| 0x0088BEC0 | 0x3FA00000 | 1.25f | Maximum powerPercentageWanted (125% overload cap) |
| 0x0088CE78 | 0x42C80000 | 100.0f | WriteState: `(int)(pct * 100.0)` encoding multiplier |
| 0x0088D4E4 | 0x3C23D70A | 0.01f | ReadState: `byte * 0.01f` decoding multiplier |
| 0x0088B9AC | 0x437F0000 | 255.0f | Condition byte: `(condition/maxCondition) * 255.0` |

---

## Python API Surface

### PowerSubsystem (SWIG, `reference/scripts/App.py` lines 5710-5760)

**Getters:**
- `GetMainBatteryPower()` — Current main battery charge level
- `GetBackupBatteryPower()` — Current backup battery charge level
- `GetPowerOutput()` — Reactor power generation rate (health-scaled)
- `GetMainBatteryLimit()` — Maximum main battery capacity
- `GetBackupBatteryLimit()` — Maximum backup battery capacity
- `GetMaxMainConduitCapacity()` — Max main conduit (raw, not health-scaled)
- `GetMainConduitCapacity()` — Current main conduit remaining this interval
- `GetBackupConduitCapacity()` — Current backup conduit remaining this interval
- `GetAvailablePower()` — Total available (main + backup conduit)
- `GetPowerWanted()` — Total power requested by all subsystems
- `GetPowerDispensed()` — Total power delivered this interval
- `GetConditionPercentage()` — Reactor health (0.0–1.0)

**Setters:**
- `SetMainBatteryPower(float)` — Set current main battery charge
- `SetBackupBatteryPower(float)` — Set current backup battery charge
- `SetAvailablePower(float)` — Set available power reserve

**Battery manipulation:**
- `AddPower(float)` — Add power to main battery
- `DeductPower(float)` — Remove power from system
- `StealPower(float)` — Drain from main battery
- `StealPowerFromReserve(float)` — Drain from backup battery

**Watchers:**
- `GetMainBatteryWatcher()` — Event trigger on main battery changes
- `GetBackupBatteryWatcher()` — Event trigger on backup battery changes

### PowerProperty (SWIG, lines 9776-9802)

- `Get/SetMainBatteryLimit(float)`
- `Get/SetBackupBatteryLimit(float)`
- `Get/SetMainConduitCapacity(float)`
- `Get/SetBackupConduitCapacity(float)`
- `Get/SetPowerOutput(float)`

### PoweredSubsystem (inherited by all consumers)

- `GetNormalPowerWanted()` — Base power requirement from hardpoint
- `GetPowerPercentageWanted()` — User slider (0.0–1.0+)
- `SetPowerPercentageWanted(float)` — Set user slider
- `GetNormalPowerPerSecond()` — Same as NormalPowerWanted (alias)

---

## Ship Power Parameters (All Hardpoints)

> [!NOTE]
> The tables below (OQ-5) are sourced from shipped hardpoint scripts (`scripts/Custom/Ships/*.py`), NOT stbc.exe. They were NOT re-validated this pass. Values match the pre-v5 doc; format-only changes here.

### Playable Ships

| Ship | Faction | MainBattery | BackupBattery | MainConduit | BackupConduit | PowerOutput |
|------|---------|-------------|---------------|-------------|---------------|-------------|
| Enterprise-E | Fed | 300,000 | 120,000 | 1,900 | 300 | 1,600 |
| Galaxy | Fed | 250,000 | 80,000 | 1,200 | 200 | 1,000 |
| Sovereign | Fed | 200,000 | 100,000 | 1,450 | 250 | 1,200 |
| Geronimo | Fed | 240,000 | 80,000 | 1,200 | 200 | 1,000 |
| Nebula | Fed | 100,000 | 150,000 | 1,000 | 200 | 800 |
| Akira | Fed | 150,000 | 50,000 | 900 | 100 | 800 |
| Ambassador | Fed | 200,000 | 50,000 | 700 | 100 | 600 |
| Peregrine | Fed | 50,000 | 200,000 | 900 | 100 | 800 |
| Shuttle | Fed | 20,000 | 10,000 | 140 | 40 | 100 |
| Warbird | Rom | 100,000 | 200,000 | 1,700 | 300 | 1,500 |
| Vor'cha | Kli | 100,000 | 100,000 | 900 | 200 | 800 |
| Bird of Prey | Kli | 80,000 | 40,000 | 470 | 70 | 400 |
| Keldon | Card | 140,000 | 50,000 | 700 | 100 | 600 |
| Galor | Card | 120,000 | 50,000 | 550 | 150 | 500 |
| Matan Keldon | Card | 160,000 | 50,000 | 1,200 | 600 | 900 |
| Cardassian Hybrid | Card | 160,000 | 50,000 | 1,100 | 100 | 1,000 |
| Kessok Heavy | Kes | 100,000 | 100,000 | 1,500 | 100 | 1,400 |
| Kessok Light | Kes | 120,000 | 80,000 | 1,000 | 50 | 900 |
| Marauder | Fer | 140,000 | 100,000 | 900 | 200 | 700 |
| Sunbuster | — | 200,000 | 50,000 | 1,550 | 100 | 1,500 |
| Transport | — | 120,000 | 50,000 | 800 | 100 | 700 |
| Freighter | — | 70,000 | 40,000 | 650 | 400 | 600 |
| Cardassian Freighter | Card | 50,000 | 10,000 | 400 | 200 | 400 |
| Escape Pod | — | 50,000 | 20,000 | 200 | 100 | 100 |
| Probe | — | 8,000 | 4,000 | 100 | 100 | 15 |
| Probe 2 | — | 8,000 | 4,000 | 100 | 100 | 15 |

### Stations

| Station | MainBattery | BackupBattery | MainConduit | BackupConduit | PowerOutput |
|---------|-------------|---------------|-------------|---------------|-------------|
| Federation Starbase | 800,000 | 200,000 | 5,500 | 500 | 5,000 |
| Federation Outpost | 100,000 | 20,000 | 1,700 | 200 | 1,500 |
| Cardassian Starbase | 200,000 | 200,000 | 2,500 | 500 | 2,000 |
| Cardassian Station | 150,000 | 150,000 | 1,300 | 300 | 1,000 |
| Cardassian Outpost | 50,000 | 100,000 | 1,600 | 200 | 1,500 |
| Cardassian Facility | 400,000 | 50,000 | 1,000 | 600 | 1,500 |
| Space Facility | 400,000 | 200,000 | 3,000 | 1,500 | 2,000 |
| Drydock | 50,000 | 5,000 | 650 | 50 | 600 |
| Comm Array | 10,000 | 5,000 | 700 | 200 | 600 |
| Comm Light | 180,000 | 5,000 | 1,000 | 400 | 600 |
| Kessok Mine | 40,000 | 20,000 | 350 | 50 | 300 |

### Non-Combatants (Generic Template / Asteroids)

All use: MainBattery=70,000, BackupBattery=10,000, MainConduit=400, BackupConduit=200, PowerOutput=100.

---

## Subsystem Power Consumption (NormalPowerPerSecond)

> [!NOTE]
> These tables (OQ-5) are also sourced from hardpoint scripts and were NOT re-validated this pass.

### Federation Ships

| Subsystem | Sovereign | Enterprise-E | Galaxy | Nebula | Akira | Ambassador |
|-----------|-----------|-------------|--------|--------|-------|------------|
| Shields | 450 | 300 | 400 | 250 | 300 | 200 |
| Sensors | 150 | — | 100 | 100 | 150 | 50 |
| Impulse | 200 | — | 150 | 100 | 50 | 100 |
| Phasers | 400 | — | 300 | 200 | 200 | 150 |
| Torpedoes | 150 | — | 100 | 150 | 100 | 100 |
| Tractors | 700 | — | 600 | 400 | 600 | 600 |
| Repair | 1 | 1 | 1 | 1 | 1 | 1 |
| Warp | 0 | — | 0 | 0 | 0 | 0 |
| **Total** | **2,051** | **301+** | **1,651** | **1,201** | **1,301** | **1,101** |

*Enterprise-E inherits most values from Sovereign parent; only overrides shown.*

### Klingon Ships

| Subsystem | Vor'cha | Bird of Prey |
|-----------|---------|-------------|
| Shields | 250 | 180 |
| Sensors | 100 | 50 |
| Impulse | 100 | 50 |
| Disruptor Beams | 50 | — |
| Disruptor Cannons | 150 | 80 |
| Torpedoes | 150 | 50 |
| Tractors | 700 | — |
| Cloak | 700 | 380 |
| Repair | 1 | 1 |
| Warp | 0 | 0 |
| **Total (no cloak)** | **1,301** | **411** |
| **Total (cloaked)** | **2,001** | **791** |

### Romulan

| Subsystem | Warbird |
|-----------|---------|
| Shields | 400 |
| Sensors | 200 |
| Impulse | 300 |
| Disruptor Beams | 100 |
| Disruptor Cannons | 200 |
| Torpedoes | 150 |
| Tractors | 800 |
| Cloak | 1,000 |
| Repair | 1 |
| Warp | 0 |
| **Total (no cloak)** | **2,151** |
| **Total (cloaked)** | **3,151** |

### Cardassian Ships

| Subsystem | Keldon | Galor |
|-----------|--------|-------|
| Shields | 200 | 200 |
| Sensors | 50 | 50 |
| Impulse | 70 | 50 |
| Torpedoes | 70 | 50 |
| Compressors | 200 | 150 |
| Tractors | 400 | — |
| Repair | 1 | 1 |
| Warp | 0 | 0 |
| **Total** | **991** | **501** |

### Ferengi

| Subsystem | Marauder |
|-----------|----------|
| Shields | 200 |
| Sensors | 100 |
| Impulse | 50 |
| Phasers | 100 |
| Plasma Emitters | 200 |
| Tractors | 2,000 |
| Repair | 1 |
| Warp | 0 |
| **Total** | **2,651** |

*Note: Marauder tractors draw 2,000/sec — highest single-subsystem draw in the game.*

### Kessok

| Subsystem | Kessok Heavy |
|-----------|-------------|
| Shields | 500 |
| Sensors | 200 |
| Impulse | 200 |
| Positron Beams | 200 |
| Torpedoes | 200 |
| Cloak | 1,300 |
| Repair | 50 |
| Warp | 0 |
| **Total (no cloak)** | **1,350** |
| **Total (cloaked)** | **2,650** |

---

## Power Budget Analysis

Ships are designed to run at a power deficit under full combat load, slowly draining batteries:

| Ship | Output | Total Draw | Deficit | Main Battery Drain Time |
|------|--------|-----------|---------|------------------------|
| Sovereign | 1,200 | 2,051 | -851 | ~235s (3m 55s) |
| Enterprise-E | 1,600 | ~2,051 | -451 | ~665s (11m 5s) |
| Galaxy | 1,000 | 1,651 | -651 | ~384s (6m 24s) |
| Warbird | 1,500 | 2,151 | -651 | ~154s (2m 34s) |
| Warbird (cloaked) | 1,500 | 3,151 | -1,651 | ~61s (1m 1s) |
| Vor'cha | 800 | 1,301 | -501 | ~200s (3m 20s) |
| Bird of Prey | 400 | 411 | -11 | ~7,273s (~2h) |
| Keldon | 600 | 991 | -391 | ~358s (5m 58s) |
| Marauder | 700 | 2,651 | -1,951 | ~72s (1m 12s) |

*Drain time = MainBatteryLimit / deficit. Real drain is slower because some subsystems are not always active (tractors, torpedoes).*

---

## AdjustPower Algorithm (PowerDisplay.py, Python-Side)

The `AdjustPower` function in `PowerDisplay.py` (lines 876–956) runs on the client to auto-balance power when demand exceeds supply:

```python
def AdjustPower(lSystems):
    # 1. Calculate each subsystem's share of total normal power
    for pSystem in lSystems:
        dPower[pSystem] = pSystem.GetNormalPowerWanted()
        fNormTotalPower += dPower[pSystem]

    # Normalize to percentages
    for pSystem in lSystems:
        dPower[pSystem] = dPower[pSystem] / fNormTotalPower

    # 2. Check for deficit
    fTotalPower = SUM(GetNormalPowerWanted() * GetPowerPercentageWanted())
    fPowerDeficit = fTotalPower - (MainConduit + BackupConduit)

    # 3. If deficit > 1% of total power:
    if fPowerDeficit > fTotalPower * 0.01:
        for pSystem in lSystems:
            fPowerReduction = dPower[pSystem] * fPowerDeficit  # proportional
            fNewPower = max(NormalPower * NormalPercentage - fPowerReduction, 0.0)
            # Never reduce below 20% or user's desired setting
            SetPowerPercentageWanted(max(fNewPower / NormalPower, min(0.2, current)))

        # 4. Sync weapon types to same percentage
        pTorps.SetPowerPercentageWanted(pPhasers.GetPowerPercentageWanted())
        pDisruptors.SetPowerPercentageWanted(pPhasers.GetPowerPercentageWanted())

        # 5. Sync engine types to same percentage
        pWarp.SetPowerPercentageWanted(pImpulse.GetPowerPercentageWanted())
```

---

## Multiplayer Network Propagation of Power Distribution [v5-validated 2026-05-28]

### Summary

Power distribution slider changes have **NO dedicated network message**. There is no event-forwarding opcode, no Python-level TGMessage, and no C++ network send call for power changes. Instead, power percentages propagate **exclusively through the StateUpdate (opcode 0x1C)** subsystem health round-robin (flag 0x20), via the `PoweredSubsystem::WriteState` / `ReadState` virtual functions.

This is a purely state-replication design: each client sets power locally, their StateUpdate includes the current power percentages, and other peers apply them on receipt.

### Complete Code Path

#### 1. Client-side: Slider Interaction

Two input paths converge on the same setter:

**Path A: Mouse slider (C++ EngPowerCtrl widget)**
```
EngPowerCtrl::HandlePowerChange (FUN_0054DDE0)
  → identifies subsystem from slider bar (hash table at +0x58)
  → resolves ship (FUN_00562210) and subsystem group (weapons/engines/single)
  → calls SetPowerPercentageWanted (FUN_00562430) for each subsystem
  → calls FUN_0054E690: posts ET_SUBSYSTEM_POWER_CHANGED (0x0080008C) event
    source = subsystem, destination = ship, float = new percentage
  → calls CallNextHandler (event chain propagation)
```

**Path B: Keyboard hotkeys (Python EngineerMenuHandlers.ManagePower)**
```
ManagePower handler (ET_MANAGE_POWER event)
  → adjusts fPercentWanted by +/- 0.25
  → calls pSubsystem.SetPowerPercentageWanted(fPercentWanted) [SWIG → FUN_00562430]
  → posts TGFloatEvent with ET_SUBSYSTEM_POWER_CHANGED, same as Path A
```

Both paths end with `SetPowerPercentageWanted` (FUN_00562430), which is a **pure local setter** [v5-validated 2026-05-28]:

```c
void PoweredSubsystem_SetPowerPercentageWanted(PoweredSubsystem* this, float pct) {
    float oldPct = this->powerPercentageWanted;  // +0x90
    this->powerPercentageWanted = pct;
    if (oldPct != 0.0)
        this->powerWanted = (this->powerWanted * pct) / oldPct;  // +0x8C rescale
}
```

No network call. No TGEvent posting (the event is posted by the *caller*, not the setter).

#### 2. ET_SUBSYSTEM_POWER_CHANGED (0x0080008C) is LOCAL ONLY [v5-validated 2026-05-28]

The event `0x0080008C` is registered with two handlers:
- `EngPowerCtrl::HandlePowerChange` (0x0054DDE0) — registered at EngPowerCtrl ctor via FUN_006D92B0
- Mission script handlers (E5M4, E7M6, E2M2) — single-player campaign use only

**Critically, `0x0080008C` is NOT registered in the MultiplayerGame constructor (FUN_0069E590).** It does not appear in any network forwarding table. The complete list of forwarded event types is:

| Event Code | Handler Name | Network Opcode |
|------------|--------------|----------------|
| 0x008000D8 | StartFiring | 0x07 |
| 0x008000DA | StopFiring | 0x08 |
| 0x008000DC | StopFiringAtTarget | 0x09 |
| 0x008000DD | SubsystemStatus | 0x0A |
| 0x00800076 | RepairListPriority | 0x11 |
| 0x008000E0 | SetPhaserLevel | 0x12 |
| 0x008000E2 | StartCloaking | 0x0E |
| 0x008000E4 | StopCloaking | 0x0F |
| 0x008000EC | StartWarp | 0x10 |
| 0x008000FE | TorpedoTypeChange | 0x1B |

**0x0080008C is absent.** Power slider changes do NOT generate any network message. Cross-anchored to `docs/protocol/wire-format-spec.md` MultiplayerGame forwarded event table.

#### 3. Network Propagation via StateUpdate (0x1C) [v5-validated 2026-05-28]

Power percentages are serialized in the **StateUpdate flag 0x20 block** by `PoweredSubsystem_WriteState` (FUN_00562960). Cross-anchored from protocol mid #11 (`docs/protocol/stateupdate-subsystem-wire-format.md`):

**WriteState (sender, FUN_00562960):**
```c
void PoweredSubsystem_WriteState(PoweredSubsystem* this, Stream* stream, bool isOwnShip) {
    ShipSubsystem_WriteState(this, stream);  // condition byte + children
    if (!isOwnShip) {
        WriteBit(stream, 1);                                       // hasData = true
        int pctByte = (int)(this->powerPercentageWanted * 100.0);  // +0x90 → 0-100
        WriteByte(stream, pctByte);
    } else {
        WriteBit(stream, 0);                                       // hasData = false (owner has local state)
    }
    EndMarker(stream);
}
```

**ReadState (receiver, FUN_005629D0):**
```c
void PoweredSubsystem_ReadState(PoweredSubsystem* this, Stream* stream, float timestamp) {
    float lastUpdate = this->lastNetworkUpdate;  // +0x84
    ShipSubsystem_ReadState(this, stream, timestamp);   // condition byte + children
    bool hasData = ReadBit(stream);
    if (hasData) {
        int pctByte = ReadByte(stream);
        if (lastUpdate < timestamp) {  // only apply if newer
            SetPowerPercentageWanted(this, (float)pctByte * 0.01f);  // byte/100 → 0.0-1.0
        }
    }
    EndMarker(stream);
}
```

**The `isOwnShip` parameter determines whether power data is included:**
- When sending state about ship X to the player who owns ship X: `isOwnShip = 1`, power data SKIPPED
- When sending state about ship X to any other player: `isOwnShip = 0`, power data INCLUDED

This is determined in `Ship_WriteStateUpdate` (FUN_005B17F0) by comparing `ship->objectID` (ship+0x04) against the target peer's `shipObjectID` (peer+0x0C). See the "isOwnShip Determination" subsection below for details.

#### 4. Data Flow in Star Topology

```
Client A adjusts power sliders
  → SetPowerPercentageWanted() changes local subsystem +0x90
  → Client A's Ship_WriteStateUpdate sends 0x1C to host
    → PoweredSubsystem_WriteState writes powerPctWanted byte (isOwnShip=0)

Host receives 0x1C from Client A
  → Ship_ReadStateUpdate → PoweredSubsystem_ReadState
    → SetPowerPercentageWanted() applies to host's copy of Client A's ship

Host broadcasts 0x1C to Client B
  → Ship_WriteStateUpdate for Client A's ship
    → PoweredSubsystem_WriteState writes powerPctWanted byte (isOwnShip=0)

Client B receives 0x1C
  → Ship_ReadStateUpdate → PoweredSubsystem_ReadState
    → SetPowerPercentageWanted() applies to Client B's copy of Client A's ship

Host sends 0x1C back to Client A (for Client A's own ship)
  → PoweredSubsystem_WriteState writes hasData=0 bit (isOwnShip=1)
  → Client A DOES NOT overwrite its own local power settings
```

#### 5. Wire Format Detail

Within the flag 0x20 (subsystem health) block of a 0x1C StateUpdate packet, each PoweredSubsystem writes:

```
[condition: byte]          // health 0-255
[child_0 condition: byte]  // recursive children (individual weapons/engines)
[child_1 condition: byte]
...
[hasData: 1 bit]           // 1 if remote ship, 0 if own ship
[if hasData=1:]
  [powerPctWanted: byte]   // (int)(powerPercentageWanted * 100.0), range 0-125
```

The powerPctWanted byte uses range 0-100 for normal (0%-100%) and can go up to 125 for 125% overload. Values above 100 indicate the player has overclocked that subsystem.

#### 6. Encoding Precision

- **Write**: `(int)(powerPercentageWanted * 100.0)` — truncation toward zero
- **Read**: `(float)byte * 0.01f` — reconstructs approximate ratio
- **Resolution**: 1% steps (0.01 increments)
- **Range**: 0.00 to 1.25 (0% to 125%)
- **Loss**: Values like 0.33 (33%) encode to byte 33, decode to 0.33 exactly. But 0.256 encodes to 25, decodes to 0.25 — a 0.006 error (max 0.009).
- **Update rate**: Round-robin at ~10Hz per ship, so subsystem power percentages converge within 1-2 seconds for a full cycle of all 11 top-level subsystems.

#### 7. Implications

1. **No instant sync**: Power changes propagate at StateUpdate rate (~10Hz round-robin), not on-demand. A slider change takes up to 1-2 seconds to fully propagate to all peers.
2. **No server authority**: The host does not validate or enforce power percentages. It applies whatever the client sends.
3. **Auto-balance is client-side only**: The `AdjustPower` function in `PowerDisplay.py` runs locally. Other peers see the final result via StateUpdate, not the intermediate balancing.
4. **EngPowerCtrl refresh is local**: The C++ EngPowerCtrl periodic refresh (event 0x0080008D, every ~0.5s) only updates the local UI. It does not trigger any network send.
5. **TurnOn/TurnOff IS forwarded**: While power percentage is StateUpdate-only, toggling a subsystem on/off uses event 0x008000DD (SubsystemStatus, opcode 0x0A), which IS network-forwarded. The on/off state also propagates in the WriteState sign bit.

### Sign Bit Encoding (On/Off State)

In `FUN_00562900` (an alternate ReadState path), the power byte has a sign encoding:

```c
if (pctByte < 1) {
    pctByte = -pctByte;       // negate
    this->isOn = 0;           // +0x9C: subsystem OFF
} else {
    this->isOn = 1;           // +0x9C: subsystem ON
}
this->powerPercentageWanted = (float)pctByte * 0.01f;
```

This allows on/off state to be packed into the same byte as the power percentage: negative = off, positive = on. This is a secondary propagation path for on/off state alongside the dedicated SubsystemStatus opcode (0x0A).

### Two Serialization Interfaces

PoweredSubsystem has two distinct serialization interfaces, each invoked through different vtable slots:

#### Interface A: Round-Robin (flag 0x20, vtable+0x70 / vtable+0x74)

Used in the **StateUpdate flag 0x20 block** (subsystem health round-robin). This is the primary path for ongoing power state replication:

```c
// WriteState (vtable+0x70, FUN_00562960):
ShipSubsystem_WriteState(this, stream);       // condition byte + children (recursive)
if (!isOwnShip) {
    WriteBit(stream, 1);                       // hasData = 1
    int pctByte = (int)(this->powerPercentageWanted * 100.0);  // 0x0088CE78
    WriteByte(stream, pctByte);                // power percentage as 0-125
} else {
    WriteBit(stream, 0);                       // hasData = 0 (owner has local state)
}
EndMarker(stream);

// ReadState (vtable+0x74, FUN_005629D0):
float savedTimestamp = this->lastNetworkUpdate;  // +0x84 — saved BEFORE base ReadState
ShipSubsystem_ReadState(this, stream, timestamp);  // condition byte + children
bool hasData = ReadBit(stream);
if (hasData) {
    int pctByte = ReadByte(stream);
    if (savedTimestamp < timestamp) {           // only apply if packet is newer
        SetPowerPercentageWanted(this, (float)pctByte * 0.01f);  // 0x0088D4E4
    }
}
EndMarker(stream);
```

**Timestamp detail**: ReadState saves `this->lastNetworkUpdate` BEFORE calling the base class ReadState. This is critical because the base class updates `lastNetworkUpdate` from the incoming timestamp. The saved value represents the timestamp of the *previous* update, allowing the receiver to correctly determine whether the incoming data is newer.

#### Interface B: ObjCreate / Full Snapshot (vtable+0x68 / vtable+0x6C)

Used during **ObjCreate (opcode 0x02/0x03)** for initial object state transmission and in weapon round-robin (flag 0x80). This path uses sign-bit encoding:

```c
// WriteState_SignBit (vtable+0x68, FUN_005628A0):
ShipSubsystem_WriteState(this, stream);       // condition byte + children
int pctByte = (int)(this->powerPercentageWanted * 100.0);
if (!this->isOn)                               // +0x9C
    pctByte = -pctByte;                        // negate to encode OFF state
WriteByte(stream, pctByte);                    // signed byte: positive=ON, negative=OFF
EndMarker(stream);

// ReadState_SignBit (vtable+0x6C, FUN_00562900):
ShipSubsystem_ReadState(this, stream, timestamp);
int pctByte = ReadByte(stream);               // signed
if (pctByte < 1) {                            // 0 or negative
    pctByte = -pctByte;                        // absolute value
    this->isOn = 0;                            // subsystem OFF
} else {
    this->isOn = 1;                            // subsystem ON
}
this->powerPercentageWanted = (float)pctByte * 0.01f;
EndMarker(stream);
```

**Key difference from Interface A**: Interface B always includes power data (no `isOwnShip` skip), and packs the on/off state into the sign bit. This is used for initial sync where the receiver needs both the power percentage AND the on/off state in a single byte.

### Round-Robin Algorithm Detail

The round-robin serializer maintains a per-peer write cursor that persists across ticks:

```c
// From Ship_WriteStateUpdate (FUN_005B17F0), flag 0x20 section:
// Per-peer tracking structure (iVar7):
//   +0x30: linked list cursor (SubsystemListNode*)
//   +0x34: subsystem index counter (int)

if (cursor == 0) {                             // First time or reset
    cursor = ship->subsystemListHead;          // ship+0x284
    index = 0;
}

initialCursor = cursor;                        // Remember for wrap detection
WriteByte(stream, index);                      // startIndex byte — tells receiver where we start

bytesWritten = 0;
while (bytesWritten < 10) {                    // 10-byte budget per tick
    node = cursor;
    if (node == NULL) { subsystem = NULL; }
    else { subsystem = node->data; cursor = node->next; }

    subsystem->WriteState(stream, isOwnShip);  // vtable+0x70

    index++;
    if (cursor == 0) {                         // End of list: wrap
        cursor = ship->subsystemListHead;
        index = 0;
    }
    if (cursor == initialCursor) break;        // Full cycle: stop
    bytesWritten = stream.position - startPosition;
}
```

**Budget**: 10 bytes per flag 0x20 block per tick. With a Sovereign's 11 top-level subsystems (some with children), a full cycle takes ~3-5 ticks. At ~10Hz StateUpdate rate, this means ~0.3-0.5 seconds for all subsystem power percentages to be transmitted.

### isOwnShip Determination

The `isOwnShip` flag is determined in `Ship_WriteStateUpdate` (FUN_005B17F0) by comparing object IDs:

```c
// isOwnShip = (ship->objectID == peer->shipObjectID) && IsMultiplayer
// ship+0x04 = objectID (assigned at creation)
// peer+0x0C = shipObjectID (set when player selects ship)
// 0x0097FA8A = IsMultiplayer flag
```

This is an **object ID comparison**, not a connection ID comparison. When the host is writing state for ship X and sending it to the player who owns ship X, `isOwnShip = 1` and power data is omitted. This prevents the server from overwriting the owner's local slider settings with potentially stale data.

---

## Power Mode Assignments (COMPLETE) [v5-validated 2026-05-28]

The `powerMode` field at PoweredSubsystem+0xA0 controls which battery pool a subsystem draws from. There are exactly 3 modes:

| Mode | Name | Draw Function | Behavior |
|------|------|---------------|----------|
| 0 | Main-first | FUN_00563A70 | Draw from main battery (+0xA4); overflow to backup (+0xA8) |
| 1 | Backup-first | FUN_00563BB0 | Draw from backup battery (+0xB4 via +0xAC); overflow to main (+0xA4 via +0xB4) |
| 2 | Backup-only | FUN_00563CB0 | Draw exclusively from backup battery (+0xB4); NO fallback |

### Per-Subsystem Mode Assignments

Verified by exhaustive binary search for `mov DWORD PTR [reg+0xA0], N` in the PoweredSubsystem inheritance chain:

| Subsystem | Constructor | Address | powerMode | Rationale |
|-----------|-------------|---------|-----------|-----------|
| PoweredSubsystem (base) | FUN_00562240 | — | 0 (main-first) | Default for all consumers |
| ImpulseEngineSubsystem | FUN_00561050 | — | 0 (inherited) | Normal power draw |
| SensorSubsystem | FUN_00566D10 | — | 0 (inherited) | Normal power draw |
| PhaserSystem | FUN_00573C90 | — | 0 (inherited) | Normal power draw |
| TorpedoSystem | FUN_0057B020 | — | 0 (inherited) | Normal power draw |
| PulseWeaponSystem | (inherits WeaponSystem) | — | 0 (inherited) | Normal power draw |
| ShieldGenerator | FUN_0056A000 | — | 0 (inherited) | Normal power draw |
| WarpEngineSubsystem | FUN_0056DE70 | — | 0 (inherited) | Normal power draw |
| RepairSubsystem | FUN_00565090 | — | 0 (inherited) | Normal power draw |
| **TractorBeamSystem** | FUN_00582080 | **0x005820B2: `MOV [ESI+0xA0], ECX` where ECX=1** | **1 (backup-first)** | Draws from backup battery first, then main |
| **CloakingSubsystem** | FUN_0055E2B0 | **0x0055E32E: `MOV [ESI+0xA0], 0x2`** | **2 (backup-only)** | Draws exclusively from backup battery |

**Key findings:**
- Only **2 of 11** subsystem types override the default power mode
- The **cloaking device** is the only subsystem that uses mode 2 (backup-only). This means cloaking can ONLY run while the backup battery has charge. Once backup is depleted, cloaking receives zero power and the auto-decloak energy failure triggers.
- The **tractor beam** uses mode 1 (backup-first), preferring backup batteries but falling back to main power if backup is depleted. This preserves main battery charge for combat systems while the tractor is active.
- All combat and essential systems (weapons, shields, engines, sensors) use mode 0 (main-first), drawing from the main battery pool.

### Shield Recharge Special Path

ShieldClass::Update (FUN_0056A230) contains a hardcoded call to `DrawFromBackupBattery` (FUN_00563BB0) outside the normal powerMode switch. This occurs in the **dead-shield recharge path**: when the shield subsystem itself is dead (IsDead returns true) but individual facings need recharge power, the shield draws directly from backup batteries. This is NOT driven by the powerMode field -- it bypasses the switch entirely.

```
ShieldClass::Update:
  if accumulated_time >= INTERVAL (constant at 0x8E529C):
    if NOT dead AND enabled (+0x9C):
      // Normal path: per-facing calculation with 0.85 factor
      // Uses powerMode switch via base PoweredSubsystem::Update
    else:
      // Dead/disabled path: loop 6 facings
      for each facing:
        if facing NOT dead:
          // DIRECT call to DrawFromBackupBattery (bypasses powerMode)
          power = EPS->DrawFromBackupBattery(chargeRate * SHIELD_CONSTANT)
          // Then recharge this facing
          // Then return excess via AddToBackupBattery (FUN_005638D0)
```

This design means damaged shields preferentially consume backup batteries during recovery, preserving main battery charge for active combat systems. The 0.85 constant at `0x892FBC` (`0x3EA8F5C3 = 0.33` is the random phase, `0x3F59999A = 0.85` is the charge factor) scales the normal charge rate.

### Design Philosophy

The three-mode system creates a power priority hierarchy:
1. **Main battery** (mode 0): Reserved for combat-critical systems (weapons, shields, engines, sensors). These get first access to the primary power reservoir.
2. **Backup battery** (mode 1): Tractor beams draw from backup first. This prevents tractor operations from draining combat power unless backup is exhausted.
3. **Backup-only** (mode 2): Cloaking is completely isolated from the main power grid. It can only operate while the backup battery has charge, creating a natural time limit on cloak duration and making it impossible for cloaking to starve combat systems.

This is consistent with Star Trek engineering: backup/auxiliary power for stealth and utility systems, primary power for weapons and shields.

---

## Open Questions

- **OQ-1 — Event ID set** (originally posed in prior Open Question #1): partially resolved.
  - **CONFIRMED this pass**: 0x0080007A (cloak status changed — posted in FUN_0055F7F0 / CloakDisengageRestoreShield) and 0x0080007B (shield enable — posted in FUN_0055F7F0).
  - **ALREADY CONFIRMED**: 0x0080008C (ET_SUBSYSTEM_POWER_CHANGED — posted by FUN_0054E690, local-only event).
  - **STILL UNVERIFIED**: prior doc's speculative 0x80006C ("power state changed"), 0x800072 ("subsystem disabled"), 0x800073 ("subsystem enabled"), 0x8000DD ("powered subsystem state changed"). Need further trace.

- **OQ-2 — Vtable 0x008936F0 identity** (cited as TractorBeamSystem in prior doc): binary shows this vtable is xref'd from FUN_0057EC70, NOT from TractorBeamSystem_Ctor. TractorBeamSystem's actual vtable is 0x00893794. Identity of vtable 0x008936F0 is unknown — likely some weapon sub-class (TorpedoTube? Phaser hardpoint?). Not validated this pass.

- **OQ-3 — FPU watcher class at PoweredMaster +0x88 / +0x94**: confirmed as 4-byte pointer fields (NOT 12-byte containers as prior doc claimed). Pointers are set in PoweredMaster ctor to `&this[+0xB0]` and `&this[+0xB8]` respectively. The watcher OBJECTS associated with the master are real, but the watcher class type is unidentified — likely a callback-trigger class. Not validated this pass.

- **OQ-4 — FUN_00563ED0 ComputeTotalPowerWanted body**: confirmed as code at this address (16 bytes of valid prologue confirmed), but the function is NOT auto-defined in Ghidra DB. Body computation (iterates consumer list at +0xC8, sums NormalPowerWanted * dt) not byte-verified this pass.

- **OQ-5 — Per-ship hardpoint power tables** (lines under "Ship Power Parameters" and "Subsystem Power Consumption"): these are sourced from shipped hardpoint scripts (`scripts/Custom/Ships/*.py`), NOT stbc.exe. Values match the pre-v5 doc but were NOT re-validated this pass. Out of scope for binary RE.

---

## Related Documentation

- [combat-mechanics-re.md](combat-mechanics-re.md) — Damage pipeline (references power efficiency for subsystem performance)
- [cloaking-state-machine.md](cloaking-state-machine.md) — Cloak state machine; calls CloakDisengageRestoreShield (FUN_0055F7F0) at state 5→0 transition
- [shield-system.md](shield-system.md) — Shield recharge is power-budget based (efficiency affects recharge rate); ShieldGenerator vtable 0x00892F34 at ship+0x2C0
- [repair-tractor-analysis.md](repair-tractor-analysis.md) — Repair and tractor power consumption
- [../protocol/stateupdate-subsystem-wire-format.md](../protocol/stateupdate-subsystem-wire-format.md) — PoweredSubsystem::WriteState serialization (cross-anchor for FUN_00562960 / FUN_005629D0)
- [../protocol/subsystem-integrity-hash.md](../protocol/subsystem-integrity-hash.md) — Subsystem integrity hash; **CASCADE PENDING** for slot 1 (+0x2C4) reversion from HullSubsystem back to PowerSubsystem reactor
- [../protocol/wire-format-spec.md](../protocol/wire-format-spec.md) — Named Slot Layout (source of truth for 12-slot identities); MultiplayerGame forwarded event list
