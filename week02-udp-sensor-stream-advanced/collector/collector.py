# collector/collector.py
import socket
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import COLLECTOR_HOST, COLLECTOR_PORT, BUFFER_SIZE
from utils.packet import parse_packet

def start_collector():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((COLLECTOR_HOST, COLLECTOR_PORT))
    
    print(f"[COLLECTOR] Listening on {COLLECTOR_HOST}:{COLLECTOR_PORT}")
    print("Press Ctrl+C to stop.")

    try:
        while True:
            data, addr = sock.recvfrom(BUFFER_SIZE)
            try:
                payload = parse_packet(data)
                s_id = payload.get("sensor_id")
                val = payload.get("value")
                ts = payload.get("timestamp")
                
                print(f"[DATA] From {addr} | ID: {s_id} | Value: {val} | TS: {ts}")
            except Exception as e:
                print(f"[ERROR] Failed to parse data: {e}")
                
    except KeyboardInterrupt:
        print("\n[COLLECTOR] Shutting down.")
    finally:
        sock.close()

if __name__ == "__main__":
    start_collector()