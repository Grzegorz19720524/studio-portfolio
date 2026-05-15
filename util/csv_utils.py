import csv
import io
from typing import Callable, Any


def read_csv(path: str, delimiter: str = ",", encoding: str = "utf-8") -> list[dict]:
    with open(path, newline="", encoding=encoding) as f:
        return list(csv.DictReader(f, delimiter=delimiter))


def write_csv(path: str, rows: list[dict], fieldnames: list[str] | None = None,
              delimiter: str = ",", encoding: str = "utf-8") -> None:
    if not rows:
        return
    fields = fieldnames or list(rows[0].keys())
    with open(path, "w", newline="", encoding=encoding) as f:
        writer = csv.DictWriter(f, fieldnames=fields, delimiter=delimiter)
        writer.writeheader()
        writer.writerows(rows)


def read_csv_rows(path: str, delimiter: str = ",", encoding: str = "utf-8") -> list[list[str]]:
    with open(path, newline="", encoding=encoding) as f:
        return list(csv.reader(f, delimiter=delimiter))


def write_csv_rows(path: str, rows: list[list], delimiter: str = ",",
                   encoding: str = "utf-8") -> None:
    with open(path, "w", newline="", encoding=encoding) as f:
        csv.writer(f, delimiter=delimiter).writerows(rows)


def append_row(path: str, row: list | dict, encoding: str = "utf-8") -> None:
    with open(path, "a", newline="", encoding=encoding) as f:
        if isinstance(row, dict):
            writer = csv.DictWriter(f, fieldnames=list(row.keys()))
            writer.writerow(row)
        else:
            csv.writer(f).writerow(row)


def csv_to_string(rows: list[dict], fieldnames: list[str] | None = None,
                  delimiter: str = ",") -> str:
    if not rows:
        return ""
    fields = fieldnames or list(rows[0].keys())
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fields, delimiter=delimiter)
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue()


def string_to_csv(text: str, delimiter: str = ",") -> list[dict]:
    return list(csv.DictReader(io.StringIO(text), delimiter=delimiter))


def get_headers(path: str, delimiter: str = ",", encoding: str = "utf-8") -> list[str]:
    with open(path, newline="", encoding=encoding) as f:
        reader = csv.reader(f, delimiter=delimiter)
        return next(reader, [])


def count_rows(path: str, encoding: str = "utf-8") -> int:
    with open(path, newline="", encoding=encoding) as f:
        return sum(1 for _ in f) - 1


def col_values(rows: list[dict], col: str) -> list[Any]:
    return [row[col] for row in rows if col in row]


def select_cols(rows: list[dict], cols: list[str]) -> list[dict]:
    return [{k: row[k] for k in cols if k in row} for row in rows]


def filter_rows(rows: list[dict], pred: Callable[[dict], bool]) -> list[dict]:
    return [row for row in rows if pred(row)]


def sort_rows(rows: list[dict], key: str, reverse: bool = False) -> list[dict]:
    return sorted(rows, key=lambda r: r.get(key, ""), reverse=reverse)


def transform_col(rows: list[dict], col: str, fn: Callable) -> list[dict]:
    return [{**row, col: fn(row[col])} if col in row else row for row in rows]


def rename_col(rows: list[dict], old: str, new: str) -> list[dict]:
    result = []
    for row in rows:
        r = {new if k == old else k: v for k, v in row.items()}
        result.append(r)
    return result


def drop_col(rows: list[dict], col: str) -> list[dict]:
    return [{k: v for k, v in row.items() if k != col} for row in rows]


def deduplicate(rows: list[dict], key: str) -> list[dict]:
    seen = set()
    result = []
    for row in rows:
        val = row.get(key)
        if val not in seen:
            seen.add(val)
            result.append(row)
    return result


if __name__ == "__main__":
    import tempfile
    import os

    data = [
        {"name": "Alice", "age": "30", "city": "Warsaw"},
        {"name": "Bob",   "age": "25", "city": "Berlin"},
        {"name": "Carol", "age": "35", "city": "Paris"},
        {"name": "Dave",  "age": "25", "city": "Warsaw"},
        {"name": "Eve",   "age": "28", "city": "Berlin"},
    ]

    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, encoding="utf-8") as f:
        tmp = f.name

    write_csv(tmp, data)
    print("write_csv + read_csv:")
    for row in read_csv(tmp):
        print(" ", row)

    print("\nget_headers:   ", get_headers(tmp))
    print("count_rows:    ", count_rows(tmp))
    print("col_values(age):", col_values(data, "age"))

    print("\nselect_cols(['name','city']):")
    for row in select_cols(data, ["name", "city"]):
        print(" ", row)

    print("\nfilter_rows(age=='25'):")
    for row in filter_rows(data, lambda r: r["age"] == "25"):
        print(" ", row)

    print("\nsort_rows(by name):")
    for row in sort_rows(data, "name"):
        print(" ", row)

    print("\ntransform_col(age, int+1):")
    transformed = transform_col(data, "age", lambda x: int(x) + 1)
    print(" ", col_values(transformed, "age"))

    print("\nrename_col(city->location):")
    renamed = rename_col(data, "city", "location")
    print(" ", list(renamed[0].keys()))

    print("\ndrop_col(age):")
    dropped = drop_col(data, "age")
    print(" ", list(dropped[0].keys()))

    print("\ndeduplicate(by age):")
    deduped = deduplicate(data, "age")
    print(" ", col_values(deduped, "name"))

    print("\ncsv_to_string (first 2 rows):")
    print(csv_to_string(data[:2]))

    print("string_to_csv round-trip:")
    s = csv_to_string(data[:2])
    print(" ", string_to_csv(s))

    os.unlink(tmp)
