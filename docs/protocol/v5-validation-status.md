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

**Campaign closed 2026-05-28 at 22/22 docs validated** — final leaf (#22 message-trace-vs-packet-trace.md) cleared on the same day as the engine cross-source pass and the final mid-tier docs. 4 docs reached `verified` (#15 collision-effect-protocol, #16 set-phaser-level-protocol, #20 cf16-precision-analysis, #21 cf16-explosion-encoding); the remaining 18 sit at `partial` pending minor body restructure / frontmatter touch-ups. See the **Campaign close summary** at the bottom of §6 for batched follow-ups (CLAUDE.md Documentation Index refresh, OpenBC clean-room cascade, family-close commit).

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
| 5 | checksum-opcodes.md | Mid: opcodes 0x20-0x28 NetFile dispatcher | wire-format-spec, transport-layer | **partial (2026-05-28)** — 2 material corrections (dialog swap + 5-round fabrication); 32 anchors confirmed; 1 open question on round-0xFF sender; see §6.5 |
| 6 | python-messages.md | Mid: opcodes 0x2C+ MAX_MESSAGE_TYPES + SendTGMessage path | wire-format-spec, stream-primitives | **partial (2026-05-28)** — 1 correction (WriteCString length-prefix width), 1 clarification (TGBufferStream::Serialize vs TGMessage::WriteToBuffer), 2 cross-source-tagged Python-handler claims; see §6.6 |
| 7 | tgmessage-routing.md | Mid: relay-all + star topology + opaque payload | python-messages, transport-layer | **partial (2026-05-28)** — 3 material corrections (C1: FUN_006B63A0 is connect handler not type-0x00 relay; C2: `NoMe` created by C++ MultiplayerGame_Ctor not Python; C3: THREE routing mechanisms not two) + 2 minor (function name FUN_006B8530 = TGBufferStream_GetBufferAndSize; SendTGMessage pseudocode now covers targetID == -1); 15 anchors confirmed; 3 open questions including chat 1:2 mystery; see §6.7 |
| 8 | stateupdate.md | Mid: opcode 0x1C dirty flags + 8 field formats + round-robin | game-opcodes, stream-primitives | **partial (2026-05-28)** — all 8 dirty-bit wire formats anchored byte-by-byte; ZERO material corrections; 5 clarifications (hash-flag-emit gate identity, wire-vs-validation conflation, weapon list shared with subsystems, CLIENT-side IsMultiplayer speculation should be dropped, PowerSubsystem WriteState created in Ghidra); see §6.8 |
| 9 | object-replication.md | Mid: FUN_0069f620 thin index for ObjCreate | game-opcodes | **partial (2026-05-28)** — all 6 claims confirmed at high confidence; 2 wording refinements (R1 sender-side helper FUN_006A19A0; R2 vtable[+0x10C] sender / vtable[+0x118]+[+0x11C] receiver via FUN_005A1F50); MpgameHandleObjCreate renamed at 0x0069F620; see §6.9 |
| 10 | objcreate-serialization.md | Mid: full ObjCreate chain + species map | object-replication, stream-primitives | **partial (2026-05-28)** — 3 material corrections (C1 velocity = CV4 3-dir + 4-mag, not f32-speed + 3-pad; C2 playerSlots base = +0x74 not +0x84; C3 vtable[+0x118] only does species+Python, body+subsystems is vtable[+0x11C]); orientation quaternion confirmed; species map byte-exact vs scripts; 11 functions renamed; see §6.10 |
| 11 | stateupdate-subsystem-wire-format.md | Mid: subsystem linked list + 3 WriteState formats | stateupdate | **partial (2026-05-28)** — 2 material corrections (C1 ship+0x2C4 was HullSubsystem not PowerSubsystem + add missing 0x2C0/0x2C8; C2 EndMarker attribution corrected from 0x006CDAE0 to 0x006CF9B0); 10+ confirmed claims; 14 Ghidra renames + 1 created + 7 plates; see §6.11 |
| 12 | per-ship-subsystem-wire-format.md | Mid: 16 stock ship subsystem catalogs | stateupdate-subsystem-wire-format | **partial (2026-05-28)** — 4 sampled ships byte-exact (Sovereign 49 / Bird of Prey 32 / Galor 31 / Akira 47); ZERO material wire-format corrections; 3 refinements (R1 cycle-byte math is per-tick exact / per-cycle approximate due to bit packing; R2 "top-level" is post-link count; R3 silently-dropped templates like Probe Launcher / Shuttle Bay / Decoy Launcher); 11 remaining ships + Enterprise@37 at medium confidence via pattern extrapolation; foundation cross-anchor (mid #11 ship+0x2B0..+0x2DC slot table) re-confirmed; see §6.12 |
| 13 | tgobjptrevent-class.md | Mid: TGObjPtrEvent class layout + 11 producers | (engine: TGEvent vtable 0x00895FF4) | **partial (2026-05-28)** — 0 wire-format / 0 producer corrections; 3 corrections (C1 0x101 is TGEvent itself not "TGSubsystemEvent" / C2 vtable slot 0 is dtor not 0x00403310 + 17 slots not 12-14 / C3 SWIG wrapper addresses unverified in current Ghidra DB); class layout 0x2C bytes confirmed byte-by-byte; all 11 game event types verified at producer sites; dual-fire and host-only gates confirmed; see §6.13 |
| 14 | pythonevent-wire-format.md | Leaf: opcode 0x06 + 4 event factories | tgobjptrevent-class, game-opcodes | **partial (2026-05-28)** — class hierarchy correction (0x101 = TGEvent itself, not "TGSubsystemEvent"); ObjectExploding IsA-chain refinement (3 IDs not 2); source-vs-dest WriteObjectRef encoding asymmetry; wire-format dimensions for all 4 classes byte-by-byte CONFIRMED; both producers (HostEventHandler 0x006A1150 + ObjectExplodingHandler 0x006A1240) byte-by-byte confirmed but were undefined in DB (still are — disassembled raw); MpgameHandlePythonEvent renamed at 0x0069F880; see §6.14 |
| 15 | collision-effect-protocol.md | Leaf: opcode 0x15 + CollisionEvent class + validation chain | game-opcodes, stream-primitives | **verified (2026-05-28)** — first protocol family doc to clear `verified`; all 110+ claims byte-by-byte confirmed; ZERO material wire-format changes; 1 byte-level typo (handler-table 0x005afab0 -> 0x005AFAD0) + 1 wording clarification (PostEvent __thiscall via TGEventManager singleton at 0x0097F838); critical OpenBC finding confirmed (stock dedi has NO server-side recomputation of contact points or force); see §6.15 |
| 16 | set-phaser-level-protocol.md | Leaf: opcode 0x12 + TGCharEvent | game-opcodes, tgobjptrevent-class | **verified (2026-05-28)** — second protocol-family doc to clear `verified`; 18-byte wire format byte-by-byte confirmed; ZERO material wire-format changes; 3 minor corrections (C1 hierarchy cascade — no TGSubsystemEvent, 0x101 IS TGEvent; C2 registration-string typography "MultiplayerGame :: SetPhaserLevelHandler" with spaces; C3 helper-fn rename FUN_006d6200 → TGFactory_DeserializeObject); 4 functions newly created (sender thunk, applier, TGCharEvent::Write/ReadFromStream) + 4 renamed + 4 plates; foundation cross-anchors (TGCharEvent 0x2C, IsA {0x105, 0x101, 0x02}, TGEvent base 16B) all hold; see §6.16 |
| 17 | delete-player-ui-wire-format.md | Leaf: opcode 0x17 + factory 0x866 | game-opcodes, pythonevent-wire-format | **partial (2026-05-28)** — 3 corrections + 4 clarifications + MAJOR architectural finding (two-registry architecture closes wire-format-spec OQ #2); receiver/transport/authority all v5-validated; 0x866 located in TGFactory registry (DAT_0099a578) which is separate from NiRTTI; FUN_006a0ca0 corrected to opcode 0x18 sender (not 0x17); dst_obj_id semantic corrected (network singleton handle, not ship/player); see §6.17 |
| 18 | objnotfound-requestobj-enterset-wire-format.md | Leaf: opcodes 0x1D/0x1E/0x1F triad | game-opcodes, objcreate-serialization | **partial (2026-05-28)** — 3 material wire/value corrections (C1 setName is length-prefixed not null-terminated; C2 DAT_008d8ab8 is `"warp"` tunnel sentinel not `default space combat set`; C3 DAT_008e5c18 is FLT_MAX undamaged sentinel not low-HP threshold — strictly stricter gate) + 2 address-mapping corrections (C4 GetPlayerSlotFromObjID is at 0x006a19a0 not 0x005a2030; C5 0x006a7770 is MakeObjIDFromPlayerSlot the INVERSE and not called by triad) + 2 clarifications (Clar1 triad uses raw stream primitives only — bypasses TGFactory_DeserializeObject — these are command/RPC messages not event objects; Clar2 IsLocalPlayerShip is host-mode-aware so opcode 0x03 is selected for every team-bearing ship on a dedicated server); foundation cross-anchors all hold (dispatcher 0x0069F2A0, jump table 0x0069F534, TGNetwork singleton, "NoMe" group, "UNKNOWN" allocator); 5 functions renamed + 2 created in Ghidra + 5 plates; closes §4 #1 (FUN_005a2030 = ShipReadSpecies — binary sides with objcreate-serialization.md); closes §4 #15 (breadcrumb added); see §6.18 |
| 19 | subsystem-integrity-hash.md | Leaf analysis: dead-code anti-cheat hash | stateupdate, per-ship-subsystem-wire-format | **partial (2026-05-28)** — ONE material correction (C1: 6 of 12 slot subsystem-identity labels were stale pre-correction names, now cascaded from foundation #1; doc line 129 negative claim "Repair does not appear in the hash" was wrong on TWO counts and is corrected — RepairSubsystem IS hashed at slot 7) + 4 clarifications (Clar-1 receiver event-type at event+0x10 as immediate; Clar-2 torpedo int->float cast precision; Clar-3 &ET_BOOT_PLAYER and 0x008000F6 are the same address constant; Clar-4 sender SAR is signed but wire-identical to unsigned shift); hash function reads CORRECT offsets — only the human-readable identity column was wrong; all 6 boolean sentinel magic constants byte-exact; sender/receiver/wire encoding/kick path byte-by-byte confirmed; container aliasing pattern documented; 5 functions renamed + 1 created (MultiplayerWindow_BootPlayerHandler at 0x00506170) + 4 plates; see §6.19 |
| 20 | cf16-precision-analysis.md | Leaf analysis: CF16 encoder/decoder + precision tables | stream-primitives | **verified (2026-05-28)** — third protocol-family doc to clear `verified`; rendered as batch with leaf #21; ZERO algorithm / constant / struct changes; 1 refinement (R1 encoder xref count 5 not 4 — extra site at 0x005a2b3b in undefined fn, flag-0x10 speed gate confirmed; full enumerated 5-site table replaces the prior 4-row narrative) + 1 clarification (Clar1 `int()` vs `round()` cross-link added to companion #21 alongside the existing column); 5 .rdata constants byte-exact via shared anchor packet; 14-byte opcode 0x29 wire frame + 0x38 ExplosionDamage struct byte-by-byte confirmed (ctor at 0x004bbde0, vtable 0x0088c6c4); OQ1 (5th caller fn identity) added to §4; see §6.20 |
| 21 | cf16-explosion-encoding.md | Leaf analysis: opcode 0x29 + mod weapon ID round-trip | cf16-precision-analysis, game-opcodes | **verified (2026-05-28)** — fourth protocol-family doc to clear `verified`; rendered as batch with leaf #20; ZERO algorithm / constant / encoded-hex changes; 1 byte-size correction (C1 CV4 position field is 5 bytes not "~7" — `mag_as_cf16=1` selects 3 dir bytes + CF16 magnitude; the 14-byte total was always inconsistent with the prior "~7" rendering) + 1 clarification (Clar1 ExplosionDamage 0x38-byte struct table cross-linked to companion #20); CV4 byte-size dispatch on `mag_as_cf16` flag documented at FUN_006d2f10; sender FUN_00595c60 + 2 replay-path callers (RequestObjHandler 0x006a02a0 + NewPlayerInGameHandler 0x006a1e70) all xref-confirmed; `round()` match results 15/25/273 YES, 2063 NO confirmed via arithmetic; cross-doc disagreement #8 (CF16 doc overlap) addressed via cross-links rather than merge; see §6.21 |
| 22 | message-trace-vs-packet-trace.md | Leaf analysis: cross-trace opcode reconciliation | game-opcodes, stateupdate, tgmessage-routing | **partial (2026-05-28)** — FINAL leaf, closes protocol family at 22/22; cross-source doc; 17 claim-promotions from `[cross-source-2026-02-10 trace]` to `[v5-validated 2026-05-28 via <anchor>]` (every load-bearing trace observation now independently anchored in a v5 mid/leaf doc); 3 historical-section marks (packet_trace decoder bug FIXED in current proxy; "newly identified opcodes" all now anchored; flags=0x00 RESOLVED via DeferredInitObject); 1 label clarification (opcode 0x28 "Unknown" → "ChecksumComplete" with anchor); ZERO material wire-format corrections; 2 open questions promoted (OQ1 informal Python-message label drift; OQ2 0x0D re-emit path); see §6.22 |
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
- **Validation status (2026-05-28):** `partial`. 6/6 claims confirmed; 2 wording refinements pending. See §6.9 for full report. Function renamed to `MpgameHandleObjCreate` in Ghidra (program: STBC.exe).

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
| 1 | `FUN_005a2030` semantics: "ReadSpeciesByte" (reads species into ship+0xEC) vs "GetPlayerSlotFromObjID" | objcreate-serialization.md (key-functions table) vs objnotfound-requestobj-enterset-wire-format.md (function-addresses table) | **CLOSED (2026-05-28, leaf #18):** binary truth — `0x005a2030` IS `ShipReadSpecies` (a 2-vtable-call ship-setup function that reads a species value into ship+0xEC). The actual `GetPlayerSlotFromObjID` is at `0x006a19a0` (formula matches the body decompile). objnotfound-requestobj-enterset-wire-format.md table corrected this pass; objcreate-serialization.md was correct. See objnotfound-requestobj-enterset-wire-format.md "Critical Correction: Function Address Map" section (C4). |
| 2 | TGBufferStream write primitives count | stream-primitives.md = 7 writes; python-messages.md = 8 writes (adds WriteBool / WriteLong / WriteCString) | python-messages.md (more complete); merge into stream-primitives.md |
| 3 | TGMessage layout, fields +0x2C/+0x30/+0x34 | transport-layer.md table 1 vs table 2 within same file ("retry_strategy" vs "num_retries", "base_delay" vs "backoff_time", "delay_factor" vs "backoff_factor") | Ghidra decompile of TGMessage constructor FUN_006b82a0 |
| 4 | Ship+0x2BC slot identity | wire-format-spec.md slot map says "(unused) NULL always"; subsystem-integrity-hash.md slot 11 says "Pulse Weapon System hashing at +0x40 / +0x2BC" | **CLOSED (2026-05-28, leaf #19):** binary truth — ship+0x2BC is **PulseWeaponSystem parent** (`HashWeaponSystem` slot 11). Wire-format-spec.md was already corrected in foundation pass §6.1 (the hub's slot map had Pulse/Tractor swapped at +0x2BC/+0x2D4); subsystem-integrity-hash.md's slot 11 reading was correct on +0x40/+0x2BC -> Pulse. Confirmed via decompile of `ComputeSubsystemIntegrityHash` (0x005b5eb0) + ground-truth from `Ship_LinkSubsystemToParent` (0x005b5030) switching on 0x802D -> ship+0x2BC. See subsystem-integrity-hash.md §C1 (corrected slot table). |
| 5 | Subsystem hash table duplication | wire-format-spec.md has its own 12-row hash order table; subsystem-integrity-hash.md is the dedicated doc | **CLOSED (2026-05-28, leaf #19):** subsystem-integrity-hash.md is canonical; foundation §6.1 retired the hub's duplicated Anti-Cheat Hash Field Offsets table in favor of a 1-line link to this leaf. The leaf's slot table is now v5-validated against the corrected ship-slot identities (foundation #1 C1 cascade applied as leaf C1). |
| 6 | Per-collision PythonEvent count | pythonevent-wire-format.md says "12-14 messages: 1 ObjectExploding + 11 ADD_TO_REPAIR_LIST + 2 delayed" but worked example shows "14: 1 ObjectExploding + 13 ADD_TO_REPAIR_LIST" | Re-derive from trace |
| 7 | TGEvent base vtable slot count | pythonevent-wire-format.md = 18 slots (0-17); engine family vtable doc baseline = 14 slots; collision-effect-protocol.md TGEvent vtable = 16 slots (ends at +0x40) | Ghidra vtable boundary check at 0x00895FF4 |
| 8 | CF16 doc overlap | cf16-precision-analysis.md and cf16-explosion-encoding.md duplicate algorithm + constants + scale table + mod round-trip analysis | **CLOSED (2026-05-28, leaves #20+#21):** addressed via cross-links rather than merge. Both docs retain the constants table + scale table + algorithm pseudocode for in-context reading (each doc must be self-sufficient at the reader's chosen entry point), but `int()` vs `round()` match strategies are split cleanly — #20 carries the `int() Match` column with FAIL rows; #21 carries the `round() Matches` column with YES/NO rows. Each doc cross-links to the other for the alternative strategy. ExplosionDamage 0x38-byte struct is rendered in both with explicit cross-link headers naming the sibling as the canonical source for the call-graph context. No merge needed — both docs `verified`. |
| 9 | Per-ship subsystem catalog cross-source | per-ship-subsystem-wire-format.md and stateupdate-subsystem-wire-format.md both list subsystem types but with different inventories | Use stateupdate-subsystem-wire-format as the type catalog; per-ship as per-class catalog |
| 10 | Direction-split claim location | stateupdate.md, stateupdate-subsystem-wire-format.md, and message-trace-vs-packet-trace.md all assert the SUB-vs-WPN by direction split with the same packet counts | stateupdate.md (canonical); others link |
| 11 | Subsystem field offsets at ship+0x280 family | stateupdate-subsystem-wire-format.md says +0x280 count, +0x284 head, +0x288 tail, +0x28C free list; stateupdate.md says subsystem list at +0x284 (head only) | Ghidra decompile of Ship_AddSubsystemToLists FUN_005b3e50 |
| 12 | Opcode 0x18 wire format | game-opcodes.md says "DeletePlayerAnim, Handler FUN_006A1420, plays animation" — no wire format | New leaf doc needed (delete-player-anim-wire-format.md exists in `OpenBC/docs/wire-formats/` already; mirror it on the BC side) |
| 13 | Factory 0x866 family | delete-player-ui-wire-format.md says "0x866 = base TGEvent"; tgobjptrevent-class.md's factory-table top is 0x02 = TGEvent; the 0x8xx family is `0x8129 = ObjectExplodingEvent` | **CLOSED (2026-05-28, leaf #17):** 0x866 lives in the **TGFactory registry** (`DAT_0099a578` / `DAT_0099a584`), a **second class registry separate from NiRTTI** used exclusively by `TGFactory_DeserializeObject` (0x006D6200). 0x866 is a TGEvent subclass (vtable 0x00895848, size 0x2C), NOT base TGEvent. Confirmed siblings: 0x801, 0x865, 0x867. Full TGFactory enumeration deferred to downstream pass. See delete-player-ui-wire-format.md "Two-Registry Architecture" section. |
| 14 | objnotfound-requestobj-enterset doc not indexed | The doc exists at `docs/protocol/objnotfound-requestobj-enterset-wire-format.md` but is not listed in `docs/protocol/README.md` (the README table has 18 docs; this is doc 19) | Add to README in v5 close batch |
| 15 | Breadcrumb header inconsistency | objnotfound-requestobj-enterset-wire-format.md lacks the `> [docs](../README.md) / [protocol](README.md) /` breadcrumb header that all siblings have | **CLOSED (2026-05-28, leaf #18):** breadcrumb added in v5 render pass. |
| 16 | SpeciesToShip table duplication | game-opcodes.md (15 playable rows) and objcreate-serialization.md (45 rows) | objcreate-serialization.md canonical; game-opcodes.md keeps short list + link |
| 17 | Opcode 0x06 worked-example accuracy | pythonevent-wire-format.md's "exactly 12-14 PythonEvents per collision" — 12-14 doesn't quite match either of the example breakdowns in the same doc | Re-derive from packet trace |
| 18 | Receiver address for explosion in cf16 docs | Both cf16-precision-analysis.md and cf16-explosion-encoding.md cite Handler_Explosion_0x29 at 0x006A0080 (consistent across CF16 family); game-opcodes.md also = 0x006A0080. OK, this is consistent. (No disagreement; noted as positive cross-anchor.) |  | — |
| 19 | 5th CF16 encoder caller identity (OQ1 from cf16-precision-analysis leaf #20) | cf16-precision-analysis.md cites a 5th xref to FUN_006d3a90 at 0x005a2b3b inside a Ghidra-undefined function (~0x005a2800-0x005a3000). The function is gated by `TEST BL,0x10` (same flag-0x10 speed bit as Ship__WriteStateUpdate) and preceded by `FMUL float ptr [0x0088d4e4]` (unit-conversion multiplier). Hypothesis: a non-Ship state-writer (torpedo/projectile). Documented at the field+gate+call-site level; only the parent function identity is open. | Decompile + name the parent function at the prologue. Non-blocking for CF16 docs. |
| 20 | Informal Python-message label drift (OQ1 from message-trace-vs-packet-trace leaf #22) | message-trace-vs-packet-trace.md labels the S->C-only block `0x35 GameState` / `0x37 PlayerRoster`; mid #6 python-messages.md names these `MISSION_INIT_MESSAGE` (0x35) and `SCORE_MESSAGE` (0x37). The trace labels are functionally accurate but informal. | Sync the cross-source doc's labels with the python-messages.md canonical names. Non-blocking. |
| 21 | 0x0D PythonEvent2 re-emit path (OQ2 from message-trace-vs-packet-trace leaf #22) | 2026-02-10 trace shows opcode 0x0D C->S=12 with S->C=0. Leaf #14 pythonevent-wire-format.md notes FUN_0069F880 is LOCAL-ONLY and handles both 0x06 and 0x0D. Open: do those 12 received 0x0D events re-emit outbound as opcode 0x06 (inflating the S->C 0x06=251 count), or does the engine drop them after the local apply step? | (a) bisect the S->C 0x06 stream for a 12-event burst correlated with the C->S 0x0D arrivals; or (b) emulate FUN_0069F880 with a 0x0D input and watch for outbound 0x06. Non-blocking. |

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

### 6.5 checksum-opcodes.md — 2026-05-28 (game-archaeology-specialist)

**Status:** validated -> `partial` (2 material corrections + 3 refinements applied;
1 open question on the round-0xFF sender keeps the doc from promoting to verified).

**Methodology:** Per-doc workflow Phases 1-3 with `program: STBC.exe` on every MCP call.
~35 load-bearing claims; the NetFile dispatcher and its 11 helper functions were
walked end-to-end. Many anchors inherited from
[decompiled-functions.md](../engine/decompiled-functions.md) — the cross-anchor density
made this pass fast.

**Headline:** the doc had two **material errors** plus several refinements. The
0x22/0x23 dialog mapping was SWAPPED in the prior doc; the "5th round at index 0xFF
for Scripts/Multiplayer" was a fabrication that conflated a real wire observation
(the 0xFF round IS sent in production traces) with a non-existent in-binary sender.
Scripts/Multiplayer IS checksummed during the handshake — but as part of round 0's
reference-hash bundle via `FUN_006A6630`, not a separate round.

**Functions touched (completeness):**

| Function | Addr | effective_score | Used to verify |
|----------|------|-----------------|----------------|
| NetFile dispatcher | 0x006A3CD0 | 0.6 / 83.1 max | Non-contiguous opcode catalog {0x20, 0x21, 0x22, 0x23, 0x25, 0x27}; 0x24/0x26 absent; 0x28 outbound-only |
| ChecksumRequestSender | 0x006A3820 | 0.0 / 81.9 | 4-iteration loop bound (`while uVar9 < 4`); 4 round directories on stack |
| ChecksumRequestBuilder | 0x006A39B0 | 0.0 / 81.9 | Wire format `[0x20][idx][u16 dir_len][dir][u16 fil_len][fil][bit recursive]`; reliable flag msg+0x3A=1 |
| 0x21 response router | 0x006A4260 | 0.0 / 83.1 | `byte[1] != 0xFF` -> FUN_006A4560; 0xFF inline branch is reserved |
| Per-round verifier | 0x006A4560 | 0.0 / 81.9 | Two-arm dispatch into FUN_006A4A00 (param_4=0 file mismatch / param_4=1 ref mismatch); success arm posts via FUN_006A4BB0 |
| Fail-message sender | 0x006A4A00 | 0.0 / 81.9 | param_4==0 -> WriteChar(0x22) + filename; param_4!=0 -> WriteChar(0x23) + PTR_DAT_008d9af4. Posts event 0x008000E7 |
| 0x22/0x23 receiver | 0x006A4C10 | 0.0 / 83.1 | `(char)iVar2 == '\"'` (0x22) -> SystemChecksumFail; else (0x23) -> VersionDifferent. Sets DAT_0097fa78+0x100 = 0x65 (disconnect) |
| Success poster | 0x006A4BB0 | 5.1 / 84.8 | Posts event 0x008000E8 (18-line function) |
| 0x20 client receiver | 0x006A5DF0 | 0.0 / 83.1 | Round-0 path runs FUN_006A6630; response prepends int32 reference hash |
| Reference-hash bundler | 0x006A6630 | 0.0 / 80.5 | 4 extra checksums (Autoexec, Scripts/ships, Scripts/Systems, Scripts/Multiplayer) into a single int32 |
| 0x25 receiver | 0x006A3EA0 | 0.0 / 80.5 | One-shot warning gated on this+0x14; reimports `Scripts/*.pyc`; always responds 0x27 |
| 0x27 receiver | 0x006A4250 | 13.1 / 100 | Thin wrapper to FUN_006A5860 (correctly classified) |
| FileTransferProcessor | 0x006A5860 | 0.0 / 80.5 | Drains per-peer queue; on empty sends single-byte 0x28 + posts event 0x008000E6 |
| ChecksumCompleteHandler | 0x006A1B10 | 0.0 / 81.9 | Consumes event 0x008000E6; sends Settings (0x00) + GameInit (0x01) reliable |

No annotations applied this pass; the dispatcher's downstream helpers all carried
their FUN_xxxxxxxx names. The completeness scores reflect un-annotated state, not
unverifiability — every behavior was tractable from decompile output.

**Confirmed claims (high confidence):** 32 anchors.

- NetFile dispatcher accepts non-contiguous opcodes {0x20, 0x21, 0x22, 0x23, 0x25, 0x27}.
  0x24 and 0x26 have no handler. 0x28 is outbound-only (no dispatcher case) — confirms
  the transport-layer.md C2 catalog.
- Per-opcode handler addresses (0x20 -> 0x6A5DF0, 0x21 -> 0x6A4260, 0x22/0x23 -> 0x6A4C10,
  0x25 -> 0x6A3EA0, 0x27 -> 0x6A4250). 0x28 sender at 0x6A5860.
- 0x21 routing: `byte[1] != 0xFF` -> FUN_006A4560; `byte[1] == 0xFF` reserved inline.
- ChecksumRequestSender FUN_006A3820 builds 4 requests (indices 0..3) and queues all in
  hash table B before sending #0.
- ChecksumRequestBuilder FUN_006A39B0 wire format with bit-packed recursive flag and
  `msg+0x3A = 1` reliable.
- Hash table B at NetFile+0x38 (vtable) and NetFile+0x44 (buckets) — cross-confirms
  decompiled-functions.md NetFile ctor description.
- Event ID anchoring with the 2-xref pattern (producer + FUN_0069E590 registration):
  0x008000E6 (FUN_006A5860 after 0x28), 0x008000E7 (FUN_006A4A00 fail), 0x008000E8
  (FUN_006A4BB0 success).
- Client round-0 reference hash includes Autoexec, Scripts/ships, Scripts/Systems,
  Scripts/Multiplayer via FUN_006A6630; result is prepended to round-0 response.
- ChecksumCompleteHandler FUN_006A1B10 consumes event 0x008000E6 and sends Settings +
  GameInit; Settings flag fields use `WriteBool_Bit` (confirms wire-format-spec C1).

**Corrected claims:**

1. **C1 — 0x22 / 0x23 dialog mapping is SWAPPED (material).**
   - Old: 0x22 = VersionDifferent dialog; 0x23 = SystemChecksumFail dialog.
   - **New: 0x22 = SystemChecksumFail dialog; 0x23 = VersionDifferent dialog.**
   - Evidence: FUN_006A4C10's `(char)iVar2 == '\"'` (0x22) branch routes to
     `s_SystemChecksumFail_0095a434`; the else (0x23) routes to
     `s_VersionDifferent_0095a420`. Sender FUN_006A4A00 confirms: `param_4 == 0`
     writes 0x22 with per-file filename (per-file mismatch); `param_4 != 0` writes
     0x23 with `PTR_DAT_008d9af4` (App.pyc reference-hash mismatch).
   - This is a clean opposite-mapping correction; clean-room implementations need it.

2. **C2 — "5th round at index 0xFF = Scripts/Multiplayer" is a fabrication (material).**
   - Old: 5 rounds with index 0xFF for `Scripts/Multiplayer/*.pyc` recursive.
   - **New: 4 rounds (indices 0..3). `Scripts/Multiplayer` IS checksummed during the
     handshake but as part of round 0's reference-hash bundle via FUN_006A6630, NOT
     as a separate round.**
   - Evidence: FUN_006A3820 loops `while (uVar9 < 4)` — the bound is decisive. The
     four directories on the function's stack literals are App.pyc, Autoexec.pyc,
     scripts/ships *.pyc (recursive), scripts/mainmenu *.pyc. FUN_006A6630 (called
     from FUN_006A5DF0 when index == 0) computes 4 extra checksums and folds them
     into a single int32 reference hash that the round-0 response prepends.
   - **Important caveat:** the 0xFF code path IS reserved in FUN_006A4260's receive
     dispatch, and packet traces from `openbc-test-20260225.md` show a real
     `ChecksumReq(round 0xFF)` message on the wire. So the 0xFF round exists in
     production — but the in-binary sender is **not located** via FUN_006A39B0
     caller analysis. Tracked as open question OQ1.

**Refinements:**

3. **C3 — 0x25 dialog timing.** Clarified: the "Receive File Warning" dialog is a
   **one-shot** — fires on the FIRST 0x25 receive only (when `this+0x14 == 0`), not
   on every transfer. The handler sets `this+0x14 = 1` and skips the dialog on all
   subsequent 0x25s in the same session.
4. **C4 — 0x21 payload structure.** Old: "variable opaque hash_data". **New:**
   `[if idx==0: int32 reference_hash][int32 dir_or_file_hash][optional file-list via
   FUN_006A6190]`. FUN_006A6190 walks a tree and joins per-file hashes with a `/`
   separator (DAT_008DACA0).
5. **C5 — Trace-vs-binary tagging.** The "~400 bytes round 2 response" observation
   is tagged `[cross-source-2026-02-25 trace]` rather than presented as a
   binary-derived claim — it's a wire observation from openbc-test-20260225.md.

**Dropped claims:**

1. **D1 — "0xFF = final round, Scripts/Multiplayer, handled by main path."** Dropped.
   The semantic attribution is unanchored: the 0xFF reserved branch exists in the
   receiver but no in-binary sender for 0xFF was located, and Scripts/Multiplayer is
   in fact bundled into round 0 via FUN_006A6630. The wire observation is preserved
   as OQ1.
2. **D2 — "FUN_006A4260 -> FUN_006A4560 (verify) or FUN_006A5570 (mismatch)."** Dropped.
   FUN_006A5570 is NOT the mismatch peer to FUN_006A4560 — it's called from FUN_006A5660
   (queue management). The true mismatch path is FUN_006A4560 -> FUN_006A4A00 (which
   then sends 0x22 or 0x23 based on `param_4`). The file-enqueue / 0x25 transfer chain
   sits on a separate branch (FUN_006A4E70 -> FUN_006A5660).

**New factual sections added:**

- **Top-of-doc NOTE block** stating partial status, the non-contiguous dispatcher
  catalog, the two material corrections, and the round-0xFF open question.
- **"Dispatcher" section** with explicit per-opcode missing-handler table (0x24, 0x26,
  0x28) — the negative claim for v5.
- **"Round 0 reference hash" subsection** documenting FUN_006A6630's role, replacing
  the dropped 5th-round table row.
- **"Round 0xFF on the wire" subsection** capturing OQ1 — the wire fact is
  authoritative; the binary sender is the gap.
- **"Opcode 0x28 - Outbound only" section** documenting FUN_006A5860 as sender,
  the single-byte payload, and the event 0x008000E6 chain to FUN_006A1B10.
- **"Event IDs" subsection** with the 3-row event/producer/consumer table.
- **"Open questions" section** capturing OQ1 (round-0xFF sender) + OQ2
  (PTR_DAT_008d9af4 init site).

**Companion follow-ups (deferred to those docs' own validation passes):**

- [decompiled-functions.md](../engine/decompiled-functions.md) — already verified;
  this pass confirms the FUN_006A4A00 / FUN_006A4BB0 fire sites that doc's "open
  question #3" flagged. The OQ closes from this side; decompiled-functions.md does
  not need a corrigendum since the question was forward-looking.
- [wire-format-spec.md](wire-format-spec.md) — already corrected; this doc inherits
  the WriteBool_Bit anchoring on FUN_006A1B10 (the Settings sender).
- [transport-layer.md](transport-layer.md) — already corrected (C2 cross-references
  this doc as the canonical NetFile opcode catalog); no further action needed.

**Open questions left for downstream rows:**

1. **OQ1 — Round-0xFF sender unlocated in the binary.** Static call-graph search from
   FUN_006A39B0 (the only known ChecksumRequestBuilder) finds only FUN_006A3820, which
   iterates 0..3. Packet traces from `openbc-test-20260225.md` show a real
   `ChecksumReq(round 0xFF)` on the wire, so the emission exists in production.
   Candidates: event handler registered by FUN_0069E590, deferred-init in NetFile
   ctor sequence, or OpenBC-side emission. Worth a dedicated dig. Trace evidence is
   authoritative for the wire fact.
2. **OQ2 — `PTR_DAT_008d9af4` initialization site.** The static bytes read as garbage,
   confirming runtime population. decompiled-functions.md describes it as the "App.pyc
   reference hash pointer" — defer to that doc's ctor/DllMain notes.

**Resolving OQ1 promotes this doc from `partial` -> `verified`.**

**Files touched:** docs/protocol/checksum-opcodes.md (re-rendered with v5 frontmatter,
top-of-doc NOTE block, dispatcher section with missing-handler table, 4-round table
replacing the 5-round fabrication, round-0xFF subsection, reference-hash bundle
subsection, IMPORTANT block on 0x22/0x23 swap, 0x28 outbound-only section, Event IDs
subsection, Open Questions section, cross-references). docs/protocol/v5-validation-status.md
(this row added; §2 row #5 status flipped to partial).

### 6.6 python-messages.md — 2026-05-28 (game-archaeology-specialist)

**Status:** validated -> `partial` (1 material correction on WriteCString length-prefix
width, 1 naming clarification on the wire-serialize entry, 3 cross-source tags
required on the Python-side handler list; the doc is overwhelmingly well-anchored —
this is the lowest-correction pass of the protocol family so far).

**Methodology:** Per-doc workflow Phases 1-3 with `program: STBC.exe` on every MCP call.
~80 load-bearing claims; all SWIG wrappers traced from format-string PUSH sites; the
ET_NETWORK_MESSAGE_EVENT receive-side dispatch confirmed end-to-end.

**Headline:** python-messages.md is the cleanest pre-v5 protocol doc validated to date.
The MAX_MESSAGE_TYPES = 0x2B constant init at 0x00654f31 is **byte-level confirmed**;
the SendTGMessage / SendTGMessageToGroup / TGMessage_Create / SetGuaranteed / SetDataFromStream
function addresses all match the binary; "NoMe" and "Forward" group-name strings at
0x008e5528 / 0x008d94a0 confirmed in-memory; the receive-side 6-step dispatch including
TGMessageEvent size 0x2C / ET_NETWORK_MESSAGE_EVENT = 0x60001 is **byte-level confirmed**
via TGWinsockNetwork::Update at 0x006b4788 (`MOV EBP, 0x60001`) + 0x006b4794 (`PUSH 0x2C`).

**Functions touched (completeness):**

| Function | Addr | effective_score | Used to verify |
|----------|------|-----------------|----------------|
| TGWinsockNetwork_SendTGMessage | 0x006b4c10 | 0.00 -> 29.07 | unicast/broadcast/special-mode targetID routing; peer binary-search at [this+0x2C]; 4/0xB error codes |
| TGWinsockNetwork_SendTGMessageToGroup | 0x006b4de0 | 6.62 -> 71.27 | group-table binary search at [this+0xF4]; strcmp loop; 0x10 not-found return |
| TGMessage_SetDataFromStream | 0x006b8a00 | 11.93 -> 78.27 | vtable+0xF4 (GetBuffer) + vtable+0xD8 (GetPos) + FUN_006b84d0 (BufferCopy) call chain |
| TGMessageEvent_Ctor | 0x006bfe80 | 0.00 -> 38.4 | size 0x2C verified at allocation site (0x006b4794 PUSH 0x2C); vtable PTR_FUN_0089580c; +0x28 message-ref slot zeroed |
| TGMessageEvent_AttachMessage | 0x006bff30 | n/a | stores TGMessage* at [this+0x28] with release-on-replace at vtable[1](1) |
| MultiplayerGame_Ctor | 0x0069e590 | 0.00 -> 5.39 | builds "NoMe" + "Forward" groups; ET_NETWORK_MESSAGE_EVENT 0x60001 handler registration; 11+ other event registrations (host-only conditional on DAT_0097fa8a) |
| MpgameHandleMessage | 0x0069f2a0 | 69.84 | dispatcher boundary verified: switch covers 0x02-0x2A only, no case >= 0x2C |
| (SWIG TGNetwork_SendTGMessage wrapper) | 0x005e3a70 | n/a (no fn entry) | format string `"OiO|i:TGNetwork_SendTGMessage"` at 0x0093846c; calls 0x006b4c10 |
| (SWIG TGNetwork_SendTGMessageToGroup wrapper) | 0x005e3b20 | n/a (no fn entry) | format string `"OOO:TGNetwork_SendTGMessageToGroup"` at 0x0093848c |
| (SWIG TGMessage_Create wrapper) | 0x005e13b0 | n/a (no fn entry) | format string `":TGMessage_Create"` at 0x00937c30; PUSH 0x40; CALL 0x00717b70 (alloc); CALL 0x006b82a0 (TGMessage_Ctor) -- confirms sizeof 0x40 |
| (SWIG TGMessage_SetGuaranteed wrapper) | 0x005e19c0 | n/a (no fn entry) | format string `"Oi:TGMessage_SetGuaranteed"` at 0x00937d30; SETNZ AL / MOV [ECX+0x3A], AL -- confirms +0x3A boolean field |

**Annotations applied this pass:** 6 function renames + 5 prototypes + 6 plate comments.

| Addr | Old | New | Prototype | Plate? |
|------|-----|-----|-----------|--------|
| 0x006b4c10 | FUN_006b4c10 | TGWinsockNetwork_SendTGMessage | `int __thiscall(void *, int, TGMessage *, int)` | yes |
| 0x006b4de0 | FUN_006b4de0 | TGWinsockNetwork_SendTGMessageToGroup | `int __thiscall(void *, char *, TGMessage *)` | yes |
| 0x006b4ec0 | FUN_006b4ec0 | TGWinsockNetwork_SendToGroup_Iterate | (none) | no |
| 0x006b8a00 | FUN_006b8a00 | TGMessage_SetDataFromStream | `void __thiscall(TGMessage *, void *)` | yes |
| 0x006b84d0 | FUN_006b84d0 | TGMessage_BufferCopy | (none) | no |
| 0x006bfe80 | FUN_006bfe80 | TGMessageEvent_Ctor | `void * __fastcall(void *)` | yes |
| 0x006bff30 | FUN_006bff30 | TGMessageEvent_AttachMessage | `void __thiscall(void *, TGMessage *)` | yes |
| 0x0069e590 | FUN_0069e590 | MultiplayerGame_Ctor | (none) | yes |

**Confirmed claims (high confidence):** ~75 anchors.

- **MAX_MESSAGE_TYPES = 0x2B at 0x0090b490, SWIG init at 0x00654f31.** Verified at byte level:
  `c70590b490002b000000` = `MOV dword ptr [0x0090b490], 0x2b`. The SWIG-globaltable name-slot
  pointer `0x00952cf8` ("MAX_MESSAGE_TYPES") is stored 10 bytes earlier at `0x00654f27`.
- **SendTGMessage at 0x006b4c10** with targetID semantics:
  - `targetID == -1` → resolves peer via FUN_006bb9d0(optional_arg), queues to that peer; returns 0xB on lookup fail.
  - `targetID > 0` → binary-search [this+0x2C] peer array (count [this+0x30]) sorted by [peer+0x18]; fallback to [this+0x20] (local-player peer ID) before returning 0xB.
  - `targetID == 0` → iterates entire [this+0x2C] peer array; for each peer with `[peer+0xBC] != 1` (not disconnected), Clone-and-enqueue via vtable[6]; last peer reuses caller's message.
- **SendTGMessageToGroup at 0x006b4de0** with group-table binary search at [this+0xF4] (count [this+0xF8]) sorted by group-name string at [entry+0x04]; strcmp via unrolled 2-bytes-at-a-time loop at 0x006b4e22; calls FUN_006b4ec0 (now `TGWinsockNetwork_SendToGroup_Iterate`) on found group; returns 0x10 on not-found.
- **"NoMe" group name at 0x008e5528** + **"Forward" group name at 0x008d94a0** — both strings inspected in-memory; null-terminated.
- **MultiplayerGame_Ctor at 0x0069e590 creates both groups when DAT_0097fa78 (TGWinsockNetwork singleton) and DAT_0097fa8a (g_IsMultiplayer) are non-zero.** Each group is a 0x14-byte allocation with vtable `PTR_FUN_00894684`, strcpy-style name copy, then FUN_006b70d0 (group register) on TGNetwork's group table.
- **ET_NETWORK_MESSAGE_EVENT = 0x60001** confirmed at three independent sites:
  - MultiplayerGame_Ctor at 0x0069e590 registers `FUN_006db380(0x60001, ..., s_MultiplayerGame____ReceiveMessag_0095a218, 1, 1, ...)`.
  - TGWinsockNetwork::Update at 0x006b4788 sets `MOV EBP, 0x60001`, the event-type written at [event+0x10].
  - Receiver path (TGMessageEvent created, message attached, posted to FUN_006d62b0).
- **TGMessageEvent sizeof = 0x2C** verified at 0x006b4794: `PUSH 0x2C` (allocation size pushed to FUN_00717b70).
- **TGMessageEvent ctor at 0x006bfe80**: installs vtable `PTR_FUN_0089580c`, zeros [+0x28] (message-ref slot).
- **TGMessageEvent::AttachMessage at 0x006bff30** stores TGMessage* at [this+0x28], releases prior reference via vtable[1](1) on replace.
- **TGMessage_Create at 0x005e13b0** allocates 0x40 bytes via FUN_00717b70 + FUN_00718010 pool, then calls TGMessage_Ctor at 0x006b82a0 (foundation #3 confirmed sizeof 0x40).
- **SetGuaranteed at 0x005e1a18** writes `byte [TGMessage+0x3A] = (param != 0) ? 1 : 0` (SETNZ AL pattern) — confirms the `+0x3A` reliable-flag field.
- **SetDataFromStream at 0x006b8a00** calls stream vtable+0xF4 (GetBuffer at [+0x1C]) and vtable+0xD8 (GetPos at [+0x24]), then BufferCopy at FUN_006b84d0 — exactly as doc claims.
- **MpgameHandleMessage dispatcher boundary** (range check `0x02-0x2A` bias-decoded) confirmed: switch has no case for opcodes >= 0x2C; opcodes 0x2C+ fall through silently.
- **Receive-side dispatch chain (6 steps)** end-to-end byte-traced:
  1. ReceivePacket FUN_006b95f0 — exists, named.
  2. ProcessIncomingPackets FUN_006b5c90 — exists, named (note: name is `ProcessIncomingPackets`, not `ProcessIncomingMessages` as doc says — see C2 below).
  3. TGMessage factory Type 0x32 at FUN_006b83f0 — exists, named.
  4. Dequeue FUN_006b52b0 — exists.
  5. TGWinsockNetwork::Update FUN_006b4560 wraps each into a TGMessageEvent; sets event type to 0x60001; calls AttachMessage; PostEvent via FUN_006d62b0.
  6. C++ handlers (MultiplayerGame, NetFile, MultiplayerWindow) each registered on 0x60001 read first payload byte.
- **TGBufferStream write primitives** all match (foundation #2 verified): WriteByte 0x006cf730 / WriteShort 0x006cf7f0 / WriteInt 0x006cf830 / WriteLong 0x006cf870 / WriteFloat 0x006cf8b0 / WriteBool 0x006cf7a0 / WriteBytes 0x006cf2b0 — addresses + vtable offsets + byte counts confirmed.
- **CHAT_MESSAGE byte-by-byte wire example walkthrough** is internally consistent: payload `2C 02 00 00 00 05 00 68 65 6C 6C 6F` (12 bytes) wraps as type-0x32 with `flags_len=0x800F` (bit 15 reliable, bits 0-12 size=15) + 16-bit seq + payload — matches TGBufferStream_Serialize (foundation-#2 wire-container Serialize) byte layout exactly.

**Corrected claims:**

1. **C1 — WriteCString length prefix is uint32 LE, not uint16 LE (material).**
   - Doc line 94: `WriteCString(s) | +0x24 (0x006cf460) | 2+N bytes | [uint16 LE strlen] [raw chars, NO null]`
   - Reality: FUN_006cf460 decompiles as `for(i = 0; param_2[i] != 0; i++); vtable[+0x6c](i); vtable[+0x14](param_2, i);` — slot +0x6c is **WriteLong** (4-byte int, FUN_006cf870), NOT slot +0x5C (WriteShort).
   - Result: wire format is `[uint32 LE strlen] [raw chars, NO null]` = **4+N bytes**, not 2+N.
   - **Important**: Stock BC's mod code uses explicit `WriteShort(len) + Write(buf, len)` (as the CHAT_MESSAGE example shows), NOT WriteCString. So this correction does NOT invalidate the CHAT_MESSAGE example or any stock-trace observation. Mods/scripts that called WriteCString directly would have used a uint32 prefix.
   - Cross-source check needed: the relay-audit memory's CHAT_MESSAGE / TEAM_CHAT relay observations are unaffected (they use the explicit `WriteShort + Write` pattern, not WriteCString).

2. **C2 — Step 4 of Receive Side Dispatch names TGMessage::WriteToBuffer for FUN_006b8340; binary names it TGBufferStream::Serialize.**
   - Doc line 140: "This payload is serialized by `TGMessage::WriteToBuffer` (`FUN_006b8340`) into a type 0x32 transport message"
   - Reality: Ghidra DB has FUN_006b8340 named `TGBufferStream_Serialize` (the wire-container class's Serialize method, vtable[2] of the 0x40-byte class at 0x006B82A0).
   - Caveat: per the stream-primitives memory + transport-layer correction C4, the 0x40-byte class is now confirmed as **TGMessage** (not "TGBufferStream wire-container"). So `FUN_006b8340 IS TGMessage::Serialize` (vtable[2]). The doc's naming "WriteToBuffer" is descriptive of behavior but the canonical method name is `Serialize` per foundation #2/#3.
   - Resolution: replace "TGMessage::WriteToBuffer" with "TGMessage::Serialize" throughout. The wire-format walkthrough below it is correct — class tag 0x32 / flags_len with bit-15 reliable / 16-bit seq / payload — and matches the decompile byte-for-byte.

3. **C3 — Receive-side dispatch step 2 names "ProcessIncomingMessages"; binary names it "ProcessIncomingPackets".**
   - Doc line 194: "ProcessIncomingMessages (FUN_006b5c90)"
   - Reality: Ghidra has it named `TGWinsockNetwork_ProcessIncomingPackets` (renamed by transport-layer validation).
   - Resolution: rename in doc to match the Ghidra symbol — `ProcessIncomingPackets`.

**Cross-source-tagged claims (mark with `[cross-source-2026-02-24 trace]` -> relay-audit memory):**

These three are cross-source observations from the Cady/XFS01 21-min trace; they corroborate
the doc's routing claims but are NOT binary-derived:

4. **0x2C CHAT_MESSAGE 1:2 echo (relayed to ALL clients including sender).** Doc line 211
   ("CHAT_MESSAGE 0x2C - MultiplayerMenus") doesn't explicitly state the relay semantics, but
   tgmessage-routing.md (the sibling) does. Tag as [cross-source-2026-02-24 trace].
5. **0x36 SCORE_CHANGE always paired (sent to ALL clients simultaneously) — 10 S->C observed.**
   Doc line 46 lists `SCORE_CHANGE_MESSAGE = 54 = 0x36 MissionShared`. The "always paired" /
   "1:N broadcast" routing semantic is a trace observation. Tag as [cross-source-2026-02-24 trace].
6. **0x37 SCORE_MESSAGE per-join roster update (6 S->C observed; doc reaches 0x37 as
   "full score sync" implicitly).** Tag as [cross-source-2026-02-24 trace].

These are NOT corrections — the doc isn't wrong about routing; it just doesn't carry the
empirical evidence inline. Adding cross-source tags makes the provenance explicit.

**Dropped claims:** None. Every claim survived validation in some form.

**Cross-doc consistency check:**

- **foundation #2 stream-primitives.md** — fully consistent: WriteByte/Short/Int/Long/Float/Bool/Bytes all at the addresses python-messages.md cites. The two docs agree on field offsets +0x1C buffer / +0x20 capacity / +0x24 cursor (cursor = "position" in stream-primitives vocab). The 7-vs-8-row write-table discrepancy from §4 #2 is RESOLVED: python-messages.md's 8-row table is the correct superset (adds WriteBool, WriteLong, WriteCString — the last with the C1 correction above).
- **foundation #3 transport-layer.md** — fully consistent: TGMessage sizeof 0x40, vtable 0x008958d0, ctor TGMessage_Ctor at 0x006b82a0. C4 of transport-layer (TGMessage naming throughout) already absorbed; python-messages.md inherits.
- **mid #4 game-opcodes.md** — fully consistent: MpgameHandleMessage at 0x0069f2a0 owns 0x02-0x2A; python-messages.md's claim that "opcodes 0x2C+ bypass the C++ dispatcher" is the negative complement of game-opcodes.md's coverage statement. Both agree on the dispatcher boundary.
- **wire-format-spec.md** — fully consistent: opcode constants 0x2C-0x39 in the Python-Level Messages section of CLAUDE.md match python-messages.md's table.
- **CLAUDE.md TopWindow drift (0x0097e238 = PlayWindow not TopWindow)** — does NOT apply to python-messages.md. The doc never cites 0x0097e238.

**New factual sections added (for documentation-writer):**

- **Top-of-doc NOTE block** stating partial status, the WriteCString length correction (C1), and the cross-source-tagged routing observations.
- **Annotation table** (the 6 renames + 5 prototypes + 6 plate comments from this pass).
- **"SWIG wrapper -> real function" cross-reference table** listing the 5 SWIG wrappers (SendTGMessage / SendTGMessageToGroup / TGMessage_Create / SetGuaranteed / SetDataFromStream) and their format strings + real targets. Currently scattered through the doc body; consolidating helps clean-room implementers.

**Companion follow-ups (deferred to those docs' own validation passes):**

- **tgmessage-routing.md** (row #7) — receives anchor confirmation for SendTGMessage / SendTGMessageToGroup / BroadcastToOthers / SendToGroupMembers; also inherits the "NoMe" / "Forward" group identity.
- **stream-primitives.md** (already partial) — should pick up the corrected WriteCString length-prefix width (4 bytes, not 2) in its write-primitives table. Cross-doc disagreement #2 is RESOLVED in python-messages.md's favor (its 8-row table is correct except for the WriteCString row).
- **wire-format-spec.md** (already partial) — should drop the Python-Level Messages summary table's claim that 0x35 "GameState" = MISSION_INIT_MESSAGE without anchoring the Python-side constant name. The doc's 11-row constants table (lines 41-51) is sourced from Python script imports (MultiplayerMenus, MissionShared, Mission5), NOT from the binary, so the numeric values 0x2C-0x41 are binary-correct (just message-type bytes on the wire) but the **names** (CHAT_MESSAGE, MISSION_INIT_MESSAGE, etc.) are Python-side. Mark the table as [python-source: scripts/MissionShared.py, scripts/MultiplayerMenus.py, scripts/Mission5/].

**Open questions left for downstream rows:**

1. **OQ1 — TGMessageEvent vtable PTR_FUN_0089580c slot layout unknown.** Used by `AttachMessage` (vtable[1] for release) but no other slots verified. Belongs to a TGMessageEvent class-layout pass under the engine family if/when one is undertaken.
2. **OQ2 — The "Python ProcessMessageHandler" claim is unanchorable from the binary alone.** The doc lists 6 handlers registered on ET_NETWORK_MESSAGE_EVENT (3 C++ + 3 Python). The 3 C++ handlers (MultiplayerGame / NetFile / MultiplayerWindow) are anchored. The 3 Python ones (MissionShared.ProcessMessageHandler / MultiplayerMenus.ProcessMessageHandler / mission-specific) live in `reference/scripts/*.py` and are out of scope for this validation pass. Documentation-writer should re-render those 3 rows with a `[python-source]` tag pointing readers to the script-side handler implementations. Verification would require Python-corpus inspection, which is policy-allowed but explicitly de-scoped here.
3. **OQ3 — 0x35 MISSION_INIT_MESSAGE vs "GameState" name conflict.** The relay-audit memory calls 0x35 "GameState"; this doc calls it `MISSION_INIT_MESSAGE`. Both refer to the same byte (0x35), but the Python-constant name is in MissionShared.py per this doc, while the relay-audit observation tagged it from packet-trace heuristic. Resolution: the doc's Python-source name is canonical; relay-audit's "GameState" was a working label. Document the resolution.
4. **OQ4 — SendTGMessage `targetID == -1` "optional 4th param" semantics.** The doc states this is a special mode; the decompile shows it calls FUN_006bb9d0(param_4) to resolve a peer object. The exact semantic (peer-handle ID? in-flight message slot? something else?) needs a FUN_006bb9d0 deep-dive — deferred to a tgmessage-routing.md / transport-layer.md follow-up.

**Files touched:** docs/protocol/v5-validation-status.md (this row added; §2 row #6 status flipped to partial). docs/protocol/python-messages.md NOT modified this pass — the documentation-writer agent will re-render with the v5 frontmatter, top-of-doc NOTE block, body corrections (C1 / C2 / C3), cross-source tags on the 3 routing claims, Python-source tag on the constants table, annotation summary, and explicit cross-links to transport-layer / stream-primitives / game-opcodes / tgmessage-routing.

### 6.7 tgmessage-routing.md — 2026-05-28 (game-archaeology-specialist)

**Status:** validated -> `partial` (3 material corrections + 2 minor; 3 open questions
including the chat 1:2 mystery; doc-render headlined the "three not two" architectural
reframe).

**Methodology:** Per-doc workflow Phases 1-3 with `program: STBC.exe` on every MCP call.
~90 load-bearing claims; the C++ side (factory table, factories, SendTGMessage 3-mode,
SendTGMessageToGroup, SendToGroup_Iterate, dispatcher boundary, per-handler relay) is now
end-to-end byte-anchored. Cross-source corroboration from the
`network-protocol-analyst/relay-audit-20260224.md` memory (21-min Cady/XFS01 stock-dedi
session) tagged `[cross-source-2026-02-24 trace]`.

**Headline:** the architectural reframe from "two relay mechanisms" to **three routing
mechanisms** is the doc's load-bearing correction. The pre-v5 doc framed relay as a
transport-level automatic property; the binary doesn't work that way - relay is **per
game-opcode handler**, mediated by the `Forward` and `NoMe` groups (both C++ created),
with a separate connect-event broadcast handling transport-level connection coordination.

**Functions touched (completeness):**

| Function | Addr | effective_score | Used to verify |
|----------|------|-----------------|----------------|
| TGWinsockNetwork_Ctor | 0x006B3A00 | high | factory-table population (7 slots); group-table init at network+0xF4 |
| TGWinsockNetwork_SendTGMessage | 0x006B4C10 | 29.07 | three-mode router; targetID == -1 (FUN_006BB9D0 lookup); targetID > 0 (binary search by peer+0x18); targetID == 0 (broadcast loop) |
| TGWinsockNetwork_SendTGMessageToGroup | 0x006B4DE0 | 71.27 | binary-search group table at network+0xF4 by group+0x4 name; 0x10 not-found return |
| TGWinsockNetwork_SendToGroup_Iterate | 0x006B4EC0 | high | iterates group+0x8 / group+0xC member array; per-member binary-search lookup; vtable[6] Clone |
| TGWinsockNetwork_ProcessIncomingPackets | 0x006B5C90 | high | wire-to-factory dispatch; never examines game opcode |
| TGWinsockNetwork_HandleConnect | 0x006B63A0 | high | NOT a game-data relay; parses peer ID, registers via FUN_006B7410, raises 0x60007, calls FUN_006B51E0 to broadcast the connect event |
| TGMessage_Factory_Type0x00 | 0x006BC6A0 | high | 14-bit length mask; opaque BufferCopy |
| TGMessage_Factory_Type32 | 0x006B83F0 | high | 13-bit length mask + bit-13 fragment flag |
| TGBufferStream_GetBufferAndSize | 0x006B8530 | high | 2-output accessor: returns *(void**)(this+4) AND writes size to *out (NOT "GetData") |
| MultiplayerGame_Ctor | 0x0069E590 | 5.39 | builds `NoMe` (string xref at 0x0069E6FA) and `Forward` (xref at 0x0069E716) groups - C++, not Python |
| MpgameHandleMessage | 0x0069F2A0 | 69.84 | class-tag gate `vtable[0]() == 0x32`; bias-decoded jump table at 0x0069F534 |
| FUN_0069F880 (PythonEvent handler) | 0x0069F880 | high | shared by 0x06 AND 0x0D via wrapper at 0x0069F3F1; LOCAL ONLY (no SendToGroup) |
| FUN_0069FDA0 (GenericEventForward) | 0x0069FDA0 | high | the per-handler relay pattern - Clone + SendToGroup(`Forward`) |
| FUN_0069F930 (TorpedoFire handler) | 0x0069F930 | high | same Clone + SendToGroup(`Forward`) pattern |
| FUN_006A01B0 (HostMsg handler) | 0x006A01B0 | high | no SendToGroup call - canonical non-relay example |
| MultiplayerWindow_Dispatch | 0x00504C10 | high | byte compares for 0x00, 0x01, 0x16 only |
| (SWIG TGNetwork_RegisterMessageType wrapper) | 0x005E4860 | high | `AND EAX, 0xFF; MOV [EAX*4 + 0x009962D4], EDX` - byte-level proof natural-wrap mask |

**No annotations applied this pass** - the dispatcher recovery + python-messages.md
validation pass had already renamed every function in scope. SWIG `TGNetwork_RegisterMessageType`
remains a bare wrapper (no Ghidra entry) located by format-string xref.

**Confirmed claims (high confidence):** 15 anchors per evidence rows.

- Transport factory table at `DAT_009962D4` (256 entries, 7 populated) - all 7 ctor +
  registration-fn pairs byte-confirmed.
- `RegisterMessageType` mask-and-store sequence: byte-level proof in the SWIG wrapper.
- Type-0x00 factory: 14-bit length mask, opaque BufferCopy, no fragment support.
- Type-0x32 factory: 13-bit length mask + bit-13 fragment flag.
- SendTGMessage 3-mode router:
  - Mode A (targetID == -1) -> `LEA ECX, [ESI+0x28]; CALL FUN_006BB9D0(nOptional)`;
    walks peer array looking for `peer+0x1C == nOptional`.
  - Mode B (targetID > 0) -> binary-search by `peer+0x18` with localID fallback.
  - Mode C (targetID == 0) -> broadcast loop with vtable[6] Clone per peer except last,
    skip `peer+0xBC == 1`.
- SendTGMessageToGroup binary-searches group table at `network+0xF4` by `[entry+0x04]`
  group-name string.
- SendToGroup_Iterate iterates `group+0x8` / `group+0xC` member array.
- `NoMe` and `Forward` group-name strings at `0x008E5528` and `0x008D94A0`; both
  built by `MultiplayerGame_Ctor` (xrefs at `0x0069E6FA` and `0x0069E716`). C++ creation
  proven; Python only USES them via SWIG SendTGMessageToGroup.
- Dispatcher class-tag gate + bias-decoded jump table (41 entries, opcodes 0x02-0x2A).
- 0x06 AND 0x0D both route to `FUN_0069F880` via the SAME wrapper at `0x0069F3F1` -
  LOCAL ONLY; no SendToGroup in body.
- The 12 opcodes routed to `FUN_0069FDA0` (StartFiring 0x07, StopFiring 0x08, etc.) +
  TorpedoFire 0x19 (FUN_0069F930) implement the per-handler relay pattern explicitly.
- HostMsg 0x13 (FUN_006A01B0) is the canonical non-relay handler.
- MultiplayerWindow dispatcher uses explicit byte compares for 0x00 / 0x01 / 0x16.

**Corrected claims (3 material + 2 minor):**

1. **C1 (material) - "Host Relay Path - Opaque Forwarding" section misattributes the
   mechanism.** The pre-v5 doc claimed `FUN_006B63A0` is the type-0x00 game-data relay
   path. The body of `FUN_006B63A0` is actually the **connect-event handler**: parses
   peer ID, registers peer via `FUN_006B7410`, raises event 0x60007. The `FUN_006B51E0`
   call inside it broadcasts the **connect event**, not game data. The TRUE game-data
   relay is per-handler: handlers like `FUN_0069FDA0` explicitly Clone the message and
   call `SendToGroup("Forward")` to relay. Replaced the entire pre-v5 section with the
   "Per-Handler Relay Pattern" section grounded in the FUN_0069FDA0 disassembly.

2. **C2 (material) - `NoMe` group attribution.** Pre-v5 doc claimed Python creates the
   `NoMe` group. Reality: it's created by **C++ `MultiplayerGame_Ctor` at 0x0069E590**,
   with the string xref at 0x0069E716 (and `Forward` at 0x0069E6FA - both groups built
   in the same ctor body, gated on `DAT_0097FA8A && DAT_0097FA78`). Python uses the
   group via SWIG SendTGMessageToGroup but does not create it.

3. **C3 (material) - "Two relay mechanisms" architectural reframe.** Pre-v5 doc:
   "C++ automatic relay + Python explicit relay = two relay mechanisms". Reality:
   **THREE routing mechanisms** exist:
   - (1) Per-handler `Forward` group routing: handlers (FUN_0069FDA0 / FUN_0069F930)
     explicitly call SendToGroup("Forward") to relay game opcodes.
   - (2) Python `NoMe` group routing: Python script messages (0x2C+) use
     SendTGMessageToGroup("NoMe") to broadcast-excluding-self.
   - (3) Connect-event broadcast: FUN_006B63A0 handles connect events with its own
     broadcast pattern (FUN_006B51E0) for join/leave coordination only.
   The doc adds a new "Three Routing Mechanisms" section near the top with a comparison
   table; the old "two relay mechanisms" bullet in the star-topology section is updated
   to reference the three.

4. **C4 (minor) - function name correction.** `0x006B8530` was called
   "TGMessage::GetData" in pre-v5 docs; it's actually `TGBufferStream_GetBufferAndSize`
   - a two-output accessor that returns `*(void**)(this+4)` AND writes size into the
   caller's `*sizeOut`. Behavior is the same; the prior name was inaccurate about the
   second output. Renamed throughout body + Key Addresses table.

5. **C5 (minor) - SendTGMessage pseudocode omission.** Pre-v5 pseudocode covered only
   `targetID == 0` (broadcast) and `targetID > 0` (unicast); it omitted the
   `targetID == -1` branch entirely. The new pseudocode covers all three modes,
   including the peer+0x1C key lookup via FUN_006BB9D0. This closes python-messages.md
   OQ4 at the **call-site level** (the meaning of `peer+0x1C` itself remains OQ1 here).

**Cross-source-tagged claims** (`[cross-source-2026-02-24 trace]` -> relay-audit memory):

These are not corrections - they corroborate per-handler relay decisions with empirical
ratios that fall directly out of which handlers do or don't make the SendToGroup call:

- Per-handler relay table column "Trace ratio C:S/S:C" - all ratios from the audit
  memory; 1:1 = relayed, x:0 = absorbed.
- Star Topology section evidence list - peer-map observation from the audit.
- PythonEvent 0x06 vs 0x0D table - 0x0D 31:0 confirms LOCAL ONLY.

**Dropped claims:** None - every doc claim survived in some form (3 reframed, 2 renamed,
the rest unchanged).

**Cross-doc impacts:**

- **Closes OQ4 from python-messages.md.** SendTGMessage targetID == -1 mode resolves the
  peer via `FUN_006BB9D0(optional_arg)` looking up `peer+0x1C == optional_arg`. The
  semantics of `peer+0x1C` itself remains OQ1 here.
- **Confirms `NoMe` and `Forward` group creation** at the C++ ctor that python-messages.md
  already cited - cross-doc agreement.
- **Confirms dispatcher boundary** with game-opcodes.md and wire-format-spec.md.
- **Confirms TGMessage class identity** (sizeof 0x40, vtable 0x008958D0, ctor
  at 0x006B82A0) - inherits cleanly from foundation #3 transport-layer C4.

**New factual sections added (in the rendered doc):**

- **Top-of-doc NOTE block** stating partial status, listing the 3 material + 2 minor
  corrections, and pointing readers at the v5 evidence header.
- **"Three Routing Mechanisms" section** with comparison table - replaces the pre-v5
  "two relay mechanisms" claim.
- **"Per-Handler Relay Pattern" section** with pseudocode for the
  `Clone + FindGroup("Forward") + SendToGroup_Iterate` triad - replaces the pre-v5
  "Host Relay Path - Opaque Forwarding" section.
- **"Connect-Event Broadcast (FUN_006B63A0)" section** documenting mechanism #3.
- **Per-handler relay table** with all 41-opcode relay decisions + trace ratios.
- **Open Questions section** with OQ1 (peer+0x1C semantics), OQ2 (does Python ever use
  targetID == -1?), OQ3 (chat 1:2 mystery).

**Companion follow-ups (deferred to those docs' own validation passes):**

- **python-messages.md** already covered the SendTGMessage 3-mode anchors in its
  validation pass; no further edit needed there. The OQ4 reference in python-messages.md
  can be marked "resolved at call-site level by tgmessage-routing.md OQ1" in the next
  python-messages.md pass.
- **transport-layer.md** already covers the cipher / fragment / factory layers; the C1
  correction here (FUN_006B63A0 is connect-event handler) does not contradict any
  transport-layer claim.
- **network-protocol-analyst memory** - the audit memory accurately describes 0x0D
  absorption, 0x15 absorption, 0x13 absorption, and the per-opcode relay ratios. The
  chat 1:2 mystery (OQ3) is worth a follow-up trace test with single-message cadence
  to disambiguate (a) "Python displays AND relays, count includes display" vs
  (b) "undiscovered second relay path".

**Open questions left for downstream rows:**

1. **OQ1 - peer+0x1C semantics.** Call site located (FUN_006BB9D0 walks peer array for
   `peer+0x1C == optionalArg`), candidate source located (FUN_006B7540 is called inside
   the connect handler and is plausibly the producer), but the field's exact semantic
   (per-connection token? session ID? something else?) is not anchored. A FUN_006B7540
   deep-dive is the natural next step.
2. **OQ2 - Does Python ever call SendTGMessage with targetID == -1?** Stock Python
   patterns observed so far use 0 (broadcast) or positive peer IDs. Whether any stock
   or mod script invokes mode A is unknown - would need a script-corpus grep over
   `SendTGMessage(...` first-arg = -1.
3. **OQ3 - Chat echo 1:2 ratio.** Audit shows 5 C->S, 10 S->C for 0x2C CHAT_MESSAGE.
   `NoMe`-only relay can't explain it (excludes host, so each chat reaches 1 OTHER
   client, not 2). Hypothesis (a): Python ALSO displays locally + relays + audit counts
   local display. Hypothesis (b): undiscovered second relay path. Worth a dedicated
   chat-trace investigation.

**Files touched:** docs/protocol/tgmessage-routing.md (re-rendered with v5 frontmatter,
top-of-doc NOTE block, "Three Routing Mechanisms" section, "Per-Handler Relay Pattern"
section replacing "Host Relay Path", "Connect-Event Broadcast" section, per-handler
relay table with trace ratios, SendTGMessage 3-mode pseudocode including targetID == -1,
NoMe-creation correction, function-name C4 correction, Open Questions section,
refreshed Key Addresses table). docs/protocol/v5-validation-status.md (this row added;
§2 row #7 status flipped to partial).

### 6.8 stateupdate.md — 2026-05-28 (game-archaeology-specialist)

**Status:** validated -> `partial` (5 clarifications, ZERO material wire-format
corrections; doc was accurate).
**Methodology:** Per-doc workflow Phases 1-3 with `program: STBC.exe` on every MCP call.

**Headline:** the highest-volume protocol message (30K+ packets per stock session)
is byte-anchored end-to-end. All 8 dirty-bit wire formats verified against the
sender (Ship__WriteStateUpdate at `0x005B17F0`, 2,472 bytes) and the receiver
(Ship__ReadStateUpdate at `0x005B21C0`, 1,539 bytes). The dispatcher entry
(MpgameHandleStateUpdate at `0x0069FF50`) was recovered and named. The
subsystem-integrity-hash.md "dead in MP" claim is re-confirmed via byte-level
disassembly (the decompiler's `bVar2` vs `bVar16` aliasing was misleading;
disasm at 005b1c76 proves BL is reloaded to `bIsSinglePlayer` before the
flag-0x01 hash-bit emit). **PowerSubsystem__WriteState at `0x005644B0`** was
CREATED in Ghidra (was an undefined function despite the doc citing the address
correctly) — Format 3 (base + 2 battery bytes) confirmed.

**Functions touched (completeness):**

| Function | Addr | effective_score | Role |
|----------|------|-----------------|------|
| MpgameHandleStateUpdate | 0x0069ff50 | 42.1 | opcode 0x1C dispatcher entry (jump-table slot 28); reads opcode + obj_id + dispatches to ship vtable[+0x124] |
| Ship__ReadStateUpdate | 0x005b21c0 | 5.8 | per-flag decode + apply to ship kinematic state + animation tracker |
| Ship__WriteStateUpdate | 0x005b17f0 | 0.0 | per-tick per-peer encoder; vtable slot 72; 2,472 bytes (348 decompiled lines) |
| PowerSubsystem__WriteState | 0x005644b0 | n/a (created) | Format 3 reactor subsystem WriteState: base + 2 battery bytes |

(Sender and receiver effective scores are below v5 target — these are massive functions
with extensive undefined struct accesses that the decompiler can't resolve without
deeper class definitions. The plate comments + 56 inline annotations on the sender +
26 on the receiver capture the wire-format and algorithm semantics required for
doc validation.)

**Confirmed claims (high confidence):**

- All 8 dirty-bit wire formats verified byte-for-byte (see memory file for table).
- Wire header layout (opcode + obj_id + gameTime + dirty_flags = 10 bytes) verified
  at both sender (writes via swig_WriteChar / WriteInt / WriteFloat) and receiver
  (reads via swig_ReadChar / ReadInt / ReadFloat).
- Dispatcher chain: 0x0069F2A0 jump-table slot 28 → 0x0069FF50 → ship vtable[+0x124] =
  slot 73 → 0x005B21C0 (Ship__ReadStateUpdate).
- Sender chain: ship vtable[+0x120] = slot 72 → 0x005B17F0 (Ship__WriteStateUpdate).
- Vtable slot 72 + slot 73 confirmed via tg-hierarchy-vtables doc + ship vtable
  at 0x00894340 with addresses 0x00894460 and 0x00894464 byte-pinned (Ship slot
  72 / 73).
- Subsystem WriteState formats: Base FUN_0056D320 (writes condition byte + recurse
  children + flush via vtable+0xD8); PoweredSubsystem FUN_00562960 (base + bit-gated
  powerPct byte); PowerSubsystem FUN_005644B0 (base + 2 battery bytes via
  FUN_005634C0 GetMainBatteryLimit + FUN_005634D0 GetBackupBatteryLimit).
- Round-robin budgets: 10 bytes for subsystems (sender 005b1ec0 `CMP EAX, 0xa`),
  6 bytes for weapons (sender 005b1f66 `CMP EAX, 0x6`).
- Weapon filtering: `vtable[+8](0x801C)` = IsWeaponType — only emitted/applied for
  matching nodes. SAME ship+0x284 linked list as subsystems.
- Receiver per-flag wire-byte sizes match sender exactly: 12 bytes (3 floats) +
  1 bit + (optional 2 bytes hash) for 0x01; 5 bytes CV4 for 0x02; 3 bytes CV3 for
  0x04 / 0x08; 2 bytes CF16 for 0x10; 1 bit for 0x40.
- Anti-cheat dead-code in MP: sender emits hash bit=1 only when single-player
  (bVar16 = !DAT_0097fa8a); receiver validates only in MP. Mutually exclusive
  conditions confirm subsystem-integrity-hash.md.
- Speed encoding: `||vel||`, sign-flipped if IsReversing (FUN_005AC4F0 returns 1
  when vel·fwd < 0), then CF16-encoded.
- Cloak state read from `ship[+0x2DC]+0x9C` (cloak device subsystem status byte).
- ET_BOOT_PLAYER constant 0x008000F6 used in anti-cheat kick path
  (FUN_006BB840 chain).

**Corrected claims (clarifications, not material corrections):**

1. **Hash flag-emit gate is `bIsSinglePlayer`, not `bVar2`.** The decompiler shows
   `if (bVar16) { WriteBit(1); ... } else WriteBit(0); }` at flag 0x01. But the
   `bVar16` here is NOT the bVar16 from earlier in the function (the !MP flag);
   nor is it bVar2 (the MP+owner-match flag). At disasm site 005b1c76, BL is
   RELOADED from `[ESP+0x23]` which holds bVar16 (= !DAT_0097fa8a = !isMultiplayer).
   So the SP-only emit logic is what's tested, and the dead-in-MP claim holds.

2. **Flag 0x01 wire-format box "[if has_subsystem_hash AND is_multiplayer:]"
   conflates wire format with validation gate.** The wire format is always
   `[bit][if bit set: ushort hash]`. The `AND is_multiplayer` part describes
   the RECEIVER's validation gate; it's not part of the wire format. Receiver
   ALWAYS reads the bit and (if set) the 2-byte hash from the stream; the MP
   check only gates whether validation is performed.

3. **Subsystems and weapons share the SAME `ship+0x284` linked list**, with the
   weapon path filtered by `IsWeaponType` vtable lookup. The doc says "weapon
   linked list at ship+0x284" — correct address but misleading; should say
   "filtered iteration over the same subsystem linked list at ship+0x284".

4. **"This suggests the CLIENT-side value of `DAT_0097fa8a` differs..." speculation
   should be DROPPED.** The mechanism is correctly described above: the
   friendly-fire + player-count gate at FUN_006a2650 naturally selects 0x20 or
   0x80 based on (host >= 2 players) / (client >= 3 players). The traces confirm
   100% disjoint usage; no need to invoke client-side IsMultiplayer
   inconsistency. (`IsMultiplayer = 1` on both endpoints during stock MP.)

5. **PowerSubsystem WriteState at 0x005644B0 was an undefined function** but the
   doc's claim is correct — this validation pass created the function in Ghidra
   and decompiled it. Format 3 confirmed: base + 2 battery bytes.

**Dropped claims:** none. All 8 dirty-bit format claims and all 3 subsystem
WriteState format claims survived intact.

**Retired (no opportunities this pass):** the doc is the canonical StateUpdate
reference; cross-link siblings (stateupdate-subsystem-wire-format.md,
subsystem-integrity-hash.md, per-ship-subsystem-wire-format.md) are downstream
and should keep referencing it.

**Body restructure suggested:**

1. Add v5 YAML frontmatter (validated 2026-05-28, methodology FUNCTION_DOC_WORKFLOW_V5,
   status partial, companions list).
2. Tag verified addresses with `[v5-validated 2026-05-28]` plus new Ghidra names
   (Ship__WriteStateUpdate, Ship__ReadStateUpdate, MpgameHandleStateUpdate,
   PowerSubsystem__WriteState).
3. Note vtable slot 72 = sender and slot 73 = receiver near the function-address citations.
4. Reframe flag 0x01 wire-format box to separate wire format from validation gate.
5. Drop the "CLIENT-side DAT_0097fa8a" speculation paragraph.
6. Clarify weapon path uses SAME ship+0x284 linked list as subsystems (filtered by
   IsWeaponType vtable call), not a separate list.
7. Cross-link to docs/engine/tg-hierarchy-vtables.md (Ship slot 72/73), to
   docs/protocol/stream-primitives.md (CV3/CV4/CF16), to docs/protocol/transport-layer.md
   (TGMessage envelope), and to docs/protocol/subsystem-integrity-hash.md
   (anti-cheat hash dead-code).

**Companion follow-ups:**

- stateupdate-subsystem-wire-format.md row in §2: stateupdate.md confirms the 3
  WriteState formats and round-robin algorithm — sibling can build on these anchors.
- per-ship-subsystem-wire-format.md row in §2: ship+0x284 linked list anchor +
  IsWeaponType filter mechanism confirmed; per-ship catalog can ground its tracer
  counts against these.
- subsystem-integrity-hash.md row in §2: dead-in-MP claim CONFIRMED by this pass;
  sibling doc can cite this validation as primary evidence.

**Open questions left for downstream rows:**

1. **OQ1 — Ship_WriteStateUpdate caller location.** No CALL with FUN_005B17F0 found
   (vtable-dispatched). Likely sits in TGNetwork tick loop iteration. Worth
   tracking, but not blocking for the doc.
2. **OQ2 — pTrackerCtx semantic identity.** Has +0x08 (hash key) and +0x0C (some
   matching ID). Looks like TargetPeerContext. Layout deferred.
3. **OQ3 — Per-weapon delta-dedup hash table at tracker+0x40 entry size 0xC bytes.**
   Layout TBD.
4. **OQ4 — Animation tracker pointer at iVar3 in receiver.** Obtained via
   FUN_005A1720 + FUN_0047DE50 (Cast to type=9). Type 9 is likely NIAnimationNode
   or similar; receiver writes interpolation state at +0x2C..+0x54.
5. **OQ5 — DAT_00888860 force-resend threshold value** — appears in 934 sites
   project-wide. Single-source-of-truth value (probably "1.0" seconds) worth
   pinning.

**Annotations applied this session:**

- 3 functions renamed: `MpgameHandleStateUpdate`, `Ship__ReadStateUpdate`,
  `Ship__WriteStateUpdate`.
- 1 function CREATED via `mcp__ghidra__create_function`:
  `PowerSubsystem__WriteState` at 0x005644B0.
- 3 typed __thiscall / __cdecl prototypes installed.
- 2 globals labeled: `g_flWeaponHealthScale` at 0x008944C4; `ET_BOOT_PLAYER`
  at 0x008000F6.
- 4 plate comments installed: MpgameHandleStateUpdate, Ship__ReadStateUpdate,
  Ship__WriteStateUpdate (massive); plus annotation patterns for the inline
  comments.
- 56 inline decompiler comments on Ship__WriteStateUpdate, 26 on Ship__ReadStateUpdate,
  5 on MpgameHandleStateUpdate.
- ~30 + ~25 variable renames on sender/receiver respectively (Hungarian-compliant).

**Files touched:** docs/protocol/v5-validation-status.md (this row added; §2 row #8
status flipped to partial). docs/protocol/stateupdate.md NOT modified this pass —
the documentation-writer agent will re-render with the corrections + restructure
listed above.

---

### 6.9 object-replication.md — 2026-05-28 (game-archaeology-specialist)

**Verdict:** `partial`. Smallest doc in the family (~30 lines). All 6 load-bearing
claims confirmed at the binary level. Two material wording REFINEMENTS (not
corrections) needed; one is a sender-vs-receiver direction clarification, the other
is a vtable-slot direction clarification. Doc body short enough that
documentation-writer should re-render in full.

**Subject:** `MpgameHandleObjCreate` at `0x0069F620` (renamed from `FUN_0069f620`).
Shared receiver+host-relay for opcodes 0x02 (ObjCreate) and 0x03 (ObjCreateTeam).

**Cross-anchors verified:**

- `MpgameHandleMessage` at `0x0069F2A0` (foundation #4) — jump table thunks
  at `0x0069F31E` (opcode 0x02, `PUSH 0`) and `0x0069F334` (opcode 0x03,
  `PUSH 1`) re-decoded byte-for-byte. Same handler, only param_3 differs.
- TGMessage envelope vtable `0x008958D0` (foundation #3) — `param_2` is a
  `TGMessage *`; relay path uses `vtable+0x18` (Clone) before SendTGMessage.
- SWIG `TGBufferStream` at `0x006CEFE0` / vtable `0x00895C58` (foundation #2)
  — used inside `FUN_005A1F50` for the per-object payload (`OpenBuffer` →
  `ReadInt` × 2 → vtable[0x118] Deserialize → vtable[0x11C] Fixup).
- `wire-format-spec.md` (foundation #1) — 0x02/0x03 listed as S→C, confirmed.

**Confirmed claims (6/6):**

1. **Shared handler** — `FUN_0069F620` is reached only via the 0x02 thunk
   (`PUSH 0`) and the 0x03 thunk (`PUSH 1`). No other xrefs to the function.
2. **Wire format** (off 0 opcode, off 1 owner_slot, off 2 team_id if 0x03) —
   confirmed against both the receiver decompile (`cVar3 = *(char *)(buf+1)`;
   `local_10 = *(char *)(buf+2)` iff `bWithTeam`) and the two senders
   (`NewPlayerInGameHandler` at `0x006A1E70` + `FUN_006A02A0` RequestObj
   handler) which write `local_40c[0] = 2|3`, `local_40c[1] = owner_slot`,
   `local_40c[2] = team`.
3. **Team byte for 0x03** — present iff `param_3 != 0`. Receiver stores at
   `piVar5[0xB9]` (int-index 0xB9 = byte offset 0x2E4); sender reads from
   `controller+0x2E4`. Symmetric.
4. **`FUN_005A1F50` deserialize path** — confirmed: opens SWIG TGBufferStream
   on (buf+iVar7, len-iVar7), reads class species ID and object ID via
   two `ReadInt`s, runs `FUN_00430730(0, classID)` as a class-category 0x8002
   pre-check (REJECT if non-null), calls factory `FUN_006F13E0(cls, id)`,
   then invokes object vtable+0x118 (Deserialize) and vtable+0x11C (Fixup).
5. **Receiver behavior** — confirmed with detail: active-slot SWAP wraps
   `FUN_005A1F50` (`DAT_0097fa84` saved/restored, `DAT_0097fa8c` swapped,
   `DAT_0095b07d` toggled 0→1 around the call); host-side relay loop walks
   16 PlayerSlots at offset +0x7C with stride 0x18, clones the message via
   `vtable+0x18` and `SendTGMessage` to peers other than the sender and
   ourselves; Network controller (88 bytes) is allocated via
   `NiAlloc(0x58)` + `FUN_0047dab0(controller, "Network")` and attached via
   `vtable+0x134`.
6. **Authority S→C** — confirmed. Senders are both server-side codepaths
   (NewPlayerInGameHandler on join; RequestObj response). Clients only
   receive (and forward via the in-handler relay when acting as host).

**Refinements (not binary corrections — wording fixes):**

R1. **`FUN_006A19A0` is sender-side only.** Doc body says the byte-1
   owner-slot is "mapped from object owner to player slot via FUN_006a19a0".
   That mapping IS done by `FUN_006A19A0` — but on the SENDER side, before
   transmit. The receiver decompile (this doc's subject) does NOT call
   `FUN_006A19A0`; it reads the already-mapped byte directly from buf+1.
   Recommend rewording to "Byte 1: owner_player_slot — sender computes via
   `FUN_006A19A0(ship->owner_ptr)`; receiver reads the byte as-is."

R2. **`vtable[0x10C]` is a sender slot.** Doc says
   `object->vtable[0x10C](buffer + offset, maxlen - offset)` writes the
   "object serialization data". That is the SENDER's vtable slot
   (used by `FUN_006A02A0` + `NewPlayerInGameHandler`). The RECEIVER
   `FUN_0069F620` does NOT call vtable[0x10C]; it calls
   `FUN_005A1F50`, which uses vtable[0x118] (Deserialize) and
   vtable[0x11C] (Fixup) on the freshly instantiated object. Recommend
   splitting the wire-format description into "sender writes via
   vtable+0x10C" and "receiver decodes via factory FUN_006F13E0 + vtable+0x118
   + vtable+0x11C."

**Cross-doc consistency:**

- `game-opcodes.md` (mid #4) — 0x02 row says "FUN_0069F620 (arg2=0)" and
  0x03 row says "(arg2=1)"; matches the byte-by-byte thunk re-decode here.
- `objcreate-serialization.md` (mid #10) — the doc-under-review cross-links
  to it for the full serialization chain. Validating that doc is the next
  step in the campaign (mid #10).
- `multiplayer-decompiled-functions.md` / `decompiled-functions.md` —
  documented receiver at the right address, consistent with this validation.

**Open questions (recorded for the next dig):**

- Active-slot SWAP reentrancy: the `DAT_0095b07d=0` flag is set false
  before `FUN_005A1F50` and true after — implies a guard. Unknown if
  FUN_005A1F50 itself can recurse into more ObjCreate paths; if so the
  outer save/restore could leak. Out of scope here; revisit during the
  multiplayer-flow archaeology if it ever resurfaces in crash reports.
- Why does the receiver skip controller attach when piVar5[1] equals
  `*(int *)(this+0x80)` (own slot) in the host branch? Likely because the
  host already has authority for its own objects. Confirm during
  objcreate-serialization.md validation.
- Per-class wire payloads (Ship vs Torpedo vs Beam vs Explosion) are
  emitted by class-specific vtable+0x10C overrides — those belong to
  the per-class wire-format docs, not here.

**Annotations written to Ghidra (program: STBC.exe):**

| Action | Target | Detail |
|---|---|---|
| rename_function | FUN_0069f620 → `MpgameHandleObjCreate` | warning re: "Mpgame" verb is benign (consistent with siblings) |
| set_function_prototype | 0x0069F620 | `void __thiscall MpgameHandleObjCreate(MultiplayerGame *, TGMessage *, char bWithTeam)` |
| set_plate_comment | 0x0069F620 | Algorithm, wire format, struct layout, control flow, magic numbers, invocation sites, complementary senders, cross-refs |

**Files touched:** docs/protocol/v5-validation-status.md (this row added). The
doc-under-review (`docs/protocol/object-replication.md`) NOT modified this pass
— documentation-writer agent will apply R1 + R2 wording fixes and add the
`[v5-validated 2026-05-28]` tag plus the v5 frontmatter header.

### 6.10 objcreate-serialization.md — 2026-05-28 (game-archaeology-specialist)

**Verdict:** `partial`. ~80 load-bearing claims. THREE material corrections
(C1 velocity wire format, C2 playerSlots base offset, C3 vtable[+0x118] /
[+0x11C] split labelling) plus 3 refinements. Foundation claims (handler,
factory, dispatch chain, species map) are rock-solid; corrections are in
specific sub-sections of the wire format.

**Subject:** the full ObjCreate deserialization pipeline for the Ship class
(class_id `0x00008008`) and Torpedo class (class_id `0x00008009`). The doc
covers the wire format from after the 2- or 3-byte opcode prefix all the
way through Python `SpeciesToShip.InitObject()` and subsystem health
deserialization.

**Cross-anchors verified:**

- `MpgameHandleObjCreate` at `0x0069F620` (foundation #9) — caller of
  `HandleObjCreateDeserialize`. Passes `buf+iVar7` and `len-iVar7` where
  `iVar7 = 2 or 3` depending on opcode.
- SWIG `TGBufferStream` at `0x006CEFE0` / vtable `0x00895C58`
  (foundation #2) — used inside `HandleObjCreateDeserialize` and the
  sister body writer. Read primitives confirmed:
  ReadChar @ vtable[+0x50], ReadShort @ vtable[+0x58], ReadInt @ vtable[+0x78],
  ReadFloat @ vtable[+0x70], ReadCV4 @ vtable[+0x94].
- Ship vtable at `0x00894340` (foundation: engine doc #7 vtable map) —
  slot offsets 0x10C / 0x110 / 0x114 / 0x118 / 0x11C verified by reading
  raw vtable bytes. Targets: `0x005A1CF0` (slot 0x10C, sender entry),
  `0x005A1D80` (slot 0x110, sender header), `0x005B0D80` (slot 0x114,
  sender body+subsystems), `0x005B0E80` (slot 0x118, receiver species+Python),
  `0x005B0DC0` (slot 0x11C, receiver body+subsystems).
- `MultiplayerGame_Ctor` at `0x0069E590` (foundation #6) —
  `FUN_00859d64(this+0x1d, 0x18, 0x10, ...)` definitively places the
  playerSlots base at `this+0x74` with 16 slots × 24 bytes.

**Functions touched (completeness):**

| Function | Addr | effective_score | Used to verify |
|----------|------|-----------------|----------------|
| HandleObjCreateDeserialize | 0x005A1F50 | 32.6 / 92.5 max | Dispatch chain: ReadInt+ReadInt+ObjectLookup+TGFactoryCreate+vtable[0x118]+vtable[0x11C] |
| ShipReadSpecies | 0x005A2030 | n/a | Species byte at vtable[+0x50] → ship+0xEC |
| ShipReadStreamBody | 0x005A2060 | 14.5 / 80 max | Wire body: 3xReadFloat (pos) + 4xReadFloat (quat) + ReadCV4 (vel) + 2 length-prefixed strings |
| ShipDeserializeStream_Slot118 | 0x005B0E80 | n/a (plate) | vtable[+0x118] = species + Python InitObject |
| ShipPostDeserializeFixup_Slot11C | 0x005B0DC0 | n/a (created this pass) | vtable[+0x11C] = body + subsystem walk |
| ShipSerializeForObjCreate_Slot10C | 0x005A1CF0 | n/a | Sender entry: opens stream, calls slots 0x110+0x114 |
| ShipWriteHeader_Slot110 | 0x005A1D80 | n/a | Sender slot 0x110: WriteInt(class), WriteInt(obj), WriteChar(species) |
| ShipWriteStreamBody | 0x005A1DC0 | n/a | Sender body: WriteFloat×3 (pos), WriteFloat×4 (quat from FUN_00816390 matrix-to-quat), WriteCV4 (vel from FUN_005A05A0), strings |
| ShipSerializeStream_Slot114 | 0x005B0D80 | n/a (created this pass) | Sender slot 0x114: writes body + walks ship+0x284 for subsystem writes |
| TGFactoryCreate | 0x006F13E0 | n/a | Factory: walks DAT_0099A578/DAT_0099A584, returns new TGObject instance |
| ObjectLookupByID | 0x00430730 | n/a | DAT_0099A67C hash lookup; gates on class category 0x8002 |

**Confirmed claims (high confidence):**

- **Wire envelope** (off 0 opcode, off 1 owner_slot, off 2 team_id iff 0x03,
  off 2|3 onwards = TGBufferStream payload) — see §6.9 receiver confirmation;
  this doc's header section accurately mirrors it.
- **Stream header** (4-byte class_id + 4-byte object_id) — both reads
  happen explicitly in `HandleObjCreateDeserialize`. Confirmed.
- **Factory class IDs 0x8008 / 0x8009** — match the trace examples. The
  per-class branching (Ship gets Network controller; Torpedo skips) is
  enforced by `if (iVar8 == 0x8009) return;` inside MpgameHandleObjCreate.
- **Species byte at ship+0xEC** — `*(int *)(param_1 + 0xec) = (int)cVar1`
  in ShipReadSpecies.
- **Python SpeciesToShip.InitObject pipeline** — confirmed via string refs
  `s_Multiplayer_SpeciesToShip_008e61ec` + `s_InitObject_008e5620` inside
  `ShipDeserializeStream_Slot118`. The 5-step pipeline (SetupModel →
  Hardpoints.LoadPropertySet → SetupProperties → UpdateNodeOnly + ship
  stats lookup) is anchored in `reference/scripts/Multiplayer/SpeciesToShip.py`
  (cross-source).
- **SpeciesToShip 1..45** — byte-exact match against the script;
  doc table accurate.
- **SpeciesToTorp 1..15** — byte-exact match.
- **SpeciesToSystem 1..9** — byte-exact match; the doc correctly lists
  Multi1..7 + Albirea + Poseidon. MAX_SYSTEMS = 10 (with index 0 = UNKNOWN).
- **Set/system name binary-search registry at DAT_0097E9C8 / size
  DAT_0097E9CC** — confirmed in ShipReadStreamBody body.
- **Object ID space (`0x3FFFFFFF + N*0x40000`)** — visible in trace
  examples; not directly disproved but the doc-cited formula is consistent
  with the trace evidence. Anchoring the ID-allocation site is out of
  scope for this pass (it lives in the sender path).

**Corrected claims:**

1. **C1 — Velocity wire format is CV4 (3 dir bytes + 4-byte magnitude),
   NOT "f32 speed + 3 padding bytes" (material).**
   - Old (doc):
     ```
     37  4 f32   speed       Speed magnitude (usually 0.0 at spawn)
     41  3 u8[3] padding     Always 0x00 0x00 0x00
     ```
   - **New (binary):**
     ```
     37  3 u8[3] velocity_dir Compressed normalized direction (signed bytes)
     40  4 f32   velocity_mag Velocity magnitude (m/s)
     ```
   - Evidence: ShipReadStreamBody (0x005A2060) calls vtable[+0x94]
     (`CompressedVector4_ReadVirtual` at `0x006D2FD0`) with param_5=0,
     which executes vtable[+0x50] ReadChar × 3 FIRST, then vtable[+0x70]
     ReadFloat × 1. Total 7 bytes. Doc had widths right (4+3=7) but
     order/semantics inverted.
   - Trace evidence: bytes 37-43 are observed as `00 00 00 00 00 00 00`
     in spawn traces, which is consistent with EITHER interpretation
     (zero velocity = both 3 dir bytes and 4 mag bytes are 0). The
     binary settles the ambiguity.

2. **C2 — `MultiplayerGame.playerSlots` base is at `+0x74`, NOT `+0x84` (material).**
   - Old (doc): *"MultiplayerGame+0x84 contains a 16-entry array with
     stride 0x18 (24 bytes per slot)."*
   - **New: base at `MultiplayerGame+0x74`, 16 slots × 24 bytes.**
   - Evidence: `MultiplayerGame_Ctor` (0x0069E590) line:
     `FUN_00859d64(param_1 + 0x1d, 0x18, 0x10, FUN_006a7720, FUN_006a7760);`
     `param_1 + 0x1d` (32-bit pointer indexed) = byte offset +0x74.
   - The "MultiplayerGame+0x84" the doc cites is offset `+0x10` within
     each PlayerSlot — the game-state pointer field. For slot 0 that
     resolves to `+0x74 + 0*0x18 + 0x10 = +0x84`. The doc and the binary
     describe the SAME table — but using different field anchors. Use
     the slot-array base (`+0x74`) as canonical for clean-room implementers;
     mention the `+0x84` only as the game-state pointer FIELD.
   - PlayerSlot layout (24 bytes):
     - +0x00 (?)
     - +0x04 inUse byte (relay-loop gate)
     - +0x08 peer/network ID (relay-loop key)
     - +0x10 game-state pointer (= MultiplayerGame+0x84 for slot 0)
     - +0x14 (?)
   - Anchors `struct-skeletons-20260528` memory entry.

3. **C3 — `vtable[+0x118]` reads ONLY the species byte; the wire BODY is
   read by `vtable[+0x11C]` (material; structural).**
   - Old (doc pipeline diagram):
     ```
     obj->vtable[0x118](stream) → ReadStream
         ├─ FUN_005a2030: ReadByte → ship+0xEC (species)
         ├─ Python: SpeciesToShip.InitObject(ship, species)
         └─ Continue reading: position, orientation, velocity, name, set, subsystems
     obj->vtable[0x11C](stream) → PostLoad
     ```
   - **New (binary):**
     - vtable[+0x118] = `ShipDeserializeStream_Slot118` (0x005B0E80):
       - Reads ONLY the 1-byte species (via `ShipReadSpecies`).
       - Invokes Python `Multiplayer.SpeciesToShip.InitObject(self, species)`.
       - Calls `stream->vtable[+0xD8]()` (bit-alignment finalize).
       - Returns. Does NOT read position / quat / velocity / names.
     - vtable[+0x11C] = `ShipPostDeserializeFixup_Slot11C` (0x005B0DC0):
       - Calls `ShipReadStreamBody` (0x005A2060) which reads:
         - 3 floats position (x, y, z)
         - 4 floats quaternion (w, x, y, z) → matrix via FUN_008162B0
         - CV4 velocity (3 dir + 4 mag = 7 bytes)
         - u8 + bytes player_name string
         - u8 + bytes set_name string (binary-searched in DAT_0097E9C8)
       - Walks ship+0x284 subsystem linked list → vtable[+0x6c] per node
       - Calls `stream->vtable[+0xD8]()` (finalize)
   - This is structurally important. The two-pass scheme is FORCED by
     data-dependency: subsystems don't exist until Python's
     `SetupProperties()` runs inside vtable[+0x118], and the body data
     needs the subsystem chain to deserialize subsystem state. The
     labels "ReadStream" / "PostLoad" in the doc are misleading —
     re-label to:
     - vtable[+0x118] = "DeserializeIdentityAndInit" (species → ship type → NIF load)
     - vtable[+0x11C] = "DeserializeBodyAndFixup" (position, quat, velocity,
                       names, per-subsystem state)

**Refinements (not binary corrections):**

R1. **Two DAT_ globals conflate "factory registry" with "object hash table".**
   - `DAT_0099A67C` = object hash table (by object_id)
   - `DAT_0099A578` = factory registry vtable
   - `DAT_0099A584` = factory bucket array
   - `TGFactoryCreate` walks the FACTORY REGISTRY (by class_id key).
     `ObjectLookupByID` walks the OBJECT HASH TABLE (by object_id key).
   - The doc says "factory_class_id is looked up in the TG object factory
     (DAT_0099a67c)" — confuses the two. Recommend split: "class_id
     resolved via factory registry (DAT_0099A578); object_id resolved via
     object hash (DAT_0099A67C)".

R2. **Duplicate check `FUN_00430730(0, object_id)` is also a class-category gate.**
   - The doc says "checked against the object hash table — if an object
     with that ID already exists, deserialization aborts."
   - Reality: the function returns the object IFF found AND its class
     category equals 0x8002 (game object). Returns NULL for non-game-object
     IDs (which the caller treats as "OK to create"). In practice this
     doesn't change observable behavior — all ObjCreate'd objects are
     game objects — but the wording should reflect the gate.

R3. **Open question on quaternion vs Euler is RESOLVED — quaternion.**
   - Doc's open question: *"Whether orientation is stored as quaternion
     (4 floats) or Euler angles (3 floats) — quaternion is more likely
     given 4 consecutive floats after position"*.
   - Definitively CONFIRMED quaternion (w, x, y, z) via:
     - FUN_00816390 (sender): matrix → quaternion (Shoemake algorithm
       with SQRT + sign-handling)
     - FUN_008162B0 (receiver): quaternion → 3×3 matrix expansion
   - Wire offsets 21-37 = 16 bytes = 4 floats = (w, x, y, z).
   - The open-question can be CLOSED.

R4. **§4 #1 cross-doc disagreement: FUN_005A2030 identity.**
   - `objcreate-serialization.md` calls it `ReadSpeciesByte`. ✓ CONFIRMED.
     `cVar1 = stream->vtable[+0x50](); *(int *)(param_1 + 0xec) = (int)cVar1;`
   - `objnotfound-requestobj-enterset.md` may call it `GetPlayerSlotFromObjID`.
     **That doc has it wrong.** This pass settles the conflict in favor of
     the objcreate-serialization claim. The objnotfound doc needs an
     accompanying re-check (mid #11 or later).

**Cross-doc consistency:**

- `object-replication.md` (mid #9) — handler at 0x0069F620 + vtable[+0x118]
  + vtable[+0x11C] + factory FUN_006F13E0 — all match.
- `stream-primitives.md` (foundation #2) — SWIG TGBufferStream primitives
  used inside the dispatch chain — all addresses + slot offsets match.
- `game-opcodes.md` (mid #4) — 0x02 / 0x03 row maps to FUN_0069F620.
- `multiplayer-decompiled-functions.md` / `decompiled-functions.md` — none
  of the renames performed here conflict with the engine-family doc set.

### 6.11 stateupdate-subsystem-wire-format.md — 2026-05-28 (game-archaeology-specialist)

**Verdict:** `partial`. ~150 load-bearing claims. Wire formats and round-robin
algorithm 100% confirmed; TWO material corrections in the named ship-slot table
(C1: ship+0x2C4 mislabelled, C2: ship+0x2C0 ShieldGenerator missing); ONE
function-attribution clarification (EndMarker call site identifies the wrong
function); the Sovereign-class wire-byte example is unverifiable in this repo
(hardpoint file absent — sovereign.py is on the client install only).

**Subject:** the StateUpdate (0x1C) flag 0x20 payload — round-robin walk of the
ship+0x284 subsystem linked list, with three polymorphic `WriteState` formats
(base / Powered / Power) and recursive child writes. Doc also covers
`SetupProperties` (which builds ship+0x284) and `LinkSubsystemToParent` (which
prunes weapon/engine children and re-attaches them under parent systems).

**Cross-anchors verified (foundation cascade):**

- `Ship__WriteStateUpdate` at 0x005B17F0 (stateupdate.md mid #8) — round-robin
  loop at flag 0x20 confirmed bytes-precise; 10-byte budget cap at offset
  005B1EC0 (`CMP EAX, 0xA`).
- `Ship__ReadStateUpdate` at 0x005B21C0 (mid #8) — receiver flag-0x20 walk
  with `start_index` byte + linked-list traversal at offset 005B26B0
  matches doc pseudocode lines 113-131.
- SWIG TGBufferStream vtable @ 0x00895C58 (stream-primitives mid #2):
  WriteChar @ vtable[+0x54], WriteBit @ vtable[+0x4C], GetPos @ vtable[+0xD8].
  All three confirmed in WriteState bodies.
- Subsystem vtable layout: WriteState at +0x70, ReadState at +0x74 — verified
  by reading raw bytes of HullSubsystem vtable @ 0x00892D00 +0x70 = 0x0056D320.

**Functions touched (completeness):**

| Function | Addr | effective_score | Used to verify |
|----------|------|-----------------|----------------|
| Ship__WriteStateUpdate | 0x005B17F0 | 0.0 / 78.0 max | Round-robin loop (flag 0x20), 10-byte budget |
| Ship__ReadStateUpdate | 0x005B21C0 | 5.8 / 85.0 max | Receiver round-robin (start_index + walk) |
| ShipSubsystem__WriteState | 0x0056D320 | 10.5 / 87.8 max | Base format: condition byte + child recursion |
| PoweredSubsystem__WriteState | 0x00562960 | 11.1 / 89.0 max | Powered format: base + hasData bit + powerPct byte |
| PowerSubsystem__WriteState | 0x005644B0 | 25.9 / 89.0 max | Power format: base + 2 battery bytes (UNCONDITIONAL) |
| ShipSubsystem__ReadState | 0x0056D390 | n/a | Receiver base: condition + child recursion |
| PoweredSubsystem__ReadState | 0x005629D0 | n/a | Receiver Powered: base + bit + opt byte |
| PowerSubsystem__ReadState | 0x00564530 | n/a (created this pass) | Receiver Power: base + 2 byte reads |
| ShipSubsystem__GetMaxCondition | 0x0056C310 | n/a | property+0x20 (or 1.0f if no property) |
| ShipSubsystem__GetChildSubsystem | 0x0056C570 | n/a | this+0x20 array, this+0x1C count, bounds-checked |
| PowerSubsystem__GetMainBatteryLimit | 0x005634C0 | n/a | property+0x48 |
| PowerSubsystem__GetBackupBatteryLimit | 0x005634D0 | n/a | property+0x4C |
| ShipSubsystem__AddChildSubsystem | 0x0056C5C0 | n/a | Grows parent's +0x20 array, increments +0x1C |
| Ship__SetupProperties | 0x005B3FB0 | n/a | Switch on property type IDs (0x812E-0x813F + 0x8145), populates named ship slots |
| Ship__AddSubsystemToLists | 0x005B3E50 | n/a | Appends to ship+0x284 (always); 8 types are EXCLUDED from second list at ship+0x29C |
| Ship__LinkSubsystemToParent | 0x005B5030 | n/a | Weapon/engine attach + remove from ship+0x284 |
| Ship__LinkAllSubsystemsToParents | 0x005B3E20 | n/a | Iterates ship+0x284 calling LinkSubsystemToParent |

**Confirmed claims (high confidence):**

- **Linked list at ship+0x284** — confirmed via WriteStateUpdate `pShip2[0xa1]`
  read (= ship+0x284) and receiver `*(int **)((int)this + 0x284)` access.
  Node layout: `+0x00 data*, +0x04 next*, +0x08 prev*`. List manages count
  at ship+0x280, head at +0x284, tail at +0x288, free list at +0x28C.
- **3 WriteState vtable functions used at slot +0x70:**
  - Base ShipSubsystem (0x0056D320) — referenced by 8 vtables.
  - PoweredSubsystem (0x00562960) — referenced by 11 vtables.
  - PowerSubsystem (0x005644B0) — referenced by 1 vtable @ 0x0088A260.
- **Base format wire layout:** `condition_byte = ftol((this+0x30 /
  GetMaxCondition()) * 255.0)` followed by recursive `vtable[+0x70](stream,
  isOwnShip)` over `this+0x20[0..this+0x1C-1]`. Confirmed instruction-by-
  instruction at 0x0056D320.
- **Powered format wire layout:** if `isOwnShip == 0` then `WriteBit(1) +
  WriteByte(ftol(this+0x90 * 100.0))`; else `WriteBit(0)`. Confirmed via
  disassembly: `TEST BL,BL / JNZ skip_power_branch`.
- **Power format wire layout:** `WriteByte(ftol((this+0xAC /
  GetMainBatteryLimit()) * 255.0)) + WriteByte(ftol((this+0xB4 /
  GetBackupBatteryLimit()) * 255.0))` — **UNCONDITIONAL** (no `TEST/JCC` on
  isOwnShip between FUN_0056D320 and the two CALL [vtable+0x54] writes).
  The doc's "ALWAYS regardless of isOwnShip" note holds.
- **Property type ID → ship slot mapping in SetupProperties (FUN_005B3FB0):**
  | Property ID | Type | Ship slot |
  |-------------|------|-----------|
  | 0x812F + iVar4==1 | CT_WEAPON_SYSTEM_PROPERTY (Phaser) | ship+0x2B8 |
  | 0x812F + iVar4==3 | CT_WEAPON_SYSTEM_PROPERTY (Pulse) | ship+0x2BC |
  | 0x812F + iVar4==4 | CT_WEAPON_SYSTEM_PROPERTY (Tractor) | ship+0x2D4 |
  | 0x8133 | CT_TORPEDO_SYSTEM_PROPERTY | ship+0x2B4 |
  | 0x8137 | CT_SHIELD_PROPERTY | ship+0x2C0 (DOC MISSING) |
  | 0x8138 | CT_HULL_PROPERTY | ship+0x2C4 (DOC INCORRECTLY says PowerSubsystem) |
  | 0x8139 | CT_SENSOR_PROPERTY | ship+0x2C8 (DOC MISSING) |
  | 0x813A | CT_CLOAKING_SUBSYSTEM_PROPERTY | ship+0x2DC |
  | 0x813B | CT_WARP_ENGINE_PROPERTY | ship+0x2D0 |
  | 0x813C | CT_IMPULSE_ENGINE_PROPERTY | ship+0x2CC |
  | 0x813E | CT_POWER_PROPERTY | ship+0x2B0 |
  | 0x813F | CT_REPAIR_SUBSYSTEM_PROPERTY | ship+0x2D8 |
- **Engine parent-child disambiguation:** property+0x48 holds EngineType enum
  (0=EP_IMPULSE, 1=EP_WARP). FUN_005B5030 reads it and routes to ship+0x2CC
  (impulse) or ship+0x2D0 (warp). Confirmed at 0x005B5097-0x005B50A0.
- **Round-robin algorithm:** doc pseudocode lines 196-225 confirmed
  instruction-for-instruction. Tracker layout `iVar5+0x30 pSubsysCursor /
  iVar5+0x34 uSubsysIndex` per stateupdate.md mid #8.
- **8 types excluded from second list (ship+0x29C/0x2A0):** 0x801F
  PhaserSystem, 0x8021 TractorBeamSystem, 0x802C PhaserBank, 0x802F
  TorpedoTube, 0x802E TractorBeamProjector, 0x802D PulseWeapon, 0x8025
  WarpEngine, 0x8024 CloakDevice. Confirmed via 8-deep nested type-ID check
  in FUN_005B3E50 lines 0x5B3EA0-0x5B3F40.
- **Globals:**
  - `_DAT_00888860 = 0x3F800000 = 1.0f` — confirmed via raw bytes; used as
    GetMaxCondition fallback when property == NULL.
  - `0x0088B9AC = 0x437F0000 = 255.0f` — byte-scale multiplier in condition
    + battery + sender weapon-health computations.
  - `0x0088CE78 = 0x42C80000 = 100.0f` — powerPct multiplier in
    PoweredSubsystem WriteState.
  - `0x0088D4E4 = 0x3C23D70A = ~0.01f` — powerPct decode scale in
    PoweredSubsystem ReadState (byte 0-100 × 0.01 → 0-1.0 ratio).

**Corrected claims:**

1. **C1 — Named ship-slot table is materially wrong (ship+0x2C0 missing,
   ship+0x2C4 mislabelled).**
   - Old (doc table at lines 348-360):
     ```
     ship+0x2B0  Powered master (EPS) / Power distribution
     ship+0x2C4  PowerSubsystem (reactor)
     ```
     (no ship+0x2C0 row; no ship+0x2C8 row)
   - **New (binary, SetupProperties):**
     ```
     ship+0x2B0  PowerSubsystem        (case 0x813E)  — THE reactor/EPS
     ship+0x2C0  ShieldGenerator       (case 0x8137)  — was missing
     ship+0x2C4  HullSubsystem         (case 0x8138)  — doc had as Power
     ship+0x2C8  SensorSubsystem       (case 0x8139)  — was missing
     ```
   - Evidence: `Ship__SetupProperties` (0x005B3FB0) switch on property type
     ID 0x813E writes `*(undefined4 *)(param_1 + 0x2b0)`; 0x8137 writes
     `+0x2c0`; 0x8138 writes `+0x2c4`; 0x8139 writes `+0x2c8`. There is no
     case that writes to `+0x2c4` other than 0x8138 (Hull).
   - Impact: the doc's "Powered master (EPS) / Power distribution" at
     ship+0x2B0 is semantically OK (PowerSubsystem IS the EPS) but the
     "(reactor)" gloss on ship+0x2C4 is flat wrong — that slot is Hull.

2. **C2 — EndMarker (`vtable[+0xD8]`) function misattribution.**
   - Old (doc lines 76-77, 90-93, 110):
     *"EndMarker — No-op (function at 0x006cdae0 is just RET)"*
   - **New:** The vtable slot called at the end of each WriteState is
     `vtable[+0xD8]`. On the SWIG TGBufferStream (vtable @ 0x00895C58),
     slot +0xD8 = `0x006CF9B0 = TGBufferStream_swig_GetPos` — reads the
     cursor and returns it. The return value is discarded so it's
     effectively a no-op on stream state, but the function address
     (0x006CDAE0) the doc cites is NOT what's called from WriteState.
     0x006CDAE0 IS a RET-only function, but it lives at slot +0xB0 of a
     DIFFERENT vtable (0x00895B80, the non-SWIG TGStreamedObject vtable —
     a separate class entirely).
   - Impact: cosmetic — the wire behavior is unchanged (no bytes
     written), but the doc identifies the wrong source function.

**Refinements (not binary corrections):**

R1. **Sovereign-class wire-byte example is observational, not anchored.**
   - The 11-row table at doc lines 175-190 ("Sovereign-Class Example") is
     based on `sovereign.py` LoadPropertySet order. That file is not
     present in this repo's reference (only client install carries
     hardpoint files), so the byte sizes per row are not binary-verified
     here. The table is internally consistent with the WriteState format
     rules — `cond + N children + bit + powerPct` arithmetic checks out.
     Confidence: medium (algorithm-derived but not byte-traced).

R2. **"List of 33 subsystems" debunked correctly.**
   - The doc's section ("Total top-level subsystems: 11 — not 33") is
     accurate: the round-robin walks only the top-level list; individual
     weapons and engines appear as CHILDREN of their parent systems and
     get visited via the recursive `vtable[+0x70](stream, isOwnShip)`
     loop inside ShipSubsystem__WriteState. No mapping array exists.

R3. **Ship+0x29C list naming is technically a head pointer.**
   - Doc references "ship+0x29C list". Binary detail: the second list has
     count at ship+0x298, HEAD at ship+0x29C, TAIL at ship+0x2A0. So
     "ship+0x29C list" is the head pointer. Doc's intent is correct; no
     correction needed, but documentation-writer may want to clarify.

R4. **Vtable inheritance chain count holds.**
   - Doc lists 7 base + 9 Powered + 1 Power = 17 types using these
     WriteState functions. Binary shows xrefs: 8 base + 11 Powered + 1
     Power = 20 vtables. The deltas (8 vs 7, 11 vs 9) likely correspond to
     intermediate base-class vtables (ShipSubsystem itself + PoweredSubsystem
     itself + one more) that the doc doesn't enumerate as "user-visible"
     subsystem types. Not a correction — doc is listing leaf classes.

**Open questions (recorded for the next dig):**

- Sovereign-class per-row byte sizes (R1) — requires Sovereign hardpoint file
  for cross-verification.
- Property type ID 0x812E (Bridge) handler FUN_005B5240 not decoded —
  whether the BridgeProperty hull goes into ship+0x284 or is special-cased.
  Doc claims "BridgeProperty_Create creates HullSubsystem — actually IS in
  the list" which suggests it goes through normal AddSubsystemToLists.
  Unverified this pass.
- Property type 0x8145 → FUN_005B5280 — also undecoded.

**Annotations written to Ghidra (program: STBC.exe):**

| Action | Target | Detail |
|---|---|---|
| rename_function | FUN_0056d320 → `ShipSubsystem__WriteState` | base format |
| rename_function | FUN_0056d390 → `ShipSubsystem__ReadState` | base receiver |
| rename_function | FUN_00562960 → `PoweredSubsystem__WriteState` | + plate |
| rename_function | FUN_005629d0 → `PoweredSubsystem__ReadState` | base + bit + opt byte |
| rename_function | FUN_005644b0 → `PowerSubsystem__WriteState` (already named) | + plate |
| create_function + rename | 0x00564530 → `PowerSubsystem__ReadState` | was undefined (DATA xref only from vtable@0x0088a264) |
| rename_function | FUN_0056c310 → `ShipSubsystem__GetMaxCondition` | property+0x20 or 1.0f |
| rename_function | FUN_0056c570 → `ShipSubsystem__GetChildSubsystem` | this+0x20 array, bounds-checked |
| rename_function | FUN_005634c0 → `PowerSubsystem__GetMainBatteryLimit` | property+0x48 |
| rename_function | FUN_005634d0 → `PowerSubsystem__GetBackupBatteryLimit` | property+0x4C |
| rename_function | FUN_0056c5c0 → `ShipSubsystem__AddChildSubsystem` | grows +0x20 array |
| rename_function | FUN_005b3e20 → `Ship__LinkAllSubsystemsToParents` | iterates +0x284 |
| rename_function | FUN_005b3e50 → `Ship__AddSubsystemToLists` | dual-list append (8 types excluded from second) |
| rename_function | FUN_005b3fb0 → `Ship__SetupProperties` | + plate listing 12 named slot mappings |
| rename_function | FUN_005b5030 → `Ship__LinkSubsystemToParent` | + plate documenting 3 classifications |
| set_plate_comment | 0x0056d320 / 00562960 / 005644b0 / 00564530 / 005b3fb0 / 005b5030 | per-function wire-format / classification docs |

**Files touched:** docs/protocol/v5-validation-status.md (this row added;
§2 row for stateupdate-subsystem-wire-format.md status flipped to partial).
The doc-under-review NOT modified this pass — documentation-writer agent
will apply C1+C2 corrections to the named-slot table and EndMarker note,
add ship+0x2C0/+0x2C8 rows, update the v5 frontmatter, and add
`[v5-validated 2026-05-28]` tags to confirmed rows.

**Open questions (recorded for the next dig):**

- Set/system registry contents at `DAT_0097E9C8` — the registration site
  is unanchored. Likely registered during `Mission.LoadScript()` Python
  sequence. Out of scope here.
- Sender-side velocity COMPRESSION step in `ShipWriteStreamBody`
  (vtable[+0x90] → vtable[+0xA0]) — direction vs magnitude separation
  not byte-traced this pass. The receive path is byte-precise, so wire
  format on the wire is anchored either way; only the sender's local
  computation would change behavior for unusual velocity vectors.
- Per-class wire payloads beyond Ship (Torpedo, Beam, Explosion if
  applicable) — Torpedo's class_id 0x8009 is the only other observed
  value. The Torpedo vtable[+0x118] / [+0x11C] pair (not Ship's) reads
  different fields; deferred to per-class wire-format docs.
- `MultiplayerGame.PlayerSlot+0x14` — relay loop pre-walks but field
  semantics unexplored. Probably a per-peer send-sequence counter.

**Annotations written to Ghidra (program: STBC.exe):**

| Action | Target | Detail |
|---|---|---|
| rename_function | FUN_005a1f50 → `HandleObjCreateDeserialize` | + prototype `int * __cdecl (void *, uint)` + plate comment |
| rename_function | FUN_005a2030 → `ShipReadSpecies` | benign warning re: "Ship" verb |
| rename_function | FUN_005a2060 → `ShipReadStreamBody` | + plate comment with byte-precise wire layout |
| rename_function | FUN_005a1cf0 → `ShipSerializeForObjCreate_Slot10C` | sender entry |
| rename_function | FUN_005a1d80 → `ShipWriteHeader_Slot110` | header writer |
| rename_function | FUN_005a1dc0 → `ShipWriteStreamBody` | body writer (FPU-confused decompile) |
| rename_function | FUN_005b0d80 → `ShipSerializeStream_Slot114` | created this pass + renamed |
| rename_function | FUN_005b0dc0 → `ShipPostDeserializeFixup_Slot11C` | created this pass + renamed |
| rename_function | FUN_005b0e80 → `ShipDeserializeStream_Slot118` | + plate comment |
| rename_function | FUN_006f13e0 → `TGFactoryCreate` | + prototype |
| rename_function | FUN_00430730 → `ObjectLookupByID` | + prototype |
| save_program | STBC.exe | |

**Files touched:** docs/protocol/v5-validation-status.md (this row added;
§2 row #10 status flipped to partial). The doc-under-review
(`docs/protocol/objcreate-serialization.md`) NOT modified this pass —
documentation-writer agent will apply C1+C2+C3 corrections and R1-R4
refinements, close the orientation open question, add the v5 frontmatter
header, and add the `[v5-validated 2026-05-28]` tag to confirmed rows.

---

### 6.12 per-ship-subsystem-wire-format.md — 2026-05-28 (game-archaeology-specialist)

**Verdict:** `partial`. ~250 load-bearing claims (largest protocol doc).
**Zero material wire-format corrections** — the doc was exceptionally
accurate. 4 sampled ships byte-by-byte verified (Sovereign 49 / Bird of
Prey 32 / Galor 31 / Akira 47); 11 remaining ships + Enterprise@37 at
medium confidence via pattern extrapolation. 3 refinements (no
binary contradictions): cycle-byte arithmetic precision; "top-level"
definition is post-link; templates that silently drop from
`Ship__SetupProperties`.

**Subject:** Per-ship catalog of the StateUpdate (0x1C) flag 0x20
payload — for each of 16 stock multiplayer ships (species 1-15 +
Enterprise@37), the AddToSet order, top-level subsystem list, child
counts, per-subsystem WriteState byte cost, and per-tick cycle bytes.
The doc operates at the cross-source layer: stbc.exe addresses anchor
the algorithm (mid #8 round-robin + mid #11 WriteState formulas);
`reference/scripts/ships/Hardpoints/<name>.py` anchors per-ship
content.

**Sampling strategy:**
Four ships verified byte-by-byte against their hardpoint .py files:
- **Sovereign**: cycle = 49 bytes (11 top-level + 22 children).
  Computation: `1+1+3+3+5+9+3+11+7+5+1 = 49`. Source: sovereign.py
  LoadPropertySet lines 1379-1474. Match.
- **Bird of Prey**: cycle = 32 bytes (10 top-level + 6 children).
  Computation: `1+1+3+5+4+4+5+3+3+3 = 32`. Source: birdofprey.py
  LoadPropertySet lines 461-509. No PhaserSystem — "Disruptor Cannons"
  via WST_PULSE at line 227. Match.
- **Galor**: cycle = 31 bytes (9 top-level + 8 children). Computation:
  `1+1+3+7+4+5+4+3+3 = 31`. Source: galor.py LoadPropertySet lines
  618-668. No Tractors entry. Match.
- **Akira**: cycle = 47 bytes (11 top-level + 20 children). Computation:
  `1+1+3+3+5+11+5+9+3+5+1 = 47`. Source: akira.py LoadPropertySet
  lines 1274-1307. Bridge at AddToSet position 38, Tractors at 21
  (reversed-from-Federation-norm order). Match.

For each sampled ship, validation followed 4 axes: structural formula
(1+N+2 for Powered; 1+0+2 for Power; 1 for Base), AddToSet ordering,
special-case catalog (Cloak / Pulse / Tractors / Bridge presence),
foundation cross-anchors (slot offsets from mid #11). All 4 axes
held for all 4 sampled ships, justifying medium-confidence extrapolation
to the 12 remaining hulls.

**Foundation cross-anchors (re-confirmed via fresh decompile):**
- `Ship__SetupProperties` at 0x005B3FB0 (4097 bytes) — switch on
  property type IDs decodes all 12 named ship slots (ship+0x2B0..+0x2DC)
  per mid #11. Per-ship doc never cites ship+offset directly (operates
  in terms of the doubly-linked list at ship+0x284), so mid #11
  corrections do not cascade.
- WriteState formula trio (Base 0x0056D320, Powered 0x00562960, Power
  0x005644B0) from mid #11 — per-ship Cycle Bytes column uses these
  formulas correctly for all sampled ships.
- Round-robin 10-byte budget (`CMP EAX, 0xA` at 0x005B1EC0 in mid #8) —
  per-ship "Ticks per Full Cycle" table internally consistent: all 16
  ships have 9-13 top-level subsystems and complete a full cycle in
  3-5 ticks.

**Cross-source verification (`reference/scripts/Multiplayer/SpeciesToShip.py`):**
- IDs 1..15 map to 16 stock MP ships per doc's species table — exact
  match.
- `MAX_FLYABLE_SHIPS = 16` at line 51 confirmed.
- Enterprise@37 inherits from Sovereign (`App.SPECIES_SOVEREIGN` at
  lines 60 + 92) — doc claim "identical subsystem layout, only
  HP/capacity values differ" confirmed.

**Confirmed claims (high confidence, sampled ships):**

- All 4 sampled cycle-byte totals match the Summary Table exactly.
- Universal patterns hold: 7 always-present subsystem types (Hull,
  Shield, Power, Sensor, Impulse, Warp, Repair) + 5 optional (Phaser,
  Torpedo, Tractor, Pulse, Cloak).
- Stock Dedi tracer counts (Section "Stock Dedi Verification") all 15
  ships (Enterprise excluded since it aliases Sovereign) match the
  hardpoint-derived totals.
- Reimplementation implications (6 points) all consistent with binary
  behavior per foundation anchors.

**Refinements (no binary contradictions, doc clarifications):**

R1. **Cycle-byte arithmetic is per-tick exact, per-cycle approximate.**
   The Cycle Bytes column rounds each Powered subsystem's
   `[bit hasData][byte powerPct]` tail to 2 whole bytes. Because
   hasData is a bit packed into the bit-stream cursor (+0x2C bit mask),
   actual per-cycle wire totals may differ by 1-3 bytes from this
   approximation. The 10-byte round-robin budget cap is measured
   against the BYTE cursor, not bit position, so the approximation is
   exact at tick boundaries.

R2. **"Top-Level Subsystems" count is post-link.**
   The number is the post-link state — after
   `Ship__LinkAllSubsystemsToParents` (0x005B3E20) reparents children.
   Pre-link, all subsystems sit in ship+0x284 doubly-linked list.
   Post-link, children with non-zero WeaponID/EngineType get pulled
   out and re-attached under their parent system.

R3. **Templates that silently drop.**
   Some templates in LoadPropertySet AddToSet calls never instantiate
   as subsystems because their property type IDs don't match any case
   in `Ship__SetupProperties`. Examples: "Probe Launcher" (Sovereign
   line 1454), "Shuttle Bay" / "Shuttle Bay 2", "Decoy launcher".
   The switch defaults out; no subsystem is allocated; the result
   does not appear in the top-level linked list. The per-ship tables
   in the doc correctly omit them.

**Open questions (recorded for the next dig):**

1. Bit-stream packing across subsystem boundaries: per-cycle byte
   totals may vary by 1-3 bytes for ships with many Powered
   subsystems. Needs bit-stream cursor trace from a single StateUpdate
   flag-0x20 packet to confirm "1+N+2" is exact bytes or +/- 1 byte
   due to bit alignment.
2. Round-robin overshoot semantics: when a subsystem starts at cursor
   9 and would write 5 bytes, does the cap allow completion (cursor
   → 14) or push to next tick? Foundation mid #8 cites `CMP EAX, 0xA`
   at 0x005B1EC0 but the comparison-direction semantic is unverified.
3. Mod ship behavior: explicitly out of scope; the catalog covers
   16 stock ships.
4. Byte-by-byte verification for the 12 remaining ships (Ambassador,
   Galaxy, Nebula, Vor'cha, Warbird, Marauder, Keldon, CardHybrid,
   KessokHeavy, KessokLight, Shuttle, Enterprise@37). Medium
   confidence pending; promote to high once verified.

**Cross-doc impacts (no in-this-pass modifications):**

- `stateupdate-subsystem-wire-format.md` (mid #11) — already provides
  foundation; consistent.
- `objcreate-serialization.md` (mid #10) — SpeciesToShip.py cross-source
  consistent.
- `subsystem-integrity-hash.md` — no overlap (covers flag 0x01, not
  flag 0x20).

**Annotations written to Ghidra (program: STBC.exe):**

None this pass — all binary anchors were verified-by-reading
(re-decompile of Ship__SetupProperties at 0x005B3FB0 to re-confirm
mid #11 slot table). No renames or plate comments were warranted by
this validation; the foundation docs already carry the heavy
annotation load.

**Files touched:** docs/protocol/v5-validation-status.md (this row
added; §2 row #12 status flipped to partial). The doc-under-review
(`docs/protocol/per-ship-subsystem-wire-format.md`) re-rendered with
v5 frontmatter, top-of-doc NOTE block, new Validation Sampling
Strategy subsection, R1/R2/R3 refinement notes, and inline
`[v5-validated 2026-05-28]` / `[confidence: medium —
pattern-extrapolated]` / `[cross-source-2026-05-28]` tags on
applicable rows.

**Promotion path:** Status stays `partial` until byte-by-byte
verification of the remaining 12 hulls; at that point the doc
promotes to `verified`. The sampling strategy passed all 4 axes
on all 4 sampled ships, so extrapolation confidence is medium
(adequate for the catalog's current operating role; not yet
suitable for "verified" labelling under v5).

---

### 6.13 tgobjptrevent-class.md — 2026-05-28 (game-archaeology-specialist)

**Status:** validated -> `partial` (1 fabricated-class correction
+ 1 vtable-slot-numbering correction + 1 third-string discovery +
several name-only renames; ZERO wire-format corrections; ZERO
producer-list corrections).

**Methodology:** Per-doc workflow Phases 1-5 with `program: STBC.exe`
on every MCP call. Ghidra database had NONE of the small vtable-slot
functions defined (0x004032b0 / 0x004032c0 / 0x004032f0 / 0x00403300
/ 0x00403310 — 6 byte bodies each — they were undefined regions);
all were `create_function`-ed during this pass. Ctor 0x00403290 was
already a function. WriteToStream 0x006d6dc0 and ReadFromStream
0x006d6df0 were also undefined regions despite the doc citing them
by address — both were `create_function`-ed.

**Headline:** TGObjPtrEvent's class layout (`0x2C` bytes, +0x28 =
int32 obj_ptr) is **byte-by-byte confirmed** via decompile of the
ctor and TGEvent base ctor. Wire format (16 base bytes + 4 obj_ptr
bytes = 20 payload, 21 over the wire) **confirmed** via WriteToStream
decompile. All 11 distinct game event types **confirmed** via direct
decompile of 11 producer functions (each emits the doc-claimed
ET_xxxx event_type constant into +0x10 and the doc-claimed obj_ptr
source into +0x28). Dual-fire pattern (Phaser + Tractor each emit
TWO events per fire cycle) confirmed by direct inspection.
Host-only gate on ET_STOP_FIRING_AT_TARGET_NOTIFY (`DAT_0097fa89 !=
'\0'`) confirmed at BOTH producer sites (FUN_00574010 phaser,
FUN_005825a0 tractor). 30 xrefs to the ctor confirmed exactly via
`get_xrefs_to(0x00403290)` (matches the doc's "30 call sites" claim).
5 vtable DATA xrefs confirmed exactly at the 5 addresses the doc
lists (0x40329d ctor + 0x551a5b repair-priority + 0x57f185 tractor +
0x5712fe phaser-stop + 0x5768c5 weapon-system).

**Functions touched (completeness):**

| Function | Addr | effective_score | Plate? |
|----------|------|-----------------|--------|
| TGObjPtrEvent_Ctor | 0x00403290 | 57.75 | yes |
| TGObjPtrEvent_GetFactoryID | 0x004032b0 | n/a (3-instruction leaf) | — |
| TGObjPtrEvent_IsA | 0x004032c0 | n/a (10-instruction leaf) | — |
| TGObjPtrEvent_GetClassName | 0x004032f0 | n/a (string-return leaf) | — |
| TGObjPtrEvent_GetSWIGName | 0x00403300 | n/a (string-return leaf) | — |
| TGObjPtrEvent_GetSWIGPtrName | 0x00403310 | n/a (string-return leaf) | — |
| TGObjPtrEvent_ScalarDeletingDtor | 0x00403320 | n/a | — |
| TGObjPtrEvent_WriteToStream | 0x006d6dc0 | 73.92 | yes |
| TGObjPtrEvent_ReadFromStream | 0x006d6df0 | n/a | yes |
| TGObjPtrEvent_CopyFrom | 0x006d6da0 | n/a | — |
| Game_SetPlayerLocal | 0x004066d0 | n/a | — |
| Ship_SetTarget | 0x005ae210 | n/a | — |
| ShipSubsystem_SetCondition | 0x0056c470 | n/a | — |
| RepairSubsystem_RaisePriority | 0x005519e0 | n/a | — |
| PhaserSystem_StopFiringAtTarget | 0x00574010 | n/a | — |
| TractorBeamSystem_StopFiringAtTarget | 0x005825a0 | n/a | — |

10 functions newly created (5 vtable-slot leaves + ScalarDeletingDtor +
WriteToStream + ReadFromStream + TGCharEvent_IsA + size-0x34 dtor
variant 0x00403500 was already present). 16 functions renamed
(10 TGObjPtrEvent_*  + 6 producer functions). 3 v5 plate comments
installed. `TGObjPtrEvent` struct (0x2C / 44 bytes / 12 fields)
created and applied via prototypes.

**Confirmed claims (high confidence):**

- **Class layout 0x2C bytes** — sizeof verified by struct
  application + ctor allocation pattern (`FUN_00717b70(0x2c) ->
  FUN_00718010 -> FUN_00403290`) at every producer site.
- **Field +0x28 = obj_ptr int32** — ctor zeros it (`param_1[10] = 0`);
  every producer writes `*(undefined4 *)(iVar+0x28) = <obj_id>`.
- **Vtable 0x0088869C** — direct memory inspection (16 slots through
  +0x40 enumerated below); ctor writes it as `*param_1 = &PTR_FUN_0088869c`.
- **Wire format 21 bytes total** — base TGEvent::WriteToStream writes
  4×i32 (factory_id, event_type, source_obj_ref, dest_obj_ref) via
  the stream's vtable[0x64] and vtable[0x84] slots; subclass appends
  one more i32 via vtable[0x84]; opcode byte = 1.
- **Source/Dest ID encoding** — NULL→0, sentinel `DAT_0095adfc`→
  0xFFFFFFFF, else `*(uint32*)(obj+0x04)` — confirmed via TGEvent
  base WriteToStream `FUN_006d6130` decompile.
- **30 ctor xrefs** — exact match to doc claim. UNCONDITIONAL_CALL
  xrefs enumerated; each maps to a producer function or LAB_ label
  in the producer table.
- **5 vtable DATA xrefs** — exact match to doc. `get_xrefs_to(0x0088869c)`
  returns exactly the 5 listed addresses.
- **TGCharEvent IsA chain** — confirmed as sibling pattern: TGCharEvent
  IsA (FUN_00574c50, byte at +0x28 init via TGCharEvent ctor 0x00574c20)
  returns true for 0x105, 0x101, 0x02 — same chain shape as
  TGObjPtrEvent.
- **All 11 producer event types** — each verified via direct
  decompile (see "Producer verification" below).
- **Dual-fire pattern** — Phaser FUN_00571f40 emits 0x00800081 +
  0x0080007C back-to-back; Tractor FUN_0057f580 emits 0x0080007D
  + 0x0080007C back-to-back; Torpedo FUN_0057c9e0 emits 0x0080007C
  only (single).
- **Host-only gate on 0x008000DC** — `if (DAT_0097fa89 != '\0' &&
  this+0xa4 != 0 && this+0xa8 != 0)` at both FUN_00574010 and
  FUN_005825a0.
- **ET_TARGET_WAS_CHANGED stores previous target** — FUN_005ae210
  reads current target (`iVar1 = FUN_005ae170()`) THEN creates event
  with `*(iVar3+0x28) = *(iVar1+4)` — the OLD target's ID.
- **String pointer RTTI scheme** — confirmed per
  event-system-architecture.md companion. GetClassName returns
  ASCIIZ "TGObjPtrEvent" at 0x008d8594; GetSWIGName returns
  "_p_TGObjPtrEvent" at 0x008d85a4; THIRD function at vtable +0x2C
  returns "TGObjPtrEventPtr" at 0x008d85b8 (see Correction C2).
- **Timer 0x00050001 delivery** — FUN_007022f0 + FUN_007023e0
  emit factory 0x10C with event_type 0x50001 (top half = 5,
  bottom half = 1), destined for global queue `DAT_0099b010`.
- **Repair priority manual-ctor pattern (FUN_005519e0)** — does NOT
  call TGObjPtrEvent_Ctor; instead allocates 0x2C, calls TGEvent
  base ctor FUN_006d5c00, then manually writes vtable at offset 0:
  `*puVar2 = &PTR_FUN_0088869c` (matches the 0x551a5b vtable DATA
  xref). This is why FUN_005519e0 appears in vtable DATA xrefs but
  not in the 30 ctor CALL xrefs.

**Corrected claims:**

1. **C1 — "TGSubsystemEvent (factory 0x101)" is fabricated** (low-
   impact). The doc names 0x101 as a class called "TGSubsystemEvent"
   and writes the hierarchy `0x10C -> 0x101 -> 0x02`. The binary has
   NO class with that name — string search for "TGSubsystemEvent"
   returns 0 matches. The vtable 0x00895FF4 (which the TGEvent base
   ctor `FUN_006d5c00` writes) emits factory_id 0x101 directly from
   its GetFactoryID slot at 0x006d5ce0 (single hit on byte pattern
   `B8 01 01 00 00 C3` = MOV EAX, 0x101 / RET). So **0x101 IS TGEvent**,
   not a separate "TGSubsystemEvent" parent class. The IsA chain
   `0x10C -> 0x101 -> 0x02` is correct in shape; just the middle-link
   name is wrong. 0x02 likely represents the SWIG-base root type
   (no RTTI emitter found for 0x02 in the same factory-id pattern;
   search returned 7 generic-looking hits, none of which is a class
   GetFactoryID). The TGCharEvent (0x105) IsA confirms: same
   `0x105 -> 0x101 -> 0x02` shape — meaning 0x105 and 0x10C are
   SIBLINGS directly under TGEvent (0x101). The doc's class-hierarchy
   diagram needs to remove the TGSubsystemEvent layer and place both
   TGCharEvent and TGObjPtrEvent directly under TGEvent (0x101).

2. **C2 — Vtable slot numbering is off by one (or one extra slot
   missed).** The doc lists slot 0 = scalar_deleting_dtor at
   0x00403310. Direct memory inspection at 0x0088869C shows slot 0 =
   0x00403320 (the real scalar_deleting_dtor for size 0x2C). The
   address 0x00403310 the doc names "scalar_deleting_dtor" is actually
   **a third RTTI string-return function** returning the ASCIIZ
   "TGObjPtrEventPtr" at 0x008d85b8 (NEW finding — call it
   GetSWIGPtrName). The full vtable slot list at 0x0088869C is:

   ```
   slot off addr        function
    0   00  0x00403320  TGObjPtrEvent_ScalarDeletingDtor (size 0x2C)
    1   04  0x004032b0  GetFactoryID -> 0x10C
    2   08  0x004032c0  IsA -> {0x10C, 0x101, 0x02}
    3   0C  0x006f1650  TGEvent inherited
    4   10  0x006d6e20  WriteToStream variant (different stream class)
    5   14  0x006d6e50  ReadFromStream variant
    6   18  0x006d6050  TGEvent inherited
    7   1C  0x006d60b0  TGEvent inherited
    8   20  0x006f15c0  TGEventHandlerObject::InvokePythonHandler
                        (universal — matches event-system mid #8)
    9   24  0x004032f0  GetClassName -> "TGObjPtrEvent"
   10   28  0x00403300  GetSWIGName -> "_p_TGObjPtrEvent"
   11   2C  0x00403310  GetSWIGPtrName -> "TGObjPtrEventPtr" [NEW]
   12   30  0x006d6da0  CopyFrom (base + obj_ptr)
   13   34  0x006d6dc0  WriteToStream (network)
   14   38  0x006d6df0  ReadFromStream (network)
   15   3C  0x00403500  ScalarDeletingDtor (size 0x34 — subclass variant)
   16   40  0x006ffa90  Handler invocation pattern (reads +0x20/+0x24/+0x28)
   ```

   The doc's "Slots 3-8, 11, 15-17 inherited from TGEvent base" line
   misses that slots 11 and 15 are NOT inherited — slot 11 is the
   new GetSWIGPtrName method and slot 15 is a separate size-0x34
   scalar deleting destructor (subclass variant, matches the doc's
   own "0x00403570 destructor variant (size 0x34 subclass?)" hint
   in the Infrastructure section — confirmed). Total vtable is at
   least 17 slots (through +0x40), not the "vtable [12, 13, 14]"
   the doc body describes.

3. **C3 — Phaser/Tractor xref counting is exact-but-confusable.**
   The doc lists `0x005712FE` (PhaserStop) and `0x005768C5`
   (WeaponSystem) as unanalyzed vtable-DATA-write sites. They ARE
   unanalyzed — but they're INSIDE the bodies of fully-analyzed
   functions (FUN_00571f40 Phaser::Fire and an unnamed weapon
   function), as part of the dual-fire / weapon emission pattern.
   The doc's table mixes "address is in unanalyzed region" with
   "address is in a defined function but not at a function boundary".
   For Phaser at 0x005712fe specifically: the vtable write happens
   in **a code region that has no function defined** (between
   PhaserSystem ctor area and FUN_00571f40); this is a SEPARATE
   producer site that did not show up in our 30 ctor CALL xrefs
   list (it's a vtable-write-only site, like FUN_005519e0). So the
   doc's "Vtable DATA References" enumeration of 5 sites is accurate,
   but the "C++ Producers in Unanalyzed Code Regions" table mistakes
   address-inside-existing-functions for genuinely unanalyzed code.

**Dropped claims:** None — all 11 game event types verified.

**SWIG wrapper functions** (5 in the doc body): the addresses
0x005C7F10 / 0x005C7F90 / 0x005C8000 / 0x005C8070 / 0x005C80E0 are
**NOT defined as functions** in the Ghidra database (annotation
scripts never applied to current import — see engine-snapshot-
20260528.md). The string identifiers (`new_TGObjPtrEvent`,
`TGObjPtrEvent_Cast`, `TGObjPtrEvent_Create`, `TGObjPtrEvent_GetObjPtr`,
`TGObjPtrEvent_SetObjPtr`) are confirmed at 0x0092eab0..0x0092eaf4
in the SWIG PyMethodDef name region, but the doc's specific
function-address claims for these wrappers are **inherited from
prior annotation runs** and not independently verifiable in the
current Ghidra DB. The SWIG NAME strings exist; the function
addresses are not anchored this pass. Recommend either (a) re-run
`tools/ghidra_annotate_swig.py` to apply names + create the
function entry points, or (b) demote the address-specific SWIG
table to `confidence: medium` with a note. No corrections needed
to the doc's behavioral claims about Python usage (those are
cross-source from script analysis, not binary-anchored).

**New factual sections recommended:**

- **GetSWIGPtrName as a separate vtable slot** — the third RTTI
  string-return method "TGObjPtrEventPtr" deserves a callout. Same
  pattern exists for TGCharEvent (TGCharEventPtr at 0x008e54ec) and
  ObjectExplodingEvent (ObjectExplodingEventPtr at 0x008da2a0).
  This is SWIG's pointer-typeinfo string used for Python script
  type negotiation distinct from the stream-RTTI "_p_TGObjPtrEvent".
- **Class hierarchy correction** — replace "TGSubsystemEvent (0x101)"
  layer with "TGEvent (0x101)" directly; TGCharEvent and TGObjPtrEvent
  are siblings under TGEvent. The "0x02" parent class is the SWIG
  base root, not a named C++ class in BC.
- **Vtable layout expanded** — list all 17 known slots with their
  function names + roles, distinguishing inherited-no-override
  (Slots 3, 6, 7) from inherited-but-special-meaning (Slot 4-5
  variant Write/Read for the "fixup-flag" stream class) from
  TGObjPtrEvent-overridden slots.

**Producer verification (cross-reference grid):**

| Address | Decompiled fn name | event_type written to +0x10 | obj_ptr source | Doc claim |
|---------|--------------------|----------------------------|----------------|-----------|
| 0x004066f6 (in 0x004066d0) | Game_SetPlayerLocal | 0x0080000E | param_2+4 (new player) | ET_SET_PLAYER ✓ |
| 0x005ae270 (in 0x005ae210) | Ship_SetTarget | 0x00800058 (DAT_00800058) | iVar1+4 (PREVIOUS target) | ET_TARGET_WAS_CHANGED ✓ stores previous |
| 0x0056c4fa (in 0x0056c470) | ShipSubsystem_SetCondition | 0x0080006B (DAT_0080006B) | param_1+4 (this subsystem) | ET_SUBSYSTEM_HIT ✓ |
| 0x551a5b (in 0x005519e0) | RepairSubsystem_RaisePriority | 0x00800076 (DAT_00800076) | param_1+4 (repair target) | ET_REPAIR_INCREASE_PRIORITY ✓ |
| 0x00572074 (in 0x00571f40) | Phaser::Fire | 0x00800081 (DAT_00800081) | target_id via 0x006f0ee0 | ET_PHASER_STARTED_FIRING ✓ |
| 0x005720df (in 0x00571f40) | Phaser::Fire | 0x0080007C (DAT_0080007c) | target_id via 0x006f0ee0 | ET_WEAPON_FIRED ✓ dual fire |
| 0x0057caa2 (in 0x0057c9e0) | Torpedo::Fire | 0x0080007C (DAT_0080007c) | 0 (constant) | ET_WEAPON_FIRED ✓ single |
| 0x0057f64b (in 0x0057f580) | Tractor::Fire | 0x0080007D (DAT_0080007d) | target_id via 0x006f0ee0 | ET_TRACTOR_BEAM_STARTED_FIRING ✓ |
| 0x0057f6b3 (in 0x0057f580) | Tractor::Fire | 0x0080007C (DAT_0080007c) | target_id via 0x006f0ee0 | ET_WEAPON_FIRED ✓ dual fire |
| 0x00568afd (in 0x00568ad0) | unnamed sensors | 0x00800088 (DAT_00800088) | iVar1+4 (identified ship) | ET_SENSORS_SHIP_IDENTIFIED ✓ |
| 0x005678ec (in 0x005678b0) | unnamed sensors | 0x00800088 (DAT_00800088) | param_2+1 (identified ship) | ET_SENSORS_SHIP_IDENTIFIED ✓ |
| 0x00580ce6 (in 0x00580910) | tractor dock | 0x00800085 (DAT_00800085) | piVar3[1] (docked ship) | ET_TRACTOR_TARGET_DOCKED ✓ |
| 0x0057405e (in 0x00574010) | PhaserSystem_StopFiringAtTarget | 0x008000DC (DAT_008000dc) | param_2+4 (target) | ET_STOP_FIRING_AT_TARGET_NOTIFY ✓ HOST-ONLY |
| 0x005825ee (in 0x005825a0) | TractorBeamSystem_StopFiringAtTarget | 0x008000DC (DAT_008000dc) | param_2+4 (target) | ET_STOP_FIRING_AT_TARGET_NOTIFY ✓ HOST-ONLY |
| 0x0070232e (in 0x007022f0) | AI timer producer | 0x00050001 | param_1[1] (timer source) | Timer delivery ✓ |
| 0x00702407 (in 0x007023e0) | AI timer producer | (assumed 0x00050001) | (similar) | Timer delivery ✓ (not re-decompiled) |

The remaining ~14 xrefs are infrastructure (dtors at 0x004028dd,
0x00403570) plus the LAB_-only sites the doc inventories in its
"Unanalyzed Code Regions" table — those align with subsystem
producer regions the doc names correctly.

**Open questions left for downstream rows:**

1. **Slot 4-5 "variant" Write/Read at 0x006d6e20 + 0x006d6e50** — these
   are pre-conditional WriteToStream/ReadFromStream gated on a
   different base-class type check (FUN_006d5ec0 / FUN_006d5ff0).
   Doc never mentions them. Suspect: SAVE/LOAD (persistent storage)
   vs NETWORK serialization split — slot 13/14 (network) writes
   unconditionally; slots 4/5 check a save-stream-class flag first.
   Requires investigation of FUN_006d5ec0 / FUN_006d5ff0 (likely
   `TGStream::CanSerializeToWire` vs `TGStream::CanSerializeToSave`).
2. **Vtable slot 16 (0x006ffa90)** — reads `this+0x20`, `this+0x24`,
   `this+0x28`. The +0x20/+0x24 fields are labelled "reserved" in
   the doc; this slot proves they ARE used (probably handler-invocation
   metadata for Python script dispatch). Worth confirming with
   pythonevent-wire-format.md row #14.
3. **SWIG wrapper addresses 0x005C7F10..0x005C80E0** — not anchored
   in the current Ghidra DB. Need annotation-script re-run OR demote
   to medium confidence.
4. **The 0x02 root SWIG type identity** — IsA returns true for 0x02
   as the grandparent factory ID, but no GetFactoryID emitter for
   factory 0x02 found. Likely a SWIG-base "object" type with no
   real C++ class. Worth checking SWIG type-info table layout.
5. **Repair priority manual-ctor pattern** — FUN_005519e0 hand-rolls
   the vtable assignment instead of calling TGObjPtrEvent_Ctor.
   This is a HOT path in MP repair flow. Worth verifying the
   resulting object passes IsA(0x10C) — if so, the wire format is
   identical; if not, downstream handlers could misclassify. Static
   analysis suggests it IS identical (same vtable, same +0x28 init
   pattern), but no emulation done.

**Files touched:** `docs/protocol/v5-validation-status.md` (this
row added; §2 row #13 status flipped to partial; §3.13 inventory
will be refreshed when documentation-writer renders the corrected
doc; §7.7 event-class anchor table for TGObjPtrEvent vtable expanded
from 12 slots to 17 slots when restructure happens).

---

### 6.14 pythonevent-wire-format.md — 2026-05-28 (game-archaeology-specialist)

**Status:** validated -> `partial`. ZERO wire-format byte-count
corrections (all 4 class sizes — 16 / 17 / 20 / 24 bytes — confirmed
byte-by-byte via WriteToStream decompiles + stream vtable slot
verification). FIVE non-wire corrections: hierarchy fabrication
(C1 — same as tgobjptrevent #13 cascade), ObjectExploding IsA
chain misnaming (C2), source/dest WriteObjectRef encoding asymmetry
(C3 — refinement), receiver-flow function-name approximation
(C4 — `EventManager::PostEvent` is actually Event-self-dispatch via
event->dest_obj vtable), and ObjectExplodingEvent's wire size
incorrectly given as 25 in doc Example heading (C5 — text says "25"
but layout sums to 24 + opcode = 25 total). All producer behavior
matches doc; both undefined-in-DB handler bodies confirmed via raw
disassembly.

**Methodology:** Phase 1-5 per v5 workflow. `program: STBC.exe` on
every MCP call. Doc anchors against doc #13 (just validated) for
TGObjPtrEvent details + engine doc #8 for TGEvent base/vtable +
doc #4 for opcode dispatch + doc #7 for routing.

**Functions touched (completeness):**

| Function | Addr | effective_score | Plate? |
|----------|------|-----------------|--------|
| MpgameHandlePythonEvent | 0x0069f880 | 22.14 | yes |

Single function renamed + prototyped + plated. The four event-class
serialization functions (WriteToStream / ReadFromStream pairs) and
the two producer-handler functions (HostEventHandler 0x006A1150,
ObjectExplodingHandler 0x006A1240) were either undefined in DB or
already named-and-plated by prior passes; no incremental v5 edits.

**Wire-format CONFIRMATION (per class, byte-by-byte):**

| Class | Factory | Base | Ext | Total payload | + opcode | Confirmed via |
|-------|---------|------|-----|---------------|----------|----------------|
| TGEvent | 0x0101 | 16 | 0 | 16 | 17 | FUN_006D6130 — 4 calls × 4-byte writes (vtable+0x64 ×2 + vtable+0x84 ×2) |
| TGCharEvent | 0x0105 | 16 | 1 | 17 | 18 | 0x006D6940 disasm — base call + `CALL [EAX+0x54]` (vtable+0x54 = WriteChar 1 byte) |
| TGObjPtrEvent | 0x010C | 16 | 4 | 20 | 21 | TGObjPtrEvent_WriteToStream 0x006D6DC0 (already v5-plated in doc #13) |
| ObjectExplodingEvent | 0x8129 | 16 | 8 | 24 | **25** | FUN_0043F990 — base + vtable+0x6C (i32 firing_player) + vtable+0x74 (f32 lifetime) |

Stream vtable slot map (TGBufferStream SWIG variant vtable
0x00895C58 — confirmed via raw memory dump + decompile of each):

| Slot offset | Address | Method | Byte cost |
|-------------|---------|--------|-----------|
| +0x60 | 0x006CF640 | ReadInt (raw 4-byte) | 4 |
| +0x64 | 0x006CF830 | WriteInt (raw 4-byte) | 4 |
| +0x68 | 0x006CF670 | ReadInt (alias) | 4 |
| +0x6C | 0x006CF870 | WriteInt (alias) | 4 |
| +0x70 | 0x006CF6B0 | ReadFloat | 4 |
| +0x74 | 0x006CF8B0 | WriteFloat | 4 |
| +0x80 | 0x006CF6A0 | ReadInt virtual dispatcher (forwards to +0x68) | 4 |
| +0x84 | 0x006CF930 | WriteInt virtual dispatcher (forwards to +0x6C) | 4 |
| +0x50 | 0x006CF540 | ReadChar (1 byte) | 1 |
| +0x54 | 0x006CF730 | WriteChar (1 byte) | 1 |

NOTE: slot +0x64 and +0x6C end up writing 4 raw bytes each. The +0x80/+0x84
slots are virtual dispatchers that forward to +0x68/+0x6C in the SWIG-
visible class. They look like "polymorphic" hooks but in this class they're
fixed-width.

**Confirmed claims (high confidence):**

- **Opcode 0x06 + 0x0D shared receiver FUN_0069F880** — receiver
  decompile confirms NO opcode-byte inspection; dispatcher (FUN_0069F2A0
  jump-table slots 6 and 13) routes both to this function. Doc claim
  byte-by-byte confirmed.
- **Receiver flow** — 8 steps: GetBufferAndSize / Ctor / OpenBuffer-skip-1 /
  ReadObjectFromStream (006D6200) / ResolveRefs (006F13C0) / clear +0x24 /
  PostEvent (006DA300) / refcount-release. Confirmed via decompile.
- **Factory-tag-first wire format** — ReadObjectFromStream reads factory_id
  via `stream->vtable[+0x60]` (4 raw bytes), looks up TGFactoryCreate
  (006F13E0), instantiates concrete class, calls `event->vtable[+0x38]`
  (= ReadFromStream). Confirmed via FUN_006D6200 decompile.
- **HostEventHandler 0x006A1150 producer flow** — byte-by-byte via raw
  disasm: reads g_TGWinsockNetwork at 0x97FA78, stores opcode 0x06 byte at
  stack +0x3C, calls SWIG TGBufferStream_Ctor (0x006CEFE0), OpenBuffer
  with cap 0x3FF, invokes event->vtable[+0x34] = WriteToStream, allocates
  TGMessage(0x40) via TGAlloc, sets msg+0x3A = 1 (reliable), calls
  SendTGMessageToGroup (0x006B4DE0) with "NoMe" string at 0x008E5528. All
  matches doc verbatim.
- **ObjectExplodingHandler 0x006A1240 dual-path** — confirmed via raw
  disasm. MP path at 006A126A is byte-identical to HostEventHandler. SP
  path at 006A131B does `FLD [event+0x2C]; FSTP [ship+0x14C]` then calls
  FUN_005AC250 (Python `Effects.ObjectExploding`). MP/SP gate is
  `MOV AL, [0x97FA8A]; TEST AL,AL; JZ` (g_IsMultiplayer test).
- **Event registration in MultiplayerGame_Ctor (0x0069E590)** — confirmed
  via decompile:
    - 0x008000DF + 0x00800074 + 0x00800075 -> HostEventHandler (host-only
      gate `DAT_0097fa8a != 0`)
    - 0x0080004E -> ObjectExplodingHandler (ALWAYS-on, gate is internal)
  Cross-doc consistency with python-messages.md plate comment.
- **Class hierarchies via IsA decompile**:
    - TGCharEvent IsA (0x00574C50) -> true for 0x105, 0x101, 0x02
    - TGObjPtrEvent IsA (0x004032C0) -> true for 0x10C, 0x101, 0x02
    - ObjectExploding IsA (0x0043F8F0) -> true for 0x8129, **0x101**, 0x02
  All three sibling classes inherit from TGEvent base (0x101). The doc's
  hierarchy diagram puts ObjectExploding as a sibling of "TGSubsystemEvent"
  but reality is they all share TGEvent base.
- **TGEvent base GetFactoryID** — at 0x006D5CE0 = `MOV EAX, 0x101; RET`.
  Confirms 0x101 IS TGEvent itself (cross-anchor with doc #13 C1).
- **TGObjPtrEvent obj_ptr encoding** — producer-side stores already-
  resolved network ID at `+0x28` (no NULL/sentinel translation needed
  at write time; the producer encodes NULL->0 itself). Verified via
  RepairSubsystem_RaisePriority (0x005519e0) producer pattern:
    `if (param_1 == 0) uVar3 = 0; else uVar3 = *(undefined4 *)(param_1 + 4);`
    `puVar2[10] = uVar3;`  (puVar2[10] = +0x28)
- **"NoMe" group string** — at 0x008E5528 = ASCIIZ "NoMe" (confirmed
  via memory dump).
- **ObjectExploding vtable @ 0x0088A178** — 18-slot table dumped:
    +0x04 = 0x0043F8E0 GetFactoryID -> 0x8129
    +0x08 = 0x0043F8F0 IsA
    +0x18/+0x1C = 0x006D6050 / 0x006D60B0 (ResolveRefs — inherited from TGEvent)
    +0x24 = 0x0043F920 GetClassName -> "ObjectExplodingEvent" @0x008DA270
    +0x28 = 0x0043F930 GetSWIGName -> "_p_ObjectExplodingEvent" @0x008DA288
    +0x30 = 0x006D6230 CopyFrom (inherited)
    +0x34 = 0x0043F990 WriteToStream (verified)
    +0x38 = 0x0043F9C0 ReadFromStream (verified)

**Corrected claims:**

1. **C1 — class hierarchy "TGSubsystemEvent (factory 0x101)" is
   fabricated** (cascade from doc #13 C1). The doc has a hierarchy
   diagram with `TGSubsystemEvent (factory 0x101)` as the parent of
   TGCharEvent/TGObjPtrEvent. Binary: GetFactoryID at TGEvent base
   (0x006D5CE0) emits 0x101 directly. NO TGSubsystemEvent class exists
   anywhere — no RTTI string, no vtable, no ctor, no IsA branch with
   that name. The doc's "Event Class 1: TGSubsystemEvent (factory 0x101)"
   section header should read "Event Class 1: TGEvent (factory 0x101)"
   and the inheritance diagram should be:
     `NiObject -> TGEvent (0x101)`
                     `├── TGCharEvent (0x105) [+1 byte]`
                     `├── TGObjPtrEvent (0x10C) [+4 byte obj_id]`
                     `└── ObjectExplodingEvent (0x8129) [+4 player + +4 lifetime]`
   The "vtable 0x008932A4" address claimed for TGSubsystemEvent has
   ZERO xrefs in the binary (confirmed via `get_xrefs_to`). Class
   layout for "TGSubsystemEvent" should be re-labeled as TGEvent base.

2. **C2 — ObjectExplodingEvent IsA chain is 3-IDs, not 2** (low impact).
   Doc says "ObjectExplodingEvent::IsA returns true for 0x8129
   (ObjectExplodingEvent), 0x02 (TGEvent)". Binary disasm of
   0x0043F8F0 returns true for **0x8129, 0x101, 0x02** (three IDs).
   ObjectExplodingEvent inherits from TGEvent (0x101) just like the
   other event subclasses. This is a 1-line text fix to the doc's
   IsA Chain bullet list.

3. **C3 — Object Reference Encoding has source/dest asymmetry**
   (refinement). Doc says `WriteObjectRef` has 3 cases (NULL / sentinel /
   valid). Binary FUN_006D6130 disasm shows:
     - SOURCE field (this+0x08): TWO cases — `if NULL -> 0; else *(obj+4)`.
       NO sentinel test. There is no path that writes 0xFFFFFFFF for
       the source.
     - DEST field (this+0x0C): THREE cases — `if sentinel -> -1; elif
       NULL -> 0; else *(obj+4)`.
   Practical impact: minimal (a producer would have to manually set
   source to the sentinel pointer for this to matter, and that doesn't
   happen in the binary). Replace the single "WriteObjectRef" rule with
   per-field rules in the doc.

4. **C4 — receiver Step 6 name "EventManager::PostEvent" approximates**
   (refinement). Doc says "Post event to local event system via
   FUN_006da300". Actual decompile of 006DA300 shows it reads
   `event->dest_obj` (this+0x0C), and invokes `dest_obj->vtable[+0x50]`.
   This is **Event::Dispatch** — the event invokes itself on its dest
   object's event handler. The name "PostEvent" is acceptable as an
   abstract description but technically misleading. Suggest renaming
   in the doc plate to `TGEvent::Dispatch` or `Event::SelfDispatch`.

5. **C5 — ObjectExplodingEvent wire example header says "(25 bytes)"
   matches layout but doc has it in the heading not the text**. The doc
   actually says "Total: 25 bytes (fixed)" in the example block but
   "24 bytes" in the inheritance diagram (`size 0x30, +0x28 = int32,
   +0x2C = float`). The CLASS size is 0x30 (48 in-memory); WIRE size is
   16 base + 8 ext = 24 payload + 1 opcode = 25 wire. Both numbers are
   correct in their respective contexts; the doc's prose is ambiguous
   and should clarify in-memory vs wire size.

**Dropped claims (none material).** The "TGCharEvent vtable 0x008932DC"
address remains correct as a reference (data xref to 0x008932DC confirmed
from FUN_00574C20 ctor at 0x00574C2D — meaning a vtable DOES exist there,
even though the doc's "vtable @ 0x008932DC" 14-slot table needs slot
recount — the SWIG triple-string scheme means slot +0x2C is GetSWIGPtrName
not "CopyFrom"; same correction as doc #13 C2).

**Open questions:**

- The doc's "Worked Example" claims 14 messages per collision (1 ObjectExploding
  + 13 ADD_TO_REPAIR_LIST), but "Collision Chain Event Count" near the end
  claims 12-14 with 1 + 11 + 2 delayed = 14. The math is inconsistent (11 + 2
  = 13 — not 14). Real ground-truth would require packet trace replay against
  a known collision. Suggest documentation-writer reconciles or labels as
  "approximate" in both places.
- The doc says PlayerN base ID is `0x3FFFFFFF + N * 0x40000`. The constant
  0x3FFFFFFF appears in `DAT_0095adfc` as the dest-sentinel. The Player0
  base claim is consistent with the sentinel value chosen so that an
  uninitialized ship (id = sentinel) wraps to player 0's base ID minus
  one. Not validated this pass; suggest cross-anchor with
  objcreate-serialization (doc #10) which has player base ID anchored.
- Subsystem ID assignment via `DAT_0095B078` global counter is doc-cited
  but not verified this pass. The receive-side hash table at `DAT_0099A67C`
  IS doc-cited; not verified this pass.

**Cross-doc anchor reuse:**

- **From doc #13 (tgobjptrevent-class.md):** TGObjPtrEvent vtable 0x0088869C,
  factory 0x010C, size 0x2C, wire 21B — directly inherited (no re-derivation).
- **From doc #7 (tgmessage-routing.md):** LOCAL-ONLY dispatch (no relay) at
  FUN_0069F880 — confirmed (no SendToGroup in receiver body).
- **From doc #4 (game-opcodes.md):** dispatcher slots 6 (PythonEvent) and
  13 (PythonEvent2) both route to FUN_0069F880 — confirmed via dispatcher
  jump table (recorded in doc #4 validation).
- **From engine doc #8 (event-system-architecture.md):** TGEvent vtable
  0x00895FF4, sizeof 0x28 — confirmed; slot +0x34 = WriteToStream and
  slot +0x38 = ReadFromStream consistent with that doc's vtable table.

**Verification methods used:**
- `decompile_function` for receiver + base WriteToStream/ReadFromStream
  + ObjectExploding WriteToStream/ReadFromStream + ResolveRefs +
  Event::Dispatch + RepairSubsystem_RaisePriority producer + ctor +
  base ctor + MultiplayerGame_Ctor + IsA functions.
- `disassemble_bytes` for the two undefined-in-DB producer functions
  (HostEventHandler 0x006A1150, ObjectExplodingHandler 0x006A1240),
  TGEvent base GetFactoryID, TGCharEvent serialize pair, ObjectExploding
  IsA + GetClassName + GetSWIGName, stream vtable slot 0x64 writer.
- `read_memory` for stream SWIG vtable @ 0x00895C58 (160 bytes) and
  ObjectExplodingEvent vtable @ 0x0088A178 (80 bytes).
- `inspect_memory_content` for "NoMe" group string verification.
- `get_xrefs_to` for vtable address xref counts (TGSubsystemEvent vtable
  address has 0 xrefs — confirms fabrication).

**Files touched:** `docs/protocol/v5-validation-status.md` (this row
added; §2 row #14 status flipped to partial; §3.14 inventory will be
refreshed when documentation-writer renders the corrected doc).

---

### 6.15 collision-effect-protocol.md — 2026-05-28 (game-archaeology-specialist)

**Status:** validated -> **`verified`**. **First protocol family doc to
clear the `verified` bar** (and the first leaf doc in protocol family).
All 110+ load-bearing claims confirmed byte-by-byte against the current
Ghidra import. ZERO material wire-format changes. Just 1 byte-level typo
(C1: handler-table line 293 had `0x005afab0` for `ShipClass::HostCollisionEffectHandler`,
correct is `0x005AFAD0` — the doc's own main "Related Functions" table at
line 318 already has it right) and 1 wording clarification (R1: PostEvent
re-tag is __thiscall to TGEventManager singleton at 0x0097F838, not a
"queue push to DAT_0097f838").

**Critical OpenBC finding confirmed**: Stock dedi `CollisionEffectHandler`
(0x006A2470) does NOT recompute collision contact points or force values.
After 3 gates (ownership / self-collision / distance gap < 26.0f) it
accepts the client-supplied `event.force` as-is and re-posts the event for
`Ship_HostCollisionEffectHandler` (0x005AFAD0) to apply damage from the
client-claimed value. This is the binary backing for CLAUDE.md's "Collision
damage authority inverted" note. Negative-claim verified by full-body
decompile of FUN_006A2470: no FMUL/FDIV on contact/force fields after
deserialize, no STR writes to event+0x40 (force) or event+0x2C (contact
array).

**Methodology:** Phase 1-5 per v5 workflow. `program: STBC.exe` on every
MCP call. Doc anchors against engine doc #8 (TGEvent vtable 0x00895FF4),
doc #4 (game-opcodes opcode 0x15 dispatcher row), doc #14 (PythonEvent
cross-anchor — collision feeds into the PythonEvent 0x06 damage cascade
downstream via ADD_TO_REPAIR_LIST + ObjectExploding).

**Functions touched (completeness):**

| Function | Addr | effective_score | Plate? |
|----------|------|-----------------|--------|
| CollisionEffectHandler | 0x006A2470 | high | yes (added) |
| Ship__HostCollisionEffectHandler | 0x005AFAD0 | high | yes (renamed) |
| GetShipFromPlayerID | 0x006A1AA0 | high | yes (renamed) |
| IsLocalPlayerShip | 0x005AE140 | high | yes (renamed) |
| CastToShipClass | 0x005AB670 | high | yes (renamed) |
| TGFactory_DeserializeObject | 0x006D6200 | high | yes (renamed) |
| TGEventManager__PostEvent | 0x006DA2A0 | high | yes (renamed) |

**Wire-format CONFIRMATION (byte-by-byte):**

| Section | Claim | Verified via |
|---------|-------|--------------|
| Constant prefix | 13 bytes `15 24 81 00 00 50 00 80 00 00 00 00 00` | 3 example packets decoded vs class layout |
| Total size | `22 + count*4` bytes | layout sum: opcode(1) + class(4) + code(4) + src(4) + tgt(4) + count(1) + n*4 + force(4) |
| Class layout | 0x44 bytes, 18 fields | ctor 0x00586D00 decompile + vtable 0x0089395C dump |
| Vtable | 17 slots at 0x0089395C | `read_memory` dump; every slot target matches doc |
| Network serialization pair | WriteToStream 0x005871A0 / ReadFromStream 0x00587300 | vtable+0x34/+0x38 slots + raw disasm of prologue bytes |
| Persistence pair | WriteStream 0x00586FB0 / ReadStream 0x00587030 | vtable+0x10/+0x14 slots |

**Confirmed claims (high confidence):**

- **Dispatcher route opcode 0x15** — jump-table at `0x0069F534` slot index
  `(0x15 - 2) = 0x13`, offset 0x4C, byte address `0x0069F580` reads
  `91 F4 69 00` -> thunk at **`0x0069F491`** -> `CALL 0x006A2470`. Cross-
  anchor with doc #4 (game-opcodes dispatcher recovery).
- **Distance gate constant = 26.0f** — `_DAT_008955C8` raw bytes
  `00 00 D0 41` = 0x41D00000 = 26.0f. Compared via `FCOMP [0x008955C8]`
  at 0x006A25DF; branched at JZ 0x006A25EA. The full algorithm:
    `dist = sqrt((p1-p2).x^2 + (p1-p2).y^2 + (p1-p2).z^2)` via FSQRT at 0x006A25B7
    `r1 = ship1->vtable[+0xE4]()[+0x0C]` (GetModelBound bbox radius)
    `r2 = ship2->vtable[+0xE4]()[+0x0C]`
    `gap = dist - r1 - r2`; reject if `gap >= 26.0f`.
- **Damage cascade constants (all 4 byte-verified):**
    - `_DAT_00888A78` = `0A D7 23 3C` = 0x3C23D70A = **0.01f** (dead-zone)
    - `_DAT_008944BC` = `00 00 61 44` = 0x44610000 = **900.0f** (HP scale)
    - `_DAT_008944B8` = `00 00 FA 43` = 0x43FA0000 = **500.0f** (HP base)
    - Force-scale arg = `0x3FC00000` = **1.5f** (3rd param at call from
      HostCollisionEffectHandler to SubsystemDamageDistributor 0x005AFD70)
  Formula: `raw = (event.force / ship.mass) / contactCount; if (raw > 0.01f) damage = raw * 900 + 500`.
- **Event re-tag + PostEvent disasm pattern** (0x006A25EC-0x006A25F9):
    ```
    PUSH ESI                       ; event
    MOV  ECX, 0x97F838             ; this = g_pEventManager
    MOV  [ESI+0x10], 0x008000FC    ; event->type = ET_HOST_OBJECT_COLLISION
    CALL TGEventManager__PostEvent ; FUN_006DA2A0
    ```
  Confirms doc's "event manager at 0x0097F838" but the function is __thiscall
  (ECX=this), not "post to DAT queue". `FUN_006DA2A0` thunks to `FUN_006DE330`
  which is the dispatch loop.
- **CompressedVec4_Byte read primitive** — `DecompressVec4_Byte` at 0x006D30E0
  is the stream vtable+0x9C entry. Reads 4 bytes via vtable+0x50 (ReadByte)
  then dispatches via vtable+0xBC for radius-scaled Vec3 reconstruction.
  `CompressVec4_Byte_Direction` at 0x006D29A0 and `CompressVec4_Byte_Magnitude`
  at 0x006D2D10 are vtable+0xA0 / +0xAC of the writer stream class.
- **3 helper functions byte-verified:**
    - `GetShipFromPlayerID` (0x006A1AA0): iterates `DAT_0097E9C8` game-set
      list, matches `ship+0x2E4 == player_id`. __cdecl.
    - `IsLocalPlayerShip` (0x005AE140): on host (`DAT_0097FA89 != 0`) returns
      `ship+0x2E4 != 0`; off-host returns `FUN_004069B0() == ship`.
    - `CastToShipClass` (0x005AB670): calls `ship->vtable[+8](0x8008)`
      (NiObject::IsA-style check for ship class ID 0x8008).
- **Vtable at 0x0089395C — 17 slots all match doc body table** byte-for-byte
  via `read_memory` dump. No slot reassignment, no slot count delta.
- **Trace cross-anchor** — 84/session frequency, C->S only confirmed via
  relay-audit-20260224 (2 C->S / 0 S->C observed). Matches wire-format-spec
  foundation #1 and the doc's "138,695 packets / 0 relays" claim.

**Corrected claims:**

1. **C1 — Handler-table line 293 byte-level typo.** Doc line 293 reads
   `ET_HOST_OBJECT_COLLISION (0x008000FC) -> ShipClass::HostCollisionEffectHandler (0x005afab0)`.
   Correct address is **`0x005AFAD0`**. The doc's own main "Related
   Functions" table at line 318 already has `0x005afad0` for this function.
   This is a 2-byte typo (the registration callout snippet had `b0` where
   it should have `d0`).

2. **R1 — PostEvent semantics clarification (refinement, not bug).** Doc
   step 12 says "Post to event queue at DAT_0097f838". The actual pattern
   is a __thiscall to TGEventManager singleton: `MOV ECX, 0x97F838; CALL
   0x006DA2A0`. The function is `TGEventManager::PostEvent` taking this in
   ECX and the event as 1st stack arg. The disasm pattern is the standard
   MSVC __thiscall invocation. "Queue push" was the abstract effect, but
   the binary signature is a virtual dispatch into a synchronous handler
   loop. Doc text updated to reflect the singleton semantics.

**Dropped claims:** None.

**Open questions:** None blocking. The hash-cascade claim
"DamageableObject::CollisionEffectHandler" -> Python "Effects.CollisionEffect"
(string at 0x008E5CC8, dispatch via FUN_006D92D0) is downstream-scope and
lives in `docs/gameplay/damage-system.md`. TGEvent vtable slot-count
disagreement (open from leaf #14 cross-doc reconciliation) is not relevant
here — this doc uses the 16-slot TGEvent base table consistent with
engine doc #8.

**Cross-doc anchor reuse:**

- **From doc #4 (game-opcodes.md):** opcode 0x15 row (handler 0x006A2470,
  total = 22 + count*4 bytes, wire layout) — confirmed.
- **From doc #14 (pythonevent-wire-format.md):** ObjectExploding +
  ADD_TO_REPAIR_LIST PythonEvents fire downstream from collision damage
  — confirmed as the collision -> 0x06 cascade. The leaf #14 doc covers
  the PythonEvent half of the chain; this doc covers the opcode 0x15
  half.
- **From engine doc #8 (event-system-architecture.md):** TGEvent base
  vtable 0x00895FF4 (16 slots used here for reference). Consistent.
- **From wire-format-spec foundation #1:** TGEventManager singleton at
  0x0097F838, ET_OBJECT_COLLISION 0x00800050, ET_HOST_OBJECT_COLLISION
  0x008000FC, ET_COLLISION_DAMAGE 0x00800053. All consumed; no overrides.

**Verification methods used:**
- `decompile_function` on CollisionEffectHandler (0x006A2470),
  Ship__HostCollisionEffectHandler (0x005AFAD0), GetShipFromPlayerID
  (0x006A1AA0), IsLocalPlayerShip (0x005AE140), CastToShipClass
  (0x005AB670), CollisionEvent ctor (0x00586D00), GetPointInternal
  (0x00595410), TGFactory_DeserializeObject (0x006D6200),
  TGEventManager__PostEvent (0x006DA2A0).
- `disassemble_bytes` for the undefined-in-DB cluster (WriteToStream
  0x005871A0, ReadFromStream 0x00587300, ShipClass::CollisionEffectHandler
  0x005AF9C0, CompressVec4_Byte primitives 0x006D29A0/0x006D2D10).
- `read_memory` for CollisionEvent vtable @ 0x0089395C (68 bytes, 17 slots),
  TGEvent base vtable @ 0x00895FF4 reference.
- `inspect_memory_content` for the 4 damage constants
  (0x008955C8 / 0x00888A78 / 0x008944BC / 0x008944B8) and the
  `"Effects.CollisionEffect"` string at 0x008E5CC8.
- `get_xrefs_to` for the 0x008000FC / 0x00800050 / 0x00800053 address-as-
  constant pattern (xrefs are exclusively immediate-operand uses, no
  data-reads, confirming the address-as-identifier semantics).

**Files touched:** `docs/protocol/v5-validation-status.md` (this row added;
§2 row #15 status flipped to `verified`); `docs/protocol/collision-effect-protocol.md`
(rendered with v5 header, NOTE block, Server-Side Authority Note,
Ghidra Annotations Applied section, C1 typo fix, R1 PostEvent clarification,
all section tables tagged `[v5-validated 2026-05-28]`).

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

### 6.16 set-phaser-level-protocol.md — 2026-05-28 (game-archaeology-specialist)

**Status:** validated -> **`verified`** (after 3 minor non-wire corrections).
**Sixteenth protocol doc** under v5 — second protocol leaf (after #15
collision-effect-protocol) to clear the `verified` bar. ZERO material
wire-format corrections — the 18-byte SetPhaserLevel packet (1B opcode +
4B factory + 4B eventType + 4B source-ref + 4B target-ref + 1B charValue)
is byte-by-byte accurate.

**Foundation cross-anchors all hold:**
- TGCharEvent class layout (0x2C, +0x28 = char) per mid #13 — `FUN_00574C20`
  ctor verified setting vtable=0x008932DC and writing `(byte)0` to +0x28
- TGCharEvent IsA chain {0x105, 0x101, 0x02} per mid #13 — verified at
  `FUN_00574C50` (B8 05 01 / B8 01 01 / CMP 0x02 — three exact branches)
- 18-byte wire format per leaf #14 — verified via TGCharEvent::WriteToStream
  (`0x006D6940`, CREATED this session) calling base `FUN_006D6130` (16B)
  then `WriteByte` of `event+0x28` (1B)
- Generic event-forward `FUN_0069FDA0` — verified jump-table slot for
  opcode 0x12 at `0x0069F3C7`: `PUSH 0; PUSH ESI; MOV ECX,EDI; CALL FUN_0069FDA0`
  (PUSH 0 = no event-type override, as doc states)
- Universal SWIG triple-string pattern — verified at 0x008E54D0/DC/EC
  (`"TGCharEvent"` / `"_p_TGCharEvent"` / `"TGCharEventPtr"`)
- Relay-audit-20260224 cross-anchor: 0x12 = 5 C→S / 5 S→C / 1:1 — verifies
  doc's "bidirectional, relayed by host" classification

**Four functions CREATED in Ghidra (all were undefined-in-DB, callback-registered):**
- `0x006A1970` MultiplayerGame::SetPhaserLevelHandler — 34-byte body
  (`8B 54 24 04 8B 42 0C 85 C0 74 14 ...`); xref `0x0069F19D` from
  `FUN_0069EFE0` registration (DATA-only)
- `0x00574180` PhaserSystem::SetPhaserLevelHandler — 23-byte body
  (`8B 44 24 04 50 0F BE 50 28 89 91 F0 00 00 00 E8 4C 4F 16 00 C2 04 00`);
  xref `0x00573E21` from `FUN_00573DE0` registration (DATA-only)
- `0x006D6940` TGCharEvent::WriteToStream — 32-byte body, vtable+0x34 slot
- `0x006D6960` TGCharEvent::ReadFromStream — 31-byte body, vtable+0x38 slot

Same pattern as leaves #13/#14/#15: SWIG vtable callbacks and handler-table-
registered functions are systematically undefined because their xrefs are
DATA-only from registration sites; auto-analysis never enters them.

**Four functions RENAMED this session:**
- `0x00574200` → `PhaserSystem__SetPowerLevel`
- `0x006A17C0` → `MultiplayerGame__SendEventMessage`
- `0x00574C20` → `TGCharEvent__Ctor`
- `0x00574C50` → `TGCharEvent__IsA`

**Four plate comments added** with `[v5-validated 2026-05-28]` tags on all
four created functions, documenting the gate logic, vtable slot mapping,
wire-format size, and asymmetry between sender and receiver behavior.

**Three minor non-wire corrections:**

**C1 — Hierarchy cascade (cosmetic, doc-level inheritance display).**
Doc lines 116-121 still depict the FABRICATED `TGSubsystemEvent (0x101)`
intermediate class. Per mid #13 + leaf #14 cascade: there is NO string
`"TGSubsystemEvent"` in the binary (confirmed 0 hits this session). 0x101
is **TGEvent itself**, not a separate subclass. The "factory 0x02 size 0x28"
line is also wrong — TGEvent's factory ID is 0x101 (it's emitted by
`FUN_006D5CE0` at vtable+0x04 of TGEvent). 0x02 is TGObject's class ID
(separate IsA-chain ancestor). Doc's IsA chain at line 142-145 correctly
includes `0x02` because TGCharEvent does inherit through TGObject (the
NiObject→TGObject→TGEvent line). Recommended doc rewrite:

```
NiObject
  └── TGObject (class ID 0x02)
        └── TGEvent (factory 0x101, ~size 0x28)
              ├── TGCharEvent (factory 0x105, size 0x2C)
              └── TGObjPtrEvent (factory 0x10C, size 0x2C)
```

**C2 — Registration string formatting (minor wording).**
Doc line 320 has `"MultiplayerGame::__SetPhaserLevelHandler"` (double-underscore).
The actual binary string at `0x00959F1C` is `"MultiplayerGame :: SetPhaserLevelHandler"`
(colon-space-colon WITH spaces, single colon-colon). The Ghidra symbol name
`s_MultiplayerGame____SetPhaserLeve_00959f1c` shows `____` as the encoded
`" :: "` (Ghidra label-mangling for spaces and colons). Doc line 311's
`"PhaserSystem::SetPhaserLevelHandler"` is **exact** in the binary at `0x008E5440`
(no spaces, double-colon). Recommend doc update lines 311, 319 to use the
exact binary string forms.

**C3 — `FUN_006d6200` naming (minor).**
Doc lines 244, 343 reference `FUN_006d6200` as `ReadObjectFromStream`. The
Ghidra DB has it renamed `TGFactory_DeserializeObject`. Same function (reads
class ID via vtable+0x60, constructs via `TGFactoryCreate`, calls vtable+0x38
ReadFromStream on the new object). Recommend doc match DB name.

**Non-corrections (verified, no change needed):**
- 18-byte wire format byte-by-byte correct
- PP_LOW=0 / PP_MEDIUM=1 / PP_HIGH=2 mapping consistent with 3-way switch
  in `PhaserSystem::SetPowerLevel` (params 0/1/2 each have own JE branch)
- Vtable @ 0x008932DC — all 16 slots correct (verified bytewise)
- "NoMe" group string at 0x008E5528 (`4E 6F 4D 65 00`) — correct
- "Forward" group string at 0x008D94A0 (`46 6F 72 77 61 72 64 00`) — correct
- Sender 8-step flow matches `SetPowerLevel` disassembly exactly
- Receiver flow in `FUN_0069FDA0` matches doc lines 229-251

**Verified asymmetry between sender and receiver:**
- Sender (`PhaserSystem::SetPowerLevel` 0x00574200): creates event, sets
  charValue, posts to event manager (triggers `MultiplayerGame::SetPhaserLevelHandler`
  thunk to send over wire), THEN cascades level to all child weapon
  subsystems via `vtable+0x90`, THEN stores level in `+0xF0`.
- Receiver (`PhaserSystem::SetPhaserLevelHandler` 0x00574180): sign-extends
  `event+0x28` to int, stores into `+0xF0`, releases event. Does **NOT**
  cascade to child weapons.

The remote weapon intensity propagation happens through a separate mechanism
(likely `PhaserSystem::Update` reading `+0xF0` per tick, or StateUpdate
weapon serialization). Doc lines 264-268 correctly flag this asymmetry.

**Cross-anchor: event ID 0x008000E0 has exactly 3 xrefs:**
- `0x00573E81` in `FUN_00573E40` — PhaserSystem handler-table registration
- `0x0069E9C3` in `MultiplayerGame_Ctor` — MP-bridge handler registration
- `0x00574247` in `FUN_00574200` — `PhaserSystem::SetPowerLevel` emit site

All three matches the doc's claimed registration/emission sites exactly.

**Open Q (LOW priority, frequency stat):** Doc claims "~33 per 15-minute
stock session"; relay-audit-20260224 shows 10 events in 21 minutes (5+5)
on a different session. The number varies by playstyle; not a binary fact.

**Function completeness (post-session):**
- `0x00574200` `PhaserSystem__SetPowerLevel`: 1.23 → still undocumented
  (plate comment would lift to ~15)
- `0x006A17C0` `MultiplayerGame__SendEventMessage`: 0.0 → still undocumented
- `0x0069FDA0` generic event-forward: 0.0 → flagged by foundation; doc
  references but does not claim ownership

The doc itself is **clean and accurate** for wire-format / behavior. The
three corrections are surface-level (hierarchy diagram, registration string
typography, helper function naming) — none change the bytes on the wire,
none change the gate logic, none change the relay semantics.

**Header inputs for documentation-writer:**
- validated: 2026-05-28
- methodology: FUNCTION_DOC_WORKFLOW_V5
- binary fingerprint: STBC.exe, image base 0x00400000, size 0x619638 (6.39 MB)
- status: `verified`
- companions: `tgobjptrevent-class.md`, `pythonevent-wire-format.md`,
  `wire-format-spec.md`, `game-opcodes.md`, `tgmessage-routing.md`,
  `event-system-architecture.md`, `weapon-firing-mechanics.md`,
  `v5-validation-status.md`
- supersedes: prior set-phaser-level-protocol.md

### 6.17 delete-player-ui-wire-format.md — 2026-05-28 (game-archaeology-specialist)

**Status:** validated -> `partial` (after 3 corrections + 4 clarifications + 1 MAJOR
architectural finding). **Seventeenth protocol doc** under v5 — third protocol leaf
(after #15 collision-effect-protocol and #16 set-phaser-level-protocol). Does NOT
clear `verified` despite zero wire-format byte changes because the dst_obj_id
semantic correction (network singleton handle vs ship/player ID) is a load-bearing
interpretation change, and the two-registry finding still has open enumeration debt.

**Headline finding: TWO independent class registries in stbc.exe.** This pass
discovered that stbc.exe has not one but two class registries that coexist:

1. **NiRTTI registry** — engine classes via `NiRTTI_*` factory paths; catalog has
   0x02 / 0x101 / 0x105 / 0x10C / 0x8124 / 0x8129. Used by engine's standard RTTI lookup.
2. **TGFactory registry** — table at `DAT_0099a578`, count at `DAT_0099a584`;
   classes registered via `FUN_006B2670` and siblings. Catalog includes 0x801 and the
   0x86x range (0x865 / 0x866 / 0x867 confirmed; full enumeration deferred).
   Used by `TGFactory_DeserializeObject` (0x006D6200) **exclusively**.

The 0x866 class registered at `0x006b27a3` inside `FUN_006B2670` is what opcode 0x17
uses. Previous validation passes that searched only the NiRTTI catalog for 0x866 came
up empty — the class isn't there. This is the binary-truth resolution for
wire-format-spec.md OQ #2 (factory 0x866 catalog gap) and the §4 #13 cross-doc
disagreement. Both are now closed.

**Methodology:** Phase 1-5 per v5 workflow. `program: STBC.exe` on every MCP call.
Doc anchors against engine doc #8 (TGEventManager singleton 0x0097F838 + TGEvent base
vtable 0x00895FF4), protocol doc #4 (game-opcodes opcode 0x17 dispatcher row), protocol
doc #14 (pythonevent-wire-format — same TGFactory_DeserializeObject + factory ID
encoding pattern). The two-registry finding is a NEW cross-anchor that affects every
protocol leaf using factory IDs in the 0x801 / 0x86x range.

**Functions touched:**

| Function | Addr | effective_score | Plate? |
|----------|------|-----------------|--------|
| DeletePlayerUIHandler (receiver) | 0x006A1360 | high | yes (anchored) |
| LAB_0x006a1590 (event-fired wire-send handler) | 0x006A1590 | n/a (LAB_) | n/a — no fn body in DB |
| FUN_006B75B0 (disconnect-side event poster) | 0x006B75B0 | high | anchored |
| FUN_006B2670 (TGFactory registration) | 0x006B2670 | high | yes (registers 0x866 at offset 0x133) |
| Class_0x866_GetTypeID | 0x006B3700 | high | yes |
| Class_0x866_Save (vtable+0x34) | 0x006BB890 | high | yes |
| Class_0x866_Read (vtable+0x38) | 0x006BB8B0 | high | yes |
| Base TGEvent ctor | 0x006D5C00 | high | anchored |
| Base TGEvent Save (vtable+0x34) | 0x006D6128 | high | anchored |
| Base TGEvent Read (vtable+0x38) | 0x006D61B8 | high | anchored |
| TGFactory_DeserializeObject | 0x006D6200 | high | yes |
| FUN_006DA300 (dispatch loop) | 0x006DA300 | high | anchored |
| TGEventManager__PostEvent wrapper | 0x006DA2A0 | high | anchored |
| FUN_0069EFE0 (handler-table registration) | 0x0069EFE0 | high | anchored (binds 28 C++ labels) |

**Wire-format CONFIRMATION (byte-by-byte, no changes):**

| Section | Claim | Verified via |
|---------|-------|--------------|
| Total size | 18 bytes (opcode + 4+4+4+4+1) | Sum of per-field byte widths |
| Class 0x866 layout | 0x2C bytes (base 0x28 + 4-byte extension) | `FUN_006BB840` ctor + vtable 0x00895848 dump |
| Per-byte sender layout | opcode @ 0x006a15d4 → class_id via Save → event+0x10 → event+0x8 → event+0x12 → event+0x28 | Disasm of LAB_0x006a1590 + Class_0x866_Save 0x006BB890 |

**Three corrections:**

**C1 — `FUN_006a0ca0` sends opcode 0x18, NOT 0x17.** Pre-v5 doc attributed
disconnect-side opcode 0x17 sending to `FUN_006a0ca0` ("DeletePlayerHandler").
Disasm of FUN_006a0ca0 at offset 166 shows `C6 44 24 48 18` = `MOV byte ptr
[ESP+0x48], 0x18` — this function sends DeletePlayerAnim, not DeletePlayerUI. The
**actual disconnect-side 0x17 sender is `FUN_006b75b0` inside TGWinsockNetwork** —
it posts a 0x866 event with event_code 0x60005, which the EventManager routes to
`LAB_0x006a1590` which performs the actual wire serialization.

**C2 — 0x866 is a TGEvent SUBCLASS, not base TGEvent.** Pre-v5 doc treated factory
0x866 as if it were base TGEvent itself. Actually:
- Base TGEvent: vtable 0x00895FF4, size 0x28
- Subclass 0x866: vtable 0x00895848, size 0x2C (adds wire_peer_id at +0x28)
- Cluster siblings: 0x865 (vtable 0x0089580C, size 0x2C), 0x867 (vtable 0x00895884, size 0x30)
- 0x866 is registered in the **TGFactory registry** (`DAT_0099a578` / `DAT_0099a584`) via
  `FUN_006B2670` at offset 0x133 — NOT in the NiRTTI catalog. This is exactly why
  prior NiRTTI-catalog searches for 0x866 turned up nothing.

**C3 — `tgt_obj_id` is the TGWinsockNetwork singleton's internal object handle,
not a ship or player ID.** Pre-v5 doc described `tgt_obj_id` as "ship or player
object ID". `FUN_006d62b0` is called with `this = TGWinsockNetwork singleton` and
writes the singleton's internal handle into event+0xC. The stock trace value
`0x0000064F` is a network context value for that session, not a ship ID. Confirmed
via decompile of FUN_006d62b0 + xref check against `FUN_006B75B0` and `FUN_006A1E70`
producer paths.

**Four clarifications:**

**Clar1 — `src_obj_id` is ALWAYS 0 via this path, not "typically 0".** No producer
in the binary writes a non-zero value through the 0x866 send path. Base TGEvent ctor
at 0x006D5C00 inits event+0x8 to 0; no subsequent path writes it before posting.

**Clar2 — `NewPlayerInGameHandler` LAB_-vs-function name collision.** Ghidra's
database shows ONE defined function named `NewPlayerInGameHandler` at 0x006A1E70 (the
opcode 0x2A wire receiver). There is ALSO an event-fired wire-send handler at
`LAB_0x006A1590` (no function body in DB) that registers under the same SWIG name
`"MultiplayerGame :: NewPlayerInGameHandler"` (string at 0x0095A028). Both are
correct — `FUN_0069EFE0` registers both addresses against the same string via
`FUN_006DA130(&LAB_006A1590, s_MultiplayerGame____NewPlayerInGa_0095A028)`. Same
SWIG-callback-vs-function pattern as leaves #13 / #14 / #15 / #16.

**Clar3 — EventManager singleton at 0x0097F838 has registry table at +0x2C =
0x0097F864.** Both addresses are correct; they're different offsets of the same
singleton, not separate globals. Cross-anchor with engine event-system-architecture.md
and protocol leaf #15.

**Clar4 — Two-Registry Architecture is a new dedicated doc section.** The discovery
that NiRTTI and TGFactory are separate registries deserves explicit body documentation
in the leaf so downstream readers don't repeat the missing-branch search. New doc
section: "Two-Registry Architecture" near the top of the doc.

**Sibling SWIG triple-string pattern confirmed:** the 0x866 class uses the standard
SWIG triple-string pattern (class-name / `_p_` pointer-tag / `Ptr` smart-pointer-tag),
same as TGCharEvent / TGObjPtrEvent / ObjectExplodingEvent in leaves #14 / #16. No
new pattern introduced.

**Non-corrections (verified, no change needed):**
- Opcode 0x17 receiver address 0x006A1360 — correct
- 7 instances/session frequency — correct (matches relay-audit-20260224)
- S->C only — correct (0 C->S, 7 S->C across audits)
- Scoreboard population requirements (TGPlayerList + score dict) — correct
- Stock trace #25 packet byte-by-byte decode — correct in structure (only
  `dst_obj_id` semantic label needs the C3 fix)

**Cross-doc anchor reuse:**

- **From doc #1 (wire-format-spec.md):** OQ #2 factory 0x866 catalog gap — **CLOSED**
  by this validation; class lives in TGFactory registry, see §4 #13 closure note.
- **From engine doc #8 (event-system-architecture.md):** TGEventManager singleton at
  0x0097F838 — confirmed; +0x2C registry pointer at 0x0097F864 — confirmed.
- **From doc #4 (game-opcodes.md):** opcode 0x17 dispatcher row + handler address
  0x006A1360 — confirmed. The 0x17 / 0x18 sender-attribution distinction needs
  reflection in game-opcodes.md (batched at family close).
- **From doc #14 (pythonevent-wire-format.md):** `TGFactory_DeserializeObject`
  (0x006D6200) is the shared factory deserialization helper for both opcodes 0x06
  and 0x17 — consistent.
- **From leaf #15 / #16:** SWIG-callback-vs-function-body pattern (handler addresses
  appear only as DATA xrefs from registration sites; Ghidra auto-analysis never
  creates a function entry) — same pattern observed here for LAB_0x006a1590.

**Cross-doc impacts (no in-this-pass modifications; batched):**

- `wire-format-spec.md` OQ #2 — **CLOSED**. The hub doc's NOTE block at line 208
  pointing to v5-validation-status.md §4 #13 can be updated at family close to point
  here as the resolution.
- `game-opcodes.md` — the 0x17 / 0x18 sender attribution may need a one-line
  clarification noting the distinct senders (also a family-close task).
- `objnotfound-requestobj-enterset-wire-format.md` (next leaf, doc #18) — may benefit
  from the TGFactory registry anchor if any 0x801 / 0x86x classes appear in that
  opcode trio.
- All protocol docs that reference factory IDs in the 0x801 / 0x86x range — should
  cross-link to the Two-Registry Architecture section as the canonical source.

**Open questions:**

- Classes 0x865 and 0x867 — payload semantics, dispatch path, any wire usage?
- `event+0x24` — receiver clears it before dispatch; sender doesn't write it. Engine
  read site unknown.
- **TGFactory registry full enumeration** — only 0x801, 0x865, 0x866, 0x867
  confirmed this session. A dedicated sweep of xrefs to `DAT_0099a578` /
  `DAT_0099a584` and `FUN_006B2670` siblings would yield the complete catalog.
- Disconnect-time 0x17 wire observation — path is binary-confirmed (FUN_006B75B0 →
  LAB_0x006a1590 → opcode 0x17); 0 instances observed across available traces.
  Reproducing this requires a multi-client session with one client disconnecting
  AND remaining receivers.

**Verification methods used:**
- `decompile_function` on FUN_006A1360, FUN_006A1E70, FUN_006D5C00, FUN_006D6200,
  FUN_006DA300, FUN_006DA2A0, FUN_006B2670, FUN_0069EFE0, FUN_006D62B0
- `disassemble_bytes` for LAB_0x006a1590 (no fn body in DB), FUN_006A0CA0 prologue
  (to confirm C1 — `MOV [ESP+0x48], 0x18`), Class_0x866_Save 0x006BB890,
  Class_0x866_Read 0x006BB8B0, GetTypeID at 0x006B3700
- `read_memory` for class 0x866 vtable @ 0x00895848 (vs base TGEvent vtable
  0x00895FF4), TGFactory registry table DAT_0099a578
- `get_xrefs_to` on 0x866 class ID immediate, on string s_MultiplayerGame____NewPlayerInGa_0095A028,
  on DAT_0099a578 / DAT_0099a584
- `inspect_memory_content` on stock trace #25 byte-by-byte (1 occurrence in
  self-destruct test; 6 in Valentine's Day 33.5-min trace)

**Files touched:** `docs/protocol/delete-player-ui-wire-format.md` (re-rendered with
v5 frontmatter, Two-Registry Architecture section, NewPlayerInGameHandler Name
Collision subsection, C1 / C2 / C3 corrections, Clar1-4 applied, all section tables
tagged `[v5-validated 2026-05-28]`); `docs/protocol/v5-validation-status.md` (this
row added; §2 row #17 status flipped to partial with summary; §4 #13 marked CLOSED
with anchor to leaf doc; §8 spot-check #6 marked CLOSED).

**Header inputs for documentation-writer:**
- validated: 2026-05-28
- methodology: FUNCTION_DOC_WORKFLOW_V5
- binary fingerprint: STBC.exe, image base 0x00400000, size 0x619638 (6.39 MB)
- status: `partial`
- companions: `wire-format-spec.md`, `game-opcodes.md`, `tgmessage-routing.md`,
  `transport-layer.md`, `tgobjptrevent-class.md`, `event-system-architecture.md`,
  `v5-validation-status.md`
- supersedes: prior 2026-02-21 delete-player-ui-wire-format.md

---

### 6.18 objnotfound-requestobj-enterset-wire-format.md — 2026-05-28 (game-archaeology-specialist)

**Status:** validated -> `partial` (after 3 material wire/value corrections + 2 address-mapping
corrections + 2 clarifications). **Eighteenth protocol doc** under v5 — fourth protocol leaf
(after #15 collision-effect-protocol, #16 set-phaser-level-protocol, #17 delete-player-ui).
Does NOT clear `verified` because three of the corrections (C1 length-prefixed string, C2
"warp" sentinel re-interpretation, C3 FLT_MAX gate) are load-bearing for OpenBC implementation
and the cross-doc §4 #1 conflict required binary arbitration this pass. Zero opcode-routing
errors; the foundation jump-table thunks (0x1D / 0x1E / 0x1F at indices 27 / 28 / 29) all
confirmed byte-by-byte.

**Methodology:** Phase 1-5 per v5 workflow. `program: STBC.exe` on every MCP call. Doc anchors
against engine doc #1 (MultiplayerGame dispatcher 0x0069F2A0 + jump table 0x0069F534),
foundation doc #2 (stream-primitives.md — TGBufferStream cursor vtable at 0x00895C58, slots
+0x10 / +0x14 / +0x68 / +0x6c), foundation doc #3 (transport-layer.md — TGMessage +0x3a
guaranteed flag, +0x3d no-notify), and protocol doc #10 (objcreate-serialization.md —
authoritative on FUN_005a2030 = ShipReadSpecies).

**Functions touched:**

| Function | Addr | effective_score | Plate? |
|----------|------|-----------------|--------|
| MultiplayerGame__ObjNotFoundHandler (0x1D) | 0x006A0490 | high | yes |
| MultiplayerGame__RequestObjHandler (0x1E) | 0x006A02A0 | high | yes |
| MultiplayerGame__EnterSetHandler (0x1F) | 0x006A05E0 | high | yes |
| MultiplayerGame__RequestObjEventHandler (sender for 0x1D / 0x1F) | 0x006A07D0 | high | yes (CREATED this pass — 575B body) |
| MultiplayerGame__EnterSetEventHandler (stub) | 0x006A0A20 | high | yes (CREATED this pass — single RET) |
| GetPlayerSlotFromObjID | 0x006A19A0 | high | anchored |
| MakeObjIDFromPlayerSlot (INVERSE; not called by triad) | 0x006A7770 | high | anchored |
| TGSceneGraph__GetObjectByID (factory 0x8003) | 0x00434E00 | high | anchored |
| PhysicsObjectClass__FindByObjectID (factory 0x8006) | 0x0059FC60 | high | anchored |
| CastToDamageableObject (IsA 0x8007) | 0x00590B20 | high | anchored |
| CastToShipClass (IsA 0x8008) | 0x005AB670 | high | anchored |
| IsLocalPlayerShip (host-mode dual) | 0x005AE140 | high | anchored |
| TGSetManager__FindSetIndexByName (binary search) | 0x004055A0 | high | anchored |
| DamageableObject__SendExplosions_0x29 (replay list at +0x13c) | 0x00595C60 | high | anchored |
| TGBufferStream__ReadString_HeapAlloc (length-prefixed) | 0x006D2370 | high | anchored |
| TGBufferStream__WriteString_LenPrefixed | 0x006D23C0 | high | anchored |
| DamageableObject ctor (+0x14c = FLT_MAX) | 0x00590CB0 | medium | anchored |
| DamageableObject damage application | 0x00592C00 | medium | anchored |

**Wire-format CONFIRMATION (byte-by-byte, no changes to opcode-routing):**

| Section | Claim | Verified via |
|---------|-------|--------------|
| Jump-table thunks | 0x1D index 27 → 0x0069F4F5 → 0x006A0490; 0x1E index 28 → 0x0069F51D → 0x006A02A0; 0x1F index 29 → 0x0069F509 → 0x006A05E0 | Bytes at jump-table+108..119 |
| 0x1D wire | `[0x1D][int32 objectID]` (5 bytes) | ReadInt at 0x006a04ee; relay WriteChar(0x1E)+WriteInt at 0x006a0535/0x006a0540 |
| 0x1E request wire | `[0x1E][int32 objectID]` (5 bytes) | ReadInt at 0x006a02dd cursor |
| 0x1E response payload | `[byte: opcode 0x02 or 0x03][byte: playerSlot][byte: team if 0x03][... WriteToStream via vtable+0x10c ...]` | Disasm 0x006a0392/0x006a039e (opcode select); 0x006a03ab (playerSlot); 0x006a03b9 (team); 0x006a03d4 (WriteToStream) |
| 0x1F wire | `[0x1F][int32 objectID][uint32 LE N][N bytes setName]` — length-prefixed, no trailing NUL | TGBufferStream__ReadString_HeapAlloc body — vtable+0x68 ReadInt then vtable+0x10 ReadBytes |
| Send flags | 0x1D / 0x1E set msg+0x3a = 1 (guaranteed); 0x1E also sets msg+0x3d = 0 (no-notify) | Disasm 0x006a0592 (0x1D); 0x006a041a / 0x006a041e (0x1E) |
| 0x1E response target | nTargetID (the requesting connection), unicast NOT broadcast | Disasm 0x006a0596: SendTGMessage(network, EDI=nTargetID, msg, 0) |
| 0x1F transition slots | currentSet->vtable[+0x58] (ExitSet, slot 22, arg = ship+4); destSet->vtable[+0x54] (EnterSet, slot 21, args = (ship, ship+0x28)) | Decompile of FUN_006A05E0 |

**Three material wire/value corrections:**

**C1 — String encoding is LENGTH-PREFIXED, not null-terminated.** Pre-v5 doc described the
0x1F setName field as "null-terminated string" and described the read as
`TGBufferStream__ReadString(stream, -1)` heap-alloc. Binary truth: the helper at
FUN_006D2370 (`TGBufferStream__ReadString_HeapAlloc`) reads `uint32 length` via vtable+0x68
then `length` raw bytes via vtable+0x10 — **no null terminator on the wire**. Symmetric on
send via FUN_006D23C0 (vtable+0x6c WriteInt + vtable+0x14 WriteBytes). Heap-alloc length
matches wire-prefix exactly. **Severity HIGH** for OpenBC interop. Wire-format row updated
in body (now 2 rows: 4 bytes length + N bytes payload). game-opcodes.md 0x1F row and
wire-format-spec.md should reflect this at family close.

**C2 — `DAT_008d8ab8` is the literal string `"warp"`, not "default space combat set name".**
Pre-v5 doc described `0x008d8ab8` as "the name of the default space combat set — the set
objects inhabit when NOT inside a named sub-region". Binary truth: `inspect_memory_content`
at 0x008d8ab8 returns `77 61 72 70 00` = literal 5-byte `"warp\0"`. The next string in the
rdata block is `"ShipClass"`, NOT `"DeleteAllMissionTimers"` as the pre-v5 doc claimed.
**Semantic re-interpretation:** the sender's `strcmp(currentSetName, "warp")` gate identifies
the in-warp-tunnel set; 0x1F is sent during warp transitions into named destination sub-sets
(e.g., `"Multi1"`), NOT during normal space combat. The pre-v5 "Space Set" subsection is
re-titled and rewritten as "the 'warp' tunnel set". Severity MEDIUM — wire format unchanged
but the gate's meaning is inverted relative to the pre-v5 reading.

**C3 — `DAT_008e5c18` is `FLT_MAX`, not "small positive HP threshold".** Pre-v5 doc described
the constant as `~some small positive float`. Binary truth: bytes at 0x008e5c18 = `ff ff 7f 7f`
= float `3.4028235e+38` = `FLT_MAX`. Used by DamageableObject as **undamaged sentinel**:
ctor (FUN_00590cb0) initializes `dobj+0x14c = FLT_MAX`; damage application (FUN_00592c00)
decrements that field. The 0x1E gate `FLT_MAX <= dobj[+0x14c] AND dobj[+0x150] == 0`
therefore succeeds **only when the object has never been damaged AND is alive** — strictly
stricter than the doc implied. **OpenBC implication:** 0x1E does not re-send damaged objects;
a late-joining client requesting hydration of a damaged object will be silently dropped.
Severity MEDIUM — gate semantics are stricter than a threshold reading suggests; mods that
rely on RequestObj for late-join hydration of damaged objects need their own resync.

**Two address-mapping corrections:**

**C4 — `GetPlayerSlotFromObjID` is at `0x006A19A0`, NOT `0x005A2030`.** Pre-v5 Function
Addresses table row `0x005a2030 | GetPlayerSlotFromObjID` is wrong. `0x005A2030` is
`ShipReadSpecies` (2-vtable-call ship-setup, reads species into ship+0xEC); `0x006A19A0`
is the actual `GetPlayerSlotFromObjID` (formula `(objID - 0x3FFFFFFF + ((objID -
0x3FFFFFFF >> 31) & 0x3FFFF)) >> 18`). The 0x1E handler `CALL 0x006A19A0` at offset
0x006A03AB matches. **CLOSES §4 #1** with binary authority siding with
objcreate-serialization.md (which had the correct `ShipReadSpecies` mapping).

**C5 — `0x006A7770` is `MakeObjIDFromPlayerSlot` (the INVERSE), and is NOT called by the
triad.** Pre-v5 Function Addresses table row `0x006a7770 | MultiplayerGame__GetPlayerSlotFromObjID`
is wrong. Body decompile: `*(int*)(this+0x10) = playerSlot * 0x40000 + 0x3FFFFFFF` — constructs
an obj ID FROM a slot (inverse). Used in player-init context. The 0x1E handler does NOT call
this address; it calls 0x006A19A0 via C4 path. Row relabeled in doc as `MakeObjIDFromPlayerSlot
(INVERSE; not called by the triad)`.

**Two clarifications:**

**Clar1 — Command Messages vs Event Messages.** The 0x1D / 0x1E / 0x1F triad uses raw
`TGBufferStream` primitives only (ReadInt / ReadString_HeapAlloc / WriteChar / WriteInt) and
bypasses `TGFactory_DeserializeObject` (FUN_006D6200) entirely. Contrasts with opcodes 0x06
(PythonEvent) / 0x12 (SetPhaserLevel) / 0x15 (CollisionEffect) / 0x17 (DeletePlayerUI) which
all go through TGFactory. New doc section: "Command Messages vs Event Messages — Why the
Triad Bypasses TGFactory" with a per-opcode style table. The triad are RPC-style requests
and responses, not event-bearing transports — simpler to reimplement in OpenBC (no class-ID
lookup, no TGFactory registry).

**Clar2 — `IsLocalPlayerShip` is host-mode-aware.** Pre-v5 pseudocode read
`if (ship != NULL && Ship__IsPlayerShip(ship)) opcode = 3;`. Binary truth: `IsLocalPlayerShip`
(FUN_005AE140) branches on `DAT_0097FA89` (IsHost): on host it returns true for ANY ship with
`ship+0x2e4 != 0` (i.e., team-bearing); on client it returns true only for the local player's
ship. **OpenBC implication for dedicated servers:** opcode 0x03 is selected for every
team-bearing ship, not one "local" ship. The body pseudocode is structurally correct;
the doc adds an explicit note.

**Refinements (R1 / R2, not promoted to body corrections):**

- R1 — Cast helper naming: pre-v5 doc body line wrote `DamageableObject__Cast`; the actual
  Ghidra-renamed helper is `CastToDamageableObject` (FUN_00590B20, IsA 0x8007). Cosmetic.
- R2 — `"UNKNOWN"` allocator class name string at 0x008d858c is the LITERAL class name used
  by the generic TGMessage pool — NOT a placeholder for "we don't know the class". Used by
  0x1D / 0x1E / 0x1F / 0x29 / NewPlayerInGameHandler. Worth a one-line note in the doc
  (added to data anchors table).

**Non-corrections (verified, no change needed):**
- Opcode 0x1D / 0x1E / 0x1F receiver addresses (0x006A0490 / 0x006A02A0 / 0x006A05E0) — correct.
- Jump-table thunks (0x0069F4F5 / 0x0069F51D / 0x0069F509) — correct.
- 0x1D relay-to-host(0) on local-miss — correct.
- 0x1E unicast back to requestor (not broadcast) — correct.
- 0x1F NULL-found fallback relays 0x1E to host(0) — correct.
- 0x1F sender uses "NoMe" group — correct (NOT host(0); pre-v5 doc was already right here).
- ExitSet (vtable+0x58, slot 22) / EnterSet (vtable+0x54, slot 21) — correct.
- ExitSet args = (objID); EnterSet args = (ship, placement at ship+0x28) — correct.
- WriteToStream via vtable[+0x10c] (slot 67) — correct.
- DamageableObject__SendExplosions_0x29 walks list at dobj+0x13c — correct.
- Empty stub at 0x006A0A20 (single RET, body 3 bytes) — correct.
- Triad bypasses TGFactory — verified via full-body read of all three handlers.

**Cross-doc anchor reuse:**

- **From doc #1 (wire-format-spec.md):** opcode 0x1D / 0x1E / 0x1F handler addresses + jump-table
  routing — confirmed. The 0x1F string-encoding row needs the C1 length-prefix correction at
  family close.
- **From foundation doc #2 (stream-primitives.md):** TGBufferStream cursor vtable @ 0x00895C58
  with slots +0x10 / +0x14 / +0x68 / +0x6c — confirmed; this leaf is independent confirmation.
- **From foundation doc #3 (transport-layer.md):** TGMessage +0x3a guaranteed flag, +0x3d
  no-notify flag — confirmed via 0x1D / 0x1E send paths.
- **From doc #4 (game-opcodes.md):** opcode 0x1F wire-format row needs the C1 length-prefix
  fix at family close.
- **From doc #10 (objcreate-serialization.md):** `FUN_005A2030 = ShipReadSpecies` — confirmed,
  binary authority sides with this doc (closes §4 #1). `WriteToStream` chain via
  vtable[+0x10c] for ObjCreate is also the chain used for 0x1E response — consistent.
- **From engine doc #1 (function-map.md):** TGNetwork singleton at DAT_0097FA78 — confirmed.

**Cross-doc impacts (no in-this-pass modifications; batched at family close):**

- `wire-format-spec.md` — 0x1F row should reflect length-prefix wire (C1).
- `game-opcodes.md` — 0x1F row should reflect length-prefix wire (C1); 0x1E row should
  note the FLT_MAX gate (C3) and the "command-message-bypasses-TGFactory" distinction (Clar1).
- `objcreate-serialization.md` — already correct on FUN_005A2030; no body change needed.
  The 0x1E response uses the same WriteToStream chain; a cross-link from objcreate to this
  leaf for the recovery-path companion would help readers.
- `docs/engine/rtti-class-catalog.md` — confirm IsA tags 0x8003 / 0x8006 / 0x8007 / 0x8008
  map to TGSceneGraph-anchored object / PhysicsObjectClass / DamageableObject / ShipClass.
  (open question)
- `docs/protocol/README.md` — doc already indexed (line 35 of README). §4 #14 still open
  for the family-close README refresh.

**Open questions:**

- SWIG registration string for FUN_006A0A20 — the doc labels it "Enter game set" but the
  actual string passed in FUN_0069efe0 (single DATA xref at 0x0069eff9) is not byte-for-byte
  verified. Decompile FUN_0069efe0 and read the string argument.
- IsA tag catalog mapping for 0x8003 / 0x8006 / 0x8007 / 0x8008 against
  `docs/engine/rtti-class-catalog.md` — currently inferred from cast-helper naming.
- 0x1F receiver uses `TGBufferStream__ReadString_HeapAlloc(stream, -1)` while sender uses
  direct vtable+0x6c / vtable+0x14 — both encodings are symmetric (length-prefixed), but the
  call-shape asymmetry is unexplained.

**Verification methods used:**
- `decompile_function` on FUN_006A0490, FUN_006A02A0, FUN_006A05E0, FUN_006A07D0, FUN_006A0A20,
  FUN_006A19A0, FUN_006A7770, FUN_005A2030, FUN_005AE140, FUN_00590CB0, FUN_00592C00,
  FUN_00595C60, FUN_006D2370, FUN_006D23C0, FUN_004055A0, FUN_00434E00, FUN_0059FC60,
  FUN_00590B20, FUN_005AB670
- `disassemble_bytes` for jump-table 0x0069F534 (offsets 108..119), and for the 0x006A0490 /
  0x006A02A0 / 0x006A05E0 prologue + key call sites (0x006a04ee / 0x006a0535 / 0x006a0540 /
  0x006a0551 / 0x006a058b / 0x006a0592 / 0x006a02dd / 0x006a032f / 0x006a034c / 0x006a036b /
  0x006a0392 / 0x006a039e / 0x006a03ab / 0x006a03b9 / 0x006a03d4 / 0x006a041a / 0x006a041e /
  0x006a042f / 0x006a0596)
- `inspect_memory_content` for 0x008d8ab8 ("warp\0"), 0x008e5c18 (FLT_MAX bytes),
  0x008d858c ("UNKNOWN"), 0x008e5528 ("NoMe")
- `read_memory` for TGBufferStream cursor vtable @ 0x00895C58 slot validation
- `get_xrefs_to` on FUN_006A0A20 (single DATA xref from FUN_0069efe0 at 0x0069eff9 confirms
  SWIG registration site); on DAT_008d8ab8 (sender FUN_006A07D0 strcmp gate confirmed);
  on DAT_008e5c18 (DamageableObject ctor + damage application + 0x1E gate)

**Files touched:** `docs/protocol/objnotfound-requestobj-enterset-wire-format.md`
(re-rendered with breadcrumb header, v5 frontmatter, NOTE block with 5 corrections + 2
clarifications, new "Command Messages vs Event Messages" subsection, C1 length-prefix
section under 0x1F wire format, C2 "warp" tunnel re-interpretation rewriting the prior
"Space Set" subsection, C3 FLT_MAX gate subsection under 0x1E handler, C4 / C5
"Critical Correction: Function Address Map" section, corrected Function Addresses table,
new Data anchors table, new TGFactory class IDs table, Open Questions, refreshed Related
Documents); `docs/protocol/v5-validation-status.md` (§2 row #18 status flipped from
`pending` to `partial` with summary; §4 #1 marked CLOSED with anchor to leaf doc §C4;
§4 #15 marked CLOSED (breadcrumb added); §8 spot-check #1 marked CLOSED with binary
truth; §8 spot-check #8 marked CLOSED with FLT_MAX value; this §6.18 entry added).

**Header inputs for documentation-writer:**
- validated: 2026-05-28
- methodology: FUNCTION_DOC_WORKFLOW_V5
- binary fingerprint: stbc.exe, image base 0x00400000, size 6182400 bytes
- status: `partial`
- companions: `wire-format-spec.md`, `game-opcodes.md`, `transport-layer.md`,
  `stream-primitives.md`, `objcreate-serialization.md`, `object-replication.md`,
  `cf16-explosion-encoding.md`, `delete-player-ui-wire-format.md`, `v5-validation-status.md`,
  `docs/engine/rtti-class-catalog.md`
- supersedes: prior 2026-02-21 objnotfound-requestobj-enterset-wire-format.md

### 6.19 subsystem-integrity-hash.md — 2026-05-28 (game-archaeology-specialist)

**Status:** validated -> `partial` (after 1 material correction + 4 clarifications). **Nineteenth
protocol doc** under v5 — fifth protocol leaf (after #15 collision-effect-protocol,
#16 set-phaser-level-protocol, #17 delete-player-ui, #18 objnotfound-requestobj-enterset).
Does NOT clear `verified` because C1 is a load-bearing cascade from foundation #1 (six
slot-identity labels in the canonical 12-row hash table required rewriting) and the body's
line 129 negative claim ("Repair does not appear in the hash") was wrong on TWO counts —
RepairSubsystem IS hashed at slot 7 (ship+0x2D8). The hash function reads CORRECT offsets;
only the human-readable identity column was stale. All other claims (functions, sender/receiver
gates, wire encoding, kick path, 6 boolean sentinel magic constants, container aliasing
pattern) are byte-by-byte confirmed.

**Methodology:** Phase 1-5 per v5 workflow. `program: STBC.exe` on every MCP call. Doc anchors
against foundation doc #1 (wire-format-spec.md C1 — corrected ship-slot Named Slot Layout,
v5-validated 2026-05-28), mid #8 (stateupdate.md — sender `bVar19 = !isMultiplayer` gate identity),
mid #11 (stateupdate-subsystem-wire-format.md — ship+0x2C0..+0x2DC linked-list order), and
the engine cross-anchors for IsMultiplayer (0x0097FA8A) + TGEventManager singleton (0x0097F838).

**Functions touched:**

| Function | Addr | effective_score | Plate? |
|----------|------|-----------------|--------|
| ComputeSubsystemIntegrityHash | 0x005B5EB0 | 38.3 | yes |
| HashBaseSubsystem | 0x005B6170 | 25.4 | yes |
| HashWeaponSystem | 0x005B6330 | 25.7 | yes |
| HashIndividualWeapon | 0x005B6560 | medium | no (OQ-2 — per-type dispatch not byte-checked) |
| HashFoldFloat | 0x005B6C10 | 40.9 | yes |
| Ship__WriteStateUpdate (sender) | 0x005B17F0 | high | anchored |
| Ship__ReadStateUpdate (receiver) | 0x005B21C0 | high | anchored |
| ShipSubsystemContainer_Ctor | 0x005B5D00 | high | anchored (vtable 0x008944c8) |
| MultiplayerWindow_BootPlayerHandler | 0x00506170 | 33.0 | yes (CREATED this pass — 0x44-byte msg, reason=4 at 0x005061CD) |

**Wire-format / mechanism CONFIRMATION (byte-by-byte, no changes to hash algorithm):**

| Section | Claim | Verified via |
|---------|-------|--------------|
| Sender gate | bVar19 = !isMultiplayer set at 0x005B1906; tested at 0x005B1D96; has_hash=1 + WriteShort only on SP branch; has_hash=0 on MP branch | Disasm 0x005B1D96..0x005B1DC5 |
| Wire encoding | `(hash >> 16) ^ (hash & 0xFFFF)` 16-bit XOR fold | Disasm 0x005B1DB6 (SAR EDX,0x10), 0x005B1DB9 (XOR EAX,EDX), 0x005B1DBC (CALL WriteShort 0x006CF7F0) |
| Receiver gate | isMultiplayer == 1 -> ComputeSubsystemIntegrityHash + compare; on mismatch post ET_BOOT_PLAYER | Decompile gate `if ((DAT_0097fa8a != '\\0') && (uComputedHash = FUN_005b5eb0(), ...))` |
| Event allocation | TGAlloc 0x2C bytes (FUN_00717b70) -> FUN_00718010 -> FUN_006BB840 (TGEvent ctor) -> FUN_006D62B0 (SetSrcDest) -> FUN_006DA2A0 (PostEvent) | Disasm 0x005B22FF..0x005B232C |
| Event type write | MOV [EDI+0x10], 0x008000F6 — immediate 32-bit constant (NOT a pointer dereference) | Disasm 0x005B2311 |
| Kick path | ET_BOOT_PLAYER (0x008000F6) -> MultiplayerWindow_BootPlayerHandler (0x00506170) -> TGBootPlayerMessage reason=4 | Disasm 0x005061A0 (PUSH 0x44), 0x005061CD (MOV [ESI+0x40], 0x4); cross-confirmed via 04_ui_windows.c line 2027 |
| 6 sentinel magic constants | All hex bit-patterns byte-exact: 0x42800083 / 0x42993333 / 0x42C53333 / 0x42C80000 / 0x4164CCCD / 0x43E40CCD / 0x41DA6666 / 0x4180CCCD / 0x3ECCCCCD / 0x42C63333 / 0x42026666 / 0x43F38CCD | Decompile of HashBaseSubsystem + HashWeaponSystem |
| Container aliasing | ship+0x27C sub-object ctor zero-fills param_1[1..0x18] = ship+0x280..+0x2DC; offsets +0x34..+0x60 alias ship+0x2B0..+0x2DC | Decompile of FUN_005B5D00 |

**One material correction:**

**C1 — Slot subsystem-identity column (6 of 12 rows mislabeled).** The pre-v5 doc's 12-row
slot table had six stale labels that pre-dated foundation #1's 2026-05-28 ship-slot table
correction. The hash function reads the **correct container offsets** (and those offsets
alias the **correct ship offsets** via the container ctor's zero-fill range), but the
human-readable subsystem name column carried legacy names. Corrections:

- Slot 1 (+0x48 / ship+0x2C4): was "Power Reactor" -> is **HullSubsystem** (0x8138)
- Slot 3 (+0x34 / ship+0x2B0): was "Powered Master" -> is **PowerSubsystem (reactor/EPS)** (0x813E) [rename only — same physical subsystem, legacy name]
- Slot 4 (+0x4C / ship+0x2C8): was "Cloak Device" -> is **SensorSubsystem** (0x8139)
- Slot 6 (+0x54 / ship+0x2D0): was "Sensor Array" -> is **WarpEngineSubsystem** (0x813B)
- Slot 7 (+0x5C / ship+0x2D8): was "Warp Drive" -> is **RepairSubsystem** (0x813F)
- Slot 8 (+0x60 / ship+0x2DC): was "Crew / Unknown-A" -> is **CloakDevice** (0x813A)

**Critical downstream fix — line 129 negative claim was wrong on TWO counts.** Pre-v5 body
read "The Repair subsystem (ship+0x2C0 in the main container table) does NOT appear in the
hash." Binary truth: (a) ShieldGenerator is at ship+0x2C0 (not Repair, never was) and
(b) RepairSubsystem IS at ship+0x2D8 (slot 7) and **does** appear in the hash via
`HashBaseSubsystem` + 1-float `prop+0x4C` extra. Corrected statement now reads: "All 12 named
subsystem slots (Power, Shield, Hull, Sensor, Impulse, Warp, Repair, Cloak, Torpedo, Phaser,
Pulse, Tractor) DO appear in the hash via the container alias at ship+0x27C."

**Severity:** the C1 cascade does NOT change wire format or hash algorithm — only labels.
But the line 129 negative claim is load-bearing for OpenBC implementation (a clean-room
implementer reading the pre-v5 doc would have skipped RepairSubsystem from their hash —
producing mismatches on any session that triggered the SP code path). Severity MEDIUM-HIGH
for OpenBC correctness; HIGH for documentation accuracy.

**Four clarifications:**

**Clar-1 — Receiver event-type write is at event+0x10 as a 32-bit immediate.** Pre-v5
pseudocode wrote `event->eventType = 0x8000F6;` without specifying byte offset. Binary truth:
`MOV dword ptr [EDI + 0x10], 0x008000F6` at 0x005B2311. Pseudocode updated to show the offset
explicitly.

**Clar-2 — Torpedo int product fold cast precision.** Pre-v5 pseudocode:
`HashFoldFloat((float)(torpType->field_0x08 * torpType->field_0x00), &hash);` (int multiply
then float cast). Binary truth: `(float)local_4[2] * (float)*local_4` — each int is cast to
float SEPARATELY then multiplied as floats. For small int values typical of torpedo metadata
the result is the same, but on overflow the float-multiply path differs in precision. Pseudocode
updated to binary-faithful form.

**Clar-3 — `&ET_BOOT_PLAYER` and `0x008000F6` are the same address constant.** Ghidra decompile
shows `*(undefined **)(iHashBit + 0x10) = &ET_BOOT_PLAYER;` (symbolic-pointer write). Actual
instruction is `MOV dword ptr [EDI + 0x10], 0x008000F6` (immediate constant). Both are
bytewise identical because **the address of the ET_BOOT_PLAYER symbol IS the event-type ID** —
the address itself is the unique event-type key, not a pointer to a value at that address.
Doc pseudocode using `0x008000F6` directly is more accurate to the bytes.

**Clar-4 — Sender uses signed SAR; wire-identical to unsigned shift.** Binary uses
`SAR EDX, 0x10` (signed shift right). The doc's `(hash >> 16)` reading as unsigned is
wire-identical because `WriteShort` truncates to the low 16 bits, and the XOR result's low
16 bits are unaffected by sign extension into the high 16. Pedantic note for re-implementers
using a signed `int32` hash type.

**Cross-doc anchor reuse:**

- **From foundation doc #1 (wire-format-spec.md C1):** corrected Named Slot Layout at
  ship+0x2B0..+0x2DC — cascade is the source of leaf C1.
- **From mid #8 (stateupdate.md):** `bVar19 = !isMultiplayer` gate identity — confirmed
  consistent.
- **From mid #11 (stateupdate-subsystem-wire-format.md):** subsystem linked-list order — no
  conflict with the hash table here (different mechanism; same ship-offset table is shared).
- **From leaf #18 (objnotfound-requestobj-enterset-wire-format.md):** command-message
  bypasses-TGFactory pattern — the receiver's `PostEvent` chain here follows the same shape
  (raw TGEvent allocation, not TGFactory_DeserializeObject). Cross-linked in body.
- **From engine doc #1 (CLAUDE.md Key Globals):** IsMultiplayer (0x0097FA8A), TGEventManager
  singleton (0x0097F838), MultiplayerWindow singleton (0x009878CC) — all confirmed.

**Cross-doc impacts (no in-this-pass modifications; batched at family close):**

- `wire-format-spec.md` — closes §4 #4 and §4 #5 (both already half-closed by foundation
  pass — this leaf provides the canonical 12-row hash table that the hub now links to instead
  of duplicating).
- `stateupdate.md` — already cites bVar19 identity; no change.
- `stateupdate-subsystem-wire-format.md` — no change (subsystem-list mechanism is separate
  from the integrity hash).
- `per-ship-subsystem-wire-format.md` — uses the same corrected slot identities (foundation
  cross-anchor already applied).
- `objnotfound-requestobj-enterset-wire-format.md` (leaf #18) — sibling cross-link added in
  body (command-message bypasses-TGFactory pattern shared).

**Open questions:**

- **OQ-1** — `FUN_0055e220` is called at slot 8 (ship+0x2DC = CloakDevice). What state does
  this side-effect getter read? Hypothesis: cloak `Refresh` / `UpdateState`. Decompile pending.
- **OQ-2** — `HashIndividualWeapon` 5-way type dispatch (0x802B / 0x802C / 0x802D / 0x802E /
  0x802F) per-type property-offset reads not byte-checked this pass. Function renamed but
  no plate yet.
- **OQ-3** — `FUN_00560fc0` (Impulse 4-float extra helper at slot 5) decompile to confirm
  Impulse / Warp engine-pair asymmetry (Warp at slot 6 has no helper).
- **OQ-4** — `reference/decompiled/05_game_mission.c` line numbers (~56151, ~56253, etc.)
  not re-verified against the 2026-05-28 import. Update or drop the line-number table.

**Verification methods used:**

- `decompile_function` on FUN_005B5EB0, FUN_005B6170, FUN_005B6330, FUN_005B6560, FUN_005B6C10,
  FUN_005B5D00, FUN_005B17F0, FUN_005B21C0
- `disassemble_bytes` for 0x005B1D96..0x005B1DC5 (sender gate + SAR/XOR/WriteShort) and
  0x005B22FF..0x005B232C (receiver kick path) and 0x005061A0..0x005061CD (boot-player handler
  size + reason)
- `create_function` at 0x00506170 (was undefined in Ghidra DB)
- `read_memory` for ET_BOOT_PLAYER (0x008000F6) confirmation as address constant
- `get_xrefs_to` on FUN_005B5EB0 (single xref from sender + receiver gate sites confirmed)

**Files touched:** `docs/protocol/subsystem-integrity-hash.md` (re-rendered with breadcrumb
header preserved, v5 frontmatter added, NOTE block with 1 correction + 4 clarifications,
dedicated C1 section with corrected slot table + line 129 fix, Clar-2 inline at torpedo
int-product fold, Clar-1 + Clar-3 in receiver section, Clar-4 in sender section, new container
aliasing pattern subsection, new kick path section, refreshed Function Addresses table with
Data anchors sub-table, Open Questions, Related Documents); `docs/protocol/v5-validation-status.md`
(§2 row #19 status flipped from `pending` to `partial`; §4 #4 marked CLOSED with binary truth;
§4 #5 marked CLOSED (canonical authority confirmed); this §6.19 entry added).

**Header inputs for documentation-writer:**

- validated: 2026-05-28
- methodology: FUNCTION_DOC_WORKFLOW_V5
- binary fingerprint: stbc.exe, image base 0x00400000, size 6182400 bytes
- status: `partial`
- companions: `wire-format-spec.md`, `stateupdate.md`, `stateupdate-subsystem-wire-format.md`,
  `per-ship-subsystem-wire-format.md`, `objnotfound-requestobj-enterset-wire-format.md`,
  `v5-validation-status.md`, `docs/engine/rtti-class-catalog.md`
- supersedes: prior 2026-02-15 subsystem-integrity-hash.md

### 6.20 cf16-precision-analysis.md — 2026-05-28 (documentation-writer batch with leaf #21)

**Status:** validated -> `verified` (after 1 refinement + 1 clarification). **Twentieth
protocol doc** under v5 — sixth protocol leaf (after #15 collision-effect-protocol, #16
set-phaser-level-protocol, #17 delete-player-ui, #18 objnotfound-requestobj-enterset, #19
subsystem-integrity-hash). **Third protocol-family doc to clear `verified`** (after #15
and #16). Rendered as a single batch with leaf #21 because both docs share the same Ghidra
anchors (5 .rdata constants, encoder + decoder addresses, explosion sender/receiver, and
the ExplosionDamage struct ctor).

**Methodology:** Phase 1-5 per v5 workflow. Combined evidence packet supplied by
game-archaeology-specialist (`.claude/agent-memory/game-archaeology-specialist/cf16-batch-validation-20260528.md`).
Doc anchors against stream-primitives (foundation #2 — CF16 encoder/decoder addresses) and
game-opcodes (mid #4 — opcode 0x29 wire frame row). No new Ghidra renames or plates this pass
(plates on `CompressedFloat16_Encode` + `CompressedFloat16_Decode` already exist from prior
stream-primitives validation; the CF16 leaves are the durable artifact for the deep dive).

**Functions touched (shared with leaf #21):**

| Function | Addr | effective_score | Plate? |
|----------|------|-----------------|--------|
| CompressedFloat16_Encode | 0x006D3A90 | 52.6 | yes (prior pass) |
| CompressedFloat16_Decode | 0x006D3B30 | 49.1 | yes (prior pass) |
| DamageableObject__SendExplosions_0x29 | 0x00595C60 | 0 (load-bearing) | needs plate (deferred) |
| Handler_Explosion_0x29 | 0x006A0080 | 0 (load-bearing) | needs plate + rename (deferred) |
| ExplosionDamage_Ctor | 0x004BBDE0 | n/a | anchored (struct layout matches doc) |

**Wire-format / algorithm CONFIRMATION (byte-by-byte, no changes):**

| Section | Claim | Verified via |
|---------|-------|--------------|
| Constants | 5 .rdata constants byte-exact: BASE=6F 12 83 3A / ZERO=00 00 00 00 / MULT=00 00 20 41 / ENC_SCALE=00 F0 7F 45 / DEC_SCALE=01 08 80 39 | Direct DAT_… read |
| Encoder | [sign:1][scale:3][mantissa:12] bit layout + __ftol truncation + scale-8 overflow clamp | Decompile FUN_006D3A90 |
| Decoder | iterative range rebuild + float32(1/4095) multiply | Decompile FUN_006D3B30 |
| Opcode 0x29 wire frame | 1 (opcode) + 4 (objID) + 5 (CV4 pos) + 2 (CF16 radius) + 2 (CF16 damage) = 14 bytes; radius first (xref 0x00595d90), damage second (xref 0x00595da1) | Decompile FUN_00595C60 + FUN_006A0080 + ctor body |
| ExplosionDamage struct | 0x38 bytes: vtable +0, position +0x08, radius +0x14, radius^2 +0x18, damage +0x1C, bbox min +0x20, bbox max +0x2C | Decompile FUN_004BBDE0; vtable 0x0088c6c4 hardcoded; allocator FUN_00718cb0(0x38) matches |
| Mod round-trip via int() | 15.0/25.0/273.0/2063.0 all FAIL `int(decoded)==original` test | Arithmetic verification via encoder + decoder pseudocode |

**One refinement:**

**R1 — Encoder xref count is 5, not 4.** The pre-v5 doc closed with "All callers confirmed
via xref analysis of FUN_006d3a90 (4 call sites total)" but the narrative listed only 4
callers in a bullet list. Binary truth: there are **5 xrefs** to FUN_006d3a90:

| # | From | Function | Field |
|---|------|----------|-------|
| 1 | 0x00595d90 | DamageableObject__SendExplosions_0x29 | radius |
| 2 | 0x00595da1 | DamageableObject__SendExplosions_0x29 | damage |
| 3 | 0x005b1e38 | Ship__WriteStateUpdate | speed (flag 0x10) |
| 4 | 0x006d2b8c | CompressedVector3_Write | magnitude |
| 5 | 0x005a2b3b | (Ghidra-undefined function) | speed-like (flag 0x10 gate via TEST BL,0x10) |

The 5th site lives in an undefined function (~0x005a2800-0x005a3000), gated by the same
flag-0x10 speed bit as Ship StateUpdate. Likely a non-Ship state-writer (torpedo/projectile
hypothesis based on FMUL multiplier at 0x0088d4e4 preceding the encode call). Promoted to
OQ1 below; tracked in §4 #19. Decoder symmetry: 5 xrefs to FUN_006d3b30 as well, paired with
each encoder site.

The pre-v5 narrative is replaced with an enumerated 5-row table that names each caller, gives
the call-site address, and tags the 5th site `[open question — OQ1: function identity]`.

**One clarification:**

**Clar1 — `int()` vs `round()` match strategy cross-link to leaf #21.** The pre-v5 doc's
"Mod Damage Value Round-Trip Analysis" table has an `int() Match` column where all four BC
Remastered values FAIL. Companion leaf #21 has a `round() Matches` column where 3 of the 4
succeed (only 2063 fails). These tables are NOT contradictory — they answer different
questions:

- `int(24.989) = 24` (truncate-toward-zero) → FAIL
- `round(24.989) = 25` (banker's / away-from-zero) → YES

A one-sentence note next to the table directs readers to leaf #21 for the `round()` view.
Both columns are correct and useful — pick the strategy that matches your mod's comparison
code. (Cross-doc disagreement §4 #8 closed via this cross-link convention rather than a
merge — see §4 #8 closure.)

**Severity:** the R1 count refinement does NOT change algorithm or wire format — only the
narrative cap; the Clar1 cross-link adds reader clarity. Doc clears `verified` because all
load-bearing claims (algorithm, constants, struct layout, wire format) are byte-by-byte
confirmed and the two changes are non-load-bearing.

**Cross-doc anchor reuse:**

- **From stream-primitives (foundation #2):** CF16 encoder / decoder addresses and the 5
  .rdata constants — confirmed.
- **From game-opcodes (mid #4):** opcode 0x29 receiver = 0x006A0080 — confirmed (matches
  this doc and leaf #21).
- **From sibling leaf #21:** `round()` match column (cross-link added in body).

**Cross-doc impacts (no in-this-pass modifications; batched at family close):**

- `stream-primitives.md` (foundation #2) — note the CV4 byte-size dispatch on `param_5`
  (`mag_as_cf16` flag): 5-byte form for CF16 magnitude, 7-byte form for raw float magnitude.
  Both leaves #20 and #21 now cite this dispatch.
- `game-opcodes.md` (mid #4) — opcode 0x29 row should cross-link both CF16 leaves.
- `stateupdate.md` (mid #8) — flag 0x10 speed cites the encoder anchored in this leaf.

**Open questions:**

- **OQ1** — The Ghidra-undefined function at ~0x005a2800-0x005a3000 containing the 5th
  encoder caller (site 0x005a2b3b). Field + gate + call-site documented; only the parent
  function identity is open. Promoted to §4 #19. Non-blocking for this doc.

**Verification methods used:**

- Shared evidence packet from game-archaeology-specialist (single Ghidra session covering
  both #20 and #21 against the 2026-05-28 import).
- `decompile_function` on FUN_006D3A90, FUN_006D3B30, FUN_00595C60, FUN_006A0080, FUN_004BBDE0
  (all confirmed via packet; not re-run by documentation-writer).
- 5 .rdata constants byte-confirmed via direct read.
- 5 xrefs to FUN_006d3a90 enumerated via `get_xrefs_to`.

**Files touched:** `docs/protocol/cf16-precision-analysis.md` (re-rendered with breadcrumb
header preserved, v5 frontmatter added with 12 evidence rows, NOTE block with 1 refinement
+ 1 clarification, enumerated 5-row caller table replacing the prior 4-row narrative bullet,
Clar1 cross-link inserted next to the Mod Damage Value Round-Trip Analysis table, OQ1 section
added, Related Documents section refreshed);
`docs/protocol/v5-validation-status.md` (§2 row #20 status flipped from `pending` to
`verified`; §4 #8 marked CLOSED with cross-link convention; §4 #19 added for OQ1; this §6.20
entry added).

**Header inputs for documentation-writer:**

- validated: 2026-05-28
- methodology: FUNCTION_DOC_WORKFLOW_V5
- binary fingerprint: stbc.exe, image base 0x00400000, size 6182400 bytes
- status: `verified`
- companions: `cf16-explosion-encoding.md`, `stream-primitives.md`, `game-opcodes.md`,
  `stateupdate.md`, `wire-format-spec.md`, `v5-validation-status.md`
- supersedes: prior 2026-02-15 cf16-precision-analysis.md

### 6.21 cf16-explosion-encoding.md — 2026-05-28 (documentation-writer batch with leaf #20)

**Status:** validated -> `verified` (after 1 byte-size correction + 1 clarification).
**Twenty-first protocol doc** under v5 — seventh protocol leaf. **Fourth protocol-family
doc to clear `verified`** (after #15, #16, #20). Rendered as a single batch with leaf #20
because both docs share the same Ghidra anchors. Sibling leaf #20 carries the algorithm-deep
view; this doc carries the explosion-specific wire format + mod weapon-type ID round-trip.

**Methodology:** Phase 1-5 per v5 workflow. Combined evidence packet supplied by
game-archaeology-specialist (`.claude/agent-memory/game-archaeology-specialist/cf16-batch-validation-20260528.md`).
Doc anchors against stream-primitives (foundation #2 — CF16 + CV4 dispatch), game-opcodes
(mid #4 — opcode 0x29 row), and sibling leaf #20.

**Functions touched (shared with leaf #20 plus 2 CV4 dispatchers and 2 replay-path callers):**

| Function | Addr | effective_score | Plate? |
|----------|------|-----------------|--------|
| CompressedFloat16_Encode | 0x006D3A90 | 52.6 | yes (prior pass) |
| CompressedFloat16_Decode | 0x006D3B30 | 49.1 | yes (prior pass) |
| CompressedVector4_WriteVirtual | 0x006D2F10 | high | anchored (dispatch on param_5) |
| CompressedVector4_ReadVirtual | 0x006D2FD0 | high | anchored (symmetric) |
| DamageableObject__SendExplosions_0x29 | 0x00595C60 | 0 (load-bearing) | needs plate (deferred) |
| Handler_Explosion_0x29 | 0x006A0080 | 0 (load-bearing) | needs plate + rename (deferred) |
| MultiplayerGame__RequestObjHandler | 0x006A02A0 | high | replay-path caller |
| Handler_NewPlayerInGame_0x2A | 0x006A1E70 | high | replay-path caller |
| ExplosionDamage_Ctor | 0x004BBDE0 | n/a | anchored |

**Wire-format / algorithm CONFIRMATION (byte-by-byte, no changes to algorithm or constants):**

| Section | Claim | Verified via |
|---------|-------|--------------|
| Constants | Same 5 .rdata constants as leaf #20 — byte-exact | Direct DAT_… read |
| Encoder / Decoder | Same algorithms as leaf #20 | Decompile FUN_006D3A90 / FUN_006D3B30 |
| Encoded hex values | 15.0→0x50E3, 25.0→0x52AA, 273.0→0x6313, 2063.0→0x71E3 (all unique) | Arithmetic + encoder pseudocode |
| round() match | 15/25/273 = YES, 2063 = NO (decodes to 2061.54 → rounds to 2062 not 2063) | Arithmetic on decoder pseudocode + Scale-7 step 2.198 |
| Scale-7 mantissa collision | Mantissa 483 = both 2062 and 2063 | Arithmetic |
| Sender + 2 replay-path callers | FUN_00595C60 called from MultiplayerGame__RequestObjHandler (0x006A02A0) + Handler_NewPlayerInGame_0x2A (0x006A1E70) | get_xrefs_to FUN_00595C60 |

**One byte-size correction:**

**C1 — CV4 position field is 5 bytes, NOT "~7 bytes".** The pre-v5 wire-format diagram
labeled the position field as `CompressedVector4 (variable, ~7 bytes)`, which is internally
inconsistent with its own 14-byte total: `1 + 4 + 7 + 2 + 2 = 16`, not 14. Binary truth:
**5 bytes** for the explosion path.

`CompressedVector4_WriteVirtual` at `0x006D2F10` dispatches on its `mag_as_cf16` / `param_5`
argument:

- `param_5 != 0` → 3 byte writes (vtable+0x54) + 1 short write (vtable+0x5C) = **5 bytes** (explosion path)
- `param_5 == 0` → 3 byte writes + 1 float write (vtable+0x74) = **7 bytes** (other callers)

`DamageableObject__SendExplosions_0x29` (FUN_00595C60) calls `CompressedVector4_WriteVirtual`
with `1` → 5-byte path. The receiver `FUN_006A0080` calls `CompressedVector4_ReadVirtual`
with `1` → matching 5-byte path. The 14-byte total `1 + 4 + 5 + 2 + 2 = 14` is consistent
only with CV4=5. The position rendering is corrected to
`CompressedVector4 (5 bytes: 3 direction bytes + CF16 magnitude)` with an explanatory note
about the dispatch and a cross-link to `stream-primitives.md`.

**Severity:** the C1 correction is HIGH severity for OpenBC wire-format implementation — a
clean-room implementer reading the pre-v5 "~7 bytes" would produce a 16-byte opcode 0x29
that no stock client can parse. The 14-byte total in the same diagram should have been the
red flag; the pre-v5 doc was internally inconsistent. No change to algorithm or constants.

**One clarification:**

**Clar1 — ExplosionDamage 0x38-byte struct table cross-linked to sibling leaf #20.** The
pre-v5 doc only mentioned three offsets in passing (`+0x14=radius, +0x18=radius^2,
+0x1C=damage`). Companion leaf #20 has the full 9-field table with bbox extents at +0x20
and +0x2C. The full table is now rendered in both docs (each doc must be self-sufficient
at the reader's chosen entry point) with explicit cross-link headers naming the sibling.

**Cross-doc anchor reuse:**

- **From stream-primitives (foundation #2):** CV4 dispatch on `param_5` (`mag_as_cf16`
  flag) — body cross-link added.
- **From game-opcodes (mid #4):** opcode 0x29 receiver at 0x006A0080 — confirmed.
- **From sibling leaf #20:** ExplosionDamage 0x38-byte struct (canonical there; mirrored
  here for in-context reading) and the `int()` truncation strategy column.

**Cross-doc impacts (no in-this-pass modifications; batched at family close):**

- `stream-primitives.md` (foundation #2) — same as leaf #20: document CV4 byte-size
  dispatch on `param_5` explicitly.
- `game-opcodes.md` (mid #4) — opcode 0x29 row should cross-link both CF16 leaves.
- `stateupdate.md` (mid #8) — no change (this doc covers explosion path, not StateUpdate).
- `pythonevent-wire-format.md` (leaf #14) — already cross-linked from this doc's Related
  Documents; no change needed.
- **OpenBC clean-room specs** — if any OpenBC wire-format spec for opcode 0x29 took the
  pre-v5 "~7 bytes" rendering, alert the OpenBC docwriter to use 5 bytes (CV4 with
  CF16 magnitude).

**Open questions:** none specific to this doc. OQ1 (5th encoder caller identity) is shared
with leaf #20.

**Verification methods used:**

- Shared evidence packet from game-archaeology-specialist (single Ghidra session covering
  both #20 and #21).
- `decompile_function` on FUN_006D2F10 (CV4 writer) for the param_5 dispatch confirmation.
- Arithmetic verification of all 14 rows in the Extended Precision Reference table against
  the decoder pseudocode.

**Files touched:** `docs/protocol/cf16-explosion-encoding.md` (re-rendered with breadcrumb
header preserved, v5 frontmatter added with 14 evidence rows, NOTE block with 1 byte-size
correction + 1 clarification, C1 dedicated subsection under the wire-format diagram with
CV4 byte-size dispatch table, Clar1 ExplosionDamage struct table rendered in full with
sibling cross-link, [v5-validated 2026-05-28] tags on each algorithm section, Related
Documents section refreshed); `docs/protocol/v5-validation-status.md` (§2 row #21 status
flipped from `pending` to `verified`; this §6.21 entry added).

**Header inputs for documentation-writer:**

- validated: 2026-05-28
- methodology: FUNCTION_DOC_WORKFLOW_V5
- binary fingerprint: stbc.exe, image base 0x00400000, size 6182400 bytes
- status: `verified`
- companions: `cf16-precision-analysis.md`, `stream-primitives.md`, `game-opcodes.md`,
  `wire-format-spec.md`, `pythonevent-wire-format.md`, `v5-validation-status.md`
- supersedes: prior 2026-02-15 cf16-explosion-encoding.md

### 6.22 message-trace-vs-packet-trace.md — 2026-05-28 (documentation-writer; FINAL leaf, closes protocol family 22/22)

**Status:** validated -> `partial` (after 17 claim-promotions + 3 historical-section marks + 1 label clarification; ZERO material wire-format corrections).
**Twenty-second protocol doc** under v5 — eighth and final protocol leaf — **closes the
protocol-family v5 campaign at 22/22**. This is a **cross-source differential analysis** doc
(2026-02-10 stock-dedi trace cross-referenced against TGMessage factory deserialize hook),
not a primary RE doc — every load-bearing observation has been independently anchored in
already-validated v5 mid/leaf docs across the campaign. The "partial" tag is for the
17 confidence-tag promotions + 3 historical-section marks + 1 label clarification that this
pass landed, not for unresolved evidence.

**Methodology:** Phase 1-3 per v5 workflow. Evidence packet supplied by
game-archaeology-specialist (`.claude/agent-memory/game-archaeology-specialist/message-trace-vs-packet-trace-validation-20260528.md`).
Doc anchors against 13 v5-validated companion docs — frontmatter `companions:` list
enumerates them. No new Ghidra renames or plates this pass (cross-source doc; all anchor
addresses already validated in their primary docs).

**Functions touched (cross-anchor confirmations only — no fresh Ghidra activity this pass):**

| Function | Addr | Anchor doc | Used to verify |
|----------|------|-----------|----------------|
| TGMessage_DeserializeFromBuffer | 0x006b83f0 | foundation #3 transport-layer.md | message_trace hook target (inbound-only) |
| Ship_WriteStateUpdate | 0x005B17F0 | mid #8 stateupdate.md | SUB/WPN direction-exclusivity |
| GenericEventForward | 0x0069FDA0 | mid #4 game-opcodes.md | relay-identical group counts |
| MpgameHandlePythonEvent | 0x0069F880 | leaf #14 pythonevent-wire-format.md | 0x0D LOCAL-ONLY explanation |
| CollisionEffectHandler | 0x006a2470 | leaf #15 collision-effect-protocol.md | 0x15 C->S only (no broadcast) |
| DeletePlayerUI_Handler | 0x006a1360 | leaf #17 delete-player-ui-wire-format.md | 0x17 S->C only |
| ObjNotFoundHandler | 0x006a0490 | leaf #18 objnotfound-requestobj-enterset-wire-format.md | 0x1D triad |
| (registration string) | 0x0095a0cc | mid #5 checksum-opcodes.md | "MultiplayerGame :: ChecksumCompleteHandler" anchors 0x28 label |

**Confidence-tag promotions (the 17):**

Every per-row "Promote" entry from the archaeology memo's full promotion list was applied
inline at the claim site. The session-specific count histograms and timestamp examples
stay `[trace 2026-02-10]`; the algorithmic/structural claims promote to
`[v5-validated 2026-05-28 via <anchor doc>]`. Full mapping (table verbatim from memo):

| Promoted claim | Promoted to anchor |
|----------------|---------------------|
| message_trace = TGMessage factory dispatch (inbound-only) | foundation #3 transport-layer.md |
| Direction-exclusivity SUB/WPN table | mid #8 stateupdate.md |
| Type 0x32 flags_len bit layout | foundation #3 transport-layer.md |
| Fragmented payload layout (frag 0 head, frag N continuation) | foundation #3 transport-layer.md |
| Opcode 0x07/0x08/0x09/0x0A/0x0B GenericEventForward relay parity | mid #4 game-opcodes.md (FUN_0069FDA0) |
| Opcode 0x0D PythonEvent2 C->S-only | leaf #14 pythonevent-wire-format.md |
| Opcode 0x11 RepairListPriority relay parity | mid #4 game-opcodes.md |
| Opcode 0x12 SetPhaserLevel relay parity | leaf #16 set-phaser-level-protocol.md |
| Opcode 0x13 HostMsg C->S-only | mid #4 game-opcodes.md |
| Opcode 0x15 CollisionEffect C->S-only | leaf #15 collision-effect-protocol.md |
| Opcode 0x17 DeletePlayerUI S->C-only | leaf #17 delete-player-ui-wire-format.md |
| Opcode 0x19/0x1A/0x1B relay parity | mid #4 game-opcodes.md |
| Opcode 0x1C StateUpdate direction asymmetry (SUB host-only) | mid #8 stateupdate.md |
| Opcode 0x1D ObjNotFound S->C-only | leaf #18 objnotfound-requestobj-enterset-wire-format.md |
| Opcode 0x20 / 0x21 / 0x28 checksums | mid #5 checksum-opcodes.md |
| Opcode 0x2A NewPlayer C->S-only | mid #4 game-opcodes.md (FUN_006A1E70) |
| Opcode 0x2C ChatMessage Python path | mid #6 python-messages.md |
| Post-ObjCreateTeam SUB cycling algorithm | mid #11 stateupdate-subsystem-wire-format.md |

(17 distinct anchor docs cited across the table; the row tally is by claim group, not by
anchor doc.)

**Three historical-section marks:**

1. **PACKET_TRACE DECODER BUG** — marked `> **Historical (resolved 2026-05-28)**` with
   reference to `src/proxy/ddraw_main/packet_trace_and_decode.inc.c` lines 1184-1211.
   The 2026-02-10 decoder misread `fragment_index` as the game opcode; current decoder
   reads `fragIdx`/`fragTotal` cleanly and labels continuation fragments. Misdecoded entry
   list preserved for trace cross-reference.

2. **Newly Identified Opcodes** — marked `> **Historical (anchored 2026-05-28)**`. All
   five opcodes (0x2C, 0x11, 0x12, 0x28, 0x13) are now fully anchored in dedicated v5
   docs; per-row anchor links added in the table:
   - 0x2C → python-messages.md
   - 0x11 → game-opcodes.md § GenericEventForward
   - 0x12 → set-phaser-level-protocol.md
   - 0x28 → checksum-opcodes.md § ChecksumComplete
   - 0x13 → game-opcodes.md § 0x13 HostMsg

3. **Implications for Our Proxy** — marked `> **Historical (resolved 2026-05-28)**`.
   The `flags=0x00` empty-StateUpdate disconnect symptom was the direct trigger for
   DeferredInitObject; the implementation has shipped, the symptom is gone. CLAUDE.md
   "What Works" status confirms `StateUpdate flags=0x20` ships with real subsystem health.

**One label clarification (Clar1):**

- Opcode 0x28 in the cross-reference table changed from `0x28 Unknown` to
  `0x28 ChecksumComplete` with cross-link to mid #5 checksum-opcodes.md. Registration
  string at `0x0095a0cc` ("MultiplayerGame :: ChecksumCompleteHandler") anchors the name.

**One arithmetic note added (opcode 0x21 row):**

A one-line explanation now sits below the cross-reference table: `11 = 8 + 3 first-frags`
works because message_trace counts after reassembly (8 reassembled responses), while
packet_trace counts after decryption (8 + 3 first-fragment frames = 11 raw entries).
The 3 first-fragment frames were also the source of the historical packet_trace decoder
bug — they carry inner opcode 0x21 at offset +2, which the 2026-02-10 decoder misread.

**Pattern note (canonical example):**

A new `## Pattern Note: Paired-Trace Differential Analysis` section was added at the end of
the doc body. It names the technique, lists the two hook points (TGMessage factory
deserialize vs sendto/recvfrom packet trace), describes what the differential surfaces
(server-generated messages, direction-exclusive opcodes, decoder bugs), and tags the
2026-02-10 session as the canonical example. Worth repeating for future protocol validation
work — recommended for any new opcode or new transport-type addition.

**Open questions (added to §4):**

- **OQ1** — Informal Python-message label drift: the trace block labels `0x35 GameState`
  and `0x37 PlayerRoster`; mid #6 python-messages.md names these `MISSION_INIT_MESSAGE`
  and `SCORE_MESSAGE`. Functionally accurate but informal. Non-blocking.
- **OQ2** — 0x0D PythonEvent2 re-emit path: doc shows C->S=12 with S->C=0. Leaf #14 notes
  FUN_0069F880 is LOCAL-ONLY for both 0x06 and 0x0D. Open: do the 12 received 0x0D
  events re-emit outbound as 0x06 (which would inflate S->C 0x06=251), or does the
  engine drop them? Non-blocking.

**Cross-doc anchor reuse (every load-bearing claim, with anchor doc):**

This doc's frontmatter `evidence:` list contains 18 rows; each row carries an `anchored_via:
docs/protocol/<doc>.md` field naming the v5-validated companion doc that anchored the claim.
All 13 protocol-family companion docs are listed in the frontmatter `companions:` list.

**Cross-doc impacts (batched at family close):**

- `docs/protocol/README.md` — needs entry refresh to reflect that all 22 protocol docs are
  now v5-validated (cross-source labels stable; index table needs the message-trace doc
  line to reflect "cross-source analysis (historical baseline)" framing). Batched.
- `CLAUDE.md` — Documentation Index protocol section needs all 22 entries refreshed with
  `[v5-validated 2026-05-28]` notation if the project uses that pattern; batched at family
  close commit.
- **OpenBC clean-room cascade** — no per-opcode changes needed (this doc's findings were
  already anchored in the per-opcode docs that the OpenBC mirrors derive from); spot-check
  only.

**Verification methods used:**

- Cross-doc spot-check against all 13 anchor docs (`docs/protocol/transport-layer.md`,
  `stateupdate.md`, `game-opcodes.md`, etc.) — all anchors found and consistent.
- No fresh Ghidra MCP calls this pass — anchors validated in primary docs.
- Proxy decoder current state verified at
  `src/proxy/ddraw_main/packet_trace_and_decode.inc.c` lines 1184-1211.
- CLAUDE.md "What Works" status confirmed as `StateUpdate flags=0x20` shipping.

**Files touched:** `docs/protocol/message-trace-vs-packet-trace.md` (full re-render with
breadcrumb header preserved, v5 frontmatter added with 18 evidence rows + 13 companions +
supersedes 2026-02-10, NOTE block with promotions + historical-marks + label-clar summary,
inline `[v5-validated 2026-05-28 via <anchor>]` tags on every algorithmic / structural
claim, `[trace 2026-02-10]` retained on session-specific count tables, 3 historical
section marks with one-line explanations + per-row anchor links, opcode 0x28 row corrected
to "ChecksumComplete", 0x21 arithmetic note added, new Pattern Note section, new Open
Questions section, Related Documents pointer);
`docs/protocol/v5-validation-status.md` (§2 row #22 status flipped from `pending` to
`partial` with full summary; §1 campaign overview updated to note campaign-close;
this §6.22 entry added; OQ1 + OQ2 added to §4; campaign-close summary appended below).

**Header inputs for documentation-writer:**

- validated: 2026-05-28
- methodology: FUNCTION_DOC_WORKFLOW_V5
- binary fingerprint: stbc.exe, image base 0x00400000, size 6182400 bytes
- status: `partial`
- companions: 13 v5-validated protocol docs (full list in doc frontmatter)
- supersedes: prior 2026-02-10 message-trace-vs-packet-trace.md

---

## Campaign close summary (2026-05-28)

**Protocol family v5 campaign closed at 22/22 docs validated.** All 22 protocol docs carry
v5 frontmatter, cross-anchored evidence rows, and a NOTE block summarizing this pass's
changes. The campaign ran simultaneously with portions of the engine cross-source pass and
completed on the same day (2026-05-28).

**Status distribution:**
- **`verified` (4 docs):** #15 collision-effect-protocol, #16 set-phaser-level-protocol,
  #20 cf16-precision-analysis, #21 cf16-explosion-encoding.
- **`partial` (18 docs):** Foundations (#1 wire-format-spec, #2 stream-primitives, #3
  transport-layer); mid-tier (#4 game-opcodes, #5 checksum-opcodes, #6 python-messages,
  #7 tgmessage-routing, #8 stateupdate, #9 object-replication, #10 objcreate-serialization,
  #11 stateupdate-subsystem-wire-format, #12 per-ship-subsystem-wire-format, #13
  tgobjptrevent-class); leaves (#14 pythonevent-wire-format, #17 delete-player-ui-wire-format,
  #18 objnotfound-requestobj-enterset-wire-format, #19 subsystem-integrity-hash, #22
  message-trace-vs-packet-trace).
- **README.md** — pending refresh at family close batch.

**Cross-doc disagreements resolved (§4):** 8 of 19 closed in-campaign (#1, #4, #5, #8,
#13, #14 backlog noted, #15, plus partial closure on #2 and #3 via foundation reconciliation).
Remaining open: #2, #3, #6, #7, #9-#12, #16-#17, #19 — most are minor and tracked in the
relevant per-doc §6.N entries.

**Family-close batch follow-ups (deferred to next session):**

1. **CLAUDE.md Documentation Index protocol section** — refresh all 22 entries with
   `[v5-validated 2026-05-28]` annotation matching the engine-family pattern.
2. **`docs/protocol/README.md` index table** — refresh entries to reflect v5 status and add
   the cross-source label to message-trace-vs-packet-trace.md ("Stock-dedi opcode
   cross-reference" → "Cross-source paired-trace analysis (canonical example, historical
   baseline)").
3. **OpenBC clean-room cascade** — review the 9 OpenBC clean-room wire-format specs against
   the validated BC-side docs; flag any pre-v5 derivations that need refresh (especially
   the CF16 explosion 14-byte wire frame which was `~7-byte CV4` pre-v5).
4. **§4 leftover disagreements** — schedule a small reconciliation pass for the 11 open
   §4 rows; most are address-mapping or table-duplication items that can be resolved with
   light cross-doc edits.

**Campaign outcomes:**

- Every protocol-family doc carries a v5 frontmatter (`validated:` + `binary:` fingerprint +
  per-claim `evidence:` rows with addresses + `companions:` cross-link list).
- Every load-bearing wire-format claim is anchored to a Ghidra address or function symbol;
  no claim survives without a citation or a `confidence: low` flag.
- 4 docs hit `verified` — the high-water mark for the campaign. The remaining 18 are at
  `partial` because the pass identified minor body-restructure work (frontmatter migration,
  table reconciliation, section retire/merge) that wasn't load-bearing for the wire format.
- The protocol family's foundations (wire-format-spec, stream-primitives, transport-layer)
  are anchored cleanly enough that any new leaf doc can lean on them without re-deriving
  primitives.
- Future cross-trace work has a canonical pattern (paired-trace differential analysis, §6.22
  Pattern Note) and a canonical example (the 2026-02-10 session).

**Next campaign target (not yet scheduled):** networking family (`docs/networking/`) —
GameSpy + AlbyRules + disconnect / ship-death lifecycle. Foundations already in place via
transport-layer.md anchor.

---

## Notes for the archaeology specialist's snapshot

When merging your protocol-family Ghidra snapshot, the per-doc rows should each gain
two additional fields: (1) **evidence-state** — for each load-bearing claim, whether the
Ghidra state agrees (verified / partial / disputed / not-found); (2) **renamed-since-doc** —
addresses where the doc cites `FUN_xxxxxxxx` but Ghidra now has a real name from the
post-engine-campaign annotation state.

Highest-priority spot-checks for the archaeology pass (load-bearing, cross-doc, or
disputed):

1. **0x005a2030** — **CLOSED (2026-05-28, leaf #18):** binary truth — is `ShipReadSpecies`
   (2-vtable-call ship-setup, reads species into ship+0xEC). The actual
   `GetPlayerSlotFromObjID` lives at `0x006a19a0`. objnotfound-requestobj-enterset.md
   corrected this pass (C4); objcreate-serialization.md was correct. See §4 #1 closure.
2. **0x008958d0** vs **0x0089598c** — confirm the TGMessage base vs TGDataMessage vtable
   slot counts (transport-layer.md claims 8 slots for base, 5 slots for TGDataMessage).
3. **0x00895FF4** — confirm TGEvent vtable slot count (§4 #7: 14 vs 16 vs 18 slot disagreement).
4. **ship+0x2BC slot** — §4 #4: is it "always NULL" (wire-format-spec slot map) or
   "Pulse Weapon System hash slot 11" (subsystem-integrity-hash)?
5. **DAT_009962d4** — confirm 256-slot transport factory table; confirm only 7 populated.
6. **Factory 0x866** — **CLOSED (2026-05-28, leaf #17):** lives in the **TGFactory
   registry** (`DAT_0099a578` / `DAT_0099a584`) — a class registry SEPARATE from
   NiRTTI, used exclusively by `TGFactory_DeserializeObject` (0x006D6200). Registered
   at `0x006b27a3` inside `FUN_006B2670`. 0x866 is a TGEvent subclass (vtable
   0x00895848, size 0x2C), not base TGEvent. See delete-player-ui-wire-format.md
   "Two-Registry Architecture" section and §4 #13 closure. Full TGFactory enumeration
   is still open — only 0x801, 0x865, 0x866, 0x867 confirmed.
7. **DAT_00888860** — the force-update threshold — what's its value?
8. **DAT_008e5c18** — **CLOSED (2026-05-28, leaf #18):** float `FLT_MAX`
   (`0x7F7FFFFF` = 3.4028235e+38). NOT a "low HP threshold" — it is the DamageableObject
   **undamaged** sentinel. DamageableObject ctor (FUN_00590cb0) initializes
   `dobj+0x14c = FLT_MAX`; damage application (FUN_00592c00) decrements it. The 0x1E
   gate `FLT_MAX <= dobj+0x14c AND dobj+0x150 == 0` therefore succeeds only when the
   object has NEVER been damaged and is alive — strictly stricter than a threshold
   reading. See objnotfound-requestobj-enterset-wire-format.md §C3.
9. **DAT_008955c8** — collision distance threshold — what's its value?

Anchor table §7 is the index — every entry there should appear in your snapshot so a
downstream pass can grep and confirm. Tables §7.4 (stream primitives) and §7.7 (event
class anchors) are the densest cross-reference clusters and yield the most leverage if
spot-checked first.
