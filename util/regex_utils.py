import re
from typing import Callable

EMAIL_PATTERN = r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}"
URL_PATTERN = r"https?://[^\s\"\']+"
IP_PATTERN = r"\b(?:\d{1,3}\.){3}\d{1,3}\b"
IPV6_PATTERN = r"\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b"
DATE_PATTERN = r"\b\d{4}-\d{2}-\d{2}\b"
TIME_PATTERN = r"\b\d{2}:\d{2}(?::\d{2})?\b"
PHONE_PATTERN = r"\+?[\d\s\-().]{7,20}"
SLUG_PATTERN = r"^[a-z0-9]+(?:-[a-z0-9]+)*$"
HEX_COLOR_PATTERN = r"#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})\b"
INTEGER_PATTERN = r"-?\b\d+\b"
FLOAT_PATTERN = r"-?\b\d+\.\d+\b"
WORD_PATTERN = r"\b[a-zA-Z]+\b"
WHITESPACE_PATTERN = r"\s+"
HTML_TAG_PATTERN = r"<[^>]+>"


def is_match(pattern: str, text: str, flags: int = 0) -> bool:
    return bool(re.fullmatch(pattern, text, flags))


def match(pattern: str, text: str, flags: int = 0) -> re.Match | None:
    return re.match(pattern, text, flags)


def search(pattern: str, text: str, flags: int = 0) -> re.Match | None:
    return re.search(pattern, text, flags)


def find_all(pattern: str, text: str, flags: int = 0) -> list[str]:
    return re.findall(pattern, text, flags)


def find_all_groups(pattern: str, text: str, flags: int = 0) -> list[tuple]:
    return [m.groups() for m in re.finditer(pattern, text, flags)]


def extract(pattern: str, text: str, group: int = 1, flags: int = 0) -> str | None:
    m = re.search(pattern, text, flags)
    if m:
        return m.group(group) if m.lastindex and m.lastindex >= group else m.group(0)
    return None


def extract_all(pattern: str, text: str, group: int = 1, flags: int = 0) -> list[str]:
    return [
        m.group(group) if m.lastindex and m.lastindex >= group else m.group(0)
        for m in re.finditer(pattern, text, flags)
    ]


def named_groups(pattern: str, text: str, flags: int = 0) -> dict[str, str] | None:
    m = re.search(pattern, text, flags)
    return m.groupdict() if m else None


def replace(pattern: str, replacement: str, text: str, count: int = 0, flags: int = 0) -> str:
    return re.sub(pattern, replacement, text, count=count, flags=flags)


def replace_fn(pattern: str, fn: Callable[[re.Match], str], text: str, flags: int = 0) -> str:
    return re.sub(pattern, fn, text, flags=flags)


def split(pattern: str, text: str, maxsplit: int = 0, flags: int = 0) -> list[str]:
    return re.split(pattern, text, maxsplit=maxsplit, flags=flags)


def escape(text: str) -> str:
    return re.escape(text)


def compile(pattern: str, flags: int = 0) -> re.Pattern:
    return re.compile(pattern, flags)


def strip_html(text: str) -> str:
    return re.sub(HTML_TAG_PATTERN, "", text)


def normalize_whitespace(text: str) -> str:
    return re.sub(WHITESPACE_PATTERN, " ", text).strip()


if __name__ == "__main__":
    text = "Contact us at hello@example.com or support@test.org for help."
    print("find_all emails:  ", find_all(EMAIL_PATTERN, text))

    text2 = "Visit https://example.com or http://test.org/page for more info."
    print("find_all urls:    ", find_all(URL_PATTERN, text2))

    text3 = "Server IPs: 192.168.1.1 and 10.0.0.255"
    print("find_all IPs:     ", find_all(IP_PATTERN, text3))

    text4 = "Dates: 2024-01-15 and 2025-12-31"
    print("find_all dates:   ", find_all(DATE_PATTERN, text4))

    text5 = "Colors: #fff, #3498db, #FF0000"
    print("find_all colors:  ", find_all(HEX_COLOR_PATTERN, text5))

    print("\nis_match slug 'hello-world':", is_match(SLUG_PATTERN, "hello-world"))
    print("is_match slug 'Hello World':", is_match(SLUG_PATTERN, "Hello World"))

    print("\nreplace digits:   ", replace(r"\d+", "NUM", "foo 123 bar 456"))
    print("replace_fn upper: ", replace_fn(r"\b[a-z]+\b", lambda m: m.group().upper(), "hello world"))

    print("\nsplit by comma:   ", split(r"\s*,\s*", "a, b,c ,  d"))

    print("\nnamed_groups:")
    pattern = r"(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})"
    print("  ", named_groups(pattern, "Today is 2025-05-11"))

    html = "<h1>Hello <b>World</b></h1>"
    print("\nstrip_html:       ", strip_html(html))

    messy = "  too   many    spaces  "
    print("normalize_ws:     ", normalize_whitespace(messy))

    print("\nescape('1+1=2?'): ", escape("1+1=2?"))
