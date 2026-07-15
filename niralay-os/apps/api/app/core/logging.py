"""
Structured logging configuration for NiralayOS.

Supports two output formats:
  - json  : machine-readable, suitable for log aggregation (production)
  - text  : human-readable with colour, suitable for development

Usage:
    from app.core.logging import get_logger

    logger = get_logger(__name__)
    logger.info("event", extra={"user_id": 42})
"""

import logging
import logging.config
import sys
from datetime import datetime, timezone
from typing import Any

try:
    import json as _json
except ImportError:  # pragma: no cover
    raise

from app.core.settings import get_settings

_CONFIGURED = False


class _JsonFormatter(logging.Formatter):
    """
    Emit log records as a single JSON line.

    Includes: timestamp (ISO-8601 UTC), level, logger, message,
    and any extra key/value pairs attached to the log call.
    """

    _SKIP_ATTRS: frozenset[str] = frozenset(
        {
            "args", "created", "exc_info", "exc_text", "filename",
            "funcName", "levelname", "levelno", "lineno", "message",
            "module", "msecs", "msg", "name", "pathname", "process",
            "processName", "relativeCreated", "stack_info", "taskName",
            "thread", "threadName",
        }
    )

    def format(self, record: logging.LogRecord) -> str:  # noqa: A003
        record.message = record.getMessage()
        if record.exc_info:
            record.exc_text = self.formatException(record.exc_info)

        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(
                record.created, tz=timezone.utc
            ).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.message,
        }

        # Add any extra fields injected via logging.info(..., extra={...})
        for key, value in record.__dict__.items():
            if key not in self._SKIP_ATTRS:
                payload[key] = value

        if record.exc_text:
            payload["exc_text"] = record.exc_text

        return _json.dumps(payload, default=str, ensure_ascii=False)


class _TextFormatter(logging.Formatter):
    """Coloured text formatter for development consoles."""

    GREY = "\x1b[38;5;240m"
    GREEN = "\x1b[32m"
    YELLOW = "\x1b[33m"
    RED = "\x1b[31m"
    BOLD_RED = "\x1b[31;1m"
    RESET = "\x1b[0m"

    _LEVEL_COLORS: dict[int, str] = {
        logging.DEBUG: GREY,
        logging.INFO: GREEN,
        logging.WARNING: YELLOW,
        logging.ERROR: RED,
        logging.CRITICAL: BOLD_RED,
    }

    def format(self, record: logging.LogRecord) -> str:  # noqa: A003
        color = self._LEVEL_COLORS.get(record.levelno, self.RESET)
        ts = datetime.fromtimestamp(record.created, tz=timezone.utc).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        prefix = (
            f"{self.GREY}{ts}{self.RESET} "
            f"{color}{record.levelname:<8}{self.RESET} "
            f"{self.GREY}{record.name}{self.RESET}"
        )
        message = record.getMessage()
        result = f"{prefix}  {message}"
        if record.exc_info:
            result += "\n" + self.formatException(record.exc_info)
        return result


def configure_logging() -> None:
    """
    Configure the root logger.

    Should be called once at application startup (from lifespan).
    Subsequent calls are no-ops.
    """
    global _CONFIGURED
    if _CONFIGURED:
        return

    cfg = get_settings()
    level = cfg.LOG_LEVEL

    formatter: logging.Formatter
    if cfg.LOG_FORMAT == "json":
        formatter = _JsonFormatter()
    else:
        formatter = _TextFormatter()

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    handlers: list[logging.Handler] = [handler]

    # Optional file handler
    if cfg.LOG_FILE_PATH:
        fh = logging.FileHandler(cfg.LOG_FILE_PATH, encoding="utf-8")
        fh.setFormatter(_JsonFormatter())  # always JSON in files
        handlers.append(fh)

    logging.basicConfig(
        level=level,
        handlers=handlers,
        force=True,
    )

    # Silence noisy third-party loggers
    for noisy in ("uvicorn.access", "sqlalchemy.engine.Engine"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    _CONFIGURED = True

    root_logger = logging.getLogger(__name__)
    root_logger.info(
        "Logging configured",
        extra={
            "log_level": level,
            "log_format": cfg.LOG_FORMAT,
            "environment": cfg.ENVIRONMENT.value,
        },
    )


def get_logger(name: str) -> logging.Logger:
    """
    Return a named logger.

    Ensures logging is configured before returning the logger instance.
    Safe to call from module level or inside functions.
    """
    if not _CONFIGURED:
        configure_logging()
    return logging.getLogger(name)
