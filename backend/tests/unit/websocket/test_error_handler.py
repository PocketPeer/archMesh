"""
Tests for WebSocket Error Handler

This module tests the comprehensive error handling and recovery strategies
for WebSocket operations.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch

from app.services.websocket.error_handler import (
    WebSocketErrorHandler, ErrorContext, ErrorRecord, ErrorSeverity, ErrorCategory
)
from app.core.exceptions import WebSocketError, ConnectionError


@pytest.fixture
def error_handler():
    """Create error handler for testing"""
    return WebSocketErrorHandler(max_error_history=100)


@pytest.fixture
def sample_error_context():
    """Sample error context for testing"""
    return ErrorContext(
        session_id="test-session-123",
        user_id="user-123",
        operation="test_operation",
        message_type="test_message"
    )


class TestWebSocketErrorHandler:
    """Test cases for WebSocket error handler"""
    
    @pytest.mark.asyncio
    async def test_error_classification(self, error_handler):
        """Test error classification"""
        # Test WebSocket error classification
        ws_error = WebSocketError("Connection timeout")
        error_type = error_handler._classify_error(ws_error)
        assert error_type == "connection_timeout"
        
        # Test connection error classification
        conn_error = ConnectionError("Connection failed")
        error_type = error_handler._classify_error(conn_error)
        assert error_type == "connection_error"
        
        # Test timeout error classification
        timeout_error = asyncio.TimeoutError()
        error_type = error_handler._classify_error(timeout_error)
        assert error_type == "timeout_error"
    
    @pytest.mark.asyncio
    async def test_severity_assessment(self, error_handler, sample_error_context):
        """Test error severity assessment"""
        # Test critical error severity
        auth_error = WebSocketError("Authentication failed")
        severity = error_handler._assess_severity(auth_error, sample_error_context)
        assert severity == ErrorSeverity.CRITICAL
        
        # Test high severity error
        conn_error = ConnectionError("Connection failed")
        severity = error_handler._assess_severity(conn_error, sample_error_context)
        assert severity == ErrorSeverity.HIGH
        
        # Test medium severity error
        timeout_error = WebSocketError("Connection timeout")
        severity = error_handler._assess_severity(timeout_error, sample_error_context)
        assert severity == ErrorSeverity.MEDIUM
    
    @pytest.mark.asyncio
    async def test_error_categorization(self, error_handler, sample_error_context):
        """Test error categorization"""
        # Test connection error category
        conn_error = ConnectionError("Connection failed")
        category = error_handler._categorize_error(conn_error, sample_error_context)
        assert category == ErrorCategory.CONNECTION
        
        # Test authentication error category
        auth_error = WebSocketError("Authentication failed")
        category = error_handler._categorize_error(auth_error, sample_error_context)
        assert category == ErrorCategory.AUTHENTICATION
        
        # Test timeout error category
        timeout_error = asyncio.TimeoutError()
        category = error_handler._categorize_error(timeout_error, sample_error_context)
        assert category == ErrorCategory.TIMEOUT
    
    @pytest.mark.asyncio
    async def test_error_handling(self, error_handler, sample_error_context):
        """Test error handling with recovery"""
        # Test connection timeout error handling
        timeout_error = WebSocketError("Connection timeout")
        error_record = await error_handler.handle_error(timeout_error, sample_error_context)
        
        assert error_record.error_type == "connection_timeout"
        assert error_record.severity == ErrorSeverity.MEDIUM
        assert error_record.category == ErrorCategory.CONNECTION
        assert error_record.recovery_attempted is True
        assert error_record.recovery_successful is True
    
    @pytest.mark.asyncio
    async def test_authentication_error_handling(self, error_handler, sample_error_context):
        """Test authentication error handling"""
        auth_error = WebSocketError("Authentication failed")
        error_record = await error_handler.handle_error(auth_error, sample_error_context)
        
        assert error_record.error_type == "authentication_failed"
        assert error_record.severity == ErrorSeverity.CRITICAL
        assert error_record.category == ErrorCategory.AUTHENTICATION
        assert error_record.recovery_attempted is True
        assert error_record.recovery_successful is False  # Auth errors can't be auto-recovered
    
    @pytest.mark.asyncio
    async def test_error_metrics(self, error_handler, sample_error_context):
        """Test error metrics collection"""
        # Handle multiple errors
        errors = [
            WebSocketError("Connection timeout"),
            ConnectionError("Connection failed"),
            WebSocketError("Authentication failed")
        ]
        
        for error in errors:
            await error_handler.handle_error(error, sample_error_context)
        
        metrics = error_handler.get_error_metrics()
        
        assert metrics.total_errors == 3
        assert metrics.errors_by_severity[ErrorSeverity.CRITICAL] == 1
        assert metrics.errors_by_severity[ErrorSeverity.HIGH] == 1
        assert metrics.errors_by_severity[ErrorSeverity.MEDIUM] == 1
        assert metrics.errors_by_category[ErrorCategory.CONNECTION] == 2
        assert metrics.errors_by_category[ErrorCategory.AUTHENTICATION] == 1
    
    @pytest.mark.asyncio
    async def test_circuit_breaker(self, error_handler, sample_error_context):
        """Test circuit breaker functionality"""
        operation = "test_operation"
        
        # Simulate multiple failures
        for _ in range(6):  # More than failure threshold (5)
            error = WebSocketError("Test error")
            await error_handler.handle_error(error, sample_error_context, operation)
        
        # Check circuit breaker status
        status = error_handler.get_circuit_breaker_status()
        assert operation in status
        assert status[operation]["state"] == "open"
        
        # Test circuit breaker blocking
        error = WebSocketError("Test error")
        error_record = await error_handler.handle_error(error, sample_error_context, operation)
        assert error_record.recovery_attempted is False  # Should be blocked by circuit breaker
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_recovery(self, error_handler, sample_error_context):
        """Test circuit breaker recovery"""
        operation = "test_operation"
        
        # Open circuit breaker
        for _ in range(6):
            error = WebSocketError("Test error")
            await error_handler.handle_error(error, sample_error_context, operation)
        
        # Wait for recovery timeout (mock time)
        with patch('app.services.websocket.error_handler.datetime') as mock_datetime:
            mock_datetime.utcnow.return_value = datetime.utcnow() + timedelta(seconds=61)
            
            # Try operation again - should transition to half-open
            error = WebSocketError("Test error")
            error_record = await error_handler.handle_error(error, sample_error_context, operation)
            assert error_record.recovery_attempted is True
    
    @pytest.mark.asyncio
    async def test_error_history(self, error_handler, sample_error_context):
        """Test error history tracking"""
        # Handle multiple errors
        errors = [
            WebSocketError("Error 1"),
            ConnectionError("Error 2"),
            WebSocketError("Error 3")
        ]
        
        for error in errors:
            await error_handler.handle_error(error, sample_error_context)
        
        # Get error history
        history = error_handler.get_error_history(limit=10)
        assert len(history) == 3
        
        # Check error records
        assert history[0].error_message == "Error 1"
        assert history[1].error_message == "Error 2"
        assert history[2].error_message == "Error 3"
    
    @pytest.mark.asyncio
    async def test_recovery_strategies(self, error_handler, sample_error_context):
        """Test recovery strategy execution"""
        # Test connection timeout recovery
        timeout_error = WebSocketError("Connection timeout")
        error_record = await error_handler.handle_error(timeout_error, sample_error_context)
        assert error_record.recovery_successful is True
        
        # Test message serialization recovery
        serialization_error = WebSocketError("Message serialization failed")
        error_record = await error_handler.handle_error(serialization_error, sample_error_context)
        assert error_record.recovery_successful is True
        
        # Test network error recovery
        network_error = OSError("Network error")
        error_record = await error_handler.handle_error(network_error, sample_error_context)
        assert error_record.recovery_successful is True
    
    @pytest.mark.asyncio
    async def test_critical_error_alerting(self, error_handler, sample_error_context):
        """Test critical error alerting"""
        with patch.object(error_handler, '_send_critical_alert', new_callable=AsyncMock) as mock_alert:
            # Handle critical error
            auth_error = WebSocketError("Authentication failed")
            await error_handler.handle_error(auth_error, sample_error_context)
            
            # Verify alert was sent
            mock_alert.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_health_check(self, error_handler, sample_error_context):
        """Test health check functionality"""
        # Handle some errors
        for _ in range(3):
            error = WebSocketError("Test error")
            await error_handler.handle_error(error, sample_error_context)
        
        # Perform health check
        health = await error_handler.health_check()
        
        assert "status" in health
        assert "total_errors" in health
        assert "recent_errors" in health
        assert "critical_errors" in health
        assert "open_circuits" in health
        assert "recovery_success_rate" in health
        assert "average_recovery_time" in health
        assert "circuit_breakers" in health
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_reset(self, error_handler, sample_error_context):
        """Test circuit breaker reset"""
        operation = "test_operation"
        
        # Open circuit breaker
        for _ in range(6):
            error = WebSocketError("Test error")
            await error_handler.handle_error(error, sample_error_context, operation)
        
        # Reset circuit breaker
        error_handler.reset_circuit_breaker(operation)
        
        # Check circuit breaker status
        status = error_handler.get_circuit_breaker_status()
        assert status[operation]["state"] == "closed"
        assert status[operation]["failure_count"] == 0
    
    @pytest.mark.asyncio
    async def test_recovery_time_tracking(self, error_handler, sample_error_context):
        """Test recovery time tracking"""
        # Handle error with recovery
        timeout_error = WebSocketError("Connection timeout")
        error_record = await error_handler.handle_error(timeout_error, sample_error_context)
        
        # Check recovery time was recorded
        assert error_record.recovery_time is not None
        assert error_record.recovery_time > 0
        
        # Check metrics
        metrics = error_handler.get_error_metrics()
        assert metrics.average_recovery_time > 0
    
    @pytest.mark.asyncio
    async def test_error_context_preservation(self, error_handler):
        """Test error context preservation"""
        context = ErrorContext(
            session_id="session-123",
            user_id="user-456",
            operation="test_op",
            message_type="test_msg",
            additional_data={"key": "value"}
        )
        
        error = WebSocketError("Test error")
        error_record = await error_handler.handle_error(error, context)
        
        # Verify context was preserved
        assert error_record.context.session_id == "session-123"
        assert error_record.context.user_id == "user-456"
        assert error_record.context.operation == "test_op"
        assert error_record.context.message_type == "test_msg"
        assert error_record.context.additional_data == {"key": "value"}
    
    @pytest.mark.asyncio
    async def test_stack_trace_capture(self, error_handler, sample_error_context):
        """Test stack trace capture"""
        try:
            raise ValueError("Test error with stack trace")
        except ValueError as e:
            error_record = await error_handler.handle_error(e, sample_error_context)
            
            # Check stack trace was captured
            assert error_record.stack_trace is not None
            assert "ValueError: Test error with stack trace" in error_record.stack_trace
    
    @pytest.mark.asyncio
    async def test_error_handler_initialization(self):
        """Test error handler initialization"""
        handler = WebSocketErrorHandler(max_error_history=500)
        
        assert handler.max_error_history == 500
        assert len(handler.recovery_strategies) > 0
        assert handler.circuit_breaker_config["failure_threshold"] == 5
        assert handler.circuit_breaker_config["recovery_timeout"] == 60

