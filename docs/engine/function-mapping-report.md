> [docs](../README.md) / [engine](README.md) / function-mapping-report.md

---
title: Function Mapping Report
type: reference
audience: re-engineer
validated: 2026-05-28
methodology: FUNCTION_DOC_WORKFLOW_V5
binary:
  name: STBC.exe
  size: 6394712
  base: 0x00400000
status: partial
evidence:
  - claim: "Eight annotation scripts exist in tools/ with the INTENT described by the script suite table"
    address: null
    function: null
    confidence: high
    note: "Files present: tools/ghidra_annotate_globals.py, _nirtti.py, _swig.py, _python_capi.py, _pymodules.py, _vtables.py, _swig_targets.py, _discover_strings.py. Row descriptions reflect script source code, not Ghidra-applied state."
  - claim: "Zero annotation scripts have been applied to the current Ghidra import"
    address: null
    function: null
    confidence: high
    note: "Five Pass 7/8 narrative rename claims spot-checked via search_functions on STBC.exe; all returned no matches: TGObject__LoadFromStream, Game__GetPlayerShip, TGEventHandlerTable, TGWinsockNetwork__RemovePeerAddress, Ship__AITickScheduler. `search_functions(\"swig_\")` = 0 matches — the 3,990-function SWIG annotation never landed."
  - claim: "Current custom-named function count is 4,797 = 25.8% of 18,581"
    address: null
    function: null
    confidence: high
    note: "Counts from search_functions_enhanced on STBC.exe. All 4,797 are Ghidra auto-analysis artifacts: 3 Catch@xxxxx + ~4,692 Unwind@xxxxx + library imports (Win32 DLLs) + CRT/STL template instantiations. None are project-applied names."
  - claim: "The only project-applied rename present in the current import is MpgameHandleMessage at 0x0069f2a0"
    address: 0x0069f2a0
    function: MpgameHandleMessage
    completeness: 69.94
    confidence: high
    note: "Applied during function-map.md (foundation #1) v5 validation, 2026-05-28. The MultiplayerGame dispatcher entry — see docs/engine/function-map.md and docs/protocol/game-opcodes.md."
  - claim: "NI 3.1 has more virtual method slots than Gb 1.2 for NiAVObject, NiNode, NiGeometry"
    address: 0x00898ca8
    function: NiAVObject_vtable
    completeness: 85
    confidence: high
    note: "Cross-confirmed by netimmerse-vtables.md v5 validation (2026-05-28). NiAVObject 39 vs 27 (+12), NiNode 43 vs 31 (+12), NiGeometry 64 vs 27 (+37). NiGeometry +37 delta flagged as open question in netimmerse-vtables.md."
companions:
  - docs/engine/function-map.md
  - docs/engine/rtti-class-catalog.md
  - docs/engine/nirtti-factory-catalog.md
  - docs/engine/netimmerse-vtables.md
  - docs/engine/v5-validation-status.md
  - docs/guides/v5-doc-validation-workflow.md
  - docs/guides/v5-evidence-header.md
supersedes:
  - prior undated revision (pre-v5)
---

# Function Mapping Report

> [!NOTE]
> This doc is `status: partial`. The annotation script reference (8 scripts in `tools/`)
> and the NI 3.1 vs Gb 1.2 vtable delta table are v5-validated. The pre-v5 Coverage
> Summary (claiming 83% / ~15,209 named) and the entire "Ghidra MCP Naming Sessions
> (Passes 1-8)" narrative were **removed** — every spot-checked claimed rename was
> absent from the current Ghidra import (created 2026-05-28). Naming work under v5
> happens function-by-function via `FUNCTION_DOC_WORKFLOW_V5`, not bulk scripts. See
> [v5-doc-validation-workflow.md § "Why no annotation scripts"](../guides/v5-doc-validation-workflow.md#why-no-annotation-scripts)
> for the policy.

## Current Coverage State

| Metric | Count | % |
|--------|-------|---|
| Total functions (in-body) | 18,249 | — |
| Total functions (incl. EXTERNAL imports) | 18,581 | — |
| Custom-named (Ghidra auto-analysis only) | 4,797 | 25.8% |
| Unnamed (`FUN_xxxxxxxx`) | 13,467 | 72.4% |
| Project-applied renames (v5 work) | 1 | 0.005% |

The 4,797 custom-named are Ghidra auto-analysis artifacts: `Catch@xxxxx` (3 entries),
`Unwind@xxxxx` (~4,692 entries), library imports (Win32 DLLs), and CRT/STL template
instantiations. They are NOT project-applied names. The single project-applied rename
is `MpgameHandleMessage` at `0x0069f2a0`, applied during foundation #1
([function-map.md](function-map.md)) v5 validation on 2026-05-28.

> [!NOTE]
> Under v5, naming coverage grows function-by-function during per-doc validations and
> dedicated per-function v5 passes — not via bulk annotation scripts. The bulk script
> approach (prior `tools/` runs through 2026-02-24) produced multiple known-wrong
> function names that caused downstream RE churn; the v5 campaign avoids them.

## Annotation Script Suite (Reference — Not Currently Applied)

> [!WARNING]
> The 8 scripts described below exist in `tools/` and would produce the function counts
> shown **if run** — but per the v5 campaign policy, none have been applied to the
> current Ghidra import. The "Functions Named" column describes script *intent* based
> on script source code, not applied state. Prior runs of these scripts produced
> known-wrong function names that caused downstream RE churn; the campaign avoids
> bulk runs. See
> [v5-doc-validation-workflow.md § "Why no annotation scripts"](../guides/v5-doc-validation-workflow.md#why-no-annotation-scripts).

Run order matters — later scripts benefit from names applied by earlier ones.

| # | Script | What It Does | Functions Named (if run) |
|---|--------|-------------|---------------------|
| 1 | `ghidra_annotate_globals.py` | Labels 19 globals, ~2,355 key RE'd functions (361 classes), 22 Python module tables | ~2,396 |
| 2 | `ghidra_annotate_nirtti.py` | Labels 117 NiRTTI factory + 117 registration functions, guard flags | 234 |
| 3 | `ghidra_annotate_swig.py` | Names 3,990 SWIG wrapper functions from PyMethodDef table | 3,990 |
| 4 | `ghidra_annotate_vtables.py` | Auto-discovers vtables from 97 factories, names constructors + slots | 1,270 |
| 5 | `ghidra_annotate_swig_targets.py` | Traces SWIG wrappers to name underlying C++ implementations | 4 |
| 6 | `ghidra_annotate_pymodules.py` | Walks 21 Python module method tables, names C implementations | 266 |
| 7 | `ghidra_annotate_python_capi.py` | Names 113 Python 1.5.2 C API functions, type objects, globals, 10 module inits | 137 |
| 8 | `ghidra_discover_strings.py` | Names functions from `"ClassName::MethodName"` debug strings | 33 (+515 comments) |

**Recommended run order (if ever re-run):** 1 → 2 → 3 → 7 → 6 → 4 → 5 → 8

Scripts 1-3 and 7 provide foundational names that scripts 4-5 use for helper detection. Script 8 runs last to benefit from all prior naming.

> **Note on swig_targets:** Most SWIG wrappers (3,986 of 3,990) are inline field accessors with no non-helper CALL instructions, so they have no separate C++ target function to name. The 4 that do get named are wrappers that call unique C++ implementations.

## What Each Script Discovers

The "What It Does" descriptions below remain accurate to the script source code and serve as a reference for what these scripts would label if executed. They are NOT a description of current Ghidra import state.

### ghidra_annotate_vtables.py

Auto-discovery pipeline for 117 NiRTTI factory classes (97 vtables discovered, 20 failed):
1. Decompiles factory function → finds constructor (first non-NiAlloc CALL after NiAlloc)
2. Scans constructor → finds vtable address (MOV to `.rdata` with noop verification at slot 11)
3. Counts vtable slots using sorted boundary detection
4. Names: vtable label, constructor (`ClassName_ctor`), scalar_deleting_dtor, base 12 NiObject slots

Designed output (if run): 1,090 virtual function slots + 96 constructors + 84 destructors = 1,270 total.

Verified slot names for known hierarchies (cross-confirmed by [netimmerse-vtables.md](netimmerse-vtables.md)):

- **NiObject** (12 slots): GetRTTI through IsEqual
- **NiAVObject** (27 additional slots): UpdateControllers through UpdateWorldBound
- **NiNode** (4 additional slots): AttachChild through SetAt
- **NiProperty** (2 additional slots): Type, Update
- **NiExtraData** (1 additional slot): GetSize
- **NiAccumulator** (4 additional slots): RegisterObjectArray through FinishAccumulating

Key verification: slot 11 (vtable+0x2C) must equal `0x0040da50` (universal no-op, confirmed in netimmerse-vtables.md).

### ghidra_annotate_swig_targets.py

Two-pass frequency analysis:

- Pass 1: Walk all 3,990 SWIG wrappers, collect all CALL targets
- Pass 2: Targets appearing in >50 wrappers = helpers (`PyArg_ParseTuple`, `SWIG_GetPointerObj`, etc.)
- Pass 3: Last non-helper CALL in each wrapper = the C++ implementation

Names derived from wrapper: `swig_NiNode_GetName` → target named `NiNode_GetName`. Handles `delete_X` → `X_dtor`, `new_X` → `X_new`.

Inline wrappers (field access, no CALL) are skipped — these have no separate target function.

### ghidra_annotate_pymodules.py

Walks 21 non-SWIG Python module method tables (same 16-byte `PyMethodDef` format as SWIG):

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

### ghidra_annotate_python_capi.py

Labels ~130 Python 1.5.2 C API functions statically linked into stbc.exe (range ~0x0074a000-0x0078ffff):

- Object protocol: `GetAttr`, `SetAttr`, `Compare`, `Hash`, etc.
- Error handling: `PyErr_SetString`, `PyErr_Format`, etc.
- Type operations: `Int`, `Float`, `String`, `Tuple`, `List`, `Dict` creation and access
- Abstract protocols: `Number`, `Sequence`, `Mapping`
- Module/Import: `PyImport_ImportModule`, `Py_InitModule4`
- Compile/eval: `PyRun_SimpleString`, `Py_CompileString`, `PyEval_EvalCode`
- 11 type object labels (`PyInt_Type`, `PyFloat_Type`, etc.)
- 3 singleton labels (`_Py_NoneStruct`, `_Py_ZeroStruct`, `_Py_TrueStruct`)
- 22 module init functions (`init_builtin`, `inittime`, `initstrop`, etc.)

### ghidra_discover_strings.py

Scans all defined strings for patterns identifying function names:

- `"ClassName::MethodName"` — C++ debug assertions / error messages
- `"ClassName::MethodName: error text"` — prefix matching
- Names function if it's the sole unnamed reference to the string

Designed to run last to benefit from all prior naming (avoids renaming already-named functions).

## NI 3.1 vs Gamebryo 1.2 Vtable Deltas

NI 3.1 has significantly **more** virtual methods than Gb 1.2 in several key hierarchies (cross-confirmed by [netimmerse-vtables.md](netimmerse-vtables.md) v5 validation on 2026-05-28):

| Class | NI 3.1 Slots | Gb 1.2 Slots | Delta | `[v5-validated 2026-05-28]` |
|-------|-------------|-------------|-------|-----------------------------|
| NiAVObject | 39 | 27 | +12 | ✓ (netimmerse-vtables.md vtable at `0x00898ca8`) |
| NiNode | 43 | 31 | +12 | ✓ (netimmerse-vtables.md vtable at `0x00898f2c`) |
| NiGeometry | 64 | 27 | +37 | ✓ (netimmerse-vtables.md vtable at `0x00899164`; the +37 delta is flagged as open question #1 in netimmerse-vtables.md — anomalous non-pointer bytes at vtable +0x9C/+0xA0 suggest the vtable may end earlier than 64 slots) |

**Implication for vtable annotation:** class-specific virtual method names CANNOT be blindly copied from Gb 1.2 header ordering — the slot indices don't match. The `ghidra_annotate_vtables.py` script uses verified base-class slot names (NiObject 0-11, NiAVObject 12-38, NiNode 39-42) and leaves class-specific extended slots as numbered entries (`vfunc_NN`) pending manual verification.

For the canonical vtable layouts and per-slot evidence, see [netimmerse-vtables.md](netimmerse-vtables.md).

## Current Naming Approach Under v5

Per `FUNCTION_DOC_WORKFLOW_V5` (`ghidra-mcp/docs/prompts/`), naming happens function-by-function. The workflow for each cited function:

1. `analyze_for_documentation` — collect decompile, callers, callees, strings, types
2. `rename` + `set_function_prototype` in parallel — only if behavior + name agree
3. Type audit + Hungarian variable renames
4. `batch_set_comments` — plate / PRE / EOL comments grounded in the function body
5. `analyze_function_completeness` — target 80%+ for load-bearing functions

Each named function carries v5 evidence: address, decompile rationale, and a completeness score. Coverage grows as docs are validated — the per-doc validation campaign progressively retires `confidence: low` rows by applying v5 passes to cited functions. No bulk operations; no script runs.

The doc-level orchestrator playbook for this work is [v5-doc-validation-workflow.md](../guides/v5-doc-validation-workflow.md); the per-function workflow is upstream at `ghidra-mcp/docs/prompts/FUNCTION_DOC_WORKFLOW_V5.md`.

## See also

- [function-map.md](function-map.md) — 20-category function inventory, the canonical post-v5 coverage truth
- [rtti-class-catalog.md](rtti-class-catalog.md) — RTTI class identity, the source of name strings the scripts would consume
- [nirtti-factory-catalog.md](nirtti-factory-catalog.md) — 117 NiRTTI factory registrations
- [netimmerse-vtables.md](netimmerse-vtables.md) — canonical vtable maps (verified, 2026-05-28)
- [v5-validation-status.md](v5-validation-status.md) — engine-family validation tracker
- [docs/guides/v5-doc-validation-workflow.md](../guides/v5-doc-validation-workflow.md) — orchestrator playbook including "Why no annotation scripts"
- [docs/guides/v5-evidence-header.md](../guides/v5-evidence-header.md) — frontmatter schema
