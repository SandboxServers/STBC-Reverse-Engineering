---
name: delete-player-ui-validation-20260528
description: Protocol leaf #17 validation — DeletePlayerUI (opcode 0x17). Resolves wire-format-spec OQ #2 (factory 0x866). Two material corrections: FUN_006a0ca0 sends 0x18 not 0x17; 0x866 is TGEvent SUBCLASS not base.
metadata:
  type: project
---

# DeletePlayerUI (opcode 0x17) — Protocol Validation #17

Validated 2026-05-28 against STBC.exe (game/stock-dedi/STBC.exe, 6,394,712 bytes, base 0x00400000).

## Anchor table

| Element | Address | Confidence |
|---------|---------|------------|
| Receiver handler | 0x006a1360 | high |
| Event-fired sender (LAB_, no fn body in DB) | 0x006a1590 | high |
| Disconnect-side event poster | 0x006b75b0 (in TGWinsockNetwork) | high |
| Class 0x866 registration | 0x006b27a3 (in FUN_006b2670) | high |
| Class 0x866 vtable | 0x00895848 | high |
| Class 0x866 GetTypeID | 0x006b3700 (`MOV EAX, 0x866; RET`) | high |
| Class 0x866 Save (vtable+0x34) | 0x006bb890 | high |
| Class 0x866 Read (vtable+0x38) | 0x006bb8b0 | high |
| Base TGEvent ctor | 0x006d5c00 (sets vtable PTR_FUN_00895ff4) | high |
| Base TGEvent Save (vtable+0x34) | 0x006d6128 | high |
| Base TGEvent Read (vtable+0x38) | 0x006d61b8 | high |
| TGFactory_DeserializeObject | 0x006d6200 | high |
| EventManager singleton base | 0x0097F838 | high |
| EventManager registry (singleton+0x2C) | 0x0097F864 | high |
| Event dispatch (`__thiscall(this=0x97F838, event)`) | 0x006da300 | high |
| TGEventManager__PostEvent (wrapper) | 0x006da2a0 | high |
| Registration table | FUN_0069efe0 (binds 28 C++ labels to "MultiplayerGame :: *Handler" strings) | high |

## Two-registry architecture (resolves wire-format-spec OQ #2)

stbc.exe has **TWO independent class registries**:

1. **NiRTTI** — engine classes, registered via NiRTTI_* factory paths; catalog has 0x02/0x101/0x105/0x10C/0x8124/0x8129 etc. Lives in different globals.
2. **TGFactory** — TG event-tree classes, registered via `FUN_006b2670` and siblings using `DAT_0099a578` registry table + `DAT_0099a584` bucket array. Class IDs in 0x801, 0x86x range.

`TGFactory_DeserializeObject` (0x006d6200) uses the TGFactory registry via `TGFactoryCreate(class_id, 0)`. The 0x866 class IS in the TGFactory registry, NOT in NiRTTI — that's why catalog searches missed it.

## TGEvent class family (0x86x cluster)

| Class ID | Vtable | Size | Use |
|----------|--------|------|-----|
| 0x865 | 0x0089580C | 0x2C | unknown — sibling |
| **0x866** | **0x00895848** | **0x2C** | DeletePlayerUI / NewPlayerInGame / DeletePlayer events (opcode 0x17) |
| 0x867 | 0x00895884 | 0x30 | unknown — sibling with 4 extra bytes |

All three derive from base TGEvent (vtable 0x00895FF4). Base TGEvent size unverified but at least 0x28 (from ctor field inits up to +0x24).

## Opcode 0x17 wire format (18 bytes total)

```
offset  size  field          source (sender side)
------  ----  -------------  ----------------------------------------
0       1     opcode 0x17    written by sender at 0x006a15d4 (MOV [ESP+0x40], 0x17)
1-4     4     class_id       base->Save calls this->GetTypeID via vtable+0x4 → 0x866;
                             written by stream->vtable+0x64 (WriteInt, 4 raw bytes)
5-8     4     event_code     event[+0x10]; stream->vtable+0x64 (WriteInt)
                             0x008000F1 = ET_NEW_PLAYER_IN_GAME (join)
                             0x00060005 = ET_NETWORK_DELETE_PLAYER (disconnect)
9-12    4     src_obj_id     event[+0x8]; stream->vtable+0x84 (WriteObjectRef);
                             ALWAYS 0x00000000 via this code path (never set)
13-16   4     dst_obj_id     event[+0xC]; stream->vtable+0x84 (WriteObjectRef);
                             set by FUN_006d62b0(this=TGWinsockNetwork singleton);
                             wire value is the network singleton's internal object handle
                             (NOT a ship/player ID — semantic correction vs prior doc)
17      1     wire_peer_id   event[+0x28]; stream->vtable+0x54 (WriteByte);
                             join: joining player's slot
                             disconnect: disconnecting player's slot
```

## End-to-end flow

**Server side, join:**
1. Opcode 0x2A (NewPlayerInGame) arrives — handler FUN_006a1e70 processes wire bytes
2. Same handler constructs 0x866 event: TGAlloc(0x2C) + FUN_006bb840 (sets vtable to 0x00895848)
3. event[+0x10] = 0x008000F1, event[+0x28] = wire_peer_id
4. FUN_006d62b0(this=network) sets event[+0xC] = network handle
5. TGEventManager__PostEvent → FUN_006da300 → walks registry at 0x0097F864
6. Handler registered for 0x008000F1 = LAB_0x006a1590 — fires
7. LAB_0x006a1590 writes opcode 0x17 to TGBufferStream, calls event->vtable[+0x34] (Save)
8. Allocates 0x40-byte TGMessage, sends via TGWinsockNetwork → NoMe/Forward group → wire

**Server side, disconnect:**
1. TGWinsockNetwork::FUN_006b75b0 detects disconnect
2. Constructs 0x866 event: TGAlloc(0x2C) + FUN_006bb840
3. event[+0x10] = 0x60005, event[+0x28] = disconnecting player slot
4. FUN_006d62b0 + FUN_006d6270 set src/dst from network ctx
5. TGEventManager__PostEvent → LAB_0x006a1590 fires (same handler — dual event_code dispatch)
6. Same wire send as join

**Client side (receive):**
1. Opcode 0x17 arrives — FUN_006a1360 handler
2. TGBufferStream_swig_Ctor + OpenBuffer skipping opcode byte (`pvVar1 + 1, size - 1`)
3. TGFactory_DeserializeObject (0x006d6200): reads class_id u32 via stream->vtable+0x60; calls TGFactoryCreate(0x866, 0) which constructs the event; calls event->vtable+0x38 (Read) which reads event_code/src/dst/peer_id
4. FUN_006f13c0 → calls vtable+0x18 then vtable+0x1C (likely "post-deserialize fixup")
5. FUN_006d62b0(this=network) → sets event+0xC = local network ctx
6. event[+0x24] = 0 (clears unknown field)
7. FUN_006da300(0x97F838, event) → dispatches event:
   - first via event->dest->vtable[+0x50]
   - then walks EventManager registry at 0x97F864 (this+0x2C in FUN_006da300)
8. Registered handler LAB_0x006a1590 fires on the client too — but NoMe/Forward groups are empty on client so wire send is no-op
9. The handler's local-apply path adds the player to the TGPlayerList

## Critical correction: FUN_006a0ca0 sends 0x18, NOT 0x17

The pre-v5 doc claimed `FUN_006a0ca0` (DeletePlayerHandler) sends opcode 0x17 at disconnect time. **Wrong.** Disasm of FUN_006a0ca0 at offset 166 shows `C6 44 24 48 18 = MOV byte ptr [ESP+0x48], 0x18` — this function sends **opcode 0x18 DeletePlayerAnim**.

The actual 0x17 disconnect-side sender is **FUN_006b75b0 inside TGWinsockNetwork** — it doesn't write 0x17 directly. It posts a 0x866 event with event_code 0x60005, which is then routed through the EventManager to LAB_0x006a1590 which performs the actual wire serialization.

This means disconnect-time 0x17 + 0x18 (and likely + 0x14 DestroyObject) all chain through different mechanisms:
- 0x18: FUN_006a0ca0 sends directly  
- 0x17: FUN_006b75b0 posts event → LAB_0x006a1590 sends
- 0x14: separate function (not investigated here)

## Naming clarification: two functions named "NewPlayerInGameHandler"

Ghidra DB shows one defined function at 0x006a1e70 named `NewPlayerInGameHandler` — this is the **opcode 0x2A wire handler**.

Pre-v5 doc said 0x006a1590 was also named `NewPlayerInGameHandler`. **Both are correct conceptually** — they're both registered with the SWIG name `"MultiplayerGame :: NewPlayerInGameHandler"` (the string at 0x0095a028). The disambiguation:
- **0x006a1e70**: receives opcode 0x2A from wire, creates the 0x866 event, posts it locally. Defined as function in DB.
- **0x006a1590**: receives the ET_NEW_PLAYER_IN_GAME event, marshals + sends opcode 0x17 wire. LAB_ only (no function body defined in DB).

The same SWIG name maps to TWO different C++ entry points because the SWIG `FUN_006da130` (registration table builder) registers both. (FUN_0069efe0 has the line `FUN_006da130(&LAB_006a1590, s_MultiplayerGame____NewPlayerInGa_0095a028)` proving this.)

## Pattern: SWIG-registered event handlers are systematically undefined-in-DB

Same pattern as leaves #13/#14/#15 — handler addresses appear only as DATA xrefs from registration sites (FUN_0069efe0 and event-table cells), so Ghidra auto-analysis never creates a function entry. The bodies exist as raw code; disasm proceeds fine; only `get_function_by_address` returns "No function found".

To find such handlers:
1. Look for the registration call site via xrefs to the SWIG name string
2. Identify the address pushed to FUN_006da130 (or similar)
3. Read raw bytes at that address — the prolog (`MOV EAX, FS:[0]; PUSH -1; PUSH <handler>`) confirms it's a function

## Open questions

- What classes are 0x865 and 0x867? Different opcodes? Used internally without wire?
- What does event[+0x24] hold? Receiver clears it before dispatch; sender doesn't write it.
- TGFactory registry full enumeration — only 0x801, 0x865, 0x866, 0x867 confirmed in this session.

## Stock trace cross-anchor

Doc's example packet (1 occurrence in self-destruct test):
```
17 66 08 00 00 F1 00 80 00 00 00 00 00 4F 06 00 00 02
```
Decode confirmed byte-by-byte:
- 17 = opcode
- 66 08 00 00 = class_id 0x00000866 ✓
- F1 00 80 00 = event_code 0x008000F1 (ET_NEW_PLAYER_IN_GAME) ✓
- 00 00 00 00 = src_obj_id (always 0 via this code path) ✓
- 4F 06 00 00 = dst_obj_id 0x0000064F (TGWinsockNetwork internal handle — NOT ship)
- 02 = wire_peer_id (joining player slot 2) ✓

Trace frequency (6 in 33-min battle, 1 in self-destruct, 1 in 91-sec session) all at join time. Disconnect-time 0x17 unobserved because traces didn't capture multi-client disconnect with remaining receivers. Per relay-audit-20260224: 0 C→S / 7 S→C (S→C only confirmed).
