# week07-store-forward-planetary/node/message_queue.py
import json
import os
import time

class PlanetaryQueue:
    def __init__(self, node_id, storage_dir):
        self.node_id = node_id
        self.storage_path = os.path.join(storage_dir, f"planetary_queue_{node_id}.json")
        if not os.path.exists(storage_dir):
            os.makedirs(storage_dir)
        self.messages = self._load()

    def add(self, target_node, sender, body, planet, priority=1, hops=0):
        packet = {
            "id": f"{self.node_id}_{time.time()}",
            "target": target_node,
            "sender": sender,
            "body": body,
            "planet": planet,
            "priority": priority,
            "hops": hops,
            "timestamp": time.time(),
            "retries": 0,
            "next_attempt": time.time()
        }
        self.messages.append(packet)
        self._save()
        return packet

    def get_all(self):
        # Return sorted by priority and timestamp
        return sorted(self.messages, key=lambda x: (-x['priority'], x['timestamp']))

    def remove(self, packet_id):
        self.messages = [m for m in self.messages if m['id'] != packet_id]
        self._save()

    def update(self, packet_id, **kwargs):
        for m in self.messages:
            if m['id'] == packet_id:
                for k, v in kwargs.items():
                    m[k] = v
                break
        self._save()

    def _save(self):
        with open(self.storage_path, 'w') as f:
            json.dump(self.messages, f, indent=2)

    def _load(self):
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r') as f:
                    return json.load(f)
            except: pass
        return []
