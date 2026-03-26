# week07-store-forward-planetary

## Overview
The **Planetary Email System** is a simulation of a **Delay-Tolerant Network (DTN)**. In deep-space communication, traditional TCP/IP fails because round-trip times take minutes or hours. 

This system uses a **Bundle-like** store-and-forward approach where each node acts as a "carrier" for messages destined for other planets.

### Advanced Features
- **Latency Simulation**: Transmission delay based on celestial distances (Earth, Moon, Mars).
- **Hop Tracking**: Messages can travel through intermediate nodes (Carriers).
- **Persistent Outbox**: All pending messages are stored in `storage/` and survive node crashes.
- **Adaptive Retry**: Uses exponential backoff to handle long-term link unavailablity.

---

## Directory Structure
- `config.py`: Latency and retry parameters.
- `utils/retry_policy.py`: Class for calculating backoff delays.
- `node/message_queue.py`: Persistent storage for the planetary outbox.
- `node/node.py`: Main entry point (Server + DTN Loop + Shell).

---

## How to Run

1. **Start the Earth Hub**:
   ```bash
   python node.py 0 EARTH
   ```

2. **Start the Mars Rover**:
   ```bash
   python node.py 1 MARS
   ```

3. **Send an Email from Earth to Mars**:
   - In Earth terminal (Node 0): `/send 1 Hello_Mars_Rover!`
   - Observe the Earth node simulating latency and queuing the message.
   
4. **Simulate Earth-Mars Link Restore**:
   - (By default, the simulation assumes the link is "up" but very slow/occasional).
   - If Node 1 is offline, Node 0 will keep retrying with increasingly long intervals.
   - Start Node 1, and watch Node 0 deliver the "Planetary Email" automatically.
