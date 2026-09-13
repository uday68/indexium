import time
import heapq
from urllib.parse import urlparse
from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple


@dataclass(order=True)
class CrawlItem:
    priority: int
    depth: int = field(compare=False)
    url: str = field(compare=False)


class CrawlScheduler:
    """Manages the URL frontier with priority queuing and domain-level politeness delays."""

    def __init__(self, politeness_delay_sec: float = 0.5):
        self.politeness_delay = politeness_delay_sec
        # Priority queue: min-heap of CrawlItem
        self._queue: list = []
        # domain -> last fetch timestamp
        self._last_domain_fetch: Dict[str, float] = {}

    def push(self, url: str, priority: int = 10, depth: int = 0):
        """Enqueue a URL to crawl."""
        item = CrawlItem(priority=priority, depth=depth, url=url)
        heapq.heappush(self._queue, item)

    def pop(self) -> Optional[Tuple[str, int]]:
        """Pop the highest priority URL from the queue."""
        if not self._queue:
            return None
        item = heapq.heappop(self._queue)
        return item.url, item.depth

    def wait_if_needed(self, url: str):
        """Enforce domain politeness rate limits before initiating an HTTP request."""
        domain = urlparse(url).netloc
        now = time.time()
        last_fetch = self._last_domain_fetch.get(domain, 0.0)
        elapsed = now - last_fetch
        if elapsed < self.politeness_delay:
            time.sleep(self.politeness_delay - elapsed)
        self._last_domain_fetch[domain] = time.time()

    @property
    def queue_size(self) -> int:
        return len(self._queue)

    def is_empty(self) -> bool:
        return len(self._queue) == 0
