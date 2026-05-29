---
name: gameplay-damage-system-render-patterns-20260528
description: 9 render patterns for the FIRST gameplay-family v5 doc (damage-system.md, the gameplay damage hub) when v5 surfaces (a) ASCII-graph contradicts body text C2, (b) destruction branch misread parent-vs-type C1, (c) named-function discovery C3, (d) wire format precision C4, (e) gate-location framing C5, plus 4 clarifications and 3 open questions, with 10 byte-confirmed magic constants and full call-graph survival
metadata:
  type: feedback
---

# Gameplay Damage System — Render Patterns (2026-05-28)

First gameplay-family v5 doc. The damage hub is to gameplay what wire-format-spec.md was to protocol — central convergence point cross-referenced by every other gameplay doc. Rendered as `partial` with 5 corrections + 4 clarifications + 3 OQs.

## Why these patterns matter for the gameplay family

Gameplay-family docs differ from protocol-family docs in three structural ways:

1. **Magic-constant density is higher.** Protocol docs anchor on opcodes + offsets; gameplay docs anchor on formulas (raw\*0.1+0.1, raw\*900+500, max_damage=6000.0f). Every constant needs `DAT_xxxxxxxx` + byte-confirmed hex + IEEE float gloss.
2. **Same constant reused across multiple call sites.** `DAT_008887A8 = 0.5f` is the collision hard cap AND the weapon radius-halve multiplier. Frontmatter must use `function: shared` or note the dual role.
3. **Trace data is load-bearing.** Caller-chain counts (`765 = 536 + 122 + 107`) survive validation and become trace-anchor evidence rows. Don't drop the trace tables; promote them with `[v5-validated YYYY-MM-DD]` tags.

## Pattern 1 — NOTE-block: "survives v5 well" + numbered correction count + cross-anchor inventory

```markdown
> [!NOTE]
> **Gameplay-family damage hub doc — survives v5 well**. ZERO formula corrections;
> every magic constant (10 of them) byte-confirmed; 765-event trace math
> (= 536 weapon + 122 collision_contacts + 107 collision_position) verified via
> `get_function_callers`. 5 localized corrections (2 medium + 3 minor) + 4
> clarifications. Cross-anchored from protocol leaves #15 / #18 / #20 / #21 +
> networking leaf #11.
```

The "ZERO formula corrections; every magic constant byte-confirmed" phrasing telegraphs "the load-bearing claims survived". Readers know not to nervously re-derive collision damage formulas. The cross-anchor inventory ("leaves #15 / #18 / #20 / #21") signals that this doc is downstream of a mature protocol-family validation.

## Pattern 2 — C-numbered subsections AT the call-graph contradiction point, not at end of doc

C2 (ASCII graph claimed "ALL DAMAGE FLOWS THROUGH DoDamage" but body text contradicted) gets a dedicated `## C2 — ProcessDamage has 3 callers, not 1; Explosion bypasses DoDamage` subsection that:
- Quotes the contradictory pre-v5 text
- Shows the get_function_callers result as a 3-row table (caller / address / role)
- Restates the binary truth
- Names the OpenBC implication ("if you build a clean-room DoDamage that funnels through `+0x18` and `+0x140`, you will NOT trap explosion damage")
- Updates the ASCII graph above to match

The 5 C-sections are placed BEFORE Function Reference, immediately after the call graph — they're load-bearing context, not appendix material. Same shape as protocol leaf #19 (subsystem-integrity-hash).

## Pattern 3 — ASCII call graph amended in-place with `<-- see CN` inline pointers

The original pre-v5 ASCII graph at lines 32-39 was load-bearing but had wrong topology. Don't replace it; AMEND it. Pattern:

```
EXPLOSION INPUT (network opcode 0x29):
  Explosion_Net (0x006A0080)                        [v5-validated 2026-05-28]
    +-> reads objectID, CompressedVector4 (sign=1), 2x CF16 (damage, radius)
    +-> looks up target via FUN_00590A50 (type 0x8007)
    +-> calls ProcessDamage DIRECTLY (BYPASSES DoDamage)   <-- see C2
```

The `<-- see CN` inline pointer lets the reader scan the graph and follow up at the relevant correction subsection. Readers who only skim the graph still see the bypass.

The amended graph also adds an explicit "THE THREE CALLERS OF ProcessDamage" subsection — three reverse-arrow lines showing the full fan-in. Reverse-arrows (`<-`) are useful when the correction is "this thing has more inputs than the doc said".

## Pattern 4 — Magic-constant frontmatter rows have `function: <consumer>` not `function: shared` for the primary use

Each of the 10 magic constants got its own evidence row. Rule applied:
- `DAT_00893F28 = 0.1f` -> `function: DoDamage_CollisionContacts` (primary consumer)
- `DAT_008887A8 = 0.5f` -> `function: DoDamage_CollisionContacts` (primary consumer), with NOTE field "also reused as the 0.5 multiplier for ApplyWeaponDamage radius"
- `DAT_00888860 = 1.0f` -> `function: shared` (genuinely cross-cutting reference constant)

Don't use `function: shared` indiscriminately. Reserve it for constants without a primary consumer. For constants with a clear primary consumer + secondary use, name the primary and call out the secondary in the NOTE field. This makes the evidence-row search ("which functions touch DAT_008887A8?") work via grep against the `function:` field.

## Pattern 5 — Cross-anchored evidence rows have `address: <cross-anchor>` not `null`

The `DamageVolume` ctor at 0x004BBDE0 is cross-anchored from protocol leaves #20 and #21 (where it's called `ExplosionDamage_Ctor`). Pattern:

```yaml
- claim: "DamageVolume (a.k.a. ExplosionDamage in protocol-leaf docs) ctor at FUN_004BBDE0 builds a 0x38-byte struct..."
  address: 0x004BBDE0
  function: DamageVolume_Ctor
  confidence: high
  note: "Cross-anchored from protocol leaf #20 (cf16-precision-analysis.md) and leaf #21 (cf16-explosion-encoding.md). vtable at 0x0088C6C4. radius^2 precomputed at field[6]. AABB built inside FUN_004BBEC0."
```

The cross-anchor goes in the NOTE field, not as `address: null`. Use `address: null` only for negative claims or for claims that genuinely span multiple sites without one canonical address.

Also: when a cross-doc name differs (DamageVolume here vs ExplosionDamage in leaves #20/#21), use BOTH names in the claim text — "DamageVolume (a.k.a. ExplosionDamage in protocol-leaf docs)" — so search hits work from either entry point.

## Pattern 6 — Gate-location distinction: call-site framing vs callee-gate framing

C5 — "Notification IsHost gate is INSIDE FUN_00593F30, not at ProcessDamage call site" — got a dedicated correction subsection because the framing matters for OpenBC implementers. Pattern:

```markdown
## C5 — Notification IsHost gate is INSIDE FUN_00593F30

The pre-v5 doc framing read as if `ProcessDamage` itself checked `IsHost`. Actually
`ProcessDamage` calls `FUN_00593F30(1)` unconditionally. The gate lives inside
FUN_00593F30:

\`\`\`c
// inside FUN_00593F30 (called by ProcessDamage)
if ((DAT_008e5c1c != 0) && (DAT_0097fa89 == 0)) {
    // event-enabled AND IsHost == 0 (i.e. client)
    ...
}
\`\`\`

**OpenBC implication:** if your damage receiver consults the
`(event_enabled && !is_host)` predicate at the call site, you'll match the
pre-v5 doc framing but you won't match the binary's flow if you ever decide to
fire FUN_00593F30 from a different caller — the gate stays inside the callee.
Keep the gate co-located with the notification builder.
```

The OpenBC implication paragraph makes the correction load-bearing. Without it, this looks like pedantic micro-refactoring; with it, the reader sees why the framing change matters.

## Pattern 7 — Disable-conditions table gets cross-references to corrections

The "Conditions That Disable Damage" table picks up `(see Clar2)` and `(see C5)` annotations:

```markdown
| `this+0x18 == NULL` | DoDamage gate | No NiNode -> DoDamage path silently dropped (Explosion_Net path NOT affected — bypasses) |
| `this+0x1B8 == 0.0` | ProcessDamage | Damage zeroed via multiply (see Clar2) — not bypassed via guard |
| `DAT_0097fa89 == 1` (IsHost) | Notification callback gate (inside FUN_00593F30, see C5) | Damage applied but NO event callback fires (by design) |
```

The annotations in-line tell the reader "this row is correct but the mechanism is subtler than the original doc implied — look at the named correction subsection". Doesn't add length; recovers nuance.

## Pattern 8 — Open Questions section with promotion-path framing per question

Three OQs at end of doc:

```markdown
## Open Questions

- **OQ1**: What writes `Ship+0x140` (the damage-target NiNode)? [...]. **Needs write-xref search.**
- **OQ2**: What populates `Ship+0x128` / `Ship+0x130` [...]. **Likely Ship__SetupProperties (0x005B3FB0) or a callee** — needs trace.
- **OQ3**: Does `FUN_00595890` [...]. The third ProcessDamage caller's run-path needs trace confirmation.
```

Each OQ ends with a bold-text **next step** (write-xref / callee trace / runtime trace). Doesn't promote OQs to body subsections (that would be `verified` shape, not `partial`). The bold-text next step is what makes these promotable in a future pass.

## Pattern 9 — Trace data DOESN'T get "Historical" header treatment for gameplay-family

Protocol leaf #22 (message-trace-vs-packet-trace) marked entire sections "Historical". Gameplay damage doc does NOT do that — the trace counts are load-bearing (they justify the 3-caller-on-DoDamage / 765-event-total math). Pattern: keep a top-of-section blockquote that contextualizes, but tag the addresses `[v5-validated YYYY-MM-DD]`:

```markdown
## Stock Dedi Trace Data (Baseline)

> Trace observations are time-stamped 2026-era stock-dedi runs. All cited addresses
> verified this pass via `get_function_callers`; the math `765 = 536 + 122 + 107`
> is self-consistent. Best treated as **historical evidence for cross-referencing**,
> not as live-binary facts.

### Session 2: Multi-Player Combat [...]

**Verified caller chains (return addresses):** [v5-validated 2026-05-28]
```

Per-table v5 tag at the heading line (not on each row). The block-quote up top sets the epistemic frame (these are runtime observations, not static binary facts); the v5 tag on the address list says the upstream call-site addresses themselves resolve correctly.

## Rule: don't restructure body for cascade-only or framing-only corrections; DO restructure for graph-topology corrections

C1 (parent-vs-no-parent destruction branch) and C2 (3 callers not 1) BOTH required graph topology updates — the call graph diagram had to be amended. C3 (named function discovery) and C4 (wire format precision) did NOT — they're cite-and-cross-link updates only. C5 (gate location) is a framing-only correction.

Rule: structural rework happens ONLY for corrections that change the topology readers see in the ASCII diagram. Wire-format precision goes into the Function Reference subsection. Gate-location framing goes into a C-subsection but doesn't ripple to the diagram.

## What I would do differently

- I think the call graph should have promoted the 3-callers-on-ProcessDamage finding to its own labeled subsection ("THE THREE CALLERS OF ProcessDamage:") within the diagram, not just an inline note. I did that this pass; it works. Future gameplay docs with fan-in corrections should follow.
- The DamageVolume struct table got duplicated between this doc and protocol leaf #21. Future passes could decide which doc is canonical and have the other refer with `## DamageVolume — see [doc] for canonical layout`. For now, both render the layout inline because they have different downstream readers (RE engineers for gameplay, network implementers for protocol).
