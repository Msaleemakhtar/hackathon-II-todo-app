import logging
import sys

from pythonjsonlogger.json import JsonFormatter

from .config import settings


def setup_logging():
    """Configure logging for the application."""
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO

    # Create handler
    handler = logging.StreamHandler(sys.stdout)

    # JSON formatter for production, simple formatter for development
    if settings.DEBUG:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    else:
        formatter = JsonFormatter(
            "%(asctime)s %(name)s %(levelname)s %(message)s"
        )

    handler.setFormatter(formatter)

    # Configure root logger
    logging.root.handlers = [handler]
    logging.root.setLevel(log_level)

    # Suppress noisy loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
