# week04-multicast-pubsub-advanced

## Overview
This lab implements a **Publish/Subscribe** system on top of IP Multicast. Topics are mapped to individual multicast groups, allowing subscribers only to receive messages for the "channels" they are interested in.

### Advanced Concepts
- **Topic-based Routing**: Instead of joining a single group, subscribers select topics.
- **Dynamic Membership**: A single subscriber can join and leave multiple multicast groups at runtime.
- **Structured Messages**: All messages are JSON-encoded to include sender metadata and timestamps.

---

## Directory Structure
- `config.py`: Global defaults for Port and TTL.
- `topics.py`: The mapping of strings (e.g., "news") to multicast IPs.
- `utils/protocol.py`: Message serialization and deserialization.
- `publisher.py`: CLI tool for publishing content to a topic.
- `subscriber.py`: CLI tool for subscribing to one or more topics.

---

## How to Run

### 1. Start a Subscriber
Run the subscriber and specify the topics you want to follow:
```bash
python subscriber.py news sports
```

### 2. Publish a Message
In another terminal, use the publisher to send a message to a topic:
```bash
python publisher.py news "Breaking News: Multicast is efficient!"
```

### 3. Verify
The subscriber should display the message correctly, while other subscribers (following different topics like "weather") will see nothing.
