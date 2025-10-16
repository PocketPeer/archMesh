"""
Unit tests for API endpoints.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import AsyncClient
from fastapi import status

from app.models import Project, WorkflowSession


class TestProjectEndpoints:
    """Test cases for project-related API endpoints."""
    
    @pytest.mark.asyncio
    async def test_create_project(self, client: AsyncClient, sample_project_data):
        """Test project creation."""
        response = await client.post("/api/v1/projects/", json=sample_project_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == sample_project_data["name"]
        assert data["description"] == sample_project_data["description"]
        assert data["domain"] == sample_project_data["domain"]
        assert "id" in data
        assert "created_at" in data
    
    @pytest.mark.asyncio
    async def test_get_project(self, client: AsyncClient, sample_project_data):
        """Test getting a project by ID."""
        # First create a project
        create_response = await client.post("/api/v1/projects/", json=sample_project_data)
        project_id = create_response.json()["id"]
        
        # Then get it
        response = await client.get(f"/api/v1/projects/{project_id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == project_id
        assert data["name"] == sample_project_data["name"]
    
    @pytest.mark.asyncio
    async def test_get_project_not_found(self, client: AsyncClient):
        """Test getting a non-existent project."""
        response = await client.get("/api/v1/projects/nonexistent-id")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.asyncio
    async def test_list_projects(self, client: AsyncClient, sample_project_data):
        """Test listing projects."""
        # Create a few projects
        for i in range(3):
            project_data = sample_project_data.copy()
            project_data["name"] = f"Test Project {i}"
            await client.post("/api/v1/projects/", json=project_data)
        
        # List projects
        response = await client.get("/api/v1/projects/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["items"]) >= 3
        assert data["total"] >= 3
    
    @pytest.mark.asyncio
    async def test_update_project(self, client: AsyncClient, sample_project_data):
        """Test updating a project."""
        # Create a project
        create_response = await client.post("/api/v1/projects/", json=sample_project_data)
        project_id = create_response.json()["id"]
        
        # Update it
        update_data = {"name": "Updated Project Name", "status": "processing"}
        response = await client.put(f"/api/v1/projects/{project_id}", json=update_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Updated Project Name"
        assert data["status"] == "processing"
    
    @pytest.mark.asyncio
    async def test_delete_project(self, client: AsyncClient, sample_project_data):
        """Test deleting a project."""
        # Create a project
        create_response = await client.post("/api/v1/projects/", json=sample_project_data)
        project_id = create_response.json()["id"]
        
        # Delete it
        response = await client.delete(f"/api/v1/projects/{project_id}")
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify it's deleted
        get_response = await client.get(f"/api/v1/projects/{project_id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND


class TestWorkflowEndpoints:
    """Test cases for workflow-related API endpoints."""
    
    @pytest.mark.asyncio
    async def test_start_architecture_workflow(self, client: AsyncClient, sample_project_data):
        """Test starting an architecture workflow."""
        # Create a project first
        project_response = await client.post("/api/v1/projects/", json=sample_project_data)
        project_id = project_response.json()["id"]
        
        # Mock file upload
        with patch('app.core.file_storage.FileStorage.save_uploaded_file') as mock_save:
            mock_save.return_value = {
                "file_id": "test-file-id",
                "file_path": "/test/path/document.txt"
            }
            
            with patch('app.workflows.architecture_workflow.ArchitectureWorkflow.start') as mock_start:
                mock_start.return_value = ("test-session-id", {"status": "started"})
                
                with patch('app.core.file_storage.FileStorage.move_to_processed'):
                    # Create a test file
                    test_file_content = b"Test document content"
                    
                    response = await client.post(
                        "/api/v1/workflows/start-architecture",
                        data={
                            "project_id": project_id,
                            "domain": "cloud-native",
                            "project_context": "Test context",
                            "llm_provider": "deepseek"
                        },
                        files={"file": ("test.txt", test_file_content, "text/plain")}
                    )
                    
                    assert response.status_code == status.HTTP_201_CREATED
                    data = response.json()
                    assert "session_id" in data
                    assert data["project_id"] == project_id
    
    @pytest.mark.asyncio
    async def test_get_workflow_status(self, client: AsyncClient, sample_workflow_data):
        """Test getting workflow status."""
        # Mock the workflow status
        with patch('app.api.v1.workflows.get_workflow_from_db') as mock_get:
            mock_workflow = MagicMock()
            mock_workflow.id = "test-session-id"
            mock_workflow.current_stage = "starting"
            mock_workflow.state_data = sample_workflow_data["state_data"]
            mock_workflow.is_active = True
            mock_get.return_value = mock_workflow
            
            response = await client.get("/api/v1/workflows/test-session-id/status")
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["session_id"] == "test-session-id"
            assert data["current_stage"] == "starting"
    
    @pytest.mark.asyncio
    async def test_get_workflow_requirements(self, client: AsyncClient, sample_requirements_data):
        """Test getting workflow requirements."""
        with patch('app.api.v1.workflows.get_workflow_from_db') as mock_get:
            mock_workflow = MagicMock()
            mock_workflow.id = "test-session-id"
            mock_workflow.state_data = {"requirements": sample_requirements_data}
            mock_get.return_value = mock_workflow
            
            response = await client.get("/api/v1/workflows/test-session-id/requirements")
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "requirements" in data
            assert data["requirements"]["structured_requirements"]["business_goals"] == ["Launch online marketplace", "Increase revenue"]
    
    @pytest.mark.asyncio
    async def test_get_workflow_architecture(self, client: AsyncClient, sample_architecture_data):
        """Test getting workflow architecture."""
        with patch('app.api.v1.workflows.get_workflow_from_db') as mock_get:
            mock_workflow = MagicMock()
            mock_workflow.id = "test-session-id"
            mock_workflow.state_data = {"architecture": sample_architecture_data}
            mock_get.return_value = mock_workflow
            
            response = await client.get("/api/v1/workflows/test-session-id/architecture")
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "architecture" in data
            assert data["architecture"]["overview"] == "Microservices-based e-commerce platform"
    
    @pytest.mark.asyncio
    async def test_submit_workflow_review(self, client: AsyncClient):
        """Test submitting workflow review."""
        with patch('app.workflows.architecture_workflow.ArchitectureWorkflow.continue_workflow') as mock_continue:
            mock_continue.return_value = {
                "current_stage": "design_architecture",
                "last_updated": "2024-01-01T00:00:00Z"
            }
            
            response = await client.post(
                "/api/v1/workflows/test-session-id/review",
                data={
                    "decision": "approved",
                    "comments": "Looks good",
                    "constraints": "{}",
                    "preferences": "[]"
                }
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["session_id"] == "test-session-id"
            assert data["feedback_submitted"] is True
            assert data["decision"] == "approved"
    
    @pytest.mark.asyncio
    async def test_submit_workflow_review_invalid_decision(self, client: AsyncClient):
        """Test submitting workflow review with invalid decision."""
        response = await client.post(
            "/api/v1/workflows/test-session-id/review",
            data={
                "decision": "invalid_decision",
                "comments": "Test comment"
            }
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "Invalid decision" in data["detail"]


class TestHealthEndpoint:
    """Test cases for health check endpoint."""
    
    @pytest.mark.asyncio
    async def test_health_check(self, client: AsyncClient):
        """Test health check endpoint."""
        response = await client.get("/api/v1/health")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data


class TestErrorHandling:
    """Test cases for error handling in API endpoints."""
    
    @pytest.mark.asyncio
    async def test_internal_server_error(self, client: AsyncClient):
        """Test handling of internal server errors."""
        with patch('app.api.v1.projects.create_project', side_effect=Exception("Database error")):
            response = await client.post("/api/v1/projects/", json={"name": "Test"})
            
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            data = response.json()
            assert "error" in data["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_validation_error(self, client: AsyncClient):
        """Test handling of validation errors."""
        response = await client.post("/api/v1/projects/", json={"invalid_field": "value"})
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
