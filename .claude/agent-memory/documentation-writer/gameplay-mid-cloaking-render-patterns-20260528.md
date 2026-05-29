---
name: gameplay-mid-cloaking-render-patterns-20260528
description: Render patterns for cloaking-state-machine.md (gameplay mid #8, 518 lines) v5 pass — 4 corrections (2 HIGH + 1 MED + 1 LOW) + 3 clarifications + 2 OQs. Notable: HIGH-severity field-label correction with semantic-correct framing (C1), event ID swap + missing event row added (C2), default-constants-statically-determinable correction with OpenBC cascade flag (C3), and Ghidra-symbol-mis-name disclosure (C4).
metadata:
  type: feedback
---

# Cloaking state machine render patterns (gameplay mid #8)

## Context

- Doc: `docs/gameplay/cloaking-state-machine.md` — 518 → ~700 lines post-render
- Verdict: `partial`
- Validation memo: `gameplay-mid-cloaking-validation-20260528.md`

## Patterns

### P1 — Field-label correction with "semantic-correct" framing

When the body of a pseudocode block describes the right behavior but uses the wrong field name (C1: prior doc said `+0xAD tryingToCloak`, binary truth `+0xAC isFullyCloaked`), the render pattern is:

1. NOTE block headline says HIGH severity and names the wrong vs right field
2. Body section header `### C1 — StopCloaking gate checks isFullyCloaked (+0xAC), not tryingToCloak (+0xAD)`
3. Three-block disclosure: **Prior doc said** → **Binary truth at <address>** → corrected pseudocode
4. Inline disasm with the exact CMP instruction highlighted (`<-- C1` inline comment)
5. Closing sentence: *"Semantic meaning was correct in prior doc — only the field label was wrong."* This is load-bearing because it tells the reader the doc's narrative still holds, only one label moved.

This framing avoids the modder reading the NOTE and concluding "the whole cloak logic was wrong" when in fact only one byte offset was mis-labeled.

### P2 — Event ID swap with missing-row added to table

C2 was a two-part correction: (a) prior doc's row for 0x00800078 said ET_CLOAK_BEGINNING but binary string at 0x009106A0 is `ET_CLOAK_COMPLETED`, and (b) the actual ET_CLOAK_BEGINNING (0x00800077, string at 0x009106B4) was missing from the doc entirely.

Render pattern:

1. NOTE block names BOTH halves of the swap in one bullet
2. In the body Event IDs table:
   - Bold the new row: **`0x00800077`** with note "[C2 — added this pass]"
   - Annotate the existing 0x00800078 row inline: **`ET_CLOAK_COMPLETED`** [C2] with cross-doc note pointer
3. After the table, a *paragraph-level reminder* explains the swap in one sentence ("the event-ID column used to label 0x00800078 as ET_CLOAK_BEGINNING. Binary truth: ...")
4. Also annotate every other site in the doc that mentions either ID — InstantCloak section, CloakComplete section, Function Address Summary table — with `[C2]` tags. The 0x00800078 reference shows up 4-5 times in the doc; each needs the corrected label.

This is heavier than a single-row table edit because the event ID is a piece of vocabulary that recurs across the body.

### P3 — Default-constants-statically-determinable correction with OpenBC cascade flag

C3 was unusual: the prior doc said the default values "cannot be verified from static analysis alone since DAT_008e4e1c is a runtime-modifiable global". This is *epistemically wrong* — the .rdata bytes ARE statically determinable; the doc just hadn't read them. And the bytes contradict OpenBC's clean-room claim of "3.0 seconds".

Render pattern:

1. NOTE block uses MED severity (not HIGH — wire format is unchanged), but boldfaces the OpenBC-impact: **"OpenBC clean-room spec needs cascade update"**
2. Dedicated `### C3 — Default constants are statically determinable` subsection inside the Transition Timer section
3. Two-row table showing **Address / Raw bytes / IEEE 754 / Field / Default** — verbatim raw hex bytes so the reader can audit
4. Blockquote `> ` OpenBC clean-room cascade flag IMMEDIATELY after the table:
   > **OpenBC clean-room cascade (2026-05-28)**: The OpenBC clean-room spec uses "3.0 seconds" for cloak transition. Binary truth: CloakTime = 5.0f at DAT_008E4E1C. OpenBC clean-room implementations should update to 5.0 seconds for stock parity.
5. Repeat the OpenBC cascade flag in the **Comparison with OpenBC Cleanroom Spec** section near the doc bottom — this section was already there in the pre-v5 doc and is where modders look first
6. Update the **Global Constants** table to add a "Default value" column showing **5.0f** and **1.0f** in bold (with C3 inline tag)

The cascade flag pattern is one *visual* blockquote (`>`) repeated at TWO places: at the source of correction AND at the OpenBC comparison section. The repetition is intentional — it ensures a modder skimming the doc sees the cascade regardless of which section they land in.

### P4 — Ghidra-symbol-mis-name LOW correction (binary truth still correct)

C4 was the lightest-weight correction: the doc's address claim (`FUN_00566d10`) is correct, but Ghidra DB labels that symbol `SensorSubsystem_Ctor`. This is a pre-v5 annotation-script artifact, not a doc bug.

Render pattern:

1. NOTE block lists it as LOW severity in the headline
2. Body subsection `### C4 — Ghidra symbol for ctor mis-labeled` near the Object Layout section (because that's where the ctor is first cited)
3. NOTE block inside that subsection lists 4 things that confirm CloakingSubsystem identity:
   - Vtable address written
   - Parent ctor called
   - Fields zeroed
   - +0xC0=2 set
4. Closing sentence: *"The doc's address claim is correct. Ghidra rename pending in a separate handoff (target: CloakingSubsystem_Ctor)."*
5. Annotate the Function Address Summary table inline: `CloakingSubsystem::ctor (Ghidra DB: SensorSubsystem_Ctor — C4)`

The pattern is: don't change the doc's claim, just annotate that the Ghidra symbol diverges, and point at the separate Ghidra cleanup handoff. Don't promote LOW corrections to the body proper — keep them in a single dedicated subsection + inline tags.

### P5 — Companions block including OpenBC cascade target

Companions for cross-doc cascade docs should explicitly list the OpenBC clean-room target with the relative path `../OpenBC/docs/...`. This is the harvest point for the next time someone runs the clean-room sync — they know which OpenBC doc needs updating from this doc's C3 correction.

```yaml
companions:
  - docs/gameplay/power-system.md
  - docs/gameplay/shield-system.md
  - docs/protocol/stateupdate-subsystem-wire-format.md
  - docs/engine/tg-hierarchy-vtables.md
  - ../OpenBC/docs/cloaking-system.md
```

### P6 — Function-creation NOT this pass (no `create_function` markers)

Unlike power-system.md (which had 26 Ghidra renames), this validation did not run renames or create any Ghidra functions. Pattern: don't include "Ghidra Annotations Applied" or "newly created" sections — they don't apply. Frontmatter `note:` lines can still reference Ghidra symbol mis-naming (e.g., the SensorSubsystem_Ctor case in C4 — handoff is separate).

### P7 — Two-OQ Open-Questions section structure

Two open questions with promotion-path framing:

- **OQ1**: identifies a non-Ghidra discoverable thing (ET_CLOAK_BEGINNING consumer) — promotion path = "cross-reference search through SWIG handler registries"
- **OQ2**: a doc-address quibble (prior doc cited 0x005B2660; functional path verified but exact byte not pinned) — promotion path = "future cross-reference if revisiting"

For mid-tier docs with 0-2 OQs, the section can be a simple bulleted list with each item leading with `**OQ# — <one-line statement>**.` followed by a sentence or two of context. No need for the formal anchor+statement+suspect+requires format used in class-identity docs.
