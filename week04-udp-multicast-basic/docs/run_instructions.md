# Run Instructions: Week 4 Basic Multicast

## Prerequisites
- Python 3.x
- At least one machine (or multiple terminal windows on the same machine).

## Steps

### 1. Start the Receiver(s)
Open one or more terminals and run:
```bash
python receiver.py
```
You should see: `[RECEIVER] Joined 224.1.1.1:8000`.

### 2. Run the Sender
In a separate terminal, run:
```bash
python sender.py
```
The sender will transmit one message to the group and exit.

### 3. Verify
All active receivers should print the message simultaneously:
`[RECEIVER] Received from ('127.0.0.1', <port>): MULTICAST: Hello subscribers! ...`

---

## Common Issues
- **Firewall**: Some firewalls block IGMP or multicast traffic.
- **Network Interface**: If you have multiple network interfaces (Wi-Fi, Ethernet, VPN), the Python `socket.INADDR_ANY` might bind to the wrong one.
- **TTL**: If the sender and receiver are on different subnets, increase `TTL` in `config.py`.
