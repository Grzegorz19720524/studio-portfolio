import re


def is_email(value: str) -> bool:
    pattern = r"^[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, value))


def is_url(value: str) -> bool:
    pattern = r"^https?://[\w.-]+(?:\.[\w.-]+)+[\w\-._~:/?#[\]@!$&'()*+,;=%]*$"
    return bool(re.match(pattern, value))


def is_phone(value: str) -> bool:
    pattern = r"^\+?[\d\s\-().]{7,20}$"
    return bool(re.match(pattern, value.strip()))


def is_non_empty(value: str) -> bool:
    return bool(value and value.strip())


def is_in_range(value: int | float, min_val: int | float, max_val: int | float) -> bool:
    return min_val <= value <= max_val


def is_min_length(value: str, min_length: int) -> bool:
    return len(value) >= min_length


if __name__ == "__main__":
    print(is_email("user@example.com"))       # True
    print(is_email("not-an-email"))            # False

    print(is_url("https://example.com/path")) # True
    print(is_url("ftp://bad.com"))            # False

    print(is_phone("+48 123 456 789"))        # True
    print(is_phone("abc"))                    # False

    print(is_non_empty("  hello  "))          # True
    print(is_non_empty("   "))                # False

    print(is_in_range(5, 1, 10))              # True
    print(is_in_range(15, 1, 10))             # False

    print(is_min_length("hello", 3))          # True
    print(is_min_length("hi", 5))             # False
