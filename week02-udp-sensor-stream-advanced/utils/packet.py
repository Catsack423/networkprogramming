# utils/packet.py
import json
import time

def create_packet(sensor_id, value):
    """สร้างโครงสร้างข้อมูลสำหรับส่ง"""
    payload = {
        "sensor_id": sensor_id,
        "timestamp": time.time(),
        "value": round(value, 2),
        "unit": "Celsius"
    }
    return json.dumps(payload).encode('utf-8')

def parse_packet(data):
    """แปลง Byte กลับเป็น Dictionary"""
    return json.loads(data.decode('utf-8'))