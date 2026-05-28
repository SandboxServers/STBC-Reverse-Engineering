> [docs](../README.md) / [protocol](README.md) / checksum-opcodes.md

---
title: NetFile Checksum Opcodes (0x20-0x28)
type: reference
audience: re-engineer
validated: 2026-05-28
methodology: FUNCTION_DOC_WORKFLOW_V5
binary:
  name: STBC.exe
  size: 6394712
  base: 0x00400000
status: partial
companions:
  - docs/protocol/wire-format-spec.md
  - docs/protocol/transport-layer.md
  - docs/protocol/game-opcodes.md
  - docs/engine/decompiled-functions.md
  - docs/protocol/v5-validation-status.md
supersedes:
  - (prior pre-v5 checksum-opcodes.md)
evidence:
  - claim: "NetFile dispatcher FUN_006A3CD0 (NetFile::ReceiveMessageHandler) routes the receive-side checksum/file opcodes. Switch cases exist for {0x20, 0x21, 0x22, 0x23, 0x25, 0x27} only — opcodes 0x24 and 0x26 have NO handler, and 0x28 is outbound-only (no receive case)."
    address: 0x006a3cd0
    function: NetFile_ReceiveMessageHandler
    completeness: 0.6
    confidence: high
    note: "Negative claim verified by reading the dispatcher switch body. Same non-contiguous opcode set is cited by transport-layer.md C2."
  - claim: "Opcode 0x20 (ChecksumRequest, server -> client) handler FUN_006A5DF0. Reads request, runs FUN_006A6630 when index == 0, computes file hashes, sends 0x21 response. Round-0 response is prepended with a 4-byte int32 reference hash."
    address: 0x006a5df0
    function: FUN_006A5DF0
    completeness: 0.0
    confidence: high
  - claim: "Opcode 0x21 (ChecksumResponse, client -> server) handler FUN_006A4260. Routing: if byte[1] != 0xFF dispatch to FUN_006A4560 (per-round verify); else inline path (reserved branch — see open question OQ1)."
    address: 0x006a4260
    function: FUN_006A4260
    completeness: 0.0
    confidence: high
  - claim: "Per-round verify FUN_006A4560 matches received hash against the queued request entry. On per-file mismatch it calls FUN_006A4A00(...,filename,0); on App.pyc reference-hash mismatch it calls FUN_006A4A00(...,PTR_DAT_008d9af4,1). On success when *local_84c == 0 it calls FUN_006A4BB0 (success poster)."
    address: 0x006a4560
    function: FUN_006A4560
    completeness: 0.0
    confidence: high
  - claim: "Opcode 0x22 (SystemChecksumFail, server -> client) handler FUN_006A4C10. The opcode read into iVar2 is compared `(char)iVar2 == '\"'` (0x22); the matching branch displays the string at s_SystemChecksumFail_0095a434. Sender FUN_006A4A00 emits 0x22 when its param_4 == 0 (per-file mismatch case with the failing filename in the payload)."
    address: 0x006a4c10
    function: FUN_006A4C10
    completeness: 0.0
    confidence: high
    note: "C1 correction (this validation): prior doc had 0x22 paired with the VersionDifferent dialog. Binary disagrees — 0x22 routes to SystemChecksumFail."
  - claim: "Opcode 0x23 (VersionDifferent, server -> client) handler FUN_006A4C10 (shared with 0x22; the dispatched opcode selects the dialog string). The else branch routes to s_VersionDifferent_0095a420. Sender FUN_006A4A00 emits 0x23 when its param_4 != 0 (App.pyc reference-hash mismatch); payload contains PTR_DAT_008d9af4 (App.pyc reference)."
    address: 0x006a4c10
    function: FUN_006A4C10
    completeness: 0.0
    confidence: high
    note: "C1 correction (this validation): prior doc had 0x23 paired with the SystemChecksumFail dialog. Swapped to match the binary."
  - claim: "Opcode 0x25 (FileTransfer) handler FUN_006A3EA0. Reads filename + remaining bytes as file data, reimports .pyc when the path starts with 'Scripts/', and ALWAYS responds with 0x27. The Receive File Warning dialog is one-shot — gated on this+0x14 == 0 (the first 0x25 of a session); subsequent 0x25s set this+0x14 = 1 and skip the dialog."
    address: 0x006a3ea0
    function: FUN_006A3EA0
    completeness: 0.0
    confidence: high
  - claim: "Opcode 0x27 (FileTransferACK) handler FUN_006A4250, a thin wrapper that calls FUN_006A5860 (FileTransferProcessor). FUN_006A5860 either sends the next 0x25 from the per-peer file-transfer queue or, when the queue drains, sends a single-byte 0x28 and posts event 0x008000E6."
    address: 0x006a4250
    function: FUN_006A4250
    completeness: 13.1
    confidence: high
  - claim: "Opcode 0x28 (Checksum Complete) is OUTBOUND ONLY — emitted by FUN_006A5860 when the per-peer file-transfer queue empties; the NetFile dispatcher has no 0x28 case. Receivers observe 0x28 immediately before the Settings (0x00) / GameInit (0x01) pair on the wire."
    address: 0x006a5860
    function: FUN_006A5860
    completeness: 0.0
    confidence: high
    note: "Negative claim about the receive side (no dispatcher case) anchored by reading FUN_006A3CD0. Positive sender claim anchored at FUN_006A5860."
  - claim: "ChecksumRequestSender FUN_006A3820 emits exactly 4 ChecksumRequest messages (indices 0..3) by looping `while (uVar9 < 4)`. The four directory/filter string literals appear on the function's stack: scripts/App.pyc, scripts/Autoexec.pyc, scripts/ships/*.pyc (recursive), scripts/mainmenu/*.pyc. All four are queued in hash table B before request #0 is sent."
    address: 0x006a3820
    function: FUN_006A3820
    completeness: 0.0
    confidence: high
    note: "C2 correction: prior doc claimed a 5th round at index 0xFF for Scripts/Multiplayer. The 4-iteration loop bound is decisive — no in-binary 5th request emission lives here."
  - claim: "ChecksumRequestBuilder FUN_006A39B0 wire format: `[u8 0x20][u8 idx][u16 dir_len][dir bytes][u16 filter_len][filter bytes][bit recursive_flag]`. Message flag msg+0x3A = 1 (reliable)."
    address: 0x006a39b0
    function: FUN_006A39B0
    completeness: 0.0
    confidence: high
  - claim: "Reference-hash bundler FUN_006A6630 runs on the CLIENT during round 0 only. It computes 4 extra checksums — Autoexec, Scripts/ships, Scripts/Systems, Scripts/Multiplayer — and folds them into a single int32 reference hash that the round-0 response (opcode 0x21) prepends ahead of its per-round hash data."
    address: 0x006a6630
    function: FUN_006A6630
    completeness: 0.0
    confidence: high
    note: "C2 correction (this validation): Scripts/Multiplayer is bundled here, NOT in a separate 5th round."
  - claim: "Event 0x008000E6 (Settings trigger) is PUSHed by FUN_006A5860 after the outbound 0x28 send. Hash table B is at NetFile+0x38 (vtable interface ptr) and NetFile+0x44 (buckets array)."
    address: 0x006a5860
    function: FUN_006A5860
    completeness: 0.0
    confidence: high
    note: "Exactly 2 DATA xrefs to the constant 0x008000E6 — producer + registration via FUN_0069E590."
  - claim: "Event 0x008000E7 (ET_SYSTEM_CHECKSUM_FAILED) is PUSHed by FUN_006A4A00 after the fail message (0x22 or 0x23) is queued. Exactly 2 DATA xrefs to the constant — producer + registration."
    address: 0x006a4a00
    function: FUN_006A4A00
    completeness: 0.0
    confidence: high
  - claim: "Event 0x008000E8 (ET_CHECKSUM_COMPLETE) is PUSHed by FUN_006A4BB0 (success poster), the 18-line function called from FUN_006A4560 when all queued rounds verify. Exactly 2 DATA xrefs to the constant — producer + registration."
    address: 0x006a4bb0
    function: FUN_006A4BB0
    completeness: 5.1
    confidence: high
  - claim: "ChecksumCompleteHandler FUN_006A1B10 (the consumer of event 0x008000E6) sends opcode 0x00 (Settings) and opcode 0x01 (GameInit), both reliable. The Settings flag fields are written with WriteBool_Bit, which is the C1 finding inherited from wire-format-spec.md."
    address: 0x006a1b10
    function: FUN_006A1B10
    completeness: 0.0
    confidence: high
---

# NetFile Checksum Opcodes (0x20-0x28)

> [!NOTE]
> This doc is `status: partial`. NetFile dispatcher FUN_006A3CD0 accepts the non-contiguous opcode set {0x20, 0x21, 0x22, 0x23, 0x25, 0x27} — opcodes 0x24 and 0x26 have NO handler, and opcode 0x28 is **outbound only** (sent by FUN_006A5860 when the per-peer file-transfer queue drains; no receive case in the dispatcher). Two material corrections from the pre-v5 doc: (C1) the 0x22/0x23 dialog mapping was SWAPPED — 0x22 = SystemChecksumFail, 0x23 = VersionDifferent. (C2) The "5th round at index 0xFF for Scripts/Multiplayer" was a fabrication; the binary emits exactly 4 requests (0..3) and bundles Scripts/Multiplayer into round 0's reference hash via FUN_006A6630. Packet traces show a 0xFF-round message on the wire but the sender is unlocated in the binary — tracked as an open question. See [docs/guides/v5-evidence-header.md](../guides/v5-evidence-header.md) for the standard.

## Dispatcher

Receive-side dispatcher: `NetFile::ReceiveMessageHandler` at `FUN_006A3CD0` `[v5-validated 2026-05-28]`.

After the type 0x32 transport framing is stripped (see [transport-layer.md](transport-layer.md)), the game-layer payload starts with the NetFile opcode byte. The dispatcher's switch has case bodies for `0x20`, `0x21`, `0x22`, `0x23`, `0x25`, `0x27` only. Three "missing" opcodes:

| Opcode | Why it's missing |
|--------|------------------|
| `0x24` | No handler. No sender located in the binary. Considered dead. |
| `0x26` | No handler. No sender located in the binary. Considered dead. |
| `0x28` | No receive case. **Outbound only** — sent by FUN_006A5860 (see [Opcode 0x28](#opcode-0x28---outbound-only) below). |

This non-contiguous set is the canonical NetFile opcode catalog and is referenced by [transport-layer.md](transport-layer.md) C2.

## Opcode catalog

All addresses below are `[v5-validated 2026-05-28]` against `STBC.exe`.

| Opcode | Direction | Handler | Role |
|--------|-----------|---------|------|
| `0x20` | S -> C | `FUN_006A5DF0` | ChecksumRequest (client receives, computes hashes, replies with 0x21) |
| `0x21` | C -> S | `FUN_006A4260` -> `FUN_006A4560` | ChecksumResponse (per-round verify) |
| `0x22` | S -> C | `FUN_006A4C10` | SystemChecksumFail (per-file mismatch dialog) |
| `0x23` | S -> C | `FUN_006A4C10` | VersionDifferent (App.pyc reference-hash mismatch dialog) |
| `0x24` | — | (none) | No handler. No sender. |
| `0x25` | S -> C | `FUN_006A3EA0` | FileTransfer (filename + body; ACKed with 0x27) |
| `0x26` | — | (none) | No handler. No sender. |
| `0x27` | C -> S | `FUN_006A4250` -> `FUN_006A5860` | FileTransferACK (advance / drain queue) |
| `0x28` | S -> C | (sender: `FUN_006A5860`) | Completion signal — **outbound only**, no dispatcher case |

## Opcode 0x20 - ChecksumRequest (server -> client)

Handler (client side): `FUN_006A5DF0`. Sender (server side): `ChecksumRequestSender FUN_006A3820`, which loops `while (uVar9 < 4)` to build and queue exactly 4 requests via `ChecksumRequestBuilder FUN_006A39B0`. The TGMessage flag `msg+0x3A = 1` makes each request reliable.

Wire format:

```
Offset  Size  Type    Field
------  ----  ----    -----
0       1     u8      opcode = 0x20
1       1     u8      request_index (0x00-0x03)
2       2     u16     dir_len
4       var   bytes   dir_name (no null terminator)
+0      2     u16     filter_len
+2      var   bytes   filter_name (no null terminator)
+0      1     bit     recursive_flag (packed bit)
```

There are **4 checksum rounds** sent sequentially — the server waits for each `0x21` response before sending the next:

| Round | Index | Directory | Filter | Recursive | Purpose |
|-------|-------|-----------|--------|-----------|---------|
| 1 | `0x00` | `scripts/` | `App.pyc` | No | Core application module + reference-hash bundle |
| 2 | `0x01` | `scripts/` | `Autoexec.pyc` | No | Startup script |
| 3 | `0x02` | `scripts/ships` | `*.pyc` | **Yes** | Ship definition modules |
| 4 | `0x03` | `scripts/mainmenu` | `*.pyc` | No | Menu system modules |

The directory and filter strings appear as stack-loaded literals in `FUN_006A3820`. Round 0 is special: its response also carries a reference-hash bundle (see [Round 0 reference hash](#round-0-reference-hash) below).

### Round 0xFF on the wire (open question)

Packet traces from production sessions [cross-source-2026-02-25 openbc-test-20260225.md] show a real `ChecksumReq(round 0xFF)` message between round 3 and the pre-Settings phase. The 0xFF code is also reserved in the receive-side dispatch: `FUN_006A4260` has an explicit `byte[1] == 0xFF` branch. **But** static call-graph search from `FUN_006A39B0` (the only known builder) finds no in-binary sender that pushes index 0xFF. The 0xFF emission path is tracked as open question OQ1 — possible candidates include an event handler registered by `FUN_0069E590`, a deferred-init path in the NetFile ctor sequence, or an OpenBC-side emission. Until OQ1 resolves, this doc's status stays `partial`.

This replaces a pre-v5 claim that "5 rounds, index 0xFF = Scripts/Multiplayer recursive" was the canonical handshake — see C2 in the NOTE block and [Round 0 reference hash](#round-0-reference-hash).

## Opcode 0x21 - ChecksumResponse (client -> server)

Handler: `FUN_006A4260` (router) -> `FUN_006A4560` (per-round verifier).

The router dispatches on `byte[1]`:
- `byte[1] != 0xFF`: hand off to `FUN_006A4560`, which matches the received hash against the queued request entry (hash table B at NetFile+0x38 vtable / NetFile+0x44 buckets).
- `byte[1] == 0xFF`: reserved inline branch — see [Round 0xFF on the wire](#round-0xff-on-the-wire-open-question).

On per-file hash mismatch the verifier calls `FUN_006A4A00(..., filename, 0)`, which sends the 0x22 SystemChecksumFail message. On reference-hash mismatch (App.pyc) the verifier calls `FUN_006A4A00(..., PTR_DAT_008d9af4, 1)`, which sends the 0x23 VersionDifferent message. On success — when `*local_84c == 0` — the verifier calls `FUN_006A4BB0` (success poster).

Wire format:

```
Offset  Size  Type    Field
------  ----  ----    -----
0       1     u8      opcode = 0x21
1       1     u8      request_index (echoes the request's round index)
[if idx == 0]
2       4     i32     reference_hash      (from FUN_006A6630 bundle)
+0      4     i32     dir_or_file_hash
+0      var   bytes   optional file-list  (written by FUN_006A6190 — walks a tree
                                           and joins per-file hashes with '/'
                                           separator DAT_008DACA0)
```

Round 2 (`scripts/ships`) responses are significantly larger than the others because the file list is non-trivial. [cross-source-2026-02-25 trace] observations show round 2 responses around ~400 bytes (fragmented).

### Round 0 reference hash

`FUN_006A6630` runs on the CLIENT only when `bValue == 0` (i.e., during round 0). It computes 4 extra checksums and bundles them into a single int32 reference hash that gets prepended to the round-0 response:

1. Autoexec
2. `scripts/ships`
3. `scripts/Systems`
4. **`scripts/Multiplayer`**

So `scripts/Multiplayer` IS checksummed during the handshake — but as part of the round-0 bundle, NOT as a separate 5th request. The 5-round-table claim from the pre-v5 doc was a fabrication; see C2 in the NOTE block.

## Opcode 0x22 - SystemChecksumFail (server -> client)

Handler (receive): `FUN_006A4C10`. Sender: `FUN_006A4A00` with `param_4 == 0`.

Inside `FUN_006A4C10`, the opcode byte is read into `iVar2` and compared `(char)iVar2 == '\"'` (i.e., `0x22`). The matching branch displays the dialog string at `s_SystemChecksumFail_0095a434`. The handler also sets `DAT_0097fa78+0x100 = 0x65`, which triggers the subsequent disconnect.

Wire format:

```
Offset  Size  Type    Field
------  ----  ----    -----
0       1     u8      opcode = 0x22
1       2     u16     filename_length
3       var   bytes   failing_filename
```

The payload identifies which file failed the per-round hash check — `FUN_006A4A00`'s `param_4 == 0` path writes the per-file filename here.

> [!IMPORTANT]
> C1 from this validation pass: prior doc had this opcode mapped to the "VersionDifferent" dialog. The binary disagrees — 0x22 displays SystemChecksumFail. Any clean-room implementation needs the corrected mapping. See also [opcode 0x23](#opcode-0x23---versiondifferent-server---client).

## Opcode 0x23 - VersionDifferent (server -> client)

Handler (receive): `FUN_006A4C10` (shared with 0x22 — the dispatched opcode selects the dialog string). Sender: `FUN_006A4A00` with `param_4 != 0`.

The else branch in `FUN_006A4C10` (i.e., `iVar2 != 0x22`) displays the dialog string at `s_VersionDifferent_0095a420`. Same disconnect trigger applies (`DAT_0097fa78+0x100 = 0x65`).

Wire format:

```
Offset  Size  Type    Field
------  ----  ----    -----
0       1     u8      opcode = 0x23
1       2     u16     filename_length
3       var   bytes   filename
```

The payload here always identifies `PTR_DAT_008d9af4` (the App.pyc reference) — the path that triggers 0x23 is "App.pyc reference hash mismatch", which is a single fixed identity.

## Opcode 0x25 - File Transfer (server -> client)

Handler: `FUN_006A3EA0`.

`this+0x14` is the per-NetFile transfer-mode flag. On the FIRST 0x25 of a session, `this+0x14 == 0` and the handler displays the one-shot "Receive File Warning" dialog before setting `this+0x14 = 1` and proceeding to the data path. Every subsequent 0x25 in the same session goes straight to the data path without a dialog.

Wire format:

```
Offset  Size  Type    Field
------  ----  ----    -----
0       1     u8      opcode = 0x25
1       2     u16     filename_length
3       var   bytes   filename
+0      var   bytes   file_data (remainder of packet)
```

After writing the file to disk, if the path starts with `Scripts/` and ends in `.pyc`, the client reimports the module. The client then ALWAYS responds with 0x27 (no error path).

## Opcode 0x27 - File Transfer ACK (client -> server)

Handler: `FUN_006A4250`, a thin wrapper that immediately calls `FUN_006A5860` (FileTransferProcessor).

Wire format:

```
Offset  Size  Type    Field
------  ----  ----    -----
0       1     u8      opcode = 0x27
```

`FUN_006A5860` walks the per-peer file-transfer queue: if there's another file pending, it sends the next 0x25; if the queue is empty, it sends a single-byte 0x28 (see below) and posts event `0x008000E6`.

## Opcode 0x28 - Outbound only

`FUN_006A3CD0` has no `case 0x28:` — 0x28 is sent but never received as a dispatched NetFile message. The sender is `FUN_006A5860`, which emits 0x28 exactly once per peer when that peer's file-transfer queue drains. Observed on the wire immediately before Settings (0x00) and GameInit (0x01).

Wire format:

```
Offset  Size  Type    Field
------  ----  ----    -----
0       1     u8      opcode = 0x28
```

Single byte, no additional payload. After sending, `FUN_006A5860` posts event `0x008000E6` — the consumer is `ChecksumCompleteHandler FUN_006A1B10`, which sends the Settings + GameInit pair.

## Event IDs

The checksum / file-transfer machinery posts three event constants. Each has exactly 2 DATA xrefs — the producer named below plus the handler-registration site at `FUN_0069E590`. This pairing is the canonical "found the only producer" signature.

| Event ID | Producer | Role | Consumer |
|----------|----------|------|----------|
| `0x008000E6` | `FUN_006A5860` (after the outbound 0x28 send) | Settings-phase trigger | `ChecksumCompleteHandler FUN_006A1B10` (sends opcodes 0x00 + 0x01) |
| `0x008000E7` | `FUN_006A4A00` (after queuing 0x22 or 0x23) | `ET_SYSTEM_CHECKSUM_FAILED` | (kick / disconnect path) |
| `0x008000E8` | `FUN_006A4BB0` (the 18-line success poster) | `ET_CHECKSUM_COMPLETE` | (host-side completion bookkeeping) |

`FUN_006A1B10`'s consumption of event `0x008000E6` is the bridge from the NetFile dispatcher into the game-opcode layer (opcodes 0x00 / 0x01). Settings packet flag fields are written with `WriteBool_Bit` per the wire-format-spec.md C1 finding.

## Open questions

1. **OQ1 — Who sends the round-0xFF ChecksumRequest?** Static-search from `FUN_006A39B0` (the only known builder) turns up only `FUN_006A3820`, which iterates indices 0..3. Yet packet traces from openbc-test-20260225 show a real `ChecksumReq(round 0xFF)` message on the wire. The sender is in a code path not yet decompiled — candidates include an event handler registered by `FUN_0069E590`, a deferred-init path in the NetFile ctor sequence, or an OpenBC-side emission. Until this resolves, the doc cannot promote to `verified`. Trace evidence is authoritative for the wire fact.
2. **OQ2 — `PTR_DAT_008d9af4` initialization site.** The pointer is the "App.pyc reference hash" pointer referenced by `FUN_006A4A00`'s 0x23 emission path; the bytes at the static address read as garbage, confirming runtime population. Resolution belongs to [docs/engine/decompiled-functions.md](../engine/decompiled-functions.md), which already calls out this pointer.

## Cross-references

- [wire-format-spec.md](wire-format-spec.md) — hub: summary opcode tables and the broader Settings packet (opcode 0x00) wire format
- [transport-layer.md](transport-layer.md) — C2 documents the same non-contiguous NetFile opcode set; the type 0x32 envelope is layered underneath everything here
- [game-opcodes.md](game-opcodes.md) — opcodes 0x20-0x28 appear as DEFAULT entries in the MultiplayerGame jump table; that doc's default-cleanup rows are anchored to this dispatcher
- [docs/engine/decompiled-functions.md](../engine/decompiled-functions.md) — per-handler addresses and `PTR_DAT_008d9af4` notes
- [v5-validation-status.md](v5-validation-status.md) §6.5 — this doc's row in the protocol re-validation campaign
