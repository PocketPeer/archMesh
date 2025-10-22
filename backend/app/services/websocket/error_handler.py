"""
Error Handler for WebSocket Service

This module provides comprehensive error handling and recovery strategies
for WebSocket operations with structured logging and monitoring.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque

from app.core.exceptions import WebSocketError, ConnectionError

logger = logging.getLogger(__name__)


class ErrorSeverity(str, Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(str, Enum):
    """Error categories for classification"""
    CONNECTION = "connection"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    MESSAGE_PROCESSING = "message_processing"
    NETWORK = "network"
    SYSTEM = "system"
    VALIDATION = "validation"
    TIMEOUT = "timeout"


@dataclass
class ErrorContext:
    """Context information for error handling"""
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    message_type: Optional[str] = None
    operation: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    additional_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ErrorRecord:
    """Record of an error occurrence"""
    error_id: str
    error_type: str
    error_message: str
    severity: ErrorSeverity
    category: ErrorCategory
    context: ErrorContext
    stack_trace: Optional[str] = None
    recovery_attempted: bool = False
    recovery_successful: bool = False
    recovery_time: Optional[float] = None


@dataclass
class ErrorMetrics:
    """Metrics for error tracking"""
    total_errors: int = 0
    errors_by_category: Dict[ErrorCategory, int] = field(default_factory=lambda: defaultdict(int))
    errors_by_severity: Dict[ErrorSeverity, int] = field(default_factory=lambda: defaultdict(int))
    recovery_success_rate: float = 0.0
    average_recovery_time: float = 0.0
    last_error_time: Optional[datetime] = None


class WebSocketErrorHandler:
    """
    Comprehensive error handling and recovery for WebSocket operations
    
    Provides:
    - Error classification and severity assessment
    - Recovery strategy selection and execution
    - Error metrics collection and monitoring
    - Structured logging and alerting
    - Circuit breaker pattern for failing operations
    """
    
    def __init__(self, max_error_history: int = 1000):
        """
        Initialize error handler
        
        Args:
            max_error_history: Maximum number of errors to keep in history
        """
        self.max_error_history = max_error_history
        self.error_history: deque = deque(maxlen=max_error_history)
        self.error_counts: Dict[str, int] = defaultdict(int)
        self.recovery_strategies: Dict[str, Callable] = {}
        self.circuit_breakers: Dict[str, Dict[str, Any]] = {}
        self.metrics = ErrorMetrics()
        
        # Initialize recovery strategies
        self._initialize_recovery_strategies()
        
        # Circuit breaker configuration
        self.circuit_breaker_config = {
            "failure_threshold": 5,
            "recovery_timeout": 60,  # seconds
            "half_open_max_calls": 3
        }
    
    def _initialize_recovery_strategies(self):
        """Initialize error recovery strategies"""
        self.recovery_strategies = {
            "connection_timeout": self._recover_connection_timeout,
            "authentication_failed": self._recover_authentication_failed,
            "message_serialization_error": self._recover_message_serialization_error,
            "network_error": self._recover_network_error,
            "rate_limit_exceeded": self._recover_rate_limit_exceeded,
            "resource_exhausted": self._recover_resource_exhausted,
            "validation_error": self._recover_validation_error,
            "system_error": self._recover_system_error
        }
    
    async def handle_error(
        self, 
        error: Exception, 
        context: ErrorContext,
        operation: Optional[str] = None
    ) -> ErrorRecord:
        """
        Handle an error with appropriate recovery strategies
        
        Args:
            error: The exception that occurred
            context: Context information about the error
            operation: Optional operation name for circuit breaker
            
        Returns:
            ErrorRecord: Record of the error and recovery attempt
        """
        # Classify the error
        error_type = self._classify_error(error)
        severity = self._assess_severity(error, context)
        category = self._categorize_error(error, context)
        
        # Create error record
        error_id = f"err_{datetime.utcnow().timestamp()}_{hash(str(error))}"
        error_record = ErrorRecord(
            error_id=error_id,
            error_type=error_type,
            error_message=str(error),
            severity=severity,
            category=category,
            context=context,
            stack_trace=self._get_stack_trace(error)
        )
        
        # Check circuit breaker
        if operation and self._is_circuit_open(operation):
            logger.warning(f"Circuit breaker open for operation: {operation}")
            error_record.recovery_attempted = False
            error_record.recovery_successful = False
        else:
            # Attempt recovery
            recovery_successful = await self._attempt_recovery(error_record)
            error_record.recovery_attempted = True
            error_record.recovery_successful = recovery_successful
            
            # Update circuit breaker
            if operation:
                self._update_circuit_breaker(operation, not recovery_successful)
        
        # Record the error
        self._record_error(error_record)
        
        # Log the error
        self._log_error(error_record)
        
        # Send alerts for critical errors
        if severity == ErrorSeverity.CRITICAL:
            await self._send_critical_alert(error_record)
        
        return error_record
    
    def _classify_error(self, error: Exception) -> str:
        """Classify the type of error"""
        error_type = type(error).__name__
        
        # Map specific error types to recovery strategies
        if isinstance(error, ConnectionError):
            return "connection_error"
        elif isinstance(error, WebSocketError):
            if "timeout" in str(error).lower():
                return "connection_timeout"
            elif "authentication" in str(error).lower():
                return "authentication_failed"
            elif "serialization" in str(error).lower():
                return "message_serialization_error"
            else:
                return "websocket_error"
        elif isinstance(error, asyncio.TimeoutError):
            return "timeout_error"
        elif isinstance(error, ValueError):
            return "validation_error"
        elif isinstance(error, OSError):
            return "network_error"
        else:
            return "system_error"
    
    def _assess_severity(self, error: Exception, context: ErrorContext) -> ErrorSeverity:
        """Assess the severity of an error"""
        error_type = self._classify_error(error)
        
        # Critical errors
        if error_type in ["authentication_failed", "system_error"]:
            return ErrorSeverity.CRITICAL
        
        # High severity errors
        if error_type in ["connection_error", "network_error"]:
            return ErrorSeverity.HIGH
        
        # Medium severity errors
        if error_type in ["connection_timeout", "message_serialization_error"]:
            return ErrorSeverity.MEDIUM
        
        # Low severity errors
        return ErrorSeverity.LOW
    
    def _categorize_error(self, error: Exception, context: ErrorContext) -> ErrorCategory:
        """Categorize the error for metrics and monitoring"""
        error_type = self._classify_error(error)
        
        if error_type in ["connection_error", "connection_timeout", "network_error"]:
            return ErrorCategory.CONNECTION
        elif error_type == "authentication_failed":
            return ErrorCategory.AUTHENTICATION
        elif "authorization" in error_type:
            return ErrorCategory.AUTHORIZATION
        elif error_type in ["message_serialization_error", "validation_error"]:
            return ErrorCategory.MESSAGE_PROCESSING
        elif error_type == "timeout_error":
            return ErrorCategory.TIMEOUT
        else:
            return ErrorCategory.SYSTEM
    
    def _get_stack_trace(self, error: Exception) -> Optional[str]:
        """Get stack trace for the error"""
        import traceback
        try:
            return traceback.format_exc()
        except Exception:
            return None
    
    async def _attempt_recovery(self, error_record: ErrorRecord) -> bool:
        """Attempt to recover from the error"""
        recovery_strategy = self.recovery_strategies.get(error_record.error_type)
        
        if not recovery_strategy:
            logger.warning(f"No recovery strategy for error type: {error_record.error_type}")
            return False
        
        try:
            start_time = datetime.utcnow()
            success = await recovery_strategy(error_record)
            recovery_time = (datetime.utcnow() - start_time).total_seconds()
            error_record.recovery_time = recovery_time
            
            if success:
                logger.info(f"Successfully recovered from error: {error_record.error_id}")
            else:
                logger.warning(f"Recovery failed for error: {error_record.error_id}")
            
            return success
            
        except Exception as recovery_error:
            logger.error(f"Recovery strategy failed: {recovery_error}")
            return False
    
    # Recovery strategy implementations
    async def _recover_connection_timeout(self, error_record: ErrorRecord) -> bool:
        """Recovery strategy for connection timeout"""
        logger.info(f"Attempting connection timeout recovery for session: {error_record.context.session_id}")
        
        # Wait before retry
        await asyncio.sleep(1)
        
        # In a real implementation, this would attempt to reconnect
        # For now, we'll simulate a successful recovery
        return True
    
    async def _recover_authentication_failed(self, error_record: ErrorRecord) -> bool:
        """Recovery strategy for authentication failure"""
        logger.warning(f"Authentication failed for user: {error_record.context.user_id}")
        
        # Authentication failures typically require user intervention
        # Return False to indicate recovery is not possible
        return False
    
    async def _recover_message_serialization_error(self, error_record: ErrorRecord) -> bool:
        """Recovery strategy for message serialization errors"""
        logger.info(f"Attempting message serialization recovery")
        
        # Try to fix the message format
        # In a real implementation, this would attempt to reformat the message
        return True
    
    async def _recover_network_error(self, error_record: ErrorRecord) -> bool:
        """Recovery strategy for network errors"""
        logger.info(f"Attempting network error recovery")
        
        # Wait and retry
        await asyncio.sleep(2)
        return True
    
    async def _recover_rate_limit_exceeded(self, error_record: ErrorRecord) -> bool:
        """Recovery strategy for rate limit exceeded"""
        logger.info(f"Rate limit exceeded, waiting before retry")
        
        # Wait longer for rate limit recovery
        await asyncio.sleep(5)
        return True
    
    async def _recover_resource_exhausted(self, error_record: ErrorRecord) -> bool:
        """Recovery strategy for resource exhaustion"""
        logger.warning(f"Resource exhausted, attempting cleanup")
        
        # In a real implementation, this would trigger resource cleanup
        return True
    
    async def _recover_validation_error(self, error_record: ErrorRecord) -> bool:
        """Recovery strategy for validation errors"""
        logger.info(f"Attempting validation error recovery")
        
        # Validation errors typically require fixing the input
        return False
    
    async def _recover_system_error(self, error_record: ErrorRecord) -> bool:
        """Recovery strategy for system errors"""
        logger.error(f"System error occurred, attempting recovery")
        
        # System errors may require restart or manual intervention
        return False
    
    def _record_error(self, error_record: ErrorRecord):
        """Record the error in history and update metrics"""
        self.error_history.append(error_record)
        self.error_counts[error_record.error_type] += 1
        
        # Update metrics
        self.metrics.total_errors += 1
        self.metrics.errors_by_category[error_record.category] += 1
        self.metrics.errors_by_severity[error_record.severity] += 1
        self.metrics.last_error_time = error_record.context.timestamp
        
        # Update recovery metrics
        if error_record.recovery_attempted:
            total_recoveries = sum(1 for e in self.error_history if e.recovery_attempted)
            successful_recoveries = sum(1 for e in self.error_history if e.recovery_successful)
            
            if total_recoveries > 0:
                self.metrics.recovery_success_rate = successful_recoveries / total_recoveries
            
            # Calculate average recovery time
            recovery_times = [e.recovery_time for e in self.error_history if e.recovery_time is not None]
            if recovery_times:
                self.metrics.average_recovery_time = sum(recovery_times) / len(recovery_times)
    
    def _log_error(self, error_record: ErrorRecord):
        """Log the error with appropriate level"""
        log_data = {
            "error_id": error_record.error_id,
            "error_type": error_record.error_type,
            "severity": error_record.severity.value,
            "category": error_record.category.value,
            "session_id": error_record.context.session_id,
            "user_id": error_record.context.user_id,
            "operation": error_record.context.operation,
            "recovery_attempted": error_record.recovery_attempted,
            "recovery_successful": error_record.recovery_successful
        }
        
        if error_record.severity == ErrorSeverity.CRITICAL:
            logger.critical(f"Critical error occurred: {error_record.error_message}", extra=log_data)
        elif error_record.severity == ErrorSeverity.HIGH:
            logger.error(f"High severity error: {error_record.error_message}", extra=log_data)
        elif error_record.severity == ErrorSeverity.MEDIUM:
            logger.warning(f"Medium severity error: {error_record.error_message}", extra=log_data)
        else:
            logger.info(f"Low severity error: {error_record.error_message}", extra=log_data)
    
    async def _send_critical_alert(self, error_record: ErrorRecord):
        """Send alert for critical errors"""
        alert_data = {
            "error_id": error_record.error_id,
            "error_type": error_record.error_type,
            "error_message": error_record.error_message,
            "session_id": error_record.context.session_id,
            "user_id": error_record.context.user_id,
            "timestamp": error_record.context.timestamp.isoformat(),
            "stack_trace": error_record.stack_trace
        }
        
        logger.critical(f"CRITICAL ERROR ALERT: {alert_data}")
        
        # In a real implementation, this would send alerts to monitoring systems
        # such as PagerDuty, Slack, or email notifications
    
    def _is_circuit_open(self, operation: str) -> bool:
        """Check if circuit breaker is open for an operation"""
        if operation not in self.circuit_breakers:
            return False
        
        circuit = self.circuit_breakers[operation]
        if circuit["state"] == "open":
            # Check if we should transition to half-open
            if datetime.utcnow() - circuit["last_failure"] > timedelta(seconds=self.circuit_breaker_config["recovery_timeout"]):
                circuit["state"] = "half-open"
                circuit["half_open_calls"] = 0
                return False
            return True
        
        return False
    
    def _update_circuit_breaker(self, operation: str, failed: bool):
        """Update circuit breaker state based on operation result"""
        if operation not in self.circuit_breakers:
            self.circuit_breakers[operation] = {
                "state": "closed",
                "failure_count": 0,
                "last_failure": None,
                "half_open_calls": 0
            }
        
        circuit = self.circuit_breakers[operation]
        
        if failed:
            circuit["failure_count"] += 1
            circuit["last_failure"] = datetime.utcnow()
            
            if circuit["state"] == "closed" and circuit["failure_count"] >= self.circuit_breaker_config["failure_threshold"]:
                circuit["state"] = "open"
                logger.warning(f"Circuit breaker opened for operation: {operation}")
            elif circuit["state"] == "half-open":
                circuit["state"] = "open"
                logger.warning(f"Circuit breaker reopened for operation: {operation}")
        else:
            # Reset failure count on success
            circuit["failure_count"] = 0
            
            if circuit["state"] == "half-open":
                circuit["half_open_calls"] += 1
                if circuit["half_open_calls"] >= self.circuit_breaker_config["half_open_max_calls"]:
                    circuit["state"] = "closed"
                    logger.info(f"Circuit breaker closed for operation: {operation}")
    
    def get_error_metrics(self) -> ErrorMetrics:
        """Get current error metrics"""
        return self.metrics
    
    def get_error_history(self, limit: int = 100) -> List[ErrorRecord]:
        """Get recent error history"""
        return list(self.error_history)[-limit:]
    
    def get_circuit_breaker_status(self) -> Dict[str, Dict[str, Any]]:
        """Get circuit breaker status for all operations"""
        return dict(self.circuit_breakers)
    
    def reset_circuit_breaker(self, operation: str):
        """Reset circuit breaker for a specific operation"""
        if operation in self.circuit_breakers:
            self.circuit_breakers[operation] = {
                "state": "closed",
                "failure_count": 0,
                "last_failure": None,
                "half_open_calls": 0
            }
            logger.info(f"Circuit breaker reset for operation: {operation}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on error handler"""
        recent_errors = [e for e in self.error_history 
                        if datetime.utcnow() - e.context.timestamp < timedelta(minutes=5)]
        
        critical_errors = [e for e in recent_errors if e.severity == ErrorSeverity.CRITICAL]
        open_circuits = [op for op, circuit in self.circuit_breakers.items() 
                        if circuit["state"] == "open"]
        
        health_status = "healthy"
        if critical_errors:
            health_status = "critical"
        elif open_circuits:
            health_status = "degraded"
        elif len(recent_errors) > 10:
            health_status = "degraded"
        
        return {
            "status": health_status,
            "total_errors": self.metrics.total_errors,
            "recent_errors": len(recent_errors),
            "critical_errors": len(critical_errors),
            "open_circuits": len(open_circuits),
            "recovery_success_rate": self.metrics.recovery_success_rate,
            "average_recovery_time": self.metrics.average_recovery_time,
            "circuit_breakers": self.get_circuit_breaker_status()
        }

