import socket
from config import HOST,PORT,BUFFER_SIZE

client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
client_socket.connect((HOST,PORT))
message = 'Hello Server'


client_socket.sendall(message.encode())

response = client_socket.recv(BUFFER_SIZE)
print(f"[CLIENT] Received: {response.decode()}")
client_socket.close()