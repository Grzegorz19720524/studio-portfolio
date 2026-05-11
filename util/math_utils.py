import math
from typing import Sequence


def clamp(value: float, min_val: float, max_val: float) -> float:
    return max(min_val, min(value, max_val))


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def normalize(values: Sequence[float]) -> list[float]:
    min_v, max_v = min(values), max(values)
    if min_v == max_v:
        return [0.0] * len(values)
    return [(v - min_v) / (max_v - min_v) for v in values]


def mean(values: Sequence[float]) -> float:
    return sum(values) / len(values)


def median(values: Sequence[float]) -> float:
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    mid = n // 2
    return sorted_vals[mid] if n % 2 else (sorted_vals[mid - 1] + sorted_vals[mid]) / 2


def variance(values: Sequence[float]) -> float:
    m = mean(values)
    return sum((v - m) ** 2 for v in values) / len(values)


def std_dev(values: Sequence[float]) -> float:
    return math.sqrt(variance(values))


def round_to(value: float, decimals: int) -> float:
    return round(value, decimals)


def percentage(part: float, total: float) -> float:
    if total == 0:
        return 0.0
    return (part / total) * 100


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    return all(n % i != 0 for i in range(2, int(math.sqrt(n)) + 1))


if __name__ == "__main__":
    data = [4, 8, 15, 16, 23, 42]

    print("clamp(15, 0, 10):  ", clamp(15, 0, 10))
    print("lerp(0, 100, 0.25):", lerp(0, 100, 0.25))
    print("normalize:         ", [round_to(v, 2) for v in normalize(data)])
    print("mean:              ", mean(data))
    print("median:            ", median(data))
    print("variance:          ", round_to(variance(data), 2))
    print("std_dev:           ", round_to(std_dev(data), 2))
    print("percentage(8, 40): ", percentage(8, 40))
    print("is_prime(23):      ", is_prime(23))
    print("is_prime(42):      ", is_prime(42))
