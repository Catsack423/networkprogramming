# week09-bio-network-advanced/node/node.py
import socket
import threading
import sys
import json
import time
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import BASE_PORT, BUFFER_SIZE, UPDATE_INTERVAL, FORWARD_THRESHOLD, INITIAL_PHEROMONE, REINFORCEMENT_SUCCESS, SIMULATION_TICK, LINK_FLAP_PROB
from pheromone_table import PheromoneTable
from encounter_simulator import EncounterSimulator
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../utils')))
from logger import MetricLogger

class SelfHealingNode:
    def __init__(self, node_id, peers):
        self.id = node_id
        self.port = BASE_PORT + node_id
        self.peers = peers
        self.pheromones = PheromoneTable()
        self.simulator = EncounterSimulator(node_id, peers, LINK_FLAP_PROB)
        self.logger = MetricLogger(node_id)
        self.queue = []
        self.running = True

        # Initialize base pheromones (Assume everyone can route to everyone via themselves initially)
        for peer in self.peers:
            self.pheromones.reinforce(peer, peer, INITIAL_PHEROMONE)

    def log(self, msg):
        term_msg = f"[NODE {self.id}] {msg}"
        print(term_msg)
        self.logger.log_event("INFO", msg)

    def send_packet(self, neighbor_id, packet):
        """Attempts to send a packet to a neighbor."""
        # Check simulation constraints first
        if not self.simulator.is_reachable(neighbor_id):
            return False

        try:
            start = time.time()
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1.0)
            s.connect(("127.0.0.1", BASE_PORT + neighbor_id))
            s.sendall(json.dumps(packet).encode())
            
            # Wait for ACK
            response = s.recv(BUFFER_SIZE)
            rtt = time.time() - start
            s.close()
            
            if response:
                # Reinforce this neighbor for the specific target
                target_id = packet['target']
                # Dynamic reinforcement: faster RTT = more pheromone
                bonus = max(0, 0.5 - rtt)
                self.pheromones.reinforce(target_id, neighbor_id, REINFORCEMENT_SUCCESS + bonus)
                self.logger.log_event("REINFORCE", {"target": target_id, "neighbor": neighbor_id, "rtt": rtt})
                return True
        except Exception:
            pass
            
        return False

    def forward_loop(self):
        """Ant colony iteration: Decay, route queued messages, penalize failures."""
        while self.running:
            self.pheromones.decay()
            self.logger.log_event("DECAY", self.pheromones.get_table())
            
            for packet in self.queue[:]:
                target = packet['target']
                
                # If we are the target, we shouldn't be forwarding it, but just in case
                if target == self.id:
                    self.queue.remove(packet)
                    continue

                candidates = self.pheromones.get_best_candidates(target, FORWARD_THRESHOLD)
                
                # If no candidates, fallback to trying all active links (exploration)
                if not candidates:
                    candidates = self.simulator.get_active_links()

                sent = False
                for neighbor in candidates:
                    # Don't send back where it came from
                    if 'path' in packet and packet['path'] and packet['path'][-1] == neighbor:
                        continue
                        
                    packet['path'] = packet.get('path', [])
                    if self.id not in packet['path']:
                        packet['path'].append(self.id)
                        
                    if self.send_packet(neighbor, packet):
                        self.queue.remove(packet)
                        self.log(f"Forwarded msg to {target} via {neighbor}")
                        sent = True
                        break
                    else:
                        # Penalize broken links
                        self.log(f"Link to {neighbor} down. Penalizing.")
                        self.pheromones.penalize(target, neighbor)
                        
                if not sent and candidates:
                    self.log(f"All candidates for {target} failed. Packet remains in queue.")

            time.sleep(UPDATE_INTERVAL)

    def env_simulator_loop(self):
        """Runs the link flapping simulation."""
        while self.running:
            if self.simulator.tick():
                active = self.simulator.get_active_links()
                self.log(f"Environment Shift! Active Links: {active}")
                self.logger.log_event("ENV_SHIFT", active)
            time.sleep(SIMULATION_TICK)

    def listen(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("127.0.0.1", self.port))
        sock.listen(5)
        
        while self.running:
            try:
                conn, addr = sock.accept()
                raw = conn.recv(BUFFER_SIZE)
                if raw:
                    packet = json.loads(raw.decode())
                    target = packet.get('target')
                    
                    if target == self.id:
                        path_str = " -> ".join(map(str, packet.get('path', [])))
                        self.log(f"\n[INBOX] Msg: '{packet['msg']}' | Path taken: {path_str} -> {self.id}")
                        conn.sendall(b"ACK")
                    else:
                        self.queue.append(packet)
                        conn.sendall(b"ACK_QUEUED")
                conn.close()
            except: continue

    def shell(self):
        print(f"--- Self-Healing Bio-Node [{self.id}] ---")
        while self.running:
            cmd = input("> ").strip().split(" ", 2)
            if not cmd[0]: continue
            
            action = cmd[0].lower()
            if action == "/exit": self.running = False
            elif action == "/table":
                print(json.dumps(self.pheromones.get_table(), indent=2))
            elif action == "/links":
                print(f"Active links: {self.simulator.get_active_links()}")
            elif action == "/send" and len(cmd) >= 3:
                target = int(cmd[1])
                msg = cmd[2]
                self.queue.append({
                    "target": target,
                    "msg": msg,
                    "origin": self.id,
                    "path": [self.id]
                })
                print(f"Queued message for {target}.")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python node.py <node_id> <peer1_id> <peer2_id> ...")
        sys.exit(1)
    
    node_id = int(sys.argv[1])
    peers = [int(p) for p in sys.argv[2:]]
    
    n = SelfHealingNode(node_id, peers)
    threading.Thread(target=n.listen, daemon=True).start()
    threading.Thread(target=n.forward_loop, daemon=True).start()
    threading.Thread(target=n.env_simulator_loop, daemon=True).start()
    n.shell()
