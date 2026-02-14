import time
import threading


class TokenBucket:
    """Thread-safe token bucket for rate limiting."""

    def __init__(self, capacity, refill_rate):
        """
        Args:
            capacity: Maximum number of tokens.
            refill_rate: Tokens added per second.
        """
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate
        self.last_refill = time.monotonic()
        self.lock = threading.Lock()

    def _refill(self):
        """Refill tokens based on elapsed time. Must be called within lock."""
        now = time.monotonic()
        delta = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + delta * self.refill_rate)
        self.last_refill = now

    def acquire(self, timeout=10):
        """
        Block until a token is available or timeout.

        Returns:
            True if token acquired, False if timed out.
        """
        start = time.monotonic()
        while time.monotonic() - start < timeout:
            with self.lock:
                self._refill()
                if self.tokens >= 1:
                    self.tokens -= 1
                    return True
            time.sleep(0.1)
        return False


class RateLimiter:
    """Manages multiple token buckets for different sources."""

    DEFAULT_LIMITS = {
        "arxiv": {"capacity": 5, "refill_rate": 0.33},
        "zhihu": {"capacity": 3, "refill_rate": 0.2},
        "scholar": {"capacity": 10, "refill_rate": 1.0},
        "duckduckgo": {"capacity": 20, "refill_rate": 2.0},
    }

    def __init__(self, config=None):
        limits = config or self.DEFAULT_LIMITS
        self.buckets = {}
        for source, params in limits.items():
            self.buckets[source] = TokenBucket(
                capacity=params["capacity"],
                refill_rate=params["refill_rate"],
            )

    def acquire(self, source, timeout=10):
        """
        Acquire a token for the given source.

        Returns:
            True if acquired, False if timed out.
        """
        bucket = self.buckets.get(source)
        if bucket is None:
            return True  # No limit configured for this source
        return bucket.acquire(timeout=timeout)
