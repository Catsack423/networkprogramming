# week07-store-forward-basic/message_queue.py
import json
import os
import time
from collections import deque

class MessageQueue:
    def __init__(self, persistence_file):
        self.persistence_file = persistence_file
        self.queue = deque()
        self.load_from_disk()

    def add_message(self, message, peer_port, priority=1):
        """Adds a message with priority (higher = first)."""
        msg_obj = {
            "message": message,
            "peer": peer_port,
            "timestamp": time.time(),
            "priority": priority,
            "retries": 0,
            "next_retry": time.time()
        }
        self.queue.append(msg_obj)
        # Sort by priority (descending) and then timestamp
        sorted_list = sorted(list(self.queue), key=lambda x: (-x['priority'], x['timestamp']))
        self.queue = deque(sorted_list)
        self.save_to_disk()

    def get_pending_messages(self):
        return list(self.queue)

    def remove_message(self, msg_id_tuple):
        # We use (peer, timestamp) as a simple unique identifier
        self.queue = deque([m for m in self.queue if (m['peer'], m['timestamp']) != msg_id_tuple])
        self.save_to_disk()

    def update_retry(self, msg_id_tuple, next_retry_time, retry_count):
        for m in self.queue:
            if (m['peer'], m['timestamp']) == msg_id_tuple:
                m['next_retry'] = next_retry_time
                m['retries'] = retry_count
                break
        self.save_to_disk()

    def save_to_disk(self):
        with open(self.persistence_file, 'w') as f:
            json.dump(list(self.queue), f, indent=2)

    def load_from_disk(self):
        if os.path.exists(self.persistence_file):
            try:
                with open(self.persistence_file, 'r') as f:
                    data = json.load(f)
                    self.queue = deque(data)
            except:
                self.queue = deque()
