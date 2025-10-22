"""
Pydantic schemas for MyAccount functionality
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, Dict, Any


class ProfileUpdateRequest(BaseModel):
    """Schema for profile update request"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    company: Optional[str] = Field(None, max_length=100)
    role: Optional[str] = Field(None, max_length=50)
    bio: Optional[str] = Field(None, max_length=500)
    
    @validator('first_name', 'last_name')
    def validate_names(cls, v):
        """Validate name fields"""
        if v is not None and v.strip() == "":
            raise ValueError('Name cannot be empty')
        return v


class PasswordChangeRequest(BaseModel):
    """Schema for password change request"""
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8)
    
    @validator('new_password')
    def validate_new_password(cls, v):
        """Validate new password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class EmailChangeRequest(BaseModel):
    """Schema for email change request"""
    new_email: EmailStr
    current_password: str = Field(..., min_length=1)


class NotificationSettingsRequest(BaseModel):
    """Schema for notification settings request"""
    email_notifications: Optional[bool] = None
    project_updates: Optional[bool] = None
    security_alerts: Optional[bool] = None
    marketing_emails: Optional[bool] = None


class PrivacySettingsRequest(BaseModel):
    """Schema for privacy settings request"""
    profile_visibility: Optional[str] = Field(None, pattern="^(public|private|friends)$")
    show_email: Optional[bool] = None
    show_company: Optional[bool] = None
    data_sharing: Optional[bool] = None


class AccountDeletionRequest(BaseModel):
    """Schema for account deletion request"""
    reason: str = Field(..., min_length=1, max_length=500)
    password: str = Field(..., min_length=1)


class ProfileResponse(BaseModel):
    """Schema for profile response"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    message: Optional[str] = None


class SettingsResponse(BaseModel):
    """Schema for settings response"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    message: Optional[str] = None


class StatisticsResponse(BaseModel):
    """Schema for statistics response"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class DataExportResponse(BaseModel):
    """Schema for data export response"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class AccountDeletionResponse(BaseModel):
    """Schema for account deletion response"""
    success: bool
    message: Optional[str] = None
    error: Optional[str] = None
