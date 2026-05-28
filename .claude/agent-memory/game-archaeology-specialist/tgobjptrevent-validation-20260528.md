# TGObjPtrEvent (Doc #13, LAST mid-tier) — 2026-05-28

Protocol mid #13 — closes the mid-tier (rows 4..13). FAST validation
because the doc was already well-anchored from prior RE passes
(45% combat PythonEvent analysis); class-layout claims survived
byte-by-byte check.

## Headline

**Class layout 0x2C / wire format 21B / 11 producers ALL verified.**
Zero wire-format corrections. Zero producer-list corrections. Three
non-wire-affecting corrections (C1 fabricated middle class /
C2 vtable slot numbering / C3 SWIG wrapper anchoring gap).

## Material findings

### C1 — "TGSubsystemEvent (0x101)" is fabricated

String search for "TGSubsystemEvent" returns **zero matches** in
STBC.exe. The IsA chain `0x10C -> 0x101 -> 0x02` is structurally
correct but the middle-link name is wrong:

- 0x101 = **TGEvent base class itself** (vtable 0x00895FF4, ctor
  FUN_006d5c00). Single byte pattern `B8 01 01 00 00 C3` hit at
  0x006d5ce0 = GetFactoryID slot of vtable 0x00895FF4.
- 0x10C = TGObjPtrEvent (sibling to TGCharEvent 0x105)
- 0x105 = TGCharEvent — IsA returns true for `{0x105, 0x101, 0x02}`
  — SAME shape as TGObjPtrEvent, confirming they are SIBLINGS
  directly under TGEvent.
- 0x02 = SWIG-base root (no GetFactoryID emitter found for this
  factory ID, unlike 0x101/0x105/0x10C/0x8129 which each have
  exactly one MOV EAX, imm32 / RET pair).

Implication: the doc's class hierarchy diagram has an extra layer
that doesn't exist. Flatten it.

### C2 — Vtable slot numbering shifted

Doc says slot 0 = "scalar_deleting_dtor at 0x00403310". Memory at
0x0088869C shows slot 0 = 0x00403320 (the real dtor for size 0x2C).
Address 0x00403310 the doc misidentifies is actually **a third RTTI
string-return function** returning "TGObjPtrEventPtr" — a SWIG
pointer-typeinfo name distinct from the stream-RTTI "_p_TGObjPtrEvent".

Same three-string pattern exists for TGCharEvent (`TGCharEvent` /
`_p_TGCharEvent` / `TGCharEventPtr` at 0x008e54d0/dc/ec) and
ObjectExplodingEvent (`ObjectExplodingEvent` / `_p_ObjectExplodingEvent`
/ `ObjectExplodingEventPtr` at 0x008da270/88/a0). This is universal
to SWIG-bridged TGEvent subclasses in BC.

Full TGObjPtrEvent vtable is at least 17 slots through +0x40 (not
the 12-14 the doc body describes).

### C3 — SWIG wrapper functions not anchored

Doc cites 5 SWIG wrapper addresses (0x005C7F10 / 0x005C7F90 /
0x005C8000 / 0x005C8070 / 0x005C80E0). NONE are defined as functions
in the current Ghidra DB. The string identifiers exist exactly where
the doc says (0x0092eab0..0x0092eaf4) but the function bodies aren't
disassembled — same pattern as engine-snapshot-20260528.md flagged
("annotation scripts never applied to current import").

Two options for the doc:
- (a) re-run `tools/ghidra_annotate_swig.py` to populate
- (b) demote SWIG addresses to `confidence: medium`

## Wire format spot-checks (all PASS)

| Claim | How verified |
|-------|--------------|
| 21 bytes total | base TGEvent::WriteToStream writes 4×i32 (factory_id + event_type + source_obj_ref + dest_obj_ref) via vtable[0x64]+vtable[0x84]; subclass adds 1×i32 via vtable[0x84]; opcode byte = 1 |
| obj_ptr at +0x28 | ctor `param_1[10] = 0`; every producer writes `*(iVar+0x28) = obj_id` |
| Source/Dest encoding NULL→0 / sentinel→0xFFFFFFFF / else→obj+0x04 | direct decompile of TGEvent::WriteToStream FUN_006d6130 |
| Class size 0x2C | every producer allocates via `FUN_00717b70(0x2c)` + `FUN_00718010` + ctor 0x00403290 |
| Dual-fire pattern | FUN_00571f40 (phaser) writes 0x81 then 0x7C; FUN_0057f580 (tractor) writes 0x7D then 0x7C; FUN_0057c9e0 (torpedo) writes 0x7C only |
| Host-only gate on 0x008000DC | `if (DAT_0097fa89 != '\0' && this+0xa4 && this+0xa8)` at FUN_00574010 + FUN_005825a0 |
| Previous-target for ET_TARGET_WAS_CHANGED | FUN_005ae210 reads CURRENT target into iVar1 BEFORE creating event, then `*(iVar3+0x28) = iVar1+4` |
| 30 ctor xrefs | exact get_xrefs_to count |
| 5 vtable DATA xrefs | exact get_xrefs_to count, exact 5 addresses |

## Field-anchor pattern observed (high-leverage)

Every producer follows the same shape:
```
FUN_00717b70(0x2c)               ; CRT new-fn size hint
iVar = FUN_00718010(...)         ; allocator
if (iVar) iVar = FUN_00403290(0) ; TGObjPtrEvent_Ctor
*(iVar+0x10) = event_type        ; ET_xxxx
FUN_006d6270(source)             ; SetSource (TGEvent::SetSource)
FUN_006d62b0(dest)               ; SetDestination
*(iVar+0x28) = obj_id            ; obj_ptr
FUN_006da2a0(iVar)               ; AddEvent (TGEventManager::AddEvent)
```

**Spotting a TGObjPtrEvent producer** in unknown code: look for the
`FUN_00717b70(0x2c)` -> `FUN_00718010` -> `FUN_00403290(0)` sequence.
The `(0x2c)` size literal is the primary signal — 0x2C = sizeof
TGObjPtrEvent. This pattern made finding the 30 producer sites trivial.

## Patterns from prior memory that worked again

- **Single-hit byte pattern for class identity** — `B8 <factory_id> 00 00 C3`
  for a 16-bit factory ID OR `B8 <factory_id_byte> 00 00 00 C3` for an 8-bit
  one finds GetFactoryID emitters uniquely. Used here for 0x10C / 0x105 /
  0x101 / 0x8129. Same pattern from `rtti-validation` and `objcreate` memory.
- **TGObject network ID = `*(obj+4)`** confirmed yet again across all
  11 producers. Used for source_obj_ref / dest_obj_ref / obj_ptr resolution.
- **`s_UNKNOWN_008d858c` allocation tag** is the SWIG type info name passed
  to the allocator — common across all TG event subclasses. Same TG class
  marker pattern.

## SWIG triple-string RTTI pattern (NEW, generalizable)

Every SWIG-bridged TGEvent subclass has THREE strings near each other:
1. `<ClassName>` — used by GetClassName (vtable slot 9)
2. `_p_<ClassName>` — used by GetSWIGName (vtable slot 10) — POINTER TYPE
3. `<ClassName>Ptr` — used by GetSWIGPtrName (vtable slot 11) — SWIG POINTER WRAPPER

The doc currently treats slot 11 as inherited from TGEvent base
because the pattern was missed. For any TGEvent doc audit going
forward (set-phaser-level for TGCharEvent, ObjectExplodingEvent for
factory 0x8129), check vtable slot 11 — should return `<Name>Ptr`.

## Annotations applied (16 renames, 1 struct, 3 plates)

- TGObjPtrEvent_Ctor (0x00403290) — full plate with class layout,
  wire format, all 11 producers
- TGObjPtrEvent_GetFactoryID (0x004032b0)
- TGObjPtrEvent_IsA (0x004032c0)
- TGObjPtrEvent_GetClassName (0x004032f0)
- TGObjPtrEvent_GetSWIGName (0x00403300)
- TGObjPtrEvent_GetSWIGPtrName (0x00403310) — NEW slot identification
- TGObjPtrEvent_ScalarDeletingDtor (0x00403320)
- TGObjPtrEvent_CopyFrom (0x006d6da0)
- TGObjPtrEvent_WriteToStream (0x006d6dc0) — with wire-format plate
- TGObjPtrEvent_ReadFromStream (0x006d6df0) — with plate
- Game_SetPlayerLocal (0x004066d0)
- Ship_SetTarget (0x005ae210)
- ShipSubsystem_SetCondition (0x0056c470)
- RepairSubsystem_RaisePriority (0x005519e0)
- PhaserSystem_StopFiringAtTarget (0x00574010)
- TractorBeamSystem_StopFiringAtTarget (0x005825a0)
- Struct `TGObjPtrEvent` (0x2C / 12 fields)

## Open Qs propagated forward

1. **Vtable slots 4-5 variant Write/Read** (0x006d6e20 / 0x006d6e50)
   are pre-conditional on `FUN_006d5ec0` / `FUN_006d5ff0` — likely
   SAVE-vs-NETWORK stream-class discrimination. Useful for
   set-phaser-level / pythonevent-wire-format leaves.
2. **SWIG anchoring gap** — affects all four protocol leaf docs that
   cite SWIG wrappers (pythonevent-wire-format, collision-effect-protocol,
   set-phaser-level-protocol, delete-player-ui-wire-format). One annotation
   script run would fix all four at once.
3. **Vtable slot 16 (0x006ffa90)** reads +0x20/+0x24/+0x28 — the doc
   marks +0x20/+0x24 as "reserved" but this slot uses them. Need leaf
   doc to confirm Python-script handler-invocation metadata role.

## Cross-anchors verified

- `TGEvent_Ctor` (FUN_006d5c00) and `TGEvent_Dtor` (FUN_006d5d70)
  both write vtable PTR_FUN_00895FF4 -> base class is at vtable
  0x00895FF4. Matches event-system-architecture.md (mid #8).
- TGEvent base ctor field inits: `+0x14 = 0xbf800000` (-1.0f
  timestamp) — confirmed.
- `FUN_006f15c0` (TGEventHandlerObject::InvokePythonHandler) appears
  at vtable slot 8 (+0x20) — matches event-system mid #8 claim
  "universal slot 8".
- `DAT_0097fa89` = IsHost — confirmed at host-only-gate sites
  (cross-anchor with engine snapshot global table).

## What I would NOT redo

- Spending time hunting SWIG wrapper bodies. They are address-stable
  but the import-state of the current Ghidra DB doesn't have them
  disassembled. Either re-run the annotation script (project decision)
  or accept "medium confidence on SWIG addresses, high confidence on
  SWIG names". Don't burn a turn on each one.
- Trying to find a class literally named "TGSubsystemEvent". Already
  ruled out by string search early.
