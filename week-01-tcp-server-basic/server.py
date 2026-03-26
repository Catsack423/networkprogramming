import socket
from config import HOST, PORT, BUFFER_SIZE

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen(5)

print(f"[SERVER] Listening on {HOST}:{PORT}")
print("[SERVER] Extension A — Sequential mode (Ctrl+C to stop)\n")

client_count = 0

try:
    while True:                                  # ← loop รอ client ใหม่ไปเรื่อยๆ
        conn, addr = server_socket.accept()
        client_count += 1
        print(f"[SERVER] [{client_count}] Connection from {addr}")

        data = conn.recv(BUFFER_SIZE)
        if data:
            message = data.decode()
            print(f"[SERVER] [{client_count}] Received : {message}")

            reply = f"ACK: {message}"
            conn.sendall(reply.encode())
            print(f"[SERVER] [{client_count}] Sent     : {reply}")
        else:
            print(f"[SERVER] [{client_count}] Empty data received")

        conn.close()
        print(f"[SERVER] [{client_count}] Connection closed\n")

except KeyboardInterrupt:
    print("\n[SERVER] Shutting down.")
finally:
    server_socket.close()