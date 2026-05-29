---
name: cascade-verification-flags-20260528
description: Cascade verification for 0x0097FA88/89/8A flag semantics. CASCADE CONFIRMED — CLAUDE.md "Key Globals" table is INVERTED. Self-destruct memo is correct. 28 docs need propagation.
metadata:
  type: project
---

# Cascade Verification: 0x0097FA88 / 0x0097FA89 / 0x0097FA8A

**Date:** 2026-05-28
**Verdict:** **CASCADE CONFIRMED** — CLAUDE.md is wrong; self-destruct-pipeline memo is correct.
**Trigger:** self-destruct-pipeline validation flagged inverted attributions; orchestrator requested independent binary verification.

## TL;DR — Corrected Flag Table

| Address | Symbol | Semantic | Host (with player) | Dedicated Server | Client | Single Player |
|---------|--------|----------|--------------------|------------------|--------|---------------|
| **0x0097FA88** | **HasLocalPlayer** (IsLocalPlayer) | 1 = there is a local player ship; 0 = no local player (dedicated only) | **1** | **0** | **1** | **1** |
| **0x0097FA89** | **GameLive** (IsMultiplayerLive) | 1 = MP game is running; 0 = menu/single-player | **1** | **1** | **1** | **0** |
| **0x0097FA8A** | **IsHost** | 1 = host (with-player OR dedicated); 0 = client | **1** | **1** | **0** | **1** (SP defaults to host) |

The fourth byte 0x0097FA8B (referenced in some docs as "isProcessingPackets") is a SEPARATE flag, untouched by this cascade.

## Verification Procedure (Phase 5)

### 1. MultiplayerGame_Ctor at 0x0069E590 — the smoking-gun decompile

End-of-ctor sequence (verified via `decompile_function` and `get_assembly_context`):

```c
// Host-only block (groups NoMe/Forward, ChecksumComplete/EnterSet handlers):
if (DAT_0097fa8a != '\0') {           // gates HOST-only handler registrations
    DAT_008e5f59 = DAT_008e5f58;
    if (DAT_0097fa78 != 0) {           // network exists
        // Create "NoMe" group (vtable PTR_FUN_00894684)
        // Create "Forward" group
        // Register on TGNetwork's group table [pNetwork+0xF4]
    }
    // Register HOST-only handlers:
    FUN_006db380(AddToRepairList, ...);
    FUN_006db380(0x800074, 0x800075, ...);
    FUN_006db380(0x008000e8, SystemChecksumP, ...);
    FUN_006db380(0x008000e7, SystemChecksumF, ...);
    FUN_006db380(0x008000e6, ChecksumCompleteHandler, ...);
    FUN_006db380(0x0080005d, EnterSetHandler, ...);
    FUN_006db380(0x008000c5, ExitedWarpHandler, ...);
}
// ... always-on handlers (Explosion, NewPlayerInGame, StartFiring, etc.) ...

if (DAT_0097fa8a == '\0') {            // CLIENT-only handler
    FUN_006db380(0x00800058, ChangedTargetHandler, ...);
}

FUN_0069efc0();

if ((DAT_0097fa8a != '\0') && (DAT_0097fa88 != '\0')) {  // HOST + has-local-player
    // Allocate TGMessageEvent (0x2C), post initial NewPlayerInGame for self
    // *(param_1 + 0x1e) = 1   // mark "we have joined"
    // param_1[0x1f] = pNetwork->localPlayerID
}

// Game-live transition (UNCONDITIONAL — both host and client):
DAT_0097fa89 = 0;                      // drain pending events
while (0 < DAT_0097fa3c) FUN_0043bbd0(0);
DAT_0097fa89 = 1;                      // game is now LIVE

if (DAT_0097fa8a != '\0') {            // HOST-only: copy friendly-fire setting
    *(iVar4 + 0xb4) = DAT_0097faa2;
}
```

**Write-site addresses confirmed via `get_assembly_context`:**
- `0x0069EB17`: `MOV byte ptr [0x0097fa89], 0x0` (clear before drain)
- `0x0069EB3A`: `MOV byte ptr [0x0097fa89], 0x1` (mark game-live)
- Both UNCONDITIONAL — runs on host AND client at end of MultiplayerGame_Ctor.

### 2. FUN_00405c10 (parent ctor / SP startup) — single-player default

```c
if (DAT_0097fa78 == 0) {        // no TGWinsockNetwork → single-player
    DAT_0097fa88 = 1;            // HAS local player
    DAT_0097fa8a = 1;            // IS host
    DAT_0097fa89 = 0;            // NOT live MP
    // ... installs scene-graph children ...
}
DAT_0097e238 = param_1;           // PlayWindow ptr (corrected name)
```

This SP init disproves CLAUDE.md instantly:
- If 0x0097FA88 were "IsClient", you'd never set it to 1 when there's no network. SP isn't client.
- 0x0097FA88=1 means "local player exists" (SP = local human player exists).
- 0x0097FA8A=1 means "act as host" (SP = local player is authority).
- 0x0097FA89=0 means "not in live MP" (SP is not MP-live).

### 3. MultiplayerGame_Start / GoLive at 0x00438CC0-0x00438D77 — the multiplayer init switch

Disassembled directly (`disassemble_bytes 0x00438C80-0x00438DD0`). With EBX=0 throughout:

```asm
00438d1b: CMP   ESI, EBX                    ; ESI mode parameter == 0 ?
00438d1d: JNZ   0x00438d57                  ; if non-zero, take host branch
; Branch A: ESI == 0 → CLIENT join
00438d1f: MOV   byte [0x0097fa89], 1        ; gameLive = 1
00438d26: MOV   byte [0x0097fa88], 1        ; hasLocalPlayer = 1
00438d2d: MOV   byte [0x0097fa8a], BL       ; isHost = 0   (BL = 0)
00438d33: JMP   0x00438d77

; Branch B: ESI != 0 → HOST
00438d57: CMP   ESI, 1                      ; ESI == 1 ?
00438d5a: MOV   byte [0x0097fa89], 1        ; gameLive = 1
00438d61: MOV   byte [0x0097fa88], 1        ; hasLocalPlayer = 1 (default)
00438d68: JZ    0x00438d70                  ; if ESI == 1, keep hasLocalPlayer=1
00438d6a: MOV   byte [0x0097fa88], BL       ; else (ESI > 1), hasLocalPlayer = 0 (dedicated)
00438d70: MOV   byte [0x0097fa8a], 1        ; isHost = 1
00438d77: ...
```

**Maps modes to flags** (the canonical ground truth):
- **ESI=0 (Client)**: gameLive=1, hasLocalPlayer=1, isHost=0
- **ESI=1 (Host with local player)**: gameLive=1, hasLocalPlayer=1, isHost=1
- **ESI>1 (Dedicated server)**: gameLive=1, hasLocalPlayer=0, isHost=1

This is the **DEFINITIVE** assignment of semantics. No interpretation needed.

### 4. TopWindow__SelfDestructHandler at 0x0050D070 — independent confirmation

```c
if (DAT_0097fa89 == '\0') {                  // OUTER: SP path (game NOT live)
    // ... local self-destruct via FUN_005af5f0
} else {                                      // OUTER: MP live
    if (DAT_0097fa8a == '\0') {              // INNER: CLIENT path
        // Build 1-byte msg [0x13], send to host via TGWinsockNetwork::SendTGMessage
        return;
    }
    // INNER ELSE: HOST path — local self-destruct
}
```

Self-destruct sends opcode 0x13 (HostMsg) **from client to host**. The "send-to-host" branch is gated by `DAT_0097fa8a == 0`, so **0x0097FA8A == 0 → CLIENT**. Matches the ground truth.

### 5. FUN_00504890 (MultiplayerWindow setup) — independent confirmation

```c
if (DAT_0097fa8a == '\0') {                  // CLIENT branch
    // ... uses Direct_Join_Address / Player_Name ...
} else {                                      // HOST branch
    // ... reads Game_Name ...
    if (DAT_0097fa88 != '\0') goto LAB_00504aa0;  // HOST WITH player → Player_Name
    FUN_006f4cc0("Dedicated Server0123");          // HOST without player → default name
}
```

UI prompts the host for a Player_Name only when `0x0097FA88 != 0` (has-local-player). On a dedicated server, default name is forced. Confirms 0x0097FA88 = HasLocalPlayer.

### 6. NewPlayerInGameHandler at 0x006A1E70 — host-only join handler

```c
if ((DAT_0097fa78 != 0) && (DAT_0097fa8a != '\0')) {   // network exists AND host
    // process new player, add to NoMe/Forward groups, walk scene-graph for state catch-up
}
```

Confirmed: only the HOST processes NewPlayerInGame messages and populates its forwarding groups. Gate `DAT_0097fa8a != 0` → HOST. Matches.

### 7. FUN_00565900 (host-only AddToRepairList post)

```c
if ((cVar1 != '\0') && (DAT_0097fa89 != '\0') && (DAT_0097fa8a != '\0')) {
    // post AddToRepairList event to event manager
}
```

Triple-gated: a repair condition met AND game-is-live AND we-are-host. Only the host emits AddToRepairList events. Matches the ground truth.

### 8. Ship__WriteStateUpdate at 0x005B17F0 — the plate IS PARTIALLY WRONG

The function plate (from a prior session) contains a mis-labeling:

> ```c
> bIsSinglePlayer = !DAT_0097fa8a (IsMultiplayer)
> ...
> if (!DAT_0097fa88) {  // we are HOST
>     if (FUN_006a2650() >= 2) skip
> } else {              // we are CLIENT
>     if (FUN_006a2650() >= 3) skip
> }
> ```

**Errors in the plate:**
- `DAT_0097fa8a` labeled "IsMultiplayer" → SHOULD BE "IsHost" (its 0 means client OR SP; its 1 means host OR SP-host). The "is-multiplayer" semantic is on `DAT_0097fa89` (game-live).
- The fa88 sub-branch labels "host" vs "client" are wrong. We are ALREADY in the host path (the gate is inside `!bIsSinglePlayer` and `DAT_0097faa2 != 0`, plus this is encoder logic running on the host's view). The fa88 sub-branch actually selects **HasLocalPlayer**: `fa88==0` (dedicated server, no local ship) skips earlier; `fa88!=0` (host-with-player, has its own ship) skips later.

The behavioral result still matches the packet-trace observation (`C->S 0x80, S->C 0x20`), so the encoder logic is unchanged — but the SEMANTIC LABELS in the plate need correction.

### 9. Collision rate-limit FUN_005A22A0 — clean four-way split

```c
if (DAT_0097fa8a == '\0') {              // CLIENT path
    // ... iVar10 thresholds 3, 4 ...
} else if (DAT_0097faa2 == '\0') {       // HOST, ff=off
    // ...
} else if (DAT_0097fa88 == '\0') {       // HOST, ff=on, DEDICATED (no local player)
    // ...
} else {                                 // HOST, ff=on, with-local-player
    // ...
}
```

Now perfectly readable:
- 0x0097FA8A == 0 → CLIENT
- 0x0097FA8A != 0 + 0x0097FAA2 == 0 → HOST with friendly-fire off
- 0x0097FA8A != 0 + 0x0097FAA2 != 0 + 0x0097FA88 == 0 → DEDICATED HOST
- 0x0097FA8A != 0 + 0x0097FAA2 != 0 + 0x0097FA88 != 0 → HOST-WITH-PLAYER

### 10. FUN_005AE090 (ship+0x2E9 setter) — confirms gameLive semantics

```c
if ((DAT_0097fa89 == '\0') || (DAT_0097fa8a != '\0')) {   // NOT-live MP OR we-are-host
    *(undefined1 *)(param_1 + 0x2e9) = param_2;          // write ship state
    // ...
}
```

The write is allowed when NOT in live multiplayer (== SP) OR when we are the authoritative host. This pattern (client-of-live-MP-cannot-write) confirms 0x0097FA89 = gameLive AND 0x0097FA8A = isHost.

### 11. IsLocalPlayerShip at 0x005AE140 — confirms gameLive gate

```c
bool IsLocalPlayerShip(int param_1) {
    if (DAT_0097fa89 != '\0') {                  // MP-live: use ship+0x2e4 owner flag
        return *(int *)(param_1 + 0x2e4) != 0;
    }
    // SP: compare against active scene
    int iVar1 = FUN_004069b0();                   // PlayWindow.activeShip
    return iVar1 == param_1;
}
```

The fa89 gate switches between two implementations: SP uses scene-graph compare, MP uses a per-ship owner-tag (set by the engine when a player takes control). Matches gameLive semantics.

## What CLAUDE.md Has Wrong

```
| 0x0097FA88 | IsClient (BYTE) - 0=host, 1=client |        ← WRONG; should be HasLocalPlayer (0=dedicated, 1=has-local-player)
| 0x0097FA89 | IsHost (BYTE) - 1=host, 0=client |          ← WRONG; should be GameLive (1=MP running, 0=menu/SP)
| 0x0097FA8A | IsMultiplayer (BYTE) |                       ← WRONG; should be IsHost (1=host, 0=client)
```

The mistake appears to be a **cyclic permutation** of three flag identities:
- Real IsHost (FA8A) was called IsMultiplayer
- Real GameLive (FA89) was called IsHost
- Real HasLocalPlayer (FA88) was called IsClient (with inverted polarity)

## Cross-Doc Impact (28 affected docs)

`grep` for `0x0097fa88|89|8a` in `docs/` returned matches across the following families:

### 0x0097FA89 (was-called-IsHost, actually GameLive) — 21 files
- `docs/gameplay/`: combat-mechanics-re, collision-detection-system, collision-rate-limiting, damage-system, repair-event-object-ids, repair-system, repair-tractor-analysis, self-destruct-pipeline, weapon-firing-mechanics, power-system, v5-validation-status
- `docs/protocol/`: wire-format-spec, objnotfound-requestobj-enterset-wire-format, collision-effect-protocol, pythonevent-wire-format, tgobjptrevent-class, v5-validation-status
- `docs/architecture/`: dedicated-server, architecture-overview
- `docs/guides/`: reading-decompiled-code
- `docs/analysis/`: server-side-computation-model

**Cascade impact**: Every "DAT_0097fa89 = IsHost gate" claim is actually a "**game-NOT-live**" (SP) gate. The damage-system, shield-system, and collision-rate-limiting gate descriptions all need re-interpretation:
- `(DAT_008e5c1c != 0) && (DAT_0097fa89 == 0)` → "trigger event setup AND game-is-NOT-live" (NOT "is-host"!) — this is a SINGLE-PLAYER gate
- These gates produce SP-only behaviors, not host-only behaviors

### 0x0097FA88 (was-called-IsClient, actually HasLocalPlayer) — 11 files
- `docs/gameplay/`: objcreate-unknown-species-analysis, self-destruct-pipeline, v5-validation-status
- `docs/protocol/`: wire-format-spec, stateupdate, v5-validation-status
- `docs/engine/`: function-map, v5-validation-status
- `docs/architecture/`: dedicated-server, architecture-overview
- `docs/guides/`: reading-decompiled-code

**Cascade impact**: Doc text like "host=0/client=1" must be replaced. The StateUpdate plate's "we are HOST/we are CLIENT" sub-branch labels are wrong (it's HasLocalPlayer, both branches are within the host path).

### 0x0097FA8A (was-called-IsMultiplayer, actually IsHost) — 28 files
- All families above + networking/ (ship-death-lifecycle, multiplayer-flow, tgmessage-routing-cleanroom, alby-rules-cipher-analysis)
- protocol/ (subsystem-integrity-hash, set-phaser-level, python-messages, stateupdate, tgmessage-routing, etc.)
- analysis/empty-stateupdate-root-cause, guides/lessons-learned

**Cascade impact**: Every "is-multiplayer" gate is actually "is-host". This changes the semantics significantly:
- Functions guarded by `DAT_0097fa8a != 0` are **HOST-ONLY** (not "any MP participant")
- Anti-cheat hash dead-in-MP: actually dead-on-host AND on client (still dead in MP overall, conclusion holds)
- ChecksumComplete/EnterSet handlers: registered HOST-ONLY (correct, matches packet trace asymmetry)

## v5 Evidence Anchors (this memo)

| Claim | Address | Function | Confidence |
|-------|---------|----------|------------|
| `[0x0097FA89] = 0` then `=1` at end of MultiplayerGame_Ctor, UNCONDITIONAL | 0x0069EB17, 0x0069EB3A | MultiplayerGame_Ctor (FUN_0069E590) | high (byte-disasm + decompile) |
| `DAT_0097fa8a != 0` gates host-only NoMe/Forward + ChecksumComplete/EnterSet | 0x0069E694, 0x0069EA51 | MultiplayerGame_Ctor | high (decompile + disasm) |
| `(DAT_0097fa8a != 0) && (DAT_0097fa88 != 0)` gates self-NewPlayerInGame post | 0x0069EA80, 0x0069EA89 | MultiplayerGame_Ctor | high |
| SP init writes FA88=1, FA8A=1, FA89=0 | 0x00405C10 region | FUN_00405C10 (parent ctor) | high (decompile) |
| MP init switch — Client (ESI=0): FA88=1, FA89=1, FA8A=0 | 0x00438D1F-0x00438D33 | unnamed (multiplayer GoLive at ~0x00438C70) | high (byte-disasm) |
| MP init switch — Dedicated (ESI>1): FA88=0, FA89=1, FA8A=1 | 0x00438D57-0x00438D70 | same | high (byte-disasm) |
| MP init switch — Host+Player (ESI=1): FA88=1, FA89=1, FA8A=1 | 0x00438D57-0x00438D70 | same | high (byte-disasm) |
| Client→Host send-self-destruct gate `DAT_0097fa8a == 0` | 0x0050D070 region | TopWindow__SelfDestructHandler | high (decompile) |
| Host-only UI "Dedicated Server0123" forced when `DAT_0097fa88 == 0` | 0x00504890 region | FUN_00504890 (MultiplayerWindow_Setup) | high (decompile) |
| Host-only NewPlayerInGame processing gate `DAT_0097fa8a != 0` | 0x006A1E70 region | NewPlayerInGameHandler | high (decompile) |
| Host-only AddToRepairList post triple-gate `fa89 && fa8a` | 0x00565900 region | FUN_00565900 (repair-related) | high (decompile) |
| Game-NOT-live ship-state write gate `(fa89 == 0) || (fa8a != 0)` | 0x005AE090 | FUN_005AE090 (ship+0x2E9 setter) | high (decompile) |
| IsLocalPlayerShip MP-vs-SP gate on `DAT_0097fa89` | 0x005AE140 | IsLocalPlayerShip | high (decompile) |
| 4-way collision-rate-limit branching on fa8a/faa2/fa88 | 0x005A22A0 | FUN_005A22A0 (CollisionRateLimit) | high (decompile) |

All evidence cross-anchors. No contradictions found.

## Recommended Propagation (for orchestrator)

1. **CLAUDE.md** — fix the Key Globals table:
   ```
   | 0x0097FA88 | HasLocalPlayer (BYTE) - 0=dedicated server, 1=local player exists |
   | 0x0097FA89 | GameLive (BYTE) - 1=multiplayer game running, 0=menu/single-player |
   | 0x0097FA8A | IsHost (BYTE) - 1=host (dedicated or with-player), 0=client |
   ```

2. **Ship__WriteStateUpdate plate at 0x005B17F0** — correct the gate labels in the v5 plate:
   - `bIsSinglePlayer = !DAT_0097fa8a (IsMultiplayer)` → `bIsClient = !DAT_0097fa8a (IsHost)` and note that "client OR (server-side WriteStateUpdate running on a remote-ship's local view)" is the trigger for the bIsSinglePlayer-named path. The behavioral interpretation (`C->S=0x80, S->C=0x20`) is intact; only labels change.
   - `if (!DAT_0097fa88) { /* we are HOST */ }` → `if (!DAT_0097fa88) { /* dedicated server, no local player */ }`
   - `else { /* we are CLIENT */ }` → `else { /* host with local player */ }`

3. **Pre-v5 docs cited above** — re-validate any gate description that says "IsHost" while citing 0x0097FA89, or "IsMultiplayer" while citing 0x0097FA8A, or "IsClient" while citing 0x0097FA88. The behavioral conclusions may still hold but the semantic chain needs correction. Highest-impact pre-v5 docs to re-check:
   - damage-system, shield-system, weapon-firing-mechanics (IsHost gates)
   - collision-rate-limiting (already cites FA89; needs SP-vs-MP framing)
   - architecture-overview, dedicated-server (top-level claims)
   - reading-decompiled-code, lessons-learned (anchor docs that taught the inverted naming to other agents)

4. **Validated docs (v5)** that already used these flags need a header note. Per my MEMORY.md index, the validated docs that cited these flags directly include: self-destruct-pipeline (correctly), stateupdate, subsystem-integrity-hash, set-phaser-level-protocol, tgmessage-routing, python-messages, pythonevent-wire-format, tgobjptrevent-class, collision-effect-protocol, ship-death-lifecycle, tgmessage-routing-cleanroom. The validation memos in my MEMORY.md were written using whichever naming the doc had — most are behaviorally correct (because the gate flows match the binary), but the SEMANTIC interpretation needs correcting in any doc that explained "DAT_0097fa89 is the IsHost flag."

## Open Questions

1. **0x0097FA8B**: 4th flag byte at adjacent offset. Some docs call it "IsProcessingPackets" or similar; not in scope of this cascade but worth a separate verification.
2. **0x0097FAA2**: Friendly-fire gate. Confirmed via 4-way collision-rate-limit pattern but never deeply traced; assume label correct.
3. **The "MultiplayerGame_Start" function around 0x00438C70**: Currently unnamed in Ghidra. It's the MultiplayerGame init that branches on ESI (mode). Should be named in a follow-up — it's the canonical "set up the three flags" function. Strings nearby ("Multiplayer Options", "Direct_Join_Address", "Player_Name", "Password", "Dedicated_Server0123") confirm its role.

## Status

`high` confidence on the corrected attribution. All three flags' semantics are independently confirmed across 9+ distinct functions. Single cascade with no contradictions.

Ghidra annotations: NONE applied this session. Per v5 policy (no annotation scripts), names live in docs only. Future v5 doc validation should label these flags correctly. Suggested labels:
- 0x0097FA88 → `g_bHasLocalPlayer`
- 0x0097FA89 → `g_bGameLive`
- 0x0097FA8A → `g_bIsHost`

Confidence: **high** (byte-level disasm + decompile + 4 independent cross-anchors).
