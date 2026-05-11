import socket
import urllib.request
import urllib.error
import time


def get_local_ip() -> str:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"


def get_hostname() -> str:
    return socket.gethostname()


def resolve_host(hostname: str) -> str | None:
    try:
        return socket.gethostbyname(hostname)
    except socket.gaierror:
        return None


def is_port_open(host: str, port: int, timeout: float = 2.0) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False


def is_online(url: str = "https://www.google.com", timeout: float = 3.0) -> bool:
    try:
        urllib.request.urlopen(url, timeout=timeout)
        return True
    except (urllib.error.URLError, OSError):
        return False


def ping(host: str, port: int = 80, timeout: float = 2.0) -> float | None:
    try:
        start = time.perf_counter()
        with socket.create_connection((host, port), timeout=timeout):
            return round((time.perf_counter() - start) * 1000, 2)
    except (socket.timeout, ConnectionRefusedError, OSError):
        return None


def get_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


def parse_url(url: str) -> dict:
    from urllib.parse import urlparse, parse_qs
    parsed = urlparse(url)
    return {
        "scheme": parsed.scheme,
        "host": parsed.hostname,
        "port": parsed.port,
        "path": parsed.path,
        "query": parse_qs(parsed.query),
        "fragment": parsed.fragment,
    }


if __name__ == "__main__":
    print("local IP:   ", get_local_ip())
    print("hostname:   ", get_hostname())
    print("resolve:    ", resolve_host("google.com"))
    print("port open:  ", is_port_open("google.com", 443))
    print("is online:  ", is_online())
    print("ping(ms):   ", ping("google.com", 443))
    print("free port:  ", get_free_port())
    print("parse url:  ", parse_url("https://example.com:8080/api/v1?foo=bar&baz=1#section"))
