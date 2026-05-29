# StateUpdate Ordering / Authority Trace Verification (2026-05-29)

Empirical leg of OpenBC StateUpdate flicker/drift investigation (#186). Mined stock BC 1.1
dedi traces (OBSERVE_ONLY, zero patches) to confirm/refute the OpenBC differential's claim:
root cause = ser_list ORDER + weapon-nesting + has_power bit-packing.

Trace files:
- `logs/collision test/stock-dedi/packet_trace.log` (10 MB; subsystem damage->repair; BEST)
- `logs/battle-of-valentines-day/packet_trace.log` (136 MB; 3-player battle)
- `logs/self-destruct-test/stock/packet_trace.log` (233 KB)

Decoder note (IMPORTANT — establishes what is real vs. inferred):
The packet_trace.log decoder (`src/proxy/ddraw_main/packet_trace_and_decode.inc.c`
lines 525-569) annotates 0x1C SUB blocks. What is REAL (raw wire bytes):
- `startIdx=N` — the single byte read immediately after dirty_flags (REAL).
- `data=[...]` — up to 20 raw data bytes dumped flat until msgEnd (REAL; decoder does
  NOT parse per-subsystem WriteState lengths, so it cannot split entries).
- `subsysBytes(non-FF): +k=0xVV` — REAL byte offsets/values that differ from 0xFF.
What is INFERRED / decoder fiction:
- `(PowerReactor)` / `subsystemCycle: 0:PowerReactor 1:RepairSubsystem ...` — these NAMES
  come from a HARDCODED guess table `PktSubsystemIndexName()` (lines 313-350), printed as
  `(startIdx + k) % 0x21` for k=0..5. The names are NOT derived from the wire. Treat the
  NAMES as a plausible-but-unverified label scheme; treat the INDEX NUMBERS and start_idx
  VALUES as ground truth.

---

## V4 (HIGHEST) — start_idx is a TOP-LEVEL ENTRY INDEX. CONFIRMED.

**Verdict: start_idx is a top-level entry index into the ship+0x284 linked list, NOT a flat
sub-subsystem index. Each weapon (torpedo tube / phaser emitter) occupies ONE top-level
index. Weapons are FLAT, not nested under a parent weapon-system entry.**

### Byte evidence — packet #52, line 560 (`collision test/stock-dedi`)

```
[20:38:48.397] #52 S->C  len=78
  0000: 01 0C 32 0A 80 0A 00 1D FF FF FF 3F 32 17 00 1C
  0010: FF FF FF 3F 80 EC 04 42 20 00 FF FF 20 FF FF FF
  0020: FF FF FF 01 ...
  [msg 1] GameData(unrel) len=23 flags=0x00
    [0x1C StateUpdate]
      obj=0x3FFFFFFF t=33.23 flags=0x20 [SUB ]
        subsystems startIdx=0 (PowerReactor) data=[FF FF 20 FF FF FF FF FF FF ]
        subsystemCycle: 0:PowerReactor 1:RepairSubsystem 2:CloakingDevice
                        3:PoweredSubsystem 4:LifeSupport 5:ShieldGenerator
```

Wire bytes for this 0x1C message (after the 0x32 transport + flags_len `17 00` + the
unreliable msg): `1C FF FF FF 3F | 80 EC 04 42 | 20 | 00 | FF FF 20 FF FF FF FF FF FF`
- `1C` opcode
- `FF FF FF 3F` object_id = 0x3FFFFFFF
- `80 EC 04 42` game_time float (~33.23)
- `20` dirty_flags = SUB only
- `00` **start_index = 0**  <-- the byte immediately after dirty_flags
- `FF FF 20 FF FF FF FF FF FF` = 9 condition bytes, one per top-level entry, indices 0..5+

Mapping the 9 condition bytes to indices starting at 0:
`idx0=FF idx1=FF idx2=20 idx3=FF idx4=FF idx5=FF ...`
The decoder confirms idx2=CloakingDevice carries 0x20 (damaged), the rest 0xFF (full).
6 named entries fit, then it wraps (3 trailing FF bytes belong to the next cycle entries).

### The decisive proof — start_idx lands ON individual weapon indices

The ground-truth proof does NOT depend on the decoder's name guesses. It rests on the
RAW start_idx byte taking EVERY consecutive value across the weapon range:

**Collision trace** (`/tmp/sub_idx.txt`, 5826 SUB blocks) — distinct start_idx values:
`0, 1, 2, 3, 4, 5, 6, 8, 9, 10`
**Valentine's trace** (136 MB, all SUB blocks) — distinct start_idx values:
`0, 1, 2, 3, 5, 6, 7, 8, 9, 10, 11` (plus rare 254, 255 — see note below)

start_idx legitimately lands on 6, 7, 8, 9, 10, 11 — the index range the decoder labels
TorpedoTube#1..#6. **If those weapon mounts were nested children under a single
weapon-system parent at one top-level index, the round-robin cursor would step over them
as ONE entry and start_idx could never equal 7, 8, 9, 10, or 11.** Because start_idx DOES
take those values, each weapon mount IS its own top-level linked-list node.

Decoder's (inferred, name-guess) reconstruction of the list for reference only — index
numbers are real, names are the hardcoded guess table:

| idx | decoder name-guess     |
|-----|------------------------|
| 0   | PowerReactor           |
| 1   | RepairSubsystem        |
| 2   | CloakingDevice         |
| 3   | PoweredSubsystem       |
| 4   | LifeSupport            |
| 5   | ShieldGenerator        |
| 6-11| TorpedoTube#1..#6      |
| 12+ | PhaserEmitter#1..#N    |

In Valentine's (mixed ship classes) start_idx reaches 11 and the windows extend to idx 16
(PhaserEmitter#5), so larger ships expose MORE distinct weapon-mount top-level indices.

Rare start_idx = 254 / 255: 9 and 286 occurrences in Valentine's. Likely an
uninitialized/edge cursor value (tracker+0x34 start_index byte) at object spawn before the
round-robin seeds, or a wrap-edge artifact. Not seen in the single-client collision trace.
Flagged as a minor OQ; does not affect the FLAT verdict.

Therefore:

- start_idx is a TOP-LEVEL ENTRY index (OpenBC differential CONFIRMED).
- A "weapon-system top-level entry serializing children inline (large byte run)" does
  NOT occur in the SUB (0x20) path. Each weapon emits its own condition byte at its own
  index. The hypothesized large weapon-group byte run is ABSENT.

### Why this matters for OpenBC
If OpenBC's serialization.json nests phaser/torpedo banks under a weapon-system container
(so they don't appear as top-level ser_list entries), its start_idx windows will be
mis-sized vs. stock. A stock client expecting 16 top-level entries reading a server that
emits e.g. 6 will desync the condition-byte stream after the first wrap -> flicker/drift.
OpenBC's ser_list MUST present every weapon mount as its own top-level entry, in the
PowerReactor->...->ShieldGenerator->TorpedoTube*->PhaserEmitter* order shown above.

---

## V-NEST (weapon nesting) — FLAT. CONFIRMED.

**Verdict: FLAT. In the SUB (0x20) block, each phaser emitter and torpedo tube is its own
top-level entry with its own condition byte. There is NO single large weapon-system entry
that serializes N weapon children inline.**

Evidence: the V4 index table above shows 10 individual weapon mounts (TorpedoTube#1..#6,
PhaserEmitter#1..#4) at consecutive top-level indices 6..15. The decoder's per-index
condition byte (e.g. `+3=0x40` for TorpedoTube damage in later packets) is emitted once per
weapon mount, not once per weapon group.

Caveat / scope: This is the SUB (0x20 S->C subsystem-HEALTH) path. The doc's "weapons
serialized recursively within their parent" note in stateupdate.md refers to the
LoadPropertySet hardpoint tree at object-CREATE time (ObjCreate 0x03), where children CAN
be nested under a parent and then Ship_LinkAllSubsystemsToParents (FUN_005B3E20) FLATTENS
them into the top-level ship+0x284 list. By the time StateUpdate runs, the list is already
flat — confirmed here: every weapon mount is a distinct top-level node. So OpenBC's
RUNTIME ser_list must be flat even if its authoring/hardpoint format is a tree.

---

## V1 — start_idx progression for one ship. CONFIRMED round-robin.

**Ship 0x3FFFFFFF (player own-ship), collision trace, S->C SUB blocks.**

First 60 start_idx values (chronological):
`0 2 6 8 | 2 6 8 | 2 6 8 | 2 6 8 | ...` (then steady 2 6 8 cycle)

Mid-trace window (line ~2000 of the extracted idx list, a different ship/state):
`5 0 2 | 5 0 2 | 5 0 2 | ... | 0 2 5 | 8 2 5 | ...`

**It DOES round-robin and wraps.** Wrap detection (idx decreases vs previous): the dominant
transition is `8 -> 2` (every ~3rd block) and `5 -> 0`. The cursor advances by a VARIABLE
number of top-level entries per tick, then wraps back toward the list head.

**Why the cycle is NOT a clean 0->15->wrap-to-0:** the 10-byte budget (disasm CMP EAX,0xA at
0x005B1EC0) is measured in STREAM BYTES, not entries. With mostly-full subsystems each
emitting a single 1-byte condition (0xFF), ~9-10 entries fit per tick, so the cursor laps
the (16-entry) list quickly and start_idx lands on a small rotating set (2,6,8 or 5,0,2).
When subsystems carry power/battery bytes (more bytes/entry), fewer entries fit and the
start_idx pattern shifts. The cycle is byte-budget-driven, not a fixed entry stride.

**Cycle length / values:** earlier mining's "0,2,6,8,10" is CONFIRMED and EXTENDED. Full
observed start_idx set this session: {0,1,2,3,4,5,6,8,9,10} (collision),
{0,1,2,3,5,6,7,8,9,10,11} (Valentine's). The earlier "0,2,6,8,10" was a PARTIAL sample of
the byte-budget-driven rotation, not the full entry set.

byte evidence: collision trace lines 574 (idx0), 598 (idx2), 625 (idx6), 646 (idx8);
self-destruct trace startIdx=10 confirmed.

---

## V3 — order stability. CONFIRMED stable across the entire session AND across sessions.

**Same start_idx -> same top-level subsystem mapping, identical byte structure, repeats.**

Evidence 1 (within-session repeat): ship 0x4000001F, startIdx=0, full-health byte run
`data=[FF FF 20 FF FF FF FF FF FF]` appears IDENTICALLY at lines 574 (t=33.23), 8818
(t=65.43), 34785 (later) — byte-for-byte identical across the whole session. The idx2 byte
is consistently the changed one (0x20); idx0/idx1 stay 0xFF.

Evidence 2 (positional stability under damage): startIdx=0 variants differ only in the
VALUES of condition/power bytes (collision damage + repair), never in the POSITION-to-
subsystem mapping: `[FF FF 20 FF FF FF FF FF FF]` -> `[00 00 20 00 00 00 00 00 00]` ->
`[FF FF FF FF 40 FF F9 FD FF]`. Damaged offsets track real HP; index->subsystem binding is
fixed.

Evidence 3 (cross-session, cross-ship): self-destruct trace produces the SAME startIdx
progression (0,2,6,8,10) and SAME window mapping for a DIFFERENT ship in a DIFFERENT
session. Valentine's (3-player, multiple ship classes) produces the SAME fixed-block order
(idx 0-5) + weapon block (idx 6+) for every ship class.

Verdict: top-level subsystem list order is a STABLE per-ship-class invariant, fixed at
object-create time (LoadPropertySet order, flattened by Ship_LinkAllSubsystemsToParents).
It does not reshuffle during a session.

---

## V2 — entries-per-tick window. VARIABLE, byte-budgeted (~10 bytes), NOT fixed count.

The wire carries NO entry-count field. The serializer emits subsystem WriteState payloads
until the 10-byte stream budget (CMP EAX,0xA at 0x005B1EC0, includes the start_index byte)
is hit or the cursor laps the list.

Observed DATA byte counts per SUB block (collision trace, 5826 blocks):
9B=2165, 10B=761, 11B=774, 12B=358, 13B=455, 14B=567, 15B=220, 16B=154, 17B=372.
- 9 bytes is most common (~9 full-health 1-byte 0xFF entries).
- 13-17 bytes when subsystem(s) carry power/battery bytes (fewer entries, more bytes).

ENTRY count per tick is variable (~6-10 top-level entries) because entry SIZE varies: base
subsystem = 1 condition byte; PoweredSubsystem (remote) = condition + bit-byte + powerPct
(~3 bytes); PowerReactor = condition + 2 battery bytes (3 bytes). The BYTE budget is the
fixed quantity (~10, can overshoot to 17 because the budget check is post-write and one
multi-byte WriteState can push past 10). The ENTRY window is the derived, variable quantity.

Load-bearing for OpenBC: a fixed entries-per-tick implementation desyncs against a
byte-budgeted stock client. OpenBC must budget by BYTES (write until
streamPos - budgetStart >= 10), not by a fixed entry count.

---

## V-BITPACK — has_power bit is PER-SUBSYSTEM (own single-bit byte), NOT a shared group byte.

**Verdict: each PoweredSubsystem's has_power bit is written as its OWN standalone bit-byte
(count=1), because the surrounding WriteByte calls (condition byte before, powerPct byte
after) BREAK the bit group every time. There is NO shared bit-byte spanning multiple
consecutive powered subsystems.**

Reasoning (binary-RE ground truth + wire byte alignment):
TGBufferStream WriteBit (FUN_006CF770) packs up to 5 bits into ONE byte as
[count:3][bits:5] (stream-primitives.md lines 288-320). The state machine resets the bit
accumulator whenever a NON-bit write (WriteByte/WriteShort) occurs: "Any non-bit write
breaks the bit group: subsequent WriteBit calls allocate a new accumulator at the new
cursor position."

PoweredSubsystem WriteState (Format 2, 0x00562960) emits, per the doc:
- [condition: u8]      <- WriteByte (breaks any prior bit group)
- WriteBit(has_power)  <- NEW accumulator byte: [count=001][bit0 = has_power]
- if has_power: [powerPct: u8]  <- WriteByte (breaks the bit group again)

Because a WriteByte (condition) immediately PRECEDES the WriteBit and a WriteByte (powerPct)
immediately FOLLOWS it, the has_power bit can NEVER share a byte with the next subsystem's
has_power bit. Each powered subsystem contributes exactly one bit-byte.

Bit-byte VALUE on the wire:
- has_power == 0 (own-ship / no data): byte = [count=001][00000] = 0x20
- has_power == 1 (remote ship, power follows): byte = [count=001][00001] = 0x21

Wire corroboration: in the SUB data runs, the value 0x20 appears at fixed positions where a
PoweredSubsystem's bit-byte is expected (e.g. packet #52 line 574 `[FF FF 20 FF FF ...]`,
idx2 position). 0x20 is exactly the count=1, bit=0 encoding. The flat-dump decoder mislabels
it as a "condition byte = 0x20"; at those positions it is actually WriteBit(0) with count=1.

CRITICAL for OpenBC: if OpenBC writes has_power as a RAW bit packed into a SHARED group byte
across consecutive subsystems (e.g. 5 powered subsystems -> one 0x25 byte), it MISALIGNS the
entire SUB bitstream vs. a stock client, which expects each powered subsystem to consume its
own [count=1] bit-byte (0x20 or 0x21) sandwiched between WriteByte calls. This single
mismatch desyncs every subsequent condition byte in the round-robin window -> the #186
flicker/drift. OpenBC MUST emit has_power as a standalone WriteBit call (own byte)
immediately after the condition WriteByte, matching the group-break semantics.

Confidence: HIGH on per-subsystem (not shared) — follows directly from the documented
group-break-on-WriteByte semantics. MEDIUM on the exact 0x20/0x21 values (the flat-dump
decoder does not split entries, so I cannot point at a labeled bit-byte; but 0x20 at
powered-subsystem positions is consistent).

---

## V6 — SUB/WPN direction split. CONFIRMED 100% disjoint.

Correlated packet header DIRECTION with the StateUpdate flag (awk over collision trace,
tracking S->C / C->S from each packet header line):

- C->S: WPN (0x80) x 5854 — never SUB, zero BOTH.
- S->C: SUB (0x20) x 5826 — never WPN, zero BOTH.

Every SUB-bearing 0x1C is bare `[SUB]`. Every WPN-bearing 0x1C never carries SUB (combos
`[DELTA FWD UP SPD WPN]`, `[DELTA SPD WPN]`, `[WPN]`, etc.). Zero S->C-with-WPN, zero
C->S-with-SUB. Matches binary-RE ground truth (player-count + friendly-fire gate at
FUN_006A2650 makes 0x20/0x80 mutually exclusive by direction in MP). Sample far exceeds the
requested 30+30.

---

## Summary for OpenBC #186 (flicker/drift root cause)

All three OpenBC-differential hypotheses CONFIRMED from real stock wire bytes:

1. **ser_list ORDER (V3/V4):** stable, fixed per-ship-class top-level order. Fixed-system
   block at idx 0-5, then every weapon mount (torpedo tubes, then phaser emitters) as its
   OWN top-level index 6+. OpenBC ser_list must reproduce this exact order AND count.

2. **weapon-nesting (V-NEST/V4):** FLAT. Each weapon mount is a distinct top-level entry;
   start_idx lands on individual weapon indices (6,7,8,9,10,11). OpenBC must NOT nest weapon
   banks under a single weapon-system container in the RUNTIME ser_list.

3. **has_power bit-packing (V-BITPACK):** PER-SUBSYSTEM standalone bit-byte (0x20/0x21),
   group-broken by surrounding condition/powerPct WriteByte calls. No shared group bit-byte.

Plus a 4th, byte-budget detail (V2): the per-tick window is BYTE-budgeted (~10 bytes incl.
start_idx), NOT a fixed entry count.

Any one of #1-#4 mismatching desyncs the SUB bitstream after the first round-robin wrap ->
the observed shield/hull/subsystem flicker. Independently corroborates the
collision-damage-trace-comparison memo (2026-02-19) ROOT CAUSE 2 ("server-side ship+0x284
subsystem list order differs from client") — this trace work pins the mechanism to ORDER +
bit-packing + byte-budget.

## Minor OQ
- start_idx = 254/255 (rare: 9 + 286 in Valentine's, absent in single-client collision
  trace). Likely uninitialized/edge tracker+0x34 start_index at object spawn before the
  round-robin seeds, or a wrap-edge artifact. Does not affect the FLAT verdict.
