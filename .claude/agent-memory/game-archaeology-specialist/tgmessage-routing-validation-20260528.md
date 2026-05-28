---
name: tgmessage-routing-validation-20260528
description: Protocol doc #7 validation. Routing model is per-handler not transport-level; "NoMe" is C++-created; FUN_006b63a0 is connect handler not game-data relay; FUN_006bb9d0 resolves peer by +0x1C key. Three routing mechanisms confirmed.
metadata:
  type: project
---

# tgmessage-routing.md v5 validation (2026-05-28)

Protocol family doc #7 of campaign. Validated against STBC.exe with cross-source data from `.claude/agent-memory/network-protocol-analyst/relay-audit-20260224.md` (21-min stock dedi session).

## Routing model — the THREE mechanisms

1. **C++ per-handler relay via "Forward" group** (game opcodes 0x07-0x12, 0x19, 0x1B)
   - Handler functions (FUN_0069fda0, FUN_0069f930, etc.) explicitly:
     - Clone msg via vtable[6]
     - Look up "Forward" group at network+0xF4 via FUN_006a2fc0(s_Forward_008d94a0)
     - Call TGWinsockNetwork_SendToGroup_Iterate(group, cloned_msg)
   - This is NOT automatic transport-level relay — each handler chooses to relay.

2. **Python explicit relay via "NoMe" group** (opcodes ≥ 0x2C)
   - Python scripts (MultiplayerMenus.py line 2273-2279) call SendTGMessageToGroup("NoMe", msg)
   - For chat, mission messages, score, etc.

3. **Connect-event broadcast via FUN_006b51e0** (TGConnectMessage / TGDisconnectMessage ONLY)
   - Called from FUN_006b63a0 (connect handler) and FUN_006b6a20 (disconnect)
   - Gated by `this+0x10E` (host flag)
   - Used so OTHER clients learn about join/leave
   - NOT a game-data relay — only transport-layer connection events

## Critical corrections from prior doc

| Old claim | New truth |
|-----------|-----------|
| FUN_006b63a0 is "type-0x00 host auto-relay" | It's the CONNECT-EVENT handler (parses peer ID, registers via FUN_006b7410, raises event 0x60007). FUN_006b51e0 call inside is connect-event broadcast, not game-data. |
| "NoMe" created by Python | Created by `MultiplayerGame_Ctor` at 0x0069E590-0x0069EB66 (string ref at 0x0069E6FA + 0x0069E716). Python USES but does not create. Same for "Forward" group. |
| "Two relay mechanisms" | THREE: per-handler "Forward", Python "NoMe", connect-event broadcast. |
| `0x006b8530 = TGMessage::GetData` | Actually `TGBufferStream_GetBufferAndSize(this, sizeOut)`. Returns `*(void**)(this+4)` and writes size to *sizeOut. |

## SendTGMessage 3-mode router (0x006B4C10) — definitive

- **targetID == -1**: `LEA ECX, [ESI + 0x28]` then CALL FUN_006bb9d0(nOptional). FUN_006bb9d0 walks peer array at network+0x2C (count network+0x30) looking for `peer+0x1C == nOptional`. Returns peer or 0. If 0 → SendTGMessage returns 0xB.
- **targetID > 0**: Binary search peer array at network+0x2C count network+0x30, sorted by peer+0x18. Found → queue. Not found but targetID == network+0x20 (local) → FUN_006b7410 create local peer. Else → 0xB.
- **targetID == 0 (broadcast)**: Loop entire peer array, skip peer+0xBC==1 (disconnecting), clone via vtable[6] for all but last, last reuses caller's pMessage.

## Peer struct keys (from FUN_006b7410)

- peer+0x18 = persistent network ID (binary-search key for targetID>0)
- peer+0x1C = second ID (lookup key for FUN_006bb9d0, used by targetID==-1)
  - Hypothesis: per-connection token/session ID. Set from `FUN_006b7540` return in connect handler.
- peer+0xBC = disconnecting flag (1 = skip)
- peer+0x30 = last-send tick (DAT_0099c6bc)
- peer+0x14 = additional metadata (uVar5 in receive path)

## Jump table at 0x0069F534 — 41 entries verified

| Opcode | Handler addr | Wrapper at | Real handler | Relay? |
|--------|--------------|------------|--------------|--------|
| 0x02 ObjCreate | 0x69f31e | PUSH 0 → 0x69f620 | FUN_0069f620 | NO |
| 0x03 ObjCreateTeam | 0x69f334 | PUSH 1 → 0x69f620 | FUN_0069f620 | NO |
| 0x04, 0x05, 0x16, 0x20-0x28 | 0x69f525 | DEFAULT cleanup | — | — |
| 0x06 PythonEvent | 0x69f3f1 | → 0x69f880 | FUN_0069f880 | NO (LOCAL ONLY) |
| 0x07 StartFiring | 0x69f34a | PUSH 0x8000d7 → 0x69fda0 | FUN_0069fda0 | YES Forward |
| 0x08 StopFiring | 0x69f363 | PUSH 0x8000d9 → 0x69fda0 | FUN_0069fda0 | YES |
| 0x09 StopFiringAtTarget | 0x69f37c | PUSH 0x8000db → 0x69fda0 | FUN_0069fda0 | YES |
| 0x0A SubsysStatus | 0x69f395 | PUSH 0x80006c → 0x69fda0 | FUN_0069fda0 | YES |
| 0x0B AddToRepairList | 0x69f3ae | PUSH 0x8000df → 0x69fda0 | FUN_0069fda0 | YES |
| 0x0C ClientEvent | 0x69f3c7 | PUSH 0 → 0x69fda0 | FUN_0069fda0 | YES (preserve wire eventCode) |
| 0x0D PythonEvent2 | 0x69f3f1 | → 0x69f880 | FUN_0069f880 | NO (LOCAL ONLY — SAME handler as 0x06) |
| 0x0E StartCloak | 0x69f405 | PUSH 0x8000e3 → 0x69fda0 | FUN_0069fda0 | YES |
| 0x0F StopCloak | 0x69f41e | PUSH 0x8000e5 → 0x69fda0 | FUN_0069fda0 | YES |
| 0x10 StartWarp | 0x69f437 | PUSH 0x8000ed → 0x69fda0 | FUN_0069fda0 | YES |
| 0x11 RepairListPriority | 0x69f3c7 | PUSH 0 → 0x69fda0 | FUN_0069fda0 | YES (preserve wire eventCode) |
| 0x12 SetPhaserLevel | 0x69f3c7 | PUSH 0 → 0x69fda0 | FUN_0069fda0 | YES (preserve wire eventCode) |
| 0x13 HostMsg | 0x69f2f6 | → 0x6a01b0 | FUN_006a01b0 | NO (absorbs, self-destruct) |
| 0x14 DestroyObject | 0x69f47d | → 0x6a01e0 | FUN_006a01e0 | (verify) |
| 0x15 CollisionEffect | 0x69f491 | → 0x6a2470 | FUN_006a2470 | NO (per audit 2:0; verify in binary) |
| 0x17 DeletePlayerUI | 0x69f4a5 | → 0x6a1360 | FUN_006a1360 | NO (verify) |
| 0x18 DeletePlayerAnim | 0x69f4b9 | → 0x6a1420 | FUN_006a1420 | NO (verify) |
| 0x19 TorpedoFire | 0x69f4cd | → 0x69f930 | FUN_0069f930 | YES (Forward — confirmed by decompile) |
| 0x1A BeamFire | 0x69f4e1 | → 0x69fbb0 | FUN_0069fbb0 | (verify) |
| 0x1B TorpTypeChange | 0x69f450 | PUSH 0x8000fd → 0x69fda0 | FUN_0069fda0 | YES |
| 0x1C StateUpdate | 0x69f3dd | → 0x69ff50 | FUN_0069ff50 | YES (per audit 23994:45355 — server generates AND relays) |
| 0x1D ObjNotFound | 0x69f4f5 | → 0x6a0490 | FUN_006a0490 | (verify) |
| 0x1E RequestObj | 0x69f51d | → 0x6a02a0 | FUN_006a02a0 | (verify; note: this jumps directly to handler, no PUSH ESI/cleanup) |
| 0x1F EnterSet | 0x69f509 | → 0x6a05e0 | FUN_006a05e0 | (verify) |
| 0x29 Explosion | 0x69f469 | → 0x6a0080 | FUN_006a0080 | NO (server-generated only) |
| 0x2A NewPlayerInGame | 0x69f30a | → 0x6a1e70 | FUN_006a1e70 | NO (triggers join handshake) |

Shared epilogue `MOV byte ptr [0x0097FA8B],0x0; POP EDI; RET 0x4` at `0x0069F525` is the "default" branch — does no work, just clears re-entrancy flag.

## Transport factory table notes

- Table at 0x009962d4 is 256 entries × 4 bytes (BSS, zero-init at load)
- 7 slots populated at runtime by TGWinsockNetwork_Ctor (0x006B3A00) gated by DAT_00995e60==0 first-time flag
- Registration functions:
  - FUN_006b8290 → slot 0x32 (TGMessage / FUN_006b83f0)
  - FUN_006bc5a0 → slot 0x00 (TGDataMessage / FUN_006bc6a0)
  - FUN_006bd110 → slot 0x01 (TGHeaderMessage / FUN_006bd1f0)
  - FUN_006bdc30 → slot 0x02 (TGConnectMessage / FUN_006bdd10)
  - FUN_006bac60 → slot 0x04 (TGBootMessage / FUN_006badb0)
  - FUN_006be720 → slot 0x03 (TGConnectAckMessage / FUN_006be860)
  - FUN_006bf2d0 → slot 0x05 (TGDisconnectMessage / FUN_006bf410)
- SWIG wrapper at 0x005e4860 (format string "bO:TGNetwork_RegisterMessageType" at 0x00938724): performs `AND EAX, 0xFF` + `MOV [EAX*4 + 0x009962D4], EDX`. The `& 0xFF` IS the only bounds-check — natural byte wrap, not validation.

## Type-0x00 vs Type-0x32 factory differences

- **Type-0x00 (FUN_006BC6A0)**: 14-bit length mask `(uVar2 & 0x3FFF)`, NO fragment support
  - Header bits: bit 15 = reliable (→ obj+0x3A), bit 14 = ack-required (→ obj+0x3B)
  - Payload starts at byte 5 if header != 0, else byte 3
- **Type-0x32 (FUN_006B83F0)**: 13-bit length mask `(uVar2 & 0x1FFF)`, fragment bit at `(uVar2 & 0x2000)`
  - Header bits: bit 15 = reliable, bit 14 = ack-required, bit 13 = fragment
  - 2 fragment fields at obj+0x38 (sequence in chain), obj+0x39 (total fragments?)

## Open questions

1. peer+0x1C semantics — likely connection-token from FUN_006b7540 but needs trace verification.
2. Chat echo to sender (audit 5:10 for 0x2C): NoMe-only relay can't explain 1:2 ratio. Possibly self-echo via local Display call counted as receive, or undiscovered second relay path.
3. Round-0xFF subsystem checksum sender — checksum doc OQ, not resolved here.

## Cross-source confirmations from audit

All audit per-opcode relay observations align with binary handler decisions:
- 0x07 StartFiring 1:1 → FUN_0069fda0 PUSH 0x8000d7 RELAY-Forward ✓
- 0x0D PythonEvent2 1:0 → FUN_0069f880 LOCAL-ONLY ✓
- 0x13 HostMsg 1:0 → FUN_006a01b0 LOCAL (self-destruct trigger) ✓
- 0x19 TorpedoFire 1:1 → FUN_0069f930 RELAY-Forward ✓

Status: PARTIAL pending material corrections (host relay re-architect, NoMe creation, 3-mechanism explanation).
