# week05-p2p-chat-advanced/router.py
import socket
from utils.protocol import create_msg

class Router:
    def __init__(self, node_id, peer_table):
        self.node_id = node_id
        self.peer_table = peer_table
        self.msg_history = set() # To prevent infinite flooding

    def flood(self, msg_payload):
        """Forwards a message to all known peers (neighbors)."""
        msg_id = f"{msg_payload['sender']}_{msg_payload['timestamp']}"
        
        if msg_id in self.msg_history:
            return # Already handled this message
        
        self.msg_history.add(msg_id)
        
        peers = self.peer_table.get_all_peers()
        for host, port in peers:
            try:
                # In a real system, we might reuse connections. 
                # Here we use short-lived TCP connections for simplicity.
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((host, port))
                sock.sendall(msg_payload['raw_bytes'])
                sock.close()
            except Exception:
                pass # Peer might be offline
