"""
Vibe Coding Tool - Natural Language to Code Generation

This module provides natural language interface for code generation that understands
architectural context, leverages MCP tools, and enables conversational development.

Components:
- IntentParser: Parse natural language input into structured intent
- ContextAggregator: Gather relevant context from multiple sources
- CodeGenerator: Generate code using LLM with context
- MCPIntegrationManager: Manage MCP server connections and tool invocations
- ExecutionSandbox: Safely execute generated code in isolated environment
"""

from .intent_parser import IntentParser
from .context_aggregator import ContextAggregator, ContextAggregatorConfig
from .unified_service import (
    VibeCodingService, VibeCodingConfig, VibeCodingRequest, VibeCodingResponse,
    ChatRequest, ChatResponse, SessionStatus, FeedbackRequest, FeedbackResponse,
    VibeCodingError, SessionNotFoundError, InvalidRequestError, HealthStatus
)
from .models import (
    CodeGeneration, ParsedIntent, UnifiedContext, GeneratedCode,
    ContextSource, ContextAggregationRequest, ContextAggregationResponse
)

__all__ = [
    "IntentParser",
    "ContextAggregator",
    "ContextAggregatorConfig",
    "VibeCodingService",
    "VibeCodingConfig",
    "VibeCodingRequest",
    "VibeCodingResponse",
    "ChatRequest",
    "ChatResponse",
    "SessionStatus",
    "FeedbackRequest",
    "FeedbackResponse",
    "VibeCodingError",
    "SessionNotFoundError",
    "InvalidRequestError",
    "HealthStatus",
    "CodeGeneration",
    "ParsedIntent",
    "UnifiedContext",
    "GeneratedCode",
    "ContextSource",
    "ContextAggregationRequest",
    "ContextAggregationResponse"
]
