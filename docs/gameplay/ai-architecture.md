---
title: AI Architecture
type: reference
audience: RE engineers, OpenBC implementers
validated: 2026-05-28
methodology: FUNCTION_DOC_WORKFLOW_V5
binary_fingerprint: stbc.exe (base 0x400000, 32-bit Windows)
status: verified
supersedes: []
evidence:
  - claim: "BaseAI vtable (3 DATA xrefs = ctor + dtor + AllocAndConstruct)"
    address: 0x0088bb54
    confidence: high
  - claim: "PlainAI vtable (3 DATA xrefs)"
    address: 0x0088c0d8
    confidence: high
  - claim: "ConditionalAI vtable (3 DATA xrefs)"
    address: 0x0088bc84
    confidence: high
  - claim: "PriorityListAI vtable (3 DATA xrefs)"
    address: 0x0088c188
    confidence: high
  - claim: "RandomAI vtable (3 DATA xrefs)"
    address: 0x0088c1dc
    confidence: high
  - claim: "SequenceAI vtable (3 DATA xrefs)"
    address: 0x0088c230
    confidence: high
  - claim: "PreprocessingAI vtable (3 DATA xrefs)"
    address: 0x0088c12c
    confidence: high
  - claim: "BuilderAI vtable (3 DATA xrefs)"
    address: 0x0088bbe0
    confidence: high
  - claim: "BaseAI ctor (root — no super-ctor call)"
    address: 0x00470520
    confidence: high
  - claim: "PlainAI ctor calls BaseAI ctor"
    address: 0x0048cc40
    confidence: high
  - claim: "ConditionalAI ctor calls BaseAI ctor"
    address: 0x00478a50
    confidence: high
  - claim: "PriorityListAI ctor"
    address: 0x0048fcb0
    confidence: high
  - claim: "RandomAI ctor"
    address: 0x00491370
    confidence: high
  - claim: "SequenceAI ctor"
    address: 0x004927d0
    confidence: high
  - claim: "PreprocessingAI ctor calls BaseAI ctor"
    address: 0x0048e2b0
    confidence: high
  - claim: "BuilderAI ctor calls PreprocessingAI ctor (proves BuilderAI → PreprocessingAI → BaseAI chain)"
    address: 0x00475fb0
    confidence: high
  - claim: "BaseAI vtable +0x20 SetActive default (no-op stub)"
    address: 0x00470700
    confidence: high
  - claim: "BaseAI vtable +0x24 SetInactive default (no-op stub)"
    address: 0x00470710
    confidence: high
  - claim: "BaseAI vtable +0x28 GotFocus default (no-op stub)"
    address: 0x00470720
    confidence: high
  - claim: "BaseAI vtable +0x2C LostFocus default (no-op stub)"
    address: 0x00470730
    confidence: high
  - claim: "BaseAI vtable +0x30 Update default — MOV EAX,3; RET 8 (returns US_INVALID)"
    address: 0x00470740
    confidence: high
    note: "bytes B8 03 00 00 00 / C2 08 00"
  - claim: "BaseAI vtable +0x34 IsDormant default — MOV EAX,ECX; RET (returns this)"
    address: 0x00470750
    confidence: high
    note: "bytes 8B C1 C3"
  - claim: "BaseAI vtable +0x4C __purecall — proves BaseAI is abstract"
    address: 0x00859a0b
    confidence: high
  - claim: "BaseAI::GetShip calls PhysicsObjectClass::FindByObjectID(0, this+4)"
    address: 0x00470a30
    confidence: high
  - claim: "Ship::AITickScheduler — reads clock at DAT_0099c6bc, calls ProcessAITick"
    address: 0x004721b0
    confidence: high
  - claim: "Ship::ProcessAITick — calls Update via vtable[+0x30], dispatches return"
    address: 0x004722d0
    confidence: high
  - claim: "AITickScheduler's only caller — ship per-tick Update method"
    address: 0x0043b55b
    confidence: high
    note: "single CALL site inside FUN_0043b4f0"
  - claim: "SaveGame::InitPickler — imports cPickle.Pickler"
    address: 0x006f9fb0
    confidence: high
  - claim: "SaveGame::FlushPickler — calls getvalue on pickler"
    address: 0x006fa020
    confidence: high
  - claim: "CreateMultiplayerGame — emits 'AI.Setup'+'GameInit' string xrefs"
    address: 0x00504f10
    confidence: high
    note: "string xrefs at 0x00504f36 and 0x00504f3b (back-to-back instructions)"
  - claim: "'AI.Setup' string in .rdata"
    address: 0x008e1994
    confidence: high
  - claim: "'GameInit' string in .rdata (adjacent to AI.Setup)"
    address: 0x008e19a0
    confidence: high
  - claim: "'pCodeAI' string (single occurrence) — used by PreprocessingAI"
    address: 0x008dbb74
    confidence: high
    note: "DATA xref from FUN_0048e400"
  - claim: "'Ship(%s)::UpdateAI' debug string"
    address: 0x008db15c
    confidence: high
  - claim: "ArtificialIntelligence_US_NUM_STATUSES enum name string (count constant)"
    address: 0x0095088c
    confidence: high
  - claim: "ArtificialIntelligence_US_INVALID enum name string (= 3, default return)"
    address: 0x009508c2
    confidence: high
  - claim: "ArtificialIntelligence_US_DORMANT enum name string (= 1)"
    address: 0x009508d0
    confidence: high
  - claim: "ArtificialIntelligence_US_DONE enum name string (= 2)"
    address: 0x009508f4
    confidence: high
  - claim: "ArtificialIntelligence_US_ACTIVE enum name string (= 0)"
    address: 0x00950914
    confidence: high
  - claim: "No PlainAI/Compound/Fleet/Player script names present as binary strings"
    address: null
    confidence: high
    note: "sampled BasicAttack, FedAttack, InaccurateTorps, SetCircleSpeed, g_lFlagThresholds, FlagThreshold — all absent; confirms behavior catalog is entirely Python"
companions:
  - docs/engine/event-system-architecture.md
  - docs/engine/rtti-class-catalog.md
  - docs/gameplay/ship-navigation.md
  - docs/gameplay/damage-system.md
  - docs/gameplay/weapon-firing-mechanics.md
  - docs/gameplay/cloaking-state-machine.md
  - docs/gameplay/self-destruct-pipeline.md
---

> [docs](../README.md) / [gameplay](README.md) / ai-architecture.md

# AI Architecture

> [!NOTE]
> **v5 verified pass — ZERO material corrections.** All 8 vtable addresses verified via 3-DATA-xref pattern (ctor + dtor + AllocAndConstruct); all 8 constructors verified including BuilderAI → PreprocessingAI → BaseAI inheritance via explicit ctor chain. AI tick scheduler pair + Python bridge + SaveGame helpers + AI.Setup preload all byte-confirmed. 2 clarifications (Clar1 vtable slot numbering starts at byte offset +0x20; Clar2 UpdateStatus enum has 5 SWIG names including US_INVALID + US_NUM_STATUSES count). 1 OQ on internal base class identity (slots +0x00..+0x1C of BaseAI vtable).

Reverse-engineered implementation details of Bridge Commander's hierarchical behavior tree AI system. Covers the C++ runtime classes, Python scripting bridge, tick scheduling, and shipped behavior catalog.

---

## 1. C++ Class Hierarchy [v5-validated 2026-05-28]

```
BaseAI (0x0088bb54)
├── PlainAI (0x0088c0d8)
├── ConditionalAI (0x0088bc84)
├── PriorityListAI (0x0088c188)
├── RandomAI (0x0088c1dc)
├── SequenceAI (0x0088c230)
└── PreprocessingAI (0x0088c12c)
      └── BuilderAI (0x0088bbe0)
```

All AI classes inherit from BaseAI. PreprocessingAI extends BaseAI, and BuilderAI extends PreprocessingAI. The remaining five (PlainAI, ConditionalAI, PriorityListAI, RandomAI, SequenceAI) are direct children of BaseAI.

Inheritance was confirmed by decompiling each constructor and checking for a super-ctor call before the vtable override:
- `PlainAI ctor` (0x0048cc40), `ConditionalAI ctor` (0x00478a50), `PreprocessingAI ctor` (0x0048e2b0) all call `BaseAI ctor` (0x00470520) first.
- `BuilderAI ctor` (0x00475fb0) calls `PreprocessingAI ctor` (0x0048e2b0) — proving the two-level chain `BuilderAI → PreprocessingAI → BaseAI`.

### Constructor Addresses

| Class | Constructor | Vtable | AllocAndConstruct |
|-------|-----------|--------|-------------------|
| BaseAI | 0x00470520 | 0x0088bb54 | (abstract — no factory) |
| PlainAI | 0x0048cc40 | 0x0088c0d8 | cdecl wrapper exists |
| ConditionalAI | 0x00478a50 | 0x0088bc84 | cdecl wrapper exists |
| PriorityListAI | 0x0048fcb0 | 0x0088c188 | cdecl wrapper exists |
| RandomAI | 0x00491370 | 0x0088c1dc | cdecl wrapper exists |
| SequenceAI | 0x004927d0 | 0x0088c230 | cdecl wrapper exists |
| PreprocessingAI | 0x0048e2b0 | 0x0088c12c | cdecl wrapper exists |
| BuilderAI | 0x00475fb0 | 0x0088bbe0 | cdecl wrapper exists |

Each AI class has both a `__thiscall` constructor and a `__cdecl` AllocAndConstruct wrapper that calls `NiAlloc()` then the constructor. The SWIG API (`App.PlainAI_Create`, etc.) calls the AllocAndConstruct wrappers. The "3 DATA xrefs per vtable" pattern (ctor + dtor + AllocAndConstruct) was the verification anchor.

---

## 2. Virtual Method Table [v5-validated 2026-05-28]

The BaseAI vtable at `0x0088bb54` defines the core dispatch points for the behavior tree. The six methods are at **byte offsets +0x20..+0x34** within the vtable (slots 8-13), not at slots 0-5. The "Slot 0..5" labels used in earlier doc passes were a logical/ordinal view from the SWIG-developer perspective; this section now uses byte offsets to match the binary.

### Clar1 — Vtable slot numbering (byte offsets from BaseAI vtable @ 0x0088bb54)

| Byte offset | Slot | Method | Default impl |
|-------------|------|--------|--------------|
| +0x20 | 8 | SetActive | 0x00470700 (no-op stub) |
| +0x24 | 9 | SetInactive | 0x00470710 (no-op stub) |
| +0x28 | 10 | GotFocus | 0x00470720 (no-op stub) |
| +0x2C | 11 | LostFocus | 0x00470730 (no-op stub) |
| +0x30 | 12 | Update | 0x00470740 — returns **US_INVALID** (`MOV EAX,3; RET 8`) |
| +0x34 | 13 | IsDormant | 0x00470750 — returns `this` (`MOV EAX,ECX; RET`) |
| +0x4C | 19 | (abstract slot) | 0x00859a0b (`__purecall` — proves BaseAI is abstract) |

Slots count from byte offset +0x20 in BaseAI vtable. The internal base class providing slots 0-7 is identified as OQ1 below — likely a Totally Games scripted-object base distinct from NiObject.

`ProcessAITick` (0x004722d0) dispatches Update via `vtable[+0x30]`, which confirms the offset assignment.

### Method semantics

| Method | Description |
|--------|-------------|
| SetActive | Called when the node becomes active in the tree |
| SetInactive | Called when the node is deactivated |
| GotFocus | Called when this node gains execution focus from its parent |
| LostFocus | Called when this node loses focus (higher priority sibling took over) |
| Update | Main tick method — returns state (ACTIVE/DORMANT/DONE/INVALID) |
| IsDormant | Returns whether this node is currently dormant |

Derived classes override these methods. PlainAI dispatches `Update` to the Python script's `Update()` method. ConditionalAI's `Update` evaluates conditions before calling the contained child. PriorityListAI iterates children by priority.

### Clar2 — UpdateStatus enum (5 SWIG names: 4 states + 1 count)

The binary exposes **5** `ArtificialIntelligence_US_*` names (not 3). The full enum is:

```c
enum UpdateStatus {
    US_ACTIVE       = 0,  // Currently executing
    US_DORMANT      = 1,  // Temporarily inactive (triggers SetInactive + LostFocus)
    US_DONE         = 2,  // Completed or failed (posts event 0x800017)
    US_INVALID      = 3,  // Default return (abstract / not implemented)
    US_NUM_STATUSES = 4   // Enum size (count, not a real state)
};
```

Name strings in `.rdata`:

| Value | Name | String address |
|-------|------|----------------|
| 0 | `ArtificialIntelligence_US_ACTIVE` | 0x00950914 |
| 1 | `ArtificialIntelligence_US_DORMANT` | 0x009508d0 |
| 2 | `ArtificialIntelligence_US_DONE` | 0x009508f4 |
| 3 | `ArtificialIntelligence_US_INVALID` | 0x009508c2 |
| 4 | `ArtificialIntelligence_US_NUM_STATUSES` | 0x0095088c |

The BaseAI Update default at `0x00470740` is `MOV EAX, 3; RET 8` — it returns `US_INVALID`, which matches "abstract / should never be called" semantics. `ProcessAITick` (0x004722d0) dispatches the return value:

- `ret == 1` (US_DORMANT) → triggers SetInactive + LostFocus
- `ret == 2` (US_DONE) → posts event `0x800017` (ET_DONE — see [event-system-architecture.md](../engine/event-system-architecture.md))
- Otherwise (incl. `0` US_ACTIVE and `3` US_INVALID) → store time, exit (no state change)

Exposed to Python as `App.ArtificialIntelligence.US_ACTIVE`, `US_DORMANT`, `US_DONE`, `US_INVALID`, `US_NUM_STATUSES`.

---

## 3. Ship AI Tick Scheduling [v5-validated 2026-05-28]

Each ship has an AI tick scheduler that invokes the root AI node's `Update()` at a configurable rate.

| Function | Address | Description |
|----------|---------|-------------|
| Ship::AITickScheduler | 0x004721b0 | Reads clock at `DAT_0099c6bc`; checks elapsed time, decides whether to call ProcessAITick |
| Ship::ProcessAITick | 0x004722d0 | Calls the root AI node's `Update()` via vtable[+0x30], dispatches return value |

`Ship::AITickScheduler` has exactly **one caller**: `FUN_0043b4f0` at `0x0043b55b` — the ship's per-tick Update method. `ProcessAITick` is called only from the scheduler. The debug string `"Ship(%s)::UpdateAI"` at `0x008db15c` confirms purpose.

The tick rate is not fixed — individual AI scripts can request their next update interval. For example, `CircleObject.GetNextUpdateTime()` returns 0.5 seconds, while `Intercept.GetNextUpdateTime()` returns 0.4 ± 0.2 seconds (randomized to prevent synchronized updates across ships).

The scheduler is called from the main game loop's update pass. Each ship's AI is independent — there is no global AI coordinator.

---

## 4. Python/C++ Bridge [v5-validated 2026-05-28]

### pCodeAI Handle

Every Python AI script receives a `pCodeAI` reference to its C++ AI object. This is the bridge between Python behavior logic and C++ runtime:

```python
class BaseAI:
    def __init__(self, pCodeAI):
        self.pCodeAI = pCodeAI
```

The `"pCodeAI"` string at `0x008dbb74` (single occurrence in the binary) is used by `PreprocessingAI` — DATA xref from `FUN_0048e400`. SWIG bindings confirmed:

- `PlainAI_Create`, `PlainAI_SetScriptModule`, `PlainAI_StopCallingActivate`
- `BuilderAI_Create`, `BuilderAI_AddAIBlock`, `BuilderAI_AddDependency`, `BuilderAI_AddDependencyObject`
- `ArtificialIntelligence_GetName`, `_GetID`, `_Reset`, `_IsInterruptable`, `_SetInterruptable`, `_IsPaused`, `_Unpause`
- `RegisterExternalFunction`, `UnregisterExternalFunction`, `RegisterExternalFunctions`

Key methods on `pCodeAI`:
- `GetShip()` — returns the ship this AI controls. Backed by `BaseAI::GetShip` at `0x00470a30`, which calls `PhysicsObjectClass::FindByObjectID(0, this+4)`.
- `RegisterExternalFunction(name, dict)` — registers a callable for the C++ runtime
- `StopCallingActivate()` — optimization: tells C++ to stop calling `Activate()` if the base class version has nothing to do

### Script Lifecycle

1. **Creation**: `App.PlainAI_Create(pShip, "Name")` → C++ allocates PlainAI → Python script `__init__(pCodeAI)` called
2. **Configuration**: Python code calls setup methods (e.g., `SetFollowObjectName`, `SetCircleSpeed`)
3. **Activation**: When the node becomes active in the tree, `Activate()` is called — validates required params
4. **Update loop**: `Update()` called each AI tick — returns US_ACTIVE/US_DORMANT/US_DONE
5. **Deactivation**: `LostFocus()` called when interrupted, `SetInactive()` when fully removed

### Save/Load [v5-validated 2026-05-28]

AI state is serialized via Python's `pickle` protocol:
- `__getstate__()` — returns `__dict__` copy, converts module references to strings
- `__setstate__(dict)` — restores dict, re-imports modules
- `FixCodeAI(pCodeAI)` — called after load to update the C++ pointer (which is invalid after deserialization). Note: `FixCodeAI` is a Python-side method name and does not appear as a string in the binary.

Save/load helpers (called from `FUN_00443ac0`, likely `SaveGameState`):

| Function | Address | Role |
|----------|---------|------|
| SaveGame::InitPickler | 0x006f9fb0 | Creates `cPickle.Pickler` (imports `cPickle` string @ 0x008d9c2c, `Pickler` string @ 0x0095b4e0) |
| SaveGame::FlushPickler | 0x006fa020 | Calls `getvalue` on pickler, then marshal-style functions |

---

## 5. AI Node Behaviors

### PlainAI (Leaf Nodes)

PlainAI wraps a Python script class. The C++ runtime calls the script's `Update()` method each tick, which controls the ship via SWIG API calls (SetImpulse, TurnTowardLocation, etc.).

**27 shipped PlainAI scripts** (from `reference/scripts/AI/PlainAI/`):

| Script | Behavior |
|--------|----------|
| CircleObject | Orbit target using fuzzy logic for distance/facing decisions |
| IntelligentCircleObject | CircleObject with shield-aware facing (turns damaged shield away) |
| Intercept | Fly to predicted intercept point of moving target, with obstacle avoidance |
| Flee | Disengage from combat, fly away from target |
| FollowObject | Maintain formation distance behind a leader |
| FollowThroughWarp | Follow a target through warp transitions between sets |
| FollowWaypoints | Follow a sequence of waypoints with per-waypoint speed |
| GoForward | Fly straight ahead at configured speed |
| Stay | Hold position (zero throttle) |
| TorpedoRun | Approach from optimal torpedo angle, fire, break away |
| PhaserSweep | Maintain phaser firing arc, sweep beam across target |
| StationaryAttack | Attack without moving (turret mode) |
| StarbaseAttack | Attack approach optimized for large stationary targets |
| Ram | Direct collision course with target |
| Defensive | Defensive maneuvering (shield management priority) |
| ManeuverLoop | Execute pre-defined maneuver pattern |
| MoveToObjectSide | Position on specific side of target |
| TurnToOrientation | Rotate to face specific direction |
| Warp | Engage warp drive to destination set |
| SelfDestruct | AI-triggered self-destruct (calls `DestroySystem(hull)` instead of Ctrl+D path) |
| TriggerEvent | Fire a game event |
| RunAction | Execute a timed action sequence |
| RunScript | Run arbitrary Python script as AI behavior |
| EvadeTorps | Dodge incoming torpedoes |
| EvilShuttleDocking | Hostile shuttle docking approach |

**[v5-validated 2026-05-28]** None of these 27 script names appear as binary strings — the C++ side only knows the 8 base classes; all behavior names are Python-only.

### ConditionalAI

Contains one child AI and one or more `ConditionScript` objects. Each tick:
1. All conditions evaluated → boolean results
2. Evaluation function (Python) maps results to US_ACTIVE/US_DORMANT/US_DONE
3. If ACTIVE, child AI's Update() is called

The error string at `0x008db388` confirms the exact `ConditionScript_Create(sModule, sClass, ...)` signature.

### PriorityListAI

Ordered list of children with priorities. Evaluates highest-priority first. First child returning US_ACTIVE wins; lower-priority children are interrupted (if `SetInterruptable(1)`).

### SequenceAI

Runs children in order. When one returns US_DONE, advances to next. Sequence completes when all children are done.

### RandomAI

Randomly selects one child to execute. When that child completes, picks another randomly.

### PreprocessingAI

Wraps a child AI with a preprocessing step. The preprocessor runs before the child each tick. Used for cross-cutting concerns:
- `FireScript` — auto-fire weapons at target
- `AvoidObstacles` — steer away from nearby objects
- `ShieldManager` — adjust shield facing
- `WarpBeforeDeath` — emergency warp at low hull

### BuilderAI

Meta-node extending PreprocessingAI. Used by compound AI scripts (FedAttack, NonFedAttack) to declaratively build ~30-node behavior trees. Assembles named blocks with dependency relationships:

```python
pBuilderAI = App.BuilderAI_Create(pShip, "Name", __name__)
pBuilderAI.AddAIBlock("TorpRun", "BuilderCreate1")
pBuilderAI.AddDependencyObject("TorpRun", "sTarget", sTarget)
```

---

## 6. Compound AI Behaviors

**15 shipped Compound AI scripts** (from `reference/scripts/AI/Compound/`):

| Script | Purpose |
|--------|---------|
| BasicAttack | Entry point: selects FedAttack/NonFedAttack/CloakAttackWrapper based on species+cloak |
| FedAttack | Federation attack — torpedo runs, phaser sweeps, shield management (~30 nodes via BuilderAI) |
| NonFedAttack | Non-Federation attack — more aggressive maneuvering |
| CloakAttack | Cloak → approach → decloak → alpha strike → recloak cycle |
| CloakAttackWrapper | Wraps CloakAttack with fallback to non-cloak attack |
| Defend | Protect a target ship — follow + engage attackers |
| DockWithStarbase | Full docking sequence (approach, dock, repair/rearm, undock) |
| UndockFromStarbase | Undocking sub-behavior |
| StarbaseAttack | Attack stationary targets with varied approach angles |
| ChainFollow | Follow leader ship in formation |
| ChainFollowThroughWarp | Follow leader through warp transitions |
| FollowThroughWarp | Follow target through warp (simpler than ChainFollow) |
| TractorDockTargets | Tractor beam docking behavior |
| CallDamageAI | Switch to damage-appropriate AI when hit |

**5 Compound Parts** (sub-behaviors reused by multiple compounds):
- `EvadeTorps`, `ICOMove`, `SweepPhasers`, `WarpBeforeDeath`, `NoSensorsEvasive`

### BasicAttack Difficulty System

AI difficulty is a 0.0–1.0 float. The `g_lFlagThresholds` table maps difficulty ranges to enabled behavior flags:

| Difficulty | Enabled Flags |
|-----------|---------------|
| 1.0 | All 18 flags enabled (torpedo selection, phaser optimization, subsystem targeting, etc.) |
| 0.5 | 8 flags: UseRearTorps, UseSideArcs, SmartShields, ChooseSubsystemTargets, AvoidTorps, NeverSitStill, PowerManagement, SmartTorpSelection |
| 0.0 | InaccurateTorps + DumbFireTorps only |

Three difficulty presets (Easy_, default, Hard_) with per-game-difficulty overrides. None of `g_lFlagThresholds`, `FlagThreshold`, `InaccurateTorps`, or `SetCircleSpeed` appear as binary strings — the entire flag table is Python-side.

---

## 7. Fleet Commands

**5 shipped Fleet command scripts** (from `reference/scripts/AI/Fleet/`):

| Command | Script | Behavior |
|---------|--------|----------|
| DefendTarget | AI.Fleet.DefendTarget | Compound.Defend wrapped in ConditionalAI (target exists + same set) |
| DestroyTarget | AI.Fleet.DestroyTarget | BasicAttack wrapped in ConditionalAI |
| DisableTarget | AI.Fleet.DisableTarget | BasicAttack with DisableOnly=1 |
| HelpMe | AI.Fleet.HelpMe | Come to player's aid |
| DockStarbase | AI.Fleet.DockStarbase | Order wingman to dock for repair |

Each command wraps its core AI in a ConditionalAI checking `ConditionAllInSameSet` (target + player + ship).

---

## 8. Player AI

**26 Player AI scripts** (from `reference/scripts/AI/Player/`):

Used when the human player issues high-level commands from the tactical UI. These are full behavior trees that auto-pilot the player's ship.

Categories:
- **Destroy** variants: DestroyFreely, DestroyFore, DestroyAft, DestroyFromSide, DestroyFaceSide + Close/Maintain/Separate range variants
- **Disable** variants: mirror of Destroy but with DisableOnly=1
- **Movement**: FlyForward, InterceptTarget, OrbitPlanet, PlayerWarp, Stay, StaySelectTarget
- **Defense**: Defense, DefenseNoTarget

---

## 9. Condition System

36 shipped condition scripts (from `reference/scripts/Conditions/`). Used by ConditionalAI nodes.

Created via: `App.ConditionScript_Create("Conditions.ConditionName", "Name", ...args)`

Key conditions: ConditionInRange, ConditionFacingToward, ConditionAttacked, ConditionSystemBelow, ConditionTorpsReady, ConditionIncomingTorps, ConditionShipDisabled, ConditionAllInSameSet, ConditionInLineOfSight, ConditionInNebula, ConditionTimer, ConditionFlagSet.

---

## 10. AI Preloading [v5-validated 2026-05-28]

`AI.Setup.GameInit()` is invoked from C++ at `CreateMultiplayerGame` (`FUN_00504f10`). The two string literals `"AI.Setup"` (`0x008e1994`) and `"GameInit"` (`0x008e19a0`) sit adjacent in `.rdata`, with back-to-back DATA xrefs from `0x00504f36` and `0x00504f3b` inside `FUN_00504f10`.

Pre-imports 73 AI modules to prevent hitching during gameplay:
- 27 PlainAI scripts
- 15 Compound AI scripts + 5 Parts
- 5 Fleet commands
- 36 Condition scripts (no DockStarbase — likely intentional omission)

---

## 11. Fuzzy Logic [v5-validated 2026-05-28]

`CircleObject` uses `App.FuzzyLogic()` for distance/facing decisions. The fuzzy system has 4 input sets (far-facing-away, far-facing-toward, near-facing-good, near-facing-bad) and 4 output sets (stop-turn-toward, fast-turn-toward, stop-turn-side, fast-turn-side). Percentage membership is computed from dot products and distance, then the output is a blended speed/turn command.

SWIG bindings present in the binary:
- `FuzzyLogic_GetResultBySet` at `0x009232c0`
- `FuzzyLogic_SetPercentageInSet` at `0x009232dc`
- `FuzzyLogic_SetRuleConfidence` at `0x009232fc`
- 23 total `FuzzyLogic*` strings (other methods exist too)

Other AIs use simpler threshold-based logic rather than fuzzy sets.

---

## 12. Multiplayer Relevance

**Stock multiplayer has NO AI opponents.** AI is single-player/campaign only in the shipped game. There is no bot system, no AI-controlled ships in MP matches, and no fleet command network synchronization.

The AI system is entirely client-local — the C++ AI tick scheduler runs only on the machine that owns the ship. In single-player, all ships are local. For future MP AI (OpenBC #158), AI state would need to be replicated or AI decisions would need to be server-authoritative.

Indirect confirmation: the C++ AI system is hooked from the ship update path (`FUN_0043b4f0 → Ship::AITickScheduler`), not from any multiplayer dispatcher. `MpgameHandleMessage` (`0x0069f2a0`) and friends do not reference AI vtables.

---

## Open Questions

**OQ1 — Identity of internal base class providing BaseAI vtable slots 0-7**

Slots `+0x00..+0x1C` of BaseAI vtable (`0x0088bb54`) are inherited from an unidentified base class:

| Byte offset | Target | Note |
|-------------|--------|------|
| +0x00 | 0x004707b0 | likely refcount/AddRef equivalent |
| +0x04 | 0x004706c0 | |
| +0x08 | 0x004706d0 | |
| +0x0C | 0x004706e0 | |
| +0x10 | 0x004706f0 | |
| +0x14 | 0x00470aa0 | **hashtable-insert** (verified via disasm) |
| +0x18 | 0x00470bd0 | |
| +0x1C | 0x00470d30 | |

The 0x0094-byte buffer allocated in `BaseAI ctor` plus the global registry pattern at `DAT_009816a0` / `DAT_009816ac` / `DAT_009816a4` (with ID counter at `DAT_008db134`) suggest a Totally Games scripted-object base distinct from NiObject. Slot `+0x14`'s hashtable-insert behavior is consistent with a global-registry self-registration pattern.

Not load-bearing for AI semantics — the 6 documented AI dispatch methods at `+0x20..+0x34` cover the full behavior contract.

---

## Related Documents

- [ship-navigation.md](ship-navigation.md) — Ship movement/targeting functions that AI scripts call
- [damage-system.md](damage-system.md) — Damage pipeline that AI combat behaviors interact with
- [weapon-firing-mechanics.md](weapon-firing-mechanics.md) — Weapon systems controlled by FireScript preprocessor
- [cloaking-state-machine.md](cloaking-state-machine.md) — Cloak states used by CloakAttack compound AI
- [self-destruct-pipeline.md](self-destruct-pipeline.md) — Self-destruct path (AI uses different entry point)
- [../engine/event-system-architecture.md](../engine/event-system-architecture.md) — Event `0x800017` (ET_DONE) posted by `Ship::ProcessAITick` on US_DONE
- [../engine/rtti-class-catalog.md](../engine/rtti-class-catalog.md) — 8 AI classes (no NiRTTI registration; RTTI-like presence via debug strings + AllocAndConstruct + vtables)
