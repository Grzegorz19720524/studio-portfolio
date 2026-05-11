import math
from typing import Any


class Page:
    def __init__(self, items: list, page: int, page_size: int, total: int):
        self.items = items
        self.page = page
        self.page_size = page_size
        self.total = total
        self.total_pages = math.ceil(total / page_size) if page_size else 0

    @property
    def has_next(self) -> bool:
        return self.page < self.total_pages

    @property
    def has_prev(self) -> bool:
        return self.page > 1

    @property
    def next_page(self) -> int | None:
        return self.page + 1 if self.has_next else None

    @property
    def prev_page(self) -> int | None:
        return self.page - 1 if self.has_prev else None

    def to_dict(self) -> dict:
        return {
            "items": self.items,
            "page": self.page,
            "page_size": self.page_size,
            "total": self.total,
            "total_pages": self.total_pages,
            "has_next": self.has_next,
            "has_prev": self.has_prev,
            "next_page": self.next_page,
            "prev_page": self.prev_page,
        }

    def __repr__(self) -> str:
        return f"Page(page={self.page}/{self.total_pages}, items={len(self.items)}, total={self.total})"


def paginate(items: list[Any], page: int = 1, page_size: int = 10) -> Page:
    page = max(1, page)
    page_size = max(1, page_size)
    total = len(items)
    start = (page - 1) * page_size
    end = start + page_size
    return Page(items[start:end], page, page_size, total)


def page_range(total_pages: int, current: int, window: int = 2) -> list[int | str]:
    if total_pages <= 1:
        return [1]
    pages = set()
    pages.update(range(1, min(3, total_pages + 1)))
    pages.update(range(max(1, current - window), min(total_pages + 1, current + window + 1)))
    pages.update(range(max(1, total_pages - 1), total_pages + 1))
    result: list[int | str] = []
    for p in sorted(pages):
        if result and isinstance(result[-1], int) and p - result[-1] > 1:
            result.append("...")
        result.append(p)
    return result


if __name__ == "__main__":
    data = list(range(1, 48))

    page = paginate(data, page=1, page_size=10)
    print(page)
    print("items:     ", page.items)
    print("has_next:  ", page.has_next)
    print("has_prev:  ", page.has_prev)
    print("next_page: ", page.next_page)

    page3 = paginate(data, page=3, page_size=10)
    print("\n", page3)
    print("prev_page: ", page3.prev_page)

    last = paginate(data, page=5, page_size=10)
    print("\n", last)
    print("items:     ", last.items)

    print("\npage_range:", page_range(total_pages=10, current=5))
