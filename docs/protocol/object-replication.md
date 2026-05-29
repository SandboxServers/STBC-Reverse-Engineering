> [docs](../README.md) / [protocol](README.md) / object-replication.md

---
title: Object Replication (Opcodes 0x02 ObjCreate / 0x03 ObjCreateTeam)
type: reference
audience: re-engineer
validated: 2026-05-29
methodology: FUNCTION_DOC_WORKFLOW_V5
binary:
  name: STBC.exe
  size: 6394712
  base: 0x00400000
status: partial
companions:
  - docs/protocol/wire-format-spec.md
  - docs/protocol/transport-layer.md
  - docs/protocol/stream-primitives.md
  - docs/protocol/game-opcodes.md
  - docs/protocol/objcreate-serialization.md
  - docs/engine/decompiled-functions.md
  - docs/protocol/v5-validation-status.md
supersedes:
  - (prior pre-v5 revision)
evidence:
  - claim: "MpgameHandleObjCreate at 0x0069F620 is the shared receiver and host-relay for opcodes 0x02 (ObjCreate) and 0x03 (ObjCreateTeam). Reached only via the two jump-table thunks; only param_3 (bWithTeam) differs."
    address: 0x0069f620
    function: MpgameHandleObjCreate
    completeness: 17.6
    confidence: high
    note: "Renamed + typed + plated this pass. effective_score 17.6 / max 78.6 is gated by 6 unrenamed DAT_* globals (shared across many other handlers, out of scope) and 12 magic-number EOL comments not added. Plate alone substantially documents the function."
  - claim: "Jump-table thunks for 0x02 and 0x03 are byte-identical except for the bWithTeam parameter. 0x02 thunk at 0x0069F31E (PUSH 0; PUSH ESI; MOV ECX,EDI; CALL 0x0069F620); 0x03 thunk at 0x0069F334 (PUSH 1; PUSH ESI; MOV ECX,EDI; CALL 0x0069F620)."
    address: 0x0069f31e
    function: MpgameHandleMessage
    completeness: 69.84
    confidence: high
    note: "Foundation #4 jump table at 0x0069F534 already v5-validated (see wire-format-spec.md and game-opcodes.md)."
  - claim: "Receiver wire format read directly from the buffer: off 0 = opcode (consumed as the jump-table key), off 1 = i8 owner_player_slot (cVar3 = *(char *)(buf+1)), off 2 = i8 net_player_id when bWithTeam (local_10 = *(char *)(buf+2)). Stream payload starts at buf+iVar7 where iVar7 = 2 or 3."
    address: 0x0069f620
    function: MpgameHandleObjCreate
    completeness: 17.6
    confidence: high
    note: "Receiver does NOT call FUN_006A19A0 — the owner-pointer-to-slot mapping happens on the sender side. See R1 in the NOTE block. [v5-correction 2026-05-29 via gamemode-system-validation memo — byte 2 is NetPlayerID, not team_id; ship+0x2E4 is the owning player's NetID. Three independent anchors: GetShipFromPlayerID @ 0x006A1AA0, IsLocalPlayerShip @ 0x005AE140, ShipClass_GetNetPlayerID @ 0x0060B8C0.]"
  - claim: "Senders symmetric with receiver. NewPlayerInGameHandler at 0x006A1E70 (player-join cascade) and FUN_006A02A0 (RequestObj response) both write local_40c[0] = 2|3, local_40c[1] = owner_slot, local_40c[2] = net_player_id. owner_slot is computed by the sender as FUN_006A19A0(ship->owner_ptr); net_player_id byte is sourced from controller+0x2E4 (= int-index 0xB9)."
    address: 0x006a1e70
    function: Handler_NewPlayerInGame
    completeness: 0.0
    confidence: high
    note: "Receiver stores the NetPlayerID byte at piVar5[0xB9] (byte offset 0x2E4); sender reads from the same offset. Wire format is direction-symmetric. [v5-correction 2026-05-29: field semantic relabeled from team_id to NetPlayerID per gamemode-system-validation memo; the offset, width, and parser are unchanged.]"
  - claim: "FUN_005A1F50 dispatch chain decodes the per-class payload: opens SWIG TGBufferStream over (buf+iVar7, len-iVar7), ReadInt32 for class species ID, ReadInt32 for object ID, runs FUN_00430730(0, classID) as a class-category 0x8002 pre-check, then instantiates via factory FUN_006F13E0(cls, id) and invokes object vtable+0x118 (Deserialize) and vtable+0x11C (PostDeserializeFixup)."
    address: 0x005a1f50
    function: FUN_005A1F50
    completeness: 0.0
    confidence: high
    note: "Per-class payload format (Ship vs Torpedo vs Beam vs Explosion) is emitted by class-specific vtable+0x10C overrides — see objcreate-serialization.md. This doc only carries the dispatch chain identity."
  - claim: "Receiver wraps FUN_005A1F50 in an active-slot SWAP so per-slot state is updated as if sender, not receiver, were the local player. DAT_0097FA84 is saved/restored, DAT_0097FA8C is swapped to the sender's slot, DAT_0095B07D is toggled 0 -> 1 around the call. On the host branch, a relay loop walks 16 PlayerSlots at MultiplayerGame+0x74 with stride 0x18, clones the message via TGMessage vtable+0x18, and SendTGMessages to every peer whose ID differs from BOTH the sender and our own. Network controller (88 bytes) is allocated via NiAlloc(0x58) + FUN_0047DAB0(controller, \"Network\") and attached via vtable+0x134 (AttachController)."
    address: 0x0069f620
    function: MpgameHandleObjCreate
    completeness: 17.6
    confidence: high
    note: "PlayerSlot array base at MultiplayerGame+0x74 with stride 0x18 confirmed via MultiplayerGame_Ctor (FUN_0069E590) line `FUN_00859d64(this+0x1d, 0x18, 0x10, ...)` — corrected from prior +0x7C and +0x84 references. Both prior numbers were intermediate field offsets within slots. See objcreate-serialization.md (mid #10) for full PlayerSlot layout and ctor evidence."
  - claim: "Authority is S -> C. Both senders (NewPlayerInGameHandler 0x006A1E70 and FUN_006A02A0) are server-side codepaths. Clients only receive and forward via the in-handler relay when acting as host. Client-observed C -> S traffic for opcode 0x03 in trace data is the host-relay echo (a peer running as host re-broadcasting), not authoritative client-initiated ObjCreate."
    address: null
    function: MpgameHandleObjCreate
    completeness: 17.6
    confidence: high
    note: "Negative claim: no C -> S authoritative ObjCreate sender exists in the binary. Both sender call sites are inside server-only handlers. game-opcodes.md (mid #4) cross-anchor confirms 0 C -> S for 0x02 and 7 C -> S for 0x03 attributable to host-relay echo."
---

# Object Replication (Opcodes 0x02 ObjCreate / 0x03 ObjCreateTeam)

> [!NOTE]
> This doc is `status: partial`. All 6 load-bearing claims confirmed at high confidence
> against the current Ghidra import (2026-05-28). Receiver handler renamed
> `MpgameHandleObjCreate` at `0x0069F620` (shared between opcodes 0x02 ObjCreate and
> 0x03 ObjCreateTeam — only differs by `bWithTeam` parameter). Two wording refinements
> applied:
>
> - **R1**: `FUN_006A19A0` is a sender-side helper that maps owner-pointer to
>   player-slot index. The receiver reads the already-mapped byte directly from buf+1.
> - **R2**: `vtable[0x10C]` is the **sender's** `SerializeForObjCreate` slot. The
>   receiver uses `vtable[0x118]` (Deserialize) and `vtable[0x11C]`
>   (PostDeserializeFixup) via the `FUN_005A1F50` dispatch chain.
>
> Detailed per-class payload format lives in
> [objcreate-serialization.md](objcreate-serialization.md) — this doc remains the thin
> handler-index summary it was meant to be. See
> [docs/guides/v5-evidence-header.md](../guides/v5-evidence-header.md) for the standard.
>
> **Pass 2 correction (2026-05-29) — wire byte 2 is `NetPlayerID`, not `team_id`.**
> When `bWithTeam == 1` (opcode `0x03`), the third wire byte is the owning player's
> network ID truncated to a signed byte, stored at `ship+0x2E4`. Stock BC has no C++
> team field; `ship+0x2E4` is consumed by `GetShipFromPlayerID @ 0x006A1AA0`,
> `IsLocalPlayerShip @ 0x005AE140`, and the SWIG accessor `ShipClass_GetNetPlayerID
> @ 0x0060B8C0`. Wire size and parser are unchanged; only the field semantic
> changes. Source: `.claude/agent-memory/game-archaeology-specialist/gamemode-system-validation-20260529.md`
> ("Major doc correction" section).

## Handler: MpgameHandleObjCreate (0x0069F620)

Shared receiver and host-relay for opcodes `0x02` (ObjCreate, non-team) and `0x03`
(ObjCreateTeam). Reached only via the two jump-table thunks; the call site differs by a
single byte of immediate (`PUSH 0` vs `PUSH 1`) that becomes the `bWithTeam` parameter.

| Opcode | Jump-table thunk | Thunk site | `bWithTeam` |
|--------|------------------|------------|-------------|
| 0x02 ObjCreate | `PUSH 0; PUSH ESI; MOV ECX,EDI; CALL 0x0069F620` | `0x0069F31E` | `0` |
| 0x03 ObjCreateTeam | `PUSH 1; PUSH ESI; MOV ECX,EDI; CALL 0x0069F620` | `0x0069F334` | `1` |

Function signature (after this pass):

```
void __thiscall MpgameHandleObjCreate(MultiplayerGame *this,
                                      TGMessage     *msg,
                                      char           bWithTeam);
```

## Wire format

```
Byte 0: opcode (0x02 or 0x03)
        — consumed by the dispatcher as the jump-table key
Byte 1: owner_player_slot (i8)
        — written by the sender as FUN_006A19A0(ship->owner_ptr)
        — receiver reads as *(char *)(buf+1)
[If bWithTeam (opcode 0x03):]
  Byte 2: net_player_id (i8)                                  [v5-correction 2026-05-29]
          — sender writes from controller+0x2E4 (= owning player's NetID)
          — receiver stores at piVar5[0xB9] (= byte offset 0x2E4)
          — prior label "team_id" was wrong; field is NetPlayerID
            per gamemode-system-validation memo

Remaining bytes (starting at off 2 or off 3):
  Per-class payload — see "Sender vs Receiver Symmetry" below
```

The first stream payload byte starts at `buf + iVar7`, where `iVar7 = 2` when
`bWithTeam == 0` and `iVar7 = 3` when `bWithTeam != 0`.

## Sender vs Receiver Symmetry

The wire format is direction-symmetric but the codepaths are not. Senders and receiver
each touch a different vtable slot on the same object.

| Direction | Function | Address | Vtable slot | Role |
|-----------|----------|---------|-------------|------|
| Sender | `Handler_NewPlayerInGame` | `0x006A1E70` | `+0x10C` | `SerializeForObjCreate(buf+iVar7, 0x400-iVar7)` |
| Sender | `Handler_RequestObj` (`FUN_006A02A0`) | `0x006A02A0` | `+0x10C` | Same — emits the per-class payload |
| Receiver | `MpgameHandleObjCreate` | `0x0069F620` | `+0x118`, `+0x11C` | Dispatched via `FUN_005A1F50` |

Sender pipeline (both senders share the layout):

```
WriteByte(opcode)                              ; 0x02 or 0x03
WriteByte(FUN_006A19A0(ship->owner_ptr))       ; owner_player_slot
if (bWithTeam)
    WriteByte(controller[0x2E4])               ; net_player_id
                                               ; [v5-correction 2026-05-29: was team_id]
ship->vtable[+0x10C](buf+iVar7, 0x400-iVar7)   ; SerializeForObjCreate
```

Receiver pipeline (`MpgameHandleObjCreate` -> `FUN_005A1F50`):

```
cVar3 = *(char *)(buf + 1)                     ; owner_player_slot
if (bWithTeam)
    local_10 = *(char *)(buf + 2)              ; net_player_id (int-promoted)
                                               ; [v5-correction 2026-05-29: was team_id;
                                               ;  stored at ship+0x2E4 = NetPlayerID]

FUN_005A1F50(buf + iVar7, len - iVar7):
    TGBufferStream_swig_OpenBuffer(stream, buf+iVar7, len-iVar7)
    classID = ReadInt32(stream)                ; class species ID
    objID   = ReadInt32(stream)                ; object ID
    if (FUN_00430730(0, classID) != NULL)
        REJECT                                 ; class-category 0x8002 pre-check
    obj = FUN_006F13E0(classID, objID)         ; factory: instantiate
    obj->vtable[+0x118](stream)                ; Deserialize
    obj->vtable[+0x11C](&fixup_ctx)            ; PostDeserializeFixup
```

The sender's `vtable[+0x10C]` and the receiver's `vtable[+0x118]` + `vtable[+0x11C]`
are direction-paired but **not the same slot**. The receiver never calls slot
`+0x10C`. The per-class payload format that flows over the wire is whatever
`SerializeForObjCreate` writes — class-specific layouts (Ship, Torpedo, Beam,
Explosion) are documented in
[objcreate-serialization.md](objcreate-serialization.md).

## Receive-side post-processing

After `FUN_005A1F50` returns, `MpgameHandleObjCreate` performs three additional
steps before returning to the dispatcher:

1. **Active-slot swap.** Wraps the deserialize so per-slot state is updated as
   though `cVar3` (owner_player_slot) were the local player.
   - `DAT_0097FA84` saved/restored
   - `DAT_0097FA8C` swapped to the sender's slot
   - `DAT_0095B07D` toggled `0 -> 1` around the call

2. **Host-side relay loop.** When this peer is the host, walks `16` PlayerSlots
   at `MultiplayerGame + 0x7C` with stride `0x18`. For every slot whose ID
   differs from BOTH the sender (`param_2[3]`) AND our own ID
   (`network + 0x20`), it clones the message via TGMessage `vtable + 0x18`
   and calls `SendTGMessage` to forward.

3. **Network controller attach.** A `Network` controller (88 bytes via
   `NiAlloc(0x58)` + `FUN_0047DAB0(controller, "Network")`) is attached to
   the freshly deserialized object via `vtable + 0x134` (AttachController).
   The host branch skips controller attach when `piVar5[1] == *(int *)(this+0x80)`
   (own slot) — see Open Questions.

## Authority

Opcodes 0x02 and 0x03 are **server-authoritative (S -> C)**.

| Sender call site | Address | Trigger |
|------------------|---------|---------|
| `Handler_NewPlayerInGame` | `0x006A1E70` | Player join — server iterates all replicated objects and sends to the new peer |
| `Handler_RequestObj` | `0x006A02A0` | Client RequestObj (`0x1E`) for an object it doesn't have — server responds with ObjCreate |

Both call sites are inside server-only handlers. There is no authoritative client
sender for ObjCreate.

Trace observations of C -> S traffic for opcode 0x03 (game-opcodes.md cross-anchor
records 7 instances; 0 for 0x02) are the **host-relay echo** path — a peer running as
host re-broadcasting the message it just received. This is a wire-direction artifact of
the topology, not authoritative ObjCreate authority.

## Cross-anchor references

| Anchor | Address | Source | Note |
|--------|---------|--------|------|
| MultiplayerGame dispatcher | `0x0069F2A0` | foundation #4 (wire-format-spec.md) | Jump-table source |
| Jump table | `0x0069F534` | foundation #4 (wire-format-spec.md) | 41 entries; 0x02 + 0x03 at offsets 0 and 4 |
| TGMessage envelope vtable | `0x008958D0` | foundation #3 (transport-layer.md) | `param_2` type; `vtable+0x18` = Clone for relay |
| SWIG TGBufferStream ctor | `0x006CEFE0` | foundation #2 (stream-primitives.md) | Used by `FUN_005A1F50` for the payload |
| `Handler_NewPlayerInGame` | `0x006A1E70` | game-opcodes.md (mid #4) | Sender on player-join |
| `Handler_RequestObj` | `0x006A02A0` | game-opcodes.md (mid #4) | Sender on RequestObj |
| Per-class payload format | (various) | [objcreate-serialization.md](objcreate-serialization.md) | This doc deliberately delegates per-class detail |

## Open questions

- **Active-slot SWAP reentrancy.** `DAT_0095B07D` is set false before
  `FUN_005A1F50` and true after, implying a guard. Unknown whether
  `FUN_005A1F50` itself can recurse into more ObjCreate paths via events
  fired during Deserialize/Fixup. If so the outer save/restore could leak.
  Out of scope here; revisit if it surfaces in crash reports.
- **Host self-skip for controller attach.** When `piVar5[1] == *(int *)(this+0x80)`
  (own slot), the host branch skips the controller attach. Likely because the
  host already has authority for its own objects, but not yet confirmed.
  Will revisit during `objcreate-serialization.md` validation (next in the
  campaign).
- **Per-class wire payloads** (Ship vs Torpedo vs Beam vs Explosion) are emitted
  by class-specific `vtable+0x10C` overrides — those belong to the per-class
  wire-format docs, not here.

## See also

- [objcreate-serialization.md](objcreate-serialization.md) — full ObjCreate
  serialization chain, species map, and per-class payload formats (next
  validation target in the campaign)
- [game-opcodes.md](game-opcodes.md) — opcodes 0x02 + 0x03 dispatcher row
- [wire-format-spec.md](wire-format-spec.md) — hub: opcode index + handler
  addresses
- [stream-primitives.md](stream-primitives.md) — TGBufferStream read/write
  primitives used by the dispatch chain
- [transport-layer.md](transport-layer.md) — TGMessage envelope + `vtable+0x18`
  Clone used by the host-relay loop
- [v5-validation-status.md](v5-validation-status.md) §6.9 — full validation
  report for this doc
