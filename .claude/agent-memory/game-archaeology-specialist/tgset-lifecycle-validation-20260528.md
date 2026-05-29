---
name: tgset-lifecycle-validation
description: Phase-2 reverse engineering of TGSet/SetManager system in stbc.exe — class hierarchy, vtable layout, manager singleton, lifecycle, standard set names, MP impact. Validated 2026-05-28 against STBC.exe Ghidra decompilation + reference/scripts/App.py.
metadata:
  type: project
---

# TGSet / SetManager — exhaustive RE (v5, 2026-05-28)

Builds on [[objnotfound-triad-validation-20260528]] (which covered the 0x1F wire format) and the wire-format-spec/EnterSet entries. This memo documents the **TGSet class system itself** — what a "set" is, who owns it, how it's mutated, what happens at set transitions.

> NOTE: All addresses are from `STBC.exe` (image base 0x00400000, stock 2002 build). The Ghidra MCP currently has SGW.exe as `is_current` — always pass `program: STBC.exe` explicitly.

## 1. TGSet class identity

The TGSet system is a **3-level inheritance chain** of NiObject-derived classes that are *not* registered via the NiRTTI factory at DAT_0099a578. They use the TGObject family's own GetClassID/IsA pattern (vtable slots 1 and 2 are GetClassID and IsA).

### Class catalog

| Class | Class ID | sizeof | vtable | Ctor | Dtor | Python name |
|-------|----------|--------|--------|------|------|-------------|
| **SetClass** (TGSet base) | **0x80d1** | **0x13C** | **0x00888a7c** | FUN_0040d150 | FUN_0040dbd0 (slot 0) → frees 0x13C | `SetClass` |
| **BridgeSet** | **0x80d2** | (≥ 0x13C, adds +0x41/+0x43 bytes, +0x4F/+0x50 ptrs) | **0x00894830** | FUN_00665cc0 | FUN_00665dd0 | `BridgeSet` |
| **WarpSet** (StarBackdrop variant) | **0x80d3** | **0x148** | **0x0088cdf8** | FUN_004d7a00 / FUN_004d7790 (full warp init) | FUN_004d7a30 | `WarpSet` |

### IsA chains (verified via vtable slot 2 == GetTypeID)

- **SetClass (0x80d1)** at 0x0040d980 supports: `0x80d1`, `0x102` (TGEventHandlerObject), `0x4`, `0x3`, `0x2` (TGObject ancestry — slots 4/3/2 form the deep TG base hierarchy)
- **BridgeSet (0x80d2)** at 0x00665d10 supports: `0x80d2`, `0x80d1`, `0x102`, `0x4`, `0x3`, `0x2`
- WarpSet IsA was not separately read but follows same pattern: `0x80d3, 0x80d1, 0x102, 0x4, 0x3, 0x2` (it inherits SetClass, not BridgeSet).

### Class metadata vtable slots (slot 9, 10, 11)

For SetClass:
- slot 9 (offset +0x24) at 0x0040d9c0: returns `s_SetClass_008d8b90` ("SetClass") — **GetTypeName**
- slot 10 (offset +0x28) at 0x0040d9d0: returns `s_p_SetClass_008d8b9c` ("_p_SetClass") — **GetSWIGName**
- slot 11 (offset +0x2C) at 0x0040d9e0: returns `s_SetClassPtr_008d8ba8` ("SetClassPtr") — **GetSWIGPtrName**

These follow the standard TGObject-family triad.

### Class category check (NOT same as NiRTTI factory)

`FUN_00665e00(obj)` is `IsSet(obj)` — calls `obj->vtable[+0x08](0x80d2)` and returns obj if IsA succeeds. Used by FUN_00408790 (current-mission-set retrieval) — so it filters for BridgeSet specifically, NOT base SetClass. The 0x80d2 byte pattern at 0x00901a90 is a stray TGFactory registry entry header (factory ID 0x80d2) but no callers — the binary uses runtime IsA, not the registry.

## 2. SetClass base layout (size 0x13C)

Reconstructed from FUN_0040d150 (ctor) + FUN_0040dbd0 (dtor) + FUN_00414750 (Save) + FUN_00414e90 (Load) + FUN_0040ec90 (EnterSet) + FUN_0040f070 (ExitSet) + FUN_00413cb0 (Update).

| Offset | Field | Type | Purpose |
|--------|-------|------|---------|
| `+0x00` | vtable | ptr | 0x00888a7c (SetClass) / 0x00894830 (BridgeSet) / 0x0088cdf8 (WarpSet) |
| `+0x04` | refCount? | u32 | (TGObject base) |
| `+0x08`-`+0x0B` | TGObject base | bytes | inherited |
| `+0x0C`-`+0x47` | TGEventHandlerObject base | bytes | event handler infra (NameToHandlerMap at +0x20 area) |
| `+0x2C` | flag | byte | "useNewObjectList" — switches +0x30 vs +0x3C as insertion list |
| `+0x30` | objects[] (main) | ptr | array of object refs in this set (sorted by ID via FUN_00431030) |
| `+0x34` | objectCount | int | count of +0x30 |
| `+0x38` | objectCapacity | int | capacity of +0x30 |
| `+0x3C` | newObjects[] | ptr | array of "new this frame" objects (used in transition path) |
| `+0x40` | newObjectCount | int | |
| `+0x44` | newObjectCapacity | int | |
| `+0x48` | cameras[] | ptr | camera array |
| `+0x4C` | cameraCount | int | |
| `+0x54` | lights[] | ptr | light array |
| `+0x58` | lightCount | int | |
| `+0x68` | (4-element float block) | floats | unused/placeholder |
| `+0x74` | **name** | char* | **set name** (e.g. "bridge", "warp") — heap-allocated, set via FUN_0040df80 (TGSet::SetName) |
| `+0x78`-`+0x8C` | misc state | various | flags/bounds |
| `+0x88` | flag | byte | init=1 |
| `+0x8A` | flag | byte | init=1 |
| `+0x8C` | bound | f32 | init=0x3FFFFFFF (~2.0f) |
| `+0x90`-`+0xAB` | camera transforms | floats | |
| `+0xA8` | backdropContainer | ptr (TGSet*) | sub-container for backdrops (+0xD4/+0xD8 = capacity/count) |
| `+0xAC`-`+0xB3` | various ptrs | | |
| `+0xB0` | savedFlag wrapper | ptr | save/load gate flag |
| `+0xDC`-`+0xE7` | vec3 fields | f32 | |
| `+0xE8` | sound? | ptr | |
| `+0xEC` | proximityListenerSet | ptr | ref to neighboring set for proximity events |
| `+0xF0` | enableProximity | byte | |
| `+0xF1` | enableSomething | byte | |
| `+0xF4` | viewBackdropController | ptr | non-null → manages backdrops |
| `+0x100` | backgroundModel | ptr (string) | "BackgroundModel" name (Sound or model resource) |
| `+0x104` | flag | u32 | |
| `+0x108` | flag | u32 | |
| `+0x10D` | isInteresting | byte | set by FUN_00416230 — "this set is currently relevant to player" |
| `+0x110` | backdropPairCount | int | number of (objID, viewBackdrop) pairs |
| `+0x114` | backdropPair[0].objID | int | begins active backdrop ID/ptr pair array |
| `+0x118` | backdropPair[0].viewBackdrop | ptr | |
| `+0x114 + i*8` | backdropPair[i].objID | int | (max 4 pairs per FUN_00413cb0 LRU eviction) |
| `+0x118 + i*8` | backdropPair[i].viewBackdrop | ptr | |
| `+0x13C` | (end of base) | | BridgeSet/WarpSet extend past here |

### BridgeSet extra fields (vtable 0x00894830, ctor FUN_00665cc0)

```c
*(undefined1 *)(this + 0x10C) = 0;   // (this[0x43] is at +0x10C, byte flag)
this[0x41] = 0;                       // (=+0x104, overwrites base flag)
this[0x4F] = 0;                       // (=+0x13C, first extra field)
this[0x50] = 0;                       // (=+0x140, second extra field)
```

So BridgeSet extends sizeof to at least 0x144 (likely 0x148 to stay aligned). The +0x10C byte and +0x104/+0x10C overwrites override base init.

### WarpSet extra fields (vtable 0x0088cdf8, ctor FUN_004d7a00 + heavy init FUN_004d7790)

```c
this[0x3A] = piVar2;     // (= +0xE8, star backdrop sub-object — NiBackdrop, allocated 0xAC bytes via FUN_0058e400)
this[0x4F] = 0;          // (= +0x13C)
this[0x50] = 0;          // (= +0x140)
*(uchar*)(this + 0x51) = 0;  // (= +0x144)
```

Star backdrop config (hard-coded by WarpSet ctor):
- Sub-object name: `"Star Backdrop"` at 0x008e0e88
- Texture path: `"data/stars/stars.tga"` at 0x008e0e78 (called via subobj vtable+0x118)
- Scale 0x100, alpha 1.0, distance 0x43960000 (=300.0f), etc.

WarpSet allocation: `FUN_004d6390` allocs 0x148 bytes via `FUN_00717b70(0x148)` / `FUN_00718010("UNKNOWN", 0)`, then calls FUN_004d7790. **Confirmed sizeof = 0x148.**

## 3. TGSet vtable (0x00888a7c) — 32 entries decoded

| Slot | Byte offset | Address | Method | Notes |
|------|-------------|---------|--------|-------|
| 0  | +0x00 | 0x0040dbd0 | **~TGSet** | scalar dtor; frees 0x13C bytes |
| 1  | +0x04 | 0x0040d970 | **GetClassID** | returns `0x80d1` |
| 2  | +0x08 | 0x0040d980 | **IsA** | 0x80d1, 0x102, 4, 3, 2 |
| 3  | +0x0C | 0x006f1650 | (inherited TGObject) | |
| 4  | +0x10 | 0x00414750 | **Save / WriteToStream** | "Saving set %s\n" |
| 5  | +0x14 | 0x00414e90 | **Load / ReadFromStream** | "Loading set %s\n" |
| 6  | +0x18 | 0x00415b70 | | |
| 7  | +0x1C | 0x00415ba0 | | |
| 8  | +0x20 | 0x006f15c0 | (inherited TGEventHandlerObject) | |
| 9  | +0x24 | 0x0040d9c0 | **GetTypeName** | returns "SetClass" |
| 10 | +0x28 | 0x0040d9d0 | **GetSWIGName** | returns "_p_SetClass" |
| 11 | +0x2C | 0x0040d9e0 | **GetSWIGPtrName** | returns "SetClassPtr" |
| 12 | +0x30 | 0x006f2750 | (TG event dispatch) | |
| 13 | +0x34 | 0x006f2790 | (TG event dispatch) | |
| 14 | +0x38 | 0x006f3400 | (TG event dispatch) | |
| 15 | +0x3C | 0x006f3500 | (TG event dispatch) | |
| 16 | +0x40 | 0x006f26e0 | (TG event dispatch) | |
| 17 | +0x44 | 0x006f2710 | (TG event dispatch) | |
| 18 | +0x48 | 0x006f2730 | (TG event dispatch) | |
| 19 | +0x4C | 0x0040d9f0 | (returns DAT_0097e7c0) | possibly GetEventTable |
| 20 | +0x50 | 0x006d9240 | (inherited base) | |
| 21 | **+0x54** | **0x0040ec90** | **EnterSet** | adds object to this set; posts event 0x0080005c (ship) or 0x0080005d (object) |
| 22 | **+0x58** | **0x0040f070** | **ExitSet** | removes object; posts event 0x0080005e (ship) or 0x0080005f (object) |
| 23 | +0x5C | 0x0040f8c0 | | (DestroyObject from set?) |
| 24 | +0x60 | 0x0040ffb0 | | |
| 25 | +0x64 | 0x004107d0 | | |
| 26 | +0x68 | 0x00410730 | | |
| 27 | **+0x6C** | **0x0040da10** | **CompareName** | strcmp(this+0x74, arg) — used by binary-search FindSetIndexByName |
| 28 | +0x70 | 0x0040da00 | **InsertCompare** | calls inner vtable[+0x6c] — used by AddSet binary insert |
| 29 | +0x74 | 0x00415ad0 | | |
| 30 | +0x78 | 0x00415cd0 | | |
| 31 | +0x7C | 0x00417970 | | |

The vtable extends beyond slot 31 (TGEventHandlerObject infrastructure continues), but these are the slots load-bearing for set lifecycle and protocol.

## 4. TGSetManager singleton

**Singleton address**: **0x0097e9c4** (5-DWORD struct). There is no "manager class" with a vtable — it's a bare global struct.

```c
struct TGSetManager {
  /*+0x00*/ TGSet* currentSet;        // DAT_0097e9c4 — active/rendered set
  /*+0x04*/ TGSet** sets;             // DAT_0097e9c8 — sorted array of TGSet*
  /*+0x08*/ int     setCount;         // DAT_0097e9cc — # of sets
  /*+0x0C*/ int     setCapacity;      // DAT_0097e9d0 — # of slots allocated
  /*+0x10*/ ??       field_10;        // DAT_0097e9d4 — extra (preserved during teardown — possibly "default set")
};
```

**Layout proof**: The block at 0x0065c100 is a "copy from other manager" routine (FUN_005bae00 caller):
```asm
0065c11f  MOV [0x0097e9c4], ECX    ; from input[1]
0065c127  MOV [0x0097e9c8], ECX    ; from input[2]
0065c130  MOV [0x0097e9cc], ECX    ; from input[3]
0065c139  MOV [0x0097e9d0], EDX    ; from input[4]
0065c142  MOV [0x0097e9d4], EAX    ; from input[5] (AX = [EAX+0x14])
```

The teardown at FUN_00408930 zeros `currentSet, sets, setCount, setCapacity` but NOT field_10.

### Manager operations (C++ side)

| Op | Function | Notes |
|----|----------|-------|
| **FindSetIndexByName(name)** | FUN_004055a0 | **Binary search** over sets[], uses vtable+0x6C (CompareName). Returns -1 if not found. Already named in Ghidra DB. |
| **FindSetByName(name)** | inlined: `set = sets[FindSetIndexByName(name)]` | Sometimes wrapped in helpers (e.g. FUN_004d6390 does this then creates if missing). |
| **AddSet(set, name)** | FUN_00417f00 | Inserts `set` into a manager-like struct's sorted array at the right position; resizes capacity if full; if a set with same name already active, calls slot+0x58 (ExitSet) on it first; rebroadcasts via FUN_0070e260(1). Note: this is the **per-object set tracking** AddSet (the one bound to objects, not the singleton — but the singleton's setup uses the same helper via FUN_00417ae0). |
| **RemoveSet(name)** | FUN_004180e0 | Binary search by name, removes from array, dec count. |
| **DeleteSet(name)** | FUN_004182f0 | Like RemoveSet but ALSO **looks up + frees** the set object, then triggers camera mode change ("PlayerCameraAsViewscreen" if removing "bridge", "PlayerCameraAsSpace" otherwise). |
| **ActivateSetByName** | FUN_004182f0 (paired w/ active assignment) | The linear scan at FUN_004182f0 sets `manager+0x04 = found set` after match — this IS MakeRenderedSet. |
| **DeleteAllSets** | (in FUN_00408930) | Iterates `sets[]` calling `vtable[0](1)` (scalar dtor) on each, then FUN_00718cf0 on array ptr, zeroes everything. |
| **GetNumSets** | direct DWORD read of DAT_0097e9cc | inline |
| **GetSet(name) / Python binding** | FUN_004188b0 (`SetManager_GetAllSets`) | Iterates DAT_0097e9c8/0x0c, returns a SWIG tuple. |

### Python API (App.py, lines 3500-3636)

```python
class SetManager:
    def GetSet(name): ...        # find by name
    def AddSet(set, name): ...   # adds and assigns name
    def RemoveSet(set): ...      # remove without deleting
    def DeleteSet(name): ...     # remove + free
    def DeleteAllSets(): ...     # nuke
    def GetNumSets(): ...        # count
    def ClearRenderedSet(): ...
    def MakeRenderedSet(name): ...  # sets manager+0x04 (currentSet) + posts camera mode events
    def GetRenderedSet(): ...
    def Terminate(): ...

g_kSetManager = SetManagerPtr(Appc.globals.g_kSetManager)
```

There's no per-instance state — the SWIG ptr is just a wrapper around the singleton block.

## 5. Set lifecycle

### Creation paths

1. **C++ allocation (warp set lazy create)**: `FUN_004d6390 GetOrCreateWarpSet()`:
   ```c
   if (FindSetByName("warp") == NULL) {
     set = FUN_00717b70(0x148);                 // TGAlloc("UNKNOWN", 0x148) — WarpSet sizeof
     set = FUN_00718010(/*tag*/"UNKNOWN", 0);   // commit alloc
     set = FUN_004d7790(set, 0);                // WarpSet ctor (calls SetClass ctor FUN_0040d150 first)
     FUN_00417f00(set, &DAT_008d8ab8);          // AddSet(set, "warp")
   }
   ```

2. **Python allocation**: Mission scripts call `App.g_kSetManager.AddSet(pSet, "name")` after constructing via `App.BridgeSet()` or `App.WarpSet()` SWIG ctors.

3. **Save-file restoration**: FUN_00444840 (TopLevel load) reads each set from save file and calls TGSet::Load (vtable+0x14 = FUN_00414e90), which deserializes objects, cameras, lights into the set fields.

### Set member add — TGSet::EnterSet (vtable+0x54 / FUN_0040ec90)

```
Input: this (TGSet*), object (TGObject*), [optional placement]
Side effects:
  1. If object already in this->name→object map at +0x80/+0x8C: return 0 (already in set).
  2. Call object->vtable[+0x68](this) — registers set ptr on object side.
  3. Insert object into hash map (this+0x80 = compare fn, this+0x8C = hash buckets) + name list.
  4. If this+0x2C == 0 (use main object list):
       Insert object pointer into sorted array this+0x30..this+0x38 (sorted by object[1] = objectID via FUN_00431030).
     else:
       Insert into "new objects" list this+0x3C..this+0x44 (deferred — picked up later).
  5. Update spatial hash via FUN_0040b220 (calls object->vtable[+0xB8](this)).
  6. Set this+0xF0 = 1 (proximity-enable flag).
  7. Post event:
       if object->IsA(0x8009) == true (Character): event ID 0x0080005C
       else: event ID 0x0080005D (object enter)
     The event is allocated as a 0x28-byte TGEvent via FUN_00717b70(0x28)+FUN_00718010+FUN_006d5c00, target = object, then TGEventManager__PostEvent.
```

The 0x0080005d event carries the entering object as target — Python's `Mission::PlayerEnteredSet` handler (registered via FUN_006da130 at 0x00408720) catches this.

### Set member remove — TGSet::ExitSet (vtable+0x58 / FUN_0040f070)

```
Input: this (TGSet*), objectID
Side effects:
  1. obj = TGSceneGraph__GetObjectByID(0, objectID).
  2. If obj->IsA(0x8009) == true (Character): post event 0x0080005E (character exit) — uses 0x38-byte TGObjPtrEvent at vtable 0x008887ac.
     else: post event 0x0080005F (object exit).
  3. Remove obj from this+0x20 (object->name map) and this+0x80 hash.
  4. Find obj in `cameras[]` (this+0x48) — if matched, release it via vtable+0xA0.
     Find obj in `lights[]` (this+0x54) — if matched, release it.
  5. Call obj->vtable[+0x60](0) — clears obj's setRef.
  6. Set this+0xF0 = 1.
  7. If this+0xF4 != 0: FUN_005A7640(obj) — drops obj from viewBackdrop tracking.
  8. If this+0xB == 1 (alt branch): binary-search remove from this+0xF and this+0xC arrays.
  9. Call this+0x16 array of "set listeners" — invokes vtable+0xD0 on each, passing obj.
```

### Object → Set linkage on the OBJECT side

When an object joins a set:
- `obj->vtable[+0x68](set)` ← sets `*(int*)(obj+0x20) = set` (this is **the ship+0x20 = currentSet field already documented in objnotfound-triad memo** — confirmed for ObjectClass; the offset is inherited).
- The object's `+0x20` slot is the canonical "containing set" pointer.

### Set destruction

`FUN_00408930` (cleanup all sets) iterates `DAT_0097e9c8` from the back, calling `vtable[0](1)` (scalar destructor with deleting flag) on each. After all are freed, it re-installs the saved "bridge" and "warp" sets (if they were captured before teardown) — so those two persist across mission boundaries.

The dtor FUN_0040dbd0 calls FUN_00717b20(0x13c) + FUN_00718180 — TGFree(this, 0x13c) confirming **base TGSet size = 316 bytes**. WarpSet/BridgeSet dtors call ~SetClass first then their own slot[0] frees their extended size.

## 6. Standard set name catalog

| Name | String addr | Subclass | Notes |
|------|-------------|----------|-------|
| `"bridge"` | `s_bridge_008d866c` (0x008d866c, len 6) | **BridgeSet (0x80d2)** | Captain's bridge scene. Has named characters: Helm, Tactical, XO, Science, Engineer, Picard, Data, Saalek, Korbus. Persisted across mission teardowns. Triggers `PlayerCameraAsViewscreen` mode on activation. |
| `"warp"` | `&DAT_008d8ab8` (0x008d8ab8, len 4) | **WarpSet (0x80d3)** | The in-space / between-systems scene. Carries the StarBackdrop (NiBackdrop loading "data/stars/stars.tga"). Persisted across teardowns. Triggers `PlayerCameraAsSpace` mode. |
| `"space"` | (referenced in BridgeHandlers.py) | (alias usage) | Python uses "space" in some places interchangeably with "warp" — may be local synonym; not present in C++ literal string table — could be a per-mission rename via SetName. |
| `"Engineering"` | (BridgeHandlers.py line 827) | **BridgeSet** | Per-mission engineering sub-scene with Engineer character. Mission-script created via `App.g_kSetManager.AddSet`. |
| `"Star Backdrop"` | `s_Star_Backdrop_008e0e88` | — | NOT a SetManager entry; it's the **object name** inside WarpSet's backdrop sub-object. |
| Mission-specific (e.g. asteroid fields) | Mission .py files | SetClass base | Created at mission init via Python's `App.g_kSetManager.AddSet`. AsteroidField sets register listeners for events 0x0080005d/0x0080005f/0x00800062. |

**Note on "Multi1"/"Multi2"**: The orchestrator's pre-anchored context mentioned these names. I searched and **did not find** any string `"Multi1"`/`"Multi2"` in the binary as a set name. The "Multi*" naming is from Multiplayer maps in Multiplayer/MultiplayerMenus.py mission selection, NOT TGSet names. **Set names in MP appear to be just "bridge" (when on the ship) and "warp" (when in space)**, with mission scripts creating ad-hoc sub-sets if needed.

The EnterSet wire packet (opcode 0x1F) carries an arbitrary set name as a uint32-prefixed string — any mission script can name its sets anything. The hard-coded common names are "bridge" and "warp".

## 7. Object→Set mapping field

**Confirmed**: `obj+0x20` is the "currentSet" pointer on every object that derives from a base TGObject-with-Set-awareness (Ship, Character, Camera, Backdrop, etc.).

Validation chain:
- **EnterSet handler (multiplayer 0x1F)** at FUN_006a05e0: reads `*(int**)(ship+0x20)` as currentSet.
- **Game_GetCurrentSet** at FUN_004069c0: returns `mission+0x20` (the play window's mission has its own currentSet ptr — actually that's `*(playWindow+0x54)+0x20`; mission and ship share the offset by convention).
- **Mission player exited handler** at FUN_00409170: reads `DAT_0097e9c4+0x74` (current set name) and compares — confirms manager+0x00 = active set ptr.

In EnterSet (FUN_0040ec90), `object->vtable[+0x68](this)` is called — that's the slot that writes `*(int*)(obj+0x20) = this`. Confirmed via decompile: `(**(code **)(*piVar2 + 0x68))(s_Star_Backdrop_008e0e88)` in WarpSet ctor uses the same slot for naming, but for set membership the actual offset writer is `vtable+0x60` (called by ExitSet to clear: `(**(code **)(*piVar9 + 0x60))(0)` — passing 0 clears the back-pointer).

So:
- `vtable+0x60` = **SetContainingSet(set)** — writes obj+0x20
- `vtable+0x68` = different — sets the object's name

## 8. Multiplayer state replication impact

### Direct: opcode 0x1F EnterSet (already documented)

The host sends opcode 0x1F when a player ship's currentSet changes from a NAMED set to another NAMED set (e.g. exiting "warp" tunnel into a system, or going to "bridge" for a cutscene). Client receives, looks up the destination set in its own TGSetManager (which must have the same name registered), and applies vtable+0x54 (EnterSet).

**Critical**: This DOES NOT replicate the set definition — both sides must already have the set with the same name. The packet contains `[u32 objectID][u32 nameLen][bytes name]`. If the client doesn't have a matching set name, it sends back opcode 0x1E (ObjNotFound).

### Indirect: object+0x20 in StateUpdate

Object's `+0x20` (currentSet ptr) is NOT serialized in StateUpdate (opcode 0x1C). StateUpdate transmits dirty-flagged fields per ship at +0x100+ — none of the documented dirty bits target +0x20. So set membership is ONLY communicated via:
1. Explicit opcode 0x1F EnterSet events (warp transitions)
2. Implicit: ObjCreate (opcode 0x02/0x03) puts the new object in the default/active set on each side — clients add the object to *their* currentSet, host adds to its active set
3. Set transition events fire as PythonEvent (opcode 0x06) — Mission::PlayerEnteredSet / PlayerExitedSet — if the Python handler decides to send anything wire-side, that goes through normal PythonEvent transport

### Set "roster" tracking

There IS a per-set roster — the `+0x30/+0x34/+0x38` sorted object array. But this is local-side only. The host's roster and a client's roster can drift; they're reconciled at object creation (each ObjCreate places the object in the current set on the receiver's side) and at set transitions (0x1F).

### No "containing set" sync on every state update

This is a major implication: **set membership is NOT continuously verified across the wire**. If host moves a ship to a different set without sending 0x1F, the client's copy will be in the wrong set forever (until next ObjCreate / re-checksum). In practice, ships rarely change sets mid-mission outside of warp transitions, so this is invisible.

### EnterSet handler validation gates (host-side, in receiver at 0x006a05e0)

The handler doesn't trust the wire blindly:
1. Object must exist via TGSceneGraph__GetObjectByID — otherwise reply with 0x1E (ObjNotFound).
2. Object must IsA(0x8008) — Ship — otherwise silently drop (no error reply).
3. Ship must have a warp engine subsystem (`ship+0x2D0 != 0`).
4. Warp engine must not already be in transit (`*(ship+0x2D0)+0xB4 == 0`).
5. Set name must resolve in local SetManager (otherwise silent drop).

This means a client cannot trigger EnterSet for a ship that has no warp engine — useful constraint for headless server because non-ship objects (subsystems, weapons) cannot have phantom set transitions injected.

## 9. Camera / rendering side notes (brief — out of scope for headless)

- `MakeRenderedSet(name)` in C++ ≈ FUN_004182f0 finds the set, assigns `manager+0x04 = set`, then posts camera mode events.
- The rendered set drives the renderer's scene root via the `viewBackdropController` at `+0xF4`. It's iterated in FUN_00413cb0 — every game-loop frame the renderer queries this set for up-to-4 nearest viewable objects (LRU-evicted; max 4 backdrop pairs at +0x114/+0x118).
- For a headless server: setting `currentSet = NULL` would break a lot of code; the bootstrap should ensure the "warp" set exists. Lazy-create logic in FUN_004d6390 ensures this.

## 10. Cross-doc updates

- **objnotfound-triad** memo: ship+0x20 = currentSet confirmed. The EnterSet handler at 0x006a05e0 was already byte-confirmed; this memo extends with vtable slot details.
- **wire-format-spec** doc: opcode 0x1F section can reference TGSet 0x80d1/0x80d2/0x80d3 IDs.
- **engine/rtti-class-catalog**: add 3 entries — SetClass (0x80d1), BridgeSet (0x80d2), WarpSet (0x80d3) with their vtables. These were NOT in the existing 670-class catalog because they don't use NiRTTI factory.
- **engine/netimmerse-vtables**: add SetClass vtable 0x00888a7c.

## 11. Open questions / low-confidence items

1. **Slot 6 and 7** of the vtable (0x00415b70, 0x00415ba0) — likely "Update" / "Render" — not decoded here.
2. **Slot 23-26** (0x0040f8c0, 0x0040ffb0, 0x004107d0, 0x00410730) — set-level operations (probably AddCamera/RemoveCamera/AddLight/RemoveLight) — not decoded.
3. **+0x20 vs vtable+0x60 alignment**: I claimed obj+0x20 = currentSet based on the EnterSet handler reading `*(ship+0x20)` and FUN_004069c0 returning `game+0x20`. The actual writer is `obj->vtable[+0x60](set)` per ExitSet (which clears it with `(0)`). Need spot-check on the slot+0x60 of e.g. Ship vtable to confirm it writes +0x20 specifically. **Confidence: HIGH (EnterSet/ExitSet both reference it, FUN_004069c0 confirms via game ptr) but the actual writer fn not decompiled.**
4. **field_10 (DAT_0097e9d4)**: Saved across teardowns. Possibly "default fallback set" or an Episode reference. Not load-bearing.
5. **The 0x102 ancestor**: I claim this is TGEventHandlerObject based on Python's `class SetClass(TGEventHandlerObject):`. The C++ class IDs are 0x80d1 (SetClass) and 0x102 (parent) — 0x102 NOT confirmed via direct decompile but follows the App.py inheritance chain.

## 12. Function-name annotations applied to Ghidra

Did NOT apply rename per v5 policy (only orchestrator applies annotations during a campaign run). Candidates for future renaming:

| Address | Suggested name |
|---------|----------------|
| FUN_0040d150 | TGSet__Ctor |
| FUN_0040dbd0 | TGSet__ScalarDtor |
| FUN_0040dc00 | TGSet__Dtor |
| FUN_0040df80 | TGSet__SetName |
| FUN_0040ec90 | TGSet__EnterSet |
| FUN_0040f070 | TGSet__ExitSet |
| FUN_0040da10 | TGSet__CompareName |
| FUN_00414750 | TGSet__Save |
| FUN_00414e90 | TGSet__Load |
| FUN_00413cb0 | TGSet__UpdateBackdrops |
| FUN_00408c00 | TGSet__ProcessRemovedObjects |
| FUN_004055a0 | TGSetManager__FindSetIndexByName (already named) |
| FUN_00417f00 | TGSetManager__InsertObjectInSet (per-obj set tracking) |
| FUN_004182f0 | TGSetManager__MakeRenderedSet |
| FUN_00408930 | TGSetManager__Shutdown |
| FUN_004188b0 | TGSetManager_GetAllSets (SWIG) |
| FUN_00665cc0 | BridgeSet__Ctor |
| FUN_00665dd0 | BridgeSet__Dtor |
| FUN_004d7a00 | WarpSet__Ctor |
| FUN_004d7790 | WarpSet__FullInit |
| FUN_004d6390 | GetOrCreateWarpSet |
| FUN_00665e00 | IsBridgeSet (IsA 0x80d2) |

## 13. Verification status

- [v5-validated]: Class IDs 0x80d1/0x80d2/0x80d3 — direct vtable slot decode
- [v5-validated]: TGSet sizeof = 0x13C — dtor FUN_00717b20(0x13c) + xref to FUN_00718180
- [v5-validated]: WarpSet sizeof = 0x148 — alloc at FUN_004d6390 via FUN_00717b70(0x148)
- [v5-validated]: TGSet vtable @ 0x00888a7c — from ctor FUN_0040d150 line `*param_1 = &PTR_FUN_00888a7c`
- [v5-validated]: Manager singleton layout — disasm of 0x0065c100..0x0065c149 + teardown FUN_00408930
- [v5-validated]: name field at +0x74 — Save fn FUN_00414750 line 1: `*(param_1 + 0x74)` as "Saving set %s" arg
- [v5-validated]: EnterSet event 0x0080005d / ExitSet event 0x0080005f — direct decompile of FUN_0040ec90 and FUN_0040f070 paired with FUN_00408720 (Mission::PlayerEnteredSet/PlayerExitedSet event reg)
- [v5-validated]: Set names "bridge" + "warp" + their hard-coded offsets — string xref + Python App.py confirmation
- [v5-validated]: object+0x20 = currentSet — multi-source: EnterSet handler 0x006a05e0, Game getter FUN_004069c0
- [partial]: vtable slot mapping past slot 21/22 — slots 23-31 decoded as offsets but not as method names
- [partial]: BridgeSet extra fields — ctor sets 4 fields, but their semantics inferred not decompiled
- [low]: 0x80d2 TGFactory entry at DAT_00901a90 — present but unreferenced; possibly dead

## 14. Cross-reference targets

- `docs/engine/netimmerse-vtables.md` — add SetClass vtable (0x00888a7c) + BridgeSet (0x00894830) + WarpSet (0x0088cdf8)
- `docs/engine/rtti-class-catalog.md` — add 3 SetClass-family class IDs
- `docs/protocol/objnotfound-requestobj-enterset-wire-format.md` — confirm/cross-link the vtable slot details and currentSet offset confirmation
- `docs/architecture/dedicated-server.md` — note that bootstrap should ensure "warp" set exists (lazy-create via FUN_004d6390 caller)

Linked memos: [[objnotfound-triad-validation-20260528]], [[wire-format-spec-validation-20260528]], [[netimmerse-vtables-validation-20260528]], [[tg-hierarchy-vtables-validation-20260528]].
