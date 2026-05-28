> [docs](../README.md) / [engine](README.md) / v5-validation-status.md

---
title: Engine Docs V5 Validation Status
type: reference
audience: re-engineer
status: partial
validated: 2026-05-28
methodology: FUNCTION_DOC_WORKFLOW_V5
evidence_refs:
  - docs/engine/README.md
  - docs/engine/rtti-class-catalog.md
  - docs/engine/nirtti-factory-catalog.md
  - docs/engine/netimmerse-vtables.md
  - docs/engine/tg-hierarchy-vtables.md
  - docs/engine/gamebryo-cross-reference.md
  - docs/engine/event-system-architecture.md
  - docs/engine/ui-class-hierarchy.md
  - docs/engine/function-map.md
  - docs/engine/function-mapping-report.md
  - docs/engine/decompiled-functions.md
companions:
  - docs/engine/README.md
---

# Engine Docs V5 Validation Status

Tracker for the v5 evidence-standard re-validation campaign on `docs/engine/`. This document
is an inventory of what the existing 10 engine docs claim today and how much of each claim
is backed by Ghidra-anchored evidence. It does **not** validate or correct any claim;
validation happens in subsequent phases. The archaeology specialist is producing a parallel
Ghidra-state snapshot to be merged with this inventory.

## 1. Campaign overview

The engine docs are being re-validated in foundation→leaves order against the
`FUNCTION_DOC_WORKFLOW_V5` evidence standard. Foundation docs (function counts, RTTI catalog,
factory registrations) anchor the binary's gross structure; mid-layer docs (vtables, Gamebryo
cross-reference) depend on the foundation; leaf docs (event system, UI hierarchy, decompiled
function notes) cite the mid-layer. Validating in this order means each pass can lean on
already-anchored evidence instead of re-deriving it.

Expected outputs per doc: (1) every load-bearing claim either cites a hex address / `FUN_xxxx`
that the archaeology snapshot confirms, or is demoted to "disputed" / "needs evidence"; (2)
status frontmatter (`status: verified | partial | disputed | stale`); (3) cross-links to
the canonical claim location so other docs can cite-by-reference; (4) any inconsistencies
between docs (e.g., conflicting totals) resolved with the binary as authority. CLAUDE.md's
doc-update map and the section README will be batch-updated at the end of Phase B.

## 2. Validation order (foundation → leaves)

Order reflects dependency direction: each row's evidence is consumed by all rows below it.

| Order | Doc | Layer | Pre-existing depends on | Current status |
|-------|-----|-------|--------------------------|----------------|
| 1 | function-map.md | Foundation: function totals + range partition | (none) | partial (2026-05-28) — foundation verified, named-function lists carry confidence: low |
| 2 | function-mapping-report.md | Foundation: coverage % + script outputs | function-map.md | partial (2026-05-28, validated 6th in campaign per documentation-writer's swap recommendation) — pre-v5 Pass narratives removed; script reference + NI/Gb delta verified; current coverage 25.8% |
| 3 | rtti-class-catalog.md | Foundation: 670 class name strings | function-map.md | partial (2026-05-28) — foundation + TG section verified; NI/game-specific deferred |
| 4 | nirtti-factory-catalog.md | Foundation: 117 factory registrations | rtti-class-catalog.md | verified (2026-05-28) — first doc in the campaign to reach `verified`; all rows confidence high/medium with documented reasoning |
| 5 | netimmerse-vtables.md | Mid: 6 NI core vtable layouts | nirtti-factory-catalog.md | verified (2026-05-28) — second doc in the campaign to reach `verified`; NiTriShape vtable reassigned to NiTriBasedGeom + new canonical NiTriShape vtable added |
| 6 | tg-hierarchy-vtables.md | Mid: TG/Ship vtable chain | netimmerse-vtables.md | verified (2026-05-28) — third doc in the campaign to reach `verified`; 9-vtable Ship inheritance chain end-to-end confirmed via 8 ctor decompiles; TGObject 12-slot map locked at high confidence |
| 7 | gamebryo-cross-reference.md | Mid: NI 3.1 vs Gb 1.2 / MWSE | netimmerse-vtables.md | partial (2026-05-28) — central size correction landed (NiAVObject 0x90→0xC8, NiNode 0xB0→0xE8); ~110 row-level external-corpus claims pattern-extrapolated |
| 8 | event-system-architecture.md | Leaf: TGEventManager dispatch | tg-hierarchy-vtables.md | partial (2026-05-28) — vtables + sizes + layouts anchored; TGEvent factory-ID corrected; unanchored method names dropped |
| 9 | ui-class-hierarchy.md | Leaf: UI inheritance + event IDs | event-system-architecture.md, tg-hierarchy-vtables.md | partial (2026-05-28) — TopWindow/PlayWindow conflation corrected (TopWindow at 0x009878cc, PlayWindow at 0x0097e238 — two distinct globals); MainWindow type IDs expanded 8→12 (types 3, 4, 6 new; types 5 and 7 revised); TopWindow's actual 5 children are {4, 2, 8, 9, 10} not {0, 2, 5, 8, 10}; STWidget / STRadioGroup / TGScrollablePane dropped or demoted (no binary string anchors); doc rendered with v5 frontmatter |
| 10 | decompiled-functions.md | Leaf: per-function notes (net/checksum/event) | function-map.md, event-system-architecture.md | pending |
| — | README.md | Index only — refreshed at end of Phase B | all above | pending |

## 3. Per-doc inventory

### 3.1 README.md

- **Size:** 867 bytes
- **Doc type:** reference (index table)
- **Load-bearing claims:** 7 (one per indexed doc; each row encodes a doc-level total)
- **Currently cited (address/count anchors):** 0 hex addresses; 4 numeric counts ("670", "129", "124", "~420", "117", "129", "18K", "~6,031", "33%")
- **Top load-bearing claims:**
  - rtti-class-catalog.md totals: "670 classes: 129 NI, 124 TG, ~420 game"
  - nirtti-factory-catalog.md: "117 NiRTTI factory registrations with addresses"
  - gamebryo-cross-reference.md: "129 NI classes cross-referenced"
  - netimmerse-vtables.md: "Vtable maps for 6 core NI classes"
  - function-mapping-report.md: "~6,031 functions named (33%)"
- **Cross-references in:** docs/README.md (root index)
- **Cross-references out:** all 7 engine docs
- **Visible debt:** "33%" coverage figure is stale (see §4 — CLAUDE.md says 83%, function-mapping-report.md says 83%); README still cites the older 33% number. No row for `tg-hierarchy-vtables.md` despite the file existing.
- **Difficulty:** trivial (numbers only)

### 3.2 rtti-class-catalog.md

- **Size:** 31,075 bytes
- **Doc type:** reference
- **Load-bearing claims:** ~250 (22 MSVC RTTI rows + 129 NI rows + 124 TG rows + ~420 game-specific rows; plus 8 summary rows + 32 SWIG-binding rows + 6 hash-bucket / address-range claims)
- **Currently cited:** ~250 — every catalog row carries a hex address. SWIG method counts (94 for TGUIObject, 63 for TGSound, etc.) are uncited.
- **Top load-bearing claims:**
  - "stbc.exe was compiled with MSVC RTTI disabled (`/GR-`) for all game and engine code"
  - "22 MSVC TypeDescriptor structures exist; all CRT/STL except TGStreamException at 0x0095AD10"
  - "129 NetImmerse, 124 TG, ~420 game-specific = ~670 total unique C++ classes"
  - "NiRTTI factory hash table at DAT_009a2b98"
  - "NiNode registration: FUN_007e3670; factory: FUN_007e5450; string at 0x00978500"
- **Cross-references in:** README.md, gamebryo-cross-reference.md, function-mapping-report.md
- **Cross-references out:** nirtti-factory-catalog.md (twice)
- **Visible debt:** Summary table at bottom says "114 classes with SWIG bindings, ~1,340 wrapper methods" but no per-class evidence trail to the SWIG method counts. Some address rows look duplicated (TGAction and TGAnimAction both at 0x00913EE3 — flagged for archaeology to verify). "Total class-like name strings: ~1,179" is a count without a derivation method.
- **Difficulty:** moderate (address rows are address-anchored but verifying 670 strings still in the binary is mechanical; SWIG counts are harder)

### 3.3 nirtti-factory-catalog.md

- **Size:** 23,056 bytes
- **Doc type:** reference
- **Load-bearing claims:** ~125 (117 factory rows + 8 architecture/summary rows)
- **Currently cited:** ~125 — every row has class string addr, factory fn, registration fn, guard flag, all hex.
- **Top load-bearing claims:**
  - "Total registration functions: 117 (113 Ni + 2 TG + 2 others)" — but the header also says "Complete Factory Registration Table (115 entries)" and the table itself numbers entries 1–117. Inconsistency.
  - "Hash table at DAT_009a2b98 with 37 buckets, vtable PTR_FUN_0088b7c4"
  - "234 xrefs to DAT_009a2b98"
  - "Factory pattern: 100% consistent across all 115 classes"
  - "Hash node = 0x0C bytes (className ptr, factory ptr, next ptr)"
- **Cross-references in:** rtti-class-catalog.md, README.md
- **Cross-references out:** rtti-class-catalog.md (Classes-NOT-in-table section)
- **Visible debt:** Header says "115 entries" but table has 117 numbered rows; summary says "117 registration functions, 113 Ni + 2 TG = 115" (math inconsistency — 113+2=115 but the table has 117). Some factory function names start with `LAB_` or `DAT_` (LAB_0078e6e0, DAT_007d8810) indicating Ghidra hasn't recognized them as functions — these need disambiguation. Bucket count "37" appears as both 0x25 (correct hex) and 37 (decimal) — consistent, but flagged for cross-check.
- **Difficulty:** trivial (mechanical xref count)

### 3.4 netimmerse-vtables.md

- **Size:** 15,965 bytes
- **Doc type:** reference (with some explanation in the methodology section)
- **Load-bearing claims:** ~160 (6 vtable address claims + 6 slot count claims + 6 object size claims + ~135 individual vtable slot entries with addresses + ~10 methodology / cross-class invariant claims)
- **Currently cited:** ~155 — almost every slot row carries a function address. ~5 inheritance/delta claims are derived from counts.
- **Top load-bearing claims:**
  - "NiObject vtable at 0x00898b94 has 12 slots; GetRTTI at slot 0, scalar_deleting_dtor at slot 10"
  - "NiAVObject adds 27 virtuals over NiObjectNET (slots 12-38), vtable 0x00898ca8, 39 slots total"
  - "NiNode adds 4 new virtuals over NiAVObject (slots 39-42): AttachChild, DetachChild, DetachChildAt, SetAt"
  - "NiGeometry slot 49 is `__purecall` (0x00859a0b) — confirms abstract class"
  - "Slot 11 universally = 0x0040da50 (no-op, never overridden) across NiObject/NiObjectNET/NiAVObject/NiNode"
  - "MSVC scalar deleting destructor is at slot 10, NOT slot 0 (opposite of Gamebryo 1.2 layout)"
- **Cross-references in:** rtti-class-catalog.md, gamebryo-cross-reference.md, function-mapping-report.md
- **Cross-references out:** none explicit (refers to NIF.xml and Gb 1.2 as external)
- **Visible debt:** Many slots labelled "(unknown)" or with proposed names + question mark (slots 12-21 of NiAVObject all have "?" suffixes). NiGeometry table shows "..." mid-table — incomplete. NiTriShape table only shows slots 0-3 — incomplete. Object sizes in the bottom table disagree with the header sizes (e.g., NiAVObject header says "0x9C" but bottom table says "0xC4 / 196 bytes" — needs reconciliation).
- **Difficulty:** hard (semantic claims about virtual method behavior need decompiler-level evidence per slot)

### 3.5 tg-hierarchy-vtables.md

- **Size:** 14,675 bytes
- **Doc type:** reference
- **Load-bearing claims:** ~140 (10 inheritance-chain claims + ~130 individual vtable slot rows across TGObject, TGStreamedObject, TGStreamedObjectEx, TGEventHandlerObject, TGSceneObject, ObjectClass, PhysicsObjectClass, DamageableObject, Ship)
- **Currently cited:** ~130 — most slot rows include both function address and Ship/DO override address.
- **Top load-bearing claims:**
  - "Ship inheritance: TGObject → TGStreamedObject → TGStreamedObjectEx → TGEventHandlerObject → TGSceneObject → ObjectClass → PhysicsObjectClass → DamageableObject → Ship"
  - "TGObject vtable layout differs from NiObject: slot 0 = scalar_deleting_dtor, slot 3 = DebugPrint (NOT GetRTTI at slot 0)"
  - "TGObject vtable at 0x00896278 — CORRECTED from 0x008963BC (which is TGHashTable, not TGObject)"
  - "DamageableObject has 92 slots (0-91), Ship has 92 slots, Ship does NOT add new slots"
  - "Ship size 0x328; vtable 0x00894340; slots 82-85 are the collision detection/damage pipeline"
- **Cross-references in:** none from other engine docs (this file is not in README.md)
- **Cross-references out:** none
- **Visible debt:** **Not listed in docs/engine/README.md** — orphan from index perspective. Internal duplicate line at line 240–241 ("~40 vtable entries" appears twice). Multiple "(unknown)" slots through middle of Ship vtable (slots 9-11, 16-18, 36-47, parts of 49-66). Contains explicit "CORRECTED from earlier doc" markers indicating prior drift. Mentions "NOTE: 0x008963BC is NOT TGObject's vtable" — flags a known-bad earlier claim worth verifying is fully scrubbed from sibling docs.
- **Difficulty:** hard (inheritance-chain claim requires decompiling 9 constructors in order)

### 3.6 gamebryo-cross-reference.md

- **Size:** 21,464 bytes
- **Doc type:** explanation + reference (mixed)
- **Load-bearing claims:** ~115 (5 size-delta rows + 87 "matched in Gb 1.2" rows + 42 "NI 3.1-only" rows + ~15 V3.1-specific NIF field claims, of which only 4 reference stbc.exe directly; the rest are claims about external sources)
- **Currently cited:** ~10 stbc.exe-anchored claims (struct sizes: 0x08, 0x14, 0x90, 0xB0; field offsets in NiObjectNET / NiAVObject / NiNode). The bulk of the doc cites external evidence (Gb 1.2 source paths, MWSE static_asserts, nif.xml line numbers) — these are claims about external corpora, not stbc.exe.
- **Top load-bearing claims:**
  - "NI 3.1 NiObjectNET size = 0x14 (vs Gb 1.2 0x1C), difference is +8 bytes — confirmed by MWSE static_assert"
  - "NI 3.1 NiAVObject size = 0x90 (vs Gb 1.2 ~0x9C), difference is +12 bytes (ExtraData + CollisionObject)"
  - "129 NI classes in stbc.exe; 87 match Gb 1.2; 42 are NI 3.1-only; 21 of 42 have nif.xml field defs"
  - "BC's NI 3.1.1 has GetRTTI at slot 0, destructor at slot 10 — MWSE NI 4.0.0.2 has destructor at slot 0, GetRTTI at slot 1"
  - "Gb 2.6 does NOT re-add the 42 NI 3.1-only classes — they are genuinely unique to NI 3.x"
- **Cross-references in:** rtti-class-catalog.md, README.md, netimmerse-vtables.md
- **Cross-references out:** docs/netimmerse-vtables.md, niftools/nifxml (external), MWSE (external), Gb 1.2 (external)
- **Visible debt:** "Practical Usage Guide" section is how-to mixed into a reference doc — Diátaxis violation. Class-count math: text says "21 of 42 have nif.xml field definitions" but elsewhere claims "21 of 42 are runtime-only" — sums to 42 only if categories are disjoint; need verification. NiObjectNET size: header table shows 0x14 vs Gb 1.2 0x1C (+8), but MWSE table at line 348 shows "MWSE NI 4.0 = 0x14, BC NI 3.1 = 0x14" — claim is consistent but the delta is described inconsistently across the doc.
- **Difficulty:** moderate (size claims trivial; field-presence claims require both binary and external source confirmation)

### 3.7 event-system-architecture.md

- **Size:** 5,867 bytes
- **Doc type:** explanation (architectural overview)
- **Load-bearing claims:** ~25 (5 class architecture claims + 6 layout claims + 4 vtable address claims + 6 event-ID range claims + 4 dispatch-flow claims)
- **Currently cited:** ~6 (TGConditionHandler vtable 0x00896104, TGCallback vtable 0x008960f4, event IDs 0x30001/0x40001/0x800XXX, 0x8000E0–E5, 0x800058–80005A, 0x25-bucket count). The rest of the architecture description is uncited prose.
- **Top load-bearing claims:**
  - "TGCallback 0x14 bytes; vtable 0x008960f4; flags bit0=isMethod, bit1=isPython, bit2=active, bit3=pendingDelete"
  - "TGConditionHandler vtable 0x00896104; manages sorted arrays with binary search; reentrant"
  - "TGInstanceHandlerTable lives at TGEventHandlerObject+0x10, uses 0x25-bucket (37-bucket) hash"
  - "TGHandlerListEntry = 0xC bytes (object ptr, callback ptr, deleted flag)"
  - "Event IDs 0x30001-0x40001 = input; 0x800XXX = game; 0x8000E0-0x8000E5 = combat (SetPhaserLevel, Cloak)"
- **Cross-references in:** none (event-system not yet linked to from other engine docs)
- **Cross-references out:** ui-class-hierarchy.md
- **Visible debt:** Class layout tables use offsets but don't cite source addresses where the structure is allocated/instantiated. "Phase 8C, 2026-02-24" provenance is in the doc body — fine for now, but should move to frontmatter. Dispatch flow steps 1-5 are prose with no function-address anchors (no FUN_006da2c0 / FUN_006db380 references — those exist in function-map.md and decompiled-functions.md but aren't pulled in here). Save/load serialization claims are entirely uncited.
- **Difficulty:** moderate (layouts moderate; dispatch semantics hard)

### 3.8 ui-class-hierarchy.md

- **Size:** 5,622 bytes
- **Doc type:** reference
- **Load-bearing claims:** ~50 (1 inheritance tree + 5 TGUIObject layout rows + 7 flag-bit rows + 9 MainWindow type ID rows + 5 TopWindow child rows + 2 PlayWindow/PlayViewWindow distinction rows + 9 PlayWindow layout rows + 9 button bitfield rows + 24 event ID rows + 3 RTTI type IDs + 2 TGL file rows)
- **Currently cited:** ~8 hex addresses (TopWindow at 0x0097e238, TopWindow constructor 0x0050c430, TopWindow__FindMainWindow 0x0050e1b0, PlayWindow ctor 0x00405c10, PlayViewWindow ctor 0x004fc480, RTTI 0x810F/0x205/0x80EA). Most event-ID and offset claims are uncited.
- **Top load-bearing claims:**
  - "Inheritance: TGEventHandlerObject → TGUIObject → {TGPane, ...} where TGPane has children TGScrollablePane, TGWindow, STWidget, TGIcon, TGParagraph, TGRootPane"
  - "PlayWindow (Game object, ctor 0x00405c10) and PlayViewWindow (UI viewport, ctor 0x004fc480) were both mislabeled 'PlayWindow' previously"
  - "TopWindow at g_TopWindow = 0x0097e238 creates 5 children: MainWindow, ConsoleWindow, MultiplayerWindow, PlayWindow, CinematicWindow"
  - "MainWindow RTTI type = 0x810F; FindMainWindow checks +0x4C type ID"
  - "TGDialogWindow__AddButtons bitfield: 0x001=OK, 0x002=Cancel, ..., 0x200000=read-only"
- **Cross-references in:** event-system-architecture.md
- **Cross-references out:** none (event-system-architecture cross-link is one-way)
- **Visible debt:** PlayWindow layout offsets (+0x38 score, +0x3C rating, etc.) and MultiplayerGame extension (+0x74 playerSlots[16], +0x1F8 readyForNewPlayers, +0x1FC maxPlayers) are uncited. Many of these correspond to claims in CLAUDE.md ("ReadyForNewPlayers=1, MaxPlayers=8") but the offset-to-claim mapping is not anchored. TGL file list mentions "data/TGL/Multiplayer.tgl" — needs cross-link to packet-related docs that use it.
- **Difficulty:** moderate (offsets need single decompile each; event IDs need xref to RegisterEventHandler calls)

### 3.9 function-map.md

- **Size:** 36,042 bytes
- **Doc type:** reference (the canonical function inventory)
- **Load-bearing claims:** ~250 (20 category totals + 1 grand total + ~75 named functions in summary + ~100 individual FUN_ row claims + ~30 global memory map rows + ~20 cross-reference table rows)
- **Currently cited:** ~250 — every row carries an address. This is the most evidence-dense doc per byte.
- **Top load-bearing claims:**
  - "Total: 18,247 functions (13,333 FUN_, 133 thunks, 86 named imports/CRT, 4,692 Unwind handlers, 3 Catch handlers); address range 0x004010e0 - 0x008879e0"
  - "MultiplayerGame range 0x0069E000-0x006A2FFF has 44 functions"
  - "TGNetwork range 0x006B0000-0x006BFFFF has 225 functions"
  - "NetImmerse/Render range 0x00770000-0x0084FFFF has 2,915 functions"
  - "EventManager global at 0x0097F838; Handler registry at 0x0097F864"
- **Cross-references in:** README.md, function-mapping-report.md, decompiled-functions.md, ui-class-hierarchy.md (implicit)
- **Cross-references out:** function-map.txt (the flat listing)
- **Visible debt:** Many functions listed as `FUN_xxxxxxxx` only — Ghidra's auto-name. After Pass 8C the script has named 1,773 functions (per function-mapping-report.md) but this doc's tables don't reflect that — needs sync. Several "PATCH target REMOVED" comments embedded in the address table (e.g., "0x00438AE6: (was PatchInitTraversal target - REMOVED)") — useful but indicate doc has both live and historical entries mixed.
- **Difficulty:** trivial (counts) / moderate (per-row identification)

### 3.10 function-mapping-report.md

- **Size:** 17,385 bytes
- **Doc type:** explanation + reference (script suite documentation + coverage stats)
- **Load-bearing claims:** ~40 (8 script-output counts + 6 coverage-pct rows + 8 Pass summaries with rename counts + 4 NI/Gb vtable delta rows + ~14 per-pass narrative claims)
- **Currently cited:** ~10 (script function totals; pass rename counts; specific addresses for NI 3.1 vs Gb 1.2 vtable slot counts; PyMethodDef table addresses)
- **Top load-bearing claims:**
  - "~15,209 total named/excluded (83% of 18,247)"
  - "Pass 7 added 1,222 new entries; KEY_FUNCTIONS dict went 331 → 1,553"
  - "Pass 8C added event-system infrastructure: 1,553 → 1,773 function entries, 318 classes"
  - "ghidra_annotate_vtables.py auto-discovers vtables from 97 factories: 1,090 virtuals + 96 constructors + 84 destructors = 1,270 named"
  - "NI 3.1 vs Gb 1.2 vtable counts: NiAVObject 39 vs 27 (+12); NiNode 43 vs 31 (+12); NiGeometry 64 vs 27 (+37)"
- **Cross-references in:** README.md
- **Cross-references out:** none
- **Visible debt:** Coverage table at top says ~15,209 named (83%). README.md says ~6,031 named (33%). CLAUDE.md says ~15,134 named (83%). Three docs, three slightly different totals. NiGeometry "Gb 1.2: 27 slots" vs "NI 3.1: 64 slots" — the +37 delta is suspiciously large; archaeology should verify Gb 1.2 NiGeometry virtual count.
- **Difficulty:** trivial (counts) / moderate (verifying script outputs match reality)

### 3.11 decompiled-functions.md

- **Size:** 9,133 bytes
- **Doc type:** reference (per-function decompilation notes — networking + checksum + event focus)
- **Load-bearing claims:** ~50 (28 function-behavior claims + 22 address-quick-reference rows)
- **Currently cited:** ~50 — every claim is anchored to a `FUN_xxxxxxxx` address.
- **Top load-bearing claims:**
  - "UtopiaModule::InitMultiplayer (0x00445d90): creates TGWinsockNetwork(0x34C) → +0x78, NetFile(0x48) → +0x80, GameSpy(0xF4) → +0x7C"
  - "NetFile_Constructor (0x006a30c0): 3 hash tables capacity 0x25, registers handler for event 0x60001"
  - "NetFile::ReceiveMessageHandler (0x006a3cd0): opcode dispatch 0x20-0x27 (5 cases listed)"
  - "ChecksumRequestSender (0x006a3820): builds 4 requests, queues in hash B, sends #0 immediately"
  - "TGNetwork::Update (0x006B4560): 3 unconditional sub-calls SendOutgoing/Process/Dispatch"
- **Cross-references in:** function-map.md (consolidates these names into Cross-Reference section)
- **Cross-references out:** none
- **Visible debt:** Scope is narrow — networking/checksum/event focus — but doc is named generically "decompiled-functions.md". Could be `multiplayer-decompiled-functions.md` to disambiguate from a hypothetical Ship/AI/render notes doc. Some claims duplicate function-map.md and could become a single source of truth. No frontmatter / metadata at all.
- **Difficulty:** moderate (each function-behavior claim is a single decompile)

## 4. Cross-doc disagreements and documentation debt

Each row is a pre-existing inconsistency to surface; v5 sweep should resolve to the binary as authority.

| # | Disagreement | Sources | Authority candidate |
|---|--------------|---------|---------------------|
| 1 | Function-naming coverage % | README.md says "33%"; function-mapping-report.md says "83%"; CLAUDE.md says "83%" | function-mapping-report.md (most recent + script-output verified) |
| 2 | Named function count | README.md: ~6,031; function-mapping-report.md: ~15,209; CLAUDE.md: ~15,134 | Ghidra ground truth via `list_functions` |
| 3 | NiRTTI table size | nirtti-factory-catalog.md header: "115 entries"; same doc summary: "113 Ni + 2 TG = 115"; same doc table: rows 1-117 | Ghidra xrefs to DAT_009a2b98 |
| 4 | NiAVObject vtable size in netimmerse-vtables.md | Header table: "0x9C bytes"; bottom Object Sizes table: "0xC4 / 196 bytes" | Ghidra vtable boundary at 0x00898ca8 |
| 5 | tg-hierarchy-vtables.md not indexed | Doc exists at docs/engine/tg-hierarchy-vtables.md; not in docs/engine/README.md | Add row to README.md |
| 6 | TGObject vtable address | tg-hierarchy-vtables.md flags previous claim at 0x008963BC as wrong, real one is 0x00896278 | Other docs may still reference the old (bad) addr — needs grep |
| 7 | "21 of 42" double-counting | gamebryo-cross-reference.md: "21 of 42 with nif.xml field definitions" AND "21 of 42 runtime-only" | Categories should partition 42; verify class lists |
| 8 | Duplicate string addresses in rtti-class-catalog.md | TGAction and TGAnimAction both shown at 0x00913EE3 | Re-read both string addresses from binary |
| 9 | function-map.md vs function-mapping-report.md sync | function-map.md still has many `FUN_xxxxxxxx` rows; report says script has named 1,773 of them | function-map.md should reflect post-Pass-8C state |
| 10 | "PATCH target REMOVED" cruft | function-map.md embeds historical patch-removal comments mixed with live function rows | Move to a separate patches-changelog or strip |
| 11 | decompiled-functions.md scope vs name | File covers only multiplayer/network/checksum/event; name implies broader scope | Rename or split |
| 12 | event-system-architecture.md missing function anchors | Doc describes dispatch flow but doesn't name FUN_006da2c0 / FUN_006db380 even though those exist in function-map.md | Add address anchors at first mention |
| 13 | ui-class-hierarchy.md offsets uncited | PlayWindow +0x38 score, +0x3C rating, MultiplayerGame +0x1F8 readyForNewPlayers — all uncited offsets | Each needs an example FUN_ that writes/reads the offset |
| 14 | rtti-class-catalog.md SWIG method counts | Per-class "94 methods" etc. uncited; aggregate "~1,340 wrapper methods" also uncited | Derive from Ghidra by walking PyMethodDef tables |

## 5. Anchor table (collected addresses, function counts, table-base offsets)

These are the cross-doc anchor points the archaeology snapshot should pin. If any of these
diverges from the binary, multiple docs need updates.

### 5.1 Global table anchors

| Anchor | Address / Value | Cited in |
|--------|-----------------|----------|
| NiRTTI factory hash table | DAT_009a2b98 | rtti-class-catalog.md, nirtti-factory-catalog.md, netimmerse-vtables.md |
| NiRTTI hash table vtable | PTR_FUN_0088b7c4 | nirtti-factory-catalog.md |
| NiRTTI hash bucket count | 37 (0x25) | nirtti-factory-catalog.md |
| NiRTTI xref count | 234 | nirtti-factory-catalog.md |
| TGEventManager global | 0x0097F838 | function-map.md, decompiled-functions.md |
| Handler registry | 0x0097F864 (= EventManager+0x2C) | function-map.md, decompiled-functions.md |
| UtopiaModule base | 0x0097FA00 | function-map.md, decompiled-functions.md |
| WSN pointer | 0x0097FA78 (= UtopiaModule+0x78) | function-map.md, decompiled-functions.md |
| NetFile pointer | 0x0097FA80 (= UtopiaModule+0x80) | decompiled-functions.md |
| IsHost flag | 0x0097FA88 | function-map.md |
| TopWindow / Game ptr | 0x0097e238 | function-map.md, ui-class-hierarchy.md |
| TGObject vtable (corrected) | 0x00896278 | tg-hierarchy-vtables.md |
| TGObject vtable (incorrect, flagged) | 0x008963BC | tg-hierarchy-vtables.md (negative claim) |
| TGCallback vtable | 0x008960f4 | event-system-architecture.md |
| TGConditionHandler vtable | 0x00896104 | event-system-architecture.md |

### 5.2 Core NI vtable anchors

| Class | Vtable | Slots | Object size | Cited in |
|-------|--------|-------|-------------|----------|
| NiObject | 0x00898b94 | 12 | 0x08 (or 0x30 per netimmerse-vtables.md header) | netimmerse-vtables.md, gamebryo-cross-reference.md |
| NiObjectNET | 0x00898c48 | 12 | 0x14 | netimmerse-vtables.md, gamebryo-cross-reference.md |
| NiAVObject | 0x00898ca8 | 39 | 0x90 (or 0xC4 — conflict §4 #4) | netimmerse-vtables.md, gamebryo-cross-reference.md |
| NiNode | 0x00898f2c | 43 | 0xB0 (or 0xE8) | netimmerse-vtables.md, gamebryo-cross-reference.md |
| NiGeometry | 0x00899164 | 64 | 0xE0 | netimmerse-vtables.md |
| NiTriShape | 0x00899264 | 68 | 0xE4 | netimmerse-vtables.md |

### 5.3 Core TG/Ship vtable anchors

| Class | Vtable | Slots | Cited in |
|-------|--------|-------|----------|
| TGObject | 0x00896278 | 12 | tg-hierarchy-vtables.md |
| TGStreamedObject | 0x008962F4 | +4 | tg-hierarchy-vtables.md |
| TGStreamedObjectEx | 0x008962A8 | inherits + override | tg-hierarchy-vtables.md |
| TGEventHandlerObject | 0x00896044 | +7 | tg-hierarchy-vtables.md |
| TGSceneObject | 0x00889708 | adds ~27 | tg-hierarchy-vtables.md |
| ObjectClass | 0x00889950 | ~66 | tg-hierarchy-vtables.md |
| PhysicsObjectClass | 0x00894128 | adds 81 | tg-hierarchy-vtables.md |
| DamageableObject | 0x00893D88 | 92 | tg-hierarchy-vtables.md |
| Ship | 0x00894340 | 92 (size 0x328) | tg-hierarchy-vtables.md |

### 5.4 Function counts (foundation)

| Count | Claim | Cited in |
|-------|-------|----------|
| 18,247 | Total functions in stbc.exe | function-map.md, function-mapping-report.md, CLAUDE.md |
| 13,333 | FUN_ entries | function-map.md |
| 4,692 | Unwind handlers | function-map.md |
| ~15,209 | Named/excluded after Pass 8C | function-mapping-report.md |
| ~6,031 | Named (older claim) | README.md (STALE — §4 #1) |
| ~15,134 | Named (CLAUDE.md value) | CLAUDE.md |
| 1,773 | KEY_FUNCTIONS dict size after Pass 8A+8C | function-mapping-report.md |
| 2,396 | annotate_globals.py outputs | function-mapping-report.md |
| 234 | annotate_nirtti.py outputs | function-mapping-report.md |
| 3,990 | annotate_swig.py outputs | function-mapping-report.md |
| 1,270 | annotate_vtables.py outputs (1,090 vfuncs + 96 ctors + 84 dtors) | function-mapping-report.md |
| 137 | annotate_python_capi.py outputs | function-mapping-report.md |
| 266 | annotate_pymodules.py outputs | function-mapping-report.md |
| 33 (+515 comments) | discover_strings.py outputs | function-mapping-report.md |

### 5.5 Class catalog counts

| Count | Claim | Cited in |
|-------|-------|----------|
| 670 | Total unique C++ classes | rtti-class-catalog.md |
| 129 | NetImmerse Ni* classes | rtti-class-catalog.md, gamebryo-cross-reference.md |
| 124 | TG framework classes | rtti-class-catalog.md |
| ~420 | Game-specific classes | rtti-class-catalog.md |
| 22 | MSVC RTTI TypeDescriptors (21 CRT + 1 game) | rtti-class-catalog.md |
| 117 | NiRTTI factory registrations (or 115 — §4 #3) | nirtti-factory-catalog.md |
| 113 | Ni-only factory entries | nirtti-factory-catalog.md |
| 2 | TG factory entries (TGDimmerController, TGFuzzyTriShape) | nirtti-factory-catalog.md |
| 87 | NI classes matched in Gb 1.2 (67%) | gamebryo-cross-reference.md |
| 42 | NI 3.1-only classes | gamebryo-cross-reference.md |
| 21 of 42 | with nif.xml field definitions | gamebryo-cross-reference.md (§4 #7) |
| 114 | TG classes with SWIG bindings | rtti-class-catalog.md |
| ~1,340 | TG SWIG wrapper methods | rtti-class-catalog.md |

### 5.6 Address ranges (function-map.md category boundaries)

These boundaries determine which category a function falls into and are load-bearing for
the function-map taxonomy.

| Range | Category | Function count |
|-------|----------|----------------|
| 0x0040-0x0042 | Core/Base Objects | 646 |
| 0x0043-0x0045 | UtopiaApp/Module | 717 |
| 0x0046-0x004B | UI Framework | 1,241 |
| 0x004C-0x0051 | Windows/Dialogs | 1,112 |
| 0x0052-0x005A | Game Logic/Ships/AI | 2,073 |
| 0x005B-0x0065 | Sparse/Mission | 201 |
| 0x0066-0x0068 | Scene Graph/3D | 527 |
| 0x0069-0x0069D | Game Session | 159 |
| 0x0069E-0x006A2 | MultiplayerGame | 44 |
| 0x006A3-0x006A7 | NetFile/Checksums | 58 |
| 0x006A8-0x006AF | Containers/Hash | 141 |
| 0x006B0-0x006BF | TGNetwork | 225 |
| 0x006C0-0x006CF | Streams/Serialization | 246 |
| 0x006D0-0x006DF | Events/Timers | 327 |
| 0x006E0-0x006EF | Config/VarMgr | 226 |
| 0x006F0-0x006FF | GameSpy/SWIG | 273 |
| 0x0070-0x0076 | Python/SWIG | 1,619 |
| 0x0077-0x0084 | NetImmerse/Render | 2,915 |
| 0x0085-0x0086 | CRT/stdlib | 787 |
| 0x0087-0x0088 | Exception/Unwind | 4,710 |

### 5.7 Key function anchors

| Address | Name | Cited in |
|---------|------|----------|
| 0x0043b4f0 | UtopiaApp_MainTick | function-map.md, decompiled-functions.md |
| 0x00445d90 | UtopiaModule::InitMultiplayer | function-map.md, decompiled-functions.md |
| 0x00451ac0 | SimulationPipelineTick | function-map.md |
| 0x00504890 | MultiplayerWindow::StartGameHandler | function-map.md, decompiled-functions.md |
| 0x0050c430 | TopWindow constructor | ui-class-hierarchy.md |
| 0x0050e1b0 | TopWindow__FindMainWindow | ui-class-hierarchy.md |
| 0x0069efe0 | RegisterMPGameHandlers | function-map.md |
| 0x006a30c0 | NetFile_Constructor | function-map.md, decompiled-functions.md |
| 0x006a3820 | ChecksumRequestSender | function-map.md, decompiled-functions.md |
| 0x006a3cd0 | NetFile::ReceiveMessageHandler | function-map.md, decompiled-functions.md |
| 0x006a4260 | ChecksumResponseEntry | function-map.md, decompiled-functions.md |
| 0x006a4560 | ChecksumResponseVerifier | function-map.md, decompiled-functions.md |
| 0x006a5df0 | Client_ChecksumRequestHandler | function-map.md, decompiled-functions.md |
| 0x006b3ec0 | TGNetwork_HostOrJoin | function-map.md, decompiled-functions.md |
| 0x006b4560 | TGNetwork::Update | function-map.md, decompiled-functions.md |
| 0x006b4c10 | TGNetwork::Send | function-map.md, decompiled-functions.md |
| 0x006b55b0 | SendOutgoingPackets | function-map.md, decompiled-functions.md |
| 0x006b5c90 | ProcessIncomingPackets | function-map.md, decompiled-functions.md |
| 0x006b9b20 | CreateUDPSocket | function-map.md, decompiled-functions.md |
| 0x006da2c0 | EventManager::ProcessEvents | function-map.md, decompiled-functions.md |
| 0x006db380 | RegisterEventHandler | function-map.md, decompiled-functions.md |
| 0x007e3670 | NiNode RTTI registration | rtti-class-catalog.md, nirtti-factory-catalog.md |
| 0x007e5450 | NiNode factory | rtti-class-catalog.md, nirtti-factory-catalog.md, netimmerse-vtables.md |
| 0x0071f270 | ComputeChecksum | function-map.md, decompiled-functions.md |
| 0x007202e0 | HashString | function-map.md, decompiled-functions.md |
| 0x00859a0b | __purecall stub | netimmerse-vtables.md |
| 0x0040da50 | NiObject slot-11 no-op (never overridden) | netimmerse-vtables.md |

### 5.8 Constants and offsets

| Anchor | Value | Cited in |
|--------|-------|----------|
| NiObject RTTI data | 0x009a1468 | netimmerse-vtables.md |
| NiObject global counter | 0x009a1478 | netimmerse-vtables.md |
| TGUIObject parent offset | +0x14 | ui-class-hierarchy.md |
| TGUIObject bounds offset | +0x18 | ui-class-hierarchy.md |
| TGUIObject flags offset | +0x28 | ui-class-hierarchy.md |
| PlayWindow score offset | +0x38 | ui-class-hierarchy.md |
| MultiplayerGame readyForNewPlayers | +0x1F8 | ui-class-hierarchy.md, CLAUDE.md |
| MultiplayerGame maxPlayers | +0x1FC | ui-class-hierarchy.md |
| TGCallback flags bits | bit0/1/2/3 = isMethod/isPython/active/pendingDelete | event-system-architecture.md |
| TGHandlerListEntry size | 0xC | event-system-architecture.md |
| TGCallback size | 0x14 | event-system-architecture.md |
| TGInstanceHandlerTable location | TGEventHandlerObject+0x10 | event-system-architecture.md |

---

## Notes for the archaeology specialist's snapshot

When merging your Ghidra snapshot into this tracker, the per-doc rows should each gain
two additional fields: (1) **evidence-state** — for each load-bearing claim, whether the
Ghidra state agrees (verified / partial / disputed / not-found); (2) **renamed-since-doc** —
addresses where the doc cites `FUN_xxxxxxxx` but Ghidra now has a real name. Anchor table
§5 is the index — every entry there should appear in your snapshot so a downstream pass
can grep and confirm.

The most evidence-dense docs (function-map.md and rtti-class-catalog.md) should be
processed first to surface any binary-level drift; everything else then validates against
post-Pass-8C names.

---

## 6. Validation log

### 2026-05-28 — function-map.md (foundation #1)

- **Confirmed:** 8 claims — address range 0x004010e0-0x008879e0, Unwind@ count 4,692, Catch@ count 3, 18 of 20 category counts, all sampled boundaries non-overlapping, MpgameHandleMessage dispatcher address + opcode set + jump table base.
- **Corrected:** 11 claims — total 18,247→18,249 (in-body) + 18,576 (incl. EXTERNAL), FUN_ 13,333→13,467, thunks 133→164, Cat 9 44→45 (the +1 is MpgameHandleMessage), Cat 17 1,619→1,620, dispatcher 0x0069f2a0 promoted from "handler addr" to function entry, header "18 categories" → "20", Cross-Reference dispatcher row updated, Summary table totals updated, parenthetical sub-range math dropped from Cat 4/6/18/20.
- **Dropped:** 0.
- **Pending (confidence: low):** ~75 entries across per-category "Named/Identified Functions" lists tagged `[v5: unnamed in current import]`. These retire progressively as per-function v5 passes name them.
- **Open question:** Cat 17 +1 specific function not identified — flagged for later targeted xref hunt.
- **Status:** `partial`. Foundation claims are verified; named-function lists carry `confidence: low` per convention (a) from `docs/guides/v5-evidence-header.md`. Doc reaches `verified` once all per-category named-function lists either reflect current Ghidra names or get dropped.
- **Files touched:** `docs/engine/function-map.md`, `docs/engine/v5-validation-status.md` (this tracker). `docs/engine/README.md` row for function-map.md was checked and needs no update — it says "18K-function organized map" without committing to a specific total.

### 2026-05-28 — rtti-class-catalog.md (foundation #2)

- **Confirmed:** 84 specific anchors — 15 foundation claims (MSVC RTTI nomenclature; TGStreamException at 0x0095AD10; NiRTTI hash table at 0x009a2b98 with 37 buckets and 237 xrefs; 117 registrations; NiNode pattern at FUN_007e3670 / FUN_007e5450 / 0x00978500; NiObject at 0x009780D8; NI bare-string range 0x00975E98-0x009799F8; .data segment 0x008bb000-0x009b5357; three TG bare-string clusters); 28 TG bare-string addresses re-anchored from `_p_` substrings to canonical bare strings (TGObject, TGEvent, TGEventHandlerObject, TGSequence, TGPythonInstanceWrapper, TGAttrObject, TGTemplatedAttrObject, TGAction, TGAnimAction, TGMovieAction, TGCreditAction, TGSoundAction, TGAnimPosition, TGConditionAction, TGCondition, TGIEvent, TGKeyboardEvent, TGMouseEvent, TGGamepadEvent, TGPlayerEvent, TGShortEvent, TGVoidPtrEvent, TGMessageEvent, TGNetwork, TGUIObject, TGFrame, TGPane, TGButton, TGTextButton, TGDialogWindow); 41 newly-discovered TG bare-string addresses added; spot-checks for ShipClass / ShipSubsystem / MultiplayerGame / DamageableObject hold.
- **Corrected:** 5 systematic corrections — (X1) MSVC RTTI nomenclature reframed: 21 `_TypeDescriptor` (CRT/STL) + 1 `.PAV` throw-type for TGStreamException, with explicit "don't conflate `.?AV` and `.PAV`" call-out; (X2) address-range claim rewritten: all TG strings live in `.data` (0x008bb000-0x009b5357), `.rdata` claim removed, three TG sub-region clusters named; (X3) TG section systematically re-anchored with `[v5-validated 2026-05-28]` tags on the 28 confirmed rows; (X4) 41 newly-discovered TG classes added to appropriate subsections; (X5) SWIG count caveat added — "method count" column conflates bound methods with enum/constant identifiers; ~1,340 reframed as "SWIG-bound Python identifiers".
- **Dropped:** 34 fictional TG rows (Group A — speculative-by-analogy): TGColorA, TGMatrix3, TGRect, TGStringStream, TGTypeInfo (5 math/data); 12 of 18 UI widgets (TGCheckButton, TGRadioButton, TGScrollBar, TGTextBox, TGLabel, TGListBox, TGComboBox, TGSlider, TGSpinner, TGImage, TGProgressBar, TGTab); 15 of 17 managers (TGAudioManager, TGEventManager, TGModuleManager, TGRenderManager, TGSystemManager, TGFileManager, TGTextureManager, TGNiManager, TGPlayManager, TGScriptManager, TGMessageManager, TGTimerManager, TGGameManager, TGControlManager, TGVarManager); 2 misc (TGdb, TGSound row in misc). The "124 unique TG classes" count is dropped — actual count is ~70 SWIG-bound + ~15 internal C++ (factory-anchored).
- **Moved (Group B → Internal C++ classes section):** ~15 real C++ classes that lack bare class-name strings because they are not SWIG-bound — TGStream, TGBufferStream (with v5-validated vtable 0x008958D0), TGProfilingInfo, TGMessage + 6 message subclasses (factory IDs 0x0100-0x010D), TGWinsockNetwork + 6 networking subclasses. Anchored via factory ID or vtable rather than bare string.
- **Pending (confidence: low / deferred):** SWIG identifier-count column carries `confidence: low` pending per-class PyMethodDef walk; full enumeration of 129 NI bare strings deferred to netimmerse-vtables.md pass; full enumeration of ~420 game-specific class strings deferred to per-subsystem passes; TG manager classes in 0x00912xxxx range still cite `_p_` substring addresses pending bare-anchor re-derivation; TG internal-class factory IDs are approximate per docs/protocol/transport-layer.md and need direct binary confirmation.
- **Open questions:**
  1. NI 129 vs 117 delta — what are the 12 NI classes not registered with the factory? Abstract bases? Stream-only types? Deferred to netimmerse-vtables.md.
  2. Are TGStringStream and TGTypeInfo real internal classes (Group B) or fully speculative (dropped)? Currently in dropped list; xref check would settle it.
  3. TGProfilingInfo — vtable not yet confirmed; flagged in Internal C++ section as "pending vtable confirmation".
  4. Actual SWIG-bound TG class count (~70 vs originally-claimed 114) needs PyMethodDef walk to firm up.
- **Status:** `partial`. Foundation claims + TG section verified; NI and game-specific samples confirmed but full row-by-row enumeration deferred. Documentation debt is explicitly listed in the doc body under "deferred" / "pending" / "estimated" markers.
- **Files touched:** `docs/engine/rtti-class-catalog.md`, `docs/engine/v5-validation-status.md` (this tracker). `docs/engine/README.md` row for rtti-class-catalog.md still says "670 classes: 129 NI, 124 TG, ~420 game" — that count is now stale (new estimate ~615; 124 TG is wrong). README update batched at end of engine family per campaign convention.

### 2026-05-28 — nirtti-factory-catalog.md (foundation #3) — **first `verified` doc in the campaign**

- **Confirmed:** 25 evidence anchors — hash-table base at `0x009a2b98` (237 xrefs); final vtable `PTR_FUN_0088b7c4` and temp-construction vtable `PTR_LAB_0088b7d8`; bucket count 37 (0x25); bucket array size 0x94; table struct 0x10; hash node 0x0C; NiAlloc body at `0x00718cb0-0x00718cc6`; consumer functions `FUN_008176b0` (904-byte LoadObject) and `FUN_00818150` (635-byte LoadObjectAlt); orphan process-shutdown READ at `0x00816c40` invoking vtable[+0]; 117 total registrations (115 NI + 2 TG); 2 TG entries (TGDimmerController, TGFuzzyTriShape) at `0x008daed4` and `0x008daee8`; TGOverlayController at `0x008daef8` NOT registered; registration range `0x00455060-0x0084ca60` and factory range `0x00455320-0x00850a30`; vtable slot semantics [+0]=dtor, [+4]=hash, [+8]=compare, [+0xC]=setEntry, [+0x10]=deleteEntry; 17 abstract-base RET-stub `DAT_*` factories + 100 concrete `FUN_*` factories; factory signature `void(int* out_ptr)`; 10 of 117 entries individually sampled (TGDimmerController, TGFuzzyTriShape, NiBinaryVoxelData, NiListener, NiNode, NiBezierCylinder, NiObject, NiObjectNET, NiAVObject, NiSoundSystem); 3 vtable cross-anchors for netimmerse-vtables.md (NiNode `0x00898f2c`, NiTriShape `0x00899374`, TGDimmerController `0x0088b7ec`).
- **Corrected:** 7 — (X1) registration-pattern preamble updated "all 115 classes" → "all 117 registered classes (115 NI + 2 TG)"; (X2) summary breakdown 113 Ni + 2 TG = 115 → 115 Ni + 2 TG = 117 (the prior 113/115 was inconsistent math); (X3) xref count 234 → 237 with breakdown (234 registration READ+WRITE pairs + 2 consumer READs + 1 process-shutdown READ); (X4) standalone READ at `0x00816c40` reframed from "purpose unclear, may be cleanup" to "hash-table destructor invocation at process shutdown — calls vtable[+0]; NOT inside any Ghidra function (orphan code)"; (X5) factory signature documented as `void(int* out_ptr)`, out-parameter, not `T* func(void)` — was undocumented and affects readers writing decoders; (Structural) new "Concrete vs Abstract Factory Distribution" section names the 17 RET-stub abstract-base factories and the 100 concrete-allocator factories as a foundational distinction (anchors netimmerse-vtables.md and gamebryo-cross-reference.md); (TG footnote) TGOverlayController at `0x008daef8` is a sibling TG class but NOT NiRTTI-registered — uses a different runtime-type mechanism.
- **Dropped:** 1 column — **Guard Flag**. Of 10 sampled rows, only 2 guard-flag addresses matched (NiNode `0x009a18a0` and NiBezierCylinder `0x009b32f0`), and those 2 may be coincidence. Guard flag is secondary metadata that nothing else in the doc family depends on. Dropped entirely rather than carrying with `confidence: low` markers — cleaner for `verified` status.
- **Pending (confidence: medium):** 107 of 117 catalog rows are pattern-extrapolated, not individually decompiled. The pattern uniformity is well-evidenced (6 spot-decompiles + 8 sub-cluster checks across the 14 MB factory range) so the rows carry `confidence: medium` rather than `low`. A per-row decompile sweep would promote all 107 to high; tracked as documentation debt.
- **Open questions:**
  1. **14 unregistered NI classes** — the catalog notes 4 (NiDDImage, NiDDBufferImage, NiCloneExtraData, NiProvider_Info); the other ~10 are unenumerated. Deferred to netimmerse-vtables.md validation pass.
  2. **TGOverlayController runtime-type mechanism** — likely TG's own type-info via a GetRTTI-style accessor (`FUN_00457550` is a candidate). Concrete mechanism unverified.
  3. **Hash-table vtable slots [+0x14], [+0x18], [+0x1C]** exist but are undocumented. Low-stakes — deferred to a dedicated vtable pass.
  4. **NiAlloc address discrepancy** — `engine-snapshot-20260528.md` (archaeology specialist's owned artifact) cites NiAlloc at `0x00717840`. This validation found NiAlloc at `0x00718cb0` (body `0x00718cb0-0x00718cc6`) used by all 117 registrations. Snapshot needs an erratum; flagged to archaeology specialist as a follow-up.
  5. **107 by-extrapolation rows** — medium confidence pending a per-row decompile sweep. Documentation debt; not blocking `verified` status given pattern evidence.
- **Status:** `verified`. **First doc in the campaign to reach `verified`** (function-map.md and rtti-class-catalog.md are both `partial`). Every claim has `confidence: high` or `confidence: medium` with documented reasoning. No `confidence: low` rows.
- **Files touched:** `docs/engine/nirtti-factory-catalog.md`, `docs/engine/v5-validation-status.md` (this tracker). `docs/engine/README.md` row for nirtti-factory-catalog.md still says "117 NiRTTI factory registrations with addresses" — that count is correct; no update needed. README batch-refresh at end of engine family per campaign convention.

### 2026-05-28 — netimmerse-vtables.md (foundation #4) — **second `verified` doc in the campaign**

- **Confirmed:** 15+ evidence anchors — 7 vtable addresses (NiObject `0x00898b94`, NiObjectNET `0x00898c48`, NiAVObject `0x00898ca8`, NiNode `0x00898f2c`, NiGeometry `0x00899164`, NiTriBasedGeom `0x00899264`, NiTriShape canonical `0x00899374` — the 7th is new); constructor chain end-to-end (FUN_007d87a0 → FUN_007dac80 → FUN_007dc0c0 → {FUN_007e5450 | FUN_007edd10 → FUN_007ef260 → FUN_007f31f0}); `__purecall` stub at `0x00859a0b` (bytes verified); per-class NiRTTI ptr storage addresses (0x009a1468, 0x009a1500, 0x009a1578, 0x009a1870, 0x009a1a98, 0x009a1af8, 0x009a1bb8) each verified via GetRTTI stub `mov eax, IMM ; ret` bytes; NiObject global counter at `0x009a1478`; RTTI factory hash table at `0x009a2b98` cross-link to nirtti-factory-catalog.md (verified companion); slot 11 universal no-op at `0x0040da50` confirmed across NiObject/NiObjectNET/NiAVObject/NiNode; 12 slot samples decompiled (NiObject 0/7/11, NiObjectNET 0/4, NiAVObject 0/7, NiNode 0/39/41, NiGeometry 0/45, NiTriBasedGeom 0); two-stage construction pattern confirmed for NiTriShape.
- **Corrected:** 5 systematic corrections — (C1) **NiTriShape vtable reassignment**: the prior doc placed NiTriShape at `0x00899264`; that vtable is actually NiTriBasedGeom (intermediate ancestor). Canonical NiTriShape vtable is `0x00899374` (per GetRTTI stub cross-check: vtable 0x00899264 slot 0 returns 0x009a1af8 = NiTriBasedGeom RTTI; vtable 0x00899374 slot 0 returns 0x009a1bb8 = NiTriShape RTTI with 28 game-code xrefs). The factory FUN_007f31f0 overwrites the intermediate vtable with the canonical one. (C2) **Constructor chain** updated to insert NiTriBasedGeom between NiGeometry and NiTriShape, showing the two-stage write explicitly. (C3) **Inheritance accounting** corrected: NiTriBasedGeom adds 4 over NiGeometry (slots 64-67, matches 0x110 vtable size); NiTriShape canonical has ~48 slots and the full per-slot accounting is open question #1. (C4) **NiGeometry slot 45 (FUN_007ef050)** is the scalar deleting destructor (calls FUN_007eecd0 then conditionally NiFree if param & 1 — MSVC canonical form), not just "NiGeometry-specific". (C5) **NiAVObject 0x9C vs 0xC4** clarified: 0x9C is the vtable size (39 slots × 4); 0xC4 is the object/instance size from ctor field writes. Two tables disagree because they measure different things — clarifying paragraph added.
- **Dropped:** 0.
- **New sections added:** "Abstract Base Classes Have Vtables" clarifier, "Two-Stage Construction Pattern" methodology paragraph, "NiTriShape Canonical Vtable (0x00899374)" skeleton with anomaly call-out at offsets +0x9C/+0xA0, "Open Questions and Documentation Debt" section enumerating the 6 follow-ups.
- **Pending (confidence: medium):** ~226 of 238 vtable slot entries are pattern-extrapolated by inheritance — consistent slot positions relative to the parent class, names inferred from decompile rationale. The top-of-doc NOTE block calls this out. A per-slot decompile sweep would promote all 226 to high; tracked as documentation debt.
- **Open questions:**
  1. **NiTriShape canonical vtable per-slot map at `0x00899374` missing entirely** — ~48 slots, anomalous non-pointer bytes at +0x9C (`0x4B189680`) and +0xA0 (`0x0DA24260`). Either inline floats in vtable space (unusual) or vtable ends at slot 38.
  2. **NiNode 43 vs 44 slot count ambiguity** — slot at offset +0xAC reads `0x007e4150` (valid pointer); needs investigation of FUN_007e4150 to determine if it's a 44th NiNode-specific virtual or padding.
  3. **NiAVObject object size 0xC4** — derived from ctor field writes (offset 0xBC), not factory allocation. Abstract base.
  4. **Suspected RTTI ptr at `0x009a14b8`** (appears in early notes) — not yet classified.
  5. **226 of 238 slot entries are pattern-extrapolated** — per-slot decompile sweep is the promotion path.
  6. **NiCamera, NiLight, and additional NI vtables in the `0x00898d44+` region** — scope question for a future doc expansion.
- **Status:** `verified`. **Second doc in the campaign to reach `verified`** (after nirtti-factory-catalog.md). Every claim has `confidence: high` or `confidence: medium` with documented reasoning (pattern extrapolation per the [[verified-status-criteria]] standard). No `confidence: low` rows.
- **Cross-doc note for next pass:** [rtti-class-catalog.md](rtti-class-catalog.md) currently lists NiTriBasedGeom (`0x009787A0`) and NiTriShape (`0x009787EC`) as separate rows but does not annotate NiTriBasedGeom's role as the `NiGeometry → NiTriShape` intermediate ancestor. When rtti-class-catalog.md is next touched (it's currently `partial` — NI section is deferred), its NiTriBasedGeom row should gain a one-line note: "intermediate ancestor between NiGeometry and NiTriShape; runtime NiTriShape uses vtable `0x00899374`, transient NiTriBasedGeom vtable `0x00899264` only exists during NiTriShape construction." Not modified this pass to keep companion-doc state stable.
- **Files touched:** `docs/engine/netimmerse-vtables.md`, `docs/engine/v5-validation-status.md` (this tracker). `docs/engine/README.md` row for netimmerse-vtables.md still says "Vtable maps for 6 core NI classes" — now technically 7 (with the new canonical NiTriShape), but the row caption is a summary and remains accurate. README batch-refresh at end of engine family per campaign convention.

### 2026-05-28 — tg-hierarchy-vtables.md (foundation #6) — **third `verified` doc in the campaign**

- **Confirmed:** 22+ evidence anchors — the 9 vtable addresses for the Ship inheritance chain (TGObject 0x00896278, TGStreamedObject 0x008962F4, TGStreamedObjectEx 0x008962A8, TGEventHandlerObject 0x00896044, TGSceneObject 0x00889708, ObjectClass 0x00889950, PhysicsObjectClass 0x00894128, DamageableObject 0x00893D88, Ship 0x00894340); 8 constructor decompiles wiring the chain end-to-end (TGObject ctor 0x006f0a70 → TGStreamedObject ctor 0x006f31a0 → TGStreamedObjectEx ctor 0x006f2590 → TGEventHandlerObject ctor 0x006d8f90 → TGSceneObject ctor 0x004308e0 → ObjectClass ctor 0x00435030 → DamageableObject ctor 0x00591200 → Ship ctor 0x005abdc0); each ctor calls its parent then writes its own vtable address as `*this = &PTR_FUN_<vtable>`; TGObject's full 12-slot vtable layout (scalar_deleting_dtor at 0x006f0b70, GetTypeID=2 at 0x006f0b60, IsTypeID at 0x00518ab0, DebugPrint at 0x006f1650, WriteToStream at 0x006f0bc0, three __purecall stubs at 0x00859a0b for slots 5-7, InvokePythonHandler at 0x006f15c0, GetClassName at 0x006f1540 returning "TGObject" string at 0x0095B05C, GetSwigTypeName at 0x006f1550 returning "_p_TGObject" string at 0x009142B0, GetObjectPtrTypeName at 0x006f1560 returning "TGObjectPtr" string at 0x0095B270); universal slot-1 GetTypeID pattern across 4 sampled classes (TGObject=0x02, TGStreamedObject=0x03, TGEventHandlerObject=0x102, TGSceneObject=0x8002 — all 6-byte `mov eax, IMM ; ret` stubs); universal slot-0 scalar_deleting_dtor MSVC byte pattern `56 8B F1 E8 ?? 00 00 00 F6 44 24 08 01 74 14 56` across 4 sampled classes; universal slot-3 DebugPrint inheritance (all 9 vtables show 0x006f1650 at offset +0x0C); universal slot-8 InvokePythonHandler inheritance (all 9 vtables show 0x006f15c0 at offset +0x20); Ship vtable boundary at 0x008944AC = 92 slots × 4 bytes = 0x16C (next 24 bytes are 6 float constants: 75.0, 50.0, 500.0, 900.0, 0.8, 0.0049 — Ship-class data adjacent to vtable); Ship slot 72 = WriteStateUpdate at 0x005b17f0 (StateUpdate pipeline confirmed); Ship slot 85 = CollisionDamageWrapper at 0x005b0060 (delegates to FUN_005afd70 + FUN_00593650 DamageableObject ApplyCollisionDamage); TGStreamedObject slot 12 (0x006f2750) = chained stream-write dispatch; TGStreamedObject slot 14 (0x006f3400) = AddEventHandler allocates 0x14-byte handler entry; TGEventHandlerObject slot 20 (0x006d9240) = HandleEvent dispatcher.
- **Corrected:** 2 doc-text issues — (C1) Slots 5/6/7 of TGObject described as "(NULL stub 0x00859a0b)" → actually MSVC `__purecall` stub (`6A 19 E8 69 13 00 00 59 C3` = `push 0x19 ; call __purecall_thunk ; pop ecx ; ret`). Same stub identified in netimmerse-vtables.md validation; doc text should align to "__purecall stub (pure-virtual placeholder)". (C2) NOTE block speculating that 0x008963BC is "TGHashTable or similar" — actually 0x008963BC has ZERO xrefs (verified via `get_xrefs_to`). It is not a runtime class vtable; it is orphan `.rdata` data that previous interpretation mis-identified. The negative claim ("NOT TGObject's vtable") remains correct; tighten the positive guess.
- **Dropped:** 0.
- **New sections to add when documentation-writer renders:** (a) NOTE block at top with v5-validated tag stating this doc has been re-anchored 2026-05-28; (b) Class Type-ID Constants table (slot-1 GetTypeID returns) showing the 4 sampled values + invitation to extend; (c) Cross-link to TGBufferStream (0x008958D0, sibling, see precision dig) and TGDimmerController (0x0088b7ec, sibling, NiRTTI-registered); (d) Inline `[v5-validated 2026-05-28]` tags on the 9 vtable address rows and the sampled slot rows.
- **Pending (confidence: medium):** ~100 of ~140 slot rows are pattern-extrapolated by inheritance (consistent positions, inferred names from doc-author rationale, decompile verification pending). Per-slot decompile sweep would promote all 100 to high; tracked as documentation debt.
- **Open questions:**
  1. **Slot-1 GetTypeID class-ID numbering scheme.** Constants 0x02 / 0x03 / 0x0102 / 0x8002 suggest structured tagging (low byte = sub-class, high byte = domain). Likely an enumeration. Cross-link to TGBufferStream's 0x32 tag and the dispatcher's wire-format tags worth catalog.
  2. **0x008963BC actual purpose.** Zero xrefs but plausible vtable-shaped bytes suggest unused linker artifact or partial-overlap with TGStreamedObjectEx's adjacent data. Not blocking; flagged for future curiosity.
  3. **TGEventHandlerObject slots 23-39, TGSceneObject slots 27-47, Ship slots 9-11/16-18/36-47** marked "unknown" or "stub" in doc. Per-slot decompile sweep is the promotion path.
  4. **Ship slot 22 (+0x58) = 0x00430d30 "AttachDefaultProperty"** — doc text needs decompile verification that it calls NiAVObject::AttachProperty(this+0x18, 0) as claimed. Pattern-plausible.
  5. **Slot 4 WriteToStream output format** — confirmed it formats "ID:%d Saving:%s [%d] number=%d" via vtable+4 and vtable+0x24, but the stream sink vtable methods (+0x64, +0x84) are unnamed in doc. Likely related to TGBufferStream Serialize but worth a direct link.
- **Status:** `verified`. **Third doc in the campaign to reach `verified`** (after nirtti-factory-catalog.md and netimmerse-vtables.md). Every confirmed claim has `confidence: high` (direct address citation) or `confidence: medium` (pattern extrapolation with documented reasoning). No `confidence: low` rows.
- **Cross-doc note for next pass:** [event-system-architecture.md](event-system-architecture.md) (foundation #8) will rely on TGEventHandlerObject's vtable slots 16-22 (HandleEvent at 0x006d9240 confirmed here). When that doc is validated next, its TGEventManager-dispatch claims can cite the TGEventHandlerObject vtable as a verified anchor. Also note that [docs/engine/README.md](README.md) currently has NO row for tg-hierarchy-vtables.md (it is orphan from the index) — adding a row is part of the eventual README batch-refresh.
- **Files touched:** `docs/engine/v5-validation-status.md` (this tracker). The `docs/engine/tg-hierarchy-vtables.md` body update will be performed by documentation-writer using the evidence packet handed off by archaeology specialist.

### 2026-05-28 — function-mapping-report.md (foundation #6 in revised order — original row #2)

- **Confirmed:** 5 evidence rows — (1) 8 annotation scripts exist in `tools/` with accurate INTENT descriptions per script source code; (2) zero annotation scripts have been applied to current Ghidra import (5 Pass 7/8 narrative rename claims spot-checked, all absent: TGObject__LoadFromStream, Game__GetPlayerShip, TGEventHandlerTable, TGWinsockNetwork__RemovePeerAddress, Ship__AITickScheduler; `search_functions("swig_")` = 0 matches); (3) current custom-named function count is 4,797 = 25.8% of 18,581 (all auto-analysis artifacts: 3 Catch@ + ~4,692 Unwind@ + library imports + CRT/STL templates); (4) only project-applied rename present is `MpgameHandleMessage` at `0x0069f2a0` (completeness 69.94, applied during foundation #1); (5) NI 3.1 vs Gb 1.2 vtable slot deltas cross-confirmed by [netimmerse-vtables.md](netimmerse-vtables.md) v5 validation — NiAVObject 39 vs 27 (+12), NiNode 43 vs 31 (+12), NiGeometry 64 vs 27 (+37).
- **Corrected:** 0 — corrections in this doc class take the form of section removal rather than text rewrite (foundation/mid docs validate by re-anchoring addresses; process-meta docs like this one validate by content removal).
- **Dropped:** 2 major sections — (D1) "Ghidra MCP Naming Sessions (2026-02-23 through 2026-02-24)" — full Pass 1-8 narrative with rename counts (Pass 1 = 156, Pass 2 = 77, Pass 2b = 90, Pass 3 = 53, Pass 4 = 42, Pass 5 = 35, Pass 6 = 75, Pass 7 = ~1,387, Pass 8A = 38, Pass 8C = 61). Pass narratives describe a prior Ghidra DB that was discarded on 2026-05-28 re-import. (D2) "Coverage Summary" claiming ~15,209 named / 83% — replaced with v5-truthful "Current Coverage State" using 4,797 / 25.8%. Also dropped: "Unmappable Functions" section, "Phase 5 (COM Interfaces) — 0 Yield" section — both were Pass-era status callouts.
- **Restructure decision:** Option A (preserve doc, restructure heavily) was chosen over Option B (full archive) and Option C (preserve Pass narratives as historical). Option C conflicts with the user-stated direction to move away from script-driven naming; Option B discards salvageable reference material (script descriptions, NI/Gb vtable delta table). Option A keeps what's useful while telling v5 truth — see [[function-mapping-report-validation-20260528]] for the agent's full rationale.
- **Pending (confidence: low):** 0 — no `confidence: low` rows. The pre-v5 stale claims were removed outright rather than retained at low confidence, per the catalog row disposition convention.
- **Open questions:**
  1. **18,581 vs 18,576 inconsistency.** Evidence packet specifies total incl. EXTERNAL = 18,581; [function-map.md](function-map.md) (validated same day, foundation #1) says 18,576. Used 18,581 from the packet but flagged for reconciliation. Likely minor analysis drift between packet preparation and tracker capture. Resolution path: re-run `get_function_count(STBC.exe)` on a stable Ghidra session to settle the 5-function delta.
  2. **CLAUDE.md stale claims.** Root CLAUDE.md still says "2,348 functions, 393 classes" for `ghidra_annotate_globals.py` outputs and "~15,134 functions named/excluded (83%)" in the Documentation Index row. Both are stale under v5. Batched to engine-family-close CLAUDE.md refresh.
  3. **README.md doc-index entry for function-mapping-report.md.** Updated this pass: was "~15,209 functions named/excluded (83%), annotation script docs"; now "Annotation script reference (currently unapplied); current naming = 25.8%". (Note: row #18 in the table; the old row text matched the stale 83% figure.)
- **Status:** `partial`. Foundation script-reference + NI/Gb delta verified; coverage figures replaced with current-state truth. No `confidence: low` rows. Doc class is `partial` (not `verified`) because the doc retains script-suite descriptions that are reference material for code not currently applied — a structural ambiguity the campaign hasn't resolved into a clean `verified` shape yet. Promotion to `verified` would require either (a) confirming the campaign permanently abandons the scripts (at which point "What Each Script Discovers" sections could be archived elsewhere), or (b) re-applying the scripts under v5 review (re-introducing the named-function claims with addresses).
- **Why this is foundation #6 in revised order:** Originally listed as row #2 in §2's foundation→leaves order, but documentation-writer's swap recommendation moved it later because its claims (coverage %, script outputs) depend on the validated state of foundation #1 ([function-map.md](function-map.md)) and the vtable-delta section depends on foundation #4 ([netimmerse-vtables.md](netimmerse-vtables.md)). Validating it 6th means both dependencies are already `verified`/`partial` rather than `pending`. Original row numbering retained in §2 for backward reference.
- **Files touched:** `docs/engine/function-mapping-report.md` (substantial restructure — see "Dropped" above), `docs/engine/README.md` (row #18 updated), `docs/engine/v5-validation-status.md` (this tracker — §2 row #2 status updated, this log entry added). CLAUDE.md root section claims about the annotation scripts are stale but **batched to engine-family-close** per campaign convention; not modified this pass.

### 2026-05-28 — gamebryo-cross-reference.md (mid #7) — **first cross-source doc validated**

- **Confirmed:** 21 evidence anchors — 7 stbc.exe-anchored size measurements (NiObject 0x08, NiObjectNET 0x14, NiAVObject 0xC8, NiNode 0xE8, NiGeometry 0xE0, NiTriBasedGeom 0xE4, NiTriShape 0xE4), each citing factory ctor or NiAlloc allocation; 7 nif.xml version-conditional field claims verified by direct file:line citation (line 3364 ExtraData Ref single, 3487 Velocity Vector3 until=4.2.2.0, 3492 Has Bounding Volume bool, 3493 Bounding Volume conditional, 3494 Collision Object since=10.0.1.0, 3608 Target ptr since=3.3.0.13, 3609 Unknown Integer until=3.1); 4 Gb 1.2 source-path claims confirmed via Glob/grep (NiObjectNET.h ExtraData array at line 143-144, NiAVObject.h CollisionObject at line 248, NiAVObject.h no Velocity grep-confirmed, NiKeyframeManager.h exists as deprecated at line 27); 5 of 5 matched-class spot-checks (NiObject, NiNode, NiBSPNode, NiAlphaProperty, NiTriShape all present in Gb 1.2); 5 of 5 NI 3.1-only absence spot-checks (NiBezierMesh, NiBezierTriangle4, NiBone, NiCollisionSwitch, NiSkinController all absent from Gb 1.2); 4 nif.xml line-citation spot-checks for NI 3.1-only struct definitions (NiKeyframeData:4327, NiBezierTriangle4:5319, NiBezierMesh:5333, NiBone:4392).
- **Corrected:** 8 systematic corrections — (C1) MWSE-equivalence footnote rewritten: NI 3.1 and MWSE 4.0 match only for NiObject and NiObjectNET; NiAVObject and below differ by +0x38 due to V3.1-only fields (Velocity, Has Bounding Volume, Bounding Volume). (C2) Core Hierarchy Offset Comparison table rewritten with corrected sizes (NiAVObject 0x90→0xC8, NiNode 0xB0→0xE8) and a new Source column citing the factory FUN_ for each size. (C3) MWSE field-offset list demoted from "exact for NiAVObject" to "exact for NiObjectNET only"; deferred NiAVObject field offsets to netimmerse-vtables.md. (C4) NiKeyframeManager re-categorized from "NI 3.1-only Misc" to "Matched Classes (deprecated)" — Gb 1.2 has the header, marked deprecated. (C5/C6) Subcategory rollup arithmetic surfaced as documentation debt: rows sum to 45 against headline "42" (Old Animation says 8 in title but lists 9); "21 of 42 with nif.xml" recount gives 20 of 42 documented; running total after NiKeyframeManager move = ~44. Flagged for row-by-row audit in Open Questions. (C7) Reference Priority table reordered (Ghidra-binary moved to #1) and MWSE qualifier added ("exact for NiObject/NiObjectNET only; +0x38 shift for NiAVObject"). (C8) Practical Usage Guide #1 rewritten — "Use MWSE for offsets" advice replaced with "Use MWSE ONLY for NiObject and NiObjectNET; use netimmerse-vtables.md for NiAVObject and below".
- **Dropped:** 2 stale claims — (D1) "*NI 3.1 sizes confirmed via MWSE static_assert checks (identical to NI 4.0.0.2)*" footnote (replaced by C1). (D2) Specific incorrect sizes: NiAVObject 0x90 and NiNode 0xB0 from the Core Hierarchy table (replaced by C2 corrected values).
- **New sections added:** (a) Top-of-doc NOTE block establishing `status: partial` and the cross-source convention (`[cross-source-2026-05-28]` for external-corpus claims vs `[v5-validated 2026-05-28]` for stbc.exe-anchored claims). (b) New "Why MWSE Sizes Don't Match NI 3.1 for NiAVObject" subsection in Compatibility Notes explaining the +0x38 V3.1-only-fields delta with sum math. (c) New "Open Questions and Documentation Debt" section at end of doc enumerating the 5 deferred items.
- **Cross-source convention introduced:** This is the first doc to use `[cross-source-2026-05-28]` tags for claims about external corpora (Gb 1.2 source, MWSE headers, nif.xml). Claims about stbc.exe still use `[v5-validated 2026-05-28]`. The two-tag system lets readers see provenance at a glance. Convention documented in the top NOTE block; should be adopted by future cross-source docs (e.g., docs that reference SWIG, embedded Python, gameSpy SDK).
- **Pending (confidence: medium):** ~110 row-level claims — ~80 of 87 "matched in Gb 1.2" rows + ~30 of 42 "NI 3.1-only" rows pattern-extrapolated from 5 of 5 successful spot-checks each. Same medium-confidence pattern-extrapolation precedent as netimmerse-vtables.md (226 of 238 slot rows) and nirtti-factory-catalog.md (107 of 117 catalog rows). Per-row Glob/grep sweep would promote to high; tracked as documentation debt.
- **Open questions:**
  1. **Subcategory rollup audit.** "42 NI 3.1-only" sums to 45 against the table rows; after NiKeyframeManager move = ~44. Full row-by-row audit deferred to surface any further mis-categorizations.
  2. **"21 of 42 with nif.xml" recount.** Current recount gives 20 of 42 documented rows. Discrepancy small but indicates pre-v5 drift; full row-by-row audit deferred.
  3. **NI 129 vs 117 delta.** rtti-class-catalog.md says 129 NI classes; nirtti-factory-catalog.md says 115 Ni + 2 TG = 117 registrations. What are the 12-14 unregistered NI classes? Cross-references the same open question in nirtti-factory-catalog.md §6 entry.
  4. **NiBound / BoundingVolume struct size in NI 3.1.** Observable from NiAVObject ctor's writes to indexes [0x15]-[0x18] via helper FUN_008136c0. Settling the inline-sphere vs box-variant question would fully account for the +0x38 NI 3.1 vs MWSE 4.0 delta.
  5. **Remaining mis-categorizations.** NiKeyframeManager was the obvious one (Gb 1.2 has it deprecated). A full Glob-sweep across all ~44 NI 3.1-only rows would catch any others.
- **Cross-doc reconciliation flagged:** [netimmerse-vtables.md](netimmerse-vtables.md) (verified 2026-05-28) currently lists NiAVObject object size as 0xC4 (confidence: medium, derived from ctor field writes at offset 0xBC). This validation found NiAVObject = 0xC8 (more rigorous: derived from NiNode 0xE8 - NiNode-specific 0x20). The 4-byte delta is the helper FUN_008136c0 call at end of NiAVObject ctor that completes the layout beyond what the ctor's own field writes touch. Both docs agree on the +0x38 delta vs MWSE; they disagree on whether the NI 3.1 NiAVObject size is 0xC4 or 0xC8. Flagged for engine-family-close batch reconciliation. **netimmerse-vtables.md NOT modified this pass** to keep companion-doc state stable.
- **Status:** `partial`. Stbc.exe-anchored size claims are `confidence: high`; nif.xml + Gb 1.2 file:line citations are `confidence: high`; ~110 row-level claims carry `confidence: medium` by pattern extrapolation (5-of-5 spot-check basis on each side). No `confidence: low` rows. Doc is `partial` rather than `verified` because the row-by-row audit of all ~88 matched + ~44 NI 3.1-only entries is deferred as documentation debt, and the 42 vs 45 subcategory mismatch is unresolved.
- **Files touched:** `docs/engine/gamebryo-cross-reference.md` (rewritten with v5 frontmatter, top NOTE block, 8 corrections C1-C8, 2 drops D1-D2, 3 new sections), `docs/engine/v5-validation-status.md` (this tracker — §2 row #7 status updated, this log entry added). CLAUDE.md row for gamebryo-cross-reference.md is "129 NI classes cross-referenced" — count is roughly correct (still ~129 NI classes total) and **batched to engine-family-close** per campaign convention; not modified this pass.

### 2026-05-28 — event-system-architecture.md (leaf #8) — **first leaf doc validated**

- **Confirmed:** 17 evidence anchors — 5 vtable addresses (TGEvent `0x00896018`, TGEventHandlerObject `0x00896044`, TGCallback `0x008960f4`, TGConditionHandler `0x00896104`, TGInstanceHandlerTable `0x00896030`); 5 struct sizes (TGEvent 0x28 via `new_TGEvent` SWIG `PUSH 0x28` at 0x005c5e66; TGCallback 0x14 via 5-field ctor `FUN_006e09e0`; TGConditionHandler ~0x34 via dual-substruct ctor `FUN_006e1870`; TGInstanceHandlerTable 0x14 + 0x94 bucket array via init `FUN_006d7b30`; TGEventHandlerObject's lazy +0x10 slot init NULL by ctor `FUN_006d8f90`); TGCallback 5-field layout (vtable / flags / next / sentinel / fn-or-string-ptr) directly verified by ctor body; TGConditionHandler dual embedded-sub-struct architecture (two 6-dword sub-structs at +0x00 and +0x18 — vtable written twice — plus reentrant flag at +0x30); TGInstanceHandlerTable two-level pointer indirection (TGEventHandlerObject+0x10 → struct → struct+0x0C → 0x94-byte bucket array, 37 buckets); TGEventManager singleton at global `0x00991438` (anchored via SWIG `TGEventManager_AddEvent` at 0x005c8be9: `MOV EAX, [0x00991438]`); Python dispatch path (TGEventHandlerObject vtable slot 8 at +0x20 = `FUN_006f15c0`, universal across all 9 vtables in the Ship hierarchy — cross-confirmed via tg-hierarchy-vtables.md); module resolution via `FUN_0074d280` against module registry at `0x008d8af0` ("ScriptObject"); Python-flavoured TGCallback subclass vtable at `0x008961ac` (ctor `FUN_006ec6f0`); 4 event-ID anchor clusters (0x008000E0 SetPhaserLevel xrefs 0x00573e82 / 0x0069e9c4; 0x008000E3 StartCloak heavy cluster in 0x008631xx; 0x00800058 TARGET_WAS_CHANGED xrefs 0x004fe62b / 0x00537d3e; 0x00030001 / 0x00040001 input UI region xrefs); anchored SWIG API names for TGEventManager / TGEventHandlerObject / TGEvent / TGObjPtrEvent from the binary's string table; TGEvent's string-pointer RTTI mechanism (slot 1 `FUN_006d5d20` returns ptr to "_p_TGEvent" at `0x0091427c`, distinct from the TGObject integer-tag chain).
- **Corrected:** 3 systematic corrections — (C1) **TGEvent factory ID 0x02 claim removed.** The prior doc described TGEvent as "factory ID 0x02, size 0x28". 0x02 is **TGObject's** GetTypeID return value (per tg-hierarchy-vtables.md slot 1 `mov eax, 2 ; ret` at TGObject vtable `0x00896278`); TGEvent is not TGObject. The size 0x28 was correct but collocated with the wrong type-ID. Rewritten as: vtable `0x00896018`, size 0x28, RTTI via slot 1 string-pointer to "_p_TGEvent". (C2) **TGConditionHandler dual-array architecture documented.** The prior doc said "manages sorted arrays with binary search; reentrant" without describing the layout. Now anchored: ctor `FUN_006e1870` writes the SAME vtable at `param_1[0]` and `param_1[6]`; two 6-dword sub-structs hold the broadcast and per-object arrays; reentrant flag lives at `+0x30` (param_1[0xc]). Full offset table added to the doc body. (C3) **TGInstanceHandlerTable two-level pointer indirection.** The prior doc said "lives at TGEventHandlerObject+0x10, uses 37-bucket hash". Now anchored: +0x10 holds a POINTER (lazy, init NULL); allocation happens on demand via TGEventHandlerObject vtable slot 5 (`FUN_006d9160`); the 0x14-byte struct holds another pointer at struct+0x0C to the 0x94-byte bucket array. Not flat embedding. ASCII layout diagram added to the doc body.
- **Dropped:** ~5 unanchored method name groups — `SaveBroadcastHandlers`, `LoadBroadcastHandlers`, `FixupReferences`, `FixupComplete`, the TGConditionHandler internal method family (`AddEntry`, `InsertSorted`, `FindFirstByKey`, `RemoveByName`, `RemoveAllForObject`), and the TGEventHandlerTable internal method family (`RegisterObject`, `FindHandlerChain`, `DispatchToNextHandler`). None of these names appear in the binary's string table; they were inferred from behaviour, not extracted. Behaviours retained in the doc body as anchored descriptions ("the handler-cleanup routine called when objects are destroyed") rather than invented C++ names. Anchored SWIG API names listed in their place where applicable.
- **New sections added:** (a) Top-of-doc NOTE block establishing `status: partial` with explicit list of dropped method-name groups; (b) "Two RTTI Systems" subsection explaining the integer-tag vs string-pointer RTTI coexistence (a structural finding from this validation, structurally important because a reader assuming a single system will read TGEvent's slot 1 as garbage); (c) "Anchored vs Inferred Method Names" methodology section (~2 paragraphs, second time we've explained an evidence-anchoring nuance to readers); (d) TGEventManager singleton address section (new anchor row); (e) "Open Questions and Documentation Debt" section enumerating 6 follow-ups.
- **Pending (confidence: medium):** 1 row — Python-flavoured TGCallback subclass at `0x008961ac` (vtable identified via ctor `FUN_006ec6f0`, per-slot semantics not decompiled). 0 `confidence: low` rows.
- **Open questions:**
  1. **TGEvent's actual type tag.** Slot 1 returns a string pointer (`0x0091427c` = "_p_TGEvent"); whether the engine uses the string-pointer value itself as a comparable type-ID or derives an integer elsewhere is unverified. Likely settled by decompiling the slot-1 callers.
  2. **TGEventManager singleton initialization site.** Pointer at `0x00991438` is populated at boot; the writing instruction wasn't located by this pass. Standard boot-side singleton, likely in UtopiaApp init.
  3. **RegisterHandlerNames / RegisterHandlers vtable slot positions.** Pattern is real (50+ classes in pre-v5 Pass 9C work) but specific slot indices in TGEventHandlerObject vtable weren't pinned. They live near HandleEvent at slot 20 (`FUN_006d9240`). Per-slot validation pass would settle it.
  4. **Python-flavoured TGCallback subclass at `0x008961ac` per-slot semantics.** Likely overrides the invocation method to skip the C++/Python branch and go straight to import-and-call.
  5. **TGEvent queue method names.** Anchored to SWIG `AddEvent` entry point but queue-internal API (enqueue/dequeue/peek) has no string anchor.
  6. **Per-array sort key.** TGConditionHandler dual sub-structs are sorted; specific sort key (priority? handler ID? object pointer?) requires decompiling the insertion routine.
- **Cross-doc reconciliation:** This validation reinforces [tg-hierarchy-vtables.md](tg-hierarchy-vtables.md) findings — slot 8 InvokePythonHandler universal at `0x006f15c0`, slot 1 GetTypeID returning 0x0102 for TGEventHandlerObject. No corrections needed in companion docs. The ~5 dropped method names were local to this doc; not in tg-hierarchy or other companions. **No companion docs modified this pass.**
- **Status:** `partial`. Doc class is `partial` (not `verified`) because claims were dropped (not just demoted) rather than the same claims at lower confidence. The TGEvent factory-ID error was load-bearing — correcting it changed the doc's foundation. No `confidence: low` rows, but the doc carries one `confidence: medium` row (Python-flavoured TGCallback subclass) and the 6 open questions above are explicit documentation debt. Promotion to `verified` requires per-slot decompiles of the Python-flavoured TGCallback vtable and resolution of the TGEvent type-tag open question.
- **Files touched:** `docs/engine/event-system-architecture.md` (rewritten with v5 frontmatter, top NOTE block, 3 corrections C1-C3, ~5 method-name groups dropped, 5 new sections, ASCII layout diagrams for InstanceHandlerTable indirection and TGConditionHandler offset table), `docs/engine/v5-validation-status.md` (this tracker — §2 row #8 status updated, this log entry added). [docs/engine/README.md](README.md) row for event-system-architecture.md is "TGEventManager dispatch, handler tables, TGCallback/TGConditionHandler internals" — caption remains accurate; **batched to engine-family-close** per campaign convention; not modified this pass. CLAUDE.md doc-index row likewise batched.

### 2026-05-28 — ui-class-hierarchy.md (leaf #9) — second leaf doc validated

- **Confirmed:** 16 evidence anchors — TopWindow ctor `FUN_0050c430` writes `DAT_009878cc = param_1` at `0x0050c485`; TopWindow's 5 children allocated inline with sizes 0x6c/0x50/0xb8/0x5c/0x64 and types 4/2/8/9/10; `TopWindow::FindMainWindow` at `0x0050e1b0` uses RTTI `IsA(0x810F)` + `+0x4C` match; MainWindow base ctor `FUN_0050e920(this, typeID, w, h)` writes typeID at `+0x4C`; 12 MainWindow subclass ctors enumerated via xref sweep on `FUN_0050e920`; PlayWindow ctor `FUN_00405c10` writes `DAT_0097e238 = param_1` at `0x00405c8d` and does NOT call `FUN_0050e920` (PlayWindow has no MainWindow type-ID); MultiplayerGame ctor `FUN_0069e590` extends PlayWindow with vtable `0x0088b480`, allocated as 0x200 bytes by GameInit `FUN_00504f10`, playerSlots[16] at +0x74 (anchored by `FUN_00859d64(this+0x1d, 0x18, 0x10, ...)`), readyForNewPlayers byte at +0x1F8 (anchored by `MOV byte ptr [EBP+0x1f8], 0x0` at 0x0069eaf1), maxPlayers dword at +0x1FC; TGUIObject ctor `FUN_0072dcc0` (parent `FUN_0072fc20`) sets +0x14 parent=NULL, +0x28 flags=0x08 (visible), +0x2C callbacks=NULL, then zeroes +0x18/+0x1C bounds; flag bit 0x10000000 (layout-in-progress guard) anchored at `FUN_00732120`; MainWindow RTTI type 0x810F anchored via FindMainWindow IsA call; handler-registration site `FUN_0050ca50` calls `FUN_006d92b0(table, eventID, "ClassName::HandlerName")` for 18 event IDs (TopWindow Mouse/Keyboard, OptionsWindow Quit/NewGame/LoadGame/SaveGame/NewMultiplayerGame, TopWindow ResolutionChange family 0x8000b7-0x8000ba (4 events, not 3), SelfDestruct 0x8001dd, ToggleConsole/ToggleOptions/TabFocus/PrintScreen/ToggleBridgeAndTactical 0x800494-0x800498, ToggleEdit 0x8003cc); TGL strings Multiplayer.tgl at 0x008e1900 and Options.TGL at 0x008e1390.
- **Corrected:** 5 systematic corrections — (C1) **TopWindow vs PlayWindow conflation** [LOAD-BEARING]: prior doc and CLAUDE.md say "TopWindow at 0x0097e238". Wrong on both counts. TopWindow lives at `0x009878cc`; `0x0097e238` is PlayWindow (the Game state object). Two distinct globals. New "TopWindow vs PlayWindow Globals" subsection added near the top of the doc to make the disambiguation impossible to miss. (C2) **TopWindow child catalog**: prior doc says children are MainWindow types {0 BridgeWindow, 2 ConsoleWindow, 5 PlayWindow, 8 MultiplayerWindow, 10 CinematicWindow}. Actual types are {4 unnamed, 2 ConsoleWindow, 8 MultiplayerWindow, 9 PlayViewWindow, 10 CinematicWindow}. BridgeWindow exists as a MainWindow (type 0) but isn't a TopWindow child; PlayWindow isn't a MainWindow at all. (C3) **MainWindow Type IDs catalog expanded 8 → 12 entries**: types 3 (vtable 0x0088aa3c, ctor FUN_00496a60), 4 (vtable 0x0088ec9c, ctor inline + FUN_00622300), and 6 (MapWindow, vtable 0x00889c4c, ctor FUN_004fe560) are NEW; type 5's ctor is `FUN_00507900` (not `FUN_00405c10` as prior doc had — that's PlayWindow); type 7 is `SortedRegionMenu` (NOT `SortedRegionMenuWindow` — SWIG string lacks the "Window" suffix). (C4) **PlayWindow vs MainWindow distinction**: prior doc said "PlayWindow | 0x00405c10 | MissionBase (TGEventHandlerObject) | The 'Game' object … Stored at g_TopWindow." Rewritten as: PlayWindow is a standalone TGEventHandlerObject-derived class (not a MainWindow); has no MainWindow type-ID; stored at `0x0097e238` (NOT g_TopWindow); MultiplayerGame extends it via vtable `0x008887e8 → 0x0088b480` override. (C5) **STWidget / STRadioGroup / TGScrollablePane class attributions**: none of these three names has a binary string anchor (exhaustive `search_strings` sweep). STWidget (claimed parent of STButton/STToggle) and STRadioGroup (claimed at type 0x80EA) DROPPED. TGScrollablePane DEMOTED to `confidence: medium` (may exist as internal C++ class with no Python binding, or may be RE inference — undecidable from string search alone).
- **Dropped:** 3 unverified class attributions — (D1) `STWidget` as a class name (replaced in inheritance tree by "internal widget chain" placeholder above STButton/STToggle). (D2) `STRadioGroup` attribution for type ID 0x80EA — the type-ID and vtable `0x00890ac4` are real, but the class is unknown (STSubPane has an `IsRadioGroup` property that may be the actual mechanism). (D3) `TGConsole/TGTextBlock` attribution for type ID 0x205 — TGConsole's actual vtable is `0x00897294` (different from the 0x00897270 vtable that returns 0x205 at slot 1). 0x205 is held by some other class in the chain (likely TGTextBlock, which has no SWIG string). Type-ID retained at `confidence: medium` pending chain-walking to identify the class.
- **New sections added:** (a) Top-of-doc NOTE block listing dropped/demoted classes and flagging the CLAUDE.md correction batch; (b) "TopWindow vs PlayWindow Globals" subsection (the disambiguation that all downstream readers need to see first); (c) "PlayWindow (Game State Object)" full subsection with ctor, vtable, layout, and MultiplayerGame extension fields; (d) "Anchored vs Inferred Method Names" methodology section (second leaf doc to carry this); (e) "Open Questions and Documentation Debt" section with 4 follow-ups.
- **Pending (confidence: medium / low):** ~12 medium-confidence rows — flag bits 0x20/0x40/0x80/0x100/0x200 (carried from prior doc, not separately re-anchored); event IDs 0x30003 Gamepad, 0x40001 Control, 0x8000F0 MissionSelected, 0x8000B6 ResolutionSelect, dialog events 0x8000CE-0x8000D1 (all carried from prior doc); TGDialogWindow button-bit→button mappings (mask concept verified via SWIG `new_TGDialogWindow` signature, specific bits carried from prior doc); PlayWindow field semantic labels (offsets confirmed via FUN_00405ad0 zero-init helper, semantic names like "score"/"rating"/"playerShip" carried from prior RE inference); type-ID 0x205 class identity (TGTextBlock plausible, unconfirmed). 0 `confidence: low` rows.
- **Open questions:**
  1. **Class identities for MainWindow type IDs 3, 4, 5.** Vtables and constructors anchored, but the class names are unknown. Type 5 uses "LCARS_640" font (HUD-style). Settling requires either a SWIG-string match against an as-yet-undiscovered name or a vtable-chain walk against the TGObject Type-ID constants table.
  2. **TGScrollablePane internal-or-invented status.** No SWIG string. Resolution requires finding (or failing to find) a class ctor that calls TGPane's base ctor and adds scroll-related fields.
  3. **TGDialogWindow button-bit → button-instance mappings.** Mask concept confirmed; specific bits carried from prior doc. Tracing `AddButtons` would settle.
  4. **PlayWindow field semantic labels.** Offsets confirmed; semantic names inherited from RE inference. Per-field xref hunting on the offsets (e.g., who writes +0x38 score) would settle.
- **Cross-doc impacts:**
  1. **CLAUDE.md Key Globals table** has a wrong entry: row `0x0097e238 TopWindow/MultiplayerGame ptr` should be `0x0097e238 PlayWindow / Game state ptr`, and a new row should be added: `0x009878cc TopWindow (root scene container)`. **QUEUED for engine-family-close CLAUDE.md refresh batch.**
  2. **struct-skeletons-20260528.md** (archaeology specialist's memory) already updated this pass (playerSlots +0x70 → +0x74). No action.
  3. **event-system-architecture.md** would benefit from a cross-link to `FUN_0050ca50` as the canonical TopWindow handler-registration site. Minor addition, deferred (not modified this pass to keep companion-doc state stable).
  4. **tg-hierarchy-vtables.md** could cross-link the TGUIObject ctor chain (`FUN_0072dcc0` → `FUN_0072fc20`). Minor addition, deferred.
- **Status:** `partial`. Doc class is `partial` (not `verified`) because the load-bearing TopWindow/PlayWindow correction reshaped the doc's foundation — downstream readers may have built on the prior wrong claim. Promotion to `verified` will come after the CLAUDE.md correction lands and the 4 open questions are settled. No `confidence: low` rows.
- **Files touched:** `docs/engine/ui-class-hierarchy.md` (rewritten with v5 frontmatter, top NOTE block, 5 corrections C1-C5, 3 drops D1-D3, new TopWindow vs PlayWindow disambiguation subsection, expanded MainWindow Type IDs table 8→12, full PlayWindow subsection, methodology section, open questions list), `docs/engine/v5-validation-status.md` (this tracker — §2 row #9 status rewritten, this log entry added). [docs/engine/README.md](README.md) row for ui-class-hierarchy.md is "UI inheritance tree, MainWindow type IDs, event constants, TGDialogWindow buttons" — caption remains accurate; **batched to engine-family-close** per campaign convention; not modified this pass. CLAUDE.md Key Globals row correction also batched.
