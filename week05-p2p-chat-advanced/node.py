# week05-p2p-chat-advanced/node.py
import socket
import threading
import sys
import time
from config import BASE_PORT, BUFFER_SIZE, ENCODING
from utils.protocol import create_msg, parse_msg
from peer_table import PeerTable
from router import Router

class P2PNode:
    def __init__(self, node_id, port):
        self.node_id = node_id
        self.port = port
        self.peer_table = PeerTable()
        self.router = Router(node_id, self.peer_table)
        self.running = True

    def listen(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("127.0.0.1", self.port))
        sock.listen(5)
        print(f"[NODE {self.node_id}] Listening on port {self.port}")

        while self.running:
            try:
                conn, addr = sock.accept()
                data = conn.recv(BUFFER_SIZE)
                if data:
                    msg = parse_msg(data)
                    if msg:
                        self.handle_message(msg, data)
                conn.close()
            except Exception as e:
                if self.running: print(f"Error in listener: {e}")

    def handle_message(self, msg, raw_data):
        m_type = msg.get("type")
        sender = msg.get("sender")
        
        if m_type == "CHAT":
            print(f"\n[CHAT] {sender}: {msg['content']}")
            # Forward the message to others (Flooding)
            msg['raw_bytes'] = raw_data
            self.router.flood(msg)
        
        elif m_type == "HELLO":
            host, port = msg['extra']['host'], msg['extra']['port']
            self.peer_table.add_peer(sender, host, port)
            print(f"\n[SYSTEM] Peer '{sender}' discovered at {host}:{port}")

    def announce_self(self, target_host, target_port):
        """Connects to a known peer to join the network."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((target_host, target_port))
            hello = create_msg("HELLO", self.node_id, extra={"host": "127.0.0.1", "port": self.port})
            sock.sendall(hello)
            sock.close()
            print(f"[SYSTEM] Connection request sent to {target_host}:{target_port}")
        except Exception as e:
            print(f"[SYSTEM] Could not connect to {target_host}:{target_port}: {e}")

    def send_chat(self, content):
        msg_bytes = create_msg("CHAT", self.node_id, content)
        # Store in router history to prevent self-processing
        import json; msg_dict = json.loads(msg_bytes.decode(ENCODING))
        msg_dict['raw_bytes'] = msg_bytes
        self.router.flood(msg_dict)

def main():
    if len(sys.argv) < 3:
        print("Usage: python node.py <node_id> <port> [target_port_to_join]")
        return

    node_id = sys.argv[1]
    port = int(sys.argv[2])
    
    node = P2PNode(node_id, port)
    threading.Thread(target=node.listen, daemon=True).start()
    
    time.sleep(1)

    if len(sys.argv) > 3:
        target_port = int(sys.argv[3])
        node.announce_self("127.0.0.1", target_port)

    print(f"\n--- Node {node_id} Ready ---")
    print("Commands: /peers (list peers), /exit, or type a message to broadcast")

    try:
        while True:
            cmd = input("> ")
            if cmd == "/exit":
                node.running = False
                break
            elif cmd == "/peers":
                print(f"Known Peers:\n{node.peer_table}")
            elif cmd.strip():
                node.send_chat(cmd)
    except KeyboardInterrupt:
        pass
    print("Shutting down...")

if __name__ == "__main__":
    main()
