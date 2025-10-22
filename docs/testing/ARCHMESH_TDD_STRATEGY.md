# ArchMesh TDD Strategy - Project-Specific Implementation

## Executive Summary

This document provides a comprehensive Test-Driven Development (TDD) strategy specifically tailored for the ArchMesh project, based on analysis of the current codebase structure, existing test infrastructure, and project requirements.

## Current Project Analysis

### 🏗️ Project Architecture
- **Backend**: FastAPI with SQLAlchemy, Redis, LangChain agents
- **Frontend**: Next.js 15 with React 19, TypeScript, Tailwind CSS
- **AI Integration**: DeepSeek, OpenAI, Anthropic via LangChain
- **Database**: PostgreSQL with Alembic migrations
- **Testing**: pytest (backend), Jest + React Testing Library (frontend)

### 📊 Current Test Status
- **Backend Tests**: 607 tests collected across multiple categories
- **Frontend Tests**: 8 test files with component and integration tests
- **Coverage**: Currently at ~67% backend, improving with recent additions
- **Test Categories**: Unit, Integration, E2E, Performance, Security

### 🎯 Key Components Requiring TDD Focus
1. **AI Agents** (`app/agents/`): RequirementsAgent, ArchitectureAgent, GitHubAnalyzerAgent
2. **Core Services** (`app/core/`): LLM clients, database, Redis, file storage
3. **API Endpoints** (`app/api/`): RESTful APIs with authentication
4. **Workflows** (`app/workflows/`): LangGraph-based workflow orchestration
5. **Frontend Components**: React components with complex state management

## ArchMesh-Specific TDD Implementation

### 1. TDD Workflow for AI Agents

#### Red-Green-Refactor for Agent Development
```python
# RED: Write failing test first
def test_requirements_agent_extract_requirements_success():
    """Test successful requirements extraction from document"""
    agent = RequirementsAgent()
    document_path = "test_requirements.txt"
    
    result = agent.execute(document_path)
    
    assert result["success"] is True
    assert "requirements" in result["data"]
    assert len(result["data"]["requirements"]) > 0
    assert result["confidence_score"] > 0.8

# GREEN: Implement minimal code
class RequirementsAgent(BaseAgent):
    def execute(self, document_path: str) -> Dict:
        # Minimal implementation to make test pass
        return {
            "success": True,
            "data": {"requirements": ["Sample requirement"]},
            "confidence_score": 0.9
        }

# REFACTOR: Improve while keeping tests green
class RequirementsAgent(BaseAgent):
    def execute(self, document_path: str) -> Dict:
        try:
            content = self._read_document(document_path)
            requirements = self._extract_requirements(content)
            confidence = self._calculate_confidence(requirements)
            
            return {
                "success": True,
                "data": {"requirements": requirements},
                "confidence_score": confidence
            }
        except Exception as e:
            return self._handle_error(e)
```

#### Agent-Specific Test Patterns
```python
class TestRequirementsAgent:
    """TDD tests for RequirementsAgent"""
    
    @pytest.fixture
    def agent(self):
        return RequirementsAgent()
    
    @pytest.fixture
    def sample_document(self, tmp_path):
        """Create sample requirements document"""
        doc_path = tmp_path / "requirements.txt"
        doc_path.write_text("The system shall process user data securely")
        return str(doc_path)
    
    def test_extract_requirements_success(self, agent, sample_document):
        """RED: Test successful extraction"""
        result = agent.execute(sample_document)
        assert result["success"] is True
    
    def test_extract_requirements_empty_document(self, agent, tmp_path):
        """RED: Test empty document handling"""
        empty_doc = tmp_path / "empty.txt"
        empty_doc.write_text("")
        
        result = agent.execute(str(empty_doc))
        assert result["success"] is False
        assert "error" in result
    
    def test_extract_requirements_llm_timeout(self, agent, sample_document):
        """RED: Test LLM timeout handling"""
        with patch.object(agent, '_call_llm', side_effect=TimeoutError):
            result = agent.execute(sample_document)
            assert result["success"] is False
            assert "timeout" in result["error"].lower()
```

### 2. TDD for API Endpoints

#### API-First TDD Approach
```python
# RED: Write API test first
def test_create_project_endpoint_success(client, sample_project_data):
    """Test successful project creation via API"""
    response = client.post("/api/v1/projects", json=sample_project_data)
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == sample_project_data["name"]
    assert "id" in data
    assert data["status"] == "processing"

# GREEN: Implement minimal endpoint
@app.post("/api/v1/projects")
async def create_project(project_data: ProjectCreate):
    return {
        "id": "temp-id",
        "name": project_data.name,
        "status": "processing"
    }

# REFACTOR: Add database integration, validation, etc.
@app.post("/api/v1/projects")
async def create_project(
    project_data: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = Project(
        name=project_data.name,
        description=project_data.description,
        owner_id=current_user.id
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)
    
    return project
```

### 3. TDD for Frontend Components

#### Component-First TDD
```typescript
// RED: Write component test first
describe('DocumentUploader', () => {
  it('should upload document successfully', async () => {
    const mockOnUpload = jest.fn();
    render(<DocumentUploader onUploadComplete={mockOnUpload} />);
    
    const file = new File(['test content'], 'test.txt', { type: 'text/plain' });
    const input = screen.getByLabelText(/upload/i);
    
    fireEvent.change(input, { target: { files: [file] } });
    
    await waitFor(() => {
      expect(mockOnUpload).toHaveBeenCalledWith(file);
    });
  });
});

// GREEN: Implement minimal component
export function DocumentUploader({ onUploadComplete }: Props) {
  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      onUploadComplete(file);
    }
  };

  return (
    <input
      type="file"
      onChange={handleFileChange}
      aria-label="Upload document"
    />
  );
}

// REFACTOR: Add progress, validation, error handling
export function DocumentUploader({ onUploadComplete }: Props) {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const handleFileChange = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    
    setUploading(true);
    setError(null);
    
    try {
      await uploadFile(file);
      onUploadComplete(file);
    } catch (err) {
      setError('Upload failed');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div>
      <input
        type="file"
        onChange={handleFileChange}
        disabled={uploading}
        aria-label="Upload document"
      />
      {uploading && <div>Uploading...</div>}
      {error && <div role="alert">{error}</div>}
    </div>
  );
}
```

### 4. TDD for Workflow Orchestration

#### Workflow-First TDD
```python
# RED: Write workflow test first
def test_brownfield_workflow_complete_execution():
    """Test complete brownfield workflow execution"""
    workflow = BrownfieldWorkflow()
    initial_state = {
        "repository_url": "https://github.com/test/repo",
        "requirements": "Add user authentication"
    }
    
    result = workflow.execute(initial_state)
    
    assert result["status"] == "completed"
    assert "architecture" in result["data"]
    assert "integration_strategy" in result["data"]

# GREEN: Implement minimal workflow
class BrownfieldWorkflow:
    def execute(self, state: Dict) -> Dict:
        return {
            "status": "completed",
            "data": {
                "architecture": {"services": []},
                "integration_strategy": {"phases": []}
            }
        }

# REFACTOR: Add LangGraph integration, error handling
class BrownfieldWorkflow:
    def __init__(self):
        self.graph = self._build_graph()
    
    def execute(self, state: Dict) -> Dict:
        try:
            result = self.graph.invoke(state)
            return {
                "status": "completed",
                "data": result
            }
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e)
            }
```

## ArchMesh-Specific TDD Guidelines

### 1. AI Agent Testing Patterns

#### Mock External Dependencies
```python
@pytest.fixture
def mock_llm_client():
    """Mock LLM client for agent tests"""
    with patch('app.core.llm_strategy.LLMStrategy.get_llm') as mock:
        mock.return_value.invoke.return_value = "Mocked LLM response"
        yield mock

@pytest.fixture
def mock_knowledge_base():
    """Mock knowledge base for brownfield tests"""
    with patch('app.services.knowledge_base_service.KnowledgeBaseService') as mock:
        mock.return_value.search.return_value = {
            "similar_features": [],
            "existing_patterns": []
        }
        yield mock
```

#### Test LLM Integration
```python
def test_agent_llm_integration(agent, mock_llm_client):
    """Test agent integration with LLM"""
    result = agent.execute("test input")
    
    mock_llm_client.assert_called_once()
    assert result["success"] is True
```

### 2. Database Testing Patterns

#### Use Test Database
```python
@pytest.fixture
async def test_db():
    """Create test database session"""
    async with get_test_db() as session:
        yield session
        await session.rollback()

def test_create_project_with_db(test_db, sample_project_data):
    """Test project creation with database"""
    project = Project(**sample_project_data)
    test_db.add(project)
    await test_db.commit()
    
    assert project.id is not None
    assert project.name == sample_project_data["name"]
```

### 3. Frontend Testing Patterns

#### Mock API Calls
```typescript
// Mock API client
jest.mock('@/lib/api-client', () => ({
  apiClient: {
    get: jest.fn(),
    post: jest.fn(),
    put: jest.fn(),
    delete: jest.fn(),
  },
}));

// Test with mocked API
it('should fetch projects on mount', async () => {
  const mockProjects = [{ id: 1, name: 'Test Project' }];
  (apiClient.get as jest.Mock).mockResolvedValue({ data: mockProjects });
  
  render(<ProjectList />);
  
  await waitFor(() => {
    expect(screen.getByText('Test Project')).toBeInTheDocument();
  });
});
```

## TDD Implementation Roadmap

### Phase 1: Foundation (Week 1-2)
- [ ] Set up TDD infrastructure and tools
- [ ] Create test templates for all component types
- [ ] Establish CI/CD pipeline with TDD gates
- [ ] Train team on ArchMesh-specific TDD patterns

### Phase 2: Core Components (Week 3-4)
- [ ] Implement TDD for all AI agents
- [ ] Add TDD for core services (database, Redis, file storage)
- [ ] Create comprehensive API endpoint tests
- [ ] Establish 90%+ coverage for critical paths

### Phase 3: Integration & E2E (Week 5-6)
- [ ] Implement TDD for workflow orchestration
- [ ] Add integration tests for agent interactions
- [ ] Create E2E tests for complete user journeys
- [ ] Add performance and security testing

### Phase 4: Frontend TDD (Week 7-8)
- [ ] Implement TDD for all React components
- [ ] Add TDD for custom hooks and utilities
- [ ] Create integration tests for page components
- [ ] Establish 85%+ frontend coverage

### Phase 5: Advanced Features (Week 9-10)
- [ ] Add TDD for new features (authentication, collaboration)
- [ ] Implement advanced testing patterns (property-based, mutation)
- [ ] Add monitoring and alerting for test failures
- [ ] Optimize test execution performance

## Quality Gates & Metrics

### Coverage Requirements
- **Backend Critical Paths**: 100% coverage
- **Backend Overall**: 90%+ coverage
- **Frontend Components**: 85%+ coverage
- **API Endpoints**: 95%+ coverage

### Performance Benchmarks
- **Test Execution Time**: < 5 minutes for full suite
- **API Response Time**: < 200ms for 95th percentile
- **Component Render Time**: < 100ms for complex components
- **Workflow Execution**: < 30 seconds for complete workflows

### Security Standards
- **OWASP Top 10**: All vulnerabilities tested
- **Authentication**: Multi-factor authentication support
- **Data Protection**: Encryption at rest and in transit
- **Input Validation**: All user inputs validated and sanitized

## Tools & Automation

### Backend Testing Stack
```toml
# pyproject.toml additions
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--strict-markers",
    "--strict-config",
    "--cov=app",
    "--cov-report=term-missing",
    "--cov-report=html",
    "--cov-report=xml",
    "--cov-fail-under=90",
    "--asyncio-mode=auto"
]
markers = [
    "unit: Unit tests",
    "integration: Integration tests",
    "e2e: End-to-end tests",
    "performance: Performance tests",
    "security: Security tests",
    "slow: Slow running tests",
]
```

### Frontend Testing Stack
```json
{
  "jest": {
    "testEnvironment": "jsdom",
    "setupFilesAfterEnv": ["<rootDir>/__tests__/setup.ts"],
    "collectCoverageFrom": [
      "src/**/*.{ts,tsx}",
      "!src/**/*.d.ts",
      "!src/**/*.stories.{ts,tsx}"
    ],
    "coverageThreshold": {
      "global": {
        "branches": 85,
        "functions": 85,
        "lines": 85,
        "statements": 85
      }
    }
  }
}
```

## Best Practices for ArchMesh

### 1. Agent Testing
- Always mock LLM calls in unit tests
- Test error handling for network timeouts
- Validate JSON parsing and response structure
- Test confidence score calculations

### 2. API Testing
- Use FastAPI TestClient for endpoint testing
- Mock database operations in unit tests
- Test authentication and authorization
- Validate request/response schemas

### 3. Frontend Testing
- Test user interactions, not implementation details
- Mock API calls and external dependencies
- Test accessibility and responsive design
- Use data-testid for reliable element selection

### 4. Workflow Testing
- Test individual workflow nodes in isolation
- Mock external service calls
- Test error handling and recovery
- Validate state transitions

## Conclusion

This TDD strategy is specifically designed for ArchMesh's unique architecture and requirements. By following these guidelines, we can ensure high-quality, reliable software that meets user expectations and business requirements.

The strategy will be continuously updated based on team feedback, project evolution, and industry best practices.

