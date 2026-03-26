# week07-store-forward-planetary/config.py
BASE_PORT = 8500
BUFFER_SIZE = 4096

# DTN (Delay Tolerant Network) Parameters
PLANET_LATENCY = {
    "EARTH": 0,
    "MOON": 1.2,    # seconds
    "MARS": 180,    # seconds (simulated)
}

RETRY_BACKOFF_FACTOR = 1.5
MAX_RETRY_INTERVAL = 300 # 5 minutes
PERSISTENCE_DIR = "storage/"
