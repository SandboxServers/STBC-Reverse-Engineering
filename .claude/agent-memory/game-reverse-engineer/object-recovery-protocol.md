# Object Recovery Protocol: Opcodes 0x1D / 0x1E / 0x1F

## Opcode Names (Python API constants)
- 0x1D: ObjNotFound (no Python constant exported)
- 0x1E: RequestObj = App.SEND_OBJECT_MESSAGE
- 0x1F: EnterSet = App.VERIFY_ENTER_SET_MESSAGE

## Function Addresses
| Address    | Function                                       |
|------------|------------------------------------------------|
| 0x006a0490 | MultiplayerGame__ObjNotFoundHandler (0x1D)     |
| 0x006a02a0 | MultiplayerGame__RequestObjHandler (0x1E)      |
| 0x006a05e0 | MultiplayerGame__EnterSetHandler (0x1F)        |
| 0x006a07d0 | MultiplayerGame__RequestObjEventHandler (sender)|
| 0x006a0a20 | MultiplayerGame__EnterSetEventHandler (STUB, empty)|

## Wire Formats

### 0x1D ObjNotFound (Client→Host, 5 bytes)
```
[0x1D][int32: objectID]
```
Client sends when it gets a message referencing an unknown object ID.
Handler: if object also missing locally → sends 0x1E to host(connID=0).
If found locally → silent (should not happen unless race condition).

### 0x1E RequestObj (Client→Host, 5 bytes; response = ObjCreate 0x02/0x03)
```
[0x1E][int32: objectID]
```
Host responds with ObjCreate (0x02 non-player, 0x03 player ship) sent unicast to requester.
Gates: object must be networked (+0x3b!=0), alive, HP > threshold (DAT_008e5c18).
After ObjCreate, host also replays pending explosion events (0x29) for that object.
Response is NOT wrapped in 0x1E — it IS a standard 0x02/0x03 ObjCreate.

### 0x1F EnterSet (Client→Host, 6+N bytes)
```
[0x1F][int32: objectID][cstr: setName\0]
```
String is NULL-TERMINATED (not length-prefixed — common trap).
Client sends when its ship begins warp and destination is NOT the default space set.
Host validates warp state, moves ship between TGSet objects.
If object not found → host sends 0x1E to itself (connID 0).

## Sender Logic (RequestObjEventHandler @ 0x006a07d0)
Triggered when local ship changes set. Branches on warp state:
- NOT in warp → sends 0x1D to "NoMe" group (unexpected set change = recovery)
- IN warp AND dest != default space set → sends 0x1F to "NoMe" group
- IN warp AND dest == default space set → nothing sent

## Set Names
The "default space combat set" string is at 0x008d8ab8 (immediately after "DeleteAllMissionTimers\0").
Named sub-sets (Multi1-Multi7, Albirea, Poseidon) from SpeciesToSystem.py.
Standard FFA multiplayer: all ships in default set, 0x1F never fires.

## Key Gate Values
- DAT_008e5c18 = minimum HP threshold for RequestObj response (~small positive float)
- ship[0x3b] = "networked" flag (must be non-zero for RequestObj to respond)
- ship[0xb4] = WarpEngineSubsystem pointer (NULL check in EnterSet handler)
- *(ship[0xb4]+0xb4) = warp in-transit flag (must be 0 for EnterSet to proceed)

## TGSet Vtable Calls in EnterSetHandler
- vtable[0x58/4] = ExitSet(objectID) — called on CURRENT set, param is ship's ObjID
- vtable[0x54/4] = EnterSet(ship*, placement) — called on DEST set

## OpenBC Implementation Note
- 0x1D and 0x1E: both result in same host response (ObjCreate unicast to requester)
- EnterSet string: NULL-terminated cstr, NOT u16-length-prefixed (OpenBC spec had this wrong, corrected 2026-02-24)
- EnterSet direction: Client→Host ONLY, not Server→Clients (old OpenBC spec was wrong)
