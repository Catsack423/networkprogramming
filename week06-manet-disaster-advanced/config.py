# week06-manet-disaster-advanced/config.py
BASE_PORT = 7500
BUFFER_SIZE = 4096

# MANET Advanced Parameters
DISCOVERY_PING_INTERVAL = 3
MSG_CLEANUP_INTERVAL = 60 # Seconds to keep msg IDs in history
DEFAULT_PROBABILITY = 0.7
MAX_TTL = 5

# Node States
ROLES = ["RESCUE_TEAM", "VICTIM", "HQ"]
