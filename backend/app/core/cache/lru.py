import time
import threading
from collections import OrderedDict
from typing import Any, Optional, Tuple


class LRUCache:
    """Thread-safe in-memory Least Recently Used (LRU) cache with optional TTL."""

    def __init__(self, capacity: int = 1000, default_ttl_sec: Optional[float] = 300.0):
        self.capacity = max(1, capacity)
        self.default_ttl = default_ttl_sec
        # key -> (value, expire_at)
        self._cache: OrderedDict[str, Tuple[Any, Optional[float]]] = OrderedDict()
        self._lock = threading.RLock()
        self.hits = 0
        self.misses = 0

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            if key not in self._cache:
                self.misses += 1
                return None

            val, expire_at = self._cache[key]
            if expire_at is not None and time.time() > expire_at:
                del self._cache[key]
                self.misses += 1
                return None

            # Move to MRU position (end)
            self._cache.move_to_end(key)
            self.hits += 1
            return val

    def set(self, key: str, value: Any, ttl_sec: Optional[float] = None):
        with self._lock:
            expire_at = None
            ttl = ttl_sec if ttl_sec is not None else self.default_ttl
            if ttl is not None:
                expire_at = time.time() + ttl

            if key in self._cache:
                self._cache.move_to_end(key)
            elif len(self._cache) >= self.capacity:
                # Evict LRU (first item)
                self._cache.popitem(last=False)

            self._cache[key] = (value, expire_at)

    def delete(self, key: str):
        with self._lock:
            self._cache.pop(key, None)

    def clear(self):
        with self._lock:
            self._cache.clear()

    @property
    def size(self) -> int:
        with self._lock:
            return len(self._cache)

    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return (self.hits / total) if total > 0 else 0.0
