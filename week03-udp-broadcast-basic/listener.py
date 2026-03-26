"""
listener.py — Extension A: Broadcast Discovery + Reply
1. Listens for broadcast discovery messages.
2. Sends a unicast reply directly back to the broadcaster.
"""
import socket
import time
from config import PORT, BUFFER_SIZE, REPLY_PORT

hostname = socket.gethostname()

# ── listen socket ─────────────────────────────────────────────────────────────
listen_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
listen_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
listen_sock.bind(("", PORT))

print(f"[LISTENER] '{hostname}' — listening for broadcast on port {PORT}")
print(f"[LISTENER] Will reply unicast to broadcaster on port {REPLY_PORT}\n")

while True:
    try:
        data, addr = listen_sock.recvfrom(BUFFER_SIZE)
    except KeyboardInterrupt:
        print("\n[LISTENER] Shutting down.")
        break

    msg       = data.decode()
    src_ip    = addr[0]
    timestamp = time.strftime("%H:%M:%S")

    print(f"[LISTENER] [{timestamp}] ← Broadcast from {src_ip}: '{msg}'")

    # ── send unicast reply directly to sender ─────────────────────────────────
    reply     = f"ONLINE: {hostname}"
    reply_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    reply_sock.sendto(reply.encode(), (src_ip, REPLY_PORT))
    reply_sock.close()

    print(f"[LISTENER] [{timestamp}] → Unicast reply sent to {src_ip}:{REPLY_PORT}: '{reply}'")
    print()

listen_sock.close()
