# Ghidra Jython Script: Annotate Game Globals, Key Functions, and Data Labels
# @category STBC
# @description Labels critical game globals, key functions identified through
#   reverse engineering, SWIG type info entries, and Python module tables.
#   Complements the SWIG, NiRTTI, and vtable annotation scripts.
#
# Run from Ghidra Script Manager with stbc.exe loaded.

from ghidra.program.model.symbol import SourceType
from ghidra.program.model.listing import CodeUnit

# ============================================================================
# UtopiaModule globals (game state flags and pointers)
# ============================================================================
UTOPIA_GLOBALS = {
    0x0097FA00: ("g_UtopiaModule", "UtopiaModule base pointer"),
    0x0097FA78: ("g_TGWinsockNetwork", "TGWinsockNetwork* (UtopiaModule+0x78)"),
    0x0097FA7C: ("g_GameSpy", "GameSpy pointer (+0xDC=qr_t for LAN discovery)"),
    0x0097FA80: ("g_NetFile", "NetFile/ChecksumManager pointer"),
    0x0097FA88: ("g_IsClient", "BYTE: 0=host, 1=client"),
    0x0097FA89: ("g_IsHost", "BYTE: 1=host, 0=client"),
    0x0097FA8A: ("g_IsMultiplayer", "BYTE: 1=multiplayer active"),
    0x008e5f59: ("g_SettingsByte1", "Settings packet byte 1 (sent in opcode 0x00)"),
    0x0097faa2: ("g_SettingsByte2", "Settings packet byte 2 (sent in opcode 0x00)"),
    0x0097e238: ("g_TopWindow", "TopWindow/MultiplayerGame pointer"),
    0x009a09d0: ("g_Clock", "Clock object (+0x90=gameTime, +0x54=frameTime)"),
    0x009a2b98: ("g_NiRTTI_FactoryHashTable", "NiRTTI factory hash table (37 buckets)"),
    0x00980798: ("g_ModelRegistry", "Ship model name -> NiNode registry (for +0x140)"),
    # Event system globals
    0x0097f838: ("g_TGEventManager", "TGEventManager singleton (queues + handler tables)"),
    0x009983a4: ("g_pTGEventObjectTable", "Global TGEvent tracking hash table (objID -> event)"),
    0x009983a8: ("g_pTGEventHandlerTable", "Global event handler table (event type -> handler chain)"),
    0x00998638: ("g_TGHandlerNameTable", "Handler name registry (hash -> function name string)"),
    0x0095adfc: ("g_pTGEvent_NullTarget", "Event null-target sentinel (default dest)"),
    0x0095adf8: ("g_pTGEvent_BroadcastMarker", "Event broadcast marker sentinel"),
}

# ============================================================================
# Key functions (reverse-engineered, from MEMORY.md and agent analysis)
# ============================================================================
KEY_FUNCTIONS = {
    # --- TGPeerArray (2) ---
    0x00401830: ("TGPeerArray__FindByID", "TGPeerArray method: FindByID"),
    0x00401cc0: ("TGPeerArray__FindIndexByID", "TGPeerArray method: FindIndexByID"),

    # --- TGObjPtrEvent (1) ---
    0x00403290: ("TGObjPtrEvent__ctor", "TGObjPtrEvent constructor (factory 0x10C, +0x28=int32 ObjID)"),

    # --- Episode (6) ---
    0x004040a0: ("Episode__ctor", "Episode method: ctor"),
    0x004041a0: ("Episode__scalar_deleting_dtor", "Episode method: scalar_deleting_dtor"),
    0x00404390: ("Episode__LoadMission", "Episode method: LoadMission"),
    0x00404730: ("Episode__LoadMissionHandler", "Episode method: LoadMissionHandler"),
    0x00404760: ("Episode__ReportGoalInfoHandler", "Episode method: ReportGoalInfoHandler"),
    0x00404800: ("Episode__RegisterGoal", "Episode method: RegisterGoal"),

    # --- TGSetManager (1) ---
    0x004055a0: ("TGSetManager__FindSetByName", "TGSetManager method: FindSetByName"),

    # --- PlayWindow (10) ---
    0x00405ad0: ("PlayWindow__InitFields", "PlayWindow method: InitFields"),
    0x00405b10: ("PlayWindow__ctor_stream", "PlayWindow method: ctor_stream"),
    0x00405be0: ("PlayWindow__scalar_deleting_dtor", "PlayWindow method: scalar_deleting_dtor"),
    0x00405c10: ("PlayWindow__ctor", "PlayWindow method: ctor"),
    0x00405ec0: ("PlayWindow__dtor", "PlayWindow method: dtor"),
    0x00406040: ("PlayWindow__GameStarted", "PlayWindow method: GameStarted"),
    0x004fc480: ("PlayWindow__ctor", "PlayWindow method: ctor"),
    0x004fc610: ("PlayWindow__LoadMission", "PlayWindow method: LoadMission"),
    0x004fcae0: ("PlayWindow__SetMissionPath", "PlayWindow method: SetMissionPath"),
    0x005143f0: ("PlayWindow__OnFadeComplete", "PlayWindow method: OnFadeComplete"),

    # --- Game (8) ---
    0x004060c0: ("Game__LoadMissionWithMovie", "Game method: LoadMissionWithMovie"),
    0x00406460: ("Game__LoadEpisode", "Game method: LoadEpisode"),
    0x00406620: ("Game__SetPreLoadDoneEvent", "Game method: SetPreLoadDoneEvent"),
    0x004066d0: ("Game__SetPlayer", "Game method: SetPlayer"),
    0x00406a90: ("Game__ReallyTerminate", "Game method: ReallyTerminate"),
    0x00443ac0: ("Game__SaveToFile", "Save game state to file (campaign save system)"),
    0x00444840: ("Game__LoadSaveFile", "Game method: LoadSaveFile"),
    0x00446360: ("Game__SetupSoundFiles", "Game method: SetupSoundFiles"),

    # --- MissionBase (5) ---
    0x004061d0: ("MissionBase__OnIdle", "MissionBase method: OnIdle"),
    0x00409d20: ("MissionBase__ctor", "MissionBase method: ctor"),
    0x00409e90: ("MissionBase__ctor_stream", "MissionBase method: ctor_stream"),
    0x00409ed0: ("MissionBase__dtor", "MissionBase method: dtor"),
    0x0040a110: ("MissionBase__CallPythonHandler", "MissionBase method: CallPythonHandler"),

    # --- _Global (101) ---
    0x004069b0: ("GetPlayerShip", "Returns current player's ship object pointer"),
    0x00434cd0: ("GetForwardDirection", "Returns global forward direction vector from DAT_00980df0"),
    0x004360c0: ("GetBoundingBox", "vtable+0xE4, computes AABB from NiBound"),
    0x00445fc0: ("UtopiaModule_CreateGameSpy", "Create GameSpy object (from Appc SWIG)"),
    0x00446010: ("UtopiaModule_TerminateGameSpy", "Destroy GameSpy object (from Appc SWIG)"),
    0x004570d0: ("RaySphereIntersect", "Auto-named: RaySphereIntersect"),
    0x00504890: ("MultiplayerWindow_StartGameHandler", "ET_START handler"),
    0x00504c10: ("MultiplayerWindow_ReceiveMessage", "UI-level dispatcher (0x00, 0x01, 0x16)"),
    0x00504c70: ("Handler_UICollisionSetting_0x16", "Collision toggle (MultiplayerWindow)"),
    0x00504f10: ("CreateMultiplayerGame", "Creates MultiplayerGame object"),
    0x0050d070: ("TopWindow_SelfDestructHandler", "Self-destruct: 3 paths (SP/host/client)"),
    0x0055e2b0: ("CloakingSubsystem_ctor", "Cloaking device constructor (powerMode=2, backup-only)"),
    0x005636d0: ("PoweredMaster_SetupFromProperty", "Init EPS: fill batteries to max from property"),
    0x005644b0: ("PowerSubsystem_WriteState", "Reactor: serialize condition + battery levels"),
    0x00564530: ("PowerSubsystem_ReadState", "Reactor: deserialize condition + battery levels"),
    0x00566d10: ("SensorSubsystem_ctor", "Sensor array subsystem constructor"),
    0x0056a230: ("ShieldClass_Update", "Shield recharge tick (power-gated)"),
    0x0056fdf0: ("EnergyWeapon_GetChargePercentage", "Phaser charge level (gates on subsystem alive)"),
    0x00584e40: ("WeaponSystem_PerWeaponFireAttempt", "Per-weapon fire attempt in UpdateWeapons"),
    0x00591b60: ("Ship_SetModelName", "Sets ship model; vtable[0x128]. Sets +0x140 damage target NiNode"),
    0x00593650: ("DoDamage_FromPosition", "Position-based damage (explosions, area effect)"),
    0x00593e50: ("ProcessDamage", "Distributes damage to subsystems via ship+0x128/+0x130 array"),
    0x00594020: ("DoDamage", "Central damage dispatcher. Gates: ship+0x18 AND ship+0x140"),
    0x005952d0: ("DoDamage_CollisionContacts", "Collision contact damage"),
    0x005a1f50: ("Ship_Deserialize", "Ship deserialization wrapper (called by ObjCreate handler)"),
    0x005b0060: ("CollisionDamageWrapper", "Collision -> damage conversion"),
    0x005b0e80: ("Ship_InitObject", "Ship deserialization from network stream"),
    0x005b17f0: ("Ship_WriteStateUpdate", "Serializes ship state (pos/orient/subsys/weapons) to stream"),
    0x005b3fb0: ("Ship_SetupProperties", "Creates subsystems from NiNode properties"),
    0x005bae00: ("SWIG_GetPointerObj", "Unwrap SWIG pointer to raw C++ pointer"),
    0x005bb040: ("SWIG_MakePtr", "Format SWIG pointer string"),
    0x005bb0e0: ("SWIG_NewPointerObj", "Wrap raw C++ pointer as SWIG pointer"),

    # --- Phase 8A: Multiplayer handler callees (NI engine utilities) ---
    0x00423480: ("NiPoint3__Copy", "Copy 3 floats (12 bytes) from source NiPoint3"),
    0x004166d0: ("WString__Clear", "Clear/reset wide string buffer (refcount release)"),
    0x00416bc0: ("WString__AssignSubstring", "Assign substring from another WString (offset+length)"),
    0x00459cb0: ("NiMatrix3__TransformPoint", "Matrix3x3 * Vector3 rotation transform"),

    # --- Phase 8A: TGDisplayTextAction (floating text for join/leave) ---
    0x0055c690: ("TGDisplayTextAction__ctor_tgl", "Floating text action ctor (from TGL file entry)"),
    0x0055c790: ("TGDisplayTextAction__ctor_string", "Floating text action ctor (from C string)"),

    0x0065a250: ("initAppc", "Initialize Appc Python module (SWIG bindings)"),
    0x0069c440: ("GameSpy_Tick", "GameSpy per-frame update (process queries, heartbeats)"),
    0x0069f2a0: ("MultiplayerGame_ReceiveMessage", "Main game opcode dispatcher (0x00-0x2A, jump table at 0x0069F534)"),
    0x0069f620: ("Handler_ObjCreate_0x02_0x03", "Object creation / ObjCreateTeam"),
    0x0069f880: ("Handler_PythonEvent2_0x06_0x0D", "Python event: create TGEvent from stream, post to event manager"),
    0x0069f930: ("Handler_TorpedoFire_0x19", "Auto-named: Handler_TorpedoFire_0x19"),
    0x0069f9e0: ("Handler_Settings_0x00", "Settings packet handler (gameTime, map, collision)"),
    0x0069fbb0: ("Handler_BeamFire_0x1A", "Auto-named: Handler_BeamFire_0x1A"),
    0x0069fc00: ("Handler_GameInit_0x01", "Game start trigger"),
    0x0069fda0: ("Handler_GenericEventForward", "Shared event forward for opcodes 0x07-0x12, 0x1B (weapons, cloak, repair, etc.)"),
    0x0069fe60: ("Handler_TorpedoFire_0x19", "Torpedo launch"),
    0x0069ff50: ("Handler_StateUpdate_0x1C", "Ship state replication (pos/orient/subsys/weapons)"),
    0x006a0080: ("Handler_Explosion_0x29", "Explosion damage (S->C)"),
    0x006a01e0: ("Handler_DestroyObject_0x14", "Object destruction (S->C)"),
    0x006a0340: ("Handler_BeamFire_0x1A", "Beam weapon hit"),
    0x006a0620: ("Handler_ObjNotFound_0x1D", "Object lookup failure"),
    0x006a07d0: ("Handler_RequestObj_0x1E", "Request object data from host"),
    0x006a0a20: ("Handler_EnterSet_0x1F", "Enter game set"),
    0x006a0ca0: ("DeletePlayerHandler", "ET_NETWORK_DELETE_PLAYER: sends 0x17+0x14+0x18 to remaining"),
    0x006a1aa0: ("GetShipFromPlayerID", "__cdecl(int connID) -> ship*, maps connection to ship object"),
    0x006a1b10: ("ChecksumCompleteHandler", "Server: sends Settings + GameInit after checksums pass"),
    0x006a1e70: ("Handler_NewPlayerInGame_0x2A", "Player join handshake"),
    0x006a2470: ("Handler_CollisionEffect_0x15", "Collision damage relay"),
    0x006a3cd0: ("NetFile_ReceiveMessage", "Checksum/file opcode dispatcher (0x20-0x27)"),
    0x006a4250: ("Handler_FileTransferACK_0x27", "File transfer acknowledgment (C->S)"),
    0x006aa720: ("SL_CreateBroadcastSocket", "Create UDP broadcast socket for LAN discovery"),
    0x006ab620: ("GameSpy_StartSearch", "Initiate server search (LAN or internet)"),
    0x006abd80: ("qr_heartbeat_tick", "Periodic heartbeat check and send"),
    0x006abe00: ("qr_send_exit", "Send exiting heartbeat to master server"),
    0x006abe40: ("qr_shutdown", "GameSpy shutdown: exit heartbeat + cleanup"),
    0x006ac550: ("qr_send_packet", "Send GameSpy response packet via UDP"),
    0x006ac5f0: ("qr_callback_basic", "GameSpy basic query: hostname, map, player count"),
    0x006b52b0: ("WSN_DequeueCompletedMessages", "Dequeue completed msgs (reliable ordering, fragment reassembly)"),
    0x006b55b0: ("SendStateUpdates", "Main state replication loop (iterates peer array)"),
    0x006b84d0: ("BufferCopy", "Alloc + memcpy for network buffers"),
    0x006b95f0: ("WSN_ReceivePacket", "recvfrom + AlbyRules decrypt bytes 1+"),
    0x006b9f40: ("RemovePeerAddress", "Removes peer from WSN (patched for NULL safety)"),
    0x006bfe80: ("TGMessageEvent_ctor", "Construct TGMessageEvent (size 0x2C, type 0x60001)"),
    0x006c9520: ("AddToSet", "Links NiProperties to NiNode in game set"),
    0x006d03d0: ("TGLManager_LoadFile", "__thiscall on 0x997fd8; fopen + parse"),
    0x006d11d0: ("TGLManager_LoadOrCache", "Allocates + parses TGL; returns NULL on failure"),
    0x006d1e10: ("TGLFile_FindEntry", "Returns TGL entry ptr (patched: NULL check on ECX)"),
    0x006d2e50: ("WriteCompressedVector3", "Auto-named: WriteCompressedVector3"),
    0x006d2eb0: ("ReadCompressedVector3", "Reads 3-component compressed vector (patched: vtable validate)"),
    0x006d2f10: ("WriteCompressedVector4", "Auto-named: WriteCompressedVector4"),
    0x006d2fd0: ("ReadCompressedVector4", "Reads 4-component compressed vector (patched: vtable validate)"),
    0x006d3070: ("WriteCompressedVector4_Byte", "Auto-named: WriteCompressedVector4_Byte"),
    0x006d3a90: ("CF16_Encode", "Compress float to 16-bit: sign + 4-bit exponent + 11-bit mantissa"),
    0x006d3b30: ("CF16_Decode", "Decompress 16-bit CF16 to float"),
    0x006f3f30: ("ChecksumMatchDataWriter", "Appends checksum data to stream"),
    0x006f7d90: ("TG_ImportModule", "__import__ + sys.modules lookup"),
    0x006f7fc0: ("TG_ReloadPythonModule", "Auto-named: TG_ReloadPythonModule"),
    0x006f8ab0: ("TG_CallPythonFunction", "Calls Python function by module.name path"),
    0x006f8bd0: ("TG_CallPythonFunctionSimple", "Wrapper: CallPythonFunctionEx with no-safe, no-decref"),
    0x006f8c00: ("TG_CallPythonFunctionEx", "Call Python function with safe-call + decref control"),
    0x006f8cf0: ("TG_CallPythonMethod", "Call method on Python object (getattr + call)"),
    0x00717840: ("NiAlloc", "malloc with 4-byte size header, pool for <=0x80"),
    0x00717960: ("NiFree", "Free NiAlloc'd memory"),
    0x007179c0: ("NiRealloc", "Realloc NiAlloc'd memory"),
    0x00718cf0: ("NiFree_Wrapper", "Auto-named: NiFree_Wrapper"),
    0x0071f270: ("ComputeFileChecksum", "Compute file checksums for directory (used by both S+C)"),
    0x007202e0: ("HashString", "Auto-named: HashString"),
    0x0074b640: ("Py_CompileAndRun", "Compile + run Python source string"),
    0x0074c140: ("PyObject_GetAttrString", "getattr equivalent"),
    0x0074d140: ("Py_InitModule4", "Register Python module with method table"),
    0x0074d280: ("Py_BuildValue", "Build Python return values"),
    0x0074e310: ("PyArg_ParseTuple", "Parse Python args using format string"),
    0x00776cf0: ("PyObject_CallObject", "Call Python callable with args tuple"),

    # --- Phase 8A: Python C API functions (statically linked, traced from MP handlers) ---
    # Error handling
    0x0074af10: ("PyErr_Print", "Print current Python exception to stderr"),
    0x0074af20: ("PyErr_PrintEx", "Print exception with optional sys.last_* update"),
    0x0074b490: ("PyErr_ParseSyntaxError", "Parse SyntaxError fields from exception"),
    0x00752db0: ("PyErr_Restore", "Restore exception state (type, value, traceback)"),
    0x00752e40: ("PyErr_SetObject", "Set exception with object value"),
    0x00752e80: ("PyErr_SetString", "Set exception with string message"),
    0x00752ec0: ("PyErr_Occurred", "Check if an exception is currently set"),
    0x00752ed0: ("PyErr_GivenExceptionMatches", "Check if exception matches a given type"),
    0x00752f90: ("PyErr_NormalizeException", "Normalize exception triple (type, value, tb)"),
    0x00753110: ("PyErr_Fetch", "Fetch and clear current exception state"),
    0x00753140: ("PyErr_Clear", "Clear current exception state"),
    0x00753150: ("PyErr_BadArgument", "Raise TypeError for bad C API argument"),
    0x00753230: ("PyErr_SetNone", "Set exception with None value"),
    0x00753240: ("PyErr_BadInternalCall", "Raise SystemError for bad internal call"),
    # Dict operations
    0x00751cf0: ("PyDict_GetItem", "Get item from dict by key object"),
    0x00752cd0: ("PyDict_GetItemString", "Get item from dict by C string key"),
    0x00752d10: ("PyDict_SetItemString", "Set item in dict with C string key"),
    0x00752d70: ("PyDict_DelItemString", "Delete item from dict by C string key"),
    # String/Int operations
    0x007506c0: ("PyString_FromString", "Create Python string from C string"),
    0x007507d0: ("PyString_AsString", "Get C string from Python string object"),
    0x00751b80: ("PyString_InternFromString", "Create interned Python string from C string"),
    0x0074c7c0: ("PyInt_AsLong", "Convert Python int to C long"),
    # Object protocol
    0x0074bc90: ("PyObject_Print", "Print Python object to FILE*"),
    0x0074bdb0: ("PyObject_Repr", "Get repr() of Python object"),
    0x0074be20: ("PyObject_Str", "Get str() of Python object"),
    0x0074c100: ("PyObject_Hash", "Compute hash of Python object"),
    0x0074c200: ("PyObject_SetAttr", "Set attribute on Python object"),
    # System/Thread/File
    0x0074bb10: ("Py_HandleSystemExit", "Handle SystemExit exception"),
    0x00776c90: ("Py_FlushLine", "Flush sys.stdout if needed"),
    0x00779f90: ("PySys_GetObject", "Get named object from sys module"),
    0x00779fe0: ("PySys_SetObject", "Set named object in sys module"),
    0x0077c130: ("PyThreadState_Get", "Get current Python thread state"),
    0x007835d0: ("PyFile_SoftSpace", "Get/set softspace flag on file object"),
    0x00783690: ("PyFile_WriteObject", "Write Python object to file"),
    0x00783800: ("PyFile_WriteString", "Write C string to Python file object"),
    0x00783ce0: ("PyTraceBack_Print", "Print Python traceback to file"),

    0x007cb2c0: ("NiD3DGeometryGroupManager_ctor", "D3D geometry group manager constructor"),
    0x00817170: ("NiStream_RegisterStreamable", "Registers object in stream hash table"),
    0x008176b0: ("NiStream_LoadObject", "Reads NIF class name, looks up factory, creates object"),
    0x00818150: ("NiStream_LoadObjectAlt", "Alternative NIF load path"),

    # --- TGStringEvent (1) ---
    0x00407c70: ("TGStringEvent__ctor", "TGStringEvent method: ctor"),

    # --- Mission (6) ---
    0x00408070: ("Mission__ctor", "Mission method: ctor"),
    0x00408720: ("Mission__PlayerDied", "Mission method: PlayerDied"),
    0x00408790: ("Mission__PlayerChanged", "Mission method: PlayerChanged"),
    0x00408ae0: ("Mission__CreateShip", "Mission method: CreateShip"),
    0x00409080: ("Mission__PlayerEnteredSet", "Mission method: PlayerEnteredSet"),
    0x004091f0: ("Mission__PlayerExitedSet", "Mission method: PlayerExitedSet"),

    # --- NiNode (1) ---
    0x0040afe0: ("NiNode__FindChildrenByType", "NiNode method: FindChildrenByType"),

    # --- TypedObjectArray (1) ---
    0x0040b170: ("TypedObjectArray__FindByTypeAndID", "TypedObjectArray method: FindByTypeAndID"),

    # --- SetClass (19) ---
    0x0040cc80: ("SetClass__Cast", "SetClass method: Cast"),
    0x0040d150: ("SetClass__ctor", "SetClass method: ctor"),
    0x0040df80: ("SetClass__SetName", "SetClass method: SetName"),
    0x0040e980: ("SetClass__AddBackdropToSet", "SetClass method: AddBackdropToSet"),
    0x0040f070: ("SetClass__RemoveObjectFromSet", "SetClass method: RemoveObjectFromSet"),
    0x0040f920: ("SetClass__DeleteObjectFromSet", "SetClass method: DeleteObjectFromSet"),
    0x0040fcd0: ("SetClass__GetObjectByID", "SetClass method: GetObjectByID"),
    0x0040fd30: ("SetClass__GetObject", "SetClass method: GetObject"),
    0x0040fde0: ("SetClass__FindObjectByTypeAndID", "SetClass method: FindObjectByTypeAndID"),
    0x0040ff00: ("SetClass__GetPreviousObject", "SetClass method: GetPreviousObject"),
    0x0040ffa0: ("SetClass__GetFirstObject", "SetClass method: GetFirstObject"),
    0x00410600: ("SetClass__IsLocationEmptyTG", "SetClass method: IsLocationEmptyTG"),
    0x004128b0: ("SetClass__AddCameraToSet", "SetClass method: AddCameraToSet"),
    0x00412c60: ("SetClass__RemoveCameraFromSet", "SetClass method: RemoveCameraFromSet"),
    0x00412e50: ("SetClass__DeleteCameraFromSet", "SetClass method: DeleteCameraFromSet"),
    0x00412ec0: ("SetClass__SetActiveCamera", "SetClass method: SetActiveCamera"),
    0x00413950: ("SetClass__StartPick", "SetClass method: StartPick"),
    0x004139e0: ("SetClass__GetDotProductToObject", "SetClass method: GetDotProductToObject"),
    0x00413b70: ("SetClass__GetPickedObject", "SetClass method: GetPickedObject"),

    # --- TGDisplayName (1) ---
    0x0040e060: ("TGDisplayName__ctor", "TGDisplayName method: ctor"),

    # --- TGObjectTree (2) ---
    0x0040fe00: ("TGObjectTree__FindByHashAndTrack", "Hash bucket walk + tracking call"),
    0x0040fe80: ("TGObjectTree__GetNextSorted", "Binary search in sorted array, wraps on boundary"),

    # --- NiPoint3 (1) ---
    0x00414540: ("NiPoint3__Set", "NiPoint3 method: Set"),

    # --- Set (2) ---
    0x00414750: ("Set__SaveSetData", "Set method: SaveSetData"),
    0x00414e90: ("Set__LoadSetData", "Set method: LoadSetData"),

    # --- NiTArray (2) ---
    0x00417120: ("NiTArray__RemoveAtIndex", "NiTArray method: RemoveAtIndex"),
    0x00417170: ("NiTArray__BinarySearchByObjectID", "NiTArray method: BinarySearchByObjectID"),

    # --- SetManager (3) ---
    0x00417f00: ("SetManager__AddSet", "SetManager method: AddSet"),
    0x004181e0: ("SetManager__DeleteSet", "SetManager method: DeleteSet"),
    0x004182f0: ("SetManager__MakeRenderedSet", "SetManager method: MakeRenderedSet"),

    # --- TGNetworkManager (3) ---
    0x00418530: ("TGNetworkManager__UpdateAll", "TGNetworkManager method: UpdateAll"),
    0x004186d0: ("TGNetworkManager__SaveToStream", "TGNetworkManager method: SaveToStream"),
    0x00418740: ("TGNetworkManager__LoadFromStream", "TGNetworkManager method: LoadFromStream"),

    # --- AsteroidField (3) ---
    0x004196d0: ("AsteroidField__HandleShipEnterSet", "AsteroidField method: HandleShipEnterSet"),
    0x00419b30: ("AsteroidField__RegisterHandlerNames", "AsteroidField: registers EnterSet/ExitSet/ShipEnter/ShipExit/Proximity name strings"),
    0x00419ba0: ("AsteroidField__RegisterHandlers", "AsteroidField: registers EnterSet/ExitSet event handlers"),

    # --- AsteroidTile (2) ---
    0x0041c280: ("AsteroidTile__RegisterHandlerNames", "AsteroidTile: registers EnterSet/ExitSet name strings"),
    0x0041c2b0: ("AsteroidTile__RegisterHandlers", "AsteroidTile: registers EnterSet/ExitSet event handlers"),

    # --- LightManager (2) ---
    0x0041ce00: ("LightManager__SaveToStream", "LightManager method: SaveToStream"),
    0x0041ce20: ("LightManager__LoadFromStream", "LightManager method: LoadFromStream"),

    # --- CameraMode (5) ---
    0x0041eee0: ("CameraMode__TrackObject", "CameraMode method: TrackObject"),
    0x0041f020: ("CameraMode__SetAttrIDObject", "CameraMode method: SetAttrIDObject"),
    0x0041f040: ("CameraMode__GetAttrIDObject", "CameraMode method: GetAttrIDObject"),
    0x0041f0b0: ("CameraMode__RegisterHandlerNames", "CameraMode: registers ObjectChangedToHulk name string, calls TorpCameraMode__RegisterHandlerNames"),
    0x00421290: ("CameraMode__GetAttrPoint", "CameraMode method: GetAttrPoint"),

    # --- TGObject (28) ---
    0x0041f710: ("TGObject__SaveAllToStream", "TGObject method: SaveAllToStream"),
    0x0041f8d0: ("TGObject__LoadAllFromStream", "TGObject method: LoadAllFromStream"),
    0x00431030: ("TGObject__CompareID", "TGObject method: CompareID"),
    0x005a04c0: ("TGObject__SetVelocity", "Sets NiAVObject velocity via +0x18"),
    0x005ab670: ("TGObject__AsShip", "IsA(0x8008) cast, returns NULL if not ship"),
    0x006d5e40: ("TGObject__SetDeleteFlag", "TGObject method: SetDeleteFlag"),
    0x006d5e80: ("TGObject__SetDirtyFlag", "Sets/clears bit 2 of +0x18 flags word"),
    0x006d92b0: ("TGObject__RegisterEventHandler", "TGObject method: RegisterEventHandler"),
    0x006d92d0: ("TGObject__RegisterKeyboardHandler", "TGObject method: RegisterKeyboardHandler"),
    0x006da130: ("TGObject__RegisterHandlerWithName", "Register event type -> handler callback"),
    0x006da160: ("TGObject__RegisterMouseHandler", "TGObject method: RegisterMouseHandler"),
    0x006f0a70: ("TGObject__ctor", "TGObject method: ctor"),
    0x006f0b70: ("TGObject__scalar_deleting_dtor", "TGObject method: scalar_deleting_dtor"),
    0x006f0ba0: ("TGObject__dtor", "TGObject method: dtor"),
    0x006f0bc0: ("TGObject__SaveToStream", "Master object save: serialize to NiStream"),
    0x006f0c40: ("TGObject__LoadFromStream", "Master object load: factory create + fixup + hash table"),
    0x006f0f30: ("TGObject__RegisterInHashTable", "TGObject method: RegisterInHashTable"),
    0x006f0fc0: ("TGObject__UnregisterFromHashTable", "TGObject method: UnregisterFromHashTable"),
    0x006f11b0: ("TGObject__FixupAllReferences", "Resolve object ID references after load"),
    0x006f13c0: ("TGObject__ResolveStreamRefs", "TGObject method: ResolveStreamRefs"),
    # TGObject vtable virtuals (Phase 8B: Ship vtable mining)
    0x006f15c0: ("TGObject__InvokePythonHandler", "Virtual slot 8 (+0x20): invoke Python event handler"),
    0x006f1650: ("TGObject__DebugPrint", "Virtual slot 3 (+0x0C): debug print object info"),
    0x006f1680: ("TGObject__GetIndentString", "TGObject method: GetIndentString"),
    0x006f16a0: ("TGObject__SetObjectID", "TGObject method: SetObjectID"),
    0x006f2670: ("TGObject__WriteToStream", "TGObject method: WriteToStream"),
    0x006f26b0: ("TGObject__ReadFromStream", "TGObject method: ReadFromStream"),
    0x006f27f0: ("TGObject__ResolveObjectRefs", "TGObject method: ResolveObjectRefs"),

    # --- TorpCameraMode (3) ---
    0x00426c80: ("TorpCameraMode__Constructor", "TorpCameraMode method: Constructor"),
    0x00427180: ("TorpCameraMode__RegisterHandlerNames", "TorpCameraMode: registers TorpFired name string"),
    0x004271a0: ("TorpCameraMode__RegisterHandlers", "TorpCameraMode: stub RegisterHandlers"),

    # --- CameraObjectClass (8) ---
    0x0042a0b0: ("CameraObjectClass__Create", "CameraObjectClass method: Create"),
    0x0042a690: ("CameraObjectClass__SetFrustumValues", "CameraObjectClass method: SetFrustumValues"),
    0x0042acd0: ("CameraObjectClass__PushCameraMode", "CameraObjectClass method: PushCameraMode"),
    0x0042ad70: ("CameraObjectClass__GetCurrentCameraMode", "CameraObjectClass method: GetCurrentCameraMode"),
    0x0042b070: ("CameraObjectClass__GetNamedCameraMode", "CameraObjectClass method: GetNamedCameraMode"),
    0x0042bcb0: ("CameraObjectClass__LookToward", "CameraObjectClass method: LookToward"),
    0x0042c380: ("CameraObjectClass__RegisterHandlerNames", "CameraObjectClass: registers AnimationDone name string, calls CameraMode chain"),
    0x0042c3a0: ("CameraObjectClass__RegisterHandlers", "CameraObjectClass: registers AnimationDone event handler, calls TorpCameraMode stub"),

    # --- TGSceneObject (6) ---
    0x00430830: ("TGSceneObject__InitSceneNode", "TGSceneObject method: InitSceneNode"),
    0x004308e0: ("TGSceneObject__ctor", "TGSceneObject method: ctor"),
    0x00430a10: ("TGSceneObject__ctor", "TGSceneObject method: ctor"),
    0x00430b70: ("TGSceneObject__SetModel", "TGSceneObject method: SetModel"),
    0x00431af0: ("TGSceneObject__WriteToStream", "TGSceneObject method: WriteToStream"),
    0x00431cd0: ("TGSceneObject__ReadFromStream", "TGSceneObject method: ReadFromStream"),

    # --- TGSceneObjectClass (1) ---
    0x00430a90: ("TGSceneObjectClass__dtor", "TGSceneObjectClass method: dtor"),

    # --- Backdrop (1) ---
    0x00433880: ("Backdrop__WriteToStream", "Backdrop method: WriteToStream"),

    # --- TGSceneGraph (3) ---
    0x00434e00: ("TGSceneGraph__GetObjectByID", "Hash lookup then IsA(0x8003) cast"),
    0x00434e70: ("TGSceneGraph__FindObjectByID", "Searches by ID across scene roots"),
    0x004a2430: ("TGSceneGraph__FindObjectByName", "TGSceneGraph method: FindObjectByName"),

    # --- ObjectClass (12) ---
    0x00434ed0: ("ObjectClass__Cast", "ObjectClass method: Cast"),
    0x00434f00: ("ObjectClass__ctor", "ObjectClass method: ctor"),
    0x00435030: ("ObjectClass__ctor", "ObjectClass method: ctor"),
    0x00435090: ("ObjectClass__InitDefaults", "ObjectClass method: InitDefaults"),
    0x004350e0: ("ObjectClass__dtor", "ObjectClass method: dtor"),
    0x00435190: ("ObjectClass__AllocAndConstruct", "ObjectClass method: AllocAndConstruct"),
    0x004351c0: ("ObjectClass__RegisterHandlerNames", "ObjectClass: registers EnteredSet name string"),
    0x004351e0: ("ObjectClass__RegisterHandlers_Stub", "ObjectClass: stub RegisterHandlers"),
    0x00435220: ("ObjectClass__PlaceObjectByName", "ObjectClass method: PlaceObjectByName"),
    0x00435ec0: ("ObjectClass__LineCollides", "ObjectClass method: LineCollides"),
    0x00435f90: ("ObjectClass__ReplaceTexture", "ObjectClass method: ReplaceTexture"),
    0x00436080: ("ObjectClass__RefreshReplacedTextures", "ObjectClass method: RefreshReplacedTextures"),
    0x00436640: ("ObjectClass__WriteToStream", "ObjectClass method: WriteToStream"),
    0x00436760: ("ObjectClass__ReadFromStream", "ObjectClass method: ReadFromStream"),

    # --- UtopiaApp (15) ---
    0x00437f50: ("UtopiaApp__New", "UtopiaApp method: New"),
    0x00437fb0: ("UtopiaApp__ctor", "UtopiaApp method: ctor"),
    0x00438280: ("UtopiaApp__dtor_00438280", "UtopiaApp method: dtor_00438280"),
    0x00438290: ("UtopiaApp__CreateRenderer", "Reads 'Graphics Options' config, creates NiDX7Renderer + NiCamera"),
    0x0043b4f0: ("UtopiaApp__MainTick", "UtopiaApp method: MainTick"),
    0x0043b790: ("UtopiaApp__UpdateWindows", "UtopiaApp method: UpdateWindows"),
    0x0043bbd0: ("UtopiaApp__SetPaused", "UtopiaApp method: SetPaused"),
    0x004433e0: ("UtopiaApp__Render", "UtopiaApp method: Render"),
    0x00443710: ("UtopiaApp__SetPendingMissionPath", "UtopiaApp method: SetPendingMissionPath"),
    0x004447f0: ("UtopiaApp__ProcessPendingMissionLoad", "UtopiaApp method: ProcessPendingMissionLoad"),
    0x00445d90: ("UtopiaApp__InitMultiplayer", "Network init: create WSN, bind port, connect"),
    0x00445ec0: ("UtopiaApp__IsNotDialupConnected", "UtopiaApp method: IsNotDialupConnected"),
    0x00445ed0: ("UtopiaApp__CleanupMultiplayer", "UtopiaApp method: CleanupMultiplayer"),
    0x006cdb10: ("UtopiaApp__dtor", "UtopiaApp method: dtor"),
    0x006cdd20: ("UtopiaApp__OnIdle", "UtopiaApp method: OnIdle"),

    # --- ObjectGroup (8) ---
    0x0043ef70: ("ObjectGroup__ctor", "ObjectGroup method: ctor"),
    0x0059c7b0: ("ObjectGroup__RegisterHandlerNames", "ObjectGroup: registers EnteredSet/ExitedSet/ObjectDestroyed/ObjectDeleted name strings"),
    0x0059d130: ("ObjectGroup__RegisterHandlers_Stub", "ObjectGroup: stub RegisterHandlers"),
    0x0059c890: ("ObjectGroup__dtor", "ObjectGroup method: dtor"),
    0x0059c900: ("ObjectGroup__ExitedSet", "ObjectGroup method: ExitedSet"),
    0x0059c990: ("ObjectGroup__AddName", "ObjectGroup method: AddName"),
    0x0059cff0: ("ObjectGroup__IsNameInGroup", "ObjectGroup method: IsNameInGroup"),
    0x0059d0d0: ("ObjectGroup__ObjectDestroyed", "ObjectGroup method: ObjectDestroyed"),
    0x0059d4b0: ("ObjectGroup__ObjectDeleted", "ObjectGroup method: ObjectDeleted"),

    # --- ObjectExplodingEvent (1) ---
    0x0043f8b0: ("ObjectExplodingEvent__ctor", "ObjectExplodingEvent constructor (factory 0x8129)"),

    # --- PoweredMaster (10) ---
    0x00440090: ("PoweredMaster__ctor_stream", "PoweredMaster method: ctor_stream"),
    0x00563530: ("PoweredMaster__ctor", "PoweredMaster method: ctor"),
    0x00563610: ("PoweredMaster__dtor", "PoweredMaster method: dtor"),
    0x00563700: ("PoweredMaster__ComputeAvailablePower", "Compute conduit limits and available pool"),
    0x00563780: ("PoweredMaster__Update", "Main power sim tick (1/sec): recharge + distribute"),
    0x005638d0: ("PoweredMaster__AddPowerToBatteries", "Recharge main battery, overflow to backup"),
    0x00563a70: ("PoweredMaster__DrawFromMainBattery", "Mode 0: main first, then backup fallback"),
    0x00563bb0: ("PoweredMaster__DrawFromBackupBattery", "Mode 1: backup first, then main fallback"),
    0x00563cb0: ("PoweredMaster__DrawFromBackupOnly", "Mode 2: backup only, no fallback"),
    0x00563d50: ("PoweredMaster__SetPowerSource", "Register consumer in power distribution list"),

    # --- MultiplayerGame (23) ---
    0x00442830: ("MultiplayerGame__ctor_stream", "MultiplayerGame method: ctor_stream"),
    0x0069e560: ("MultiplayerGame__Cast", "MultiplayerGame method: Cast"),
    0x0069e590: ("MultiplayerGame__Constructor", "MultiplayerGame constructor (registers all event handlers)"),
    0x0069ebb0: ("MultiplayerGame__dtor", "MultiplayerGame method: dtor"),
    0x0069edc0: ("MultiplayerGame__Update", "MultiplayerGame method: Update"),
    0x0069ee50: ("MultiplayerGame__SendStateUpdates", "MultiplayerGame method: SendStateUpdates"),
    0x0069efc0: ("MultiplayerGame__InitializeAllSlots", "MultiplayerGame method: InitializeAllSlots"),
    0x0069efe0: ("MultiplayerGame__RegisterHandlerNames", "Registers game event -> opcode mappings"),
    0x0069f250: ("MultiplayerGame__KillGameHandler", "MultiplayerGame method: KillGameHandler"),
    0x006a01b0: ("MultiplayerGame__HostMsgHandler", "Self-destruct request (client->host, 1-byte, no payload)"),
    0x006a02a0: ("MultiplayerGame__RequestObjHandler", "MultiplayerGame method: RequestObjHandler"),
    0x006a0490: ("MultiplayerGame__ObjNotFoundHandler", "MultiplayerGame method: ObjNotFoundHandler"),
    0x006a05e0: ("MultiplayerGame__EnterSetHandler", "MultiplayerGame method: EnterSetHandler"),
    0x006a0a30: ("MultiplayerGame__NewPlayerHandler", "New player joined (init slot, start checksums)"),
    0x006a1360: ("MultiplayerGame__DeletePlayerUIHandler", "Join/disconnect player list update (TGEvent factory 0x866)"),
    0x006a1420: ("MultiplayerGame__DeletePlayerAnimHandler", "Player join/leave floating text (TGL lookup, crash risk)"),
    0x006a17c0: ("MultiplayerGame__SendSerializedEvent", "MultiplayerGame method: SendSerializedEvent"),
    0x006a19a0: ("MultiplayerGame__GetPlayerSlotFromObjID", "MultiplayerGame method: GetPlayerSlotFromObjID"),
    0x006a19c0: ("MultiplayerGame__FindSlotByConnID", "MultiplayerGame method: FindSlotByConnID"),
    0x006a2650: ("MultiplayerGame__CountActivePlayers", "Returns number of connected players"),
    0x006a7720: ("MultiplayerGame__PlayerSlotElementCtor", "MultiplayerGame method: PlayerSlotElementCtor"),
    0x006a7760: ("MultiplayerGame__PlayerSlotElementDtor", "MultiplayerGame method: PlayerSlotElementDtor"),
    0x006a7770: ("MultiplayerGame__InitPlayerSlot", "Initialize player slot data"),

    # --- SaveGame (4) ---
    0x00444470: ("SaveGame__DeleteTempSaveFiles", "FindFirstFile *.msv in TEMP_MISSION_SAVE_FOLDER, deletes"),
    0x006dd5b0: ("SaveGame__SaveDirtyObjects", "Walks hash table of dirty objects, serializes each"),
    0x006f9fb0: ("SaveGame__InitPickler", "Creates cPickle.Pickler for Python state serialization"),
    0x006fa020: ("SaveGame__FlushPickler", "Calls marshal.dump + getvalue, writes pickled data"),

    # --- SetFloatVarEvent (3) ---
    0x00448d60: ("SetFloatVarEvent__ctor", "SetFloatVarEvent method: ctor"),
    0x00448e10: ("SetFloatVarEvent__SetScope", "SetFloatVarEvent method: SetScope"),
    0x00448e80: ("SetFloatVarEvent__SetName", "SetFloatVarEvent method: SetName"),

    # --- VarManagerClass (6) ---
    0x0044b2d0: ("VarManagerClass__RegisterHandlerNames", "VarManagerClass: registers SetFloatVar handler name string"),
    0x0044b2f0: ("VarManagerClass__RegisterHandlers", "VarManagerClass: registers SetFloatVar event handler"),
    0x0044b310: ("VarManagerClass__SetFloatVariable", "VarManagerClass method: SetFloatVariable"),
    0x0044b490: ("VarManagerClass__GetFloatVariable", "VarManagerClass method: GetFloatVariable"),
    0x0044b500: ("VarManagerClass__SetStringVariable", "VarManagerClass method: SetStringVariable"),
    0x0044b680: ("VarManagerClass__GetStringVariable", "VarManagerClass method: GetStringVariable"),

    # --- SystemManager (2) ---
    0x0044d7a0: ("SystemManager__SaveToStream", "SystemManager method: SaveToStream"),
    0x0044d7e0: ("SystemManager__LoadFromStream", "SystemManager method: LoadFromStream"),

    # --- TGModelRegistry (2) ---
    0x00452b70: ("TGModelRegistry__SaveToStream", "TGModelRegistry method: SaveToStream"),
    0x00452cb0: ("TGModelRegistry__LoadFromStream", "TGModelRegistry method: LoadFromStream"),

    # --- TGMatrix3 (11) ---
    0x00459e60: ("TGMatrix3__Inverse", "TGMatrix3 method: Inverse"),
    0x00459ec0: ("TGMatrix3__Transpose", "TGMatrix3 method: Transpose"),
    0x0045a460: ("TGMatrix3__TransposeTimes", "TGMatrix3 method: TransposeTimes"),
    0x0045a590: ("TGMatrix3__Congruence", "TGMatrix3 method: Congruence"),
    0x0045a8e0: ("TGMatrix3__EigenSolveSymmetric", "TGMatrix3 method: EigenSolveSymmetric"),
    0x0045b3a0: ("TGMatrix3__FromEulerAnglesXYZ", "TGMatrix3 method: FromEulerAnglesXYZ"),
    0x0045b450: ("TGMatrix3__FromEulerAnglesXZY", "TGMatrix3 method: FromEulerAnglesXZY"),
    0x0045b500: ("TGMatrix3__FromEulerAnglesYXZ", "TGMatrix3 method: FromEulerAnglesYXZ"),
    0x0045b5b0: ("TGMatrix3__FromEulerAnglesYZX", "TGMatrix3 method: FromEulerAnglesYZX"),
    0x0045b660: ("TGMatrix3__FromEulerAnglesZXY", "TGMatrix3 method: FromEulerAnglesZXY"),
    0x0045b710: ("TGMatrix3__FromEulerAnglesZYX", "TGMatrix3 method: FromEulerAnglesZYX"),

    # --- TGPoint3 (8) ---
    0x0045c1a0: ("TGPoint3__Cross", "TGPoint3 method: Cross"),
    0x0045e7b0: ("TGPoint3__GetRandomUnitVector", "TGPoint3 method: GetRandomUnitVector"),
    0x0045e8d0: ("TGPoint3__MultMatrix", "TGPoint3 method: MultMatrix"),
    0x0045e980: ("TGPoint3__GetAlignedComponent", "TGPoint3 method: GetAlignedComponent"),
    0x0045ea50: ("TGPoint3__GetPerpendicularComponent", "TGPoint3 method: GetPerpendicularComponent"),
    0x00581e60: ("TGPoint3__UnitCross", "TGPoint3 method: UnitCross"),
    0x00811b10: ("TGPoint3__LoadBinary", "TGPoint3 method: LoadBinary"),
    0x00811b50: ("TGPoint3__SaveBinary", "TGPoint3 method: SaveBinary"),

    # --- TGStringToStringMap (2) ---
    0x0045f810: ("TGStringToStringMap__GetDest", "TGStringToStringMap method: GetDest"),
    0x0045f8b0: ("TGStringToStringMap__DeleteMappings", "TGStringToStringMap method: DeleteMappings"),

    # --- ChatObjectClass (4) ---
    0x00461220: ("ChatObjectClass__ReceiveMessageHandler", "ChatObjectClass method: ReceiveMessageHandler"),
    0x004617c0: ("ChatObjectClass__DisconnectHandler", "ChatObjectClass: handle disconnect event"),
    0x00461500: ("ChatObjectClass__RegisterHandlerNames", "ChatObjectClass: registers Connect/Disconnect/ReceiveMessage name strings"),
    0x00461560: ("ChatObjectClass__RegisterHandlers", "ChatObjectClass: registers Connect/Disconnect/ReceiveMessage event handlers"),

    # --- FrameBudgetScheduler (1) ---
    0x0046f420: ("FrameBudgetScheduler__Update", "FrameBudgetScheduler method: Update"),

    # --- BaseAI (2) ---
    0x00470520: ("BaseAI__Constructor", "Base AI node ctor: assigns ID from global counter, writes vtable 0x0088bb54"),
    0x004707d0: ("BaseAI__dtor", "BaseAI method: dtor"),

    # --- Ship (56) --- vtable at 0x00894340, 92 slots, size 0x328
    0x004721b0: ("Ship__AITickScheduler", "Iterates ship array calling Ship__ProcessAITick per ship"),
    0x004722d0: ("Ship__ProcessAITick", "Per-ship AI callback: walks behavior tree, fires preprocessors"),
    0x00472810: ("Ship__UpdateAI", "Ship method: UpdateAI"),
    0x0057cb10: ("Ship__SendTorpedoFire_0x19", "Ship method: SendTorpedoFire_0x19"),
    0x00593f30: ("Ship__CreateDamageNotification", "Creates visual notification, gated on IsHost==0 (client-only)"),
    0x005a05a0: ("Ship__GetVelocity", "Ship method: GetVelocity"),
    0x005a2030: ("Ship__ReadSpeciesFromStream", "Ship method: ReadSpeciesFromStream"),
    0x005ab970: ("Ship__InitFields", "Ship method: InitFields"),
    0x005abac0: ("Ship__ComputeBoundsFromGeometry", "Ship method: ComputeBoundsFromGeometry"),
    0x005abc30: ("Ship__GetBoundingBox", "Virtual slot 58 (+0xE8): AABB computation override"),
    0x005abdc0: ("Ship__ctor", "Ship method: ctor (writes vtable 0x00894340, size 0x328)"),
    0x005abfe0: ("Ship__scalar_deleting_dtor", "Virtual slot 0 (+0x00): destructor"),
    0x005ac010: ("Ship__ctor_stream", "Ship method: ctor_stream"),
    0x005ac0a0: ("Ship__dtor", "Ship method: dtor"),
    0x005ac250: ("Ship__RunDeathScript", "SWIG target: calls Effects.ObjectExploding or custom death script"),
    0x005ac370: ("Ship__StartGetSubsystemMatch", "SWIG target: allocates iterator for type matching"),
    0x005ac390: ("Ship__GetNextSubsystemMatch", "SWIG target: returns next subsystem matching type"),
    0x005ac450: ("Ship__IsCloaked", "SWIG target: reads cloaking subsystem +0xAC state"),
    0x005ac470: ("Ship__SetImpulse", "SWIG target: clamps 0..1, sets direction/speed"),
    0x005ac4f0: ("Ship__IsReversing", "Ship method: IsReversing"),
    0x005ac590: ("Ship__SetSpeed", "SWIG target: divides by max speed then calls SetImpulse"),
    0x005ac6e0: ("Ship__InSystemWarp", "SWIG target: pathfinding + obstacle avoidance"),
    0x005acdb0: ("Ship__StopInSystemWarp", "Clears warp state, fires ET_EXITED_WARP, restores velocity"),
    0x005ad290: ("Ship__SetTargetAngularVelocityDirect", "SWIG target: sets angular velocity directly"),
    0x005ad3a0: ("Ship__TurnTowardLocation", "Normalizes direction to target, calls TurnTowardDirection"),
    0x005ad450: ("Ship__TurnTowardDirection", "Gets orientation, computes turn via ComputeTurnAngularVelocity"),
    0x005ad4d0: ("Ship__TurnTowardDifference", "SWIG target: turn toward angle difference"),
    0x005ad910: ("Ship__ComputeTurnAngularVelocity", "Quaternion slerp-style turn with up/forward constraints"),
    0x005adae0: ("Ship__Update", "Virtual slot 21 (+0x54): per-tick ship update override"),
    0x005ae140: ("Ship__IsPlayerShip", "SWIG target: host checks +0x2E4, client compares GetPlayerShip()"),
    0x005ae170: ("Ship__GetTarget", "SWIG target: reads +0x21C target ID, validates alive"),
    0x005ae1e0: ("Ship__SetTarget", "SWIG target: FindObjectByID + SetTargetInternal"),
    0x005ae210: ("Ship__SetTargetInternal", "Fires ET_TARGET_WAS_CHANGED, stops weapons, updates subsystems"),
    0x005ae2c0: ("Ship__OnTargetChanged", "Updates weapon offsets, fires ET_TARGET_SUBSYSTEM_SET"),
    0x005ae430: ("Ship__UpdateWeaponTargets", "Walks +0x284 subsystems, updates weapon target entries"),
    0x005ae600: ("Ship__ClearTargets", "Virtual slot 78 (+0x138): clear all target references"),
    0x005ae630: ("Ship__GetTargetSubsystemObject", "Resolves +0x220 target subsystem ID via ForwardEvent"),
    0x005ae650: ("Ship__GetTargetOffset", "Returns +0x228 target offset"),
    0x005ae6d0: ("Ship__GetNextTarget", "Cycles through sorted targets via +0x87 index"),
    0x005aeb90: ("Ship__CollectSubsystemsInRadius", "Recursive distance check per subsystem, builds result list"),
    0x005aecc0: ("Ship__FindSubsystemsInDamageRadius", "Walks +0x284 linked list, collects subsystems within radius"),
    0x005af7d0: ("Ship__CheckCollisionWithCulling", "Virtual slot 82 (+0x148): collision check with view culling"),
    0x005af830: ("Ship__CheckCollisionWithCulling_B", "Virtual slot 83 (+0x14C): alternate collision check"),
    0x005af890: ("Ship__CheckCollision", "Virtual slot 84 (+0x150): main collision check override"),
    0x005b0110: ("Ship__AssignWeaponGroups", "Ship method: AssignWeaponGroups"),
    0x005b0bb0: ("Ship__StopFiringWeapons", "SWIG target: walks +0x284, finds WeaponSystems via IsA(0x801D)"),
    0x005b0f00: ("Ship__WriteToStream", "Virtual slot 4 (+0x10): serialize ship to stream"),
    0x005b1220: ("Ship__ReadFromStream", "Virtual slot 5 (+0x14): deserialize ship from stream"),
    0x005b1500: ("Ship__ResolveObjectRefs", "Virtual slot 6 (+0x18): resolve all subsystem object references"),
    0x005b1550: ("Ship__PostDeserialize", "Virtual slot 7 (+0x1C): rebuild subsystem serialization list"),
    0x005b21c0: ("Ship__ReadStateUpdate", "Virtual slot 73 (+0x124): receives state update from network"),
    0x005b3e20: ("Ship__LinkAllSubsystemsToParents", "Virtual slot 89 (+0x164): type-based parent-child linking"),
    0x005b3e50: ("Ship__AddSubsystem", "SWIG target: adds to +0x280 list, classifies by IsA checks"),
    0x005b5030: ("Ship__LinkSubsystemToParent", "Ship method: LinkSubsystemToParent"),
    0x005b5eb0: ("Ship__SubsystemHashComputation", "Ship method: SubsystemHashComputation"),

    # --- AIScheduler (3) ---
    0x00472660: ("AIScheduler__ProcessSpecialTicks", "AIScheduler method: ProcessSpecialTicks"),
    0x00472ad0: ("AIScheduler__SaveToStream", "AIScheduler method: SaveToStream"),
    0x00472b60: ("AIScheduler__LoadFromStream", "AIScheduler method: LoadFromStream"),

    # --- BuilderAI (2) ---
    0x00475fb0: ("BuilderAI__Constructor", "Builder meta-node ctor: writes vtable 0x0088bbe0, extends PreprocessingAI, size 0x88"),
    0x00606a10: ("BuilderAI__AllocAndConstruct", "cdecl factory: NiAlloc + BuilderAI ctor"),

    # --- ConditionalAI (5) ---
    0x00478a50: ("ConditionalAI__Constructor", "Conditional eval node ctor: writes vtable 0x0088bc84, size 0x58"),
    0x00479670: ("ConditionalAI__SetActive", "ConditionalAI becomes active (evaluates conditions)"),
    0x00479710: ("ConditionalAI__SetInactive", "ConditionalAI goes inactive"),
    0x004797d0: ("ConditionalAI__LostFocus", "ConditionalAI loses focus"),
    0x00605640: ("ConditionalAI__AllocAndConstruct", "cdecl factory: NiAlloc + ConditionalAI ctor"),

    # --- ConditionScript (2) ---
    0x0047b120: ("ConditionScript__SaveConditionEventCreators", "Serialize condition event creators"),
    0x0047b310: ("ConditionScript__LoadConditionEventCreators", "ConditionScript method: LoadConditionEventCreators"),

    # --- NetworkAI (1) ---
    0x0047dab0: ("NetworkAI__ctor", "NetworkAI method: ctor"),

    # --- PulseWeaponProperty (6) ---
    0x00484a20: ("PulseWeaponProperty__GetOrientationForward", "PulseWeaponProperty method: GetOrientationForward"),
    0x00575d50: ("PulseWeaponProperty__GetOrientationUp", "PulseWeaponProperty method: GetOrientationUp"),
    0x00575d80: ("PulseWeaponProperty__GetOrientationRight", "PulseWeaponProperty method: GetOrientationRight"),
    0x0068c0f0: ("PulseWeaponProperty__Cast", "PulseWeaponProperty method: Cast"),
    0x0068d820: ("PulseWeaponProperty__SetOrientation", "PulseWeaponProperty method: SetOrientation"),
    0x0068d8e0: ("PulseWeaponProperty__SetModuleName", "PulseWeaponProperty method: SetModuleName"),

    # --- TGLinkedList (4) ---
    0x00486be0: ("TGLinkedList__AllocNode", "Pool allocator: chunks of N*12 bytes, free list at +0xC"),
    0x005666e0: ("TGLinkedList__RemoveNode", "Unlinks node from doubly-linked list, returns value"),
    0x006d6f80: ("TGLinkedList__Pop", "Pop front from singly-linked list"),
    0x006d7100: ("TGDoublyLinkedList__Remove", "Remove node from doubly-linked list (head/tail/mid)"),

    # --- TGEventHandlerObject (16) ---
    0x0048bc40: ("TGEventHandlerObject__dtor_0048bc40", "TGEventHandlerObject method: dtor_0048bc40"),
    0x006d4b10: ("TGEventHandlerObject__dtor_006d4b10", "TGEventHandlerObject method: dtor_006d4b10"),
    0x006d5a80: ("TGEventHandlerObject__RemoveHandler", "TGEventHandlerObject method: RemoveHandler"),
    0x006d8f90: ("TGEventHandlerObject__ctor", "TGEventHandlerObject method: ctor"),
    0x006d9060: ("TGEventHandlerObject__dtor", "TGEventHandlerObject method: dtor"),
    0x006d90e0: ("TGEventHandlerObject__CallNextHandler", "Forward event through responder chain"),
    0x006d9100: ("TGEventHandlerObject__WriteToStream", "TGEventHandlerObject method: WriteToStream"),
    0x006d9160: ("TGEventHandlerObject__ReadFromStream", "TGEventHandlerObject method: ReadFromStream"),
    0x006d9330: ("TGEventHandlerObject__EnsureInstanceTable", "Lazy-init per-object handler table (+0x10)"),
    0x006d9420: ("TGEventHandlerObject__AddPythonFuncHandler", "TGEventHandlerObject method: AddPythonFuncHandler"),
    0x006d9450: ("TGEventHandlerObject__AddPythonMethodHandler", "TGEventHandlerObject method: AddPythonMethodHandler"),
    0x006d94a0: ("TGEventHandlerObject__RemoveAllInstanceHandlers", "TGEventHandlerObject method: RemoveAllInstanceHandlers"),
    0x006d94e0: ("TGEventHandlerObject__RegisterHandlerNames", "TGEventHandlerObject method: RegisterHandlerNames"),
    0x006d9510: ("TGEventHandlerObject__RegisterHandlers", "TGEventHandlerObject method: RegisterHandlers"),
    0x006d9540: ("TGEventHandlerObject__DeleteMeStage1", "TGEventHandlerObject method: DeleteMeStage1"),
    0x006f2650: ("TGEventHandlerObject__dtor", "TGEventHandlerObject method: dtor"),

    # --- PlainAI (9) ---
    0x0048cc40: ("PlainAI__Constructor", "Leaf AI node ctor: writes vtable 0x0088c0d8, calls BaseAI ctor"),
    0x0048ccd0: ("PlainAI__dtor", "PlainAI method: dtor"),
    0x0048d100: ("PlainAI__Update", "PlainAI tick: calls Python script Activate/update"),
    0x0048d360: ("PlainAI__SetActive", "PlainAI becomes active in behavior tree"),
    0x0048d400: ("PlainAI__SetInactive", "PlainAI goes inactive"),
    0x0048d4a0: ("PlainAI__GotFocus", "PlainAI gains priority focus"),
    0x0048d540: ("PlainAI__LostFocus", "PlainAI loses priority focus"),
    0x0048d710: ("PlainAI__ctor_stream", "PlainAI method: ctor_stream"),
    0x006043c0: ("PlainAI__AllocAndConstruct", "cdecl factory: NiAlloc + PlainAI ctor"),

    # --- PreprocessingAI (8) ---
    0x0048e2b0: ("PreprocessingAI__Constructor", "Preprocessor wrapper node ctor: writes vtable 0x0088c12c, size 0x4C"),
    0x0048e710: ("PreprocessingAI__SetActive", "PreprocessingAI becomes active (runs preprocessor)"),
    0x0048e7d0: ("PreprocessingAI__SetInactive", "PreprocessingAI goes inactive"),
    0x0048e890: ("PreprocessingAI__GotFocus", "PreprocessingAI gains focus"),
    0x0048e950: ("PreprocessingAI__LostFocus", "PreprocessingAI loses focus"),
    0x0048ea30: ("PreprocessingAI__Update", "PreprocessingAI tick: preprocessor + contained AI"),
    0x0048ec20: ("PreprocessingAI__IsDormant", "PreprocessingAI dormancy check"),
    0x006050c0: ("PreprocessingAI__AllocAndConstruct", "cdecl factory: NiAlloc + PreprocessingAI ctor"),

    # --- PriorityListAI (7) ---
    0x0048fcb0: ("PriorityListAI__Constructor", "Priority composite node ctor: writes vtable 0x0088c188, size 0x38"),
    0x00490140: ("PriorityListAI__SetActive", "PriorityListAI becomes active (evaluates children by priority)"),
    0x004901e0: ("PriorityListAI__SetInactive", "PriorityListAI goes inactive"),
    0x004902a0: ("PriorityListAI__LostFocus", "PriorityListAI loses focus"),
    0x00490340: ("PriorityListAI__Update", "PriorityListAI tick: iterate children by priority"),
    0x00490560: ("PriorityListAI__IsDormant", "PriorityListAI dormancy check"),
    0x00604620: ("PriorityListAI__AllocAndConstruct", "cdecl factory: NiAlloc + PriorityListAI ctor"),

    # --- RandomAI (6) ---
    0x00491370: ("RandomAI__Constructor", "Random selection node ctor: writes vtable 0x0088c1dc, size 0x40"),
    0x00491620: ("RandomAI__SetActive", "RandomAI becomes active (picks random child)"),
    0x00491690: ("RandomAI__SetInactive", "RandomAI goes inactive"),
    0x00491740: ("RandomAI__LostFocus", "RandomAI loses focus"),
    0x004917f0: ("RandomAI__Update", "RandomAI tick: run selected child"),
    0x00604ef0: ("RandomAI__AllocAndConstruct", "cdecl factory: NiAlloc + RandomAI ctor"),

    # --- SequenceAI (7) ---
    0x004927d0: ("SequenceAI__Constructor", "Sequence composite node ctor: writes vtable 0x0088c230, size 0x40"),
    0x00492b10: ("SequenceAI__SetActive", "SequenceAI becomes active (runs children in order)"),
    0x00492b90: ("SequenceAI__SetInactive", "SequenceAI goes inactive"),
    0x00492c50: ("SequenceAI__LostFocus", "SequenceAI loses focus"),
    0x00492d00: ("SequenceAI__Update", "SequenceAI tick: advance to next child when current completes"),
    0x00492ea0: ("SequenceAI__IsDormant", "SequenceAI dormancy check"),
    0x00604920: ("SequenceAI__AllocAndConstruct", "cdecl factory: NiAlloc + SequenceAI ctor"),

    # --- BackgroundEditor (3) ---
    0x004954f0: ("BackgroundEditor__SaveDialogHandler", "BackgroundEditor method: SaveDialogHandler"),
    0x004956b0: ("BackgroundEditor__RegisterHandlerNames", "BackgroundEditor: registers CreateDialog/Menu handler name strings"),
    0x004956f0: ("BackgroundEditor__RegisterHandlers", "BackgroundEditor: registers dialog/menu event handlers"),
    0x00495890: ("BackgroundEditor__SaveDialogHandler_B", "BackgroundEditor: handle save dialog event"),

    # --- Editor (3) ---
    0x00496da0: ("Editor__RegisterHandlerNames", "Editor: registers keyboard/dialog handler name strings"),
    0x00496e00: ("Editor__RegisterHandlers", "Editor: registers keyboard/dialog event handlers"),
    0x00496f90: ("Editor__KeyboardHandler", "Editor: handle keyboard event"),
    0x00497bc0: ("Editor__ErrorDialogHandler", "Editor method: ErrorDialogHandler"),

    # --- PlacementEditor (8) ---
    0x0049b310: ("PlacementEditor__EditNameDialogHandler", "PlacementEditor method: EditNameDialogHandler"),
    0x0049b760: ("PlacementEditor__RegisterHandlerNames", "PlacementEditor: registers handler name strings"),
    0x0049b810: ("PlacementEditor__RegisterHandlers", "PlacementEditor: registers event handlers"),
    0x0049bd50: ("PlacementEditor__SaveDialogHandler", "PlacementEditor: handle save dialog event"),
    0x0049bef0: ("PlacementEditor__EditNameDialogHandler_B", "PlacementEditor: handle edit name dialog event"),
    0x0049bf60: ("PlacementEditor__DeleteDialogHandler", "PlacementEditor: handle delete dialog event"),
    0x0049cb10: ("PlacementEditor__SwitchSetsDialogHandler", "PlacementEditor method: SwitchSetsDialogHandler"),
    0x0049e8f0: ("PlacementEditor__HandleAsteroidFieldConfig", "PlacementEditor: handle asteroid field config"),
    0x0049d020: ("PlacementEditor__SaveDialogHandler_B", "PlacementEditor: handle save game dialog event"),

    # --- PlacementObject (8) ---
    0x004a1050: ("PlacementObject__Cast", "PlacementObject method: Cast"),
    0x004a1280: ("PlacementObject__ctor", "PlacementObject method: ctor"),
    0x004a1760: ("PlacementObject__SetModel", "PlacementObject method: SetModel"),
    0x004a1840: ("PlacementObject__SaveObject", "PlacementObject method: SaveObject"),
    0x004a2340: ("PlacementObject__FindContainingSet", "PlacementObject method: FindContainingSet"),
    0x004a2540: ("PlacementObject__GetObjectBySetName", "PlacementObject method: GetObjectBySetName"),
    0x004a3360: ("PlacementObject__SetStatic", "PlacementObject method: SetStatic"),
    0x004a33a0: ("PlacementObject__SetNavPoint", "PlacementObject method: SetNavPoint"),

    # --- PlacementManager (2) ---
    0x004a2be0: ("PlacementManager__SaveToStream", "PlacementManager method: SaveToStream"),
    0x004a2d00: ("PlacementManager__LoadFromStream", "PlacementManager method: LoadFromStream"),

    # --- Waypoint (4) ---
    0x004a4240: ("Waypoint__Cast", "Waypoint method: Cast"),
    0x004a43c0: ("Waypoint__InsertAfterObj", "Waypoint method: InsertAfterObj"),
    0x004a4870: ("Waypoint__RegisterHandlerNames", "Waypoint: registers HandleSetSpeed name string"),
    0x004a4890: ("Waypoint__RegisterHandlers", "Waypoint: registers HandleSetSpeed event handler"),

    # --- DamageHandler (1) ---
    0x004b1ff0: ("DamageHandler__Process", "Per-handler: shield zone check + hull AABB overlap"),

    # --- NiTObjectArray (1) ---
    0x004b20f0: ("NiTObjectArray__GetAt", "NiTObjectArray method: GetAt"),

    # --- ShieldZone (2) ---
    0x004b4b40: ("ShieldZone__Intersect", "Shield geometry intersection (finds hit facing)"),
    0x004b8e80: ("ShieldZone__LookupFacing", "ShieldZone method: LookupFacing"),

    # --- DamageInfo (4) ---
    0x004bbde0: ("DamageInfo__ctor", "DamageInfo constructor: position+radius+type, vtable 0x0088c6c4"),
    0x004bbe90: ("DamageInfo__SetRadius", "Sets +0x14=r, +0x18=r^2, recomputes bounding box"),
    0x004bbeb0: ("DamageInfo__SetDamageType", "Sets +0x1c damage type field"),
    0x004bbec0: ("DamageInfo__ComputeBoundingBox", "center +/- radius -> min/max at +0x20..+0x34"),

    # --- HullAABB (1) ---
    0x004bd9f0: ("HullAABB__Overlap", "AABB intersection test for subsystem damage"),

    # --- ScriptActionCounter (2) ---
    0x004d5090: ("ScriptActionCounter__SaveToStream", "ScriptActionCounter method: SaveToStream"),
    0x004d50b0: ("ScriptActionCounter__LoadFromStream", "ScriptActionCounter method: LoadFromStream"),

    # --- DialogManager (2) ---
    0x004e1be0: ("DialogManager__SaveToStream", "DialogManager method: SaveToStream"),
    0x004e1c30: ("DialogManager__LoadFromStream", "DialogManager method: LoadFromStream"),

    # --- SubsystemProperty (4) ---
    0x004e74e0: ("SubsystemProperty__GetOrientationForward", "SubsystemProperty method: GetOrientationForward"),
    0x004e7510: ("SubsystemProperty__GetOrientationUp", "SubsystemProperty method: GetOrientationUp"),
    0x00579d90: ("SubsystemProperty__InitObject", "SubsystemProperty method: InitObject"),
    0x006923f0: ("SubsystemProperty__Cast", "SubsystemProperty method: Cast"),

    # --- MapWindow (7) ---
    0x004fb8e0: ("MapWindow__RegisterHandlers_Inner", "MapWindow method: RegisterHandlers_Inner"),
    0x004fda10: ("MapWindow__RegisterHandlers_TargetChanged", "MapWindow method: RegisterHandlers_TargetChanged"),
    0x004fe560: ("MapWindow__AddShipHandler", "MapWindow method: AddShipHandler"),
    0x004febc0: ("MapWindow__RegisterHandlerNames", "MapWindow: registers GroupChange/PeriodicUpdate handler name strings"),
    0x004fec30: ("MapWindow__RegisterHandlers", "MapWindow: registers event handlers"),
    0x004fef50: ("MapWindow__UpdatePlayerOrientationGraphics", "MapWindow method: UpdatePlayerOrientationGraphics"),
    0x004ff020: ("MapWindow__RemovePlayerOrientationGraphics", "MapWindow method: RemovePlayerOrientationGraphics"),

    # --- BridgeHandlers (1) ---
    0x004fb8f0: ("BridgeHandlers__RegisterInputHandlers", "BridgeHandlers method: RegisterInputHandlers"),

    # --- CDCheckWindow (2) ---
    0x004fc820: ("CDCheckWindow__RegisterHandlerNames", "CDCheckWindow: registers ShowRetry/RetryCD handler name strings"),
    0x004fc860: ("CDCheckWindow__RegisterHandlers", "CDCheckWindow: registers retry event handlers"),

    # --- CinematicInterfaceHandlers (1) ---
    0x004fda20: ("CinematicInterfaceHandlers__RegisterInputHandlers", "CinematicInterfaceHandlers method: RegisterInputHandlers"),

    # --- CinematicWindow (1) ---
    0x005023c0: ("CinematicWindow__ctor", "CinematicWindow method: ctor"),

    # --- ModalDialogWindow (8) ---
    0x00502fa0: ("ModalDialogWindow__RegisterHandlerNames", "ModalDialogWindow: registers Keyboard/RestoreGraphics/Okay/Cancel/Exit name strings"),
    0x00503030: ("ModalDialogWindow__RegisterHandlers", "ModalDialogWindow: registers keyboard/graphics event handlers"),
    0x00503150: ("ModalDialogWindow__OkayHandler", "ModalDialogWindow method: OkayHandler"),
    0x005031b0: ("ModalDialogWindow__CancelHandler", "ModalDialogWindow method: CancelHandler"),
    0x00503220: ("ModalDialogWindow__ExitGameHandler", "ModalDialogWindow method: ExitGameHandler"),
    0x005032d0: ("ModalDialogWindow__ExitProgramHandler", "ModalDialogWindow method: ExitProgramHandler"),
    0x005033c0: ("ModalDialogWindow__KeyboardHandlerImpl", "ModalDialogWindow method: KeyboardHandlerImpl"),
    0x00503600: ("ModalDialogWindow__MouseHandler", "ModalDialogWindow method: MouseHandler"),

    # --- MultiplayerWindow (5) ---
    0x00504390: ("MultiplayerWindow__ctor", "MultiplayerWindow method: ctor"),
    0x005046b0: ("MultiplayerWindow__RegisterHandlerNames", "MultiplayerWindow: registers all MP message handler name strings"),
    0x00504770: ("MultiplayerWindow__RegisterHandlers", "MultiplayerWindow: registers MP message event handlers"),
    0x00504d30: ("MultiplayerWindow__SettingsHandler_0x00", "MultiplayerWindow method: SettingsHandler_0x00"),
    0x005054b0: ("MultiplayerWindow__UpdateStatusPaneText", "MultiplayerWindow method: UpdateStatusPaneText"),
    0x00506f10: ("MultiplayerWindow__ShowInNotification", "MultiplayerWindow method: ShowInNotification"),

    # --- TacticalControlWindow (4) ---
    0x00509750: ("TacticalControlWindow__ctor", "TacticalControlWindow method: ctor"),
    0x00509b20: ("TacticalControlWindow__RegisterHandlerNames", "TacticalControlWindow: registers HandleRadarToggle name string"),
    0x00509b40: ("TacticalControlWindow__RegisterHandlers", "TacticalControlWindow: registers radar toggle event handler"),
    0x0050a2f0: ("TacticalControlWindow__FindMenu", "TacticalControlWindow method: FindMenu"),

    # --- TopWindow (28) ---
    0x0050b3f0: ("TopWindow__RegisterHandlers_Inner", "TopWindow method: RegisterHandlers_Inner"),
    0x0050c430: ("TopWindow__ctor", "TopWindow method: ctor"),
    0x0050c8b0: ("TopWindow__RegisterHandlerNames", "TopWindow: registers all game handler name strings"),
    0x0050ceb0: ("TopWindow__ResolutionChangeBackHandler", "TopWindow method: ResolutionChangeBackHandler"),
    0x0050d150: ("TopWindow__KeyboardHandler", "TopWindow method: KeyboardHandler"),
    0x0050d2e0: ("TopWindow__ToggleConsoleHandler", "TopWindow method: ToggleConsoleHandler"),
    0x0050d310: ("TopWindow__ToggleOptionsHandler", "TopWindow method: ToggleOptionsHandler"),
    0x0050d340: ("TopWindow__ToggleEditHandler", "TopWindow method: ToggleEditHandler"),
    0x0050d370: ("TopWindow__ToggleBridgeAndTacticalHandler", "TopWindow method: ToggleBridgeAndTacticalHandler"),
    0x0050d400: ("TopWindow__TabFocusHandler", "TopWindow method: TabFocusHandler"),
    0x0050d420: ("TopWindow__PrintScreenHandler", "TopWindow method: PrintScreenHandler"),
    0x0050d440: ("TopWindow__MouseHandler", "TopWindow method: MouseHandler"),
    0x0050d4d0: ("TopWindow__ToggleMapWindow", "TopWindow method: ToggleMapWindow"),
    0x0050d550: ("TopWindow__ShowBadConnectionText", "TopWindow method: ShowBadConnectionText"),
    0x0050d620: ("TopWindow__ToggleOptionsMenu", "TopWindow method: ToggleOptionsMenu"),
    0x0050d7e0: ("TopWindow__ToggleConsole", "TopWindow method: ToggleConsole"),
    0x0050d830: ("TopWindow__ToggleCinematicWindow", "TopWindow method: ToggleCinematicWindow"),
    0x0050d890: ("TopWindow__ToggleEditMode", "TopWindow method: ToggleEditMode"),
    0x0050d8d0: ("TopWindow__ForceBridgeVisible", "TopWindow method: ForceBridgeVisible"),
    0x0050d980: ("TopWindow__ForceTacticalVisible", "TopWindow method: ForceTacticalVisible"),
    0x0050da30: ("TopWindow__ToggleBridgeAndTactical", "TopWindow method: ToggleBridgeAndTactical"),
    0x0050dea0: ("TopWindow__AbortCutscene", "TopWindow method: AbortCutscene"),
    0x0050e070: ("TopWindow__FadeIn", "TopWindow method: FadeIn"),
    0x0050e0e0: ("TopWindow__AbortFade", "TopWindow method: AbortFade"),
    0x0050e1b0: ("TopWindow__FindMainWindow", "TopWindow method: FindMainWindow"),
    0x0050e220: ("TopWindow__Initialize", "TopWindow method: Initialize"),
    0x0050e300: ("TopWindow__UpdateNotificationObject", "TopWindow method: UpdateNotificationObject"),
    0x0050e420: ("TopWindow__UpdateFade", "TopWindow method: UpdateFade"),

    # --- TacticalInterfaceHandlers (1) ---
    0x0050b400: ("TacticalInterfaceHandlers__RegisterInputHandlers", "TacticalInterfaceHandlers method: RegisterInputHandlers"),

    # --- TacticalWindow (1) ---
    0x0050b6b0: ("TacticalWindow__SpaceCameraRotation", "TacticalWindow method: SpaceCameraRotation"),

    # --- OptionsWindow (1) ---
    0x0050ca50: ("OptionsWindow__RegisterHandlers", "OptionsWindow method: RegisterHandlers"),

    # --- MainWindow (2) ---
    0x0050e920: ("MainWindow__ctor", "MainWindow method: ctor"),
    0x0050eb20: ("MainWindow__SetupVisibility", "MainWindow method: SetupVisibility"),

    # --- ConsoleWindow (1) ---
    0x0050ebc0: ("ConsoleWindow__ctor", "ConsoleWindow method: ctor"),

    # --- NamedReticleWindow (5) ---
    0x0050fea0: ("NamedReticleWindow__Constructor", "Writes vtable 0x0088f1e8, registers 3 event handlers"),
    0x00510310: ("NamedReticleWindow__RegisterHandlerNames", "NamedReticleWindow: registers handler name strings (HandleNameChange/ObjectGroupChanged/ShipIdentified)"),
    0x00510870: ("NamedReticleWindow__HandleShipIdentified", "NamedReticleWindow method: HandleShipIdentified"),
    # --- PlayerReticleWindow (2) ---
    0x00511d80: ("PlayerReticleWindow__RegisterHandlerNames", "PlayerReticleWindow: stub RegisterHandlerNames"),
    0x00511d90: ("PlayerReticleWindow__RegisterHandlers", "PlayerReticleWindow: stub RegisterHandlers"),

    # --- ReticleManagerWindow (4) ---
    0x00513e20: ("ReticleManagerWindow__ShipDestroyedHandler", "ReticleManagerWindow method: ShipDestroyedHandler"),
    0x00513f00: ("ReticleManagerWindow__RegisterHandlerNames", "ReticleManagerWindow: registers ShipDestroyedHandler name string"),
    0x00513f20: ("ReticleManagerWindow__RegisterHandlers", "ReticleManagerWindow: stub RegisterHandlers"),

    # --- ReticleWindow (2) ---
    0x00515280: ("ReticleWindow__RegisterHandlerNames", "ReticleWindow: stub RegisterHandlerNames"),
    0x00515290: ("ReticleWindow__RegisterHandlers", "ReticleWindow: stub RegisterHandlers"),

    # --- SortedRegionMenu (3) ---
    0x00517df0: ("SortedRegionMenu__RegisterHandlerNames", "SortedRegionMenu: registers SetPlayer/PlayerShipMoved handler name strings"),
    0x00517e20: ("SortedRegionMenu__PlayerShipMovedHandler", "SortedRegionMenu method: PlayerShipMovedHandler"),
    0x00517f90: ("SortedRegionMenu__PlayerShipMovedHandler_B", "SortedRegionMenu: handle player ship position changed"),

    # --- STButton (10) ---
    0x00518bb0: ("STButton__Cast", "STButton method: Cast"),
    0x00518be0: ("STButton__ctor", "STButton method: ctor"),
    0x00518e70: ("STButton__ctorW", "STButton method: ctorW"),
    0x005194e0: ("STButton__SetName", "STButton method: SetName"),
    0x00519550: ("STButton__GetName", "STButton method: GetName"),
    0x005196b0: ("STButton__UpdateColorScheme", "STButton method: UpdateColorScheme"),
    0x00519e00: ("STButton__SetColor", "STButton method: SetColor"),
    0x00519f30: ("STButton__SetColorBasedOnFlags", "STButton method: SetColorBasedOnFlags"),
    0x0051a2c0: ("STButton__SetChosen", "STButton method: SetChosen"),
    0x0051a5b0: ("STButton__GetContainingWindow", "STButton method: GetContainingWindow"),

    # --- STCharacterMenu (4) ---
    0x0051b4a0: ("STCharacterMenu__ctor", "STCharacterMenu method: ctor"),
    0x0051b5c0: ("STCharacterMenu__ctorW", "STCharacterMenu method: ctorW"),
    0x0051b5f0: ("STCharacterMenu__RegisterHandlerNames", "STCharacterMenu: registers ButtonClickedHandler name string"),
    0x0051b610: ("STCharacterMenu__RegisterHandlers", "STCharacterMenu: registers ButtonClicked event handler"),

    # --- STMarker (1) ---
    0x0051c060: ("STMarker__Cast", "STMarker method: Cast"),

    # --- STFileMenu (3) ---
    0x005210c0: ("STFileMenu__RegisterHandlerNames", "STFileMenu: registers HandleKeyboard name string"),
    0x005210e0: ("STFileMenu__RegisterHandlers", "STFileMenu: registers keyboard event handler"),
    # --- STFileListWindow (2) ---
    0x0051f720: ("STFileListWindow__RegisterHandlerNames", "STFileListWindow: stub RegisterHandlerNames"),
    0x0051f730: ("STFileListWindow__RegisterHandlers", "STFileListWindow: stub RegisterHandlers"),

    # --- STLoadDialog (5) ---
    0x00523f70: ("STLoadDialog__RegisterHandlerNames", "STLoadDialog: registers handler name strings"),
    0x00523fd0: ("STLoadDialog__RegisterHandlers", "STLoadDialog: registers event handlers"),
    0x005243f0: ("STLoadDialog__HandleFileSelection", "STLoadDialog method: HandleFileSelection"),
    0x005244c0: ("STLoadDialog__HandleLoadButton", "STLoadDialog method: HandleLoadButton"),
    0x00524b00: ("STLoadDialog__KeyboardHandler", "STLoadDialog method: KeyboardHandler"),

    # --- STMenu (8) ---
    0x00525560: ("STMenu__Cast", "STMenu method: Cast"),
    0x005255b0: ("STMenu__ctorW", "STMenu method: ctorW"),
    0x00525750: ("STMenu__ctor", "STMenu method: ctor"),
    0x00525b50: ("STMenu__RegisterHandlerNames", "STMenu: registers HandleSelectOption/TacticalMenu name strings"),
    0x00525b90: ("STMenu__RegisterHandlers", "STMenu: registers select-option event handler"),
    0x00525c00: ("STMenu__GetContainingWindow", "STMenu method: GetContainingWindow"),
    0x00525ce0: ("STMenu__ForceUpdate", "STMenu method: ForceUpdate"),
    0x00526f80: ("STMenu__SetChosen", "STMenu method: SetChosen"),

    # --- STMissionLog (2) ---
    0x00528e10: ("STMissionLog__RegisterHandlerNames", "STMissionLog: registers handler name strings"),
    0x00528e50: ("STMissionLog__RegisterHandlers", "STMissionLog: registers event handlers"),

    # --- STNumericBar (2) ---
    0x0052a730: ("STNumericBar__RegisterHandlerNames", "STNumericBar: registers handler name strings"),
    0x0052a790: ("STNumericBar__RegisterHandlers", "STNumericBar: registers event handlers"),

    # --- STRepairButton (3) ---
    0x0052c9c0: ("STRepairButton__RegisterHandlerNames", "STRepairButton: registers HandleSubsystemStateChanged name string"),
    0x0052c9e0: ("STRepairButton__RegisterHandlers", "STRepairButton: stub RegisterHandlers"),
    0x0052c9f0: ("STRepairButton__HandleSubsystemStateChanged", "STRepairButton: handle subsystem state change event"),

    # --- STSaveDialog (3) ---
    0x0052f760: ("STSaveDialog__RegisterHandlerNames_Simple", "STSaveDialog: registers handler name strings (simple variant)"),
    0x0052f7c0: ("STSaveDialog__RegisterHandlers", "STSaveDialog: registers event handlers"),
    0x0052f800: ("STSaveDialog__RegisterHandlerNames", "STSaveDialog: registers extended handler name strings"),

    # --- TGWindow (2) ---
    0x00530d50: ("TGWindow__Cast", "TGWindow method: Cast"),
    0x0073eb30: ("TGWindow__SetIndent", "TGWindow method: SetIndent"),

    # --- STStylizedWindow (13) ---
    0x00531220: ("STStylizedWindow__SetUseFocusGlass", "STStylizedWindow method: SetUseFocusGlass"),
    0x005312c0: ("STStylizedWindow__InteriorChangedSize", "STStylizedWindow method: InteriorChangedSize"),
    0x00531810: ("STStylizedWindow__SetTitleBarThickness", "STStylizedWindow method: SetTitleBarThickness"),
    0x00531880: ("STStylizedWindow__SetFixedSize", "STStylizedWindow method: SetFixedSize"),
    0x005318f0: ("STStylizedWindow__SetMinimized", "STStylizedWindow method: SetMinimized"),
    0x00531950: ("STStylizedWindow__SetNotMinimized", "STStylizedWindow method: SetNotMinimized"),
    0x005319c0: ("STStylizedWindow__SetUseScrolling", "STStylizedWindow method: SetUseScrolling"),
    0x00531a10: ("STStylizedWindow__SetMaximumSize", "STStylizedWindow method: SetMaximumSize"),
    0x00531de0: ("STStylizedWindow__PeriodicScrollUp", "STStylizedWindow method: PeriodicScrollUp"),
    0x00531e20: ("STStylizedWindow__PeriodicScrollDown", "STStylizedWindow method: PeriodicScrollDown"),
    0x00531fa0: ("STStylizedWindow__RegisterHandlerNames", "STStylizedWindow: registers handler name strings"),
    0x00532000: ("STStylizedWindow__RegisterHandlers", "STStylizedWindow: registers event handlers"),
    0x0072ed70: ("STStylizedWindow__GetExteriorPane", "STStylizedWindow method: GetExteriorPane"),

    # --- STRadioGroup (1) ---
    0x00532f20: ("STRadioGroup__Cast", "STRadioGroup method: Cast"),

    # --- STSubPane (2) ---
    0x005331e0: ("STSubPane__RegisterHandlerNames", "STSubPane: registers handler name strings"),
    0x00533210: ("STSubPane__RegisterHandlers", "STSubPane: registers event handlers"),

    # --- STToggle (10) ---
    0x00533a00: ("STToggle__GetPrimaryCaption", "STToggle method: GetPrimaryCaption"),
    0x0053b5a0: ("STToggle__Cast", "STToggle method: Cast"),
    0x0053b5d0: ("STToggle__ctor", "STToggle method: ctor"),
    0x0053b840: ("STToggle__ctorW", "STToggle method: ctorW"),
    0x0053b9a0: ("STToggle__ctorUnsizedW", "STToggle method: ctorUnsizedW"),
    0x0053be20: ("STToggle__SetState", "STToggle method: SetState"),
    0x0053bfe0: ("STToggle__RegisterHandlerNames", "STToggle: registers keyboard handler name string"),
    0x0053c000: ("STToggle__RegisterHandlers", "STToggle: registers keyboard event handler"),
    0x0054a080: ("STToggle__SetStateValue", "STToggle method: SetStateValue"),
    0x0062bc20: ("STToggle__SetPrimaryCaptionW", "STToggle method: SetPrimaryCaptionW"),

    # --- STSubsystemMenu (3) ---
    0x00535170: ("STSubsystemMenu__ctor", "STSubsystemMenu: constructor (was misnamed RegisterHandlers)"),
    0x00535760: ("STSubsystemMenu__RegisterHandlerNames", "STSubsystemMenu: registers handler name strings"),
    0x005357d0: ("STSubsystemMenu__RegisterHandlers", "STSubsystemMenu: registers TargetButtonClicked/KeyboardHandler event handlers"),

    # --- STComponentMenu (2) ---
    0x00536960: ("STComponentMenu__RegisterHandlerNames", "STComponentMenu: registers handler name strings"),
    0x00536990: ("STComponentMenu__RegisterHandlers", "STComponentMenu: registers event handlers"),

    # --- STTargetMenu (9) ---
    0x00537be0: ("STTargetMenu__ctor", "STTargetMenu: constructor (was misnamed RegisterHandlers_B)"),
    0x00538170: ("STTargetMenu__RegisterHandlerNames", "STTargetMenu: registers handler name strings"),
    0x00538240: ("STTargetMenu__TargetButtonClicked", "STTargetMenu method: TargetButtonClicked"),
    0x00538280: ("STTargetMenu__ObjectEnteredSet", "STTargetMenu method: ObjectEnteredSet"),
    0x005382d0: ("STTargetMenu__ObjectExitedSet", "STTargetMenu method: ObjectExitedSet"),
    0x005383c0: ("STTargetMenu__ObjectChangedGroup", "STTargetMenu method: ObjectChangedGroup"),
    0x00538560: ("STTargetMenu__TargetedSubsystemChanged", "STTargetMenu method: TargetedSubsystemChanged"),
    0x00538590: ("STTargetMenu__RegisterHandlers", "STTargetMenu: registers event handlers (TargetButtonClicked)"),
    0x00538690: ("STTargetMenu__TargetChanged", "STTargetMenu method: TargetChanged"),

    # --- STTopLevelMenu (2) ---
    0x0053d610: ("STTopLevelMenu__RegisterHandlerNames", "STTopLevelMenu: registers handler name strings"),
    0x0053d650: ("STTopLevelMenu__RegisterHandlers", "STTopLevelMenu: registers event handlers"),

    # --- STWarpButton (2) ---
    0x0053efa0: ("STWarpButton__RegisterHandlerNames", "STWarpButton: registers HandleWarpEvent/ExitedWarp name strings"),
    0x0053efd0: ("STWarpButton__RegisterHandlers", "STWarpButton: registers warp event handlers"),

    # --- DamageIcon (4) ---
    0x005407a0: ("DamageIcon__RegisterHandlerNames", "DamageIcon: registers HandleExpire/Blink name strings"),
    0x005407d0: ("DamageIcon__HandleExpire", "DamageIcon method: HandleExpire (periodic expire timer)"),
    0x005408b0: ("DamageIcon__ResetPosition", "DamageIcon method: ResetPosition"),
    0x00540870: ("DamageIcon__HandleBlinkEvent", "DamageIcon: handle blink timer event"),
    0x005408c0: ("DamageIcon__RegisterHandlers", "DamageIcon: registers HandleBlink event handler"),

    # --- DamageDisplay (8) ---
    0x00540e90: ("DamageDisplay__ctor", "DamageDisplay method: ctor"),
    0x00541090: ("DamageDisplay__GetShip", "DamageDisplay method: GetShip"),
    0x005410b0: ("DamageDisplay__HandleSubsystemEvents", "DamageDisplay method: HandleSubsystemEvents"),
    0x005411e0: ("DamageDisplay__HandleSubsystemEvents_B", "DamageDisplay method: HandleSubsystemEvents_B"),
    0x005412d0: ("DamageDisplay__RepositionUI", "DamageDisplay method: RepositionUI"),
    0x00541310: ("DamageDisplay__RegisterHandlerNames", "DamageDisplay: registers HandleDamageDisplayRefresh name string"),
    0x005413f0: ("DamageDisplay__HandleDamageDisplayRefreshEvent", "DamageDisplay: handle refresh event"),
    0x00541340: ("DamageDisplay__RegisterHandlers", "DamageDisplay: registers refresh event handler"),

    # --- RadarDisplay (4) ---
    0x00542310: ("RadarDisplay__ctor", "RadarDisplay method: ctor"),
    0x005424c0: ("RadarDisplay__RegisterHandlerNames", "RadarDisplay: registers MouseHandler name string"),
    0x00542500: ("RadarDisplay__RegisterHandlers", "RadarDisplay: registers mouse event handler"),
    0x00542650: ("RadarDisplay__SetColorBasedOnFlags", "RadarDisplay method: SetColorBasedOnFlags"),

    # --- RadarScope (4) ---
    0x00543670: ("RadarScope__SetObjectUpdate", "RadarScope method: SetObjectUpdate"),
    0x00543a30: ("RadarScope__RegisterHandlerNames", "RadarScope: registers SetPlayer/BracketExpire handler name strings"),
    0x00543aa0: ("RadarScope__RegisterHandlers", "RadarScope: registers event handlers"),
    0x00543dc0: ("RadarScope__PlayerDamagedHandler", "RadarScope method: PlayerDamagedHandler"),

    # --- ShieldsDisplay (4) ---
    0x005457e0: ("ShieldsDisplay__ctor", "ShieldsDisplay method: ctor"),
    0x00545970: ("ShieldsDisplay__Update", "ShieldsDisplay method: Update"),
    0x00545be0: ("ShieldsDisplay__RegisterHandlerNames", "ShieldsDisplay: registers Update/HandleSetPlayer name strings"),
    0x00545c10: ("ShieldsDisplay__RegisterHandlers", "ShieldsDisplay: stub RegisterHandlers"),

    # --- ShipDisplay (5) ---
    0x00546a50: ("ShipDisplay__ctor", "ShipDisplay method: ctor"),
    0x00546cd0: ("ShipDisplay__HandleShipDestroyed", "ShipDisplay method: HandleShipDestroyed"),
    0x00546dc0: ("ShipDisplay__HandleChangeTarget", "ShipDisplay method: HandleChangeTarget"),
    0x00546df0: ("ShipDisplay__RegisterHandlerNames", "ShipDisplay: registers HandleShipDestroyed/ChangeTarget/HandleSetPlayer name strings"),
    0x00546e30: ("ShipDisplay__RegisterHandlers", "ShipDisplay: stub RegisterHandlers"),

    # --- TacWeaponsCtrl (9) ---
    0x00547b10: ("TacWeaponsCtrl__ctor", "TacWeaponsCtrl: constructor (was misnamed RegisterHandlers_B)"),
    0x00547e50: ("TacWeaponsCtrl__BuildUI", "TacWeaponsCtrl: builds weapon UI layout (was misnamed RegisterHandlers)"),
    0x00549520: ("TacWeaponsCtrl__RegisterHandlerNames", "TacWeaponsCtrl: registers handler name strings"),
    0x00549640: ("TacWeaponsCtrl__RegisterHandlers", "TacWeaponsCtrl: registers PhaserSetting/TorpType/CloakToggle event handlers"),
    0x00549830: ("TacWeaponsCtrl__TorpedoTypeToggle", "TacWeaponsCtrl: toggle torpedo type"),
    0x0054a1a0: ("TacWeaponsCtrl__HandleSubsystemDisabled", "TacWeaponsCtrl: handle subsystem disabled event"),
    0x0054a260: ("TacWeaponsCtrl__HandleSubsystemOperational", "TacWeaponsCtrl: handle subsystem operational event"),
    0x00549a30: ("TacWeaponsCtrl__HandleCloakToggleRefresh", "TacWeaponsCtrl: handle cloak toggle refresh event"),
    0x0054a320: ("TacWeaponsCtrl__HandleTractorBeamToggle", "TacWeaponsCtrl: handle tractor beam toggle event"),

    # --- WeaponsDisplay (7) ---
    0x0054aea0: ("WeaponsDisplay__ctor", "WeaponsDisplay method: ctor"),
    0x0054b120: ("WeaponsDisplay__RegisterHandlerNames", "WeaponsDisplay: registers Update/HandleFiringChain/HandleSetPlayer name strings"),
    0x0054b160: ("WeaponsDisplay__RegisterHandlers", "WeaponsDisplay: registers event handlers"),
    0x0054ba30: ("WeaponsDisplay__UpdateHandler", "WeaponsDisplay: handle periodic update event"),
    0x0054b2f0: ("WeaponsDisplay__Update_Impl", "WeaponsDisplay method: Update_Impl"),
    0x0054b6e0: ("WeaponsDisplay__Update_Impl_B", "WeaponsDisplay method: Update_Impl_B"),

    # --- EngPowerCtrl (6) ---
    0x0054d340: ("EngPowerCtrl__RegisterHandlerNames", "EngPowerCtrl: registers handler name strings"),
    0x0054d3b0: ("EngPowerCtrl__RegisterHandlers", "EngPowerCtrl: registers event handlers"),
    0x0054dde0: ("EngPowerCtrl__HandlePowerChange", "UI power slider handler (local only)"),
    0x0054e1f0: ("EngPowerCtrl__HandlePeriodicRefresh", "EngPowerCtrl method: HandlePeriodicRefresh"),
    0x0054e2b0: ("EngPowerCtrl__HandleKeyboard", "EngPowerCtrl method: HandleKeyboard"),
    0x0054e690: ("EngPowerCtrl__PostPowerChangedEvent", "EngPowerCtrl method: PostPowerChangedEvent"),

    # --- InterfaceModule (6) ---
    0x0054d940: ("InterfaceModule__CreateOverridePane", "Create UI override pane for handler routing"),
    0x005559c0: ("InterfaceModule__RegisterUIHandlers", "InterfaceModule method: RegisterUIHandlers"),
    0x00559130: ("InterfaceModule__RegisterHandlerNames", "InterfaceModule: master RegisterHandlerNames dispatcher for all UI classes"),
    0x00559270: ("InterfaceModule__RegisterHandlers", "InterfaceModule: master RegisterHandlers dispatcher for all UI classes"),
    0x00559360: ("InterfaceModule__SaveToStream", "InterfaceModule method: SaveToStream"),
    0x00559380: ("InterfaceModule__LoadFromStream", "InterfaceModule method: LoadFromStream"),

    # --- STSpacer (2) ---
    0x00539c20: ("STSpacer__RegisterHandlerNames", "STSpacer: stub RegisterHandlerNames"),
    0x00539c30: ("STSpacer__RegisterHandlers", "STSpacer: stub RegisterHandlers"),

    # --- EngRepairPane (11) ---
    0x00550770: ("EngRepairPane__Constructor", "Writes vtable 0x008927f4, loads 'Bridge Menus.tgl'"),
    0x00550e60: ("EngRepairPane__RegisterHandlerNames", "EngRepairPane: registers handler name strings"),
    0x00550ea0: ("EngRepairPane__RegisterHandlers", "EngRepairPane: registers event handlers"),
    0x00550ef0: ("EngRepairPane__SetRepairSubsystem", "EngRepairPane method: SetRepairSubsystem"),
    0x00551230: ("EngRepairPane__ClearAll", "EngRepairPane method: ClearAll"),
    0x005512e0: ("EngRepairPane__Update", "EngRepairPane method: Update"),
    0x00551870: ("EngRepairPane__ShowDestroyed", "EngRepairPane method: ShowDestroyed"),
    0x00551990: ("EngRepairPane__RefreshRepairItem", "EngRepairPane method: RefreshRepairItem"),
    0x00551cc0: ("EngRepairPane__ResizeToContents", "EngRepairPane method: ResizeToContents"),
    0x00551e00: ("EngRepairPane__HandleKeyboard", "EngRepairPane method: HandleKeyboard"),
    0x00551ff0: ("EngRepairPane__HandleSetPlayer", "EngRepairPane method: HandleSetPlayer"),

    # --- GraphicsMenu (4) ---
    0x00553a00: ("GraphicsMenu__RegisterHandlerNames", "GraphicsMenu: registers DeviceChange/ResolutionChange/RefreshRate name strings"),
    0x00553a40: ("GraphicsMenu__RegisterHandlers", "GraphicsMenu: registers device change event handler"),
    0x00553c70: ("GraphicsMenu__DeviceChangeHandler", "GraphicsMenu: handle device change event"),
    # PowerDisplay (2)
    0x0054fb10: ("PowerDisplay__RegisterHandlerNames", "PowerDisplay: stub RegisterHandlerNames"),
    0x0054fb20: ("PowerDisplay__RegisterHandlers", "PowerDisplay: stub RegisterHandlers"),

    # --- CloakingSubsystem (10) ---
    0x0055e220: ("CloakingSubsystem__GetProperty", "CloakingSubsystem method: GetProperty"),
    0x0055e280: ("CloakingSubsystem__Cast", "CloakingSubsystem method: Cast"),
    0x0055e430: ("CloakingSubsystem__dtor", "CloakingSubsystem method: dtor"),
    0x0055e4a0: ("CloakingSubsystem__RegisterHandlerNames", "CloakingSubsystem: registers StartCloaking/StopCloaking name strings"),
    0x0055e4d0: ("CloakingSubsystem__RegisterHandlers", "CloakingSubsystem: registers start/stop cloak event handlers"),
    0x0055f110: ("CloakingSubsystem__CloakShieldHandler", "CloakingSubsystem method: CloakShieldHandler"),
    0x0055f360: ("CloakingSubsystem__StartCloaking", "Begin cloak sequence (sets cloakObj+0xAD=1)"),
    0x0055f380: ("CloakingSubsystem__StopCloaking", "CloakingSubsystem method: StopCloaking"),
    0x0055f3e0: ("CloakingSubsystem__InstantCloak", "SWIG target: instant cloak activation"),
    0x0055f560: ("CloakingSubsystem__InstantDecloak", "CloakingSubsystem method: InstantDecloak"),

    # --- HullClass (1) ---
    0x00560440: ("HullClass__Cast", "HullClass method: Cast"),

    # --- PowerSubsystem (9) ---
    0x00560470: ("PowerSubsystem__Constructor", "Reactor/warp core constructor"),
    0x00560560: ("PowerSubsystem__dtor", "PowerSubsystem method: dtor"),
    0x00563470: ("PowerSubsystem__Cast", "PowerSubsystem method: Cast"),
    0x005634a0: ("PowerSubsystem__GetProperty", "PowerSubsystem method: GetProperty"),
    0x005634b0: ("PowerSubsystem__GetPowerOutput", "PowerSubsystem method: GetPowerOutput"),
    0x005634c0: ("PowerSubsystem__GetMainBatteryLimit", "PowerSubsystem method: GetMainBatteryLimit"),
    0x005634d0: ("PowerSubsystem__GetBackupBatteryLimit", "PowerSubsystem method: GetBackupBatteryLimit"),
    0x005634f0: ("PowerSubsystem__GetMainConduitCapacity_Scaled", "PowerSubsystem method: GetMainConduitCapacity_Scaled"),
    0x00563520: ("PowerSubsystem__GetBackupConduitCapacity", "PowerSubsystem method: GetBackupConduitCapacity"),

    # --- Subsystem (6) ---
    0x00560fc0: ("Subsystem__GetProperty", "Returns +0x18 SubsystemProperty pointer"),
    0x0056b940: ("Subsystem__GetRadius", "Reads property+0x44 radius float"),
    0x0056c340: ("Subsystem__IsActive", "Reads property+0x25 active flag via +0x18"),
    0x0056c570: ("Subsystem__GetChild", "Array bounds check, returns child at index from +0x20"),
    0x00570b20: ("Subsystem__AsPhaserSubsystem", "IsA(0x802C) cast check"),
    0x00583f60: ("Subsystem__AsWeaponSystem", "IsA(0x801D) cast check"),

    # --- ImpulseEngineSubsystem (5) ---
    0x00561020: ("ImpulseEngineSubsystem__Cast", "ImpulseEngineSubsystem method: Cast"),
    0x00561050: ("ImpulseEngineSubsystem__ctor", "Impulse engine subsystem constructor"),
    0x00561170: ("ImpulseEngineSubsystem__dtor", "ImpulseEngineSubsystem method: dtor"),
    0x00561230: ("ImpulseEngineSubsystem__GetEffectiveAcceleration", "Same pattern for acceleration"),
    0x00561330: ("ImpulseEngineSubsystem__GetEffectiveSpeed", "Computes max speed from child health + power efficiency"),

    # --- PoweredSubsystem (12) ---
    0x00562210: ("PoweredSubsystem__Cast", "PoweredSubsystem method: Cast"),
    0x00562240: ("PoweredSubsystem__ctor", "Powered subsystem base constructor"),
    0x00562380: ("PoweredSubsystem__dtor", "PoweredSubsystem method: dtor"),
    0x005623c0: ("PoweredSubsystem__SetPowerSource", "Delegates to PoweredMaster__SetPowerSource"),
    0x005623d0: ("PoweredSubsystem__GetNormalPowerWanted", "PoweredSubsystem method: GetNormalPowerWanted"),
    0x00562430: ("PoweredSubsystem__SetPowerPercentageWanted", "Set power allocation (0.0-1.25)"),
    0x00562470: ("PoweredSubsystem__Update", "Per-consumer power draw (every frame)"),
    0x00562710: ("PoweredSubsystem__RegisterHandlerNames", "PoweredSubsystem: registers StateChangedHandler name string"),
    0x00562730: ("PoweredSubsystem__RegisterHandlers", "PoweredSubsystem: registers StateChanged event handler"),
    0x00562960: ("PoweredSubsystem__WriteState", "Powered subsystem: condition + power pct"),
    0x005629d0: ("PoweredSubsystem__ReadState", "Powered subsystem: deserialize condition + power"),
    0x005822d0: ("PoweredSubsystem__GetEfficiency", "Returns received/wanted power ratio, clamped"),

    # --- RepairSubsystem (12) ---
    0x00564fe0: ("RepairSubsystem__GetProperty", "Returns repair subsystem property pointer"),
    0x00565060: ("RepairSubsystem__Cast", "RepairSubsystem method: Cast"),
    0x00565090: ("RepairSubsystem__Constructor", "Repair system constructor (vtable 0x00892e24)"),
    0x005651c0: ("RepairSubsystem__Destructor", "RepairSubsystem method: Destructor"),
    0x00565520: ("RepairSubsystem__AddSubsystem", "Add subsystem to repair queue"),
    0x00565890: ("RepairSubsystem__IsBeingRepaired", "RepairSubsystem method: IsBeingRepaired"),
    0x00565900: ("RepairSubsystem__AddToRepairList_MP", "Add to repair list (multiplayer-safe)"),
    0x00565980: ("RepairSubsystem__HandleRepairCompleted", "RepairSubsystem method: HandleRepairCompleted"),
    0x00565a10: ("RepairSubsystem__HandleSubsystemRebuilt", "RepairSubsystem method: HandleSubsystemRebuilt"),
    0x00565d30: ("RepairSubsystem__UpdateRepairPane", "RepairSubsystem method: UpdateRepairPane"),
    0x00565d40: ("RepairSubsystem__RegisterHandlerNames", "RepairSubsystem: registers SetPlayer/AddToRepairList/IncreasePriority name strings"),
    0x00565dd0: ("RepairSubsystem__RegisterHandlers", "RepairSubsystem: registers repair event handlers"),

    # --- SensorSubsystem (12) ---
    0x00566c90: ("SensorSubsystem__Cast", "SensorSubsystem method: Cast"),
    0x00566e50: ("SensorSubsystem__dtor", "SensorSubsystem method: dtor"),
    0x00566f50: ("SensorSubsystem__RegisterHandlerNames", "SensorSubsystem: registers SetPlayer/EnterSet/ExitSet/ObjectExploding/ObjectTargeted/PeriodicScan name strings"),
    0x00566fd0: ("SensorSubsystem__RegisterHandlers", "SensorSubsystem: registers SetPlayer/PeriodicScan event handlers"),
    0x00567190: ("SensorSubsystem__GetSensorRange", "SWIG target: computes effective range from efficiency"),
    0x005671d0: ("SensorSubsystem__IsObjectVisible", "SensorSubsystem method: IsObjectVisible"),
    0x00567440: ("SensorSubsystem__IsObjectNear", "SensorSubsystem method: IsObjectNear"),
    0x00567640: ("SensorSubsystem__IsObjectFar", "SensorSubsystem method: IsObjectFar"),
    0x00567830: ("SensorSubsystem__IsObjectKnown", "SensorSubsystem method: IsObjectKnown"),
    0x00567880: ("SensorSubsystem__IdentifyObject", "SWIG target: force-identify target object"),
    0x005678b0: ("SensorSubsystem__ForceObjectIdentified", "SensorSubsystem method: ForceObjectIdentified"),
    0x00569140: ("SensorSubsystem__LoadSensorData", "SensorSubsystem method: LoadSensorData"),

    # --- SubsystemPropertyManager (2) ---
    0x00568320: ("SubsystemPropertyManager__SaveToStream", "SubsystemPropertyManager method: SaveToStream"),
    0x00568340: ("SubsystemPropertyManager__LoadFromStream", "SubsystemPropertyManager method: LoadFromStream"),

    # --- ShieldClass (3) ---
    0x00569fd0: ("ShieldClass__Cast", "ShieldClass method: Cast"),
    0x005af3b0: ("ShieldClass__GetShieldGlowColor", "ShieldClass method: GetShieldGlowColor"),
    0x0056a210: ("ShieldClass__RegisterHandlers", "ShieldClass: registers HandleSetShieldState event handler"),

    # --- ShieldSubsystem (12) ---
    0x0056a000: ("ShieldSubsystem__Constructor", "ShieldSubsystem method: Constructor"),
    0x0056a190: ("ShieldSubsystem__Destructor", "ShieldSubsystem method: Destructor"),
    0x0056a1f0: ("ShieldSubsystem__RegisterHandlerNames", "ShieldSubsystem: registers HandleSetShieldState name string"),
    0x0056a420: ("ShieldSubsystem__BoostShield", "Per-facing shield recharge"),
    0x0056a540: ("ShieldSubsystem__GetShieldPercentage", "ShieldSubsystem method: GetShieldPercentage"),
    0x0056a5c0: ("ShieldSubsystem__SetCurShields", "Set current shield HP for a facing"),
    0x0056a620: ("ShieldSubsystem__IsShieldBreached", "ShieldSubsystem method: IsShieldBreached"),
    0x0056a670: ("ShieldSubsystem__IsAnyShieldBreached", "ShieldSubsystem method: IsAnyShieldBreached"),
    0x0056a690: ("ShieldSubsystem__GetShieldFacingFromRay", "Ray-ellipsoid intersection test for directed weapon hits"),
    0x0056a8d0: ("ShieldSubsystem__NormalToFacing", "Determines which of 6 shield facings a point hits"),
    0x0056ae10: ("ShieldSubsystem__ReadStream", "ShieldSubsystem method: ReadStream"),
    0x0056bde0: ("ShieldSubsystem__ScheduleShieldEvents", "ShieldSubsystem method: ScheduleShieldEvents"),

    # --- ShieldProperty (6) ---
    0x0056b960: ("ShieldProperty__GetCurrentPower", "ShieldProperty method: GetCurrentPower"),
    0x0056b970: ("ShieldProperty__Constructor", "ShieldProperty method: Constructor"),
    0x0056bc50: ("ShieldProperty__SetPower", "ShieldProperty method: SetPower"),
    0x005af3d0: ("ShieldProperty__GetShieldGlowColor", "ShieldProperty method: GetShieldGlowColor"),
    0x00643030: ("ShieldProperty__SetShieldGlowColor", "ShieldProperty method: SetShieldGlowColor"),
    0x006900f0: ("ShieldProperty__Cast", "ShieldProperty method: Cast"),

    # --- ShipSubsystem (12) ---
    0x0056bb90: ("ShipSubsystem__dtor", "ShipSubsystem method: dtor"),
    0x0056bc60: ("ShipSubsystem__Update", "Base subsystem update: condition tracking"),
    0x0056bd90: ("ShipSubsystem__Repair", "Apply repair HP to a subsystem"),
    0x0056c310: ("ShipSubsystem__GetMaxHP", "Returns subsystem max condition (max HP)"),
    0x0056c330: ("ShipSubsystem__IsDead", "ShipSubsystem method: IsDead"),
    0x0056c350: ("ShipSubsystem__IsSubsystemDestroyed", "Check if subsystem HP below threshold"),
    0x0056c3b0: ("ShipSubsystem__IsHittableFromLocation", "ShipSubsystem method: IsHittableFromLocation"),
    0x0056c470: ("ShipSubsystem__SetCurrentHP", "Set subsystem HP, triggers death cascade if <=0"),
    0x0056c5c0: ("ShipSubsystem__AddChildSubsystem", "ShipSubsystem method: AddChildSubsystem"),
    0x0056c8f0: ("ShipSubsystem__UpdateDamagePoint", "ShipSubsystem method: UpdateDamagePoint"),
    0x0056d320: ("ShipSubsystem__WriteState", "ShipSubsystem method: WriteState"),
    0x0056d390: ("ShipSubsystem__ReadState", "ShipSubsystem method: ReadState"),

    # --- WarpEngineSubsystem (6) ---
    0x0056de40: ("WarpEngineSubsystem__Cast", "WarpEngineSubsystem method: Cast"),
    0x0056de70: ("WarpEngineSubsystem__ctor", "WarpEngineSubsystem method: ctor"),
    0x0056dfd0: ("WarpEngineSubsystem__dtor", "WarpEngineSubsystem method: dtor"),
    0x0056e7d0: ("WarpEngineSubsystem__TransitionToState", "WarpEngineSubsystem method: TransitionToState"),
    0x0056ecd0: ("WarpEngineSubsystem__RegisterHandlerNames", "WarpEngineSubsystem: registers SetWarpSequence name string"),
    0x0056ecf0: ("WarpEngineSubsystem__RegisterHandlers", "WarpEngineSubsystem: registers SetWarpSequence event handler"),

    # --- EnergyWeapon (12) ---
    0x0056f8d0: ("EnergyWeapon__GetProperty", "EnergyWeapon: returns +0x18 (property pointer)"),
    0x0056f8e0: ("EnergyWeapon__GetRechargeRate", "EnergyWeapon: property+0x6C recharge rate"),
    0x0056f910: ("EnergyWeapon__GetFireSoundBase", "EnergyWeapon: property+0x74 fire sound base name"),
    0x0056f920: ("EnergyWeapon__GetFireSoundBase_Alt", "EnergyWeapon: property+0x74 alternate path"),
    0x0056f930: ("EnergyWeapon__GetMaxDamage", "EnergyWeapon: property+0x64 max damage"),
    0x0056f940: ("EnergyWeapon__GetMaxDamageDistance", "EnergyWeapon: property+0x7C max damage distance (SWIG-confirmed)"),
    0x0056fbd0: ("EnergyWeapon__SetPropertyAndInit", "EnergyWeapon: set property, init charge fields"),
    0x0056fd70: ("EnergyWeapon__UpdateChargeLevel", "EnergyWeapon: recalculate charge ratio +0xBC"),
    0x0056fdc0: ("EnergyWeapon__Update", "EnergyWeapon: per-tick update (charge ratio, parent Update)"),
    0x0056fe30: ("EnergyWeapon__WriteToStream", "EnergyWeapon: serialize charge + fire state to stream"),
    0x0056feb0: ("EnergyWeapon__ReadFromStream", "EnergyWeapon: deserialize charge + fire state from stream"),
    0x0056ff40: ("EnergyWeapon__ResolveObjectRefs", "EnergyWeapon: resolve parent + fire target refs"),
    0x0056ff60: ("EnergyWeapon__FixupObjectRefs", "EnergyWeapon: fixup parent + fire target refs"),

    # --- PhaserSubsystem (3) ---
    0x0056f900: ("PhaserSubsystem__GetMaxCharge", "PhaserSubsystem method: GetMaxCharge"),
    0x0056f950: ("PhaserSubsystem__ctor", "PhaserSubsystem method: ctor"),
    0x0056fb60: ("PhaserSubsystem__dtor", "PhaserSubsystem method: dtor"),

    # --- PhaserBank (25) ---
    0x00570b50: ("PhaserBank__GetProperty", "PhaserBank method: GetProperty"),
    0x00570b60: ("PhaserBank__GetOrientationForward", "PhaserBank method: GetOrientationForward"),
    0x00570b80: ("PhaserBank__GetOrientationUp", "PhaserBank method: GetOrientationUp"),
    0x00570ba0: ("PhaserBank__GetOrientationRight", "PhaserBank method: GetOrientationRight"),
    0x00570c80: ("PhaserBank__GetWidth", "PhaserBank method: GetWidth"),
    0x00570c90: ("PhaserBank__GetLength", "PhaserBank method: GetLength"),
    0x00570cd0: ("PhaserBank__GetArcWidthAngles", "PhaserBank method: GetArcWidthAngles"),
    0x00570d00: ("PhaserBank__GetArcHeightAngles", "PhaserBank method: GetArcHeightAngles"),
    0x00570d30: ("PhaserBank__GetArcWidthAngleMin", "PhaserBank method: GetArcWidthAngleMin"),
    0x00570d40: ("PhaserBank__GetArcWidthAngleMax", "PhaserBank method: GetArcWidthAngleMax"),
    0x00570d50: ("PhaserBank__GetArcHeightAngleMin", "PhaserBank method: GetArcHeightAngleMin"),
    0x00570d60: ("PhaserBank__GetArcHeightAngleMax", "PhaserBank method: GetArcHeightAngleMax"),
    0x00570d70: ("PhaserBank__ctor", "PhaserBank method: ctor"),
    0x00570ee0: ("PhaserBank__dtor", "PhaserBank method: dtor"),
    0x005714a0: ("PhaserBank__ComputeFiringArcToTarget", "PhaserBank: compute arc angle to target with obstacle check"),
    0x00571a00: ("PhaserBank__CanFireAtTarget", "PhaserBank: range + power check for firing"),
    0x00571ab0: ("PhaserBank__ComputeBeamEndpoint", "PhaserBank: compute beam endpoint from angle via sin/cos"),
    0x00571ee0: ("PhaserBank__IsAngleInFiringArc", "PhaserBank: check angle within width/height arc limits"),
    0x00572b00: ("PhaserBank__GetDischargeRateForPowerLevel", "PhaserBank: 3 power levels -> discharge rate constants"),
    0x00572b80: ("PhaserBank__UpdateCharge", "PhaserBank method: UpdateCharge"),
    0x00572c50: ("PhaserBank__GetArcCenterWorldDir", "PhaserBank: arc center direction in world space"),
    0x00572f00: ("PhaserBank__ComputeRestPosition", "PhaserBank: compute rest position at arc center -> +0x11C"),
    0x00573040: ("PhaserBank__WriteToStream", "PhaserBank: serialize to stream (parent + 3 floats)"),
    0x005730a0: ("PhaserBank__ReadFromStream", "PhaserBank: deserialize from stream (parent + 3 floats)"),
    0x0056fc10: ("PhaserBank__GetFireStartSoundName", "PhaserBank: fire start sound name from property"),
    0x0056fcc0: ("PhaserBank__GetFireLoopSoundName", "PhaserBank: fire loop sound name from property"),

    # --- PhaserSystem (11) ---
    0x00573c60: ("PhaserSystem__Cast", "PhaserSystem method: Cast"),
    0x00573c90: ("PhaserSystem__ctor", "Phaser weapon system constructor"),
    0x00573dd0: ("PhaserSystem__dtor", "PhaserSystem method: dtor"),
    0x00573de0: ("PhaserSystem__RegisterHandlerNames", "PhaserSystem method: RegisterHandlerNames"),
    0x00573e40: ("PhaserSystem__RegisterHandlers", "PhaserSystem method: RegisterHandlers"),
    0x00574010: ("PhaserSystem__StopFiringAtTarget", "PhaserSystem: stop firing + post ET_STOP_FIRING_AT_TARGET_NOTIFY"),
    0x00574110: ("PhaserSystem__StopFiringHandler", "PhaserSystem method: StopFiringHandler"),
    0x00574200: ("PhaserSystem__SetPowerLevel", "SWIG target: fires ET_SET_PHASER_LEVEL(0x8000E0)"),
    0x005741a0: ("PhaserSystem__WriteState", "PhaserSystem: serialize state (parent + power level byte)"),
    0x005741d0: ("PhaserSystem__ReadState", "PhaserSystem: deserialize state (parent + power level byte)"),

    # --- TGCharEvent (1) ---
    0x00574c20: ("TGCharEvent__ctor", "TGCharEvent constructor (factory 0x105, +0x28=byte)"),

    # --- PulseWeapon (4) ---
    0x00574fd0: ("PulseWeapon__ctor", "PulseWeapon method: ctor"),
    0x00575110: ("PulseWeapon__dtor", "PulseWeapon method: dtor"),
    0x005769a0: ("PulseWeapon__WriteToStream", "PulseWeapon: serialize to stream (parent + 3 fields)"),
    0x005769f0: ("PulseWeapon__ReadFromStream", "PulseWeapon: deserialize from stream"),

    # --- TorpedoTube (25) ---
    0x00574f40: ("TorpedoTube__GetArcHeightAngleMin", "TorpedoTube: height arc min from property"),
    0x00574f50: ("TorpedoTube__GetArcHeightAngleMax", "TorpedoTube: height arc max from property"),
    0x00574f60: ("TorpedoTube__GetArcWidthAngleMin", "TorpedoTube: width arc min from property"),
    0x00574f70: ("TorpedoTube__GetArcWidthAngleMax", "TorpedoTube: width arc max from property"),
    0x00574f80: ("TorpedoTube__GetArcHeightAngleRange", "TorpedoTube: get height angle min+max pair"),
    0x00574fa0: ("TorpedoTube__GetArcWidthAngleRange", "TorpedoTube: get width angle min+max pair"),
    0x00574fc0: ("TorpedoTube__GetLaunchSpeed", "TorpedoTube: property+0xC8 launch speed"),
    0x00575230: ("TorpedoTube__GetDamageForPowerLevel", "TorpedoTube: scale damage by power level (0/1/2)"),
    0x00575a60: ("TorpedoTube__IsTargetInFiringArc", "TorpedoTube: check target within firing arc angles"),
    0x00575db0: ("TorpedoTube__ComputeRandomDirectionInArc", "TorpedoTube: random direction within firing arc"),
    0x005762b0: ("TorpedoTube__LaunchFromNetwork", "TorpedoTube: network receive path for torpedo launch"),
    0x0057c330: ("TorpedoTube__GetProperty", "TorpedoTube method: GetProperty"),
    0x0057c340: ("TorpedoTube__GetDirection", "TorpedoTube method: GetDirection"),
    0x0057c3a0: ("TorpedoTube__GetRight", "TorpedoTube method: GetRight"),
    0x0057c410: ("TorpedoTube__GetReloadDelay", "TorpedoTube method: GetReloadDelay"),
    0x0057c420: ("TorpedoTube__GetMaxReady", "TorpedoTube method: GetMaxReady"),
    0x0057c480: ("TorpedoTube__Cast", "TorpedoTube method: Cast"),
    0x0057c4b0: ("TorpedoTube__ctor", "TorpedoTube method: ctor"),
    0x0057c5f0: ("TorpedoTube__dtor", "TorpedoTube method: dtor"),
    0x0057c740: ("TorpedoTube__ClearReadySlots", "TorpedoTube: zero all ready slots array"),
    0x0057c9e0: ("TorpedoTube__Fire", "TorpedoTube method: Fire"),
    0x0057d8a0: ("TorpedoTube__ReloadTorpedo", "TorpedoTube method: ReloadTorpedo"),
    0x0057d9a0: ("TorpedoTube__UnloadTorpedo", "TorpedoTube method: UnloadTorpedo"),
    0x0057da90: ("TorpedoTube__CanHit", "TorpedoTube method: CanHit"),
    0x0057dc10: ("TorpedoTube__IsInArc", "TorpedoTube method: IsInArc"),
    0x0057de90: ("TorpedoTube__GetWorldDirection", "TorpedoTube: transform local direction to world space"),
    0x0057df40: ("TorpedoTube__WriteToStream", "TorpedoTube: serialize tube state to stream"),
    0x0057dfd0: ("TorpedoTube__ReadFromStream", "TorpedoTube: deserialize tube state from stream"),

    # --- PulseWeaponSystem (3) ---
    0x00577380: ("PulseWeaponSystem__Cast", "PulseWeaponSystem method: Cast"),
    0x005773b0: ("PulseWeaponSystem__ctor", "PulseWeaponSystem method: ctor"),
    0x005774b0: ("PulseWeaponSystem__dtor", "PulseWeaponSystem method: dtor"),

    # --- Torpedo (19) ---
    0x00578110: ("Torpedo__Cast", "Torpedo method: Cast"),
    0x00578140: ("Torpedo__RegisterHandlerNames", "Torpedo method: RegisterHandlerNames"),
    0x00578160: ("Torpedo__RegisterHandlers", "Torpedo method: RegisterHandlers"),
    0x00578180: ("Torpedo__Create", "Create torpedo entity from Python script + schedule lifetime"),
    0x00578340: ("Torpedo__GetLaunchSpeed", "Torpedo method: GetLaunchSpeed"),
    0x00578370: ("Torpedo__GetLaunchSound", "Torpedo method: GetLaunchSound"),
    0x005783d0: ("Torpedo__ctor", "Torpedo ctor: 0x170 bytes, vtable 0x00893458"),
    0x00578660: ("Torpedo__dtor", "Torpedo method: dtor"),
    0x005786a0: ("Torpedo__CreateDisruptorModel", "Torpedo method: CreateDisruptorModel"),
    0x00578730: ("Torpedo__CreateTorpedoModel", "Torpedo method: CreateTorpedoModel"),
    0x00578800: ("Torpedo__OrientToVelocity", "Torpedo: compute orientation matrix from velocity dir"),
    0x00578cb0: ("Torpedo__UpdateGuidance", "Torpedo: homing guidance (predict target, clamp turn rate)"),
    0x00579010: ("Torpedo__DetectCollision", "Torpedo: shield intersection + hull damage"),
    0x00579530: ("Torpedo__ApplyTorque", "Torpedo: apply angular torque for turning"),
    0x00579610: ("Torpedo__ComputeSplineTurnTime", "Torpedo: spline-based turn time computation"),
    0x00579a30: ("Torpedo__GetVelocity", "Torpedo: compute velocity = speed * direction"),
    0x00579a90: ("Torpedo__SetClampedAngularAcceleration", "Torpedo: set clamped angular acceleration for homing"),
    0x00579cc0: ("Torpedo__WriteNetworkState", "Torpedo: serialize owner/target/flags + CompressedVec4"),
    0x0057a280: ("Torpedo__WriteToStream", "Torpedo method: WriteToStream"),
    0x0057a400: ("Torpedo__ReadFromStream", "Torpedo method: ReadFromStream"),

    # --- TorpedoSystem (12) ---
    0x0057aff0: ("TorpedoSystem__Cast", "TorpedoSystem method: Cast"),
    0x0057b020: ("TorpedoSystem__ctor", "Torpedo weapon system constructor"),
    0x0057b170: ("TorpedoSystem__dtor", "TorpedoSystem method: dtor"),
    0x0057b180: ("TorpedoSystem__RegisterHandlerNames", "TorpedoSystem: registers TorpedoTypeChangedHandler name string (chains to stub)"),
    0x0057b1a0: ("TorpedoSystem__RegisterHandlers", "TorpedoSystem: registers TorpedoTypeChanged event handler (chains to stub)"),
    0x0057b1c0: ("TorpedoSystem__SetSkewFire", "TorpedoSystem method: SetSkewFire"),
    0x0057b230: ("TorpedoSystem__SetAmmoType", "SWIG target: sets ammo type with reload flag"),
    0x0057b740: ("TorpedoSystem__GetNumAvailableTorpsToType", "TorpedoSystem method: GetNumAvailableTorpsToType"),
    0x0057b780: ("TorpedoSystem__WriteToStream", "TorpedoSystem: serialize to stream (parent + ammo type)"),
    0x0057b7b0: ("TorpedoSystem__ReadFromStream", "TorpedoSystem: deserialize from stream (parent + ammo type)"),
    0x0057b8e0: ("TorpedoSystem__ResolveObjectRefs", "TorpedoSystem: resolve parent + child object refs"),
    0x0057d890: ("TorpedoSystem__RegisterHandlerNames_Stub", "TorpedoSystem: stub RegisterHandlerNames (empty, called by TorpedoSystem__RegisterHandlerNames chain)"),

    # --- TorpedoTubeProperty (3) ---
    0x0057c370: ("TorpedoTubeProperty__GetDirection", "TorpedoTubeProperty method: GetDirection"),
    0x0057c3d0: ("TorpedoTubeProperty__GetRight", "TorpedoTubeProperty method: GetRight"),
    0x00694fe0: ("TorpedoTubeProperty__Cast", "TorpedoTubeProperty method: Cast"),

    # --- TractorBeamProperty (10) ---
    0x0057ead0: ("TractorBeamProperty__GetOrientationForward", "TractorBeamProperty method: GetOrientationForward"),
    0x0057eb30: ("TractorBeamProperty__GetOrientationUp", "TractorBeamProperty method: GetOrientationUp"),
    0x0057f530: ("TractorBeamProperty__GetOrientationRight", "TractorBeamProperty method: GetOrientationRight"),
    0x00640b20: ("TractorBeamProperty__SetOuterShellColor", "TractorBeamProperty method: SetOuterShellColor"),
    0x00640c10: ("TractorBeamProperty__SetInnerShellColor", "TractorBeamProperty method: SetInnerShellColor"),
    0x00640d00: ("TractorBeamProperty__SetOuterCoreColor", "TractorBeamProperty method: SetOuterCoreColor"),
    0x00640df0: ("TractorBeamProperty__SetInnerCoreColor", "TractorBeamProperty method: SetInnerCoreColor"),
    0x006966b0: ("TractorBeamProperty__Cast", "TractorBeamProperty method: Cast"),
    0x00696c10: ("TractorBeamProperty__SetTextureName", "TractorBeamProperty method: SetTextureName"),
    0x006983a0: ("TractorBeamProperty__SetOrientation", "TractorBeamProperty method: SetOrientation"),

    # --- TractorBeam (10) ---
    0x0057fcd0: ("TractorBeam__ApplyMode0_Drag", "TractorBeam: mode 0 drag toward tractor source"),
    0x0057ff60: ("TractorBeam__ApplyMode1_Push", "TractorBeam: mode 1 push away from source"),
    0x00580590: ("TractorBeam__ApplyMode2_Hold", "TractorBeam: mode 2 hold at fixed position"),
    0x00580740: ("TractorBeam__ApplyMode3_Repel", "TractorBeam: mode 3 repel away"),
    0x00580910: ("TractorBeam__ApplyMode5_Dock", "TractorBeam: mode 5 docking approach"),
    0x00580d70: ("TractorBeam__InitBeamAndStartFiring", "TractorBeam: init beam visual and start firing"),
    0x00580e90: ("TractorBeam__SetBeamEndpoints", "TractorBeam: update beam start/end points"),
    0x00580f50: ("TractorBeam__ComputeDamageForBeam", "TractorBeam: per-tick damage calculation"),
    0x005814f0: ("TractorBeam__WriteToStream", "TractorBeam: serialize (parent + mode byte)"),
    0x00581550: ("TractorBeam__ReadFromStream", "TractorBeam: deserialize (parent + mode byte)"),

    # --- TractorBeamProjector (2) ---
    0x0057ec70: ("TractorBeamProjector__ctor", "TractorBeamProjector method: ctor"),
    0x0057edb0: ("TractorBeamProjector__dtor", "TractorBeamProjector method: dtor"),

    # --- TractorBeamSystem (6) ---
    0x00582050: ("TractorBeamSystem__Cast", "TractorBeamSystem method: Cast"),
    0x00582080: ("TractorBeamSystem__ctor", "Tractor beam system constructor (powerMode=1, backup-first)"),
    0x005821a0: ("TractorBeamSystem__dtor", "TractorBeamSystem method: dtor"),
    0x005821b0: ("TractorBeamSystem__RegisterHandlerNames", "TractorBeamSystem method: RegisterHandlerNames"),
    0x005821f0: ("TractorBeamSystem__RegisterHandlers", "TractorBeamSystem method: RegisterHandlers"),
    0x005826a0: ("TractorBeamSystem__StopFiringHandler", "TractorBeamSystem method: StopFiringHandler"),

    # --- Weapon (3) ---
    0x00583240: ("Weapon__IsMemberOfGroup", "Weapon method: IsMemberOfGroup"),
    0x00583260: ("Weapon__GetDamageRadiusFactor", "Weapon method: GetDamageRadiusFactor"),
    0x00583270: ("Weapon__IsDumbFire", "Weapon method: IsDumbFire"),

    # --- WeaponSubsystem (4) ---
    0x00583280: ("WeaponSubsystem__ctor", "WeaponSubsystem method: ctor"),
    0x005833d0: ("WeaponSubsystem__dtor", "WeaponSubsystem method: dtor"),
    0x00583400: ("WeaponSubsystem__WriteToStream", "WeaponSubsystem: serialize (parent + target)"),
    0x00583440: ("WeaponSubsystem__ReadFromStream", "WeaponSubsystem: deserialize (parent + target)"),

    # --- WeaponSystem (29) ---
    0x00584070: ("WeaponSystem__GetSingleFireMode", "WeaponSystem: get single-fire flag from property+0x51"),
    0x00584080: ("WeaponSystem__FindTargetByObjectID", "Extracts obj+4 ID, delegates to FindTargetEntry"),
    0x00584090: ("WeaponSystem__RemoveFromTargetList", "WeaponSystem method: RemoveFromTargetList"),
    0x005840a0: ("WeaponSystem__Constructor", "WeaponSystem method: Constructor"),
    0x00584270: ("WeaponSystem__dtor", "WeaponSystem method: dtor"),
    0x00584360: ("WeaponSystem__RegisterHandlerNames", "WeaponSystem: registers ObjectExitedSet name string, chains to PhaserSystem+TractorBeamSystem"),
    0x00584380: ("WeaponSystem__RegisterHandlers", "WeaponSystem: registers event handlers, chains to PhaserSystem+TractorBeamSystem"),
    0x00584390: ("WeaponSystem__StartFiringAtTarget", "WeaponSystem: add target to list, start firing"),
    0x00584560: ("WeaponSystem__StopFiringAll", "WeaponSystem: clear targets, stop all children"),
    0x005845a0: ("WeaponSystem__StopFiringAtTarget", "WeaponSystem method: StopFiringAtTarget"),
    0x00584750: ("WeaponSystem__ClearTargetList", "WeaponSystem method: ClearTargetList"),
    0x005847d0: ("WeaponSystem__Update", "WeaponSystem: per-tick update (fire loop, single-fire, cooldown)"),
    0x00584930: ("WeaponSystem__UpdateWeapons", "WeaponSystem method: UpdateWeapons"),
    0x00584cc0: ("WeaponSystem__UpdateTargetList", "WeaponSystem method: UpdateTargetList"),
    0x00584fa0: ("WeaponSystem__SetFiringChainMode", "WeaponSystem method: SetFiringChainMode"),
    0x00584fc0: ("WeaponSystem__GetFiringChain", "WeaponSystem method: GetFiringChain"),
    0x00585020: ("WeaponSystem__ParseFiringChains", "WeaponSystem: parse firing chain string into bitmask groups"),
    0x005852a0: ("WeaponSystem__GetTargetWorldPosition", "WeaponSystem: transform target offset to world position"),
    0x00585360: ("WeaponSystem__FindTargetEntry", "Searches +0xC4 target list by object ID"),
    0x00585390: ("WeaponSystem__RemoveTarget", "WeaponSystem: remove target from linked list, free entry"),
    0x00585580: ("WeaponSystem__SetTargetOffset", "Updates target entry offset + clears child subsystem targets"),
    0x005856b0: ("WeaponSystem__OnDisabled", "WeaponSystem: post disabled event, clear targets"),
    0x005856d0: ("WeaponSystem__BuildVisibleTargetList", "WeaponSystem: build target list from weapons + sensor visibility"),
    0x005859d0: ("WeaponSystem__IsTargetVisible", "WeaponSystem: check if target in visible list"),
    0x00585a10: ("WeaponSystem__WriteState", "WeaponSystem: serialize state (parent + firing flag)"),
    0x00585a40: ("WeaponSystem__ReadState", "WeaponSystem: deserialize state (parent + firing flag)"),
    0x00585a70: ("WeaponSystem__WriteToStream", "WeaponSystem: full serialize (targets + firing chains)"),
    0x00585b80: ("WeaponSystem__ReadFromStream", "WeaponSystem: full deserialize (targets + firing chains)"),
    0x00585f40: ("WeaponSystem__GetTargets_Py", "WeaponSystem: SWIG Python target list query"),

    # --- WeaponTargetEntry (2) ---
    0x00585ec0: ("WeaponTargetEntry__WriteToStream", "WeaponTargetEntry: serialize (objectID + 3 offset floats)"),
    0x00585f00: ("WeaponTargetEntry__ReadFromStream", "WeaponTargetEntry: deserialize (objectID + 3 offset floats)"),

    # --- FiringChain (3) ---
    0x00586220: ("FiringChain__GetFirstGroupIndex", "FiringChain: get first set bit index from bitmask"),
    0x00586250: ("FiringChain__GetNextGroupIndex", "FiringChain: get next set bit index from bitmask"),
    0x00586280: ("FiringChain__WriteToStream", "FiringChain: serialize (uint mask + bits)"),

    # --- DamageableObject (17) ---
    0x00590a50: ("DamageableObject__FindByObjectID", "DamageableObject method: FindByObjectID"),
    0x00590b20: ("DamageableObject__Cast", "DamageableObject method: Cast"),
    0x00590b50: ("DamageableObject__RegisterHandlerNames", "DamageableObject: registers ObjectDestroyed/DeleteMe handler name strings"),
    0x00590bb0: ("DamageableObject__RegisterHandlers", "DamageableObject: registers ObjectDestroyed/DeleteMe event handlers"),
    0x00590cb0: ("DamageableObject__InitFields", "DamageableObject method: InitFields"),
    0x00591410: ("DamageableObject__ctor", "DamageableObject method: ctor"),
    0x00591620: ("DamageableObject__dtor", "DamageableObject method: dtor"),
    0x00592680: ("DamageableObject__DamageRefresh", "DamageableObject method: DamageRefresh"),
    0x005930a0: ("DamageableObject__DeadObjectRemovalCheck", "DamageableObject method: DeadObjectRemovalCheck"),
    0x005942d0: ("DamageableObject__DisableGlowAlphaMaps", "DamageableObject method: DisableGlowAlphaMaps"),
    0x005946a0: ("DamageableObject__CanCollide", "DamageableObject method: CanCollide"),
    0x005946f0: ("DamageableObject__EnableCollisionsWith", "DamageableObject method: EnableCollisionsWith"),
    0x00595650: ("DamageableObject__WriteToStream", "DamageableObject method: WriteToStream"),
    0x00595890: ("DamageableObject__ReadFromStream", "DamageableObject method: ReadFromStream"),
    0x00595c60: ("DamageableObject__SendExplosions_0x29", "Iterates explosion damage list at ship+0x13C"),
    0x0059db80: ("DamageableObject__SaveAllToStream", "DamageableObject method: SaveAllToStream"),
    0x0059dd40: ("DamageableObject__LoadAllFromStream", "DamageableObject method: LoadAllFromStream"),

    # --- DamageSystem (3) ---
    0x00592960: ("DamageSystem__DamageTickUpdate", "DamageSystem method: DamageTickUpdate"),
    0x00593c10: ("DamageSystem__AreaEffectDamage", "Area-effect shield damage: uniform 1/6 per facing"),
    0x00593ee0: ("DamageSystem__ApplyRemainingDamageToHull", "After handlers, applies remaining damage to hull"),

    # --- CollisionEvent (1) ---
    0x00595410: ("CollisionEvent__GetPoint", "CollisionEvent method: GetPoint"),

    # --- Nebula (2) ---
    0x005973b0: ("Nebula__Cast", "Nebula method: Cast"),
    0x00599290: ("Nebula__IsObjectInNebula", "Nebula method: IsObjectInNebula"),

    # --- PhysicsObjectClass (19) ---
    0x0059fc10: ("PhysicsObjectClass__GetNetworkChildren", "PhysicsObjectClass method: GetNetworkChildren"),
    0x0059fc60: ("PhysicsObjectClass__FindByObjectID", "PhysicsObjectClass method: FindByObjectID"),
    0x0059fd30: ("PhysicsObjectClass__Cast", "PhysicsObjectClass method: Cast"),
    0x0059fd60: ("PhysicsObjectClass__ctor", "PhysicsObjectClass method: ctor"),
    0x005a0040: ("PhysicsObjectClass__InitPhysics", "PhysicsObjectClass method: InitPhysics"),
    0x005a0200: ("PhysicsObjectClass__dtor", "PhysicsObjectClass method: dtor"),
    0x005a04f0: ("PhysicsObjectClass__SetAngularVelocity", "PhysicsObjectClass method: SetAngularVelocity"),
    0x005a0790: ("PhysicsObjectClass__ApplyForce", "PhysicsObjectClass method: ApplyForce"),
    0x005a1430: ("PhysicsObjectClass__SetAngularAcceleration", "PhysicsObjectClass method: SetAngularAcceleration"),
    0x005a1480: ("PhysicsObjectClass__SetAngularAccelerationLinear", "PhysicsObjectClass method: SetAngularAccelerationLinear"),
    0x005a14d0: ("PhysicsObjectClass__SetAngularDirectionType", "PhysicsObjectClass method: SetAngularDirectionType"),
    0x005a1740: ("PhysicsObjectClass__RegisterHandlerNames", "PhysicsObjectClass: registers ObjectDestroyed/CollisionDestroyed handler name strings"),
    0x005a1780: ("PhysicsObjectClass__RegisterHandlers", "PhysicsObjectClass: registers ObjectDestroyed event handlers"),
    0x005a17c0: ("PhysicsObjectClass__DeleteMeStage1", "PhysicsObjectClass method: DeleteMeStage1"),
    0x005a17e0: ("PhysicsObjectClass__ObjectDestroyedHandler", "PhysicsObjectClass method: ObjectDestroyedHandler"),
    0x005a18f0: ("PhysicsObjectClass__WriteToStream", "PhysicsObjectClass method: WriteToStream"),
    0x005a1af0: ("PhysicsObjectClass__ReadFromStream", "PhysicsObjectClass method: ReadFromStream"),
    0x005a59c0: ("PhysicsObjectClass__StepPhysics", "PhysicsObjectClass method: StepPhysics"),
    0x005a5a30: ("PhysicsObjectClass__UpdateProximity", "PhysicsObjectClass method: UpdateProximity"),

    # --- Planet (3) ---
    0x005a4280: ("Planet__AtmosphereProximityHandler_A", "Planet method: AtmosphereProximityHandler_A"),
    0x005a42a0: ("Planet__AtmosphereProximityHandler_B", "Planet method: AtmosphereProximityHandler_B"),
    0x005a4580: ("Planet__LoadFromStream", "Deserialize planet from NiStream"),

    # --- ProximityCheck (14) ---
    0x005a5420: ("ProximityCheck__ctor", "ProximityCheck method: ctor"),
    0x005a5610: ("ProximityCheck__ctorWithEvent", "ProximityCheck method: ctorWithEvent"),
    0x005a5c10: ("ProximityCheck__AddObjectToCheckList", "ProximityCheck method: AddObjectToCheckList"),
    0x005a5c30: ("ProximityCheck__AddObjectToCheckListByID", "ProximityCheck method: AddObjectToCheckListByID"),
    0x005a5d50: ("ProximityCheck__AddObjectListToCheckList", "ProximityCheck method: AddObjectListToCheckList"),
    0x005a5d80: ("ProximityCheck__AddObjectTypeToCheckList", "ProximityCheck method: AddObjectTypeToCheckList"),
    0x005a5de0: ("ProximityCheck__IsObjectInCheckList", "ProximityCheck method: IsObjectInCheckList"),
    0x005a5e90: ("ProximityCheck__GetTriggerType", "ProximityCheck method: GetTriggerType"),
    0x005a5eb0: ("ProximityCheck__SetTriggerType", "ProximityCheck method: SetTriggerType"),
    0x005a5f80: ("ProximityCheck__RemoveObjectFromCheckList", "ProximityCheck method: RemoveObjectFromCheckList"),
    0x005a5f90: ("ProximityCheck__RemoveObjectFromCheckListByID", "ProximityCheck method: RemoveObjectFromCheckListByID"),
    0x005a60c0: ("ProximityCheck__RemoveObjectTypeFromCheckList", "ProximityCheck method: RemoveObjectTypeFromCheckList"),
    0x005a61c0: ("ProximityCheck__CheckProximity", "ProximityCheck method: CheckProximity"),
    0x005a6340: ("ProximityCheck__RemoveAndDelete", "ProximityCheck method: RemoveAndDelete"),

    # --- ProximityManager (5) ---
    0x005a7640: ("ProximityManager__AddObject", "ProximityManager method: AddObject"),
    0x005a7720: ("ProximityManager__RemoveObject", "ProximityManager method: RemoveObject"),
    0x005a78e0: ("ProximityManager__GetNearObjects", "ProximityManager method: GetNearObjects"),
    0x005a83a0: ("ProximityManager__Update", "ProximityManager method: Update"),
    0x005a8420: ("ProximityManager__UpdateObject", "ProximityManager method: UpdateObject"),

    # --- CollisionQuery (3) ---
    0x005a7cf0: ("CollisionQuery__Execute", "CollisionQuery method: Execute"),
    0x005a8320: ("CollisionQuery__GetNextResult", "CollisionQuery method: GetNextResult"),
    0x005a8350: ("CollisionQuery__Destroy", "CollisionQuery method: Destroy"),

    # --- ShipClass (20) ---
    0x005ab5a0: ("ShipClass__GetObjectByID", "ShipClass method: GetObjectByID"),
    0x005ab610: ("ShipClass__GetObject", "ShipClass method: GetObject"),
    0x005ab6a0: ("Ship__RegisterHandlerNames", "Ship: registers all ship handler name strings (12 handlers + subsystem chain)"),
    0x005ab7c0: ("Ship__RegisterHandlers", "Ship: registers all ship event handlers + subsystem chain"),
    0x005ac170: ("ShipClass__SetScript", "ShipClass method: SetScript"),
    0x005ac1e0: ("ShipClass__SetDeathScript", "ShipClass method: SetDeathScript"),
    0x005ae090: ("ShipClass__SetInvincible", "ShipClass method: SetInvincible"),
    0x005af010: ("ShipClass__WeaponHitHandler", "Weapon hit entry point -> ApplyWeaponDamage"),
    0x005af420: ("ShipClass__ApplyWeaponDamage", "Scales weapon hit: damage*2, radius*0.5"),
    0x005af4a0: ("ShipClass__DoDamageToSelf_Inner", "Per-subsystem damage (gates: god mode, damage disabled)"),
    0x005af5f0: ("ShipClass__DoDamageToSelf", "Lethal self-damage to reactor (self-destruct path)"),
    0x005af9c0: ("ShipClass__CollisionEffectHandler", "ShipClass method: CollisionEffectHandler"),
    0x005afad0: ("ShipClass__HostCollisionEffectHandler", "ShipClass method: HostCollisionEffectHandler"),
    0x005afd70: ("ShipClass__SubsystemDamageDistributor", "Walks ship+0x284 subsystem list, shield absorption + hull damage"),
    0x005afea0: ("ShipClass__ShipDeathHandler", "Ship death: fires OBJECT_EXPLODING event, plays death effects"),
    0x005b0760: ("ShipClass__HandleChangeAlertLevel", "ShipClass method: HandleChangeAlertLevel"),
    0x005b0810: ("ShipClass__SetNoAIState", "ShipClass method: SetNoAIState"),
    0x005b0bf0: ("ShipClass__HandleTractorHitStart", "ShipClass method: HandleTractorHitStart"),
    0x005b0c70: ("ShipClass__HandleTractorHitStop", "ShipClass method: HandleTractorHitStop"),
    0x005b0e00: ("ShipClass__SetTargetHandler", "ShipClass method: SetTargetHandler"),

    # --- WeaponSystemProperty (2) ---
    0x005b4ec0: ("WeaponSystemProperty__GetFiringChainString", "WeaponSystemProperty method: GetFiringChainString"),
    0x0069af60: ("WeaponSystemProperty__Cast", "WeaponSystemProperty method: Cast"),

    # --- TGParagraph (11) ---
    0x005d47c0: ("TGParagraph__InsertString", "TGParagraph method: InsertString"),
    0x005d4900: ("TGParagraph__AppendString", "TGParagraph method: AppendString"),
    0x00731b80: ("TGParagraph__Cast", "TGParagraph method: Cast"),
    0x00731c50: ("TGParagraph__ctor", "TGParagraph method: ctor"),
    0x00731fc0: ("TGParagraph__SetReadOnly", "TGParagraph method: SetReadOnly"),
    0x00732070: ("TGParagraph__SetString", "TGParagraph method: SetString"),
    0x00732100: ("TGParagraph__SetIgnoreString", "TGParagraph method: SetIgnoreString"),
    0x00733160: ("TGParagraph__RegisterHandlerNames", "TGParagraph: registers Mouse/Keyboard/CursorBlink name strings"),
    0x007331a0: ("TGParagraph__RegisterHandlers", "TGParagraph: registers Mouse/Keyboard/CursorBlink event handlers"),
    0x00733330: ("TGParagraph__KeyboardHandler", "TGParagraph: handle keyboard event"),
    0x00733850: ("TGParagraph__SetColor", "TGParagraph method: SetColor"),
    0x00733af0: ("TGParagraph__SetFontGroup", "TGParagraph method: SetFontGroup"),

    # --- TGSound (29) ---
    0x005d92f0: ("TGSound__ctor", "TGSound method: ctor"),
    0x0070b730: ("TGSound__Load", "TGSound method: Load"),
    0x0070b930: ("TGSound__Unload", "TGSound method: Unload"),
    0x0070b9b0: ("TGSound__SetGroup", "TGSound method: SetGroup"),
    0x0070ba10: ("TGSound__Play", "TGSound method: Play"),
    0x0070ba60: ("TGSound__PlayAndNotify", "TGSound method: PlayAndNotify"),
    0x0070bbf0: ("TGSound__Stop", "TGSound method: Stop"),
    0x0070bcb0: ("TGSound__Rewind", "TGSound method: Rewind"),
    0x0070bcc0: ("TGSound__Pause", "TGSound method: Pause"),
    0x0070bce0: ("TGSound__Unpause", "TGSound method: Unpause"),
    0x0070bd00: ("TGSound__GetStatus", "TGSound method: GetStatus"),
    0x0070bd50: ("TGSound__AttachToNode", "TGSound method: AttachToNode"),
    0x0070bd90: ("TGSound__DetachFromNode", "TGSound method: DetachFromNode"),
    0x0070bdf0: ("TGSound__GetParentNode", "TGSound method: GetParentNode"),
    0x0070be00: ("TGSound__SetOrientation", "TGSound method: SetOrientation"),
    0x0070be80: ("TGSound__GetOrientation", "TGSound method: GetOrientation"),
    0x0070bf00: ("TGSound__SetPosition", "TGSound method: SetPosition"),
    0x0070bf90: ("TGSound__SetConeData", "TGSound method: SetConeData"),
    0x0070c000: ("TGSound__GetConeData", "TGSound method: GetConeData"),
    0x0070c050: ("TGSound__SetMinMaxDistance", "TGSound method: SetMinMaxDistance"),
    0x0070c080: ("TGSound__GetMinMaxDistance", "TGSound method: GetMinMaxDistance"),
    0x0070c0b0: ("TGSound__SetVolume", "TGSound method: SetVolume"),
    0x0070c170: ("TGSound__SetPitch", "TGSound method: SetPitch"),
    0x0070c1b0: ("TGSound__GetPitch", "TGSound method: GetPitch"),
    0x0070c270: ("TGSound__GetDurationSeconds", "TGSound method: GetDurationSeconds"),
    0x0070c2a0: ("TGSound__Update", "TGSound method: Update"),
    0x0070c640: ("TGSound__ClearFadePoints", "TGSound method: ClearFadePoints"),
    0x0070c690: ("TGSound__SetEndEvent", "TGSound method: SetEndEvent"),
    0x0070c6e0: ("TGSound__GetEndEvent", "TGSound method: GetEndEvent"),

    # --- WaypointEvent (1) ---
    0x00606120: ("WaypointEvent__ctor", "WaypointEvent method: ctor"),

    # --- PhaserProperty (6) ---
    0x0063d620: ("PhaserProperty__SetOuterShellColor", "PhaserProperty method: SetOuterShellColor"),
    0x0063d710: ("PhaserProperty__SetInnerShellColor", "PhaserProperty method: SetInnerShellColor"),
    0x0063d800: ("PhaserProperty__SetOuterCoreColor", "PhaserProperty method: SetOuterCoreColor"),
    0x0063d8f0: ("PhaserProperty__SetInnerCoreColor", "PhaserProperty method: SetInnerCoreColor"),
    0x00685800: ("PhaserProperty__Cast", "PhaserProperty method: Cast"),
    0x00685d90: ("PhaserProperty__SetTextureName", "PhaserProperty method: SetTextureName"),

    # --- BridgeObjectClass (8) ---
    0x00661220: ("BridgeObjectClass__Cast", "BridgeObjectClass method: Cast"),
    0x00661250: ("BridgeObjectClass__RegisterHandlerNames_Chain", "BridgeObjectClass: registers handler name strings (CreateEffect/AlertLevel/PlayerChanged)"),
    0x006612b0: ("BridgeObjectClass__RegisterHandlers_Stub", "BridgeObjectClass: stub RegisterHandlers (via vtable)"),
    0x00661460: ("BridgeObjectClass__Constructor", "BridgeObjectClass method: Constructor"),
    0x00661de0: ("BridgeObjectClass__RegisterHandlers", "BridgeObjectClass: registers CreateEffect/AlertLevel handlers via TGEventManager"),
    0x006648a0: ("BridgeObjectClass__CreateEffectHandler", "BridgeObjectClass: handle CreateEffect event (WeaponHit)"),
    0x006641c0: ("BridgeObjectClass__CreateEffect", "BridgeObjectClass method: CreateEffect"),
    0x00664840: ("BridgeObjectClass__GoToGreenAlert", "BridgeObjectClass method: GoToGreenAlert"),
    0x00664860: ("BridgeObjectClass__GoToYellowAlert", "BridgeObjectClass method: GoToYellowAlert"),
    0x00664880: ("BridgeObjectClass__GoToRedAlert", "BridgeObjectClass method: GoToRedAlert"),

    # --- BridgeSet (1) ---
    0x00665e00: ("BridgeSet__Cast", "BridgeSet method: Cast"),

    # --- CharacterClass (26) ---
    0x00668430: ("CharacterClass__ReplaceBodyAndHead", "CharacterClass method: ReplaceBodyAndHead"),
    0x00668f60: ("CharacterClass__AddFacialImage", "CharacterClass method: AddFacialImage"),
    0x00669050: ("CharacterClass__AddPhoneme", "CharacterClass method: AddPhoneme"),
    0x00669cc0: ("CharacterClass__GetStatus", "CharacterClass method: GetStatus"),
    0x00669d10: ("CharacterClass__SetStatus", "CharacterClass method: SetStatus"),
    0x0066a7f0: ("CharacterClass__ClearAnimations", "CharacterClass method: ClearAnimations"),
    0x0066ada0: ("CharacterClass__SetBlinkAnimation", "CharacterClass method: SetBlinkAnimation"),
    0x0066ae50: ("CharacterClass__ClearAnimationsOfType", "CharacterClass method: ClearAnimationsOfType"),
    0x0066ae90: ("CharacterClass__SetAnimationDoneEvent", "CharacterClass method: SetAnimationDoneEvent"),
    0x0066aef0: ("CharacterClass__SetCurrentAnimation", "CharacterClass method: SetCurrentAnimation"),
    0x0066b3d0: ("CharacterClass__SetLocation", "CharacterClass method: SetLocation"),
    0x0066b610: ("CharacterClass__SetLocationName", "CharacterClass method: SetLocationName"),
    0x0066b680: ("CharacterClass__MoveTo", "CharacterClass method: MoveTo"),
    0x0066b760: ("CharacterClass__GlanceAt", "CharacterClass method: GlanceAt"),
    0x0066b840: ("CharacterClass__GlanceAway", "CharacterClass method: GlanceAway"),
    0x0066bd10: ("CharacterClass__Breathe", "CharacterClass method: Breathe"),
    0x0066be00: ("CharacterClass__PlayAnimation", "CharacterClass method: PlayAnimation"),
    0x0066beb0: ("CharacterClass__PlayAnimationFile", "CharacterClass method: PlayAnimationFile"),
    0x0066c020: ("CharacterClass__SayLine", "CharacterClass method: SayLine"),
    0x0066c200: ("CharacterClass__Blink", "CharacterClass method: Blink"),
    0x0066c7f0: ("CharacterClass__SetCharacterName", "CharacterClass method: SetCharacterName"),
    0x0066cb90: ("CharacterClass__AddSoundToQueue", "CharacterClass method: AddSoundToQueue"),
    0x0066cf20: ("CharacterClass__LookAtMe", "CharacterClass method: LookAtMe"),
    0x0066d1f0: ("CharacterClass__RegisterHandlerNames", "CharacterClass method: RegisterHandlerNames"),
    0x0066d220: ("CharacterClass__RegisterHandlers", "CharacterClass method: RegisterHandlers"),
    0x0066dc10: ("CharacterClass__SetDatabase", "CharacterClass method: SetDatabase"),

    # --- CharacterSpeakingQueue (2) ---
    0x006726e0: ("CharacterSpeakingQueue__RegisterHandlerNames", "CharacterSpeakingQueue method: RegisterHandlerNames"),
    0x00672700: ("CharacterSpeakingQueue__RegisterHandlers", "CharacterSpeakingQueue method: RegisterHandlers"),

    # --- ViewScreenObject (9) ---
    0x00678750: ("ViewScreenObject__RegisterHandlerNames", "ViewScreenObject method: RegisterHandlerNames"),
    0x00678780: ("ViewScreenObject__RegisterHandlers", "ViewScreenObject method: RegisterHandlers"),
    0x00678850: ("ViewScreenObject__SetModel", "ViewScreenObject method: SetModel"),
    0x00678910: ("ViewScreenObject__SetCamera", "ViewScreenObject method: SetCamera"),
    0x006789c0: ("ViewScreenObject__SetIsOn", "ViewScreenObject method: SetIsOn"),
    0x006789e0: ("ViewScreenObject__IsOn", "ViewScreenObject method: IsOn"),
    0x00678e20: ("ViewScreenObject__MenuUp", "ViewScreenObject method: MenuUp"),
    0x00678e80: ("ViewScreenObject__MenuDown", "ViewScreenObject method: MenuDown"),
    0x00679190: ("ViewScreenObject__LookTowardsSpace", "ViewScreenObject method: LookTowardsSpace"),

    # --- CloakingSubsystemProperty (1) ---
    0x00680270: ("CloakingSubsystemProperty__Cast", "CloakingSubsystemProperty method: Cast"),

    # --- HullProperty (1) ---
    0x00682f30: ("HullProperty__Cast", "HullProperty method: Cast"),

    # --- ImpulseEngineProperty (2) ---
    0x00683bc0: ("ImpulseEngineProperty__Cast", "ImpulseEngineProperty method: Cast"),
    0x00683e60: ("ImpulseEngineProperty__SetEngineSound", "ImpulseEngineProperty method: SetEngineSound"),

    # --- PoweredSubsystemProperty (1) ---
    0x0068a580: ("PoweredSubsystemProperty__Cast", "PoweredSubsystemProperty method: Cast"),

    # --- PowerProperty (1) ---
    0x0068b290: ("PowerProperty__Cast", "PowerProperty method: Cast"),

    # --- RepairSubsystemProperty (1) ---
    0x0068e5d0: ("RepairSubsystemProperty__Cast", "RepairSubsystemProperty method: Cast"),

    # --- SensorProperty (1) ---
    0x0068f360: ("SensorProperty__Cast", "SensorProperty method: Cast"),

    # --- ShipProperty (5) ---
    0x00691190: ("ShipProperty__Cast", "ShipProperty method: Cast"),
    0x006915b0: ("ShipProperty__SetShipName", "ShipProperty method: SetShipName"),
    0x00691620: ("ShipProperty__SetModelFilename", "ShipProperty method: SetModelFilename"),
    0x00691690: ("ShipProperty__SetAIString", "ShipProperty method: SetAIString"),
    0x00691700: ("ShipProperty__SetDeathExplosionSound", "ShipProperty method: SetDeathExplosionSound"),

    # --- TorpedoSystemProperty (1) ---
    0x00693ed0: ("TorpedoSystemProperty__Cast", "TorpedoSystemProperty method: Cast"),

    # --- TorpedoAmmoType (3) ---
    0x00694240: ("TorpedoAmmoType__SetTorpedoScript", "TorpedoAmmoType method: SetTorpedoScript"),
    0x006942f0: ("TorpedoAmmoType__GetPowerCost", "TorpedoAmmoType method: GetPowerCost"),
    0x00694330: ("TorpedoAmmoType__GetName", "TorpedoAmmoType method: GetName"),

    # --- WarpEngineProperty (1) ---
    0x006993e0: ("WarpEngineProperty__Cast", "WarpEngineProperty method: Cast"),

    # --- GameSpy (13) ---
    0x0069bfa0: ("GameSpy__ProcessQueryHandler", "GameSpy method: ProcessQueryHandler"),
    0x0069c4e0: ("GameSpy__RegisterHandlerNames", "GameSpy: registers SetGameMode/ProcessQuery name strings"),
    0x0069c580: ("GameSpy__BuildBasicResponse", "Build hostname/map/numplayers/maxplayers/gamemode response"),
    0x0069cc40: ("GameSpy__SetGameModeHandler", "GameSpy: handle game mode change event (copies mode string)"),
    0x0069ccd0: ("GameSpy__ConnectFailed", "GameSpy method: ConnectFailed"),
    0x0069d720: ("GameSpy__ProcessQueryHandler", "GameSpy method: ProcessQueryHandler"),
    0x006a9930: ("GameSpy__qr_parse_query", "GameSpy method: qr_parse_query"),
    0x006a9aa0: ("GameSpy__TokenizeString", "GameSpy method: TokenizeString"),
    0x006a9af0: ("GameSpy__qr_lookup_or_add_key", "GameSpy method: qr_lookup_or_add_key"),
    0x006aa770: ("GameSpy__SL_send_lan_broadcast", "Send \\status\\ to 255.255.255.255 ports 22101-22201"),
    0x006ac1e0: ("GameSpy__qr_handle_query", "GameSpy query dispatcher: 8 query types (basic/info/rules/players/etc)"),
    0x006ac950: ("GameSpy__qr_send_final", "Append \\validate\\ + \\final\\, send response"),
    0x006aca60: ("GameSpy__qr_send_heartbeat", "Send \\heartbeat\\<port>\\gamename\\bcommander to master"),

    # --- TGNetworkGroup (5) ---
    0x006a2d90: ("TGNetworkGroup__InsertPeerSorted", "TGNetworkGroup method: InsertPeerSorted"),
    0x006a2e60: ("TGNetworkGroup__RemoveAtIndex", "TGNetworkGroup method: RemoveAtIndex"),
    0x006a2f10: ("TGNetworkGroup__FindPeerByID", "TGNetworkGroup method: FindPeerByID"),
    0x006bb9d0: ("TGNetworkGroup__FindPeer", "TGNetworkGroup method: FindPeer"),
    0x006bba10: ("TGNetworkGroup__ReassignPeer", "TGNetworkGroup method: ReassignPeer"),

    # --- TGNetwork (27) ---
    0x006a2f60: ("TGNetwork__DeleteGroupByIndex", "TGNetwork method: DeleteGroupByIndex"),
    0x006b3a00: ("TGNetwork__ctor", "TGNetwork method: ctor"),
    0x006b3c40: ("TGNetwork__dtor", "TGNetwork method: dtor"),
    0x006b3ec0: ("TGNetwork__HostOrJoin", "TGNetwork method: HostOrJoin"),
    0x006b4060: ("TGNetwork__Disconnect", "TGNetwork method: Disconnect"),
    0x006b4560: ("TGNetwork__Update", "Main network tick: dequeue messages, post events"),
    0x006b4930: ("TGNetwork__GetState", "TGNetwork method: GetState"),
    0x006b4940: ("TGNetwork__CreateLocalPlayer", "TGNetwork method: CreateLocalPlayer"),
    0x006b4a50: ("TGNetwork__SetName", "TGNetwork method: SetName"),
    0x006b4c10: ("TGNetwork__Send", "Send TGMessage to specific peer by ID"),
    0x006b4de0: ("TGNetwork__SendTGMsgToGroup", "Send TGMessage to all peers in named group"),
    0x006b4ec0: ("TGNetwork__SendTGMessageToGroup", "TGNetwork method: SendTGMessageToGroup"),
    0x006b5080: ("TGNetwork__QueueMessageToPeer", "TGNetwork method: QueueMessageToPeer"),
    0x006b51e0: ("TGNetwork__BroadcastToAllPeers", "TGNetwork method: BroadcastToAllPeers"),
    0x006b5c90: ("TGNetwork__ProcessIncomingMessages", "recvfrom loop: decrypt, dispatch by type"),
    0x006b5f70: ("TGNetwork__DispatchIncomingQueue", "TGNetwork method: DispatchIncomingQueue"),
    0x006b63a0: ("TGNetwork__HandleNewConnection", "TGNetwork method: HandleNewConnection"),
    0x006b6640: ("TGNetwork__HandleIncomingData", "TGNetwork method: HandleIncomingData"),
    0x006b6a20: ("TGNetwork__ProcessDisconnectMessage", "TGNetwork method: ProcessDisconnectMessage"),
    0x006b7070: ("TGNetwork__SetLocalPlayerName", "TGNetwork method: SetLocalPlayerName"),
    0x006b7090: ("TGNetwork__SetEncryptor", "TGNetwork method: SetEncryptor"),
    0x006b70d0: ("TGNetwork__AddGroup", "TGNetwork method: AddGroup"),
    0x006b7410: ("TGNetwork__CreatePeer", "TGNetwork method: CreatePeer"),
    0x006b7540: ("TGNetwork__AllocPlayerID", "TGNetwork method: AllocPlayerID"),
    0x006b7590: ("TGNetwork__FreePlayerID", "TGNetwork method: FreePlayerID"),
    0x006b75b0: ("TGNetwork__HandleDisconnect", "TGNetwork method: HandleDisconnect"),
    0x006b7700: ("TGNetwork__GetTimeSinceLastReceive", "TGNetwork method: GetTimeSinceLastReceive"),

    # --- TGNetworkGroupManager (1) ---
    0x006a2fc0: ("TGNetworkGroupManager__FindGroupByName", "TGNetworkGroupManager method: FindGroupByName"),

    # --- NetFile (18) ---
    0x006a30c0: ("NetFile__Constructor", "NetFile method: Constructor"),
    0x006a3560: ("NetFile__RegisterHandlerNames", "Registers 'NetFile :: ReceiveMessageHandler' name string"),
    0x006a35b0: ("NetFile__SendChecksumRequest", "NetFile method: SendChecksumRequest"),
    0x006a3820: ("NetFile__ChecksumRequestSender", "Starts checksum exchange for a player (5 rounds)"),
    0x006a39b0: ("NetFile__ChecksumRequestBuilder", "NetFile method: ChecksumRequestBuilder"),
    0x006a3ea0: ("NetFile__FileReceiveHandler", "File transfer data delivery (S->C)"),
    0x006a4260: ("NetFile__ChecksumRequestHandler", "Server: receives client checksum response"),
    0x006a4560: ("NetFile__ChecksumResponseVerifier", "Compares client vs server checksums"),
    0x006a4a00: ("NetFile__ChecksumFailHandler", "NetFile method: ChecksumFailHandler"),
    0x006a4bb0: ("NetFile__ChecksumAllPassed", "All 5 rounds passed, triggers ET_CHECKSUM_COMPLETE"),
    0x006a4c10: ("NetFile__SystemChecksumFail", "Version/system checksum fail notification"),
    0x006a4d80: ("NetFile__ParseChecksumRequest", "NetFile method: ParseChecksumRequest"),
    0x006a4e70: ("NetFile__VerifyDirectoryChecksums", "NetFile method: VerifyDirectoryChecksums"),
    0x006a5570: ("NetFile__SendMismatchedFiles", "NetFile method: SendMismatchedFiles"),
    0x006a5660: ("NetFile__QueueFileForTransfer", "NetFile method: QueueFileForTransfer"),
    0x006a5860: ("NetFile__FileTransferProcessor", "NetFile method: FileTransferProcessor"),
    0x006a5df0: ("NetFile__ClientChecksumHandler", "Client: receives checksum request, computes hashes"),
    0x006a62f0: ("NetFile__ComputeFileContentChecksum", "NetFile method: ComputeFileContentChecksum"),

    # --- RAS (1) ---
    0x006a8170: ("RAS__IsDialupConnected", "RAS method: IsDialupConnected"),

    # --- BinkVideoManager (3) ---
    0x006af140: ("BinkVideoManager__RenderAll", "BinkVideoManager method: RenderAll"),
    0x006afd40: ("BinkVideoManager__SaveToStream", "BinkVideoManager method: SaveToStream"),
    0x006afdd0: ("BinkVideoManager__LoadFromStream", "BinkVideoManager method: LoadFromStream"),

    # --- BinkVideo (2) ---
    0x006b0030: ("BinkVideo__RenderFrame", "BinkVideo method: RenderFrame"),
    0x006b0360: ("BinkVideo__Close", "BinkVideo method: Close"),

    # --- TGWinsockPeer (3) ---
    0x006b3300: ("TGWinsockPeer__Constructor", "TGWinsockPeer method: Constructor"),
    0x006c08d0: ("TGWinsockPeer__ctor", "TGWinsockPeer method: ctor"),
    0x006c0b50: ("TGWinsockPeer__SetName", "TGWinsockPeer method: SetName"),

    # --- TGMessageQueue (2) ---
    0x006b3450: ("TGMessageQueue__dtor", "TGMessageQueue method: dtor"),
    0x006bb990: ("TGMessageQueue__ctor", "TGMessageQueue method: ctor"),

    # --- TGNetworkEvent (4) ---
    0x006b36e0: ("TGNetworkEvent__ctor_stream", "TGNetworkEvent method: ctor_stream"),
    0x006b3770: ("TGNetworkEvent__scalar_deleting_dtor", "TGNetworkEvent method: scalar_deleting_dtor"),
    0x006bb840: ("TGNetworkEvent__ctor", "TGNetworkEvent method: ctor"),
    0x006bb860: ("TGNetworkEvent__dtor", "TGNetworkEvent method: dtor"),

    # --- TGMessage (11) ---
    0x006b8290: ("TGMessage__RegisterFactory", "TGMessage method: RegisterFactory"),
    0x006b82a0: ("TGMessage__ctor", "TGMessage constructor"),
    0x006b8320: ("TGMessage__Reset", "TGMessage method: Reset"),
    0x006b8340: ("TGMessage__WriteToBuffer", "Serialize TGMessage payload to type 0x32 transport"),
    0x006b83f0: ("TGMessage__Factory", "TGMessage factory: create from transport stream"),
    0x006b8530: ("TGMessage__GetBuffer", "TGMessage method: GetBuffer"),
    0x006b8550: ("TGMessage__CopyCtor", "TGMessage method: CopyCtor"),
    0x006b8610: ("TGMessage__Clone", "TGMessage method: Clone"),
    0x006b8640: ("TGMessage__GetSize", "TGMessage method: GetSize"),
    0x006b89a0: ("TGMessage__SetBuffer", "TGMessage method: SetBuffer"),
    0x006bac70: ("TGMessage__CtorGuaranteed", "TGMessage method: CtorGuaranteed"),

    # --- TGWinsockNetwork (5) ---
    0x006b9b20: ("TGWinsockNetwork__CreateUDPSocket", "TGWinsockNetwork method: CreateUDPSocket"),
    0x006b9bb0: ("TGWinsockNetwork__SetPortNumber", "TGWinsockNetwork method: SetPortNumber"),
    0x006b9bf0: ("TGWinsockNetwork__ctor", "TGWinsockNetwork method: ctor"),
    0x006b9c80: ("TGWinsockNetwork__dtor", "TGWinsockNetwork method: dtor"),
    0x006ba160: ("TGWinsockNetwork__BanPlayerByIP", "TGWinsockNetwork method: BanPlayerByIP"),

    # --- TGBootMessage (2) ---
    0x006bac60: ("TGBootMessage__RegisterFactory", "TGBootMessage method: RegisterFactory"),
    0x006badb0: ("TGBootMessage__Factory", "TGBootMessage method: Factory"),

    # --- TGDataMessage (6) ---
    0x006bc5a0: ("TGDataMessage__RegisterFactory", "TGDataMessage method: RegisterFactory"),
    0x006bc5b0: ("TGDataMessage__ctor", "TGDataMessage method: ctor"),
    0x006bc610: ("TGDataMessage__WriteToBuffer", "TGDataMessage method: WriteToBuffer"),
    0x006bc6a0: ("TGDataMessage__Factory", "TGDataMessage method: Factory"),
    0x006bc720: ("TGDataMessage__CopyCtor", "TGDataMessage method: CopyCtor"),
    0x006bc740: ("TGDataMessage__Clone", "TGDataMessage method: Clone"),

    # --- TGHeaderMessage (3) ---
    0x006bd110: ("TGHeaderMessage__RegisterFactory", "TGHeaderMessage method: RegisterFactory"),
    0x006bd120: ("TGHeaderMessage__ctor", "TGHeaderMessage method: ctor"),
    0x006bd1f0: ("TGHeaderMessage__Factory", "TGHeaderMessage method: Factory"),

    # --- TGConnectMessage (3) ---
    0x006bdc30: ("TGConnectMessage__RegisterFactory", "TGConnectMessage method: RegisterFactory"),
    0x006bdc40: ("TGConnectMessage__ctor", "TGConnectMessage method: ctor"),
    0x006bdd10: ("TGConnectMessage__Factory", "TGConnectMessage method: Factory"),

    # --- TGConnectAckMsg (5) ---
    0x006be720: ("TGConnectAckMsg__RegisterFactory", "TGConnectAckMsg method: RegisterFactory"),
    0x006be730: ("TGConnectAckMsg__ctor", "TGConnectAckMsg method: ctor"),
    0x006be7c0: ("TGConnectAckMsg__dtor", "TGConnectAckMsg method: dtor"),
    0x006be860: ("TGConnectAckMsg__Factory", "TGConnectAckMsg method: Factory"),
    0x006be8e0: ("TGConnectAckMsg__CopyCtor", "TGConnectAckMsg method: CopyCtor"),

    # --- TGDisconnectMsg (3) ---
    0x006bf2d0: ("TGDisconnectMsg__RegisterFactory", "TGDisconnectMsg method: RegisterFactory"),
    0x006bf2e0: ("TGDisconnectMsg__ctor", "TGDisconnectMsg method: ctor"),
    0x006bf410: ("TGDisconnectMsg__Factory", "TGDisconnectMsg method: Factory"),

    # --- AlbyRulesCipher (5) ---
    0x006c2280: ("AlbyRulesCipher__Reset", "AlbyRulesCipher method: Reset"),
    0x006c22f0: ("AlbyRulesCipher__InitKey", "AlbyRulesCipher method: InitKey"),
    0x006c23c0: ("AlbyRulesCipher__PRNGStep", "AlbyRulesCipher method: PRNGStep"),
    0x006c2490: ("AlbyRulesCipher__Encrypt", "AlbyRulesCipher method: Encrypt"),
    0x006c2520: ("AlbyRulesCipher__Decrypt", "AlbyRulesCipher method: Decrypt"),

    # --- TGSocket (1) ---
    0x006c25a0: ("TGSocket__Close", "TGSocket method: Close"),

    # --- TGModelManager (14) ---
    0x006c3900: ("TGModelManager__IsModelLoaded", "TGModelManager method: IsModelLoaded"),
    0x006c3970: ("TGModelManager__LoadModel", "TGModelManager method: LoadModel"),
    0x006c39a0: ("TGModelManager__Unrefer", "TGModelManager method: Unrefer"),
    0x006c3a10: ("TGModelManager__Refer", "TGModelManager method: Refer"),
    0x006c3af0: ("TGModelManager__AddModel", "TGModelManager method: AddModel"),
    0x006c3c30: ("TGModelManager__FreeModel", "TGModelManager method: FreeModel"),
    0x006c3cf0: ("TGModelManager__Purge", "TGModelManager method: Purge"),
    0x006c3da0: ("TGModelManager__GetModel", "TGModelManager method: GetModel"),
    0x006c3e20: ("TGModelManager__GetCamera", "TGModelManager method: GetCamera"),
    0x006c3f00: ("TGModelManager__CloneModel", "TGModelManager method: CloneModel"),
    0x006c3f20: ("TGModelManager__CopyModel", "TGModelManager method: CopyModel"),
    0x006c3f50: ("TGModelManager__FreeAllModels", "TGModelManager method: FreeAllModels"),
    0x006c4010: ("TGModelManager__ClearIncrementalLoadQueue", "TGModelManager method: ClearIncrementalLoadQueue"),
    0x006c4080: ("TGModelManager__DoIncrementalLoad", "TGModelManager method: DoIncrementalLoad"),

    # --- TGAnimNode (8) ---
    0x006c4bb0: ("TGAnimNode__Copy", "TGAnimNode method: Copy"),
    0x006c4d20: ("TGAnimNode__UseAnimation", "TGAnimNode method: UseAnimation"),
    0x006c4d90: ("TGAnimNode__SetExclusiveAnimation", "TGAnimNode method: SetExclusiveAnimation"),
    0x006c5070: ("TGAnimNode__SetNonExclusiveAnimation", "TGAnimNode method: SetNonExclusiveAnimation"),
    0x006c5350: ("TGAnimNode__StopNonExclusiveAnimation", "TGAnimNode method: StopNonExclusiveAnimation"),
    0x006c53f0: ("TGAnimNode__SetExclusiveAnimationUseDefault", "TGAnimNode method: SetExclusiveAnimationUseDefault"),
    0x006c5460: ("TGAnimNode__UseAnimationPosition", "TGAnimNode method: UseAnimationPosition"),
    0x006c57b0: ("TGAnimNode__Stop", "TGAnimNode method: Stop"),

    # --- TGPropertyStore (2) ---
    0x006c8bd0: ("TGPropertyStore__SaveToStream", "TGPropertyStore method: SaveToStream"),
    0x006c8c70: ("TGPropertyStore__LoadFromStream", "TGPropertyStore method: LoadFromStream"),

    # --- NiApplication (6) ---
    0x006cd790: ("NiApplication__ctor", "NiApplication method: ctor"),
    0x007b7180: ("NiApplication__CtorBase", "NiApplication method: CtorBase"),
    0x007b7390: ("NiApplication__dtor", "NiApplication method: dtor"),
    0x007b74d0: ("NiApplication__ParseCommandLine", "NiApplication method: ParseCommandLine"),
    0x007b9090: ("NiApplication__HasCommandLineArg", "NiApplication method: HasCommandLineArg"),
    0x0086eff0: ("NiApplication__Create", "NiApplication method: Create"),

    # --- TGBufferStream (21) ---
    0x006cefe0: ("TGBufferStream__ctor", "TGBufferStream method: ctor"),
    0x006cf120: ("TGBufferStream__dtor", "TGBufferStream method: dtor"),
    0x006cf180: ("TGBufferStream__OpenBuffer", "TGBufferStream method: OpenBuffer"),
    0x006cf1c0: ("TGBufferStream__CloseBuffer", "TGBufferStream method: CloseBuffer"),
    0x006cf230: ("TGBufferStream__ReadBytes", "TGBufferStream method: ReadBytes"),
    0x006cf2b0: ("TGBufferStream__WriteBytes", "TGBufferStream method: WriteBytes"),
    0x006cf410: ("TGBufferStream__ReadCString", "TGBufferStream method: ReadCString"),
    0x006cf460: ("TGBufferStream__WriteCString", "TGBufferStream method: WriteCString"),
    0x006cf540: ("TGBufferStream__ReadByte", "TGBufferStream method: ReadByte"),
    0x006cf580: ("TGBufferStream__ReadBit", "TGBufferStream method: ReadBit"),
    0x006cf600: ("TGBufferStream__ReadShort", "TGBufferStream method: ReadShort"),
    0x006cf670: ("TGBufferStream__ReadInt", "TGBufferStream method: ReadInt"),
    0x006cf6b0: ("TGBufferStream__ReadFloat", "TGBufferStream method: ReadFloat"),
    0x006cf730: ("TGBufferStream__WriteByte", "TGBufferStream method: WriteByte"),
    0x006cf770: ("TGBufferStream__WriteBit", "TGBufferStream method: WriteBit"),
    0x006cf7f0: ("TGBufferStream__WriteShort", "TGBufferStream method: WriteShort"),
    0x006cf870: ("TGBufferStream__WriteInt", "TGBufferStream method: WriteInt"),
    0x006cf8b0: ("TGBufferStream__WriteFloat", "TGBufferStream method: WriteFloat"),
    0x006cf930: ("TGBufferStream__WriteObjectID", "TGBufferStream method: WriteObjectID"),
    0x006cf9b0: ("TGBufferStream__GetCursor", "TGBufferStream method: GetCursor"),
    0x006cf6a0: ("TGBufferStream__vReadInt", "Virtual ReadInt thunk (JMP [vtable+0x68])"),
    0x006d2370: ("TGBufferStream__ReadString", "TGBufferStream method: ReadString"),
    0x006d30e0: ("TGBufferStream__ReadCompressedVector4_ByteScale", "Read 4 bytes + decompress position with custom scale"),

    # --- TGLManager (3) ---
    0x006d04f0: ("TGLManager__ReleaseFile", "Decrement refcount on loaded TGL file"),
    0x006d0670: ("TGLManager__SaveToStream", "TGLManager method: SaveToStream"),
    0x006d06d0: ("TGLManager__LoadFromStream", "TGLManager method: LoadFromStream"),

    # --- TGFileStream (6) ---
    0x006d1fc0: ("TGFileStream__ctor", "Sets vtable 0x00895d60, allocates status object"),
    0x006d2050: ("TGFileStream__dtor", "Restores vtable, closes handle, frees status"),
    0x006d2080: ("TGFileStream__OpenFile", "fopen via CRT, sets +0x08 handle"),
    0x006d20e0: ("TGFileStream__CloseHandle", "fclose on +0x08 FILE*"),
    0x006d23c0: ("TGFileStream__WriteString", "strlen + write_size + write_data"),
    0x006d31f0: ("TGFileStream__GetError", "Returns error code from status object"),

    # --- TGBufferedFileStream (8) ---
    0x006d32d0: ("TGBufferedFileStream__ctor", "Extends TGFileStream, vtable 0x00895e58, adds buffer"),
    0x006d3350: ("TGBufferedFileStream__Open", "Opens file, checks w/W for write mode"),
    0x006d33c0: ("TGBufferedFileStream__Close", "Flushes buffer, frees memory, closes file"),
    0x006d3470: ("TGBufferedFileStream__Flush", "Writes buffered data to file, resets position"),
    0x006d38d0: ("TGBufferedFileStream__WriteInt", "Grow-check + write 4 bytes at buffer offset"),
    0x006d3910: ("TGBufferedFileStream__WriteUInt", "Same pattern as WriteInt"),
    0x006d3950: ("TGBufferedFileStream__WriteFloat", "Grow-check + write 4 bytes at buffer offset"),
    0x006d39d0: ("TGBufferedFileStream__WriteID", "Virtual dispatch via +0x6C"),

    # --- TGEvent (9) ---
    0x006d5c00: ("TGEvent__ctor", "TGEvent method: ctor"),
    0x006d5d70: ("TGEvent__dtor", "TGEvent method: dtor"),
    0x006d6270: ("TGEvent__SetSource", "TGEvent method: SetSource"),
    0x006d62b0: ("TGEvent__SetDestination", "TGEvent method: SetDestination"),
    0x006d6300: ("TGEvent__Release", "TGEvent method: Release (refcount--, dtor at 0)"),
    0x006d63a0: ("TGEvent__LookupInEventTable", "Lookup event by object ID in g_pTGEventObjectTable"),
    0x006d63f0: ("TGEvent__RegisterInEventTable", "Register event in g_pTGEventObjectTable hash table"),
    0x006d6480: ("TGEvent__UnregisterFromEventTable", "TGEvent method: UnregisterFromEventTable"),
    0x006d6810: ("TGEvent__Duplicate", "TGEvent method: Duplicate (factory clone)"),

    # --- TGStreamedObject (6) ---
    0x006d6200: ("TGStreamedObject__FactoryDeserialize", "Polymorphic factory: class ID -> construct from stream"),
    0x006f13e0: ("TGStreamedObject__CreateFromFactory", "TGStreamedObject method: CreateFromFactory"),
    0x006f31a0: ("TGStreamedObject__ctor", "TGStreamedObject method: ctor"),
    0x006f3270: ("TGStreamedObject__dtor", "TGStreamedObject method: dtor"),
    0x006f32d0: ("TGStreamedObject__WriteToStream", "TGStreamedObject method: WriteToStream"),
    0x006f3310: ("TGStreamedObject__ReadFromStream", "TGStreamedObject method: ReadFromStream"),

    # --- TGEventManager (14) ---
    0x006d6320: ("TGEventManager__CleanupObjectRefs", "TGEventManager method: CleanupObjectRefs"),
    0x006d65e0: ("TGEventManager__SaveEventsToStream", "Save event registrations to stream"),
    0x006d6780: ("TGEventManager__LoadEventsFromStream", "Load event registrations from stream"),
    0x006da190: ("TGEventManager__SaveToStream", "TGEventManager method: SaveToStream"),
    0x006da1e0: ("TGEventManager__LoadFromStream", "TGEventManager method: LoadFromStream"),
    0x006da240: ("TGEventManager__FixupReferences", "TGEventManager method: FixupReferences"),
    0x006da260: ("TGEventManager__FixupComplete", "TGEventManager method: FixupComplete"),
    0x006da2a0: ("TGEventManager__AddEvent", "Post event to global event manager"),
    0x006da2b0: ("TGEventManager__EnqueueEvent", "TGEventManager method: EnqueueEvent"),
    0x006da2c0: ("TGEventManager__ProcessEvents", "TGEventManager method: ProcessEvents"),
    0x006da300: ("TGEventManager__PostEvent", "TGEventManager method: PostEvent"),
    0x006db380: ("TGEventManager__RegisterHandler", "TGEventManager method: RegisterHandler"),
    0x006db620: ("TGEventManager__DispatchToBroadcastHandlers", "TGEventManager method: DispatchToBroadcastHandlers"),
    0x006de370: ("TGEventManager__DequeueEvent", "TGEventManager method: DequeueEvent"),

    # --- TGHandlerNameTable (2) ---
    0x006da3d0: ("TGHandlerNameTable__Register", "Register handler name + hash in g_TGHandlerNameTable"),
    0x006da450: ("TGHandlerNameTable__LookupByHash", "Lookup handler function ptr by hash in name table"),

    # --- TGEventHandlerTable (12) ---
    0x006d5850: ("TGEventHandlerTable__RegisterObject", "Create handler chain entry for object in global table"),
    0x006d8230: ("TGEventHandlerTable__FindHandlerChain", "Look up handler chain for event type (hash table)"),
    0x006d8270: ("TGEventHandlerTable__FindHandlerInParentChain", "Walk parent chain to find handler for event type"),
    0x006d82b0: ("TGEventHandlerTable__RemoveAllHandlers", "Remove all handler chains from table"),
    0x006d83e0: ("TGEventHandlerTable__DispatchToNextHandler", "Walk chain, invoke callbacks via TGConditionHandler"),
    0x006db530: ("TGEventHandlerTable__RemoveBroadcastHandler", "Remove broadcast handler by name"),
    0x006db590: ("TGEventHandlerTable__RemoveAllHandlersForObject", "Remove all handlers registered by an object"),
    0x006daf70: ("TGEventHandlerTable__SaveBroadcastHandlers", "Serialize broadcast handler table"),
    0x006db020: ("TGEventHandlerTable__LoadBroadcastHandlers", "Deserialize broadcast handler table"),
    0x006db1b0: ("TGEventHandlerTable__FixupBroadcastRefs", "Fixup broadcast handler object references"),
    0x006db230: ("TGEventHandlerTable__FixupBroadcastComplete", "Complete broadcast handler reference fixup"),
    0x006db670: ("TGEventHandlerTable__ClearBroadcastHandlers", "Remove and free all broadcast handler chains"),

    # --- TGInstanceHandlerTable (5) ---
    0x006d7b30: ("TGInstanceHandlerTable__ctor", "Per-object handler hash table (0x25 buckets)"),
    0x006d7b80: ("TGInstanceHandlerTable__dtor", "Destroy per-object handler table"),
    0x006d7c30: ("TGInstanceHandlerTable__SaveToStream", "Serialize per-object handler chains"),
    0x006d7d00: ("TGInstanceHandlerTable__LoadFromStream", "Deserialize per-object handler chains"),
    0x006d7eb0: ("TGInstanceHandlerTable__AddHandler", "Add callback for event type in instance table"),

    # --- TGTimerManager (9) ---
    0x006dc240: ("TGTimerManager__ctor", "TGTimerManager constructor (stores event mgr at +0x08)"),
    0x006dc5d0: ("TGTimerManager__Init", "TGTimerManager init (+0x04=0)"),
    0x006dc2e0: ("TGTimerManager__SaveToStream", "TGTimerManager method: SaveToStream"),
    0x006dc310: ("TGTimerManager__LoadFromStream", "TGTimerManager method: LoadFromStream"),
    0x006dc3c0: ("TGTimerManager__FixupReferences", "TGTimerManager method: FixupReferences"),
    0x006dc3d0: ("TGTimerManager__FixupComplete", "TGTimerManager method: FixupComplete"),
    0x006dc3f0: ("TGTimerManager__AddTimer", "TGTimerManager method: AddTimer"),
    0x006dc470: ("TGTimerManager__DeleteTimer", "TGTimerManager method: DeleteTimer"),
    0x006dc490: ("TGTimerManager__Update", "TGTimerManager method: Update"),

    # --- TGTimer (8) ---
    0x006dcf50: ("TGTimer__ctor", "TGTimer method: ctor"),
    0x006dd0c0: ("TGTimer__dtor", "TGTimer method: dtor"),
    0x006dd270: ("TGTimer__SetEvent", "TGTimer method: SetEvent"),
    0x006dd2a0: ("TGTimer__ReleaseEvent", "TGTimer method: ReleaseEvent"),
    0x006dd2c0: ("TGTimer__Reschedule", "TGTimer method: Reschedule"),
    0x006dd380: ("TGTimer__GetTGTimerPtr", "TGTimer method: GetTGTimerPtr"),
    0x006dd3d0: ("TGTimer__InsertIntoHashTable", "TGTimer method: InsertIntoHashTable"),
    0x006dd460: ("TGTimer__RemoveFromHashTable", "TGTimer method: RemoveFromHashTable"),

    # --- TGEventTarget (1) ---
    0x006dd680: ("TGEventTarget__LoadAllFromStream", "TGEventTarget method: LoadAllFromStream"),

    # --- TGEventQueue (7) ---
    0x006de1d0: ("TGEventQueue__SaveToStream", "Serialize event queue (head/tail IDs + count)"),
    0x006de240: ("TGEventQueue__LoadFromStream", "Deserialize event queue from stream"),
    0x006de280: ("TGEventQueue__FixupReferences", "Resolve event queue object ID references"),
    0x006de2c0: ("TGEventQueue__FixupComplete", "Complete event queue reference fixup"),
    0x006de310: ("TGEventQueue__Clear", "Dequeue all events from queue"),
    0x006de330: ("TGEventQueue__Enqueue", "TGEventQueue method: Enqueue"),
    0x006dee60: ("TGEventQueue__ctor_inner", "Init event queue fields (head=0, tail=0, count=0)"),

    # --- TGSortedTimerList (2) ---
    0x006df000: ("TGSortedTimerList__Insert", "TGSortedTimerList method: Insert"),
    0x006df0a0: ("TGSortedTimerList__PopHead", "TGSortedTimerList method: PopHead"),

    # --- TGCallback (8) ---
    0x006e09e0: ("TGCallback__ctor", "TGCallback ctor (vtable 0x008960f4, 5 fields, 0x14 bytes)"),
    0x006e0a00: ("TGCallback__dtor", "TGCallback dtor (free owned string)"),
    0x006e0a10: ("TGCallback__FreeString", "Free function name string at +0x10 if owned"),
    0x006e0d40: ("TGCallback__InvokePythonFunction", "Import module.func and call from C++"),
    0x006e0e00: ("TGCallback__SetFunctionByName", "Set callback as named C++ function (string copy)"),
    0x006e0e70: ("TGCallback__SetFunctionByHash", "Set callback by hash lookup in handler name table"),
    0x006e0ec0: ("TGCallback__SetIsPythonCallback", "Set/clear bit 1 of flags (Python vs C++ callback)"),
    0x006e0ee0: ("TGCallback__SetIsMethodCallback", "Set/clear bit 0 of flags (method vs function)"),

    # --- TGConditionHandler (19) ---
    0x006e0c30: ("TGConditionHandler__InvokeCallback", "Invoke C++/Python callback with event + handler object"),
    0x006e1870: ("TGConditionHandler__ctor", "TGConditionHandler ctor (two sorted arrays, vtable 0x00896104)"),
    0x006e1900: ("TGConditionHandler__dtor", "TGConditionHandler dtor (free sorted arrays)"),
    0x006e1960: ("TGConditionHandler__SaveHandlerEntries", "Serialize handler entries with object IDs"),
    0x006e1a30: ("TGConditionHandler__LoadHandlerEntries", "Deserialize handler entries, rebuild sorted array"),
    0x006e1c00: ("TGConditionHandler__FixupReferences", "Resolve handler entry object IDs to pointers"),
    0x006e1c50: ("TGConditionHandler__FixupComplete", "Complete handler entry reference fixup"),
    0x006e1cd0: ("TGConditionHandler__AddEntry", "Create entry node and insert in sorted position"),
    0x006e1d60: ("TGConditionHandler__InsertSorted", "Insert handler entry with sort key from object ID"),
    0x006e1ed0: ("TGConditionHandler__RemoveByName", "Find and remove handler by name hash"),
    0x006e2030: ("TGConditionHandler__MatchEntry", "Match handler entry by object + name/hash"),
    0x006e20b0: ("TGConditionHandler__RemoveAllForObject", "Remove all handler entries for a given object"),
    0x006e21d0: ("TGConditionHandler__DispatchEvent", "Dispatch event to all matching handlers (broadcast + targeted)"),
    0x006e2310: ("TGConditionHandler__RemoveAllEntries", "Iterate all entries and remove each"),
    0x006e2330: ("TGConditionHandler__FindInsertionPoint", "Binary search for sorted insertion index"),
    0x006e2380: ("TGConditionHandler__FindFirstByKey", "Binary search for first entry with matching key"),
    0x006e23f0: ("TGConditionHandler__RemoveAtIndex", "Remove handler entry at specific index"),
    0x006e24d0: ("TGConditionHandler__SetAtIndex", "Set entry in sorted array with active-count tracking"),
    0x006e25a0: ("TGConditionHandler__Resize", "Reallocate sorted handler array"),

    # --- TGHandlerListEntry (3) ---
    0x006e2f60: ("TGHandlerListEntry__ctor", "Handler list entry ctor (obj=0, callback=0, deleted=0)"),
    0x006e2f70: ("TGHandlerListEntry__dtor", "Handler list entry dtor (destroy callback, free)"),
    0x006e2f90: ("TGHandlerListEntry__GetObjectID", "Get object ID from handler list entry chain"),

    # --- TGConditionHandler persistence (1, already named) ---
    0x006ea2a0: ("TGConditionHandler__SaveToStream", "TGConditionHandler method: SaveToStream"),

    # --- TGInputManager (16) ---
    0x006e4810: ("TGInputManager__SetGamepadButtonState", "TGInputManager method: SetGamepadButtonState"),
    0x006e5380: ("TGInputManager__KeyEvent", "TGInputManager method: KeyEvent"),
    0x006e56f0: ("TGInputManager__SendKeyRepeatEvent", "TGInputManager method: SendKeyRepeatEvent"),
    0x006e5760: ("TGInputManager__RegisterUnicodeKey", "TGInputManager method: RegisterUnicodeKey"),
    0x006e5a70: ("TGInputManager__GetUnicodeKey", "TGInputManager method: GetUnicodeKey"),
    0x006e5b00: ("TGInputManager__GetScanCode", "TGInputManager method: GetScanCode"),
    0x006e5b50: ("TGInputManager__SetCurrentUnicodeKeyList", "TGInputManager method: SetCurrentUnicodeKeyList"),
    0x006e5c40: ("TGInputManager__SetDisplayStringForUnicode", "TGInputManager method: SetDisplayStringForUnicode"),
    0x006e5dc0: ("TGInputManager__GetDisplayStringFromUnicode", "TGInputManager method: GetDisplayStringFromUnicode"),
    0x006e5f90: ("TGInputManager__MouseEvent", "TGInputManager method: MouseEvent"),
    0x006e6390: ("TGInputManager__GamepadEvent", "TGInputManager method: GamepadEvent"),
    0x006e6420: ("TGInputManager__UpdateDevices", "TGInputManager method: UpdateDevices"),
    0x006e6430: ("TGInputManager__Poll", "TGInputManager method: Poll"),
    0x006e7150: ("TGInputManager__PauseMouseCursorMoveTo", "TGInputManager method: PauseMouseCursorMoveTo"),
    0x006e7180: ("TGInputManager__ResumeMouseCursorMoveTo", "TGInputManager method: ResumeMouseCursorMoveTo"),
    0x00728740: ("TGInputManager__SaveToStream", "TGInputManager method: SaveToStream"),

    # --- TGCameraManager (2) ---
    0x006e7330: ("TGCameraManager__SaveToStream", "TGCameraManager method: SaveToStream"),
    0x006e73d0: ("TGCameraManager__LoadFromStream", "TGCameraManager method: LoadFromStream"),

    # --- TGModelPropertyManager (11) ---
    0x006e96b0: ("TGModelPropertyManager__RegisterGlobalTemplate", "TGModelPropertyManager method: RegisterGlobalTemplate"),
    0x006e9880: ("TGModelPropertyManager__RegisterLocalTemplate", "TGModelPropertyManager method: RegisterLocalTemplate"),
    0x006e9a50: ("TGModelPropertyManager__FindByNameAndType", "TGModelPropertyManager method: FindByNameAndType"),
    0x006e9ba0: ("TGModelPropertyManager__ClearLocalTemplates", "TGModelPropertyManager method: ClearLocalTemplates"),
    0x006e9c00: ("TGModelPropertyManager__ClearGlobalTemplates", "TGModelPropertyManager method: ClearGlobalTemplates"),
    0x006e9f40: ("TGModelPropertyManager__ApplyFilters", "TGModelPropertyManager method: ApplyFilters"),
    0x006ea0e0: ("TGModelPropertyManager__RegisterFilter", "TGModelPropertyManager method: RegisterFilter"),
    0x006ea1a0: ("TGModelPropertyManager__ClearRegisteredFilters", "TGModelPropertyManager method: ClearRegisteredFilters"),
    0x006ea220: ("TGModelPropertyManager__IsGlobalTemplate", "TGModelPropertyManager method: IsGlobalTemplate"),
    0x006ea260: ("TGModelPropertyManager__IsLocalTemplate", "TGModelPropertyManager method: IsLocalTemplate"),
    0x006ea320: ("TGModelPropertyManager__LoadFromStream", "Load model property sets from stream"),

    # --- TGModelPropertyInstance (1) ---
    0x006ed480: ("TGModelPropertyInstance__UseOriginalTemplate", "TGModelPropertyInstance method: UseOriginalTemplate"),

    # --- TGModelPropertyList (2) ---
    0x006ee090: ("TGModelPropertyList__BeginIteration", "TGModelPropertyList method: BeginIteration"),
    0x006ee0a0: ("TGModelPropertyList__GetNext", "TGModelPropertyList method: GetNext"),

    # --- TGEventResponder (1) ---
    0x006f0ee0: ("TGEventResponder__ForwardEvent", "Look up game object by ID"),

    # --- DebugTrace (1) ---
    0x006f1880: ("DebugTrace__Noop", "DebugTrace method: Noop"),

    # --- TGStreamedObjectEx (1) ---
    0x006f2590: ("TGStreamedObjectEx__ctor", "TGStreamedObjectEx method: ctor"),

    # --- TGString (8) ---
    0x006f3e90: ("TGString__ctor", "TGString method: ctor"),
    0x006f3ef0: ("TGString__dtor", "TGString method: dtor"),
    0x006f41e0: ("TGString__FindC", "TGString method: FindC"),
    0x006f4260: ("TGString__Find", "TGString method: Find"),
    0x006f43e0: ("TGString__CompareC", "TGString method: CompareC"),
    0x006f4450: ("TGString__Compare", "TGString method: Compare"),
    0x006f47c0: ("TGString__SetString", "TGString method: SetString"),
    0x006f4cc0: ("TGString__Assign", "TGString method: Assign"),

    # --- TGWString (3) ---
    0x006f4000: ("TGWString__ReadFromStream", "TGWString method: ReadFromStream"),
    0x006f4ce0: ("TGWString__Assign", "TGWString method: Assign"),
    0x006f4ee0: ("TGWString__CopyFrom", "TGWString method: CopyFrom"),

    # --- WString (1) ---
    0x006f56f0: ("WString__ToASCII", "__fastcall: WString -> ASCII. 93 callers, NO NULL check (crash risk)"),

    # --- TG (2) ---
    0x006f8490: ("TG__ImportAndGetAttr", "TG method: ImportAndGetAttr"),
    0x006f8650: ("TG__ReadPythonVariable", "TG method: ReadPythonVariable"),

    # --- PythonModules (3) ---
    0x006fa150: ("PythonModules__InitPickleUnpickler", "PythonModules method: InitPickleUnpickler"),
    0x006faa90: ("PythonModules__SaveToStream", "PythonModules method: SaveToStream"),
    0x006faf70: ("PythonModules__LoadFromStream", "PythonModules method: LoadFromStream"),

    # --- PyEmbed (3) ---
    0x006fa410: ("PyEmbed__UnserializePython", "PyEmbed method: UnserializePython"),
    0x006fb1a0: ("PyEmbed__Serialize", "PyEmbed method: Serialize"),
    0x006fb410: ("PyEmbed__Unserialize", "PyEmbed method: Unserialize"),

    # --- TGAction (2) ---
    0x006fe500: ("TGAction__Cast", "TGAction method: Cast"),
    0x006fe760: ("TGAction__AddCompletedEvent", "TGAction method: AddCompletedEvent"),

    # --- TGActionManager (2) ---
    0x006ff1f0: ("TGActionManager__RegisterHandlerNames", "TGActionManager: registers ActionCompleted/ActionSkip/PlaySequence name strings"),
    0x006ff470: ("TGActionManager__SaveToStream", "TGActionManager method: SaveToStream"),

    # --- TGScriptAction (2) ---
    0x006ff6e0: ("TGScriptAction__ctor", "TGScriptAction method: ctor"),
    0x006ff940: ("TGScriptAction__AddParam", "TGScriptAction method: AddParam"),

    # --- TGSequence (4) ---
    0x007004c0: ("TGSequence__ctor", "TGSequence method: ctor"),
    0x00700710: ("TGSequence__AddAction", "TGSequence method: AddAction"),
    0x007007f0: ("TGSequence__AppendAction", "TGSequence method: AppendAction"),
    0x00700f10: ("TGSequence__Cast", "TGSequence method: Cast"),

    # --- TGActionScript (2) ---
    0x007012d0: ("TGActionScript__SaveAllToStream", "TGActionScript method: SaveAllToStream"),
    0x00701490: ("TGActionScript__LoadAllFromStream", "TGActionScript method: LoadAllFromStream"),

    # --- TGSoundAction (1) ---
    0x00702fa0: ("TGSoundAction__ctor", "TGSoundAction method: ctor"),

    # --- TGAnimAction (1) ---
    0x00703f90: ("TGAnimAction__ctor", "TGAnimAction method: ctor"),

    # --- PhonemeList (1) ---
    0x00707b80: ("PhonemeList__SaveToStream", "Save phoneme animation data to stream"),

    # --- TGSoundRegion (6) ---
    0x0070dd90: ("TGSoundRegion__ctor", "TGSoundRegion method: ctor"),
    0x0070e0a0: ("TGSoundRegion__GetRegion", "TGSoundRegion method: GetRegion"),
    0x0070e0f0: ("TGSoundRegion__AddSound", "TGSoundRegion method: AddSound"),
    0x0070e180: ("TGSoundRegion__RemoveSound", "TGSoundRegion method: RemoveSound"),
    0x0070e260: ("TGSoundRegion__SetFilter", "TGSoundRegion method: SetFilter"),
    0x0070e790: ("TGSoundRegion__ApplySoundFilter", "TGSoundRegion method: ApplySoundFilter"),

    # --- TGSoundRegionManager (1) ---
    0x0070e5e0: ("TGSoundRegionManager__SaveToStream", "Save sound regions to stream"),

    # --- TGSoundSystem (1) ---
    0x0070e6d0: ("TGSoundSystem__LoadObjectsFromStream", "TGSoundSystem method: LoadObjectsFromStream"),

    # --- TGSoundManager (16) ---
    0x0070f400: ("TGSoundManager__Reload", "TGSoundManager method: Reload"),
    0x0070f7a0: ("TGSoundManager__RegisterHandlerNames", "TGSoundManager method: RegisterHandlerNames"),
    0x0070f7c0: ("TGSoundManager__RegisterHandlers", "TGSoundManager method: RegisterHandlers"),
    0x0070f7e0: ("TGSoundManager__Update", "TGSoundManager method: Update"),
    0x0070fbb0: ("TGSoundManager__GetSound", "TGSoundManager method: GetSound"),
    0x0070fc10: ("TGSoundManager__GetPlayingSound", "TGSoundManager method: GetPlayingSound"),
    0x0070fcd0: ("TGSoundManager__PlaySound", "TGSoundManager method: PlaySound"),
    0x0070fd00: ("TGSoundManager__StopSound", "TGSoundManager method: StopSound"),
    0x0070fe70: ("TGSoundManager__StopAllSounds", "TGSoundManager method: StopAllSounds"),
    0x0070feb0: ("TGSoundManager__StopAllSoundsInGroup", "TGSoundManager method: StopAllSoundsInGroup"),
    0x0070ff40: ("TGSoundManager__DeleteSound", "TGSoundManager method: DeleteSound"),
    0x007100a0: ("TGSoundManager__DeleteAllSounds", "TGSoundManager method: DeleteAllSounds"),
    0x00710140: ("TGSoundManager__DeleteAllSoundsInGroup", "TGSoundManager method: DeleteAllSoundsInGroup"),
    0x00711460: ("TGSoundManager__HandleDeleteSoundEvent", "TGSoundManager method: HandleDeleteSoundEvent"),
    0x00711560: ("TGSoundManager__SaveToStream", "TGSoundManager method: SaveToStream"),
    0x00711750: ("TGSoundManager__LoadFromStream", "Load sound manager state from stream"),

    # --- TGMusic (2) ---
    0x007148e0: ("TGMusic__RegisterHandlerNames", "TGMusic method: RegisterHandlerNames"),
    0x00714910: ("TGMusic__RegisterHandlers", "TGMusic method: RegisterHandlers"),

    # --- TGMusicManager (1) ---
    0x00714b50: ("TGMusicManager__SaveToStream", "TGMusicManager method: SaveToStream"),

    # --- NiSmallObjectAlloc (2) ---
    0x00717b70: ("NiSmallObjectAlloc__FindPool", "NiSmallObjectAlloc method: FindPool"),
    0x00718010: ("NiSmallObjectAlloc__Alloc", "NiSmallObjectAlloc method: Alloc"),

    # --- NiClock (4) ---
    0x0071a8c0: ("NiClock__InitGlobal", "NiClock method: InitGlobal"),
    0x0071a8f0: ("NiClock__ctor", "NiClock method: ctor"),
    0x0071a9e0: ("NiClock__Update", "NiClock method: Update"),
    0x0071acc0: ("NiClock__GetCurrentTime", "NiClock method: GetCurrentTime"),

    # --- TGConfigFile (3) ---
    0x0071cb60: ("TGConfigFile__GetInt", "TGConfigFile method: GetInt"),
    0x0071d180: ("TGConfigFile__HasKey", "TGConfigFile method: HasKey"),
    0x0071d1e0: ("TGConfigFile__Load", "TGConfigFile method: Load"),

    # --- FPSCounter (1) ---
    0x00727a40: ("FPSCounter__Update", "FPSCounter method: Update"),

    # --- TGRootPane (2) ---
    0x00727fe0: ("TGRootPane__RegisterHandlerNames", "TGRootPane: registers Mouse/Keyboard/Gamepad name strings"),
    0x00728020: ("TGRootPane__RegisterHandlers", "TGRootPane: registers Mouse/Keyboard/Gamepad event handlers"),

    # --- TGIconManager (7) ---
    0x00729dc0: ("TGIconManager__SetDisplayInfo", "TGIconManager method: SetDisplayInfo"),
    0x00729e70: ("TGIconManager__RegisterIconGroup", "TGIconManager method: RegisterIconGroup"),
    0x00729fa0: ("TGIconManager__CreateIconGroup", "TGIconManager method: CreateIconGroup"),
    0x0072a000: ("TGIconManager__AddIconGroup", "TGIconManager method: AddIconGroup"),
    0x0072a080: ("TGIconManager__Purge", "TGIconManager method: Purge"),
    0x0072a150: ("TGIconManager__GetIconGroup", "TGIconManager method: GetIconGroup"),
    0x0072a690: ("TGIconManager__Draw", "TGIconManager method: Draw"),

    # --- TGIconGroup (3) ---
    0x0072bde0: ("TGIconGroup__Reset", "TGIconGroup method: Reset"),
    0x0072bf70: ("TGIconGroup__SetName", "TGIconGroup method: SetName"),
    0x0072bfe0: ("TGIconGroup__LoadIconTexture", "TGIconGroup method: LoadIconTexture"),

    # --- TGPane (6) ---
    0x0072dc90: ("TGPane__Cast", "TGPane method: Cast"),
    0x0072dcc0: ("TGPane__ctor", "TGPane method: ctor"),
    0x0072e120: ("TGPane__RegisterHandlerNames", "TGPane: registers Mouse/Keyboard/Gamepad/Control name strings"),
    0x0072e180: ("TGPane__RegisterHandlers", "TGPane: registers Mouse/Keyboard/Gamepad/Control event handlers"),
    0x0072e1e0: ("TGPane__MouseHandler", "TGPane method: MouseHandler"),
    0x0072e350: ("TGPane__KeyboardHandler", "TGPane method: KeyboardHandler"),

    # --- TGUIObject (2) ---
    0x00730e70: ("TGUIObject__RegisterHandlerNames", "TGUIObject: registers Mouse/Keyboard name strings"),
    0x00730ea0: ("TGUIObject__RegisterHandlers", "TGUIObject: registers Mouse/Keyboard event handlers"),
    0x00730ed0: ("TGUIObject__MouseHandler", "TGUIObject: handle mouse event"),

    # --- TGCursorManager (3) ---
    0x00733ce0: ("TGCursorManager__SaveReference", "TGCursorManager method: SaveReference"),
    0x00733d10: ("TGCursorManager__LoadReference", "TGCursorManager method: LoadReference"),
    0x00733d30: ("TGCursorManager__FixupReferences", "TGCursorManager method: FixupReferences"),

    # --- TGFontManager (5) ---
    0x00734db0: ("TGFontManager__CreateFontGroup", "TGFontManager method: CreateFontGroup"),
    0x00734e20: ("TGFontManager__AddFontGroup", "TGFontManager method: AddFontGroup"),
    0x00734f10: ("TGFontManager__SetDefaultFont", "TGFontManager method: SetDefaultFont"),
    0x00734f70: ("TGFontManager__GetFontGroup", "TGFontManager method: GetFontGroup"),
    0x00735280: ("TGFontManager__RemoveGroup", "TGFontManager method: RemoveGroup"),

    # --- TGConsole (2) ---
    0x00736900: ("TGConsole__RegisterHandlerNames", "TGConsole method: RegisterHandlerNames"),
    0x00736930: ("TGConsole__RegisterHandlers", "TGConsole method: RegisterHandlers"),

    # --- TGStringDialog (4) ---
    0x00737e40: ("TGStringDialog__RegisterHandlers", "TGStringDialog: registers Mouse/DialogEvent event handlers"),
    0x00737e70: ("TGStringDialog__RegisterHandlerNames", "TGStringDialog: registers DialogEventHandler name string"),
    0x00737e90: ("TGStringDialog__DialogEventHandler", "TGStringDialog: handle string input dialog event"),

    # --- TGDialogWindow (4) ---
    0x00738c80: ("TGDialogWindow__RegisterHandlerNames", "TGDialogWindow: registers Mouse/DialogEvent name strings"),
    0x00738cb0: ("TGDialogWindow__RegisterHandlers", "TGDialogWindow: registers Mouse/DialogEvent event handlers"),
    0x00739220: ("TGDialogWindow__DialogEventHandler", "TGDialogWindow: handle dialog event"),

    # --- TGIcon (2) ---
    0x0073d2f0: ("TGIcon__ctor", "TGIcon method: ctor"),
    0x0073d4d0: ("TGIcon__SizeToArtwork", "TGIcon method: SizeToArtwork"),

    # --- TGButtonBase (2) ---
    0x0073f7d0: ("TGButtonBase__RegisterHandlerNames", "TGButtonBase method: RegisterHandlerNames"),
    0x0073f800: ("TGButtonBase__RegisterHandlers", "TGButtonBase method: RegisterHandlers"),

    # --- TGFontGroup (1) ---
    0x00744540: ("TGFontGroup__MapChar", "TGFontGroup method: MapChar"),

    # --- NiDX7Renderer (21) ---
    0x007b9ef0: ("NiDX7Renderer__BuildDeviceSelectionDialog", "Builds Win32 DLGTEMPLATE: 'Select New DirectDraw Driver'"),
    0x007ba2e0: ("NiDX7Renderer__CreateFromDialog", "Shows device selection dialog, loops until Create succeeds"),
    0x007c09c0: ("NiDX7Renderer__Create", "NiDX7Renderer method: Create"),
    0x007c0ea0: ("NiDX7Renderer__Shutdown", "NiDX7Renderer method: Shutdown"),
    0x007c3480: ("NiDX7Renderer__CreateD3DDevice", "NiDX7Renderer method: CreateD3DDevice"),
    0x007c4850: ("NiDX7Renderer__LogInfo", "Format: 'NI D3D Renderer: %s' + OutputDebugString"),
    0x007c4880: ("NiDX7Renderer__LogWarning", "Format: 'NI D3D Renderer WARNING: %s' + OutputDebugString"),
    0x007c48b0: ("NiDX7Renderer__LogError", "Format: 'NI D3D Renderer ERROR: %s' + OutputDebugString"),
    0x007c7d90: ("NiDX7Renderer__DestroyAdapter", "NiDX7Renderer method: DestroyAdapter"),
    0x007c7f80: ("NiDX7Renderer__InitDirectDraw", "NiDX7Renderer method: InitDirectDraw"),
    0x007c8eb0: ("NiDX7Renderer__EnumerateAdapters", "NiDX7Renderer method: EnumerateAdapters"),
    0x007c9020: ("NiDX7Renderer__SetDisplayMode", "SetCooperativeLevel + SetDisplayMode, 'Set Display Mode failed'"),
    0x007c96c0: ("NiDX7Renderer__CreateFrontBuffer", "Primary DirectDraw surface creation"),
    0x007c98c0: ("NiDX7Renderer__CreateBackBuffer", "Back buffer surface creation"),
    0x007c99e0: ("NiDX7Renderer__CreateZBuffer", "DirectDraw Z-buffer surface creation"),
    0x007c9df0: ("NiDX7Renderer__InitAdapter", "NiDX7Renderer method: InitAdapter"),
    0x007ca1d0: ("NiDX7Renderer__CreateFramebuffers", "NiDX7Renderer method: CreateFramebuffers"),
    0x007ccd10: ("NiDX7Renderer__CreateTexturePipeline", "NiDX7Renderer method: CreateTexturePipeline"),
    0x007ce9c0: ("NiDX7Renderer__DetectMultitextureModes", "Tests single/multi-pass texture combos, 'Number of available modes'"),
    0x007d2230: ("NiDX7Renderer__CreateRenderStateMgr", "NiDX7Renderer method: CreateRenderStateMgr"),
    0x007d5080: ("NiDX7Renderer__CreateTextureManager", "'Attempting to create texture manager' + success string"),

    # --- NiDX7TextureManager (1) ---
    0x007d3460: ("NiDX7TextureManager__QueryTextureFormats", "'Texture format query failed', enumerates D3D pixel formats"),

    # --- NiDX7Texture (2) ---
    0x007d62a0: ("NiDX7Texture__CreateSurface", "'(TexDebug): Create Texture failed', creates DDraw texture surface"),
    0x007d6380: ("NiDX7Texture__ComputeTextureKey", "'(TexDebug): Non-square texture', packs texture properties"),

    # --- NiApp (3) ---
    0x007e7f70: ("NiApp__BeginFrame", "NiApp method: BeginFrame"),
    0x007e7fa0: ("NiApp__DrawScene", "NiApp method: DrawScene"),
    0x007e81b0: ("NiApp__Present", "NiApp method: Present"),

    # --- NiMatrix3 (2) ---
    0x00813a40: ("NiMatrix3__TransformVector", "Matrix * vector multiplication"),
    0x00813aa0: ("NiMatrix3__TransposeTransformVector", "Matrix^T * vector multiplication"),

    # --- NiStream (1) ---
    0x00817a40: ("NiStream__LoadFile", "NiStream method: LoadFile"),

    # --- CRT (4) ---
    0x00859530: ("CRT__memmove", "CRT method: memmove"),
    0x00859865: ("CRT__ArrayDestructor", "CRT method: ArrayDestructor"),
    0x008599b9: ("CRT__sprintf", "CRT method: sprintf"),
    0x00859d64: ("CRT__ArrayConstructor", "CRT method: ArrayConstructor"),

    # =======================================================================
    # Phase 8H: Cross-reference mining (103 functions)
    # =======================================================================

    # --- UI / Map Window (1) ---
    0x004fea50: ("MapWindow__ExitMapView", "MapWindow: exit map view"),

    # --- Weapons Display (11) ---
    0x005499a0: ("WeaponsDisplay__HandleFireButton", "WeaponsDisplay: handle fire button"),
    0x00549a50: ("WeaponsDisplay__HandleCloakButton", "WeaponsDisplay: handle cloak button"),
    0x00549d70: ("WeaponsDisplay__UpdateFiringStatus", "WeaponsDisplay: update firing status"),
    0x00549ed0: ("WeaponsDisplay__UpdateWarpStatus", "WeaponsDisplay: update warp status"),
    0x00549f30: ("WeaponsDisplay__UpdateTorpedoSelector", "WeaponsDisplay: update torpedo selector"),
    0x00549c60: ("WeaponsDisplay__ScheduleRefreshTimer", "WeaponsDisplay: schedule refresh timer"),
    0x00549850: ("WeaponsDisplay__CycleTorpedoType", "WeaponsDisplay: cycle torpedo type"),
    0x00549920: ("WeaponsDisplay__HandleFiringChainChanged", "WeaponsDisplay: handle firing chain changed"),
    0x00549980: ("WeaponsDisplay__HandleFireButtonEvent", "WeaponsDisplay: handle fire button event"),
    0x00549ac0: ("WeaponsDisplay__HandleKeyboardNavigation", "WeaponsDisplay: handle keyboard navigation"),
    0x0054a120: ("WeaponsDisplay__HandleSetPlayerEvent", "WeaponsDisplay: handle set player event"),

    # --- Weapons Control Pane (3) ---
    0x00548120: ("WeaponsCtrlPane__BuildTorpedoControls", "WeaponsCtrlPane: build torpedo toggle/spread controls"),
    0x00548a00: ("WeaponsCtrlPane__BuildPhaserControls", "WeaponsCtrlPane: build phaser intensity toggle"),
    0x00548e60: ("WeaponsCtrlPane__BuildTractorCloakControls", "WeaponsCtrlPane: build tractor/cloak toggles"),

    # --- Tactical Weapons Control (1) ---
    0x00544a00: ("TacWeaponsCtrl__HandleTorpedoReloadEvent", "TacWeaponsCtrl: handle torpedo reload event"),

    # --- Camera / Trail (4) ---
    0x00410730: ("GameSet__UpdateCameraAnimation", "GameSet: update camera animation"),
    0x004201f0: ("TrailTracker__RecordPositionSample", "TrailTracker: record position sample"),
    0x00420640: ("TrailTracker__InterpolateRotation", "TrailTracker: interpolate rotation"),
    0x004204a0: ("TrailTracker__InterpolatePosition", "TrailTracker: interpolate position"),

    # --- Camera Mode (2) ---
    0x00423820: ("CameraMode__ComputeSweepPosition", "CameraMode: compute sweep position"),
    0x004272d0: ("CameraMode__ComputeTorpedoCameraPosition", "CameraMode: compute torpedo follow camera position"),

    # --- Interface Module (1) ---
    0x004624f0: ("InterfaceModule__InitializeFromRenderer", "InterfaceModule: initialize from renderer"),

    # --- AI: Sensor (2) ---
    0x0047fa40: ("SensorAI__RecordContactTimestamp", "SensorAI: record contact timestamp"),
    0x0047fb00: ("SensorAI__BuildVisibleObjectList", "SensorAI: build visible object list"),

    # --- AI: Attack (4) ---
    0x00481cc0: ("AttackAI__ctor", "AttackAI: constructor"),
    0x00480250: ("AttackAI__ComputeBestEvasionDirection", "AttackAI: compute best evasion direction"),
    0x0047f5f0: ("AttackAI__EvaluateThreatsAndEvade", "AttackAI: evaluate threats and compute evasion"),
    0x00484a90: ("AttackAI__PredictTargetPosition", "AttackAI: predict target position with lead"),

    # --- NiTimeController / NiPathController (3) ---
    0x004ca220: ("NiTimeController__StartAnimation", "NiTimeController: start animation"),
    0x00451ac0: ("NiPathController__BuildPathAnimation", "NiPathController: build path animation"),
    0x007dc690: ("NiPathController__ComputeControlPoints", "NiPathController: compute control points"),

    # --- Warp Effect (1) ---
    0x004d4950: ("WarpEffect__StartWarpFlash", "WarpEffect: start warp flash"),

    # --- NiApplication (1) ---
    0x007ba5a0: ("NiApplication__ProcessAllMessages", "NiApplication: process all messages"),

    # --- Input Manager (3) ---
    0x006e6290: ("TGInputManager__GetMouseTimestampAsInt", "TGInputManager: get mouse timestamp as int"),
    0x006e62d0: ("TGInputManager__GetKeyTimestampAsInt", "TGInputManager: get key timestamp as int"),
    0x005599d0: ("TGKeyBindingTable__ProcessInput", "TGKeyBindingTable: process input"),

    # --- Target Reticle / Tactical Overlay (3) ---
    0x005140e0: ("TargetReticleDisplay__Initialize", "TargetReticleDisplay: initialize"),
    0x00512310: ("TargetReticleDisplay__UpdateLayout", "TargetReticleDisplay: update layout"),
    0x00543310: ("TacticalOverlay__UpdateTargetArrow", "TacticalOverlay: update target direction arrow"),

    # --- Tactical Overlay Radar (1) ---
    0x00544200: ("TacticalOverlay__UpdateRadarDots", "TacticalOverlay: update radar dot positions"),

    # --- Damage Display (2) ---
    0x00540aa0: ("DamageDisplay__UpdateSubsystemIndicator", "DamageDisplay: update subsystem indicator"),
    0x00540800: ("DamageDisplay__HandleSetPlayerEvent", "DamageDisplay: handle set player event"),

    # --- Engineering Power Control (1) ---
    0x0054cfe0: ("EngPowerCtrl__ctor", "EngPowerCtrl: constructor"),

    # --- Renderer (1) ---
    0x00554750: ("NiDX7Renderer__GetCurrentFrameFormat", "NiDX7Renderer: get current frame format"),

    # --- Streamed Objects (1) ---
    0x006fea70: ("TGStreamedObject__ReadFromStream_Base", "TGStreamedObject: read from stream base"),

    # --- Small Block Allocator (1) ---
    0x006fba70: ("TGSmallBlockAllocator__AllocBlock", "TGSmallBlockAllocator: allocate block"),

    # --- NIF Loading (1) ---
    0x0045f990: ("NiMorphData__ReadFromStream", "NiMorphData: read from stream"),

    # --- TGL System (3) ---
    0x006d0470: ("TGLManager__AddResource", "TGLManager: add resource"),
    0x006d18b0: ("TGLFile__ReadHeader", "TGLFile: read header"),
    0x006d1980: ("TGLFile__ReadEntries", "TGLFile: read entries"),

    # --- Paragraph / Status Bar (2) ---
    0x00733bf0: ("TGParagraph__ReadFromStream", "TGParagraph: read from stream"),
    0x007be320: ("NiStatusBar__Destroy", "NiStatusBar: destroy"),

    # --- Paragraph Text (1) ---
    0x00738f60: ("TGParagraph__AddAnnotatedText", "TGParagraph: add annotated text"),

    # --- Menu (2) ---
    0x00516b80: ("SortedRegionMenu__ctor_FromWString", "SortedRegionMenu: ctor from WString"),
    0x00516fd0: ("SortedRegionMenu__ctor", "SortedRegionMenu: ctor"),

    # --- Display Name (2) ---
    0x0040e3b0: ("TGDisplayName__SetDatabaseName", "TGDisplayName: set database name"),
    0x0040e530: ("TGDisplayName__FlushPendingObjects", "TGDisplayName: flush pending objects"),

    # --- WString (1) ---
    0x00416870: ("TGWString__AllocBuffer", "TGWString: allocate buffer"),

    # --- Sensor / Subsystem (2) ---
    0x00568ad0: ("SensorSubsystem__SchedulePeriodicScan", "SensorSubsystem: schedule periodic scan"),
    0x0056c130: ("Subsystem__GetLocalizedName", "Subsystem: get localized name from TGL"),

    # --- Timer System (2) ---
    0x007023e0: ("TGTimerCallback__RescheduleTimer", "TGTimerCallback: reschedule timer"),
    0x007008e0: ("TGTimerManager__ProcessTimerCallbacks", "TGTimerManager: process timer callbacks"),

    # --- Scrollbar (1) ---
    0x00531e60: ("STScrollbar__HandleDragEvent", "STScrollbar: handle drag event"),

    # --- VarManager (3) ---
    0x00448060: ("VarManagerNode__SetName", "VarManagerNode: set name"),
    0x004480d0: ("VarManagerNode__SetVariable", "VarManagerNode: set variable"),
    0x00447510: ("VarManagerEntry__SetKey", "VarManagerEntry: set key"),

    # --- Sound System (5) ---
    0x0070b0c0: ("TGSound__CopyFrom", "TGSound: copy from"),
    0x0070c7a0: ("TGSoundCache__LoadOrGetFile", "TGSoundCache: load or get file"),
    0x0070c6f0: ("TGSoundFileEntry__ctor", "TGSoundFileEntry: ctor"),
    0x0070d580: ("TGLinkedList__AllocNodes", "TGLinkedList: allocate nodes"),
    0x00710910: ("TGSoundManager__RegisterSoundEvent", "TGSoundManager: register sound event"),

    # --- DX7 / Renderer (2) ---
    0x0078df20: ("NiDX7TextureGroup__AddTexture", "NiDX7TextureGroup: add texture"),
    0x0078f550: ("NiDX7SoundObject__OpenStream", "NiDX7SoundObject: open stream"),

    # --- NiString (1) ---
    0x00721200: ("NiString__AllocBuffer", "NiString: allocate buffer"),

    # --- Placement Editor (2) ---
    0x0049d390: ("PlacementEditor__BuildLightEditDialog", "PlacementEditor: build light edit dialog"),
    0x0049da50: ("PlacementEditor__BuildAsteroidFieldDialog", "PlacementEditor: build asteroid field dialog"),

    # --- File List / Main Menu (2) ---
    0x0051fc60: ("STFileListWindow__Create", "STFileListWindow: create"),
    0x00524040: ("MainMenu__BuildLoadDeleteButtons", "MainMenu: build load/delete buttons"),

    # --- STWidget (1) ---
    0x00529f00: ("STWidget__ctor", "STWidget: ctor"),

    # --- Mission Log Pane (1) ---
    0x005286d0: ("MissionLogPane__ctor", "MissionLogPane: ctor (scrollable, config-driven line limit)"),

    # --- Sensor Menu / Target Menu (5) ---
    0x00535800: ("SensorMenu__UpdateUnidentifiedContactLabel", "SensorMenu: update unidentified contact label"),
    0x005367c0: ("SubsystemTargetMenu__PopulateItems", "SubsystemTargetMenu: populate subsystem items"),
    0x00535590: ("SubsystemRepairMenu__PopulateItems", "SubsystemRepairMenu: populate repair items"),
    0x00536160: ("SubsystemTargetMenu__HandleTargetSelected", "SubsystemTargetMenu: handle target selected"),
    0x00538c90: ("SubsystemTargetMenu__RefreshTargetList", "SubsystemTargetMenu: refresh visible target list"),

    # --- STTimerButton (2) ---
    0x0053e600: ("STTimerButton__ctor", "STTimerButton: ctor (ASCII)"),
    0x0053e800: ("STTimerButton__ctorW", "STTimerButton: ctor (wide string)"),

    # --- Helm Display (1) ---
    0x0054c200: ("HelmDisplay__UpdateSpeedReadout", "HelmDisplay: update speed readout"),

    # --- Shields / Ship Display (2) ---
    0x00545d30: ("ShieldsDisplay__HandleSetPlayerEvent", "ShieldsDisplay: handle set player event"),
    0x00546e40: ("ShipDisplay__HandleShipDestroyedEvent", "ShipDisplay: handle ship destroyed event"),

    # --- Character / Animation (3) ---
    0x00667420: ("CharacterClass__dtor", "CharacterClass: destructor (cleanup models, anims, hash tables)"),
    0x0066fb90: ("TGAnimAction__ctor", "TGAnimAction: constructor (extends TGAction)"),
    0x0066fcd0: ("TGAnimAction__dtor", "TGAnimAction: destructor"),

    # --- GameSpy Browser (1) ---
    0x0069c140: ("GameSpyBrowser__dtor", "GameSpyBrowser: destructor (TGL, heartbeat, event cleanup)"),

    # --- Cloaking Subsystem (2) ---
    0x0055f9d0: ("CloakingSubsystem__HandleCloakStartedEvent", "CloakingSubsystem: handle cloak started event"),
    0x0055fa00: ("CloakingSubsystem__HandleCloakStoppedEvent", "CloakingSubsystem: handle cloak stopped event"),

    # --- Physics (3) ---
    0x005a88e0: ("PhysicsObjectClass__CheckCollision", "PhysicsObjectClass: check collision between two objects"),
    0x005a05c0: ("PhysicsObject__IntegrateMotion", "PhysicsObject: integrate motion (velocity + rotation)"),
    0x005a1dc0: ("PhysicsObjectClass__WriteNetworkState", "PhysicsObjectClass: write network state (pos, rot, vel, name) [vtable slot 68]"),

    # --- Torpedo System (2) ---
    0x00591ee0: ("TorpedoSystem__LaunchProjectile", "TorpedoSystem: create torpedo, set velocity, add to scene"),
    0x00576080: ("TorpedoTube__CreateAndLaunchProjectile", "TorpedoTube: create and launch projectile with sound"),

    # --- NiNode / NiAVObject (2) ---
    0x007e4220: ("NiNode__BuildPropertyState", "NiNode: build property state (recursive)"),
    0x007dc7b0: ("NiAVObject__AccumulateProperties", "NiAVObject: accumulate properties into state"),

    # --- Main Window (4) ---
    0x004fecf0: ("MainWindow__UpdateVisibleObjectNames", "MainWindow: update visible object display names"),
    0x00501510: ("MainWindow__HandleObjectClickedForTarget", "MainWindow: handle object clicked for targeting"),
    0x00501610: ("MainWindow__HandleObjectEnteredScene", "MainWindow: handle object entered scene"),
    0x005018f0: ("MainWindow__HandleTargetChangedEvent", "MainWindow: handle target changed event"),


    # =================================================================
    # Pass 8 (2026-02-24): 10 parallel agents across event system,
    # weapons, UI, scene graph, Ship vtable, subsystems, TGObject
    # hierarchy, mission/game, xref mining
    # =================================================================

    # --- BridgeWindow (2) ---
    0x004fb750: ("BridgeWindow__ctor", "BridgeWindow: ctor"),
    0x004fb830: ("BridgeWindow__scalar_deleting_dtor", "BridgeWindow: scalar_deleting_dtor"),

    # --- CinematicWindow (2) ---
    0x005024e0: ("CinematicWindow__scalar_deleting_dtor", "CinematicWindow: scalar_deleting_dtor"),
    0x00502520: ("CinematicWindow__ctor_FromStream", "CinematicWindow: ctor_FromStream"),

    # --- DamageableObject (6) ---
    0x00590980: ("DamageableObject__RegisterEventHandlers", "DamageableObject: RegisterEventHandlers"),
    0x005909b0: ("DamageableObject__UnregisterEventHandlers", "DamageableObject: UnregisterEventHandlers"),
    0x00590ec0: ("DamageableObject__ctor_stream", "DamageableObject: ctor_stream"),
    0x00594310: ("DamageableObject__RayIntersect", "DamageableObject: RayIntersect"),
    0x00594440: ("DamageableObject__CollisionTest_A", "DamageableObject: CollisionTest_A"),
    0x005945b0: ("DamageableObject__CollisionTest_B", "DamageableObject: CollisionTest_B"),

    # --- EnergyWeapon (12) ---

    # --- Episode (3) ---
    0x004047e0: ("Episode__GetNextEventType", "Episode: GetNextEventType"),
    0x00404a60: ("Episode__RemoveGoal", "Episode: RemoveGoal"),
    0x0043d8b0: ("Episode__ctor_stream", "Episode: ctor_stream"),

    # --- FiringChain (3) ---

    # --- ForceVector (1) ---
    0x005965f0: ("ForceVector__Init", "ForceVector: Init"),

    # --- LoadEpisodeAction (1) ---
    0x004027d0: ("LoadEpisodeAction__ctor", "LoadEpisodeAction: ctor"),

    # --- LoadMissionAction (1) ---
    0x00403460: ("LoadMissionAction__ctor", "LoadMissionAction: ctor"),

    # --- MainWindow (6) ---
    0x0050ea00: ("MainWindow__scalar_deleting_dtor", "MainWindow: scalar_deleting_dtor"),
    0x0050ea30: ("MainWindow__ToggleVisibility", "MainWindow: ToggleVisibility"),
    0x0050eab0: ("MainWindow__IsCurrentWindow", "MainWindow: IsCurrentWindow"),
    0x0050eb00: ("MainWindow__SetVisibleWithFocus", "MainWindow: SetVisibleWithFocus"),
    0x0050f480: ("MainWindow__AddToObjectList", "MainWindow: AddToObjectList"),
    0x0050f590: ("MainWindow__RemoveFromObjectList", "MainWindow: RemoveFromObjectList"),

    # --- Mission (2) ---
    0x00409170: ("Mission__PlayerExitedSetHandler", "Mission: PlayerExitedSetHandler"),
    0x00409270: ("Mission__PlayerChangedHandler", "Mission: PlayerChangedHandler"),

    # --- MultiplayerGame (1) ---
    0x00442940: ("MultiplayerGame__scalar_deleting_dtor", "MultiplayerGame: scalar_deleting_dtor"),

    # --- MultiplayerWindow (11) ---
    0x00504360: ("MultiplayerWindow__Cast", "MultiplayerWindow: Cast"),
    0x00504530: ("MultiplayerWindow__scalar_deleting_dtor", "MultiplayerWindow: scalar_deleting_dtor"),
    0x00504560: ("MultiplayerWindow__dtor", "MultiplayerWindow: dtor"),
    0x00505480: ("MultiplayerWindow__HideAllChildren", "MultiplayerWindow: HideAllChildren"),
    0x00505500: ("MultiplayerWindow__WriteToStream", "MultiplayerWindow: WriteToStream"),
    0x00505660: ("MultiplayerWindow__ReadFromStream", "MultiplayerWindow: ReadFromStream"),
    0x00505770: ("MultiplayerWindow__ResolveIDs", "MultiplayerWindow: ResolveIDs"),
    0x00505880: ("MultiplayerWindow__RestoreIDsToPointers", "MultiplayerWindow: RestoreIDsToPointers"),
    0x00505d70: ("MultiplayerWindow__ButtonSelectionHandler", "MultiplayerWindow: ButtonSelectionHandler"),
    0x00506910: ("MultiplayerWindow__InitClientUI", "MultiplayerWindow: InitClientUI"),
    0x00506eb0: ("MultiplayerWindow__SetVisible", "MultiplayerWindow: SetVisible"),

    # --- NamedReticleWindow (2) ---
    0x00510270: ("NamedReticleWindow__scalar_deleting_dtor", "NamedReticleWindow: scalar_deleting_dtor"),
    0x005102a0: ("NamedReticleWindow__dtor", "NamedReticleWindow: dtor"),

    # --- NiAVObject (5) ---
    0x007dc330: ("NiAVObject__SetParent", "NiAVObject: SetParent"),
    0x007dcb80: ("NiAVObject__CullAgainstPlanes", "NiAVObject: CullAgainstPlanes"),
    0x007dcdb0: ("NiAVObject__TestBoundIntersection", "NiAVObject: TestBoundIntersection"),
    0x007dcf00: ("NiAVObject__TestBoundIntersection_Detail", "NiAVObject: TestBoundIntersection_Detail"),
    0x007dd230: ("NiAVObject__GetObjectByName", "NiAVObject: GetObjectByName (vtable slot 22, name compare)"),

    # --- NiAssetLoader (1) ---
    0x00819000: ("NiAssetLoader__LoadFromPath", "NiAssetLoader: LoadFromPath"),

    # --- NiBound (8) ---
    0x007dd170: ("NiBound__IntersectRay", "NiBound: IntersectRay"),
    0x008122c0: ("NiBound__Init", "NiBound: Init"),
    0x00812300: ("NiBound__ComputeFromPoints", "NiBound: ComputeFromPoints"),
    0x008124f0: ("NiBound__TestPlane", "NiBound: TestPlane"),
    0x00812540: ("NiBound__TestSweepIntersection", "NiBound: TestSweepIntersection"),
    0x00812690: ("NiBound__FindSweepIntersection", "NiBound: FindSweepIntersection"),
    0x00812f30: ("NiBound__SetFromCenterRadius", "NiBound: SetFromCenterRadius"),
    0x00813070: ("NiBound__Merge", "NiBound: Merge"),

    # --- NiDynamicEffect (1) ---
    0x007e2330: ("NiDynamicEffect__AttachAffectedNode", "NiDynamicEffect: AttachAffectedNode"),

    # --- NiDynamicEffectState (3) ---
    0x00820f00: ("NiDynamicEffectState__Clone", "NiDynamicEffectState: Clone"),
    0x00821020: ("NiDynamicEffectState__AddEffect", "NiDynamicEffectState: AddEffect"),
    0x00821220: ("NiDynamicEffectState__InsertSorted", "NiDynamicEffectState: InsertSorted"),

    # --- NiFile (3) ---
    0x0086e550: ("NiFile__ctor", "NiFile: ctor"),
    0x0086e620: ("NiFile__dtor", "NiFile: dtor"),
    0x0086ec40: ("NiFile__ReadLine", "NiFile: ReadLine"),

    # --- NiMatrix3 (1) ---
    0x008136c0: ("NiMatrix3__Copy", "NiMatrix3: Copy"),

    # --- NiMemStream (1) ---
    0x0086ed70: ("NiMemStream__ctor", "NiMemStream: ctor"),

    # --- NiNode (3) ---
    0x004321a0: ("NiNode__GetChildAt", "NiNode: GetChildAt"),
    0x007e4400: ("NiNode__PushLocalEffects", "NiNode: PushLocalEffects"),
    0x007e4770: ("NiNode__AttachEffect", "NiNode: AttachEffect"),

    # --- NiObjectNET (2) ---
    0x007db120: ("NiObjectNET__GetName", "NiObjectNET: GetName"),
    0x007db440: ("NiObjectNET__GetExtraData", "NiObjectNET: GetExtraData"),

    # --- NiPoint3 (6) ---
    0x00414560: ("NiPoint3__CopyFromPtr", "NiPoint3: CopyFromPtr"),
    0x004145b0: ("NiPoint3__Length", "NiPoint3: Length"),
    0x004234a0: ("NiPoint3__Scale", "NiPoint3: Scale"),
    0x00423560: ("NiPoint3__Unitize", "NiPoint3: Unitize"),
    0x00426c30: ("NiPoint3__Add", "NiPoint3: Add"),
    0x00580570: ("NiPoint3__Negate", "NiPoint3: Negate"),

    # --- NiPropertyState (2) ---
    0x008204e0: ("NiPropertyState__CopyFrom", "NiPropertyState: CopyFrom"),
    0x00820590: ("NiPropertyState__dtor", "NiPropertyState: dtor"),

    # --- NiSmartPtr (4) ---
    0x0040cfe0: ("NiSmartPtr__DecRefCount", "NiSmartPtr: DecRefCount"),
    0x00416ec0: ("NiSmartPtr__Release", "NiSmartPtr: Release"),
    0x00416fa0: ("NiSmartPtr__SetValue", "NiSmartPtr: SetValue"),
    0x007e6520: ("NiSmartPtr__Assign", "NiSmartPtr: Assign"),

    # --- NiStream (8) ---
    0x00816c60: ("NiStream__ctor", "NiStream: ctor"),
    0x00816da0: ("NiStream__dtor", "NiStream: dtor"),
    0x00817120: ("NiStream__HashIndex", "NiStream: HashIndex"),
    0x008172a0: ("NiStream__CleanupHashTable", "NiStream: CleanupHashTable"),
    0x008173a0: ("NiStream__GetObjectFromLinkID", "NiStream: GetObjectFromLinkID"),
    0x00817420: ("NiStream__ReadHeader", "NiStream: ReadHeader"),
    0x00817b60: ("NiStream__LoadFromBuffer", "NiStream: LoadFromBuffer"),
    0x00818cb0: ("NiStream__PostLinkObjects", "NiStream: PostLinkObjects"),

    # --- NiTArray (2) ---
    0x00818d80: ("NiTArray__RemoveAll", "NiTArray: RemoveAll"),
    0x00818df0: ("NiTArray__SetAtGrow_Raw", "NiTArray: SetAtGrow_Raw"),

    # --- NiTArray_NiAVObjectPtr (5) ---
    0x007e5e20: ("NiTArray_NiAVObjectPtr__SetAt", "NiTArray_NiAVObjectPtr: SetAt"),
    0x007e5f40: ("NiTArray_NiAVObjectPtr__SetAtGrow", "NiTArray_NiAVObjectPtr: SetAtGrow"),
    0x007e60c0: ("NiTArray_NiAVObjectPtr__Add", "NiTArray_NiAVObjectPtr: Add"),
    0x007e6130: ("NiTArray_NiAVObjectPtr__AddFirstEmpty", "NiTArray_NiAVObjectPtr: AddFirstEmpty"),
    0x007e6230: ("NiTArray_NiAVObjectPtr__RemoveAt", "NiTArray_NiAVObjectPtr: RemoveAt"),

    # --- NiTArray_NiSmartPtr (1) ---
    0x00416f50: ("NiTArray_NiSmartPtr__GetAt", "NiTArray_NiSmartPtr: GetAt"),

    # --- NiTArray_Raw (1) ---
    0x007e6560: ("NiTArray_Raw__SetAtGrow", "NiTArray_Raw: SetAtGrow"),

    # --- NiTList (2) ---
    0x007e2840: ("NiTList__Prepend", "NiTList: Prepend"),
    0x007e6360: ("NiTList__CountItems", "NiTList: CountItems"),

    # --- NiTListNode (2) ---
    0x00416ee0: ("NiTListNode__ctor", "NiTListNode: ctor"),
    0x004e11f0: ("NiTListNode__GetValue", "NiTListNode: GetValue"),

    # --- NiTList_Int (1) ---
    0x007e6380: ("NiTList_Int__Prepend", "NiTList_Int: Prepend"),

    # --- ObjectClass (1) ---
    0x004356a0: ("ObjectClass__CreateCollisionProxy", "ObjectClass: CreateCollisionProxy"),

    # --- PhaserBank (14) ---
    0x00572800: ("PhaserBank__InitBeamAndStartFiring", "PhaserBank: InitBeamAndStartFiring"),
    0x00572950: ("PhaserBank__SetBeamEndpoints", "PhaserBank: SetBeamEndpoints"),
    0x00572a50: ("PhaserBank__ComputeDamageForBeam", "PhaserBank: ComputeDamageForBeam"),

    # --- PhaserSystem (1) ---

    # --- PhysicsObjectClass (3) ---
    0x005a15a0: ("PhysicsObjectClass__SetTargetObject", "PhysicsObjectClass: SetTargetObject"),
    0x005a1cf0: ("PhysicsObjectClass__SerializeToBuffer", "PhysicsObjectClass: SerializeToBuffer"),
    0x005a2060: ("PhysicsObjectClass__DeserializeFromNetwork", "PhysicsObjectClass: DeserializeFromNetwork"),

    # --- PlayViewWindow (1) ---
    0x004fc5e0: ("PlayViewWindow__ctor_stream", "PlayViewWindow: ctor_stream"),

    # --- PlayWindow (9) ---
    0x00405a90: ("PlayWindow__InitHandlerTable", "PlayWindow: InitHandlerTable"),
    0x004062b0: ("PlayWindow__TerminateWithEvent", "PlayWindow: TerminateWithEvent"),
    0x004062d0: ("PlayWindow__ReallyTerminate", "PlayWindow: ReallyTerminate"),
    0x00406640: ("PlayWindow__SetLastSavedGame", "PlayWindow: SetLastSavedGame"),
    0x00406770: ("PlayWindow__SetUIShipID", "PlayWindow: SetUIShipID"),
    0x00406d80: ("PlayWindow__WriteToStream", "PlayWindow: WriteToStream"),
    0x00407070: ("PlayWindow__ResolveIDs", "PlayWindow: ResolveIDs"),
    0x004070f0: ("PlayWindow__RestoreIDsToPointers", "PlayWindow: RestoreIDsToPointers"),
    0x00508520: ("PlayWindow__LoadSubtitlePositions", "PlayWindow: LoadSubtitlePositions"),

    # --- PulseWeapon (2) ---

    # --- STButton (1) ---
    0x00518e30: ("STButton__scalar_deleting_dtor", "STButton: scalar_deleting_dtor"),

    # --- STMenu (13) ---
    0x00525720: ("STMenu__scalar_deleting_dtor", "STMenu: scalar_deleting_dtor"),
    0x00525820: ("STMenu__Setup", "STMenu: Setup"),
    0x00525b00: ("STMenu__dtor", "STMenu: dtor"),
    0x00525c30: ("STMenu__GetArrowOffsetX", "STMenu: GetArrowOffsetX"),
    0x00525c90: ("STMenu__Layout", "STMenu: Layout"),
    0x00525d10: ("STMenu__GotFocus", "STMenu: GotFocus"),
    0x00525d70: ("STMenu__AddChild", "STMenu: AddChild"),
    0x00525e00: ("STMenu__GetNestingDepth", "STMenu: GetNestingDepth"),
    0x00526120: ("STMenu__PositionChildren", "STMenu: PositionChildren"),
    0x00526910: ("STMenu__ResizeAndUpdateParentWindows", "STMenu: ResizeAndUpdateParentWindows"),
    0x00526b40: ("STMenu__ReleaseChosenEvent", "STMenu: ReleaseChosenEvent"),
    0x00526c10: ("STMenu__Open", "STMenu: Open"),
    0x00526d50: ("STMenu__Close", "STMenu: Close"),

    # --- STStylizedWindow (4) ---
    0x005310f0: ("STStylizedWindow__scalar_deleting_dtor", "STStylizedWindow: scalar_deleting_dtor"),
    0x00531120: ("STStylizedWindow__dtor", "STStylizedWindow: dtor"),
    0x005314f0: ("STStylizedWindow__ClearFixedSize", "STStylizedWindow: ClearFixedSize"),
    0x00531730: ("STStylizedWindow__EnsureChildVisible", "STStylizedWindow: EnsureChildVisible"),

    # --- STWidget (8) ---
    0x0073f770: ("STWidget__dtor", "STWidget: dtor"),
    0x0073fa40: ("STWidget__ReleaseCompletionEvent", "STWidget: ReleaseCompletionEvent"),
    0x0073fa80: ("STWidget__SetHighlightedEvent", "STWidget: SetHighlightedEvent"),
    0x0073fad0: ("STWidget__SetUnhighlightedEvent", "STWidget: SetUnhighlightedEvent"),
    0x0073fb20: ("STWidget__HandleClick", "STWidget: HandleClick"),
    0x0073fb90: ("STWidget__WriteToStream", "STWidget: WriteToStream"),
    0x0073fc10: ("STWidget__ReadFromStream", "STWidget: ReadFromStream"),
    0x0073fc60: ("STWidget__ResolveIDs", "STWidget: ResolveIDs"),

    # --- ShieldSubsystem (1) ---
    0x0056a160: ("ShieldSubsystem__ScalarDeletingDtor", "ShieldSubsystem: ScalarDeletingDtor"),

    # --- SortedRegionMenuWindow (1) ---
    0x004fd6f0: ("SortedRegionMenuWindow__ctor", "SortedRegionMenuWindow: ctor"),

    # --- Standalone (4) ---
    0x004068c0: ("GetDifficultyDamageScale", "GetDifficultyDamageScale"),
    0x0086e3f0: ("NiOutputDebugString", "NiOutputDebugString"),
    0x0086e400: ("NiStricmp", "NiStricmp"),
    0x0086e420: ("NiStrncmp", "NiStrncmp"),

    # --- TGDialogWindow (4) ---
    0x00738a90: ("TGDialogWindow__ctor", "TGDialogWindow: ctor"),
    0x00738c10: ("TGDialogWindow__Create", "TGDialogWindow: Create"),
    0x00738e40: ("TGDialogWindow__AddButtons", "TGDialogWindow: AddButtons"),
    0x00739060: ("TGDialogWindow__LayoutContent", "TGDialogWindow: LayoutContent"),

    # --- TGEventHandlerObject (2) ---
    0x006d9240: ("TGEventHandlerObject__HandleEvent", "TGEventHandlerObject: HandleEvent"),
    0x006da4e0: ("TGEventHandlerObject__RegisterConditionHandler", "TGEventHandlerObject: RegisterConditionHandler"),

    # --- TGPane (22) ---
    0x0072e000: ("TGPane__KillChildren", "TGPane: KillChildren"),
    0x0072e060: ("TGPane__Render", "TGPane: Render"),
    0x0072e0a0: ("TGPane__Update", "TGPane: Update"),
    0x0072e3a0: ("TGPane__GamepadHandler", "TGPane: GamepadHandler"),
    0x0072e3d0: ("TGPane__ControlHandler", "TGPane: ControlHandler"),
    0x0072e5b0: ("TGPane__RemoveChild", "TGPane: RemoveChild"),
    0x0072e6c0: ("TGPane__DeleteChild", "TGPane: DeleteChild"),
    0x0072e7e0: ("TGPane__SetFocus", "TGPane: SetFocus"),
    0x0072e920: ("TGPane__MoveToFront", "TGPane: MoveToFront"),
    0x0072e970: ("TGPane__MoveToBack", "TGPane: MoveToBack"),
    0x0072eac0: ("TGPane__MoveTowardsBack", "TGPane: MoveTowardsBack"),
    0x0072ec60: ("TGPane__GetFocusLeaf", "TGPane: GetFocusLeaf"),
    0x0072ec80: ("TGPane__InvalidateAllChildPolys", "TGPane: InvalidateAllChildPolys"),
    0x0072ecb0: ("TGPane__SetClipRectOnChildren", "TGPane: SetClipRectOnChildren"),
    0x0072ece0: ("TGPane__BuildPolyList", "TGPane: BuildPolyList"),
    0x0072ed80: ("TGPane__GetNthChild", "TGPane: GetNthChild"),
    0x0072edd0: ("TGPane__GetFirstVisibleChild", "TGPane: GetFirstVisibleChild"),
    0x0072eeb0: ("TGPane__SetNotVisibleRecursive", "TGPane: SetNotVisibleRecursive"),
    0x0072ef50: ("TGPane__SetEnabledRecursive", "TGPane: SetEnabledRecursive"),
    0x0072efa0: ("TGPane__ClearDirtyAndLayoutChildren", "TGPane: ClearDirtyAndLayoutChildren"),
    0x0072f060: ("TGPane__WriteToStream", "TGPane: WriteToStream"),
    0x0072f0e0: ("TGPane__ReadFromStream", "TGPane: ReadFromStream"),

    # --- TGPoolAllocator (1) ---
    0x00586c50: ("TGPoolAllocator__Init", "TGPoolAllocator: Init"),

    # --- TGRootPane (11) ---
    0x00727620: ("TGRootPane__ctor", "TGRootPane: ctor"),
    0x00727760: ("TGRootPane__scalar_deleting_dtor", "TGRootPane: scalar_deleting_dtor"),
    0x00727840: ("TGRootPane__dtor", "TGRootPane: dtor"),
    0x007278a0: ("TGRootPane__DestroyAll", "TGRootPane: DestroyAll"),
    0x00727920: ("TGRootPane__DestroyCursor", "TGRootPane: DestroyCursor"),
    0x00727940: ("TGRootPane__CreateTooltip", "TGRootPane: CreateTooltip"),
    0x00727a10: ("TGRootPane__ReleaseCursor", "TGRootPane: ReleaseCursor"),
    0x00727b30: ("TGRootPane__SetMouseCursor", "TGRootPane: SetMouseCursor"),
    0x00727e30: ("TGRootPane__RestorePreviousCursor", "TGRootPane: RestorePreviousCursor"),
    0x00727ee0: ("TGRootPane__PushCursor", "TGRootPane: PushCursor"),
    0x00727fa0: ("TGRootPane__PopCursor", "TGRootPane: PopCursor"),

    # --- TGSceneObject (3) ---
    0x00430cf0: ("TGSceneObject__Update", "TGSceneObject: Update"),
    0x00430e20: ("TGSceneObject__SetScene", "TGSceneObject: SetScene"),
    0x00431e20: ("TGSceneObject__ResolveObjectRefs", "TGSceneObject: ResolveObjectRefs"),

    # --- TGStreamedObject (2) ---
    0x006f2750: ("TGStreamedObject__WriteToStreamChain", "TGStreamedObject: WriteToStreamChain"),
    0x006f3400: ("TGStreamedObject__AddEventHandler", "TGStreamedObject: AddEventHandler"),

    # --- TGStreamedObjectEx (1) ---
    0x006f2810: ("TGStreamedObjectEx__PostDeserialize", "TGStreamedObjectEx: PostDeserialize"),

    # --- TGTextBlock (4) ---
    0x007367a0: ("TGTextBlock__AddParagraph", "TGTextBlock: AddParagraph"),
    0x00736ac0: ("TGTextBlock__ProcessAndAddPrompt", "TGTextBlock: ProcessAndAddPrompt"),
    0x00736ba0: ("TGTextBlock__ScrollToBottom", "TGTextBlock: ScrollToBottom"),
    0x00736f30: ("TGTextBlock__EvalString", "TGTextBlock: EvalString"),

    # --- TGUIObject (9) ---
    0x0072fe40: ("TGUIObject__GetConceptualParent", "TGUIObject: GetConceptualParent"),
    0x0072fed0: ("TGUIObject__SetEnabled", "TGUIObject: SetEnabled"),
    0x0072ff10: ("TGUIObject__SetDisabled", "TGUIObject: SetDisabled"),
    0x0072ff30: ("TGUIObject__SetBounds", "TGUIObject: SetBounds"),
    0x0072ff80: ("TGUIObject__GetScreenOffset", "TGUIObject: GetScreenOffset"),
    0x0072ffc0: ("TGUIObject__GetClipRect", "TGUIObject: GetClipRect"),
    0x007300e0: ("TGUIObject__Move", "TGUIObject: Move"),
    0x007302f0: ("TGUIObject__SetPosition", "TGUIObject: SetPosition"),
    0x007305d0: ("TGUIObject__AlignTo", "TGUIObject: AlignTo"),

    # --- TGWindow (5) ---
    0x0073e7d0: ("TGWindow__dtor", "TGWindow: dtor"),
    0x0073e8c0: ("TGWindow__SetDefaultChild", "TGWindow: SetDefaultChild"),
    0x0073e940: ("TGWindow__AddChild", "TGWindow: AddChild"),
    0x0073e980: ("TGWindow__RemoveChild", "TGWindow: RemoveChild"),
    0x0073e9b0: ("TGWindow__InsertChild", "TGWindow: InsertChild"),

    # --- TacticalWindow (1) ---
    0x0050b290: ("TacticalWindow__ctor", "TacticalWindow: ctor"),

    # --- TopWindow (7) ---
    0x0050e110: ("TopWindow__IsBridgeVisible", "TopWindow: IsBridgeVisible"),
    0x0050e130: ("TopWindow__IsTacticalVisible", "TopWindow: IsTacticalVisible"),
    0x0050e170: ("TopWindow__SetLastRenderedSet", "TopWindow: SetLastRenderedSet"),
    0x0050e190: ("TopWindow__GetLastRenderedSet", "TopWindow: GetLastRenderedSet"),
    0x0050e630: ("TopWindow__WriteToStream", "TopWindow: WriteToStream"),
    0x0050e7c0: ("TopWindow__ReadFromStream", "TopWindow: ReadFromStream"),
    0x0050e910: ("TopWindow__ClearGlobal", "TopWindow: ClearGlobal"),

    # --- Torpedo (7) ---

    # --- TorpedoSystem (5) ---
    0x0057b560: ("TorpedoSystem__IncrementLoadedTorps", "TorpedoSystem: IncrementLoadedTorps"),
    0x0057b570: ("TorpedoSystem__DecrementLoadedTorps", "TorpedoSystem: DecrementLoadedTorps"),

    # --- TorpedoTube (17) ---
    0x00574f30: ("TorpedoTube__GetTorpedoSystemProperty", "TorpedoTube: GetTorpedoSystemProperty"),
    0x00575270: ("TorpedoTube__GetSkewFireDamageScale", "TorpedoTube: GetSkewFireDamageScale"),
    0x0057cd90: ("TorpedoTube__LaunchLocal_ClientPath", "TorpedoTube: LaunchLocal_ClientPath"),

    # --- TractorBeam (10) ---

    # --- WeaponSubsystem (3) ---
    0x00584f70: ("WeaponSubsystem__SetTargetIDAndOffset", "WeaponSubsystem: SetTargetIDAndOffset"),

    # --- WeaponSystem (17) ---
    0x00584050: ("WeaponSystem__GetProperty", "WeaponSystem: GetProperty"),
    0x00584060: ("WeaponSystem__IsSingleFire", "WeaponSystem: IsSingleFire"),

    # --- WeaponTargetEntry (2) ---

    # =================================================================
    # Pass 8 consolidated (2026-02-24): Phases 8B-8J across 8 agents
    # Ship vtable, UI, Subsystems, SceneGraph, TGObject, Xref, Weapons, Mission
    # =================================================================
    # --- BridgeObjectClass (2) ---
    0x006617e0: ("BridgeObjectClass__ctor_Impl", "BridgeObjectClass: ctor_Impl"),
    0x00664660: ("BridgeObjectClass__PlayDamageReaction", "BridgeObjectClass: PlayDamageReaction"),
    # --- CharacterClass (1) ---
    0x00668250: ("CharacterClass__LoadCharacterModel", "CharacterClass: LoadCharacterModel"),
    # --- CloakingSubsystem (7) ---
    0x0055e400: ("CloakingSubsystem__ScalarDeletingDtor", "CloakingSubsystem: ScalarDeletingDtor"),
    0x0055e500: ("CloakingSubsystem__Update", "CloakingSubsystem: Update"),
    0x0055f930: ("CloakingSubsystem__TurnOff", "CloakingSubsystem: TurnOff"),
    0x0055f970: ("CloakingSubsystem__WriteState_A", "CloakingSubsystem: WriteState_A"),
    0x0055f9a0: ("CloakingSubsystem__ReadState_A", "CloakingSubsystem: ReadState_A"),
    0x0055fa30: ("CloakingSubsystem__WriteToStream", "CloakingSubsystem: WriteToStream"),
    0x0055faa0: ("CloakingSubsystem__ReadFromStream", "CloakingSubsystem: ReadFromStream"),
    # --- CollisionEvent (8) ---
    0x005b7cf0: ("CollisionEvent__SetPositionFromObject", "CollisionEvent: SetPositionFromObject"),
    0x005b8840: ("CollisionEvent__scalar_deleting_dtor", "CollisionEvent: scalar_deleting_dtor"),
    0x005b8880: ("CollisionEvent__FixupObjectRef", "CollisionEvent: FixupObjectRef"),
    0x005b88b0: ("CollisionEvent__GetSourceAsGameObject", "CollisionEvent: GetSourceAsGameObject"),
    0x005b8980: ("CollisionEvent__GetWorldPosition", "CollisionEvent: GetWorldPosition"),
    0x005b89d0: ("CollisionEvent__CopyFrom", "CollisionEvent: CopyFrom"),
    0x005b8a50: ("CollisionEvent__WriteToStream", "CollisionEvent: WriteToStream"),
    0x005b8b10: ("CollisionEvent__ReadFromStream", "CollisionEvent: ReadFromStream"),
    # --- DamageableObject (1) ---
    0x00593270: ("DamageableObject__SpawnDeathAnimation", "DamageableObject: SpawnDeathAnimation"),
    # --- FleetAI (1) ---
    0x00484f10: ("FleetAI__CheckTargetInRange", "FleetAI: CheckTargetInRange"),
    # --- FrameBudgetTask (1) ---
    0x0046f740: ("FrameBudgetTask__IsReady", "FrameBudgetTask: IsReady"),
    # --- Game (1) ---
    0x004434d0: ("Game__LoadMissionWithUI", "Game: LoadMissionWithUI"),
    # --- ImpulseEngineSubsystem (3) ---
    0x00561140: ("ImpulseEngineSubsystem__ScalarDeletingDtor", "ImpulseEngineSubsystem: ScalarDeletingDtor"),
    0x005616a0: ("ImpulseEngineSubsystem__WriteToStream", "ImpulseEngineSubsystem: WriteToStream"),
    0x00561710: ("ImpulseEngineSubsystem__ReadFromStream", "ImpulseEngineSubsystem: ReadFromStream"),
    # --- IntegrityHash (1) ---
    0x005b6c10: ("IntegrityHash__AccumulateFloat", "IntegrityHash: AccumulateFloat"),
    # --- MissionBase (2) ---
    0x0040a250: ("MissionBase__LoadTGLFile", "MissionBase: LoadTGLFile"),
    0x0040a400: ("MissionBase__ReadFromStream", "MissionBase: ReadFromStream"),
    # --- ModalDialogWindow (2) ---
    0x00502550: ("ModalDialogWindow__BuildDialog", "ModalDialogWindow: BuildDialog"),
    0x00502990: ("ModalDialogWindow__BuildQuitDialog", "ModalDialogWindow: BuildQuitDialog"),
    # --- NetworkAI (1) ---
    0x0047de70: ("NetworkAI__Update", "NetworkAI: Update"),
    # --- NiAVObject (4) ---
    0x007dc390: ("NiAVObject__GetProperty", "NiAVObject: GetProperty"),
    0x007dc490: ("NiAVObject__RemoveProperty", "NiAVObject: RemoveProperty"),
    0x007dc5c0: ("NiAVObject__AttachProperty", "NiAVObject: AttachProperty"),
    0x007dc950: ("NiAVObject__UpdateEffects", "NiAVObject: UpdateEffects"),
    # --- NiApplication (1) ---
    0x007b7540: ("NiApplication__ParseRendererArgs", "NiApplication: ParseRendererArgs"),
    # --- NiClock (2) ---
    0x00407c50: ("NiClock__GetActiveCameraSmartPtr", "NiClock: GetActiveCameraSmartPtr"),
    0x004460f0: ("NiClock__SetActiveCamera", "NiClock: SetActiveCamera"),
    # --- NiDX7Renderer (1) ---
    0x00555b90: ("NiDX7Renderer__HandleFocusChange", "NiDX7Renderer: HandleFocusChange"),
    # --- NiDX7RendererManager (3) ---
    0x006af650: ("NiDX7RendererManager__InitializeRenderer", "NiDX7RendererManager: InitializeRenderer"),
    0x006afa40: ("NiDX7RendererManager__RecreateRenderer", "NiDX7RendererManager: RecreateRenderer"),
    0x006afd10: ("NiDX7RendererManager__GetRenderWindow", "NiDX7RendererManager: GetRenderWindow"),
    # --- NiDynamicEffect (1) ---
    0x007e2380: ("NiDynamicEffect__DetachAffectedNode", "NiDynamicEffect: DetachAffectedNode"),
    # --- NiNode (24) ---
    0x007e37c0: ("NiNode__ctor", "NiNode: ctor"),
    0x007e3880: ("NiNode__dtor", "NiNode: dtor"),
    0x007e39b0: ("NiNode__AttachChild", "NiNode: AttachChild (vtable slot 39)"),
    0x007e3a30: ("NiNode__DetachChildAt", "NiNode: DetachChildAt (vtable slot 41)"),
    0x007e3b30: ("NiNode__DetachChild", "NiNode: DetachChild (vtable slot 40)"),
    0x007e3c50: ("NiNode__SetAt", "NiNode: SetAt (vtable slot 42)"),
    0x007e4330: ("NiNode__UpdateEffectsUpward", "NiNode: UpdateEffectsUpward"),
    0x007e47c0: ("NiNode__DetachEffect", "NiNode: DetachEffect"),
    0x007e4900: ("NiNode__ApplyTransform", "NiNode: ApplyTransform (vtable slot 14)"),
    0x007e4940: ("NiNode__vfn15_IterateChildren", "NiNode: vfn15 IterateChildren (+0x3C)"),
    0x007e4980: ("NiNode__SetSelectiveUpdateFlags", "NiNode: SetSelectiveUpdateFlags"),
    0x007e49c0: ("NiNode__UpdateDownwardPass", "NiNode: UpdateDownwardPass"),
    0x007e4a00: ("NiNode__UpdateSelectedDownwardPass", "NiNode: UpdateSelectedDownwardPass"),
    0x007e4a40: ("NiNode__UpdateRigidDownwardPass", "NiNode: UpdateRigidDownwardPass"),
    0x007e4a80: ("NiNode__UpdateWorldBound", "NiNode: UpdateWorldBound"),
    0x007e4ac0: ("NiNode__Display", "NiNode: Display"),
    0x007e4ee0: ("NiNode__GetObjectByName", "NiNode: GetObjectByName (vtable slot 22, +0x58)"),
    0x007e4f30: ("NiNode__CreateClone", "NiNode: CreateClone"),
    0x007e50c0: ("NiNode__ProcessClone", "NiNode: ProcessClone"),
    0x007e5300: ("NiNode__CopyEffectListClones", "NiNode: CopyEffectListClones"),
    0x007e4530: ("NiNode__UpdatePropertiesDownward", "NiNode: UpdatePropertiesDownward"),
    0x007e4610: ("NiNode__UpdateEffectsDownward", "NiNode: UpdateEffectsDownward"),
    0x007e53e0: ("NiNode__PostLinkObject", "NiNode: PostLinkObject"),
    0x007e5630: ("NiNode__RegisterStreamables", "NiNode: RegisterStreamables"),
    0x007e57d0: ("NiNode__LoadBinary", "NiNode: LoadBinary"),
    0x007e58d0: ("NiNode__LinkObject", "NiNode: LinkObject"),
    0x007e5940: ("NiNode__SaveBinary", "NiNode: SaveBinary"),
    0x007e5a00: ("NiNode__IsEqual", "NiNode: IsEqual"),
    0x007e5b30: ("NiNode__AddViewerStrings", "NiNode: AddViewerStrings"),
    0x007e67d0: ("NiNode__scalar_deleting_dtor", "NiNode: scalar_deleting_dtor"),
    # --- NiObject (2) ---
    0x007d87a0: ("NiObject__ctor", "NiObject: ctor (vtable + refcount=0 + instanceCount++)"),
    0x007d87f0: ("NiObject__dtor", "NiObject: dtor"),
    # --- NiObjectNET (4) ---
    0x007dad10: ("NiObjectNET__dtor", "NiObjectNET: dtor"),
    0x007dae10: ("NiObjectNET__ProcessClone", "NiObjectNET: ProcessClone"),
    0x007db390: ("NiObjectNET__PrependController", "NiObjectNET: PrependController"),
    0x007db450: ("NiObjectNET__RemoveController", "NiObjectNET: RemoveController"),
    # --- NiTArray (2) ---
    0x007e5d10: ("NiTArray__ctor", "NiTArray: ctor"),
    0x007e5d80: ("NiTArray__dtor_Simple", "NiTArray: dtor_Simple"),
    # --- NiTObjectArray (1) ---
    0x007e5df0: ("NiTObjectArray__dtor", "NiTObjectArray: dtor"),
    # --- NiTimeController (8) ---
    0x007d9c10: ("NiTimeController__dtor", "NiTimeController: dtor"),
    0x007d9cb0: ("NiTimeController__ItemsInList", "NiTimeController: ItemsInList"),
    0x007d9cc0: ("NiTimeController__Start", "NiTimeController: Start"),
    0x007d9cf0: ("NiTimeController__Stop", "NiTimeController: Stop"),
    0x007d9fc0: ("NiTimeController__StartAnimations", "NiTimeController: StartAnimations"),
    0x007da140: ("NiTimeController__StopAnimations", "NiTimeController: StopAnimations"),
    0x007da2c0: ("NiTimeController__SetTarget", "NiTimeController: SetTarget"),
    0x007da340: ("NiTimeController__ProcessClone", "NiTimeController: ProcessClone"),
    # --- PhaserSubsystem (1) ---
    0x0056fb30: ("PhaserSubsystem__ScalarDeletingDtor", "PhaserSubsystem: ScalarDeletingDtor"),
    # --- PhaserSystem (1) ---
    0x00573ea0: ("PhaserSystem__StartFiringAtTarget", "PhaserSystem: StartFiringAtTarget"),
    # --- PhysicsObject (3) ---
    0x005a09d0: ("PhysicsObject__AdvanceSimulation", "PhysicsObject: AdvanceSimulation"),
    0x005a0c20: ("PhysicsObject__PredictOrientation", "PhysicsObject: PredictOrientation"),
    0x005a0d80: ("PhysicsObject__IntegrateRotation", "PhysicsObject: IntegrateRotation"),
    # --- PlayWindow (2) ---
    0x004fc8b0: ("PlayWindow__ShowOptionsMenu", "PlayWindow: ShowOptionsMenu"),
    0x00501590: ("PlayWindow__HandleSetAdded", "PlayWindow: HandleSetAdded"),
    # --- PowerSubsystem (1) ---
    0x00560530: ("PowerSubsystem__ScalarDeletingDtor", "PowerSubsystem: ScalarDeletingDtor"),
    # --- PoweredMaster (2) ---
    0x004401d0: ("PoweredMaster__ScalarDeletingDtor", "PoweredMaster: ScalarDeletingDtor"),
    0x00563f00: ("PoweredMaster__WriteToStream", "PoweredMaster: WriteToStream"),
    # --- PoweredSubsystem (1) ---
    0x00562330: ("PoweredSubsystem__ScalarDeletingDtor", "PoweredSubsystem: ScalarDeletingDtor"),
    # --- PulseWeapon (1) ---
    0x005750e0: ("PulseWeapon__ScalarDeletingDtor", "PulseWeapon: ScalarDeletingDtor"),
    # --- PulseWeaponSystem (1) ---
    0x00577480: ("PulseWeaponSystem__ScalarDeletingDtor", "PulseWeaponSystem: ScalarDeletingDtor"),
    # --- RepairSubsystem (2) ---
    0x00565190: ("RepairSubsystem__ScalarDeletingDtor", "RepairSubsystem: ScalarDeletingDtor"),
    0x00565e80: ("RepairSubsystem__ReadFromStream", "RepairSubsystem: ReadFromStream"),
    # --- STMissionLog (4) ---
    0x00528b70: ("STMissionLog__SetNumStoredLines", "STMissionLog: SetNumStoredLines"),
    0x00528c20: ("STMissionLog__AddLine", "STMissionLog: AddLine"),
    0x00528d70: ("STMissionLog__ClearLines", "STMissionLog: ClearLines"),
    0x00529170: ("STMissionLog__Close", "STMissionLog: Close"),
    # --- STToggle (1) ---
    0x0053bd60: ("STToggle__SetStateValueAndEvent", "STToggle: SetStateValueAndEvent"),
    # --- SensorSubsystem (1) ---
    0x00566e20: ("SensorSubsystem__ScalarDeletingDtor", "SensorSubsystem: ScalarDeletingDtor"),
    # --- SetManager (1) ---
    0x0042c210: ("SetManager__SetActiveCamera", "SetManager: SetActiveCamera"),
    # --- ShieldSubsystem (2) ---
    0x0056acc0: ("ShieldSubsystem__ResolveObjectRefs", "ShieldSubsystem: ResolveObjectRefs"),
    0x0056ad00: ("ShieldSubsystem__FixupObjectRefs", "ShieldSubsystem: FixupObjectRefs"),
    # --- Ship (1) ---
    0x005a22a0: ("Ship__CheckCollisionRateLimit", "Ship: CheckCollisionRateLimit"),
    # --- ShipSubsystem (4) ---
    0x0056b920: ("ShipSubsystem__GetPosition", "ShipSubsystem: GetPosition"),
    0x0056bb60: ("ShipSubsystem__ScalarDeletingDtor", "ShipSubsystem: ScalarDeletingDtor"),
    0x0056d170: ("ShipSubsystem__ResolveObjectRefs", "ShipSubsystem: ResolveObjectRefs"),
    0x0056d1f0: ("ShipSubsystem__FixupObjectRefs", "ShipSubsystem: FixupObjectRefs"),
    # --- ShipSubsystemList (3) ---
    0x005b6ca0: ("ShipSubsystemList__WriteToStream", "ShipSubsystemList: WriteToStream"),
    0x005b6e40: ("ShipSubsystemList__ReadFromStream", "ShipSubsystemList: ReadFromStream"),
    0x005b6fe0: ("ShipSubsystemList__VerifyReferences", "ShipSubsystemList: VerifyReferences"),
    # --- Subsystem (1) ---
    0x005b6170: ("Subsystem__ComputeIntegrityHash", "Subsystem: ComputeIntegrityHash"),
    # --- SubtitleAction (4) ---
    0x006b1ba0: ("SubtitleAction__ctor", "SubtitleAction: ctor"),
    0x006b1dd0: ("SubtitleAction__scalar_deleting_dtor", "SubtitleAction: scalar_deleting_dtor"),
    0x006b1e00: ("SubtitleAction__ctor_stream", "SubtitleAction: ctor_stream"),
    0x006b1f30: ("SubtitleAction__dtor", "SubtitleAction: dtor"),
    # --- TGEvent (8) ---
    0x006d5d40: ("TGEvent__scalar_deleting_dtor", "TGEvent: scalar_deleting_dtor"),
    0x006d5ec0: ("TGEvent__WriteToStream", "TGEvent: WriteToStream"),
    0x006d5ff0: ("TGEvent__ReadFromStream", "TGEvent: ReadFromStream"),
    0x006d6050: ("TGEvent__ResolveObjectRefs", "TGEvent: ResolveObjectRefs"),
    0x006d60b0: ("TGEvent__FixupReferences", "TGEvent: FixupReferences"),
    0x006d6130: ("TGEvent__WriteNetworkStream", "TGEvent: WriteNetworkStream"),
    0x006d61c0: ("TGEvent__ReadNetworkStream", "TGEvent: ReadNetworkStream"),
    0x006d6230: ("TGEvent__CopyFrom", "TGEvent: CopyFrom"),
    # --- TGEventHandlerObject (2) ---
    0x006d9030: ("TGEventHandlerObject__scalar_deleting_dtor", "TGEventHandlerObject: scalar_deleting_dtor"),
    0x006d95d0: ("TGEventHandlerObject__FindHandler", "TGEventHandlerObject: FindHandler"),
    # --- TGHashTable (5) ---
    0x006f65c0: ("TGHashTable__ctor", "TGHashTable: ctor"),
    0x006f6610: ("TGHashTable__scalar_deleting_dtor", "TGHashTable: scalar_deleting_dtor"),
    0x006f6630: ("TGHashTable__dtor", "TGHashTable: dtor"),
    0x006f67e0: ("TGHashTable__FindByKey", "TGHashTable: FindByKey"),
    0x006f6830: ("TGHashTable__Insert", "TGHashTable: Insert"),
    # --- TGIcon (7) ---
    0x0073d540: ("TGIcon__SetColor", "TGIcon: SetColor"),
    0x0073d590: ("TGIcon__SetIconGroupName", "TGIcon: SetIconGroupName"),
    0x0073d610: ("TGIcon__BuildPolyList", "TGIcon: BuildPolyList"),
    0x0073d750: ("TGIcon__Move", "TGIcon: Move"),
    0x0073d9a0: ("TGIcon__SetPosition", "TGIcon: SetPosition"),
    0x0073dbd0: ("TGIcon__WriteToStream", "TGIcon: WriteToStream"),
    0x0073dc40: ("TGIcon__ReadFromStream", "TGIcon: ReadFromStream"),
    # --- TGMessage (1) ---
    0x006b8720: ("TGMessage__FragmentForSend", "TGMessage: FragmentForSend"),
    # --- TGModelContainer (1) ---
    0x006ca9b0: ("TGModelContainer__LoadNIFFile", "TGModelContainer: LoadNIFFile"),
    # --- TGMovieAction (5) ---
    0x006ae180: ("TGMovieAction__ctor_stream", "TGMovieAction: ctor_stream"),
    0x006b0620: ("TGMovieAction__ctor", "TGMovieAction: ctor"),
    0x006b06f0: ("TGMovieAction__dtor", "TGMovieAction: dtor"),
    0x006b0ed0: ("TGMovieAction__ProcessScheduledFrames", "TGMovieAction: ProcessScheduledFrames"),
    0x006b1010: ("TGMovieAction__DestroyAllFrameActions", "TGMovieAction: DestroyAllFrameActions"),
    # --- TGObjPtrEvent (4) ---
    0x00403320: ("TGObjPtrEvent__scalar_deleting_dtor", "TGObjPtrEvent: scalar_deleting_dtor"),
    0x006d6da0: ("TGObjPtrEvent__CopyFrom", "TGObjPtrEvent: CopyFrom"),
    0x006d6e20: ("TGObjPtrEvent__WriteToStream", "TGObjPtrEvent: WriteToStream"),
    0x006d6e50: ("TGObjPtrEvent__ReadFromStream", "TGObjPtrEvent: ReadFromStream"),
    # --- TGObject (5) ---
    0x00518ab0: ("TGObject__IsTypeOf", "TGObject: IsTypeOf"),
    0x006f0730: ("TGObject__InitDeserializationQueue", "TGObject: InitDeserializationQueue"),
    0x006f07f0: ("TGObject__InitFixupCallbackQueue", "TGObject: InitFixupCallbackQueue"),
    0x006f14e0: ("TGObject__IntToHexString", "TGObject: IntToHexString"),
    0x006f1570: ("TGObject__BuildPythonName", "TGObject: BuildPythonName"),
    # --- TGPane (1) ---
    0x0072de40: ("TGPane__dtor", "TGPane: dtor"),
    # --- TGParagraph (3) ---
    0x00731ed0: ("TGParagraph__InvalidatePolys", "TGParagraph: InvalidatePolys"),
    0x00731f40: ("TGParagraph__SetClipRectOnChildren", "TGParagraph: SetClipRectOnChildren"),
    0x00732120: ("TGParagraph__RecalcLayout", "TGParagraph: RecalcLayout"),
    # --- TGRect (2) ---
    0x0073a130: ("TGRect__WriteToStream", "TGRect: WriteToStream"),
    0x0073a170: ("TGRect__ReadFromStream", "TGRect: ReadFromStream"),
    # --- TGRootPane (1) ---
    0x00728720: ("TGRootPane__UnregisterFocus", "TGRootPane: UnregisterFocus"),
    # --- TGSceneObject (2) ---
    0x004315c0: ("TGSceneObject__SetDatabaseName", "TGSceneObject: SetDatabaseName"),
    0x00436250: ("TGSceneObject__GetObjectGroup", "TGSceneObject: GetObjectGroup"),
    # --- TGStreamedObject (2) ---
    0x006f3240: ("TGStreamedObject__scalar_deleting_dtor", "TGStreamedObject: scalar_deleting_dtor"),
    0x006f33a0: ("TGStreamedObject__FindChild", "TGStreamedObject: FindChild"),
    # --- TGStreamedObjectEx (1) ---
    0x006f2620: ("TGStreamedObjectEx__scalar_deleting_dtor", "TGStreamedObjectEx: scalar_deleting_dtor"),
    # --- TGTimerCallback (2) ---
    0x006fe800: ("TGTimerCallback__RecordStartTime", "TGTimerCallback: RecordStartTime"),
    0x007022f0: ("TGTimerCallback__StartTimer", "TGTimerCallback: StartTimer"),
    # --- TGUIObject (7) ---
    0x0072fd70: ("TGUIObject__dtor", "TGUIObject: dtor"),
    0x0072fe00: ("TGUIObject__ClearCallbackList", "TGUIObject: ClearCallbackList"),
    0x00730b80: ("TGUIObject__GetRenderTarget", "TGUIObject: GetRenderTarget"),
    0x00730df0: ("TGUIObject__IsFocused", "TGUIObject: IsFocused"),
    0x00731030: ("TGUIObject__WriteToStream", "TGUIObject: WriteToStream"),
    0x007310a0: ("TGUIObject__ReadFromStream", "TGUIObject: ReadFromStream"),
    0x00731120: ("TGUIObject__ResolveIDs", "TGUIObject: ResolveIDs"),
    # --- TargetReticleDisplay (2) ---
    0x00511e70: ("TargetReticleDisplay__UpdateCrosshair", "TargetReticleDisplay: UpdateCrosshair"),
    0x00515310: ("TargetReticleDisplay__Update", "TargetReticleDisplay: Update"),
    # --- TopWindow (1) ---
    0x00406f30: ("TopWindow__ReadFromStream", "TopWindow: ReadFromStream"),
    # --- Torpedo (1) ---
    0x00578320: ("Torpedo__SetOwnerShipID", "Torpedo: SetOwnerShipID"),
    # --- TorpedoSystem (1) ---
    0x0057b140: ("TorpedoSystem__ScalarDeletingDtor", "TorpedoSystem: ScalarDeletingDtor"),
    # --- TorpedoTube (1) ---
    0x0057d110: ("TorpedoTube__LaunchLocal", "TorpedoTube: LaunchLocal"),
    # --- TractorBeamSystem (3) ---
    0x00582170: ("TractorBeamSystem__ScalarDeletingDtor", "TractorBeamSystem: ScalarDeletingDtor"),
    0x00582710: ("TractorBeamSystem__WriteToStream", "TractorBeamSystem: WriteToStream"),
    0x00582780: ("TractorBeamSystem__ReadFromStream", "TractorBeamSystem: ReadFromStream"),
    # --- UtopiaApp (2) ---
    0x0043bc50: ("UtopiaApp__CleanupAndReset", "UtopiaApp: CleanupAndReset"),
    0x00496b40: ("UtopiaApp__dtor", "UtopiaApp: dtor"),
    # --- ViewScreenObject (3) ---
    0x00678990: ("ViewScreenObject__GetOrCreateCamera", "ViewScreenObject: GetOrCreateCamera"),
    0x00678a80: ("ViewScreenObject__HandleTargetEvent", "ViewScreenObject: HandleTargetEvent"),
    0x00678c30: ("ViewScreenObject__CreateCameraForTarget", "ViewScreenObject: CreateCameraForTarget"),
    # --- WarpEngineSubsystem (3) ---
    0x0056dfa0: ("WarpEngineSubsystem__ScalarDeletingDtor", "WarpEngineSubsystem: ScalarDeletingDtor"),
    0x0056ed40: ("WarpEngineSubsystem__WriteToStream", "WarpEngineSubsystem: WriteToStream"),
    0x0056ee20: ("WarpEngineSubsystem__ReadFromStream", "WarpEngineSubsystem: ReadFromStream"),
    # --- WeaponHitEvent (2) ---
    0x005b8750: ("WeaponHitEvent__ctor", "WeaponHitEvent: ctor"),
    0x005b8890: ("WeaponHitEvent__SetFiringPlayerID", "WeaponHitEvent: SetFiringPlayerID"),
    # --- WeaponSubsystem (3) ---
    0x005833a0: ("WeaponSubsystem__ScalarDeletingDtor", "WeaponSubsystem: ScalarDeletingDtor"),
    0x005833e0: ("WeaponSubsystem__Update", "WeaponSubsystem: Update"),
    0x005b6560: ("WeaponSubsystem__ComputeIntegrityHash", "WeaponSubsystem: ComputeIntegrityHash"),
    # --- WeaponSystem (2) ---
    0x00584240: ("WeaponSystem__ScalarDeletingDtor", "WeaponSystem: ScalarDeletingDtor"),
    0x005b6330: ("WeaponSystem__ComputeIntegrityHash", "WeaponSystem: ComputeIntegrityHash"),
    # --- WeaponsDisplay (1) ---
    0x00549940: ("WeaponsDisplay__SetFiringChainMode", "WeaponsDisplay: SetFiringChainMode"),
    # --- _Global (4) ---
    0x00407620: ("ClearTopWindowAndMPGame", "ClearTopWindowAndMPGame"),
    0x005a0b50: ("PredictPositionAtTime", "PredictPositionAtTime"),
    # --- Phase 9C: RegisterHandlers Master Dispatchers ---
    0x00442fb0: ("RegisterAllHandlerNames", "Master dispatcher: calls RegisterHandlerNames for all game classes (~22 classes)"),
    0x00443020: ("RegisterAllHandlers", "Master dispatcher: calls RegisterHandlers for all game classes (~18 classes)"),

}

# ============================================================================
# SWIG type info array
# ============================================================================
SWIG_TYPE_INFO = 0x00900a94  # Pointer array, 348 type descriptors

# ============================================================================
# Jump table for MultiplayerGame dispatcher
# ============================================================================
JUMP_TABLE = 0x0069F534  # 41 entries (opcodes 0x00-0x28)

# ============================================================================
# Python module tables (addresses from swig-method-tables.md)
# ============================================================================
PYTHON_MODULES = {
    0x008e6438: ("g_SwigMethodTable_AppAppc", "SWIG App/Appc shared method table (3990 entries)"),
    0x00961490: ("g_PyMethodTable_builtin", "__builtin__ module methods"),
    0x00963a80: ("g_PyMethodTable_imp", "imp module methods"),
    0x009643a0: ("g_PyMethodTable_marshal", "marshal module methods"),
    0x00964658: ("g_PyMethodTable_locale", "_locale module methods"),
    0x00964b60: ("g_PyMethodTable_cPickle", "cPickle module methods"),
    0x009660a8: ("g_PyMethodTable_cStringIO", "cStringIO module methods"),
    0x00966ab0: ("g_PyMethodTable_thread", "thread module methods"),
    0x00967410: ("g_PyMethodTable_time", "time module methods"),
    0x009686c0: ("g_PyMethodTable_struct", "struct module methods"),
    0x009697d8: ("g_PyMethodTable_strop", "strop module methods"),
    0x00969d28: ("g_PyMethodTable_regex", "regex module methods"),
    0x0096a078: ("g_PyMethodTable_operator", "operator module methods"),
    0x0096b888: ("g_PyMethodTable_nt", "nt (os) module methods"),
    0x0096bd88: ("g_PyMethodTable_new", "new module methods"),
    0x0096c378: ("g_PyMethodTable_math", "math module methods"),
    0x0099f5c8: ("g_PyMethodTable_errno", "errno module methods"),
    0x0096d178: ("g_PyMethodTable_cmath", "cmath module methods"),
    0x0096d818: ("g_PyMethodTable_binascii", "binascii module methods"),
    0x0096e118: ("g_PyMethodTable_array", "array module methods"),
    0x0096faa8: ("g_PyMethodTable_sys", "sys module methods"),
    0x009743d8: ("g_PyMethodTable_signal", "signal module methods"),
}


def label_or_rename(st, addr, name):
    """Create or replace a label at addr. Returns True on success."""
    # Remove any existing user-defined symbol with this name elsewhere
    for sym in st.getSymbols(name):
        if sym.getAddress() != addr and sym.getSource() == SourceType.USER_DEFINED:
            sym.delete()

    # Check if the desired label already exists at this address
    existing = st.getPrimarySymbol(addr)
    if existing is not None and existing.getName() == name:
        return True  # already correct

    # Try to set existing symbol's name, or create new label
    try:
        if existing is not None and existing.getSource() != SourceType.DEFAULT:
            existing.setName(name, SourceType.USER_DEFINED)
        else:
            st.createLabel(addr, name, SourceType.USER_DEFINED)
        return True
    except:
        # Fallback: try creating with explicit global namespace
        try:
            ns = currentProgram.getGlobalNamespace()
            st.createLabel(addr, name, ns, SourceType.USER_DEFINED)
            return True
        except:
            return False


def main():
    fm = currentProgram.getFunctionManager()
    st = currentProgram.getSymbolTable()
    listing = currentProgram.getListing()

    globals_ok = 0
    globals_fail = 0
    funcs_named = 0
    funcs_commented = 0
    funcs_skipped = 0
    funcs_fail = 0
    modules_ok = 0
    modules_skip = 0
    modules_fail = 0

    # ---- Label UtopiaModule globals ----
    println("Labeling game globals...")
    for addr_int, (name, comment) in UTOPIA_GLOBALS.items():
        addr = toAddr(addr_int)
        try:
            if label_or_rename(st, addr, name):
                listing.setComment(addr, CodeUnit.PLATE_COMMENT, comment)
                globals_ok += 1
            else:
                println("  WARN: could not label 0x%08x as %s" % (addr_int, name))
                globals_fail += 1
        except Exception, e:
            println("  ERROR at 0x%08x (%s): %s" % (addr_int, name, str(e)))
            globals_fail += 1

    # ---- Name key functions ----
    println("Naming key functions...")
    for addr_int, (name, comment) in KEY_FUNCTIONS.items():
        addr = toAddr(addr_int)
        try:
            fn = fm.getFunctionAt(addr)
            if fn is not None:
                old = fn.getName()
                # Always rename - our RE names are more meaningful
                if old != name:
                    fn.setName(name, SourceType.USER_DEFINED)
                    funcs_named += 1
                else:
                    funcs_named += 1  # already correct
                listing.setComment(addr, CodeUnit.PLATE_COMMENT, comment)
            else:
                # No function at this address - create one, then name it
                try:
                    fn = createFunction(addr, name)
                    if fn is not None:
                        listing.setComment(addr, CodeUnit.PLATE_COMMENT, comment)
                        funcs_named += 1
                    else:
                        # Can't create function, at least label it
                        if label_or_rename(st, addr, name):
                            listing.setComment(addr, CodeUnit.PLATE_COMMENT, comment)
                            funcs_named += 1
                        else:
                            println("  WARN: no function at 0x%08x, label failed for %s" % (addr_int, name))
                            funcs_fail += 1
                except:
                    # createFunction failed, try label
                    if label_or_rename(st, addr, name):
                        listing.setComment(addr, CodeUnit.PLATE_COMMENT, comment)
                        funcs_named += 1
                    else:
                        println("  WARN: no function at 0x%08x, label failed for %s" % (addr_int, name))
                        funcs_fail += 1
        except Exception, e:
            println("  ERROR at 0x%08x (%s): %s" % (addr_int, name, str(e)))
            funcs_fail += 1

    # ---- Label jump table ----
    try:
        jt_addr = toAddr(JUMP_TABLE)
        label_or_rename(st, jt_addr, "MultiplayerGame_opcodeJumpTable")
        listing.setComment(jt_addr, CodeUnit.PLATE_COMMENT,
            "Jump table for MultiplayerGame::ReceiveMessage dispatcher.\n"
            "41 entries (opcodes 0x00-0x28). Indexed by first byte of message payload.")
    except Exception, e:
        println("  ERROR labeling jump table: %s" % str(e))

    # ---- Label SWIG type info ----
    try:
        label_or_rename(st, toAddr(SWIG_TYPE_INFO), "g_SwigTypeInfo")
        listing.setComment(toAddr(SWIG_TYPE_INFO), CodeUnit.PLATE_COMMENT,
            "SWIG type descriptor pointer array (348 entries).\n"
            "Each entry: {name, converter, str, next}.\n"
            "Used by SWIG_GetPointerObj/SWIG_NewPointerObj for type checking.")
    except Exception, e:
        println("  ERROR labeling SWIG type info: %s" % str(e))

    # ---- Label Python module tables ----
    println("Labeling Python module tables...")
    for addr_int, (name, comment) in PYTHON_MODULES.items():
        addr = toAddr(addr_int)
        try:
            if label_or_rename(st, addr, name):
                listing.setComment(addr, CodeUnit.PLATE_COMMENT, comment)
                modules_ok += 1
            else:
                println("  WARN: could not label 0x%08x as %s" % (addr_int, name))
                modules_fail += 1
        except Exception, e:
            println("  ERROR at 0x%08x (%s): %s" % (addr_int, name, str(e)))
            modules_fail += 1

    # ---- Summary ----
    total_funcs = len(KEY_FUNCTIONS)
    total_modules = len(PYTHON_MODULES)
    println("")
    println("=" * 60)
    println("Game Globals & Functions Annotation Complete")
    println("  Globals labeled:         %d / %d" % (globals_ok, len(UTOPIA_GLOBALS)))
    if globals_fail > 0:
        println("  Globals FAILED:          %d" % globals_fail)
    println("  Functions named:         %d / %d" % (funcs_named, total_funcs))
    if funcs_fail > 0:
        println("  Functions FAILED:        %d" % funcs_fail)
    println("  Module tables labeled:   %d / %d" % (modules_ok, total_modules))
    if modules_fail > 0:
        println("  Module tables FAILED:    %d" % modules_fail)
    println("=" * 60)

main()
