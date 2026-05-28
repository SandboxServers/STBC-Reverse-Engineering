---
name: stateupdate-render-patterns
description: Rendering patterns for "zero material corrections" v5 mid-tier docs where the doc was exceptionally accurate (clarifications + Ghidra annotation work only). Learned from stateupdate.md (protocol mid #8, 2026-05-28).
metadata:
  type: feedback
---

The stateupdate.md re-render (protocol family mid #8, 2026-05-28) was the cleanest pass
in the protocol-family campaign so far: ~120 load-bearing claims and **zero material
wire-format corrections**. The doc's authors got the bytes right; the validation pass
contributed Ghidra annotation work (4 renames + 4 plate comments + 82 inline annotations +
56 variable renames) and 5 clarifications that distinguished wire-format from validation-
gate semantics. The render leaned on patterns that fit this specific shape.

## Pattern 1 — "Zero material corrections" headline

When the validation pass produces **zero material corrections** but substantive
Ghidra-side annotation work, the headline in the top-of-doc NOTE block IS that fact.
Lead with it in **bold**, then enumerate what DID happen: function renames in Ghidra,
function creations in Ghidra, the clarifications applied (numbered list).

```markdown
> [!NOTE]
> This doc is `status: partial`. **Zero material wire-format corrections** in this pass -
> all N dirty bits, the algorithm, and the M formats are v5-validated against the current
> Ghidra import (YYYY-MM-DD). The dispatcher F1 at A1, the serializer F2 at A2 (vtable
> slot S2, body B2 bytes), and the receiver F3 at A3 (vtable slot S3) were all v5-
> documented in Ghidra during this validation. F4 at A4 (FormatN) was newly created in
> Ghidra (function entry was missing; address was correct). Five clarifications applied:
> [list]. See [v5-evidence-header.md](...) for the standard.
```

This signals to readers that the doc is high-confidence on the wire format itself; the
`partial` status reflects open questions / low effective_scores, not byte-level
uncertainty.

## Pattern 2 — Function-creation-in-Ghidra disclosure

When validation needs `mcp__ghidra__create_function` to make an existing address
recognizable as a function (the doc was right, Ghidra just hadn't found it), surface
this explicitly:

- In the NOTE block: "F at A was newly created in Ghidra (function entry was missing;
  address was correct)."
- In the body section where F is cited: a "The function at A was an undefined entry in
  the Ghidra import before this validation pass; the doc's address was already correct -
  it was just not recognized as a function. Created and decompiled this pass."
- In the Ghidra annotations table: completeness column = "n/a (created)".
- In the evidence row: `completeness: n/a (created)` with a note describing the create.

This protects the doc from looking like it cited a wrong address while preserving the
audit trail that the function entry was new to Ghidra.

## Pattern 3 — Wire-format vs validation-gate disambiguation

When pre-v5 docs conflated "what's on the wire" with "what the receiver validates on the
wire" (e.g., "[if has_subsystem_hash AND is_multiplayer:] +0 2 u16 subsystem_hash"), the
v5 render must split them:

1. **Wire format box** describes what bytes are emitted/read UNCONDITIONALLY:
   `[bit:has_X] [if bit set: ushort:hash]`
2. **Validation gate** is described in the prose: sender emits bit=1 only when CONDITION1;
   receiver always reads, but only validates when CONDITION2.

This is a recurring v5 pattern - the wire format is ALWAYS what's on the wire; conditions
described inside the wire box are usually mis-located validation logic. Move the condition
to the prose around the box.

## Pattern 4 — Order-is-not-numeric callout for dirty-flag emit sequences

When a dirty-flag byte's emit/decode order doesn't match the numeric bit order (e.g.,
StateUpdate emits 0x01, 0x02, 0x04, 0x08, 0x10, **0x40**, **0x20**, 0x80), this is a
load-bearing invariant for clean-room implementers. Surface it with:

- A "**NOT numeric order**" header annotation in the dirty-flag list
- An inline annotation on the out-of-order bit: `Bit 6 (0x40): CLOAK_STATE - emitted BEFORE 0x20`
- A consequence sentence: "A receiver that decodes in numeric order will desynchronize on
  the cloak transition - the cloak bit gets consumed as if it were the start_index byte
  for subsystems."

## Pattern 5 — Speculation-dropped explicit note

When the pre-v5 doc contained a speculation paragraph that the validation pass disproves,
the render must **explicitly say it was dropped** rather than silently removing it. The
pattern: a final paragraph in the affected section saying "The pre-v5 doc speculated
that X. That speculation is **dropped** - [the new explanation] accounts for the trace
naturally without needing [the speculative mechanism]."

This pattern protects against future readers re-introducing the speculation from memory
or other docs that still carry it. It also tells downstream docs (like ones whose own
validation might cite the same speculation) that the speculation is dead.

## Pattern 6 — Two-state-buffer disclosure for receivers

When a receiver function updates more than one state buffer, surface ALL of them in a
"updates two/three/N state buffers" sentence:

```markdown
The receiver updates **two** state buffers, not one: the ship kinematic cache at
`ship+0x88` (pos), `ship+0x90` (orientation accumulator), `ship+0x9C` (velocity hint),
and the animation tracker at `iVar3+0x2C..+0x54`.
```

This callout flags subtle implementation requirements that aren't obvious from the wire
format - a clean-room reimpl needs to know that more than the obvious "apply position to
ship" is happening.

## Pattern 7 — Cross-source-tagged trace counts

When trace counts in the body come from a cross-source memory file (e.g., relay-audit
memory) rather than the binary directly, tag inline with `[cross-source-YYYY-MM-DD trace]`
next to the count. Don't put them in a separate table - inline tagging preserves the
reader's flow while making provenance explicit.

```markdown
The relay-audit cross-source trace [`[cross-source-2026-02-24 trace]`] recorded **23,994
C->S** StateUpdate packets and **45,355 S->C** in a 21-minute Cady / XFS01 session.
```

## Pattern 8 — Open-Questions section before Cross-Links

For docs with multiple confidence:low items, surface them as a numbered "Open Questions"
section near the end (before Cross-Links). Use OQ# inline tags in the body where the
question would otherwise read as a confident claim. Each OQ should:

- Name what's unknown (subject of the question)
- Cite where the call site IS located (if call site is known but semantic is unknown)
- Suggest the next investigative step ("worth pinning", "deferred", "would need...")

This treats open questions as first-class structured debt, not editorial hand-waving.

## Pattern 9 — Effective-score disclosure for low scores

When a function's effective_score from `analyze_function_completeness` is low (e.g.,
Ship__WriteStateUpdate at 0.0, Ship__ReadStateUpdate at 5.8), explain WHY in the
annotation table or the evidence row note:

```markdown
The low effective scores on the sender (0.0) and receiver (5.8) reflect the decompiler's
inability to resolve the per-peer tracker context and per-ship state buffer struct types;
the plate + inline comments capture the wire-format and algorithm semantics required for
clean-room reimplementation.
```

This protects the doc's status:partial from looking like wire-format uncertainty when in
fact the wire format is fully byte-level confirmed - the score is gated by struct typing
work that's downstream of doc validation.
