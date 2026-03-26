# week09-bio-routing-basic/pheromone_table.py
from config import DECAY_FACTOR

class PheromoneTable:
    def __init__(self):
        # Extension B: target -> {peer_port: pheromone_value}
        self.table = {}

    def reinforce(self, target, peer, value):
        """Adds pheromone to a path (simulating success/reinforcement)."""
        if target not in self.table:
            self.table[target] = {}
        current = self.table[target].get(peer, 0.0)
        self.table[target][peer] = current + value

    def decay(self):
        """Applies evaporation decay to all paths."""
        for target, peers in list(self.table.items()):
            for peer in list(peers.keys()):
                self.table[target][peer] *= DECAY_FACTOR
                if self.table[target][peer] <= 0.01:
                    del self.table[target][peer]
            if not self.table[target]:
                del self.table[target]

    def get_best_candidates(self, target, threshold):
        """Returns peers that have a pheromone level above the threshold for the target."""
        if target not in self.table:
            return []
        candidates = [(peer, pher) for peer, pher in self.table[target].items() if pher >= threshold]
        candidates.sort(key=lambda x: x[1], reverse=True)
        return [peer for peer, pher in candidates]
        
    def get_all(self):
        return self.table
