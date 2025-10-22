"""
Simple data models for Vibe Coding Module
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class ProgrammingLanguage(str, Enum):
    """Supported programming languages"""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    CSHARP = "csharp"
    GO = "go"
    RUST = "rust"


class CodeComplexity(str, Enum):
    """Code complexity levels"""
    SIMPLE = "simple"
    MEDIUM = "medium"
    COMPLEX = "complex"


class ExecutionStatus(str, Enum):
    """Execution status"""
    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"
    RUNTIME_ERROR = "runtime_error"


class QualityLevel(str, Enum):
    """Code quality levels"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"


class GeneratedCode(BaseModel):
    """Simple generated code structure"""
    id: str
    language: ProgrammingLanguage
    code: str
    description: str
    complexity: CodeComplexity
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ExecutionResult(BaseModel):
    """Simple execution result"""
    status: ExecutionStatus
    output: str = ""
    error: str = ""
    execution_time: float = 0.0
    memory_usage: float = 0.0
    metadata: Dict[str, Any] = Field(default_factory=dict)


class QualityReport(BaseModel):
    """Simple quality report"""
    overall_quality: QualityLevel
    score: float = Field(ge=0.0, le=1.0)
    issues: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)
    metrics: Dict[str, Any] = Field(default_factory=dict)


class VibeCodingResult(BaseModel):
    """Complete vibe coding result"""
    generated_code: GeneratedCode
    execution_result: Optional[ExecutionResult] = None
    quality_report: Optional[QualityReport] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
