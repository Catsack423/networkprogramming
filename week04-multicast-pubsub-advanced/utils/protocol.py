# week04-multicast-pubsub-advanced/utils/protocol.py
import json
import time

def create_message(topic: str, content: str, sender_id: str = "Anonymous") -> bytes:
    """Wraps the content in a JSON structure for multicast transmission."""
    payload = {
        "topic": topic,
        "content": content,
        "sender": sender_id,
        "timestamp": time.time()
    }
    return json.dumps(payload).encode("utf-8")

def parse_message(data: bytes) -> dict:
    """Parses raw bytes into a dictionary."""
    try:
        return json.loads(data.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None
