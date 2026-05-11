import os
from pathlib import Path


def get_env(key: str, default: str | None = None) -> str | None:
    return os.environ.get(key, default)


def require_env(key: str) -> str:
    value = os.environ.get(key)
    if value is None:
        raise KeyError(f"Required environment variable missing: '{key}'")
    return value


def get_bool(key: str, default: bool = False) -> bool:
    value = os.environ.get(key, "").strip().lower()
    if not value:
        return default
    return value in ("1", "true", "yes", "on")


def get_int(key: str, default: int = 0) -> int:
    try:
        return int(os.environ.get(key, default))
    except (ValueError, TypeError):
        return default


def get_float(key: str, default: float = 0.0) -> float:
    try:
        return float(os.environ.get(key, default))
    except (ValueError, TypeError):
        return default


def get_list(key: str, separator: str = ",", default: list | None = None) -> list[str]:
    value = os.environ.get(key, "")
    if not value:
        return default or []
    return [item.strip() for item in value.split(separator) if item.strip()]


def load_dotenv(path: str = ".env") -> int:
    p = Path(path)
    if not p.exists():
        return 0
    loaded = 0
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value
            loaded += 1
    return loaded


def is_production() -> bool:
    return get_env("APP_ENV", "").lower() in ("production", "prod")


def is_development() -> bool:
    return get_env("APP_ENV", "development").lower() in ("development", "dev")


if __name__ == "__main__":
    os.environ["APP_ENV"] = "development"
    os.environ["DEBUG"] = "true"
    os.environ["MAX_RETRIES"] = "5"
    os.environ["THRESHOLD"] = "0.85"
    os.environ["ALLOWED_HOSTS"] = "localhost, 127.0.0.1, example.com"

    print("APP_ENV:       ", get_env("APP_ENV"))
    print("MISSING:       ", get_env("MISSING", "fallback"))
    print("DEBUG:         ", get_bool("DEBUG"))
    print("MAX_RETRIES:   ", get_int("MAX_RETRIES"))
    print("THRESHOLD:     ", get_float("THRESHOLD"))
    print("ALLOWED_HOSTS: ", get_list("ALLOWED_HOSTS"))
    print("is_production: ", is_production())
    print("is_development:", is_development())

    try:
        require_env("SECRET_KEY")
    except KeyError as e:
        print(f"KeyError: {e}")
