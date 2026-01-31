from config import BUFFER_SIZE, ENCODING
from server.logger import log_message

def handle_client(conn, addr, clients):
    log_message(f"New connection from {addr}")
    try:
        while True:
            data = conn.recv(BUFFER_SIZE)
            if not data:
                break
            
            message = data.decode(ENCODING)
            log_message(f"Message from {addr}: {message}")
            
            # Broadcast: ส่งข้อความให้ทุกคนที่เชื่อมต่ออยู่
            broadcast(message, conn, clients)
            
    except ConnectionResetError:
        log_message(f"Client {addr} forcibly disconnected.")
    finally:
        clients.remove(conn)
        conn.close()
        log_message(f"Connection closed for {addr}")

def broadcast(message, sender_conn, clients):
    for client in clients:
        # ไม่ส่งกลับไปหาตัวเอง (Optional)
        if client != sender_conn:
            try:
                client.sendall(f"Broadcast: {message}".encode(ENCODING))
            except:
                client.close()
                clients.remove(client)