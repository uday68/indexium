import time
from typing import Dict, List
from fastapi import HTTPException, Request, status
from app.config.feature_flags import feature_flags


class RateLimiter:
    """Sliding window rate limiter keyed by client IP."""

    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.client_requests: Dict[str, List[float]] = {}

    def is_allowed(self, client_id: str) -> bool:
        if not feature_flags.is_enabled("enable_rate_limiting"):
            return True

        now = time.time()
        window_start = now - self.window_seconds

        timestamps = self.client_requests.get(client_id, [])
        # Filter timestamps within window
        valid_timestamps = [t for t in timestamps if t > window_start]
        
        if len(valid_timestamps) >= self.max_requests:
            self.client_requests[client_id] = valid_timestamps
            return False

        valid_timestamps.append(now)
        self.client_requests[client_id] = valid_timestamps
        return True


rate_limiter = RateLimiter()


def rate_limit_dependency(request: Request):
    client_ip = request.client.host if request.client else "unknown"
    if not rate_limiter.is_allowed(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later."
        )
