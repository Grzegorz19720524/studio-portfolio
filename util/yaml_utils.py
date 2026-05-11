from pathlib import Path
from typing import Any


def _parse_scalar(s: str) -> Any:
    s = s.strip()
    if s in ("null", "Null", "NULL", "~"):
        return None
    if s in ("true", "True", "TRUE", "yes", "Yes", "YES"):
        return True
    if s in ("false", "False", "FALSE", "no", "No", "NO"):
        return False
    try:
        return int(s)
    except ValueError:
        pass
    try:
        return float(s)
    except ValueError:
        pass
    if s.startswith('"') and s.endswith('"'):
        return s[1:-1].replace('\\"', '"').replace("\\n", "\n")
    if s.startswith("'") and s.endswith("'"):
        return s[1:-1]
    return s


class _Parser:
    def __init__(self, text: str):
        self.lines = text.splitlines()
        self.pos = 0

    def _skip_empty(self) -> None:
        while self.pos < len(self.lines):
            s = self.lines[self.pos].strip()
            if s and not s.startswith("#"):
                break
            self.pos += 1

    def _indent(self) -> int:
        if self.pos >= len(self.lines):
            return -1
        line = self.lines[self.pos]
        return len(line) - len(line.lstrip())

    def parse(self) -> Any:
        self._skip_empty()
        if self.pos >= len(self.lines):
            return {}
        if self.lines[self.pos].lstrip().startswith("- "):
            return self._parse_list(self._indent())
        return self._parse_dict(self._indent())

    def _parse_dict(self, base: int) -> dict:
        result = {}
        while self.pos < len(self.lines):
            self._skip_empty()
            if self.pos >= len(self.lines):
                break
            line = self.lines[self.pos]
            indent = len(line) - len(line.lstrip())
            if indent < base:
                break
            stripped = line.lstrip()
            if stripped.startswith("- "):
                break
            if ":" not in stripped:
                self.pos += 1
                continue
            colon = stripped.index(":")
            key = stripped[:colon].strip()
            rest = stripped[colon + 1:].strip()
            self.pos += 1
            if rest and not rest.startswith("#"):
                result[key] = _parse_scalar(rest)
            else:
                self._skip_empty()
                if self.pos < len(self.lines):
                    ni = self._indent()
                    ns = self.lines[self.pos].lstrip()
                    if ni > indent:
                        result[key] = self._parse_list(ni) if ns.startswith("- ") else self._parse_dict(ni)
                    else:
                        result[key] = None
                else:
                    result[key] = None
        return result

    def _parse_list(self, base: int) -> list:
        result = []
        while self.pos < len(self.lines):
            self._skip_empty()
            if self.pos >= len(self.lines):
                break
            line = self.lines[self.pos]
            indent = len(line) - len(line.lstrip())
            if indent < base:
                break
            stripped = line.lstrip()
            if not stripped.startswith("- "):
                break
            item_text = stripped[2:].strip()
            self.pos += 1
            if item_text:
                result.append(_parse_scalar(item_text))
            else:
                self._skip_empty()
                if self.pos < len(self.lines):
                    ni = self._indent()
                    ns = self.lines[self.pos].lstrip()
                    result.append(self._parse_list(ni) if ns.startswith("- ") else self._parse_dict(ni))
        return result


def _needs_quotes(s: str) -> bool:
    if not s:
        return True
    specials = set(':#{}[]|>&*!,\n\t')
    if any(c in s for c in specials) or s[0] in ' \'"':
        return True
    if _parse_scalar(s) != s:
        return True
    return False


def _dump(value: Any, level: int = 0) -> str:
    indent = "  " * level
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return repr(value)
    if isinstance(value, str):
        if _needs_quotes(value):
            escaped = value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
            return f'"{escaped}"'
        return value
    if isinstance(value, list):
        if not value:
            return "[]"
        lines = []
        for item in value:
            if isinstance(item, dict) and item:
                inner_lines = _dump(item, level + 1).splitlines()
                lines.append(f"{indent}- {inner_lines[0].lstrip()}")
                for il in inner_lines[1:]:
                    lines.append(il)
            elif isinstance(item, list):
                lines.append(f"{indent}-")
                lines.append(_dump(item, level + 1))
            else:
                lines.append(f"{indent}- {_dump(item)}")
        return "\n".join(lines)
    if isinstance(value, dict):
        if not value:
            return "{}"
        lines = []
        for k, v in value.items():
            if isinstance(v, dict) and v:
                lines.append(f"{indent}{k}:")
                lines.append(_dump(v, level + 1))
            elif isinstance(v, list) and v:
                lines.append(f"{indent}{k}:")
                lines.append(_dump(v, level + 1))
            else:
                lines.append(f"{indent}{k}: {_dump(v)}")
        return "\n".join(lines)
    return str(value)


def parse_string(text: str) -> Any:
    return _Parser(text).parse()


def read_yaml(path: str, encoding: str = "utf-8") -> Any:
    return parse_string(Path(path).read_text(encoding=encoding))


def to_string(data: Any) -> str:
    return _dump(data) + "\n"


def write_yaml(path: str, data: Any, encoding: str = "utf-8") -> None:
    Path(path).write_text(to_string(data), encoding=encoding)


def get(data: dict, key: str, default: Any = None) -> Any:
    current = data
    for k in key.split("."):
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


def merge(base: dict, override: dict) -> dict:
    result = dict(base)
    for k, v in override.items():
        if k in result and isinstance(result[k], dict) and isinstance(v, dict):
            result[k] = merge(result[k], v)
        else:
            result[k] = v
    return result


if __name__ == "__main__":
    yaml_text = """\
project:
  name: MyApp
  version: 1.0.0
  debug: false

database:
  host: localhost
  port: 5432
  name: mydb
  pool:
    min: 2
    max: 10

tags:
  - python
  - yaml
  - utils

features:
  - name: auth
    enabled: true
  - name: cache
    enabled: false
"""

    data = parse_string(yaml_text)

    print("get(project.name):      ", get(data, "project.name"))
    print("get(database.port):     ", get(data, "database.port"))
    print("get(database.pool.max): ", get(data, "database.pool.max"))
    print("get(missing, 'N/A'):    ", get(data, "missing.key", "N/A"))
    print("tags:                   ", data.get("tags"))
    print()

    set_value(data, "cache.ttl", 300)
    print("after set_value, cache: ", get(data, "cache"))

    override = {"database": {"port": 5433}, "project": {"debug": True}}
    merged = merge(data, override)
    print("after merge, db.port:   ", get(merged, "database.port"))
    print("after merge, debug:     ", get(merged, "project.debug"))

    print("\nto_string (simple):")
    simple = {
        "app": {"name": "Test", "debug": True, "port": 8080},
        "items": [1, 2, 3],
    }
    print(to_string(simple))

    print("round-trip parse:")
    parsed = parse_string(to_string(simple))
    print("  app.name:", get(parsed, "app.name"))
    print("  app.port:", get(parsed, "app.port"))
    print("  items:   ", parsed.get("items"))
