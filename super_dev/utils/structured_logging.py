"""Structured JSON logging support for the Super Dev pipeline.

Configuration is driven by environment variables ``SUPER_DEV_LOG_LEVEL`` and
``SUPER_DEV_LOG_FORMAT``. JSON output is single-line for log aggregation tools.

Usage::

    from super_dev.utils.structured_logging import get_logger, setup_structured_logging
    setup_structured_logging()
    log = get_logger("pipeline.engine")
    log.info("phase completed", extra={"phase": "drafting"})
"""

from __future__ import annotations

import json
import logging
import os
from collections.abc import MutableMapping
from datetime import datetime, timezone
from typing import Any


class _JsonFormatter(logging.Formatter):
    """Format log records as single-line JSON for log aggregation tools."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "funcName": record.funcName,
            "lineno": record.lineno,
        }
        for key in ("run_id", "phase", "project"):
            value = getattr(record, key, None)
            if value is not None:
                payload[key] = value
        if record.exc_info and not record.exc_text:
            record.exc_text = self.formatException(record.exc_info)
        if record.exc_text:
            payload["exception"] = record.exc_text
        return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


_TEXT_FMT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


def setup_structured_logging(level: str | None = None, fmt: str | None = None) -> None:
    """Configure the root logger for structured or text output.

    Falls back to env vars ``SUPER_DEV_LOG_LEVEL`` / ``SUPER_DEV_LOG_FORMAT``
    when *level* or *fmt* are not provided explicitly.
    """
    resolved_level = (level or os.environ.get("SUPER_DEV_LOG_LEVEL") or "INFO").upper()
    resolved_fmt = (fmt or os.environ.get("SUPER_DEV_LOG_FORMAT") or "text").lower()

    root = logging.getLogger()
    root.setLevel(getattr(logging, resolved_level, logging.INFO))

    formatter = _JsonFormatter() if resolved_fmt == "json" else logging.Formatter(_TEXT_FMT)

    # Update existing StreamHandler formatters, or add a new one.
    updated = False
    for h in root.handlers:
        if isinstance(h, logging.StreamHandler):
            h.setFormatter(formatter)
            updated = True

    if not updated:
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        root.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    """Return a :class:`logging.Logger` with the given *name*."""
    return logging.getLogger(name)


class PipelineLogAdapter(logging.LoggerAdapter):
    """Logger adapter that injects pipeline context (*run_id*, *phase*, *project*)
    into every log record via extra fields."""

    def __init__(
        self,
        logger: logging.Logger,
        run_id: str = "",
        phase: str = "",
        project: str = "",
    ) -> None:
        super().__init__(logger, {})
        self.run_id = run_id
        self.phase = phase
        self.project = project

    def process(
        self, msg: str, kwargs: MutableMapping[str, Any]
    ) -> tuple[str, MutableMapping[str, Any]]:
        """Attach pipeline fields to the ``extra`` dict of the log record."""
        extra = dict(kwargs.get("extra") or {})
        extra.update({"run_id": self.run_id, "phase": self.phase, "project": self.project})
        return msg, {**kwargs, "extra": extra}
