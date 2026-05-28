> [docs](../README.md) / [protocol](README.md) / v5-validation-status.md

---
title: Protocol Docs V5 Validation Status
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
  - docs/protocol/README.md
  - docs/protocol/wire-format-spec.md
  - docs/protocol/stream-primitives.md
  - docs/protocol/transport-layer.md
  - docs/protocol/game-opcodes.md
  - docs/protocol/checksum-opcodes.md
  - docs/protocol/python-messages.md
  - docs/protocol/tgmessage-routing.md
  - docs/protocol/stateupdate.md
  - docs/protocol/object-replication.md
  - docs/protocol/objcreate-serialization.md
  - docs/protocol/stateupdate-subsystem-wire-format.md
  - docs/protocol/per-ship-subsystem-wire-format.md
  - docs/protocol/tgobjptrevent-class.md
  - docs/protocol/pythonevent-wire-format.md
  - docs/protocol/collision-effect-protocol.md
  - docs/protocol/set-phaser-level-protocol.md
  - docs/protocol/delete-player-ui-wire-format.md
  - docs/protocol/objnotfound-requestobj-enterset-wire-format.md
  - docs/protocol/subsystem-integrity-hash.md
  - docs/protocol/cf16-precision-analysis.md
  - docs/protocol/cf16-explosion-encoding.md
  - docs/protocol/message-trace-vs-packet-trace.md
companions:
  - docs/engine/v5-validation-status.md
  - docs/protocol/README.md
  - docs/guides/v5-evidence-header.md
  - docs/guides/v5-doc-validation-workflow.md
---

# Protocol Docs V5 Validation Status

Tracker for the v5 evidence-standard re-validation campaign on `docs/protocol/`. This is the
second family in the campaign (engine completed 2026-05-28, 10/10 docs). It inventories
what the 22 existing protocol docs claim and how much of each claim is backed by
Ghidra-anchored evidence. It does **not** validate or correct any claim — validation
happens per-doc in subsequent phases. The archaeology specialist is producing a parallel
protocol-specific Ghidra snapshot to be merged with this inventory.

## 1. Campaign overview

Protocol docs sit on top of two foundations: the engine family (already validated — vtables,
TGEvent/TGBufferStream layouts, event manager) and the wire-format primitive layer
(`stream-primitives.md`, `transport-layer.md`). The mid-tier groups the opcode tables
(`game-opcodes.md`, `checksum-opcodes.md`, `python-messages.md`) and the heavy per-opcode
references (`stateupdate.md`, `objcreate-serialization.md`); leaves are per-opcode RE docs
(`collision-effect-protocol.md`, `set-phaser-level-protocol.md`, etc.) and analyses
(`cf16-*.md`, `subsystem-integrity-hash.md`). Re-validating in foundation→leaves order means
every opcode-handler address gets anchored once in the foundation and the leaves cite the
foundation by reference instead of re-deriving.

Expected outputs per doc: (1) every load-bearing claim either cites a hex address /
`FUN_xxxx` confirmed by the archaeology snapshot, or is demoted to `confidence: low` / dropped;
(2) v5 frontmatter (`status: verified | partial | disputed | stale`); (3) cross-links into
the engine-family anchor table where applicable; (4) cross-doc disagreements (§4 below)
resolved with the binary as authority. CLAUDE.md's Documentation Index and the section README
will be batch-updated at end of family close.

## 2. Validation order (foundation → leaves)

Order reflects dependency direction. Each row's anchors are consumed by all rows below it.

| # | Doc | Layer | Pre-existing depends on | Current status |
|---|-----|-------|--------------------------|----------------|
| 1 | wire-format-spec.md | Foundation / hub: opcode index + handler addresses + subsystem catalog | (engine: MpgameHandleMessage, vtable anchors) | **partial (2026-05-28)** — body restructure pending; see §6.1 |
| 2 | stream-primitives.md | Foundation: TGBufferStream read/write + CF16 + CompressedVector3/4 | (engine: TGBufferStream vtable 0x008958D0) | **partial (2026-05-28)** — see §6.2; one CV3 correction + restructure for two-class disambiguation |
| 3 | transport-layer.md | Foundation: UDP framing + 7 transport types + TGMessage vtable + fragments | wire-format-spec, stream-primitives | **partial (2026-05-28)** — 4 corrections, AlbyRules cipher anchored, TGMessage cascade absorbed; see §6.3 |
| 4 | game-opcodes.md | Mid: opcodes 0x00-0x2A handler addresses + per-opcode formats | wire-format-spec, transport-layer | **partial (2026-05-28)** — opcode table fully anchored from dispatcher recovery; one column-header clarification + small wire-format anchorings; see §6.4 |
| 5 | checksum-opcodes.md | Mid: opcodes 0x20-0x28 NetFile dispatcher | wire-format-spec, transport-layer | pending |
| 6 | python-messages.md | Mid: opcodes 0x2C+ MAX_MESSAGE_TYPES + SendTGMessage path | wire-format-spec, stream-primitives | pending |
| 7 | tgmessage-routing.md | Mid: relay-all + star topology + opaque payload | python-messages, transport-layer | pending |
| 8 | stateupdate.md | Mid: opcode 0x1C dirty flags + 8 field formats + round-robin | game-opcodes, stream-primitives | pending |
| 9 | object-replication.md | Mid: FUN_0069f620 thin index for ObjCreate | game-opcodes | pending |
| 10 | objcreate-serialization.md | Mid: full ObjCreate chain + species map | object-replication, stream-primitives | pending |
| 11 | stateupdate-subsystem-wire-format.md | Mid: subsystem linked list + 3 WriteState formats | stateupdate | pending |
| 12 | per-ship-subsystem-wire-format.md | Mid: 16 stock ship subsystem catalogs | stateupdate-subsystem-wire-format | pending |
| 13 | tgobjptrevent-class.md | Mid: TGObjPtrEvent class layout + 11 producers | (engine: TGEvent vtable 0x00895FF4) | pending |
| 14 | pythonevent-wire-format.md | Leaf: opcode 0x06 + 4 event factories | tgobjptrevent-class, game-opcodes | pending |
| 15 | collision-effect-protocol.md | Leaf: opcode 0x15 + CollisionEvent class + validation chain | game-opcodes, stream-primitives | pending |
| 16 | set-phaser-level-protocol.md | Leaf: opcode 0x12 + TGCharEvent | game-opcodes, tgobjptrevent-class | pending |
| 17 | delete-player-ui-wire-format.md | Leaf: opcode 0x17 + factory 0x866 | game-opcodes, pythonevent-wire-format | pending |
| 18 | objnotfound-requestobj-enterset-wire-format.md | Leaf: opcodes 0x1D/0x1E/0x1F triad | game-opcodes, objcreate-serialization | pending |
| 19 | subsystem-integrity-hash.md | Leaf analysis: dead-code anti-cheat hash | stateupdate, per-ship-subsystem-wire-format | pending |
| 20 | cf16-precision-analysis.md | Leaf analysis: CF16 encoder/decoder + precision tables | stream-primitives | pending |
| 21 | cf16-explosion-encoding.md | Leaf analysis: opcode 0x29 + mod weapon ID round-trip | cf16-precision-analysis, game-opcodes | pending |
| 22 | message-trace-vs-packet-trace.md | Leaf analysis: cross-trace opcode reconciliation | game-opcodes, stateupdate, tgmessage-routing | pending |
| — | README.md | Index only — refreshed at end of family | all above | pending |

A foundation doc must reach `status: verified` before docs that depend on it begin
validation. This prevents wasted re-renders when a foundation correction cascades downward.
Per the engine campaign's lesson: process-meta docs (this tracker) carry `status: partial`
until the campaign concludes — it would be misleading to mark a tracker `verified` while
its per-doc rows are still pending.

## 3. Per-doc inventory

### 3.1 wire-format-spec.md

- **Size:** 12,842 bytes
- **Doc type:** reference (hub / index over the protocol family)
- **Load-bearing claims:** ~110 (3 MultiplayerWindow opcode rows + 28 game-opcode rows + 7 Python-message rows + 6 checksum rows + 29 event-handler registration rows + 15 vtable-to-subsystem rows + 13 ship-slot offset rows + 12 hash-order rows)
- **Currently cited:** ~108 — every opcode row carries a handler address; every event handler has an address; every vtable + subsystem row has an address. Two rows are address-free (the 0x04/0x05 "dead" jump-table defaults).
- **Top load-bearing claims:**
  - "Game opcodes 0x02-0x2A dispatched by MultiplayerGame ReceiveMessageHandler at 0x0069F2A0 via 41-entry jump table at 0x0069F534"
  - "MultiplayerWindow dispatcher FUN_00504c10 owns opcodes 0x00/0x01/0x16"
  - "28 event-handler registration rows from FUN_0069efe0 with addresses 0x006a0a10 to 0x006a2a40"
  - "ShipRef slot at ship+0x2E0 holds NiNode scene-graph backpointer (vtable 0x00895340)"
  - "Anti-cheat hash iterates 12 slots from ship+0x27C in fixed order (Power, Shield, Powered, Cloak, Impulse, Sensor, Warp, Crew, Torpedo, Phaser, Pulse, Tractor)"
- **Cross-references in:** README.md, message-trace-vs-packet-trace.md, all 6 sub-docs
- **Cross-references out:** transport-layer, stream-primitives, checksum-opcodes, game-opcodes, stateupdate, object-replication, python-messages, plus 9 related-protocol docs, plus `../analysis/subsystem-trace-analysis.md` and `subsystem-integrity-hash.md`
- **Visible debt:**
  - Two distinct anti-cheat-hash tables (lines 188-208 and the per-ship slot map). Slot 11 says "Pulse Weapon System" hashing at `+0x40` / `+0x2BC` but the per-ship slot map shows `+0x2BC` is "always NULL / unused" — needs reconciliation against `subsystem-integrity-hash.md` which calls slot 11 "Pulse Weapon System" at ship+0x2BC.
  - Subsystem-table vtable addresses (0x0088A1F0, 0x00892C98, …) overlap with TG/Ship hierarchy claims in `docs/engine/tg-hierarchy-vtables.md` and `docs/engine/rtti-class-catalog.md` but no cross-link is made.
  - "Validated by JMP detour trace 2026-02-10" provenance lives in the body — should move to frontmatter on re-validation.
  - Opcode 0x17 row in the hub table says factory `0x866`; `delete-player-ui-wire-format.md` also says `0x866`; needs verification — `0x866` is a `TGEvent`-family factory ID range and we should anchor it.
- **Difficulty:** moderate (mechanical address-by-address re-check, but ~108 cited rows is a lot of surface area)

### 3.2 stream-primitives.md

- **Size:** 6,332 bytes
- **Doc type:** reference
- **Load-bearing claims:** ~50 (7 write-function rows + 7 read-function rows + 5 TGBufferStream offset rows + 4 CF16 constant rows + 1 CF16 encoder addr + 1 CF16 decoder addr + 2 CompressedVector3 addresses + 2 CompressedVector4 addresses + bit-packing format claim + 5 wire-format byte claims)
- **Currently cited:** ~50 — every function has an address (FUN_006cf… range), every constant has a DAT_… address, every layout offset is given.
- **Top load-bearing claims:**
  - "TGBufferStream offsets: +0x1C buffer ptr, +0x20 capacity, +0x24 position, +0x28 bit-pack bookmark, +0x2C bit-pack state"
  - "WriteByte FUN_006cf730, WriteShort FUN_006cf7f0, WriteInt32 FUN_006cf870, WriteFloat FUN_006cf8b0"
  - "CF16 encoder FUN_006d3a90, decoder FUN_006d3b30; constants BASE=0.001 at DAT_00888b4c, MULT=10.0 at DAT_0088c548, ENC_SCALE=4095.0 at DAT_00895f50, DEC_SCALE=1/4095 at DAT_00895f54"
  - "Bit packing format: [count:3][bits:5] in one byte, up to 5 booleans"
  - "CompressedVector3 write FUN_006d2ad0, read FUN_006d2eb0, wire = 5 bytes (dirX/dirY/dirZ u8 + magnitude u16)"
- **Cross-references in:** wire-format-spec.md, transport-layer.md (appendix), python-messages.md (WriteCString fn map)
- **Cross-references out:** cf16-precision-analysis.md, cf16-explosion-encoding.md
- **Visible debt:**
  - Write function table at line 13 lists 7 writes; python-messages.md fn map lists 8 (it adds WriteBool/WriteLong/WriteCString). The two docs are not in sync — stream-primitives.md is missing WriteBool (vtable+0x58), WriteLong (vtable+0x6C), WriteCString (vtable+0x24). Same for reads.
  - The TGBufferStream offsets section says "+0x2C = 0 means no active bit group" but the body's bit-packing section refers to `+0x2C` as the bookmark — needs disambiguation; transport-layer.md Appendix A treats `+0x28` as bookmark and `+0x2C` as bit-pack state. The two protocol docs already agree internally; the conflict is between the offsets paragraph and the bit-packing paragraph in this same file.
  - No frontmatter / metadata. Doc type stated only by file location.
  - Read vtable+0x80 = ReadInt32v (FUN_006cf6a0) is described as "Reads via vtable (variant read)" — collision-effect-protocol.md says it's a thunk to ReadU32 at +0x68. Conflicting wording.
- **Difficulty:** trivial (each function/constant is a single Ghidra spot-check)

### 3.3 transport-layer.md

- **Size:** 15,989 bytes
- **Doc type:** reference (with some explanation in fragment section)
- **Load-bearing claims:** ~100 (1 encryption claim + 3 raw UDP layout rows + 7 transport-type factory rows + 1 type-0x32 wire format + 5 flags_len bit-field rows + 1 type-0x00 wire format + 1 type-0x01 ACK wire format + fragment reassembly description + reliable delivery sequence counter pair + TGMessage 22-field layout + TGMessage base vtable 8 slots + TGDataMessage vtable 5 slots + 4 message-dispatcher rows + flags_len high-byte 4 commonly-observed values + fragment example traces + TGBufferStream Appendix A layout + Network Object Tracker Appendix B layout)
- **Currently cited:** ~100 — every factory has an address, every TGMessage offset is given, every vtable slot has an address.
- **Top load-bearing claims:**
  - "AlbyRules! cipher key at 0x0095abb4; SendPacket FUN_006b9870, ReceivePacket FUN_006b95f0; byte 0 NOT encrypted (cipher operates on buffer+1)"
  - "Factory table at DAT_009962d4 has 256 slots, 7 populated (types 0x00-0x05 and 0x32)"
  - "Type 0x32 = general game-payload TGMessage, vtable 0x008958d0, base factory FUN_006b83f0"
  - "TGMessage constructor FUN_006b82a0 allocates 0x40 bytes from pool FUN_00717b70"
  - "Two reliable sequence counters: peer+0x98 for types <0x32, peer+0xA8 for types >=0x32"
- **Cross-references in:** wire-format-spec.md
- **Cross-references out:** none explicit (refers to FUN_006b5c90, FUN_006b6cc0 internally)
- **Visible debt:**
  - Two TGMessage object-layout tables (lines 173-197 and 296-323). They mostly agree but differ on three fields: +0x2C ("retry_strategy" vs "num_retries"), +0x30 ("base_delay" vs "backoff_time"), +0x34 ("delay_factor" vs "backoff_factor"). The second table is more detailed; needs single source of truth.
  - "Network Object Tracker Layout" Appendix B is for StateUpdate per-ship tracking, not really transport — belongs in `stateupdate.md` or its subsystem-format sibling.
  - "Historical Note on flag 0x01" already does correction work (previous doc said "more fragments", correction says "bit 8 of length"). Mark these as `[v5-validated]` once re-confirmed; keep the historical note for context.
  - No frontmatter.
- **Difficulty:** moderate (TGMessage layout reconciliation is the only non-mechanical bit; factory addresses are mechanical)

### 3.4 game-opcodes.md

- **Size:** 14,689 bytes
- **Doc type:** reference
- **Load-bearing claims:** ~140 (2 jump-table claims + 25 per-opcode handler addresses + 25 per-opcode wire-format rows + 11 GenericEventForward event-code rows + 8 SpeciesToShip rows + collision-effect detail + sender/receiver event-code pairing list + torpedo flags1/flags2 observed values + beam flags observed values + opcode 0x14 stock-trace negative claim)
- **Currently cited:** ~135 — handler addresses present for every opcode; ship+offset readers/writers given; event-code constants given. ~5 narrative observations (e.g. "ships die via 0x29+0x03 respawn") cite trace evidence, not Ghidra.
- **Top load-bearing claims:**
  - "MultiplayerGame ReceiveMessageHandler at 0x0069f2a0 with 41-entry jump table at 0x0069F534, opcodes 0x02-0x2A"
  - "GenericEventForward FUN_0069FDA0 handles opcodes 0x07-0x0C, 0x0E-0x12, 0x1B with 11 event code mappings"
  - "Sender/receiver event-code pairing: D8→D7 (StartFire), DA→D9, DC→DB, DD→6C, E2→E3, E4→E5, EC→ED, FE→FD; exception 0x12 has no pairing"
  - "Opcode 0x15 CollisionEffect: typeClassId=0x00008124, eventCode=0x00800050, total = 22 + count*4 bytes"
  - "Opcode 0x29 Explosion: 14 bytes total, radius written first by sender (from source+0x14), damage second (from source+0x1C)"
- **Cross-references in:** wire-format-spec.md, README.md, message-trace-vs-packet-trace.md, plus every leaf wire-format doc
- **Cross-references out:** pythonevent-wire-format, collision-effect-protocol, cf16-precision-analysis, set-phaser-level-protocol, ../gameplay/self-destruct-pipeline, ../gameplay/repair-system, delete-player-ui-wire-format
- **Visible debt:**
  - "Stock 15-min count" column on the event-forward table cites packet-trace counts (2282, 33, etc.) — fine but needs explicit trace-citation as `confidence: medium` since these are trace observations, not Ghidra-grounded.
  - Opcodes 0x17, 0x18 each have only "Handler: FUN_006A1360 / FUN_006A1420" with no wire format — delete-player-ui-wire-format.md fills 0x17 in; nothing fills 0x18. Documentation debt: 0x18 has no companion doc.
  - SpeciesToShip table here is a subset (15 IDs) — objcreate-serialization.md has the full 45-entry table. Either link or unify.
  - Opcode 0x29 receiver name: "Handler_Explosion_0x29 at 0x006A0080" matches cf16-explosion-encoding.md. Consistent.
- **Difficulty:** moderate (high address density; the event-code mapping is the trickiest part)

### 3.5 checksum-opcodes.md

- **Size:** 3,922 bytes
- **Doc type:** reference
- **Load-bearing claims:** ~35 (1 dispatcher claim + 6 per-opcode handler addresses + 6 wire formats + 5-round table (5 rows) + 2 0x21 routing branches + 0x22/0x23 sub-opcode split + 0x25 transfer-mode gate + 0x28 description + 0x24/0x26 negative claim)
- **Currently cited:** ~32 — every handler has an address. The 5-round table has no per-row Ghidra address (it's derived from runtime trace).
- **Top load-bearing claims:**
  - "NetFile::ReceiveMessageHandler at FUN_006a3cd0 dispatches opcodes 0x20-0x28"
  - "0x21 routing: byte[1]==0xFF → main path; else FUN_006a4560 (verify) or FUN_006a5570 (mismatch)"
  - "5 checksum rounds: 0x00 scripts/App.pyc, 0x01 scripts/Autoexec.pyc, 0x02 scripts/ships/*.pyc recursive, 0x03 scripts/mainmenu/*.pyc, 0xFF Scripts/Multiplayer/*.pyc recursive"
  - "0x25 file transfer entry gated on this+0x14: 0 = setup dialog, !=0 = data path"
  - "0x24, 0x26 = unknown/unused: no handler, no packet trace evidence"
- **Cross-references in:** wire-format-spec.md, README.md
- **Cross-references out:** none
- **Visible debt:**
  - The 5-round table directories (`scripts/`, `scripts/ships`, `scripts/mainmenu`, `Scripts/Multiplayer`) come from observation, not Ghidra — they should be anchored to the actual string-literal addresses in the binary.
  - "0x28 — No dedicated handler" needs a positive citation that the jump table does NOT have a 0x28 entry (it's a negative claim per v5 standard).
  - No frontmatter.
- **Difficulty:** trivial

### 3.6 python-messages.md

- **Size:** 11,170 bytes
- **Doc type:** reference + how-to (mixed Diátaxis)
- **Load-bearing claims:** ~80 (mechanism description (2) + MAX_MESSAGE_TYPES constant + 10 Python-constant rows + 8 SWIG vtable-slot rows for writes + Python TGMessage create/send pattern + SendTGMessage two-mode description + SendTGMessageToGroup spec + 2 built-in group names + CHAT_MESSAGE wire example + custom-mod wire example + 6-step receive-side dispatch + 6-row handler list + SetGuaranteed semantics)
- **Currently cited:** ~70 — every SWIG vtable slot has an address (0x006cf… range), MAX_MESSAGE_TYPES constant has a value, group names have string addresses. The 6-step receive dispatch cites handler addresses.
- **Top load-bearing claims:**
  - "MAX_MESSAGE_TYPES = 43 (0x2B), registered at 0x00654f31 in SWIG init, stored at 0x0090b490"
  - "SetDataFromStream at 0x006b8a00 calls stream GetBuffer (vtable+0xF4) and GetPos (vtable+0xD8), then BufferCopy at FUN_006b84d0"
  - "SendTGMessage at FUN_006b4c10 (__thiscall, SWIG 'OiO|i'); targetID==0 broadcasts, >0 binary-searches peers, ==-1 special mode"
  - "Built-in groups created by MultiplayerGame ctor FUN_0069e590: 'NoMe' at 0x008e5528, 'Forward' at 0x008d94a0"
  - "Receive dispatch flow has 6 steps ending in TGMessageEvent created at FUN_006bfe80 (size 0x2C), posted as ET_NETWORK_MESSAGE_EVENT (0x60001)"
- **Cross-references in:** wire-format-spec.md, README.md, tgmessage-routing.md (twice)
- **Cross-references out:** stream-primitives.md (implicit — writes use TGBufferStream)
- **Visible debt:**
  - Diátaxis violation: mixes how-to ("Python Usage Pattern" code blocks) with reference (vtable slot tables). Splitting is plausible but not urgent.
  - The 8-row SWIG write primitives table is more complete than stream-primitives.md's 7-row table. Sync needed.
  - Wire example header byte 0x800F is decoded as "bit 15 = reliable" — fine, but also `bit 12-0 = length`; the bit layout description matches transport-layer.md. Cross-check the flags-len bit order across both docs.
  - The "Receive Side Dispatch" step 4 says `TGMessageEvent` at FUN_006bfe80 size 0x2C — this is a class layout claim that belongs in the engine event-system-architecture doc.
- **Difficulty:** moderate

### 3.7 tgmessage-routing.md

- **Size:** 17,296 bytes
- **Doc type:** explanation + reference (mixed; lots of "why" plus address tables)
- **Load-bearing claims:** ~90 (4 executive-summary Q&A claims + 2-system-types description (3 rows each) + factory-table 7-row catalog + factory-registration claim + 3-step receive path + type-0x00 factory pseudocode + host relay path + BroadcastToOthers pseudocode + SendTGMessage pseudocode + SendTGMessageToGroup pseudocode + NoMe group description + 3 C++ dispatcher analyses + Python message dispatch flow + 10 Python-allocation rows + Python receive pattern + chat relay description + star-topology 4-evidence list + 4-mode broadcast semantics table + Kobayashi Maru / BC Remastered compatibility analysis + PythonEvent 0x06 vs 0x0D 1:1 trace evidence (Valentines) + OpenBC parity bug note + 17-row Key Addresses table)
- **Currently cited:** ~80 — every function in the Key Addresses table has an address; every factory in the factory table has an address; pseudocode functions are named with addresses.
- **Top load-bearing claims:**
  - "TGNetwork constructor at 0x006b3a00 initializes factory table at 0x009962d4 (256 slots, 7 populated)"
  - "Type-0x00 factory FUN_006bc6a0 does opaque BufferCopy — no game-opcode inspection"
  - "BroadcastToOthers (host relay) at FUN_006b51e0 iterates peer array unconditionally"
  - "RegisterMessageType SWIG wrapper at 0x005e4860 uses (type & 0xFF) mask as only bounds check; stock Python never calls it"
  - "PythonEvent 0x0D NOT relayed: 75 wire-count == 75 factory events in Valentine's Day 3-player 33.5min trace; only 1:1 opcode in trace data"
- **Cross-references in:** wire-format-spec.md, README.md, python-messages.md (twice)
- **Cross-references out:** ../networking/tgmessage-routing-cleanroom.md (clean-room sibling)
- **Visible debt:**
  - "OpenBC Parity Bug" section is implementation-status content in a behavioral-spec doc. Acceptable but should move to a separate parity tracker per the engine campaign's separation rule.
  - The 0x0D 1:1 ratio claim is medium-confidence (trace-based, not Ghidra). Needs `confidence: medium` annotation.
  - "The original developers left it open" (silent fallthrough enabling mod compat) is editorial; fine for explanation type.
  - Receive path step 3.b reads `factory_table[transport_type * 4]` — confirm `* 4` (pointer table stride) against the engine RTTI-hash convention.
- **Difficulty:** moderate

### 3.8 stateupdate.md

- **Size:** 12,318 bytes
- **Doc type:** reference
- **Load-bearing claims:** ~120 (serializer/receiver address pair + 9-byte fixed prefix layout + 8 dirty-flag rows + 7 per-flag wire-format sections (each with several sub-claims) + 3 WriteState implementation addresses + round-robin algorithm + receiver flag-0x20 pseudocode + flag direction-split observation (10,459 / 19,997 packet counts) + 5 top C→S flag combos + 5 top S→C flag combos + flag decision logic decompile with 3 conditions + complete receiver pseudocode (8 steps) + force-update timestamp explanation)
- **Currently cited:** ~100 — every primary function has an address, every flag has its read/write pseudocode, every WriteState implementation has its address. ~20 narrative claims (e.g., "subsystem hash dead code in MP", "weapon scale factor at DAT_008944c4") cite addresses but the claims are derivative.
- **Top load-bearing claims:**
  - "Serializer FUN_005b17f0, receiver FUN_005b21c0; round-robin tracker fields iVar7+0x30 (cursor), iVar7+0x34 (index)"
  - "8 dirty flags: 0x01 POS, 0x02 DELTA, 0x04 FWD, 0x08 UP, 0x10 SPEED, 0x20 SUB, 0x40 CLOAK, 0x80 WPN"
  - "C→S uses 0x80 (WPN) only; S→C uses 0x20 (SUB) only; mutually exclusive (10,459 / 19,997 verified packets)"
  - "Subsystem WriteState formats: Base FUN_0056d320, Powered FUN_00562960, Power FUN_005644b0"
  - "10-byte round-robin budget per tick on flag 0x20; ~6-byte budget on flag 0x80"
- **Cross-references in:** wire-format-spec.md, README.md
- **Cross-references out:** subsystem-integrity-hash.md, stateupdate-subsystem-wire-format.md, ../analysis/empty-stateupdate-root-cause.md (implicit)
- **Visible debt:**
  - Decompiled flag-decision logic comments say `DAT_0097fa8a == 0` (SP mode) triggers 0x80, but packet traces show clients send 0x80 in MP. The doc itself flags this contradiction: "This suggests the CLIENT-side value of `DAT_0097fa8a` differs from the HOST-side". Needs a v5 evidence-grounded resolution — does the client REALLY have `DAT_0097fa8a == 0` at serialization time? Either decompile the client init path or accept as `confidence: low` mystery.
  - "Force-Update Timing" cites `DAT_00888860` as a global threshold without a v5-grounded value.
  - Some references to "uStack_494._3_1_" Ghidra raw names should be cleaned up per v5 voice rules.
- **Difficulty:** hard (the DAT_0097fa8a vs trace discrepancy is a real open question)

### 3.9 object-replication.md

- **Size:** 1,050 bytes
- **Doc type:** reference (very thin)
- **Load-bearing claims:** ~6 (handler address + type_tag 2/3 split + owner_player_slot byte + team_id byte for type 3 + vtable[0x10C] serialization + 5-step receive-side flow with FUN_005a1f50 / FUN_0047dab0)
- **Currently cited:** ~5 (FUN_0069f620, FUN_005a1f50, FUN_006a19a0, FUN_0047dab0 named).
- **Top load-bearing claims:**
  - "FUN_0069f620 receives opcodes 0x02 (no team) and 0x03 (team)"
  - "Serialization via vtable[0x10C](buffer, maxlen)"
  - "Receive: swap local player slot, FUN_005a1f50 deserialize, replicate to peers, attach Network controller via FUN_0047dab0"
- **Cross-references in:** wire-format-spec.md, README.md
- **Cross-references out:** objcreate-serialization.md (one link)
- **Visible debt:**
  - Doc is so thin it could be folded into objcreate-serialization.md or game-opcodes.md. Currently both objcreate-serialization.md and this doc cover overlapping material; this one is the lighter index.
  - vtable slot 0x10C = WriteStream is a load-bearing claim that should anchor against the engine vtable maps.
- **Difficulty:** trivial

### 3.10 objcreate-serialization.md

- **Size:** 12,194 bytes
- **Doc type:** reference
- **Load-bearing claims:** ~80 (envelope spec + 8-byte stream header + 2 factory class IDs + Ship ReadStream offsets (10 rows) + species_type field description + set_name → SpeciesToSystem 9-row table + torpedo ReadStream + 15 playable-ship rows (SpeciesToShip) + 30 non-playable rows + MAX_FLYABLE_SHIPS / MAX_SHIPS constants + handler pipeline detail (10+ steps) + player context slot table (MultiplayerGame+0x84, stride 0x18) + object ID range formula + 2 decoded trace examples + 10-row key functions table)
- **Currently cited:** ~70 — every handler/factory/function has an address; species enum values are anchored to a script file (referenced by name, not in-binary address); 2 packet examples decoded.
- **Top load-bearing claims:**
  - "Handler FUN_0069f620; Ship deserialize FUN_005a1f50; species reader FUN_005a2030 stores at ship+0xEC"
  - "Factory class IDs: 0x00008008 = ShipClass (creates network tracker), 0x00008009 = Torpedo (no tracker)"
  - "MultiplayerGame+0x84 = 16-entry player slot array, stride 0x18; player N obj ID base = 0x3FFFFFFF + N*0x40000"
  - "Quaternion at offset 21-37 is 4 floats (W,X,Y,Z); 3 padding bytes at 41-43 always 0x00"
  - "set_name maps to Multiplayer.SpeciesToSystem (9 entries: Multi1-Multi7, Albirea, Poseidon)"
- **Cross-references in:** wire-format-spec.md, README.md, object-replication.md
- **Cross-references out:** none explicit (refers to Python script paths)
- **Visible debt:**
  - "Open Questions" section at end already lists 3 unknowns (padding bytes, subsystem_state blob, orientation quaternion vs Euler). Accept these as `confidence: low` rows on re-validation.
  - Species tables are sourced from `scripts/Multiplayer/SpeciesToShip.py`, not stbc.exe — these are external-corpus claims and need the two-tag convention from the engine cross-source pattern (`[cross-source-YYYY-MM-DD]` for Python script content).
  - SpeciesToSystem table partial — Multi8-Multi10 missing if they exist; needs grep.
- **Difficulty:** moderate

### 3.11 stateupdate-subsystem-wire-format.md

- **Size:** 18,177 bytes
- **Doc type:** reference (with explanation in Q&A section)
- **Load-bearing claims:** ~150 (executive summary + 4 Q&A claims + flag 0x20 block structure + 3 WriteState format specs (Base/Powered/Power) with addresses + receiver pseudocode + 12-row "what's IN the list" table with runtime type IDs + 5-row "what's REMOVED" table + Sovereign-class 11-row layout example + round-robin algorithm + linked list node struct + ship subsystem fields at +0x280/+0x284/+0x288/+0x28C + 15-row key functions table + 22 CT_ type constants + 17 property type constants + engine parent-child linking mechanism (EP_IMPULSE / EP_WARP enum) + Python API usage examples + named ship subsystem slots + stock-ship verification claim + subsystem classification in FUN_005b3e50 (2 partition lists) + 6 implications for dedi server)
- **Currently cited:** ~140 — every WriteState format function has an address, every runtime type ID has its hex value, every C++ function has an address.
- **Top load-bearing claims:**
  - "Round-robin over ship+0x284 doubly-linked list; 10-byte budget per tick"
  - "Three WriteState formats: Base 0x0056d320 (cond+children), Powered 0x00562960 (base+bit+powerPct), Power 0x005644b0 (base+2 batteries)"
  - "PowerSubsystem ALWAYS writes both battery bytes regardless of isOwnShip"
  - "Ship_LinkAllSubsystemsToParents FUN_005b3e20 removes children from 0x284 by reading property+0x48 tag for engines (EP_IMPULSE=0, EP_WARP=1)"
  - "Ship subsystem list fields: +0x280 count, +0x284 head, +0x288 tail, +0x28C free list"
- **Cross-references in:** wire-format-spec.md, README.md, stateupdate.md, per-ship-subsystem-wire-format.md
- **Cross-references out:** none
- **Visible debt:**
  - "Date: 2026-02-18 / Status: VERIFIED" — already claims verified status without v5 frontmatter. Move provenance to YAML, downgrade body claim until v5 re-validation.
  - 22 CT_ type constants and 17 property constants are presented as SWIG-registered values without their stbc.exe registration addresses (in stock python-152 init code). Need anchoring.
  - "Universal Subsystem Patterns" (7 always-present + 5 optional) is an extracted invariant — should be cross-checked against per-ship-subsystem-wire-format.md's claim that BoP is missing phasers (the only ship without PhaserSystem).
- **Difficulty:** moderate

### 3.12 per-ship-subsystem-wire-format.md

- **Size:** 22,917 bytes
- **Doc type:** reference (catalog)
- **Load-bearing claims:** ~250 (species ID mapping (17 rows) + WriteState type reference (3 rows) + summary table (16 ships, ~8 columns each ≈ 128 cells) + 15-row hardpoint-vs-tracer verification + 16 per-ship sections (each ~10-row subsystem table) + universal patterns list + round-robin timing table + implications list)
- **Currently cited:** ~30 — the addresses 0x005b17f0, 0x005b3e20, 0x005b3fb0, 0x0056d320, 0x00562960, 0x005644b0 anchor the algorithms. The per-ship subsystem counts/order come from hardpoint Python files (external corpus), verified against tracer count.
- **Top load-bearing claims:**
  - "Sovereign: 11 top-level / 22 children / 33 total; cycle 49 bytes"
  - "Bird of Prey: 10 top-level / 6 children / 16 total; no PhaserSystem; only ship with PulseWeapon-only weapons"
  - "All 15 hardpoint-derived counts match runtime function tracer exactly"
  - "All ships complete a full subsystem health cycle in under 1 second at 10Hz"
  - "Enterprise (species 37) inherits from Sovereign — identical layout, only HP/capacity differ"
- **Cross-references in:** README.md
- **Cross-references out:** stateupdate-subsystem-wire-format.md
- **Visible debt:**
  - This is fundamentally a **cross-source** doc (16 ship hardpoint scripts + stock-dedi tracer + stbc.exe addresses). Needs the two-tag convention. The stbc.exe-anchored claims are ~30; the rest are external-corpus claims.
  - "Date: 2026-02-22 / Status: HIGH-CONFIDENCE" — same pattern as the sibling doc. Move to frontmatter.
  - The 2026-02-22 collision test claim (15 species, 15 matches) lives in body — should be tagged `[cross-source-2026-02-22]`.
  - Per-ship sections lack Ghidra anchors entirely — they cite Python script line counts only. This is fine for content (the Python scripts are the source of truth) but needs explicit two-tag annotation.
- **Difficulty:** hard (lots of cells × 16 ships; bulk re-checks against the hardpoint files needed)

### 3.13 tgobjptrevent-class.md

- **Size:** 21,960 bytes
- **Doc type:** reference (with usage-pattern how-to mixed in)
- **Load-bearing claims:** ~180 (summary table (8 fields) + class layout 11 rows + difference vs TGCharEvent (6 comparison rows) + IsA chain (3 values) + class hierarchy diagram + wire-format spec (6 rows) + decoded packet example + 3-row serialization functions table + vtable map (7 slots) + 5-row Python API + Python usage pattern + 11-row C++ event type catalog + timer delivery row + dual-fire pattern (3 events) + ET_TARGET_WAS_CHANGED previous-target note + ET_STOP_FIRING_AT_TARGET_NOTIFY host-only gate + network-vs-local classification + Python script usage 27+ events (7-row most common) + 45% combat traffic stats + ET_ constant mapping formula + 12-row C++ event types with hex values + factory ID full table (5 rows) + ~10-row unanalyzed-code regions + 5-row vtable DATA references + infrastructure non-producer calls + complete Python event type table (27+ rows) + consolidated hex map 14 rows)
- **Currently cited:** ~150 — every function has an address, every vtable slot has an address, every event type has a hex value, every Python xref has a script-file pointer.
- **Top load-bearing claims:**
  - "Factory ID 0x010C, vtable 0x0088869C, size 0x2C, constructor 0x00403290"
  - "IsA chain: 0x10C → 0x101 (TGSubsystemEvent) → 0x02 (TGEvent)"
  - "Wire size 21 bytes (17-byte base + 4-byte int32 obj_ptr at offset 17)"
  - "WriteToStream 0x006D6DC0 calls stream vtable+0x84 (WriteInt32); ReadFromStream 0x006D6DF0 calls vtable+0x80 (ReadInt32)"
  - "1,718 of 3,825 PythonEvents (45%) in 33.5-min battle use factory 0x010C; dual-fire pattern is the driver"
- **Cross-references in:** wire-format-spec.md, README.md, pythonevent-wire-format.md
- **Cross-references out:** pythonevent-wire-format.md, repair-event-object-ids.md, set-phaser-level-protocol.md, weapon-firing-mechanics.md, repair-system.md, stock-trace-analysis.md
- **Visible debt:**
  - "C++ Producers in Unanalyzed Code Regions" section has 10 rows of `LAB_xxxxxxxx` addresses with "likely function" prose — these are inherently `confidence: low` until Ghidra disassembles those regions. Mark as such on v5.
  - "Vtable DATA References" lists 5 sites that WRITE the vtable into objects — 4 of them are in unanalyzed code. Need to anchor against `mcp__ghidra__get_xrefs_to` for the vtable.
  - ET_ constant mapping formula `value = 0x00800001 + (line_number - 12835)` is an external-corpus claim about App.py — flag as `[cross-source-…]`.
  - 27+ Python ET_ constants come from grep over script directory — bulk external-corpus.
  - The 11-row C++ event types table and the 12-row consolidated hex map duplicate each other — needs deduplication.
- **Difficulty:** hard (high address density + many cross-source rows + 10 unanalyzed-code claims)

### 3.14 pythonevent-wire-format.md

- **Size:** 31,241 bytes
- **Doc type:** reference (large, near-comprehensive per-class layouts and producers)
- **Load-bearing claims:** ~280 (overview + 0x0D shared-receiver claim + message structure 5 rows + 4-row factory catalog + object reference encoding rules + Ship/Subsystem ID encoding (DAT_0095B078, DAT_0099A67C) + 4 event-class sections (TGSubsystemEvent / TGCharEvent / TGObjPtrEvent / ObjectExplodingEvent), each with: wire layout 6 rows, class layout 11 rows, IsA chain, serialization function pair, decoded example + 3 producer descriptions (HostEventHandler 0x006A1150, ObjectExplodingHandler 0x006A1240, GenericEventForward 0x006A17C0) + 2 receiver paths (FUN_0069f880, FUN_0069fda0) + event-type override table (12 rows) + collision damage chain 7 steps + ~14 message count + worked example trace (14-row table) + 3 event registration tables (RepairSubsystem 4 events, MultiplayerGame 4 events, ShipClass 2 events) + TGEvent base vtable 18 slots + ObjectExplodingEvent vtable 9 slots + TGCharEvent vtable 14 slots + traffic stats (3 directions) + 25-row related-functions table + 10-row event-type constants table + collision chain event count breakdown)
- **Currently cited:** ~250 — every function has an address, every vtable has an address, every event type has hex value, every class layout has offsets.
- **Top load-bearing claims:**
  - "Opcode 0x06 polymorphic event transport; 4 event classes registered: 0x0101 / 0x0105 / 0x010C / 0x8129"
  - "Subsystem IDs from global counter DAT_0095B078, NOT derived from ship base"
  - "Hash table at DAT_0099A67C resolves IDs on receive"
  - "HostEventHandler FUN_006A1150 serializes opcode 0x06 to 'NoMe' group; gated on g_IsMultiplayer"
  - "ObjectExplodingEvent constructor 0x0043F8B0; WriteToStream 0x0043F990; ReadFromStream 0x0043F9C0"
- **Cross-references in:** wire-format-spec.md, README.md, game-opcodes.md
- **Cross-references out:** tgobjptrevent-class.md (twice), collision-effect-protocol.md, collision-detection-system.md, set-phaser-level-protocol.md, damage-system.md, cf16-explosion-encoding.md, repair-tractor-analysis.md, combat-mechanics-re.md
- **Visible debt:**
  - The 11-row TGObjPtrEvent event types table here is a subset of tgobjptrevent-class.md's tables — sync needed.
  - "Collision Chain Event Count" section says "12-14 PythonEvents per collision" with 1 ObjectExploding + 11 ADD_TO_REPAIR_LIST + 2 delayed. The "Worked Example" above lists 14 with 1 ObjectExploding + 13 ADD_TO_REPAIR_LIST. The math doesn't quite reconcile (11 + 2 = 13 vs 13 from the worked example). Flag for resolution.
  - "Event Type Constants" table at end has 10 rows; the consolidated hex map in tgobjptrevent-class.md has 14 rows. Sync.
  - TGEvent base vtable here lists 18 slots (0-17); engine-family vtable docs use 14-slot baseline. Need to verify whether TGEvent really has 18 virtuals or whether 15-17 are inherited from a higher base.
- **Difficulty:** hard (very dense; multiple sub-class layouts; sync to siblings)

### 3.15 collision-effect-protocol.md

- **Size:** 18,560 bytes
- **Doc type:** reference (with explanation)
- **Load-bearing claims:** ~110 (overview claim of 138,695 packets / 33.5min / 0 server-relayed instances + wire format (10 rows) + constant prefix (13 bytes) + contact point compression algorithm + 2 serialization paths (network vs persistence) + 3 example decoded packets + CollisionEvent class layout (18 fields) + constructor + destructor + SWIG API + receive handler logic 12 steps + 3 validation checks + send-side flow 4 steps + host-side damage processing (2 sub-handlers + Python) + event registration (ShipClass + DamageableObject) + related functions 27 rows + CollisionEvent vtable 16 slots + TGEvent base vtable 16 slots + Stream Reader vtable 8 slots)
- **Currently cited:** ~105 — every function has an address, every vtable slot has an address, contact-compression chain references stream vtable slots.
- **Top load-bearing claims:**
  - "Opcode 0x15 C→S only, server never relays (138,695 packets, 0 relays verified)"
  - "Handler FUN_006a2470; CollisionEvent::WriteToStream FUN_005871a0; ReadFromStream FUN_00587300"
  - "Wire size = 22 + count*4 bytes; force is raw f32, contacts are 4-byte CompressedVec4_Byte"
  - "3 validations: ownership (sender must own source or target), self-collision filter (rejects if target is local player), distance gap < DAT_008955c8 threshold"
  - "Event type transformation: arrives 0x00800050 (ET_OBJECT_COLLISION), re-posted as 0x008000FC (ET_HOST_OBJECT_COLLISION)"
- **Cross-references in:** wire-format-spec.md, README.md, game-opcodes.md, pythonevent-wire-format.md
- **Cross-references out:** none
- **Visible debt:**
  - Per-contact damage scaling formula "raw * 900.0 + 500.0" cites "constants verified from binary" but no specific DAT_ addresses for 900.0 / 500.0 / 0.01 — needs anchoring.
  - "DAT_008955c8 threshold" cited without value — needs anchoring.
  - "Effects.CollisionEffect (Python handler)" — external-corpus, needs cross-source tag.
  - 16-slot CollisionEvent vtable has 4 "(unknown)" slots — accept as `confidence: low` or anchor.
  - Two TGEvent vtable maps appear in this doc and pythonevent-wire-format.md with slightly different slot descriptions — reconcile.
- **Difficulty:** moderate

### 3.16 set-phaser-level-protocol.md

- **Size:** 16,159 bytes
- **Doc type:** reference (with explanation)
- **Load-bearing claims:** ~80 (overview + wire-format spec (6 rows) + serialization detail with TGCharEvent WriteToStream chain + object reference encoding + 3-row phaser power level values + 2 example decoded packets + TGCharEvent class layout (11 rows) + class hierarchy + constructor + SWIG factory + IsA chain + sender flow (PhaserSystem::SetPowerLevel 8 steps) + multiplayer bridge thunk (3 steps) + SendEventMessage flow (8 steps) + receive jump-table dispatch + GenericEventForward analysis (host relay + local dispatch) + applier 3 steps + critical asymmetry claim + event-type-code table + shared-handler group 12-row table + 2 event registrations + 14-row related functions + TGCharEvent vtable 14 slots)
- **Currently cited:** ~75 — every function has an address, every vtable slot has an address, every step in the flows is anchored.
- **Top load-bearing claims:**
  - "Opcode 0x12; wire size 18 bytes fixed; TGCharEvent factory 0x105"
  - "Sender thunk MultiplayerGame::SetPhaserLevelHandler at 0x006A1970"
  - "Applier PhaserSystem::SetPhaserLevelHandler at 0x00574180; PhaserSystem+0xF0 stores phaser level"
  - "0x12 uses generic forward override=0 (no event-code pairing); event keeps 0x008000E0 on both sides"
  - "Shared handler group (12 opcodes); 0x12 is in the override=0 subgroup with 0x0B, 0x0C, 0x11"
- **Cross-references in:** wire-format-spec.md, README.md, game-opcodes.md, pythonevent-wire-format.md, tgobjptrevent-class.md
- **Cross-references out:** none
- **Visible debt:**
  - "Critical asymmetry" claim ("receiver does NOT call SetPowerSetting on child weapons; level applies via StateUpdate") is partially speculative — phrased as "either the Update tick reads +0xF0 and applies it, or individual weapon intensity values are carried in StateUpdate". This is a `confidence: low` claim that needs decompile evidence one way or the other.
  - TGCharEvent vtable here matches the one in pythonevent-wire-format.md and tgobjptrevent-class.md (after re-check) — confirm in v5 pass.
  - SWIG factory registration "in the event factory hash table" cited without address.
- **Difficulty:** moderate (the "critical asymmetry" question is genuinely unresolved)

### 3.17 delete-player-ui-wire-format.md

- **Size:** 7,261 bytes
- **Doc type:** reference (with explanation)
- **Load-bearing claims:** ~30 (overview + wire format (6 rows) + factory ID 0x00000866 = TGEvent + 2 event codes (0x008000F1, 0x00060005) + 2 context field-value sets (join vs disconnect) + decoded join-time packet + 3-row trace frequency table + handler chain (5 steps with addresses) + scoreboard population 2-condition requirement + naming clarification + 5-row related docs)
- **Currently cited:** ~25 — handler FUN_006a1360, FUN_006d6200, FUN_006da2a0, NewPlayerInGameHandler 0x006a1590, DeletePlayerHandler FUN_006a0ca0 all anchored.
- **Top load-bearing claims:**
  - "Opcode 0x17 handler FUN_006a1360; factory 0x00000866 (base TGEvent) deserialized via FUN_006d6200"
  - "Join event code 0x008000F1 (ET_NEW_PLAYER_IN_GAME); disconnect event code 0x00060005 (ET_NETWORK_DELETE_PLAYER)"
  - "Wire size 18 bytes: opcode + factory_id + event_code + src_obj_id + tgt_obj_id + wire_peer_id"
  - "Scoreboard requires both TGPlayerList entry (from 0x17) AND score dict entry (from 0x37/0x36)"
- **Cross-references in:** wire-format-spec.md, README.md, game-opcodes.md
- **Cross-references out:** wire-format-spec.md, pythonevent-wire-format.md, ../networking/disconnect-flow.md, ../networking/multiplayer-flow.md
- **Visible debt:**
  - Factory ID 0x866 anchoring: the factory-ID range claim ("0x866 is a TGEvent-family factory ID") needs cross-reference to the factory table in tgobjptrevent-class.md, which lists factories 0x02 / 0x101 / 0x105 / 0x10C / 0x8129. Where does 0x866 fit? Likely a different factory family — needs Ghidra hash-table lookup.
  - "Zero 0x17 instances at disconnect time" is a negative claim — the doc admits insufficient trace coverage. Mark as `confidence: low` until a disconnect trace appears.
  - Mission1Menus.py reference is external-corpus.
- **Difficulty:** moderate (factory 0x866 is the key unknown)

### 3.18 objnotfound-requestobj-enterset-wire-format.md

- **Size:** 15,679 bytes
- **Doc type:** reference (with explanation)
- **Load-bearing claims:** ~70 (overview of triad + 3 per-opcode sections, each with: handler address + wire format + handler pseudocode with decompiled C + dispatch behavior + key observations + send-side analysis + 4-row relationship diagram + ObjNotFound to RequestObj round-trip + EnterSet warp scenario + Set Name "Space" set with string address 0x008d8ab8 + RequestObjEventHandler client-side sender at 0x006a07d0 + Set transition vtable[0x58/4] vs vtable[0x54/4] + OpenBC implementation notes + 7-row function address table)
- **Currently cited:** ~60 — every handler has an address, every key function has an address, the "Space" set string has an address.
- **Top load-bearing claims:**
  - "0x1D handler FUN_006a0490; sends 0x1E if also not found locally"
  - "0x1E handler FUN_006a02a0; host gates on object networked (+0x3b), HP threshold DAT_008e5c18, dead_flag; sends full ObjCreate (0x02 or 0x03) + replays explosions via DamageableObject__SendExplosions_0x29"
  - "0x1F handler FUN_006a05e0; reads null-terminated string, allocates with TGBufferStream__ReadString(-1), frees with NiFree_Wrapper"
  - "RequestObjEventHandler at 0x006a07d0 is client-side sender for both 0x1D and 0x1F; branches on warp state (ship+0xb4 + 0xb4)"
  - "Set Name 'Space' constant at 0x008d8ab8 — the default space combat set"
- **Cross-references in:** README.md (under \"Detailed Protocol Documents\" — verify wire-format-spec.md links to it; the protocol README does NOT currently list this doc as separate entry — see §4)
- **Cross-references out:** none explicit
- **Visible debt:**
  - **Missing from README.md table!** The protocol README only lists 18 specific docs (excluding this one + the v5-validation-status.md being created). Adding this to README is one of the campaign-close actions.
  - Doc has NO breadcrumb header `> [docs](...) / [protocol](...)`. Inconsistent with siblings.
  - No frontmatter.
  - "RequestObjEventHandler" is referenced as `MultiplayerGame__RequestObjEventHandler @ 0x006a07d0` but later as just "0x006a07d0". Naming consistent.
  - "GetPlayerSlotFromObjID" at 0x005a2030 — this address is ALSO claimed in objcreate-serialization.md as `FUN_005a2030 = ReadSpeciesByte`. Conflict! Two docs claim the same address for different functions. Resolution: probably one of them is wrong; objcreate-serialization.md's claim seems more strongly supported (it cites the species byte read into ship+0xEC). Flag for v5 binary check.
  - vtable slot computations use `/4` (e.g., "vtable[0x58/4]") — Ghidra-style byte-offset notation. House style prefers slot numbers.
- **Difficulty:** moderate (the 0x005a2030 conflict is real)

### 3.19 subsystem-integrity-hash.md

- **Size:** 16,204 bytes
- **Doc type:** reference + explanation (mixed; lots of "why dead")
- **Load-bearing claims:** ~120 (overview + dead-code-in-MP claim + 7-row function table + hash_fold pseudocode + base_subsystem_hash pseudocode + 7-property hash order + 4 boolean sentinels + ordering rule + ComputeSubsystemHash subsystem slot table (12 rows × ~5 columns) + corrections from prior analysis (2 misidentifications) + weapon_system_hash pseudocode + torpedo mirror convolution + individual_weapon_hash pseudocode + 5 type-dispatch sections (0x802B / 0x802C / 0x802D / 0x802E / 0x802F) each with property offset list + boolean sentinel constants table (6 entries) + sender pseudocode + receiver pseudocode + kick chain ET_BOOT_PLAYER 0x8000F6 + wire encoding XOR fold + dead-code proof + decompiled source line references)
- **Currently cited:** ~110 — every function has an address (0x005b6c10 hash_fold, 0x005b6170 base_subsystem_hash, 0x005b5eb0 ComputeSubsystemHash, etc.); every property offset is given; every magic constant has hex float bit-pattern.
- **Top load-bearing claims:**
  - "Dead code: sender writes only when isMultiplayer==0, receiver checks only when isMultiplayer==1 — never both"
  - "12 subsystem slots hashed in fixed order at ship+0x27C; corrected from prior analysis (Shield was misidentified as Repair, Torpedo as Shield)"
  - "Repair subsystem NOT in the hash (corrected from earlier docs)"
  - "Boolean sentinels use specific float constants: 64.0002f/76.6f, 98.6f/100.0f, 14.3f/456.1f, 27.3f/16.1f for base; 0.4f/99.1f, 32.6f/487.1f for weapon"
  - "Kick path: ET_BOOT_PLAYER 0x8000F6 → BootPlayerHandler 0x00506170 → TGBootPlayerMessage reason=4"
- **Cross-references in:** wire-format-spec.md, README.md, stateupdate.md (twice via subsystem-integrity-hash link)
- **Cross-references out:** none
- **Visible debt:**
  - The 12-slot subsystem table here partially overlaps with wire-format-spec.md's Anti-Cheat Hash table (which has the same 12 rows). Two sources of truth on the same data. Reconcile to one.
  - "Corrections from prior analysis" section at line 129 already explicitly flags 2 misidentifications. Carry these forward into the v5 frontmatter under the `supersedes:` field.
  - Decompiled source line numbers (~56151, ~56253, etc.) cite `reference/decompiled/05_game_mission.c` — these are derived-corpus refs (Ghidra-output text), should use the two-tag convention but the underlying claims are stbc.exe-grounded.
- **Difficulty:** moderate

### 3.20 cf16-precision-analysis.md

- **Size:** 7,785 bytes
- **Doc type:** explanation + reference (mixed)
- **Load-bearing claims:** ~70 (format bit layout + 5 constants table + encoder algorithm pseudocode + decoder algorithm pseudocode + 8-row scale table + precision characteristics + explosion-packet 0x29 wire format (8-byte description) + ExplosionDamage 9-field layout + mod weapon-type ID round-trip (4 rows) + integer-survival analysis (4 scales) + 4-row CF16 callers list)
- **Currently cited:** ~60 — every constant has a DAT_… address, every key function has an address (encoder FUN_006d3a90, decoder FUN_006d3b30, FUN_00595c60, FUN_006A0080, FUN_005b1e38). ExplosionDamage vtable at 0x0088c6c4 anchored. 4 xref sites cited but not enumerated.
- **Top load-bearing claims:**
  - "16-bit format: [sign:1][scale:3][mantissa:12]; 8 logarithmic decades 0 to 10000"
  - "Decoder uses 1/4095 (NOT 1/4096) — mantissa 4095 decodes to exactly range_hi"
  - "Encoder uses x87 __ftol (truncate toward zero, always rounds down)"
  - "Mod values 15.0/25.0/273.0/2063.0 all FAIL exact int round-trip but produce unique uint16 encodings"
  - "All float fields in opcode 0x29 are CF16 — no raw float32"
- **Cross-references in:** stream-primitives.md, README.md, game-opcodes.md, cf16-explosion-encoding.md (sibling)
- **Cross-references out:** cf16-explosion-encoding.md
- **Visible debt:**
  - Calculation tables (round-trip values) are deterministic from the algorithm + constants. They could be regenerated. Carry forward.
  - "ExplosionDamage struct" 9-field layout is partially in scope of game-opcodes.md too (different doc, same struct). Sync.
  - "4 CF16 callers confirmed via xref" doesn't enumerate the 4 callers — needs the actual address list.
- **Difficulty:** trivial

### 3.21 cf16-explosion-encoding.md

- **Size:** 9,637 bytes
- **Doc type:** explanation + reference (heavily overlaps cf16-precision-analysis.md)
- **Load-bearing claims:** ~80 (5-row constants table + bit layout + 8-row scale table + encoder pseudocode + decoder pseudocode + explosion 0x29 wire layout + sender FUN_00595c60 detail (explosion list at this+0x13C, radius at +0x14, damage at +0x1C) + receiver Handler_Explosion_0x29 + ExplosionDamage struct + BC Remastered weapon-type values + round-trip table (4 rows) + uniqueness check + round-match analysis + 3-row integer-collision-at-scale-7 + 3 recommended matching strategies + 14-row extended precision reference + 5-point assessment)
- **Currently cited:** ~70 — every constant has a DAT_… address, every function has an address. Same constants as cf16-precision-analysis.md.
- **Top load-bearing claims:**
  - Same constants as cf16-precision-analysis.md (BASE 0.001, MULT 10.0, ENC_MULT 4095.0, DEC_MULT 1/4095)
  - "Sender FUN_00595c60 iterates explosion list at this+0x13C; called from FUN_006a02a0 (RequestObj) and NewPlayerInGame handler"
  - "Receiver Handler_Explosion_0x29 at 0x006A0080"
  - "2063.0 fails round-trip (decodes to 2061.54 → rounds to 2062, not 2063); integer step at scale 7 is ~2.2"
  - "4 BC Remastered values produce unique uint16 encodings (0x50E3, 0x52AA, 0x6313, 0x71E3)"
- **Cross-references in:** stream-primitives.md, README.md, cf16-precision-analysis.md (sibling), pythonevent-wire-format.md (related)
- **Cross-references out:** cf16-precision-analysis.md
- **Visible debt:**
  - **Major overlap** with cf16-precision-analysis.md. Both docs have: same constants, same algorithm pseudocode, same scale table, same mod-value round-trip analysis. One should be the source of truth; the other should be a thin cross-reference. Resolution candidate: precision-analysis.md = the algorithm/constants reference; explosion-encoding.md = the explosion-specific wire format and mod-compatibility analysis only.
  - "BC Remastered" weapon-type values are external-corpus claims about a mod.
- **Difficulty:** trivial (after the merge decision is made)

### 3.22 message-trace-vs-packet-trace.md

- **Size:** 7,862 bytes
- **Doc type:** explanation + reference (cross-trace reconciliation analysis)
- **Load-bearing claims:** ~50 (key discovery: message_trace = receive path only + StateUpdate SUB/WPN direction split (10,459 / 19,997) + S→C flag-distribution top 5 + C→S flag-distribution top 5 + flags_len LE u16 bit layout + packet decoder bug for fragments + 13-row corrected opcode cross-reference table + 10-row S→C-only opcodes list + 5-row newly-identified opcodes + post-ObjCreate SUB cycling pattern + 5-row timing example + implications-for-proxy summary)
- **Currently cited:** ~5 — this doc is fundamentally trace-derived. The flag bit layout and StateUpdate cross-reference rely on stateupdate.md for grounding, but no addresses are cited here.
- **Top load-bearing claims:**
  - "message_trace.log captures only the RECEIVE path (TGMessage factory deserialization); all S→C messages absent"
  - "C→S uses WPN (0x80) always, SUB (0x20) never — 10,459 packets; S→C inverse — 19,997 packets"
  - "Type 0x32 flags_len: bits 12-0 length, bit 13 fragment, bit 14 ordered, bit 15 reliable"
  - "Bit 0 of flags_len high byte is NOT 'more fragments' — it is bit 8 of the 13-bit length"
  - "Packet trace decoder bug: misdecodes fragment_index as game opcode for fragmented checksum responses"
- **Cross-references in:** wire-format-spec.md (top), README.md
- **Cross-references out:** none
- **Visible debt:**
  - This is a **cross-source** doc (packet trace + message trace + stbc.exe-derived format). Should use the two-tag convention. All trace-derived claims are `[cross-source-2026-02-10]`.
  - The corrected opcode cross-reference table has counts that match stateupdate.md's direction-split claim. Both docs cite the same evidence; they should agree on which is canonical (stateupdate.md is the more reference-style location for the SUB/WPN finding).
  - "Implications for Our Proxy" section is implementation-status content — belongs in CLAUDE.md or a separate proxy-progress tracker.
  - No frontmatter.
- **Difficulty:** trivial (this doc is observational; few stbc.exe claims, mostly trace cross-referencing)

## 4. Cross-doc disagreements and documentation debt

Each row is a pre-existing inconsistency to surface; the v5 sweep should resolve to the
binary as authority.

| # | Disagreement | Sources | Authority candidate |
|---|--------------|---------|---------------------|
| 1 | `FUN_005a2030` semantics: "ReadSpeciesByte" (reads species into ship+0xEC) vs "GetPlayerSlotFromObjID" | objcreate-serialization.md (key-functions table) vs objnotfound-requestobj-enterset-wire-format.md (function-addresses table) | Ghidra decompile of 0x005a2030 — one of them is wrong |
| 2 | TGBufferStream write primitives count | stream-primitives.md = 7 writes; python-messages.md = 8 writes (adds WriteBool / WriteLong / WriteCString) | python-messages.md (more complete); merge into stream-primitives.md |
| 3 | TGMessage layout, fields +0x2C/+0x30/+0x34 | transport-layer.md table 1 vs table 2 within same file ("retry_strategy" vs "num_retries", "base_delay" vs "backoff_time", "delay_factor" vs "backoff_factor") | Ghidra decompile of TGMessage constructor FUN_006b82a0 |
| 4 | Ship+0x2BC slot identity | wire-format-spec.md slot map says "(unused) NULL always"; subsystem-integrity-hash.md slot 11 says "Pulse Weapon System hashing at +0x40 / +0x2BC" | Ghidra decompile of ComputeSubsystemHash 0x005b5eb0 |
| 5 | Subsystem hash table duplication | wire-format-spec.md has its own 12-row hash order table; subsystem-integrity-hash.md is the dedicated doc | Make subsystem-integrity-hash.md canonical; wire-format-spec hub keeps a 1-line summary + link |
| 6 | Per-collision PythonEvent count | pythonevent-wire-format.md says "12-14 messages: 1 ObjectExploding + 11 ADD_TO_REPAIR_LIST + 2 delayed" but worked example shows "14: 1 ObjectExploding + 13 ADD_TO_REPAIR_LIST" | Re-derive from trace |
| 7 | TGEvent base vtable slot count | pythonevent-wire-format.md = 18 slots (0-17); engine family vtable doc baseline = 14 slots; collision-effect-protocol.md TGEvent vtable = 16 slots (ends at +0x40) | Ghidra vtable boundary check at 0x00895FF4 |
| 8 | CF16 doc overlap | cf16-precision-analysis.md and cf16-explosion-encoding.md duplicate algorithm + constants + scale table + mod round-trip analysis | Merge: precision-analysis = algorithm/constants; explosion-encoding = wire-format + mod ID only |
| 9 | Per-ship subsystem catalog cross-source | per-ship-subsystem-wire-format.md and stateupdate-subsystem-wire-format.md both list subsystem types but with different inventories | Use stateupdate-subsystem-wire-format as the type catalog; per-ship as per-class catalog |
| 10 | Direction-split claim location | stateupdate.md, stateupdate-subsystem-wire-format.md, and message-trace-vs-packet-trace.md all assert the SUB-vs-WPN by direction split with the same packet counts | stateupdate.md (canonical); others link |
| 11 | Subsystem field offsets at ship+0x280 family | stateupdate-subsystem-wire-format.md says +0x280 count, +0x284 head, +0x288 tail, +0x28C free list; stateupdate.md says subsystem list at +0x284 (head only) | Ghidra decompile of Ship_AddSubsystemToLists FUN_005b3e50 |
| 12 | Opcode 0x18 wire format | game-opcodes.md says "DeletePlayerAnim, Handler FUN_006A1420, plays animation" — no wire format | New leaf doc needed (delete-player-anim-wire-format.md exists in `OpenBC/docs/wire-formats/` already; mirror it on the BC side) |
| 13 | Factory 0x866 family | delete-player-ui-wire-format.md says "0x866 = base TGEvent"; tgobjptrevent-class.md's factory-table top is 0x02 = TGEvent; the 0x8xx family is `0x8129 = ObjectExplodingEvent` | Need a factory-id catalog: 0x02 vs 0x101 / 0x105 / 0x10C / 0x866 / 0x8124 / 0x8129. Where does 0x866 live? |
| 14 | objnotfound-requestobj-enterset doc not indexed | The doc exists at `docs/protocol/objnotfound-requestobj-enterset-wire-format.md` but is not listed in `docs/protocol/README.md` (the README table has 18 docs; this is doc 19) | Add to README in v5 close batch |
| 15 | Breadcrumb header inconsistency | objnotfound-requestobj-enterset-wire-format.md lacks the `> [docs](../README.md) / [protocol](README.md) /` breadcrumb header that all siblings have | Add on re-validation |
| 16 | SpeciesToShip table duplication | game-opcodes.md (15 playable rows) and objcreate-serialization.md (45 rows) | objcreate-serialization.md canonical; game-opcodes.md keeps short list + link |
| 17 | Opcode 0x06 worked-example accuracy | pythonevent-wire-format.md's "exactly 12-14 PythonEvents per collision" — 12-14 doesn't quite match either of the example breakdowns in the same doc | Re-derive from packet trace |
| 18 | Receiver address for explosion in cf16 docs | Both cf16-precision-analysis.md and cf16-explosion-encoding.md cite Handler_Explosion_0x29 at 0x006A0080 (consistent across CF16 family); game-opcodes.md also = 0x006A0080. OK, this is consistent. (No disagreement; noted as positive cross-anchor.) |  | — |

## 5. Cross-family disagreements (engine vs protocol)

The engine campaign produced an anchor table covering 6 NI vtables, 9 TG/Ship vtables, ~30
function anchors, and 12 constant/offset anchors (engine tracker §5.1–§5.8). The protocol
family will lean on these. Cross-checks identified so far:

| # | Engine anchor | Protocol claim | Notes |
|---|---------------|----------------|-------|
| 1 | TGMessage base vtable @ 0x008958d0 (engine `nirtti-factory-catalog` and decompiled-functions infrastructure) | transport-layer.md cites the same address 0x008958d0 for TGMessage vtable. **Agreement.** | Cross-anchor verified at survey time |
| 2 | TGEvent base vtable @ 0x00895FF4 (engine event-system-architecture.md) | pythonevent-wire-format.md uses 0x00895FF4 as TGEvent base vtable; collision-effect-protocol.md uses 0x00895ff4 (lowercase). **Agreement.** | Same address |
| 3 | TGEvent slot count | Engine event-system-architecture.md baseline implies ~14 slots; protocol pythonevent-wire-format.md table lists 18 slots (0-17). **Possible disagreement.** | §4 #7. May reflect engine doc's baseline being incomplete OR pythonevent's table being inferred. v5 pass needs the boundary check. |
| 4 | TGCallback vtable @ 0x008960f4 (engine event-system-architecture.md) | No protocol doc references this; protocol docs use TGEvent + factory IDs. No conflict. | — |
| 5 | TGConditionHandler vtable @ 0x00896104 (engine) | No protocol doc references this. No conflict. | — |
| 6 | MultiplayerGame dispatcher @ 0x0069f2a0 (engine function-map.md / decompiled-functions.md) | wire-format-spec.md, game-opcodes.md, tgmessage-routing.md, transport-layer.md, set-phaser-level-protocol.md, pythonevent-wire-format.md all cite 0x0069F2A0 (or 0x0069f2a0). **Agreement.** Engine campaign #1 result documented dispatcher at this address, function-map.md row corrected. | Strong cross-anchor |
| 7 | Jump table @ 0x0069F534 (engine function-map.md) | wire-format-spec.md and game-opcodes.md both cite this with 41 entries. **Agreement.** | Strong cross-anchor |
| 8 | UtopiaModule globals (0x0097FA78 WSN, etc., engine decompiled-functions.md) | pythonevent-wire-format.md cites WSN at 0x0097FA78; collision-effect-protocol.md uses g_IsHost at 0x0097FA89; objnotfound-requestobj-enterset uses g_IsMultiplayer indirectly. **Agreement.** | Strong cross-anchor |
| 9 | TGBufferStream vtable + offsets (engine decompiled-functions.md describes constructor FUN_006cefe0; protocol stream-primitives.md gives layout) | Protocol stream-primitives.md describes +0x1C buffer, +0x20 capacity, +0x24 position, +0x28 bookmark, +0x2C bit-pack state. transport-layer.md Appendix A has slightly different offsets (mentions +0x08 and +0x0C base-class fields). **Possible disagreement.** | Resolution: protocol stream-primitives.md is the canonical layout; engine has not yet documented TGBufferStream layout — engine campaign may need a follow-up. |
| 10 | NiRTTI factory @ DAT_009a2b98 (engine) | tgmessage-routing.md cites factory table @ 0x009962d4 for transport types (256 slots). These are different tables (NiRTTI vs transport factory). No conflict. | Engine table is for NI classes; protocol table is for transport-message types — independent registries |
| 11 | Event manager @ 0x0097F838 (engine decompiled-functions.md) | pythonevent-wire-format.md cites `&DAT_0097f838` as the event-manager global for AddEvent calls in subsystem-integrity-hash.md. **Agreement.** | Strong cross-anchor |
| 12 | TG hierarchy claim: TGStreamedObject etc. (engine tg-hierarchy-vtables.md) | No direct conflict surfaced in protocol docs; protocol docs reference factory IDs (0x101 TGSubsystemEvent etc.) but don't drill into TGStreamedObject's vtable. | Indirect dependency only |
| 13 | "Two-RTTI-Systems" disclosure (engine — leaf doc pattern) | Protocol docs use factory_id (0x101, 0x105, 0x10C, 0x866, 0x8129) for events. This is the **TG RTTI** registry (not NiRTTI). Per the engine pattern, every protocol doc that introduces factory IDs should disclose which RTTI system it uses. None currently do. | Universal documentation debt across the protocol family |

The engine campaign's anchor table is the single biggest gift to the protocol campaign:
the dispatcher, jump table, base vtables, and UtopiaModule globals are all already v5-locked.
Protocol docs cite-by-reference rather than re-anchoring.

## 6. Validation log

### 6.1 wire-format-spec.md — 2026-05-28 (game-archaeology-specialist)

**Status:** validated -> `partial` (pending two corrections + frontmatter).
**Methodology:** Per-doc workflow Phases 1-3 with `program: STBC.exe` on every MCP call.
**Functions touched (completeness):**

| Function | Addr | effective_score | Used to verify |
|----------|------|-----------------|----------------|
| MpgameHandleMessage | 0x0069f2a0 | 69.84 | dispatcher + jump-table claim |
| FUN_006a1b10 (ChecksumCompleteHandler) | 0x006a1b10 | 0.00 | Settings packet wire format |
| FUN_005b5eb0 (ComputeSubsystemHash) | 0x005b5eb0 | 0.00 | 12-slot hash table + ship+0x2BC identity |
| FUN_005b5030 (Ship_LinkSubsystemToParent) | 0x005b5030 | 6.26 | weapon-type -> ship-slot mapping (ground truth) |
| FUN_005b17f0 (StateUpdate sender) | 0x005b17f0 | 0.00 | anti-cheat hash dead-code gate |

**Confirmed claims (high confidence):**
- 3 dispatchers (MultiplayerGame 0x0069F2A0, NetFile 0x006A3CD0, MultiplayerWindow 0x00504C10) — bodies exist + sizes match.
- 41-entry jump table at 0x0069F534, opcode-2 indexed — bytes verified, all 16 dispatched handlers exist, all 41 decoded paths confirmed via plate + `decompile_function`.
- 6 NetFile handlers (0x20/21/22/23/25/27) — all exist.
- 3 MultiplayerWindow handlers (0x00, 0x01, 0x16) — all exist.
- 29 event-handler registration rows (FUN_0069EFE0): 5 exist as Ghidra functions; 24 are LAB_ labels but identity proved by `decompile_function(0x0069efe0)` returning 29 `FUN_006da130(&LAB_xxxxxxxx, s_MultiplayerGame____<Name>Handler)` calls — string-name match confirms each addr->name binding.
- Anti-cheat hash DEAD-CODE-IN-MP claim — verified via FUN_005b17f0 line `bVar17 = (DAT_0097fa8a == '\0')` and `if (bVar17) WriteBit(1); ComputeSubsystemHash(...); else WriteBit(0)`.
- Subsystem catalog vtable->class mappings (lines 152-167) — vtables 0x00893794 (PulseWeapon) + 0x008936F0 (TractorBeam) confirmed by `get_xrefs_to` -> constructor bodies that install them at offset 0.
- Settings packet (opcode 0x00) globals — DAT_008e5f59, DAT_0097faa2 confirmed via `get_xrefs_to` (WRITE from MP setup paths, READ from FUN_006a1b10).
- Cross-doc references (stateupdate.md / collision-effect-protocol.md / pythonevent-wire-format.md) — spot-checked, each linked doc covers what the hub claims.

**Corrected claims:**

1. **Settings packet wire format.** Doc shows `[byte:0x008e5f59] [byte:0x0097faa2]` (and `[byte:checksumFlag]`); binary uses `WriteBit` (FUN_006cf770) for all three. Decompile of FUN_006a1b10 (Settings sender):
   ```
   WriteByte(0x00)                       opcode
   WriteFloat(*(DAT_009a09d0 + 0x90))    gameTime
   WriteBit(DAT_008e5f59)                bit-packed setting 1
   WriteBit(DAT_0097faa2)                bit-packed setting 2
   WriteByte(playerSlot)                 closes/breaks bit group
   WriteShort(strlen(mapName))
   WriteBytes(mapName, strlen)
   WriteBit(checksumFlag)                bit-packed (new group)
   if (checksumFlag) FUN_006f3f30(...)
   ```
   The doc's `[byte:...]` representation should become `[bit:...]` with a note about the bit-packing wrapper (FUN_006cf770 vs FUN_006cf730).

2. **Ship+0x2BC and ship+0x2D4 named-slot identities** (resolves cross-doc disagreement #4). The "Named Slot Layout" table:
   - **Wrong**: `+2BC (unused) NULL Always NULL` → **Correct**: `Pulse Weapon System (PulseWeaponSystem parent)`
   - **Wrong**: `+2D4 Pulse 0x00893794` → **Correct**: `Tractor (TractorBeamSystem parent at 0x008936F0)`
   - Ground truth: `decompile_function(0x005b5030)` switches on weapon-class-ID 0x802A subclasses:
     - 0x802C (PhaserBank) → reads `ship+0x2B8` (Phaser parent)
     - 0x802D (PulseWeapon) → reads `ship+0x2BC` (Pulse parent — note: 700 decimal in decompile = 0x2BC)
     - 0x802E (TractorBeamProjector) → reads `ship+0x2D4` (Tractor parent)
     - 0x802F (TorpedoTube) → reads `ship+0x2B4` (Torpedo parent)
   - **subsystem-integrity-hash.md is the correct doc** — its slot 11 "Pulse +0x40/+0x2BC" matches the binary; the hub doc's Named Slot Layout had the Pulse/Tractor slot identities swapped.

**Retired (dedup with sibling — resolves cross-doc disagreement #5):**
- The "Anti-Cheat Hash Field Offsets" table (lines 188-208) should be retired in favor of subsystem-integrity-hash.md's identical table. Wire-format-spec.md keeps a one-line summary linking to subsystem-integrity-hash.md as canonical.

**Body restructure suggested:**
- Tag verified anchor rows with `[v5-validated 2026-05-28]`.
- Move "Validated by JMP detour trace 2026-02-10" body provenance into v5 YAML frontmatter under `cross_source` tag.
- Update Settings Packet section: replace `[byte:DAT_008e5f59]` syntax with `[bit:DAT_008e5f59]` and explain the bit-pack wrapper.
- Update Named Slot Layout: swap +0x2BC and +0x2D4 row contents per the FUN_005b5030 switch.
- Retire the Anti-Cheat Hash Field Offsets table → 1-line "See subsystem-integrity-hash.md for the full hash-order table".

**Companion follow-ups:**
- subsystem-integrity-hash.md row 11 (already correct) — flag as the canonical authority once v5-validated in its own pass.
- stream-primitives.md — drift #1 from protocol-snapshot already covers the WriteBit / WriteByte distinction; that's where the bit-packing wrapper class needs full docs.
- CLAUDE.md "TopWindow ptr at 0x0097e238" — out-of-scope for this row (hub doc does not cite that global), but pending for ui/engine drift sweep.

**Open questions left for downstream rows:**
- ship+0x2DC = "unused NULL Always NULL" in the doc — not verified this pass. `FUN_005b5030` only handles 4 weapon classes (0x802C/D/E/F); could be another mis-identification. Worth checking when per-ship-subsystem-wire-format.md validates.
- **Factory ID 0x866** (used by opcode 0x17 DeletePlayerUI) is not in the engine factory catalog (0x02 / 0x101 / 0x105 / 0x10C / 0x8124 / 0x8129). Flagged in §4 #13; resolution belongs to the delete-player-ui-wire-format.md row. Hub doc continues to cite 0x866 with a NOTE pointing readers to the open question.
- **9 of 13 Named Slot Layout rows remain un-ground-truthed.** Only 4 of the 13 slot rows (+0x2B4/+0x2B8/+0x2BC/+0x2D4 — the weapon parents) are anchored by the FUN_005b5030 switch decompile. The remaining 9 rows (Powered, Repair, Power, Cloak, LifeSupport, SensorArray, WarpDrive, +0x2DC unused, ShipRef) inherit from the older JMP detour trace and have not been re-anchored to vtable installer xrefs this pass. Picking these up is a per-ship-subsystem-wire-format.md (row #12) task — the per-ship doc traces every slot to its vtable installer for each species.

**Files touched:** docs/protocol/wire-format-spec.md (re-rendered with v5 frontmatter, NOTE block, body corrections, retired hash table, cross-link section), docs/protocol/v5-validation-status.md (this row updated; §2 row #1 status flipped to partial).

### 6.2 stream-primitives.md — 2026-05-28 (game-archaeology-specialist)

**Status:** validated -> `partial` (pending one CV3-wire-format correction + body restructure for the two-class disambiguation).
**Methodology:** Per-doc workflow Phases 1-3 with `program: STBC.exe` on every MCP call.

**Headline:** the doc was CORRECT all along about TGBufferStream's identity, field layout, primitive addresses, and bit-pack format. The "two-class confusion" flagged in protocol-snapshot drift finding #1 is resolved in the OPPOSITE direction from what the snapshot suggested: the 0x30-byte class at 0x006CEFE0 / vtable 0x00895C58 IS the SWIG-visible TGBufferStream. My prior memory `tgbufferstream-vtable-20260528.md` mis-labeled the 0x40-byte class at 0x006B82A0 (vtable 0x008958D0) as TGBufferStream — that class is actually the OUTER wire-container (likely TGStreamedObject / TGSerialized), distinct from the SWIG primitive class.

**Class-identity adjudication:**

| Class | Ctor | Sizeof | Vtable | Role | Identity |
|-------|------|--------|--------|------|----------|
| A | 0x006CEFE0 | 0x30 | 0x00895C58 | Typed-primitive cursor over external buffer; SWIG-visible | **TGBufferStream** (SWIG verified via `new_TGBufferStream` at 0x005C22A0) |
| B | 0x006B82A0 | 0x40 | 0x008958D0 | Wire-message envelope; owns buffer; vtable[0] returns 0x32 (class tag, first byte on wire) | **TGMessage** (SWIG verified via `new_TGMessage` at 0x005E12E0 — identified 2026-05-28; corrects prior "NOT TGBufferStream — open Q" note) |

Class-A identity proven by SWIG `new_TGBufferStream` wrapper at 0x005C22A0 (function created this session): `PUSH 0x30; CALL alloc; MOV ECX,EAX; CALL 0x006CEFE0`. The 0x30-byte allocation and the FUN_006CEFE0 ctor target are decisive.

Class-A field layout proven by every primitive decompile (uses +0x1C buf, +0x20 cap, +0x24 cursor, +0x28 bookmark, +0x2C bit-mask consistently).

The handler pattern (CollisionEffectHandler at 0x006A2470 was the smoking gun):
```
pBuf = TGBufferStream_GetBufferAndSize(pStream_classB, &len)
FUN_006CEFE0()                      // construct stack-local class A
FUN_006CF180(pBuf+1, len-1)         // OpenBuffer on class A — skip opcode byte
... use class-A primitives to extract typed payload ...
FUN_006CF120()                      // destruct stack-local class A
```
So class A is the per-handler scratch cursor over class B's wire buffer.

**Functions touched (completeness):**

| Function | Addr | effective_score | Used to verify |
|----------|------|-----------------|----------------|
| TGBufferStream_swig_WriteBool_Bit (WriteBit) | 0x006CF770 | 68.1 | bit-pack format + state-machine semantics |
| TGBufferStream_swig_ReadBool_Bit (ReadBit) | 0x006CF580 | n/a | bit-pack reader symmetry |
| TGBufferStream_swig_Ctor | 0x006CEFE0 | 45.1 | class-A identity, vtable installer, field zeroing |
| CompressedFloat16_Encode | 0x006D3A90 | 52.6 | CF16 encoder algorithm + 5 constants |
| CompressedFloat16_Decode | 0x006D3B30 | 49.1 | CF16 decoder algorithm + 1/4095 multiplier |
| CompressedVector3_ReadVirtual | 0x006D2EB0 | n/a | CV3 wire-format (3 bytes only, not 5) |
| CompressedVector4_ReadVirtual | 0x006D2FD0 | n/a | CV4 wire-format (3 bytes + u16 OR float) |
| FUN_006D2C60 (CV3 decompress callback) | 0x006D2C60 | n/a (created this session) | 3-byte direction unpack to floats |
| FUN_005C22A0 (SWIG new_TGBufferStream) | 0x005C22A0 | n/a (created this session) | class-A 0x30 sizeof proof |

**Confirmed claims (high confidence):**

- All 14 primitive addresses match the doc exactly (WriteByte/Bit/Short/Int/Float/Bytes/GetPos + ReadByte/Bit/Short/Int/Float/Bytes + Read32v). Doc was 100% accurate.
- Field layout +0x1C pBuffer / +0x20 uCapacity / +0x24 uCursor / +0x28 uBitBookmark / +0x2C bBitMask — CONFIRMED via decompile of WriteBit, WriteChar, OpenBuffer, ReadByte (each primitive consistently reads/writes these offsets).
- Bit-pack wire layout `[count:3][bits:5]` — CONFIRMED.
- Count stored as ACTUAL count (1..5), NOT count-1. (Doc was right; my prior reading was wrong.)
- Bit mask in +0x2C walks 1, 2, 4, 8, 16 as a SINGLE walking bit; resets to 0 when count > 4 (i.e., after writing 5th bit) so next call allocates a new accumulator byte.
- CF16 encoder algorithm: sign + 3-bit scale + 12-bit mantissa, log scale base 0.001 mult 10.0, mantissa = ftol((value-lo)/(hi-lo)*4095.0).
- CF16 decoder algorithm: range = (hi-lo)*mantissa*(1/4095) + lo.
- All 4 CF16 constants verified in .rdata: BASE=0.001 at DAT_00888B4C, MULT=10.0 at DAT_0088C548, ENC_SCALE=4095.0 at DAT_00895F50, DEC_SCALE=1/4095 at DAT_00895F54. (Plus DAT_00888B54 = small float used as sign-check epsilon.)
- CV3 reader at 0x006D2EB0 calls vtable[0x50] 3 times then vtable[0xB8] to decompress — confirms vtable-virtual reader pattern shared across 3 different stream-reader vtables (0x00895CD0, 0x00895DD8, 0x00895ED0 per snapshot).
- TGBufferStream vtable slot 20 (offset 0x50) IS ReadByte for class A (FUN_006CF540 — verified). Same slot also installs the doc's claim of "vtable+0x50 = ReadByte".
- OpenBuffer at 0x006CF180 attaches an external buffer (sets +0x1C/+0x20, resets +0x24/+0x28/+0x2C). New function naming this pass: TGBufferStream_swig_OpenBuffer.

**Corrected claims:**

1. **CV3 wire format is 3 bytes (direction-only), NOT 5 bytes (`[dirX:u8][dirY:u8][dirZ:u8][magnitude:u16]`).**
   - Doc line 124: "Wire format: `[dirX:u8][dirY:u8][dirZ:u8][magnitude:u16]` = **5 bytes total**"
   - Reality: CV3_ReadVirtual (FUN_006D2EB0) only calls vtable[0x50] (ReadByte) 3 times, then vtable[0xB8] (FUN_006D2C60 = direction unpack to 3 floats). NO magnitude is read; NO uint16 appears in the read path.
   - CV4 (FUN_006D2FD0) IS the type with the magnitude: 3 bytes + (u16 if param5 set, else f32). CV4_Write similarly.
   - CV3_Write (FUN_006D2AD0) does produce a CF16 magnitude as a 4th output, but that's a UTILITY return — callers choose whether/how to write it. The wire CV3 read primitive consumes only 3 bytes.
   - Possible explanation: doc author may have conflated CV3 with CV4, or assumed symmetry that doesn't exist in the binary. CV3 is direction-only on the wire.

2. **Class identity note: the doc is right that TGBufferStream owns these primitives, but the doc is silent about the existence of the 0x40-byte wire-container class that ALSO has a vtable+Serialize/Clone surface and is what the dispatcher receives.** Recommend the doc add a "Class context" preamble explaining that TGBufferStream is the typed-cursor class, separate from the wire-container class that gets deserialized off the wire and that the dispatcher gates on `vtable[0]() == 0x32`.

3. **Doc says "+0x2C bit-packing state (0 = no active bit group)" which is correct but cryptic.** The field is a SINGLE walking bit mask (1, 2, 4, 8, 16, or 0), not a count. Recommend renaming the offset description to "+0x2C bit-write mask (walking 1→2→4→8→16; 0 = need new accumulator byte)" for clarity.

**Dropped claims:**

None — every doc claim survived in some form.

**Retired (no opportunities this pass):**

The doc has minimal redundancy with siblings (CF16 details are in cf16-precision-analysis.md but cross-linked, not duplicated).

**Body restructure suggested:**

1. Add v5 YAML frontmatter (validated 2026-05-28, methodology FUNCTION_DOC_WORKFLOW_V5, status partial, companions).
2. Add a "Class identity" preamble: TGBufferStream is the SWIG-visible 0x30-byte typed-cursor class; a separate 0x40-byte wire-container class also exists in the binary (cited as open question) and the two are sometimes conflated in older docs.
3. Tag each table row with `[v5-validated 2026-05-28]` plus the new Ghidra name (`TGBufferStream_swig_WriteChar` etc.).
4. Update CV3 wire format: 3 bytes only (direction); remove the `+u16 magnitude` claim. Add an explicit warning that CV3 and CV4 are NOT symmetric.
5. Clarify bit-pack state field as a walking single-bit mask, not a count.
6. Add cross-link to docs/protocol/wire-format-spec.md (which uses these primitives for opcode 0x00 Settings packet's 3 WriteBit calls) and to docs/protocol/transport-layer.md.

**Companion follow-ups:**

- ~~The 0x40-byte class at 0x006B82A0 / vtable 0x008958D0 needs its true identity recovered.~~ **RESOLVED 2026-05-28: TGMessage** (base class of TGMessage hierarchy). SWIG `new_TGMessage` wrapper at 0x005E12E0 allocates exactly 0x40 bytes and calls FUN_006B82A0 as ctor. 95 SWIG `TGMessage_*` method strings at 0x0092A098 cross-confirm. Derived classes (TGConnectMessage, TGAckMessage size 0x44, TGBootPlayerMessage size 0x44, TGDisconnectMessage, TGDoNothingMessage, TGNameChangeMessage) all call this base ctor. Ghidra DB renamed: FUN_006B82A0 → TGMessage_Ctor (v5 plate comment installed).
- Cascade corrections applied in same commit: docs/engine/rtti-class-catalog.md (TGBufferStream row rewritten with 0x00895C58 vtable; TGMessage row rewritten with 0x008958D0 vtable), docs/engine/tg-hierarchy-vtables.md (Sibling TG vtables section updated with both classes), docs/engine/v5-validation-status.md (foundation #2 corrigenda added). docs/protocol/transport-layer.md still TBD — its own validation pass will pick up the TGMessage naming directly.
- CV3 wire-format correction should propagate to docs/protocol/stateupdate.md if it cites CV3 for position fields, and to cf16-precision-analysis.md if it cites CV3 examples.
- DAT_00888B54 (small-float sign-check epsilon) should be added to the protocol-snapshot CF16 constants section.

**Open questions left for downstream rows:**

- What is the inner status struct allocated by FUN_006D1FC0 (base ctor of class A)? It's 0x14 bytes. Status codes seen: 0xFFFFFFFB (write overflow), 0xFFFFFFFC (read overflow), 0xFFFFFFFD (already attached). Probably a Status/IOResult tracker. Deferred.
- Why does CV3_Write produce a uint16 magnitude that the reader doesn't consume? Maybe there's a separate caller-driven write+read pattern. Deferred — does not affect the doc's correctness once the wire-format claim is corrected.
- What are slots 1-19 of class-A vtable (0x00895C58)? Only slot 20 (ReadByte) verified directly this session; other slots inferred from SWIG bindings. Full vtable mapping deferred.
- The 0x40-byte class's true identity (open Q for the entire protocol family).

**Annotations applied this session:**

16 functions renamed `TGBufferStream_swig_*` (Ctor, Dtor, OpenBuffer, WriteChar/Bit/Short/Int/Float/Bytes, ReadChar/Bit/Short/Int/Float/Bytes/IntVirtual, GetPos). 5 functions renamed `CompressedFloat16_Encode/Decode` and `CompressedVector3_Write/ReadVirtual + CompressedVector4_WriteVirtual/ReadVirtual`. All 16 also got typed __thiscall prototypes. 5 plate comments applied (WriteBit, ReadBit, Ctor, CF16 Encode, CF16 Decode). 2 functions newly CREATED via `mcp__ghidra__create_function`: SWIG new_TGBufferStream at 0x005C22A0 and CV3 decompress callback at 0x006D2C60.

**Files touched:** docs/protocol/v5-validation-status.md (this row added; §2 row #2 status flipped to partial). docs/protocol/stream-primitives.md NOT modified this pass — the documentation-writer agent will re-render with the corrections+restructure listed above.

### 6.3 transport-layer.md — 2026-05-28 (game-archaeology-specialist)

**Status:** validated -> `partial` (4 corrections applied; 3 open questions remain).
**Methodology:** Per-doc workflow Phases 1-3 with `program: STBC.exe` on every MCP call.

**Headline:** the AlbyRules cipher transform is **fully located** for the first time
(`AlbyRulesCipher_InitKey` at `0x006c2280`, `AlbyRulesCipher_Encrypt` at `0x006c2490`,
`AlbyRulesCipher_Decrypt` at `0x006c2520`, vtable `0x008958c0`, `0x58`-byte state). Both
Encrypt and Decrypt call `InitKey` on every packet — the cipher is **re-keyed per packet**,
which is why it's robust to UDP packet loss. The two TGWinsockNetwork functions
`SendPacket` (`0x006b9870`) and `ReceivePacket` (`0x006b95f0`) had to be **created** via
`mcp__ghidra__create_function` because auto-analysis had not disassembled them (vtable[27]
and vtable[28] of the TGWinsockNetwork base class — no direct CALL xrefs, same hidden-DATA
pattern as `MpgameHandleMessage`).

**Functions touched (completeness):**

| Function | Addr | Role | Plate? |
|----------|------|------|--------|
| `TGWinsockNetwork_Ctor` | 0x006b3a00 | MTU 1024 (network+0xAC, +0x2B); cipher state alloc; initial conn state 4 | — |
| `TGWinsockNetwork_HostOrJoin` | 0x006b3ec0 | Connection states 4 -> 2 (host) / 4 -> 3 (join) | — |
| `TGWinsockNetwork_QueueMessageForPeer` | 0x006b5080 | Seq counter offsets peer+0x26 / +0x2A | — |
| `TGWinsockNetwork_SendOutgoingPackets` | 0x006b55b0 | MTU-bounded pack buffer | — |
| `TGWinsockNetwork_ProcessIncomingPackets` | 0x006b5c90 | Packet structure peer_id / msg_count; factory dispatch | — |
| `TGWinsockNetwork_HandleReliableReceived` | 0x006b61e0 | Below32 SET site | yes |
| `TGWinsockNetwork_HandleACK` | 0x006b64d0 | Below32 READ site | — |
| `TGWinsockNetwork_EnqueueReceived` | 0x006b6ad0 | Seq window + reassemble dispatch | — |
| `TGMessage_ReassembleFragments` | 0x006b6cc0 | 256-entry index; fragment 0 carries total_frags | — |
| `TGMessage_Ctor` | 0x006b82a0 | Size 0x40; vtable 0x008958d0 (was existing — name confirmed) | — |
| `TGMessage_Factory_Type32` | 0x006b83f0 | Type 0x32 deserialize | — |
| `FragmentMessage` | 0x006b8720 | Vtable[7] splitter — open question on total_frags placement | — |
| `TGWinsockNetwork_ReceivePacket` | 0x006b95f0 | Decrypt; GameSpy bypass at 0x006b9706 | yes |
| `TGWinsockNetwork_SendPacket` | 0x006b9870 | Encrypt; self-send loop-back path | yes |
| `TGBootMessage_Ctor` | 0x006bac70 | Type 0x04 | — |
| `TGDataMessage_Ctor` | 0x006bc5b0 | Type 0x00 | — |
| `TGHeaderMessage_Ctor` | 0x006bd120 | Type 0x01 ACK; size 0x44 | — |
| `TGHeaderMessage_Serialize` | 0x006bd190 | 4 or 5 byte ACK wire format | yes |
| `TGConnectMessage_Ctor` | 0x006bdc40 | Type 0x02 | — |
| `TGConnectAckMessage_Ctor` | 0x006be730 | Type 0x03 | — |
| `TGDisconnectMessage_Ctor` | 0x006bf2e0 | Type 0x05 | — |
| `AlbyRulesCipher_InitKey` | 0x006c2280 | Key 'AlbyRules!' @ 0x0095abb4 -> 0x58-byte state | yes |
| `AlbyRulesCipher_Encrypt` | 0x006c2490 | Vtable[1]; called per packet; re-keys via InitKey | yes |
| `AlbyRulesCipher_Decrypt` | 0x006c2520 | Vtable[2]; called per packet; re-keys via InitKey | yes |

7 v5 plate comments installed; 2 functions newly created
(`TGWinsockNetwork_SendPacket`, `TGWinsockNetwork_ReceivePacket`).

**Confirmed claims (high confidence):** 23 anchors. Packet structure (peer_id / msg_count /
factory dispatch via `DAT_009962d4`); all 7 transport-type factory registrations; TGMessage
envelope layout (`+0x14` seq, `+0x38` total_frags, `+0x39` frag_idx, `+0x3A` reliable,
`+0x3B` ordered, `+0x3C` is_fragment, `+0x40` below32); TGMessage base vtable 8 slots;
TGHeaderMessage ACK subclass (size `0x44`, 4-or-5-byte wire format with flag bits
`is_fragment` and `is_below_0x32`); 256-entry fragment reassembly; MTU `1024` (network+0xAC
+ network+0x2B); below32 ACK three-site agreement (SET / READ / WIRE); AlbyRules cipher
location + algorithm + vtable + re-key-per-packet; GameSpy bypass (`*buf != '\\'`); cipher
applied to `buf+1` with `len-1`; self-send loop-back path; three C++ dispatchers (NetFile,
MpgameHandleMessage, MultiplayerWindow) confirmed including the `this+0xB0 != 0` gate.

**Corrected claims:**

1. **C1 — Sequence counter offsets (load-bearing).** Doc said `peer + 0x98` (types `< 0x32`)
   and `peer + 0xA8` (types `>= 0x32`). Direct decompile of
   `TGWinsockNetwork_QueueMessageForPeer` (`0x006b5080`) shows:
   - `peer + 0x26` (16-bit) for types `< 0x32`
   - `peer + 0x2A` (16-bit) for types `>= 0x32`
   - Receive-side window check uses `peer + 0x24` and `peer + 0x28`.

   The prior `+0xA8` likely came from confusing `network + 0xA8 = 0x8000` (a constant set in
   the ctor — probably a seq-window threshold or max-seq, NOT a per-peer seq counter).

2. **C2 — NetFile dispatcher opcodes (correct catalog).** Doc said "0x20-0x27 contiguous".
   Actual cases in `FUN_006A3CD0` switch are `0x20`, `0x21`, `0x22`, `0x23`, `0x25`, `0x27`
   — 0x24 and 0x26 have **no handler**. Range is correct as bounds but not contiguous. Body
   updated to cross-link to `docs/protocol/checksum-opcodes.md` as the canonical opcode map.

3. **C3 — Appendix A "TGBufferStream Layout" replacement (cascade from foundation #2).**
   The prior Appendix A described the SWIG `TGBufferStream` class (`0x30`-byte cursor at
   `FUN_006CEFE0` / vtable `0x00895C58`), not the wire envelope. Appendix A is now retired
   in favour of a one-paragraph cross-link to `stream-primitives.md` plus a note explaining
   that the bit-packing primitive class shares `+0x1C` / `+0x20` / `+0x24` conventions with
   TGMessage but has an independent buffer.

4. **C4 — TGMessage naming throughout the doc.** The validation of stream-primitives.md
   (§6.2) resolved the long-standing "0x40-byte wire-container class" open question:
   that class is `TGMessage`. Anywhere the doc previously said "TGBufferStream" referring
   to the wire envelope is now `TGMessage`. The canonical anchor row is now: vtable
   `0x008958d0`, ctor `TGMessage_Ctor` at `0x006b82a0`, size `0x40`. SWIG `new_TGMessage`
   wrapper at `0x005e12e0` confirms class identity (allocates `0x40`, calls
   `TGMessage_Ctor`).

**Dropped claims:** None.

**New factual sections added:**

- **Top-of-doc NOTE block** stating partial status and listing the 4 corrections and 2 open
  questions.
- **MTU promoted to the introduction** with explicit citation (`network+0xAC` and `+0x2B`,
  both `0x400 = 1024`, set in ctor `0x006b3a00`). Previously implicit.
- **"Cipher object" subsection** under Encryption: vtable `0x008958c0`, `0x58`-byte state,
  re-key-per-packet property, cipher applied to `buf+1` with `len-1`, GameSpy `\\` first-
  byte bypass at `0x006b9706`, send-side call at `0x006b98e0`, receive-side call at
  `0x006b970e`. Cross-link to `docs/networking/alby-rules-cipher-analysis.md`.
- **"Self-send Loop-back" subsection** under Send Path: local queue at `network+0x33C`
  / `+0x340`, toggle at `network+0x344`, branch at `0x006b9870` `if (param_2 ==
  *(int *)(param_1 + 0x1c))`.
- **Connection state machine** subsection: states 2 (HOSTING), 3 (JOINING), 4 (IDLE / READY)
  documented; state 1 marked as open question.
- **`+0x40` below32 field** added to the TGMessage object-layout table (most prior versions
  missed this field).
- **Cross-doc reconciliation** subsection near doc bottom: three deferred companion-doc
  follow-ups (alby-rules-cipher-analysis.md, network-protocol.md, checksum-opcodes.md).

**Companion follow-ups (deferred to those docs' own validation passes):**

- `docs/networking/alby-rules-cipher-analysis.md` — absorb cipher addresses (`0x006c2280`,
  `0x006c2490`, `0x006c2520`, vtable `0x008958c0`, `0x58`-byte state) + re-key-per-packet
  property.
- `docs/networking/network-protocol.md` — re-anchor any peer-offset claims that cited
  `+0x98` / `+0xA8` to `+0x26` / `+0x2A`.
- `docs/protocol/checksum-opcodes.md` — canonical for NetFile non-contiguous opcode list
  (`0x20`, `0x21`, `0x22`, `0x23`, `0x25`, `0x27`); this doc just cross-links.

**Open questions left for downstream rows:**

1. **`FragmentMessage` total_fragments placement** (medium confidence). The cleaned
   decompile of `0x006b8720` is ambiguous about whether the post-loop write
   `*(undefined1 *)(*piVar8 + 0x38) = (undefined1)iStack_38` targets Fragment 0 or the
   last clone. The deserializer-side read is unambiguous (`aiStack_400[0]+0x38`), and
   working packet traces confirm reassembly succeeds, so the sender code MUST put it on
   whatever clone has `+0x39 == 0`. Resolution: emulate `FragmentMessage` with a synthetic
   3-fragment input.

2. **Connection state 1.** Doc claims states 1, 2, 3, 4. Only 2, 3, 4 verified directly in
   `HostOrJoin`. State 1 may be a sub-state during connect handshake; needs investigation
   of the `006B8B30` family (TGConnectMessage send-side helpers).

3. **TGMessage vtable slots 3 and 4** (`0x006b9440` returns 0; `0x006b9450` unknown). Likely
   Save/Load or GetAge/IsExpired given surrounding retry-state context. Not investigated.

4. **NetFile event registration at `0x60001`.** The dispatcher posts event `0x60002` from
   inside (visible in case 0x25 handler). The `0x60001` registration site is not anchored
   here; needs `RegisterHandler` call-site cross-check.

5. **MTU divergence.** `network+0x2B` (pack buffer) and `network+0xAC` (recv buffer) both
   init to `0x400` in the ctor. Are they ALWAYS equal, or could they diverge under runtime
   config? Could affect fragmentation thresholds.

**Files touched:** docs/protocol/transport-layer.md (re-rendered with v5 frontmatter,
top-of-doc NOTE block, body corrections, retired Appendix A, new Cipher Object subsection,
new Self-send Loop-back subsection, new Connection State Machine subsection, Cross-doc
reconciliation table, Open Questions list). docs/protocol/v5-validation-status.md (this
row added; §2 row #3 status flipped to partial).

### 6.4 game-opcodes.md — 2026-05-28 (game-archaeology-specialist)

**Status:** validated -> `partial` (1 column-header clarification + 4 cross-reference
restructure suggestions; no binary corrections needed — the doc is exceptionally well
anchored already).

**Methodology:** Per-doc workflow Phases 1-3 with `program: STBC.exe` on every MCP call.
Heavy cross-anchoring against the dispatcher-recovery work captured in the engine campaign
+ this archaeology specialist's `dispatcher-recovery-20260528.md` memory.

**Headline:** game-opcodes.md was already at near-v5-quality before this pass. The 41-entry
jump table is verified byte-by-byte; every handler address survives spot-check; every event
ID PUSHed by the generic-event-forward thunks matches what the doc claims is on the wire;
all 25 active opcodes route to the addresses the doc states. The single clarification
needed is on a table column header that conflates **dispatcher PUSH overrides** with
**wire-payload event codes** — both are correct, but the column "Recv Event Code" doesn't
disclose which is which.

**Functions touched (completeness):**

| Function | Addr | effective_score | Used to verify |
|----------|------|-----------------|----------------|
| MpgameHandleMessage | 0x0069f2a0 | 69.84 | dispatcher + 41-entry jump table + per-opcode case bodies |
| FUN_0069FDA0 (GenericEventForward) | 0x0069fda0 | n/a | event-code override semantics (param_2 != 0 ? override : keep stream value) |
| FUN_006A01E0 (DestroyObjectHandler) | 0x006a01e0 | n/a | wire format opcode + i32v + owner-branch verified |
| FUN_0069F880 (PythonEventHandler) | 0x0069f880 | n/a | TGEvent factory chain + ResolveRefs + posting |
| CollisionEffectHandler | 0x006a2470 | n/a | event-code re-post 0x008000FC + distance-gap check |
| FUN_006A0080 (ExplosionHandler) | 0x006a0080 | n/a | wire format opcode + i32v + CV4 + 2x CF16 (radius then damage) |
| FUN_006A1360 (DeletePlayerUIHandler) | 0x006a1360 | n/a | TGEvent factory chain + FUN_006D62B0 with this |
| FUN_0069FF50 (StateUpdateHandler) | 0x0069ff50 | n/a | exists (84-byte body); deep wire format deferred to stateupdate.md row #8 |

No annotations were applied this pass — the dispatcher and all handler addresses already
carried their final v5 names from the engine-campaign dispatcher recovery (memory:
`.claude/agent-memory/game-archaeology-specialist/dispatcher-recovery-20260528.md`).

**Confirmed claims (high confidence):**

- **Dispatcher + jump table:** MultiplayerGame ReceiveMessageHandler at `0x0069f2a0` with
  41-entry jump table at `0x0069F534`, opcodes 0x02-0x2A — bytes decoded directly:
  ```
  index opcode  thunk_addr   role
   00   0x02   0x0069f31e   ObjCreate          -> FUN_0069f620(stream, 0)
   01   0x03   0x0069f334   ObjCreateTeam      -> FUN_0069f620(stream, 1)
   02   0x04   0x0069f525   DEFAULT (dead)
   03   0x05   0x0069f525   DEFAULT (dead)
   04   0x06   0x0069f3f1   PythonEvent        -> FUN_0069f880
   05   0x07   0x0069f34a   StartFiring        -> FUN_0069fda0(stream, 0x008000D7)
   06   0x08   0x0069f363   StopFiring         -> FUN_0069fda0(stream, 0x008000D9)
   07   0x09   0x0069f37c   StopFiringAtTarget -> FUN_0069fda0(stream, 0x008000DB)
   08   0x0A   0x0069f395   SubsysStatus       -> FUN_0069fda0(stream, 0x0080006C)
   09   0x0B   0x0069f3ae   AddToRepairList    -> FUN_0069fda0(stream, 0x008000DF)
   0A   0x0C   0x0069f3c7   ClientEvent        -> FUN_0069fda0(stream, 0)            (shared)
   0B   0x0D   0x0069f3f1   PythonEvent2       -> FUN_0069f880                       (shared)
   0C   0x0E   0x0069f405   StartCloak         -> FUN_0069fda0(stream, 0x008000E3)
   0D   0x0F   0x0069f41e   StopCloak          -> FUN_0069fda0(stream, 0x008000E5)
   0E   0x10   0x0069f437   StartWarp          -> FUN_0069fda0(stream, 0x008000ED)
   0F   0x11   0x0069f3c7   RepairListPriority -> FUN_0069fda0(stream, 0)            (shared)
   10   0x12   0x0069f3c7   SetPhaserLevel     -> FUN_0069fda0(stream, 0)            (shared)
   11   0x13   0x0069f2f6   HostMsg            -> HostMsgHandler @ 0x006A01B0
   12   0x14   0x0069f47d   DestroyObject      -> FUN_006A01E0
   13   0x15   0x0069f491   CollisionEffect    -> CollisionEffectHandler @ 0x006A2470
   14   0x16   0x0069f525   DEFAULT (routes via MultiplayerWindow dispatcher)
   15   0x17   0x0069f4a5   DeletePlayerUI     -> FUN_006A1360
   16   0x18   0x0069f4b9   DeletePlayerAnim   -> FUN_006A1420
   17   0x19   0x0069f4cd   TorpedoFire        -> FUN_0069F930
   18   0x1A   0x0069f4e1   BeamFire           -> FUN_0069FBB0
   19   0x1B   0x0069f450   TorpTypeChange     -> FUN_0069fda0(stream, 0x008000FD)
   1A   0x1C   0x0069f3dd   StateUpdate        -> FUN_0069FF50
   1B   0x1D   0x0069f4f5   ObjNotFound        -> FUN_006A0490
   1C   0x1E   0x0069f51d   RequestObj         -> FUN_006A02A0
   1D   0x1F   0x0069f509   EnterSet           -> FUN_006A05E0
   1E   0x20   0x0069f525   DEFAULT (NetFile dispatcher owns 0x20)
   1F   0x21   0x0069f525   DEFAULT
   20   0x22   0x0069f525   DEFAULT
   21   0x23   0x0069f525   DEFAULT
   22   0x24   0x0069f525   DEFAULT
   23   0x25   0x0069f525   DEFAULT
   24   0x26   0x0069f525   DEFAULT
   25   0x27   0x0069f525   DEFAULT
   26   0x28   0x0069f525   DEFAULT
   27   0x29   0x0069f469   Explosion          -> FUN_006A0080
   28   0x2A   0x0069f30a   NewPlayerInGame    -> NewPlayerInGameHandler @ 0x006A1E70
  ```
- **Generic event-forward override semantics:** confirmed by direct decompile of
  `FUN_0069FDA0` line `if (param_2 != 0) puVar7[4] = param_2;`. When the dispatcher
  PUSHes a non-zero event-ID (opcodes 0x07/0x08/0x09/0x0A/0x0B/0x0E/0x0F/0x10/0x1B),
  that constant **overrides** the event code that came in on the wire. When the
  dispatcher PUSHes 0 (opcodes 0x0C/0x11/0x12), the wire's event code is kept verbatim.
  This is exactly the asymmetry the doc's footer documents (line 148: *"0x12 uses the
  same code 0x008000E0 on both sides (no pairing, no override)"*).
- **Dead opcodes 0x04 and 0x05:** confirmed dead — jump table entries 2 and 3 (`0069f525`)
  point to the same default cleanup as 0x16/0x20-0x28, and no `case '\x04':` or `case
  '\x05':` exists in the dispatcher body.
- **Opcode 0x16 routing:** confirmed — jump table index 0x14 (=0x16-2) is the default-
  cleanup address `0x0069F525`; the opcode is handled by `MultiplayerWindow` dispatcher
  `FUN_00504C10` per the wire-format-spec hub.
- **DestroyObject (0x14) wire format:** confirmed `[u8 opcode][i32v object_id]` —
  decompile of `FUN_006A01E0` shows `OpenBuffer(buf+1, len-1)` (skips opcode) then
  `ReadIntVirtual()` (i32v); branches on `puVar3[8] == 0` (owner field at +0x20) to
  cleanup vs `owner->vtable[0x5C](object_id)`.
- **PythonEvent (0x06 / 0x0D) handler shape:** confirmed — both opcodes share
  `FUN_0069F880`. Body skips opcode byte, instantiates TGEvent via `FUN_006D6200` factory,
  resolves refs via `FUN_006F13C0`, zeroes `puVar2[9]` (the "preserve" field), and posts
  via `FUN_006DA300`.
- **CollisionEffect (0x15) re-post event code:** confirmed `0x008000FC`
  (`ET_HOST_OBJECT_COLLISION`) via direct read of
  `piVar9[4] = (int)&DAT_008000fc;` at the end of the handler. Doc's claim about
  the event-type transformation 0x00800050 -> 0x008000FC is anchored.
- **CollisionEffect (0x15) distance gate:** confirmed — handler reads
  `_DAT_008955c8` and compares `(distance - radius1 - radius2)`; rejects if the gap is
  >= threshold. Anchors the collision-effect-protocol's distance-gap claim.
- **Explosion (0x29) wire field order:** confirmed — receiver reads `ReadIntVirtual()`
  (object_id), `CompressedVector4_ReadVirtual(..., 1)` (impact_pos with CF16 magnitude),
  then `ReadShort` -> `CompressedFloat16_Decode` -> `fStack_50`, then `ReadShort` ->
  `CompressedFloat16_Decode` -> `fStack_54`. Calls `FUN_004BBDE0(&pos, fStack_50,
  fStack_54)`. Doc's claim "radius written first, damage second" survives if the
  receiver's first CF16 read is radius and the constructor signature is `(pos, radius,
  damage)`. This pairs cleanly with the cf16-explosion-encoding.md doc's anchor on
  `FUN_00595C60` (sender) writing radius from `source+0x14` first.
- **StateUpdate (0x1C):** handler exists at `0x0069FF50` (body 0x0069FF50-0x0069FFEB,
  84 bytes — small wrapper that delegates to StateUpdate machinery). This was previously
  missing from CLAUDE.md's opcode table; campaign-close action will add it.

**Corrected claims:**

1. **C1 — "Recv Event Code" column header is ambiguous (clarification, not a binary
   correction).** The doc's table at lines 131-144 has a column "Recv Event Code" with
   values `0x008000D7`, `0x008000D9`, ..., `0x00800076`, `0x008000E0`. Two of those
   entries (`0x00800076` for 0x11 RepairListPriority and `0x008000E0` for 0x12
   SetPhaserLevel) are NOT what the dispatcher PUSHes — those thunks PUSH 0, falling
   through to keep whatever event code the wire payload carried. The values in the doc
   ARE correct as "event code carried on the wire and ultimately seen by the Python
   receive handler", but they are NOT "event code injected by the dispatcher". The
   doc's own footer (line 148) explains this asymmetry, but the column header doesn't
   reflect it. Recommend:
   - Rename column to "Effective Event Code (post-receive)" OR add an explicit
     "(override)" / "(from stream)" marker per row.
   - The 8 rows where the dispatcher PUSHes a non-zero constant are: 0x07, 0x08, 0x09,
     0x0A, 0x0B, 0x0E, 0x0F, 0x10, 0x1B (9 actually) — these are the rows where the
     event code is forced by the dispatcher and the receiver sees the override.
   - The 3 rows where the dispatcher PUSHes 0 are: 0x0C, 0x11, 0x12 — for these, the
     value in the table came from the WIRE payload, and the receiver sees what the
     sender wrote.
   - The sender/receiver pairing list at line 148 (`D8->D7`, `DA->D9`, ...) describes
     how the **sender** path uses one code and the **dispatcher override** swaps it to
     a paired code on the receive side. That list is correct and unchanged.

**Dropped claims:** None — every doc claim survived.

**Retired (dedup with sibling — resolves cross-doc disagreement #16):**

- The 15-row SpeciesToShip table in game-opcodes.md (inventory §3.4 notes this) overlaps
  with the 45-row table in `objcreate-serialization.md`. Recommend: game-opcodes.md
  keeps a 3-line summary + cross-link; `objcreate-serialization.md` remains canonical.
  Note: the inventory's #3.4 row for this debt may have been about a different table
  scope (I did not see the 15-row table in the current doc body, which suggests it may
  already have been trimmed in a prior edit; no action required this pass beyond the
  cross-link). **Status: deferred to objcreate-serialization.md row's pass.**

**Body restructure suggested:**

1. Add v5 YAML frontmatter:
   ```yaml
   ---
   title: Game Opcodes (0x02-0x2A)
   type: reference
   audience: re-engineer
   status: partial
   validated: 2026-05-28
   methodology: FUNCTION_DOC_WORKFLOW_V5
   binary:
     name: stbc.exe
     size: 6182400
     base: 0x00400000
   companions:
     - docs/protocol/wire-format-spec.md
     - docs/protocol/transport-layer.md
     - docs/protocol/stream-primitives.md
     - docs/protocol/stateupdate.md
     - docs/protocol/object-replication.md
     - docs/protocol/pythonevent-wire-format.md
     - docs/protocol/collision-effect-protocol.md
     - docs/protocol/set-phaser-level-protocol.md
     - docs/protocol/delete-player-ui-wire-format.md
     - docs/protocol/objnotfound-requestobj-enterset-wire-format.md
     - docs/protocol/cf16-explosion-encoding.md
     - docs/engine/decompiled-functions.md
     - docs/protocol/v5-validation-status.md
   supersedes: prior pre-v5 game-opcodes.md
   ---
   ```
2. Tag every per-opcode row + the jump-table + dispatcher claim with
   `[v5-validated 2026-05-28]`. The 41-entry jump table is the single biggest anchor —
   surface it explicitly at the top of the doc (after the intro) so downstream docs
   can cite "see jump-table table in game-opcodes.md".
3. Tag the trace-derived session-frequency counts (2282/session StartFiring, 33/session
   SetPhaserLevel, 84/session CollisionEffect, etc.) as
   `[cross-source-2026-02-XX trace]` per the engine campaign's two-tag convention —
   these come from `docs/analysis/valentines-day-battle-analysis.md` and similar trace
   docs, not from Ghidra.
4. Clarify the "Recv Event Code" column per C1 above. Add a short footer paragraph
   distinguishing:
   - **Sender path event code** = what the local C++ posts to its event manager.
   - **Wire event code** = what gets serialized into the opcode 0x07-0x1B payload
     (TGEvent factory + event_code field).
   - **Dispatcher override** = what the receive-side dispatcher thunk PUSHes (non-zero
     for 9 opcodes, 0 for 3 opcodes).
   - **Effective event code** = what the receiver's event manager ultimately sees
     (override wins if non-zero, else wire value).
5. Cross-link every opcode row with a wire-format sub-doc to that sub-doc explicitly
   (collision-effect-protocol.md for 0x15, pythonevent-wire-format.md for 0x06/0x0D,
   set-phaser-level-protocol.md for 0x12, delete-player-ui-wire-format.md for 0x17,
   objnotfound-requestobj-enterset-wire-format.md for 0x1D/0x1E/0x1F,
   cf16-explosion-encoding.md for 0x29, stateupdate.md for 0x1C, object-replication.md
   for 0x02/0x03).
6. Add a "Stub" doc note for opcode 0x18 (DeletePlayerAnim) — game-opcodes.md mentions
   the handler address but has no wire-format detail; per the inventory §3.4 visible
   debt, no companion leaf exists for 0x18. There IS an OpenBC clean-room doc
   (`../OpenBC/docs/wire-formats/delete-player-anim-wire-format.md`); the BC side
   should mirror it. **Status: open question; not blocking game-opcodes.md's
   partial->verified transition once the doc is restructured.**

**Companion follow-ups:**

- **stateupdate.md** (row #8) — receives the StateUpdate handler anchor at `0x0069FF50`
  from this pass; its own validation will deepen the per-flag wire formats.
- **collision-effect-protocol.md** (row #15) — receives the re-post event code
  `0x008000FC` and the distance gate `_DAT_008955c8` confirmations.
- **cf16-explosion-encoding.md** (row #21) — receives the receive-side field-order
  confirmation (radius first via fStack_50, damage second via fStack_54).
- **pythonevent-wire-format.md** (row #14) — receives the 0x06/0x0D shared-handler
  confirmation.
- **delete-player-ui-wire-format.md** (row #17) — receives the 0x17 handler chain
  confirmation.
- **CLAUDE.md game-opcode table** — campaign-close batch should add the 0x1C row
  (currently missing). The dispatcher recovery already noted this in
  `dispatcher-recovery-20260528.md`. Action: append a row
  `| 0x1C | StateUpdate | FUN_0069FF50 | Object state replication (8 dirty-flag formats)|`
  to CLAUDE.md's Game Opcode Table.
- **OpenBC** has a delete-player-anim spec; the BC side needs a mirror doc for opcode
  0x18 to fill the documentation gap.

**Open questions left for downstream rows:**

1. **Opcode 0x18 (DeletePlayerAnim) wire format.** Handler `FUN_006A1420` is named but
   the wire format and TGL crash risk noted in `docs/analysis/tgl-lookup-crash-analysis.md`
   need a dedicated wire-format leaf doc on the BC side. Mirror from
   `../OpenBC/docs/wire-formats/delete-player-anim-wire-format.md`.
2. **TGEvent factory address `DAT_0097f838` for posting.** Doc claims (line 111):
   *"posts it to the event manager at `DAT_0097f838`"*. The body of FUN_0069F880 reaches
   `FUN_006DA300` (the event-poster pipeline), but the engine campaign doc #8 validation
   placed the TGEventManager singleton at global `0x00991438`, not `0x0097F838`.
   `0x0097F838` is documented in the engine anchor table (§7.1) as "Event manager", so
   both addresses may be valid — possibly two registries (event-handler hash table vs
   event manager singleton). Resolution belongs to whichever doc claims the precise
   field. This game-opcodes.md row does not need to anchor that distinction; defer to
   pythonevent-wire-format.md or stateupdate.md when one of them needs the exact
   singleton address.
3. **Session-frequency counts** — the doc's "Stock 15-min count" column (2282, 33, 84,
   etc.) is sourced from packet traces, not the binary. Per the engine campaign's
   two-tag convention, these need `[cross-source-2026-02-XX]` tags pointing to the
   trace docs in `docs/analysis/`. **Status: stylistic; doc remains correct, just
   needs the tags surfaced.**

**Files touched:** docs/protocol/v5-validation-status.md (this row added; §2 row #4
status flipped to partial). docs/protocol/game-opcodes.md NOT modified this pass —
the documentation-writer agent will re-render with the v5 frontmatter, column-header
clarification, two-tag annotations on session-frequency claims, and explicit
cross-links to each leaf wire-format doc.

---

## 7. Anchor table

Cross-doc anchor points the protocol-family Ghidra snapshot should pin. Many are inherited
from the engine campaign (marked `[engine v5-validated 2026-05-28]`); the rest are new in
the protocol family.

### 7.1 Engine-inherited anchors (already v5-validated)

| Anchor | Address / Value | First cited in | Reused by (protocol) |
|--------|-----------------|----------------|-----------------------|
| MultiplayerGame dispatcher | 0x0069f2a0 | engine function-map.md | wire-format-spec, game-opcodes, transport-layer, tgmessage-routing, set-phaser-level-protocol, pythonevent-wire-format |
| Jump table for game opcodes 0x02-0x2A | 0x0069F534 (41 entries) | engine function-map.md | wire-format-spec, game-opcodes |
| TGMessage base vtable | 0x008958d0 | engine decompiled-functions.md (implicit) | transport-layer.md |
| TGEvent base vtable | 0x00895FF4 | engine event-system-architecture.md | pythonevent-wire-format.md, collision-effect-protocol.md |
| TGCallback vtable | 0x008960f4 | engine event-system-architecture.md | (unused in protocol) |
| Event manager | 0x0097F838 | engine decompiled-functions.md | pythonevent-wire-format.md, subsystem-integrity-hash.md |
| UtopiaModule base | 0x0097FA00 | engine decompiled-functions.md | (used implicitly everywhere) |
| WSN pointer | 0x0097FA78 | engine decompiled-functions.md | pythonevent-wire-format.md, set-phaser-level-protocol.md |
| NetFile ptr / dispatcher | 0x006a3cd0 | engine decompiled-functions.md | checksum-opcodes.md, transport-layer.md |
| IsClient byte | 0x0097FA88 | CLAUDE.md | implicit in stateupdate.md |
| IsHost byte | 0x0097FA89 | CLAUDE.md | collision-effect-protocol.md |
| IsMultiplayer byte | 0x0097FA8A | CLAUDE.md | stateupdate.md, subsystem-integrity-hash.md, pythonevent-wire-format.md |
| TGNetwork::Update | 0x006b4560 | engine decompiled-functions.md | python-messages.md, tgmessage-routing.md |
| TGNetwork::Send / SendTGMessage | 0x006b4c10 | engine decompiled-functions.md | python-messages.md, tgmessage-routing.md, objnotfound-requestobj-enterset |
| ProcessIncomingPackets | 0x006b5c90 | engine decompiled-functions.md | tgmessage-routing.md, transport-layer.md |
| SendOutgoingPackets | 0x006b55b0 | engine decompiled-functions.md | implicit |
| ComputeChecksum | 0x0071f270 | engine decompiled-functions.md | (used indirectly by checksum-opcodes flow) |

### 7.2 Protocol-new globals and tables

| Anchor | Address / Value | Cited in |
|--------|-----------------|----------|
| Transport factory table | DAT_009962d4 (256 slots, 7 populated) | transport-layer, tgmessage-routing |
| AlbyRules cipher key | 0x0095abb4 | transport-layer |
| SendPacket | 0x006b9870 | transport-layer |
| ReceivePacket | 0x006b95f0 | transport-layer |
| Subsystem-ID counter | DAT_0095B078 | pythonevent-wire-format |
| TGObject hash table for ID resolution | DAT_0099A67C | pythonevent-wire-format, objcreate-serialization (FUN_006f13c0 ResolveReferences) |
| CF16 BASE constant | DAT_00888b4c = 0.001f | stream-primitives, cf16-precision-analysis, cf16-explosion-encoding |
| CF16 MULT constant | DAT_0088c548 = 10.0f | (same three) |
| CF16 ENC_SCALE | DAT_00895f50 = 4095.0f | (same three) |
| CF16 DEC_SCALE | DAT_00895f54 = float32(1/4095) | (same three) |
| CF16 ZERO | DAT_00888b54 = 0.0f | cf16-explosion-encoding |
| Force-update threshold | DAT_00888860 | stateupdate.md (currently uncited value) |
| Settings byte 1 / collisionDamage | DAT_008e5f59 | game-opcodes.md (opcode 0x00 wire format) |
| Settings byte 2 / friendlyFire | DAT_0097faa2 | game-opcodes.md, stateupdate.md |
| Object lookup threshold | DAT_008e5c18 (RequestObj HP gate) | objnotfound-requestobj-enterset |
| Collision distance threshold | DAT_008955c8 | collision-effect-protocol.md |
| "NoMe" group name string | 0x008e5528 | python-messages, tgmessage-routing |
| "Forward" group name string | 0x008d94a0 | python-messages, tgmessage-routing |
| MAX_MESSAGE_TYPES SWIG constant | 43 (registered 0x00654f31, value at 0x0090b490) | python-messages, tgmessage-routing |
| Sentinel value for object refs | 0x0095ADFC | pythonevent-wire-format, set-phaser-level-protocol |
| "Space" set name string | 0x008d8ab8 | objnotfound-requestobj-enterset |
| Anti-cheat sentinel constants (8 float bit patterns) | 0x42800083 / 0x42993333 / 0x42c53333 / 0x42c80000 / 0x4164cccd / 0x43e40ccd / 0x41da6666 / 0x4180cccd | subsystem-integrity-hash |

### 7.3 Protocol-new function anchors (game opcodes 0x02-0x2A handlers)

| Address | Name | Opcode | Cited in |
|---------|------|--------|----------|
| 0x0069f620 | Handler_ObjCreate_0x02_0x03 | 0x02, 0x03 | game-opcodes, object-replication, objcreate-serialization |
| 0x0069f880 | Handler_PythonEvent | 0x06, 0x0D | game-opcodes, tgmessage-routing, pythonevent-wire-format |
| 0x0069fda0 | Handler_GenericEventForward | 0x07-0x0C, 0x0E-0x12, 0x1B | game-opcodes, set-phaser-level-protocol, pythonevent-wire-format |
| 0x006A01B0 | Handler_HostMsg | 0x13 | game-opcodes |
| 0x006a01e0 | Handler_DestroyObject | 0x14 | game-opcodes |
| 0x006a2470 | Handler_CollisionEffect | 0x15 | wire-format-spec, game-opcodes, collision-effect-protocol |
| 0x006a1360 | Handler_DeletePlayerUI | 0x17 | wire-format-spec, game-opcodes, delete-player-ui-wire-format |
| 0x006a1420 | Handler_DeletePlayerAnim | 0x18 | wire-format-spec, game-opcodes |
| 0x0069F930 | Handler_TorpedoFire | 0x19 | game-opcodes |
| 0x0069FBB0 | Handler_BeamFire | 0x1A | game-opcodes |
| 0x0069FF50 | Ship_WriteStateUpdate dispatch | 0x1C (sender FUN_005b17f0) | wire-format-spec |
| 0x006a0490 | Handler_ObjNotFound | 0x1D | game-opcodes, objnotfound-requestobj-enterset |
| 0x006a02a0 | Handler_RequestObj | 0x1E | game-opcodes, objnotfound-requestobj-enterset |
| 0x006a05e0 | Handler_EnterSet | 0x1F | game-opcodes, objnotfound-requestobj-enterset |
| 0x006A0080 | Handler_Explosion | 0x29 | game-opcodes, cf16-precision-analysis, cf16-explosion-encoding |
| 0x006A1E70 | Handler_NewPlayerInGame | 0x2A | game-opcodes, wire-format-spec |
| 0x00504c10 | MultiplayerWindow dispatcher | 0x00, 0x01, 0x16 | wire-format-spec, transport-layer, tgmessage-routing |
| 0x00504d30 | Handler_Settings | 0x00 | game-opcodes |
| 0x00504f10 | Handler_GameInit | 0x01 | game-opcodes |
| 0x00504c70 | Handler_UICollisionSetting | 0x16 | game-opcodes |
| 0x006a5df0 | Handler_ChecksumRequest | 0x20 | checksum-opcodes |
| 0x006a4260 | Handler_ChecksumResponse | 0x21 | checksum-opcodes |
| 0x006a4c10 | Handler_ChecksumFail | 0x22, 0x23 | checksum-opcodes |
| 0x006a3ea0 | Handler_FileTransfer | 0x25 | checksum-opcodes |
| 0x006a4250 | Handler_FileTransferACK | 0x27 | checksum-opcodes |

### 7.4 Stream-primitives function anchors

| Address | Name | Cited in |
|---------|------|----------|
| 0x006cefe0 | TGBufferStream constructor | stream-primitives, collision-effect-protocol |
| 0x006cf180 | TGBufferStream::Init (set buf/offset/size) | objcreate-serialization, collision-effect-protocol |
| 0x006cf230 | ReadBytes | stream-primitives |
| 0x006cf2b0 | WriteBytes / memcpy | stream-primitives, python-messages |
| 0x006cf460 | WriteCString | python-messages |
| 0x006cf540 | ReadByte | stream-primitives |
| 0x006cf580 | ReadBit | stream-primitives |
| 0x006cf5e0 | ReadByte (alt — collision-effect-protocol vtable +0x50) | collision-effect-protocol |
| 0x006cf600 | ReadShort / ReadU16 | stream-primitives, collision-effect-protocol |
| 0x006cf640 | ReadU32 (class type ID — vtable +0x60) | collision-effect-protocol |
| 0x006cf670 | ReadInt32 / ReadU32 (general — vtable +0x68) | stream-primitives, objcreate-serialization, collision-effect-protocol |
| 0x006cf6a0 | ReadInt32v / ReadObjID thunk | stream-primitives, collision-effect-protocol |
| 0x006cf6b0 | ReadFloat | stream-primitives, collision-effect-protocol |
| 0x006cf730 | WriteByte | stream-primitives, python-messages |
| 0x006cf770 | WriteBit | stream-primitives |
| 0x006cf7a0 | WriteBool | python-messages |
| 0x006cf7f0 | WriteShort | stream-primitives, python-messages |
| 0x006cf830 | WriteInt | python-messages |
| 0x006cf870 | WriteInt32 / WriteLong | stream-primitives, python-messages |
| 0x006cf8b0 | WriteFloat | stream-primitives, python-messages |
| 0x006cf9b0 | GetPosition | stream-primitives |
| 0x006d29a0 | CompressVec4_Byte_Direction | collision-effect-protocol |
| 0x006d2ad0 | WriteCompressedVector3 | stream-primitives |
| 0x006d2d10 | CompressVec4_Byte_Magnitude | collision-effect-protocol |
| 0x006d2eb0 | ReadCompressedVector3 | stream-primitives |
| 0x006d2f10 | WriteCompressedVector4 | stream-primitives, stateupdate |
| 0x006d2fd0 | ReadCompressedVector4 | stream-primitives |
| 0x006d30e0 | DecompressVec4_Byte | collision-effect-protocol |
| 0x006d3a90 | CF16 encoder | stream-primitives, cf16-precision-analysis, cf16-explosion-encoding |
| 0x006d3b30 | CF16 decoder | stream-primitives, cf16-precision-analysis, cf16-explosion-encoding |

### 7.5 Transport / TGMessage / message-routing anchors

| Address | Name | Cited in |
|---------|------|----------|
| 0x006b3a00 | TGNetwork constructor (initializes factory table) | tgmessage-routing |
| 0x006b4c10 | SendTGMessage | python-messages, tgmessage-routing, objnotfound-requestobj-enterset |
| 0x006b4de0 | SendTGMessageToGroup | python-messages, tgmessage-routing |
| 0x006b4ec0 | SendToGroupMembers | python-messages, tgmessage-routing |
| 0x006b51e0 | BroadcastToOthers (host relay) | tgmessage-routing |
| 0x006b5080 | QueueForSend | tgmessage-routing, transport-layer (seq counter set) |
| 0x006b52b0 | DequeueCompletedMessages | python-messages |
| 0x006b61e0 | ReliableACK | transport-layer |
| 0x006b63a0 | HandleConnection / auto-relay | tgmessage-routing |
| 0x006b6ad0 | Fragment dispatch | transport-layer |
| 0x006b6cc0 | FragmentReassembly | transport-layer |
| 0x006b82a0 | TGMessage constructor (size 0x40) | transport-layer, python-messages |
| 0x006b8340 | TGMessage::WriteToBuffer | transport-layer, python-messages |
| 0x006b83f0 | TGMessage factory (type 0x32) | transport-layer, tgmessage-routing |
| 0x006b84d0 | BufferCopy | python-messages |
| 0x006b8530 | TGMessage::GetData / GetBuffer | tgmessage-routing, collision-effect-protocol, objcreate-serialization |
| 0x006b8550 | TGMessage copy constructor | transport-layer |
| 0x006b8610 | TGMessage::Clone (vtable[6]) | transport-layer |
| 0x006b8640 | TGMessage::GetSize (vtable[5]) | transport-layer |
| 0x006b8720 | FragmentMessage (vtable[7]) | transport-layer |
| 0x006b89a0 | Replace message buffer (post-reassembly) | transport-layer |
| 0x006b8a00 | SetDataFromStream | python-messages |
| 0x006b9430 | GetType (returns 0x32, vtable[0]) | transport-layer |
| 0x006bc6a0 | TGDataMessage factory (type 0x00) | transport-layer, tgmessage-routing |
| 0x006bd1f0 | TGHeaderMessage factory (type 0x01 ACK) | transport-layer |
| 0x006bdd10 | TGConnectMessage factory (type 0x02) | transport-layer |
| 0x006be860 | TGConnectAckMessage factory (type 0x03) | transport-layer |
| 0x006badb0 | TGBootMessage factory (type 0x04) | transport-layer |
| 0x006bf410 | TGDisconnectMessage factory (type 0x05) | transport-layer |
| 0x006bfe80 | TGMessageEvent constructor (size 0x2C) | python-messages |
| 0x006bff30 | TGMessageEvent::AttachMessage | python-messages |
| 0x005e4860 | RegisterMessageType SWIG wrapper | tgmessage-routing |

### 7.6 StateUpdate, ObjCreate, subsystem anchors

| Address | Name | Cited in |
|---------|------|----------|
| 0x005b17f0 | Ship_WriteStateUpdate (sender) | stateupdate, stateupdate-subsystem-wire-format, subsystem-integrity-hash |
| 0x005b21c0 | Ship_ReadStateUpdate (receiver) | stateupdate, stateupdate-subsystem-wire-format, subsystem-integrity-hash |
| 0x005b1e38 | (CF16 caller in StateUpdate writer) | cf16-precision-analysis |
| 0x005b3e20 | Ship_LinkAllSubsystemsToParents | stateupdate-subsystem-wire-format |
| 0x005b3e50 | Ship_AddSubsystemToLists | stateupdate-subsystem-wire-format |
| 0x005b3fb0 | Ship_SetupProperties | stateupdate-subsystem-wire-format |
| 0x005b5030 | Ship_LinkSubsystemToParent (engine type tag) | stateupdate-subsystem-wire-format |
| 0x005b5eb0 | ComputeSubsystemHash (12-slot iterator) | wire-format-spec, subsystem-integrity-hash |
| 0x005b6170 | base_subsystem_hash | subsystem-integrity-hash |
| 0x005b6330 | weapon_system_hash | subsystem-integrity-hash |
| 0x005b6560 | individual_weapon_hash | subsystem-integrity-hash |
| 0x005b6c10 | hash_fold (XOR + rotate accumulator) | subsystem-integrity-hash |
| 0x0056d320 | ShipSubsystem WriteState (Base) | stateupdate, stateupdate-subsystem-wire-format |
| 0x0056d390 | ShipSubsystem ReadState (Base) | stateupdate-subsystem-wire-format |
| 0x00562960 | PoweredSubsystem WriteState | stateupdate, stateupdate-subsystem-wire-format |
| 0x005629d0 | PoweredSubsystem ReadState | stateupdate-subsystem-wire-format |
| 0x005644b0 | PowerSubsystem WriteState (reactor — battery bytes) | stateupdate, stateupdate-subsystem-wire-format |
| 0x00564530 | PowerSubsystem ReadState | stateupdate-subsystem-wire-format |
| 0x0056c310 | GetMaxCondition | stateupdate-subsystem-wire-format |
| 0x0056c570 | GetChildSubsystem | stateupdate-subsystem-wire-format |
| 0x0056c5c0 | AddChildSubsystem | stateupdate-subsystem-wire-format |
| 0x005a1f50 | Ship_Deserialize | objcreate-serialization, object-replication |
| 0x005a2030 | (disputed: ReadSpeciesByte vs GetPlayerSlotFromObjID — §4 #1) | objcreate-serialization, objnotfound-requestobj-enterset |
| 0x005b0e80 | InitObject (Ship field deserialization) | objcreate-serialization |
| 0x00430730 | ObjectLookupByID hash | objcreate-serialization |
| 0x006f13e0 | TGFactoryCreate / TGEventFactory::Lookup | objcreate-serialization, collision-effect-protocol, pythonevent-wire-format |
| 0x006f13c0 | ResolveReferences (object ID → ptr) | collision-effect-protocol, pythonevent-wire-format |

### 7.7 Event-class anchors (factory IDs and class layouts)

| Anchor | Address / Value | Cited in |
|--------|-----------------|----------|
| TGEvent factory | 0x0002 / size 0x28 / vtable 0x00895FF4 | pythonevent-wire-format, set-phaser-level-protocol, collision-effect-protocol |
| TGSubsystemEvent factory | 0x0101 / size 0x28 / vtable 0x008932A4 | pythonevent-wire-format |
| TGCharEvent factory | 0x0105 / size 0x2C / vtable 0x008932DC / ctor 0x00574C20 | pythonevent-wire-format, set-phaser-level-protocol |
| TGObjPtrEvent factory | 0x010C / size 0x2C / vtable 0x0088869C / ctor 0x00403290 | tgobjptrevent-class, pythonevent-wire-format |
| ObjectExplodingEvent factory | 0x8129 / size 0x30 / vtable 0x0088A178 / ctor 0x0043F8B0 | pythonevent-wire-format |
| CollisionEvent factory | 0x8124 / size 0x44 / vtable 0x0089395c / ctor 0x00586d00 | collision-effect-protocol |
| DeletePlayerUI factory (disputed family — §4 #13) | 0x0866 | delete-player-ui-wire-format |
| TGEvent::WriteToStream / ReadToStream | 0x006D6130 / 0x006D61C0 | pythonevent-wire-format, set-phaser-level-protocol, collision-effect-protocol |
| TGCharEvent::WriteToStream / ReadFromStream | 0x006D6940 / 0x006D6960 | pythonevent-wire-format, set-phaser-level-protocol |
| TGObjPtrEvent::WriteToStream / ReadFromStream | 0x006D6DC0 / 0x006D6DF0 | tgobjptrevent-class, pythonevent-wire-format |
| ObjectExplodingEvent::WriteToStream / ReadFromStream | 0x0043F990 / 0x0043F9C0 | pythonevent-wire-format |
| CollisionEvent::WriteToStream / ReadFromStream (network) | 0x005871a0 / 0x00587300 | collision-effect-protocol |
| ReadObjectFromStream (factory dispatch) | 0x006d6200 | game-opcodes, collision-effect-protocol, pythonevent-wire-format, delete-player-ui-wire-format |

### 7.8 Event types (constants used across protocol docs)

| Constant | Value | Cited in |
|----------|-------|----------|
| ET_NETWORK_MESSAGE_EVENT | 0x60001 | python-messages, transport-layer |
| ET_NETWORK_DELETE_PLAYER | 0x60005 | delete-player-ui-wire-format |
| ET_OBJECT_COLLISION | 0x00800050 | wire-format-spec, game-opcodes, collision-effect-protocol, pythonevent-wire-format |
| ET_HOST_OBJECT_COLLISION | 0x008000FC | collision-effect-protocol, pythonevent-wire-format |
| ET_COLLISION_DAMAGE | 0x00800053 | collision-effect-protocol, pythonevent-wire-format |
| ET_OBJECT_EXPLODING | 0x0080004E | pythonevent-wire-format |
| ET_SUBSYSTEM_HIT | 0x0080006B | pythonevent-wire-format, tgobjptrevent-class |
| ET_SUBSYSTEM_STATUS_CHANGED | 0x0080006C | game-opcodes (opcode 0x0A) |
| ET_SUBSYSTEM_DAMAGED | 0x00800070 | pythonevent-wire-format |
| ET_REPAIR_COMPLETED | 0x00800074 | pythonevent-wire-format |
| ET_REPAIR_CANNOT_BE_COMPLETED | 0x00800075 | pythonevent-wire-format |
| ET_REPAIR_INCREASE_PRIORITY | 0x00800076 | game-opcodes, tgobjptrevent-class |
| ET_WEAPON_FIRED | 0x0080007C | tgobjptrevent-class, pythonevent-wire-format |
| ET_TRACTOR_BEAM_STARTED_FIRING | 0x0080007D | tgobjptrevent-class |
| ET_PHASER_STARTED_FIRING | 0x00800081 | tgobjptrevent-class |
| ET_PHASER_STOPPED_FIRING | 0x00800083 | tgobjptrevent-class |
| ET_START_FIRING (received) | 0x008000D7 | game-opcodes (opcode 0x07) |
| ET_STOP_FIRING (received) | 0x008000D9 | game-opcodes (opcode 0x08) |
| ET_STOP_FIRING_AT_TARGET (received) | 0x008000DB | game-opcodes (opcode 0x09) |
| ET_STOP_FIRING_AT_TARGET_NOTIFY | 0x008000DC | tgobjptrevent-class (host-only gate) |
| ET_ADD_TO_REPAIR_LIST | 0x008000DF | game-opcodes, pythonevent-wire-format |
| ET_SET_PHASER_LEVEL | 0x008000E0 | game-opcodes, set-phaser-level-protocol |
| ET_START_CLOAK | 0x008000E3 | game-opcodes |
| ET_STOP_CLOAK | 0x008000E5 | game-opcodes |
| ET_START_WARP | 0x008000ED | game-opcodes |
| ET_NEW_PLAYER_IN_GAME | 0x008000F1 | delete-player-ui-wire-format |
| ET_BOOT_PLAYER | 0x008000F6 | subsystem-integrity-hash |
| ET_TORP_TYPE_CHANGE | 0x008000FD | game-opcodes |

---

## Notes for the archaeology specialist's snapshot

When merging your protocol-family Ghidra snapshot, the per-doc rows should each gain
two additional fields: (1) **evidence-state** — for each load-bearing claim, whether the
Ghidra state agrees (verified / partial / disputed / not-found); (2) **renamed-since-doc** —
addresses where the doc cites `FUN_xxxxxxxx` but Ghidra now has a real name from the
post-engine-campaign annotation state.

Highest-priority spot-checks for the archaeology pass (load-bearing, cross-doc, or
disputed):

1. **0x005a2030** — confirm semantics. The §4 #1 conflict has objcreate-serialization.md
   calling it `ReadSpeciesByte` and objnotfound-requestobj-enterset.md calling it
   `GetPlayerSlotFromObjID`. Cannot both be true.
2. **0x008958d0** vs **0x0089598c** — confirm the TGMessage base vs TGDataMessage vtable
   slot counts (transport-layer.md claims 8 slots for base, 5 slots for TGDataMessage).
3. **0x00895FF4** — confirm TGEvent vtable slot count (§4 #7: 14 vs 16 vs 18 slot disagreement).
4. **ship+0x2BC slot** — §4 #4: is it "always NULL" (wire-format-spec slot map) or
   "Pulse Weapon System hash slot 11" (subsystem-integrity-hash)?
5. **DAT_009962d4** — confirm 256-slot transport factory table; confirm only 7 populated.
6. **Factory 0x866** — find it in the factory hash table. Where does it live in the
   factory-ID space (0x02 base / 0x101 / 0x105 / 0x10C / 0x866 / 0x8124 / 0x8129)?
7. **DAT_00888860** — the force-update threshold — what's its value?
8. **DAT_008e5c18** — RequestObj HP gate threshold — what's its value?
9. **DAT_008955c8** — collision distance threshold — what's its value?

Anchor table §7 is the index — every entry there should appear in your snapshot so a
downstream pass can grep and confirm. Tables §7.4 (stream primitives) and §7.7 (event
class anchors) are the densest cross-reference clusters and yield the most leverage if
spot-checked first.
