# Network Protocol Analyst - Memory

## Trace Mining Verification (2026-05-29)
- See [trace-mining-verification-20260529.md](trace-mining-verification-20260529.md) — answers 7 OpenBC OQs from existing traces
- REPAIR: 0x101 form=17B msg body / 0x10C TGObjPtrEvent form=21B (opcode-incl) = 20B payload. 21-vs-20 = opcode counted or not.
- Bundling: max msgCount=110 (datagram len=491, NOT 512-padded). Header `[dir:1][msgCount:1]` confirmed from bytes.
- Relay matrix (3-player): combat 0x07/08/0A/19/1A/1B/11/12 RELAYED 1:2 to OTHERS (no sender echo); 0x06/29 server-gen; 0x15/0D/13 ABSORBED; 0x14 never on wire.
- StateUpdate ~10.4Hz/ship/peer (median 96ms). Chat = broadcast to ALL incl sender (1:N, NOT 1:2).
- NEW captures still needed: TEAM_DM (0x3F-41), mid-battle late-joiner (0x1E catch-up), isolated cloak, idle-ship force-resend (~0.5s? not 1.0s).

## Comprehensive Gap Analysis (2026-02-15)
- See [gap-analysis-20260215.md](gap-analysis-20260215.md) for full report
- 5 gaps: 1 High (DamageEventHandler missing), 2 Medium (time limit timer, 0x35 byte), 2 Low

### Settings Packet (0x00) Bytes RESOLVED
- **DAT_008e5f59** = collision damage toggle (WriteBit)
- **DAT_0097faa2** = friendly fire toggle (WriteBit)

### Event Handler Gaps
- DamageEventHandler (ET_WEAPON_HIT) NOT registered = damage scoring always zero
- DeletePlayerHandler/ProcessNameChangeHandler not registered = cosmetic only

### Stock Disconnect Flow
- Engine handles C++ side (0x17, 0x18 opcodes sent automatically)
- Python DeletePlayerHandler only rebuilds UI list; scores preserved for reconnect

## Key Protocol Facts (Verified)

### ENCRYPTION FULLY IMPLEMENTED AND VERIFIED (2026-02-09)
- Cipher: Custom stream cipher with fixed key "AlbyRules!" (10 bytes at 0x0095abb4)
- BYTE 0 NOT ENCRYPTED (direction flag: 0x01=server, 0x02=client, 0xFF=init)
- See [encryption-analysis.md](encryption-analysis.md)

### TGNetwork Message Framing (CORRECTED 2026-02-17)
- See [transport-header-format.md](transport-header-format.md) for FULL analysis
- byte[0]=direction, byte[1]=msg_count, byte[2+]=messages
- **CRITICAL**: Data messages use 16-bit LE flags_len field, NOT separate u8 totalLen + u8 flags
- Format: `[type:1][flags_len:2 LE][seq:2 LE][payload]`
- flags_len: bit15=reliable, bit14=priority, bit13=fragment, bit8=more_frags, bits13-0=totalLen
- ACK (type 0x01) uses DIFFERENT format: `[0x01][seq:2 LE][flags:1]` (4-5 bytes)
- Previous docs (tgnetwork-message-types.md) have WRONG header format

### Opcodes 0x35 and 0x37 (IDENTIFIED)
- **0x35**: Game state after NewPlayerInGame: [maxPlayers][totalSlots][FF][FF]
  - Stock sends totalSlots=0x09, we send 0x01 (still a bug)
- **0x37**: Player roster update for 2nd+ player joins

### StateUpdate Flag Split (VERIFIED from 30K+ packets)
- C->S: always 0x80 (WPN), never 0x20 (SUB)
- S->C: always 0x20 (SUB), never 0x80 (WPN)
- Mutually exclusive by direction in MP

### Stock Post-Join: 0x2A -> 0x35 -> 0x17 -> idle -> ObjCreateTeam
### Stock Post-Spawn: ObjCreateTeam -> ObjNotFound -> SUB cycling (100ms intervals)

### CollisionEffect (0x15) FULLY DECODED (2026-02-17)
- Wraps TGEvent with factory ID 0x00008124, event code 0x00800050
- Format: [opcode:1][typeClassId:i32][eventCode:i32][srcObjId:i32v][tgtObjId:i32v][count:u8][count * CompressedVec4Byte:4B][force:f32]
- CompressedVec4Byte = [dirX:s8][dirY:s8][dirZ:s8][magnitude:u8] (ship-relative, bounding-sphere-normalized)
- Write at 0x005871a0: parent TGEvent Write + WriteByte(count) + per-contact vtable+0x98 + WriteFloat(force)
- Read at 0x00587300: parent TGEvent Read + ReadByte(count) + per-contact vtable+0x9C + ReadFloat(force)
- Compression: vtable+0xA0 (0x006d29a0) normalizes Vec3 to 3 dir bytes; vtable+0xAC (0x006d2d10) adds magnitude byte
- Handler validates sender owns a collision object, checks bounding proximity, re-posts as 0x008000fc
- See [collision-effect-analysis.md](collision-effect-analysis.md) for full decode

### TGEvent Serialization Pattern (VERIFIED)
- Base TGEvent Write (FUN_006d6130, vtable+0x34): [typeClassId:i32][eventCode:i32][srcObjId:i32v][tgtObjId:i32v]
- Base TGEvent Read (FUN_006d61c0, vtable+0x38): reads 3 fields (code, src, tgt); typeClassId read separately by FUN_006d6200
- Event factory: FUN_006d6200 reads typeClassId, creates event via FUN_006f13e0, calls event->Read(stream)
- Event sender: FUN_006a17c0 writes [opcode_byte][event->Write(stream)], sends reliable to all peers
- Subclasses override Write/Read at vtable+0x34/+0x38 to add class-specific fields after calling parent

### Stream Vtable Map (TGBufferStream at PTR_LAB_00895c58)
- +0x50: ReadByte   | +0x54: WriteByte
- +0x58: ReadShort  | +0x5C: WriteShort
- +0x60: ReadInt32  | +0x64: WriteInt32 (variant)
- +0x68: ReadInt32  | +0x6C: WriteInt32 (FUN_006cf870)
- +0x70: ReadFloat  | +0x74: WriteFloat
- +0x80: ReadInt32v | +0x84: WriteInt32v (thunk to +0x6C)
- +0x98: WriteCompressedVec4Byte (4B: 3 dir + 1 mag)
- +0x9C: ReadCompressedVec4Byte
- +0xA0: CompressVec3ToDirBytes (normalize + 3 signed bytes + magnitude)
- +0xA8: CompressVec3 (3 dir bytes + CF16 magnitude = 5B standard)
- +0xAC: CompressVec4Byte (calls +0xA0, adds magnitude byte)
- +0xBC: DecompressVec4Byte (4 bytes -> Vec3 + magnitude)

## Collision Damage Comparison (2026-02-19)
- See [collision-damage-trace-comparison.md](collision-damage-trace-comparison.md)
- **ROOT CAUSE 1**: Stock server sends 14 PythonEvent (0x06) after collision (eventCode 0x00008129 + 0x00000101)
  - These trigger client-side AddDamage (18 DoDamage_FromPosition calls) = actual ship destruction
  - OpenBC sends ZERO PythonEvents -> client only gets 4 collision contact DoDamage (not lethal)
- **ROOT CAUSE 2**: Server-side ship+0x284 subsystem list order differs from client
  - Stock cycles: startIdx 0,2,6,8,10 | OpenBC cycles: startIdx 0,5,7,9
  - DeferredInitObject creates subsystems in wrong order -> client misreads subsystem bytes
  - This causes shield/hull/PTG flickering on client HUD
- **OpenBC sends 0x29 Explosion (2x)** but stock does NOT for same collision scenario
- CollisionEffect (0x15) sent identically by both servers (2x each)

## Ship_Deserialize Crash (2026-02-21) — REPRODUCIBLE
- See [ship-deserialize-crash-analysis.md](ship-deserialize-crash-analysis.md) for full decode
- **Crash**: NULL deref at 0x005A1FE9 (Ship_Deserialize+0x99), ESI=NULL, EDI=0x3FFFFFFF
- **Root cause**: Server sends ObjCreateTeam MISSING 4-byte factory_class_id prefix
  - Ship_Deserialize reads objectID (0x3FFFFFFF) as classID -> FUN_006f13e0 returns NULL
  - No NULL check in Ship_Deserialize before vtable+0x118 call
- **Trigger**: Ship destroyed by collision damage, then ~5s later server sends ObjCreateTeam
  - owner=1 (server's ship slot), team=0, position off-map (-1959,-51,333)
  - Uses DIFFERENT serialization: no classID, no name/set, full maxHP table (198 bytes vs 110)
- **Likely cause**: NewPlayerInGame (FUN_006a1e70) serializes destroyed ship via wrong vtable+0x10c
  - FUN_005a1dc0 (base class WriteStream at vtable 0x00893e9c / 0x0089423c) does NOT write classID
  - Destroyed/invalid ship may have different vtable than live ship
- **3rd crash** at 0x006D621C (TGEvent factory): same NULL pattern, different deserialization path
- **Occurred twice** in one session (18:04:20 and 18:31:24), identical registers both times

## Valentine's Day Wire Format Cross-Reference (2026-02-23)
- See [valentines-wire-gaps.md](valentines-wire-gaps.md) for full analysis

### TorpedoFire (0x19) — ARC DATA UNDOCUMENTED
- flags2 bit0=has_arc, bit1=has_target
- When has_arc + no target: 8 trailing bytes after cv3 velocity (not documented)
  - First 4 bytes look like ReadInt32v (source ship ID?), last 4 unknown
- When has_target: target_id (ReadInt32v) + impact data (4 bytes, not 5 as doc says)
- Needs RE of FUN_0057CB10 (TorpedoSystem::SendFireMessage) to fully decode

### PythonEvent2 (0x0D) — NOT RELAYED, CLIENT-ORIGINATED (CORRECTED 2026-02-24)
- Jump table entry for 0x0D goes directly to FUN_0069f880 (no relay)
- ALL observed instances carry factory 0x0000010C (TGObjPtrEvent) + eventCode 0x00800058 (TARGET_WAS_CHANGED)
- **3x verified**: Valentine 75x C->S, stock-dedi server 31x C->S / 0x S->C, client 15x (inverted labels)
- **Direction**: ALWAYS client -> server. Server absorbs, never relays.
- Client sends targeting changes to server via 0x0D; server does not forward to other clients
- Valentine analysis line 483 cloak note still valid — cloak propagates via StateUpdate CLK flag

### 0x28+0x00+0x01 Bundling — CONFIRMED
- Stock ALWAYS bundles [ACK][0x28 ChecksumComplete][0x00 Settings][0x01 GameInit] in ONE UDP datagram
- 0x28 has no payload (6 bytes total with transport header)
- Verified 3/3 player joins in Valentine's trace

### Keepalive — Two Formats
- **Full** (22+ bytes): type=0x00, reliable+ordered, slot + IP:4 + name:UTF-16LE+null. Handshake only.
- **Short** (1 byte): type=0x00, just the type byte. Steady-state heartbeat.

### Graceful Disconnect (type 0x05)
- First payload byte always 0x0A, then 8 bytes data
- Server ACKs with seq=2, retransmits 7x at ~0.67s intervals
- TGBootMessage (type 0x04) never observed on wire

## Timing Constraints Catalog (2026-02-23)
- See [timing-constraints.md](timing-constraints.md) for full report
- Key values: ~45s peer timeout, ~12s keepalive, 1.0s retransmit, 9.5s explosion
- CRITICAL: Collision cooldown (DAT_0089054c) not yet extracted from binary
- CRITICAL: 0x28+0x00+0x01 MUST be bundled in single UDP datagram
- Stock StateUpdate ~10Hz/ship, PythonEvent ~2/sec combat, CollisionEffect ~0.16/sec

## Stock Dedi Server-Side Relay Audit (2026-02-24)
- See [relay-audit-20260224.md](relay-audit-20260224.md) for full analysis
- Session: 2-player stock BC dedi, 21min, 6 peers (3 player connections + reconnects)

### CLIENT PROXY DIRECTION BUG (CRITICAL)
- `socket_and_input_hooks.inc.c` labels sendto="S->C" and recvfrom="C->S"
- This is CORRECT for server, INVERTED for client
- All previous client-trace direction analysis was backwards
- 0x0D "S->C at client" = actually C->S (client sending)
- 0x36 "C->S at client" = actually S->C (client receiving)

### Relay Classification (from server perspective)
| Opcode | C->S | S->C | Behavior |
|--------|------|------|----------|
| 0x07 StartFiring | 174 | 172 | RELAYED to other clients |
| 0x08 StopFiring | 86 | 87 | RELAYED |
| 0x0A SubsysStatus | 60 | 71 | RELAYED + server-generated (shield toggles on death) |
| 0x0D PythonEvent2 | 31 | 0 | NOT RELAYED — absorbed by server |
| 0x10 StartWarp | 2 | 2 | RELAYED |
| 0x11 RepairPriority | 4 | 4 | RELAYED |
| 0x12 SetPhaserLevel | 5 | 5 | RELAYED |
| 0x13 HostMsg | 3 | 0 | NOT RELAYED — server-only processing |
| 0x15 CollisionEffect | 2 | 0 | NOT RELAYED — server generates 0x06 damage instead |
| 0x19 TorpedoFire | 110 | 110 | RELAYED |
| 0x1B TorpTypeChange | 1 | 1 | RELAYED |
| 0x1C StateUpdate | 23994 | 45355 | RELAYED + server-generated |
| 0x2A NewPlayerInGame | 4 | 0 | NOT RELAYED — server-only processing |
| 0x2C ChatMessage | 5 | 10 | RELAYED to ALL clients incl sender (echo) |

### Server-Only Generated (never received from clients)
| Opcode | Count | Notes |
|--------|-------|-------|
| 0x00 Settings | 5 | Per-join handshake |
| 0x01 GameInit | 5 | Per-join handshake |
| 0x03 ObjCreateTeam | 8 S->C | Server creates objects (also 7 C->S = relayed) |
| 0x06 PythonEvent | 529 | ALL server-generated: 310x 0x101, 209x 0x10C, 10x 0x8129 |
| 0x17 DeletePlayerUI | 7 | Server-generated player list updates |
| 0x1D ObjNotFound | 16 | S->C only (corrects docs: not C->S) |
| 0x1F EnterSet | 4 | S->C only (corrects docs: not C->S) |
| 0x28 ChecksumComplete | 5 | Bundled with Settings+GameInit |
| 0x35 GameState | 4 | Per-join game state |
| 0x36 ScoreChange | 10 | ALL server-generated, sent to all clients |
| 0x37 PlayerRoster | 6 | Per-join roster update |

### Never Observed on Wire
- 0x14 DestroyObj — zero instances in entire session
- 0x29 Explosion — zero instances in entire session (stock dedi)
- 0x04 Boot (dead opcode, uses TGBootPlayerMessage type 0x04 at transport level)
- 0x0E/0x0F StartCloak/StopCloak — zero (no cloaking ships in this session)

### Direction Corrections vs Previous Docs
- **0x1D ObjNotFound**: Was "C->S only" → actually S->C only (server broadcasts)
- **0x1F EnterSet**: Was "C->S only" → actually S->C only (server broadcasts)
- **0x0D PythonEvent2**: Confirmed NOT relayed (3rd independent verification)
- **0x15 CollisionEffect**: NOT relayed by stock dedi (server absorbs + generates 0x06 damage)
- **0x13 HostMsg**: NOT relayed (server processes locally, no response)

## ACK below32 Flag (2026-02-25)
- See [below32-ack-mechanism.md](below32-ack-mechanism.md) for full analysis
- ACK flags byte bit 1 = is_below_0x32: identifies which reliable seq counter channel
- below32=1 for types 0x00-0x05, below32=0 for type 0x32+
- HandleACK CHECK 1 compares ACK.below32 against retxQ entry GetType() < 0x32
- **OpenBC bug**: Not sending below32=1 for ConnectAck/DataMsg ACKs -> retxQ never drains
- **OpenBC spec gap**: transport-layer.md says ACK flags bit 1 is "unused" — it is is_below_0x32

## Files Reference
- [below32-ack-mechanism.md](below32-ack-mechanism.md) - ACK below32 flag analysis
- [openbc-test-20260225.md](openbc-test-20260225.md) - OpenBC test session 2026-02-25
- [valentines-wire-gaps.md](valentines-wire-gaps.md) - Valentine's Day wire format gaps
- [timing-constraints.md](timing-constraints.md) - Protocol timing catalog
- [relay-audit-20260224.md](relay-audit-20260224.md) - Stock dedi relay audit
