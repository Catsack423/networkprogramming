# week06-manet-disaster-advanced/utils/routing_metrics.py
import time

class MetricsTable:
    def __init__(self):
        self.received = 0
        self.relayed = 0
        self.duplicates = 0
        self.start_time = time.time()

    def add_received(self): self.received += 1
    def add_relayed(self): self.relayed += 1
    def add_duplicate(self): self.duplicates += 1

    def get_summary(self):
        uptime = int(time.time() - self.start_time)
        return {
            "uptime": uptime,
            "received": self.received,
            "relayed": self.relayed,
            "duplicates": self.duplicates,
            "success_rate": f"{(self.relayed/self.received*100):.1f}%" if self.received > 0 else "0%"
        }
