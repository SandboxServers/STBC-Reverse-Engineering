# Stock Dedicated Server Relay Audit — 2026-02-24

## Session Details
- **Server**: Stock BC dedicated server with passive proxy DLL (OBSERVE_ONLY mode)
- **Duration**: ~21 minutes (19:47:07 — 20:08:xx)
- **Players**: 2 humans (Cady=local, XFS01 Dauntless=remote), 3 reconnections
- **Traces**: `game/stock-dedi/packet_trace.log` (41.9MB), `game/stock-dedi/message_trace.log` (10.8MB)

## Peer Map
| Peer | Address | Player | Notes |
|------|---------|--------|-------|
| Peer#0 | 10.10.10.239:57857 | — | GameSpy LAN scanner |
| Peer#1 | 98.187.133.199:54760 | XFS01 Dauntless | First connection |
| Peer#2 | 10.10.10.239:57858 | — | GameSpy scanner |
| Peer#3 | 127.0.0.1:57859 | Cady | Local client (entire session) |
| Peer#4 | 98.187.133.199:53023 | XFS01 Dauntless | Reconnect #1 |
| Peer#5 | 98.187.133.199:63646 | XFS01 Dauntless | Reconnect #2 |
| Peer#6 | 81.205.81.173:27900 | — | GameSpy master server |

## CLIENT PROXY DIRECTION BUG

**CRITICAL DISCOVERY**: The proxy DLL's direction labeling in `socket_and_input_hooks.inc.c` uses:
- `sendto` → "S->C"
- `recvfrom` → "C->S"

This is correct when running on the SERVER (sendto = server sending to client = S->C).
When the same DLL runs on a CLIENT, labels are INVERTED (sendto = client sending = should be C->S).

**Impact**: ALL previous client-trace direction analyses were backwards.
- Client "S->C" = actually C->S (client is sending)
- Client "C->S" = actually S->C (client is receiving)

Verified by cross-referencing identical packets seen at both server and client:
- Server: `19:47:21.136 C->S Peer#3` 0x0D PythonEvent2 (received FROM client)
- Client: `19:47:21.136 S->C` same bytes (client SENT this via sendto, mislabeled S->C)

## Complete Relay Audit

### RELAYED Opcodes (server receives from one client, sends to other clients)

| Opcode | Name | C->S | S->C | Relay Ratio | Notes |
|--------|------|------|------|-------------|-------|
| 0x07 | StartFiring | 174 | 172 | ~1:1 | To all OTHER clients |
| 0x08 | StopFiring | 86 | 87 | ~1:1 | To all OTHER clients |
| 0x0A | SubsysStatus | 60 | 71 | 1:1+ | ALSO server-generated (shield toggles on death/respawn) |
| 0x10 | StartWarp | 2 | 2 | 1:1 | To all OTHER clients |
| 0x11 | RepairPriority | 4 | 4 | 1:1 | To all OTHER clients |
| 0x12 | SetPhaserLevel | 5 | 5 | 1:1 | To all OTHER clients |
| 0x19 | TorpedoFire | 110 | 110 | 1:1 | To all OTHER clients |
| 0x1B | TorpTypeChange | 1 | 1 | 1:1 | To all OTHER clients |
| 0x1C | StateUpdate | 23994 | 45355 | relay + generate | S->C ≈ 2x C->S (server also generates for all objects) |
| 0x2C | ChatMessage | 5 | 10 | 1:2 | Relayed to ALL clients INCLUDING sender (echo) |

### NOT RELAYED (server absorbs, processes locally)

| Opcode | Name | C->S | S->C | What Server Does Instead |
|--------|------|------|------|--------------------------|
| 0x0D | PythonEvent2 | 31 | 0 | Dispatches to FUN_0069f880 locally; target change absorbed |
| 0x13 | HostMsg | 3 | 0 | Self-destruct request processed locally |
| 0x15 | CollisionEffect | 2 | 0 | Processes collision, generates 0x06 PythonEvent damage |
| 0x2A | NewPlayerInGame | 4 | 0 | Triggers join handshake locally |

### SERVER-ONLY GENERATED (never received from clients)

| Opcode | Name | S->C | Notes |
|--------|------|------|-------|
| 0x00 | Settings | 5 | Per-join handshake |
| 0x01 | GameInit | 5 | Per-join handshake |
| 0x06 | PythonEvent | 529 | 310x TGSubsystemEvent(0x101), 209x TGObjPtrEvent(0x10C), 10x ObjectExploding(0x8129) |
| 0x17 | DeletePlayerUI | 7 | Player list updates |
| 0x1D | ObjNotFound | 16 | Sent WITH ObjCreateTeam (CORRECTS docs: was "C->S only") |
| 0x1F | EnterSet | 4 | Set transition broadcast (CORRECTS docs: was "C->S only") |
| 0x28 | ChecksumComplete | 5 | Bundled with Settings+GameInit |
| 0x35 | GameState | 4 | Per-join state |
| 0x36 | ScoreChange | 10 | Always paired: sent to ALL clients simultaneously |
| 0x37 | PlayerRoster | 6 | Per-join roster update |

### BIDIRECTIONAL (server relays client + generates its own)

| Opcode | C->S | S->C | Server-Generated |
|--------|------|------|------------------|
| 0x03 | ObjCreateTeam | 7 | 8 | Yes — server creates objects for respawning ships |
| 0x0A | SubsysStatus | 60 | 71 | Yes — shield toggles on death, ~11 server-generated |
| 0x1C | StateUpdate | 23994 | 45355 | Yes — server sends state for all objects |

### NEVER OBSERVED ON WIRE

| Opcode | Name | Notes |
|--------|------|-------|
| 0x04 | Boot (dead) | Uses TGBootPlayerMessage at transport level |
| 0x05 | (dead) | Jump table default |
| 0x09 | StopFireAtTarget | Never occurred in this session |
| 0x0B | AddToRepairList | Never occurred |
| 0x0C | ClientEvent | Never occurred |
| 0x0E | StartCloak | No cloaking ships |
| 0x0F | StopCloak | No cloaking ships |
| 0x14 | DestroyObject | Zero instances (stock dedi never sends this) |
| 0x1A | BeamFire | Zero instances (surprising!) |
| 0x29 | Explosion | Zero instances (stock dedi never sends this on wire) |

## Key Findings

### 1. CollisionEffect (0x15) is NOT Relayed
The server receives 0x15 from the client that detected the collision, validates it locally, and generates 0x06 PythonEvent damage events (ObjectExploding 0x8129 + SubsystemDamage 0x0101) which are sent to ALL clients. The 0x15 itself never reaches other clients.

### 2. PythonEvent2 (0x0D) is Client->Server Only
All 31 instances carry TGObjPtrEvent with eventCode TARGET_WAS_CHANGED (0x00800058). Clients inform the server of target changes. Server absorbs them.

### 3. HostMsg (0x13) is Client->Server Only
3 self-destruct requests, all absorbed by server. No relay, no response.

### 4. ChatMessage (0x2C) Echoes to Sender
Unlike other relayed opcodes, chat is sent to ALL clients including the original sender. 5 messages -> 10 sends.

### 5. Direction Corrections
- **0x1D ObjNotFound**: Previously documented as C->S only. Actually S->C only (server proactively informs clients).
- **0x1F EnterSet**: Previously documented as C->S only. Actually S->C only (server broadcasts set transitions).

### 6. 0x29 Explosion and 0x14 DestroyObject: Zero Instances
Neither appears in the entire 21-minute stock dedi session despite multiple ship deaths. Ship death uses 0x06 PythonEvent (ObjectExploding 0x8129) instead.
