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
            msg_id = payload['id']
            msg_text = payload['body']
            ttl = payload['ttl']
            origin = payload['origin']

            if msg_id in self.msg_history:
                return # Already seen

            with self.lock:
                self.msg_history.add(msg_id)
                self.received_count += 1
            
            self.log(f"Received from {addr[1]}: '{msg_text}' (TTL={ttl}, Origin={origin})")

            # Extension A: Discovery on reception
            with self.lock:
                if addr[1] not in self.neighbor_table:
                    self.neighbor_table.add(addr[1])
                    self.log(f"New neighbor discovered: {addr[1]}")

            # Probabilistic Forwarding
            if ttl > 0:
                if random.random() < FORWARD_PROBABILITY:
                    self.log(f"Probability check passed. Forwarding...")
                    self.forwarded_count += 1
                    payload['ttl'] = ttl - 1
                    self.broadcast_to_neighbors(payload, exclude_port=addr[1])
                else:
                    self.log("Probability check failed. Dropping packet.")

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

def main():
    if len(sys.argv) < 2:
        print("Usage: python node.py <port>")
        return

    port = int(sys.argv[1])
    node = AdHocNode(port)
    
    threading.Thread(target=node.start_server, daemon=True).start()
    threading.Thread(target=node.neighbor_discovery, daemon=True).start()
    threading.Thread(target=node.mobility_simulation, daemon=True).start()

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
                print(f"Received: {node.received_count}, Forwarded: {node.forwarded_count}")
            elif cmd.startswith("/send"):
                msg_body = cmd[6:]
                payload = {
                    "id": f"{port}_{time.time()}",
                    "origin": port,
                    "body": msg_body,
                    "ttl": DEFAULT_TTL
                }
                node.broadcast_to_neighbors(payload)
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
