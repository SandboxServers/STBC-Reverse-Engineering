---
name: networking-mid-tgmessage-cleanroom-validation-20260528
description: v5 validation of docs/networking/tgmessage-routing-cleanroom.md against protocol mid #7 (tgmessage-routing.md). 1 material correction (false transport-level auto-relay), 4 clarifications (3-mechanism model missing, NoMe creator misattributed, target=-1 missing, dispatcher count "two" vs "three"). Most behavioral claims survive — the spec's contracts hold even when one of its causal explanations is wrong.
metadata:
  type: project
---

# tgmessage-routing-cleanroom.md (Networking mid #6) — Validation Memo

**Date:** 2026-05-28
**Doc:** docs/networking/tgmessage-routing-cleanroom.md (297 lines)
**Pre-anchored by:** docs/protocol/tgmessage-routing.md (Protocol mid #7, validated 2026-05-28)
**Result:** 1 material C, 4 Clar, 0 R; net status `partial` (matches sibling)

## Headline

The clean-room spec was written before protocol mid #7's C1 correction landed. It carries forward the
**pre-v5 mental model** that the C++ transport layer performs an automatic, unconditional, opaque
relay of all type-0x00 game messages on the host. Protocol mid #7 anchored this as FALSE: relay is
**per-handler**, **inside the FUN_0069FDA0 / FUN_0069F930 handler bodies**, **after dispatch**, gated
on `DAT_0097fa8a` (g_IsMultiplayer). Opcodes 0x06 (PythonEvent), 0x0D (PythonEvent2), 0x13 (HostMsg)
have NO SendToGroup call and are LOCAL-ONLY.

The *contracts* the clean-room spec promises ("clients reach other clients via host", "host forwards
game messages") are still substantially correct in observable outcome — because for the opcodes that
DO get forwarded, the per-handler relay produces a 1:1 fan-out indistinguishable from the
"automatic" model. But the implementation guidance is misleading: implementers who follow it will
either over-relay (forwarding 0x06/0x0D/0x13, like OpenBC currently does) or fail to understand the
3-mechanism model that controls who gets what.

## Cross-source v5 tagging

Most of the spec's load-bearing claims overlap with protocol mid #7 anchors. Where they agree, tag
`[v5-validated 2026-05-28 via docs/protocol/tgmessage-routing.md]`. Disagreements are flagged below.

## Live-Ghidra spot checks (3)

1. **FUN_0069F880 (MpgameHandlePythonEvent, 0x0069F880)** — decompile shows TGFactory_DeserializeObject → FUN_006f13c0 → FUN_006da300 (PostEvent). **ZERO SendToGroup, ZERO TGWinsockNetwork_SendTGMessage, ZERO Clone calls.** Confirms LOCAL-ONLY for both 0x06 AND 0x0D.

2. **FUN_006B63A0 (Connect handler, 0x006B63A0)** — decompile shows FUN_006B7410 (peer register) + raises event 0x60007 (ET_NEW_PEER_CONNECTED) + calls FUN_006B51E0 gated on `param_1+0x10E` (host flag). NOT a game-data relay; this is connection-coordination mechanism #3.

3. **FUN_0069FDA0 (GenericEventForward, 0x0069FDA0)** — decompile shows EXPLICIT per-handler relay:
   - `FUN_006a2fc0(s_Forward_008d94a0)` (FindGroupByName)
   - `TGWinsockNetwork_SendToGroup_Iterate(iVar2, param_1)` (the relay call)
   - Gated by `DAT_0097fa8a` (g_IsMultiplayer) and `DAT_0097fa78` (TGWinsockNetwork singleton)
   - vtable[6] Clone via `(**(code **)(*param_1 + 0x18))()` before the relay

Xrefs: NoMe `0x008E5528` xrefs at 0x0069E6F9 + 0x0069E715 (both inside MultiplayerGame_Ctor — confirms C2). Forward `0x008D94A0` xrefs at 0x0069E784 + 0x0069E7A0 (MultiplayerGame_Ctor — confirms ownership) + 0x0069FDF9 (FUN_0069FDA0 — confirms per-handler relay anchor) + 0x0069F997 (FUN_0069F930 TorpedoFire — same pattern).

## Corrections (1)

**C1 — Automatic Relay (C++ Layer) (lines 154–165) is FACTUALLY WRONG.**

The doc claims:

> "When the host receives ANY game message from a client via the transport layer, the host
> **automatically relays** it to all other connected clients. This relay is:
> - **Unconditional**: Every message is relayed, regardless of opcode or content
> - **Opaque**: The host does not read or interpret the message payload
> - **Immediate**: Happens during the network update tick, before dispatch"

Reality (anchored in protocol mid #7 C1 + spot-check #3 above):

- **Not unconditional.** Opcodes 0x06, 0x0D, 0x13, 0x14, 0x15, 0x17, 0x18, 0x1A, 0x29 do not relay. The relay-vs-absorb pattern is per-opcode.
- **Not opaque.** The decision-to-relay happens AFTER the dispatcher decoded the opcode and routed to a specific handler. The Clone+SendToGroup call is INSIDE the handler body (the FUN_0069FDA0 family for the relay-yes opcodes).
- **Not immediate / before-dispatch.** The handler runs the local effect first (e.g., posts to EventManager via FUN_006DA300), then conditionally clones and forwards. Order: receive → dispatch → handler.local-effect → handler.optional-clone-and-relay.

The behavioral consequence: a clean-room server that implements this section as written will over-relay 0x06/0x0D/0x13 (the OpenBC parity bug the protocol-side doc already calls out at line 766-769: "OpenBC currently relays 0x0D to all peers. That's WRONG."). The doc as written *causes* that bug.

**Suggested rewrite for clean-room:**

```
### Per-Handler Relay (C++ Layer)

When the host's dispatcher routes a game opcode to its handler, the HANDLER decides whether
to forward the message to other clients. Forwarding is performed by:

1. Cloning the message.
2. Calling SendToGroup with the "Forward" group (peers excluding the sender).

Some handlers forward (most weapon/movement events: opcodes 0x07-0x12, 0x19, 0x1B).
Some do not (PythonEvent 0x06 and 0x0D, HostMsg 0x13, CollisionEffect 0x15, lifecycle events 0x17/0x29).

A clean-room implementation MUST replicate this per-opcode policy — relaying messages that
the stock handlers don't forward will cause duplicate event delivery on clients.
```

## Clarifications (4)

**Clar1 — "Three C++ Dispatchers" header is correct, narrative under-explains.** (Line 72–85)

The header table correctly says THREE dispatchers (MultiplayerWindow, MultiplayerGame, NetFile).
But the spec never explains that all three are attached to the same `ET_NETWORK_MESSAGE_EVENT`
(0x60001) and run on every received message, each handling its own opcode subset and silently
ignoring others. This is the why-it-works of mod custom opcodes. Protocol mid #7 has it (lines
562–567, 600–620). Recommend adding one short paragraph to the clean-room spec.

**Clar2 — `NoMe` group creator unattributed.** (Lines 144–150)

The clean-room doc just says `"NoMe" group contains all peers except the local player` and
doesn't say who creates it. A naive reader will assume Python (because Python calls SendTGMessageToGroup
against it). Protocol mid #7 C2 anchored: **MultiplayerGame_Ctor at 0x0069E590** creates both NoMe and Forward.
For OpenBC: the group must be created by the equivalent of MultiplayerGame_Ctor's init path, not by
Python script init. Add: "Groups MUST be created during server-side multiplayer init, not by script."

**Clar3 — SendTGMessage targetID semantics is incomplete.** (Lines 138–142)

The doc gives only two modes: `target_id = 0` (broadcast) and `target_id = N` (unicast). Protocol
mid #7 anchored a THIRD mode: `targetID == -1` with the 4th argument as a `peer+0x1C` lookup key
(FUN_006BB9D0). Whether stock Python ever uses this mode is itself an open question (protocol mid
#7 OQ2). For a clean-room spec, the targetID == -1 mode should at minimum be documented as a
behavior the server MUST support if it accepts Python script calls from mods.

**Clar4 — "TGMessageFactory deserialize (raw messages)" missing from clean-room.**

Protocol mid #7 lists 3 routing mechanisms; the clean-room doc lists 2 (Automatic Relay + Python NoMe).
The missing mechanism is the connect-event broadcast (FUN_006B63A0 → FUN_006B51E0). This matters for
clean-room because join/leave events must reach other clients via a separate code path from game-data
events. A clean-room spec that elides this will produce a server where new players join but other
clients don't see them. Add as mechanism #3 in the routing section.

## Surviving claims (good)

- **Two-layer transport/application model.** (lines 14–25) Correct, matches protocol mid #7's "two
  independent type systems" framing.
- **7 transport types + factory table.** (lines 31–46) Numbers match; protocol mid #7 anchors are
  byte-confirmed.
- **Star topology + peer counts.** (lines 124–152) Correct. Clients have 1 peer (host); host has
  all-clients. Anchored in protocol mid #7 Star Topology section.
- **Silent-fallthrough behavior at dispatcher and Python.** (lines 80–84, 180–193) Correct and
  load-bearing for mod compatibility. Matches protocol mid #7's EAX>0x28 bias-bounds-check anchor.
- **Mod custom opcode mechanism.** (lines 204–249) Substantially correct. The mechanism described
  (Python writes opcode byte → wraps in type-0x32 → host opaque-forwards → client Python reads byte
  and dispatches) survives even with the C1 correction, because mods USE the relayed opcodes
  (0x06/0x0D bypass aside).
- **Behavioral guarantees enumeration.** (lines 252–274) Items 2-7 are correct. Item 1 ("host MUST
  relay all game messages") is WRONG in the same way C1 is wrong — should be re-phrased as "host MUST
  relay all game messages WHOSE HANDLER CHOOSES TO RELAY."
- **Implementation considerations.** (lines 280–297) Item 1 inherits the C1 bug. Items 2-6 are
  correct.
- **MAX_MESSAGE_TYPES = 43** (line 109). Matches protocol mid #7 anchor (SWIG-registered at
  0x00654F31, stored at 0x0090B490).
- **Opcode ranges table** (lines 230–238). Matches protocol mid #7 game-opcodes.md anchors.

## Open Questions (carry from protocol mid #7)

OQ1 — `peer+0x1C` semantics (still open in protocol mid #7; clean-room doc doesn't even mention this field — fine for clean-room, just don't claim two-modes-only).

OQ2 — Whether stock Python uses targetID == -1 (carries over; same question).

OQ3 — Chat 1:2 ratio mystery (the clean-room doc actually inadvertently addresses this at line
170–172: "this results in the message being sent twice (once by C++ auto-relay, once by Python)" —
but this hypothesis is FALSE under the C1 correction, because the C++ auto-relay doesn't exist for
opcode 0x2C. The 1:2 chat ratio remains genuinely unexplained).

## Verdict & status

**status: `partial`** (matches sibling protocol mid #7)

1 material correction (C1 — automatic-relay narrative), 4 clarifications (3-dispatcher narrative,
NoMe creator, targetID==-1, connect-event mechanism). Most factual content survives. The doc
should be EITHER refactored to remove the "Automatic Relay (C++ Layer)" section and replace with
the per-handler relay model, OR explicitly note that the automatic-relay claim was wrong and
update the behavioral guarantees + implementation considerations accordingly.

The clean-room doc is more dangerous than protocol mid #7 when its behavioral guidance is wrong,
because clean-room readers will follow it as a spec without cross-checking. Recommend re-publication
with C1 fix is HIGH PRIORITY.
