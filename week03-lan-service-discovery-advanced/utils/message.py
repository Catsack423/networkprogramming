"""
utils/message.py
Utility functions for building and parsing JSON-based discovery messages.
"""

import json
import time
import socket


def build_announce_message(service_name: str, service_type: str, metadata: dict = None) -> bytes:
    """Build a JSON announcement payload sent by the announcer via broadcast."""
    payload = {
        "type": "ANNOUNCE",
        "service_name": service_name,
        "service_type": service_type,
        "host": socket.gethostname(),
        "timestamp": time.time(),
        "metadata": metadata or {},
    }
    return json.dumps(payload).encode("utf-8")


def build_reply_message(service_name: str) -> bytes:
    """Build a JSON unicast reply from responder back to announcer."""
    payload = {
        "type": "REPLY",
        "service_name": service_name,
        "host": socket.gethostname(),
        "timestamp": time.time(),
    }
    return json.dumps(payload).encode("utf-8")


def parse_message(raw: bytes) -> dict:
    """
    Parse a raw UDP datagram into a Python dict.
    Returns None if the payload is not valid JSON.
    """
    try:
        return json.loads(raw.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None
