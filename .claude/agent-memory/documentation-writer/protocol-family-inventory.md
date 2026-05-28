---
name: protocol-family-inventory
description: Observations from the 22-doc protocol-family inventory pass (2026-05-28); reusable for the next family inventory
metadata:
  type: project
---

# Protocol Family Inventory — Observations

Inventoried 22 protocol docs on 2026-05-28 for the v5 re-validation campaign. Notes for the next family (likely networking) and for the protocol per-doc passes.

**Why:** The engine campaign provided strong cross-anchors that the protocol family inherits; without recording which engine anchors the protocol family leans on, the per-doc passes will redo work.

**How to apply:** Before starting a protocol per-doc validation pass, check the protocol tracker's §5 (cross-family disagreements) and §7.1 (engine-inherited anchors). When starting the next family (networking, gameplay), spend the first inventory pass identifying which protocol-family anchors that family leans on.

## Voice/structure choices that worked

- **Foundation→leaves order**, even with 22 docs, works fine: 3 foundations (wire-format-spec, stream-primitives, transport-layer), 10 mid-tier (opcode tables + state-update + obj-create chain + event class), 9 leaves (per-opcode + analyses). Map each leaf to its mid-tier dependency.
- **Anchor table §7 with sub-tables by category**: §7.1 engine-inherited, §7.2 globals, §7.3 opcode handlers, §7.4 stream primitives, §7.5 transport/routing, §7.6 stateupdate/objcreate, §7.7 event-class factories, §7.8 event-type constants. The engine tracker had 8 anchor sub-tables; protocol has 8 too. This is the pattern.
- **Cross-family disagreements §5 as its own section** rather than rolled into §4 (cross-doc within family). Lets the engine tracker stay the authoritative source for engine claims, with disagreements explicitly named.

## Documentation debt discovered (forwarded to per-doc validation)

The five highest-leverage items, all of which surfaced in the inventory and warrant explicit follow-up:

1. **`FUN_005a2030` semantics conflict** (objcreate-serialization.md vs objnotfound-requestobj-enterset.md) — Two docs claim different functions at the same address. One is wrong.
2. **`ship+0x2BC` slot identity conflict** — wire-format-spec slot map vs subsystem-integrity-hash slot table.
3. **TGEvent vtable slot count drift** — engine event-system-architecture vs pythonevent-wire-format vs collision-effect-protocol disagree (14 vs 16 vs 18 slots).
4. **CF16 doc overlap** (cf16-precision-analysis.md vs cf16-explosion-encoding.md) — full duplication of algorithm, constants, scale table, mod round-trip.
5. **Two duplicate subsystem-hash tables** (wire-format-spec.md vs subsystem-integrity-hash.md) — make subsystem-integrity-hash canonical.

## Protocol-specific patterns

- **Many protocol docs already self-claim "VERIFIED" / "HIGH-CONFIDENCE"** in their bodies without v5 frontmatter (stateupdate-subsystem-wire-format.md, per-ship-subsystem-wire-format.md, delete-player-ui-wire-format.md). On re-validation, move provenance to frontmatter and demote the body's "VERIFIED" claim until v5 evidence is recorded.
- **External-corpus claims are denser than in the engine family** — Python script paths (`Multiplayer/SpeciesToShip.py`, `MissionShared.py`, `Mission1.py`) and packet-trace observations (`30,000+ packets verified`, `Battle of Valentine's Day 33.5min`) appear constantly. The cross-source two-tag convention (`[v5-validated]` vs `[cross-source-YYYY-MM-DD]`) from the engine campaign extends directly.
- **Some docs are very thin** (object-replication.md = 1,050 bytes, with only 6 claims) — candidates for merger into a richer sibling. Don't preserve thin docs just because they exist.
- **Trace-derived counts** (e.g., "84 CollisionEffect per 15-min", "10,459 C→S StateUpdate packets") should be `confidence: medium` and cited with the trace date.

## What did NOT work / would change next time

- The engine tracker's per-doc inventory used ~10 lines per doc. The protocol tracker uses ~15 lines per doc because docs are larger and more cross-linked. This is fine but pushes the tracker past 700 lines — consider splitting per-doc sections into a separate "inventory" sub-doc if a future family has 30+ docs.
- I batched all 22 doc reads in 4 parallel pairs. Could have done 22 reads in fewer batches with more parallelism, but the docs include 30K+ byte files that hit the 25K-token Read cap. Read order: foundation → mid → leaf and check token budget when batching.

## Cross-family handoff to networking

The protocol tracker's §7.1 lists 17 engine-inherited anchors. The networking family will inherit many of these PLUS the protocol-family-new anchors (transport factory table @ 0x009962d4, AlbyRules cipher key, peer struct offsets at +0x98/+0xA8, sequence counters). When starting the networking inventory, the equivalent of §7.1 should be **two** rows: engine-inherited and protocol-inherited.
