---
name: gameplay-collision-batch-leaf-render-patterns
description: 9 patterns for rendering TWO sibling gameplay leaf docs in a single batch pass (collision-shield-interaction + collision-rate-limiting) from one combined archaeology evidence packet, where leaf A has 2 mid-severity corrections (class-identity flip + chain-layer insertion) and leaf B has 1 HIGH call-chain narrative correction (3-claim falsification) + cross-doc cascade pending from sibling foundation. Patterns: shared-packet two-NOTE-headlines with category-tagged severity (P1), three-problems-numbered-list format for high-severity call-chain corrections (P2), corrected-call-chain rendered immediately after the falsification list (P3), prior-doc-was-correct-by-accident disclosure for class-identity flips that happen to share offsets (P4), two-allocation linked-storage callout for entries the prior doc treated as monolithic (P5), cross-doc-cascade-pending tag for findings whose name change waits on another doc's correction landing (P6), wrong-attribution table with NOT-prefixed roles in Key Function Reference (P7), vtable-anchor table for negative claims (X is NOT Y) where multiple slots needed disambiguation (P8), batched-sibling cross-link mention naming each other as batch partner (P9)
metadata:
  type: feedback
---

Render patterns from the 2026-05-28 batched v5 pass on `docs/gameplay/collision-shield-interaction.md` (256 lines pre-v5; 2 corrections + 2 clarifications + 1 OQ) and `docs/gameplay/collision-rate-limiting.md` (150 lines pre-v5; 1 HIGH correction + 3 clarifications + 1 OQ). Both rendered from ONE combined archaeology evidence packet.

## Pattern 1 — Shared-packet two-NOTE-headlines with category-tagged severity

When the archaeology agent produces ONE combined evidence packet for two siblings, render TWO separate NOTE blocks (one in each doc) — DO NOT cross-quote or share a single NOTE. Each NOTE leads with its own severity headline tagged by category:

Leaf A: "**Zero formula/wire errors**. 2 corrections (C1 MED: class-identity flip; C2 LOW: chain-layer insertion) + 2 clarifications + 1 OQ. AoE 6-facing 1/6 split byte-confirmed at DAT_0088BACC = 0.16666."

Leaf B: "**Zero algorithm/constant errors — all 5 distance constants + 5 cooldown constants byte-confirmed**. 1 HIGH correction (C1: call chain narrative materially wrong...) + 3 clarifications + 1 OQ. **C1 will mislead OpenBC implementers if not corrected.**"

The bolded openers MUST be different — they categorize what survived (e.g. "wire errors" for one, "algorithm/constant errors" for the other). The number-of-corrections-by-severity goes inline after the bold. Reserve the trailing **bold caveat** for HIGH-severity corrections that have OpenBC implementation risk; leaf A's MED corrections do NOT get a trailing bolded caveat.

## Pattern 2 — Three-problems-numbered-list format for high-severity call-chain corrections

When v5 finds that a multi-step call-chain narrative is wrong (not a single byte/constant flip but a structural attribution error across multiple frames), render the correction as:

1. The prior chain quoted verbatim in a code block
2. "**Three problems with that chain**:" numbered list — each numbered item names ONE specific falsification with the binary evidence inline (byte sequence, decomp line, vtable slot read)
3. The corrected chain rendered as a separate code block AFTER the falsification

Each numbered problem MUST cite a different falsification axis (vtable slot mismatch, dispatch routing mismatch, function body lookup mismatch). Do not collapse multiple axes into one bullet — readers need to verify each claim independently.

For collision-rate-limiting C1, the three axes were: (a) vtable +0x150 contents (RET-only stub), (b) FUN_005A88E0 routing path (dispatches via FUN_005A8810, not vtable+0x150), (c) FUN_005AF890 body contents (no CALL [E?X+0x13C] instruction). All three needed independent rebuttal.

## Pattern 3 — Corrected-call-chain rendered immediately after the falsification list

The corrected chain code block goes IMMEDIATELY after the numbered falsification list, NOT at the bottom of the section. Pattern:

```
### Corrected Call Chain

(code block with arrows showing actual dispatch)
```

Append a one-paragraph "**For OpenBC**: the rate limiter EXISTS at Ship vtable +0x13C — that part of the prior doc is correct. Only the call-chain narrative needed correction." paragraph IMMEDIATELY after the corrected chain. This disambiguates "what survives" from "what doesn't" so a reader doesn't conclude the entire mechanism was wrong.

## Pattern 4 — Prior-doc-was-correct-by-accident disclosure for class-identity flips that share offsets

For collision-shield-interaction C1 (TGObjPtrEvent not TGCharEvent), the prior doc's pseudocode (`event[4] = 0x0080006B; event[10] = ...`) was **numerically correct** because TGObjPtrEvent's `dwEvent_type` field at +0x10 happens to be int-index 4 and `nObj_ptr` at +0x28 is int-index 10. Both classes have those offsets.

In the body, explicitly call this out: "**Impact**: The doc's pseudocode offsets (`event[4]`, `event[10]`) line up correctly with the TGObjPtrEvent layout (`dwEvent_type` at +0x10 = int-index 4; `nObj_ptr` at +0x28 = int-index 10), so any code reading the old text still worked accidentally. But OpenBC implementers naming the event class need the correct identity."

This pattern is load-bearing because readers (especially OpenBC implementers) might assume "the offsets matched so the class was probably right too." Make explicit that **the offsets happened to align across two distinct classes** but only one is the actual class.

## Pattern 5 — Two-allocation linked-storage callout for entries the prior doc treated as monolithic

When v5 reveals that a "0x50 entry" the prior doc described as one allocation is actually TWO allocations linked through a hash-node value-pointer (12-byte hash node + 0x50-byte value object), render as:

```
### Per-Pair Entry — Clar1

The prior doc described `entry[0]=key, entry[1]=lastTime` as a single block. Binary reveals **two separate allocations** linked through the hash node:

**Hash node** (12 bytes, via `FUN_00718CB0(0xC)`):
+0x00  int     key
+0x04  void*   value_ptr
+0x08  void*   next_ptr

**Value object** (80 bytes / 0x50, via `FUN_00718CB0(0x50)`):
+0x04  float   lastTime  (read as *pfStack_30 = (float)puVar3[1] dereferenced)
```

The "linked through the hash node" framing reinterprets the prior doc's `entry[1]` (the "lastTime float") as **the pointer from hash-node-to-value-object, not the timestamp itself**. State this reinterpretation explicitly — readers may have written code based on the prior layout.

## Pattern 6 — Cross-doc-cascade-pending tag for findings whose name change waits on another doc's correction landing

For collision-rate-limiting Clar4, the byte at 0x0097FA89 was identified per the self-destruct doc's C3 as `GameLive_MP` (not `IsHost`). Self-destruct hasn't landed yet, so the cascade is pending. Render with explicit tag:

> ## Clar4 — Byte at 0x0097FA89 is GameLive_MP, not IsHost
> ...
> Per the self-destruct doc's C3 correction (currently CASCADE PENDING across docs), the byte at `0x0097FA89` is actually `GameLive_MP`, not `IsHost`. **Cross-doc cascade pending** — this name should be revised once self-destruct C3 lands.

Plus an evidence-row note: `note: "Clar4 — global identity per self-destruct doc C3 cascade; rename pending across docs."`

This signals to future doc passes that the name is owed a final update once the upstream doc lands. Don't choose a name unilaterally — defer to the originating doc.

## Pattern 7 — Wrong-attribution table with NOT-prefixed roles in Key Function Reference

For high-severity attribution corrections (like collision-rate-limiting C1), the Key Function Reference table at the end includes rows for the WRONG attributions with explicit NOT prefixes:

| Address | Name | Purpose |
|---------|------|---------|
| ~0x005A26D0 | (unnamed wrapper) | **Actual rate-limiter gate** — calls vtable+0x13C; Ghidra-unpromoted (C1) |
| 0x005AF890 | (host-side collision gate) | Reads GameLive_MP; does NOT call rate limiter (C1) |
| 0x005A3900 | (RET-only stub) | Ship vtable +0x150 — 8-byte no-op (C1) |
| 0x005A38C0 | (identity-compare stub) | Ship vtable +0x148 — SETZ AL (C1) |

The "NOT call rate limiter (C1)" pattern in the Purpose column points readers back to the C1 correction. The unnamed wrapper gets bolded as "Actual rate-limiter gate" to lead. Stubs get explicit byte-count descriptions ("8-byte no-op", "SETZ AL"). The (C1) tag is required on every wrong-attribution row.

## Pattern 8 — Vtable-anchor table for negative claims (X is NOT Y) where multiple slots needed disambiguation

For docs where multiple vtable slots needed disambiguation (collision-rate-limiting had THREE: +0x148, +0x150, +0x13C), render a dedicated Vtable Anchors table with a Vtable column distinguishing main from sub-vtables:

| Vtable | Address | Slot | Target | Role |
|--------|---------|------|--------|------|
| Ship main vtable | 0x00894128 | +0x13C | 0x005A22A0 | **Rate limiter (CORRECT)** |
| Ship main vtable | 0x00894128 | +0x148 | 0x005A38C0 | Identity-compare stub (NOT CollisionTest_A) |
| Ship main vtable | 0x00894128 | +0x150 | 0x005A3900 | RET-only stub (NOT Ship::CheckCollision) |
| Ship damage sub-vtable | 0x00894488 | +0x8 | 0x005AF890 | Host-side collision gate (NOT Ship::CheckCollision) |

The Vtable column distinguishes "Ship main vtable" (0x00894128) from "Ship damage sub-vtable" (0x00894488) — important when the prior doc conflated them. Bolded `**Rate limiter (CORRECT)**` row clarifies what SURVIVED v5; the other rows get NOT-prefixed negative claims. The damage sub-vtable row pulls in 0x005AF890 to clarify "this address lives HERE in the sub-vtable, not in the main vtable as a Ship::CheckCollision dispatch."

## Pattern 9 — Batched-sibling cross-link mention naming each other as batch partner

In the Related Documents section of EACH leaf, explicitly name the other leaf with one-line role description naming it as a sibling (NOT a batch partner — keep the rendering invisible to readers):

Leaf A:
> - [collision-rate-limiting.md](collision-rate-limiting.md) — Sibling leaf: per-pair rate limiter (ship+0xEC enable flag)

Leaf B:
> - [collision-shield-interaction.md](collision-shield-interaction.md) — Sibling leaf: what happens AFTER the rate limiter passes (CollisionDamageWrapper at FUN_005B0060)

Don't mention "batched" or "pass" in the public-facing text — that's render-time metadata. The sibling relationship is a permanent feature of the doc layout. Each row describes what's NEXT in the conceptual chain (rate limit gate → damage absorption flow), not what's "also being validated this pass."

## Cross-cutting rules

- **Identical frontmatter `validated:` date** for both batched docs.
- **Identical `methodology`, `binary.*`** rows; v5 standard fields.
- **`status: partial`** for both — even though leaf A's corrections are MED+LOW, the cross-doc cascade (Clar4) keeps leaf B from being `verified`; and leaf A inherits its sibling's `partial` status via the OQ1 dependency on subsystem hit-list authority (the package memo didn't elevate either to `verified`).
- **Companions:** include each sibling on the other; both include the parent foundation (collision-detection-system); both include damage-system; leaf A additionally includes shield-system + protocol leaf #13 (tgobjptrevent).
- **Evidence rows for negative claims**: when a doc states "X is NOT Y" (e.g., "Ship vtable +0x150 is NOT Ship::CheckCollision"), render TWO evidence rows: one for the correct identity ("Ship vtable +0x150 = 0x005A3900 is an 8-byte RET-only stub") and one for the wrong identity ("0x005AF890 is NOT Ship::CheckCollision"). The negative claim row's `note:` explicitly states "Ghidra has not promoted it" or "function body byte-walked" — negative claims require body-read evidence, not pattern-grep.

## What NOT to do (caught during this pass)

- Do NOT downgrade collision-rate-limiting C1 to MEDIUM severity just because the rate-limiter algorithm itself is correct. The CALL CHAIN is what OpenBC implementers will follow when designing their pipeline — and they'll follow the wrong functions. HIGH severity for call-chain attribution errors, regardless of whether the destination is correctly documented.
- Do NOT collapse the two siblings into one combined doc just because the evidence packet was combined. They serve different audiences (rate-limiter is about wireshark-side enable/disable tuning; shield-interaction is about damage absorption math). Keep the doc boundary; share the packet.
- Do NOT delete the prior call-chain code block when rendering C1 — render the prior chain verbatim FIRST so readers can see exactly what the doc previously said, then falsify it, then render the corrected chain. Readers may have inbound links or cached copies referring to the old framing.
- Do NOT promote either doc to `verified` this pass — leaf A has OQ1 (FUN_005AFD70 source-arg dataflow not exhaustively traced); leaf B has cascade-pending Clar4 (GameLive_MP rename). Both stay `partial`.
