import logging
import logging.handlers
import sys
import json
from pathlib import Path
from typing import Any

DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL

_DEFAULT_FMT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
_DEFAULT_DATE_FMT = "%Y-%m-%d %H:%M:%S"


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        _skip = set(logging.LogRecord("", 0, "", 0, "", (), None).__dict__) | {"message", "asctime"}
        entry: dict[str, Any] = {
            "time": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            entry["exception"] = self.formatException(record.exc_info)
        extra = {k: v for k, v in record.__dict__.items() if k not in _skip and not k.startswith("_")}
        if extra:
            entry["extra"] = extra
        return json.dumps(entry)


def make_logger(
    name: str,
    level: int = DEBUG,
    fmt: str = _DEFAULT_FMT,
    date_fmt: str = _DEFAULT_DATE_FMT,
    *,
    to_console: bool = True,
    to_file: str | None = None,
    json_format: bool = False,
    rotate: bool = False,
    max_bytes: int = 5 * 1024 * 1024,
    backup_count: int = 3,
) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.handlers.clear()
    formatter: logging.Formatter = JsonFormatter(datefmt=date_fmt) if json_format else logging.Formatter(fmt, date_fmt)
    if to_console:
        ch = logging.StreamHandler(sys.stdout)
        ch.setFormatter(formatter)
        logger.addHandler(ch)
    if to_file:
        Path(to_file).parent.mkdir(parents=True, exist_ok=True)
        fh: logging.Handler = (
            logging.handlers.RotatingFileHandler(
                to_file, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8"
            )
            if rotate
            else logging.FileHandler(to_file, encoding="utf-8")
        )
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    logger.propagate = False
    return logger


def get_logger(name: str, level: int = INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        make_logger(name, level=level)
    return logger


def add_console_handler(
    logger: logging.Logger,
    level: int = DEBUG,
    fmt: str = _DEFAULT_FMT,
    date_fmt: str = _DEFAULT_DATE_FMT,
) -> logging.StreamHandler:
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter(fmt, date_fmt))
    logger.addHandler(handler)
    return handler


def add_file_handler(
    logger: logging.Logger,
    path: str,
    level: int = DEBUG,
    fmt: str = _DEFAULT_FMT,
    date_fmt: str = _DEFAULT_DATE_FMT,
    encoding: str = "utf-8",
) -> logging.FileHandler:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    handler = logging.FileHandler(path, encoding=encoding)
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter(fmt, date_fmt))
    logger.addHandler(handler)
    return handler


def add_rotating_handler(
    logger: logging.Logger,
    path: str,
    max_bytes: int = 5 * 1024 * 1024,
    backup_count: int = 3,
    level: int = DEBUG,
    fmt: str = _DEFAULT_FMT,
    date_fmt: str = _DEFAULT_DATE_FMT,
    encoding: str = "utf-8",
) -> logging.handlers.RotatingFileHandler:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    handler = logging.handlers.RotatingFileHandler(
        path, maxBytes=max_bytes, backupCount=backup_count, encoding=encoding
    )
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter(fmt, date_fmt))
    logger.addHandler(handler)
    return handler


def set_level(logger: logging.Logger | str, level: int) -> None:
    if isinstance(logger, str):
        logger = logging.getLogger(logger)
    logger.setLevel(level)


def silence(logger: logging.Logger | str) -> None:
    set_level(logger, CRITICAL + 1)


def enable(logger: logging.Logger | str, level: int = DEBUG) -> None:
    set_level(logger, level)


def get_level_name(level: int) -> str:
    return logging.getLevelName(level)


def parse_level(name: str) -> int:
    return getattr(logging, name.upper(), INFO)


def clear_handlers(logger: logging.Logger | str) -> None:
    if isinstance(logger, str):
        logger = logging.getLogger(logger)
    logger.handlers.clear()


def list_loggers() -> list[str]:
    return sorted(logging.Logger.manager.loggerDict.keys())


class _ListHandler(logging.Handler):
    def __init__(self, records: list) -> None:
        super().__init__()
        self.records = records

    def emit(self, record: logging.LogRecord) -> None:
        self.records.append(record)


class LogCapture:
    def __init__(self, logger_name: str = "", level: int = DEBUG) -> None:
        self.logger_name = logger_name
        self.level = level
        self.records: list[logging.LogRecord] = []
        self._handler: _ListHandler | None = None
        self._logger: logging.Logger | None = None

    def __enter__(self) -> "LogCapture":
        self._handler = _ListHandler(self.records)
        self._handler.setLevel(self.level)
        self._logger = logging.getLogger(self.logger_name)
        self._logger.addHandler(self._handler)
        return self

    def __exit__(self, *_) -> None:
        if self._logger and self._handler:
            self._logger.removeHandler(self._handler)

    @property
    def messages(self) -> list[str]:
        return [r.getMessage() for r in self.records]

    @property
    def levels(self) -> list[str]:
        return [r.levelname for r in self.records]


class BoundLogger:
    def __init__(self, logger: logging.Logger, **fields: Any) -> None:
        self._logger = logger
        self._fields = fields

    def _log(self, level: int, msg: str, **kw: Any) -> None:
        self._logger.log(level, msg, extra={**self._fields, **kw})

    def debug(self, msg: str, **kw: Any) -> None:
        self._log(DEBUG, msg, **kw)

    def info(self, msg: str, **kw: Any) -> None:
        self._log(INFO, msg, **kw)

    def warning(self, msg: str, **kw: Any) -> None:
        self._log(WARNING, msg, **kw)

    def error(self, msg: str, **kw: Any) -> None:
        self._log(ERROR, msg, **kw)

    def critical(self, msg: str, **kw: Any) -> None:
        self._log(CRITICAL, msg, **kw)

    def bind(self, **fields: Any) -> "BoundLogger":
        return BoundLogger(self._logger, **{**self._fields, **fields})


def bind(logger: logging.Logger, **fields: Any) -> BoundLogger:
    return BoundLogger(logger, **fields)


if __name__ == "__main__":
    print("--- make_logger (console) ---")
    log = make_logger("app", level=DEBUG)
    log.debug("debug message")
    log.info("info message")
    log.warning("warning message")
    log.error("error message")

    print("\n--- get_logger ---")
    log2 = get_logger("mymodule", level=INFO)
    log2.info("logger ready")
    log2.debug("this debug is suppressed (level=INFO)")

    print("\n--- set_level / silence / enable ---")
    silence("mymodule")
    log2.error("silenced - not shown")
    enable("mymodule", INFO)
    log2.info("re-enabled")

    print("\n--- parse_level / get_level_name ---")
    print("parse_level('warning'):", parse_level("warning"))
    print("get_level_name(30):    ", get_level_name(30))

    print("\n--- LogCapture ---")
    cap_log = make_logger("capture_test", level=DEBUG)
    with LogCapture("capture_test") as cap:
        cap_log.info("captured info")
        cap_log.warning("captured warning")
        cap_log.error("captured error")
    print("messages:", cap.messages)
    print("levels:  ", cap.levels)

    print("\n--- BoundLogger / bind ---")
    base = make_logger("bound", level=DEBUG)
    bound = bind(base, service="api", version="1.0")
    bound.info("request received")
    worker = bound.bind(worker_id=42)
    worker.warning("slow response")

    print("\n--- JSON format ---")
    jlog = make_logger("json_demo", level=DEBUG, json_format=True)
    jlog.info("structured log entry")
    jlog.error("something failed")

    print("\n--- list_loggers ---")
    names = list_loggers()
    print("active loggers:", names[:5], "..." if len(names) > 5 else "")
