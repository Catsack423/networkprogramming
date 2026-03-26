"""
listener.py — Extension C: Subnet Broadcast Observer
Listens on PORT and shows the origin IP of each broadcast received.
Demonstrates that subnet-directed broadcast (e.g. 192.168.1.255)
reaches the same nodes as 255.255.255.255 but is more network-friendly.
"""
import socket
import time
from config import PORT, BUFFER_SIZE
from subnet import get_subnet_broadcast

local_ip, subnet_mask, subnet_bcast = get_subnet_broadcast()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(("", PORT))

print(f"[LISTENER] Extension C — Subnet Broadcast Observer")
print(f"[LISTENER] This node : {local_ip}  mask={subnet_mask}  bcast={subnet_bcast}")
print(f"[LISTENER] Listening on port {PORT}  (Ctrl+C to stop)\n")

count = 0
try:
    while True:
        data, addr = sock.recvfrom(BUFFER_SIZE)
        count += 1
        ts  = time.strftime("%H:%M:%S")
        msg = data.decode()

        # Label the broadcast type
        if addr[0] == local_ip:
            origin = "← from self (loopback)"
        else:
            origin = f"← from {addr[0]}"

        print(f"[LISTENER] [{ts}] #{count:>3}  {origin}")
        print(f"           msg: '{msg}'")
        print()

except KeyboardInterrupt:
    print(f"\n[LISTENER] Received {count} broadcast(s). Shutting down.")

finally:
    sock.close()
