---
name: networking-netimmerse-transport-render-patterns-20260528
description: Render patterns for v5 partial pass on a foundation doc that was created WITHOUT live Ghidra (had a top-of-doc "Ghidra not reachable" disclaimer). 3 corrections + 2 clarifications + 1 historical hypothesis demoted. Wire claims survived with high fidelity; structural/control-flow reasoning errored more. Cross-doc note: this doc had peer seq offsets RIGHT where protocol foundation #3 had them wrong.
metadata:
  type: feedback
---

# Render patterns — netimmerse-transport-deep-dive.md (networking foundation #5)

## Setting

Pre-v5 doc had an explicit "Ghidra not reachable" disclaimer + orchestrator confidence flags interleaved. v5 pass found wire format + field offsets survived byte-confirmed; **structural claims** (vtable size), **control-flow reasoning** (Section 5 fragment window), and **scope of hidden-state enumeration** (Section 9) errored more.

## Patterns applied

### P1 — Preserve the "Ghidra not reachable" provenance in the NOTE block headline
Don't strip the original disclaimer; surface it as a pattern observation. Top-of-doc NOTE leads with the validation outcome (3 corrections / 2 clarifications / 1 historical) AND names the methodology gap (created from static decompilation). This converts what was a confidence-warning footer into a feature of the doc's history.

### P2 — Cross-anchor against prior-family wins where this doc was right
Section 2 gets a NOTE block calling out: "This doc had +0x24/+0x26/+0x28/+0x2A correct; protocol foundation #3 (transport-layer.md) had +0x98/+0xA8 (now corrected)." Pattern: when a later-validated foundation doc was RIGHT on something an earlier-validated sibling was WRONG on, surface the reconciliation in the body, not just in the validation memo. Future readers benefit from knowing which doc to trust on disputed offsets.

### P3 — Structural-error correction reuses the table format
C1 (vtable size) doesn't rewrite the original 0..7 table. Adds an IMPORTANT block right below it with a NEW table of slots 8..11 + sentence framing them as "base-class slots (TGBufferStream)." The original table stays valid; the correction extends it. Then re-asserts the downstream conclusion ("no virtual dispatch in ACK matching") which is independent.

### P4 — Control-flow reasoning correction rewrites the WHY but keeps the WHAT
C2 (Section 5 fragment window) keeps the original code block AND the original conclusion ("No blocking here"), but rewrites the reasoning paragraph with a numbered 1-2-3 walkthrough explaining the correct order of operations (reassembly fires INSIDE QueueForDispatch BEFORE expected counter advances). Pattern: when reasoning was wrong but conclusion was right, the IMPORTANT block leads with "the reasoning is wrong, the conclusion survives because <actual mechanism>." Don't delete the conclusion.

### P5 — Scope-error correction RETITLES the section, doesn't delete it
C3 (Section 9 hidden state) renames heading from "Hidden Peer State Between +0x30 and +0x64" to "Peer State +0x30 to +0x64 (Non-ACK Range)." Keeps the original table (still accurate for THAT range). Adds an IMPORTANT block listing the ACK-critical fields at peer+0x80+ that the original missed, cross-linked to ack-outbox-deadlock leaf. Pattern: when a section was correct-but-over-claiming, narrow the scope in the heading + add a table of what's NOT in that range with a pointer.

### P6 — OQ-RESOLVED gets a full inline disasm block
Clar1 (ACK factory) has the orchestrator's old "open question" NOTE BLOCK replaced inline with a NOTE that includes the actual disassembled bytes (0x21..0x2c offsets, `MOV [eax+0x40], cl` etc.) + explicit statement "the factory body remains an unnamed raw label in Ghidra DB." Pattern: when an OQ is closed via raw-byte verification (no Ghidra function record), show the bytes IN the doc. Readers reproducing the analysis don't have to chase the validation memo.

### P7 — Disambiguation Clar with parallel-but-unrelated callout
Clar2 (Section 10 backoff mode) opens with a NOTE: "+0x2C is on the TGMessage retransmit entry, NOT the peer. Not to be confused with peer+0x2C which holds last_activity_time (see Section 9)." Pattern: when an offset is reused across two unrelated objects in the same doc, cross-reference both within the same NOTE block (with Section pointer). Cheap to write, prevents reader confusion.

### P8 — Historical hypothesis demoted with binary-correct-but-behaviorally-insufficient framing
The "Agent's Root Cause Hypothesis" section gets retitled "Historical (resolved 2026-05-28) — ACK Retransmit Count Exhaustion: Binary-Correct But Behaviorally-Insufficient." Replaces orchestrator's old "LOW CONFIDENCE" warning with a NOTE that EXPLICITLY validates the binary claim ("the gate exists, the code matches") AND explains why the conclusion is wrong ("stock dedi sends StateUpdate routinely, pass 2 fires normally, observed bug shows identical ACK bytes"). Then names the superseding doc (ack-outbox-deadlock).

Pattern: when a hypothesis is binary-correct but behaviorally-wrong, don't delete it. Demote with the dual framing — confirm the code claim, falsify the behavioral claim, point at the superseding mechanism. This preserves the analysis for future readers who might rediscover the same gate and need to know it's been considered and ruled out.

### P9 — Per-section v5-validated tag at heading level
Sections 1, 2, 3, 8, 10 each got `[v5-validated 2026-05-28]` appended to the `## N. Title` heading. Pattern for foundation/long docs: tag per-section, not per-paragraph, so future readers can see at a glance which sections were re-audited. Sections without tags (4, 5, 6, 7, 9) are either implicitly validated (no claims contested) or carry their correction inline.

### P10 — OQ section consolidates: RESOLVED vs OPEN with cross-section pointer
Open Questions section at the bottom flattened to a bulleted list with `**OQ1 — RESOLVED 2026-05-28**` and `**OQ2 — open**` prefixes. RESOLVED entries get a pointer to the section where the closure was made (`See Section 3 Clar1.`). Pattern: don't delete resolved OQs — convert them to "RESOLVED <date>" with a body-section cross-ref. Lets future readers see the closure history without re-reading the whole doc.

### P11 — Pattern Note as a final "Static-Decompilation-Only Validation: Lessons" section
Added a new `---` separator + `## Static-Decompilation-Only Validation: Lessons` section that captures the meta-finding (wire claims reliable, reasoning less so). Pattern: when a doc is the FIRST of its kind to be validated (e.g., first Ghidra-not-reachable doc), append a Lessons section so future docs of the same shape have a heuristic to inherit. Keeps the meta-finding in the doc body, not just in agent memory.

## Frontmatter shape (foundation, partial)

- 14 evidence rows (vtable, slot 6, slot 7, serialize, factory, HandleReliableReceived, HandleACK, SendOutgoingPackets, Update chain, 4 peer-seq counters, field map, backoff modes)
- completeness scores cited for: TGHeaderMessage_Serialize (53.5), HandleReliableReceived (31.6), HandleACK (33.6), SendOutgoingPackets (0.0)
- companions array: transport-layer (foundation cross-anchor), ack-outbox-deadlock (supersedes hypothesis), fragmented-ack-bug (related leaf), network-protocol (parent)
- supersedes: [2026-02-19] — the original date in the now-removed top-of-doc byline
- ACK factory evidence row carries `address: 0x006bd1f0` + `completeness: n/a` + note "Address is NOT a Ghidra function (get_function_by_address returns 'No function found')." Pattern for raw-label addresses: name the address as the claim anchor, disclose in note that no Ghidra function record exists, cite the byte offset where the load-bearing instruction lives.

## What I did NOT do (concurrency rules)

- Did NOT touch `docs/networking/v5-validation-status.md` — batched at end of wave per orchestrator instruction
- Did NOT touch `.claude/agent-memory/documentation-writer/MEMORY.md` — batched at end
- This memo lives in its own file per the wave protocol
