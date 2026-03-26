"""
broadcaster.py — Extension B: Periodic Broadcast
Sends a DISCOVERY broadcast every BROADCAST_INTERVAL seconds.
Each broadcast includes a round counter so receivers can observe the pattern.
Press Ctrl+C to stop.
"""
import socket
import time
from config import BROADCAST_IP, PORT, BROADCAST_INTERVAL, MAX_BROADCASTS

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

stop_after = MAX_BROADCASTS if MAX_BROADCASTS > 0 else float("inf")

print(f"[BROADCASTER] Extension B — Periodic Broadcast")
print(f"[BROADCASTER] Interval : {BROADCAST_INTERVAL}s  |  Target: {BROADCAST_IP}:{PORT}")
print(f"[BROADCASTER] Rounds   : {'∞ (Ctrl+C to stop)' if stop_after == float('inf') else MAX_BROADCASTS}\n")

round_num   = 0
total_bytes = 0

try:
    while round_num < stop_after:
        round_num += 1
        ts      = time.strftime("%H:%M:%S")
        message = f"DISCOVERY round={round_num} ts={ts}"

        sock.sendto(message.encode(), (BROADCAST_IP, PORT))
        total_bytes += len(message)

        print(f"[BROADCASTER] [{ts}] → Round {round_num:>4}  '{message}'")

        time.sleep(BROADCAST_INTERVAL)

except KeyboardInterrupt:
    pass

finally:
    print(f"\n[BROADCASTER] Stopped after {round_num} broadcast(s).")
    print(f"[BROADCASTER] Total bytes sent: {total_bytes} B  "
          f"({total_bytes/1024:.2f} KB)  — network noise from this node")
    sock.close()
