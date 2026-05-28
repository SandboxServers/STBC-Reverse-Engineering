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
| 2 | function-mapping-report.md | Foundation: coverage % + script outputs | function-map.md | pending |
| 3 | rtti-class-catalog.md | Foundation: 670 class name strings | function-map.md | partial (2026-05-28) — foundation + TG section verified; NI/game-specific deferred |
| 4 | nirtti-factory-catalog.md | Foundation: 117 factory registrations | rtti-class-catalog.md | verified (2026-05-28) — first doc in the campaign to reach `verified`; all rows confidence high/medium with documented reasoning |
| 5 | netimmerse-vtables.md | Mid: 6 NI core vtable layouts | nirtti-factory-catalog.md | pending |
| 6 | tg-hierarchy-vtables.md | Mid: TG/Ship vtable chain | netimmerse-vtables.md | pending |
| 7 | gamebryo-cross-reference.md | Mid: NI 3.1 vs Gb 1.2 / MWSE | netimmerse-vtables.md | pending |
| 8 | event-system-architecture.md | Leaf: TGEventManager dispatch | tg-hierarchy-vtables.md | pending |
| 9 | ui-class-hierarchy.md | Leaf: UI inheritance + event IDs | event-system-architecture.md, tg-hierarchy-vtables.md | pending |
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
