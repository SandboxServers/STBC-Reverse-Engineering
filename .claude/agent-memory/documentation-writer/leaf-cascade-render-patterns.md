---
name: leaf-cascade-render-patterns
description: 7 patterns for rendering FIRST-leaf protocol docs when v5 cascade from mid-tier flips inheritance hierarchy + introduces source/dest encoding asymmetry + receiver-name correction + in-memory-vs-wire-size disambiguation
metadata:
  type: feedback
---

# Leaf-cascade render patterns (protocol leaf #14, pythonevent-wire-format.md)

**Why:** First leaf in the protocol family. Cascade from mid #13 (tgobjptrevent-class)
flipped a class-identity claim that propagated to **multiple sibling classes** in
the leaf doc. Also introduced an encoding asymmetry (source vs dest) and a
receiver-flow function-name correction. 5 corrections, 0 wire-format byte-count
changes. Doc went from 696 to ~1000 lines (more cross-anchor framing) but stayed
the same shape.

**How to apply:** When you receive a leaf evidence packet that says "cascade from
mid X" + "wire formats all byte-by-byte clean," lead with the cascade headline
in the NOTE block, then walk each correction in order. Wire formats are a quick
table; the *narrative* corrections are what need new sections.

## Pattern 1: Two-producer not three-producer

Pre-v5 doc named THREE producers (HostEventHandler / ObjectExplodingHandler /
GenericEventForward). Validation determined GenericEventForward is NOT a producer
of opcode 0x06 — it writes opcodes 0x07-0x12 + 0x1B. Renamed section from "Three
Producers" to "Two Producers" and moved GenericEventForward into the receiver
section (Path 2). When a pre-v5 doc conflates producers across opcodes, the count
itself becomes a correction.

## Pattern 2: Sibling cascade in inheritance correction

When mid-tier flips a class-identity claim (here: "0x101 is NOT TGSubsystemEvent;
it IS TGEvent base"), the cascade applies to **every sibling that inherited from
that fabricated class**. In this doc: TGCharEvent, TGObjPtrEvent, AND
ObjectExplodingEvent all had to be reframed as direct children of TGEvent base.
The corrected hierarchy diagram becomes a 3-sibling flat tree, not a 2-level tree.

## Pattern 3: IsA chain row gets a Confirmed-At column

Cascade verification: each sibling's `IsA` function was disassembled to confirm
it returns true for 0x101 (the parent). Create a 4-row table (one per class)
with columns: Class / IsA returns true for / Confirmed at. The 0x101 column is
the cascade evidence — it's how you PROVE the inheritance instead of asserting
it from a class-name.

## Pattern 4: Source-vs-dest encoding asymmetry callout

When a single function in a leaf does NOT apply a uniform encoder to two
ostensibly-symmetric fields, the doc must:
- Replace any "WriteX encoding rule" prose with a 2-row table (one row per field)
- Add a "Practical impact" line explaining whether the asymmetry shows up in
  observed traffic
- Cite the disasm address ONCE in the table caption — both rows pivot off the
  same function

Pattern row format: `| Field | Offset (in-memory) | Cases | Wire encoding |`

## Pattern 5: In-memory vs wire-size disambiguation block

When a class has both an in-memory size (e.g., 0x30 = 48 bytes) AND a wire size
(e.g., 25 bytes including opcode), the pre-v5 doc usually conflates them. The
v5 fix is a short disambiguation block at the top of the class section with
both numbers labeled:

> - **In-memory class size**: `0x30` bytes (48 in decimal) — includes [breakdown]
> - **Wire payload size**: 24 bytes — [breakdown]. Add the 1-byte opcode for
>   **25 bytes total on the wire**.

This separates "what the C++ class size is" from "what travels over UDP". The
breakdown forces both numbers to add up consistently.

## Pattern 6: Receiver-flow function-rename inline note

When a function previously cited by name approximation (e.g.,
`EventManager::PostEvent`) is renamed to a more accurate name based on its
disassembly (`TGEvent::Dispatch` because it reads event->dest_obj and invokes
dest_obj->vtable[+0x50]), embed the rename **inline at the step** in the
pseudocode AND add a "what X actually does" paragraph right under the
pseudocode block. Don't make readers chase the disasm:

> **Step 7 — what TGEvent::Dispatch actually does (C4 correction)**:
> `FUN_006DA300` reads `event->dest_obj` (this+0x0C) and invokes
> `dest_obj->vtable[+0x50](event)`. This is **event self-dispatch via the
> event's dest object**, not a global event manager `PostEvent`. The pre-v5
> doc named this function `EventManager::PostEvent` based on its caller
> pattern, but the disasm shows it's calling through the event's own
> `dest_obj` vtable — much narrower in scope than the name suggests.

## Pattern 7: Stream-vtable slot-map appendix near doc end

Wire-format docs benefit from a dedicated "Stream Vtable Slot Map" section
near the end that:
- Lists the slot table (slot offset / address / method / byte cost columns)
- Maps each slot back to the wire-format extension(s) it generates
- Explicitly disclaims any virtual-dispatch indirection (e.g., "+0x80 thunks
  through to +0x68 in this SWIG class")

This addresses the common reader question "why does the producer call +0x6C and
not +0x84?" without making them grep the vtable themselves.

## Pattern 8: Producer-undefined-in-DB disclosure (extended from netimmerse pattern)

When raw disasm works but `decompile_function` fails (annotation script gap), use
this row format in the function-actions table:

> | Action | Address | Symbol | Notes |
> |--------|---------|--------|-------|
> | (none) | 0x006A1150 | `LAB_006A1150` (undefined in DB) | Confirmed via raw disasm only |

And mention in the producer section heading that the function is undefined in
DB but the raw disassembly walks cleanly. This explains why `completeness:`
is `null` for those evidence rows.

## Pattern 9: TGEvent vtable slot-count conflict NOTE

Three docs cite three different slot counts for the same TGEvent base vtable
(14 / 16 / 18). When this kind of cross-doc disagreement is documented in the
tracker §4 but not yet resolved, embed a `> [!NOTE]` block under the vtable
table flagging the issue, naming the tracker section, and downgrading specific
slot rows to `confidence: low` in the body. Do not silently pick one count.

## Key learning for future protocol leaves

When the cascade headline is "pre-v5 named a class that doesn't exist":
1. Re-derive the hierarchy diagram from the IsA chains of each known sibling
2. Verify by checking GetFactoryID disasm at the base (single MOV-EAX instruction)
3. Verify by checking vtable address xrefs — fabricated classes have ZERO xrefs
4. Cascade the rename to every sibling's IsA chain (each one gains a row)

Time budget: a hierarchy cascade in a leaf is ~20% of the doc rewrite. The
rest (sections that were already correct) is mechanical tagging with
`[v5-validated 2026-05-28]`.
