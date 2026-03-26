# week10-quantum-messenger-advanced/node/token.py
import time
import uuid
import hashlib

class EphemeralToken:
    """
    Advanced simulation of a Quantum-secured message token.
    Uses basic cryptographic hashing to ensure tampering causes immediate state collapse.
    """
    def __init__(self, target_id, message, lifespan):
        self.id = str(uuid.uuid4())[:12]
        self.target_id = target_id
        self.message = message
        self.lifespan = lifespan
        self.birth = time.time()
        self.hops = 0
        self.path_history = []
        self._state_hash = self._compute_hash()
        
    def _compute_hash(self):
        """Quantum state signature. Any mutation corrupts it without specific keys."""
        data = f"{self.id}:{self.target_id}:{self.message}:{self.birth}"
        return hashlib.sha256(data.encode()).hexdigest()

    def is_valid(self):
        """Checks for environmental decay (timeout) and state tampering."""
        if time.time() - self.birth > self.lifespan:
            return False, "DECAY_TIMEOUT"
        if self._compute_hash() != self._state_hash:
            return False, "STATE_CORRUPTED"
        return True, "VALID"

    def read_payload(self):
        """Collapses the state entirely upon extraction."""
        valid, reason = self.is_valid()
        if not valid:
            self._corrupt()
            return None, reason
            
        payload = self.message
        self._corrupt() # No-cloning enforce
        return payload, "SUCCESS"
        
    def _corrupt(self):
        """Destroys the internal message state simulating observation collapse."""
        self.message = "[COLLAPSED]"
        self._state_hash = "0000"

    def serialize(self):
        return {
            "id": self.id,
            "target": self.target_id,
            "message": self.message,
            "lifespan": self.lifespan,
            "birth": self.birth,
            "hops": self.hops,
            "path": self.path_history,
            "hash": self._state_hash
        }

    @staticmethod
    def deserialize(data):
        t = EphemeralToken(
            data["target"], 
            data["message"], 
            data["lifespan"]
        )
        t.id = data["id"]
        t.birth = data["birth"]
        t.hops = data["hops"]
        t.path_history = data["path"]
        t._state_hash = data["hash"]
        return t
