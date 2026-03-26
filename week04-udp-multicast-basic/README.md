# week04-udp-multicast-basic

## Overview
This lab introduces **IP Multicast** using UDP. Unlike broadcast (which sends to everyone on the LAN) or unicast (which sends to one specific IP), multicast sends data to a specific **multicast group address**. Only hosts that have explicitly joined the group will receive the data.

### Key Concepts
- **Multicast Group**: A special range of IP addresses (224.0.0.0 to 239.255.255.255).
- **TTL (Time-To-Live)**: Controls how many "hops" a multicast packet can travel. TTL=1 stays within the local network segment.
- **Group Membership**: Managed via the IGMP protocol (Internet Group Management Protocol) under the hood.

---

## Directory Structure
- `config.py`: Port, multicast group, and TTL settings.
- `receiver.py`: The client that joins the group and waits for data.
- `sender.py`: The server that pushes data to the group.
- `docs/run_instructions.md`: Detailed setup guide.
