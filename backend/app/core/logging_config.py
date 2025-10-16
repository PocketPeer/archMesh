"""
Structured logging configuration using loguru.

This module configures structured logging with JSON formatting for production
and colored console output for development.
"""

import sys
from pathlib import Path
from typing import Dict, Any

from loguru import logger

from app.config import settings


def setup_logging() -> None:
    """
    Configure structured logging with loguru.
    
    Sets up logging with different formats for development and production,
    including file rotation and structured JSON output.
    """
    # Remove default logger
    logger.remove()
    
    # Console logging
    if settings.is_development:
        # Colored console output for development
        logger.add(
            sys.stdout,
            format=settings.log_format,
            level=settings.log_level,
            colorize=True,
            backtrace=True,
            diagnose=True,
        )
    else:
        # Structured JSON output for production
        logger.add(
            sys.stdout,
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {name}:{function}:{line} | {message}",
            level=settings.log_level,
            serialize=True,  # JSON output
            backtrace=False,
            diagnose=False,
        )
    
    # File logging with rotation
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logger.add(
        log_dir / "app.log",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {name}:{function}:{line} | {message}",
        level=settings.log_level,
        rotation="100 MB",
        retention="30 days",
        compression="zip",
        backtrace=True,
        diagnose=True,
    )
    
    # Error file logging
    logger.add(
        log_dir / "error.log",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {name}:{function}:{line} | {message}",
        level="ERROR",
        rotation="50 MB",
        retention="90 days",
        compression="zip",
        backtrace=True,
        diagnose=True,
    )


def get_logger(name: str) -> Any:
    """
    Get logger instance for a specific module.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Logger instance
        
    Example:
        ```python
        from app.core.logging_config import get_logger
        
        logger = get_logger(__name__)
        logger.info("Application started")
        ```
    """
    return logger.bind(name=name)


class LoggerMixin:
    """
    Mixin class to add logging capabilities to any class.
    
    Provides a logger property that returns a logger bound to the class name.
    """
    
    @property
    def logger(self) -> Any:
        """Get logger instance for this class."""
        return get_logger(self.__class__.__name__)


def log_function_call(func_name: str, **kwargs: Any) -> None:
    """
    Log function call with parameters.
    
    Args:
        func_name: Name of the function being called
        **kwargs: Function parameters to log
    """
    logger.debug(f"Calling {func_name}", extra={"function": func_name, "params": kwargs})


def log_function_result(func_name: str, result: Any, **kwargs: Any) -> None:
    """
    Log function result.
    
    Args:
        func_name: Name of the function that was called
        result: Function result
        **kwargs: Additional context
    """
    logger.debug(
        f"Function {func_name} completed",
        extra={"function": func_name, "result": str(result)[:200], **kwargs}
    )


def log_error(error: Exception, context: Dict[str, Any] = None) -> None:
    """
    Log error with context.
    
    Args:
        error: Exception instance
        context: Additional context information
    """
    logger.error(
        f"Error occurred: {str(error)}",
        extra={"error_type": type(error).__name__, "context": context or {}},
        exc_info=True,
    )


# Initialize logging when module is imported
setup_logging()
