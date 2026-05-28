---
name: thin-handler-index-render-patterns
description: 7 patterns for rendering thin handler-index docs (smallest mid-tier docs that delegate per-class detail to a sibling) when v5 validation surfaces direction/symmetry refinements rather than corrections
metadata:
  type: feedback
---

# Thin handler-index doc render patterns

Learned rendering `docs/protocol/object-replication.md` (protocol mid #9,
~30 lines pre-v5, 6/6 claims confirmed clean, 2 wording refinements).
The doc is a thin index that exists ONLY to anchor the receiver handler
and delegate per-class payload detail to a sibling doc
(`objcreate-serialization.md`). The render patterns below preserve that
thin-index character even as the v5 frontmatter adds substantial weight.

## Pattern 1 — Two-refinement NOTE block with R1/R2 tags

When the validation produces refinements (not corrections), use an
explicit `R1` / `R2` numbering inside the top-of-doc `> [!NOTE]` block.
Each refinement gets its own indented bullet under the NOTE. Both
refinements are direction-symmetry fixes (sender-side vs receiver-side
helper / vtable slot) — the same shape.

**Why:** R1/R2 tags make the NOTE block searchable and let the §6.x
tracker row reference them by tag without re-quoting the body. Future
re-validation can ask "are R1/R2 still applicable?" without reading
through the prose.

**How to apply:** Whenever a `status: partial` render has 2 or more
material wording fixes (not binary corrections), open the NOTE with the
status line, list the renamed function, then bullet-list `R1`, `R2` (etc.)
with one-line summaries. Pointer to companion doc lives in the final
NOTE sentence.

## Pattern 2 — Sender-vs-Receiver Symmetry section as a 3-row table

When v5 reveals that sender and receiver touch DIFFERENT vtable slots
on the same object (here: sender `+0x10C`, receiver `+0x118` + `+0x11C`),
render this as a dedicated section near the top of the body with a
three-column table: Direction / Function / Vtable slot / Role.

**Why:** The pre-v5 body conflated direction-symmetric pairs into one
line ("Produced by object->vtable[0x10C](...)"). A reader who only
decompiles the receiver and looks for `vtable[0x10C]` finds nothing and
loses an afternoon. A 3-row table at the top of the body makes the
asymmetry impossible to miss.

**How to apply:** Whenever a wire format is direction-symmetric but the
codepaths are NOT (different vtable slots in each direction, or a
sender-only helper like `FUN_006A19A0`), add a Sender vs Receiver
Symmetry section EARLY in the body — before the receive-side
post-processing details.

## Pattern 3 — Pseudocode sender + receiver pipeline pair

Inside the Symmetry section, paired pseudocode blocks (one labeled
SENDER, one labeled RECEIVER) make the asymmetry concrete. Use
ASM-style pseudo-syntax (`ship->vtable[+0x10C](buf+iVar7, ...)`) so the
slot offsets are visually obvious.

**Why:** Tables list slot numbers; pseudocode shows the control flow.
Both are needed for a thin index doc that's supposed to be self-contained
at the handler level.

**How to apply:** Pair them. Sender first (because the wire is written
before it's read); receiver second. Use the same variable names
(`buf+iVar7`, `bWithTeam`) across both blocks so reader can pattern-match.

## Pattern 4 — Authority section as a 2-row sender table

When the doc's authority claim is "S -> C only, both senders are
server-side codepaths", render Authority as a small `Sender call site /
Address / Trigger` table. This anchors the negative claim ("no
authoritative client sender exists") to the positive evidence (the two
server-side call sites).

**Why:** Per v5 evidence-header rules, negative claims need positive
evidence cited. A 2-row sender table is the cleanest way to discharge
the negative claim ("no C -> S authoritative ObjCreate sender exists in
the binary") — by enumerating the only call sites that DO exist.

**How to apply:** For any S -> C only / C -> S only opcode where the
trace shows some wrong-direction traffic (e.g. host-relay echo), use a
small sender table + a follow-up paragraph naming the echo path as a
topology artifact. The reader leaves with both the authority direction
AND the explanation for the seemingly-contradicting trace evidence.

## Pattern 5 — Cross-anchor references table near doc bottom

For thin index docs that lean heavily on foundation/sibling docs,
render a Cross-anchor references table listing every external address
the doc consumes (dispatcher, jump table, base vtables, sender handlers,
companion doc anchors).

**Why:** Thin index docs don't re-derive foundation anchors — they
inherit them. Listing the inherited anchors makes the dependency graph
explicit and gives the next reviewer a one-shot consistency check.

**How to apply:** Add the table near the bottom (before Open Questions).
Each row carries (Anchor name / Address / Source doc / Note). The Source
column doubles as a navigation aid; the Note column flags
delegation-to-sibling for any per-class detail.

## Pattern 6 — "Per-class payload format" anchor delegation in evidence row

In the v5 frontmatter, evidence rows about the dispatch chain
(here: `FUN_005A1F50` -> factory + vtable+0x118 + vtable+0x11C) should
carry an explicit `note:` line that names the sibling doc holding the
per-class detail (here: `objcreate-serialization.md`).

**Why:** Thin index docs WILL be regenerated against the same Ghidra
state during downstream sibling validation. The `note:` on the dispatch
evidence row tells the next pass "do not re-derive per-class payloads
here — see sibling X".

**How to apply:** Any evidence row about a dispatch chain or polymorphic
dispatcher gets a `note:` block naming the sibling doc that owns the
per-class detail. Keep the row's `claim:` field focused on dispatch
identity (factory + slot indices), not payload format.

## Pattern 7 — `address: null` for relay/topology negative claims

The authority evidence row uses `address: null` because the claim is
negative ("no C -> S authoritative ObjCreate sender exists"). The
`note:` field cites the cross-anchor source (game-opcodes.md trace
counts) AND names the host-relay-echo explanation.

**Why:** Per v5 standard, negative claims (`address: null`) at
`confidence: high` require the searcher to have read the full function
body. The `note:` field discharges that requirement by explaining WHAT
was searched (both sender call sites) and WHY the wrong-direction trace
is not a counter-example (relay echo).

**How to apply:** Use `address: null` only for negative claims that have
been positively verified by enumerating the positive evidence. Always
include the explanatory `note:` with the cross-anchor cite and the
topology artifact explanation.

## When NOT to use these patterns

These patterns assume the doc IS a thin index that delegates per-class
detail to a sibling. If the doc is supposed to be a comprehensive
catalog (`game-opcodes.md`, `objcreate-serialization.md` itself), use
the catalog render patterns instead — those expect every per-class row
to be inline, not delegated.

If the doc is `> 50 lines pre-v5` and lists individual class payloads
inline, it's NOT a thin index — don't add the Sender vs Receiver
Symmetry table as the primary detail surface. Use it as a sub-section
within the per-class layout instead.

Related memory: [[stateupdate-render-patterns]] — for "zero material
corrections" precedent;
[[catalog-row-disposition-tree]] — for catalog docs;
[[load-bearing-correction-disambiguation]] — for when refinements
become full corrections.
