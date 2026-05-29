---
name: gameplay-leaf-16-repair-event-ids-render-patterns-20260528
description: Render patterns for gameplay leaf #16 (repair-event-object-ids.md) — first gameplay doc to reach `verified` via 0-wire-correction + 4-cosmetic-clarification triage. Single-writer global counter proof pattern.
metadata:
  type: project
---

# Gameplay Leaf #16 — repair-event-object-ids.md render patterns (2026-05-28)

Validated 2026-05-28 against game-archaeology-specialist memo
`gameplay-leaf-repair-event-ids-validation-20260528.md`. Doc went from no-frontmatter (pre-v5)
to `status: verified` based on zero wire-format / mechanism / address corrections + 4 cosmetic
clarifications.

## Status decision: verified (not partial)

The 4 clarifications were all **cosmetic and non-wire**:
- Clar-1: stale ASCII comment label ("TGSubsystemEvent" — fabricated class name)
- Clar-2: stale "NOT in DB" annotation (HandleHitEvent IS in DB now)
- Clar-3: dead stack arg disclosure (RET 0x8 quirk; no wire effect)
- Clar-4: variant registration fn for 1 of 7 handlers (likely different handler-type ADT)

None of them change wire bytes, gates, or mechanism. Memo verdict was "ROCK SOLID". The
`partial` shape is for cases where something material changed; here only doc-text drift was
cleaned up. Compare against ack-outbox-deadlock.md which also reached `verified` with 4
address-precision clarifications and zero mechanism changes — same shape.

**Rule:** if all v5 corrections are non-wire cosmetic (stale annotations, dead-arg
disclosure, naming carryover, signature ABI shape) AND the memo verdict is "ROCK SOLID" or
equivalent, `verified` is the right status. `partial` shape is for cases where a body
section needed material rework.

## Render patterns (P1-P7)

### P1 — Single-writer global counter proof subsection

When a doc traces an ID/counter origin, add an explicit "Single-Writer Global Counter Proof
Pattern" subsection that names the `get_xrefs_to` result and asserts no other writer exists.
For DAT_0095b078 the result was exactly 4 xrefs (3 reads + 1 write, all from the same
function). This is the canonical proof pattern for ID-origin questions.

Place the subsection directly under the function-level ID-assignment code block, NOT in a
separate "Pattern Notes" appendix. Readers asking "where does this ID come from" need the
proof inline at the point of evidence, not in a footnote.

Add a top-tier evidence row in frontmatter:
```yaml
  - claim: "DAT_0095b078 — sole producer/consumer is TGObject_Ctor itself (4 xrefs total: 3 READs + 1 WRITE, all from FUN_006f0a70). Single-writer global ID counter, proven by get_xrefs_to."
    address: null
    confidence: high
    note: "canonical single-writer proof pattern — no other writer exists in stbc.exe"
```

`address: null` here because the claim is about a data symbol's xref topology, not a code
anchor. The note explains why null is acceptable.

### P2 — Constructor chain via vtable trail disclosure

When validating a 7-step (or N-step) constructor inheritance chain via vtable assignments,
embed the vtable address trail directly under the section header — not in a separate
"verification methodology" paragraph at the bottom.

Pattern:
```markdown
## TGObject Class Hierarchy (Subsystems) [v5-validated 2026-05-28]

All subsystems inherit from TGObject (the base game object class). The full constructor
chain for a RepairSubsystem is byte-confirmed via the vtable trail
`0x00896278 -> 0x008962F4 -> 0x008962A8 -> 0x00896044 -> 0x00892FC4 -> 0x00892D98 -> 0x00892E24`:

[ASCII tree diagram]
```

This anchors the chain in 2 things at once: (a) the function address each step calls (in
the tree), and (b) the vtable address each step assigns (in the trail). Reviewers can
follow either path.

### P3 — Stale-annotation cleanup with NOTE-block disclosure

When a v5 pass finds a "NOT in Ghidra func DB" or similar staleness annotation that's no
longer true, do TWO things:
1. Remove the stale annotation from the body
2. Mention the now-current state in the function description (e.g. "body 0x005658d0-0x005658fe; created during this v5 pass")

AND surface it as a Clar in the top-of-doc NOTE block so reviewers can see why the line
changed. Do NOT silently delete — readers cross-referencing older PDFs/notes need to know
the doc evolved.

### P4 — Fabricated-class-name carryover Clar pattern

When a fabricated class name (e.g. "TGSubsystemEvent" which doesn't exist in the binary)
shows up in an ASCII art comment but the in-body prose already debunks it, the v5 pass
should:
1. Update the ASCII comment to remove the stale label
2. Strengthen the in-body note to cross-reference the upstream v5-validated source (here:
   protocol leaf #13 tgobjptrevent-class.md)
3. Add explicit "There is **no class called X** in stbc.exe" prose
4. Tag the in-body note "(inherited from protocol leaf #N)" so future readers can trace
   provenance

This is a cross-doc cascade pattern — when one doc validates a name correction, all sibling
docs need the same correction. The Clar-1 mention in the NOTE block names the protocol
leaf as the upstream source.

### P5 — Dead stack arg disclosure pattern

When a function's `RET 0x8` pops more args than the function body reads (dead args from
caller), update the signature to show the dead arg with an `unused_dead_arg` parameter
name and a code comment explaining the ABI shape. Don't hide it — OpenBC implementers
need to know the stack effect.

Pattern in body:
```c
void __thiscall AddSubsystemToRepairList(RepairSubsystem *this,
                                          ShipSubsystem *damagedSub,
                                          int unused_dead_arg) {
    // ... function body that never reads unused_dead_arg ...
}
```

AND mention in the prose preamble: "thiscall confirmed via disassembly (ECX=..., EBX=...,
3rd stack arg is a dead `1` literal never read by the callee; `RET 0x8` pops both stack
args)".

### P6 — Handler-registration table with variant-fn column

When a registration table has N handlers but 1 (or a minority) register via a variant
function (e.g. 6 use FUN_006da130 + 1 uses FUN_006da160), ADD a "Registration fn" column
to the table and bold the variant row. Then add a paragraph below the table explaining the
variant is "likely a different handler-type ADT" and flagging follow-up for the
event-system-architecture.md doc.

Pattern:
```markdown
| Address | Handler | Event | Registration fn |
|---------|---------|-------|-----------------|
| 0x005658d0 | HandleHitEvent | SUBSYSTEM_HIT | FUN_006da130 |
| ... 5 more rows with FUN_006da130 ...
| 0x00565cd0 | HandleSetPlayer | SET_PLAYER | **FUN_006da160** (Clar-4) |
```

This makes the asymmetry visible at a glance. The Clar-4 inline tag lets readers jump from
the table directly to the NOTE block explanation.

### P7 — Wire-format byte total in evidence row note

For wire-format claims, include the byte total in the claim text AND the byte breakdown in
the note:
```yaml
  - claim: "SUBSYSTEM_HIT wire format: 21 bytes — [byte 0x06][int32 0x010C][int32 0x0080006B][int32 0][int32 ship_obj_id][int32 subsystem_obj_id]"
    address: null
    confidence: high
    note: "byte-confirmed: opcode 1 + factory 4 + eventType 4 + source 4 + dest 4 + obj_ptr 4 = 21"
```

`address: null` because the wire format is the sum of multiple addresses (TGEvent::WriteToStream
+ TGObjPtrEvent::WriteToStream + HostEventHandler buffer write). The arithmetic in the note
gives reviewers the breakdown without needing to add it up themselves.

For paired wire formats (here SUBSYSTEM_HIT 21B vs ADD_TO_REPAIR_LIST 17B), put both
evidence rows adjacent in the frontmatter so the size comparison is visible. The 4-byte
delta is the obj_ptr field — that's the whole point of TGObjPtrEvent vs TGEvent.

## Frontmatter summary

- 23 evidence rows (1 single-writer proof, 1 hash table, 7 constructor chain, 1 owner ship,
  2 event ctor sizes, 2 setters, 2 WriteToStream, 1 SetCondition, 1 AddToRepairList, 1 send
  gate, 1 HandleHitEvent body, 1 handler registration table, 1 HostEventHandler, 2 wire
  format totals)
- 4 companions: repair-system, damage-system, tgobjptrevent-class, pythonevent-wire-format
- status: verified
- supersedes: []

## Tag density

`[v5-validated 2026-05-28]` appears on 10 section headers — heavy tagging is appropriate
for a doc where every byte sequence and offset is binary-confirmed. Don't dilute by tagging
prose paragraphs; tag the section header and let it cascade to all content under it.

## Body order preserved

No section reordering — original Summary -> TGObject -> TGEvent layout -> Setter -> Wire
format -> Chain -> Answer -> Handler reg -> HostEventHandler -> Key addresses order
preserved. Reader inbound links from companion docs (repair-system.md, damage-system.md)
likely target specific sections; restructuring breaks those.
