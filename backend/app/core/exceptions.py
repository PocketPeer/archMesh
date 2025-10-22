"""
Custom exceptions for ArchMesh
"""


class ArchMeshException(Exception):
    """Base exception for ArchMesh"""
    pass


class AuthenticationError(ArchMeshException):
    """Authentication related errors"""
    pass


class AuthorizationError(ArchMeshException):
    """Authorization related errors"""
    pass


class ValidationError(ArchMeshException):
    """Validation related errors"""
    pass


class NotFoundError(ArchMeshException):
    """Resource not found errors"""
    pass


class ConflictError(ArchMeshException):
    """Resource conflict errors"""
    pass


class ServiceError(ArchMeshException):
    """Service related errors"""
    pass


class LLMError(ArchMeshException):
    """LLM related errors"""
    pass


class AIChatError(ArchMeshException):
    """AI Chat service related errors"""
    pass


class WorkflowError(ArchMeshException):
    """Workflow related errors"""
    pass


class RegistrationError(ArchMeshException):
    """Registration related errors"""
    pass


class EmailValidationError(ArchMeshException):
    """Email validation related errors"""
    pass


class AccountActivationError(ArchMeshException):
    """Account activation related errors"""
    pass


class ProfileError(ArchMeshException):
    """Profile related errors"""
    pass


class SettingsError(ArchMeshException):
    """Settings related errors"""
    pass


class AccountError(ArchMeshException):
    """Account management related errors"""
    pass


class ProjectAccessError(ArchMeshException):
    """Project access related errors"""
    pass


class OwnershipError(ArchMeshException):
    """Project ownership related errors"""
    pass


class PermissionError(ArchMeshException):
    """Permission related errors"""
    pass


class CollaborationError(ArchMeshException):
    """Collaboration related errors"""
    pass


class TeamError(ArchMeshException):
    """Team management related errors"""
    pass


class WorkflowError(ArchMeshException):
    """Workflow related errors"""
    pass


# Vibe Coding Tool Exceptions

class VibeCodingError(ArchMeshException):
    """Base exception for Vibe Coding Tool"""
    pass


class IntentParseError(VibeCodingError):
    """Intent parsing related errors"""
    pass


class ContextGatherError(VibeCodingError):
    """Context gathering related errors"""
    pass


class CodeGenerationError(VibeCodingError):
    """Code generation related errors"""
    pass


class CodeExecutionError(VibeCodingError):
    """Code execution related errors"""
    pass


class MCPIntegrationError(VibeCodingError):
    """MCP integration related errors"""
    pass


class SandboxError(VibeCodingError):
    """Code execution sandbox related errors"""
    pass


class QualityAnalysisError(VibeCodingError):
    """Code quality analysis related errors"""
    pass


class VibeCodingTimeoutError(VibeCodingError):
    """Vibe coding operation timeout errors"""
    pass


class VibeCodingValidationError(VibeCodingError):
    """Vibe coding validation related errors"""
    pass


# WebSocket and Notification Exceptions

class WebSocketError(ArchMeshException):
    """WebSocket related errors"""
    pass


class ConnectionError(ArchMeshException):
    """Connection related errors"""
    pass


class NotificationError(ArchMeshException):
    """Notification related errors"""
    pass


class EmailError(ArchMeshException):
    """Email service related errors"""
    pass


class SMSError(ArchMeshException):
    """SMS service related errors"""
    pass


class TemplateError(ArchMeshException):
    """Template rendering related errors"""
    pass


class CodeGenerationError(ArchMeshException):
    """Code generation errors"""
    pass


class ValidationError(ArchMeshException):
    """Validation errors"""
    pass


class SandboxError(ArchMeshException):
    """Sandbox execution errors"""
    pass


class SecurityError(ArchMeshException):
    """Security-related errors"""
    pass


class ExecutionError(ArchMeshException):
    """Code execution errors"""
    pass


class TimeoutError(ArchMeshException):
    """Timeout errors"""
    pass
