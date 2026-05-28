# Game Archaeology Specialist — Memory

Field journal for binary archaeology on stbc.exe. The binary is finite; every dig builds the shared map.

## Index

- [Engine Snapshot 2026-05-28](engine-snapshot-20260528.md) — v5 campaign ground truth: binary fingerprint, naming coverage (25.7%, not 83%), annotation scripts never applied to current import, top 3 drift findings
- [Dispatcher Recovery 2026-05-28](dispatcher-recovery-20260528.md) — MpgameHandleMessage at 0x0069F2A0 recovered (Ghidra missed it: DATA-only xref); jump table decoded; v5 patterns for callback-registered functions, plate header format, __thiscall prototype gotchas
- [Struct Skeletons 2026-05-28](struct-skeletons-20260528.md) — MultiplayerGame (0x200), TGMessage (0x2C), TGBufferStream (0x2C), PlayerSlot (0x18) in Ghidra DB; dispatcher 69.94->79.0; HostMsgHandler +30 by typing; field-anchor patterns
- [TGBufferStream Vtable 2026-05-28](tgbufferstream-vtable-20260528.md) — vtable[0]=GetStreamTypeId returns 0x32 (95.0 score); sizeof grown 0x2C->0x40; 8 vtable slots named; cursor/pad open Q resolved; dispatcher 0x32 claim medium->high
