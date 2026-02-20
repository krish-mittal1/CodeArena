"""
Production-grade structured logging with correlation IDs.

Uses contextvars for async-safe correlation ID storage.
All log records automatically include correlation_id (defaults to "-").
"""

import logging
import contextvars
from typing import Optional

# Context variable for correlation ID (async-safe)
_correlation_id: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "correlation_id", default=None
)


def get_correlation_id() -> str:
    """Get current correlation ID from context, or "-" if not set."""
    return _correlation_id.get() or "-"


def set_correlation_id(correlation_id: str) -> None:
    """Set correlation ID in current context."""
    _correlation_id.set(correlation_id)


class CorrelationIDFilter(logging.Filter):
    """
    Logging filter that ALWAYS injects correlation_id into log records.
    
    PRODUCTION: Ensures no formatting errors can occur.
    Defaults to "-" if correlation_id is not set in context.
    """
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Inject correlation_id into log record."""
        # Always set correlation_id - never leave it missing
        record.correlation_id = get_correlation_id()
        return True


def setup_logging() -> None:
    """
    Configure structured logging with correlation ID support.
    
    PRODUCTION: Called once at startup, before any logs are created.
    Ensures ALL log records (including uvicorn, background tasks) have correlation_id.
    """
    # Remove any existing handlers to avoid duplicates
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create console handler with structured format
    console_handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] [%(correlation_id)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(formatter)
    
    # Add correlation ID filter (must be added to handler, not logger)
    correlation_filter = CorrelationIDFilter()
    console_handler.addFilter(correlation_filter)
    
    # Configure root logger
    root_logger.addHandler(console_handler)
    root_logger.setLevel(logging.INFO)
    
    # Suppress noisy loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
