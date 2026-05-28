---
name: tg-vtable-render-patterns
description: TG-hierarchy vtable doc patterns — purecall reclassification, universal slot inheritance call-out, type-ID constants table, sibling cross-link section
metadata:
  type: feedback
---

Patterns specific to rendering the TG hierarchy vtable doc (tg-hierarchy-vtables.md) that complement the more general [[vtable-doc-render-patterns]].

## Pattern 1 — `__purecall` reclassification (NOT "NULL stub")

The MSVC `__purecall` stub at `0x00859a0b` (bytes `6A 19 E8 69 13 00 00 59 C3` = `push 0x19 ; call __purecall_thunk ; pop ecx ; ret`) appears in **both** TGObject (slots 5/6/7) and NiGeometry (slot 49). Prior docs labeled it "NULL stub" — that is misleading because:

- NULL stub implies a no-op that returns successfully — readers may assume the base implementation does nothing meaningful.
- `__purecall` is the pure-virtual placeholder — calling it crashes with the purecall thunk, which is what you want when a derived class **must** override.

When rendering, always say "MSVC `__purecall` stub (pure-virtual placeholder)" and cite the byte sequence. Cross-anchor across docs — if NiGeometry slot 49 is cited in netimmerse-vtables.md, the TGObject doc should cross-link there for the same stub.

**Why:** Readers writing OpenBC re-implementations need to know which slots are abstract (must implement) vs which slots have no-op base implementations (optional override). "NULL stub" is ambiguous between the two.

## Pattern 2 — Universal slot inheritance call-out (slot 3 + slot 8)

When a slot is inherited unchanged across **all** classes in the hierarchy, surface it in three places:

1. The per-class slot table: "inherited unchanged across all 9 hierarchy vtables".
2. The class type-ID / universal slot section near the top.
3. The Methodology section — explain what the verification was ("verified that all 9 vtables show 0x006f1650 at offset +0x0C").

In TG hierarchy: slot 3 (DebugPrint at 0x006f1650) and slot 8 (InvokePythonHandler at 0x006f15c0) are universal across all 9 vtables in the Ship chain. This is load-bearing for OpenBC — knowing a slot is universal means the implementer only needs to write it once in the base class.

**Why:** Inheritance patterns determine implementation effort. Universal-inheritance slots are write-once; per-class-overridden slots are write-N-times.

## Pattern 3 — Class Type-ID Constants table

When slot-1 GetTypeID stubs follow a uniform `mov eax, IMM ; ret` pattern, surface the IDs as their own table:

| Class | Type ID | GetTypeID Addr |
|-------|---------|----------------|
| TGObject | 0x02 | 0x006f0b60 |
| TGStreamedObject | 0x03 | 0x006f31c0 |
| TGEventHandlerObject | 0x0102 | 0x006d8fb0 |
| TGSceneObject | 0x8002 | 0x00430950 |

Mark it "incomplete — extend as more classes sampled" and flag the bit-field-semantics open question (low byte = sub-class, high byte = domain). This table becomes its own catalog candidate when extended.

**Why:** Type-ID constants are wire-format-adjacent. TGBufferStream's wire tag `0x32` and class-runtime type IDs likely share a numbering scheme; surfacing the pattern early invites cross-cataloging.

## Pattern 4 — "Sibling TG Classes" cross-link section

The TG vtable doc should not pretend the Ship chain is the only TG hierarchy. List sibling classes that exist outside the chain:

- TG classes registered with NiRTTI (TGDimmerController, TGFuzzyTriShape) — cross-link to nirtti-factory-catalog.md.
- TG classes with bare strings but NOT NiRTTI-registered (TGOverlayController) — flag as using a different runtime-type mechanism.
- TG classes with their own type-tag mechanism (TGBufferStream's 0x32 tag) — cross-link to netimmerse-vtables.md precision dig.

Render this as a short list with one-line descriptions and companion-doc links. Do NOT try to document their vtables here — that's scope creep.

**Why:** Readers coming to the doc for "what TG vtables exist?" need to know the Ship chain isn't exhaustive. Without this section they'd assume any TG class follows the TGObject layout, which is wrong for sibling families.

## Pattern 5 — Zero-xref negative claim format

When a prior doc identified address X as class Y's vtable, but X has ZERO xrefs (no constructor writes it), the negative claim format is:

```
> **X is NOT Y's vtable.** `get_xrefs_to(X)` returns ZERO references — no constructor writes
> that address; it is not a runtime class vtable. The prior speculation about [old identity]
> is unsupported and should be dropped. Likely [orphan .rdata / linker artifact / unused
> data].
```

Then keep a one-line "CORRECTED from X — that was wrong" historical grep marker for readers searching for the old address.

**Why:** Negative claims need explicit evidence-of-absence — "no xrefs" is the strongest form. Without this readers may resurrect the old misidentification.

**Related:** [[vtable-doc-render-patterns]], [[verified-status-criteria]], [[v5-foundation-claim-patterns]]
