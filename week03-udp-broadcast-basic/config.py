BROADCAST_IP  = "255.255.255.255"
PORT          = 7000    # broadcaster → listeners (broadcast)
BUFFER_SIZE   = 1024

# Extension A — Broadcast Discovery + Reply
REPLY_PORT    = 7001    # listeners → broadcaster (unicast reply)
REPLY_TIMEOUT = 3.0     # seconds broadcaster waits for replies
