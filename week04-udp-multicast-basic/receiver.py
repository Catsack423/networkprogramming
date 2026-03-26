import socket
import struct
import sys
from config import CHANNELS, PORT, BUFFER_SIZE

def main():
    if len(sys.argv) < 2:
        print("Usage: python receiver.py <channel1> [channel2] ...")
        print(f"Available channels: {', '.join(CHANNELS.keys())}")
        return

    target_channels = [c.lower() for c in sys.argv[1:]]
    valid_groups = []

    for c in target_channels:
        if c in CHANNELS:
            valid_groups.append((c, CHANNELS[c]))
        else:
            print(f"Warning: Channel '{c}' not found.")

    if not valid_groups:
        print("Error: No valid channels selected.")
        return

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("", PORT))

    # Join each selected multicast group
    for name, group in valid_groups:
        mreq = struct.pack("4sl", socket.inet_aton(group), socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        print(f"[RECEIVER] Subscribed to {name} ({group})")

    print(f"[RECEIVER] Listening on port {PORT}...")

    try:
        while True:
            data, addr = sock.recvfrom(BUFFER_SIZE)
            print(f"[RECEIVER] From {addr}: {data.decode()}")
    except KeyboardInterrupt:
        print("\n[RECEIVER] Unsubscribing and shutting down.")
    finally:
        sock.close()

if __name__ == "__main__":
    main()
