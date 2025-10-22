"""
Unit tests for the GitHub Analyzer Agent.

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
        # Create directory structure
        os.makedirs(os.path.join(temp_repo_dir, "src", "components"), exist_ok=True)
        os.makedirs(os.path.join(temp_repo_dir, "tests"), exist_ok=True)
        os.makedirs(os.path.join(temp_repo_dir, "docs"), exist_ok=True)
        
        # Create sample files
        files_to_create = [
            "package.json",
            "requirements.txt",
            "docker-compose.yml",
            "README.md",
            "src/main.py",
            "src/components/user.py",
            "tests/test_main.py",
            "docs/api.md"
        ]
        
        for file_path in files_to_create:
            full_path = os.path.join(temp_repo_dir, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w') as f:
                f.write(f"# Sample content for {file_path}")
        
        return temp_repo_dir

    def test_agent_initialization(self, agent):
        """Test GitHubAnalyzerAgent initialization."""
        assert agent.agent_type == "github_analyzer"
        assert agent.agent_version == "1.0.0"
        assert agent.llm_provider == "deepseek"
        assert agent.llm_model == "deepseek-r1"

    def test_get_system_prompt(self, agent):
        """Test system prompt generation."""
        prompt = agent.get_system_prompt()
        assert isinstance(prompt, str)
        assert "GitHub repository" in prompt
        assert "architecture analysis" in prompt
        assert len(prompt) > 100

    @pytest.mark.asyncio
    async def test_execute_success(self, agent, sample_repo_structure):
        """Test successful repository analysis."""
        # Mock the repository cloning and analysis methods
        with patch.object(agent, '_clone_repository', return_value=sample_repo_structure) as mock_clone:
            with patch.object(agent, '_analyze_file_structure', return_value={
                'total_files': 8,
                'file_types': {'.py': 3, '.json': 1, '.yml': 1, '.md': 3},
                'directories': ['src', 'tests', 'docs']
            }) as mock_analyze:
                with patch.object(agent, '_extract_tech_stack', return_value={
                    'languages': ['Python', 'JavaScript'],
                    'frameworks': ['FastAPI', 'React'],
                    'databases': ['PostgreSQL'],
                    'tools': ['Docker', 'pytest']
                }) as mock_tech:
                    with patch.object(agent, '_parse_configurations', return_value={
                        'docker_compose': {'services': ['web', 'db']},
                        'package_json': {'dependencies': ['react', 'express']}
                    }) as mock_config:
                        with patch.object(agent, '_analyze_architecture_with_llm', return_value={
                            'architecture_style': 'microservices',
                            'components': [
                                {'name': 'web-service', 'type': 'api'},
                                {'name': 'database', 'type': 'storage'}
                            ],
                            'dependencies': [
                                {'from': 'web-service', 'to': 'database', 'type': 'data'}
                            ]
                        }) as mock_llm:
                            with patch.object(agent, '_cleanup_repository') as mock_cleanup:
                                
                                result = await agent.execute({
                                    "repository_url": "https://github.com/test/repo.git",
                                    "project_context": "Test project",
                                    "domain": "cloud-native"
                                })
                                
                                # Verify method calls
                                mock_clone.assert_called_once()
                                mock_analyze.assert_called_once()
                                mock_tech.assert_called_once()
                                mock_config.assert_called_once()
                                mock_llm.assert_called_once()
                                mock_cleanup.assert_called_once()
                                
                                # Verify result structure
                                assert "repository_analysis" in result
                                assert "file_structure" in result
                                assert "technology_stack" in result
                                assert "configurations" in result
                                assert "architecture_analysis" in result
                                assert result["repository_analysis"]["url"] == "https://github.com/test/repo.git"

    @pytest.mark.asyncio
    async def test_execute_missing_repository_url(self, agent):
        """Test execution with missing repository URL."""
        with pytest.raises(ValueError, match="repository_url is required"):
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
                    "repository_url": "https://github.com/invalid/repo.git",
                    "project_context": "Test project",
                    "domain": "cloud-native"
                })

    @pytest.mark.asyncio
    async def test_execute_llm_timeout(self, agent, sample_repo_structure):
        """Test execution when LLM call times out."""
        with patch.object(agent, '_clone_repository', return_value=sample_repo_structure):
            with patch.object(agent, '_analyze_file_structure', return_value={}):
                with patch.object(agent, '_extract_tech_stack', return_value={}):
                    with patch.object(agent, '_parse_configurations', return_value={}):
                        with patch.object(agent, '_analyze_architecture_with_llm', side_effect=LLMTimeoutError("Timeout")):
                            with patch.object(agent, '_cleanup_repository'):
                                with pytest.raises(LLMTimeoutError, match="Timeout"):
                                    await agent.execute({
                                        "repository_url": "https://github.com/test/repo.git",
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

    def test_analyze_file_structure_empty_directory(self, agent, temp_repo_dir):
        """Test file structure analysis on empty directory."""
        result = agent._analyze_file_structure(temp_repo_dir)
        
        assert result["total_files"] == 0
        assert result["file_types"] == {}
        assert result["directories"] == []

    def test_extract_tech_stack_python_project(self, agent, temp_repo_dir):
        """Test technology stack extraction for Python project."""
        # Create Python project files
        with open(os.path.join(temp_repo_dir, "requirements.txt"), 'w') as f:
            f.write("fastapi==0.68.0\npydantic==1.8.2\nuvicorn==0.15.0")
        
        with open(os.path.join(temp_repo_dir, "setup.py"), 'w') as f:
            f.write("from setuptools import setup\nsetup(name='test')")
        
        result = agent._extract_tech_stack(temp_repo_dir)
        
        assert "languages" in result
        assert "frameworks" in result
        assert "databases" in result
        assert "tools" in result
        assert "Python" in result["languages"]
        assert "FastAPI" in result["frameworks"]

    def test_extract_tech_stack_nodejs_project(self, agent, temp_repo_dir):
        """Test technology stack extraction for Node.js project."""
        # Create Node.js project files
        with open(os.path.join(temp_repo_dir, "package.json"), 'w') as f:
            f.write('{"dependencies": {"express": "^4.17.1", "react": "^17.0.0"}}')
        
        result = agent._extract_tech_stack(temp_repo_dir)
        
        assert "JavaScript" in result["languages"]
        assert "Express" in result["frameworks"]
        assert "React" in result["frameworks"]

    def test_extract_tech_stack_java_project(self, agent, temp_repo_dir):
        """Test technology stack extraction for Java project."""
        # Create Java project files
        with open(os.path.join(temp_repo_dir, "pom.xml"), 'w') as f:
            f.write('<?xml version="1.0"?><project><dependencies><dependency><groupId>org.springframework</groupId><artifactId>spring-boot-starter</artifactId></dependency></dependencies></project>')
        
        result = agent._extract_tech_stack(temp_repo_dir)
        
        assert "Java" in result["languages"]
        assert "Spring Boot" in result["frameworks"]

    def test_extract_tech_stack_go_project(self, agent, temp_repo_dir):
        """Test technology stack extraction for Go project."""
        # Create Go project files
        with open(os.path.join(temp_repo_dir, "go.mod"), 'w') as f:
            f.write('module test\n\ngo 1.19\n\nrequire github.com/gin-gonic/gin v1.9.0')
        
        result = agent._extract_tech_stack(temp_repo_dir)
        
        assert "Go" in result["languages"]
        assert "Gin" in result["frameworks"]

    def test_extract_tech_stack_rust_project(self, agent, temp_repo_dir):
        """Test technology stack extraction for Rust project."""
        # Create Rust project files
        with open(os.path.join(temp_repo_dir, "Cargo.toml"), 'w') as f:
            f.write('[package]\nname = "test"\nversion = "0.1.0"\n\n[dependencies]\nactix-web = "4.0"')
        
        result = agent._extract_tech_stack(temp_repo_dir)
        
        assert "Rust" in result["languages"]
        assert "Actix Web" in result["frameworks"]

    def test_parse_configurations_docker_compose(self, agent, temp_repo_dir):
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
        
        result = agent._parse_configurations(temp_repo_dir)
        
        assert "docker_compose" in result
        assert "services" in result["docker_compose"]
        assert "web" in result["docker_compose"]["services"]
        assert "db" in result["docker_compose"]["services"]

    def test_parse_configurations_kubernetes(self, agent, temp_repo_dir):
        """Test Kubernetes configuration parsing."""
        k8s_dir = os.path.join(temp_repo_dir, "k8s")
        os.makedirs(k8s_dir, exist_ok=True)
        
        deployment_content = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web
"""
        with open(os.path.join(k8s_dir, "deployment.yaml"), 'w') as f:
            f.write(deployment_content)
        
        result = agent._parse_configurations(temp_repo_dir)
        
        assert "kubernetes" in result
        assert "deployments" in result["kubernetes"]
        assert "web-deployment" in result["kubernetes"]["deployments"]

    def test_parse_configurations_openapi(self, agent, temp_repo_dir):
        """Test OpenAPI/Swagger configuration parsing."""
        openapi_content = """
{
  "openapi": "3.0.0",
  "info": {
    "title": "Test API",
    "version": "1.0.0"
  },
  "paths": {
    "/users": {
      "get": {
        "summary": "Get users"
      }
    }
  }
}
"""
        with open(os.path.join(temp_repo_dir, "openapi.json"), 'w') as f:
            f.write(openapi_content)
        
        result = agent._parse_configurations(temp_repo_dir)
        
        assert "openapi" in result
        assert "paths" in result["openapi"]
        assert "/users" in result["openapi"]["paths"]

    @pytest.mark.asyncio
    async def test_analyze_architecture_with_llm_success(self, agent, sample_repo_structure):
        """Test successful LLM-based architecture analysis."""
        mock_llm_response = {
            "architecture_style": "microservices",
            "components": [
                {"name": "api-gateway", "type": "gateway"},
                {"name": "user-service", "type": "service"},
                {"name": "database", "type": "storage"}
            ],
            "dependencies": [
                {"from": "api-gateway", "to": "user-service", "type": "http"},
                {"from": "user-service", "to": "database", "type": "data"}
            ],
            "patterns": ["API Gateway", "Database per Service"],
            "quality_metrics": {
                "cohesion": 0.8,
                "coupling": 0.3,
                "scalability": 0.9
            }
        }
        
        with patch.object(agent, '_call_llm', return_value=str(mock_llm_response)):
            result = await agent._analyze_architecture_with_llm(
                sample_repo_structure,
                {"languages": ["Python"], "frameworks": ["FastAPI"]},
                {"docker_compose": {"services": ["web", "db"]}},
                "Test project context"
            )
            
            assert result["architecture_style"] == "microservices"
            assert len(result["components"]) == 3
            assert len(result["dependencies"]) == 2
            assert "patterns" in result
            assert "quality_metrics" in result

    @pytest.mark.asyncio
    async def test_analyze_architecture_with_llm_invalid_json(self, agent, sample_repo_structure):
        """Test LLM architecture analysis with invalid JSON response."""
        with patch.object(agent, '_call_llm', return_value="Invalid JSON response"):
            with patch.object(agent, '_parse_json_response', side_effect=ValueError("Invalid JSON")):
                with pytest.raises(ValueError, match="Invalid JSON"):
                    await agent._analyze_architecture_with_llm(
                        sample_repo_structure,
                        {"languages": ["Python"]},
                        {},
                        "Test context"
                    )

    def test_cleanup_repository(self, agent, temp_repo_dir):
        """Test repository cleanup."""
        # Create some files in the temp directory
        test_file = os.path.join(temp_repo_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("test content")
        
        # Verify file exists
        assert os.path.exists(test_file)
        
        # Cleanup
        agent._cleanup_repository(temp_repo_dir)
        
        # Verify directory is removed
        assert not os.path.exists(temp_repo_dir)

    def test_cleanup_repository_nonexistent(self, agent):
        """Test cleanup of non-existent repository."""
        # Should not raise an exception
        agent._cleanup_repository("/nonexistent/path")

    def test_get_agent_capabilities(self, agent):
        """Test agent capabilities reporting."""
        capabilities = agent.get_agent_capabilities()
        
        assert "capabilities" in capabilities
        assert "GitHub repository analysis" in capabilities["capabilities"]
        assert "Technology stack detection" in capabilities["capabilities"]
        assert "Architecture pattern recognition" in capabilities["capabilities"]
        assert "Configuration parsing" in capabilities["capabilities"]
        
        assert "supported_formats" in capabilities
        assert "git" in capabilities["supported_formats"]
        assert "docker-compose" in capabilities["supported_formats"]
        assert "kubernetes" in capabilities["supported_formats"]
        
        assert "output_types" in capabilities
        assert "repository_analysis" in capabilities["output_types"]
        assert "architecture_analysis" in capabilities["output_types"]

    @pytest.mark.asyncio
    async def test_execute_with_cleanup_on_error(self, agent):
        """Test that cleanup is called even when execution fails."""
        with patch.object(agent, '_clone_repository', return_value="/tmp/test") as mock_clone:
            with patch.object(agent, '_cleanup_repository') as mock_cleanup:
                with patch.object(agent, '_analyze_file_structure', side_effect=Exception("Analysis failed")):
                    with pytest.raises(Exception, match="Analysis failed"):
                        await agent.execute({
                            "repository_url": "https://github.com/test/repo.git",
                            "project_context": "Test project",
                            "domain": "cloud-native"
                        })
                    
                    # Verify cleanup was called
                    mock_cleanup.assert_called_once_with("/tmp/test")

    def test_analyze_file_structure_with_hidden_files(self, agent, temp_repo_dir):
        """Test file structure analysis including hidden files."""
        # Create hidden files
        with open(os.path.join(temp_repo_dir, ".gitignore"), 'w') as f:
            f.write("*.pyc\n__pycache__/")
        
        with open(os.path.join(temp_repo_dir, ".env"), 'w') as f:
            f.write("SECRET_KEY=test")
        
        result = agent._analyze_file_structure(temp_repo_dir)
        
        # Should include hidden files
        assert result["total_files"] >= 2
        assert ".gitignore" in str(result["file_types"]) or ".env" in str(result["file_types"])

    def test_extract_tech_stack_multiple_languages(self, agent, temp_repo_dir):
        """Test technology stack extraction for multi-language project."""
        # Create files for multiple languages
        with open(os.path.join(temp_repo_dir, "requirements.txt"), 'w') as f:
            f.write("fastapi==0.68.0")
        
        with open(os.path.join(temp_repo_dir, "package.json"), 'w') as f:
            f.write('{"dependencies": {"react": "^17.0.0"}}')
        
        with open(os.path.join(temp_repo_dir, "Dockerfile"), 'w') as f:
            f.write("FROM python:3.9\nCOPY . .\nRUN pip install -r requirements.txt")
        
        result = agent._extract_tech_stack(temp_repo_dir)
        
        assert "Python" in result["languages"]
        assert "JavaScript" in result["languages"]
        assert "FastAPI" in result["frameworks"]
        assert "React" in result["frameworks"]
        assert "Docker" in result["tools"]
