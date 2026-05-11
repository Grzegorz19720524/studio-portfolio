import json
import urllib.error
import urllib.request
from typing import Any


def _request(method: str, url: str, data: dict | None = None, headers: dict | None = None) -> dict:
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, method=method)
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json")
    if headers:
        for key, value in headers.items():
            req.add_header(key, value)

    try:
        with urllib.request.urlopen(req) as response:
            raw = response.read().decode()
            return {
                "status": response.status,
                "headers": dict(response.headers),
                "body": json.loads(raw) if raw else None,
            }
    except urllib.error.HTTPError as e:
        return {"status": e.code, "error": str(e), "body": None}
    except urllib.error.URLError as e:
        return {"status": None, "error": str(e.reason), "body": None}


def get(url: str, headers: dict | None = None) -> dict:
    return _request("GET", url, headers=headers)


def post(url: str, data: dict, headers: dict | None = None) -> dict:
    return _request("POST", url, data=data, headers=headers)


def put(url: str, data: dict, headers: dict | None = None) -> dict:
    return _request("PUT", url, data=data, headers=headers)


def delete(url: str, headers: dict | None = None) -> dict:
    return _request("DELETE", url, headers=headers)


def is_ok(response: dict) -> bool:
    return isinstance(response.get("status"), int) and 200 <= response["status"] < 300


if __name__ == "__main__":
    response = get("https://jsonplaceholder.typicode.com/todos/1")
    print("status:", response["status"])
    print("is_ok: ", is_ok(response))
    print("body:  ", response["body"])

    created = post(
        "https://jsonplaceholder.typicode.com/posts",
        data={"title": "test", "body": "hello", "userId": 1},
    )
    print("\nPOST status:", created["status"])
    print("POST body:  ", created["body"])
