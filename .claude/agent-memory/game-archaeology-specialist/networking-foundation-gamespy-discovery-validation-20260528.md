---
name: networking-foundation-gamespy-discovery-validation-20260528
description: Networking foundation doc #3 (gamespy-discovery, 975 lines) — v5 validation. ZERO wire/algorithm corrections; ~6 struct-table drift corrections (DWORD-index vs byte-offset confusion + qr_t+0xE4 mislabeled as packet counter). RC4+base64+heartbeat+vtable byte-confirmed.
metadata:
  type: project
---

# Networking Foundation Doc #3: gamespy-discovery.md v5 Validation

**Doc**: `docs/networking/gamespy-discovery.md` (975 lines)
**Family position**: 3rd networking-family v5 validation (after foundation #1 and #2)
**Date**: 2026-05-28
**Verdict**: Wire format + algorithms + addresses **CONFIRMED**. Struct-offset table has DWORD-index-vs-byte-offset notation drift requiring corrections to Section 4 (qr_t Layout) and ServerList Layout. Sections 10 (Crypto), 5 (Function Address Table), 6 (Data Section Addresses), and 12 (Vtable) are rock-solid.

## Function Addresses (12 spot-checks, all CONFIRMED present)

| Address | Doc Name | Confirmed |
|---------|----------|-----------|
| 0x006ac1e0 | qr_handle_query | YES — dispatcher loops table at 0x0095a71c, 8 cases (0=basic..7=secure) |
| 0x006ac050 | gs_rc4_cipher | YES — modified PRGA: `i = (data[n] + 1 + i) % 256` byte-confirmed |
| 0x006aca60 | qr_send_heartbeat | YES — format string at 0x0095a904, sendto to DAT_00995880 |
| 0x006aa720 | SL_create_broadcast_socket | YES — socket(2,2,0x11), SOL_SOCKET/SO_BROADCAST, stored ServerList+0x88 |
| 0x006aa770 | SL_send_lan_broadcast | YES — htons port loop, sendto `\status\` from 0x0095a554 len 8 |
| 0x006abd80 | qr_heartbeat_tick | YES — 30000ms check, max 10 counter at +0xE8, socket at +0x04 |
| 0x006abf70 | gs_validate_encode | YES — 3-byte→4-char base64 with FUN_006ac020 char mapping |
| 0x006aa4c0 | SL_master_connect | YES — recv→strstr secure→RC4→base64→send auth+list req via TCP |
| 0x0069bfa0 | GameSpy::ctor | YES — sets vtable, +0xED=0, +0xEE=1, +0xEF=0, loads TGL, registers handler 0x60006 |
| 0x0069c440 | GameSpy::Tick | YES — branching matches Section 12 pseudocode |
| 0x006ab620 | SL_start_update | YES — case 0/1/2/default mode dispatch |
| 0x006ac550 | qr_send_packet | YES — appends `\queryid\%d.%d`, sendto |

## Strings/Data Addresses (10 byte-confirmed)

| Address | Expected | Confirmed (hex) |
|---------|----------|-----------------|
| 0x00959c24 | `bcommander` | `62 63 6f 6d 6d 61 6e 64 65 72 00` |
| 0x0095a4fc | `stbridgecmnd01.activision.com` | `73 74 62 72 69 64 67 65 63 6d 6e 64 30 31 2e 61 63 74 69 76 69 73 69 6f 6e 2e 63 6f 6d 00` |
| 0x0095a554 | `\status\` | `5c 73 74 61 74 75 73 5c 00` |
| 0x0095a5cc | `\list\%s\gamename\%s\final\` | matches |
| 0x0095a624 | `\gamename\%s\gamever\%s\location\0\validate\%s\final\\queryid\1.1\` | matches |
| 0x0095a668 | `1.6` (auth gamever) | `31 2e 36 00` |
| 0x0095a66c | `\secure\` | `5c 73 65 63 75 72 65 5c` |
| 0x0095a8f0 | `\statechanged\%d` | matches |
| 0x0095a904 | `\heartbeat\%d\gamename\%s` | matches |
| 0x00895564 | GameSpy vtable | 11 slots all match doc line 906-916 |

## Algorithm Confirmations (byte-level)

### Modified RC4 (FUN_006ac050) — CONFIRMED

Decompile shows PRGA loop:
```
uVar5 = (uint)(byte)(*(char *)(iVar4 + param_3) + '\x01' + (char)uVar5);
```
That's exactly `i = (data[n] + 1 + i) % 256` (the GameSpy QR1 modification). Standard RC4 has `i = (i+1) % 256`. Doc's Section 10 algorithm description is **byte-confirmed**.

### Secret Key Construction (FUN_0069c3a0) — CONFIRMED

```
local_c = 0x4e;  // 'N'
local_b = 0x6d;  // 'm'
local_a = 0x33;  // '3'
local_9 = 0x61;  // 'a'
local_8 = 0x5a;  // 'Z'
local_7 = 0x39;  // '9'
local_6 = 0;     // '\0'
```
`"Nm3aZ9\0"` — exactly 6 chars + NUL — built on stack, passed to FUN_006aa100 as `param_3`. Stored at ServerList+0x2C (DWORD index 0xB → byte offset 0x2C). Doc Section 10 confirmed.

### Heartbeat Format (FUN_006aca60) — CONFIRMED

`FUN_008599b9(local_100, s__heartbeat__d_gamename__s_0095a904, *(undefined4*)(param_1 + 0xe4), param_1 + 8)`
- `%d` arg = qr_t+0xE4 (the "port" value)
- `%s` arg = qr_t+0x08 (gamename = "bcommander" from ctor)
- sendto destination = `DAT_00995880` (master sockaddr)

### Heartbeat Timer (FUN_006abd80) — CONFIRMED
- `30000 < DVar2 - uVar1` — 30s interval
- `'\n' < cVar3` (10) — max 10 heartbeats
- `0x493e1` = 300,001 ms stale-window check
- Counter at qr_t+0xE8, socket at qr_t+0x04, last-tick at qr_t+0xD8

## Drift / Corrections Required

### Correction #1 (Section 4 qr_t Layout — MAJOR mislabeling)

Doc table line 376-382 shows offsets as "+0x37, +0x38, +0xE4" but these are mixed DWORD indices and byte offsets, and qr_t+0xE4 is mislabeled. Actual layout from decompile:

| Doc says | Actual | Evidence |
|----------|--------|----------|
| `+0x37 DWORD` Query seq counter | byte **0xDC** (= DWORD index 0x37) | FUN_006ac1e0: `*(int *)(param_1 + 0xdc) = *(int *)(param_1 + 0xdc) + 1` (byte-indexed); FUN_006ac550: `param_1[0x37]` (SOCKET*-indexed → byte 0xDC) |
| `+0x38 DWORD` Fragment counter | byte **0xE0** (= DWORD index 0x38) | FUN_006ac550: `param_1[0x38] = SVar2 + 1;` |
| `+0xE4 int` Packet counter | byte **0xE4** = **active flag AND heartbeat port** | FUN_006abce0: `if (param_1[0x39] != 0)` (DWORD idx 0x39 = byte 0xE4); FUN_006aca60: `%d` arg = `*(undefined4 *)(param_1 + 0xe4)` |
| `+0x3A byte` Flag | byte **0xE8** (= DWORD idx 0x3A) | Doc says "cleared at start" — but FUN_006abd80 uses byte 0xE8 as heartbeat counter (matches doc's other claim at +0xE8) |

The doc presents offsets in mixed bases. Section 12 line 970 correctly says `qr_t[0x39] (active flag)` — that means DWORD index 0x39 = byte 0xE4. So Section 4 table's `+0xE4 int Packet counter` is the **same field** as Section 12's "active flag" — just contradictorily labeled.

**Best correction**: Rewrite qr_t Layout table in byte offsets consistently with annotations like "byte 0xDC (DWORD idx 0x37)":
- byte 0xDC = Query sequence counter
- byte 0xE0 = Fragment counter within query
- byte 0xD8 = Last heartbeat timestamp (GetTickCount)
- byte 0xE4 = Active flag / heartbeat port number
- byte 0xE8 = Heartbeat repetition counter (max 10)

### Correction #2 (Section 4 ServerList Layout — broadcast socket offset)

Doc says ServerList+0x22 = broadcast socket. Actual: **ServerList+0x88**.

Evidence: FUN_006aa720 stores broadcast socket at `param_1 + 0x88` (byte offset). FUN_006aa770 reads it from `param_1 + 0x88`. FUN_006aa4c0 (master connect) also uses `param_1 + 0x88` for TCP — so it's a **shared socket field**.

Likely root cause: 0x22 was a DWORD index (0x22 * 4 = 0x88).

Same pattern applies to other ServerList entries in the table. Probably:
- `+0x23 DWORD Last activity timestamp` → byte **0x8C** (DWORD idx 0x23)
- `+0x2C char[] Secret key` — actually correct as byte offset 0x2C (DWORD index 0xB → byte 0x2C, both consistent)

The mix is what makes the table misleading. Decompile shows secret key stored at `puVar3 + 0xB` (DWORD index 0xB = byte 0x2C) — and FUN_006aa4c0 reads it from `param_1 + 0x2c` (byte 0x2C). Both notations land on byte 0x2C.

### Correction #3 (Section 6 — "duplicate" master server hostnames)

Doc line 222-224 lists 0x0095a4fc, 0x0095a594, 0x0095a834 as identical "duplicates". Actually they play distinct roles:

| Address | Role | Evidence |
|---------|------|----------|
| 0x0095a4fc | **Mutable destination** for masterserver.txt override | FUN_006aa100: `_strncpy(s_stbridgecmnd01_activision_com_0095a4fc, local_100, 0x40)` |
| 0x0095a594 | **Immutable source** (canonical hardcoded) | Same function: fallback copies from 0x0095a594 to 0x0095a4fc when no masterserver.txt |
| 0x0095a834 | (different role — not verified) | Out of scope this pass |

So 333networks support **works via runtime overwrite of 0x0095a4fc**. Doc Section 11 (Implications) implicitly captures this but Section 6 misleadingly calls them duplicates.

### Correction #4 (Section 12 Dead Code claim)

Doc line 957-963 says dead block is at 0x006ab558-0x006ab5BF. Confirmed **stronger** than "no xrefs" — Ghidra does not recognize 0x006ab558 as code at all (`disassemble_function` returns "No function found"). The block exists as raw bytes containing the dead RVAs for the master-resolution strings but has never been disassembled. Doc claim holds but could be sharpened.

## Cross-anchors from Protocol Family (zero conflicts)

Pre-validated foundations all hold:
- UtopiaModule base 0x0097FA00 — confirmed (FUN_0069c580 reads `DAT_0097fa78` = UtopiaModule+0x78 = TGWinsockNetwork)
- TGWinsockNetwork at 0x0097FA78 — confirmed
- GameSpy at UtopiaModule+0x7C — confirmed via SWIG `Appc.UtopiaModule_GetGameSpy(self) -> self[0x1F]` = +0x7C

## Open Questions

1. **qr_t+0xD0..D4 callbacks** — doc lists basic/info/rules/players callback pointers at qr_t+0xC8/CC/D0/D4. Spot-checked FUN_006ac5f0 (basic builder) but did not confirm the callback table location. Defer to a deeper qr_t struct dig if needed.
2. **Heartbeat send failure (rc=-1)** — Section 11's "open question". The master sockaddr at 0x00995880 stays NULL when masterserver.txt is missing, which would explain rc=-1, but the trace says masterserver.txt was present. Unresolved.
3. **0x0095a834 third hostname copy** — role unclear from this validation pass.

## Promotion (low → medium → high)

| Claim | Pre | Post | Reason |
|-------|-----|------|--------|
| Wire format (LAN broadcast, response field order, fragmentation 1349) | [trace] | **[v5-validated]** | Code-level confirmation via FUN_006aa770, FUN_0069c580, FUN_006ac660 |
| RC4 modification `i = (data[n]+1+i)%256` | [doc] | **[v5-validated]** | FUN_006ac050 byte-confirmed |
| Secret key "Nm3aZ9" | [doc] | **[v5-validated]** | FUN_0069c3a0 stack literal byte-confirmed |
| Heartbeat 30s/max-10 timing | [doc] | **[v5-validated]** | FUN_006abd80 constants byte-confirmed |
| GameSpy vtable 11 slots | [doc] | **[v5-validated]** | 0x00895564 bytes read and matched |
| masterserver.txt override mechanism | [trace] | **[v5-validated]** | FUN_006aa100 strncpy to 0x0095a4fc confirmed |
| qr_t struct offsets | [doc] | **[v5-validated-corrected]** | See Correction #1 |
| ServerList struct offsets | [doc] | **[v5-validated-corrected]** | See Correction #2 |
| Dead code 0x006ab558 | [doc] | **[v5-validated]** | Stronger — Ghidra hasn't even disassembled it |

## Cross-references for documentation-writer

- Companion doc: `docs/networking/gamespy-crypto-analysis.md` — being validated in parallel; should cross-link Section 10 of gamespy-discovery.md to crypto-analysis for full algorithm depth
- Pre-anchored: protocol-family memos (UtopiaModule, TGWinsockNetwork, GameSpy ptr)
- Should update: `docs/networking/README.md` family index, mark gamespy-discovery as v5-validated
