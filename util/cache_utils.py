import time
from typing import Any


class Cache:
    def __init__(self, ttl: float | None = None):
        self._store: dict[str, tuple[Any, float | None]] = {}
        self._ttl = ttl

    def set(self, key: str, value: Any, ttl: float | None = None) -> None:
        expires_at = time.time() + (ttl or self._ttl) if (ttl or self._ttl) else None
        self._store[key] = (value, expires_at)

    def get(self, key: str, default: Any = None) -> Any:
        if key not in self._store:
            return default
        value, expires_at = self._store[key]
        if expires_at and time.time() > expires_at:
            del self._store[key]
            return default
        return value

    def delete(self, key: str) -> bool:
        return self._store.pop(key, None) is not None

    def has(self, key: str) -> bool:
        return self.get(key) is not None

    def clear(self) -> None:
        self._store.clear()

    def purge_expired(self) -> int:
        now = time.time()
        expired = [k for k, (_, exp) in self._store.items() if exp and now > exp]
        for key in expired:
            del self._store[key]
        return len(expired)

    def size(self) -> int:
        return len(self._store)

    def __repr__(self) -> str:
        return f"Cache(size={self.size()}, ttl={self._ttl})"


if __name__ == "__main__":
    cache = Cache(ttl=2)
    print(cache)

    cache.set("user", {"name": "Grzegorz"})
    cache.set("lang", "pl")
    cache.set("temp", "expires soon", ttl=1)

    print("user:     ", cache.get("user"))
    print("lang:     ", cache.get("lang"))
    print("has temp: ", cache.has("temp"))
    print("size:     ", cache.size())

    time.sleep(1.1)
    print("\nafter 1.1s:")
    print("has temp: ", cache.has("temp"))
    print("purged:   ", cache.purge_expired(), "expired entries")

    cache.delete("lang")
    print("has lang: ", cache.has("lang"))
    print("size:     ", cache.size())
