import logging
import sys
from pathlib import Path


def get_logger(name: str, level: int = logging.DEBUG, log_file: str | None = None) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(level)
    fmt = logging.Formatter(
        "%(asctime)s [%(levelname)-8s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(fmt)
    logger.addHandler(stream_handler)

    if log_file:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(fmt)
        logger.addHandler(file_handler)

    return logger


if __name__ == "__main__":
    # stdout only
    log = get_logger("demo")
    log.debug("debug message")
    log.info("info message")
    log.warning("warning message")
    log.error("error message")

    # stdout + file
    log_file = get_logger("demo.file", log_file="logs/demo.log")
    log_file.info("this also writes to logs/demo.log")
