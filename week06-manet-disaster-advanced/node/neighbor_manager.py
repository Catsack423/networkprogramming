# week06-manet-disaster-advanced/node/neighbor_manager.py
import socket
import threading
import time
from config import BASE_PORT, DISCOVERY_PING_INTERVAL

class NeighborManager:
    def __init__(self, node_port, role):
        self.node_port = node_port
        self.role = role
        self.neighbors = {} # port -> last_seen
        self.lock = threading.Lock()
        self.running = True

    def start_discovery(self):
        """Periodically pings ports 7500-7510 to find mesh neighbors."""
        threading.Thread(target=self._discovery_loop, daemon=True).start()

    def _discovery_loop(self):
        while self.running:
            for p in range(7500, 7511):
                if p == self.node_port: continue
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(0.3)
                    s.connect(("127.0.0.1", p))
                    s.close()
                    with self.lock:
                        self.neighbors[p] = time.time()
                except:
                    pass
            self._cleanup_old_neighbors()
            time.sleep(DISCOVERY_PING_INTERVAL)

    def _cleanup_old_neighbors(self):
        now = time.time()
        with self.lock:
            # Drop neighbors not seen in 10 seconds
            self.neighbors = {p: t for p, t in self.neighbors.items() if now - t < 10}

    def get_neighbors(self):
        with self.lock:
            return list(self.neighbors.keys())
