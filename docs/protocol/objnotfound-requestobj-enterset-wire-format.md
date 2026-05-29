> [docs](../README.md) / [protocol](README.md) / objnotfound-requestobj-enterset-wire-format.md

---
title: ObjNotFound / RequestObj / EnterSet Wire Format (Opcodes 0x1D / 0x1E / 0x1F)
type: reference
audience: re-engineer
validated: 2026-05-28
methodology: FUNCTION_DOC_WORKFLOW_V5
binary:
  name: stbc.exe
  size: 6182400
  base: 0x00400000
status: partial
evidence:
  - claim: "MpgameHandleMessage dispatches game opcodes 0x02-0x2A via 41-entry jump table"
    address: 0x0069F2A0
    function: MpgameHandleMessage
    completeness: high
    confidence: high
    note: "Engine cross-anchor — see v5-validation-status.md §7.1"
  - claim: "Jump table at 0x0069F534 routes opcode 0x1D to thunk 0x0069f4f5 then to handler 0x006a0490"
    address: 0x0069F534
    function: MpgameHandleMessage
    completeness: high
    confidence: high
    note: "Bytes at jump-table+108..111 = `f5 f4 69 00` (index 27 = opcode 0x1D - 2)"
  - claim: "Jump table at 0x0069F534 routes opcode 0x1E to thunk 0x0069f51d then to handler 0x006a02a0"
    address: 0x0069F534
    function: MpgameHandleMessage
    completeness: high
    confidence: high
    note: "Bytes at jump-table+112..115 = `1d f5 69 00` (index 28)"
  - claim: "Jump table at 0x0069F534 routes opcode 0x1F to thunk 0x0069f509 then to handler 0x006a05e0"
    address: 0x0069F534
    function: MpgameHandleMessage
    completeness: high
    confidence: high
    note: "Bytes at jump-table+116..119 = `09 f5 69 00` (index 29)"
  - claim: "Opcode 0x1D ObjNotFound receiver reads `[int32 objectID]` then relays opcode 0x1E with the same ID back to host (connection 0) when the object is also missing locally"
    address: 0x006a0490
    function: MultiplayerGame__ObjNotFoundHandler
    completeness: high
    confidence: high
    note: "Disasm 0x006a04ee=ReadInt; 0x006a0535=WriteChar(0x1e); 0x006a0540=WriteInt; 0x006a058b=SendTGMessage(target=0)"
  - claim: "Opcode 0x1E RequestObj receiver reads `[int32 objectID]` and responds with a freshly-built ObjCreate (0x02 / 0x03) plus any pending 0x29 explosion replays, sent only to the requesting connection"
    address: 0x006a02a0
    function: MultiplayerGame__RequestObjHandler
    completeness: high
    confidence: high
  - claim: "Opcode 0x1F EnterSet receiver reads `[int32 objectID][uint32 N][N bytes setName]` then performs ExitSet on the ship's current TGSet and EnterSet on the destination set"
    address: 0x006a05e0
    function: MultiplayerGame__EnterSetHandler
    completeness: high
    confidence: high
  - claim: "0x1E sends to nTargetID (the requesting connection) only, NOT broadcast"
    address: 0x006a0596
    function: MultiplayerGame__RequestObjHandler
    completeness: high
    confidence: high
    note: "Disasm: `PUSH 0, PUSH ESI(msg), PUSH EDI(nTargetID), CALL SendTGMessage`. EDI was loaded with sender ID at handler entry."
  - claim: "0x1D allocates a 64-byte TGMessage via the `\"UNKNOWN\"` class-name pool"
    address: 0x006a0551
    function: MultiplayerGame__ObjNotFoundHandler
    completeness: high
    confidence: high
    note: "Disasm: `PUSH 0x40, PUSH 0x8d858c` (s_UNKNOWN). The same `\"UNKNOWN\"` pool is used by 0x1D / 0x1E / 0x1F / 0x29 / NewPlayerInGameHandler — it is the literal class name for generic-pool TGMessage allocation, not a placeholder for an unknown class."
  - claim: "0x1D / 0x1E set msg+0x3a = 1 (guaranteed flag); 0x1E additionally sets msg+0x3d = 0 (no-notify)"
    address: 0x006a0592
    function: MultiplayerGame__ObjNotFoundHandler
    completeness: high
    confidence: high
    note: "Disasm 0x006a0592 (0x1D): `MOV byte ptr [ESI + 0x3a], 0x1`. Same pattern at 0x006a041a / 0x006a041e in 0x1E handler."
  - claim: "0x1E gates the response on `obj+0xec != 0` (the network-enable byte; `piVar4[0x3b]` in raw decompile = byte offset 0xec)"
    address: 0x006a032f
    function: MultiplayerGame__RequestObjHandler
    completeness: high
    confidence: high
    note: "Disasm: `MOV EAX, dword ptr [ESI + 0xec]`"
  - claim: "0x1E gates the response on `DAT_008e5c18 <= dobj[+0x14c]` AND `dobj[+0x150] == 0` — effectively `dobj+0x14c == FLT_MAX AND dobj+0x150 == 0` (undamaged AND alive)"
    address: 0x006a034c
    function: MultiplayerGame__RequestObjHandler
    completeness: high
    confidence: high
    note: "Disasm 0x006a034c-0x006a036b: `FLD float ptr [EBX + 0x14c]; FCOMP [008e5c18]; FNSTSW; JNZ cleanup`; then `CMP byte ptr [EBX + 0x150], 0; JNZ cleanup`. C3 correction — see body §C3."
  - claim: "DAT_008e5c18 is float32 FLT_MAX (0x7F7FFFFF = 3.4028235e+38), used by DamageableObject as the `undamaged` sentinel for dobj+0x14c"
    address: 0x008e5c18
    function: null
    completeness: high
    confidence: high
    note: "C3 correction — pre-v5 doc called this a `small positive HP threshold`. Bytes at 0x008e5c18 = `ff ff 7f 7f` = FLT_MAX. Ctor at FUN_00590cb0 initializes dobj+0x14c = FLT_MAX; damage-application FUN_00592c00 decrements that field. The gate succeeds only on a never-damaged object."
  - claim: "DamageableObject ctor initializes `dobj+0x14c = FLT_MAX`, `dobj+0x150 = 0` (alive flag)"
    address: 0x00590cb0
    function: FUN_00590cb0
    completeness: medium
    confidence: high
    note: "Ctor identified by xref from class 0x8007 IsA path. Field init confirmed at prologue."
  - claim: "DamageableObject damage application path writes `dobj+0x14c -= delta` and sets dobj+0x150 dead flag on death"
    address: 0x00592c00
    function: FUN_00592c00
    completeness: medium
    confidence: high
  - claim: "0x1E response opcode is 0x03 (ObjCreateTeam) when `IsLocalPlayerShip(ship)` returns non-zero, else 0x02 (ObjCreate)"
    address: 0x006a0392
    function: MultiplayerGame__RequestObjHandler
    completeness: high
    confidence: high
    note: "Disasm 0x006a0392: `MOV byte ptr [ESP + 0x50], 0x3`; 0x006a039e: `MOV byte ptr [ESP + 0x50], 0x2`. Note Clar2: on a HOST, `IsLocalPlayerShip` (FUN_005ae140) returns true for ANY team-bearing ship (ship+0x2e4 != 0), not just one local player."
  - claim: "0x1E response payload writes `playerSlot = GetPlayerSlotFromObjID(obj+4)` into payload byte 1"
    address: 0x006a03ab
    function: MultiplayerGame__RequestObjHandler
    completeness: high
    confidence: high
    note: "Disasm: `CALL 0x006a19a0` after `PUSH obj+4`. C4 — GetPlayerSlotFromObjID is at 0x006a19a0, NOT 0x005a2030 (which is ShipReadSpecies)."
  - claim: "For opcode 0x03 response, payload byte 2 is `ship+0x2e4` (team/species byte)"
    address: 0x006a03b9
    function: MultiplayerGame__RequestObjHandler
    completeness: high
    confidence: high
    note: "Disasm: `MOV EAX, dword ptr [EBP + 0x2e4]; MOV byte ptr [ESP + 0x52], AL`"
  - claim: "Object serialization invokes WriteToStream via vtable[+0x10c] (= slot 67)"
    address: 0x006a03d4
    function: MultiplayerGame__RequestObjHandler
    completeness: high
    confidence: high
    note: "Disasm: `CALL dword ptr [EDX + 0x10c]` where EDX = *ESI (obj vtable)"
  - claim: "After serving 0x1E, the handler replays explosions only when the object IS-A DamageableObject (class 0x8007); otherwise the replay step is skipped"
    address: 0x006a042f
    function: MultiplayerGame__RequestObjHandler
    completeness: high
    confidence: high
    note: "Disasm: `TEST EBX, EBX; JZ 0x006a043b`; else `CALL DamageableObject__SendExplosions_0x29`"
  - claim: "DamageableObject__SendExplosions_0x29 walks the linked list at dobj+0x13c and emits one opcode 0x29 packet per entry (CompressedVector4 + 2x CF16)"
    address: 0x00595c60
    function: DamageableObject__SendExplosions_0x29
    completeness: high
    confidence: high
    note: "Decompile: `iVar1 = *(int *)(*(int *)(param_1 + 0x13c) + 0x14);` then loop writing 0x29 + CompressedVector4 + CF16 + CF16"
  - claim: "0x1F NULL-found path relays `[0x1E][int32 objectID]` to host (target=0) — same pattern as 0x1D fallback"
    address: 0x006a05e0
    function: MultiplayerGame__EnterSetHandler
    completeness: high
    confidence: high
  - claim: "0x1F warp-engine gate: `ship+0x2d0 != 0` (warp subsystem ptr) AND `*(ship+0x2d0+0xb4) == 0` (not already in transit)"
    address: 0x006a05e0
    function: MultiplayerGame__EnterSetHandler
    completeness: high
    confidence: high
  - claim: "0x1F set lookup consults TGSetManager array at DAT_0097e9c8 via FindSetIndexByName (FUN_004055a0, binary search)"
    address: 0x006a05e0
    function: MultiplayerGame__EnterSetHandler
    completeness: high
    confidence: high
    note: "Decompile: `*(int **)(DAT_0097e9c8 + iVar6 * 4)`. FindSetIndexByName at 0x004055a0."
  - claim: "0x1F transition calls ExitSet via current-set vtable[+0x58] (slot 22) with arg = ship+4 (obj ID); then EnterSet via dest-set vtable[+0x54] (slot 21) with args = (ship, ship+0x28)"
    address: 0x006a05e0
    function: MultiplayerGame__EnterSetHandler
    completeness: high
    confidence: high
    note: "Decompile: `(**(code **)(*piVar1 + 0x58))(*(undefined4 *)(iVar5 + 4));` and `(**(code **)(*piVar7 + 0x54))(iVar5, *(undefined4 *)(iVar5 + 0x28));`"
  - claim: "0x1F frees the heap-allocated setName via NiFree thunk FUN_00718cf0 (jumps to FUN_00717960) before return"
    address: 0x006a05e0
    function: MultiplayerGame__EnterSetHandler
    completeness: high
    confidence: high
  - claim: "Stream-string read is LENGTH-PREFIXED: `TGBufferStream__ReadString_HeapAlloc` reads uint32 length via vtable[+0x68] then raw bytes via vtable[+0x10] — no null terminator on the wire"
    address: 0x006d2370
    function: TGBufferStream__ReadString_HeapAlloc
    completeness: high
    confidence: high
    note: "C1 correction — pre-v5 doc said `null-terminated`. Decompile: `iVar1 = (**(code **)(*param_1 + 0x68))(); ... (**(code **)(*param_1 + 0x10))(uVar2, iVar1);`"
  - claim: "Stream-string write is symmetric LENGTH-PREFIXED: `TGBufferStream__WriteString_LenPrefixed` writes uint32 length via vtable[+0x6c] then raw bytes via vtable[+0x14]"
    address: 0x006d23c0
    function: TGBufferStream__WriteString_LenPrefixed
    completeness: high
    confidence: high
  - claim: "TGBufferStream cursor vtable @ 0x00895C58 has slots +0x10 ReadBytes, +0x14 WriteBytes, +0x68 ReadInt, +0x6c WriteInt"
    address: 0x00895C58
    function: TGBufferStream_cursor_vtable
    completeness: high
    confidence: high
    note: "Foundation cross-anchor for stream-primitives.md vtable layout"
  - claim: "GetPlayerSlotFromObjID at 0x006a19a0 computes `(objID - 0x3FFFFFFF + ((objID - 0x3FFFFFFF >> 31) & 0x3FFFF)) >> 18`"
    address: 0x006a19a0
    function: GetPlayerSlotFromObjID
    completeness: high
    confidence: high
    note: "C4 correction — pre-v5 doc listed this at 0x005a2030. FUN_005a2030 is ShipReadSpecies, an unrelated 2-vtable-call ship-setup function."
  - claim: "MakeObjIDFromPlayerSlot at 0x006a7770 is the INVERSE of GetPlayerSlotFromObjID; it is NOT called by the 0x1D / 0x1E / 0x1F triad"
    address: 0x006a7770
    function: MakeObjIDFromPlayerSlot
    completeness: high
    confidence: high
    note: "C5 correction — pre-v5 doc labeled this `MultiplayerGame__GetPlayerSlotFromObjID`. Body: `*(int *)(param_1 + 0x10) = param_2 * 0x40000 + 0x3fffffff;` — constructs an obj ID from a slot."
  - claim: "0x1F client-side sender event handler MultiplayerGame__RequestObjEventHandler at 0x006a07d0 sends to the `\"NoMe\"` group (DAT_008e5528)"
    address: 0x006a07d0
    function: MultiplayerGame__RequestObjEventHandler
    completeness: high
    confidence: high
    note: "575-byte body; newly defined in Ghidra this pass. The `\"NoMe\"` group is `all peers except self`; the 0x1D / 0x1F senders broadcast to `\"NoMe\"`, NOT to host(0) (host(0) is only the relay target on the receiver-side NULL-found fallback in 0x1F). Function renamed 2026-05-28 per docs/networking/disconnect-flow.md — SWIG plate is `MultiplayerGame__EnterSetHandler` per FUN_0069efe0 binding (string at 0x0095a0a8); dual-opcode behavior unchanged."
  - claim: "0x1F sender suppresses emission when ship's current set name == `\"warp\"`; sends 0x1F only when ship IS in warp AND currentSetName != `\"warp\"`"
    address: 0x006a07d0
    function: MultiplayerGame__RequestObjEventHandler
    completeness: high
    confidence: high
    note: "C2 correction — DAT_008d8ab8 is the literal 5 bytes `\"warp\\0\"`, NOT the `default space combat set name`. Sender uses strcmp(currentSetName, DAT_008d8ab8) to gate. Function renamed 2026-05-28 per docs/networking/disconnect-flow.md — SWIG plate is `MultiplayerGame__EnterSetHandler`; behavior unchanged."
  - claim: "DAT_008d8ab8 is the literal C-string `\"warp\\0\"` (5 bytes including NUL), the `in-warp-tunnel` set name sentinel"
    address: 0x008d8ab8
    function: null
    completeness: high
    confidence: high
    note: "C2 correction. Bytes at 0x008d8ab8 = `77 61 72 70 00`. Next string in the rdata block is `\"ShipClass\"`."
  - claim: "MultiplayerGame__EnterSetEventHandler at 0x006a0a20 is a single-RET empty stub (3-byte body)"
    address: 0x006a0a20
    function: MultiplayerGame__EnterSetEventHandler
    completeness: high
    confidence: high
    note: "Newly defined in Ghidra this pass. Single DATA xref from FUN_0069efe0 at 0x0069eff9 (SWIG handler registration). Function renamed 2026-05-28 per docs/networking/disconnect-flow.md — actual SWIG plate is `MultiplayerGame__DisconnectHandler` (event 0x60003 ET_NETWORK_DISCONNECT, binding string at 0x0095a1f0); empty body in MP because cleanup runs via transport layer."
  - claim: "TGSceneGraph__GetObjectByID at 0x00434e00 resolves an object ID via factory class tag 0x8003"
    address: 0x00434e00
    function: TGSceneGraph__GetObjectByID
    completeness: high
    confidence: high
  - claim: "PhysicsObjectClass__FindByObjectID at 0x0059fc60 uses class tag 0x8006"
    address: 0x0059fc60
    function: PhysicsObjectClass__FindByObjectID
    completeness: high
    confidence: high
  - claim: "CastToDamageableObject at 0x00590b20 is the IsA(0x8007) check used by the 0x1E explosion-replay gate"
    address: 0x00590b20
    function: CastToDamageableObject
    completeness: high
    confidence: high
  - claim: "CastToShipClass at 0x005ab670 is the IsA(0x8008) check used by the 0x1E opcode-selection (0x02 vs 0x03) branch"
    address: 0x005ab670
    function: CastToShipClass
    completeness: high
    confidence: high
  - claim: "IsLocalPlayerShip at 0x005ae140 is host-mode-aware: on host (DAT_0097fa89 != 0) returns true for any ship with team-id != 0; on client returns true only for the local player's ship"
    address: 0x005ae140
    function: IsLocalPlayerShip
    completeness: high
    confidence: high
    note: "Clar2 — name is misleading on a dedicated server, where opcode 0x03 is selected for every team-bearing ship, not one `local` ship."
  - claim: "TGNetwork singleton at DAT_0097fa78 (UtopiaModule+0x78) is loaded by every triad handler"
    address: 0x0097fa78
    function: TGNetwork_singleton
    completeness: high
    confidence: high
    note: "Engine cross-anchor — see v5-validation-status.md §7.1"
  - claim: "TGSetManager array head at DAT_0097e9c8 is the in-game set table, binary-searched by FindSetIndexByName (FUN_004055a0)"
    address: 0x0097e9c8
    function: TGSetManager_array
    completeness: high
    confidence: high
  - claim: "`\"NoMe\"` relay group name (all-peers-except-self) at DAT_008e5528"
    address: 0x008e5528
    function: null
    completeness: high
    confidence: high
    note: "Foundation cross-anchor — see v5-validation-status.md §7.2"
  - claim: "`\"UNKNOWN\"` allocator class-name string at 0x008d858c is the LITERAL class name for the generic TGMessage pool, used by 0x1D / 0x1E / 0x1F / 0x29 / NewPlayerInGameHandler"
    address: 0x008d858c
    function: null
    completeness: high
    confidence: high
    note: "R2 — not a placeholder for `we don't know the class`."
  - claim: "Triad uses raw TGBufferStream primitives only (ReadInt / ReadString_HeapAlloc / WriteChar / WriteInt), bypassing TGFactory_DeserializeObject (0x006d6200)"
    address: null
    function: null
    completeness: high
    confidence: high
    note: "Negative claim. Verified by reading 0x006a0490 / 0x006a02a0 / 0x006a05e0 bodies in full — no calls to FUN_006d6200 or to any TGFactory helper. Contrasts with opcodes 0x06 / 0x12 / 0x15 / 0x17 which all go through TGFactory."
companions:
  - docs/protocol/wire-format-spec.md
  - docs/protocol/game-opcodes.md
  - docs/protocol/transport-layer.md
  - docs/protocol/stream-primitives.md
  - docs/protocol/objcreate-serialization.md
  - docs/protocol/object-replication.md
  - docs/protocol/cf16-explosion-encoding.md
  - docs/protocol/delete-player-ui-wire-format.md
  - docs/protocol/v5-validation-status.md
  - docs/engine/rtti-class-catalog.md
supersedes:
  - 2026-02-21
---

# Opcodes 0x1D, 0x1E, 0x1F Wire Format and Handler Analysis

> [!NOTE]
> This doc is `status: partial`. The handler addresses, dispatcher routing, and structural semantics of the triad (0x1D requests recovery, 0x1E carries the response, 0x1F handles in-system-warp set transitions) are v5-validated. **Three material wire-format / data-constant corrections** plus **two address-mapping corrections** are applied. Per-claim sections are linked from the bullets. **(C1)** the EnterSet `setName` field is length-prefixed (`uint32 len + N bytes`), NOT null-terminated. **(C2)** the gate constant at `0x008d8ab8` is the literal string `"warp"` — the in-warp-tunnel sentinel — NOT the `default space combat set name`; 0x1F is sent during warp transitions to named warp-target sub-sets, not during normal combat. **(C3)** `DAT_008e5c18` is `FLT_MAX` (the DamageableObject `undamaged` sentinel), NOT a `small positive HP threshold`; the 0x1E gate is therefore stricter than the doc implied — only never-damaged + alive objects are served. **(C4)** `GetPlayerSlotFromObjID` lives at `0x006a19a0`, NOT `0x005a2030` (which is `ShipReadSpecies`). **(C5)** `0x006a7770` is `MakeObjIDFromPlayerSlot` (the INVERSE) and is not called by the triad. Plus two clarifications: **(Clar1)** the triad uses raw `TGBufferStream` primitives only and bypasses `TGFactory_DeserializeObject` — these are command (RPC) messages, not event objects (new subsection below). **(Clar2)** `IsLocalPlayerShip` is host-mode-aware: on a dedicated server, opcode 0x03 is selected for every team-bearing ship, not one local player. See [v5-evidence-header.md](../guides/v5-evidence-header.md) for the standard. Source evidence: `.claude/agent-memory/game-archaeology-specialist/objnotfound-triad-validation-20260528.md`.
>
> **Post-validation update (2026-05-28 via networking leaf #10 disconnect-flow)**: Function-name attributions at 0x006a0a20 and 0x006a07d0 were corrected in Ghidra plates after this doc rendered. **0x006a0a20** is the `MultiplayerGame__DisconnectHandler` stub (event 0x60003 ET_NETWORK_DISCONNECT), NOT an EnterSet stub. **0x006a07d0** carries the SWIG-registered name `MultiplayerGame__EnterSetHandler` per FUN_0069efe0 binding (string at 0x0095a0a8); its dual-opcode body (sends BOTH 0x1D ObjNotFound when ship NOT in warp AND 0x1F EnterSet when ship IN warp + destination != "warp") remains as documented. See `docs/networking/disconnect-flow.md` for the binding-table evidence chain.

---

## Overview

These three opcodes form the **object recovery / scene transition** subsystem in Bridge Commander multiplayer. They work as a triad:

- **0x1D ObjNotFound** (OBJECT_NOT_FOUND) — client tells host "I got a message referencing object X but I don't have it"
- **0x1E RequestObj** (SEND_OBJECT_MESSAGE) — host responds with a full serialized copy of the object
- **0x1F EnterSet** (VERIFY_ENTER_SET_MESSAGE) — client tells host "my ship is entering set Y"

All three are routed by `MpgameHandleMessage` (0x0069F2A0) via the 41-entry jump table at `0x0069F534`:

| Opcode | Jump-table index | Thunk | Handler |
|--------|------------------|-------|---------|
| 0x1D | 27 | 0x0069f4f5 | 0x006a0490 (`MultiplayerGame__ObjNotFoundHandler`) |
| 0x1E | 28 | 0x0069f51d | 0x006a02a0 (`MultiplayerGame__RequestObjHandler`) |
| 0x1F | 29 | 0x0069f509 | 0x006a05e0 (`MultiplayerGame__EnterSetHandler`) |

---

## Command Messages vs Event Messages — Why the Triad Bypasses TGFactory

[v5-validated 2026-05-28]

The 0x1D / 0x1E / 0x1F handlers are **command messages** (RPC-style requests and responses), not event-bearing transports. They differ structurally from the TGEvent-family opcodes documented in sibling leaves:

| Opcode | Style | Deserialization path |
|--------|-------|----------------------|
| 0x06 PythonEvent | Event-bearing | `TGFactory_DeserializeObject` (0x006d6200) → class lookup → typed event Read |
| 0x12 SetPhaserLevel | Event-bearing | `TGFactory_DeserializeObject` (TGCharEvent factory 0x105) |
| 0x15 CollisionEffect | Event-bearing | `TGFactory_DeserializeObject` (CollisionEvent factory) |
| 0x17 DeletePlayerUI | Event-bearing | `TGFactory_DeserializeObject` (TGFactory 0x866) |
| **0x1D ObjNotFound** | **Command** | **Raw `stream->vtable[+0x68]` ReadInt only** |
| **0x1E RequestObj** | **Command** | **Raw `stream->vtable[+0x68]` ReadInt; response built directly via `WriteByte` + `WriteInt` + WriteToStream** |
| **0x1F EnterSet** | **Command** | **Raw `stream->vtable[+0x68]` ReadInt + `TGBufferStream__ReadString_HeapAlloc` only** |

No factory plumbing is involved in the triad — the receivers read primitive fields, look up the referenced object directly from the scene graph, and either build a response payload by hand (0x1E) or perform a state transition (0x1F). This makes them simpler to reimplement in OpenBC: no class-ID lookup, no TGFactory registry table needed.

---

## Opcode 0x1D — ObjNotFound

**Handler:** `MultiplayerGame__ObjNotFoundHandler` @ `0x006a0490`
**Python constant:** (none exported — internal opcode)
**Direction:** Client → Host

### Purpose

Sent by the client when it receives a message referencing an object ID that it cannot find in its local TGSceneGraph. Acts as a request: "please resend object X to me."

### Wire Format

```
[0x1D][int32: objectID]
```

| Offset | Size | Type   | Description                     |
|--------|------|--------|---------------------------------|
| 0      | 1    | byte   | Opcode = 0x1D                   |
| 1      | 4    | int32  | Object ID to locate             |

Total: 5 bytes.

### Handler Behavior

```c
void MultiplayerGame__ObjNotFoundHandler(void *param_1) {
    // Read 4-byte object ID via stream->vtable[+0x68]
    int objectID = TGBufferStream__ReadInt(stream);    // 0x006a04ee

    // Try to find the object locally
    int *obj = TGSceneGraph__GetObjectByID(NULL, objectID);

    if (obj == NULL) {
        // Object is ALSO not found locally — respond with opcode 0x1E (RequestObj) to host
        // Allocate a 64-byte TGMessage from the "UNKNOWN" generic pool (s_UNKNOWN at 0x008d858c)
        msg = TGAlloc(0x40, "UNKNOWN");                // 0x006a0551
        WriteChar(stream, 0x1e);                       // 0x006a0535
        WriteInt(stream, objectID);                    // 0x006a0540
        msg->guaranteed = 1;                           // [msg + 0x3a] = 1  (0x006a0592)
        TGNetwork__Send(network, 0, msg, 0);           // target = host (0)  (0x006a058b)
    }
    // If found locally, do nothing — the object exists, no recovery needed
}
```

**Key observation:** the handler only relays a 0x1E upward if the object is ALSO missing locally. On a dedicated server, the host's own missing-object case relays to itself (connection 0), which is normally a no-op. The 0x1D pathway is genuinely active when an upstream peer (in a chained or relay setup) might still have the object.

**Response it sends (when relaying):** `[0x1E][int32: objectID]` to connectionID 0 (host), guaranteed.

---

## Opcode 0x1E — RequestObj (SEND_OBJECT_MESSAGE)

**Handler:** `MultiplayerGame__RequestObjHandler` @ `0x006a02a0`
**Python constant:** `App.SEND_OBJECT_MESSAGE`
**Direction:** Client → Host, then Host → requesting Client

### Purpose

A client requests that the host resend a full object serialization for a given object ID. The host responds with a full `ObjCreate` (opcode 0x02 or 0x03) packet for that object plus any queued explosions.

### Wire Format (Request)

```
[0x1E][int32: objectID]
```

| Offset | Size | Type   | Description              |
|--------|------|--------|--------------------------|
| 0      | 1    | byte   | Opcode = 0x1E            |
| 1      | 4    | int32  | Object ID to request     |

Total: 5 bytes.

### Handler Behavior

```c
void MultiplayerGame__RequestObjHandler(void *stream_msg) {
    int nTargetID = *(int*)(stream_msg + 0x0C);        // sender's connection ID  (0x006a02dd)
    int objectID  = TGBufferStream__ReadInt(stream);

    // Resolve via PhysicsObjectClass factory (IsA 0x8006)
    int *obj = PhysicsObjectClass__FindByObjectID(NULL, objectID);

    if (obj == NULL) return;                            // Object doesn't exist — silent drop
    if (*(int*)(obj + 0xec) == 0) return;               // Object not networked — drop  (0x006a032f)

    // (C3) DamageableObject "undamaged + alive" gate:
    //   dobj+0x14c == FLT_MAX  AND  dobj+0x150 == 0
    DamageableObject *dobj = CastToDamageableObject(obj);   // IsA(0x8007)
    if (dobj != NULL) {
        // FLT_MAX <= dobj->hp_sentinel  (0x006a034c) — succeeds only if dobj->hp_sentinel == FLT_MAX
        if (!(*(float*)0x008e5c18 <= dobj->hp_sentinel)) return;
        // dead-flag check  (0x006a036b)
        if (dobj->dead_flag != 0) return;
    }

    // Determine opcode: 0x02 (ObjCreate) or 0x03 (ObjCreateTeam)
    Ship *ship = CastToShipClass(obj);                  // IsA(0x8008)
    int opcode = 2;
    if (ship != NULL && IsLocalPlayerShip(ship)) {
        opcode = 3;                                     // 0x006a0392
    } else {
        opcode = 2;                                     // 0x006a039e
    }

    // Build response payload:
    //   [byte: opcode 0x02 or 0x03]
    //   [byte: playerSlot = GetPlayerSlotFromObjID(obj+4)]  (0x006a03ab → 0x006a19a0)
    //   [byte: ship->team_species (ship+0x2e4) — only when opcode==0x03]  (0x006a03b9)
    //   [... obj->WriteToStream(stream) via vtable[+0x10c] ...]  (0x006a03d4)

    msg = TGAlloc(0x40, "UNKNOWN");
    // ... payload assembly above ...
    msg->guaranteed = 1;                                // [msg+0x3a] = 1  (0x006a041a)
    msg->no_notify  = 0;                                // [msg+0x3d] = 0  (0x006a041e)
    TGNetwork__Send(network, nTargetID, msg, 0);        // unicast back to requestor  (0x006a0596)

    // Replay any pending explosion records if this is a DamageableObject
    if (dobj != NULL) {                                 // 0x006a042f: TEST EBX, EBX; JZ 0x006a043b
        DamageableObject__SendExplosions_0x29(dobj, nTargetID);
    }
}
```

### Response Format

The handler builds a standard `ObjCreate` or `ObjCreateTeam` message on the fly and sends it directly back to the requesting connection ID. The format is identical to how objects are sent during `NewPlayerInGame` (opcode 0x2A):

**Non-player objects (opcode 0x02):**
```
[0x02][byte: player_slot][... PhysicsObjectClass WriteToStream ...]
```

**Player ships (opcode 0x03):**
```
[0x03][byte: player_slot][byte: team_species (ship+0x2e4)][... PhysicsObjectClass WriteToStream ...]
```

The `WriteToStream` chain is:
```
ObjectClass -> PhysicsObjectClass -> DamageableObject -> Ship
```

This is exactly the same serialization used during initial object creation. See [`objcreate-serialization.md`](objcreate-serialization.md) for the byte-by-byte structure.

### C3 — `DAT_008e5c18` is FLT_MAX, not a low-HP threshold

[v5-validated 2026-05-28]

The pre-v5 doc described the 0x1E HP gate as "if HP < threshold return — too damaged". That reading is structurally backwards. The actual constant at `0x008e5c18` is FLT_MAX (`0x7F7FFFFF` = 3.4028235e+38).

Mechanism (confirmed via DamageableObject ctor at `FUN_00590cb0` and damage application at `FUN_00592c00`):

- The ctor initializes `dobj+0x14c = FLT_MAX` and `dobj+0x150 = 0` (alive).
- Damage application **decrements** `dobj+0x14c` from FLT_MAX as damage accumulates.
- On death, `dobj+0x14c` is reset to FLT_MAX simultaneously with `dobj+0x150 = 1` (dead flag).

The composite gate `(FLT_MAX <= dobj+0x14c) AND (dobj+0x150 == 0)` therefore succeeds **only when the object has never been damaged AND is alive**. Any non-zero accumulated damage makes the float strictly less than FLT_MAX; the FCOM at `0x006a034c` fails and the handler bails.

**OpenBC implication:** 0x1E does not re-send damaged objects. A late-joining client that requests an object via 0x1D / 0x1E will only receive a response if the host's copy is in pristine condition. If it has taken any damage, the request is silently dropped. This is a stricter gate than a "minimum HP threshold" reading would suggest, and modders that rely on RequestObj for late-join hydration of damaged objects will need to provide their own resync mechanism.

### DamageableObject__SendExplosions_0x29

After sending the object, the handler also replays any pending explosion events (the linked list at DamageableObject + `0x13c`). These are sent as individual `0x29` (Explosion) packets, one per explosion in the list (each carries a CompressedVector4 contact + two CF16 fields).

This ensures that if the client missed both the object creation AND its subsequent damage events, it gets a complete picture of the object's state including any in-flight explosions.

### GetPlayerSlotFromObjID

```c
int GetPlayerSlotFromObjID(int objID) {   // FUN_006a19a0
    return (int)(objID - 0x3FFFFFFF +
                 ((objID - 0x3FFFFFFF >> 31) & 0x3FFFF)) >> 18;
}
```

This is arithmetic right-shift with sign extension — correctly handles the base offset and extracts the player slot number. Matches the formula documented in [CLAUDE.md](../../CLAUDE.md) and in [`set-phaser-level-protocol.md`](set-phaser-level-protocol.md).

The inverse is at `0x006a7770` (`MakeObjIDFromPlayerSlot`): `*(int*)(this+0x10) = playerSlot * 0x40000 + 0x3FFFFFFF`. It is used at player-init time and is **not** called by the 0x1D / 0x1E / 0x1F triad — see C5 below.

---

## Opcode 0x1F — EnterSet (VERIFY_ENTER_SET_MESSAGE)

**Handler:** `MultiplayerGame__EnterSetHandler` @ `0x006a05e0`
**Python constant:** `App.VERIFY_ENTER_SET_MESSAGE`
**Direction:** Client → Host
**Event handler attribution corrected 2026-05-28**: There is NO EnterSet event handler at `0x006a0a20`. That address is the `MultiplayerGame__DisconnectHandler` stub (event 0x60003 ET_NETWORK_DISCONNECT, binding string at `0x0095a1f0`) — see `docs/networking/disconnect-flow.md` for the binding-table evidence chain. The original cited stub registered as "Enter game set" was a misattribution from the pre-v5 doc; no separate event handler is registered for the 0x1F EnterSet receive path beyond the dispatcher entry at `0x006a05e0`.

### Purpose

Sent by a client when its player ship is about to enter a new TGSet (i.e., a named scene region — the in-system-warp destination). The host verifies the object exists, then transitions that ship from its current set to the named destination set.

This is part of the in-system warp flow. When a player warps from one region (set) of the game map to another, the client fires this message to notify the host to perform the set transition server-side. All other clients see the ship "disappear" from one set and "appear" in another.

### Wire Format

```
[0x1F][int32: objectID][uint32: N][N bytes: setName]
```

[v5-validated 2026-05-28]

| Offset | Size       | Type      | Description                                                |
|--------|------------|-----------|------------------------------------------------------------|
| 0      | 1          | byte      | Opcode = 0x1F                                              |
| 1      | 4          | int32     | Object ID of the ship requesting transit                   |
| 5      | 4          | uint32 LE | Length of setName (call it N)                              |
| 9      | N          | bytes     | setName payload (raw, no null terminator on the wire)      |

Total: `9 + N` bytes.

### C1 — Length-prefixed string, NOT null-terminated

[v5-validated 2026-05-28]

The pre-v5 doc described the `setName` field as "null-terminated string" and described the read as `TGBufferStream__ReadString(stream, -1)`. That representation is wrong on the wire.

`TGBufferStream__ReadString_HeapAlloc` (FUN_006d2370) reads:

```c
iVar1 = (**(code **)(*param_1 + 0x68))();          // vtable+0x68 = ReadInt  -> length
if (iVar1 < 1) return 0;
uVar2 = FUN_00718cb0(iVar1);                        // heap-alloc length bytes
(**(code **)(*param_1 + 0x10))(uVar2, iVar1);       // vtable+0x10 = ReadBytes raw payload
return uVar2;
```

Symmetric on send via `TGBufferStream__WriteString_LenPrefixed` (FUN_006d23c0):

```c
// strlen via DO-WHILE-NULL loop
(**(code **)(*param_1 + 0x6c))(~uVar2);             // vtable+0x6c = WriteInt  -> length prefix
(**(code **)(*param_1 + 0x14))(param_2, ~uVar2);    // vtable+0x14 = WriteBytes raw payload
```

The heap-alloc length matches the wire-prefix exactly (no off-by-one for a null terminator). For OpenBC: encode `setName` with a 4-byte little-endian length prefix followed by exactly that many bytes — no trailing NUL.

This is consistent with the wider TGBufferStream cursor-vtable layout (vtable @ `0x00895C58`, slots +0x10 ReadBytes / +0x14 WriteBytes / +0x68 ReadInt / +0x6c WriteInt). See [`stream-primitives.md`](stream-primitives.md).

### Handler Behavior

```c
void MultiplayerGame__EnterSetHandler(void *stream_msg) {
    int objectID  = TGBufferStream__ReadInt(stream);
    char *setName = TGBufferStream__ReadString_HeapAlloc(stream, -1);    // length-prefixed read

    int *obj = TGSceneGraph__GetObjectByID(NULL, objectID);    // factory 0x8003

    if (obj == NULL) {
        // Object not found — relay [0x1E][int32: objectID] to host (target=0)
        // Same fallback pattern as ObjNotFound (msg+0x3a = 1, guaranteed)
        TGNetwork__Send(network, 0, msg, 0);
        goto cleanup;
    }

    Ship *ship = CastToShipClass(obj);                    // IsA(0x8008)
    if (ship == NULL) goto cleanup;
    if (ship+0x2d0 == NULL) goto cleanup;                 // No warp engine subsystem
    if (*(int*)(ship+0x2d0 + 0xb4) != 0) goto cleanup;    // Already in transit

    // Look up the destination set by name (binary search)
    int setIndex = TGSetManager__FindSetIndexByName(&DAT_0097e9c8, setName);    // FUN_004055a0
    TGSet *destSet = (setIndex >= 0) ? DAT_0097e9c8[setIndex] : NULL;

    TGSet *currentSet = (TGSet*)ship[8];   // ship->currentSet at +0x20

    if (currentSet != destSet) {
        // Notify current set of departure: vtable+0x58 (slot 22) = ExitSet
        if (currentSet != NULL) {
            (*currentSet->vtable[+0x58])(ship+4);          // arg = obj ID
        }
        // Notify destination set of arrival: vtable+0x54 (slot 21) = EnterSet
        (*destSet->vtable[+0x54])(ship, ship+0x28);        // args = (ship, placement)
    }

cleanup:
    NiFree(setName);    // FUN_00718cf0 -> FUN_00717960
}
```

### C2 — `DAT_008d8ab8` is the literal string `"warp"`, not a "default space combat set name"

[v5-validated 2026-05-28]

The pre-v5 doc claimed `0x008d8ab8` was "the name of the default space combat set". Reading the memory directly:

```
0x008d8ab8: 77 61 72 70 00 00 00 00  53 68 69 70 43 6c 61 73    "warp\0\0\0\0ShipClas"
0x008d8ac8: 73 00 00 00 43 72 65 61  74 65 53 68 69 70 00 00    "s\0\0\0CreateShip\0\0"
```

The literal 5 bytes are `"warp\0"`. The next string in the rdata block is `"ShipClass"`, not `"DeleteAllMissionTimers"` as the pre-v5 doc claimed appears immediately after.

The constant is used by the client-side sender (`MultiplayerGame__RequestObjEventHandler` @ `0x006a07d0`) as a gate: when a ship's set membership changes while in warp, the sender compares `currentSetName` against `"warp"` with `strcmp`. The semantic is:

- The ship's `currentSet` named `"warp"` is the **warp tunnel** itself (the synthetic in-transit container).
- 0x1F is emitted when the ship is in warp but its `currentSet` name is **NOT** `"warp"` — i.e., during the warp transition into a named destination sub-set (e.g., `"Multi1"`, `"Multi2"`).
- During in-tunnel transit (`currentSetName == "warp"`), no 0x1F is sent — no notification is needed while the ship is mid-warp.

So 0x1F is fundamentally a "ship-leaving-warp-tunnel-into-named-set" notification, not a "leaving the default combat space" notification.

### Set Transition Logic

The vtable calls in the EnterSet handler correspond to TGSet methods at byte offsets:

- `vtable[+0x58]` (slot 22) = `ExitSet` — called on the ship's CURRENT set to notify departure; arg = ship object ID (`ship+4`).
- `vtable[+0x54]` (slot 21) = `EnterSet` — called on the DESTINATION set to notify arrival; args = `(ship, ship->placement at ship+0x28)`.

The notation `vtable[+0x58]` is the byte-offset form used elsewhere in this doc family (e.g., `WriteToStream` at `vtable[+0x10c]` in the 0x1E handler). The pre-v5 doc used a `vtable[0x58/4]` form for the same slot — both refer to the same address, the byte-offset form is preferred for cross-doc consistency.

### Who Sends 0x1F — The RequestObjEventHandler Path

[v5-validated 2026-05-28]

`MultiplayerGame__RequestObjEventHandler` @ `0x006a07d0` is the **client-side sender** for both 0x1D and 0x1F:

```c
// Triggered by an internal event when a local physics object changes set
void RequestObjEventHandler(int event_param) {
    if (!IsMultiplayer) return;

    Ship *obj = CastToShipClass(*(event_param + 0x0C));    // get ship from event
    if (obj == NULL || obj+0xec == 0) return;              // must be a networked ship

    if (obj+0x2d0 == NULL || *(obj+0x2d0 + 0xb4) == 0) {
        // Ship is NOT in warp (no warp subsystem OR subsystem-flag clear)
        // -> Send ObjNotFound (0x1D) to "NoMe" (all peers except self)
        WriteByte(stream, 0x1D);
        WriteInt(stream, obj+4);                           // ship object ID
        TGNetwork__SendTGMsgToGroupByName(network, "NoMe", msg);  // DAT_008e5528
    } else {
        // Ship IS in warp — check current set name vs "warp" tunnel sentinel
        char *currentSetName = *(char**)(obj[8] + 0x74);   // set+0x74 = name ptr
        if (strcmp(currentSetName, "warp") != 0) {          // DAT_008d8ab8 = "warp\0"
            // Sub-set transition (e.g., "Multi1") — emit 0x1F
            WriteByte(stream, 0x1F);
            WriteInt(stream, obj+4);
            WriteString_LenPrefixed(stream, currentSetName);
            TGNetwork__SendTGMsgToGroupByName(network, "NoMe", msg);
        }
        // If in-tunnel ("warp"), nothing sent — no notification needed during transit
    }
}
```

Routing summary (sender side):

| Sender condition | Opcode | Target | Why |
|------------------|--------|--------|-----|
| Ship NOT in warp | 0x1D | `"NoMe"` group | Ship's set membership changed unexpectedly — peers should reconcile |
| Ship IN warp AND currentSet name != `"warp"` | 0x1F | `"NoMe"` group | Ship arrived in a named warp-destination sub-set — notify peers |
| Ship IN warp AND currentSet name == `"warp"` | (none) | — | Mid-tunnel; no transition to report |

The `"NoMe"` group string is at `0x008e5528`. Note that the receiver-side NULL-found fallback inside `MultiplayerGame__EnterSetHandler` still targets host(0) — that fallback path is distinct from this sender's broadcast pattern.

---

## Relationship Between the Three Opcodes

```
CLIENT                                  HOST
  |                                       |
  | [receives msg with unknown objID]     |
  | --> 0x1D ObjNotFound(objID) --------> |
  |                                       | [if also missing: relay 0x1E to host(0)]
  |                                       | [if found AND undamaged AND alive: build ObjCreate]
  | <-- 0x1E ObjCreate(0x02 | 0x03) ----- |
  |     + any 0x29 explosion replays      |
  |                                       |
  | [ship leaves warp tunnel into "Multi1"]|
  | --> 0x1F EnterSet(objID,"Multi1") --> |
  |                                       | [host: move ship from current->dest set via]
  |                                       | [     ExitSet (vtable+0x58) + EnterSet (vtable+0x54)]
```

The three opcodes form a recovery and synchronization path:
1. **0x1D** — "I'm missing an object you referenced"
2. **0x1E** — "Here is the full state of that object" (plus explosion history) — gated on undamaged + alive
3. **0x1F** — "My ship is entering a new sub-region"

---

## Critical Correction: Function Address Map

[v5-validated 2026-05-28]

Two address rows in the pre-v5 doc's Function Addresses table were misattributed. Resolution:

### C4 — `GetPlayerSlotFromObjID` lives at `0x006a19a0`, not `0x005a2030`

Pre-v5 doc claimed `0x005a2030 | GetPlayerSlotFromObjID`. Binary truth:

- **`0x005a2030`** is `ShipReadSpecies` — a two-vtable-call ship-setup function that reads a species value into `ship+0xEC`. It is unrelated to player-slot extraction. (This resolves [v5-validation-status.md](v5-validation-status.md) §4 #1 — the cross-doc disagreement between this leaf and `objcreate-serialization.md`. Binary authority sides with `objcreate-serialization.md`: `0x005a2030` is `ShipReadSpecies`.)
- **`0x006a19a0`** is the actual `GetPlayerSlotFromObjID`. The bit-twiddle formula `(objID - 0x3FFFFFFF + ((objID - 0x3FFFFFFF >> 31) & 0x3FFFF)) >> 18` matches the body cited above. The 0x1E handler calls this address via `CALL 0x006a19a0` at `0x006a03ab`.

### C5 — `0x006a7770` is `MakeObjIDFromPlayerSlot` (the INVERSE), not called by the triad

Pre-v5 doc labeled `0x006a7770` as `MultiplayerGame__GetPlayerSlotFromObjID`. Binary truth:

```c
// FUN_006a7770 - MakeObjIDFromPlayerSlot
void MakeObjIDFromPlayerSlot(int *this, int playerSlot) {
    *(int *)(this + 0x10) = playerSlot * 0x40000 + 0x3FFFFFFF;
}
```

The function constructs an obj ID **from** a player slot (multiplies by `0x40000 = 2^18`, adds the `0x3FFFFFFF` base). It is used in player-init context and is NOT called by the 0x1D / 0x1E / 0x1F triad. The 0x1E handler's `playerSlot` write at `0x006a03ab` targets `0x006a19a0`, never `0x006a7770`.

---

## OpenBC Implementation Notes

### ObjNotFound (0x1D)
- Parse: skip opcode byte + read 4-byte objectID.
- On receive: look up the object locally. If found, send a full ObjCreate (0x02 or 0x03) packet back to the sender (unicast, guaranteed).
- If also not found locally: relay a `[0x1E][int32: objectID]` to upstream/host (target=0), guaranteed. On a single-host topology this is a no-op.

### RequestObj (0x1E)
- Parse: skip opcode byte + read 4-byte objectID.
- On receive (host only): look up the object via PhysicsObjectClass factory (IsA 0x8006).
  - If not found, drop silently.
  - If found, gate on: object must be networked (`obj+0xec != 0`).
  - **(C3)** If the object IsA DamageableObject (0x8007), gate further on `dobj+0x14c == FLT_MAX` (never damaged) AND `dobj+0x150 == 0` (alive). Damaged objects are silently dropped — this is stock behavior.
  - **(Clar2)** Select opcode 0x03 if the ship has a non-zero team id (`ship+0x2e4 != 0`) — on a host, this is the practical heuristic. Otherwise 0x02.
  - Build the response payload: opcode byte, playerSlot (via `GetPlayerSlotFromObjID(obj+4)` formula), team byte (only for 0x03), then `obj->WriteToStream(stream)` via the same `vtable[+0x10c]` chain as ObjCreate.
  - Send to the requesting connection ID only (NOT broadcast). Guaranteed + no-notify.
  - Replay any pending explosion events (the linked list at `dobj+0x13c`) as individual 0x29 packets.

### EnterSet (0x1F)
- Parse: skip opcode byte + read 4-byte objectID + read length-prefixed string (uint32 LE length, then exactly N bytes — **no trailing NUL on the wire**).
- On receive (host): look up ship by objectID via TGSceneGraph factory (IsA 0x8003).
  - If not found: relay `[0x1E][int32: objectID]` to host(0), guaranteed.
  - If found: validate ship has warp engine (`ship+0x2d0 != 0`) and is not already in transit (`*(ship+0x2d0+0xb4) == 0`).
  - Look up destination set by name in TGSetManager (binary search, `FUN_004055a0`).
  - If ship is already in dest set, no-op.
  - Otherwise: call `ExitSet` on current set (`vtable[+0x58]`, arg = object ID), then `EnterSet` on dest set (`vtable[+0x54]`, args = (ship, placement)).
- Free the heap-allocated setName before return (`NiFree`, `FUN_00718cf0` -> `FUN_00717960`).
- Guaranteed delivery: yes (warp transition is critical state).

### Set Name Context (corrected)
- **(C2)** The set name `"warp"` (at `0x008d8ab8`) is the in-warp-tunnel sentinel — the synthetic set a ship occupies while mid-transit.
- 0x1F is emitted by clients when their ship moves between named sub-sets during a warp transition (e.g., into `"Multi1"` or `"Multi2"`).
- When a ship is in the `"warp"` tunnel, no 0x1F is sent — only on entry into a named destination set.

---

## Function Addresses

[v5-validated 2026-05-28]

| Address    | Function                                                                  |
|------------|---------------------------------------------------------------------------|
| 0x0069F2A0 | `MpgameHandleMessage` (dispatcher for opcodes 0x02-0x2A)                  |
| 0x0069F534 | MultiplayerGame jump table (41 entries, opcode-2 indexed)                 |
| 0x006a0490 | `MultiplayerGame__ObjNotFoundHandler` (opcode 0x1D)                       |
| 0x006a02a0 | `MultiplayerGame__RequestObjHandler` (opcode 0x1E)                        |
| 0x006a05e0 | `MultiplayerGame__EnterSetHandler` (opcode 0x1F)                          |
| 0x006a07d0 | `MultiplayerGame__RequestObjEventHandler` (client-side sender for 0x1D / 0x1F) — **renamed 2026-05-28**: SWIG plate is `MultiplayerGame__EnterSetHandler` per FUN_0069efe0 binding (string at 0x0095a0a8); dual-opcode behavior unchanged |
| 0x006a0a20 | `MultiplayerGame__EnterSetEventHandler` (stub, single RET) — **renamed 2026-05-28**: actually `MultiplayerGame__DisconnectHandler` stub (event 0x60003 ET_NETWORK_DISCONNECT, binding string at 0x0095a1f0); empty in MP because cleanup runs via transport layer — see `docs/networking/disconnect-flow.md` |
| 0x006a19a0 | `GetPlayerSlotFromObjID` **(C4 — corrected; was 0x005a2030)**             |
| 0x006a7770 | `MakeObjIDFromPlayerSlot` (INVERSE; **not called by the triad**, C5)      |
| 0x00434e00 | `TGSceneGraph__GetObjectByID` (factory IsA 0x8003)                        |
| 0x0059fc60 | `PhysicsObjectClass__FindByObjectID` (factory IsA 0x8006)                 |
| 0x00590b20 | `CastToDamageableObject` (IsA 0x8007)                                     |
| 0x005ab670 | `CastToShipClass` (IsA 0x8008)                                            |
| 0x005ae140 | `IsLocalPlayerShip` (host-mode dual — Clar2)                              |
| 0x00590cb0 | `DamageableObject` ctor (initializes `+0x14c = FLT_MAX`, `+0x150 = 0`)    |
| 0x00592c00 | DamageableObject damage application (decrements `+0x14c`)                 |
| 0x00595c60 | `DamageableObject__SendExplosions_0x29` (walks list at `+0x13c`)          |
| 0x004055a0 | `TGSetManager__FindSetIndexByName` (binary search)                        |
| 0x006d2370 | `TGBufferStream__ReadString_HeapAlloc` (length-prefixed; C1)              |
| 0x006d23c0 | `TGBufferStream__WriteString_LenPrefixed` (length-prefixed; C1)           |
| 0x006d6200 | `TGFactory_DeserializeObject` (**NOT called by the triad** — Clar1)       |

### Data anchors

| Address    | Symbol                       | Value / Description                                                              |
|------------|------------------------------|----------------------------------------------------------------------------------|
| 0x00895C58 | TGBufferStream cursor vtable | slots +0x10 ReadBytes, +0x14 WriteBytes, +0x68 ReadInt, +0x6c WriteInt           |
| 0x0097fa78 | TGNetwork singleton          | UtopiaModule+0x78 (engine cross-anchor)                                          |
| 0x0097e9c8 | TGSetManager array head      | in-game set table, binary-searched by FindSetIndexByName                         |
| 0x008d8ab8 | `"warp\0"` (5 bytes, C2)     | in-warp-tunnel set-name sentinel (NOT "default space combat set")                |
| 0x008e5c18 | float `FLT_MAX` (C3)         | DamageableObject undamaged sentinel (`0x7F7FFFFF` = 3.4028235e+38)               |
| 0x008e5528 | `"NoMe"`                     | sender's relay group (all peers except self)                                     |
| 0x008d858c | `"UNKNOWN"`                  | LITERAL class name for generic-pool TGMessage allocation (R2 — not a placeholder) |

### TGFactory class IDs used by the triad

| Class ID | Cast helper              | Used by                                  |
|----------|--------------------------|------------------------------------------|
| 0x8003   | TGSceneGraph__GetObjectByID | 0x1F object lookup                    |
| 0x8006   | PhysicsObjectClass__FindByObjectID | 0x1E object lookup            |
| 0x8007   | CastToDamageableObject   | 0x1E explosion-replay gate               |
| 0x8008   | CastToShipClass          | 0x1E opcode (0x02 vs 0x03) selection; 0x1F ship lookup |

Cross-reference these against [`docs/engine/rtti-class-catalog.md`](../engine/rtti-class-catalog.md) for the canonical class-name mappings (currently open — see Open Questions).

---

## Open Questions

- ~~SWIG registration string for the empty stub at `0x006a0a20`~~ **CLOSED 2026-05-28** via networking leaf #10 (disconnect-flow): `FUN_0069efe0` binds `0x006a0a20` to string at `0x0095a1f0` = `"MultiplayerGame :: DisconnectHandler"` (registered for event 0x60003 ET_NETWORK_DISCONNECT, empty in MP because real cleanup runs via transport layer). The original "Enter game set" attribution was wrong; see `docs/networking/disconnect-flow.md` for evidence.
- Class-ID table cross-reference: confirm the IsA tags `0x8003` / `0x8006` / `0x8007` / `0x8008` map to canonical names (likely `TGSceneGraph-anchored object` / `PhysicsObjectClass` / `DamageableObject` / `ShipClass`) against [`docs/engine/rtti-class-catalog.md`](../engine/rtti-class-catalog.md). The triad provides independent confirmation that these IDs partition the cast hierarchy, but the catalog mapping is still pending.
- `MultiplayerGame__EnterSetHandler` (0x006a05e0) calls `TGBufferStream__ReadString_HeapAlloc(stream, -1)` while the sender path `MultiplayerGame__RequestObjEventHandler` (0x006a07d0) writes via `WriteString` (vtable+0x6c + vtable+0x14). Verified that both encodings are symmetric — both length-prefixed — but the call shape differs at the source level. The reason for the helper-vs-vtable-direct asymmetry has not been investigated.

---

## Related Documents

- [wire-format-spec.md](wire-format-spec.md) — Hub: summary opcode tables. The triad rows (0x1D / 0x1E / 0x1F) should be cross-checked against this leaf for the string-encoding correction (C1).
- [game-opcodes.md](game-opcodes.md) — Full game opcode reference; opcode 0x1F wire-format row needs the length-prefix correction (C1) at family close.
- [objcreate-serialization.md](objcreate-serialization.md) — Full ObjCreate (0x02 / 0x03) chain, which is the response payload for 0x1E. Authoritative on `FUN_005a2030 = ShipReadSpecies` (resolves §4 #1).
- [object-replication.md](object-replication.md) — Thin index for the ObjCreate handler `FUN_0069f620`; same `WriteToStream` chain via `vtable[+0x10c]`.
- [stream-primitives.md](stream-primitives.md) — TGBufferStream layout, including the cursor vtable at `0x00895C58` (+0x68 ReadInt, +0x6c WriteInt, +0x10 ReadBytes, +0x14 WriteBytes).
- [cf16-explosion-encoding.md](cf16-explosion-encoding.md) — Opcode 0x29 wire format (the explosion-replay packets emitted by `DamageableObject__SendExplosions_0x29`).
- [delete-player-ui-wire-format.md](delete-player-ui-wire-format.md) — Sibling leaf documenting the TGFactory-based deserialization path that the triad explicitly bypasses (Clar1 contrast).
- [transport-layer.md](transport-layer.md) — TGMessage layout for the `+0x3a` guaranteed flag and `+0x3d` no-notify flag set by 0x1D / 0x1E.
- [v5-validation-status.md](v5-validation-status.md) — Protocol-family campaign tracker; this leaf is row #18.
