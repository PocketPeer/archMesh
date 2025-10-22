"""
User model for authentication and authorization.

This module defines the User model with authentication capabilities,
including password hashing, email verification, and session management.
"""

import uuid
from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.hybrid import hybrid_property
from passlib.context import CryptContext

from app.core.database import Base


# Association table for user roles
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id'), primary_key=True),
    Column('role_id', UUID(as_uuid=True), ForeignKey('roles.id'), primary_key=True)
)


class Role(Base):
    """User role model for role-based access control."""
    
    __tablename__ = "roles"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique role identifier"
    )
    
    name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
        comment="Role name (e.g., 'admin', 'user', 'viewer')"
    )
    
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Role description"
    )
    
    permissions: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="JSON string of permissions for this role"
    )
    
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Whether the role is active"
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="Role creation timestamp"
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        comment="Role last update timestamp"
    )
    
    # Relationships
    users: Mapped[List["User"]] = relationship(
        "User",
        secondary=user_roles,
        back_populates="roles"
    )


class User(Base):
    """User model for authentication and user management."""
    
    __tablename__ = "users"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique user identifier"
    )
    
    # Basic user information
    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
        comment="User email address (used as username)"
    )
    
    username: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        unique=True,
        index=True,
        comment="User display name"
    )
    
    first_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="User first name"
    )
    
    last_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="User last name"
    )
    
    # Authentication fields
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Hashed password"
    )
    
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Whether the user account is active"
    )
    
    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether the user email is verified"
    )
    
    is_superuser: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether the user is a superuser/admin"
    )
    
    # Email verification
    verification_token: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        unique=True,
        comment="Email verification token"
    )
    
    verification_token_expires: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        comment="Email verification token expiration"
    )
    
    # Password reset
    password_reset_token: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        unique=True,
        comment="Password reset token"
    )
    
    password_reset_token_expires: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        comment="Password reset token expiration"
    )
    
    # Account security
    failed_login_attempts: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
        comment="Number of failed login attempts"
    )
    
    locked_until: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        comment="Account lockout expiration time"
    )
    
    last_login: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        comment="Last successful login timestamp"
    )
    
    last_login_ip: Mapped[Optional[str]] = mapped_column(
        String(45),
        nullable=True,
        comment="Last login IP address"
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="User creation timestamp"
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        comment="User last update timestamp"
    )
    
    # Relationships
    roles: Mapped[List[Role]] = relationship(
        "Role",
        secondary=user_roles,
        back_populates="users"
    )
    
    projects: Mapped[List["Project"]] = relationship(
        "Project",
        back_populates="owner",
        cascade="all, delete-orphan"
    )
    
    # Password context for hashing
    # Use bcrypt_sha256 to avoid 72-byte bcrypt limit
    _password_context = CryptContext(schemes=["bcrypt_sha256"], deprecated="auto")
    
    @hybrid_property
    def full_name(self) -> str:
        """Get user's full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        elif self.username:
            return self.username
        else:
            return self.email.split('@')[0]
    
    @hybrid_property
    def display_name(self) -> str:
        """Get user's display name."""
        return self.username or self.full_name or self.email.split('@')[0]
    
    def set_password(self, password: str) -> None:
        """Set user password with hashing."""
        self.hashed_password = self._password_context.hash(password)
    
    def verify_password(self, password: str) -> bool:
        """Verify user password."""
        return self._password_context.verify(password, self.hashed_password)
    
    def is_account_locked(self) -> bool:
        """Check if account is locked."""
        if self.locked_until is None:
            return False
        return datetime.utcnow() < self.locked_until
    
    def lock_account(self, duration_minutes: int = 30) -> None:
        """Lock user account for specified duration."""
        self.locked_until = datetime.utcnow() + timedelta(minutes=duration_minutes)
    
    def unlock_account(self) -> None:
        """Unlock user account."""
        self.locked_until = None
        self.failed_login_attempts = 0
    
    def increment_failed_login(self) -> None:
        """Increment failed login attempts and lock if threshold reached."""
        self.failed_login_attempts += 1
        
        # Lock account after 5 failed attempts
        if self.failed_login_attempts >= 5:
            self.lock_account(duration_minutes=30)
    
    def reset_failed_login_attempts(self) -> None:
        """Reset failed login attempts on successful login."""
        self.failed_login_attempts = 0
        self.locked_until = None
        self.last_login = datetime.utcnow()
    
    def generate_verification_token(self) -> str:
        """Generate email verification token."""
        token = str(uuid.uuid4())
        self.verification_token = token
        self.verification_token_expires = datetime.utcnow() + timedelta(hours=24)
        return token
    
    def generate_password_reset_token(self) -> str:
        """Generate password reset token."""
        token = str(uuid.uuid4())
        self.password_reset_token = token
        self.password_reset_token_expires = datetime.utcnow() + timedelta(hours=1)
        return token
    
    def verify_email(self) -> None:
        """Mark email as verified."""
        self.is_verified = True
        self.verification_token = None
        self.verification_token_expires = None
    
    def has_role(self, role_name: str) -> bool:
        """Check if user has a specific role."""
        return any(role.name == role_name for role in self.roles)
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has a specific permission."""
        # Superusers have all permissions
        if self.is_superuser:
            return True
        
        # Check role permissions
        for role in self.roles:
            if role.permissions and permission in role.permissions:
                return True
        
        return False
    
    def can_access_project(self, project_id: uuid.UUID) -> bool:
        """Check if user can access a specific project."""
        # Superusers can access all projects
        if self.is_superuser:
            return True
        
        # Users can access their own projects
        return any(project.id == project_id for project in self.projects)
    
    def to_dict(self, include_sensitive: bool = False) -> dict:
        """Convert user to dictionary representation."""
        data = {
            "id": str(self.id),
            "email": self.email,
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": self.full_name,
            "display_name": self.display_name,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "is_superuser": self.is_superuser,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "roles": [{"id": str(role.id), "name": role.name} for role in self.roles]
        }
        
        if include_sensitive:
            data.update({
                "failed_login_attempts": self.failed_login_attempts,
                "locked_until": self.locked_until.isoformat() if self.locked_until else None,
                "last_login_ip": self.last_login_ip
            })
        
        return data
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, username={self.username})>"


class UserSession(Base):
    """User session model for session management."""
    
    __tablename__ = "user_sessions"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique session identifier"
    )
    
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        comment="User ID for this session"
    )
    
    session_token: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
        comment="Session token"
    )
    
    refresh_token: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        unique=True,
        index=True,
        comment="Refresh token"
    )
    
    ip_address: Mapped[Optional[str]] = mapped_column(
        String(45),
        nullable=True,
        comment="IP address of the session"
    )
    
    user_agent: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="User agent string"
    )
    
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Whether the session is active"
    )
    
    expires_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        comment="Session expiration time"
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="Session creation timestamp"
    )
    
    last_accessed: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="Last session access timestamp"
    )
    
    # Relationships
    user: Mapped[User] = relationship("User", backref="sessions")
    
    def is_expired(self) -> bool:
        """Check if session is expired."""
        return datetime.utcnow() > self.expires_at
    
    def extend_session(self, duration_hours: int = 24) -> None:
        """Extend session expiration."""
        self.expires_at = datetime.utcnow() + timedelta(hours=duration_hours)
        self.last_accessed = datetime.utcnow()
    
    def deactivate(self) -> None:
        """Deactivate session."""
        self.is_active = False
    
    def to_dict(self) -> dict:
        """Convert session to dictionary representation."""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "is_active": self.is_active,
            "expires_at": self.expires_at.isoformat(),
            "created_at": self.created_at.isoformat(),
            "last_accessed": self.last_accessed.isoformat()
        }
    
    def __repr__(self) -> str:
        return f"<UserSession(id={self.id}, user_id={self.user_id}, active={self.is_active})>"

