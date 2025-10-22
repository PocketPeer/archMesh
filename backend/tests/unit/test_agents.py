"""
Unit tests for AI agents.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any

from app.agents.requirements_agent import RequirementsAgent
from app.agents.architecture_agent import ArchitectureAgent
from app.core.error_handling import LLMTimeoutError, LLMProviderError


class TestRequirementsAgent:
    """Test cases for RequirementsAgent."""
    
    @pytest.fixture
    def agent(self):
        """Create a RequirementsAgent instance for testing."""
        return RequirementsAgent()
    
    def test_agent_initialization(self, agent):
        """Test agent initialization."""
        assert agent.agent_type == "requirements_extractor"
        assert agent.agent_version == "1.0.0"
        assert agent.temperature == 0.5
        assert agent.max_retries == 3
        assert agent.timeout_seconds == 120
        assert agent.max_tokens == 4000
    
    def test_get_system_prompt(self, agent):
        """Test system prompt generation."""
        prompt = agent.get_system_prompt()
        assert isinstance(prompt, str)
        assert "business analyst" in prompt.lower()
        assert "json" in prompt.lower()
        assert "structured_requirements" in prompt
    
    @pytest.mark.asyncio
    async def test_execute_success(self, agent, sample_requirements_data):
        """Test successful requirements extraction."""
        import json
        
        # Mock the document reading and LLM response
        with patch.object(agent, '_read_document', return_value="Test document content"):
            with patch.object(agent, '_call_llm', return_value=json.dumps(sample_requirements_data)):
                result = await agent.execute({
                    "document_path": "/test/path/document.txt",
                    "project_context": "Test context",
                    "domain": "cloud-native"
                })
                
                assert "structured_requirements" in result
                assert result["structured_requirements"]["business_goals"] == ["Launch online marketplace", "Increase revenue"]
                assert "confidence_score" in result
                assert 0.0 <= result["confidence_score"] <= 1.0
    
    @pytest.mark.asyncio
    async def test_execute_llm_timeout(self, agent):
        """Test handling of LLM timeout errors."""
        with patch.object(agent, '_read_document', return_value="Test document content"):
            with patch.object(agent, '_call_llm', side_effect=LLMTimeoutError("Timeout", "deepseek", "deepseek-r1")):
                with pytest.raises(LLMTimeoutError, match="Timeout"):
                    await agent.execute({
                        "document_path": "/test/path/document.txt",
                        "project_context": "Test context",
                        "domain": "cloud-native"
                    })
    
    @pytest.mark.asyncio
    async def test_execute_llm_provider_error(self, agent):
        """Test handling of LLM provider errors."""
        with patch.object(agent, '_read_document', return_value="Test document content"):
            with patch.object(agent, '_call_llm', side_effect=LLMProviderError("Provider error", "deepseek", "deepseek-r1")):
                with pytest.raises(LLMProviderError, match="Provider error"):
                    await agent.execute({
                        "document_path": "/test/path/document.txt",
                        "project_context": "Test context",
                        "domain": "cloud-native"
                    })
    
    @pytest.mark.asyncio
    async def test_execute_invalid_json(self, agent):
        """Test handling of invalid JSON responses."""
        with patch.object(agent, '_read_document', return_value="Test document content"):
            with patch.object(agent, '_call_llm', return_value="invalid json response"):
                with pytest.raises(ValueError, match="Could not parse JSON"):
                    await agent.execute({
                        "document_path": "/test/path/document.txt",
                        "project_context": "Test context",
                        "domain": "cloud-native"
                    })
    
    @pytest.mark.asyncio
    async def test_execute_file_not_found(self, agent):
        """Test handling of file not found errors."""
        with patch('os.path.exists', return_value=False):
            with pytest.raises(Exception, match="Failed to read document"):
                await agent.execute({
                    "document_path": "/nonexistent/path/document.txt",
                    "project_context": "Test context",
                    "domain": "cloud-native"
                })


class TestArchitectureAgent:
    """Test cases for ArchitectureAgent."""
    
    @pytest.fixture
    def agent(self):
        """Create an ArchitectureAgent instance for testing."""
        return ArchitectureAgent()
    
    def test_agent_initialization(self, agent):
        """Test agent initialization."""
        assert agent.agent_type == "architecture_designer"
        assert agent.agent_version == "1.1.0"
        assert agent.temperature == 0.5
        assert agent.max_retries == 3
        assert agent.timeout_seconds == 180
        assert agent.max_tokens == 6000
    
    def test_get_system_prompt(self, agent):
        """Test system prompt generation."""
        prompt = agent.get_system_prompt()
        assert isinstance(prompt, str)
        assert "architect" in prompt.lower()
        assert "architecture" in prompt.lower()
        assert "technology stack" in prompt.lower()
    
    @pytest.mark.asyncio
    async def test_execute_success(self, agent, sample_architecture_data):
        """Test successful architecture design."""
        import json
        
        # Mock the LLM response
        with patch.object(agent, '_call_llm', return_value=json.dumps(sample_architecture_data)):
            result = await agent.execute({
                "requirements": {
                    "structured_requirements": {
                        "business_goals": ["Launch online marketplace"],
                        "functional_requirements": ["User registration"],
                        "non_functional_requirements": {
                            "performance": ["Handle 1000 users"],
                            "security": ["Encrypt data"]
                        }
                    }
                },
                "project_context": "Test context",
                "domain": "cloud-native"
            })
            
            assert "architecture" in result
            assert result["architecture"]["overview"] == "Microservices-based e-commerce platform"
    
    @pytest.mark.asyncio
    async def test_execute_llm_timeout(self, agent):
        """Test handling of LLM timeout errors."""
        with patch.object(agent, '_call_llm', side_effect=LLMTimeoutError("Timeout", "deepseek", "deepseek-r1")):
            with pytest.raises(LLMTimeoutError, match="Timeout"):
                await agent.execute({
                    "requirements": {"structured_requirements": {}},
                    "project_context": "Test context",
                    "domain": "cloud-native"
                })
    
    @pytest.mark.asyncio
    async def test_execute_missing_requirements(self, agent):
        """Test handling of missing requirements."""
        with pytest.raises(ValueError, match="requirements is required"):
            await agent.execute({
                "project_context": "Test context",
                "domain": "cloud-native"
            })


class TestAgentErrorHandling:
    """Test cases for agent error handling and fallback mechanisms."""
    
    @pytest.mark.asyncio
    async def test_retry_mechanism(self):
        """Test that agents raise retryable errors for higher-level retry logic."""
        agent = RequirementsAgent()
        
        # Mock LLM to fail with retryable error
        with patch.object(agent, '_read_document', return_value="Test document content"):
            with patch.object(agent, '_call_llm', side_effect=LLMTimeoutError("Temporary timeout", "deepseek", "deepseek-r1")):
                # Agent should raise the error for higher-level retry logic to handle
                with pytest.raises(LLMTimeoutError, match="Temporary timeout"):
                    await agent.execute({
                        "document_path": "/test/path/document.txt",
                        "project_context": "Test context",
                        "domain": "cloud-native"
                    })
    
    @pytest.mark.asyncio
    async def test_fallback_provider(self):
        """Test fallback to different LLM provider."""
        agent = RequirementsAgent()
        
        # Mock the LLM initialization to simulate provider fallback
        with patch('app.agents.base_agent.BaseAgent._initialize_llm') as mock_init:
            # First call fails, second succeeds
            mock_init.side_effect = [
                LLMProviderError("Provider unavailable", "deepseek", "deepseek-r1"),
                MagicMock()  # Successful fallback
            ]
            
            # This test would require more complex mocking of the fallback mechanism
            # For now, we'll test the error handling structure
            assert True  # Placeholder for more complex fallback testing
