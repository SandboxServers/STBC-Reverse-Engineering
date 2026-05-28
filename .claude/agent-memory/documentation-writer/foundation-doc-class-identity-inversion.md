---
name: foundation-doc-class-identity-inversion
description: Render pattern for foundation docs where a load-bearing class-identity claim flips during v5 validation, cascading corrections into already-validated companion docs (engine + protocol). Six patterns: NOTE-block headline, dedicated "Two X Classes" preamble section, address-keep-name-flip rule, handler-pattern transcript, dedicated cross-doc reconciliation table near doc bottom, separation of wire-fact (high confidence) from open-question (deferred).
metadata:
  type: feedback
---

# Foundation-doc class-identity inversion (render patterns)

Six render patterns from rendering `docs/protocol/stream-primitives.md` when the v5
validation surfaced that a load-bearing class identity was inverted in prior docs (the
0x30-byte class was the SWIG `TGBufferStream`; the 0x40-byte class previously holding the
name was actually the wire-container). The inversion was the headline of the validation —
not a side correction. The patterns below are what worked.

## Pattern 1: NOTE-block headline naming the inversion explicitly

The top-of-doc `> [!NOTE]` block lists what's v5-validated first (so the doc still reads
as authoritative on its core subject), then names the inversion in one sentence using
**bold** for the load-bearing fact. Don't bury the inversion in a Caveats footer — it's
the reason the doc is `partial`.

**Why:** Subsequent readers (clean-room implementers, other doc maintainers) need the
inversion fact within the first screen, not buried in section 7. A reader who skims will
miss a footer.

**How to apply:** Whenever a foundation doc validation produces a class-identity inversion
that cascades to companion docs, lead the NOTE block with the validated facts, then drop
one bold-faced sentence naming the inversion and pointing at the reconciliation table.

## Pattern 2: Dedicated "Two X Classes" preamble between intro and primitives

When two classes are *commonly conflated* (same prefix in vtable address, similar role,
similar Ghidra naming history), don't try to handle them inline in the primitive tables.
Open a dedicated subsection right after the one-paragraph intro, with one table or two
narrative blocks per class. Cover for each: ctor address, sizeof, vtable, role,
identity-proof sentence (SWIG wrapper, vtable behavior, etc.).

Close the subsection with a handler-pattern code transcript that names **both classes by
role** ("class B is passed in, class A is constructed over class B's buffer"). The handler
pattern is what proves they're distinct AND lets the reader see how they fit together.

**Why:** A primitives table that conflates two classes will be silently wrong even if every
row's address is right (because the reader doesn't know which class the slot belongs to).
The preamble disambiguates once so the rest of the doc can stay terse.

**How to apply:** Pre-condition is "doc has been described as `partial` because of a
class-identity conflict". The preamble goes immediately after the lead paragraph and
before any layout/primitive table.

## Pattern 3: Address-keep, name-flip rule

When the inversion is "we had the address right but the class name wrong", the right cascade
strategy is **keep all the addresses, flip just the names in the dependent doc rows**. Do
NOT remove or move rows. Phrase the cross-doc reconciliation as "name should change to the
[other class]'s real identity" — the addresses stay in the engine vtable maps; just the
labels need rework when the open-question identity is resolved.

This is important because:
- Removing rows from a cross-referenced foundation doc breaks downstream anchors.
- "Re-attribute the row when the open question resolves" is a precise instruction the
  next maintainer can act on.

**Why:** Address-keep / name-flip lets the validation be batched at family-close without
breaking any inbound links in the meantime.

**How to apply:** Cross-doc reconciliation tables should list (a) the doc, (b) the current
load-bearing claim, (c) a specific "re-attribute on next pass" or "wait for resolution of
open question N" action. Never "drop this row".

## Pattern 4: Handler-pattern transcript with both class roles labeled

Pseudocode like the CollisionEffectHandler example below proves the two classes are
distinct AND shows how the cursor class operates on the container class's buffer:

```
pBuf = TGBufferStream_GetBufferAndSize(pStream_classB, &len)   // Class B accessor
FUN_006CEFE0()                       // construct stack-local Class A
FUN_006CF180(pBuf + 1, len - 1)      // OpenBuffer Class A on Class B's buffer, skip opcode
... use Class A primitives to read typed payload ...
FUN_006CF120()                       // destruct stack-local Class A
```

The labels "Class A" / "Class B" tied to specific addresses are what carry the disambiguation
forward. Don't use the actual class names in the transcript (the wire-container's true name
is the open question) — use roles + addresses.

**Why:** This is the smoking-gun proof a reader can verify themselves by decompiling the
named handler. It's also the pattern future leaf docs need to reproduce.

**How to apply:** Pick one well-understood handler (CollisionEffectHandler was perfect —
it's already v5-documented in `collision-effect-protocol.md`) and render the transcript.
Cross-link to the handler's own doc so the reader can verify against the real decompile.

## Pattern 5: Dedicated "Cross-doc Reconciliation Required" section near doc bottom

A single table named "Cross-doc Reconciliation Required" placed just before the
Open-Questions section. Three columns: doc path, current claim, reconciliation action.

This is distinct from a normal "See also" list — it's an explicit work-tracker telling the
next validator which docs need cascade corrections that this validation pass did NOT
make. The tracker §6.2 entry references this table.

**Why:** Otherwise the cascade work gets lost. A "See also" link reads as "these are
related"; a "Cross-doc Reconciliation Required" table reads as "these are work items".

**How to apply:** Use whenever a foundation-doc validation surfaces cascade corrections that
intentionally defer to a batch close (family-close, OpenBC-merge, etc.). Cross-reference
the tracker section where the impacts are also logged.

## Pattern 6: Separate the wire-fact (high confidence) from the open-question (deferred)

The CV3 correction (CV3_Write produces a magnitude that CV3_Read doesn't consume) was
**not** allowed to become a fuzzy hedge in the doc body. The wire fact ("CV3 = 3 bytes,
direction-only") is stated cleanly in bold; the open question ("why does the writer
produce a magnitude?") moves to a dedicated `> [!NOTE]` block AND to the Open Questions
list at the end.

**Why:** Mixing the high-confidence fact with the open-question hedge in the same paragraph
makes both look unreliable. Separating them lets the wire fact stand authoritative.

**How to apply:** Whenever the validation produces both (a) a clean wire-format
correction and (b) a residual mystery, render them in two different doc surfaces. Bold
sentence for the fact; NOTE block + Open Questions row for the mystery.

## When this whole pattern doesn't apply

Apply only when validation surfaces a *class-identity* inversion (or analogous
load-bearing-identity correction — e.g., "we thought this was global G1 but it's G2").
Routine address corrections (single-row updates, slot-map swaps, magic-number changes)
use simpler patterns (the IMPORTANT block from protocol-hub-doc-render Pattern 5, or the
two-row disambiguation from load-bearing-correction-disambiguation).
