---
name: python-messages-validation-20260528
description: Protocol doc #6 (python-messages.md) v5 validation. Cleanest pre-v5 protocol doc to date — only 1 material correction (WriteCString length-prefix width: uint32 LE not uint16 LE). Confirms MAX_MESSAGE_TYPES init byte-level + ET_NETWORK_MESSAGE_EVENT 0x60001 byte-level + TGMessage sizeof 0x40 + TGMessageEvent sizeof 0x2C. 6 renames + 5 prototypes + 6 plate comments applied.
metadata:
  type: project
---

# Python-Messages Validation — 2026-05-28

Phase-1-through-3 validation of `docs/protocol/python-messages.md`. Headline: this doc was overwhelmingly well-anchored before validation. Lowest-correction pass of the protocol family so far.

## What Got Confirmed (Byte-Level)

### MAX_MESSAGE_TYPES SWIG constant
- **0x00654f31**: `MOV dword ptr [0x0090b490], 0x2b` — exactly as doc says. Verified by raw bytes `c70590b490002b000000`.
- The SWIG `name`-slot for "MAX_MESSAGE_TYPES" lives at 0x00952cf8 and is written into the globaltable entry at +0xC bytes before (`MOV [0x0090b48c], 0x952cf8` at 0x00654f27).

### SWIG wrappers (none have function entries — Ghidra missed them)
| SWIG name | Wrapper addr | Format string addr | Format | Real fn called |
|-----------|--------------|--------------------|--------|----------------|
| TGNetwork_SendTGMessage | 0x005e3a70 | 0x0093846c | `OiO\|i:TGNetwork_SendTGMessage` | 0x006b4c10 |
| TGNetwork_SendTGMessageToGroup | 0x005e3b20 | 0x0093848c | `OOO:TGNetwork_SendTGMessageToGroup` | 0x006b4de0 (indirect via FUN_006bb840 / TGStringResolver chain) |
| TGMessage_Create | 0x005e13b0 | 0x00937c30 | `:TGMessage_Create` (no args) | 0x006b82a0 (after PUSH 0x40 alloc) — confirms sizeof 0x40 |
| TGMessage_SetGuaranteed | 0x005e19c0 | 0x00937d30 | `Oi:TGMessage_SetGuaranteed` | Inline SETNZ AL / MOV [ECX+0x3A], AL — confirms +0x3A field |

Pattern to find SWIG wrappers when Ghidra missed them: byte-pattern search for `PUSH <fmt_string_addr>` = `68 LL LL LL 00`. The wrapper is the function above it.

### ET_NETWORK_MESSAGE_EVENT (0x60001) confirmed at THREE sites
1. **MultiplayerGame_Ctor (0x0069e590)** registers `FUN_006db380(0x60001, ..., s_MultiplayerGame____ReceiveMessag_0095a218, 1, 1, ...)`.
2. **TGWinsockNetwork::Update at 0x006b4788** does `MOV EBP, 0x60001` — this is the event-type pushed into TGMessageEvent+0x10.
3. **TGMessageEvent alloc at 0x006b4794**: `PUSH 0x2C` confirms sizeof 0x2C exactly as doc says.

### Group names verified in-memory
- 0x008e5528 = "NoMe\0\0\0\0" (4-char string + padding) — All peers EXCEPT local player.
- 0x008d94a0 = "Forward\0" — Same membership; engine event forward path.
- Both built by MultiplayerGame_Ctor when DAT_0097fa8a (g_IsMultiplayer) AND DAT_0097fa78 (TGWinsockNetwork singleton) are non-zero. Each is 0x14-byte struct with vtable `PTR_FUN_00894684`, strcpy-style name copy, then FUN_006b70d0 (group register on TGNetwork's group table at network+0xF4).

### SetGuaranteed wire-pattern (0x005e1a18-0x005e1a21)
```
TEST ECX, ECX              ; param value (int)
MOV  ECX, [ESP+4]          ; TGMessage*
SETNZ AL                    ; AL = (param != 0) ? 1 : 0
MOV  byte [ECX+0x3A], AL   ; write boolean to +0x3A
```
This is the canonical "SETNZ-to-boolean-field" pattern; useful template for finding similar bool-setters elsewhere.

### SetDataFromStream call chain (0x006b8a00)
```
uVar1 = pStream->vtable[+0xF4]()   ; GetBuffer  -> [stream+0x1C]
uVar2 = pStream->vtable[+0xD8]()   ; GetPos     -> [stream+0x24]
FUN_006b84d0(uVar1, uVar2)         ; BufferCopy -> allocates and memcpys to TGMessage+0x04
```
Tail-call pattern. Total 4 instructions; matches doc exactly.

## The One Material Correction

**WriteCString writes uint32 LE length prefix, NOT uint16 LE.**

FUN_006cf460 (vtable slot +0x24 of TGBufferStream) decompiles as:
```c
for (i = 0; param_2[i] != 0; i++);
vtable[+0x6c](i);          // WriteLong (4 bytes), NOT WriteShort (+0x5C, 2 bytes)
vtable[+0x14](param_2, i); // WriteBytes
```
The doc's row `WriteCString | +0x24 (0x006cf460) | 2+N bytes | [uint16 LE strlen]` should be `4+N bytes | [uint32 LE strlen]`.

**Material impact**: stock BC's mod code never calls WriteCString — they explicitly write `WriteShort(len)` + `Write(buf, len)`. So this correction doesn't affect any stock-trace observation or the CHAT_MESSAGE byte-by-byte example. But mods that call WriteCString directly would emit a 4-byte length prefix; clean-room implementations need this right.

## Two Naming Clarifications

1. **TGMessage::WriteToBuffer vs TGMessage::Serialize.** The doc calls FUN_006b8340 "TGMessage::WriteToBuffer"; Ghidra names it `TGBufferStream_Serialize` (foundation-#2 legacy). Per the foundation #3 correction, the 0x40-byte class IS TGMessage. So FUN_006b8340 IS `TGMessage::Serialize` (vtable[2]). Behavior walkthrough in doc is correct; only the method name needs updating.

2. **ProcessIncomingMessages vs ProcessIncomingPackets.** Doc step 2: `ProcessIncomingMessages (FUN_006b5c90)`. Ghidra has it as `TGWinsockNetwork_ProcessIncomingPackets`. Rename in doc.

## Cross-Source Tags Required

The relay-audit-20260224 memory (Cady/XFS01 21-min trace) provides:
- 0x2C CHAT_MESSAGE: 1:2 echo (5 C->S, 10 S->C — relayed to ALL clients including sender)
- 0x36 SCORE_CHANGE: always paired (always sent to ALL clients simultaneously, 10 S->C)
- 0x37 SCORE_MESSAGE: 6 per-join roster updates (S->C only)

These corroborate the doc's routing claims but are NOT binary-derived. Tag with `[cross-source-2026-02-24 trace]` pointing to the relay-audit memory.

## What Got Annotated This Pass

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

## Completeness Scores Post-V5

| Addr | Score (pre) | Score (post) | Notes |
|------|-------------|--------------|-------|
| 0x006b4c10 SendTGMessage | 0.00 | 29.07 | renamed + prototype + plate; 8 magic#s + 1 unrenamed global + 2 unrenamed labels + 3 unresolved struct accesses remain |
| 0x006b4de0 SendTGMessageToGroup | 6.62 | 71.27 | renamed + prototype + plate; above 50 threshold |
| 0x006b8a00 SetDataFromStream | 11.93 | 78.27 | renamed + prototype + plate; structural ceiling reached |
| 0x0069e590 MultiplayerGame_Ctor | 0.00 | 5.39 | renamed + plate only; needs dedicated pass — 31 unrenamed globals + 99 magic numbers (mostly event-ID constants 0x008000xx) |

The MultiplayerGame_Ctor low score is structural — its body is a long list of event-handler registrations (`FUN_006db380(EVENT_ID, ..., s_HandlerName, 1, 1, ...)` × ~30). Each call has 6 args, 4 of which are unrenamed strings/labels. A dedicated MultiplayerGame ctor pass under the engine family is the right home for that lift.

## Open Questions

1. **TGMessageEvent vtable layout.** Only vtable[1] (release) verified. The other slots (Serialize, Clone, GetType, etc.) are untouched. Engine event-system-architecture.md scope.
2. **3 Python ProcessMessageHandler handlers** (MissionShared / MultiplayerMenus / mission-specific) live in `reference/scripts/*.py`. Out of scope for binary validation; documentation-writer should tag with `[python-source]`.
3. **0x35 name conflict.** relay-audit calls it "GameState"; doc says "MISSION_INIT_MESSAGE". Same byte; doc's Python-source name is canonical.
4. **SendTGMessage `targetID == -1` semantics.** Calls FUN_006bb9d0(optional_arg) to resolve a peer object. Exact meaning of optional_arg unclear — peer-handle ID? in-flight message slot? Deferred to tgmessage-routing.md validation.

## Patterns Learned

1. **Cleanest pre-v5 docs are the ones where the original author was reading the binary, not extrapolating.** python-messages.md cites specific addresses for every primitive + every wrapper + every constant. The handful of corrections needed are mechanical (length-prefix width; method names that drifted between the doc and Ghidra DB).

2. **SWIG wrappers are sometimes missing from Ghidra's function inventory.** All 4 wrappers I traced today (SendTGMessage / SendTGMessageToGroup / TGMessage_Create / SetGuaranteed) lack function entries — they appear only as bare disassembly. Find them by byte-pattern searching for `PUSH <format_string_addr>` instructions (`68 LL LL LL 00`). The function above the PUSH is the wrapper; the CALL to the real function is several lines later.

3. **The relay-audit-20260224 memory is the canonical cross-source for opcode routing semantics.** When validating any protocol doc that makes routing claims, check that memory first for the empirical 1:1 / 1:N / 1:2 ratios.

4. **MAX_MESSAGE_TYPES init pattern is byte-level distinctive.** The bytes `c705 <const_addr_LE> <value_LE>` = `MOV dword ptr [addr], value` is the SWIG-globaltable init style for integer constants. Useful for finding other SWIG constants whose addresses you know but whose init sites you don't.

5. **`PUSH 0x40` + `CALL <ctor_addr>` is the gold-standard class-identity / sizeof proof.** Same technique as foundation #2 used for TGBufferStream. Worked again here for TGMessage sizeof. Worked for TGMessageEvent (PUSH 0x2C). Use whenever you need to verify a class's sizeof.

## Cross-References

- [[engine-snapshot-20260528]] — predecessor snapshot; this memory consumes it.
- [[stream-primitives-validation-20260528]] — foundation #2; TGBufferStream class identity + primitives + WriteCString lookup confirmed here.
- [[transport-layer-validation-20260528]] — foundation #3; TGMessage sizeof 0x40 + vtable 0x008958d0 + ctor 0x006b82a0 confirmed here.
- [[game-opcodes-validation-20260528]] — mid #4; MpgameHandleMessage dispatcher boundary at 0x02-0x2A confirmed; python-messages.md complementarily owns 0x2C+.
- `.claude/agent-memory/network-protocol-analyst/relay-audit-20260224.md` — cross-source for 0x2C / 0x36 / 0x37 routing claims.
- docs/protocol/python-messages.md — doc being validated.
- docs/protocol/v5-validation-status.md §6.6 — tracker row.

## v5-Conformant Evidence Trail Summary

| Claim | Address | Function | Confidence |
|-------|---------|----------|-----------|
| MAX_MESSAGE_TYPES = 0x2B at 0x0090b490 init at 0x00654f31 | 0x00654f31 | (SWIG init in shared init region) | high — byte-level |
| SWIG SendTGMessage wrapper at 0x005e3a70 calls real fn at 0x006b4c10 | 0x005e3a70 | (no fn entry; bare disassembly) | high — format string + CALL |
| SWIG SendTGMessageToGroup wrapper at 0x005e3b20 | 0x005e3b20 | (no fn entry) | high — format string anchor |
| SWIG TGMessage_Create wrapper at 0x005e13b0 PUSH 0x40 | 0x005e13b0 | (no fn entry) | high — PUSH 0x40 + CALL ctor |
| SetGuaranteed writes byte to [TGMessage+0x3A] | 0x005e1a18 | (no fn entry) | high — SETNZ AL pattern |
| SetDataFromStream calls vtable+0xF4 + vtable+0xD8 + BufferCopy | 0x006b8a00 | TGMessage_SetDataFromStream | high |
| SendTGMessage targetID==0 broadcasts via peer-array loop at [this+0x2C] | 0x006b4c10 | TGWinsockNetwork_SendTGMessage | high |
| SendTGMessage targetID>0 binary-searches peer array | 0x006b4c10 | (same) | high |
| SendTGMessageToGroup binary-searches groups at [this+0xF4] | 0x006b4de0 | TGWinsockNetwork_SendTGMessageToGroup | high |
| Returns 0x10 on group not found | 0x006b4de0 | (same) | high |
| "NoMe" string at 0x008e5528 | 0x008e5528 | (data) | high — in-memory inspect |
| "Forward" string at 0x008d94a0 | 0x008d94a0 | (data) | high — in-memory inspect |
| Both groups built in MultiplayerGame_Ctor under IsMultiplayer + WSN-nonnull gate | 0x0069e590 | MultiplayerGame_Ctor | high |
| ET_NETWORK_MESSAGE_EVENT = 0x60001 | 0x0069e590, 0x006b4788 | both sites | high — byte-level |
| TGMessageEvent sizeof = 0x2C | 0x006b4794 | (PUSH 0x2C at alloc site) | high — byte-level |
| TGMessageEvent ctor installs PTR_FUN_0089580c | 0x006bfe80 | TGMessageEvent_Ctor | high |
| TGMessageEvent::AttachMessage stores at [this+0x28] | 0x006bff30 | TGMessageEvent_AttachMessage | high |
| MpgameHandleMessage dispatcher boundary: 0x02-0x2A only, no case for 0x2C+ | 0x0069f2a0 | MpgameHandleMessage | high — full switch decompile |
| WriteCString uses vtable+0x6c (WriteLong, 4 bytes), NOT vtable+0x5C (WriteShort, 2) | 0x006cf460 | FUN_006cf460 | high — CORRECTS doc |
| FUN_006b8340 IS TGMessage::Serialize (foundation-3 class identity) | 0x006b8340 | TGBufferStream_Serialize (Ghidra DB name; semantic = TGMessage::Serialize) | high |
| FUN_006b5c90 = TGWinsockNetwork_ProcessIncomingPackets (renamed from doc's name) | 0x006b5c90 | TGWinsockNetwork_ProcessIncomingPackets | high |
