# week08-opportunistic-basic

## Overview
This lab implements **Opportunistic Routing** using an **Epidemic Sync** protocol with **Spray-and-Wait** copy control.

In this model, nodes don't search for a "route" to a specific destination. Instead, they "infect" any neighbor they meet with new messages, ensuring that data eventually diffuses through the network even if there is no end-to-end path at any single moment.

### Key Features
- **Anti-entropy Sync**: Nodes periodically exchange message inventories and pull/push missing data.
- **Spray-and-Wait (K-copy)**: To avoid infinite flooding, each message starts with a fixed number of "tickets" (copies). When a node sends a message to another, it splits its tickets with the recipient. Once a node has 1 ticket left, it only delivers the message to the final destination (if known).
- **Persistent Message Store**: All messages are saved to `store_<port>.json`.

---

## How to Run

1. **Start 3 nodes**:
   - Terminal 1: `python node.py 9000`
   - Terminal 2: `python node.py 9001`
   - Terminal 3: `python node.py 9002`

2. **Create a message**:
   - In Terminal 1: `/msg Hello_Everyone`
   - Terminal 1 will now attempt to sync this message whenever it "meets" another node (simulated by random scanning).

3. **Observe Diffusion**:
   - Within 10-20 seconds, the message should appear in the lists of Terminals 2 and 3.
   - Check with: `/list`

4. **Observe Spray-and-Wait**:
   - See how the `copies_left` count decreases as the message spreads across the network.
