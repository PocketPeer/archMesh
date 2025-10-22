# Test Execution Plan for ArchMesh

## Overview

This document provides a detailed execution plan for implementing the comprehensive test strategy, establishing a solid baseline for TDD development.

## Phase 1: Test Infrastructure Setup (Week 1)

### 1.1 Backend Test Infrastructure

#### Test Configuration
```python
# backend/pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --strict-markers
    --strict-config
    --cov=app
    --cov-report=html
    --cov-report=xml
    --cov-report=term-missing
    --cov-fail-under=90
    --maxfail=5
    --tb=short
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow running tests
    llm: Tests requiring LLM calls
    database: Tests requiring database
    redis: Tests requiring Redis
    neo4j: Tests requiring Neo4j
    pinecone: Tests requiring Pinecone
```

#### Test Environment Setup
```python
# backend/tests/conftest.py
import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.core.redis_client import RedisClient
from app.services.knowledge_base_service import KnowledgeBaseService

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_db():
    """Create test database."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()

@pytest.fixture
async def db_session(test_db):
    """Create database session for tests."""
    async_session = sessionmaker(test_db, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session

@pytest.fixture
async def redis_client():
    """Create Redis client for tests."""
    client = RedisClient("redis://localhost:6380/1")
    yield client
    await client.close()

@pytest.fixture
async def knowledge_base_service():
    """Create knowledge base service for tests."""
    service = KnowledgeBaseService()
    yield service
    await service.close()
```

### 1.2 Frontend Test Infrastructure

#### Test Configuration
```javascript
// frontend/jest.config.js
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
    '^@/components/(.*)$': '<rootDir>/components/$1',
    '^@/lib/(.*)$': '<rootDir>/lib/$1',
    '^@/types/(.*)$': '<rootDir>/types/$1',
  },
  collectCoverageFrom: [
    'src/**/*.{ts,tsx}',
    'components/**/*.{ts,tsx}',
    'lib/**/*.{ts,tsx}',
    '!**/*.d.ts',
    '!**/node_modules/**',
  ],
  coverageThreshold: {
    global: {
      branches: 85,
      functions: 85,
      lines: 85,
      statements: 85,
    },
  },
  testMatch: [
    '<rootDir>/__tests__/**/*.{ts,tsx}',
    '<rootDir>/src/**/__tests__/**/*.{ts,tsx}',
    '<rootDir>/components/**/__tests__/**/*.{ts,tsx}',
  ],
  transform: {
    '^.+\\.(ts|tsx)$': 'ts-jest',
  },
  moduleFileExtensions: ['ts', 'tsx', 'js', 'jsx', 'json'],
};
```

#### Test Setup
```javascript
// frontend/jest.setup.js
import '@testing-library/jest-dom';
import { TextEncoder, TextDecoder } from 'util';

// Polyfills for Node.js environment
global.TextEncoder = TextEncoder;
global.TextDecoder = TextDecoder;

// Mock Next.js router
jest.mock('next/router', () => ({
  useRouter() {
    return {
      route: '/',
      pathname: '/',
      query: {},
      asPath: '/',
      push: jest.fn(),
      pop: jest.fn(),
      reload: jest.fn(),
      back: jest.fn(),
      prefetch: jest.fn(),
      beforePopState: jest.fn(),
      events: {
        on: jest.fn(),
        off: jest.fn(),
        emit: jest.fn(),
      },
    };
  },
}));

// Mock API client
jest.mock('@/lib/api-client', () => ({
  apiClient: {
    getProjects: jest.fn(),
    createProject: jest.fn(),
    updateProject: jest.fn(),
    deleteProject: jest.fn(),
    listWorkflows: jest.fn(),
    getWorkflowStatus: jest.fn(),
    startArchitectureWorkflow: jest.fn(),
    submitReview: jest.fn(),
    getHealth: jest.fn(),
    analyzeRepository: jest.fn(),
    updateProjectMode: jest.fn(),
    approveIntegration: jest.fn(),
    rejectIntegration: jest.fn(),
  },
}));
```

## Phase 2: Unit Test Implementation (Week 2-3)

### 2.1 Backend Unit Tests

#### Agent Tests
```python
# backend/tests/unit/test_requirements_agent.py
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.agents.requirements_agent import RequirementsAgent
from app.core.error_handling import LLMProviderError

class TestRequirementsAgent:
    @pytest.fixture
    def agent(self):
        return RequirementsAgent()

    @pytest.mark.unit
    async def test_extract_requirements_success(self, agent):
        """Test successful requirements extraction."""
        # Arrange
        mock_response = {
            "structured_requirements": {
                "business_goals": ["Goal 1", "Goal 2"],
                "functional_requirements": ["Req 1", "Req 2"],
                "non_functional_requirements": {
                    "performance": ["Perf 1"],
                    "security": ["Sec 1"],
                },
                "constraints": ["Constraint 1"],
                "stakeholders": ["Stakeholder 1"],
            },
            "clarification_questions": [
                {
                    "question": "What is the expected load?",
                    "category": "performance",
                    "priority": 1,
                    "rationale": "Need to understand scalability",
                }
            ],
            "identified_gaps": ["Gap 1"],
            "confidence_score": 0.8,
        }
        
        with patch.object(agent, '_call_llm', return_value=json.dumps(mock_response)):
            # Act
            result = await agent.execute({
                "document_path": "/test/path/document.txt",
                "domain": "cloud-native",
            })
            
            # Assert
            assert result["structured_requirements"]["business_goals"] == ["Goal 1", "Goal 2"]
            assert result["confidence_score"] == 0.8
            assert "metadata" in result

    @pytest.mark.unit
    async def test_extract_requirements_llm_timeout(self, agent):
        """Test LLM timeout handling."""
        with patch.object(agent, '_call_llm', side_effect=LLMProviderError("Timeout")):
            with pytest.raises(LLMProviderError):
                await agent.execute({
                    "document_path": "/test/path/document.txt",
                    "domain": "cloud-native",
                })

    @pytest.mark.unit
    async def test_extract_requirements_invalid_json(self, agent):
        """Test invalid JSON response handling."""
        with patch.object(agent, '_call_llm', return_value="invalid json"):
            with pytest.raises(ValueError, match="Could not parse JSON"):
                await agent.execute({
                    "document_path": "/test/path/document.txt",
                    "domain": "cloud-native",
                })
```

#### Service Tests
```python
# backend/tests/unit/test_knowledge_base_service.py
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.knowledge_base_service import KnowledgeBaseService

class TestKnowledgeBaseService:
    @pytest.fixture
    def service(self):
        return KnowledgeBaseService()

    @pytest.mark.unit
    async def test_index_repository_analysis_success(self, service):
        """Test successful repository analysis indexing."""
        # Arrange
        analysis_data = {
            "repository_info": {
                "name": "test-repo",
                "url": "https://github.com/test/repo",
                "tech_stack": ["Python", "FastAPI"],
            },
            "architecture": {
                "services": ["api", "database"],
                "dependencies": ["redis", "postgresql"],
            },
        }
        
        with patch.object(service, '_generate_embedding', return_value=[0.1, 0.2, 0.3]):
            with patch.object(service, 'index') as mock_index:
                mock_index.upsert.return_value = {"upserted_count": 1}
                
                # Act
                result = await service.index_repository_analysis("project-1", analysis_data)
                
                # Assert
                assert result["indexed_chunks"] > 0
                assert result["project_id"] == "project-1"
                mock_index.upsert.assert_called_once()

    @pytest.mark.unit
    async def test_search_similar_architectures_success(self, service):
        """Test successful architecture search."""
        # Arrange
        query = "microservices architecture"
        filters = {"tech_stack": ["Python", "FastAPI"]}
        
        mock_results = [
            {
                "id": "chunk-1",
                "score": 0.95,
                "metadata": {
                    "project_id": "project-1",
                    "chunk_type": "architecture",
                    "tech_stack": ["Python", "FastAPI"],
                },
            }
        ]
        
        with patch.object(service, '_generate_embedding', return_value=[0.1, 0.2, 0.3]):
            with patch.object(service, 'index') as mock_index:
                mock_index.query.return_value = {"matches": mock_results}
                
                # Act
                result = await service.search_similar_architectures(query, filters)
                
                # Assert
                assert len(result) == 1
                assert result[0]["score"] == 0.95
                assert result[0]["metadata"]["project_id"] == "project-1"
```

### 2.2 Frontend Unit Tests

#### Component Tests
```typescript
// frontend/__tests__/components/ArchitectureVisualizer.test.tsx
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ArchitectureVisualizer } from '@/components/architecture/ArchitectureVisualizer';
import { ArchitectureGraph } from '@/types/architecture';

describe('ArchitectureVisualizer', () => {
  const mockArchitecture: ArchitectureGraph = {
    services: [
      {
        id: 'service-1',
        name: 'API Service',
        type: 'api',
        status: 'healthy',
        technologies: ['Python', 'FastAPI'],
        dependencies: ['service-2'],
        metadata: {
          description: 'Main API service',
          version: '1.0.0',
        },
      },
      {
        id: 'service-2',
        name: 'Database',
        type: 'database',
        status: 'healthy',
        technologies: ['PostgreSQL'],
        dependencies: [],
        metadata: {
          description: 'Primary database',
          version: '13.0',
        },
      },
    ],
    dependencies: [
      {
        id: 'dep-1',
        source: 'service-1',
        target: 'service-2',
        type: 'database',
        metadata: {
          description: 'Database connection',
        },
      },
    ],
  };

  it('renders architecture graph correctly', () => {
    render(<ArchitectureVisualizer architecture={mockArchitecture} />);
    
    expect(screen.getByText('API Service')).toBeInTheDocument();
    expect(screen.getByText('Database')).toBeInTheDocument();
  });

  it('handles zoom in/out interactions', async () => {
    render(<ArchitectureVisualizer architecture={mockArchitecture} />);
    
    const zoomInButton = screen.getByLabelText('Zoom In');
    const zoomOutButton = screen.getByLabelText('Zoom Out');
    
    fireEvent.click(zoomInButton);
    fireEvent.click(zoomOutButton);
    
    // Verify zoom state changes
    await waitFor(() => {
      expect(screen.getByTestId('architecture-graph')).toBeInTheDocument();
    });
  });

  it('exports architecture data correctly', async () => {
    const mockOnExport = jest.fn();
    render(
      <ArchitectureVisualizer 
        architecture={mockArchitecture} 
        onExport={mockOnExport}
      />
    );
    
    const exportButton = screen.getByLabelText('Export');
    fireEvent.click(exportButton);
    
    await waitFor(() => {
      expect(mockOnExport).toHaveBeenCalledWith('json');
    });
  });

  it('displays error state when architecture is invalid', () => {
    const invalidArchitecture = { services: [], dependencies: [] };
    render(<ArchitectureVisualizer architecture={invalidArchitecture} />);
    
    expect(screen.getByText('No architecture data available')).toBeInTheDocument();
  });
});
```

#### Hook Tests
```typescript
// frontend/__tests__/hooks/useArchitectureGraph.test.ts
import { renderHook, act } from '@testing-library/react';
import { useArchitectureGraph } from '@/hooks/useArchitectureGraph';
import { ArchitectureGraph } from '@/types/architecture';

describe('useArchitectureGraph', () => {
  const mockArchitecture: ArchitectureGraph = {
    services: [
      {
        id: 'service-1',
        name: 'API Service',
        type: 'api',
        status: 'healthy',
        technologies: ['Python'],
        dependencies: [],
        metadata: {},
      },
    ],
    dependencies: [],
  };

  it('initializes with provided architecture', () => {
    const { result } = renderHook(() => useArchitectureGraph(mockArchitecture));
    
    expect(result.current.architecture).toEqual(mockArchitecture);
    expect(result.current.zoomLevel).toBe('system');
  });

  it('updates zoom level correctly', () => {
    const { result } = renderHook(() => useArchitectureGraph(mockArchitecture));
    
    act(() => {
      result.current.setZoomLevel('service');
    });
    
    expect(result.current.zoomLevel).toBe('service');
  });

  it('filters services by zoom level', () => {
    const { result } = renderHook(() => useArchitectureGraph(mockArchitecture));
    
    act(() => {
      result.current.setZoomLevel('component');
    });
    
    expect(result.current.filteredServices).toHaveLength(0);
  });
});
```

## Phase 3: Integration Test Implementation (Week 4)

### 3.1 Backend Integration Tests

#### API Integration Tests
```python
# backend/tests/integration/test_workflow_api.py
import pytest
from httpx import AsyncClient
from app.main import app

class TestWorkflowAPI:
    @pytest.mark.integration
    async def test_start_architecture_workflow_success(self, client: AsyncClient):
        """Test successful workflow start."""
        # Arrange
        with open("sample-docs/sample-requirements.txt", "rb") as f:
            files = {"file": ("requirements.txt", f, "text/plain")}
            data = {
                "project_id": "test-project-1",
                "domain": "cloud-native",
                "project_context": "Test project",
                "llm_provider": "deepseek",
            }
            
            # Act
            response = await client.post("/api/v1/workflows/start-architecture", files=files, data=data)
            
            # Assert
            assert response.status_code == 201
            result = response.json()
            assert "session_id" in result
            assert result["workflow_status"]["current_stage"] == "starting"

    @pytest.mark.integration
    async def test_get_workflow_status_success(self, client: AsyncClient):
        """Test successful workflow status retrieval."""
        # Arrange
        session_id = "test-session-1"
        
        # Act
        response = await client.get(f"/api/v1/workflows/{session_id}/status")
        
        # Assert
        assert response.status_code == 200
        result = response.json()
        assert result["session_id"] == session_id
        assert "current_stage" in result
        assert "state_data" in result
```

#### Database Integration Tests
```python
# backend/tests/integration/test_database_operations.py
import pytest
from app.models.project import Project
from app.models.workflow import WorkflowSession

class TestDatabaseOperations:
    @pytest.mark.integration
    @pytest.mark.database
    async def test_project_crud_operations(self, db_session):
        """Test project CRUD operations."""
        # Create
        project = Project(
            name="Test Project",
            description="Test Description",
            domain="cloud-native",
            status="active",
        )
        db_session.add(project)
        await db_session.commit()
        
        # Read
        retrieved_project = await db_session.get(Project, project.id)
        assert retrieved_project.name == "Test Project"
        
        # Update
        retrieved_project.description = "Updated Description"
        await db_session.commit()
        
        # Delete
        await db_session.delete(retrieved_project)
        await db_session.commit()
        
        # Verify deletion
        deleted_project = await db_session.get(Project, project.id)
        assert deleted_project is None
```

### 3.2 Frontend Integration Tests

#### Page Integration Tests
```typescript
// frontend/__tests__/pages/ProjectDetailPage.test.tsx
import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { ProjectDetailPage } from '@/app/projects/[id]/page';
import { apiClient } from '@/lib/api-client';

// Mock the API client
jest.mock('@/lib/api-client');

describe('ProjectDetailPage', () => {
  const mockProject = {
    id: 'project-1',
    name: 'Test Project',
    description: 'Test Description',
    domain: 'cloud-native',
    status: 'active',
    created_at: '2023-01-01T00:00:00Z',
    updated_at: '2023-01-01T00:00:00Z',
  };

  const mockWorkflows = [
    {
      session_id: 'workflow-1',
      project_id: 'project-1',
      current_stage: 'completed',
      is_active: true,
      started_at: '2023-01-01T00:00:00Z',
    },
  ];

  beforeEach(() => {
    (apiClient.getProject as jest.Mock).mockResolvedValue(mockProject);
    (apiClient.listWorkflows as jest.Mock).mockResolvedValue(mockWorkflows);
  });

  it('renders project details correctly', async () => {
    render(<ProjectDetailPage params={{ id: 'project-1' }} />);
    
    await waitFor(() => {
      expect(screen.getByText('Test Project')).toBeInTheDocument();
      expect(screen.getByText('Test Description')).toBeInTheDocument();
    });
  });

  it('displays workflow status correctly', async () => {
    render(<ProjectDetailPage params={{ id: 'project-1' }} />);
    
    await waitFor(() => {
      expect(screen.getByText('completed')).toBeInTheDocument();
    });
  });

  it('handles mode switching correctly', async () => {
    render(<ProjectDetailPage params={{ id: 'project-1' }} />);
    
    await waitFor(() => {
      const brownfieldMode = screen.getByText('Brownfield');
      fireEvent.click(brownfieldMode);
      
      expect(screen.getByText('GitHub Repository')).toBeInTheDocument();
    });
  });
});
```

## Phase 4: End-to-End Test Implementation (Week 5)

### 4.1 E2E Test Setup

#### Playwright Configuration
```typescript
// frontend/playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
});
```

#### E2E Test Implementation
```typescript
// frontend/e2e/greenfield-workflow.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Greenfield Workflow', () => {
  test('complete greenfield project workflow', async ({ page }) => {
    // Navigate to home page
    await page.goto('/');
    
    // Create new project
    await page.click('text=Create New Project');
    await page.fill('input[name="name"]', 'E-commerce Platform');
    await page.fill('textarea[name="description"]', 'Online marketplace for handmade crafts');
    await page.selectOption('select[name="domain"]', 'cloud-native');
    await page.click('button[type="submit"]');
    
    // Wait for project creation
    await expect(page.locator('text=Project created successfully')).toBeVisible();
    
    // Upload requirements document
    await page.setInputFiles('input[type="file"]', 'sample-docs/sample-requirements.txt');
    await page.click('button:has-text("Upload Document")');
    
    // Wait for upload completion
    await expect(page.locator('text=Document uploaded successfully')).toBeVisible();
    
    // Start architecture workflow
    await page.click('button:has-text("Start Architecture Design")');
    
    // Wait for workflow to start
    await expect(page.locator('text=Workflow started')).toBeVisible();
    
    // Monitor workflow progress
    await page.waitForSelector('text=Requirements Analysis', { timeout: 30000 });
    await page.waitForSelector('text=Architecture Design', { timeout: 60000 });
    
    // Review architecture
    await expect(page.locator('text=Architecture Proposal')).toBeVisible();
    await page.click('button:has-text("Approve")');
    
    // Verify completion
    await expect(page.locator('text=Workflow completed successfully')).toBeVisible();
    
    // Export results
    await page.click('button:has-text("Export")');
    await expect(page.locator('text=Architecture exported')).toBeVisible();
  });
});
```

## Phase 5: Performance and Security Tests (Week 6)

### 5.1 Performance Tests

#### Load Testing
```python
# backend/tests/performance/test_load.py
import pytest
import asyncio
from httpx import AsyncClient
from app.main import app

class TestLoadPerformance:
    @pytest.mark.performance
    @pytest.mark.slow
    async def test_concurrent_workflow_creation(self):
        """Test concurrent workflow creation performance."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Create 10 concurrent workflow requests
            tasks = []
            for i in range(10):
                task = client.post("/api/v1/workflows/start-architecture", json={
                    "project_id": f"project-{i}",
                    "domain": "cloud-native",
                    "project_context": f"Test project {i}",
                })
                tasks.append(task)
            
            # Execute all requests concurrently
            start_time = asyncio.get_event_loop().time()
            responses = await asyncio.gather(*tasks)
            end_time = asyncio.get_event_loop().time()
            
            # Verify all requests succeeded
            for response in responses:
                assert response.status_code == 201
            
            # Verify performance (should complete within 30 seconds)
            assert (end_time - start_time) < 30.0
```

### 5.2 Security Tests

#### Security Test Implementation
```python
# backend/tests/security/test_security.py
import pytest
from httpx import AsyncClient
from app.main import app

class TestSecurity:
    @pytest.mark.security
    async def test_sql_injection_protection(self, client: AsyncClient):
        """Test SQL injection protection."""
        malicious_input = "'; DROP TABLE projects; --"
        
        response = await client.post("/api/v1/projects/", json={
            "name": malicious_input,
            "description": "Test",
            "domain": "cloud-native",
        })
        
        # Should not cause database error
        assert response.status_code in [400, 422]  # Validation error, not server error

    @pytest.mark.security
    async def test_file_upload_security(self, client: AsyncClient):
        """Test malicious file upload protection."""
        # Create a fake executable file
        malicious_content = b"MZ\x90\x00"  # PE header
        files = {"file": ("malicious.exe", malicious_content, "application/octet-stream")}
        
        response = await client.post("/api/v1/workflows/start-architecture", files=files, data={
            "project_id": "test-project",
            "domain": "cloud-native",
        })
        
        # Should reject non-text files
        assert response.status_code == 400
```

## Phase 6: Test Automation and CI/CD (Week 7)

### 6.1 GitHub Actions Workflow

```yaml
# .github/workflows/test.yml
name: Test Suite

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: archmesh_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
      
      redis:
        image: redis:6
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        cd backend
        pip install -r requirements.txt
        pip install -r requirements-test.txt
    
    - name: Run unit tests
      run: |
        cd backend
        pytest tests/unit -v --cov=app --cov-report=xml --cov-report=html
    
    - name: Run integration tests
      run: |
        cd backend
        pytest tests/integration -v
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./backend/coverage.xml
        flags: backend
        name: backend-coverage

  frontend-tests:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        cache: 'npm'
        cache-dependency-path: frontend/package-lock.json
    
    - name: Install dependencies
      run: |
        cd frontend
        npm ci
    
    - name: Run unit tests
      run: |
        cd frontend
        npm test -- --coverage --watchAll=false
    
    - name: Run integration tests
      run: |
        cd frontend
        npm run test:integration
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./frontend/coverage/lcov.info
        flags: frontend
        name: frontend-coverage

  e2e-tests:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        cache: 'npm'
        cache-dependency-path: frontend/package-lock.json
    
    - name: Install dependencies
      run: |
        cd frontend
        npm ci
    
    - name: Install Playwright Browsers
      run: |
        cd frontend
        npx playwright install --with-deps
    
    - name: Run E2E tests
      run: |
        cd frontend
        npm run test:e2e
    
    - uses: actions/upload-artifact@v3
      if: always()
      with:
        name: playwright-report
        path: frontend/playwright-report/
        retention-days: 30

  performance-tests:
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        cd backend
        pip install -r requirements.txt
        pip install -r requirements-test.txt
    
    - name: Run performance tests
      run: |
        cd backend
        pytest tests/performance -v --tb=short
```

## Phase 7: Test Monitoring and Reporting (Week 8)

### 7.1 Test Metrics Dashboard

```python
# backend/tests/monitoring/test_metrics.py
import pytest
from datetime import datetime, timedelta
from app.core.test_metrics import TestMetrics

class TestMetrics:
    def __init__(self):
        self.metrics = {
            'test_execution_time': [],
            'coverage_percentage': [],
            'failure_rate': [],
            'flaky_tests': [],
        }
    
    def record_test_execution(self, test_name: str, duration: float, status: str):
        """Record test execution metrics."""
        self.metrics['test_execution_time'].append({
            'test_name': test_name,
            'duration': duration,
            'status': status,
            'timestamp': datetime.now(),
        })
    
    def get_coverage_trend(self, days: int = 30):
        """Get coverage trend over specified days."""
        cutoff_date = datetime.now() - timedelta(days=days)
        return [
            metric for metric in self.metrics['coverage_percentage']
            if metric['timestamp'] >= cutoff_date
        ]
    
    def get_failure_rate(self, days: int = 7):
        """Get failure rate over specified days."""
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_tests = [
            metric for metric in self.metrics['test_execution_time']
            if metric['timestamp'] >= cutoff_date
        ]
        
        if not recent_tests:
            return 0.0
        
        failed_tests = [test for test in recent_tests if test['status'] == 'failed']
        return len(failed_tests) / len(recent_tests)
```

### 7.2 Automated Test Reporting

```python
# backend/scripts/generate_test_report.py
import json
import datetime
from pathlib import Path
from app.core.test_metrics import TestMetrics

def generate_test_report():
    """Generate comprehensive test report."""
    metrics = TestMetrics()
    
    report = {
        'generated_at': datetime.datetime.now().isoformat(),
        'summary': {
            'total_tests': len(metrics.metrics['test_execution_time']),
            'coverage_percentage': metrics.get_latest_coverage(),
            'failure_rate': metrics.get_failure_rate(),
            'flaky_tests_count': len(metrics.metrics['flaky_tests']),
        },
        'trends': {
            'coverage_trend': metrics.get_coverage_trend(),
            'execution_time_trend': metrics.get_execution_time_trend(),
        },
        'recommendations': generate_recommendations(metrics),
    }
    
    # Save report
    report_path = Path('reports/test-report.json')
    report_path.parent.mkdir(exist_ok=True)
    
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    return report

def generate_recommendations(metrics):
    """Generate test improvement recommendations."""
    recommendations = []
    
    if metrics.get_failure_rate() > 0.05:
        recommendations.append("High failure rate detected. Review failing tests.")
    
    if metrics.get_latest_coverage() < 90:
        recommendations.append("Coverage below 90%. Add more tests.")
    
    if len(metrics.metrics['flaky_tests']) > 0:
        recommendations.append("Flaky tests detected. Investigate and fix.")
    
    return recommendations
```

## Execution Timeline

| Week | Phase | Focus | Deliverables |
|------|-------|-------|--------------|
| 1 | Infrastructure | Test setup and configuration | Test frameworks, CI/CD pipeline |
| 2-3 | Unit Tests | Core component testing | 90%+ unit test coverage |
| 4 | Integration Tests | Component interaction testing | API and database integration tests |
| 5 | E2E Tests | User journey testing | Critical path E2E tests |
| 6 | Performance & Security | Non-functional testing | Load tests, security tests |
| 7 | Automation | CI/CD integration | Automated test execution |
| 8 | Monitoring | Test metrics and reporting | Test dashboard, reporting system |

## Success Criteria

### Coverage Targets
- **Backend Unit Tests**: 90%+ code coverage
- **Frontend Unit Tests**: 85%+ code coverage
- **Integration Tests**: 100% API endpoint coverage
- **E2E Tests**: 100% critical user journey coverage

### Quality Gates
- **All Tests Pass**: No failing tests in CI/CD
- **Performance Benchmarks**: Response times within acceptable limits
- **Security Scans**: No critical vulnerabilities
- **Test Stability**: <5% flaky test rate

### Maintenance Standards
- **Test Review**: All new tests reviewed before merge
- **Documentation**: Test documentation updated with code changes
- **Refactoring**: Tests refactored with code changes
- **Training**: Team trained on testing best practices

## Conclusion

This comprehensive test execution plan provides a structured approach to implementing the test strategy, ensuring:

1. **Solid Foundation**: Robust test infrastructure and tooling
2. **Comprehensive Coverage**: All layers of the application tested
3. **Quality Assurance**: High-quality, maintainable test code
4. **Automation**: Fully automated test execution and reporting
5. **Continuous Improvement**: Metrics-driven test quality improvement

The plan establishes a strong baseline for TDD development, enabling confident feature development and reliable releases.
