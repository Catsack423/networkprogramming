# week10-quantum-network-basic/config.py
HOST = "127.0.0.1"
BASE_PORT = 11000
PEER_PORTS = [11001, 11002, 11003]  # Example peers
BUFFER_SIZE = 1024

# Quantum-inspired constraints
TOKEN_EXPIRY_DEFAULT = 15  # seconds until token becomes invalid (state collapse via decay)
UPDATE_INTERVAL = 3        # routing loop tick interval
