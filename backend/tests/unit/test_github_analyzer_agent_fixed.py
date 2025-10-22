"""
Unit tests for the GitHub Analyzer Agent - Fixed version.

This module tests the GitHubAnalyzerAgent functionality including:
- Repository cloning and analysis
- File structure analysis
- Technology stack detection
- Configuration parsing
- LLM-based architecture analysis
"""

import pytest
import tempfile
import shutil
import os
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from pathlib import Path

# Import the agent class directly to avoid LangChain import issues
import sys
sys.path.insert(0, '/Users/schwipee/dev/archMesh/archmesh-poc/backend')

# Mock the problematic imports before importing the agent
with patch.dict('sys.modules', {
    'langchain_anthropic': Mock(),
    'langchain_openai': Mock(),
    'langchain_core': Mock(),
}):
    from app.agents.github_analyzer_agent import GitHubAnalyzerAgent
    from app.core.error_handling import LLMTimeoutError, LLMProviderError


class TestGitHubAnalyzerAgent:
    """Test cases for GitHubAnalyzerAgent."""

    @pytest.fixture
    def agent(self):
        """Create a GitHubAnalyzerAgent instance for testing."""
        return GitHubAnalyzerAgent()

    @pytest.fixture
    def temp_repo_dir(self):
        """Create a temporary directory for repository testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def sample_repo_structure(self, temp_repo_dir):
        """Create a sample repository structure for testing."""
        # Create sample files
        (Path(temp_repo_dir) / "src" / "main.py").parent.mkdir(parents=True, exist_ok=True)
        (Path(temp_repo_dir) / "src" / "main.py").write_text("print('Hello World')")
        
        (Path(temp_repo_dir) / "requirements.txt").write_text("fastapi==0.68.0\npydantic==1.8.2")
        (Path(temp_repo_dir) / "README.md").write_text("# Test Repository")
        (Path(temp_repo_dir) / "package.json").write_text('{"name": "test", "version": "1.0.0"}')
        (Path(temp_repo_dir) / "Dockerfile").write_text("FROM python:3.9")
        (Path(temp_repo_dir) / "docker-compose.yml").write_text("version: '3.8'")
        (Path(temp_repo_dir) / "config.json").write_text('{"database": "postgresql"}')
        
        return temp_repo_dir

    def test_get_system_prompt(self, agent):
        """Test system prompt generation."""
        prompt = agent.get_system_prompt()
        
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert "GitHub repository" in prompt
        assert "architecture analysis" in prompt

    @pytest.mark.asyncio
    async def test_execute_success(self, agent, sample_repo_structure):
        """Test successful repository analysis."""
        with patch.object(agent, '_clone_repository', return_value=sample_repo_structure):
            with patch.object(agent, '_analyze_file_structure', return_value={"total_files": 10}):
                with patch.object(agent, '_extract_tech_stack', return_value={"languages": ["Python"]}):
                    with patch.object(agent, '_parse_configurations', return_value={"docker": True}):
                        with patch.object(agent, '_analyze_architecture_with_llm', return_value={"style": "microservices"}):
                            with patch.object(agent, '_cleanup_repository'):
                                result = await agent.execute({
                                    "repo_url": "https://github.com/test/repo.git",
                                    "project_context": "Test project",
                                    "domain": "cloud-native"
                                })
                                
                                assert "repository_info" in result
                                assert "tech_stack" in result
                                assert "architecture" in result
                                assert "services" in result
                                assert "dependencies" in result
                                assert "api_contracts" in result
                                assert "configurations" in result
                                assert "code_quality" in result
                                assert "recommendations" in result
                                assert "metadata" in result

    @pytest.mark.asyncio
    async def test_execute_missing_repository_url(self, agent):
        """Test execution with missing repository URL."""
        with pytest.raises(ValueError, match="repo_url is required"):
            await agent.execute({
                "project_context": "Test project",
                "domain": "cloud-native"
            })

    @pytest.mark.asyncio
    async def test_execute_clone_failure(self, agent):
        """Test execution when repository cloning fails."""
        with patch.object(agent, '_clone_repository', side_effect=Exception("Clone failed")):
            with pytest.raises(Exception, match="Clone failed"):
                await agent.execute({
                    "repo_url": "https://github.com/test/repo.git",
                    "project_context": "Test project",
                    "domain": "cloud-native"
                })

    @pytest.mark.asyncio
    async def test_execute_llm_timeout(self, agent, sample_repo_structure):
        """Test execution when LLM times out."""
        with patch.object(agent, '_clone_repository', return_value=sample_repo_structure):
            with patch.object(agent, '_analyze_file_structure', return_value={}):
                with patch.object(agent, '_extract_tech_stack', return_value={}):
                    with patch.object(agent, '_parse_configurations', return_value={}):
                        with patch.object(agent, '_analyze_architecture_with_llm', side_effect=LLMTimeoutError("Timeout")):
                            with patch.object(agent, '_cleanup_repository'):
                                with pytest.raises(LLMTimeoutError, match="Timeout"):
                                    await agent.execute({
                                        "repo_url": "https://github.com/test/repo.git",
                                        "project_context": "Test project",
                                        "domain": "cloud-native"
                                    })

    @pytest.mark.asyncio
    async def test_execute_llm_provider_error(self, agent, sample_repo_structure):
        """Test execution when LLM provider fails."""
        with patch.object(agent, '_clone_repository', return_value=sample_repo_structure):
            with patch.object(agent, '_analyze_file_structure', return_value={}):
                with patch.object(agent, '_extract_tech_stack', return_value={}):
                    with patch.object(agent, '_parse_configurations', return_value={}):
                        with patch.object(agent, '_analyze_architecture_with_llm', side_effect=LLMProviderError("Provider error")):
                            with patch.object(agent, '_cleanup_repository'):
                                with pytest.raises(LLMProviderError, match="Provider error"):
                                    await agent.execute({
                                        "repo_url": "https://github.com/test/repo.git",
                                        "project_context": "Test project",
                                        "domain": "cloud-native"
                                    })

    @pytest.mark.asyncio
    async def test_analyze_file_structure(self, agent, sample_repo_structure):
        """Test file structure analysis."""
        result = await agent._analyze_file_structure(sample_repo_structure)
        
        assert "total_files" in result
        assert "file_types" in result
        assert "directories" in result
        assert result["total_files"] >= 8  # At least the files we created
        assert ".py" in result["file_types"]
        assert ".json" in result["file_types"]
        assert "src" in result["directories"]

    @pytest.mark.asyncio
    async def test_analyze_file_structure_empty_directory(self, agent, temp_repo_dir):
        """Test file structure analysis on empty directory."""
        result = await agent._analyze_file_structure(temp_repo_dir)
        
        assert result["total_files"] == 0
        assert result["directories"] == []
        assert result["file_types"] == {}

    @pytest.mark.asyncio
    async def test_extract_tech_stack_python_project(self, agent, temp_repo_dir):
        """Test technology stack extraction for Python project."""
        # Create Python project files
        with open(os.path.join(temp_repo_dir, "requirements.txt"), 'w') as f:
            f.write("fastapi==0.68.0\npydantic==1.8.2\nuvicorn==0.15.0")

        with open(os.path.join(temp_repo_dir, "setup.py"), 'w') as f:
            f.write("from setuptools import setup\nsetup(name='test')")

        result = await agent._extract_tech_stack(temp_repo_dir)

        assert "languages" in result
        assert "Python" in result["languages"]
        assert "frameworks" in result
        assert "FastAPI" in result["frameworks"]

    @pytest.mark.asyncio
    async def test_extract_tech_stack_nodejs_project(self, agent, temp_repo_dir):
        """Test technology stack extraction for Node.js project."""
        # Create Node.js project files
        with open(os.path.join(temp_repo_dir, "package.json"), 'w') as f:
            f.write('{"dependencies": {"express": "^4.17.1", "react": "^17.0.0"}}')

        result = await agent._extract_tech_stack(temp_repo_dir)

        assert "JavaScript" in result["languages"]
        assert "Express" in result["frameworks"]
        assert "React" in result["frameworks"]

    @pytest.mark.asyncio
    async def test_extract_tech_stack_java_project(self, agent, temp_repo_dir):
        """Test technology stack extraction for Java project."""
        # Create Java project files
        with open(os.path.join(temp_repo_dir, "pom.xml"), 'w') as f:
            f.write('<?xml version="1.0"?><project><dependencies><dependency><groupId>org.springframework</groupId><artifactId>spring-boot-starter</artifactId></dependency></dependencies></project>')

        result = await agent._extract_tech_stack(temp_repo_dir)

        assert "Java" in result["languages"]
        assert "Spring Boot" in result["frameworks"]

    @pytest.mark.asyncio
    async def test_extract_tech_stack_go_project(self, agent, temp_repo_dir):
        """Test technology stack extraction for Go project."""
        # Create Go project files
        with open(os.path.join(temp_repo_dir, "go.mod"), 'w') as f:
            f.write('module test\n\ngo 1.19\n\nrequire github.com/gin-gonic/gin v1.9.0')

        result = await agent._extract_tech_stack(temp_repo_dir)

        assert "Go" in result["languages"]
        assert "Gin" in result["frameworks"]

    @pytest.mark.asyncio
    async def test_extract_tech_stack_rust_project(self, agent, temp_repo_dir):
        """Test technology stack extraction for Rust project."""
        # Create Rust project files
        with open(os.path.join(temp_repo_dir, "Cargo.toml"), 'w') as f:
            f.write('[package]\nname = "test"\nversion = "0.1.0"\n\n[dependencies]\nactix-web = "4.0"')

        result = await agent._extract_tech_stack(temp_repo_dir)

        assert "Rust" in result["languages"]
        assert "Actix Web" in result["frameworks"]

    @pytest.mark.asyncio
    async def test_parse_configurations_docker_compose(self, agent, temp_repo_dir):
        """Test Docker Compose configuration parsing."""
        docker_compose_content = """
version: '3.8'
services:
  web:
    image: nginx
    ports:
      - "80:80"
  db:
    image: postgres
    environment:
      POSTGRES_DB: testdb
"""
        with open(os.path.join(temp_repo_dir, "docker-compose.yml"), 'w') as f:
            f.write(docker_compose_content)

        result = await agent._parse_configurations(temp_repo_dir)

        assert "docker_compose" in result
        assert "services" in result["docker_compose"]
        assert "web" in result["docker_compose"]["services"]
        assert "db" in result["docker_compose"]["services"]

    @pytest.mark.asyncio
    async def test_parse_configurations_kubernetes(self, agent, temp_repo_dir):
        """Test Kubernetes configuration parsing."""
        k8s_content = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: test-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: test-app
"""
        os.makedirs(os.path.join(temp_repo_dir, "k8s"), exist_ok=True)
        with open(os.path.join(temp_repo_dir, "k8s", "deployment.yaml"), 'w') as f:
            f.write(k8s_content)

        result = await agent._parse_configurations(temp_repo_dir)

        assert "kubernetes" in result
        assert "deployments" in result["kubernetes"]

    @pytest.mark.asyncio
    async def test_parse_configurations_openapi(self, agent, temp_repo_dir):
        """Test OpenAPI configuration parsing."""
        openapi_content = """
openapi: 3.0.0
info:
  title: Test API
  version: 1.0.0
paths:
  /users:
    get:
      summary: Get users
      responses:
        '200':
          description: Success
"""
        with open(os.path.join(temp_repo_dir, "openapi.yaml"), 'w') as f:
            f.write(openapi_content)

        result = await agent._parse_configurations(temp_repo_dir)

        assert "openapi" in result
        assert "paths" in result["openapi"]

    @pytest.mark.asyncio
    async def test_analyze_architecture_with_llm_success(self, agent):
        """Test successful LLM-based architecture analysis."""
        mock_llm_response = {
            "architecture_style": "microservices",
            "components": ["api-gateway", "user-service", "order-service"],
            "patterns": ["CQRS", "Event Sourcing"],
            "quality_score": 0.85
        }
        
        with patch.object(agent, '_call_llm', return_value=str(mock_llm_response)):
            with patch.object(agent, '_parse_json_response', return_value=mock_llm_response):
                result = await agent._analyze_architecture_with_llm(
                    repo_path="/test/path",
                    file_structure={"total_files": 100},
                    tech_stack={"languages": ["Python"]},
                    configurations={"docker": True}
                )
                
                assert result == mock_llm_response

    @pytest.mark.asyncio
    async def test_analyze_architecture_with_llm_invalid_json(self, agent):
        """Test LLM architecture analysis with invalid JSON response."""
        with patch.object(agent, '_call_llm', return_value="invalid json"):
            with patch.object(agent, '_parse_json_response', side_effect=ValueError("Invalid JSON")):
                with pytest.raises(ValueError, match="Invalid JSON"):
                    await agent._analyze_architecture_with_llm(
                        repo_path="/test/path",
                        file_structure={},
                        tech_stack={},
                        configurations={}
                    )

    @pytest.mark.asyncio
    async def test_cleanup_repository(self, agent, temp_repo_dir):
        """Test repository cleanup."""
        # This should not raise an exception
        await agent._cleanup_repository(temp_repo_dir)

    @pytest.mark.asyncio
    async def test_cleanup_repository_nonexistent(self, agent):
        """Test cleanup of non-existent repository."""
        # This should handle gracefully
        await agent._cleanup_repository("/nonexistent/path")

    def test_get_agent_capabilities(self, agent):
        """Test agent capabilities."""
        capabilities = agent.get_agent_capabilities()
        
        assert "capabilities" in capabilities
        assert "GitHub repository analysis" in capabilities["capabilities"]
        assert "Technology stack detection" in capabilities["capabilities"]
        assert "Architecture analysis" in capabilities["capabilities"]
        assert "Configuration parsing" in capabilities["capabilities"]

    @pytest.mark.asyncio
    async def test_execute_with_cleanup_on_error(self, agent):
        """Test that cleanup is called even when execution fails."""
        with patch.object(agent, '_clone_repository', return_value="/test/path"):
            with patch.object(agent, '_analyze_file_structure', side_effect=Exception("Analysis failed")):
                with patch.object(agent, '_cleanup_repository') as mock_cleanup:
                    with pytest.raises(Exception, match="Analysis failed"):
                        await agent.execute({
                            "repo_url": "https://github.com/test/repo.git",
                            "project_context": "Test project",
                            "domain": "cloud-native"
                        })
                    
                    mock_cleanup.assert_called_once_with("/test/path")

    @pytest.mark.asyncio
    async def test_analyze_file_structure_with_hidden_files(self, agent, temp_repo_dir):
        """Test file structure analysis with hidden files."""
        # Create hidden files
        (Path(temp_repo_dir) / ".gitignore").write_text("*.pyc")
        (Path(temp_repo_dir) / ".env").write_text("SECRET_KEY=test")
        (Path(temp_repo_dir) / "src" / ".hidden").write_text("hidden content")

        result = await agent._analyze_file_structure(temp_repo_dir)

        assert result["total_files"] >= 3
        assert ".gitignore" in result["file_types"]
        assert ".env" in result["file_types"]

    @pytest.mark.asyncio
    async def test_extract_tech_stack_multiple_languages(self, agent, temp_repo_dir):
        """Test technology stack extraction for multi-language project."""
        # Create files for multiple languages
        with open(os.path.join(temp_repo_dir, "requirements.txt"), 'w') as f:
            f.write("fastapi==0.68.0")
        
        with open(os.path.join(temp_repo_dir, "package.json"), 'w') as f:
            f.write('{"dependencies": {"express": "^4.17.1"}}')
        
        with open(os.path.join(temp_repo_dir, "pom.xml"), 'w') as f:
            f.write('<?xml version="1.0"?><project><dependencies><dependency><groupId>org.springframework</groupId><artifactId>spring-boot-starter</artifactId></dependency></dependencies></project>')

        result = await agent._extract_tech_stack(temp_repo_dir)

        assert "Python" in result["languages"]
        assert "JavaScript" in result["languages"]
        assert "Java" in result["languages"]
        assert "FastAPI" in result["frameworks"]
        assert "Express" in result["frameworks"]
        assert "Spring Boot" in result["frameworks"]

