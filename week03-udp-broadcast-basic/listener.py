"""
listener.py — Extension B: Observe Network Noise
Receives periodic broadcast packets and reports:
- Arrival rate (packets/min)
- Inter-arrival gap
- Total bytes received (noise volume)
Press Ctrl+C to print the noise summary.
"""
import socket
import time
from config import PORT, BUFFER_SIZE, BROADCAST_INTERVAL

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(("", PORT))

print(f"[LISTENER] Extension B — Network Noise Observer")
print(f"[LISTENER] Listening on port {PORT}  (Ctrl+C to show noise summary)\n")

recv_times   = []   # perf_counter timestamps
total_bytes  = 0
last_round   = None

try:
    while True:
        data, addr = sock.recvfrom(BUFFER_SIZE)
        t_now  = time.perf_counter()
        ts     = time.strftime("%H:%M:%S")
        msg    = data.decode()
        nbytes = len(data)

        recv_times.append(t_now)
        total_bytes += nbytes

        # inter-arrival gap
        if len(recv_times) >= 2:
            gap = t_now - recv_times[-2]
            gap_str = f"  gap={gap:.2f}s"
        else:
            gap_str = "  gap=--"

        print(f"[LISTENER] [{ts}] #{len(recv_times):>4}  from {addr[0]}  {nbytes}B{gap_str}  '{msg}'")

except KeyboardInterrupt:
    pass

finally:
    n = len(recv_times)
    if n < 2:
        print("\n[LISTENER] Not enough data to compute noise stats.")
    else:
        elapsed  = recv_times[-1] - recv_times[0]
        rate_ppm = (n - 1) / elapsed * 60 if elapsed > 0 else 0
        gaps     = [recv_times[i+1] - recv_times[i] for i in range(n-1)]
        avg_gap  = sum(gaps) / len(gaps)
        max_gap  = max(gaps)
        min_gap  = min(gaps)

        print()
        print("=" * 55)
        print("  NETWORK NOISE REPORT")
        print("=" * 55)
        print(f"  Broadcasts received  : {n}")
        print(f"  Total duration       : {elapsed:.1f}s")
        print(f"  Arrival rate         : {rate_ppm:.1f} packets/min")
        print(f"  Expected interval    : {BROADCAST_INTERVAL}s")
        print(f"  Avg inter-gap        : {avg_gap:.3f}s")
        print(f"  Min / Max gap        : {min_gap:.3f}s / {max_gap:.3f}s")
        print(f"  Total bytes received : {total_bytes} B  ({total_bytes/1024:.2f} KB)")
        print(f"  Bandwidth consumed   : {total_bytes/elapsed:.1f} B/s  (noise floor)")
        print("=" * 55)
        if max_gap > BROADCAST_INTERVAL * 2:
            print("  ⚠  Large gap detected — possible packet loss!")
        else:
            print("  ✓  Broadcast arrived consistently.")
        print("=" * 55)

    sock.close()
