"""
receiver.py — Extension B: Manual ACK
Listens for data packets, sends unicast ACK for each one.
Detects and ignores duplicate packets (retransmits from sender).
"""
import socket
import json
from config import HOST, PORT, ACK_PORT, BUFFER_SIZE

# ── data socket ───────────────────────────────────────────────────────────────────
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind((HOST, PORT))
sock.settimeout(5.0)   # quit 5s after last packet

print(f"[RECEIVER] Extension B — Listening on {HOST}:{PORT}")
print(f"[RECEIVER] Sending ACKs to {HOST}:{ACK_PORT}\n")

received_seqs = set()   # for duplicate detection
pkt_count     = 0

try:
    while True:
        try:
            raw, addr = sock.recvfrom(BUFFER_SIZE)
        except socket.timeout:
            print("[RECEIVER] No packet for 5s — done.\n")
            break

        try:
            pkt = json.loads(raw.decode())
        except json.JSONDecodeError:
            print(f"[RECEIVER] ⚠  Bad packet from {addr}")
            continue

        seq   = pkt.get("seq")
        total = pkt.get("total", "?")
        msg   = pkt.get("msg", "")

        is_dup = seq in received_seqs
        received_seqs.add(seq)

        if is_dup:
            print(f"[RECEIVER] ↩  DUP  seq={seq}/{total} — sending ACK anyway")
        else:
            pkt_count += 1
            print(f"[RECEIVER] ✓ Got  seq={seq}/{total}  | '{msg}'")

        # ── send ACK ──────────────────────────────────────────────────────────────
        ack_payload = json.dumps({
            "ack":  seq,
            "host": HOST,
        }).encode()

        ack_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ack_sock.sendto(ack_payload, (addr[0], ACK_PORT))
        ack_sock.close()
        print(f"[RECEIVER]   → ACK sent for seq={seq} to {addr[0]}:{ACK_PORT}")

except KeyboardInterrupt:
    print("\n[RECEIVER] Interrupted.")

finally:
    print("=" * 55)
    print("  RECEIVER SUMMARY")
    print("=" * 55)
    print(f"  Unique packets received : {len(received_seqs)}")
    print(f"  total ACK sent          : {pkt_count + (len(received_seqs) - pkt_count)}")
    print(f"  Duplicate detections    : {len(received_seqs) - pkt_count}")
    print("=" * 55)
    sock.close()

