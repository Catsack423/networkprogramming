# week10-quantum-messenger-advanced/node/node.py
import socket
import threading
import sys
import json
import time
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import BASE_PORT, BUFFER_SIZE, TOKEN_LIFESPAN, DEFAULT_EXPIRY, MAX_HOPS, STATE_COLLAPSE_PROB
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../utils')))
from logger import QuantumLogger
from token import EphemeralToken
from state_manager import QuantumStateManager

class AdvancedQuantumNode:
    def __init__(self, node_id, target_peers):
        self.id = node_id
        self.port = BASE_PORT + node_id
        self.target_peers = target_peers # Who we know about in the network
        self.logger = QuantumLogger(node_id)
        # Using a config constant but falling back to 20 if DEFAULT_EXPIRY isn't in config
        lifespan = globals().get('TOKEN_LIFESPAN', 20)
        prob = globals().get('STATE_COLLAPSE_PROB', 0.2)
        hops = globals().get('MAX_HOPS', 5)
        self.state_manager = QuantumStateManager(node_id, lifespan, prob, self.logger)
        self.running = True

    def log(self, msg):
        print(f"[NODE {self.id}] {msg}")

    def send_packet(self, target_node, token):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2.0)
            s.connect(("127.0.0.1", BASE_PORT + target_node))
            
            # Increment hops and serialize
            token.hops += 1
            token.path_history.append(self.id)
            data = json.dumps(token.serialize())
            s.sendall(data.encode())
            s.close()
            return True
        except:
            return False

    def forward_loop(self):
        """Continuously checks for forwardable tokens and tries to push them out."""
        while self.running:
            tokens_to_send = self.state_manager.get_forwardable_tokens(globals().get('MAX_HOPS', 5))
            
            for token in tokens_to_send:
                forwarded = False
                import random
                # Randomly pick a known peer to forward to that isn't already in the path
                candidates = [p for p in self.target_peers if p not in token.path_history]
                random.shuffle(candidates)
                
                for peer in candidates:
                    if self.send_packet(peer, token):
                        self.state_manager.remove_token(token.id)
                        self.log(f"Forwarded token {token.id} to node {peer}")
                        forwarded = True
                        break
                        
            time.sleep(3)

    def serve(self):
        """Listens for incoming quantum states."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("127.0.0.1", self.port))
        sock.listen(5)
        self.log(f"Quantum listener active on port {self.port}")
        
        while self.running:
            try:
                conn, addr = sock.accept()
                raw = conn.recv(BUFFER_SIZE)
                if raw:
                    data = json.loads(raw.decode())
                    token = EphemeralToken.deserialize(data)
                    
                    if self.state_manager.ingest_token(token):
                        # If the token is meant for us, attempt to read it
                        if token.target_id == self.id:
                            self.log(f"--- INBOX: Intercepted targeted state {token.id} ---")
                            payload, status = self.state_manager.attempt_read(token.id)
                            if payload:
                                self.log(f"[READ SUCCESS] Message: {payload}")
                            else:
                                self.log(f"[READ FAILED] State Collapsed: {status}")
                        else:
                            self.log(f"Received quantum state {token.id} heading for {token.target_id}. Buffered.")
                conn.close()
            except: continue

    def shell(self):
        print(f"--- Post-Quantum Routing Node [{self.id}] ---")
        while self.running:
            cmd = input("> ").strip().split(" ", 2)
            if not cmd[0]: continue
            
            action = cmd[0].lower()
            if action == "/exit": self.running = False
            elif action == "/stats":
                print(f"Active Quantum States: {len(self.state_manager.active_tokens)}")
                print(f"Historical States Processed: {len(self.state_manager.history)}")
            elif action == "/logs":
                print(f"View logs at: logs/quantum_node_{self.id}.jsonl")
            elif action == "/send" and len(cmd) >= 3:
                target = int(cmd[1])
                msg = cmd[2]
                tok = EphemeralToken(target, msg, globals().get('TOKEN_LIFESPAN', 20))
                # Inject locally
                self.state_manager.active_tokens[tok.id] = tok
                self.state_manager.history.add(tok.id)
                self.logger.log_state_change(tok.id, "GENERATED", "State initialized locally")
                print(f"Generated quantum state {tok.id} -> Target {target}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python node.py <node_id> <peer1_id> <peer2_id> ...")
        sys.exit(1)
        
    node_id = int(sys.argv[1])
    peers = [int(p) for p in sys.argv[2:]]
    
    n = AdvancedQuantumNode(node_id, peers)
    threading.Thread(target=n.serve, daemon=True).start()
    threading.Thread(target=n.forward_loop, daemon=True).start()
    n.shell()
