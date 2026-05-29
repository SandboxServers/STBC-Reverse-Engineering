> [docs](../README.md) / [networking](README.md) / v5-validation-status.md

---
title: Networking Docs V5 Validation Status
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
  - docs/networking/network-protocol.md
  - docs/networking/multiplayer-flow.md
  - docs/networking/gamespy-discovery.md
  - docs/networking/gamespy-crypto-analysis.md
  - docs/networking/alby-rules-cipher-analysis.md
  - docs/networking/tgmessage-routing-cleanroom.md
  - docs/networking/netimmerse-transport-deep-dive.md
  - docs/networking/fragmented-ack-bug.md
  - docs/networking/ack-outbox-deadlock.md
  - docs/networking/disconnect-flow.md
  - docs/networking/ship-death-lifecycle.md
companions:
  - docs/protocol/v5-validation-status.md
  - docs/engine/v5-validation-status.md
  - docs/networking/README.md
  - docs/guides/v5-evidence-header.md
  - docs/guides/v5-doc-validation-workflow.md
---

# Networking Docs V5 Validation Status

Tracker for the v5 evidence-standard re-validation campaign on `docs/networking/`. This
is the **third family** in the campaign (engine completed 2026-05-28 at 10/10; protocol
completed 2026-05-28 at 22/22). It inventories what the 11 existing networking docs
claim and how much of each claim is backed by Ghidra-anchored evidence.

## 1. Campaign overview

Networking docs sit on top of two completed families (engine + protocol) and provide the
**connection lifecycle** and **transport-internals** layer. Many networking-family claims
are already independently anchored in the protocol family — particularly anything touching
TGMessage envelopes, TGNetwork singletons, opcodes, dispatchers, and the AlbyRules cipher.
This means many networking docs will validate via cross-doc anchor promotion (claim already
proven elsewhere) rather than fresh Ghidra cites.

Foundation layer covers protocol architecture, the AlbyRules cipher (anchored via protocol
foundation #3 transport-layer.md), and the GameSpy SDK integration (independent code region).
Mid-tier groups the clean-room routing spec and the high-level join flow. Leaves are
specific scenarios (fragmented-ack-bug, ack-outbox-deadlock, disconnect-flow,
ship-death-lifecycle).

Expected outputs per doc: (1) every load-bearing claim either cites a hex address /
`FUN_xxxx` confirmed by Ghidra MCP OR is promoted to `[v5-validated 2026-05-28 via <doc>]`
from a protocol-family / engine-family anchor; (2) v5 frontmatter; (3) cross-links into the
anchor docs; (4) historical sections marked where current proxy state has resolved the
investigation. CLAUDE.md's Documentation Index will be batch-updated at family close.

## 2. Validation order (foundation → leaves)

Order reflects dependency direction. Each row's anchors are consumed by all rows below it.

| # | Doc | Layer | Pre-existing depends on | Current status |
|---|-----|-------|--------------------------|----------------|
| 1 | network-protocol.md | Foundation: architecture + dispatchers + handler tables | (protocol family foundation #1, #3; mid #5; engine event system) | **partial (2026-05-28)** — 2 corrections (C1 THREE dispatchers not two — MultiplayerWindow was omitted from heading; C2 EventManager 0x0097F838 vs TGEventManager 0x00991438 are TWO separate singletons) + 3 clarifications + 2 refutations + 3 historical sections (STATUS/Previously Solved/IAT Hooks) + 2 OQs. 17 protocol-family anchors cross-confirmed + 5 new claims verified this pass. Handler-table cross-doc corrections applied inline (FUN_006a0a20/FUN_006a07d0/FUN_006a0ca0 per leaves #17/#18). See §6.1 |
| 2 | alby-rules-cipher-analysis.md | Foundation: cipher RE | (protocol foundation #3 transport-layer.md cipher anchors) | **verified (2026-05-28)** — first networking-family doc to clear `verified`; ZERO algorithm/wire corrections; 2 terminology clarifications (Clar1 `0x15A` is a second LCG multiplier not addend; Clar2 Encrypt feeds back CIPHERTEXT not plaintext) + 2 refinements (R1 cite vtable 0x008958c0 explicitly; R2 cipher object lives at TGWinsockNetwork+0xF0); UDP-tolerance via re-key-per-packet confirmed. See §6.2 |
| 3 | gamespy-discovery.md | Foundation: GameSpy QR1 SDK integration | (UtopiaModule+0x7C GameSpy ptr) | **partial (2026-05-28)** — algorithm + address + wire-format claims byte-confirmed; 4 corrections (C1 qr_t Layout in byte-offset notation with dual-role disclosure for qr_t+0xE4 = active flag + heartbeat port; C2 ServerList broadcast socket at byte +0x88 not +0x22; C3 +0x9C is state field not padding; C4 master hostname 0x0095a4fc is runtime-mutable not "duplicate") + 1 refinement (R1 dead code at 0x006ab558 not disassembled) + 3 OQs. See §6.3 |
| 4 | gamespy-crypto-analysis.md | Foundation: GameSpy challenge-response crypto | gamespy-discovery | **partial (2026-05-28)** — algorithm + crypto core byte-confirmed; 3 corrections (C1 wire example gamever `\1.6\` not `\1.1\` — OpenBC clean-room cascade flag; C2 ServerList timer slot +0x94 not +0x08; C3 +0x9C state field not padding) + 2 clarifications (Clar1 stale SOCKET*-arithmetic narrative; Clar2 qr_t/GameSpy struct conflation) + 3 OQs. See §6.4 |
| 5 | netimmerse-transport-deep-dive.md | Foundation: NetImmerse transport internals | network-protocol, protocol foundation #3 | **partial (2026-05-28)** — first foundation doc validated that was created WITHOUT live Ghidra (per its own disclaimer); 3 structural corrections (C1 vtable size — slots 8..15 are TGBufferStream base inheritance; C2 Section 5 fragment-window reasoning; C3 Section 9 peer-state scope) + 2 clarifications (Clar1 ACK factory OQ1 RESOLVED; Clar2 +0x2C disambiguation) + 1 historical hypothesis demoted (ACK Retransmit Count Exhaustion superseded by leaf #9); pattern note added: wire claims reliable, structural reasoning less so. This doc had peer seq offsets CORRECT (+0x24/+0x26/+0x28/+0x2A) where protocol foundation #3 had them wrong. See §6.5 |
| 6 | tgmessage-routing-cleanroom.md | Mid: clean-room routing spec | (protocol mid #7 tgmessage-routing.md, including the 3-routing-mechanisms correction) | **partial (2026-05-28)** — **HIGH PRIORITY for OpenBC implementers**; 1 material correction with OpenBC impact (C1 "Automatic Relay (C++ Layer)" is FACTUALLY WRONG — relay is per-handler not transport-level; following the old model produces duplicate event delivery for 0x06/0x0D/0x13 = the documented OpenBC parity bug) + 4 clarifications (Clar1 three-dispatchers-on-one-event; Clar2 NoMe/Forward created by MultiplayerGame_Ctor C++ not Python; Clar3 targetID==-1 third mode; Clar4 third routing mechanism = connect-event broadcast). 22 promotion tags. See §6.6 |
| 7 | multiplayer-flow.md | Mid: client/server join flow | network-protocol, protocol mid #5 checksum-opcodes.md | **partial (2026-05-28)** — zero wire-format errors; 3 corrections (C1 player slot table at MpgameBase+0x78 not +0x74 — note `docs/engine/ui-class-hierarchy.md` ALSO has this off-by-4 inheritance; C2 0x0097e238 is PlayWindow not TopWindow; C3 client checksum handler does NOT silently drop — sends placeholder via unreliable FUN_006b89a0) + 4 clarifications + 2 historical sections + 2 OQs. See §6.7 |
| 8 | fragmented-ack-bug.md | Leaf: fragmented reliable message ACK bug | netimmerse-transport-deep-dive, protocol foundation #3 | **partial (2026-05-28)** — bipartite verdict; wire format + Ghidra-Verified Analysis byte-confirmed (verified-quality reference); 1 HIGH-PRIORITY correction (C1 "Root Cause: Missing Cleanup" is binary-wrong — Pass-2 cleanup DOES exist; surgical deferral to ack-outbox-deadlock.md applied) + 2 medium/low corrections + 3 clarifications + 5 historical-preservation actions (hypothesis chain preserved). See §6.8 |
| 9 | ack-outbox-deadlock.md | Leaf: ACK-outbox deadlock | netimmerse-transport-deep-dive | **verified (2026-05-28)** — second networking-family doc to clear `verified`; ZERO mechanism corrections; most byte-verifiable networking-family doc to date (deadlock model, two-pass filter ranges, cleanup threshold, buffer sizing, struct offsets, all 9 function addresses survive byte-level cross-check at cited disassembly); 4 address-precision clarifications applied; supersedes netimmerse-transport's "ACK Retransmit Count Exhaustion" hypothesis. See §6.9 |
| 10 | disconnect-flow.md | Leaf: 4 detection paths (was 3) + cleanup cascade | network-protocol, netimmerse-transport-deep-dive | **partial (2026-05-28)** — 5 material corrections (2 CRITICAL); C1 CRITICAL FUN_006b6a20 ↔ FUN_006b6a70 swap throughout Section 1.2 (case 4 = BOOT/0x006b6a70; case 5 = DISCONNECT/0x006b6a20 — graceful path also has broadcast-relay step); C2 CRITICAL peer offsets +0x2C ↔ +0x30 swap (+0x2C = lastRecvTime, +0x30 = lastSendTime); C3 missed 4th convergence path (connect-clobber at 0x006b5d97); C4 0x006a0a20 IS DisconnectHandler — SUPERSEDES wrong Ghidra plate added during leaf #18 (actual EnterSetHandler at 0x006a07d0); C5 BootPlayerHandler is MultiplayerWindow not MultiplayerGame. 4 clarifications + 2 OQs + cross-doc inline 0x14 correction (NOT for combat kills). See §6.10 |
| 11 | ship-death-lifecycle.md | Leaf: MP ship death + respawn | network-protocol, protocol mid #4 game-opcodes.md (opcodes 0x14/0x29) | **partial (2026-05-28)** — FINAL networking leaf; zero wire/sequence corrections; 2 minor cosmetic/speculation fixes (C1 "TGSubsystemEvent" name fabrication cascade from leaf #13 — renamed throughout to "TGEvent factory 0x101 ET_ADD_TO_REPAIR_LIST"; C2 SCORE_CHANGE speculation falsified — Python ObjectKilledHandler IS registered) + 1 clarification (Clar1 handler at 0x006a1240 was bare code, CREATED this pass as MultiplayerGame_ObjectExplodingHandler) + 3 OQs. Cross-doc tension: 0x14 combat-kills claim contradicted disconnect-flow.md line 389 — resolved in disconnect-flow's C5 update. See §6.11 |
| — | README.md | Index only — refreshed at end of family | all above | **partial (2026-05-28)** — family campaign closed at 11/11 |

A foundation doc must reach `status: verified` or `partial` before docs that depend on it
begin validation. Process-meta docs (this tracker) carry `status: partial` until the
campaign concludes.

## 3. Pre-anchored claims from completed families

These are already proven by the engine + protocol family campaigns and DO NOT need fresh
Ghidra cites in networking docs. Networking-family validations should reference these by
cross-link instead of re-deriving.

### From engine family (10/10 verified)

- **TGEvent class hierarchy**: NiObject (0x02) → TGObject → TGEvent (0x101) — TGEvent IS
  0x101, NOT "TGSubsystemEvent". Subclasses: TGCharEvent (0x105), TGObjPtrEvent (0x10C).
- **TGEvent base vtable** @ 0x00895FF4 (size 0x28 bytes, 17 slots)
- **TGFactory registry** at DAT_0099a578 (table) + DAT_0099a584 (count) — DISTINCT from
  NiRTTI registry
- **TGFactory_DeserializeObject** @ 0x006d6200
- **EventManager singleton** at 0x0097F838 (+0x2C registry = 0x0097F864)
- **TGEventManager::PostEvent** @ 0x006da2a0
- **MultiplayerWindow_BootPlayerHandler** @ 0x00506170 (CREATED in leaf #19; reason=4
  BOOT_REASON_INTEGRITY)

### From protocol family (22/22 validated)

Foundation tier:
- **MpgameHandleMessage** @ 0x0069F2A0 with 41-entry jump table at 0x0069F534
- **NetFile dispatcher** FUN_006a3cd0 (opcodes 0x20-0x27)
- **MultiplayerWindow dispatcher** FUN_00504c10 (opcodes 0x00, 0x01, 0x16)
- **TGMessage envelope** vtable 0x008958D0 (size 0x40)
- **TGBufferStream cursor** vtable 0x00895C58 (size 0x30)
- **Stream primitives**: WriteByte FUN_006cf730, WriteShort FUN_006cf7f0, WriteInt32
  FUN_006cf870, WriteFloat FUN_006cf8b0, CF16 encoder 0x006d3a90 / decoder 0x006d3b30
- **AlbyRules cipher** key @ 0x0095abb4 → 0x58-byte state; InitKey @ 0x006c2280; Encrypt
  @ 0x006c2490; cipher operates on `buffer+1` (byte 0 NOT encrypted); re-key per packet
- **7 transport types** at factory table DAT_009962d4 (types 0x00-0x05 and 0x32)
- **Type 0x32 framing**: 13-bit length + bit 13 fragment + bit 14 ordered + bit 15 reliable
- **TGMessage ctor** FUN_006b82a0 allocates 0x40 bytes from pool FUN_00717b70
- **TWO reliable sequence counters**: peer+0x98 (types <0x32) + peer+0xA8 (types >=0x32)

Mid tier:
- **All opcode handlers** 0x00-0x2A anchored (game-opcodes.md, mid #4)
- **4 checksum rounds** (not 5 — mid #5 correction)
- **0x22/0x23 dialog swap** corrected (mid #5)
- **MAX_MESSAGE_TYPES** Python-side opcodes 0x2C+ (mid #6)
- **3 routing mechanisms** (not 2): C++ MultiplayerGame dispatcher, Python SendTGMessage,
  TGMessageFactory deserialize (mid #7 — TGMessage routing)
- **"NoMe" group** = "all except me" routing target, created by C++ MultiplayerGame_Ctor
  (mid #7 — not Python)
- **GenericEventForward** FUN_0069FDA0 handles opcodes 0x07-0x12, 0x1B
- **StateUpdate flags** byte-by-byte (mid #8)
- **SUB/WPN flag direction exclusivity**: SUB (0x20) S→C only, WPN (0x80) C→S only

Leaves:
- **Settings packet** (opcode 0x00) uses WriteBit not WriteByte (leaf #15/#14 area)
- **CollisionEffect** (opcode 0x15) is C→S only; no server-side recomputation
- **CompressedVec4_Byte** in collision contacts
- **DeletePlayerUI** (opcode 0x17) handler at FUN_006A1360; uses TGFactory class 0x866
  (TGFactory registry, not NiRTTI)
- **Object recovery triad** (0x1D ObjNotFound, 0x1E RequestObj, 0x1F EnterSet)
- **CV4 5-byte form** when mag_as_cf16=1 (used by explosion path); 7-byte form when =0

## 4. Cross-doc disagreements resolved during the campaign

- **0x006a0a20**: was claimed by `network-protocol.md` as `DisconnectHandler`; leaf #18
  (objnotfound-requestobj-enterset) renamed it to `MultiplayerGame__EnterSetEventHandler`
  (3-byte stub). Leaf #10 (disconnect-flow) cross-evidence via FUN_0069efe0 binding table
  + registration string at 0x0095a1f0 proved this address IS
  `MultiplayerGame__DisconnectHandler` (the 3-byte stub for event 0x60003 ET_NETWORK_DISCONNECT,
  empty in MP because real cleanup runs via transport layer FUN_006b75b0 + WSN vtable[0x74]).
  **CLOSED 2026-05-28**: Ghidra plate corrected (renamed to `MultiplayerGame__DisconnectHandler`);
  leaf #18 doc patched separately.
- **0x006a07d0**: was claimed by `network-protocol.md` as `EnterSetHandler`; leaf #18
  renamed it to `MultiplayerGame__RequestObjEventHandler` (sender for 0x1D/0x1F). Leaf #10
  cross-evidence via FUN_0069efe0 binding table + registration string at 0x0095a0a8 proved
  the canonical SWIG-registration name IS `MultiplayerGame__EnterSetHandler`. The function
  body sends BOTH opcode 0x1D (ObjNotFound, gated on ship NOT in warp) and 0x1F (EnterSet,
  gated on ship IN warp AND destination != "warp") — leaf #18's behavioral description
  remains correct; only the name was wrong. **CLOSED 2026-05-28**: Ghidra plate corrected
  to `MultiplayerGame__EnterSetHandler` with dual-purpose note in plate.
- **0x006a0ca0**: was claimed by `network-protocol.md` as `DeletePlayerHandler`; leaf #17
  (delete-player-ui) confirmed FUN_006a0ca0 sends opcode 0x18 (DeletePlayerAnim), NOT 0x17.
  Confirmed cascade-propagated through network-protocol render this family. **CLOSED 2026-05-28**.
- **disconnect-flow.md line 389 "0x14 DestroyObject combat kills"**: contradicted by
  ship-death-lifecycle.md's 33.5-min battle trace showing 0/59 combat deaths use 0x14.
  The 0x14 IS used for disconnect-triggered cleanup but NOT for combat death. **CLOSED
  2026-05-28**: corrected inline in disconnect-flow render.
- **fragmented-ack-bug.md "Root Cause: Missing Cleanup"**: contradicted by validated leaf
  #9 (ack-outbox-deadlock). Pass-2 cleanup DOES exist; the real bug is the pass-2 gate.
  **CLOSED 2026-05-28**: surgical deferral applied; hypothesis chain preserved as
  historical archaeology.
- **netimmerse-transport "ACK Retransmit Count Exhaustion" hypothesis**: binary-correct
  but behaviorally-insufficient. **CLOSED 2026-05-28**: demoted to historical sidebar;
  leaf #9 ack-outbox-deadlock holds canonical authority.
- **TGMessage vtable size** (netimmerse-transport claimed 32 bytes / 8 slots): actual
  slots 0..7 are TGMessage-specific overrides; slots 8..15 inherit from TGBufferStream
  base. **CLOSED 2026-05-28**: structural correction applied.
- **peer seq counter offsets** (protocol foundation #3 had +0x98/+0xA8): netimmerse-transport
  had correct values +0x24/+0x26/+0x28/+0x2A. Protocol foundation #3 was already corrected
  in protocol campaign. **CLOSED 2026-05-28** (during protocol pass).
- **"TGSubsystemEvent" name** (ship-death-lifecycle + leaf #13 area): name is fabricated,
  factory 0x101 IS TGEvent itself. **CLOSED 2026-05-28**: renamed to "TGEvent (factory 0x101)
  ET_ADD_TO_REPAIR_LIST".

## 4b. Cross-family / OpenBC-impact debt surfaced

- **OpenBC clean-room cascade** required for these networking-family corrections:
  - gamespy-crypto C1: gamever literal `\1.6\` (not `\1.1\`) — affects masterserver
    version filtering
  - tgmessage-routing-cleanroom C1: per-handler relay model (not transport-level
    auto-relay) — this is the documented OpenBC parity bug for 0x06/0x0D/0x13 duplicate
    delivery
- **docs/engine/ui-class-hierarchy.md** has the same `+0x74` playerSlots off-by-4 that
  multiplayer-flow inherited (corrected this pass). Engine doc should be patched separately.
- **Leaf #18 doc** (docs/protocol/objnotfound-requestobj-enterset-wire-format.md) needs
  surgical patch to remove the 0x006a0a20 EnterSetEventHandler attribution and update
  function-address table to reflect new Ghidra plates.

## 5. Methodology notes

Networking-family validations should:
1. Identify claims already proven in engine/protocol families and PROMOTE rather than
   re-derive
2. Cross-link to anchor docs heavily; this is a derived family
3. Mark "Previously Solved Issues" / status-header content as **historical** with one-line
   notes pointing to CLAUDE.md "What Works" status where appropriate
4. Surface any fresh load-bearing claims that need direct Ghidra anchoring

## 6. Per-doc validation entries

Each entry summarizes the validation outcome and points to the doc's top-of-doc NOTE block
for the full per-correction detail. Memo files in `.claude/agent-memory/game-archaeology-specialist/`
carry the full Ghidra evidence packets.

### 6.1 network-protocol.md — 2026-05-28

- **Verdict**: `partial`
- **Archaeology memo**: `networking-foundation-network-protocol-validation-20260528.md`
- **Render memo**: `networking-network-protocol-render-patterns-20260528.md`
- **Notable**: 2 corrections (THREE dispatchers not two; EventManager 0x0097F838 vs
  TGEventManager 0x00991438 are two distinct singletons) + 3 clarifications + 2 refutations
  (handler table is 15-of-30 partial; ProcessEvents chain skips intermediate FUN_006da300)
  + 3 historical sections (STATUS / Previously Solved / IAT Hooks)

### 6.2 alby-rules-cipher-analysis.md — 2026-05-28

- **Verdict**: `verified` — first networking-family doc to clear `verified`
- **Archaeology memo**: `networking-foundation-alby-cipher-validation-20260528.md`
- **Render memo**: `networking-cipher-render-patterns-20260528.md`
- **Notable**: ZERO algorithm/wire corrections; 2 terminology clarifications + 2 refinements.
  UDP-tolerance via re-key-per-packet confirmed.

### 6.3 gamespy-discovery.md — 2026-05-28

- **Verdict**: `partial`
- **Archaeology memo**: `networking-foundation-gamespy-discovery-validation-20260528.md`
- **Render memo**: `networking-gamespy-render-patterns-20260528.md`
- **Notable**: Algorithm + address + wire-format byte-confirmed; 4 corrections (qr_t
  byte-offset notation with dual-role for qr_t+0xE4; ServerList broadcast socket at byte
  +0x88; +0x9C is state field; master hostname 0x0095a4fc is mutable runtime override) +
  1 refinement (dead code at 0x006ab558 not disassembled) + 3 OQs.

### 6.4 gamespy-crypto-analysis.md — 2026-05-28

- **Verdict**: `partial`
- **Archaeology memo**: `networking-foundation-gamespy-crypto-validation-20260528.md`
- **Render memo**: `networking-gamespy-crypto-render-patterns-20260528.md`
- **Notable**: Algorithm + crypto core byte-confirmed; 3 corrections (**C1: gamever
  literal `\1.6\` not `\1.1\` — OpenBC clean-room cascade flag**; ServerList timer at
  +0x94 not +0x08; +0x9C is state field) + 2 clarifications (stale SOCKET*-arithmetic;
  qr_t/GameSpy struct conflation) + 3 OQs.

### 6.5 netimmerse-transport-deep-dive.md — 2026-05-28

- **Verdict**: `partial`
- **Archaeology memo**: `networking-foundation-netimmerse-transport-validation-20260528.md`
- **Render memo**: `networking-netimmerse-transport-render-patterns-20260528.md`
- **Notable**: First doc validated that was created WITHOUT live Ghidra (per its own
  disclaimer). 3 structural corrections + 2 clarifications + 1 historical hypothesis
  demoted (ACK Retransmit Count Exhaustion superseded by leaf #9). Pattern note added
  for future "Ghidra-not-reachable" docs: wire claims reliable, structural reasoning less
  so. **This doc had peer seq offsets CORRECT (+0x24/+0x26/+0x28/+0x2A)** where protocol
  foundation #3 had been wrong — protocol family already corrected.

### 6.6 tgmessage-routing-cleanroom.md — 2026-05-28

- **Verdict**: `partial`
- **Archaeology memo**: `networking-mid-tgmessage-cleanroom-validation-20260528.md`
- **Render memo**: `networking-tgmessage-cleanroom-render-patterns-20260528.md`
- **Notable**: **HIGH PRIORITY for OpenBC implementers**. 1 material correction
  (**C1: "Automatic Relay (C++ Layer)" is FACTUALLY WRONG — relay is per-handler not
  transport-level; following the old model produces duplicate event delivery for
  0x06/0x0D/0x13 = the documented OpenBC parity bug**) + 4 clarifications (three
  dispatchers share ET_NETWORK_MESSAGE_EVENT; NoMe/Forward created by MultiplayerGame_Ctor
  C++; targetID==-1 third mode; third routing mechanism = connect-event broadcast).

### 6.7 multiplayer-flow.md — 2026-05-28

- **Verdict**: `partial`
- **Archaeology memo**: `networking-mid-multiplayer-flow-validation-20260528.md`
- **Render memo**: `networking-multiplayer-flow-render-patterns-20260528.md`
- **Notable**: Zero wire-format errors; 3 corrections (player slot at MpgameBase+0x78
  not +0x74 — **also affects engine ui-class-hierarchy.md inheritance**; 0x0097e238 is
  PlayWindow not TopWindow; client "silent failure" premise is wrong — sends placeholder
  via unreliable FUN_006b89a0) + 4 clarifications + 2 historical sections + 2 OQs.

### 6.8 fragmented-ack-bug.md — 2026-05-28

- **Verdict**: `partial` (bipartite — first half verified-quality, second half corrected)
- **Archaeology memo**: `networking-leaf-fragmented-ack-bug-validation-20260528.md`
- **Render memo**: `networking-fragmented-ack-render-patterns-20260528.md`
- **Notable**: Wire format + Ghidra-Verified Analysis byte-confirmed. 1 HIGH-PRIORITY
  correction (C1: "Root Cause: Missing Cleanup" surgical deferral to ack-outbox-deadlock)
  + 2 medium/low corrections + 3 clarifications + 5 historical-preservation actions
  (hypothesis chain preserved as investigation log).

### 6.9 ack-outbox-deadlock.md — 2026-05-28

- **Verdict**: `verified` — second networking-family doc to clear `verified`
- **Archaeology memo**: `networking-leaf-ack-outbox-deadlock-validation-20260528.md`
- **Render memo**: `networking-ack-outbox-render-patterns-20260528.md`
- **Notable**: ZERO mechanism corrections. Most byte-verifiable networking-family doc
  to date. Supersedes netimmerse-transport's "ACK Retransmit Count Exhaustion" hypothesis.
  4 address-precision clarifications applied; no behavior or wire changes.

### 6.10 disconnect-flow.md — 2026-05-28

- **Verdict**: `partial`
- **Archaeology memo**: `networking-leaf-disconnect-flow-validation-20260528.md`
- **Render memo**: `networking-disconnect-flow-render-patterns-20260528.md`
- **Notable**: 5 material corrections (2 CRITICAL). C1 CRITICAL: FUN_006b6a20 ↔
  FUN_006b6a70 swap (case 4 = BOOT; case 5 = DISCONNECT — graceful path also has
  broadcast-relay step). C2 CRITICAL: peer offsets +0x2C ↔ +0x30 swap (+0x2C = lastRecvTime).
  C3: 4th convergence path (connect-clobber at 0x006b5d97). **C4: 0x006a0a20 IS
  DisconnectHandler — supersedes wrong Ghidra plate from leaf #18 — propagated to Ghidra
  rename + leaf #18 doc patch** (Ghidra plates corrected this pass; leaf #18 doc patched
  separately). C5: BootPlayerHandler is MultiplayerWindow not MultiplayerGame.

### 6.11 ship-death-lifecycle.md — 2026-05-28

- **Verdict**: `partial` (FINAL networking leaf)
- **Archaeology memo**: `networking-leaf-ship-death-lifecycle-validation-20260528.md`
- **Render memo**: `networking-ship-death-render-patterns-20260528.md`
- **Notable**: Zero wire/sequence corrections. 2 minor cosmetic/speculation fixes
  ("TGSubsystemEvent" name fabrication cascade — renamed to "TGEvent factory 0x101
  ET_ADD_TO_REPAIR_LIST"; SCORE_CHANGE Python handler IS registered, root cause is in
  Python early-return logic). 1 clarification (handler at 0x006a1240 was bare code,
  CREATED this pass as `MultiplayerGame_ObjectExplodingHandler`). 3 OQs. Cross-doc
  tension on opcode 0x14 resolved via disconnect-flow inline correction.

## 7. Campaign close summary (2026-05-28)

**Networking family v5 campaign is closed at 11/11 docs validated.**

- **2 docs `verified`**: #2 alby-rules-cipher, #9 ack-outbox-deadlock
- **9 docs `partial`**: all load-bearing claims now byte-anchored; minor cleanups
  deferred for future polish

### Architectural discoveries surfaced

- AlbyRules cipher full algorithm (KSA + two-LCG cross-XOR PRGA + re-key-per-packet)
  byte-confirmed; UDP-tolerance property explains stock dedi resilience
- GameSpy crypto: RC4 PRGA modification `i = (data[n] + 1 + i) % 256` byte-confirmed;
  secret key "Nm3aZ9" byte-confirmed; gamever literal `\1.6\` (NOT `\1.1\`) — OpenBC
  clean-room cascade flag
- TGMessage routing: **per-handler relay, not transport-level auto-relay** — this is
  the OpenBC parity bug for 0x06/0x0D/0x13 duplicate delivery
- THREE routing mechanisms (per-handler relay + Python SendTGMessage + connect-event
  broadcast at FUN_006B63A0)
- NoMe / Forward groups created by **C++ MultiplayerGame_Ctor** at 0x0069E590 (NOT
  Python)
- 4 disconnect detection paths (was documented as 3) — missing path is
  ProcessIncomingPackets connect-clobber at 0x006b5d97
- ACK-outbox deadlock root cause: pass-2 gate `(msg_count > 0 OR peer+0xBC != 0) AND
  peer+0xB4 > 0` — supersedes earlier "missing cleanup" hypothesis
- Peer seq counter offsets corrected to +0x24/+0x26/+0x28/+0x2A across the family
- 0x006a0a20 is `MultiplayerGame__DisconnectHandler` (3-byte stub for event 0x60003);
  0x006a07d0 is `MultiplayerGame__EnterSetHandler` (sends BOTH 0x1D and 0x1F);
  Ghidra plates corrected; leaf #18 cross-doc patch follow-up batched
- Player slot table at MpgameBase+0x78 (not +0x74 — engine ui-class-hierarchy.md also
  inherits the off-by-4)
- Cross-family confirmation: opcode 0x14 DestroyObject is NOT used for combat kills
  (0/59 in 33.5-min battle trace) — only for disconnect cleanup

### Family-close batch follow-ups

- CLAUDE.md Documentation Index refreshed to reflect 11/11 networking validated
- `.claude/agent-memory/documentation-writer/MEMORY.md` merged with 11 render-pattern
  memos
- Ghidra plates corrected at 0x006a0a20 (DisconnectHandler) + 0x006a07d0 (EnterSetHandler)
- Leaf #18 doc (objnotfound-requestobj-enterset-wire-format.md) patched with the C4
  cross-doc correction
- OpenBC clean-room cascade for gamespy-crypto C1 (gamever `\1.6\`) + tgmessage-routing
  C1 (per-handler relay) is OUT-OF-SCOPE for this family but flagged for OpenBC team
- engine doc ui-class-hierarchy.md +0x74 → +0x78 propagation is deferred (engine family
  already closed; will need a single targeted re-render)

### Campaign progression

- Engine family: 10/10 verified (2026-05-28)
- Protocol family: 22/22 (4 verified + 18 partial, 2026-05-28)
- Networking family: 11/11 (2 verified + 9 partial, 2026-05-28)
- Gameplay family: pending (16 docs in `docs/gameplay/`)

Total v5-validated docs to date: **43/43 across 3 families.**
