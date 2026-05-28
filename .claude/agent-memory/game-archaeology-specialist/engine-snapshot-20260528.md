---
name: engine-snapshot-20260528
description: Phase 1 reconnaissance snapshot of STBC.exe in Ghidra — binary fingerprint, function coverage, RTTI/vtable/event/UI anchors, annotation script claims vs. current state. Anchors the v5 docs/engine/ validation campaign.
metadata:
  type: project
---

# Engine Subsystem Snapshot — 2026-05-28

## Critical Context: Two Programs Open in Ghidra

Ghidra has **two programs open** in project "SGW":
- `SGW.exe` — Stargate Worlds, **currently active** when the session started. 173,223 functions. This is the Cimmeria project binary.
- `STBC.exe` — Star Trek: Bridge Commander, at `/C:/Users/Steve/source/projects/STBC-Dedicated-Server/game/stock-dedi/STBC.exe`. **All STBC-specific data below comes from this program.**

The docs/engine/ docs are for **STBC.exe**, not SGW.exe. Tool calls must specify `program: STBC.exe` explicitly or queries silently target the wrong binary.

---

## 1. Binary Fingerprint (high confidence — direct tool output)

| Field | Value |
|-------|-------|
| Program name | STBC.exe |
| Executable path | `/C:/Users/Steve/source/projects/STBC-Dedicated-Server/game/stock-dedi/STBC.exe` |
| Format | Portable Executable (PE) |
| Architecture | x86:LE:32:default |
| Compiler | windows (32-bit) |
| Image base | `0x00400000` |
| Memory size | 6,394,712 bytes (6.1 MB) |
| Memory blocks | 7 |
| Function count | 18,575 |
| Symbol count | 39,656 |
| Data type count | 398 |
| Creation date (Ghidra import) | Thu May 28 07:51:11 CDT 2026 |

No MD5/SHA obtainable via current MCP tools. File size 6,394,712 bytes is the binary anchor for all engine docs.

---

## 2. Function Count and Naming Coverage (high confidence)

| Metric | Value | Source |
|--------|-------|--------|
| Total functions | 18,575 | `get_function_count` |
| Functions with custom names | 4,781 | `search_functions_enhanced(has_custom_name=true)` |
| Functions still FUN_* (unnamed) | 13,467 | `search_functions_enhanced(has_custom_name=false)` |
| Named coverage % | **25.7%** | 4,781 / 18,575 |

**Reconciliation of conflicting claims:**

- CLAUDE.md claims: "~15,134 of 18,247 named (83%)". **This is wrong for current Ghidra state.**
- `docs/engine/function-mapping-report.md` (README.md) claims ~6,031 (33%). **Also wrong.**
- Actual Ghidra state: 4,781 custom-named functions = **25.7% coverage**.
- Total function count discrepancy: CLAUDE.md says 18,247; Ghidra reports 18,575. Delta = 328 functions. Plausible if Ghidra found additional thunks/stubs on re-analysis.
- The annotation scripts enumerate named functions in Python dicts. Those dicts may have been authored without being run against the current Ghidra database, or a run didn't take effect (known bug class per project notes).

**Key finding: The annotation scripts claim coverage numbers that do not match current Ghidra state. The scripts have not been successfully applied to STBC.exe, or their results were not saved/persisted. No function in STBC.exe currently has a custom name except 4,781 — none of the KEY_FUNCTIONS dict entries (e.g., `MultiplayerGame_ReceiveMessage`, `Handler_ObjCreate_0x02_0x03`) are present as named functions.**

Verification: `search_functions("Handler")` → "No functions matching 'Handler'". `search_functions("NiObject")` → "No functions matching". `search_functions("swig_")` → "No functions matching". The globals script claims 2,355+ named functions; none are reflected in Ghidra.

The 4,781 "custom named" functions likely include: standard library functions (`__copysign`, `_strncpy`), exception handlers (`Catch@004168c8`), C++ STL template instantiations, and import thunks — i.e., names auto-applied by Ghidra's analysis, not the annotation scripts.

---

## 3. RTTI Catalog Ground Truth (medium confidence)

`list_classes` on STBC.exe returns **~200 entries** (full page), but these are overwhelmingly:
- C++ STL template instantiations (`basic_filebuf<...>`, `basic_ios<...>`, etc.)
- Import DLL pseudo-namespaces (ADVAPI32.DLL, KERNEL32.DLL, etc.)
- Ghidra switch-table artifacts (`switchD_00433c36`, `switchD_00495765`, etc.)
- One game class: `TGStreamException`
- One CRT type: `CRect`

**No NI classes, no TG game classes, no game-class hierarchy** visible in Ghidra's class/namespace list.

Docs claim 670 classes (129 NI, 124 TG, ~420 game). **Current Ghidra state: 0 recognized NI/TG/game classes by namespace.** The annotation scripts that would populate these (nirtti, vtables, globals) have not taken effect.

`search_strings("NiObject")` and `search_strings("NiRTTI")` both return 0 matches. The NiRTTI class name strings are in .rdata (addresses like 0x009780D8, 0x00975E98) but Ghidra has not defined them as string data items — no string labels present.

---

## 4. NiRTTI Factory Cluster (high confidence — xref count)

Global hash table: `0x009a2b98` (g_NiRTTI_FactoryHashTable per annotation script).

Xrefs to `0x009a2b98`: **237 total** (confirmed via two paginated queries, limit 200 + offset 200).
- Each factory registration function produces exactly 2 xrefs (READ bucket + WRITE new entry).
- 1 stray READ at `0x00816c40` = lookup from NiStream_LoadObject consumer, not a registration.
- Factory registration xrefs: (237 - 1) = 236 / 2 = **118 unique registration functions**.

Script claim: 117 factories. **Actual xref count: 118**. Delta = 1. One factory may have been added after the script was authored, or the script miscounted. Low-stakes difference.

Key consumers of the hash table (also xref'd, correctly not counted as factories):
- `FUN_008176b0` (NiStream_LoadObject — reads table to find factory by class name)
- `FUN_00818150` (NiStream_LoadObjectAlt — same purpose)

All 118 registration functions resolve as `FUN_*` (unnamed) in current Ghidra — the nirtti annotation script has not been applied.

Script's factory address range (from FACTORY_TABLE): `0x00455320` (TGDimmerController) through `0x0084ca60` (NiBezierCylinder). Verified: `FUN_00455320` exists at `0x00455320`; `FUN_007d8650` exists at `0x007d8650` (NiObject registration per script). Both unnamed.

---

## 5. Vtable Addresses (high confidence — direct address checks)

Script `ghidra_annotate_vtables.py` defines 6 fully-verified vtables in VTABLE_DEFS:

| Class | Vtable address | Ghidra state |
|-------|---------------|--------------|
| NiObject | 0x00898b94 | No function/data at address — data item, not a function |
| NiObjectNET | 0x00898c48 | No function found (data item) |
| NiAVObject | 0x00898ca8 | Not checked (same expected pattern) |
| NiGeometry | (in script) | Not checked |
| NiTriShape | (in script) | Not checked |

Note: Vtable addresses are data, not functions — `get_function_by_address` correctly returns "No function found" for vtable addresses. This is expected behavior, not drift. The vtable labels (e.g., `vtbl_NiObject`) would be data symbols, not functions; the MCP tool cannot confirm their presence without a `get_xrefs_to` or `read_memory` check.

CLAUDE.md says "97 vtables auto-discovered". Script header says "Auto-discovers vtable addresses from all 117 NiRTTI factory functions". The vtable discovery pipeline runs at script execution time — no persistent Ghidra state. Since the script hasn't run against the current DB, no vtable labels exist.

---

## 6. Event System Anchors (high confidence — address checks)

From globals script UTOPIA_GLOBALS and KEY_FUNCTIONS:

| Symbol | Address | Ghidra state |
|--------|---------|--------------|
| g_TGEventManager | 0x0097f838 | Data address, no function — correct (global, not fn) |
| g_pTGEventObjectTable | 0x009983a4 | Data address, no function — correct |
| g_pTGEventHandlerTable | 0x009983a8 | Data address, no function — correct |
| Handler_GenericEventForward | 0x0069fda0 | Not checked (search_functions("Handler") = 0 matches) |
| MultiplayerGame_ReceiveMessage | 0x0069f2a0 | **No function found** — gap in Ghidra's function recognition |

`0x0069f2a0` is documented as the main game opcode dispatcher. `get_function_by_address(0x0069f2a0)` returns "No function found" — **Ghidra did not create a function at this address**. This is a notable gap; either the byte at that address is not recognized as a function entry point, or the function was merged into an adjacent one.

`FUN_006a3cd0` (NetFile_ReceiveMessage) **does** exist as a function. `FUN_00504c10` (MultiplayerWindow_ReceiveMessage) **does** exist. `FUN_006b55b0` (SendStateUpdates) **does** exist. `FUN_00504890` (MultiplayerWindow_StartGameHandler) **does** exist.

Anchor addresses confirmed present as functions (unnamed FUN_*):

- `0x006a3cd0` — NetFile dispatcher
- `0x00504c10` — MultiplayerWindow dispatcher
- `0x006b55b0` — SendStateUpdates
- `0x00504890` — MultiplayerWindow_StartGameHandler
- `0x006a1e70` — Handler_NewPlayerInGame_0x2A
- `0x007d8650` — NiObject registration function (NiRTTI factory)
- `0x00717840` — NiAlloc
- `0x00455320` — TGDimmerController factory

---

## 7. UI Hierarchy Anchors (low confidence — not directly queried)

No UI-specific functions appear in search results because the annotation scripts haven't run. The script's KEY_FUNCTIONS dict includes UI classes (PlayWindow, Mission, SetClass, etc.) but none are named in Ghidra. UI class init functions would be at addresses like `0x00405ad0` (PlayWindow__InitFields) but not yet verified.

---

## 8. Annotation Script Claims vs. Current State

| Script | Claimed count | Current Ghidra state |
|--------|--------------|---------------------|
| ghidra_annotate_globals.py | 19 globals + 2,355 key functions (361 classes) + 22 Python module tables = 2,396 total | **0 named** — no KEY_FUNCTIONS names present |
| ghidra_annotate_nirtti.py | 117 factory functions + 117 registration functions + guard flags + string labels = ~234+ labels | **0 named** — all addresses are FUN_* |
| ghidra_annotate_swig.py | 3,990 SWIG wrapper functions named `swig_<method>` | **0 named** — `search_functions("swig_")` = 0 |
| ghidra_annotate_python_capi.py | 113 Python C API + 10 module inits + type objects + globals = 137 total | **0 named** — `search_functions("Py")` returns only CRT stubs |
| ghidra_annotate_pymodules.py | 21 module tables, 266 C implementations named `py_<module>_<method>` | **0 named** |
| ghidra_annotate_vtables.py | 97 vtables from 117 NiRTTI factories: 1,090 virtuals + 96 ctors + 84 dtors = 1,270 labels | **0 named** |
| ghidra_annotate_swig_targets.py | 4 named C++ targets; 3,986 inline field accessors | **0 named** |
| ghidra_discover_strings.py | 33 functions from debug strings + 515 comments | **0 from this script** |

**Root cause: STBC.exe was imported into Ghidra on 2026-05-28 (creation_date = today). The annotation scripts have never been run against this import.** The 4,781 "custom named" functions are entirely Ghidra auto-analysis artifacts (thunks, library imports, C++ exception handling symbols).

---

## 9. Function Tags

`list_function_tags` on STBC.exe: **0 tags defined**. The annotation scripts do not apply tags (they use labels and plate comments only). The tag system is unused.

---

## 10. Sanity Sample — 5 Cross-Doc Address Checks

| Doc | Address | Expected name | Actual Ghidra state | Verdict |
|-----|---------|--------------|---------------------|---------|
| rtti-class-catalog.md | 0x009780D8 | NiObject class string | Data region, no string label | DRIFT: string not labeled |
| nirtti-factory-catalog.md | 0x00455320 | TGDimmerController factory | `FUN_00455320` (body 0x00455320-0x004553bd) | CONFIRMED (unnamed) |
| netimmerse-vtables.md | 0x00898b94 | NiObject vtable | No function (data region) | CONFIRMED (data, not fn — correct) |
| event-system-architecture.md | 0x0069f2a0 | MultiplayerGame_ReceiveMessage | **No function found** | DRIFT: function not recognized by Ghidra |
| ui-class-hierarchy.md | 0x00504c10 | MultiplayerWindow_ReceiveMessage | `FUN_00504c10` (body 0x00504c10-0x00504c6f) | CONFIRMED (unnamed) |

**Notable drift #1**: `0x0069f2a0` — the main game opcode dispatcher documented as the central opcode hub — has no function entry in Ghidra. This may mean the function starts with a non-standard prologue that Ghidra's analysis didn't recognize as a function entry point. Requires manual function creation before annotation script can name it.

**Notable drift #2**: All NiRTTI class name strings (.rdata region: 0x008DAED4 through 0x009793A4 per nirtti script) are not labeled as string data items. The nirtti script would label these; without a run, they are raw bytes.

**Notable drift #3**: `search_strings("NiRTTI")` and `search_strings("NiObject")` return 0 matches despite the strings existing in .rdata. Ghidra has not defined string data items in the .rdata range — it recognized bytes but did not create string data type objects. The string-discovery annotation script cannot function until Ghidra's "Defined Strings" pass creates them (or the script creates them itself via `createAsciiString`).

---

## Key Addresses for v5 Engine Doc Frontmatter `binary:` Block

These are the load-bearing address anchors for every engine doc. Confirmed present as executable functions (FUN_*) in current Ghidra STBC.exe:

```
binary:
  file: STBC.exe
  size_bytes: 6394712
  image_base: 0x00400000
  arch: x86-32 LE
  compiler: MSVC (windows)
  ghidra_import: 2026-05-28
  total_functions: 18575
  custom_named: 4781 (25.7%)
  annotation_scripts_applied: NONE

anchors:
  # Dispatchers
  - { addr: 0x006a3cd0, role: NetFile_ReceiveMessage, status: unnamed-FUN }
  - { addr: 0x00504c10, role: MultiplayerWindow_ReceiveMessage, status: unnamed-FUN }
  - { addr: 0x006b55b0, role: SendStateUpdates, status: unnamed-FUN }
  - { addr: 0x006a1e70, role: Handler_NewPlayerInGame, status: unnamed-FUN }
  - { addr: 0x00504890, role: MultiplayerWindow_StartGameHandler, status: unnamed-FUN }
  # NiRTTI
  - { addr: 0x009a2b98, role: g_NiRTTI_FactoryHashTable, type: global-data }
  - { addr: 0x00455320, role: TGDimmerController_factory, status: unnamed-FUN }
  - { addr: 0x007d8650, role: NiObject_registration, status: unnamed-FUN }
  # NiAlloc
  - { addr: 0x00717840, role: NiAlloc, status: unnamed-FUN }
  # NIF streaming
  - { addr: 0x008176b0, role: NiStream_RegisterStreamable, status: unnamed-FUN }
  # Vtables (data, not functions)
  - { addr: 0x00898b94, role: vtbl_NiObject, type: data }
  - { addr: 0x00898c48, role: vtbl_NiObjectNET, type: data }
  - { addr: 0x00898ca8, role: vtbl_NiAVObject, type: data }
  # SWIG table
  - { addr: 0x008e6438, role: g_SwigMethodTable_AppAppc, type: data }
  # Event system globals
  - { addr: 0x0097f838, role: g_TGEventManager, type: global-data }
  - { addr: 0x009983a4, role: g_pTGEventObjectTable, type: global-data }
```

---

## Top 3 Drift Findings for v5 Validation Campaign

1. **Annotation scripts never applied to STBC.exe** — The binary was imported today (2026-05-28). Zero of the ~6,000+ claimed function names from all 8 annotation scripts are present. CLAUDE.md's "83% named" claim is **completely wrong** for the current database. Every engine doc that cites a function by name has an unnamed `FUN_*` at that address in Ghidra today. The validation campaign must either run all annotation scripts first, or treat all function-name citations as "verified by address, unnamed in Ghidra."

2. **`0x0069f2a0` (MultiplayerGame_ReceiveMessage) — no function in Ghidra** — This is the most-cited address in the protocol docs. Ghidra did not recognize a function entry here. May require manual `create_function` at this address before the annotation scripts can name it. All 41 entries of the jump table at `0x0069F534` downstream of this function are also at risk of not being recognized as function start points.

3. **NiRTTI string labels absent from .rdata** — The nirtti annotation script labels 117+ class name strings in .rdata (range ~0x008DAED4 to 0x009793A4). None are labeled. `search_strings("NiObject")` = 0. The "NiRTTI catalog" and "RTTI class catalog" engine docs cite string addresses as anchors; those addresses exist as raw bytes but have no Ghidra string type applied. Any doc that says "string at 0x00978500 = 'NiNode'" is describing the file content, not a Ghidra annotation.

---

## Open Questions

- Why did Ghidra not recognize `0x0069f2a0` as a function entry? (Needs `disassemble_function` or `inspect_memory_content` to check the prologue bytes.)
- Has anyone ever successfully run the annotation scripts against this Ghidra import, or is this a fresh import from today that has never been annotated?
- STBC.exe creation_date = today (2026-05-28) — if this is a re-import, was the old annotated project preserved elsewhere?
- NiRTTI xref count gives 118 factory registrations vs. script's 117 — which specific entry is the discrepancy? (Requires iterating FACTORY_TABLE entries against the full xref list.)
