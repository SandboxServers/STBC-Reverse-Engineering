> [docs](../README.md) / [protocol](README.md) / subsystem-integrity-hash.md

---
title: Subsystem Integrity Hash (anti-cheat) — RE Analysis
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
  - claim: "ComputeSubsystemIntegrityHash at 0x005b5eb0 reads 12 container slots from ship+0x27C in a fixed order, calling base/weapon/individual hash helpers per slot"
    address: 0x005b5eb0
    function: ComputeSubsystemIntegrityHash
    completeness: 26.0
    effective: 38.3
    confidence: high
    note: "Full decompile; 12 slot-offset reads (+0x48, +0x44, +0x34, +0x4C, +0x50, +0x54, +0x5C, +0x60, +0x38, +0x3C, +0x40, +0x58) match the corrected slot table exactly. Renamed + plate this pass."
  - claim: "HashBaseSubsystem at 0x005b6170 hashes 7 property floats + N children (recursive) + 4 boolean sentinels + optional PoweredSubsystem energy field"
    address: 0x005b6170
    function: HashBaseSubsystem
    completeness: 10.4
    effective: 25.4
    confidence: high
    note: "All 4 boolean magic-constant pairs match doc table byte-for-byte. Renamed + plate this pass."
  - claim: "HashWeaponSystem at 0x005b6330 wraps HashBaseSubsystem with 2 weapon-system boolean sentinels + per-child HashIndividualWeapon + optional torpedo-system extras"
    address: 0x005b6330
    function: HashWeaponSystem
    completeness: 7.6
    effective: 25.7
    confidence: high
    note: "2 weapon-system magic constants match doc table byte-for-byte. Renamed + plate this pass."
  - claim: "HashIndividualWeapon at 0x005b6560 dispatches 5-way per weapon type (0x802B EnergyWeapon, 0x802C PhaserBank, 0x802D PulseWeapon, 0x802E TractorBeamProjector, 0x802F TorpedoTube)"
    address: 0x005b6560
    function: HashIndividualWeapon
    confidence: medium
    note: "Function exists, dispatcher renamed; per-type property-offset reads not byte-checked this pass (see Open Question OQ-2)"
  - claim: "HashFoldFloat at 0x005b6c10 — abs(__ftol(value)) integer, then per-byte XOR into accumulator, then ROL by 1"
    address: 0x005b6c10
    function: HashFoldFloat
    completeness: 29.5
    effective: 40.9
    confidence: high
    note: "Body 0x005b6c10..0x005b6c94. Renamed + plate this pass."
  - claim: "Sender Ship__WriteStateUpdate at 0x005b17f0 emits has_hash bit only when !isMultiplayer; the wire hash is (hash >> 16) ^ (hash & 0xFFFF) — a 16-bit XOR fold"
    address: 0x005b1d96
    function: Ship__WriteStateUpdate
    confidence: high
    note: "Disasm anchor 0x005b1d96..0x005b1dc1: TEST BL,BL; PUSH 0x1; CALL WriteBit (0x006cf770); LEA ECX,[ESI+0x27c]; CALL 0x005b5eb0; SAR EDX,0x10; XOR EAX,EDX; CALL WriteShort (0x006cf7f0). BL = bVar19 set at 0x005b1906."
  - claim: "Receiver Ship__ReadStateUpdate at 0x005b21c0 validates the hash only when isMultiplayer; on mismatch it posts event_type 0x008000F6 (ET_BOOT_PLAYER) at event+0x10"
    address: 0x005b2311
    function: Ship__ReadStateUpdate
    confidence: high
    note: "Disasm anchor 0x005b22ff..0x005b232c: MOV [EDI+0x10], 0x8000f6 (immediate); MOV ECX, 0x97f838 (TGEventManager singleton); MOV [EDI+0x28], EAX (playerSlot); CALL 0x006da2a0 (PostEvent)."
  - claim: "Kick path ET_BOOT_PLAYER (0x008000F6) -> MultiplayerWindow_BootPlayerHandler (0x00506170) -> TGBootPlayerMessage with reason=4"
    address: 0x00506170
    function: MultiplayerWindow_BootPlayerHandler
    completeness: 17.7
    effective: 33.0
    confidence: high
    note: "Function CREATED this pass (was undefined in Ghidra DB). Cross-confirmed via reference/decompiled/04_ui_windows.c line 2027 registers this address with the string MultiplayerWindow__BootPlayerHandler keyed on &DAT_008000f6. reason=4 confirmed via MOV [ESI+0x40], 0x4 at 0x005061CD; TGBootPlayerMessage size = 0x44 bytes (PUSH 0x44 at 0x005061A0)."
  - claim: "Container at ship+0x27C is a sub-object created by FUN_005b5d00 with its own vtable at 0x008944c8; the ctor zero-fills param_1[1..0x18] which arithmetically aliases ship+0x280..+0x2DC"
    address: 0x005b5d00
    function: ShipSubsystemContainer_Ctor
    confidence: high
    note: "Container offsets +0x34..+0x60 alias ship+0x2B0..+0x2DC; this explains why the hash function's container-relative offsets are bytewise identical to the named-slot table populated by Ship__SetupProperties."
  - claim: "Slot subsystem identities (CORRECTED 2026-05-28; slot 1 re-corrected via docs/gameplay/power-system.md C1 cascade 2026-05-28): slot 1 +0x2C4 PowerSubsystem reactor (instance class ID 0x8027, vtable 0x00892C98); slot 3 +0x2B0 PoweredSubsystem master (0x813E); slot 4 +0x2C8 SensorSubsystem (0x8139); slot 6 +0x2D0 WarpEngineSubsystem (0x813B); slot 7 +0x2D8 RepairSubsystem (0x813F); slot 8 +0x2DC CloakDevice (0x813A) — five pre-v5 labels were stale (slot 1 was correctly 'Power Reactor' pre-v5; a transient HullSubsystem 0x8138 rename was reverted via power-system cascade)"
    address: 0x005b5eb0
    function: ComputeSubsystemIntegrityHash
    completeness: 26.0
    effective: 38.3
    confidence: high
    note: "C1 — see body. Foundation cross-anchor: wire-format-spec.md Named Slot Layout (v5-validated 2026-05-28). Slot 1 +0x2C4 cascade-corrected 2026-05-28 via docs/gameplay/power-system.md C1: the 0x8138 class ID is PowerProperty (script-facing property type returned by getter wrappers FUN_005634C0/D0/E0/F0/520), NOT the subsystem instance class. The underlying SUBSYSTEM at ship+0x2C4 has vtable 0x00892C98 = PowerSubsystem reactor (instance class ID 0x8027 per Ship__SetupProperties FUN_005B3FB0). Hash function reads correct offsets; only the human-readable identity column was wrong. Doc line 129 negative claim is now WRONG: RepairSubsystem IS hashed at slot 7."
  - claim: "All 6 boolean sentinel magic constants byte-exact: prop+0x24 64.0002f/76.6f; subsys+0x44 98.6f/100.0f; prop+0x25 14.3f/456.1f; prop+0x26 27.3f/16.1f; wsProp+0x50 0.4f/99.1f; wsProp+0x51 32.6f/487.1f"
    address: 0x005b6170
    function: HashBaseSubsystem
    confidence: high
    note: "All 6 hex bit-patterns (0x42800083 / 0x42993333 / 0x42c53333 / 0x42c80000 / 0x4164cccd / 0x43e40ccd / 0x41da6666 / 0x4180cccd / 0x3ecccccd / 0x42c63333 / 0x42026666 / 0x43f38ccd) match the doc table verbatim."
  - claim: "Sender uses signed shift (SAR EDX, 0x10) for the high-16-bit fold; low 16 bits are wire-identical to an unsigned shift because WriteShort truncates"
    address: 0x005b1db6
    function: Ship__WriteStateUpdate
    confidence: high
    note: "Clar-4. Pedantic only — for re-implementers using a signed int32 hash type."
  - claim: "Receiver mismatch event posting uses raw TGEvent allocation (TGAlloc 0x2C -> ctor chain FUN_00717b70 -> FUN_00718010 -> FUN_006bb840 -> FUN_006d62b0 -> FUN_006da2a0); it does NOT use TGFactory_DeserializeObject"
    address: 0x005b21c0
    function: Ship__ReadStateUpdate
    confidence: high
    note: "Send-side event POSTING (command-style), not wire-side deserialization. Matches the leaf #18 command-message-bypasses-TGFactory pattern. Cross-link: objnotfound-requestobj-enterset-wire-format.md (Clar1 Command Messages vs Event Messages)."
  - claim: "PatchSubsystemHashCheck at 0x005b22b5 (binary patch in src/proxy/ddraw_main/binary_patches_and_python_bridge.inc.c) is safe because stock gameplay never reaches the hash mismatch path — sender emits has_hash=0 in MP"
    address: 0x005b22b5
    function: null
    confidence: high
    note: "Mutually exclusive gates -> dead code in MP confirmed."
  - claim: "DAT_0097fa8a is IsMultiplayer (byte); DAT_0097f838 is TGEventManager singleton; DAT_009878cc is MultiplayerWindow singleton"
    address: 0x0097fa8a
    function: null
    confidence: high
    note: "Engine cross-anchors — see CLAUDE.md Key Globals. DAT_0097f838 is the same global cited by pythonevent-wire-format.md for AddEvent calls."
companions:
  - docs/protocol/wire-format-spec.md
  - docs/protocol/stateupdate.md
  - docs/protocol/stateupdate-subsystem-wire-format.md
  - docs/protocol/per-ship-subsystem-wire-format.md
  - docs/protocol/objnotfound-requestobj-enterset-wire-format.md
  - docs/protocol/v5-validation-status.md
  - docs/engine/rtti-class-catalog.md
supersedes:
  - 2026-02-15
---

# Subsystem Integrity Hash — Reverse Engineering Analysis

> [!NOTE]
> This doc is `status: partial`. **ONE material correction (slot subsystem-identity labels)** + 4 clarifications. Hash function reads correct offsets; only the human-readable identity column in the slot table was stale. Doc line 129 negative claim ("The Repair subsystem does NOT appear in the hash") is now WRONG — RepairSubsystem IS hashed at slot 7 (ship+0x2D8). All other claims — functions, sender/receiver gates, wire encoding, the 6 boolean sentinel magic constants, the dead-code-in-MP proof, and the kick path — are byte-by-byte confirmed. **C1** rewrites the 12-row slot table to match foundation #1's corrected ship-slot identities and fixes the line 129 negative claim. **Clar-1** documents the receiver event-type immediate at `event+0x10`. **Clar-2** documents a torpedo int-to-float cast precision detail. **Clar-3** notes that `&ET_BOOT_PLAYER` and `0x008000F6` are the same address constant. **Clar-4** notes the sender's signed `SAR` is wire-identical to an unsigned shift. See [v5-evidence-header.md](../guides/v5-evidence-header.md) for the standard. Source evidence: `.claude/agent-memory/game-archaeology-specialist/subsystem-integrity-hash-validation-20260528.md`.
>
> **Post-validation cascade 2026-05-28**: Slot 1 (+0x2C4) attribution corrected from "HullSubsystem 0x8138" back to "PowerSubsystem (Reactor) 0x8027" per docs/gameplay/power-system.md C1 cascade. The 0x8138 class ID is PowerProperty (script-facing property type), not the subsystem instance class. Other slot identities from leaf #19 unchanged.
>
> **2026-05-28 meta-cascade**: Slot 1 (+0x2C4) was originally HullSubsystem in leaf #19 — power-system C1 cascade "corrected" to PowerSubsystem (Reactor) — sensor/hull RE definitively reverted to HullSubsystem (vtable strings prove "HullClass"). Slot 1 IS HullSubsystem. PowerSubsystem reactor is at ship+0x2B0. See `.claude/agent-memory/game-archaeology-specialist/sensor-hull-subsystem-validation-20260528.md` for the binary-truth evidence (literal vtable strings "HullClass" / "_p_HullClass" / "HullClassPtr" at vtable 0x00892C98; PoweredMaster reactor class 0x813E at vtable 0x0088A1F0 lives at ship+0x2B0 via PoweredMaster_Ctor 0x00563530).

---

## Overview

The subsystem integrity hash is a tamper-detection system that hashes all ship subsystem property values (health, weapon stats, shield facings, etc.) into a 32-bit checksum, XOR-folded to 16 bits for wire transmission. It was designed to detect client-side cheating by comparing a locally-computed hash against the one received in StateUpdate packets.

**Dead code in multiplayer**: The sender (`Ship__WriteStateUpdate` at 0x005b17f0) only writes the hash when `isMultiplayer == 0` (single-player). The receiver (`Ship__ReadStateUpdate` at 0x005b21c0) only validates it when `isMultiplayer == 1` (multiplayer). These conditions are mutually exclusive in stock gameplay — the hash is never sent AND checked in the same session. This is proven byte-by-byte below.

### Function Table

[v5-validated 2026-05-28]

| Address | Name | Signature | Purpose |
|---------|------|-----------|---------|
| 0x005b6c10 | `HashFoldFloat` | `void(float value, uint32_t* acc)` | XOR + rotate accumulator |
| 0x005b6170 | `HashBaseSubsystem` | `float(ShipSubsystem* subsys)` | 7 floats + children + 4 booleans + optional powered extra |
| 0x005b5eb0 | `ComputeSubsystemIntegrityHash` | `uint32_t __fastcall(void* container)` | 12 slots in fixed order, type-specific extras |
| 0x005b6330 | `HashWeaponSystem` | `float(ShipSubsystem* weaponSys)` | base + 2 booleans + per-child dispatch + torpedo data |
| 0x005b6560 | `HashIndividualWeapon` | `float(EnergyWeapon* weapon)` | 5-way type dispatch per weapon |
| 0x005b17f0 | `Ship__WriteStateUpdate` (sender) | — | Writes hash only when `!isMultiplayer` AND flag 0x01 |
| 0x005b21c0 | `Ship__ReadStateUpdate` (receiver) | — | Checks hash only when `isMultiplayer` AND `has_hash != 0` |
| 0x00506170 | `MultiplayerWindow_BootPlayerHandler` | — | Kick path target — CREATED in Ghidra this pass |

---

## C1 — Slot subsystem-identity column (5 of 12 rows mislabeled)

[v5-validated 2026-05-28] [post-validation cascade 2026-05-28 via docs/gameplay/power-system.md]

The pre-v5 doc labeled five of the twelve hash slots with stale subsystem identities. The hash function reads the **correct container offsets** — and those offsets alias the correct **ship offsets** — but the human-readable subsystem name column was wrong on five rows. This is a cascade from foundation #1 (`wire-format-spec.md` C1, validated 2026-05-28), which corrected the canonical ship-slot table, added the previously-missing rows at ship+0x2C8 (SensorSubsystem) and ship+0x2DC (CloakDevice), and confirmed PoweredSubsystem master at ship+0x2B0.

> **PowerProperty class ID 0x8138 vs PowerSubsystem instance class ID 0x8027**: The hash function reads property values via PoweredSubsystem helpers (FUN_005634C0/D0/E0/F0/520). The PowerProperty CLASS at vtable 0x..._8138 is the SCRIPT-FACING property type returned by getter wrappers; the underlying SUBSYSTEM instance at ship+0x2C4 has vtable 0x00892C98 (class ID 0x8027 per Ship__SetupProperties FUN_005B3FB0). The leaf #19 correction conflated these two class-ID namespaces. The pre-v5 doc's "Power Reactor" label at slot 1 was already correct; an intermediate v5 rename to "HullSubsystem (0x8138)" has been reverted via the 2026-05-28 power-system cascade.
>
> **Meta-cascade sub-note (2026-05-28)**: The class 0x8027 here is **HullSubsystem** (binary vtable string proof: literal "HullClass" / "_p_HullClass" / "HullClassPtr" anchored to vtable 0x00892C98), NOT PowerSubsystem reactor. PowerSubsystem reactor (PoweredMaster, class 0x813E) lives at **ship+0x2B0** instead, set by Ship__SetupProperties case 0x813E via PoweredMaster_Ctor at 0x00563530 with vtable PTR_FUN_0088A1F0. The slot 1 (+0x2C4) attribution in this doc is HullSubsystem; PowerSubsystem reactor occupies a different ship slot. See `.claude/agent-memory/game-archaeology-specialist/sensor-hull-subsystem-validation-20260528.md` for the vtable-string evidence.

**Key archaeological finding.** The container at `ship+0x27C` is a sub-object constructed by `FUN_005b5d00` with its own vtable at `0x008944c8`. The ctor zero-fills `param_1[1..0x18]` — exactly the range `ship+0x280..ship+0x2DC` that overlaps the named-slot table at `ship+0x2B0..0x2DC`. So `container+N == ship+0x27C+N` arithmetically. After `Ship__SetupProperties` populates the named-slot pointers, the hash function reads those same pointers through the container alias. This is why the doc's container-relative offsets are consistent with the canonical ship offsets — they refer to the same memory through two aliases.

### Corrected Slot Table (binary truth)

| Hash Order | Container Offset | Ship Offset | Subsystem (CORRECTED) | Prior Label | Hash Method |
|---|---|---|---|---|---|
| 1 | +0x48 | +0x2C4 | **HullSubsystem (class 0x8027) vtable 0x00892C98** `[v5-meta-cascade 2026-05-28 — vtable strings "HullClass" prove identity]` | Power Reactor | `HashBaseSubsystem` |
| 2 | +0x44 | +0x2C0 | ShieldGenerator (0x8137) | Shield Generator | base + 12-float shield-array extras |
| 3 | +0x34 | +0x2B0 | **PoweredSubsystem (master)** (0x813E) | Powered Master | base + 5-float powered extras |
| 4 | +0x4C | +0x2C8 | **SensorSubsystem** (0x8139) | Cloak Device | base + 1-float (prop+0x4C) |
| 5 | +0x50 | +0x2CC | ImpulseEngineSubsystem (0x813C) | Impulse Engine | base + 4-float ordered extras |
| 6 | +0x54 | +0x2D0 | **WarpEngineSubsystem** (0x813B) | Sensor Array | `HashBaseSubsystem` |
| 7 | +0x5C | +0x2D8 | **RepairSubsystem** (0x813F) | Warp Drive | base + 1-float (prop+0x4C) |
| 8 | +0x60 | +0x2DC | **CloakDevice** (0x813A) | Crew / Unknown-A | base + side-effect `FUN_0055e220` |
| 9 | +0x38 | +0x2B4 | TorpedoSystem (0x8133) | Torpedo System | `HashWeaponSystem` (children + torpedo extras) |
| 10 | +0x3C | +0x2B8 | PhaserSystem (0x812F, iVar4==1) | Phaser System | `HashWeaponSystem` (children) |
| 11 | +0x40 | +0x2BC | PulseWeaponSystem (0x812F, iVar4==3) | Pulse Weapon System | `HashWeaponSystem` (children) |
| 12 | +0x58 | +0x2D4 | TractorBeamSystem (0x812F, iVar4==4) | Tractor Beam System | `HashWeaponSystem` (children) |

Bolded rows are corrections. Slot 1 (+0x2C4) underwent a meta-cascade: pre-v5 label was "Power Reactor"; rev 1 (cascade-patch from power-system C1) said "PowerSubsystem (Reactor)"; rev 2 (sensor/hull RE, the FINAL binary truth) reverted to **HullSubsystem** (class 0x8027, vtable 0x00892C98) — vtable strings "HullClass" / "_p_HullClass" / "HullClassPtr" prove identity. The actual PowerSubsystem reactor (PoweredMaster, class 0x813E, vtable 0x0088A1F0) lives at ship+0x2B0 instead. Authority: foundation doc [`wire-format-spec.md`](wire-format-spec.md) (Named Slot Layout, v5-validated 2026-05-28, meta-cascade rev 2 applied) and [`docs/gameplay/power-system.md`](../gameplay/power-system.md) C1 (slot 1 cascade rev 2, 2026-05-28). Reference: `.claude/agent-memory/game-archaeology-specialist/sensor-hull-subsystem-validation-20260528.md`.

### Downstream impact — line 129 negative claim is wrong

The pre-v5 body line 129 read:

> The Repair subsystem (ship+0x2C0 in the main container table) does NOT appear in the hash.

This statement is wrong on **two** counts:

1. **ShieldGenerator** is at `ship+0x2C0` — that slot has never been Repair, in the hash or in the named-slot table. The pre-v5 doc was carrying a stale label from an earlier (pre-foundation-#1) misidentification.
2. **RepairSubsystem** is at `ship+0x2D8` (slot 7 of the hash). It **does** appear in the hash, via `HashBaseSubsystem` + a 1-float `prop+0x4C` extra.

Corrected statement (replace line 129):

> All 12 named subsystem slots (PowerReactor, Shield, PoweredMaster, Sensor, Impulse, Warp, Repair, Cloak, Torpedo, Phaser, Pulse, Tractor) DO appear in the hash via the container alias at `ship+0x27C`. See foundation [`wire-format-spec.md`](wire-format-spec.md) Named Slot Layout (v5-validated 2026-05-28) for the authoritative ship-slot identity table, and [`docs/gameplay/power-system.md`](../gameplay/power-system.md) C1 for the slot 1 cascade (PowerSubsystem reactor at ship+0x2C4 with instance class ID 0x8027 — not PowerProperty 0x8138, which is the script-facing property class).

---

## HashFoldFloat (0x005b6c10)

[v5-validated 2026-05-28]

Core accumulator function. Called once per hashed value. Body 0x005b6c10..0x005b6c94.

```c
void HashFoldFloat(float value, uint32_t* accumulator) {
    // Convert float to absolute integer (truncation via x87 __ftol)
    bool negative = (value < 0.0f);
    int32_t ival = (int32_t)value;
    if (negative) ival = -ival;

    // XOR each byte of ival into accumulator
    uint8_t* acc_bytes = (uint8_t*)accumulator;
    uint8_t* val_bytes = (uint8_t*)&ival;
    for (int i = 0; i < 4; i++) {
        acc_bytes[i] ^= val_bytes[i];
    }

    // Rotate left by 1 bit
    *accumulator = (*accumulator << 1) | (*accumulator >> 31);
}
```

The absolute-value step means positive and negative values of the same magnitude produce identical hash contributions (e.g., 3.7f and -3.7f both contribute integer 3).

---

## HashBaseSubsystem (0x005b6170)

[v5-validated 2026-05-28]

Called for every subsystem. Contributes a minimum of 11 `HashFoldFloat` calls (7 property floats + 4 boolean sentinels), plus 1 more if it is a PoweredSubsystem, plus N more for N children (recursive).

```c
float HashBaseSubsystem(ShipSubsystem* subsys) {
    float hash = 0.0f;
    SubsystemProperty* prop = subsys->property;  // *(subsys + 0x18)

    // --- 7 base property floats (hashed in this exact order) ---
    HashFoldFloat(prop->maxCondition,      &hash);  // property+0x20
    HashFoldFloat(prop->currentPower,      &hash);  // property+0x40
    HashFoldFloat(prop->field_0x28,        &hash);  // property+0x28
    HashFoldFloat(prop->field_0x2C,        &hash);  // property+0x2C
    HashFoldFloat(prop->field_0x30,        &hash);  // property+0x30
    HashFoldFloat(prop->field_0x44,        &hash);  // property+0x44
    HashFoldFloat(prop->repairComplexity,  &hash);  // property+0x3C

    // --- Recursively hash all child subsystems ---
    int childCount = *(int*)(subsys + 0x1C);
    for (int i = 0; i < childCount; i++) {
        ShipSubsystem* child = FUN_0056c570(subsys, i);  // GetChildSubsystem
        float childHash = HashBaseSubsystem(child);       // RECURSIVE
        HashFoldFloat(childHash, &hash);
    }

    // --- 4 boolean sentinel values (AFTER children) ---
    bool flag1 = FUN_0056c330(subsys);            // property+0x24 (disableable)
    HashFoldFloat(flag1 ? 64.0002f : 76.6f, &hash);

    bool flag2 = *(uint8_t*)((char*)subsys + 0x44);  // subsys+0x44 (operational state)
    HashFoldFloat(flag2 ? 98.6f : 100.0f, &hash);

    bool flag3 = FUN_0056c340(subsys);            // property+0x25 (repairable)
    HashFoldFloat(flag3 ? 14.3f : 456.1f, &hash);

    bool flag4 = *(uint8_t*)(prop + 0x26);        // property+0x26 (primary flag)
    HashFoldFloat(flag4 ? 27.3f : 16.1f, &hash);

    // --- PoweredSubsystem extra field ---
    PoweredSubsystem* powered = FUN_00562210(subsys);  // CastToPowered, type 0x801C
    if (powered != NULL) {
        PoweredSubsystemProperty* powProp = FUN_005621b0(powered);
        HashFoldFloat(powProp->field_0x48, &hash);  // property+0x48 (energy field)
    }

    return hash;
}
```

**Critical ordering**: children are hashed BEFORE the boolean sentinels. Child hash values feed into the accumulator state that the booleans then modify.

---

## ComputeSubsystemIntegrityHash (0x005b5eb0)

[v5-validated 2026-05-28]

Called as `__fastcall` with `ship + 0x27C` (subsystem container pointer) in ECX. Hashes 12 subsystem slots in a fixed order, with type-specific extra fields per slot. Each slot is NULL-checked before hashing; if a slot pointer is NULL, it is skipped.

See **C1 — Slot subsystem-identity column** above for the corrected slot table. The container offsets `+0x34..+0x60` arithmetically alias `ship+0x2B0..+0x2DC` because the container itself lives at `ship+0x27C` and zero-fills that range in its ctor (`FUN_005b5d00`).

---

## HashWeaponSystem (0x005b6330)

[v5-validated 2026-05-28]

Called for slots 9-12 (the 4 weapon-system slots). Extends `HashBaseSubsystem` with weapon-specific data.

```c
float HashWeaponSystem(ShipSubsystem* weaponSys) {
    float hash = 0.0f;
    WeaponSystemProperty* wsProp = FUN_00584050(weaponSys);  // GetWeaponSystemProperty

    // Step 1: HashBaseSubsystem (7 floats + 4 booleans + children + powered extra)
    float baseHash = HashBaseSubsystem(weaponSys);
    HashFoldFloat(baseHash, &hash);

    // Step 2: 2 weapon-system boolean sentinels
    bool wsEnabled = *(uint8_t*)(wsProp + 0x50);
    HashFoldFloat(wsEnabled ? 0.4f : 99.1f, &hash);
    bool wsOnline = *(uint8_t*)(wsProp + 0x51);
    HashFoldFloat(wsOnline ? 32.6f : 487.1f, &hash);

    // Step 3: Hash each weapon child via HashIndividualWeapon
    int childCount = *(int*)(weaponSys + 0x1C);
    for (int i = 0; i < childCount; i++) {
        ShipSubsystem* child = FUN_0056c570(weaponSys, i);
        EnergyWeapon* weapon = FUN_00583200(child);   // CastToWeapon, type 0x802A
        float weapHash = HashIndividualWeapon(weapon);
        HashFoldFloat(weapHash, &hash);
    }

    // Step 4: Torpedo data (gated behind type check 0x801E)
    TorpedoSystem* torpSys = FUN_0057aff0(weaponSys);  // CastToTorpedoSystem
    if (torpSys != NULL) {
        TorpedoSystemProperty* torpProp = torpSys->property;
        int numTypes = *(int*)(torpProp + 0xA4);

        for (int t = 0; t < numTypes; t++) {
            // Hash maxTorpedoes
            int maxTorps = FUN_006944d0(torpProp, t);  // GetMaxTorpedoes
            HashFoldFloat((float)maxTorps, &hash);

            // Torpedo script name - mirror convolution
            char* torpName = FUN_006944e0(torpProp, t);  // GetTorpedoScript
            int nameLen = strlen(torpName);
            for (int j = 0; j < nameLen; j++) {
                int val = (int)torpName[j] * (int)torpName[nameLen - 1 - j];
                HashFoldFloat((float)val, &hash);
            }

            // Torpedo type object name - mirror convolution
            TorpedoType* torpType = FUN_006944c0(torpProp, t);
            char* typeName = FUN_00694330(torpType);  // GetName via Python
            int typeLen = strlen(typeName);
            for (int j = 0; j < typeLen; j++) {
                int val = (int)typeName[j] * (int)typeName[typeLen - 1 - j];
                HashFoldFloat((float)val, &hash);
            }

            // Two int fields product — Clar-2: each int is cast to float SEPARATELY then multiplied
            HashFoldFloat((float)torpType->field_0x08 * (float)torpType->field_0x00, &hash);
        }
    }

    return hash;
}
```

### Clar-2 — Torpedo int product fold (precision detail)

The pre-v5 pseudocode at this line read:

```c
HashFoldFloat((float)(torpType->field_0x08 * torpType->field_0x00), &hash);
```

Binary truth: each int is cast to float **separately** and the multiplication is performed in float, not int. The body decompile is `FUN_005b6c10((float)local_4[2] * (float)*local_4, ...)`. For small int values typical of torpedo metadata the result is the same, but on overflow the float-multiply path differs in precision. The corrected pseudocode above uses the binary-faithful form.

### Torpedo Mirror Convolution

For a string `"ABCD"` (length 4), the hash contributions are:

- `A * D`, `B * C`, `C * B`, `D * A`

Each character is multiplied by its mirror-position character. This makes the hash palindrome-sensitive. Two strings are hashed per torpedo type: the script name and the type object name.

Only subsystems that pass the 0x801E type cast (actual torpedo systems) contribute torpedo data. Phaser, Pulse, and Tractor systems skip step 4 entirely.

---

## HashIndividualWeapon (0x005b6560)

Each individual weapon child is first hashed with `HashBaseSubsystem`, then checked against 5 type IDs. A weapon can match multiple types due to class inheritance (e.g., a phaser bank matches both 0x802B EnergyWeapon and 0x802C PhaserBank).

### Type 0x802B: EnergyWeapon (CT_ENERGY_WEAPON)

Cast via `FUN_0056f8a0`. Hashes 7 weapon property floats:

| Property Offset | Field | Getter |
|-----------------|-------|--------|
| prop+0x54 | maxDamagePerShot | FUN_00583260 |
| prop+0x68 | maxCharge | FUN_0056f900 |
| prop+0x78 | maxDamage | FUN_0056f930 |
| prop+0x7C | maxDamageDistance | FUN_0056f940 |
| prop+0x74 | rechargeRate | FUN_0056f910 |
| prop+0x70 | dischargeRate | FUN_0056f8f0 |
| prop+0x6C | minDamageRange | FUN_0056f8e0 |

### Type 0x802C: PhaserBank (CT_PHASER_BANK)

Cast via `FUN_00570b20`. Hashes:

- 2 firing arc direction vectors (6 floats via `FUN_004e74e0`, `FUN_004e7510`)
- 6 property floats: prop+0x140, 0x144, 0xA0, 0x9C, 0x98, 0x94

### Type 0x802D: PulseWeapon (CT_PULSE_WEAPON)

Cast via `FUN_00574f00`. Hashes:

- 3 vectors — position + 2 directions (9 floats via `FUN_00484a20`, `FUN_00575d50`, `FUN_00575d80`)
- 5 property floats: prop+0xA0, 0x9C, 0x98, 0x94, 0xC8
- Weapon name string mirror convolution: `sum += name[j] * name[len-1-j]`, folded as a single float

### Type 0x802E: TractorBeamProjector (CT_TRACTOR_BEAM_PROJECTOR)

Cast via `FUN_0057ea60`. Hashes:

- 3 vectors (9 floats via `FUN_0057ead0`, `FUN_0057eb30`, `FUN_0057f530`)
- 4 property floats: prop+0xA0, 0x9C, 0x98, 0x94

### Type 0x802F: TorpedoTube (CT_TORPEDO_TUBE)

Cast via `FUN_0057c480`. Hashes:

- 2 firing direction vectors (6 floats at prop+0x6C..0x80 via `FUN_0057c370`, `FUN_0057c3d0`)
- 3 fields: prop+0x84, prop+0x88, and `(float)*(int*)(prop+0x8C)` (int cast to float)

---

## Boolean Sentinel Magic Constants

[v5-validated 2026-05-28]

Boolean flags are hashed as arbitrary float constants rather than 0/1, making the hash sensitive to boolean state changes. All 6 byte-exact pairs confirmed against the binary this pass.

### HashBaseSubsystem (4 pairs)

| # | Source | True Constant | True Hex | False Constant | False Hex | Meaning |
|---|--------|---------------|----------|----------------|-----------|---------|
| 1 | property+0x24 | 64.0002f | 0x42800083 | 76.6f | 0x42993333 | Disableable |
| 2 | subsys+0x44 | 98.6f | 0x42c53333 | 100.0f | 0x42c80000 | Operational state |
| 3 | property+0x25 | 14.3f | 0x4164cccd | 456.1f | 0x43e40ccd | Repairable |
| 4 | property+0x26 | 27.3f | 0x41da6666 | 16.1f | 0x4180cccd | Primary flag |

### HashWeaponSystem (2 pairs)

| # | Source | True Constant | True Hex | False Constant | False Hex | Meaning |
|---|--------|---------------|----------|----------------|-----------|---------|
| 5 | wsProp+0x50 | 0.4f | 0x3ecccccd | 99.1f | 0x42c63333 | WS enabled |
| 6 | wsProp+0x51 | 32.6f | 0x42026666 | 487.1f | 0x43f38ccd | WS online |

---

## Sender (0x005b17f0)

[v5-validated 2026-05-28]

Inside the StateUpdate writer, within the flag 0x01 (POSITION_ABSOLUTE) block. Disasm anchor `0x005b1d96..0x005b1dc1`:

```
005b1d96  TEST BL,BL                  ; BL = bVar19 (set at 005b1906 when CL=DAT_0097fa8a is 0)
005b1d98  JZ   0x005b1dc3             ; if BL=0 (MP), branch to push 0
005b1d9a  PUSH 0x1                    ; has_hash = 1 (SP branch)
005b1d9c  CALL 0x006cf770             ; WriteBit
005b1da5  LEA  ECX,[ESI + 0x27c]      ; container = ship+0x27C
005b1dab  CALL 0x005b5eb0             ; ComputeSubsystemIntegrityHash, __fastcall via ECX
005b1db0  MOV  EDX,EAX
005b1db6  SAR  EDX,0x10               ; EDX = hash >> 16 (signed - Clar-4)
005b1db9  XOR  EAX,EDX                ; low 16 bits = (low 16) XOR (high 16)
005b1dbb  PUSH EAX
005b1dbc  CALL 0x006cf7f0             ; WriteShort (low 16 bits only)
005b1dc3  PUSH 0x0                    ; MP branch: has_hash = 0
005b1dc5  CALL 0x006cf770             ; WriteBit
```

Equivalent C:

```c
bVar19 = DAT_0097fa8a == '\0';   // bVar19 = !isMultiplayer

// ... within flag 0x01 processing:
if (bVar19) {     // NOT multiplayer (single-player only)
    WriteBit(stream, 1);                           // has_subsystem_hash = 1
    hash = ComputeSubsystemIntegrityHash(ship + 0x27C);  // __fastcall via ECX
    WriteShort(stream, (hash >> 16) ^ (hash & 0xFFFF));  // 32->16 bit XOR fold
} else {          // IS multiplayer
    WriteBit(stream, 0);                           // has_subsystem_hash = 0
}
```

**The hash is ONLY written when `isMultiplayer == 0` (single-player mode)**. In multiplayer, `has_subsystem_hash` is always 0.

### Clar-4 — SAR is signed; wire-identical to unsigned shift

The binary uses `SAR EDX, 0x10` (signed shift right) on EDX after copying EAX. Only the low 16 bits are written by `WriteShort` at `0x006cf7f0`, so any sign-extended bits in the high 16 are truncated off the wire. The pseudocode `(hash >> 16)` reading as unsigned is wire-identical. This is a pedantic note for re-implementers using a signed `int32` hash type: the SAR produces sign-extension into the high 16 bits before the XOR, but the XOR result's low 16 are unaffected.

---

## Receiver (0x005b21c0)

[v5-validated 2026-05-28]

Inside the StateUpdate reader, within the flag 0x01 (POSITION_ABSOLUTE) block. Disasm anchor for the kick path `0x005b22ff..0x005b232c`:

```
005b2311  MOV  dword ptr [EDI + 0x10], 0x8000f6    ; event_type = ET_BOOT_PLAYER (immediate 32-bit)
005b2318  CALL 0x006d62b0                          ; set event src/dest (TGEvent::SetSrcDest)
005b231d  MOV  EAX, dword ptr [ESI + 0x2e4]        ; this->playerSlot
005b2323  PUSH EDI                                  ; push event
005b2324  MOV  ECX, 0x97f838                        ; ECX = &DAT_0097f838 (TGEventManager singleton)
005b2329  MOV  dword ptr [EDI + 0x28], EAX         ; event+0x28 = playerSlot
005b232c  CALL 0x006da2a0                          ; TGEventManager__PostEvent
```

Equivalent C:

```c
uint8_t hasHash = ReadByte(stream);
if (hasHash != 0) {
    uint16_t receivedHash = ReadShort(stream);

    if (isMultiplayer) {  // DAT_0097fa8a != 0
        uint32_t localHash = ComputeSubsystemIntegrityHash((int)this + 0x27C);
        uint16_t localWire = (uint16_t)(localHash >> 16) ^ (uint16_t)(localHash & 0xFFFF);

        if (localWire != receivedHash) {
            // CHEAT DETECTED - post ET_BOOT_PLAYER event
            void* mpWindow = FUN_0050e1b0(DAT_009878cc, 8);
            void* mpGame   = FUN_00504360(mpWindow);
            void* eventMem = FUN_00717b70(0x2C);                  // TGAlloc 44 bytes
            void* eventObj = FUN_00718010(eventMem);              // TGAlloc ctor
            TGEvent* event = FUN_006bb840(eventObj);              // TGEvent ctor
            *(uint32_t*)((char*)event + 0x10) = 0x008000F6;       // event_type at +0x10  (Clar-1, Clar-3)
            FUN_006d62b0(event, (int)mpGame);                     // SetSrcDest
            *(int*)((char*)event + 0x28) = this->net_player_id;   // *(this + 0x2E4) — NetPlayerID
                                                                  // [v5-clarification 2026-05-29:
                                                                  //  ship+0x2E4 is the owning player's
                                                                  //  NetPlayerID per gamemode-system-
                                                                  //  validation memo; was labeled
                                                                  //  "playerSlot" — close synonym but
                                                                  //  semantically the NetID, not slot
                                                                  //  index, on the wire.]
            FUN_006da2a0(&DAT_0097f838, event);                   // PostEvent (TGEventManager singleton)
        }
    }
}
```

### Clar-1 — Receiver writes event_type at `event+0x10`

The pre-v5 pseudocode wrote `event->eventType = 0x8000F6;` without specifying the byte offset. Binary truth: the MOV at `0x005b2311` is `MOV dword ptr [EDI + 0x10], 0x008000F6` — the event-type lives at `event+0x10` and is written as an immediate 32-bit constant. The pseudocode above reflects this explicitly.

### Clar-3 — `&ET_BOOT_PLAYER` and `0x008000F6` are the same address constant

Ghidra's decompile renders the MOV as `*(undefined **)(iHashBit + 0x10) = &ET_BOOT_PLAYER;` (a symbolic-pointer write). The actual instruction is `MOV dword ptr [EDI + 0x10], 0x008000F6` — an immediate-constant write. Both are bytewise identical at runtime because **the address of the `ET_BOOT_PLAYER` symbol IS the event-type ID** — Bridge Commander uses the address of a label as the unique event-type key, not a pointer to a value at that address. The pseudocode using `0x008000F6` directly is more accurate to the bytes; Ghidra's symbolic form is a naming artifact.

### Receiver event posting bypasses TGFactory

The mismatch path allocates the event via the raw TGEvent ctor chain (`TGAlloc 0x2C` → `FUN_00718010` → `FUN_006bb840` → `FUN_006d62b0` → `FUN_006da2a0`), not via `TGFactory_DeserializeObject` (0x006d6200). This is a **send-side event posting** (command-style), not a wire-side deserialization. Same pattern as the leaf #18 triad ([`objnotfound-requestobj-enterset-wire-format.md`](objnotfound-requestobj-enterset-wire-format.md)): command/control messages bypass TGFactory because they are RPC-style operations, not event-bearing transports.

---

## Wire Encoding

[v5-validated 2026-05-28]

The 32-bit hash is XOR-folded to 16 bits:

```c
uint16_t wire_hash = (uint16_t)(hash32 >> 16) ^ (uint16_t)(hash32 & 0xFFFF);
```

Carried in the StateUpdate packet after position data, gated behind flag 0x01 (POSITION_ABSOLUTE):

```
[position data] [has_hash: bit] [if has_hash != 0: hash16: ushort]
```

### Container aliasing pattern

`ship+0x27C` is a sub-object created by `FUN_005b5d00` with vtable `0x008944c8`. The ctor zero-fills `param_1[1..0x18]` — exactly the range `ship+0x280..ship+0x2DC` that overlaps the named-slot table at `ship+0x2B0..0x2DC`. After `Ship__SetupProperties` populates the named slots, the hash function reads those same pointers through the container alias. This explains why the doc's container offsets (+0x34..+0x60) and ship offsets (+0x2B0..+0x2DC) are consistent — they refer to the same memory through two aliases.

---

## Kick Path

[v5-validated 2026-05-28]

```
StateUpdate receiver detects hash mismatch
    -> PostEvent(ET_BOOT_PLAYER = 0x008000F6, playerSlot)
        -> TGEventManager singleton at DAT_0097f838 dispatches
            -> MultiplayerWindow_BootPlayerHandler at 0x00506170
                -> reads DAT_0097fa8a (IsMultiplayer gate)
                -> TGAlloc 0x44 bytes (TGBootPlayerMessage)
                -> sets [ESI+0x40] = 0x4 at 0x005061CD  (reason=4 = BOOT_REASON_INTEGRITY)
                -> broadcast TGBootPlayerMessage
                -> client receives, disconnects
```

`MultiplayerWindow_BootPlayerHandler` was **undefined in Ghidra DB before this pass** — created via `create_function` at 0x00506170, plate added. Cross-confirmed by `reference/decompiled/04_ui_windows.c` line 2027 which registers this address against the string `"MultiplayerWindow__BootPlayerHandler"` keyed on `&DAT_008000f6`.

---

## Dead Code Proof

| Mode | Sender writes hash? | Receiver checks hash? | Outcome |
|------|---------------------|-----------------------|---------|
| Single-player | YES (has_hash=1, hash16 follows) | NO (isMultiplayer is false) | Hash sent but ignored |
| Multiplayer | NO (has_hash=0) | YES (would check if has_hash were 1) | Check never reached |

The sender and receiver conditions are mutually exclusive. The subsystem integrity hash has **never been functional in any stock multiplayer session**.

This confirms that `PatchSubsystemHashCheck` at `0x005b22b5` (the binary patch in `src/proxy/ddraw_main/binary_patches_and_python_bridge.inc.c` that prevents false-positive kicks when the dedicated server has no ship subsystems) is safe — stock gameplay already never triggers this code path.

---

## Function Addresses

[v5-validated 2026-05-28]

| Address | Name | Notes |
|---------|------|-------|
| 0x005b5eb0 | `ComputeSubsystemIntegrityHash` | 12-slot iterator; renamed + plated this pass |
| 0x005b6170 | `HashBaseSubsystem` | 7+N+4+powered; renamed + plated this pass |
| 0x005b6330 | `HashWeaponSystem` | base + 2 ws-sentinels + children + torpedo; renamed + plated this pass |
| 0x005b6560 | `HashIndividualWeapon` | 5-way type dispatch; renamed this pass (no plate yet — see OQ-2) |
| 0x005b6c10 | `HashFoldFloat` | abs-ftol + XOR + ROL; renamed + plated this pass |
| 0x005b5d00 | `ShipSubsystemContainer_Ctor` | Container sub-object ctor; vtable 0x008944c8 |
| 0x005b17f0 | `Ship__WriteStateUpdate` | Sender; bVar19 SP gate |
| 0x005b21c0 | `Ship__ReadStateUpdate` | Receiver; isMultiplayer gate |
| 0x005b22b5 | `PatchSubsystemHashCheck` | Binary patch site (proxy) |
| 0x00506170 | `MultiplayerWindow_BootPlayerHandler` | Kick path target; **CREATED this pass** |

### Data anchors

| Address | Symbol | Value / Description |
|---------|--------|---------------------|
| 0x008944c8 | Container vtable | Used by `ShipSubsystemContainer_Ctor` |
| 0x008000F6 | `ET_BOOT_PLAYER` | Event-type ID (the address IS the constant — Clar-3) |
| 0x0097fa8a | `IsMultiplayer` (byte) | Engine cross-anchor (CLAUDE.md Key Globals) |
| 0x0097f838 | `TGEventManager` singleton | Engine cross-anchor; also cited by `pythonevent-wire-format.md` |
| 0x009878cc | `MultiplayerWindow` singleton | Used by receiver to walk to mpGame |

---

## Decompiled Source Reference

All analysis performed against `reference/decompiled/05_game_mission.c`:

| Function | Decompiled Line |
|----------|-----------------|
| `ComputeSubsystemIntegrityHash` (0x005b5eb0) | ~56151 |
| `HashBaseSubsystem` (0x005b6170) | ~56253 |
| `HashWeaponSystem` (0x005b6330) | ~56321 |
| `HashIndividualWeapon` (0x005b6560) | ~56431 |
| `HashFoldFloat` (0x005b6c10) | ~56617 |
| `Ship__WriteStateUpdate` (0x005b17f0) | ~53987 |
| `Ship__ReadStateUpdate` (0x005b21c0) | ~53747 |

> [!NOTE]
> The reference/decompiled/05_game_mission.c file has not been re-generated since the 2026-05-28 Ghidra import. Line numbers above are from the prior corpus and may drift. OQ-4 below tracks the re-verification.

---

## Open Questions

- **OQ-1** — Slot 8 (`+0x60 / ship+0x2DC` = CloakDevice per foundation #1): the doc previously labeled this slot `Crew / Unknown-A` and noted "calls `FUN_0055e220` (side-effect getter)". If the actual subsystem at +0x2DC is CloakDevice, what is `FUN_0055e220` reading? Hypothesis: cloak-state side-effect (e.g., `cloak->Refresh` / `cloak->UpdateState`). Needs `FUN_0055e220` decompile to confirm.
- **OQ-2** — Slot 7 (`+0x5C / ship+0x2D8` = RepairSubsystem per foundation #1): the doc previously labeled this slot "Warp Drive" with `prop+0x4C` extra via `FUN_00564fe0`. If it is actually RepairSubsystem, what is `prop+0x4C` on RepairSubsystem? Hypothesis: repair team count or queue length. `FUN_00564fe0` decompile would confirm. (Also covers `HashIndividualWeapon`'s 5-way type dispatch — the per-type property reads were not byte-checked this pass.)
- **OQ-3** — Slot 6 (`+0x54 / ship+0x2D0` = WarpEngineSubsystem per foundation #1): the doc's `HashBaseSubsystem | none` matches the engine-pair asymmetry pattern (Impulse at slot 5 has 4 extras via `FUN_00560fc0`; Warp at slot 6 has none). Confirm via `FUN_00560fc0` decompile vs no-helper for WarpEngine.
- **OQ-4** — Decompiled-source line numbers (table above). The `reference/decompiled/05_game_mission.c` file has not been re-generated since the 2026-05-28 import. Verify the cited line numbers still resolve to the expected functions; if not, update or drop the table.

---

## Related Documents

- [`wire-format-spec.md`](wire-format-spec.md) — Hub: summary opcode tables and the canonical **Named Slot Layout** at ship+0x2B0..+0x2DC. Authority for the C1 slot-identity corrections (v5-validated 2026-05-28).
- [`stateupdate.md`](stateupdate.md) — Opcode 0x1C: dirty flags + 8 field formats. Hash bit lives in the flag 0x01 (POSITION_ABSOLUTE) block; sender's `bVar19 = !isMultiplayer` gate identity confirmed in mid #8.
- [`stateupdate-subsystem-wire-format.md`](stateupdate-subsystem-wire-format.md) — Subsystem linked-list order + WriteState formats; sibling for ship+0x2C0..+0x2DC.
- [`per-ship-subsystem-wire-format.md`](per-ship-subsystem-wire-format.md) — Per-ship subsystem catalogs (16 stock ships) — uses the same corrected slot identities.
- [`objnotfound-requestobj-enterset-wire-format.md`](objnotfound-requestobj-enterset-wire-format.md) — Sibling leaf documenting the **command-message-bypasses-TGFactory** pattern; the receiver's `PostEvent` chain here follows the same pattern.
- [`docs/engine/rtti-class-catalog.md`](../engine/rtti-class-catalog.md) — Canonical class-ID mappings (CT_SHIELD_PROPERTY 0x8137, CT_SENSOR 0x8139, etc.) used in the corrected slot table. Note: 0x8138 is **PowerProperty** (script-facing property class), not a HullSubsystem identity — see [`docs/gameplay/power-system.md`](../gameplay/power-system.md) C1 for the cascade that disambiguates the PowerProperty (0x8138) / PowerSubsystem-instance (0x8027) namespaces.
- [`docs/gameplay/power-system.md`](../gameplay/power-system.md) — Authority for the slot 1 (+0x2C4) cascade: PowerSubsystem reactor instance class ID 0x8027 vs PowerProperty class ID 0x8138 disambiguation.
- [`v5-validation-status.md`](v5-validation-status.md) — Protocol-family campaign tracker; this leaf is row #19. See §6.19 for the validation log entry.
