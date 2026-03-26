# week07-store-forward-basic/config.py
HOST = "127.0.0.1"
BASE_PORT = 8000
BUFFER_SIZE = 1024

# Retry Parameters
RETRY_INTERVAL = 5        # Initial retry interval in seconds
MAX_RETRY_BACKOFF = 60    # Maximum backoff interval
PERSISTENCE_FILE = "queue.json"
