"""
Template for testing AI agents in ArchMesh.

This template provides a standardized structure for testing agents,
ensuring consistent test coverage and quality across all agent implementations.
"""

import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock
from typing import Dict, Any, List
from app.agents.base_agent import BaseAgent


@pytest.mark.skip(reason="Template test - should be customized for each agent")
class TestAgentTemplate:
    """
    Template test class for AI agents.
    
    This template should be copied and customized for each specific agent.
    Replace 'AgentName' with the actual agent class name.
    """
    
    @pytest.fixture
    def agent(self):
        """Create agent instance for testing."""
        # This is a template - should be customized for each agent
        # For now, return None to indicate this is a template
        return None
    
    @pytest.fixture
    def sample_input_data(self):
        """Sample input data for testing."""
        return {
            "document_path": "/test/path/document.txt",
            "domain": "cloud-native",
            "project_context": "Test project context",
            "session_id": "test-session-123"
        }
    
    @pytest.fixture
    def sample_llm_response(self):
        """Sample LLM response for testing."""
        return {
            "structured_data": {
                "key1": "value1",
                "key2": "value2",
            },
            "confidence_score": 0.8,
            "metadata": {
                "agent_version": "1.0.0",
                "execution_time": 1.5
            }
        }
    
    # Test Agent Initialization
    def test_agent_initialization(self, agent):
        """Test agent initializes correctly."""
        assert agent is not None
        assert hasattr(agent, 'agent_type')
        assert hasattr(agent, 'agent_version')
        assert hasattr(agent, 'llm_provider')
        assert hasattr(agent, 'llm_model')
    
    def test_agent_default_configuration(self, agent):
        """Test agent has correct default configuration."""
        assert agent.llm_provider == "deepseek"
        assert agent.llm_model == "deepseek-r1"
        assert agent.temperature == 0.7
        assert agent.max_retries == 3
    
    # Test System Prompt
    def test_get_system_prompt(self, agent):
        """Test system prompt is properly formatted."""
        prompt = agent.get_system_prompt()
        
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert "You are" in prompt or "Your task" in prompt
    
    # Test Input Validation
    async def test_execute_with_valid_input(self, agent, sample_input_data, sample_llm_response):
        """Test agent executes successfully with valid input."""
        with patch.object(agent, '_call_llm', return_value=json.dumps(sample_llm_response)):
            result = await agent.execute(sample_input_data)
            
            assert isinstance(result, dict)
            assert "metadata" in result
            assert result["metadata"]["agent_version"] == agent.agent_version
    
    async def test_execute_with_invalid_input(self, agent):
        """Test agent handles invalid input gracefully."""
        invalid_inputs = [
            {},  # Empty input
            {"invalid_key": "value"},  # Missing required keys
            None,  # None input
        ]
        
        for invalid_input in invalid_inputs:
            with pytest.raises((ValueError, TypeError, KeyError)):
                await agent.execute(invalid_input)
    
    async def test_execute_with_missing_document(self, agent):
        """Test agent handles missing document gracefully."""
        input_data = {
            "document_path": "/nonexistent/path/document.txt",
            "domain": "cloud-native"
        }
        
        with pytest.raises(FileNotFoundError):
            await agent.execute(input_data)
    
    # Test LLM Integration
    async def test_llm_call_success(self, agent, sample_input_data, sample_llm_response):
        """Test successful LLM call."""
        with patch.object(agent, '_call_llm', return_value=json.dumps(sample_llm_response)) as mock_call:
            result = await agent.execute(sample_input_data)
            
            mock_call.assert_called_once()
            assert result is not None
    
    async def test_llm_call_timeout(self, agent, sample_input_data):
        """Test LLM timeout handling."""
        from app.core.error_handling import LLMTimeoutError
        
        with patch.object(agent, '_call_llm', side_effect=LLMTimeoutError("Timeout")):
            with pytest.raises(LLMTimeoutError):
                await agent.execute(sample_input_data)
    
    async def test_llm_call_provider_error(self, agent, sample_input_data):
        """Test LLM provider error handling."""
        from app.core.error_handling import LLMProviderError
        
        with patch.object(agent, '_call_llm', side_effect=LLMProviderError("Provider error")):
            with pytest.raises(LLMProviderError):
                await agent.execute(sample_input_data)
    
    # Test JSON Parsing
    async def test_json_parsing_success(self, agent, sample_input_data, sample_llm_response):
        """Test successful JSON parsing."""
        with patch.object(agent, '_call_llm', return_value=json.dumps(sample_llm_response)):
            result = await agent.execute(sample_input_data)
            
            assert isinstance(result, dict)
            assert "structured_data" in result or "structured_requirements" in result
    
    async def test_json_parsing_invalid_json(self, agent, sample_input_data):
        """Test invalid JSON response handling."""
        with patch.object(agent, '_call_llm', return_value="invalid json"):
            with pytest.raises(ValueError, match="Could not parse JSON"):
                await agent.execute(sample_input_data)
    
    async def test_json_parsing_markdown_wrapped(self, agent, sample_input_data, sample_llm_response):
        """Test JSON parsing with markdown code blocks."""
        markdown_response = f"```json\n{json.dumps(sample_llm_response)}\n```"
        
        with patch.object(agent, '_call_llm', return_value=markdown_response):
            result = await agent.execute(sample_input_data)
            
            assert isinstance(result, dict)
            assert "structured_data" in result or "structured_requirements" in result
    
    # Test Error Handling
    async def test_error_handling_generic_error(self, agent, sample_input_data):
        """Test generic error handling."""
        with patch.object(agent, '_call_llm', side_effect=Exception("Generic error")):
            with pytest.raises(Exception):
                await agent.execute(sample_input_data)
    
    async def test_error_handling_retry_mechanism(self, agent, sample_input_data, sample_llm_response):
        """Test retry mechanism on transient failures."""
        call_count = 0
        
        def mock_call_with_retry(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Transient error")
            return json.dumps(sample_llm_response)
        
        with patch.object(agent, '_call_llm', side_effect=mock_call_with_retry):
            result = await agent.execute(sample_input_data)
            
            assert call_count == 3  # Should retry 3 times
            assert result is not None
    
    # Test Data Validation
    async def test_data_validation_success(self, agent, sample_input_data, sample_llm_response):
        """Test successful data validation."""
        with patch.object(agent, '_call_llm', return_value=json.dumps(sample_llm_response)):
            result = await agent.execute(sample_input_data)
            
            # Validate result structure
            assert isinstance(result, dict)
            assert "metadata" in result
            assert "confidence_score" in result or "confidence_score" in result.get("metadata", {})
    
    async def test_data_validation_missing_fields(self, agent, sample_input_data):
        """Test data validation with missing required fields."""
        incomplete_response = {
            "structured_data": {
                "key1": "value1"
                # Missing required fields
            }
        }
        
        with patch.object(agent, '_call_llm', return_value=json.dumps(incomplete_response)):
            # Should either handle gracefully or raise appropriate error
            try:
                result = await agent.execute(sample_input_data)
                # If successful, validate that missing fields are handled
                assert isinstance(result, dict)
            except (ValueError, KeyError):
                # Expected behavior for missing required fields
                pass
    
    # Test Performance
    async def test_execution_performance(self, agent, sample_input_data, sample_llm_response):
        """Test agent execution performance."""
        import time
        
        with patch.object(agent, '_call_llm', return_value=json.dumps(sample_llm_response)):
            start_time = time.time()
            result = await agent.execute(sample_input_data)
            end_time = time.time()
            
            execution_time = end_time - start_time
            
            # Should complete within reasonable time (adjust threshold as needed)
            assert execution_time < 10.0, f"Execution took {execution_time}s, expected < 10.0s"
            assert result is not None
    
    # Test Logging
    async def test_execution_logging(self, agent, sample_input_data, sample_llm_response):
        """Test that execution is properly logged."""
        with patch.object(agent, '_call_llm', return_value=json.dumps(sample_llm_response)):
            with patch('app.agents.base_agent.logger') as mock_logger:
                result = await agent.execute(sample_input_data)
                
                # Verify logging calls
                assert mock_logger.info.called
                assert mock_logger.debug.called
    
    # Test Metadata
    async def test_result_metadata(self, agent, sample_input_data, sample_llm_response):
        """Test that result contains proper metadata."""
        with patch.object(agent, '_call_llm', return_value=json.dumps(sample_llm_response)):
            result = await agent.execute(sample_input_data)
            
            metadata = result.get("metadata", {})
            
            assert "agent_version" in metadata
            assert "execution_timestamp" in metadata or "timestamp" in metadata
            assert metadata["agent_version"] == agent.agent_version
    
    # Test Edge Cases
    async def test_empty_document_content(self, agent):
        """Test handling of empty document content."""
        input_data = {
            "document_path": "/test/path/empty.txt",
            "domain": "cloud-native"
        }
        
        # Create empty file for testing
        with patch('builtins.open', MagicMock(return_value=MagicMock(read=MagicMock(return_value="")))):
            with pytest.raises(ValueError, match="empty or contains no readable content"):
                await agent.execute(input_data)
    
    async def test_very_large_document(self, agent):
        """Test handling of very large documents."""
        large_content = "x" * 1000000  # 1MB of content
        
        input_data = {
            "document_path": "/test/path/large.txt",
            "domain": "cloud-native"
        }
        
        with patch('builtins.open', MagicMock(return_value=MagicMock(read=MagicMock(return_value=large_content)))):
            with patch.object(agent, '_call_llm', return_value='{"result": "success"}'):
                result = await agent.execute(input_data)
                
                # Should handle large documents gracefully
                assert result is not None
    
    # Test Configuration
    def test_agent_configuration_validation(self, agent):
        """Test agent configuration validation."""
        assert agent.temperature >= 0.0 and agent.temperature <= 2.0
        assert agent.max_retries >= 1 and agent.max_retries <= 10
        assert agent.timeout_seconds >= 30 and agent.timeout_seconds <= 600
        assert agent.llm_provider in ["deepseek", "openai", "anthropic"]
    
    # Test Agent Capabilities
    def test_get_agent_capabilities(self, agent):
        """Test agent capabilities are properly defined."""
        capabilities = agent.get_agent_capabilities()
        
        assert isinstance(capabilities, dict)
        assert "supported_domains" in capabilities
        assert "supported_formats" in capabilities
        assert "max_document_size" in capabilities
        assert isinstance(capabilities["supported_domains"], list)
        assert isinstance(capabilities["supported_formats"], list)


# Usage Instructions:
"""
To use this template for a specific agent:

1. Copy this file to tests/unit/test_[agent_name].py
2. Replace 'AgentName' with the actual agent class name
3. Update the agent fixture to return the actual agent instance
4. Customize the sample_input_data and sample_llm_response fixtures
5. Add agent-specific test cases
6. Remove or modify tests that don't apply to the specific agent
7. Add additional tests for agent-specific functionality

Example for RequirementsAgent:
- Replace 'AgentName' with 'RequirementsAgent'
- Update sample_input_data to include document_path and domain
- Update sample_llm_response to match requirements extraction format
- Add tests for requirements-specific functionality like clarification questions
"""
