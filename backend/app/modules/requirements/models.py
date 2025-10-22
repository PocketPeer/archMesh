"""
Simple data models for Requirements Module
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class InputType(str, Enum):
    """Types of input supported"""
    TEXT = "text"
    FILE = "file"
    URL = "url"


class RequirementType(str, Enum):
    """Types of requirements"""
    BUSINESS_GOAL = "business_goal"
    FUNCTIONAL = "functional"
    NON_FUNCTIONAL = "non_functional"
    CONSTRAINT = "constraint"
    STAKEHOLDER = "stakeholder"


class ValidationStatus(str, Enum):
    """Validation status"""
    VALID = "valid"
    INVALID = "invalid"
    WARNING = "warning"


class ParsedInput(BaseModel):
    """Simple parsed input structure"""
    text: str
    input_type: InputType
    metadata: Dict[str, Any] = Field(default_factory=dict)
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)


class ExtractedRequirement(BaseModel):
    """Simple extracted requirement"""
    id: str
    type: RequirementType
    title: str
    description: str
    priority: str = "medium"
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)


class ExtractedRequirements(BaseModel):
    """Collection of extracted requirements"""
    business_goals: List[ExtractedRequirement] = Field(default_factory=list)
    functional_requirements: List[ExtractedRequirement] = Field(default_factory=list)
    non_functional_requirements: List[ExtractedRequirement] = Field(default_factory=list)
    constraints: List[ExtractedRequirement] = Field(default_factory=list)
    stakeholders: List[ExtractedRequirement] = Field(default_factory=list)


class ValidationResult(BaseModel):
    """Simple validation result"""
    status: ValidationStatus
    score: float = Field(ge=0.0, le=1.0)
    issues: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)


class StructuredRequirements(BaseModel):
    """Final structured requirements"""
    requirements: ExtractedRequirements
    validation: ValidationResult
    metadata: Dict[str, Any] = Field(default_factory=dict)
