# week05-peer-to-peer-basic/peer.py
import socket
import threading
import sys
import time
from config import HOST, BASE_PORT, BUFFER_SIZE

if len(sys.argv) < 2:
    print("Usage: python peer.py <peer_id>")
    sys.exit(1)

peer_id = int(sys.argv[1])
PORT = BASE_PORT + peer_id

def listen():
    """Listener thread: accepts incoming TCP connections from other peers."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, PORT))
    sock.listen(5)
    print(f"[PEER {peer_id}] Listening on {HOST}:{PORT}")

    while True:
        try:
            conn, addr = sock.accept()
            data = conn.recv(BUFFER_SIZE)
            if data:
                print(f"\n[PEER {peer_id}] Received from {addr}: {data.decode()}")
                print("Send to peer ID: ", end="", flush=True)
            conn.close()
        except Exception as e:
            print(f"[PEER {peer_id}] Listener error: {e}")
            break

def send_message(target_peer_id, message):
    """Sender function: initiates an outbound TCP connection to a target peer."""
    target_port = BASE_PORT + target_peer_id
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((HOST, target_port))
        sock.sendall(message.encode())
        sock.close()
        print(f"[PEER {peer_id}] Message sent to Peer {target_peer_id}")
    except ConnectionRefusedError:
        print(f"[PEER {peer_id}] Error: Peer {target_peer_id} (port {target_port}) is not active.")
    except Exception as e:
        print(f"[PEER {peer_id}] Send error: {e}")

def main():
    # Start the listener thread
    threading.Thread(target=listen, daemon=True).start()

    # Small delay to let the listener start
    time.sleep(0.5)

    print(f"--- Welcome Peer {peer_id} ---")
    print("Commands: Enter peer ID, then the message.")
    
    try:
        while True:
            try:
                target_input = input("Send to peer ID: ")
                if not target_input.strip(): continue
                target = int(target_input)
                
                msg = input("Message: ")
                if not msg.strip(): continue
                
                send_message(target, msg)
            except ValueError:
                print("Invalid input. Please enter a numeric Peer ID.")
    except KeyboardInterrupt:
        print(f"\n[PEER {peer_id}] Shutting down.")

if __name__ == "__main__":
    main()
