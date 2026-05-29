> [docs](../README.md) / [gameplay](README.md) / self-destruct-pipeline.md

---
title: Self-Destruct Complete Pipeline Analysis
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
  - claim: "TopWindow::SelfDestructHandler at 0x0050D070 — body size 0x0DB (219 bytes), ends 0x0050D14B. Bare code in Ghidra prior to this session; function created this pass."
    address: 0x0050D070
    function: TopWindow__SelfDestructHandler
    confidence: high
    note: "Created this session as `TopWindow__SelfDestructHandler`. Three execution paths (SP, MP host, MP client) verified against disassembly."
  - claim: "HostMsgHandler (opcode 0x13) at 0x006A01B0 — reads sender connection ID from TGBufferStream field at offset 0x0C, looks up ship via GetShipFromPlayerID, calls DoDamageToSelf(ship+0x2C4) passing the PowerSubsystem ptr."
    address: 0x006A01B0
    function: HostMsgHandler
    confidence: high
    note: "Cross-anchored with power-system.md C1 (PowerSubsystem at ship+0x2C4)."
  - claim: "DoDamageToSelf at 0x005AF5F0 — single-arg signature `float10(subsystem*)`. 5 xrefs confirmed: 0x0050D132, 0x006A01D3, 0x005AFD56, 0x006A0E18, 0x005B355B."
    address: 0x005AF5F0
    function: DoDamageToSelf
    confidence: high
    note: "Clar1 — prior doc claimed 2-arg `__thiscall(ship*, powerSubsystem*)`. Binary is 1-arg (subsystem*); ship is recovered inside DoDamageToSelf_Inner via subsystem+0x40 parent backref."
  - claim: "DoDamageToSelf_Inner at 0x005AF4A0 — 5-param `(ship*, subsystem*, float damageAmount, int* attacker, char force_kill)`. Body 0x005AF4A0-0x005AF5E6."
    address: 0x005AF4A0
    function: DoDamageToSelf_Inner
    confidence: high
  - claim: "ShipDeathHandler at 0x005AFEA0 — creates ET_OBJECT_EXPLODING event (type 0x0080004E) with hullHP (read from ship+0x14C) written to event+0x2C."
    address: 0x005AFEA0
    function: ShipDeathHandler
    confidence: high
    note: "Clar2 — prior doc said `dest = ship`. Asm sets event+0x28 = attacker_ship_id (or 0 when attacker NULL), event+0x2C = hullHP. Wire format claim resolves correctly at the wire layer; in-memory description was hand-wavy."
  - claim: "String \"TopWindow::SelfDestructHandler\" at 0x008E2354 (debug name for handler registration)"
    address: 0x008E2354
    confidence: high
    note: "Bytes byte-confirmed: 54 6f 70 57 69 6e 64 6f 77 3a 3a 53 65 6c 66 44 65 73 74 72 75 63 74 48 61 6e 64 6c 65 72 00 00."
  - claim: "String \"SELF_DESTRUCT_REQUEST_MESSAGE\" at 0x00952F44 (SWIG constant name for opcode 0x13)"
    address: 0x00952F44
    confidence: high
  - claim: "String \"ET_INPUT_SELF_DESTRUCT\" at 0x00953920 (event type 0x008001DD)"
    address: 0x00953920
    confidence: high
  - claim: "DAT_00888B54 = 0.0f (used as DoDamageToSelf early-return-NULL return value)"
    address: 0x00888B54
    confidence: high
  - claim: "DAT_008E5C18 = FLT_MAX (0x7F7FFFFF; raw bytes ff ff 7f 7f). Used as **dying-sentinel reentrancy guard** at ShipDeathHandler — `hullHP < FLT_MAX` means \"ship not yet sentinel-marked / still alive\". Once a ship enters dying state, hullHP is overwritten to FLT_MAX as a flag, preventing OBJECT_EXPLODING reentry."
    address: 0x008E5C18
    confidence: high
    note: "C2 — corrects prior doc's \"some threshold\" framing. Cross-anchored with protocol leaf #18 (objnotfound-requestobj-enterset) which uses the same FLT_MAX sentinel pattern for DamageableObject HP slot."
  - claim: "Opcode 0x13 payload is 1 byte (just the opcode). Disasm at 0x0050D0CE: `MOV byte ptr [ESP+0x17], 0x13`, then `PUSH 0x1` (size), `PUSH EAX` (ptr), CALL FUN_006B84D0 (TGMessage BufferCopy)."
    address: 0x0050D0CE
    function: TopWindow__SelfDestructHandler
    confidence: high
  - claim: "TGMessage allocation size 0x40 bytes at 0x0050D0A1 (`PUSH 0x40` prior to NiAlloc call)."
    address: 0x0050D0A1
    function: TopWindow__SelfDestructHandler
    confidence: high
  - claim: "Host connection ID read from network+0x20 at 0x0050D0D8: `MOV ECX, dword ptr [EDI + 0x20]`."
    address: 0x0050D0D8
    function: TopWindow__SelfDestructHandler
    confidence: high
  - claim: "Event-type registration: `FUN_006d92b0(&DAT_00987878, 0x8001DD, \"TopWindow::SelfDestructHandler\")` inside FUN_0050CA50."
    address: 0x0050CA50
    confidence: high
  - claim: "Name→code binding: `FUN_006da130(&LAB_0050D070, \"TopWindow::SelfDestructHandler\")` inside FUN_0050C8B0."
    address: 0x0050C8B0
    confidence: high
  - claim: "HostMsgHandler reads sender connection ID from pStream->dwField_0x0C (TGBufferStream field 0x0C carries embedded sender connection ID). Then HostMsgHandler calls `FUN_005af5f0(*(undefined4 *)(ship + 0x2c4))` — passes ship+0x2C4 (PowerSubsystem ptr per power-system.md C1)."
    address: 0x006A01B0
    function: HostMsgHandler
    confidence: high
  - claim: "DoDamageToSelf passes attacker=NULL and force_kill=1 to DoDamageToSelf_Inner. NULL attacker results in event+0x28 = 0 in ShipDeathHandler, which is why self-destruct awards no kill credit (FiringPlayerID=0)."
    address: 0x005AF5F0
    function: DoDamageToSelf
    confidence: high
    note: "Trace data corroborates: 6/6 firing_player=0 in PR#34 testing."
companions:
  - docs/gameplay/power-system.md
  - docs/gameplay/damage-system.md
  - docs/networking/ship-death-lifecycle.md
  - docs/protocol/game-opcodes.md
  - docs/protocol/objnotfound-requestobj-enterset-wire-format.md
---

> [!NOTE]
> **v5 re-validation 2026-05-28 — 3 corrections (1 HIGH cascade-pending + 2 medium/low) + 2 clarifications + 3 OQs**. Three execution paths narrative + wire format byte-confirmed. Handler at 0x0050D070 CREATED this pass as `TopWindow__SelfDestructHandler`.
>
> - **C1 (MED)**: `DestroyObject Handler (Opcode 0x14)` section (lines 319-358 of prior doc) is **vestigial**. The handler at FUN_006A01E0 exists but is NEVER invoked during MP ship death (0/59 sends in battle trace per [ship-death-lifecycle.md](../networking/ship-death-lifecycle.md) — leaf #11). The prior doc's own findings section already states this, but the named subsection implied 0x14 IS sent after explosion. Section reframed below.
> - **C2 (LOW)**: `DAT_008E5C18` is **FLT_MAX dying-sentinel reentrancy guard**, NOT a damage threshold. Prior doc framed it as "some threshold". Once a ship enters dying state, `*(float*)(ship+0x14C)` is overwritten to FLT_MAX (0x7F7FFFFF) — the gate `hullHP < FLT_MAX` is "ship not yet sentinel-marked / still alive". Cross-anchored with protocol leaf #18 (same FLT_MAX sentinel pattern for DamageableObject HP slot).
> - **C3 (HIGH — CASCADE PENDING)**: The flag identifications at `0x0097FA88` / `0x0097FA89` / `0x0097FA8A` in CLAUDE.md "Key Globals" are inverted. Binary truth (per FUN_0069EB17 / MultiplayerGame_Ctor): `0x0097FA89 = GameLive_MP`, `0x0097FA8A = IsHost`. This propagates across multiple docs (this one, damage-system, network-protocol, ship-death-lifecycle, etc.). This doc preserves the prior flag labels in narrative below and flags them in the dedicated **Cascade Pending** section. Behavior described by the prior doc is correct; only the per-flag global names are inverted.

---

## C3 (CASCADE PENDING) — Flag identifications inverted at 0x0097FA88 / 0x0097FA89 / 0x0097FA8A

> [!IMPORTANT]
> **C3 HIGH — Flag attribution CASCADE pending (2026-05-28)**
>
> CLAUDE.md "Key Globals" currently lists:
>
> - `0x0097FA88` | IsClient (BYTE) — 0=host, 1=client
> - `0x0097FA89` | IsHost (BYTE) — 1=host, 0=client
> - `0x0097FA8A` | IsMultiplayer (BYTE)
>
> **Binary truth** (per FUN_0069EB17 in MultiplayerGame_Ctor at 0x0069E590):
>
> - `0x0097FA88` = **IsClient** (matches CLAUDE.md)
> - `0x0097FA89` = **GameLive_MP** (toggles to 1 at end of MultiplayerGame_Ctor for **BOTH host AND client** — NOT IsHost)
> - `0x0097FA8A` = **IsHost** (gates host-only block that registers ChecksumComplete / EnterSet handlers and creates NoMe / Forward groups — NOT IsMultiplayer)
>
> This mislabel has propagated across multiple docs (damage-system, network-protocol, ship-death-lifecycle, and others). A focused CLAUDE.md + cross-doc sweep is needed to propagate the correction.
>
> **This doc preserves the prior flag labels in the narrative below but flags them here so future readers see the cascade warning before diving into the 3-path narrative.** Do not assume per-doc flag claims are correct until they are re-verified against this attribution. With corrected labels, the 3-path narrative still maps perfectly: Host MP (GameLive=1, IsHost=1) → local damage; Client MP (GameLive=1, IsHost=0) → network send via 0x13; SP (GameLive=0) → local damage with TestMenuState guard.

---

## Executive Summary

Self-destruct is a **shipped, working feature** that allows any player to destroy their own ship via Ctrl+D. In multiplayer, it uses opcode 0x13 (HostMsg) as a **client-to-host request** -- the client sends a 1-byte message (just the opcode byte `0x13`) to the host, which looks up the requesting player's ship and calls `FUN_005af5f0` (DoDamageToSelf) to apply lethal damage through the PowerSubsystem. The ship then follows the normal destruction pipeline (hull reaches zero -> OBJECT_EXPLODING event -> scoring -> DestroyObject network broadcast).

There is no confirmation dialog, no countdown timer, and no abort mechanism. Ctrl+D = instant death.

---

## Key Components

### Constants and Strings [v5-validated 2026-05-28]

| Item | Address | Value |
|------|---------|-------|
| ET_INPUT_SELF_DESTRUCT | string at 0x00953920 | Event type `0x8001DD` (registered in FUN_0050ca50) |
| SELF_DESTRUCT_REQUEST_MESSAGE | string at 0x00952F44 | SWIG constant name (opcode `0x13`) |
| "TopWindow::SelfDestructHandler" | string at 0x008E2354 | Debug name for handler registration (byte-confirmed) |
| DAT_00888B54 | 0x00888B54 | 0.0f — DoDamageToSelf early-return value |
| DAT_008E5C18 | 0x008E5C18 | FLT_MAX (0x7F7FFFFF, bytes `ff ff 7f 7f`) — **dying-sentinel reentrancy guard** (see C2 in NOTE block) |

### Key Functions [v5-validated 2026-05-28]

| Address | Name | Signature | Role |
|---------|------|-----------|------|
| 0x0050D070 | TopWindow__SelfDestructHandler | `__thiscall(this, pEvent)` | Client-side: local SP destruct or MP network send. **CREATED this pass** — bare code prior; body size 0x0DB (219 bytes). |
| 0x006A01B0 | HostMsgHandler (opcode 0x13) | `void __thiscall(this, TGBufferStream*)` | Host-side: receives request, looks up ship, applies damage |
| 0x005AF5F0 | DoDamageToSelf | `float10(subsystem*)` | Core: applies lethal damage via PowerSubsystem. **1-arg, not 2-arg** — see Clar1 in NOTE block. |
| 0x005AF4A0 | DoDamageToSelf_Inner | `(ship*, subsystem*, float damageAmount, int* attacker, char force_kill)` | Core: actual damage application + death chain |
| 0x005AFEA0 | ShipDeathHandler | `(ship*, int* attacker_subsystem)` | Core: fires OBJECT_EXPLODING event after ship dies |
| 0x006A1AA0 | GetShipFromPlayerID | `__cdecl(int connID) -> ship*` | Utility: maps connection ID to ship pointer |
| 0x0056C310 | GetMaxHP | `__fastcall(subsystem*) -> float` | Reads `subsystem->property->maxCondition` (+0x18 -> +0x20) |
| 0x0056C330 | IsDead | `__fastcall(subsystem*) -> bool` | Checks subsystem death flag (+0x18 -> +0x24) |
| 0x0056C470 | SetCondition | `__thiscall(subsystem*, float newHP)` | Sets HP, clamps to max, fires SUBSYSTEM_HIT if damaged |

---

## Complete Flow Diagram [v5-validated 2026-05-28 — three execution paths]

### Single-Player Path

```
Player presses Ctrl+D
    |
    v
KeyboardBinding: WC_CTRL_D -> ET_INPUT_SELF_DESTRUCT (0x8001DD)
    |
    v
TopWindow::SelfDestructHandler (0x0050D070)
    |
    +-- Check: IsHost == 0 (false in SP host mode)
    |   +-- Check: IsMultiplayer == 0 (true -- skip network path)
    |       +-- Check: Clock+0x8C != 2 and != 3 (TestMenuState guard)
    |           +-- Get player ship via FUN_004069b0
    |           +-- Call FUN_005af5f0(ship, ship+0x2C4)  [PowerSubsystem]
    |
    v
DoDamageToSelf (0x005AF5F0)
    |
    v
Ship destruction via normal pipeline
```

### Multiplayer Path (Client -> Host -> All)

```
CLIENT SIDE:
============
Player presses Ctrl+D
    |
    v
KeyboardBinding: WC_CTRL_D -> ET_INPUT_SELF_DESTRUCT (0x8001DD)
    |
    v
TopWindow::SelfDestructHandler (0x0050D070)
    |
    +-- Check: IsHost != 0? NO (IsHost==0 for client)
    +-- Check: IsMultiplayer != 0? YES
    |
    v
    Create TGMessage (factory at 0x008958D0, size 0x40)
    Write single byte: 0x13 (opcode) to message buffer
    Send to host: TGNetwork::SendTGMessage(hostConnectionID, msg, 0)
    CallNextHandler(event) -- propagates event chain


HOST SIDE (on receiving opcode 0x13):  [v5-validated 2026-05-28 — HostMsgHandler reads sender + PowerSubsystem cascade]
=====================================
MpgameHandleMessage (0x0069F2A0)
    |
    +-- case 0x13:
    |
    v
HostMsgHandler (0x006A01B0)
    |
    +-- Check: g_IsMultiplayer != 0? YES   [see C3 — actual flag is 0x0097FA8A=IsHost]
    +-- Read sender connection ID from TGBufferStream field at offset 0x0C
    +-- GetShipFromPlayerID(connID) -> ship pointer
    +-- If ship != NULL:
    |       FUN_005af5f0( *(undefined4*)(ship + 0x2c4) )  [pass PowerSubsystem ptr; 1-arg per Clar1]
    |
    v
DoDamageToSelf (0x005AF5F0)
    |
    v
Ship destruction -> OBJECT_EXPLODING event -> scoring


ALL CLIENTS (via normal event forwarding):
==========================================
The ship's death is communicated via:
  1. StateUpdate 0x1C (HP drops to 0)
  2. Opcode 0x06 PythonEvent (OBJECT_EXPLODING, forwarded by HostEventHandler)
  3. Opcode 0x36 SCORE_CHANGE (death counted, no kill credit)
  4. Opcode 0x06 TGSubsystemEvent (ET_ADD_TO_REPAIR_LIST) for damaged subsystems
  Client returns to ship selection after explosion timer (9.5s) expires.
  NO opcode 0x14 DestroyObject is sent. NO server-initiated respawn.
  The client picks a new ship and sends ObjCreateTeam (0x03) to respawn.
```

---

## Wire Format: Opcode 0x13 (HostMsg) [v5-validated 2026-05-28 — 1-byte payload]

The HostMsg opcode is remarkably simple -- the **smallest possible game message**:

```
Offset  Size  Type    Field          Notes
------  ----  ----    -----          -----
0       1     u8      opcode         Always 0x13
```

Total size: **1 byte** (just the opcode). There is no payload.

The **sender's identity** is carried in the TGMessage envelope (the `+0x0C` field contains the sender's connection ID), not in the game-level payload. The host uses `GetShipFromPlayerID()` to map the connection ID to the ship object.

### Sender Code (from SelfDestructHandler disassembly at 0x0050D070) [v5-validated 2026-05-28]

[v5: TGMessage 0x40-byte alloc at 0x0050D0A1; opcode byte write at 0x0050D0CE; host connection ID via network+0x20 at 0x0050D0D8.]

```asm
; Create TGMessage (0x40 bytes)
push   0x0                       ; flags=0
push   0x8d858c                  ; factory string (TGMessage)
push   0x40                      ; size=64
mov    ecx, 0x99c478             ; allocator
call   FUN_00717b70              ; NiAlloc
mov    ecx, eax
call   FUN_00718010              ; construct
; ...
call   FUN_006b82a0              ; TGMessage ctor

; Write opcode byte
mov    BYTE PTR [esp+0x17], 0x13 ; opcode = 0x13
push   0x1                       ; size = 1 byte
push   eax                       ; pointer to byte
mov    ecx, esi                  ; TGMessage*
call   FUN_006b84d0              ; Buffer copy (allocate + memcpy)

; Send to host
mov    ecx, [edi+0x20]           ; host connection ID
push   0x0                       ; options
push   esi                       ; TGMessage*
push   ecx                       ; target ID
mov    ecx, edi                  ; TGNetwork*
call   FUN_006b4c10              ; SendTGMessage
```

---

## DoDamageToSelf (FUN_005AF5F0) -- Decompiled [v5-validated 2026-05-28 — 5 xrefs, 1-arg signature]

> **Clar1 (2026-05-28)**: Ghidra signature is **single-arg** `float10(int subsystem)`. The earlier 2-arg `__thiscall(ship*, powerSubsystem*)` rendering was wrong. Callers (e.g. `TopWindow__SelfDestructHandler` and `HostMsgHandler`) pass `ship+0x2C4` (the PowerSubsystem ptr) as the only arg. Ship is then recovered **inside DoDamageToSelf_Inner** via the subsystem→ship parent backref at `subsystem+0x40`. The semantics are unchanged — same data flows through — only the param count was wrong.

```c
float10 DoDamageToSelf(void *powerSubsystem)
{
    if (powerSubsystem == NULL)
        return 0.0f;  // DAT_00888b54 = 0.0

    float maxHP = GetMaxHP(powerSubsystem);  // FUN_0056c310
    // ship recovered inside _Inner via subsystem+0x40 parent backref
    // DoDamageToSelf_Inner(ship_from_backref, powerSubsystem, maxHP, NULL, 1)
    //   param: attacker=NULL, force_kill=1 (bypasses certain checks)
    return DoDamageToSelf_Inner(/* ship_via_backref */, powerSubsystem, maxHP, NULL, 1);
}
```

Key insight: Callers pass `ship+0x2C4` (the **PowerSubsystem** pointer). DoDamageToSelf reads the PowerSubsystem's max HP and applies that as damage -- effectively **one-shotting the reactor**. The `force_kill=1` flag (5th param of inner) ensures the damage goes through regardless of protection states. The NULL attacker flows through to ShipDeathHandler, which writes `event+0x28 = 0` — guaranteeing FiringPlayerID=0 on the resulting OBJECT_EXPLODING wire frame and therefore no kill credit.

---

## DoDamageToSelf_Inner (FUN_005AF4A0) -- Decompiled + Annotated

```c
float10 __thiscall DoDamageToSelf_Inner(
    void *ship,               // this = ship object
    void *subsystem,          // PowerSubsystem or target subsystem
    float damageAmount,       // amount of damage to apply (= maxHP for self-destruct)
    int  *attacker,           // NULL for self-destruct (no attacker)
    char  force_kill          // 1 = force through protections
)
{
    // Gate 1: Is this the player's own ship AND is the ship in god mode?
    void *playerShip = FUN_004069b0();  // Get current player's ship
    if (ship == playerShip && *(char*)(g_TopWindow + 0x60) != 0) {
        // Ship is in God Mode -- refuse damage
        return 0.0f;
    }

    // Gate 2: ship+0x2EA flag (damage enabled flag)
    if (*(char*)((int)ship + 0x2EA) == 0) {
        return 0.0f;  // Damage disabled on this ship
    }

    // Read current HP and max HP
    float currentHP = *(float*)((int)subsystem + 0x30);
    float maxHP = GetMaxHP(subsystem);
    float excessDamage = currentHP - damageAmount;

    float damageApplied = 0.0f;

    if (excessDamage <= 0.0f) {
        // Damage exceeds current HP -- subsystem will die
        damageApplied = -excessDamage;  // overshoot
    } else if (force_kill == 0) {
        goto skip_to_end;
    }

    // Check if ship should auto-self-destruct (ship+0x2E9 flag)
    // This handles cascade failure: if the power subsystem dies,
    // check if the ENTIRE ship should blow up
    if (*(char*)((int)ship + 0x2E9) == 1) {
        if (IsDead(subsystem)) {
            // Power subsystem is dead -- apply total maxHP as damage
            float totalMaxHP = GetMaxHP(subsystem);
            damageApplied = 0.0f;
            force_kill = 0;
            excessDamage = totalMaxHP * DAT_00888a78;  // scale factor
        }
    }

    // Check subsystem minimum HP threshold (+0x44 flag)
    if (*(char*)((int)subsystem + 0x44) == 1) {
        float minHPRatio = GetMinHPRatio(subsystem);  // FUN_0056b960
        if ((float)excessDamage / maxHP < minHPRatio) {
            // Below minimum threshold -- force to minimum
            float minHP = (minHPRatio + DAT_00888a78) * maxHP;
            damageApplied = 0.0f;
            excessDamage = minHP;
        }
    }

    // Apply the damage
    SetCondition(subsystem, excessDamage);  // FUN_0056c470

    // If subsystem is now dead (or force_kill), trigger death chain
    if ((excessDamage <= 0.0f || force_kill != 0) && IsDead(subsystem)) {
        ShipDeathHandler(ship, attacker);  // FUN_005afea0
    }

    return damageApplied;

skip_to_end:
    return damageApplied;
}
```

### Critical Detail: SetCondition (FUN_0056C470)

When `SetCondition` is called and the subsystem's HP drops below its max, it fires a **SUBSYSTEM_HIT** event (`0x0080006B` via TGCharEvent). This is the same event type used for weapon damage -- meaning self-destruct damage flows through the exact same notification pipeline as combat damage.

```c
// Inside SetCondition, when HP < maxHP:
TGCharEvent *event = new TGCharEvent();
event->source = NULL;
event->dest = subsystem->parentShip;  // ship+0x40
event->eventType = 0x0080006B;        // ET_SUBSYSTEM_HIT
event->charData = subsystem->objectID; // +0x04
PostEvent(g_EventManager, event);
```

---

## ShipDeathHandler (FUN_005AFEA0) -- What Happens After Death [v5-validated 2026-05-28]

After `DoDamageToSelf_Inner` applies lethal damage, `ShipDeathHandler` at `0x005AFEA0` fires. This function:

1. **Gate checks** [v5 C2]: `*(float*)(ship+0x14C) < DAT_008e5c18` where `DAT_008e5c18 = FLT_MAX (0x7F7FFFFF)`. This is a **dying-sentinel reentrancy guard**, NOT a "must be above threshold" damage check. Once a ship enters dying state, hullHP is overwritten to FLT_MAX as a sentinel flag — the gate means "ship is not yet sentinel-marked / still alive". Also gated on `ship+0x150` (already-dying flag) being clear. (Cross-anchor: protocol leaf #18 uses the same FLT_MAX sentinel pattern for DamageableObject HP slot.)
2. **Clears special state**: ship+0x244 = 0
3. **Plays death effects**: `FUN_005ae1b0(ship, 0)` -- explosion visuals/sounds
4. **Cleanup**: `FUN_005b0bb0` (ship state), `FUN_005af460` (subsystem shutdown), `FUN_005ac250` (AI removal)
5. **Creates OBJECT_EXPLODING event** (TGEvent, event type `0x0080004E`) [v5 Clar2]:
   - `event+0x10` = `0x0080004E` (event type)
   - `event+0x28` = attacker's ship ID (from subsystem→ship lookup via attacker_subsystem) OR **0 when attacker is NULL** (self-destruct path)
   - `event+0x2C` = `*(int*)(ship + 0x14C)` = hullHP (the "charData" payload)
   - Sender/source field is set via `FUN_006d62b0(ship)` (likely TGEvent_SetSource) — outside what is visible in the direct decompile
   - Posts to `g_EventManager`
6. **Wire-format authority**: the wire-format trace section below is authoritative on the over-the-wire layout. The prior doc's shorthand "dest = ship" was a hand-wavy in-memory description; the wire layer ends up with `dest = ship_objID` at the correct wire offset, but the in-memory event-field assignment doesn't have a `dest = ship` field as literally described.

The OBJECT_EXPLODING event then triggers:
- **Scoring** (Python `ObjectKilledHandler` in mission scripts)
- **Network forwarding** via HostEventHandler -> opcode 0x06 to "NoMe" group
- **Visual destruction** on all clients

### Multiplayer Event Flow After Death

In multiplayer (host side), the OBJECT_EXPLODING event is handled by the registered `HostEventHandler` (0x006A1150), which serializes it as opcode 0x06 (PythonEvent) and sends it to the "NoMe" network group (all peers except self). This is how all clients learn the ship has died.

For self-destruct specifically, the attacker pointer is **NULL** (passed as NULL from `DoDamageToSelf`), so:
- `FiringPlayerID` = 0 in the event
- The scoring system sees `iFiringPlayerID == 0` and awards no kill credit
- A death IS counted for the self-destructing player
- In Mission5 (team mode), self-destruct awards a kill to the **opposing team** (lines 797-809 of Mission5.py)

---

## DestroyObject Handler (Opcode 0x14, FUN_006a01e0) -- **Vestigial in MP** [v5-validated 2026-05-28]

> [!IMPORTANT]
> **C1 (MED) — This handler exists in stbc.exe but is NEVER invoked during MP ship death.**
>
> [`docs/networking/ship-death-lifecycle.md`](../networking/ship-death-lifecycle.md) (validated leaf #11 earlier this campaign) confirms `0/59` DestroyObject sends across the entire 33.5-min battle trace, across both self-destruct deaths AND combat kills. The prior version of this section claimed "After the explosion sequence completes, the host sends opcode 0x14 (DestroyObject) to remove the object from all clients" — that claim is **wrong**. The wire-format-spec, the stock-trace analysis, and the prior version of this very doc's own "Verified Stock Trace Data" section (`NOT sent: opcode 0x14 (DestroyObject) — zero across both self-destruct and combat kills`) all agree: 0x14 is not part of ship death.
>
> The handler at `FUN_006A01E0` is preserved here **for reference only** — to document what the dead-code handler WOULD do if it ever ran. OpenBC implementers should NOT send opcode 0x14 on ship death. Use the OBJECT_EXPLODING (opcode 0x06, factory 0x8129) + scoring (opcode 0x36) + repair-list events sequence instead. See [`docs/networking/ship-death-lifecycle.md`](../networking/ship-death-lifecycle.md) for the correct sequence.

### Reference: dead-handler body at FUN_006A01E0

```c
void Handler_DestroyObject_0x14(void *param_1)
{
    // Read object data from stream
    int streamResult = FUN_006b8530(param_1, &param_1);

    // Create TGObjectList for multi-object cleanup
    TGObjectList list;
    FUN_006cefe0(&list);
    FUN_006cf180(&list, streamResult + 1, (int)param_1 - 1);

    int objectID = FUN_006cf6a0(&list);
    int *objectPtr = FUN_00434e00(NULL, objectID);  // Look up object by ID

    if (objectPtr != NULL) {
        if (objectPtr[8] == NULL) {
            // No parent set -- direct cleanup
            int *subsysPtr = FUN_0059fd30(objectPtr);  // Get subsystem
            if (subsysPtr != NULL) {
                // Call vtable+0x138: subsystem teardown
                (*(code **)(*(int*)subsysPtr + 0x138))(1, 0);
            }
            // Call vtable+0x00: destructor
            (*(code **)*objectPtr)(1);
        } else {
            // Has parent set -- remove from set
            // vtable+0x5C: RemoveFromSet
            (*(code **)(*(int*)objectPtr[8] + 0x5C))(objectID);
        }
    }

    // Cleanup list
    FUN_006cf120(&list);
}
```

---

## All Callers of DoDamageToSelf (FUN_005af5f0) [v5-validated 2026-05-28 — 5 xrefs confirmed]

There are **5 call sites** for `FUN_005af5f0`, revealing all paths that can trigger the self-destruct damage:

| Call Site | Context | When |
|-----------|---------|------|
| 0x0050D132 | `TopWindow__SelfDestructHandler` | Player presses Ctrl+D (local path: SP or MP-host) |
| 0x006A01D3 | `HostMsgHandler` (opcode 0x13) | Host receives self-destruct request from client |
| 0x005AFD56 | Ship damage handler (bare code, suspected cascade damage) | Part of cascading damage / shield failure path — see OQ1 |
| 0x006A0E18 | MultiplayerGame player slot reset (bare code) | Ship destruction during player slot cleanup/respawn — see OQ1 |
| 0x005B355B | Ship linked-list iteration (bare code) | Loop iterating subsystems, applying damage (cascade?) — see OQ1 |

The first two are the self-destruct initiation paths. The last three are internal engine uses where the same "apply lethal damage via PowerSubsystem" primitive is reused. Call-site addresses confirmed via xref enumeration; semantic context labels for the last three are inferred from caller plate comments and have not been verified by promoting those bare-code sites to functions (see OQ1).

---

## TopWindow__SelfDestructHandler (0x0050D070) -- Full Reconstruction [v5-validated 2026-05-28]

> **Function CREATED this pass.** Prior to this v5 validation, the body at `0x0050D070` was bare code in Ghidra — no function existed. The archaeology pass created `TopWindow__SelfDestructHandler` (body size 0x0DB = 219 bytes, ending 0x0050D14B). The reconstruction below is verified against the live disassembly.
>
> **Flag-name caveat**: the variables `g_IsHost` / `g_IsMultiplayer` shown below correspond to the **CURRENT CLAUDE.md labels** at 0x0097FA89 and 0x0097FA8A. Per C3 in the NOTE block at top of doc, those labels are inverted — actual semantics are `0x0097FA89 = GameLive_MP`, `0x0097FA8A = IsHost`. The control-flow logic shown is correct against the binary; only the per-flag names are wrong pending the CLAUDE.md sweep.

Based on the disassembly, here is the complete handler logic:

```c
void __thiscall TopWindow_SelfDestructHandler(void *this, void *pEvent)
{
    // Path 1: Host in multiplayer
    if (g_IsHost != 0) {
        if (g_IsMultiplayer != 0) {
            // Host in MP -- apply damage directly to own ship
            void *playerShip = FUN_004069b0();  // Get player's ship
            if (playerShip != NULL) {
                void *powerSS = *(void**)((int)playerShip + 0x2C4);
                FUN_005af5f0(playerShip, powerSS);  // DoDamageToSelf
            }
        }
        // else: Host in SP mode -- fall through to SP path
    }

    // Path 2: Not host (client) AND multiplayer
    else if (g_IsMultiplayer != 0) {
        // NETWORK PATH: Send opcode 0x13 to host
        TGNetwork *network = g_TGWinsockNetwork;  // 0x97fa78
        if (network != NULL) {
            TGMessage *msg = AllocAndConstruct_TGMessage(0x40);
            byte opcode = 0x13;
            BufferCopy(msg, &opcode, 1);  // Write 1 byte: opcode 0x13

            int hostID = *(int*)(network + 0x20);  // Host connection ID
            TGNetwork_SendTGMessage(network, hostID, msg, 0);
        }

        // CallNextHandler
        CallNextHandler(this, pEvent);
        return;
    }

    // Path 3: Single-player (IsHost==0, IsMp==0)
    else {
        // Check TestMenuState != 2 and != 3 (guard against certain game states)
        int clock = *(int*)0x9a09d0;
        int menuState = *(int*)(clock + 0x8C);
        if (menuState == 2 || menuState == 3) {
            // In menu state 2 or 3 -- don't allow self-destruct
            goto end;
        }

        // Apply damage locally
        void *playerShip = FUN_004069b0();
        if (playerShip != NULL) {
            void *powerSS = *(void**)((int)playerShip + 0x2C4);
            FUN_005af5f0(playerShip, powerSS);
        }
    }

end:
    // CallNextHandler
    CallNextHandler(this, pEvent);
}
```

### Three Execution Paths

1. **Single-player** (IsHost=0, IsMp=0): Direct local damage via PowerSubsystem. Gated by TestMenuState != 2/3.
2. **Multiplayer host** (IsHost=1, IsMp=1): Direct local damage (host is authoritative, no need to send to self).
3. **Multiplayer client** (IsHost=0, IsMp=1): Sends 1-byte network message (opcode 0x13) to host. Host applies damage on next receive.

---

## AI Self-Destruct (PlainAI/SelfDestruct.py)

A separate, parallel implementation exists for AI-controlled ships. The `SelfDestruct` AI module at `reference/scripts/AI/PlainAI/SelfDestruct.py` uses a completely different mechanism:

```python
class SelfDestruct(BaseAI.BaseAI):
    def Update(self):
        pObject = self.pCodeAI.GetObject()
        pShip = App.ShipClass_Cast(pObject)
        if pShip:
            pHull = pShip.GetHull()
            if pHull:
                pShip.DestroySystem(pHull)  # 100% damage to hull
                bDead = 1
        if not bDead:
            pObject.SetDeleteMe(1)  # Fallback: just delete
```

This uses `pShip.DestroySystem(hull)` rather than the PowerSubsystem path. It is used in campaign missions:
- **E3M4** (Maelstrom Episode 3 Mission 4): `E3M4SelfDestructAI.py` -- T'Awsun ship self-destructs
- **E3M2**: `ProbeDestructAI.py` -- probe self-destructs
- **E4M5/E4M6**: `DestructAI.py` -- ships self-destruct

---

## Python PlayerSelfDestruct (COMMENTED OUT)

`TacticalInterfaceHandlers.py` line 97-123 contains a **commented-out** Python handler:

```python
#def PlayerSelfDestruct(pObject, pEvent):
#   pShip = MissionLib.GetPlayer()
#   if (pShip):
#       pShip.DamageSystem(pShip.GetHull(), pShip.GetHull().GetMaxCondition())
#
#   pObject.CallNextHandler(pEvent)
```

This was an earlier prototype that applied hull damage directly. It was superseded by the C++ `TopWindow::SelfDestructHandler` which uses the PowerSubsystem path instead. The key differences:
- Python version: `DamageSystem(hull, maxCondition)` -- damages hull directly
- C++ version: `DoDamageToSelf(ship, powerSubsystem)` -- destroys the reactor, which cascades

The C++ version is more thorough because destroying the PowerSubsystem triggers cascade failure of all powered subsystems.

---

## Event Registration [v5-validated 2026-05-28]

The SelfDestructHandler is registered in two complementary calls:

**Event-type registration (FUN_0050CA50):**

```c
FUN_006d92b0(&DAT_00987878, 0x8001DD, "TopWindow::SelfDestructHandler");
```

**Name→code binding (FUN_0050C8B0):**

```c
FUN_006da130(&LAB_0050D070, "TopWindow::SelfDestructHandler");
```

Where:
- `0x00987878` = TopWindow event handler table
- `0x8001DD` = ET_INPUT_SELF_DESTRUCT event type
- `0x0050D070` = `TopWindow__SelfDestructHandler` (created this pass)

Keyboard binding (all language variants):
```python
App.g_kKeyboardBinding.BindKey(App.WC_CTRL_D, App.TGKeyboardEvent.KS_KEYDOWN,
                                App.ET_INPUT_SELF_DESTRUCT, 0, 0)
```

---

## Scoring Implications

When a ship self-destructs in multiplayer:

1. `FiringPlayerID` = 0 (no attacker, since attacker is NULL)
2. **No kill credit** awarded to any player (the `iFiringPlayerID != 0` check in scoring handlers)
3. **Death IS counted** for the self-destructing player (deaths always counted for `iKilledPlayerID`)
4. **In team mode** (Mission5): If the self-destructing player is an Attacker (team 0), a kill is awarded to the Defending team (team 1) -- see Mission5.py lines 797-809:
   ```python
   else:
       # Self destruct?  Collision?  Still award a team kill
       if (g_kTeamDictionary.has_key(iKilledPlayerID)):
           iKilledTeam = g_kTeamDictionary[iKilledPlayerID]
           if (iKilledTeam == 0):  # Attacking team died
               # award a kill to the defending team
               iTeamKills = g_kTeamKillsDictionary.get(1, 0) + 1
               g_kTeamKillsDictionary[1] = iTeamKills
   ```

---

## Summary: Self-Destruct Pipeline

```
Ctrl+D
  -> ET_INPUT_SELF_DESTRUCT (0x8001DD)
    -> TopWindow::SelfDestructHandler (0x0050D070)
      -> [if client] Send opcode 0x13 to host
      -> [if host/SP] DoDamageToSelf(ship, ship+0x2C4)
        -> DoDamageToSelf_Inner(ship, powerSS, maxHP, NULL, force=1)
          -> SetCondition(powerSS, 0)
            -> ET_SUBSYSTEM_HIT (0x0080006B) event
          -> ShipDeathHandler (0x005AFEA0)
            -> ET_OBJECT_EXPLODING (0x0080004E) event
              -> [MP] HostEventHandler -> opcode 0x06 -> "NoMe" group
              -> [MP] Python ObjectKilledHandler -> SCORE_CHANGE_MESSAGE
              -> [all] Explosion visuals/sounds (9.5s animation)
            -> Client returns to spawn menu after explosion timer
            -> Client sends ObjCreateTeam (0x03) to respawn
            (NO DestroyObject 0x14, NO server-initiated respawn)
```

Total latency in MP: ~1 network round-trip (client sends 0x13, host processes, state updates propagate on next tick).

---

## Verified Stock Trace Data (2026-02-21)

Validated against packet traces from stock dedicated server (instrumented with proxy DLL).

### ObjectExplodingEvent Field Values

| Field | Value | Notes |
|-------|-------|-------|
| factory_id | 0x8129 | ObjectExplodingEvent |
| event_type | 0x0080004E | ET_OBJECT_EXPLODING |
| source | 0x00000000 (NULL) | No attacker for self-destruct |
| dest | 0x3FFFFFFF (ship objID) | The dying ship |
| firing_player | 0 | No kill credit awarded |
| lifetime | 9.5f | Client plays 9.5-second explosion animation |

### Complete Opcode Sequence

```
T+0.000  C->S  0x13 HostMsg (self-destruct request, 1 byte, unreliable)
T+0.004  S->C  0x06 ObjectExplodingEvent (factory 0x8129, lifetime=9.5s)
T+0.004  S->C  0x36 SCORE_CHANGE (deaths+1, kills=0)
T+0.004  S->C  4x 0x06 TGSubsystemEvent (ET_ADD_TO_REPAIR_LIST)
                PowerReactor, ShieldGenerator, PhaserController, PulseWeapon
         --- 9.5 seconds: explosion animation plays, StateUpdates continue ---
         --- 15 debris collision events during explosion (600.0 dmg, all HP=0) ---
T+9.498  S->C  2x 0x06 TGSubsystemEvent (debris damage to EPS, Repair)
         --- client returns to spawn menu ---
```

### Key Findings

- **4ms latency** from HostMsg (0x13) to server response (ObjectExplodingEvent + SCORE_CHANGE)
- **9.5 seconds** explosion animation (controlled by ObjectExplodingEvent lifetime field)
- **StateUpdates continue** both directions during the explosion — the ship exists as wreckage
- **NOT sent**: opcode 0x29 (Explosion) — this IS sent for combat kills (59/59 in battle trace) but NOT for self-destruct
- **NOT sent**: opcode 0x14 (DestroyObject) — zero across both self-destruct and combat kills (0/59 in battle trace)
- **NOT sent**: opcode 0x03 (server-initiated respawn) — the client returns to the spawn menu and initiates respawn by sending ObjCreateTeam when the player picks a new ship
- **Self-destruct vs combat kill**: Combat kills use 0x29 (Explosion) + server-initiated 0x03 (ObjCreateTeam respawn). Self-destruct uses only ObjectExplodingEvent (0x06) with no 0x29 and no auto-respawn.

---

## Stock vs OpenBC: Self-Destruct Trace Comparison

### Pre-PR#34 (2026-02-21): 5 Anomalies

Side-by-side comparison from instrumented packet traces: stock dedicated server vs OpenBC
server (pre-PR#34), both running the same client.

| # | Anomaly | Severity | Description |
|---|---------|----------|-------------|
| 1 | ObjectExplodingEvent wrong fields | HIGH | source/dest swapped, lifetime=1.0 instead of 9.5 |
| 2 | DestroyObject (0x14) sent | HIGH | Ship removed before explosion animation |
| 3 | Server auto-respawn | HIGH | Server sends ObjCreateTeam, bypassing ship selection |
| 4 | Wrong owner_slot/team in respawn | MEDIUM | owner_slot=0 (host) instead of client's slot |
| 5 | MissionInit totalSlots=1 | LOW | Should be maxplayers+1 |

### Post-PR#34 (2026-02-21): All 5 Fixed

All 5 anomalies were resolved by OpenBC PR #34 (issue #33). Verified by re-testing
with the same procedure (connect, spawn, self-destruct, observe) across 6 deaths
(1 collision kill + 5 self-destructs), 3 ship types (Sovereign, Galaxy, Warbird).

| # | Anomaly | Status | Evidence |
|---|---------|--------|----------|
| 1 | ObjectExplodingEvent wrong fields | **FIXED** | All 6 events: source=0, dest=ship_objID, lifetime=9.5f |
| 2 | DestroyObject (0x14) sent | **FIXED** | Zero 0x14 during any death |
| 3 | Server auto-respawn after self-destruct | **FIXED** | Zero server-initiated ObjCreateTeam after any self-destruct |
| 4 | Wrong owner_slot/team in respawn | **FIXED** | Moot — no auto-respawn occurs |
| 5 | MissionInit totalSlots=1 | **FIXED** | Now 7 (maxplayers=6+1), was 1 |

Post-fix ObjectExplodingEvent wire format matches stock exactly:
```
Stock:   06 29 81 00 00 4E 00 80 00 00 00 00 00 FF FF FF 3F 00 00 00 00 00 00 18 41
OpenBC:  06 29 81 00 00 4E 00 80 00 00 00 00 00 XX XX XX XX 00 00 00 00 00 00 18 41
         |  |factory 8129|event 0x4E  |source=0   |dest=ship  |killer=0   |life=9.5|
```

### Post-fix Self-Destruct Sequence

```
T+0.000  C->S  0x13 HostMsg
T+0.015  S->C  25x TGSubsystemEvent + ObjectExplodingEvent + SCORE_CHANGE
         --- client returns to spawn menu, picks new ship ---
         --- client sends ObjCreateTeam when ready ---
```

Response latency: stock=4ms, OpenBC=15-32ms (1-2 ticks). Both acceptable.

### Remaining Issues (post-PR#34)

Two issues remain after PR #34, tracked in OpenBC issue #38:

1. **Combat death auto-respawn** (HIGH): PR #34 fixed self-destruct (respawn_timer=0.0f),
   but all 4 combat death paths still set respawn_timer=5.0f. Stock BC NEVER auto-respawns
   for ANY death type — all respawns are client-initiated. See
   [../networking/ship-death-lifecycle.md](../networking/ship-death-lifecycle.md).

2. **Excess TGSubsystemEvents** (MEDIUM): OpenBC sends 18-25 repair events per death
   (one per subsystem), stock sends 6 (primary subsystems only). Overflows the reliable
   retransmit queue (16 entries), causing 52 warnings per session.

### Key Correction: Stock Never Auto-Respawns

The earlier version of this document stated that combat kills use server-initiated
ObjCreateTeam (0x03) respawn. **This was incorrect.** Further analysis of the battle
trace confirmed that ALL 62 ObjCreateTeam messages are client-initiated relays through
the server's star topology, not server-originated spawns. Stock BC does not auto-respawn
for any death type (combat or self-destruct). See
[../networking/ship-death-lifecycle.md](../networking/ship-death-lifecycle.md) for details.

---

## Appendix: Related Event Types

| Event Type | Name | Role in Self-Destruct |
|------------|------|----------------------|
| 0x8001DD | ET_INPUT_SELF_DESTRUCT | Input trigger (keyboard) |
| 0x0080006B | ET_SUBSYSTEM_HIT | Fired when PowerSubsystem HP changes |
| 0x0080004E | ET_OBJECT_EXPLODING | Fired when ship dies (triggers scoring + visuals) |
| 0x00800050 | ET_COLLISION_EFFECT | NOT involved in self-destruct |
| 0x008000DF | ET_ADD_TO_REPAIR_LIST | NOT involved (damage is instant-lethal) |

---

## Open Questions [v5-validated 2026-05-28]

**OQ1 — Unpromoted bare-code call sites for FUN_005AF5F0.**
Three of the five xrefs (`0x005AFD56`, `0x006A0E18`, `0x005B355B`) point at bare code that has not been promoted to a function in Ghidra. The "Ship damage handler", "MultiplayerGame player slot reset", and "Ship linked-list iteration" context labels in the [All Callers](#all-callers-of-dodamagetoself-fun_005af5f0-v5-validated-2026-05-28--5-xrefs-confirmed) table are **inferred from caller plate comments** and have not been verified by re-decompilation. Promoting these three sites to functions and re-decompiling would either confirm or falsify the labels. Out of scope for this self-destruct validation; flagged for a future damage-cascade pass.

**OQ2 — Is `event+0x28 = 0` for self-destruct really enforced?**
The asm path for self-destruct (`param_2 = NULL` passed to ShipDeathHandler) hits the `else { ... iVar2+0x28 = 0; ... }` branch at LAB_005B0042. **Trace data corroborates**: 6/6 self-destructs in PR#34 testing had `firing_player=0`. However, the deduction chain from `param_2 == NULL` to `iVar2+0x28 = 0` is non-trivial — if the `param_2 != NULL` branch were ever taken with a stale-but-non-NULL attacker pointer, weapon-attacker fields could leak in. Worth a focused dataflow trace at some future point.

**OQ3 — Mission5 team-kill awarding to opposing team.**
The doc cites `reference/scripts/Mission/Mission5.py` lines 797-809 ("Self destruct? Collision? Still award a team kill"). This Python-source claim was NOT verified against the script during this v5 pass — the Python source is checked in and the claim is likely true (mission scripts are public and self-explanatory), but flagged for completeness. Verifying would mean reading `reference/scripts/Mission/Mission5.py:797-809` and confirming the team-kill branch fires for `firing_player=0` deaths.
