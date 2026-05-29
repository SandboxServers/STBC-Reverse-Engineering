---
name: networking-cipher-render-patterns-20260528
description: Render patterns for the FIRST networking foundation doc (cipher) to clear `verified`. Light pass — zero algorithm/wire corrections, 2 clarifications + 2 refinements. Patterns for terminology-only clarifications + vtable/object-location refinements without restructuring an already-clean cryptography doc.
metadata:
  type: project
---

# Networking foundation #2 (AlbyRules cipher) render patterns — 2026-05-28

Source render: `docs/networking/alby-rules-cipher-analysis.md` (verified, 108 → ~165 lines after v5 header).

Sibling/predecessor docs in render style: protocol leaf #15 collision-effect-protocol.md (first verified protocol leaf — same frontmatter shape borrowed here).

## Render shape (verified networking foundation, light render)

**Top-of-doc NOTE block — verified-with-clarifications variant**

> [!NOTE]
> **v5 verified pass — zero algorithm or wire corrections.** Two terminology clarifications + two refinements applied. <one-line load-bearing property carried forward>.
>
> - **Clar-1**: <terminology fix> — <correct framing>. <why old phrasing was imprecise>.
> - **Clar-2**: <semantic fix> — <correct mechanism>. <why old phrasing was off but conclusion was right>.
> - **R1**: <new citation added>.
> - **R2**: <new citation added>.

Difference from first-verified-protocol-leaf (collision-effect-protocol.md): this NOTE leads with **clarifications**, not corrections, because no body claim was wrong — only its phrasing. Each Clar/R item is enumerated inline in the NOTE so readers see the full delta without scrolling.

## Pattern 1 — Terminology-only correction stays inline; no dedicated `## C1` section

Because Clar-1 (`0x15A` = second LCG multiplier, not addend) and Clar-2 (Encrypt feeds back ciphertext, not plaintext) do not change any wire byte or algorithm output, they live in the NOTE summary AND get folded into prose at the natural section. No `## C1: ...` second-heading section is needed — that shape is reserved for material body-claim corrections (partial-tier docs).

Where applied in cipher doc:
- "Per-byte encryption" step text was rewritten to say "feed the **ciphertext byte** (the cursor state after XOR) back into all 10 key bytes" — bold-emphasis on the corrected term.
- "Decryption" step text was rewritten to say "Decrypt computes plaintext first then folds it, and Encrypt folds the ciphertext... **both directions converge on the same key-buffer trajectory per byte**" — bold emphasis on the load-bearing consequence.
- A new dedicated `### PRNG structure (two LCGs cross-XORed)` subsection was added to make the multiplier-vs-addend fix explicit AND state the constants are correct.

Rule: a terminology-only fix gets a dedicated `###` subsection only when the corrected framing is technically load-bearing (PRNG structure here — Clar-1). A semantic fix that doesn't restructure the body (Clar-2 — both directions converge) just gets a bold-emphasis sentence at the natural paragraph.

## Pattern 2 — Refinement-as-additive-line in existing tables / paragraphs

For R1 (vtable cite) and R2 (object location), no NEW section was needed. Both refinements were appended as one-line additions immediately after the introductory anchor table:

> Vtable at `0x008958c0`: slot[1] = Encrypt (`0x006c2490`), slot[2] = Decrypt (`0x006c2520`). Called via dispatch from `TGWinsockNetwork_SendPacket` (`0x006b9870`) and `TGWinsockNetwork_ReceivePacket` (`0x006b95f0`).
>
> Cipher object lives at `TGWinsockNetwork+0xF0` — 0x58 bytes, single instance per singleton.

Rule: refinements that don't have a natural columnar home (the existing table here is keyed by function address, not object structure) become free-standing 1-line statements directly after the table. Two short paragraphs is cleaner than appending a `Vtable` row that breaks the function-address keying.

## Pattern 3 — `address: null` evidence row for property claims with no single-anchor address

The "cipher object lives at TGWinsockNetwork+0xF0" claim is a structural property, not a code address. Evidence row form:

```yaml
- claim: "Cipher object lives at TGWinsockNetwork+0xF0 (0x58 bytes, single instance per singleton)"
  address: null
  confidence: high
  note: "per TGWinsockNetwork_SendPacket plate; offset is +0xF0 within the singleton"
```

Same pattern as protocol leaf #17 used for negative claims (no anchor in the binary, evidence cited via plate comment of a related function). For structural/offset claims like this one, naming the plate-bearing function in the `note:` is sufficient.

## Pattern 4 — Re-key-per-packet load-bearing property gets a callout

The cipher's UDP-tolerance property (InitKey re-runs at the top of both Encrypt and Decrypt — so no stream state survives between packets) is what makes the cipher OpenBC-portable. Lifted into NOTE block headline ("Cipher's UDP-tolerance property (re-key per packet) confirmed; carries forward to OpenBC and proxy decoder cleanly") AND restated in step 1 of "Per-packet behavior" (existing text was kept but extended with "This re-key-per-packet property is what makes the cipher UDP-tolerant").

Rule: when a foundation doc is verified and its load-bearing property carries forward to OpenBC clean-room, surface that explicitly in the NOTE so OpenBC implementers know they can rely on it.

## Pattern 5 — Companion-list section at doc bottom

For the first networking-foundation `verified` doc, a `## Companions` section was added at the bottom that mirrors the frontmatter `companions:` array — one bullet per companion with a one-line "what they confirm" framing. This is good practice for foundation docs because foundations get cited by leaves, and the companion list makes the cross-validation explicit:

> - [docs/protocol/transport-layer.md](../protocol/transport-layer.md) — confirms re-key-per-packet, SendPacket/ReceivePacket addresses, and `(buf+1, len-1)` cipher window
> - [docs/networking/network-protocol.md](network-protocol.md) — places the cipher in the wider transport stack

## What NOT to do (light-render guards)

- DO NOT add Open Questions section for a verified doc with zero corrections.
- DO NOT add a §6 / tracker subsection inline in the doc (tracker batched at family close).
- DO NOT rewrite the "How It Works" overview text just because of terminology — fold the term-fix into the affected paragraph, keep everything else.
- DO NOT add `[v5-validated YYYY-MM-DD]` tags to every paragraph (this is verified-tier — frontmatter is the timestamp).
- DO NOT downgrade the Verification table or the Impact section just because they're prose-heavy — they captured the discovery story and are still load-bearing for onboarding.

## Tracker row shape (for batched family-close pass)

Pending tracker update for `docs/networking/v5-validation-status.md`:
- Status: `verified`
- Methodology: FUNCTION_DOC_WORKFLOW_V5
- Date: 2026-05-28
- Corrections: 0 algorithm/wire; 2 terminology clarifications (`0x15A` framing, ciphertext-feedback direction); 2 refinements (vtable address, object location)
- §6 cross-doc impacts: confirms re-key-per-packet for transport-layer.md; confirms cipher placement in network-protocol.md stack; no outbound impacts
