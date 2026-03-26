# week09-bio-network-advanced/utils/logger.py
import time
import os
import json

class MetricLogger:
    def __init__(self, node_id, log_dir="logs/"):
        self.node_id = node_id
        self.log_dir = log_dir
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        self.log_file = os.path.join(log_dir, f"node_{node_id}.jsonl")
        
    def log_event(self, event_type, details):
        """Append a JSON line to the log file for later visualization."""
        entry = {
            "timestamp": time.time(),
            "node": self.node_id,
            "event": event_type,
            "details": details
        }
        with open(self.log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")
