# week09-bio-network-advanced/node/encounter_simulator.py
import random
import time

class EncounterSimulator:
    """Simulates dynamic link availability to force the routing to heal."""
    
    def __init__(self, node_id, active_peers, link_flap_prob):
        self.node_id = node_id
        self.flap_prob = link_flap_prob
        # State: Which peers are currently "reachable"
        self.link_states = {peer: True for peer in active_peers}
        
    def tick(self):
        """Randomly toggles link states to simulate mobile nodes or interference."""
        changed = False
        for peer in self.link_states:
            if random.random() < self.flap_prob:
                self.link_states[peer] = not self.link_states[peer]
                changed = True
        return changed

    def is_reachable(self, peer_id):
        return self.link_states.get(peer_id, False)
        
    def get_active_links(self):
        return [p for p, active in self.link_states.items() if active]
