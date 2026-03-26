# week10-quantum-messenger-advanced

## Overview
This is the **Quantum-Secure Messenger Simulation**. It expands on the basic quantum token concept by modeling environmental interference and adding basic cryptographic constraints.

### Features
- **Cryptographic State Signatures**: Tokens contain a SHA-256 hash representing their unobserved state. Any unauthorized tampering or observation destroys the state and renders the token unreadable (`node/token.py`).
- **Environmental Collapse**: As tokens hop through the network, the `StateManager` occasionally forces them to collapse randomly based on `STATE_COLLAPSE_PROB` (simulating quantum decoherence).
- **Hop Degradation & Expiry**: Tokens degrade if they pass through too many nodes (`MAX_HOPS`) or exist too long (`TOKEN_LIFESPAN`), modeling the difficulty of long-distance quantum entanglement.
- **Detailed Audit Logging**: Every state transition (Gen, Forward, Reject, Collapse, Succeed) is written to a JSONL log file tracing exactly what happened to every token in the system without manually observing the live output.

## How to Run
1. Start 3 Mesh Nodes in multiple terminals. You must pass their node_id and the peers they know about.
   - Node 0: `python node.py 0 1 2`
   - Node 1: `python node.py 1 0 2`
   - Node 2: `python node.py 2 0 1`

2. Send a Quantum Message:
   - On Node 0, type: `/send 2 TopSecretData`
   
3. Observe Network Behavior:
   - Because the forwarding takes immediate effect via threads, Node 0 might send it directly to Node 2, or indirectly via Node 1.
   - If you send a lot of traffic, you will eventually see environmental inference destroy some tokens mid-flight, simulating quantum decoherence: `[NODE X] Received quantum state Y heading for Z... [FAILED_READ] State Collapsed: ENVIRONMENTAL_COLLAPSE`.

4. Check Quantum State Memory:
   - Type `/stats` on any node to see how many unique tokens it's processed and how many are currently resting in its memory buffers.
   
5. Inspect Offline Analytics:
   - Look at `logs/quantum_node_0.jsonl` to see a full time-series trace of the token's lifetime.
