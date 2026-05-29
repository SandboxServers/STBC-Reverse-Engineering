---
name: networking-foundation-network-protocol-validation-20260528
description: Networking #1 (FIRST family, foundation/hub) — docs/networking/network-protocol.md v5 validation. Doc is a higher-level architecture summary; ~90% of claims duplicate or summarize protocol-family anchors. 7 address-existence misses (LAB_ vs FUNC) + 2 substantive corrections (Two/Three dispatchers count, EventManager vs TGEventManager singleton conflation) + STATUS section is HISTORICAL.
metadata:
  type: project
---

# Networking Doc #1: docs/networking/network-protocol.md

**Validated:** 2026-05-28 (FIRST in networking family v5 campaign)
**Doc class:** foundation/hub (architecture overview, 167 lines)
**Verdict:** PARTIAL — anchored where it counts, but several issues need surface treatment.

## Why this validation went fast

This doc was written as a higher-level summary of the same material covered in much greater depth by `docs/engine/decompiled-functions.md` (validated 2026-05-28 with 5/5 PASS) and the protocol-family checksum/transport-layer docs. **Roughly 90% of load-bearing claims here have already been byte-confirmed during protocol-family.** This validation cross-references rather than re-derives.

## Anchored claims (high confidence, already pinned by protocol family)

| Claim | Addr | Anchor source |
|---|---|---|
| MpgameHandleMessage / ReceiveMessageHandler | 0x0069F2A0 | [[wire-format-spec-validation-20260528]] |
| Jump table 41 entries at 0x0069F534 | 0x0069F534 | [[game-opcodes-validation-20260528]] |
| NetFile::ReceiveMessageHandler | 0x006a3cd0 | [[checksum-opcodes-validation-20260528]] |
| NetFile ctor FUN_006a30c0 | 0x006a30c0 | [[checksum-opcodes-validation-20260528]] |
| NetFile registered for event 0x60001 with name "NetFile::ReceiveMessageHandler" | inside FUN_006a30c0 | confirmed inline (FUN_006db380(0x60001,...)) |
| NetFile ctor allocs 0x48 bytes / stored at +0x80 of UtopiaModule | FUN_00445d90 | [[decompiled-functions-validation-20260528]] |
| MultiplayerWindow dispatcher FUN_00504c10 (opcodes 0x00, 0x01, 0x16) | 0x00504c10 | [[wire-format-spec-validation-20260528]] |
| 4 checksum requests (App.pyc, Autoexec.pyc, ships/*.pyc, mainmenu/*.pyc) | FUN_006a3820 | [[checksum-opcodes-validation-20260528]] |
| Checksum response opcodes 0x20–0x27 (no 0x24/0x26/0x28 receive) | FUN_006a3cd0 switch | [[checksum-opcodes-validation-20260528]] |
| ChecksumCompleteHandler sends Settings+GameInit | FUN_006a1b10 → 0x006a1b10 | [[decompiled-functions-validation-20260528]] (full byte-level confirmation incl. 2 WriteBool_Bit settings flags) |
| AlbyRules transport / TGWinsockNetwork / NetFile globals | 0x0097FA00/+0x78/+0x80 | [[transport-layer-validation-20260528]] |
| TGNetwork::Update three sub-functions (FUN_006b55b0/006b5c90/006b5f70) at 0x006B4560 | confirmed inline by decompile | direct re-verification this pass + matches decompiled-functions doc |
| State 2 dequeue loop posts ET_NETWORK_MESSAGE_EVENT 0x60001 | line `*(undefined4 *)((int)pvVar4 + 0x10) = 0x60001;` inside FUN_006b4560 | direct re-verification |
| Phase 1 init (FUN_00445d90) creates WSN+0x78 (0x34C bytes), NetFile +0x80 (0x48 bytes), GameSpy +0x7C (0xF4 bytes), port via FUN_006b9bb0 to WSN+0x338 | FUN_00445d90 decompile | direct re-verification |
| g_bMpgameInOpcodeDispatch at 0x0097FA8B | 36 xrefs incl. MpgameHandleMessage + FUN_006a3cd0 | direct verification (`list_globals` returns the label) |
| qr_handle_query at 0x006ac1e0 (GameSpy QR1 query) | FUN_006ac1e0 | direct re-verification (qr_t struct +0xdc/+0xe0/+0xe8 fields visible) |
| TGNetwork_HostOrJoin at 0x006b3ec0 | direct lookup | named in Ghidra DB already |

## CORRECTIONS (C-tier — material doc errors)

### C1: "Two Message Dispatchers" — actually THREE
**Doc says** (line 62): "Two Message Dispatchers" with NetFile + MultiplayerGame.
**Binary says**: THREE dispatchers exist, all confirmed by protocol-family work:
1. NetFile dispatcher FUN_006a3cd0 (opcodes 0x20-0x27)
2. MultiplayerGame dispatcher MpgameHandleMessage at 0x0069F2A0 (opcodes 0x02-0x2A)
3. **MultiplayerWindow dispatcher FUN_00504c10** (opcodes 0x00, 0x01, 0x16) — completely omitted in the "Two Dispatchers" framing

The doc DOES separately mention MultiplayerWindow handlers in the "MultiplayerWindow Event Handlers" table (line 123) and includes FUN_00504c10 there — but the "Two Dispatchers" section header is wrong. CLAUDE.md correctly calls out three, and protocol-family unanimously treats them as three.

**Severity:** Material framing error. Anyone using the doc as their on-ramp will form a wrong mental model.

### C2: EventManager vs TGEventManager singleton conflation
**Doc says** (lines 84-90): "EventManager object at 0x0097F838; Handler registry at EventManager+0x2C = 0x0097F864; ProcessEvents (FUN_006da2c0); Event posting: FUN_006da2a0(&0x0097F838, event)."
**Binary says**: There are TWO distinct event-system objects:
- **0x0097F838** = the event queue / dispatcher object (140+ xrefs; +0x2C registry at 0x0097F864 confirmed by [[decompiled-functions-validation-20260528]] byte-level `MOV ECX,0x97f864`)
- **0x00991438** = the SWIG-accessible `TGEventManager` singleton (only 2 xrefs at 0x0065b430/0x0065b460; identified by [[event-system-validation-20260528]] via SWIG `TGEventManager_AddEvent` wrapper at 0x005c8be9: `MOV EAX, [0x00991438]`)

Both are valid; they likely play different roles in the system (queue vs Python-bridge accessor). The doc's "EventManager" claim is CORRECT for the queue/dispatcher (0x0097F838), but the v5 protocol-family memo calls 0x00991438 the "TGEventManager singleton" which is the alternate name. **Doc would benefit from disambiguating** which one it's talking about — current text implies single global, when in fact there are two.

**Severity:** Material — but only matters for cross-referencing with SWIG/Python-layer code. The +0x2C registry chain via 0x0097F838 is correctly anchored.

## CLARIFICATIONS (Clar-tier)

### Clar1: "Two hash tables" terminology in NetFile description
**Doc says** (lines 80-82): "A (vtable+0x18, buckets+0x24)", "B (vtable+0x28, buckets+0x34)", "C (vtable+0x38, buckets+0x44)".
**Binary**: Offsets are correct, but "vtable+0x18" is misleading shorthand. These are object-base offsets (NetFile+0x18 is the FIRST hash-table sub-struct's vtable pointer). The protocol-family doc [[decompiled-functions-validation-20260528]] uses cleaner wording: "Table A: vtable +0x18, count +0x1C, capacity +0x20 (0x25), buckets +0x24".
**Suggestion**: Rephrase as "Hash Table A at NetFile+0x18 (vtable), +0x1C count, +0x20 capacity, +0x24 buckets" — matches reality and decompiled-functions doc.

### Clar2: "byte[1] != 0xFF (always true)"
**Doc says** (line 26): "FUN_006a4260 checks byte[1] != 0xFF (always true), calls FUN_006a4560".
**Binary**: The "(always true)" parenthetical is WRONG. FUN_006a4260 takes both paths:
- `if byte[1] != 0xFF` → FUN_006a4560 (per-file verification path)
- `else` (0xFF case) → inline path that uses TGBufferStream to read filename/dirname/recursive + checks reference hash and posts events
The 0xFF code path IS reachable (see [[checksum-opcodes-validation-20260528]] OQ1 — round-0xFF observed in production traces). The doc's "always true" claim is a misread.

### Clar3: Both dispatchers set g_bMpgameInOpcodeDispatch
**Doc says** (line 66): NetFile dispatcher "Sets DAT_0097fa8b = 1 during processing".
**Binary**: BOTH dispatchers set this flag — MpgameHandleMessage sets it at 0x0069f2be and clears at 0x0069f525; FUN_006a3cd0 sets at 0x006a3cd6 and clears at 0x006a3e75. The flag is a re-entry guard for the whole MP-opcode-dispatch cycle, not NetFile-exclusive.

## REFUTATIONS (R-tier — addresses-don't-exist-as-functions)

The doc's handler tables list addresses; several do NOT resolve to a function (they're LAB_ labels inside the registration sweep). This is technically valid (they ARE valid code entry points for handlers), but the doc presents them as if they're regular functions — they're not. They're code labels that the auto-analyzer didn't promote.

**MultiplayerGame Event Handlers table — addresses present but NOT marked as functions:**
- 0x006a0c60 (SystemChecksumPassedHandler) — actually `&LAB_006a0c60`
- 0x006a0c90 (SystemChecksumFailedHandler) — actually `&DAT_006a0c90`
- 0x006a0ca0 (DeletePlayerHandler) — actually `&LAB_006a0ca0`
- 0x006a0f90 (ObjectCreatedHandler) — actually `&LAB_006a0f90`
- 0x006a1150 (HostEventHandler) — actually `&LAB_006a1150`
- 0x006a1590 (NewPlayerInGameHandler) — actually `&LAB_006a1590`
- 0x006a1790 (StartFiringHandler) — actually `&LAB_006a1790`
- 0x006a1930 (ClientEventHandler) — actually `&LAB_006a1930`
- 0x006a2640 (KillGameHandler) — actually `&LAB_006a2640`
- 0x006a2a40 (RetryConnectHandler) — actually `&LAB_006a2a40`

**MultiplayerWindow Event Handlers — same pattern:**
- 0x00505040 (ConnectHandler) — LAB_
- 0x00505110 (DisconnectHandler) — LAB_
- 0x00505e00 (RefreshServerListHandler) — LAB_
- 0x00506a50 (SortServerListHandler) — LAB_

**Why this matters:** When a future investigator looks up "DisconnectHandler at 0x00505110" in Ghidra MCP, they get "No function found" and may think the doc is wrong. The doc's addresses ARE the correct entry points (verified by reading FUN_005046b0 which registers them all). But the workflow gap is real.

**Recommended fix**: Note in the doc that these are code labels (not Ghidra functions). Or, even better, the v5 campaign should `create_function` at each label so the addresses become first-class.

### R1.5: Handler tables INCOMPLETE
The MultiplayerGame handlers table lists 15 entries. FUN_0069efe0 actually registers **30 handlers** (verified by decompile). The doc is missing approximately HALF of the registered handlers:
- StopFiringHandler (0x006a18d0)
- StopFiringAtTargetHandler (0x006a18e0)
- SubsystemStatusHandler (0x006a1910)
- AddToRepairListHandler (0x006a1920)
- RepairListPriorityHandler (0x006a1940)
- ChangedTargetHandler (0x006a1a70)
- StartCloakingHandler (0x006a18f0)
- StopCloakingHandler (0x006a1900)
- StartWarpHandler (0x006a17a0)
- SetPhaserLevelHandler (already named in Ghidra DB)
- ObjectExplodingHandler (0x006a1240)
- ExitedWarpHandler (0x006a0a10)
- TorpedoTypeChangeHandler (0x006a17b0)
- DeleteObjectHandler (0x006a1a60)

The doc's table is a strict subset. Not wrong per se, but incomplete.

### R2: "ProcessEvents dispatches via FUN_006db620(this+0x2C, event)"
**Doc says** (line 87): direct dispatch from ProcessEvents to FUN_006db620.
**Binary**: ProcessEvents (FUN_006da2c0) dequeues from queue, calls FUN_006da300 per event, which then calls FUN_006db620 (via this+0x4 + a vtable hop). The doc skips a level. Intent correct, signature is `FUN_006db620(registry, event)` where `registry = this+0x2C` — but the call chain goes through FUN_006da300, not direct.

## HISTORICAL sections (H-tier — current STATUS reflects old game state)

### H1: "## STATUS: CLIENT DISCONNECTS AFTER SHIP SELECTION" (lines 5-9)
The status section describes the **flags=0x00 empty StateUpdate** issue. This was RESOLVED per CLAUDE.md ("StateUpdate flags=0x20: Server sends real subsystem health data") and per [[stateupdate-validation-20260528]].

### H2: "Previously Solved Issues" (lines 11-15)
Mentions black screen, checksum stall, first connection timeout. Black screen and checksum stall ARE resolved per CLAUDE.md. First connection timeout is still listed as Known-Issue in CLAUDE.md.

### H3: "IAT Hooks (Currently Installed)" (lines 160-163) and "Peer Send Queue Monitoring" (lines 165-168)
These describe the proxy DLL's instrumentation, not stbc.exe behavior. Not in scope for v5 validation against the binary. **Move to a docs/proxy/instrumentation.md file** or label as "Proxy DLL observability" section.

## OPEN QUESTIONS (OQ-tier)

### OQ1: What are the actual numeric values of 0x60002 (hosting start), 0x8000e6 (checksum result), 0x8000e9 (kill game), 0x8000f6 (boot player), 0x8000ff (retry connect)?
The doc lists these in the "Key Event Types" table. I confirmed `ET_NETWORK_MESSAGE_EVENT` string at 0x00953bc4, `ET_CHECKSUM_COMPLETE` at 0x0090fb8c, `ET_KILL_GAME` at 0x0090fb44 exist as strings. But the strings don't have data xrefs to bind them to numeric values. The protocol-family memos anchor some of these:
- 0x8000e7 (ET_SYSTEM_CHECKSUM_FAILED) — anchored at FUN_006a4a00 (`*(undefined **)(iVar2 + 0x10) = &DAT_008000e7`)
- 0x8000e8 (ET_CHECKSUM_COMPLETE) — anchored at FUN_006a4bb0 (`*(undefined **)(iVar1 + 0x10) = &DAT_008000e8`)
- 0x60001 (ET_NETWORK_MESSAGE_EVENT) — anchored at FUN_00445d90 and FUN_006b4560

For 0x60002 (hosting start), 0x8000e6 (checksum result), 0x8000e9 (kill game), 0x8000f6 (boot player), 0x8000ff (retry connect): the doc claims the names but doesn't have anchors I could verify. The names mostly look plausible (0x8000e9 KillGameHandler is registered at LAB_006a2640, so event 0x8000e9 firing → handler 0x006a2640 is coherent) but the EVENT-NUMERIC to NAME mapping is unanchored for those 5 entries.

### OQ2: Are FUN_006da2a0 and TGEventManager__PostEvent the same?
The doc says "Event posting: FUN_006da2a0(&0x0097F838, event)". Ghidra DB has TGEventManager__PostEvent at 0x006da2a0 (renamed). The decompile shows it forwards directly to FUN_006de330 (which manipulates queue at *param_1). So FUN_006da2a0 IS TGEventManager::PostEvent, and yes, &0x0097F838 is the implicit `this`. Confirmed; no longer an OQ — just was unclear from doc framing.

## Cross-doc consistency

- ✓ Matches CLAUDE.md "Key Globals" section (UtopiaModule, TGWinsockNetwork, NetFile, GameSpy addresses)
- ✓ Matches [[wire-format-spec-validation-20260528]] dispatcher anchors
- ✓ Matches [[checksum-opcodes-validation-20260528]] opcode table and 4 checksum requests
- ✓ Matches [[transport-layer-validation-20260528]] WSN/NetFile/GameSpy struct sizes
- ✓ Matches [[stateupdate-validation-20260528]] for StateUpdate references
- ✓ Matches [[decompiled-functions-validation-20260528]] for per-function anchors
- ⚠ Conflicts with [[event-system-validation-20260528]] on EventManager singleton — see C2

## Completeness scores (worker classification, all v5 standard)

| Address | Function | Effective | Max | Notes |
|---|---|---|---|---|
| 0x0069F2A0 | MpgameHandleMessage | 69.8 | 94.4 | Best-documented function in this doc (custom-named, prototyped) |
| 0x006a3cd0 | FUN_006a3cd0 (NetFile dispatcher) | 0.6 | 81.9 | Low score but tractable — switch-table function |
| 0x00504c10 | FUN_00504c10 (MP-Window dispatcher) | 9.6 | 87.1 | Tractable switch |
| 0x006B4560 | FUN_006b4560 (TGNetwork::Update) | 0.0 | 83.1 | Largest (196 lines), most magic numbers |
| 0x00445d90 | FUN_00445d90 (Phase 1 init) | 5.0 | 83.1 | Standard sub-object allocation pattern |
| 0x006a30c0 | FUN_006a30c0 (NetFile ctor) | 0.0 | 85.8 | Hash-table init loops |
| 0x006a1b10 | FUN_006a1b10 (ChecksumCompleteHandler) | 0.0 | 81.1 | Settings packet writer (TGBufferStream chain) |
| 0x006da130 | FUN_006da130 (RegisterHandlerFunc) | 15.0 | 89.0 | Thin wrapper |

All under v5 thresholds, but behaviors are tractable from pseudocode. The pre-v5 doc's claims hold up despite low completeness scores.

## Lessons for future networking docs

1. **Pre-v5 architecture summaries duplicate engine/protocol family content.** The network-protocol.md doc is ~95% rederivable from decompiled-functions.md + checksum-opcodes.md. Future validators should cross-reference rather than re-verify.

2. **"Two Dispatchers" framing is a pre-2026 artifact.** The MultiplayerWindow dispatcher was only added to the canonical picture during late protocol family work. Pre-v5 docs treat it as "UI window code" rather than a third dispatcher.

3. **Event-system architecture has TWO singleton addresses.** Pre-v5 docs conflate them. Both are valid: 0x0097F838 (queue/dispatcher, +0x2C registry) and 0x00991438 (SWIG TGEventManager bridge). Cross-doc work should disambiguate.

4. **Handler tables in pre-v5 docs are systematically incomplete.** The doc lists 15 of 30 MultiplayerGame handlers. The shortened tables are not WRONG but should be flagged as partial.

5. **Code-label addresses (LAB_) vs function-entry addresses (FUN_).** When the auto-analyzer fails to promote a label to a function, Ghidra MCP's `get_function_by_address` returns "No function found." The address is still a valid entry point, but the workflow asymmetry is confusing.

6. **STATUS sections decay.** Three sections of this doc describe a 2026-02 game state ("CLIENT DISCONNECTS AFTER SHIP SELECTION", "Previously Solved Issues") that's now stale per CLAUDE.md.

## Recommended doc updates (for documentation-writer)

1. Change "Two Message Dispatchers" → "Three Message Dispatchers" and add MultiplayerWindow row
2. Disambiguate "EventManager" 0x0097F838 vs "TGEventManager" 0x00991438 in the Event System section
3. Fix Clar1 (hash table offset terminology) and Clar2 ("always true" misread)
4. Mark MultiplayerGame Event Handlers table as PARTIAL or expand to include the 14 missing entries
5. Move "STATUS" + "Previously Solved Issues" to a HISTORICAL collapsible or remove
6. Move "IAT Hooks" + "Peer Send Queue Monitoring" to docs/proxy/instrumentation.md (if it doesn't already live elsewhere)
7. Note that handler-table addresses (LAB_xxxxxxxx) are code labels — Ghidra auto-analyzer did not promote them to functions, but they ARE valid call targets

## v5 header inputs

- **validated:** 2026-05-28
- **status:** partial (anchored but with C1/C2 corrections + R1.5 incompleteness + H1-H3 historical)
- **binary.size:** 5.9 MB / 18615 functions (matches engine-snapshot)
- **evidence rows:** 17 anchored + 5 corrections + 1 OQ
- **companions:** decompiled-functions.md (engine-family hub), wire-format-spec.md (protocol-family hub), checksum-opcodes.md, transport-layer.md, event-system-architecture.md

[[engine-snapshot-20260528]] | [[decompiled-functions-validation-20260528]] | [[checksum-opcodes-validation-20260528]] | [[event-system-validation-20260528]]
