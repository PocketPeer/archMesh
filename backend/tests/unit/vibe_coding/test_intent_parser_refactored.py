"""
Tests for refactored Intent Parser functionality.

This module tests the new features added during the REFACTOR phase:
- Performance tracking and statistics
- Caching functionality
- Configuration management
- Enhanced error handling
- Constants usage
"""

import pytest
import asyncio
import time
from unittest.mock import AsyncMock, patch, MagicMock
from app.vibe_coding.intent_parser import IntentParser, IntentParserConfig, IntentParserConstants
from app.vibe_coding.models import ParsedIntent
from app.core.exceptions import IntentParseError


@pytest.fixture
def intent_parser_config():
    """Create IntentParserConfig for testing"""
    return IntentParserConfig(
        max_tokens=500,
        temperature=0.2,
        timeout_seconds=15,
        enable_caching=True,
        cache_size=50,
        confidence_threshold=0.7
    )


@pytest.fixture
def intent_parser_with_config(intent_parser_config):
    """Create IntentParser with custom config"""
    return IntentParser(config=intent_parser_config)


@pytest.fixture
def intent_parser_default():
    """Create IntentParser with default config"""
    return IntentParser()


@pytest.mark.asyncio
class TestIntentParserRefactored:
    """Test refactored Intent Parser functionality"""
    
    async def test_config_initialization(self, intent_parser_config):
        """Test that IntentParser initializes with custom config"""
        parser = IntentParser(config=intent_parser_config)
        
        assert parser.config.max_tokens == 500
        assert parser.config.temperature == 0.2
        assert parser.config.timeout_seconds == 15
        assert parser.config.enable_caching is True
        assert parser.config.cache_size == 50
        assert parser.config.confidence_threshold == 0.7
    
    async def test_default_config_initialization(self, intent_parser_default):
        """Test that IntentParser initializes with default config"""
        parser = intent_parser_default
        
        assert parser.config.max_tokens == 1000
        assert parser.config.temperature == 0.1
        assert parser.config.timeout_seconds == 30
        assert parser.config.enable_caching is True
        assert parser.config.cache_size == 100
        assert parser.config.confidence_threshold == 0.5
    
    async def test_performance_stats_initialization(self, intent_parser_default):
        """Test that performance stats are properly initialized"""
        parser = intent_parser_default
        
        stats = parser.get_performance_stats()
        
        assert stats["total_parses"] == 0
        assert stats["successful_parses"] == 0
        assert stats["failed_parses"] == 0
        assert stats["average_parse_time"] == 0.0
        assert stats["success_rate"] == 0.0
    
    async def test_performance_stats_tracking(self, intent_parser_default):
        """Test that performance stats are tracked correctly"""
        parser = intent_parser_default
        
        # Simulate successful parse
        with patch.object(parser, '_call_llm', return_value='{"action": "generate", "target": "endpoint", "language": "python", "framework": "fastapi", "purpose": "test", "keywords": [], "complexity": "low", "requirements": [], "confidence_score": 0.9}'):
            await parser.parse("Create a test endpoint")
        
        stats = parser.get_performance_stats()
        
        assert stats["total_parses"] == 1
        assert stats["successful_parses"] == 1
        assert stats["failed_parses"] == 0
        assert stats["success_rate"] == 1.0
        assert stats["average_parse_time"] > 0
    
    async def test_performance_stats_failure_tracking(self, intent_parser_default):
        """Test that performance stats track failures correctly"""
        parser = intent_parser_default
        
        # Simulate failed parse
        with patch.object(parser, '_call_llm', side_effect=IntentParseError("Test error")):
            try:
                await parser.parse("Create a test endpoint")
            except IntentParseError:
                pass
        
        stats = parser.get_performance_stats()
        
        assert stats["total_parses"] == 1
        assert stats["successful_parses"] == 0
        assert stats["failed_parses"] == 1
        assert stats["success_rate"] == 0.0
    
    async def test_caching_enabled(self, intent_parser_with_config):
        """Test that caching works when enabled"""
        parser = intent_parser_with_config
        
        # First parse should cache the result
        with patch.object(parser, '_call_llm', return_value='{"action": "generate", "target": "endpoint", "language": "python", "framework": "fastapi", "purpose": "test", "keywords": [], "complexity": "low", "requirements": [], "confidence_score": 0.9}'):
            result1 = await parser.parse("Create a test endpoint")
        
        # Second parse should use cache (no LLM call)
        with patch.object(parser, '_call_llm') as mock_call:
            result2 = await parser.parse("Create a test endpoint")
            mock_call.assert_not_called()
        
        # Results should be identical
        assert result1.action == result2.action
        assert result1.target == result2.target
    
    async def test_caching_disabled(self):
        """Test that caching is bypassed when disabled"""
        config = IntentParserConfig(enable_caching=False)
        parser = IntentParser(config=config)
        
        # Both parses should call LLM
        with patch.object(parser, '_call_llm', return_value='{"action": "generate", "target": "endpoint", "language": "python", "framework": "fastapi", "purpose": "test", "keywords": [], "complexity": "low", "requirements": [], "confidence_score": 0.9}') as mock_call:
            await parser.parse("Create a test endpoint")
            await parser.parse("Create a test endpoint")
            
            assert mock_call.call_count == 2
    
    async def test_cache_size_limit(self):
        """Test that cache respects size limit"""
        config = IntentParserConfig(cache_size=2)
        parser = IntentParser(config=config)
        
        # Parse 3 different inputs
        with patch.object(parser, '_call_llm', return_value='{"action": "generate", "target": "endpoint", "language": "python", "framework": "fastapi", "purpose": "test", "keywords": [], "complexity": "low", "requirements": [], "confidence_score": 0.9}'):
            await parser.parse("Create endpoint 1")
            await parser.parse("Create endpoint 2")
            await parser.parse("Create endpoint 3")
        
        # Cache should only contain 2 entries
        assert len(parser._cache) == 2
    
    async def test_input_validation_enhanced(self, intent_parser_default):
        """Test enhanced input validation"""
        parser = intent_parser_default
        
        # Test too short input
        with pytest.raises(IntentParseError, match="User input too short"):
            await parser.parse("ab")
        
        # Test too long input
        long_input = "a" * 2001
        with pytest.raises(IntentParseError, match="User input too long"):
            await parser.parse(long_input)
    
    async def test_constants_usage(self):
        """Test that constants are properly defined and used"""
        # Test action constants
        assert "generate" in IntentParserConstants.ACTIONS
        assert "refactor" in IntentParserConstants.ACTIONS
        assert "test" in IntentParserConstants.ACTIONS
        assert "explain" in IntentParserConstants.ACTIONS
        assert "fix" in IntentParserConstants.ACTIONS
        
        # Test target constants
        assert "endpoint" in IntentParserConstants.TARGETS
        assert "model" in IntentParserConstants.TARGETS
        assert "function" in IntentParserConstants.TARGETS
        
        # Test language constants
        assert "python" in IntentParserConstants.LANGUAGES
        assert "javascript" in IntentParserConstants.LANGUAGES
        assert "typescript" in IntentParserConstants.LANGUAGES
        
        # Test framework constants
        assert "fastapi" in IntentParserConstants.FRAMEWORKS
        assert "react" in IntentParserConstants.FRAMEWORKS
        
        # Test complexity constants
        assert "low" in IntentParserConstants.COMPLEXITY_LEVELS
        assert "medium" in IntentParserConstants.COMPLEXITY_LEVELS
        assert "high" in IntentParserConstants.COMPLEXITY_LEVELS
        
        # Test intent keywords
        assert "create" in IntentParserConstants.INTENT_KEYWORDS
        assert "generate" in IntentParserConstants.INTENT_KEYWORDS
        
        # Test performance thresholds
        assert IntentParserConstants.MAX_PARSING_TIME == 5.0
        assert IntentParserConstants.MIN_CONFIDENCE_SCORE == 0.0
        assert IntentParserConstants.MAX_CONFIDENCE_SCORE == 1.0
    
    async def test_enhanced_error_messages(self, intent_parser_default):
        """Test that error messages include helpful information"""
        parser = intent_parser_default
        
        # Test invalid action error message
        with patch.object(parser, '_call_llm', return_value='{"action": "invalid", "target": "endpoint", "language": "python", "framework": "fastapi", "purpose": "test", "keywords": [], "complexity": "low", "requirements": [], "confidence_score": 0.9}'):
            with pytest.raises(IntentParseError, match="Invalid action.*Valid actions"):
                await parser.parse("Create a test endpoint")
        
        # Test invalid target error message
        with patch.object(parser, '_call_llm', return_value='{"action": "generate", "target": "invalid", "language": "python", "framework": "fastapi", "purpose": "test", "keywords": [], "complexity": "low", "requirements": [], "confidence_score": 0.9}'):
            with pytest.raises(IntentParseError, match="Invalid target.*Valid targets"):
                await parser.parse("Create a test endpoint")
        
        # Test invalid language error message
        with patch.object(parser, '_call_llm', return_value='{"action": "generate", "target": "endpoint", "language": "invalid", "framework": "fastapi", "purpose": "test", "keywords": [], "complexity": "low", "requirements": [], "confidence_score": 0.9}'):
            with pytest.raises(IntentParseError, match="Invalid language.*Valid languages"):
                await parser.parse("Create a test endpoint")
    
    async def test_mock_responses_initialization(self, intent_parser_default):
        """Test that mock responses are properly initialized"""
        parser = intent_parser_default
        
        # Check that mock responses are loaded
        assert len(parser._mock_responses) > 0
        
        # Check specific mock responses
        assert "Create a FastAPI endpoint for user login" in parser._mock_responses
        assert "Generate a User model with email and password fields" in parser._mock_responses
        assert "Refactor this function to be more efficient" in parser._mock_responses
    
    async def test_parse_time_tracking(self, intent_parser_default):
        """Test that parse time is tracked accurately"""
        parser = intent_parser_default
        
        # Mock a slow LLM response
        async def slow_llm_response(*args, **kwargs):
            await asyncio.sleep(0.1)  # Simulate 100ms delay
            return '{"action": "generate", "target": "endpoint", "language": "python", "framework": "fastapi", "purpose": "test", "keywords": [], "complexity": "low", "requirements": [], "confidence_score": 0.9}'
        
        with patch.object(parser, '_call_llm', side_effect=slow_llm_response):
            await parser.parse("Create a test endpoint")
        
        stats = parser.get_performance_stats()
        
        # Parse time should be at least 100ms
        assert stats["average_parse_time"] >= 0.1
    
    async def test_config_immutability(self, intent_parser_config):
        """Test that config is properly isolated"""
        # Create separate config objects
        config1 = IntentParserConfig(max_tokens=500, temperature=0.2, timeout_seconds=15, enable_caching=True, cache_size=50, confidence_threshold=0.7)
        config2 = IntentParserConfig(max_tokens=500, temperature=0.2, timeout_seconds=15, enable_caching=True, cache_size=50, confidence_threshold=0.7)
        
        parser1 = IntentParser(config=config1)
        parser2 = IntentParser(config=config2)
        
        # Modify config for parser1
        parser1.config.max_tokens = 999
        
        # Parser2 config should be unchanged
        assert parser2.config.max_tokens == 500
        assert parser1.config.max_tokens == 999


class TestIntentParserConstants:
    """Test IntentParserConstants class"""
    
    def test_constants_completeness(self):
        """Test that all constants are properly defined"""
        # Test that all required constants exist
        assert hasattr(IntentParserConstants, 'ACTIONS')
        assert hasattr(IntentParserConstants, 'TARGETS')
        assert hasattr(IntentParserConstants, 'LANGUAGES')
        assert hasattr(IntentParserConstants, 'FRAMEWORKS')
        assert hasattr(IntentParserConstants, 'COMPLEXITY_LEVELS')
        assert hasattr(IntentParserConstants, 'INTENT_KEYWORDS')
        assert hasattr(IntentParserConstants, 'MAX_PARSING_TIME')
        assert hasattr(IntentParserConstants, 'MIN_CONFIDENCE_SCORE')
        assert hasattr(IntentParserConstants, 'MAX_CONFIDENCE_SCORE')
    
    def test_constants_values(self):
        """Test that constants have expected values"""
        # Test performance thresholds
        assert IntentParserConstants.MAX_PARSING_TIME == 5.0
        assert IntentParserConstants.MIN_CONFIDENCE_SCORE == 0.0
        assert IntentParserConstants.MAX_CONFIDENCE_SCORE == 1.0
        
        # Test that lists are not empty
        assert len(IntentParserConstants.ACTIONS) > 0
        assert len(IntentParserConstants.TARGETS) > 0
        assert len(IntentParserConstants.LANGUAGES) > 0
        assert len(IntentParserConstants.FRAMEWORKS) > 0
        assert len(IntentParserConstants.COMPLEXITY_LEVELS) > 0
        assert len(IntentParserConstants.INTENT_KEYWORDS) > 0


class TestIntentParserConfig:
    """Test IntentParserConfig class"""
    
    def test_default_config_values(self):
        """Test default configuration values"""
        config = IntentParserConfig()
        
        assert config.max_tokens == 1000
        assert config.temperature == 0.1
        assert config.timeout_seconds == 30
        assert config.enable_caching is True
        assert config.cache_size == 100
        assert config.confidence_threshold == 0.5
    
    def test_custom_config_values(self):
        """Test custom configuration values"""
        config = IntentParserConfig(
            max_tokens=500,
            temperature=0.2,
            timeout_seconds=15,
            enable_caching=False,
            cache_size=50,
            confidence_threshold=0.7
        )
        
        assert config.max_tokens == 500
        assert config.temperature == 0.2
        assert config.timeout_seconds == 15
        assert config.enable_caching is False
        assert config.cache_size == 50
        assert config.confidence_threshold == 0.7
    
    def test_config_immutability(self):
        """Test that config values can be modified"""
        config = IntentParserConfig()
        
        # Should be able to modify values
        config.max_tokens = 2000
        config.temperature = 0.5
        
        assert config.max_tokens == 2000
        assert config.temperature == 0.5
