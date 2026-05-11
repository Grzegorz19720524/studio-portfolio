import threading
import time
import queue
from typing import Callable, Any


def run_in_thread(fn: Callable, *args, daemon: bool = True, **kwargs) -> threading.Thread:
    t = threading.Thread(target=fn, args=args, kwargs=kwargs, daemon=daemon)
    t.start()
    return t


def run_parallel(fns: list[Callable], *args) -> list[threading.Thread]:
    threads = [threading.Thread(target=fn, args=args, daemon=True) for fn in fns]
    for t in threads:
        t.start()
    return threads


def join_all(threads: list[threading.Thread], timeout: float | None = None) -> None:
    for t in threads:
        t.join(timeout=timeout)


def current_thread_name() -> str:
    return threading.current_thread().name


def active_count() -> int:
    return threading.active_count()


def timeout_call(fn: Callable, timeout: float, *args, **kwargs) -> Any:
    result = [None]
    exc = [None]

    def target():
        try:
            result[0] = fn(*args, **kwargs)
        except Exception as e:
            exc[0] = e

    t = threading.Thread(target=target, daemon=True)
    t.start()
    t.join(timeout=timeout)
    if t.is_alive():
        raise TimeoutError(f"Function did not complete within {timeout}s")
    if exc[0]:
        raise exc[0]
    return result[0]


class AtomicInt:
    def __init__(self, value: int = 0):
        self._value = value
        self._lock = threading.Lock()

    def increment(self, by: int = 1) -> int:
        with self._lock:
            self._value += by
            return self._value

    def decrement(self, by: int = 1) -> int:
        with self._lock:
            self._value -= by
            return self._value

    def get(self) -> int:
        with self._lock:
            return self._value

    def set(self, value: int) -> None:
        with self._lock:
            self._value = value

    def __repr__(self) -> str:
        return f"AtomicInt({self._value})"


class RWLock:
    def __init__(self):
        self._read_ready = threading.Condition(threading.Lock())
        self._readers = 0

    def acquire_read(self) -> None:
        with self._read_ready:
            self._readers += 1

    def release_read(self) -> None:
        with self._read_ready:
            self._readers -= 1
            if self._readers == 0:
                self._read_ready.notify_all()

    def acquire_write(self) -> None:
        self._read_ready.acquire()
        while self._readers > 0:
            self._read_ready.wait()

    def release_write(self) -> None:
        self._read_ready.release()


class Debouncer:
    def __init__(self, fn: Callable, delay: float):
        self.fn = fn
        self.delay = delay
        self._timer: threading.Timer | None = None
        self._lock = threading.Lock()

    def __call__(self, *args, **kwargs) -> None:
        with self._lock:
            if self._timer:
                self._timer.cancel()
            self._timer = threading.Timer(self.delay, self.fn, args, kwargs)
            self._timer.start()

    def cancel(self) -> None:
        with self._lock:
            if self._timer:
                self._timer.cancel()


class Throttler:
    def __init__(self, fn: Callable, interval: float):
        self.fn = fn
        self.interval = interval
        self._last: float = 0
        self._lock = threading.Lock()

    def __call__(self, *args, **kwargs) -> Any | None:
        with self._lock:
            now = time.monotonic()
            if now - self._last >= self.interval:
                self._last = now
                return self.fn(*args, **kwargs)
        return None


class PeriodicTimer:
    def __init__(self, fn: Callable, interval: float):
        self.fn = fn
        self.interval = interval
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)

    def _run(self) -> None:
        while not self._stop.wait(self.interval):
            self.fn()

    def start(self) -> None:
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()


class ThreadPool:
    def __init__(self, workers: int = 4):
        self._queue: queue.Queue = queue.Queue()
        self._threads = [
            threading.Thread(target=self._worker, daemon=True)
            for _ in range(workers)
        ]
        for t in self._threads:
            t.start()

    def _worker(self) -> None:
        while True:
            fn, args, kwargs = self._queue.get()
            try:
                fn(*args, **kwargs)
            finally:
                self._queue.task_done()

    def submit(self, fn: Callable, *args, **kwargs) -> None:
        self._queue.put((fn, args, kwargs))

    def wait(self) -> None:
        self._queue.join()


if __name__ == "__main__":
    print("--- run_in_thread ---")
    results = []
    lock = threading.Lock()

    def task(n):
        time.sleep(0.05)
        with lock:
            results.append(n)

    threads = [run_in_thread(task, i) for i in range(5)]
    join_all(threads)
    print("collected:", sorted(results))

    print("\n--- AtomicInt ---")
    counter = AtomicInt(0)
    workers = [run_in_thread(lambda: [counter.increment() for _ in range(100)]) for _ in range(5)]
    join_all(workers)
    print("counter:", counter)

    print("\n--- timeout_call ---")
    try:
        result = timeout_call(lambda: (time.sleep(0.01), "ok")[1], timeout=1.0)
        print("result:", result)
        timeout_call(lambda: time.sleep(5), timeout=0.1)
    except TimeoutError as e:
        print("caught:", e)

    print("\n--- Debouncer ---")
    fired = []
    db = Debouncer(lambda: fired.append("fired"), delay=0.1)
    for _ in range(5):
        db()
        time.sleep(0.02)
    time.sleep(0.2)
    print("debounce fired:", len(fired), "time(s)")

    print("\n--- Throttler ---")
    calls = []
    th = Throttler(lambda: calls.append(1), interval=0.1)
    for _ in range(10):
        th()
        time.sleep(0.02)
    print("throttled calls:", len(calls))

    print("\n--- PeriodicTimer ---")
    ticks = []
    pt = PeriodicTimer(lambda: ticks.append(1), interval=0.05)
    pt.start()
    time.sleep(0.28)
    pt.stop()
    print("ticks:", len(ticks))

    print("\n--- ThreadPool ---")
    pool_results = []
    pool = ThreadPool(workers=3)
    for i in range(9):
        pool.submit(lambda n=i: pool_results.append(n))
    pool.wait()
    print("pool results:", sorted(pool_results))

    print("\nactive_count:", active_count())
    print("current_thread:", current_thread_name())
