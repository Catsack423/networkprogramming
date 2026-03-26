# week08-opportunistic-advanced

## Overview
The **Content Diffusion Mesh** is an advanced opportunistic routing system designed for **Post-Disaster Data Sharing**. When centralized servers are down, important data (maps, photos, injury reports) must find its way across a fragmented network of mobile devices.

### Advanced Features
- **3-Way Handshake Sync**: Nodes exchange "Hellos", compare catalogs, and only push the delta (missing data) to conserve battery and bandwidth.
- **Priority-Aware Diffusion**: High-priority bundles (e.g., Medical Alerts) are prioritized during the sync process.
- **Anti-entropy Pushing**: Nodes actively "push" new data to neighbors as they encounter them.
- **Persistent Data Bundles**: All shared content is stored in `storage/` and persists across reboots.

---

## Directory Structure
- `config.py`: Mesh and sync parameters.
- `node/bundle_manager.py`: Logic for creating and integrating data bundles.
- `node/sync_protocol.py`: Protocol definitions for HELLO and DATA exchange.
- `node/node.py`: Main entry point (Server + Sync Loop + Shell).

---

## How to Run

1. **Start the Command Post**:
   ```bash
   python node.py 0
   ```

2. **Start Field Personnel Nodes**:
   ```bash
   python node.py 1
   python node.py 2
   ```

3. **Share Data from an Isolated Node**:
   - In Node 2 terminal: `/share MAPS "Sector 4 Cleared"`
   - Node 2 will now wait to "encounter" another node.
   
4. **Simulate Encounters**:
   - (The simulation uses random scanning). Within 10-20 seconds, Node 2 should find Node 1 or Node 0.
   - Observe Node 2 pushing the bundle to the others.
   - Check the catalog on any node: `/catalog`
