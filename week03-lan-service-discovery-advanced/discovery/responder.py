"""
discovery/responder.py
Service Responder — listens for broadcast announcements and replies via unicast.

Usage:
    python responder.py --name MyDBServer --type PostgreSQL

The responder:
1. Binds to PORT and listens for broadcast ANNOUNCE messages.
2. Sends a unicast REPLY directly back to the announcer's REPLY_PORT.
3. Maintains its own registry of known announcers.
"""

import socket
import sys
import os
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config import PORT, REPLY_PORT, BUFFER_SIZE, ENTRY_TTL
from utils.message import build_reply_message, parse_message
from registry.registry import ServiceRegistry

# ── argument parsing ────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="LAN Service Responder")
parser.add_argument("--name", default="MyResponder", help="This responder's service name")
parser.add_argument("--type", default="GENERIC",     help="This responder's service type")
args = parser.parse_args()

# ── local registry (tracks announcers seen) ─────────────────────────────────────
registry = ServiceRegistry(ttl=ENTRY_TTL)


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("", PORT))

    print(f"[RESPONDER] '{args.name}' ({args.type}) — listening for broadcasts on port {PORT}")

    while True:
        try:
            raw, addr = sock.recvfrom(BUFFER_SIZE)
            msg = parse_message(raw)

            if not msg:
                continue

            if msg.get("type") != "ANNOUNCE":
                continue  # ignore non-announce messages

            src_ip   = addr[0]
            svc_name = msg.get("service_name", "unknown")
            svc_type = msg.get("service_type", "")
            host     = msg.get("host", "")

            print(f"[RESPONDER] ← Announcement from {src_ip} | '{svc_name}' ({svc_type}) on host '{host}'")

            # Register the announcer locally
            registry.register(msg, src_ip=src_ip)

            # Send unicast reply to the announcer's REPLY_PORT
            reply = build_reply_message(service_name=args.name)
            reply_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            reply_sock.sendto(reply, (src_ip, REPLY_PORT))
            reply_sock.close()

            print(f"[RESPONDER] → Unicast reply sent to {src_ip}:{REPLY_PORT}")
            print(f"[RESPONDER] Known announcers:")
            registry.display()
            print()

        except KeyboardInterrupt:
            print("\n[RESPONDER] Shutting down.")
            break
        except Exception as e:
            print(f"[RESPONDER][ERROR] {e}")

    sock.close()


if __name__ == "__main__":
    main()
