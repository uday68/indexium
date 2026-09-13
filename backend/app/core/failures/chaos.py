import time
import random
from typing import Optional


class ChaosMonkey:
    """Injects artificial latency and intermittent failures for chaos testing."""

    def __init__(self, latency_rate: float = 0.0, max_latency_sec: float = 0.5, error_rate: float = 0.0):
        self.latency_rate = latency_rate
        self.max_latency_sec = max_latency_sec
        self.error_rate = error_rate
        self.enabled = False

    def enable(self, latency_rate: float = 0.1, error_rate: float = 0.05):
        self.enabled = True
        self.latency_rate = latency_rate
        self.error_rate = error_rate

    def disable(self):
        self.enabled = False

    def maybe_inject(self):
        """Conditionally sleep or raise an exception if chaos is active."""
        if not self.enabled:
            return

        if self.error_rate > 0 and random.random() < self.error_rate:
            raise RuntimeError("ChaosMonkey injected failure: Simulated network / subsystem outage!")

        if self.latency_rate > 0 and random.random() < self.latency_rate:
            delay = random.uniform(0.05, self.max_latency_sec)
            time.sleep(delay)
