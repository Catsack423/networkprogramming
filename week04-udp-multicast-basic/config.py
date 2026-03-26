# week04-udp-multicast-basic/config.py
# Shared configuration for basic multicast lab.

MULTICAST_GROUP = "224.1.1.1"
PORT = 8000
BUFFER_SIZE = 1024
TTL = 1  # Time-to-Live: 1 means restricted to local network segment
