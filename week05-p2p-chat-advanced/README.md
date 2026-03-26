# week05-p2p-chat-advanced

## Overview
This lab implements a **Decentralized Chat Overlay**. Each node acts as a message router, forwarding (flooding) chat messages to all its known neighbors. This allows messages to reach nodes that are not directly connected.

### Advanced Concepts
- **Overlay Network**: A logical network built on top of another network (TCP/IP).
- **Message Flooding**: A simple routing algorithm where every incoming message is sent out to all neighbors (except the sender).
- **Peer Discovery**: Nodes "announce" themselves to a known neighbor to join the network and build their local peer table.
- **Deduplication**: The router keeps a history of message IDs to prevent infinite loops in the network.

---

## Directory Structure
- `config.py`: Global port and buffer settings.
- `utils/protocol.py`: JSON message framing.
- `peer_table.py`: Thread-safe storage for known neighbors.
- `router.py`: Logic for message forwarding and history tracking.
- `node.py`: Main entry point for the P2P chat node.

---

## How to Run

### 1. Start the first node (seed)
```bash
python node.py Alice 10001
```

### 2. Start a second node and join Alice
```bash
python node.py Bob 10002 10001
```

### 3. Start a third node and join Bob
```bash
python node.py Charlie 10003 10002
```

### 4. Test Chat
Message flooding ensures that if Alice sends a message, it reaches Bob (direct) and Charlie (via Bob's forward), even if Alice and Charlie aren't directly connected.
- Type a message and press Enter to broadcast.
- Type `/peers` to see who this node knows.
- Type `/exit` to shutdown.
