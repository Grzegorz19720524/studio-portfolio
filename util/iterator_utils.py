import itertools
from collections import deque
from typing import Any, Iterable, Callable


def chunks(iterable: Iterable, n: int) -> Iterable:
    it = iter(iterable)
    while True:
        batch = list(itertools.islice(it, n))
        if not batch:
            return
        yield batch


def sliding_window(iterable: Iterable, n: int) -> Iterable:
    it = iter(iterable)
    window = deque(itertools.islice(it, n), maxlen=n)
    if len(window) == n:
        yield tuple(window)
    for item in it:
        window.append(item)
        yield tuple(window)


def pairwise(iterable: Iterable) -> Iterable:
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)


def flatten(iterable: Iterable) -> list:
    return list(itertools.chain.from_iterable(iterable))


def deep_flatten(iterable: Iterable) -> list:
    result = []
    for item in iterable:
        if isinstance(item, (list, tuple, set, frozenset)):
            result.extend(deep_flatten(item))
        else:
            result.append(item)
    return result


def interleave(*iterables: Iterable) -> list:
    return [item for pair in itertools.zip_longest(*iterables) for item in pair if item is not None]


def roundrobin(*iterables: Iterable) -> list:
    nexts = itertools.cycle(iter(it).__next__ for it in iterables)
    pending = len(iterables)
    result = []
    while pending:
        try:
            for fn in nexts:
                result.append(fn())
        except StopIteration:
            pending -= 1
            nexts = itertools.cycle(itertools.islice(nexts, pending))
    return result


def first(iterable: Iterable, default: Any = None) -> Any:
    return next(iter(iterable), default)


def last(iterable: Iterable, default: Any = None) -> Any:
    item = default
    for item in iterable:
        pass
    return item


def nth(iterable: Iterable, n: int, default: Any = None) -> Any:
    return next(itertools.islice(iterable, n, None), default)


def count_items(iterable: Iterable) -> int:
    return sum(1 for _ in iterable)


def all_equal(iterable: Iterable) -> bool:
    g = itertools.groupby(iterable)
    return next(g, True) and not next(g, False)


def minmax(iterable: Iterable) -> tuple[Any, Any]:
    it = iter(iterable)
    lo = hi = next(it)
    for item in it:
        if item < lo:
            lo = item
        if item > hi:
            hi = item
    return lo, hi


def accumulate(iterable: Iterable, fn: Callable = lambda a, b: a + b) -> list:
    return list(itertools.accumulate(iterable, fn))


def zip_longest(*iterables: Iterable, fillvalue: Any = None) -> list[tuple]:
    return list(itertools.zip_longest(*iterables, fillvalue=fillvalue))


def product(*iterables: Iterable) -> list[tuple]:
    return list(itertools.product(*iterables))


def permutations(iterable: Iterable, r: int | None = None) -> list[tuple]:
    return list(itertools.permutations(iterable, r))


def combinations(iterable: Iterable, r: int) -> list[tuple]:
    return list(itertools.combinations(iterable, r))


def combinations_with_replacement(iterable: Iterable, r: int) -> list[tuple]:
    return list(itertools.combinations_with_replacement(iterable, r))


class Peekable:
    def __init__(self, iterable: Iterable):
        self._it = iter(iterable)
        self._cache: deque = deque()

    def peek(self, default: Any = None) -> Any:
        if not self._cache:
            try:
                self._cache.append(next(self._it))
            except StopIteration:
                return default
        return self._cache[0]

    def __next__(self) -> Any:
        if self._cache:
            return self._cache.popleft()
        return next(self._it)

    def __iter__(self):
        return self


if __name__ == "__main__":
    data = range(10)

    print("chunks(10, 3):      ", list(chunks(data, 3)))
    print("sliding_window(3):  ", list(sliding_window(data, 3))[:4], "...")
    print("pairwise:           ", list(pairwise([1, 2, 3, 4])))
    print("flatten:            ", flatten([[1, 2], [3, 4], [5]]))
    print("deep_flatten:       ", deep_flatten([1, [2, [3, [4]]], 5]))
    print("interleave:         ", interleave([1, 3, 5], [2, 4, 6]))
    print("roundrobin:         ", roundrobin("ABC", "DE", "FGH"))
    print()
    print("first([10,20,30]):  ", first([10, 20, 30]))
    print("last([10,20,30]):   ", last([10, 20, 30]))
    print("nth([10,20,30], 1): ", nth(iter([10, 20, 30]), 1))
    print("count_items:        ", count_items(range(100)))
    print("all_equal([1,1,1]): ", all_equal([1, 1, 1]))
    print("all_equal([1,2,1]): ", all_equal([1, 2, 1]))
    print("minmax([3,1,4,1,5]):", minmax([3, 1, 4, 1, 5]))
    print()
    print("accumulate([1..5]): ", accumulate([1, 2, 3, 4, 5]))
    print("zip_longest:        ", zip_longest([1, 2, 3], [4, 5], fillvalue=0))
    print("product([1,2],[A,B]):", product([1, 2], ["A", "B"]))
    print("permutations(3,2):  ", permutations([1, 2, 3], 2))
    print("combinations(4,2):  ", combinations([1, 2, 3, 4], 2))
    print()
    print("Peekable:")
    p = Peekable([10, 20, 30])
    print("  peek:", p.peek())
    print("  next:", next(p))
    print("  peek:", p.peek())
    print("  rest:", list(p))
