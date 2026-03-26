# week09-bio-routing-basic

## Overview
This lab simulates **Ant-Colony Optimization** for network routing. Instead of hardcoding paths or using complex state-tracking protocols like OSPF, nodes rely on **Pheromones**.

When a node successfully sends a message to a neighbor, it reinforces that path (adds pheromone). Over time, all paths naturally evaporate (decay). This creates a self-optimizing system where fast, reliable routes organically attract the most traffic.

### Extensions Included
- **Extension A: Dynamic Learning**: Nodes track Round-Trip Time (RTT) of the ACK packet. Faster nodes get a higher pheromone bonus.
- **Extension B: Multi-Hop**: If a node receives a packet meant for someone else, it stores it in a queue and uses its own pheromone table to forward it later.
- **Extension C: Visualization**: Run the node with `--plot` to see a live Matplotlib bar chart of the pheromone tables evolving.

---

## How to Run

1. **Install requirements** (for the plot extension):
   ```bash
   pip install matplotlib
   ```

2. **Start the Network**:
   Open 3 terminals:
   - Terminal 1: `python node.py 10001 --plot`
   - Terminal 2: `python node.py 10002`
   - Terminal 3: `python node.py 10003`

3. **Check Initial State**:
   - In Terminal 1, type `/table`. You'll see initial pheromones for 10002 and 10003 (value: `1.0`).
   - Wait a few seconds and run `/table` again. Notice how the values are shrinking (Decay).

4. **Reinforce paths**:
   - In Terminal 1: `/msg 10002 Hello_Path_A`
   - Every time this succeeds, the pheromone value for `10002` will jump up (Reinforcement).
   - If you have the `--plot` flag active, you will see the green bar for `10002` spike rapidly.

5. **Simulate Network Failure**:
   - Close Terminal 2 (`Ctrl+C`).
   - Try to send to 10002 again from Terminal 1. It will fail, queue the message, and the pheromone for `10002` will continue to decay until it drops below the threshold.
