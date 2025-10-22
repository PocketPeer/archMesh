"""
Pydantic schemas for Vibe Coding Tool API

This module defines the request and response schemas for the Vibe Coding API endpoints.
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid


class IntentParseRequest(BaseModel):
    """Request schema for intent parsing"""
    
    user_input: str = Field(..., min_length=1, max_length=2000, description="Natural language input")
    
    @validator('user_input')
    def validate_user_input(cls, v):
        if not v.strip():
            raise ValueError("User input cannot be empty")
        return v.strip()


class IntentParseResponse(BaseModel):
    """Response schema for intent parsing"""
    
    success: bool = Field(..., description="Whether parsing was successful")
    parsed_intent: Optional[Dict[str, Any]] = Field(None, description="Parsed intent data")
    error_message: Optional[str] = Field(None, description="Error message if parsing failed")
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Confidence score")


class ContextGatherRequest(BaseModel):
    """Request schema for context gathering"""
    
    document_id: Optional[str] = Field(None, description="ArchMesh document ID")
    project_id: Optional[str] = Field(None, description="Project ID")
    intent: Dict[str, Any] = Field(..., description="Parsed intent data")
    max_context_size: int = Field(default=8000, ge=1000, le=16000, description="Maximum context size in tokens")


class ContextGatherResponse(BaseModel):
    """Response schema for context gathering"""
    
    success: bool = Field(..., description="Whether context gathering was successful")
    context: Optional[Dict[str, Any]] = Field(None, description="Gathered context data")
    context_size: int = Field(default=0, description="Context size in tokens")
    sources: List[str] = Field(default_factory=list, description="Context sources used")
    error_message: Optional[str] = Field(None, description="Error message if gathering failed")


class CodeGenerationRequest(BaseModel):
    """Request schema for code generation"""
    
    user_input: str = Field(..., min_length=1, max_length=2000, description="Natural language description")
    document_id: Optional[str] = Field(None, description="ArchMesh document ID for context")
    project_id: Optional[str] = Field(None, description="Project ID for context")
    language: Optional[str] = Field(None, description="Preferred programming language")
    framework: Optional[str] = Field(None, description="Preferred framework")
    include_tests: bool = Field(default=True, description="Include test generation")
    include_docs: bool = Field(default=True, description="Include documentation")
    max_tokens: int = Field(default=4000, ge=1000, le=8000, description="Maximum tokens for generation")
    temperature: float = Field(default=0.2, ge=0.0, le=1.0, description="LLM temperature")
    
    @validator('user_input')
    def validate_user_input(cls, v):
        if not v.strip():
            raise ValueError("User input cannot be empty")
        return v.strip()
    
    @validator('language')
    def validate_language(cls, v):
        if v and v.lower() not in ['python', 'javascript', 'typescript', 'java', 'go', 'rust']:
            raise ValueError("Unsupported programming language")
        return v.lower() if v else None


class CodeGenerationResponse(BaseModel):
    """Response schema for code generation"""
    
    id: str = Field(..., description="Generation ID")
    status: str = Field(..., description="Generation status")
    generated_code: Optional[Dict[str, Any]] = Field(None, description="Generated code")
    parsed_intent: Optional[Dict[str, Any]] = Field(None, description="Parsed intent")
    context_used: Optional[Dict[str, Any]] = Field(None, description="Context used for generation")
    execution_results: List[Dict[str, Any]] = Field(default_factory=list, description="Execution results")
    quality_metrics: Dict[str, Any] = Field(default_factory=dict, description="Quality metrics")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    created_at: datetime = Field(..., description="Creation timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    generation_time_ms: Optional[int] = Field(None, description="Generation time in milliseconds")
    token_count: Optional[int] = Field(None, description="Tokens used")
    cost_usd: Optional[float] = Field(None, description="Cost in USD")


class CodeExecutionRequest(BaseModel):
    """Request schema for code execution"""
    
    generation_id: str = Field(..., description="Code generation ID")
    execution_type: str = Field(default="test", description="Execution type: test, run, lint, format")
    timeout_seconds: int = Field(default=30, ge=5, le=300, description="Execution timeout")
    include_coverage: bool = Field(default=True, description="Include code coverage")
    
    @validator('execution_type')
    def validate_execution_type(cls, v):
        if v not in ['test', 'run', 'lint', 'format']:
            raise ValueError("Invalid execution type")
        return v


class CodeExecutionResponse(BaseModel):
    """Response schema for code execution"""
    
    id: str = Field(..., description="Execution ID")
    generation_id: str = Field(..., description="Code generation ID")
    execution_type: str = Field(..., description="Execution type")
    status: str = Field(..., description="Execution status")
    exit_code: Optional[int] = Field(None, description="Exit code")
    stdout: Optional[str] = Field(None, description="Standard output")
    stderr: Optional[str] = Field(None, description="Standard error")
    execution_time_ms: Optional[int] = Field(None, description="Execution time in milliseconds")
    test_results: Optional[Dict[str, Any]] = Field(None, description="Test results if applicable")
    coverage_results: Optional[Dict[str, Any]] = Field(None, description="Coverage results if applicable")
    quality_results: Optional[Dict[str, Any]] = Field(None, description="Quality analysis results")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    created_at: datetime = Field(..., description="Creation timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")


class VibeChatRequest(BaseModel):
    """Request schema for conversational vibe coding"""
    
    message: str = Field(..., min_length=1, max_length=2000, description="User message")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for context")
    document_id: Optional[str] = Field(None, description="ArchMesh document ID for context")
    project_id: Optional[str] = Field(None, description="Project ID for context")
    include_code: bool = Field(default=True, description="Include code generation in response")
    
    @validator('message')
    def validate_message(cls, v):
        if not v.strip():
            raise ValueError("Message cannot be empty")
        return v.strip()


class VibeChatResponse(BaseModel):
    """Response schema for conversational vibe coding"""
    
    conversation_id: str = Field(..., description="Conversation ID")
    message: str = Field(..., description="Response message")
    generated_code: Optional[Dict[str, Any]] = Field(None, description="Generated code if applicable")
    suggestions: List[str] = Field(default_factory=list, description="Follow-up suggestions")
    requires_clarification: bool = Field(default=False, description="Whether clarification is needed")
    created_at: datetime = Field(..., description="Response timestamp")


class FeedbackRequest(BaseModel):
    """Request schema for providing feedback on generated code"""
    
    generation_id: str = Field(..., description="Code generation ID")
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5")
    feedback_text: Optional[str] = Field(None, max_length=1000, description="Optional feedback text")
    issues: List[str] = Field(default_factory=list, description="List of issues found")
    suggestions: List[str] = Field(default_factory=list, description="List of suggestions")
    
    @validator('feedback_text')
    def validate_feedback_text(cls, v):
        if v and not v.strip():
            raise ValueError("Feedback text cannot be empty")
        return v.strip() if v else None


class FeedbackResponse(BaseModel):
    """Response schema for feedback submission"""
    
    success: bool = Field(..., description="Whether feedback was submitted successfully")
    feedback_id: str = Field(..., description="Feedback ID")
    message: str = Field(..., description="Response message")
    created_at: datetime = Field(..., description="Feedback timestamp")


class GenerationListRequest(BaseModel):
    """Request schema for listing code generations"""
    
    user_id: Optional[str] = Field(None, description="Filter by user ID")
    project_id: Optional[str] = Field(None, description="Filter by project ID")
    status: Optional[str] = Field(None, description="Filter by status")
    language: Optional[str] = Field(None, description="Filter by language")
    limit: int = Field(default=20, ge=1, le=100, description="Number of results to return")
    offset: int = Field(default=0, ge=0, description="Number of results to skip")
    
    @validator('status')
    def validate_status(cls, v):
        if v and v not in ['pending', 'completed', 'failed', 'executing']:
            raise ValueError("Invalid status filter")
        return v


class GenerationListResponse(BaseModel):
    """Response schema for listing code generations"""
    
    generations: List[Dict[str, Any]] = Field(..., description="List of code generations")
    total_count: int = Field(..., description="Total number of generations")
    limit: int = Field(..., description="Limit applied")
    offset: int = Field(..., description="Offset applied")
    has_more: bool = Field(..., description="Whether there are more results")


class GenerationDetailResponse(BaseModel):
    """Response schema for detailed code generation view"""
    
    id: str = Field(..., description="Generation ID")
    user_id: str = Field(..., description="User ID")
    project_id: Optional[str] = Field(None, description="Project ID")
    user_input: str = Field(..., description="Original user input")
    parsed_intent: Optional[Dict[str, Any]] = Field(None, description="Parsed intent")
    context_data: Optional[Dict[str, Any]] = Field(None, description="Context data used")
    generated_code: Optional[Dict[str, Any]] = Field(None, description="Generated code")
    language: Optional[str] = Field(None, description="Programming language")
    framework: Optional[str] = Field(None, description="Framework used")
    status: str = Field(..., description="Generation status")
    quality_metrics: Dict[str, Any] = Field(default_factory=dict, description="Quality metrics")
    execution_results: List[Dict[str, Any]] = Field(default_factory=list, description="Execution results")
    feedback: Optional[Dict[str, Any]] = Field(None, description="User feedback")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")

