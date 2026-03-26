"""
broadcaster.py — Extension C: Subnet Broadcast Address
Uses the subnet-directed broadcast address (e.g. 192.168.1.255)
instead of the limited broadcast 255.255.255.255.

Key difference:
  255.255.255.255  — limited broadcast, may be dropped by some OS/router stacks
  x.x.x.255       — directed broadcast, subnet-specific, more reliably delivered
"""
import socket
import time
from config import BROADCAST_IP, PORT, BUFFER_SIZE
from subnet import get_subnet_broadcast

# ── resolve broadcast address ─────────────────────────────────────────────────
local_ip, subnet_mask, subnet_bcast = get_subnet_broadcast()

if BROADCAST_IP is None:
    # Auto-detected subnet broadcast
    bcast_addr = subnet_bcast
    mode       = "subnet-directed (auto)"
else:
    # Manual override from config.py
    bcast_addr = BROADCAST_IP
    mode       = "manual override"

print(f"[BROADCASTER] Extension C — Subnet Broadcast")
print(f"[BROADCASTER] Local IP        : {local_ip}")
print(f"[BROADCASTER] Subnet Mask     : {subnet_mask}")
print(f"[BROADCASTER] Broadcast Addr  : {bcast_addr}  ({mode})")
print(f"[BROADCASTER] Port            : {PORT}")
print()
print(f"[BROADCASTER] Compare:")
print(f"  255.255.255.255  → limited broadcast (doesn't cross router hops)")
print(f"  {subnet_bcast:<15}  → directed broadcast (subnet-scoped, more compatible)")
print()

# ── send ─────────────────────────────────────────────────────────────────────
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

round_num = 0
try:
    while True:
        round_num += 1
        ts      = time.strftime("%H:%M:%S")
        message = f"DISCOVERY subnet={subnet_bcast} round={round_num} ts={ts}"

        sock.sendto(message.encode(), (bcast_addr, PORT))
        print(f"[BROADCASTER] [{ts}] → {bcast_addr}:{PORT}  round={round_num}")

        time.sleep(3)

except KeyboardInterrupt:
    print(f"\n[BROADCASTER] Stopped after {round_num} broadcast(s).")

finally:
    sock.close()
