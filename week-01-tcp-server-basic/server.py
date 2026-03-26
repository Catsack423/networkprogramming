import socket
from config import HOST, PORT, BUFFER_SIZE, ENCODING, MAX_MESSAGE_LENGTH

# ── validation helper ────────────────────────────────────────────────────────────
def validate_message(message: str) -> tuple[bool, str]:
    """
    Check if a message is acceptable.
    Returns (is_valid, error_reason).
    """
    if not message or message.strip() == "":
        return False, "ERROR: Empty message rejected"
    if len(message) > MAX_MESSAGE_LENGTH:
        return False, f"ERROR: Message too long ({len(message)}/{MAX_MESSAGE_LENGTH} chars)"
    return True, ""

# ── server setup ─────────────────────────────────────────────────────────────────
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen(5)

print(f"[SERVER] Listening on {HOST}:{PORT}")
print(f"[SERVER] Extension B — Validation ON  (max {MAX_MESSAGE_LENGTH} chars, no empty)\n")

client_count = 0

try:
    while True:
        conn, addr = server_socket.accept()
        client_count += 1
        print(f"[SERVER] [{client_count}] Connection from {addr}")

        data = conn.recv(BUFFER_SIZE)
        message = data.decode(ENCODING)

        is_valid, error_reason = validate_message(message)

        if is_valid:
            print(f"[SERVER] [{client_count}] ✓ Valid   : '{message}'")
            reply = f"ACK: {message}"
        else:
            print(f"[SERVER] [{client_count}] ✗ Invalid : {error_reason}")
            reply = error_reason          # ส่ง error กลับ client

        conn.sendall(reply.encode(ENCODING))
        conn.close()
        print(f"[SERVER] [{client_count}] Connection closed\n")

except KeyboardInterrupt:
    print("\n[SERVER] Shutting down.")
finally:
    server_socket.close()