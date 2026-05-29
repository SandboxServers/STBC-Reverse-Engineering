---
name: protocol-family-campaign-close
description: Protocol family v5 campaign closed 2026-05-28 at 22/22 docs validated. 4 verified, 18 partial, 0 disputed/stale. Cross-doc disagreement table partial resolution. Family-close batch follow-ups deferred.
metadata:
  type: project
---

# Protocol family v5 campaign close — 2026-05-28

**The protocol family (`docs/protocol/`) is fully v5-validated as of 2026-05-28.** All 22
docs carry v5 frontmatter, cross-anchored evidence rows, and NOTE-block change summaries.
Campaign ran ~Feb 26 to May 28, 2026; closed simultaneously with engine cross-source pass.

## Why: Why does it matter that this campaign closed?

Future doc work in `docs/protocol/` should treat foundations (#1 wire-format-spec, #2
stream-primitives, #3 transport-layer) as fully anchored — new leaves can lean on these
addresses without re-deriving. The 4 `verified` docs (#15, #16, #20, #21) are also durable
anchors. The 18 `partial` docs have known minor body-restructure work tracked in their §6.N
tracker entries but no unresolved evidence.

## How to apply

- **New leaf docs in `docs/protocol/`** — lean on the foundation anchors (dispatcher
  `0x0069F2A0`, jump table `0x0069F534`, TGMessage vtable `0x008958d0`, TGEvent vtable
  `0x00895FF4`) without re-citing the primary source unless your claim is new.
- **Cross-family work** — the protocol family is one of two families fully validated
  (engine being the other). Networking family next; lean on transport-layer.md and
  python-messages.md for boundary cases.
- **Family-close batch follow-ups still pending** (deferred from 2026-05-28):
  1. **CLAUDE.md Documentation Index protocol section refresh** — add `[v5-validated
     2026-05-28]` annotation to all 22 entries matching the engine-family pattern.
  2. **`docs/protocol/README.md`** — refresh entries to reflect v5 status (the campaign
     close banner was added 2026-05-28 but per-row freshening not done).
  3. **OpenBC clean-room cascade** — review 9 OpenBC clean-room wire-format specs against
     validated BC-side docs; especially the CF16 explosion 14-byte wire frame (was
     `~7-byte CV4` pre-v5 — corrected to 5-byte CV4 with CF16 magnitude).
  4. **§4 leftover disagreements** — schedule a light reconciliation pass for the 11
     unresolved §4 rows.

## Status distribution

- **`verified` (4 docs):**
  - #15 collision-effect-protocol (leaf, opcode 0x15)
  - #16 set-phaser-level-protocol (leaf, opcode 0x12)
  - #20 cf16-precision-analysis (leaf analysis)
  - #21 cf16-explosion-encoding (leaf analysis)

- **`partial` (18 docs):**
  - **Foundations (3):** #1 wire-format-spec, #2 stream-primitives, #3 transport-layer
  - **Mid-tier (10):** #4 game-opcodes, #5 checksum-opcodes, #6 python-messages, #7
    tgmessage-routing, #8 stateupdate, #9 object-replication, #10 objcreate-serialization,
    #11 stateupdate-subsystem-wire-format, #12 per-ship-subsystem-wire-format, #13
    tgobjptrevent-class
  - **Leaves (5):** #14 pythonevent-wire-format, #17 delete-player-ui-wire-format,
    #18 objnotfound-requestobj-enterset-wire-format, #19 subsystem-integrity-hash,
    #22 message-trace-vs-packet-trace

- **`pending` (1):** README.md (index doc — refreshed at family-close commit, not a content doc)

## Cross-doc disagreements (§4) resolved in campaign

8 of 19 rows closed during the campaign: #1, #4, #5, #8, #13, #14 (backlog noted), #15,
plus partial closure on others via foundation reconciliation. New OQs added: #19 (CF16
5th caller identity), #20 (Python-message label drift), #21 (0x0D re-emit path).

## Canonical anchors (for future leaf docs)

These are the most-cited anchors across the protocol family — use them by reference:

| Anchor | Address | Source doc | Use for |
|--------|---------|-----------|---------|
| MultiplayerGame dispatcher | 0x0069F2A0 | game-opcodes.md | every game opcode handler |
| 41-entry jump table | 0x0069F534 | game-opcodes.md | opcode-to-handler mapping (opcode-2 indexed) |
| TGMessage base vtable | 0x008958d0 | transport-layer.md | every TGMessage subclass |
| TGEvent base vtable | 0x00895FF4 | pythonevent-wire-format.md | every event subclass |
| TGFactory registry | DAT_0099a578 / DAT_0099a584 | delete-player-ui-wire-format.md | TGEvent factory IDs (0x801, 0x865, 0x866, 0x867 confirmed) |
| Transport factory table | DAT_009962d4 | transport-layer.md | 7 transport types; type 0x32 → FUN_006b83f0 |
| Ship_WriteStateUpdate | 0x005B17F0 | stateupdate.md | dirty-flag emit gate; SUB/WPN direction-exclusivity |
| TGEventManager singleton | 0x0097F838 | event-system-architecture (engine) | event re-post pattern |
| TGBufferStream vtable | 0x008958D0 (engine) | stream-primitives.md | bit-pack write/read |

## Patterns demonstrated in this campaign

- **address-first authoring** (foundations) — each per-function entry leads with hex
- **two-tag convention** — `[v5-validated YYYY-MM-DD]` for stbc.exe + `[cross-source-YYYY-MM-DD]`
  for trace / corpus material
- **cascade-correction NOTE block** — leaf doc cites originating doc when a v5 correction
  cascades downward (e.g. foundation #1 ship+0x2BC slot correction cascaded to leaf #19)
- **two-registry architecture** (leaf #17) — surfaced a MAJOR finding (TGFactory registry
  separate from NiRTTI) that closed foundation OQ #2
- **paired-trace differential analysis** (leaf #22) — canonical example doc for future
  cross-source work

## Cross-references

- [protocol family inventory](protocol-family-inventory.md) — original 22-doc inventory
  (campaign-start view)
- [cross-source leaf render patterns](cross-source-leaf-render-patterns.md) — leaf #22
  render shape (cross-source / paired-trace docs)
- [verified status criteria](verified-status-criteria.md) — when a doc qualifies for
  `verified` vs `partial`
- [v5 foundation claim patterns](v5-foundation-claim-patterns.md) — foundation-tier
  evidence-row patterns
