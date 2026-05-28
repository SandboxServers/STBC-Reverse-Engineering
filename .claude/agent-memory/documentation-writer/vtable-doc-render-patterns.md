---
name: vtable-doc-render-patterns
description: Rendering patterns for NI/TG vtable docs — multi-vtable address reassignment, two-stage construction, GetRTTI cross-check, vtable size vs object size disambiguation
metadata:
  type: feedback
---

When rendering vtable reference docs (netimmerse-vtables.md, tg-hierarchy-vtables.md style), four patterns recur. Use them.

## Pattern 1 — Vtable address reassignment ("the doc had the wrong class")

When the evidence packet reports "the prior doc claimed vtable X belonged to class A; it actually belongs to class B" (e.g., the netimmerse-vtables.md pass where `0x00899264` was reassigned from NiTriShape to NiTriBasedGeom):

- The corrected row in the Vtable Addresses table needs the **new** class name and **address unchanged**.
- Add a body NOTE at the top of the affected vtable section: "> **Renamed from "X" in the prior doc revision.**"
- A new vtable row for the actually-canonical class B (e.g., NiTriShape at `0x00899374`) is added.
- The Constructor Chain diagram needs the new intermediate inserted explicitly — don't just rename, show the parent→intermediate→derived chain.
- The Inheritance Accounting bullets need updating: counts that were attributed to the wrong class need to be split between the intermediate and the canonical derived class.
- In the v5 NOTE block at top of doc, name the correction explicitly: "The major correction this pass: X's canonical vtable is at A, NOT B." Readers searching for "0x00899264" should land on the corrected story immediately.

**Why:** vtable misidentification is high-stakes — downstream docs (gamebryo-cross-reference, tg-hierarchy-vtables, decompiled-functions) cite vtable addresses by class. Leaving the body ambiguous about the reassignment causes the next reader to re-derive the same correction.

## Pattern 2 — Two-stage construction (intermediate ctor + derived factory overwrites)

NI 3.1 idiom: an intermediate base-class constructor writes a vtable; then the derived factory overwrites it with the canonical runtime vtable. This is **not** the same as a normal C++ vtable write chain — those write progressively more-derived vtables in order. Here, the intermediate vtable is **transient** — it exists only on the stack during construction.

Render this with:
- A standalone "Two-Stage Construction Pattern" section, 2-3 paragraphs.
- Cite both addresses (the intermediate that gets written, and the final that overwrites).
- The Constructor Chain diagram uses an explicit `-> OVERWRITES with` arrow for the final write.
- The intermediate vtable's own section gets a paragraph noting it is "transient at runtime" and naming where it lives (only while the inner ctor is on the stack).

**Why:** A reader observing only the intermediate ctor would conclude (incorrectly) that the intermediate vtable is the runtime vtable. The render must call this out — otherwise the reader trying to compute "what vtable does my object have?" gets the wrong answer.

## Pattern 3 — GetRTTI cross-check as the canonical identity test

For ambiguous vtable identification, the canonical test is:

1. Look at the vtable's slot 0 (GetRTTI stub).
2. The stub is `mov eax, IMM ; ret` where IMM is the NiRTTI ptr storage address.
3. Cross-check which game-code addresses xref that NiRTTI ptr storage.
4. The class with the most game-code xrefs (especially in the 0x004xxxxx-0x006xxxxx range) is the canonical runtime class.

This is how netimmerse-vtables-validation-20260528.md confirmed `0x00899374` is NiTriShape and `0x00899264` is NiTriBasedGeom — by following slot 0 to its NiRTTI ptr storage and counting xrefs.

When rendering, surface this in the Methodology section so future validators can apply the same test. Example phrasing:

> **GetRTTI cross-check** (correction methodology): Each GetRTTI stub returns a NiRTTI ptr storage address (`mov eax, IMM ; ret` pattern). Cross-checking which game-code addresses xref each NiRTTI ptr storage identifies the canonical runtime type.

## Pattern 4 — Vtable size vs object size disambiguation

These get confused. Disambiguate explicitly:

- **Vtable size** = slot count × 4 bytes. This is what the "Size (bytes)" column means in the main Vtable Addresses table.
- **Object size** = the byte count allocated by the factory (`NiAlloc(N)`). This is what the Object Sizes table at the bottom means.

When the two tables disagree (e.g., NiAVObject's `0x9C` vtable vs `0xC4` object), don't just leave them sitting in opposition. Add a one-line clarifier:

> **Vtable size vs object size**: the "Size (bytes)" column above is the **vtable** size (slot count × 4). For **object/instance** sizes, see [Object Sizes] below — they measure different things and will not match.

For abstract bases (no factory allocation), the object size is **derived from constructor field-write offsets** and carries `confidence: medium`. Tag every Object Sizes row with its confidence — high (factory-confirmed) or medium (ctor-derived).

**Why:** A reader sees two numbers, assumes one is wrong, picks one at random, and propagates the wrong answer to their re-implementation. Naming what each table measures resolves the disagreement.

## Documentation debt convention for vtable docs

When a vtable has N slots but only M are individually decompiled (N >> M), the doc reaches `verified` if:

- The N - M slots carry `confidence: medium` by inheritance pattern.
- The top-of-doc NOTE block calls out the ratio: "12 of 238 slots are v5-validated; the other ~226 are pattern-extrapolated."
- The Open Questions section names "per-slot decompile sweep" as the promotion path.
- Specifically v5-validated slots in each per-class table carry the `[v5-validated YYYY-MM-DD]` tag inline.

See [[verified-status-criteria]] for the underlying rule (catalog docs reach `verified` with documented extrapolation).

**Related:** [[verified-status-criteria]], [[v5-foundation-claim-patterns]], [[catalog-row-disposition-tree]]
