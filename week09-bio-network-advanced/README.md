# week09-bio-network-advanced

## Overview
This is the **Self-Healing Network Simulator**. It applies Ant-Colony Optimization to a mesh network where links are constantly dropping and recovering (simulating moving sensors, disaster zones, or interference).

### Advanced Features
- **Target-Aware Pheromones**: Unlike basic broadcast, the pheromone table maps `Target -> Neighbor -> Strength`. It answers: "To get to Node Z, how good is Node Y right now?"
- **Encounter Simulator**: A background thread randomly 'flaps' links (turns them on/off) to force the routing algorithm to adapt.
- **Negative Reinforcement (Penalties)**: If a link is physically down, the node penalizes the pheromone score for that neighbor, helping it "unlearn" bad routes much faster than standard decay.
- **Data Logging**: All major events (Decay, Reinforcement, Environmental Shifts) are logged to `logs/node_X.jsonl` for offline analysis.

---

## Directory Structure
- `config.py`: Simulation and Ant-colony math parameters.
- `utils/logger.py`: JSONL logging utility.
- `node/pheromone_table.py`: Advanced multi-dimensional routing table.
- `node/encounter_simulator.py`: Random environment flapper.
- `node/node.py`: Main mesh entry point.

---

## How to Run

1. **Start the Simulator Nodes**:
   Open 3 terminals. You must tell each node who its peers are.
   - Node 0: `python node.py 0 1 2`
   - Node 1: `python node.py 1 0 2`
   - Node 2: `python node.py 2 0 1`

2. **Observe the Flapping Environment**:
   - You will see outputs like `Environment Shift! Active Links: [1]`. This means Node 0 can currently ONLY talk to Node 1.

3. **Send a Message (Multi-Hop)**:
   - In Node 0: `/send 2 Find_Route_To_2`
   - Watch the logs. If Node 0 cannot reach Node 2 directly, it will explore and send to Node 1. Node 1 will then queue it, and eventually forward it to Node 2 when their link becomes active.
   
4. **View Routing Brain**:
   - Type `/table` to see how the node is currently valuing its neighbors for different ultimate destinations.
