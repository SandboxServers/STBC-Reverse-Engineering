# OpenBC Test Session Analysis (2026-02-25)

## Session: OpenBC v? vs stock BC client (local, 127.0.0.1)
- Duration: ~3m (T+0:00:04 to T+0:03:00)
- Outcome: FUNCTIONAL multiplayer with known issues

## Key Findings

### 1. CRITICAL: Client retransmission queue leak (ConnectAck + DataMsg/Keepalive)
- Client sends ConnectAck (type=0x03) seq=0 and DataMsg (type=0x00) seq=1 as reliable
- OpenBC never ACKs these with below32=1 flag
- Client retransmits both endlessly (190+ retransmissions before disconnect)
- Stock dedi: retxQ drains to 0 within 12ms of connection
- Stock sends ACK with below32=1 which clears these from client's retxQ
- **This is the main protocol gap** - OpenBC doesn't send/recognize below32 ACKs

### 2. Connect retransmissions (192 Connect packets over 3min)
- Client sends Connect (0xC0 0x00) repeatedly even after being connected
- These happen at ~1s intervals throughout the session
- This is the client's keepalive connect retry - harmless but noisy

### 3. ACK seq=1 flags=0x02 (371 instances from client)
- Client keeps sending this "ConnectAck ACK" (flags=0x02 = below32 bit?)
- OpenBC receives but doesn't act on it

### 4. BeamFire (0x1A) warnings: 10 malformed
- All at T+2:31 to T+2:34 (after ship change to BirdOfPrey)
- All same payload: [1A 26/27 00 00 40 02 AC B7 3C 01]
- Retransmissions: client resends every ~300ms

### 5. Graceful disconnect at T+3:00
- Client sends ConnectACK after ~3 minutes
- OpenBC interprets as graceful disconnect
- Post-disconnect client keeps retrying Connect for 18 more seconds

## Sequence Comparison: OpenBC vs Stock Dedi

### OpenBC handshake (T+0:00:04):
1. C->S: Connect
2. S->C: Connect + ChecksumReq(round 0) [bundled]
3. C->S: Keepalive (player name "Cady")
4. C->S: ACK seq=0 + ACK seq=0(flags=0x02) + ChecksumResp(round 0)
5. S->C: ACK seq=0 + ChecksumReq(round 1)
6. C->S: ACK seq=1 + ChecksumResp(round 1)
7. S->C: ACK seq=1 + ChecksumReq(round 2)
8. C->S: ACK seq=2(frag x3) + ChecksumResp(round 2) [fragmented, 832 bytes]
9. S->C: ACK seq=2(x3) + ChecksumReq(round 3)
10. C->S: ACK seq=3 + ChecksumResp(round 3)
11. S->C: ACK seq=3 + ChecksumReq(round 0xFF)
12. C->S: ACK seq=4 + ChecksumResp(round 0xFF) [268 bytes]
13. S->C: ACK seq=4 + 0x28(PreSettings) + 0x00(Settings) + 0x01(GameInit) + 0x37(Score)
14. C->S: ACK seq=5,6,7,8
15. C->S: NewPlayerInGame (0x2A)
16. S->C: ACK seq=5 + 0x35(MissionInit) + 0x17(DeletePlayerUI)
17. C->S: ACK seq=9,10

### Key differences from stock dedi:
- Stock bundles 0x28+0x00+0x01 in a SINGLE UDP datagram (confirmed)
- OpenBC also bundles them (verified from raw flush: same datagram)
- Stock sends Settings as: [00 15 00 A3 41 ...] (gameTime as float, then WriteBit, WriteBit, slot)
- OpenBC sends Settings as: [00 30 08 6C 3F ...] = gameTime is in different float range
  - 0x3F6C0830 = 0.922... vs stock 0x41A30015 = 20.38
  - OpenBC gameTime appears wrong or differently formatted

### Settings packet decode (from client msg trace):
- OpenBC: gameTime=20.38, collisionDmg=1, friendlyFire=0, slot=0
  - raw: [00 15 00 A3 41 61 00 25 00 ...]
  - Actually: the client decoded it correctly as 20.38. The trace format is after decryption.

## Gameplay Reached
- Ship select: YES (ObjCreateTeam received at T+2.8s after connect)
- Ship spawned: Sovereign (species=5, hull=12000)
- StateUpdate exchange: WORKING (both directions)
- Collision damage: WORKING (10 CollisionEffect events)
- Self-destruct: WORKING (2x HostMsg 0x13 at T+2:07 and T+2:55)
- Ship change: WORKING (BirdOfPrey at T+2:20)
- PythonEvent relay: WORKING (damage events sent to client)
- ScoreChange: WORKING (sent after self-destruct)
- Collision rate limiting: WORKING (1.00s cooldown applied)

## Protocol Statistics (OpenBC session)
- StateUpdate C->S: 1701
- CollisionEffect: 10
- BeamFire: 10 (all malformed)
- ChecksumResp: 5
- ObjCreateTeam: 2
- SubsysStatus: 2
- HostMsg: 2
- TorpedoFire: 1
- NewPlayerInGame: 1
