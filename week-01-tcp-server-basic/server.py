import socket
from config import HOST,PORT,BUFFER_SIZE

server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server_socket.bind((HOST,PORT))
server_socket.listen(1)

print(f"[SERVER] Listening on {HOST}:{PORT}")


conn,addr = server_socket.accept()

print(f"[SERVER] COnnectioin form {addr}")

data = conn.recv(BUFFER_SIZE)
message = data.decode()
print(f"[SERVER] Received: {message}")

reply = f"ACK: {message}"
conn.sendall(reply.encode())


conn.close()
server_socket.close()
print("[SERVER] Closed connection")