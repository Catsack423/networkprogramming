# week09-bio-routing-basic/pheromone_table.py
from config import DECAY_FACTOR

class PheromoneTable:
    def __init__(self):
        self.table = {}  # {peer_port: pheromone_value}

    def reinforce(self, peer, value):
        """Adds pheromone to a path (simulating success/reinforcement)."""
        current = self.table.get(peer, 0.0)
        self.table[peer] = current + value

    def decay(self):
        """Applies evaporation decay to all paths."""
        for peer in self.table:
            self.table[peer] *= DECAY_FACTOR
            
        # Optional: remove extremely weak paths to keep table clean
        self.table = {p: v for p, v in self.table.items() if v > 0.01}

    def get_best_candidates(self, threshold):
        """Returns peers that have a pheromone level above the threshold, sorted by strength."""
        candidates = [(peer, pher) for peer, pher in self.table.items() if pher >= threshold]
        candidates.sort(key=lambda x: x[1], reverse=True)
        return [peer for peer, pher in candidates]
        
    def get_all(self):
        return self.table
