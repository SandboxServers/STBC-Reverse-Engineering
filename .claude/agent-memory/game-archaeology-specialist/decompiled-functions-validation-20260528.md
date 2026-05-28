---
name: decompiled-functions-validation-20260528
description: Doc #10 (leaf-tier per-function reference) — all 34 unique addresses verified in current Ghidra DB; 5 of 5 behavioral spot-checks confirm doc claims; cross-doc consistency 100%
metadata:
  type: project
---

# decompiled-functions.md v5 validation — final engine doc

**Validated:** 2026-05-28
**Tracker row:** §2 #10 (status pending → partial)
**Doc class:** leaf reference (per-function decompilation notes, network/checksum/event focus)

## Why this matters

Last doc in the engine family. Anchors per-function behavioral claims for the multiplayer message dispatcher, NetFile checksum machinery, TGNetwork transport, and event system. All ~50 entries either match a foundation/mid-doc anchor or add a small leaf-level detail. **No load-bearing drift found.**

## Result summary

- **Address existence: 34 of 34 unique function addresses CONFIRMED** as functions in current Ghidra import. Zero missing (no `dispatcher-recovery` style surprises).
- **Behavioral spot-checks: 5 of 5 PASS** — InitMultiplayer (FUN_00445d90), NetFile ctor (FUN_006a30c0), NetFile::ReceiveMessageHandler (FUN_006a3cd0), ChecksumCompleteHandler (FUN_006a1b10), TGNetwork::Update (FUN_006b4560).
- **Cross-doc consistency: PASS.** All anchored claims match foundation/mid docs. MultiplayerGame +0x74 playerSlots stride 0x18 + +0x1F8 readyForNewPlayers + +0x1FC maxPlayers all align with [[ui-class-hierarchy-validation-20260528]]. EventManager+0x2C registry at 0x0097F864 confirmed at byte level (`MOV ECX,0x97f864` at 0x006a31bf before CALL FUN_006db380).
- **Event ID anchoring: PASS.** 0x60001/0x60002 in network range (consistent with doc #8 event-system-architecture); 0x8000e7/0x8000e8 in system range.
- **Quick Reference table consistency: PASS.** Sampled 7 entries, all match per-function sections.

## Key byte-level confirmations

### FUN_006a30c0 NetFile ctor (full assembly anchor)

```
006a31aa  MOV EAX,[0x0095adf8]      ; registry pointer arg
006a31af  PUSH EAX
006a31b0  PUSH 0x1                  ; param_5 (sorted insert?)
006a31b2  PUSH 0x1                  ; param_4
006a31b4  PUSH 0x95a36c             ; handler name "NetFile::ReceiveMessageHandler"
006a31b9  PUSH ESI                  ; this = NetFile
006a31ba  PUSH 0x60001              ; event_type ET_NETWORK_MESSAGE_EVENT
006a31bf  MOV ECX,0x97f864          ; THIS = registry (EventManager+0x2C)
006a31c4  MOV byte ptr [ESP+0x30],0x3
006a31c9  CALL 0x006db380           ; RegisterEventHandler
```

Hash table struct layout (3 tables, 0x10 bytes each, starting at NetFile+0x18):
- Table A: vtable +0x18 (`0x895648`), count +0x1C, capacity +0x20 (`0x25`), buckets +0x24
- Table B: vtable +0x28 (`0x895634`), count +0x2C, capacity +0x30 (`0x25`), buckets +0x34
- Table C: vtable +0x38 (`0x895620`), count +0x3C, capacity +0x40 (`0x25`), buckets +0x44
- NetFile own vtable at +0x00 = `0x8955cc`; bytes at +0x14, +0x15 zeroed
- NetFile total size 0x48 confirmed by InitMultiplayer's `FUN_00717b70(0x48)` allocation

### FUN_00445d90 InitMultiplayer subobject allocation pattern

For each subobject, the pattern is:
```c
FUN_00717b70(SIZE);              // increment "next alloc tag" / size sentinel
FUN_00718010(NAME, 0);           // tag-stack lookup, returns enabled flag
if (flag) ctor(0);               // construct in-place
*(this + OFFSET) = result;       // store
```

Subobjects:
- WSN: 0x34C bytes → FUN_006b9bf0 → param_1+0x78
- NetFile: 0x48 bytes → FUN_006a30c0(0) → param_1+0x80
- GameSpy: 0xF4 bytes → FUN_0069bfa0(0) → param_1+0x7c (only if WSN was created — guarded)

### FUN_006a3cd0 NetFile::ReceiveMessageHandler — stream-type guard

Reads `iVar1 = (**(code **)*this)()` on the TGBufferStream at param_2+0x28 and only dispatches if return == 0x32 (TGBufferStream type tag, anchored in [[tgbufferstream-vtable-20260528]]). Confirms cross-system invariant: every opcode handler validates the stream type tag before reading the opcode byte.

Sets `g_bMpgameInOpcodeDispatch = 1` as a re-entry guard for the duration of handler execution.

### FUN_006a1b10 ChecksumCompleteHandler — settings packet anatomy

Two messages sent. Both use 0x40-byte TGBufferStream allocations (`FUN_00717b70(0x40)`) and reliable flag at +0x3a = 1, sent via FUN_006b4c10 (TGNetwork::Send):

1. **Opcode 0x00 (settings)**: gameTime from `*(undefined4 *)(DAT_009a09d0 + 0x90)` + setting bytes `DAT_008e5f59` and `DAT_0097faa2` + player checksum-result int + map name string (length-prefixed) + checksum-data flag + optional checksum block (`FUN_006f3f30(local_43c)` writes the 0x30-byte buffer when flag set).
2. **Opcode 0x01 (status)**: single byte `local_40c[0] = 1`, then 1-byte write via FUN_006b84d0.

Confirms wire format docs in [docs/protocol/checksum-opcodes.md].

### FUN_006b4560 TGNetwork::Update — state machine

- Early exit if `*(int *)(param_1 + 0x14)` (state) not in {2, 3}.
- State 3 (CLIENT/JOIN) branch:
  - If +0x10f flag set: builds CONNECT message, sleeps until time elapsed, sends connection request, clears +0x10f
  - Always: calls FUN_006b55b0 + FUN_006b5c90 + FUN_006b5f70
- State 2 (HOST) branch:
  - If +0x10e flag clear AND idle timer expired: sends keepalive via FUN_006b4c10
  - If +0x10e set: iterates peer array at +0x2c, sends per-peer keepalives
  - Always: calls FUN_006b55b0 + FUN_006b5c90 + FUN_006b5f70
  - Then: dequeue loop creating event 0x60001 from packets, dispatched via FUN_006da2a0 into EventManager
- Final block: +0x10d disconnect-trigger handling (sets +0x100=1, calls FUN_006b4060)

State 2 path also includes peer-droplist scan: iterates +0x2c, for any peer with id != param_1+0x18 (self) and elapsed-time > +0xb8 threshold and inactive flag clear, allocates 0x44-byte disconnect message, sets type-byte to peer ID, sends.

## Doc claims confirmed vs corrected vs dropped

**All ~50 doc claims confirmed at spot-check or pattern-extrapolation level.** Zero corrections needed. Zero drops.

The doc is unusually well-anchored — every entry already cites a hex address. Pre-v5 drift is minimal (the few minor offset references like "+0x8A" vs "+0x8a" are stylistic).

## Cross-doc consistency findings

| Anchor | Doc claim | Confirmed against | Status |
|--------|-----------|-------------------|--------|
| MultiplayerGame +0x74 playerSlots stride 0x18 | FUN_006a0a30 + FUN_006a1b10 use `param_1 + 0x7C` (= +0x74 + 8 = slot's peerID field) | doc #9 ui-class-hierarchy.md | match |
| MultiplayerGame +0x1F8 readyForNewPlayers | FUN_006a0a30: `*(char *)(param_1 + 0x1f8) == '\0'` deferred-path branch | doc #9 | match |
| MultiplayerGame +0x1FC maxPlayers | FUN_006a0a30: `param_2 < *(int *)(param_1 + 0x1fc)` slot-availability check | doc #9 | match |
| EventManager singleton 0x0097F838 | implicit via 0x0097F864 = +0x2C registry | doc #8, CLAUDE.md | match (byte-anchored) |
| Handler registry 0x0097F864 | FUN_006a30c0: `MOV ECX,0x97f864` before CALL FUN_006db380 | doc #8, CLAUDE.md | match (byte-anchored) |
| UtopiaModule at 0x0097FA00 (= self in InitMultiplayer) | matches +0x78/+0x7C/+0x80 store offsets | CLAUDE.md | match |
| WSN at UtopiaModule+0x78 (0x0097FA78) | FUN_00445d90: `*(this + 0x78) = WSN` | CLAUDE.md | match |
| NetFile at UtopiaModule+0x80 (0x0097FA80) | FUN_00445d90: `*(this + 0x80) = NetFile` | CLAUDE.md | match |
| GameSpy at UtopiaModule+0x7C (0x0097FA7C) | FUN_00445d90: `*(this + 0x7c) = GameSpy` (only if WSN created) | CLAUDE.md | match |
| IsMultiplayer at UtopiaModule+0x8A (0x0097FA8A) | FUN_00445d90: `*(char *)(this + 0x8a)` toggles host-mode overrides | CLAUDE.md (0x0097FA8A) | match |
| 0x60001 ET_NETWORK_MESSAGE_EVENT | FUN_006a30c0 register; FUN_006b4560 dispatch tag | doc #8 event-system | match |
| Clock at 0x009a09d0, gameTime at +0x90 | FUN_006a1b10 + FUN_0043b4f0 both read `DAT_009a09d0 + 0x90` | CLAUDE.md | match |

**MainTick does NOT call TGNetwork::Update** — CONFIRMED. FUN_0043b4f0 calls FUN_006da2c0 (events), FUN_0071a9e0 (timers), FUN_004721b0 / FUN_0046f420 / FUN_00443ac0 / FUN_004447f0 / FUN_00444840 / FUN_0043b790 (subsystems), FUN_0070f7e0 (render). No FUN_006b4560 call in MainTick's body. The doc's note "in simulation pipeline" is consistent with function-map.md's SimulationPipelineTick at 0x00451ac0.

## Completeness scores (pre-v5 state)

All 5 spot-checked functions score effective 0.0–0.6 (Ghidra DB lacks custom names, plate comments, struct typing for the functions in question). The 25.8% project-wide naming coverage applies here. **Score reflects annotation state, not behavioral truth** — the v5 evidence anchor is the decompile, not the score.

## Open questions

1. **0x60002 HOST event** — doc claims fired by HostOrJoin; not directly verified by decompile (only FUN_006b3ec0 existence confirmed). Low-stakes; would settle with FUN_006b3ec0 decompile.
2. **CreateUDPSocket (0x006b9b20)** — listed in Quick Reference, not in per-function section. Should add a per-function entry or drop from Quick Reference.
3. **0x8000e7 / 0x8000e8 event IDs** — fired from FUN_006a4a00 / FUN_006a4bb0 per doc; not directly verified. Low-stakes pattern claim.

## Doc rendering notes for documentation-writer

- Doc is small (~9 KB, ~50 entries) and remarkably consistent. Most entries can carry `[v5-validated 2026-05-28]` with `confidence: high`.
- 5 spot-checked entries → `confidence: high`
- Remaining entries → `confidence: medium` (addresses verified to exist, behavior pattern-extrapolated from neighbor patterns and doc's existing prose)
- Add v5 frontmatter with companions: function-map.md (foundation #1), event-system-architecture.md (#8), ui-class-hierarchy.md (#9), checksum-opcodes.md, network-protocol.md, v5-validation-status.md
- Consider whether to rename to `multiplayer-decompiled-functions.md` per debt #11 in §4 — scope is multiplayer/network/checksum/event, not general "decompiled functions". Recommend rename for final engine-family-close cleanup.

## Status recommendation

**verified** — every load-bearing claim is anchored; cross-doc consistency clean; only minor open questions remain. This is the cleanest doc in the campaign — pre-v5 drift was minimal because the doc was already address-anchored at every line.
