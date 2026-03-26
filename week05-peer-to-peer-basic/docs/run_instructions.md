# Run Instructions: Week 5 Basic P2P

## Prerequisites
- Python 3.x
- Multiple terminal windows.

## Steps

### 1. Start Peer 1
Open a terminal and run:
```bash
python peer.py 1
```
It will listen on port 9001.

### 2. Start Peer 2
Open another terminal and run:
```bash
python peer.py 2
```
It will listen on port 9002.

### 3. Send a Message from Peer 1 to Peer 2
In Peer 1's terminal:
- Enter `2` for peer ID.
- Enter `Hello from Peer 1!` as the message.

### 4. Verify
Check Peer 2's terminal. You should see:
`[PEER 2] Received from ('127.0.0.1', <port>): Hello from Peer 1!`

### 5. Send a Message from Peer 2 to Peer 1
In Peer 2's terminal:
- Enter `1` for peer ID.
- Enter `Hi Peer 1, I got your message!` as the message.

Peer 1's terminal should display the incoming message.

---

## Technical Details
- Each peer calculates its port as `BASE_PORT + peer_id`.
- The `listen()` function runs in a background thread to prevent blocking.
