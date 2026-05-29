---
title: GameSpy Challenge-Response Crypto Analysis
type: reference
audience: RE engineers, OpenBC implementers
validated: 2026-05-28
methodology: FUNCTION_DOC_WORKFLOW_V5
binary:
  name: stbc.exe
  size: 6182400
  base: 0x00400000
status: partial
supersedes:
  - 2026-02-15
evidence:
  - claim: "gs_rc4_cipher: KSA + modified PRGA (data byte mixed into i)"
    address: 0x006ac050
    function: gs_rc4_cipher
    confidence: high
    note: "Byte-confirmed: PRGA `i = data[n] + 1 + i mod 256`, XOR uses `S[(S[j]+S[i]) & 0xFF]`"
  - claim: "gs_validate_encode: 3-byte to 4-byte base64-like encoding"
    address: 0x006abf70
    function: gs_validate_encode
    completeness: 11.3
    confidence: high
    note: "Byte-confirmed: shifts/masks produce a,b,c,d 6-bit fields exactly as doc"
  - claim: "gs_encode_char: 6-bit value to ASCII (A-Z/a-z/0-9/+//)"
    address: 0x006ac020
    function: gs_encode_char
    completeness: 10.4
    confidence: high
    note: "Byte-confirmed: `(val != 0x3f) - 1 & 0x2f` trick for '/'"
  - claim: "gs_swap: 3-line byte swap helper used by gs_rc4_cipher"
    address: 0x006ac1c0
    function: gs_swap
    confidence: high
  - claim: "qr_send_validate_and_final: QR path; calls cipher with secret at qr_t+0x48, then encode, then `\\validate\\%s` sprintf"
    address: 0x006ac950
    function: qr_send_validate_and_final
    confidence: high
  - claim: "SL_master_connect: ServerList auth path; calls cipher with (server_list+0x2C, 6, challenge+8, 6)"
    address: 0x006aa4c0
    function: SL_master_connect
    confidence: high
  - claim: "gs_list_init: ServerList ctor; malloc(0xA0), copies game name to +0x0C, secret to +0x2C, second name to +0x4C"
    address: 0x006aa100
    function: gs_list_init
    confidence: high
  - claim: "GameSpy::InitBrowser: builds secret key 'Nm3aZ9' as 7 stack-byte locals"
    address: 0x0069c3a0
    function: GameSpy::InitBrowser
    confidence: high
    note: "Stack locals 0x4e/0x6d/0x33/0x61/0x5a/0x39/0x00 = 'Nm3aZ9\\0'"
  - claim: "Server entry hash struct ctor (0x18-byte entry, 0x40 buckets); stored at ServerList+0x04"
    address: 0x006ad180
    function: FUN_006ad180
    confidence: high
  - claim: "Poll/timer struct ctor (0x14-byte, 500 entries); stored at ServerList+0x94 (puVar3[0x25]), NOT +0x08"
    address: 0x006acb30
    function: FUN_006acb30
    confidence: high
    note: "Corrects pre-v5 doc which placed timer at +0x08"
  - claim: "Literal 'bcommander' (game name) at .rdata 0x00959c24"
    address: 0x00959c24
    function: null
    confidence: high
    note: "bytes 62 63 6f 6d 6d 61 6e 64 65 72 00"
  - claim: "Format-string template `\\gamename\\%s\\gamever\\%s\\location\\0\\validate\\%s\\final\\\\queryid\\1.1\\` at .rdata 0x0095a624"
    address: 0x0095a624
    function: null
    confidence: high
    note: "The `\\queryid\\1.1\\` suffix is a literal format-template tail, not a substituted value"
  - claim: "gamever wire literal '1.6' at .rdata 0x0095a668"
    address: 0x0095a668
    function: null
    confidence: high
    note: "bytes 31 2e 36 00; substituted into the `\\gamever\\%s\\` field by SL_master_connect — corrects pre-v5 doc example which showed '1.1'"
  - claim: "Literal `\\secure\\` at .rdata 0x0095a66c"
    address: 0x0095a66c
    function: null
    confidence: high
    note: "bytes 5c 73 65 63 75 72 65 5c 00"
  - claim: "Literal `\\final\\` at .rdata 0x0095a678"
    address: 0x0095a678
    function: null
    confidence: high
    note: "bytes 5c 66 69 6e 61 6c 5c 00"
  - claim: "Format string `\\validate\\%s` at .rdata 0x0095a8e0 (QR path sprintf format)"
    address: 0x0095a8e0
    function: null
    confidence: high
    note: "bytes 5c 76 61 6c 69 64 61 74 65 5c 25 73 00"
  - claim: "ServerList +0x9C is a state/mode side-channel, NOT padding"
    address: 0x006aa4c0
    function: SL_master_connect
    confidence: high
    note: "Cleared (written 0) by SL_master_connect in two branches (groups path, info2 path) — corrects pre-v5 doc which labeled it 'Padding/unused'"
  - claim: "qr_t struct rows beyond +0x48 (callback ptrs, sequence counters, retry/active flags) are NOT directly anchored to stbc.exe in this validation pass"
    address: null
    function: null
    confidence: low
    note: "Negative claim: searched qr_send_validate_and_final body for offset references beyond +0x48 and did not find anchor sites for the +0xC8/+0xCC/+0xD0/+0xD8/+0xE0/+0xE4/+0xE8/+0xEC entries. Likely SDK-derived. See OQ1."
companions:
  - docs/networking/alby-rules-cipher-analysis.md
  - docs/networking/gamespy-discovery.md
  - docs/networking/network-protocol.md
---

> [docs](../README.md) / [networking](README.md) / gamespy-crypto-analysis.md

# GameSpy Challenge-Response Crypto Analysis

> [!NOTE]
> **v5 partial pass — algorithm and crypto core are byte-confirmed rock-solid.** 3 corrections in secondary documentation (wire example gamever, ServerList timer slot offset, +0x9C field role) + 2 clarifications (stale SOCKET*-arithmetic narrative, qr_t/GameSpy struct conflation) + 3 OQs.
>
> **Notable**: the binary emits gamever `\1.6\` from the literal at `0x0095a668`; the pre-v5 doc's wire example incorrectly showed `\1.1\`. This may affect OpenBC clean-room compatibility with strict-version-filter masterservers — flagged as OQ3.
>
> - **C1**: wire-example `\gamever\1.1\` → `\gamever\1.6\` (literal at `0x0095a668`).
> - **C2**: ServerList timer slot is at `+0x94` (written by `gs_list_init` as `puVar3[0x25]`), not `+0x08`.
> - **C3**: ServerList `+0x9C` is a state/mode side-channel (cleared by `SL_master_connect`), not padding.
> - **Clar-1**: The "SOCKET* arithmetic" narrative for `param_1 + 0x12` → byte `0x48` reflects an older Ghidra session; current decompilation shows `param_1 + 0x48` as a plain byte offset.
> - **Clar-2**: The "qr_t" struct (param to `FUN_006ac950`) and the "GameSpy" struct (param to `FUN_0069c3a0`) are different structs; offsets like `+0xDC/+0xE0/+0xED/+0xEE` belong to the GameSpy object, not qr_t.

## Overview

Bridge Commander uses the standard GameSpy QR1 (Query/Reporting version 1) challenge-response
protocol for two purposes:

1. **Server-side (QR)**: When a master server sends `\secure\<challenge>` to validate a game
   server is real, the server must respond with `\validate\<hash>`.
2. **Client-side (Server List)**: When a client connects to the master server on TCP 28900 to
   browse servers, the master sends `\secure\<challenge>` and the client must respond with
   `\validate\<hash>` embedded in its `\gamename\...\validate\...\final\` response.

Both paths use identical crypto: RC4 encryption with the game's secret key, followed by a
custom base64-like encoding.

## Secret Key

**Value**: `"Nm3aZ9"` (6 bytes)

**Location**: Hardcoded at `GameSpy::InitBrowser` (`0x0069c3a0`), built as 7 stack-byte locals
(`0x4e 0x6d 0x33 0x61 0x5a 0x39 0x00`):

```c
builtin_strncpy(local_c, "Nm3aZ9", 7);
```

This is then passed to `gs_list_init` (`0x006aa100`) as `param_3`, which copies it into the
ServerList struct at byte offset `+0x2C` (i.e., `puVar4 + 0xb` in the constructor's `puVar4`
pointer arithmetic).

In the QR path (`qr_send_validate_and_final` at `0x006ac950`), the secret key is at byte
offset **`+0x48`** within the qr_t struct.

> [!NOTE]
> **Clar-1**: Earlier revisions of this doc walked through a `SOCKET*`-arithmetic explanation
> (Ghidra had typed `param_1` as `SOCKET*`, so `param_1 + 0x12` was interpreted as
> `0x12 * sizeof(SOCKET) = 0x48`). The current decompilation shows `(char *)(param_1 + 0x48)`
> directly as a plain byte offset — no SOCKET typing in evidence. The arithmetic was always
> correct; the narrative was an artifact of a prior Ghidra session whose typing has reset.

The two paths agree on which 6 bytes go into the cipher:

```c
// gs_list_init (0x006aa100): write side
// puVar4 = malloc(0xA0) — the ServerList struct
// Game name copied to byte offset +0x0C
// Secret key copied to byte offset +0x2C   ← key offset
// Second game name (param_2) to +0x4C

// SL_master_connect (0x006aa4c0): read side
FUN_006ac050((int)(param_1 + 0xb), 6, (int)(pcVar3 + 8), 6);
//           ^secret_key (+0x2C)   ^key_len  ^challenge   ^challenge_len
```

## The Algorithm (3 Functions) [v5-validated 2026-05-28]

### 1. gs_rc4_cipher (0x006ac050) — Modified RC4 Encryption

This is a **modified RC4** stream cipher. It encrypts the challenge data in-place using the
secret key.

**Prototype**: `void __cdecl gs_rc4_cipher(int key, int keyLen, int data, int dataLen)`

**Reconstructed C code**:
```c
void gs_rc4_cipher(unsigned char *key, int keyLen,
                   unsigned char *data, int dataLen)
{
    unsigned char S[256];
    int i, j, k;

    // KSA (Key Scheduling Algorithm) — standard RC4
    for (i = 0; i < 256; i++)
        S[i] = (unsigned char)i;

    j = 0;
    k = 0;
    for (i = 0; i < 256; i++) {
        j = (unsigned char)(S[i] + j + key[k]);
        k = (unsigned char)((k + 1) % keyLen);
        SWAP(S[i], S[j]);
    }

    // PRGA (Pseudo-Random Generation Algorithm) — MODIFIED!
    // Standard RC4 uses: i = (i+1) % 256
    // This uses:         i = (data[n] + 1 + i) % 256
    // The data byte itself is mixed into the index!
    i = 0;
    j = 0;
    for (int n = 0; n < dataLen; n++) {
        i = (unsigned char)(data[n] + 1 + i);    // <-- NON-STANDARD
        j = (unsigned char)(S[i] + j);
        SWAP(S[i], S[j]);
        data[n] ^= S[(unsigned char)(S[j] + S[i])];
    }
}
```

**Key difference from standard RC4**: In the PRGA phase, standard RC4 increments `i` by 1
each iteration (`i = (i+1) % 256`). This implementation uses
`i = (data[n] + 1 + i) % 256` — the plaintext byte is mixed into the index before
encryption. This makes it a **non-standard RC4 variant** specific to GameSpy's QR1 SDK.

The `gs_swap` call (`0x006ac1c0`) is a simple byte swap:
```c
void gs_swap(unsigned char *a, unsigned char *b) {
    unsigned char tmp = *a;
    *a = *b;
    *b = tmp;
}
```

### 2. gs_validate_encode (0x006abf70) — Base64-like Encoding

After RC4 encryption, the binary ciphertext must be converted to printable ASCII for
embedding in the `\validate\` field. This function performs a base64-like encoding.

**Prototype**: `void __cdecl gs_validate_encode(unsigned char *src, int srcLen, unsigned char *dst)`

**Reconstructed C code**:
```c
void gs_validate_encode(unsigned char *src, int srcLen, unsigned char *dst)
{
    int i = 0;
    unsigned char triple[3];

    if (srcLen < 1) {
        *dst = 0;
        return;
    }

    do {
        // Read 3 bytes (pad with 0 if beyond srcLen)
        for (int j = 0; j < 3; j++, i++) {
            if (i < srcLen)
                triple[j] = src[i];   // Note: reads from LOCAL copy on stack
            else
                triple[j] = 0;
        }

        // Split 3 bytes (24 bits) into 4 x 6-bit values
        unsigned char a = triple[0] >> 2;
        unsigned char b = ((triple[0] & 0x03) << 4) | (triple[1] >> 4);
        unsigned char c = ((triple[1] & 0x0F) << 2) | (triple[2] >> 6);
        unsigned char d = triple[2] & 0x3F;

        // Encode each 6-bit value to a printable character
        *dst++ = gs_encode_char(a);
        *dst++ = gs_encode_char(b);
        *dst++ = gs_encode_char(c);
        *dst++ = gs_encode_char(d);

    } while (i < srcLen);

    *dst = 0;  // NULL terminate
}
```

**NOTE**: The decompilation shows the source bytes are read into what Ghidra displays as
`(int)&param_3 + iVar2` — this is actually reading into a local stack variable (3-byte
triple buffer). Ghidra's decompilation is confused because the triple is stored in the same
stack slot as the `param_3` pointer. The actual semantics are: read 3 bytes from `src` into
a local buffer, then encode 4 output bytes.

The encoding ratio is standard base64: 3 input bytes become 4 output bytes.
For a 6-byte input (the challenge), output is 8 characters + NULL terminator.

### 3. gs_encode_char (0x006ac020) — Character Mapping

Maps a 6-bit value (0-63) to a printable ASCII character.

**Prototype**: `unsigned char __cdecl gs_encode_char(unsigned char val)`

**Reconstructed C code**:
```c
unsigned char gs_encode_char(unsigned char val)
{
    if (val < 26)           // 0-25 -> 'A'-'Z'
        return val + 'A';   // 0x41
    if (val < 52)           // 26-51 -> 'a'-'z'
        return val + 'G';   // 0x47 (26 + 0x47 = 0x61 = 'a')
    if (val < 62)           // 52-61 -> '0'-'9'
        return val - 4;     // 0x30..0x39 (52 - 4 = 48 = '0')
    if (val == 62)          // 62 -> '+'
        return '+';         // 0x2B
    if (val == 63)          // 63 -> '/'
        return '/';         // 0x2F
    return 0;               // shouldn't happen
}
```

This is **exactly standard Base64** character mapping (RFC 4648 Table 1):
`A-Z a-z 0-9 + /`

Note: the last case `(param_1 != 0x3f) - 1U & 0x2f` resolves to:
- If val == 63: `(0) - 1 = 0xFFFFFFFF`, `& 0x2F = 0x2F = '/'`
- If val > 63: `(1) - 1 = 0`, `& 0x2F = 0x00` (never reached with 6-bit input)

## Full Validation Flow

### QR Path (Server responding to master server query)

In `qr_send_validate_and_final` (`0x006ac950`):

```
1. Master sends UDP query containing "\secure\<CHALLENGE>"
2. qr_parse_query extracts the challenge string (param_4)
3. qr_send_validate_and_final:
   a. Copy challenge to local buffer (local_248, max 128 bytes)
   b. Get secret key from qr_t+0x48 (the key stored at init time)
   c. Compute key length via strlen(secret_key)
   d. RC4-encrypt challenge in-place:
      gs_rc4_cipher(secret_key, keyLen, challenge_copy, challengeLen)
   e. Base64-encode the encrypted result:
      gs_validate_encode(challenge_copy, challengeLen, encoded_output)
   f. Format response string: sprintf(buf, "\\validate\\%s", encoded_output)
      // format string at .rdata 0x0095a8e0
   g. Send via qr_assemble_response (FUN_006ac660)
   h. Send "\\final\\" trailer (literal at .rdata 0x0095a678)
   i. Flush buffer via qr_flush_send (FUN_006ac550)
```

### Server List Path (Client authenticating with master)

In `SL_master_connect` (`0x006aa4c0`):

```
1. Client connects to master on TCP 28900
2. Master sends: "...\secure\<CHALLENGE>..."
3. Client parses out "\secure\" prefix, gets challenge at pcVar3+8
4. RC4-encrypt the 6-byte challenge with the 6-byte secret key:
   gs_rc4_cipher(server_list+0x2C, 6, challenge_ptr+8, 6)
   // key = "Nm3aZ9" (at byte offset 0x2C in ServerList struct)
   // keyLen = 6
   // data = 6-byte challenge token
   // dataLen = 6
5. Base64-encode the result:
   gs_validate_encode(challenge_ptr+8, 6, local_40)
   // Produces 8-char encoded string
6. Format response using template at .rdata 0x0095a624:
   sprintf(buf, "\\gamename\\%s\\gamever\\%s\\location\\0\\validate\\%s\\final\\\\queryid\\1.1\\",
           gamename,         // "bcommander" at .rdata 0x00959c24
           gamever,          // "1.6"        at .rdata 0x0095a668  ← v5 correction
           encoded_result)
7. Send via TCP send()
```

## Reimplementation

Here is a complete, standalone C reimplementation of the GameSpy challenge-response:

```c
/*
 * GameSpy QR1 Challenge-Response Implementation
 * For Bridge Commander ("bcommander", secret key "Nm3aZ9")
 *
 * Usage:
 *   char validate[16];
 *   gs_compute_validate("Nm3aZ9", challenge_string, validate, sizeof(validate));
 *   // validate now contains the base64-encoded response
 */

#include <string.h>

static void gs_swap(unsigned char *a, unsigned char *b)
{
    unsigned char tmp = *a;
    *a = *b;
    *b = tmp;
}

static unsigned char gs_encode_char(unsigned char val)
{
    if (val < 26)  return val + 'A';        /* A-Z */
    if (val < 52)  return val + ('a' - 26); /* a-z */
    if (val < 62)  return val + ('0' - 52); /* 0-9 */
    if (val == 62) return '+';
    if (val == 63) return '/';
    return 0;
}

/*
 * GameSpy modified RC4 cipher.
 * Encrypts 'data' in-place using 'key'.
 *
 * IMPORTANT: This is NOT standard RC4!
 * The PRGA phase mixes the plaintext byte into the index:
 *   i = (data[n] + 1 + i) % 256   (standard RC4 uses i = (i+1) % 256)
 */
static void gs_rc4_cipher(const unsigned char *key, int keyLen,
                           unsigned char *data, int dataLen)
{
    unsigned char S[256];
    int n;
    unsigned char i, j, k;

    /* KSA - Key Scheduling Algorithm (standard RC4) */
    for (n = 0; n < 256; n++)
        S[n] = (unsigned char)n;

    j = 0;
    k = 0;
    for (n = 0; n < 256; n++) {
        j = (unsigned char)(S[n] + j + key[k]);
        k = (unsigned char)((k + 1) % keyLen);
        gs_swap(&S[n], &S[j]);
    }

    /* PRGA - Pseudo-Random Generation Algorithm (MODIFIED) */
    i = 0;
    j = 0;
    for (n = 0; n < dataLen; n++) {
        i = (unsigned char)(data[n] + 1 + i);   /* non-standard! */
        j = (unsigned char)(S[i] + j);
        gs_swap(&S[i], &S[j]);
        data[n] ^= S[(unsigned char)(S[j] + S[i])];
    }
}

/*
 * GameSpy base64-like encoding.
 * Encodes 'srcLen' bytes from 'src' into 'dst' as printable ASCII.
 * 'dst' must have room for (srcLen+2)/3*4 + 1 bytes.
 */
static void gs_validate_encode(const unsigned char *src, int srcLen,
                                char *dst)
{
    int i = 0;

    if (srcLen < 1) {
        *dst = 0;
        return;
    }

    while (i < srcLen) {
        unsigned char triple[3];
        unsigned char a, b, c, d;
        int j;

        /* Read up to 3 bytes, zero-pad if needed */
        for (j = 0; j < 3; j++) {
            if (i < srcLen)
                triple[j] = src[i];
            else
                triple[j] = 0;
            i++;
        }

        /* Split 24 bits into 4 x 6-bit values */
        a =  triple[0] >> 2;
        b = ((triple[0] & 0x03) << 4) | (triple[1] >> 4);
        c = ((triple[1] & 0x0F) << 2) | (triple[2] >> 6);
        d =  triple[2] & 0x3F;

        /* Encode to printable characters */
        *dst++ = gs_encode_char(a);
        *dst++ = gs_encode_char(b);
        *dst++ = gs_encode_char(c);
        *dst++ = gs_encode_char(d);
    }

    *dst = 0;  /* NULL terminate */
}

/*
 * High-level: compute the \validate\ response for a GameSpy challenge.
 *
 * secret_key: Game secret key ("Nm3aZ9" for Bridge Commander)
 * challenge:  The challenge string from \secure\<challenge>
 * out:        Output buffer for encoded validate string
 * outSize:    Size of output buffer (>= 16 for 6-byte challenges)
 */
void gs_compute_validate(const char *secret_key,
                          const char *challenge,
                          char *out, int outSize)
{
    unsigned char buf[128];
    int challengeLen = strlen(challenge);
    int keyLen = strlen(secret_key);

    if (challengeLen > (int)sizeof(buf))
        challengeLen = (int)sizeof(buf);

    /* Copy challenge — RC4 encrypts in-place */
    memcpy(buf, challenge, challengeLen);

    /* RC4-encrypt with game secret key */
    gs_rc4_cipher((const unsigned char *)secret_key, keyLen,
                  buf, challengeLen);

    /* Base64-encode the ciphertext */
    gs_validate_encode(buf, challengeLen, out);
}
```

## Wire Format Examples [v5-validated 2026-05-28]

All literal string addresses verified against `.rdata` byte-for-byte.

### QR (Server) Response to Master
```
Master -> Server (UDP): \secure\ABCDEF
Server -> Master (UDP): \validate\XXXXXXXX\final\\queryid\1.1\
```

The `\validate\%s` template lives at `.rdata 0x0095a8e0`; the `\final\` literal lives at
`.rdata 0x0095a678`.

### Server List (Client) Auth with Master
```
Master -> Client (TCP): ...\secure\ABCDEF...
Client -> Master (TCP): \gamename\bcommander\gamever\1.6\location\0\validate\XXXXXXXX\final\\queryid\1.1\
```

**C1 (v5 correction)**: the pre-v5 doc previously showed `\gamever\1.1\` in this example.
The wire substitution is the literal at `.rdata 0x0095a668` = `"1.6"`. The trailing
`\queryid\1.1\` IS correct — that string is part of the fixed format-template tail
(`.rdata 0x0095a624`), not a substituted value. Only the `\gamever\%s\` field is filled in
at runtime, and it uses `"1.6"`.

**OpenBC implication**: clean-room implementations must emit `\gamever\1.6\` to match stock
Bridge Commander's masterserver version filter. A clean-room server that emits `\1.1\` will
be rejected by any masterserver replaying stock's version-filter logic.

In both wire formats, `XXXXXXXX` is the 8-character base64-encoded result of RC4-encrypting
the 6-byte challenge with `"Nm3aZ9"`.

## Server List Struct Layout (from gs_list_init / 0x006aa100) [v5-validated 2026-05-28]

The malloc'd 0xA0-byte ServerList struct. Offsets verified against `gs_list_init`'s write
sites (the constructor is the source-of-truth for struct shape):

| Offset | Size | Field | Set By |
|--------|------|-------|--------|
| +0x00 | 4 | State/status | FUN_006aa660 |
| +0x04 | 4 | Server entry hash struct (0x18-byte entries, 0x40 buckets) | `FUN_006ad180` |
| +0x0C | 32 | Game name (`"bcommander"`) | `gs_list_init`, copied from `param_1` |
| +0x2C | 32 | Secret key (`"Nm3aZ9"`) | `gs_list_init`, copied from `param_3` |
| +0x4C | 32 | Game name copy (`param_2`) | `gs_list_init`, copied from `param_2` |
| +0x6C | 4 | Num basic fields (`param_4=10`) | `gs_list_init` |
| +0x70 | 4 | Basic field memory | `malloc(param_4 * 0x1c)` |
| +0x78 | 4 | Basic info callback | `gs_list_init` (`param_5 = LAB_0069c420`) |
| +0x7C | 4 | User data (GameSpy this ptr) | `gs_list_init` (`param_7`) |
| +0x80 | 4 | Window name ref | `gs_list_init` (`&lpWindowName_0097dc28`) |
| +0x88 | 4 | TCP socket (master conn) | `gs_master_tcp_connect` |
| **+0x94** | 4 | **Poll/timer struct** (`FUN_006acb30`, 500 entries) | `gs_list_init` (`puVar3[0x25]`) **[C2: was +0x08 pre-v5]** |
| +0x98 | 4 | Connection result | `SL_master_connect` |
| **+0x9C** | 4 | **Mode-side state field** (cleared by `SL_master_connect` on group/info2 paths) **[C3: was labeled padding pre-v5]** | `SL_master_connect` |

**C2 (v5 correction)**: the pre-v5 doc placed the timer/poll struct at `+0x08`. The
decompiled `gs_list_init` writes the `FUN_006acb30` result to `puVar3[0x25]`, i.e., byte
offset `+0x94`. Nothing is written to `+0x08` by the constructor.

**C3 (v5 correction)**: the pre-v5 doc labeled `+0x9C` as "Padding/unused". The decompiled
`SL_master_connect` writes `0` to `*(undefined4 *)(param_1 + 0x9c)` in two distinct branches
(the groups path and the info2 path), so it is a state/mode side-channel — likely related to
the `+0x90` mode field already in the table.

## qr_t Struct Layout

The qr_t struct is passed as `param_1` to `qr_send_validate_and_final` (`0x006ac950`).

> [!NOTE]
> **Clar-1 + OQ1**: this validation pass anchored only the `+0x48` secret-key offset directly
> against `qr_send_validate_and_final`'s decompilation. The rows beyond `+0x48` (callback
> pointers, sequence counters, heartbeat retry, active flag, total query counter) are
> `[unanchored — SDK-derived; OQ1 covers a focused dig]`. They look plausible against the
> external GameSpy QR1 SDK source, but the validation pass could not place them at write
> sites in `stbc.exe`. Treat them as `confidence: low` pending OQ1 resolution.
>
> **Clar-2**: the "qr_t" struct and the "GameSpy" struct (`param_1` to
> `GameSpy::InitBrowser` at `0x0069c3a0`) are **different structs**. Offsets like `+0xDC`
> (server list ptr), `+0xE0` (`GameSpy.serverList`), `+0xED` (init guard byte), `+0xEE`
> (other flag) belong to the **GameSpy** object, not qr_t. Cross-reference
> [gamespy-discovery.md](gamespy-discovery.md) for the GameSpy object layout.

| Byte Offset | Field | Status |
|---|---|---|
| +0x00 | Query socket (SOCKET) | [unanchored — SDK-derived] |
| +0x04 | Heartbeat socket (SOCKET) | [unanchored — SDK-derived] |
| +0x08 | Game name (char[32]) | [unanchored — SDK-derived] |
| **+0x48** | **Secret key (char[32])** | **v5-validated 2026-05-28** — confirmed by `qr_send_validate_and_final` call site |
| +0xC8 | Basic info callback | [unanchored — see OQ1] |
| +0xCC | Rules callback | [unanchored — see OQ1] |
| +0xD0 | Players callback | [unanchored — see OQ1] |
| +0xD8 | Last heartbeat tick | [unanchored — see OQ1] |
| +0xE0 | Query sequence counter | [unanchored — see OQ1] |
| +0xE4 | Active flag | [unanchored — see OQ1] |
| +0xE8 | Heartbeat retry counter | [unanchored — see OQ1] |
| +0xEC | Total query counter | [unanchored — see OQ1] |

## Sibling cross-references [v5-validated 2026-05-28]

These cross-anchor with [gamespy-discovery.md](gamespy-discovery.md)'s v5 pass:

- `gs_rc4_cipher` @ `0x006ac050` — same function called by both QR path and ServerList path
- Secret key `"Nm3aZ9"` — built as stack literals in `GameSpy::InitBrowser` @ `0x0069c3a0`
- ServerList byte offset `+0x2C` for secret-key storage — written by `gs_list_init`, read by
  `SL_master_connect`

The companion doc places these in the wider discovery/heartbeat flow; this doc focuses on
the crypto/auth payload.

## Can We Reimplement This?

**Yes, absolutely.** The algorithm is:

1. **Standard RC4 KSA** (key scheduling) — identical to textbook RC4
2. **Modified RC4 PRGA** — one-line change: `i = (data[n] + 1 + i)` instead of `i = (i + 1)`
3. **Standard Base64 encoding** with the canonical `A-Za-z0-9+/` alphabet

The secret key `"Nm3aZ9"` is publicly known (it was extracted from the binary years ago
and is documented in GameSpy open-source SDK reimplementations like OpenSpy and 333networks).

For our dedicated server:
- We can call the existing functions in the binary (at `0x006ac050` and `0x006abf70`) via
  function pointer casts in our C code
- OR we can reimplement them entirely in the proxy DLL (cleaner, no dependency on exact
  binary layout)
- The challenge from the master is typically 6 random bytes; the response is always 8
  printable base64 characters

### Calling Existing Binary Functions

```c
/* Function pointer typedefs for the existing binary functions */
typedef void (__cdecl *fn_gs_rc4_cipher)(int key, int keyLen, int data, int dataLen);
typedef void (__cdecl *fn_gs_validate_encode)(unsigned char *src, int srcLen, unsigned char *dst);

#define GS_RC4_CIPHER         ((fn_gs_rc4_cipher)0x006ac050)
#define GS_VALIDATE_ENCODE    ((fn_gs_validate_encode)0x006abf70)

void compute_validate_from_binary(const char *challenge, char *out)
{
    char buf[128];
    int len = strlen(challenge);
    memcpy(buf, challenge, len);

    GS_RC4_CIPHER((int)"Nm3aZ9", 6, (int)buf, len);
    GS_VALIDATE_ENCODE((unsigned char *)buf, len, (unsigned char *)out);
}
```

## Verification Against Known Implementations

This algorithm matches the GameSpy QR1 SDK `gs_encrypt()` / `gs_encode()` functions
documented in:
- OpenSpy server source
- 333networks master server source
- Luigi Auriemma's gslist tool
- The original GameSpy SDK (leaked/archived versions)

The "modified RC4" with `data[n] + 1 + i` is the distinguishing feature of GameSpy's
implementation and is well-known in the game server emulation community.

## Open Questions

- **OQ1**: qr_t struct rows beyond `+0x48` — the rows for callback pointers at
  `+0xC8/+0xCC/+0xD0`, last-heartbeat at `+0xD8`, sequence counter at `+0xE0`, active flag
  at `+0xE4`, heartbeat retry at `+0xE8`, and total query counter at `+0xEC` are not
  anchored in this validation pass. They appear consistent with the external GameSpy QR1
  SDK source but have not been placed at write sites in `stbc.exe`. Resolving would require
  chasing the qr_t initializer (likely via `FUN_006ac1e0`'s parent path, or a callee that
  mallocs and populates qr_t via `FUN_006ac5f0`/`FUN_006ac7a0`/...). Overlaps with
  [gamespy-discovery.md](gamespy-discovery.md) OQ1.
- **OQ2**: Does any code path emit `\gamever\1.1\` instead of `\1.6\`? The pre-v5 doc
  example showed `1.1`. The only gamever literal located in `.rdata` is `"1.6"` at
  `0x0095a668`. Most likely the `1.1` in the prior example was a doc typo (carried over
  from the `\queryid\1.1\` tail), not a second wire variant. Worth a quick cross-check
  before closing.
- **OQ3 (OpenBC-impact)**: Does OpenBC's clean-room masterserver auth spec emit `1.6` or
  `1.1` for the `\gamever\` field? If `1.1`, the clean-room server's auth response will
  not match what stock BC clients send, and any masterserver that filters on the version
  field will reject it. **Flag for clean-room cascade** — confirm OpenBC's
  `gamespy-crypto-analysis.md` (if it exists) before any masterserver deployment.

## Companions

- [docs/networking/alby-rules-cipher-analysis.md](alby-rules-cipher-analysis.md) — the
  other crypto path in stbc.exe (UDP packet cipher, distinct from GameSpy auth)
- [docs/networking/gamespy-discovery.md](gamespy-discovery.md) — the GameSpy LAN/master
  discovery flow that drives both the QR and ServerList paths
- [docs/networking/network-protocol.md](network-protocol.md) — places this auth flow in
  the wider transport stack
