from datetime import datetime, timezone
import time


def utc_now() -> datetime:
    """Return current UTC datetime."""
    return datetime.now(timezone.utc)


def current_timestamp_ms() -> int:
    """Return current timestamp in milliseconds."""
    return int(time.time() * 1000)
