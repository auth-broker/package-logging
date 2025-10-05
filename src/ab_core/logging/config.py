"""Main application for the User Service."""

import logging
import logging.config
from rich.traceback import install as rich_traceback_install

from pydantic import BaseModel, Field


class LoggingConfig(BaseModel):
    """Logging configuration factory."""

    level: str = Field(
        default="INFO",
        title="Log Level",
        description="Log Level for auth broker"
    )

    def apply(self):
        """Apply configuration."""
        rich_traceback_install(show_locals=False, width=120, word_wrap=True)

        LOGGING_CONFIG = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "rich": {
                    "format": "%(message)s",
                    "datefmt": "[%X]",
                },
            },
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
                },
            },
            "loggers": {
                # Root logger: colourful INFO+ output
                "": {
                    "level": self.level,
                    "handlers": ["rich"],
                    "propagate": False,
                },
                "ab_core": {
                    "level": self.level,
                    "handlers": ["rich"],
                    "propagate": False,
                },
                "ab_service": {
                    "level": "INFO",
                    "handlers": ["rich"],
                    "propagate": False,
                },
                "ab_client": {
                    "level": self.level,
                    "handlers": ["rich"],
                    "propagate": False,
                },
                "uvicorn": {
                    "level": self.level,
                    "handlers": ["rich"],
                    "propagate": False,
                },
            },
        }

        logging.config.dictConfig(LOGGING_CONFIG)
