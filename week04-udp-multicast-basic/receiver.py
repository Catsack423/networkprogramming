# week04-udp-multicast-basic/receiver.py
import socket
import struct
import time
from config import MULTICAST_GROUP, PORT, BUFFER_SIZE

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(("", PORT))

# Join the multicast group
mreq = struct.pack("4sl", socket.inet_aton(MULTICAST_GROUP), socket.INADDR_ANY)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

print(f"[RECEIVER] Joined {MULTICAST_GROUP}:{PORT}")
print("[RECEIVER] Waiting for multicast stream (Ctrl+C to stop)...")

count = 0
try:
    while True:
        data, addr = sock.recvfrom(BUFFER_SIZE)
        count += 1
        print(f"[RECEIVER] [{time.strftime('%H:%M:%S')}] #{count} from {addr}: {data.decode()}")
except KeyboardInterrupt:
    print("\n[RECEIVER] Leaving group and shutting down.")
finally:
    # Cleanup
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_DROP_MEMBERSHIP, mreq)
    sock.close()
