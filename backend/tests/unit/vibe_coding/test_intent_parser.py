"""
TDD Tests for Intent Parser - RED Phase

This module contains comprehensive tests for the IntentParser class.
Following TDD methodology: Write failing tests first, then implement to make them pass.
"""

import pytest
from unittest.mock import patch, AsyncMock
from app.vibe_coding.intent_parser import IntentParser
from app.vibe_coding.models import ParsedIntent
from app.core.exceptions import IntentParseError, LLMError
import json


@pytest.fixture
def intent_parser():
    """Create IntentParser instance for testing"""
    return IntentParser()


@pytest.fixture
def sample_user_inputs():
    """Sample user inputs for testing different intent types"""
    return {
        "generate_endpoint": "Create a FastAPI endpoint for user login",
        "generate_model": "Generate a User model with email and password fields",
        "refactor_function": "Refactor this function to be more efficient",
        "create_tests": "Write unit tests for the authentication service",
        "explain_code": "Explain how this authentication flow works",
        "fix_bug": "Fix the memory leak in the data processing function",
        "complex_request": "Create a REST API with user authentication, role-based access control, and audit logging using FastAPI and PostgreSQL",
        "javascript_request": "Create a React component for user profile management",
        "typescript_request": "Build a TypeScript service for handling payment processing"
    }


@pytest.fixture
def expected_intents():
    """Expected parsed intents for sample inputs"""
    return {
        "generate_endpoint": ParsedIntent(
            action="generate",
            target="endpoint",
            language="python",
            framework="fastapi",
            purpose="user login",
            keywords=["endpoint", "login", "user"],
            complexity="medium",
            requirements=["authentication", "user management"]
        ),
        "generate_model": ParsedIntent(
            action="generate",
            target="model",
            language="python",
            framework=None,
            purpose="user data model",
            keywords=["model", "user", "email", "password"],
            complexity="low",
            requirements=["data modeling", "validation"]
        ),
        "refactor_function": ParsedIntent(
            action="refactor",
            target="function",
            language="python",
            framework=None,
            purpose="improve efficiency",
            keywords=["refactor", "function", "efficient"],
            complexity="medium",
            requirements=["performance optimization"]
        ),
        "create_tests": ParsedIntent(
            action="test",
            target="service",
            language="python",
            framework=None,
            purpose="unit testing",
            keywords=["tests", "unit", "authentication", "service"],
            complexity="medium",
            requirements=["test coverage", "unit testing"]
        ),
        "explain_code": ParsedIntent(
            action="explain",
            target="flow",
            language="python",
            framework=None,
            purpose="code explanation",
            keywords=["explain", "authentication", "flow"],
            complexity="low",
            requirements=["documentation", "explanation"]
        ),
        "fix_bug": ParsedIntent(
            action="fix",
            target="function",
            language="python",
            framework=None,
            purpose="bug fix",
            keywords=["fix", "memory", "leak", "data", "processing"],
            complexity="high",
            requirements=["bug fixing", "memory management"]
        )
    }


class TestIntentParser:
    """Test suite for IntentParser class"""
    
    @pytest.mark.asyncio
    async def test_parse_generate_endpoint_intent(self, intent_parser, sample_user_inputs):
        """Test parsing generate endpoint intent"""
        # Arrange
        user_input = sample_user_inputs["generate_endpoint"]
        
        # Act
        result = await intent_parser.parse(user_input)
        
        # Assert
        assert isinstance(result, ParsedIntent)
        assert result.action == "generate"
        assert result.target == "endpoint"
        assert result.language == "python"
        assert result.framework == "fastapi"
        assert "user login" in result.purpose.lower()
        assert "endpoint" in result.keywords
        assert "login" in result.keywords
        assert result.complexity in ["low", "medium", "high"]
    
    @pytest.mark.asyncio
    async def test_parse_generate_model_intent(self, intent_parser, sample_user_inputs):
        """Test parsing generate model intent"""
        # Arrange
        user_input = sample_user_inputs["generate_model"]
        
        # Act
        result = await intent_parser.parse(user_input)
        
        # Assert
        assert isinstance(result, ParsedIntent)
        assert result.action == "generate"
        assert result.target == "model"
        assert result.language == "python"
        assert result.framework is None or result.framework == ""
        assert "user" in result.purpose.lower()
        assert "model" in result.keywords
        assert "email" in result.keywords
        assert "password" in result.keywords
    
    @pytest.mark.asyncio
    async def test_parse_refactor_intent(self, intent_parser, sample_user_inputs):
        """Test parsing refactor intent"""
        # Arrange
        user_input = sample_user_inputs["refactor_function"]
        
        # Act
        result = await intent_parser.parse(user_input)
        
        # Assert
        assert isinstance(result, ParsedIntent)
        assert result.action == "refactor"
        assert result.target == "function"
        assert result.language == "python"
        assert "refactor" in result.keywords
        assert "efficient" in result.keywords or "efficiency" in result.keywords
    
    @pytest.mark.asyncio
    async def test_parse_test_intent(self, intent_parser, sample_user_inputs):
        """Test parsing test creation intent"""
        # Arrange
        user_input = sample_user_inputs["create_tests"]
        
        # Act
        result = await intent_parser.parse(user_input)
        
        # Assert
        assert isinstance(result, ParsedIntent)
        assert result.action == "test"
        assert result.target in ["service", "function", "component"]
        assert result.language == "python"
        assert "test" in result.keywords or "tests" in result.keywords
        assert "authentication" in result.keywords
    
    @pytest.mark.asyncio
    async def test_parse_explain_intent(self, intent_parser, sample_user_inputs):
        """Test parsing explain intent"""
        # Arrange
        user_input = sample_user_inputs["explain_code"]
        
        # Act
        result = await intent_parser.parse(user_input)
        
        # Assert
        assert isinstance(result, ParsedIntent)
        assert result.action == "explain"
        assert result.target in ["flow", "code", "function", "component"]
        assert result.language == "python"
        assert "explain" in result.keywords
        assert "authentication" in result.keywords
    
    @pytest.mark.asyncio
    async def test_parse_fix_intent(self, intent_parser, sample_user_inputs):
        """Test parsing fix intent"""
        # Arrange
        user_input = sample_user_inputs["fix_bug"]
        
        # Act
        result = await intent_parser.parse(user_input)
        
        # Assert
        assert isinstance(result, ParsedIntent)
        assert result.action == "fix"
        assert result.target in ["function", "code", "component"]
        assert result.language == "python"
        assert "fix" in result.keywords
        assert "memory" in result.keywords
        assert "leak" in result.keywords
    
    @pytest.mark.asyncio
    async def test_parse_javascript_intent(self, intent_parser, sample_user_inputs):
        """Test parsing JavaScript/React intent"""
        # Arrange
        user_input = sample_user_inputs["javascript_request"]
        
        # Act
        result = await intent_parser.parse(user_input)
        
        # Assert
        assert isinstance(result, ParsedIntent)
        assert result.action == "generate"
        assert result.target in ["component", "service"]
        assert result.language == "javascript"
        assert result.framework == "react"
        assert "react" in result.keywords
        assert "component" in result.keywords
    
    @pytest.mark.asyncio
    async def test_parse_typescript_intent(self, intent_parser, sample_user_inputs):
        """Test parsing TypeScript intent"""
        # Arrange
        user_input = sample_user_inputs["typescript_request"]
        
        # Act
        result = await intent_parser.parse(user_input)
        
        # Assert
        assert isinstance(result, ParsedIntent)
        assert result.action == "generate"
        assert result.target in ["service", "component"]
        assert result.language == "typescript"
        assert "typescript" in result.keywords
        assert "service" in result.keywords
    
    @pytest.mark.asyncio
    async def test_parse_complex_intent(self, intent_parser, sample_user_inputs):
        """Test parsing complex multi-requirement intent"""
        # Arrange
        user_input = sample_user_inputs["complex_request"]
        
        # Act
        result = await intent_parser.parse(user_input)
        
        # Assert
        assert isinstance(result, ParsedIntent)
        assert result.action == "generate"
        assert result.target in ["api", "endpoint", "service"]
        assert result.language == "python"
        assert result.framework == "fastapi"
        assert result.complexity == "high"
        assert len(result.requirements) > 2
        assert any("authentication" in req.lower() for req in result.requirements)
        assert any("access control" in req.lower() or "rbac" in req.lower() for req in result.requirements)
    
    @pytest.mark.asyncio
    async def test_parse_empty_input(self, intent_parser):
        """Test parsing empty input raises error"""
        # Arrange
        user_input = ""
        
        # Act & Assert
        with pytest.raises(IntentParseError):
            await intent_parser.parse(user_input)
    
    @pytest.mark.asyncio
    async def test_parse_whitespace_only_input(self, intent_parser):
        """Test parsing whitespace-only input raises error"""
        # Arrange
        user_input = "   \n\t   "
        
        # Act & Assert
        with pytest.raises(IntentParseError):
            await intent_parser.parse(user_input)
    
    @pytest.mark.asyncio
    async def test_parse_invalid_input(self, intent_parser):
        """Test parsing invalid input raises error"""
        # Arrange
        user_input = "asdfghjkl qwertyuiop zxcvbnm"
        
        # Act & Assert
        with pytest.raises(IntentParseError):
            await intent_parser.parse(user_input)
    
    @pytest.mark.asyncio
    async def test_parse_llm_timeout(self, intent_parser, sample_user_inputs):
        """Test handling LLM timeout error"""
        # Arrange
        user_input = sample_user_inputs["generate_endpoint"]
        
        with patch.object(intent_parser, '_call_llm', side_effect=LLMError("Timeout")):
            # Act & Assert
            with pytest.raises(IntentParseError):
                await intent_parser.parse(user_input)
    
    @pytest.mark.asyncio
    async def test_parse_llm_invalid_response(self, intent_parser, sample_user_inputs):
        """Test handling invalid LLM response"""
        # Arrange
        user_input = sample_user_inputs["generate_endpoint"]
        
        with patch.object(intent_parser, '_call_llm', return_value="invalid json"):
            # Act & Assert
            with pytest.raises(IntentParseError):
                await intent_parser.parse(user_input)
    
    @pytest.mark.asyncio
    async def test_parse_llm_missing_fields(self, intent_parser, sample_user_inputs):
        """Test handling LLM response with missing required fields"""
        # Arrange
        user_input = sample_user_inputs["generate_endpoint"]
        incomplete_response = json.dumps({
            "action": "generate",
            "target": "endpoint"
            # Missing required fields
        })
        
        with patch.object(intent_parser, '_call_llm', return_value=incomplete_response):
            # Act & Assert
            with pytest.raises(IntentParseError):
                await intent_parser.parse(user_input)
    
    @pytest.mark.asyncio
    async def test_parse_confidence_scoring(self, intent_parser, sample_user_inputs):
        """Test that parsed intents have confidence scores"""
        # Arrange
        user_input = sample_user_inputs["generate_endpoint"]
        
        # Act
        result = await intent_parser.parse(user_input)
        
        # Assert
        assert hasattr(result, 'confidence_score') or hasattr(result, 'confidence')
        # Confidence should be a reasonable value
        confidence = getattr(result, 'confidence_score', getattr(result, 'confidence', 0))
        assert 0.0 <= confidence <= 1.0
    
    @pytest.mark.asyncio
    async def test_parse_performance(self, intent_parser, sample_user_inputs):
        """Test that parsing completes within reasonable time"""
        import time
        
        # Arrange
        user_input = sample_user_inputs["generate_endpoint"]
        
        # Act
        start_time = time.time()
        result = await intent_parser.parse(user_input)
        end_time = time.time()
        
        # Assert
        assert isinstance(result, ParsedIntent)
        assert (end_time - start_time) < 5.0  # Should complete within 5 seconds
    
    @pytest.mark.asyncio
    async def test_parse_keyword_extraction(self, intent_parser, sample_user_inputs):
        """Test that keywords are properly extracted"""
        # Arrange
        user_input = sample_user_inputs["complex_request"]
        
        # Act
        result = await intent_parser.parse(user_input)
        
        # Assert
        assert len(result.keywords) > 0
        assert any(keyword in user_input.lower() for keyword in result.keywords)
        # Should extract technical terms
        technical_terms = ["api", "authentication", "fastapi", "postgresql", "rest"]
        assert any(term in [kw.lower() for kw in result.keywords] for term in technical_terms)
    
    @pytest.mark.asyncio
    async def test_parse_requirement_extraction(self, intent_parser, sample_user_inputs):
        """Test that requirements are properly extracted"""
        # Arrange
        user_input = sample_user_inputs["complex_request"]
        
        # Act
        result = await intent_parser.parse(user_input)
        
        # Assert
        assert len(result.requirements) > 0
        # Should extract functional requirements
        functional_requirements = ["authentication", "access control", "audit logging"]
        assert any(req in [r.lower() for r in result.requirements] for req in functional_requirements)
    
    @pytest.mark.asyncio
    async def test_parse_complexity_assessment(self, intent_parser, sample_user_inputs):
        """Test that complexity is properly assessed"""
        # Arrange
        simple_input = sample_user_inputs["generate_model"]
        complex_input = sample_user_inputs["complex_request"]
        
        # Act
        simple_result = await intent_parser.parse(simple_input)
        complex_result = await intent_parser.parse(complex_input)
        
        # Assert
        assert simple_result.complexity in ["low", "medium", "high"]
        assert complex_result.complexity in ["low", "medium", "high"]
        # Complex request should generally be higher complexity
        complexity_order = {"low": 1, "medium": 2, "high": 3}
        assert complexity_order[complex_result.complexity] >= complexity_order[simple_result.complexity]
