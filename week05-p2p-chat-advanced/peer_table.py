# week05-p2p-chat-advanced/peer_table.py
import threading

class PeerTable:
    def __init__(self):
        self.peers = {} # name -> (host, port)
        self.lock = threading.Lock()

    def add_peer(self, name, host, port):
        with self.lock:
            self.peers[name] = (host, port)

    def remove_peer(self, name):
        with self.lock:
            if name in self.peers:
                del self.peers[name]

    def get_all_peers(self):
        with self.lock:
            return list(self.peers.values())

    def get_peer_count(self):
        with self.lock:
            return len(self.peers)

    def __str__(self):
        with self.lock:
            if not self.peers: return "No active peers."
            return "\n".join([f" - {name}: {host}:{port}" for name, (host, port) in self.peers.items()])
