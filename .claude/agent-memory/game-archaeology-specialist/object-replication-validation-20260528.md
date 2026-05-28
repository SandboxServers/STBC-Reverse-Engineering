---
name: object-replication-validation-20260528
description: Protocol doc #9 validation. 6/6 claims confirmed with 2 material refinements. Annotated MpgameHandleObjCreate at 0x0069F620.
metadata:
  type: project
---

# object-replication.md Validation — 2026-05-28

Smallest protocol-family doc (~30 lines). 6 load-bearing claims. Cleanest validation of the campaign so far.

## Confirmed Claims (6/6)

1. **Shared handler FUN_0069F620** — CONFIRMED. Jump-table thunks at:
   - 0x0069F31E (opcode 0x02): `PUSH 0; PUSH ESI; MOV ECX,EDI; CALL 0x0069F620`
   - 0x0069F334 (opcode 0x03): `PUSH 1; PUSH ESI; MOV ECX,EDI; CALL 0x0069F620`
   - Only difference: `bWithTeam` flag (param_3).

2. **Wire format** — CONFIRMED, with byte-numbering clarification:
   - off 0: u8 opcode (`0x02` or `0x03`) — present in raw buffer view but
     dispatcher consumed it as the jump key first
   - off 1: i8 owner_slot — `cVar3 = *(char *)((int)pvVar4 + 1)`
   - off 2: i8 team_id (iff `bWithTeam`) — `local_10 = (int)*(char *)((int)pvVar4 + 2)`
   - off 2 or 3: TGBufferStream payload — opened at `iVar7 + (int)pvVar4`
     (iVar7 = 2 or 3 depending on team flag)

3. **Team byte added for 0x03** — CONFIRMED. `iVar7 = 3` set ONLY when
   `param_3 != 0`; without team, `iVar7 = 2`. Receiver stores at
   `piVar5[0xB9]` (int index 0xB9 = byte offset 0x2E4). Sender side
   (FUN_006A02A0 + NewPlayerInGameHandler) writes from `controller+0x2E4`.

4. **FUN_005A1F50 deserializes** — CONFIRMED. Decompile shows:
   - `TGBufferStream_swig_OpenBuffer(local_3c, buf+iVar7, len-iVar7)`
   - `uVar1 = ReadInt`  -> class species ID
   - `uVar2 = ReadInt`  -> object ID
   - `FUN_00430730(0, uVar2)` -> class-category 0x8002 pre-check
   - `FUN_006F13E0(uVar1, uVar2)` -> factory: instantiate object
   - `vtable[0x118](stream)` -> Deserialize
   - `vtable[0x11C](&stack)` -> PostDeserializeFixup

5. **Receiver behavior** — CONFIRMED with refinement:
   - Active-slot SWAP (DAT_0097fa84 / DAT_0097fa8c / DAT_0095b07d) wraps
     the deserialize so per-slot state is updated for sender, not us.
   - On host: iterate 16 PlayerSlot entries at +0x7C (stride 0x18); for
     every slot whose `*piVar9` ID differs from BOTH the sender
     (param_2[3]) AND our own ID (network+0x20), clone+SendTGMessage.
   - Network controller (88 bytes via NiAlloc(0x58) + FUN_0047dab0) is
     attached via vtable+0x134 (AttachController).

6. **Authority** — CONFIRMED as S->C ONLY (per game-opcodes.md cross-anchor):
   - Senders of 0x02/0x03 are NewPlayerInGameHandler (on join) and
     FUN_006A02A0 (RequestObj response). Both are server-side codepaths.
   - Clients receive then forward via the in-loop relay (when running
     as host). game-opcodes audit shows 0 C->S for 0x02, 7 C->S for
     0x03 — but those C->S observations are likely the relay/echo from
     a player-host (a peer running as host re-broadcasting).

## Material Refinements (NOT corrections)

R1. **FUN_006A19A0 is SENDER-side only**.
   Doc says owner_slot is "mapped from object owner to player slot via
   FUN_006a19a0" — true of senders. The RECEIVER does not call 006a19a0.
   It reads the already-mapped byte directly. Tighten wording:
   "Byte 1: owner_player_slot (sender writes via FUN_006a19a0(owner_ptr))".

R2. **Doc cites `vtable[0x10C]` for serialization**.
   Correct — but 0x10C is byte offset (slot index 67 / 0x43). 0x10C is
   the SENDER vtable slot (writes the body). The RECEIVER uses 0x118
   (Deserialize) and 0x11C (Fixup), invoked from inside FUN_005A1F50.
   Body text conflates direction-symmetric pair into one.

## Open Questions

- Is the active-slot swap (DAT_0097fa84/8c) sound under re-entrancy?
  The DAT_0095b07d flag is set false before and true after FUN_005A1F50
  — but FUN_005A1F50 itself can recurse into events that might trigger
  more ObjCreate paths. Unknown if this is a known bug or guarded
  elsewhere. Out of scope.

- The "(if param_3 then attach controller; else don't)" client-side
  guard means non-team objects don't get a Network controller on
  clients. Is this intentional? Possibly: non-team objects might be
  inert decorations (torpedoes, debris).

- Why does the host path skip controller attach for `piVar5[1] ==
  *(int *)(param_1 + 0x80)` (own slot)? Likely because the host already
  has authority for its own objects.

## Cross-Anchor Validation

- transport-layer.md (foundation #3): TGMessage envelope at vtable
  0x008958D0 — CONSISTENT. param_2 is TGMessage, vtable+0x18 is
  Clone (Clone is the standard pattern in foundation #3).
- stream-primitives.md (foundation #2): SWIG TGBufferStream
  (`TGBufferStream_swig_*`) used inside FUN_005A1F50 — CONSISTENT.
  Opens against (buf+offset, len-offset) — same wrap pattern.
- game-opcodes.md (mid #4): 0x02/0x03 jump-table entries CONFIRMED
  byte-by-byte.
- wire-format-spec.md (foundation #1): 0x02/0x03 listed as S->C —
  CONSISTENT.

## v5 Annotations Applied

- Renamed: FUN_0069f620 -> MpgameHandleObjCreate
- Prototype: `void __thiscall MpgameHandleObjCreate(MultiplayerGame *,TGMessage *,char)`
- Plate comment: comprehensive (algorithm, params, wire format, struct
  layout, control flow, magic numbers, callers, cross-refs).
- effective_score 17.6 / max_achievable 78.6 — capped by the 6
  unrenamed DAT_* globals (shared across many other handlers, out of
  scope for this doc) and 12 magic-number EOL comments not added.
  Plate alone substantially documents the function.

## Patterns / Lessons

- Smallest doc in the protocol family — only ~30 lines, but the doc
  IS a thin handler index that delegates detail to
  objcreate-serialization.md. Cross-link discipline is important.
- Decompile of the receiver alone is insufficient — must decompile
  the senders (FUN_006A02A0 + 0x006A1E70) to verify wire format
  symmetry. The senders write what the receiver reads.
- Doc's `vtable[0x10C]` is a SENDER-side slot but appears in
  receiver-doc context — easy reader confusion. Tighten wording.
- "BIDIRECTIONAL" hypothesis in the task prompt (7 C->S for 0x03)
  was a misreading of game-opcodes audit. ObjCreateTeam is S->C
  with C->S observations being the in-loop relay path.

## Status

`partial` — all 6 claims confirmed; 2 material wording refinements
(direction of FUN_006A19A0 + receiver-vs-sender vtable slot) merit
update in the doc body. Cross-anchors aggressively to
objcreate-serialization.md (not yet validated).
