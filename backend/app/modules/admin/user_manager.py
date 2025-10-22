"""
User Manager - Handles user management and permissions
"""

import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from loguru import logger

from .models import UserConfig, UserRole


class UserManager:
    """
    Manages users, permissions, and access control.
    
    Responsibilities:
    - User creation and management
    - Role-based access control
    - Usage limits and quotas
    - API key management
    """
    
    def __init__(self):
        self.users: List[UserConfig] = []
        self._initialize_default_users()
    
    def _initialize_default_users(self):
        """Initialize default users"""
        # Create default admin user
        admin_user = UserConfig(
            id=str(uuid.uuid4()),
            email="admin@archmesh.com",
            name="System Administrator",
            role=UserRole.ADMIN,
            is_active=True,
            usage_limit=None,  # No limit for admin
            cost_limit=None
        )
        
        # Create default regular user
        regular_user = UserConfig(
            id=str(uuid.uuid4()),
            email="user@archmesh.com",
            name="Regular User",
            role=UserRole.USER,
            is_active=True,
            usage_limit=100,  # 100 requests per day
            cost_limit=10.0  # $10 per day
        )
        
        self.users = [admin_user, regular_user]
        logger.info(f"Initialized {len(self.users)} default users")
    
    def create_user(self, email: str, name: str, role: UserRole = UserRole.USER, 
                   usage_limit: Optional[int] = None, cost_limit: Optional[float] = None) -> Optional[UserConfig]:
        """Create a new user"""
        # Check if user already exists
        if self.get_user_by_email(email):
            logger.warning(f"User with email {email} already exists")
            return None
        
        user = UserConfig(
            id=str(uuid.uuid4()),
            email=email,
            name=name,
            role=role,
            is_active=True,
            usage_limit=usage_limit,
            cost_limit=cost_limit,
            api_key=self._generate_api_key()
        )
        
        self.users.append(user)
        logger.info(f"Created user {name} with role {role}")
        return user
    
    def get_user_by_id(self, user_id: str) -> Optional[UserConfig]:
        """Get user by ID"""
        for user in self.users:
            if user.id == user_id:
                return user
        return None
    
    def get_user_by_email(self, email: str) -> Optional[UserConfig]:
        """Get user by email"""
        for user in self.users:
            if user.email == email:
                return user
        return None
    
    def get_user_by_api_key(self, api_key: str) -> Optional[UserConfig]:
        """Get user by API key"""
        for user in self.users:
            if user.api_key == api_key:
                return user
        return None
    
    def get_all_users(self) -> List[UserConfig]:
        """Get all users"""
        return self.users.copy()
    
    def get_active_users(self) -> List[UserConfig]:
        """Get all active users"""
        return [user for user in self.users if user.is_active]
    
    def get_users_by_role(self, role: UserRole) -> List[UserConfig]:
        """Get users by role"""
        return [user for user in self.users if user.role == role and user.is_active]
    
    def update_user(self, user_id: str, **updates) -> bool:
        """Update user information"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        # Update allowed fields
        allowed_fields = ['name', 'role', 'is_active', 'usage_limit', 'cost_limit']
        for field, value in updates.items():
            if field in allowed_fields and hasattr(user, field):
                setattr(user, field, value)
        
        user.updated_at = datetime.now()
        logger.info(f"Updated user {user.name}")
        return True
    
    def delete_user(self, user_id: str) -> bool:
        """Delete a user (soft delete by setting inactive)"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        # Don't allow deleting admin users
        if user.role == UserRole.ADMIN:
            logger.warning("Cannot delete admin users")
            return False
        
        user.is_active = False
        user.updated_at = datetime.now()
        logger.info(f"Deactivated user {user.name}")
        return True
    
    def regenerate_api_key(self, user_id: str) -> Optional[str]:
        """Regenerate API key for a user"""
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        
        new_api_key = self._generate_api_key()
        user.api_key = new_api_key
        user.updated_at = datetime.now()
        
        logger.info(f"Regenerated API key for user {user.name}")
        return new_api_key
    
    def check_permission(self, user_id: str, permission: str) -> bool:
        """Check if user has a specific permission"""
        user = self.get_user_by_id(user_id)
        if not user or not user.is_active:
            return False
        
        # Admin has all permissions
        if user.role == UserRole.ADMIN:
            return True
        
        # Define role-based permissions
        permissions = {
            UserRole.ADMIN: ["read", "write", "delete", "admin", "manage_users", "manage_models"],
            UserRole.USER: ["read", "write", "create_projects", "run_workflows"],
            UserRole.VIEWER: ["read", "view_projects"]
        }
        
        user_permissions = permissions.get(user.role, [])
        return permission in user_permissions
    
    def check_usage_limits(self, user_id: str, request_cost: float = 0.0) -> Dict[str, Any]:
        """Check if user is within usage limits"""
        user = self.get_user_by_id(user_id)
        if not user or not user.is_active:
            return {"allowed": False, "reason": "User not found or inactive"}
        
        # Check usage limit (requests per day)
        if user.usage_limit is not None:
            # This would need to be integrated with actual usage tracking
            # For now, we'll assume the user is within limits
            pass
        
        # Check cost limit
        if user.cost_limit is not None and request_cost > user.cost_limit:
            return {
                "allowed": False, 
                "reason": f"Request cost ${request_cost:.2f} exceeds daily limit ${user.cost_limit:.2f}"
            }
        
        return {"allowed": True, "reason": "Within limits"}
    
    def _generate_api_key(self) -> str:
        """Generate a secure API key"""
        return f"ak_{uuid.uuid4().hex[:32]}"
    
    def get_user_statistics(self) -> Dict[str, Any]:
        """Get user statistics"""
        total_users = len(self.users)
        active_users = len(self.get_active_users())
        admin_users = len(self.get_users_by_role(UserRole.ADMIN))
        regular_users = len(self.get_users_by_role(UserRole.USER))
        viewer_users = len(self.get_users_by_role(UserRole.VIEWER))
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "inactive_users": total_users - active_users,
            "admin_users": admin_users,
            "regular_users": regular_users,
            "viewer_users": viewer_users,
            "users_with_limits": len([u for u in self.users if u.usage_limit is not None or u.cost_limit is not None])
        }
    
    def export_user_data(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Export user data (for GDPR compliance)"""
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        
        return {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "role": user.role.value,
            "is_active": user.is_active,
            "usage_limit": user.usage_limit,
            "cost_limit": user.cost_limit,
            "created_at": user.created_at.isoformat(),
            "updated_at": user.updated_at.isoformat()
        }
