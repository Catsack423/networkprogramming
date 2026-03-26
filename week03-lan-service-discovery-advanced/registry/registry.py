"""
registry/registry.py
In-memory service registry with time-based expiration (soft state).

Each record looks like:
  {
      "service_name": str,
      "service_type": str,
      "host":         str,
      "ip":           str,
      "last_seen":    float,   # epoch seconds
      "metadata":     dict,
  }
"""

import time
import threading
from config import ENTRY_TTL


class ServiceRegistry:
    def __init__(self, ttl: float = ENTRY_TTL):
        self._records: dict[str, dict] = {}  # keyed by service_name
        self._lock = threading.Lock()
        self._ttl = ttl

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def register(self, msg: dict, src_ip: str) -> None:
        """Insert or refresh a service entry from a parsed ANNOUNCE message."""
        name = msg.get("service_name", "unknown")
        with self._lock:
            self._records[name] = {
                "service_name": name,
                "service_type": msg.get("service_type", ""),
                "host":         msg.get("host", ""),
                "ip":           src_ip,
                "last_seen":    time.time(),
                "metadata":     msg.get("metadata", {}),
            }

    def active_services(self) -> list[dict]:
        """Return services that have been seen within the TTL window."""
        now = time.time()
        with self._lock:
            return [
                r for r in self._records.values()
                if now - r["last_seen"] < self._ttl
            ]

    def expire(self) -> list[str]:
        """Remove stale entries. Returns list of expired service names."""
        now = time.time()
        expired = []
        with self._lock:
            stale = [n for n, r in self._records.items() if now - r["last_seen"] >= self._ttl]
            for name in stale:
                del self._records[name]
                expired.append(name)
        return expired

    def count(self) -> int:
        return len(self.active_services())

    def display(self) -> None:
        """Pretty-print the current active registry to stdout."""
        services = self.active_services()
        if not services:
            print("  [REGISTRY] No active services.")
            return
        print(f"  {'SERVICE NAME':<25} {'TYPE':<20} {'HOST':<20} {'IP':<16} {'AGE (s)'}")
        print("  " + "-" * 95)
        now = time.time()
        for r in services:
            age = int(now - r["last_seen"])
            print(f"  {r['service_name']:<25} {r['service_type']:<20} {r['host']:<20} {r['ip']:<16} {age}")
