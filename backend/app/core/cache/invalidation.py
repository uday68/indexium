from typing import List, Optional
from app.core.cache.redis_client import CacheClient


class CacheInvalidator:
    """Manages cache invalidation when the underlying search index changes."""

    def __init__(self, cache_client: CacheClient):
        self.cache = cache_client

    def invalidate_query(self, query: str):
        key = f"query:{query.lower().strip()}"
        self.cache.delete(key)

    def invalidate_terms(self, terms: List[str]):
        """Invalidate all cached queries related to updated terms."""
        for term in terms:
            self.cache.delete(f"query:{term.lower()}")

    def invalidate_all(self):
        """Clear all cached query results."""
        self.cache.clear()
