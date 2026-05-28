---
name: protocol-snapshot-20260528
description: Phase 1 reconnaissance snapshot of the protocol subsystem in STBC.exe — dispatchers, opcode handlers, stream methods, CF16/CompressedVector helpers, AlbyRules anchor, reliable ACK pipeline. Anchors the v5 docs/protocol/ validation campaign.
metadata:
  type: project
---

# Protocol Subsystem Snapshot — 2026-05-28

Companion snapshot to [[engine-snapshot-20260528]] for the **protocol** doc family (22 docs under `docs/protocol/`, `docs/networking/`). Same Ghidra DB, same STBC.exe, same caveats — function count moved 18,575 → 18,581 since engine snapshot (+6 from prior v5 dispatcher recovery sessions that ran `create_function` manually).

All claims below cite `program: STBC.exe` queries.

---

## 1. Binary Fingerprint Delta vs. Engine Snapshot

| Field | This snapshot | Engine snapshot | Delta |
|-------|--------------|------------------|-------|
| total_functions | 18,581 | 18,575 | +6 |
| custom_named | n/a (not re-queried) | 4,781 | — |
| Ghidra import date | 2026-05-28 | 2026-05-28 | same |

The +6 function delta is attributable to manual `create_function` calls during the dispatcher-recovery + tgbufferstream-vtable sessions documented in [[dispatcher-recovery-20260528]] and [[tgbufferstream-vtable-20260528]]. No annotation script has run.

---

## 2. The Three Dispatchers — Confirmed

| Addr | Ghidra symbol | Body bytes | effective_score | Confidence |
|------|---------------|-----------|-----------------|-----------|
| 0x0069f2a0 | **MpgameHandleMessage** | 0x0069f2a0–0x0069f530 (657) | **69.84** | high |
| 0x006a3cd0 | FUN_006a3cd0 (NetFile dispatcher) | 0x006a3cd0–0x006a3e7f (432) | 0.60 | high (anchor + decoded body) |
| 0x00504c10 | FUN_00504c10 (MultiplayerWindow dispatcher) | 0x00504c10–0x00504c6f (96) | 9.64 | high (anchor + decoded body) |

**NetFile dispatcher** (0x006a3cd0) decoded this session — handles checksum/file opcodes 0x20-0x27. Uses the same `vtable[0]==0x32` pre-check + `TGBufferStream_GetBufferAndSize` + first-byte switch pattern as MpgameHandleMessage. Sub-handlers:

| Opcode | Handler addr | Role |
|--------|--------------|------|
| 0x20 | FUN_006a5df0 | StateChange (sets MultiplayerGame+0x14 = 0) |
| 0x21 | FUN_006a4260 | Checksum exchange |
| 0x22/0x23 | FUN_006a4c10 | File transfer (data) |
| 0x25 | FUN_006a3ea0 (or first-time UI build inline) | File transfer with confirmation gate; on first 0x25, builds "Receive File Warning" dialog inline using TGL "Cancel"/"OK" strings |
| 0x27 | FUN_006a4250 | Checksum response variant |

**MultiplayerWindow dispatcher** (0x00504c10) gated by `this+0xb0 != 0`. Switch on first wire byte:
| Wire byte | Handler | Role |
|-----------|---------|------|
| 0x00 | FUN_00504d30 | Settings (per CLAUDE.md) |
| 0x01 | FUN_00504f10 | GameInit |
| 0x16 | FUN_00504c70 | UICollisionSetting |

All three dispatchers WRITE `g_bMpgameInOpcodeDispatch` at 0x0097FA8B — shared re-entrancy guard.

---

## 3. Game Opcode Handlers (jump table at 0x0069F534) — All Present

12 spot-checked from CLAUDE.md table, all exist as functions:

| Opcode | Addr | Ghidra symbol | Body size |
|--------|------|---------------|-----------|
| 0x02/0x03 | 0x0069f620 | FUN_0069f620 | 553 |
| 0x06/0x0D | 0x0069f880 | FUN_0069f880 | 167 |
| 0x07-0x12 generic | 0x0069fda0 | FUN_0069fda0 | 389 |
| 0x13 | 0x006a01b0 | **HostMsgHandler** | 44 |
| 0x14 | 0x006a01e0 | FUN_006a01e0 | 189 |
| 0x15 | 0x006a2470 | **CollisionEffectHandler** | 448 |
| 0x17 | 0x006a1360 | FUN_006a1360 | 179 |
| 0x18 | 0x006a1420 | FUN_006a1420 | 354 |
| 0x19 | 0x0069f930 | FUN_0069f930 | 598 |
| 0x1A | 0x0069fbb0 | FUN_0069fbb0 | 455 |
| 0x1C | 0x0069ff50 | FUN_0069ff50 | 155 (StateUpdate — confirmed) |
| 0x29 | 0x006a0080 | FUN_006a0080 | 292 |
| 0x1D | 0x006a0490 | FUN_006a0490 | 328 |
| 0x1E | 0x006a02a0 | FUN_006a02a0 | 455 |
| 0x1F | 0x006a05e0 | FUN_006a05e0 | 458 |
| 0x2A | 0x006a1e70 | **NewPlayerInGameHandler** | 1471 |

Three handlers named from prior v5 work (HostMsg, CollisionEffect, NewPlayerInGame). Completeness data for those:

| Function | effective_score |
|---------|----------------|
| HostMsgHandler | 38.97 |
| CollisionEffectHandler | 2.99 |
| NewPlayerInGameHandler | 0.0 (1471 bytes, 292 lines, untouched) |

CollisionEffect + NewPlayerInGame are large handlers with extensive deductions — major lift opportunities during protocol validation.

---

## 4. TGBufferStream Wire Methods — Vtable 0x008958D0

All 8 documented vtable slots exist as functions (per [[tgbufferstream-vtable-20260528]]). Re-confirmed this session.

| # | Slot Addr | Target | Name | effective_score |
|---|-----------|--------|------|----------------|
| 0 | 0x008958D0 | 0x006b9430 | **TGBufferStream_GetStreamTypeId** | **95.0** |
| 1 | 0x008958D4 | 0x006b82f0 | **TGBufferStream_ScalarDeletingDtor** | n/a |
| 2 | 0x008958D8 | 0x006b8340 | **TGBufferStream_Serialize** | **82.6** |
| 3 | 0x008958DC | 0x006b9440 | **TGBufferStream_HasDerivedType** | n/a |
| 4 | 0x008958E0 | 0x006b9450 | **TGBufferStream_IsSpecialStream** | n/a |
| 5 | 0x008958E4 | 0x006b8640 | **TGBufferStream_GetSerializedSize** | n/a |
| 6 | 0x008958E8 | 0x006b8610 | **TGBufferStream_Clone** | n/a |
| 7 | 0x008958EC | 0x006b8720 | **TGBufferStream_Fragment** | n/a |

Vtable extends to at least slot 31 (read 128 bytes). Slots 8-31 not investigated this session; from [[tgbufferstream-vtable-20260528]] Open Question 3, slots 8+ may be a different adjacent class.

**TGBufferStream class ctors trio (vtable installers):**
- 0x006b82a0 → **TGBufferStream_Ctor** (named)
- 0x006b8320 → **TGBufferStream_Dtor** (named)
- 0x006b8550 → **TGBufferStream_CopyCtor** (named)

**GetBufferAndSize accessor** (used by both NetFile + Mpgame dispatchers to read the opcode byte): `0x006b8530` — `TGBufferStream_GetBufferAndSize(this, *pnSizeOut)` (named, v5).

---

## 5. SWIG-Exposed TGBufferStream API (rich anchor table)

76 string matches for `TGBufferStream` in `.rdata`. Each SWIG method implies a method body in the C++ class (some inline accessor, some real function). High-value subset for documenting stream primitives:

WriteID, ReadID, WriteDouble, WriteFloat, WriteLong, WriteInt, WriteShort, WriteChar, WriteBool, WriteWChar, WriteCWLine, WriteCString, WriteCLine, Write, ReadDouble, ReadFloat, ReadLong, ReadInt, ReadShort, ReadBool, ReadChar, ReadWChar, ReadCWLine, ReadCString, ReadCLine, Read, GetWriteMode, SetWriteMode, Close, GetBuffer, OpenBuffer, CloseBuffer, GetPos, GetLength, Eof, new_TGBufferStream, delete_TGBufferStream.

These are the **canonical names** for the wire primitives — stream-primitives.md uses `WriteByte/WriteShort/WriteInt32/WriteFloat` etc., but the C++ class actually exposes `WriteChar` (1 byte), `WriteShort` (2), `WriteInt` (4 signed), `WriteLong` (4), `WriteFloat`, `WriteDouble`. **Minor naming mismatch to flag in doc validation.**

---

## 6. CF16 / CompressedVector Helpers — Confirmed

All 4 doc-cited helper addresses are real functions:

| Addr | Body | Role per doc | Status |
|------|------|--------------|--------|
| 0x006d3a90 | 150 bytes | CF16 encode | function exists, unnamed |
| 0x006d3b30 | 121 bytes | CF16 decode | function exists, unnamed |
| 0x006d2ad0 | 205 bytes | CompressedVector3 write | function exists, unnamed |
| 0x006d2eb0 | 83 bytes | CompressedVector3 read | function exists, unnamed (decompile-confirmed) |
| 0x006d2f10 | 178 bytes | CompressedVector4 write | function exists, unnamed |
| 0x006d2fd0 | 158 bytes | CompressedVector4 read | function exists, unnamed |

**CF16 constants** (bytes confirmed in memory):
- 0x00888b4c = `6F 12 83 3A` (float 0.001) — BASE ✓
- 0x0088c548 = `00 00 20 41` (float 10.0) — MULT ✓
- 0x00895f50 = `00 F0 7F 45` (float 4095.0) — ENC_SCALE ✓
- 0x00895f54 = `01 08 80 39` (float 1/4095) — DEC_SCALE ✓

**ReadCompressedVector3 (0x006d2eb0) decompiled** — confirms doc's vtable-slot claim: calls `vtable[0x50]()` three times (byte reads) then `vtable[0xB8]()` to decompress. The fact that it operates via vtable slots means there is a **separate stream-reader class hierarchy** apart from TGBufferStream. Three different stream-reader vtables install 0x006d2eb0 at slot index 5 (offset +0x14):
- 0x00895cd0 region
- 0x00895dd8 region
- 0x00895ed0 region

That's the patched-via-proxy site referenced in CLAUDE.md ("Compressed vector read guard at 0x006D2EB0/0x006D2FD0") — confirmed.

---

## 7. TGMessage Subclass Vtables (event-system family)

`.rdata` block at 0x00896000-0x008961xx is the event/message vtable cluster. From [[event-system-validation-20260528]] + this session's reads:

| Class | Vtable | sizeof | First slot target | Confidence |
|------|--------|--------|-------------------|-----------|
| (unknown — 0x00896000) | 0x00896000 | unknown | 0x006f1650 (GetTypeID universal) | low — class identity unconfirmed |
| **TGEvent** | 0x00896018 | 0x28 | 0x006d5d10 (function not in Ghidra; bytes exist) | high (anchor) / medium (slot bodies) |
| TGEvent slot 1 stub | (stub at 0x006d5d20) | 5 bytes | MOV EAX, ptr to `_p_TGEvent`@0x0091427c; RET | high (bytes read) |
| **TGEventHandlerObject** | 0x00896044 | (≥0x14) | 0x006d5d30 (function not in Ghidra) | high (anchor per event-system memo) |
| **TGCallback** | 0x008960f4 | 0x14 | (per event-system memo) | high |
| **TGConditionHandler** | 0x00896104 | ~0x34 | (per event-system memo) | high |
| **TGInstanceHandlerTable** | 0x00896030 | 0x14 | (per event-system memo) | high |

**TGCharEvent slot-1 stub** at 0x00574c90: `MOV EAX, 0x008e54dc; RET` — returns pointer to string `_p_TGCharEvent`. Confirms class identity via string-pointer RTTI scheme (not integer tag).

**TGObjPtrEvent slot-1 stub** at 0x00403300: `MOV EAX, 0x008d85a4; RET` — returns pointer to string `_p_TGObjPtrEvent`. Confirms class identity.

**SWIG type-info tables** (different from class vtables — used by SWIG runtime for C-to-Python cast safety):
- TGCharEvent type-info: 0x008fe278
- TGObjPtrEvent type-info: 0x008fe778
- TGEvent type-info: 0x008fe8f8
- TGBufferStream type-info: 0x008ff488
- TGMessage type-info: 0x008fc0b8
- TGBootPlayerMessage type-info: 0x008fc2e8

**Class vtable** (the C++ vtable, not the SWIG type-info table) for TGObjPtrEvent/TGCharEvent — **not located this session**. Each has only its stub function visible. The class vtable is elsewhere in `.rdata` and would need to be found by tracing `new_*` SWIG wrapper allocator paths. Deferred to per-class validation work.

---

## 8. AlbyRules Cipher Anchor — Confirmed

String `"AlbyRules!"` at **0x0095abb4** — only 1 producer in the binary.

| Function | Body | Role |
|----------|------|------|
| FUN_006c2280 | 0x006c2280–0x006c22ea (107 bytes) | Initializer / ctor — zeros 0x4..0x54 of param_1 struct, then strcpy-copies "AlbyRules!" into `(struct+0x48)`. NOT the cipher transform itself. |

**Open question:** the actual cipher transform (XOR/permute over packet bytes using the "AlbyRules!" key) lives elsewhere. FUN_006c2280 is the constructor that stamps the key into a network-context struct. To find the cipher, would need xrefs to `(thisstruct + 0x48)` read pattern. Deferred. Document any doc-claimed cipher function addresses by checking `docs/networking/alby-rules-cipher-analysis.md` for follow-up.

---

## 9. Reliable ACK Pipeline — Confirmed

| Addr | Ghidra symbol | Body | Caller |
|------|---------------|------|--------|
| 0x006b61e0 | FUN_006b61e0 | 438 bytes | 0x006b5c90 → CALL 006b61e0 (UNCONDITIONAL) |
| 0x006b64d0 | FUN_006b64d0 | 360 bytes | 0x006b5f70 → CALL 006b64d0 (UNCONDITIONAL) |

Both exist as Ghidra functions, neither named. effective scores: 2.57 + 3.55. Per network-protocol-analyst notes (`below32-ack-mechanism.md`), 006b61e0 is `HandleReliableReceived` and 006b64d0 is `HandleACK`. Naming + plate work remains.

---

## 10. SendStateUpdates Confirmation

`FUN_006b55b0` (271 lines decompiled, body 0x006b55b0-0x006b5c8a, 1755 bytes). Decompile-confirmed as the **round-robin StateUpdate sender**:
- Walks player array at `this+0xb*4`, count at `this+0xc`
- Cursor stored at `this+0x2c` (advances per call)
- Allocates send buffer of `this+0x2b` bytes via FUN_00718cb0
- Processes 3 queues per peer: subsystems at iVar2+0x9c, weapons at iVar2+0x80, state at iVar2+0x64 (queue counts at +0xb4/+0x98/+0x7c)
- Writes header byte (player id) + iStack_28 count at offsets [0]/[1] of buffer
- Sends via vtable+0x70 (likely `SendUnreliable(addr, buf, len)`)
- Threshold constant `DAT_0099c6bc` (used as time threshold)
- 3 callers: FUN_006b4060, FUN_006b4560 (UNCONDITIONAL_CALLs from Update/Tick paths)

effective_score: 0.0 (untouched). Major lift target.

---

## 11. Protocol Globals (CLAUDE.md cross-check)

All confirmed via xref readback:

| Addr | Role per CLAUDE | xref pattern |
|------|------------------|--------------|
| 0x0097FA00 | UtopiaModule base | 5+ data xrefs across bootstrap functions |
| 0x0097FA78 | TGWinsockNetwork* (UtopiaModule+0x78) | 5+ READ xrefs from MP/dispatcher code |
| 0x0097FA8B | g_bMpgameInOpcodeDispatch (reentrancy guard) | WRITE from MpgameHandleMessage + FUN_006a3cd0 (NetFile dispatcher) + 0055e2b0 (READ) |
| 0x0097e238 | TopWindow/MultiplayerGame ptr | per ui-class-hierarchy-validation memo — actually PlayWindow/Game (TopWindow is at 0x009878cc) |
| 0x009878cc | TopWindow (per ui-class-hierarchy-validation) | 5+ READ xrefs from FUN_00405ec0/c10 family |
| 0x00991438 | g_TGEventManager (per event-system memo) | 2 READ xrefs at 0x0065b430/460 |

CLAUDE.md row `0x0097e238 TopWindow/MultiplayerGame ptr` is a **known drift** — see [[ui-class-hierarchy-validation-20260528]] for the correction. Protocol docs that cite 0x0097e238 as "TopWindow" should be flagged.

---

## 12. Protocol Anchor Table (yaml for documentation-writer)

```yaml
protocol_anchors:
  binary:
    file: STBC.exe
    size_bytes: 6394712
    image_base: 0x00400000
    arch: x86-32 LE
    compiler: MSVC (windows)
    ghidra_import: 2026-05-28
    total_functions: 18581
    annotation_scripts_applied: NONE

  dispatchers:
    - { addr: 0x0069f2a0, name: MpgameHandleMessage, completeness: 69.84, source: dispatcher-recovery-20260528 + this snapshot }
    - { addr: 0x006a3cd0, name: NetFile_dispatcher,           completeness: 0.60,  source: decompiled-functions.md (engine doc #10) + this snapshot (decoded) }
    - { addr: 0x00504c10, name: MultiplayerWindow_dispatcher, completeness: 9.64,  source: function-map.md + this snapshot (decoded) }

  jump_table:
    addr: 0x0069F534
    entries: 41
    opcode_offset: -2
    source: dispatcher-recovery-20260528

  game_opcode_handlers:
    - { opcode: 0x02, addr: 0x0069f620, name: ObjCreate,           body: 553 }
    - { opcode: 0x03, addr: 0x0069f620, name: ObjCreateTeam,       body: 553 }
    - { opcode: 0x06, addr: 0x0069f880, name: PythonEvent,         body: 167 }
    - { opcode: 0x0D, addr: 0x0069f880, name: PythonEvent2,        body: 167 }
    - { opcode: 0x07, addr: 0x0069fda0, name: StartFiring,         body: 389 }
    - { opcode: 0x08, addr: 0x0069fda0, name: StopFiring,          body: 389 }
    - { opcode: 0x09, addr: 0x0069fda0, name: StopFiringAtTarget,  body: 389 }
    - { opcode: 0x0A, addr: 0x0069fda0, name: SubsysStatus,        body: 389 }
    - { opcode: 0x0B, addr: 0x0069fda0, name: AddToRepairList,     body: 389 }
    - { opcode: 0x0C, addr: 0x0069fda0, name: ClientEvent,         body: 389 }
    - { opcode: 0x0E, addr: 0x0069fda0, name: StartCloak,          body: 389 }
    - { opcode: 0x0F, addr: 0x0069fda0, name: StopCloak,           body: 389 }
    - { opcode: 0x10, addr: 0x0069fda0, name: StartWarp,           body: 389 }
    - { opcode: 0x11, addr: 0x0069fda0, name: RepairListPriority,  body: 389 }
    - { opcode: 0x12, addr: 0x0069fda0, name: SetPhaserLevel,      body: 389 }
    - { opcode: 0x13, addr: 0x006a01b0, name: HostMsgHandler,      body: 44,   effective: 38.97, custom_named: true }
    - { opcode: 0x14, addr: 0x006a01e0, name: DestroyObject,       body: 189 }
    - { opcode: 0x15, addr: 0x006a2470, name: CollisionEffectHandler, body: 448, effective: 2.99, custom_named: true }
    - { opcode: 0x17, addr: 0x006a1360, name: DeletePlayerUI,      body: 179 }
    - { opcode: 0x18, addr: 0x006a1420, name: DeletePlayerAnim,    body: 354 }
    - { opcode: 0x19, addr: 0x0069f930, name: TorpedoFire,         body: 598 }
    - { opcode: 0x1A, addr: 0x0069fbb0, name: BeamFire,            body: 455 }
    - { opcode: 0x1B, addr: 0x0069fda0, name: TorpTypeChange,      body: 389 }
    - { opcode: 0x1C, addr: 0x0069ff50, name: StateUpdate,         body: 155, note: MISSING_FROM_CLAUDE_MD }
    - { opcode: 0x1D, addr: 0x006a0490, name: ObjNotFound,         body: 328 }
    - { opcode: 0x1E, addr: 0x006a02a0, name: RequestObj,          body: 455 }
    - { opcode: 0x1F, addr: 0x006a05e0, name: EnterSet,            body: 458 }
    - { opcode: 0x29, addr: 0x006a0080, name: Explosion,           body: 292 }
    - { opcode: 0x2A, addr: 0x006a1e70, name: NewPlayerInGameHandler, body: 1471, effective: 0.0, custom_named: true }

  mp_window_handlers:
    - { wire_byte: 0x00, addr: 0x00504d30, name: Settings,        body: 470 }
    - { wire_byte: 0x01, addr: 0x00504f10, name: GameInit,        body: 298 }
    - { wire_byte: 0x16, addr: 0x00504c70, name: UICollisionSetting, body: 191 }

  netfile_handlers:
    - { opcode: 0x20, addr: 0x006a5df0, name: NetFile_StateChange,   body: 882  }
    - { opcode: 0x21, addr: 0x006a4260, name: NetFile_Checksum,      body: 757  }
    - { opcode: 0x22, addr: 0x006a4c10, name: NetFile_FileData,      body: 364  }
    - { opcode: 0x23, addr: 0x006a4c10, name: NetFile_FileData_alt,  body: 364  }
    - { opcode: 0x25, addr: 0x006a3ea0, name: NetFile_FileConfirm,   body: 671, note: "First receive builds UI dialog inline; subsequent receives delegate to 006a3ea0" }
    - { opcode: 0x27, addr: 0x006a4250, name: NetFile_ChecksumAck,   body: 16   }

  tgbufferstream_vtable:
    addr: 0x008958D0
    sizeof: 0x40
    slots:
      - { idx: 0, slot_addr: 0x008958D0, target: 0x006b9430, name: TGBufferStream_GetStreamTypeId, returns: 0x32, effective: 95.0 }
      - { idx: 1, slot_addr: 0x008958D4, target: 0x006b82f0, name: TGBufferStream_ScalarDeletingDtor }
      - { idx: 2, slot_addr: 0x008958D8, target: 0x006b8340, name: TGBufferStream_Serialize, effective: 82.6 }
      - { idx: 3, slot_addr: 0x008958DC, target: 0x006b9440, name: TGBufferStream_HasDerivedType }
      - { idx: 4, slot_addr: 0x008958E0, target: 0x006b9450, name: TGBufferStream_IsSpecialStream }
      - { idx: 5, slot_addr: 0x008958E4, target: 0x006b8640, name: TGBufferStream_GetSerializedSize }
      - { idx: 6, slot_addr: 0x008958E8, target: 0x006b8610, name: TGBufferStream_Clone }
      - { idx: 7, slot_addr: 0x008958EC, target: 0x006b8720, name: TGBufferStream_Fragment }
    ctors:
      - { addr: 0x006b82a0, name: TGBufferStream_Ctor }
      - { addr: 0x006b8320, name: TGBufferStream_Dtor }
      - { addr: 0x006b8550, name: TGBufferStream_CopyCtor }
    accessor:
      - { addr: 0x006b8530, name: TGBufferStream_GetBufferAndSize }

  stream_primitives:
    ctor: { addr: 0x006cefe0, name_per_doc: TGBufferStream_ctor_alt, note: "stream-primitives.md cites this as ctor — distinct from 0x006b82a0; likely a different stream class" }
    write:
      - { addr: 0x006cf730, name: WriteByte / WriteChar (per SWIG: TGBufferStream_WriteChar), size: 1 }
      - { addr: 0x006cf770, name: WriteBit, size: 0-1 }
      - { addr: 0x006cf7f0, name: WriteShort, size: 2 }
      - { addr: 0x006cf870, name: WriteInt32 / WriteInt (per SWIG: TGBufferStream_WriteInt), size: 4 }
      - { addr: 0x006cf8b0, name: WriteFloat, size: 4 }
      - { addr: 0x006cf2b0, name: WriteBytes, size: N }
    read:
      - { addr: 0x006cf540, name: ReadByte / ReadChar, size: 1 }
      - { addr: 0x006cf580, name: ReadBit, size: 0-1 }
      - { addr: 0x006cf600, name: ReadShort, size: 2 }
      - { addr: 0x006cf670, name: ReadInt32 / ReadInt, size: 4 }
      - { addr: 0x006cf6b0, name: ReadFloat, size: 4 }
      - { addr: 0x006cf230, name: ReadBytes, size: N }

  cf16:
    encode: { addr: 0x006d3a90, body_bytes: 150 }
    decode: { addr: 0x006d3b30, body_bytes: 121 }
    constants:
      - { addr: 0x00888b4c, value: 0.001f,  hex: 3A83126F, role: BASE }
      - { addr: 0x0088c548, value: 10.0f,   hex: 41200000, role: MULT }
      - { addr: 0x00895f50, value: 4095.0f, hex: 457FF000, role: ENC_SCALE }
      - { addr: 0x00895f54, value: 1/4095,  hex: 39800108, role: DEC_SCALE }

  compressed_vector:
    write_cv3: { addr: 0x006d2ad0 }
    read_cv3:  { addr: 0x006d2eb0, decompiled_this_session: true, calls: ["vtable[0x50]x3", "vtable[0xB8]"] }
    write_cv4: { addr: 0x006d2f10 }
    read_cv4:  { addr: 0x006d2fd0 }
    stream_reader_vtables:
      - 0x00895CD0  # cluster (slot 5 = 0x006d2eb0)
      - 0x00895DD8
      - 0x00895ED0

  message_factories:
    # Class vtables (the C++ vtable that holds GetTypeID etc.)
    tgevent_class_vtable:       { addr: 0x00896018, sizeof: 0x28, source: event-system-validation }
    tgevent_handler_vtable:     { addr: 0x00896044, source: event-system-validation }
    tgcallback_vtable:          { addr: 0x008960f4, sizeof: 0x14, source: event-system-validation }
    tgconditionhandler_vtable:  { addr: 0x00896104, source: event-system-validation }
    tginstancehandlertable_vt:  { addr: 0x00896030, sizeof: 0x14, source: event-system-validation }

    # SWIG type-info tables (used by Python runtime; first slot = string ptr)
    swig_typeinfo:
      - { class: TGCharEvent,         table: 0x008fe278, name_str: 0x008e54dc }
      - { class: TGObjPtrEvent,       table: 0x008fe778, name_str: 0x008d85a4 }
      - { class: TGEvent,             table: 0x008fe8f8, name_str: 0x0091427c }
      - { class: TGBufferStream,      table: 0x008ff488 }
      - { class: TGMessage,           table: 0x008fc0b8 }
      - { class: TGBootPlayerMessage, table: 0x008fc2e8 }

    # GetRTTI stubs (slot 1 of each TGEvent subclass class-vtable; returns string-pointer)
    rtti_stubs:
      - { class: TGCharEvent,   stub_addr: 0x00574c90, code: "MOV EAX, 0x008e54dc; RET" }
      - { class: TGObjPtrEvent, stub_addr: 0x00403300, code: "MOV EAX, 0x008d85a4; RET" }

    open_questions:
      - "TGObjPtrEvent class-vtable (the C++ vtable, not the SWIG type-info table) — not located this session. Must trace new_TGObjPtrEvent SWIG wrapper body to find ctor write site."
      - "TGCharEvent class-vtable — same as above."
      - "TGBootPlayerMessage class-vtable — not located."

  reliable_pipeline:
    - { addr: 0x006b61e0, name: HandleReliableReceived, effective: 2.57, body: 438, caller: 0x006b5c90 }
    - { addr: 0x006b64d0, name: HandleACK,              effective: 3.55, body: 360, caller: 0x006b5f70 }

  state_update_sender:
    - { addr: 0x006b55b0, name: SendStateUpdates, effective: 0.0, body: 1755, code_lines: 271, callers: [0x006b4060, 0x006b4560] }

  cipher:
    alby_rules:
      string_addr: 0x0095abb4
      initializer: { addr: 0x006c2280, body: 107, role: "ctor stamps key into struct+0x48" }
      open_question: "transform function (actual XOR/permute) not located; would require xref pattern READ from struct+0x48"

  setphaser_handlers:
    engine_subsystem: { addr: 0x00573de0, debug_string: 0x008e5440 ("PhaserSystem::SetPhaserLevelHandler") }
    mp_dispatcher:    { addr: 0x0069efe0, registration_string: 0x00959f1c ("MultiplayerGame :: SetPhaserLevelHandler") }

  globals:
    - { addr: 0x0097FA00, name: g_UtopiaModule_base }
    - { addr: 0x0097FA78, name: g_TGWinsockNetwork_ptr }
    - { addr: 0x0097FA8B, name: g_bMpgameInOpcodeDispatch }
    - { addr: 0x0097e238, name: g_PlayWindow (NOT TopWindow — see drift_findings #2) }
    - { addr: 0x009878cc, name: g_TopWindow, source: ui-class-hierarchy-validation }
    - { addr: 0x00991438, name: g_TGEventManager, source: event-system-validation }
```

---

## Top 3 Drift Findings for v5 Protocol Validation

### 1. Stream-primitives doc cites wrong ctor address

`docs/protocol/stream-primitives.md` line 5 says: "All serialization uses a `TGBufferStream` object (`FUN_006cefe0` constructor). The stream has +0x1C = buffer pointer, +0x20 = capacity, +0x24 = position, +0x28 = bit-pack bookmark, +0x2C = bit-pack state."

But the `TGBufferStream` class vtable is at `0x008958D0`, and the three actual TGBufferStream constructors are `0x006b82a0` (default), `0x006b8320` (dtor), `0x006b8550` (copy). FUN_006cefe0 is a DIFFERENT class — likely a stream-reader/bit-reader wrapper that holds a BitStreamReader at offset +0x1C..+0x2C. Field offsets in the doc are correct for THAT class, not for TGBufferStream.

This was already flagged in [[tgbufferstream-vtable-20260528]] Open Question (the bit-cursor wrapper). Protocol validation campaign must:
- Rename the doc's `TGBufferStream` references to `BitStreamReader` (or whatever the actual class is) when describing offsets 0x1C-0x2C.
- Keep references to 0x006cefe0 + the 16 read/write helpers, but document them as the **bit-packing wrapper class**, not TGBufferStream.
- Cross-reference [[tgbufferstream-vtable-20260528]] for the actual TGBufferStream layout (0x40 bytes, fields at 0x00/0x04/0x08/0x0C, no bit state).

### 2. CLAUDE.md's "TopWindow ptr at 0x0097e238" is wrong

Per [[ui-class-hierarchy-validation-20260528]], `0x0097e238` is `g_PlayWindow` (the active in-game Window), not TopWindow. Actual TopWindow is at `0x009878cc`. Protocol docs that cite `(*0x0097e238)` to reach MultiplayerGame (e.g., "TopWindow at 0x0097e238 -> MultiplayerGame at +0xXX") need to be re-verified — the dereference path may still work because PlayWindow holds a Game/MultiplayerGame pointer, but the symbol name is wrong.

### 3. Three core protocol functions still unnamed and unscored

- `FUN_006a3cd0` NetFile dispatcher: 0.60 effective
- `FUN_00504c10` MultiplayerWindow dispatcher: 9.64 effective
- `FUN_006b55b0` SendStateUpdates: 0.0 effective (1755-byte body, 271 decompile lines)
- `FUN_006b61e0` HandleReliableReceived: 2.57 effective
- `FUN_006b64d0` HandleACK: 3.55 effective

The protocol family's load-bearing functions are essentially unannotated. v5 validation will need substantial naming + plate-comment work just to get baseline scores above the "structural ceiling -5" threshold. Estimate: 3-5 of these need dedicated v5 passes during the campaign (similar lifts to dispatcher-recovery). Expect campaign to surface 1-2 architectural corrections per function (analogous to the +0x14 cursor fix in TGBufferStream).

---

## "This doc family will be hard because..."

1. **Stream-primitives mis-anchors the class.** The doc was written before TGBufferStream's vtable was found and conflates two stream classes (TGBufferStream byte-aligned with field +0x08 cursor, vs. an unidentified bit-packing wrapper at 0x006cefe0 with +0x1C/0x20/0x24/0x28/0x2C fields). The two are different classes serving different roles and the doc treats them as one. **Every reference to "TGBufferStream" in stream-primitives.md must be audited** — some are correct (the SWIG API names), some refer to the wrapper class (the offsets).

2. **TGMessage-subclass class-vtables not located.** TGObjPtrEvent (factory 0x010C), TGCharEvent, TGBootPlayerMessage — their actual class vtables (with GetTypeID, Serialize, etc.) are NOT at the addresses commonly cited in docs. The docs may cite SWIG type-info tables (0x008fe278/778/8f8) or stub addresses (0x00574c90, 0x00403300) without distinguishing them. Validation pass needs to:
   - Locate each class's actual vtable (trace ctor from `new_*` SWIG wrapper).
   - Re-anchor every doc claim "TGObjPtrEvent vtable at 0xXXX" against the located address.

3. **Reliable ACK pipeline at floor.** 0x006b61e0 + 0x006b64d0 are described in two memory files (`below32-ack-mechanism.md` from network-protocol-analyst, plus `ack-outbox-deadlock.md` in docs/) but neither has plate comments nor names in Ghidra. The doc `docs/networking/fragmented-ack-bug.md` may cite line numbers / state variables that have shifted; validation needs to re-read the binary first.

4. **No string anchors for many message-types.** TGStreamedObject (mentioned in pythonevent-wire-format.md) has 0 string matches — its identity is purely behavioral (integer slot-1 return value 0x03 per event-system memo). Docs that cite "TGStreamedObject" or its serialize signature must be evidence-anchored against vtable bytes, not strings.

5. **CompressedVector reader has 3 vtable installers, not 1.** 0x006d2eb0 is shared across 3 stream-reader class vtables. Documentation cannot describe "the" reader as if it lived in one class — it's a hot-shared utility installed by multiple classes. Validation must enumerate the 3 installer classes and document why each needs CV3 reading.

6. **AlbyRules cipher transform unlocated.** Doc `docs/networking/alby-rules-cipher-analysis.md` likely cites function addresses for the cipher — verify each because the only producer of `"AlbyRules!"` string is an initializer that stamps the key, not the cipher itself.

---

## Open Questions for follow-up

1. Where is the TGBufferStream cursor advance? `Serialize` writes via REP MOVSD using count = `*(this+8)`, but who advances `*(this+8)` per WriteByte/WriteShort? Likely in 0x006cf730/770/7f0 family (the wrapper class methods). Need to verify these wrapper methods modify TGBufferStream fields or their own class's fields.
2. What is the BitStreamReader class at 0x006cefe0? sizeof? vtable? Open work item.
3. AlbyRules transform function: scan all xrefs READ from `(struct+0x48)` after ctor 0x006c2280 returns. The transform should appear as a function that reads a key-byte from offset 0x48-0x52.
4. SendStateUpdates: per peer the function processes 3 queues with rotating cursor at this+0x2c. Are the 3 queue types (+0x7c/+0x98/+0xb4) (subsystems, weapons, state) or different? StateUpdate doc claims 3 round-robin lists — verify by tracing what writes to each queue.
5. MpgameHandleMessage's vtable[0]==0x32 self-check echoes in NetFile dispatcher with the same value. Is `0x32` the universal "TGBufferStream class tag" across all 3 dispatchers? Spot-check by confirming the same constant in MultiplayerWindow dispatcher's check (we already saw: yes, line 9 of decompile, `if (iVar2 == 0x32)`). Consistent — confirms TGBufferStream is the universal payload class.

---

## Cross-References

- [[engine-snapshot-20260528]] — original ground truth + binary fingerprint
- [[dispatcher-recovery-20260528]] — MpgameHandleMessage and jump table
- [[struct-skeletons-20260528]] — MultiplayerGame, TGMessage, TGBufferStream, PlayerSlot structs
- [[tgbufferstream-vtable-20260528]] — full TGBufferStream vtable + sizeof=0x40 correction
- [[event-system-validation-20260528]] — TGEvent / TGCallback / TGConditionHandler vtables and sizes
- [[ui-class-hierarchy-validation-20260528]] — TopWindow/PlayWindow global correction (relevant to protocol docs that cite 0x0097e238)
- [[netimmerse-vtables-validation-20260528]] — adjacent .rdata region patterns (vtable cluster discovery technique reuse)
