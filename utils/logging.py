import logging
import json
import os
import sys
from datetime import datetime, timezone
from typing import Any


def _resolve_level(level: str | int | None) -> int:
    if isinstance(level, int):
        return level

    if isinstance(level, str):
        return getattr(logging, level.upper(), logging.INFO)

    env_level = os.getenv("LOG_LEVEL", "INFO").upper()
    return getattr(logging, env_level, logging.INFO)


def get_logger(name: str = "voice_agent", level: str | int | None = None):
    logger = logging.getLogger(name)
    logger.setLevel(_resolve_level(level))
    logger.propagate = False

    if logger.handlers:
        return logger

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(_resolve_level(level))

    formatter = JsonFormatter()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


class JsonFormatter(logging.Formatter):

    def format(self, record: logging.LogRecord) -> str:
        log_record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        if isinstance(record.msg, dict):
            payload = dict(record.msg)
            log_record["message"] = payload.pop("message", "structured_log")
            log_record.update(payload)
        else:
            log_record["message"] = record.getMessage()

        if hasattr(record, "extra_data"):
            extra_data: Any = record.extra_data
            if isinstance(extra_data, dict):
                log_record.update(extra_data)

        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_record, ensure_ascii=False, default=str)
