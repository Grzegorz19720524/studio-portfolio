import functools
import itertools
from typing import Callable, Any, Iterable


def identity(x: Any) -> Any:
    return x


def always(x: Any) -> Callable:
    return lambda *args, **kwargs: x


def pipe(*fns: Callable) -> Callable:
    def _pipe(value):
        for fn in fns:
            value = fn(value)
        return value
    return _pipe


def compose(*fns: Callable) -> Callable:
    return pipe(*reversed(fns))


def partial(fn: Callable, *args, **kwargs) -> Callable:
    return functools.partial(fn, *args, **kwargs)


def curry(fn: Callable) -> Callable:
    arity = fn.__code__.co_argcount

    def curried(*args):
        if len(args) >= arity:
            return fn(*args)
        return lambda *more: curried(*(args + more))

    return curried


def flip(fn: Callable) -> Callable:
    def flipped(a, b, *args, **kwargs):
        return fn(b, a, *args, **kwargs)
    return flipped


def tap(fn: Callable) -> Callable:
    def _tap(value):
        fn(value)
        return value
    return _tap


def complement(fn: Callable) -> Callable:
    return lambda *args, **kwargs: not fn(*args, **kwargs)


def juxt(*fns: Callable) -> Callable:
    return lambda *args, **kwargs: [fn(*args, **kwargs) for fn in fns]


def memoize(fn: Callable) -> Callable:
    return functools.lru_cache(maxsize=None)(fn)


def reduce(fn: Callable, iterable: Iterable, initial: Any = None) -> Any:
    if initial is None:
        return functools.reduce(fn, iterable)
    return functools.reduce(fn, iterable, initial)


def scan(fn: Callable, iterable: Iterable, initial: Any) -> list[Any]:
    result = [initial]
    acc = initial
    for item in iterable:
        acc = fn(acc, item)
        result.append(acc)
    return result


def take(n: int, iterable: Iterable) -> list:
    return list(itertools.islice(iterable, n))


def drop(n: int, iterable: Iterable) -> list:
    return list(itertools.islice(iterable, n, None))


def partition(pred: Callable, iterable: Iterable) -> tuple[list, list]:
    true_items, false_items = [], []
    for item in iterable:
        (true_items if pred(item) else false_items).append(item)
    return true_items, false_items


def group_by(fn: Callable, iterable: Iterable) -> dict:
    result: dict = {}
    for item in iterable:
        key = fn(item)
        result.setdefault(key, []).append(item)
    return result


def zip_with(fn: Callable, *iterables: Iterable) -> list:
    return [fn(*args) for args in zip(*iterables)]


def unique(iterable: Iterable, key: Callable | None = None) -> list:
    seen = set()
    result = []
    for item in iterable:
        k = key(item) if key else item
        if k not in seen:
            seen.add(k)
            result.append(item)
    return result


def flatten_iter(iterable: Iterable, depth: int = 1) -> list:
    result = []
    for item in iterable:
        if depth > 0 and isinstance(item, (list, tuple)):
            result.extend(flatten_iter(item, depth - 1))
        else:
            result.append(item)
    return result


def iterate(fn: Callable, x: Any):
    while True:
        yield x
        x = fn(x)


if __name__ == "__main__":
    print("--- pipe ---")
    process = pipe(str.strip, str.lower, lambda s: s.replace(" ", "-"))
    print(process("  Hello World  "))

    print("\n--- compose ---")
    double_then_str = compose(str, lambda x: x * 2)
    print(double_then_str(21))

    print("\n--- curry ---")
    add = curry(lambda a, b, c: a + b + c)
    print(add(1)(2)(3))
    print(add(1, 2)(3))

    print("\n--- flip ---")
    sub = flip(lambda a, b: a - b)
    print(sub(3, 10))

    print("\n--- tap ---")
    log = tap(lambda x: print(f"  value: {x}"))
    result = log(42)
    print("  returned:", result)

    print("\n--- complement ---")
    is_odd = complement(lambda x: x % 2 == 0)
    print(list(filter(is_odd, range(10))))

    print("\n--- juxt ---")
    stats = juxt(min, max, sum, len)
    print(stats([3, 1, 4, 1, 5, 9, 2, 6]))

    print("\n--- scan ---")
    print(scan(lambda a, b: a + b, [1, 2, 3, 4, 5], 0))

    print("\n--- partition ---")
    evens, odds = partition(lambda x: x % 2 == 0, range(10))
    print("evens:", evens, " odds:", odds)

    print("\n--- group_by ---")
    print(group_by(lambda x: x % 3, range(9)))

    print("\n--- zip_with ---")
    print(zip_with(lambda a, b: a * b, [1, 2, 3], [4, 5, 6]))

    print("\n--- unique ---")
    print(unique([1, 2, 2, 3, 1, 4, 3]))
    print(unique(["foo", "bar", "FOO"], key=str.lower))

    print("\n--- flatten_iter ---")
    print(flatten_iter([[1, [2, 3]], [4, 5]], depth=1))
    print(flatten_iter([[1, [2, 3]], [4, 5]], depth=2))

    print("\n--- iterate (first 8 powers of 2) ---")
    print(take(8, iterate(lambda x: x * 2, 1)))
