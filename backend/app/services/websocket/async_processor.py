"""
Async Message Processor for WebSocket Service

This module provides high-performance async message processing with worker pools,
message queuing, and concurrent processing for scalable WebSocket operations.
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable, Set, Union
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import weakref

from app.schemas.websocket import WebSocketMessage
from app.core.exceptions import WebSocketError

logger = logging.getLogger(__name__)


class ProcessingPriority(str, Enum):
    """Message processing priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


class WorkerState(str, Enum):
    """Worker thread states"""
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    STOPPING = "stopping"


@dataclass
class ProcessingTask:
    """Task for async processing"""
    task_id: str
    message: Dict[str, Any]
    session_id: str
    user_id: Optional[str]
    priority: ProcessingPriority
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3
    callback: Optional[Callable] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkerMetrics:
    """Metrics for worker performance"""
    worker_id: str
    state: WorkerState
    tasks_processed: int = 0
    tasks_failed: int = 0
    total_processing_time: float = 0.0
    average_processing_time: float = 0.0
    last_task_time: Optional[datetime] = None
    error_count: int = 0
    uptime: float = 0.0


@dataclass
class ProcessingMetrics:
    """Overall processing metrics"""
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    queued_tasks: int = 0
    active_workers: int = 0
    average_processing_time: float = 0.0
    throughput_per_second: float = 0.0
    error_rate: float = 0.0
    last_activity: datetime = field(default_factory=datetime.utcnow)


class AsyncMessageProcessor:
    """
    High-performance async message processor with worker pools
    
    Provides:
    - Async message processing with configurable worker pools
    - Priority-based task queuing and processing
    - Worker health monitoring and auto-scaling
    - Performance metrics and monitoring
    - Error handling and retry logic
    - Load balancing across workers
    """
    
    def __init__(
        self,
        max_workers: int = 20,
        queue_size: int = 50000,
        processing_timeout: float = 30.0,
        auto_scale: bool = True,
        scale_threshold: float = 0.8,
        min_workers: int = 5,
        max_workers_limit: int = 100
    ):
        """
        Initialize async message processor
        
        Args:
            max_workers: Maximum number of worker tasks
            queue_size: Maximum queue size per priority
            processing_timeout: Timeout for message processing
            auto_scale: Enable automatic worker scaling
            scale_threshold: Queue utilization threshold for scaling
            min_workers: Minimum number of workers
            max_workers_limit: Maximum number of workers (hard limit)
        """
        self.max_workers = max_workers
        self.queue_size = queue_size
        self.processing_timeout = processing_timeout
        self.auto_scale = auto_scale
        self.scale_threshold = scale_threshold
        self.min_workers = min_workers
        self.max_workers_limit = max_workers_limit
        
        # Task queues by priority
        self.task_queues = {
            ProcessingPriority.CRITICAL: asyncio.Queue(maxsize=queue_size),
            ProcessingPriority.HIGH: asyncio.Queue(maxsize=queue_size),
            ProcessingPriority.NORMAL: asyncio.Queue(maxsize=queue_size),
            ProcessingPriority.LOW: asyncio.Queue(maxsize=queue_size)
        }
        
        # Worker management
        self.workers: Dict[str, asyncio.Task] = {}
        self.worker_metrics: Dict[str, WorkerMetrics] = {}
        self.worker_states: Dict[str, WorkerState] = {}
        self.active_tasks: Dict[str, ProcessingTask] = {}
        
        # Processing state
        self.running = False
        self.start_time = datetime.utcnow()
        self.metrics = ProcessingMetrics()
        
        # Message handlers
        self.message_handlers: Dict[str, Callable] = {}
        
        # Auto-scaling
        self.scaling_task: Optional[asyncio.Task] = None
        self.last_scale_time = datetime.utcnow()
        self.scale_cooldown = 30.0  # seconds
        
        # Performance tracking
        self.processing_times: deque = deque(maxlen=10000)
        self.throughput_history: deque = deque(maxlen=100)
        
        # Retry configuration
        self.retry_delays = [1, 2, 5, 10, 30]  # seconds
    
    async def start(self):
        """Start the async message processor"""
        if self.running:
            return
        
        self.running = True
        self.start_time = datetime.utcnow()
        
        # Start initial workers
        for i in range(self.min_workers):
            await self._create_worker(f"worker-{i}")
        
        # Start auto-scaling if enabled
        if self.auto_scale:
            self.scaling_task = asyncio.create_task(self._auto_scale_loop())
        
        logger.info(f"Async message processor started with {self.min_workers} workers")
    
    async def stop(self):
        """Stop the async message processor"""
        self.running = False
        
        # Stop auto-scaling
        if self.scaling_task:
            self.scaling_task.cancel()
            try:
                await self.scaling_task
            except asyncio.CancelledError:
                pass
        
        # Stop all workers
        for worker_id, worker_task in list(self.workers.items()):
            self.worker_states[worker_id] = WorkerState.STOPPING
            worker_task.cancel()
        
        # Wait for workers to finish
        if self.workers:
            await asyncio.gather(*self.workers.values(), return_exceptions=True)
        
        self.workers.clear()
        self.worker_metrics.clear()
        self.worker_states.clear()
        
        logger.info("Async message processor stopped")
    
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
        priority: ProcessingPriority = ProcessingPriority.NORMAL,
        callback: Optional[Callable] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Queue a message for async processing
        
        Args:
            message: Message data
            session_id: Session identifier
            user_id: Optional user identifier
            priority: Message priority
            callback: Optional callback function
            metadata: Optional metadata
            
        Returns:
            str: Task ID
            
        Raises:
            WebSocketError: If queue is full
        """
        task_id = f"task_{int(time.time() * 1000)}_{id(message)}"
        
        task = ProcessingTask(
            task_id=task_id,
            message=message,
            session_id=session_id,
            user_id=user_id,
            priority=priority,
            callback=callback,
            metadata=metadata or {}
        )
        
        try:
            # Add to appropriate priority queue
            queue = self.task_queues[priority]
            queue.put_nowait(task)
            
            self.metrics.total_tasks += 1
            self.metrics.queued_tasks += 1
            self.metrics.last_activity = datetime.utcnow()
            
            logger.debug(f"Message queued: {task_id} (priority: {priority})")
            return task_id
            
        except asyncio.QueueFull:
            raise WebSocketError(f"Queue full for priority {priority}")
    
    async def _create_worker(self, worker_id: str):
        """Create a new worker task"""
        if worker_id in self.workers:
            return
        
        worker_task = asyncio.create_task(self._worker_loop(worker_id))
        self.workers[worker_id] = worker_task
        
        # Initialize worker metrics
        self.worker_metrics[worker_id] = WorkerMetrics(
            worker_id=worker_id,
            state=WorkerState.IDLE
        )
        self.worker_states[worker_id] = WorkerState.IDLE
        
        logger.debug(f"Created worker: {worker_id}")
    
    async def _remove_worker(self, worker_id: str):
        """Remove a worker task"""
        if worker_id not in self.workers:
            return
        
        # Mark worker as stopping
        self.worker_states[worker_id] = WorkerState.STOPPING
        
        # Cancel worker task
        worker_task = self.workers[worker_id]
        worker_task.cancel()
        
        try:
            await worker_task
        except asyncio.CancelledError:
            pass
        
        # Clean up
        del self.workers[worker_id]
        del self.worker_metrics[worker_id]
        del self.worker_states[worker_id]
        
        logger.debug(f"Removed worker: {worker_id}")
    
    async def _worker_loop(self, worker_id: str):
        """Worker task loop"""
        logger.debug(f"Worker {worker_id} started")
        
        while self.running and self.worker_states.get(worker_id) != WorkerState.STOPPING:
            try:
                # Get next task from highest priority queue
                task = await self._get_next_task()
                if task:
                    await self._process_task(worker_id, task)
                else:
                    # No tasks available, wait a bit
                    await asyncio.sleep(0.1)
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Worker {worker_id} error: {e}")
                self.worker_metrics[worker_id].error_count += 1
                self.worker_states[worker_id] = WorkerState.ERROR
                await asyncio.sleep(1)  # Wait before retrying
        
        logger.debug(f"Worker {worker_id} stopped")
    
    async def _get_next_task(self) -> Optional[ProcessingTask]:
        """Get next task from priority queues"""
        # Check queues in priority order
        for priority in [ProcessingPriority.CRITICAL, ProcessingPriority.HIGH,
                        ProcessingPriority.NORMAL, ProcessingPriority.LOW]:
            queue = self.task_queues[priority]
            try:
                task = queue.get_nowait()
                return task
            except asyncio.QueueEmpty:
                continue
        
        return None
    
    async def _process_task(self, worker_id: str, task: ProcessingTask):
        """Process a single task"""
        start_time = time.time()
        
        # Update worker state
        self.worker_states[worker_id] = WorkerState.BUSY
        self.worker_metrics[worker_id].state = WorkerState.BUSY
        task.started_at = datetime.utcnow()
        
        # Track active task
        self.active_tasks[task.task_id] = task
        
        try:
            # Get message type
            message_type = task.message.get("type", "unknown")
            
            # Find appropriate handler
            handler = self.message_handlers.get(message_type)
            if handler:
                # Process with timeout
                await asyncio.wait_for(
                    handler(task.message, task.session_id, task.user_id),
                    timeout=self.processing_timeout
                )
            else:
                logger.warning(f"No handler for message type: {message_type}")
            
            # Update metrics
            processing_time = time.time() - start_time
            self.processing_times.append(processing_time)
            
            # Update worker metrics
            worker_metrics = self.worker_metrics[worker_id]
            worker_metrics.tasks_processed += 1
            worker_metrics.total_processing_time += processing_time
            worker_metrics.average_processing_time = (
                worker_metrics.total_processing_time / worker_metrics.tasks_processed
            )
            worker_metrics.last_task_time = datetime.utcnow()
            worker_metrics.state = WorkerState.IDLE
            
            # Update overall metrics
            self.metrics.completed_tasks += 1
            self.metrics.queued_tasks -= 1
            
            # Update average processing time
            if self.processing_times:
                self.metrics.average_processing_time = sum(self.processing_times) / len(self.processing_times)
            
            # Update throughput
            elapsed = (datetime.utcnow() - self.start_time).total_seconds()
            if elapsed > 0:
                self.metrics.throughput_per_second = self.metrics.completed_tasks / elapsed
            
            # Update error rate
            if self.metrics.total_tasks > 0:
                self.metrics.error_rate = self.metrics.failed_tasks / self.metrics.total_tasks
            
            # Update worker state
            self.worker_states[worker_id] = WorkerState.IDLE
            
            # Execute callback if provided
            if task.callback:
                try:
                    await task.callback(task, processing_time)
                except Exception as e:
                    logger.error(f"Callback error for task {task.task_id}: {e}")
            
            task.completed_at = datetime.utcnow()
            logger.debug(f"Task {task.task_id} processed by {worker_id} ({processing_time:.3f}s)")
            
        except asyncio.TimeoutError:
            logger.error(f"Task processing timeout: {task.task_id}")
            await self._handle_task_error(worker_id, task, "timeout")
        except Exception as e:
            logger.error(f"Task processing error: {e}")
            await self._handle_task_error(worker_id, task, str(e))
        finally:
            # Remove from active tasks
            self.active_tasks.pop(task.task_id, None)
    
    async def _handle_task_error(self, worker_id: str, task: ProcessingTask, error: str):
        """Handle task processing errors with retry logic"""
        task.retry_count += 1
        self.metrics.failed_tasks += 1
        self.worker_metrics[worker_id].tasks_failed += 1
        self.worker_metrics[worker_id].error_count += 1
        self.worker_states[worker_id] = WorkerState.ERROR
        
        if task.retry_count <= task.max_retries:
            # Retry with exponential backoff
            delay = self.retry_delays[min(task.retry_count - 1, len(self.retry_delays) - 1)]
            logger.info(f"Retrying task {task.task_id} in {delay}s (attempt {task.retry_count})")
            
            await asyncio.sleep(delay)
            
            # Re-queue for retry
            queue = self.task_queues[task.priority]
            try:
                queue.put_nowait(task)
                self.metrics.queued_tasks += 1
            except asyncio.QueueFull:
                logger.error(f"Retry queue full, dropping task: {task.task_id}")
        else:
            logger.error(f"Task failed after {task.max_retries} retries: {task.task_id}")
    
    async def _auto_scale_loop(self):
        """Auto-scaling loop for worker management"""
        while self.running:
            try:
                await asyncio.sleep(10)  # Check every 10 seconds
                
                if not self.auto_scale:
                    continue
                
                # Check if we can scale (cooldown period)
                if (datetime.utcnow() - self.last_scale_time).total_seconds() < self.scale_cooldown:
                    continue
                
                # Calculate queue utilization
                total_queue_size = sum(q.qsize() for q in self.task_queues.values())
                total_capacity = len(self.task_queues) * self.queue_size
                utilization = total_queue_size / total_capacity if total_capacity > 0 else 0
                
                current_workers = len(self.workers)
                
                # Scale up if utilization is high
                if utilization > self.scale_threshold and current_workers < self.max_workers_limit:
                    new_workers = min(5, self.max_workers_limit - current_workers)
                    for i in range(new_workers):
                        worker_id = f"worker-{current_workers + i}"
                        await self._create_worker(worker_id)
                    
                    self.last_scale_time = datetime.utcnow()
                    logger.info(f"Scaled up to {len(self.workers)} workers (utilization: {utilization:.2f})")
                
                # Scale down if utilization is low and we have more than minimum workers
                elif utilization < 0.2 and current_workers > self.min_workers:
                    workers_to_remove = min(2, current_workers - self.min_workers)
                    idle_workers = [w for w, state in self.worker_states.items() if state == WorkerState.IDLE]
                    
                    for worker_id in idle_workers[:workers_to_remove]:
                        await self._remove_worker(worker_id)
                    
                    self.last_scale_time = datetime.utcnow()
                    logger.info(f"Scaled down to {len(self.workers)} workers (utilization: {utilization:.2f})")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Auto-scaling error: {e}")
    
    def get_metrics(self) -> ProcessingMetrics:
        """Get processing metrics"""
        self.metrics.active_workers = len([w for w in self.worker_states.values() if w == WorkerState.BUSY])
        self.metrics.queued_tasks = sum(q.qsize() for q in self.task_queues.values())
        return self.metrics
    
    def get_worker_metrics(self) -> Dict[str, WorkerMetrics]:
        """Get worker metrics"""
        # Update uptime for all workers
        current_time = datetime.utcnow()
        for worker_metrics in self.worker_metrics.values():
            worker_metrics.uptime = (current_time - self.start_time).total_seconds()
        
        return dict(self.worker_metrics)
    
    def get_queue_status(self) -> Dict[str, Any]:
        """Get detailed queue status"""
        return {
            "critical_queue_size": self.task_queues[ProcessingPriority.CRITICAL].qsize(),
            "high_queue_size": self.task_queues[ProcessingPriority.HIGH].qsize(),
            "normal_queue_size": self.task_queues[ProcessingPriority.NORMAL].qsize(),
            "low_queue_size": self.task_queues[ProcessingPriority.LOW].qsize(),
            "total_queue_size": sum(q.qsize() for q in self.task_queues.values()),
            "active_workers": len([w for w in self.worker_states.values() if w == WorkerState.BUSY]),
            "idle_workers": len([w for w in self.worker_states.values() if w == WorkerState.IDLE]),
            "error_workers": len([w for w in self.worker_states.values() if w == WorkerState.ERROR]),
            "active_tasks": len(self.active_tasks),
            "registered_handlers": list(self.message_handlers.keys())
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on async processor
        
        Returns:
            Dict[str, Any]: Health check results
        """
        queue_status = self.get_queue_status()
        metrics = self.get_metrics()
        worker_metrics = self.get_worker_metrics()
        
        # Calculate health status
        total_workers = len(self.workers)
        error_workers = queue_status["error_workers"]
        queue_utilization = queue_status["total_queue_size"] / (len(self.task_queues) * self.queue_size)
        
        if error_workers > total_workers * 0.5:
            status = "critical"
        elif error_workers > total_workers * 0.2 or queue_utilization > 0.9:
            status = "degraded"
        elif metrics.error_rate > 0.1:
            status = "degraded"
        else:
            status = "healthy"
        
        return {
            "status": status,
            "uptime": (datetime.utcnow() - self.start_time).total_seconds(),
            "queue_status": queue_status,
            "metrics": {
                "total_tasks": metrics.total_tasks,
                "completed_tasks": metrics.completed_tasks,
                "failed_tasks": metrics.failed_tasks,
                "queued_tasks": metrics.queued_tasks,
                "active_workers": metrics.active_workers,
                "average_processing_time": metrics.average_processing_time,
                "throughput_per_second": metrics.throughput_per_second,
                "error_rate": metrics.error_rate
            },
            "worker_metrics": worker_metrics,
            "configuration": {
                "max_workers": self.max_workers,
                "queue_size": self.queue_size,
                "processing_timeout": self.processing_timeout,
                "auto_scale": self.auto_scale,
                "scale_threshold": self.scale_threshold,
                "min_workers": self.min_workers,
                "max_workers_limit": self.max_workers_limit
            }
        }

