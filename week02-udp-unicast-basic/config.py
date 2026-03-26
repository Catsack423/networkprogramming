HOST = "127.0.0.1"
PORT = 6000
BUFFER_SIZE = 1024

# Extension C — Rate Control
TOTAL_PACKETS   = 200          # total packets to send
SEND_RATE_PPS   = 50           # target packets-per-second (pps)
# derived interval; sender uses this between packets
SEND_INTERVAL   = 1.0 / SEND_RATE_PPS   # 0.02s = 20ms @ 50 pps

# Receiver buffer / saturation experiment
RECV_QUEUE_WARN = 50           # warn when receiver is this far behind (packets)