"""
Pytest configuration and fixtures for ArchMesh backend tests.
"""

import asyncio
import pytest
import pytest_asyncio
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock, patch

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from httpx import AsyncClient

from app.main import app
from app.core.database import get_db, Base
from app.config import settings


# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def test_db() -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    # Create test engine
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        yield session
    
    # Clean up
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture
def override_get_db(test_db: AsyncSession):
    """Override the database dependency for testing."""
    async def _override_get_db():
        yield test_db
    
    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def client(override_get_db) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def mock_llm():
    """Mock LLM for testing."""
    mock_llm = AsyncMock()
    mock_response = MagicMock()
    mock_response.content = '{"test": "response"}'
    mock_llm.ainvoke.return_value = mock_response
    return mock_llm


@pytest.fixture
def mock_deepseek_client():
    """Mock DeepSeek client for testing."""
    with patch('app.core.deepseek_client.ChatDeepSeek') as mock:
        mock_instance = AsyncMock()
        mock_instance.agenerate.return_value = MagicMock()
        mock_instance.agenerate.return_value.generations = [MagicMock()]
        mock_instance.agenerate.return_value.generations[0].text = '{"test": "response"}'
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def sample_project_data():
    """Sample project data for testing."""
    return {
        "name": "Test Project",
        "description": "A test project for unit testing",
        "domain": "cloud-native",
        "status": "pending"
    }


@pytest.fixture
def sample_workflow_data():
    """Sample workflow data for testing."""
    return {
        "project_id": "test-project-id",
        "current_stage": "starting",
        "state_data": {
            "current_stage": "starting",
            "stage_progress": 0.0,
            "completed_stages": [],
            "stage_results": {},
            "pending_tasks": ["parse_requirements"],
            "errors": [],
            "metadata": {
                "document_path": "/test/path/document.txt",
                "domain": "cloud-native",
                "project_context": "Test context"
            }
        }
    }


@pytest.fixture
def sample_requirements_data():
    """Sample requirements data for testing."""
    return {
        "structured_requirements": {
            "business_goals": ["Launch online marketplace", "Increase revenue"],
            "functional_requirements": ["User registration", "Product listing"],
            "non_functional_requirements": {
                "performance": ["Handle 1000 concurrent users"],
                "security": ["Encrypt user data"],
                "scalability": ["Auto-scale based on load"]
            },
            "constraints": ["Budget: $50k", "Timeline: 6 months"],
            "stakeholders": ["Product Manager", "Development Team"]
        },
        "clarification_questions": [
            {
                "question": "What is the expected user load?",
                "category": "performance",
                "priority": 1,
                "rationale": "Need to understand scalability requirements"
            }
        ],
        "identified_gaps": ["Missing payment integration details"],
        "confidence_score": 0.8
    }


@pytest.fixture
def sample_architecture_data():
    """Sample architecture data for testing."""
    return {
        "overview": "Microservices-based e-commerce platform",
        "technology_stack": ["Node.js", "PostgreSQL", "Redis", "Docker"],
        "components": [
            {
                "name": "User Service",
                "description": "Handles user authentication and profile management",
                "technology": "Node.js + Express"
            },
            {
                "name": "Product Service", 
                "description": "Manages product catalog and inventory",
                "technology": "Node.js + Express"
            }
        ],
        "security_considerations": [
            "JWT-based authentication",
            "HTTPS encryption",
            "Input validation"
        ],
        "scalability_approach": [
            "Horizontal scaling with load balancers",
            "Database read replicas",
            "Caching with Redis"
        ],
        "implementation_roadmap": [
            {
                "phase": 1,
                "description": "Core user and product services",
                "duration": "2 months"
            },
            {
                "phase": 2,
                "description": "Payment and order management",
                "duration": "2 months"
            }
        ],
        "c4_diagrams": {
            "system_context": "```mermaid\ngraph TB\n    User[User] --> System[E-commerce System]\n```",
            "container": "```mermaid\ngraph TB\n    User[User] --> LB[Load Balancer]\n    LB --> US[User Service]\n    LB --> PS[Product Service]\n```"
        }
    }
