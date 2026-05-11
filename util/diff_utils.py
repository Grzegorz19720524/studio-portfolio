import difflib
from typing import Any


def diff_ratio(a: str, b: str) -> float:
    return round(difflib.SequenceMatcher(None, a, b).ratio(), 4)


def is_similar(a: str, b: str, threshold: float = 0.8) -> bool:
    return diff_ratio(a, b) >= threshold


def unified_diff(a: str, b: str, fromfile: str = "a", tofile: str = "b") -> str:
    a_lines = a.splitlines(keepends=True)
    b_lines = b.splitlines(keepends=True)
    return "".join(difflib.unified_diff(a_lines, b_lines, fromfile=fromfile, tofile=tofile))


def ndiff(a: str, b: str) -> str:
    a_lines = a.splitlines(keepends=True)
    b_lines = b.splitlines(keepends=True)
    return "".join(difflib.ndiff(a_lines, b_lines))


def added_lines(a: str, b: str) -> list[str]:
    a_set = set(a.splitlines())
    return [line for line in b.splitlines() if line not in a_set]


def removed_lines(a: str, b: str) -> list[str]:
    b_set = set(b.splitlines())
    return [line for line in a.splitlines() if line not in b_set]


def common_lines(a: str, b: str) -> list[str]:
    a_set = set(a.splitlines())
    b_set = set(b.splitlines())
    return sorted(a_set & b_set)


def dict_diff(a: dict, b: dict) -> dict:
    added = {k: b[k] for k in b if k not in a}
    removed = {k: a[k] for k in a if k not in b}
    changed = {k: {"from": a[k], "to": b[k]} for k in a if k in b and a[k] != b[k]}
    return {"added": added, "removed": removed, "changed": changed}


def lcs(a: list[Any], b: list[Any]) -> list[Any]:
    matcher = difflib.SequenceMatcher(None, a, b)
    result = []
    for block in matcher.get_matching_blocks():
        result.extend(a[block.a: block.a + block.size])
    return result


def close_matches(word: str, possibilities: list[str], n: int = 3, cutoff: float = 0.6) -> list[str]:
    return difflib.get_close_matches(word, possibilities, n=n, cutoff=cutoff)


if __name__ == "__main__":
    a = "hello world\nfoo bar\nbaz"
    b = "hello world\nfoo baz\nqux"

    print("diff_ratio:")
    print(" ", diff_ratio("kitten", "sitting"))
    print(" ", diff_ratio("hello", "hello"))

    print("\nis_similar('hello', 'helo', 0.8):", is_similar("hello", "helo", 0.8))
    print("is_similar('cat', 'dog', 0.8):  ", is_similar("cat", "dog", 0.8))

    print("\nunified_diff:")
    print(unified_diff(a, b, fromfile="old.txt", tofile="new.txt"))

    print("added_lines:  ", added_lines(a, b))
    print("removed_lines:", removed_lines(a, b))
    print("common_lines: ", common_lines(a, b))

    print("\ndict_diff:")
    d1 = {"x": 1, "y": 2, "z": 3}
    d2 = {"x": 1, "y": 99, "w": 4}
    import pprint
    pprint.pprint(dict_diff(d1, d2))

    print("\nlcs([1,2,3,4,5], [2,4,5,6]):", lcs([1, 2, 3, 4, 5], [2, 4, 5, 6]))

    print("\nclose_matches('hellp', ['hello','world','help']):",
          close_matches("hellp", ["hello", "world", "help"]))
