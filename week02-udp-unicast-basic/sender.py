"""
sender.py — Extension B: Manual ACK + Retry
Sends each packet and waits for an ACK from the receiver.
Retransmits up to MAX_RETRIES times if no ACK is received.
"""
import socket
import json
import time
from config import HOST, PORT, ACK_PORT, BUFFER_SIZE, ACK_TIMEOUT, MAX_RETRIES, TOTAL_PACKETS

# ── sockets ──────────────────────────────────────────────────────────────────────
send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # for sending data

ack_sock  = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # for receiving ACKs
ack_sock.bind((HOST, ACK_PORT))
ack_sock.settimeout(ACK_TIMEOUT)

# ── stats ─────────────────────────────────────────────────────────────────────────
total_sent        = 0
total_acked       = 0
total_retransmits = 0
failed_packets    = []

print(f"[SENDER] Extension B — Manual ACK  ({TOTAL_PACKETS} packets → {HOST}:{PORT})")
print(f"[SENDER] ACK expected on port {ACK_PORT} | timeout={ACK_TIMEOUT}s | max_retries={MAX_RETRIES}\n")

for seq in range(1, TOTAL_PACKETS + 1):
    payload = json.dumps({
        "seq":   seq,
        "total": TOTAL_PACKETS,
        "msg":   f"Packet #{seq}",
        "ts":    time.time(),
    }).encode()

    acked    = False
    attempts = 0

    while attempts <= MAX_RETRIES:
        # ── send ──
        send_sock.sendto(payload, (HOST, PORT))
        total_sent += 1
        label = "SEND " if attempts == 0 else f"RETRY {attempts}"
        print(f"[SENDER] [{label}] seq={seq}/{TOTAL_PACKETS}")

        # ── wait for ACK ──
        try:
            raw, _ = ack_sock.recvfrom(BUFFER_SIZE)
            ack    = json.loads(raw.decode())
            if ack.get("ack") == seq:
                print(f"[SENDER] ✓ ACK received for seq={seq}")
                acked = True
                total_acked += 1
                break
            else:
                print(f"[SENDER] ⚠  Wrong ACK seq={ack.get('ack')} (expected {seq})")
        except socket.timeout:
            print(f"[SENDER] ⏱  Timeout waiting for ACK (seq={seq})")

        attempts += 1
        if attempts <= MAX_RETRIES:
            total_retransmits += 1

    if not acked:
        print(f"[SENDER] ✗ FAILED seq={seq} after {MAX_RETRIES} retries\n")
        failed_packets.append(seq)
    print()

# ── summary ────────────────────────────────────────────────────────────────────────
print("=" * 55)
print("  SENDER SUMMARY")
print("=" * 55)
print(f"  Packets sent        : {TOTAL_PACKETS}")
print(f"  ACKed (delivered)   : {total_acked}")
print(f"  Failed (no ACK)     : {len(failed_packets)} — {failed_packets}")
print(f"  Total transmissions : {total_sent}  (incl. retransmits)")
print(f"  Retransmissions     : {total_retransmits}")
print("=" * 55)

send_sock.close()
ack_sock.close()
