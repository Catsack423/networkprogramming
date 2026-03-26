# week04-multicast-pubsub-advanced/topics.py
# Mapping of human-readable topics to multicast groups.

TOPIC_MAP = {
    "news":    "224.5.5.1",
    "sports":  "224.5.5.2",
    "weather": "224.5.5.3",
    "alerts":  "224.5.5.4"
}

def get_group_for_topic(topic: str) -> str:
    """Returns the multicast group address for a given topic."""
    return TOPIC_MAP.get(topic.lower())

def list_topics() -> list:
    """Returns a list of available topics."""
    return list(TOPIC_MAP.keys())
