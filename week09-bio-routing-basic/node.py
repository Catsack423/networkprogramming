# week09-bio-routing-basic/node.py
import socket
import threading
import time
import sys
import json
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque
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

        # Initialize base pheromones for known peers
        for peer in PEER_PORTS:
            if peer != self.port:
                self.pheromones.reinforce(peer, INITIAL_PHEROMONE)

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
                self.pheromones.reinforce(peer_port, total_reinforcement)
                return True
        except:
            pass
        
        return False

    def forward_loop(self):
        """Main routing loop (Ant colony iteration step)."""
        while self.running:
            # 1. Decay all paths
            self.pheromones.decay()
            
            # 2. Find paths with enough pheromone to be considered
            candidates = self.pheromones.get_best_candidates(FORWARD_THRESHOLD)
            
            if candidates:
                # 3. Opportunistically try to forward queued messages
                for packet in self.queue[:]:
                    for peer in candidates:
                        if self.send_packet(peer, packet):
                            # Success! Remove from local queue and break candidate loop
                            self.queue.remove(packet)
                            self.log(f"Delivered buffered message to {peer}")
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
                print("--- Pheromone Table ---")
                for peer, val in self.pheromones.get_all().items():
                    print(f" Port {peer}: {val:.3f}")
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
                
                # Immediate attempt logic: Pick best candidate
                candidates = self.pheromones.get_best_candidates(FORWARD_THRESHOLD)
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
        # Start a simple plot to visualize pheromone evolution over time
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.set_title(f"Node {port}: Pheromone Evolution Over Time")
        ax.set_xlabel("Time (ticks)")
        ax.set_ylabel("Pheromone Strength")
        
        # Keep track of history: { "T_N": deque([...]) }
        MAX_HISTORY = 60
        history = {}
        time_data = deque(maxlen=MAX_HISTORY)
        tick_counter = [0]
        
        def update_plot(frame):
            ax.clear()
            ax.set_ylim(0, 5)
            ax.set_title(f"Node {port}: Pheromone Evolution Over Time")
            ax.set_xlabel("Time (ticks)")
            ax.set_ylabel("Pheromone Strength")
            ax.axhline(y=FORWARD_THRESHOLD, color='r', linestyle='--', label='Threshold')
            
            table = n.pheromones.get_all()
            tick_counter[0] += 1
            time_data.append(tick_counter[0])
            
            # Ensure all known paths have a deque
            current_keys = set()
            for target, peers in table.items():
                for peer, val in peers.items():
                    key = f"Target {target} via {peer}"
                    current_keys.add(key)
                    if key not in history:
                        # Pad with zeros for previous ticks if it's a newly discovered path
                        history[key] = deque([0] * (len(time_data) - 1), maxlen=MAX_HISTORY)
                    history[key].append(val)
                    
            # Pad keys that disappeared (decayed below 0.01) with 0
            for key in list(history.keys()): # Iterate over a copy to allow modification
                if key not in current_keys:
                    history[key].append(0)
                    
            # Plot the lines
            has_data = False
            for key, y_data in history.items():
                # Only plot lines that actually existed or have current value > 0
                if any(val > 0.01 for val in y_data): 
                    ax.plot(time_data, y_data, marker='.', label=key)
                    has_data = True
                    
            if has_data:
                ax.legend(loc='upper right')
        
        ani = animation.FuncAnimation(fig, update_plot, interval=1000)
        plt.ion()
        plt.show(block=False)

    n.cmd_loop()

if __name__ == "__main__":
    main()
