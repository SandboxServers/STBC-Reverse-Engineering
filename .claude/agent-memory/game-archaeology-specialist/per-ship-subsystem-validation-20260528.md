---
name: per-ship-subsystem-validation-20260528
description: Per-ship subsystem wire format catalog validation — sampled 4 ships byte-by-byte (Sovereign, Bird of Prey, Galor, Akira); doc structurally sound, no material wire-format corrections, two clarifications (Powered byte cycle ≈ N+3 because bit+byte ≈ ~2; AddToSet semantics confirm reparenting via type machinery)
metadata:
  type: project
---

# Per-Ship Subsystem Wire Format Validation — 2026-05-28

## Scope
Protocol family mid #12 — `docs/protocol/per-ship-subsystem-wire-format.md` (~250 claims). Largest protocol doc. Sampling validation strategy: 4 ships byte-by-byte (Sovereign, Bird of Prey, Galor, Akira); remaining 12 ships extrapolated via uniform structural pattern.

## Strategy that worked
- Cross-source corpus first: read all 4 hardpoint `.py` files + SpeciesToShip.py + WriteState formula doc.
- Anchor wire formula via foundation (Base/Powered/Power addresses already v5-validated in mid #11).
- Hand-derive cycle bytes for each sampled ship from `AddToSet` order + child counts → match doc table.
- Use `Ship__SetupProperties` decompile to confirm `ship+0x2B0..+0x2DC` named-slot table.
- Use AddToSet order to validate per-ship top-level subsystem list order.

## Per-ship cycle-byte math (recomputed from hardpoint .py + WriteState formulas)

| Ship | Top-Level | Computation | Doc | Match |
|------|-----------|-------------|-----|-------|
| Sovereign | 11 | 1+1+3+3+5+9+3+11+7+5+1 | 49 | ✓ |
| Bird of Prey | 10 | 1+1+3+5+4+4+5+3+3+3 | 32 | ✓ |
| Galor | 9 | 1+1+3+7+4+5+4+3+3 | 31 | ✓ |
| Akira | 11 | 1+1+3+3+5+11+5+9+3+5+1 | 47 | ✓ |

(Cycle-byte formula: Base subsystem = 1; Powered = 1+N children+2; Power = 1+0+2 — children always Base.)

## Per-ship AddToSet vs. doc top-level order — all 4 sampled match

Sovereign: doc Hull/Shield/Sensor/WarpCore/Impulse/Torpedoes/Repair/Phasers/Tractors/WarpEng/Bridge — matches sovereign.py order (Hull→Shield→Sensor→WarpCore→Impulse Engines→Torpedoes [children F1-F4/A1/A2/V1-4/D1-4/P/SImpulse/P/SWarp inline]→Repair→Phasers→Tractors→WarpEngines→Bridge). The "Probe Launcher" template is referenced but not registered → drops out of LoadPropertySet silently → no contribution.

Bird of Prey: doc order matches birdofprey.py exactly (Hull/Shield/WarpCore/DisruptorCannons/Torpedoes/ImpulseEngines/WarpEngines/Cloaking/Sensor/Engineering).

Galor: doc order matches galor.py LoadPropertySet (Hull/Shield/WarpCore/Compressors/Torpedoes/ImpulseEngines/WarpEngine/Repair/SensorArray; "Aft Beam" gets reparented to Compressors as 4th phaser child).

Akira: doc order matches akira.py LoadPropertySet (Hull/Shield/Sensor/WarpCore/ImpulseEng/Phasers/WarpEng/Torpedoes/Repair/Bridge/Tractors — Bridge at index 9 and Tractors at index 10 is doc's noted Ambassador-like reversed pattern; doc table for Akira shows Bridge=10/Tractors=9 but that's because "Engineering" (Repair) is at index 8, Tractors at 9, Bridge at 10 in the doc Akira table. Re-check: doc index 8=Engineering, 9=Tractors, 10=Bridge. Verify against AddToSet position — "Engineering" appears at AddToSet position 12, "Tractors" at 21, "Bridge" at 38. Order: Engineering→Tractors→Bridge ✓).

## Confirmed: ship+0x2B0..+0x2DC named slot table (mid #11 corrections still hold)

| Offset | Type ID | Slot | Confirmed via |
|--------|---------|------|---------------|
| +0x2B0 | 0x813E PowerSubsystem (reactor) | param_1 + 0x2b0 = uVar3 | Ship__SetupProperties case 0x813e |
| +0x2B4 | 0x8133 TorpedoSystem | param_1 + 0x2b4 = uVar3 (700d) | case 0x8133 |
| +0x2B8 | 0x812F WeaponSystem iVar4==1 PhaserSystem | param_1 + 0x2b8 = uVar3 | case 0x812f branch 1 |
| +0x2BC | 0x812F WeaponSystem iVar4==3 PulseWeaponSystem | param_1 + 700 (=0x2bc) | case 0x812f branch 3 |
| +0x2C0 | 0x8137 ShieldGenerator | param_1 + 0x2c0 = uVar3 | case 0x8137 |
| +0x2C4 | 0x8138 HullSubsystem | param_1 + 0x2c4 = uVar3 | case 0x8138 (NOT PowerSubsystem) |
| +0x2C8 | 0x8139 SensorSubsystem | param_1 + 0x2c8 = uVar3 | case 0x8139 |
| +0x2CC | 0x813C ImpulseEngineSubsystem | param_1 + 0x2cc = uVar3 | case 0x813c |
| +0x2D0 | 0x813B WarpEngineSubsystem | param_1 + 0x2d0 = uVar3 | case 0x813b |
| +0x2D4 | 0x812F WeaponSystem iVar4==4 TractorBeamSystem | param_1 + 0x2d4 = uVar3 | case 0x812f branch 4 |
| +0x2D8 | 0x813F RepairSubsystem | param_1 + 0x2d8 = uVar3 | case 0x813f |
| +0x2DC | 0x813A CloakDevice | param_1 + 0x2dc = uVar3 | case 0x813a |

Pulse Weapon slot at +0x2BC confirmed by `Ship__SetupProperties` case 0x812F branch iVar4==3 STM at param_1+700=0x2BC.
Tractor Beam slot at +0x2D4 confirmed by case 0x812F branch iVar4==4 STM at param_1+0x2D4.

## Material findings (no corrections)

- **Zero binary wire-format errors.** All 4 sampled ships derive cycle byte counts that match the doc summary table exactly.
- **AddToSet ordering hypothesis confirmed.** Doc claim that "top-level order = LoadPropertySet AddToSet order with children removed" matches all 4 sampled scripts.
- **Cycle byte formula uses approximation.** The "1+N+2" math for PoweredSubsystem treats `[bit hasData=1][byte powerPct]` as ~2 bytes. Actual wire is 1 bit + 1 byte; whether the bit packs into a partial byte depends on adjacent subsystem write boundaries. The 10-byte budget is a soft limit measured by stream cursor position (CMP EAX, 0xA at 0x005B1EC0), so this approximation is accurate per-tick.
- **`Probe Launcher`, `Shuttle Bay`, `Decoy launcher`, `Shuttle Bay 2`, viewscreens, camera, ship-property entries all fall out of the linked list silently** — they don't have registered templates that map to a top-level subsystem type in `Ship__SetupProperties`. Result: their `FindByName` returns NULL or their template's `GetTypeID` falls through the `default:` branch (no subsystem allocated). Doc's "0 children" / silent ignore behavior is correct.

## Open questions

1. Round-robin "10-byte cap" boundary semantics: when a subsystem starts at cursor 9, does the cap let it overshoot, or restart from this subsystem next tick? Foundation mid #8 cites `CMP EAX, 0xA` but doesn't decode the comparison direction.
2. Powered child bit packing across subsystem boundaries: needs bit-stream cursor trace from a single StateUpdate flag-0x20 packet to confirm "1+N+2" is exact bytes or +/- 1 byte due to bit alignment.
3. Mod ship validation: doc explicitly scopes to 16 stock ships; mod ship behavior is extrapolation.

## Pattern learned: sampling strategy validation
For large catalog docs with many parallel rows (per-ship, per-opcode), sample N=4 byte-by-byte and verify:
1. Structural formula holds (1+N+2 etc.)
2. Ordering algorithm holds (AddToSet)
3. Special cases catalog correct (which ships have Cloak/Pulse/Tractors/Bridge)
4. Foundation cross-anchors hold (slot offsets)
If all 4 sampled ships pass each check, extrapolation confidence is high (medium → high+1).
