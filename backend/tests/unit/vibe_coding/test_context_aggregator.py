"""
Tests for Context Aggregator component.

This module tests the Context Aggregator functionality for the Vibe Coding Tool.
The Context Aggregator is responsible for gathering and unifying context from
various sources to provide comprehensive information for code generation.

Test Categories:
- Context gathering from multiple sources
- Context unification and deduplication
- Context quality assessment
- Context filtering and prioritization
- Error handling and edge cases
- Performance and caching
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from app.vibe_coding.context_aggregator import ContextAggregator, ContextAggregatorConfig
from app.vibe_coding.models import UnifiedContext, ParsedIntent
from app.core.exceptions import ContextGatherError, VibeCodingError
import time


@pytest.fixture
def context_aggregator_config():
    """Create ContextAggregatorConfig for testing"""
    return ContextAggregatorConfig(
        max_context_sources=10,
        context_timeout=30,
        enable_caching=True,
        cache_size=50,
        quality_threshold=0.7,
        max_context_length=5000
    )


@pytest.fixture
def context_aggregator(context_aggregator_config):
    """Create ContextAggregator instance for testing"""
    return ContextAggregator(config=context_aggregator_config)


@pytest.fixture
def sample_parsed_intent():
    """Sample ParsedIntent for testing"""
    return ParsedIntent(
        action="generate",
        target="endpoint",
        language="python",
        framework="fastapi",
        purpose="Create a user authentication endpoint",
        keywords=["authentication", "endpoint", "user", "login"],
        complexity="medium",
        requirements=["Handle POST requests", "Validate credentials", "Return JWT token"],
        confidence_score=0.9
    )


@pytest.fixture
def sample_context_sources():
    """Sample context sources for testing"""
    return {
        "project_structure": {
            "files": ["app/main.py", "app/models/user.py", "app/auth/"],
            "frameworks": ["fastapi", "sqlalchemy"],
            "patterns": ["repository", "service layer"]
        },
        "existing_code": {
            "similar_endpoints": [
                {"path": "/api/v1/users", "method": "GET", "auth_required": True},
                {"path": "/api/v1/profile", "method": "PUT", "auth_required": True}
            ],
            "auth_patterns": ["JWT", "OAuth2", "session-based"]
        },
        "documentation": {
            "api_docs": "FastAPI authentication guide",
            "examples": ["JWT implementation", "OAuth2 setup"],
            "best_practices": ["secure endpoints", "token validation"]
        },
        "dependencies": {
            "installed_packages": ["fastapi", "python-jose", "passlib"],
            "version_constraints": ["fastapi>=0.68.0", "python-jose>=3.3.0"]
        }
    }


@pytest.mark.asyncio
class TestContextAggregator:
    """Test Context Aggregator functionality"""
    
    async def test_aggregate_context_success(self, context_aggregator, sample_parsed_intent, sample_context_sources):
        """Test successful context aggregation"""
        # Arrange
        with patch.object(context_aggregator, '_gather_project_context', return_value=sample_context_sources["project_structure"]):
            with patch.object(context_aggregator, '_gather_code_context', return_value=sample_context_sources["existing_code"]):
                with patch.object(context_aggregator, '_gather_documentation_context', return_value=sample_context_sources["documentation"]):
                    with patch.object(context_aggregator, '_gather_dependency_context', return_value=sample_context_sources["dependencies"]):
                        # Act
                        result = await context_aggregator.aggregate_context(sample_parsed_intent)
                        
                        # Assert
                        assert isinstance(result, UnifiedContext)
                        assert result.intent == sample_parsed_intent
                        assert result.project_structure is not None
                        assert result.existing_code is not None
                        assert result.documentation is not None
                        assert result.dependencies is not None
                        assert result.quality_score > 0.0
                        assert result.timestamp is not None
    
    async def test_aggregate_context_with_caching(self, context_aggregator, sample_parsed_intent):
        """Test context aggregation with caching enabled"""
        # First call should gather context
        with patch.object(context_aggregator, '_gather_all_context_sources', return_value={}):
            result1 = await context_aggregator.aggregate_context(sample_parsed_intent)
        
        # Second call should use cache
        with patch.object(context_aggregator, '_gather_all_context_sources') as mock_gather:
            result2 = await context_aggregator.aggregate_context(sample_parsed_intent)
            mock_gather.assert_not_called()
        
        # Results should be identical
        assert result1.intent == result2.intent
        assert result1.timestamp == result2.timestamp
    
    async def test_aggregate_context_caching_disabled(self, sample_parsed_intent):
        """Test context aggregation with caching disabled"""
        config = ContextAggregatorConfig(enable_caching=False)
        aggregator = ContextAggregator(config=config)
        
        # Both calls should gather context
        with patch.object(aggregator, '_gather_all_context_sources', return_value={}) as mock_gather:
            await aggregator.aggregate_context(sample_parsed_intent)
            await aggregator.aggregate_context(sample_parsed_intent)
            
            assert mock_gather.call_count == 2
    
    async def test_context_quality_assessment_high_quality(self, context_aggregator, sample_parsed_intent):
        """Test context quality assessment for high-quality context"""
        # Arrange
        high_quality_context = {
            "project_structure": {"files": ["app/main.py", "app/models/"], "frameworks": ["fastapi"]},
            "existing_code": {"similar_endpoints": [{"path": "/api/v1/users", "method": "GET"}]},
            "documentation": {"api_docs": "Comprehensive FastAPI guide"},
            "dependencies": {"installed_packages": ["fastapi", "python-jose"]}
        }
        
        with patch.object(context_aggregator, '_gather_all_context_sources', return_value=high_quality_context):
            # Act
            result = await context_aggregator.aggregate_context(sample_parsed_intent)
            
            # Assert
            assert result.quality_score >= 0.7
    
    async def test_context_quality_assessment_low_quality(self, context_aggregator, sample_parsed_intent):
        """Test context quality assessment for low-quality context"""
        # Arrange
        low_quality_context = {
            "project_structure": {},
            "existing_code": {},
            "documentation": {},
            "dependencies": {}
        }
        
        with patch.object(context_aggregator, '_gather_all_context_sources', return_value=low_quality_context):
            # Act
            result = await context_aggregator.aggregate_context(sample_parsed_intent)
            
            # Assert
            assert result.quality_score < 0.5
    
    async def test_context_filtering_and_prioritization(self, context_aggregator, sample_parsed_intent):
        """Test context filtering and prioritization"""
        # Arrange
        mixed_context = {
            "project_structure": {"files": ["app/main.py"], "frameworks": ["fastapi"]},
            "existing_code": {"similar_endpoints": [{"path": "/api/v1/users", "method": "GET"}]},
            "documentation": {"api_docs": "FastAPI guide"},
            "dependencies": {"installed_packages": ["fastapi"]},
            "irrelevant_data": {"unrelated": "information"}
        }
        
        with patch.object(context_aggregator, '_gather_all_context_sources', return_value=mixed_context):
            # Act
            result = await context_aggregator.aggregate_context(sample_parsed_intent)
            
            # Assert
            assert result.project_structure is not None
            assert result.existing_code is not None
            assert result.documentation is not None
            assert result.dependencies is not None
            # Irrelevant data should be filtered out
            assert not hasattr(result, 'irrelevant_data')
    
    async def test_context_aggregation_timeout(self, sample_parsed_intent):
        """Test context aggregation timeout handling"""
        config = ContextAggregatorConfig(context_timeout=1)  # 1 second timeout
        aggregator = ContextAggregator(config=config)
        
        # Mock slow context gathering by patching individual gather methods
        async def slow_gather(*args, **kwargs):
            await asyncio.sleep(2)  # Longer than timeout
            return {}
        
        with patch.object(aggregator, '_gather_project_context', side_effect=slow_gather):
            with patch.object(aggregator, '_gather_code_context', side_effect=slow_gather):
                with patch.object(aggregator, '_gather_documentation_context', side_effect=slow_gather):
                    with patch.object(aggregator, '_gather_dependency_context', side_effect=slow_gather):
                        # Act & Assert
                        with pytest.raises(ContextGatherError, match="Context aggregation timeout"):
                            await aggregator.aggregate_context(sample_parsed_intent)
    
    async def test_context_aggregation_partial_failure(self, context_aggregator, sample_parsed_intent):
        """Test context aggregation with partial source failures"""
        # Arrange
        def mock_gather_with_failure(*args, **kwargs):
            # Simulate some sources failing
            if "project_structure" in str(args):
                raise Exception("Project structure unavailable")
            return {"existing_code": {"similar_endpoints": []}}
        
        with patch.object(context_aggregator, '_gather_all_context_sources', side_effect=mock_gather_with_failure):
            # Act
            result = await context_aggregator.aggregate_context(sample_parsed_intent)
            
            # Assert
            assert isinstance(result, UnifiedContext)
            # Should still work with partial context
            assert result.existing_code is not None
    
    async def test_context_aggregation_empty_intent(self, context_aggregator):
        """Test context aggregation with empty intent"""
        # Arrange
        empty_intent = ParsedIntent(
            action="",
            target="",
            language="",
            framework="",
            purpose="",
            keywords=[],
            complexity="low",
            requirements=[],
            confidence_score=0.0
        )
        
        # Act & Assert
        with pytest.raises(ContextGatherError, match="Invalid intent provided"):
            await context_aggregator.aggregate_context(empty_intent)
    
    async def test_context_aggregation_performance(self, context_aggregator, sample_parsed_intent):
        """Test context aggregation performance"""
        # Arrange
        start_time = time.time()
        
        with patch.object(context_aggregator, '_gather_all_context_sources', return_value={}):
            # Act
            await context_aggregator.aggregate_context(sample_parsed_intent)
            
            # Assert
            elapsed_time = time.time() - start_time
            assert elapsed_time < 5.0  # Should complete within 5 seconds
    
    async def test_context_deduplication(self, context_aggregator, sample_parsed_intent):
        """Test context deduplication"""
        # Arrange
        duplicate_context = {
            "project_structure": {"files": ["app/main.py", "app/main.py"]},  # Duplicate file
            "existing_code": {"similar_endpoints": [
                {"path": "/api/v1/users", "method": "GET"},
                {"path": "/api/v1/users", "method": "GET"}  # Duplicate endpoint
            ]},
            "documentation": {"api_docs": "FastAPI guide"},
            "dependencies": {"installed_packages": ["fastapi", "fastapi"]}  # Duplicate package
        }
        
        with patch.object(context_aggregator, '_gather_all_context_sources', return_value=duplicate_context):
            # Act
            result = await context_aggregator.aggregate_context(sample_parsed_intent)
            
            # Assert
            # Duplicates should be removed
            if hasattr(result.project_structure, 'files'):
                assert len(result.project_structure['files']) == 1
            if hasattr(result.existing_code, 'similar_endpoints'):
                assert len(result.existing_code['similar_endpoints']) == 1
            if hasattr(result.dependencies, 'installed_packages'):
                assert len(result.dependencies['installed_packages']) == 1
    
    async def test_context_aggregation_with_large_context(self, context_aggregator, sample_parsed_intent):
        """Test context aggregation with large context data"""
        # Arrange
        large_context = {
            "project_structure": {"files": [f"app/file_{i}.py" for i in range(1000)]},
            "existing_code": {"similar_endpoints": [{"path": f"/api/v1/endpoint_{i}", "method": "GET"} for i in range(100)]},
            "documentation": {"api_docs": "x" * 10000},  # Large documentation
            "dependencies": {"installed_packages": [f"package_{i}" for i in range(100)]}
        }
        
        with patch.object(context_aggregator, '_gather_all_context_sources', return_value=large_context):
            # Act
            result = await context_aggregator.aggregate_context(sample_parsed_intent)
            
            # Assert
            assert isinstance(result, UnifiedContext)
            # Context should be truncated to max length
            assert len(str(result)) <= context_aggregator.config.max_context_length
    
    async def test_context_aggregation_error_handling(self, context_aggregator, sample_parsed_intent):
        """Test context aggregation error handling"""
        # Arrange
        with patch.object(context_aggregator, '_gather_all_context_sources', side_effect=Exception("Unexpected error")):
            # Act & Assert
            with pytest.raises(ContextGatherError, match="Context aggregation failed"):
                await context_aggregator.aggregate_context(sample_parsed_intent)
    
    async def test_context_aggregation_config_validation(self):
        """Test context aggregation configuration validation"""
        # Test invalid config
        with pytest.raises(ValueError, match="Invalid configuration"):
            ContextAggregatorConfig(max_context_sources=-1)
        
        with pytest.raises(ValueError, match="Invalid configuration"):
            ContextAggregatorConfig(context_timeout=0)
        
        with pytest.raises(ValueError, match="Invalid configuration"):
            ContextAggregatorConfig(quality_threshold=2.0)
    
    async def test_context_aggregation_statistics(self, context_aggregator, sample_parsed_intent):
        """Test context aggregation statistics tracking"""
        # Arrange
        with patch.object(context_aggregator, '_gather_all_context_sources', return_value={}):
            # Act
            await context_aggregator.aggregate_context(sample_parsed_intent)
            
            # Assert
            stats = context_aggregator.get_statistics()
            assert stats["total_aggregations"] == 1
            assert stats["successful_aggregations"] == 1
            assert stats["failed_aggregations"] == 0
            assert stats["average_aggregation_time"] > 0.0
    
    async def test_context_aggregation_cache_management(self, context_aggregator, sample_parsed_intent):
        """Test context aggregation cache management"""
        # Fill cache beyond limit
        config = ContextAggregatorConfig(cache_size=2)
        aggregator = ContextAggregator(config=config)
        
        with patch.object(aggregator, '_gather_all_context_sources', return_value={}):
            # Add 3 different intents to cache
            intent1 = ParsedIntent(action="generate", target="endpoint", language="python", framework="fastapi", purpose="test1", keywords=[], complexity="low", requirements=[], confidence_score=0.9)
            intent2 = ParsedIntent(action="generate", target="model", language="python", framework="fastapi", purpose="test2", keywords=[], complexity="low", requirements=[], confidence_score=0.9)
            intent3 = ParsedIntent(action="refactor", target="function", language="python", framework="fastapi", purpose="test3", keywords=[], complexity="low", requirements=[], confidence_score=0.9)
            
            await aggregator.aggregate_context(intent1)
            await aggregator.aggregate_context(intent2)
            await aggregator.aggregate_context(intent3)
            
            # Cache should only contain 2 entries
            assert len(aggregator._cache) == 2


@pytest.mark.asyncio
class TestContextAggregatorConfig:
    """Test ContextAggregatorConfig class"""
    
    def test_default_config_values(self):
        """Test default configuration values"""
        config = ContextAggregatorConfig()
        
        assert config.max_context_sources == 10
        assert config.context_timeout == 30
        assert config.enable_caching is True
        assert config.cache_size == 50
        assert config.quality_threshold == 0.7
        assert config.max_context_length == 5000
    
    def test_custom_config_values(self):
        """Test custom configuration values"""
        config = ContextAggregatorConfig(
            max_context_sources=20,
            context_timeout=60,
            enable_caching=False,
            cache_size=100,
            quality_threshold=0.8,
            max_context_length=10000
        )
        
        assert config.max_context_sources == 20
        assert config.context_timeout == 60
        assert config.enable_caching is False
        assert config.cache_size == 100
        assert config.quality_threshold == 0.8
        assert config.max_context_length == 10000
    
    def test_config_validation(self):
        """Test configuration validation"""
        # Valid configs should not raise
        ContextAggregatorConfig(max_context_sources=1)
        ContextAggregatorConfig(context_timeout=1)
        ContextAggregatorConfig(quality_threshold=0.0)
        ContextAggregatorConfig(quality_threshold=1.0)
        ContextAggregatorConfig(max_context_length=1)
        
        # Invalid configs should raise
        with pytest.raises(ValueError):
            ContextAggregatorConfig(max_context_sources=0)
        
        with pytest.raises(ValueError):
            ContextAggregatorConfig(context_timeout=0)
        
        with pytest.raises(ValueError):
            ContextAggregatorConfig(quality_threshold=-0.1)
        
        with pytest.raises(ValueError):
            ContextAggregatorConfig(quality_threshold=1.1)
        
        with pytest.raises(ValueError):
            ContextAggregatorConfig(max_context_length=0)
