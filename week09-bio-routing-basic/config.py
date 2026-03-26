# week09-bio-routing-basic/config.py
HOST = "127.0.0.1"
BASE_PORT = 10000
PEER_PORTS = [10001, 10002, 10003]  # Local peers to interact with
BUFFER_SIZE = 1024

# Pheromone routing parameters
INITIAL_PHEROMONE = 1.0
DECAY_FACTOR = 0.9           # Pheromones decay by 10% each tick
REINFORCEMENT = 0.5          # Amount added on successful delivery
FORWARD_THRESHOLD = 0.2      # Minimum pheromone level required to consider a peer
UPDATE_INTERVAL = 3          # Seconds between decay cycles and forward attempts
