import os
import signal
import threading
from typing import Callable, Any


def handle(sig: int, fn: Callable) -> Callable:
    old = signal.signal(sig, fn)
    return old


def ignore(sig: int) -> Callable:
    return signal.signal(sig, signal.SIG_IGN)


def reset(sig: int) -> Callable:
    return signal.signal(sig, signal.SIG_DFL)


def send(pid: int, sig: int) -> None:
    os.kill(pid, sig)


def raise_signal(sig: int) -> None:
    signal.raise_signal(sig)


def on_sigint(fn: Callable) -> None:
    signal.signal(signal.SIGINT, lambda s, f: fn())


def on_sigterm(fn: Callable) -> None:
    signal.signal(signal.SIGTERM, lambda s, f: fn())


def register_shutdown(fn: Callable) -> None:
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, lambda s, f: fn())


def current_handler(sig: int) -> Any:
    return signal.getsignal(sig)


def available_signals() -> dict[str, int]:
    return {
        name: num
        for name, num in signal.__dict__.items()
        if name.startswith("SIG") and not name.startswith("SIG_") and isinstance(num, int)
    }


class SignalCounter:
    def __init__(self, sig: int):
        self.sig = sig
        self.count = 0
        self._lock = threading.Lock()
        signal.signal(sig, self._handler)

    def _handler(self, signum, frame):
        with self._lock:
            self.count += 1

    def reset_count(self) -> None:
        with self._lock:
            self.count = 0


class GracefulShutdown:
    def __init__(self):
        self._shutdown = threading.Event()
        self._handlers: list[Callable] = []
        for sig in (signal.SIGINT, signal.SIGTERM):
            signal.signal(sig, self._handle)

    def _handle(self, signum, frame):
        self._shutdown.set()
        for fn in self._handlers:
            fn()

    def on_shutdown(self, fn: Callable) -> None:
        self._handlers.append(fn)

    def wait(self, timeout: float | None = None) -> bool:
        return self._shutdown.wait(timeout=timeout)

    @property
    def is_shutdown(self) -> bool:
        return self._shutdown.is_set()


if __name__ == "__main__":
    print("available_signals():")
    sigs = available_signals()
    for name, num in sorted(sigs.items(), key=lambda x: x[1]):
        print(f"  {name:<20} = {num}")

    print("\ncurrent_handler(SIGINT): ", current_handler(signal.SIGINT))
    print("current_handler(SIGTERM):", current_handler(signal.SIGTERM))

    received = []

    def my_handler(signum, frame):
        received.append(signum)

    old = handle(signal.SIGINT, my_handler)
    raise_signal(signal.SIGINT)
    print(f"\nafter raise_signal(SIGINT), received: {received}")

    reset(signal.SIGINT)
    print("after reset(SIGINT), handler:", current_handler(signal.SIGINT))

    print("\nSignalCounter demo:")
    counter = SignalCounter(signal.SIGINT)
    for _ in range(3):
        raise_signal(signal.SIGINT)
    print(f"  SIGINT received {counter.count} times")

    reset(signal.SIGINT)

    print("\nGracefulShutdown demo:")
    gs = GracefulShutdown()
    gs.on_shutdown(lambda: print("  shutdown handler called"))
    raise_signal(signal.SIGINT)
    print("  is_shutdown:", gs.is_shutdown)
