"""
Project Ownership Service for ArchMesh
TDD Implementation - GREEN phase: Minimal implementation to make tests pass
"""

from typing import Dict, Any, Optional, List
from app.models.user import User
from app.models.project import Project
from app.core.exceptions import ProjectAccessError, OwnershipError, PermissionError


class ProjectOwnershipService:
    """Service for handling project ownership and access control"""
    
    def __init__(self):
        """Initialize Project Ownership service"""
        pass
    
    async def get_user_projects(self, user_id: str) -> Dict[str, Any]:
        """Get all projects owned by a user"""
        try:
            # Get user by ID
            user = await self._get_user_by_id(user_id)
            if not user:
                return {
                    "success": False,
                    "error": "User not found"
                }
            
            # Get user's projects
            projects = await self._get_user_projects(user_id)
            
            return {
                "success": True,
                "data": {
                    "owner_id": user_id,
                    "projects": [
                        {
                            "id": str(project.id),
                            "name": project.name,
                            "description": project.description,
                            "domain": project.domain,
                            "status": project.status,
                            "created_at": project.created_at.isoformat() if project.created_at else None
                        }
                        for project in projects
                    ]
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get user projects: {str(e)}"
            }
    
    async def check_project_access(self, user_id: str, project_id: str) -> Dict[str, Any]:
        """Check if user has access to a project"""
        try:
            # Get user by ID
            user = await self._get_user_by_id(user_id)
            if not user:
                return {
                    "success": False,
                    "error": "User not found"
                }
            
            # Get project by ID
            project = await self._get_project_by_id(project_id)
            if not project:
                return {
                    "success": False,
                    "error": "Project not found"
                }
            
            # Check if user is owner
            if str(project.owner_id) == user_id:
                return {
                    "success": True,
                    "data": {
                        "has_access": True,
                        "access_level": "owner",
                        "permissions": ["read", "write", "delete", "share"]
                    }
                }
            
            # Check if user is collaborator
            permissions = await self._get_user_project_permissions(user_id, project_id)
            if permissions:
                return {
                    "success": True,
                    "data": {
                        "has_access": True,
                        "access_level": "collaborator",
                        "permissions": permissions
                    }
                }
            
            # No access
            return {
                "success": True,
                "data": {
                    "has_access": False,
                    "access_level": "none",
                    "permissions": []
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to check project access: {str(e)}"
            }
    
    async def share_project(self, owner_id: str, project_id: str, share_data: Dict[str, Any]) -> Dict[str, Any]:
        """Share project with another user"""
        try:
            # Get owner by ID
            owner = await self._get_user_by_id(owner_id)
            if not owner:
                return {
                    "success": False,
                    "error": "User not found"
                }
            
            # Get project by ID
            project = await self._get_project_by_id(project_id)
            if not project:
                return {
                    "success": False,
                    "error": "Project not found"
                }
            
            # Verify ownership
            if not await self._verify_ownership(owner_id, project_id):
                return {
                    "success": False,
                    "error": "Access denied"
                }
            
            # Get collaborator by email
            collaborator = await self._get_user_by_email(share_data["collaborator_email"])
            if not collaborator:
                return {
                    "success": False,
                    "error": "Collaborator not found"
                }
            
            # Grant project access
            await self._grant_project_access(collaborator.id, project_id, share_data["permissions"])
            
            # Send collaboration invite
            await self._send_collaboration_invite(collaborator.email, project.name, share_data.get("message", ""))
            
            return {
                "success": True,
                "message": "Project shared successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to share project: {str(e)}"
            }
    
    async def revoke_project_access(self, owner_id: str, project_id: str, collaborator_id: str) -> Dict[str, Any]:
        """Revoke project access for a collaborator"""
        try:
            # Get owner by ID
            owner = await self._get_user_by_id(owner_id)
            if not owner:
                return {
                    "success": False,
                    "error": "User not found"
                }
            
            # Get project by ID
            project = await self._get_project_by_id(project_id)
            if not project:
                return {
                    "success": False,
                    "error": "Project not found"
                }
            
            # Verify ownership
            if not await self._verify_ownership(owner_id, project_id):
                return {
                    "success": False,
                    "error": "Access denied"
                }
            
            # Revoke project access
            await self._revoke_project_access(collaborator_id, project_id)
            
            return {
                "success": True,
                "message": "Project access revoked successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to revoke project access: {str(e)}"
            }
    
    async def update_project_permissions(self, owner_id: str, project_id: str, collaborator_id: str, permissions_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update project permissions for a collaborator"""
        try:
            # Get owner by ID
            owner = await self._get_user_by_id(owner_id)
            if not owner:
                return {
                    "success": False,
                    "error": "User not found"
                }
            
            # Get project by ID
            project = await self._get_project_by_id(project_id)
            if not project:
                return {
                    "success": False,
                    "error": "Project not found"
                }
            
            # Verify ownership
            if not await self._verify_ownership(owner_id, project_id):
                return {
                    "success": False,
                    "error": "Access denied"
                }
            
            # Update permissions
            await self._update_user_project_permissions(collaborator_id, project_id, permissions_data["permissions"])
            
            return {
                "success": True,
                "message": "Project permissions updated successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to update project permissions: {str(e)}"
            }
    
    async def get_project_collaborators(self, owner_id: str, project_id: str) -> Dict[str, Any]:
        """Get all collaborators for a project"""
        try:
            # Get owner by ID
            owner = await self._get_user_by_id(owner_id)
            if not owner:
                return {
                    "success": False,
                    "error": "User not found"
                }
            
            # Get project by ID
            project = await self._get_project_by_id(project_id)
            if not project:
                return {
                    "success": False,
                    "error": "Project not found"
                }
            
            # Verify ownership
            if not await self._verify_ownership(owner_id, project_id):
                return {
                    "success": False,
                    "error": "Access denied"
                }
            
            # Get collaborators
            collaborators = await self._get_project_collaborators(project_id)
            
            return {
                "success": True,
                "data": {
                    "project_id": project_id,
                    "collaborators": collaborators
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get project collaborators: {str(e)}"
            }
    
    async def transfer_project_ownership(self, current_owner_id: str, project_id: str, transfer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transfer project ownership to another user"""
        try:
            # Get current owner by ID
            current_owner = await self._get_user_by_id(current_owner_id)
            if not current_owner:
                return {
                    "success": False,
                    "error": "User not found"
                }
            
            # Get project by ID
            project = await self._get_project_by_id(project_id)
            if not project:
                return {
                    "success": False,
                    "error": "Project not found"
                }
            
            # Verify ownership
            if not await self._verify_ownership(current_owner_id, project_id):
                return {
                    "success": False,
                    "error": "Access denied"
                }
            
            # Get new owner by email
            new_owner = await self._get_user_by_email(transfer_data["new_owner_email"])
            if not new_owner:
                return {
                    "success": False,
                    "error": "New owner not found"
                }
            
            # Transfer ownership
            await self._transfer_ownership(project_id, new_owner.id)
            
            return {
                "success": True,
                "message": "Project ownership transferred successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to transfer project ownership: {str(e)}"
            }
    
    async def leave_project(self, user_id: str, project_id: str) -> Dict[str, Any]:
        """Leave a project (for collaborators only)"""
        try:
            # Get user by ID
            user = await self._get_user_by_id(user_id)
            if not user:
                return {
                    "success": False,
                    "error": "User not found"
                }
            
            # Get project by ID
            project = await self._get_project_by_id(project_id)
            if not project:
                return {
                    "success": False,
                    "error": "Project not found"
                }
            
            # Check if user is owner
            if await self._verify_ownership(user_id, project_id):
                return {
                    "success": False,
                    "error": "Project owner cannot leave"
                }
            
            # Check if user is collaborator
            permissions = await self._get_user_project_permissions(user_id, project_id)
            if not permissions:
                return {
                    "success": False,
                    "error": "User is not a collaborator"
                }
            
            # Revoke access
            await self._revoke_project_access(user_id, project_id)
            
            return {
                "success": True,
                "message": "Left project successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to leave project: {str(e)}"
            }
    
    # Helper methods (Mock implementations for testing)
    
    async def _get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        # This is a mock implementation for testing
        return None
    
    async def _get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        # This is a mock implementation for testing
        return None
    
    async def _get_project_by_id(self, project_id: str) -> Optional[Project]:
        """Get project by ID"""
        # This is a mock implementation for testing
        return None
    
    async def _get_user_projects(self, user_id: str) -> List[Project]:
        """Get all projects owned by user"""
        # This is a mock implementation for testing
        return []
    
    async def _verify_ownership(self, user_id: str, project_id: str) -> bool:
        """Verify if user owns the project"""
        # This is a mock implementation for testing
        return False
    
    async def _get_user_project_permissions(self, user_id: str, project_id: str) -> List[str]:
        """Get user permissions for a project"""
        # This is a mock implementation for testing
        return []
    
    async def _grant_project_access(self, user_id: str, project_id: str, permissions: List[str]) -> bool:
        """Grant project access to user"""
        # This is a mock implementation for testing
        return True
    
    async def _revoke_project_access(self, user_id: str, project_id: str) -> bool:
        """Revoke project access for user"""
        # This is a mock implementation for testing
        return True
    
    async def _update_user_project_permissions(self, user_id: str, project_id: str, permissions: List[str]) -> bool:
        """Update user project permissions"""
        # This is a mock implementation for testing
        return True
    
    async def _get_project_collaborators(self, project_id: str) -> List[Dict[str, Any]]:
        """Get project collaborators"""
        # This is a mock implementation for testing
        return []
    
    async def _transfer_ownership(self, project_id: str, new_owner_id: str) -> bool:
        """Transfer project ownership"""
        # This is a mock implementation for testing
        return True
    
    async def _send_collaboration_invite(self, email: str, project_name: str, message: str) -> bool:
        """Send collaboration invite email"""
        # This is a mock implementation for testing
        return True

