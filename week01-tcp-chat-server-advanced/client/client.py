import socket
import threading
import sys
from config import HOST, PORT, BUFFER_SIZE, ENCODING

def receive_messages(sock):
    while True:
        try:
            message = sock.recv(BUFFER_SIZE).decode(ENCODING)
            if message:
                print(f"\n{message}\n> ", end="")
            else:
                break
        except:
            print("[ERROR] Connection lost.")
            break

def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((HOST, PORT))
        print(f"Connected to server at {HOST}:{PORT}")

        # Thread สำหรับรอรับข้อความจาก Server
        threading.Thread(target=receive_messages, args=(client_socket,), daemon=True).start()

        while True:
            msg = input("> ")
            if msg.lower() == 'exit':
                break
            client_socket.sendall(msg.encode(ENCODING))

    except Exception as e:
        print(f"Connection error: {e}")
    finally:
        client_socket.close()
        print("Disconnected.")

if __name__ == "__main__":
    start_client()