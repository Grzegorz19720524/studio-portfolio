import time
import threading
import functools
from collections import deque
from typing import Any, Callable


class RateLimitExceeded(Exception):
    def __init__(self, retry_after: float = 0.0) -> None:
        self.retry_after = retry_after
        super().__init__(f"Rate limit exceeded. Retry after {retry_after:.3f}s")


class FixedWindow:
    """Allows at most `limit` calls per `window` seconds. Resets at window boundaries."""

    def __init__(self, limit: int, window: float) -> None:
        self.limit = limit
        self.window = window
        self._count = 0
        self._window_start = time.monotonic()
        self._lock = threading.Lock()

    def _reset_if_expired(self) -> None:
        now = time.monotonic()
        if now - self._window_start >= self.window:
            self._count = 0
            self._window_start = now

    def allow(self) -> bool:
        with self._lock:
            self._reset_if_expired()
            if self._count < self.limit:
                self._count += 1
                return True
            return False

    def acquire(self) -> None:
        with self._lock:
            self._reset_if_expired()
            if self._count < self.limit:
                self._count += 1
                return
            retry_after = self.window - (time.monotonic() - self._window_start)
        raise RateLimitExceeded(max(retry_after, 0.0))

    def remaining(self) -> int:
        with self._lock:
            self._reset_if_expired()
            return max(0, self.limit - self._count)

    def reset_after(self) -> float:
        with self._lock:
            return max(0.0, self.window - (time.monotonic() - self._window_start))

    def __repr__(self) -> str:
        return f"FixedWindow(limit={self.limit}, window={self.window}s, remaining={self.remaining()})"


class SlidingWindow:
    """Allows at most `limit` calls in any rolling `window`-second period."""

    def __init__(self, limit: int, window: float) -> None:
        self.limit = limit
        self.window = window
        self._timestamps: deque[float] = deque()
        self._lock = threading.Lock()

    def _evict(self, now: float) -> None:
        cutoff = now - self.window
        while self._timestamps and self._timestamps[0] <= cutoff:
            self._timestamps.popleft()

    def allow(self) -> bool:
        with self._lock:
            now = time.monotonic()
            self._evict(now)
            if len(self._timestamps) < self.limit:
                self._timestamps.append(now)
                return True
            return False

    def acquire(self) -> None:
        with self._lock:
            now = time.monotonic()
            self._evict(now)
            if len(self._timestamps) < self.limit:
                self._timestamps.append(now)
                return
            oldest = self._timestamps[0]
            retry_after = self.window - (now - oldest)
        raise RateLimitExceeded(max(retry_after, 0.0))

    def remaining(self) -> int:
        with self._lock:
            self._evict(time.monotonic())
            return max(0, self.limit - len(self._timestamps))

    def reset_after(self) -> float:
        with self._lock:
            now = time.monotonic()
            self._evict(now)
            if not self._timestamps or len(self._timestamps) < self.limit:
                return 0.0
            return max(0.0, self.window - (now - self._timestamps[0]))

    def __repr__(self) -> str:
        return f"SlidingWindow(limit={self.limit}, window={self.window}s, remaining={self.remaining()})"


class TokenBucket:
    """Tokens refill at `rate` per second up to `capacity`. Each call consumes `cost` tokens."""

    def __init__(self, capacity: float, rate: float) -> None:
        self.capacity = capacity
        self.rate = rate
        self._tokens = float(capacity)
        self._last_refill = time.monotonic()
        self._lock = threading.Lock()

    def _refill(self) -> None:
        now = time.monotonic()
        elapsed = now - self._last_refill
        self._tokens = min(self.capacity, self._tokens + elapsed * self.rate)
        self._last_refill = now

    def allow(self, cost: float = 1.0) -> bool:
        with self._lock:
            self._refill()
            if self._tokens >= cost:
                self._tokens -= cost
                return True
            return False

    def acquire(self, cost: float = 1.0) -> None:
        with self._lock:
            self._refill()
            if self._tokens >= cost:
                self._tokens -= cost
                return
            deficit = cost - self._tokens
            retry_after = deficit / self.rate
        raise RateLimitExceeded(retry_after)

    def wait(self, cost: float = 1.0) -> float:
        with self._lock:
            self._refill()
            if self._tokens >= cost:
                self._tokens -= cost
                return 0.0
            deficit = cost - self._tokens
            wait_time = deficit / self.rate
        time.sleep(wait_time)
        with self._lock:
            self._refill()
            self._tokens -= cost
        return wait_time

    @property
    def tokens(self) -> float:
        with self._lock:
            self._refill()
            return self._tokens

    def __repr__(self) -> str:
        return f"TokenBucket(capacity={self.capacity}, rate={self.rate}/s, tokens={self.tokens:.2f})"


class LeakyBucket:
    """Requests leak out at a fixed `rate` per second. Excess requests are rejected."""

    def __init__(self, capacity: int, rate: float) -> None:
        self.capacity = capacity
        self.rate = rate
        self._queue: deque[float] = deque()
        self._lock = threading.Lock()

    def _leak(self, now: float) -> None:
        while self._queue:
            age = now - self._queue[0]
            slots_leaked = int(age * self.rate)
            if slots_leaked > 0:
                for _ in range(min(slots_leaked, len(self._queue))):
                    self._queue.popleft()
                break
            break

    def allow(self) -> bool:
        with self._lock:
            now = time.monotonic()
            self._leak(now)
            if len(self._queue) < self.capacity:
                self._queue.append(now)
                return True
            return False

    def acquire(self) -> None:
        with self._lock:
            now = time.monotonic()
            self._leak(now)
            if len(self._queue) < self.capacity:
                self._queue.append(now)
                return
            retry_after = 1.0 / self.rate
        raise RateLimitExceeded(retry_after)

    def remaining(self) -> int:
        with self._lock:
            self._leak(time.monotonic())
            return max(0, self.capacity - len(self._queue))

    def __repr__(self) -> str:
        return f"LeakyBucket(capacity={self.capacity}, rate={self.rate}/s, remaining={self.remaining()})"


def rate_limit(
    limit: int,
    window: float,
    *,
    strategy: str = "sliding",
    block: bool = False,
) -> Callable:
    """Decorator that rate-limits a function. strategy: 'fixed', 'sliding', or 'token'."""
    if strategy == "fixed":
        limiter = FixedWindow(limit, window)
    elif strategy == "token":
        limiter = TokenBucket(limit, limit / window)
    else:
        limiter = SlidingWindow(limit, window)

    def decorator(fn: Callable) -> Callable:
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            if block and hasattr(limiter, "wait"):
                limiter.wait()
            else:
                limiter.acquire()
            return fn(*args, **kwargs)
        wrapper._limiter = limiter
        return wrapper
    return decorator


def throttle(min_interval: float) -> Callable:
    """Decorator that ensures at least `min_interval` seconds between calls."""
    def decorator(fn: Callable) -> Callable:
        last_called: list[float] = [0.0]
        lock = threading.Lock()

        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            with lock:
                now = time.monotonic()
                elapsed = now - last_called[0]
                if elapsed < min_interval:
                    time.sleep(min_interval - elapsed)
                last_called[0] = time.monotonic()
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def debounce(wait: float) -> Callable:
    """Decorator that delays execution until `wait` seconds after the last call."""
    def decorator(fn: Callable) -> Callable:
        timer_ref: list[Any] = [None]
        lock = threading.Lock()

        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            with lock:
                if timer_ref[0] is not None:
                    timer_ref[0].cancel()
                t = threading.Timer(wait, fn, args, kwargs)
                t.daemon = True
                t.start()
                timer_ref[0] = t
        return wrapper
    return decorator


def try_acquire(limiter, cost: float = 1.0) -> bool:
    """Returns True if the limiter allows the call, False otherwise (never raises)."""
    try:
        if isinstance(limiter, TokenBucket):
            return limiter.allow(cost)
        return limiter.allow()
    except Exception:
        return False


def wait_and_acquire(limiter, cost: float = 1.0, max_wait: float = 60.0) -> float:
    """Blocks until the limiter allows the call. Returns time waited in seconds."""
    start = time.monotonic()
    while True:
        try:
            if isinstance(limiter, TokenBucket):
                return limiter.wait(cost)
            limiter.acquire()
            return time.monotonic() - start
        except RateLimitExceeded as e:
            waited = time.monotonic() - start
            if waited + e.retry_after > max_wait:
                raise
            time.sleep(min(e.retry_after, max_wait - waited))


if __name__ == "__main__":
    print("--- FixedWindow ---")
    fw = FixedWindow(limit=3, window=1.0)
    results = [fw.allow() for _ in range(5)]
    print("allow x5:", results)
    print("remaining:", fw.remaining())
    print("reset_after:", round(fw.reset_after(), 2), "s")
    print(fw)

    print("\n--- SlidingWindow ---")
    sw = SlidingWindow(limit=3, window=1.0)
    results = [sw.allow() for _ in range(5)]
    print("allow x5:", results)
    print("remaining:", sw.remaining())
    print(sw)

    print("\n--- TokenBucket ---")
    tb = TokenBucket(capacity=5, rate=2.0)
    results = [tb.allow() for _ in range(7)]
    print("allow x7:", results)
    print("tokens left:", round(tb.tokens, 2))
    time.sleep(1.0)
    print("tokens after 1s:", round(tb.tokens, 2))
    print(tb)

    print("\n--- LeakyBucket ---")
    lb = LeakyBucket(capacity=3, rate=1.0)
    results = [lb.allow() for _ in range(5)]
    print("allow x5:", results)
    print("remaining:", lb.remaining())
    print(lb)

    print("\n--- RateLimitExceeded ---")
    fw2 = FixedWindow(limit=2, window=5.0)
    fw2.allow()
    fw2.allow()
    try:
        fw2.acquire()
    except RateLimitExceeded as e:
        print(f"Caught: {e}")

    print("\n--- rate_limit decorator (sliding) ---")
    @rate_limit(limit=3, window=1.0)
    def fetch(n):
        return f"result-{n}"

    ok, blocked = 0, 0
    for i in range(6):
        try:
            fetch(i)
            ok += 1
        except RateLimitExceeded:
            blocked += 1
    print(f"allowed={ok} blocked={blocked}")

    print("\n--- throttle decorator ---")
    calls = []
    @throttle(min_interval=0.05)
    def log_call():
        calls.append(time.monotonic())

    for _ in range(3):
        log_call()
    gaps = [round(calls[i+1] - calls[i], 3) for i in range(len(calls)-1)]
    print("gaps between calls (s):", gaps)
    print("all >= 0.05s:", all(g >= 0.05 for g in gaps))

    print("\n--- try_acquire ---")
    tb2 = TokenBucket(capacity=2, rate=1.0)
    print("try_acquire x4:", [try_acquire(tb2) for _ in range(4)])

    print("\n--- wait_and_acquire (token bucket) ---")
    tb3 = TokenBucket(capacity=1, rate=5.0)
    tb3.allow()
    waited = wait_and_acquire(tb3, max_wait=5.0)
    print(f"waited: {waited:.3f}s")
