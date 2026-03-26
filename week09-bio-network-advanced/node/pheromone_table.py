# week09-bio-network-advanced/node/pheromone_table.py
from config import DECAY_FACTOR, REINFORCEMENT_FAILURE

class PheromoneTable:
    def __init__(self):
        # Maps target_id -> { neighbor_id: priority }
        # Ant routing: "To get to target X, how good is neighbor Y?"
        self.routing_table = {}

    def init_target(self, target_id, initial_val):
        if target_id not in self.routing_table:
            self.routing_table[target_id] = {}

    def reinforce(self, target_id, neighbor_id, value):
        self.init_target(target_id, 0.0)
        current = self.routing_table[target_id].get(neighbor_id, 0.0)
        # Prevent pheromones from going below 0 or above a cap if needed
        self.routing_table[target_id][neighbor_id] = max(0.001, current + value)

    def penalize(self, target_id, neighbor_id):
        self.reinforce(target_id, neighbor_id, REINFORCEMENT_FAILURE)

    def decay(self):
        """Evaporate pheromones across all targets and neighbors."""
        for target_id, neighbors in list(self.routing_table.items()):
            for neighbor_id in list(neighbors.keys()):
                self.routing_table[target_id][neighbor_id] *= DECAY_FACTOR
                # Cleanup dead links
                if self.routing_table[target_id][neighbor_id] < 0.05:
                    del self.routing_table[target_id][neighbor_id]
            if not self.routing_table[target_id]:
                del self.routing_table[target_id]

    def get_best_candidates(self, target_id, threshold):
        """Return list of neighbor IDs to forward a packet to."""
        if target_id not in self.routing_table:
            return []
            
        candidates = [(nid, p) for nid, p in self.routing_table[target_id].items() if p >= threshold]
        candidates.sort(key=lambda x: x[1], reverse=True)
        return [nid for nid, p in candidates]
        
    def get_table(self):
        return self.routing_table
