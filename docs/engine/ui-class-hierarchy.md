> [docs](../README.md) / [engine](README.md) / ui-class-hierarchy.md

---
title: UI Class Hierarchy
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
  - claim: "TopWindow constructor at 0x0050c430 allocates 5 children and stores `this` at global 0x009878cc"
    address: 0x0050c430
    function: FUN_0050c430
    confidence: high
    note: "Singleton write at 0x0050c485 (`DAT_009878cc = param_1`). The prior doc + CLAUDE.md said TopWindow lived at 0x0097e238; that is wrong. See [TopWindow vs PlayWindow Globals](#topwindow-vs-playwindow-globals)."
  - claim: "TopWindow::FindMainWindow at 0x0050e1b0 selects a child by RTTI IsA(0x810F) + type-ID match at +0x4C"
    address: 0x0050e1b0
    function: FUN_0050e1b0
    confidence: high
    note: "Calls child vtable slot 2 (IsA) with 0x810F (MainWindow RTTI type), then compares `*(int*)(child + 0x4C)` against the requested type-ID."
  - claim: "MainWindow base ctor FUN_0050e920(this, typeID, w, h) writes typeID at +0x4C"
    address: 0x0050e920
    function: FUN_0050e920
    confidence: high
    note: "Every MainWindow subclass ctor calls this base ctor with its own type-ID as param_2. Walking the xrefs gives the full subclass catalog (12 entries — see below)."
  - claim: "PlayWindow ctor at 0x00405c10 stores `this` at global 0x0097e238 (Game state object, NOT a TopWindow child)"
    address: 0x00405c10
    function: FUN_00405c10
    confidence: high
    note: "Singleton write at 0x00405c8d (`DAT_0097e238 = param_1`). PlayWindow does NOT call FUN_0050e920 (MainWindow base ctor) — it has no MainWindow type-ID. Vtable 0x008887e8."
  - claim: "MultiplayerGame ctor FUN_0069e590 extends PlayWindow with playerSlots[16] at +0x74, readyForNewPlayers byte at +0x1F8, maxPlayers dword at +0x1FC"
    address: 0x0069e590
    function: FUN_0069e590
    confidence: high
    note: "Called from GameInit FUN_00504f10 with 0x200-byte allocation. Vtable 0x0088b480 overrides PlayWindow's 0x008887e8. Array init helper FUN_00859d64(this+0x1d, 0x18, 0x10, ...) anchors the +0x74 offset (0x1d*4); `MOV byte ptr [EBP+0x1f8], 0x0` at 0x0069eaf1 confirms +0x1F8 is a BYTE. Internal consistency: +0x74 + 0x18*16 = +0x1F4; +0x1F8 byte + 3 pad + +0x1FC dword = +0x200."
  - claim: "TGUIObject ctor FUN_0072dcc0 (parent FUN_0072fc20) writes initial flag value 0x08 (visible) at +0x28"
    address: 0x0072dcc0
    function: FUN_0072dcc0
    confidence: high
    note: "Parent ctor at FUN_0072fc20: `param_1[5] = 0` (+0x14 parent = NULL), `param_1[10] = 8` (+0x28 flags = 0x08), `param_1[0xb] = 0` (+0x2C callbacks = NULL). TGUIObject ctor itself zeroes +0x18, +0x1C (bounds.x, bounds.y) and writes 2 at +0x44."
  - claim: "Flag bit 0x10000000 (layout-in-progress guard) set/cleared in FUN_00732120"
    address: 0x00732120
    function: FUN_00732120
    confidence: high
    note: "TGParagraph recalc guard: `param_1[10] |= 0x10000000` then later `&= 0xefffffff`. Prevents reentrant layout passes."
  - claim: "MainWindow RTTI type ID = 0x810F"
    address: 0x0050e1b0
    function: FUN_0050e1b0
    confidence: high
    note: "Derived from FindMainWindow's IsA call: `vtable[2](child, 0x810F)`. Every MainWindow subclass writes 0x810F into its RTTI stub at slot 2."
  - claim: "TopWindow handler-registration site FUN_0050ca50 calls FUN_006d92b0(table, eventID, handlerName) for all 18 top-level event IDs"
    address: 0x0050ca50
    function: FUN_0050ca50
    confidence: high
    note: "Each call passes a string-literal handler name (e.g., 'TopWindow::MouseHandler', 'OptionsWindow::QuitHandler'). Cross-link: each registered handler anchors its event ID by name."
  - claim: "Event ID 0x30001 = TopWindow::MouseHandler"
    address: 0x0050ca50
    function: FUN_0050ca50
    confidence: high
  - claim: "Event ID 0x30002 = TopWindow::KeyboardHandler"
    address: 0x0050ca50
    function: FUN_0050ca50
    confidence: high
  - claim: "Event IDs 0x800002 / 0x800005 / 0x800006 / 0x800007 / 0x8000c6 = OptionsWindow Quit/NewGame/LoadGame/SaveGame/NewMultiplayerGame"
    address: 0x0050ca50
    function: FUN_0050ca50
    confidence: high
  - claim: "Event IDs 0x8000b7 / 0x8000b8 / 0x8000b9 / 0x8000ba = ResolutionChange family (4 events, not 3 as prior doc had)"
    address: 0x0050ca50
    function: FUN_0050ca50
    confidence: high
    note: "0x8000b9 (ResolutionChangeBackHandler) was missing from the prior doc. Two of the four event IDs reuse the same handler name (ResolutionChangeHandler at 0x8000b7 and 0x8000ba; ResolutionChangeBackHandler at 0x8000b8 and 0x8000b9)."
  - claim: "Event ID 0x8001dd = SelfDestruct"
    address: 0x0050ca50
    function: FUN_0050ca50
    confidence: high
    note: "Handler name string 'TopWindow::SelfDestructHandler'. Cross-link: docs/gameplay/self-destruct-pipeline.md."
  - claim: "Event IDs 0x800494 / 0x800495 / 0x800496 / 0x800497 / 0x800498 = ToggleConsole/ToggleOptions/TabFocus/PrintScreen/ToggleBridgeAndTactical"
    address: 0x0050ca50
    function: FUN_0050ca50
    confidence: high
  - claim: "Event ID 0x8003cc = ToggleEdit"
    address: 0x0050ca50
    function: FUN_0050ca50
    confidence: high
  - claim: "MainWindow type-ID catalog has 12 distinct entries (types 0-10) — expanded from prior doc's 8"
    address: 0x0050e920
    function: FUN_0050e920
    confidence: high
    note: "Found by exhaustive xref sweep on FUN_0050e920. NEW vs prior doc: type 3 (vtable 0x0088aa3c), type 4 (vtable 0x0088ec9c), type 6 MapWindow (vtable 0x00889c4c). REVISED: type 5 ctor is FUN_00507900 (not FUN_00405c10 as prior doc had — PlayWindow at 0x00405c10 is not a MainWindow); type 7 is 'SortedRegionMenu' (SWIG string lacks 'Window' suffix)."
  - claim: "TopWindow's 5 children are MainWindow type IDs {4, 2, 8, 9, 10} — NOT {0, 2, 5, 8, 10} as prior doc had"
    address: 0x0050c430
    function: FUN_0050c430
    confidence: high
    note: "Inspection of the 5 child allocations in TopWindow ctor yields sizes/vtables/type-IDs: 0x6c/0x0088ec9c/4 (unnamed, inline), 0x50/0x0088f098/2 (ConsoleWindow, FUN_0050ebc0), 0xb8/0x0088e74c/8 (MultiplayerWindow, FUN_00504390), 0x5c/0x0088e344/9 (PlayViewWindow inferred), 0x64/0x0088e5fc/10 (CinematicWindow, FUN_005023c0)."
  - claim: "STWidget / STRadioGroup / TGScrollablePane have no binary string anchors"
    address: null
    function: null
    confidence: high
    note: "search_strings exhaustive sweep finds zero matches for 'STWidget' or 'STRadioGroup' as bare class names anywhere in the binary. 'TGScrollablePane' has no SWIG string. STButton, STToggle, TGUIObject, TGPane, TGConsole, TGWindow, TGIcon, TGParagraph, TGRootPane, TGDialogWindow all DO have SWIG strings. STWidget and STRadioGroup are dropped as unverified RE inferences; TGScrollablePane is demoted to medium confidence (may exist as internal C++ class with no Python binding)."
  - claim: "RTTI type 0x80EA exists as a class GetTypeID return value at vtable 0x00890ac4 — but the class identity is NOT STRadioGroup"
    address: 0x00890ac4
    function: FUN_00532f50
    confidence: high
    note: "Vtable 0x00890ac4 slot 1 returns 0x80EA. The class at this vtable has ctor FUN_00532f50. Prior doc labeled this 'STRadioGroup' — that string does not exist in the binary. Closest SWIG match is STSubPane (which exposes an `IsRadioGroup` property, suggesting the radio-group concept is a STSubPane feature, not a separate class)."
  - claim: "RTTI type 0x205 is a class GetTypeID return value at vtable 0x00897270 — but the class is NOT TGConsole"
    address: 0x00897270
    function: null
    confidence: medium
    note: "TGConsole's actual vtable is at 0x00897294 (different address). 0x205 may be a parent class of TGConsole (e.g., TGTextBlock — which also has no SWIG string). Doc retains the type ID at medium confidence pending chain-walking to identify the class."
  - claim: "TGL resource files Multiplayer.tgl + Options.tgl exist as string constants in the binary"
    address: 0x008e1900
    function: null
    confidence: high
    note: "Multiplayer.tgl string at 0x008e1900, Options.TGL string at 0x008e1390. The binary contains 12 TGL files total; the doc lists only these two as load-bearing for the UI subsystem."
companions:
  - docs/engine/event-system-architecture.md
  - docs/engine/tg-hierarchy-vtables.md
  - docs/engine/function-map.md
  - docs/engine/rtti-class-catalog.md
  - docs/engine/v5-validation-status.md
supersedes:
  - 2026-02-24
---

> [!NOTE]
> This doc is `status: partial`. The TopWindow constructor + children catalog, MainWindow type IDs (12 entries), event ID registrations (anchored at FUN_0050ca50), TGUIObject layout + flag bits, MultiplayerGame field layout, and TGL resource files are v5-validated against the current Ghidra import (2026-05-28). The prior doc's most load-bearing error — conflating TopWindow (`0x009878cc`) with PlayWindow (`0x0097e238`) — has been corrected; this also affects CLAUDE.md's Key Globals table (correction batched for engine-family-close). The prior doc's MainWindow type-ID catalog (8 entries) is expanded to 12 entries; types 3, 4, and 6 are new, types 5 and 7 are revised. The class names `STWidget` and `STRadioGroup` and the TGScrollablePane certainty have been dropped or demoted because they have no binary string anchors. See [docs/guides/v5-evidence-header.md](../guides/v5-evidence-header.md) for the standard.

# UI Class Hierarchy

Reverse-engineered from `stbc.exe` vtable analysis, constructor chains, SWIG wrapper tracing, and exhaustive xref sweeps. The UI subsystem layers TGUIObject (TGEventHandlerObject subclass) below MainWindow (the full-screen view base) below the per-mode MainWindow subclasses (Bridge, Tactical, Multiplayer, etc.). TopWindow is the root scene/window container that owns the linked list of MainWindow children.

## TopWindow vs PlayWindow Globals

There are **two distinct globals**, and the prior doc + CLAUDE.md conflated them. Disambiguating these is the most important fact in this doc.

| Global | Class | Created by | Singleton write | Role |
|--------|-------|------------|-----------------|------|
| `0x009878cc` | TopWindow | `FUN_0050c430` | `DAT_009878cc = param_1` at `0x0050c485` | Root scene/window container. Owns the 5 children visited by FindMainWindow. Vtable governs window-system layout, focus, and input routing. |
| `0x0097e238` | PlayWindow | `FUN_00405c10` | `DAT_0097e238 = param_1` at `0x00405c8d` | Game state object (score, rating, kills, playerShip, godMode, terminateEvent, currentEpisode). MultiplayerGame extends this (vtable `0x008887e8` → `0x0088b480`). |

**Key consequence:** PlayWindow is **NOT** a MainWindow — it never calls the MainWindow base ctor `FUN_0050e920` and has no type-ID at `+0x4C`. It is a standalone TGEventHandlerObject-derived class. The prior doc's claim that PlayWindow is "Type ID 5, a TopWindow child" is wrong; type ID 5's actual ctor is `FUN_00507900` (a different unnamed class — see [MainWindow Type IDs](#mainwindow-type-ids) below).

CLAUDE.md's Key Globals row "`0x0097e238 TopWindow/MultiplayerGame ptr`" needs the same correction — it should be "`0x0097e238 PlayWindow / Game state ptr`" with a new row added for `0x009878cc TopWindow (root scene container)`. Batched to engine-family-close.

## Inheritance Tree

```
TGEventHandlerObject (event dispatch base)
  -> TGUIObject (UI element base: bounds, visibility, parent link)
       -> TGPane (child container: linked list of children, rendering)
            -> TGTextBlock [confidence: medium] (console/chat text — no SWIG string; aliased as `TGConsole` in the SWIG API)
                 -> [internal scroll-capable text container]
            -> TGWindow (default child tracking, focus management)
            -> [internal widget chain] (no SWIG string for the abstract intermediate)
                 -> STButton (text, colors, states, click handling)
                      -> STToggle (4-state toggle: values at +0x124, events at +0x164)
            -> TGIcon (sprite rendering: icon group, poly, RGBA color)
            -> TGParagraph (rich text: cursor, word wrap, layout)
            -> TGRootPane (top-level: cursor stack, tooltip, focus tracking)
            -> TGDialogWindow (modal dialog with button bar — see [TGDialogWindow Button System](#tgdialogwindow-button-system))
```

Two classes the prior doc placed in this tree have **no binary string anchor**:

- **STWidget** (as the abstract base above STButton/STToggle) — no occurrence in the binary's string table. May exist as an internal C++ class with no SWIG binding, or may be RE inference. Replaced by "internal widget chain" placeholder above.
- **TGScrollablePane** (between TGPane and TGTextBlock) — no SWIG string. Demoted to `confidence: medium`; the position in the tree is plausible from behaviour but unverified.

Both **STButton** and **STToggle** have SWIG strings and are anchored; only the abstract intermediate is unverified.

## TGUIObject Layout

`FUN_0072dcc0` ctor (parent `FUN_0072fc20`).

| Offset | Type | Field | Initial value | Notes |
|--------|------|-------|---------------|-------|
| +0x14 | TGPane* | parent | NULL | Set by parent ctor `param_1[5] = 0` |
| +0x18 | int | bounds.x | 0 | |
| +0x1C | int | bounds.y | 0 | |
| +0x28 | uint32 | flags | 0x08 (visible) | Set by parent ctor `param_1[10] = 8` |
| +0x2C | void* | callbacks | NULL | Set by parent ctor `param_1[0xb] = 0` |
| +0x44 | int | (default) | 2 | Meaning unverified |

### Flag Bits (+0x28)

| Bit | Meaning | Anchor |
|-----|---------|--------|
| 0x08 | Visible | Initial value set by TGUIObject ctor at FUN_0072fc20 [v5-validated] |
| 0x20 | Skip parent in rendering chain | (carried from prior doc — not separately re-anchored) |
| 0x40 | Exclusive keyboard focus | (carried from prior doc) |
| 0x80 | Dirty (needs repaint) | (carried from prior doc) |
| 0x100 | Hidden | (carried from prior doc) |
| 0x200 | Disabled | (carried from prior doc) |
| 0x10000000 | Layout in progress (TGParagraph recalc guard) | Set/cleared at FUN_00732120 [v5-validated] |

## MainWindow Type IDs

`MainWindow` is the abstract base class for every full-screen game view. The base ctor `FUN_0050e920(this, typeID, w, h)` writes the type ID into `this+0x4C` and sets up the MainWindow RTTI tag (`0x810F`). `TopWindow::FindMainWindow` (`FUN_0050e1b0`) iterates TopWindow's child list, calls each child's `IsA(0x810F)` (vtable slot 2) to filter for MainWindows, then matches `*(int*)(child+0x4C) == typeID`.

The complete catalog is derived by walking every xref to `FUN_0050e920` — each subclass ctor passes its type-ID as `param_2`. Twelve distinct subclasses exist:

| Type ID | Class | Constructor | Vtable | SWIG-confirmed? |
|---------|-------|-------------|--------|-----------------|
| 0 | BridgeWindow | FUN_004fb750 | 0x0088e1f4 | yes |
| 1 | TacticalWindow | FUN_0050b290 | 0x0088eb48 | yes |
| 2 | ConsoleWindow | FUN_0050ebc0 | 0x0088f098 | yes |
| 3 | (unknown class) | FUN_00496a60 | 0x0088aa3c | no — class identity is an open question |
| 4 | (unknown class) | TopWindow inline + FUN_00622300 | 0x0088ec9c | no — class identity is an open question |
| 5 | (unknown class — possibly HUD/LCARS_640) | FUN_00507900 | 0x0088e8a0 | no — uses "LCARS_640" font; not PlayWindow |
| 6 | MapWindow | FUN_004fe560 | 0x00889c4c | yes (SWIG string `MapWindow::*`) |
| 7 | SortedRegionMenu | FUN_004fd6f0 | 0x0088e494 | yes — SWIG string `SortedRegionMenu` (NOT `SortedRegionMenuWindow` as prior doc had — no "Window" suffix) |
| 8 | MultiplayerWindow | FUN_00504390 | 0x0088e74c | yes |
| 9 | PlayViewWindow | FUN_004fc480 | 0x0088e344 | inferred — no direct SWIG string, but is one of TopWindow's 5 children |
| 10 | CinematicWindow | FUN_005023c0 | 0x0088e5fc | yes |

**Changes from prior doc:**

- **New:** types 3, 4, 6 (MapWindow). The prior doc had only types {0, 1, 2, 5, 7, 8, 9, 10}.
- **Revised:** type 5's ctor is `FUN_00507900`, not `FUN_00405c10` as prior doc had. `FUN_00405c10` is PlayWindow (a different class — see [TopWindow vs PlayWindow Globals](#topwindow-vs-playwindow-globals)).
- **Revised:** type 7 is `SortedRegionMenu`, not `SortedRegionMenuWindow`. SWIG string lacks the "Window" suffix.

Types 3, 4, and 5 lack SWIG string anchors for their class identities — listed as open questions.

### TopWindow Children

`TopWindow::TopWindow` (`FUN_0050c430`) allocates 5 children directly. Each child carries a MainWindow type-ID at `+0x4C`. Actual types and sizes:

| Slot | Size | Type ID | Vtable | Class | Ctor |
|------|------|---------|--------|-------|------|
| 0 | 0x6c | 4 | 0x0088ec9c | (unnamed) | inline in TopWindow ctor |
| 1 | 0x50 | 2 | 0x0088f098 | ConsoleWindow | FUN_0050ebc0 |
| 2 | 0xb8 | 8 | 0x0088e74c | MultiplayerWindow | FUN_00504390 |
| 3 | 0x5c | 9 | 0x0088e344 | PlayViewWindow (inferred) | FUN_004fc480 |
| 4 | 0x64 | 10 | 0x0088e5fc | CinematicWindow | FUN_005023c0 |

**This contradicts the prior doc**, which listed the 5 children as types {0, 2, 5, 8, 10} including BridgeWindow and PlayWindow. The actual set is {4, 2, 8, 9, 10}: an unnamed type-4 class instead of BridgeWindow, and PlayViewWindow (type 9) instead of "PlayWindow" (type 5). BridgeWindow exists as a MainWindow subclass (type 0) but isn't a TopWindow child — it's allocated elsewhere (mode-dependent). PlayWindow (the Game state object at `0x0097e238`) was never a child to begin with.

## PlayWindow (Game State Object)

PlayWindow is **not** a MainWindow. It's a standalone TGEventHandlerObject-derived class that holds game state. The class is exposed to Python as the `Game` SWIG object.

| Anchor | Value |
|--------|-------|
| Constructor | FUN_00405c10 |
| Singleton write | `DAT_0097e238 = param_1` at 0x00405c8d |
| Vtable | 0x008887e8 |
| Field zero-init helper | FUN_00405ad0 (called from ctor) |

### PlayWindow layout

Offsets anchored by `FUN_00405ad0` (the zero-init helper called from the ctor). Field semantic names (e.g., "score", "rating") are carried from prior RE inference and are plausible from context, but the names themselves are not separately anchored — only the offsets are.

| Offset | Type | Field (inferred) | Anchored as |
|--------|------|------------------|-------------|
| +0x38 | int | score | dword in FUN_00405ad0 zero-init [offset confirmed] |
| +0x3C | int | rating | dword in FUN_00405ad0 zero-init [offset confirmed] |
| +0x40 | int | kills | dword in FUN_00405ad0 zero-init [offset confirmed] |
| +0x44 | int | (unverified) | dword in FUN_00405ad0 zero-init [offset confirmed] |
| +0x48 | int | (unverified) | dword in FUN_00405ad0 zero-init [offset confirmed] |
| +0x4C | int | (unverified) | dword in FUN_00405ad0 zero-init [offset confirmed] |
| +0x50 | int | (unverified) | dword in FUN_00405ad0 zero-init [offset confirmed] |
| +0x54 | Ship* | playerShip | dword in FUN_00405ad0 zero-init [offset confirmed] |
| +0x60 | byte | godMode | byte in FUN_00405ad0 zero-init [offset confirmed] |
| +0x61 | byte | (unverified) | byte in FUN_00405ad0 zero-init [offset confirmed] |
| +0x62 | byte | (unverified) | byte = 1 in FUN_00405ad0 zero-init [offset confirmed] |
| +0x64 | int | (unverified) | dword in FUN_00405ad0 zero-init [offset confirmed] |
| +0x68 | int | (unverified) | dword in FUN_00405ad0 zero-init [offset confirmed] |
| +0x6C | int | terminateEvent | dword in FUN_00405ad0 zero-init [offset confirmed] |
| +0x70 | Episode* | currentEpisode | dword in FUN_00405ad0 zero-init [offset confirmed] |

Note that `+0x70` is **occupied by PlayWindow**, which structurally forces MultiplayerGame's playerSlots array to start at `+0x74` — see next section.

### MultiplayerGame extends PlayWindow

`MultiplayerGame` is allocated as 0x200 bytes by GameInit `FUN_00504f10`, then constructed by `FUN_0069e590`. Its ctor calls into PlayWindow's ctor chain, then overrides the vtable from `0x008887e8` to `0x0088b480`, then writes its own extension fields.

| Offset | Type | Field | Anchor |
|--------|------|-------|--------|
| +0x74 | playerSlot[16] (stride 0x18) | playerSlots | Array init helper `FUN_00859d64(this+0x1d, 0x18, 0x10, ...)` — `this+0x1d` is `this + 0x1d*4 = this+0x74` |
| +0x1F8 | byte | readyForNewPlayers | `MOV byte ptr [EBP+0x1f8], 0x0` at 0x0069eaf1 |
| +0x1FC | dword | maxPlayers | `param_1[0x7f] = playerLimit` — 0x7f*4 = 0x1FC |

Internal consistency: `+0x74 + (16 * 0x18) = +0x1F4`, then `+0x1F8 byte + 3 pad + +0x1FC dword` = `+0x200` total — matches GameInit's 0x200-byte allocation exactly.

The prior doc's `+0x74` for playerSlots was correct. (An earlier internal RE memo claimed `+0x70`; that was wrong and the agent already corrected its own notes.)

## Event ID Catalog

`TopWindow::TopWindow` calls `FUN_0050ca50` immediately after allocating children. `FUN_0050ca50` calls `FUN_006d92b0(dispatchTable, eventID, handlerName)` once per event ID, registering each handler with a debug-name string. Each event ID is **anchored by name** via the string-literal handler argument.

For the event dispatch mechanism (TGEventManager, TGCallback, TGInstanceHandlerTable) see [event-system-architecture.md](event-system-architecture.md). The handler registration site `FUN_0050ca50` is the canonical anchor point for the TopWindow event IDs listed below.

### Input Events

| ID | Handler name string | Source |
|----|---------------------|--------|
| 0x30001 | `TopWindow::MouseHandler` | Input system [v5-validated at FUN_0050ca50] |
| 0x30002 | `TopWindow::KeyboardHandler` | Input system [v5-validated at FUN_0050ca50] |
| 0x30003 | Gamepad | (carried from prior doc — not separately anchored this pass) |
| 0x40001 | Control | (carried from prior doc) |

### UI Toggle Events

| ID | Handler name string | Notes |
|----|---------------------|-------|
| 0x800494 | `TopWindow::ToggleConsoleHandler` | [v5-validated] |
| 0x800495 | `TopWindow::ToggleOptionsHandler` | [v5-validated] |
| 0x800496 | `TopWindow::TabFocusHandler` | [v5-validated] |
| 0x800497 | `TopWindow::PrintScreenHandler` | [v5-validated] |
| 0x800498 | `TopWindow::ToggleBridgeAndTacticalHandler` | [v5-validated] |
| 0x8003CC | `TopWindow::ToggleEditHandler` | [v5-validated] |
| 0x8001DD | `TopWindow::SelfDestructHandler` | [v5-validated] — cross-link: [docs/gameplay/self-destruct-pipeline.md](../gameplay/self-destruct-pipeline.md) |

### Game Flow Events

| ID | Handler name string | Notes |
|----|---------------------|-------|
| 0x800002 | `OptionsWindow::QuitHandler` | [v5-validated] |
| 0x800005 | `OptionsWindow::NewGameHandler` | [v5-validated] |
| 0x800006 | `OptionsWindow::LoadGameHandler` | [v5-validated] |
| 0x800007 | `OptionsWindow::SaveGameHandler` | [v5-validated] |
| 0x8000C6 | `OptionsWindow::NewMultiplayerGame` | [v5-validated] |
| 0x8000F0 | MissionSelected | (carried from prior doc — not separately anchored this pass) |

### Resolution Change Events

The prior doc listed three resolution events (0x8000B7, 0x8000B8, 0x8000BA). The handler-registration site shows **four**:

| ID | Handler name string | Notes |
|----|---------------------|-------|
| 0x8000B6 | ResolutionSelect | (carried from prior doc — not separately anchored this pass) |
| 0x8000B7 | `TopWindow::ResolutionChangeHandler` | [v5-validated] |
| 0x8000B8 | `TopWindow::ResolutionChangeBackHandler` | [v5-validated] |
| 0x8000B9 | `TopWindow::ResolutionChangeBackHandler` | [v5-validated] — **NEW**, missing from prior doc (same handler name as 0x8000B8; likely a dual-registration mode) |
| 0x8000BA | `TopWindow::ResolutionChangeHandler` | [v5-validated] (same handler name as 0x8000B7) |

Two pairs of event IDs reuse the same handler name. The dual-registration pattern suggests separate event IDs that both feed the same window-system action — likely "forward" and "back" navigation through resolution presets, each with both an immediate and a confirmation event.

### Dialog Events

| ID | Name | Notes |
|----|------|-------|
| 0x8000CE | DialogOK | (carried from prior doc — not separately anchored this pass) |
| 0x8000CF | DialogCancel | (carried from prior doc) |
| 0x8000D0 | ExitGame | (carried from prior doc) |
| 0x8000D1 | ExitProgram | (carried from prior doc) |

## TGDialogWindow Button System

`TGDialogWindow::AddButtons` accepts a bitfield parameter. The SWIG wrapper `new_TGDialogWindow` has an `i` (int) param confirmed as the button-mask. The bitfield layout below is carried from the prior doc; specific bit→button mappings beyond the mask concept are an open question (the prior doc's bit values are plausible from convention but were not separately anchored this pass).

| Bit | Button | Confidence |
|-----|--------|-----------|
| 0x001 | OK | medium (carried from prior doc) |
| 0x002 | Cancel | medium |
| 0x004 | Yes | medium |
| 0x008 | No | medium |
| 0x010 | Abort | medium |
| 0x020 | Retry | medium |
| 0x040 | Continue | medium |
| 0x080 | Ignore | medium |
| 0x200000 | Read-only mode (no buttons, display only) | medium |

The high-bit `0x200000` "read-only mode" is structurally distinct from the low-byte button bits — likely a flag that suppresses button creation entirely. The other bits sum into a `8`-bit button mask in the low byte.

## TGL Resource Files

The binary contains 12 TGL (TG Layout) file string references. The two most load-bearing for the UI subsystem:

| File | String address | Contents |
|------|----------------|----------|
| `data/TGL/Multiplayer.tgl` | 0x008e1900 [v5-validated] | MP lobby buttons, mission list, player list |
| `data/TGL/Options.TGL` | 0x008e1390 [v5-validated] | Quit dialog, graphics/sound settings |

The full list of 12 TGL files is not enumerated in this doc — flagged as documentation debt.

## RTTI Type IDs (UI region)

The TG hierarchy uses **integer-tag RTTI** for most classes (vtable slot 1 returns an integer constant). See [Two RTTI Systems](event-system-architecture.md#two-rtti-systems) in `event-system-architecture.md` for the framework and [tg-hierarchy-vtables.md](tg-hierarchy-vtables.md) for the Class Type-ID Constants table covering the TGObject chain.

| ID | Class | Anchor | Confidence |
|----|-------|--------|-----------|
| 0x810F | MainWindow (base for all full-screen views) | FindMainWindow's IsA call at 0x0050e1b0 | high [v5-validated] |
| 0x205 | (unknown class — vtable 0x00897270) | Slot 1 returns 0x205 | medium — TGConsole's actual vtable is 0x00897294 (different); 0x205 may be a parent (TGTextBlock?) |
| 0x80EA | (unknown class — vtable 0x00890ac4) | Slot 1 returns 0x80EA | medium — prior doc labeled "STRadioGroup" but that string does not exist in the binary; STSubPane has an `IsRadioGroup` property that may be the actual mechanism |

Two prior-doc class attributions were dropped because the class-name strings don't exist in the binary:

- **STRadioGroup** at 0x80EA — dropped. The vtable is real and slot 1 returns 0x80EA, but the class name does not exist in the SWIG string table or anywhere else searchable. STSubPane (which exists) exposes an `IsRadioGroup` property, suggesting "radio group" is a STSubPane feature rather than a separate class.
- **TGConsole/TGTextBlock** at 0x205 — partially dropped. TGConsole exists with vtable 0x00897294 (different from 0x00897270). 0x205 belongs to some other class in the chain — likely TGTextBlock (which has no SWIG string but is the inferred parent of TGConsole).

## Anchored vs Inferred Method Names

A v5-honest doc only names a class when there's a string anchor for it in the binary. SWIG wrapper strings are the most reliable source — every SWIG-bound class has its name as a constant string in the `.data` segment, retrievable via `search_strings`. Classes that are purely internal C++ (no Python binding, no debug print) won't appear in the string table and aren't anchorable by name.

The prior revision of this doc named three classes (`STWidget`, `STRadioGroup`, `TGScrollablePane`) that have no binary string anchor. Their positions in the inheritance tree are plausible from behaviour — STWidget as an abstract above STButton/STToggle, STRadioGroup as a TG-hierarchy class with type-ID 0x80EA, TGScrollablePane as a scroll-capable TGPane subclass between TGPane and TGTextBlock — but the C++ names aren't anchored. STWidget and STRadioGroup have been dropped (replaced by behavioural placeholders); TGScrollablePane has been demoted to `confidence: medium`.

This is the same disposition applied in [event-system-architecture.md](event-system-architecture.md) for the `SaveBroadcastHandlers` / `LoadBroadcastHandlers` / `FixupReferences` / `FixupComplete` / TGConditionHandler-internal / TGEventHandlerTable-internal method-name families.

## Open Questions and Documentation Debt

1. **Class identities for MainWindow type IDs 3, 4, 5.** Vtables and constructors are anchored, but the class names are unknown. Type 5 uses an "LCARS_640" font reference, suggesting a HUD or PlayControls-style class. Settling each would require either a SWIG-string match against an as-yet-undiscovered name or a vtable-chain walk against the TGObject hierarchy's Type-ID constants table.
2. **TGScrollablePane internal-or-invented status.** No SWIG string. Resolution would require finding (or failing to find) a class ctor that calls TGPane's base ctor and adds scroll-related fields. If such a ctor exists, TGScrollablePane is real-but-internal; if not, it's RE inference.
3. **TGDialogWindow button-bit → button-instance mappings.** The bitfield-mask concept is confirmed by the SWIG signature (`new_TGDialogWindow` takes an `i` int param), but the specific bits-to-button mapping (0x001 OK, 0x002 Cancel, etc.) is carried from prior doc convention rather than separately verified. Tracing what button objects get created for each set bit would settle this — likely a per-bit conditional in TGDialogWindow's `AddButtons` method.
4. **PlayWindow field semantic labels.** Offsets at +0x38 through +0x70 are confirmed as PlayWindow fields by the `FUN_00405ad0` zero-init helper, but the semantic names (`score`, `rating`, `kills`, `playerShip`, `godMode`, `terminateEvent`, `currentEpisode`) are inherited RE inference. The labels are plausible but only the offsets are anchored.

## See also

- [event-system-architecture.md](event-system-architecture.md) — TGEventManager dispatch, TGCallback / TGConditionHandler internals. The event IDs cataloged above are registered through that dispatch infrastructure.
- [tg-hierarchy-vtables.md](tg-hierarchy-vtables.md) — TGObject → Ship vtable chain (verified). Anchors the integer-tag RTTI mechanism that the UI classes inherit.
- [function-map.md](function-map.md) — address-range partition. UI framework lives in `0x0046-0x004B` (1,241 functions); Windows/Dialogs in `0x004C-0x0051` (1,112 functions); MainWindow ctors and TopWindow are in the Windows/Dialogs range.
- [rtti-class-catalog.md](rtti-class-catalog.md) — the 670-class catalog. TG/UI classes covered there at higher level; this doc adds the per-class layout/RTTI detail for the UI subset.
- [v5-validation-status.md](v5-validation-status.md) §6 — validation log entry for this doc.
- [docs/guides/v5-evidence-header.md](../guides/v5-evidence-header.md) — the evidence standard.
