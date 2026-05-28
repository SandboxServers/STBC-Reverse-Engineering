---
name: ui-class-hierarchy-validation-20260528
description: V5 doc #9 validation — UI class hierarchy. TopWindow global mis-attribution corrected (0x009878cc, not 0x0097e238). MultiplayerGame +0x74/+0x1FC offsets locked in via ctor; struct-skeletons memory had +0x70 wrong. MainWindow type-ID catalog expanded 8 → 12 (types 3, 4, 6 NEW). Doc's "PlayWindow type ID 5 ctor 0x00405c10" REFUTED.
metadata:
  type: project
---

# UI Class Hierarchy Validation — 2026-05-28

V5 campaign doc #9. Heavy load-bearing corrections. Net: doc keeps about ~70% of its claims; the big one (TopWindow global address) flips, and the doc conflates two distinct PlayWindow concepts.

## Headline correction: TopWindow vs PlayWindow globals

CLAUDE.md and the doc both say "TopWindow at `0x0097e238`". **Wrong.** Two distinct globals exist:

| Global | Class | Set by | Stored by |
|--------|-------|--------|-----------|
| `0x009878cc` | TopWindow (root scene container) | FUN_0050c430 (TopWindow ctor) | `DAT_009878cc = param_1` at 0x0050c485 |
| `0x0097e238` | PlayWindow / "Game" state object | FUN_00405c10 (PlayWindow ctor) | `DAT_0097e238 = param_1` at 0x00405c8d |

The PlayWindow class (FUN_00405c10) is **NOT** a child of TopWindow and **NOT** a MainWindow (it never calls FUN_0050e920 to register a typeID). It's a standalone TGEventHandlerObject-derived class that holds game state (score/rating/kills/playerShip/godMode/terminateEvent/currentEpisode). MultiplayerGame extends it.

CLAUDE.md needs the same correction.

## TopWindow's 5 children — actual catalog

`FUN_0050c430` allocates 5 children. Sizes + type IDs + vtables:

| # | Size | Type ID | vtable | Class | Ctor |
|---|------|---------|--------|-------|------|
| 1 | 0x6c | **4** | 0x0088ec9c | unnamed | inline in TopWindow ctor |
| 2 | 0x50 | **2** | 0x0088f098 | ConsoleWindow | FUN_0050ebc0 |
| 3 | 0xb8 | **8** | 0x0088e74c | MultiplayerWindow | FUN_00504390 |
| 4 | 0x5c | **9** | 0x0088e344 | PlayViewWindow (no SWIG string — inferred name) | FUN_004fc480 |
| 5 | 0x64 | **10** | 0x0088e5fc | CinematicWindow | FUN_005023c0 |

Doc claims TopWindow's 5 children are types {0, 2, 5, 8, 10}. **Wrong.** Actual is {4, 2, 8, 9, 10}.

## Full MainWindow ctor catalog (extends doc's 8 entries → 12)

Every caller of `FUN_0050e920` (MainWindow base ctor) — found via xref sweep:

| Ctor | Type ID | vtable | Class name (verified by SWIG string) |
|------|---------|--------|--------------------------------------|
| FUN_004fb750 | 0 | 0x0088e1f4 | BridgeWindow ✓ |
| FUN_0050b290 | 1 | 0x0088eb48 | TacticalWindow ✓ |
| FUN_0050ebc0 | 2 | 0x0088f098 | ConsoleWindow ✓ |
| FUN_00496a60 | 3 | 0x0088aa3c | **NEW — class unknown** |
| TopWindow inline, FUN_00622300 | 4 | 0x0088ec9c | **NEW — class unknown** |
| FUN_00507900 | 5 | 0x0088e8a0 | **NEW — class unknown (doc wrongly maps this to FUN_00405c10)** |
| FUN_004fe560 | 6 | 0x00889c4c | **MapWindow** (NEW — has SWIG string `MapWindow::*`) |
| FUN_004fd6f0 | 7 | 0x0088e494 | **SortedRegionMenu** (NOT `SortedRegionMenuWindow` as doc says — SWIG string lacks "Window" suffix) |
| FUN_00504390 | 8 | 0x0088e74c | MultiplayerWindow ✓ |
| FUN_004fc480 | 9 | 0x0088e344 | (PlayViewWindow inferred — no SWIG string) |
| FUN_005023c0 | 10 | 0x0088e5fc | CinematicWindow ✓ |

MainWindow base ctor `FUN_0050e920(this, typeID, w, h)` always writes typeID to `this+0x4C`. Confirmed via `FUN_0050e1b0` (FindMainWindow) which calls `vtable[2]=IsA(0x810F)` then matches `*(int*)(child+0x4C) == typeID`. **0x810F MainWindow type ID is solid.**

## MultiplayerGame layout — +0x74 / +0x1F8 / +0x1FC verified, struct-skeletons memory was WRONG

The doc says playerSlots[16] at +0x74. My older `struct-skeletons-20260528.md` said +0x70. **The doc is right.**

Anchored in MultiplayerGame ctor `FUN_0069e590`:
- `FUN_00859d64(param_1 + 0x1d, 0x18, 0x10, ...)` → array at +0x74 (= 0x1d * 4), stride 0x18, count 0x10 = **playerSlots[16] at +0x74**
- Caller `FUN_00504f10` (GameInit) allocates **0x200** bytes for the class
- `param_1[0x7f] = playerLimit` → **+0x1FC = maxPlayers (dword)**
- `MOV byte ptr [EBP + 0x1f8], 0x0` at 0x0069eaf1 → **+0x1F8 = readyForNewPlayers (BYTE not DWORD)**

Internal consistency: +0x74 + (0x18 * 16) = +0x1F4. Then +0x1F8 (byte) + 3 pad + +0x1FC (dword) = +0x200. Perfect.

MultiplayerGame vtable: **0x0088b480**. Overrides PlayWindow vtable 0x008887e8.

`struct-skeletons-20260528.md` needs a correction — the "MultiplayerGame +0x70 playerSlots" claim there is wrong. Will fix in a follow-up.

## PlayWindow base class layout (anchored via FUN_00405ad0 zero-init helper)

`FUN_00405ad0` is called from PlayWindow ctor and zeroes all PlayWindow fields. Layout (dword fields unless noted):

```
+0x38 0x44 0x48 0x4C 0x50 0x54  (6 contiguous dwords)
+0x60 byte   +0x61 byte   +0x62 byte (= 1)
+0x64 0x68 0x6C 0x70 (4 dwords)
```

So **+0x70 IS a PlayWindow field** (doc says currentEpisode — plausible label, unverified). This is why MultiplayerGame's playerSlots can't start at +0x70: it would clobber the inherited PlayWindow.currentEpisode. **MultiplayerGame.playerSlots at +0x74 is structurally forced.**

Doc's specific labels (+0x38 score, +0x3C rating, +0x40 kills, +0x54 playerShip, +0x60 godMode, +0x6C terminateEvent, +0x70 currentEpisode) — the **offsets** are confirmed as PlayWindow fields; the **semantic names** are unverified RE inference but plausible from context.

## TGUIObject layout — flag 0x08 verified

TGUIObject ctor (`FUN_0072dcc0`) calls parent `FUN_0072fc20` which sets:
- `param_1[5] = 0` → +0x14 = NULL (parent) ✓ — doc confirmed
- `param_1[10] = 8` → **+0x28 = 0x08 initial (visible bit)** ✓ — doc's "0x08 visible" confirmed
- `param_1[0xb] = 0` → +0x2C = NULL (callbacks) ✓

Then TGUIObject ctor sets:
- `+0x18, +0x1C` zeroed (bounds.x, bounds.y) ✓ — doc's "+0x18 bounds" confirmed
- `+0x30..+0x40` zeroed
- `+0x44 = 2` (some default — meaning unknown)
- vtable at `0x00897c14` (NOT 0x00897d80 — that's the **RTTI-name lookup block**, separate from real vtable)

Flag bit `0x10000000` (TGParagraph layout-in-progress guard) **confirmed** at FUN_00732120: `param_1[10] |= 0x10000000` then later `&= 0xefffffff`. Verifies the doc claim.

## Inheritance tree validation — TGScrollablePane and STWidget don't exist as SWIG classes

All SWIG class strings present in binary:
- TGUIObject ✓ (184 methods exposed)
- TGPane ✓ (52 methods)
- TGScrollablePane — **NO SWIG STRING** (internal class — may still exist as a C++ class but not Python-exposed)
- TGTextBlock — **NO SWIG STRING** (matches doc's "aliased as TGConsole")
- TGConsole ✓ (15 methods)
- TGWindow ✓ (17 methods)
- STWidget — **NO STRING ANYWHERE** — may be RE invention
- STButton ✓
- STToggle ✓
- TGIcon ✓
- TGParagraph ✓
- TGRootPane ✓ (43 methods)
- TGDialogWindow ✓
- STRadioGroup — **NO STRING ANYWHERE** — likely RE invention; actual is `STSubPane.IsRadioGroup` property

Doc's tree {TGScrollablePane → TGTextBlock} and {STWidget → STButton → STToggle} have no SWIG anchor. Either they exist internally (no Python binding) or they're RE inference. Cannot confirm or refute from string search alone — would need vtable-chain walking to resolve.

## Event ID registrations — TopWindow handler table

Found a goldmine at `FUN_0050ca50` — registers all top-level event handlers via `FUN_006d92b0(dispatchTable, eventID, handlerName)`. Confirms 16+ event IDs by name string:

| Event ID | Handler | Doc verdict |
|----------|---------|-------------|
| 0x30001 | TopWindow::MouseHandler | ✓ |
| 0x30002 | TopWindow::KeyboardHandler | ✓ (matches doc's 0x30002 Keyboard) |
| 0x800494 | TopWindow::ToggleConsoleHandler | ✓ |
| 0x800495 | TopWindow::ToggleOptionsHandler | ✓ |
| 0x8003cc | TopWindow::ToggleEditHandler | ✓ |
| 0x800496 | TopWindow::TabFocusHandler | ✓ |
| 0x800497 | TopWindow::PrintScreenHandler | ✓ |
| 0x800498 | TopWindow::ToggleBridgeAndTacticalHandler | ✓ |
| 0x8001dd | TopWindow::SelfDestructHandler | ✓ |
| 0x800005 | OptionsWindow::NewGameHandler | ✓ |
| 0x800006 | OptionsWindow::LoadGameHandler | ✓ |
| 0x800007 | OptionsWindow::SaveGameHandler | ✓ |
| 0x800002 | OptionsWindow::QuitHandler | ✓ |
| 0x8000c6 | OptionsWindow::NewMultiplayerGame | ✓ |
| 0x8000b7 | TopWindow::ResolutionChangeHandler | ✓ (doc's ResolutionChangeForward) |
| 0x8000b8 | TopWindow::ResolutionChangeBackHandler | ✓ |
| 0x8000b9 | TopWindow::ResolutionChangeBackHandler | NEW — doc missing |
| 0x8000ba | TopWindow::ResolutionChangeHandler | ✓ (doc's ResolutionApply) |

Doc's event-ID block is well-verified. Cross-link to event-system-architecture.md.

## RTTI type IDs — 0x205 and 0x80EA need re-anchoring

- **0x810F MainWindow**: solidly verified via FindMainWindow logic. Keep at `high` confidence.
- **0x205**: confirmed as a class's GetTypeID-return value (vtable 0x00897270 at slot 1). The **TGConsole vtable is at 0x00897294** (different vtable!). So 0x205 may be a parent class of TGConsole, not TGConsole itself. Doc's "0x205 TGConsole/TGTextBlock" is **medium** at best — needs chain-walking to confirm.
- **0x80EA**: confirmed as a class's GetTypeID-return (vtable 0x00890ac4 slot 1, ctor FUN_00532f50). **No SWIG class named STRadioGroup exists.** Closest is STSubPane (which has IsRadioGroup property). Doc's "0x80EA STRadioGroup" appears **wrong** — the actual class name is unknown but is not STRadioGroup.

## Pattern lessons (reusable across UI docs)

1. **RTTI-name lookup blocks ≠ vtables.** In stbc.exe, each TG/UI class has TWO data tables: a name-pointer block at one address (3 dwords: name, name-with-Ptr stubs) and a vtable at a different address (where ctors write into `*this`). Confusing these wastes hours. The vtable address is whatever `*param_1 = &PTR_FUN_XXXX` writes in the ctor.

2. **GetTypeID convention in TG/UI classes**: vtable slot 1 (offset +4) is a tiny stub `MOV EAX, <typeID>; RET`. vtable slot 2 (offset +8) is the IsA stub: `MOV EAX, [ESP+4]; CMP EAX, <typeID>; SETZ AL; RET 4`. Find these by searching for `b8 XX XX XX XX c3` followed by NOPs followed by `8b 44 24 04 3d XX XX XX XX 75 05 b0 01 c2 04 00`. This pattern is **highly reusable**.

3. **MainWindow type-ID catalog by xref to FUN_0050e920**: every MainWindow subclass ctor passes its type ID as `param_2`. Walking the xrefs gives a complete catalog in one sweep.

4. **The "child stored at global X" idiom**: ctors that store `DAT_XXXXXXXX = param_1` are establishing well-known global accessors. Cross-check by xref-counting on the global.

## Open questions

1. What is the class at type ID **4** (vtable 0x0088ec9c)? Created twice (TopWindow inline + FUN_00622300). No SWIG string match.
2. What is the class at type ID **3** (vtable 0x0088aa3c, ctor FUN_00496a60)?
3. What is the class at type ID **5** (vtable 0x0088e8a0, ctor FUN_00507900)? Uses "LCARS_640" font — likely HUD/PlayControls UI. Not "PlayWindow" (that name belongs to FUN_00405c10).
4. Is TGScrollablePane an internal C++ class with no Python binding, or pure RE invention? Would need to find a class whose ctor calls TGPane base ctor AND adds scroll-related fields.
5. Is the doc's "TGDialogWindow button bitfield" claim correct? `new_TGDialogWindow` SWIG signature has an `i` param (int — buttonMask) — bitfield concept is right but specific bit→button mappings (0x001 OK, 0x002 Cancel, etc.) need verification by tracing what buttons get created.

## Status

- Doc moves from `pending` to `partial` in §6 row #9.
- Tracker §6 was updated (single-line, with the headline corrections).
- Next: documentation-writer to render the corrected doc with v5 frontmatter.
