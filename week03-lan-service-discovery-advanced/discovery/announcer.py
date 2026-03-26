"""
discovery/announcer.py
Service Announcer — broadcasts service presence on a LAN.

Usage:
    python announcer.py --name MyWebServer --type HTTP [--interval 5]

The announcer:
1. Sends a broadcast ANNOUNCE every ANNOUNCE_INTERVAL seconds.
2. Listens on REPLY_PORT for unicast replies from responders.
3. Maintains a local registry of discovered peers and displays it.
"""

import socket
import threading
import time
import argparse
import sys
import os

# Allow running from the repo root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config import BROADCAST_IP, PORT, REPLY_PORT, BUFFER_SIZE, ANNOUNCE_INTERVAL, ENTRY_TTL
from utils.message import build_announce_message, parse_message
from registry.registry import ServiceRegistry

# ── argument parsing ────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="LAN Service Announcer")
parser.add_argument("--name",     default="MyService",  help="Service name to announce")
parser.add_argument("--type",     default="GENERIC",    help="Service type label (e.g. HTTP, DB, …)")
parser.add_argument("--interval", type=float, default=ANNOUNCE_INTERVAL,
                    help=f"Broadcast interval in seconds (default {ANNOUNCE_INTERVAL})")
args = parser.parse_args()

# ── shared registry ──────────────────────────────────────────────────────────────
registry = ServiceRegistry(ttl=ENTRY_TTL)


# ── reply listener thread ────────────────────────────────────────────────────────
def reply_listener():
    """Listen for unicast replies from responders."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("", REPLY_PORT))
    print(f"[ANNOUNCER] Listening for replies on port {REPLY_PORT}")

    while True:
        try:
            raw, addr = sock.recvfrom(BUFFER_SIZE)
            msg = parse_message(raw)
            if msg and msg.get("type") == "REPLY":
                registry.register(msg, src_ip=addr[0])
                print(f"\n[ANNOUNCER] ← Reply from {addr[0]}  service='{msg.get('service_name')}'")
        except Exception as e:
            print(f"[ANNOUNCER][ERROR] reply_listener: {e}")


# ── expiry thread ────────────────────────────────────────────────────────────────
def expiry_loop():
    """Periodically remove stale registry entries."""
    while True:
        time.sleep(ENTRY_TTL / 2)
        expired = registry.expire()
        for name in expired:
            print(f"[ANNOUNCER] ⏱  Entry expired: '{name}'")


# ── broadcast loop (main) ────────────────────────────────────────────────────────
def main():
    # Start background threads
    threading.Thread(target=reply_listener, daemon=True).start()
    threading.Thread(target=expiry_loop,    daemon=True).start()

    # Broadcast socket
    bcast_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    bcast_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    print(f"[ANNOUNCER] Starting — service='{args.name}' type='{args.type}' interval={args.interval}s")
    print(f"[ANNOUNCER] Broadcasting to {BROADCAST_IP}:{PORT}")

    try:
        while True:
            payload = build_announce_message(
                service_name=args.name,
                service_type=args.type,
                metadata={"interval": args.interval},
            )
            bcast_sock.sendto(payload, (BROADCAST_IP, PORT))
            print(f"[ANNOUNCER] → Broadcast sent  ({len(payload)} bytes)")

            # Show current discovered peers
            print(f"[ANNOUNCER] Active peers in registry: {registry.count()}")
            registry.display()
            print()

            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\n[ANNOUNCER] Shutting down.")
    finally:
        bcast_sock.close()


if __name__ == "__main__":
    main()
