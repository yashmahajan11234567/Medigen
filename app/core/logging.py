import contextvars
import logging
from logging.config import dictConfig

from app.core.config import get_settings
from app.core.constants import REQUEST_ID_HEADER


_request_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "request_id", default=None
)


def set_request_id(request_id: str) -> None:
    _request_id_var.set(request_id)


def get_request_id() -> str | None:
    return _request_id_var.get()


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = _request_id_var.get() or "-"
        return True


def configure_logging() -> None:
    settings = get_settings()
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {
                    "format": "%(asctime)s | %(levelname)s | %(name)s | [%(request_id)s] | %(message)s"
                }
            },
            "handlers": {
                "default": {
                    "class": "logging.StreamHandler",
                    "formatter": "standard",
                    "filters": ["request_id"],
                }
            },
            "filters": {
                "request_id": {
                    "()": "app.core.logging.RequestIdFilter",
                }
            },
            "root": {"handlers": ["default"], "level": settings.log_level},
        }
    )
    logging.getLogger(__name__).debug("Logging configured.")

