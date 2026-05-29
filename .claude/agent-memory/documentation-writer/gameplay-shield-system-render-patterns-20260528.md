---
name: gameplay-shield-system-render-patterns-20260528
description: 7 render patterns for gameplay-foundation docs with semantic-relabel correction (ctor-time vs runtime field identity), fabricated example table, function-name swap, and gate-threshold off-by-one. Learned from shield-system.md (gameplay foundation #2, 2026-05-28).
metadata:
  type: feedback
---

# Render Patterns — gameplay/shield-system.md (gameplay foundation #2, 2026-05-28)

7 patterns for rendering a v5 partial-pass on a gameplay-foundation doc whose algorithm/wire-format/constants are byte-confirmed but whose bookkeeping fields, example table, and one function name need correction.

**Why:** The shield-system pass had four correction shapes that show up across foundation docs and weren't previously cataloged: (1) **semantic relabel** of a field whose ctor-time identity differs from its runtime identity (C1), (2) **function-name swap** where pre-v5 ReadStream → v5 WriteState by inspecting first instruction + vtable slot (C2), (3) **fabricated example table** that needs replacement from script source (C3), (4) **gate-threshold off-by-one** where the doc said `== 0` but the binary says `< 1.0` (C4). Each shape gets a slightly different render pattern.

**How to apply:** When the validation memo carries a mix of (semantic-relabel + function-rename + table-replacement + threshold-fix), use these 7 patterns. They scale from foundation-tier to leaf-tier docs.

---

## Pattern 1 — NOTE block headline counts categories AND bolds severity

The NOTE block at the top of the doc opens with a one-line verdict ("v5 partial pass — algorithm, wire format, and constants are byte-confirmed") followed by `4 corrections (C1 HIGH: ..., C2 HIGH: ..., C3 MEDIUM: ..., C4 LOW: ...) + 6 clarifications + 2 OQs`. The HIGH/MEDIUM/LOW severity is **bolded inline** with the C-tag.

Why: readers scanning the NOTE need to know severity without reading each correction body. Bold-severity-inline lets the eye triage.

Don't: list corrections as a separate bullet list inside the NOTE — that bloats the block and disrupts the at-a-glance triage.

---

## Pattern 2 — Semantic relabel (ctor-time vs runtime identity) gets a dedicated `## C1` section + struct table rewrite

When the validation memo says "field +0x48 was labeled X based on ctor inspection but its runtime identity is Y because consumer Z reads it as Y", the doc gets a dedicated `## C1 — <field> is Y at runtime (NOT X)` section placed between Overview and the struct table.

The C1 section has three subsections:
1. **The ctor-time identity** — quote the ctor line, name the random-seed constants
2. **The runtime identity** — name 2+ consumer functions and what they do with the field
3. **Reframe** — name the corrected field label, explain how the doc author got confused
4. **OpenBC impact** — 1-2 lines on what implementers must do differently

Then in the actual struct table, the field row uses the corrected name in **bold** and a NOTE column that says "Ctor seeds with `rand() * 0.33 * 3.05e-5` for tick stagger; hardpoint scripts overwrite at config time. Read by `<consumer1>` and `<consumer2>`. **See C1.**"

Why: ctor-vs-runtime mismatches are the most pernicious semantic error class in this codebase. Naming the consumer functions is what disambiguates — saying "it's a power budget at runtime" is less load-bearing than "PoweredSubsystem_GetNormalPowerWanted at 0x005623d0 reads it".

Don't: drop the ctor-time identity entirely from the doc. The random-seed behavior IS real and other code paths (event-system tick stagger) may still rely on it for un-configured ships.

---

## Pattern 3 — Function-name swap (C2) gets a short `## C2` section + table-row callout

When pre-v5 named a function `ReadStream` and v5 disasm says it's `WriteState`, the C2 section is **short** (3-4 paragraphs). Lead with the first instruction (`calls PoweredSubsystem__WriteState`), name the vtable slot it uses (`vtable[0x54] = write float`), cite a cross-doc that already had the right name (`docs/analysis/server-side-computation-model.md:436`), and note what the **read** path would look like for completeness.

Then in the function-reference table at the bottom of the doc, that row uses **bold** for the corrected name and a parenthetical `(C2 — pre-v5 misnamed `ReadStream`)`.

Why: name swaps are simple enough that a short body section is enough; the readers who care are the implementers reading the function-reference table, so the table-row callout is what they'll actually hit.

Don't: rebuild the entire function-reference table just to fix one name — keep the table stable and use the bold + parenthetical to flag the change.

---

## Pattern 4 — Fabricated example table (C3) gets a side-by-side "Prior doc claim" column

When the validation memo replaces a per-ship example table where N of M rows were wrong, the corrected table includes a `Prior doc claim` column showing each old value and labeling it `WRONG` / `OK` per row. The corrected values go in the leading columns, the old (wrong) values in the trailing `Prior doc claim` column.

Format:
```
| Ship | Front/Top/Bottom MaxShield | L/R/Rear MaxShield | ChargePerSecond | Prior doc claim |
|---|---|---|---|---|
| Sovereign | 11000 | 5500 | 12 (all facings) | "6000 / 15" — WRONG |
| ...
| Warbird | 4000 | 4000 | 8 | "4000 / 8" — OK (only correct row) |
```

Also include a closing line that **names the source** (`reference/scripts/ships/Hardpoints/<ship>.py`) and a sentence framing values as "per-ship hardpoint properties, not engine constants" — readers who came looking for "the shield charge rate" need to know there isn't one canonical number.

Why: explicit OK/WRONG-row tagging lets readers verify against their own memory of the old doc; pointing at the script source path lets them go check.

Don't: silently replace the table — readers who quoted the old values elsewhere need to know which rows were wrong.

---

## Pattern 5 — Gate-threshold off-by-one (C4) gets a `## C4` section with code transcript

When the doc said `value == 0` and the binary says `value < 1.0`, the C4 section includes a short C-pseudocode transcript of the actual gate:

```c
// IsShieldBreached at 0x0056a620
bool IsShieldBreached(ShieldClass* this, int facing) {
    if (this->curShields[facing] >= 1.0f && this->shieldDamaged[facing] == 0) {
        return false;  // NOT breached
    }
    return true;  // breached
}
```

Plus a "practical effect is identical for normal gameplay but matters for replication parity" framing sentence. Then update the gate-conditions summary table at the bottom of the doc with the correct gate (NOT the simplified `== 0`).

Why: thresholds that only matter at the boundary value (e.g., during depletion frame) are easy to miss; the C transcript + the explicit "matters for OpenBC replication parity" sentence is what justifies the correction even when behavior is indistinguishable in practice.

Don't: skip C4 because behavior is identical in normal play. OpenBC implementers writing fresh code will hit the boundary case and produce a different replicated state.

---

## Pattern 6 — Clarifications (6 Clar-tags) are inlined at their original sections, NOT collected at the end

When the doc has 6 clarifications that refine existing sections (e.g., "the random seed is product of TWO constants" refining the ShieldProperty section), each Clar-N tag is placed **at the section it refines** as a parenthetical or inline note (`(Clar2 — pre-v5 presented as single combined constant; binary uses two)`). The body sections aren't restructured.

The only Clar that gets standalone treatment is `Clar1` (struct-layout addition: 3rd float[6] array + single float), and even then it's just an additional row in the existing struct table with `(Clar1 — purpose unknown, OQ2)` as the NOTE.

Why: clarifications are non-blocking refinements; readers benefit from finding them in context, not at the bottom in a "clarifications appendix". The reader scanning the ShieldProperty struct table sees Clar1 inline and doesn't need to jump elsewhere.

Don't: bundle clarifications into a `## Clarifications` section — that detaches them from the context they refine and reads as scolding the original author.

---

## Pattern 7 — Constants table gets a `0x00888dbc` row added explicitly when Clar2 establishes a two-constant pattern

When the validation memo says "the random seed uses TWO separate constants `_DAT_00892fc0` and `_DAT_00888dbc`" but the original constants table only had the first, the corrected constants table gets a NEW row for the second constant, and the first constant's "Meaning" column adds `(Clar2 — first of two; combined product ≈ 1.007e-5)`.

Same pattern for `0x00888b58`: pre-v5 listed only as epsilon; v5 finds it's **dual-use** as the next-tick interval for ScheduleShieldEvents. Updated meaning column says `Epsilon AND next-tick interval for ScheduleShieldEvents events 0x6f/0x70/0x71 (Clar5 — dual-use)`.

Why: constants that get reused in two different contexts are easy to lose track of — flagging the dual-use in the meaning column means a reader looking up either context finds both anchors.

Don't: split into two rows for a single .rdata address. It's one constant; the meaning is "constant value 1e-6 used in two places."

---

## What NOT to do (negative lessons from this pass)

- **Don't promote OQ4 from the validation memo to a `## Open Questions` section** if it's already-covered by the body's Clar4 mention of the code-gap. The validation memo's "OQ4: needs Ghidra promotion" is satisfied by the doc body saying "needs Ghidra promotion for full analysis" inline at the code-gap section. Adding a duplicate OQ4 entry at the bottom is redundant. (In this pass I kept it as OQ3 only because validation memo had it; the inline mention in section 3 is the primary anchor.)
- **Don't update the gate-conditions summary table by just appending a new row** — replace the existing row(s) that had the wrong gate. The table is a quick-reference; readers shouldn't see both the old wrong gate and the corrected one.
- **Don't bold the field name in the struct table when the field's old name was technically correct (just incomplete)** — only bold when there's a true rename. For Clar1's float[6]@+0x130 and float@+0xD8, the rows are NEW additions, not renames, so no bolding.

---

## Frontmatter evidence row patterns (specific to this pass)

- **Vtable rows have `function: null`** (they're not functions). Address is the vtable address. Use `note:` to cite the ctor/dtor xrefs.
- **Constants get `function: null`** as well. Address is the .rdata address. Note field describes what reads it and what the value is.
- **The `_DAT_00892fc0` row uses `function: ShieldProperty__ctor`** because the constant is only meaningful in the context of that consumer — but the address points to the .rdata constant, not the function. This is a judgment call; readers searching by constant address will find it via the address column.
- **Effective scores** copied from the validation memo's bottom table. Only cite for functions where the memo computed them (NormalToFacing, BoostShield, AreaEffectDamage, GetShieldFacingFromRay).
- **`completeness` of 0.0 with `effective` of 89.0** is fine — it means the function is leaf-tier with unrenamed magic ints but byte-confirmed. The validation memo gave these scores; render them.

---

## File outputs

- `docs/gameplay/shield-system.md` — fully rewritten in v5 shape (frontmatter + 4 corrections + 6 clarifications + 3 OQs)
- This memo

## Untouched (per pass instructions)

- `docs/gameplay/v5-validation-status.md` — batched at family close
- `.claude/agent-memory/documentation-writer/MEMORY.md` — batched at family close
- No companion docs modified
