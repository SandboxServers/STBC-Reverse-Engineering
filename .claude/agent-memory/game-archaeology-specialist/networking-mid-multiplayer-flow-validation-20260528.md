---
name: networking-mid-multiplayer-flow-validation-20260528
description: Networking mid #7 validation memo. multiplayer-flow.md complete client/server join flow 5-phase narrative. ZERO wire corrections. 3 material clarifications/corrections (slot offset +0x78 not +0x74, PlayWindow not TopWindow at 0x0097e238, silent-failure claim wrong). Phase 5 InitNetwork/DeferredInitObject anchors verified against WSN+0x2C/+0x30 in TGWinsockNetwork_ProcessIncomingPackets.
metadata:
  type: project
---

# Networking Mid #7 — `multiplayer-flow.md` v5 Validation

**Date**: 2026-05-28
**Binary**: STBC.exe (image base 0x00400000)
**Doc**: `docs/networking/multiplayer-flow.md` (188 lines, 5 phases + key-functions table + Phase 5 + timing + failure points)
**Status**: `partial` — 3 corrections, 4 clarifications, ZERO wire-format errors

## Bottom line
The 5-phase join narrative is structurally correct. Every function address resolves. Wire formats align with binary. Three claims are technically wrong (slot offset, PlayWindow vs TopWindow, silent failure), but they don't change the join sequence. Doc is mid-doc quality: shows real understanding of the dispatcher graph and uses correct function addresses throughout, but predates the ui-class-hierarchy.md (0x0097e238 = PlayWindow) and per-byte slot-offset verification.

## Cross-anchoring inventory

Pre-anchored from completed v5 validations (all confirmed):
- MultiplayerGame ReceiveMessageHandler @ 0x0069F2A0 (Ghidra: `MpgameHandleMessage`) — protocol mid #4
- NetFile dispatcher FUN_006a3cd0 — protocol mid #5
- ChecksumCompleteHandler @ 0x006a1b10 — networking foundation #1
- TGNetwork_HostOrJoin @ 0x006b3ec0 (Ghidra: `TGWinsockNetwork_HostOrJoin`) — foundation #1
- WSN port setter @ 0x006b9bb0 — foundation #1
- TGWinsockNetwork_SendTGMessage @ 0x006b4c10 (Ghidra-named) — protocol family
- 0x008000e7 / 0x008000e8 event IDs — protocol mid #5

Spot-verified live for this doc:
- FUN_006a0a30 (NewPlayerHandler) — slot stride 0x18 confirmed; +0x78/+0x7C offsets read directly from `(iVar6 * 3 + 0xf) * 8` formula
- FUN_006a1b10 (ChecksumComplete) — Settings packet wire: `WriteChar(0) WriteFloat(gameTime) WriteBool_Bit(DAT_008e5f59) WriteBool_Bit(DAT_0097faa2) WriteChar(playerSlot) WriteShort(mapLen) WriteBytes(mapName) WriteBool_Bit(passFail) [if passFail: FUN_006f3f30 hash block]`
- FUN_006a4260 — `byte[1] != 0xFF` → FUN_006a4560 (checksum path); `byte[1] == 0xFF` → FUN_006a4e70/006a5570 (file-transfer path) + ends with FUN_006a5860
- FUN_006a4560 — index 0 reads reference int hash then dir hash; FUN_006a5290 success / FUN_006a4a00 fail
- FUN_006a4a00 — opcode 0x22 (param_4=0, file fail) vs opcode 0x23 (param_4=1, ref string fail) ✓ matches mid #5 swap
- FUN_006a4bb0 — posts `0x008000e8` ✓ (ChecksumComplete event)
- FUN_006a5860 — client's queue-empty path sends opcode 0x28, posts `0x008000e6`
- FUN_006b5c90 (ProcessIncomingPackets) — confirms WSN+0x2C (param_1[0xb]) is sorted peer-array ptr; WSN+0x30 (param_1[0xc]) is count; binary search uses `*(int *)(peer + 0x18)` as sort key ✓ Phase 5 claim

## v5 Triage

### C — Corrections

**C1: Player slot offset is +0x78, not +0x74**
- Doc Phase 2: "Iterates player slots (0-15, each 0x18 bytes at this+0x74)"
- Binary (FUN_006a0a30): `pcVar7 = (char *)(param_1 + 0x78);` for the iteration loop; slot 0 active byte at `(0*3+0xf)*8 = 0x78`; peer ID at `param_1 + 0*0x18 + 0x7c`.
- ChecksumCompleteHandler (FUN_006a1b10) cross-confirms: `puVar7 = (undefined4 *)(param_1 + 0x7c)` reads peer ID at slot 0, and `puVar7 + 6` (0x18 byte stride) for slot 1.
- Source of error: pre-existing UI-class-hierarchy memo says "+0x74 playerSlots"; that field name may refer to a 4-byte "playerSlots base index" before the actual slot array. Doc inherits that off-by-4.
- Impact: cosmetic for a narrative doc; would matter if someone tried to access slot 0 via `mpgame+0x74`.

**C2: 0x0097e238 is PlayWindow, not TopWindow**
- Doc Phase 1: "If already in multiplayer (DAT_0097fa8a): passes event to TopWindow vtable+0x68"
- Binary (FUN_00504890): `piVar2 = DAT_0097e238; ... (**(code **)(*piVar2 + 0x68))(param_2)`
- Per CLAUDE.md memory and ui-class-hierarchy.md (engine #9): `0x0097e238 = PlayWindow`, `0x009878cc = TopWindow`. Confirmed by the same FUN_00504890 also using `DAT_009878cc` for a different vtable call (line `(**(code **)(*DAT_009878cc + 300))(param_1,0)`).
- Impact: misnames the dispatcher receiver. Doc should say "PlayWindow vtable+0x68" (which forwards the event to its container).

**C3: Client checksum-handler does NOT silently drop the response when no files found**
- Doc Phase 3: "If NO files found (returns 0): response NOT sent! Silent failure!"
- Binary (FUN_006a5df0): `if (cVar1 == '\0')` (FUN_0071f270 returned 0) branch builds a 6-byte response:
  - `WriteChar(0x21) WriteChar(bValue) [if bValue==0: WriteInt(FUN_0071aec0(0xffff))] WriteInt(FUN_007202e0(local_40c)+1)`
  - Then calls **FUN_006b89a0** (NOT TGNetwork_SendTGMessage) — this is the unreliable send path.
- So the response IS sent, just via a different sender (likely raw sendto) with a placeholder dir-name hash instead of file hashes.
- Impact: marketing-language correction. The bug investigation that led to "silent failure" was likely seeing real failures from a different cause (e.g., FUN_006b89a0 path drops the message, or the placeholder hash mismatches server-side).

### Clar — Clarifications

**Clar1: FUN_006a4260 also handles file-transfer (byte[1] == 0xFF) path**
- Doc says: "FUN_006a4260 checks byte[1]: if != 0xFF, calls FUN_006a4560 (always for indices 0-3)"
- True — indices 0-3 are `!= 0xFF` and go to FUN_006a4560. But the ELSE branch (byte[1] == 0xFF) handles a streamed-file-block format: reads `WriteChar(0x21) WriteChar(0xFF) WriteInt(hash)`, calls FUN_006a4e70 on hash match (file accept) or FUN_006a5570 on mismatch (file reject). After processing, calls FUN_006a5860 (FileTransferProcessor).
- The doc is correct for the join-checksum flow but incomplete on the broader 0x21 protocol shape.

**Clar2: Both settings packet boolean fields use WriteBool_Bit, not WriteByte**
- Doc Phase 4: "[0x00][gameTime:f32][setting1:u8][setting2:u8][playerSlot:u8] [mapNameLen:u16][mapName:bytes][passFail:u8]"
- Binary writes:
  - `WriteChar(0)` — 1 byte ✓
  - `WriteFloat(gameTime)` — 4 bytes ✓
  - `WriteBool_Bit(DAT_008e5f59)` — **1 BIT**, doc says u8
  - `WriteBool_Bit(DAT_0097faa2)` — **1 BIT**, doc says u8
  - `WriteChar(playerSlot)` — 1 byte ✓
  - `WriteShort(mapLen) WriteBytes(mapName)` ✓
  - `WriteBool_Bit(passFail)` — **1 BIT**, doc says u8
  - `if (passFail) FUN_006f3f30(stream)` — extra hash block
- CLAUDE.md doc index already notes "Settings packet uses WriteBit"; consistent with wire-format-spec v5 validation.
- Impact: wire format is byte-aligned overall (bits are packed by TGBufferStream's bit-accumulator), but the doc's "[setting1:u8]" notation is misleading.

**Clar3: TGNetwork_HostOrJoin sets WSN+0x10E differently for host vs join**
- Doc Phase 1: "addr=0: HOST mode (sets WSN+0x10E=1, state=2, fires 0x60002 event) / addr!=0: JOIN mode (sets WSN+0x10E=0, state=3, sets WSN+0x10F=1)"
- Binary confirms: `WSN+0x10E = 1` (host) or `0` (join), `WSN+0x10F = 1` only in join branch as flag, state field is `WSN[5]` (offset 0x14). All correct.
- Minor: state values are written via `param_1[5] = 2` (host) or `param_1[5] = 3` (join), and the host branch also fires event 0x60002. ✓

**Clar4: "Exponential backoff" for not-ready retry is just a fixed delay**
- Doc Phase 2: "When +0x1F8 = 0 (not ready): Creates timer event to retry later (with exponential backoff)"
- Binary (FUN_006a0a30 not-ready branch): `fVar1 = *(float *)(DAT_009a09d0 + 0x90) + _DAT_00888860; *(float *)(iVar3 + 0x14) = fVar1;` — adds a CONSTANT (`_DAT_00888860`) to current game time. No backoff.

### R — Removals

(none — doc has no fabrications, just imprecisions)

### OQ — Open Questions

**OQ1: What does FUN_006b89a0 (the no-files-found send path) actually do?**
- 0x006b89a0 - 0x006b89dd (62 bytes). It's an unreliable send for the empty checksum response. Not anchored.

**OQ2: What is the +0x8a flag on UtopiaModule?**
- Doc calls it "IsMultiplayer" but the FUN_00445d90 code path suggests it's more specifically a "force host mode" flag (when set: zeroes addr, forces port 0x5655). May be the dedicated-server flag.

### H — Historical sections (mark in doc)

**H1: "Our Server (Broken)" column in Phase 5 timing table**
- Reflects the InitNetwork bc-flag bug (peer+0xBC). RESOLVED per CLAUDE.md "What Works" — peer-array detection now fires within ~1.4s.

**H2: Potential Failure Point #4 ("Client FUN_0071f270 returning 0 - client silently drops response")**
- Wrong premise per C3. Should be removed or rewritten — client DOES send something, just via unreliable path with placeholder hash. The actual failure mode (if any) is on FUN_006b89a0 or server-side hash mismatch.

## Key offsets verified live

| Offset | Field | Source |
|--------|-------|--------|
| MpgameBase+0x70 | maybe map/level reference (deref'd in FUN_006a1b10) | FUN_006a1b10 |
| MpgameBase+0x74 | unknown 4-byte field (NOT slot start) | gap between 0x70 and 0x78 |
| MpgameBase+0x78 | slot[0] active byte | (0*3+0xf)*8=0x78 in FUN_006a0a30 |
| MpgameBase+0x7C | slot[0] peer ID (u32) | `param_1 + 0*0x18 + 0x7c` |
| MpgameBase+0x1F8 | ready-for-new-players flag (byte) | doc + FUN_006a0a30 ✓ |
| MpgameBase+0x1FC | max players (int) | FUN_006a0a30 `if (param_2 < *(int *)(param_1 + 0x1fc))` |
| WSN+0x10D | (unknown — cleared in HostOrJoin success) | FUN_006b3ec0 |
| WSN+0x10E | host-or-join flag (1=host, 0=join) | FUN_006b3ec0 ✓ |
| WSN+0x10F | join-only flag (=1 in join branch) | FUN_006b3ec0 ✓ |
| WSN+0x14 (=[5]) | state field (2=hosting, 3=joining, 4=idle) | FUN_006b3ec0 ✓ |
| WSN+0x28 (=[10]) | unknown | seen in FUN_006a3820 |
| WSN+0x2C (=[11]) | peer hash-table/sorted-array pointer | FUN_006b5c90, FUN_006a1b10 ✓ Phase 5 |
| WSN+0x30 (=[12]) | peer count | FUN_006b5c90 (`param_1[0xc]` in binary search) ✓ Phase 5 |
| WSN+0x18 (=[6]) | local peer ID (compared to iVar11 to know "is this us") | FUN_006b5c90 |
| WSN+0x338 | UDP port number | FUN_006b9bb0 |
| Peer+0x18 | peer ID (sort key for WSN+0x2C array) | FUN_006b5c90 binary search ✓ Phase 5 |
| Peer+0xBC | "bc flag" — broken indicator per CLAUDE.md, used in ChecksumComplete | FUN_006a1b10 `*(char *)(iVar4 + 0xbc) != '\0'` |

## Confidence per Phase

| Phase | Confidence | Notes |
|-------|-----------|-------|
| 1 (StartGameHandler + InitMultiplayer) | high | C2 affects narrative only |
| 2 (TGNetwork_Update + NewPlayerHandler) | high | C1 cosmetic, Clar4 minor |
| 3 (Checksum exchange) | high | Most byte-anchored phase; mid #5 already validated 0x20-0x28 |
| 4 (Post-checksum settings) | high | Clar2 (bit-vs-byte) is the only nuance |
| 5 (InitNetwork + DeferredInitObject) | medium | WSN+0x2C/+0x30 confirmed; the 1.4s timing claim and Python InitNetwork side are not in the binary (proxy/Python code) |

## Doc completeness for downstream

- Function table (16 entries) — all addresses resolve, all roles correct
- Phase 5 narrative is the only novel content (Phase 1-4 overlap with foundations #1-#5)
- Suitable for clean-room implementation if C1/C2/C3 corrections applied and H1/H2 marked historical
