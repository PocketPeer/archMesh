"""
Pydantic schemas for collaboration and team management
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime


class TeamCreateRequest(BaseModel):
    """Schema for team creation request"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    visibility: str = Field("private", pattern="^(public|private)$")
    
    @validator('name')
    def validate_name(cls, v):
        """Validate team name"""
        if not v.strip():
            raise ValueError('Team name cannot be empty')
        return v.strip()


class TeamInviteRequest(BaseModel):
    """Schema for team invitation request"""
    user_email: EmailStr
    role: str = Field(..., pattern="^(member|admin)$")
    message: Optional[str] = Field(None, max_length=500)


class TeamJoinRequest(BaseModel):
    """Schema for team join request"""
    invite_token: str = Field(..., min_length=1)


class TeamLeaveRequest(BaseModel):
    """Schema for team leave request"""
    team_id: str = Field(..., min_length=1)


class TeamRoleRequest(BaseModel):
    """Schema for team role update request"""
    role: str = Field(..., pattern="^(member|admin)$")


class CollaborationWorkflowRequest(BaseModel):
    """Schema for collaboration workflow request"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    steps: List[Dict[str, Any]] = Field(..., min_items=1)
    
    @validator('steps')
    def validate_steps(cls, v):
        """Validate workflow steps"""
        for step in v:
            if not step.get('name'):
                raise ValueError('Each step must have a name')
            if not step.get('assignee'):
                raise ValueError('Each step must have an assignee')
        return v


class SharedProjectAccessRequest(BaseModel):
    """Schema for shared project access request"""
    permissions: List[str] = Field(..., min_items=1)
    expires_at: Optional[datetime] = None
    
    @validator('permissions')
    def validate_permissions(cls, v):
        """Validate permissions"""
        valid_permissions = ["read", "write", "delete", "share"]
        for permission in v:
            if permission not in valid_permissions:
                raise ValueError(f'Invalid permission: {permission}')
        return v


class TeamResponse(BaseModel):
    """Schema for team response"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    message: Optional[str] = None


class CollaborationResponse(BaseModel):
    """Schema for collaboration response"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    message: Optional[str] = None


class TeamInviteResponse(BaseModel):
    """Schema for team invite response"""
    success: bool
    message: Optional[str] = None
    error: Optional[str] = None


class WorkflowResponse(BaseModel):
    """Schema for workflow response"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    message: Optional[str] = None


class TeamMemberInfo(BaseModel):
    """Schema for team member information"""
    user_id: str
    email: str
    role: str
    joined_at: str


class TeamInfo(BaseModel):
    """Schema for team information"""
    id: str
    name: str
    description: Optional[str]
    role: str
    joined_at: str


class CollaborationActivity(BaseModel):
    """Schema for collaboration activity"""
    id: str
    type: str
    user_id: str
    description: str
    timestamp: str


class TeamMembersResponse(BaseModel):
    """Schema for team members response"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class UserTeamsResponse(BaseModel):
    """Schema for user teams response"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class TeamActivitiesResponse(BaseModel):
    """Schema for team activities response"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
