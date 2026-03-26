# week06-manet-disaster-advanced/node/node.py
import socket
import threading
import sys
import json
import time
import os

# Adjust path to import from parent/sibling
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import BUFFER_SIZE, ROLES
from utils.routing_metrics import MetricsTable
from neighbor_manager import NeighborManager
from message_forwarder import MessageForwarder

class DisasterNode:
    def __init__(self, port, role):
        self.port = port
        self.role = role
        self.metrics = MetricsTable()
        self.neighbors = NeighborManager(port, role)
        self.forwarder = MessageForwarder(port, self.metrics)
        self.running = True

    def start(self):
        self.neighbors.start_discovery()
        threading.Thread(target=self.serve, daemon=True).start()
        self.shell()

    def serve(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("127.0.0.1", self.port))
        sock.listen(5)
        
        while self.running:
            try:
                conn, addr = sock.accept()
                data = conn.recv(BUFFER_SIZE)
                if data:
                    packet = json.loads(data.decode())
                    if self.forwarder.should_forward(packet['id'], packet['ttl']):
                        print(f"\n[ALERT] From {packet['origin']} ({packet['role']}): {packet['body']}")
                        self.forwarder.forward(packet, self.neighbors.get_neighbors(), addr[1])
                conn.close()
            except: continue

    def shell(self):
        print(f"--- Disaster Mesh Node {self.port} [{self.role}] ---")
        while self.running:
            cmd = input("> ").strip().split(" ", 1)
            if not cmd[0]: continue
            
            action = cmd[0].lower()
            if action == "/exit": self.running = False
            elif action == "/peers": print(f"Neighbors: {self.neighbors.get_neighbors()}")
            elif action == "/stats": print(f"Stats: {json.dumps(self.metrics.get_summary(), indent=2)}")
            elif action == "/alert":
                if len(cmd) < 2: continue
                packet = self.forwarder.create_packet(cmd[1], self.role)
                self.forwarder.forward(packet, self.neighbors.get_neighbors())
                print("Alert broadcasted to mesh.")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python node.py <port> <role_index 0-2>")
        sys.exit(1)
    
    port = int(sys.argv[1])
    role = ROLES[int(sys.argv[2])]
    DisasterNode(port, role).start()
