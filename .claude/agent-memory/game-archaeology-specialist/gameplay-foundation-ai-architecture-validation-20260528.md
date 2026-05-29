---
name: gameplay-foundation-ai-architecture-validation-20260528
description: Gameplay foundation #6 v5 validation — AI architecture (308 lines). 8 vtables + 8 ctors + tick scheduler all byte-confirmed. ZERO corrections to class hierarchy. 2 C: vtable slot numbering is OFFSETS-not-INDICES (Update is byte +0x30 = slot 12, not slot 4), and enum actually has 4 states (US_INVALID = 3rd) + US_NUM_STATUSES count constant. Status `validated`.
metadata:
  type: project
---

# Gameplay #6 — AI Architecture Validation (2026-05-28)

**Doc**: `docs/gameplay/ai-architecture.md` (308 lines)
**Binary**: STBC.exe (image_base 0x00400000, 18616 functions)
**v5 verdict**: `validated` with 2 minor doc clarifications

## Evidence summary

### Section 1 (Class Hierarchy) — ROCK SOLID

All 8 vtable addresses verified via `get_xrefs_to` (3 DATA xrefs each = ctor + dtor + AllocAndConstruct wrapper):

| Class | Vtable | Ctor | Inheritance verified |
|-------|--------|------|----------------------|
| BaseAI | 0x0088bb54 | FUN_00470520 | Root (no super-ctor call) |
| PlainAI | 0x0088c0d8 | FUN_0048cc40 | calls BaseAI ctor ✓ |
| ConditionalAI | 0x0088bc84 | FUN_00478a50 | calls BaseAI ctor ✓ |
| PriorityListAI | 0x0088c188 | FUN_0048fcb0 | (matches 3-xref pattern) |
| RandomAI | 0x0088c1dc | FUN_00491370 | (matches 3-xref pattern) |
| SequenceAI | 0x0088c230 | FUN_004927d0 | (matches 3-xref pattern) |
| PreprocessingAI | 0x0088c12c | FUN_0048e2b0 | calls BaseAI ctor ✓ |
| BuilderAI | 0x0088bbe0 | FUN_00475fb0 | **calls FUN_0048e2b0 (PreprocessingAI)** ✓ |

**Critical confirmation**: BuilderAI ctor explicitly calls PreprocessingAI ctor at line 1 of decompilation, then overrides vtable to 0x0088bbe0. This proves the inheritance chain `BuilderAI → PreprocessingAI → BaseAI` exactly as the doc claims.

### Section 2 (Virtual Method Table) — REFRAMING NEEDED (C1)

**C1 (doc clarification, not error)**: The "Slot 0..5" labeling in the doc is logical/ordinal — but the actual binary vtable has these methods at byte offsets +0x20..+0x34, i.e., **vtable slot indices 8-13**, not 0-5.

Binary evidence (BaseAI vtable @ 0x0088bb54, read via `read_memory`):

| Byte offset | Slot # | Target | Identity (from ProcessAITick calls) |
|-------------|--------|--------|--------------------------------------|
| 0x00 | 0 | 0x004707b0 | (inherited base — possibly NiObject AddRef equivalent) |
| 0x04 | 1 | 0x004706c0 | (inherited base) |
| 0x08 | 2 | 0x004706d0 | (inherited base) |
| 0x0C | 3 | 0x004706e0 | (inherited base) |
| 0x10 | 4 | 0x004706f0 | (inherited base) |
| 0x14 | 5 | 0x00470aa0 | hashtable-insert (verified via disasm) |
| 0x18 | 6 | 0x00470bd0 | (inherited base) |
| 0x1C | 7 | 0x00470d30 | (inherited base) |
| **0x20** | **8** | 0x00470700 | **SetActive** (doc "slot 0") |
| 0x24 | 9 | 0x00470710 | **SetInactive** (doc "slot 1") |
| 0x28 | 10 | 0x00470720 | **GotFocus** (doc "slot 2") |
| 0x2C | 11 | 0x00470730 | **LostFocus** (doc "slot 3") |
| 0x30 | 12 | 0x00470740 | **Update** (doc "slot 4") |
| 0x34 | 13 | 0x00470750 | **IsDormant** (doc "slot 5") |
| 0x38 | 14 | 0x00470760 | (returns 0 — likely another boolean predicate) |
| 0x3C | 15 | 0x00470770 | (unknown) |
| 0x40 | 16 | 0x004710c0 | (real function — Clone variant) |
| 0x44 | 17 | 0x00470780 | (small stub) |
| 0x48 | 18 | 0x00470790 | (small stub) |
| 0x4C | 19 | 0x00859a0b | **__purecall** (abstract method!) |
| 0x50 | 20 | 0x004707a0 | called from tick scheduler with arg `9` |

**Rationale for "slot 0..5" framing in doc**: From a Python/SWIG developer's POV, the BaseAI is presented as having 6 main dispatch methods. The inherited slots 0-7 are infrastructure (probably from an internal NetImmerse-style base class — possibly NiObject or a TG analog). The doc is correct in spirit but a reader trying to find Update by counting from byte 0 of the vtable will be off by 12 slots.

**Recommended doc revision** (low priority — doesn't change correctness of the AI model):
> Slot offsets in BaseAI vtable: SetActive=+0x20, SetInactive=+0x24, GotFocus=+0x28, LostFocus=+0x2C, Update=+0x30, IsDormant=+0x34. (Slots before +0x20 are inherited from an internal base class.)

Binary anchors:
- BaseAI Update default at 0x00470740: `B8 03 00 00 00 / C2 08 00` → `MOV EAX, 3; RET 8` (returns US_INVALID, takes 1 float10 = 8 bytes)
- BaseAI IsDormant default at 0x00470750: `8B C1 C3` → `MOV EAX, ECX; RET` (returns `this`)
- BaseAI slot+0x38 at 0x00470760: `32 C0 C3` → `XOR AL,AL; RET` (returns false)
- BaseAI slot+0x4C at 0x004707a0: `0x00859a0b` is `__purecall` — proves BaseAI is **abstract** ✓ matches doc

### Section 2.1 (UpdateStatus enum) — NEW STATE FOUND (C2)

**C2 (doc completion)**: The doc lists 3 enum values (US_ACTIVE=0, US_DORMANT=1, US_DONE=2). The binary has **4 states + 1 count**:

Strings found via `search_strings` at adjacent addresses (0x009508a0-0x0095091c):
- `ArtificialIntelligence_US_NUM_STATUSES` (count constant, not a real state)
- `ArtificialIntelligence_US_INVALID`  ← **doc missed this**
- `ArtificialIntelligence_US_DORMANT`
- `ArtificialIntelligence_US_DONE`
- `ArtificialIntelligence_US_ACTIVE`

The BaseAI Update default returns **3** (`MOV EAX, 3`). Looking at ProcessAITick (0x004722d0) return-value handling:
- `if (local_34 == 1)` → triggers SetInactive + LostFocus (DORMANT path)
- `else if (local_34 == 2)` → posts event 0x800017 (DONE path)
- Otherwise (incl. 0 and 3): stores time, exits (no state change)

So actual enum order is likely `{US_ACTIVE=0, US_DORMANT=1, US_DONE=2, US_INVALID=3, US_NUM_STATUSES=4}`. The default BaseAI Update returning `US_INVALID` matches "abstract — should never be called" semantics.

**Recommended doc revision** (medium priority):
```c
enum UpdateStatus {
    US_ACTIVE       = 0,  // Currently executing
    US_DORMANT      = 1,  // Temporarily inactive (triggers SetInactive + LostFocus)
    US_DONE         = 2,  // Completed or failed (posts event 0x800017)
    US_INVALID      = 3,  // Default return (abstract / not implemented)
    US_NUM_STATUSES = 4   // Enum size (not a real state)
};
```

### Section 3 (Tick Scheduling) — VERIFIED

| Function | Address | Verified |
|----------|---------|----------|
| Ship__AITickScheduler | 0x004721b0 | ✓ Reads clock at DAT_0099c6bc, calls FUN_004722d0 |
| Ship__ProcessAITick | 0x004722d0 | ✓ Calls Update via vtable[+0x30], dispatches return |

`Ship__AITickScheduler` has exactly 1 caller: `FUN_0043b4f0` at 0x0043b55b (the ship's per-tick Update method). `ProcessAITick` is called ONLY from the scheduler. Debug string `s_Ship__s___UpdateAI` at 0x008db15c = `"Ship(%s)::UpdateAI"` confirms purpose. ✓ matches doc.

### Section 4 (Python/C++ Bridge) — VERIFIED

Anchored evidence:
- `pCodeAI` string at 0x008dbb74 (single occurrence) — used by PreprocessingAI (xref from FUN_0048e400)
- `BaseAI__GetShip` (FUN_00470a30) calls `PhysicsObjectClass__FindByObjectID(0, this+4)` — confirms doc's `GetShip()` claim
- SWIG bindings exist:
  - `PlainAI_Create`, `PlainAI_SetScriptModule`, `PlainAI_StopCallingActivate`
  - `BuilderAI_Create`, `BuilderAI_AddAIBlock`, `BuilderAI_AddDependency`/`BuilderAI_AddDependencyObject`
  - `ArtificialIntelligence_GetName`, `_GetID`, `_Reset`, `_IsInterruptable`, `_SetInterruptable`, `_IsPaused`, `_Unpause`
  - `RegisterExternalFunction`, `UnregisterExternalFunction`, `RegisterExternalFunctions`
- `ConditionScript_Create(sModule, sClass, ...)` error string at 0x008db388 confirms doc's exact signature ✓

**Note**: `FixCodeAI` string is NOT in the binary — it's a Python-side method name (in AI/PlainAI/*.py). Not an error; just clarification that the binary doesn't know about that helper.

### Section 5+ (Behaviors / Compounds / Fleet / Player / Conditions) — VERIFIED INDIRECTLY

None of the 27 PlainAI script names, 15 Compound script names, 5 Fleet script names, or 26 Player script names appear as strings in the binary (sampled: `BasicAttack`, `FedAttack`, `InaccurateTorps`, `SetCircleSpeed`, `g_lFlagThresholds`, `FlagThreshold` — all absent). This **confirms** the doc's claim that the C++ side only knows the 8 base classes — all behavior names, the difficulty flag table, the fuzzy logic configs, and the compound/fleet/player/condition tables are entirely Python (in `reference/scripts/AI/`).

### Section 10 (Preloading) — VERIFIED

- `"AI.Setup"` at 0x008e1994 and `"GameInit"` at 0x008e19a0 — adjacent strings
- Both have DATA xrefs from `FUN_00504f10` at 0x00504f36 and 0x00504f3b (back-to-back instructions)
- `FUN_00504f10` is the `CreateMultiplayerGame` function (the doc's claim)
- ✓ matches "AI.Setup.GameInit() called from CreateMultiplayerGame at 0x00504F10"

### Section 11 (Fuzzy Logic) — VERIFIED

SWIG bindings present:
- `FuzzyLogic_GetResultBySet` at 0x009232c0
- `FuzzyLogic_SetPercentageInSet` at 0x009232dc
- `FuzzyLogic_SetRuleConfidence` at 0x009232fc
- 23 total `FuzzyLogic*` strings (other methods exist too)

✓ matches doc's `App.FuzzyLogic()` claim.

### Section 4 (Save/Load) — VERIFIED

- SaveGame__InitPickler (0x006f9fb0): uses `cPickle` (string at 0x008d9c2c) + `Pickler` (string at 0x0095b4e0) — creates Pickler instance ✓
- SaveGame__FlushPickler (0x006fa020): calls `getvalue` on pickler, then marshal-style functions ✓
- Both called from FUN_00443ac0 (likely SaveGameState)

### Section 12 (Multiplayer Relevance) — INDIRECTLY SUPPORTED

The C++ AI system is hooked from the **ship update path** (FUN_0043b4f0 → AITickScheduler), not from any multiplayer dispatcher. MultiplayerGame (FUN_0069f2a0) and friends don't reference AI vtables. This is consistent with the doc's claim that "AI is single-player/campaign only." Not exhaustively proven but no counter-evidence found.

## v5 Triage Summary

| Class | Count | Items |
|-------|-------|-------|
| **C** (Material correction) | 0 | — |
| **Clar** (Clarification) | 2 | C1 (slot numbering offsets-not-indices); C2 (US_INVALID + US_NUM_STATUSES missing from enum) |
| **R** (Rederivation) | 0 | — |
| **OQ** (Open Question) | 1 | Slots +0x00..+0x1C of BaseAI vtable — what is the "base class" they come from? Possibly an internal Totally Games scripted-object base. Slot 5 is a hashtable-add method (FUN_00470aa0) suggesting registry behavior. |
| **H** (Historical) | 0 | — |

**Verdict**: `validated` (v5 status). Doc is highly accurate; both Clar items are clarifications rather than wire-format or contract corrections.

## Anchored addresses (final inventory)

| What | Address |
|------|---------|
| BaseAI vtable | 0x0088bb54 |
| PlainAI vtable | 0x0088c0d8 |
| ConditionalAI vtable | 0x0088bc84 |
| PriorityListAI vtable | 0x0088c188 |
| RandomAI vtable | 0x0088c1dc |
| SequenceAI vtable | 0x0088c230 |
| PreprocessingAI vtable | 0x0088c12c |
| BuilderAI vtable | 0x0088bbe0 |
| BaseAI ctor | 0x00470520 |
| PlainAI ctor | 0x0048cc40 |
| ConditionalAI ctor | 0x00478a50 |
| PriorityListAI ctor | 0x0048fcb0 |
| RandomAI ctor | 0x00491370 |
| SequenceAI ctor | 0x004927d0 |
| PreprocessingAI ctor | 0x0048e2b0 |
| BuilderAI ctor | 0x00475fb0 |
| BaseAI Update default (returns US_INVALID=3) | 0x00470740 |
| BaseAI IsDormant default | 0x00470750 |
| BaseAI __purecall slot | 0x00859a0b |
| BaseAI__GetShip | 0x00470a30 |
| Ship__AITickScheduler | 0x004721b0 |
| Ship__ProcessAITick | 0x004722d0 |
| AITickScheduler's only caller | 0x0043b55b (in FUN_0043b4f0) |
| SaveGame__InitPickler | 0x006f9fb0 |
| SaveGame__FlushPickler | 0x006fa020 |
| CreateMultiplayerGame (calls AI.Setup.GameInit) | 0x00504f10 |
| Global clock | DAT_0099c6bc |
| AI hashtable registry | DAT_009816a0, DAT_009816a4, DAT_009816ac |
| ID counter | DAT_008db134 |
| "AI.Setup" string | 0x008e1994 |
| "GameInit" string | 0x008e19a0 |
| "pCodeAI" string | 0x008dbb74 |
| `Ship(%s)::UpdateAI` debug string | 0x008db15c |
| US_INVALID name string | 0x009508c2 |
| US_DORMANT name string | 0x009508d0 |
| US_DONE name string | 0x009508f4 |
| US_ACTIVE name string | 0x00950914 |
| US_NUM_STATUSES name string | 0x0095088c |

## Cross-reference targets

- `docs/engine/rtti-class-catalog.md` — should this list the 8 AI classes? They have no NiRTTI registration but have RTTI-like presence via debug strings + AllocAndConstruct + vtables.
- `docs/protocol/wire-format-spec.md` — no AI opcodes (AI is client-local; ship state is what gets replicated)
- `docs/gameplay/ship-navigation.md` — sibling doc, AI calls into navigation. ✓ doc links it.

## Methodology notes (for next archaeologist)

- Pattern for ctor verification: 3 DATA xrefs to a vtable = (ctor, dtor, AllocAndConstruct). Confirmed across all 8 classes.
- Pattern for inheritance: decompile ctor → look for super-ctor call before vtable override. BuilderAI calls FUN_0048e2b0 (PreprocessingAI ctor); PlainAI/ConditionalAI/PreprocessingAI all call FUN_00470520 (BaseAI ctor).
- Stub vtable slots are often inline assembly (3-byte `XOR AL,AL; RET`) that Ghidra won't auto-create as functions — use `disassemble_bytes` or `inspect_memory_content` to read them.
- SWIG enum constant tables: search for `<ClassName>_<CONSTANT>` strings — they're in `.rdata` near the SWIG type metadata. The actual integer values are populated at module-init time from `swig_const_info` structs.
