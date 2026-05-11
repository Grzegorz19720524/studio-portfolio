import time
import statistics
from typing import Callable, Any


def measure(fn: Callable, *args, runs: int = 100, **kwargs) -> dict:
    times = []
    for _ in range(runs):
        start = time.perf_counter()
        result = fn(*args, **kwargs)
        times.append(time.perf_counter() - start)
    return {
        "fn": fn.__name__,
        "runs": runs,
        "total": sum(times),
        "mean": statistics.mean(times),
        "median": statistics.median(times),
        "min": min(times),
        "max": max(times),
        "stdev": statistics.stdev(times) if runs > 1 else 0.0,
        "result": result,
    }


def compare(*fns: Callable, args: tuple = (), kwargs: dict | None = None, runs: int = 100) -> list[dict]:
    kwargs = kwargs or {}
    results = [measure(fn, *args, runs=runs, **kwargs) for fn in fns]
    results.sort(key=lambda r: r["mean"])
    fastest = results[0]["mean"]
    for r in results:
        r["relative"] = r["mean"] / fastest
    return results


def print_report(results: list[dict]) -> None:
    width = max(len(r["fn"]) for r in results) + 2
    print(f"{'Function':<{width}} {'Mean':>10} {'Median':>10} {'Min':>10} {'Max':>10} {'Rel':>6}")
    print("-" * (width + 50))
    for r in results:
        rel = f"{r['relative']:.2f}x"
        print(
            f"{r['fn']:<{width}} "
            f"{r['mean']*1000:>9.4f}ms "
            f"{r['median']*1000:>9.4f}ms "
            f"{r['min']*1000:>9.4f}ms "
            f"{r['max']*1000:>9.4f}ms "
            f"{rel:>6}"
        )


if __name__ == "__main__":
    def sum_builtin(n):
        return sum(range(n))

    def sum_loop(n):
        total = 0
        for i in range(n):
            total += i
        return total

    def sum_formula(n):
        return n * (n - 1) // 2

    print("Benchmarking sum implementations (n=10_000, 200 runs):\n")
    results = compare(sum_builtin, sum_loop, sum_formula, args=(10_000,), runs=200)
    print_report(results)

    print("\nFastest:", results[0]["fn"])
    print("Slowest:", results[-1]["fn"], f"({results[-1]['relative']:.2f}x slower)")
