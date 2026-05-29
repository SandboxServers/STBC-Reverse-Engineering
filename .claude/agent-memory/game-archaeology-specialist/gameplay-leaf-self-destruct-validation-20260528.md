# Gameplay Leaf #14 — Self-Destruct Pipeline Validation (2026-05-28)

**Doc**: `docs/gameplay/self-destruct-pipeline.md` (680 lines, dated 2026-02-21)
**Status**: `partial` (1 doc-level correction, 2 binary-level clarifications, ~6 inherited mislabels from CLAUDE.md)
**Method**: live Ghidra @ STBC.exe — decompile + xref + disassembly verification

---

## Verdict

The doc's THREE EXECUTION PATHS narrative is **binary-correct**. The 3-path table at lines 439–443 maps directly to the asm at `0x0050D070`. The wire-format table at lines 562–587 is rock-solid (anchored to trace data + .rdata constants).

The doc inherits CLAUDE.md's mislabeling of `0x0097FA89` as "IsHost" and `0x0097FA8A` as "IsMultiplayer". The actual asm-derived semantics flip these: `0x0097FA8A=IsHost`, `0x0097FA89=GameLive` (toggled to 1 at end of MultiplayerGame_Ctor for BOTH host AND client). The doc's prose uses the wrong names but the asm flow is correctly described.

The handler at `0x0050D070` was **bare code** in Ghidra — NO function existed prior to this session. I created `TopWindow__SelfDestructHandler` (body size 0x0DB = 219 bytes, ending 0x0050D14B, matching doc claim).

---

## Anchors Confirmed (byte-level)

### Constants / Strings
| Item | Address | Bytes | Status |
|------|---------|-------|--------|
| `"TopWindow::SelfDestructHandler"` | 0x008E2354 | `54 6f 70 57 69 6e 64 6f 77 3a 3a 53 65 6c 66 44 65 73 74 72 75 63 74 48 61 6e 64 6c 65 72 00 00` | ✓ |
| `"SELF_DESTRUCT_REQUEST_MESSAGE"` | 0x00952F44 | confirmed | ✓ |
| `"ET_INPUT_SELF_DESTRUCT"` | 0x00953920 | confirmed | ✓ |
| `DAT_00888B54` = 0.0f | 0x00888B54 | `00 00 00 00` | ✓ |
| `DAT_008E5C18` = FLT_MAX | 0x008E5C18 | `ff ff 7f 7f` | ✓ (sentinel, NOT a damage threshold — see C2) |

### Functions
| Address | Doc Name | Reality | Status |
|---------|----------|---------|--------|
| 0x0050D070 | TopWindow::SelfDestructHandler | bare code → created this session | ✓ post-create |
| 0x006A01B0 | HostMsgHandler (opcode 0x13) | `void __thiscall HostMsgHandler(this, TGBufferStream*)` | ✓ |
| 0x005AF5F0 | DoDamageToSelf | `float10(int ship)` — single-arg, calls FUN_005af4a0 | ✓ |
| 0x005AF4A0 | DoDamageToSelf_Inner | 5-param, body 0x005af4a0-0x005af5e6 | ✓ |
| 0x005AFEA0 | ShipDeathHandler | OBJECT_EXPLODING event creator | ✓ |
| 0x0050CA50 | event-type registrar | `FUN_006d92b0(&DAT_00987878, 0x8001dd, "TopWindow::SelfDestructHandler")` | ✓ |
| 0x0050C8B0 | name→code binder | `FUN_006da130(&LAB_0050d070, "TopWindow::SelfDestructHandler")` | ✓ |

### Wire / Behavior
- **1-byte payload** confirmed via disasm at 0x0050D0CE: `MOV byte ptr [ESP + 0x17], 0x13`, `PUSH 0x1` (size), `PUSH EAX` (ptr), CALL TGMessage BufferCopy (FUN_006B84D0). ✓
- **TGMessage 0x40-byte alloc** at 0x0050D0A1: `PUSH 0x40`. ✓
- **Host connection ID at network+0x20**: `MOV ECX, dword ptr [EDI + 0x20]` at 0x0050D0D8. ✓
- **5 xrefs to FUN_005af5f0** confirmed: 0x0050d132, 0x005afd56, 0x006a01d3, 0x006a0e18, 0x005b355b. ✓ (matches doc's "5 call sites" table)
- HostMsgHandler reads sender ID from `pStream->dwField_0x0C` (NOT msg+0x0C — TGBufferStream field 0x0C, which is the embedded sender connection ID). ✓
- HostMsgHandler calls `FUN_005af5f0(*(undefined4 *)(ship + 0x2c4))` — passes PowerSubsystem ptr (ship+0x2C4 matches power-system memo). ✓
- DoDamageToSelf passes `param_2=0` (attacker=NULL), `param_5=1` (force_kill=1) to inner. ✓ (matches doc's "force_kill=1" claim and "NULL attacker → no kill credit" implication)

---

## Corrections

### C1 (DOC) — "DestroyObject Handler (Opcode 0x14)" section misstates the role

**Doc Lines 319-358**: claims "After the explosion sequence completes, the host sends opcode 0x14 (DestroyObject) to remove the object from all clients."

**Binary Reality**: ship-death-lifecycle.md (validated leaf #11 earlier this campaign) confirmed `0/59` DestroyObject sends across the entire 33.5-min battle trace. The doc's own line 595 contradicts the section header: "NOT sent: opcode 0x14 (DestroyObject) — zero across both self-destruct and combat kills (0/59 in battle trace)". The section is **vestigial** — it describes what the FUN_006A01E0 handler DOES, but the handler is NEVER invoked in stock-dedi MP play. Should be reframed as "DestroyObject Handler exists in code but is not used during ship death — kept for reference only".

**Severity**: medium. Doc body and Executive Summary contradict the section heading. OpenBC implementers reading lines 319-358 may believe they need to send 0x14 on death.

### C2 (Clarification) — ShipDeathHandler gate `hullHP < 0x008E5C18`

**Doc Line 292**: "ship+0x14C (hull HP) must be >= some threshold (DAT_008e5c18)"

**Binary Reality**: `DAT_008E5C18 = 0x7F7FFFFF = FLT_MAX` (raw bytes `ff ff 7f 7f`). The gate `*(float*)(ship+0x14C) < FLT_MAX` is the "ship not yet sentinel-marked" check, i.e., "ship is still considered alive". When a ship is set to die, this field is overwritten to FLT_MAX as a sentinel. So the gate is really a **dead-ship reentrancy guard** ("don't re-fire OBJECT_EXPLODING for an already-dying ship"), NOT a "must be above threshold" damage check. The doc's "some threshold" framing is misleading.

**Severity**: low. Clarification only.

### C3 (Inherited from CLAUDE.md) — Flag identification inversion

**Doc Lines 105, 213, 384-407**: Treats `0x0097FA89` as IsHost and `0x0097FA8A` as IsMultiplayer (matching CLAUDE.md's "Key Globals" table).

**Binary Reality** (asm at SelfDestructHandler 0x0050D070 + MultiplayerGame_Ctor 0x0069E590):
- `0x0097FA89` is toggled to 1 at the **end** of MultiplayerGame_Ctor (line near 0x006eb35) for **BOTH host AND client** — it represents "MultiplayerGame is live/active" or "GameStarted-in-MP", NOT IsHost.
- `0x0097FA8A` gates the HOST-ONLY block of MultiplayerGame_Ctor (NoMe/Forward group creation, EnterSetHandler/ChecksumCompleteHandler registration) — this is IsHost.
- `0x0097FA88` gates the CLIENT-ONLY initial NewPlayerInGame post (peer-side join broadcast) — this is IsClient.

With correct labels, the doc's 3-path narrative still maps perfectly:
- Host MP (GameLive=1, IsHost=1) → local damage ✓
- Client MP (GameLive=1, IsHost=0) → network send via 0x13 ✓
- SP (GameLive=0) → local damage with TestMenuState ✓

**Severity**: high for global naming, low for self-destruct flow correctness. The doc's behavior description is correct; only the per-flag identification is inverted. Multiple validated docs (this one, networking docs, protocol docs) inherit the same mislabel from CLAUDE.md and should be corrected in one sweep.

**Recommendation**: Update CLAUDE.md "Key Globals" table:
- `0x0097FA88 IsClient` (1=client, 0=host or SP)
- `0x0097FA89 GameLive_MP` (1=MultiplayerGame_Ctor completed, 0=not in MP or SP)
- `0x0097FA8A IsHost` (1=host or SP-acting-as-host, 0=client)

This sweep should be its own corrective task.

---

## Clarifications

### Clar1 — DoDamageToSelf signature

**Doc Line 36**: `FUN_005AF5F0 — __thiscall(ship*, powerSubsystem*)`

**Binary Reality**: Ghidra signature is single-arg `float10(int param_1)`. The decompile shows it only reads `param_1` and passes literals to FUN_005af4a0. **Likely the caller pushes ship+0x2C4 as the only arg** (because PowerSubsystem owns its parent ship via subsystem+0x40 backref). Looking at HostMsgHandler: `FUN_005af5f0(*(undefined4 *)(iVar1 + 0x2c4))` — passes ONE arg (the PowerSubsystem). Then DoDamageToSelf_Inner gets ship by reading `*(int*)(powerSS + 0x40)` (subsystem parent backref). The doc's 2-arg signature is wrong; it's 1 arg (the subsystem) and ship is recovered via the subsystem→parent backref.

**Severity**: low. The semantics match — same data flows through — just the param-count is wrong.

### Clar2 — ShipDeathHandler "dest = ship" claim

**Doc Line 297**: "dest = ship (the dying ship), charData = ship->hullHP (at +0x14C)"

**Binary Reality**: The asm sets:
- event+0x10 = 0x0080004E (event type) ✓
- event+0x2C = `*(int*)(param_1 + 0x14C)` = hullHP ✓ (matches doc's "charData")
- event+0x28 = attacker's ship ID (via subsystem→ship lookup) OR 0 if no attacker

There is NO field set to "ship" (the dying ship pointer). The event uses `FUN_006d62b0(param_1)` which is likely TGEvent_SetSource/Sender — that sets a different field outside what I can see in this decompile. The wire-format trace (line 632) shows `dest=ship_objID` at the appropriate wire offset, so the doc's high-level claim resolves correctly at the wire layer, but the in-memory event-field assignment as described doesn't quite match the decompile.

**Severity**: low. Wire format matches; in-memory description is hand-wavy.

---

## Field-Offset Cross-References (foundation alignment)

| Offset | Subject | Meaning | Source |
|--------|---------|---------|--------|
| ship+0x2C4 | PowerSubsystem ptr | reactor subsystem | power-system memo + HostMsgHandler asm |
| ship+0x14C | hullHP (float) | health, FLT_MAX = "dying sentinel" | damage-system memo + ShipDeathHandler |
| ship+0x150 | already-dying flag | reentrancy guard | ShipDeathHandler asm |
| ship+0x244 | special state | cleared on death (cloak?) | ShipDeathHandler asm |
| ship+0x2E9 | cascade-fail flag | DoDamageToSelf_Inner Gate3 | DoDamageToSelf_Inner asm |
| ship+0x2EA | damage-enabled flag | DoDamageToSelf_Inner Gate2 | DoDamageToSelf_Inner asm |
| subsystem+0x30 | currentHP (float) | DoDamageToSelf_Inner reads | inner asm |
| subsystem+0x40 | parent ship backref | (inferred) | shield-system memo |
| subsystem+0x44 | min-HP-threshold flag | DoDamageToSelf_Inner Gate4 | inner asm |
| TopWindow+0x60 | God Mode flag | DoDamageToSelf_Inner Gate1 | inner asm + DAT_0097e238 |
| Clock+0x8C | TestMenuState | SelfDestructHandler SP gate | SelfDestructHandler asm + Clock global @ 0x009A09D0 |

---

## Open Questions

### OQ1 — What are FUN_005AFD56, FUN_006A0E18, FUN_005B355B?
The doc claims these are "Ship damage handler", "MultiplayerGame player slot reset", "Ship linked-list iteration". All 3 are unpromoted bare code. Verifying these claims would require promoting them to functions and re-decompiling. Out of scope for this self-destruct validation; recorded for future archaeologists doing damage-cascade work.

### OQ2 — Is `event+0x28 = 0` for self-destruct really enforced?
The asm path for self-destruct (`param_2 = NULL` passed to ShipDeathHandler) hits the `else { ... iVar2+0x28 = 0; ... }` branch. Confirmed at line 0x005B0042 (`LAB_005B0042: TGEventManager__PostEvent(iVar2);`). So yes, self-destruct events have firing_player=0 → no kill credit. ✓ But the deduction chain from `param_2==NULL` to `iVar2+0x28=0` requires careful trace; if the `param_2 != (int *)0x0` branch is somehow taken, weapon-attacker fields could leak in. **Trace data corroborates**: 6/6 self-destructs in PR#34 testing all had `firing_player=0`.

### OQ3 — Mission5 team-kill awarding to opposing team
Doc Lines 522-531 cite Mission5.py 797-809. Python source is checked-in at `reference/scripts/Mission/Mission5.py`. I didn't verify this Python claim against the script. Likely true (mission scripts are public) but flagged for completeness.

---

## Completeness Scores

| Function | Effective Score | Fixable Deductions | Notes |
|----------|-----------------|-------------------|-------|
| TopWindow__SelfDestructHandler (0x0050D070) | 13.08 | 86.92 | Newly created; no plate, no var naming yet |
| HostMsgHandler (0x006A01B0) | 38.97 | 61.03 | Has prototype + convention; missing plate |
| DoDamageToSelf (0x005AF5F0) | 11.91 | 88.09 | FUN_ name, no plate |
| DoDamageToSelf_Inner (0x005AF4A0) | 0.0 | 110.68 | FUN_ name, no plate, 3 magic, 4 struct unresolved |
| ShipDeathHandler (0x005AFEA0) | 0.0 | 104.93 | FUN_ name, no plate, 12 magic |

All five are load-bearing for self-destruct; none are at v5 doc-ready (>50) yet. The doc's claims are accurate against the binary even though Ghidra naming is sparse.

---

## v5 Status

**Document**: `partial`

**Reason**: 1 medium correction (DestroyObject section is vestigial / contradicts own wire-format finding) + 1 high-but-shared correction (flag mislabel inherited from CLAUDE.md, applies to multiple docs). All wire-format and execution-path claims hold against the binary.

**Recommended actions**:
1. Add a "DestroyObject IS NOT SENT" note at the top of the 0x14 section, OR remove the section entirely.
2. Update CLAUDE.md flag table (separate task) — will fix this doc and several others in one stroke.
3. The doc is generally clean for OpenBC implementers if they read the wire-format and 3-path sections.

---

## Cross-doc tensions

- **wire-format-spec.md** opcode table line for 0x13: `HostMsg | FUN_006A01B0 | Self-destruct request (client→host, 1-byte, no payload)` — agrees with this doc. ✓
- **damage-system.md** validated 2026-05-28 — confirms DAT_00888B54=0.0f, ship+0x14C=hullHP, ship+0xD8=mass (not referenced here). ✓
- **power-system.md** validated 2026-05-28 — confirms PowerSubsystem at ship+0x2C4. ✓
- **ship-death-lifecycle.md** validated 2026-05-28 — confirms 0/59 DestroyObject sends in battle trace, agreeing with this doc's wire findings (line 595) but contradicting this doc's section 319-358.
