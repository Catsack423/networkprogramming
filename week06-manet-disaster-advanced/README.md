# week06-manet-disaster-advanced

## Overview
The **Disaster Response Mesh** is an advanced MANET simulation designed for search and rescue scenarios. In disaster zones where standard infrastructure (cell towers, fiber) is destroyed, mobile devices form an ad-hoc mesh to relay critical alerts.

### Advanced Features
- **Neighbor Management**: Nodes dynamically track neighbors based on periodic pings and discovery on packet reception.
- **Role-Based Messaging**: Nodes can assume roles (Rescue Team, Victim, HQ) which are tagged in every packet.
- **Routing Metrics**: Each node tracks duplicates, successful relays, and uptime to measure network health.
- **History Tracking**: Robust deduplication ensures that same alerts don't loop indefinitely.

---

## Directory Structure
- `config.py`: Mesh and routing parameters.
- `utils/routing_metrics.py`: Class for tracking delivery statistics.
- `node/neighbor_manager.py`: Handles dynamic topology discovery.
- `node/message_forwarder.py`: Logic for probabilistic relay and TTL.
- `node/node.py`: Main entry point.

---

## How to Run

1. **Start the HQ**:
   ```bash
   python node.py 7500 2
   ```

2. **Start Rescue Teams**:
   ```bash
   python node.py 7501 0
   python node.py 7502 0
   ```

3. **Start Victims**:
   ```bash
   python node.py 7503 1
   ```

4. **Verify Mesh**:
   - In any terminal, type `/peers` to see discovered neighbors.
   - Send an alert: `/alert Help! Trapped in sector 4.`
   - Check statistics on any node: `/stats`
