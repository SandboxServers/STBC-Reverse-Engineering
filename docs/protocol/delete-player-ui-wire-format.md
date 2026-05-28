> [docs](../README.md) / [protocol](README.md) / delete-player-ui-wire-format.md

---
title: DeletePlayerUI Wire Format (Opcode 0x17)
type: reference
audience: re-engineer
validated: 2026-05-28
methodology: FUNCTION_DOC_WORKFLOW_V5
binary:
  name: STBC.exe
  size: 6394712
  base: 0x00400000
status: partial
evidence:
  - claim: "Opcode 0x17 dispatches to DeletePlayerUIHandler (receiver) on the client"
    address: 0x006a1360
    function: FUN_006A1360
    completeness: high
    confidence: high
  - claim: "Disconnect-side 0x17 sender is FUN_006b75b0 inside TGWinsockNetwork (posts a 0x866 event with event_code 0x00060005 — wire send is performed by LAB_0x006a1590 when the event fires)"
    address: 0x006b75b0
    function: FUN_006B75B0
    completeness: high
    confidence: high
    note: "Corrects pre-v5 claim that FUN_006a0ca0 sends opcode 0x17. FUN_006a0ca0 writes byte 0x18 at offset 166 (`C6 44 24 48 18`) — it sends DeletePlayerAnim, not DeletePlayerUI."
  - claim: "Event-fired wire-send handler LAB_0x006a1590 writes opcode 0x17 and serializes the 0x866 event to a TGBufferStream"
    address: 0x006a1590
    function: LAB_0x006a1590
    completeness: high
    confidence: high
    note: "LAB_ only — no Ghidra function body in DB. Disasm at 0x006a15d4 shows `MOV [ESP+0x40], 0x17` then a Save call through event->vtable+0x34."
  - claim: "Class 0x866 is a TGEvent SUBCLASS (size 0x2C), not base TGEvent (size 0x28)"
    address: 0x00895848
    function: vtable_class_0x866
    completeness: high
    confidence: high
    note: "Base TGEvent vtable is at 0x00895FF4. Subclass 0x866 vtable at 0x00895848 is one slot larger; subclass adds a 1-byte wire_peer_id field at +0x28."
  - claim: "Class 0x866 is registered in the TGFactory registry (DAT_0099a578 / DAT_0099a584), not the NiRTTI registry"
    address: 0x006b27a3
    function: FUN_006B2670
    completeness: high
    confidence: high
    note: "Resolves the long-standing wire-format-spec.md OQ #2 (factory 0x866 catalog gap). The TGFactory registry is a second class registry separate from NiRTTI; class IDs in the 0x801 / 0x86x range live here exclusively."
  - claim: "GetTypeID for class 0x866 returns 0x866 via `MOV EAX, 0x866; RET`"
    address: 0x006b3700
    function: Class_0x866_GetTypeID
    completeness: high
    confidence: high
  - claim: "Class 0x866 Save (vtable+0x34) at 0x006bb890 writes class_id + event_code + src_obj_id + dst_obj_id + wire_peer_id"
    address: 0x006bb890
    function: Class_0x866_Save
    completeness: high
    confidence: high
  - claim: "Class 0x866 Read (vtable+0x38) at 0x006bb8b0 reads the same 5 fields from the stream"
    address: 0x006bb8b0
    function: Class_0x866_Read
    completeness: high
    confidence: high
  - claim: "TGFactory_DeserializeObject reads class_id u32 via stream->vtable+0x60, calls TGFactoryCreate(class_id, 0), then dispatches event->vtable+0x38 (Read)"
    address: 0x006d6200
    function: TGFactory_DeserializeObject
    completeness: high
    confidence: high
  - claim: "src_obj_id (event+0x8) is ALWAYS 0x00000000 via this code path — no producer writes it"
    address: null
    function: FUN_006D5C00
    completeness: high
    confidence: high
    note: "Negative claim: base TGEvent ctor at 0x006d5c00 initializes event+0x8 to 0; no xrefs to 0x866 producer paths write that slot before posting."
  - claim: "dst_obj_id (event+0xC) is the TGWinsockNetwork singleton's internal object handle — NOT a ship or player ID"
    address: 0x006d62b0
    function: FUN_006D62B0
    completeness: high
    confidence: high
    note: "Corrects pre-v5 claim that tgt_obj_id is a ship/player object. The decompile shows FUN_006d62b0 called with `this = TGWinsockNetwork singleton` and writes the singleton's handle into event+0xC. Stock trace value 0x0000064F is the network singleton handle for that session, not a ship ID."
  - claim: "wire_peer_id (event+0x28) is written by stream->vtable+0x54 (WriteByte 1B) — the SUBCLASS-only field that distinguishes 0x866 from base TGEvent"
    address: 0x006bb890
    function: Class_0x866_Save
    completeness: high
    confidence: high
  - claim: "EventManager singleton at 0x0097F838; registry walked by dispatch at singleton+0x2C = 0x0097F864"
    address: 0x0097F838
    function: TGEventManager_singleton
    completeness: high
    confidence: high
    note: "Cross-anchor with engine event-system-architecture.md and protocol leaf #15 (collision-effect-protocol.md). +0x2C is the registry table; 0x0097F864 is the same singleton's registry-table offset, not a separate global."
  - claim: "Event dispatch loop FUN_006da300 reads event->dest->vtable+0x50 first, then walks the EventManager registry at 0x97F864"
    address: 0x006da300
    function: FUN_006DA300
    completeness: high
    confidence: high
  - claim: "Both functions named `NewPlayerInGameHandler` (LAB_0x006a1590 and FUN_006a1e70) share the same SWIG name `MultiplayerGame :: NewPlayerInGameHandler` — FUN_0069efe0 registers BOTH against the same string at 0x0095a028"
    address: 0x0069efe0
    function: FUN_0069EFE0
    completeness: high
    confidence: high
    note: "LAB_0x006a1590 = event-fired wire-send handler (no function body in DB). FUN_006a1e70 = opcode 0x2A wire receiver. Naming collision is by design — both register through the same SWIG registration table builder."
  - claim: "S->C only: 7 instances/session observed across audits; 0 C->S, 7 S->C"
    address: null
    function: FUN_006A1360
    completeness: high
    confidence: medium
    note: "Per relay-audit-20260224 and Valentine's Day 33.5-min battle trace (6 instances, all join-time). Disconnect-time 0x17 unobserved in available traces because no trace captured a multi-client session with a disconnecting client AND remaining receivers."
companions:
  - docs/protocol/wire-format-spec.md
  - docs/protocol/game-opcodes.md
  - docs/protocol/tgmessage-routing.md
  - docs/protocol/transport-layer.md
  - docs/protocol/tgobjptrevent-class.md
  - docs/engine/event-system-architecture.md
  - docs/protocol/v5-validation-status.md
supersedes:
  - 2026-02-21
---

# DeletePlayerUI (Opcode 0x17) Wire Format

> [!NOTE]
> This doc is `status: partial`. The opcode 0x17 receiver (FUN_006A1360), TGEvent-family transport architecture, and authority semantics (S->C only) are v5-validated. **MAJOR ARCHITECTURAL DISCOVERY this pass: stbc.exe has TWO independent class registries** — the standard NiRTTI catalog (0x02 / 0x101 / 0x105 / 0x10C / 0x8124 / 0x8129) and a separate **TGFactory registry** at `DAT_0099a578` / `DAT_0099a584` used exclusively by `TGFactory_DeserializeObject`. Class ID 0x866 (used by this opcode) lives in the TGFactory registry; this resolves the long-standing wire-format-spec.md OQ #2. Three corrections: **(C1)** `FUN_006a0ca0` sends opcode 0x18 (DeletePlayerAnim), NOT 0x17 — the actual 0x17 disconnect-side sender is `FUN_006b75b0`. **(C2)** 0x866 is a TGEvent SUBCLASS (vtable 0x00895848, size 0x2C), not base TGEvent. **(C3)** `tgt_obj_id` is the TGWinsockNetwork singleton's internal object handle, not a ship/player ID. Plus 4 clarifications including the `NewPlayerInGameHandler` LAB_ vs function-name collision. See [docs/guides/v5-evidence-header.md](../guides/v5-evidence-header.md) for the standard.

---

## Overview

Opcode 0x17 ("DeletePlayerUI") is a **generic player-list-update event transport** that carries a serialized TGEvent-family object to the client's engine event system. Despite its name, it is used for **both** player addition (at join time) and player removal (at disconnect time).

The handler at `FUN_006A1360` deserializes a 0x866 event from the wire using `TGFactory_DeserializeObject` (0x006D6200) — which looks up class ID 0x866 in the **TGFactory** registry (not NiRTTI) — and posts it through the global event manager. The handler registered for `ET_NEW_PLAYER_IN_GAME` / `0x008000F1` (event-fired wire-send handler `LAB_0x006a1590`) is what writes the opcode-17 byte on the sender side.

---

## Two-Registry Architecture

> [!IMPORTANT]
> This section is the load-bearing resolution for [wire-format-spec.md](wire-format-spec.md) OQ #2 (factory 0x866 catalog gap) and is shared anchor material for every protocol doc that references factory IDs in the 0x801 / 0x86x range.

stbc.exe has **TWO independent class registries** that coexist. Prior validation passes that searched only the NiRTTI catalog for class IDs in the 0x86x range came up empty — those classes live in the second registry.

| Registry | Backing table | Registered via | Class IDs (catalog) | Used by |
|----------|---------------|----------------|---------------------|---------|
| **NiRTTI** | NiRTTI factory globals (engine-side) | `NiRTTI_*` factory paths | 0x02, 0x101, 0x105, 0x10C, 0x8124, 0x8129 | engine's standard RTTI lookup; most NI classes |
| **TGFactory** | `DAT_0099a578` (table) + `DAT_0099a584` (count) | `FUN_006B2670` and siblings | 0x801, 0x86x range (includes 0x865 / 0x866 / 0x867) | `TGFactory_DeserializeObject` (0x006D6200) **exclusively** |

The handler chain confirms the registry split. `TGFactory_DeserializeObject` at 0x006D6200 reads a class_id u32 from the stream, then calls `TGFactoryCreate(class_id, 0)` which consults the TGFactory registry — not NiRTTI. The 0x866 class is registered at `0x006b27a3` inside `FUN_006B2670` against the TGFactory table; the NiRTTI catalog has no entry for it.

**Implication for OpenBC and future validations:** when a class ID isn't found in the NiRTTI catalog, check the TGFactory registry. Several prior cross-doc disagreements (wire-format-spec.md OQ #2; the "where does 0x866 live?" thread) trace to this missing branch in the search procedure. The TGFactory registry currently has confirmed entries for **0x801, 0x865, 0x866, 0x867** — full enumeration is an open question for a downstream pass.

### TGEvent class family — the 0x86x cluster

All three confirmed 0x86x-cluster classes derive from base TGEvent (vtable 0x00895FF4, size 0x28).

| Class ID | Vtable | Size | Use |
|----------|--------|------|-----|
| 0x865 | 0x0089580C | 0x2C | Unknown — sibling (no protocol doc covers it yet) |
| **0x866** | **0x00895848** | **0x2C** | DeletePlayerUI / NewPlayerInGame / DeletePlayer events (opcode 0x17) |
| 0x867 | 0x00895884 | 0x30 | Unknown — sibling with 4 extra bytes |

Each subclass extends base TGEvent (size 0x28) by 4 bytes (size 0x2C for 0x865/0x866; size 0x30 for 0x867). For 0x866, the extra slot at +0x28 is `wire_peer_id` (1 byte; the rest is padding in memory). Base TGEvent is not on the wire by itself — it's always serialized through a concrete subclass.

---

## Wire Format

```
Offset  Size  Type     Field           Notes
------  ----  ----     -----           -----
0       1     u8       opcode          Always 0x17
1       4     u32le    class_id        TGFactory class ID (0x00000866)
5       4     u32le    event_code      Event type code (see below)
9       4     u32le    src_obj_id      Always 0x00000000 via this code path
13      4     u32le    dst_obj_id      TGWinsockNetwork singleton handle (NOT ship/player)
17      1     u8       wire_peer_id    Subscriber's wire peer slot (1-based)
```

**Total**: 18 bytes (1 opcode + 17 payload).

### Per-byte sender-side sourcing

[v5-validated 2026-05-28]

| Bytes | Field | Sender-side source |
|-------|-------|--------------------|
| 0 | `opcode 0x17` | Written by `LAB_0x006a1590` at `0x006a15d4`: `MOV [ESP+0x40], 0x17` |
| 1-4 | `class_id` | `base->Save` calls `this->GetTypeID` via vtable+0x4 → 0x866; written by `stream->vtable+0x64` (`WriteInt`, 4 raw bytes) |
| 5-8 | `event_code` | `event+0x10`; written by `stream->vtable+0x64` (`WriteInt`) |
| 9-12 | `src_obj_id` | `event+0x8`; written by `stream->vtable+0x84` (`WriteObjectRef`); **always 0x00000000** through this path |
| 13-16 | `dst_obj_id` | `event+0xC`; written by `stream->vtable+0x84` (`WriteObjectRef`); set by `FUN_006d62b0(this=TGWinsockNetwork)` — wire value is the network singleton's internal object handle |
| 17 | `wire_peer_id` | `event+0x28`; written by `stream->vtable+0x54` (`WriteByte`); subscriber's wire peer slot |

### Event codes

| Context | Event code | Constant | Effect |
|---------|-----------|----------|--------|
| Player join | `0x008000F1` | `ET_NEW_PLAYER_IN_GAME` | Adds player to TGPlayerList |
| Player disconnect | `0x00060005` | `ET_NETWORK_DELETE_PLAYER` | Removes player from TGPlayerList |

The same handler (`LAB_0x006a1590`) is registered for both event codes — it dispatches on `event_code` internally to decide add vs. remove.

### Object-reference semantics

- `src_obj_id` is **always 0**: no producer in the binary writes a non-zero value through this code path. Pre-v5 wording said "typically 0" — that's strictly "always 0" for opcode 0x17.
- `dst_obj_id` is **the network singleton's internal handle**, not a ship or player ID. The handle value depends on session state and is set by `FUN_006d62b0(this=TGWinsockNetwork singleton)`. Stock trace `0x0000064F` is a network context value, not a player object ID.

---

## Handler Chain

### Receiving (client side)

[v5-validated 2026-05-28]

```
FUN_006A1360 (opcode 0x17 receiver — DeletePlayerUIHandler)
  │
  ├── TGBufferStream_swig_Ctor + OpenBuffer skipping the opcode byte (pvVar1+1, size-1)
  │
  ├── TGFactory_DeserializeObject (0x006D6200)
  │     ├── Reads class_id u32 via stream->vtable+0x60
  │     ├── TGFactoryCreate(0x866, 0) — looks up class in TGFactory registry (NOT NiRTTI)
  │     │     and constructs a 0x2C-byte 0x866 event
  │     └── event->vtable+0x38 (Read) at 0x006bb8b0 — reads event_code / src / dst / peer_id
  │
  ├── FUN_006F13C0 — post-deserialize fixup (calls vtable+0x18, then vtable+0x1C)
  │
  ├── FUN_006d62b0(this=TGWinsockNetwork) — sets event+0xC = local network ctx
  │
  ├── event+0x24 = 0 (clears unknown field)
  │
  └── FUN_006DA300(0x97F838, event) — dispatches event:
        ├── first via event->dest->vtable+0x50
        └── then walks EventManager registry at 0x97F864 (this+0x2C in FUN_006DA300)
              │
              └── Registered handler LAB_0x006a1590 fires:
                    ├── [if ET_NEW_PLAYER_IN_GAME (0x008000F1)]
                    │     → adds player to TGPlayerList
                    └── [if ET_NETWORK_DELETE_PLAYER (0x00060005)]
                          → removes player from TGPlayerList
                          → Python RebuildPlayerList()
```

On the client, the `LAB_0x006a1590` handler runs but the wire-send path (`NoMe` / `Forward` group send) is a no-op — those groups are empty on a client.

### Sending (server side)

[v5-validated 2026-05-28]

**At join time**: opcode 0x2A (`NewPlayerInGame`) arrives at the server. Handler `FUN_006a1e70` processes the wire bytes, then constructs a 0x866 event:

```
ship = TGAlloc(0x2C)
FUN_006bb840(ship)             ; sets vtable = 0x00895848 (class 0x866)
event+0x10 = 0x008000F1        ; ET_NEW_PLAYER_IN_GAME
event+0x28 = wire_peer_id      ; joining player's slot
FUN_006d62b0(this=network)     ; event+0xC = network singleton handle
TGEventManager__PostEvent      ; FUN_006da2a0 → FUN_006da300
  → walks registry at 0x0097F864
  → fires LAB_0x006a1590       ; writes opcode 0x17, serializes event, sends TGMessage
```

**At disconnect time**: `FUN_006b75b0` inside `TGWinsockNetwork` detects the disconnect. It constructs a 0x866 event with `event_code = 0x00060005`, sets the disconnecting peer slot, then posts the event the same way as join. The same `LAB_0x006a1590` handler fires and serializes the opcode-17 wire bytes. The wire frame is byte-identical to the join case except for `event_code`.

#### NewPlayerInGameHandler name collision

There are **two distinct functions both named `NewPlayerInGameHandler`** in Ghidra's database — and that's intentional, not a labeling bug.

| Address | Type in DB | Role | When it runs |
|---------|------------|------|--------------|
| `FUN_006a1e70` | function (defined body) | Opcode 0x2A wire receiver | Server receives a player-joined message from a client |
| `LAB_0x006a1590` | LAB only (no function body in DB) | Event-fired wire-send handler | Posted 0x866 event matches `ET_NEW_PLAYER_IN_GAME` — handler writes opcode 0x17 to the wire |

Both register against the same SWIG name string `"MultiplayerGame :: NewPlayerInGameHandler"` at `0x0095a028`. The disambiguation happens inside `FUN_0069efe0` (the registration table builder), which calls `FUN_006da130(&LAB_006a1590, s_MultiplayerGame____NewPlayerInGa_0095a028)` — registering the LAB_ address under the same name that the function entry already has. This is the same SWIG-callback-vs-function pattern documented in leaves #13/#14/#15: handler addresses appear only as DATA xrefs from registration sites, so Ghidra auto-analysis never creates a function entry for them.

### Critical correction: FUN_006a0ca0 sends opcode 0x18, NOT 0x17

Pre-v5 wording attributed disconnect-time opcode 0x17 sending to `FUN_006a0ca0` ("DeletePlayerHandler"). **This is wrong.** Disasm of `FUN_006a0ca0` at offset 166 shows:

```
C6 44 24 48 18    MOV byte ptr [ESP+0x48], 0x18
```

— this function sends **opcode 0x18 (DeletePlayerAnim)**, not opcode 0x17. The actual disconnect-side 0x17 sender is `FUN_006b75b0` inside `TGWinsockNetwork`. It doesn't write 0x17 directly — it posts a 0x866 event with `event_code = 0x00060005`, and the EventManager routes that to `LAB_0x006a1590` which performs the actual serialization.

This means disconnect-time 0x17 + 0x18 (and likely + 0x14 `DestroyObject`) reach the wire via different mechanisms:

- **0x18** — `FUN_006a0ca0` writes the opcode byte directly
- **0x17** — `FUN_006b75b0` posts an event → `LAB_0x006a1590` writes the opcode byte
- **0x14** — separate path (not investigated this pass)

---

## Stock Trace Evidence

### Join-time packet (stock dedi self-destruct test, 2026-02-21)

Packet #25, sent S→C after `NewPlayerInGame` (0x2A) and alongside `MissionInit` (0x35):

```
17 66 08 00 00 F1 00 80 00 00 00 00 00 4F 06 00 00 02
```

[v5-validated 2026-05-28] decoded byte-by-byte:
- `17` — opcode 0x17 (DeletePlayerUI)
- `66 08 00 00` — `class_id = 0x00000866` (TGFactory subclass, NOT NiRTTI)
- `F1 00 80 00` — `event_code = 0x008000F1` (`ET_NEW_PLAYER_IN_GAME`)
- `00 00 00 00` — `src_obj_id = 0` (always 0 via this code path)
- `4F 06 00 00` — `dst_obj_id = 0x0000064F` — **TGWinsockNetwork singleton's internal handle for this session, not a ship/player ID**
- `02` — `wire_peer_id = 2` (joining client's slot)

### Trace frequency

| Trace | 0x17 count | Context | Authority |
|-------|-----------|---------|-----------|
| Stock dedi self-destruct test | 1 | Join time (player 2 joins) | S->C |
| Battle of Valentine's Day (33.5 min, 3 players) | 6 | All at join time (slot reuse) | S->C |
| Stock dedi 91-second session | 1 | Join time | S->C |
| `relay-audit-20260224` aggregate | 7 | All S->C | 0 C->S, 7 S->C |

Zero 0x17 instances observed at disconnect time across available traces. Disconnect cleanup uses the path described above (`FUN_006b75b0` posts an event → `LAB_0x006a1590` writes the wire), but no trace captured a multi-client session with both a disconnecting client AND remaining receivers. The path is binary-confirmed; trace observation is pending.

---

## Scoreboard Population Requirements

[v5-validated 2026-05-28]

The client's scoreboard (`Mission1Menus.py RebuildPlayerList`) requires **both** conditions to display a player:

1. **TGPlayerList entry**: player must exist in `pNetwork.GetPlayerList()` — populated by opcode 0x17 carrying `ET_NEW_PLAYER_IN_GAME`.
2. **Score dictionary entry**: player's `GetNetID()` must appear in `g_kKillsDictionary` — populated by `SCORE_MESSAGE` (0x37) or `SCORE_CHANGE` (0x36).

```python
# Mission1Menus.py line 267
if (pDict.has_key(pPlayer.GetNetID()) and pPlayer.IsDisconnected() == 0):
```

If either is missing, the player won't appear on the scoreboard:
- Missing 0x17 → TGPlayerList empty → no players to iterate
- Missing 0x37 / 0x36 → dictionary empty → players filtered out

On a completely fresh server with no kills, the stock behavior is that a new joiner won't see themselves on the scoreboard until the first kill or death triggers a `SCORE_CHANGE` (0x36). This is stock behavior, not a bug.

---

## Naming Clarification

The name "DeletePlayerUI" is inherited from the opcode's role in the disconnect flow (where it was first identified by trace inspection). The opcode is fundamentally a **TGEvent-family transport** carrying a 0x866 subclass — the same receiver handles both join and disconnect events by dispatching on `event_code`. A more accurate name would be "PlayerListEvent" or "PlayerEvent", but the existing name is retained for cross-doc consistency with `game-opcodes.md` and `wire-format-spec.md`.

---

## Open Questions

- Classes 0x865 and 0x867 — what do they carry? Different opcodes? Internal-only without wire serialization?
- `event+0x24` — receiver clears it before dispatch; sender doesn't write it. What does the engine read it for?
- **TGFactory registry full enumeration** — only 0x801, 0x865, 0x866, 0x867 are confirmed entries this pass. A dedicated sweep of all xrefs to `DAT_0099a578` / `DAT_0099a584` and to `FUN_006B2670` / siblings would yield the complete catalog.

---

## Related Documents

- [wire-format-spec.md](wire-format-spec.md) — Summary opcode table. OQ #2 (factory 0x866 catalog gap) is closed by the Two-Registry section above.
- [game-opcodes.md](game-opcodes.md) — Full game opcode reference. Opcode 0x17 / 0x18 distinction now corrected (FUN_006a0ca0 is 0x18, not 0x17).
- [tgmessage-routing.md](tgmessage-routing.md) — `NoMe` / `Forward` group routing for the wire send.
- [transport-layer.md](transport-layer.md) — TGMessage framing under the 0x17 payload.
- [tgobjptrevent-class.md](tgobjptrevent-class.md) — TGEvent subclass pattern (0x10C cousin); for hierarchy reference.
- [pythonevent-wire-format.md](pythonevent-wire-format.md) — PythonEvent (0x06): another factory-based event transport.
- [../engine/event-system-architecture.md](../engine/event-system-architecture.md) — TGEventManager singleton + dispatch loop.
- [../networking/disconnect-flow.md](../networking/disconnect-flow.md) — Disconnect cleanup cascade (now correctly identifying the 0x17 path).
- [../networking/multiplayer-flow.md](../networking/multiplayer-flow.md) — Join flow.
