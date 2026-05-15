import tomllib
from typing import Any


def read_toml(path: str) -> dict:
    with open(path, "rb") as f:
        return tomllib.load(f)


def parse_string(text: str) -> dict:
    return tomllib.loads(text)


def _toml_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return repr(value)
    if isinstance(value, str):
        escaped = value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
        return f'"{escaped}"'
    if isinstance(value, list):
        items = ", ".join(_toml_value(v) for v in value if not isinstance(v, dict))
        return f"[{items}]"
    return f'"{value}"'


def _write_section(data: dict, prefix: str = "") -> list[str]:
    lines = []
    scalars = {k: v for k, v in data.items() if not isinstance(v, dict)}
    tables = {k: v for k, v in data.items() if isinstance(v, dict)}
    for key, value in scalars.items():
        lines.append(f"{key} = {_toml_value(value)}")
    for key, value in tables.items():
        section = f"{prefix}.{key}" if prefix else key
        lines.append(f"\n[{section}]")
        lines.extend(_write_section(value, section))
    return lines


def to_string(data: dict) -> str:
    return "\n".join(_write_section(data)) + "\n"


def write_toml(path: str, data: dict, encoding: str = "utf-8") -> None:
    with open(path, "w", encoding=encoding) as f:
        f.write(to_string(data))


def get(data: dict, key: str, default: Any = None) -> Any:
    keys = key.split(".")
    current = data
    for k in keys:
        if not isinstance(current, dict) or k not in current:
            return default
        current = current[k]
    return current


def set_value(data: dict, key: str, value: Any) -> None:
    keys = key.split(".")
    current = data
    for k in keys[:-1]:
        current = current.setdefault(k, {})
    current[keys[-1]] = value


def has_key(data: dict, key: str) -> bool:
    sentinel = object()
    return get(data, key, sentinel) is not sentinel


def merge(base: dict, override: dict) -> dict:
    result = dict(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge(result[key], value)
        else:
            result[key] = value
    return result


def flatten_keys(data: dict, sep: str = ".", prefix: str = "") -> dict:
    result = {}
    for key, value in data.items():
        full_key = f"{prefix}{sep}{key}" if prefix else key
        if isinstance(value, dict):
            result.update(flatten_keys(value, sep=sep, prefix=full_key))
        else:
            result[full_key] = value
    return result


def keys_at(data: dict, section: str) -> list[str]:
    node = get(data, section)
    if not isinstance(node, dict):
        return []
    return list(node.keys())


if __name__ == "__main__":
    toml_text = """
[project]
name = "MyApp"
version = "1.2.3"
debug = false
tags = ["python", "util", "tools"]

[database]
host = "localhost"
port = 5432
name = "mydb"

[database.pool]
min = 2
max = 10
timeout = 30.0

[server]
host = "0.0.0.0"
port = 8080
"""

    data = parse_string(toml_text)

    print("get(project.name):       ", get(data, "project.name"))
    print("get(database.port):      ", get(data, "database.port"))
    print("get(database.pool.max):  ", get(data, "database.pool.max"))
    print("get(missing.key, 'N/A'): ", get(data, "missing.key", "N/A"))

    print("\nhas_key(database.host):  ", has_key(data, "database.host"))
    print("has_key(cache.ttl):      ", has_key(data, "cache.ttl"))

    print("\nkeys_at(database):       ", keys_at(data, "database"))

    set_value(data, "cache.ttl", 300)
    set_value(data, "cache.max_size", 1000)
    print("\nafter set_value, cache:  ", get(data, "cache"))

    print("\nflatten_keys:")
    flat = flatten_keys(data)
    for k, v in list(flat.items())[:8]:
        print(f"  {k:<30} = {v}")

    override = {"database": {"port": 5433}, "server": {"port": 9090}}
    merged = merge(data, override)
    print("\nafter merge:")
    print("  database.port:", get(merged, "database.port"))
    print("  server.port:  ", get(merged, "server.port"))

    print("\nto_string:")
    simple = {"app": {"name": "Test", "debug": True}, "port": 8000}
    print(to_string(simple))
