# week08-opportunistic-advanced/node/node.py
import socket
import threading
import sys
import json
import time
import os
import random

# Adjust path to import from parent/sibling
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import BASE_PORT, BUFFER_SIZE, SYNC_SCAN_INTERVAL, PERSISTENCE_DIR
from bundle_manager import BundleManager
from sync_protocol import SyncProtocol

class DiffusionNode:
    def __init__(self, node_id):
        self.node_id = node_id
        self.port = BASE_PORT + node_id
        self.manager = BundleManager(self.node_id, PERSISTENCE_DIR)
        self.running = True

    def log(self, msg):
        print(f"[NODE {self.node_id}] {msg}")

    def listen(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("127.0.0.1", self.port))
        sock.listen(5)
        self.log(f"Diffusion server listening on {self.port}")
        
        while self.running:
            try:
                conn, addr = sock.accept()
                raw = conn.recv(BUFFER_SIZE)
                if raw:
                    req = json.loads(raw.decode())
                    if req['type'] == 'HELLO':
                        # Someone initiated a sync with us
                        me_need, they_need = SyncProtocol.compare_catalogs(self.manager.get_catalog(), req['catalog'])
                        
                        # Respond with what we want and what we have for them (if they want it)
                        # We'll just respond to their HELLO first.
                        res = {"type": "HELLO_RES", "node": self.node_id, "catalog": self.manager.get_catalog()}
                        conn.sendall(json.dumps(res).encode())
                        
                    elif req['type'] == 'DATA':
                        # We received content!
                        if self.manager.integrate_bundle(req['bundle']):
                            self.log(f"Integrated new bundle: {req['bundle']['id']} from {req['node']}")
                conn.close()
            except: continue

    def scan_and_sync(self):
        """Pick a neighbor and initiate HELLO protocol."""
        while self.running:
            time.sleep(SYNC_SCAN_INTERVAL)
            # Scan ports 9500-9510
            target = random.randint(9500, 9510)
            if target == self.port: continue
            
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.5)
                s.connect(("127.0.0.1", target))
                
                # 1. Send HELLO
                hello = SyncProtocol.create_hello(self.node_id, self.manager.get_catalog())
                s.sendall(json.dumps(hello).encode())
                
                # 2. Get HELLO_RES
                res_raw = s.recv(BUFFER_SIZE)
                if not res_raw: 
                    s.close()
                    continue
                res = json.loads(res_raw.decode())
                
                # 3. Compare catalogs and PUSH any unique data we have
                me_need, they_need = SyncProtocol.compare_catalogs(self.manager.get_catalog(), res['catalog'])
                
                if they_need:
                    for bid in they_need[:3]: # Send top 3 missing bundles
                        bundle = self.manager.get_bundle(bid)
                        if bundle:
                            data = SyncProtocol.create_data_packet(self.node_id, bundle)
                            s.sendall(json.dumps(data).encode())
                            # Simple non-blocking push
                s.close()
            except: pass

    def shell(self):
        print(f"--- Welcome to Content Diffusion Mesh [NODE {self.node_id}] ---")
        while self.running:
            cmd = input("> ").strip().split(" ", 2)
            if not cmd[0]: continue
            
            action = cmd[0].lower()
            if action == "/exit": self.running = False
            elif action == "/catalog":
                print(f"Bundles: {json.dumps(self.manager.get_catalog(), indent=2)}")
            elif action == "/share" and len(cmd) >= 3:
                # /share <app_name> <content>
                bid = self.manager.create_bundle(cmd[2], cmd[1])
                print(f"Published content to mesh. Bundle ID: {bid}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python node.py <node_id>")
        sys.exit(1)
    
    node_id = int(sys.argv[1])
    n = DiffusionNode(node_id)
    threading.Thread(target=n.listen, daemon=True).start()
    threading.Thread(target=n.scan_and_sync, daemon=True).start()
    n.shell()
