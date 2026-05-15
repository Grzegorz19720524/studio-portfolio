import re


def filter_by(items: list[dict], **filters) -> list[dict]:
    result = items
    for key, value in filters.items():
        result = [item for item in result if item.get(key) == value]
    return result


def search_by_key(items: list[dict], key: str, query: str, case_sensitive: bool = False) -> list[dict]:
    if not case_sensitive:
        query = query.lower()
        return [item for item in items if query in str(item.get(key, "")).lower()]
    return [item for item in items if query in str(item.get(key, ""))]


def sort_by(items: list[dict], key: str, reverse: bool = False) -> list[dict]:
    return sorted(items, key=lambda x: x.get(key) or "", reverse=reverse)


def fuzzy_match(text: str, pattern: str, case_sensitive: bool = False) -> bool:
    if not case_sensitive:
        text, pattern = text.lower(), pattern.lower()
    it = iter(text)
    return all(char in it for char in pattern)


def fuzzy_search(items: list[dict], key: str, pattern: str) -> list[dict]:
    return [item for item in items if fuzzy_match(str(item.get(key, "")), pattern)]


def highlight(text: str, query: str, tag: str = "**") -> str:
    if not query:
        return text
    pattern = re.compile(re.escape(query), re.IGNORECASE)
    return pattern.sub(lambda m: f"{tag}{m.group()}{tag}", text)


def multi_search(items: list[dict], keys: list[str], query: str) -> list[dict]:
    query = query.lower()
    return [
        item for item in items
        if any(query in str(item.get(k, "")).lower() for k in keys)
    ]


if __name__ == "__main__":
    products = [
        {"id": 1, "name": "Laptop Pro", "category": "electronics", "price": 2999},
        {"id": 2, "name": "Wireless Mouse", "category": "electronics", "price": 149},
        {"id": 3, "name": "Standing Desk", "category": "furniture", "price": 1200},
        {"id": 4, "name": "Desk Lamp", "category": "furniture", "price": 89},
        {"id": 5, "name": "Laptop Stand", "category": "accessories", "price": 199},
    ]

    print("filter electronics:")
    for p in filter_by(products, category="electronics"):
        print(" ", p["name"])

    print("\nsearch 'desk':")
    for p in search_by_key(products, "name", "desk"):
        print(" ", p["name"])

    print("\nsort by price:")
    for p in sort_by(products, "price"):
        print(f"  {p['name']} - {p['price']}")

    print("\nfuzzy search 'lpt':")
    for p in fuzzy_search(products, "name", "lpt"):
        print(" ", p["name"])

    print("\nhighlight 'desk':", highlight("Standing Desk and Desk Lamp", "desk"))

    print("\nmulti search 'lap' in name+category:")
    for p in multi_search(products, ["name", "category"], "lap"):
        print(" ", p["name"])
