---
name: sensor-hull-subsystem-validation-20260528
description: Sensor and Hull subsystems (ship+0x2C8 / ship+0x2C4) recovered. Slot 1 (+0x2C4) identity DEFINITIVE → HullSubsystem (NOT PowerSubsystem reactor). Slot 4 (+0x2C8) DEFINITIVE → SensorSubsystem. Ghidra symbol names `PowerSubsystem_Ctor` (at 0x00560470) and `CloakingSubsystem_Ctor` (at 0x00566D10) are HISTORICAL MISNAMES from pre-v5 work — they actually construct HullSubsystem and SensorSubsystem respectively. Full class layouts, vtable maps, WriteState behavior, IsObjectVisible algorithm anchored.
metadata:
  type: project
---

# Sensor & Hull Subsystems — v5 Recovery (2026-05-28)

## 2026-05-28 UPDATE: Ghidra plates corrected (cloaking swap)

The cloaking-side misnaming is now FIXED in the Ghidra DB:

- **0x00566D10** → `SensorSubsystem_Ctor` (was wrongly `CloakingSubsystem_Ctor`). Body: vtable 0x00892EAC + `param_1[0x30]=2` powerMode + 8 field-zeros. NO state machine, NO SEH frame.
- **0x0055E2B0** → `CloakingSubsystem_Ctor` (was wrongly `SensorSubsystem_Ctor` after a prior cascade rename). Body: vtable 0x00892C04 + SEH frame + `FUN_0055F930()` state-machine init + `param_1[0x28]=2`.

Both plate comments rewritten with the correction note + Ship__SetupProperties case mapping (0x8139 → Sensor, 0x813A → Cloak). Saved.

**Lesson learned (swap pattern)**: When two functions share a wrong name in Ghidra, a single `rename_function(old, new)` call resolves the old name to ONE of them non-deterministically. To swap names cleanly, ALWAYS rename one to a `_TMP` intermediate first, then assign final names in order. The first attempt here hit the wrong target (0x0055E2B0 instead of 0x00566D10) and had to be undone via the temp-name technique.

## Original verdict (unchanged below)

## Verdict on slot 1 (+0x2C4) — DEFINITIVE

**ship+0x2C4 = HullSubsystem** instance (NOT PowerSubsystem reactor).

The reactor (PoweredMaster, class 0x813E) lives at **ship+0x2B0**, set by case 0x813E in Ship__SetupProperties. The case 0x8138 (CT_HULL_PROPERTY) sets ship+0x2C4, which is HullSubsystem (class ID 0x8027).

### Why prior memos disagreed

Several prior v5 memos (power-system C1 cascade, leaf #19 post-cascade) labelled ship+0x2C4 as "PowerSubsystem (Reactor) class ID 0x8027". That labelling is WRONG; the cascade-correction RESTORED a false reading. The truth:

- **vtable 0x00892C98** has `GetTypeID() → 0x8027` (byte-confirmed at 0x00560490: `MOV EAX, 0x8027 ; RET`)
- **Ghidra symbol `PowerSubsystem_Ctor @ 0x00560470` is HISTORICAL MISNAME.** This ctor sets vtable 0x00892C98 and is called ONLY from Ship__SetupProperties case 0x8138 (CT_HULL_PROPERTY).
- The actual PowerSubsystem (reactor) ctor is `PoweredMaster_Ctor @ 0x00563530`, sets vtable `PTR_FUN_0088A1F0`, called from case 0x813E (CT_POWERED_SUBSYSTEM_PROPERTY).
- The class-name strings returned by vtable 0x00892C98 slots 9/10/11 are `"HullClass"`, `"_p_HullClass"`, `"HullClassPtr"` (byte-confirmed at 0x008E4EC0/0x008E4ECC/0x008E4EDC). Not "PowerSubsystem".
- Type ID 0x8027 is the HullSubsystem instance class (it has NO `CT_HULL_SUBSYSTEM` self-string — only `CT_HULL_PROPERTY` 0x8138 for the property side and `CT_HULL_SUBSYSTEM` 0x???? at 0x00911EB4 for a separate class label). The SWIG bindings use "HullClass" (not "HullSubsystem") — Totally Games called the live runtime instance "HullClass" in their nomenclature.

**Conclusion**: vtable 0x00892C98 IS the HullClass / HullSubsystem instance vtable; the Ghidra name `PowerSubsystem_Ctor` is a misnomer that the v5 cascade-correction perpetuated and should be reverted.

## Verdict on slot 4 (+0x2C8) — DEFINITIVE

**ship+0x2C8 = SensorSubsystem** instance.

- **vtable 0x00892EAC** has `GetTypeID() → 0x8023` (byte-confirmed at 0x00566D70: `MOV EAX, 0x8023 ; RET`)
- **Ghidra symbol `CloakingSubsystem_Ctor @ 0x00566D10` is HISTORICAL MISNAME.** This ctor sets vtable 0x00892EAC and is called ONLY from case 0x8139 (CT_SENSOR_PROPERTY).
- The REAL CloakingSubsystem ctor is at `0x0055E2B0` (also named CloakingSubsystem_Ctor — duplicate name), sets vtable `0x00892C04`, called from case 0x813A (CT_CLOAKING_SUBSYSTEM_PROPERTY) into ship+0x2DC.
- The 6 event-handler registrations all reference `"SensorSubsystem::HandleX"` strings (0x008E5130 PeriodicScan, 0x008E515C ShipDecloaked, 0x008E5184 ShipIdentified, 0x008E51AC ExitSet, 0x008E51CC EnterSet, 0x008E51EC SetPlayer) and their handler bodies live in functions at 0x00567CD0 / 0x00567F60 / 0x005680C0 / 0x00568040 / 0x00568080 / 0x00566F50 (FUN_00566F50 registers all 6).

This corrects the in-memory Ghidra cloaking-validation C4 H2 recommendation in `gameplay-mid-cloaking-validation-20260528.md` (which said "rename 0x00566D10 from SensorSubsystem_Ctor to CloakingSubsystem_Ctor"). The cloaking memo was RIGHT that the original Ghidra name "SensorSubsystem_Ctor" matched real code, but a later session renamed it to "CloakingSubsystem_Ctor" — making the Ghidra DB now wrong in the OPPOSITE direction. The correct name is **SensorSubsystem_Ctor**.

---

## Hull Subsystem (ship+0x2C4)

### Identity
| Attribute | Value | Evidence |
|---|---|---|
| Class | HullSubsystem / HullClass | vtable slot 9 returns string "HullClass" at 0x008E4EC0 |
| Type ID | 0x8027 | GetTypeID at 0x00560490 |
| IsA chain | 0x8027 → 0x801B (ShipSubsystem) → 0x102 | IsA disasm at 0x005604A0–0x005604BC |
| vtable | 0x00892C98 | sets by HullSubsystem_Ctor at 0x00560470 (currently misnamed `PowerSubsystem_Ctor`) |
| Property type | 0x8138 (CT_HULL_PROPERTY) | Ship__SetupProperties case 0x8138 |
| Instance alloc size | 0x88 bytes (136) | `FUN_0040f030(0x88, ..., 0)` at 0x005b... case 0x8138 |
| Ship slot | ship+0x2C4 | Ship__SetupProperties writes uVar3 there |

### Field layout

HullSubsystem is a near-trivial extension of ShipSubsystem base. The ctor (0x00560470) calls `FUN_0056B970` (ShipSubsystem base ctor) and sets vtable — NO additional fields beyond what ShipSubsystem provides.

ShipSubsystem base layout (from FUN_0056B970 ctor):
```
+0x00   vtable ptr
+0x04…+0x1C  Inherited from FUN_006D8F90 (DamageableObject? — TGObject base)
+0x14    childCount uint16 (= 0xFFFF init)
+0x18    parent ptr (NULL init)
+0x20    childArrayPtr (NULL init)
+0x2A    childCapacity uint16 (= 0xFFFF init)
+0x2C    childArrayBound uint16 (= 0xFFFF init)
+0x30    currentCondition (HP) float (= 1.0)   ← per-instance HP
+0x34    maxCondition float (= 1.0)             ← per-instance max HP
+0x38    conditionPct float (= 1.0)             ← cur/max derived
+0x3C    propertyPtr (= 0 init, set by SetProperty)
+0x40    something float (= 0 init)
+0x44    bool flag1 byte (= 0 init)
+0x45    bool flag2 byte (= 0 init)
+0x48    randPhase float (= rand()*0x00892FC0)
+0x4C    randSeedFloat float (= randPhase * 0x00888DBC)
+0x64    pad uint32 (= 0)
+0x68    pad uint32 (= 0x3A83126F = 1e-3f — small epsilon)
+0x6C    childSubsystemList head (= 0 init)
+0x70    sceneAttachPtr (= 0 init)
+0x78    DAT_0098039C float[5] watchers — 5 timer/state slots
+0x84    lastReadStateTime float (=DAT_009A2880 init)
+0x88    extension fields start (HullSubsystem has NONE)
```

The alloc size 0x88 (136) matches the ShipSubsystem base + vtable slot exactly. HullSubsystem adds NO instance fields.

### Vtable overrides

HullSubsystem (0x00892C98) inherits from ShipSubsystem (0x00892FC4). Slot-by-slot diff:

| Slot off | HullSubsystem | ShipSubsystem | Status |
|---|---|---|---|
| +0x00 dtor | 0x00560530 | 0x0056BB60 | OVERRIDE (HullSubsystem dtor calls FUN_00560560 = vtable+FUN_0056BB90) |
| +0x04 GetTypeID | 0x00560490 (= 0x8027) | 0x0056BAD0 (= 0x801B) | OVERRIDE |
| +0x08 IsA | 0x005604A0 (0x8027 ∨ 0x801B ∨ 0x102) | 0x0056BAE0 | OVERRIDE |
| +0x0C GetClassName_a | 0x006F1650 | 0x006F1650 | INHERITED |
| +0x10 WriteStream (save) | 0x0056CEB0 | (same) | INHERITED — generic ShipSubsystem save |
| +0x14 ReadStream (load) | 0x0056D010 | (same) | INHERITED — generic ShipSubsystem load |
| +0x18 ValidateStream (save) | 0x0056D170 | (same) | INHERITED |
| +0x1C FixupStream | 0x0056D1F0 | (same) | INHERITED |
| +0x20 GetClassName_b | 0x006F15C0 | (same) | INHERITED |
| +0x24 GetTypeName1 | 0x005604F0 → "HullClass" | 0x0056BB20 → "ShipSubsystem" | OVERRIDE |
| +0x28 GetTypeName2 | 0x00560500 → "_p_HullClass" | 0x0056BB30 → "_p_ShipSubsystem" | OVERRIDE |
| +0x2C GetTypeName3 | 0x00560510 → "HullClassPtr" | 0x0056BB40 → "ShipSubsystemPtr" | OVERRIDE |
| +0x30..+0x48 RTTI factory glue | (all same as ShipSubsystem) | (same) | INHERITED |
| +0x4C GetSwigClass | 0x00560520 → 0x0098B940 | 0x0056BB50 → ShipSubsystem swig | OVERRIDE (swig static) |
| +0x50..+0x5C class util | (all same) | (same) | INHERITED |
| +0x60 SetProperty | 0x0056BDC0 (ShipSubsystem::SetProperty — sets +0x18=property, then SetCondition(max)) | (same) | INHERITED |
| +0x68 Save_v2 | 0x0056D250 (children via slot +0x68) | (same) | INHERITED |
| +0x6C Load_v2 | 0x0056D2B0 (children via slot +0x6C) | (same) | INHERITED |
| +0x70 **WriteState** | **0x0056D320 = ShipSubsystem::WriteState** | (same) | INHERITED |
| +0x74 ReadState | 0x0056D390 = ShipSubsystem::ReadState | (same) | INHERITED |
| +0x78 misc | 0x00561140 | 0x0056D3D0 | OVERRIDE |
| +0x7C misc | 0x00561090 | 0x0056D440 | OVERRIDE |
| +0x80..+0xFF | (mostly inherited) | (mostly inherited) | INHERITED |

**Bottom line**: HullSubsystem is essentially `class HullSubsystem : ShipSubsystem { /* nothing new */ };` with a different type ID, class name, and SWIG bindings. It exists to:
1. **Receive the CT_HULL_PROPERTY** (hull metadata: ship class definition, fHullFactor, fHullSelectedChooseAlternate, HullProperty floats) and bind it as ShipSubsystem property at +0x3C.
2. **Participate in the round-robin subsystem list** at ship+0x284 — sending its HP byte in StateUpdate flag 0x20.
3. **Provide the per-ship identity** of "HullClass" for SWIG-script reflection.

### Hull HP relationship to DamageableObject (ship+0x14C)

The doc claim "ship+0x14c = DamageableObject HP slot (FLT_MAX undamaged sentinel per leaf #18)" is for the SHIP's hull HP. HullSubsystem's `+0x30 currentCondition` is a DIFFERENT field — it's the per-subsystem health, not the global ship hull HP.

How they relate:
- Ship hull HP lives at `ship+0x14C` (DamageableObject base level).
- HullSubsystem instance hull HP at `instance+0x30` mirrors the ship hull as a subsystem-tracker.
- ProcessDamage (damage-system.md) writes to `ship+0x14C` directly when damage targets the "hull" category.
- HullSubsystem's StateUpdate participation emits `condition_byte = ftol((this+0x30 / GetMaxCondition()) * 255.0)` — this is read by the CLIENT for UI/HUD purposes.

The two HP slots are kept in sync by some sync function — likely a ShipSubsystem watcher that mirrors ship+0x14C → instance+0x30. NEEDS verification: which function does this mirroring?

### Wire format (StateUpdate flag 0x20)

HullSubsystem emits via **ShipSubsystem::WriteState** (0x0056D320, slot +0x70):

```
+0    1 byte    condition_byte = ftol((currentCondition / maxCondition) * 255.0)
+1+   N bytes   For each child in instance+0x20..+0x1C-1, recurse child.vtable[+0x70]
end             vtable[+0xd8] (GetPos no-op) for end-marker symmetry
```

HullSubsystem has NO children (childArrayPtr=0, childCount=0xFFFF=invalid). So per-tick HullSubsystem payload in StateUpdate flag 0x20 is exactly **1 byte** (the condition byte representing HP percentage).

In a typical StateUpdate stream (3+ subsystems per tick within the 10-byte budget), HullSubsystem appears as a single byte at its round-robin position.

### Tick / Update

HullSubsystem has NO dedicated per-tick Update method. ShipSubsystem family uses event-driven state changes (e.g., `ShipSubsystem::SetCondition` is called from damage handlers, not from a per-frame Update). Hull HP is changed externally by:

- `ProcessDamage` → `ship+0x14C -= damage` (damage-system.md cascade)
- `Repair queue` → `ship+0x14C += repair_amount` (repair-system.md)
- `Explosion handler` → catastrophic HP zeroing

Then the next StateUpdate tick will encode the new condition byte automatically.

---

## Sensor Subsystem (ship+0x2C8)

### Identity
| Attribute | Value | Evidence |
|---|---|---|
| Class | SensorSubsystem | strings at 0x008E50F7 "?SensorSubsystem", 6 "SensorSubsystem::Handle*" strings 0x008E5130-0x008E51EC |
| Type ID | 0x8023 | GetTypeID at 0x00566D70 |
| IsA chain | 0x8023 → 0x801C (PoweredSubsystem) → 0x801B (ShipSubsystem) | IsA disasm at 0x00566D80–0x00566D9F |
| vtable | 0x00892EAC | sets by SensorSubsystem_Ctor at 0x00566D10 (currently misnamed `CloakingSubsystem_Ctor`) |
| Property type | 0x8139 (CT_SENSOR_PROPERTY) | Ship__SetupProperties case 0x8139 |
| Instance alloc size | 0xCC bytes (204) | `FUN_0040f030(0xcc, ..., 0)` at 0x005B428B for case 0x8139 |
| Ship slot | ship+0x2C8 | Ship__SetupProperties writes uVar3 there |

### Field layout

SensorSubsystem inherits from PoweredSubsystem (which extends ShipSubsystem). Layout:

```
+0x00   vtable ptr = 0x00892EAC
+0x04…+0x88  Inherited ShipSubsystem base fields (see HullSubsystem layout above)
+0x84   lastReadStateTime float
+0x88   PoweredSubsystem extension fields begin
+0x88   property+0x40 mirror (PowerSubsystem watcher 1)         [from PoweredSubsystem_Ctor]
+0x8C   property+0x44 mirror (PowerSubsystem watcher 2)
+0x90   PowerPercentageWanted (float 0..1, init 1.0)
+0x94   isMaster bool (byte init 1)
+0x98   PowerPercentage (current actual power) float
+0x9C   isPowered/isActive bool — gates many checks
+0xA0   misc PoweredSubsystem state
+0xA4   PowerSubsystem ctor flag (=0 init)
+0xA8   misc
+0xAC   visibleObjectCount uint32 (Sensor-specific!)
+0xB0   visibleObjectList head ptr (Sensor-specific)
+0xB4   visibleObjectList tail ptr (Sensor-specific)
+0xB8   visibleObjectFreeList head ptr (Sensor-specific)
+0xBC..+0xC4  reserved / scratch
+0xC0   powerMode = 2 (set by ctor — Sensor power mode enum)
+0xC8   baseSensorRange CACHE (copied from property+0x4C by SetProperty) — float
+0xCC   end of instance
```

The `+0xC8` field is the cached `BaseSensorRange` (mirrored from CT_SENSOR_PROPERTY+0x4C in the SetProperty call at 0x00567080: `MOV [ESI+0xC8], EAX` where EAX came from property[+0x50]). Wait — re-reading: 0x0056709E uses `EAX+0x50`, which is one float offset past +0x4C. Let me re-decode:

At 0x0056709B: `MOV EAX, [EAX+0x50]` reads from property+0x50. So instance+0xC8 = property+0x50.

**But the hash function reads property+0x4C** (`HashFoldFloat(*(undefined4 *)(iVar1 + 0x4c), &local_4)` in ComputeSubsystemIntegrityHash) — that's a DIFFERENT property field. Property+0x4C is "BaseSensorRange" (per the SWIG fn `SensorProperty_GetBaseSensorRange` at 0x009160F4 — `Of:SensorProperty_GetBaseSensorRange`); property+0x50 might be a related multiplier or `MaxProbes` field cached locally.

**Resolution**: property+0x4C IS BaseSensorRange (the hashed value); property+0x50 is a different field that gets cached at instance+0xC8 (likely `MaxProbes` per the SWIG fn `SensorProperty_GetMaxProbes` at 0x00916098). The `BaseSensorRange` is read live from property each frame via GetBaseSensorRange — it is NOT cached on the instance.

### Vtable overrides (sample of key slots)

| Slot off | SensorSubsystem | Behaviour |
|---|---|---|
| +0x00 dtor | 0x00566E20 | SensorSubsystem dtor |
| +0x04 GetTypeID | 0x00566D70 (= 0x8023) | constant return |
| +0x08 IsA | 0x00566D80 (0x8023 ∨ 0x801C ∨ 0x801B ∨ 0x102) | IsA chain |
| +0x60 SetProperty | 0x00567080 | calls ShipSubsystem::SetProperty(0x0056BDC0) then `FUN_0068F360` (cast to 0x8139) and stores `prop[+0x50]` → `this+0xC8` |
| +0x70 **WriteState** | 0x00562960 = **PoweredSubsystem::WriteState** | base 1 byte HP + 1 bit hasPower + (optional 1 byte powerPct if remote ship) |
| +0x74 ReadState | 0x005629D0 = PoweredSubsystem::ReadState | symmetric reader |
| +0x80..+0xE0 | various Sensor-specific methods incl. IsObjectVisible chain | see below |

### Sensor-specific functions found

| Address | Name | Behaviour |
|---|---|---|
| 0x00567190 | **SensorSubsystem::GetSensorRange** | returns `prop[+0x4C] * this[+0x98] * this[+0x34]` = `BaseSensorRange × PowerPct × HpPct`. Returns `_DAT_00888B54` (likely 0.0) if power-off (`this+0x9C==0`) or fail check. |
| 0x005671C0 | **SensorSubsystem::GetBaseSensorRange** | returns const `_DAT_00888B5C` = 4.0f. NB: this is NOT property-based; it's a static fallback constant. Real per-ship range uses `prop+0x4C` directly via GetSensorRange. Possibly unused / dead. |
| 0x005671D0 | **SensorSubsystem::IsObjectVisible** | full algorithm: cloak check (target+0x2DC+0xAC=='\x01' = fully cloaked = invisible), faction group match (`this+0x40 group == target+0x20 group`), 0x800E retry budget loop (FUN_0040AFE0(0x800E,&local_4)), distance/probe walk via list at `this+0xB0..+0xBC` |
| 0x00567CD0 | **SensorSubsystem::HandleSetPlayer** | global SensorSubsystem manager init (0x0098C000 / 0x0098C060); posts events 0x80008B (PeriodicScan begin) + 0x80005D via EventManagers 0x0097F838 + 0x0097F864 |
| 0x00567F60 | **SensorSubsystem::HandleEnterSet** | registers ship in active-Sensor list; calls FUN_00567440 / FUN_00568AD0 |
| 0x00568040 | **SensorSubsystem::HandleExitSet** | unregisters ship |
| 0x00568080 | **SensorSubsystem::HandleShipIdentified** | adds identified target to visibility list (FUN_00568C00 / FUN_00568EB0) |
| 0x005680C0 | **SensorSubsystem::HandlePeriodicScan** | recurring per-NPC scan; posts next 0x80008B event with `gameTime + 0x008E50F4` (likely 1.0s rescan interval) |
| 0x00566F50 | **SensorSubsystem::RegisterStaticHandlers** | calls FUN_006DA160/FUN_006DA130 to bind all 6 SensorSubsystem::Handle* methods to event types |
| 0x00566FD0 | **SensorSubsystem::RegisterEventTypes** | FUN_006DB380(0x80000E, ..., "HandleSetPlayer") and FUN_006D92B0(0x0098C0B0, 0x0080008B, ...) — registers the SET_PLAYER and PERIODIC_SCAN event types |
| 0x008DAB2C | "Fixing up SensorSubsystem statics\n" | called from FUN_00444840 — singleton/statics init |

### Sensor event types (registered by 0x00566FD0)

| Event ID | Symbol | Use |
|---|---|---|
| 0x80000E | (SET_PLAYER) | SensorSubsystem::HandleSetPlayer fires when player changes ships |
| 0x80008B | ET_SENSORS_PERIODIC_SCAN | Recurring per-tick scan timer event |
| 0x800087 | ET_SENSORS_SHIP_FAR_PROXIMITY | (string at 0x009104AC) |
| 0x800086 | ET_SENSORS_SHIP_NEAR_PROXIMITY | (string at 0x009104CC) |
| 0x800085 | ET_SENSORS_SHIP_IDENTIFIED | (string at 0x009104EC) |
| 0x800088 | ET_SENSORS_RANGE_CHANGED | (string at 0x00910508) |
| 0x80005D | (likely ENTER_SET broadcast) | posted by SetPlayer handler |
| 0x800010 | (TARGET_CHANGED — from MapWindow registration) | maps to MapWindow_GroupChangeHandler |

### What SensorSubsystem DOES

1. **Active target tracking**: maintains a per-ship list at +0xB0..+0xBC of identified hostile ships. Each entry has `[node]=ship_ptr, [next]=next_node, [prev]=prev_node`.
2. **Periodic scan tick**: every ~1.0s game-time, posts ET_SENSORS_PERIODIC_SCAN event which iterates set members and runs IsObjectVisible. Calls FUN_006DC3F0 (event queue add) and FUN_006D90E0 (free event).
3. **Cloak detection**: IsObjectVisible reads `target[+0x2DC]+0xAC` — target's CloakDevice fully-cloaked flag. If 1, target is INVISIBLE regardless of distance.
4. **Range calculation**: `range = BaseSensorRange × PowerPercentage × ConditionPct` — power drain and damage both reduce effective range proportionally.
5. **Visibility events**: posts ET_SENSORS_SHIP_IDENTIFIED when a target newly enters range; ET_SENSORS_SHIP_NEAR_PROXIMITY / FAR_PROXIMITY for distance thresholds.

### Wire format (StateUpdate flag 0x20)

SensorSubsystem emits via **PoweredSubsystem::WriteState** (0x00562960, slot +0x70):

```
+0    1 byte    condition_byte = ftol((currentCondition / maxCondition) * 255.0)
                 — Sensor's own HP (=full unless damaged in combat)
+1+   N bytes   For each child subsystem (none for Sensor), recurse
[then]
+X    1 bit     hasPowerData = 0 if isOwnShip else 1
[if hasPowerData]
+X+1  1 byte    powerPctWanted = ftol(this+0x90 * 100.0)  — 0..100
end             vtable[+0xd8] (GetPos no-op)
```

So per-tick SensorSubsystem payload in StateUpdate flag 0x20 is **1 byte + 1 bit** (own ship) or **1 byte + 1 bit + 1 byte = 2 bytes + 1 bit** (remote ship).

The "extra" hashable float at `prop+0x4C` (BaseSensorRange) DOES NOT travel over StateUpdate — it's the property/config side, not the runtime state side. Clients see the SAME BaseSensorRange because the ship NIF/property data is loaded identically on both ends via ObjCreate. What changes per-tick are the multipliers (HP%, Power%) — and those ARE serialized.

### Tick / Update

SensorSubsystem uses **event-driven scanning**, not per-frame Update. The TGEvent (ET_SENSORS_PERIODIC_SCAN, 0x80008B) is scheduled with a recurring delay. HandlePeriodicScan runs the actual scan tick:

```c
// Pseudocode of FUN_005680C0 (SensorSubsystem::HandlePeriodicScan)
1. Call FUN_00568520 on global SensorSubsystem singleton (0x0098C000) — likely tick of scan iterator
2. Allocate new event of size 0x28 via TGAlloc
3. Call FUN_006D5C00 on event — likely PostEvent for ship-specific scan
4. Allocate another event of size 0x20 via TGAlloc, set event_type=0x80008B
5. Read current gameTime from 0x009A09D0+0x90, add constant 0x008E50F4
6. Schedule re-fire of this handler at (gameTime + delta)
7. Update tracker fields (this[+0xC4] = next event id from event_ptr+4)
8. Add event to EventManager 0x0097F898 (global timer queue) via FUN_006DC3F0
9. FUN_006D90E0 — release temporary event
```

The constant at `0x008E50F4` is the rescan interval. Likely 0.5s or 1.0s game-time.

### Stock behavior — how clients see Sensor state of other ships

1. **HP byte** (via PoweredSubsystem::WriteState — 1 byte): in every StateUpdate that round-robins through Sensor on ship+0x284.
2. **Power% byte** (1 byte): for REMOTE ships, the server sends the sensor's `PowerPercentageWanted` so clients know if the target is sensor-damaged or sensor-powered-off.
3. **Range calculation is CLIENT-SIDE**: each client computes `BaseSensorRange × PowerPct × HpPct` locally from received state. Server doesn't send range directly.
4. **Visibility decisions are CLIENT-LOCAL**: each client's own SensorSubsystem decides what targets are visible based on locally-applied IsObjectVisible. This is why cloaked enemies can be invisible to one player and visible to another at the same instant.
5. **Identified-state**: ET_SENSORS_SHIP_IDENTIFIED is fired client-locally when target enters local sensor range — this is NOT replicated. Each client independently identifies targets.

### Network-state implications for OpenBC

- SensorSubsystem and HullSubsystem MUST be present in the ship+0x284 linked list — the server's StateUpdate round-robin will visit them and emit their HP bytes.
- SensorSubsystem's `BaseSensorRange` (property+0x4C) must match between server and clients — this is baked into the NIF/property files (CT_SENSOR_PROPERTY). Modded ships with different BaseSensorRange WILL desync sensor behavior.
- HullSubsystem HP must mirror ship+0x14C — the encoder reads `instance+0x30 / instance+0x34` for the condition byte. If our OpenBC ship state stores hull HP at `ship.hull_hp` we must mirror it to `hull_subsystem.current_condition` before each StateUpdate.
- Sensor scan events (0x80008B periodic) are CLIENT-LOCAL — server does NOT need to fire these. They're purely UI/AI hints.
- Anti-cheat hash dead in MP (per leaf #19) means the prop+0x4C hash drift is harmless in practice — but mod compatibility still depends on matching BaseSensorRange across hosts/clients.

---

## Hash function inputs — CORRECTED

Re-reading `ComputeSubsystemIntegrityHash` (0x005B5EB0) with corrected slot identities:

| Hash Order | Container Offset | Ship Offset | Subsystem (DEFINITIVE) | Hash Method | Property extras |
|---|---|---|---|---|---|
| 1 | +0x48 | +0x2C4 | **HullSubsystem** (0x8027, vtable 0x00892C98) | HashBaseSubsystem | NONE |
| 2 | +0x44 | +0x2C0 | ShieldGenerator (0x8137) | HashBaseSubsystem + 12 shield floats | 12 floats at prop+0x60..+0x90 |
| 3 | +0x34 | +0x2B0 | **PowerSubsystem (reactor / PoweredMaster)** (0x813E, vtable 0x0088A1F0) | HashBaseSubsystem + 5 prop floats | prop+0x4C, 0x48, 0x54, 0x50, 0x58 |
| 4 | +0x4C | +0x2C8 | **SensorSubsystem** (0x8023, vtable 0x00892EAC) | HashBaseSubsystem + 1 prop float | prop+0x4C (=BaseSensorRange) |
| 5 | +0x50 | +0x2CC | ImpulseEngineSubsystem (0x813C) | HashBaseSubsystem + 4 prop floats | (see FUN_00560FC0) |
| 6 | +0x54 | +0x2D0 | WarpEngineSubsystem (0x813B) | HashBaseSubsystem | NONE |
| 7 | +0x5C | +0x2D8 | RepairSubsystem (0x813F) | HashBaseSubsystem + 1 prop float | (see FUN_00564FE0) |
| 8 | +0x60 | +0x2DC | CloakingSubsystem (0x813A) | HashBaseSubsystem + side effect | (see FUN_0055E220) |
| 9 | +0x38 | +0x2B4 | TorpedoSystem (0x8133) | HashWeaponSystem + torpedo data | weapon-system specific |
| 10 | +0x3C | +0x2B8 | PhaserSystem (0x812F iVar4==1) | HashWeaponSystem | weapon-system specific |
| 11 | +0x40 | +0x2BC | PulseWeaponSystem (0x812F iVar4==3) | HashWeaponSystem | weapon-system specific |
| 12 | +0x58 | +0x2D4 | TractorBeamSystem (0x812F iVar4==4) | HashWeaponSystem | weapon-system specific |

This is the SAME table as the leaf #19 post-cascade table — confirming that the slot 1 cascade was correct in restoring "HullSubsystem 0x8027" (with the type-ID 0x8027 being the HullSubsystem instance class, NOT PowerSubsystem). The labels "PowerSubsystem (Reactor)" applied to slot 1 in BOTH the original AND the cascade-correction were WRONG; both should read "HullSubsystem".

---

## Recommended Ghidra renames (NOT applied this session)

If this campaign moves to applying corrections:

| Address | Current Ghidra Name | Correct Name | Reason |
|---|---|---|---|
| 0x00560470 | PowerSubsystem_Ctor | **HullSubsystem_Ctor** | sets vtable 0x00892C98 (HullSubsystem); used by case 0x8138 (CT_HULL_PROPERTY) |
| 0x00566D10 | CloakingSubsystem_Ctor | **SensorSubsystem_Ctor** | sets vtable 0x00892EAC (SensorSubsystem); used by case 0x8139 (CT_SENSOR_PROPERTY) |
| 0x00567190 | (unnamed) | SensorSubsystem__GetSensorRange | algorithm matches SWIG binding name |
| 0x005671D0 | (unnamed) | SensorSubsystem__IsObjectVisible | matches SWIG SensorSubsystem_IsObjectVisible binding |
| 0x00567080 | (unnamed) | SensorSubsystem__SetProperty | vtable slot +0x60 |
| 0x00567CD0 | (unnamed) | SensorSubsystem__HandleSetPlayer | string at 0x008E51EC binds here via FUN_00566F50 |
| 0x00567F60 | (unnamed) | SensorSubsystem__HandleEnterSet | string at 0x008E51CC |
| 0x00568040 | (unnamed) | SensorSubsystem__HandleShipDecloaked | string at 0x008E515C |
| 0x00568080 | (unnamed) | SensorSubsystem__HandleShipIdentified | string at 0x008E5184 |
| 0x005680C0 | (unnamed) | SensorSubsystem__HandlePeriodicScan | string at 0x008E5130 |
| 0x00566F50 | (unnamed) | SensorSubsystem__RegisterHandlers | calls 6× FUN_006DA130/160 with handler strings |
| 0x00566FD0 | (unnamed) | SensorSubsystem__RegisterEventTypes | registers 0x80000E, 0x80008B event types |

---

## Open questions

1. **What syncs ship+0x14C → HullSubsystem instance+0x30?** Need to find the watcher/observer that mirrors DamageableObject HP into the subsystem's currentCondition. Likely a watcher slot at instance+0x44/+0x48 or a ProcessDamage callout.
2. **What is `_DAT_00888B5C` = 4.0f used for in GetBaseSensorRange (0x005671C0)?** Is this a dead fallback or the actual default for hardcoded fallback case?
3. **What is the `0x008E50F4` rescan interval constant?** Need to read 4 bytes at that address to know if it's 0.5f, 1.0f, etc.
4. **Why DOES HullSubsystem inherit `[+0x84] lastReadStateTime` but never write its own state delta?** ShipSubsystem::ReadState checks `param_3 > this+0x84` before updating — Hull will participate in this gate.
5. **Are there per-Hull "watcher" fields at instance+0x78..+0x84 (the DAT_0098039C[5] block)?** These are inherited from ShipSubsystem and could be sync registrations to ship+0x14C.

## Evidence anchors (v5 confidence high)

| Claim | Address | Evidence |
|---|---|---|
| vtable 0x00892C98 GetTypeID returns 0x8027 | 0x00560490 | byte disasm `B8 27 80 00 00 C3` |
| vtable 0x00892EAC GetTypeID returns 0x8023 | 0x00566D70 | byte disasm `B8 23 80 00 00 C3` |
| Hull class strings live at 0x008E4EC0/EC/EDC | (string table) | search_strings |
| Sensor handler strings 0x008E5130-0x008E51EC | (string table) | search_strings |
| Ship__SetupProperties case 0x8138 → +0x2C4 via HullSubsystem ctor | 0x005B3FB0+~0xBA | decompile shows `case 0x8138: ... PowerSubsystem_Ctor(0)... param_1+0x2C4 = uVar3` |
| Ship__SetupProperties case 0x8139 → +0x2C8 via SensorSubsystem ctor | 0x005B3FB0+~0xBE | decompile shows `case 0x8139: ... CloakingSubsystem_Ctor(0)... param_1+0x2C8 = uVar3` |
| HullSubsystem ctor at 0x00560470 sets vtable 0x00892C98 only | (decompile) | minimal body: parent call + vtable assign |
| SensorSubsystem ctor at 0x00566D10 sets vtable 0x00892EAC + powerMode=2 | (decompile) | calls PoweredSubsystem_Ctor + 9 field zeros + [+0x30]=2 |
| HullSubsystem alloc size 0x88 | 0x005B... case 0x8138 | `PUSH 0x88` before FUN_0040F030 |
| SensorSubsystem alloc size 0xCC | 0x005B428B | `PUSH 0xCC` before FUN_0040F030 |
| GetSensorRange formula = prop+4C * inst+0x98 * inst+0x34 | 0x00567190 | full disasm: FLD [+0x4C] / FMUL [+0x98] / FMUL [+0x34] |
| IsObjectVisible checks target+0x2DC+0xAC (cloak full) | 0x005671D0 | decompile shows the dereference chain |
| HullSubsystem WriteState = ShipSubsystem::WriteState (slot +0x70 inherited) | 0x00892D08 → 0x0056D320 | vtable read + Ghidra-named function |
| SensorSubsystem WriteState = PoweredSubsystem::WriteState (slot +0x70 inherited) | 0x00892F1C → 0x00562960 | vtable read + Ghidra plate comment |
| 6 SensorSubsystem static handlers registered at 0x00566F50 | (decompile) | 6 calls to FUN_006DA130/160 with handler-name strings |

## Confidence

- **HIGH**: slot identities (+0x2C4 = HullSubsystem, +0x2C8 = SensorSubsystem) — byte-level evidence from GetTypeID disasm + class-name string returns + Ship__SetupProperties switch-case decompile
- **HIGH**: vtable slot map for both subsystems (WriteState, IsA, GetTypeID, dtor, GetClassName) — byte-level reads + decompile cross-anchors
- **HIGH**: GetSensorRange formula — byte-level disasm
- **HIGH**: SensorSubsystem event handler binding (6 handlers + 2 event-type registrations)
- **HIGH**: IsObjectVisible cloak-check + visibility list mechanism
- **HIGH**: StateUpdate wire format (Hull = 1 byte; Sensor = 1 byte + 1 bit + optional 1 byte)
- **MEDIUM**: SensorSubsystem field layout +0xAC..+0xC8 — derived from IsObjectVisible/SetProperty disasm, not from ctor zero-init
- **MEDIUM**: Hull HP / DamageableObject sync mechanism — UNRESOLVED (open question #1)
- **LOW**: `_DAT_00888B5C = 4.0f` purpose — fallback may be dead code
