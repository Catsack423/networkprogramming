# week08-opportunistic-basic/message_store.py
import json
import os
import time

class MessageStore:
    def __init__(self, persistence_file):
        self.persistence_file = persistence_file
        self.messages = self._load()

    def add(self, msg_id, body, origin, copies_left, ttl, hops=0):
        if msg_id in self.messages:
            return False
            
        self.messages[msg_id] = {
            "id": msg_id,
            "body": body,
            "origin": origin,
            "copies_left": copies_left,
            "ttl": ttl,
            "hops": hops,
            "timestamp": time.time()
        }
        self._save()
        return True

    def get_inventory(self):
        """Returns a list of message IDs for sync comparison."""
        # Filter expired messages
        now = time.time()
        return [mid for mid, m in self.messages.items() if now - m['timestamp'] < m['ttl']]

    def get_message(self, msg_id):
        return self.messages.get(msg_id)

    def _save(self):
        with open(self.persistence_file, 'w') as f:
            json.dump(self.messages, f, indent=2)

    def _load(self):
        if os.path.exists(self.persistence_file):
            try:
                with open(self.persistence_file, 'r') as f:
                    return json.load(f)
            except: pass
        return {}
