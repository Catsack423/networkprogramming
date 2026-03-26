# week06-manet-basic/config.py
HOST = "127.0.0.1"
BASE_PORT = 7000
BUFFER_SIZE = 1024

# Initial neighbors (static for Step 0, can be dynamic later)
NEIGHBORS = [] 

# MANET Parameters
FORWARD_PROBABILITY = 0.6  # 60% chance to relay
DEFAULT_TTL = 3            # Max hops
DISCOVERY_INTERVAL = 5     # Seconds between neighbor pings
MOBILITY_INTERVAL = 10     # Seconds for random neighbor shifts
