---
name: gameplay-foundation-shield-system-validation-20260528
description: Gameplay foundation #2 validation. ZERO algorithm/wire corrections. 4 material corrections + 6 Clar. Recharge per-ship table fabricated.
metadata:
  type: project
---

# Gameplay Foundation #2 — Shield System Validation (2026-05-28)

## Verdict
**v5 status**: `partial` — rock-solid on core math, mislabeled bookkeeping fields, fabricated example table.

## What the doc gets RIGHT (byte-confirmed)

### Core algorithm — ALL CORRECT
- **FUN_0056a8d0 NormalToFacing** (max-component test): switch mapping `0→0, 1→2, 2→5, 3→1, 4→3, 5→4` matches decomp EXACTLY (axis-aligned cube face test, not dot product).
- **FUN_0056a690 GetShieldFacingFromRay**: ellipsoid-to-sphere normalization via piVar1[0x93/0x94/0x95] = ship NiNode+0x24C/+0x250/+0x254 semi-axes. Calls FUN_004570d0 (ray-sphere, verified — proper quadratic). Then FUN_0056a8d0.
- **FUN_00593c10 AreaEffectDamage**: 6-iteration loop with `fStack_28 * _DAT_0088bacc` (1/6 multiplier byte-confirmed `abaa2a3e` = 0.16666667). Calls FUN_0056a5c0 6 times per target. Overflow goes to hull via FUN_005afd70.
- **FUN_0056a5c0 SetCurShields**: clamp to `[0, property+0x60+facing*4]`. Storage at `this+0xA8+facing*4`. Floor = `_DAT_00888b54` (byte-confirmed = 0).
- **FUN_0056a420 BoostShield**: `(property+0x78+facing*4 * powerAmount) / (property+0x48 * (1/6))`. Cap at maxShields. Returns excess via `(newHP - max) / (rate / normalizedPower)`. Decomp matches doc pseudocode line-for-line.
- **FUN_0055f110 CloakShieldHandler**: param_2==1 → delayed event 0x00800077 scheduled with `_DAT_008e4e20` (1.0s). param_2!=1 → immediate event 0x00800079. State writes +0xB0 and +0xB4. ✓
- **FUN_0055f360 StartCloaking**: `+0xAD = 1` confirmed (single instruction).
- **FUN_004b1ff0 DamageHandler_Process**: shield gate `handler+0x20+0x18 != 0` confirmed. (Hull gate has OR of +0x9 AND +0x8 — doc only mentions +0x9. Minor Clar.)
- **FUN_005af010 WeaponHitHandler**: byte at `param_2+0x58` decides shield-vs-hull effect. Confirmed.
- **FUN_0056c350 IsSubsystemDestroyed**: recursive (self HP at +0x34 vs threshold, then iterates children). Confirmed.
- **FUN_0056a1f0**: registers `LAB_0056aae0` with string `"ShieldClass::HandleSetShieldState"`. ✓
- **FUN_0056bde0 ScheduleShieldEvents**: registers 5 timers — events 0x6d/0x6e use FUN_0056b960 (currentPower) for interval; 0x6f/0x70/0x71 use `0x358637bd` (~1e-6) for next-tick. Doc says "0x6d-0x71" — correct count, glossed over the 3-vs-2 detail.

### Constants — ALL byte-confirmed
| Address | Bytes | Value | Doc Says |
|---------|-------|-------|----------|
| 0x0088bacc | abaa2a3e | 1/6 | ✓ |
| 0x00888b54 | 00000000 | 0.0 | ✓ |
| 0x008e4e20 | 0000803f | 1.0 (ShieldDelay) | ✓ |
| 0x008e4e1c | 0000a040 | 5.0 (Cloak rate) | ✓ |
| 0x00892fc0 | c3f5a83e | 0.33 | ✓ |
| 0x00888b58 | bd378635 | ~9.99e-07 (epsilon) | ✓ |
| 0x00888860 | 0000803f | 1.0 | ✓ |
| 0x008887a8 | 0000003f | 0.5 | ✓ |

### Vtables — ALL confirmed
- ShieldGenerator vtable @ 0x00892f34 (xrefs from 0x0056a04b ctor + 0x0056a1ad dtor). ✓
- ShieldProperty vtable @ 0x00892fc4 (xrefs from 0x0056b9c6 ctor + 0x0056bbad dtor). ✓

## Corrections (material)

### C1 — `+0x48` is NOT `tickPhaseOffset` at runtime [HIGH PRIORITY]
**Doc says**: ShieldProperty +0x48 = "tickPhaseOffset (Random phase for staggered event scheduling)"

**Binary says**: At runtime, +0x48 holds **NormalPowerWanted / NormalPowerPerSecond** (read by `PoweredSubsystem_GetNormalPowerWanted` at 0x005623d0 as `*(float*)(iVar2 + 0x48)`). This is the SUBSYSTEM POWER REQUIREMENT, not a tick stagger.

**The confusion**: Ctor at 0x0056b970 line `param_1[0x12] = fVar2 * _DAT_00888dbc` does INITIALIZE +0x48 to a random value (`rand() * 0.33 * 3.05e-5`). But this is overwritten by hardpoint scripts when they set the power required. The doc captured the ctor-time meaning, missing the runtime semantics.

**BoostShield (0x0056a420) reads `property+0x48`** and uses it as `normalizedPower * 1/6`. This works because power-want is what `BoostShield` allocates per-facing.

**Impact**: doc's "tickPhaseOffset (Random phase for staggered event scheduling)" mislabels the field that drives `BoostShield`. OpenBC implementing per-facing budgets must label this `NormalPowerWanted`, not `tickPhaseOffset`.

### C2 — 0x0056ae10 is WriteState, not ReadStream [HIGH PRIORITY]
**Doc says**: "ShieldClass::ReadStream | Network deserialization (reads 6 maxShield values)"

**Binary says**: First line of FUN_0056ae10 is `PoweredSubsystem__WriteState(param_1, param_2)`. Loop iterates 0x60..0x78 (the maxShields array) calling vtable[0x54] (write float) for each. Then calls vtable[0xd8] (EndMarker / GetPos).

This is the WRITE path (server → wire). The `__ftol()` call converts each float to int for compact storage. Already cross-referenced in `server-side-computation-model.md:436`.

**Reads** would use a different vtable slot and call ReadFromStream. Not analyzed in this pass.

### C3 — Per-ship recharge table is FABRICATED [MEDIUM PRIORITY]
**Doc says**:
```
| Sovereign | All | 6000 | 15 |
| Galaxy | All | 5600 | 12 |
| Akira | All | 3600 | 11 |
| Warbird | All | 4000 | 8 |
| Vor'cha | Front | 24000 | 28 |
| Vor'cha | Others | varies | 2-9 |
```

**Actual hardpoints** (`reference/scripts/ships/Hardpoints/*.py`):
| Ship | Front MaxHP | Other MaxHP | All ChargePerSecond |
|------|-------------|-------------|---------------------|
| Sovereign | 11000 | 5500 (Rear/L/R) + 11000 (T/B) | 12 |
| Galaxy | 8000 | 4000 | 11 |
| Akira | 10000 | 5000 | 11 |
| Warbird | 4000 | 4000 | 8 ✓ (only match) |
| Vor'cha | 24000 ✓ | 6000/3500/3000/4500 | 28/9/2/2/2/2 |

Only Warbird matches the doc; Vor'cha front matches but doc says "2-9" for others (actuals are 2/2/2/2/9 — directionally OK but specifics are off).

The doc's table presents itself as factual ("Typical Recharge Values (from hardpoint scripts)") — should be replaced with verified Python-script values.

### C4 — IsShieldBreached threshold is 1.0, not 0 [LOW PRIORITY]
**Doc says** gate condition: `curShields[facing] == 0`

**Binary** (FUN_0056a620): returns NOT_BREACHED when `curShields[facing] >= 1.0 AND shieldDamaged[facing] == 0`. So "breached" means `curShields < 1.0 OR shieldDamaged != 0`.

The 1.0 threshold means a facing with 0.5 HP is treated as breached. Practical effect identical (full-strength shields absorb), but the wire condition matters for replication.

## Clarifications (non-blocking)

### Clar1 — Ctor has THREE float[6] arrays, not two
Doc shows curShields @ +0xA8 and shieldPercentage @ +0xC0. Ctor loop also writes a third float[6] at +0x130 (each = 1.0 init). Use unknown, but it sits between the watcher array (+0xDC, 7*0xC=0x54 bytes = ends at +0x130) and shieldDamaged (+0x14C). Also `overallWatcher` at +0x124 actually points to ESI+0xD8 (which is 4 bytes BEFORE the watcher block — a float written to 1.0).

### Clar2 — Random phase scale is product of TWO constants
Doc says ctor uses `0.33 * 3.05e-5` as single multiplier. Actual:
- `_DAT_00892fc0 = 0x3EA8F5C3 = 0.33`
- `_DAT_00888dbc = 0x38000100 = ~3.052e-5`
Combined product ≈ 1.007e-5. Doc value 1.0065e-5 is the right ballpark but the code uses two separate constants.

### Clar3 — DamageHandler_Process hull gate has TWO bytes
Doc gate: `handler+0x1C+0x9`. Actual code checks `(*(handler+0x1C+0x9) != 0) OR (*(handler+0x1C+0x8) != 0)`. Either byte being non-zero triggers the hull/subsystem path.

### Clar4 — HandleSetShieldState is in code-gap (CONFIRMED)
Address range 0x0056a230..0x0056aad0 (incl. LAB_0056aae0) is real code (registers BoostShield calls at 0x0056a2e6 and 0x0056a392 per xrefs to FUN_0056a420) but Ghidra hasn't promoted it to a function. Doc correctly flags this.

### Clar5 — ScheduleShieldEvents has TWO time sources
Events 0x6d/0x6e schedule via `FUN_0056b960(param_1)` = read `property+0x40` (currentPower) as the recurrence interval. Events 0x6f/0x70/0x71 use the constant `0x358637bd` (~1e-6) which essentially means "next tick". Doc bundles these into "additional periodic events" — true but glosses over the per-tick semantics.

### Clar6 — ProcessDamage at 0x00593E50 actual signature
Doc claims ProcessDamage "iterates the handler array (ship+0x128, count at ship+0x130)" — CONFIRMED. Decomp shows `*(int *)(param_1 + 0x130)` as loop count and `*(int *)(*(int *)(param_1 + 0x128) + uVar1 * 4)` as handler array. Then calls FUN_004b1ff0, FUN_00593ee0, FUN_00593f30. (Cross-doc: damage-system memo notes the notification gate is INSIDE FUN_00593f30, which doc doesn't mention.)

## Pre-anchors validated
- ShieldGenerator at ship+0x2C0 — NOT validated this pass (struct field is in PoweredSubsystem chain; protocol leaf #19 already byte-confirmed).
- Class ID 0x8137 — NOT validated this pass (requires NiRTTI factory lookup; protocol leaf #19 already anchored).
- WeaponHitHandler shield gate via flag `param_2+0x58 == 0` — CONFIRMED here (FUN_005af010).
- shieldScale 1.5f — NOT in shield-system.md (would be in damage-system; already validated there).
- Ray-ellipsoid test at 0x0056a690 — CONFIRMED.

## Open Questions
- **OQ1**: What sets ShieldProperty+0x48 (NormalPowerWanted) at runtime? Likely a SWIG setter accessible to hardpoint scripts (something like `SetNormalPowerWanted`). Not investigated this pass.
- **OQ2**: What is the third float[6] array at ShieldClass+0x130? Initialized to 1.0 per facing; unknown purpose.
- **OQ3**: ShieldClass+0xD8 single float (init 1.0) — purpose unknown. `overallWatcher` pointer at +0x124 points here.
- **OQ4**: HandleSetShieldState (in code-gap 0x0056a230..0x0056aad0) needs to be promoted to a function in Ghidra for proper analysis of the redistribution logic.

## Patterns / Lessons
- **Ctor + runtime semantics divergence**: ShieldProperty+0x48 was init'd to a random number by ctor but used as `NormalPowerWanted` at runtime. When the doc author looked only at ctor, they wrote "tickPhaseOffset". Always cross-check FUN_0056b970 (ctor) against `PoweredSubsystem_GetNormalPowerWanted` (consumer) before labeling a field.
- **Hardpoint script tables must be derived, not transcribed**: per-ship value tables in docs without script-anchored quotes drift from reality. The doc's `Sovereign | All | 6000 | 15` doesn't match any ship — looks invented from "round numbers we'd expect".
- **"ReadStream" suffix is a red flag for symmetric WriteState functions**: when the function calls WriteState as its first line and uses vtable slot 0x54 (write float), it's the write path. Read functions use different slots and don't call WriteState.
- **Code-gaps in handler regions are normal**: HandleSetShieldState at 0x0056aae0 is reachable code that Ghidra's auto-analyzer didn't promote. The doc correctly flagged this — pattern worth recording for other dispatcher handlers.

## v5 completeness scores (cited fns)
| Fn | Address | Effective Score | Notes |
|----|---------|----------------|-------|
| NormalToFacing | 0x0056a8d0 | 0.0 (max 89.0) | Leaf, 14 unrenamed magic ints (the switch cases) |
| BoostShield | 0x0056a420 | 5.87 (max 89.0) | Leaf, 2 globals unrenamed |
| AreaEffectDamage | 0x00593c10 | 0.0 (max 81.1) | Worker, 4 globals + 3 struct accesses unresolved |
| GetShieldFacingFromRay | 0x0056a690 | 0.0 (max 80.0) | Worker, 18 hungarian violations |

All four well below 50; doc-level naming work would lift these. Not blockers for the validation.
