---
title: STBC Main Loop & Timing Architecture
type: reference + explanation
audience: RE engineers, OpenBC implementers
validated: 2026-05-28
methodology: FUNCTION_DOC_WORKFLOW_V5
binary:
  name: stbc.exe
  size: 6182400
  base: 0x00400000
status: verified
evidence:
  - claim: "Stock main loop driver is PeekMessage spin (no WM_TIMER); idle path dispatches via vtable[0x80]"
    address: 0x007b8790
    function: Application_RunMessageLoopIteration
    confidence: high
    note: "Created this pass. Body: PeekMessageA -> (msg ? Translate/Dispatch : vtable[0x80](this)). Loop driver is FUN_007ba5a0 calling vtable[0x78] in a do/while."
  - claim: "Per-frame tick entry point reached from idle path"
    address: 0x00438e20
    function: UtopiaApp_PerFrameTick
    confidence: high
    note: "Created this pass. Bound to UtopiaApp vtable slot 0x80 (0x00895b8c). Body runs the throttle gate then calls Application::Tick (FUN_006cdd20) and TGEventManager dispatch (FUN_0071e420)."
  - claim: "60 Hz frame cap seeded at app construction"
    address: 0x00437fea
    function: TGApp_Ctor
    confidence: high
    note: "MOV [ESI+0x74], 0x3C888889. 0x3C888889 = 1.0f/60.0f = 0.01666667s = app[0x1d] (m_fMinFramePeriod). Base NiApplication uses 1/100; TGApp overrides to 1/60."
  - claim: "49ms idle throttle fires only when GameSpy registered AND idle"
    address: 0x00438e3c
    function: UtopiaApp_PerFrameTick
    confidence: high
    note: "Gate: (qr_t==NULL) OR (qr_t[0xec]!=0) OR (timeGetTime() - DAT_0097F950 > 0x31). 0x31 = 49 decimal. Throttle anchor is DWORD at 0x0097F950 (last-tick timeGetTime). Effective floor ~20Hz when GameSpy idle."
  - claim: "Scene-priority dispatcher computes adaptive budget from 14-sample rolling mean"
    address: 0x0088bb28
    function: null
    confidence: high
    note: "DAT_0088bb28 = 0x3FB2492492492492 (double) = 1/14. Used as divisor in FUN_0046f420 against the 16-sample frame-time ring at DAT_00981560 (excludes min+max). Min budget clamp DAT_0088bb20 (double) = 0.01s."
  - claim: "TopWindow::Update body — drains TGTimer + TGEvent, ticks AI, runs scene-priority dispatcher"
    address: 0x0043b4f0
    function: TopWindow__Update
    confidence: high
    note: "Called from vtable[0x94] (UtopiaApp_FrameWork at 0x00438e60) in the natural chain; called directly via SetTimer 0xBCBC from proxy DLL. Sequence: TGTimerManager(gameTime), TGTimerManager(frameTime), TGEventManager, AITickScheduler, scene-priority dispatcher, scene work, render."
  - claim: "AI scheduler does up to 4 cycles/ship/tick, capped at 6 evaluations before yielding"
    address: 0x004721b0
    function: Ship__AITickScheduler
    confidence: high
    note: "Inner: iVar8 = floor(currentTime - ship+0x20), clamp [1,4]; Ship__ProcessAITick at 0x004722d0 hard-caps at iVar9>6 then checks FUN_0071acc0 vs deadline. AI lock-time constant DAT_0088bb20 (float) = 2.0f."
  - claim: "PoweredMaster::Update is the only 1Hz-strict subsystem"
    address: 0x00563780
    function: PoweredMaster_Update
    confidence: high
    note: "Gate: currentTime - ship+0xc0 > DAT_00892e20 (1.0f = 0x3F800000)."
  - claim: "WeaponSystem child Update gates at 0.33s (3Hz per child)"
    address: 0x005847d0
    function: WeaponSystem__Update
    confidence: high
    note: "Inner per-child gate: child+0x12 (accumulator) > DAT_00892fc0 (0.33f = 0x3EA8F5C3)."
  - claim: "StateUpdate emission is UNGATED — fires every main tick per ship per peer"
    address: 0x0069ee50
    function: MultiplayerGame__SendStateUpdates
    confidence: high
    note: "Called via Mpgame vtable slot 0x328 once per main tick. No internal rate gate; the dirty-flag system at Ship__WriteStateUpdate (0x005B17F0) is the only suppression mechanism. Force-resend gate is the per-field 1.0s timer (DAT_00888860)."
  - claim: "Force-resend threshold (per-tracker absolute resync) is 1.0s"
    address: 0x00888860
    function: null
    confidence: high
    note: "DAT_00888860 = 0x3F800000 = 1.0f. Read at Ship__WriteStateUpdate (0x005b17f0) as `gameTime - tracker+0x4 > 1.0s` and `gameTime - tracker+0x24 > 1.0s` for the bForceResendPos gate."
  - claim: "TGNetwork keepalive interval is 5.0s"
    address: 0x0088bd58
    function: null
    confidence: high
    note: "DAT_0088bd58 = 0x40A00000 = 5.0f. Read in TGWinsockNetwork_Update (FUN_006b4560) as `gameTime - WSN+0xc0 > 5.0s` for the connect-ping path."
  - claim: "TGNetwork session timeout is 360s (6 min)"
    address: null
    function: TGWinsockNetwork_Ctor
    confidence: high
    note: "WSN+0xb4 seeded with 0x43b40000 = 360.0f at construction. Hard disconnect after 6 minutes silence."
  - claim: "TGNetwork connect-retry interval is 45s"
    address: null
    function: TGWinsockNetwork_Ctor
    confidence: high
    note: "WSN+0xb8 seeded with 0x42340000 = 45.0f at construction. Boot-phase connect retry."
  - claim: "Collision rate-limit gate is per-pair with 5 cooldown values"
    address: 0x005a22a0
    function: Ship__CollisionRateGate
    confidence: high
    note: "Ship vtable+0x13C. 5-way conditional table on player count + host/client + friendly-fire: 0.1f (0x3DCCCCCD) / 0.125f (0x3E000000) / 0.166667f (0x3E2B020C) / 0.25f (0x3E800000) / 0.5f (0x3F000000)."
  - claim: "Stock has NO SetTimer/WM_TIMER for the main game tick"
    address: null
    function: null
    confidence: high
    note: "Negative claim. SetTimer call sites in stbc.exe: GameSpy query throttle, CRT thread sync. None route to TopWindow__Update or Application::Tick. The 33ms WM_TIMER described in pre-v5 versions of this doc is exclusive to the proxy DLL at src/proxy/ddraw_main/game_loop_and_bootstrap.inc.c:1410."
companions:
  - docs/networking/ack-outbox-deadlock.md
  - docs/networking/packet-bundling.md
  - docs/networking/netimmerse-transport-deep-dive.md
  - docs/networking/multiplayer-flow.md
supersedes:
  - 2026-02-15
---

> [docs](../README.md) / [architecture](README.md) / main-loop-timing.md

# STBC Main Loop & Timing Architecture

> [!NOTE]
> **Stock STBC has NO WM_TIMER for the main game tick.** The natural tick is the PeekMessage spin loop at `Application_RunMessageLoopIteration` (0x007b8790); when no Windows message is pending, it dispatches via vtable[0x80] to `UtopiaApp_PerFrameTick` (0x00438e20). The 33ms WM_TIMER described in pre-v5 versions of this doc was an artifact of the **proxy DLL** (which fires WM_TIMER directly into `TopWindow__Update` at 0x0043b4f0 to drive game logic in minimized-headless mode). Stock runs unthrottled (capped at 60Hz frame rate); idle-throttles to 49ms (~20Hz) when GameSpy is idle (`qr_t[0xec] == 0`). See [v5-evidence-header.md](../guides/v5-evidence-header.md) for the standard. Source evidence: `.claude/agent-memory/game-archaeology-specialist/tick-rate-inventory-validation-20260528.md`.

Reverse-engineered from stbc.exe via Ghidra decompilation. Two functions created this pass: `Application_RunMessageLoopIteration` (0x007b8790) and `UtopiaApp_PerFrameTick` (0x00438e20). Tick constants byte-confirmed from `.rdata` at the addresses cited in the evidence rows.

**Related docs**:
- [ack-outbox-deadlock.md](../networking/ack-outbox-deadlock.md) — drained per main tick by `SendOutgoingPackets`; deadlock interacts with the cadences here
- [packet-bundling.md](../networking/packet-bundling.md) — what `SendOutgoingPackets` actually does per tick
- [netimmerse-transport-deep-dive.md](../networking/netimmerse-transport-deep-dive.md) — engine-level transport layer
- [multiplayer-flow.md](../networking/multiplayer-flow.md) — end-to-end join flow that depends on these cadences

---

## 1. Stock Main Loop Architecture [v5-validated 2026-05-28]

### Call chain

```
WinMain (FUN_0086eff0)
 └── Application_RunMessageLoop (FUN_007ba5a0)
      └── do { vtable[0x78]() } while (!=0)
           └── Application_RunMessageLoopIteration (0x007b8790)
                ├── PeekMessageA -> if (msg) { TranslateMessage; DispatchMessageA }
                └── if (!msg) vtable[0x80]()       <- per-frame idle dispatch
                     └── UtopiaApp_PerFrameTick (0x00438e20)
                          ├── 49ms timeGetTime throttle (only when GameSpy registered + idle)
                          └── Application::Tick (FUN_006cdd20)
                                ├── vtable[0x94]()  -> UtopiaApp_FrameWork (0x00438e60)
                                │     ├── Pause-state machine (FUN_006cdb90)
                                │     ├── Render passes (FUN_0070fdb0 / FUN_0070fdf0)
                                │     └── TopWindow::Update (0x0043b4f0)  <-- the actual game tick
                                ├── 60 Hz frame-rate cap (app[0x1d] gate)
                                ├── DirectInput poll (FUN_006e6430)
                                └── app[0x19]++  (frame counter)
                          └── TGEventManager dispatch (FUN_0071e420)
```

### PeekMessage idle dispatch — no Sleep, no WaitMessage

The loop driver `FUN_007ba5a0` (Application::RunMessageLoop) is a tight `do { vtable[0x78](&retval); } while (!=0);` over `Application_RunMessageLoopIteration` (0x007b8790). The iteration body is the standard NiApplication PeekMessage pattern:

```c
bool Application::RunMessageLoopIteration(int* pRetval) {
    MSG msg;
    if (PeekMessageA(&msg, NULL, 0, 0, PM_REMOVE)) {
        if (msg.message == WM_QUIT) { *pRetval = msg.wParam; return false; }
        TranslateAccelerator(...);
        TranslateMessage(&msg);
        DispatchMessageA(&msg);
    } else {
        this->vtable[0x80](this);   // <-- UtopiaApp_PerFrameTick
    }
    return true;
}
```

There is no `Sleep`, no `WaitMessage`, no `MsgWaitForMultipleObjects` in this loop. When PeekMessage returns 0, the per-frame tick fires immediately. **The loop runs as fast as the CPU allows** unless the throttle gate inside `UtopiaApp_PerFrameTick` engages.

### 60 Hz frame-rate cap is a render gate only

Application::Tick (`FUN_006cdd20`) compares `app[0x1d] + app[0x1e] <= app[0x15]` to set a `readyToRender` flag. `app[0x1d]` (m_fMinFramePeriod) is seeded with `0x3C888889` = 1.0f/60.0f = 0.01666667s at construction (`TGApp_Ctor`, 0x00437fea). This cap gates rendering readiness — not game-logic execution. The TopWindow::Update body runs every iteration of the main loop; the renderer only swaps when the frame cap allows.

Base `NiApplication` uses 1/100 (100 Hz cap) by default. TGApp overrides to 1/60 in its constructor.

### 49ms idle throttle (the GameSpy-driven floor)

`UtopiaApp_PerFrameTick` (0x00438e20) gates Application::Tick on:

```c
if (qr_t == NULL || qr_t[0xec] != 0 || (timeGetTime() - DAT_0097F950) > 49) {
    DAT_0097F950 = timeGetTime();           // anchor last-tick
    Application__Tick();                     // FUN_006cdd20
    TGEventManager__Dispatch();              // FUN_0071e420
}
```

The 49 decimal lives as an immediate at 0x00438e3c. The condition reads: "tick only if GameSpy isn't registered, OR GameSpy is active, OR at least 49ms have elapsed." In practice the third arm becomes the throttle when GameSpy is registered but idle (`qr_t[0xec] == 0`) — effectively ~20Hz minimum cadence. Default (unthrottled) PeekMessage spin gives 60-200+ Hz depending on workload.

---

## 2. Proxy DLL Difference [v5-validated 2026-05-28]

The proxy DLL (this project's `ddraw.dll`) does NOT use the natural Application::Tick chain. Instead it installs a Windows `SetTimer(hwnd, 0xBCBC, 33, GameLoopTimerProc)` that calls `TopWindow__Update` (0x0043b4f0) directly at 33ms intervals. See `src/proxy/ddraw_main/game_loop_and_bootstrap.inc.c:1410`.

| Aspect | Stock | Proxy |
|--------|-------|-------|
| Driver | PeekMessage spin (`Application_RunMessageLoopIteration` 0x007b8790) | `SetTimer 0xBCBC` -> WM_TIMER -> `GameLoopTimerProc` |
| Wakeup | Whenever the message queue is empty | Every 33ms (Windows multimedia timer) |
| Tick entry | `UtopiaApp_PerFrameTick` (0x00438e20) -> Application::Tick -> TopWindow::Update | `TopWindow__Update` (0x0043b4f0) directly — skips Application::Tick |
| Frame-rate cap | 60 Hz gate on rendering (`app[0x1d] = 1/60`) | Bypassed (TopWindow::Update runs on every timer fire) |
| Effective rate | ~60-200 Hz unthrottled / ~20 Hz idle | ~30 Hz (33ms timer + ~5ms work) |
| Sleep behavior | None — 100% CPU when active | Implicit yield between timer fires |

**Why the proxy diverges**: the dedicated-server use case requires headless operation in a minimized window. Minimized message-pump behavior changes under WM_PAINT/WM_ACTIVATE, and the natural Application::Tick chain can stall. The proxy bypasses the chain entirely by driving TopWindow::Update from WM_TIMER.

**Implication for OpenBC**: OpenBC currently matches the proxy (30Hz fixed). It does NOT match stock (which runs unthrottled / 60Hz-render-capped). Wire-rate parity tests against stock clients should account for this gap — see Section 7.

---

## 3. TopWindow::Update Tick Chain [v5-validated 2026-05-28]

`TopWindow__Update` (0x0043b4f0) is the real per-tick work — called from both the natural chain (via UtopiaApp_FrameWork at 0x00438e60, vtable slot 0x94) and the proxy (directly from WM_TIMER).

```c
void TopWindow__Update(int* this) {
    FUN_0071a9e0();                                             // ?
    TGTimerManager__Update(*(Clock+0x90));                      // gameTime — fires scheduled timers
    TGTimerManager__Update(*(Clock+0x54));                      // frameTime — fires scheduled timers
    TGEventManager__ProcessQueue();                             // drain event queue (no rate gate)
    Ship__AITickScheduler();                                    // 0x004721b0 — AI batcher
    FUN_0046f420();                                             // scene-priority dispatcher (14-sample rolling mean)
    FUN_00443ac0();                                             // TopWindow scene work
    FUN_004447f0();                                             // ?
    FUN_00444840();                                             // ?
    FUN_0043b790();                                             // TopWindow tail
    // ... selective render (FUN_004433e0)
}
```

The two `TGTimerManager::Update` calls are critical: one uses `gameTime` (Clock+0x90, time-scaled — can be slowed/sped via `UtopiaModule.SetTimeRate`), the other uses `frameTime` (Clock+0x54, wall-clock). Both drain fully each tick — any timer whose due time has passed fires this tick.

`TGEventManager::ProcessQueue` similarly drains fully. There is no per-tick event budget; queued events all dispatch before the tick returns.

---

## 4. Per-System Tick Gates [v5-validated 2026-05-28]

Every per-tick subsystem in the binary, ordered by frequency.

### Main loop (the driver itself)

| System | Address | Rate | Constant source | Wire impact |
|--------|---------|------|-----------------|-------------|
| Application_RunMessageLoopIteration | 0x007b8790 | Unthrottled (PeekMessage spin) | n/a | None directly |
| UtopiaApp_PerFrameTick idle throttle | 0x00438e20 | ~20 Hz floor when GameSpy idle | immediate 49 @ 0x00438e3c | None directly |
| Application::Tick frame-rate cap | FUN_006cdd20 | 60 Hz render cap | `0x3C888889` = 1/60 @ app[0x1d] (seeded at 0x00437fea) | Render only |
| Proxy GameLoopTimerProc | (proxy DLL) | 30 Hz (33ms) | `SetTimer(hwnd, 0xBCBC, 33, ...)` | Drives all packet I/O via TopWindow::Update |

### Per-main-tick (run every main tick)

| System | Address | Gate | Constant | Wire impact |
|--------|---------|------|----------|-------------|
| TGTimerManager::Update (gameTime) | FUN_006dc490 | none — drains queue | n/a | Posts events that may emit packets |
| TGTimerManager::Update (frameTime) | FUN_006dc490 | none — drains queue | n/a | Posts events that may emit packets |
| TGEventManager::ProcessQueue | FUN_006da2c0 | none — drains queue | n/a | Dispatches all queued events |
| Ship__AITickScheduler | 0x004721b0 | up to 4 cycles/ship/tick, 6-eval cap | floor[1,4]; hard-cap 6 | Posts AI events (BUILDER_DONE 0x800017 etc.) |
| TGWinsockNetwork::Update | FUN_006b2620 | none | n/a | Drives `SendOutgoingPackets` (see [packet-bundling.md](../networking/packet-bundling.md)) |
| SendOutgoingPackets | 0x006b55b0 | none | n/a | All outbound UDP per peer |
| ProcessIncomingPackets | 0x006b5c90 | none | n/a | All inbound UDP processing |
| MultiplayerGame::SendStateUpdates | 0x0069ee50 | **ungated** | n/a | StateUpdate (0x1C) per ship per peer every tick |
| Ship__WriteStateUpdate | 0x005b17f0 | per-field dirty flags + 1.0s force-resend | DAT_00888860 = 1.0f | StateUpdate payload suppression only |
| PoweredSubsystem::Update | FUN_00562470 | none | n/a | Power state in StateUpdate |
| RepairSubsystem::Update | FUN_005652a0 | none | n/a | Posts events 0x800074 (REPAIRED), 0x800075 (TIME_TO_REPAIR) |
| CloakingSubsystem::Update | FUN_0055e500 | none | engage time 5.0s, fail threshold 0.8f | Cloak state in StateUpdate flag 0x40 |
| ShieldGenerator::BoostShield | FUN_0056a420 | none | DAT_0088bacc = 0.166667f power fraction | StateUpdate shield fields |

### Sub-rate (gated below main tick)

| System | Address | Gate | Constant | Wire impact |
|--------|---------|------|----------|-------------|
| PoweredMaster::Update | 0x00563780 | `currentTime - ship+0xc0 > 1.0s` (1 Hz strict) | DAT_00892e20 = 1.0f | Battery state in StateUpdate |
| WeaponSystem child Update | FUN_005847d0 inner | `child+0x12 > 0.33s` (~3 Hz per child) | DAT_00892fc0 = 0.33f | Drives phaser recharge / torpedo reload, surfaces in StateUpdate flag 0x80 |
| Collision per-pair cooldown | 0x005a22a0 | 5-way conditional table | 0.1f / 0.125f / 0.166667f / 0.25f / 0.5f | CollisionEffect (0x15) per pair |

### Super-rate (multiple cycles per main tick)

| System | Address | Cap | Notes |
|--------|---------|-----|-------|
| AI ProcessAITick | 0x004722d0 | up to 4 cycles/ship/tick, 6-eval budget | Soft real-time catch-up if delta is large |

### Subsystem Update master gate

All subsystem Update bodies are gated on `DAT_0097fa89 != 0 AND (DAT_0097fa89 != 0x01 OR DAT_0097fa8a != 0)` — server runs subsystem updates; clients run them too but the state is read-only on the client.

---

## 5. Network Cadence Constants [v5-validated 2026-05-28]

The cadences that bound multiplayer state replication.

| Constant | Address | Value | Read at | Meaning |
|----------|---------|-------|---------|---------|
| Frame cap | app[0x1d] (seeded 0x00437fea) | 1/60 = 0.01667s | FUN_006cdd20 | 60 Hz render readiness |
| Idle throttle | imm 0x31 @ 0x00438e3c | 49 ms | UtopiaApp_PerFrameTick | ~20Hz floor when GameSpy idle |
| Force-resend (pos/rot) | DAT_00888860 | 1.0f | Ship__WriteStateUpdate (0x005b17f0) | Forces absolute pos resync every 1s |
| Keepalive interval | DAT_0088bd58 | 5.0f | TGWinsockNetwork_Update (FUN_006b4560) | Internal connect ping when no peer activity |
| Connect retry | WSN+0xb8 (ctor 0x42340000) | 45.0f | TGWinsockNetwork_Update (boot path) | Boot-phase peer connect retry |
| Session timeout | WSN+0xb4 (ctor 0x43b40000) | 360.0f | inferred from peer last-recv | Hard disconnect after 6 min silence |
| Stale-disconnect threshold | 0x008958cc | 15.0f | SendOutgoingPackets post-scan | Triggers peer disconnect after 15s no traffic |
| GameSpy heartbeat | hardcoded | 30s, max 10 attempts | qr_t::Heartbeat | LAN/master server presence |
| AI lock-time bonus | DAT_0088bb20 (float) | 2.0f | Ship__ProcessAITick (0x004722d0) | AI cycle bonus on delta overshoot |
| PoweredMaster 1Hz | DAT_00892e20 | 1.0f | PoweredMaster_Update (0x00563780) | Battery + reactor tick |
| WeaponSystem 3Hz | DAT_00892fc0 | 0.33f | WeaponSystem__Update (FUN_005847d0) | Per-weapon-child gate |
| Scene-priority min budget | DAT_0088bb20 (double) | 0.01 | FUN_0046f420 | Min per-group budget |
| Scene-priority divisor | DAT_0088bb28 | 1/14 (double) | FUN_0046f420 | 14-sample rolling-mean divisor |

**Net effect on StateUpdate traffic**: At proxy 30 Hz with 8 players and 16 trackers each, base emission rate is ~3,840 send sites/sec across all peers, heavily reduced by per-field dirty-flag suppression. Stock client would run the same loop at 60+ Hz, doubling base emission.

---

## 6. NetImmerse Adaptive Scene-Priority Scheduler [v5-validated 2026-05-28]

`FUN_0046f420` is the per-frame work dispatcher that calls registered updateable objects (ships, AI, physics). It uses a NetImmerse-style adaptive deadline.

### Algorithm

1. **Sample buffer**: 16-sample ring at `DAT_00981560`, circular index `DAT_009815E0 & 0xF`. Each entry is a frame time.
2. **Mean computation**: Excludes min and max from the average:
   ```
   mean = (sum - min - max) / 14
   ```
   The divisor `1/14` lives at `DAT_0088bb28` (double) = `0x3FB2492492492492`.
3. **Per-group budget**: 4 priority groups (0-3). Group 0 (highest) runs first; remaining budget cascades down to groups 1, 2, 3.
4. **Min budget clamp**: `DAT_0088bb20` (double) = 0.01s — a group always gets at least 10ms of budget regardless of frame timing.
5. **Round-robin**: `DAT_009815E4` rotates which group gets first pick across ticks.

### Group iteration

`FUN_0046f610` iterates the list at `DAT_00981494[group*6]`, calling each entry's `vtable[0](deadline)` until budget exhausted.

### Implication

High-priority objects (rendered ships, active AI) can starve low-priority ones (idle scene props) when the frame is loaded. This explains observed "AI freeze" reports under heavy combat load — when group 0 burns the full budget, groups 1-3 may skip ticks entirely.

---

## 7. OpenBC Parity Implications

### Critical-must-match

1. **Per-system tick gates MUST match.** PoweredMaster at 1Hz, WeaponSystem child at 3Hz, AI at up to 4 cycles/ship/tick. Wrong rates cause wrong shield/power/weapon state on the wire.
2. **Force-resend interval is 1.0s.** Position/rotation absolute resyncs every 1s regardless of dirty flag — receivers depend on this to prevent drift.
3. **StateUpdate is UNGATED per main tick.** Every ship emits a StateUpdate for every peer every tick (suppression only via dirty flags). Skipping ticks breaks dead-reckoning on clients.
4. **Session timeout is 360s.** Clients silent for >6 min get hard-disconnected.

### Important-to-match

5. **Main tick rate**: OpenBC currently runs ~30 Hz (matching the proxy). Stock runs ~60+ Hz. The wire format tolerates both, but observation density on the wire will differ (more StateUpdates per second on stock).
6. **Idle throttle**: When GameSpy is registered but idle, drop to ~20Hz. Avoids CPU burn on a stalled dedicated server.
7. **Scene-priority budget**: A reimplementation can use a simpler scheduler if it can keep tick latency under 33ms. The adaptive algorithm matters when frames are over budget.

### Safe to differ

8. **Frame-rate cap (60 Hz render gate)**: only affects rendering, irrelevant to headless server.
9. **49ms idle anchor**: implementation detail; any throttle to ~20Hz when no players present is equivalent.
10. **AI cycle bonus** (2.0f lock-time): tuning value; matches catch-up semantics, not wire-observable.

---

## 8. Cross-Refs

- [packet-bundling.md](../networking/packet-bundling.md) — what `SendOutgoingPackets` does every tick (4-pass drain, 255-msg cap, 512-byte MTU)
- [ack-outbox-deadlock.md](../networking/ack-outbox-deadlock.md) — the per-tick ACK retransmit gate that interacts with these cadences
- [netimmerse-transport-deep-dive.md](../networking/netimmerse-transport-deep-dive.md) — engine-layer transport
- [multiplayer-flow.md](../networking/multiplayer-flow.md) — how cadences interact during join handshake
- [stateupdate.md](../protocol/stateupdate.md) — the per-tick wire payload these cadences drive

---

## 9. Open Questions

1. **app[0x27] = 0.25f semantics**: seeded in ctor but no usage trace yet. Possibly auto-pause delay.
2. **FUN_006e6420 identity**: appears to be an empty stub; not load-bearing.
3. **SensorSubsystem Update rate**: no dedicated function found this pass; assumed to run at the generic per-tick subsystem rate. Worth a follow-up.
4. **Stock client actual tick rate when not GPU-bound**: needs instrumentation; estimate is 60-200 Hz uncapped, ~60 Hz with vsync.
5. **DAT_0099c6bc network-time anchor writer**: all callers READ it; the writing path was not located this pass.

---

## 10. Functions Created This Pass

- `Application_RunMessageLoopIteration` @ 0x007b8790 (PeekMessage iteration body)
- `UtopiaApp_PerFrameTick` @ 0x00438e20 (per-frame idle dispatch + 49ms throttle)
- `UtopiaApp_FrameWork` @ 0x00438e60 (vtable slot 0x94)
- `Application_OnPauseTransition` @ 0x006cdf70
- `TGWinsockNetwork_Update` @ 0x006b2620 (vtable slot 2)

Ghidra saved successfully.
