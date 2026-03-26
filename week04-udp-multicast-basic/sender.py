import sys
from config import CHANNELS, PORT, TTL

def main():
    if len(sys.argv) < 2:
        print("Usage: python sender.py <channel_name> [message]")
        print(f"Available channels: {', '.join(CHANNELS.keys())}")
        return

    channel_name = sys.argv[1].lower()
    if channel_name not in CHANNELS:
        print(f"Error: Channel '{channel_name}' not found.")
        return

    group = CHANNELS[channel_name]
    message = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else f"Hello from {channel_name} channel!"

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, TTL)

    print(f"[SENDER] Sending to {channel_name} ({group}:{PORT})")
    sock.sendto(message.encode(), (group, PORT))
    print("[SENDER] Message sent successfully.")
    sock.close()

if __name__ == "__main__":
    main()
