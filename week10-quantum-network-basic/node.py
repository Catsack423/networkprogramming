# week10-quantum-network-basic/node.py
import socket
import threading
import time
import sys
import json
from config import HOST, BASE_PORT, PEER_PORTS, BUFFER_SIZE, UPDATE_INTERVAL, TOKEN_EXPIRY_DEFAULT
from token import QuantumToken

class ConceptualQuantumNode:
    def __init__(self, port):
        self.port = port
        self.token_queue = [] # Tokens awaiting forwarding/reading
        self.running = True

    def log(self, msg):
        print(f"[NODE {self.port}] {msg}")

    def send_token(self, peer_port, token: QuantumToken):
        """Send a serialized token to a peer."""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2.0)
            s.connect((HOST, peer_port))
            
            s.sendall(json.dumps(token.serialize()).encode())
            s.close()
            self.log(f"Transferred quantum token '{token.id}' to {peer_port}")
            return True
        except:
            return False

    def forward_loop(self):
        """Routing loop ensuring tokens are only forwarded if they haven't collapsed."""
        while self.running:
            # Extension A: Cleanup expired tokens
            active_tokens = []
            for token in self.token_queue:
                if not token.peek_valid():
                    self.log(f"Token '{token.id}' collapsed due to expiry in queue. Invalidating.")
                else:
                    active_tokens.append(token)
            self.token_queue = active_tokens

            # Attempt to forward valid tokens
            for token in self.token_queue[:]:
                forwarded = False
                for peer in PEER_PORTS:
                    if peer == self.port: continue
                    
                    if self.send_token(peer, token):
                        # No-Cloning: We MUST remove it locally
                        self.token_queue.remove(token)
                        forwarded = True
                        break
                        
            time.sleep(UPDATE_INTERVAL)

    def serve(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((HOST, self.port))
        sock.listen(5)
        self.log(f"Listening for incoming quantum states on {self.port}...")
        
        while self.running:
            try:
                conn, addr = sock.accept()
                data = conn.recv(BUFFER_SIZE).decode()
                
                if data:
                    token_data = json.loads(data)
                    token = QuantumToken.deserialize(token_data)
                    
                    # Random conceptual constraint: 50% chance the node decides it's the target and reads it.
                    # Otherwise, it just acts as a router.
                    import random
                    if random.random() > 0.5:
                        # Attempt to read (Collapse State)
                        message, status = token.read_token()
                        if message:
                            self.log(f"\n[SECURITY] Successfully un-collapsed state for '{token.id}': {message}")
                        else:
                            self.log(f"\n[SECURITY] Failed to read '{token.id}': {status}")
                    else:
                        # Act as router
                        self.log(f"Received token state '{token.id}'. Storing for relay.")
                        self.token_queue.append(token)
                            
                conn.close()
            except: continue

    def shell(self):
        print(f"--- Conceptual Quantum Node {self.port} Ready ---")
        while self.running:
            cmd = input("> ").strip().split(" ", 2)
            if not cmd[0]: continue
            
            action = cmd[0].lower()
            if action == "/exit": self.running = False
            elif action == "/queue":
                print(f"Queue Size: {len(self.token_queue)}")
                for t in self.token_queue:
                    print(f" - Token {t.id} | Valid: {t.peek_valid()}")
            elif action == "/generate" and len(cmd) >= 2:
                msg = cmd[1] if len(cmd) > 1 else "Empty State"
                expiry = int(cmd[2]) if len(cmd) > 2 else TOKEN_EXPIRY_DEFAULT
                
                t = QuantumToken(msg, expiry_seconds=expiry)
                self.token_queue.append(t)
                print(f"Generated quantum token {t.id} (Expires in {expiry}s). It is now in queue.")

def main():
    if len(sys.argv) < 2:
        print("Usage: python node.py <port>")
        return

    port = int(sys.argv[1])
    n = ConceptualQuantumNode(port)
    
    threading.Thread(target=n.serve, daemon=True).start()
    threading.Thread(target=n.forward_loop, daemon=True).start()
    n.shell()

if __name__ == "__main__":
    main()
