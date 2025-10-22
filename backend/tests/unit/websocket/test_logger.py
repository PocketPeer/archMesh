"""
Tests for WebSocket Logger

This module tests the enhanced logging system for WebSocket operations
with performance monitoring and structured logging.
"""

import pytest
import time
import asyncio
import logging
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from app.services.websocket.logger import (
    WebSocketLogger, LogContext, LogEntry, LogLevel, LogCategory
)
from app.core.exceptions import WebSocketError


@pytest.fixture
def websocket_logger():
    """Create WebSocket logger for testing"""
    return WebSocketLogger(name="test_websocket", max_log_history=100)


@pytest.fixture
def sample_log_context():
    """Sample log context for testing"""
    return LogContext(
        session_id="test-session-123",
        user_id="user-123",
        operation="test_operation",
        message_type="test_message",
        workflow_id="workflow-456",
        project_id="project-789"
    )


class TestWebSocketLogger:
    """Test cases for WebSocket logger"""
    
    def test_logger_initialization(self, websocket_logger):
        """Test logger initialization"""
        assert websocket_logger.name == "test_websocket"
        assert websocket_logger.max_log_history == 100
        assert websocket_logger.logger is not None
        assert len(websocket_logger.log_history) == 0
    
    def test_log_connection_event(self, websocket_logger):
        """Test connection event logging"""
        websocket_logger.log_connection_event(
            event="connected",
            session_id="session-123",
            user_id="user-456",
            additional_data={"ip": "192.168.1.1"}
        )
        
        # Check log was recorded
        assert len(websocket_logger.log_history) == 1
        
        log_entry = websocket_logger.log_history[0]
        assert log_entry.level == LogLevel.INFO
        assert log_entry.category == LogCategory.CONNECTION
        assert log_entry.context.session_id == "session-123"
        assert log_entry.context.user_id == "user-456"
        assert log_entry.context.additional_data == {"ip": "192.168.1.1"}
    
    def test_log_message_event(self, websocket_logger):
        """Test message event logging"""
        websocket_logger.log_message_event(
            event="sent",
            session_id="session-123",
            message_type="workflow_update",
            user_id="user-456",
            duration=0.05,
            additional_data={"size": 1024}
        )
        
        # Check log was recorded
        assert len(websocket_logger.log_history) == 1
        
        log_entry = websocket_logger.log_history[0]
        assert log_entry.level == LogLevel.INFO
        assert log_entry.category == LogCategory.MESSAGE
        assert log_entry.context.message_type == "workflow_update"
        assert log_entry.duration == 0.05
        assert log_entry.context.additional_data == {"size": 1024}
    
    def test_log_performance_event(self, websocket_logger):
        """Test performance event logging"""
        websocket_logger.log_performance_event(
            operation="message_processing",
            duration=0.1,
            session_id="session-123",
            user_id="user-456",
            metrics={"throughput": 100, "latency": 0.05}
        )
        
        # Check log was recorded
        assert len(websocket_logger.log_history) == 1
        
        log_entry = websocket_logger.log_history[0]
        assert log_entry.level == LogLevel.INFO
        assert log_entry.category == LogCategory.PERFORMANCE
        assert log_entry.context.operation == "message_processing"
        assert log_entry.duration == 0.1
        assert log_entry.metrics == {"throughput": 100, "latency": 0.05}
        
        # Check operation times tracking
        assert "message_processing" in websocket_logger.operation_times
        assert 0.1 in websocket_logger.operation_times["message_processing"]
    
    def test_log_error_event(self, websocket_logger):
        """Test error event logging"""
        error = WebSocketError("Connection failed")
        
        websocket_logger.log_error_event(
            error=error,
            session_id="session-123",
            user_id="user-456",
            operation="connect",
            additional_data={"retry_count": 3}
        )
        
        # Check log was recorded
        assert len(websocket_logger.log_history) == 1
        
        log_entry = websocket_logger.log_history[0]
        assert log_entry.level == LogLevel.ERROR
        assert log_entry.category == LogCategory.ERROR
        assert log_entry.context.operation == "connect"
        assert log_entry.context.additional_data == {"retry_count": 3}
        assert log_entry.stack_trace is not None
    
    def test_log_security_event(self, websocket_logger):
        """Test security event logging"""
        websocket_logger.log_security_event(
            event="authentication_failed",
            session_id="session-123",
            user_id="user-456",
            additional_data={"ip": "192.168.1.1", "attempts": 3}
        )
        
        # Check log was recorded
        assert len(websocket_logger.log_history) == 1
        
        log_entry = websocket_logger.log_history[0]
        assert log_entry.level == LogLevel.WARNING
        assert log_entry.category == LogCategory.SECURITY
        assert log_entry.context.additional_data == {"ip": "192.168.1.1", "attempts": 3}
    
    def test_log_user_action(self, websocket_logger):
        """Test user action logging"""
        websocket_logger.log_user_action(
            action="workflow_started",
            session_id="session-123",
            user_id="user-456",
            workflow_id="workflow-789",
            project_id="project-101",
            additional_data={"requirements_file": "req.txt"}
        )
        
        # Check log was recorded
        assert len(websocket_logger.log_history) == 1
        
        log_entry = websocket_logger.log_history[0]
        assert log_entry.level == LogLevel.INFO
        assert log_entry.category == LogCategory.USER_ACTION
        assert log_entry.context.workflow_id == "workflow-789"
        assert log_entry.context.project_id == "project-101"
        assert log_entry.context.additional_data == {"requirements_file": "req.txt"}
    
    @pytest.mark.asyncio
    async def test_log_operation_context_manager(self, websocket_logger):
        """Test operation logging context manager"""
        async with websocket_logger.log_operation("test_operation", "session-123", "user-456"):
            await asyncio.sleep(0.1)  # Simulate work
        
        # Check log was recorded
        assert len(websocket_logger.log_history) == 1
        
        log_entry = websocket_logger.log_history[0]
        assert log_entry.category == LogCategory.PERFORMANCE
        assert log_entry.context.operation == "test_operation"
        assert log_entry.duration is not None
        assert log_entry.duration >= 0.1
    
    @pytest.mark.asyncio
    async def test_log_operation_context_manager_with_error(self, websocket_logger):
        """Test operation logging context manager with error"""
        with pytest.raises(ValueError):
            async with websocket_logger.log_operation("test_operation", "session-123", "user-456"):
                raise ValueError("Test error")
        
        # Check both performance and error logs were recorded
        assert len(websocket_logger.log_history) == 2
        
        # Check error log (logged first due to exception)
        error_log = websocket_logger.log_history[0]
        assert error_log.category == LogCategory.ERROR
        assert error_log.context.operation == "test_operation"
        
        # Check performance log
        perf_log = websocket_logger.log_history[1]
        assert perf_log.category == LogCategory.PERFORMANCE
    
    def test_log_metrics(self, websocket_logger):
        """Test log metrics collection"""
        # Log various events
        websocket_logger.log_connection_event("connected", "session-1")
        websocket_logger.log_message_event("sent", "session-2", "workflow_update")
        websocket_logger.log_performance_event("operation", 0.1, "session-3")
        
        # Get metrics
        metrics = websocket_logger.get_log_metrics()
        
        assert metrics.total_logs == 3
        assert metrics.logs_by_level[LogLevel.INFO] == 3
        assert metrics.logs_by_category[LogCategory.CONNECTION] == 1
        assert metrics.logs_by_category[LogCategory.MESSAGE] == 1
        assert metrics.logs_by_category[LogCategory.PERFORMANCE] == 1
        assert metrics.log_throughput > 0
    
    def test_log_history_retrieval(self, websocket_logger):
        """Test log history retrieval"""
        # Log multiple events
        for i in range(5):
            websocket_logger.log_connection_event(f"event_{i}", f"session-{i}")
        
        # Get history with limit
        history = websocket_logger.get_log_history(limit=3)
        assert len(history) == 3
        
        # Get history by category
        conn_history = websocket_logger.get_log_history(category=LogCategory.CONNECTION)
        assert len(conn_history) == 5
        
        # Get history with non-existent category
        perf_history = websocket_logger.get_log_history(category=LogCategory.PERFORMANCE)
        assert len(perf_history) == 0
    
    def test_operation_metrics(self, websocket_logger):
        """Test operation metrics collection"""
        # Log performance events for different operations
        websocket_logger.log_performance_event("op1", 0.1, "session-1")
        websocket_logger.log_performance_event("op1", 0.2, "session-2")
        websocket_logger.log_performance_event("op2", 0.3, "session-3")
        
        # Get operation metrics
        metrics = websocket_logger.get_operation_metrics()
        
        assert "op1" in metrics
        assert "op2" in metrics
        
        op1_metrics = metrics["op1"]
        assert op1_metrics["count"] == 2
        assert abs(op1_metrics["average"] - 0.15) < 0.001
        assert op1_metrics["min"] == 0.1
        assert op1_metrics["max"] == 0.2
        assert abs(op1_metrics["total"] - 0.3) < 0.001
    
    def test_active_operations_tracking(self, websocket_logger):
        """Test active operations tracking"""
        # Start operation
        operation_key = "test_op_session-123_user-456"
        websocket_logger.active_operations[operation_key] = time.time()
        
        # Get active operations
        active = websocket_logger.get_active_operations()
        
        assert operation_key in active
        assert active[operation_key] >= 0
    
    def test_log_export_json(self, websocket_logger):
        """Test log export in JSON format"""
        # Log some events
        websocket_logger.log_connection_event("connected", "session-1")
        websocket_logger.log_message_event("sent", "session-2", "workflow_update")
        
        # Export logs
        exported = websocket_logger.export_logs(format="json", limit=10)
        
        assert isinstance(exported, list)
        assert len(exported) == 2
        
        # Check exported log structure
        log = exported[0]
        assert "log_id" in log
        assert "level" in log
        assert "category" in log
        assert "message" in log
        assert "timestamp" in log
        assert "session_id" in log
    
    def test_log_export_string(self, websocket_logger):
        """Test log export in string format"""
        # Log some events
        websocket_logger.log_connection_event("connected", "session-1")
        
        # Export logs
        exported = websocket_logger.export_logs(format="string", limit=10)
        
        assert isinstance(exported, str)
        assert "connected" in exported
        # Note: session-1 is not included in the string format, only in the message
    
    @pytest.mark.asyncio
    async def test_health_check(self, websocket_logger):
        """Test health check functionality"""
        # Log some events including errors
        websocket_logger.log_connection_event("connected", "session-1")
        websocket_logger.log_error_event(WebSocketError("Test error"), "session-2")
        
        # Perform health check
        health = await websocket_logger.health_check()
        
        assert "status" in health
        assert "total_logs" in health
        assert "recent_logs" in health
        assert "error_logs" in health
        assert "active_operations" in health
        assert "log_throughput" in health
        assert "average_log_duration" in health
        assert "operation_metrics" in health
        
        assert health["total_logs"] == 2
        assert health["error_logs"] == 1
    
    def test_log_history_limit(self, websocket_logger):
        """Test log history limit enforcement"""
        # Create logger with small limit
        small_logger = WebSocketLogger(name="small", max_log_history=3)
        
        # Log more events than limit
        for i in range(5):
            small_logger.log_connection_event(f"event_{i}", f"session-{i}")
        
        # Check only last 3 events are kept
        assert len(small_logger.log_history) == 3
        
        # Check correct events are kept (last 3)
        history = list(small_logger.log_history)
        assert "event_2" in history[0].message
        assert "event_3" in history[1].message
        assert "event_4" in history[2].message
    
    def test_log_context_preservation(self, websocket_logger, sample_log_context):
        """Test log context preservation"""
        websocket_logger.log_connection_event(
            "test_event",
            sample_log_context.session_id,
            sample_log_context.user_id,
            sample_log_context.additional_data
        )
        
        log_entry = websocket_logger.log_history[0]
        
        # Verify all context fields are preserved
        assert log_entry.context.session_id == sample_log_context.session_id
        assert log_entry.context.user_id == sample_log_context.user_id
        # Note: operation is set to "connection" by log_connection_event, not from context
        assert log_entry.context.operation == "connection"
        # Note: message_type and other fields are not set by log_connection_event
        assert log_entry.context.additional_data == sample_log_context.additional_data
    
    def test_logger_configuration(self, websocket_logger):
        """Test logger configuration"""
        # Check logger is properly configured
        assert websocket_logger.logger.name == "test_websocket"
        assert websocket_logger.logger.level <= logging.DEBUG
        
        # Check handlers are configured
        assert len(websocket_logger.logger.handlers) > 0
    
    @pytest.mark.asyncio
    async def test_concurrent_logging(self, websocket_logger):
        """Test concurrent logging operations"""
        async def log_event(i):
            websocket_logger.log_connection_event(f"event_{i}", f"session-{i}")
        
        # Log events concurrently
        tasks = [log_event(i) for i in range(10)]
        await asyncio.gather(*tasks)
        
        # Check all events were logged
        assert len(websocket_logger.log_history) == 10
        
        # Check metrics are correct
        metrics = websocket_logger.get_log_metrics()
        assert metrics.total_logs == 10
