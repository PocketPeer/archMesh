"""
Unit tests for Project Ownership Service - TDD Implementation
Following Red-Green-Refactor cycle for project ownership, access control, and user-project relationships
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from app.services.project_ownership_service import ProjectOwnershipService
from app.models.user import User
from app.models.project import Project
from app.schemas.project_ownership import (
    ProjectAccessRequest, ProjectShareRequest, ProjectPermissionRequest,
    ProjectOwnershipResponse, ProjectAccessResponse, ProjectShareResponse
)
from app.core.exceptions import ProjectAccessError, OwnershipError, PermissionError


class TestProjectOwnershipService:
    """Test cases for Project Ownership Service - TDD Implementation"""
    
    @pytest.fixture
    def ownership_service(self):
        """Create a test instance of ProjectOwnershipService"""
        return ProjectOwnershipService()
    
    @pytest.fixture
    def sample_owner(self):
        """Create a sample project owner"""
        return User(
            id="owner-123",
            email="owner@example.com",
            username="projectowner",
            first_name="Project",
            last_name="Owner",
            hashed_password="$2b$12$hashed_password",
            is_active=True,
            is_verified=True
        )
    
    @pytest.fixture
    def sample_collaborator(self):
        """Create a sample collaborator"""
        return User(
            id="collaborator-456",
            email="collaborator@example.com",
            username="collaborator",
            first_name="Project",
            last_name="Collaborator",
            hashed_password="$2b$12$hashed_password",
            is_active=True,
            is_verified=True
        )
    
    @pytest.fixture
    def sample_project(self, sample_owner):
        """Create a sample project"""
        return Project(
            id="project-789",
            name="Test Project",
            description="A test project",
            domain="software",
            status="active",
            owner_id=sample_owner.id
        )

    # RED PHASE: Write failing tests first
    
    @pytest.mark.asyncio
    async def test_get_user_projects_success(self, ownership_service, sample_owner, sample_project):
        """Test successful retrieval of user's projects"""
        # Arrange
        user_id = "owner-123"
        
        with patch.object(ownership_service, '_get_user_by_id', return_value=sample_owner):
            with patch.object(ownership_service, '_get_user_projects') as mock_get:
                mock_get.return_value = [sample_project]
                
                # Act
                result = await ownership_service.get_user_projects(user_id)
                
                # Assert
                assert result["success"] is True
                assert len(result["data"]["projects"]) == 1
                assert result["data"]["projects"][0]["id"] == str(sample_project.id)
                assert result["data"]["projects"][0]["name"] == sample_project.name
                assert result["data"]["owner_id"] == str(sample_owner.id)
    
    @pytest.mark.asyncio
    async def test_get_user_projects_user_not_found(self, ownership_service):
        """Test get user projects for non-existent user"""
        # Arrange
        user_id = "nonexistent-user"
        
        with patch.object(ownership_service, '_get_user_by_id', return_value=None):
            # Act
            result = await ownership_service.get_user_projects(user_id)
            
            # Assert
            assert result["success"] is False
            assert "User not found" in result["error"]
    
    @pytest.mark.asyncio
    async def test_check_project_access_owner_success(self, ownership_service, sample_owner, sample_project):
        """Test project access check for project owner"""
        # Arrange
        user_id = "owner-123"
        project_id = "project-789"
        
        with patch.object(ownership_service, '_get_user_by_id', return_value=sample_owner):
            with patch.object(ownership_service, '_get_project_by_id', return_value=sample_project):
                # Act
                result = await ownership_service.check_project_access(user_id, project_id)
                
                # Assert
                assert result["success"] is True
                assert result["data"]["has_access"] is True
                assert result["data"]["access_level"] == "owner"
                assert result["data"]["permissions"] == ["read", "write", "delete", "share"]
    
    @pytest.mark.asyncio
    async def test_check_project_access_collaborator_success(self, ownership_service, sample_collaborator, sample_project):
        """Test project access check for collaborator"""
        # Arrange
        user_id = "collaborator-456"
        project_id = "project-789"
        
        with patch.object(ownership_service, '_get_user_by_id', return_value=sample_collaborator):
            with patch.object(ownership_service, '_get_project_by_id', return_value=sample_project):
                with patch.object(ownership_service, '_get_user_project_permissions', return_value=["read", "write"]):
                    # Act
                    result = await ownership_service.check_project_access(user_id, project_id)
                    
                    # Assert
                    assert result["success"] is True
                    assert result["data"]["has_access"] is True
                    assert result["data"]["access_level"] == "collaborator"
                    assert result["data"]["permissions"] == ["read", "write"]
    
    @pytest.mark.asyncio
    async def test_check_project_access_no_access(self, ownership_service, sample_collaborator, sample_project):
        """Test project access check for user with no access"""
        # Arrange
        user_id = "collaborator-456"
        project_id = "project-789"
        
        with patch.object(ownership_service, '_get_user_by_id', return_value=sample_collaborator):
            with patch.object(ownership_service, '_get_project_by_id', return_value=sample_project):
                with patch.object(ownership_service, '_get_user_project_permissions', return_value=[]):
                    # Act
                    result = await ownership_service.check_project_access(user_id, project_id)
                    
                    # Assert
                    assert result["success"] is True
                    assert result["data"]["has_access"] is False
                    assert result["data"]["access_level"] == "none"
                    assert result["data"]["permissions"] == []
    
    @pytest.mark.asyncio
    async def test_check_project_access_project_not_found(self, ownership_service, sample_owner):
        """Test project access check for non-existent project"""
        # Arrange
        user_id = "owner-123"
        project_id = "nonexistent-project"
        
        with patch.object(ownership_service, '_get_user_by_id', return_value=sample_owner):
            with patch.object(ownership_service, '_get_project_by_id', return_value=None):
                # Act
                result = await ownership_service.check_project_access(user_id, project_id)
                
                # Assert
                assert result["success"] is False
                assert "Project not found" in result["error"]
    
    @pytest.mark.asyncio
    async def test_share_project_success(self, ownership_service, sample_owner, sample_collaborator, sample_project):
        """Test successful project sharing"""
        # Arrange
        owner_id = "owner-123"
        collaborator_id = "collaborator-456"
        project_id = "project-789"
        share_data = {
            "collaborator_email": "collaborator@example.com",
            "permissions": ["read", "write"],
            "message": "Please collaborate on this project"
        }
        
        with patch.object(ownership_service, '_get_user_by_id', return_value=sample_owner):
            with patch.object(ownership_service, '_get_project_by_id', return_value=sample_project):
                with patch.object(ownership_service, '_verify_ownership', return_value=True):
                    with patch.object(ownership_service, '_get_user_by_email', return_value=sample_collaborator):
                        with patch.object(ownership_service, '_grant_project_access') as mock_grant:
                            mock_grant.return_value = True
                            with patch.object(ownership_service, '_send_collaboration_invite') as mock_send:
                                mock_send.return_value = True
                                
                                # Act
                                result = await ownership_service.share_project(owner_id, project_id, share_data)
                                
                                # Assert
                                assert result["success"] is True
                                assert result["message"] == "Project shared successfully"
                                mock_grant.assert_called_once_with(collaborator_id, project_id, share_data["permissions"])
                                mock_send.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_share_project_not_owner(self, ownership_service, sample_collaborator, sample_project):
        """Test project sharing by non-owner"""
        # Arrange
        user_id = "collaborator-456"
        project_id = "project-789"
        share_data = {
            "collaborator_email": "other@example.com",
            "permissions": ["read"],
            "message": "Please collaborate"
        }
        
        with patch.object(ownership_service, '_get_user_by_id', return_value=sample_collaborator):
            with patch.object(ownership_service, '_get_project_by_id', return_value=sample_project):
                with patch.object(ownership_service, '_verify_ownership', return_value=False):
                    # Act
                    result = await ownership_service.share_project(user_id, project_id, share_data)
                    
                    # Assert
                    assert result["success"] is False
                    assert "Access denied" in result["error"]
    
    @pytest.mark.asyncio
    async def test_share_project_collaborator_not_found(self, ownership_service, sample_owner, sample_project):
        """Test project sharing with non-existent collaborator"""
        # Arrange
        owner_id = "owner-123"
        project_id = "project-789"
        share_data = {
            "collaborator_email": "nonexistent@example.com",
            "permissions": ["read"],
            "message": "Please collaborate"
        }
        
        with patch.object(ownership_service, '_get_user_by_id', return_value=sample_owner):
            with patch.object(ownership_service, '_get_project_by_id', return_value=sample_project):
                with patch.object(ownership_service, '_verify_ownership', return_value=True):
                    with patch.object(ownership_service, '_get_user_by_email', return_value=None):
                        # Act
                        result = await ownership_service.share_project(owner_id, project_id, share_data)
                        
                        # Assert
                        assert result["success"] is False
                        assert "Collaborator not found" in result["error"]
    
    @pytest.mark.asyncio
    async def test_revoke_project_access_success(self, ownership_service, sample_owner, sample_collaborator, sample_project):
        """Test successful project access revocation"""
        # Arrange
        owner_id = "owner-123"
        collaborator_id = "collaborator-456"
        project_id = "project-789"
        
        with patch.object(ownership_service, '_get_user_by_id', return_value=sample_owner):
            with patch.object(ownership_service, '_get_project_by_id', return_value=sample_project):
                with patch.object(ownership_service, '_verify_ownership', return_value=True):
                    with patch.object(ownership_service, '_revoke_project_access') as mock_revoke:
                        mock_revoke.return_value = True
                        
                        # Act
                        result = await ownership_service.revoke_project_access(owner_id, project_id, collaborator_id)
                        
                        # Assert
                        assert result["success"] is True
                        assert result["message"] == "Project access revoked successfully"
                        mock_revoke.assert_called_once_with(collaborator_id, project_id)
    
    @pytest.mark.asyncio
    async def test_revoke_project_access_not_owner(self, ownership_service, sample_collaborator, sample_project):
        """Test project access revocation by non-owner"""
        # Arrange
        user_id = "collaborator-456"
        project_id = "project-789"
        collaborator_id = "other-123"
        
        with patch.object(ownership_service, '_get_user_by_id', return_value=sample_collaborator):
            with patch.object(ownership_service, '_get_project_by_id', return_value=sample_project):
                with patch.object(ownership_service, '_verify_ownership', return_value=False):
                    # Act
                    result = await ownership_service.revoke_project_access(user_id, project_id, collaborator_id)
                    
                    # Assert
                    assert result["success"] is False
                    assert "Access denied" in result["error"]
    
    @pytest.mark.asyncio
    async def test_update_project_permissions_success(self, ownership_service, sample_owner, sample_collaborator, sample_project):
        """Test successful project permissions update"""
        # Arrange
        owner_id = "owner-123"
        collaborator_id = "collaborator-456"
        project_id = "project-789"
        permissions_data = {
            "permissions": ["read", "write", "delete"]
        }
        
        with patch.object(ownership_service, '_get_user_by_id', return_value=sample_owner):
            with patch.object(ownership_service, '_get_project_by_id', return_value=sample_project):
                with patch.object(ownership_service, '_verify_ownership', return_value=True):
                    with patch.object(ownership_service, '_update_user_project_permissions') as mock_update:
                        mock_update.return_value = True
                        
                        # Act
                        result = await ownership_service.update_project_permissions(owner_id, project_id, collaborator_id, permissions_data)
                        
                        # Assert
                        assert result["success"] is True
                        assert result["message"] == "Project permissions updated successfully"
                        mock_update.assert_called_once_with(collaborator_id, project_id, permissions_data["permissions"])
    
    @pytest.mark.asyncio
    async def test_update_project_permissions_not_owner(self, ownership_service, sample_collaborator, sample_project):
        """Test project permissions update by non-owner"""
        # Arrange
        user_id = "collaborator-456"
        project_id = "project-789"
        collaborator_id = "other-123"
        permissions_data = {
            "permissions": ["read"]
        }
        
        with patch.object(ownership_service, '_get_user_by_id', return_value=sample_collaborator):
            with patch.object(ownership_service, '_get_project_by_id', return_value=sample_project):
                with patch.object(ownership_service, '_verify_ownership', return_value=False):
                    # Act
                    result = await ownership_service.update_project_permissions(user_id, project_id, collaborator_id, permissions_data)
                    
                    # Assert
                    assert result["success"] is False
                    assert "Access denied" in result["error"]
    
    @pytest.mark.asyncio
    async def test_get_project_collaborators_success(self, ownership_service, sample_owner, sample_project):
        """Test successful retrieval of project collaborators"""
        # Arrange
        owner_id = "owner-123"
        project_id = "project-789"
        
        mock_collaborators = [
            {
                "user_id": "collaborator-456",
                "email": "collaborator@example.com",
                "permissions": ["read", "write"],
                "joined_at": "2024-01-15T10:30:00Z"
            }
        ]
        
        with patch.object(ownership_service, '_get_user_by_id', return_value=sample_owner):
            with patch.object(ownership_service, '_get_project_by_id', return_value=sample_project):
                with patch.object(ownership_service, '_verify_ownership', return_value=True):
                    with patch.object(ownership_service, '_get_project_collaborators') as mock_get:
                        mock_get.return_value = mock_collaborators
                        
                        # Act
                        result = await ownership_service.get_project_collaborators(owner_id, project_id)
                        
                        # Assert
                        assert result["success"] is True
                        assert len(result["data"]["collaborators"]) == 1
                        assert result["data"]["collaborators"][0]["user_id"] == "collaborator-456"
                        assert result["data"]["collaborators"][0]["permissions"] == ["read", "write"]
    
    @pytest.mark.asyncio
    async def test_get_project_collaborators_not_owner(self, ownership_service, sample_collaborator, sample_project):
        """Test get project collaborators by non-owner"""
        # Arrange
        user_id = "collaborator-456"
        project_id = "project-789"
        
        with patch.object(ownership_service, '_get_user_by_id', return_value=sample_collaborator):
            with patch.object(ownership_service, '_get_project_by_id', return_value=sample_project):
                with patch.object(ownership_service, '_verify_ownership', return_value=False):
                    # Act
                    result = await ownership_service.get_project_collaborators(user_id, project_id)
                    
                    # Assert
                    assert result["success"] is False
                    assert "Access denied" in result["error"]
    
    @pytest.mark.asyncio
    async def test_transfer_project_ownership_success(self, ownership_service, sample_owner, sample_collaborator, sample_project):
        """Test successful project ownership transfer"""
        # Arrange
        current_owner_id = "owner-123"
        new_owner_id = "collaborator-456"
        project_id = "project-789"
        transfer_data = {
            "new_owner_email": "collaborator@example.com",
            "confirm_transfer": True
        }
        
        with patch.object(ownership_service, '_get_user_by_id', return_value=sample_owner):
            with patch.object(ownership_service, '_get_project_by_id', return_value=sample_project):
                with patch.object(ownership_service, '_verify_ownership', return_value=True):
                    with patch.object(ownership_service, '_get_user_by_email', return_value=sample_collaborator):
                        with patch.object(ownership_service, '_transfer_ownership') as mock_transfer:
                            mock_transfer.return_value = True
                            
                            # Act
                            result = await ownership_service.transfer_project_ownership(current_owner_id, project_id, transfer_data)
                            
                            # Assert
                            assert result["success"] is True
                            assert result["message"] == "Project ownership transferred successfully"
                            mock_transfer.assert_called_once_with(project_id, new_owner_id)
    
    @pytest.mark.asyncio
    async def test_transfer_project_ownership_not_owner(self, ownership_service, sample_collaborator, sample_project):
        """Test project ownership transfer by non-owner"""
        # Arrange
        user_id = "collaborator-456"
        project_id = "project-789"
        transfer_data = {
            "new_owner_email": "other@example.com",
            "confirm_transfer": True
        }
        
        with patch.object(ownership_service, '_get_user_by_id', return_value=sample_collaborator):
            with patch.object(ownership_service, '_get_project_by_id', return_value=sample_project):
                with patch.object(ownership_service, '_verify_ownership', return_value=False):
                    # Act
                    result = await ownership_service.transfer_project_ownership(user_id, project_id, transfer_data)
                    
                    # Assert
                    assert result["success"] is False
                    assert "Access denied" in result["error"]
    
    @pytest.mark.asyncio
    async def test_transfer_project_ownership_new_owner_not_found(self, ownership_service, sample_owner, sample_project):
        """Test project ownership transfer to non-existent user"""
        # Arrange
        owner_id = "owner-123"
        project_id = "project-789"
        transfer_data = {
            "new_owner_email": "nonexistent@example.com",
            "confirm_transfer": True
        }
        
        with patch.object(ownership_service, '_get_user_by_id', return_value=sample_owner):
            with patch.object(ownership_service, '_get_project_by_id', return_value=sample_project):
                with patch.object(ownership_service, '_verify_ownership', return_value=True):
                    with patch.object(ownership_service, '_get_user_by_email', return_value=None):
                        # Act
                        result = await ownership_service.transfer_project_ownership(owner_id, project_id, transfer_data)
                        
                        # Assert
                        assert result["success"] is False
                        assert "New owner not found" in result["error"]
    
    @pytest.mark.asyncio
    async def test_leave_project_success(self, ownership_service, sample_collaborator, sample_project):
        """Test successful project leaving by collaborator"""
        # Arrange
        user_id = "collaborator-456"
        project_id = "project-789"
        
        with patch.object(ownership_service, '_get_user_by_id', return_value=sample_collaborator):
            with patch.object(ownership_service, '_get_project_by_id', return_value=sample_project):
                with patch.object(ownership_service, '_verify_ownership', return_value=False):
                    with patch.object(ownership_service, '_get_user_project_permissions', return_value=["read", "write"]):
                        with patch.object(ownership_service, '_revoke_project_access') as mock_revoke:
                            mock_revoke.return_value = True
                            
                            # Act
                            result = await ownership_service.leave_project(user_id, project_id)
                            
                            # Assert
                            assert result["success"] is True
                            assert result["message"] == "Left project successfully"
                            mock_revoke.assert_called_once_with(user_id, project_id)
    
    @pytest.mark.asyncio
    async def test_leave_project_owner_cannot_leave(self, ownership_service, sample_owner, sample_project):
        """Test project owner cannot leave their own project"""
        # Arrange
        user_id = "owner-123"
        project_id = "project-789"
        
        with patch.object(ownership_service, '_get_user_by_id', return_value=sample_owner):
            with patch.object(ownership_service, '_get_project_by_id', return_value=sample_project):
                with patch.object(ownership_service, '_verify_ownership', return_value=True):
                    # Act
                    result = await ownership_service.leave_project(user_id, project_id)
                    
                    # Assert
                    assert result["success"] is False
                    assert "Project owner cannot leave" in result["error"]

