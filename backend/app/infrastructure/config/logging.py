"""Structured logging configuration for the backend service."""

from __future__ import annotations

import json
import logging
import time
from contextlib import contextmanager
from typing import Iterator


def configure_logging(level: int = logging.INFO) -> None:
    logging.basicConfig(level=level, format="%(message)s")


def log_event(**fields: object) -> None:
    logging.getLogger("multirag").info(json.dumps(fields, default=str, sort_keys=True))


@contextmanager
def timed_operation(operation: str, **fields: object) -> Iterator[None]:
    started = time.perf_counter()
    try:
        yield
    except Exception as exc:
        log_event(
            operation=operation,
            duration_ms=int((time.perf_counter() - started) * 1000),
            status="error",
            error_type=type(exc).__name__,
            **fields,
        )
        raise
    else:
        log_event(
            operation=operation,
            duration_ms=int((time.perf_counter() - started) * 1000),
            status="success",
            **fields,
        )

