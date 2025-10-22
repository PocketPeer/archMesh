"""
Enhanced Logger for WebSocket Service

This module provides structured logging for WebSocket operations with
performance monitoring, metrics collection, and comprehensive debugging.
"""

import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
from contextlib import asynccontextmanager

from app.core.exceptions import WebSocketError


class LogLevel(str, Enum):
    """Log levels for structured logging"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class LogCategory(str, Enum):
    """Log categories for classification"""
    CONNECTION = "connection"
    MESSAGE = "message"
    PERFORMANCE = "performance"
    ERROR = "error"
    SECURITY = "security"
    SYSTEM = "system"
    USER_ACTION = "user_action"


@dataclass
class LogContext:
    """Context information for logging"""
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    operation: Optional[str] = None
    message_type: Optional[str] = None
    workflow_id: Optional[str] = None
    project_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    additional_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LogEntry:
    """Structured log entry"""
    log_id: str
    level: LogLevel
    category: LogCategory
    message: str
    context: LogContext
    duration: Optional[float] = None
    metrics: Dict[str, Any] = field(default_factory=dict)
    stack_trace: Optional[str] = None


@dataclass
class LogMetrics:
    """Metrics for logging performance"""
    total_logs: int = 0
    logs_by_level: Dict[LogLevel, int] = field(default_factory=lambda: defaultdict(int))
    logs_by_category: Dict[LogCategory, int] = field(default_factory=lambda: defaultdict(int))
    average_log_duration: float = 0.0
    log_throughput: float = 0.0
    last_log_time: Optional[datetime] = None


class WebSocketLogger:
    """
    Enhanced logger for WebSocket operations
    
    Provides:
    - Structured logging with context
    - Performance monitoring and metrics
    - Log aggregation and analysis
    - Debugging and troubleshooting support
    - Security and audit logging
    """
    
    def __init__(self, name: str = "websocket", max_log_history: int = 10000):
        """
        Initialize WebSocket logger
        
        Args:
            name: Logger name
            max_log_history: Maximum number of logs to keep in history
        """
        self.name = name
        self.logger = logging.getLogger(name)
        self.max_log_history = max_log_history
        
        # Log storage
        self.log_history: deque = deque(maxlen=max_log_history)
        self.metrics = LogMetrics()
        self.start_time = datetime.utcnow()
        
        # Performance tracking
        self.operation_times: Dict[str, List[float]] = defaultdict(list)
        self.active_operations: Dict[str, float] = {}
        
        # Configure logger
        self._configure_logger()
    
    def _configure_logger(self):
        """Configure the logger with appropriate handlers and formatters"""
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.INFO)
        
        # File handler (optional)
        try:
            file_handler = logging.FileHandler(f'logs/{self.name}.log')
            file_handler.setFormatter(formatter)
            file_handler.setLevel(logging.DEBUG)
            self.logger.addHandler(file_handler)
        except (OSError, PermissionError):
            # If file logging fails, continue with console only
            pass
        
        self.logger.addHandler(console_handler)
        self.logger.setLevel(logging.DEBUG)
    
    def _create_log_entry(
        self,
        level: LogLevel,
        category: LogCategory,
        message: str,
        context: LogContext,
        duration: Optional[float] = None,
        metrics: Optional[Dict[str, Any]] = None,
        stack_trace: Optional[str] = None
    ) -> LogEntry:
        """Create a structured log entry"""
        log_id = f"log_{datetime.utcnow().timestamp()}_{hash(message)}"
        
        return LogEntry(
            log_id=log_id,
            level=level,
            category=category,
            message=message,
            context=context,
            duration=duration,
            metrics=metrics or {},
            stack_trace=stack_trace
        )
    
    def _log_entry(self, log_entry: LogEntry):
        """Log the entry and update metrics"""
        # Add to history
        self.log_history.append(log_entry)
        
        # Update metrics
        self.metrics.total_logs += 1
        self.metrics.logs_by_level[log_entry.level] += 1
        self.metrics.logs_by_category[log_entry.category] += 1
        self.metrics.last_log_time = log_entry.context.timestamp
        
        # Update throughput
        elapsed = (datetime.utcnow() - self.start_time).total_seconds()
        if elapsed > 0:
            self.metrics.log_throughput = self.metrics.total_logs / elapsed
        
        # Update average duration
        if log_entry.duration is not None:
            durations = [log.duration for log in self.log_history if log.duration is not None]
            if durations:
                self.metrics.average_log_duration = sum(durations) / len(durations)
        
        # Log to standard logger
        log_data = {
            "log_id": log_entry.log_id,
            "category": log_entry.category.value,
            "session_id": log_entry.context.session_id,
            "user_id": log_entry.context.user_id,
            "operation": log_entry.context.operation,
            "duration": log_entry.duration,
            "metrics": log_entry.metrics
        }
        
        # Add stack trace if present
        if log_entry.stack_trace:
            log_data["stack_trace"] = log_entry.stack_trace
        
        # Log with appropriate level
        if log_entry.level == LogLevel.DEBUG:
            self.logger.debug(f"{log_entry.message}", extra=log_data)
        elif log_entry.level == LogLevel.INFO:
            self.logger.info(f"{log_entry.message}", extra=log_data)
        elif log_entry.level == LogLevel.WARNING:
            self.logger.warning(f"{log_entry.message}", extra=log_data)
        elif log_entry.level == LogLevel.ERROR:
            self.logger.error(f"{log_entry.message}", extra=log_data)
        elif log_entry.level == LogLevel.CRITICAL:
            self.logger.critical(f"{log_entry.message}", extra=log_data)
    
    def log_connection_event(
        self,
        event: str,
        session_id: str,
        user_id: Optional[str] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ):
        """Log connection-related events"""
        context = LogContext(
            session_id=session_id,
            user_id=user_id,
            operation="connection",
            additional_data=additional_data or {}
        )
        
        log_entry = self._create_log_entry(
            level=LogLevel.INFO,
            category=LogCategory.CONNECTION,
            message=f"Connection event: {event}",
            context=context
        )
        
        self._log_entry(log_entry)
    
    def log_message_event(
        self,
        event: str,
        session_id: str,
        message_type: str,
        user_id: Optional[str] = None,
        duration: Optional[float] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ):
        """Log message-related events"""
        context = LogContext(
            session_id=session_id,
            user_id=user_id,
            operation="message",
            message_type=message_type,
            additional_data=additional_data or {}
        )
        
        log_entry = self._create_log_entry(
            level=LogLevel.INFO,
            category=LogCategory.MESSAGE,
            message=f"Message event: {event}",
            context=context,
            duration=duration
        )
        
        self._log_entry(log_entry)
    
    def log_performance_event(
        self,
        operation: str,
        duration: float,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
        metrics: Optional[Dict[str, Any]] = None
    ):
        """Log performance-related events"""
        context = LogContext(
            session_id=session_id,
            user_id=user_id,
            operation=operation
        )
        
        # Track operation times
        self.operation_times[operation].append(duration)
        
        log_entry = self._create_log_entry(
            level=LogLevel.INFO,
            category=LogCategory.PERFORMANCE,
            message=f"Performance: {operation} took {duration:.3f}s",
            context=context,
            duration=duration,
            metrics=metrics or {}
        )
        
        self._log_entry(log_entry)
    
    def log_error_event(
        self,
        error: Exception,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
        operation: Optional[str] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ):
        """Log error events"""
        context = LogContext(
            session_id=session_id,
            user_id=user_id,
            operation=operation,
            additional_data=additional_data or {}
        )
        
        # Get stack trace
        import traceback
        stack_trace = traceback.format_exc()
        
        # Determine log level based on error type
        if isinstance(error, WebSocketError):
            level = LogLevel.ERROR
        else:
            level = LogLevel.WARNING
        
        log_entry = self._create_log_entry(
            level=level,
            category=LogCategory.ERROR,
            message=f"Error: {str(error)}",
            context=context,
            stack_trace=stack_trace
        )
        
        self._log_entry(log_entry)
    
    def log_security_event(
        self,
        event: str,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ):
        """Log security-related events"""
        context = LogContext(
            session_id=session_id,
            user_id=user_id,
            operation="security",
            additional_data=additional_data or {}
        )
        
        log_entry = self._create_log_entry(
            level=LogLevel.WARNING,
            category=LogCategory.SECURITY,
            message=f"Security event: {event}",
            context=context
        )
        
        self._log_entry(log_entry)
    
    def log_user_action(
        self,
        action: str,
        session_id: str,
        user_id: str,
        workflow_id: Optional[str] = None,
        project_id: Optional[str] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ):
        """Log user actions for audit trail"""
        context = LogContext(
            session_id=session_id,
            user_id=user_id,
            operation="user_action",
            workflow_id=workflow_id,
            project_id=project_id,
            additional_data=additional_data or {}
        )
        
        log_entry = self._create_log_entry(
            level=LogLevel.INFO,
            category=LogCategory.USER_ACTION,
            message=f"User action: {action}",
            context=context
        )
        
        self._log_entry(log_entry)
    
    @asynccontextmanager
    async def log_operation(self, operation: str, session_id: Optional[str] = None, user_id: Optional[str] = None):
        """Context manager for logging operation duration"""
        start_time = time.time()
        operation_key = f"{operation}_{session_id}_{user_id}"
        
        # Track active operation
        self.active_operations[operation_key] = start_time
        
        try:
            yield
        except Exception as e:
            # Log error if operation fails
            self.log_error_event(e, session_id, user_id, operation)
            raise
        finally:
            # Calculate duration and log
            duration = time.time() - start_time
            self.log_performance_event(operation, duration, session_id, user_id)
            
            # Remove from active operations
            self.active_operations.pop(operation_key, None)
    
    def get_log_metrics(self) -> LogMetrics:
        """Get current log metrics"""
        return self.metrics
    
    def get_log_history(self, limit: int = 100, category: Optional[LogCategory] = None) -> List[LogEntry]:
        """Get recent log history"""
        logs = list(self.log_history)
        
        if category:
            logs = [log for log in logs if log.category == category]
        
        return logs[-limit:]
    
    def get_operation_metrics(self) -> Dict[str, Dict[str, float]]:
        """Get performance metrics for operations"""
        metrics = {}
        
        for operation, times in self.operation_times.items():
            if times:
                metrics[operation] = {
                    "count": len(times),
                    "average": sum(times) / len(times),
                    "min": min(times),
                    "max": max(times),
                    "total": sum(times)
                }
        
        return metrics
    
    def get_active_operations(self) -> Dict[str, float]:
        """Get currently active operations"""
        current_time = time.time()
        active = {}
        
        for operation_key, start_time in self.active_operations.items():
            duration = current_time - start_time
            active[operation_key] = duration
        
        return active
    
    def export_logs(self, format: str = "json", limit: int = 1000) -> Union[str, List[Dict[str, Any]]]:
        """Export logs in specified format"""
        logs = list(self.log_history)[-limit:]
        
        if format == "json":
            return [
                {
                    "log_id": log.log_id,
                    "level": log.level.value,
                    "category": log.category.value,
                    "message": log.message,
                    "timestamp": log.context.timestamp.isoformat(),
                    "session_id": log.context.session_id,
                    "user_id": log.context.user_id,
                    "operation": log.context.operation,
                    "duration": log.duration,
                    "metrics": log.metrics
                }
                for log in logs
            ]
        else:
            # Return as formatted string
            return "\n".join([
                f"{log.context.timestamp.isoformat()} [{log.level.value.upper()}] "
                f"[{log.category.value}] {log.message}"
                for log in logs
            ])
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on logger"""
        recent_logs = [log for log in self.log_history 
                      if datetime.utcnow() - log.context.timestamp < timedelta(minutes=5)]
        
        error_logs = [log for log in recent_logs if log.level in [LogLevel.ERROR, LogLevel.CRITICAL]]
        active_operations = self.get_active_operations()
        
        health_status = "healthy"
        if len(error_logs) > 10:
            health_status = "degraded"
        elif any(duration > 300 for duration in active_operations.values()):  # 5 minutes
            health_status = "degraded"
        
        return {
            "status": health_status,
            "total_logs": self.metrics.total_logs,
            "recent_logs": len(recent_logs),
            "error_logs": len(error_logs),
            "active_operations": len(active_operations),
            "log_throughput": self.metrics.log_throughput,
            "average_log_duration": self.metrics.average_log_duration,
            "operation_metrics": self.get_operation_metrics()
        }
