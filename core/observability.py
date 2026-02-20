"""
Observability and structured logging.

Provides injectable logging with structured events for monitoring and debugging.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from .metrics import RenderMetrics


class LogLevel(str, Enum):
    """Log levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


@dataclass
class LogEvent:
    """
    Structured log event.
    
    All events have consistent structure for parsing and monitoring.
    """

    timestamp: str
    level: LogLevel
    event_type: str
    message: str
    context: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON logging."""
        return {
            "timestamp": self.timestamp,
            "level": self.level.value,
            "event_type": self.event_type,
            "message": self.message,
            **self.context,
        }


class SpreadsheetLogger(ABC):
    """
    Abstract logger interface.
    
    Allows injection of different logging implementations
    (standard logging, structured JSON, cloud logging, etc.)
    """

    @abstractmethod
    def log(self, event: LogEvent) -> None:
        """Log an event."""
        ...

    def debug(self, event_type: str, message: str, **context):
        """Log debug event."""
        self.log(self._create_event(LogLevel.DEBUG, event_type, message, context))

    def info(self, event_type: str, message: str, **context):
        """Log info event."""
        self.log(self._create_event(LogLevel.INFO, event_type, message, context))

    def warning(self, event_type: str, message: str, **context):
        """Log warning event."""
        self.log(self._create_event(LogLevel.WARNING, event_type, message, context))

    def error(self, event_type: str, message: str, **context):
        """Log error event."""
        self.log(self._create_event(LogLevel.ERROR, event_type, message, context))

    def _create_event(
        self,
        level: LogLevel,
        event_type: str,
        message: str,
        context: Dict[str, Any],
    ) -> LogEvent:
        """Create log event with timestamp."""
        return LogEvent(
            timestamp=datetime.utcnow().isoformat(),
            level=level,
            event_type=event_type,
            message=message,
            context=context,
        )


class StandardLogger(SpreadsheetLogger):
    """
    Standard Python logging implementation.
    
    Bridges to Python's logging module with structured data.
    """

    def __init__(self, logger_name: str = "spreadsheet_engine"):
        self._logger = logging.getLogger(logger_name)

    def log(self, event: LogEvent) -> None:
        """Log event using Python logging."""
        level_map = {
            LogLevel.DEBUG: logging.DEBUG,
            LogLevel.INFO: logging.INFO,
            LogLevel.WARNING: logging.WARNING,
            LogLevel.ERROR: logging.ERROR,
        }

        log_level = level_map.get(event.level, logging.INFO)
        
        # Format: [event_type] message {context}
        extra_str = " ".join(f"{k}={v}" for k, v in event.context.items())
        log_message = f"[{event.event_type}] {event.message}"
        if extra_str:
            log_message += f" | {extra_str}"

        self._logger.log(log_level, log_message)


class NullLogger(SpreadsheetLogger):
    """
    Null logger that discards all events.
    
    Used when logging is disabled.
    """

    def log(self, event: LogEvent) -> None:
        """Discard event."""
        pass


class RenderEventLogger:
    """
    High-level logger for render events.
    
    Provides semantic methods for common events.
    """

    def __init__(self, logger: Optional[SpreadsheetLogger] = None):
        self._logger = logger or NullLogger()

    def render_started(
        self,
        report_type: str,
        template_version: str,
        format: str,
        streaming: bool,
        row_count: int,
    ):
        """Log render start."""
        self._logger.info(
            event_type="render_started",
            message=f"Starting render of {report_type}",
            report_type=report_type,
            template_version=template_version,
            format=format,
            streaming=streaming,
            estimated_rows=row_count,
        )

    def render_completed(
        self,
        report_type: str,
        metrics: RenderMetrics,
    ):
        """Log render completion."""
        self._logger.info(
            event_type="render_completed",
            message=f"Completed render of {report_type}",
            report_type=report_type,
            **metrics.to_dict(),
        )

    def render_failed(
        self,
        report_type: str,
        error: Exception,
        duration_ms: float,
    ):
        """Log render failure."""
        self._logger.error(
            event_type="render_failed",
            message=f"Render failed for {report_type}: {str(error)}",
            report_type=report_type,
            error_type=type(error).__name__,
            error_message=str(error),
            duration_ms=duration_ms,
        )

    def template_merged(
        self,
        template_name: str,
        sheet_count: int,
        table_count: int,
        duration_ms: float,
    ):
        """Log template merge."""
        self._logger.debug(
            event_type="template_merged",
            message=f"Merged template {template_name}",
            template_name=template_name,
            sheet_count=sheet_count,
            table_count=table_count,
            duration_ms=duration_ms,
        )

    def adapter_selected(
        self,
        adapter_type: str,
        format: str,
    ):
        """Log adapter selection."""
        self._logger.debug(
            event_type="adapter_selected",
            message=f"Selected adapter {adapter_type}",
            adapter_type=adapter_type,
            format=format,
        )

    def streaming_chunk_processed(
        self,
        chunk_number: int,
        rows_in_chunk: int,
        total_rows_so_far: int,
    ):
        """Log streaming chunk processing."""
        self._logger.debug(
            event_type="streaming_chunk_processed",
            message=f"Processed chunk {chunk_number}",
            chunk_number=chunk_number,
            rows_in_chunk=rows_in_chunk,
            total_rows=total_rows_so_far,
        )

    def performance_warning(
        self,
        metric_name: str,
        actual_value: float,
        threshold_value: float,
        message: str,
    ):
        """Log performance warning."""
        self._logger.warning(
            event_type="performance_warning",
            message=message,
            metric=metric_name,
            actual=actual_value,
            threshold=threshold_value,
        )

    def contract_violation(
        self,
        violations: list[str],
        metrics: RenderMetrics,
    ):
        """Log performance contract violation."""
        self._logger.warning(
            event_type="contract_violation",
            message=f"Performance contract violated: {'; '.join(violations)}",
            violations=violations,
            **metrics.to_dict(),
        )

    def deprecation_warning(
        self,
        feature: str,
        deprecated_version: str,
        removal_version: str,
        alternative: str,
    ):
        """Log deprecation warning."""
        self._logger.warning(
            event_type="deprecation_warning",
            message=f"{feature} is deprecated",
            feature=feature,
            deprecated_in=deprecated_version,
            removed_in=removal_version,
            use_instead=alternative,
        )


# Global default logger (can be overridden)
_default_logger: SpreadsheetLogger = StandardLogger()


def set_default_logger(logger: SpreadsheetLogger) -> None:
    """
    Set the default logger for all operations.
    
    Args:
        logger: Logger implementation
    """
    global _default_logger
    _default_logger = logger


def get_default_logger() -> SpreadsheetLogger:
    """Get the default logger."""
    return _default_logger


def get_render_logger(logger: Optional[SpreadsheetLogger] = None) -> RenderEventLogger:
    """
    Get a render event logger.
    
    Args:
        logger: Optional logger (uses default if None)
        
    Returns:
        RenderEventLogger instance
    """
    return RenderEventLogger(logger or _default_logger)
