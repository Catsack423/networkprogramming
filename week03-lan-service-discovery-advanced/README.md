# Week 3 Advanced — LAN Service Discovery Tool

> **Course**: Network Programming · Week 3 · Advanced Lab  
> **Topic**: UDP Broadcast + Unicast Reply + Service Registry

---

## Overview

This lab transforms raw UDP broadcast into a **controlled service-discovery system** — the kind real protocols like mDNS/Zeroconf and DHCP use under the hood.

| Component | File | Role |
|-----------|------|------|
| Shared config | `config.py` | Ports, TTL, intervals |
| Message utilities | `utils/message.py` | JSON encode/decode |
| Announcer | `discovery/announcer.py` | Broadcasts service presence |
| Responder | `discovery/responder.py` | Listens and replies via unicast |
| Registry | `registry/registry.py` | Tracks active services + TTL expiry |

---

## Directory Structure

```
week03-lan-service-discovery-advanced/
├── README.md
├── config.py
├── discovery/
│   ├── announcer.py
│   └── responder.py
├── registry/
│   └── registry.py
└── utils/
    └── message.py
```

---

## Key Concepts

| Concept | Description |
|---------|-------------|
| **UDP Broadcast** | One packet → all nodes on the LAN segment |
| **Unicast Reply** | Responder sends a targeted reply back to the announcer |
| **Soft State** | Registry entries expire unless refreshed (TTL-based) |
| **SO_BROADCAST** | Socket option required to send broadcast datagrams |

---

## How to Run

### Prerequisites
- Python 3.10+
- All machines on the **same LAN / subnet**
- No special libraries required (stdlib only)

### Step 1 — Start one or more Responders

Run this on each node that wants to **respond** to service announcements:

```bash
python discovery/responder.py --name DatabaseServer --type PostgreSQL
```

```bash
python discovery/responder.py --name WebServer --type HTTP
```

### Step 2 — Start the Announcer

Run this on the node offering a service:

```bash
python discovery/announcer.py --name AppServer --type Flask --interval 5
```

### Expected Output

**Announcer terminal:**
```
[ANNOUNCER] Starting — service='AppServer' type='Flask' interval=5.0s
[ANNOUNCER] Broadcasting to 255.255.255.255:7100
[ANNOUNCER] → Broadcast sent  (120 bytes)
[ANNOUNCER] Active peers in registry: 2
  SERVICE NAME              TYPE                 HOST                 IP               AGE (s)
  -------------------------------------------------------------------------------------------------
  DatabaseServer            PostgreSQL           HOST-A               192.168.1.5      1
  WebServer                 HTTP                 HOST-B               192.168.1.8      1
```

**Responder terminal:**
```
[RESPONDER] 'DatabaseServer' (PostgreSQL) — listening for broadcasts on port 7100
[RESPONDER] ← Announcement from 192.168.1.10 | 'AppServer' (Flask) on host 'HOST-C'
[RESPONDER] → Unicast reply sent to 192.168.1.10:7101
```

---

## Configuration (`config.py`)

| Variable | Default | Description |
|----------|---------|-------------|
| `BROADCAST_IP` | `255.255.255.255` | Limited broadcast address |
| `PORT` | `7100` | Announcer broadcasts to this port |
| `REPLY_PORT` | `7101` | Responders send unicast replies here |
| `ANNOUNCE_INTERVAL` | `5` s | How often the announcer broadcasts |
| `ENTRY_TTL` | `15` s | Stale entry expiration window |

---

## Flow Diagram

```
Announcer                          (All LAN nodes)
    |                                    |
    |──── UDP BROADCAST (PORT 7100) ────>|  ← every 5s
    |                                    |
    |<─── UDP UNICAST REPLY (PORT 7101)──|  Responder 1
    |<─── UDP UNICAST REPLY (PORT 7101)──|  Responder 2
    |                                    |
    |   Registry updated + TTL checked   |
```

---

## Common Mistakes

| Mistake | Effect | Fix |
|---------|--------|-----|
| Forgetting `SO_BROADCAST` | Packet silently dropped | Set before `sendto` |
| Nodes on different subnets | Broadcast doesn't route | Use mDNS or unicast mesh |
| No TTL / expiry logic | Dead nodes stay in registry forever | Implement soft state |
| Blocking reply port | Announcer misses replies | Run reply listener in a thread |

---

## Real-World Mapping

| This Lab | Real Protocol |
|----------|--------------|
| Broadcast ANNOUNCE | DHCP Discover / mDNS Query |
| Unicast REPLY | DHCP Offer / mDNS Answer |
| Registry + TTL | DNS-SD service cache |

---

## Extension Ideas

- **Subnet broadcast** — replace `255.255.255.255` with your subnet's broadcast address  
- **Service filtering** — responders only reply to matching `service_type`  
- **GUI dashboard** — render the registry in a terminal table refreshed with `curses`  
- **Multi-announcer mesh** — multiple announcers, each collecting a combined registry  
