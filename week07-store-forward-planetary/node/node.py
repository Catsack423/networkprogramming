# week07-store-forward-planetary/node/node.py
import socket
import threading
import sys
import json
import time
import os

# Adjust path to import from parent/sibling
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import BASE_PORT, BUFFER_SIZE, PLANET_LATENCY, RETRY_BACKOFF_FACTOR, MAX_RETRY_INTERVAL, PERSISTENCE_DIR
from utils.retry_policy import RetryPolicy
from message_queue import PlanetaryQueue

class PlanetaryNode:
    def __init__(self, node_id, planet):
        self.id = node_id
        self.port = BASE_PORT + node_id
        self.planet = planet
        self.latency = PLANET_LATENCY.get(planet, 0)
        self.queue = PlanetaryQueue(node_id, PERSISTENCE_DIR)
        self.policy = RetryPolicy(10, RETRY_BACKOFF_FACTOR, MAX_RETRY_INTERVAL)
        self.running = True

    def log(self, msg):
        print(f"[{self.planet} Node {self.id}] {msg}")

    def send_with_latency(self, target_port, packet):
        """Simulate high-latency interplanetary transmission."""
        try:
            # Latency simulation
            if self.latency > 0:
                self.log(f"Simulating {self.latency}s transmission delay...")
                time.sleep(self.latency)
            
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2.0)
            s.connect(("127.0.0.1", target_port))
            s.sendall(json.dumps(packet).encode())
            s.close()
            return True
        except:
            return False

    def retry_loop(self):
        """Asynchronous delay-tolerant delivery loop."""
        while self.running:
            pending = self.queue.get_all()
            now = time.time()
            
            for p in pending:
                if now >= p['next_attempt']:
                    target_port = BASE_PORT + p['target']
                    self.log(f"Attempting delivery to Node {p['target']} (Hop {p['hops'] + 1})")
                    
                    if self.send_with_latency(target_port, p):
                        self.log(f"Delivered successfully to Node {p['target']}.")
                        self.queue.remove(p['id'])
                    else:
                        new_retries = p['retries'] + 1
                        delay = self.policy.get_next_delay(new_retries)
                        self.queue.update(p['id'], retries=new_retries, next_attempt=now + delay)
                        self.log(f"Delivery failed. Will retry in {int(delay)}s.")
            
            time.sleep(5)

    def serve(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("127.0.0.1", self.port))
        sock.listen(5)
        self.log(f"Server online on port {self.port}")
        
        while self.running:
            try:
                conn, addr = sock.accept()
                data = conn.recv(BUFFER_SIZE)
                if data:
                    packet = json.loads(data.decode())
                    # If we are the target, show message. Else, we are a carrier (DTN).
                    if packet['target'] == self.id:
                        self.log(f"\n[INBOX] From {packet['sender']} ({packet['planet']}): {packet['body']}")
                        self.log(f"        Travelled through {packet['hops']} hops.")
                    else:
                        self.log(f"\n[CARRIER] Relaying packet for {packet['target']}...")
                        packet['hops'] += 1
                        self.queue.add(packet['target'], packet['sender'], packet['body'], packet['planet'], packet['priority'], packet['hops'])
                conn.close()
            except: continue

    def shell(self):
        print(f"--- Welcome to Planetary Email [{self.planet}] ---")
        while self.running:
            cmd = input("> ").strip().split(" ", 2)
            if not cmd[0]: continue
            
            action = cmd[0].lower()
            if action == "/exit": self.running = False
            elif action == "/list": 
                msgs = self.queue.get_all()
                print(f"Outbox: {len(msgs)} items pending.")
                for m in msgs: print(f" - To {m['target']}: (Retries: {m['retries']}, Next: {int(m['next_attempt'] - time.time())}s)")
            elif action == "/send" and len(cmd) >= 3:
                target_id = int(cmd[1])
                body = cmd[2]
                self.queue.add(target_id, f"Node {self.id}", body, self.planet)
                print("Message queued in outbox.")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python node.py <node_id> <planet_name>")
        sys.exit(1)
    
    node_id = int(sys.argv[1])
    planet = sys.argv[2].upper()
    PlanetaryNode(node_id, planet).start()

    # Convenience start
    n = PlanetaryNode(node_id, planet)
    threading.Thread(target=n.serve, daemon=True).start()
    threading.Thread(target=n.retry_loop, daemon=True).start()
    n.shell()
