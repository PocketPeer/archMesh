"""
API Integration Tests

These tests verify the complete API integration including all endpoints,
authentication, error handling, and data flow between services.
"""

import pytest
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


class TestAPIIntegration:
    """Test complete API integration."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    @pytest.fixture
    def async_client(self):
        """Create async test client."""
        return AsyncClient(app=app, base_url="http://test")

    @pytest.fixture
    def sample_project(self):
        """Sample project for testing."""
        return {
            "id": str(uuid4()),
            "name": "Test Project",
            "description": "Test project description",
            "domain": "e-commerce",
            "mode": "greenfield",
            "status": "active",
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z"
        }

    def test_api_root_endpoint(self, client):
        """Test API root endpoint."""
        response = client.get("/")
        assert response.status_code == 200

    def test_api_docs_endpoint(self, client):
        """Test API documentation endpoint."""
        response = client.get("/docs")
        assert response.status_code == 200

    def test_api_openapi_endpoint(self, client):
        """Test OpenAPI schema endpoint."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data

    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        with patch('app.core.redis_client.redis_client.ping', return_value=True):
            response = client.get("/api/v1/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert "timestamp" in data
            assert "version" in data

    def test_health_endpoint_unhealthy(self, client):
        """Test health check endpoint when unhealthy."""
        with patch('app.core.redis_client.redis_client.ping', return_value=False):
            response = client.get("/api/v1/health")
            assert response.status_code == 503
            data = response.json()
            assert data["status"] == "unhealthy"

    def test_projects_crud_operations(self, client, sample_project):
        """Test complete CRUD operations for projects."""
        project_id = sample_project["id"]
        
        with patch('app.api.v1.projects.get_db') as mock_get_db:
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            # Mock project object
            mock_project = Project(
                id=project_id,
                name=sample_project["name"],
                description=sample_project["description"],
                domain=sample_project["domain"],
                mode=ProjectDomain.CLOUD_NATIVE,
                status=ProjectStatus.PROCESSING
            )
            
            # CREATE
            mock_db.add.return_value = None
            mock_db.commit.return_value = None
            mock_db.refresh.return_value = None
            
            def mock_refresh(project):
                project.id = project_id
                project.created_at = "2023-01-01T00:00:00Z"
                project.updated_at = "2023-01-01T00:00:00Z"
            
            mock_db.refresh.side_effect = mock_refresh
            
            create_data = {
                "name": sample_project["name"],
                "description": sample_project["description"],
                "domain": sample_project["domain"],
                "mode": "greenfield"
            }
            
            response = client.post("/api/v1/projects", json=create_data)
            assert response.status_code == 201
            created_project = response.json()
            assert created_project["name"] == sample_project["name"]
            
            # READ
            mock_result = Mock()
            mock_result.scalar_one_or_none.return_value = mock_project
            mock_db.execute.return_value = mock_result
            
            response = client.get(f"/api/v1/projects/{project_id}")
            assert response.status_code == 200
            retrieved_project = response.json()
            assert retrieved_project["id"] == project_id
            
            # UPDATE
            update_data = {
                "name": "Updated Project Name",
                "description": "Updated description"
            }
            
            response = client.put(f"/api/v1/projects/{project_id}", json=update_data)
            assert response.status_code == 200
            updated_project = response.json()
            assert updated_project["name"] == "Updated Project Name"
            
            # DELETE
            mock_db.delete.return_value = None
            mock_db.commit.return_value = None
            
            response = client.delete(f"/api/v1/projects/{project_id}")
            assert response.status_code == 204

    def test_projects_list_with_pagination(self, client):
        """Test projects list endpoint with pagination."""
        with patch('app.api.v1.projects.get_db') as mock_get_db:
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            # Mock projects list
            mock_projects = [
                Project(
                    id=str(uuid4()),
                    name=f"Project {i}",
                    description=f"Description {i}",
                    domain="e-commerce",
                    mode=ProjectDomain.CLOUD_NATIVE,
                    status=ProjectStatus.PROCESSING
                )
                for i in range(5)
            ]
            
            mock_result = Mock()
            mock_result.scalars.return_value.all.return_value = mock_projects
            mock_result.scalar.return_value = 5
            mock_db.execute.return_value = mock_result
            
            # Test without pagination
            response = client.get("/api/v1/projects")
            assert response.status_code == 200
            data = response.json()
            assert "projects" in data
            assert "total" in data
            assert len(data["projects"]) == 5
            
            # Test with pagination
            response = client.get("/api/v1/projects?page=1&size=2")
            assert response.status_code == 200
            data = response.json()
            assert len(data["projects"]) == 2

    def test_projects_filtering(self, client):
        """Test projects filtering by domain and status."""
        with patch('app.api.v1.projects.get_db') as mock_get_db:
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            # Mock filtered projects
            mock_projects = [
                Project(
                    id=str(uuid4()),
                    name="E-commerce Project",
                    description="E-commerce description",
                    domain="e-commerce",
                    mode=ProjectDomain.CLOUD_NATIVE,
                    status=ProjectStatus.PROCESSING
                )
            ]
            
            mock_result = Mock()
            mock_result.scalars.return_value.all.return_value = mock_projects
            mock_result.scalar.return_value = 1
            mock_db.execute.return_value = mock_result
            
            # Test filtering by domain
            response = client.get("/api/v1/projects?domain=e-commerce")
            assert response.status_code == 200
            data = response.json()
            assert len(data["projects"]) == 1
            assert data["projects"][0]["domain"] == "e-commerce"
            
            # Test filtering by status
            response = client.get("/api/v1/projects?status=active")
            assert response.status_code == 200
            data = response.json()
            assert len(data["projects"]) == 1
            assert data["projects"][0]["status"] == "active"

    def test_projects_statistics(self, client):
        """Test projects statistics endpoint."""
        with patch('app.api.v1.projects.get_db') as mock_get_db:
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            # Mock statistics
            mock_stats = {
                "total_projects": 10,
                "active_projects": 8,
                "completed_projects": 2,
                "projects_by_domain": {
                    "e-commerce": 5,
                    "healthcare": 3,
                    "finance": 2
                },
                "projects_by_mode": {
                    "greenfield": 7,
                    "brownfield": 3
                }
            }
            
            mock_result = Mock()
            mock_result.scalar.return_value = 10
            mock_db.execute.return_value = mock_result
            
            response = client.get("/api/v1/projects/statistics")
            assert response.status_code == 200
            data = response.json()
            assert "total_projects" in data

    def test_workflows_crud_operations(self, client):
        """Test complete CRUD operations for workflows."""
        session_id = str(uuid4())
        project_id = str(uuid4())
        
        with patch('app.api.v1.workflows.get_db') as mock_get_db:
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            # Mock workflow object
            mock_workflow = WorkflowSession(
                id=session_id,
                project_id=project_id,
                current_stage="requirements_parsing",
                status=True
            )
            
            # CREATE
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
                "document_path": "/test/requirements.txt",
                "mode": "greenfield"
            }
            
            with patch('app.agents.requirements_agent.RequirementsAgent') as mock_req_agent:
                mock_req_agent.return_value.execute = AsyncMock(return_value={
                    "structured_requirements": {"business_goals": ["Test goal"]},
                    "confidence_score": 0.8
                })
                
                response = client.post("/api/v1/workflows/start", json=workflow_data)
                assert response.status_code == 201
                created_workflow = response.json()
                assert created_workflow["session_id"] == session_id
            
            # READ
            mock_result = Mock()
            mock_result.scalar_one_or_none.return_value = mock_workflow
            mock_db.execute.return_value = mock_result
            
            response = client.get(f"/api/v1/workflows/{session_id}/status")
            assert response.status_code == 200
            retrieved_workflow = response.json()
            assert retrieved_workflow["session_id"] == session_id

    def test_workflows_list_with_pagination(self, client):
        """Test workflows list endpoint with pagination."""
        with patch('app.api.v1.workflows.get_db') as mock_get_db:
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            # Mock workflows list
            mock_workflows = [
                WorkflowSession(
                    id=str(uuid4()),
                    project_id=str(uuid4()),
                    current_stage="requirements_parsing",
                    status=True
                )
                for i in range(3)
            ]
            
            mock_result = Mock()
            mock_result.scalars.return_value.all.return_value = mock_workflows
            mock_result.scalar.return_value = 3
            mock_db.execute.return_value = mock_result
            
            response = client.get("/api/v1/workflows")
            assert response.status_code == 200
            data = response.json()
            assert "workflows" in data
            assert "total" in data
            assert len(data["workflows"]) == 3

    def test_workflow_requirements_retrieval(self, client):
        """Test workflow requirements retrieval."""
        session_id = str(uuid4())
        
        with patch('app.api.v1.workflows.get_db') as mock_get_db:
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            # Mock workflow with requirements
            mock_workflow = Mock()
            mock_workflow.id = session_id
            mock_workflow.state_data = {
                "requirements": {
                    "structured_requirements": {
                        "business_goals": ["Launch marketplace", "Increase revenue"],
                        "functional_requirements": ["User authentication", "Product catalog"],
                        "non_functional_requirements": {
                            "performance": ["Response time < 200ms"],
                            "security": ["PCI DSS compliance"]
                        }
                    },
                    "confidence_score": 0.92
                }
            }
            
            mock_result = Mock()
            mock_result.scalar_one_or_none.return_value = mock_workflow
            mock_db.execute.return_value = mock_result
            
            response = client.get(f"/api/v1/workflows/{session_id}/requirements")
            assert response.status_code == 200
            data = response.json()
            assert "requirements" in data
            assert data["requirements"]["confidence_score"] == 0.92
            assert len(data["requirements"]["structured_requirements"]["business_goals"]) == 2

    def test_workflow_architecture_retrieval(self, client):
        """Test workflow architecture retrieval."""
        session_id = str(uuid4())
        
        with patch('app.api.v1.workflows.get_db') as mock_get_db:
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            # Mock workflow with architecture
            mock_workflow = Mock()
            mock_workflow.id = session_id
            mock_workflow.state_data = {
                "architecture": {
                    "architecture_overview": {
                        "style": "microservices",
                        "rationale": "Scalable and maintainable architecture"
                    },
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
                    "quality_score": 0.85
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
            assert len(data["architecture"]["services"]) == 2
            assert data["architecture"]["quality_score"] == 0.85

    def test_brownfield_api_endpoints(self, client):
        """Test brownfield API endpoints."""
        with patch('app.api.v1.brownfield.get_db') as mock_get_db, \
             patch('app.agents.github_analyzer_agent.GitHubAnalyzerAgent') as mock_github_agent, \
             patch('app.services.knowledge_base_service.KnowledgeBaseService') as mock_kb_service:
            
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            # Mock agents
            mock_github_agent.return_value.execute = AsyncMock(return_value={
                "repository_url": "https://github.com/test/repo",
                "services": [{"id": "test-service", "name": "Test Service"}],
                "technology_stack": {"Node.js": 1}
            })
            mock_kb_service.return_value.index_repository_analysis = AsyncMock()
            mock_kb_service.return_value.search_similar_architectures = AsyncMock(return_value=[
                {"id": "similar-1", "similarity_score": 0.85}
            ])
            
            # Test repository analysis
            analysis_data = {
                "repository_url": "https://github.com/test/repo",
                "branch": "main"
            }
            
            response = client.post("/api/v1/brownfield/analyze-repository", json=analysis_data)
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "analysis_started"
            assert "session_id" in data
            
            # Test knowledge search
            search_data = {
                "query": "microservices architecture",
                "filters": {"technologies": ["Node.js"]}
            }
            
            response = client.post("/api/v1/brownfield/search-knowledge", json=search_data)
            assert response.status_code == 200
            data = response.json()
            assert "results" in data
            assert len(data["results"]) > 0

    def test_file_upload_endpoint(self, client):
        """Test file upload endpoint."""
        project_id = str(uuid4())
        
        with patch('app.api.v1.workflows.get_db') as mock_get_db, \
             patch('app.core.file_storage.FileStorage.save_file') as mock_save_file:
            
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            mock_save_file.return_value = f"/uploads/{project_id}/requirements.txt"
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
                temp_file.write("Test requirements content")
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

    def test_error_handling_validation_errors(self, client):
        """Test validation error handling."""
        # Test invalid project data
        invalid_project_data = {
            "name": "",  # Empty name should fail validation
            "domain": "invalid-domain"  # Invalid domain
        }
        
        response = client.post("/api/v1/projects", json=invalid_project_data)
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
        assert "errors" in data

    def test_error_handling_not_found(self, client):
        """Test not found error handling."""
        nonexistent_id = str(uuid4())
        
        with patch('app.api.v1.projects.get_db') as mock_get_db:
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            mock_result = Mock()
            mock_result.scalar_one_or_none.return_value = None
            mock_db.execute.return_value = mock_result
            
            response = client.get(f"/api/v1/projects/{nonexistent_id}")
            assert response.status_code == 404

    def test_error_handling_server_errors(self, client):
        """Test server error handling."""
        with patch('app.api.v1.projects.get_db') as mock_get_db:
            mock_db = Mock()
            mock_get_db.side_effect = Exception("Database connection failed")
            
            response = client.get("/api/v1/projects")
            assert response.status_code == 500

    def test_cors_headers(self, client):
        """Test CORS headers are present."""
        response = client.options("/api/v1/health")
        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers

    def test_content_type_headers(self, client):
        """Test content type headers."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"

    def test_rate_limiting_headers(self, client):
        """Test rate limiting headers (if implemented)."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        # Rate limiting headers would be present if implemented
        # assert "x-ratelimit-limit" in response.headers

    def test_api_versioning(self, client):
        """Test API versioning."""
        # Test v1 endpoints
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        
        # Test that v1 is the current version
        response = client.get("/api/health")
        assert response.status_code == 404  # Should not exist without version

    def test_concurrent_requests(self, client):
        """Test handling of concurrent requests."""
        import threading
        import time
        
        results = []
        
        def make_request():
            with patch('app.core.redis_client.redis_client.ping', return_value=True):
                response = client.get("/api/v1/health")
                results.append(response.status_code)
        
        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All requests should succeed
        assert all(status == 200 for status in results)
        assert len(results) == 5

    def test_large_payload_handling(self, client):
        """Test handling of large payloads."""
        # Create a large project description
        large_description = "A" * 10000  # 10KB description
        
        with patch('app.api.v1.projects.get_db') as mock_get_db:
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            mock_project = Project(
                id=str(uuid4()),
                name="Large Project",
                description=large_description,
                domain="e-commerce",
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
            
            project_data = {
                "name": "Large Project",
                "description": large_description,
                "domain": "e-commerce",
                "mode": "greenfield"
            }
            
            response = client.post("/api/v1/projects", json=project_data)
            assert response.status_code == 201
            data = response.json()
            assert len(data["description"]) == 10000
