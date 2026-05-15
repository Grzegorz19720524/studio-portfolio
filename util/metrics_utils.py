import time
import threading
from typing import Any


class Counter:
    def __init__(self, name: str, description: str = "") -> None:
        self.name = name
        self.description = description
        self._value: float = 0.0
        self._lock = threading.Lock()

    def inc(self, amount: float = 1.0) -> None:
        if amount < 0:
            raise ValueError("Counter can only increase")
        with self._lock:
            self._value += amount

    @property
    def value(self) -> float:
        with self._lock:
            return self._value

    def reset(self) -> None:
        with self._lock:
            self._value = 0.0

    def snapshot(self) -> dict[str, Any]:
        return {"type": "counter", "name": self.name, "value": self.value}

    def __repr__(self) -> str:
        return f"Counter({self.name!r}, value={self.value})"


class Gauge:
    def __init__(self, name: str, description: str = "") -> None:
        self.name = name
        self.description = description
        self._value: float = 0.0
        self._lock = threading.Lock()

    def set(self, value: float) -> None:
        with self._lock:
            self._value = value

    def inc(self, amount: float = 1.0) -> None:
        with self._lock:
            self._value += amount

    def dec(self, amount: float = 1.0) -> None:
        with self._lock:
            self._value -= amount

    @property
    def value(self) -> float:
        with self._lock:
            return self._value

    def reset(self) -> None:
        with self._lock:
            self._value = 0.0

    def snapshot(self) -> dict[str, Any]:
        return {"type": "gauge", "name": self.name, "value": self.value}

    def __repr__(self) -> str:
        return f"Gauge({self.name!r}, value={self.value})"


class Histogram:
    def __init__(self, name: str, buckets: list[float] | None = None, description: str = "") -> None:
        self.name = name
        self.description = description
        self._buckets = sorted(buckets or [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0])
        self._counts = [0] * len(self._buckets)
        self._sum: float = 0.0
        self._total: int = 0
        self._lock = threading.Lock()

    def observe(self, value: float) -> None:
        with self._lock:
            self._sum += value
            self._total += 1
            for i, bound in enumerate(self._buckets):
                if value <= bound:
                    self._counts[i] += 1

    @property
    def count(self) -> int:
        with self._lock:
            return self._total

    @property
    def sum(self) -> float:
        with self._lock:
            return self._sum

    @property
    def mean(self) -> float:
        with self._lock:
            return self._sum / self._total if self._total else 0.0

    def percentile(self, p: float) -> float:
        with self._lock:
            if self._total == 0:
                return 0.0
            target = p / 100.0 * self._total
            cumulative = 0
            for i, bound in enumerate(self._buckets):
                cumulative += self._counts[i]
                if cumulative >= target:
                    return bound
            return self._buckets[-1]

    def reset(self) -> None:
        with self._lock:
            self._counts = [0] * len(self._buckets)
            self._sum = 0.0
            self._total = 0

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            return {
                "type": "histogram",
                "name": self.name,
                "count": self._total,
                "sum": self._sum,
                "mean": self._sum / self._total if self._total else 0.0,
                "buckets": {str(b): c for b, c in zip(self._buckets, self._counts)},
            }

    def __repr__(self) -> str:
        return f"Histogram({self.name!r}, count={self.count}, mean={self.mean:.4f})"


class Summary:
    def __init__(self, name: str, description: str = "") -> None:
        self.name = name
        self.description = description
        self._values: list[float] = []
        self._sum: float = 0.0
        self._lock = threading.RLock()

    def observe(self, value: float) -> None:
        with self._lock:
            self._values.append(value)
            self._sum += value

    @property
    def count(self) -> int:
        with self._lock:
            return len(self._values)

    @property
    def sum(self) -> float:
        with self._lock:
            return self._sum

    @property
    def mean(self) -> float:
        with self._lock:
            return self._sum / len(self._values) if self._values else 0.0

    def percentile(self, p: float) -> float:
        with self._lock:
            if not self._values:
                return 0.0
            sorted_vals = sorted(self._values)
            idx = (p / 100.0) * (len(sorted_vals) - 1)
            lo, hi = int(idx), min(int(idx) + 1, len(sorted_vals) - 1)
            return sorted_vals[lo] + (idx - lo) * (sorted_vals[hi] - sorted_vals[lo])

    def reset(self) -> None:
        with self._lock:
            self._values.clear()
            self._sum = 0.0

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            n = len(self._values)
            mean = self._sum / n if n else 0.0
            return {
                "type": "summary",
                "name": self.name,
                "count": n,
                "sum": self._sum,
                "mean": mean,
                "p50": self.percentile(50),
                "p90": self.percentile(90),
                "p99": self.percentile(99),
            }

    def __repr__(self) -> str:
        return f"Summary({self.name!r}, count={self.count}, mean={self.mean:.4f})"


class Timer:
    def __init__(self, name: str, description: str = "") -> None:
        self.name = name
        self.description = description
        self._histogram = Histogram(name)
        self._active_start: float | None = None

    def __enter__(self) -> "Timer":
        self._active_start = time.perf_counter()
        return self

    def __exit__(self, *_) -> None:
        if self._active_start is not None:
            self._histogram.observe(time.perf_counter() - self._active_start)
            self._active_start = None

    def time(self, fn, *args, **kwargs):
        start = time.perf_counter()
        result = fn(*args, **kwargs)
        self._histogram.observe(time.perf_counter() - start)
        return result

    @property
    def count(self) -> int:
        return self._histogram.count

    @property
    def mean(self) -> float:
        return self._histogram.mean

    def percentile(self, p: float) -> float:
        return self._histogram.percentile(p)

    def reset(self) -> None:
        self._histogram.reset()

    def snapshot(self) -> dict[str, Any]:
        snap = self._histogram.snapshot()
        snap["type"] = "timer"
        return snap

    def __repr__(self) -> str:
        return f"Timer({self.name!r}, count={self.count}, mean={self.mean:.4f}s)"


class MetricsRegistry:
    def __init__(self) -> None:
        self._metrics: dict[str, Counter | Gauge | Histogram | Summary | Timer] = {}
        self._lock = threading.Lock()

    def _register(self, metric):
        with self._lock:
            if metric.name in self._metrics:
                return self._metrics[metric.name]
            self._metrics[metric.name] = metric
            return metric

    def counter(self, name: str, description: str = "") -> Counter:
        return self._register(Counter(name, description))

    def gauge(self, name: str, description: str = "") -> Gauge:
        return self._register(Gauge(name, description))

    def histogram(self, name: str, buckets: list[float] | None = None, description: str = "") -> Histogram:
        return self._register(Histogram(name, buckets, description))

    def summary(self, name: str, description: str = "") -> Summary:
        return self._register(Summary(name, description))

    def timer(self, name: str, description: str = "") -> Timer:
        return self._register(Timer(name, description))

    def get(self, name: str):
        with self._lock:
            return self._metrics.get(name)

    def reset_all(self) -> None:
        with self._lock:
            for m in self._metrics.values():
                m.reset()

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            return {name: m.snapshot() for name, m in self._metrics.items()}

    def report(self) -> None:
        for name, snap in self.snapshot().items():
            kind = snap["type"]
            if kind in ("counter", "gauge"):
                print(f"{name} [{kind}]: {snap['value']}")
            elif kind in ("histogram", "timer"):
                print(f"{name} [{kind}]: count={snap['count']} mean={snap['mean']:.4f} sum={snap['sum']:.4f}")
            elif kind == "summary":
                print(f"{name} [summary]: count={snap['count']} p50={snap['p50']:.4f} p90={snap['p90']:.4f} p99={snap['p99']:.4f}")

    def __repr__(self) -> str:
        with self._lock:
            return f"MetricsRegistry({list(self._metrics.keys())})"


_default_registry = MetricsRegistry()


def counter(name: str, description: str = "") -> Counter:
    return _default_registry.counter(name, description)


def gauge(name: str, description: str = "") -> Gauge:
    return _default_registry.gauge(name, description)


def histogram(name: str, buckets: list[float] | None = None, description: str = "") -> Histogram:
    return _default_registry.histogram(name, buckets, description)


def summary(name: str, description: str = "") -> Summary:
    return _default_registry.summary(name, description)


def timer(name: str, description: str = "") -> Timer:
    return _default_registry.timer(name, description)


def report() -> None:
    _default_registry.report()


def reset_all() -> None:
    _default_registry.reset_all()


def snapshot() -> dict[str, Any]:
    return _default_registry.snapshot()


if __name__ == "__main__":
    print("--- Counter ---")
    c = Counter("requests_total")
    c.inc()
    c.inc()
    c.inc(5)
    print(c)

    print("\n--- Gauge ---")
    g = Gauge("active_connections")
    g.set(10)
    g.inc(5)
    g.dec(3)
    print(g)

    print("\n--- Histogram ---")
    h = Histogram("response_time", buckets=[0.1, 0.5, 1.0, 2.0, 5.0])
    for v in [0.05, 0.2, 0.4, 0.9, 1.5, 3.0, 0.1, 0.3]:
        h.observe(v)
    print(h)
    print(f"  p50={h.percentile(50):.2f}  p90={h.percentile(90):.2f}  p99={h.percentile(99):.2f}")

    print("\n--- Summary ---")
    s = Summary("latency_ms")
    for v in [10, 20, 15, 50, 80, 100, 12, 18, 25, 200]:
        s.observe(v)
    print(s)
    print(f"  p50={s.percentile(50):.1f}  p90={s.percentile(90):.1f}  p99={s.percentile(99):.1f}")

    print("\n--- Timer (context manager) ---")
    t = Timer("db_query")
    for _ in range(3):
        with t:
            time.sleep(0.01)
    print(t)

    print("\n--- Timer (time function) ---")
    t2 = Timer("compute")
    t2.time(lambda: time.sleep(0.005))
    t2.time(lambda: time.sleep(0.008))
    print(t2)

    print("\n--- MetricsRegistry ---")
    reg = MetricsRegistry()
    req = reg.counter("http_requests")
    lat = reg.summary("http_latency")
    mem = reg.gauge("memory_mb")

    req.inc(42)
    for v in [5, 10, 8, 20, 15, 50]:
        lat.observe(v)
    mem.set(512.5)

    reg.report()

    print("\n--- default registry ---")
    counter("api.calls").inc(10)
    gauge("queue.depth").set(7)
    summary("job.duration").observe(1.2)
    summary("job.duration").observe(3.4)
    report()

    print("\n--- snapshot ---")
    snap = reg.snapshot()
    for name, data in snap.items():
        print(f"  {name}: {data}")
