---
name: wire-format-spec-validation-20260528
description: v5 re-validation of docs/protocol/wire-format-spec.md (hub doc, ~110 claims). All 41 game opcode handlers + 3 dispatchers + 3 MP-Window handlers + 6 NetFile handlers confirmed; 29 event handlers ALL exist as labels with name-matched registration strings via FUN_0069efe0; Settings packet structure CORRECTED (bit-pack not byte); ship+0x2BC/+0x2D4 slot identities CORRECTED via Ship_LinkSubsystemToParent switch decompile; anti-cheat dead-code claim CONFIRMED via FUN_005b17f0 bVar17 gate.
metadata:
  type: project
---

# wire-format-spec.md v5 Validation — 2026-05-28

Protocol family hub validation pass. Doc had ~110 load-bearing claims. Verdict: mostly accurate hub-level consolidation, but two ground-truth corrections in the "Named Slot Layout" subsystem catalog plus one wire-format misrepresentation of the Settings packet.

## Confirmed (high confidence — all addresses verified by `get_function_by_address` against `program: STBC.exe`)

- **3 dispatchers**: MpgameHandleMessage at 0x0069F2A0 (named, plate-attached), FUN_006a3cd0 NetFile, FUN_00504c10 MultiplayerWindow — all exist + bodies match doc sizes.
- **3 MultiplayerWindow handlers**: FUN_00504D30 Settings, FUN_00504F10 GameInit, FUN_00504C70 UICollisionSetting — all confirmed.
- **All 16 dispatched game opcode handlers** (0x02/03, 0x06/0D, 0x07-12/1B generic, 0x13, 0x14, 0x15, 0x17, 0x18, 0x19, 0x1A, 0x1C, 0x1D, 0x1E, 0x1F, 0x29, 0x2A): exist, body sizes match.
- **All 6 NetFile handlers** (0x20/21/22/23/25/27): exist.
- **29 event handler registration addresses** via FUN_0069efe0 — Ghidra hasn't promoted 24 of them to functions (DATA-only xref from registration table — same pattern that hid MpgameHandleMessage pre-recovery), BUT decompile of FUN_0069efe0 confirms identity via registration strings (e.g., `s_MultiplayerGame____SetPhaserLeve_00959f1c` -> "MultiplayerGame :: SetPhaserLevelHandler" at `LAB_006a1970`). All 29 names in doc match string literals exactly.
- **Jump table**: 41 entries at 0x0069F534, opcode-2 indexed, range 0x02-0x2A — confirmed via plate comment + decompile.
- **Anti-cheat hash dead-code claim**: CONFIRMED. FUN_005b17f0 sender computes hash only when `bVar17 = (DAT_0097fa8a == 0)` (single-player); MP path WriteBit(0) and skips hash entirely.

## Corrections (high confidence — Ghidra evidence)

### 1. Settings packet wire format — three bytes are actually packed bits

Doc claims (line near "Settings Packet"):
```
[0x00] [float:gameTime] [byte:0x008e5f59] [byte:0x0097faa2] [byte:playerSlot] [short:mapLen] [data:mapName] [byte:checksumFlag] [if 1: checksum data]
```

Binary (decompile of FUN_006a1b10, the producer):
```
WriteByte(0x00)               # opcode
WriteFloat(gameTime)          # 4 bytes
WriteBit(DAT_008e5f59)        # bit-packed into shared bit group
WriteBit(DAT_0097faa2)        # bit-packed (same group)
WriteByte(playerSlot)         # 1 byte — closes/breaks bit group
WriteShort(strlen(mapName))   # 2 bytes
WriteBytes(mapName, strlen)
WriteBit(checksumFlag)        # bit-packed (new group)
if (checksumFlag) FUN_006f3f30(local_43c)
```

`FUN_006cf770` is **WriteBit** (per stream snapshot, confirmed by decompile: manipulates +0x2C bit-pack state, uses high-3-bits-count + low-5-bits-data format). The doc's `[byte:...]` representation is the visible byte on the wire when only one bit is packed (the rest of the bit-group byte is empty), but architecturally it's a bit-packed field. This matters for clients that read bit-by-bit (correct) vs. byte-by-byte (relies on padding being zero).

### 2. Ship+0x2BC slot identity (cross-doc conflict #4 RESOLVED)

Doc's "Named Slot Layout" line 176: `+2BC  (unused)  NULL  Always NULL`
Doc's "Anti-Cheat Hash" line 205: `Slot 11 +0x40/+0x2BC  Pulse Weapon System`

Ground truth from decompile of FUN_005b5030 (Ship_LinkSubsystemToParent — switches on weapon-type-ID 0x802A subclasses):
- `case 0x802C` (PhaserBank) -> reads `ship+0x2B8` (Phaser parent)
- `case 0x802D` (PulseWeapon) -> reads `ship+0x2BC` (Pulse parent) [700 decimal in decompile]
- `case 0x802E` (TractorBeamProjector) -> reads `ship+0x2D4` (Tractor parent)
- `case 0x802F` (TorpedoTube) -> reads `ship+0x2B4` (Torpedo parent)

So **subsystem-integrity-hash.md is CORRECT** (slot 11 +0x2BC = Pulse). **wire-format-spec.md's Named Slot Layout is WRONG** on TWO rows:

| Row | Doc (wrong) | Correction |
|-----|-------------|------------|
| +0x2BC | `(unused) NULL Always NULL` | `Pulse Weapon System (PulseWeaponSystem parent)` |
| +0x2D4 | `Pulse 0x00893794` | `Tractor (TractorBeamSystem parent)` |

The vtable-to-type map at lines 152-167 has correct vtable->class mappings (0x00893794 IS PulseWeapon, 0x008936F0 IS TractorBeam), but the slot column at "+2D4 Pulse" is wrong.

### 3. Subsystem-hash table duplication (cross-doc conflict #5 RESOLVED)

Both wire-format-spec.md (lines 188-208) and subsystem-integrity-hash.md (lines 110-127) carry the same 12-row hash table. Per binary (FUN_005b5eb0), subsystem-integrity-hash.md's table is the more accurate canonical (it explicitly notes Repair is NOT in the hash, and shows the type-specific extras correctly). **Resolution**: subsystem-integrity-hash.md = canonical; wire-format-spec.md keeps a 1-line summary + cross-link.

## Dropped / open

- The doc cites vtable 0x00895340 = ShipRefNiNode at ship+0x2E0. Not verified this pass (not load-bearing for the hub — that row is included for the Sovereign-class inventory illustration, not for protocol dispatch).
- "Validated by JMP detour trace 2026-02-10" provenance lives in the body — move to v5 frontmatter on re-render.

## Completeness scores (cited functions, all sub-baseline; mostly fixable)

| Function | effective_score | classification |
|----------|-----------------|----------------|
| MpgameHandleMessage @ 0x0069f2a0 | **69.84** | named + plated; remaining issues are 2 hungarian-violations + 3 type-quality issues |
| FUN_006a1b10 (ChecksumCompleteHandler / Settings sender) | **0.00** | unnamed; 13 magic numbers, 7 unrenamed globals, 35 undefined types |
| FUN_005b5eb0 (ComputeSubsystemHash) | **0.00** | unnamed; 13 unresolved struct accesses, 2 magic numbers |
| FUN_005b5030 (Ship_LinkSubsystemToParent) | **6.26** | unnamed; 11 unresolved struct accesses, 5 magic numbers (the 0x802A-0x802F class IDs) |
| FUN_005b17f0 (StateUpdate sender) | **0.00** | unnamed; 32 unresolved struct accesses, 31 magic numbers, 15 hungarian violations — 343 lines, the heaviest lift in the protocol family |

These 5 functions are all load-bearing for protocol claims and all below 70.0. None block the hub doc's claims because the verifications used decompile-grounded evidence directly, but the family campaign should lift them over time.

## Cross-doc reference spot-checks (3 PASS)

- "Detail: stateupdate.md" — verified: stateupdate.md opens with "FUN_005b17f0 serializer, FUN_005b21c0 receiver" and covers opcode 0x1C dirty flags. CONSISTENT with hub.
- "Detail: collision-effect-protocol.md" — verified: doc covers opcode 0x15, handler 0x006a2470, C->S only, 138K packets verified. CONSISTENT.
- "Detail: pythonevent-wire-format.md" — verified: doc covers opcode 0x06 + shared 0x0D receiver, FUN_0069f880, polymorphic factory-based. CONSISTENT.

## Globals cross-anchor

All 4 globals referenced in the Settings packet section were verified by `get_xrefs_to`:
- 0x0097fa78 (TGWinsockNetwork ptr) — 5+ READ xrefs from MP/dispatcher code
- 0x008e5f59 (Settings byte 1 / collisionDamage) — WRITE from FUN_00504c70/d30/0069e590, READ from FUN_006a1b10 (the Settings sender) — confirms it's the per-MP setting
- 0x0097faa2 (Settings byte 2 / friendlyFire) — READ patterns match (set by MP setup, read by Settings sender)
- 0x009a09d0 (Clock obj, gameTime at +0x90) — multiple READ xrefs; matches doc claim

## TopWindow drift propagation

wire-format-spec.md does NOT cite 0x0097e238 or "TopWindow" anywhere. Drift finding #2 from protocol-snapshot does NOT apply to this doc.

## Status proposal

`partial` — body claims are mostly accurate, but (a) two named-slot-layout cells need correction; (b) settings-packet wire format needs WriteBit annotation; (c) hash table duplication should be retired in favor of subsystem-integrity-hash.md as canonical. After corrections + v5 frontmatter applied, can move to `verified`.

## Cross-references

- [[protocol-snapshot-20260528]] — anchor table this validation consumed
- [[dispatcher-recovery-20260528]] — MpgameHandleMessage recovery + 41-entry jump table
- [[struct-skeletons-20260528]] — MultiplayerGame + TGMessage + TGBufferStream layouts
- [[tg-hierarchy-vtables-validation-20260528]] — vtable identities for subsystem classes (0x00893794 PulseWeapon, 0x008936F0 TractorBeam — both confirmed independently)
- docs/protocol/v5-validation-status.md — row #1 transitions to validated/partial here
