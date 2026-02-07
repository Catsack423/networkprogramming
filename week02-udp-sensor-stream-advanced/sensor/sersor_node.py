# sensor/sensor_node.py
import socket
import time
import random
import sys
import os

# เพิ่ม Path เพื่อให้เรียกใช้ config และ utils ได้
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import COLLECTOR_HOST, COLLECTOR_PORT, SEND_INTERVAL
from utils.packet import create_packet

def run_sensor(sensor_id):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print(f"[SENSOR {sensor_id}] Started streaming to {COLLECTOR_HOST}:{COLLECTOR_PORT}")

    try:
        temp = 25.0 # อุณหภูมิเริ่มต้น
        while True:
            # จำลองการเปลี่ยนแปลงของอุณหภูมิแบบ Random Walk
            temp += random.uniform(-0.5, 0.5)
            
            packet = create_packet(sensor_id, temp)
            sock.sendto(packet, (COLLECTOR_HOST, COLLECTOR_PORT))
            
            print(f"[SENT] {sensor_id} -> {temp:.2f}°C")
            time.sleep(SEND_INTERVAL)
    except KeyboardInterrupt:
        print(f"\n[SENSOR {sensor_id}] Stopped.")
    finally:
        sock.close()

if __name__ == "__main__":
    # รับชื่อ Sensor จาก Command Line เช่น python sensor_node.py SENSOR_01
    s_id = sys.argv[1] if len(sys.argv) > 1 else "UNKOWN_SENSOR"
    run_sensor(s_id)