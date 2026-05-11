from datetime import datetime, timedelta, date


def now(fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    return datetime.now().strftime(fmt)


def today() -> date:
    return date.today()


def parse_date(value: str, fmt: str = "%Y-%m-%d") -> date:
    return datetime.strptime(value, fmt).date()


def format_date(d: date, fmt: str = "%Y-%m-%d") -> str:
    return d.strftime(fmt)


def days_between(start: date, end: date) -> int:
    return (end - start).days


def add_days(d: date, days: int) -> date:
    return d + timedelta(days=days)


def is_past(d: date) -> bool:
    return d < date.today()


def is_future(d: date) -> bool:
    return d > date.today()


def start_of_week(d: date) -> date:
    return d - timedelta(days=d.weekday())


def end_of_week(d: date) -> date:
    return start_of_week(d) + timedelta(days=6)


if __name__ == "__main__":
    print("now:          ", now())
    print("today:        ", today())

    d = parse_date("2026-01-01")
    print("parsed:       ", d)
    print("formatted:    ", format_date(d, "%d %B %Y"))
    print("days since:   ", days_between(d, today()))
    print("add 10 days:  ", add_days(d, 10))
    print("is past:      ", is_past(d))
    print("is future:    ", is_future(d))
    print("start of week:", start_of_week(today()))
    print("end of week:  ", end_of_week(today()))
