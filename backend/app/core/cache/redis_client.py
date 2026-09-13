import json
import logging
from typing import Any, Optional
from app.core.cache.lru import LRUCache

logger = logging.getLogger(__name__)


class CacheClient:
    """
    Unified Cache Client supporting Redis with automatic fallback to in-memory LRU.
    Ensures zero runtime failure if Redis is unavailable.
    """

    def __init__(self, redis_url: Optional[str] = None, fallback_capacity: int = 1000):
        self.fallback_cache = LRUCache(capacity=fallback_capacity)
        self.redis = None

        if redis_url:
            try:
                import redis
                self.redis = redis.from_url(redis_url, decode_responses=True)
                self.redis.ping()
                logger.info(f"Connected to Redis cache at {redis_url}")
            except Exception as e:
                logger.warning(f"Could not connect to Redis ({e}), falling back to in-memory LRU cache.")
                self.redis = None

    def get(self, key: str) -> Optional[Any]:
        if self.redis:
            try:
                data = self.redis.get(key)
                if data:
                    return json.loads(data)
                return None
            except Exception as e:
                logger.warning(f"Redis get error ({e}), falling back to LRU")
        return self.fallback_cache.get(key)

    def set(self, key: str, value: Any, ttl_sec: Optional[int] = 300):
        if self.redis:
            try:
                data = json.dumps(value)
                self.redis.set(key, data, ex=ttl_sec)
                return
            except Exception as e:
                logger.warning(f"Redis set error ({e}), falling back to LRU")
        self.fallback_cache.set(key, value, ttl_sec=float(ttl_sec) if ttl_sec else None)

    def delete(self, key: str):
        if self.redis:
            try:
                self.redis.delete(key)
            except Exception:
                pass
        self.fallback_cache.delete(key)

    def clear(self):
        if self.redis:
            try:
                self.redis.flushdb()
            except Exception:
                pass
        self.fallback_cache.clear()

    @property
    def hit_rate(self) -> float:
        return self.fallback_cache.hit_rate
