---
name: checksum-opcodes-validation-20260528
description: Protocol doc #5 (mid) — checksum-opcodes.md validation. Two material corrections (C1 0x22/0x23 dialog swap; C2 5-round table fabrication), plus 0x28 sender + 3 event IDs fully anchored. Reveals 5th-round 0xFF sender is unlocated.
metadata:
  type: project
---

# Doc #5: docs/protocol/checksum-opcodes.md

Phase 1-3 validation, 2026-05-28. ~35 load-bearing claims, finished in ~1 hour. The decompiled-functions.md cross-anchors made it fast — but the doc had **two material errors** plus several refinements worth recording.

## Key binary anchors (all in program: STBC.exe)

| Address | Function | Role |
|---|---|---|
| 0x006A3CD0 | NetFile dispatcher | switch on byte[0]: cases 0x20, 0x21, 0x22, 0x23, 0x25, 0x27. NO 0x24, 0x26, 0x28. |
| 0x006A3820 | ChecksumRequestSender | Sends 4 requests (indices 0..3). String literals on stack: App.pyc, Autoexec.pyc, Scripts/ships *.pyc (recursive), Scripts/mainmenu *.pyc. |
| 0x006A39B0 | ChecksumRequestBuilder | Wire: `[0x20][idx][u16 dir_len][dir][u16 fil_len][fil][recursive_bit]`. msg+0x3A=1 (reliable). |
| 0x006A4260 | 0x21 response receiver | Dispatch: `if byte[1] != 0xFF → FUN_006A4560` else inline path. |
| 0x006A4560 | Per-round verify | Reads hash, matches against queued request, calls FUN_006A4A00(...,filename,0) on mismatch OR FUN_006A4A00(...,PTR_DAT_008d9af4,1) on reference-hash mismatch. |
| 0x006A4A00 | Fail-message sender | param_4==0 → WriteChar(0x22) + per-file filename; param_4!=0 → WriteChar(0x23) + PTR_DAT_008d9af4 ("App.pyc"). Posts event 0x008000E7. |
| 0x006A4C10 | 0x22/0x23 receiver | iVar2==0x22 → display "SystemChecksumFail"; else (0x23) → "VersionDifferent". Sets DAT_0097fa78+0x100=0x65 (disconnect). |
| 0x006A4BB0 | AllChecksumsPassed | Posts event 0x008000E8. Called from FUN_006A4560 when *local_84c==0. |
| 0x006A5DF0 | 0x20 receiver (client) | Reads request, runs FUN_006A6630 if bValue==0, computes hashes, sends 0x21 response. When bValue==0, response prepends int32 reference hash. |
| 0x006A6630 | Reference-hash extra checksums | 4 calls: Autoexec, Scripts/ships, Scripts/Systems, **Scripts/Multiplayer**. Bundles into round-0 response — NOT a separate 5th round. |
| 0x006A3EA0 | 0x25 receiver | Reads filename + remainder as file data. Reimports `.pyc` if path starts `Scripts/`. ALWAYS responds with 0x27. |
| 0x006A4250 | 0x27 receiver | Thin wrapper → FUN_006A5860. |
| 0x006A5860 | FileTransferProcessor | Sends next 0x25 from queue OR sends single-byte 0x28 + posts event 0x008000E6 when queue empty. |
| 0x006A1B10 | ChecksumCompleteHandler | Sends 0x00 Settings + 0x01 GameInit (both reliable). Uses WriteBool_Bit for settings flags (confirms wire-format-spec.md C1 correction). |

## Material corrections (C1/C2)

### C1: 0x22/0x23 dialog swap

**Doc says**: 0x22="VersionDifferent", 0x23="SystemChecksumFail"
**Binary says**: 0x22→"SystemChecksumFail" (per-file mismatch), 0x23→"VersionDifferent" (App.pyc reference mismatch)

Proof: FUN_006A4C10 reads opcode and the comparison `(char)iVar2 == '\"'` (0x22) routes to `s_SystemChecksumFail_0095a434`; the else (0x23) routes to `s_VersionDifferent_0095a420`. FUN_006A4A00 confirms the sender side: param_4=0 writes 0x22 with per-file path; param_4=1 writes 0x23 with PTR_DAT_008d9af4 (App.pyc reference).

**Severity**: Material. Affects any clean-room implementation following the doc.

### C2: "5th round = index 0xFF, Scripts/Multiplayer" — fabrication

**Doc says**: There are 5 rounds: 0, 1, 2, 3, 0xFF. Round 0xFF checksums `Scripts/Multiplayer/*.pyc` recursive.
**Binary says**:
- FUN_006A3820 (only ChecksumRequestSender) emits **exactly 4 requests** (indices 0..3).
- `Scripts/Multiplayer` is checksummed by the CLIENT during round 0 via FUN_006A6630 (alongside Autoexec, Scripts/ships, Scripts/Systems), with the result bundled into the round-0 response as a 4-byte `int32` reference hash.
- The 0xFF code path in FUN_006A4260 (response handler) IS reserved but its triggering sender is **not located** in the binary I decompiled.

**Trace evidence**: openbc-test-20260225.md shows a real session with "ChecksumReq(round 0xFF)" between rounds 3 and PreSettings. So 0xFF IS sent in production handshakes — but by a code path I haven't found.

**Severity**: Material — the 5-row table mis-attributes Scripts/Multiplayer to a non-existent separate round.

## Wire-format refinements (C3/C4)

### C3: 0x25 dialog is first-shot only

Doc framing is OK but doesn't make clear: the receive-file warning dialog appears only when `this+0x14 == 0` (first 0x25 of session); subsequent 0x25s set `this+0x14 = 1` and route to FUN_006A3EA0 for actual file write.

### C4: 0x21 payload is NOT opaque

Doc says "variable opaque hash_data". Binary says: `[if idx==0: int32 ref_hash][int32 dir_hash][optional file-list via FUN_006A6190]`. FUN_006A6190 walks a tree and writes hashes joined by `/` separator (DAT_008DACA0).

## Net-new content (worth adding to doc)

1. **0x28 sender** = FUN_006A5860 (the doc says "no dedicated handler" but doesn't name the sender)
2. **Event ID table** — 3 events: 0x8000E6 (post-checksum trigger Settings), 0x8000E7 (fail), 0x8000E8 (success). Each has exactly 2 xrefs (the producer + the FUN_0069E590 handler-registration).
3. **NetFile dispatcher accepts non-contiguous opcodes** {0x20, 0x21, 0x22, 0x23, 0x25, 0x27} — this is the transport-layer.md C2 correction applied here.
4. **Hash table B** offsets: at +0x38 (vtable interface), +0x44 (buckets array). Used by sender's queueing (FUN_006A39B0) and receiver's lookup (FUN_006A4260, FUN_006A4560, FUN_006A5860).

## Open questions remaining after this dig

1. **OQ1 — Who sends the round-0xFF ChecksumRequest?** Static-search FUN_006A39B0 callers turned up only FUN_006A3820, which iterates 0..3. The 0xFF sender is in a code path I didn't decompile. Possible candidates: event handler registered by FUN_0069E590, a deferred-init function in the NetFile ctor sequence, or possibly OpenBC-side emission. Worth a dedicated dig.
2. **OQ4 — `PTR_DAT_008d9af4` initialization**. The pointer slot is at 0x008d9af4, but the bytes at that offset read as garbage as a string. Runtime-populated (probably in NetFile ctor or DllMain). decompiled-functions.md describes it as the "App.pyc reference hash pointer" — defer to that doc.

## Completeness scores (all worker classification)

- FUN_006A3CD0 (dispatcher): effective 0.6, max 83.1 (lots of magic numbers undocumented — by design for a switch table)
- FUN_006A39B0 (request builder): 0.0/81.9
- FUN_006A4260 (response receiver): 0.0/83.1
- FUN_006A4560 (verifier): 0.0/81.9
- FUN_006A4C10 (fail receiver): 0.0/83.1
- FUN_006A4A00 (fail sender): 0.0/81.9
- FUN_006A4BB0 (success poster): 5.1/84.8 (smallest function — 18 lines)
- FUN_006A5DF0 (client request handler): 0.0/83.1
- FUN_006A5860 (file transfer processor): 0.0/80.5 (largest — 317 lines)
- FUN_006A1B10 (checksum complete handler): 0.0/81.9
- FUN_006A3EA0 (file receive): 0.0/80.5
- FUN_006A4250 (0x27 wrapper): 13.1/100 (correctly classified wrapper)

All "effective_score" < 50, but all behaviors are tractable from decompile output — the scores reflect un-annotated state, not unverifiability.

## Lessons for next dig

1. **`char**` globals read as garbage statically** but the function code reveals they're string pointers populated at runtime. The C-code idiom `pcVar5 = PTR_DAT_xxx; while (uVar4--, *pcVar5++ != 0)` confirms it's a char*-deref-and-strlen pattern.
2. **Dispatcher switch defaults are evidence of dead opcodes**. FUN_006A3CD0's switch has no case 0x24, 0x26, 0x28 → these are not received. (0x28 IS sent but never received as a dispatched message — it triggers the event chain in the SENDER's flow.)
3. **Event xrefs come in pairs**: 1 producer + 1 registration (FUN_0069E590). When you see exactly 2 DATA xrefs to an event constant, you've found the canonical producer.
4. **Inverted opcode/dialog mappings are an easy mistake to make** during initial RE — the reverse mapping (0x22→x means 0x22 produces dialog X) IS the truth, but if you sample a wrong path (look at the sender's intent rather than the receiver's behavior), you can pin the dialog to the wrong opcode. C1 here was probably this kind of error in the original RE.
5. **packet-trace evidence (openbc-test sessions) is authoritative for behaviors that have multiple emission paths** — the binary's static call graph alone underestimates the protocol surface. The 0xFF round is real in the wire even though FUN_006A3820 doesn't emit it.

[[engine-snapshot-20260528]] is the campaign ground truth; [[protocol-snapshot-20260528]] is the protocol-family inventory; [[wire-format-spec-validation-20260528]] is the hub doc this complements.
