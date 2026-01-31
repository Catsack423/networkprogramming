import socket
import threading
from config import HOST, PORT
from server.client_handler import handle_client
from server.logger import log_message

def start_server():
    # สร้าง Socket และตั้งค่าพื้นฐาน
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)
        server_socket.settimeout(1.0) # กัน accept() ค้างเพื่อให้กด Ctrl+C ได้
        
        clients = []
        log_message(f"Chat Server started on {HOST}:{PORT}")

        while True:
            try:
                conn, addr = server_socket.accept()
                clients.append(conn)
                thread = threading.Thread(target=handle_client, args=(conn, addr, clients))
                thread.daemon = True
                thread.start()
                log_message(f"Active connections: {len(clients)}")
                
            except (TimeoutError, socket.timeout):
                # ปล่อยให้วนลูปต่อไป เพื่อรอรับคนใหม่หรือรอรับ Ctrl+C
                continue 
                
    except KeyboardInterrupt:
        # ดักจับการกด Ctrl+C ที่นี่ที่เดียวให้จบ
        log_message("\n[SERVER] Shutdown signal received (Ctrl+C).")
    except Exception as e:
        log_message(f"[ERROR] {e}")
    finally:
        # ส่วนนี้จะทำงานเสมอไม่ว่าจะจบแบบปกติหรือ Error
        log_message("[SERVER] Cleaning up resources...")
        
        # ปิด Client ทุกคนที่ค้างอยู่
        if 'clients' in locals():
            for c in clients:
                try:
                    c.close()
                except:
                    pass
        
        server_socket.close()
        log_message("[SERVER] Server closed successfully.")

if __name__ == "__main__":
    start_server()