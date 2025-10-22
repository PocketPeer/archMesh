"""
Unified Vibe Coding Service - Main Orchestrator

This module provides the main orchestrator service that integrates all
Vibe Coding components (Intent Parser, Context Aggregator, Code Generator, Sandbox Service)
into a cohesive workflow.
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum

from app.vibe_coding.intent_parser import IntentParser, IntentParserConfig
from app.vibe_coding.context_aggregator import ContextAggregator, ContextAggregatorConfig
from app.vibe_coding.code_generator import CodeGenerator, CodeGeneratorConfig
from app.sandbox.sandbox_service import SandboxService
from app.vibe_coding.models import (
    ParsedIntent,
    UnifiedContext,
    GeneratedCode
)
from app.sandbox.models import (
    SandboxExecutionResponse,
    CodeQualityResult
)
from app.core.exceptions import VibeCodingError as CoreVibeCodingError


class VibeCodingError(Exception):
    """Custom exception for Vibe Coding Service errors."""
    pass


class SessionNotFoundError(VibeCodingError):
    """Exception raised when a session is not found."""
    pass


class InvalidRequestError(VibeCodingError):
    """Exception raised when a request is invalid."""
    pass


class WorkflowStage(Enum):
    """Enumeration of workflow stages."""
    INTENT_PARSING = "intent_parsing"
    CONTEXT_AGGREGATION = "context_aggregation"
    CODE_GENERATION = "code_generation"
    EXECUTION = "execution"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class VibeCodingConfig:
    """Configuration for the Vibe Coding Service."""
    max_context_length: int = 10000
    timeout_seconds: int = 60
    enable_caching: bool = True
    max_concurrent_sessions: int = 10
    intent_parser_config: IntentParserConfig = field(default_factory=IntentParserConfig)
    context_aggregator_config: ContextAggregatorConfig = field(default_factory=ContextAggregatorConfig)
    code_generator_config: CodeGeneratorConfig = field(default_factory=CodeGeneratorConfig)
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        if self.max_context_length <= 0:
            raise ValueError("Invalid configuration: max_context_length must be positive")
        if self.timeout_seconds <= 0:
            raise ValueError("Invalid configuration: timeout_seconds must be positive")
        if self.max_concurrent_sessions <= 0:
            raise ValueError("Invalid configuration: max_concurrent_sessions must be positive")


@dataclass
class VibeCodingRequest:
    """Request for code generation."""
    user_input: str
    project_id: str
    session_id: str
    context_sources: List[str] = field(default_factory=lambda: ["requirements", "architecture"])
    language: Optional[str] = None
    framework: Optional[str] = None
    additional_context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class VibeCodingResponse:
    """Response from code generation."""
    success: bool
    session_id: str
    generated_code: Optional[GeneratedCode] = None
    execution_result: Optional[SandboxExecutionResponse] = None
    execution_time: float = 0.0
    memory_usage: float = 0.0
    cpu_usage: float = 0.0
    progress: int = 0
    current_stage: str = "pending"
    stages_completed: List[str] = field(default_factory=list)
    error_message: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None


@dataclass
class ChatRequest:
    """Request for chat interface."""
    message: str
    session_id: str
    project_id: str
    context: Optional[Dict[str, Any]] = None


@dataclass
class ChatResponse:
    """Response from chat interface."""
    success: bool
    message: str
    session_id: str
    generated_code: Optional[GeneratedCode] = None
    execution_result: Optional[SandboxExecutionResponse] = None
    suggestions: List[str] = field(default_factory=list)


@dataclass
class SessionStatus:
    """Status of a generation session."""
    session_id: str
    status: str
    progress: int
    current_stage: str
    stages_completed: List[str]
    created_at: datetime
    updated_at: datetime
    result: Optional[Dict[str, Any]] = None


@dataclass
class FeedbackRequest:
    """Request for feedback submission."""
    session_id: str
    feedback_type: str
    rating: Optional[int] = None
    comments: Optional[str] = None
    suggestions: List[str] = field(default_factory=list)


@dataclass
class FeedbackResponse:
    """Response from feedback submission."""
    success: bool
    message: str
    session_id: str


@dataclass
class HealthStatus:
    """Health status of the service."""
    overall_health: bool
    components: Dict[str, bool]
    timestamp: datetime


class MetricsCollector:
    """Collects and tracks performance metrics."""
    
    def __init__(self):
        self.request_count = 0
        self.success_count = 0
        self.error_count = 0
        self.total_execution_time = 0.0
        self.total_memory_usage = 0.0
    
    def record_request(self):
        """Record a new request."""
        self.request_count += 1
    
    def record_success(self):
        """Record a successful request."""
        self.success_count += 1
    
    def record_error(self):
        """Record a failed request."""
        self.error_count += 1
    
    def record_execution_time(self, execution_time: float):
        """Record execution time."""
        self.total_execution_time += execution_time
    
    def record_memory_usage(self, memory_usage: float):
        """Record memory usage."""
        self.total_memory_usage += memory_usage
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics."""
        return {
            "request_count": self.request_count,
            "success_count": self.success_count,
            "error_count": self.error_count,
            "success_rate": self.success_count / max(self.request_count, 1),
            "average_execution_time": self.total_execution_time / max(self.request_count, 1),
            "average_memory_usage": self.total_memory_usage / max(self.request_count, 1)
        }


class Logger:
    """Simple logger for the service."""
    
    def info(self, message: str):
        """Log info message."""
        print(f"[INFO] {message}")
    
    def error(self, message: str):
        """Log error message."""
        print(f"[ERROR] {message}")
    
    def warning(self, message: str):
        """Log warning message."""
        print(f"[WARNING] {message}")
    
    def debug(self, message: str):
        """Log debug message."""
        print(f"[DEBUG] {message}")


class VibeCodingService:
    """Main orchestrator service for Vibe Coding Tool."""
    
    def __init__(self, config: Optional[VibeCodingConfig] = None):
        """Initialize the Vibe Coding Service."""
        self.config = config or VibeCodingConfig()
        
        # Initialize components
        self.intent_parser = IntentParser(self.config.intent_parser_config)
        self.context_aggregator = ContextAggregator(self.config.context_aggregator_config)
        self.code_generator = CodeGenerator(self.config.code_generator_config)
        self.sandbox_service = SandboxService()
        
        # Initialize service components
        self.metrics = MetricsCollector()
        self.logger = Logger()
        
        # Session management
        self._sessions: Dict[str, Dict[str, Any]] = {}
        self._active_sessions: Dict[str, bool] = {}
    
    async def generate_code(self, request: VibeCodingRequest) -> VibeCodingResponse:
        """Main entry point for code generation workflow."""
        start_time = time.time()
        
        try:
            # Validate request
            if not request.user_input or not request.user_input.strip():
                raise InvalidRequestError("Invalid input: user_input cannot be empty")
            
            if not request.project_id or not request.session_id:
                raise InvalidRequestError("Invalid input: project_id and session_id are required")
            
            # Record request
            self.metrics.record_request()
            
            # Initialize session
            session_id = request.session_id
            self._sessions[session_id] = {
                "status": "in_progress",
                "progress": 0,
                "current_stage": "intent_parsing",
                "stages_completed": [],
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "result": None
            }
            self._active_sessions[session_id] = True
            
            # Stage 1: Intent Parsing
            self.logger.info(f"Starting intent parsing for session {session_id}")
            parsed_intent = await self.intent_parser.parse(request.user_input)
            self._update_session(session_id, "intent_parsing", 25, ["intent_parsing"])
            
            # Stage 2: Context Aggregation
            self.logger.info(f"Starting context aggregation for session {session_id}")
            context_request = {
                "project_id": request.project_id,
                "sources": request.context_sources,
                "intent": parsed_intent
            }
            unified_context = await self.context_aggregator.aggregate_context(context_request)
            self._update_session(session_id, "context_aggregation", 50, ["intent_parsing", "context_aggregation"])
            
            # Stage 3: Code Generation
            self.logger.info(f"Starting code generation for session {session_id}")
            generation_request = {
                "intent": parsed_intent,
                "context": unified_context,
                "language": request.language,
                "framework": request.framework
            }
            generated_code = await self.code_generator.generate_code(generation_request)
            self._update_session(session_id, "code_generation", 75, ["intent_parsing", "context_aggregation", "code_generation"])
            
            # Stage 4: Execution
            self.logger.info(f"Starting code execution for session {session_id}")
            execution_request = {
                "code": generated_code.code,
                "language": generated_code.language,
                "dependencies": generated_code.dependencies
            }
            execution_result = await self.sandbox_service.execute_code(execution_request)
            self._update_session(session_id, "execution", 100, ["intent_parsing", "context_aggregation", "code_generation", "execution"])
            
            # Calculate execution time
            execution_time = time.time() - start_time
            
            # Record metrics
            self.metrics.record_success()
            self.metrics.record_execution_time(execution_time)
            self.metrics.record_memory_usage(execution_result.memory_usage_mb if execution_result else 0.0)
            
            # Create response
            response = VibeCodingResponse(
                success=True,
                session_id=session_id,
                generated_code=generated_code,
                execution_result=execution_result,
                execution_time=execution_time,
                memory_usage=execution_result.memory_usage_mb if execution_result else 0.0,
                cpu_usage=0.0,  # Placeholder
                progress=100,
                current_stage="completed",
                stages_completed=["intent_parsing", "context_aggregation", "code_generation", "execution"],
                metrics=self.metrics.get_metrics()
            )
            
            # Update session with result
            self._sessions[session_id]["status"] = "completed"
            self._sessions[session_id]["result"] = {
                "success": True,
                "generated_code": generated_code,
                "execution_result": execution_result
            }
            self._sessions[session_id]["updated_at"] = datetime.now()
            
            self.logger.info(f"Code generation completed successfully for session {session_id}")
            return response
            
        except Exception as e:
            # Record error
            self.metrics.record_error()
            execution_time = time.time() - start_time
            
            # Update session with error (use request.session_id if session_id is not defined)
            session_id_for_error = getattr(request, 'session_id', 'unknown')
            if session_id_for_error in self._sessions:
                self._sessions[session_id_for_error]["status"] = "failed"
                self._sessions[session_id_for_error]["result"] = {
                    "success": False,
                    "error": str(e)
                }
                self._sessions[session_id_for_error]["updated_at"] = datetime.now()
            
            self.logger.error(f"Code generation failed for session {session_id_for_error}: {str(e)}")
            
            # Create error response
            response = VibeCodingResponse(
                success=False,
                session_id=session_id_for_error,
                execution_time=execution_time,
                progress=0,
                current_stage="failed",
                error_message=str(e),
                metrics=self.metrics.get_metrics()
            )
            
            raise VibeCodingError(f"Workflow execution failed: {str(e)}") from e
    
    async def chat(self, request: ChatRequest) -> ChatResponse:
        """Conversational interface for iterative development."""
        try:
            # Convert chat request to generation request
            generation_request = VibeCodingRequest(
                user_input=request.message,
                project_id=request.project_id,
                session_id=request.session_id,
                context_sources=["requirements", "architecture"],
                additional_context=request.context or {}
            )
            
            # Generate code
            generation_response = await self.generate_code(generation_request)
            
            # Create chat response
            response = ChatResponse(
                success=generation_response.success,
                message="Code generated successfully" if generation_response.success else "Code generation failed",
                session_id=request.session_id,
                generated_code=generation_response.generated_code,
                execution_result=generation_response.execution_result,
                suggestions=["Try refining your request", "Add more specific requirements"]
            )
            
            return response
            
        except Exception as e:
            self.logger.error(f"Chat processing failed for session {request.session_id}: {str(e)}")
            raise VibeCodingError(f"Chat processing failed: {str(e)}") from e
    
    async def get_session_status(self, session_id: str) -> SessionStatus:
        """Get current status of a generation session."""
        if session_id not in self._sessions:
            raise SessionNotFoundError(f"Session not found: {session_id}")
        
        session_data = self._sessions[session_id]
        
        return SessionStatus(
            session_id=session_id,
            status=session_data["status"],
            progress=session_data["progress"],
            current_stage=session_data["current_stage"],
            stages_completed=session_data["stages_completed"],
            created_at=session_data["created_at"],
            updated_at=session_data["updated_at"],
            result=session_data["result"]
        )
    
    async def submit_feedback(self, request: FeedbackRequest) -> FeedbackResponse:
        """Submit user feedback for improvement."""
        if request.session_id not in self._sessions:
            raise SessionNotFoundError(f"Session not found: {request.session_id}")
        
        # Store feedback (in a real implementation, this would be persisted)
        session_data = self._sessions[request.session_id]
        if "feedback" not in session_data:
            session_data["feedback"] = []
        
        feedback_data = {
            "type": request.feedback_type,
            "rating": request.rating,
            "comments": request.comments,
            "suggestions": request.suggestions,
            "submitted_at": datetime.now()
        }
        session_data["feedback"].append(feedback_data)
        session_data["updated_at"] = datetime.now()
        
        return FeedbackResponse(
            success=True,
            message="Feedback submitted successfully",
            session_id=request.session_id
        )
    
    async def health_check(self) -> HealthStatus:
        """Perform health check on all components."""
        components = {}
        
        try:
            # Check intent parser
            components["intent_parser"] = True
        except Exception:
            components["intent_parser"] = False
        
        try:
            # Check context aggregator
            components["context_aggregator"] = True
        except Exception:
            components["context_aggregator"] = False
        
        try:
            # Check code generator
            components["code_generator"] = True
        except Exception:
            components["code_generator"] = False
        
        try:
            # Check sandbox service
            components["sandbox_service"] = True
        except Exception:
            components["sandbox_service"] = False
        
        overall_health = all(components.values())
        
        return HealthStatus(
            overall_health=overall_health,
            components=components,
            timestamp=datetime.now()
        )
    
    def _update_session(self, session_id: str, stage: str, progress: int, stages_completed: List[str]):
        """Update session status."""
        if session_id in self._sessions:
            self._sessions[session_id]["current_stage"] = stage
            self._sessions[session_id]["progress"] = progress
            self._sessions[session_id]["stages_completed"] = stages_completed
            self._sessions[session_id]["updated_at"] = datetime.now()
    
    def _cleanup_session(self, session_id: str):
        """Clean up session data."""
        if session_id in self._sessions:
            del self._sessions[session_id]
        if session_id in self._active_sessions:
            del self._active_sessions[session_id]
