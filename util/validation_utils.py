import re
from typing import Any, Callable


class ValidationError(Exception):
    def __init__(self, message: str, field: str | None = None):
        self.field = field
        self.message = message
        super().__init__(f"{field}: {message}" if field else message)


class ValidationResult:
    def __init__(self):
        self.errors: dict[str, list[str]] = {}

    def add(self, field: str, message: str) -> None:
        self.errors.setdefault(field, []).append(message)

    @property
    def is_valid(self) -> bool:
        return not self.errors

    def raise_if_invalid(self) -> None:
        if not self.is_valid:
            msgs = "; ".join(f"{f}: {', '.join(e)}" for f, e in self.errors.items())
            raise ValidationError(msgs)

    def __repr__(self) -> str:
        return f"ValidationResult(valid={self.is_valid}, errors={self.errors})"


def _check_field(value: Any, rules: dict, field: str, result: ValidationResult) -> None:
    required = rules.get("required", True)
    if value is None or value == "":
        if required:
            default = rules.get("default")
            if default is None:
                result.add(field, "field is required")
        return

    expected_type = rules.get("type")
    if expected_type is not None:
        types = expected_type if isinstance(expected_type, (list, tuple)) else (expected_type,)
        if not isinstance(value, tuple(types)):
            names = " or ".join(t.__name__ for t in types)
            result.add(field, f"expected {names}, got {type(value).__name__}")
            return

    if "min" in rules and value < rules["min"]:
        result.add(field, f"must be >= {rules['min']}")
    if "max" in rules and value > rules["max"]:
        result.add(field, f"must be <= {rules['max']}")

    if "min_length" in rules and len(value) < rules["min_length"]:
        result.add(field, f"length must be >= {rules['min_length']}")
    if "max_length" in rules and len(value) > rules["max_length"]:
        result.add(field, f"length must be <= {rules['max_length']}")

    if "pattern" in rules and isinstance(value, str):
        if not re.fullmatch(rules["pattern"], value):
            result.add(field, f"does not match pattern {rules['pattern']!r}")

    if "choices" in rules and value not in rules["choices"]:
        result.add(field, f"must be one of {rules['choices']}")

    if "validator" in rules:
        ok, msg = rules["validator"](value)
        if not ok:
            result.add(field, msg)


def validate(data: dict, schema: dict) -> ValidationResult:
    result = ValidationResult()
    for field, rules in schema.items():
        value = data.get(field)
        _check_field(value, rules, field, result)
    return result


def validate_type(value: Any, expected: type | tuple) -> bool:
    return isinstance(value, expected)


def validate_range(value: float, min_val: float | None = None,
                   max_val: float | None = None) -> bool:
    if min_val is not None and value < min_val:
        return False
    if max_val is not None and value > max_val:
        return False
    return True


def validate_length(value, min_len: int | None = None,
                    max_len: int | None = None) -> bool:
    n = len(value)
    if min_len is not None and n < min_len:
        return False
    if max_len is not None and n > max_len:
        return False
    return True


def validate_pattern(value: str, pattern: str) -> bool:
    return bool(re.fullmatch(pattern, value))


def validate_choices(value: Any, choices: list) -> bool:
    return value in choices


def validate_required(data: dict, fields: list[str]) -> list[str]:
    return [f for f in fields if data.get(f) is None or data.get(f) == ""]


class Validator:
    def __init__(self, value: Any, field: str = "value"):
        self._value = value
        self._field = field
        self._errors: list[str] = []

    def required(self) -> "Validator":
        if self._value is None or self._value == "":
            self._errors.append("is required")
        return self

    def type(self, expected: type | tuple) -> "Validator":
        if self._value is not None and not isinstance(self._value, expected):
            names = expected.__name__ if isinstance(expected, type) else \
                    " or ".join(t.__name__ for t in expected)
            self._errors.append(f"must be {names}")
        return self

    def min(self, n: float) -> "Validator":
        if self._value is not None and self._value < n:
            self._errors.append(f"must be >= {n}")
        return self

    def max(self, n: float) -> "Validator":
        if self._value is not None and self._value > n:
            self._errors.append(f"must be <= {n}")
        return self

    def min_length(self, n: int) -> "Validator":
        if self._value is not None and len(self._value) < n:
            self._errors.append(f"length must be >= {n}")
        return self

    def max_length(self, n: int) -> "Validator":
        if self._value is not None and len(self._value) > n:
            self._errors.append(f"length must be <= {n}")
        return self

    def pattern(self, regex: str) -> "Validator":
        if self._value is not None and not re.fullmatch(regex, str(self._value)):
            self._errors.append(f"does not match pattern {regex!r}")
        return self

    def choices(self, options: list) -> "Validator":
        if self._value is not None and self._value not in options:
            self._errors.append(f"must be one of {options}")
        return self

    def custom(self, fn: Callable[[Any], tuple[bool, str]]) -> "Validator":
        if self._value is not None:
            ok, msg = fn(self._value)
            if not ok:
                self._errors.append(msg)
        return self

    @property
    def is_valid(self) -> bool:
        return not self._errors

    @property
    def errors(self) -> list[str]:
        return self._errors

    def raise_if_invalid(self) -> None:
        if self._errors:
            raise ValidationError(", ".join(self._errors), self._field)


if __name__ == "__main__":
    print("--- validate() with schema ---")
    schema = {
        "name":  {"type": str, "min_length": 2, "max_length": 50},
        "age":   {"type": int, "min": 0, "max": 150},
        "email": {"type": str, "pattern": r"[^@]+@[^@]+\.[^@]+"},
        "role":  {"type": str, "choices": ["admin", "user", "guest"]},
        "score": {"type": float, "required": False, "min": 0.0, "max": 100.0},
    }

    good = {"name": "Alice", "age": 30, "email": "alice@example.com", "role": "admin"}
    result = validate(good, schema)
    print("valid data:  ", result)

    bad = {"name": "A", "age": 200, "email": "not-an-email", "role": "superuser"}
    result2 = validate(bad, schema)
    print("invalid data:", result2)
    for field, errs in result2.errors.items():
        print(f"  {field}: {errs}")

    print("\n--- Validator chain ---")
    v = Validator("hello@world.com", "email") \
        .required() \
        .type(str) \
        .min_length(5) \
        .pattern(r"[^@]+@[^@]+\.[^@]+")
    print("email valid:", v.is_valid)

    v2 = Validator(17, "age").required().type(int).min(18).max(99)
    print("age valid:  ", v2.is_valid, "| errors:", v2.errors)

    print("\n--- helper functions ---")
    print("validate_type(42, int):          ", validate_type(42, int))
    print("validate_range(50, 0, 100):      ", validate_range(50, 0, 100))
    print("validate_range(150, 0, 100):     ", validate_range(150, 0, 100))
    print("validate_length('hi', 3, 10):   ", validate_length("hi", 3, 10))
    print("validate_pattern('abc123', r'\\w+'):", validate_pattern("abc123", r"\w+"))
    print("validate_choices('red', ['red','green','blue']):", validate_choices("red", ["red", "green", "blue"]))
    print("validate_required({'a':1,'b':None}, ['a','b']):", validate_required({"a": 1, "b": None}, ["a", "b"]))

    print("\n--- custom validator ---")
    def even_check(v):
        return (True, "") if v % 2 == 0 else (False, "must be even")

    v3 = Validator(7, "number").custom(even_check)
    print("7 is even:", v3.is_valid, "| errors:", v3.errors)
