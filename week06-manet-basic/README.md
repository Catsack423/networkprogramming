# week06-manet-basic

## Overview
This lab simulates a **Mobile Ad-Hoc Network (MANET)**. In this model, there is no central router. Each node is responsible for discovering its neighbors and deciding whether to forward (relay) messages to others.

### Key Features
- **Neighbor Discovery**: Nodes automatically find each other by scanning a port range (7000-7010).
- **Probabilistic Forwarding**: To prevent network congestion, each node has a limited chance (e.g., 60%) to relay a packet.
- **TTL (Time To Live)**: Packets carry a counter that decrements each hop. When it hits 0, the packet is dropped to prevent infinite loops.
- **Mobility Simulation**: Nodes randomly "move out of range" by dropping neighbors from their local table.

---

## How to Run

1. **Start multiple nodes**: Open 3-4 terminals and run:
   - Terminal 1: `python node.py 7000`
   - Terminal 2: `python node.py 7001`
   - Terminal 3: `python node.py 7002`

2. **Wait for discovery**: Within 5 seconds, nodes will find each other. Type `/peers` to check.

3. **Send a message**:
   - In Terminal 1: `/send Hello Mesh!`
   - Observe which other terminals receive it. Due to probabilistic forwarding, some might not!

4. **Check stats**:
   - Type `/stats` to see how many messages were received vs. forwarded.
