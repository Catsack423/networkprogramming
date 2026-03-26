# week10-quantum-messenger-advanced/config.py
BASE_PORT = 11500
BUFFER_SIZE = 4096

# Advanced Quantum Constraints
TOKEN_LIFESPAN = 20         # Ext B: Tokens live slightly longer to allow hopping
MAX_HOPS = 5                # Tokens collapse if passed around too much
STATE_COLLAPSE_PROB = 0.3   # Probability of environmental interference reading the token in transit

LOG_DIR = "logs/"
