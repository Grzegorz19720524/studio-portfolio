import textwrap


def format_number(value: float, decimals: int = 2, sep: str = ",") -> str:
    formatted = f"{value:,.{decimals}f}"
    if sep != ",":
        formatted = formatted.replace(",", sep)
    return formatted


def format_currency(value: float, symbol: str = "$", decimals: int = 2) -> str:
    return f"{symbol}{format_number(value, decimals)}"


def format_percent(value: float, decimals: int = 1) -> str:
    return f"{value:.{decimals}f}%"


def format_filesize(num_bytes: int) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB", "PB"):
        if abs(num_bytes) < 1024:
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024
    return f"{num_bytes:.1f} EB"


def format_duration(seconds: float) -> str:
    seconds = int(seconds)
    parts = []
    for unit, size in (("h", 3600), ("m", 60), ("s", 1)):
        val, seconds = divmod(seconds, size)
        if val:
            parts.append(f"{val}{unit}")
    return " ".join(parts) if parts else "0s"


def format_ordinal(n: int) -> str:
    suffix = "th"
    if n % 100 not in (11, 12, 13):
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def format_list(items: list, sep: str = ", ", last_sep: str = " and ") -> str:
    if not items:
        return ""
    if len(items) == 1:
        return str(items[0])
    return sep.join(str(i) for i in items[:-1]) + last_sep + str(items[-1])


def format_table(rows: list[list], headers: list | None = None) -> str:
    all_rows = [headers] + rows if headers else rows
    col_widths = [max(len(str(row[i])) for row in all_rows) for i in range(len(all_rows[0]))]
    sep = "+" + "+".join("-" * (w + 2) for w in col_widths) + "+"

    def fmt_row(row):
        return "|" + "|".join(f" {str(cell):<{col_widths[i]}} " for i, cell in enumerate(row)) + "|"

    lines = [sep]
    if headers:
        lines += [fmt_row(headers), sep]
    for row in rows:
        lines.append(fmt_row(row))
    lines.append(sep)
    return "\n".join(lines)


def indent(text: str, spaces: int = 4) -> str:
    prefix = " " * spaces
    return "\n".join(prefix + line for line in text.splitlines())


def wrap(text: str, width: int = 80) -> str:
    return textwrap.fill(text, width=width)


if __name__ == "__main__":
    print("format_number(1234567.89):     ", format_number(1234567.89))
    print("format_currency(9.99):         ", format_currency(9.99))
    print("format_currency(1200, 'EUR'):  ", format_currency(1200, symbol="EUR"))
    print("format_percent(0.753 * 100):   ", format_percent(75.3))
    print()
    print("format_filesize(500):          ", format_filesize(500))
    print("format_filesize(2048):         ", format_filesize(2048))
    print("format_filesize(1_500_000):    ", format_filesize(1_500_000))
    print("format_filesize(3_000_000_000):", format_filesize(3_000_000_000))
    print()
    print("format_duration(0):            ", format_duration(0))
    print("format_duration(90):           ", format_duration(90))
    print("format_duration(3725):         ", format_duration(3725))
    print()
    print("format_ordinal(1):             ", format_ordinal(1))
    print("format_ordinal(2):             ", format_ordinal(2))
    print("format_ordinal(3):             ", format_ordinal(3))
    print("format_ordinal(11):            ", format_ordinal(11))
    print("format_ordinal(21):            ", format_ordinal(21))
    print()
    print("format_list([]):               ", format_list([]))
    print("format_list(['a']):            ", format_list(["a"]))
    print("format_list(['a','b','c']):    ", format_list(["a", "b", "c"]))
    print()
    headers = ["Name", "Age", "City"]
    rows = [["Alice", 30, "Warsaw"], ["Bob", 25, "Berlin"], ["Carol", 35, "Paris"]]
    print(format_table(rows, headers=headers))
    print()
    print("indent:")
    print(indent("line one\nline two\nline three", spaces=4))
    print()
    long_text = "This is a very long line of text that should be wrapped at a certain column width so it does not exceed the terminal width."
    print("wrap(text, 50):")
    print(wrap(long_text, width=50))
