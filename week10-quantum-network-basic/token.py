# week10-quantum-network-basic/token.py
import time
import uuid

class QuantumToken:
    """
    A conceptual one-time-read message token inspired by Quantum mechanics.
    - No-Cloning: Cannot be duplicated.
    - State Collapse: Reading it destroys its payload.
    - Ephemeral: Decays over time even if unread.
    """
    def __init__(self, message, expiry_seconds=10, token_id=None, creation_time=None, read=False, paths=None):
        self.id = token_id or str(uuid.uuid4())[:8]
        self.message = message
        self.expiry_time = expiry_seconds
        self.timestamp = creation_time or time.time()
        self.read = read
        
        # Extension B: Multi-Hop Token Routing (Track history)
        self.paths = paths or []

    def read_token(self):
        """Attempts to read the message. Collapses the state upon successful read."""
        if self.read:
            return None, "STATE_COLLAPSED_ALREADY_READ"
        # Hardcoded 10 second expiry simulating default environment rules
        if time.time() - self.timestamp > self.expiry_time:
            self.read = True # Force collapse
            return None, "STATE_COLLAPSED_EXPIRED"
            
        self.read = True
        return self.message, "SUCCESS"

    def serialize(self):
        return {
            "id": self.id,
            "message": self.message,
            "expiry_time": self.expiry_time,
            "timestamp": self.timestamp,
            "read": self.read,
            "paths": self.paths
        }

    @staticmethod
    def deserialize(data):
        return QuantumToken(
            message=data.get("message"),
            expiry_seconds=data.get("expiry_time", 10),
            token_id=data.get("id"),
            creation_time=data.get("timestamp"),
            read=data.get("read", False),
            paths=data.get("paths", [])
        )
