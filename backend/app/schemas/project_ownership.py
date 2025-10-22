"""
Pydantic schemas for project ownership and access control
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any


class ProjectAccessRequest(BaseModel):
    """Schema for project access request"""
    project_id: str = Field(..., min_length=1)
    user_id: str = Field(..., min_length=1)


class ProjectShareRequest(BaseModel):
    """Schema for project sharing request"""
    collaborator_email: EmailStr
    permissions: List[str] = Field(..., min_items=1)
    message: Optional[str] = Field(None, max_length=500)
    
    @validator('permissions')
    def validate_permissions(cls, v):
        """Validate permissions"""
        valid_permissions = ["read", "write", "delete", "share"]
        for permission in v:
            if permission not in valid_permissions:
                raise ValueError(f'Invalid permission: {permission}')
        return v


class ProjectPermissionRequest(BaseModel):
    """Schema for project permission request"""
    collaborator_id: str = Field(..., min_length=1)
    permissions: List[str] = Field(..., min_items=1)
    
    @validator('permissions')
    def validate_permissions(cls, v):
        """Validate permissions"""
        valid_permissions = ["read", "write", "delete", "share"]
        for permission in v:
            if permission not in valid_permissions:
                raise ValueError(f'Invalid permission: {permission}')
        return v


class ProjectOwnershipTransferRequest(BaseModel):
    """Schema for project ownership transfer request"""
    new_owner_email: EmailStr
    confirm_transfer: bool = Field(..., description="Must be True to confirm transfer")


class ProjectOwnershipResponse(BaseModel):
    """Schema for project ownership response"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    message: Optional[str] = None


class ProjectAccessResponse(BaseModel):
    """Schema for project access response"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class ProjectShareResponse(BaseModel):
    """Schema for project share response"""
    success: bool
    message: Optional[str] = None
    error: Optional[str] = None


class ProjectCollaboratorInfo(BaseModel):
    """Schema for project collaborator information"""
    user_id: str
    email: str
    permissions: List[str]
    joined_at: str


class ProjectCollaboratorsResponse(BaseModel):
    """Schema for project collaborators response"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class ProjectLeaveRequest(BaseModel):
    """Schema for project leave request"""
    project_id: str = Field(..., min_length=1)


class ProjectLeaveResponse(BaseModel):
    """Schema for project leave response"""
    success: bool
    message: Optional[str] = None
    error: Optional[str] = None

