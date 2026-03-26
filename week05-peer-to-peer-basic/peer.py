# week05-peer-to-peer-basic/peer.py
import socket
import threading
import sys
import time
from config import HOST, BASE_PORT, BUFFER_SIZE, MAX_PEERS

if len(sys.argv) < 2:
    print("Usage: python peer.py <peer_id>")
    sys.exit(1)

peer_id = int(sys.argv[1])
PORT = BASE_PORT + peer_id

known_peers = set() # Set of peer IDs discovered
lock = threading.Lock()

def listen():
    """Listener thread: accepts incoming TCP connections and handles discovery."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, PORT))
    sock.listen(5)
    print(f"[PEER {peer_id}] Listening on {HOST}:{PORT}")

    while True:
        try:
            conn, addr = sock.accept()
            raw_data = conn.recv(BUFFER_SIZE)
            if raw_data:
                data = raw_data.decode()
                if data.startswith("HELLO:"):
                    try:
                        remote_id = int(data.split(":")[1])
                        if remote_id != peer_id:
                            with lock:
                                known_peers.add(remote_id)
                            print(f"\n[SYSTEM] Discovered Peer {remote_id} at {addr[0]}:{BASE_PORT + remote_id}")
                    except ValueError: pass
                else:
                    print(f"\n[PEER {peer_id}] Message from {addr}: {data}")
                
                print("> ", end="", flush=True)
            conn.close()
        except Exception as e:
            print(f"[PEER {peer_id}] Listener error: {e}")
            break

def send_message(target_peer_id, message, silent=False):
    """Sends a message to a target peer."""
    target_port = BASE_PORT + target_peer_id
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)
        sock.connect((HOST, target_port))
        sock.sendall(message.encode())
        sock.close()
        if not silent:
            print(f"[PEER {peer_id}] Sent to Peer {target_peer_id}: {message}")
        return True
    except (ConnectionRefusedError, socket.timeout):
        if not silent:
            print(f"[PEER {peer_id}] Error: Peer {target_peer_id} is unreachable.")
        return False
    except Exception as e:
        if not silent:
            print(f"[PEER {peer_id}] Send error: {e}")
        return False

def main():
    threading.Thread(target=listen, daemon=True).start()
    time.sleep(0.5)

    print(f"--- Welcome Peer {peer_id} ---")
    print("Commands:")
    print("  /list      - Show known peers")
    print("  /broadcast - Discover active peers")
    print("  <id> <msg> - Send private message")
    
    try:
        while True:
            cmd = input("> ").strip()
            if not cmd: continue

            if cmd == "/list":
                with lock:
                    if not known_peers:
                        print("[SYSTEM] No peers known yet. Try /broadcast")
                    else:
                        print(f"[SYSTEM] Known peers: {sorted(list(known_peers))}")
            
            elif cmd == "/broadcast":
                print(f"[SYSTEM] Broadcasting presence to peers 1-{MAX_PEERS}...")
                found = 0
                for i in range(1, MAX_PEERS + 1):
                    if i == peer_id: continue
                    if send_message(i, f"HELLO:{peer_id}", silent=True):
                        with lock:
                            known_peers.add(i)
                        found += 1
                print(f"[SYSTEM] Broadcast complete. Found {found} active peer(s).")
            
            else:
                # Private message: <id> <msg>
                parts = cmd.split(" ", 1)
                if len(parts) < 2:
                    print("Usage: <peer_id> <message>")
                    continue
                try:
                    target = int(parts[0])
                    send_message(target, parts[1])
                except ValueError:
                    print("Invalid Peer ID.")
    except KeyboardInterrupt:
        print(f"\n[PEER {peer_id}] Shutting down.")

if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()
