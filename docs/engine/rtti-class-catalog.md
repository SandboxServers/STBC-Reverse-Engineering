> [docs](../README.md) / [engine](README.md) / rtti-class-catalog.md

---
title: stbc.exe RTTI / Class Catalog
type: reference
audience: re-engineer
validated: 2026-05-28
methodology: FUNCTION_DOC_WORKFLOW_V5
binary:
  name: STBC.exe
  size: 6394712
  base: 0x00400000
status: partial
evidence:
  - claim: "stbc.exe was compiled with MSVC RTTI disabled (/GR-) for all game and engine code"
    address: null
    function: null
    confidence: high
    note: "Only MSVC TypeDescriptors present belong to CRT/STL (21 entries) plus one game throw-type (TGStreamException). No NiObject/TGObject _TypeDescriptor exists. Verified by scanning .data for the `.?AV` pattern."
  - claim: "21 MSVC _TypeDescriptor structures plus 1 MSVC throw-type for TGStreamException"
    address: 0x00979A18
    function: null
    confidence: high
    note: "TypeDescriptors at 0x00979A18-0x00979E98 (all CRT/STL). The `.?AV` and `.PAV` are distinct MSVC RTTI structures — don't conflate them."
  - claim: "TGStreamException MSVC throw-type at 0x0095AD10"
    address: 0x0095AD10
    function: null
    confidence: high
    note: "Byte-perfect `.PAVTGStreamException@@\\0` at this address. The only game-specific exception with MSVC RTTI, used with C++ throw/catch."
  - claim: "NiRTTI factory hash table at DAT_009a2b98 with 37 buckets"
    address: 0x009a2b98
    function: null
    confidence: high
    note: "237 xrefs; 117 factory registrations partition into 37 buckets (0x25). Vtable PTR_FUN_0088b7c4 — see nirtti-factory-catalog.md."
  - claim: "117 NiRTTI factory registrations"
    address: null
    function: null
    confidence: high
    note: "Of 129 NI classes catalogued, 117 are registered with the factory table; the remaining 12 are abstract bases or stream-only types — exact partition deferred for netimmerse-vtables.md."
  - claim: "NiNode registration FUN_007e3670, factory FUN_007e5450, string at 0x00978500"
    address: 0x007e3670
    function: FUN_007e3670
    confidence: high
    note: "Canonical example of the NiRTTI registration pattern. String s_NiNode at 0x00978500 is pushed alongside factory FUN_007e5450."
  - claim: "NiObject class-name string at 0x009780D8"
    address: 0x009780D8
    function: null
    confidence: high
    note: "Bare class-name string anchor for the root of the NiRTTI tree."
  - claim: "NI bare class-name strings occupy .data range 0x00975E98-0x009799F8"
    address: 0x00975E98
    function: null
    confidence: high
    note: "Sampled — full enumeration of all 129 NI bare-string addresses deferred to netimmerse-vtables.md."
  - claim: "All TG class-name strings live in the .data segment (0x008bb000-0x009b5357)"
    address: null
    function: null
    confidence: high
    note: "Per list_segments on STBC.exe; .rdata is 0x00888000-0x008bafff and does NOT contain TG class strings. The prior `.rdata 0x008Dxxxx` claim was wrong."
  - claim: "TG bare class-name strings cluster into three sub-regions: 0x008D8000-0x008E6000 (early classes), 0x00958000-0x0095D200 (SWIG table), 0x00932B00-0x00933600 (input events)"
    address: 0x008D8000
    function: null
    confidence: high
    note: "Primary early cluster ~18 classes (animation events, math/data, dimmer, fuzzy, model property, window, paragraph). Secondary SWIG cluster ~47 classes (actions, scripting, UI, sound, music, network, typed events). Outlier input-event cluster 5 classes."
  - claim: "TG bare-string addresses verified for 28 originally-listed classes (re-anchored 2026-05-28)"
    address: null
    function: null
    confidence: high
    note: "Phase 2.6 re-derivation: 28 of 81 originally-listed TG classes have confirmed bare-string addresses; their row addresses are updated. See body for the [v5-validated 2026-05-28] tag."
  - claim: "41 newly-discovered TG classes added to catalog"
    address: 0x008d8594
    function: null
    confidence: high
    note: "Bare-string anchors for TGObjPtrEvent, TGScriptAction, TGStringEvent, and 38 others — slotted into appropriate subsections."
  - claim: "TGBufferStream is an internal C++ class with no bare class-name string in the binary"
    address: 0x008958D0
    function: null
    confidence: high
    note: "v5-validated vtable at 0x008958D0 (parallel investigation). Anchored via factory ID / vtable rather than bare string. Same applies to TGStream, TGMessage subclasses, TGWinsockNetwork, etc."
  - claim: "Game-specific class-name strings sampled at canonical addresses (ShipClass, ShipSubsystem, MultiplayerGame, DamageableObject)"
    address: 0x008D8AC0
    function: null
    confidence: medium
    note: "Spot-checked. Full enumeration of all ~420 game-specific class strings deferred — surface as documentation debt."
  - claim: "TG SWIG method counts are aspirational identifier counts pending v5 verification"
    address: null
    function: null
    confidence: low
    note: "Per-class 'method count' column equals `^ClassName_` prefix string count in the binary, which mixes bound methods with enum/constant identifiers (e.g., TGSound_SS_PLAYING). Actual bound-method counts typically 3-10 lower. Aggregate ~1,340 should read as '~1,340 SWIG-bound Python identifiers (methods + constants)'."
companions:
  - docs/engine/nirtti-factory-catalog.md
  - docs/engine/gamebryo-cross-reference.md
  - docs/engine/netimmerse-vtables.md
  - docs/engine/function-map.md
  - docs/engine/v5-validation-status.md
supersedes:
  - 2026-02-15
---

# RTTI Class Catalog - stbc.exe

> [!NOTE]
> This doc is `status: partial`. The MSVC RTTI section, NiRTTI factory anchors, and the TG section are v5-verified against the current Ghidra import (2026-05-28). The NetImmerse and game-specific catalog rows are **sampled** — canonical anchors confirmed, but full enumeration is deferred. SWIG method-count columns carry `confidence: low` because they conflate bound methods with constant identifiers. See [docs/guides/v5-evidence-header.md](../guides/v5-evidence-header.md) for the standard.

Complete catalog of class type information extracted from the Star Trek: Bridge Commander
executable (`stbc.exe`, ~6.1 MB, 32-bit PE, base 0x00400000).

## Key Finding: No MSVC RTTI for Game/Engine Classes

stbc.exe was compiled with MSVC RTTI **disabled** (`/GR-`) for all game and engine code. The
binary contains **21 standard MSVC `_TypeDescriptor` structures** (all CRT / STL) and **1 MSVC
throw-type / ThrowInfo** (`.PAV` pattern) for `TGStreamException`. The `.?AV` (TypeDescriptor)
and `.PAV` (throw-type) are distinct MSVC RTTI structures — don't conflate them.

Instead, the game uses **two custom type information systems**:

1. **NetImmerse NiRTTI** -- A custom factory/registration system where class name strings are
   registered into a hash table (at `DAT_009a2b98`) along with factory functions. Each class
   has a static registration function (e.g., `FUN_007e3670` for NiNode) that runs once.

2. **SWIG 1.x Python Binding Tables** -- Method tables containing `ClassName_MethodName` string
   pairs that register C++ methods as Python callables. These account for the majority of
   class name strings in the binary (thousands of entries).

---

## MSVC RTTI TypeDescriptors (21 entries, all CRT/STL)

All located in `.data` segment (0x00979A18-0x00979E98). Pattern: `.?AVClassName@@`

| Address | Mangled Name | Demangled |
|---------|-------------|-----------|
| 0x00979A18 | `.?AVios_base@std@@` | std::ios_base |
| 0x00979A38 | `.?AV?$basic_ios@DU?$char_traits@D@std@@@std@@` | std::basic_ios<char> |
| 0x00979A70 | `.?AV?$basic_istream@DU?$char_traits@D@std@@@std@@` | std::basic_istream<char> |
| 0x00979AB0 | `.?AV?$basic_ostream@DU?$char_traits@D@std@@@std@@` | std::basic_ostream<char> |
| 0x00979AF0 | `.?AV?$basic_streambuf@DU?$char_traits@D@std@@@std@@` | std::basic_streambuf<char> |
| 0x00979B30 | `.?AV?$basic_filebuf@DU?$char_traits@D@std@@@std@@` | std::basic_filebuf<char> |
| 0x00979B70 | `.?AV?$basic_ios@GU?$char_traits@G@std@@@std@@` | std::basic_ios<wchar_t> |
| 0x00979BA8 | `.?AV?$basic_istream@GU?$char_traits@G@std@@@std@@` | std::basic_istream<wchar_t> |
| 0x00979BE8 | `.?AV?$basic_ostream@GU?$char_traits@G@std@@@std@@` | std::basic_ostream<wchar_t> |
| 0x00979C28 | `.?AV?$basic_filebuf@GU?$char_traits@G@std@@@std@@` | std::basic_filebuf<wchar_t> |
| 0x00979C68 | `.?AV?$basic_streambuf@GU?$char_traits@G@std@@@std@@` | std::basic_streambuf<wchar_t> |
| 0x00979CA8 | `.?AVexception@@` | exception |
| 0x00979CC0 | `.?AVlogic_error@std@@` | std::logic_error |
| 0x00979CE0 | `.?AVlength_error@std@@` | std::length_error |
| 0x00979D00 | `.?AVout_of_range@std@@` | std::out_of_range |
| 0x00979D28 | `.?AVruntime_error@std@@` | std::runtime_error |
| 0x00979D48 | `.?AVfailure@ios_base@std@@` | std::ios_base::failure |
| 0x00979D70 | `.?AVfacet@locale@std@@` | std::locale::facet |
| 0x00979D90 | `.?AV_Locimp@locale@std@@` | std::locale::_Locimp |
| 0x00979DB8 | `.?AVbad_alloc@std@@` | std::bad_alloc |
| 0x00979E98 | `.?AVtype_info@@` | type_info |

### MSVC Throw Type (`.PAV` pointer-to-class)

| Address | Name |
|---------|------|
| 0x0095AD10 | `.PAVTGStreamException@@` [v5-validated 2026-05-28] |

This is the only game-specific exception class with MSVC RTTI, used with C++ throw/catch. The
`.PAV` pattern is the MSVC throw-type / ThrowInfo structure — a distinct RTTI artifact from
`.?AV` TypeDescriptors. The binary contains exactly one `.PAV` entry and 21 `.?AV` entries.

---

## NetImmerse 3.1 Classes (129 catalogued, sampled anchors)

These are the core engine classes from the NetImmerse 3.1 SDK. Class name strings are located
primarily in `.data` at 0x00975E98-0x009799F8 (sampled — full enumeration deferred to the
`netimmerse-vtables.md` v5 pass). Each class registers itself into the NiRTTI factory hash
table via a static initialization function.

Of 129 NI classes catalogued, **117 are registered** with the NiRTTI factory table; the
remaining 12 are abstract bases or stream-only types. Exact partition deferred for the
netimmerse-vtables.md validation pass.

Registration pattern (from `FUN_007e3670` -- NiNode registration):
```
push FUN_007e5450          ; factory function
push offset s_NiNode       ; "NiNode" string at 0x00978500
call hash_insert           ; register in DAT_009a2b98
```

For the complete factory registration mapping (all 117 entries with registration function,
factory function, and guard flag addresses), see
[nirtti-factory-catalog.md](nirtti-factory-catalog.md).

### Scene Graph / Node Hierarchy
| Address | Class | Description |
|---------|-------|-------------|
| 0x009780D8 | NiObject | Root of all NiRTTI objects |
| 0x00978228 | NiObjectNET | Named object with time controllers |
| 0x0095B050 | NiAVObject | Audio-Visual object (transform, bounds, properties) |
| 0x00978500 | NiNode | Scene graph interior node (children list) |
| 0x009788A8 | NiBillboardNode | Auto-facing node |
| 0x00978908 | NiBone | Skeletal animation bone |
| 0x00978910 | NiBSPNode | Binary space partition node |
| 0x0097893C | NiCollisionSwitch | Enables/disables collision per-node |
| 0x00978A24 | NiFltAnimationNode | Flight animation node |
| 0x00978AE8 | NiLODNode | Level-of-detail switcher |
| 0x00978E88 | NiSortAdjustNode | Sort order override |
| 0x009789E4 | NiSwitchNode | Child visibility switcher |

### Geometry
| Address | Class | Description |
|---------|-------|-------------|
| 0x00978770 | NiGeometry | Base geometry class |
| 0x0097873C | NiGeometryData | Vertex/normal/UV data |
| 0x0097877C | NiTriBasedGeomData | Triangle-based geometry data |
| 0x009787A0 | NiTriBasedGeom | Triangle-based geometry |
| 0x009787BC | NiTriShapeData | Triangle list data |
| 0x009787EC | NiTriShape | Triangle list mesh |
| 0x0097920C | NiTriShapeDynamicData | Dynamic (mutable) triangle data |
| 0x009789B8 | NiEnvMappedTriShapeData | Environment-mapped mesh data |
| 0x009789D0 | NiEnvMappedTriShape | Environment-mapped mesh |
| 0x009791F0 | NiTrianglesData | Alternative triangle data |
| 0x00979200 | NiTriangles | Alternative triangle mesh |
| 0x00979268 | NiTriStripData | Triangle strip data |
| 0x00979278 | NiTriStrip | Triangle strip mesh |
| 0x00979284 | NiTriStripsData | Multiple triangle strips data |
| 0x009792C4 | NiTriStrips | Multiple triangle strips mesh |
| 0x00978AC8 | NiLinesData | Line geometry data |
| 0x00978AE0 | NiLines | Line geometry |
| 0x00978520 | NiScreenPolygon | 2D screen-space polygon |

### Bezier Geometry (NIF Bezier Patch Support)
| Address | Class |
|---------|-------|
| 0x009798A8 | NiBezierMesh |
| 0x00979944 | NiBezierPatch |
| 0x009799BC | NiBezierRectangle |
| 0x009799D0 | NiBezierRectangle2 |
| 0x009799E4 | NiBezierRectangle3 |
| 0x0097996C | NiBezierTriangle |
| 0x00979980 | NiBezierTriangle2 |
| 0x00979994 | NiBezierTriangle3 |
| 0x009799A8 | NiBezierTriangle4 |
| 0x009799F8 | NiBezierCylinder |
| 0x00979954 | NiBezierSkinController |

### Properties (Render State)
| Address | Class | Description |
|---------|-------|-------------|
| 0x0097823C | NiProperty | Base property |
| 0x00978620 | NiAlphaProperty | Alpha blending |
| 0x00978960 | NiCorrectionProperty | Color correction |
| 0x00978998 | NiDitherProperty | Dithering |
| 0x00978A50 | NiFogProperty | Fog |
| 0x00978B40 | NiMaterialProperty | Material (diffuse, specular, etc.) |
| 0x00978D2C | NiMultiTextureProperty | Multi-texturing |
| 0x00978E58 | NiShadeProperty | Shading model |
| 0x00978EA4 | NiSpecularProperty | Specular highlights |
| 0x00978EEC | NiStencilProperty | Stencil buffer |
| 0x00978B74 | NiTextureModeProperty | Texture filtering/wrapping |
| 0x0097919C | NiTextureProperty | Texture assignment |
| 0x009791BC | NiTransparentProperty | Transparency |
| 0x009792D0 | NiVertexColorProperty | Vertex coloring |
| 0x00979380 | NiWireframeProperty | Wireframe mode |
| 0x009793A4 | NiZBufferProperty | Z-buffer |

### Lights
| Address | Class | Description |
|---------|-------|-------------|
| 0x009787F8 | NiLight | Base light |
| 0x009784D8 | NiDynamicEffect | Dynamic lighting/effects |
| 0x00978824 | NiAmbientLight | Ambient light |
| 0x00978984 | NiDirectionalLight | Directional light |
| 0x00978E24 | NiPointLight | Point light |
| 0x00978EC0 | NiSpotLight | Spot light |
| 0x00979084 | NiTextureEffect | Texture projection effect |

### Controllers / Animation
| Address | Class | Description |
|---------|-------|-------------|
| 0x00978118 | NiTimeController | Base animation controller |
| 0x00975FBC | NiAlphaController | Alpha animation |
| 0x00975F7C | NiFlipController | Flipbook animation |
| 0x00975F90 | NiFloatController | Float value animation |
| 0x00975F64 | NiKeyframeController | Keyframe animation |
| 0x009760CC | NiKeyframeManager | Multi-sequence keyframe manager |
| 0x009761DC | NiLightColorController | Light color animation |
| 0x009761F4 | NiLookAtController | Look-at constraint |
| 0x0097626C | NiMaterialColorController | Material color animation |
| 0x00976208 | NiMorphController | Morph target animation |
| 0x00976250 | NiMorpherController | Alternative morph controller |
| 0x009762B0 | NiPathController | Path following |
| 0x009762C4 | NiParticleSystemController | Particle system driver |
| 0x009762E0 | NiRollController | Roll animation |
| 0x00978E74 | NiSkinController | Skeletal mesh skinning |
| 0x0097924C | NiTriShapeSkinController | Per-shape skin controller |
| 0x00976328 | NiVisController | Visibility animation |

### Animation Data
| Address | Class | Description |
|---------|-------|-------------|
| 0x00975F20 | NiKeyframeData | Keyframe animation data |
| 0x00975FA4 | NiFloatData | Float animation data |
| 0x00976070 | NiColorData | Color animation data |
| 0x0097621C | NiMorphData | Morph target data |
| 0x009761D0 | NiPosData | Position animation data |
| 0x0097630C | NiVisData | Visibility animation data |
| 0x00976058 | NiAnimBlender | Animation blending |

### Extra Data / Metadata
| Address | Class | Description |
|---------|-------|-------------|
| 0x00978100 | NiExtraData | Base extra data |
| 0x008DD2A8 | NiBinaryVoxelData | Binary voxel data |
| 0x008DD2BC | NiBinaryVoxelExtraData | Voxel extra data |
| 0x009797A4 | NiCloneExtraData | Clone tracking data |
| 0x00979064 | NiStringExtraData | String metadata |
| 0x00976044 | NiTextKeyExtraData | Text key markers (animation events) |
| 0x00979368 | NiVertWeightsExtraData | Vertex weight data |
| 0x009762F4 | NiSequenceStreamHelper | Sequence stream helper |

### Physics / Collision
| Address | Class | Description |
|---------|-------|-------------|
| 0x0097607C | NiForce | Base force |
| 0x00976084 | NiGravity | Gravity force |
| 0x00976090 | NiParticleBomb | Particle explosion force |
| 0x009760A0 | NiSphericalCollider | Sphere collision |
| 0x009760B4 | NiPlanarCollider | Plane collision |

### Rendering / Images
| Address | Class | Description |
|---------|-------|-------------|
| 0x009784F4 | NiRender | Base renderer |
| 0x00976724 | NiD3DRender | Direct3D renderer |
| 0x009783DC | NiImage | Image/texture data |
| 0x00978330 | NiRawImageData | Raw pixel data |
| 0x00976EB0 | NiDDImage | DirectDraw image |
| 0x00976EBC | NiDDBufferImage | DirectDraw buffer image |
| 0x0097856C | NiCamera | Camera |
| 0x009785F4 | NiClusterAccumulator | Cluster-based accumulator |
| 0x009780F0 | NiAccumulator | Base rendering accumulator |
| 0x0097860C | NiAlphaAccumulator | Alpha sorting accumulator |

### Audio
| Address | Class | Description |
|---------|-------|-------------|
| 0x00975EA4 | NiSoundSystem | Sound system |
| 0x00975EB4 | NiSource | Audio source |
| 0x00975E98 | NiListener | Audio listener |
| 0x00975EC0 | NiProvider_Info | Audio provider info |

### Math / Data Types
| Address | Class | Description |
|---------|-------|-------------|
| 0x008E3568 | NiPoint2 | 2D point/vector |
| 0x00914967 | NiPoint3 | 3D point/vector |
| 0x008E2DC8 | NiColorA | RGBA color |
| 0x00913B3F | NiColor | RGB color |
| 0x00914513 | NiFrustum | View frustum |

### Template Instantiations
| Address | Class |
|---------|-------|
| 0x00914B83 | NiTList\<ShipSubsystem\> |
| 0x009145B7 | NiTListIterator |

### Smart Pointer Types
| Address | Class |
|---------|-------|
| 0x0091342B | NiSourcePtr |
| 0x00913BD3 | NiCameraPtr |
| 0x0092B94F | NiSourceObj |

### Constants
| Address | Name |
|---------|------|
| 0x00956018 | NiPoint2_UNIT_Y |
| 0x00956028 | NiPoint2_UNIT_X |
| 0x00956038 | NiPoint2_ZERO |
| 0x00956048 | NiColorA_BLACK |
| 0x00956058 | NiColorA_WHITE |
| 0x00956068 | NiColor_BLACK |
| 0x00956078 | NiColor_WHITE |

---

## Totally Games Framework Classes (~70 confirmed)

The TG framework is the game engine layer built on top of NetImmerse. All TG class-name
strings live in the `.data` segment (0x008bb000-0x009b5357 per `list_segments`; `.rdata` is
0x00888000-0x008bafff and does **not** contain TG class strings).

TG bare class-name strings occupy three sub-regions:

- **Primary cluster:** 0x008D8000-0x008E6000 — ~18 early classes (animation events, math/data,
  dimmer, fuzzy, model property, window, paragraph).
- **Secondary cluster:** 0x00958000-0x0095D200 — the SWIG-driven TG class string table,
  ~47 classes (actions, scripting, UI, sound, music, network, typed events).
- **Outlier cluster:** 0x00932B00-0x00933600 — 5 typed input-event classes (TGShortEvent,
  TGVoidPtrEvent, TGIEvent, TGMouseEvent, TGKeyboardEvent, TGGamepadEvent).

The 0x0091xxxx-0x0094xxxx range previously cited holds SWIG `_p_<class>\0` pointer-type
strings, where bare class names appear as substrings 3 bytes into the `_p_` prefix. Those
offsets are **not** canonical anchors for class-identity purposes — addresses below have been
re-anchored to the bare-string locations.

> [!NOTE]
> The prior catalog claimed "124 unique TG classes". That count was inflated by ~34
> speculative-by-analogy rows (UI widgets named after Windows conventions, Manager classes by
> pattern-matching) that have **no** matching string in the binary. Those rows are dropped.
> Real internal C++ classes that exist but have no bare string (because they are not
> SWIG-bound) are listed separately under "Internal C++ classes (no SWIG binding)" below.

### Core Framework
| Address | Class | SWIG Identifiers | Description |
|---------|-------|------------------|-------------|
| 0x0095b05c | TGObject | 9 | Base game object [v5-validated 2026-05-28] |
| 0x0095ad70 | TGEvent | 21 | Event system base [v5-validated 2026-05-28] |
| 0x0095ae00 | TGEventHandlerObject | 7 | Event handler [v5-validated 2026-05-28] |
| 0x0095b9a8 | TGSequence | 8 | Action sequence [v5-validated 2026-05-28] |
| 0x008DBA14 | TGCondition | 8 | Conditional logic |
| 0x0095ad28 | TGPythonInstanceWrapper | 1 | Python-to-C++ bridge [v5-validated 2026-05-28] |
| 0x0095b328 | TGAttrObject | 7 | Attributed object [v5-validated 2026-05-28] |
| 0x0095b2f4 | TGTemplatedAttrObject | 1 | Templated attributed object [v5-validated 2026-05-28] |
| 0x008DA004 | TGString | 7 | String class |
| 0x008D9808 | TGPoint3 | 35 | 3D vector (wraps NiPoint3) |

### Actions / Scripting
| Address | Class | SWIG Identifiers | Description |
|---------|-------|------------------|-------------|
| 0x0095b874 | TGAction | 20 | Base action [v5-validated 2026-05-28] |
| 0x0095b71c | TGActionManager | 3 | Action scheduler [v5-validated 2026-05-28] |
| 0x0095b758 | TGAnimAction | 5 | Animation action [v5-validated 2026-05-28] |
| 0x0095b778 | TGAnimPosition | 2 | Animation position [v5-validated 2026-05-28] |
| 0x0095b708 | TGConditionAction | 4 | Conditional action [v5-validated 2026-05-28] |
| 0x0095a9f0 | TGCreditAction | 10 | Credits sequence [v5-validated 2026-05-28] |
| 0x0095a998 | TGMovieAction | 10 | Movie playback action [v5-validated 2026-05-28] |
| 0x0095B83C | TGOverlayAction | — | Overlay display action |
| 0x0095B7C0 | TGPhonemeAction | — | Lip-sync phoneme action |
| 0x008D85CC | TGScriptAction | — | Python script action |
| 0x0095b79c | TGSoundAction | 7 | Sound playback action [v5-validated 2026-05-28] |
| 0x008E0F20 | TGTimedAction | — | Time-delayed action |

### Events (Typed)
| Address | Class | Description |
|---------|-------|-------------|
| 0x009332a4 | TGIEvent | Input event base [v5-validated 2026-05-28] |
| 0x008D9840 | TGBoolEvent | Boolean event |
| 0x008E54D0 | TGCharEvent | Character event |
| 0x008DCE9C | TGFloatEvent | Float event |
| 0x0095AA78 | TGGameSpyEvent | GameSpy event |
| 0x008DAC5C | TGIntEvent | Integer event |
| 0x00933430 | TGKeyboardEvent | Keyboard event [v5-validated 2026-05-28] |
| 0x00933574 | TGGamepadEvent | Gamepad input [v5-validated 2026-05-28] |
| 0x0095aa30 | TGMessageEvent | Network message event [v5-validated 2026-05-28] |
| 0x00933314 | TGMouseEvent | Mouse input (15 identifiers) [v5-validated 2026-05-28] |
| 0x0095BAA8 | TGMusicFadeEvent | Music fade event |
| 0x008D8594 | TGObjPtrEvent | Object pointer event |
| 0x0095aa54 | TGPlayerEvent | Player event [v5-validated 2026-05-28] |
| 0x009580E4 | TGSequenceEvent | Sequence event |
| 0x00932b00 | TGShortEvent | Short integer event [v5-validated 2026-05-28] |
| 0x008D8764 | TGStringEvent | String event |
| 0x00932d50 | TGVoidPtrEvent | Void pointer event [v5-validated 2026-05-28] |

### Networking (SWIG-bound)
| Address | Class | SWIG Identifiers | Description |
|---------|-------|------------------|-------------|
| 0x0095aa14 | TGNetwork | 50 | Network abstraction [v5-validated 2026-05-28] |

See **Internal C++ classes** below for `TGWinsockNetwork`, `TGNetGroup`, `TGNetPlayer`,
`TGPlayerList`, `TGGroupPlayer`, `TGEncrypt`, `TGNetworkListType` — these are real C++
classes used by the network layer but have no bare class-name string in the binary because
they are not exposed to Python via SWIG. The prior catalog rows for those classes pointed at
`_p_` SWIG pointer-type substrings, not at canonical class-name anchors.

### Managers (Singletons, SWIG-bound)
| Address | Class | SWIG Identifiers | Description |
|---------|-------|------------------|-------------|
| 0x0095b71c | TGActionManager | 3 | Action scheduler |
| 0x0095ba70 | TGSoundManager | 33 | Sound management |

The prior catalog listed many additional "manager" classes (TGEventManager, TGModuleManager,
TGRenderManager, TGAudioManager, TGSystemManager, TGFileManager, TGTextureManager,
TGNiManager, TGPlayManager, TGScriptManager, TGMessageManager, TGTimerManager, TGGameManager,
TGControlManager, TGVarManager). **None of those strings exist in the binary** — they were
speculative-by-analogy with conventional engine naming. They are dropped from this catalog.
The real manager-style classes use the names above plus the four below (which are
SWIG-bound but distributed across other clusters):

| Address | Class | SWIG Identifiers | Description |
|---------|-------|------------------|-------------|
| 0x00912C93 | TGInputManager | 41 | Input handling |
| 0x00912CB7 | TGIconManager | 22 | Icon management |
| 0x00912B33 | TGModelPropertyManager | 18 | Model property management |
| 0x00912C1B | TGModelManager | 17 | Model management |
| 0x00912AEF | TGMovieManager | 7 | Movie playback |
| 0x00912BBF | TGPoolManager | 9 | Object pool management |
| 0x00912BEB | TGLocalizationManager | 6 | Localization |
| 0x00912B9B | TGFontManager | 8 | Font management |
| 0x00912B77 | TGUIThemeManager | 4 | UI theme management |

(The 0x00912xxxx range above lists SWIG `_p_TGxxxManager` substring addresses pending
re-anchoring to bare strings in a follow-up pass — flagged as documentation debt.)

### UI Framework (SWIG-bound)
| Address | Class | SWIG Identifiers | Description |
|---------|-------|------------------|-------------|
| 0x0095cd48 | TGFrame | 17 | Frame container [v5-validated 2026-05-28] |
| 0x0095cd5c | TGFrameWindow | — | Frame window |
| 0x0095cf1c | TGPane | 26 | Pane container [v5-validated 2026-05-28] |
| 0x0095ce8c | TGRootPane | 21 | Root UI pane |
| 0x0095ce54 | TGButton | 5 | Button [v5-validated 2026-05-28] |
| 0x0095ce34 | TGButtonBase | 11 | Button base |
| 0x0095ce6c | TGTextButton | 19 | Text button [v5-validated 2026-05-28] |
| 0x0095ce20 | TGIcon | 12 | Icon |
| 0x0095cdec | TGConsole | 7 | Debug console |
| 0x0095cd90 | TGDialogWindow | 28 | Dialog window [v5-validated 2026-05-28] |
| 0x0095CDB4 | TGStringDialog | — | String input dialog |
| 0x0095ce08 | TGPrompt | 3 | Prompt dialog |
| 0x0095cf90 | TGUIObject | 94 | Base UI object (largest binding) [v5-validated 2026-05-28] |
| 0x00914DF3 | TGUITheme | 16 | UI theme |
| 0x008E3574 | TGParagraph | 34 | Text paragraph |
| 0x008E4A41 | TGParagraphSoundHandler | — | Paragraph sound |
| 0x008E4A5C | TGWindow | 4 | Base window |

### Model Properties
| Address | Class | SWIG Identifiers | Description |
|---------|-------|------------------|-------------|
| 0x008e5d1c | TGModelPropertySet | 4 | Property set |
| 0x0095b00c | TGModelProperty | 11 | Model property |
| 0x00912357 | TGModelPropertyInstance | 4 | Property instance (pending bare-anchor re-derivation) |
| 0x009133D7 | TGModelPropertyList | 5 | Property list (pending bare-anchor re-derivation) |

### Audio / Music
| Address | Class | SWIG Identifiers | Description |
|---------|-------|------------------|-------------|
| 0x009124AF | TGSound | 63 | Sound (pending bare-anchor re-derivation) |
| 0x0095ba94 | TGMusic | 9 | Music |
| 0x0095baa8 | TGMusicFadeEvent | — | Music fade event |
| 0x0095bb14 | TGSoundRegion | 8 | Spatial audio region |
| 0x0095B7C0 | TGPhonemeAction | — | Lip-sync phoneme action |
| 0x0095B7F8 | TGPhonemeSequence | — | Lip-sync sequence |
| 0x00913003 | TGRedbookClass | 12 | CD audio (Redbook) (pending bare-anchor re-derivation) |

### Scene Graph Extensions
| Address | Class | Description |
|---------|-------|-------------|
| 0x0095abc0 | TGAnimNode | Animation scene node (14 identifiers) |
| 0x0095abcc | TGAnimBlender | Animation blender |
| 0x008DAED4 | TGDimmerController | Brightness controller |
| 0x008DAEE8 | TGFuzzyTriShape | Soft-edged geometry |
| 0x008E5D88 | TGFuzzyClusterGeom | Fuzzy cluster geometry |
| 0x008E5D70 | TGFuzzyClusterInnerGeom | Fuzzy cluster inner geometry |
| 0x008DAEF8 | TGOverlayController | Overlay controller |
| 0x008E5D1C | TGModelPropertySet | Property set |

### Localization
| Address | Class | Description |
|---------|-------|-------------|
| 0x0095ACD8 | TGLocalizationDatabase | Localization DB (5 identifiers) |
| 0x00930A74 | TGLocDBWrapperSerialize | Localization serializer |
| 0x00930A58 | TGLocDBWrapperUnserialize | Localization deserializer |

### Miscellaneous (SWIG-bound)
| Address | Class | Description |
|---------|-------|-------------|
| 0x0095d188 | TGFontGroup | Font group (17 identifiers) |
| 0x0095cf10 | TGIconGroup | Icon group (21 identifiers) |
| 0x0091338B | TGConfigMapping | Configuration (11 identifiers, pending bare-anchor) |
| 0x00913B5B | TGGroupList | Group list (pending bare-anchor) |
| 0x0091306B | TGPMWalkObjectsFunc | Property manager walk (pending bare-anchor) |
| 0x009145FB | TGStringToStringMap | String-to-string map (pending bare-anchor) |
| 0x0095ae88 | TGTimer | Timer (10 identifiers) |
| 0x0091340B | TGPhoneme | Phoneme data (pending bare-anchor) |
| 0x00913DEB | TGConditionHandler | Condition handler (3 identifiers, pending bare-anchor) |

### Other / Newly-discovered (v5 sweep additions)

The Phase 2.6 re-derivation pulled 41 previously-uncatalogued bare TG class-name strings out
of the .data clusters. Most are slotted into the subsections above; the remainder live here.

| Address | Class | Description |
|---------|-------|-------------|
| 0x008E5D1C | TGModelPropertySet | (also listed under Model Properties) |

(Remaining 40 newly-discovered classes are already integrated into the appropriate
subsections above with `[v5-validated 2026-05-28]` tags where applicable.)

---

## Internal C++ classes (no SWIG binding)

These are real C++ classes used internally by the engine but never exposed to Python, so no
bare class-name string was emitted in the binary. They are anchored via factory ID, vtable
address, or an internal-use note rather than a bare string. The prior catalog listed many of
these with addresses that were actually `_p_<class>` SWIG pointer-type substrings, not
canonical anchors — those address citations were removed.

### Streaming / Serialization

| Class | Anchor | Description |
|-------|--------|-------------|
| TGStream | (internal C++ class — no SWIG binding) | Base stream |
| TGBufferStream | SWIG-visible class. Bare string 0x0091277C (`_p_TGBufferStream`); vtable 0x00895C58; ctor FUN_006CEFE0; size 0x30 [v5-validated 2026-05-28; corrected from prior mis-identification] | Buffer-cursor stream over external buffer. Used by TGMessage handlers to extract typed payload. See `docs/protocol/stream-primitives.md`. |
| TGProfilingInfo | (internal C++ class — no SWIG binding) | Performance profiling (pending vtable confirmation) |

### Network Messages (factory-anchored)

These are real internal C++ classes per [docs/protocol/transport-layer.md](../protocol/transport-layer.md);
each has a factory ID in the 0x0100-0x010D range, no bare class-name string.

| Class | Anchor | Description |
|-------|--------|-------------|
| TGMessage | SWIG-visible class. Bare string 0x00913685 (`_p_TGMessage`); vtable 0x008958D0; ctor FUN_006B82A0; size 0x40 [v5-validated 2026-05-28] | Base wire-message envelope. Slot 0 (GetTypeId) returns 0x32 — emitted as first byte of every serialized blob. Derived subclasses: TGConnectMessage, TGDisconnectMessage, TGAckMessage, TGBootPlayerMessage, TGDoNothingMessage, TGNameChangeMessage. See `docs/protocol/stream-primitives.md` § "Two Stream Classes". |
| TGAckMessage | (internal C++ class) factory ID ~0x0100 | Acknowledgement message |
| TGBootPlayerMessage | (internal C++ class) factory ID ~0x010D | Boot/kick player message |
| TGConnectMessage | (internal C++ class) factory ID ~0x0101 | Connection message |
| TGDisconnectMessage | (internal C++ class) factory ID ~0x0102 | Disconnection message |
| TGDoNothingMessage | (internal C++ class) factory ID ~0x0103 | No-op/keepalive message |
| TGNameChangeMessage | (internal C++ class) factory ID ~0x0104 | Name change message |

### Networking (factory- / vtable-anchored)

Real internal C++ classes per [docs/networking/network-protocol.md](../networking/network-protocol.md).

| Class | Anchor | Description |
|-------|--------|-------------|
| TGWinsockNetwork | (internal C++ class — no SWIG binding) | UDP network (WSN) |
| TGNetworkListType | (internal C++ class — no SWIG binding) | Network list type |
| TGNetGroup | (internal C++ class — no SWIG binding) | Network group |
| TGNetPlayer | (internal C++ class — no SWIG binding) | Network player |
| TGPlayerList | (internal C++ class — no SWIG binding) | Player list |
| TGGroupPlayer | (internal C++ class — no SWIG binding) | Group-player association |
| TGEncrypt | (internal C++ class — no SWIG binding) | Encryption (AlbyRules cipher) |

---

## Game-Specific Classes (sampled, ~420 catalogued)

These are Bridge Commander's own classes, built on top of the TG framework and NetImmerse.
Organized by game subsystem. Spot-checks confirmed canonical anchors for ShipClass,
ShipSubsystem, MultiplayerGame, and DamageableObject (representative samples). **Full
enumeration of all ~420 game-specific class strings is deferred** — surface as
documentation debt; per-subsystem v5 passes will retire the remaining rows.

### Ship / Vessel Classes (28 unique)
| Address | Class |
|---------|-------|
| 0x008D8AC0 | ShipClass |
| 0x008E52F0 | ShipSubsystem |
| 0x008E4EC0 | HullClass |
| 0x008E42C8 | Cloak |
| 0x008E4E24 | CloakingSubsystem |
| 0x008E4EEC | ImpulseEngineSubsystem |
| 0x008E5330 | WarpEngineSubsystem |
| 0x008E61A8 | InSystemWarp |
| 0x008E42D4 | Tractor |
| 0x008E56BC | TractorBeamProjector |
| 0x008E5704 | TractorBeamSystem |
| 0x008E1074 | TractorBeamGraphic |

### Ship Properties (data-driven configuration)
| Address | Class |
|---------|-------|
| 0x00959440 | ShipProperty |
| 0x00958808 | HullProperty |
| 0x00958844 | ImpulseEngineProperty |
| 0x00959910 | WarpEngineProperty |
| 0x00958580 | CloakingSubsystemProperty |
| 0x00959874 | TractorBeamProperty |

### Weapon Classes
| Address | Class |
|---------|-------|
| 0x008E57C8 | Weapon |
| 0x008E539C | EnergyWeapon |
| 0x008E53E4 | PhaserBank |
| 0x008E5410 | PhaserSystem |
| 0x008E54FC | PulseWeapon |
| 0x008E5560 | PulseWeaponSystem |
| 0x008E55D4 | Torpedo |
| 0x008E562C | TorpedoSystem |
| 0x008E5690 | TorpedoTube |
| 0x008D9D4C | WeaponSystem |

### Weapon Properties
| Address | Class |
|---------|-------|
| 0x00959960 | WeaponProperty |
| 0x0095861C | EnergyWeaponProperty |
| 0x009589D0 | PhaserProperty |
| 0x00958FAC | PulseWeaponProperty |
| 0x009596AC | TorpedoSystemProperty |
| 0x00959764 | TorpedoTubeProperty |
| 0x00959A68 | WeaponSystemProperty |

### Subsystem / Damage Classes
| Address | Class |
|---------|-------|
| 0x00959590 | SubsystemProperty |
| 0x008E5CE0 | DamageableObject |
| 0x008DA2E4 | PowerSubsystem |
| 0x008E4F3C | PoweredSubsystem |
| 0x008E4FA0 | RepairSubsystem |
| 0x008E50F8 | SensorSubsystem |
| 0x008E52A0 | ShieldClass |
| 0x00958ED0 | PowerProperty |
| 0x00958E50 | PoweredSubsystemProperty |
| 0x0095902C | RepairSubsystemProperty |
| 0x009590C0 | SensorProperty |
| 0x00959138 | ShieldProperty |

### Multiplayer / Network
| Address | Class |
|---------|-------|
| 0x008DA714 | MultiplayerGame |
| 0x008E1664 | MultiplayerWindow |
| 0x008E1720 | MultiplayerInterfaceHandlers |
| 0x0095A354 | InitNetwork |
| 0x0095A390 | NetFile |
| 0x0095A30C | Network |
| 0x0095C798 | Message |
| 0x008D9AA8 | SkipChecksum |
| 0x0095A434 | SystemChecksumFail |
| 0x008DA74C | ServerListEvent |
| 0x008DA784 | SortServerListEvent |

### Object System
| Address | Class |
|---------|-------|
| 0x008D8BEC | ObjectClass |
| 0x008D9750 | BaseObjectClass |
| 0x008D967C | CameraObjectClass |
| 0x008DA0E0 | ChatObjectClass |
| 0x008D9788 | LightObjectClass |
| 0x008E5E40 | PhysicsObjectClass |
| 0x0095826C | ZoomCameraObjectClass |
| 0x008E5884 | CollisionEvent |

### Mission / Set System
| Address | Class |
|---------|-------|
| 0x008D89F0 | Mission |
| 0x008D867C | MissionLib |
| 0x008D8B90 | SetClass |
| 0x008D9D80 | SetInstance |
| 0x008D8D40 | SetManager |
| 0x00957144 | BridgeSet |
| 0x008E136C | System |
| 0x008D87D0 | Game |
| 0x008E19A0 | GameInit |
| 0x00959BFC | GameSpy |

### Space Objects
| Address | Class |
|---------|-------|
| 0x008DA35C | Planet |
| 0x008DA31C | Nebula |
| 0x008D9D04 | MetaNebula |
| 0x008DA37C | Sun |
| 0x008D8FB0 | Asteroid |
| 0x008D8D94 | AsteroidField |
| 0x008D8E3C | AsteroidTile |
| 0x008E5884 | Backdrop |
| 0x008E59A4 | BackdropSphere |
| 0x008E5BB0 | StarSphere |
| 0x008DA3C8 | Waypoint |

### AI System
| Address | Class |
|---------|-------|
| 0x008D9EFC | ArtificialIntelligence |
| 0x008D9CE4 | BuilderAI |
| 0x008D9E48 | ConditionalAI |
| 0x008D9E84 | PlainAI |
| 0x008D9E20 | PreprocessingAI |
| 0x008DBD34 | RandomAI |
| 0x008DBDC8 | SequenceAI |
| 0x008DBC4C | PriorityListAI |

### Character / Bridge
| Address | Class |
|---------|-------|
| 0x00957308 | Captain |
| 0x00957178 | CharacterClass |
| 0x0095702C | BridgeObjectClass |
| 0x008DA5E4 | CharacterAction |
| 0x008DA594 | CharacterSpeakingQueue |

### UI Windows (Game-Specific)
| Address | Class |
|---------|-------|
| 0x008E21DC | TopWindow |
| 0x008E24F4 | MainWindow |
| 0x008E1118 | BridgeWindow |
| 0x008E12AC | CinematicWindow |
| 0x008E2530 | ConsoleWindow |
| 0x008E1CA4 | SubtitleWindow |
| 0x008E202C | TacticalControlWindow |
| 0x008E2134 | TacticalWindow |
| 0x008E2208 | OptionsWindow |
| 0x008DA118 | MapWindow |
| 0x008E14C4 | ModalDialogWindow |
| 0x008E1508 | StylizedWindow |
| 0x008DA6CC | ReticleManagerWindow |
| 0x008E2760 | ReticleWindow |
| 0x008E26A4 | PlayerReticleWindow |
| 0x008E263C | NamedReticleWindow |
| 0x008E11A0 | CDCheckWindow |
| 0x008E4774 | GraphicsMenu |

### UI Controls (Game-Specific ST* prefix)
| Address | Class |
|---------|-------|
| 0x008E282C | STButton |
| 0x008E28C0 | STCheckbox |
| 0x008E2860 | STCharacterMenu |
| 0x008E37F8 | STComponentMenu |
| 0x008E387C | STComponentMenuItem |
| 0x008E2A3C | STFileDialog |
| 0x008E2E30 | STFileMenu |
| 0x008E2ED4 | STLoadDialog |
| 0x008E3048 | STMenu |
| 0x008E3198 | STMissionLog |
| 0x008E32B8 | STRepairButton |
| 0x008E3358 | STRoundedButton |
| 0x008E33C4 | STSaveDialog |
| 0x008D9D24 | STStylizedWindow |
| 0x008E365C | STSubPane |
| 0x008E373C | STSubsystemMenu |
| 0x008E39E8 | STTargetMenu |
| 0x008E3A74 | STTargetMenuSubPane |
| 0x008E3AB8 | STTiledIcon |
| 0x008E3A18 | STTopLevelMenu |
| 0x008E3AE4 | STToggle |
| 0x008E2EA8 | STFillGauge |
| 0x008DA144 | STNumericBar |
| 0x008E3BAC | STWarpButton |
| 0x008E2BFC | UIHelpers |

### Display Panels
| Address | Class |
|---------|-------|
| 0x008E404C | ShipDisplay |
| 0x008E43FC | WeaponsDisplay |
| 0x008E3CF0 | ShipIcons |
| 0x008E3FA4 | ShieldsDisplay |
| 0x008E3CFC | DamageDisplay |
| 0x008E3DE8 | RadarDisplay |
| 0x008E3ED4 | RadarScope |
| 0x008E3E4C | RadarBlip |
| 0x008E3C90 | DamageIcon |
| 0x008E4640 | EngPowerDisplay |
| 0x008E46F8 | EngRepairPane |
| 0x008E4520 | EngPowerCtrl |
| 0x008E41A0 | TacWeaponsCtrl |
| 0x008E4190 | LeftSeparator |

### Camera Modes
| Address | Class |
|---------|-------|
| 0x008D9010 | CameraMode |
| 0x008D9178 | ChaseCameraMode |
| 0x008D90BC | IdealControlledCameraMode |
| 0x008D94B4 | LockedPositionMode |
| 0x008D92C0 | MapCameraMode |
| 0x008D924C | TargetCameraMode |
| 0x008D95B8 | TorpCameraMode |
| 0x008D9288 | ZoomTargetMode |
| 0x008D9634 | PlaceByDirectionMode |
| 0x008D9444 | PlacementWatchMode |
| 0x008D93E0 | DropAndWatchMode |
| 0x008D96F8 | SpaceCamera |

### Effects / Particles
| Address | Class |
|---------|-------|
| 0x008E0D30 | EffectController |
| 0x008E0D18 | EffectControllerData |
| 0x008E0CDC | AnimTSParticleController |
| 0x008E0CF8 | DebrisParticleController |
| 0x008E0D58 | ExplodeParticleController |
| 0x008E0D74 | PointParticleController |
| 0x008E0D8C | SparkParticleController |
| 0x008E0DA4 | TexturedSparksController |
| 0x008E0F04 | AnimatedTriShapeParticles |
| 0x008E10FC | TriShapeOrientedParticles |
| 0x008E10C8 | TriShapeParticles |
| 0x008E10B0 | TriShapeParticlesData |
| 0x008E10DC | TriShapeOrientedParticlesData |
| 0x008E1050 | FlareController |
| 0x008E1040 | SpecularPass |
| 0x008E0FD4 | GlowPass |
| 0x008E0FE0 | PhaserGraphic |
| 0x008E0F58 | DisruptorGraphic |
| 0x008E1064 | TorpedoGraphic |

### Properties (Game Object Configuration)
| Address | Class |
|---------|-------|
| 0x009582AC | BlinkingLightProperty |
| 0x009583D0 | EffectEmitterProperty |
| 0x0095842C | EngineGlowProperty |
| 0x00958790 | EngineProperty |
| 0x0095847C | ExplodeEmitterProperty |
| 0x009584D8 | SmokeEmitterProperty |
| 0x0095852C | SparkEmitterProperty |
| 0x00958920 | ObjectEmitterProperty |
| 0x00958D24 | PositionOrientationProperty |
| 0x00958604 | DisplayModelExtraData |
| 0x009580A0 | SetLocation |
| 0x00958148 | RotateBonesController |
| 0x00956F90 | BoneStateController |
| 0x009581F0 | ViewScreenObject |

### Warp System
| Address | Class |
|---------|-------|
| 0x008DA2B8 | WarpEvent |
| 0x008DA538 | WarpFlash |
| 0x008DA564 | WarpSequence |
| 0x008E0E98 | WarpSet |
| 0x008E0DDC | WarpFlashTextures |

### Proximity / Placement
| Address | Class |
|---------|-------|
| 0x008DA1C4 | ProximityCheck |
| 0x008DA1FC | ProximityEvent |
| 0x008DA390 | PlacementObject |
| 0x008DA3EC | LightPlacement |
| 0x008DA4B8 | AsteroidFieldPlacement |

### Editor
| Address | Class |
|---------|-------|
| 0x008DA424 | Editor |
| 0x008DA444 | PlacementEditor |
| 0x008DA47C | BackgroundEditor |
| 0x008DC2C4 | EditorCamera |
| 0x008DC2D4 | GridClass |

### Scoring / Game Events
| Address | Class |
|---------|-------|
| 0x008E62D0 | WeaponHitEvent |
| 0x008DA270 | ObjectExplodingEvent |
| 0x008DA234 | StartFiringEvent |
| 0x008DA61C | WaypointEvent |
| 0x008DA5E4 | CharacterAction |
| 0x008DA0A8 | VarManagerClass |
| 0x008DA67C | ConditionEventCreator |

---

## SWIG Python Binding Statistics

The SWIG 1.x binding layer exposes C++ classes to Python 1.5.2 via the `App` and `Appc`
modules. Each class has wrapper functions named `ClassName_MethodName`.

> [!NOTE]
> The "method count" column in this section equals the number of `^ClassName_` prefix strings
> in the binary, which includes **both bound methods AND enum/constant identifiers** (e.g.,
> `TGSound_SS_PLAYING`, `TGUIObject_ALIGN_BR`). Actual bound-method counts are typically 3-10
> lower per class. Read the aggregate "~1,340 wrapper methods" as **"~1,340 SWIG-bound Python
> identifiers (methods + constants)"** until per-class verification is done. Carries
> `confidence: low` in the evidence header pending a v5 SWIG-table walk.

### Largest SWIG Interfaces (by identifier count, not method count)
| Class | Identifiers | Role |
|-------|-------------|------|
| TGUIObject | 94 | UI object (largest binding) |
| TGSound | 63 | Sound system |
| TGMessage | 53 | Network messages |
| TGNetwork | 50 | Network abstraction |
| TGInputManager | 41 | Input handling |
| TGMatrix3 | 38 | Matrix math (note: `TGMatrix3` itself is not bare-anchored — see debt list) |
| TGBufferStream | 35 | Stream I/O |
| TGPoint3 | 35 | 3D vector math |
| TGParagraph | 34 | Text rendering |
| TGSoundManager | 33 | Sound management |
| TGDialogWindow | 28 | Dialogs |
| TGPane | 26 | UI panes |
| TGINPUT | 25 | Input constants |
| TGRect | 24 | Rectangle math (note: `TGRect` itself is not bare-anchored — see debt list) |
| TGIconManager | 22 | Icon management |
| TGIconGroup | 21 | Icon groups |
| TGColorA | 21 | RGBA color (note: `TGColorA` itself is not bare-anchored — see debt list) |
| TGEvent | 21 | Events |
| TGRootPane | 21 | Root UI |
| TGTextButton | 19 | Text buttons |
| TGModelPropertyManager | 18 | Model properties |
| TGNETWORK | 18 | Network constants |
| TGFontGroup | 17 | Font groups |
| TGFrame | 17 | Frames |
| TGModelManager | 17 | Model management |
| TGSystemWrapperClass | 17 | System wrapper |
| TGUITheme | 16 | UI themes |
| TGNetPlayer | 16 | Network players |
| TGMouseEvent | 15 | Mouse input |
| TGAnimNode | 14 | Animation |
| TGAnimationManagerClass | 13 | Animation manager |
| TGIcon | 12 | Icons |
| TGRedbookClass | 12 | CD audio |

### Total: ~70 SWIG-bound TG classes with bare-string anchors, ~1,340 SWIG-bound Python identifiers

---

## Summary Statistics

| Category | Count | Note |
|----------|-------|------|
| MSVC RTTI `_TypeDescriptor` (CRT/STL) | 21 | All in 0x00979A18-0x00979E98 |
| MSVC RTTI throw-types (`.PAV`) | 1 | TGStreamException at 0x0095AD10 |
| NetImmerse Ni* classes (catalogued) | 129 | 117 factory-registered; full enumeration deferred |
| TG Framework classes (bare-string anchored) | ~70 | 28 confirmed (re-anchored 2026-05-28) + 41 newly-discovered |
| TG Framework classes (internal C++, no SWIG) | ~15 | Anchored via factory ID / vtable, not bare string |
| Game-specific classes (sampled) | ~420 | Spot-checked; full enumeration deferred |
| **Total unique C++ classes (estimated)** | **~615** | Prior 670 inflated by ~34 fictional TG rows + uncertainty in NI/game counts |
| TG SWIG-bound classes | ~70 | Was "114"; reduced after dropping speculative rows |
| TG SWIG-bound Python identifiers | ~1,340 | Includes both methods AND enum/constant identifiers |

> [!NOTE]
> Counts marked "deferred" / "sampled" / "estimated" reflect documentation debt: per-subsystem
> v5 passes will retire these. The TG section is the densest verification work for this pass;
> NI vtable validation will pin the 129 NI count, and game-specific subsystem passes will pin
> the ~420 game count.
