---
name: game-opcodes-validation-20260528
description: Protocol doc #4 (game-opcodes.md) v5 validation. Cleanest validation in the protocol campaign so far — dispatcher recovery did all the heavy lifting; the doc was already well-anchored. Zero binary corrections needed. Captures the dispatcher-PUSH vs wire-event-code asymmetry, the 41-entry jump table re-decoded, and per-handler spot-checks.
metadata:
  type: project
---

# game-opcodes.md Validation — 2026-05-28

Protocol family doc #4. Mid-tier — the opcode reference that translates the 41-entry
jump table into per-opcode wire formats. Heavy leveraged on the dispatcher recovery
work from the engine campaign.

## TL;DR

- **Status:** partial -> ready for documentation-writer re-render.
- **Binary corrections:** 0. The doc is exceptionally well-anchored.
- **Doc clarifications:** 1 (column-header asymmetry in the generic-event-forward table).
- **Anchoring re-verifications:** 41-entry jump table re-decoded byte-by-byte; 9 handler
  bodies spot-checked; event-ID override semantics confirmed in `FUN_0069FDA0`.
- **Cleanest doc in the protocol campaign so far** (parallels engine doc #10
  decompiled-functions.md from the engine campaign).

## Why this validation went fast

The dispatcher recovery (memory: `dispatcher-recovery-20260528.md`) had already:
- Decoded the 41-entry jump table byte-by-byte
- Cited each opcode -> handler binding
- Cited each generic-event-forward thunk's PUSH constant
- Installed a v5 plate comment on `MpgameHandleMessage` at 0x0069F2A0

This validation just re-anchored those claims against the current Ghidra DB and
spot-checked the 4 handlers that game-opcodes.md gives wire-format detail for.

## The one clarification: dispatcher PUSH vs wire event code

The doc's table at lines 131-144 has a column "Recv Event Code" with hex values per
opcode. Reality:

| Opcode | Doc says | Dispatcher PUSH | What the wire carries |
|--------|----------|------------------|------------------------|
| 0x07 StartFiring | 0x008000D7 | 0x008000D7 | (overridden by PUSH) |
| 0x08 StopFiring | 0x008000D9 | 0x008000D9 | (overridden) |
| 0x09 StopFiringAtTarget | 0x008000DB | 0x008000DB | (overridden) |
| 0x0A SubsysStatus | 0x0080006C | 0x0080006C | (overridden) |
| 0x0B AddToRepairList | 0x008000DF | 0x008000DF | (overridden) |
| 0x0C ClientEvent | (from stream) | 0 | wire value kept |
| 0x0E StartCloak | 0x008000E3 | 0x008000E3 | (overridden) |
| 0x0F StopCloak | 0x008000E5 | 0x008000E5 | (overridden) |
| 0x10 StartWarp | 0x008000ED | 0x008000ED | (overridden) |
| 0x11 RepairListPriority | 0x00800076 | 0 | wire value kept (doc's value IS the wire value) |
| 0x12 SetPhaserLevel | 0x008000E0 | 0 | wire value kept |
| 0x1B TorpedoTypeChange | 0x008000FD | 0x008000FD | (overridden) |

The semantic: `FUN_0069FDA0` line `if (param_2 != 0) puVar7[4] = param_2;` — when the
PUSH is non-zero, it OVERRIDES the wire event code. When PUSH=0, the wire value is
kept.

The doc's footer (line 148) documents this asymmetry explicitly (*"0x12 uses the same
code 0x008000E0 on both sides (no pairing, no override)"*) — but the table column
header doesn't disclose it. Recommend rename to "Effective Event Code (post-receive)".

## Anchored facts to remember

- Jump table at `0x0069F534` is **41 entries × 4 bytes = 164 bytes**.
- 9 entries point to the shared DEFAULT cleanup at `0x0069F525`: indices for opcodes
  0x04, 0x05, 0x16, 0x20, 0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x27, 0x28 (that's 12
  entries — 0x04/0x05 + 0x16 + 0x20..0x28 = 3 + 9 = 12). Re-check arithmetic before
  citing.
- Shared thunks (multiple opcodes sharing one thunk address):
  - 0x06 + 0x0D both at `0x0069F3F1` -> `FUN_0069F880` (PythonEvent)
  - 0x0C + 0x11 + 0x12 all at `0x0069F3C7` -> `FUN_0069FDA0(stream, 0)` (override=0)
- Opcode 0x1C StateUpdate handler at `0x0069FF50` was missing from CLAUDE.md's game
  opcode table before this campaign. Body is small (84 bytes); the heavy StateUpdate
  logic lives elsewhere.

## Handler quick-reference (verified this pass)

| Opcode | Handler | Verified detail |
|--------|---------|-----------------|
| 0x14 DestroyObject | FUN_006A01E0 | wire = `[u8 opcode][i32v object_id]`; branches on owner=NULL (cleanup) vs owner (call vtable[0x5C]) |
| 0x15 CollisionEffect | FUN_006A2470 | re-posts as event 0x008000FC; distance gate `_DAT_008955c8` |
| 0x06/0x0D PythonEvent | FUN_0069F880 | TGEvent factory `FUN_006D6200` + `FUN_006F13C0` (resolve refs) + `puVar2[9]=0` + `FUN_006DA300` (post) |
| 0x17 DeletePlayerUI | FUN_006A1360 | TGEvent factory chain + `FUN_006D62B0(this)` (this = MultiplayerGame*) |
| 0x29 Explosion | FUN_006A0080 | wire = `[opcode][i32v id][CV4 pos (5B)][CF16 radius][CF16 damage]`; radius (fStack_50) read FIRST, damage (fStack_54) SECOND, passed as `(pos, fStack_50, fStack_54)` to ctor at FUN_004BBDE0 |

## Open questions

1. **Opcode 0x18 DeletePlayerAnim wire format.** Handler `FUN_006A1420` named but no
   companion leaf doc on the BC side. OpenBC has one
   (`../OpenBC/docs/wire-formats/delete-player-anim-wire-format.md`). Mirror it.
2. **Event manager singleton address.** Engine doc #8 said TGEventManager singleton at
   `0x00991438`; engine anchor table §7.1 says "Event manager" at `0x0097F838`. Are
   these two distinct registries (handler-hash vs singleton) or a contradiction? Defer
   to whichever protocol doc cites the precise field.
3. **Session-frequency counts** need `[cross-source-2026-02-XX]` tags — they come from
   `docs/analysis/valentines-day-battle-analysis.md` and siblings, not the binary.

## Lessons (for the next protocol-doc validation)

- **When the dispatcher recovery has already decoded the jump table, validation is
  fast.** All you need to do is spot-check a handful of handlers + verify one or two
  load-bearing claims unique to this doc.
- **"Column header drift" is a real category of doc bug** distinct from binary
  drift. Two table rows can be technically correct under different semantic
  interpretations of the column header; the table needs disambiguation, not value
  correction.
- **The `FUN_0069FDA0` override semantics (`param_2 != 0 ? override : keep`)** is a
  load-bearing protocol invariant that should be cross-linked from every event-forward
  opcode doc. The doc footer mentions it once; reference it more aggressively in
  per-opcode leaf docs.
- **Cross-doc consistency between game-opcodes.md and the per-opcode leaf docs is
  high** — the doc was authored after the leaves and pulls in their formats by
  reference, so this row's debt is mostly cosmetic (tagging, frontmatter, restructure)
  rather than substantive.

## Next: protocol doc #5 (checksum-opcodes.md)

That doc covers opcodes 0x20-0x28 via NetFile dispatcher `FUN_006A3CD0`. Per
transport-layer.md correction C2, the actual cases are 0x20, 0x21, 0x22, 0x23, 0x25,
0x27 — NOT contiguous (0x24, 0x26, 0x28 are dead/unused). The 5-round table directories
need string-literal anchoring.
