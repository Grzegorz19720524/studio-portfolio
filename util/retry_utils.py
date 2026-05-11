import time
import random
from typing import Callable, Any, Type


def retry(
    func: Callable,
    *args,
    attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple[Type[Exception], ...] = (Exception,),
    **kwargs,
) -> Any:
    last_exc = None
    current_delay = delay
    for attempt in range(1, attempts + 1):
        try:
            return func(*args, **kwargs)
        except exceptions as e:
            last_exc = e
            if attempt < attempts:
                time.sleep(current_delay)
                current_delay *= backoff
    raise last_exc


def retry_with_jitter(
    func: Callable,
    *args,
    attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    jitter: float = 0.5,
    exceptions: tuple[Type[Exception], ...] = (Exception,),
    **kwargs,
) -> Any:
    last_exc = None
    current_delay = delay
    for attempt in range(1, attempts + 1):
        try:
            return func(*args, **kwargs)
        except exceptions as e:
            last_exc = e
            if attempt < attempts:
                sleep_time = current_delay + random.uniform(0, jitter)
                time.sleep(sleep_time)
                current_delay *= backoff
    raise last_exc


def with_fallback(func: Callable, fallback: Any, *args, **kwargs) -> Any:
    try:
        return func(*args, **kwargs)
    except Exception:
        return fallback


if __name__ == "__main__":
    call_count = 0

    def flaky(fail_times: int):
        global call_count
        call_count += 1
        if call_count <= fail_times:
            raise ValueError(f"Simulated failure #{call_count}")
        return f"success on attempt {call_count}"

    call_count = 0
    result = retry(flaky, 2, attempts=3, delay=0.1, exceptions=(ValueError,))
    print("retry result:   ", result)

    call_count = 0
    result = with_fallback(flaky, "fallback value", 99)
    print("fallback result:", result)
