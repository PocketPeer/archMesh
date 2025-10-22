"""
Message Processor for WebSocket Service

This module provides optimized message processing with batching, queuing,
and performance optimization for WebSocket communications.
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass, field
from collections import defaultdict, deque
from enum import Enum

from app.schemas.websocket import WebSocketMessage, WorkflowUpdate, NotificationMessage
from app.core.exceptions import WebSocketError

logger = logging.getLogger(__name__)


class MessagePriority(str, Enum):
    """Message priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ProcessedMessage:
    """Processed message with metadata"""
    message: Dict[str, Any]
    session_id: str
    user_id: Optional[str]
    priority: MessagePriority
    timestamp: datetime
    processing_time: float = 0.0
    retry_count: int = 0
    max_retries: int = 3


@dataclass
class MessageProcessorMetrics:
    """Metrics for message processor performance"""
    total_messages: int = 0
    processed_messages: int = 0
    failed_messages: int = 0
    average_processing_time: float = 0.0
    messages_per_second: float = 0.0
    queue_size: int = 0
    batch_size: int = 0
    last_processed: datetime = field(default_factory=datetime.utcnow)


class MessageProcessor:
    """
    Optimized message processor with batching and queuing
    
    Provides efficient message processing with:
    - Message batching for improved throughput
    - Priority-based message queuing
    - Async processing with worker pools
    - Performance metrics and monitoring
    - Error handling and retry logic
    """
    
    def __init__(
        self,
        batch_size: int = 100,
        max_workers: int = 10,
        queue_size: int = 10000,
        processing_timeout: float = 30.0
    ):
        """
        Initialize message processor
        
        Args:
            batch_size: Maximum number of messages to process in a batch
            max_workers: Maximum number of worker tasks
            queue_size: Maximum queue size
            processing_timeout: Timeout for message processing
        """
        self.batch_size = batch_size
        self.max_workers = max_workers
        self.queue_size = queue_size
        self.processing_timeout = processing_timeout
        
        # Message queues by priority
        self.message_queues = {
            MessagePriority.CRITICAL: asyncio.Queue(maxsize=queue_size),
            MessagePriority.HIGH: asyncio.Queue(maxsize=queue_size),
            MessagePriority.NORMAL: asyncio.Queue(maxsize=queue_size),
            MessagePriority.LOW: asyncio.Queue(maxsize=queue_size)
        }
        
        # Processing state
        self.workers: List[asyncio.Task] = []
        self.running = False
        self.processing_times: deque = deque(maxlen=1000)
        
        # Metrics
        self.metrics = MessageProcessorMetrics()
        self.start_time = datetime.utcnow()
        
        # Message handlers
        self.message_handlers: Dict[str, Callable] = {}
        
        # Retry logic
        self.retry_delays = [1, 2, 5, 10, 30]  # seconds
    
    async def start(self):
        """Start the message processor with worker tasks"""
        if self.running:
            return
        
        self.running = True
        self.start_time = datetime.utcnow()
        
        # Start worker tasks
        for i in range(self.max_workers):
            worker = asyncio.create_task(self._worker(f"worker-{i}"))
            self.workers.append(worker)
        
        logger.info(f"Message processor started with {self.max_workers} workers")
    
    async def stop(self):
        """Stop the message processor and worker tasks"""
        self.running = False
        
        # Cancel all workers
        for worker in self.workers:
            worker.cancel()
        
        # Wait for workers to finish
        if self.workers:
            await asyncio.gather(*self.workers, return_exceptions=True)
        
        self.workers.clear()
        logger.info("Message processor stopped")
    
    def register_handler(self, message_type: str, handler: Callable):
        """
        Register a message handler
        
        Args:
            message_type: Type of message to handle
            handler: Handler function
        """
        self.message_handlers[message_type] = handler
        logger.debug(f"Registered handler for message type: {message_type}")
    
    async def queue_message(
        self,
        message: Dict[str, Any],
        session_id: str,
        user_id: Optional[str] = None,
        priority: MessagePriority = MessagePriority.NORMAL
    ) -> bool:
        """
        Queue a message for processing
        
        Args:
            message: Message data
            session_id: Session identifier
            user_id: Optional user identifier
            priority: Message priority
            
        Returns:
            bool: True if queued successfully, False if queue is full
        """
        try:
            processed_message = ProcessedMessage(
                message=message,
                session_id=session_id,
                user_id=user_id,
                priority=priority,
                timestamp=datetime.utcnow()
            )
            
            # Add to appropriate priority queue
            queue = self.message_queues[priority]
            queue.put_nowait(processed_message)
            
            self.metrics.total_messages += 1
            self.metrics.queue_size = sum(q.qsize() for q in self.message_queues.values())
            
            logger.debug(f"Message queued: {session_id} (priority: {priority})")
            return True
            
        except asyncio.QueueFull:
            logger.warning(f"Message queue full, dropping message: {session_id}")
            return False
        except Exception as e:
            logger.error(f"Error queuing message: {e}")
            return False
    
    async def _worker(self, worker_name: str):
        """Worker task for processing messages"""
        logger.debug(f"Worker {worker_name} started")
        
        while self.running:
            try:
                # Get message from highest priority queue
                message = await self._get_next_message()
                if message:
                    await self._process_message(message, worker_name)
                else:
                    # No messages available, wait a bit
                    await asyncio.sleep(0.1)
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Worker {worker_name} error: {e}")
                await asyncio.sleep(1)  # Wait before retrying
        
        logger.debug(f"Worker {worker_name} stopped")
    
    async def _get_next_message(self) -> Optional[ProcessedMessage]:
        """Get next message from priority queues"""
        # Check queues in priority order
        for priority in [MessagePriority.CRITICAL, MessagePriority.HIGH, 
                        MessagePriority.NORMAL, MessagePriority.LOW]:
            queue = self.message_queues[priority]
            try:
                message = queue.get_nowait()
                return message
            except asyncio.QueueEmpty:
                continue
        
        return None
    
    async def _process_message(self, message: ProcessedMessage, worker_name: str):
        """Process a single message"""
        start_time = time.time()
        
        try:
            # Get message type
            message_type = message.message.get("type", "unknown")
            
            # Find appropriate handler
            handler = self.message_handlers.get(message_type)
            if handler:
                # Process with timeout
                await asyncio.wait_for(
                    handler(message.message, message.session_id, message.user_id),
                    timeout=self.processing_timeout
                )
            else:
                logger.warning(f"No handler for message type: {message_type}")
            
            # Update metrics
            processing_time = time.time() - start_time
            self.processing_times.append(processing_time)
            self.metrics.processed_messages += 1
            self.metrics.last_processed = datetime.utcnow()
            
            # Update average processing time
            if self.processing_times:
                self.metrics.average_processing_time = sum(self.processing_times) / len(self.processing_times)
            
            # Update messages per second
            elapsed = (datetime.utcnow() - self.start_time).total_seconds()
            if elapsed > 0:
                self.metrics.messages_per_second = self.metrics.processed_messages / elapsed
            
            logger.debug(f"Message processed by {worker_name}: {message.session_id} ({processing_time:.3f}s)")
            
        except asyncio.TimeoutError:
            logger.error(f"Message processing timeout: {message.session_id}")
            await self._handle_processing_error(message, "timeout")
        except Exception as e:
            logger.error(f"Message processing error: {e}")
            await self._handle_processing_error(message, str(e))
    
    async def _handle_processing_error(self, message: ProcessedMessage, error: str):
        """Handle message processing errors with retry logic"""
        message.retry_count += 1
        self.metrics.failed_messages += 1
        
        if message.retry_count <= message.max_retries:
            # Retry with exponential backoff
            delay = self.retry_delays[min(message.retry_count - 1, len(self.retry_delays) - 1)]
            logger.info(f"Retrying message {message.session_id} in {delay}s (attempt {message.retry_count})")
            
            await asyncio.sleep(delay)
            
            # Re-queue for retry
            queue = self.message_queues[message.priority]
            try:
                queue.put_nowait(message)
            except asyncio.QueueFull:
                logger.error(f"Retry queue full, dropping message: {message.session_id}")
        else:
            logger.error(f"Message failed after {message.max_retries} retries: {message.session_id}")
    
    async def process_batch(self, messages: List[ProcessedMessage]) -> List[bool]:
        """
        Process a batch of messages
        
        Args:
            messages: List of messages to process
            
        Returns:
            List[bool]: Success status for each message
        """
        results = []
        
        # Process messages concurrently
        tasks = []
        for message in messages:
            task = asyncio.create_task(self._process_single_message(message))
            tasks.append(task)
        
        # Wait for all tasks to complete
        try:
            results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=self.processing_timeout
            )
        except asyncio.TimeoutError:
            logger.error("Batch processing timeout")
            results = [False] * len(messages)
        
        return results
    
    async def _process_single_message(self, message: ProcessedMessage) -> bool:
        """Process a single message and return success status"""
        try:
            message_type = message.message.get("type", "unknown")
            handler = self.message_handlers.get(message_type)
            
            if handler:
                await handler(message.message, message.session_id, message.user_id)
                return True
            else:
                logger.warning(f"No handler for message type: {message_type}")
                return False
                
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return False
    
    async def get_metrics(self) -> MessageProcessorMetrics:
        """Get message processor metrics"""
        self.metrics.queue_size = sum(q.qsize() for q in self.message_queues.values())
        self.metrics.batch_size = self.batch_size
        
        # Update messages per second
        elapsed = (datetime.utcnow() - self.start_time).total_seconds()
        if elapsed > 0:
            self.metrics.messages_per_second = self.metrics.processed_messages / elapsed
        
        return self.metrics
    
    async def get_queue_status(self) -> Dict[str, Any]:
        """Get detailed queue status"""
        return {
            "critical_queue_size": self.message_queues[MessagePriority.CRITICAL].qsize(),
            "high_queue_size": self.message_queues[MessagePriority.HIGH].qsize(),
            "normal_queue_size": self.message_queues[MessagePriority.NORMAL].qsize(),
            "low_queue_size": self.message_queues[MessagePriority.LOW].qsize(),
            "total_queue_size": sum(q.qsize() for q in self.message_queues.values()),
            "active_workers": len([w for w in self.workers if not w.done()]),
            "registered_handlers": list(self.message_handlers.keys())
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on message processor
        
        Returns:
            Dict[str, Any]: Health check results
        """
        queue_status = await self.get_queue_status()
        metrics = await self.get_metrics()
        
        # Determine health status
        total_queue_size = queue_status["total_queue_size"]
        active_workers = queue_status["active_workers"]
        
        if total_queue_size > self.queue_size * 0.8:
            status = "degraded"
        elif active_workers < self.max_workers * 0.5:
            status = "degraded"
        elif metrics.failed_messages > metrics.processed_messages * 0.1:
            status = "degraded"
        else:
            status = "healthy"
        
        return {
            "status": status,
            "uptime": (datetime.utcnow() - self.start_time).total_seconds(),
            "queue_status": queue_status,
            "metrics": {
                "total_messages": metrics.total_messages,
                "processed_messages": metrics.processed_messages,
                "failed_messages": metrics.failed_messages,
                "average_processing_time": metrics.average_processing_time,
                "messages_per_second": metrics.messages_per_second
            },
            "configuration": {
                "batch_size": self.batch_size,
                "max_workers": self.max_workers,
                "queue_size": self.queue_size,
                "processing_timeout": self.processing_timeout
            }
        }

