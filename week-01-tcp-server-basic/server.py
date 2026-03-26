import socket
from config import HOST, PORT, BUFFER_SIZE, ENCODING, RECV_TIMEOUT

# ── server setup ─────────────────────────────────────────────────────────────────
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen(5)

print(f"[SERVER] Listening on {HOST}:{PORT}")
print(f"[SERVER] Extension C — Timeout ON  (recv timeout = {RECV_TIMEOUT}s)\n")

client_count = 0

try:
    while True:
        conn, addr = server_socket.accept()
        client_count += 1
        print(f"[SERVER] [{client_count}] Connection from {addr}")

        # Set timeout on the accepted connection socket only.
        # If no data arrives within RECV_TIMEOUT seconds → socket.timeout is raised.
        conn.settimeout(RECV_TIMEOUT)

        try:
            data = conn.recv(BUFFER_SIZE)

            if data:
                message = data.decode(ENCODING)
                print(f"[SERVER] [{client_count}] Received : '{message}'")
                reply = f"ACK: {message}"
            else:
                print(f"[SERVER] [{client_count}] Client disconnected before sending data")
                reply = "ERROR: No data received"

            conn.sendall(reply.encode(ENCODING))

        except socket.timeout:
            # Peer connected but never sent data within RECV_TIMEOUT seconds
            print(f"[SERVER] [{client_count}] ⏱  Timeout — {addr} was unresponsive ({RECV_TIMEOUT}s)")
            try:
                conn.sendall("ERROR: Connection timed out".encode(ENCODING))
            except Exception:
                pass   # peer may have already closed

        except ConnectionResetError:
            print(f"[SERVER] [{client_count}] ⚠  Connection reset by {addr}")

        finally:
            conn.close()
            print(f"[SERVER] [{client_count}] Connection closed\n")

except KeyboardInterrupt:
    print("\n[SERVER] Shutting down.")
finally:
    server_socket.close()