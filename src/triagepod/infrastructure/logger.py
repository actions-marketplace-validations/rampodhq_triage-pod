from __future__ import annotations

import logging
from typing import cast

import structlog


def configure_logging(level: str) -> structlog.stdlib.BoundLogger:
    logging.basicConfig(level=getattr(logging, level.upper(), logging.INFO), format="%(message)s")
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    return cast(structlog.stdlib.BoundLogger, structlog.get_logger("triagepod"))
