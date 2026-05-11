import os
import re
import shutil
import hashlib
import tempfile
from pathlib import Path
from typing import Generator


def read_lines(path: str, encoding: str = "utf-8") -> list[str]:
    return Path(path).read_text(encoding=encoding).splitlines()


def write_lines(path: str, lines: list[str], encoding: str = "utf-8") -> None:
    Path(path).write_text("\n".join(lines), encoding=encoding)


def read_bytes(path: str) -> bytes:
    return Path(path).read_bytes()


def write_bytes(path: str, data: bytes) -> None:
    Path(path).write_bytes(data)


def append_text(path: str, text: str, encoding: str = "utf-8") -> None:
    with open(path, "a", encoding=encoding) as f:
        f.write(text)


def head(path: str, n: int = 10, encoding: str = "utf-8") -> list[str]:
    lines = []
    with open(path, encoding=encoding) as f:
        for i, line in enumerate(f):
            if i >= n:
                break
            lines.append(line.rstrip("\n"))
    return lines


def tail(path: str, n: int = 10, encoding: str = "utf-8") -> list[str]:
    with open(path, encoding=encoding) as f:
        all_lines = f.readlines()
    return [line.rstrip("\n") for line in all_lines[-n:]]


def count_lines(path: str, encoding: str = "utf-8") -> int:
    with open(path, encoding=encoding) as f:
        return sum(1 for _ in f)


def grep(path: str, pattern: str, encoding: str = "utf-8") -> list[tuple[int, str]]:
    regex = re.compile(pattern)
    matches = []
    with open(path, encoding=encoding) as f:
        for i, line in enumerate(f, 1):
            if regex.search(line):
                matches.append((i, line.rstrip("\n")))
    return matches


def stream_lines(path: str, encoding: str = "utf-8") -> Generator[str, None, None]:
    with open(path, encoding=encoding) as f:
        for line in f:
            yield line.rstrip("\n")


def find_files(directory: str, pattern: str = "*") -> list[str]:
    return sorted(str(p) for p in Path(directory).rglob(pattern) if p.is_file())


def atomic_write(path: str, content: str, encoding: str = "utf-8") -> None:
    dir_name = os.path.dirname(os.path.abspath(path))
    with tempfile.NamedTemporaryFile("w", dir=dir_name, delete=False,
                                     encoding=encoding, suffix=".tmp") as tmp:
        tmp.write(content)
        tmp_path = tmp.name
    os.replace(tmp_path, path)


def backup(path: str) -> str:
    bak_path = path + ".bak"
    shutil.copy2(path, bak_path)
    return bak_path


def checksum(path: str, algorithm: str = "sha256") -> str:
    h = hashlib.new(algorithm)
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def touch(path: str) -> None:
    Path(path).touch()


def file_size(path: str) -> int:
    return os.path.getsize(path)


if __name__ == "__main__":
    import tempfile
    import os

    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as f:
        f.write("\n".join(f"line {i}" for i in range(1, 21)))
        tmp = f.name

    print("head(5):      ", head(tmp, 5))
    print("tail(5):      ", tail(tmp, 5))
    print("count_lines:  ", count_lines(tmp))
    print("grep('1'):    ", grep(tmp, r"\b1\b"))

    print("\nstream first 3:")
    for i, line in enumerate(stream_lines(tmp)):
        if i >= 3:
            break
        print(" ", line)

    atomic_write(tmp, "rewritten atomically\nline 2\nline 3")
    print("\nafter atomic_write, head(3):", head(tmp, 3))

    bak = backup(tmp)
    print("backup created:", bak)
    print("checksum (sha256):", checksum(tmp)[:20] + "...")
    print("file_size:", file_size(tmp), "bytes")

    os.unlink(tmp)
    os.unlink(bak)
    print("\ntemp files cleaned up")
