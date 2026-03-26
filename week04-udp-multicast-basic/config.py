# week04-udp-multicast-basic/config.py
PORT = 8000
BUFFER_SIZE = 1024
TTL = 1

# Extension 2 & 3: Channels
CHANNELS = {
    "sports":  "224.1.1.1",
    "news":    "224.1.1.2",
    "weather": "224.1.1.3",
    "alerts":  "224.1.1.4"
}
