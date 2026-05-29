---
name: tick-rate-inventory-validation-20260528
description: Comprehensive v5 tick-rate inventory for stbc.exe — every Update/tick driver, frequency, gating constant, and network impact, recovered from binary
metadata:
  type: project
---

# Tick-Rate Inventory — stbc.exe (v5)

## Scope

OpenBC compare-phase reference for matching stock-BC cadences across every subsystem. Pre-v5 `docs/architecture/main-loop-timing.md` had GameLoopTimerProc=33ms as the canonical tick — that is the **proxy DLL artifact**, NOT the natural stbc.exe rate. This memo recovers the actual stbc.exe tick architecture.

---

## TL;DR — The Real Main Tick Architecture

In **stock stbc.exe**, there is NO `WM_TIMER`/`SetTimer` for the main game tick. The main tick is the **PeekMessage spin loop** at the WinMain message pump. It runs at the maximum rate the host CPU allows, throttled only when GameSpy is active.

Proxy's `GameLoopTimerProc(33ms)` is a dedicated-server hook that calls `TopWindow__Update` (0x0043b4f0) directly because the proxy minimizes the window — once minimized, `GetMessage`-style pumping changes behavior and the natural tick path can stall. The proxy installs WM_TIMER as a fallback driver.

**Stock client tick rate** ≈ display refresh rate (~60-200 Hz uncapped, capped at 60Hz frame budget per `app[0x1d] = 1/60 ≈ 0.01667s`).

**Dedicated server (proxy)** ≈ **30 Hz** (33ms SetTimer + ~5ms work) → `TopWindow__Update` per tick.

---

## Main Loop Architecture (stbc.exe, NO proxy)

### Call Chain

```
WinMain (FUN_0086eff0)
  └── Application_RunMessageLoop (FUN_007ba5a0)
       └── do { vtable[0x78]() } while !=0
            └── Application_RunMessageLoopIteration (0x007b8790)
                 ├── PeekMessageA → if (msg) { TranslateMessage; DispatchMessageA }
                 └── if (!msg) vtable[0x80]()   ← per-frame tick
                      └── UtopiaApp_PerFrameTick (0x00438e20)
                           ├── 49ms timeGetTime throttle (when GameSpy registered + idle)
                           └── FUN_006cdd20  ← Application::Tick
                                 ├── vtable[0x94]()                  → UtopiaApp_FrameWork (0x00438e60)
                                 │     ├── FUN_006cdb90              ← pause-state machine
                                 │     └── FUN_0070fdb0 / FUN_0070fdf0 ← render passes
                                 ├── app[0x1d] + app[0x1e] <= app[0x15]  ← FRAME RATE CAP (1/60 = 60Hz)
                                 ├── vtable[0xA0]() if app[0x23]==1  ← state-1 callback
                                 ├── vtable[0xA4]() if app[0x23]==3  ← state-3 callback
                                 ├── FUN_006e6420()                  ← (empty stub)
                                 ├── FUN_006e6430()                  ← DirectInput polling (kbd/mouse/joy)
                                 └── app[0x19]++                     ← frame counter
                           └── FUN_0071e420 → FUN_0071e3b0(&LAB_0071e540)
```

### Where TopWindow__Update Actually Runs

Inside the per-frame chain via `vtable[0x94]()` → eventually scene work — TopWindow__Update at **0x0043b4f0** (UtopiaApp vtable+0xF4 slot in vtable at 0x00889a98). This runs `TGTimerManager::Update`, `TGEventManager::ProcessQueue`, `Ship__AITickScheduler`, scene-priority dispatch, render.

Per the proxy notes (`src/proxy/ddraw_main/game_loop_and_bootstrap.inc.c:1410`), the proxy bypasses the natural chain and calls TopWindow__Update directly at 33ms intervals via WM_TIMER 0xBCBC.

### Critical Constants — Application object (vtable PTR_FUN_0088b1b8, instance at 0x009a09d0)

| Address | Bytes | Float | Meaning |
|---------|-------|-------|---------|
| app[0x1d] (instance) | seeded 0x3C888889 in ctor (0x00437fb0:0x00437fea) | 1.0f/60.0f = **0.01666667s** | Min frame interval — **60 Hz frame cap** |
| app[0x27] (instance) | seeded 0x3E800000 | 0.25f = **250ms** | (unknown timer field, possibly idle-pause threshold) |
| 0x0097F950 | runtime DWORD | timeGetTime() last-tick | **49ms throttle anchor** (UtopiaApp_PerFrameTick) |
| 0x31 immediate | hard-coded in PerFrameTick | 49 (ms) | **49ms = ~20Hz minimum throttle when GameSpy idle** |
| _DAT_00893f20 | 0x3F50624DD2F1A9FC (double) | 0.001 | ms→s conversion in TGTimer::GetElapsedSeconds (FUN_0071acc0) |

### Throttle Logic (UtopiaApp_PerFrameTick at 0x00438e20)

```c
// Tick fires if ANY of:
//   1. GameSpy not registered (qr_t @ 0x0097fa7c == 0)
//   2. GameSpy active flag set (qr_t[0xec] != 0)
//   3. > 49ms elapsed since last tick (timeGetTime() - 0x0097F950 > 0x31)
if (qr_t == 0 || qr_t[0xec] != 0 || (timeGetTime() - lastTick) > 49) {
    lastTick = timeGetTime();
    FUN_006cdd20();   // Application::Tick
    FUN_0071e420();   // TGEventManager dispatch
}
```

Default: unthrottled (PeekMessage spin). When GameSpy registered + idle: 49ms throttle = **~20Hz minimum**.

---

## TopWindow::Update Tick Chain (0x0043b4f0)

The "real" per-tick work. Called from proxy (33ms WM_TIMER) or from natural chain.

```c
void TopWindow__Update(int *param_1) {
    FUN_0071a9e0();                                                     // ?
    TGTimerManager__Update(*(Clock+0x90));                              // gameTime — fires scheduled timers
    TGTimerManager__Update(*(Clock+0x54));                              // frameTime — fires scheduled timers
    TGEventManager__ProcessQueue();                                     // drain event queue (no rate gate)
    Ship__AITickScheduler();                                            // 0x004721b0 — AI tick batcher
    FUN_0046f420();                                                     // rolling-avg scene dispatch (4 priority groups)
    FUN_00443ac0();                                                     // TopWindow scene work
    FUN_004447f0();                                                     // ?
    FUN_00444840();                                                     // ?
    FUN_0043b790();                                                     // TopWindow tail
    // ... selective render (FUN_004433e0)
}
```

### Per-frame work via priority groups (FUN_0046f420 + FUN_0046f610)

NetImmerse-style adaptive-deadline dispatcher:

1. **FUN_0046f420** computes adaptive time budget per group:
   - Maintains 16-sample rolling buffer of frame times at `DAT_00981560` (circular index `DAT_009815E0 & 0xF`)
   - Excludes min + max from average: `mean = (sum - min - max) / 14`
   - Constant `_DAT_0088bb28` = 0x3FB2492492492492 (double) = **1/14**
   - Min budget = 0.01s (clamped from `_DAT_0088bb20` = 0x00999... double = 0.01)
2. **FUN_0046f610** iterates list at `DAT_00981494[group*6]` (group 0..3, 4 groups), calls each entry's `vtable[0](deadline)` until budget exhausted.
3. Group priority: round-robin via bit-rotated index `DAT_009815E4`. Group 1 runs first, then if budget remains, groups 2/3/4 in rotation.

**Implication**: Ships and other Updateables register into a priority group at construction. Their Update is called **at most once per TopWindow tick**, but only if the group's time budget hasn't been exhausted by higher-priority objects.

---

## Per-Subsystem Tick Rates — Inventory Table

### Network / Transport

| Subsystem | Address | Driving Function | Rate | Constant Source | Wire Impact |
|-----------|---------|------------------|------|------------------|-------------|
| **TGNetwork::Update** | FUN_006b4560 | TGWinsockNetwork_Update (FUN_006b2620, vtable slot 2) | Per main tick (~30 Hz dedi, ~60+ Hz stock client) | NO internal gate | Drives all packet I/O |
| **SendOutgoingPackets** | TGWinsockNetwork_SendOutgoingPackets (0x006b55b0) | Called from TGNetwork::Update | Per tick | NO gate | All outbound packets |
| **ProcessIncomingPackets** | TGWinsockNetwork_ProcessIncomingPackets (0x006b5c90) | Called from TGNetwork::Update | Per tick | NO gate | All inbound packets |
| **TGWinsockNetwork_HandleReliableReceived** | 0x006b6200 | Per-message in ProcessIncomingPackets | Per packet | event-driven | Dispatches handlers |
| **GameSpy heartbeat** | qr_t+0xE4 logic | qr_t::Heartbeat | **30s** per heartbeat (max 10) | hardcoded constant per gamespy-discovery memo | LAN broadcast presence |
| **TGNetwork connect keepalive** | FUN_006b4560 internal | `_DAT_0088bd58 < (currentTime - WSN+0xc0)` | **5s interval** | _DAT_0088bd58 = 5.0f @ 0x0088bd58 | Connect ping to bring peers up |
| **TGNetwork connect retry** | FUN_006b4560 boot-phase | `WSN+0xb8 < (currentTime - WSN+0xbc)` per peer | **45s timeout** (boot-only path) | WSN+0xb8 ctor-set 0x42340000 = 45.0f | Boot phase connect retry |
| **TGNetwork session timeout** | inferred from WSN+0xb4 | per-peer last-recv | **360s = 6 min** | WSN+0xb4 ctor-set 0x43b40000 = 360.0f | Hard disconnect after 6m silence |

### StateUpdate (opcode 0x1C) — per-ship per-peer

| Subsystem | Address | Driver | Rate | Constant | Wire |
|-----------|---------|--------|------|----------|------|
| **MultiplayerGame::SendStateUpdates** | FUN_0069ee50 | called via vtable slot 0x328 (Mpgame Tick) | Per main tick | NO gate (sends opcode 0x1C every tick per ship per peer) | StateUpdate (opcode 0x1C) |
| **Ship__WriteStateUpdate** | 0x005B17F0 | called per-peer per-tick from MultiplayerGame::SendStateUpdates | Per main tick per peer | NO rate gate; field-level "force resend" gate: `_DAT_00888860 < (gameTime - tracker+0x4)` → forceFlag | StateUpdate (opcode 0x1C) per ship per peer |
| **Force-resend threshold** | _DAT_00888860 | sender-side absolute-resend gate | **1.0s** | _DAT_00888860 = 0x3F800000 = 1.0f @ 0x00888860 | If 1s elapsed since last full resend → set bForceResendPos flag |
| **Stateupdate caller plate** | FUN_0069edc0 | also fires keepalive when no peer activity in 5s (_DAT_0088bd58) | Per main tick | _DAT_0088bd58 = 5.0f | Triggers FUN_006b4930 disconnect-check + UI bad-connection |

**Net effect**: Server emits a StateUpdate packet for every active ship to every active peer **every main tick** — so on a dedicated server with 33ms tick, that's ~30 Hz per ship per peer. With 8 players × 2 trackers each = 16 ships → up to ~480 packets/s base rate just from StateUpdate. The dirty-flag system suppresses payload but the empty header still goes out unless all 8 dirty bits are clear.

### AI System

| Subsystem | Address | Driver | Rate | Constant | Wire |
|-----------|---------|--------|------|----------|------|
| **Ship__AITickScheduler** | 0x004721b0 | called from TopWindow__Update | Per main tick | Internal: `iVar8 = floor(currentTime - ship+0x20)` clamped to [1, 4] cycles per call | Posts events 0x800017 (BUILDER_DONE) etc. |
| **Ship__ProcessAITick** | 0x004722d0 | called once per scheduled cycle | Per cycle | `_DAT_0088bb20` = 2.0f = AI lock-time bonus | Posts handler events |
| **AI 6-tick budget** | FUN_004722d0 inner | per-cycle time check | After iVar9>6 calls, checks FUN_0071acc0 vs deadline → break | hard-coded threshold 6 | (no direct wire) |

**Implication**: AI runs at the main tick rate but each ship can have its AI evaluated up to ~4 times per tick if the AI lock time has elapsed. With proxy 33ms tick: ~30 Hz max AI evaluation per ship.

### Ship Subsystem Updates

| Subsystem | Address | Driver | Rate | Constant | Wire |
|-----------|---------|--------|------|----------|------|
| **WeaponSystem::Update** | FUN_005847d0 | vtable slot 0x64 on WeaponSystem (one of Ship's subsystems) | Per main tick | Internal child-throttle | indirectly drives StateUpdate flag 0x80 |
| **WeaponSystem child Update** | each weapon subsystem | called from WeaponSystem::Update | **3 Hz per child** | `_DAT_00892fc0` = 0x3EA8F5C3 = **0.33f** @ 0x00892fc0 | Drives phaser recharge / torpedo reload |
| **PhaserBank::UpdateCharge** | FUN_00572b80 | called from WeaponSystem child Update | Per child tick (3 Hz) | Power-level multipliers @ 0x0089317c: 0=0.35f, 1=1.0f, 2=1.0f, 3=0.5f | Charge level transmitted in StateUpdate flag 0x80 |
| **PoweredSubsystem::Update** | PoweredSubsystem_Update (FUN_00562470) | vtable slot 0x78 on PoweredSubsystem | Per main tick | NO direct gate (always tick) | Drives power state in StateUpdate |
| **PoweredMaster::Update** | PoweredMaster_Update (FUN_00563780) | vtable slot 0x78 on PoweredMaster | **1 Hz** (strict) | `_DAT_00892e20` = 0x3F800000 = **1.0f** @ 0x00892e20; gates `currentTime - ship+0xc0 > 1.0s` | Drives battery state in StateUpdate |
| **RepairSubsystem::Update** | FUN_005652a0 | vtable slot (Ship.subsystems[].vtable.Update) | Per main tick | First calls PoweredSubsystem_Update; then iterates ship+0xAC repair list once | Posts events 0x800074 (REPAIRED), 0x800075 (TIME_TO_REPAIR) |
| **CloakingSubsystem::Update** | FUN_0055e500 | vtable slot 0x70 | Per main tick | `DAT_008e4e1c` = **5.0f** = engage/disengage duration; `_DAT_0088d4ec` = **0.8f** = failure threshold | Drives cloak state in StateUpdate flag 0x40 |
| **ShieldGenerator::BoostShield** | FUN_0056a420 | called from PoweredSubsystem_Update → vtable+0x78 | Per main tick | `_DAT_0088bacc` = 0x3E2AAAAB = **0.166667f** = shield power fraction | Charges shields per power-budget |

**Subsystem Update gate**: `DAT_0097fa89 != 0 AND (DAT_0097fa89 != 0x01 OR DAT_0097fa8a != 0)` — only fires Update body when **GameLive == 1** AND IsHost == 1 (per shield-system + ship gate semantics). Server runs subsystem updates; clients run them too but most state is read-only.

### Sensor Subsystem

No SensorSubsystem-specific Update was found in this pass (no naming pattern match). Ship+0x2C8 is the SensorSubsystem slot per CLAUDE.md. Its Update is implicitly driven via the generic ShipSubsystem vtable slot, like all other subsystems. **Rate: per main tick** (no rate gate seen).

### Repair Tick

RepairSubsystem::Update (FUN_005652a0) runs PoweredSubsystem_Update first (so its power draw is computed) then iterates the per-ship repair list at ship+0xAC. Each repair member updates a "repair progress" float via the formula already documented in `gameplay-mid-repair-batch-validation`. Per-iteration: events posted for completion / progress.

| Constant | Address | Value | Meaning |
|----------|---------|-------|---------|
| `_DAT_00888b54` | 0x00888b54 | 0.0f | "is positive" epsilon |
| `_DAT_00888860` | 0x00888860 | 1.0f | unity constant; many gates |
| `_DAT_0088bd58` | 0x0088bd58 | 5.0f | keepalive interval + various 5s thresholds |
| `_DAT_00892e20` | 0x00892e20 | 1.0f | PoweredMaster 1Hz gate |
| `_DAT_0088bb20` (float) | 0x0088bb20 | 2.0f | AI tick lock-bonus |
| `_DAT_0088bb20` (double) | 0x0088bb20 | 0.01 | min frame-budget clamp |
| `_DAT_0088bb28` | 0x0088bb28 | 1/14 (double) | rolling-mean divisor |
| `_DAT_00892fc0` | 0x00892fc0 | 0.33f | WeaponSystem per-child tick interval |
| `DAT_008e4e1c` | 0x008e4e1c | 5.0f | Cloak engage/disengage seconds |
| `_DAT_0088d4ec` | 0x0088d4ec | 0.8f | Cloak failure power threshold |
| `_DAT_0088bacc` | 0x0088bacc | 0.166667f | Shield power fraction |
| App ctor `1/60` | seeded at 0x00437fea | 0.01667f | 60 Hz frame cap |
| App ctor `0.25` | seeded at 0x00437fea+0x?? | 0.25f | unknown app[0x27] |

### Event System

| Subsystem | Address | Driver | Rate | Wire Impact |
|-----------|---------|--------|------|-------------|
| **TGTimerManager::Update** | FUN_006dc490 (renamed) | TopWindow__Update | Per tick | drains queue: any timer whose `due_time <= currentTime` fires |
| **TGEventManager::ProcessQueue** | FUN_006da2c0 (renamed) | TopWindow__Update | Per tick | drains queue: dispatches all queued events |

Both run **at the TopWindow tick rate** (~30 Hz dedi proxy / ~60-200 Hz stock client). Neither has an internal rate gate — they drain fully each tick.

### Collision Detection Rate Limit

Per `gameplay-leaves-collision-batch` memo, the collision rate-limit gate at Ship-vtable+0x13C = **FUN_005a22a0** uses a 5-way conditional table on player count + (host/client) + friendly-fire:

| Cooldown | Float | Use Case |
|----------|-------|----------|
| 0.1f (10 Hz) | 0x3DCCCCCD | <2 players, generic |
| 0.125f (8 Hz) | 0x3E000000 | <5 players certain flag paths |
| 0.166667f (6 Hz) | 0x3E2B020C | 2-3 active players, host |
| 0.25f (4 Hz) | 0x3E800000 | 3+ active players, host |
| 0.5f (2 Hz) | 0x3F000000 | 3+ active players, dedicated server |

This is a "per-collision-pair" rate limit — limits CollisionEffect (opcode 0x15) emission. Stock-dedi observed ratio is 84 events / session under typical 3-player load = ~0.04 events/sec = 0.04 Hz effective collision rate. The gate determines max possible — not a fixed tick.

---

## Network Tick → Wire Format Mapping

| Tick | Wire Output | Frequency Source |
|------|-------------|------------------|
| Main tick | StateUpdate (0x1C) per ship per peer | All ships emit each tick; suppressed only if all dirty bits=0 (rare while in motion) |
| Main tick | StartFiring (0x07) on weapon-fire event | Event-driven; not rate-gated |
| Main tick | StateUpdate flag 0x20 (subsystems) | Per main tick when subsystem state changes |
| Main tick | StateUpdate flag 0x80 (weapons) | Per main tick on client-or-SP-host-view |
| 5s keepalive | (no opcode — internal connect ping) | TGNetwork::Update boot-phase only |
| 30s heartbeat | GameSpy heartbeat | GameSpy auto |
| Collision-rate gate | CollisionEffect (0x15) | Per-pair-cooldown gate (0.1s..0.5s) |
| 1Hz Power | StateUpdate flag 0x40 effects (cloak power-fail) | Power tick updates internal state, surfaces via StateUpdate next tick |

---

## Critical Cadences for Multiplayer State Replication

### Cadence Tree

```
WinMain spin loop (PeekMessage)        — ~60-200 Hz on client (uncapped)
└── 49ms throttle if GameSpy idle      — 20 Hz floor
    └── UtopiaApp_PerFrameTick          — same rate
         └── Application::Tick           — same rate
              └── TopWindow::Update      — same rate
                   ├── TGTimerManager::Update         — drains all scheduled timers each tick
                   ├── TGEventManager::ProcessQueue   — drains all queued events each tick
                   ├── Ship__AITickScheduler          — up to 4 AI evals/ship/tick
                   ├── Scene priority dispatcher      — adaptive deadline; min 10ms budget
                   │    └── per-Ship vtable[0](deadline)   — per-ship-per-tick
                   │         └── Ship subsystem chain
                   │              ├── PoweredMaster::Update    — 1 Hz strict
                   │              ├── PoweredSubsystem::Update — per tick
                   │              ├── WeaponSystem::Update     — per tick
                   │              │    └── child Update         — 3 Hz per child
                   │              ├── RepairSubsystem::Update  — per tick
                   │              └── CloakingSubsystem::Update — per tick
                   └── MultiplayerGame::SendStateUpdates       — per tick
                        └── Ship__WriteStateUpdate (per peer)   — per tick per ship per peer
                             └── 1s force-resend timer          — absolute pos resend
```

### Dedicated Server (proxy DLL — current OpenBC compare target)

- Tick driver: `SetTimer(hwnd, 0xBCBC, 33, GameLoopTimerProc)` — 33ms
- Effective rate: **~30 Hz** (33ms + work time)
- Each tick directly calls `TopWindow__Update` (0x0043b4f0) — bypasses the natural Application::Tick chain
- StateUpdate emission: ~30 packets/sec per (ship × peer) pair
- 8 players × 16 trackers each = up to 128 send sites per tick × 30 Hz = ~3,840 packets/s theoretical (heavily reduced by dirty-flag suppression)

### Stock client (no proxy)

- Tick driver: natural PeekMessage spin
- Effective rate: **60 Hz** (60-FPS frame cap via app[0x1d] gate) — but Update fires on every PeekMessage spin regardless of frame cap. The cap only affects rendering.
- Throttle when alt-tabbed / GameSpy idle: **20 Hz** (49ms timeGetTime)

---

## Rate-Limit Gates Discovered (Not in Per-Subsystem Table)

| Gate | Address | Condition | Constant |
|------|---------|-----------|----------|
| UtopiaApp_PerFrameTick throttle | 0x00438e20 | `timeGetTime() - lastTick > 49ms` when `qr_t!=NULL && qr_t[0xec]==0` | 49 (immediate) @ 0x00438e3c |
| FrameRate cap | FUN_006cdd20 | `app[0x1d] + app[0x1e] <= app[0x15]` (interval + last + cur) | app[0x1d] = 1/60.0 = 0x3C888889 @ ctor |
| Scene-priority budget | FUN_0046f420 | min budget 0.01s, mean of 14-sample window | _DAT_0088bb20 double = 0.01 |
| Network 49ms throttle effectiveness | UtopiaApp_PerFrameTick | only when GameSpy registered + idle | qr_t[0xec] (byte) |
| StateUpdate force-resend | Ship__WriteStateUpdate 0x005b17f0 | `gameTime - tracker+0x4 > 1.0s` | _DAT_00888860 = 1.0f |
| StateUpdate position-anchor force | Ship__WriteStateUpdate 0x005b17f0 | `gameTime - tracker+0x24 > 1.0s` | _DAT_00888860 = 1.0f |
| TGNetwork keepalive | FUN_006b4560 | `gameTime - WSN+0xc0 > 5.0s` | _DAT_0088bd58 = 5.0f |
| AI tick cycle limit | Ship__AITickScheduler 0x004721b0 | iVar8 = floor(delta), clamp [1,4] | hardcoded `1` floor |
| AI cycle deadline | Ship__ProcessAITick 0x004722d0 | after 6+ AI evals: check budget | hardcoded `6` |
| PoweredMaster 1Hz | PoweredMaster_Update 0x00563780 | `gameTime - ship+0xc0 > 1.0s` | _DAT_00892e20 = 1.0f |
| WeaponSystem child 3Hz | FUN_005847d0 inner loop | `child+0x12 (accumulator) > 0.33s` | _DAT_00892fc0 = 0.33f |
| Collision per-pair cooldown | FUN_005a22a0 (Ship vtable+0x13C) | 5-way conditional; 0.1f to 0.5f | per table above |
| Phaser discharge multiplier | FUN_00572b00 | per power-level | 0x35/1.0/1.0/0.5 @ 0x0089317c |
| Cloak engage time | FUN_0055e500 | 5.0s ramp | DAT_008e4e1c = 5.0f |
| Cloak failure threshold | FUN_0055e500 | power < 0.8f | _DAT_0088d4ec = 0.8f |
| GameSpy heartbeat | qr_t internal | every 30s, max 10 attempts | per gamespy-discovery memo |
| TGNetwork connect retry | FUN_006b4560 | every WSN+0xb8 = 45s | 0x42340000 @ WSN+0xb8 ctor |
| TGNetwork session timeout | inferred | 360s = 6min | 0x43b40000 @ WSN+0xb4 ctor |

---

## Discoveries This Pass

1. **The proxy's 33ms WM_TIMER ≠ stock tick.** Stock is unthrottled PeekMessage spin (~60-200 Hz). Proxy is 30Hz. **OpenBC must match proxy or stock depending on intended host model.**
2. **StateUpdate is unthrottled — fires every tick per ship per peer.** Dirty-flag suppression is the only throttle. With 30Hz proxy + 8 players, expect ~30 packets/s per (ship × peer).
3. **PoweredMaster is the only 1 Hz strict-gated tick.** Battery + reactor compute. Everything else runs at parent rate.
4. **WeaponSystem child Update is the only mid-rate subsystem gate (3 Hz).** Phaser/torpedo per-weapon work.
5. **NetImmerse scene priority dispatcher is adaptive.** 14-sample rolling mean computes per-group budget. Min 0.01s budget. **Implication: high-priority objects can starve low-priority ones if frame is loaded.** Could explain reported "AI freeze" issues under high load.
6. **TGTimerManager and TGEventManager drain fully each tick.** Not rate-gated. Any timer/event scheduled with `due <= currentTime` will fire next tick.
7. **The 49ms throttle (qr_t+0xec gate) is a "minimized window" optimization.** When GameSpy is registered but server is paused/idle, drop to 20Hz. Headless server scenario uses this if window minimized.
8. **AI runs up to 4 cycles per ship per tick.** Allows AI to "catch up" if delta is large. Soft-real-time guarantee.
9. **No `RunFrame` Python hook exposed.** SWIG exposes `UtopiaApp_SetFrameRate`, `UtopiaApp_GetApp`, `UtopiaModule_SetTimeRate`, `TopWindow_Update` but no per-frame Python callback. Python-driven ticks happen inside C++ Update bodies (e.g., PythonEvent dispatcher).
10. **Force-resend at 1s** for absolute position — prevents drift accumulation. Every 1s a full position resync is forced regardless of delta.

---

## Open Questions / Followups

1. **What is app[0x27] = 0.25f (set in ctor)?** Possibly auto-pause threshold or render-after-pause delay. Not load-bearing for tick.
2. **What writes DAT_0099c6bc (the "network time" anchor)?** All callers READ it; no FSTP/MOV writes found. Likely set as part of a larger struct via memcpy.
3. **Exact identity of FUN_006e6420 (empty stub) vs FUN_006e6430 (DirectInput poll).** The empty stub might be a deprecated/unused per-frame hook.
4. **Sensor subsystem Update — is there a dedicated rate or does it run at the generic ship-subsystem rate?** Not found in this pass.
5. **What's the actual stock client tick rate when not GPU-bound?** Need to instrument with proxy logging or live measurement.
6. **MultiplayerGame vtable boundaries.** The vtable at 0x0088b1b8 extends past slot 200 (0x328 offset). Need to validate where slot count actually ends. Many other "vtables" in this region may actually be data tables.

---

## Cross-Refs

- Anchors `cascade-verification-flags`: 0x0097fa88/89/8a flag semantics
- Anchors `stateupdate-validation`: Ship__WriteStateUpdate 0x005b17f0
- Anchors `gameplay-foundation-power-system`: PoweredMaster_Update + PoweredSubsystem_Update
- Anchors `gameplay-foundation-shield-system`: BoostShield 0x0056a420 + ShieldGenerator_Ctor
- Anchors `gameplay-mid-cloaking`: CloakingSubsystem at FUN_0055e500
- Anchors `gameplay-mid-repair-batch`: RepairSubsystem::Update FUN_005652a0
- Anchors `gameplay-foundation-ai-architecture`: Ship_AITickScheduler 0x004721b0
- Anchors `gameplay-leaves-collision-batch`: Collision rate limit gate
- Anchors `networking-foundation-network-protocol`: TGNetwork::Update chain
- Anchors `networking-leaf-ack-outbox-deadlock`: SendOutgoingPackets pass logic
- Anchors `networking-foundation-gamespy-discovery`: heartbeat 30s
- Anchors `networking-leaf-disconnect-flow`: 5.0s keepalive (`_DAT_0088bd58`)

## Confidence

- High-confidence (byte-confirmed): all listed addresses + all .rdata constants + UtopiaApp tick chain + Ship__AITickScheduler + PoweredMaster 1Hz gate + WeaponSystem 3Hz child gate + RepairSubsystem chain + MultiplayerGame::SendStateUpdates (FUN_0069ee50) + Ship__WriteStateUpdate gating
- Medium-confidence: scene priority dispatcher group identity (DAT_00981494 lists are zeroed in image; populated dynamically); per-group object counts unknown without runtime trace
- Open: stock client effective tick rate (depends on hardware); sensor-specific update; app[0x27] semantics; DAT_0099c6bc writer

## Functions Created/Renamed This Session

- 0x007b8790 = `Application_RunMessageLoopIteration` (created)
- 0x00438e20 = `UtopiaApp_PerFrameTick` (created)
- 0x00438e90 = `UtopiaApp_FrameWork` (created)
- 0x006cdf70 = `Application_OnPauseTransition` (created)
- 0x006b2620 = `TGWinsockNetwork_Update` (created)

Ghidra saved successfully.
