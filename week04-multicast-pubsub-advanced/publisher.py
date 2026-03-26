# week04-multicast-pubsub-advanced/publisher.py
import socket
import sys
import os
from config import DEFAULT_PORT, DEFAULT_TTL
from topics import get_group_for_topic, list_topics
from utils.protocol import create_message

def main():
    if len(sys.argv) < 3:
        print("Usage: python publisher.py <topic> <message>")
        print(f"Available topics: {', '.join(list_topics())}")
        return

    topic = sys.argv[1].lower()
    content = " ".join(sys.argv[2:])
    group = get_group_for_topic(topic)

    if not group:
        print(f"Error: Topic '{topic}' is not valid.")
        return

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, DEFAULT_TTL)

    msg_bytes = create_message(topic, content)

    print(f"[PUBLISHER] Sending to topic '{topic}' ({group}:{DEFAULT_PORT})")
    sock.sendto(msg_bytes, (group, DEFAULT_PORT))
    print("[PUBLISHER] Message sent.")
    sock.close()

if __name__ == "__main__":
    main()
