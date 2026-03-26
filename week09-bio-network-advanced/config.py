# week09-bio-network-advanced/config.py
BASE_PORT = 10500
BUFFER_SIZE = 4096

# Pheromone routing parameters (Advanced)
INITIAL_PHEROMONE = 1.0
DECAY_FACTOR = 0.85
REINFORCEMENT_SUCCESS = 0.4
REINFORCEMENT_FAILURE = -0.3 # Penalize broken links faster
FORWARD_THRESHOLD = 0.2
UPDATE_INTERVAL = 2

# Encounter Simulation
SIMULATION_TICK = 1.0
LINK_FLAP_PROB = 0.1         # 10% chance a link goes down or comes up each tick
