---
name: transport-foundation-render-patterns
description: Render patterns from transport-layer.md v5 validation (protocol foundation #3). Five patterns specific to transport docs: newly-located algorithm subsection (cipher), function-creation NOTE block for missing-from-Ghidra functions, side-channel path documentation (self-send loop-back), MTU-promote-to-intro, three-site agreement table for cross-coordinated flags.
metadata:
  type: feedback
---

# Transport-foundation render patterns

Five render patterns that emerged from rendering `docs/protocol/transport-layer.md`
(protocol foundation #3) under v5. Transport docs span cipher, framing, fragmentation,
and connection state — each surfaces a specific render decision.

## Pattern 1: Newly-located-algorithm dedicated subsection

When v5 validation locates a previously-unknown function (here, the AlbyRules cipher
Encrypt / Decrypt), the dedicated subsection should:

1. Open with one sentence stating the key property of the newly-located algorithm (here:
   "re-keys per packet — no streaming state").
2. Provide the **complete vtable / object layout** as a small table — slot, offset,
   address, name.
3. Name every site that calls the algorithm (here: send and receive paths) with addresses.
4. Cite any related companion doc that should absorb the new anchors (with explicit "this
   pass deferred — its own validation will pick up these anchors" note).

**Why:** Newly-located algorithms are the headline finding. Giving them a small dedicated
subsection (not a paragraph inline in a larger section) ensures future readers find the
addresses by scanning the TOC.

**How to apply:** Use whenever v5 validation produces a NAMED function that has at least
2-3 callers and a coherent role. The subsection is independent of normal doc structure.

## Pattern 2: Function-creation NOTE block

When the validation pass had to `mcp__ghidra__create_function` because Ghidra auto-analysis
missed the function (e.g., it's a vtable slot reached only by DATA xref), render a
`> [!NOTE]` block describing:

- Why the function was missing (vtable index, dispatch pattern, no direct CALL xref)
- The exact dispatch idiom (`(**(code **)(*p + 0x6C))(...)` style)
- A pointer to the precedent case for this project (here: `MpgameHandleMessage`)
- That the function was CREATED this session — flagging the Ghidra state change

**Why:** Without this NOTE, a future maintainer who tries `get_function_by_address` on the
SAME stale Ghidra snapshot will get "no function" and assume the doc is wrong. Disclosing
the dispatch pattern + creation event makes the cycle robust.

**How to apply:** Whenever a v5 validation pass creates a function via
`mcp__ghidra__create_function`, the doc that cites that function gets a NOTE block at
the first mention of the function.

## Pattern 3: Side-channel path documentation (loop-back, queue-bypass, etc.)

When a system has a primary path AND a side-channel path (here: the host's self-send
loop-back queue), render them as **separate sibling subsections** under the same parent,
not as a "main path with caveats" structure. The side-channel subsection needs:

1. Explicit trigger condition (the address-comparison branch).
2. The state fields it manipulates (local queue at `network+0x33C` / `+0x340`, toggle at
   `network+0x344`).
3. Why the side channel exists (here: zero OS round-trip latency for host's own broadcasts).
4. Cross-link to anywhere else that consumes the side-channel state (here: the receive
   side that drains the queue alternately with recvfrom).

**Why:** A clean-room implementer needs the side channel called out as an architectural
feature, not a footnote. Loopback paths look like dead code if not explicitly explained.

**How to apply:** Anywhere the system has a same-host shortcut that bypasses the network
stack. Common in transport / RPC / message-bus subsystems.

## Pattern 4: MTU / threshold values promoted to introduction

Quantitative wire-level constants (MTU, max packet size, max fragments) should appear in
the doc's introductory paragraph, not buried in a fragmentation section. Promote the
number, cite the function that sets it, and reference both locations in the binary (here:
`network+0xAC` and `network+0x2B`, both `0x400`).

**Why:** Readers who care about wire-level limits scan the intro first. Hiding the MTU in
a downstream section forces them to read everything.

**How to apply:** Any time the doc establishes a load-bearing numeric limit. State it,
cite it, move on.

## Pattern 5: Three-site agreement table for cross-coordinated flags

When a single state flag is SET at one site, READ at another, and put on the WIRE at a
third (here: the `is_below_0x32` flag, three-site agreement at HandleReliableReceived /
HandleACK / TGHeaderMessage_Serialize), render the agreement as a small table with
columns: Site role, Address, Function, What it does.

This is distinct from a normal call chain because there's no caller / callee relationship —
the three sites are *coordinated by state*, not by call.

**Why:** Wire flags that need to round-trip through the network back to a different site
(an ACK back to a different outbox) are easy to get wrong in a clean-room reimplementation.
Showing the three sites side-by-side makes the contract explicit.

**How to apply:** Any time a v5 validation surfaces a flag with set/read/wire agreement at
multiple coordinated addresses. The pattern also applies to per-tick caches (write site,
read site, invalidation site).

## When this pattern set applies

Apply to **transport / framing / reliability** layer docs where the doc covers multiple
loosely-coupled subsystems (cipher, framing, fragmentation, sequence numbers,
connection state). Each subsystem may use 1-3 of the patterns above. Higher-level docs
(per-opcode RE) use leaf patterns instead.
