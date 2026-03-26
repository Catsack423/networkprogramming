# config.py — Shared configuration for LAN Service Discovery

BROADCAST_IP = "255.255.255.255"
PORT = 7100                   # UDP port for broadcast announcements
REPLY_PORT = 7101             # UDP port for unicast replies back to announcer
BUFFER_SIZE = 4096

# How often (seconds) a service re-announces itself
ANNOUNCE_INTERVAL = 5

# How long (seconds) before a registry entry is considered stale
ENTRY_TTL = 15
