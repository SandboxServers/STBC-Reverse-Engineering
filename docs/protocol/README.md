> [docs](../README.md) / protocol

# Protocol Documentation

Wire formats, opcodes, and serialization for BC's multiplayer protocol.

## Wire Format (split from monolith)

| Document | Contents |
|----------|----------|
| [wire-format-spec.md](wire-format-spec.md) | **Hub** — summary opcode tables, subsystem catalog, anti-cheat hash |
| [transport-layer.md](transport-layer.md) | Raw UDP packet, 7 transport types, TGMessage layout, fragment reassembly, reliable delivery |
| [stream-primitives.md](stream-primitives.md) | TGBufferStream read/write, bit packing, CF16 encoding, CompressedVector3/4 |
| [checksum-opcodes.md](checksum-opcodes.md) | Opcodes 0x20-0x28: checksum request/response, file transfer, 5 rounds |
| [game-opcodes.md](game-opcodes.md) | Opcodes 0x00-0x2A: Settings, GameInit, ObjCreate, PythonEvent, weapons, etc. |
| [stateupdate.md](stateupdate.md) | Opcode 0x1C: dirty flags, 8 field formats, round-robin subsystem/weapon serialization |
| [object-replication.md](object-replication.md) | FUN_0069f620 object create/update, serialization chain |
| [python-messages.md](python-messages.md) | Opcodes 0x2C+: TGMessage script messages, SendTGMessage API, wire examples |

## Detailed Protocol Documents

| Document | Contents |
|----------|----------|
| [pythonevent-wire-format.md](pythonevent-wire-format.md) | PythonEvent (0x06) polymorphic event transport, 4 factory types |
| [tgobjptrevent-class.md](tgobjptrevent-class.md) | TGObjPtrEvent (factory 0x010C): class layout, wire format, 5 C++ producers |
| [set-phaser-level-protocol.md](set-phaser-level-protocol.md) | SetPhaserLevel (opcode 0x12): TGCharEvent wire format |
| [collision-effect-protocol.md](collision-effect-protocol.md) | CollisionEffect (opcode 0x15): contact point compression, handler validation |
| [stateupdate-subsystem-wire-format.md](stateupdate-subsystem-wire-format.md) | Subsystem health wire format: linked list order, WriteState formats |
| [subsystem-integrity-hash.md](subsystem-integrity-hash.md) | Subsystem hash (anti-cheat): dead code in MP |
| [cf16-precision-analysis.md](cf16-precision-analysis.md) | CF16 precision tables and mod compatibility |
| [cf16-explosion-encoding.md](cf16-explosion-encoding.md) | CF16 explosion encoding analysis |
| [objcreate-serialization.md](objcreate-serialization.md) | Full object serialization chain |
| [message-trace-vs-packet-trace.md](message-trace-vs-packet-trace.md) | Stock-dedi opcode cross-reference |
| [tgmessage-routing.md](tgmessage-routing.md) | TGMessage routing: relay-all, no whitelist, star topology |
| [objnotfound-requestobj-enterset-wire-format.md](objnotfound-requestobj-enterset-wire-format.md) | Opcodes 0x1D/0x1E/0x1F triad: object recovery + scene transition |

## Campaign Tracker

| Document | Contents |
|----------|----------|
| [v5-validation-status.md](v5-validation-status.md) | Protocol-family v5 re-validation tracker: 22-doc inventory, foundation→leaves order, cross-doc disagreements, engine-family anchor table |
