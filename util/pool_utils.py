import threading
from typing import Callable, Any, Generic, TypeVar

T = TypeVar("T")


class ObjectPool(Generic[T]):
    def __init__(self, factory: Callable[[], T], max_size: int = 10):
        self._factory = factory
        self._max_size = max_size
        self._pool: list[T] = []
        self._lock = threading.Lock()
        self._created = 0

    def acquire(self) -> T:
        with self._lock:
            if self._pool:
                return self._pool.pop()
            if self._created < self._max_size:
                self._created += 1
                return self._factory()
            raise RuntimeError("Object pool exhausted")

    def release(self, obj: T) -> None:
        with self._lock:
            if len(self._pool) < self._max_size:
                self._pool.append(obj)

    def available(self) -> int:
        return len(self._pool)

    def size(self) -> int:
        return self._created

    def __repr__(self) -> str:
        return f"ObjectPool(available={self.available()}, created={self.size()}, max={self._max_size})"


class PoolContext:
    def __init__(self, pool: ObjectPool):
        self._pool = pool
        self._obj = None

    def __enter__(self):
        self._obj = self._pool.acquire()
        return self._obj

    def __exit__(self, *args):
        if self._obj is not None:
            self._pool.release(self._obj)
            self._obj = None


if __name__ == "__main__":
    class Connection:
        _count = 0

        def __init__(self):
            Connection._count += 1
            self.id = Connection._count

        def __repr__(self):
            return f"Connection(id={self.id})"

    pool = ObjectPool(Connection, max_size=3)
    print(pool)

    c1 = pool.acquire()
    c2 = pool.acquire()
    print("acquired:", c1, c2)
    print("available:", pool.available())

    pool.release(c1)
    pool.release(c2)
    print("after release:", pool)

    print("\nusing context manager:")
    with PoolContext(pool) as conn:
        print("  got:", conn)
        print("  available during use:", pool.available())
    print("  available after:", pool.available())
