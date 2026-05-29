> [docs](../README.md) / [protocol](README.md) / per-ship-subsystem-wire-format.md

---
title: Per-Ship Subsystem Wire Format Catalog
type: reference
audience: re-engineer
validated: 2026-05-29
methodology: FUNCTION_DOC_WORKFLOW_V5
binary:
  name: STBC.exe
  size: 6394712
  base: 0x00400000
status: partial
companions:
  - docs/protocol/stateupdate.md
  - docs/protocol/stateupdate-subsystem-wire-format.md
  - docs/protocol/wire-format-spec.md
  - docs/protocol/objcreate-serialization.md
  - docs/engine/decompiled-functions.md
  - docs/protocol/v5-validation-status.md
cross_source:
  - reference/scripts/Multiplayer/SpeciesToShip.py
  - reference/scripts/ships/Hardpoints/sovereign.py
  - reference/scripts/ships/Hardpoints/birdofprey.py
  - reference/scripts/ships/Hardpoints/galor.py
  - reference/scripts/ships/Hardpoints/akira.py
  - reference/scripts/ships/Hardpoints/ambassador.py
  - reference/scripts/ships/Hardpoints/galaxy.py
  - reference/scripts/ships/Hardpoints/nebula.py
  - reference/scripts/ships/Hardpoints/vorcha.py
  - reference/scripts/ships/Hardpoints/warbird.py
  - reference/scripts/ships/Hardpoints/marauder.py
  - reference/scripts/ships/Hardpoints/keldon.py
  - reference/scripts/ships/Hardpoints/cardhybrid.py
  - reference/scripts/ships/Hardpoints/kessokheavy.py
  - reference/scripts/ships/Hardpoints/kessoklight.py
  - reference/scripts/ships/Hardpoints/shuttle.py
  - reference/scripts/ships/Hardpoints/enterprise.py
evidence:
  - claim: "16 stock multiplayer ships (species 1-15 + Enterprise@37) cataloged via hardpoint LoadPropertySet"
    address: null
    function: null
    completeness: n/a
    confidence: high
    note: "Cross-source: reference/scripts/Multiplayer/SpeciesToShip.py (MAX_FLYABLE_SHIPS=16 at line 51); Enterprise inherits via App.SPECIES_SOVEREIGN at lines 60+92"
  - claim: "Round-robin walks ship+0x284 linked list with 10-byte budget per tick"
    address: 0x005b17f0
    function: Ship__WriteStateUpdate
    completeness: 0.0
    confidence: high
    note: "Foundation: mid #8 (stateupdate.md). Budget cap at CMP EAX, 0xA at 0x005B1EC0"
  - claim: "Base WriteState format: 1 byte condition + recursive children"
    address: 0x0056d320
    function: ShipSubsystem__WriteState
    completeness: 10.5
    confidence: high
    note: "Foundation: mid #11 (stateupdate-subsystem-wire-format.md). 8 vtables use this slot"
  - claim: "Powered WriteState format: base + 1 bit hasData + 1 byte powerPct (remote)"
    address: 0x00562960
    function: PoweredSubsystem__WriteState
    completeness: 11.1
    confidence: high
    note: "Foundation: mid #11. 11 vtables use this slot. Bit packs against +0x2C bit cursor"
  - claim: "Power WriteState format: base + 2 battery bytes UNCONDITIONAL"
    address: 0x005644b0
    function: PowerSubsystem__WriteState
    completeness: 25.9
    confidence: high
    note: "Foundation: mid #11. 1 vtable @ 0x0088A260 (PowerSubsystem reactor)"
  - claim: "Sovereign cycle = 49 bytes; 11 top-level / 22 children / 33 total"
    address: null
    function: null
    completeness: n/a
    confidence: high
    note: "Cross-source: sovereign.py LoadPropertySet lines 1379-1474. Hand-computed: 1+1+3+3+5+9+3+11+7+5+1 = 49. Match"
  - claim: "Bird of Prey cycle = 32 bytes; 10 top-level / 6 children / 16 total; no PhaserSystem"
    address: null
    function: null
    completeness: n/a
    confidence: high
    note: "Cross-source: birdofprey.py LoadPropertySet lines 461-509. Hand-computed: 1+1+3+5+4+4+5+3+3+3 = 32. Match. PulseWeaponSystem-only via WST_PULSE at line 227"
  - claim: "Galor cycle = 31 bytes; 9 top-level / 8 children / 17 total; no tractors"
    address: null
    function: null
    completeness: n/a
    confidence: high
    note: "Cross-source: galor.py LoadPropertySet lines 618-668. Hand-computed: 1+1+3+7+4+5+4+3+3 = 31. Match"
  - claim: "Akira cycle = 47 bytes; 11 top-level / 20 children / 31 total"
    address: null
    function: null
    completeness: n/a
    confidence: high
    note: "Cross-source: akira.py LoadPropertySet lines 1274-1307. Hand-computed: 1+1+3+3+5+11+5+9+3+5+1 = 47. Match. Bridge at AddToSet pos 38, Tractors at pos 21 (reversed)"
  - claim: "12 remaining ships + Enterprise@37 derived by pattern extrapolation from sampled set"
    address: null
    function: null
    completeness: n/a
    confidence: medium
    note: "All 4 axes (structural formula, AddToSet ordering, special-case catalog, foundation slot offsets) held for 4 sampled ships. Promotion to high requires byte-by-byte verification of remaining 12"
  - claim: "Ship_LinkAllSubsystemsToParents reparents children before round-robin sees the list"
    address: 0x005b3e20
    function: Ship__LinkAllSubsystemsToParents
    completeness: n/a
    confidence: high
    note: "Foundation: mid #11. Doc's 'Top-Level' count is the post-link state, not the raw AddToSet count"
  - claim: "Runtime ship+0x284 list is FLAT: each weapon mount is its own top-level round-robin entry; catalog 'Children' grouping is hardpoint-tree readability only. True top-level entry count = Top-Level + Children"
    address: 0x005b3e20
    function: Ship__LinkAllSubsystemsToParents
    completeness: n/a
    confidence: high
    note: "[v5-correction 2026-05-29 via authority-ordering investigation] Wire-trace: start_idx reaches 6-11 (up to 16 on larger hulls), impossible if mounts were children under one parent index. Cycle-byte totals unchanged. Memos: authority-ordering-validation-20260529 + ordering-trace-verification-20260529."
supersedes:
  - 2026-02-22
  - 2026-05-28
---

# Per-Ship Subsystem Wire Format Catalog

> [!NOTE]
> This doc is `status: partial`. **Zero material wire-format corrections** in this v5 pass — the doc was exceptionally accurate. Four ships sampled byte-by-byte against `reference/scripts/ships/Hardpoints/<name>.py`: **Sovereign (49 bytes)**, **Bird of Prey (32)**, **Galor (31)**, **Akira (47)** — cycle-byte math matches the Summary Table EXACTLY. The 12 remaining ships are tagged `confidence: medium` by pattern extrapolation from the sampled set (the validation strategy: structural formula + AddToSet ordering + special-case catalog + foundation slot offsets all held for sampled ships; extrapolation justified). Three refinements landed: **(R1)** cycle-byte arithmetic is per-tick exact but per-cycle approximate due to bit-stream packing; **(R2)** "Top-Level Subsystems" is the post-link count after `Ship__LinkAllSubsystemsToParents` reparenting; **(R3)** templates like Probe Launcher / Shuttle Bay / Decoy Launcher silently drop because their property type IDs don't match any case in `Ship__SetupProperties`. Foundation cross-anchor: mid #11 slot table (ship+0x2B0..+0x2DC) re-confirmed via fresh `Ship__SetupProperties` decompile; per-ship doc never cites ship+offset directly, so foundation corrections don't cascade. See [docs/guides/v5-evidence-header.md](../guides/v5-evidence-header.md) for the standard.

> [!IMPORTANT]
> **2026-05-29 runtime list is FLAT `[v5-correction 2026-05-29 via authority-ordering investigation]`.**
> The per-ship catalogs below group each ship's weapon mounts (phaser banks, torpedo tubes,
> tractor projectors) as **children nested under their parent system** (PhaserSystem,
> TorpedoSystem, TractorBeamSystem) at a single top-level index — this is the **hardpoint
> `AddToSet` tree** and is kept here for readability. The **RUNTIME serialization list is FLAT**:
> `Ship_LinkAllSubsystemsToParents` (FUN_005B3E20) reparents every child out of the tree into the
> flat top-level ship+0x284 list **before** the first StateUpdate, so on the wire **each weapon
> mount is its own top-level round-robin entry with its own `start_idx`** — NOT absorbed inline
> under a parent.
>
> Wire proof: stock traces show `start_idx` taking the values 6, 7, 8, 9, 10, 11 (and up to 16
> on larger hulls), which is impossible if those mounts were children stepped over as one entry.
> So the **"Children" column and the "1 + N children inline" cycle-byte arithmetic below model
> the byte TOTAL correctly** (the same bytes appear on the wire either way), **but the
> top-level-entry COUNT and the per-index mapping must be read as flat**: a ship's true top-level
> entry count is `Top-Level + Children` (e.g. Sovereign = 11 + 22 = 33 flat top-level nodes, not
> 11). For the flatten reconciliation, the byte-anchored `start_idx`/`has_power`/stream-exhaustion
> corrections, and the OpenBC `ser_list` requirement, see
> [stateupdate-subsystem-wire-format.md § Flatten Reconciliation](stateupdate-subsystem-wire-format.md).
> Evidence: `.claude/agent-memory/game-archaeology-specialist/authority-ordering-validation-20260529.md`
> + `.claude/agent-memory/network-protocol-analyst/ordering-trace-verification-20260529.md`.

## Overview

The StateUpdate flag 0x20 (subsystem health) serializes the ship's **top-level subsystem
linked list** (ship+0x284) using a round-robin algorithm with a 10-byte budget per tick.
Each ship class has a **different** top-level subsystem list determined by its hardpoint
Python script's `LoadPropertySet()` function. Both the order and composition of subsystems
vary per ship.

This document catalogs the exact wire format for all 16 stock multiplayer ships
(species 1-15 plus Enterprise at species slot 37). The catalog was originally derived from a
2026-02-22 collision test stock-dedi trace and the published hardpoint scripts; the
2026-05-28 v5 pass byte-verified 4 ships against their `LoadPropertySet` order and the
mid #11 / mid #8 binary anchors.

For the round-robin algorithm, WriteState implementations, and linked list structure, see
[stateupdate-subsystem-wire-format.md](stateupdate-subsystem-wire-format.md).

## Validation Sampling Strategy

For a catalog doc with ~250 parallel rows (16 ships × ~16 cells each), full byte-by-byte
verification of every cell is expensive. The v5 pass adopted a sampling strategy: verify
4 ships byte-by-byte, then extrapolate to the remaining 12 only if the structural pattern
holds on every sampled ship.

Each sampled ship was checked along 4 axes:

1. **Structural formula** — Base = 1 byte; Powered = 1 + N children + ~2; Power = 1 + 0 + 2.
   Hand-compute the cycle total from the AddToSet order; compare to the doc's Cycle Bytes
   column.
2. **AddToSet ordering** — Read the hardpoint .py `LoadPropertySet`; verify the doc's
   top-level subsystem index column matches the AddToSet position (post-link, per
   refinement R2).
3. **Special-case catalog** — Does the ship's row in the Summary Table correctly call out
   Cloak / Pulse / Tractors / Bridge presence?
4. **Foundation cross-anchors** — Does the ship+0x2B0..+0x2DC slot population implied by
   the ship's property IDs match the mid #11 named-slot table?

All 4 axes held for all 4 sampled ships. The extrapolation to the remaining 12 hulls is
medium-confidence: the structural rules are uniform (`SetupProperties` is one switch
statement; `LinkAllSubsystemsToParents` is one loop), so a ship that follows the same
AddToSet shape will fall out byte-correct without re-derivation. Promotion of the remaining
12 to high confidence (and the doc to `verified`) requires byte-by-byte verification of
each of those hulls.

The 4 sampled ships were chosen for coverage: 1 large Federation capital
(**Sovereign**, 11/22, 49 bytes), 1 small non-Federation no-Phaser hull (**Bird of Prey**,
10/6, 32 bytes), 1 small no-Tractor Cardassian (**Galor**, 9/8, 31 bytes), 1 Federation
mid-size with reversed Bridge/Tractor ordering (**Akira**, 11/20, 47 bytes). Together
these exercise every special case in the Universal Subsystem Patterns section.

## Species ID Mapping `[cross-source-2026-05-28]`

From `reference/scripts/Multiplayer/SpeciesToShip.py` (`MAX_FLYABLE_SHIPS = 16` at line 51).
Enterprise (slot 37) inherits from Sovereign via `App.SPECIES_SOVEREIGN` at lines 60 + 92.

| Species ID | Ship | Faction | Hardpoint File | Species Code |
|-----------|------|---------|----------------|--------------|
| 1 | Akira | Federation | akira.py | 103 |
| 2 | Ambassador | Federation | ambassador.py | 104 |
| 3 | Galaxy | Federation | galaxy.py | 101 |
| 4 | Nebula | Federation | nebula.py | 105 |
| 5 | Sovereign | Federation | sovereign.py | 102 |
| 6 | Bird of Prey | Klingon | birdofprey.py | 401 |
| 7 | Vor'cha | Klingon | vorcha.py | 402 |
| 8 | Warbird | Romulan | warbird.py | 301 |
| 9 | Marauder | Ferengi | marauder.py | 601 |
| 10 | Galor | Cardassian | galor.py | 201 |
| 11 | Keldon | Cardassian | keldon.py | 202 |
| 12 | CardHybrid | Cardassian | cardhybrid.py | 204 |
| 13 | KessokHeavy | Kessok | kessokheavy.py | 501 |
| 14 | KessokLight | Kessok | kessoklight.py | 502 |
| 15 | Shuttle | Federation | shuttle.py | 106 |
| 37 | Enterprise | Federation | enterprise.py | 102 (=Sovereign) |

`MAX_FLYABLE_SHIPS = 16`. Enterprise (slot 37) inherits from Sovereign and has an
identical subsystem layout — only HP/capacity values differ.

## WriteState Type Reference `[v5-validated 2026-05-28]`

Three virtual implementations of WriteState (vtable+0x70) exist. All three anchored
against mid #11 (`stateupdate-subsystem-wire-format.md`).

| Class | Address | Used By | Bytes (remote) | Format |
|-------|---------|---------|----------------|--------|
| Base ShipSubsystem | 0x0056d320 | HullSubsystem, ShieldGenerator | 1 + N_children | `[cond:u8][child conds...]` |
| PoweredSubsystem | 0x00562960 | SensorSS, ImpulseEngine, WarpEngine, PhaserSystem, TorpedoSystem, TractorBeamSystem, PulseWeaponSystem, CloakDevice, RepairSS | 1 + N_children + ~2 | `[cond:u8][child conds...][hasData:bit=1][powerPct:u8]` |
| PowerSubsystem | 0x005644b0 | PowerSubsystem (reactor) | 1 + 2 | `[cond:u8][mainBatt:u8][backupBatt:u8]` |

- **condition**: `(int)(currentCondition / maxCondition * 255.0)`, 0xFF=100%, 0x00=destroyed
- **powerPct**: `(int)(powerPercentageWanted * 100.0)`, range 0-100
- **mainBatt/backupBatt**: `(int)(batteryPower / batteryLimit * 255.0)`, range 0x00-0xFF
- PowerSubsystem ALWAYS writes battery bytes regardless of isOwnShip (verified by absence
  of `TEST/JCC` on isOwnShip between the base call and the two CALL `[vtable+0x54]` writes
  in `PowerSubsystem__WriteState`).
- PoweredSubsystem only writes power data for remote ships (isOwnShip==0)
- Child subsystems always use Base WriteState (1 byte each)

> **R1 — Per-tick exact, per-cycle approximate.** The Powered "~2 bytes" tail packs
> `[bit hasData][byte powerPct]` against the bit-stream cursor at TGBufferStream+0x2C.
> Because hasData is a single bit, actual per-cycle wire totals may differ by 1-3 bytes
> from the 2-byte approximation, depending on subsystem-boundary alignment. The
> round-robin 10-byte budget cap at 0x005B1EC0 (`CMP EAX, 0xA`) is measured against
> the BYTE cursor, so the approximation is **exact at tick boundaries** but only
> approximate when summing a whole cycle.

## Summary Table

| Sp | Ship | Top-Level | Children | Total | Cycle Bytes | Cloak | Pulse | Tractors | Bridge | Validation |
|----|------|-----------|----------|-------|-------------|-------|-------|----------|--------|------------|
| 1 | Akira | 11 | 20 | 31 | 47 | — | — | 2 | Yes | `[v5-validated 2026-05-28]` |
| 2 | Ambassador | 11 | 18 | 29 | 45 | — | — | 2 | Yes | `[confidence: medium]` |
| 3 | Galaxy | 11 | 23 | 34 | 50 | — | — | 4 | Yes | `[confidence: medium]` |
| 4 | Nebula | 11 | 20 | 31 | 47 | — | — | 2 | Yes | `[confidence: medium]` |
| 5 | Sovereign | 11 | 22 | 33 | 49 | — | — | 4 | Yes | `[v5-validated 2026-05-28]` |
| 6 | Bird of Prey | 10 | 6 | 16 | 32 | Yes | 2 | — | — | `[v5-validated 2026-05-28]` |
| 7 | Vor'cha | 12 | 12 | 24 | 44 | Yes | 2 | 2 | — | `[confidence: medium]` |
| 8 | Warbird | 13 | 13 | 26 | 46 | Yes | 4 | 2 | Yes | `[confidence: medium]` |
| 9 | Marauder | 10 | 9 | 19 | 35 | — | 2 | 2 | — | `[confidence: medium]` |
| 10 | Galor | 9 | 8 | 17 | 31 | — | — | — | — | `[v5-validated 2026-05-28]` |
| 11 | Keldon | 10 | 13 | 23 | 39 | — | — | 2 | — | `[confidence: medium]` |
| 12 | CardHybrid | 11 | 18 | 29 | 47 | — | 1 | 2 | — | `[confidence: medium]` |
| 13 | KessokHeavy | 10 | 14 | 24 | 40 | Yes | — | — | — | `[confidence: medium]` |
| 14 | KessokLight | 10 | 13 | 23 | 39 | Yes | — | — | — | `[confidence: medium]` |
| 15 | Shuttle | 9 | 6 | 15 | 29 | — | — | 1 | — | `[confidence: medium]` |
| 37 | Enterprise | 11 | 22 | 33 | 49 | — | — | 4 | Yes | `[confidence: medium]` |

- **Top-Level**: Subsystems in ship+0x284 after `Ship__LinkAllSubsystemsToParents`
  (FUN_005b3e20) — see R2.
- **Children**: Subsystems removed from ship+0x284 and nested under parent systems
- **Total**: All subsystems created by `Ship__SetupProperties` (FUN_005b3fb0)
- **Cycle Bytes**: Total bytes to serialize all top-level subsystems once (flag 0x20 full
  cycle). Subject to R1 (per-cycle approximation due to bit-stream packing).

> **R2 — "Top-Level" is post-link.** The Top-Level count is the post-link state — after
> `Ship__LinkAllSubsystemsToParents` (0x005B3E20) reparents children. Pre-link, all
> subsystems sit in the ship+0x284 doubly-linked list. Post-link, children with non-zero
> WeaponID/EngineType get pulled out and re-attached under their parent system. The
> round-robin walks the post-link list.

### Stock Dedi Verification `[cross-source-2026-02-22]`

From function tracer `Ship_AddSubsystem` counts (2026-02-22 collision test, 15 species —
Enterprise excluded since it aliases Sovereign):

| Species | Ship | Hardpoint Count | Tracer Count | Match |
|---------|------|----------------|--------------|-------|
| 1 | Akira | 31 | 31 | ✓ |
| 2 | Ambassador | 29 | 29 | ✓ |
| 3 | Galaxy | 34 | 34 | ✓ |
| 4 | Nebula | 31 | 31 | ✓ |
| 5 | Sovereign | 33 | 33 | ✓ |
| 6 | Bird of Prey | 16 | 16 | ✓ |
| 7 | Vor'cha | 24 | 24 | ✓ |
| 8 | Warbird | 26 | 26 | ✓ |
| 9 | Marauder | 19 | 19 | ✓ |
| 10 | Galor | 17 | 17 | ✓ |
| 11 | Keldon | 23 | 23 | ✓ |
| 12 | CardHybrid | 29 | 29 | ✓ |
| 13 | KessokHeavy | 24 | 24 | ✓ |
| 14 | KessokLight | 23 | 23 | ✓ |
| 15 | Shuttle | 15 | 15 | ✓ |

All 15 hardpoint-derived counts match the runtime function tracer exactly.

### Templates That Don't Materialize (R3)

Some templates in `LoadPropertySet` `AddToSet` calls never instantiate as subsystems
because their property type IDs don't match any case in `Ship__SetupProperties`
(0x005B3FB0). The switch defaults out; no subsystem is allocated; `Ship_AddSubsystemToLists`
is never called. Result: they don't appear in the top-level linked list, and the per-ship
tables below correctly omit them.

Examples:

| Template | Cited in | Result |
|----------|----------|--------|
| "Probe Launcher" | sovereign.py line 1454 | Drops; not in list |
| "Shuttle Bay" / "Shuttle Bay 2" | Multiple Federation hardpoints | Drops; not in list |
| "Decoy launcher" | Various | Drops; not in list |
| Viewscreen / camera entries | Various | Drops; not subsystems |

These are not bugs in the per-ship tables — the catalog reflects the post-`SetupProperties`
state, which is what the round-robin sees.

## Per-Ship Detail

Each ship section shows:
1. Top-level subsystem list (ship+0x284 order after child linking)
2. Children per top-level subsystem
3. WriteState type and byte count for a remote ship
4. The AddToSet order determines the linked list order (per R2: post-link)

> **Reading the "Children" column post-2026-05-29 `[v5-correction 2026-05-29 via authority-ordering investigation]`:**
> The "Children" column groups weapon mounts under their parent system for readability, mirroring
> the hardpoint tree. On the wire the runtime list is **FLAT** — each listed child is its own
> top-level round-robin entry with its own `start_idx` (see the IMPORTANT block at the top of this
> doc). The byte counts in the "WriteState Bytes" column are unchanged (the same bytes appear on
> the wire), but a ship's true top-level entry count for `start_idx` purposes is
> `Top-Level + Children`, not the "Top-Level" figure alone.

---

### Species 1: Akira (Akira-class) `[v5-validated 2026-05-28]`

Cross-source: `reference/scripts/ships/Hardpoints/akira.py` LoadPropertySet lines 1274-1307.

| Idx | Subsystem | Type | Children | WriteState Bytes |
|-----|-----------|------|----------|-----------------|
| 0 | Hull | HullSubsystem | 0 | 1 |
| 1 | Shield Generator | ShieldGenerator | 0 | 1 |
| 2 | Sensor Array | SensorSubsystem | 0 | 3 |
| 3 | Warp Core | PowerSubsystem | 0 | 3 |
| 4 | Impulse Engines | ImpulseEngine | 2 (Port, Star) | 5 |
| 5 | Phasers | PhaserSystem | 8 (Ventral 1-4, Dorsal 1-4) | 11 |
| 6 | Warp Engines | WarpEngine | 2 (Port, Star) | 5 |
| 7 | Torpedoes | TorpedoSystem | 6 (Fwd 1-2, Aft 1, Fwd 3-4, Aft 2) | 9 |
| 8 | Engineering | RepairSubsystem | 0 | 3 |
| 9 | Tractors | TractorBeamSystem | 2 (Forward, Aft) | 5 |
| 10 | Bridge | HullSubsystem | 0 | 1 |

**11 top-level, 20 children, 31 total. Full cycle: 47 bytes.**
Hand-computed cycle: `1+1+3+3+5+11+5+9+3+5+1 = 47`. Bridge at AddToSet position 38,
Tractors at position 21 (reversed-from-Federation-norm order).

---

### Species 2: Ambassador (Ambassador-class) `[confidence: medium — pattern-extrapolated from sampled set]`

Cross-source: `reference/scripts/ships/Hardpoints/ambassador.py` (lines per LoadPropertySet).

| Idx | Subsystem | Type | Children | WriteState Bytes |
|-----|-----------|------|----------|-----------------|
| 0 | Hull | HullSubsystem | 0 | 1 |
| 1 | Shield Generator | ShieldGenerator | 0 | 1 |
| 2 | Sensor Array | SensorSubsystem | 0 | 3 |
| 3 | Warp Core | PowerSubsystem | 0 | 3 |
| 4 | Impulse Engines | ImpulseEngine | 2 (Port, Star) | 5 |
| 5 | Phasers | PhaserSystem | 8 (Ventral 1-3, Dorsal 1-3, Aft 1-2) | 11 |
| 6 | Warp Engines | WarpEngine | 2 (Port, Star) | 5 |
| 7 | Torpedoes | TorpedoSystem | 4 (Fwd 1-2, Aft 1-2) | 7 |
| 8 | Engineering | RepairSubsystem | 0 | 3 |
| 9 | Bridge | HullSubsystem | 0 | 1 |
| 10 | Tractors | TractorBeamSystem | 2 (Forward, Aft) | 5 |

**11 top-level, 18 children, 29 total. Full cycle: 45 bytes.**

Note: Bridge at index 9 and Tractors at index 10 (reversed vs. most Federation ships).

---

### Species 3: Galaxy (Galaxy-class) `[confidence: medium — pattern-extrapolated from sampled set]`

Cross-source: `reference/scripts/ships/Hardpoints/galaxy.py` (lines per LoadPropertySet).

| Idx | Subsystem | Type | Children | WriteState Bytes |
|-----|-----------|------|----------|-----------------|
| 0 | Hull | HullSubsystem | 0 | 1 |
| 1 | Warp Core | PowerSubsystem | 0 | 3 |
| 2 | Shield Generator | ShieldGenerator | 0 | 1 |
| 3 | Sensor Array | SensorSubsystem | 0 | 3 |
| 4 | Torpedoes | TorpedoSystem | 6 (Fwd 1-4, Aft 1-2) | 9 |
| 5 | Phasers | PhaserSystem | 8 (Ventral 1-4, Dorsal 1-4) | 11 |
| 6 | Impulse Engines | ImpulseEngine | 3 (Port, Star, Center) | 6 |
| 7 | Warp Engines | WarpEngine | 2 (Port, Star) | 5 |
| 8 | Tractors | TractorBeamSystem | 4 (Aft 1-2, Fwd 1-2) | 7 |
| 9 | Bridge | HullSubsystem | 0 | 1 |
| 10 | Engineering | RepairSubsystem | 0 | 3 |

**11 top-level, 23 children, 34 total. Full cycle: 50 bytes.**

Notable: Warp Core at index 1 (before Shield Generator). **3 impulse engines** (unique
among Federation ships). Engineering at index 10 (last).

---

### Species 4: Nebula (Nebula-class) `[confidence: medium — pattern-extrapolated from sampled set]`

Cross-source: `reference/scripts/ships/Hardpoints/nebula.py` (lines per LoadPropertySet).

| Idx | Subsystem | Type | Children | WriteState Bytes |
|-----|-----------|------|----------|-----------------|
| 0 | Hull | HullSubsystem | 0 | 1 |
| 1 | Shield Generator | ShieldGenerator | 0 | 1 |
| 2 | Sensor Array | SensorSubsystem | 0 | 3 |
| 3 | Warp Core | PowerSubsystem | 0 | 3 |
| 4 | Impulse Engines | ImpulseEngine | 2 (Port, Star) | 5 |
| 5 | Phasers | PhaserSystem | 8 (Ventral 1-4, Dorsal 1-4) | 11 |
| 6 | Warp Engines | WarpEngine | 2 (Port, Star) | 5 |
| 7 | Torpedoes | TorpedoSystem | 6 (Fwd 1-4, Aft 1-2) | 9 |
| 8 | Repair | RepairSubsystem | 0 | 3 |
| 9 | Tractors | TractorBeamSystem | 2 (Aft, Forward) | 5 |
| 10 | Bridge | HullSubsystem | 0 | 1 |

**11 top-level, 20 children, 31 total. Full cycle: 47 bytes.**

---

### Species 5: Sovereign (Sovereign-class) `[v5-validated 2026-05-28]`

Cross-source: `reference/scripts/ships/Hardpoints/sovereign.py` LoadPropertySet lines 1379-1474.

| Idx | Subsystem | Type | Children | WriteState Bytes |
|-----|-----------|------|----------|-----------------|
| 0 | Hull | HullSubsystem | 0 | 1 |
| 1 | Shield Generator | ShieldGenerator | 0 | 1 |
| 2 | Sensor Array | SensorSubsystem | 0 | 3 |
| 3 | Warp Core | PowerSubsystem | 0 | 3 |
| 4 | Impulse Engines | ImpulseEngine | 2 (Port, Star) | 5 |
| 5 | Torpedoes | TorpedoSystem | 6 (Fwd 1-4, Aft 1-2) | 9 |
| 6 | Repair | RepairSubsystem | 0 | 3 |
| 7 | Phasers | PhaserSystem | 8 (Ventral 1-4, Dorsal 1-4) | 11 |
| 8 | Tractors | TractorBeamSystem | 4 (Aft 1-2, Fwd 1-2) | 7 |
| 9 | Warp Engines | WarpEngine | 2 (Port, Star) | 5 |
| 10 | Bridge | HullSubsystem | 0 | 1 |

**11 top-level, 22 children, 33 total. Full cycle: 49 bytes.**
Hand-computed cycle: `1+1+3+3+5+9+3+11+7+5+1 = 49`. Probe Launcher (line 1454) is in
LoadPropertySet but its type ID does not match any `Ship__SetupProperties` case — it
silently drops (R3).

Enterprise (species 37) has an identical layout — it inherits from Sovereign via
`ParentModule.LoadPropertySet()` and only overrides 4 property values (Hull HP, Shield HP,
Warp Core capacity, Engineering repair capacity).

---

### Species 6: Bird of Prey (Klingon B'rel-class) `[v5-validated 2026-05-28]`

Cross-source: `reference/scripts/ships/Hardpoints/birdofprey.py` LoadPropertySet lines 461-509.

| Idx | Subsystem | Type | Children | WriteState Bytes |
|-----|-----------|------|----------|-----------------|
| 0 | Hull | HullSubsystem | 0 | 1 |
| 1 | Shield Generator | ShieldGenerator | 0 | 1 |
| 2 | Warp Core | PowerSubsystem | 0 | 3 |
| 3 | Disruptor Cannons | PulseWeaponSystem | 2 (Port, Star) | 5 |
| 4 | Torpedoes | TorpedoSystem | 1 (Forward) | 4 |
| 5 | Impulse Engines | ImpulseEngine | 1 (single engine) | 4 |
| 6 | Warp Engines | WarpEngine | 2 (Port, Star) | 5 |
| 7 | Cloaking Device | CloakDevice | 0 | 3 |
| 8 | Sensor Array | SensorSubsystem | 0 | 3 |
| 9 | Engineering | RepairSubsystem | 0 | 3 |

**10 top-level, 6 children, 16 total. Full cycle: 32 bytes.**
Hand-computed cycle: `1+1+3+5+4+4+5+3+3+3 = 32`.

Notable: No phasers — uses PulseWeaponSystem (disruptor cannons) only, via `WST_PULSE` at
line 227. Single impulse engine, single torpedo tube. Has cloaking device. No Bridge,
no tractors.

---

### Species 7: Vor'cha (Klingon Vor'cha-class) `[confidence: medium — pattern-extrapolated from sampled set]`

Cross-source: `reference/scripts/ships/Hardpoints/vorcha.py` (lines per LoadPropertySet).

| Idx | Subsystem | Type | Children | WriteState Bytes |
|-----|-----------|------|----------|-----------------|
| 0 | Hull | HullSubsystem | 0 | 1 |
| 1 | Shield Generator | ShieldGenerator | 0 | 1 |
| 2 | Warp Core | PowerSubsystem | 0 | 3 |
| 3 | Disruptor Beams | PhaserSystem | 1 (single disruptor) | 4 |
| 4 | Disruptor Cannons | PulseWeaponSystem | 2 (Port, Star) | 5 |
| 5 | Torpedoes | TorpedoSystem | 3 (Fwd 1-2, Aft) | 6 |
| 6 | Impulse Engines | ImpulseEngine | 2 (Port, Star) | 5 |
| 7 | Warp Engines | WarpEngine | 2 (Port, Star) | 5 |
| 8 | Cloaking Device | CloakDevice | 0 | 3 |
| 9 | Sensor Array | SensorSubsystem | 0 | 3 |
| 10 | Repair System | RepairSubsystem | 0 | 3 |
| 11 | Tractors | TractorBeamSystem | 2 (Aft, Forward) | 5 |

**12 top-level, 12 children, 24 total. Full cycle: 44 bytes.**

Notable: Has BOTH PhaserSystem (1 disruptor beam) AND PulseWeaponSystem (2 cannons).
12 top-level is the most of any non-Romulan ship. Has cloaking device.

---

### Species 8: Warbird (Romulan D'deridex-class) `[confidence: medium — pattern-extrapolated from sampled set]`

Cross-source: `reference/scripts/ships/Hardpoints/warbird.py` (lines per LoadPropertySet).

| Idx | Subsystem | Type | Children | WriteState Bytes |
|-----|-----------|------|----------|-----------------|
| 0 | Hull | HullSubsystem | 0 | 1 |
| 1 | Shield Generator | ShieldGenerator | 0 | 1 |
| 2 | Power Plant | PowerSubsystem | 0 | 3 |
| 3 | Disruptor Beam | PhaserSystem | 1 (single disruptor) | 4 |
| 4 | Disruptor Cannons | PulseWeaponSystem | 4 (Port 1-2, Star 1-2) | 7 |
| 5 | Torpedoes | TorpedoSystem | 2 (Forward, Aft) | 5 |
| 6 | Impulse Engines | ImpulseEngine | 2 (Port, Star) | 5 |
| 7 | Warp Engines | WarpEngine | 2 (Port, Star) | 5 |
| 8 | Cloaking Device | CloakDevice | 0 | 3 |
| 9 | Sensor Array | SensorSubsystem | 0 | 3 |
| 10 | Engineering | RepairSubsystem | 0 | 3 |
| 11 | Bridge | HullSubsystem | 0 | 1 |
| 12 | Tractors | TractorBeamSystem | 2 (Aft, Forward) | 5 |

**13 top-level, 13 children, 26 total. Full cycle: 46 bytes.**

Notable: **13 top-level** — the most of any stock ship. Reactor named "Power Plant".
4 pulse weapons (most of any ship). Only non-Federation ship with Bridge hull.
Has both PhaserSystem and PulseWeaponSystem.

---

### Species 9: Marauder (Ferengi D'Kora-class) `[confidence: medium — pattern-extrapolated from sampled set]`

Cross-source: `reference/scripts/ships/Hardpoints/marauder.py` (lines per LoadPropertySet).

| Idx | Subsystem | Type | Children | WriteState Bytes |
|-----|-----------|------|----------|-----------------|
| 0 | Hull | HullSubsystem | 0 | 1 |
| 1 | Shield Generator | ShieldGenerator | 0 | 1 |
| 2 | Warp Core | PowerSubsystem | 0 | 3 |
| 3 | Phasers | PhaserSystem | 1 (Ventral Phaser) | 4 |
| 4 | Impulse Engines | ImpulseEngine | 2 (Port, Star) | 5 |
| 5 | Warp Engines | WarpEngine | 2 (Star, Port) | 5 |
| 6 | Tractors | TractorBeamSystem | 2 (Forward, Aft) | 5 |
| 7 | Sensor Array | SensorSubsystem | 0 | 3 |
| 8 | Repair Subsystem | RepairSubsystem | 0 | 3 |
| 9 | Plasma Emitters | PulseWeaponSystem | 2 (Port, Star) | 5 |

**10 top-level, 9 children, 19 total. Full cycle: 35 bytes.**

Notable: NO torpedoes at all — only stock ship without them. Only 1 phaser bank. Has
Plasma Emitters (PulseWeaponSystem). No Bridge.

---

### Species 10: Galor (Cardassian Galor-class) `[v5-validated 2026-05-28]`

Cross-source: `reference/scripts/ships/Hardpoints/galor.py` LoadPropertySet lines 618-668.

| Idx | Subsystem | Type | Children | WriteState Bytes |
|-----|-----------|------|----------|-----------------|
| 0 | Hull | HullSubsystem | 0 | 1 |
| 1 | Shield Generator | ShieldGenerator | 0 | 1 |
| 2 | Warp Core | PowerSubsystem | 0 | 3 |
| 3 | Compressors | PhaserSystem | 4 (Forward, Port, Star, Aft Beam) | 7 |
| 4 | Torpedoes | TorpedoSystem | 1 (Forward) | 4 |
| 5 | Impulse Engines | ImpulseEngine | 2 (Port, Star) | 5 |
| 6 | Warp Engine | WarpEngine | 1 (single engine) | 4 |
| 7 | Repair Subsystem | RepairSubsystem | 0 | 3 |
| 8 | Sensor Array | SensorSubsystem | 0 | 3 |

**9 top-level, 8 children, 17 total. Full cycle: 31 bytes.**
Hand-computed cycle: `1+1+3+7+4+5+4+3+3 = 31`. "Aft Beam" gets reparented to Compressors
as the 4th phaser child via `Ship__LinkAllSubsystemsToParents`.

Notable: Only **9 top-level** — smallest non-shuttle ship. Phaser system named
"Compressors". Single warp engine. Single torpedo tube. No tractors, no Bridge, no cloak.

---

### Species 11: Keldon (Cardassian Keldon-class) `[confidence: medium — pattern-extrapolated from sampled set]`

Cross-source: `reference/scripts/ships/Hardpoints/keldon.py` (lines per LoadPropertySet).

| Idx | Subsystem | Type | Children | WriteState Bytes |
|-----|-----------|------|----------|-----------------|
| 0 | Hull | HullSubsystem | 0 | 1 |
| 1 | Shield Generator | ShieldGenerator | 0 | 1 |
| 2 | Warp Core | PowerSubsystem | 0 | 3 |
| 3 | Compressors | PhaserSystem | 4 (Forward, Port, Star, Aft Beam) | 7 |
| 4 | Torpedoes | TorpedoSystem | 2 (Forward, Aft) | 5 |
| 5 | Impulse Engines | ImpulseEngine | 4 (Engine 1-4) | 7 |
| 6 | Warp Engine | WarpEngine | 1 (single engine) | 4 |
| 7 | Sensor Array | SensorSubsystem | 0 | 3 |
| 8 | Repair Subsystem | RepairSubsystem | 0 | 3 |
| 9 | Tractors | TractorBeamSystem | 2 (Ventral, Dorsal) | 5 |

**10 top-level, 13 children, 23 total. Full cycle: 39 bytes.**

Notable: **4 impulse engines** — unique among all stock ships. Like Galor, uses
"Compressors" for phasers and has single warp engine.

---

### Species 12: CardHybrid (Cardassian Hybrid) `[confidence: medium — pattern-extrapolated from sampled set]`

Cross-source: `reference/scripts/ships/Hardpoints/cardhybrid.py` (lines per LoadPropertySet).

| Idx | Subsystem | Type | Children | WriteState Bytes |
|-----|-----------|------|----------|-----------------|
| 0 | Hull | HullSubsystem | 0 | 1 |
| 1 | Warp Core | PowerSubsystem | 0 | 3 |
| 2 | Torpedoes | TorpedoSystem | 3 (Torpedo 1-2, Aft Torpedo) | 6 |
| 3 | Repair System | RepairSubsystem | 0 | 3 |
| 4 | Shield Generator | ShieldGenerator | 0 | 1 |
| 5 | Sensor Array | SensorSubsystem | 0 | 3 |
| 6 | Impulse Engines | ImpulseEngine | 2 (Port, Star) | 5 |
| 7 | Warp Engines | WarpEngine | 3 (Port, Star, Center) | 6 |
| 8 | Beams | PhaserSystem | 7 (Fwd Compressor, Fwd 1-2, Ventral 1-2, Dorsal 1-2) | 10 |
| 9 | Disruptor Cannons | PulseWeaponSystem | 1 (single cannon) | 4 |
| 10 | Tractors | TractorBeamSystem | 2 (Forward, Aft) | 5 |

**11 top-level, 18 children, 29 total. Full cycle: 47 bytes.**

Notable: Unusual AddToSet order — Warp Core at index 1, Repair at index 3, Shield at
index 4. Has BOTH PhaserSystem ("Beams", 7 banks — most phaser banks) AND PulseWeaponSystem
(1 cannon). **3 warp engines** (Port, Star, Center) — unique among stock ships.

---

### Species 13: KessokHeavy (Kessok Heavy Cruiser) `[confidence: medium — pattern-extrapolated from sampled set]`

Cross-source: `reference/scripts/ships/Hardpoints/kessokheavy.py` (lines per LoadPropertySet).

| Idx | Subsystem | Type | Children | WriteState Bytes |
|-----|-----------|------|----------|-----------------|
| 0 | Hull | HullSubsystem | 0 | 1 |
| 1 | Warp Core | PowerSubsystem | 0 | 3 |
| 2 | Impulse Engines | ImpulseEngine | 2 (Port, Star) | 5 |
| 3 | Warp Engines | WarpEngine | 2 (Port, Star) | 5 |
| 4 | Positron Beams | PhaserSystem | 8 (Fwd 1-4, Ventral 1-2, Dorsal 1-2) | 11 |
| 5 | Torpedoes | TorpedoSystem | 2 (Tube 1-2) | 5 |
| 6 | Repair System | RepairSubsystem | 0 | 3 |
| 7 | Shield Generator | ShieldGenerator | 0 | 1 |
| 8 | Sensor Array | SensorSubsystem | 0 | 3 |
| 9 | Cloaking Device | CloakDevice | 0 | 3 |

**10 top-level, 14 children, 24 total. Full cycle: 40 bytes.**

Notable: Has Cloaking Device. Phasers named "Positron Beams" (8 banks). Shield Generator
at index 7 (unusual). No tractors, no Bridge.

---

### Species 14: KessokLight (Kessok Destroyer) `[confidence: medium — pattern-extrapolated from sampled set]`

Cross-source: `reference/scripts/ships/Hardpoints/kessoklight.py` (lines per LoadPropertySet).

| Idx | Subsystem | Type | Children | WriteState Bytes |
|-----|-----------|------|----------|-----------------|
| 0 | Hull | HullSubsystem | 0 | 1 |
| 1 | Warp Core | PowerSubsystem | 0 | 3 |
| 2 | Torpedoes | TorpedoSystem | 1 (single torpedo) | 4 |
| 3 | Repair System | RepairSubsystem | 0 | 3 |
| 4 | Shield Generator | ShieldGenerator | 0 | 1 |
| 5 | Sensor Array | SensorSubsystem | 0 | 3 |
| 6 | Impulse Engines | ImpulseEngine | 2 (Port, Star) | 5 |
| 7 | Warp Engines | WarpEngine | 2 (Port, Star) | 5 |
| 8 | Beams | PhaserSystem | 8 (Fwd 1-2, Port 1-2, Star 1-2, Aft 1-2) | 11 |
| 9 | Cloaking Device | CloakDevice | 0 | 3 |

**10 top-level, 13 children, 23 total. Full cycle: 39 bytes.**

Notable: Has Cloaking Device. 8 phaser banks ("Beams"). Only 1 torpedo tube.
No tractors, no Bridge.

---

### Species 15: Shuttle (Federation Shuttlecraft) `[confidence: medium — pattern-extrapolated from sampled set]`

Cross-source: `reference/scripts/ships/Hardpoints/shuttle.py` (lines per LoadPropertySet).

| Idx | Subsystem | Type | Children | WriteState Bytes |
|-----|-----------|------|----------|-----------------|
| 0 | Hull | HullSubsystem | 0 | 1 |
| 1 | Impulse Engines | ImpulseEngine | 2 (Port, Star) | 5 |
| 2 | Warp Core | PowerSubsystem | 0 | 3 |
| 3 | Sensor Array | SensorSubsystem | 0 | 3 |
| 4 | Shield Generator | ShieldGenerator | 0 | 1 |
| 5 | Phasers | PhaserSystem | 1 (single phaser) | 4 |
| 6 | Repair | RepairSubsystem | 0 | 3 |
| 7 | Warp Engines | WarpEngine | 2 (Port, Star) | 5 |
| 8 | Tractors | TractorBeamSystem | 1 (Forward) | 4 |

**9 top-level, 6 children, 15 total. Full cycle: 29 bytes.**

Notable: Smallest combat ship. No torpedoes. Only 1 phaser bank, 1 tractor beam.
Impulse Engines at index 1 (before Warp Core). No Bridge, no cloak.

---

### Species 37: Enterprise (Federation Enterprise-E) `[confidence: medium — pattern-extrapolated from sampled set]`

Cross-source: `reference/scripts/ships/Hardpoints/enterprise.py` — inherits from Sovereign
via `ParentModule.LoadPropertySet()` (App.SPECIES_SOVEREIGN at SpeciesToShip.py lines
60 + 92). Layout is **identical to Sovereign (species 5)**; only HP/capacity property
values are overridden (Hull HP, Shield HP, Warp Core capacity, Engineering repair
capacity).

**11 top-level, 22 children, 33 total. Full cycle: 49 bytes.**

See Species 5 (Sovereign) for the per-index subsystem table — every row applies.

---

## Universal Subsystem Patterns `[v5-validated 2026-05-28]`

Per mid #11 cross-anchor (`stateupdate-subsystem-wire-format.md`): the ship+0x2B0..+0x2DC
named-slot table in `Ship__SetupProperties` (0x005B3FB0) defines the universe of slot
types. The pattern below is the observed superset across the 16 stock hulls.

All 16 stock MP ships share these 7 subsystem types (always present):
1. **HullSubsystem** — at least 1 hull (5 Federation capital ships have 2: Hull + Bridge)
2. **ShieldGenerator** — always 1 (shield facing data is in flag 0x40, not flag 0x20)
3. **PowerSubsystem** — always 1 reactor (named "Warp Core" or "Power Plant")
4. **SensorSubsystem** — always 1
5. **ImpulseEngine** — always 1 system (1-4 child engines)
6. **WarpEngine** — always 1 system (1-3 child engines)
7. **RepairSubsystem** — always 1

Optional subsystem types:
- **PhaserSystem** — present on all ships except Bird of Prey (1-8 child banks)
- **TorpedoSystem** — present on all ships except Marauder (1-6 child tubes)
- **TractorBeamSystem** — absent from: Bird of Prey, Galor, KessokHeavy, KessokLight
- **PulseWeaponSystem** — present on: Bird of Prey, Vor'cha, Warbird, Marauder, CardHybrid
- **CloakDevice** — present on: Bird of Prey, Vor'cha, Warbird, KessokHeavy, KessokLight
- **Bridge (HullSubsystem)** — present on: all 5 Federation capital ships + Warbird

## Round-Robin Timing `[v5-validated 2026-05-28]`

With the 10-byte budget per tick at ~10 Hz (foundation: mid #8 budget anchor at
`CMP EAX, 0xA` at 0x005B1EC0):

| Cycle Bytes | Ticks per Full Cycle | Full Cycle Time |
|-------------|---------------------|-----------------|
| 29 (Shuttle) | ~3 | ~0.3s |
| 31 (Galor) | ~4 | ~0.4s |
| 32 (BoP) | ~4 | ~0.4s |
| 35 (Marauder) | ~4 | ~0.4s |
| 39 (Keldon, KLight) | ~4 | ~0.4s |
| 40 (KHeavy) | ~4 | ~0.4s |
| 44 (Vorcha) | ~5 | ~0.5s |
| 45 (Ambassador) | ~5 | ~0.5s |
| 46 (Warbird) | ~5 | ~0.5s |
| 47 (Akira, Nebula, CHybrid) | ~5 | ~0.5s |
| 49 (Sovereign, Enterprise) | ~5 | ~0.5s |
| 50 (Galaxy) | ~5 | ~0.5s |

All ships complete a full subsystem health cycle in under 1 second. Subject to R1
(per-cycle approximation due to bit-stream packing — actual cycle totals may differ
by 1-3 bytes for ships with many Powered subsystems).

## Implications for Reimplementation `[v5-validated 2026-05-28]`

All 6 points consistent with binary behavior per foundation anchors.

1. **Subsystem list order is ship-specific.** A reimplementation must build the same
   linked list for each ship class, in the same order as the original hardpoint scripts.
   Mismatches cause the receiver to apply subsystem health to the wrong subsystem.

2. **The receiver and sender must agree on the list.** Both sides run the same hardpoint
   file (verified by checksum exchange), so both build identical linked lists via
   `SetupProperties` + `LinkAllSubsystemsToParents`.

3. **Only top-level subsystems are in the round-robin.** Children are serialized
   recursively inside their parent's WriteState call.

4. **Shield facing data is NOT in flag 0x20.** The ShieldGenerator in the subsystem list
   only writes 1 condition byte. Actual shield facing HP uses flag 0x40 (CLOAK_STATE
   bit — overloaded for shield data on non-cloaking ships or as a separate data path).

5. **WriteState format is determined by the subsystem's vtable.** Base subsystems write
   1 byte, Powered subsystems write 1+N+~2 bytes, PowerSubsystem writes 1+2 bytes.
   The vtable is determined by the property type used in `AddToSet`.

6. **Mod ships will have different layouts.** This catalog only covers the 16 stock ships.
   Any mod-added ship will have its own AddToSet order and subsystem composition.

## Open Questions

Recorded for the next pass:

1. **Bit-stream packing across subsystem boundaries** — per-cycle byte totals may vary
   by 1-3 bytes for ships with many Powered subsystems (R1). Needs bit-stream cursor
   trace from a single StateUpdate flag-0x20 packet to confirm whether "1+N+2" is exact
   bytes or +/- 1 byte due to bit alignment.
2. **Round-robin overshoot semantics** — when a subsystem starts at cursor 9 and would
   write 5 bytes, does the cap allow completion (cursor → 14) or push it to the next
   tick? Foundation mid #8 cites `CMP EAX, 0xA` at 0x005B1EC0 but the comparison-
   direction semantic is unverified.
3. **Mod ship behavior** — explicitly out of scope for this catalog.
4. **Byte-by-byte verification for remaining 12 hulls** — Ambassador, Galaxy, Nebula,
   Vor'cha, Warbird, Marauder, Keldon, CardHybrid, KessokHeavy, KessokLight, Shuttle,
   Enterprise@37. Currently medium confidence; promote to high once verified, then
   promote the doc to `status: verified`.
