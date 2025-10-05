"""Main application for the User Service."""

import logging
import logging.config

from pydantic import BaseModel, Field
from rich.traceback import install as rich_traceback_install

# ── Filters ────────────────────────────────────────────────────────────────────


# Append the logger name (e.g. ab_service.user.routes) in front of the message.
class PrependLoggerName(logging.Filter):
    """Prepend the logger name to logs."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Prepend the logger name to logs."""
        prefix = f"[bold green]{record.name}[/]"
        record.msg = f"{prefix} {record.getMessage()}"
        record.args = ()
        return True


# Append any non-standard LogRecord attributes (those provided via `extra=...`)
# as key=value pairs after the message.
_STANDARD_LOGRECORD_FIELDS = {
    "name",
    "msg",
    "args",
    "levelname",
    "levelno",
    "pathname",
    "filename",
    "module",
    "exc_info",
    "exc_text",
    "stack_info",
    "lineno",
    "funcName",
    "created",
    "msecs",
    "relativeCreated",
    "thread",
    "threadName",
    "processName",
    "process",
    "taskName",
    "color_message",
}


class ExtrasToMessage(logging.Filter):
    """Append the log records 'extras' to logs."""

    def __init__(self, *, redact: list[str] | None = None):
        """Support optional redaction."""
        super().__init__()
        self.redact = set(redact or [])

    def filter(self, record: logging.LogRecord) -> bool:
        """Append the log records 'extras' to logs."""
        extras = {
            k: ("***" if k in self.redact else v)
            for k, v in record.__dict__.items()
            if k not in _STANDARD_LOGRECORD_FIELDS and not k.startswith("_")
        }
        if extras:
            pairs = "\n".join(f"\t{k}={extras[k]}" for k in sorted(extras))
            if pairs:
                record.msg = f"{record.getMessage()}\n{pairs}"
            record.args = ()
        return True


class LoggingConfig(BaseModel):
    """Logging configuration factory."""

    level: str | int = Field(
        default="INFO",
        title="Log Level",
        description="Log level for the service",
    )
    show_logger_name: bool = Field(
        default=True,
        description="Prepend the logger name (e.g. ab_service.user) to each log line.",
    )
    show_extras: bool = Field(
        default=True,
        description="Append any LogRecord extras (from extra={}) as key=value.",
    )
    redact_extras: list[str] = Field(
        default=["password", "secret", "token"],
        description="Keys in extras to redact if show_extras is enabled.",
    )
    namespaces: list[str] = Field(default=[""], description="Namespaces that this logging configuration applies to.")

    def apply(self) -> None:
        """Apply configuration."""
        rich_traceback_install(show_locals=False, width=120, word_wrap=True)

        filters = {}
        handler_filters = []

        if self.show_logger_name:
            filters["prepend_logger_name"] = {"()": f"{__name__}.PrependLoggerName"}
            handler_filters.append("prepend_logger_name")

        if self.show_extras:
            filters["extras_to_message"] = {
                "()": f"{__name__}.ExtrasToMessage",
                "redact": self.redact_extras,
            }
            handler_filters.append("extras_to_message")

        logging.config.dictConfig(
            {
                "version": 1,
                "disable_existing_loggers": False,
                "formatters": {
                    # RichHandler mainly uses the message; timestamp/level/path are handled by the handler.
                    "rich": {"format": "%(message)s", "datefmt": "[%X]"},
                },
                "filters": filters,
                "handlers": {
                    "rich": {
                        "class": "rich.logging.RichHandler",
                        "level": self.level,
                        "formatter": "rich",
                        "rich_tracebacks": True,
                        "tracebacks_show_locals": False,
                        "markup": True,
                        "show_time": True,
                        "show_level": True,
                        "show_path": True,
                        "enable_link_path": True,
                        "keywords": ["DEBUG", "INFO", "WARNING", "ERROR", "EXCEPTION", "CRITICAL"],
                        **({"filters": handler_filters} if handler_filters else {}),
                    },
                },
                "loggers": {
                    namespace: {"level": self.level, "handlers": ["rich"], "propagate": False}
                    for namespace in self.namespaces
                },
            }
        )
