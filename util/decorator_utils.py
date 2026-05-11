import time
import functools
import warnings
from typing import Callable, Any


def timer(fn: Callable) -> Callable:
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = fn(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"[timer] {fn.__name__} took {elapsed:.4f}s")
        return result
    return wrapper


def memoize(fn: Callable) -> Callable:
    cache: dict = {}

    @functools.wraps(fn)
    def wrapper(*args):
        if args not in cache:
            cache[args] = fn(*args)
        return cache[args]

    wrapper.cache = cache
    wrapper.clear_cache = cache.clear
    return wrapper


def retry(attempts: int = 3, delay: float = 0.0, exceptions: tuple = (Exception,)):
    def decorator(fn: Callable) -> Callable:
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(1, attempts + 1):
                try:
                    return fn(*args, **kwargs)
                except exceptions as e:
                    last_exc = e
                    if delay and attempt < attempts:
                        time.sleep(delay)
            raise last_exc
        return wrapper
    return decorator


def singleton(cls):
    instances: dict = {}

    @functools.wraps(cls)
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


def deprecated(reason: str = ""):
    def decorator(fn: Callable) -> Callable:
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            msg = f"{fn.__name__} is deprecated. {reason}".strip()
            warnings.warn(msg, DeprecationWarning, stacklevel=2)
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def clamp_result(min_val: float, max_val: float):
    def decorator(fn: Callable) -> Callable:
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            return max(min_val, min(max_val, fn(*args, **kwargs)))
        return wrapper
    return decorator


if __name__ == "__main__":
    @timer
    def slow_add(a, b):
        time.sleep(0.05)
        return a + b

    print("timer:", slow_add(2, 3))

    @memoize
    def fib(n):
        return n if n < 2 else fib(n - 1) + fib(n - 2)

    print("fib(10):", fib(10))
    print("fib(30):", fib(30))

    count = 0

    @retry(attempts=3, exceptions=(ValueError,))
    def flaky():
        global count
        count += 1
        if count < 3:
            raise ValueError("not yet")
        return "ok"

    print("retry:", flaky())

    @singleton
    class Config:
        def __init__(self):
            self.value = 42

    print("singleton:", Config() is Config())

    @deprecated("Use new_func() instead.")
    def old_func():
        return "old"

    import warnings
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        old_func()
        print("deprecated warning:", w[0].message)

    @clamp_result(0, 100)
    def score(x):
        return x * 10

    print("clamp_result:", score(15))
