"""
Unit tests for Collaboration Service - TDD Implementation
Following Red-Green-Refactor cycle for team management, collaboration workflows, and shared project access
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from app.services.collaboration_service import CollaborationService
from app.models.user import User
from app.models.project import Project
from app.schemas.collaboration import (
    TeamCreateRequest, TeamInviteRequest, TeamJoinRequest, TeamLeaveRequest,
    CollaborationWorkflowRequest, SharedProjectAccessRequest, TeamRoleRequest,
    TeamResponse, CollaborationResponse, TeamInviteResponse, WorkflowResponse
)
from app.core.exceptions import CollaborationError, TeamError, WorkflowError


class TestCollaborationService:
    """Test cases for Collaboration Service - TDD Implementation"""
    
    @pytest.fixture
    def collaboration_service(self):
        """Create a test instance of CollaborationService"""
        return CollaborationService()
    
    @pytest.fixture
    def sample_team_owner(self):
        """Create a sample team owner"""
        return User(
            id="owner-123",
            email="owner@example.com",
            username="teamowner",
            first_name="Team",
            last_name="Owner",
            hashed_password="$2b$12$hashed_password",
            is_active=True,
            is_verified=True
        )
    
    @pytest.fixture
    def sample_team_member(self):
        """Create a sample team member"""
        return User(
            id="member-456",
            email="member@example.com",
            username="teammember",
            first_name="Team",
            last_name="Member",
            hashed_password="$2b$12$hashed_password",
            is_active=True,
            is_verified=True
        )
    
    @pytest.fixture
    def sample_project(self, sample_team_owner):
        """Create a sample project"""
        return Project(
            id="project-789",
            name="Team Project",
            description="A team collaboration project",
            domain="software",
            status="active",
            owner_id=sample_team_owner.id
        )

    # RED PHASE: Write failing tests first
    
    @pytest.mark.asyncio
    async def test_create_team_success(self, collaboration_service, sample_team_owner):
        """Test successful team creation"""
        # Arrange
        owner_id = "owner-123"
        team_data = {
            "name": "Development Team",
            "description": "A team for software development",
            "visibility": "private"
        }
        
        with patch.object(collaboration_service, '_get_user_by_id', return_value=sample_team_owner):
            with patch.object(collaboration_service, '_create_team') as mock_create:
                mock_team = {
                    "id": "team-123",
                    "name": "Development Team",
                    "description": "A team for software development",
                    "owner_id": owner_id,
                    "visibility": "private",
                    "created_at": "2024-01-15T10:30:00Z"
                }
                mock_create.return_value = mock_team
                
                # Act
                result = await collaboration_service.create_team(owner_id, team_data)
                
                # Assert
                assert result["success"] is True
                assert result["message"] == "Team created successfully"
                assert result["data"]["id"] == "team-123"
                assert result["data"]["name"] == "Development Team"
                assert result["data"]["owner_id"] == owner_id
                mock_create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_team_user_not_found(self, collaboration_service):
        """Test team creation by non-existent user"""
        # Arrange
        user_id = "nonexistent-user"
        team_data = {
            "name": "Test Team",
            "description": "A test team"
        }
        
        with patch.object(collaboration_service, '_get_user_by_id', return_value=None):
            # Act
            result = await collaboration_service.create_team(user_id, team_data)
            
            # Assert
            assert result["success"] is False
            assert "User not found" in result["error"]
    
    @pytest.mark.asyncio
    async def test_invite_user_to_team_success(self, collaboration_service, sample_team_owner, sample_team_member):
        """Test successful user invitation to team"""
        # Arrange
        owner_id = "owner-123"
        team_id = "team-123"
        invite_data = {
            "user_email": "member@example.com",
            "role": "member",
            "message": "Join our development team"
        }
        
        with patch.object(collaboration_service, '_get_user_by_id', return_value=sample_team_owner):
            with patch.object(collaboration_service, '_get_team_by_id', return_value={"id": team_id, "owner_id": owner_id, "name": "Test Team"}):
                with patch.object(collaboration_service, '_verify_team_ownership', return_value=True):
                    with patch.object(collaboration_service, '_get_user_by_email', return_value=sample_team_member):
                        with patch.object(collaboration_service, '_send_team_invite') as mock_send:
                            mock_send.return_value = True
                            
                            # Act
                            result = await collaboration_service.invite_user_to_team(owner_id, team_id, invite_data)
                            
                            # Assert
                            assert result["success"] is True
                            assert result["message"] == "Team invitation sent successfully"
                            mock_send.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_invite_user_to_team_not_owner(self, collaboration_service, sample_team_member):
        """Test team invitation by non-owner"""
        # Arrange
        user_id = "member-456"
        team_id = "team-123"
        invite_data = {
            "user_email": "other@example.com",
            "role": "member"
        }
        
        with patch.object(collaboration_service, '_get_user_by_id', return_value=sample_team_member):
            with patch.object(collaboration_service, '_get_team_by_id', return_value={"id": team_id, "owner_id": "owner-123"}):
                with patch.object(collaboration_service, '_verify_team_ownership', return_value=False):
                    # Act
                    result = await collaboration_service.invite_user_to_team(user_id, team_id, invite_data)
                    
                    # Assert
                    assert result["success"] is False
                    assert "Access denied" in result["error"]
    
    @pytest.mark.asyncio
    async def test_join_team_success(self, collaboration_service, sample_team_member):
        """Test successful team joining"""
        # Arrange
        user_id = "member-456"
        team_id = "team-123"
        join_data = {
            "invite_token": "valid_invite_token"
        }
        
        with patch.object(collaboration_service, '_get_user_by_id', return_value=sample_team_member):
            with patch.object(collaboration_service, '_validate_invite_token', return_value={"team_id": team_id, "role": "member"}):
                with patch.object(collaboration_service, '_add_user_to_team') as mock_add:
                    mock_add.return_value = True
                    
                    # Act
                    result = await collaboration_service.join_team(user_id, join_data)
                    
                    # Assert
                    assert result["success"] is True
                    assert result["message"] == "Successfully joined team"
                    mock_add.assert_called_once_with(user_id, team_id, "member")
    
    @pytest.mark.asyncio
    async def test_join_team_invalid_token(self, collaboration_service, sample_team_member):
        """Test team joining with invalid token"""
        # Arrange
        user_id = "member-456"
        join_data = {
            "invite_token": "invalid_token"
        }
        
        with patch.object(collaboration_service, '_get_user_by_id', return_value=sample_team_member):
            with patch.object(collaboration_service, '_validate_invite_token', return_value=None):
                # Act
                result = await collaboration_service.join_team(user_id, join_data)
                
                # Assert
                assert result["success"] is False
                assert "Invalid invitation token" in result["error"]
    
    @pytest.mark.asyncio
    async def test_leave_team_success(self, collaboration_service, sample_team_member):
        """Test successful team leaving"""
        # Arrange
        user_id = "member-456"
        team_id = "team-123"
        
        with patch.object(collaboration_service, '_get_user_by_id', return_value=sample_team_member):
            with patch.object(collaboration_service, '_get_team_by_id', return_value={"id": team_id, "owner_id": "owner-123"}):
                with patch.object(collaboration_service, '_verify_team_ownership', return_value=False):
                    with patch.object(collaboration_service, '_remove_user_from_team') as mock_remove:
                        mock_remove.return_value = True
                        
                        # Act
                        result = await collaboration_service.leave_team(user_id, team_id)
                        
                        # Assert
                        assert result["success"] is True
                        assert result["message"] == "Successfully left team"
                        mock_remove.assert_called_once_with(user_id, team_id)
    
    @pytest.mark.asyncio
    async def test_leave_team_owner_cannot_leave(self, collaboration_service, sample_team_owner):
        """Test team owner cannot leave their own team"""
        # Arrange
        user_id = "owner-123"
        team_id = "team-123"
        
        with patch.object(collaboration_service, '_get_user_by_id', return_value=sample_team_owner):
            with patch.object(collaboration_service, '_get_team_by_id', return_value={"id": team_id, "owner_id": user_id}):
                with patch.object(collaboration_service, '_verify_team_ownership', return_value=True):
                    # Act
                    result = await collaboration_service.leave_team(user_id, team_id)
                    
                    # Assert
                    assert result["success"] is False
                    assert "Team owner cannot leave" in result["error"]
    
    @pytest.mark.asyncio
    async def test_get_team_members_success(self, collaboration_service, sample_team_owner):
        """Test successful retrieval of team members"""
        # Arrange
        owner_id = "owner-123"
        team_id = "team-123"
        
        mock_members = [
            {
                "user_id": "owner-123",
                "email": "owner@example.com",
                "role": "owner",
                "joined_at": "2024-01-15T10:30:00Z"
            },
            {
                "user_id": "member-456",
                "email": "member@example.com",
                "role": "member",
                "joined_at": "2024-01-16T09:15:00Z"
            }
        ]
        
        with patch.object(collaboration_service, '_get_user_by_id', return_value=sample_team_owner):
            with patch.object(collaboration_service, '_get_team_by_id', return_value={"id": team_id, "owner_id": owner_id}):
                with patch.object(collaboration_service, '_verify_team_ownership', return_value=True):
                    with patch.object(collaboration_service, '_get_team_members') as mock_get:
                        mock_get.return_value = mock_members
                        
                        # Act
                        result = await collaboration_service.get_team_members(owner_id, team_id)
                        
                        # Assert
                        assert result["success"] is True
                        assert len(result["data"]["members"]) == 2
                        assert result["data"]["members"][0]["role"] == "owner"
                        assert result["data"]["members"][1]["role"] == "member"
    
    @pytest.mark.asyncio
    async def test_get_team_members_not_owner(self, collaboration_service, sample_team_member):
        """Test get team members by non-owner"""
        # Arrange
        user_id = "member-456"
        team_id = "team-123"
        
        with patch.object(collaboration_service, '_get_user_by_id', return_value=sample_team_member):
            with patch.object(collaboration_service, '_get_team_by_id', return_value={"id": team_id, "owner_id": "owner-123"}):
                with patch.object(collaboration_service, '_verify_team_ownership', return_value=False):
                    # Act
                    result = await collaboration_service.get_team_members(user_id, team_id)
                    
                    # Assert
                    assert result["success"] is False
                    assert "Access denied" in result["error"]
    
    @pytest.mark.asyncio
    async def test_update_team_member_role_success(self, collaboration_service, sample_team_owner, sample_team_member):
        """Test successful team member role update"""
        # Arrange
        owner_id = "owner-123"
        team_id = "team-123"
        member_id = "member-456"
        role_data = {
            "role": "admin"
        }
        
        with patch.object(collaboration_service, '_get_user_by_id', return_value=sample_team_owner):
            with patch.object(collaboration_service, '_get_team_by_id', return_value={"id": team_id, "owner_id": owner_id}):
                with patch.object(collaboration_service, '_verify_team_ownership', return_value=True):
                    with patch.object(collaboration_service, '_update_team_member_role') as mock_update:
                        mock_update.return_value = True
                        
                        # Act
                        result = await collaboration_service.update_team_member_role(owner_id, team_id, member_id, role_data)
                        
                        # Assert
                        assert result["success"] is True
                        assert result["message"] == "Team member role updated successfully"
                        mock_update.assert_called_once_with(member_id, team_id, "admin")
    
    @pytest.mark.asyncio
    async def test_update_team_member_role_not_owner(self, collaboration_service, sample_team_member):
        """Test team member role update by non-owner"""
        # Arrange
        user_id = "member-456"
        team_id = "team-123"
        member_id = "other-789"
        role_data = {
            "role": "admin"
        }
        
        with patch.object(collaboration_service, '_get_user_by_id', return_value=sample_team_member):
            with patch.object(collaboration_service, '_get_team_by_id', return_value={"id": team_id, "owner_id": "owner-123"}):
                with patch.object(collaboration_service, '_verify_team_ownership', return_value=False):
                    # Act
                    result = await collaboration_service.update_team_member_role(user_id, team_id, member_id, role_data)
                    
                    # Assert
                    assert result["success"] is False
                    assert "Access denied" in result["error"]
    
    @pytest.mark.asyncio
    async def test_create_collaboration_workflow_success(self, collaboration_service, sample_team_owner, sample_project):
        """Test successful collaboration workflow creation"""
        # Arrange
        owner_id = "owner-123"
        team_id = "team-123"
        project_id = "project-789"
        workflow_data = {
            "name": "Code Review Workflow",
            "description": "Automated code review process",
            "steps": [
                {"name": "Create PR", "assignee": "developer"},
                {"name": "Review Code", "assignee": "reviewer"},
                {"name": "Merge", "assignee": "admin"}
            ]
        }
        
        with patch.object(collaboration_service, '_get_user_by_id', return_value=sample_team_owner):
            with patch.object(collaboration_service, '_get_team_by_id', return_value={"id": team_id, "owner_id": owner_id}):
                with patch.object(collaboration_service, '_verify_team_ownership', return_value=True):
                    with patch.object(collaboration_service, '_get_project_by_id', return_value=sample_project):
                        with patch.object(collaboration_service, '_create_workflow') as mock_create:
                            mock_workflow = {
                                "id": "workflow-123",
                                "name": "Code Review Workflow",
                                "team_id": team_id,
                                "project_id": project_id,
                                "created_at": "2024-01-15T10:30:00Z"
                            }
                            mock_create.return_value = mock_workflow
                            
                            # Act
                            result = await collaboration_service.create_collaboration_workflow(owner_id, team_id, project_id, workflow_data)
                            
                            # Assert
                            assert result["success"] is True
                            assert result["message"] == "Collaboration workflow created successfully"
                            assert result["data"]["id"] == "workflow-123"
                            mock_create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_collaboration_workflow_not_owner(self, collaboration_service, sample_team_member, sample_project):
        """Test collaboration workflow creation by non-owner"""
        # Arrange
        user_id = "member-456"
        team_id = "team-123"
        project_id = "project-789"
        workflow_data = {
            "name": "Test Workflow",
            "description": "A test workflow"
        }
        
        with patch.object(collaboration_service, '_get_user_by_id', return_value=sample_team_member):
            with patch.object(collaboration_service, '_get_team_by_id', return_value={"id": team_id, "owner_id": "owner-123"}):
                with patch.object(collaboration_service, '_verify_team_ownership', return_value=False):
                    # Act
                    result = await collaboration_service.create_collaboration_workflow(user_id, team_id, project_id, workflow_data)
                    
                    # Assert
                    assert result["success"] is False
                    assert "Access denied" in result["error"]
    
    @pytest.mark.asyncio
    async def test_assign_shared_project_access_success(self, collaboration_service, sample_team_owner, sample_project):
        """Test successful shared project access assignment"""
        # Arrange
        owner_id = "owner-123"
        team_id = "team-123"
        project_id = "project-789"
        access_data = {
            "permissions": ["read", "write"],
            "expires_at": "2024-12-31T23:59:59Z"
        }
        
        with patch.object(collaboration_service, '_get_user_by_id', return_value=sample_team_owner):
            with patch.object(collaboration_service, '_get_team_by_id', return_value={"id": team_id, "owner_id": owner_id}):
                with patch.object(collaboration_service, '_verify_team_ownership', return_value=True):
                    with patch.object(collaboration_service, '_get_project_by_id', return_value=sample_project):
                        with patch.object(collaboration_service, '_assign_team_project_access') as mock_assign:
                            mock_assign.return_value = True
                            
                            # Act
                            result = await collaboration_service.assign_shared_project_access(owner_id, team_id, project_id, access_data)
                            
                            # Assert
                            assert result["success"] is True
                            assert result["message"] == "Shared project access assigned successfully"
                            mock_assign.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_assign_shared_project_access_not_owner(self, collaboration_service, sample_team_member, sample_project):
        """Test shared project access assignment by non-owner"""
        # Arrange
        user_id = "member-456"
        team_id = "team-123"
        project_id = "project-789"
        access_data = {
            "permissions": ["read"]
        }
        
        with patch.object(collaboration_service, '_get_user_by_id', return_value=sample_team_member):
            with patch.object(collaboration_service, '_get_team_by_id', return_value={"id": team_id, "owner_id": "owner-123"}):
                with patch.object(collaboration_service, '_verify_team_ownership', return_value=False):
                    # Act
                    result = await collaboration_service.assign_shared_project_access(user_id, team_id, project_id, access_data)
                    
                    # Assert
                    assert result["success"] is False
                    assert "Access denied" in result["error"]
    
    @pytest.mark.asyncio
    async def test_get_team_collaboration_activities_success(self, collaboration_service, sample_team_owner):
        """Test successful retrieval of team collaboration activities"""
        # Arrange
        owner_id = "owner-123"
        team_id = "team-123"
        
        mock_activities = [
            {
                "id": "activity-1",
                "type": "project_created",
                "user_id": "owner-123",
                "description": "Created new project",
                "timestamp": "2024-01-15T10:30:00Z"
            },
            {
                "id": "activity-2",
                "type": "member_joined",
                "user_id": "member-456",
                "description": "Joined the team",
                "timestamp": "2024-01-16T09:15:00Z"
            }
        ]
        
        with patch.object(collaboration_service, '_get_user_by_id', return_value=sample_team_owner):
            with patch.object(collaboration_service, '_get_team_by_id', return_value={"id": team_id, "owner_id": owner_id}):
                with patch.object(collaboration_service, '_verify_team_ownership', return_value=True):
                    with patch.object(collaboration_service, '_get_team_activities') as mock_get:
                        mock_get.return_value = mock_activities
                        
                        # Act
                        result = await collaboration_service.get_team_collaboration_activities(owner_id, team_id)
                        
                        # Assert
                        assert result["success"] is True
                        assert len(result["data"]["activities"]) == 2
                        assert result["data"]["activities"][0]["type"] == "project_created"
                        assert result["data"]["activities"][1]["type"] == "member_joined"
    
    @pytest.mark.asyncio
    async def test_get_team_collaboration_activities_not_owner(self, collaboration_service, sample_team_member):
        """Test get team collaboration activities by non-owner"""
        # Arrange
        user_id = "member-456"
        team_id = "team-123"
        
        with patch.object(collaboration_service, '_get_user_by_id', return_value=sample_team_member):
            with patch.object(collaboration_service, '_get_team_by_id', return_value={"id": team_id, "owner_id": "owner-123"}):
                with patch.object(collaboration_service, '_verify_team_ownership', return_value=False):
                    # Act
                    result = await collaboration_service.get_team_collaboration_activities(user_id, team_id)
                    
                    # Assert
                    assert result["success"] is False
                    assert "Access denied" in result["error"]
    
    @pytest.mark.asyncio
    async def test_get_user_teams_success(self, collaboration_service, sample_team_member):
        """Test successful retrieval of user's teams"""
        # Arrange
        user_id = "member-456"
        
        mock_teams = [
            {
                "id": "team-123",
                "name": "Development Team",
                "role": "member",
                "joined_at": "2024-01-16T09:15:00Z"
            },
            {
                "id": "team-456",
                "name": "Design Team",
                "role": "admin",
                "joined_at": "2024-01-17T14:20:00Z"
            }
        ]
        
        with patch.object(collaboration_service, '_get_user_by_id', return_value=sample_team_member):
            with patch.object(collaboration_service, '_get_user_teams') as mock_get:
                mock_get.return_value = mock_teams
                
                # Act
                result = await collaboration_service.get_user_teams(user_id)
                
                # Assert
                assert result["success"] is True
                assert len(result["data"]["teams"]) == 2
                assert result["data"]["teams"][0]["role"] == "member"
                assert result["data"]["teams"][1]["role"] == "admin"
    
    @pytest.mark.asyncio
    async def test_get_user_teams_user_not_found(self, collaboration_service):
        """Test get user teams for non-existent user"""
        # Arrange
        user_id = "nonexistent-user"
        
        with patch.object(collaboration_service, '_get_user_by_id', return_value=None):
            # Act
            result = await collaboration_service.get_user_teams(user_id)
            
            # Assert
            assert result["success"] is False
            assert "User not found" in result["error"]
