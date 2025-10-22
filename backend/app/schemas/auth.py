"""
Authentication schemas for ArchMesh
Pydantic models for authentication requests and responses
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime


class LoginRequest(BaseModel):
    """Schema for user login request"""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=6, description="User password")


class RegisterRequest(BaseModel):
    """Schema for user registration request"""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password")
    name: str = Field(..., min_length=2, max_length=100, description="User full name")
    
    @validator('password')
    def validate_password(cls, v):
        """Validate password strength"""
        # bcrypt has a 72-byte limit; bcrypt_sha256 mitigates this, but we still
        # enforce a maximum to give clear feedback and avoid accidental truncation
        if len(v.encode('utf-8')) > 256:
            raise ValueError('Password must be at most 256 bytes')
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class TokenResponse(BaseModel):
    """Schema for token response"""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(default=3600, description="Token expiration time in seconds")


class UserResponse(BaseModel):
    """Schema for user response"""
    id: str = Field(..., description="User ID")
    email: str = Field(..., description="User email")
    name: Optional[str] = Field(None, description="User name")
    is_active: bool = Field(..., description="Whether user account is active")
    is_verified: bool = Field(..., description="Whether user email is verified")
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class LoginResponse(BaseModel):
    """Schema for login response"""
    success: bool = Field(..., description="Whether login was successful")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")
    error: Optional[str] = Field(None, description="Error message if login failed")


class RegisterResponse(BaseModel):
    """Schema for registration response"""
    success: bool = Field(..., description="Whether registration was successful")
    data: Optional[UserResponse] = Field(None, description="User data if registration successful")
    error: Optional[str] = Field(None, description="Error message if registration failed")


class RefreshTokenRequest(BaseModel):
    """Schema for refresh token request"""
    refresh_token: str = Field(..., description="Refresh token")


class ChangePasswordRequest(BaseModel):
    """Schema for change password request"""
    old_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")
    
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


class ResetPasswordRequest(BaseModel):
    """Schema for password reset request"""
    email: EmailStr = Field(..., description="User email address")


class ResetPasswordConfirmRequest(BaseModel):
    """Schema for password reset confirmation"""
    token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., min_length=8, description="New password")
    
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


class VerifyEmailRequest(BaseModel):
    """Schema for email verification request"""
    token: str = Field(..., description="Email verification token")


class AuthResponse(BaseModel):
    """Generic authentication response schema"""
    success: bool = Field(..., description="Whether operation was successful")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")
    error: Optional[str] = Field(None, description="Error message if operation failed")
    message: Optional[str] = Field(None, description="Success message")


class LogoutRequest(BaseModel):
    """Schema for logout request"""
    access_token: str = Field(..., description="Access token to invalidate")

