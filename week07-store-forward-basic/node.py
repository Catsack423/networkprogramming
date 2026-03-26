# week07-store-forward-basic/node.py
import socket
import threading
import time
import sys
from config import HOST, BUFFER_SIZE, RETRY_INTERVAL, MAX_RETRY_BACKOFF, PERSISTENCE_FILE
from message_queue import MessageQueue

class StoreForwardNode:
    def __init__(self, port):
        self.port = port
        # Use a unique persistence file per node
        self.queue = MessageQueue(f"queue_{port}.json")
        self.running = True

    def log(self, msg):
        print(f"[NODE {self.port}] {msg}")

    def send_attempt(self, peer_port, message):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1.0)
            sock.connect((HOST, peer_port))
            sock.sendall(message.encode())
            sock.close()
            return True
        except:
            return False

    def forward_loop(self):
        """Background thread to retry sending queued messages with exponential backoff."""
        while self.running:
            pending = self.queue.get_pending_messages()
            now = time.time()
            
            for msg in pending:
                if now >= msg['next_retry']:
                    self.log(f"Retrying message to {msg['peer']} (Attempt {msg['retries'] + 1})")
                    if self.send_attempt(msg['peer'], msg['message']):
                        self.log(f"Success! Message delivered to {msg['peer']}")
                        self.queue.remove_message((msg['peer'], msg['timestamp']))
                    else:
                        # Exponential backoff: retry_interval * (2 ^ retries)
                        new_retries = msg['retries'] + 1
                        backoff = min(RETRY_INTERVAL * (2 ** new_retries), MAX_RETRY_BACKOFF)
                        self.queue.update_retry(
                            (msg['peer'], msg['timestamp']), 
                            now + backoff, 
                            new_retries
                        )
                        self.log(f"Failed. Backing off for {backoff}s")
            
            time.sleep(1)

    def start_server(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((HOST, self.port))
        sock.listen(5)
        self.log(f"Listening on port {self.port}")
        
        while self.running:
            try:
                conn, addr = sock.accept()
                data = conn.recv(BUFFER_SIZE)
                if data:
                    self.log(f"Received from {addr}: {data.decode()}")
                conn.close()
            except: continue

def main():
    if len(sys.argv) < 2:
        print("Usage: python node.py <port>")
        return

    port = int(sys.argv[1])
    node = StoreForwardNode(port)
    
    threading.Thread(target=node.start_server, daemon=True).start()
    threading.Thread(target=node.forward_loop, daemon=True).start()

    print(f"--- Store-and-Forward Node {port} Ready ---")
    print("Commands: /send <port> <msg> [priority], /list, /exit")

    try:
        while True:
            cmd = input("> ").strip().split()
            if not cmd: continue
            
            if cmd[0] == "/exit":
                node.running = False
                break
            elif cmd[0] == "/list":
                pending = node.queue.get_pending_messages()
                print(f"Pending Messages: {len(pending)}")
                for m in pending:
                    print(f" - To {m['peer']}: '{m['message']}' (Priority: {m['priority']}, Next Retry in: {int(m['next_retry'] - time.time())}s)")
            elif cmd[0] == "/send" and len(cmd) >= 3:
                target_port = int(cmd[1])
                msg_text = " ".join(cmd[2:-1]) if cmd[-1].isdigit() else " ".join(cmd[2:])
                priority = int(cmd[-1]) if cmd[-1].isdigit() else 1
                
                print(f"Attempting to send to {target_port}...")
                if node.send_attempt(target_port, msg_text):
                    print("Sent immediately.")
                else:
                    print(f"Peer {target_port} unavailable. Queuing message with priority {priority}.")
                    node.queue.add_message(msg_text, target_port, priority)
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
