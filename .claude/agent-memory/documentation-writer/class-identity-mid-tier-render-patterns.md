---
name: class-identity-mid-tier-render-patterns
description: 7 render patterns for mid-tier class-reference docs when v5 validation surfaces a fabricated-parent-class correction (C1) + vtable slot-numbering correction (C2) + unverified-annotation-address correction (C3) + substantial Ghidra creation work. Learned from tgobjptrevent-class.md (protocol mid #13, last mid-tier of protocol family).
metadata:
  type: feedback
---

# Class-identity mid-tier render patterns

Seven render patterns for rendering `docs/protocol/tgobjptrevent-class.md` (protocol mid
#13, last mid-tier) when v5 validation surfaced (a) a fabricated intermediate class
("TGSubsystemEvent 0x101" did not exist — 0x101 IS TGEvent), (b) a vtable slot-numbering
correction (17 slots, not 12-14; slot 0 is the dtor, slot 11 is a third RTTI method),
(c) annotation-script drift (SWIG wrapper addresses unverified in current Ghidra DB), and
(d) substantial in-pass Ghidra annotation creation (10 functions created, 16 renamed, 1
struct, 6 prototypes, 3 plates).

Distinct from `foundation-doc-class-identity-inversion` (that was the foundation
stream-primitives doc where two classes were inverted *across* docs). This pattern is for
a *mid-tier subclass doc* where the inversion is in the class's *own* hierarchy
description — the doc's subject class is correct; its parent identity is wrong.

## Pattern 1: NOTE-block triage with bold-faced first-sentence correction headlines

The NOTE block leads with what's v5-validated (so the doc reads authoritative on its
subject), then enumerates the three corrections each as a `- **CN — short headline.**`
bullet with the load-bearing fact in the opening sentence. Don't bury the corrections in
prose.

For C1 (fabricated parent class), the opening sentence names the false class **AND** the
true class in the same bold-faced line: "TGSubsystemEvent (0x101) is fabricated. 0x101
IS TGEvent itself." For C2 (slot-numbering off), the headline gives the correct slot
count up front: "Vtable is 17 slots through +0x40, not the smaller count shown
previously." For C3 (unanchored addresses), the headline calls out the affected family:
"SWIG wrapper addresses unanchored."

**Why:** A mid-tier subclass doc gets read by leaf-doc validators (set-phaser-level-protocol,
pythonevent-wire-format) who need the corrections cleanly named. They don't have time to
parse hedged prose.

**How to apply:** For each correction, write one `- **CN — headline.**` bullet then 2-3
sentences of explanation. The headline must be falsifiable (a reader can verify it
against the binary with a single Ghidra query).

## Pattern 2: Dedicated "Class Hierarchy (Corrected)" section with diagram

Place immediately after the Summary table — high in the doc, before any wire-format or
vtable content. The section title MUST include "(Corrected)" so a reader skimming the TOC
sees the inversion was the headline.

Diagram conventions:
- ASCII tree (not Mermaid — these hierarchies are 4-5 nodes; the overhead isn't worth it).
- Root labeled `SWIG "Object" root (factory 0x02)` with a `// no GetFactoryID emitter
  found` comment.
- Each child node carries its `(factory 0xNNN)` and ctor/vtable address.
- Sibling nodes use `├──` and `└──` glyphs to make the sibling relationship visually
  obvious.

Follow the diagram with an **"Evidence that 0x101 is TGEvent itself, not a missing parent"**
subsection that lists 4 falsifiable claims:
1. Byte-pattern hit count (`MOV EAX, 0x101 / RET` → exactly 1 match at FUN_XXX).
2. That function is at slot +0x04 of vtable 0xVVVVVVV.
3. Vtable 0xVVVVVVV is written by `FUN_YYY` (base ctor).
4. String search for the fabricated class name → 0 matches.

The 4-claim falsification list is the load-bearing proof. Without it, the correction
reads as opinion.

**Why:** A mid-tier subclass doc carries the responsibility of being the canonical
hierarchy reference for its sibling classes. The diagram + falsification list is the
artifact future doc maintainers reuse.

**How to apply:** Whenever a class-identity correction surfaces in a mid-tier doc, render
the corrected hierarchy with siblings visible, then prove the correction with 4
binary-anchored falsification claims (byte pattern, vtable slot, ctor xref, string
search). Negative claims (zero string matches) count and should be cited.

## Pattern 3: Sibling-class differentiator table (small, focused)

After the corrected hierarchy, render a small "Key Difference from [Sibling]" table that
shows the doc's subject class side-by-side with its newly-confirmed sibling (TGObjPtrEvent
vs TGCharEvent here). Columns: ctor address, vtable, +0x28 field type, WriteToStream
extension call (stream vtable slot + primitive), wire extension bytes, total wire size,
IsA chain.

The IsA chain row is the *proof* that they're siblings: both end in `0x101 -> 0x02`
(same parent chain). The pre-v5 doc had this table too, but it was framed as
"differences" without showing the IsA chain identity. Adding the IsA chain row makes the
sibling relationship visually trivial.

**Why:** Mid-tier docs are consumed by leaf docs that often want to call out parallel
patterns ("TGCharEvent uses the same approach but with a byte instead of int"). The
sibling table is the artifact those leaf docs cite.

**How to apply:** Sibling-class differentiator tables go *after* the hierarchy diagram
but *before* the layout/wire sections. Include the IsA chain row.

## Pattern 4: Vtable section with new-slot bolding + "NEW this pass" callouts

The 17-slot vtable table is the largest single artifact in the doc. Render conventions:
- Slot column is the integer slot index (0-16).
- Offset column is the byte offset (+0x00 .. +0x40).
- Address column is the function address.
- Function column has the function name OR `(inherited from base)` for inherited slots.
- Notes column carries the **NEW this pass** callout for slots discovered in validation
  (here: slot 11 GetSWIGPtrName, slot 15 size-0x34 dtor).

The slot 11 row carries **bold formatting** on the slot number, offset, address, function
name, and the "NEW this pass" note — four columns visually bolded. This is the load-bearing
new finding from C2.

Slot 8 (universal `InvokePythonHandler`) carries a cross-link to the engine-family doc:
`See [event-system-architecture.md](../engine/event-system-architecture.md)`. The
universal slot pattern is owned by the engine family; the protocol mid-tier doc cites it.

**Why:** Vtable corrections are the most common cascade source — leaf docs use slot
numbers to call slots. Getting the slot table right and visually flagging new slots
prevents downstream miscites.

**How to apply:** When a vtable validation produces newly-discovered slots, bold all four
columns of the new-slot rows and put **NEW this pass** in the Notes column. Cross-link
universal slots (slot 8 InvokePythonHandler in TG events; slot 0 dtor in C++ classes) to
the engine doc that owns them.

## Pattern 5: Universal-pattern callout subsection (SWIG Triple-String)

After the vtable table, render a dedicated subsection for any *universal pattern* the
validation surfaced. Here: the three RTTI string-return slots (GetClassName / GetSWIGName
/ GetSWIGPtrName) shared across TGObjPtrEvent, TGCharEvent, ObjectExplodingEvent.

Format:
- One-paragraph explanation of what the pattern does (SWIG typeinfo negotiation).
- A small table showing the *role* of each slot (what kind of name it returns + purpose).
- A second small table showing the *cross-class occurrence* (one row per class, columns
  for each of the three RTTI string addresses).

The cross-class occurrence table is what proves the pattern is universal — without it
the section reads as a single-class quirk.

**Why:** Universal patterns surfaced in mid-tier docs become foundation knowledge for
leaf docs (set-phaser-level-protocol will reuse this for TGCharEvent). Calling them out
explicitly in a dedicated subsection (not buried in a vtable row note) is what makes
them rediscoverable.

**How to apply:** Whenever validation surfaces a pattern that obviously generalizes
across siblings, render it as a dedicated subsection with (1) what-it-does paragraph,
(2) per-slot role table, (3) cross-class occurrence table. Don't try to explain the
generalization inside the original vtable table — that's how universal patterns get
lost.

## Pattern 6: Ghidra Annotations Applied section with "newly created" subdivision

When validation passes do substantial Ghidra work (here: 10 created + 16 renamed + 1
struct + 6 prototypes + 3 plates), render a dedicated `## Ghidra Annotations Applied
(YYYY-MM-DD)` section.

Subdivisions:
1. **Functions newly created (N)** — table with Address, Name, Reason columns. The
   "Reason" column carries the disclosure that Ghidra had not synthesized the body
   ("Was undefined", "Was 6-byte leaf undefined", etc.). This is what differentiates
   *creation* from *renaming*.
2. **Functions renamed (M)** — table with Old name, New name, Address columns.
3. **Struct created** — single paragraph naming the struct + the application sites.
4. **Prototypes installed (P)** — single sentence listing the sites.
5. **Plate comments installed (Q)** — bulleted list with each address + plate content
   summary.

The disclosure "Ghidra had not synthesized function bodies for several of the small
vtable-slot leaves nor for the network WriteToStream / ReadFromStream — the doc cited
their addresses correctly but the binary database had them as undefined regions" is the
critical context. It explains *why* the previous doc could cite the addresses without
having the bodies — the addresses were correct, but the binary database was incomplete.

**Why:** Annotation work is invisible to readers without an explicit section. The
"Reason" column on newly-created functions is the disclosure that the prior doc was not
wrong — the binary database was.

**How to apply:** Whenever a pass creates more than ~3 functions in Ghidra, render a
dedicated section near the bottom (after the body, before Companions/Open Questions).
The "newly created" subsection is more interesting than "renamed" — list it first.

## Pattern 7: Open Questions section with hypothesis + investigation path

Render `## Open Questions (documentation debt)` as a numbered list. Each entry has:
1. A bold-faced address or anchor identifying the open question.
2. A 1-2 sentence statement of *what* is unknown.
3. A "Suspect:" line with the working hypothesis (testable).
4. A "Requires:" line naming the investigation steps (e.g., "decompile FUN_006d5ec0",
   "re-run annotation script").

For cross-doc dependencies, the entry names the dependent doc explicitly: "Worth
cross-confirming with pythonevent-wire-format.md (leaf #14, pending)".

Order entries by *blast radius*: a question that affects multiple docs goes higher than
a question affecting one doc.

**Why:** Open questions are how documentation debt gets paid. Without an explicit
section, future validators have to grep the body for hedged language. The numbered list
with hypothesis + investigation path is the artifact that turns a future archaeology pass
from "what was unresolved?" into a checklist.

**How to apply:** Every v5 mid-tier doc gets an Open Questions section if validation
left ANY unresolved items, even one. The 4-entry format (anchor, statement, suspect,
requires) is reusable.

## When this pattern bundle applies

Apply when a v5 mid-tier (or leaf) class-reference doc validation produces:
- A fabricated-class correction (parent name wrong), OR
- A vtable slot-count correction with newly-discovered slots, OR
- Substantial in-pass Ghidra annotation creation (>3 functions created).

Don't apply for routine address-only corrections, which use simpler patterns (single
NOTE-block headline + inline tags, no dedicated sections).

## What we didn't need this pass

- Mermaid diagrams — ASCII trees and tables were sufficient. The hierarchy has 4 nodes.
- Footnote-style cross-doc reconciliation tables — this is a mid-tier doc, not a
  foundation doc. The Open Questions section + the tracker §6.13 entry handle the
  cascade. The `foundation-doc-class-identity-inversion` Pattern 5 ("Cross-doc
  Reconciliation Required" table) is for *foundation* docs that drive multi-doc cascades;
  for a mid-tier subclass doc, the cascade is narrower and lives in the tracker.

## Tags I used in the body

- `[v5-validated 2026-05-28]` — applied to every kept section header (Wire Format, IsA
  Chain, Vtable, Class Layout, Vtable DATA References, Dual-Fire Pattern, Host-Only Gate,
  Previous-Target Semantics, Manual-Ctor Pattern, Complete C++ Event Type Catalog).
- `**NEW this pass**` — applied to the slot 11 row in the vtable table and to the
  GetSWIGPtrName column in the SWIG triple-string per-class table.
- `(medium confidence)` — applied as a Markdown column-header annotation on the Python
  API table to flag the SWIG wrapper address demotion.

These three tag types are sufficient for mid-tier reference docs. Don't add more tag
species — readers stop noticing tags after about three.
