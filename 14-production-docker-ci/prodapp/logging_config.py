"""structlog configuration ≈ logback-spring.xml with a JSON encoder.

The mental model is identical to SLF4J: any module grabs a logger
(`structlog.get_logger()` ≈ `LoggerFactory.getLogger(...)`), key=value pairs
replace string concatenation (`log.info("user_created", user_id=u.id)`), and
ALL configuration lives in one place called from the composition root.

Output is one JSON object per line — the format Loki/ELK/CloudWatch/Datadog
ingest. A grep-able plain-text line dies the day you have 12 replicas.

stdlib `logging` stays as the backend (existing `logging.getLogger` calls —
uvicorn's, SQLAlchemy's — get captured and re-emitted as JSON via
ProcessorFormatter's foreign_pre_chain), so nothing in the ecosystem breaks.
"""

import logging
import sys
from typing import TextIO

import structlog
from structlog.typing import Processor

_SHARED_PROCESSORS: list[Processor] = [
    structlog.contextvars.merge_contextvars,  # bind_contextvars ≈ SLF4J's MDC
    structlog.stdlib.add_log_level,
    structlog.stdlib.add_logger_name,
    structlog.stdlib.PositionalArgumentsFormatter(),
    structlog.processors.StackInfoRenderer(),
    structlog.processors.format_exc_info,  # tracebacks as structured fields
]


def make_json_handler(stream: TextIO) -> logging.Handler:
    """The single handler that renders EVERYTHING as JSON — including records
    from plain stdlib loggers (uvicorn, alembic, sqlalchemy) via foreign_pre_chain.
    Exposed for tests: point it at a StringIO instead of stdout."""
    handler = logging.StreamHandler(stream)
    handler.setFormatter(
        structlog.stdlib.ProcessorFormatter(
            processors=[
                structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                structlog.processors.TimeStamper(fmt="iso", utc=True),
                structlog.processors.JSONRenderer(),
            ],
            foreign_pre_chain=_SHARED_PROCESSORS,
        )
    )
    return handler


def configure_structlog(log_level: int = logging.INFO) -> None:
    root = logging.getLogger()
    root.handlers = [make_json_handler(sys.stdout)]  # replace: no dev basicConfig
    root.setLevel(log_level)

    structlog.configure(
        processors=[*_SHARED_PROCESSORS, structlog.stdlib.ProcessorFormatter.wrap_for_formatter],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        cache_logger_on_first_use=True,
    )
