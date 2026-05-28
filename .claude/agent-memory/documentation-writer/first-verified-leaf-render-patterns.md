---
name: first-verified-leaf-render-patterns
description: 7 patterns for the first protocol-family leaf doc to reach `status: verified` (1 byte-level typo + 1 wording refinement, 110+ claims clean). Learned from collision-effect-protocol.md (protocol leaf #15).
metadata:
  type: feedback
---

# First-Verified-Leaf Render Patterns

When v5 validation surfaces a doc that's essentially clean — 110+ load-bearing
claims confirmed byte-by-byte, ZERO wire-format changes, the only corrections
are a byte-level typo and a wording refinement — the render is a fundamentally
different shape from `partial`-status renders. The doc gets `status: verified`
on first pass, no `confidence: low` rows, no Open-Questions blocking section.
The story is "this doc was right; here is the evidence trail." These patterns
ensure the verified-tier render reads as authoritative rather than triumphalist.

**Why:** A doc validated as `verified` becomes a foundation for downstream
docs. Reviewers should be able to skim the NOTE block and immediately see
both the status AND the 1-2 corrections that landed, without hunting through
the body for what changed.

**How to apply:** Use these patterns when the evidence packet says "ZERO
material corrections" + "status: verified" + "all N claims confirmed byte-by-byte"
+ "≤2 minor corrections". For docs with 3+ corrections OR any architectural
flip, use the leaf-cascade or class-identity patterns instead.

---

## Pattern 1: "First to reach verified" headline in NOTE block

When this is the family's first `verified` doc, lead the NOTE block with that
distinction in bold, then state the byte-level evidence ratio. The reader's
first sentence should be the campaign-level victory; the second should be the
proof-by-numbers.

```markdown
> [!NOTE]
> This doc is `status: verified`. All 110+ load-bearing claims confirmed
> byte-by-byte against the current Ghidra import (2026-05-28). The handler
> dispatch (CollisionEffectHandler at 0x006A2470, dispatcher thunk at
> 0x0069F491), distance gate constant (_DAT_008955C8 = 26.0f), damage cascade
> formula (...), all 4 damage constants byte-verified, vtable at 0x0089395C
> (17 slots), and 3 helper functions (...) all v5-validated.
```

Don't say "first" cheaply — only when the tracker row will actually flip
from pending to verified ahead of all siblings.

## Pattern 2: Critical-finding-confirmed callout

When the validation confirms a critical OpenBC finding (an
already-known-suspected behavior gap), make it the bold sentence inside the
NOTE block. This is the load-bearing signal for downstream clean-room work.

```markdown
> **Critical OpenBC finding confirmed**: stock dedi handler never recomputes
> contact points or force — only the distance gap (< 26.0f) is sanity-checked;
> the client-claimed force value is accepted as-is.
```

The bold inside a `> [!NOTE]` block is rare and should be reserved for the
single most load-bearing fact the validation produced.

## Pattern 3: Server-Side Authority subsection (load-bearing for clean-room)

For protocol docs where the validation establishes a key authority/recomputation
behavior, add a dedicated `## Server-Side Authority Note` subsection near the
top (before Wire Format). Wrap the headline in `> [!IMPORTANT]` (not NOTE),
and follow with bulleted negative-claim evidence.

```markdown
## Server-Side Authority Note

> [!IMPORTANT]
> **The stock dedi CollisionEffectHandler does NOT recompute collision contact
> points or force values from server-side object state.** It applies three
> gates (...) and then accepts the client-supplied force value as-is.

Full body of `FUN_006A2470` was decompiled this validation pass. There are:

- No `FMUL`/`FDIV` operations on the contact-point or force fields after deserialization
- No `STR` writes to `event+0x40` (collision_force) or `event+0x2C` (contact array)
- No re-derivation of contact points from ship world transforms
```

The bullet list IS the negative-claim's evidence. List what's absent
specifically, by instruction type or write target. This is the body backing
for the `address: null + note:` negative-claim row in the frontmatter.

## Pattern 4: Address-as-constant pattern callout

When the binary uses memory-address values as 32-bit type IDs (the address
itself is the namespace), document the pattern explicitly in a dedicated NOTE
block. Readers seeing `MOV [ESI+0x10], 0x008000FC` for the first time often
assume it's a dereference.

```markdown
## Address-Value-as-Constant Pattern

> [!NOTE]
> The values `0x008000FC`, `0x008000DC`, `0x00800050`, `0x00800053` are used
> as 32-bit event-type IDs via their **address values** (not data dereferences).
> The bytes stored *at* those addresses are irrelevant — those addresses often
> fall inside code sections. The engine uses the address itself as a unique
> global identifier (the address space is the namespace).
```

Place this NOTE block after the Event Registration section, before Related
Functions. The pattern is family-wide (all ET_ constants use it) so it's
worth one re-explanation per doc that has many ET_ references.

## Pattern 5: Real-code-but-undefined-fn disclosure

Mirror the leaf #14 pattern: when WriteToStream/ReadFromStream/ctor are
real-code-but-undefined-in-Ghidra (vtable-DATA xrefs only), disclose this
in a NOTE block under the section that first cites them. Cite the prologue
bytes inline so a future re-validation can re-confirm.

```markdown
> [!NOTE]
> `0x005871A0`, `0x00587300`, `0x00586D00` (ctor), `0x005AF9C0` (ShipClass
> sender), `0x006D29A0`, and `0x006D2D10` are **real code at those addresses
> but undefined as functions** in the current Ghidra DB. They have valid
> prologue bytes (`83 EC 30 53 55` for WriteToStream, ...) and clean
> disassembly. Their only xrefs are vtable-DATA writes (no plain CALLs to
> spot via auto-analysis). This mirrors the leaf #14 pattern of
> "real-code-but-undefined-fn cluster" caused by auto-analysis missing
> virtual-dispatch-only entry points.
```

Naming the prior leaf doc that established the pattern helps reviewers
recognize the recurring problem rather than thinking each doc independently
discovered it.

## Pattern 6: Damage-constants in-line byte-verified table

When the validation byte-verifies 3+ floating-point constants used in a
formula, embed them as a small NOTE-block table directly under the formula
itself, not in a separate "constants" section. This collocates the value
with its use site.

```markdown
> [!NOTE]
> All four damage constants were verified byte-by-byte from the binary this pass:
> - `_DAT_00888A78` = `0A D7 23 3C` = 0x3C23D70A = **0.01f** (dead-zone threshold)
> - `_DAT_008944BC` = `00 00 61 44` = 0x44610000 = **900.0f** (HP damage scale)
> - `_DAT_008944B8` = `00 00 FA 43` = 0x43FA0000 = **500.0f** (HP base offset)
> - Force-scale arg = `0x3FC00000` = **1.5f** (3rd parameter at call from ...)
```

The format is: raw-bytes `=` hex-DWORD `=` decoded-value (bold) plus role.
This lets a future pass byte-compare in either direction (binary → decoded
or decoded → binary).

## Pattern 7: Ghidra Annotations Applied section (verified-tier)

In verified-tier renders, the Ghidra Annotations Applied section is short and
declarative — not a debt list. Three subsections: function renames table,
global labels table, prototypes + plates one-liner. No "newly created" subdivision
(those are partial-tier signals).

```markdown
## Ghidra Annotations Applied [v5 2026-05-28]

### Function renames (6)
| Address | Old name | New name |
|---------|----------|----------|
| 0x006A2470 | Handler_CollisionEffect_0x15 | CollisionEffectHandler (kept canonical; plated this pass) |
...

### Global labels (7)
| Address | Label | Value / Role |
|---------|-------|--------------|
| 0x008955C8 | g_flCollisionBoundingGapCap | 26.0f — distance gate cap |
...

### Prototypes + plates
- Prototype set on `CollisionEffectHandler` (0x006A2470).
- Plate comment added on `CollisionEffectHandler` summarising: dispatcher
  route, 3 validations, distance gate constant, re-post semantics, and the
  "no server-side recomputation" finding.
```

The plates one-liner is a 2-3 line summary of what the plate says, not a copy
of the plate. Keep it brief — the plate itself lives in the Ghidra DB.

---

## What NOT to do in a verified-tier render

- **Don't add Open-Questions section** unless there's actual blocking work.
  Verified-tier docs may have a 1-2 line "Open Questions" section that says
  "None blocking" plus the downstream-scope cross-link. That's it.
- **Don't tag every section** with `[v5-validated YYYY-MM-DD]`. Tag the
  major reference tables (vtables, related-functions, wire format) but not
  every paragraph header. The frontmatter `validated:` date is the source of
  truth.
- **Don't restructure body sections** unless the corrections require it. A
  verified-tier render is mostly "frontmatter + NOTE block + tagged tables"
  — the body prose should look ~90% like the pre-v5 version. Reviewers
  should see "this was right" not "this got rewritten."
- **Don't claim `verified` in the tracker §2 row without inline justification.**
  The row needs the corrections summary AND the cross-link to §6.N so a
  downstream reader can verify the claim without scrolling.

## Cross-link to related patterns

Leaf-tier patterns this builds on:
- `[[leaf-cascade-render-patterns]]` — for leaves with 3+ corrections / class-identity flips
- `[[address-first-authoring]]` — for the "frontmatter renders correctly because the body cites addresses" precondition
- `[[stateupdate-render-patterns]]` — the mid-tier "ZERO material corrections" sibling; some patterns transfer (negative-claim disclosure, byte-verified-constant callouts)

When the next leaf doc validates clean, reach for these patterns first. If
corrections climb above 2 or any architectural flip surfaces, fall back to
the leaf-cascade pattern set.
