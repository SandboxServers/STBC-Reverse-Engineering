---
name: function-map-validation-20260528
description: V5 validation findings for docs/engine/function-map.md against current Ghidra state — totals, ranges, per-category partition, spot-check named functions.
metadata:
  type: project
---

# function-map.md V5 Validation (2026-05-28)

## Validation outcome
Foundation doc validates **almost perfectly**. The 20-category address-range partition is fully intact — every category's claimed range and count match within +/-1. Only two deltas, both tiny.

## Ghidra totals (STBC.exe, get_function_count=18,576)
- Functions visible via paginated list_functions_enhanced: **18,249** (matches "total: 18249" from search_functions_enhanced)
- Functions in .text section (0x00401000-0x00887fff): 18,249
- Discrepancy 18,576 - 18,249 = 327 — these are EXTERNAL import thunks (addresses like `EXTERNAL:0000XXXX`), not in the function body inventory. The doc's "18,247 functions" matches the in-binary-body count (delta +2).

## Function-type breakdown (from search_functions_enhanced)
| Type | Doc | Ghidra | Delta |
|------|-----|--------|-------|
| Total (in-body) | 18,247 | 18,249 | +2 |
| FUN_xxxxxxxx | 13,333 | 13,467 | +134 |
| Thunks | 133 | 164 | +31 |
| Unwind@ | 4,692 | 4,692 | **EXACT** |
| Catch@ | 3 | 3 | **EXACT** |
| Custom-named | (not stated) | 4,782 | n/a |
| has_custom_name=false | n/a | 13,467 | n/a |

## Address range
- Lowest function: **0x004010e0** (doc match)
- Highest function: **0x008879e0** (doc match)
- .text section: 0x00401000 - 0x00887fff (segment boundary)

## Per-category validation (all 20 categories)
The partition is exact except for +1 in two cells:

| # | Category | Claimed Range | Claimed Count | Actual | Delta |
|---|----------|---------------|---------------|--------|-------|
| 1 | Core/Base Objects | 0x00401000-0x0042FFFF | 646 | 646 | 0 |
| 2 | UtopiaApp/Module | 0x00430000-0x0045FFFF | 717 | 717 | 0 |
| 3 | UI Framework | 0x00460000-0x004BFFFF | 1241 | 1241 | 0 |
| 4 | Windows/Dialogs | 0x004C0000-0x0051FFFF | 1112 | 1112 | 0 |
| 5 | Game Logic/Ships/AI | 0x00520000-0x005AFFFF | 2073 | 2073 | 0 |
| 6 | Sparse/Mission | 0x005B0000-0x0065FFFF | 201 | 201 | 0 |
| 7 | Scene Graph/3D | 0x00660000-0x0068FFFF | 527 | 527 | 0 |
| 8 | Game Session | 0x00690000-0x0069DFFF | 159 | 159 | 0 |
| 9 | MultiplayerGame | 0x0069E000-0x006A2FFF | 44 | **45** | **+1** |
| 10 | NetFile/Checksums | 0x006A3000-0x006A7FFF | 58 | 58 | 0 |
| 11 | Containers/Hash | 0x006A8000-0x006AFFFF | 141 | 141 | 0 |
| 12 | TGNetwork | 0x006B0000-0x006BFFFF | 225 | 225 | 0 |
| 13 | Streams/Serial | 0x006C0000-0x006CFFFF | 246 | 246 | 0 |
| 14 | Events/Timers | 0x006D0000-0x006DFFFF | 327 | 327 | 0 |
| 15 | Config/VarMgr | 0x006E0000-0x006EFFFF | 226 | 226 | 0 |
| 16 | GameSpy/SWIG | 0x006F0000-0x006FFFFF | 273 | 273 | 0 |
| 17 | Python/SWIG | 0x00700000-0x0076FFFF | 1619 | **1620** | **+1** |
| 18 | NetImmerse/Render | 0x00770000-0x0084FFFF | 2915 | 2915 | 0 |
| 19 | CRT/stdlib | 0x00850000-0x0086FFFF | 787 | 787 | 0 |
| 20 | Exception/Unwind | 0x00870000-0x008879E0 | 4710 | 4710 | 0 |
| | **TOTAL** | | **18,247** | **18,249** | **+2** |

## The +1 in Cat 9 is identifiable
**0x0069f2a0 = MpgameHandleMessage** (the only custom-named function in Cat 9). This was created by the v5 dispatcher recovery work. The doc says "0x0069f2a0 = ReceiveMessageHandler (handler addr, not function entry)" — explicitly flagging it as NOT a function entry. The v5 work created a function there with `__thiscall(void* this, void* pMsg)` signature. So +1 in Cat 9 is the dispatcher Ghidra entry that didn't previously exist.

## The +1 in Cat 17 is not yet pinned
Python/SWIG range; 1,619 → 1,620. Did not investigate the specific extra function. Possibly Ghidra found one additional function during a recent re-analysis pass.

## Spot-check on named function claims
Per the no-annotation-scripts constraint, the "Named/Identified Functions" sub-lists in the doc are pre-v5 claims. Sampled 6 addresses:

| Addr | Doc name | Ghidra current | Status |
|------|----------|----------------|--------|
| 0x0043b4f0 | UtopiaApp_MainTick | FUN_0043b4f0 | UNNAMED |
| 0x0069efe0 | RegisterMPGameHandlers | FUN_0069efe0 | UNNAMED |
| 0x006a3cd0 | NetFile::ReceiveMessageHandler | FUN_006a3cd0 | UNNAMED |
| 0x006b4560 | TGNetwork::Update | FUN_006b4560 | UNNAMED |
| 0x006da2c0 | EventManager::ProcessEvents | FUN_006da2c0 | UNNAMED |
| 0x0069f2a0 | ReceiveMessageHandler | MpgameHandleMessage | NAMED (v5 work) |

All cited addresses exist as functions. None are renamed except 0x0069f2a0.

## Boundary verification (3 sampled)
- Cat 9→10 boundary at 0x006A3000: cleanly partitioned (last Cat 9 = 0x006a2fc0; first Cat 10 = 0x006a3080)
- Cat 14→15 boundary at 0x006E0000: clean (0x006dffb0 / 0x006e00b0)
- Cat 19→20 boundary at 0x00870000: clean (0x0086ffb1 / 0x008700e8)

## MCP techniques that worked
- `get_function_count(program=STBC.exe)` — gives total including external thunks (18,576)
- `search_functions_enhanced(name_pattern=Unwind@)` — returns `total: 4692` (exact match to doc)
- `search_functions_enhanced(name_pattern=Catch@)` — returns 3
- `search_functions_enhanced(name_pattern=FUN_)` — returns 13,467 (Ghidra FUN_* count)
- `search_functions_enhanced(is_thunk=true)` — returns 164
- `search_functions_enhanced(has_custom_name=true)` — returns 4,782
- `list_functions_enhanced(limit=10000)` in two batches — covers the full 18,249 in-body functions
- `list_segments` reveals `.text: 00401000-00887fff` which anchors the partition's outer boundary

## MCP gotcha: pagination cap
`list_functions_enhanced` with offset >= 18249 returns empty `[]`. The `total` field in `search_functions_enhanced` reports 18,249 (the visible-by-pagination count), NOT 18,576 (the `get_function_count` value). The 327 delta is external import thunks not iterated by the address-sorted list.

## Pattern: doc partitions hold up well
The category boundaries in function-map.md are pure address-range cuts (e.g., 0x006A3000-0x006A7FFF). These don't drift between Ghidra imports — they're mechanical partitions of the .text segment. Only deltas come from:
1. Newly recognized functions Ghidra finds during analysis (the +1 in Cat 17)
2. Functions intentionally created via `create_function` (the Cat 9 +1 dispatcher)

The "Named/Identified Functions" sub-lists are tied to annotation scripts and DO drift.
