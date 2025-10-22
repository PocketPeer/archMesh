"""
Database models for Vibe Coding Tool

This module defines the database models for storing code generations,
parsed intents, and related metadata.
"""

from sqlalchemy import Column, String, Text, DateTime, JSON, ForeignKey, Integer, Float, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from app.core.database import Base


class CodeGeneration(Base):
    """Database model for storing code generation requests and results"""
    
    __tablename__ = "code_generations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True)
    
    # Input data
    user_input = Column(Text, nullable=False)
    parsed_intent = Column(JSON, nullable=True)  # Store ParsedIntent as JSON
    context_data = Column(JSON, nullable=True)   # Store UnifiedContext as JSON
    
    # Generated code
    generated_code = Column(Text, nullable=True)
    language = Column(String(50), nullable=True)
    framework = Column(String(100), nullable=True)
    
    # Metadata
    generation_time_ms = Column(Integer, nullable=True)
    token_count = Column(Integer, nullable=True)
    cost_usd = Column(Float, nullable=True)
    
    # Quality metrics
    syntax_valid = Column(Boolean, default=False)
    test_passed = Column(Boolean, default=False)
    quality_score = Column(Float, nullable=True)
    
    # Status tracking
    status = Column(String(50), default="pending")  # pending, completed, failed, executing
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="code_generations")
    project = relationship("Project", back_populates="code_generations")
    executions = relationship("CodeExecution", back_populates="generation", cascade="all, delete-orphan")


class CodeExecution(Base):
    """Database model for storing code execution results"""
    
    __tablename__ = "code_executions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    generation_id = Column(UUID(as_uuid=True), ForeignKey("code_generations.id"), nullable=False)
    
    # Execution details
    execution_type = Column(String(50), nullable=False)  # test, run, lint, format
    language = Column(String(50), nullable=False)
    
    # Results
    exit_code = Column(Integer, nullable=True)
    stdout = Column(Text, nullable=True)
    stderr = Column(Text, nullable=True)
    execution_time_ms = Column(Integer, nullable=True)
    
    # Quality metrics
    test_count = Column(Integer, nullable=True)
    test_passed = Column(Integer, nullable=True)
    test_failed = Column(Integer, nullable=True)
    coverage_percentage = Column(Float, nullable=True)
    
    # Status
    status = Column(String(50), default="pending")  # pending, completed, failed, timeout
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    generation = relationship("CodeGeneration", back_populates="executions")


class MCPToolUsage(Base):
    """Database model for tracking MCP tool usage"""
    
    __tablename__ = "mcp_tool_usage"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    generation_id = Column(UUID(as_uuid=True), ForeignKey("code_generations.id"), nullable=False)
    
    # Tool details
    tool_name = Column(String(100), nullable=False)
    server_name = Column(String(100), nullable=False)
    parameters = Column(JSON, nullable=True)
    
    # Results
    success = Column(Boolean, default=False)
    result_data = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    execution_time_ms = Column(Integer, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# Pydantic models for API and business logic

class ParsedIntent(BaseModel):
    """Parsed intent from natural language input"""
    
    intent_type: str = Field(..., description="Type of intent: create_api_endpoint, refactor_code, etc.")
    confidence_score: float = Field(default=0.8, ge=0.0, le=1.0, description="Confidence score for the parsed intent")
    requirements: List[str] = Field(default_factory=list, description="Specific requirements")
    entities: Dict[str, Any] = Field(default_factory=dict, description="Extracted entities")
    constraints: List[str] = Field(default_factory=list, description="Constraints and limitations")
    context_hints: List[str] = Field(default_factory=list, description="Context hints and suggestions")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class UnifiedContext(BaseModel):
    """Unified context gathered from multiple sources"""
    
    project_structure: Dict[str, Any] = Field(default_factory=dict, description="Project structure context")
    existing_code: Dict[str, Any] = Field(default_factory=dict, description="Existing code patterns and examples")
    documentation: Dict[str, Any] = Field(default_factory=dict, description="Documentation and examples")
    dependencies: Dict[str, Any] = Field(default_factory=dict, description="Dependencies and packages")
    quality_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Overall quality score of the context")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When this context was created")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class GeneratedCode(BaseModel):
    """Generated code result"""
    
    code: str = Field(..., description="Generated code")
    language: str = Field(..., description="Programming language")
    framework: Optional[str] = Field(None, description="Framework used")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Generation metadata")
    files: List[Dict[str, str]] = Field(default_factory=list, description="Multiple files if applicable")
    dependencies: List[str] = Field(default_factory=list, description="Required dependencies")
    instructions: str = Field(default="", description="Setup and usage instructions")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class CodeGenerationRequest(BaseModel):
    """Request model for code generation"""
    
    intent: ParsedIntent = Field(..., description="Parsed intent for code generation")
    context: UnifiedContext = Field(..., description="Unified context for code generation")
    language: str = Field(..., description="Programming language")
    framework: str = Field(..., description="Framework")
    output_format: str = Field(default="file", description="Output format: file, string, etc.")
    custom_template: Optional[str] = Field(None, description="Custom template to use")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class CodeGenerationResponse(BaseModel):
    """Response model for code generation"""
    
    success: bool = Field(..., description="Whether code generation was successful")
    generated_code: Optional[str] = Field(None, description="Generated code")
    language: str = Field(..., description="Programming language")
    framework: str = Field(..., description="Framework")
    validation_passed: bool = Field(default=False, description="Whether validation passed")
    syntax_check_passed: bool = Field(default=False, description="Whether syntax check passed")
    best_practices_passed: bool = Field(default=False, description="Whether best practices check passed")
    generation_time: float = Field(default=0.0, description="Time taken for generation")
    template_used: Optional[str] = Field(None, description="Template used for generation")
    context_integration_score: float = Field(default=0.0, description="How well context was integrated")
    template_loading_time: float = Field(default=0.0, description="Time taken to load template")
    validation_time: float = Field(default=0.0, description="Time taken for validation")
    syntax_check_time: float = Field(default=0.0, description="Time taken for syntax check")
    best_practices_time: float = Field(default=0.0, description="Time taken for best practices check")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ContextSource(BaseModel):
    """Represents a single context source"""
    source_type: str = Field(..., description="Type of context source (project, code, docs, etc.)")
    content: Dict[str, Any] = Field(..., description="Context content from this source")
    quality_score: float = Field(default=0.8, ge=0.0, le=1.0, description="Quality score for this source")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When this context was gathered")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata about the source")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ContextAggregationRequest(BaseModel):
    """Request schema for context aggregation"""
    intent: ParsedIntent = Field(..., description="Parsed intent for context gathering")
    include_sources: List[str] = Field(default_factory=lambda: ["project", "code", "docs", "dependencies"], description="Context sources to include")
    quality_threshold: float = Field(default=0.7, ge=0.0, le=1.0, description="Minimum quality threshold for context")
    max_context_length: int = Field(default=5000, gt=0, description="Maximum context length")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ContextAggregationResponse(BaseModel):
    """Response schema for context aggregation"""
    success: bool = Field(..., description="Whether context aggregation was successful")
    unified_context: Optional[UnifiedContext] = Field(None, description="Unified context if successful")
    error: Optional[str] = Field(None, description="Error message if aggregation failed")
    execution_time: float = Field(..., description="Time taken for context aggregation")
    sources_used: List[ContextSource] = Field(default_factory=list, description="Context sources that were used")
    quality_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Overall quality score of aggregated context")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
