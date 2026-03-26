# week04-udp-multicast-basic/sender.py
import socket
import sys
import time
from config import CHANNELS, PORT, TTL

def main():
    if len(sys.argv) < 2:
        print("Usage: python sender.py <channel_name> [message]")
        print(f"Channels: {', '.join(CHANNELS.keys())}")
        return

    name = sys.argv[1].lower()
    if name not in CHANNELS:
        print(f"Error: Unknown channel '{name}'")
        return

    group = CHANNELS[name]
    message = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else f"Update on {name} at {time.strftime('%H:%M:%S')}"

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, TTL)

    print(f"[SENDER] Sending to {name} ({group}:{PORT})")
    sock.sendto(message.encode(), (group, PORT))
    print("[SENDER] Sent.")
    sock.close()

if __name__ == "__main__":
    main()
