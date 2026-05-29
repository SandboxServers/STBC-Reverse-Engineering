> [docs](../README.md) / [networking](README.md) / gamespy-discovery.md

---
title: GameSpy Discovery & Master Server Protocol — RE Analysis
type: reference + explanation
audience: re-engineer
validated: 2026-05-28
methodology: FUNCTION_DOC_WORKFLOW_V5
binary:
  name: stbc.exe
  size: 6182400
  base: 0x00400000
status: partial
evidence:
  - claim: "qr_handle_query at 0x006ac1e0 — dispatcher loops query-type table at 0x0095a71c with 8 entries (basic/info/rules/players/status/packets/echo/secure)"
    address: 0x006ac1e0
    function: qr_handle_query
    confidence: high
    note: "Table at 0x0095a71c byte-confirmed (8 DWORD entries → 8 query-type strings)."
  - claim: "gs_rc4_cipher at 0x006ac050 — modified GameSpy QR1 PRGA: i = (data[n] + 1 + i) % 256 (standard RC4 is i = (i+1) % 256)"
    address: 0x006ac050
    function: gs_rc4_cipher
    confidence: high
    note: "Decompile shows uVar5 = (uint)(byte)(*(char *)(iVar4 + param_3) + '\\x01' + (char)uVar5) — byte-confirmed."
  - claim: "qr_send_heartbeat at 0x006aca60 — formats `\\heartbeat\\<port>\\gamename\\bcommander` from 0x0095a904, sendto to master sockaddr at DAT_00995880"
    address: 0x006aca60
    function: qr_send_heartbeat
    confidence: high
    note: "Format string at 0x0095a904 byte-confirmed; %d arg = *(undefined4 *)(param_1 + 0xe4), %s arg = param_1 + 8 (gamename buffer)."
  - claim: "SL_create_broadcast_socket at 0x006aa720 — socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP) + setsockopt(SOL_SOCKET, SO_BROADCAST), stores socket at ServerList+0x88"
    address: 0x006aa720
    function: SL_create_broadcast_socket
    confidence: high
    note: "socket(2, 2, 0x11); setsockopt(s, 0xffff, 0x20, ...). Result stored at param_1+0x88 (byte offset)."
  - claim: "SL_send_lan_broadcast at 0x006aa770 — htons port loop, sendto `\\status\\` (8 bytes from 0x0095a554) to 255.255.255.255 across port range"
    address: 0x006aa770
    function: SL_send_lan_broadcast
    confidence: high
    note: "Source string at 0x0095a554, length 8; broadcast socket read from ServerList+0x88."
  - claim: "qr_heartbeat_tick at 0x006abd80 — 30000ms interval, max 10 repetitions (counter at qr_t+0xE8), stale window 300,001ms"
    address: 0x006abd80
    function: qr_heartbeat_tick
    confidence: high
    note: "Constants byte-confirmed: 30000 < DVar2 - uVar1; '\\n' < cVar3 (10 max); 0x493e1 (300,001) stale-window check; counter at qr_t+0xE8; socket at qr_t+0x04; last-tick at qr_t+0xD8."
  - claim: "gs_validate_encode at 0x006abf70 — standard base64 (3 bytes → 4 chars) using gs_base64_char mapping at 0x006ac020"
    address: 0x006abf70
    function: gs_validate_encode
    confidence: high
    note: "Output for 6-byte challenge = exactly 8 chars + NUL."
  - claim: "SL_master_connect at 0x006aa4c0 — TCP client path: recv → strstr `\\secure\\` → RC4 → base64 → send auth + list request"
    address: 0x006aa4c0
    function: SL_master_connect
    confidence: high
    note: "Reads secret key from ServerList+0x2c (byte offset). Client-side only."
  - claim: "GameSpy::ctor at 0x0069bfa0 — sets vtable at 0x00895564, +0xED=0, +0xEE=1 (QR/host mode), +0xEF=0, loads TGL, registers handler 0x60006"
    address: 0x0069bfa0
    function: GameSpy__ctor
    confidence: high
    note: "Flag offsets at +0xED/+0xEE/+0xEF byte-confirmed."
  - claim: "GameSpy::Tick at 0x0069c440 — branching: if (+0xED==0) return; else if (+0xEE!=0) qr-mode; else server-list mode"
    address: 0x0069c440
    function: GameSpy__Tick
    confidence: high
    note: "Branch structure matches Section 12 pseudocode."
  - claim: "SL_start_update at 0x006ab620 — case 0/1/2/default mode dispatch (case 0 = Internet, case 2/3 = LAN)"
    address: 0x006ab620
    function: SL_start_update
    confidence: high
  - claim: "qr_send_packet at 0x006ac550 — appends `\\queryid\\%d.%d` from 0x0095a8c4, calls sendto"
    address: 0x006ac550
    function: qr_send_packet
    confidence: high
    note: "%d args: qr_t+0xDC (query seq, accessed as param_1[0x37] in some sites), qr_t+0xE0 (fragment counter, param_1[0x38])."
  - claim: "Secret key `\"Nm3aZ9\"` constructed on stack in FUN_0069c3a0 (GameSpy::InitBrowser); stored at qr_t+0x48 and ServerList+0x2C (both byte offsets)"
    address: 0x0069c3a0
    function: GameSpy__InitBrowser
    confidence: high
    note: "Stack literal byte-confirmed: 0x4e/0x6d/0x33/0x61/0x5a/0x39/0x00 = 'N','m','3','a','Z','9','\\0' (6 chars + NUL). Passed to FUN_006aa100 as param_3."
  - claim: "GameSpy vtable at 0x00895564 — 11 slots (scalar_deleting_destructor + 10 method slots)"
    address: 0x00895564
    function: null
    confidence: high
    note: "All 11 slot addresses byte-read and match Section 12 table verbatim."
  - claim: "Master server hostname 0x0095a4fc is the RUNTIME-MUTABLE target of masterserver.txt override (overwritten via _strncpy width 0x40 in FUN_006aa100); 0x0095a594 is the IMMUTABLE canonical source"
    address: 0x006aa100
    function: null
    confidence: high
    note: "FUN_006aa100 contains `_strncpy(s_stbridgecmnd01_activision_com_0095a4fc, local_100, 0x40)`. Fallback path copies from 0x0095a594 to 0x0095a4fc when masterserver.txt is absent. The 0x0095a834 third instance role is OQ3."
  - claim: "Dead code at 0x006ab558 — Ghidra has not disassembled this block. Raw bytes contain dead error-message RVAs (`Unable to resolve master`, `Connection to master reset`) but were never linked into the executable's reachable graph"
    address: 0x006ab558
    function: null
    confidence: high
    note: "`disassemble_function` returns 'No function found'. Stronger than 'no xrefs' — Ghidra does not recognize the address as code."
  - claim: "qr_t struct (CORRECTED 2026-05-28): byte 0x04=heartbeat socket; byte 0x48=secret key buffer; byte 0xD8=last heartbeat timestamp; byte 0xDC=query seq counter; byte 0xE0=fragment counter; byte 0xE4=active flag AND heartbeat port (NOT 'packet counter'); byte 0xE8=heartbeat repetition counter (max 10)"
    address: 0x006abd80
    function: qr_heartbeat_tick
    confidence: high
    note: "C1 — see body. Pre-v5 table mixed DWORD indices with byte offsets. qr_t[0x37] (SOCKET*-indexed) and qr_t+0xDC (byte-indexed) refer to the SAME byte. FUN_006abce0 reads `param_1[0x39]` (DWORD idx 0x39 = byte 0xE4) as the active flag; FUN_006aca60 reads `*(undefined4 *)(param_1 + 0xe4)` as the heartbeat-port %d argument — same field, dual role."
  - claim: "ServerList struct (CORRECTED 2026-05-28): byte 0x88 = broadcast socket (NOT byte 0x22). Shared field used by both LAN broadcast (FUN_006aa770) and TCP master connect (FUN_006aa4c0)"
    address: 0x006aa720
    function: SL_create_broadcast_socket
    confidence: high
    note: "C2 — see body. Pre-v5 doc said `+0x22 SOCKET Broadcast socket`. 0x22 was a DWORD index (0x22 * 4 = 0x88). Decompile: FUN_006aa720 stores at `param_1 + 0x88` (byte); FUN_006aa770 reads from `param_1 + 0x88`; FUN_006aa4c0 (TCP master connect) also uses `param_1 + 0x88` — confirming it's a shared socket field."
  - claim: "ServerList+0x2C secret key — byte offset 0x2C (DWORD idx 0xB → byte 0x2C, both notations consistent here). Read by FUN_006aa4c0 at `param_1 + 0x2c`"
    address: 0x006aa4c0
    function: SL_master_connect
    confidence: high
    note: "C1-companion. The +0x2C value is unambiguous because DWORD-idx 0xB and byte-offset 0x2C land on the same byte."
  - claim: "qr_t+0xC8..+0xD4 callback table (basic/info/rules/players) — listed in pre-v5 doc; not byte-confirmed this pass"
    address: null
    function: null
    confidence: low
    note: "OQ1 — see Open Questions. Spot-checked FUN_006ac5f0 (basic builder) but the callback-table location was not confirmed."
companions:
  - docs/networking/gamespy-crypto-analysis.md
  - docs/protocol/transport-layer.md
  - docs/networking/network-protocol.md
  - docs/networking/multiplayer-flow.md
supersedes:
  - 2026-02-16
---

# GameSpy Discovery & Master Server Protocol

> [!NOTE]
> This doc is `status: partial`. **Algorithm + address claims byte-confirmed at high confidence**. 4 struct-offset table corrections needed (qr_t and ServerList layout tables mix DWORD indices with byte offsets — clarification). Master server hostname mechanism corrected: `0x0095a4fc` is the runtime-mutable target of `masterserver.txt`; `0x0095a594` is the immutable canonical source. RC4 PRGA modification, secret key `"Nm3aZ9"`, heartbeat timing (30s / max 10), vtable slots (11 at `0x00895564`), and base64 encoder all byte-confirmed. **C1** rewrites the qr_t Layout table in consistent byte-offset notation and renames `qr_t+0xE4` from "packet counter" to "active flag / heartbeat port number". **C2** corrects `ServerList` broadcast socket from "+0x22" to byte `+0x88` (the pre-v5 value was a DWORD index). **C3** retitles `qr_t+0xE4` references throughout the heartbeat narrative. **C4** rewrites the "duplicate master hostname" claim — `0x0095a4fc` is mutable, `0x0095a594` is immutable. **R1** sharpens the dead-code claim at `0x006ab558` to note that Ghidra has not even disassembled the block. See [v5-evidence-header.md](../guides/v5-evidence-header.md) for the standard. Source evidence: `.claude/agent-memory/game-archaeology-specialist/networking-foundation-gamespy-discovery-validation-20260528.md`.

Complete reverse-engineered analysis of Star Trek: Bridge Commander's GameSpy integration: LAN discovery, query/response protocol, and master server heartbeat. Verified against live stock dedicated server traces (2026-02-16) and byte-confirmed against `stbc.exe` (2026-05-28).

## Overview

BC uses the **GameSpy QR (Query & Reporting) SDK** for server-side query response and the **GameSpy ServerList SDK** for client-side server browsing. All GameSpy traffic shares the game's UDP socket and is distinguished from game traffic by the leading `\` (0x5C) byte.

- **Game name**: `"bcommander"` (hardcoded at `0x00959c24`)
- **Game version**: `60` (sent in responses as `\gamever\60`)
- **Master server**: `stbridgecmnd01.activision.com` (hardcoded at `0x0095a4fc`, dead since ~2012)
- **333networks master**: `81.205.81.173` (via `masterserver.txt`)
  - **Heartbeat port**: UDP 27900 (server → master, registration)
  - **List port**: TCP 28900 (client → master, server list browsing)
  - **Verify port**: UDP 27901 (master → server, status verification)
- **Game port**: UDP 22101 (0x5655)
- **LAN scan range**: UDP 22101-22201 (0x5655-0x56B9)

---

## 1. LAN Discovery Flow

### Step 1: Client Clicks "Start Query"

**Python layer** (`Multiplayer/MultiplayerMenus.py`):
- "Start Query" button fires `App.ET_REFRESH_SERVER_LIST` event with `SetBool(0)` (start=0, stop=1)
- LAN/Internet mode toggle (`ET_LOCAL_INTERNET_HOST`): int=0 for LAN, int=1 for Internet

**C++ layer** (`FUN_006ab620` at `0x006ab620`):
- Dispatches based on mode parameter: case 2 or 3 = LAN, case 0 = Internet
- Stores callback pointers and calls `FUN_006ad430` to initiate the search

### Step 2: Client Creates Broadcast Socket

**`FUN_006aa720`** at `0x006aa720` (SL_CreateBroadcastSocket):
```c
socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);   // socket(2, 2, 0x11)
setsockopt(s, SOL_SOCKET, SO_BROADCAST, &on, 4);  // setsockopt(s, 0xffff, 0x20, ...)
```
Socket stored at `ServerList+0x88`.

### Step 3: Client Broadcasts `\status\`

**`FUN_006aa770`** at `0x006aa770` (SL_SendLANBroadcast):
```c
// param_2 = 0x5655 (22101), param_3 = 0x56B9 (22201), param_4 = 1 (step)
sockaddr dest;
dest.sa_family = AF_INET;          // 2
dest.sa_data[2..5] = 0xFF;         // 255.255.255.255 (broadcast)

while ((short)port <= endPort) {
    dest.sa_data[0..1] = htons(port);
    sendto(socket, "\\status\\", 8, 0, &dest, 16);
    port += step;                   // increment by 1
}
```

**The client sends `\status\` (8 bytes) to `255.255.255.255` on every port from 22101 through 22201 — that's 101 UDP broadcasts.** After sending, it sets the ServerList state to "searching" and records `GetTickCount()` for timeout tracking.

### Step 4: Server Receives Query

The server's **peek-based UDP router** (in `game_loop_and_bootstrap.inc.c`) runs every game tick:

1. `select()` checks for pending data on the shared game socket
2. `recvfrom()` with `MSG_PEEK` reads the first byte
3. If byte is `\` (0x5C): this is a GameSpy query — consume the full packet and dispatch
4. If byte is binary (not `\`): leave it for `TGNetwork_Update` (game traffic)

The query is dispatched to **`FUN_006ac1e0`** (qr_handle_query).

### Step 5: Server Parses Query Type

**`FUN_006ac1e0`** at `0x006ac1e0` (qr_handle_query):

Iterates a table of 8 query type strings at `0x0095a71c` and uses `strstr`-based matching (`FUN_006ac450`):

| Index | String | Handler | What It Returns |
|-------|--------|---------|-----------------|
| 0 | `basic` | `FUN_006ac5f0` | Hostname, map, player count |
| 1 | `info` | `FUN_006ac7a0` | Extended server info |
| 2 | `rules` | `FUN_006ac810` | Game settings (timelimit, fraglimit, system, password) |
| 3 | `players` | `FUN_006ac880` | Connected player list |
| 4 | **`status`** | **All four above** | Combined response (basic + info + rules + players) |
| 5 | `packets` | All four + flush between each | Fragmented combined response |
| 6 | `echo` | `FUN_006ac8f0` | Reflects query data back |
| 7 | (secure) | Stores challenge string | For `\validate\` response |

**Since the LAN broadcast sends `\status\`, the server calls ALL FOUR builders sequentially (case 4).**

### Step 6: Server Builds Response

Each builder calls a registered callback that populates a response buffer with backslash-delimited key-value pairs.

**Basic callback** (`FUN_0069c580` at `0x0069c580`):

The basic info callback builds the core server identity. It reads from Python globals and engine state. **Verified field order** from trace (the basic+info callbacks produce these first):

```
\gamename\bcommander              # hardcoded game name
\gamever\60                       # hardcoded game version
\location\1                       # server location/region
\hostname\<serverName>            # or \hostname\*<name> if password-protected
\missionscript\<script>           # e.g. "Multiplayer.Episode.Mission1.Mission1"
\mapname\<displayName>            # calls Python GetMissionShortName() (e.g. "DM")
\numplayers\<count>               # from FUN_006a2650 (connected player count)
\maxplayers\<limit>               # reads Python Multiplayer.MissionMenusShared.g_iPlayerLimit
\gamemode\<mode>                  # from GameSpy object +0x14 (e.g. "openplaying")
```

When a password is set, hostname gets a `*` prefix: `\hostname\*My Server`

**Rules callback** (uses format string at `0x00959cf8`):
```
\timelimit\<value>                # reads Python g_iTimeLimit
\fraglimit\<value>                # reads Python g_iFragLimit
\system\<systemScript>            # SpeciesToSystem.GetScriptFromSpecies(g_iSystem)
\password\<0|1>                   # password protection flag
```

**Players callback**: Iterates connected players and adds `\player_N\<name>` entries.

**Info callback**: Additional server metadata.

### Step 7: Response Transmission

**Fragment handling** (`FUN_006ac660` at `0x006ac660`):
- Concatenates key-value pairs to the response buffer
- If total exceeds **0x545 bytes (1349)**, splits at a backslash boundary
- Sends the first fragment via `FUN_006ac550`, continues with remainder

**Send packet** (`FUN_006ac550` at `0x006ac550`):
- Appends `\queryid\<N>.<M>` where N = sequence counter (`qr_t+0x37`), M = fragment counter (`qr_t+0x38`)
- Calls `sendto()` to the client's source address
- Clears the buffer for the next fragment

**Final packet** (`FUN_006ac950` at `0x006ac950`):
- If a `\secure\` challenge was received: generates validation hash via RC4 (`FUN_006abf70`) and appends `\validate\<hash>`
- Appends `\final\`
- Sends via `FUN_006ac550`

### Step 8: Client Receives Response

The client polls its broadcast socket each frame:

1. `select()` with zero timeout checks for data
2. `recvfrom()` reads up to ~1500 bytes
3. Searches for `\final\` to know the response is complete
4. Extracts server IP and port from the `recvfrom` `sockaddr`
5. Adds server to the browser list with parsed hostname, map, player count
6. **3-second timeout**: if no more responses arrive within 3 seconds after the last one, closes the broadcast socket and fires `ET_REFRESH_SERVER_LIST_DONE`

---

## 2. Wire Format [v5-validated 2026-05-28]

### Query Packet (Client → Server)
```
\status\                                    8 bytes, LAN broadcast
\basic\                                     individual server query
\info\                                      individual query type
\rules\                                     individual query type
\players\                                   individual query type
\echo\<data>                                ping/echo test
\secure\<challenge_string>                  validation request
```

### Response Packet (Server → Client)

Verified from stock dedi trace (267 bytes, single unfragmented packet):
```
\gamename\bcommander\gamever\60\location\1\hostname\My Game23\missionscript\Multiplayer.Episode.Mission1.Mission1\mapname\DM\numplayers\0\maxplayers\8\gamemode\openplaying\timelimit\-1\fraglimit\-2\system\Multi1\password\0\player_0\Dedicated Server\final\\queryid\2.1
```

**Field order** (verified): gamename, gamever, location, hostname, missionscript, mapname, numplayers, maxplayers, gamemode, timelimit, fraglimit, system, password, player_N (for each connected player), final, queryid.

**Note**: `\final\` is followed by `\` (double backslash), then `queryid`. The response terminates with `\queryid\N.M` as the last field (no trailing backslash).

If password-protected, hostname gets `*` prefix:
```
\hostname\*My Server\...
```

**gamemode values**: `"openplaying"` = game in progress and accepting players, `"settings"` = in lobby

### Response Fragmentation [v5-validated 2026-05-28]
- Maximum packet payload: **1349 bytes** (0x545) — enforced at `FUN_006ac660` (`qr_append_fragment`)
- Fragments split at backslash boundaries
- Each fragment gets `\queryid\N.M` — N = query sequence (`qr_t+0xDC`), M = fragment index within query (`qr_t+0xE0`)
- Final fragment includes `\final\` (and optionally `\validate\<hash>`)

### Validation (Internet mode only)
```
Server receives:  \secure\<challenge>        (6-char challenge string)
Server computes:  Modified RC4 encrypt with key "Nm3aZ9", then Base64 encode
Server appends:   \validate\<8-char-hash>
```

See **Section 10** for full algorithm details, standalone C implementation, and binary function addresses.

---

## 3. Master Server Protocol

### Architecture: Pure UDP (No TCP)

The master server registration protocol is **entirely UDP**. The server sends heartbeats via `sendto()` and receives verification queries via the same GameSpy query socket. **TCP is never used server-side** — only the client uses TCP (via `SL_master_connect`) to browse the master server list.

This was verified by hooking `connect()`, `send()`, and `recv()` on the stock dedi — all three hooks installed successfully but never fired during an entire session. All master server communication went through the existing `sendto()`/`recvfrom()` hooks.

### Registration Flow

1. **Server sends UDP heartbeat** to master:27900
2. **Master server sends UDP `\status\` query** back to the game port to verify the server is alive
3. **Server responds** with full status response (same as LAN query)
4. **Master adds server** to its list and makes it available to clients

### Master Server Addresses [v5-validated 2026-05-28]

> [!IMPORTANT]
> **C4 — Pre-v5 doc treated the three hostname addresses as identical duplicates. They are not.** Two of them play distinct, load-bearing roles in the `masterserver.txt` override mechanism.

| Address | Role | Evidence |
|---------|------|----------|
| `0x0095a4fc` | **Runtime-mutable target** of `masterserver.txt` override | `FUN_006aa100` calls `_strncpy(s_stbridgecmnd01_activision_com_0095a4fc, local_100, 0x40)` — overwrites in-place with width 0x40. |
| `0x0095a594` | **Immutable canonical source** | Same function — fallback path copies from `0x0095a594` to `0x0095a4fc` when `masterserver.txt` is absent. |
| `0x0095a834` | Third instance — role not fully traced this pass | See Open Question OQ3. |

The original Activision hostname (`stbridgecmnd01.activision.com`) has been dead since ~2012. The master server sockaddr is stored at `0x00995880`. When hostname resolution fails (e.g. the canonical hostname no longer exists), this sockaddr stays zeroed and heartbeats silently fail (`sendto` returns -1 to `0.0.0.0:0`).

**333networks support — why it works**: When a `masterserver.txt` file exists in the game directory with a hostname or IP, the stock dedi resolves it and populates the sockaddr at `0x00995880`. The mechanism is **runtime overwrite of `0x0095a4fc`** (not a separate config path) — `FUN_006aa100` `strncpy`'s the resolved hostname into the original Activision hostname slot with width `0x40` (64 bytes). Heartbeats are then sent to the 333networks master server (e.g. `81.205.81.173:27900`).

### Verified Master Server Verification Queries (from stock dedi trace)

After the heartbeat, master servers query the dedi back via UDP on port 27901 to verify it's alive:

| Master Server IP | Port | Response Size | Notes |
|-----------------|------|---------------|-------|
| 150.230.23.146 | 27901 | 256 bytes | Query at T+16s |
| 116.202.247.76 | 27901 | 241 bytes | Query at T+25s |
| 49.13.114.72 | 27901 | 282 bytes | Query at T+5min |

These are `\status\` queries identical to LAN queries — the same response builder handles both. The varying response sizes reflect different player counts at the time of each query (e.g., 256 bytes with 0 players vs 282 bytes with 2 players).

### Heartbeat Format

**`FUN_006aca60`** at `0x006aca60` (qr_send_heartbeat):

```
\heartbeat\<port>\gamename\bcommander
```

With state change notification:
```
\heartbeat\<port>\gamename\bcommander\statechanged\<N>
```

**Verified from stock dedi trace** (packet #205987, sent to `81.205.81.173:27900`):
```
\heartbeat\0\gamename\bcommander\statechanged\1
```

**Heartbeat port value** [v5-validated 2026-05-28]: `\heartbeat\0` — the stock dedi reports port 0. The `%d` argument in the format string is `*(undefined4 *)(qr_t + 0xE4)` — this field serves a **dual role as both the heartbeat port number AND the QR active flag**. When the field is 0, you get `\heartbeat\0` (matching what stock traces show). When non-zero, it indicates the port offset from the base game port and the master server uses this to know which port to send verification queries to. See Section 4 qr_t Layout C1 for the field-naming correction.

> [!NOTE]
> **C3 — `qr_t+0xE4` was mislabeled as "packet counter" in the pre-v5 doc.** Decompile evidence: `FUN_006abce0` reads `param_1[0x39]` (DWORD idx 0x39 = byte 0xE4) as the active flag (`if (param_1[0x39] != 0)`); `FUN_006aca60` reads `*(undefined4 *)(param_1 + 0xe4)` as the heartbeat-port `%d` argument. Same field, same byte, two roles — when zero, the QR system is inactive AND the wire reports port 0.

**`\statechanged\1`**: Indicates the first state-change notification (player joined/left or game state changed). The `statechanged` flag tells the master server to re-query the game server for updated info.

**Heartbeat failure**: In the trace, `rc=-1` (sendto returned SOCKET_ERROR). The heartbeat was attempted but the send failed. Despite this, three master servers still queried us — they may have cached the server from a previous session or discovered it through other means (e.g., another client's query traffic).

Sent via `sendto()` to the master server sockaddr at `0x00995880` using the heartbeat socket at `qr_t+0x04`.

### Heartbeat Timing [v5-validated 2026-05-28]

**`FUN_006abd80`** at `0x006abd80` (qr_heartbeat_tick):

- Sends heartbeat every **30 seconds** (30000ms check — `30000 < DVar2 - uVar1` byte-confirmed)
- Tracks count at `qr_t+0xE8` (byte offset) — stops after **10 heartbeats** (counter > `'\n'` = 10)
- First heartbeat sent immediately (when `qr_t+0xD8` timestamp is 0 or stale > 300,001 ms — `0x493e1` byte-confirmed)
- Heartbeat socket at `qr_t+0x04` must not be `INVALID_SOCKET` (-1)

### Client Master Server Browsing (TCP, Client-Side Only)

**`FUN_006aa4c0`** (SL_master_connect):

**This is a client-only path.** The dedicated server never uses TCP — only clients use this to browse the internet server list.

**Verified from client trace** (TCP hooks captured the complete flow):

```
CLIENT                                              MASTER (81.205.81.173:28900)
  |                                                    |
  T+0ms    TCP connect ===============================>|
  |                                                    |
  T+6119ms <==== \basic\\secure\LRPOPQ (21 bytes)      |
  |                                                    |
  T+6119ms Auth ======================================>|
  |        \gamename\bcommander\gamever\1.6            |
  |        \location\0\validate\hMwdTNWS               |
  |        \final\\queryid\1.1\  (81 bytes)            |
  |                                                    |
  T+6119ms List request ==============================>|
  |        \list\cmp\gamename\bcommander\final\        |
  |        (36 bytes)                                  |
  |                                                    |
  T+6573ms <==== Binary server list (37 bytes)          |
  |        5 entries × 6 bytes (4=IP + 2=port)         |
  |        + \final\ terminator                        |
  |                                                    |
  T+6623ms Client sends \status\ to first server ====> |  (UDP to 72.206.34.241:29876)
```

**Key details from trace:**
- **Master server port is 28900** (not 28964 as in some GameSpy docs)
- **Challenge**: 6-char string (e.g. `LRPOPQ`), preceded by `\basic\` prefix
- **gamever in auth is `1.6`** (string version), not `60` (numeric version used in status responses)
- **Validate hash**: 8-char string (e.g. `hMwdTNWS`), computed from challenge + secret key via RC4
- **List filter**: `cmp` — likely a GameSpy comparison/filter string
- **Binary server list format**: 6 bytes per entry (4-byte IP big-endian + 2-byte port big-endian), terminated by `\final\`
- **6-second TCP delay**: The `connect()` returned immediately but the challenge wasn't received for ~6 seconds

**Decoded server list from trace:**
```
48 CE 22 F1 74 B4 → 72.206.34.241:29876
48 CE 22 F1 74 B5 → 72.206.34.241:29877
48 CE 22 F1 74 B6 → 72.206.34.241:29878
48 CE 22 F1 74 CC → 72.206.34.241:29900
48 CE 22 F1 56 55 → 72.206.34.241:22101
```

After receiving the list, the client immediately sends `\status\` UDP queries to each server to get their details for the server browser.

Format string at `0x0095a624`:
```
\gamename\%s\gamever\%s\location\0\validate\%s\final\\queryid\1.1\
```

Filter/list format at `0x0095a5cc`:
```
\list\%s\gamename\%s\final\
```

### Shutdown

**`FUN_006abe00`** (qr_send_exit): Sends an "exiting" heartbeat to the master server.

**`FUN_006abe40`** (qr_shutdown):
- `closesocket()` on both query and heartbeat sockets
- Sets both to `INVALID_SOCKET` (0xFFFFFFFF)
- Frees qr_t if not the static instance (checks against `DAT_0095a740`)
- Calls `WSACleanup()`

---

## 4. GameSpy Object Layout

### GameSpy Object (0xF4 bytes, at UtopiaModule+0x7C = 0x0097FA7C)

| Offset | Type | Field |
|--------|------|-------|
| +0x00 | vtable* | vtable pointer |
| +0x14 | char[~64] | gameMode string (e.g. "settings", "playing") |
| +0xDC | qr_t* | Server-side Query/Report struct (NULL if not hosting) |
| +0xE0 | ServerList* | Client-side server browser (NULL if not browsing) |
| +0xE4 | float | Last ServerList poll time |
| +0xE8 | void* | TGL file handle (`Multiplayer.tgl`) |
| +0xEC | byte | Flag: initialized |
| +0xED | byte | Flag: active (tick processing enabled) |
| +0xEE | byte | Flag: isHost (1=server, 0=client) |
| +0xEF | byte | Flag: queryOnly (skip heartbeat, LAN mode) |

### qr_t Layout (CORRECTED 2026-05-28, byte offsets) [v5-validated-corrected]

> [!IMPORTANT]
> **C1 — Pre-v5 table mixed DWORD indices (e.g. `+0x37`, `+0x38`) with byte offsets (e.g. `+0x48`, `+0xE4`).** Decompile-side, Ghidra renders the same field two different ways depending on the cast: `qr_t[0x37]` (SOCKET*-indexed = DWORD-indexed) and `qr_t + 0xDC` (byte-indexed) refer to the **same byte**. The table below uses byte offsets exclusively, with the DWORD index annotated for cross-reference. The `+0xE4` "Packet counter" entry is also corrected — see note below table.

| Byte offset | DWORD idx | Type | Field |
|-------------|-----------|------|-------|
| 0x00 | 0 | SOCKET | Query socket (receives GameSpy queries) |
| 0x04 | 1 | SOCKET | Heartbeat socket (sends to master server) |
| 0x08 | 2 | char[] | Gamename buffer (holds `"bcommander"`, used as `%s` in heartbeat format) |
| 0x48 | 0x12 | char[~48] | Secret key buffer (holds `"Nm3aZ9"`) |
| 0xC8 | 0x32 | callback* | basic_callback (builds basic response section) `[OQ1]` |
| 0xCC | 0x33 | callback* | info_callback (builds info response section) `[OQ1]` |
| 0xD0 | 0x34 | callback* | rules_callback (builds rules response section) `[OQ1]` |
| 0xD4 | 0x35 | callback* | players_callback (builds players response section) `[OQ1]` |
| 0xD8 | 0x36 | DWORD | Last heartbeat timestamp (GetTickCount) — stale window 300,001 ms |
| 0xDC | 0x37 | DWORD | Query sequence counter (`queryid` N) |
| 0xE0 | 0x38 | DWORD | Fragment counter within query (`queryid` M) |
| **0xE4** | **0x39** | DWORD | **Active flag AND heartbeat port number** (NOT "packet counter") |
| 0xE8 | 0x3A | byte | Heartbeat repetition counter (max 10) |

**Field-naming evidence**:

- `qr_t+0xDC` (query seq): `FUN_006ac1e0` reads as `*(int *)(param_1 + 0xdc)` (byte-indexed) and increments. `FUN_006ac550` accesses the same byte as `param_1[0x37]` (SOCKET*-indexed) for the `\queryid\N.M` `%d` argument.
- `qr_t+0xE0` (fragment counter): `FUN_006ac550` writes `param_1[0x38] = SVar2 + 1;` — DWORD index 0x38 = byte 0xE0.
- `qr_t+0xE4` (active flag + heartbeat port — **C1 correction**): `FUN_006abce0` (`qr_process_queries`) gates query processing on `if (param_1[0x39] != 0)` — DWORD idx 0x39 = byte 0xE4. **The same field** is read by `FUN_006aca60` (`qr_send_heartbeat`) as `*(undefined4 *)(param_1 + 0xe4)` and formatted as the heartbeat port number (`\heartbeat\<port>`). When the field is 0 the QR system is "inactive" AND the wire reports port 0.
- `qr_t+0xE8` (heartbeat counter): `FUN_006abd80` increments and compares against `'\n'` (10). DWORD idx 0x3A = byte 0xE8.

The callback-table addresses at `qr_t+0xC8..+0xD4` (OQ1) were spot-checked via `FUN_006ac5f0` (basic builder) but the callback-table location was not byte-confirmed this pass. Defer to a deeper qr_t struct dig if needed.

### ServerList Layout (CORRECTED 2026-05-28, byte offsets) [v5-validated-corrected]

> [!IMPORTANT]
> **C2 — Pre-v5 doc said `+0x22 SOCKET Broadcast socket`.** The value `0x22` was a DWORD index (0x22 * 4 = 0x88). The byte-offset truth is `+0x88`, and the same field is used for **both** LAN broadcast (UDP) and TCP master connect — it is a shared socket field, not two separate slots. Same mixing-of-bases issue as C1.

| Byte offset | DWORD idx | Type | Field |
|-------------|-----------|------|-------|
| 0x2C | 0xB | char[] | Secret key buffer (holds `"Nm3aZ9"`, used for validate hash) |
| 0x88 | 0x22 | SOCKET | **Shared socket** — UDP broadcast (LAN scan) AND TCP master connect |
| 0x8C | 0x23 | DWORD | Last activity timestamp (3-second timeout) |

**Field-access evidence**:

- `+0x88` shared socket — `FUN_006aa720` (`SL_create_broadcast_socket`) stores the UDP broadcast socket at `param_1 + 0x88`; `FUN_006aa770` (`SL_send_lan_broadcast`) reads from `param_1 + 0x88`; `FUN_006aa4c0` (`SL_master_connect`, TCP) also uses `param_1 + 0x88`. The LAN-vs-Internet mode dispatch in `SL_start_update` selects which kind of socket gets created, but the slot is shared.
- `+0x2C` secret key — the +0x2C value is unambiguous because DWORD index 0xB and byte offset 0x2C land on the same byte. `FUN_006aa4c0` reads from `param_1 + 0x2c`. The same `"Nm3aZ9"` constructed in `GameSpy::InitBrowser` (`0x0069c3a0`) is stored here for the client-side browsing path.

---

## 5. Function Address Table

### GameSpy Object Methods

| Address | Name | Description |
|---------|------|-------------|
| 0x0069bfa0 | GameSpy::ctor | Constructor: allocates 0xF4, loads TGL, registers handlers |
| 0x0069c140 | GameSpy::dtor | Destructor: sends exit heartbeat, closes sockets |
| 0x0069c440 | GameSpy::Tick | Per-frame: polls query socket (host) or ServerList (client) |
| 0x0069c580 | GameSpy::BuildBasicResponse | Builds hostname/map/numplayers/maxplayers/gamemode |
| 0x0069cc40 | GameSpy::SetGameModeHandler | Event 0x109: updates gameMode string |
| 0x0069d720 | GameSpy::ProcessQueryHandler | Event 0x867: routes query to QR handler |

### QR SDK Functions (Server-Side)

| Address | Name | Description |
|---------|------|-------------|
| 0x006abca0 | qr_process_all | Heartbeat check + query processing |
| 0x006abcc0 | qr_process_queries_only | Query processing without heartbeat |
| 0x006abce0 | qr_process_queries | select()+recvfrom() loop on query socket |
| 0x006abd80 | qr_heartbeat_tick | 30-second heartbeat timer, max 10 repeats |
| 0x006abe00 | qr_send_exit | Sends "exiting" heartbeat to master |
| 0x006abe40 | qr_shutdown | closesocket() both sockets, WSACleanup() |
| 0x006ac1e0 | qr_handle_query | Main dispatcher: matches query type, calls builders |
| 0x006ac450 | qr_match_type | strstr-based query type matching |
| 0x006ac550 | qr_send_packet | Appends queryid, calls sendto() |
| 0x006ac5f0 | qr_build_basic | Invokes basic callback at qr_t+0xC8 |
| 0x006ac660 | qr_append_fragment | Append data + fragment if > 1349 bytes |
| 0x006ac7a0 | qr_build_info | Invokes info callback at qr_t+0xCC |
| 0x006ac810 | qr_build_rules | Invokes rules callback at qr_t+0xD0 |
| 0x006ac880 | qr_build_players | Invokes players callback at qr_t+0xD4 |
| 0x006ac8f0 | qr_build_echo | Reflects query data back |
| 0x006ac950 | qr_send_final | Appends \validate\ + \final\, sends |
| 0x006aca60 | qr_send_heartbeat | Sends `\heartbeat\<port>\gamename\bcommander` |

### ServerList SDK Functions (Client-Side)

| Address | Name | Description |
|---------|------|-------------|
| 0x006aa720 | SL_create_broadcast_socket | UDP socket with SO_BROADCAST |
| 0x006aa770 | SL_send_lan_broadcast | Sends `\status\` to 255.255.255.255 across port range |
| 0x006aab40 | SL_process | Per-frame state machine processing |
| 0x006ab150 | SL_query_server | Individual server query with ping measurement |
| 0x006ab620 | SL_start_update | Initiates refresh: mode 0=Internet, 2/3=LAN |

### Master Server Functions

| Address | Name | Description |
|---------|------|-------------|
| 0x006aa4c0 | SL_master_connect | TCP to master:28900, challenge-response auth (**client-side only**) |

### Crypto Functions

| Address | Name | Description |
|---------|------|-------------|
| 0x006ac050 | gs_rc4_cipher | Modified RC4 encrypt (GameSpy QR1 variant, see Section 10) |
| 0x006abf70 | gs_validate_encode | Base64 encode (3 input bytes → 4 output chars) |
| 0x006ac020 | gs_base64_char | Base64 character mapping (A-Za-z0-9+/) |
| 0x006ac1c0 | gs_swap_byte | Trivial byte swap helper for RC4 S-box |
| 0x0069c3a0 | GameSpy::InitBrowser | Constructs secret key `"Nm3aZ9"` on stack, passes to SL init |

---

## 6. Data Section Addresses

### Format Strings

| Address | String |
|---------|--------|
| 0x00959c24 | `bcommander` (game name) |
| 0x00959c50 | `\gamename\%s\gamever\%s\location\%d` |
| 0x00959c74 | `\gamemode\%s` |
| 0x00959c84 | `\maxplayers\%d` |
| 0x00959c94 | `\numplayers\%d` |
| 0x00959ca4 | `\mapname\%s` |
| 0x00959cc4 | `\missionscript\%s` |
| 0x00959cd8 | `\hostname\%s` |
| 0x00959ce8 | `\hostname\*%s` (password-protected) |
| 0x00959cf8 | `\timelimit\%d\fraglimit\%d\system\%s\password\%d` |
| 0x0095a554 | `\status\` (LAN broadcast query payload) |
| 0x0095a58c | `\basic\` |
| 0x0095a5cc | `\list\%s\gamename\%s\final\` |
| 0x0095a624 | `\gamename\%s\gamever\%s\location\0\validate\%s\final\\queryid\1.1\` |
| 0x0095a678 | `\final\` |
| 0x0095a8c4 | `\queryid\%d.%d` |
| 0x0095a8d4 | `\echo\%s` |
| 0x0095a8e0 | `\validate\%s` |
| 0x0095a8f0 | `\statechanged\%d` |
| 0x0095a904 | `\heartbeat\%d\gamename\%s` |

### Query Type Table (at 0x0095a71c, 8 DWORD pointers)

| Index | Pointer | String |
|-------|---------|--------|
| 0 | 0x0095a8ac | `basic` |
| 1 | 0x0095a8a4 | `info` |
| 2 | 0x0095a89c | `rules` |
| 3 | 0x0095a894 | `players` |
| 4 | 0x0095a88c | `status` |
| 5 | 0x0095a884 | `packets` |
| 6 | 0x0095a87c | `echo` |
| 7 | 0x0095a874 | (secure challenge) |

### Static Buffers

| Address | Size | Purpose |
|---------|------|---------|
| 0x00995578 | 255 | Static recvfrom buffer for query socket |
| 0x00995880 | 16 | sockaddr_in for master server |
| 0x0095a740 | — | Static qr_t address (for free-check in shutdown) |
| 0x0095a4fc | — | `"stbridgecmnd01.activision.com"` (master hostname) |

---

## 7. Verified LAN Discovery Sequence (from stock dedi trace)

```
CLIENT (10.10.10.239)                               SERVER (10.10.10.1)
  |                                                    |
  |-- Click "Start Query" (LAN mode)                   |
  |   SL_create_broadcast_socket + SO_BROADCAST        |
  |   SL_send_lan_broadcast ports 22101-22201          |
  |                                                    |
  | ===== \status\ to 255.255.255.255:22101 =========> |
  |   (101 broadcasts, one per port)                   |
  |                                                    |
  |                     Peek router: byte[0]='\'       |
  |                     recvfrom() consumes packet      |
  |                     qr_handle_query → case 4        |
  |                     Builds ALL fields into 1 packet |
  |                                                    |
  | <===== 267 bytes from server:22101 =============== |
  |   \gamename\bcommander\gamever\60\location\1       |
  |   \hostname\My Game23\missionscript\Multi...       |
  |   \mapname\DM\numplayers\0\maxplayers\8            |
  |   \gamemode\openplaying\timelimit\-1               |
  |   \fraglimit\-2\system\Multi1\password\0           |
  |   \player_0\Dedicated Server                       |
  |   \final\\queryid\2.1                              |
  |                                                    |
  |-- Parse response, add to server browser list       |
  |-- 3-second timeout → close broadcast socket        |
```

**Observed timing** (from packet_trace.log):
- LAN queries arrive from multiple IPs/ports (each client uses a fresh ephemeral port per query)
- Response is immediate (<1ms after query received)
- queryid increments per query: 2.1, 3.1, 4.1, 5.1 (starts at 2 in this session)

---

## 8. Verified Connection Handshake (from stock dedi trace)

Complete client-to-server join sequence captured on stock dedi. All timestamps from a single session, relative to Connect at T=0.

```
CLIENT (10.10.10.239:59405)                          SERVER (stock dedi)
  |                                                    |
  T+0ms    Connect (0x03) ============================>|
  |                                                    |
  T+2ms   <==== Connect (0x03) + ChecksumReq round 0  |
  |              dir="scripts/" filter="App.pyc"       |
  |              (non-recursive)                       |
  T+2ms   <==== ACK                                    |
  |                                                    |
  T+9ms    ACK + ACK + Keepalive (player name) =======>|
  |         "C.a.d.y.2." (wide chars)                  |
  |                                                    |
  T+11ms  <==== Keepalive echo + ACK                   |
  |                                                    |
  T+17ms   ChecksumResp round 0 ======================>|
  |                                                    |
  T+17ms  <==== ACK + ChecksumReq round 1              |
  |              dir="scripts/" filter="Autoexec.pyc"  |
  |              (non-recursive)                       |
  |                                                    |
  T+26ms   ChecksumResp round 1 ======================>|
  |                                                    |
  T+26ms  <==== ACK + ChecksumReq round 2              |
  |              dir="scripts/ships" filter="*.pyc"    |
  |              (RECURSIVE)                           |
  |                                                    |
  T+38ms   ChecksumResp round 2 (FRAGMENTED: 3 parts)=>|
  |         seq=512, flags=0xA1, 418+441 bytes         |
  |                                                    |
  T+41ms  <==== ACK + ChecksumReq round 3              |
  |              dir="scripts/mainmenu" filter="*.pyc" |
  |              (non-recursive)                       |
  |                                                    |
  T+53ms   ChecksumResp round 3 ======================>|
  |                                                    |
  T+53ms  <==== ACK + ChecksumReq round 255 (0xFF)     |
  |              dir="Scripts/Multiplayer" filter="*.pyc"
  |              (RECURSIVE) — final/multiplayer round |
  |                                                    |
  T+63ms   ChecksumResp round 255 (FRAGMENTED) =======>|
  |         first-response crc=0x8794D13F              |
  |                                                    |
  T+66ms  <==== 0x28 (ChecksumComplete, no payload)    |
  |        <==== 0x00 Settings:                        |
  |              gameTime=35.84 collision=1 ff=0       |
  |              slot=0 map="Multi...Mission1"         |
  |        <==== 0x01 GameInit (trigger, no payload)   |
  |         (ALL THREE in one 65-byte packet!)         |
  |                                                    |
  T+113ms  ACKs for seq 5,6,7 ========================>|
  |                                                    |
  T+140ms  0x2A NewPlayerInGame =======================>|
  |         trailing byte: 0x20 (space)                |
  |                                                    |
  T+142ms <==== ACK + 0x35 GameState [08 01 FF FF]     |
  |        <==== 0x17 DeletePlayerUI (clear stale UI)  |
  |                                                    |
  T+5006ms ConnectAck (0x05) =========================>|
  |         + batch of 12 ACKs for all game messages   |
  |                                                    |
  T+10084ms                                            |
  |        ====> HEARTBEAT to 81.205.81.173:27900      |
  |              \heartbeat\0\gamename\bcommander      |
  |              \statechanged\1  (rc=-1, failed)      |
  |                                                    |
  T+16s   <==== Master 150.230.23.146:27901 \status\   |
  |        ====> 256-byte response (0 players)         |
  T+25s   <==== Master 116.202.247.76:27901 \status\   |
  |        ====> 241-byte response                     |
  T+5min  <==== Master 49.13.114.72:27901 \status\     |
  |        ====> 282-byte response (2 players)         |
```

### Key Observations

1. **5 checksum rounds** (not 4): rounds 0, 1, 2, 3, and 0xFF (255). Round 0xFF is the final "multiplayer scripts" round.
2. **Checksums complete in ~66ms**: entire checksum exchange from Connect to Settings delivery.
3. **Opcode 0x28** appears between checksums and Settings. No payload. Signals "checksums complete".
4. **Settings + GameInit bundled**: Both sent in one packet immediately after 0x28.
5. **ConnectAck at +5 seconds**: Transport-level ConnectAck arrives ~5 seconds after Connect, well after the game handshake is complete. This is a delayed transport confirmation, not part of the game flow.
6. **Round 2 and 255 are RECURSIVE** (`flag=0x21`): scan subdirectories. These produce large fragmented checksum responses.
7. **Keepalive contains player name**: Wide-char encoded name in the Keepalive payload, sent immediately after Connect.
8. **0x35 GameState data**: `[08 01 FF FF]` — byte 0 = max players (8), byte 1 = lobby state (0x01), bytes 2-3 = 0xFFFF.
9. **0x17 DeletePlayerUI**: Sent right after GameState to clear stale scoreboard entries.

### Checksum Rounds (verified)

| Round | Dir | Filter | Recursive | Typical Response Size |
|-------|-----|--------|-----------|----------------------|
| 0 | `scripts/` | `App.pyc` | No | ~26 bytes |
| 1 | `scripts/` | `Autoexec.pyc` | No | ~22 bytes |
| 2 | `scripts/ships` | `*.pyc` | Yes | ~418+441 bytes (fragmented) |
| 3 | `scripts/mainmenu` | `*.pyc` | No | ~46 bytes |
| 255 | `Scripts/Multiplayer` | `*.pyc` | Yes | ~279 bytes (fragmented) |

---

## 9. Verified Internet Server Browsing (from client trace)

Complete client-side master server browsing flow captured via TCP hooks. The client connects to the 333networks master to get a list of online servers, then queries each one individually.

```
CLIENT                                              MASTER (81.205.81.173:28900)
  |                                                    |
  T+0ms    TCP connect ===============================>|
  |         socket=2116, result=0 (success)            |
  |                                                    |
  T+6119ms <==== \basic\\secure\LRPOPQ (21 bytes)      |
  |         challenge = "LRPOPQ" (6 chars)             |
  |                                                    |
  T+6119ms Auth response =============================>|
  |         \gamename\bcommander\gamever\1.6            |
  |         \location\0\validate\hMwdTNWS               |
  |         \final\\queryid\1.1\  (81 bytes)            |
  |                                                    |
  T+6119ms List request ==============================>|
  |         \list\cmp\gamename\bcommander\final\        |
  |         (36 bytes)                                  |
  |                                                    |
  T+6573ms <==== Binary server list (37 bytes)          |
  |         5 entries × 6 bytes + \final\ terminator   |
  |                                                    |
  T+6623ms Client queries each server via UDP =======>  (individual \status\ queries)
```

### Binary Server List Format

Each entry is 6 bytes: 4-byte IP (big-endian) + 2-byte port (big-endian). List terminated by `\final\`.

**Decoded from trace:**
```
48 CE 22 F1 74 B4 → 72.206.34.241:29876
48 CE 22 F1 74 B5 → 72.206.34.241:29877
48 CE 22 F1 74 B6 → 72.206.34.241:29878
48 CE 22 F1 74 CC → 72.206.34.241:29900
48 CE 22 F1 56 55 → 72.206.34.241:22101
```

After receiving the list, the client immediately sends `\status\` UDP queries to each server to populate the server browser. Only servers that respond appear in the list.

### Key Details

- **Master port**: TCP 28900 (not 28964 as in some generic GameSpy documentation)
- **Challenge format**: `\basic\\secure\<6-char-challenge>` — the `\basic\` prefix is always present
- **Auth gamever**: `"1.6"` (string version), distinct from status response gamever `"60"` (numeric)
- **List filter**: `"cmp"` — passed as the `%s` in `\list\%s\gamename\%s\final\`
- **TCP timing**: `connect()` returns immediately but challenge receipt is delayed ~6 seconds (master server processing time)
- **Internet before LAN**: When both modes are active, the master server query fires first; LAN broadcasts follow ~4 seconds later

---

## 10. Challenge-Response Crypto (GameSpy QR1 SDK) [v5-validated 2026-05-28]

The validate hash computation used in both server-side `\secure\`/`\validate\` exchange and client-side master server auth. Fully reverse-engineered from the binary — the algorithm is the well-known GameSpy QR1 SDK crypto, widely reimplemented in open-source projects (OpenSpy, gslist, etc.).

### Secret Key

**`"Nm3aZ9"`** — 6 bytes, hardcoded. Constructed on stack in `GameSpy::InitBrowser` (`0x0069c3a0`). The stack literal is byte-confirmed: bytes `0x4e 0x6d 0x33 0x61 0x5a 0x39 0x00` = `'N' 'm' '3' 'a' 'Z' '9' '\0'` (6 chars + NUL), set via individual stack stores then passed to `FUN_006aa100` as `param_3`.

Not present as a standalone string in the data section — only exists as a stack-constructed literal. Stored at:
- `qr_t+0x48` (byte offset; same field is reachable as `qr_t[0x12]` if cast to `DWORD*`) — server-side QR path
- `ServerList+0x2C` (byte offset; DWORD idx 0xB) — client-side browsing path

### Algorithm: Modified RC4 + Base64

**Step 1: Modified RC4 Cipher** (`gs_rc4_cipher` at `0x006ac050`) [v5-validated 2026-05-28]

Standard RC4 Key Scheduling Algorithm (KSA): initialize S-box [0..255], permute using key bytes. The **modification** is in the Pseudo-Random Generation Algorithm (PRGA):

```
Standard RC4:  i = (i + 1) % 256
GameSpy QR1:   i = (data[n] + 1 + i) % 256
```

The plaintext byte itself is mixed into the S-box index before encryption. This is the signature difference of GameSpy's QR1 SDK variant. The encryption is in-place — the challenge buffer is modified directly. Decompile evidence:

```c
uVar5 = (uint)(byte)(*(char *)(iVar4 + param_3) + '\x01' + (char)uVar5);
```

That is precisely `i = (data[n] + 1 + i) % 256` (byte-confirmed against the binary 2026-05-28).

**Step 2: Base64 Encode** (`gs_validate_encode` at 0x006abf70)

Standard base64 encoding using the canonical RFC 4648 alphabet (`A-Za-z0-9+/`), implemented via `gs_base64_char` (0x006ac020). Three input bytes produce four output characters. For a 6-byte challenge, output is exactly 8 characters + NUL terminator.

### Complete Flow

```
Input:  challenge = "LRPOPQ" (6 bytes)
        secret    = "Nm3aZ9" (6 bytes)

Step 1: gs_rc4_cipher("Nm3aZ9", 6, "LRPOPQ", 6)
        → 6 encrypted bytes (in-place, overwrites challenge)

Step 2: gs_validate_encode(encrypted, 6, output)
        → "hMwdTNWS" (8 printable chars)

Output: \validate\hMwdTNWS
```

### Where It's Used

**Server-side** (`qr_send_final` at 0x006ac950):
1. Master server sends `\secure\<challenge>` to the game server (UDP query)
2. Server computes validate hash from challenge + secret key
3. Server appends `\validate\<hash>` to the status response before `\final\`

**Client-side** (`SL_master_connect` at 0x006aa4c0):
1. Client connects to master via TCP port 28900
2. Master sends `\basic\\secure\<challenge>` (21 bytes)
3. Client computes validate hash: `gs_rc4_cipher(key, 6, challenge, 6)` then `gs_validate_encode(challenge, 6, output)`
4. Client sends `\gamename\bcommander\gamever\1.6\location\0\validate\<hash>\final\\queryid\1.1\`

Both paths use the identical key and algorithm — the crypto is symmetric.

### Standalone C Implementation

```c
/* GameSpy QR1 modified RC4 cipher */
static void gs_rc4_cipher(const char *key, int keyLen,
                          unsigned char *data, int dataLen) {
    unsigned char S[256];
    int i, j = 0, n;
    unsigned char tmp;

    /* KSA: standard RC4 key scheduling */
    for (i = 0; i < 256; i++) S[i] = (unsigned char)i;
    for (i = 0; i < 256; i++) {
        j = (j + S[i] + (unsigned char)key[i % keyLen]) % 256;
        tmp = S[i]; S[i] = S[j]; S[j] = tmp;
    }

    /* PRGA: modified — mixes plaintext byte into index */
    i = 0; j = 0;
    for (n = 0; n < dataLen; n++) {
        i = (data[n] + 1 + i) % 256;       /* GameSpy modification */
        j = (j + S[i]) % 256;
        tmp = S[i]; S[i] = S[j]; S[j] = tmp;
        data[n] ^= S[(S[i] + S[j]) % 256];
    }
}

/* Standard base64 encode */
static const char b64[] =
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";

static void gs_validate_encode(const unsigned char *in, int inLen,
                               char *out) {
    int i, o = 0;
    for (i = 0; i < inLen; i += 3) {
        unsigned int triple = (in[i] << 16)
            | ((i+1 < inLen ? in[i+1] : 0) << 8)
            | (i+2 < inLen ? in[i+2] : 0);
        out[o++] = b64[(triple >> 18) & 0x3F];
        out[o++] = b64[(triple >> 12) & 0x3F];
        out[o++] = b64[(triple >>  6) & 0x3F];
        out[o++] = b64[ triple        & 0x3F];
    }
    out[o] = '\0';
}

/* Compute validate hash from challenge */
static void gs_compute_validate(const char *challenge,
                                char *out /* min 9 bytes */) {
    unsigned char buf[128];
    int len = strlen(challenge);
    memcpy(buf, challenge, len);
    gs_rc4_cipher("Nm3aZ9", 6, buf, len);
    gs_validate_encode(buf, len, out);
}
```

### Calling Into the Binary

Alternatively, call the existing functions at their known addresses:

```c
typedef void (__cdecl *PFN_gs_rc4)(const char*, int, unsigned char*, int);
typedef void (__cdecl *PFN_gs_b64)(const unsigned char*, int, char*);

#define GS_RC4_CIPHER  ((PFN_gs_rc4)0x006ac050)
#define GS_VALIDATE_ENC ((PFN_gs_b64)0x006abf70)

static void compute_validate(const char *challenge, char *out) {
    unsigned char buf[128];
    int len = strlen(challenge);
    memcpy(buf, challenge, len);
    GS_RC4_CIPHER("Nm3aZ9", 6, buf, len);
    GS_VALIDATE_ENC(buf, len, out);
}
```

---

## 11. Implications for Dedicated Server

### What Works
- GameSpy object is created during Phase 2 bootstrap (`UtopiaModule::SetupNetwork`)
- QR SDK query handling runs via the game loop tick
- Response builder reads Python globals (hostname, player count, map name)
- The peek-based UDP router correctly separates GameSpy queries from game traffic

### Requirements for LAN Discovery
1. **GameSpy object must exist** at UtopiaModule+0x7C (created during network setup)
2. **GameSpy+0xED (active) must be 1** for GameSpy::Tick to process queries
3. **GameSpy+0xEE (isHost) must be 1** for server-side query processing
4. **qr_t (GameSpy+0xDC) must be non-NULL** with a bound query socket
5. **Python globals must be set**: `g_iPlayerLimit`, `g_iTimeLimit`, `g_iFragLimit`, server name
6. **The peek-based UDP router** must route `\`-prefixed packets to the QR handler

### For 333networks Master Server Support
To register with a modern master server (e.g. 333networks), the dedicated server needs:
1. Resolve the master server hostname to get a valid sockaddr
2. Store it at the master server sockaddr location (or pass it to `qr_send_heartbeat`)
3. Set `GameSpy+0xEF (queryOnly) = 0` to enable heartbeat sending
4. Ensure the heartbeat socket (`qr_t+0x04`) is created and bound
5. The heartbeat format `\heartbeat\<port>\gamename\bcommander` is already compatible with 333networks

**Verified**: The stock dedi with a `masterserver.txt` file sends heartbeats to the 333networks master at `81.205.81.173:27900`. The heartbeat was attempted but `sendto()` returned -1 (SOCKET_ERROR). Despite the failed heartbeat, three different 333networks master servers (150.230.23.146, 116.202.247.76, 49.13.114.72) queried the server back on port 27901 — confirming the server was reachable and the master servers knew about it.

**Open question**: Why did the heartbeat `sendto()` fail? Possible causes:
- The heartbeat socket (`qr_t+0x04`) may not be properly bound
- Firewall may be blocking outbound UDP to port 27900
- The `\heartbeat\0` port value (port 0) may confuse something in the send path

### Current Status
LAN discovery is functional on both the stock dedi and our headless dedicated server. The GameSpy::Tick processes queries via the QR SDK each frame, and the response builder correctly reads Python globals to report server name, map, player count, and game rules.

Master server registration works via pure UDP heartbeats. The stock dedi with `masterserver.txt` pointing to 333networks sends heartbeats to `81.205.81.173:27900` and receives verification queries from master servers on port 27901. The full flow (heartbeat → verification query → response) is captured in the observer's packet trace.

### Verified Response Fields (from stock dedi trace)
| Field | Example Value | Source |
|-------|---------------|--------|
| gamename | `bcommander` | Hardcoded |
| gamever | `60` | Hardcoded |
| location | `1` | Config |
| hostname | `My Game23` | Python `ServerName` |
| missionscript | `Multiplayer.Episode.Mission1.Mission1` | Python mission module |
| mapname | `DM` | Python `GetMissionShortName()` |
| numplayers | `0` | Connected player count |
| maxplayers | `8` | Python `g_iPlayerLimit` |
| gamemode | `openplaying` | GameSpy+0x14 mode string |
| timelimit | `-1` | Python `g_iTimeLimit` (-1 = disabled) |
| fraglimit | `-2` | Python `g_iFragLimit` (-2 = disabled) |
| system | `Multi1` | Python `SpeciesToSystem` mapping |
| password | `0` | Password protection flag |
| player_0 | `Dedicated Server` | Host player name |

---

## 12. GameSpy Object Internals (Deep Dive)

### GameSpy Vtable (`PTR_FUN_00895564`) [v5-validated 2026-05-28]

All 11 slot addresses byte-read against `stbc.exe` and match the table verbatim.

| Slot | Address | Name |
|------|---------|------|
| 0 | 0x0069c110 | scalar_deleting_destructor |
| 1 | 0x0069c080 | (tiny stub, undefined) |
| 2 | 0x0069c090 | (tiny stub, undefined) |
| 3 | 0x006f1650 | base class virtual |
| 4 | 0x0069c530 | (tiny stub, undefined -- likely StartQR?) |
| 5 | 0x0069c540 | (tiny stub, undefined -- likely StopQR?) |
| 6 | 0x006f27f0 | base class virtual |
| 7 | 0x006f2810 | base class virtual |
| 8 | 0x006f15c0 | base class virtual |
| 9 | 0x0069c0d0 | (tiny stub, undefined) |
| 10 | 0x0069c0e0 | (tiny stub, undefined) |

### SWIG Interface

The GameSpy class has NO direct SWIG wrappers. Access is through UtopiaModule:
- `Appc.UtopiaModule_CreateGameSpy(self)` -> FUN_00445fc0 (creates GameSpy object)
- `Appc.UtopiaModule_GetGameSpy(self)` -> returns `self[0x1F]` = UtopiaModule+0x7C
- `Appc.UtopiaModule_TerminateGameSpy(self)` -> FUN_00446010 (destroys GameSpy object)

### Tick/Update Function (FUN_0069c440)

Called every frame. Logic branches:

```
if (+0xED == 0)  // not enabled
    return;

if (+0xEE != 0)  // QR mode
    if (+0xEF != 0)  // shutdown-only mode
        FUN_006abcc0(+0xDC)  // process queries only (no heartbeat)
    else
        FUN_006abca0(+0xDC)  // process queries + heartbeat timer
else  // browser mode
    if (enough time elapsed && +0xEC == 0)
        FUN_006aab40(+0xE0)  // process server list
```

### Event System Integration

| Event ID | Name | Description |
|----------|------|-------------|
| 0x0109 | ET_SET_GAME_MODE | Updates GameSpy+0x14 settings string |
| 0x0867 | (GameSpy query event) | Incoming query data from network layer |
| 0x60006 | (GameSpy message) | Event handler registration token |

Event handlers:
- **SetGameModeHandler** (FUN_0069cc40): Copies game mode string to GameSpy+0x14
- **ProcessQueryHandler** (FUN_0069d720): Dispatches incoming queries (event 0x867) to qr_parse_query

Both registered in FUN_0069c4e0 via FUN_006da130.

### Dead Code: QR Initialization (`0x006ab558`-`0x006ab5BF`) [v5-validated 2026-05-28]

A block of bytes exists at `0x006ab558`-`0x006ab5BF` that contains RVA references to:
- "Unable to resolve master" (`0x0095a6e4`)
- "Connection to master reset" (`0x0095a6c8`)

This code would resolve the master server hostname and fill `to_00995880` (the heartbeat destination sockaddr), and likely create/bind the QR UDP socket.

> [!NOTE]
> **R1 — stronger than "no xrefs".** Pre-v5 doc said Ghidra finds no xrefs to this block. The v5 validation pass found a stronger statement: **Ghidra does not recognize `0x006ab558` as code at all.** `disassemble_function` returns "No function found". The bytes exist as raw data containing dead error-message RVAs but were never disassembled — they have never been linked into the executable's reachable graph. This is dead code from the GameSpy QR1 SDK that was compiled into the binary but never called.

### Why QR Never Self-Activates

1. GameSpy constructor sets `+0xEE=1` (QR mode) and `+0xDC=0` (qr_t pointer)
2. Tick function calls `FUN_006abca0(NULL)` which uses static qr_t at `0x0095a740`
3. Static qr_t is entirely zeroed -- all fields are 0
4. `qr_process_incoming_queries` checks `qr_t[0x39]` (active flag — byte 0xE4, **see C1**) -- it's 0, so returns immediately
5. `qr_process_heartbeat_timer` checks `qr_t+0x04` (heartbeat socket) against -1 -- socket 0 IS != -1, so it would try to send... but:
6. The `to_00995880` sockaddr is zeroed (family=0, port=0, addr=0.0.0.0) -- sendto() to 0.0.0.0:0 fails silently
7. No code ever calls the qr_init function to create/bind sockets, resolve master hostname, or set the active flag

The stock dedicated server works around this by having the proxy DLL set up the QR system externally.

---

## 13. Open Questions

Items that need follow-up investigation. These are documented here to surface debt rather than silently drop.

### OQ1 — `qr_t+0xC8..+0xD4` callback table not byte-confirmed

The pre-v5 doc lists basic/info/rules/players callback pointers at `qr_t+0xC8`, `+0xCC`, `+0xD0`, `+0xD4`. v5 spot-checked `FUN_006ac5f0` (the basic builder) but did not confirm the actual callback-table location in `qr_t`. The doc body still uses these offsets as a working theory; treat them as `confidence: low` until a deeper qr_t struct dig confirms the field addresses.

### OQ2 — Heartbeat `sendto` rc=-1 with `masterserver.txt` present

In the stock dedi trace, the heartbeat to `81.205.81.173:27900` returned `SOCKET_ERROR` (-1). The master sockaddr at `0x00995880` would stay zeroed if `masterserver.txt` resolution failed, but the trace indicates `masterserver.txt` was present — so the resolution presumably succeeded. Despite the failed `sendto`, three 333networks master servers (`150.230.23.146`, `116.202.247.76`, `49.13.114.72`) still queried the dedi back on port 27901. Hypotheses worth pursuing:
- The heartbeat socket at `qr_t+0x04` may not be properly bound when `\heartbeat\` is formatted.
- Firewall may be blocking outbound UDP to port 27900.
- The `\heartbeat\0` port value (qr_t+0xE4 = 0) may be rejected by the master.
- Inbound master queries may come from a separate discovery mechanism (cached server from a prior session, or another client's query traffic).

Unresolved this pass.

### OQ3 — `0x0095a834` third hostname instance

Pre-v5 doc treated `0x0095a834` as a third duplicate of the master hostname string. v5 verified the runtime-mutable (`0x0095a4fc`) and immutable canonical (`0x0095a594`) roles (see C4), but the `0x0095a834` role was not fully traced this pass. Possibilities: a third runtime cache, a debug-string copy, or genuinely a duplicate. Defer to a string-xref sweep.

---

## Cross-Anchors

- **Companion**: [docs/networking/gamespy-crypto-analysis.md](gamespy-crypto-analysis.md) — full crypto algorithm depth; Section 10 of this doc cross-links there.
- **Anchor (shared socket / cipher boundary)**: [docs/protocol/transport-layer.md](../protocol/transport-layer.md).
- **Family index**: [docs/networking/README.md](README.md).
- **Engine anchors** (UtopiaModule base `0x0097FA00`, TGWinsockNetwork at `+0x78`, GameSpy at `+0x7C`): pre-validated by protocol-family foundations. Confirmed at `FUN_0069c580` via `DAT_0097fa78`.
