---
name: dispatcher-recovery-20260528
description: MpgameHandleMessage (game opcode dispatcher) recovery at 0x0069f2a0 — Ghidra missed it because the only xref is DATA (handler registration), not a CALL. Pattern applies to any TGMessage handler.
metadata:
  type: project
---

# Dispatcher Recovery — 0x0069f2a0 (MpgameHandleMessage)

## What was recovered

**Function**: `MpgameHandleMessage` at `0x0069F2A0` (body 0x0069F2A0 - 0x0069F530, 657 bytes).
**Signature**: `void __thiscall MpgameHandleMessage(MultiplayerGame *this, TGMessage *pMsg)`.
**Role**: Tier-2 message dispatcher — game opcodes 0x02-0x2A. Receives a TGMessage, extracts the embedded TGBufferStream (at pMsg+0x28), virtual-calls vtable[0] for a stream-type tag (expected 0x32), then opcode-dispatches via a 41-entry jump table at `0x0069F534` (`MpgameHandleMessage_OpcodeJumpTable`).

**Completeness after v5 pass**: 64.4 raw / 69.94 effective (max achievable 94.4).
Remaining fixable deductions are all type-quality issues: no `MultiplayerGame`, `TGMessage`, or `TGBufferStream` structs exist in Ghidra's type DB yet. Creating those structs is the next obvious lift.

## Why: this is the v5 campaign's most-cited address. Every protocol doc references it; without a function entry it could not be re-validated.

## How to apply: when you encounter a documented function address that returns "No function found" from Ghidra, check the prologue bytes first — if they look like a valid prologue (`57 8B F9` for __thiscall, `55 8B EC` for __cdecl/__stdcall with frame), it's almost certainly a real entry Ghidra missed because the xrefs are all DATA-mode (callback registration tables, vtables).

## Decoded jump table (raw bytes from 0x0069F534)

41 little-endian DWORDs (index = opcode - 2). Each entry points to a thunk inside the dispatcher body (0x0069F2F6-0x0069F51D); the thunk CALLs the actual handler then RET 4. Full mapping is in the function plate comment. Key correction to existing docs:

- **opcode 0x1C (StateUpdate) handler is FUN_0069FF50** — this row is missing from the CLAUDE.md opcode table.

## Pattern learned: "Ghidra-missed function" detection

When auto-analysis fails to declare a function entry, the most common cause for stbc.exe is:

1. **Registered callback** — function pointer pushed into a registry table at static-init time, never directly CALLed. Detected by:
   - `get_xrefs_to(addr)` returns 1-3 entries, all marked `[DATA]`.
   - The DATA xref site disassembles to a PUSH-imm32-of-the-address followed by `MOV ECX, <registry>; CALL <register-method>`.
2. **Vtable slot** — function address sits in a vtable layout. DATA xref from the `.rdata` vtable bytes.
3. **Computed jump target** — entry only reached via switch jump tables (rare; handlers are usually full functions). Detected by xref from a JMP-via-table site.

For case 1 (the most common), the fix is:
```
create_function(addr, name="<PascalCase>")
set_function_prototype(addr, "<prototype>", calling_convention="__thiscall")
analyze_for_documentation(addr)
# proceed with v5 workflow
```

For STBC specifically: callbacks are usually __thiscall (PUSH EDI; MOV EDI, ECX prologue) because they're MultiplayerGame methods registered through a member-pointer registry.

## Pattern learned: v5 plate-comment section headers

The `analyze_function_completeness` linter looks for **section headers** with **exact** formatting:
- `Parameters:` (mixed case, colon, on its own line)
- `Returns:` (mixed case, colon)
- `Algorithm:` (mixed case, colon)

ALL-CAPS headers (`PARAMETERS`, `RETURNS`, `ALGORITHM`) are NOT recognized and produce false "Missing X section" deductions. First plate comment used ALL-CAPS and was rejected; switching to `Title:` form removed the deductions and added 15 points to the completeness score.

## Pattern learned: __thiscall prototype gotcha

When using `set_function_prototype` on a `__thiscall` function:
- Do NOT include a `this` parameter explicitly in the prototype string — the API adds it automatically as ECX auto-parameter.
- Pass ONLY the explicit stack parameters.
- Example: `void Func(void * pMsg)` with `calling_convention="__thiscall"` becomes `void __thiscall Func(this, pMsg)`.

If you pass `void Func(void * pThis, void * pMsg)`, you get a 3-param function (`this, pThis, pMsg`) which is wrong.

Note: Ghidra cannot retype the `this` auto-parameter via the API. The `Hungarian violations: this (expected p prefix)` deduction is **structural** and accepted by the v5 standard.

## Pattern learned: linter type-name hallucinations

`analyze_function_completeness` recommendations sometimes claim a struct exists (e.g., `struct 'Msg' exists in program, use Msg*`) when `validate_data_type_exists` says it doesn't. Verify before applying.

## Open questions for follow-up

1. **0x32 stream-type tag** — confirmation needed via decompile of the TGBufferStream vtable[0] slot. Could be a message-length tag (50 bytes max?) or a class-ID enum value. Will affect documentation of TGStreamedObject family.
2. **g_bMpgameInOpcodeDispatch (0x0097FA8B)** — re-entrancy guard usage elsewhere. Search xrefs to confirm it gates reentrant SendTGMessage calls from inside a handler.
3. **FUN_006b8530 (TGBufferStream getter)** — single-purpose helper called only from this dispatcher. Should be renamed (likely `TGBufferStream::GetReadPointer`) but needs body decompile first.
4. **Three other dispatchers** still need the same recovery treatment if Ghidra missed them:
   - `FUN_006a3cd0` (NetFile/checksum dispatcher) — confirmed exists.
   - `FUN_00504c10` (MultiplayerWindow UI dispatcher) — confirmed exists.
   - All three downstream group handlers (`FUN_0069f880` PythonEvent, `FUN_0069fda0` generic event-forward, `FUN_006a2470` collision) need their own v5 passes.

## Cross-reference targets

- `CLAUDE.md` Documentation Index — opcode handler table needs row 0x1C added (`StateUpdate -> FUN_0069ff50`).
- `docs/protocol/game-opcodes.md` — should be updated with the jump-table evidence trail and 0x32 stream-type-tag note.
- `docs/protocol/stateupdate.md` — should cross-reference `FUN_0069ff50` as the StateUpdate entry handler.
- `docs/networking/network-protocol.md` — three-dispatcher overview should cite this dispatcher's address with v5 confidence.

## Structs to create (next v5 pass)

To push completeness above 80%, create skeletons for:
- `MultiplayerGame` — at least `field_0x70` (network ptr), enough to type `this`.
- `TGMessage` — at least `field_0x28` (embedded stream).
- `TGBufferStream` — vtable layout with at least `vtable[0]` (type/length getter).

These structs are referenced across ~17 handler functions and will propagate completeness gains far beyond just this dispatcher.

Linked memory: [[engine-snapshot-20260528]]
