# week06-manet-basic/node.py
import socket
import threading
import random
import time
import sys
import json
from config import HOST, BUFFER_SIZE, FORWARD_PROBABILITY, DEFAULT_TTL, DISCOVERY_INTERVAL, MOBILITY_INTERVAL

class AdHocNode:
    def __init__(self, port):
        self.port = port
        self.neighbor_table = set()
        self.msg_history = set() # To prevent loops
        self.received_count = 0
        self.forwarded_count = 0
        self.duplicate_count = 0
        self.forward_prob = FORWARD_PROBABILITY
        self.lock = threading.Lock()
        self.running = True

    def log(self, msg):
        print(f"[NODE {self.port}] {msg}")

    def start_server(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((HOST, self.port))
        sock.listen(5)
        self.log("Listening...")
        
        while self.running:
            try:
                conn, addr = sock.accept()
                data = conn.recv(BUFFER_SIZE)
                if data:
                    threading.Thread(target=self.handle_incoming, args=(data, addr)).start()
                conn.close()
            except Exception as e:
                if self.running: self.log(f"Server error: {e}")

    def handle_incoming(self, raw_data, addr):
        try:
            payload = json.loads(raw_data.decode())
            msg_id = payload.get('id')
            
            if not msg_id: return

            if msg_id in self.msg_history:
                with self.lock: self.duplicate_count += 1
                return 

            msg_text = payload.get('body', '')
            ttl = payload.get('ttl', 0)
            origin = payload.get('origin', 'unknown')

            with self.lock:
                self.msg_history.add(msg_id)
                self.received_count += 1
            
            self.log(f"Received from {addr[1]}: '{msg_text}' (TTL={ttl}, Origin={origin})")

            # Discovery logic...
            sender_port = payload.get('sender_port')
            if sender_port and sender_port != self.port:
                with self.lock:
                    if sender_port not in self.neighbor_table:
                        self.neighbor_table.add(sender_port)
                        self.log(f"New neighbor discovered: {sender_port}")

            if ttl > 0:
                with self.lock: current_prob = self.forward_prob
                if random.random() < current_prob:
                    self.log(f"Forward check passed ({current_prob:.2f}). Forwarding...")
                    self.forwarded_count += 1
                    payload['ttl'] = ttl - 1
                    self.broadcast_to_neighbors(payload, exclude_port=addr[1])
                else:
                    self.log(f"Forward check failed ({current_prob:.2f}). Dropping.")

        except Exception as e:
            self.log(f"Error handling message: {e}")

    def broadcast_to_neighbors(self, payload, exclude_port=None):
        raw_msg = json.dumps(payload).encode()
        with self.lock:
            targets = list(self.neighbor_table)
        
        for p in targets:
            if p == exclude_port or p == self.port:
                continue
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.5)
                s.connect((HOST, p))
                s.sendall(raw_msg)
                s.close()
            except:
                # Neighbor might be gone (Mobility)
                with self.lock:
                    if p in self.neighbor_table: self.neighbor_table.remove(p)

    def neighbor_discovery(self):
        """Extension A: Periodically ping a range of ports to find neighbors."""
        while self.running:
            # Ping ports 7000-7010
            for p in range(7000, 7011):
                if p == self.port: continue
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(0.2)
                    s.connect((HOST, p))
                    # Just a ping or a HELLO message
                    hello = json.dumps({"type": "PING", "port": self.port})
                    # This node doesn't handle PING specifically in handle_incoming yet,
                    # but the connect itself confirms port is open.
                    s.close()
                    with self.lock:
                        if p not in self.neighbor_table:
                            self.neighbor_table.add(p)
                            self.log(f"Discovered {p} via discovery loop.")
                except:
                    pass
            time.sleep(DISCOVERY_INTERVAL)

    def mobility_simulation(self):
        """Extension B: Randomly lose neighbors to simulate movement."""
        while self.running:
            time.sleep(MOBILITY_INTERVAL)
            with self.lock:
                if self.neighbor_table and random.random() < 0.3:
                    lost = random.choice(list(self.neighbor_table))
                    self.neighbor_table.remove(lost)
                    self.log(f"!! Mobility: Neighbor {lost} went out of range.")

    def monitor_metrics(self):
        """Extension C: Adjust forward probability based on duplicate rate."""
        while self.running:
            time.sleep(10)
            with self.lock:
                # If we see many duplicates, it means the network is saturated
                # If we see very few, we might need to be more aggressive
                if self.received_count > 0:
                    dup_rate = self.duplicate_count / (self.received_count + self.duplicate_count)
                    
                    if dup_rate > 0.5: # Highly saturated
                        self.forward_prob = max(0.1, self.forward_prob - 0.1)
                        self.log(f"!! METRICS: Saturation high ({dup_rate:.1%}). Reducing Prob to {self.forward_prob:.2f}")
                    elif dup_rate < 0.1: # Potential under-delivery
                        self.forward_prob = min(0.9, self.forward_prob + 0.1)
                        self.log(f"!! METRICS: Saturation low ({dup_rate:.1%}). Increasing Prob to {self.forward_prob:.2f}")
                    
                    # Reset window
                    self.duplicate_count = 0
                    self.received_count = 0

def main():
    if len(sys.argv) < 2:
        print("Usage: python node.py <port>")
        return

    port = int(sys.argv[1])
    node = AdHocNode(port)
    
    threading.Thread(target=node.start_server, daemon=True).start()
    threading.Thread(target=node.neighbor_discovery, daemon=True).start()
    threading.Thread(target=node.mobility_simulation, daemon=True).start()
    threading.Thread(target=node.monitor_metrics, daemon=True).start()

    print(f"--- MANET Node {port} Ready ---")
    print("Commands: /send <msg>, /peers, /stats, /exit")

    try:
        while True:
            cmd = input("> ").strip()
            if not cmd: continue
            
            if cmd == "/exit":
                node.running = False
                break
            elif cmd == "/peers":
                print(f"Neighbors: {list(node.neighbor_table)}")
            elif cmd == "/stats":
                with node.lock:
                    print(f"Prob: {node.forward_prob:.2f}, Received(Unique): {len(node.msg_history)}")
            elif cmd.startswith("/send"):
                msg_body = cmd[6:]
                payload = {
                    "id": f"{port}_{time.time()}",
                    "origin": port,
                    "sender_port": port,
                    "body": msg_body,
                    "ttl": DEFAULT_TTL
                }
                node.broadcast_to_neighbors(payload)
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
