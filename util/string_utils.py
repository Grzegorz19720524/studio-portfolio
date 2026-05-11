import re


def camel_to_snake(text: str) -> str:
    text = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", text)
    return re.sub(r"([a-z\d])([A-Z])", r"\1_\2", text).lower()


def snake_to_camel(text: str) -> str:
    parts = text.split("_")
    return parts[0] + "".join(p.capitalize() for p in parts[1:])


def snake_to_pascal(text: str) -> str:
    return "".join(p.capitalize() for p in text.split("_"))


def capitalize_words(text: str) -> str:
    return text.title()


def remove_whitespace(text: str) -> str:
    return re.sub(r"\s+", "", text)


def count_words(text: str) -> int:
    return len(text.split())


def reverse(text: str) -> str:
    return text[::-1]


def is_palindrome(text: str) -> bool:
    clean = re.sub(r"[^a-z0-9]", "", text.lower())
    return clean == clean[::-1]


def pad_left(text: str, width: int, char: str = " ") -> str:
    return text.rjust(width, char)


def pad_right(text: str, width: int, char: str = " ") -> str:
    return text.ljust(width, char)


if __name__ == "__main__":
    print(camel_to_snake("myVariableName"))
    print(snake_to_camel("my_variable_name"))
    print(snake_to_pascal("my_variable_name"))
    print(capitalize_words("hello world from poland"))
    print(remove_whitespace("h e l l o"))
    print(count_words("the quick brown fox"))
    print(reverse("Claude"))
    print(is_palindrome("A man a plan a canal Panama"))
    print(is_palindrome("hello"))
    print(pad_left("42", 6, "0"))
    print(pad_right("hi", 10, "-"))
