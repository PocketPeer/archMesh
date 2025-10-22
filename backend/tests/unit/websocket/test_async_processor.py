"""
Tests for Async Message Processor

This module tests the high-performance async message processing
with worker pools and priority queuing.
"""

import pytest
import asyncio
import time
from datetime import datetime
from unittest.mock import AsyncMock, patch

from app.services.websocket.async_processor import (
    AsyncMessageProcessor, ProcessingTask, ProcessingPriority, WorkerState
)
from app.core.exceptions import WebSocketError


@pytest.fixture
def async_processor():
    """Create async message processor for testing"""
    return AsyncMessageProcessor(
        max_workers=5,
        queue_size=100,
        processing_timeout=10.0,
        auto_scale=False,
        min_workers=2
    )


@pytest.fixture
def sample_message():
    """Sample message for testing"""
    return {
        "type": "test_message",
        "content": "Hello, World!",
        "timestamp": datetime.utcnow().isoformat()
    }


class TestAsyncMessageProcessor:
    """Test cases for async message processor"""
    
    @pytest.mark.asyncio
    async def test_processor_startup_and_shutdown(self, async_processor):
        """Test processor startup and shutdown"""
        # Start processor
        await async_processor.start()
        assert async_processor.running is True
        assert len(async_processor.workers) == 2  # min_workers
        
        # Stop processor
        await async_processor.stop()
        assert async_processor.running is False
        assert len(async_processor.workers) == 0
    
    @pytest.mark.asyncio
    async def test_message_handler_registration(self, async_processor):
        """Test message handler registration"""
        async def test_handler(message, session_id, user_id):
            return "processed"
        
        async_processor.register_handler("test_message", test_handler)
        assert "test_message" in async_processor.message_handlers
    
    @pytest.mark.asyncio
    async def test_message_queuing(self, async_processor, sample_message):
        """Test message queuing"""
        await async_processor.start()
        
        # Queue message
        task_id = await async_processor.queue_message(
            message=sample_message,
            session_id="session-123",
            user_id="user-456",
            priority=ProcessingPriority.HIGH
        )
        
        assert task_id is not None
        assert async_processor.metrics.total_tasks == 1
        assert async_processor.metrics.queued_tasks == 1
        
        await async_processor.stop()
    
    @pytest.mark.asyncio
    async def test_priority_queuing(self, async_processor):
        """Test priority-based message queuing"""
        await async_processor.start()
        
        # Queue messages with different priorities
        messages = [
            ("low", ProcessingPriority.LOW),
            ("normal", ProcessingPriority.NORMAL),
            ("high", ProcessingPriority.HIGH),
            ("critical", ProcessingPriority.CRITICAL)
        ]
        
        task_ids = []
        for content, priority in messages:
            task_id = await async_processor.queue_message(
                message={"type": "test", "content": content},
                session_id="session-123",
                priority=priority
            )
            task_ids.append(task_id)
        
        # Check that all messages were queued
        assert len(task_ids) == 4
        assert async_processor.metrics.total_tasks == 4
        
        await async_processor.stop()
    
    @pytest.mark.asyncio
    async def test_message_processing(self, async_processor, sample_message):
        """Test message processing with handler"""
        await async_processor.start()
        
        # Register handler
        processed_messages = []
        
        async def test_handler(message, session_id, user_id):
            processed_messages.append(message)
            return "processed"
        
        async_processor.register_handler("test_message", test_handler)
        
        # Queue message
        task_id = await async_processor.queue_message(
            message=sample_message,
            session_id="session-123",
            user_id="user-456"
        )
        
        # Wait for processing
        await asyncio.sleep(0.5)
        
        # Check that message was processed
        assert len(processed_messages) == 1
        assert processed_messages[0] == sample_message
        assert async_processor.metrics.completed_tasks == 1
        
        await async_processor.stop()
    
    @pytest.mark.asyncio
    async def test_worker_creation_and_removal(self, async_processor):
        """Test worker creation and removal"""
        await async_processor.start()
        
        initial_workers = len(async_processor.workers)
        
        # Create additional worker
        await async_processor._create_worker("test-worker")
        assert len(async_processor.workers) == initial_workers + 1
        assert "test-worker" in async_processor.workers
        
        # Remove worker
        await async_processor._remove_worker("test-worker")
        assert len(async_processor.workers) == initial_workers
        assert "test-worker" not in async_processor.workers
        
        await async_processor.stop()
    
    @pytest.mark.asyncio
    async def test_processing_timeout(self, async_processor):
        """Test processing timeout handling"""
        await async_processor.start()
        
        # Register slow handler
        async def slow_handler(message, session_id, user_id):
            await asyncio.sleep(15)  # Longer than timeout
            return "processed"
        
        async_processor.register_handler("slow_message", slow_handler)
        
        # Queue message
        task_id = await async_processor.queue_message(
            message={"type": "slow_message", "content": "test"},
            session_id="session-123"
        )
        
        # Wait for timeout (need to wait longer than the timeout)
        await asyncio.sleep(12)  # Wait longer than the 10s timeout
        
        # Check that task failed due to timeout
        assert async_processor.metrics.failed_tasks == 1
        
        await async_processor.stop()
    
    @pytest.mark.asyncio
    async def test_error_handling_and_retry(self, async_processor):
        """Test error handling and retry logic"""
        await async_processor.start()
        
        # Register handler that fails
        call_count = 0
        
        async def failing_handler(message, session_id, user_id):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Test error")
            return "processed"
        
        async_processor.register_handler("failing_message", failing_handler)
        
        # Queue message
        task_id = await async_processor.queue_message(
            message={"type": "failing_message", "content": "test"},
            session_id="session-123"
        )
        
        # Wait for processing and retries (need to wait for retry delays)
        await asyncio.sleep(5)  # Wait for retry delays (1s + 2s + processing time)
        
        # Check that handler was called multiple times due to retries
        assert call_count >= 2  # At least 2 calls (initial + retry)
        assert async_processor.metrics.completed_tasks == 1
        
        await async_processor.stop()
    
    @pytest.mark.asyncio
    async def test_worker_metrics(self, async_processor, sample_message):
        """Test worker metrics collection"""
        await async_processor.start()
        
        # Register handler
        async def test_handler(message, session_id, user_id):
            await asyncio.sleep(0.1)  # Simulate work
            return "processed"
        
        async_processor.register_handler("test_message", test_handler)
        
        # Queue message
        await async_processor.queue_message(
            message=sample_message,
            session_id="session-123"
        )
        
        # Wait for processing
        await asyncio.sleep(0.5)
        
        # Check worker metrics
        worker_metrics = async_processor.get_worker_metrics()
        assert len(worker_metrics) > 0
        
        for worker_id, metrics in worker_metrics.items():
            assert metrics.tasks_processed >= 0
            assert metrics.average_processing_time >= 0
        
        await async_processor.stop()
    
    @pytest.mark.asyncio
    async def test_queue_status(self, async_processor):
        """Test queue status reporting"""
        await async_processor.start()
        
        # Queue messages with different priorities
        for priority in ProcessingPriority:
            await async_processor.queue_message(
                message={"type": "test", "priority": priority.value},
                session_id="session-123",
                priority=priority
            )
        
        # Get queue status
        status = async_processor.get_queue_status()
        
        assert "critical_queue_size" in status
        assert "high_queue_size" in status
        assert "normal_queue_size" in status
        assert "low_queue_size" in status
        assert "total_queue_size" in status
        assert "active_workers" in status
        assert "idle_workers" in status
        
        await async_processor.stop()
    
    @pytest.mark.asyncio
    async def test_processing_metrics(self, async_processor, sample_message):
        """Test processing metrics collection"""
        await async_processor.start()
        
        # Register handler
        async def test_handler(message, session_id, user_id):
            await asyncio.sleep(0.1)
            return "processed"
        
        async_processor.register_handler("test_message", test_handler)
        
        # Queue multiple messages
        for i in range(5):
            await async_processor.queue_message(
                message={**sample_message, "id": i},
                session_id=f"session-{i}"
            )
        
        # Wait for processing
        await asyncio.sleep(1)
        
        # Check metrics
        metrics = async_processor.get_metrics()
        
        assert metrics.total_tasks == 5
        assert metrics.completed_tasks == 5
        assert metrics.average_processing_time > 0
        assert metrics.throughput_per_second > 0
        
        await async_processor.stop()
    
    @pytest.mark.asyncio
    async def test_health_check(self, async_processor):
        """Test health check functionality"""
        await async_processor.start()
        
        # Perform health check
        health = await async_processor.health_check()
        
        assert "status" in health
        assert "uptime" in health
        assert "queue_status" in health
        assert "metrics" in health
        assert "worker_metrics" in health
        assert "configuration" in health
        
        assert health["status"] in ["healthy", "degraded", "critical"]
        assert health["uptime"] >= 0
        
        await async_processor.stop()
    
    @pytest.mark.asyncio
    async def test_callback_execution(self, async_processor, sample_message):
        """Test callback execution after message processing"""
        await async_processor.start()
        
        # Register handler
        async def test_handler(message, session_id, user_id):
            return "processed"
        
        async_processor.register_handler("test_message", test_handler)
        
        # Track callback execution
        callback_executed = False
        callback_task = None
        callback_time = None
        
        async def test_callback(task, processing_time):
            nonlocal callback_executed, callback_task, callback_time
            callback_executed = True
            callback_task = task
            callback_time = processing_time
        
        # Queue message with callback
        task_id = await async_processor.queue_message(
            message=sample_message,
            session_id="session-123",
            callback=test_callback
        )
        
        # Wait for processing
        await asyncio.sleep(0.5)
        
        # Check callback execution
        assert callback_executed is True
        assert callback_task is not None
        assert callback_time is not None
        assert callback_time > 0
        
        await async_processor.stop()
    
    @pytest.mark.asyncio
    async def test_concurrent_processing(self, async_processor):
        """Test concurrent message processing"""
        await async_processor.start()
        
        # Register handler
        processed_count = 0
        
        async def test_handler(message, session_id, user_id):
            nonlocal processed_count
            await asyncio.sleep(0.1)  # Simulate work
            processed_count += 1
            return "processed"
        
        async_processor.register_handler("test_message", test_handler)
        
        # Queue multiple messages concurrently
        tasks = []
        for i in range(10):
            task = async_processor.queue_message(
                message={"type": "test_message", "id": i},
                session_id=f"session-{i}"
            )
            tasks.append(task)
        
        await asyncio.gather(*tasks)
        
        # Wait for processing
        await asyncio.sleep(1)
        
        # Check that all messages were processed
        assert processed_count == 10
        assert async_processor.metrics.completed_tasks == 10
        
        await async_processor.stop()
    
    @pytest.mark.asyncio
    async def test_worker_state_management(self, async_processor, sample_message):
        """Test worker state management"""
        await async_processor.start()
        
        # Register handler
        async def test_handler(message, session_id, user_id):
            await asyncio.sleep(0.1)
            return "processed"
        
        async_processor.register_handler("test_message", test_handler)
        
        # Queue message
        await async_processor.queue_message(
            message=sample_message,
            session_id="session-123"
        )
        
        # Wait for processing
        await asyncio.sleep(0.5)
        
        # Check worker states
        for worker_id, state in async_processor.worker_states.items():
            assert state in [WorkerState.IDLE, WorkerState.BUSY, WorkerState.ERROR]
        
        await async_processor.stop()
    
    @pytest.mark.asyncio
    async def test_queue_full_handling(self, async_processor):
        """Test queue full handling"""
        # Create processor with small queue
        small_processor = AsyncMessageProcessor(
            max_workers=1,
            queue_size=2,
            auto_scale=False,
            min_workers=1
        )
        
        await small_processor.start()
        
        # Fill up the queue
        for i in range(2):
            await small_processor.queue_message(
                message={"type": "test", "id": i},
                session_id=f"session-{i}"
            )
        
        # Try to queue one more message (should fail)
        with pytest.raises(WebSocketError):
            await small_processor.queue_message(
                message={"type": "test", "id": 3},
                session_id="session-3"
            )
        
        await small_processor.stop()
