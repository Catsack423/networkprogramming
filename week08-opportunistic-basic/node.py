# week08-opportunistic-basic/node.py
import socket
import threading
import time
import sys
import json
import random
from config import HOST, BUFFER_SIZE, SYNC_INTERVAL, SCAN_RANGE, DEFAULT_MAX_COPIES, DEFAULT_TTL
from message_store import MessageStore

class OpportunisticNode:
    def __init__(self, port):
        self.port = port
        self.store = MessageStore(f"store_{port}.json")
        self.running = True

    def log(self, msg):
        print(f"[NODE {self.port}] {msg}")

    def sync_with_neighbor(self, neighbor_port):
        """Anti-entropy: Exchange inventories and sync missing data."""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1.0)
            s.connect((HOST, neighbor_port))
            
            # 1. Send our inventory
            my_inv = self.store.get_inventory()
            request = {"type": "SYNC_REQ", "sender": self.port, "inventory": my_inv}
            s.sendall(json.dumps(request).encode())
            
            # 2. Receive their missing IDs or their inventory
            response_raw = s.recv(BUFFER_SIZE)
            if not response_raw: return
            response = json.loads(response_raw.decode())
            
            if response['type'] == 'SYNC_RES':
                # They sent us what they need from us
                needed_ids = response['needed']
                for mid in needed_ids:
                    msg = self.store.get_message(mid)
                    if msg and msg['copies_left'] > 1:
                        # Spray-and-Wait: Give half of our copies to the neighbor
                        shared_copies = msg['copies_left'] // 2
                        msg['copies_left'] -= shared_copies
                        msg['hops'] += 1
                        
                        data_packet = {
                            "type": "DATA",
                            "msg": {**msg, "copies_left": shared_copies}
                        }
                        s.sendall(json.dumps(data_packet).encode())
                        # Note: In a real protocol, we'd wait for ACK before decrementing locally
                        self.store._save() 
            s.close()
        except: pass

    def serve(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((HOST, self.port))
        sock.listen(5)
        
        while self.running:
            try:
                conn, addr = sock.accept()
                raw = conn.recv(BUFFER_SIZE)
                if raw:
                    req = json.loads(raw.decode())
                    if req['type'] == 'SYNC_REQ':
                        # Someone wants to sync with us
                        neighbor_inv = set(req['inventory'])
                        my_inv = set(self.store.get_inventory())
                        
                        # What do I have that they don't?
                        needed_by_them = list(my_inv - neighbor_inv)
                        
                        # What do they have that I don't?
                        needed_by_me = list(neighbor_inv - my_inv)
                        
                        res = {"type": "SYNC_RES", "needed": needed_by_them, "i_have": list(my_inv)}
                        conn.sendall(json.dumps(res).encode())
                        
                        # Now wait for them to send DATA if they have stuff for me
                        # (Simplification: In a real epidemic protocol, this is a 3-way handshake)
                conn.close()
            except: continue

    def discovery_loop(self):
        """Periodically pick a random peer in range and try to sync."""
        while self.running:
            time.sleep(SYNC_INTERVAL)
            target = random.randint(9000, 9000 + SCAN_RANGE)
            if target == self.port: continue
            self.sync_with_neighbor(target)

def main():
    if len(sys.argv) < 2:
        print("Usage: python node.py <port>")
        return

    port = int(sys.argv[1])
    node = OpportunisticNode(port)
    
    threading.Thread(target=node.serve, daemon=True).start()
    threading.Thread(target=node.discovery_loop, daemon=True).start()

    print(f"--- Opportunistic Sync Node {port} Ready ---")
    print("Commands: /msg <text>, /list, /exit")

    try:
        while True:
            cmd = input("> ").strip().split(" ", 1)
            if not cmd[0]: continue
            
            if cmd[0] == "/exit":
                node.running = False
                break
            elif cmd[0] == "/list":
                inv = node.store.messages
                print(f"Stored Messages: {len(inv)}")
                for mid, m in inv.items():
                    print(f" - [{m['origin']}] '{m['body']}' (Copies: {m['copies_left']}, Hops: {m['hops']})")
            elif cmd[0] == "/msg" and len(cmd) > 1:
                mid = f"{port}_{time.time()}"
                node.store.add(mid, cmd[1], port, DEFAULT_MAX_COPIES, DEFAULT_TTL)
                print("Message created. Will diffuse opportunistically.")
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
