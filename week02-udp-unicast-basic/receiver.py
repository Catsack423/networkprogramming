# Extension A — Sequence Number Receiver
import socket
import json
import time
from config import HOST, PORT, BUFFER_SIZE

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((HOST, PORT))
sock.settimeout(3.0)   # stop waiting 3s after the last packet arrives

print(f"[RECEIVER] Extension A — Listening on {HOST}:{PORT}")
print("[RECEIVER] Tracking sequence numbers (Ctrl+C or 3s idle to show report)\n")

received_seqs = []   # list of seq numbers we actually got
expected_next = 1    # what we expect to arrive next

try:
    while True:
        try:
            data, addr = sock.recvfrom(BUFFER_SIZE)
        except socket.timeout:
            print("[RECEIVER] No packet for 3s — assuming sender is done.\n")
            break

        try:
            pkt = json.loads(data.decode())
        except json.JSONDecodeError:
            print(f"[RECEIVER] ⚠  Non-JSON packet from {addr}: {data[:40]}")
            continue

        seq   = pkt.get("seq")
        total = pkt.get("total", "?")
        msg   = pkt.get("msg", "")

        received_seqs.append(seq)

        # Detect gap vs in-order
        if seq == expected_next:
            status = "✓"
        elif seq > expected_next:
            missing = list(range(expected_next, seq))
            status  = f"⚠  GAP — missing {missing}"
        else:
            status = f"↩  OUT-OF-ORDER (expected {expected_next})"

        print(f"[RECEIVER] seq={seq}/{total}  {status}  | '{msg}'")

        # Advance expected pointer (handles in-order case)
        if seq >= expected_next:
            expected_next = seq + 1

except KeyboardInterrupt:
    print("\n[RECEIVER] Interrupted.")

finally:
    # ── Summary Report ────────────────────────────────────────────────────────
    received_set = set(received_seqs)
    total_sent   = max(received_seqs) if received_seqs else 0
    expected_set = set(range(1, total_sent + 1))
    missing      = sorted(expected_set - received_set)
    duplicates   = [s for s in received_seqs if received_seqs.count(s) > 1]

    print("=" * 55)
    print("  SUMMARY REPORT")
    print("=" * 55)
    print(f"  Packets received : {len(received_seqs)}")
    print(f"  Highest seq seen : {total_sent}")
    print(f"  Missing packets  : {missing if missing else 'None'}")
    print(f"  Duplicates       : {list(set(duplicates)) if duplicates else 'None'}")
    loss_pct = (len(missing) / total_sent * 100) if total_sent else 0
    print(f"  Packet loss      : {loss_pct:.1f}%")
    print("=" * 55)
    sock.close()
