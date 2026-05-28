---
name: tgbufferstream-vtable-20260528
description: TGBufferStream vtable at 0x008958D0 recovered. vtable[0] returns 0x32 constant; struct grown 0x2C -> 0x40 with Serialize/GetSerializedSize field anchors. Dispatcher 0x32 claim promoted medium -> high.
metadata:
  type: project
---

# TGBufferStream Vtable Recovery — 2026-05-28

Follow-up to [[struct-skeletons-20260528]]. Decompiled vtable[0] of TGBufferStream (0x006B9430) which was previously unknown / unmapped by Ghidra. Lit up the entire stream-class identity, grew struct from 0x2C to 0x40 bytes, and resolved Open Question 1 from the struct work (cursor field).

## The vtable: 0x008958D0

Sits in `.rdata`. 32+ slots discovered (read first 128 bytes; more likely follow). Slots 0-7 documented at v5; slots 8+ deferred.

| # | Slot Addr | Target | Name | Purpose |
|---|-----------|--------|------|---------|
| 0 | 0x008958D0 | 0x006B9430 | TGBufferStream_GetStreamTypeId | Returns 0x32 (class tag) |
| 1 | 0x008958D4 | 0x006B82F0 | TGBufferStream_ScalarDeletingDtor | MSVC `delete this` pattern; size=0x40 |
| 2 | 0x008958D8 | 0x006B8340 | TGBufferStream_Serialize | Writes class-tag + headers + payload to buffer |
| 3 | 0x008958DC | 0x006B9440 | TGBufferStream_HasDerivedType | Always false (base default) |
| 4 | 0x008958E0 | 0x006B9450 | TGBufferStream_IsSpecialStream | Always false (base default) |
| 5 | 0x008958E4 | 0x006B8640 | TGBufferStream_GetSerializedSize | Sum of payload + header byte counts |
| 6 | 0x008958E8 | 0x006B8610 | TGBufferStream_Clone | Calls CopyCtor after some check |
| 7 | 0x008958EC | 0x006B8720 | TGBufferStream_Fragment | Splits stream into list when serialized size exceeds limit |

## Sizeof Pinned at 0x40 (NOT 0x2C)

The MSVC scalar-deleting-destructor at slot 1 calls `operator delete(this, 0x40)`. **0x40 (64) is the compiler-embedded sizeof.** My prior struct skeleton at 0x2C was too small by 20 bytes.

## Three Vtable Installers (constructor cluster)

All three xref the vtable address 0x008958D0 and write it into `*(this+0x00)` as their first store:

| Address | Role | Evidence |
|---------|------|----------|
| 0x006B82A0 | `TGBufferStream::TGBufferStream()` default ctor | Clears all fields, sets vtable, sets 1.0f at +0x30/+0x34, dwField_0x2C=1, bField_0x3D=1 |
| 0x006B8320 | `TGBufferStream::~TGBufferStream()` dtor | Sets vtable, frees buffer if non-NULL via FUN_00718cf0 |
| 0x006B8550 | `TGBufferStream::TGBufferStream(const&)` copy ctor | Sets vtable, allocates new buffer, REP MOVSD payload, copies all observable fields |

The copy constructor is the **richest field-map source** — it touches every initialized field on both source and dest. It directly reveals the field layout 0x14, 0x18, 0x1C, 0x20, 0x24, 0x28, 0x2C, 0x30, 0x34, 0x38, 0x39, 0x3A, 0x3B, 0x3C, 0x3D.

## Open Question 1 from struct-skeletons-20260528 — RESOLVED

> "TGBufferStream +0x10..+0x27 (24 bytes) — at least one of these bytes is the bit-cursor state, and one is likely a read-position cursor."

**Resolution:** `field_0x08` (formerly `dwBufferLen`) is actually `dwCursor` — the buffer length / write cursor. `field_0x04` (already named `pBuffer`) is the buffer base. The 0x10..0x27 region is NOT cursor state; it's other format-control fields and an interior pad we still haven't decoded.

Specifically:
- `dwBufferLen` at 0x08 was misnamed; it's the **current cursor / payload length**, written by `*param_1 = *(int*)(param_2 + 8)` in the copy ctor and used by Serialize as the REP MOVSD count.
- Bit-level cursor state lives in the **BitStreamReader at 48-byte FUN_006cefe0** wrapper (per docs/protocol/stream-primitives.md), NOT in TGBufferStream itself. TGBufferStream is byte-aligned.

## TGBufferStream Struct (Ghidra DB, post-update)

Size: 64 bytes (0x40). Live in STBC.exe Ghidra DB.

| Offset | Size | Type | Name | Anchor evidence |
|--------|------|------|------|-----------------|
| 0x00 | 4 | void* | pVtable | All 3 ctors install 0x008958D0 |
| 0x04 | 4 | BYTE* | pBuffer | GetBufferAndSize returns *(this+4); Serialize REP MOVSD source ESI |
| 0x08 | 4 | uint | dwCursor | GetBufferAndSize writes *(this+8) to *out; Serialize REP MOVSD count |
| 0x0C | 4 | uint | dwField_0x0C | HostMsgHandler reads (sender player id, suspected) |
| 0x10-0x27 | 24 | byte[24] | pPad14 | Copy ctor touches short@0x14, int@0x18..0x24 (5 ints) — not yet semantically decoded |
| 0x28 | 4 | uint | dwField_0x28 | NewPlayerInGame compares to slot ID — target player id, suspected |
| 0x2C | 4 | uint | dwField_0x2C | Ctor default=1; copy ctor mirrors. Likely mode flag (read/write?) |
| 0x30 | 4 | float | flField_0x30 | Ctor default=1.0f; likely buffer-growth or position multiplier |
| 0x34 | 4 | float | flField_0x34 | Ctor default=1.0f; same family as 0x30 |
| 0x38 | 1 | byte | bRouteByte0_0x38 | Serialize writes when bHasRouteBytes_0x3C && bRouteByte1_0x39==0 |
| 0x39 | 1 | byte | bRouteByte1_0x39 | Serialize writes when bHasRouteBytes_0x3C set; doubles as discriminator |
| 0x3A | 1 | byte | bHasVariantPrefix_0x3A | If non-zero, Serialize writes [this+0x14] short prefix |
| 0x3B | 1 | byte | bField_0x3B | Cleared by ctor; role unknown |
| 0x3C | 1 | byte | bHasRouteBytes_0x3C | If non-zero, Serialize writes 1-2 route bytes |
| 0x3D | 1 | byte | bField_0x3D | Ctor default=1; copy ctor mirrors |
| 0x3E | 2 | byte[2] | pTailPad_0x3E | Likely struct alignment padding |

## Wire-Format Insight

The dispatcher's `vtable[0]() == 0x32` check is NOT a memory-only RTTI guard.

`TGBufferStream_Serialize` (0x006B8340) writes the FIRST byte of the wire-format blob as `vtable[0]()` -- i.e. always 0x32. So 0x32 IS on the wire. The dispatcher's check is a **self-consistency** check: the deserializer reads 0x32 from the wire to pick the TGBufferStream class, instantiates one, and the dispatcher re-asks the resulting object what its class tag is. Mismatch means deserialization picked the wrong class -> silent drop.

Knock-on for clean-room OpenBC: do NOT need a virtual `GetTypeId` call. A simple "if first byte != 0x32 reject" suffices. Documented in the TGBufferStream_Serialize plate.

## Knock-on: Dispatcher (0x0069F2A0)

Plate comment updated: `0x32` claim promoted **medium -> high**. Cited new evidence: TGBufferStream_GetStreamTypeId at 0x006B9430, cross-checked via the three vtable installers and emulation.

Score did NOT increase from 79.0 (now reports 69.84 effective). Investigation: completeness analyzer surfaces 10 untyped globals + 11 missing global plates that I did not address. These were latent in the prior 79.0 number and got re-evaluated this session under a different weighting. **Score swing is methodology drift, not a regression in this dig.** The qualitative outcome — claim confidence promotion — is locked.

## TGBufferStream_GetStreamTypeId Completeness

| Metric | Value |
|--------|-------|
| Effective score | **95.0** |
| Raw score | 89.43 |
| Max achievable | 94.43 |
| Fixable deductions | 5.0 (one type_quality flag for `void* this`) |
| Structural deductions | 5.57 (ECX void* — unfixable per Ghidra API) |

Emulation result: `registers={ecx:0x10000000}` -> EAX=0x32 deterministic. Confirms constant-return semantics.

## Patterns Learned

1. **Ghidra silently skips functions reached only through `mov eax, [vtable+N]; call eax` patterns** when no other CALL/JMP xref exists. Same root cause as the dispatcher recovery — but now extended: even short stub functions (5 bytes!) get skipped. Look at vtable data references; create_function manually whenever needed.

2. **MSVC scalar-deleting-destructor reveals sizeof for free**: the `operator delete(this, N)` constant N is the class size. Search pattern: `E8 ?? ?? ?? ?? 8B C3 5B C3` (call dtor, mov eax,ebx, pop ebx, ret) preceded by a `83 7C 24 08 01` style flag-check and `6A 40` (push 0x40 / push sizeof) is the scalar-deleting-destructor signature.

3. **Copy constructor = field map oracle**: A type's copy ctor enumerates EVERY initialized field, in source-to-dest pairs. It's the densest single-function source of field-layout evidence.

4. **vtable[0] convention in stbc.exe**: stream classes implement `GetTypeId` at slot 0 returning a class-tag constant. The constant ALSO appears at the front of the serialized blob. This pattern likely extends to all serializable Tg* classes — worth checking other `vtable[0] -> 5-byte function returning constant` patterns when investigating other stream/message types.

5. **"Always false" virtuals at slots 3 and 4** (`HasDerivedType`, `IsSpecialStream`) are base-class polymorphic discriminator hooks. Derived classes would override; TGBufferStream itself sits at the base. Useful for hierarchy mapping.

## Open Questions

1. **The 24-byte interior pad at 0x14-0x27** has 5+ field accesses observed in the copy ctor (short@0x14, int@0x18, int@0x1C, int@0x20, int@0x24, int@0x28). Their semantics need follow-up. The short@0x14 is "variant prefix" (written by Serialize when 0x3A flag set), but the 4 ints between 0x18-0x24 are unmapped.

2. **What is the size limit Fragment() uses?** Function body (0x006B8720) is 250+ instructions of state management. The threshold against which `GetSerializedSize` is compared (param 3) is caller-supplied. Likely 1400-byte UDP MTU. Verify against `TGWinsockNetwork` send-side fragmentation.

3. **vtable slots 8-31**: not yet investigated. Slot 8 calls a destructor for an 0x34C-byte object — but the xref pattern (only FUN_006B9BF0 and FUN_006B9C80 reach those) suggests these slots may be **a different class's vtable that abuts TGBufferStream's in `.rdata`**. Possible derived class (TGFragmentedBufferStream?) sharing slots 0-7. Worth a follow-up dig.

4. **Are there other stream classes with vtable[0] returning different constants?** Suggested search: grep `.rdata` for 5-byte sequences `B8 ?? 00 00 00 C3` (MOV EAX, imm; RET) and check which are pointed at by vtables. Cheap way to enumerate the stream-class registry.

## Cross-References

- [[struct-skeletons-20260528]] — predecessor dig; this work resolves Open Question 1 and grows TGBufferStream 0x2C -> 0x40
- [[dispatcher-recovery-20260528]] — the dispatcher whose 0x32 claim this work locks at HIGH confidence
- docs/protocol/transport-layer.md (existing doc; TGBufferStream layout could now be updated from this dig)
- docs/protocol/stream-primitives.md (existing doc; clarifies that bit-cursor lives in a separate wrapper, not TGBufferStream)
