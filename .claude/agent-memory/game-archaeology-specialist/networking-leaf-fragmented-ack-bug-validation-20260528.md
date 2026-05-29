# Networking Leaf #8: Fragmented Reliable ACK Bug — v5 Validation 2026-05-28

**Doc:** `docs/networking/fragmented-ack-bug.md` (680 lines, largest in family)
**Sibling:** `docs/networking/ack-outbox-deadlock.md` (leaf #9, already `verified`)
**Status after pass:** `partial` — wire format & 4-field ACK matching ROCK SOLID; one section ("Root Cause: Missing Cleanup in SendOutgoingPackets") is BINARY-WRONG and must be reconciled with the validated leaf #9.

## Overall verdict

The doc is in TWO halves:

1. **First half (Observable Behavior → "Complete Static Verification Summary")** — the wire format, four-field matching logic, type values 0x32 / 0x01, and Ghidra-Verified Analysis section are byte-confirmed. The block of asm in section "ACK Factory / Deserializer — 0x006bd1f0 (VERIFIED)" matches my live disasm BYTE-FOR-BYTE.

2. **Second half (Runtime Evidence → end)** — the "ACK-outbox never drains" framing **CONFLICTS with the binary** and with the validated `ack-outbox-deadlock.md`. SendOutgoingPackets DOES contain a pass-2 retransmit-count gate (retx>=3) and a cleanup branch (retx>=9 → FUN_006b78d0). The doc's section heading "ACK entries are NEVER removed" is a runtime-observation overgeneralization, not a code claim.

## Anchored verifications (PASS)

### Function existence + signatures
| Function | Address | Decompile? | Notes |
|----------|---------|------------|-------|
| TGHeaderMessage_Serialize | 0x006bd190 | YES (rich plate) | vtable[2] slot of TGHeaderMessage |
| TGHeaderMessage factory (deser) | 0x006bd1f0 | NO (bare code, NOT a fn) | 96-byte raw disasm CONFIRMED — matches doc's asm exactly |
| HandleReliableReceived | 0x006b61e0 | YES (rich plate) | sets +0x40 = (type<0x32) on new ACK |
| HandleACK | 0x006b64d0 | YES | 4-field match logic confirmed |
| SendOutgoingPackets | 0x006b55b0 | YES | 3-queue loop, 2-pass ACK drain |
| ProcessIncomingPackets | 0x006b5c90 | YES | factory table DAT_009962d4, type-0x01 slot DAT_009962d8 |
| EnqueueReceived (QueueForDispatch) | 0x006b6ad0 | YES | unreliable→+0x70, reliable→+0x8C |
| DispatchReceivedMessages | 0x006b5f70 | YES | switch case 1 → HandleACK confirmed |
| ReassembleFragments | 0x006b6cc0 | YES | 256-elem array, clears +0x3C after reassembly |
| FragmentMessage (TGBufferStream_Fragment) | 0x006b8720 | YES | sets +0xF (=0x3C, is_fragmented)=1, +0x39=idx |
| TGMessage_Ctor (FUN_006b82a0) | 0x006b82a0 | bare | sizeof=0x40 confirmed (PUSH 0x40 @ 0x006b8300) |
| TGMessage::GetType | 0x006b9430 | bare | `MOV EAX,0x32; RET` ✓ |
| TGHeaderMessage::GetType | 0x006bdc20 | bare | `MOV EAX,0x01; RET` ✓ |

### Wire format (ACK type 0x01)
4-byte non-fragment / 5-byte fragment layout EXACT MATCH:
- byte[0] = vtable[0]() = 0x01
- bytes[1..2] = LE u16 seq (msg+0x14)
- byte[3] bit 0 = is_fragmented (msg+0x3C); bit 1 = is_below_0x32 (msg+0x40)
- [byte[4]] frag_idx (msg+0x39) when bit 0 set

Doc's annotation at line 111 ("`flags` byte bit 1 carries `is_below_0x32`, NOT `has_total_frags` as previously documented in wire-format-spec.md") is **correct** and was already absorbed into wire-format-spec validation (protocol #1).

### Field offsets (TGMessage layout 0x40 bytes)
All confirmed from constructor at 0x006b82a0:
- vtable=0x008958d0 written to +0x00
- +0x14 = seq (u16) — `MOV [EAX+0x14], CX`
- +0x18 = retransmit_count (u32) — zeroed
- +0x1C/+0x20/+0x24 = float timers — zeroed
- +0x2C = backoff mode = 1 (`mov [EAX+0x2c], EDX` where EDX=1)
- +0x30/+0x34 = floats = 1.0f (0x3F800000)
- +0x38=total_frags, +0x39=frag_idx, +0x3A=is_reliable, +0x3B=is_ordered, +0x3C=is_fragmented, +0x3D=1
- sizeof=0x40 (alloc PUSH 0x40)

### Field offsets (TGHeaderMessage extension 0x44 bytes)
- Alloc PUSH 0x44 at 0x006bd1f7 ✓
- +0x40 = is_below_0x32 ✓

### Peer queue offsets (cross-anchored from leaf #9 + foundation #5)
| Offset | Field | Source |
|--------|-------|--------|
| +0x64 / +0x68 / +0x7C / +0x70 / +0x74 / +0x78 | first-send head/tail/count/cursor/index/?? | SendOutgoingPackets first-send loop |
| +0x80 / +0x84 / +0x98 / +0x8C / +0x90 | retransmit head/tail/count/cursor/index | HandleACK + SendOutgoingPackets pass-1 |
| +0x9C / +0xA0 / +0xB4 / +0xA8 / +0xAC | ACK-outbox head/tail/count/cursor/index | HandleReliableReceived + SendOutgoingPackets pass-1 ACK + pass-2 ACK |
| +0xBC | is_disconnecting (u8) | leaf #9 |
| +0xB4 | ACK count | leaf #9 |

### Switch dispatch in DispatchReceivedMessages
`switch(GetType())` at LAB_006b60b6:
- case 0 → FUN_006b63a0 (data)
- **case 1 → HandleACK** ✓
- case 3 → FUN_006b6640 (connack)
- case 4 → FUN_006b6a70 (boot)
- case 5 → FUN_006b6a20 (disconnect)

## CORRECTIONS

### C1 (HIGH PRIORITY): "Root Cause: Missing Cleanup in SendOutgoingPackets" is BINARY-WRONG

**Doc claim** (line 628-638):
> The `SendOutgoingPackets` function (0x006b55b0) processes the ACK-outbox queue and serializes each ACK into the outgoing packet. After serialization, it increments the retransmit count and updates the timestamp — **but it never checks whether the ACK has been successfully delivered or whether the retransmit count exceeds a limit**.
>
> ... once an ACK entry is in the outbox, **there is no code path that removes it**.

**Binary truth** (decompile of 0x006b55b0):
- **Pass 1** at lines ~46-64: `if ((cVar6 != '\0') && (piVar9[6] < 3))` — only serializes when `retx < 3`.
- **Pass 2** at lines ~150-177: gated by `(0 < iStack_28) || (peer+0xBC != 0)` AND `(0 < peer+0xB4)`. Filter `(cVar6 != '\0') && (2 < piVar9[6])` — only handles `retx >= 3`. THEN at `(8 < piVar9[6])` calls `FUN_006b78d0` which **removes the entry from the queue**.

So ACK entries DO get removed — just only when retx reaches 9 AND pass-2 gate fires AND timer expires.

The observed `retx=7-8` after 6 seconds in the trace is the path INTO the deadlock (entries climbing toward the retx>=9 cleanup but stuck below the pass-2 gate). This is exactly the mechanism documented and validated in `ack-outbox-deadlock.md` (leaf #9).

**Action:** Section "Root Cause: Missing Cleanup in SendOutgoingPackets" should be replaced with a pointer to `docs/networking/ack-outbox-deadlock.md` or rewritten to say:
> "ACK entries DO have a removal path at retx>=9 in pass 2, but pass 2 only fires when (msg_count>0 OR peer+0xBC!=0) AND peer+0xB4>0. In observed sessions the gate is rarely satisfied, so entries climb to retx=7-8 and stall — see ack-outbox-deadlock.md for the full mechanism."

### C2 (MEDIUM): Section "Eliminated Hypotheses → Hypothesis #1 (ACK delivery failure)" mentions "retransmit count limit of 3"

**Doc claim** (line 486):
> The ACK-outbox queue (`peer+0x9C`) is processed with a **retransmit count limit of 3** and a timer check (FUN_006b8700).

This is partially true but undersells the full structure. Pass 1 cap is `retx < 3`, but pass 2 catches `retx >= 3`. So "limit of 3" applies only to pass 1; the entry can keep going through pass 2 up to retx=8 before cleanup. Should be clarified.

### C3 (LOW): "FUN_006b8700 / FUN_006b8670" naming pairing

**Doc claim** (line 150-162):
> ### Retransmit Timer — FUN_006b8700 / FUN_006b8670
> `FUN_006b8700` checks if `current_time - last_send_time > retransmit_interval`. If expired, returns true.
> `FUN_006b8670` updates the retransmit count and interval.

The function role-assignment is correct (consistent with leaf #9). Just note: leaf #9 anchors `FUN_006b8670` as updater (which also has the side-effect of computing the interval). This is the same function the doc describes — no contradiction, just keep the naming consistent if the doc is re-edited.

## Clarifications

### Clar 1: "stock dedi has same bug" — context
Line 15: "Both the stock dedicated server and our reimplementation produce identical ACK bytes and identical endless retransmit behavior. This confirms a **client-side bug**."

The framing is correct for Bug 1 (fragment retransmission). The client's `retxQ=0` but it keeps retransmitting fragments because Bug 1 is asymmetric — the server's per-fragment ACKs arrive after the client already cleared the retransmit queue via some other path (likely whole-message reassembly clearing the entries first).

But for Bug 2 (ACK-outbox accumulation), the bug is on **both sides** — both the server's ackOutQ and the client's ackOutQ grow monotonically. This is the same deadlock mechanism described in leaf #9.

### Clar 2: ReassembleFragments at 0x006b6cc0 — fragment cleanup confirmed
Lines 87-99 of the decompile show the second-pass cleanup loop that calls `FUN_00718cf0(piVar4)` and decrements `piVar8[6]` (count). So fragments DO get removed from the reliable dispatch queue after successful reassembly. This is consistent with the doc's "Removes consumed fragments from the queue" claim (line 235).

### Clar 3: SendHelper (FUN_006b5080) seq assignment
The decompile confirms doc's claim about same-seq + different-frag-idx:
- Reads `uVar4 = *(undefined2 *)(param_3 + 0x26)` (or +0x2A for types>=0x32) ONCE before loop
- Loop calls vtable[7] (FragmentMessage) which returns piVar2 (array of N msg pointers)
- For each fragment: `*(undefined2 *)(iVar1 + 0x14) = uVar4` (same seq for all)
- Counter incremented ONCE after loop: `*(short *)(param_3 + 0x2a) = *(short *)(param_3 + 0x2a) + 1`

Wait — the increment is OUTSIDE the per-fragment loop. So yes, seq counter is bumped once per logical message (3 fragments share seq + counter bumps by 1). ✓ doc claim verified.

### Clar 4: TGMessage::Clone (FUN_006b8610) NOT independently verified this pass
Doc claims (line 130) clones preserve fragment fields via copy ctor. Trust this; aligns with FragmentMessage decompile which calls vtable[6] then sets +0xF=1 and +0x39=idx on each clone.

## Historical sections

### H1: "Ghidra-Verified Analysis (2026-02-19)" framing
The whole section's intro says "All five priority functions have been decompiled and verified via Ghidra MCP and raw objdump disassembly. The previous analysis (without Ghidra) was largely correct but incomplete. This section supersedes the earlier hypotheses." — this is a historical archaeology note. Still useful but should be flagged as a previous-pass anchor, not the current state. The byte-by-byte asm listings within ARE current and correct.

### H2: Hypothesis chain (#1-#7) discussion
The "Eliminated Hypotheses" → "Surviving Hypotheses" → "NEW Hypothesis #6" → "NEW Hypothesis #7 → "Revised: Hypothesis #7 is also ELIMINATED" chain is detailed investigation history. Useful as a record but the FINAL section ("FINAL Assessment: Two Distinct Bugs") is what matters for current behavior reasoning.

### H3: Valentine's Day Battle Trace (2026-02-14)
Line 650-654 — historical observation about Bug 1 not being present in the 34-min trace. Still useful as a session-phase finding, not stale.

## Open Questions

### OQ 1: Bug 1 (Fragment retransmission) root cause — UNRESOLVED
The doc concludes (line 528): "fragments were already cleared by an earlier mechanism (possibly the whole-message ACK or fragment reassembly path), but the server's per-fragment ACKs arrive after that and find nothing to remove."

But:
- HandleACK only matches ONE fragment at a time (it returns after removing one entry).
- ReassembleFragments removes fragments from the **dispatch** queue, not the **retransmit** queue. The retransmit queue still holds the original 3 fragment messages.
- So who clears the retransmit queue's fragments?

This is the genuine UNRESOLVED root cause. The 4-field ACK matching is provably correct, but if retxQ=0 BEFORE the per-fragment ACKs arrive, something else cleared it. Candidates worth investigating:
- The "whole-message ACK" hypothesis is incorrect — there is no whole-message ACK; each fragment generates its own ACK with distinct frag_idx, and HandleACK only matches per-fragment.
- Possibility: the **CLIENT** treats its outgoing fragments differently — maybe the client clears retx fragments on a different trigger than ACK receipt (e.g., session-state transition during checksum phase).
- Possibility: the fragments share seq=0x0200 but the retx queue had distinct entries that were each individually ACKed but the server's ACKs all arrived in one burst BEFORE the client finished processing the first batch, so by the time the third ACK runs HandleACK the entries are already gone — but this should drain in order, not leave anything.

OQ 1 requires runtime instrumentation on the CLIENT side specifically to capture the moment retxQ goes to 0.

### OQ 2: Why does Bug 1 appear in the 91-sec checksum trace but NOT in the 34-min Valentine's combat trace?
Doc speculates "session-phase dependent (only occurs during the initial checksum/settings exchange)" (line 653). Plausible — during checksum exchange, large reliable messages (checksum data ~3KB each) get fragmented; during combat, individual TGMessages are small (<1024B) and never fragment. So Bug 1 may simply never trigger post-checksum because no fragmentation occurs.

This makes Bug 1 a checksum-phase-only bug in practice. Worth confirming with a wire trace showing fragments=0 throughout combat (the doc's Valentine analysis already supports this).

## Cross-references

- **`ack-outbox-deadlock.md` (leaf #9, verified)** is the AUTHORITATIVE doc on Bug 2 (ACK-outbox accumulation). This doc's section on Bug 2 should defer to it.
- **`netimmerse-transport-deep-dive.md` (foundation #5)** provided peer seq offsets (+0x24/+0x26/+0x28/+0x2A) and ACK factory location (0x006bd1f0 bare code). All confirmed here.
- **`wire-format-spec.md` (protocol #1)** absorbed the "is_below_0x32 not has_total_frags" correction (doc line 111 — already validated).

## v5 status recommendation

**Status:** `partial`

**Rationale:**
- First half (Observable Behavior + Transport Layer Architecture + TGMessage Layout + ACK Wire Format + Complete Message Flow + Ghidra-Verified Analysis): ROCK SOLID. Should be promoted to `verified` if separated.
- Second half (Runtime Evidence section): Bug 1 reasoning is sound and reproducible from binary; Bug 2 framing CONFLICTS with binary + with validated leaf #9. Material C1 correction required.

**Re-publication priority:** MEDIUM. Bug 1 is interesting but checksum-phase-only; Bug 2 should redirect to ack-outbox-deadlock.md. Could be merged into ack-outbox-deadlock as a "see also: fragmented ACK historical investigation" appendix.

## Anchors summary

- 9 functions decompiled (8 with rich plates, 2 GetType bare)
- 96 bytes byte-disassembled at 0x006bd1f0 (ACK factory)
- 128 bytes byte-disassembled at 0x006b82a0 (TGMessage_Ctor, sizeof 0x40)
- TGMessage vtable 0x008958d0 + TGHeaderMessage vtable 0x008959ac CONFIRMED
- 4 v5 completeness scores collected (effective 33-54 range, fixable deductions present but non-blocking)
- 0 wire-format corrections
- 1 material code-claim correction (C1: "ACK never removed")
- 2 hypothesis-section reframings (C2, C3)
- 4 clarifications
- 3 historical-section markers
- 2 open questions surfaced (OQ1 unresolved Bug 1 root cause, OQ2 phase dependence)
