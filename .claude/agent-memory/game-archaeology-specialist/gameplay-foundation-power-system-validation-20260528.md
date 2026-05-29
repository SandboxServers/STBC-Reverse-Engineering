---
name: gameplay-foundation-power-system-validation-20260528
description: Validation memo for docs/gameplay/power-system.md (gameplay foundation #3, 1221 lines) — verdict partial; class-hierarchy vtable map circular-shifted (8 swaps), 2 host-authority gating omissions, 1 cloak-shield restore mislabel
metadata:
  type: project
date: 2026-05-28
---

# power-system.md — v5 Evidence Packet (Gameplay Foundation #3)

## Overview status

**partial** — power model (3-class architecture, 5 PowerProperty fields, 3 powerMode pools, battery/conduit math, network propagation) substantively CORRECT. Ship/subsystem hardpoint tables not validated this pass (out of scope; they are mod-data not stbc.exe). Constants and helper function addresses all byte-confirmed.

ONE MAJOR ISSUE: **vtable identities in the Class Hierarchy section (lines 35-53) are scrambled across 8 of 11 subsystem classes**. Doc lists vtables but pairs them with WRONG subsystem class names. The slot offsets (which slot maps to which subsystem) are mostly correct because foundation #1 (wire-format-spec.md) had already been corrected for Pulse/Tractor swap; the **vtable-to-class-name** map within the hierarchy block is the new problem.

Three behavioral mis-claims also need correction:
1. **AddPowerToBatteries gate** (line 298) — "HOST-ONLY in multiplayer" is INVERTED from the actual `(!IsHost) || IsMultiplayer` condition.
2. **DrawFromMainBattery/Backup/BackupOnly pseudocode** (line 330-366) — OMITS host-authority gating (bVar3/bVar5) that determines whether clients actually mutate battery state.
3. **FUN_0055F7F0 mislabeled** (line 444) — "When the reactor is enabled, a guard check" is WRONG; this is the cloak-disengage shield-restore path.

Recommend re-render to `status: partial` with the vtable-identity table corrected, the 3 behavior issues fixed, and Open Question #1 promoted (event IDs verified — see below).

## Confirmed claims

### Three-class architecture (Lines 13-19)
**CONFIRMED**:
- PowerSubsystem (the reactor) is a ShipSubsystem (vtable+0x892C98). Does NOT inherit PoweredSubsystem — verified: ctor FUN_00560470 calls FUN_0056B970 (ShipSubsystem base ctor), not FUN_00562240 (PoweredSubsystem base ctor).
- PoweredSubsystem base ctor FUN_00562240 writes vtable 0x00892D98 and initializes consumer state.
- "Powered" distributor (FUN_00563530) writes vtable 0x0088A1F0 — derived from PoweredSubsystem.

### PowerProperty field offsets (lines 60-72)
**CONFIRMED via helper functions at 0x005634C0/D0/E0/F0/520**:
- +0x48 MainBatteryLimit
- +0x4C BackupBatteryLimit
- +0x50 MainConduitCapacity
- +0x54 BackupConduitCapacity
- +0x58 PowerOutput

### Slot installation (Ship__SetupProperties FUN_005B3FB0)
**Binary-truth slot table** (decompile of 0x005b3fb0..0x005b4e70 via `disassemble_function`):

| Slot | Type-ID gate | Ctor called | Vtable written | Subsystem class |
|---|---|---|---|---|
| +0x2B0 | FUN_00563470 (0x8022) | FUN_00563530 | 0x0088A1F0 | PoweredMaster (EPS distributor) |
| +0x2B4 | FUN_0057AFF0 (0x801E) | FUN_0057B020 | 0x00893598 | TorpedoSystem |
| +0x2B8 | FUN_00573C60 (0x801F) | FUN_00573C90 | 0x00893240 | PhaserSystem |
| +0x2BC | FUN_00577380 (0x8020) | FUN_005773B0 | 0x008933B0 | PulseWeaponSystem |
| +0x2C0 | FUN_00569FD0 (0x8028) | FUN_0056A000 | 0x00892F34 | ShieldGenerator |
| +0x2C4 | FUN_00560440 (0x8027) | FUN_00560470 | 0x00892C98 | PowerSubsystem (Reactor) |
| +0x2C8 | FUN_00566C90 (0x8023) | FUN_00566D10 | 0x00892EAC | SensorSubsystem |
| +0x2CC | FUN_00561020 (0x8026) | FUN_00561050 | 0x00892D10 | ImpulseEngineSubsystem |
| +0x2D0 | FUN_0056DE40 (0x8025) | FUN_0056DE70 | 0x00893040 | WarpEngineSubsystem |
| +0x2D4 | FUN_00582050 (0x8021) | FUN_00582080 | 0x00893794 | TractorBeamSystem |
| +0x2D8 | FUN_00565060 (0x8029) | FUN_00565090 | 0x00892E24 | RepairSubsystem |
| +0x2DC | FUN_0055E280 (0x8024) | FUN_0055E2B0 | 0x00892C04 | CloakingSubsystem |

(0x00892FC4 = ShipSubsystem base vtable — written by FUN_0056B970, the base-base ctor.
0x00892D98 = PoweredSubsystem base vtable — written by FUN_00562240.)

Slot offsets MATCH the doc's Class Hierarchy listing. Vtable-to-class mappings do NOT (see C1).

### Key function table (lines 145-168)
All addresses VERIFIED:
- 0x00563780 PoweredMaster::Update (FUN_00563780 decompile confirmed)
- 0x00562470 PoweredSubsystem::Update (powerMode switch at +0xA0 confirmed)
- 0x0056BC60 ShipSubsystem::Update (base)
- 0x00560470 PowerSubsystem::ctor (writes vtable 0x892C98)
- 0x005634A0 GetProperty → this+0x18 ✓
- 0x005634B0 GetPowerOutput → property+0x58 * conditionPct ✓
- 0x005634C0 GetMainBatteryLimit → property+0x48 ✓
- 0x005634D0 GetBackupBatteryLimit → property+0x4C ✓
- 0x005634E0 GetMaxMainConduitCapacity → property+0x50 (raw) — function exists but undefined in Ghidra; 16 bytes confirmed
- 0x005634F0 GetMainConduitCapacity_Scaled → property+0x50 * conditionPct ✓
- 0x00563520 GetBackupConduitCapacity → property+0x54 (raw) ✓
- 0x00563700 ComputeAvailablePower → min(battery, capacity*ticks) per pool ✓
- 0x005638D0 AddPowerToBatteries — but gate logic is INVERTED in doc (see C2)
- 0x00563A70 DrawFromMainBattery — but pseudocode omits host-auth gating (see C3)
- 0x00563BB0 DrawFromBackupBattery — same gating omission
- 0x00563CB0 DrawFromBackupOnly — same gating omission
- 0x005623D0 GetNormalPowerWanted → property+0x48 if (!IsDisabled && isOn && property!=NULL) else 0 ✓
- 0x00562430 SetPowerPercentageWanted → writes +0x90, rescales +0x8C ✓
- 0x00563ED0 ComputeTotalPowerWanted — exists as code (not defined fn in Ghidra); 16 bytes confirmed
- 0x00563D50 SetPowerSource → adds node to linked list ✓
- 0x005644B0 PowerSubsystem::WriteState ✓ (battery bytes, byte-confirmed at v5 mid #11)
- 0x00564530 PowerSubsystem::ReadState ✓ (mid #11)

### Initialization chain (lines 412-461)
**Stage 1 (FUN_00562240, PoweredSubsystem ctor)** — defaults table CONFIRMED:
- +0x88 powerReceived = 0
- +0x8C powerWanted = 0
- +0x90 powerPercentageWanted = 1.0f (0x3F800000)
- +0x94 efficiency = 1.0f
- +0x98 conditionRatio = 1.0f
- +0x9C isOn = 1
- +0xA0 powerMode = 0
- Writes vtable 0x00892D98

**Stage 2 (FUN_005636D0, PoweredMaster::SetupFromProperty)** — battery fill CONFIRMED via disasm:
- `CALL 0x005634C0` (GetMainBatteryLimit) → FSTP [ESI+0xAC] → mainBatteryPower = MainBatteryLimit ✓
- `CALL 0x005634D0` (GetBackupBatteryLimit) → FSTP [ESI+0xB4] → backupBatteryPower = BackupBatteryLimit ✓

  Note: FUN_005636D0 is NOT an auto-detected function in Ghidra DB. It's installed in PoweredMaster vtable at slot 22 (vtable+0x58 = 0x0088A248 → 0x005636D0). Doc's address is CORRECT.

### Constants (lines 564-575) — ALL byte-confirmed
- 0x00892E20 = 0x3F800000 = 1.0f (INTERVAL)
- 0x00888B54 = 0x00000000 = 0.0f
- 0x00888860 = 0x3F800000 = 1.0f
- 0x0088BEC0 = 0x3FA00000 = 1.25f (overload cap)
- 0x0088CE78 = 0x42C80000 = 100.0f (encoding mult)
- 0x0088D4E4 = 0x3C23D70A = 0.01f (decoding mult)
- 0x0088B9AC = 0x437F0000 = 255.0f (condition byte mult)

### Network propagation (lines 839-1004) — CORROBORATES protocol mid #11
- Path A (FUN_0054DDE0 EngPowerCtrl::HandlePowerChange) → calls FUN_00562430 ✓
- Path B (Python ManagePower → SWIG → FUN_00562430) ✓
- FUN_0054E690 posts event 0x0080008C carrying powerPctWanted (decompile confirms: writes &DAT_0080008C to event+0x10, then PostEvent) ✓
- Event 0x0080008C IS NOT in the MultiplayerGame forwarded list — cross-anchored from protocol foundation #1
- PoweredSubsystem::WriteState (FUN_00562960) writes hasData bit + powerPctByte gated on isOwnShip — CONFIRMED via existing v5 mid #11 plate comment
- PoweredSubsystem::ReadState (FUN_005629D0) gates apply on timestamp newer than last update — CONFIRMED

### Power modes (lines 1136-1167) — ALL CONFIRMED
- Base ctor FUN_00562240 sets +0xA0 = 0 (main-first default) ✓
- TractorBeamSystem ctor FUN_00582080 at 0x005820B2: `MOV [ESI+0xA0], ECX` where `ECX = 1` ✓ (mode 1, backup-first)
- CloakingSubsystem ctor FUN_0055E2B0 at 0x0055E32E: `MOV [ESI+0xA0], 0x2` ✓ (mode 2, backup-only)
- All other subsystem ctors do NOT touch +0xA0 → inherit mode 0 from base ctor ✓

### Consumer registration (lines 391-393)
FUN_00563D50 (PoweredMaster::SetPowerSource): allocates 12-byte node from FUN_0054F720 pool, inserts at head of linked list. CONFIRMED. Doc's "+0xC8 head, +0xCC tail" labels are REVERSED — see C5.

## Per-correction triage

### C1 — Class Hierarchy vtable-to-class map is scrambled (lines 35-53) — HIGH SEVERITY

**Severity**: material (mis-identifies 8 of 11 subsystem vtables) but does NOT affect wire format or behavioral analysis — the doc reasons about subsystems by NAME and SLOT throughout the rest of the document, not by vtable. The vtable column is the load-bearing error.

**Reconciliation table** (binary-truth from Ship__SetupProperties + ctor decompile):

| Doc claim (lines 35-53) | Actual vtable | Actual class | Verdict |
|---|---|---|---|
| ShieldGenerator (vtable 0x893598) | 0x00892F34 | ShieldGenerator | **vtable WRONG** — 0x00893598 is TorpedoSystem |
| PhaserController (vtable 0x893240) | 0x00893240 | PhaserSystem | OK (name slight: "Controller" vs "System") |
| SensorArray (vtable 0x893040) | 0x00892EAC | SensorSubsystem | **vtable WRONG** — 0x00893040 is WarpEngineSubsystem |
| ImpulseEngineSubsystem (vtable 0x892FC4) | 0x00892D10 | ImpulseEngineSubsystem | **vtable WRONG** — 0x00892FC4 is ShipSubsystem (base class) |
| WarpEngineSubsystem (vtable 0x892E24) | 0x00893040 | WarpEngineSubsystem | **vtable WRONG** — 0x00892E24 is RepairSubsystem |
| RepairSubsystem (vtable 0x892F34) | 0x00892E24 | RepairSubsystem | **vtable WRONG** — 0x00892F34 is ShieldGenerator |
| CloakingSubsystem (vtable 0x892EAC) | 0x00892C04 | CloakingSubsystem | **vtable WRONG** — 0x00892EAC is SensorSubsystem |
| TractorBeamSystem (vtable 0x8936F0) | 0x00893794 | TractorBeamSystem | **vtable WRONG** — 0x008936F0 is some other class (xref'd from FUN_0057EC70) |
| TorpedoSystem (vtable 0x893630) | 0x00893598 | TorpedoSystem | **vtable WRONG** — 0x00893630 unverified |
| PulseWeaponSystem (vtable 0x893794) | 0x008933B0 | PulseWeaponSystem | **vtable WRONG** — 0x00893794 is TractorBeamSystem |

**Suggested replacement table** (binary-truth):

```
PoweredSubsystem (vtable 0x0892D98)  ← Base for all powered systems
  Ctor: FUN_00562240
  Update: FUN_00562470 (slot 25)
  │
  ├── "Powered" distributor (vtable 0x0088A1F0)  ← Master power manager / EPS grid
  │     Ctor: FUN_00563530, slot ship+0x2B0, type ID 0x8022
  │     Update override: FUN_00563780 (MAIN POWER SIMULATION)
  │     SetupFromProperty: FUN_005636D0 (slot 22)
  │
  ├── ShieldGenerator (vtable 0x00892F34)
  │     Ctor: FUN_0056A000, slot ship+0x2C0, type ID 0x8028
  │
  ├── SensorSubsystem (vtable 0x00892EAC)
  │     Ctor: FUN_00566D10, slot ship+0x2C8, type ID 0x8023
  │
  ├── ImpulseEngineSubsystem (vtable 0x00892D10)
  │     Ctor: FUN_00561050, slot ship+0x2CC, type ID 0x8026
  │
  ├── WarpEngineSubsystem (vtable 0x00893040)
  │     Ctor: FUN_0056DE70, slot ship+0x2D0, type ID 0x8025
  │
  ├── RepairSubsystem (vtable 0x00892E24)
  │     Ctor: FUN_00565090, slot ship+0x2D8, type ID 0x8029
  │
  ├── CloakingSubsystem (vtable 0x00892C04)
  │     Ctor: FUN_0055E2B0, slot ship+0x2DC, type ID 0x8024
  │     powerMode = 2 (backup-only)
  │
  ├── TractorBeamSystem (vtable 0x00893794)
  │     Ctor: FUN_00582080, slot ship+0x2D4, type ID 0x8021
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

ShipSubsystem (vtable 0x00892FC4)  ← Base for ALL ship subsystems (incl. reactor)
  Ctor: FUN_0056B970
  Update: FUN_0056BC60 (slot 25)
  │
  └── PowerSubsystem (vtable 0x00892C98)  ← Reactor / "Warp Core"
        Ctor: FUN_00560470, slot ship+0x2C4, type ID 0x8027
        DOES NOT inherit PoweredSubsystem
        DOES NOT override Update (uses base ShipSubsystem::Update)
```

**Note on type IDs**: doc lines 32, 42 cite "type ID 0x8138" (PowerSubsystem) and "type ID 0x813E" (PoweredMaster). These are the **PowerProperty/HullProperty class IDs** in the Context Type ID space (0x812F-0x813F), NOT the subsystem instance class IDs. Subsystem instance IDs are in the 0x8021-0x8029 range (see table above, gated by FUN_005604x0 functions). The doc conflates the two namespaces.

### C2 — AddPowerToBatteries host-only claim INVERTED (line 298)

**Doc**: "HOST-ONLY in multiplayer (gated on g_IsHost at 0x0097FA89)"

**Binary** (FUN_005638D0 line 1 of body):
```c
if ((DAT_0097fa89 == '\0') || (DAT_0097fa8a != '\0')) {
    // recharge logic
}
```
Translated: `(!IsHost) || IsMultiplayer`. Truth table:

| IsHost | IsMultiplayer | Gate value |
|---|---|---|
| 0 | 0 | TRUE — SP-client (impossible config, but truthy) |
| 0 | 1 | TRUE — MP-client RUNS recharge |
| 1 | 0 | FALSE — SP-host SKIPS recharge |
| 1 | 1 | TRUE — MP-host RUNS recharge |

Net effect: recharge runs everywhere EXCEPT the SP-host config. But SP-host doesn't exist as a meaningful state (in SP, IsHost is typically 0). In practice this gate likely NEVER excludes anything.

**Suggested wording**: "Gated on `(!IsHost) || IsMultiplayer` — runs unconditionally in MP (both host AND clients), and runs in SP. The actual host-authority over battery state is enforced inside Draw functions (see C3), not here."

### C3 — Draw functions OMIT host-authority gating (lines 326-366)

**Doc** pseudocode for DrawFromMainBattery shows naive `this->mainBatteryPower -= wanted` mutations.

**Binary** (FUN_00563A70, FUN_00563BB0, FUN_00563CB0): each starts with:
```c
bVar3 = true;       // mutate-allowed
bVar5 = true;       // early-return-allowed
if (DAT_0097fa89 != '\0') {                                  // host build
  iVar4 = FUN_004069b0();                                    // get local player ship?
  iVar2 = *(int *)(param_1 + 0x40);                          // consumer->ownerShip
  if (DAT_0097fa8a == '\0') {                                // SP-host
    bVar5 = (iVar2 == iVar4);
    bVar3 = false;                                           // NEVER mutate in SP-host
  } else if ((iVar2 != iVar4)
             && (*(int *)(iVar2 + 0x2e4) != 0)) {            // MP, foreign player-owned ship
    bVar5 = false;
  }
}
```

Subsequent code uses `if (bVar3)` to gate writes to `+0xAC` (mainBatteryPower) and `+0xB4` (backupBatteryPower), and uses `if (bVar5)` to gate early-return when depleted.

**Implication for clean-room**: clients **CALCULATE** what they would have drawn (returning the value), but do NOT mutate authoritative battery state. The host's batteries are the source of truth; client-side battery values are predictive only. This is fundamental client-prediction architecture that the doc completely misses.

**Suggested addition**: a new section "Host Authority Over Battery State" placed before the per-mode pseudocode, explaining the bVar3/bVar5 gating pattern.

### C4 — FUN_0055F7F0 is the CLOAK-DECLOAK shield restore, NOT reactor enable guard (line 444)

**Doc**: "When the reactor is enabled, a guard check at FUN_0055f7f0 forces `powerPercentageWanted = 1.0` if the current value is `<= 0.0`."

**Binary**:
- Only caller is FUN_0055E500 (CloakingSubsystem::Update), at the state-5 → state-0 transition (decloak complete).
- FUN_0055F7F0 body:
  1. Zeros consumer->[+0xB0] (cloak counter)
  2. Posts event 0x0080007A (cloak status change)
  3. Reads `ship+0x2C0` = ShieldGenerator (per binary-truth slot table)
  4. If `shield->powerPctWanted (+0x90) <= 0`, calls SetPowerPercentageWanted(1.0) on the SHIELD
  5. Posts event 0x0080007B (shield enable)

This is the SHIELDS-COME-BACK-ON-AFTER-DECLOAK mechanism. It is NOT triggered by reactor enable.

**Suggested replacement** (line 442-444): "When the cloak finishes disengaging (state transition 5→0), FUN_0055F7F0 restores shield power to 1.0 if it was zeroed during cloak engagement. Reads ship+0x2C0 (ShieldGenerator), posts events 0x0080007A (cloak status) and 0x0080007B (shield enable)."

### C5 — Consumer list head/tail labels REVERSED (lines 114-115)

**Doc**: `+0xC8 consumerListHead, +0xCC consumerListTail`

**Binary** (FUN_00563D50 SetPowerSource):
```c
// On first insert (param_1[0x32] == NULL):
param_1[0x32] = local_4;   // +0xC8 first set = TAIL
param_1[0x33] = local_4;   // +0xCC first set = HEAD
// On subsequent inserts (param_1[0x33] != NULL):
*(undefined4 **)(param_1[0x33] + 4) = local_4;  // old_head->[+4] = new_head — back-link
param_1[0x33] = local_4;                         // +0xCC = new HEAD (LIFO insertion)
// node layout: [data:0, prev:4, next:8]
```

So inserts grow at +0xCC (the head). +0xC8 remains pointing to the FIRST inserted node = the TAIL. The doc's labels are SWAPPED.

(This is a minor labeling issue; the data structure is correctly characterized as a doubly-linked list with pool-allocated nodes.)

### Clar-1 — PowerProperty type ID is 0x813E (line 17) — NOT the PoweredMaster instance ID

Doc line 17 mentions "type ID: 0x813E" for the Powered master. 0x813E is the **PowerProperty CLASS ID** (the read-only template's class), not the PoweredMaster instance class. The PoweredMaster instance class ID is **0x8022** (verified via FUN_00563470 type-gate at slot installation). Both numbers are legitimate, just from different namespaces:
- 0x813E = PowerProperty (instance of which lives at PoweredMaster+0x18)
- 0x8022 = PoweredMaster instance class

Similarly for line 32: "type ID: 0x8138" for PowerSubsystem — 0x8138 is the HullProperty class ID; PowerSubsystem instance class is **0x8027**. Doc's leaf #19 memo also confused these.

### Clar-2 — Watcher fields at +0x88/+0x94 are POINTERS, not 12-byte structs (line 102-103)

Doc claims "+0x88 mainBatteryWatcher (12 bytes)". Binary (PoweredMaster ctor):
- `param_1[0x22] = param_1 + 0x2c;` → +0x88 = `&this->[+0xB0]` (just a pointer field)
- `param_1[0x25] = param_1 + 0x2e;` → +0x94 = `&this->[+0xB8]` (just a pointer field)

The FPU watchers ARE associated with the master, but +0x88 and +0x94 are 4-byte pointer fields, not 12-byte container regions. The actual watcher objects are wired elsewhere.

### Clar-3 — FUN_005636D0 SetupFromProperty exists but is not in Ghidra's function list

Doc cites FUN_005636D0 at line 434 as "PoweredMaster::SetupFromProperty". The address contains valid code (disassembled byte-for-byte, calls 0x005634C0 and 0x005634D0 to fill batteries) but Ghidra did not auto-create the function entry. Confirmed via vtable slot 22 pointer at 0x0088A248 = 0x005636D0. Doc is correct; this is a Ghidra-DB artifact, not a doc error.

## Anchor table (for docwriter frontmatter)

```yaml
binary:
  size: 6394712
  build_id: stbc.exe-2002
  image_base: 0x00400000
evidence:
  - claim: "Power system uses 3-class architecture: PowerSubsystem (reactor, vtable 0x892C98) NOT inheriting PoweredSubsystem; PoweredSubsystem base (vtable 0x892D98); PoweredMaster (vtable 0x88A1F0) at ship+0x2B0 as EPS distributor"
    address: 0x00560470
    confidence: high
    note: "Reactor ctor FUN_00560470 calls FUN_0056B970 (ShipSubsystem base) — NOT FUN_00562240 (PoweredSubsystem base) — confirming non-inheritance"
  - claim: "PoweredMaster::Update at 0x00563780 runs once per INTERVAL (1.0s constant at 0x00892E20), calls ShipSubsystem::Update, computes elapsed game time, runs AddPowerToBatteries + ComputeAvailablePower, updates battery percentages"
    address: 0x00563780
    confidence: high
  - claim: "PoweredSubsystem::Update at 0x00562470 runs every frame; per-frame powerMode switch at consumer+0xA0 dispatches to one of three Draw functions (mode 0/1/2)"
    address: 0x00562470
    confidence: high
    note: "Decompile confirms three-way switch on param_1[0x28] (= +0xA0)"
  - claim: "Ship slot installation Ship__SetupProperties at 0x005B3FB0 with binary-confirmed 12-slot subsystem table (ship+0x2B0..+0x2DC); ctor + type-gate + vtable mapping per-slot"
    address: 0x005B3FB0
    confidence: high
    note: "Full disasm of switch body 0x005B402C..0x005B445C decoded; matches foundation #1 slot identities and CORRECTS leaf #19 ship+0x2C4 mis-identification"
  - claim: "FUN_005638D0 AddPowerToBatteries gate is (!IsHost OR IsMultiplayer) — NOT 'HOST-ONLY in multiplayer' as docs/gameplay/power-system.md line 298 claims"
    address: 0x005638D0
    confidence: high
    note: "Decompile shows: if ((DAT_0097fa89 == 0) || (DAT_0097fa8a != 0)) { recharge }; doc's HOST-ONLY claim is inverted"
  - claim: "DrawFromMainBattery (0x00563A70), DrawFromBackupBattery (0x00563BB0), DrawFromBackupOnly (0x00563CB0) all contain host-authority gating (bVar3 mutate-allow, bVar5 early-return-allow) that doc pseudocode entirely omits"
    address: 0x00563A70
    confidence: high
  - claim: "FUN_0055F7F0 is the cloak-decloak shield-restore handler, NOT 'reactor enable guard' as line 444 claims. Called only from CloakingSubsystem::Update (FUN_0055E500) at state-5→state-0 transition; reads ship+0x2C0 (ShieldGenerator) and restores shield power to 1.0 if zeroed"
    address: 0x0055F7F0
    confidence: high
  - claim: "PoweredSubsystem ctor FUN_00562240 sets +0x90 (powerPercentageWanted) = 1.0, +0x9C (isOn) = 1, +0xA0 (powerMode) = 0 at construction — Stage 1 of init chain confirmed"
    address: 0x00562240
    confidence: high
  - claim: "TractorBeamSystem ctor FUN_00582080 at 0x005820B2 sets +0xA0 = 1 (mode 1, backup-first); CloakingSubsystem ctor FUN_0055E2B0 at 0x0055E32E sets +0xA0 = 2 (mode 2, backup-only). All other ctors inherit mode 0"
    address: 0x00582080
    confidence: high
  - claim: "PoweredMaster::SetupFromProperty FUN_005636D0 (slot 22 in vtable 0x0088A1F0+0x58) fills mainBatteryPower=MainBatteryLimit and backupBatteryPower=BackupBatteryLimit at spawn"
    address: 0x005636D0
    confidence: high
    note: "Disasm: CALL 0x005634C0 (GetMainBatteryLimit); FSTP [ESI+0xAC]; CALL 0x005634D0 (GetBackupBatteryLimit); FSTP [ESI+0xB4]. Function exists but is not auto-defined in Ghidra DB"
  - claim: "All 7 documented constants byte-confirmed at their cited .rdata addresses (INTERVAL=1.0f@0x892E20, 0.0f@0x888B54, 1.0f@0x888860, 1.25f@0x88BEC0, 100.0f@0x88CE78, 0.01f@0x88D4E4, 255.0f@0x88B9AC)"
    address: 0x00892E20
    confidence: high
  - claim: "Event 0x0080008C ET_SUBSYSTEM_POWER_CHANGED is posted by FUN_0054E690 (helper called from EngPowerCtrl HandlePowerChange) but is NOT in MultiplayerGame's network-forwarded event list — power slider changes propagate ONLY via StateUpdate (opcode 0x1C) round-robin"
    address: 0x0054E690
    confidence: high
    note: "Confirmed via decompile: event creation writes &DAT_0080008C to event+0x10, payload at +0x28 = source->[+0x90] (powerPctWanted)"
  - claim: "PoweredSubsystem::WriteState FUN_00562960 writes power byte gated on isOwnShip (omitted for the consumer's owning player to prevent overwriting local slider state); PoweredSubsystem::ReadState FUN_005629D0 gates apply on timestamp newer than saved lastNetworkUpdate"
    address: 0x00562960
    confidence: high
    note: "Cross-anchored from protocol mid #11 (stateupdate-subsystem-wire-format.md), v5-validated 2026-05-28"
status: partial
verified: 2026-05-28
companions:
  - docs/protocol/wire-format-spec.md
  - docs/protocol/stateupdate.md
  - docs/protocol/stateupdate-subsystem-wire-format.md
  - docs/protocol/subsystem-integrity-hash.md
  - docs/gameplay/cloaking-state-machine.md
  - docs/gameplay/shield-system.md
  - docs/gameplay/repair-system.md
```

## Open questions

- **OQ-1** — Event ID set (doc Open Question #1): doc speculates 0x80006C, 0x800072, 0x800073, 0x8000DD. From this pass: **0x0080007A** (cloak status changed — posted in FUN_0055F7F0) and **0x0080007B** (shield enable — posted in FUN_0055F7F0). 0x0080008C ET_SUBSYSTEM_POWER_CHANGED confirmed already (line 482, 887). Other event IDs need further trace.
- **OQ-2** — vtable 0x008936F0 (cited in doc as TractorBeamSystem) — actually referenced from FUN_0057EC70 — what class is this? Likely TorpedoTube or similar weapon sub-class. Not validated this pass.
- **OQ-3** — PoweredMaster +0x88 / +0x94 — confirmed as pointer fields, but the FPU watcher class they point INTO is not identified. The doc's "12 bytes for watcher" was likely from class-size estimation; actual watcher mechanism unknown.
- **OQ-4** — FUN_00563ED0 ComputeTotalPowerWanted body — confirmed as code starting with "iterate consumer list at +0xC8", but full computation not byte-verified this pass.
- **OQ-5** — Per-ship hardpoint power tables (lines 630-779) — these come from hardpoint scripts (`scripts/Custom/Ships/*.py`), not stbc.exe. Validation would require iterating shipped hardpoints; out of scope for binary RE.

## Cascade

- **subsystem-integrity-hash.md** (protocol leaf #19): C1 in that memo claimed ship+0x2C4 = HullSubsystem (0x8138). This pass shows ship+0x2C4 = PowerSubsystem (reactor, vtable 0x00892C98, instance type 0x8027). The 0x8138 = HullProperty CLASS ID — the doc confused property class IDs with subsystem instance class IDs. **Leaf #19's slot 1 reconciliation table needs re-correction back to PowerSubsystem.** Slots 4/6/7/8 corrections in leaf #19 (SensorSubsystem, WarpEngineSubsystem, RepairSubsystem, CloakDevice) all STAND — those identity changes are confirmed by this pass.
- **wire-format-spec.md** (protocol foundation #1): line 351 has `+2C4  Power  0x00892C98  Power reactor` — CORRECT, matches this pass. The Named Slot Layout in foundation #1 is the source of truth for slot identities.
- **cloaking-state-machine.md** — should reference FUN_0055F7F0 as the decloak-shield-restore handler. Possible existing coverage.
- **stateupdate-subsystem-wire-format.md** (protocol mid #11) — power byte serialization already byte-confirmed; no change.
- **stateupdate.md** (protocol mid #8) — no change.

## Ghidra renames / plates / functions created

Renamed (26 functions):
- 0x00560470 FUN_00560470 → **PowerSubsystem_Ctor**
- 0x00563530 FUN_00563530 → **PoweredMaster_Ctor**
- 0x00563780 FUN_00563780 → **PoweredMaster_Update**
- 0x00562470 FUN_00562470 → **PoweredSubsystem_Update**
- 0x00562240 FUN_00562240 → **PoweredSubsystem_Ctor**
- 0x00562430 FUN_00562430 → **PoweredSubsystem_SetPowerPercentageWanted**
- 0x005623D0 FUN_005623D0 → **PoweredSubsystem_GetNormalPowerWanted**
- 0x005634A0 FUN_005634A0 → **PowerSubsystem_GetProperty**
- 0x005634B0 FUN_005634B0 → **PowerSubsystem_GetPowerOutput**
- 0x005634F0 FUN_005634F0 → **PowerSubsystem_GetMainConduitCapacity_Scaled**
- 0x00563520 FUN_00563520 → **PowerSubsystem_GetBackupConduitCapacity**
- 0x00563700 FUN_00563700 → **PoweredMaster_ComputeAvailablePower**
- 0x005638D0 FUN_005638D0 → **PoweredMaster_AddPowerToBatteries** + plate (gate clarification)
- 0x00563A70 FUN_00563A70 → **PoweredMaster_DrawFromMainBattery** + plate (host-auth gating)
- 0x00563BB0 FUN_00563BB0 → **PoweredMaster_DrawFromBackupBattery**
- 0x00563CB0 FUN_00563CB0 → **PoweredMaster_DrawFromBackupOnly**
- 0x00563D50 FUN_00563D50 → **PoweredMaster_SetPowerSource**
- 0x0056A000 FUN_0056A000 → **ShieldGenerator_Ctor**
- 0x0055E2B0 FUN_0055E2B0 → **CloakingSubsystem_Ctor**
- 0x00561050 FUN_00561050 → **ImpulseEngineSubsystem_Ctor**
- 0x00565090 FUN_00565090 → **RepairSubsystem_Ctor**
- 0x0056DE70 FUN_0056DE70 → **WarpEngineSubsystem_Ctor**
- 0x00566D10 FUN_00566D10 → **SensorSubsystem_Ctor**
- 0x00582080 FUN_00582080 → **TractorBeamSystem_Ctor**
- 0x0055F7F0 FUN_0055F7F0 → **CloakDisengageRestoreShield** + plate (mislabel correction)

Plates added to: 0x005638D0, 0x00563A70, 0x0055F7F0.
Saved Ghidra DB.

## Patterns / lessons

1. **Property class ID vs Subsystem instance class ID is a recurring trap**. The Context Type ID space 0x812F-0x813F describes PROPERTIES (read-only hardpoint templates), while the subsystem-instance space 0x8021-0x8029 describes the runtime class. The doc (and leaf #19 memo) repeatedly conflated them. When you see a "type ID" claim, ask: which namespace? The property goes at this+0x18 (a member field); the instance ID is what GetClassID returns (vtable[1]).

2. **Vtable identification by xref is the safe path**. For each vtable address mentioned in a doc, do `get_xrefs_to(vtable_addr)`. The single ctor that writes that vtable pointer at `*param_1 = &PTR_FUN_00xxxxxx` IS the class definition. Cross-check with the type-ID gate (FUN at 0xCcccccc4 just below the ctor): the gate's hardcoded immediate is the instance class ID. This pass found 8 swapped vtables in the doc's hierarchy block — all caught by this xref-and-confirm method.

3. **Host-authority gating is a recurring blind spot in pre-v5 docs**. Pre-v5 power/damage/movement docs tend to read decompiled pseudocode as "this is what happens" without noticing the `if (DAT_0097fa89)` (IsHost), `if (DAT_0097fa8a)` (IsMultiplayer) gates that often restrict state mutations to the host. These gates create client-prediction vs host-authoritative architecture splits that the doc must call out. Three Draw functions in this doc all had it omitted.

4. **"Pseudocode close" can hide critical guards**. The doc's pseudocode for `SetPowerPercentageWanted` (line 873-880) reads correctly: it shows `if (oldPct != 0.0)` for the rescale. The binary uses `bVar2 = fVar1 != _DAT_00888b54` which is the SAME check (0.0). But the equally-close-looking AddPowerToBatteries had a gate that the doc completely missed. Lesson: when validating pseudocode, check every `if` in the binary, not just the algorithmic core.

5. **"Function exists at this address but isn't a Ghidra function" is a thing**. FUN_005636D0 (PoweredMaster::SetupFromProperty) and FUN_005634E0 (GetMaxMainConduitCapacity) are real code paths reachable via vtable slots — and the doc's addresses are correct — but Ghidra's auto-analyzer didn't promote them. They show as "no function found" via decompile_function. Use `read_memory` + manual disasm to verify, OR check vtable slots for code-pointing-into-here addresses. This is an artifact of the v5 import policy (no annotation scripts run), not a doc error.
