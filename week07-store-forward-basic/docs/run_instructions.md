# week07-store-forward-basic: Run Instructions

## Persistence (Extension A) Test

1. **Start Node 8000**:
   ```bash
   python node.py 8000
   ```

2. **Add a message for an offline peer (8001)**:
   ```bash
   > /send 8001 Persistence_Test
   ```
   *Output*: "Peer 8001 unavailable. Queuing message..."

3. **Check the local file**:
   - Open `queue_8000.json` in your editor.
   - You should see the message stored with its timestamp and priority.

4. **Simulate a Crash**:
   - Close the Node 8000 terminal (`Ctrl+C`).
   - Re-run Node 8000: `python node.py 8000`.
   - Type `/list`. The message "Persistence_Test" should still be in the queue!

5. **Deliver to Restore**:
   - Open a 2nd terminal: `python node.py 8001`.
   - Node 8000 will automatically detect Node 8001 and deliver the stored message.
   - Check `queue_8000.json`; it will now be empty.
