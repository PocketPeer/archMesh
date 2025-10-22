# Test-Driven Development (TDD) Workflow for ArchMesh

## Overview

This document establishes the TDD workflow for ArchMesh, providing a structured approach to feature development that ensures high code quality and reliability.

## TDD Principles

### 1. Red-Green-Refactor Cycle
```
Write Failing Test → Write Code → Refactor → Repeat
```

### 2. Test-First Development
- Write tests before implementation
- Tests define expected behavior
- Implementation satisfies tests
- Refactor while keeping tests green

### 3. Small Increments
- Make small, focused changes
- Commit frequently
- Each commit should be working
- Easy to debug and rollback

## TDD Workflow Steps

### Step 1: Write Failing Test (Red)
```python
# Example: Adding a new feature to RequirementsAgent
def test_extract_requirements_with_priorities(self):
    """Test requirements extraction with priority levels."""
    # Arrange
    agent = RequirementsAgent()
    document_content = """
    # High Priority Requirements
    1. User authentication (Priority: High)
    2. Data validation (Priority: Medium)
    3. Logging (Priority: Low)
    """
    
    # Act
    result = await agent.execute({
        "document_path": "/test/path/document.txt",
        "domain": "cloud-native",
    })
    
    # Assert
    assert "priority_levels" in result["structured_requirements"]
    assert result["structured_requirements"]["priority_levels"]["high"] == ["User authentication"]
    assert result["structured_requirements"]["priority_levels"]["medium"] == ["Data validation"]
    assert result["structured_requirements"]["priority_levels"]["low"] == ["Logging"]
```

### Step 2: Write Minimal Code (Green)
```python
# Minimal implementation to make test pass
class RequirementsAgent:
    async def execute(self, input_data):
        # ... existing code ...
        
        # Add priority extraction logic
        priority_levels = self._extract_priority_levels(content)
        structured_requirements["priority_levels"] = priority_levels
        
        return enhanced_data
    
    def _extract_priority_levels(self, content):
        """Extract priority levels from requirements."""
        # Simple implementation to make test pass
        return {
            "high": ["User authentication"],
            "medium": ["Data validation"],
            "low": ["Logging"]
        }
```

### Step 3: Refactor (Refactor)
```python
# Improved implementation
def _extract_priority_levels(self, content):
    """Extract priority levels from requirements using regex."""
    import re
    
    priority_patterns = {
        "high": r"Priority:\s*High|High\s*Priority",
        "medium": r"Priority:\s*Medium|Medium\s*Priority",
        "low": r"Priority:\s*Low|Low\s*Priority"
    }
    
    priority_levels = {"high": [], "medium": [], "low": []}
    
    for priority, pattern in priority_patterns.items():
        matches = re.findall(pattern, content, re.IGNORECASE)
        priority_levels[priority] = matches
    
    return priority_levels
```

## Feature Development Process

### 1. Feature Planning
```markdown
## Feature: Priority-Based Requirements Extraction

### User Story
As a business analyst, I want to extract requirements with priority levels so that I can focus on high-priority items first.

### Acceptance Criteria
- [ ] Extract high-priority requirements
- [ ] Extract medium-priority requirements  
- [ ] Extract low-priority requirements
- [ ] Handle requirements without explicit priorities
- [ ] Validate priority format

### Technical Requirements
- Add priority extraction to RequirementsAgent
- Update JSON schema for requirements
- Add priority validation
- Update documentation
```

### 2. Test Design
```python
# Test cases to cover
class TestPriorityExtraction:
    def test_extract_high_priority_requirements(self):
        """Test extraction of high-priority requirements."""
        
    def test_extract_medium_priority_requirements(self):
        """Test extraction of medium-priority requirements."""
        
    def test_extract_low_priority_requirements(self):
        """Test extraction of low-priority requirements."""
        
    def test_handle_requirements_without_priorities(self):
        """Test handling of requirements without explicit priorities."""
        
    def test_validate_priority_format(self):
        """Test validation of priority format."""
        
    def test_priority_extraction_edge_cases(self):
        """Test edge cases in priority extraction."""
```

### 3. Implementation
```python
# Implementation following TDD cycle
class RequirementsAgent:
    def _extract_priority_levels(self, content):
        """Extract priority levels from requirements."""
        # Implementation with comprehensive error handling
        # and edge case management
        pass
```

### 4. Integration Testing
```python
# Integration test for the complete feature
class TestPriorityExtractionIntegration:
    async def test_end_to_end_priority_extraction(self):
        """Test complete priority extraction workflow."""
        # Test with real document
        # Test with API endpoint
        # Test with frontend integration
```

## Test Categories and Priorities

### 1. Critical Path Tests (Priority 1)
- Core business logic
- Data validation
- Error handling
- Security features

### 2. Integration Tests (Priority 2)
- API endpoints
- Database operations
- External service integration
- Component interactions

### 3. Edge Case Tests (Priority 3)
- Boundary conditions
- Error scenarios
- Performance limits
- Unusual inputs

### 4. User Experience Tests (Priority 4)
- UI interactions
- User workflows
- Accessibility
- Cross-browser compatibility

## Test Quality Standards

### 1. Test Naming
```python
# Good test names
def test_extract_requirements_with_valid_document():
def test_handle_llm_timeout_gracefully():
def test_validate_architecture_schema():

# Bad test names
def test_requirements():
def test_error():
def test_validation():
```

### 2. Test Structure (AAA Pattern)
```python
def test_feature_behavior():
    # Arrange - Set up test data and conditions
    agent = RequirementsAgent()
    input_data = {"document_path": "/test/path"}
    
    # Act - Execute the code under test
    result = await agent.execute(input_data)
    
    # Assert - Verify the expected outcome
    assert result["status"] == "success"
    assert "requirements" in result
```

### 3. Test Isolation
```python
# Each test should be independent
class TestRequirementsAgent:
    def setup_method(self):
        """Set up fresh state for each test."""
        self.agent = RequirementsAgent()
        self.test_data = self._create_test_data()
    
    def teardown_method(self):
        """Clean up after each test."""
        self.agent = None
        self.test_data = None
```

### 4. Test Data Management
```python
# Use factories for test data
class TestDataFactory:
    @staticmethod
    def create_requirements_document():
        return {
            "content": "Sample requirements content",
            "path": "/test/path/document.txt",
            "domain": "cloud-native"
        }
    
    @staticmethod
    def create_expected_result():
        return {
            "structured_requirements": {
                "business_goals": ["Goal 1"],
                "functional_requirements": ["Req 1"],
            },
            "confidence_score": 0.8
        }
```

## Continuous Integration Integration

### 1. Pre-commit Hooks
```bash
#!/bin/bash
# .git/hooks/pre-commit

# Run tests before commit
echo "Running tests before commit..."
./scripts/run-test-suite.sh --backend --frontend

if [ $? -ne 0 ]; then
    echo "Tests failed. Commit aborted."
    exit 1
fi

echo "All tests passed. Proceeding with commit."
```

### 2. Pull Request Validation
```yaml
# .github/workflows/pr-validation.yml
name: PR Validation

on:
  pull_request:
    branches: [ main, develop ]

jobs:
  test-validation:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Test Suite
        run: ./scripts/run-test-suite.sh
      - name: Check Coverage
        run: |
          if [ $(cat coverage/backend-coverage.xml | grep -o 'line-rate="[^"]*"' | cut -d'"' -f2 | cut -d'.' -f2) -lt 90 ]; then
            echo "Backend coverage below 90%"
            exit 1
          fi
```

### 3. Quality Gates
```python
# Quality gate configuration
QUALITY_GATES = {
    "coverage_threshold": 90,
    "test_failure_threshold": 0,
    "performance_threshold": 2.0,  # seconds
    "security_scan_required": True,
    "code_review_required": True,
}
```

## Test Maintenance

### 1. Test Refactoring
```python
# When refactoring tests, maintain the same behavior
class TestRequirementsAgent:
    # Before refactoring
    def test_extract_requirements(self):
        agent = RequirementsAgent()
        result = agent.extract_requirements("test content")
        assert result["status"] == "success"
    
    # After refactoring - same behavior, better structure
    def test_extract_requirements(self):
        # Arrange
        agent = self._create_agent()
        content = self._create_test_content()
        
        # Act
        result = agent.extract_requirements(content)
        
        # Assert
        self._assert_successful_extraction(result)
```

### 2. Test Documentation
```python
class TestRequirementsAgent:
    """
    Test suite for RequirementsAgent.
    
    This test suite covers:
    - Requirements extraction from documents
    - Error handling and edge cases
    - Integration with LLM services
    - Data validation and transformation
    """
    
    def test_extract_requirements_success(self):
        """
        Test successful requirements extraction.
        
        Given: A valid requirements document
        When: The agent extracts requirements
        Then: Structured requirements are returned with confidence score
        """
        pass
```

### 3. Test Performance
```python
# Monitor test performance
import time
import pytest

class TestPerformance:
    @pytest.mark.performance
    def test_requirements_extraction_performance(self):
        """Test that requirements extraction completes within acceptable time."""
        start_time = time.time()
        
        # Execute test
        result = await agent.execute(test_data)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Assert performance requirement
        assert execution_time < 5.0, f"Execution took {execution_time}s, expected < 5.0s"
```

## Best Practices

### 1. Test Organization
```
tests/
├── unit/
│   ├── test_agents/
│   ├── test_services/
│   └── test_core/
├── integration/
│   ├── test_api/
│   ├── test_database/
│   └── test_external/
├── e2e/
│   ├── test_workflows/
│   └── test_user_journeys/
└── fixtures/
    ├── test_data/
    └── mock_services/
```

### 2. Mock Strategy
```python
# Mock external dependencies
@pytest.fixture
def mock_llm_client():
    """Mock LLM client for testing."""
    with patch('app.core.llm_client.LLMClient') as mock:
        mock.return_value.generate.return_value = {
            "content": "Mocked LLM response",
            "usage": {"total_tokens": 100}
        }
        yield mock
```

### 3. Test Data Management
```python
# Use parameterized tests for multiple scenarios
@pytest.mark.parametrize("input_data,expected_output", [
    ("valid document", {"status": "success"}),
    ("invalid document", {"status": "error"}),
    ("empty document", {"status": "error"}),
])
def test_document_processing(input_data, expected_output):
    """Test document processing with various inputs."""
    result = process_document(input_data)
    assert result["status"] == expected_output["status"]
```

## Metrics and Monitoring

### 1. Test Metrics
```python
# Track test metrics
TEST_METRICS = {
    "total_tests": 0,
    "passed_tests": 0,
    "failed_tests": 0,
    "skipped_tests": 0,
    "coverage_percentage": 0,
    "execution_time": 0,
    "flaky_tests": [],
}
```

### 2. Quality Trends
```python
# Monitor quality trends over time
def generate_quality_report():
    """Generate quality report for the project."""
    return {
        "coverage_trend": get_coverage_trend(),
        "test_stability": get_test_stability(),
        "performance_trend": get_performance_trend(),
        "recommendations": get_improvement_recommendations(),
    }
```

## Conclusion

This TDD workflow ensures:

1. **High Code Quality** - Tests drive implementation
2. **Reliable Features** - Comprehensive test coverage
3. **Maintainable Code** - Well-tested, refactorable code
4. **Team Confidence** - Clear development process
5. **Continuous Improvement** - Metrics-driven development

By following this workflow, ArchMesh development will be:
- **Predictable** - Clear process and standards
- **Reliable** - Comprehensive testing
- **Efficient** - Automated quality gates
- **Scalable** - Maintainable test suite
