# week04-udp-multicast-basic/receiver.py
import socket
import struct
from config import MULTICAST_GROUP, PORT, BUFFER_SIZE

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

# Allow multiple sockets to use the same PORT number
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Bind to the port
sock.bind(("", PORT))

# Tell the kernel that we want to join the multicast group
# struct.pack("4sl", ...) creates a 12-byte binary representation 
# (4-byte IP address followed by 4-byte interface address)
mreq = struct.pack("4sl", socket.inet_aton(MULTICAST_GROUP), socket.INADDR_ANY)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

print(f"[RECEIVER] Joined {MULTICAST_GROUP}:{PORT}")
print("[RECEIVER] Waiting for multicast messages...")

try:
    while True:
        data, addr = sock.recvfrom(BUFFER_SIZE)
        print(f"[RECEIVER] Received from {addr}: {data.decode()}")
except KeyboardInterrupt:
    print("\n[RECEIVER] Leaving group and shutting down.")
finally:
    # Cleanup: Leave membership (optional but good practice)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_DROP_MEMBERSHIP, mreq)
    sock.close()
