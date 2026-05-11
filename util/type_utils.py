from typing import Any, Type, TypeVar

T = TypeVar("T")


def is_type(value: Any, *types: Type) -> bool:
    return isinstance(value, types)


def is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def is_float(value: Any) -> bool:
    return isinstance(value, float)


def is_numeric(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def is_string(value: Any) -> bool:
    return isinstance(value, str)


def is_bool(value: Any) -> bool:
    return isinstance(value, bool)


def is_list(value: Any) -> bool:
    return isinstance(value, list)


def is_dict(value: Any) -> bool:
    return isinstance(value, dict)


def is_none(value: Any) -> bool:
    return value is None


def safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def safe_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in ("1", "true", "yes", "on")
    return bool(value)


def safe_cast(value: Any, target: Type[T], default: T | None = None) -> T | None:
    try:
        return target(value)
    except (ValueError, TypeError):
        return default


def coerce(value: Any) -> Any:
    if isinstance(value, str):
        if value.lower() in ("true", "yes"):
            return True
        if value.lower() in ("false", "no"):
            return False
        if value.lower() in ("none", "null", ""):
            return None
        try:
            return int(value)
        except ValueError:
            pass
        try:
            return float(value)
        except ValueError:
            pass
    return value


def type_name(value: Any) -> str:
    return type(value).__name__


if __name__ == "__main__":
    print("is_int(42):       ", is_int(42))
    print("is_int(True):     ", is_int(True))
    print("is_float(3.14):   ", is_float(3.14))
    print("is_numeric(42):   ", is_numeric(42))
    print("is_string('hi'):  ", is_string("hi"))
    print("is_bool(False):   ", is_bool(False))
    print("is_list([]):      ", is_list([]))
    print("is_dict({}):      ", is_dict({}))
    print("is_none(None):    ", is_none(None))

    print("\nsafe_int('42'):   ", safe_int("42"))
    print("safe_int('oops'): ", safe_int("oops", default=-1))
    print("safe_float('3.5'):", safe_float("3.5"))
    print("safe_bool('yes'): ", safe_bool("yes"))
    print("safe_cast('7',int):", safe_cast("7", int))

    print("\ncoerce('true'):   ", coerce("true"))
    print("coerce('42'):     ", coerce("42"))
    print("coerce('3.14'):   ", coerce("3.14"))
    print("coerce('null'):   ", coerce("null"))
    print("coerce('hello'):  ", coerce("hello"))

    print("\ntype_name(42):    ", type_name(42))
    print("type_name([]):    ", type_name([]))
