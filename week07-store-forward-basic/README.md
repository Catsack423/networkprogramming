# week07-store-forward-basic

## Overview
This lab implements **Store-and-Forward** communication. In unreliable networks, nodes must be able to queue messages when the recipient is offline and retry later.

### Key Features
- **Persistent Queuing**: Messages are saved to `queue_<port>.json`. They survive node restarts.
- **Priority Support**: High-priority messages (e.g., emergency alerts) move to the front of the queue.
- **Exponential Backoff**: If a delivery fails, the node waits longer before the next attempt (5s -> 10s -> 20s -> ... up to 60s) to avoid flooding the network.
- **Async Retries**: A background thread handles retries without blocking the user interface.

---

## How to Run

1. **Start two nodes**:
   - Terminal 1: `python node.py 8000`
   - Terminal 2: `python node.py 8001`

2. **Test instant delivery**:
   - In Terminal 1: `/send 8001 Hello_Basic`

3. **Test Store-and-Forward**:
   - Close Terminal 2 (`/exit`).
   - In Terminal 1: `/send 8001 Urgent_Message 10` (Priority 10)
   - In Terminal 1: `/send 8001 Normal_Message 1` (Priority 1)
   - Check the queue: `/list` (Observe Urgent is at the top).

4. **Restore link**:
   - Start Terminal 2 again: `python node.py 8001`
   - Observe Terminal 1 delivering the stored messages automatically within 5-10 seconds.
