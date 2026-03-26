# week04-multicast-pubsub-advanced/subscriber.py
import socket
import struct
import sys
from config import DEFAULT_PORT, BUFFER_SIZE
from topics import get_group_for_topic, list_topics
from utils.protocol import parse_message

def main():
    if len(sys.argv) < 2:
        print("Usage: python subscriber.py <topic1> [topic2] ...")
        print(f"Available topics: {', '.join(list_topics())}")
        return

    topics = [t.lower() for t in sys.argv[1:]]
    groups = []

    for t in topics:
        g = get_group_for_topic(t)
        if g:
            groups.append((t, g))
        else:
            print(f"Warning: Topic '{t}' is not valid and will be ignored.")

    if not groups:
        print("Error: No valid topics selected.")
        return

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("", DEFAULT_PORT))

    for topic, group in groups:
        mreq = struct.pack("4sl", socket.inet_aton(group), socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        print(f"[SUBSCRIBER] Subscribed to topic '{topic}' ({group})")

    print(f"[SUBSCRIBER] Listening on port {DEFAULT_PORT}...")

    try:
        while True:
            data, addr = sock.recvfrom(BUFFER_SIZE)
            msg = parse_message(data)
            if msg:
                print(f"\n[SUBSCRIBER] New message from {addr}")
                print(f"  Topic:   {msg['topic']}")
                print(f"  Sender:  {msg['sender']}")
                print(f"  Content: {msg['content']}")
            else:
                print(f"\n[SUBSCRIBER] Received invalid message from {addr}")
    except KeyboardInterrupt:
        print("\n[SUBSCRIBER] Unsubscribing and shutting down.")
    finally:
        sock.close()

if __name__ == "__main__":
    main()
