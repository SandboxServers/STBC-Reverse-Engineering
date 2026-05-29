> [docs](../README.md) / [gameplay](README.md) / hull-subsystem.md

---
title: HullSubsystem (ship+0x2C4) — RE Analysis
type: reference + explanation
audience: re-engineer
validated: 2026-05-28
methodology: FUNCTION_DOC_WORKFLOW_V5
binary:
  name: stbc.exe
  size: 6182400
  base: 0x00400000
status: verified
evidence:
  - claim: "HullSubsystem instance lives at ship+0x2C4 (slot 1 of the ship subsystem named-slot table); set by Ship__SetupProperties case 0x8138 (CT_HULL_PROPERTY)"
    address: 0x005B3FB0
    function: Ship__SetupProperties
    completeness: 28.2
    effective: 41.4
    confidence: high
    note: "Case 0x8138 allocates 0x88 bytes, calls HullSubsystem_Ctor (currently mis-symbolised PowerSubsystem_Ctor at 0x00560470), writes pointer into param_1+0x2C4. Cross-anchor: subsystem-integrity-hash.md slot 1 + wire-format-spec.md Named Slot Layout."
  - claim: "Class identity 0x8027 — definitive proof via vtable 0x00892C98 owning the literal strings 'HullClass', '_p_HullClass', 'HullClassPtr' at 0x008E4EC0 / 0x008E4ECC / 0x008E4EDC"
    address: 0x00892C98
    function: null
    confidence: high
    note: "GetTypeID at 0x00560490 byte-confirmed: `B8 27 80 00 00 C3` (MOV EAX, 0x8027 ; RET). Vtable slots 9/10/11 (GetClassName trio) return the three HullClass-prefixed strings via SWIG class-name convention."
  - claim: "Instance alloc size 0x88 bytes (136) — matches ShipSubsystem base exactly; HullSubsystem adds NO extension fields"
    address: 0x005B3FB0
    function: Ship__SetupProperties
    confidence: high
    note: "`PUSH 0x88` before allocator call in case 0x8138. ShipSubsystem base layout from FUN_0056B970 ctor accounts for the entire 0x88 byte range."
  - claim: "IsA chain: 0x8027 -> 0x801B (ShipSubsystem) -> 0x102 (DamageableObject)"
    address: 0x005604A0
    function: HullSubsystem__IsA
    confidence: high
    note: "Disasm 0x005604A0..0x005604BC enumerates the 3-step type-ID chain with CMP/JE cascade. Does NOT inherit PoweredSubsystem (Hull is unpowered)."
  - claim: "HullSubsystem_Ctor at 0x00560470 sets vtable 0x00892C98 only; calls ShipSubsystem base ctor (FUN_0056B970); no additional field init"
    address: 0x00560470
    function: HullSubsystem_Ctor
    completeness: 12.5
    effective: 28.6
    confidence: high
    note: "Currently mis-symbolised in Ghidra DB as `PowerSubsystem_Ctor` — the real PowerSubsystem reactor ctor is `PoweredMaster_Ctor` at 0x00563530 (vtable PTR_FUN_0088A1F0). Body of 0x00560470: parent call -> `*param_1 = 0x00892C98`. That's it."
  - claim: "Vtable 0x00892C98 inherits WriteState from ShipSubsystem base — slot +0x70 = 0x0056D320 (ShipSubsystem::WriteState)"
    address: 0x00892D08
    function: ShipSubsystem__WriteState
    confidence: high
    note: "Vtable slot +0x70 at offset 0x00892D08 holds the function pointer 0x0056D320. HullSubsystem does NOT override WriteState — it uses the base implementation."
  - claim: "Wire format: 1 byte condition only (no children, no powered extras). Per-tick payload size = exactly 1 byte"
    address: 0x0056D320
    function: ShipSubsystem__WriteState
    confidence: high
    note: "condition_byte = ftol((this+0x30 / this+0x34) * 255.0). Hull has childCount=0xFFFF (invalid sentinel from ctor), so the child-recursion loop runs zero iterations. End marker is vtable[+0xD8] (GetPos no-op)."
  - claim: "Hull HP at instance+0x30 mirrors ship+0x14C (DamageableObject HP, FLT_MAX undamaged sentinel per leaf #18) — the exact watcher/mirror function is not located this pass"
    address: 0x0000014C
    function: null
    confidence: medium
    note: "Open question (OQ-1). Cross-anchor: leaf #18 (objnotfound-requestobj-enterset-wire-format.md) documents ship+0x14C as DamageableObject HP slot with FLT_MAX sentinel; the StateUpdate 0x20 wire stream encodes condition byte from instance+0x30. A watcher slot at instance+0x44/+0x48 or a `ProcessDamage` callout is the most likely sync site."
  - claim: "Hull is a pure ShipSubsystem extension — NO new instance fields beyond the base; only overrides are GetTypeID, IsA, GetClassName trio (slots 9/10/11), and GetSwigClass (slot +0x4C)"
    address: 0x00892C98
    function: null
    confidence: high
    note: "Slot-by-slot vtable diff against ShipSubsystem (0x00892FC4): 8 slots OVERRIDE (dtor, GetTypeID, IsA, GetClassName x3, GetSwigClass, plus 2 misc slots +0x78/+0x7C). Remaining 28 slots INHERITED."
  - claim: "Pre-v5 doc attribution history: leaf #19 originally had HullSubsystem (correct), power-system C1 'corrected' to PowerSubsystem (Reactor) (wrong), and the cascade-patch propagated the error. This validation pass definitively reverts to HullSubsystem via byte-confirmed vtable strings."
    address: null
    function: null
    confidence: high
    note: "Meta-cascade: see source memo `.claude/agent-memory/game-archaeology-specialist/sensor-hull-subsystem-validation-20260528.md`. The 0x8027 class ID is HullSubsystem (proved by string 'HullClass'); 0x8138 is PowerProperty (script-facing property class returned by getter wrappers); PowerSubsystem reactor (PoweredMaster, class 0x813E) lives at ship+0x2B0 via PoweredMaster_Ctor 0x00563530 with vtable PTR_FUN_0088A1F0."
  - claim: "Hull is in the ship+0x284 round-robin subsystem list; the StateUpdate flag 0x20 sequencer will visit Hull's slot and emit its 1-byte condition byte"
    address: 0x005B17F0
    function: Ship__WriteStateUpdate
    confidence: high
    note: "Cross-anchor: stateupdate-subsystem-wire-format.md (round-robin list at ship+0x284), and per-ship-subsystem-wire-format.md (per-ship subsystem catalog). Sender-side gate confirmed in mid #8 stateupdate.md."
  - claim: "HullSubsystem has NO dedicated per-tick Update method; HP changes flow externally via ProcessDamage -> ship+0x14C -= damage, then the next StateUpdate emits the updated condition byte automatically"
    address: null
    function: null
    confidence: high
    note: "ShipSubsystem family uses event-driven state changes (ShipSubsystem::SetCondition is called from damage handlers and Repair queue, not from a per-frame Update). Hull just rides the StateUpdate round-robin."
companions:
  - docs/gameplay/sensor-subsystem.md
  - docs/gameplay/damage-system.md
  - docs/gameplay/power-system.md
  - docs/protocol/subsystem-integrity-hash.md
  - docs/protocol/stateupdate-subsystem-wire-format.md
  - docs/engine/rtti-class-catalog.md
supersedes: []
---

# HullSubsystem (ship+0x2C4) — Reverse Engineering Analysis

> [!NOTE]
> **HullSubsystem at ship+0x2C4** (class 0x8027, NOT PowerSubsystem reactor). Earlier passes mis-attributed this slot — leaf #19 originally had HullSubsystem (correct), `power-system` C1 "corrected" to PowerSubsystem (Reactor) (wrong), and a cascade-patch propagated the error into [docs/protocol/subsystem-integrity-hash.md](../protocol/subsystem-integrity-hash.md). Sensor/hull RE definitively reverted via **byte-confirmed vtable strings "HullClass" / "_p_HullClass" / "HullClassPtr"** owned by vtable 0x00892C98. PowerSubsystem reactor (PoweredMaster, class 0x813E) actually lives at **ship+0x2B0** (a separate slot, ctor at 0x00563530, vtable PTR_FUN_0088A1F0). Hull is a pure ShipSubsystem extension — no new fields beyond base. Wire emits just 1 byte (condition). Hull HP at `instance+0x30` mirrors DamageableObject HP at `ship+0x14C` (FLT_MAX undamaged sentinel per leaf #18). See `.claude/agent-memory/game-archaeology-specialist/sensor-hull-subsystem-validation-20260528.md` for the binary-truth evidence packet.

---

## Overview

HullSubsystem is the simplest ship subsystem in Bridge Commander. It exists primarily as a typed handle so the engine can:

1. Receive the `CT_HULL_PROPERTY` (hull metadata: ship class definition, fHullFactor, fHullSelectedChooseAlternate, HullProperty floats) and bind it as a `ShipSubsystem` property at `instance+0x3C`.
2. Participate in the round-robin subsystem list at `ship+0x284` — emitting its 1-byte hull-condition byte in each StateUpdate (flag 0x20).
3. Provide the per-ship identity `"HullClass"` for SWIG-script reflection (Python code can grab the hull and read its HP without touching the DamageableObject base directly).

There is no Hull-specific logic. There is no Hull subsystem method that does anything other than self-identification, save/load, and wire serialization. The hull's actual HP lives at the DamageableObject layer (`ship+0x14C`) and is consumed/modified by `ProcessDamage`, `Repair`, and `Explosion` cascades. HullSubsystem just mirrors that HP into `instance+0x30` for round-robin StateUpdate participation.

---

## Class Identity & Meta-Cascade History

[v5-validated 2026-05-28]

### Definitive proof via vtable strings

| Attribute | Value | Evidence |
|---|---|---|
| Class name | `HullClass` (Totally Games' nomenclature) | vtable slot 9 returns string "HullClass" at 0x008E4EC0 |
| Class ID | `0x8027` | GetTypeID at 0x00560490 byte-confirmed: `B8 27 80 00 00 C3` |
| IsA chain | 0x8027 -> 0x801B (ShipSubsystem) -> 0x102 (DamageableObject) | IsA disasm 0x005604A0..0x005604BC |
| vtable | `0x00892C98` | Owns class-name strings "HullClass" / "_p_HullClass" / "HullClassPtr" at 0x008E4EC0 / EC / EDC |
| Property type | `0x8138` (CT_HULL_PROPERTY) | Ship__SetupProperties case 0x8138 |
| Instance alloc size | `0x88` bytes (136) | `PUSH 0x88` before allocator call in case 0x8138 |
| Ship slot | `ship+0x2C4` | Ship__SetupProperties writes the new instance pointer there |

The three SWIG class-name strings owned by vtable slots 9/10/11 — "HullClass", "_p_HullClass", "HullClassPtr" — are the binary-truth tiebreaker. They prove that vtable 0x00892C98 (and therefore the instance at ship+0x2C4 constructed by ctor 0x00560470) is HullSubsystem and NOT PowerSubsystem.

### Meta-cascade history

This slot's identity has been re-attributed multiple times in the v5 campaign. Setting the record straight:

| Round | Source | Verdict | Status |
|---|---|---|---|
| Pre-v5 | Original docs | "Power Reactor" at ship+0x2C4 | Stale — derived from outdated label |
| v5 leaf #19 (early) | subsystem-integrity-hash.md initial validation | **HullSubsystem 0x8138** at ship+0x2C4 | Half-right (slot was Hull, but ID was wrong) |
| v5 power-system C1 cascade | docs/gameplay/power-system.md | "Cascade-correct to PowerSubsystem (Reactor) 0x8027" | **WRONG** — conflated the property class ID (0x8138) with subsystem instance class IDs |
| v5 sensor/hull validation (this pass) | source memo 2026-05-28 | **HullSubsystem class 0x8027** at ship+0x2C4 | Definitive via vtable strings |

The confusion stemmed from two facts being treated as if they referred to the same class:

- **0x8138** = `CT_HULL_PROPERTY` (PROPERTY class ID — the script-facing property type returned by SWIG getter wrappers).
- **0x8027** = HullSubsystem (instance class ID — the actual class of the runtime subsystem object at ship+0x2C4).

The power-system C1 cascade conflated the property-ID and instance-ID namespaces, propagating a wrong identity into [docs/protocol/subsystem-integrity-hash.md](../protocol/subsystem-integrity-hash.md). The hash function itself was always reading the correct memory — only the human-readable identity column in the slot table was wrong.

PowerSubsystem reactor (`PoweredMaster`, class 0x813E) actually lives at **ship+0x2B0** in a different slot, constructed by `PoweredMaster_Ctor` at 0x00563530 with vtable `PTR_FUN_0088A1F0` (set by Ship__SetupProperties case 0x813E / CT_POWERED_SUBSYSTEM_PROPERTY).

### Ctor — currently mis-symbolised in Ghidra DB

The HullSubsystem ctor lives at **0x00560470** but is currently named `PowerSubsystem_Ctor` in the Ghidra DB — a historical misname that should be reverted. Diagnostic shape of the function body:

- Calls `FUN_0056B970` (ShipSubsystem base ctor)
- Sets `*param_1 = 0x00892C98` (vtable assign)
- That is the entire body. No field zeroing, no power-mode init, no state-machine.

This minimality is what tipped off the validation: if 0x00560470 were really PowerSubsystem_Ctor, it would zero PoweredSubsystem fields and set powerMode = 2 (like `SensorSubsystem_Ctor` at 0x00566D10 does). It does not. It just sets the vtable. That is HullSubsystem behavior.

---

## Field Layout (instance, 0x88 bytes)

[v5-validated 2026-05-28]

HullSubsystem adds **zero new fields** beyond the ShipSubsystem base. Layout (inherited from `FUN_0056B970`):

| Offset | Field | Notes |
|---|---|---|
| +0x00 | vtable ptr = 0x00892C98 | (ctor) |
| +0x04..+0x1C | Inherited TGObject / DamageableObject base | |
| +0x14 | childCount | uint16; init = 0xFFFF (invalid sentinel — Hull has no children) |
| +0x18 | parent ptr | NULL init |
| +0x20 | childArrayPtr | NULL init |
| +0x2A | childCapacity | uint16; init = 0xFFFF |
| +0x2C | childArrayBound | uint16; init = 0xFFFF |
| **+0x30** | **currentCondition (HP)** | float; init = 1.0 — **mirror of ship+0x14C** |
| **+0x34** | **maxCondition** | float; init = 1.0 |
| +0x38 | conditionPct (derived) | float; init = 1.0 |
| +0x3C | propertyPtr | (set by `SetProperty`) |
| +0x40 | misc float | init = 0 |
| +0x44 | bool flag1 | byte; init = 0 |
| +0x45 | bool flag2 | byte; init = 0 |
| +0x48 | randPhase | float = `rand() * 0x00892FC0` |
| +0x4C | randSeedFloat | float = randPhase * 0x00888DBC |
| +0x64 | pad uint32 | = 0 |
| +0x68 | small epsilon | uint32 = 0x3A83126F (= 1e-3f) |
| +0x6C | childSubsystemList head | = 0 init |
| +0x70 | sceneAttachPtr | = 0 init |
| +0x78..+0x7C | DAT_0098039C float[5] watchers | 5 timer/state slots |
| +0x84 | lastReadStateTime | float; init = DAT_009A2880 |
| +0x88 | end of instance | HullSubsystem has NO extension fields |

The alloc size `0x88` (136) matches the ShipSubsystem base layout + vtable slot exactly. There is no space for Hull-specific data because the engine doesn't need any.

---

## Wire Format (StateUpdate flag 0x20)

[v5-validated 2026-05-28]

HullSubsystem emits via **`ShipSubsystem::WriteState`** (vtable slot `+0x70` = `0x0056D320`):

```
+0    1 byte    condition_byte = ftol((current_condition / max_condition) * 255.0)
                Hull's HP byte (0..255, derived from instance+0x30 / instance+0x34)
```

That is the entire payload. Per-tick HullSubsystem encoding in StateUpdate flag 0x20 is **exactly 1 byte** — the simplest subsystem on the wire.

Why so simple:

- Hull has `childCount = 0xFFFF` (invalid sentinel from the ctor) — so the child-recursion loop in `WriteState` runs zero iterations.
- Hull is NOT a PoweredSubsystem — there is no `hasPowerData` bit, no powerPctWanted byte to follow.
- Hull has no per-instance state fields that need replication. HP is the only thing clients care about.
- The end marker (vtable[+0xD8] GetPos no-op) emits nothing for Hull because Hull inherits the no-op from ShipSubsystem base.

In a typical StateUpdate stream (3+ subsystems per tick within the 10-byte budget), HullSubsystem appears as a single byte at its round-robin position.

---

## Hull HP Sync

[v5-validated 2026-05-28]

Two HP slots exist for the ship's hull:

| Slot | Type | Authority | Used For |
|---|---|---|---|
| `ship+0x14C` | DamageableObject base float | **Authoritative** — `ProcessDamage` / `Repair` write here directly | The "real" hull HP; FLT_MAX undamaged sentinel per leaf #18 |
| `HullSubsystem instance+0x30` | ShipSubsystem currentCondition float | Mirror — encoded into the StateUpdate condition byte | What clients see on the wire (after `ftol(./max * 255)`) |

These two values are kept in sync, but the **exact sync mechanism is not located this pass** (see Open Question 1). The most likely candidates:

1. A watcher registration at `HullSubsystem instance+0x44` / `+0x48` / `+0x78..+0x84` (the `DAT_0098039C[5]` block inherited from ShipSubsystem) wires up a mirror callback that fires when `ship+0x14C` changes.
2. A direct callout inside `ProcessDamage` (damage-system.md) that, after writing `ship+0x14C`, also writes `HullSubsystem instance+0x30` via the named-slot pointer at `ship+0x2C4`.

For practical OpenBC purposes either mechanism works — write the new HP to BOTH slots before the next StateUpdate tick. Stock binary appears to do this consistently because all stock traces show coherent hull-HP bytes in StateUpdate flag 0x20.

---

## Update Behavior

[v5-validated 2026-05-28]

HullSubsystem has **NO dedicated per-tick Update method**. ShipSubsystem family uses event-driven state changes (no per-frame loop), so HP changes flow externally:

```
ProcessDamage (damage-system.md cascade)
    -> writes to ship+0x14C (DamageableObject HP slot)
        -> syncs to HullSubsystem instance+0x30 via watcher / direct callout
            -> next StateUpdate tick (flag 0x20) encodes the new condition byte

Repair queue (repair-system.md)
    -> writes to ship+0x14C += repair_amount
        -> same sync path
            -> StateUpdate encodes the higher condition byte on the next emit

Explosion handler (ship-death-lifecycle.md)
    -> catastrophic HP zeroing at ship+0x14C
        -> sync sets HullSubsystem instance+0x30 = 0
            -> final StateUpdate emits condition byte = 0
```

Hull is a passive participant in the StateUpdate round-robin — it never schedules its own events, never starts a timer, never decays on its own. It just rides whatever HP value is in `instance+0x30` at the moment the wire encoder visits it.

---

## OpenBC Implications

Server-side OpenBC implementation notes:

- **HullSubsystem MUST appear in the ship+0x284 round-robin subsystem list.** The server's StateUpdate flag 0x20 round-robin will visit Hull's slot and emit `ShipSubsystem::WriteState` — exactly 1 byte (the condition byte).
- **Mirror the authoritative hull HP into the HullSubsystem instance+0x30.** Whichever slot you treat as authoritative (most OpenBC server designs use `ship.hull_hp` at a single location), copy it to the HullSubsystem's currentCondition field before each StateUpdate tick. Otherwise clients will see stale hull HP bytes.
- **No power, no children, no events.** Hull is the simplest subsystem in the catalog. Implementation effort is minimal once the round-robin scheduler is correct.
- **The 1-byte wire format means precision is limited to ~0.4%.** Going from full HP to one-step-down emits a delta of `(max_hp / 255)` on the wire. If your ship's max HP is 100, the smallest visible client-side HP change is ~0.39 HP. Stock binary behavior is identical because both server and client use the same `ftol(./max * 255)` encoding.
- **Integrity hash for Hull (slot 1) reads `HashBaseSubsystem` against the property — dead in MP per leaf #19.** Modded hull stats do not trigger the kick path in stock multiplayer.

---

## Open Questions

- **OQ-1** — Exact watcher/mirror function that syncs `ship+0x14C` -> `HullSubsystem instance+0x30`. The two are clearly kept in sync (stock traces emit consistent hull HP bytes), but the sync site has not been located. Candidates: a watcher slot at instance+0x44/+0x48, or a direct callout inside `ProcessDamage`. Resolving this requires xref-walking everything that writes to `ship+0x14C` and looking for an adjacent write to `*(*(ship + 0x2C4) + 0x30)`.

---

## Related Documents

- [sensor-subsystem.md](sensor-subsystem.md) — Sibling subsystem (ship+0x2C8); has its own field layout and event handlers (Hull is much simpler).
- [damage-system.md](damage-system.md) — `ProcessDamage` cascade; writes to ship+0x14C, which propagates to HullSubsystem instance+0x30.
- [power-system.md](power-system.md) — PowerSubsystem reactor (`PoweredMaster` class 0x813E) at ship+0x2B0; NOT to be confused with HullSubsystem at ship+0x2C4 (the cascade-correction history above documents the prior confusion).
- [docs/protocol/subsystem-integrity-hash.md](../protocol/subsystem-integrity-hash.md) — Slot 1 (`+0x2C4`) hashes Hull via `HashBaseSubsystem`; dead in MP. Carries cross-cascade history notes referencing this doc's identity verdict.
- [docs/protocol/stateupdate-subsystem-wire-format.md](../protocol/stateupdate-subsystem-wire-format.md) — Round-robin subsystem encoding; Hull's 1-byte emit is the simplest case.
- [docs/engine/rtti-class-catalog.md](../engine/rtti-class-catalog.md) — Class IDs 0x8027 (HullSubsystem instance) / 0x8138 (CT_HULL_PROPERTY); the namespace separation that drove the meta-cascade above.
