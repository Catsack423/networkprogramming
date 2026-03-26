import socket
import time
import json
from config import HOST, PORT, TOTAL_PACKETS, SEND_INTERVAL

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print(f"[SENDER] Extension A — sending {TOTAL_PACKETS} packets to {HOST}:{PORT}")
print(f"[SENDER] Interval: {SEND_INTERVAL}s per packet\n")

for seq in range(1, TOTAL_PACKETS + 1):
    payload = json.dumps({
        "seq": seq,
        "total": TOTAL_PACKETS,
        "msg": f"Packet #{seq}",
        "ts": time.time(),
    })
    sock.sendto(payload.encode(), (HOST, PORT))
    print(f"[SENDER] → Sent seq={seq}/{TOTAL_PACKETS}")
    time.sleep(SEND_INTERVAL)

print(f"\n[SENDER] Done — {TOTAL_PACKETS} packets sent.")
sock.close()
