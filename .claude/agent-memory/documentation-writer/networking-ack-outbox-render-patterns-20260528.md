---
name: networking-ack-outbox-render-patterns-20260528
description: Render patterns from networking leaf #9 (ack-outbox-deadlock.md). Second networking-family doc to clear v5 `verified`. Zero mechanism corrections + 4 address-precision Clars + supersession of parent foundation's sidebar hypothesis. Patterns for byte-anchor table density, gate-completion Clar pattern, supersession-of-binary-correct-but-behaviorally-insufficient sidebar pattern.
metadata:
  type: project
---

# Networking Leaf #9 — ACK-Outbox Deadlock Render Patterns

**Doc**: `docs/networking/ack-outbox-deadlock.md`
**Pass**: v5 verified, 2026-05-28
**Verdict**: Zero mechanism corrections + 4 address-precision Clars
**Significance**: Second networking-family doc to clear `verified` (after alby-rules-cipher-analysis.md). Most byte-verifiable networking-family doc to date.

## Patterns established

### P1 — Byte-anchor density in evidence rows
For "most byte-verifiable" docs (every claim has a `CMP/MOV/JG` anchor at a specific address), put the byte-level disassembly in the `note:` field of each evidence row, not in the body. The body cites the address; the frontmatter row carries the exact instruction. Reader pattern: scan frontmatter for byte-truth, jump to body for prose context.

Example:
```yaml
- claim: "Pass 2 deadlock gate: `(msg_count > 0 OR peer+0xBC != 0) AND peer+0xB4 > 0` — the bug"
  address: 0x006b5a01
  confidence: high
  note: "0x006b5a01: MOV EAX,[ESP+0x14]; 0x006b5a09: MOV AL,[ESI+0xbc]; 0x006b5a17-0x006b5a1f: TEST EAX (peer+0xB4); JLE bypass"
```

### P2 — Gate-completion Clar pattern
When v5 adds a third predicate to a previously-2-predicate gate, **don't restructure** the body explanation of the gate — add the predicate inline with an explicit `└─── address range ───┘` ASCII bracket diagram showing which byte range contributes which predicate. The reader needs to see the predicates aligned to their bytes.

Example used in §2:
```
GATE: (msg_count > 0 OR peer+0xBC != 0) AND (peer+0xB4 > 0)
      └─────────── 0x006b5a01-0x006b5a11 ────────────┘  └ 0x006b5a17-0x006b5a1f ┘
      "either we already sent something this tick,        "and the outbox actually
       or we're tearing the peer down"                     has entries to serialize"
```

This makes the predicate-to-byte mapping unambiguous and lets the deadlock analysis below stay unchanged (the deadlock requires non-empty outbox by construction, so the third predicate is implied for the deadlock case).

### P3 — Supersession of binary-correct-but-behaviorally-insufficient sidebar
When v5 surfaces that a parent foundation doc's sidebar hypothesis describes the **same end-state** as the leaf doc but via a different mechanism — and the leaf's mechanism is the correct one for OpenBC fix design — render a dedicated `## N. Supersedes <parent> <hypothesis name>` section with this structure:

1. "What \<parent\> claimed" — short blockquote of the hypothesis
2. "What the binary actually does" — counter-claim citing the byte-anchor that disproves the prior framing
3. "The actual root cause" — restate the correct mechanism
4. "For OpenBC, the correct fix flows from this doc" — practical bullet showing which fix-direction follows from which framing

Critically, **don't delete the parent's sidebar** — instead, write "should be cross-linked to this doc for historical context but should not be treated as the canonical root-cause explanation." This preserves the parent's prose for readers with inbound links while making the canonical source unambiguous.

Use this pattern when:
- Parent's claim and leaf's claim agree on end-state
- They disagree on mechanism
- Leaf has byte-level proof
- Fix design depends on which framing is canonical

### P4 — Address-precision Clar without restructuring
For Clars that move an anchor address by a small offset (e.g., "0x006b6240 → 0x006b624D, off by 13 bytes"), inline the corrected address into the existing pseudocode comment with a `// Preamble (init + null-check): 0x006b6240 - 0x006b624B` / `// Comparison loop body starts at: 0x006b624D` two-line header. Don't restructure. Add a short `> **Clar-N (address precision)**:` blockquote AFTER the pseudocode explaining that the mechanism is unchanged.

This keeps inbound links to the old address valid (reader still sees 0x006b6240 in the doc) while making the corrected address visible.

### P5 — Range overstatement correction with role disambiguation
For Clars that tighten a range (e.g., "Pass 2 is 0x006b5a50-0x006b5af4, not -0x006b5b90"), don't just shorten the range — explain what the over-extended region actually does. In this doc: "The range 0x006b5af4-0x006b5b90 is the **packet-finalize block** (writing peer_id + msg_count to buffer[0..1] and calling sendto via the network vtable)."

This turns a precision correction into a tutorial moment: the reader now knows where the finalize block lives even though it's outside the loop they were studying.

### P6 — Side-effect disclosure with OpenBC parity note
When v5 reveals that a one-line pseudocode operation hides a multi-effect function call (here: `entry.retx_count++` is actually `SetRetransmitCount(entry, n+1)` which also recomputes `msg+0x1C`), don't promote the side effect to a full section. Instead:
1. Replace the pseudocode line with the function call (e.g., `SetRetransmitCount(entry, entry.retx_count + 1)  // ← also recomputes msg+0x1C (interval)`)
2. Add a Key-details bullet: "**Side effect** (Clar-4): ... Doesn't affect the deadlock mechanism, but OpenBC implementations must replicate the interval recomputation for retransmit-timing parity."

The OpenBC-parity framing is the load-bearing reason to record the Clar at all — without it, the side effect is trivia.

### P7 — Trace confidence retention block
For docs that mix v5-anchored mechanism claims with `[trace]`-derived projections (queue sizes, ratios, packet counts), add a single `> **Trace confidence note**:` block at the end of the trace-projection section explicitly listing which numbers stay `[trace]`-confidence rather than being promoted to v5. This prevents readers from assuming the byte-anchored sections also validate the empirical numbers.

### P8 — Companions block includes parent-superseded foundation
When the leaf supersedes a sidebar hypothesis in a parent foundation doc, include the parent in `companions:` AND name it explicitly in the in-body Related Docs list with a "this doc supersedes its X sidebar" annotation. The reader reaches the leaf either from the parent (where the supersession will be cross-linked once batch close runs) or from a sibling — both paths should land them looking at the canonical mechanism.

## What this doc is good as a template for

- Future networking leaves where multiple gate predicates need to be anchored to specific bytes
- Future docs where v5 supersedes a parent's binary-correct-but-behaviorally-insufficient hypothesis
- Any doc where the ratio of evidence-row byte-anchors to body prose is unusually high (this doc has 23 evidence rows for ~310 lines of body)

## Not-yet-templated

- Multi-doc supersession (this is single-parent supersession; multi-parent has not been encountered yet in networking family)
- Supersession where the leaf's framing changes the OpenBC wire-format (this doc supersedes mechanism, not wire format — wire format unchanged)

## Family-close follow-ups deferred

- netimmerse-transport-deep-dive.md needs a cross-link sidebar pointing to this doc's §7 (Supersedes section). Batched at networking family close, not done now.
- v5 validation tracker row update — batched.
- MEMORY.md index entry update — batched.
