import json
import time
import urllib.request
import urllib.parse
import urllib.error
import base64
import gzip
import zlib
from typing import Any
from http.client import HTTPResponse


class HttpError(Exception):
    def __init__(self, status: int, reason: str, body: str = "") -> None:
        self.status = status
        self.reason = reason
        self.body = body
        super().__init__(f"HTTP {status} {reason}")


class Response:
    def __init__(self, status: int, reason: str, headers: dict[str, str], raw: bytes, url: str) -> None:
        self.status = status
        self.reason = reason
        self.headers = headers
        self.content = raw
        self.url = url

    @property
    def ok(self) -> bool:
        return 200 <= self.status < 300

    @property
    def text(self) -> str:
        encoding = "utf-8"
        ct = self.headers.get("content-type", "")
        if "charset=" in ct:
            encoding = ct.split("charset=")[-1].split(";")[0].strip()
        return self.content.decode(encoding, errors="replace")

    def json(self) -> Any:
        return json.loads(self.text)

    def raise_for_status(self) -> None:
        if not self.ok:
            raise HttpError(self.status, self.reason, self.text)

    def __repr__(self) -> str:
        return f"Response(status={self.status}, url={self.url!r})"


def _build_url(base: str, path: str = "", params: dict | None = None) -> str:
    url = base.rstrip("/") + ("/" + path.lstrip("/") if path else "")
    if params:
        url += "?" + urllib.parse.urlencode(
            {k: v for k, v in params.items() if v is not None}
        )
    return url


def _decompress(data: bytes, encoding: str) -> bytes:
    if encoding == "gzip":
        return gzip.decompress(data)
    if encoding in ("deflate", "zlib"):
        return zlib.decompress(data)
    return data


def _send(
    url: str,
    method: str = "GET",
    headers: dict[str, str] | None = None,
    body: bytes | None = None,
    timeout: float = 10.0,
) -> Response:
    req = urllib.request.Request(url, data=body, method=method)
    for k, v in (headers or {}).items():
        req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            enc = resp.headers.get("Content-Encoding", "")
            raw = _decompress(raw, enc)
            hdrs = {k.lower(): v for k, v in resp.headers.items()}
            return Response(resp.status, resp.reason, hdrs, raw, resp.url)
    except urllib.error.HTTPError as e:
        raw = e.read() or b""
        hdrs = {k.lower(): v for k, v in e.headers.items()}
        return Response(e.code, e.reason or "", hdrs, raw, url)
    except urllib.error.URLError as e:
        raise ConnectionError(str(e.reason)) from e


class HttpClient:
    def __init__(
        self,
        base_url: str = "",
        headers: dict[str, str] | None = None,
        timeout: float = 10.0,
        retries: int = 0,
        retry_delay: float = 1.0,
        retry_on: tuple[int, ...] = (429, 500, 502, 503, 504),
        auth: tuple[str, str] | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.retries = retries
        self.retry_delay = retry_delay
        self.retry_on = retry_on
        self._headers: dict[str, str] = {
            "Accept": "application/json",
            "User-Agent": "http-client-utils/1.0",
        }
        if headers:
            self._headers.update(headers)
        if auth:
            token = base64.b64encode(f"{auth[0]}:{auth[1]}".encode()).decode()
            self._headers["Authorization"] = f"Basic {token}"

    def set_header(self, key: str, value: str) -> None:
        self._headers[key] = value

    def set_auth(self, username: str, password: str) -> None:
        token = base64.b64encode(f"{username}:{password}".encode()).decode()
        self._headers["Authorization"] = f"Basic {token}"

    def set_bearer(self, token: str) -> None:
        self._headers["Authorization"] = f"Bearer {token}"

    def request(
        self,
        method: str,
        path: str = "",
        *,
        params: dict | None = None,
        json_data: Any = None,
        form_data: dict | None = None,
        data: bytes | None = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> Response:
        url = _build_url(self.base_url, path, params)
        merged = {**self._headers, **(headers or {})}
        body: bytes | None = data

        if json_data is not None:
            body = json.dumps(json_data).encode()
            merged.setdefault("Content-Type", "application/json")
        elif form_data is not None:
            body = urllib.parse.urlencode(form_data).encode()
            merged.setdefault("Content-Type", "application/x-www-form-urlencoded")

        if body is not None:
            merged["Content-Length"] = str(len(body))

        effective_timeout = timeout if timeout is not None else self.timeout
        attempts = self.retries + 1
        last_resp: Response | None = None

        for attempt in range(attempts):
            try:
                resp = _send(url, method.upper(), merged, body, effective_timeout)
                if resp.status in self.retry_on and attempt < attempts - 1:
                    last_resp = resp
                    time.sleep(self.retry_delay * (2 ** attempt))
                    continue
                return resp
            except ConnectionError:
                if attempt < attempts - 1:
                    time.sleep(self.retry_delay * (2 ** attempt))
                else:
                    raise

        return last_resp  # type: ignore[return-value]

    def get(self, path: str = "", *, params: dict | None = None, **kw) -> Response:
        return self.request("GET", path, params=params, **kw)

    def post(self, path: str = "", *, json_data: Any = None, form_data: dict | None = None, **kw) -> Response:
        return self.request("POST", path, json_data=json_data, form_data=form_data, **kw)

    def put(self, path: str = "", *, json_data: Any = None, **kw) -> Response:
        return self.request("PUT", path, json_data=json_data, **kw)

    def patch(self, path: str = "", *, json_data: Any = None, **kw) -> Response:
        return self.request("PATCH", path, json_data=json_data, **kw)

    def delete(self, path: str = "", **kw) -> Response:
        return self.request("DELETE", path, **kw)

    def head(self, path: str = "", **kw) -> Response:
        return self.request("HEAD", path, **kw)

    def __repr__(self) -> str:
        return f"HttpClient(base_url={self.base_url!r}, timeout={self.timeout})"


def get(url: str, *, params: dict | None = None, headers: dict | None = None, timeout: float = 10.0) -> Response:
    return _send(_build_url(url, params=params), "GET", headers, timeout=timeout)


def post(url: str, *, json_data: Any = None, form_data: dict | None = None,
         headers: dict | None = None, timeout: float = 10.0) -> Response:
    hdrs = dict(headers or {})
    body: bytes | None = None
    if json_data is not None:
        body = json.dumps(json_data).encode()
        hdrs.setdefault("Content-Type", "application/json")
    elif form_data is not None:
        body = urllib.parse.urlencode(form_data).encode()
        hdrs.setdefault("Content-Type", "application/x-www-form-urlencoded")
    if body:
        hdrs["Content-Length"] = str(len(body))
    return _send(url, "POST", hdrs, body, timeout)


def put(url: str, *, json_data: Any = None, headers: dict | None = None, timeout: float = 10.0) -> Response:
    hdrs = dict(headers or {})
    body: bytes | None = None
    if json_data is not None:
        body = json.dumps(json_data).encode()
        hdrs.setdefault("Content-Type", "application/json")
        hdrs["Content-Length"] = str(len(body))
    return _send(url, "PUT", hdrs, body, timeout)


def patch(url: str, *, json_data: Any = None, headers: dict | None = None, timeout: float = 10.0) -> Response:
    hdrs = dict(headers or {})
    body: bytes | None = None
    if json_data is not None:
        body = json.dumps(json_data).encode()
        hdrs.setdefault("Content-Type", "application/json")
        hdrs["Content-Length"] = str(len(body))
    return _send(url, "PATCH", hdrs, body, timeout)


def delete(url: str, *, headers: dict | None = None, timeout: float = 10.0) -> Response:
    return _send(url, "DELETE", headers, timeout=timeout)


def head(url: str, *, headers: dict | None = None, timeout: float = 10.0) -> Response:
    return _send(url, "HEAD", headers, timeout=timeout)


def build_url(base: str, path: str = "", params: dict | None = None) -> str:
    return _build_url(base, path, params)


def encode_params(params: dict) -> str:
    return urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})


def parse_url(url: str) -> dict[str, str]:
    p = urllib.parse.urlparse(url)
    return {
        "scheme": p.scheme,
        "host": p.netloc,
        "path": p.path,
        "query": p.query,
        "fragment": p.fragment,
    }


if __name__ == "__main__":
    BASE = "https://httpbin.org"

    print("--- GET ---")
    r = get(f"{BASE}/get", params={"foo": "bar", "n": 42})
    print("status:", r.status, "| ok:", r.ok)
    data = r.json()
    print("args:", data.get("args"))

    print("\n--- POST JSON ---")
    r2 = post(f"{BASE}/post", json_data={"name": "Alice", "age": 30})
    print("status:", r2.status)
    print("json sent:", r2.json().get("json"))

    print("\n--- POST form ---")
    r3 = post(f"{BASE}/post", form_data={"user": "bob", "pass": "secret"})
    print("status:", r3.status)
    print("form sent:", r3.json().get("form"))

    print("\n--- Response.raise_for_status ---")
    r4 = get(f"{BASE}/status/404")
    print("status:", r4.status)
    try:
        r4.raise_for_status()
    except HttpError as e:
        print(f"HttpError: {e}")

    print("\n--- HttpClient ---")
    client = HttpClient(base_url=BASE, timeout=10.0)
    r5 = client.get("/get", params={"client": "yes"})
    print("status:", r5.status)
    print("args:", r5.json().get("args"))

    print("\n--- HttpClient POST ---")
    r6 = client.post("/post", json_data={"x": 1, "y": 2})
    print("status:", r6.status)
    print("json:", r6.json().get("json"))

    print("\n--- HttpClient set_bearer ---")
    client.set_bearer("my-token-123")
    r7 = client.get("/bearer")
    print("status:", r7.status)
    print("authenticated:", r7.json().get("authenticated"))

    print("\n--- build_url / encode_params / parse_url ---")
    print("build_url:    ", build_url("https://api.example.com", "/users", {"page": 1, "limit": 10}))
    print("encode_params:", encode_params({"q": "hello world", "lang": "en", "empty": None}))
    print("parse_url:    ", parse_url("https://api.example.com/v1/users?page=2#top"))

    print("\n--- headers in response ---")
    r8 = get(f"{BASE}/get")
    print("content-type:", r8.headers.get("content-type"))
