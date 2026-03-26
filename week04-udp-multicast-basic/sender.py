# week04-udp-multicast-basic/sender.py
import time
from config import MULTICAST_GROUP, PORT, TTL, SEND_INTERVAL

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, TTL)

print(f"[SENDER] Starting periodic stream to {MULTICAST_GROUP}:{PORT} (Interval: {SEND_INTERVAL}s)")

count = 0
try:
    while True:
        count += 1
        message = f"MULTICAST STREAM: Packet #{count} at {time.strftime('%H:%M:%S')}"
        sock.sendto(message.encode(), (MULTICAST_GROUP, PORT))
        print(f"[SENDER] Sent: {message}")
        time.sleep(SEND_INTERVAL)
except KeyboardInterrupt:
    print("\n[SENDER] Stopping stream.")
finally:
    sock.close()
