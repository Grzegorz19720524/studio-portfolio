import time
import threading
import functools
from enum import Enum
from typing import Any, Callable, Type


class State(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreakerOpen(Exception):
    def __init__(self, name: str, retry_after: float = 0.0) -> None:
        self.name = name
        self.retry_after = retry_after
        super().__init__(f"Circuit '{name}' is OPEN. Retry after {retry_after:.2f}s")


class CircuitBreaker:
    def __init__(
        self,
        name: str = "default",
        failure_threshold: int = 5,
        recovery_timeout: float = 30.0,
        success_threshold: int = 2,
        expected_exceptions: tuple[Type[Exception], ...] = (Exception,),
        on_open: Callable | None = None,
        on_close: Callable | None = None,
        on_half_open: Callable | None = None,
    ) -> None:
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.success_threshold = success_threshold
        self.expected_exceptions = expected_exceptions
        self._on_open = on_open
        self._on_close = on_close
        self._on_half_open = on_half_open

        self._state = State.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time: float | None = None
        self._total_calls = 0
        self._total_failures = 0
        self._total_successes = 0
        self._lock = threading.Lock()

    @property
    def state(self) -> State:
        with self._lock:
            return self._eval_state()

    def _eval_state(self) -> State:
        if self._state == State.OPEN:
            if self._last_failure_time is not None:
                elapsed = time.monotonic() - self._last_failure_time
                if elapsed >= self.recovery_timeout:
                    self._transition(State.HALF_OPEN)
        return self._state

    def _transition(self, new_state: State) -> None:
        if self._state == new_state:
            return
        self._state = new_state
        if new_state == State.OPEN and self._on_open:
            self._on_open(self)
        elif new_state == State.CLOSED and self._on_close:
            self._on_close(self)
        elif new_state == State.HALF_OPEN and self._on_half_open:
            self._on_half_open(self)

    def call(self, fn: Callable, *args, **kwargs) -> Any:
        with self._lock:
            state = self._eval_state()
            if state == State.OPEN:
                retry_after = 0.0
                if self._last_failure_time is not None:
                    retry_after = max(
                        0.0,
                        self.recovery_timeout - (time.monotonic() - self._last_failure_time),
                    )
                raise CircuitBreakerOpen(self.name, retry_after)
            self._total_calls += 1

        try:
            result = fn(*args, **kwargs)
        except self.expected_exceptions as exc:
            with self._lock:
                self._total_failures += 1
                self._failure_count += 1
                self._success_count = 0
                self._last_failure_time = time.monotonic()
                if self._state == State.HALF_OPEN or self._failure_count >= self.failure_threshold:
                    self._transition(State.OPEN)
            raise

        with self._lock:
            self._total_successes += 1
            self._success_count += 1
            self._failure_count = 0
            if self._state == State.HALF_OPEN and self._success_count >= self.success_threshold:
                self._transition(State.CLOSED)
        return result

    def __call__(self, fn: Callable) -> Callable:
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            return self.call(fn, *args, **kwargs)
        wrapper._circuit_breaker = self
        return wrapper

    def reset(self) -> None:
        with self._lock:
            self._state = State.CLOSED
            self._failure_count = 0
            self._success_count = 0
            self._last_failure_time = None

    def trip(self) -> None:
        with self._lock:
            self._last_failure_time = time.monotonic()
            self._transition(State.OPEN)

    @property
    def is_closed(self) -> bool:
        return self.state == State.CLOSED

    @property
    def is_open(self) -> bool:
        return self.state == State.OPEN

    @property
    def is_half_open(self) -> bool:
        return self.state == State.HALF_OPEN

    @property
    def stats(self) -> dict[str, Any]:
        with self._lock:
            return {
                "name": self.name,
                "state": self._state.value,
                "failure_count": self._failure_count,
                "success_count": self._success_count,
                "total_calls": self._total_calls,
                "total_failures": self._total_failures,
                "total_successes": self._total_successes,
            }

    def retry_after(self) -> float:
        with self._lock:
            if self._state != State.OPEN or self._last_failure_time is None:
                return 0.0
            return max(0.0, self.recovery_timeout - (time.monotonic() - self._last_failure_time))

    def __repr__(self) -> str:
        return (
            f"CircuitBreaker({self.name!r}, state={self.state.value}, "
            f"failures={self._failure_count}/{self.failure_threshold})"
        )


class CircuitBreakerRegistry:
    def __init__(self) -> None:
        self._breakers: dict[str, CircuitBreaker] = {}
        self._lock = threading.Lock()

    def get_or_create(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: float = 30.0,
        success_threshold: int = 2,
        **kwargs,
    ) -> CircuitBreaker:
        with self._lock:
            if name not in self._breakers:
                self._breakers[name] = CircuitBreaker(
                    name=name,
                    failure_threshold=failure_threshold,
                    recovery_timeout=recovery_timeout,
                    success_threshold=success_threshold,
                    **kwargs,
                )
            return self._breakers[name]

    def get(self, name: str) -> CircuitBreaker | None:
        with self._lock:
            return self._breakers.get(name)

    def reset_all(self) -> None:
        with self._lock:
            for cb in self._breakers.values():
                cb.reset()

    def stats(self) -> dict[str, Any]:
        with self._lock:
            return {name: cb.stats for name, cb in self._breakers.items()}

    def names(self) -> list[str]:
        with self._lock:
            return list(self._breakers.keys())

    def __repr__(self) -> str:
        with self._lock:
            return f"CircuitBreakerRegistry({list(self._breakers.keys())})"


_default_registry = CircuitBreakerRegistry()


def circuit_breaker(
    name: str,
    failure_threshold: int = 5,
    recovery_timeout: float = 30.0,
    success_threshold: int = 2,
    expected_exceptions: tuple[Type[Exception], ...] = (Exception,),
) -> Callable:
    """Decorator that wraps a function with a named circuit breaker."""
    cb = _default_registry.get_or_create(
        name,
        failure_threshold=failure_threshold,
        recovery_timeout=recovery_timeout,
        success_threshold=success_threshold,
        expected_exceptions=expected_exceptions,
    )

    def decorator(fn: Callable) -> Callable:
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            return cb.call(fn, *args, **kwargs)
        wrapper._circuit_breaker = cb
        return wrapper
    return decorator


if __name__ == "__main__":
    print("--- basic circuit breaker (threshold=3) ---")
    cb = CircuitBreaker(name="api", failure_threshold=3, recovery_timeout=0.2, success_threshold=2)
    print("initial state:", cb.state.value)

    def flaky(fail=False):
        if fail:
            raise ConnectionError("timeout")
        return "ok"

    print("call ok:", cb.call(flaky))

    for i in range(3):
        try:
            cb.call(flaky, fail=True)
        except ConnectionError:
            pass
    print("after 3 failures:", cb.state.value)
    print(cb)

    print("\n--- open circuit rejects calls ---")
    try:
        cb.call(flaky)
    except CircuitBreakerOpen as e:
        print(f"Caught: {e}")

    print("\n--- recovery (half-open -> closed) ---")
    time.sleep(0.25)
    print("state after timeout:", cb.state.value)
    cb.call(flaky)
    cb.call(flaky)
    print("state after 2 successes:", cb.state.value)

    print("\n--- stats ---")
    for k, v in cb.stats.items():
        print(f"  {k}: {v}")

    print("\n--- callbacks ---")
    events = []
    cb2 = CircuitBreaker(
        name="db",
        failure_threshold=2,
        recovery_timeout=0.1,
        on_open=lambda c: events.append("opened"),
        on_close=lambda c: events.append("closed"),
        on_half_open=lambda c: events.append("half_open"),
    )
    try: cb2.call(flaky, fail=True)
    except: pass
    try: cb2.call(flaky, fail=True)
    except: pass
    time.sleep(0.15)
    cb2.call(flaky)
    print("events:", events)

    print("\n--- as decorator ---")
    cb3 = CircuitBreaker(name="svc", failure_threshold=2, recovery_timeout=60.0)

    @cb3
    def fetch_data(fail=False):
        if fail:
            raise RuntimeError("unavailable")
        return "data"

    print("fetch ok:", fetch_data())
    try: fetch_data(fail=True)
    except RuntimeError: pass
    try: fetch_data(fail=True)
    except RuntimeError: pass
    print("state:", cb3.state.value)
    try:
        fetch_data()
    except CircuitBreakerOpen as e:
        print(f"Caught: {e}")

    print("\n--- @circuit_breaker decorator ---")
    @circuit_breaker("payment", failure_threshold=2, recovery_timeout=60.0)
    def charge(fail=False):
        if fail:
            raise ValueError("declined")
        return "charged"

    print("charge ok:", charge())
    try: charge(fail=True)
    except ValueError: pass
    try: charge(fail=True)
    except ValueError: pass
    try:
        charge()
    except CircuitBreakerOpen as e:
        print(f"Caught: {e}")

    print("\n--- registry ---")
    print("registered:", _default_registry.names())
    for name, s in _default_registry.stats().items():
        print(f"  {name}: state={s['state']} calls={s['total_calls']}")

    print("\n--- manual trip / reset ---")
    cb4 = CircuitBreaker(name="manual", failure_threshold=5, recovery_timeout=60.0)
    cb4.trip()
    print("after trip:", cb4.state.value)
    cb4.reset()
    print("after reset:", cb4.state.value)
