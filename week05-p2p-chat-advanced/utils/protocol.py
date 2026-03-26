# week05-p2p-chat-advanced/utils/protocol.py
import json
import time

def create_msg(msg_type: str, sender: str, content: str = "", extra: dict = None) -> bytes:
    """Creates a JSON-framed P2P message."""
    payload = {
        "type": msg_type,
        "sender": sender,
        "content": content,
        "timestamp": time.time(),
        "extra": extra or {}
    }
    return json.dumps(payload).encode("utf-8")

def parse_msg(data: bytes) -> dict:
    """Parses incoming bytes into a JSON message."""
    try:
        return json.loads(data.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None
