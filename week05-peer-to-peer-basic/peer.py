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

known_peers = set()
lock = threading.Lock()
running = True

def listen():
    """Listener thread: handles discovery, relay, and shutdown notices."""
    global running
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, PORT))
    sock.listen(5)
    sock.settimeout(1.0) # Allow checking 'running' flag
    print(f"[PEER {peer_id}] Listening on {HOST}:{PORT}")

    while running:
        try:
            conn, addr = sock.accept()
            raw_data = conn.recv(BUFFER_SIZE)
            if not raw_data:
                conn.close()
                continue
            
            data = raw_data.decode()
            
            # 1. Discovery
            if data.startswith("HELLO:"):
                try:
                    remote_id = int(data.split(":")[1])
                    if remote_id != peer_id:
                        with lock: known_peers.add(remote_id)
                        print(f"\n[SYSTEM] Discovered Peer {remote_id} at {addr[0]}")
                except ValueError: pass

            # 2. Relaying / Hop-based Routing
            elif data.startswith("RELAY|"):
                try:
                    _, target, origin, path, content = data.split("|", 4)
                    target, origin = int(target), int(origin)
                    path_list = [int(p) for p in path.split(",") if p]
                    
                    if target == peer_id:
                        print(f"\n[MSG] Final Destination! From {origin} (Path: {path_list} -> {peer_id}): {content}")
                    else:
                        print(f"\n[HOP] Relaying for {origin} -> {target}")
                        new_path = path + ("," if path else "") + str(peer_id)
                        relay_packet = f"RELAY|{target}|{origin}|{new_path}|{content}"
                        send_to_port(BASE_PORT + target, relay_packet)
                except ValueError: pass

            # 3. Graceful Shutdown (Extension 3)
            elif data.startswith("BYE:"):
                try:
                    remote_id = int(data.split(":")[1])
                    with lock:
                        if remote_id in known_peers:
                            known_peers.remove(remote_id)
                            print(f"\n[SYSTEM] Peer {remote_id} left the network.")
                except ValueError: pass

            else:
                print(f"\n[DATA] From {addr}: {data}")

            print("> ", end="", flush=True)
            conn.close()
        except socket.timeout:
            continue
        except Exception as e:
            if running: print(f"[ERROR] Listener: {e}")
            break
    sock.close()

def send_to_port(port, message):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.5)
        s.connect((HOST, port))
        s.sendall(message.encode())
        s.close()
        return True
    except:
        return False

def shutdown():
    global running
    print(f"\n[PEER {peer_id}] Shutting down gracefully...")
    running = False
    
    # Notify all known peers that we are leaving
    with lock:
        peers_to_notify = list(known_peers)
    
    if peers_to_notify:
        print(f"[SYSTEM] Notifying {len(peers_to_notify)} peers...")
        for pid in peers_to_notify:
            send_to_port(BASE_PORT + pid, f"BYE:{peer_id}")
    
    time.sleep(0.1) # Give listener a moment to exit loop
    print("Done.")

def main():
    threading.Thread(target=listen, daemon=True).start()
    time.sleep(0.5)

    print(f"--- Welcome Peer {peer_id} ---")
    print("Commands: /broadcast, /list, /exit, <id> <msg>, /relay <dst> <via> <msg>")
    
    try:
        while running:
            cmd = input("> ").strip()
            if not cmd: continue

            if cmd == "/exit":
                break
            elif cmd == "/list":
                with lock: print(f"Peers: {sorted(list(known_peers))}")
            elif cmd == "/broadcast":
                print("Broadcasting...")
                for i in range(1, MAX_PEERS + 1):
                    if i != peer_id and send_to_port(BASE_PORT + i, f"HELLO:{peer_id}"):
                        with lock: known_peers.add(i)
                print("Complete.")
            elif cmd.startswith("/relay"):
                parts = cmd.split(" ", 3)
                if len(parts) >= 4:
                    send_to_port(BASE_PORT + int(parts[2]), f"RELAY|{parts[1]}|{peer_id}||{parts[3]}")
            else:
                parts = cmd.split(" ", 1)
                if len(parts) >= 2:
                    send_to_port(BASE_PORT + int(parts[0]), f"RELAY|{parts[0]}|{peer_id}||{parts[1]}")
    except KeyboardInterrupt:
        pass
    
    shutdown()

if __name__ == "__main__":
    main()
