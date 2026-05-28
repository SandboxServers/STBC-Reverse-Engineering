---
name: set-phaser-level-validation-20260528
description: Protocol doc #16 (LEAF). docs/protocol/set-phaser-level-protocol.md — Opcode 0x12 SetPhaserLevel byte-by-byte verified. ZERO wire-format corrections. Two non-wire corrections (TGSubsystemEvent cascade + registration string format). Sender/receiver/applier all byte-anchored.
metadata:
  type: project
---

# set-phaser-level-protocol.md — v5 Validation

## Status
verified pending hierarchy correction (cascade from [[tgobjptrevent-validation-20260528]] / [[pythonevent-wire-format-validation-20260528]])

## Foundation Cross-Anchor Hits
- TGCharEvent class layout (0x2C, +0x28 = char) per mid #13 — CONFIRMED via FUN_00574C20 ctor
- TGCharEvent IsA {0x105, 0x101, 0x02} per mid #13 — CONFIRMED at 0x00574C50 (`B8 05 01 / B8 01 01 / cmp 0x02`)
- 18-byte wire format per leaf #14 — CONFIRMED: opcode(1) + base TGEvent(16) + charValue(1)
- Generic event-forward FUN_0069FDA0 — CONFIRMED dispatcher slot for opcode 0x12 (jump table entry index 0x10 = 0x0069F3C7)
- Universal SWIG triple-string pattern — CONFIRMED at 0x008E54D0/DC/EC ("TGCharEvent" / "_p_TGCharEvent" / "TGCharEventPtr")
- "NoMe" group string at 0x008E5528 — CONFIRMED ("4E 6F 4D 65 00")
- Relay-audit 1:1 (5 C→S / 5 S→C) — CONFIRMED via relay-audit-20260224

## Byte-Verified Anchors
- **0x006A1970** MultiplayerGame::SetPhaserLevelHandler (CREATED — was undefined-in-DB; xref 0x0069F19D registers it). Bytes `8B 54 24 04 8B 42 0C 85 C0 74 14 8B 40 40 56 8B 71 54 3B C6 5E 75 08 6A 12 52 E8 31 FE FF FF C2 04 00` — full 34-byte body.
  - Gate: `event->source (+0x0C) != NULL && event->source->objectID (+0x40) == this->localPlayerObjID (+0x54)` → `PUSH 0x12; PUSH event; CALL SendEventMessage(0x006A17C0)`
- **0x00574180** PhaserSystem::SetPhaserLevelHandler (CREATED — was undefined; xref 0x00573E21). Bytes `8B 44 24 04 50 0F BE 50 28 89 91 F0 00 00 00 E8 4C 4F 16 00 C2 04 00` — 23 bytes total.
  - Reads sign-extended `event->charValue (+0x28)`, stores into `this+0xF0`, releases event via FUN_006D90E0.
- **0x00574200** PhaserSystem::SetPowerLevel (RENAMED).
  - `FUN_00717b70(0x2c)` + `FUN_00574c20` (ctor) → TGCharEvent
  - `*(char*)(event+0x28) = (char)param_2` — sets level byte
  - `FUN_006D62B0(this)` — sets source
  - `*(undefined**)(event+0x10) = &DAT_008000E0` — sets event type
  - `TGEventManager__PostEvent(event)`
  - Loops `this+0x1C` children, dynamic_casts via FUN_00570B20, calls vtable+0x90 with level
  - Stores `*(int*)(this+0xF0) = param_2`
- **0x00574C20** TGCharEvent::Ctor (RENAMED). Base TGEvent ctor + vtable=0x008932DC + `(byte)+0x28=0`.
- **0x00574C50** TGCharEvent::IsA (RENAMED). Returns true for {0x105, 0x101, 0x02}.
- **0x00574C40** TGCharEvent::GetFactoryID. `B8 05 01 00 00 C3` = MOV EAX, 0x105; RET. (Still FUN-named — vtable callback, not entered.)
- **0x00574C80** GetClassName → 0x008E54D0 ("TGCharEvent")
- **0x00574C90** GetSWIGName → 0x008E54DC ("_p_TGCharEvent")
- **0x00574CA0** GetPtrName → 0x008E54EC ("TGCharEventPtr")
- **0x006A17C0** MultiplayerGame::SendEventMessage (RENAMED). 1023-byte stack buffer, alloc TGMessage(0x40), reliable bit `msg[+0x3A]=1`, branch on DAT_0097fa8a (IsMultiplayer): SendToGroup("NoMe") vs SendTGMessage to host.
- **0x006D6940** TGCharEvent::WriteToStream (CREATED). Calls base FUN_006D6130 (16 bytes), then WriteByte via stream vtable+0x54 (1 byte). 32-byte body.
- **0x006D6960** TGCharEvent::ReadFromStream (CREATED). Calls base FUN_006D61C0, then `MOV [ESI+0x28], AL` (1 byte read). 31-byte body.
- **0x008932DC** TGCharEvent vtable — all 16 slots verified byte-by-byte against doc table.
- **0x0069F3C7** dispatcher case for opcode 0x12 — `PUSH 0; PUSH ESI; MOV ECX,EDI; CALL 0x0069FDA0` (no event-type override).
- **0x0069E9C3** MultiplayerGame_Ctor SetPhaserLevel registration — `PUSH 0x008000E0; CALL FUN_006DB380` with name @ 0x959F1C.
- **0x00573E40** PhaserSystem handler-table registration — `FUN_006D92B0(table, &DAT_008000E0, "PhaserSystem::SetPhaserLevelHandler" @ 0x008E5440)`.

## Corrections

### C1 — Hierarchy cascade (cosmetic, doc-level)
Doc lines 116-121 still depict the FABRICATED `TGSubsystemEvent (0x101)`. Per mid #13 + leaf #14 cascade: NO string "TGSubsystemEvent" exists in binary (confirmed 0 hits this session). 0x101 IS the TGEvent base factory ID itself. Replace with:
```
NiObject
  └── TGEvent (factory 0x101)
        ├── TGCharEvent (factory 0x105)
        └── TGObjPtrEvent (factory 0x10C)
```
The "factory 0x02 size 0x28" line is also wrong — TGEvent's factory ID is 0x101 (its IsA branch), not 0x02. 0x02 is TGObject's class ID (separate inheritance line). Doc's IsA chain at line 142-145 correctly lists `0x02` because TGCharEvent IS-A TGObject too (NiObject→TGObject→TGEvent). Flatten the hierarchy display and clarify TGObject is the 0x02 ancestor.

### C2 — Registration string formatting (minor)
Doc line 320: `"MultiplayerGame::__SetPhaserLevelHandler"` (double-underscore). Binary string @ 0x00959F1C is actually `"MultiplayerGame :: SetPhaserLevelHandler"` (colon-space, single, with spaces). Same applies to line 311: `"PhaserSystem::SetPhaserLevelHandler"` @ 0x008E5440 — that one is exact in binary (NO spaces, single colon-colon).
The Ghidra symbol display `s_MultiplayerGame____SetPhaserLeve_00959f1c` shows `____` as the encoded `" :: "` (Ghidra's space/colon mangling for label names).

### C3 — "FUN_006d6200 ReadObjectFromStream" naming
Doc lines 244, 343 reference `FUN_006d6200` as `ReadObjectFromStream`. Actual rename in Ghidra DB: `TGFactory_DeserializeObject`. Same function, different alias. Doc can use either — recommend matching DB name.

## Non-Corrections (already verified)
- 18-byte wire format — byte-by-byte CORRECT
- PP_LOW=0 / PP_MEDIUM=1 / PP_HIGH=2 mapping — three-value switch in SetPowerLevel proves three levels; SWIG strings exist for all three. Ordinal {LOW→0, HIGH→2} mapping is convention (matches FOSS convention "LOW < MEDIUM < HIGH").
- Vtable @ 0x008932DC — all 16 slots CORRECT
- WriteObjectRef 3-case (NULL/sentinel/valid) at 0x006D6130 — CORRECT (was leaf #14 finding for source field SOURCE is 2-case but doc shows 3-case here; FUN_006D6130 here is the BASE event WriteToStream, source+target encoding flows through there)
- Sender flow steps 1-8 — match SetPowerLevel disassembly
- Receiver flow steps 1-7 (FUN_0069FDA0) — match generic-event-forward decompile

## Cross-Source Anchors
- Relay-audit-20260224 (network-protocol-analyst memory): 0x12 = 5 C→S / 5 S→C / 1:1 / "To all OTHER clients" — CONFIRMS doc's "Bidirectional (any peer → all other peers, relayed by host)" classification
- App.py:6444-6446 (scripts repo): PP_LOW/MEDIUM/HIGH Python exports
- AI/Preprocessors.py:497-500: shows AI uses {PP_LOW, PP_HIGH} (skips PP_MEDIUM)

## Function Completeness Scores
- 0x00574200 PhaserSystem::SetPowerLevel: effective_score 1.23 → after rename+1 plate would be ~15 — undocumented
- 0x006A17C0 SendEventMessage: 0.0 → after rename ~15 — undocumented
- 0x0069FDA0 generic event-forward: 0.0 → flagged by foundation; doc references it but doesn't claim ownership

## Annotation Summary (this session)
- 4 functions CREATED (0x006A1970, 0x00574180, 0x006D6940, 0x006D6960)
- 4 functions RENAMED (0x00574200, 0x006A17C0, 0x00574C20, 0x00574C50)
- 4 plate comments added with `[v5-validated 2026-05-28]` tags

## Pattern
**SWIG vtable callbacks + handler-table registered functions are both undefined-in-DB.** Same as leaf #14 (PythonEvent), leaf #13 (TGObjPtrEvent), leaf #15 (CollisionEffect). The annotation script never registered these because they have ONLY DATA xrefs (vtable slot or registration table), no plain `CALL` instructions. Pattern: search `get_xrefs_to` on the doc-cited address; if result is `[DATA]` from a registration function, create the function manually using `mcp__ghidra__create_function` after byte-verifying a valid prologue.

## Open Questions
- Doc's frequency claim "~33 per 15-minute stock session" — relay-audit shows 10 events in 21min (5+5); doc's number may come from a different trace. LOW priority (frequency stats vary by session).
- Whether `event+0x18/0x1A/0x1C-0x24` field semantics (doc class layout lines 105-110) are byte-correct or speculative — these are TGEvent base layout fields, not modified by TGCharEvent.
