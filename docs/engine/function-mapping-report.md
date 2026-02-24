> [docs](../README.md) / [engine](README.md) / function-mapping-report.md

# Function Mapping Report

Coverage analysis of stbc.exe (~18,247 functions) after running all Ghidra annotation scripts.

## Annotation Script Suite

Run order matters — later scripts benefit from names applied by earlier ones.

| # | Script | What It Does | Functions Named |
|---|--------|-------------|---------------------|
| 1 | `ghidra_annotate_globals.py` | Labels 19 globals, 2,355 key RE'd functions (361 classes), 22 Python module tables | 2,396 |
| 2 | `ghidra_annotate_nirtti.py` | Labels 117 NiRTTI factory + 117 registration functions, guard flags | 234 |
| 3 | `ghidra_annotate_swig.py` | Names 3,990 SWIG wrapper functions from PyMethodDef table | 3,990 |
| 4 | `ghidra_annotate_vtables.py` | Auto-discovers vtables from 97 factories, names constructors + slots | 1,270 |
| 5 | `ghidra_annotate_swig_targets.py` | Traces SWIG wrappers to name underlying C++ implementations | 4 |
| 6 | `ghidra_annotate_pymodules.py` | Walks 21 Python module method tables, names C implementations | 266 |
| 7 | `ghidra_annotate_python_capi.py` | Names 113 Python 1.5.2 C API functions, type objects, globals, 10 module inits | 137 |
| 8 | `ghidra_discover_strings.py` | Names functions from "ClassName::MethodName" debug strings | 33 (+515 comments) |

**Recommended run order:** 1 → 2 → 3 → 7 → 6 → 4 → 5 → 8

Scripts 1-3 and 7 provide foundational names that scripts 4-5 use for helper detection. Script 8 runs last to benefit from all prior naming.

> **Note on swig_targets:** Most SWIG wrappers (3,986 of 3,990) are inline field accessors with no non-helper CALL instructions, so they have no separate C++ target function to name. The 4 that do get named are wrappers that call unique C++ implementations.

## Coverage Summary

| Category | Count | % of 18,247 |
|----------|-------|-------------|
| Auto-generated (Unwind/Catch handlers) | ~4,695 | 26% |
| Named by annotation scripts | ~8,330 | 46% |
| Named by Ghidra MCP sessions (Passes 1-8) | ~2,184 | 12% |
| **Total named/excluded** | **~15,209** | **83%** |
| Remaining unnamed (game-specific) | ~1,113 | 6% |
| Remaining unnamed (compiler/helper) | ~2,000 | 11% |

### Ghidra MCP Naming Sessions (2026-02-23 through 2026-02-24)

Eight rounds of systematic function naming via the Ghidra MCP bridge. Pass 8 used 10 parallel agents covering event system, weapons, UI, scene graph, Ship vtable, subsystems, TGObject hierarchy, mission/game, and xref mining:

**Pass 1 (string mining + xref walking)**: 156 functions renamed. Method: search for `ClassName::MethodName` debug strings compiled into the binary from original TG source, trace xrefs to containing functions, rename. Covered: Game, Mission, Episode, ShipClass, AsteroidField, CameraMode, NiDX7Renderer, UI handlers, and more.

**Pass 2 (continued string mining + constructor chains)**: 77 additional renames. Method: continued string categories (Warning, Cannot, Error), plus decompiling known constructors to trace callees. Discovered: UtopiaApp__ctor → NiApplication__ctor, TGConfigFile__Load/HasKey/GetInt, TGEventManager functions, TGNetwork core methods.

**Pass 2b (documented RE'd functions)**: 90 renames from addresses documented in RE docs but not previously in Ghidra. Method: bulk-rename from known function addresses in docs/gameplay/, docs/networking/, docs/protocol/. 30 addresses failed (not function entry points in Ghidra — mid-function or unanalyzed code).

**Pass 3 (RegisterHandlers + constructors + GameSpy)**: 53 renames, 2 failures. Method: extracted `RegisterHandlerNames`/`RegisterHandlers` pattern from TGEventHandlerObject hierarchy — every class that registers event handlers has this pair. Also found constructors (BridgeObjectClass, TGWinsockPeer, WeaponSystem, TorpCameraMode), ship state functions (ReadStateUpdate, LinkSubsystemToParent, AssignWeaponGroups), GameSpy query handling (TokenizeString, qr_parse_query, qr_lookup_or_add_key), and game loading (LoadMissionWithMovie, LoadSaveFile). Covered classes: TGSoundManager, TGMusic, CharacterSpeakingQueue, ViewScreenObject, TGUIObject, TGDialogWindow, TGButtonBase, TGParagraph, TGConsole, TGStringDialog, Torpedo, ConditionScript.

**Pass 3 annotation script update**: Consolidated 115 additional documented function addresses from RE docs (gameplay, networking, protocol) into `ghidra_annotate_globals.py` KEY_FUNCTIONS dict (62 → 177 entries). These cover: damage pipeline, shield system, power system, repair system, weapon systems, self-destruct, multiplayer lifecycle, checksum handlers, GameSpy discovery, event system, TGMessage routing, CF16 encoding, and subsystem constructors.

**Pass 4 (AI classes + serialization + sound)**: 42 renames, 0 failures. Method: systematic analysis of AI behavior tree node classes (PlainAI, ConditionalAI, PreprocessingAI, PriorityListAI, RandomAI, SequenceAI) — named virtual method implementations (SetActive, SetInactive, GotFocus, LostFocus, Update, IsDormant) by decompiling vtable slots and matching behavioral patterns. Also traced NiStream save/load pipeline (TGObject__LoadFromStream, TGObject__SaveToStream, TGEventManager load/save, Game__SaveToFile, Planet__LoadFromStream), sound system serialization (TGSoundManager, TGSoundRegionManager, PhonemeList), UI system (InterfaceModule__CreateOverridePane), condition system (ConditionScript__SaveConditionEventCreators), and camera (CameraObjectClass__RegisterAnimationDoneHandler).

**Pass 4 annotation script update**: Added 42 Pass 4 addresses to `ghidra_annotate_globals.py` KEY_FUNCTIONS dict (177 → 219 entries). New coverage: AI behavior tree methods (28), object serialization pipeline (8), sound system (3), camera (1), UI (1), conditions (1).

**Pass 5 (AI constructors + renderer pipeline + Ship AI)**: 35 renames, 0 failures, 10 discards. Method: traced SWIG `*AI_Create` wrappers through AllocAndConstruct factories to actual `__thiscall` constructors (confirmed by vtable writes) — identified complete AI class hierarchy (`BaseAI` → `{PlainAI, ConditionalAI, PriorityListAI, RandomAI, SequenceAI}` and `BaseAI` → `PreprocessingAI` → `BuilderAI`). Named 8 constructors + 7 AllocAndConstruct wrappers. Traced NiDX7Renderer initialization pipeline via debug strings ("NI D3D Renderer ERROR/WARNING:", "Set Display Mode failed", "Create Texture failed", etc.) — 11 renderer functions + 3 texture system functions + device selection dialog builder. Also: `UtopiaApp__CreateRenderer` (reads "Graphics Options" config), `Ship__AITickScheduler`/`Ship__ProcessAITick` (per-ship AI callback), `NetFile__RegisterHandlerNames`, and 2 UI constructors (`NamedReticleWindow`, `EngRepairPane`).

**Pass 5 annotation script update**: Added 35 Pass 5 addresses to `ghidra_annotate_globals.py` KEY_FUNCTIONS dict (219 → 254 entries). New coverage: AI constructors (15), NiDX7Renderer pipeline (11), NiDX7Texture/Manager (3), Ship AI (2), game init (1), network (1), UI (2).

**Pass 6 (SWIG tracing + callee chains + save system)**: 75 renames, 4 failures, 11 discards. Method: three complementary strategies — (1) SWIG wrapper tracing: decompiled `swig_ShipClass_*` wrappers to reveal C++ target functions for Ship navigation, targeting, state, and combat operations (22 renames). (2) Constructor callee chain walking: decompiled known constructors and damage pipeline functions (DoDamage, ProcessDamage, Game__SaveToFile) to trace unnamed callees (20 renames). (3) Save system tracing: followed Game__SaveToFile callee chain to discover complete TGFileStream class hierarchy (13 renames). Covered: Ship navigation (SetTarget, TurnTowardLocation, ComputeTurnAngularVelocity), DamageInfo class (ctor, SetRadius, SetDamageType, ComputeBoundingBox), combat subsystems (PhaserSystem__SetPowerLevel, TorpedoSystem__SetAmmoType, ShieldSystem__SetShieldFacing), ship state (RunDeathScript, StopFiringWeapons, SetImpulse, IsCloaked), TGFileStream hierarchy (ctor, Open, Close, Flush, BufferedFileStream), save game helpers (InitPickler, FlushPickler, SaveDirtyObjects), scene graph lookup (TGObjectTree__FindByHashAndTrack), NiMatrix3 math (TransformVector, TransposeTransformVector), and subsystem iterators (StartGetSubsystemMatch, GetNextSubsystemMatch).

**Pass 6 annotation script update**: Added 79 Pass 6 addresses to `ghidra_annotate_globals.py` KEY_FUNCTIONS dict (254 → 331 entries, 2 duplicates consolidated). New coverage: Ship navigation/targeting (14), TGFileStream/save system (14), Ship state (8), Subsystem/weapon helpers (7), Combat subsystem functions (6), Ship combat/damage (5), DamageInfo class (4), TGObject/scene graph (4), Scene graph lookup (4), Save game helpers (4), Subsystem property (3), NiMatrix3 math (2), Engine subsystem (2), Ship subsystem iterator (2).

**Pass 7 (massive SWIG + constructor + xref sweep)**: ~968 renames via main agent, plus ~234 (string mining), ~90 (bulk import from docs), ~53 (Pass 3 continuation), ~42 (Pass 4 continuation) from supplementary agents. Total: ~1,387 rename operations across 5 agents, yielding 1,468 unique addressed names (1,222 new + 86 updated existing names + 180 overlapping with pre-existing script entries). Methods: (1) Exhaustive SWIG wrapper decompilation — systematically decompiled swig_ClassName_Method wrappers to identify direct C++ CALL targets; (2) Constructor callee chain walking — traced constructors' FUN_ callees through entire class hierarchies (TGObject → TGStreamedObject → TGStreamedObjectEx → TGEventHandlerObject, AI class trees, power system classes); (3) Xref-based discovery — used get_xrefs_to on key functions (NiAlloc, EventManager_PostEvent, DoDamage) to find callers and name them by context; (4) Name normalization — updated 86 existing names from single-underscore to double-underscore convention and added proper class prefixes (e.g., `GetPlayerShip` → `Game__GetPlayerShip`, `RemovePeerAddress` → `TGWinsockNetwork__RemovePeerAddress`). Coverage spans 277 distinct classes including Episode, PlayWindow, Game, Mission, NiNode, NiDX7Renderer, NiApplication, TGPeerArray, TGSetManager, TGFileStream, Ship subsystems, AI classes, weapon systems, sensor systems, camera modes, sound system, and more.

**Pass 7 annotation script update**: Complete rebuild of `ghidra_annotate_globals.py` KEY_FUNCTIONS dict (331 → 1,553 entries), organized by class into 277 categories. Includes all prior passes plus 1,222 new entries from Pass 7 agents. UTOPIA_GLOBALS (13) and PYTHON_MODULES (22) unchanged.

**Pass 8A (multiplayer handler callees)**: 38 renames — decompiled all 15 MP dispatcher handler functions, traced unnamed callees. 9 game-specific (NiPoint3__Copy, NiMatrix3__TransformPoint, WString__Clear/AssignSubstring, TGDisplayTextAction ctors, TGBufferStream__vReadInt, TGBufferStream__ReadCompressedVector4_ByteScale, TGLManager__ReleaseFile) + 29 Python C API functions (PyErr_*, PyDict_*, PyString_*, PyObject_*, PyFile_*, PySys_*, PyTraceBack_Print, etc.).

**Pass 8C (TGEventManager deep-dive)**: 61 renames + 6 globals — full event dispatch infrastructure: TGEventHandlerTable (10), TGInstanceHandlerTable (5), TGCallback (8), TGConditionHandler (16), TGHandlerListEntry (3), TGEventQueue (6), TGEvent infrastructure (2), TGLinkedList (2), and supporting functions (9).

**Pass 8A+8C annotation script update**: Added 220 net new entries to `ghidra_annotate_globals.py` (1,553 → 1,773 function entries, 318 classes). Includes Phase 8A game/Python C API functions and Phase 8C event system infrastructure.

All renames are high-confidence only — backed by debug strings from original source code, clear behavioral patterns in decompiled code, or verified against live game traces.

## What Each Script Discovers

### ghidra_annotate_vtables.py (Phase 1+2)

Auto-discovery pipeline for 117 NiRTTI factory classes (97 vtables discovered, 20 failed):
1. Decompiles factory function -> finds constructor (first non-NiAlloc CALL after NiAlloc)
2. Scans constructor -> finds vtable address (MOV to .rdata with noop verification at slot 11)
3. Counts vtable slots using sorted boundary detection
4. Names: vtable label, constructor (`ClassName_ctor`), scalar_deleting_dtor, base 12 NiObject slots

Actual results: 1,090 virtual function slots + 96 constructors + 84 destructors = 1,270 total.

Verified slot names for known hierarchies:
- **NiObject** (12 slots): GetRTTI through IsEqual
- **NiAVObject** (27 additional slots): UpdateControllers through UpdateWorldBound
- **NiNode** (4 additional slots): AttachChild through SetAt
- **NiProperty** (2 additional slots): Type, Update
- **NiExtraData** (1 additional slot): GetSize
- **NiAccumulator** (4 additional slots): RegisterObjectArray through FinishAccumulating

Key verification: slot 11 (vtable+0x2C) must equal `0x0040da50` (universal noop).

### ghidra_annotate_swig_targets.py (Phase 3)

Two-pass frequency analysis:
- Pass 1: Walk all 3,990 SWIG wrappers, collect all CALL targets
- Pass 2: Targets appearing in >50 wrappers = helpers (PyArg_ParseTuple, SWIG_GetPointerObj, etc.)
- Pass 3: Last non-helper CALL in each wrapper = the C++ implementation

Names derived from wrapper: `swig_NiNode_GetName` → target named `NiNode_GetName`.
Handles `delete_X` → `X_dtor`, `new_X` → `X_new`.

Inline wrappers (field access, no CALL) are skipped — these have no separate target function.

### ghidra_annotate_pymodules.py (Phase 7)

Walks 21 non-SWIG Python module method tables (same 16-byte PyMethodDef format as SWIG):

| Module | Table Address | Description |
|--------|-------------|-------------|
| builtin | 0x00961490 | `__builtin__` module |
| imp | 0x00963a80 | Module import |
| marshal | 0x009643a0 | Serialization |
| locale | 0x00964658 | Locale support |
| cPickle | 0x00964b60 | Fast pickle |
| cStringIO | 0x009660a8 | String I/O |
| thread | 0x00966ab0 | Threading |
| time | 0x00967410 | Time functions |
| struct | 0x009686c0 | Binary packing |
| strop | 0x009697d8 | String operations |
| regex | 0x00969d28 | Regular expressions |
| operator | 0x0096a078 | Operator overloads |
| nt | 0x0096b888 | OS interface |
| new | 0x0096bd88 | Object creation |
| math | 0x0096c378 | Math functions |
| errno | 0x0099f5c8 | Error codes |
| cmath | 0x0096d178 | Complex math |
| binascii | 0x0096d818 | Binary ↔ ASCII |
| array | 0x0096e118 | Array type |
| sys | 0x0096faa8 | System interface |
| signal | 0x009743d8 | Signal handling |

Names: `py_<module>_<method>` (e.g., `py_time_time`, `py_struct_pack`).

### ghidra_annotate_python_capi.py (Phase 4)

Labels ~130 Python 1.5.2 C API functions statically linked into stbc.exe (range ~0x0074a000-0x0078ffff):

- Object protocol: GetAttr, SetAttr, Compare, Hash, etc.
- Error handling: PyErr_SetString, PyErr_Format, etc.
- Type operations: Int, Float, String, Tuple, List, Dict creation and access
- Abstract protocols: Number, Sequence, Mapping
- Module/Import: PyImport_ImportModule, Py_InitModule4
- Compile/eval: PyRun_SimpleString, Py_CompileString, PyEval_EvalCode
- 11 type object labels (PyInt_Type, PyFloat_Type, etc.)
- 3 singleton labels (_Py_NoneStruct, _Py_ZeroStruct, _Py_TrueStruct)
- 22 module init functions (init_builtin, inittime, initstrop, etc.)

### ghidra_discover_strings.py (Phase 6)

Scans all defined strings for patterns identifying function names:
- `"ClassName::MethodName"` — C++ debug assertions/error messages
- `"ClassName::MethodName: error text"` — prefix matching
- Names function if it's the sole unnamed reference to the string

Runs last to benefit from all prior naming (avoids renaming already-named functions).

## Unmappable Functions

### Game-Specific Class Internals (~2,520-2,940)

~420 Totally Games proprietary classes (ShipClass, TGUIObject, STMission_*, AIShipBehavior, etc.). Zero external documentation. Only discoverable through per-function manual RE.

### NI 3.1-Only Subsystems (~250-340)

42 NI classes with no Gamebryo 1.2 source: Bezier patches (11), old animation system (8), old texture properties (5), DirectDraw rendering (8), NI 3.1-specific nodes (3), audio (4), misc (3).

### Compiler-Generated Code (~800-1,200)

Thunks, inlined CRT, template instantiations, exception handlers, adjuster thunks. No meaningful semantic names possible.

### Anonymous Helpers (~200-400)

1-10 instruction functions with no strings, no distinctive patterns. Too small to identify purpose.

## Phase 5 (COM Interfaces) — 0 Yield

COM vtables for DDraw7/D3D7/Surface7 are in external DirectX DLLs, not in stbc.exe. The NetImmerse wrapper classes (NiDX8Renderer etc.) are NiObject-derived and already handled by the vtable script. No additional functions to name.

## Key Architectural Discovery: NI 3.1 vs Gb 1.2 Vtable Differences

NI 3.1 has significantly MORE virtual methods than Gb 1.2 in several key hierarchies:

| Class | NI 3.1 Slots | Gb 1.2 Slots | Delta |
|-------|-------------|-------------|-------|
| NiAVObject | 39 | 27 | +12 |
| NiNode | 43 | 31 | +12 |
| NiGeometry | 64 | 27 | +37 |

This means class-specific virtual method names CANNOT be blindly copied from Gb 1.2 header ordering — the slot indices don't match. The vtable script uses verified base-class slot names (NiObject 0-11, NiAVObject 12-38, NiNode 39-42) and leaves class-specific extended slots as numbered entries (`vfunc_NN`) pending manual verification.
