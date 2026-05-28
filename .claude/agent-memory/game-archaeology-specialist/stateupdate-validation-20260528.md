---
name: stateupdate-validation-20260528
description: v5 validation of docs/protocol/stateupdate.md (mid #8) — opcode 0x1C wire format byte-anchored against the 2,472-byte Ship__WriteStateUpdate at 0x005B17F0 and 1,539-byte Ship__ReadStateUpdate at 0x005B21C0; dispatcher MpgameHandleStateUpdate at 0x0069FF50 recovered. ZERO material wire-format corrections — doc accurately describes the 8 dirty bits and their payload formats. Two corrections: (1) Ship vtable slot 73 (NOT vtable+0x124 of arbitrary class) is the receiver; (2) hash-flag-emit gate uses bIsSinglePlayer (bVar16), NOT bVar2 — the decompiler's bVar2/bVar16 naming was misleading. Receiver-side hash check is gated by isMultiplayer; sender emits hash bit only in SP. Result: subsystem-integrity-hash.md's "dead in MP" claim STILL holds. PowerSubsystem__WriteState created (Ghidra missed it: function entry at 0x005644b0 was undefined; doc had correct address).
metadata:
  type: project
---

# StateUpdate Validation — 2026-05-28

Phase 1-3 v5 validation of `docs/protocol/stateupdate.md` (protocol family mid #8). The highest-volume protocol message — 30,000+ packets per stock session.

## Top-Level Findings

1. **All 8 dirty-bit wire formats CONFIRMED byte-by-byte** by cross-anchoring sender FUN_005B17F0 + receiver FUN_005B21C0 + stream-primitive vtable sizes. Per-flag payload sizes:
   - 0x01 POSITION_ABSOLUTE = 12 bytes (3 floats) + 1 bit + (if SP) 2 bytes (XOR-folded hash)
   - 0x02 POSITION_DELTA = CV4 with param=1 → 5 bytes (3 dir + ushort mag)
   - 0x04 FORWARD = CV3 = 3 bytes
   - 0x08 UP = CV3 = 3 bytes
   - 0x10 SPEED = CF16 = 2 bytes
   - 0x40 CLOAK = 1 bit
   - 0x20 SUBSYSTEMS = 1 byte (start_index) + variable per-subsystem WriteState payload
   - 0x80 WEAPONS = repeated [idx:u8][health:u8] pairs

2. **Dispatcher chain CONFIRMED:**
   - MpgameHandleMessage at 0x0069F2A0 jump-table slot 28 (opcode 0x1C)
   - → FUN_0069FF50 (NOW: `MpgameHandleStateUpdate`, plate-documented)
   - → vtable[+0x124] (slot 73) on the looked-up object
   - → FUN_005B21C0 (NOW: `Ship__ReadStateUpdate`, plate-documented)
   - Sender chain (vtable[+0x120] = slot 72):
   - → FUN_005B17F0 (NOW: `Ship__WriteStateUpdate`, plate-documented)

3. **PowerSubsystem__WriteState (0x005644B0) CREATED in Ghidra.** Doc claimed this address; Ghidra had NOT recognized it as a function (no calls pointed to function-entry-recognized code). Created and decompiled — wire format Format 3 confirmed: base WriteState + WriteChar(mainBatteryByte) + WriteChar(backupBatteryByte) where each byte = (currentPower / property->limit) * 255.0. Property limit offsets confirmed: +0x48 = main, +0x4C = backup (both via FUN_005634A0 = GetProperty).

4. **Position hash flag-emit gate has SUBTLE decompiler-misleading variable naming.** The decompiled C reads:
   ```c
   if (bVar16) { WriteBit(1); WriteShort(hash); } else { WriteBit(0); }
   ```
   Looks like it tests bVar2 (the MP+owner-match flag computed earlier). But disassembly proves at 005b1c76 BL was RELOADED with bVar16 (=!isMultiplayer) immediately before the WriteBit dispatch. So the emit-test is: **hash bit = 1 only in single-player**. Receiver-side validation gated by `isMultiplayer != 0`. Therefore:
   - SP: sender emits hash bit + hash; receiver does NOT validate (skip path).
   - MP: sender emits hash bit = 0; receiver reads bit but never enters validate.
   - Result: anti-cheat hash is **DEAD IN MULTIPLAYER** — confirmed via byte-level disassembly. The subsystem-integrity-hash.md doc's existing claim still holds.

5. **Direction-flag selection logic CONFIRMED:**
   - bVar16 = !DAT_0097fa8a (IsMultiplayer)
   - SP path: bValue |= 0x80 (always weapons), never 0x20
   - MP + friendly_fire on + (host>=2 players OR client>=3 players): skip 0x20
   - Otherwise: bValue |= 0x20
   - Cross-anchors against 30K+ stock-dedi traces: C→S exclusively 0x80, S→C exclusively 0x20. Matches.

6. **SUBSYSTEM and WEAPON share the SAME linked list at ship+0x284.** Doc claim "iterates the weapon linked list at ship+0x284" is correct in address but misleading — it's the same list as subsystems. Filter is `vtable[+8](0x801C) == true` (IsWeaponType check) which selects only weapon nodes during flag-0x80 emission.

7. **Per-tracker state record at iVar5 layout decoded:**
   - +0x04 flLastForceSendTime (master timestamp)
   - +0x0C flLastSpeedSent (dedup)
   - +0x10..+0x18 vfSavedAnchorPos (delta basis)
   - +0x1C flLastDeltaMag (dedup)
   - +0x20..+0x22 abForwardBytes3 (last sent fwd dir bytes)
   - +0x24 flLastForcePosTime
   - +0x28..+0x2A abUpBytes3 (last sent up bytes)
   - +0x2B..+0x2D abDeltaDirBytes (last sent delta dir bytes)
   - +0x2E bLastCloakState
   - +0x30 pSubsysCursor (round-robin pointer)
   - +0x34 uSubsysIndex
   - +0x38 pWeaponCursor
   - +0x3C uWeaponIndex
   - +0x40..+0x4C per-weapon hash-table for delta-dedup (allocates 0xC bytes per entry)

8. **TWO state buffers updated on receive:**
   - ship+0x88, +0x90..+0x98, +0x9C..+0xA4 (kinematic state with anchor + last timestamp)
   - iVar3+0x2C..+0x50 = animation tracker (kinematic interpolation for rendering)
   - iVar3 obtained via FUN_005A1720 (returns Animation parent) then FUN_0047DE50 (Cast to type 9 — the animation node type).

9. **Stream primitive vtable offsets (already validated in stream-primitives.md but cross-checked):**
   - +0x50 ReadChar / +0x54 WriteChar (1 byte)
   - +0x58 ReadBool_Bit? / +0x58 WriteBool_Bit?
   - +0x60 ReadShort? / +0x5C WriteShort (2 bytes)
   - +0x68 ReadInt / +0x6C WriteInt (4 bytes) — used for ReadShort path in CV4
   - +0x70 ReadFloat / +0x74 WriteFloat (4 bytes)
   - +0xA0/+0xA4 CV4 in-place encoders (ushort vs float magnitude)
   - +0xA8 CV3 in-place encoder
   - +0xB0/+0xB4 CV4 in-place decoders (float vs ushort magnitude)
   - +0xB8 CV3 in-place decoder
   - +0xD8 flush bit-aligned write group

10. **Force-resend timing CONFIRMED:** DAT_00888860 = master force-update threshold (float). Per-field flLastSent at iVar5+0x24 (full-pos). Master at iVar5+0x4. When ALL fields sent simultaneously (pos+delta+fwd+up+speed+cloak), tracker.flLastForceSendTime updates.

## Doc Claim Verification — Verbatim

| Doc Claim | Status | Evidence |
|-----------|--------|----------|
| Serializer at FUN_005b17f0 | ✓ CONFIRMED | Ship vtable slot 72 at 0x00894340+0x120 (tg-hierarchy-vtables) |
| Receiver at FUN_005b21c0 | ✓ CONFIRMED | Ship vtable slot 73 at 0x00894340+0x124 |
| Sent at ~10Hz per ship | medium | Implied by per-tracker DAT_00888860 throttle; rate not byte-anchored |
| Wire header opcode=1B, obj_id=4B, gameTime=4B, dirty_flags=1B | ✓ CONFIRMED | Sender 005b1d31/d44/d52/d60 + receiver 005b2231/36/3b/40 |
| Dirty bit 0x01 = POSITION_ABSOLUTE | ✓ CONFIRMED | Receiver 005b2250 path reads 3 floats + hash bit |
| Dirty bit 0x02 = POSITION_DELTA via CV4 | ✓ CONFIRMED | Receiver 005b2334 calls CompressedVector4_ReadVirtual(_,_,_,1) |
| Dirty bit 0x04 = FORWARD via CV3 | ✓ CONFIRMED | Receiver 005b2378 calls CompressedVector3_ReadVirtual; CV3 = 3 bytes |
| Dirty bit 0x08 = UP via CV3 | ✓ CONFIRMED | Receiver 005b23ac calls CV3 read |
| Dirty bit 0x10 = SPEED via CF16 | ✓ CONFIRMED | Receiver 005b23e0 reads ushort, decodes via CompressedFloat16_Decode |
| Dirty bit 0x40 = CLOAK_STATE via WriteBit/ReadBit | ✓ CONFIRMED | Receiver 005b2408 reads bool bit |
| Dirty bit 0x20 = SUBSYSTEM_STATES round-robin | ✓ CONFIRMED | Receiver 005b2439 + sender 005b1e78 with 10-byte budget |
| Dirty bit 0x80 = WEAPON_STATES round-robin | ✓ CONFIRMED | Receiver 005b249e + sender 005b1f24 with 6-byte budget |
| Wire reads "ship->vtable[0xAC] = GetForwardVector" | ✓ CONFIRMED | Sender 005b19ad calls vtable+0xac |
| Wire reads "ship->vtable[0xB0] = GetUpVector" | ✓ CONFIRMED | Sender 005b19d3 calls vtable+0xb0 |
| FUN_005a05a0 = GetVelocity | ✓ CONFIRMED | Returns (ship+0x18)+0x98 |
| FUN_005ac4f0 = IsReversing | ✓ CONFIRMED | Returns 1 if vel·fwd < 0 |
| FUN_006d2f10 = CV4 write | ✓ CONFIRMED | Existing rename + decompile |
| FUN_006d2e50 = CV3 write | ✓ CONFIRMED | Decompile shows vtable+0xa8 + 3x WriteChar |
| Subsystem ReadState vtable+0x74 | ✓ CONFIRMED | Receiver 005b2476 dispatches via [+0x74] |
| Weapon SetHealth vtable+0x84 | ✓ CONFIRMED | Receiver 005b24e0/24e9 dispatches via [+0x84] |
| Weapon IsType filter vtable+0x08(0x801C) | ✓ CONFIRMED | Receiver 005b24d2 |
| Format 1 base ShipSubsystem WriteState at 0x0056d320 | ✓ CONFIRMED | Decompile shows condition byte + child recurse + flush |
| Format 2 PoweredSubsystem WriteState at 0x00562960 | ✓ CONFIRMED | Decompile shows base + isOwnShip-gated bit + powerPct byte |
| Format 3 PowerSubsystem WriteState at 0x005644b0 | ✓ CONFIRMED | CREATED in Ghidra (was undefined-fn); confirms base + 2 battery bytes |
| Per-tracker round-robin cursor+index at iVar7+0x30/0x34 | ✓ CONFIRMED | Sender 005b1e89..1f04 walks ship+0x284 linked list with cursor cycle |
| Subsystem budget 10 bytes | ✓ CONFIRMED | Sender 005b1ec0 `CMP EAX, 0xa` |
| Weapon budget 6 bytes | ✓ CONFIRMED | Sender 005b1f66 `CMP EAX, 0x6` |
| Receiver wraps subsystem list to head on NULL | ✓ CONFIRMED | Receiver 005b2493 sets piVar9 = ship[+0x284] when NULL |
| Subsystem hash dead-in-MP (sender SP-only emits) | ✓ CONFIRMED | Bytes 005b1c76 reload BL with bVar16; flag-0x01 hash branch tests BL |
| Hash function FUN_005b5eb0 = ComputeSubsystemHash | ✓ CONFIRMED | Sender 005b1dab + receiver 005b22b0 both call same fn |
| ET_BOOT_PLAYER = 0x008000F6 | ✓ CONFIRMED | Receiver 005b2311 writes to allocated event obj +0x10 |
| Cloak engage FUN_0055f360 / disengage FUN_0055f380 | ✓ CONFIRMED | Receiver 005b242f/2434 dispatch by bit |
| Speed scale via DAT_008944c4 (weapon health scale, NOT speed) | ✓ CORRECTION CONFIRMED | DAT_008944c4 ONLY at receiver 005b24e0 (weapon health, not speed) — doc gets this right at flag 0x80 |

## Open Questions

1. **Caller of Ship_WriteStateUpdate not directly identified.** No CALL with the function address (vtable-dispatched). Likely the per-tick TGNetwork::Update or per-peer message-queue builder iterates remote objects. The Tracker hash-table at ship+0x68 implies an outer loop iterates the tracker contexts and dispatches per-ship per-peer. The function is invoked as `ship->vtable[+0x120](pTrackerCtx)` — would need to find the iteration site. Estimated: somewhere in 0x006B…7… range based on TGNetwork tick callbacks.

2. **What is `param_2 (pTrackerCtx)` precisely?** It has:
   - +0x08 = hash key (used to find per-ship tracker record)
   - +0x0C = some matching ID compared against ship.netId (for the hash gate)
   It looks like a "TargetPeerContext" with the peer's player slot or session ID. Worth tracking in a future investigation.

3. **What does iVar3 (animation tracker) point to exactly?** FUN_005A1720 + FUN_0047DE50 chain produces a non-null pointer used to update interpolation state (+0x2C through +0x54). NIF scene-graph cast? AnimationController?

4. **Per-weapon delta-dedup hash table at iVar5+0x40 uses 0xC-byte entries.** Layout TBD (head pointer + size + ...).

5. **Verify CV4-with-param-1 magnitude width.** Doc says "uint16 magnitude" — receiver 005b2348 path reads via vtable+0x58 (likely u16 read). CV4 with param=0 path would read u32 mag via vtable+0x70 (ReadFloat) — but param=0 not used in StateUpdate path. Foundation-stream-primitives CV4 RE confirms 5-byte wire format with ushort.

## Corrections / Refinements Needed in Doc

| Section | Issue | Fix |
|---------|-------|-----|
| Header | "FUN_005b17f0 (called per-ship per-tick on the owning peer)" | Add: "Ship vtable slot 72 (offset +0x120 in vtable at 0x00894340)" |
| Header | "FUN_005b21c0 (processes incoming state updates)" | Add: "Ship vtable slot 73 (+0x124). Called by MpgameHandleStateUpdate at 0x0069FF50 (opcode 0x1C dispatcher entry)." |
| Flag 0x01 section | "[if has_subsystem_hash AND is_multiplayer:]" wire-format box | Clarify: wire format is ALWAYS `[bit][if bit set: ushort hash]`. The `AND is_multiplayer` is the RECEIVER's validation gate, not the wire format. Receiver always reads the bit + (if set) the 2-byte hash; only validates in MP. |
| Flag 0x01 section | Mention SENDER emits hash bit=1 only in SP (matches subsystem-integrity-hash.md) | Add: "Sender emits hash bit=1 only when single-player (DAT_0097fa8a == 0); always 0 in MP. Receiver validates only in MP. Dead in stock MP gameplay." |
| Flag 0x80 section | "iterates the weapon linked list at ship+0x284" | Clarify: "iterates the SAME ship+0x284 linked list as subsystems; vtable[+8](0x801C) filter selects only weapon-type nodes during emission/apply." |
| Flag Decision Logic | "However, packet traces show clients send 0x80 in multiplayer..." | DROP the speculation paragraph. The mechanism is correctly described above; the trace pattern is a natural consequence of who is host vs client and the friendly-fire + player-count gate. Replace with: "These flags are mutually exclusive in MP per the (host >=2 players) / (client >=3 players) skip-subsystems gate when friendly fire is enabled — the stock dedi traces confirm 100% disjoint usage." |
| Receiver section | "+0    1     u8       weapon_index" wire format | Note: receiver walks idx+1 nodes from ship+0x284 head, then filters by IsWeaponType. Same list as subsystems. |
| Open metadata | (no frontmatter) | Add v5 header: status=partial-pending-publication (now mostly verified, minor clarifications above) |

## Status

**Recommendation: status=verified after corrections applied** — all 8 dirty-bit wire formats anchored to byte-level positions in sender + receiver. The doc was accurate; only clarifications (not corrections) needed.

## Method Notes

- **Decompiler variable-name aliasing:** Critical caveat — Ghidra's pseudocode assigns local names (`bVar2`, `bVar16`) but the underlying disassembly can REUSE the same register (BL) across multiple semantic variables. Always cross-check decompiled boolean conditions with disasm. The Ship_WriteStateUpdate `if (bVar16)` test at flag 0x01 path is the canonical example.
- **vtable[+0x13c] = CanReplicate / ShouldReplicate** observed in sender entry as the gate before any wire emission.
- **Ship vtable slot 72/73 pair is the canonical state-replication interface.** Same pattern likely applies to other replicable classes (DamageableObject, PhysicsObjectClass, anything derived from Ship's tree).
- **PowerSubsystem WriteState at 0x005644B0** is one of those orphan code regions Ghidra missed because no CALL pointed to function-entry — vtable-only dispatch. The doc had the correct address — created the function and decompiled it to verify Format 3.
- **FUN_005A0B50 = KinematicPredictor** (`pos = startPos + vel*t + 0.5*accel*t²`) — used in receiver flag-0x01 path when no fresh position has arrived for `DAT_00888860` seconds.
- **Cross-doc cross-link to stateupdate-subsystem-wire-format.md** for the subsystem linked list structure is preserved; this doc summarizes, that doc has the full catalog.

## Cross-References

- [[engine-snapshot-20260528]] — binary fingerprint, naming coverage
- [[dispatcher-recovery-20260528]] — MpgameHandleMessage at 0x0069F2A0 + jump-table slot 28
- [[struct-skeletons-20260528]] — Ship layout, MultiplayerGame layout
- [[tgbufferstream-vtable-20260528]] — TGBufferStream vtable @ 0x008958d0 (the wire-container)
- [[tg-hierarchy-vtables-validation-20260528]] — Ship vtable 0x00894340 slot 72 = Ship_WriteStateUpdate
- [[stream-primitives-validation-20260528]] — CV3/CV4/CF16 wire formats; SWIG TGBufferStream
- [[transport-layer-validation-20260528]] — TGMessage envelope vtable; type 0x32 wire format
- [[game-opcodes-validation-20260528]] — jump-table slot 28 for opcode 0x1C
- docs/protocol/stateupdate.md — doc being validated
- docs/protocol/stateupdate-subsystem-wire-format.md — subsystem linked list + 3 WriteState formats (cross-link target; will need its own validation pass)
- docs/protocol/subsystem-integrity-hash.md — dead-in-MP claim CONFIRMED by this validation
- docs/protocol/stream-primitives.md — foundation CV3/CV4/CF16 used by this doc
