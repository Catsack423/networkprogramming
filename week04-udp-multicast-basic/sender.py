# week04-udp-multicast-basic/sender.py
import socket
from config import MULTICAST_GROUP, PORT, TTL

# Create a UDP socket
# Note: IPPROTO_UDP is explicit here
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

# Set the Time-to-Live (TTL) for the multicast packets
# TTL=1 means the packet won't leave the local network
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, TTL)

message = "MULTICAST: Hello subscribers! This is a group announcement."

print(f"[SENDER] Sending to {MULTICAST_GROUP}:{PORT} (TTL={TTL})")

try:
    sock.sendto(message.encode(), (MULTICAST_GROUP, PORT))
    print("[SENDER] Multicast message sent successfully.")
finally:
    sock.close()
