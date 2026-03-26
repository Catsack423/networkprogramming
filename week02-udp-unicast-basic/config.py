HOST = "127.0.0.1"
PORT = 6000
BUFFER_SIZE = 1024

# Extension B — Manual ACK
ACK_PORT    = 6001    # receiver sends ACK back on this port
ACK_TIMEOUT = 1.0     # seconds sender waits for ACK before retrying
MAX_RETRIES = 3       # max number of retransmissions per packet
TOTAL_PACKETS = 10    # total packets sender will send