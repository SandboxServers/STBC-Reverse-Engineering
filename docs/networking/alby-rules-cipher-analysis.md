---
title: The "AlbyRules!" Cipher: Analysis and Impact on Reverse Engineering
type: reference
audience: RE engineers, OpenBC implementers
validated: 2026-05-28
methodology: FUNCTION_DOC_WORKFLOW_V5
binary_fingerprint: stbc.exe (base 0x400000, 32-bit Windows)
status: verified
supersedes: []
evidence:
  - claim: "Key string 'AlbyRules!' (10 bytes + 2 padding)"
    address: 0x0095abb4
    confidence: high
    note: "bytes 41 6C 62 79 52 75 6C 65 73 21 00 00"
  - claim: "AlbyRulesCipher_InitKey: builds 0x58-byte state from key"
    address: 0x006c2280
    confidence: high
  - claim: "AlbyRulesCipher_Step: 5-round chained PRNG + key fold"
    address: 0x006c22f0
    confidence: high
  - claim: "AlbyRulesCipher_PRNG: two-LCG cross-XOR (multipliers 0x4E35 + 0x15A)"
    address: 0x006c23c0
    confidence: high
  - claim: "AlbyRulesCipher_Encrypt: per-byte XOR + key feedback"
    address: 0x006c2490
    confidence: high
  - claim: "AlbyRulesCipher_Decrypt: XOR + fold-after-XOR (plaintext folded back)"
    address: 0x006c2520
    confidence: high
  - claim: "AlbyRulesCipher_vtable: slot[1]=Encrypt, slot[2]=Decrypt"
    address: 0x008958c0
    confidence: high
  - claim: "TGWinsockNetwork_SendPacket calls vtable[+4] on (buf+1, len-1) — byte 0 not encrypted"
    address: 0x006b9870
    confidence: high
  - claim: "TGWinsockNetwork_ReceivePacket calls vtable[+8] on (buf+1, len-1); GameSpy 0x5C bypass at 0x006B9706"
    address: 0x006b95f0
    confidence: high
  - claim: "Cipher object lives at TGWinsockNetwork+0xF0 (0x58 bytes, single instance per singleton)"
    address: null
    confidence: high
    note: "per TGWinsockNetwork_SendPacket plate; offset is +0xF0 within the singleton"
  - claim: "Re-key per packet: InitKey is called at top of both Encrypt and Decrypt"
    address: 0x006c2280
    confidence: high
    note: "callers via get_function_callers: {Ctor, Encrypt, Decrypt}"
companions:
  - docs/protocol/transport-layer.md
  - docs/networking/network-protocol.md
---

> [docs](../README.md) / [networking](README.md) / alby-rules-cipher-analysis.md

# The "AlbyRules!" Cipher: Analysis and Impact on Reverse Engineering

> [!NOTE]
> **v5 verified pass — zero algorithm or wire corrections.** Two terminology clarifications + two refinements applied. Cipher's UDP-tolerance property (re-key per packet) confirmed; carries forward to OpenBC and proxy decoder cleanly.
>
> - **Clar-1**: `0x15A` is the SECOND LCG multiplier in a two-LCG cross-XOR — not an additive constant. Numeric value is correct in the original doc; phrasing updated.
> - **Clar-2**: Encrypt folds back the **ciphertext** (cursor after XOR), not the plaintext. Decrypt computes plaintext first then folds it. Both directions converge on the same key-buffer trajectory.
> - **R1**: Vtable cited explicitly at `0x008958c0`.
> - **R2**: Cipher object location cited — lives at `TGWinsockNetwork+0xF0`, 0x58 bytes, single instance per singleton.

## Discovery

Every UDP game packet in Star Trek: Bridge Commander is encrypted by a custom stream cipher before transmission. The cipher key is the hardcoded ASCII string `"AlbyRules!"` (10 bytes: `41 6C 62 79 52 75 6C 65 73 21`, plus 2 bytes of padding to `41 6C 62 79 52 75 6C 65 73 21 00 00`), stored in the `.rdata` section of `stbc.exe` at address `0x0095abb4`. The name is almost certainly a reference to a Totally Games developer — likely an in-joke that shipped to production.

The cipher was identified by tracing the TGWinsockNetwork send/receive path through Ghidra decompilation:

| Address | Function | Role |
|---------|----------|------|
| 0x006c2280 | InitKey (Reset) | Copies `"AlbyRules!"` into cipher object, zeros 0x40-byte working area |
| 0x006c22f0 | Key schedule (5-round step) | Derives 5 key words from the 10-byte key, runs 5 PRNG rounds, chained by XOR fold |
| 0x006c23c0 | PRNG step | Two LCGs cross-XORed (multipliers `0x4E35` and `0x15A`) |
| 0x006c2490 | Encrypt (vtable slot [1]) | Per-byte: re-key, XOR with PRNG output, ciphertext fed back into key buffer |
| 0x006c2520 | Decrypt (vtable slot [2]) | Inverse of encrypt (XOR first to recover plaintext, then fold plaintext back) |

Vtable at `0x008958c0`: slot[1] = Encrypt (`0x006c2490`), slot[2] = Decrypt (`0x006c2520`). Called via dispatch from `TGWinsockNetwork_SendPacket` (`0x006b9870`) and `TGWinsockNetwork_ReceivePacket` (`0x006b95f0`).

Cipher object lives at `TGWinsockNetwork+0xF0` — 0x58 bytes, single instance per singleton.

## How It Works

The cipher is a **stream cipher with key-buffer feedback**. It is not a simple XOR — each cursor byte modifies the key state for subsequent bytes, creating position-dependent encryption.

Per-packet behavior:
1. **Reset** — every encrypt/decrypt call starts by calling `InitKey` at `0x006c2280`, resetting from the same initial state (fresh copy of `"AlbyRules!"`). This re-key-per-packet property is what makes the cipher UDP-tolerant — no streaming state survives across packets.
2. **Key schedule** — 10 key bytes are paired into 5 key words, each XORed with its predecessor, then 5 rounds of PRNG produce an accumulator value.
3. **Per-byte encryption** — for each byte: run the full key schedule, extract `mask_low` and `mask_high` from the PRNG accumulator, XOR the plaintext byte with both masks, then feed the **ciphertext byte** (the cursor state after XOR) back into all 10 key bytes (modifying them for the next byte).
4. **Decryption** is identical except the cursor XOR happens **before** the fold: XOR ciphertext with mask first to recover plaintext, then fold the plaintext back into the key buffer. Because Decrypt computes plaintext first then folds it, and Encrypt folds the ciphertext (which equals XOR'd plaintext at that point), **both directions converge on the same key-buffer trajectory per byte**. This is why `decrypt(encrypt(P)) == P`.

### PRNG structure (two LCGs cross-XORed)

The PRNG at `0x006c23c0` is **not** a single LCG with multiplier and addend. It is two LCGs cross-XORed:

- First LCG multiplier: `0x4E35`
- Second LCG multiplier: `0x15A`
- Each LCG produces an output; the two outputs are XORed to form the keystream word at `state[+0x34]`.

The doc originally described `0x15A` as an addend; it is in fact the multiplier of the second LCG branch. The two magic constants are correct in name and value — only the framing changed.

### Critical properties

- **Static key** — same for all sessions, all players, all packets. No key exchange, no nonces, no session keys.
- **Per-packet reset** — each packet starts from the same cipher state (InitKey re-runs at the top of both Encrypt and Decrypt). Same plaintext always produces the same ciphertext.
- **Byte 0 quirk (cipher-side)** — the first PRNG output happens to XOR to `0x00` with the `"AlbyRules!"` key, so byte 0 would pass through unchanged even if it were cipher'd. (It is technically encrypted, but the XOR mask is zero.)
- **Byte 0 not encrypted (transport-side)** — at the transport layer, byte 0 of each UDP datagram is the direction flag (`0x01`=server, `0x02`=client, `0xFF`=initial contact) and is **not** passed through the cipher. `SendPacket` invokes `vtable[+4]` on `(buf+1, len-1)`; `ReceivePacket` invokes `vtable[+8]` on `(buf+1, len-1)`. Encryption starts at byte 1. The transport-side skip is the operative behavior; the cipher-side byte-0 coincidence is academic.
- **GameSpy bypass** — `ReceivePacket` at `0x006B9706` compares `byte ptr [buf]` against `0x5C` (`'\\'`). If the leading byte is `0x5C`, the packet is recognized as GameSpy traffic and routed to the GameSpy path without cipher invocation.

## Verification

The cipher reimplementation was verified against captured packet traces:

| Test | Result |
|------|--------|
| Packet #3 (8 bytes) | Decrypts to `01 01 03 06 C0 00 00 02` — correct connect message |
| Packet #4 (33 bytes) | Decrypts to checksum request containing ASCII `"scripts/App.pyc"` |
| 22 keepalive packets | All decode consistently with incrementing sequence numbers |
| Packet #55 (72 bytes) | Contains float `1.0f` (`FF FF FF 3F` little-endian) — confirms byte ordering |
| Round-trip test | `encrypt(decrypt(data)) == data` for all tested packets |

## Impact on Reverse Engineering

### Before: Opaque Wire Data
Without the cipher, packet traces were walls of seemingly random bytes. Analysis was limited to:
- Timing patterns (when packets arrived, how often)
- Packet sizes (which could hint at content type)
- The unencrypted direction flag byte
- Correlation with game events (connect, disconnect) by timing alone

Any attempt to understand **what** the server was sending or **why** the client disconnected required either running the full game engine (impossible headless) or guessing at packet structure from behavioral observations.

### After: Full Protocol Visibility
With the cipher broken, we can now:

**1. Read every packet in plaintext.**
Our packet trace system (`packet_trace.log`) now decrypts all game traffic in real-time and performs structured decode. Each packet is logged with its opcode name, parsed fields, and full hex dump of the decrypted payload. This turned an opaque binary stream into readable protocol documentation.

**2. Identify the exact disconnect cause.**
The cipher breakthrough directly led to identifying why clients disconnect after ship selection. By reading decrypted StateUpdate packets, we discovered the server sends `flags=0x00` (empty) instead of `flags=0x20` (subsystem data). This is because NIF ship models don't load headlessly, leaving the subsystem list at `ship+0x284` as NULL. Without decrypted packets, this would have been nearly impossible to diagnose — the symptom (client disconnect) is many layers removed from the cause (empty subsystem flags in a specific packet field).

**3. Compare our server against stock.**
We can capture packet traces from both our dedicated server and a stock hosted game, decrypt both, and diff them opcode-by-opcode. This revealed:
- Stock server cycles StateUpdate `startIdx` through `0, 2, 6, 8, 10` at ~100ms intervals (subsystem round-robin)
- Our server sends `startIdx=0` with `flags=0x00` every time (no subsystems to cycle)
- Stock server sends `flags=0x20` (SUB) on S->C; client sends `flags=0x80` (WPN) on C->S — mutually exclusive by direction
- The `0x80` flag in the decompiled code at FUN_005b17f0 checks `IsMultiplayer` (`0x0097FA8A`), but the client sends `0x80` in multiplayer mode, suggesting the client-side `IsMultiplayer` value differs from the host during serialization

**4. Discover undocumented opcodes.**
Decrypted traces revealed opcodes not previously documented anywhere:
- `0x11` — Unknown (seen in stock server post-join)
- `0x12` — Unknown (seen in stock server post-join)
- `0x13` — Unknown (post-join)
- `0x28` — Unknown (post-join)
- `0x2C` — Appears related to game state sync
- `0x35`, `0x37` — Seen during gameplay

**5. Validate our handshake implementation.**
We can verify that our checksum exchange, settings packet (opcode `0x00`), and NewPlayerInGame (opcode `0x2A`) match what the stock server sends byte-for-byte. Any deviation is immediately visible in the decrypted trace.

**6. Build protocol documentation from evidence.**
The [wire format spec](../protocol/wire-format-spec.md) was written entirely from decrypted packet analysis. Every field offset, flag bit, and opcode meaning was determined by reading actual decrypted traffic — not guessing from behavioral observations.

### Enables Future Work
The cipher is also the key enabler for potential future capabilities:
- **Standalone server** — a from-scratch server implementation could use this cipher to communicate with unmodified clients, without needing the game engine at all
- **Protocol proxy** — a man-in-the-middle tool could decrypt, inspect, modify, and re-encrypt packets between client and server for debugging
- **Automated testing** — synthetic packets can be constructed, encrypted, and injected to test specific server behaviors without a real client

## Cryptographic Assessment

This is **not** a secure cipher by any modern standard. It was clearly designed as an obfuscation layer, not for security:

- **Fixed key with no session randomness** — identical plaintext always produces identical ciphertext
- **No authentication** — packets can be forged or modified without detection
- **Key in `.rdata`** — trivially extractable from the binary (as we did)
- **Deterministic PRNG** — the two-LCG cross-XOR construction is reversible and predictable

This is typical for early-2000s game networking where the threat model was casual cheating, not determined attackers. The cipher's purpose was to prevent trivial packet sniffing with tools like Wireshark from revealing game state — and for that limited goal, it was adequate for its era.

## Implementation

The cipher is reimplemented in ~80 lines of C in `src/proxy/ddraw_main.c` (functions `BC_InitCipher`, `BC_PrngStep`, `BC_KeySchedule`, `BC_DecryptPacket`). It is used by the packet trace system to decrypt all captured traffic before logging.

## Companions

- [docs/protocol/transport-layer.md](../protocol/transport-layer.md) — confirms re-key-per-packet, SendPacket/ReceivePacket addresses, and `(buf+1, len-1)` cipher window
- [docs/networking/network-protocol.md](network-protocol.md) — places the cipher in the wider transport stack
