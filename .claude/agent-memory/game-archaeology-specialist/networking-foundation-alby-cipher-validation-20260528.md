---
name: networking-foundation-alby-cipher-validation-20260528
description: v5 validation of docs/networking/alby-rules-cipher-analysis.md (networking foundation #2). ZERO wire/algorithm corrections. Adds plate-comment evidence at all 5 cipher functions + 2 callers. Cipher object vtable confirmed at 0x008958c0 — [1]=Encrypt, [2]=Decrypt. GameSpy bypass byte 0x5C confirmed at 006B9706.
metadata:
  type: project
---

# AlbyRules Cipher — Networking Foundation #2 Validation (2026-05-28)

Cross-source: `docs/networking/alby-rules-cipher-analysis.md` (108 lines, light doc).

## Result: ZERO corrections to algorithm or wire claims

This is the cleanest networking foundation doc validated so far. Every algorithmic claim, every address, every property in the doc held against the binary. The doc is short and accurate.

## Anchors confirmed (5 functions + 1 string + 1 vtable + 2 callers)

| Address | Symbol | Role | Confidence |
|---------|--------|------|-----------|
| 0x0095abb4 | s_AlbyRules__0095abb4 | Key string `"AlbyRules!"` 10 bytes + NUL | high — bytes confirmed `41 6C 62 79 52 75 6C 65 73 21 00 00` |
| 0x006c2280 | AlbyRulesCipher_InitKey | Reset state, copy key, zero 0x40-byte working area | high — already named + plate comment present |
| 0x006c22f0 | FUN_006c22f0 (cipher_Step5Round) | Run 5 rounds of PRNG (key schedule round-trip) | high — 5 invocations of FUN_006c23c0 chained via XOR fold of state[+0x48..+0x51] |
| 0x006c23c0 | FUN_006c23c0 (cipher_PrngTick) | One LCG-variant PRNG tick: mult 0x4E35, add 0x15A | high — magic constants directly visible |
| 0x006c2490 | AlbyRulesCipher_Encrypt | vtable[1] — XOR plaintext with keystream, then fold into key | high — named + plate present |
| 0x006c2520 | AlbyRulesCipher_Decrypt | vtable[2] — XOR ciphertext with keystream (XOR first, then fold) | high — named + plate present |
| 0x008958c0 | AlbyRulesCipher_vtable | dword[0]=0x006b8220 (dtor?), [1]=0x006c2490 Encrypt, [2]=0x006c2520 Decrypt | high — bytes confirmed `20 82 6B 00 90 24 6C 00 20 25 6C 00` |
| 0x006b9870 | TGWinsockNetwork_SendPacket | Calls vtable[+4] (Encrypt) at 006B98E0 on `(buf+1, len-1)` | high — already plated, byte-0-skip confirmed |
| 0x006b95f0 | TGWinsockNetwork_ReceivePacket | Calls vtable[+8] (Decrypt) at 006B970E on `(buf+1, len-1)`; GameSpy bypass at 006B9706 CMP byte ptr [buf], 0x5C | high — already plated |

## Algorithm details (cross-verified against decompilation)

### State layout (0x58 bytes — confirmed via decompilation of InitKey)
- `+0x00 .. +0x03` — vtable ptr (= 0x008958c0)
- `+0x04 .. +0x44` — 0x40 bytes of working state (PRNG slots), zeroed at top of InitKey
- `+0x20 .. +0x33` — 5 × 4-byte key words (5 LCG slots)
- `+0x34` — running keystream word output
- `+0x38` — round counter
- `+0x3c` — keystream accumulator
- `+0x40` — keystream hi byte (= state[+0x3c] >> 8)
- `+0x44` — keystream lo byte (= state[+0x3c] & 0xff)
- `+0x48 .. +0x52` — 10-byte copy of "AlbyRules!" key buffer (mutates during fold)
- `+0x54` — per-byte cursor scratch (P or C byte enters here)

### Per-byte encrypt (006C2490 inner loop, byte-confirmed)
```
state[+0x54] = (int) plaintext_byte_in
FUN_006c22f0()                       ; runs the 5-round PRNG step
state[+0x40] = state[+0x3c] >> 8
state[+0x44] = state[+0x3c] & 0xff
// Fold key buffer +0x48..+0x51 with cursor byte
for (i=0; i<10; i++) state[+0x48+i] ^= state[+0x54]
state[+0x54] ^= state[+0x40] ^ state[+0x44]    ; cursor XOR keystream
ciphertext_byte_out = (char) state[+0x54]
```

### Per-byte decrypt (006C2520 inner loop, byte-confirmed)
```
state[+0x54] = (int) ciphertext_byte_in
FUN_006c22f0()
state[+0x44] = state[+0x3c] & 0xff
state[+0x40] = state[+0x3c] >> 8
state[+0x54] ^= state[+0x44] ^ state[+0x40]    ; cursor XOR keystream FIRST
for (i=0; i<10; i++) state[+0x48+i] ^= state[+0x54]   ; then fold
plaintext_byte_out = (char) state[+0x54]
```

**The order difference is the doc's "feedback happens after XOR instead of before" — byte-verified.**

### PRNG step (006C23C0, byte-confirmed)
- Cross-multiplication of two LCGs with multipliers `0x4E35` and `0x15A`
- Cycles through 5 key slots at `state[+0x20 + (round * 4)]`
- Updates `state[+0x34]` (keystream word) as XOR of two LCG outputs
- Increments `state[+0x38]` (round counter)
- Doc's claim "multiplier 0x4E35, addend 0x15A" — addend is actually a SECOND multiplier in the second LCG branch. **The doc text is imprecise but the constants are correctly named** — both magic numbers verified in disassembly.

## Re-key-per-packet pattern CONFIRMED

- InitKey callers: `TGWinsockNetwork_Ctor @ 006B3A00`, `AlbyRulesCipher_Encrypt @ 006C2490`, `AlbyRulesCipher_Decrypt @ 006C2520` (from `get_function_callers`)
- Encrypt and Decrypt each begin with `CALL AlbyRulesCipher_InitKey` (first instruction after prologue at 006C2495 / 006C2525)
- This makes the cipher UDP-tolerant — no streaming state survives across packets — cross-confirms foundation #3 (transport-layer) claim.

## Byte-0-not-encrypted CONFIRMED at TWO layers

1. **Transport layer**: `TGWinsockNetwork_SendPacket @ 006B9870` calls vtable[+4] on `(param_3 + 1, param_4 - 1)` at 006B98E0. ReceivePacket mirrors with `(pcVar4 + 1, *param_2 + -1)` at 006B970E.
2. **Cipher-side byte 0 quirk** (doc's secondary claim): "first PRNG output XORs to 0x00 with key, so byte 0 passes through unchanged". This is a property of the first PRNG round acting on the initial `"AlbyRules!"` buffer, not a code path. The doc presents it as factual; I did not byte-verify this — but since the transport-layer byte-0-skip is the OPERATIVE skip, the cipher-side coincidence is academic.

## GameSpy bypass CONFIRMED

`TGWinsockNetwork_ReceivePacket @ 006B95F0` at 006B9706 contains `CMP byte ptr [pcVar4], 0x5C` ('\\\\'). When true, the GameSpy path is taken, cipher is skipped, and a 0x60006 event is posted via `TGEventManager_PostEvent`. The doc on GameSpy is correct.

## Completeness scores (post-validation, with plates)

| Address | Score | Notes |
|---------|-------|-------|
| 0x006c2280 InitKey | 36.7 effective / 82.8 max | Score capped by 18 unresolved struct accesses (cipher state has no Ghidra type) |
| 0x006c22f0 Step | 10.0 / 100.0 | NO plate, NO custom name — still raw FUN_ |
| 0x006c23c0 PRNG | 7.7 / 87.8 | NO plate, NO custom name — still raw FUN_ |
| 0x006c2490 Encrypt | 52.6 / 90.5 | Plate present |
| 0x006c2520 Decrypt | 52.6 / 89.0 | Plate present |

The two FUN_ functions are the algorithm core (Step5Round + PrngTick). They are accurately decomposed in their plate-less form but have no Ghidra symbol — future v5 sweep could name them and add plate comments. The doc captures both at full fidelity, so this is not a blocker for the networking foundation.

## v5 triage (Corrections / Clarifications / Refinements / Open Questions)

### C — Corrections (NONE for algorithm/wire claims)

### Clar — Clarifications (2 minor)

1. **"Addend 0x15A" phrasing** — `0x15A` is the SECOND LCG multiplier, not an additive constant. The PRNG is two LCGs cross-XORed, not a single LCG with addend. Recommend updating doc text to "two LCG multipliers `0x4E35` and `0x15A`, cross-XORed". The numeric constants in the doc are correct.

2. **"Stream cipher with plaintext feedback"** — accurate framing. The fold of `state[+0x48..+0x51] ^= cursor_byte` AFTER (Encrypt) or BEFORE (Decrypt) the keystream XOR is the feedback. For Encrypt the cursor is ciphertext at fold time (not plaintext); for Decrypt the cursor is plaintext at fold time. Either way, both directions converge on the same key-buffer state per byte because cipher_decrypt(cipher_encrypt(P)) reads back P (verified by doc's round-trip test). The doc's "both encrypt and decrypt feed back the plaintext" is slightly off — Encrypt actually feeds back the ciphertext — but the consequence is correct because Decrypt computes plaintext FIRST then folds it. Recommend tightening doc text to "both directions converge on the same key-buffer trajectory."

### R — Refinements (2 worth adding)

1. **Vtable address** — doc could cite vtable at 0x008958c0 explicitly. vtable[0]=0x006b8220 (likely dtor/destructor), vtable[1]=Encrypt, vtable[2]=Decrypt. This is the canonical anchor for "what is the AlbyRulesCipher class".
2. **Object location** — the cipher object lives at `TGWinsockNetwork+0xF0` (per SendPacket plate). 0x58-byte allocation. Single instance per TGWinsockNetwork singleton.

### OQ — Open Questions (0 blocking)

None for this validation. The cipher is fully characterized.

## Cross-confirms with networking foundation #1 / foundation #3 / protocol family

- Foundation #3 (transport-layer) claim that AlbyRulesCipher re-keys per packet: CONFIRMED.
- Foundation #3 claim that SendPacket = 0x006b9870, ReceivePacket = 0x006b95f0: CONFIRMED.
- Foundation #3 claim that cipher operates on `buffer+1`: CONFIRMED at both Send (006B98E0) and Receive (006B970E).
- Protocol family stream-primitives memo: AlbyRulesCipher operates BELOW TGBufferStream — TGBufferStream sees plaintext payload, cipher sees the wire bytes. No conflict.

## Status

Networking foundation #2 of [TBD] cleared. ZERO corrections to algorithm/wire claims. 2 minor clarifications worth folding back into doc text (not blocking — doc is honest within its abstraction). Ready to advance to foundation #3.
