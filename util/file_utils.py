import json
import shutil
from pathlib import Path


def read_text(path: str, encoding: str = "utf-8") -> str:
    return Path(path).read_text(encoding=encoding)


def write_text(path: str, content: str, encoding: str = "utf-8") -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding=encoding)


def read_json(path: str) -> dict | list:
    return json.loads(read_text(path))


def write_json(path: str, data: dict | list, indent: int = 2) -> None:
    write_text(path, json.dumps(data, indent=indent, ensure_ascii=False))


def file_exists(path: str) -> bool:
    return Path(path).is_file()


def ensure_dir(path: str) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def delete_file(path: str) -> bool:
    p = Path(path)
    if p.is_file():
        p.unlink()
        return True
    return False


def copy_file(src: str, dst: str) -> None:
    Path(dst).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def list_files(directory: str, pattern: str = "*") -> list[Path]:
    return sorted(Path(directory).glob(pattern))


if __name__ == "__main__":
    ensure_dir("tmp")

    write_text("tmp/hello.txt", "Hello, World!")
    print(read_text("tmp/hello.txt"))

    write_json("tmp/data.json", {"name": "Claude", "version": 4})
    print(read_json("tmp/data.json"))

    copy_file("tmp/hello.txt", "tmp/hello_copy.txt")
    print(list_files("tmp"))

    print(file_exists("tmp/hello.txt"))
    print(delete_file("tmp/hello.txt"))
    print(file_exists("tmp/hello.txt"))

    shutil.rmtree("tmp")
