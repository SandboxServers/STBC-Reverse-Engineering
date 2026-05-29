---
name: networking-fragmented-ack-render-patterns-20260528
description: 7 render patterns for BIPARTITE leaf docs where v5 finds (a) first-half byte-confirmed reference quality + (b) second-half binary-wrong root-cause claim that contradicts a sibling-leaf doc validated in the same pass — surgical replacement with deferral rather than wholesale rewrite, with hypothesis-chain investigation history preserved
metadata:
  type: feedback
---

# Networking Leaf #8 Render Patterns — Fragmented ACK Bug (2026-05-28)

Context: `docs/networking/fragmented-ack-bug.md` (680 lines, largest in networking family). Pre-v5. Validated against archaeology-specialist memo where verdict was bipartite — first half ROCK SOLID (wire format + 4-field matching + 13 byte-confirmed function addresses), second half had ONE binary-wrong section ("Root Cause: Missing Cleanup in SendOutgoingPackets") that contradicts validated sibling leaf #9 (ack-outbox-deadlock.md, `verified` same day).

Rendered as `partial` because the doc contains both verified-quality reference material AND a binary-wrong interpretation that cannot be promoted; the wrong section is materially load-bearing for Bug 2 reasoning.

## Pattern 1 — Bipartite doc NOTE-block headline

When validation finds the doc is in two halves with different statuses (verified-quality first half + binary-wrong second half), the NOTE block leads with the **BIPARTITE** label, then explicitly names what is byte-confirmed and what's wrong. Don't try to summarize as a single status — call out the split explicitly:

```
> [!NOTE]
> **BIPARTITE doc — wire format + Ghidra-verified analysis byte-confirmed.** First half is
> `verified`-quality reference for ACK encoding (4-field matching, 4/5-byte wire layout, ...).
> Second half's "Root Cause: Missing Cleanup" claim is binary-wrong; deferred to
> [ack-outbox-deadlock.md](ack-outbox-deadlock.md). Bug 1 root cause remains an OQ — requires
> client-side runtime instrumentation. Status: `partial`.
```

## Pattern 2 — Surgical replacement with IMPORTANT-block supersession marker

The original "Root Cause: Missing Cleanup in SendOutgoingPackets" section was structurally load-bearing — it was the punchline of the second half. Rather than delete it (which would orphan the preceding runtime-evidence buildup), rename the section heading AND open with an `> [!IMPORTANT]` block that:

1. Names the original (wrong) section title with the word **"binary-wrong"**.
2. Distinguishes what evidence is correct (the trace observations) vs. what interpretation is wrong.
3. Preserves the bullet-list results from the original (ACK accumulation, ~190 bytes overhead, retx=8 in 6sec) — these are observationally true, just need to be reframed as "path INTO the deadlock" not "absence of cleanup."

```
### Root Cause: Pass-2 Gate Deadlock [v5-correction 2026-05-28 — defers to ack-outbox-deadlock.md]

> [!IMPORTANT]
> **C1 supersession**: The original section here — "Root Cause: Missing Cleanup in
> SendOutgoingPackets" — is binary-wrong and has been replaced. The preserved evidence above
> (server/client observations, retx climbing to 7-8, HandleACK firing against empty retxQ) is
> correct; the *interpretation* of that evidence as "no code path removes ACK entries" is wrong.
```

## Pattern 3 — Historical-preamble before hypothesis chains

When the doc has a deep investigation log (Hypothesis #1 → #7 → "FINAL Assessment" structure), preserve the entire chain but prepend a `> [!NOTE]` historical preamble. The preamble tells readers what to rely on (FINAL Assessment + the v5 correction) vs. what's archaeology (individual hypotheses). Don't gut the hypothesis chain — that's the investigation record and future RE engineers reading the doc need to see WHY each hypothesis was eliminated.

## Pattern 4 — In-line clarification blockquote (C2 pattern)

For a MEDIUM-severity correction that doesn't invalidate the surrounding claim but adds critical scope nuance (here: pass-1 limit-of-3 is NOT a hard limit), use a blockquote immediately AFTER the existing claim with the `[v5-correction]` tag:

```
**Hypothesis #1**: ... limit of 3 ... [original text]

> **Clarification (2026-05-28)** [v5-correction per docs/networking/ack-outbox-deadlock.md]:
> The "limit of 3" is the **pass-1 gate** (`retx < 3`), NOT a hard limit. Pass-2 ... DOES
> process retransmits AND has a cleanup at `retx >= 9` ... See `ack-outbox-deadlock.md` § 2.
```

This preserves the original hypothesis text (archaeology value) while clarifying scope for current readers.

## Pattern 5 — Cross-doc scope disambiguation as a postscript NOTE

When a clarification (here: Clar2 — ReassembleFragments cleanup scope is DISPATCH queue NOT retransmit queue) is load-bearing for an Open Question (here: OQ1 — what clears the client's retransmit queue?), put the disambiguation as a `> [!NOTE]` postscript immediately after the surrounding section steps, AND reference it explicitly when the OQ is later stated:

```
7. Removes consumed fragments from the **dispatch queue** (NOT the retransmit queue — Clar2)

> [!NOTE]
> **Clar2 (2026-05-28)**: The cleanup loop calls `FUN_00718cf0(piVar4)` and decrements
> `piVar8[6]` (dispatch queue count). The retransmit queue (peer+0x80) is NOT touched here —
> that scope distinction matters for Bug 1 OQ1 below.
```

Then OQ1 cites: "**ReassembleFragments** (FUN_006b6cc0, Clar2) only touches the **dispatch queue**, NOT the retransmit queue." This forward-reference + back-reference makes the load-bearing scope explicit.

## Pattern 6 — Open Questions with constraints-from-validated-code list

For UNRESOLVED Bug 1 root cause, the Open Question structure leads with the unresolved claim from FINAL Assessment, then enumerates "Constraints from validated code" (what we know CAN'T be the answer based on byte-confirmed code paths), then lists candidate hypotheses + the required next step (runtime instrumentation). This shape is more useful than "we don't know" because it points future investigators at the search space:

```
### OQ1 (UNRESOLVED): Bug 1 root cause — what clears the client's retransmit queue?

[Restate the claim from FINAL Assessment]

Constraints from validated code:
- HandleACK matches one fragment per call ...
- ReassembleFragments only touches the dispatch queue ...
- No whole-message ACK exists ...

Candidate hypotheses worth investigating ...

**Required next step**: Client-side runtime instrumentation hooked into ...
```

## Pattern 7 — Preserve runtime trace data with `[preserved historical evidence]` tag

The Valentine's Day Battle Trace section is 2026-02-14 wire trace observation — predates v5 but the OBSERVATION is still useful evidence. Tag the section header `[preserved historical evidence]` (a new tag, distinct from `[v5-validated]`) to mark it as "we did NOT re-validate this in v5 but the prior evidence is still load-bearing for current reasoning."

This is different from `[v5-validated]` (we byte-checked it this pass) and different from `[v5-correction]` (we changed it this pass). For evidence that was correct then and is still correct now but didn't get a fresh check, `[preserved historical evidence]` is the right tag.

## Anti-pattern — don't try to delete the wrong section

The temptation with a binary-wrong section is to DELETE it. Don't. The runtime evidence preceding it (retx counts climbing 3 → 7 → 8, ACK-outbox accumulation observations) is correct and load-bearing. The flaw is purely interpretive — the section concludes the wrong cause from correct observations. Surgical replacement with an IMPORTANT-block supersession marker preserves the evidence and the interpretive chain (showing readers WHERE the wrong interpretation slipped in) while pointing them to the correct mechanism in the sibling doc.

## Frontmatter notes

- 16 evidence rows (13 byte-confirmed function addresses + 1 wire-format claim + 1 C1 supersession claim + 1 placeholder for the bare-code factory)
- `status: partial` — bipartite shape demands it; first half could be promoted to `verified` if the doc were split, but in practice readers will land on the whole doc and the C1 supersession is non-trivial
- `supersedes: [2026-02-19]` — the prior "Ghidra-Verified Analysis" section header date stands as the supersession anchor
- `companions:` includes `docs/networking/ack-outbox-deadlock.md` as the AUTHORITATIVE doc for Bug 2 (sibling-leaf supersession pattern)
