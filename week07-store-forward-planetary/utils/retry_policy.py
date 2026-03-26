# week07-store-forward-planetary/utils/retry_policy.py
import math

class RetryPolicy:
    def __init__(self, base_interval, factor, max_interval):
        self.base_interval = base_interval
        self.factor = factor
        self.max_interval = max_interval

    def get_next_delay(self, current_retries):
        """Calculates exponential backoff delay."""
        # delay = base * (factor ^ retries)
        delay = self.base_interval * (self.factor ** current_retries)
        return min(delay, self.max_interval)
