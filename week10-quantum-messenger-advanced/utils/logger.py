# week10-quantum-messenger-advanced/utils/logger.py
import time
import os
import json

class QuantumLogger:
    def __init__(self, node_id, log_dir="logs/"):
        self.node_id = node_id
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        self.log_file = os.path.join(log_dir, f"quantum_node_{node_id}.jsonl")
        
    def log_state_change(self, token_id, event, details):
        entry = {
            "timestamp": time.time(),
            "node": self.node_id,
            "token_id": token_id,
            "event": event,
            "details": details
        }
        with open(self.log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")
