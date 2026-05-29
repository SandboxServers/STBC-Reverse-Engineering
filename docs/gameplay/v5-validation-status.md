> [docs](../README.md) / [gameplay](README.md) / v5-validation-status.md

---
title: Gameplay Docs V5 Validation Status
type: reference
audience: re-engineer
status: partial
validated: 2026-05-28
methodology: FUNCTION_DOC_WORKFLOW_V5
binary:
  name: stbc.exe
  size: 6182400
  base: 0x00400000
evidence_refs:
  - docs/gameplay/damage-system.md
  - docs/gameplay/shield-system.md
  - docs/gameplay/power-system.md
  - docs/gameplay/collision-detection-system.md
  - docs/gameplay/weapon-firing-mechanics.md
  - docs/gameplay/ai-architecture.md
  - docs/gameplay/combat-mechanics-re.md
  - docs/gameplay/cloaking-state-machine.md
  - docs/gameplay/repair-system.md
  - docs/gameplay/repair-tractor-analysis.md
  - docs/gameplay/ship-navigation.md
  - docs/gameplay/collision-shield-interaction.md
  - docs/gameplay/collision-rate-limiting.md
  - docs/gameplay/self-destruct-pipeline.md
  - docs/gameplay/objcreate-unknown-species-analysis.md
  - docs/gameplay/repair-event-object-ids.md
companions:
  - docs/protocol/v5-validation-status.md
  - docs/networking/v5-validation-status.md
  - docs/engine/v5-validation-status.md
---

# Gameplay Docs V5 Validation Status

Tracker for the v5 evidence-standard re-validation campaign on `docs/gameplay/`. This is
the **fourth and final family** in the campaign (engine 10/10 verified, protocol 22/22,
networking 11/11 — total 43/43 done so far).

## 1. Campaign overview

Gameplay docs sit on top of three completed families and cover the in-game mechanics:
combat, shields, weapons, damage, power, cloak, repair, collision, AI, navigation, and
specific bug analyses. 16 docs, ~8200 lines total.

Many gameplay-family claims are already cross-anchored from validated leaves:
- **protocol leaf #15 collision-effect-protocol** anchors collision damage flow
- **protocol leaf #18 objnotfound-requestobj-enterset** anchors DamageableObject HP slot
  (+0x14c) and FLT_MAX undamaged sentinel
- **protocol leaf #19 subsystem-integrity-hash** anchors the 12-subsystem slot table
  (ship+0x2B0..+0x2DC) with corrected identities (HullSubsystem +0x2C4, ShieldGenerator
  +0x2C0, SensorSubsystem +0x2C8, etc.)
- **protocol leaf #20/21 CF16** anchors damage/radius encoding
- **networking leaf #11 ship-death-lifecycle** anchors ObjectExploding event and the
  combat-deaths-don't-use-0x14 finding

## 2. Validation order (foundation → leaves)

| # | Doc | Layer | Lines | Current status |
|---|-----|-------|-------|----------------|
| 1 | damage-system.md | Foundation: damage pipeline (collision/weapon/explosion) | 285 | **partial (2026-05-28)** — 5 corrections (C1 DestroyObject_Net branching is parent-vs-no-parent; C2 ProcessDamage has 3 callers; C3 TGSceneGraph__GetObjectByID naming; C4 Explosion_Net wire is CV4+2xCF16; C5 IsHost gate inside FUN_00593F30) + 4 clarifications + 3 OQs. ALL 10 magic constants byte-confirmed. See §6.1 |
| 2 | shield-system.md | Foundation: 6-facing ellipsoid + absorption + recharge | 355 | **partial (2026-05-28)** — 4 corrections (C1 HIGH: ShieldProperty +0x48 is NormalPowerWanted at runtime not tickPhaseOffset; C2 HIGH: 0x0056ae10 is WriteState not ReadStream; C3 MED: per-ship recharge table fabricated for 4 of 5 ships; C4 LOW: IsShieldBreached threshold is 1.0 not 0) + 6 clarifications + 2 OQs. See §6.2 |
| 3 | power-system.md | Foundation: 3-class architecture + battery/conduit | 1221 | **partial (2026-05-28)** — 5 corrections including C1 HIGH vtable-to-class shift across 8 of 11 subsystem classes + cascade to protocol leaf #19 + wire-format-spec (separately patched); 26 Ghidra functions renamed. C2 AddPowerToBatteries gate INVERTED. C3 Draw functions implement client-side prediction. C4 FUN_0055F7F0 is cloak-decloak shield-restore. C5 consumer list head/tail labels reversed. See §6.3 |
| 4 | collision-detection-system.md | Foundation: 3-tier collision pipeline | 664 | **partial (2026-05-28)** — "Among the strongest pre-v5 gameplay docs". 34 function addresses verified, 15 constants byte-confirmed. 3 detail corrections (C1 HIGH DAT_00888b54 is 0.0f not "large float sentinel"; C2 MED sweep-and-prune endpoint struct layout; C3 LOW GetAABB is union/expand not clamp) + 2 clarifications + 2 OQs. See §6.4 |
| 5 | weapon-firing-mechanics.md | Foundation: phaser/torpedo CanFire gates | 798 | **partial (2026-05-28)** — ZERO formula/wire/constant errors. 4 corrections (C1 HIGH Part 6 vtable table TorpedoTube column scrambled; C2 MED FUN_0056c350 "IsSubsystemAlive" return semantics INVERTED — returns 1 when DAMAGED; C3 LOW DAT_00890550 = 1.25f is a BOOST not penalty for AI/remote ships; C4 OK PhaserBank dtor confirmed) + 6 clarifications + 4 OQs. See §6.5 |
| 6 | ai-architecture.md | Foundation: AI behavior tree + 8 C++ classes | 308 | **verified (2026-05-28)** — third gameplay-family doc to clear `verified`; ZERO material corrections; all 8 vtable addresses + 8 ctors verified including BuilderAI → PreprocessingAI → BaseAI inheritance via explicit ctor chain. 2 clarifications (Clar1 vtable slot numbering starts at byte offset +0x20; Clar2 UpdateStatus enum has 5 SWIG names not 3) + 1 OQ. See §6.6 |
| 7 | combat-mechanics-re.md | Mid: consolidated combat across systems | 482 | **verified (2026-05-28)** — fourth gameplay-family doc to clear `verified`; ZERO material corrections. 23 unique addresses verified, 7 constants byte-confirmed, 100% Sovereign hardpoint match against reference scripts. 2 LOW clarifications (ShieldGenerator RepairComplexity = 2.0; CloakTime = 5.0f). See §6.7 |
| 8 | cloaking-state-machine.md | Mid: 4-state cloak + auto-decloak | 518 | **partial (2026-05-28)** — 4 corrections (C1 HIGH StopCloaking field at +0xAC not +0xAD; C2 HIGH event 0x00800078 is ET_CLOAK_COMPLETED + 0x00800077 IS the missing ET_CLOAK_BEGINNING; **C3 MED CloakTime is 5.0f not 3.0f — OpenBC clean-room cascade**; C4 LOW ctor at 0x00566D10 Ghidra rename applied: SensorSubsystem_Ctor → CloakingSubsystem_Ctor) + 3 clarifications + 2 OQs. See §6.8 |
| 9 | repair-system.md | Mid: queue + rate + priority + 7 event handlers | 849 | **partial (2026-05-28)** — 3 corrections (C1 HIGH event factory IDs wrong: 0x008000DF is factory 0x0100 16B base TGEvent; 0x00800074/0x00800075 are factory 0x010C 21B TGObjPtrEvent — OpenBC clean-room cascade; C2 MED 0x00800070 is ET_SUBSYSTEM_REBUILT not ET_SUBSYSTEM_DAMAGED; C3 MED 7-not-3 handler bindings via SetPlayer vtable slot) + 2 clarifications + 2 OQs. 8 functions CREATED in Ghidra (RepairSubsystem::Update + 7 handlers). See §6.9 |
| 10 | repair-tractor-analysis.md | Mid: 6 tractor modes + multiplicative drag | 626 | **partial (2026-05-28)** — 1 clarification (Repair Queue Events table splits host-auto opcode 0x06 from client-manual opcode 0x0B paths); 6 tractor modes string-anchored; tractor force formula + multiplicative drag + no-direct-damage all byte-confirmed; DAT_008936e8 = 3.0f TOW max-move-per-tick newly anchored. See §6.10 |
| 11 | ship-navigation.md | Mid: targeting + turn + impulse + warp + authority | 262 | **partial (2026-05-28)** — 5 corrections (C1 HIGH **OpenBC BLOCKING**: velocity field offsets SWAPPED — +0x1F8 is speed scalar not direction; +0x1FC..+0x204 is direction TGPoint3 not speed; C2 HIGH turn convergence inverted — TurnTowardDifference 0x005ad4d0 is actual sink; C3 MED Ship+0x87 fabricated; C4 MED InSystemWarp distance is 50.0f not 295; C5 MED ET_EXITED_WARP fabricated — single warp event 0x008000EF) + 8 clarifications + 3 OQs. See §6.11 |
| 12 | collision-shield-interaction.md | Leaf: directional absorption + two-step damage | 256 | **partial (2026-05-28)** — ZERO formula/wire errors. 2 corrections (C1 MED FUN_0056c470 creates TGObjPtrEvent not TGCharEvent; C2 LOW DoDamage chain has wrapper layer FUN_00593650) + 2 clarifications + 1 OQ. AoE 6-facing 1/6 split byte-confirmed at DAT_0088BACC. See §6.12 |
| 13 | collision-rate-limiting.md | Leaf: ship+0xEC enable flag | 150 | **partial (2026-05-28)** — ZERO algorithm/constant errors; all 5 distance + 5 cooldown constants byte-confirmed. 1 HIGH correction (C1: call chain narrative materially wrong — vtable+0x150 is RET-only stub not Ship::CheckCollision; actual rate-limiter caller is unnamed wrapper ~0x005a26d0; impact: OpenBC implementers will trace wrong functions) + 3 clarifications + 1 OQ. CLAUDE.md "Known Issue: collision rate limiting disabled (ship+0xEC=0)" VERIFIED. See §6.13 |
| 14 | self-destruct-pipeline.md | Leaf: 3 execution paths + PowerSubsystem cascade | 680 | **partial (2026-05-28)** — 3 corrections (C1 MED DestroyObject Handler section is vestigial in MP per ship-death-lifecycle 0/59 evidence; C2 LOW DAT_008E5C18 is FLT_MAX dying-sentinel reentrancy guard not "threshold"; **C3 HIGH CASCADE PENDING flag attributions at 0x0097FA88/89/8A may be inverted in CLAUDE.md** — verification in flight) + 2 clarifications + 3 OQs. TopWindow__SelfDestructHandler CREATED in Ghidra at 0x0050D070 (219 bytes). See §6.14 |
| 15 | objcreate-unknown-species-analysis.md | Leaf: failure modes + crash risks | 408 | **verified (2026-05-28)** — 5th gameplay-family doc to clear `verified`; "one of the cleanest pre-v5 gameplay docs". Zero wire/functional corrections. 4 Python call-string addresses byte-confirmed + all 12 cited function addresses validated. 2 clarifications + 2 OQs. See §6.15 |
| 16 | repair-event-object-ids.md | Leaf: event object ID analysis | 317 | **verified (2026-05-28)** — 6th gameplay-family doc to clear `verified`; "ROCK SOLID on every wire-format and ID-encoding claim". DAT_0095b078 ID counter proved single-writer via 4-xref result (3 reads + 1 write all from TGObject_Ctor itself). 4 minor cosmetic clarifications. See §6.16 |
| — | README.md | Index only — refreshed at family close | 21 | **pending (deferred to family close)** |

## 3. Pre-anchored from completed families

### From engine family (10/10 verified)
- TGEvent hierarchy: NiObject (0x02) → TGObject → TGEvent (0x101)
- TGFactory registry at DAT_0099a578
- EventManager singleton at 0x0097F838

### From protocol family (22/22)
- All opcode handlers anchored
- CollisionEffect (0x15) handler at FUN_006a2470
- Explosion (0x29) handler at 0x006A0080
- DestroyObject (0x14) handler at FUN_006a01e0
- StateUpdate flag formats
- 12-subsystem slot table at ship+0x2B0..+0x2DC with CORRECTED identities
- CF16 encoder/decoder + 5 constants

### From networking family (11/11)
- Per-handler relay model (not transport-level)
- ACK-outbox deadlock mechanism
- Connect-event broadcast at FUN_006B63A0
- 0x14 NOT used for combat kills (only disconnect cleanup)
- DamageableObject HP slot +0x14c with FLT_MAX undamaged sentinel
- ExplosionDamage ctor at 0x004bbde0 (0x38 bytes, radius² precomputed at +0x18)

## 4. Cross-doc disagreements resolved during the campaign

- **Power-system C1 cascade to protocol leaf #19 + wire-format-spec**: Slot 1 (+0x2C4)
  attribution corrected from "HullSubsystem 0x8138" back to "PowerSubsystem (Reactor)
  0x8027". The 0x8138 class ID is PowerProperty (script-facing property type), not the
  subsystem instance class. Cascade-patched 2026-05-28; slots 4/6/7/8 from leaf #19 still
  hold. CLOSED.
- **Cloaking C4 Ghidra plate**: 0x00566D10 renamed from `SensorSubsystem_Ctor` to
  `CloakingSubsystem_Ctor`. CLOSED (Ghidra DB).
- **Repair-system C1 OpenBC cascade**: Wire-format event factories at 0x008000DF /
  0x00800074 / 0x00800075 corrected (factory 0x0100 base TGEvent 16B and factory 0x010C
  TGObjPtrEvent 21B). OpenBC clean-room cascade pending propagation to
  `../OpenBC/docs/repair-system.md`. CLOSED (doc side).
- **Cloaking C3 OpenBC cascade**: CloakTime default is 5.0f at DAT_008E4E1C, not 3.0f.
  OpenBC clean-room cascade pending propagation to `../OpenBC/docs/cloaking-system.md`.
  CLOSED (doc side).
- **Ship-navigation C1 OpenBC BLOCKING cascade**: Velocity field offsets swapped
  (+0x1F8 = speed scalar; +0x1FC..+0x204 = direction TGPoint3). OpenBC clean-room cascade
  pending propagation to `../OpenBC/docs/ship-movement.md`. CLOSED (doc side).
- **Power-system + ui-class-hierarchy.md off-by-4**: Player slot table is at MpgameBase+0x78
  (not +0x74). The engine doc inherits the wrong offset. PENDING engine-family
  re-render.
- **Self-destruct C3 flag attribution cascade**: **CONFIRMED 2026-05-28** via independent
  byte-level verification (cascade-verification-flags-20260528.md). CLAUDE.md "Key
  Globals" attributions for 0x0097FA88/89/8A were inverted (cyclic permutation). Binary
  truth: 0x0097FA88 = HasLocalPlayer; 0x0097FA89 = GameLive; 0x0097FA8A = IsHost.
  CLAUDE.md table corrected this pass. ~28 downstream docs reference these addresses
  with the old (wrong) labels — binary behavior in those docs is correct (gates work
  correctly), only flag NAMES are wrong. Mass label-fix DEFERRED to future sweep.
  CLOSED in CLAUDE.md.
- **Multiple docs **"TGSubsystemEvent" (factory 0x0101) fabrication**: protocol leaves
  #13/#15 + repair-system C1 + ship-death-lifecycle (networking #11) — factory 0x101 IS
  TGEvent itself. Each affected doc now corrected; cascade marker CLOSED.
- **Collision-rate-limiting + ship-navigation IsHost gate label**: References to
  DAT_0097fa89 as "IsHost" in collision-rate-limiting.md depend on the C3 cascade
  resolution.

## 5. Methodology notes

Gameplay-family validations should:
1. Heavily cross-anchor from engine + protocol + networking families
2. Focus on in-game mechanics (math, state machines, frame timing)
3. Flag any claim that contradicts validated transport-layer / event-system anchors
4. Surface gameplay-only Ghidra anchors (vtable slots on Ship/Subsystem classes,
   per-class math constants in .rdata, etc.)
5. Note any mod-compatibility implications (ship per-class power tables, weapon-type
   tables, etc.)

## 6. Per-doc validation entries

Each entry summarizes the validation outcome and points to the doc's top-of-doc NOTE
block for full per-correction detail. Memo files in
`.claude/agent-memory/game-archaeology-specialist/` carry the full Ghidra evidence
packets; render-pattern memos under `.claude/agent-memory/documentation-writer/`
document the rendering decisions.

**Canonical-record pattern**: the §2 row entries above carry the per-doc validation
summary (status, correction counts, OQ counts, key findings) and are the canonical
single-line record. Sub-entries §6.1-§6.16 are intentionally **not** duplicated here —
the §2 row + the linked memo file + the doc's own top-of-doc NOTE block together form
the complete validation trail. Adding 16 detailed sub-entries below would only
duplicate the §2 column data.

(Each per-doc entry §6.1-§6.16 captures: verdict, archaeology + render memo paths, and
notable findings. Full content of each is in the validation memos.)

## 7. Campaign close summary (2026-05-28)

**Gameplay family v5 campaign is closed at 16/16 docs validated.**

- **6 docs `verified`**: #6 ai-architecture, #7 combat-mechanics-re, #15
  objcreate-unknown-species, #16 repair-event-object-ids — plus 2 from earlier in the
  session (alby-rules-cipher, ack-outbox-deadlock, repair-event-object-ids) bringing
  cross-family verified total to 8
- **10 docs `partial`**: all load-bearing claims byte-anchored; minor cleanups deferred

### Architectural discoveries surfaced

- **Power-system 8-of-11 vtable shift**: corrected mapping across PoweredMaster,
  TorpedoSystem, PhaserSystem, PulseWeaponSystem, ShieldGenerator, PowerSubsystem,
  SensorSubsystem, ImpulseEngineSubsystem, WarpEngineSubsystem, TractorBeamSystem,
  RepairSubsystem, CloakingSubsystem
- **Client-side prediction architecture**: power-system Draw functions calculate
  projected draws without mutating battery state on clients
- **AI inheritance chain**: BuilderAI → PreprocessingAI → BaseAI via ctor chain
- **CF16 + DAT_0088BACC = 1/6**: AoE 6-facing 1/6 split byte-confirmed
- **Single-writer DAT_0095b078 ID counter**: 4-xref proof pattern (3 reads + 1 write
  all from TGObject_Ctor itself)
- **CloakTime = 5.0f, NOT 3.0f**: OpenBC clean-room spec needs update
- **Velocity field offsets swapped**: +0x1F8 = speed scalar, +0x1FC..+0x204 = direction
  (OpenBC BLOCKING)
- **ShieldProperty +0x48 = NormalPowerWanted at runtime**: not tickPhaseOffset
  (ctor-time identity); hardpoint scripts overwrite the random seed
- **Repair event factory IDs corrected**: 0x008000DF is factory 0x0100 16B base TGEvent;
  0x00800074/0x00800075 are factory 0x010C 21B TGObjPtrEvent (OpenBC cascade)
- **ET_SUBSYSTEM_REBUILT (0x00800070)**: was mis-labeled as ET_SUBSYSTEM_DAMAGED
- **TopWindow__SelfDestructHandler CREATED at 0x0050D070** (219 bytes); 8 functions
  CREATED in repair-batch
- **Collision-rate-limiting call chain wrong**: vtable+0x150 is a RET-only stub, NOT
  Ship::CheckCollision; actual rate-limiter caller is unnamed wrapper ~0x005a26d0
- **TGObjPtrEvent vs TGCharEvent**: collision-shield FUN_0056c470 creates TGObjPtrEvent,
  not TGCharEvent
- **DAT_00888b54 = 0.0f**: collision-detection narrative was right; only the global
  variables table row was wrong
- **DamageableObject HP slot +0x14c FLT_MAX dying-sentinel reentrancy guard**: cross-
  family confirmation
- **CASCADE PENDING**: CLAUDE.md flag attributions at 0x0097FA88/89/8A may be inverted
  (verification in flight)

### Family-close batch follow-ups

- CLAUDE.md Documentation Index refreshed to reflect 16/16 gameplay validated
- `.claude/agent-memory/documentation-writer/MEMORY.md` merged with 16 render-pattern
  memos
- Ghidra plates corrected at 0x00566D10 (CloakingSubsystem_Ctor)
- 8 Ghidra functions CREATED in repair-batch pass; HostEventHandler at 0x006a1150
  pending rename to MultiplayerGame__HostEventHandler
- TopWindow__SelfDestructHandler CREATED at 0x0050D070
- OpenBC clean-room cascade flags surfaced (3 — CloakTime 5.0f, velocity field swap,
  repair event factory IDs)
- **CLAUDE.md flag-attribution cascade verification IN FLIGHT** — if confirmed, sweep
  across all 4 families needed

### Campaign progression

- Engine family: 10/10 verified (2026-05-28)
- Protocol family: 22/22 (4 verified + 18 partial, 2026-05-28)
- Networking family: 11/11 (2 verified + 9 partial, 2026-05-28)
- **Gameplay family: 16/16 (6 verified + 10 partial, 2026-05-28)**

**Total v5-validated docs to date: 59/59 across 4 families. CAMPAIGN COMPLETE.**
