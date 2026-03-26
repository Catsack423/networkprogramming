# week08-opportunistic-advanced/config.py
BASE_PORT = 9500
BUFFER_SIZE = 8192
CHUNK_SIZE = 1024  # Size for file splitting

# Diffusion mesh parameters
SYNC_SCAN_INTERVAL = 3
TTL_HOPS = 10
MAX_BUNDLE_LIFETIME = 86400 # 24 hours
PERSISTENCE_DIR = "storage/"
