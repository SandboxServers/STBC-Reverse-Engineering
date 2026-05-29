---
name: crash-patch-lineage-20260529
description: Engine bug lineage behind 10 binary patches; OpenBC applicability matrix; bug-condition + defensive-action per patch.
metadata:
  type: project
---

# Crash-Patch Lineage v5 — 10 Binary/Runtime Fixes in STBC Proxy

**Date:** 2026-05-29
**Program fingerprint:** STBC.exe @ 0x00400000, image size 6,394,712, 18,635 fns (Ghidra DB)
**Scope:** The 10 "Key Fixes Applied" listed in CLAUDE.md, traced to root engine behavior via live Ghidra and mapped to OpenBC analog code paths.
**OpenBC reference path:** `C:\Users\Steve\source\projects\OpenBC\src` (C codebase, NOT Rust; ~25 source files across server/, client/, shared/).

## Per-patch entries

### #1 — TGL FindEntry NULL guard

| Field | Value |
|---|---|
| Patch site | 0x006D1E10 (function entry, 5-byte JMP into code cave) |
| Stock function | `FUN_006d1e10` = `TGL::FindEntry(this, key)`, `__thiscall`, RET 4 |
| Completeness score | 13.07 effective / 86.93 fixable (low — bare worker, no plate) |
| Confidence | high (full decompile + binary disasm + 30 xrefs) |
| Stock decompile | `if (key==0) return this+0x1c; iVar1 = FUN_006d1ea0(key); if (iVar1==-1) return this+0x1c; return *(int*)(this+0x14) + 4 + iVar1*0x18;` |
| Bug condition | When `this == NULL` and lookup misses, returns `0x1C` — a **non-NULL pointer to invalid memory**. All downstream NULL checks pass; deref crashes when reading entry+0x8 (= address 0x24). |
| Trigger in headless | TGL file fails to load (no UI atlas in dedi mode); manager `this` is NULL; downstream caller (e.g. text-rendering, scoreboard, MainWindow setup) crashes on first access to the bogus 0x1C "entry". |
| Bug class | **Stock-client architectural shortcut** — Totally Games optimized for the case where the manager always exists, no NULL check needed. Headless dedi violates that invariant. |
| Patch action | NULL-guard prepended at entry: `TEST ECX,ECX; JNZ +5; XOR EAX,EAX; RET 4`. Returns NULL instead of `this+0x1c` when `this` is NULL. |
| Bug also bites stock client? | Only on extreme edge case (corrupt install / mod with bad TGL). In retail this works because TGL manager is always non-NULL after Init. |
| OpenBC applicability | **DOES NOT APPLY (architecture).** OpenBC has no TGL system. The closest analog `find_entry()` in `src/server/event_bus.c:65` returns `NULL` correctly: `for(...) if(strcmp==0) return &g_events[i]; return NULL;`. There is no "magic this+0x1c" sentinel idiom anywhere in OpenBC. |
| OpenBC action | None required. |
| Test guard | Not needed — pattern absent. |

### #2 — Network NULL list guard (StateUpdate flags byte clearing)

| Field | Value |
|---|---|
| Patch site | 0x005B1D57 (5-byte JMP into code cave; replaces `MOV ECX,[ESP+0x14]; PUSH ECX` between flag-byte computation and `WriteChar` of flags into stream) |
| Stock function | `Ship__WriteStateUpdate` at 0x005B17F0, `__thiscall`, vtable slot 72 (+0x120) |
| Completeness score | 0.0 effective / 103.62 fixable (high plate but many magic numbers) |
| Confidence | high (full decompile, byte-level wire-format docs, 30K+ packet validation) |
| Stock decompile (relevant) | Flag-byte `uDirtyFlags` is OR'd with 0x20 (SUB) or 0x80 (WPN) **before** the subsystem/weapon round-robin payload-write loops. Loops at 0x005B1E73 (SUB) and 0x005B1F1F (WPN) walk `*(int*)(ship+0x284)` linked list. |
| Bug condition | Sender always sets 0x20 / 0x80 in the flags byte regardless of whether `ship+0x284` (subsystem/weapon list head) is NULL. If NULL, the round-robin loops write **zero** subsystem bytes — but the receiver parses 0x20/0x80 first, looks for the data, and either crashes or interprets the next byte as "subsystem index" → corrupt parse → ship reported as destroyed. |
| Trigger in headless | DeferredInitObject hadn't yet run on a ship; ship+0x284 is NULL; first StateUpdate fires before subsystem list is populated. |
| Bug class | **Dedi-specific (post-init race)** — in stock SP/MP, every ship has subsystems by the time replication begins. The dedi ship-creation pipeline (Python-driven, deferred) creates the C++ ship object **before** populating its subsystem list. |
| Patch action | Before `WriteChar(uDirtyFlags)`, check `[ESI+0x284]`. If NULL: `AND byte [ESP+0x18], 0x5F` (clears bits 0x20 and 0x80). Now flags byte truthfully advertises only the data actually written. |
| Bug also bites stock client? | No — ships always have subsystems before replication. |
| OpenBC applicability | **DOES NOT APPLY (architecture).** OpenBC's `bc_build_state_update()` in `src/shared/protocol/game_builders.c:296` takes `dirty_flags` + `field_data` as caller-provided. The caller controls both; the builder cannot lie about what's in `field_data`. The "subsystem list" is a flat array `cls->subsystems[]` attached to ship class definition, populated synchronously at class-load time. No deferred ship init exists. |
| OpenBC action | None required. The risk only re-emerges if OpenBC added late-binding subsystem allocation. |
| Test guard | Future regression: assert that StateUpdate payload length matches `popcount(dirty_flags & 0xA0) * sizeof_payload + ...`. |

### #3 — Subsystem hash check fix (anti-cheat false-positive kick)

| Field | Value |
|---|---|
| Patch site | 0x005B22B5 (5-byte CALL `FUN_005b5eb0` redirected to code cave) |
| Stock function | `ComputeSubsystemIntegrityHash` at 0x005B5EB0, `__fastcall(ecx=ship+0x27C)`. Called from `Ship__ReadStateUpdate` at 0x005B21C0. |
| Completeness score | 38.26 effective / 61.74 fixable (medium) |
| Confidence | high (full decompile, 12-slot hash chain verified, KICK event 0x008000F6 ID anchored) |
| Stock decompile | Hashes 12 subsystem-class slots at `ship+0x27C + {0x34..0x60}`: Hull/Shield/Power/Sensors/Impulse/Warp/Repair/Cloak/Torpedo/Phaser/Pulse/Tractor. Each slot NULL-checked; computes XOR-fold over base hash + 0..12 prop floats. |
| Bug condition (1) | When `ship+0x284` (subsystem list head) is NULL, `FUN_005b5eb0(ship+0x27C)` returns 0 (all 12 NULL checks pass through). Receiver compares received hash (which sender computed from valid subsystems) vs locally-computed 0 → MISMATCH. |
| Bug condition (2) | Stock multiplayer is **also** affected because per the wire-format-spec memo, sender at `Ship_WriteStateUpdate:005B1D96` emits hash bit=`!isHost` and receiver validates hash only when `isMultiplayer`. In MP host→client, sender bit=0 ⇒ no hash on wire ⇒ check skipped. But in **dedi**, the dedi acts as host while accepting StateUpdates from clients; the bug is path-dependent. |
| Trigger in headless | Header ship has no subsystem objects (no DeferredInitObject yet, or system ship); receiver parses opcode 0x1C with flag 0x01 + hash bit set → reads 2-byte hash → compares → MISMATCH → posts ET_BOOT_PLAYER (0x008000F6) → `BootPlayerHandler` at 0x00506170 sends type=4 sub=4 kick → "You have been disconnected from the host" on client. |
| Bug class | **Dedi-specific anti-cheat false positive** (stock devs assumed every ship has subsystems). |
| Patch action | Cave checks `[ESI+0x284]`. If NULL: `MOV ECX,EDI; ADD ESP,4; JMP 0x005b22c7` (forces CMP ECX,EDI to match received). If non-NULL: trampoline through `SubsysHashComputeAndTrace` then real hash. Anti-cheat STAYS ACTIVE for ships that have subsystems. |
| Bug also bites stock client? | No — local-player ship always has subsystems. |
| OpenBC applicability | **DOES NOT APPLY (architecture).** OpenBC has no hash-folded anti-cheat in StateUpdate. The "Settings packet uses 3x WriteBool_Bit" wire-format flow stays; the integrity hash byte is dead in MP per `subsystem-integrity-hash.md`. Additionally OpenBC server **generates** downstream StateUpdate from authoritative state (`src/server/main.c:156 bc_build_state_update(...)`), so there's no client-supplied hash to compare against. |
| OpenBC action | If OpenBC ever adds anti-cheat for inbound 0x1C: do NOT key it off subsystem list contents; key off a deterministic function of declared ship class + last applied damage events. |
| Test guard | Send a StateUpdate with flag 0x01 + hash_present=1 from a client to verify server doesn't kick (since OpenBC ignores hash). |

### #4 — Compressed vector read guard (vtable cascade)

| Field | Value |
|---|---|
| Patch site (a) | 0x006D2EB0 — `CompressedVector3_ReadVirtual` (3 params, RET 0xC) |
| Patch site (b) | 0x006D2FD0 — `CompressedVector4_ReadVirtual` (4 params, RET 0x10) |
| Stock function | Both wrap `*param_1` (stream vtable) calls: 3 ReadByte at vtable[+0x50] + 1 decode-vec at vtable[+0xb0/b4/b8]. CV4 also reads vtable[+0x58] for mag. |
| Completeness score | CV3 = 41.93 / CV4 = 37.11 (leaf functions, plate missing) |
| Confidence | high (decompile + byte-level prologue match in patch — `83 EC 0C 56 8B F1`) |
| Stock decompile (CV3) | `uVar1 = (**(code**)(*param_1 + 0x50))(); uVar2 = (**(code**)(*param_1 + 0x50))(); uVar3 = (**(code**)(*param_1 + 0x50))(); (**(code**)(*param_1 + 0xb8))(p2,p3,p4,uVar1,uVar2,uVar3);` |
| Bug condition | If the stream object's vtable pointer is corrupted (e.g. from upstream stack misalignment after a prior VEH-skipped call), **all four** virtual calls fault. VEH recovers each one by popping the return address. The fourth call's callee was supposed to clean 24 bytes via RET 0x18; since callee never ran, those bytes stay on the stack. The function epilogue (`POP ESI; ADD ESP,0xC; RET 0xC`) then pops garbage as RA. Cascades to next CV3 call with `this` offset 12 bytes wrong, reads "vtable" = 1, crashes at `CALL [1+0x50]` → AV at 0x00000051. |
| Trigger in headless | Network parse path with partial / malformed StateUpdate or BeamFire payload; combined with VEH recovery from upstream NULL deref it cascades through this function. |
| Bug class | **Stock bug latent** + **dedi-VEH-amplified cascade**. The vtable-corruption itself is upstream; this fn is the symptom site for a fatal AV. |
| Patch action | At entry: validate `[ECX]` (vtable ptr) is in `0x00800000..0x00900000` (.rdata range). If invalid: zero-fill 3 float* output params, RET 0xC (or 0x10 for CV4). Otherwise execute original 6 prologue bytes + JMP back. |
| Bug also bites stock client? | Indirectly — the cascade requires VEH recovery, which the proxy installs. Stock client without VEH would have crashed at the original upstream fault. |
| OpenBC applicability | **DOES NOT APPLY (architecture).** OpenBC parses StateUpdate via `bc_parse_state_update()` (game_events.c:283) using flat byte cursors over a `bc_buffer_t`. No vtable dispatch. CompressedVector fields, if present, would be parsed by inline byte reads. No cascading vtable-call failure mode. |
| OpenBC action | None required. The defensive lesson: when reading variable-width payloads, validate input length against declared dirty_flags before parsing each field. OpenBC already does this in `bc_parse_state_update`. |
| Test guard | Fuzz inbound 0x1C with truncated payloads at every flag-boundary; assert parser rejects (returns false) without writing to outputs. |

### #5 — CWD fix (SetCurrentDirectoryA in DllMain)

| Field | Value |
|---|---|
| Patch site | `core_runtime_and_exports.inc.c:632` — single line `SetCurrentDirectoryA(g_szBasePath)` in DllMain DLL_PROCESS_ATTACH. |
| Stock function | `Python_ImportModule` at 0x006F7D90; called by FUN_0043ad70 (UtopiaApp_PythonInit) with `"Autoexec"` string. |
| Completeness score | n/a (this is a proxy-side workaround, not a stock-binary patch) |
| Confidence | high (decompile shows `FUN_006f7d90("Autoexec",0)` ⇒ FUN_006f8ab0 ⇒ Python `import Autoexec` ⇒ relative `Scripts/...` paths) |
| Bug condition | The engine resolves Python module paths and NIF data files via **relative paths** rooted at the process CWD. When launched from WSL2/`cmd.exe` via `start /B`, CWD is the launcher's directory, not the game install. Python `import Autoexec` fails → engine sequence fails. |
| Trigger in headless | Run `make run-server` from WSL — process inherits WSL's `/mnt/c/...` translated CWD; engine looks for `Scripts/Autoexec.py` relative to that. |
| Bug class | **Stock-binary assumption violated by modern launch context.** Original devs launched via shortcut/`.exe` double-click which sets CWD to install dir. |
| Patch action | `SetCurrentDirectoryA(g_szBasePath)` — sets CWD to the directory containing the proxy `ddraw.dll` (= game install dir). |
| Bug also bites stock client? | Yes if launched from non-game-dir. Stock workaround: a shortcut with explicit "Start in" path. |
| OpenBC applicability | **DOES NOT APPLY (architecture).** OpenBC server reads files via explicit `bc_read_file(path)` calls with absolute paths derived from `server.toml` config. Browse `src/server/main.c` — there's no CWD-relative resource loading. |
| OpenBC action | Keep config-driven absolute paths. Document that asset directory must be specified in `server.toml`, not inferred from CWD. |
| Test guard | Launch with deliberately wrong CWD; server should still start. |

### #6 — NewPlayerInGame handshake (GameLoopTimerProc trigger)

| Field | Value |
|---|---|
| Patch site | `game_loop_and_bootstrap.inc.c:660` — when hook #15 (FUN_006a1e70) `callCount` increments, fire deferred Python `_m1.InitNetwork(peerID)`. |
| Stock function | `NewPlayerInGameHandler` (FUN_006A1E70), `__thiscall`, called from `MpgameHandleMessage` at 0x0069F30D (opcode 0x2A dispatch). |
| Completeness score | 0.0 / 104 fixable (high complexity, no plate) |
| Confidence | high (decompile shows internal `FUN_006f8ab0(...,"InitNetwork",...,uVar14)` Python C-API call → returns -1 → FUN_0074af10 swallows error) |
| Stock decompile (relevant) | Inside handler: posts event 0x008000F1 (NEW_PLAYER), then calls `FUN_006f8ab0(*(*(*(this+0x70)+0x3c)+0x14), s_InitNetwork_0095a354, ...)`. `FUN_006f8ab0` is `Python_CallMethod(module, method, fmt, args...)` returning -1 on error. |
| Bug condition | The Python `Mission1.InitNetwork(playerID)` call fails inside `NewPlayerInGameHandler` because it runs from TIMERPROC context — `PyRun_SimpleString` nesting / GIL state is fragile under our renderer-proxy callback chain. Native `FUN_006f8ab0` returns -1; `FUN_0074af10` (Python error clear stub) eats the error. **InitNetwork never runs server-side**, so `MISSION_INIT_MESSAGE` is never sent to the joining client. |
| Trigger in headless | Every new player join. |
| Bug class | **Dedi-specific Python-context bug** stemming from our proxy invoking GameLoop via SetTimer instead of via the engine's WinMain message loop. |
| Patch action | Polling block in GameLoopTimerProc detects when hook #15 (TG_FunctionTracer wrapper around FUN_006a1e70) increments its `callCount`. Then constructs `import sys; if sys.modules.has_key('Multiplayer.Episode.Mission1.Mission1'): _m1=...; _m1.InitNetwork(%u)\n` and fires via `RunPyCode`. RunPyCode uses `PyRun_SimpleString` from a different context that works. |
| Bug also bites stock client? | No — stock dedi did not exist as a productized configuration; the original SP/MP flow ran InitNetwork synchronously inside the engine's main loop. |
| OpenBC applicability | **DOES NOT APPLY (architecture).** OpenBC server's "new player" path is `bc_peers_add()` (`src/server/server_handshake.c:462`) returning slot index synchronously. The Mission1.InitNetwork() equivalent — sending mission-init data to the new player — is replaced by `bc_build_score_init()` for each existing player batch (`game_builders.c:334`). No Python interpreter, no deferred Python callback, no race condition. |
| OpenBC action | Continue routing all per-player initialization through synchronous handshake state machine in server_handshake.c. |
| Test guard | Sustained spam-reconnect from a test client; each connect must produce a SCORE_INIT batch. |

### #7 — Scoring dict registration (post-NewPlayer Python registration)

| Field | Value |
|---|---|
| Patch site | Same GameLoopTimerProc block as #6; also see DSNetHandlers.py `DSNetHandlers.py:382` (SCORE_MESSAGE send during join). |
| Stock function | No single C function — scoring is **Python state** in `Multiplayer.Episode.Mission1.Mission1` module (kills/deaths/scores dicts keyed by playerID). |
| Completeness score | n/a (Python-layer) |
| Confidence | medium (read DSNetHandlers comments + match against stock trace SCORE_MESSAGE sequence) |
| Bug condition | When `NewPlayerInGameHandler` C-side processes 0x2A, it expects the Python mission scripting layer to immediately register the new player in `m_dKills` / `m_dDeaths` / `m_dScores` dicts. The Python-side registration is normally chained from `InitNetwork()` which our patch #6 also defers. The first inbound damage/kill event hits an unregistered player ID → `KeyError` → Python exception → handler aborts → no SCORE_CHANGE message → known issue `scoring dict fix rc=-1` in CLAUDE.md. |
| Trigger in headless | Joining player takes damage / scores a kill before MISSION_INIT_MESSAGE round-trip completes. |
| Bug class | **Dedi-specific Python state race**. |
| Patch action | DSNetHandlers.NewPlayerInGameHandler path (Custom layer) preempts by initializing all three dicts to zero for the new playerID and broadcasting SCORE_MESSAGE to all peers before InitNetwork. |
| Bug also bites stock client? | No — same timing as #6. |
| OpenBC applicability | **DOES NOT APPLY (architecture).** OpenBC stores per-peer score in `bc_peer_t.score/kills/deaths` (zero-initialized on `bc_peers_add`) and broadcasts via `bc_build_score_init()` to the joining peer (`src/server/server_handshake.c:486 clear_slot_score_state(slot); g_peers.peers[slot].kills=0;` etc.). No dict-key lookup, no KeyError possible, no Python in the loop. |
| OpenBC action | None required. Stock has separate per-PLAYER (network ID) and per-SLOT keying that can drift; OpenBC's single-source slot-keyed storage avoids it. |
| Test guard | Send DAMAGE/KILL event before SCORE_INIT broadcast completes; verify server tracks correctly and emits SCORE update. |

### #8 — Renderer pipeline proxy (D3D7/DDraw7/Surface7 COM)

| Field | Value |
|---|---|
| Patch site | `src/proxy/ddraw_ddraw7.c`, `ddraw_d3d7.c`, `ddraw_surface7.c` — full COM interface proxies. |
| Stock function | `UtopiaApp_SetupRenderer` at 0x00438290 — calls `FUN_007c09c0(fullscreen_flag, width, height, ...)` to construct `NiDX7Renderer`. Then asks renderer for caps via vtable+0x34 and matrix setup via vtable+0x60. Crash chain originally hit on `(**(piVar11+0x28))(1)` (Release) during renderer-not-found error path. |
| Completeness score | 0.0 / 133 fixable (large worker, no plate) |
| Confidence | high (decompile shows FUN_00438290 reads fullscreen flag from `EBP+0x2c`, picks fullscreen vs windowed FUN_007c09c0 variant, then refs renderer state via piVar11) |
| Bug condition | The real `NiDX7Renderer` constructor inside FUN_007c09c0 calls into DirectDraw7/Direct3D7 COM objects. On modern Windows, fullscreen 640x480x16bpp mode is not supported ⇒ FUN_007c09c0 returns NULL ⇒ `*(int*)(param_1+0xc) == 0` branch ⇒ error popup `s_D3D_Render_Creation_Error_Error_s_008d993c` ⇒ FUN_0086e440 message box ⇒ process exits. |
| Trigger in headless | Always at boot in headless mode without our proxy. |
| Bug class | **Stock-binary 2002 fullscreen mode incompatible with 2026 Win11 D3D7**, AND **headless can't render at all anyway**. |
| Patch action | Proxy provides synthetic `IDirectDraw7` / `IDirect3D7` / `IDirectDrawSurface7` COM objects with valid vtables and stub methods. Renderer ctor succeeds with them; downstream renderer state (frustum, matrices, render-target arrays) initializes cleanly; the no-op render loop calls render methods that do nothing but return SUCCESS. PatchForceWindowed (0x004384E7 JZ→JMP) also forces windowed code path. |
| Bug also bites stock client? | Stock client on Win11 hits the fullscreen-mode-unsupported error unless run with `PatchForceWindowed` equivalent (compatibility mode + low-res). |
| OpenBC applicability | **DOES NOT APPLY (architecture).** OpenBC server has no rendering subsystem (`bc_server_main()` is a pure UDP loop). OpenBC client (`src/client/client_backend_sdl3_bgfx.c`) uses SDL3 + bgfx, not DirectDraw7. |
| OpenBC action | None required. The server is headless by design. The client backend has a noop variant for unit tests. |
| Test guard | n/a |

### #9 — DeferredInitObject (Python-driven ship creation)

| Field | Value |
|---|---|
| Patch site | `game_loop_and_bootstrap.inc.c:741` — polls per-peer ship via `Custom.DedicatedServer.DeferredInitObject(peerID)` (Python). |
| Stock function | Engine's `TG_CallPythonFunction` invokes `SpeciesToShip.InitObject(self, iType)` during ship `ReadStream` deserialization in opcode 0x02/0x03 (ObjCreate) handler at FUN_0069F620. The Python `InitObject` is what loads NIF model, instantiates per-subsystem C++ objects, populates `ship+0x284` list. |
| Completeness score | n/a (Python-layer + headless workaround) |
| Confidence | high (DSNetHandlers.py:456 monkey-patches InitObject with tracing; verified call returns success on second invocation after DeferredInitObject) |
| Bug condition | The native `SpeciesToShip.InitObject` call fails silently when fired from inside the engine's `ReadStream` codepath in headless mode (Python module-loading state or ship's `self` isn't fully initialized). Without InitObject, ship has no NIF model, no subsystems (ship+0x284=NULL), no collision geometry, and no DmgTarget at +0x140. All damage paths silently drop. |
| Trigger in headless | Every player ship spawn. |
| Bug class | **Dedi-specific Python timing bug** within ObjCreate dispatch. |
| Patch action | After InitNetwork fires for a peer (per patch #6), poll every ~1s via `RunPyCode("sys.modules['Custom.DedicatedServer'].DeferredInitObject(%u)")`. DeferredInitObject is idempotent — checks ship type changed since last call, returns 0 if not. Sets up NIF, populates subsystem list, fixes up `ship+0x140 = ship+0x18` (DmgTarget). |
| Bug also bites stock client? | No — stock clients run InitObject synchronously during ObjCreate. |
| OpenBC applicability | **DOES NOT APPLY (architecture).** OpenBC has no NIF assets, no ship+0x18 NiNode, no ship+0x140 DmgTarget. Ship state is the flat `bc_ship_state_t` struct attached to `bc_peer_t`. Class data (subsystems, hardpoints) comes from `module_loader.c` JSON/config files synchronously at server boot. Per-peer ship state is zero-initialized on `bc_peers_add()`. |
| OpenBC action | Continue synchronous class-data load + zero-init peer ship-state model. Document the pattern: server's "ship spawn" = zero-init + reference to immutable class def, no per-ship dynamic allocation. |
| Test guard | Boot server with N peer slots; immediately probe each peer's ship_state to ensure it's valid. |

### #10 — InitNetwork peer-array detection

| Field | Value |
|---|---|
| Patch site | `game_loop_and_bootstrap.inc.c:611-689` — polls `wsnPtr+0x2C` (peer array) / `+0x30` (peer count) every tick; reads `peer+0x18` (peer ID). |
| Stock function | Field-offset evidence: `TGWinsockNetwork_SendOutgoingPackets` at 0x006B55B0 iterates `param_1[0xb]` (= WSN+0x2C peer array) of length `param_1[0xc]` (= WSN+0x30 count). Per peer accesses `iVar2 + 0x18` (peer ID), `iVar2+0x1C` (target addr), `iVar2+0x48/+0x54` (stats). |
| Completeness score | n/a (proxy-side polling logic) |
| Confidence | high (offsets cross-referenced from SendOutgoingPackets binary; matches docs/networking field map) |
| Bug condition | Original detection: poll `peer+0xBC` (a "bc" sticky bit set by some part of the checksum pipeline). Took 200+ ticks (~6.6s at 33ms) because the bit fires after checksum round 5 completes. Result: clients reached gameplay before our InitNetwork was triggered. |
| Trigger in headless | Every join. |
| Bug class | **Proxy-side detection-heuristic improvement** (not a stock bug — stock uses synchronous flow). |
| Patch action | New detection: enumerate `wsnPtr[+0x2C]` array; for each non-NULL peer ptr, read `peer[+0x18]` as peer ID. New ID appearing = new peer connected. Fires at tick ~174 (~5.7s, matches stock connect timing). Skips host (ID=1). |
| Bug also bites stock client? | No — proxy-side concern only. |
| OpenBC applicability | **DOES NOT APPLY (architecture).** OpenBC's peer manager is `bc_peers_add()` in `server_handshake.c:462` returning the slot index synchronously. No polling, no detection heuristic. Each new peer enters PEER_CHECKSUMMING state immediately and the dispatch loop drives them through PEER_PLAYING. |
| OpenBC action | Continue state-machine-driven peer lifecycle. Document the peer states (`PEER_CHECKSUMMING` → `PEER_PLAYING` → `PEER_DISCONNECTED`). |
| Test guard | Send rapid Connect messages from multiple clients; verify each transitions through states without dropping. |

## Summary table (10 × applies/partial/skip)

| # | Patch | Bug class | OpenBC verdict | OpenBC action |
|---|-------|-----------|---------------|----------------|
| 1 | TGL FindEntry NULL | Stock-client edge | **SKIP** (no TGL) | none |
| 2 | StateUpdate flag-clear | Dedi-race | **SKIP** (synchronous spawn) | none |
| 3 | Subsystem hash kick | Dedi anti-cheat FP | **SKIP** (no hash, server-authoritative) | none |
| 4 | CV3/CV4 vtable guard | Stock latent + VEH cascade | **SKIP** (no vtable, flat parse) | length-validate dirty_flags payload |
| 5 | CWD SetCurrentDirectory | Stock + launcher | **SKIP** (config absolute paths) | already done |
| 6 | NewPlayerInGame InitNetwork | Dedi Python context | **SKIP** (synchronous handshake) | already done |
| 7 | Scoring dict registration | Dedi Python state race | **SKIP** (flat peer struct fields) | already done |
| 8 | Renderer COM proxy | Stock + Win11 D3D7 | **SKIP** (headless by design) | n/a |
| 9 | DeferredInitObject | Dedi Python timing | **SKIP** (class-data + zero-init) | already done |
| 10 | Peer-array detection | Proxy heuristic | **SKIP** (state-machine peers) | already done |

**All 10 patches are SKIP for OpenBC.** OpenBC's architectural choices (flat C structs over NetImmerse vtables; synchronous state-machine peer lifecycle over polled Python callbacks; class-data over per-instance allocation; no embedded Python interpreter; built-in headless design) **insulate it from every single bug surface** these patches address.

The patches are 100% diagnostic of stbc.exe's specific 2002-NetImmerse-Python-1.5-DirectDraw7 architecture. OpenBC's clean-room reimplementation does not inherit any of them.

## Cross-references to v5 docs

| Patch | Related v5-validated docs |
|---|---|
| #1 TGL | docs/engine/ui-class-hierarchy.md (UI registries that use TGL); docs/troubleshooting.md |
| #2 NULL list flags | docs/protocol/stateupdate.md, docs/protocol/stateupdate-subsystem-wire-format.md (sub/wpn flag semantics) |
| #3 Subsys hash | docs/protocol/subsystem-integrity-hash.md (dead-in-MP analysis); subsystem-integrity-hash-validation-20260528.md memo |
| #4 CompVec | docs/protocol/stream-primitives.md (CV3 + CV4 wire format); docs/analysis/veh-cascade-triage.md (cascade history) |
| #5 CWD | docs/architecture/dedicated-server.md (bootstrap) |
| #6 NewPlayer | docs/networking/multiplayer-flow.md (Phase 5 join handshake); docs/protocol/game-opcodes.md (0x2A NewPlayerInGame) |
| #7 Scoring | docs/protocol/python-messages.md (0x37 SCORE_MESSAGE); docs/gamemode-system.md |
| #8 Renderer | docs/architecture/architecture-overview.md (COM proxy chain); docs/architecture/dedicated-server.md |
| #9 DeferredInitObject | docs/architecture/dedicated-server.md; docs/analysis/subsystem-trace-analysis.md (ship subsystem creation pipeline); docs/gameplay/objcreate-unknown-species-analysis.md |
| #10 Peer-array | docs/networking/network-protocol.md (WSN+0x2C peer array offsets); docs/networking/multiplayer-flow.md |

## Notes / open questions

- **OQ-1:** Patch #3 stock-bug claim — the wire-format memo says hash bit=`!isHost` in sender at 005B1D96. If we ever see a packet trace with a non-host **client** sending hash bit=1 (client→server StateUpdate), then **the patch is also defending against a real anti-cheat path**, not just the dedi-null-list case. Need a stock-MP trace (client→host, host-MP-game) to confirm or refute. Memo `stateupdate-validation-20260528` says "C→S always 0x80 (WPN)" with no 0x01 flag carry — so the hash check is essentially never invoked. Status: **dead-in-MP** confirmed; patch's anti-FP path is purely for the dedi-host-receives-from-client case.

- **OQ-2:** The patch file also contains 7 additional patches not in CLAUDE.md's "10 Key Fixes" list (PatchRenderTick, PatchInitAbort, PatchForceWindowed, PatchSkipDeviceLost, PatchSkipDisplayModeSearch, PatchRendererMethods, PatchDeviceCapsRawCopy, PatchHeadlessCrashSites, PatchNullThunk_00419960, PatchStreamReadNullBuffer, PatchCollisionNullNodeCall_005AFE2C, PatchCollisionNullNodeCallGuard_005AFE44, PatchSendStateUpdatesPeerValidation, PatchRemovePeerAddress, PatchDebugConsoleToFile). Many are subsidiary to the "10" — for example PatchForceWindowed is a sub-fix supporting #8. Future investigation could expand the inventory.

- **OQ-3:** `FUN_006a1e70` Python `InitNetwork` call failure root cause — confirmed it returns -1, but **why** the call fails in TIMERPROC context is not fully understood. Hypothesis: thread-state stack pointer mismatch in `_PyThreadState_Current` because the SetTimer thread is the same OS thread as the original window-procedure caller, but `PyRun_SimpleString` context is per-thread per-frame and our timer fires before the frame's previous Python frame is unwound. Worth a future python-152-reviewer investigation.

## Pattern memory: stock-headless-shortcuts

A consistent pattern across stock-bug patches: **Totally Games coded for the invariant case** ("manager always exists", "ship always has subsystems", "InitObject always runs synchronously during ObjCreate") and didn't NULL-check the broken invariants because in stock SP/MP they couldn't be broken. Headless dedi is the breaking context. Whenever a future investigation surfaces another bug like "headless crash at vtable-X", first check: **is this a stock-client invariant we violated?** before assuming it's a fresh bug.
