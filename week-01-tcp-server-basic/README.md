# week-01-tcp-server-basic ✅

**Simple TCP client/server example (Python)**

A minimal TCP server and client that demonstrate basic socket communication using Python's builtin `socket` module.

---

## Files 🔧

- `server.py` — Simple TCP server that listens for a single connection, receives a message, and replies with an `ACK:` prefix.
- `client.py` — Connects to the server, sends a message (`"Hello Server"`) and prints the response.
- `config.py` — Central settings for `HOST`, `PORT`, `BUFFER_SIZE`, and `ENCODING`.

---

## Requirements 🧩

- Python 3.x
- No external dependencies

---

## Configuration ⚙️

Edit `config.py` to change network settings:

```python
HOST = "127.0.0.1"  # loopback
PORT = 5000
BUFFER_SIZE = 1024
ENCODING = "utf-8"
```

Keep `HOST` as `127.0.0.1` for local testing or change to a reachable address for networked runs.

---

## Usage 🚀

1. Run the server (in one terminal):

```bash
python server.py
```

You should see:

```
[SERVER] Listening on 127.0.0.1:5000
```

2. Run the client (in another terminal):

```bash
python client.py
```

Client output example:

```
[CLIENT] Received: ACK: Hello Server
```

Server output example:

```
[SERVER] COnnectioin form ('127.0.0.1', 54712)
[SERVER] Received: Hello Server
[SERVER] Closed connection
```

---

## Notes 💡

- This example expects a single client connection and closes after handling that one message. It's intentionally minimal for learning purposes.
- For multiple clients or production use, consider using threading/asyncio and proper error handling.

---

## License

MIT — feel free to reuse and modify for learning.
