import json
import csv
import io
from datetime import date, datetime
from typing import Any


class JSONEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        if hasattr(obj, "__dict__"):
            return obj.__dict__
        return super().default(obj)


def to_json(data: Any, indent: int | None = None) -> str:
    return json.dumps(data, cls=JSONEncoder, ensure_ascii=False, indent=indent)


def from_json(text: str) -> Any:
    return json.loads(text)


def to_csv(records: list[dict], fields: list[str] | None = None) -> str:
    if not records:
        return ""
    fields = fields or list(records[0].keys())
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fields, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(records)
    return buf.getvalue()


def from_csv(text: str) -> list[dict]:
    reader = csv.DictReader(io.StringIO(text))
    return list(reader)


def to_flat(data: dict, sep: str = ".", prefix: str = "") -> dict:
    result = {}
    for key, value in data.items():
        full_key = f"{prefix}{sep}{key}" if prefix else key
        if isinstance(value, dict):
            result.update(to_flat(value, sep=sep, prefix=full_key))
        else:
            result[full_key] = value
    return result


def from_flat(data: dict, sep: str = ".") -> dict:
    result: dict = {}
    for key, value in data.items():
        parts = key.split(sep)
        node = result
        for part in parts[:-1]:
            node = node.setdefault(part, {})
        node[parts[-1]] = value
    return result


def pick(data: dict, keys: list[str]) -> dict:
    return {k: data[k] for k in keys if k in data}


def omit(data: dict, keys: list[str]) -> dict:
    return {k: v for k, v in data.items() if k not in keys}


if __name__ == "__main__":
    data = {"name": "Claude", "born": date(2023, 3, 14), "score": 99.5}
    print("to_json:  ", to_json(data))
    print("indented:\n", to_json(data, indent=2))

    records = [
        {"id": 1, "name": "Alice", "role": "admin"},
        {"id": 2, "name": "Bob", "role": "user"},
    ]
    csv_str = to_csv(records)
    print("\nto_csv:\n", csv_str)
    print("from_csv:", from_csv(csv_str))

    nested = {"user": {"name": "Alice", "address": {"city": "Berlin", "zip": "10115"}}}
    flat = to_flat(nested)
    print("\nto_flat: ", flat)
    print("from_flat:", from_flat(flat))

    print("\npick:    ", pick(records[0], ["id", "name"]))
    print("omit:    ", omit(records[0], ["role"]))
