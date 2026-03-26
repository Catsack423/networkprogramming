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

def listen():
    """Listener thread: handles discovery (HELLO) and routing (RELAY)."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, PORT))
    sock.listen(5)
    print(f"[PEER {peer_id}] Listening on {HOST}:{PORT}")

    while True:
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
                        print(f"\n[SYSTEM] Discovered Peer {remote_id}")
                except ValueError: pass

            # 2. Relaying / Hop-based Routing
            elif data.startswith("RELAY|"):
                # Format: RELAY|target_id|origin_id|path|message
                try:
                    _, target, origin, path, content = data.split("|", 4)
                    target, origin = int(target), int(origin)
                    path_list = [int(p) for p in path.split(",") if p]
                    
                    if target == peer_id:
                        print(f"\n[MSG] Final destination! From Peer {origin}")
                        print(f"      Path: {path_list} -> {peer_id}")
                        print(f"      Content: '{content}'")
                    else:
                        print(f"\n[HOP] Relaying for Peer {origin} -> Peer {target}")
                        new_path = path + ("," if path else "") + str(peer_id)
                        relay_packet = f"RELAY|{target}|{origin}|{new_path}|{content}"
                        if not send_to_port(BASE_PORT + target, relay_packet):
                            print(f"      !! Link failed to Peer {target}")
                except ValueError: pass

            else:
                print(f"\n[PEER {peer_id}] Raw data: {data}")

            print("> ", end="", flush=True)
            conn.close()
        except Exception as e:
            print(f"[ERROR] Listener loop: {e}")
            break

def send_to_port(port, message):
    """Helper for low-level socket sending with timeout."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.5)
        s.connect((HOST, port))
        s.sendall(message.encode())
        s.close()
        return True
    except:
        return False

def main():
    threading.Thread(target=listen, daemon=True).start()
    time.sleep(0.5)

    print(f"--- Peer {peer_id} Online ---")
    print("Commands:")
    print("  /list             - Known peers")
    print("  /broadcast        - Find neighbors")
    print("  /relay <dst> <via> <msg> - Hop routing")
    print("  <id> <msg>        - Direct message")

    try:
        while True:
            cmd = input("> ").strip()
            if not cmd: continue

            if cmd == "/list":
                with lock: print(f"Known: {sorted(list(known_peers))}")
            
            elif cmd == "/broadcast":
                print("Broadcasting...")
                found = 0
                for i in range(1, MAX_PEERS + 1):
                    if i == peer_id: continue
                    if send_to_port(BASE_PORT + i, f"HELLO:{peer_id}"):
                        with lock: known_peers.add(i)
                        found += 1
                print(f"Found {found} peers.")

            elif cmd.startswith("/relay"):
                parts = cmd.split(" ", 3)
                if len(parts) < 4: continue
                try:
                    target, via, msg = int(parts[1]), int(parts[2]), parts[3]
                    packet = f"RELAY|{target}|{peer_id}||{msg}"
                    if not send_to_port(BASE_PORT + via, packet):
                        print(f"Failed to connect to relay node {via}")
                except ValueError: print("Invalid ID.")

            else:
                parts = cmd.split(" ", 1)
                if len(parts) < 2: continue
                try:
                    target, msg = int(parts[0]), parts[1]
                    packet = f"RELAY|{target}|{peer_id}||{msg}"
                    if not send_to_port(BASE_PORT + target, packet):
                        print(f"Peer {target} unreachable.")
                except ValueError: print("Invalid ID.")
    except KeyboardInterrupt:
        print("\nShutdown.")

if __name__ == "__main__":
    main()
