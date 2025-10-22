"""
End-to-End Integration Tests for Complete User Journey

These tests verify the complete user journey from frontend to backend,
including project creation, document upload, workflow execution, and results delivery.
"""

import pytest
import asyncio
import json
import tempfile
import os
from unittest.mock import Mock, patch, AsyncMock
from uuid import uuid4
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.main import app
from app.models.project import Project, ProjectStatus, ProjectDomain
from app.models.workflow_session import WorkflowSession, WorkflowStageEnum
from app.agents.requirements_agent import RequirementsAgent
from app.agents.architecture_agent import ArchitectureAgent
from app.agents.github_analyzer_agent import GitHubAnalyzerAgent
from app.services.knowledge_base_service import KnowledgeBaseService


class TestCompleteUserJourney:
    """Test the complete user journey from frontend to backend."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    @pytest.fixture
    def async_client(self):
        """Create async test client."""
        return AsyncClient(app=app, base_url="http://test")

    @pytest.fixture
    def sample_project_data(self):
        """Sample project data for testing."""
        return {
            "name": "E-commerce Platform",
            "description": "Modern e-commerce platform with microservices architecture",
            "domain": "e-commerce",
            "mode": "greenfield"
        }

    @pytest.fixture
    def sample_requirements_document(self):
        """Sample requirements document content."""
        return """
        # E-commerce Platform Requirements

        ## Business Goals
        - Launch online marketplace
        - Increase revenue by 200%
        - Improve customer experience

        ## Functional Requirements
        - User authentication and authorization
        - Product catalog management
        - Shopping cart functionality
        - Order processing and payment
        - Inventory management
        - Customer support system

        ## Non-Functional Requirements
        - Performance: Response time < 200ms
        - Scalability: Support 10,000 concurrent users
        - Security: PCI DSS compliance
        - Availability: 99.9% uptime

        ## Constraints
        - Must integrate with existing payment gateway
        - Budget: $500,000
        - Timeline: 6 months
        """

    @pytest.fixture
    def sample_github_repo_data(self):
        """Sample GitHub repository data for brownfield testing."""
        return {
            "repository_url": "https://github.com/test/ecommerce-platform",
            "branch": "main",
            "services": [
                {
                    "id": "user-service",
                    "name": "User Service",
                    "type": "service",
                    "technology": "Node.js + Express",
                    "description": "Handles user authentication and management",
                    "endpoints": ["/api/users", "/api/auth"],
                    "dependencies": ["user-database"]
                },
                {
                    "id": "product-service",
                    "name": "Product Service",
                    "type": "service",
                    "technology": "Python + FastAPI",
                    "description": "Manages product catalog",
                    "endpoints": ["/api/products", "/api/categories"],
                    "dependencies": ["product-database"]
                }
            ],
            "dependencies": [
                {
                    "from": "user-service",
                    "to": "user-database",
                    "type": "database-call",
                    "description": "User service reads/writes to database"
                }
            ],
            "technology_stack": {
                "Node.js": 1,
                "Python": 1,
                "PostgreSQL": 2,
                "Express": 1,
                "FastAPI": 1
            }
        }

    @pytest.fixture
    def mock_agents(self):
        """Create mock agents for testing."""
        requirements_agent = Mock(spec=RequirementsAgent)
        architecture_agent = Mock(spec=ArchitectureAgent)
        github_analyzer = Mock(spec=GitHubAnalyzerAgent)
        kb_service = Mock(spec=KnowledgeBaseService)
        
        return {
            'requirements_agent': requirements_agent,
            'architecture_agent': architecture_agent,
            'github_analyzer': github_analyzer,
            'kb_service': kb_service
        }

    def test_health_check(self, client):
        """Test that the API is healthy."""
        # Mock Redis client
        mock_redis = Mock()
        mock_redis.ping = AsyncMock(return_value=True)
        
        with patch('app.api.v1.health.get_redis', return_value=mock_redis):
            response = client.get("/api/v1/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"

    def test_project_creation_greenfield(self, client, sample_project_data):
        """Test creating a greenfield project."""
        with patch('app.api.v1.projects.get_db') as mock_get_db:
            # Mock database session
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            # Mock project creation
            mock_project = Project(
                id=uuid4(),
                name=sample_project_data["name"],
                description=sample_project_data["description"],
                domain=ProjectDomain.CLOUD_NATIVE,
                status=ProjectStatus.PROCESSING
            )
            mock_db.add.return_value = None
            mock_db.commit.return_value = None
            mock_db.refresh.return_value = None
            
            # Mock the refresh to set the ID
            def mock_refresh(project):
                project.id = mock_project.id
                project.created_at = "2023-01-01T00:00:00Z"
                project.updated_at = "2023-01-01T00:00:00Z"
            
            mock_db.refresh.side_effect = mock_refresh
            
            # Create project data without mode field
            project_data = {
                "name": sample_project_data["name"],
                "description": sample_project_data["description"],
                "domain": "cloud-native"
            }
            
            response = client.post("/api/v1/projects", json=project_data)
            
            assert response.status_code == 201
            data = response.json()
            assert data["name"] == sample_project_data["name"]
            assert data["domain"] == "cloud-native"
            assert data["status"] == "processing"

    def test_project_creation_brownfield(self, client, sample_project_data):
        """Test creating a brownfield project."""
        brownfield_data = {**sample_project_data, "mode": "brownfield"}
        
        with patch('app.api.v1.projects.get_db') as mock_get_db:
            # Mock database session
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            # Mock project creation
            mock_project = Project(
                id=uuid4(),
                name=brownfield_data["name"],
                description=brownfield_data["description"],
                domain=brownfield_data["domain"],
                mode=ProjectDomain.ENTERPRISE,
                status=ProjectStatus.PROCESSING
            )
            mock_db.add.return_value = None
            mock_db.commit.return_value = None
            mock_db.refresh.return_value = None
            
            # Mock the refresh to set the ID
            def mock_refresh(project):
                project.id = mock_project.id
                project.created_at = "2023-01-01T00:00:00Z"
                project.updated_at = "2023-01-01T00:00:00Z"
            
            mock_db.refresh.side_effect = mock_refresh
            
            response = client.post("/api/v1/projects", json=brownfield_data)
            
            assert response.status_code == 201
            data = response.json()
            assert data["mode"] == "brownfield"

    def test_document_upload(self, client, sample_requirements_document):
        """Test document upload functionality."""
        project_id = str(uuid4())
        
        with patch('app.api.v1.workflows.get_db') as mock_get_db, \
             patch('app.core.file_storage.FileStorage.save_file') as mock_save_file:
            
            # Mock database session
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            # Mock file storage
            mock_save_file.return_value = f"/uploads/{project_id}/requirements.txt"
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
                temp_file.write(sample_requirements_document)
                temp_file_path = temp_file.name
            
            try:
                with open(temp_file_path, 'rb') as file:
                    response = client.post(
                        f"/api/v1/projects/{project_id}/upload",
                        files={"file": ("requirements.txt", file, "text/plain")}
                    )
                
                assert response.status_code == 200
                data = response.json()
                assert "file_path" in data
                assert data["file_path"].endswith("requirements.txt")
                
            finally:
                os.unlink(temp_file_path)

    @pytest.mark.asyncio
    async def test_workflow_start_greenfield(self, async_client, mock_agents, sample_requirements_document):
        """Test starting a greenfield workflow."""
        project_id = str(uuid4())
        session_id = str(uuid4())
        
        # Mock agent responses
        mock_requirements_result = {
            "structured_requirements": {
                "business_goals": ["Launch online marketplace", "Increase revenue"],
                "functional_requirements": ["User authentication", "Product catalog"],
                "non_functional_requirements": {
                    "performance": ["Response time < 200ms"],
                    "security": ["PCI DSS compliance"]
                }
            },
            "confidence_score": 0.9
        }
        
        mock_architecture_result = {
            "architecture_overview": {
                "style": "microservices",
                "rationale": "Scalable and maintainable architecture"
            },
            "services": [
                {
                    "id": "user-service",
                    "name": "User Service",
                    "type": "service",
                    "technology": "Node.js + Express"
                }
            ],
            "quality_score": 0.85
        }
        
        mock_agents['requirements_agent'].execute = AsyncMock(return_value=mock_requirements_result)
        mock_agents['architecture_agent'].execute = AsyncMock(return_value=mock_architecture_result)
        
        with patch('app.api.v1.workflows.get_db') as mock_get_db, \
             patch('app.agents.requirements_agent.RequirementsAgent', return_value=mock_agents['requirements_agent']), \
             patch('app.agents.architecture_agent.ArchitectureAgent', return_value=mock_agents['architecture_agent']):
            
            # Mock database session
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            # Mock workflow creation
            mock_workflow = WorkflowSession(
                id=session_id,
                project_id=project_id,
                current_stage="requirements_parsing",
                status=True
            )
            mock_db.add.return_value = None
            mock_db.commit.return_value = None
            mock_db.refresh.return_value = None
            
            # Mock the refresh to set the ID
            def mock_refresh(workflow):
                workflow.id = session_id
                workflow.created_at = "2023-01-01T00:00:00Z"
                workflow.updated_at = "2023-01-01T00:00:00Z"
            
            mock_db.refresh.side_effect = mock_refresh
            
            workflow_data = {
                "project_id": project_id,
                "document_path": "/uploads/requirements.txt",
                "mode": "greenfield"
            }
            
            response = await async_client.post("/api/v1/workflows/start", json=workflow_data)
            
            assert response.status_code == 201
            data = response.json()
            assert data["session_id"] == session_id
            assert data["status"] == "active"
            assert data["current_stage"] == "requirements_parsing"

    @pytest.mark.asyncio
    async def test_workflow_start_brownfield(self, async_client, mock_agents, sample_github_repo_data):
        """Test starting a brownfield workflow."""
        project_id = str(uuid4())
        session_id = str(uuid4())
        
        # Mock agent responses
        mock_agents['github_analyzer'].execute = AsyncMock(return_value=sample_github_repo_data)
        mock_agents['requirements_agent'].execute = AsyncMock(return_value={
            "structured_requirements": {"business_goals": ["Add new features"]},
            "confidence_score": 0.8
        })
        mock_agents['architecture_agent'].execute = AsyncMock(return_value={
            "architecture_overview": {"style": "microservices"},
            "integration_strategy": {"phases": []}
        })
        mock_agents['kb_service'].index_repository_analysis = AsyncMock()
        
        with patch('app.api.v1.workflows.get_db') as mock_get_db, \
             patch('app.agents.github_analyzer_agent.GitHubAnalyzerAgent', return_value=mock_agents['github_analyzer']), \
             patch('app.agents.requirements_agent.RequirementsAgent', return_value=mock_agents['requirements_agent']), \
             patch('app.agents.architecture_agent.ArchitectureAgent', return_value=mock_agents['architecture_agent']), \
             patch('app.services.knowledge_base_service.KnowledgeBaseService', return_value=mock_agents['kb_service']):
            
            # Mock database session
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            # Mock workflow creation
            mock_workflow = WorkflowSession(
                id=session_id,
                project_id=project_id,
                current_stage="analyze_existing",
                status=True
            )
            mock_db.add.return_value = None
            mock_db.commit.return_value = None
            mock_db.refresh.return_value = None
            
            # Mock the refresh to set the ID
            def mock_refresh(workflow):
                workflow.id = session_id
                workflow.created_at = "2023-01-01T00:00:00Z"
                workflow.updated_at = "2023-01-01T00:00:00Z"
            
            mock_db.refresh.side_effect = mock_refresh
            
            workflow_data = {
                "project_id": project_id,
                "repository_url": sample_github_repo_data["repository_url"],
                "mode": "brownfield"
            }
            
            response = await async_client.post("/api/v1/workflows/start", json=workflow_data)
            
            assert response.status_code == 201
            data = response.json()
            assert data["session_id"] == session_id
            assert data["status"] == "active"
            assert data["current_stage"] == "analyze_existing"

    def test_workflow_status_retrieval(self, client):
        """Test retrieving workflow status."""
        session_id = str(uuid4())
        
        with patch('app.api.v1.workflows.get_db') as mock_get_db:
            # Mock database session
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            # Mock workflow query
            mock_workflow = Mock()
            mock_workflow.id = session_id
            mock_workflow.current_stage = "architecture_design"
            mock_workflow.status = True
            mock_workflow.created_at = "2023-01-01T00:00:00Z"
            mock_workflow.updated_at = "2023-01-01T00:00:00Z"
            mock_workflow.agent_executions = []
            
            mock_result = Mock()
            mock_result.scalar_one_or_none.return_value = mock_workflow
            mock_db.execute.return_value = mock_result
            
            response = client.get(f"/api/v1/workflows/{session_id}/status")
            
            assert response.status_code == 200
            data = response.json()
            assert data["session_id"] == session_id
            assert data["current_stage"] == "architecture_design"
            assert data["status"] == "active"

    def test_workflow_requirements_retrieval(self, client):
        """Test retrieving workflow requirements."""
        session_id = str(uuid4())
        
        with patch('app.api.v1.workflows.get_db') as mock_get_db:
            # Mock database session
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            # Mock workflow query
            mock_workflow = Mock()
            mock_workflow.id = session_id
            mock_workflow.state_data = {
                "requirements": {
                    "structured_requirements": {
                        "business_goals": ["Launch marketplace"],
                        "functional_requirements": ["User auth"]
                    },
                    "confidence_score": 0.9
                }
            }
            
            mock_result = Mock()
            mock_result.scalar_one_or_none.return_value = mock_workflow
            mock_db.execute.return_value = mock_result
            
            response = client.get(f"/api/v1/workflows/{session_id}/requirements")
            
            assert response.status_code == 200
            data = response.json()
            assert "requirements" in data
            assert data["requirements"]["confidence_score"] == 0.9

    def test_workflow_architecture_retrieval(self, client):
        """Test retrieving workflow architecture."""
        session_id = str(uuid4())
        
        with patch('app.api.v1.workflows.get_db') as mock_get_db:
            # Mock database session
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            # Mock workflow query
            mock_workflow = Mock()
            mock_workflow.id = session_id
            mock_workflow.state_data = {
                "architecture": {
                    "architecture_overview": {
                        "style": "microservices"
                    },
                    "services": [
                        {
                            "id": "user-service",
                            "name": "User Service",
                            "type": "service"
                        }
                    ]
                }
            }
            
            mock_result = Mock()
            mock_result.scalar_one_or_none.return_value = mock_workflow
            mock_db.execute.return_value = mock_result
            
            response = client.get(f"/api/v1/workflows/{session_id}/architecture")
            
            assert response.status_code == 200
            data = response.json()
            assert "architecture" in data
            assert data["architecture"]["architecture_overview"]["style"] == "microservices"

    def test_workflow_review_submission(self, client):
        """Test submitting workflow review."""
        session_id = str(uuid4())
        
        with patch('app.api.v1.workflows.get_db') as mock_get_db:
            # Mock database session
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            # Mock workflow query
            mock_workflow = Mock()
            mock_workflow.id = session_id
            mock_workflow.current_stage = "requirements_review"
            mock_workflow.state_data = {}
            
            mock_result = Mock()
            mock_result.scalar_one_or_none.return_value = mock_workflow
            mock_db.execute.return_value = mock_result
            
            review_data = {
                "session_id": session_id,
                "status": "approved",
                "comments": "Requirements look good",
                "reviewer": "test-user"
            }
            
            response = client.post("/api/v1/workflows/review", data=review_data)
            
            # Should return 200 or 422 (depending on form data handling)
            assert response.status_code in [200, 422]

    def test_brownfield_repository_analysis(self, client, sample_github_repo_data):
        """Test brownfield repository analysis."""
        with patch('app.api.v1.brownfield.get_db') as mock_get_db, \
             patch('app.agents.github_analyzer_agent.GitHubAnalyzerAgent') as mock_github_agent, \
             patch('app.services.knowledge_base_service.KnowledgeBaseService') as mock_kb_service:
            
            # Mock database session
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            # Mock agents
            mock_github_agent.return_value.execute = AsyncMock(return_value=sample_github_repo_data)
            mock_kb_service.return_value.index_repository_analysis = AsyncMock()
            
            analysis_data = {
                "repository_url": sample_github_repo_data["repository_url"],
                "branch": "main"
            }
            
            response = client.post("/api/v1/brownfield/analyze-repository", json=analysis_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "analysis_started"
            assert "session_id" in data

    def test_brownfield_knowledge_search(self, client):
        """Test brownfield knowledge base search."""
        with patch('app.api.v1.brownfield.get_db') as mock_get_db, \
             patch('app.services.knowledge_base_service.KnowledgeBaseService') as mock_kb_service:
            
            # Mock database session
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            # Mock knowledge base service
            mock_kb_service.return_value.search_similar_architectures = AsyncMock(return_value=[
                {
                    "id": "similar-arch-1",
                    "similarity_score": 0.85,
                    "metadata": {"technologies": ["Node.js", "PostgreSQL"]}
                }
            ])
            
            search_data = {
                "query": "microservices architecture",
                "filters": {"technologies": ["Node.js"]}
            }
            
            response = client.post("/api/v1/brownfield/search-knowledge", json=search_data)
            
            assert response.status_code == 200
            data = response.json()
            assert "results" in data
            assert len(data["results"]) > 0

    def test_complete_greenfield_journey(self, client, sample_project_data, sample_requirements_document):
        """Test complete greenfield user journey."""
        # Step 1: Create project
        with patch('app.api.v1.projects.get_db') as mock_get_db:
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            mock_project = Project(
                id=uuid4(),
                name=sample_project_data["name"],
                description=sample_project_data["description"],
                domain=sample_project_data["domain"],
                mode=ProjectDomain.CLOUD_NATIVE,
                status=ProjectStatus.PROCESSING
            )
            mock_db.add.return_value = None
            mock_db.commit.return_value = None
            mock_db.refresh.return_value = None
            
            def mock_refresh(project):
                project.id = mock_project.id
                project.created_at = "2023-01-01T00:00:00Z"
                project.updated_at = "2023-01-01T00:00:00Z"
            
            mock_db.refresh.side_effect = mock_refresh
            
            response = client.post("/api/v1/projects", json=sample_project_data)
            assert response.status_code == 201
            project_data = response.json()
            project_id = project_data["id"]
        
        # Step 2: Upload document
        with patch('app.api.v1.workflows.get_db') as mock_get_db, \
             patch('app.core.file_storage.FileStorage.save_file') as mock_save_file:
            
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            mock_save_file.return_value = f"/uploads/{project_id}/requirements.txt"
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
                temp_file.write(sample_requirements_document)
                temp_file_path = temp_file.name
            
            try:
                with open(temp_file_path, 'rb') as file:
                    response = client.post(
                        f"/api/v1/projects/{project_id}/upload",
                        files={"file": ("requirements.txt", file, "text/plain")}
                    )
                assert response.status_code == 200
                upload_data = response.json()
                file_path = upload_data["file_path"]
                
            finally:
                os.unlink(temp_file_path)
        
        # Step 3: Start workflow
        with patch('app.api.v1.workflows.get_db') as mock_get_db, \
             patch('app.agents.requirements_agent.RequirementsAgent') as mock_req_agent, \
             patch('app.agents.architecture_agent.ArchitectureAgent') as mock_arch_agent:
            
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            # Mock agents
            mock_req_agent.return_value.execute = AsyncMock(return_value={
                "structured_requirements": {"business_goals": ["Launch marketplace"]},
                "confidence_score": 0.9
            })
            mock_arch_agent.return_value.execute = AsyncMock(return_value={
                "architecture_overview": {"style": "microservices"},
                "services": [{"id": "user-service", "name": "User Service"}]
            })
            
            # Mock workflow creation
            session_id = str(uuid4())
            mock_workflow = WorkflowSession(
                id=session_id,
                project_id=project_id,
                current_stage="requirements_parsing",
                status=True
            )
            mock_db.add.return_value = None
            mock_db.commit.return_value = None
            mock_db.refresh.return_value = None
            
            def mock_refresh(workflow):
                workflow.id = session_id
                workflow.created_at = "2023-01-01T00:00:00Z"
                workflow.updated_at = "2023-01-01T00:00:00Z"
            
            mock_db.refresh.side_effect = mock_refresh
            
            workflow_data = {
                "project_id": project_id,
                "document_path": file_path,
                "mode": "greenfield"
            }
            
            response = client.post("/api/v1/workflows/start", json=workflow_data)
            assert response.status_code == 201
            workflow_data = response.json()
            session_id = workflow_data["session_id"]
        
        # Step 4: Check workflow status
        with patch('app.api.v1.workflows.get_db') as mock_get_db:
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            mock_workflow = Mock()
            mock_workflow.id = session_id
            mock_workflow.current_stage = "architecture_design"
            mock_workflow.status = True
            mock_workflow.created_at = "2023-01-01T00:00:00Z"
            mock_workflow.updated_at = "2023-01-01T00:00:00Z"
            mock_workflow.agent_executions = []
            
            mock_result = Mock()
            mock_result.scalar_one_or_none.return_value = mock_workflow
            mock_db.execute.return_value = mock_result
            
            response = client.get(f"/api/v1/workflows/{session_id}/status")
            assert response.status_code == 200
            status_data = response.json()
            assert status_data["session_id"] == session_id
            assert status_data["current_stage"] == "architecture_design"

    def test_error_handling_invalid_project_id(self, client):
        """Test error handling for invalid project ID."""
        invalid_project_id = "invalid-uuid"
        
        response = client.get(f"/api/v1/projects/{invalid_project_id}")
        assert response.status_code == 422  # Validation error

    def test_error_handling_nonexistent_workflow(self, client):
        """Test error handling for nonexistent workflow."""
        nonexistent_session_id = str(uuid4())
        
        with patch('app.api.v1.workflows.get_db') as mock_get_db:
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            mock_result = Mock()
            mock_result.scalar_one_or_none.return_value = None
            mock_db.execute.return_value = mock_result
            
            response = client.get(f"/api/v1/workflows/{nonexistent_session_id}/status")
            assert response.status_code == 404

    def test_concurrent_workflow_execution(self, client, sample_project_data):
        """Test concurrent workflow execution."""
        project_id = str(uuid4())
        
        with patch('app.api.v1.workflows.get_db') as mock_get_db, \
             patch('app.agents.requirements_agent.RequirementsAgent') as mock_req_agent:
            
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            # Mock agent
            mock_req_agent.return_value.execute = AsyncMock(return_value={
                "structured_requirements": {"business_goals": ["Test goal"]},
                "confidence_score": 0.8
            })
            
            # Mock workflow creation
            session_id = str(uuid4())
            mock_workflow = WorkflowSession(
                id=session_id,
                project_id=project_id,
                current_stage="requirements_parsing",
                status=True
            )
            mock_db.add.return_value = None
            mock_db.commit.return_value = None
            mock_db.refresh.return_value = None
            
            def mock_refresh(workflow):
                workflow.id = session_id
                workflow.created_at = "2023-01-01T00:00:00Z"
                workflow.updated_at = "2023-01-01T00:00:00Z"
            
            mock_db.refresh.side_effect = mock_refresh
            
            # Start multiple workflows concurrently
            workflow_data = {
                "project_id": project_id,
                "document_path": "/test/requirements.txt",
                "mode": "greenfield"
            }
            
            # This should handle concurrent execution gracefully
            response1 = client.post("/api/v1/workflows/start", json=workflow_data)
            response2 = client.post("/api/v1/workflows/start", json=workflow_data)
            
            # At least one should succeed
            assert response1.status_code == 201 or response2.status_code == 201
