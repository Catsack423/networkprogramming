# week09-bio-routing-basic/node.py
import socket
import threading
import time
import sys
import json
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from config import HOST, BASE_PORT, PEER_PORTS, BUFFER_SIZE, FORWARD_THRESHOLD, UPDATE_INTERVAL, REINFORCEMENT, DECAY_FACTOR, INITIAL_PHEROMONE
from pheromone_table import PheromoneTable

class BioNode:
    def __init__(self, port):
        self.port = port
        self.pheromones = PheromoneTable()
        self.queue = []
        self.running = True
        
        # Extension A: Tracking round-trip latency to adjust reinforcement
        self.latency_stats = {} 

        # Initialize base pheromones for known peers (direct link = assume they are their own target)
        for peer in PEER_PORTS:
            if peer != self.port:
                self.pheromones.reinforce(peer, peer, INITIAL_PHEROMONE)

    def log(self, msg):
        print(f"[NODE {self.port}] {msg}")

    def send_packet(self, peer_port, packet):
        try:
            start_time = time.time()
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2.0)
            s.connect((HOST, peer_port))
            s.sendall(json.dumps(packet).encode())
            
            # Simulated ACK wait (Optional Extension A behavior)
            response = s.recv(BUFFER_SIZE)
            rtt = time.time() - start_time
            s.close()
            
            if response:
                # Extension A: Dynamic Reinforcement based on RTT
                # Faster responses get higher reinforcement
                dynamic_bonus = max(0, 0.5 - rtt)
                total_reinforcement = REINFORCEMENT + dynamic_bonus
                # Extension B: target is stored in packet
                self.pheromones.reinforce(packet['target'], peer_port, total_reinforcement)
                return True
        except:
            pass
        
        return False

    def forward_loop(self):
        """Main routing loop (Ant colony iteration step)."""
        while self.running:
            # 1. Decay all paths
            self.pheromones.decay()
            
            # 2. Opportunistically try to forward queued messages
            for packet in self.queue[:]:
                target = packet['target']
                candidates = self.pheromones.get_best_candidates(target, FORWARD_THRESHOLD)
                
                # Simple fallback: if no known path, probe all known peers
                if not candidates:
                    candidates = [p for p in PEER_PORTS if p != self.port]
                    
                for peer in candidates:
                    # Prevent routing loops
                    if 'path' in packet and packet['path'] and packet['path'][-1] == peer:
                        continue
                        
                    packet['path'] = packet.get('path', [])
                    if self.port not in packet['path']:
                        packet['path'].append(self.port)
                        
                    if self.send_packet(peer, packet):
                        self.queue.remove(packet)
                        self.log(f"Delivered buffered message to {peer} (Target: {target})")
                        break
            
            time.sleep(UPDATE_INTERVAL)

    def serve(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((HOST, self.port))
        sock.listen(5)
        self.log(f"Listening on {self.port}")
        
        while self.running:
            try:
                conn, addr = sock.accept()
                raw = conn.recv(BUFFER_SIZE)
                if raw:
                    packet = json.loads(raw.decode())
                    
                    if packet['target'] == self.port:
                        self.log(f"--- INBOX: From {packet['origin']} -> '{packet['msg']}' ---")
                        # ACK the message (helps with Extension A RTT calculation)
                        conn.sendall(b"ACK")
                    else:
                        # We are just a router.
                        # Extension B: Multi-Hop simulation. 
                        # We add it to our queue to forward later.
                        self.log(f"Relaying packet intended for {packet['target']}")
                        packet['hops'] = packet.get('hops', 0) + 1
                        self.queue.append(packet)
                        conn.sendall(b"ACK_QUEUED")
                conn.close()
            except: continue

    def cmd_loop(self):
        print(f"--- Bio-Inspired Node {self.port} Ready ---")
        print("Commands: /msg <target_port> <text>, /table, /exit")
        while self.running:
            cmd = input("> ").strip().split(" ", 2)
            if not cmd[0]: continue
            
            action = cmd[0].lower()
            if action == "/exit": self.running = False
            elif action == "/table":
                print("--- Pheromone Table (Target -> Peer) ---")
                table = self.pheromones.get_all()
                if not table: print(" Empty.")
                for t, peers in table.items():
                    for p, val in peers.items():
                        print(f" Target {t} via {p}: {val:.3f}")
                print(f" Threshold: {FORWARD_THRESHOLD}")
            elif action == "/msg" and len(cmd) >= 3:
                target = int(cmd[1])
                body = cmd[2]
                packet = {
                    "origin": self.port,
                    "target": target,
                    "msg": body,
                    "hops": 0
                }
                
                # Immediate attempt logic
                candidates = self.pheromones.get_best_candidates(target, FORWARD_THRESHOLD)
                
                # Fallback to direct try if no path
                if not candidates:
                    candidates = [p for p in PEER_PORTS if p != self.port]
                    
                sent = False
                for peer in candidates:
                    if self.send_packet(peer, packet):
                        print(f"Sent immediately via {peer}")
                        sent = True
                        break
                
                if not sent:
                    print("No available paths. Queued for opportunistic forwarding.")
                    self.queue.append(packet)

def main():
    if len(sys.argv) < 2:
        print("Usage: python node.py <port> [--plot]")
        return

    port = int(sys.argv[1])
    n = BioNode(port)
    
    threading.Thread(target=n.serve, daemon=True).start()
    threading.Thread(target=n.forward_loop, daemon=True).start()

    # Extension C: Logging & Visualization (Optional Matplotlib plot)
    if "--plot" in sys.argv:
        # Start a simple plot to visualize pheromone evolution
        fig, ax = plt.subplots()
        ax.set_ylim(0, 5)
        ax.set_title(f"Node {port} Pheromone Levels")
        
        def update_plot(frame):
            ax.clear()
            ax.set_ylim(0, 5)
            ax.set_title(f"Node {port} Pheromone Levels")
            table = n.pheromones.get_all()
            
            # Flatten table for plotting
            labels = []
            values = []
            for t, peers in table.items():
                for p, val in peers.items():
                    labels.append(f"T:{t}\nP:{p}")
                    values.append(val)
                    
            if labels:
                ax.bar(labels, values, color='green')
                ax.axhline(y=FORWARD_THRESHOLD, color='r', linestyle='--', label='Threshold')
                ax.legend()
        
        ani = animation.FuncAnimation(fig, update_plot, interval=1000)
        # Run plot in non-blocking mode (not strictly perfect CLI integration, but works for lab demo)
        plt.ion()
        plt.show(block=False)

    n.cmd_loop()

if __name__ == "__main__":
    main()
