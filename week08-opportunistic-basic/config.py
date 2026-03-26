# week08-opportunistic-basic/config.py
HOST = "127.0.0.1"
BASE_PORT = 9000
BUFFER_SIZE = 4096

# Opportunistic Parameters
SYNC_INTERVAL = 5         # Seconds between sync attempts
SCAN_RANGE = 10           # Range of ports to scan for neighbors (9000-9010)
DEFAULT_MAX_COPIES = 5    # Spray-and-Wait: Max copies allowed in the network
DEFAULT_TTL = 3600        # 1 hour lifetime
PERSISTENCE_FILE = "storage.json"
