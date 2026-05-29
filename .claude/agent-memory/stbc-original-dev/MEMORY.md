# STBC Original Developer Agent Memory

## Key Design Intent Conclusions

### Scene Graph is Load-Bearing for Networking
FUN_005b17f0 (network state update) calls NiAVObject vtable methods (0x94=GetWorldTranslation, 0xac=GetWorldRotation, 0xb0=GetWorldScale) with ZERO null checks. Objects in the simulation MUST have valid scene graphs. This was an invariant, not a checked condition. See [design-intent.md](design-intent.md).

### Stock Dedicated Server = Full Engine + Different UI
The stock "Dedicated Server" toggle (MultiplayerMenus.py:2996) only sets IsClient=0. Full renderer, NIF loading, scene graph, simulation all run normally. The dedicated host sees the options menu pane, not the tactical view. GPU still renders every frame.

### Ship Subsystem/Weapon Population Chain
CreateShip -> SetupModel(NIF load) -> LoadPropertySet(hardpoints) -> SetupProperties(C++ engine creates subsystem objects from hardpoints + scene graph nodes) -> UpdateNodeOnly. SetupProperties requires named NiNode children in the scene graph matching hardpoint names.

### The Correct Headless Approach
Stub D3D draw calls (DrawPrimitive, Present/Flip) at the lowest level. Let renderer pipeline build fully. The NIF loader and scene graph construction depend on renderer internal state. PatchDeviceCapsRawCopy prevents the raw memcpy crash, PatchRendererMethods stubs specific vtable methods. See [design-intent.md](design-intent.md) for full analysis.

### NiDX7Renderer Pipeline (FUN_007c3480) Analysis
FUN_007cb2c0 (NiD3DGeometryGroupManager ctor) takes 3 stack params, not 1 as Ghidra shows:
IDirect3D7*, IDirect3DDevice7*, bool. RET 0xC confirms. Both D3D pointers get AddRef'd via
vtable[1]. T&L flag determines SYSTEMMEMORY vs WRITEONLY VB path. Adapter creation (FUN_007c7f80)
calls DirectDrawCreateEx internally via GetProcAddress("DDRAW.DLL") which hits the proxy DLL.
Full analysis in [design-intent.md](design-intent.md).

### Multiplayer Architecture: Split Authority Model with Delta Compression
NOT lockstep, NOT fully peer-to-peer, NOT fully server-authoritative. Split model:
- Server-authoritative: collision damage, object lifecycle, game flow, explosions
- Owner-authoritative: movement/position (StateUpdate sends POSITIONS not INPUTS),
  weapon fire (0x19/0x1A), event-forward messages (0x07-0x12)
- Receiver-local: weapon damage (each client runs DoDamage independently)
State updates use dirty-flag delta compression with round-robin subsystem/weapon
budgets (10 bytes/6 bytes per frame).

### Full Network Protocol Architecture (NEW)
Two dispatch layers: C++ engine messages (binary, compact) and Python TGMessages
(via TGBufferStream). State updates use dirty-flag delta compression with round-robin
subsystem/weapon budgets (10 bytes/6 bytes per frame). Combat events (fire, cloak,
warp, explode) are separate reliable messages. Python messages use first-byte type
discriminator with App.MAX_MESSAGE_TYPES as base offset. Full protocol breakdown
in design-intent.md under "Multiplayer Network Protocol - Full Architecture".

### Python vs C++ Split
C++ handles ~90% of simulation (physics, collision, weapons, shields, AI, network
serialization). Python handles ~10% (mission setup, game mode rules, UI flow, event
handlers, scoring, chat). Cannot run server on Python alone.

### Stock Dedicated Server Implementation
MultiplayerMenus.py line 2996: `g_pHostDedicatedButton.IsChosen()` -> `SetIsClient(0)`.
Line 909-917: `IsHost() and (not IsClient())` -> show options pane instead of tactical.
Full renderer runs. No headless capability. This was a scope/priority decision, not
a technical impossibility.

### Collision Damage is HOST-Authoritative
Physics response (bouncing) runs locally on all clients. Damage calculation runs ONLY on
the host. Two collision events: 0x00800050 (client-detected, sent to host via opcode 0x0C)
and 0x008000fc (host-validated, triggers damage). FUN_005afad0 (HostCollisionEffectHandler)
applies damage on the host; on clients it only damages OTHER players' ships (not local ship).
FUN_005ae140 invulnerability check: client returns true for own ship, host checks ship+0x2e4.
Requires ProximityManager active + valid bounding volumes on server.
See [design-intent.md](design-intent.md) "Collision Damage Authority Model".

### InitObject Hook Safety
`src/scripts/Custom/DedicatedServer.py` currently replaces `SpeciesToShip.InitObject`
with a logging wrapper that reruns the same `GetShipFromSpecies/SetupModel/LoadPropertySet/SetupProperties/UpdateNodeOnly`
sequence the stock Python script already performs. Because that patch reimplements the
behavior instead of calling the original, any future adjustments or side effects of the
native path can drift, so the safest pattern is to call `_orig_InitObject` inside the
wrapper and only add instrumentation.

### Server Authority Feasibility Assessment
Making movement server-authoritative requires changing StateUpdate from position-based
to input-based -- a fundamental protocol redesign that breaks all clients. Not practical.
No client-prediction/server-reconciliation infrastructure exists in BC's engine.
Realistic additions: damage bounds checking, weapon fire rate limiting, plausibility
validation. Full server-side damage computation introduces desync without prediction.
See full analysis in conversation dated 2026-02-16.

### OpenBC Design Questions (2026-02-23)
- **PythonEvents**: Generated by C++ event handlers (not scripts). Simulation side effects.
- **Weapon damage**: Receiver-local by design (56K optimization). Server-side OK for OpenBC-only.
- **ObjCreate 0x02**: Host dummy ship (3 instances = 3 player joins).
- **PythonEvent2 0x0D**: Client→server private notification. NOT relayed. Do not relay.
- **Post-death StateUpdates**: Continue during 9.5s explosion (ship = debris still simulating).
- **EnterSet 0x1F**: Custom mission multi-zone infrastructure. Never fires in FFA/TDM.
Full details in design-intent.md "OpenBC Design Questions" section.

### StateUpdate Condition/Power Byte Semantics (2026-02-26)
- **Condition byte is scalar, not boolean**: subsystem ReadState applies `condition = byte * (1/255) * maxCondition` (FUN_0056d390). So `0x01` means "barely alive" (~0.39%), not destroyed.
- **`0x00` means destroyed; `0xFF` means full health** for hull/bridge/shield/system condition bytes.
- **Power slider default is 100% by construction**: PoweredSubsystem ctor sets `+0x90 = 1.0f`, then setup path reaffirms 1.0.
- **Wire power byte `0x64` = 100%** in flag 0x20 PoweredSubsystem state (`powerPctWanted = int(pct*100)`).

### Multiplayer Score/Cloak Authority Notes (2026-02-26)
- **Score messages are server-originated (`0x36`/`0x37`, S→C)**, but stock dedi has a known gap: weapon kills often emit no `SCORE_CHANGE (0x36)` while collision/self-destruct paths do.
- **Cloak toggles are client-initiated relay events** (`0x0E/0x0F` via GenericEventForward), frequently observed wrapped in client `PythonEvent2 (0x0D)` payloads in stock traces.

## File Index
- [design-intent.md](design-intent.md) - Detailed architecture analysis and design intent
- [load-bearing-bugs.md](load-bearing-bugs.md) - Bugs/behaviors that other code depends on
- [alternative-approaches.md](alternative-approaches.md) - Analysis of headless server strategies
