---
name: architectural-reframe-render-patterns
description: 6 patterns for rendering mid-tier protocol docs where v5 validation flips an architectural framing (count of mechanisms, who owns what, etc.) - learned from tgmessage-routing.md
metadata:
  type: project
---

# Architectural reframe render patterns

When a v5 validation pass surfaces an architectural reframe (not just a per-claim correction
but a re-conceptualization of how the system is organized), the rendered doc needs more than
swap-in-place fixes. Six patterns developed for tgmessage-routing.md v5 render (2026-05-28).

## Pattern 1: NOTE-block headline with C-tagged corrections

The doc's top `> [!NOTE]` block enumerates corrections as `C1` / `C2` / `C3` (material) plus
`C4` / `C5` (minor). This lets the body cite "C1 correction" inline at the section where
the reframe lands, without re-explaining the headline.

**When to apply:** any mid-tier doc with >= 2 material corrections, especially when one of
them is an architectural reframe (count-of-mechanisms flip, ownership re-attribution).

**Example structure:**
```
> [!NOTE]
> This doc is `status: partial`. [list the v5-anchored side]. N material corrections from
> the pre-v5 doc:
>
> - **C1.** [headline correction with the reframe]
> - **C2.** [next material correction]
> - **C3.** [next material correction]
>
> Plus minor corrections: [list with explicit C4 / C5 markers]. [cross-source provenance].
```

## Pattern 2: Dedicated "[New mechanism count] [System name]" section near top

For a count-flip ("two becomes three" or "single becomes layered"), insert a dedicated
section EARLY in the doc with the new count in the section title, plus a comparison table.
Do not let this idea live inside an existing section - it deserves its own anchor for cross-
linking.

**Example:** `## Three Routing Mechanisms` comes BEFORE the existing `## Two Independent
Type Systems` section. The reframe table has 3 columns: Mechanism / Used by / C++
implementation / Trace evidence.

Add a "Two ideas to keep separate" prose paragraph after the table for the conceptual
distinction (e.g. routing-by-target vs decision-to-relay). This is where the reader's
mental model gets rebuilt.

## Pattern 3: Replacement section heading rename + inline `(replaces "Old Heading")` marker

When a body section gets replaced (not just edited), keep BOTH names accessible: the new
heading carries the v5 truth, and a parenthetical inside the heading or in the first
sentence cites the pre-v5 heading. Lets readers searching for old content land in the new
place.

**Example:** `## Per-Handler Relay Pattern (replaces "Host Relay Path - Opaque
Forwarding")` - the section heading flags the rename, and the first sentence elaborates
why the old framing was wrong.

## Pattern 4: Per-handler table with trace ratios INLINE in the relay column

When you have empirical trace data corroborating per-handler decisions, put the trace
ratio in the same table row as the binary-anchored relay decision, not in a separate
appendix. The 1:1-vs-x:0 pattern in the ratio column is the visual proof of the
mechanism.

**Example:** Per-Handler Relay Pattern table with columns Opcode / Name / Handler /
Relays via? / Trace ratio C:S/S:C. The ratio column tags ungrouped opcodes with `—` to
mark "not observed in audit"; absorbed opcodes show `31:0` or `3:0`; relayed opcodes
show `~1:1`. Reader scans the column and sees the pattern.

Tag the table once at the top: `[v5-validated 2026-05-28 - dispatcher decode]
[cross-source-2026-02-24 trace - audit ratios]` - two tags, one for each evidence
source.

## Pattern 5: Open Questions section disambiguates "call-site located" from "semantic unknown"

When a v5 pass closes an upstream open question PARTIALLY (the function call site is
located, but the meaning of a field used by that call site is still unknown), the
Open Questions list distinguishes the two. The closure status to the upstream OQ goes in
the doc's per-doc tracker entry (§6.N), not buried in the body.

**Example:** OQ1 here is `peer+0x1C semantics`. The body of the doc says "SendTGMessage
mode A uses peer+0x1C as the lookup key via FUN_006BB9D0(optionalArg)" - the **call site**
is anchored. But OQ1 explicitly says the **meaning** of peer+0x1C isn't anchored. The
companion python-messages.md OQ4 ("what is targetID == -1?") is **partially closed** by
this doc: closed at the call-site level, still open at the semantic level. Track this in
the per-doc entry's "Cross-doc impacts" subsection.

## Pattern 6: Three-tag provenance: v5 (structural) + cross-source (trace) + (none, for negative claims)

For star-topology evidence lists where some bullets are structural (anchored in binary)
and others are empirical (observed in trace), use TWO tags inline:
`[v5-validated 2026-05-28 - structural] [cross-source-2026-02-24 trace - peer-map]`.

The reader gets to see which bullets are binary-grounded vs trace-observed in the SAME
list, without splitting the list across two sections.

## Render order for an architectural-reframe doc

1. Breadcrumb + v5 frontmatter
2. Title + 1-paragraph subtitle
3. NOTE block (with C-tagged corrections)
4. Executive Summary (Q&A table - the reader's index)
5. **Three [Mechanisms] section** (the reframe headline - early!)
6. Two-systems / boundary section (the conceptual primitives)
7. Transport-layer section (factory table, factories)
8. Receive Path
9. **Per-Handler Relay Pattern** (replacing the old "Host Relay" section)
10. SendTGMessage / SendTGMessageToGroup / SendToGroup_Iterate (with 3-mode pseudocode)
11. **Connect-Event Broadcast (FUN_xxxxxxxx)** (mechanism #3 explicitly named)
12. C++ Dispatchers (the silent-fallthrough proof)
13. Python Message Dispatch (the >= 0x2C side)
14. Star Topology (the reader's mental model)
15. Why Mod Custom Types Work (the cleared-path explanation)
16. PythonEvent 0x06 vs 0x0D (the trace-vs-binary cross-check)
17. **Open Questions** (3-item bulleted list with OQ# tags)
18. Key Addresses (the lookup table for the impatient reader)
