---
name: gameplay-repair-batch-render-patterns-20260528
description: Render patterns for FIRST gameplay-family batched-sibling pass (repair-system + repair-tractor-analysis). 3 corrections + 2 clarifications in the heavier doc, 1 clarification in the lighter doc, shared anchors across both.
metadata:
  type: feedback
---

# Gameplay Repair Batched-Sibling Render Patterns (2026-05-28)

Rendered `docs/gameplay/repair-system.md` + `docs/gameplay/repair-tractor-analysis.md` as a batch from ONE shared evidence packet. First batched-sibling render in the gameplay family. Both docs went `partial`. Eight new Ghidra functions created this pass, all named via the function-name list in the packet (HostEventHandler still needs a Ghidra rename — flagged for follow-up).

This render is the gameplay-family analog to the protocol cf16-precision/cf16-explosion batched pass. The shape carries over with one notable departure (see Pattern 8 below).

## Pattern 1 — Asymmetric NOTE-block headlines (heavier doc bold-counts; lighter doc cross-references)

The heavier doc (repair-system.md) gets a NOTE block that leads with **bolded triage** of all corrections + clarifications:
- "v5-validated 2026-05-28 — 3 corrections + 2 clarifications."
- Then C1 (HIGH, wire format) / C2 (MED, event label) / C3 (MED, handler count) inline with section anchors.
- Clar1 / Clar2 brief one-line summaries.
- OpenBC cascade callout at the end of the NOTE.

The lighter doc (repair-tractor-analysis.md) gets a NOTE block that leads with **cross-reference to the batch partner**:
- "v5-validated 2026-05-28 — 1 clarification (events-table row split)."
- Names the partner doc as the source of full corrections.
- Explicit "For full wire-format corrections see the batch partner: [repair-system.md]".

This asymmetry signals that the lighter doc inherits material findings without duplicating them — readers go to the canonical doc for wire format.

## Pattern 2 — Shared Ghidra-creation count disclosed in BOTH NOTEs

When a batched pass creates Ghidra function bodies that BOTH docs reference, name the function-creation count in each NOTE block:
- Heavier doc: "Six Ghidra function bodies were created this pass (...) plus RepairSubsystem::Update which had an existing body but was undefined to Ghidra's auto-analyzer."
- Lighter doc: "Two Ghidra function bodies were created this pass on the tractor side: TractorBeamSystem::Update (0x00582460) and RepairSubsystem::Update (0x005652a0)."

The lighter doc names only the bodies it cites. Don't enumerate functions the doc doesn't reference — it confuses readers.

## Pattern 3 — Fabricated-class correction headline pattern (C1)

When v5 invalidates a fabricated class name carried forward from pre-v5 RE (e.g., "TGSubsystemEvent (0x0101)" which doesn't exist), use a dedicated IMPORTANT block in the body section where the claim lives, AND a triage row in the headline NOTE.

Template:
```
> [!IMPORTANT]
> **C1 — Wire-format factory IDs corrected.** The pre-v5 doc uniformly claimed
> "Factory: <fabricated_class> (0xNNNN), N bytes total" for all three Path 1 events.
> That was wrong on two counts: (1) "<fabricated_class>" is a fabricated class —
> factory 0xNNNN IS <real_class>; (2) the three events use **two different factories**
> with different payload sizes.
>
> | Event | Pre-v5 (wrong) | Actual (byte-confirmed) |
> ...
>
> Evidence: <function> (0xADDR) calls TGAlloc(0xN) + <ctor> (...)
```

The two-axis correction (the class name AND the factory diversity) gets a two-column table. Calling out "fabricated class" explicitly signals that this is a known-bad pattern, not just a typo.

## Pattern 4 — Three-Layer Registration architecture for C3 (count-of-bindings correction)

When v5 surfaces additional registration sites that pre-v5 missed (e.g., per-instance bindings in a SetPlayer hook), restructure the registration section into NUMBERED LAYERS:

- Layer 1 — Handler Name Registration (static-init lookup table)
- Layer 2 — Per-Class Event-Type Routing (class-wide static routing)
- Layer 3 — Per-Instance Event-Type Bindings (instance-specific, from SetPlayer)
- Total Bindings — N (summary count)

Each layer gets its own subsection with its OWN function table. This makes the architecture readable AND surfaces why the pre-v5 count was wrong (it only counted Layers 1+2).

This pattern is reusable for any subsystem where event registrations split between static and per-instance paths — common in the TG event system.

## Pattern 5 — Inverted-but-effective Clar1 (mechanism wrong, outcome same)

When pre-v5 prose says X about a mechanism but the binary truth is NOT X with the same outcome, render the correction inline at the affected section, NOT as a separate body subsection. Use a `>` blockquote labeled "**Clar1 — <one-line mechanism summary>.**" with structure:

1. Quote the pre-v5 wording
2. State the binary truth (which mechanism is actually invoked)
3. State the net effect (which matches pre-v5)
4. Disambiguate why the pre-v5 wording was wrong (typically: misread of an `if (X != 0)` gate)

The reader needs to know that the net behavior is unchanged AND that the mechanism description was wrong. Both pieces matter; bury neither.

Used in repair-system.md for the "event type override: 0 (preserve original)" inversion. Override IS non-zero; the type IS forced.

## Pattern 6 — Inline-offset Clar2 (typo-level fix)

For low-severity inline-comment typos (e.g., "subsystem+0x0C float field check" where the actual offset is +0x30 because the decompiler shows `param_2[0xc]` = INDEX not OFFSET), apply the fix in-place at the offending comment with a brief `[v5-validated 2026-05-28]` tag and a one-line explanation:

```
// 2. Check if subsystem condition > 0.0  (read at subsystem+0x30)
// [v5-validated 2026-05-28] Decompiler shows param_2[0xc] = param_2 + 0xC*4 = +0x30.
// The +0x30 layout in the instance table is correct.
if (subsystem->condition > 0.0f) {
```

Don't promote a typo-level fix to a body subsection. The inline comment + tracker entry is sufficient.

## Pattern 7 — Two-row split for sender-path ambiguity (events table Clar in tractor doc)

When pre-v5 collapses two sender paths into one row (e.g., "0x008000DF → opcode 0x0B (Host → All)" conflating host-auto path and client-manual path), SPLIT INTO TWO ROWS keyed by the SAME event ID:

| Event ID | Name | Wire Opcode | Direction | Notes |
|---|---|---|---|---|
| 0x008000DF | ET_ADD_TO_REPAIR_LIST | **0x06 (PythonEvent)** | Host → All | host-auto path detail |
| 0x008000DF | ET_ADD_TO_REPAIR_LIST | **0x0B (AddToRepairList)** | Client → Host → All | client-manual path detail |

Bold the wire opcode in each row so the reader sees the wire-path difference at-a-glance. Add a trailing `>` blockquote naming the canonical wire-format details in the batch partner doc.

This pattern is canonical for any event that travels on multiple wire opcodes depending on origin.

## Pattern 8 — Open Questions go in the heavier doc only (departure from cf16 batch precedent)

In the cf16 batched pass, both docs ended up `verified` and neither carried an Open Questions section. Here, the heavier doc (repair-system.md) carries 2 OQs (OQ1 = unanchored 0x0B sender, OQ2 = unanchored 0x0B factory). The lighter doc does NOT duplicate them — it cross-links to `[OQ2 in repair-system.md](repair-system.md#open-questions)` from the events table.

Rule: when a batched sibling pair has OQs that span both docs' subject matter, put them in the doc that owns the affected wire format / handler chain. The other doc cross-links. This avoids the "where's the canonical OQ list?" question.

## Pattern 9 — OpenBC Cascade as `>` blockquote with bolded-table replacement

The OpenBC clean-room cascade flag goes in the heavier doc only, near the end before Related Documents, as a `>` blockquote section. Inside the blockquote: bolded headline ("**C1 propagation needed.**"), one paragraph naming the OpenBC target spec, then a bullet-list showing the corrected values that need cascading:

> - **0x008000DF** → factory 0x0100 (base TGEvent), 16B payload
> - **0x00800074** → factory 0x010C (TGObjPtrEvent), 21B payload
> - **0x00800075** → factory 0x010C (TGObjPtrEvent), 21B payload

The cascade flag does NOT go in the lighter doc — the lighter doc cross-links via its NOTE block to the batch partner.

## Pattern 10 — Repair-rate formula tags promote in BOTH docs

For shared algorithms that BOTH docs cite (the repair rate formula appears in both), apply `[v5-validated 2026-05-28 — byte-confirmed in <function> at 0xADDR]` directly under the formula heading in EACH doc, with a matching `address: 0x005652a0` evidence row in BOTH frontmatter blocks. Readers landing on either doc see the same provenance.

Don't worry about duplicating the formula text — that's by design for read-anywhere docs. What matters is that the v5 tags MATCH on date and address.

## What NOT to do

- **Don't move tractor RE into repair-system.md.** The tractor side has its own sibling doc; copying tractor content into repair-system.md would create a synchronization problem on future passes.
- **Don't promote Clar2 (inline-comment typo) to a body subsection.** Inline fix + one-line `[v5-validated]` tag is sufficient.
- **Don't restructure the body for cascade-only corrections.** This is `partial` shape — preserve original section order (readers may have inbound links).
- **Don't omit the cross-link pointer in the events-table split.** When a row splits, ALWAYS point readers to the canonical wire-format doc for byte-level detail.

## Architectural finding

This is the FIRST gameplay-family doc to land an OpenBC clean-room cascade flag. The cf16 batched pair raised no OpenBC concerns because OpenBC didn't have wire-format claims for explosion encoding. Repair does — `../OpenBC/docs/repair-system.md` is listed in CLAUDE.md as a clean-room target. Future gameplay docs that cascade to OpenBC specs should follow this pattern: dedicated `## OpenBC Clean-Room Cascade` section near the end with bolded-bullet correction summary.

## Cross-doc reconciliation note

Both docs share the repair rate formula, AddSubsystem logic, instance layouts, and function table. The heavier doc (repair-system.md) is the canonical source for wire format (Path 1a / 1b / 2 / 3); the lighter doc (repair-tractor-analysis.md) is the canonical source for tractor mechanics (6 modes, force formula, multiplicative drag, "no direct damage" negative claim). When v5 corrections affect both, fix at the canonical source and cross-link the other.

## Follow-up flagged but NOT touched in this pass

- Ghidra rename: HostEventHandler at 0x006a1150 → MultiplayerGame__HostEventHandler (per evidence packet's "promote naming" suggestion).
- gameplay/v5-validation-status.md tracker row updates (deferred per instructions).
- CLAUDE.md Documentation Index check (deferred per instructions).
- MEMORY.md index entry pointer to this file (deferred per instructions).
