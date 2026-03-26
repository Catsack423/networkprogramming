# week10-quantum-network-basic

## Overview
This lab introduces **Conceptual Quantum-Inspired Networking**. Real quantum networking involves entanglement and qubits that literally cannot be copied without destroying their state (No-Cloning Theorem).

Here, we simulate this in software using **One-Time-Read Ephemeral Tokens**:
1. **No-Cloning**: When a node forwards a token, it *must* delete its local copy.
2. **State Collapse**: When a node reads a token's message, the token's boolean state flips permanently to `read = True`. Any subsequent attempt to read it fails.
3. **Decay/Expiry**: Tokens exist in a volatile state. They have a time-to-live before they naturally "collapse" into useless noise.

### Features & Extensions Included
- **Extension A: Expiry Management**: Generates tokens with adjustable expiry via the CLI. The routing loop actively cleans up tokens that have "decayed" while waiting.
- **Extension B: Multi-Hop Routing**: Tokens remember where they've been (the `paths` attribute) to prevent infinite loops as they bounce between nodes looking for a reader.
- **Extension C: Analytics**: `/stats` command shows how many states successfully collapsed via a read vs collapsed due to expiry or interference.

## How to Run

1. Open 3 terminals in this folder.
2. Run standard peers:
   - Terminal 1: `python node.py 11001`
   - Terminal 2: `python node.py 11002`
   - Terminal 3: `python node.py 11003`

3. Generate a Quantum Token:
   - In Terminal 1, type: `/generate "Secret_Meeting" 20` (Generates a token with a 20-second lifespan).

4. Observe the Behavior:
   - Terminal 1 will attempt to offload the state to a neighbor.
   - Wait and watch Terminals 2 and 3. When a node receives the token, it essentially flips a quantum coin (50% probability):
     - **Heads**: It acts as the destination, "collapses" the state by reading the message, and prints `[SECURITY] Successfully un-collapsed...`.
     - **Tails**: It merely acts as a router, storing it in its queue (without reading it) to forward to another node.

5. Inspect State:
   - Type `/stats` on any node to see how many tokens were read vs destroyed.
   - If a token bounces around for 20 seconds without a node deciding to read it, it will organically collapse and be purged from the queues.
