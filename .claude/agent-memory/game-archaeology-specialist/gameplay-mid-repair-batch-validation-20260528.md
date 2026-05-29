---
name: gameplay-mid-repair-batch
description: v5 batch validation of repair-system.md + repair-tractor-analysis.md (sibling pair). Wire-format and event-type corrections; tractor mechanics largely confirmed.
metadata:
  type: project
---

# Gameplay Mid Repair Batch — Validation 2026-05-28

Batch validation of TWO sibling docs:
- `docs/gameplay/repair-system.md` (849 lines, consolidated)
- `docs/gameplay/repair-tractor-analysis.md` (626 lines, original RE)

## Per-Doc Verdicts

- repair-system.md: `partial` (3 wire-format C, 2 event-label C, 1 RegisterHandlers Clar)
- repair-tractor-analysis.md: `verified` (all tractor claims pass; only inherited repair-event verdict needs alignment with corrected wire format)

## Session work in Ghidra

Created 7 functions that were previously undefined (no Ghidra fn body):
- 0x005652a0 RepairSubsystem::Update (631 bytes = 0x277, matches doc claim)
- 0x005658d0 HandleHitEvent (47 bytes)
- 0x00565a80 HandleRepairCannotBeCompleted (169 bytes)
- 0x00565b30 HandleAddToRepairList (27 bytes)
- 0x00565b50 HandleIncreasePriority (383 bytes)
- 0x00565cd0 HandleSetPlayer (85 bytes)
- 0x006a1150 HostEventHandler (229 bytes)
- 0x00582460 TractorBeamSystem::Update (40 bytes)

All saved to Ghidra DB.

## Confirmed Claims (both docs)

**Class hierarchy + sizes**:
- ShipSubsystem vtable 0x00892fc4 size >= 0x88 ✓
- PoweredSubsystem vtable 0x00892d98 size >= 0xA8 ✓
- RepairSubsystem vtable 0x00892e24 size 0xC0 ✓
- TractorBeamSystem vtable 0x00893794 ✓
- TractorBeamProjector vtable 0x008936f0 ✓

**Slot/offset layout** (cross-confirmed with power-system memo):
- RepairSubsystem at ship+0x2D8 ✓ (HandleSetPlayer reads `iVar1 + 0x2d8`)
- TractorBeamSystem at ship+0x2D4 ✓ (memo, not re-anchored here)
- RepairSubsystem +0xA8/+0xAC/+0xB0/+0xBC queue layout ✓
- TractorBeamSystem +0xF4 mode, +0xF8 totalMaxDamage, +0xFC forceUsed ✓
- ImpulseEngineSubsystem +0xA8 tractorPtr ✓ (FUN_00561230 reads `param_1 + 0xa8`)

**Function addresses**:
- 0x005652a0 Update ✓
- 0x00565520 AddSubsystem ✓ (FUN_00565520 decomp matches doc)
- 0x00565890 IsBeingRepaired ✓
- 0x00565900 AddToRepairList_MP ✓
- 0x00565980 HandleRepairCompleted ✓
- 0x00565a10 HandleSubsystemRebuilt ✓
- 0x00565a80 HandleRepairCannotBeCompleted ✓
- 0x00565b30 HandleAddToRepairList ✓
- 0x00565b50 HandleIncreasePriority ✓
- 0x00565cd0 HandleSetPlayer ✓
- 0x00565d40 RegisterHandlers ✓ (6 per-instance + 1 static, all string-anchored)
- 0x00565dd0 RegisterEventTypes ✓ (3 bindings)
- 0x00582460 TractorBeamSystem::Update ✓
- 0x00582280 SumProjectorMaxDamage ✓
- 0x005822d0 GetForceRatio ✓ (returns 0 if forceUsed<=0, else fU/fM)
- 0x00580f50 ComputeTractorForce ✓ (max_damage_dist/beam_dist clamped to 1.0)
- 0x0057f8c0 FireTick ✓ (6-mode switch, 0/1/2/3/4/5 → handlers, default no-op)
- 0x00561230 ComputeEffectiveMaxSpeed ✓ (multiplicative drag via FUN_005822d0)
- 0x006a1150 HostEventHandler ✓ (PUSHes 0x06, sends "NoMe", reliable msg+0x3a=1)

**Repair rate formula** (both docs cite identical formula):
- rawRepair = MaxRepairPoints × conditionPct × dt ✓
- divisor = min(queueCount, NumRepairTeams) ✓
- perSub = rawRepair / divisor ✓
- actualGain = perSub / RepairComplexity ✓
- Skip-but-not-consume-team for condition<=0 → posts ET_REPAIR_CANNOT_BE_COMPLETED ✓
- Full-repair check ratio >= 1.0 → posts ET_REPAIR_COMPLETED ✓
- "Process remaining queue beyond team count" pass for additional cannot-complete posts ✓
- Player-ship UI update via FUN_005512e0 ✓

**Tractor force formula** (repair-tractor-analysis):
- force = maxDamage × (sysCondPct × projCondPct) × distanceRatio × deltaTime ✓
- distanceRatio = min(1.0, maxDamageDistance/beamDistance) using DAT_0088b9c0 (double 1.0) ✓
- Optional target tracker (+0xF0) multiplier via FUN_0056c740 ✓

**Tractor 6 modes** — STRING-ANCHORED at 0x0095017c..0x00950218:
- TBS_HOLD (0) FUN_0057fcd0 ✓
- TBS_TOW (1) FUN_0057ff60 ✓
- TBS_PULL (2) FUN_00580590 ✓
- TBS_PUSH (3) FUN_00580740 ✓
- TBS_DOCK_STAGE_1 (4) FUN_0057ff60 (shared with TOW) ✓
- TBS_DOCK_STAGE_2 (5) FUN_00580910 ✓
- Default → no-op (returns input force) ✓

**Tractor speed drag** (multiplicative):
- ImpulseEngine reads tractor at +0xA8 → calls GetForceRatio → multiplies (1.0 - ratio) ✓
- 1.0 from `_DAT_00888860` (anchored 0x3F800000 = 1.0f) ✓
- Force ratio uses `_DAT_00888b54` (anchored 0x00000000 = 0.0f) as zero-check ✓
- DAT_008936e8 = 0x40400000 = 3.0f (TOW max-move-per-tick cap) — NEW anchor

**Tractor "no direct damage"** — DoDamage NOT in callees of any of 5 mode handlers ✓
- FUN_0057fcd0 callees: shape/vector math only
- FUN_0057ff60 callees: misc + parent ops
- FUN_00580590 callees: subset of HOLD
- FUN_00580740 callees: subset of HOLD
- FUN_00580910 callees: vector + TGEventManager_PostEvent + TGObjPtrEvent_Ctor (event-posting only)
- None call FUN_00593E50 (ProcessDamage) or DoDamage

**Event registration** (both docs):
- HostEventHandler (FUN_006a1150) BOUND to 3 event types via FUN_006db380 in MultiplayerGame_Ctor (0x0069e7d0+):
  - 0x008000DF (ET_ADD_TO_REPAIR_LIST) at 0x0069e7e8
  - 0x00800074 (ET_REPAIR_COMPLETED) at 0x0069e80d
  - 0x00800075 (ET_REPAIR_CANNOT_BE_COMPLETED) at 0x0069e82c
- All 3 routed to opcode 0x06 PythonEvent to "NoMe" group (0x008e5528 = "NoMe\0") with reliable flag ✓

**Repair → opcode 0x06 wire path** — VERIFIED via HostEventHandler decomp:
- alloc TGMessage (0x40 bytes via FUN_00717b70)
- TGBufferStream open 0x3FF buffer, vtable[0x34/4]=13 calls Serialize on the event
- msg type = 6 (opcode 0x06)
- msg+0x3A = 1 (reliable flag)
- TGWinsockNetwork_SendTGMessageToGroup(this, "NoMe", msg)

## CORRECTIONS

### repair-system.md

**C1 [HIGH] — Path 1 wire format factory ID** (lines 658, 663, 674):

Doc claims: "Factory: TGSubsystemEvent (0x0101), 17 bytes total" applied to ALL 3 event types (0x008000DF, 0x00800074, 0x00800075).

**ACTUAL** (byte-confirmed via Ghidra decomp):
- **0x008000DF (ET_ADD_TO_REPAIR_LIST)**: factory 0x0100 (base TGEvent), size 0x28, **16-byte wire payload** (per pythonevent-wire-format memo). Posted by AddToRepairList_MP (FUN_00565900) via TGAlloc(0x28) + FUN_006d5c00 (TGEvent ctor).
- **0x00800074 (ET_REPAIR_COMPLETED)**: factory 0x010C (TGObjPtrEvent), size 0x2C, **21-byte wire payload** with obj_ptr = subsystem TGObject ID. Posted by Update (FUN_005652a0) via TGAlloc(0x2C) + TGObjPtrEvent_Ctor.
- **0x00800075 (ET_REPAIR_CANNOT_BE_COMPLETED)**: factory 0x010C (TGObjPtrEvent), size 0x2C, **21-byte wire payload** with obj_ptr = subsystem TGObject ID. Same posting pattern as 0x00800074.

"TGSubsystemEvent (0x0101)" is the leaf #13 fabrication — not a real class. The repair system uses TWO different factories for its 3 wire events.

**C2 [MED] — Event label** (line 614):

Doc lists "0x00800070 | ET_SUBSYSTEM_DAMAGED | Internal only | Damage tracking".

**ACTUAL** — String at 0x00910784 is `ET_SUBSYSTEM_REBUILT`. The 0x800070 event is the PERIODIC SUBSYSTEM REBUILD tick scheduled in ShipSubsystem ctor (FUN_0056bde0) with period `0x358637bd` (= ~1e-6, indicating next-tick scheduling). RepairSubsystem binds HandleSubsystemRebuilt (FUN_00565a10) to this event (per-instance registration in RepairSubsystem::SetPlayer at 0x00565220).

**C3 [MED] — Per-instance handler registration MISSING from doc** (line 576 "7 Handlers" table):

Doc lists 7 handlers in RegisterHandlers (0x00565d40). **MISSING**: RepairSubsystem::SetPlayer (around 0x00565220) registers 4 ADDITIONAL per-instance handlers via FUN_006db380:
- ET_SUBSYSTEM_HIT (0x80006B) → s_RepairSubsystem__HandleHitEvent
- ET_REPAIR_COMPLETED (0x800074) → s_RepairSubsystem__HandleRepairCom
- ET_SUBSYSTEM_REBUILT (0x800070) → s_RepairSubsystem__HandleSubsystem
- ET_REPAIR_CANNOT_BE_COMPLETED (0x800075) → s_RepairSubsystem__HandleRepairCan

These bind incoming event-types-by-ID to the per-instance handlers. Total event-type registrations: 4 (in SetPlayer per instance) + 3 (in RegisterEventTypes static) = **7 distinct event-type-to-handler bindings**, not 3 as the doc shows.

**Clar [LOW] — RegisterEventTypes binding mechanism**:

Doc shows `FUN_006d92b0` as "per-instance event handlers" for 0x800076 and 0x008000DF. **CLARIFICATION**: FUN_006d92b0 registers the HANDLER NAME against EventManager (ECX=0x97f864) for per-CLASS routing. The actual per-instance binding happens via FUN_006db380 inside SetPlayer (one per RepairSubsystem instance). Both layers exist; the doc conflates them.

**Clar [LOW] — Event type override on opcode 0x0B** (lines 685-689):

Doc says "Event type override: 0 (preserve original type 0x008000DF)". **ACTUAL**: opcode 0x0B's site at 0x0069f3ae PUSHes 0x8000df, and GenericEventForward (FUN_0069fda0) overrides `puVar7[4] = param_2` when param_2 ≠ 0. So opcode 0x0B FORCES event type to 0x008000DF regardless of the wire payload's type field. The override is non-zero; the doc's wording is wrong but the effect is the same (events arrive as 0x008000DF locally).

**Clar [LOW] — AddSubsystem condition-check offset note** (line 213 in repair-tractor-analysis; line 247 in repair-system):

Doc comment says "subsystem+0x0C float field check". **ACTUAL**: The decompiler shows `param_2[0xc]`, which is `param_2 + 0xc*4 = param_2 + 0x30`. The layout tables in both docs correctly state condition at +0x30. The inline comment is using INDEX notation (×4) and is misleading. Suggest removing or rewriting.

### repair-tractor-analysis.md

This doc is mostly INHERITED into repair-system.md and is the cleaner of the two on the tractor side. Repair side requires the same 5 corrections as repair-system.md (factory + event label + missing registrations), but they apply to LESS surface area here (the tractor doc doesn't make a wire-format claim for the repair events).

**Clar [LOW] — Repair Queue Events table** (lines 257-263):

Table maps:
- 0x008000DF → "Wire Opcode 0x0B" (Host -> All)
- 0x00800076 → "Wire Opcode 0x11" (Client -> Host)

**ACTUAL**:
- 0x008000DF travels as opcode **0x06** (PythonEvent via HostEventHandler) when posted by HOST-auto-queue (AddToRepairList_MP after auto-add). Opcode 0x0B is the CLIENT->HOST manual-repair path (different sender).
- 0x00800076 travels as opcode 0x11 (RepairListPriority, GenericEventForward path). ✓

The table conflates the two transmission paths for 0x008000DF. Suggest splitting into two rows.

## Cross-doc reconciliation

Both docs share the same correct repair-rate formula, hierarchy, function table, and AddSubsystem semantics. The corrections to repair-system.md propagate to the SUMMARY sections of repair-tractor-analysis.md's "Part 4 - OpenBC Claims vs Binary Evidence" table only as far as adding the new evidence that the wire format claim differs between event types. No tractor-side claim needed correction.

## Suggested cascade

repair-system.md needs C1/C2/C3 applied + 2 Clar fixes. repair-tractor-analysis.md only needs the events-table split into two rows (one for 0x008000DF host-auto-path opcode 0x06, one for client-manual-path opcode 0x0B).

If a clean-room OpenBC repair spec exists (referenced at `../OpenBC/docs/repair-system.md`), C1 is HIGH PRIORITY for that spec — wire format is incorrect there.

## New anchors discovered (cascade to other docs)

- DAT_008936e8 = 3.0f (TractorBeamSystem TOW/DOCK_1 max-move-per-tick rate) — feed into tractor wire/timing tables.
- 0x008e5528 = "NoMe\0" string anchor (matches network family group-routing memos).
- ET_SUBSYSTEM_REBUILT (0x800070) — correct label string at 0x00910784. Multiple docs use the wrong "ET_SUBSYSTEM_DAMAGED" name; cascade-rename.
- RepairSubsystem::SetPlayer at 0x00565220 (was UNCATALOGUED). Doc cites HandleSetPlayer at 0x00565cd0 but the per-instance event registrations live in SetPlayer.
- FUN_006a1150 HostEventHandler bound to 3 repair event-types — promote naming MultiplayerGame__HostEventHandler.
- RepairSubsystem::SetPlayer instance handler bindings reference labels at 0x008e5008/0x008e5030/0x008e5058/0x008e4fd8 — same strings as RegisterHandlers but via per-instance registration path.

## OQs

1. What client-side code originally posts the local 0x008000DF event that gets WIRE-serialized as opcode 0x0B? AddToRepairList_MP only fires when called from the SP-only HandleAddToRepairList or from HandleHitEvent (auto-queue). The manual-Repair-button → opcode 0x0B path is currently undocumented to its source.
2. What is the wire format of the event payload for opcode 0x0B specifically? The doc's claim of TGCharEvent (0x105, 18 bytes) is unanchored — the sender's factory choice determines this. If only the SP-only HandleAddToRepairList exists, opcode 0x0B may be dead code in MP. Verify by searching for `0x0B` MP packet trace occurrences in stock-dedi traces.
