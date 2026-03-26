"""
receiver.py — Extension C: Rate Control / Saturation Observation
Tracks arrival rate, inter-packet gaps, dropped packets, and queue pressure.
Prints a live rate ticker and a final saturation report.
"""
import socket
import json
import time
from config import HOST, PORT, BUFFER_SIZE, TOTAL_PACKETS, RECV_QUEUE_WARN

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind((HOST, PORT))
sock.settimeout(3.0)   # 3s idle → done

print(f"[RECEIVER] Extension C — Rate Saturation Observer")
print(f"[RECEIVER] Listening on {HOST}:{PORT}  (expecting ~{TOTAL_PACKETS} packets)\n")

recv_times    = []    # perf_counter timestamps of each arrival
received_seqs = []
expected_next = 1
drop_count    = 0

try:
    while True:
        try:
            raw, addr = sock.recvfrom(BUFFER_SIZE)
        except socket.timeout:
            print("[RECEIVER] Idle 3s — sender done.\n")
            break

        t_arrive = time.perf_counter()
        recv_times.append(t_arrive)

        try:
            pkt = json.loads(raw.decode())
        except json.JSONDecodeError:
            continue

        seq   = pkt.get("seq", -1)
        total = pkt.get("total", "?")
        received_seqs.append(seq)

        # ── gap / drop detection ────────────────────────────────────────────────
        if seq > expected_next:
            gap       = seq - expected_next
            drop_count += gap
            gap_warn  = f"  ⚠  GAP +{gap} (seq {expected_next}–{seq-1} missing)"
        else:
            gap_warn  = ""

        if seq >= expected_next:
            expected_next = seq + 1

        # ── live rate ticker (every 25 packets) ────────────────────────────────
        n = len(recv_times)
        if n >= 2 and (n == 1 or n % 25 == 0 or seq == TOTAL_PACKETS):
            window    = recv_times[-25:] if n >= 25 else recv_times
            w_elapsed = window[-1] - window[0]
            rate      = (len(window) - 1) / w_elapsed if w_elapsed > 0 else 0
            print(f"[RECEIVER] seq={seq:>3}/{total}  rate≈{rate:.1f} pps{gap_warn}")
        elif gap_warn:
            print(f"[RECEIVER] seq={seq:>3}/{total}{gap_warn}")

except KeyboardInterrupt:
    print("\n[RECEIVER] Interrupted.")

finally:
    n           = len(recv_times)
    total_time  = recv_times[-1] - recv_times[0] if n > 1 else 0
    avg_rate    = (n - 1) / total_time if total_time > 0 else 0

    # inter-arrival jitter
    gaps         = [recv_times[i+1] - recv_times[i] for i in range(n-1)]
    avg_gap      = sum(gaps) / len(gaps) if gaps else 0
    max_gap      = max(gaps) if gaps else 0
    jitter       = max(abs(g - avg_gap) for g in gaps) if gaps else 0

    # saturation heuristic: % of gaps that are 2× the average (backlog building)
    slow_gaps    = sum(1 for g in gaps if g > 2 * avg_gap)
    saturation   = slow_gaps / len(gaps) * 100 if gaps else 0

    print("=" * 55)
    print("  RECEIVER SATURATION REPORT")
    print("=" * 55)
    print(f"  Packets received : {n}")
    print(f"  Missing / dropped: {drop_count}")
    print(f"  Loss rate        : {drop_count/(n+drop_count)*100:.1f}%" if (n+drop_count) > 0 else "  Loss rate        : 0%")
    print(f"  Total duration   : {total_time:.3f} s")
    print(f"  Avg arrival rate : {avg_rate:.1f} pps")
    print(f"  Avg inter-gap    : {avg_gap*1000:.2f} ms")
    print(f"  Max inter-gap    : {max_gap*1000:.2f} ms  ← large = backpressure")
    print(f"  Jitter           : {jitter*1000:.2f} ms")
    print(f"  Saturation index : {saturation:.1f}%  ({slow_gaps} slow gaps)")
    if saturation > 20:
        print("  ⚠  HIGH SATURATION — receiver is falling behind the sender!")
    else:
        print("  ✓  Receiver kept up with sender rate.")
    print("=" * 55)
    sock.close()

