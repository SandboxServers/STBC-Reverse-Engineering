---
name: struct-skeletons-20260528
description: v5 struct skeletons created in Ghidra DB for MultiplayerGame (0x200), TGMessage (0x2C), TGBufferStream (0x2C), PlayerSlot (0x18). Dispatcher 0x0069F2A0 score 69.94 -> 79.0.
metadata:
  type: project
---

# Struct Skeletons — 2026-05-28

Created four evidence-anchored struct skeletons in STBC.exe Ghidra DB after MpgameHandleMessage dispatcher recovery. Dispatcher's effective completeness score lifted from **69.94 -> 79.0** (+9.06 points). Remaining gap to ceiling (94.43) is global-typing work, not structural.

## Struct: PlayerSlot (size 0x18)

Sub-element of MultiplayerGame's `aPlayerSlots[16]`. 16 entries x 0x18 = 0x180 bytes (0x78 -> 0x1F7 in parent).

| Offset | Size | Hungarian | Type | Evidence |
|--------|------|-----------|------|----------|
| 0x00 | 1 | bActive | byte | 0x006a0a4f `(char)piVar4[-1] != '\0'` |
| 0x04 | 4 | dwPlayerId | uint | 0x006a0a55 `*piVar4 == *(param_2+0x28)` |
| 0x08 | 4 | dwShipObjId | uint | 0x0069f6e2 `piVar5[1] == *(param_1+0x80)` (slot[0]+0x08) |
| 0x0C | 4 | dwEvent | uint | 0x0069f66b `param_1 + 0x84 + ...*0x18` (slot+0x0C) |
| 0x10 | 1 | bSlotByte | byte | 0x006a1ed4 `*(param_1 + 0x88 + iVar5*0x18)` |

Pad bytes inserted for 1->4 boundary alignment and 0x11..0x17 tail.

## Struct: TGBufferStream (size 0x2C)

The dispatcher's "stream" object — what `pMsg->pStreamBuffer` points to. The dispatcher dereferences it as an object with vtable.

| Offset | Size | Hungarian | Type | Evidence |
|--------|------|-----------|------|----------|
| 0x00 | 4 | pVtable | void* | 0x0069f2cc `CALL [EDX]` virtual GetType (returns 0x32) |
| 0x04 | 4 | pBuffer | byte* | 0x006b8538 `return *(param_1+4)` (GetReadPointer) |
| 0x08 | 4 | dwBufferLen | uint | 0x006b8533 `*param_2 = *(param_1+8)` |
| 0x0C | 4 | dwSenderPlayerId | uint | 0x006a01b5 `*(param_1+0xc)` (HostMsg); 0x006a1eba `MOV EBX, [ESI+0xc]` (NewPlayerInGame); 0x006a2486 (CollisionEffect) |
| 0x28 | 4 | dwTargetPlayerId | uint | 0x006a0a55 `*piVar9 == *(param_2+0x28)` (NewPlayerHandler comparing slot ID to stream's target) |

Pad `abPad10[24]` between dwSenderPlayerId and dwTargetPlayerId — those bytes have observed accesses but no decoded semantics yet. Open question: is +0x28 actually a "second player" or could it be e.g. an object/ship ID? Several producer sites write a uint there.

## Struct: TGMessage (size 0x2C)

The dispatcher's stack-arg type — outer message envelope.

| Offset | Size | Hungarian | Type | Evidence |
|--------|------|-----------|------|----------|
| 0x00 | 4 | pVtable | void* | 0x0069f2ca dispatcher takes [pMsg] = vtable but the actual virtual call is on pStreamBuffer's vtable. pMsg's vtable still exists from other code paths. |
| 0x28 | 4 | pStreamBuffer | TGBufferStream* | 0x0069f2c5 `MOV ESI, [EAX+0x28]` (dispatcher) |

Pad `abPad04[36]` between vtable and pStreamBuffer — intentionally empty. The 4 known TGMessage subclasses (TGObjPtrEvent factory 0x010C, TGCharEvent, TGEvent, TGBootPlayerMessage) likely populate these slots but per-subclass; the base layout we can confidently anchor is just the two fields above.

Open question: are sender/event-type fields part of TGMessage base, or do they belong to one specific subclass used in dispatch? FUN_006bb840 sets fields up to +0x28, FUN_006b82a0 sets fields up to +0x40. Different subclasses, different fields.

## Struct: MultiplayerGame (size 0x200)

Confirmed by allocation site 0x00504F4F: `FUN_00717b70(0x200)` immediately before ctor 0x0069E590.

| Offset | Size | Hungarian | Type | Evidence |
|--------|------|-----------|------|----------|
| 0x00 | 4 | pVtable | void* | 0x00405c13 ctor sets &PTR_FUN_008887e8; 0x00405ee6 dtor sets same |
| 0x04 | 52 | abPad04 | byte[52] | Unrecovered region (settings, base-class state, etc.) |
| 0x38 | 24 | adwInit38 | uint[6] | Zeroed by FUN_00405ad0 (offsets 0x38,0x3C,0x40,0x44,0x48,0x4C) |
| 0x50 | 4 | pAllocBlock | void* | 0x00405f00 `FUN_00718cf0(param_1[0x14])` in dtor (free call) |
| 0x54 | 4 | dwField54 | uint | Part of FUN_00405ad0's zero'd range (zero'd, role unknown) |
| 0x58 | 4 | pUiHandler | void* | 0x00405eed dtor calls `*pUi->vtable[0](1)` — Release call |
| 0x5C | 4 | dwSessionCookie | uint | 0x00405f57 used with FUN_00429960 (session lookup) |
| 0x60 | 3 | abFlagsPad60 | byte[3] | Zeroed bytes at 0x60, 0x61, 0x62 by FUN_00405ad0 |
| 0x63 | 1 | bPad63 | byte | Adjacent unverified byte |
| 0x64 | 12 | adwInit64 | uint[3] | Zeroed ints at 0x64, 0x68, 0x6C by FUN_00405ad0 |
| 0x70 | 4 | pNetwork | void* | 0x0069f2a3 dispatcher entry NULL check (most-cited field) |
| 0x74 | 4 | dwSlotArrayHdr | uint | 0x0069e5b9 container header for slot collection (FUN_00859d64) |
| 0x78 | 384 | aPlayerSlots | PlayerSlot[16] | 0x0069e5b9 `FUN_00859d64(param_1+0x1d, 0x18, 0x10, ...)` — elem_size=0x18, count=16 |
| 0x1F8 | 1 | bGameInProgress | byte | 0x006a0a51 `if (*(char *)(param_1 + 0x1f8) == '\0')` |
| 0x1F9 | 3 | abPad1F9 | byte[3] | Alignment padding |
| 0x1FC | 4 | dwMaxPlayers | uint | 0x00504F77 stores param_3 (clamped to 0x10); 0x006a0ae1 read |

## Dispatcher Score Before/After

| Metric | Before | After |
|--------|--------|-------|
| Effective score | 69.94 | 79.0 |
| Max achievable (ceiling) | 94.43 | 94.43 |
| Fixable deductions | 30.06 | 21.0 |
| Structural deductions | 5.57 | 5.57 |
| type_quality issues | 2 (count) | 1 (count) |

Remaining 21 fixable points are all global-typing (10 untyped_global x 0.8 + 1 generic_global_name x 5 + 11 missing_global_plate_comment x ~0.27 + 5 type_quality void* this) — out of scope for the struct campaign.

## Sample Handler Deltas (with typed `this` and `pStream`)

| Handler | Before effective | After effective | Delta |
|---------|------------------|-----------------|-------|
| HostMsgHandler 0x006a01b0 | 8.84 | 38.97 | **+30.13** |
| CollisionEffectHandler 0x006a2470 | 0.0 | 2.99 | +2.99 |
| NewPlayerInGameHandler 0x006a1e70 | 0.0 | 0.0 | 0 (still no plate; struct typing alone insufficient when plate+rename absent) |

HostMsgHandler illustrates the upper bound of "typed prototype only" gain — small functions with few unresolved fields go from ~9 to ~39 just by typing the params. Larger handlers need plate comments + magic-number docs + local renames to break above 0.

## Field-Size Uncertainties to Revisit

1. **TGBufferStream +0x10..+0x27 (24 bytes)** — at least one of these bytes is the bit-cursor state (per `docs/protocol/stream-primitives.md`), and one is likely a read-position cursor. The local 48-byte BitStreamReader at FUN_006cefe0 wraps TGBufferStream and tracks its OWN cursor, suggesting TGBufferStream doesn't internalize bit-level state.
2. **TGMessage +0x04..+0x27 (36 bytes)** — completely unknown. The dispatcher reads only +0x00 and +0x28. Producer paths in handlers write +0x10, +0x14, +0x28, +0x39..+0x3D, +0x40, but only after `new TGMessageSubclass` calls (FUN_006bb840, FUN_006b82a0) — those are SUBCLASS-specific.
3. **MultiplayerGame +0x04..+0x37 (52 bytes)** — base class state. Likely contains a TGUtopiaModule-derived base + RTTI/SmartPointer slots.
4. **MultiplayerGame +0x38..+0x4F** — 6 ints zeroed by ctor; roles unknown. Could be game-settings (gameTime, mapID, etc.) hinted at by CLAUDE.md "Settings packet".
5. **PlayerSlot +0x11..+0x17 (7 bytes)** — only +0x10 byte was anchored. Slot stride is 0x18; the rest is unknown.

## Key Patterns Learned

1. **MultiplayerGame allocation is explicit**: `FUN_00717b70(0x200)` at 0x00504F4F is the `operator new` call. Any class with this pattern (alloc-size constant before ctor call) gives you struct size for free.
2. **Player slot iteration uses pointer-step-6** (4-byte pointer-arithmetic with stride 6 ints = 0x18). Look for `piVar = piVar + 6; iVar++; while (iVar < 0x10)` to recognize player-slot scans.
3. **Handler `this` is MultiplayerGame, stack arg is pStream**. Dispatcher pattern: `MOV ECX, EDI (this); PUSH ESI (pStream); CALL handler`. Confirmed across all 17 jump-table entries.
4. **The struct rename API is fragile** — when you replace a typed local, Ghidra creates a phantom that the completeness checker counts as an undefined. Workaround: don't reuse the old name; use a new name (`pInnerStream` not `pStream`).
5. **Struct field renames silently revert** for array/pointer fields without `p`/`ab`/etc. prefixes. Ghidra auto-prefixes them. Work with the prefixes rather than against.

## Cross-References

- [[dispatcher-recovery-20260528]] — the dispatcher recovery that motivated these structs
- [[engine-snapshot-20260528]] — naming coverage baseline; struct work raises a different metric (type quality), not naming coverage
