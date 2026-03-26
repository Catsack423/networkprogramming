"""
sender.py — Extension C: Rate Control
Sends TOTAL_PACKETS at a fixed rate of SEND_RATE_PPS packets/second.
Uses a high-precision timer loop to maintain consistent inter-packet gap.
Measures actual achieved throughput and jitter.
"""
import socket
import json
import time
from config import HOST, PORT, BUFFER_SIZE, TOTAL_PACKETS, SEND_RATE_PPS, SEND_INTERVAL

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print(f"[SENDER] Extension C — Rate Control")
print(f"[SENDER] Target rate : {SEND_RATE_PPS} pps  ({SEND_INTERVAL*1000:.1f} ms/packet)")
print(f"[SENDER] Total       : {TOTAL_PACKETS} packets → {HOST}:{PORT}\n")

sent_times = []   # record actual send timestamps for jitter analysis
start_time = time.perf_counter()

for seq in range(1, TOTAL_PACKETS + 1):
    # ── precision rate limiter ────────────────────────────────────────────────
    # target time for this packet based on start
    target_time = start_time + (seq - 1) * SEND_INTERVAL
    now = time.perf_counter()
    if target_time > now:
        time.sleep(target_time - now)   # sleep only the remainder

    payload = json.dumps({
        "seq":   seq,
        "total": TOTAL_PACKETS,
        "msg":   f"Packet #{seq}",
        "ts":    time.time(),
    }).encode()

    sock.sendto(payload, (HOST, PORT))
    t = time.perf_counter()
    sent_times.append(t)

    if seq == 1 or seq % 25 == 0 or seq == TOTAL_PACKETS:
        elapsed  = t - start_time
        actual_pps = seq / elapsed if elapsed > 0 else 0
        print(f"[SENDER] seq={seq:>3}/{TOTAL_PACKETS}  elapsed={elapsed:.2f}s  actual={actual_pps:.1f} pps")

total_elapsed = sent_times[-1] - sent_times[0] if len(sent_times) > 1 else 0

# ── jitter calculation (difference between consecutive inter-packet gaps) ──
gaps    = [sent_times[i+1] - sent_times[i] for i in range(len(sent_times)-1)]
avg_gap = sum(gaps) / len(gaps) if gaps else 0
jitter  = max(abs(g - avg_gap) for g in gaps) if gaps else 0

# ── summary ───────────────────────────────────────────────────────────────────
print()
print("=" * 55)
print("  SENDER SUMMARY")
print("=" * 55)
print(f"  Packets sent     : {TOTAL_PACKETS}")
print(f"  Target rate      : {SEND_RATE_PPS} pps")
print(f"  Actual rate      : {(TOTAL_PACKETS-1)/total_elapsed:.1f} pps" if total_elapsed > 0 else "  Actual rate      : N/A")
print(f"  Total duration   : {total_elapsed:.3f} s")
print(f"  Avg gap          : {avg_gap*1000:.2f} ms  (target {SEND_INTERVAL*1000:.2f} ms)")
print(f"  Max jitter       : {jitter*1000:.2f} ms")
print("=" * 55)

sock.close()
