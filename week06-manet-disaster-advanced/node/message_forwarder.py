# week06-manet-disaster-advanced/node/message_forwarder.py
import random
import socket
import json
import time
from config import DEFAULT_PROBABILITY, MAX_TTL

class MessageForwarder:
    def __init__(self, node_port, metrics):
        self.node_port = node_port
        self.metrics = metrics
        self.history = set()

    def create_packet(self, body, role, ttl=MAX_TTL):
        return {
            "id": f"{self.node_port}_{time.time()}",
            "origin": self.node_port,
            "role": role,
            "body": body,
            "ttl": ttl,
            "timestamp": time.time()
        }

    def should_forward(self, packet_id, ttl):
        if packet_id in self.history:
            self.metrics.add_duplicate()
            return False
        
        self.history.add(packet_id)
        self.metrics.add_received()
        
        if ttl <= 0: return False
        
        # In a real disaster mesh, we might adjust probability based on role
        return random.random() < DEFAULT_PROBABILITY

    def forward(self, packet, neighbors, exclude_port=None):
        packet['ttl'] -= 1
        raw_msg = json.dumps(packet).encode()
        
        self.metrics.add_relayed()
        
        for p in neighbors:
            if p == exclude_port: continue
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.5)
                s.connect(("127.0.0.1", p))
                s.sendall(raw_msg)
                s.close()
            except:
                pass
