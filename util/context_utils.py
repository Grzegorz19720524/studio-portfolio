import time
import os
import sys
import tempfile
import shutil
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def timer(label: str = ""):
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed = time.perf_counter() - start
        tag = f"[{label}] " if label else ""
        print(f"{tag}elapsed: {elapsed:.4f}s")


@contextmanager
def suppress(*exceptions):
    try:
        yield
    except exceptions:
        pass


@contextmanager
def temp_dir():
    path = tempfile.mkdtemp()
    try:
        yield Path(path)
    finally:
        shutil.rmtree(path, ignore_errors=True)


@contextmanager
def temp_env(**env_vars):
    original = {k: os.environ.get(k) for k in env_vars}
    os.environ.update({k: str(v) for k, v in env_vars.items()})
    try:
        yield
    finally:
        for key, val in original.items():
            if val is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = val


@contextmanager
def redirect_stdout(target):
    old = sys.stdout
    sys.stdout = target
    try:
        yield target
    finally:
        sys.stdout = old


@contextmanager
def chdir(path: str):
    original = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(original)


class ManagedResource:
    def __init__(self, name: str):
        self.name = name
        self.active = False

    def __enter__(self):
        self.active = True
        print(f"  [{self.name}] acquired")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.active = False
        print(f"  [{self.name}] released")
        return False

    def __repr__(self) -> str:
        return f"ManagedResource(name={self.name!r}, active={self.active})"


if __name__ == "__main__":
    print("--- timer ---")
    with timer("loop"):
        total = sum(range(1_000_000))
    print("sum:", total)

    print("\n--- suppress ---")
    with suppress(ZeroDivisionError, ValueError):
        x = 1 / 0
    print("suppressed ZeroDivisionError")

    print("\n--- temp_dir ---")
    with temp_dir() as d:
        (d / "test.txt").write_text("hello")
        print("temp file:", (d / "test.txt").read_text())
    print("temp dir cleaned up:", not d.exists())

    print("\n--- temp_env ---")
    with temp_env(MY_VAR="hello", DEBUG="1"):
        print("MY_VAR:", os.environ.get("MY_VAR"))
    print("MY_VAR after:", os.environ.get("MY_VAR"))

    print("\n--- ManagedResource ---")
    with ManagedResource("db_connection") as res:
        print(" ", res)
    print("active after:", res.active)
