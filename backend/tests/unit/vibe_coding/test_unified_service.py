"""
Test suite for the Unified Vibe Coding Service.

This test suite covers the main orchestrator service that integrates all
Vibe Coding components (Intent Parser, Context Aggregator, Code Generator, Sandbox Service)
into a cohesive workflow.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
from typing import Dict, Any, List

from app.vibe_coding.unified_service import (
    VibeCodingService,
    VibeCodingConfig,
    VibeCodingRequest,
    VibeCodingResponse,
    ChatRequest,
    ChatResponse,
    SessionStatus,
    FeedbackRequest,
    FeedbackResponse,
    VibeCodingError,
    SessionNotFoundError,
    InvalidRequestError
)
from app.vibe_coding.models import (
    ParsedIntent,
    UnifiedContext,
    GeneratedCode
)
from app.sandbox.models import (
    SandboxExecutionResponse,
    CodeQualityResult,
    ExecutionType,
    TestResult
)
from app.core.exceptions import VibeCodingError as CoreVibeCodingError


class TestVibeCodingServiceInitialization:
    """Test service initialization and configuration."""
    
    @pytest.mark.asyncio
    async def test_service_initialization_default_config(self):
        """Test service initialization with default configuration."""
        service = VibeCodingService()
        
        assert service is not None
        assert service.config is not None
        assert service.intent_parser is not None
        assert service.context_aggregator is not None
        assert service.code_generator is not None
        assert service.sandbox_service is not None
        assert service.metrics is not None
        assert service.logger is not None
    
    @pytest.mark.asyncio
    async def test_service_initialization_custom_config(self):
        """Test service initialization with custom configuration."""
        config = VibeCodingConfig(
            max_context_length=5000,
            timeout_seconds=60,
            enable_caching=True,
            max_concurrent_sessions=10
        )
        service = VibeCodingService(config)
        
        assert service.config == config
        assert service.config.max_context_length == 5000
        assert service.config.timeout_seconds == 60
        assert service.config.enable_caching is True
        assert service.config.max_concurrent_sessions == 10
    
    @pytest.mark.asyncio
    async def test_service_component_integration(self):
        """Test that all components are properly integrated."""
        service = VibeCodingService()
        
        # Verify all components are initialized
        assert hasattr(service, 'intent_parser')
        assert hasattr(service, 'context_aggregator')
        assert hasattr(service, 'code_generator')
        assert hasattr(service, 'sandbox_service')
        
        # Verify components have required methods
        assert hasattr(service.intent_parser, 'parse')
        assert hasattr(service.context_aggregator, 'aggregate_context')
        assert hasattr(service.code_generator, 'generate_code')
        assert hasattr(service.sandbox_service, 'execute_code')
    
    @pytest.mark.asyncio
    async def test_service_configuration_validation(self):
        """Test configuration validation."""
        with pytest.raises(ValueError, match="Invalid configuration"):
            VibeCodingConfig(
                max_context_length=-1,  # Invalid
                timeout_seconds=60,
                enable_caching=True,
                max_concurrent_sessions=10
            )
    
    @pytest.mark.asyncio
    async def test_service_error_handling_invalid_config(self):
        """Test error handling for invalid configuration."""
        with pytest.raises(ValueError):
            VibeCodingConfig(
                max_context_length=1000,
                timeout_seconds=-5,  # Invalid
                enable_caching=True,
                max_concurrent_sessions=10
            )


class TestVibeCodingServiceWorkflow:
    """Test end-to-end workflow execution."""
    
    @pytest.fixture
    def mock_service(self):
        """Create a mock service with mocked components."""
        service = VibeCodingService()
        
        # Mock all components
        service.intent_parser = AsyncMock()
        service.context_aggregator = AsyncMock()
        service.code_generator = AsyncMock()
        service.sandbox_service = AsyncMock()
        service.metrics = Mock()
        service.logger = Mock()
        
        return service
    
    @pytest.fixture
    def sample_request(self):
        """Create a sample VibeCodingRequest."""
        return VibeCodingRequest(
            user_input="Create a FastAPI endpoint for user authentication",
            project_id="test-project-123",
            session_id="test-session-456",
            context_sources=["requirements", "architecture"],
            language="python",
            framework="fastapi"
        )
    
    @pytest.fixture
    def mock_parsed_intent(self):
        """Create a mock ParsedIntent."""
        return ParsedIntent(
            intent_type="create_api_endpoint",
            confidence_score=0.95,
            requirements=["authentication", "security"],
            entities={
                "language": "python",
                "framework": "fastapi",
                "purpose": "user authentication"
            },
            constraints=[],
            context_hints=[]
        )
    
    @pytest.fixture
    def mock_unified_context(self):
        """Create a mock UnifiedContext."""
        return UnifiedContext(
            project_structure={"src": ["main.py", "models.py"]},
            requirements=["User authentication", "JWT tokens"],
            architecture={"style": "microservices", "components": ["auth-service"]},
            dependencies={"fastapi": "0.104.1", "python-jose": "3.3.0"},
            quality_score=0.85
        )
    
    @pytest.fixture
    def mock_generated_code(self):
        """Create a mock GeneratedCode."""
        return GeneratedCode(
            code='from fastapi import FastAPI, Depends, HTTPException\nfrom fastapi.security import HTTPBearer\n\napp = FastAPI()\nsecurity = HTTPBearer()\n\n@app.post("/auth/login")\nasync def login(username: str, password: str):\n    # Authentication logic here\n    return {"access_token": "jwt_token"}\n',
            language="python",
            framework="fastapi",
            file_path="src/auth.py",
            dependencies=["fastapi", "python-jose"],
            quality_score=0.9,
            execution_time=2.5
        )
    
    @pytest.fixture
    def mock_execution_result(self):
        """Create a mock SandboxExecutionResponse result."""
        from app.sandbox.models import ExecutionType, TestResult
        return SandboxExecutionResponse(
            execution_id="test-execution-123",
            success=True,
            language="python",
            execution_type=ExecutionType.RUN,
            exit_code=0,
            stdout="Authentication endpoint created successfully",
            stderr="",
            execution_time=1.2,
            memory_usage_mb=45.6,
            cpu_usage_percent=25.0,
            test_results=TestResult(
                test_name="authentication_test",
                passed=True,
                execution_time=0.5
            ),
            passed_tests=["test_auth_endpoint", "test_auth_validation"],
            failed_tests=[],
            security_scan_passed=True,
            security_violations=[],
            performance_results=None
        )
    
    @pytest.mark.asyncio
    async def test_simple_code_generation_workflow(self, mock_service, sample_request, 
                                                 mock_parsed_intent, mock_unified_context, 
                                                 mock_generated_code, mock_execution_result):
        """Test simple code generation workflow."""
        # Setup mocks
        mock_service.intent_parser.parse.return_value = mock_parsed_intent
        mock_service.context_aggregator.aggregate_context.return_value = mock_unified_context
        mock_service.code_generator.generate_code.return_value = mock_generated_code
        mock_service.sandbox_service.execute_code.return_value = mock_execution_result
        
        # Execute workflow
        response = await mock_service.generate_code(sample_request)
        
        # Verify response
        assert response is not None
        assert response.success is True
        assert response.generated_code is not None
        assert response.execution_result is not None
        assert response.session_id == sample_request.session_id
        assert response.execution_time > 0
        
        # Verify component calls
        mock_service.intent_parser.parse.assert_called_once_with(sample_request.user_input)
        mock_service.context_aggregator.aggregate_context.assert_called_once()
        mock_service.code_generator.generate_code.assert_called_once()
        mock_service.sandbox_service.execute_code.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_complex_multi_step_workflow(self, mock_service):
        """Test complex multi-step workflow with multiple iterations."""
        # Create a complex request
        request = VibeCodingRequest(
            user_input="Create a complete user management system with authentication, authorization, and user CRUD operations",
            project_id="complex-project-789",
            session_id="complex-session-101",
            context_sources=["requirements", "architecture", "database"],
            language="python",
            framework="fastapi"
        )
        
        # Setup mocks for complex workflow
        mock_service.intent_parser.parse.return_value = ParsedIntent(
            intent_type="create_system",
            confidence_score=0.88,
            requirements=["authentication", "authorization", "CRUD operations"],
            entities={
                "language": "python",
                "framework": "fastapi",
                "purpose": "user management"
            },
            constraints=[],
            context_hints=[]
        )
        
        mock_service.context_aggregator.aggregate_context.return_value = UnifiedContext(
            project_structure={"src": ["main.py", "models.py", "auth.py", "users.py"]},
            requirements=["User management", "Authentication", "Authorization"],
            architecture={"style": "microservices", "components": ["user-service", "auth-service"]},
            dependencies={"fastapi": "0.104.1", "sqlalchemy": "2.0.23"},
            quality_score=0.92
        )
        
        mock_service.code_generator.generate_code.return_value = GeneratedCode(
            code="# Complete user management system code...",
            language="python",
            framework="fastapi",
            file_path="src/user_management.py",
            dependencies=["fastapi", "sqlalchemy", "python-jose"],
            quality_score=0.85,
            execution_time=5.2
        )
        
        mock_service.sandbox_service.execute_code.return_value = SandboxExecutionResponse(
            execution_id="test-execution-595",
            success=True,
            language="python",
            execution_type=ExecutionType.RUN,
            exit_code=0,
            stdout="User management system created successfully",
            stderr="",
            execution_time=3.1,
            memory_usage_mb=78.3,
            cpu_usage_percent=25.0,
            test_results=TestResult(
                test_name="test_execution",
                passed=True,
                execution_time=3.1
            ),
            passed_tests=["test_passed"],
            failed_tests=[],
            security_scan_passed=True,
            security_violations=[],
            performance_results=None
        )
        
        # Execute workflow
        response = await mock_service.generate_code(request)
        
        # Verify response
        assert response is not None
        assert response.success is True
        assert response.generated_code is not None
        assert response.execution_result is not None
        assert response.session_id == request.session_id
        assert response.execution_time > 0
        
        # Verify all components were called
        mock_service.intent_parser.parse.assert_called_once()
        mock_service.context_aggregator.aggregate_context.assert_called_once()
        mock_service.code_generator.generate_code.assert_called_once()
        mock_service.sandbox_service.execute_code.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_workflow_with_context_aggregation(self, mock_service, sample_request):
        """Test workflow with context aggregation."""
        # Setup mocks
        mock_service.intent_parser.parse.return_value = ParsedIntent(
            intent_type="create_api_endpoint",
            confidence_score=0.9,
            requirements=["authentication"],
            entities={
                "language": "python",
                "framework": "fastapi",
                "purpose": "user authentication"
            },
            constraints=[],
            context_hints=[]
        )
        
        mock_service.context_aggregator.aggregate_context.return_value = UnifiedContext(
            project_structure={"src": ["main.py"]},
            requirements=["User authentication with JWT"],
            architecture={"style": "monolithic", "components": ["api"]},
            dependencies={"fastapi": "0.104.1"},
            quality_score=0.8
        )
        
        mock_service.code_generator.generate_code.return_value = GeneratedCode(
            code="# Authentication endpoint code...",
            language="python",
            framework="fastapi",
            file_path="src/auth.py",
            dependencies=["fastapi"],
            quality_score=0.85,
            execution_time=2.0
        )
        
        mock_service.sandbox_service.execute_code.return_value = SandboxExecutionResponse(
            execution_id="test-execution-17",
            success=True,
            language="python",
            execution_type=ExecutionType.RUN,
            exit_code=0,
            stdout="Authentication endpoint created",
            stderr="",
            execution_time=1.5,
            memory_usage_mb=32.1,
            cpu_usage_percent=25.0,
            test_results=TestResult(
                test_name="test_execution",
                passed=True,
                execution_time=1.5
            ),
            passed_tests=["test_passed"],
            failed_tests=[],
            security_scan_passed=True,
            security_violations=[],
            performance_results=None
        )
        
        # Execute workflow
        response = await mock_service.generate_code(sample_request)
        
        # Verify context aggregation was called with correct parameters
        mock_service.context_aggregator.aggregate_context.assert_called_once()
        call_args = mock_service.context_aggregator.aggregate_context.call_args
        context_request = call_args[0][0]  # First positional argument
        assert context_request['project_id'] == sample_request.project_id
        assert context_request['sources'] == sample_request.context_sources
    
    @pytest.mark.asyncio
    async def test_workflow_with_sandbox_execution(self, mock_service, sample_request):
        """Test workflow with sandbox execution."""
        # Setup mocks
        mock_service.intent_parser.parse.return_value = ParsedIntent(
            intent_type="create_api_endpoint",
            confidence_score=0.9,
            requirements=["authentication"],
            entities={
                "language": "python",
                "framework": "fastapi",
                "purpose": "user authentication"
            },
            constraints=[],
            context_hints=[]
        )
        
        mock_service.context_aggregator.aggregate_context.return_value = UnifiedContext(
            project_structure={"src": ["main.py"]},
            requirements=["User authentication"],
            architecture={"style": "monolithic"},
            dependencies={"fastapi": "0.104.1"},
            quality_score=0.8
        )
        
        mock_service.code_generator.generate_code.return_value = GeneratedCode(
            code="# Authentication endpoint code...",
            language="python",
            framework="fastapi",
            file_path="src/auth.py",
            dependencies=["fastapi"],
            quality_score=0.85,
            execution_time=2.0
        )
        
        mock_service.sandbox_service.execute_code.return_value = SandboxExecutionResponse(
            execution_id="test-execution-484",
            success=True,
            language="python",
            execution_type=ExecutionType.RUN,
            exit_code=0,
            stdout="Authentication endpoint created successfully",
            stderr="",
            execution_time=1.8,
            memory_usage_mb=45.2,
            cpu_usage_percent=25.0,
            test_results=TestResult(
                test_name="test_execution",
                passed=True,
                execution_time=1.8
            ),
            passed_tests=["test_passed"],
            failed_tests=[],
            security_scan_passed=True,
            security_violations=[],
            performance_results=None
        )
        
        # Execute workflow
        response = await mock_service.generate_code(sample_request)
        
        # Verify sandbox execution was called
        mock_service.sandbox_service.execute_code.assert_called_once()
        call_args = mock_service.sandbox_service.execute_code.call_args
        execution_request = call_args[0][0]  # First positional argument
        assert execution_request['code'] is not None
        assert execution_request['language'] == "python"
    
    @pytest.mark.asyncio
    async def test_workflow_error_handling(self, mock_service, sample_request):
        """Test workflow error handling."""
        # Setup mock to raise an error
        mock_service.intent_parser.parse.side_effect = Exception("Intent parsing failed")
        
        # Execute workflow and expect error
        with pytest.raises(VibeCodingError, match="Workflow execution failed"):
            await mock_service.generate_code(sample_request)
        
        # Verify error handling
        mock_service.logger.error.assert_called()
    
    @pytest.mark.asyncio
    async def test_workflow_cancellation(self, mock_service, sample_request):
        """Test workflow cancellation."""
        # Setup mock to simulate cancellation
        mock_service.intent_parser.parse.side_effect = asyncio.CancelledError()
        
        # Execute workflow and expect cancellation
        with pytest.raises(asyncio.CancelledError):
            await mock_service.generate_code(sample_request)
    
    @pytest.mark.asyncio
    async def test_workflow_progress_tracking(self, mock_service, sample_request):
        """Test workflow progress tracking."""
        # Setup mocks
        mock_service.intent_parser.parse.return_value = ParsedIntent(
            intent_type="create_api_endpoint",
            confidence_score=0.9,
            requirements=["authentication"],
            entities={
                "language": "python",
                "framework": "fastapi",
                "purpose": "user authentication"
            },
            constraints=[],
            context_hints=[]
        )
        
        mock_service.context_aggregator.aggregate_context.return_value = UnifiedContext(
            project_structure={"src": ["main.py"]},
            requirements=["User authentication"],
            architecture={"style": "monolithic"},
            dependencies={"fastapi": "0.104.1"},
            quality_score=0.8
        )
        
        mock_service.code_generator.generate_code.return_value = GeneratedCode(
            code="# Authentication endpoint code...",
            language="python",
            framework="fastapi",
            file_path="src/auth.py",
            dependencies=["fastapi"],
            quality_score=0.85,
            execution_time=2.0
        )
        
        mock_service.sandbox_service.execute_code.return_value = SandboxExecutionResponse(
            execution_id="test-execution-17",
            success=True,
            language="python",
            execution_type=ExecutionType.RUN,
            exit_code=0,
            stdout="Authentication endpoint created",
            stderr="",
            execution_time=1.5,
            memory_usage_mb=32.1,
            cpu_usage_percent=25.0,
            test_results=TestResult(
                test_name="test_execution",
                passed=True,
                execution_time=1.5
            ),
            passed_tests=["test_passed"],
            failed_tests=[],
            security_scan_passed=True,
            security_violations=[],
            performance_results=None
        )
        
        # Execute workflow
        response = await mock_service.generate_code(sample_request)
        
        # Verify progress tracking
        assert response.progress == 100
        assert response.current_stage == "completed"
        assert response.stages_completed == ["intent_parsing", "context_aggregation", "code_generation", "execution"]
    
    @pytest.mark.asyncio
    async def test_workflow_result_validation(self, mock_service, sample_request):
        """Test workflow result validation."""
        # Setup mocks
        mock_service.intent_parser.parse.return_value = ParsedIntent(
            intent_type="create_api_endpoint",
            confidence_score=0.9,
            requirements=["authentication"],
            entities={
                "language": "python",
                "framework": "fastapi",
                "purpose": "user authentication"
            },
            constraints=[],
            context_hints=[]
        )
        
        mock_service.context_aggregator.aggregate_context.return_value = UnifiedContext(
            project_structure={"src": ["main.py"]},
            requirements=["User authentication"],
            architecture={"style": "monolithic"},
            dependencies={"fastapi": "0.104.1"},
            quality_score=0.8
        )
        
        mock_service.code_generator.generate_code.return_value = GeneratedCode(
            code="# Authentication endpoint code...",
            language="python",
            framework="fastapi",
            file_path="src/auth.py",
            dependencies=["fastapi"],
            quality_score=0.85,
            execution_time=2.0
        )
        
        mock_service.sandbox_service.execute_code.return_value = SandboxExecutionResponse(
            execution_id="test-execution-17",
            success=True,
            language="python",
            execution_type=ExecutionType.RUN,
            exit_code=0,
            stdout="Authentication endpoint created",
            stderr="",
            execution_time=1.5,
            memory_usage_mb=32.1,
            cpu_usage_percent=25.0,
            test_results=TestResult(
                test_name="test_execution",
                passed=True,
                execution_time=1.5
            ),
            passed_tests=["test_passed"],
            failed_tests=[],
            security_scan_passed=True,
            security_violations=[],
            performance_results=None
        )
        
        # Execute workflow
        response = await mock_service.generate_code(sample_request)
        
        # Verify result validation
        assert response.success is True
        assert response.generated_code is not None
        assert response.execution_result is not None
        assert response.execution_result.success is True
        assert len(response.generated_code.code) > 0
        assert response.execution_result.test_results.passed is True


class TestVibeCodingServiceComponentIntegration:
    """Test integration with individual components."""
    
    @pytest.fixture
    def mock_service(self):
        """Create a mock service with mocked components."""
        service = VibeCodingService()
        service.intent_parser = AsyncMock()
        service.context_aggregator = AsyncMock()
        service.code_generator = AsyncMock()
        service.sandbox_service = AsyncMock()
        service.metrics = Mock()
        service.logger = Mock()
        return service
    
    @pytest.mark.asyncio
    async def test_intent_parser_integration(self, mock_service):
        """Test integration with Intent Parser."""
        request = VibeCodingRequest(
            user_input="Create a REST API endpoint",
            project_id="test-project",
            session_id="test-session"
        )
        
        mock_service.intent_parser.parse.return_value = ParsedIntent(
            intent_type="create_api_endpoint",
            confidence_score=0.9,
            requirements=["API endpoint"],
            entities={
                "language": "python",
                "framework": "fastapi",
                "purpose": "REST API"
            },
            constraints=[],
            context_hints=[]
        )
        
        # Mock other components
        mock_service.context_aggregator.aggregate_context.return_value = UnifiedContext(
            project_structure={},
            requirements=[],
            architecture={},
            dependencies={},
            quality_score=0.8
        )
        
        mock_service.code_generator.generate_code.return_value = GeneratedCode(
            code="# API endpoint code...",
            language="python",
            framework="fastapi",
            file_path="src/api.py",
            dependencies=["fastapi"],
            quality_score=0.85,
            execution_time=1.5
        )
        
        mock_service.sandbox_service.execute_code.return_value = SandboxExecutionResponse(
            execution_id="test-execution-422",
            success=True,
            language="python",
            execution_type=ExecutionType.RUN,
            exit_code=0,
            stdout="API endpoint created",
            stderr="",
            execution_time=1.0,
            memory_usage_mb=25.0,
            cpu_usage_percent=25.0,
            test_results=TestResult(
                test_name="test_execution",
                passed=True,
                execution_time=1.0
            ),
            passed_tests=["test_passed"],
            failed_tests=[],
            security_scan_passed=True,
            security_violations=[],
            performance_results=None
        )
        
        response = await mock_service.generate_code(request)
        
        # Verify intent parser was called correctly
        mock_service.intent_parser.parse.assert_called_once_with(request.user_input)
        assert response.success is True
    
    @pytest.mark.asyncio
    async def test_context_aggregator_integration(self, mock_service):
        """Test integration with Context Aggregator."""
        request = VibeCodingRequest(
            user_input="Create a user model",
            project_id="test-project",
            session_id="test-session",
            context_sources=["requirements", "database"]
        )
        
        # Mock intent parser
        mock_service.intent_parser.parse.return_value = ParsedIntent(
            intent_type="create_model",
            confidence_score=0.9,
            requirements=["user model"],
            entities={
                "language": "python",
                "framework": "sqlalchemy",
                "purpose": "user model"
            },
            constraints=[],
            context_hints=[]
        )
        
        # Mock context aggregator
        mock_service.context_aggregator.aggregate_context.return_value = UnifiedContext(
            project_structure={"models": ["user.py"]},
            requirements=["User model with authentication"],
            architecture={"style": "monolithic"},
            dependencies={"sqlalchemy": "2.0.23"},
            quality_score=0.9
        )
        
        # Mock other components
        mock_service.code_generator.generate_code.return_value = GeneratedCode(
            code="# User model code...",
            language="python",
            framework="sqlalchemy",
            file_path="models/user.py",
            dependencies=["sqlalchemy"],
            quality_score=0.9,
            execution_time=1.0
        )
        
        mock_service.sandbox_service.execute_code.return_value = SandboxExecutionResponse(
            execution_id="test-execution-662",
            success=True,
            language="python",
            execution_type=ExecutionType.RUN,
            exit_code=0,
            stdout="User model created",
            stderr="",
            execution_time=0.8,
            memory_usage_mb=20.0,
            cpu_usage_percent=25.0,
            test_results=TestResult(
                test_name="test_execution",
                passed=True,
                execution_time=0.8
            ),
            passed_tests=["test_passed"],
            failed_tests=[],
            security_scan_passed=True,
            security_violations=[],
            performance_results=None
        )
        
        response = await mock_service.generate_code(request)
        
        # Verify context aggregator was called correctly
        mock_service.context_aggregator.aggregate_context.assert_called_once()
        call_args = mock_service.context_aggregator.aggregate_context.call_args
        context_request = call_args[0][0]  # First positional argument
        assert context_request['project_id'] == request.project_id
        assert context_request['sources'] == request.context_sources
    
    @pytest.mark.asyncio
    async def test_code_generator_integration(self, mock_service):
        """Test integration with Code Generator."""
        request = VibeCodingRequest(
            user_input="Create a test for user authentication",
            project_id="test-project",
            session_id="test-session"
        )
        
        # Mock intent parser
        mock_service.intent_parser.parse.return_value = ParsedIntent(
            intent_type="create_test",
            confidence_score=0.9,
            requirements=["test", "authentication"],
            entities={
                "language": "python",
                "framework": "pytest",
                "purpose": "user authentication test"
            },
            constraints=[],
            context_hints=[]
        )
        
        # Mock context aggregator
        mock_service.context_aggregator.aggregate_context.return_value = UnifiedContext(
            project_structure={"tests": ["test_auth.py"]},
            requirements=["Test user authentication"],
            architecture={"style": "monolithic"},
            dependencies={"pytest": "7.4.3"},
            quality_score=0.8
        )
        
        # Mock code generator
        mock_service.code_generator.generate_code.return_value = GeneratedCode(
            code="# Test code...",
            language="python",
            framework="pytest",
            file_path="tests/test_auth.py",
            dependencies=["pytest"],
            quality_score=0.9,
            execution_time=1.2
        )
        
        # Mock sandbox service
        mock_service.sandbox_service.execute_code.return_value = SandboxExecutionResponse(
            execution_id="test-execution-425",
            success=True,
            language="python",
            execution_type=ExecutionType.RUN,
            exit_code=0,
            stdout="Tests passed",
            stderr="",
            execution_time=0.5,
            memory_usage_mb=15.0,
            cpu_usage_percent=25.0,
            test_results=TestResult(
                test_name="test_execution",
                passed=True,
                execution_time=0.5
            ),
            passed_tests=["test_passed"],
            failed_tests=[],
            security_scan_passed=True,
            security_violations=[],
            performance_results=None
        )
        
        response = await mock_service.generate_code(request)
        
        # Verify code generator was called correctly
        mock_service.code_generator.generate_code.assert_called_once()
        call_args = mock_service.code_generator.generate_code.call_args
        generation_request = call_args[0][0]  # First positional argument
        assert generation_request['intent'] is not None
        assert generation_request['context'] is not None
    
    @pytest.mark.asyncio
    async def test_sandbox_service_integration(self, mock_service):
        """Test integration with Sandbox Service."""
        request = VibeCodingRequest(
            user_input="Create a simple calculator function",
            project_id="test-project",
            session_id="test-session"
        )
        
        # Mock intent parser
        mock_service.intent_parser.parse.return_value = ParsedIntent(
            intent_type="create_function",
            confidence_score=0.9,
            requirements=["calculator"],
            entities={
                "language": "python",
                "framework": "standard",
                "purpose": "calculator function"
            },
            constraints=[],
            context_hints=[]
        )
        
        # Mock context aggregator
        mock_service.context_aggregator.aggregate_context.return_value = UnifiedContext(
            project_structure={"src": ["calculator.py"]},
            requirements=["Calculator function"],
            architecture={"style": "monolithic"},
            dependencies={},
            quality_score=0.8
        )
        
        # Mock code generator
        mock_service.code_generator.generate_code.return_value = GeneratedCode(
            code="def add(a, b):\n    return a + b",
            language="python",
            framework="standard",
            file_path="src/calculator.py",
            dependencies=[],
            quality_score=0.95,
            execution_time=0.5
        )
        
        # Mock sandbox service
        mock_service.sandbox_service.execute_code.return_value = SandboxExecutionResponse(
            execution_id="test-execution-522",
            success=True,
            language="python",
            execution_type=ExecutionType.RUN,
            exit_code=0,
            stdout="Function executed successfully",
            stderr="",
            execution_time=0.1,
            memory_usage_mb=10.0,
            cpu_usage_percent=25.0,
            test_results=TestResult(
                test_name="test_execution",
                passed=True,
                execution_time=0.1
            ),
            passed_tests=["test_passed"],
            failed_tests=[],
            security_scan_passed=True,
            security_violations=[],
            performance_results=None
        )
        
        response = await mock_service.generate_code(request)
        
        # Verify sandbox service was called correctly
        mock_service.sandbox_service.execute_code.assert_called_once()
        call_args = mock_service.sandbox_service.execute_code.call_args
        execution_request = call_args[0][0]  # First positional argument
        assert execution_request['code'] is not None
        assert execution_request['language'] == "python"
    
    @pytest.mark.asyncio
    async def test_component_failure_handling(self, mock_service):
        """Test handling of component failures."""
        request = VibeCodingRequest(
            user_input="Create a broken function",
            project_id="test-project",
            session_id="test-session"
        )
        
        # Mock intent parser to fail
        mock_service.intent_parser.parse.side_effect = Exception("Intent parsing failed")
        
        # Execute workflow and expect error
        with pytest.raises(VibeCodingError, match="Workflow execution failed"):
            await mock_service.generate_code(request)
        
        # Verify error logging
        mock_service.logger.error.assert_called()


class TestVibeCodingServiceErrorHandling:
    """Test error handling and recovery."""
    
    @pytest.fixture
    def mock_service(self):
        """Create a mock service with mocked components."""
        service = VibeCodingService()
        service.intent_parser = AsyncMock()
        service.context_aggregator = AsyncMock()
        service.code_generator = AsyncMock()
        service.sandbox_service = AsyncMock()
        service.metrics = Mock()
        service.logger = Mock()
        return service
    
    @pytest.mark.asyncio
    async def test_invalid_input_handling(self, mock_service):
        """Test handling of invalid input."""
        # Test with empty input
        request = VibeCodingRequest(
            user_input="",
            project_id="test-project",
            session_id="test-session"
        )
        
        with pytest.raises(VibeCodingError, match="Workflow execution failed"):
            await mock_service.generate_code(request)
        
        # Test with None input
        request.user_input = None
        
        with pytest.raises(VibeCodingError, match="Workflow execution failed"):
            await mock_service.generate_code(request)
    
    @pytest.mark.asyncio
    async def test_component_failure_recovery(self, mock_service):
        """Test recovery from component failures."""
        request = VibeCodingRequest(
            user_input="Create a function",
            project_id="test-project",
            session_id="test-session"
        )
        
        # Mock context aggregator to fail
        mock_service.intent_parser.parse.return_value = ParsedIntent(
            intent_type="create_function",
            confidence_score=0.9,
            requirements=["function"],
            entities={
                "language": "python",
                "framework": "standard",
                "purpose": "function"
            },
            constraints=[],
            context_hints=[]
        )
        
        mock_service.context_aggregator.aggregate_context.side_effect = Exception("Context aggregation failed")
        
        # Execute workflow and expect error
        with pytest.raises(VibeCodingError, match="Workflow execution failed"):
            await mock_service.generate_code(request)
        
        # Verify error logging
        mock_service.logger.error.assert_called()
    
    @pytest.mark.asyncio
    async def test_network_error_handling(self, mock_service):
        """Test handling of network errors."""
        request = VibeCodingRequest(
            user_input="Create a function",
            project_id="test-project",
            session_id="test-session"
        )
        
        # Mock network error
        mock_service.intent_parser.parse.side_effect = ConnectionError("Network error")
        
        # Execute workflow and expect error
        with pytest.raises(VibeCodingError, match="Workflow execution failed"):
            await mock_service.generate_code(request)
    
    @pytest.mark.asyncio
    async def test_timeout_handling(self, mock_service):
        """Test handling of timeouts."""
        request = VibeCodingRequest(
            user_input="Create a function",
            project_id="test-project",
            session_id="test-session"
        )
        
        # Mock timeout
        mock_service.intent_parser.parse.side_effect = asyncio.TimeoutError("Operation timed out")
        
        # Execute workflow and expect error
        with pytest.raises(VibeCodingError, match="Workflow execution failed"):
            await mock_service.generate_code(request)


class TestVibeCodingServicePerformance:
    """Test performance and monitoring."""
    
    @pytest.fixture
    def mock_service(self):
        """Create a mock service with mocked components."""
        service = VibeCodingService()
        service.intent_parser = AsyncMock()
        service.context_aggregator = AsyncMock()
        service.code_generator = AsyncMock()
        service.sandbox_service = AsyncMock()
        service.metrics = Mock()
        service.logger = Mock()
        return service
    
    @pytest.mark.asyncio
    async def test_performance_metrics_collection(self, mock_service):
        """Test collection of performance metrics."""
        request = VibeCodingRequest(
            user_input="Create a function",
            project_id="test-project",
            session_id="test-session"
        )
        
        # Setup mocks
        mock_service.intent_parser.parse.return_value = ParsedIntent(
            intent_type="create_function",
            confidence_score=0.9,
            requirements=["function"],
            entities={
                "language": "python",
                "framework": "standard",
                "purpose": "function"
            },
            constraints=[],
            context_hints=[]
        )
        
        mock_service.context_aggregator.aggregate_context.return_value = UnifiedContext(
            project_structure={},
            requirements=[],
            architecture={},
            dependencies={},
            quality_score=0.8
        )
        
        mock_service.code_generator.generate_code.return_value = GeneratedCode(
            code="# Function code...",
            language="python",
            framework="standard",
            file_path="src/function.py",
            dependencies=[],
            quality_score=0.9,
            execution_time=1.0
        )
        
        mock_service.sandbox_service.execute_code.return_value = SandboxExecutionResponse(
            execution_id="test-execution-592",
            success=True,
            language="python",
            execution_type=ExecutionType.RUN,
            exit_code=0,
            stdout="Function created",
            stderr="",
            execution_time=0.5,
            memory_usage_mb=20.0,
            cpu_usage_percent=25.0,
            test_results=TestResult(
                test_name="test_execution",
                passed=True,
                execution_time=0.5
            ),
            passed_tests=["test_passed"],
            failed_tests=[],
            security_scan_passed=True,
            security_violations=[],
            performance_results=None
        )
        
        response = await mock_service.generate_code(request)
        
        # Verify metrics collection
        mock_service.metrics.record_request.assert_called()
        mock_service.metrics.record_execution_time.assert_called()
        mock_service.metrics.record_success.assert_called()
        
        assert response.execution_time > 0
        assert response.metrics is not None
    
    @pytest.mark.asyncio
    async def test_resource_usage_monitoring(self, mock_service):
        """Test resource usage monitoring."""
        request = VibeCodingRequest(
            user_input="Create a function",
            project_id="test-project",
            session_id="test-session"
        )
        
        # Setup mocks
        mock_service.intent_parser.parse.return_value = ParsedIntent(
            intent_type="create_function",
            confidence_score=0.9,
            requirements=["function"],
            entities={
                "language": "python",
                "framework": "standard",
                "purpose": "function"
            },
            constraints=[],
            context_hints=[]
        )
        
        mock_service.context_aggregator.aggregate_context.return_value = UnifiedContext(
            project_structure={},
            requirements=[],
            architecture={},
            dependencies={},
            quality_score=0.8
        )
        
        mock_service.code_generator.generate_code.return_value = GeneratedCode(
            code="# Function code...",
            language="python",
            framework="standard",
            file_path="src/function.py",
            dependencies=[],
            quality_score=0.9,
            execution_time=1.0
        )
        
        mock_service.sandbox_service.execute_code.return_value = SandboxExecutionResponse(
            execution_id="test-execution-592",
            success=True,
            language="python",
            execution_type=ExecutionType.RUN,
            exit_code=0,
            stdout="Function created",
            stderr="",
            execution_time=0.5,
            memory_usage_mb=25.0,
            cpu_usage_percent=25.0,
            test_results=TestResult(
                test_name="test_execution",
                passed=True,
                execution_time=0.5
            ),
            passed_tests=["test_passed"],
            failed_tests=[],
            security_scan_passed=True,
            security_violations=[],
            performance_results=None
        )
        
        response = await mock_service.generate_code(request)
        
        # Verify resource monitoring
        assert response.memory_usage > 0
        assert response.cpu_usage >= 0
        assert response.execution_time > 0
    
    @pytest.mark.asyncio
    async def test_health_check_functionality(self, mock_service):
        """Test health check functionality."""
        # Mock health check
        mock_service.intent_parser.health_check.return_value = True
        mock_service.context_aggregator.health_check.return_value = True
        mock_service.code_generator.health_check.return_value = True
        mock_service.sandbox_service.health_check.return_value = True
        
        # Test health check
        health_status = await mock_service.health_check()
        
        # Verify health check
        assert health_status is not None
        assert health_status.overall_health is True
        assert health_status.components["intent_parser"] is True
        assert health_status.components["context_aggregator"] is True
        assert health_status.components["code_generator"] is True
        assert health_status.components["sandbox_service"] is True


class TestVibeCodingServiceChatInterface:
    """Test conversational interface."""
    
    @pytest.fixture
    def mock_service(self):
        """Create a mock service with mocked components."""
        service = VibeCodingService()
        service.intent_parser = AsyncMock()
        service.context_aggregator = AsyncMock()
        service.code_generator = AsyncMock()
        service.sandbox_service = AsyncMock()
        service.metrics = Mock()
        service.logger = Mock()
        return service
    
    @pytest.mark.asyncio
    async def test_chat_interface_basic(self, mock_service):
        """Test basic chat interface functionality."""
        chat_request = ChatRequest(
            message="Create a function to add two numbers",
            session_id="chat-session-123",
            project_id="test-project"
        )
        
        # Setup mocks
        mock_service.intent_parser.parse.return_value = ParsedIntent(
            intent_type="create_function",
            confidence_score=0.9,
            requirements=["addition"],
            entities={
                "language": "python",
                "framework": "standard",
                "purpose": "add two numbers"
            },
            constraints=[],
            context_hints=[]
        )
        
        mock_service.context_aggregator.aggregate_context.return_value = UnifiedContext(
            project_structure={},
            requirements=[],
            architecture={},
            dependencies={},
            quality_score=0.8
        )
        
        mock_service.code_generator.generate_code.return_value = GeneratedCode(
            code="def add(a, b):\n    return a + b",
            language="python",
            framework="standard",
            file_path="src/math.py",
            dependencies=[],
            quality_score=0.95,
            execution_time=0.5
        )
        
        mock_service.sandbox_service.execute_code.return_value = SandboxExecutionResponse(
            execution_id="test-execution-490",
            success=True,
            language="python",
            execution_type=ExecutionType.RUN,
            exit_code=0,
            stdout="Function created successfully",
            stderr="",
            execution_time=0.1,
            memory_usage_mb=10.0,
            cpu_usage_percent=25.0,
            test_results=TestResult(
                test_name="test_execution",
                passed=True,
                execution_time=0.1
            ),
            passed_tests=["test_passed"],
            failed_tests=[],
            security_scan_passed=True,
            security_violations=[],
            performance_results=None
        )
        
        response = await mock_service.chat(chat_request)
        
        # Verify chat response
        assert response is not None
        assert response.success is True
        assert response.message is not None
        assert response.generated_code is not None
        assert response.session_id == chat_request.session_id
    
    @pytest.mark.asyncio
    async def test_chat_interface_iterative(self, mock_service):
        """Test iterative chat interface."""
        # First message
        chat_request1 = ChatRequest(
            message="Create a function to add two numbers",
            session_id="chat-session-123",
            project_id="test-project"
        )
        
        # Setup mocks for first message
        mock_service.intent_parser.parse.return_value = ParsedIntent(
            intent_type="create_function",
            confidence_score=0.9,
            requirements=["addition"],
            entities={
                "language": "python",
                "framework": "standard",
                "purpose": "add two numbers"
            },
            constraints=[],
            context_hints=[]
        )
        
        mock_service.context_aggregator.aggregate_context.return_value = UnifiedContext(
            project_structure={},
            requirements=[],
            architecture={},
            dependencies={},
            quality_score=0.8
        )
        
        mock_service.code_generator.generate_code.return_value = GeneratedCode(
            code="def add(a, b):\n    return a + b",
            language="python",
            framework="standard",
            file_path="src/math.py",
            dependencies=[],
            quality_score=0.95,
            execution_time=0.5
        )
        
        mock_service.sandbox_service.execute_code.return_value = SandboxExecutionResponse(
            execution_id="test-execution-490",
            success=True,
            language="python",
            execution_type=ExecutionType.RUN,
            exit_code=0,
            stdout="Function created successfully",
            stderr="",
            execution_time=0.1,
            memory_usage_mb=10.0,
            cpu_usage_percent=25.0,
            test_results=TestResult(
                test_name="test_execution",
                passed=True,
                execution_time=0.1
            ),
            passed_tests=["test_passed"],
            failed_tests=[],
            security_scan_passed=True,
            security_violations=[],
            performance_results=None
        )
        
        response1 = await mock_service.chat(chat_request1)
        
        # Second message (refinement)
        chat_request2 = ChatRequest(
            message="Now add error handling to the function",
            session_id="chat-session-123",
            project_id="test-project"
        )
        
        # Setup mocks for second message
        mock_service.intent_parser.parse.return_value = ParsedIntent(
            intent_type="refactor_code",
            confidence_score=0.9,
            requirements=["error handling"],
            entities={
                "language": "python",
                "framework": "standard",
                "purpose": "add error handling"
            },
            constraints=[],
            context_hints=[]
        )
        
        mock_service.context_aggregator.aggregate_context.return_value = UnifiedContext(
            project_structure={"src": ["math.py"]},
            requirements=["Error handling for addition function"],
            architecture={"style": "monolithic"},
            dependencies={},
            quality_score=0.8
        )
        
        mock_service.code_generator.generate_code.return_value = GeneratedCode(
            code="def add(a, b):\n    try:\n        return a + b\n    except TypeError:\n        raise ValueError('Invalid input types')",
            language="python",
            framework="standard",
            file_path="src/math.py",
            dependencies=[],
            quality_score=0.9,
            execution_time=0.8
        )
        
        mock_service.sandbox_service.execute_code.return_value = SandboxExecutionResponse(
            execution_id="test-execution-287",
            success=True,
            language="python",
            execution_type=ExecutionType.RUN,
            exit_code=0,
            stdout="Function updated with error handling",
            stderr="",
            execution_time=0.2,
            memory_usage_mb=12.0,
            cpu_usage_percent=25.0,
            test_results=TestResult(
                test_name="test_execution",
                passed=True,
                execution_time=0.2
            ),
            passed_tests=["test_passed"],
            failed_tests=[],
            security_scan_passed=True,
            security_violations=[],
            performance_results=None
        )
        
        response2 = await mock_service.chat(chat_request2)
        
        # Verify both responses
        assert response1.success is True
        assert response2.success is True
        assert response1.session_id == response2.session_id
        assert len(response2.generated_code.code) >= len(response1.generated_code.code)
    
    @pytest.mark.asyncio
    async def test_chat_interface_error_handling(self, mock_service):
        """Test chat interface error handling."""
        chat_request = ChatRequest(
            message="Create a broken function",
            session_id="chat-session-123",
            project_id="test-project"
        )
        
        # Mock error
        mock_service.intent_parser.parse.side_effect = Exception("Intent parsing failed")
        
        # Execute chat and expect error
        with pytest.raises(VibeCodingError, match="Chat processing failed"):
            await mock_service.chat(chat_request)


class TestVibeCodingServiceSessionManagement:
    """Test session management functionality."""
    
    @pytest.fixture
    def mock_service(self):
        """Create a mock service with mocked components."""
        service = VibeCodingService()
        service.intent_parser = AsyncMock()
        service.context_aggregator = AsyncMock()
        service.code_generator = AsyncMock()
        service.sandbox_service = AsyncMock()
        service.metrics = Mock()
        service.logger = Mock()
        return service
    
    @pytest.mark.asyncio
    async def test_get_session_status(self, mock_service):
        """Test getting session status."""
        session_id = "test-session-123"
        
        # Mock session data
        mock_service._sessions = {
            session_id: {
                "status": "completed",
                "progress": 100,
                "current_stage": "execution",
                "stages_completed": ["intent_parsing", "context_aggregation", "code_generation", "execution"],
                "created_at": datetime.now() - timedelta(minutes=5),
                "updated_at": datetime.now(),
                "result": {
                    "success": True,
                    "generated_code": "def add(a, b): return a + b",
                    "execution_result": {"success": True, "output": "Function created"}
                }
            }
        }
        
        status = await mock_service.get_session_status(session_id)
        
        # Verify session status
        assert status is not None
        assert status.session_id == session_id
        assert status.status == "completed"
        assert status.progress == 100
        assert status.current_stage == "execution"
        assert len(status.stages_completed) == 4
    
    @pytest.mark.asyncio
    async def test_get_session_status_not_found(self, mock_service):
        """Test getting status for non-existent session."""
        session_id = "non-existent-session"
        
        with pytest.raises(SessionNotFoundError, match="Session not found"):
            await mock_service.get_session_status(session_id)
    
    @pytest.mark.asyncio
    async def test_submit_feedback(self, mock_service):
        """Test submitting feedback."""
        feedback_request = FeedbackRequest(
            session_id="test-session-123",
            feedback_type="rating",
            rating=5,
            comments="Great code generation!",
            suggestions=["Add more error handling"]
        )
        
        # Mock session data
        mock_service._sessions = {
            "test-session-123": {
                "status": "completed",
                "progress": 100,
                "current_stage": "execution",
                "stages_completed": ["intent_parsing", "context_aggregation", "code_generation", "execution"],
                "created_at": datetime.now() - timedelta(minutes=5),
                "updated_at": datetime.now(),
                "result": {
                    "success": True,
                    "generated_code": "def add(a, b): return a + b",
                    "execution_result": {"success": True, "output": "Function created"}
                }
            }
        }
        
        response = await mock_service.submit_feedback(feedback_request)
        
        # Verify feedback response
        assert response is not None
        assert response.success is True
        assert response.message == "Feedback submitted successfully"
        assert response.session_id == feedback_request.session_id
    
    @pytest.mark.asyncio
    async def test_submit_feedback_session_not_found(self, mock_service):
        """Test submitting feedback for non-existent session."""
        feedback_request = FeedbackRequest(
            session_id="non-existent-session",
            feedback_type="rating",
            rating=5,
            comments="Great code generation!"
        )
        
        with pytest.raises(SessionNotFoundError, match="Session not found"):
            await mock_service.submit_feedback(feedback_request)
