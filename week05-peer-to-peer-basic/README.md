# week05-peer-to-peer-basic

## Overview
This lab introduces **Peer-to-Peer (P2P)** networking. In a P2P system, there is no fixed server or client. Every node (peer) has a symmetric role:
- **Server Activity**: Listening for incoming TCP connections from other peers.
- **Client Activity**: Initiating outbound TCP connections to send messages to other peers.

### Key Concepts
- **Symmetry**: All nodes run the same code and have the same capabilities.
- **Concurrency**: Using `threading` to handle background listening while the main thread waits for user input.
- **Dynamic Identification**: Peers identify each other by their ID, which maps to a unique port number.

---

## Directory Structure
- `config.py`: Shared base settings (Host, Base Port).
- `peer.py`: The implementation of a P2P node.
- `docs/run_instructions.md`: Step-by-step guide to testing.
