import math
import statistics
from collections import Counter
from typing import Sequence


def mean(data: Sequence[float]) -> float:
    return statistics.mean(data)


def median(data: Sequence[float]) -> float:
    return statistics.median(data)


def mode(data: Sequence) -> any:
    return statistics.mode(data)


def multimode(data: Sequence) -> list:
    return statistics.multimode(data)


def variance(data: Sequence[float]) -> float:
    return statistics.variance(data)


def stdev(data: Sequence[float]) -> float:
    return statistics.stdev(data)


def pvariance(data: Sequence[float]) -> float:
    return statistics.pvariance(data)


def pstdev(data: Sequence[float]) -> float:
    return statistics.pstdev(data)


def harmonic_mean(data: Sequence[float]) -> float:
    return statistics.harmonic_mean(data)


def geometric_mean(data: Sequence[float]) -> float:
    return math.exp(sum(math.log(x) for x in data) / len(data))


def weighted_mean(data: Sequence[float], weights: Sequence[float]) -> float:
    return sum(x * w for x, w in zip(data, weights)) / sum(weights)


def quantile(data: Sequence[float], p: float) -> float:
    sorted_data = sorted(data)
    n = len(sorted_data)
    idx = p * (n - 1)
    lo, hi = int(idx), min(int(idx) + 1, n - 1)
    return sorted_data[lo] + (idx - lo) * (sorted_data[hi] - sorted_data[lo])


def quartiles(data: Sequence[float]) -> tuple[float, float, float]:
    return quantile(data, 0.25), quantile(data, 0.50), quantile(data, 0.75)


def iqr(data: Sequence[float]) -> float:
    q1, _, q3 = quartiles(data)
    return q3 - q1


def z_score(x: float, data: Sequence[float]) -> float:
    m, s = mean(data), stdev(data)
    return (x - m) / s if s != 0 else 0.0


def z_scores(data: Sequence[float]) -> list[float]:
    m, s = mean(data), stdev(data)
    return [(x - m) / s if s != 0 else 0.0 for x in data]


def normalize(data: Sequence[float]) -> list[float]:
    lo, hi = min(data), max(data)
    spread = hi - lo
    return [(x - lo) / spread if spread != 0 else 0.0 for x in data]


def standardize(data: Sequence[float]) -> list[float]:
    return z_scores(data)


def covariance(x: Sequence[float], y: Sequence[float]) -> float:
    n = len(x)
    mx, my = mean(x), mean(y)
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / (n - 1)


def correlation(x: Sequence[float], y: Sequence[float]) -> float:
    cov = covariance(x, y)
    sx, sy = stdev(x), stdev(y)
    return cov / (sx * sy) if sx and sy else 0.0


def moving_average(data: Sequence[float], window: int) -> list[float]:
    return [
        sum(data[i:i + window]) / window
        for i in range(len(data) - window + 1)
    ]


def outliers(data: Sequence[float], threshold: float = 2.0) -> list[float]:
    zs = z_scores(data)
    return [x for x, z in zip(data, zs) if abs(z) > threshold]


def frequency(data: Sequence) -> dict:
    total = len(data)
    counts = Counter(data)
    return {k: {"count": v, "pct": round(v / total * 100, 2)} for k, v in counts.most_common()}


def describe(data: Sequence[float]) -> dict:
    q1, q2, q3 = quartiles(data)
    return {
        "count": len(data),
        "mean": round(mean(data), 6),
        "median": round(median(data), 6),
        "mode": multimode(data),
        "stdev": round(stdev(data), 6),
        "variance": round(variance(data), 6),
        "min": min(data),
        "max": max(data),
        "range": max(data) - min(data),
        "q1": round(q1, 6),
        "q2": round(q2, 6),
        "q3": round(q3, 6),
        "iqr": round(iqr(data), 6),
    }


if __name__ == "__main__":
    data = [2, 4, 4, 4, 5, 5, 7, 9, 10, 12, 3, 8, 1, 6, 11]

    print("mean:            ", mean(data))
    print("median:          ", median(data))
    print("mode:            ", mode(data))
    print("multimode:       ", multimode(data))
    print("stdev:           ", round(stdev(data), 4))
    print("variance:        ", round(variance(data), 4))
    print("harmonic_mean:   ", round(harmonic_mean(data), 4))
    print("geometric_mean:  ", round(geometric_mean(data), 4))
    print()
    print("quartiles:       ", tuple(round(q, 4) for q in quartiles(data)))
    print("iqr:             ", round(iqr(data), 4))
    print("z_score(10):     ", round(z_score(10, data), 4))
    print()
    print("normalize[:5]:   ", [round(v, 4) for v in normalize(data)][:5])
    print("moving_avg(3)[:5]:", moving_average(data, 3)[:5])
    print()
    x = [1, 2, 3, 4, 5]
    y = [2, 4, 5, 4, 5]
    print("covariance(x,y): ", round(covariance(x, y), 4))
    print("correlation(x,y):", round(correlation(x, y), 4))
    print()
    noisy = [2, 4, 4, 5, 5, 7, 100, -50]
    print("outliers(noisy): ", outliers(noisy))
    print()
    print("frequency([1,2,2,3,3,3]):", frequency([1, 2, 2, 3, 3, 3]))
    print()
    print("describe(data):")
    for k, v in describe(data).items():
        print(f"  {k:<12} {v}")
