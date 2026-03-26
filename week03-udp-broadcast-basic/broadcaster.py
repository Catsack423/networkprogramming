"""
broadcaster.py — Extension A: Broadcast Discovery + Reply
1. Sends a broadcast DISCOVERY message to all nodes.
2. Opens REPLY_PORT and collects unicast replies from each listener.
3. Prints a summary of nodes that responded.
"""
import socket
import threading
from config import BROADCAST_IP, PORT, BUFFER_SIZE, REPLY_PORT, REPLY_TIMEOUT

responders = []        # list of (ip, hostname) that replied
lock       = threading.Lock()


def collect_replies():
    """Listen for unicast replies on REPLY_PORT until timeout."""
    reply_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    reply_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    reply_sock.bind(("", REPLY_PORT))
    reply_sock.settimeout(REPLY_TIMEOUT)

    print(f"[BROADCASTER] Listening for replies on port {REPLY_PORT} ({REPLY_TIMEOUT}s)...")

    while True:
        try:
            data, addr = reply_sock.recvfrom(BUFFER_SIZE)
            msg = data.decode()
            with lock:
                responders.append((addr[0], msg))
            print(f"[BROADCASTER] ← Reply from {addr[0]} : '{msg}'")
        except socket.timeout:
            break

    reply_sock.close()


# ── Step 1: start reply collector thread BEFORE broadcasting ─────────────────
collector = threading.Thread(target=collect_replies, daemon=False)
collector.start()

# Small yield so the collector socket is bound before the broadcast fires
import time; time.sleep(0.05)

# ── Step 2: send broadcast ───────────────────────────────────────────────────
bcast_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
bcast_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

message = "DISCOVERY: Who is online?"
bcast_sock.sendto(message.encode(), (BROADCAST_IP, PORT))
bcast_sock.close()
print(f"[BROADCASTER] → Broadcast sent: '{message}'\n")

# ── Step 3: wait for collector to finish ─────────────────────────────────────
collector.join()

# ── Summary ───────────────────────────────────────────────────────────────────
print()
print("=" * 45)
print("  DISCOVERY RESULTS")
print("=" * 45)
if responders:
    for i, (ip, msg) in enumerate(responders, 1):
        print(f"  {i}. {ip:<16}  → '{msg}'")
else:
    print("  No nodes replied within the timeout window.")
print(f"\n  Total responders: {len(responders)}")
print("=" * 45)
