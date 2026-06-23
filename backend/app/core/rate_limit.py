import time
from collections import defaultdict


class RateLimitExceeded(Exception):
    """Raised when a caller exceeds a configured request budget."""


_buckets: dict[str, list[float]] = defaultdict(list)


def check_rate_limit(*, key: str, max_requests: int, window_seconds: int) -> None:
    """Simple in-process sliding-window limiter.

    Suitable for single-worker deployments. For multi-replica production,
    replace with a shared store such as Redis.
    """
    now = time.monotonic()
    window_start = now - window_seconds
    recent_requests = [timestamp for timestamp in _buckets[key] if timestamp > window_start]

    if len(recent_requests) >= max_requests:
        raise RateLimitExceeded(key)

    recent_requests.append(now)
    _buckets[key] = recent_requests
