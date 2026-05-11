import json
import os
from pathlib import Path


class Config:
    def __init__(self, path: str | None = None):
        self._data: dict = {}
        if path:
            self.load_file(path)
        self._load_env()

    def load_file(self, path: str) -> None:
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"Config file not found: {path}")
        with p.open(encoding="utf-8") as f:
            self._data.update(json.load(f))

    def _load_env(self) -> None:
        for key, value in os.environ.items():
            self._data.setdefault(key.lower(), value)

    def get(self, key: str, default=None):
        return self._data.get(key.lower(), default)

    def require(self, key: str):
        value = self.get(key)
        if value is None:
            raise KeyError(f"Required config key missing: '{key}'")
        return value

    def __repr__(self) -> str:
        return f"Config({list(self._data.keys())})"


if __name__ == "__main__":
    cfg = Config()

    print(cfg)
    print("DEBUG:", cfg.get("debug", False))
    print("APP_ENV:", cfg.get("app_env", "development"))

    try:
        cfg.require("nonexistent_key")
    except KeyError as e:
        print(f"KeyError caught: {e}")
