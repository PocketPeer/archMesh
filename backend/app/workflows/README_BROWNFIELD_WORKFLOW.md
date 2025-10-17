# Brownfield Workflow

The Brownfield Workflow is a comprehensive workflow system designed to handle brownfield projects by analyzing existing systems and designing new features that integrate seamlessly with them.

## Overview

The Brownfield Workflow provides an end-to-end solution for:
- **Analyzing existing architecture** from GitHub repositories
- **Integrating with knowledge base** for context-aware design
- **Designing new features** that work with existing systems
- **Generating integration strategies** with migration plans
- **Creating implementation plans** with risk assessment

## Architecture

### Workflow Graph

```mermaid
graph TD
    A[analyze_existing] --> B[parse_requirements]
    B --> C[human_review_requirements]
    C --> D{Approved?}
    D -->|Yes| E[design_integration]
    D -->|No| B
    E --> F[human_review_integration]
    F --> G{Approved?}
    G -->|Yes| H[generate_implementation_plan]
    G -->|No| E
    H --> I[finalize_workflow]
    I --> J[END]
```

### State Management

The workflow uses a comprehensive state object (`BrownfieldWorkflowState`) that tracks:
- **Session and project identification**
- **Repository and architecture data**
- **Requirements and proposed architecture**
- **Human feedback and approval status**
- **Workflow control and metadata**

## Workflow Stages

### 1. Analyze Existing (`analyze_existing`)

**Purpose**: Extract current architecture from GitHub repository

**Process**:
1. Clone and analyze the GitHub repository
2. Extract architecture information (services, dependencies, technologies)
3. Index the analysis in the knowledge base
4. Update workflow state with existing architecture

**Outputs**:
- `existing_architecture`: Complete architecture analysis
- `analysis_metadata`: Analysis quality and statistics

**Agents Used**:
- `GitHubAnalyzerAgent`: Repository analysis
- `KnowledgeBaseService`: Context indexing

### 2. Parse Requirements (`parse_requirements`)

**Purpose**: Parse new requirements from documents

**Process**:
1. Process requirement documents
2. Extract structured requirements
3. Validate requirements completeness
4. Update workflow state with requirements

**Outputs**:
- `requirements`: Structured requirements data

**Agents Used**:
- `RequirementsAgent`: Requirements parsing

### 3. Human Review Requirements (`human_review_requirements`)

**Purpose**: Human review of parsed requirements

**Process**:
1. Present requirements for human review
2. Collect feedback and approval status
3. Update feedback history
4. Determine next workflow step

**Outputs**:
- `approval_status`: Approval decision
- `human_feedback`: Review feedback
- `feedback_history`: Complete feedback log

**Decision Points**:
- **Approved**: Continue to design integration
- **Rejected/Needs Revision**: Return to parse requirements

### 4. Design Integration (`design_integration`)

**Purpose**: Design architecture with brownfield context

**Process**:
1. Use brownfield-aware architecture agent
2. Leverage existing architecture context
3. Design new services and integration points
4. Generate integration strategy

**Outputs**:
- `proposed_architecture`: Complete architecture design
- `integration_strategy`: Integration and migration plan

**Agents Used**:
- `ArchitectureAgent`: Brownfield architecture design

### 5. Human Review Integration (`human_review_integration`)

**Purpose**: Human review of integration design

**Process**:
1. Present integration design for review
2. Collect feedback on architecture decisions
3. Update feedback history
4. Determine next workflow step

**Outputs**:
- `approval_status`: Approval decision
- `human_feedback`: Review feedback
- `feedback_history`: Complete feedback log

**Decision Points**:
- **Approved**: Continue to implementation planning
- **Rejected/Needs Revision**: Return to design integration

### 6. Generate Implementation Plan (`generate_implementation_plan`)

**Purpose**: Create detailed implementation plan

**Process**:
1. Extract implementation details from integration strategy
2. Create detailed timeline and resource requirements
3. Generate risk mitigation plan
4. Prepare comprehensive implementation guide

**Outputs**:
- `implementation_plan`: Complete implementation plan

### 7. Finalize Workflow (`finalize_workflow`)

**Purpose**: Complete workflow and prepare final results

**Process**:
1. Compile all deliverables
2. Calculate quality metrics
3. Create workflow summary
4. Mark workflow as completed

**Outputs**:
- `workflow_summary`: Complete workflow results

## Usage

### Basic Usage

```python
from app.workflows.brownfield_workflow import BrownfieldWorkflow

# Initialize workflow
workflow = BrownfieldWorkflow()

# Run complete workflow
result = await workflow.run_workflow(
    session_id="session-123",
    project_id="project-456",
    repository_url="https://github.com/company/existing-system",
    document_path="requirements.txt",
    branch="main",
    github_token="optional-token"
)
```

### Advanced Usage

```python
# Initialize with custom database connection
workflow = BrownfieldWorkflow(db_connection_string="postgresql://...")

# Check workflow status
status = await workflow.get_workflow_status("session-123")

# Get workflow information
info = workflow.get_workflow_info()
```

## Input Parameters

### Required Parameters

- **`session_id`**: Unique session identifier
- **`project_id`**: Project identifier
- **`repository_url`**: GitHub repository URL to analyze
- **`document_path`**: Path to requirements document

### Optional Parameters

- **`branch`**: Git branch to analyze (default: "main")
- **`github_token`**: GitHub token for private repositories
- **`db_connection_string`**: Custom database connection for checkpointing

## Output Structure

### Workflow Summary

```json
{
  "project_id": "project-123",
  "session_id": "session-456",
  "repository_url": "https://github.com/company/repo",
  "workflow_status": "completed",
  "stages_completed": [
    "existing_analyzed",
    "requirements_parsed",
    "requirements_reviewed",
    "integration_designed",
    "integration_reviewed",
    "implementation_planned"
  ],
  "deliverables": {
    "existing_architecture": {...},
    "requirements": {...},
    "proposed_architecture": {...},
    "integration_strategy": {...},
    "implementation_plan": {...}
  },
  "quality_metrics": {
    "analysis_quality": 0.85,
    "requirements_confidence": 0.92,
    "architecture_quality": 0.88
  },
  "feedback_history": [...],
  "errors": [],
  "warnings": []
}
```

### Existing Architecture

```json
{
  "services": [
    {
      "id": "user-service",
      "name": "User Service",
      "type": "service",
      "technology": "Node.js + Express",
      "description": "Handles user authentication and profiles",
      "endpoints": ["/api/users", "/api/auth"],
      "dependencies": ["user-database"]
    }
  ],
  "dependencies": [...],
  "technology_stack": {...},
  "quality_score": 0.85
}
```

### Proposed Architecture

```json
{
  "architecture_overview": {
    "style": "microservices",
    "integration_approach": "Event-driven integration",
    "rationale": "Extends existing microservices architecture"
  },
  "new_services": [
    {
      "name": "Notification Service",
      "type": "service",
      "description": "Handles real-time notifications",
      "technology": "Node.js + Express",
      "dependencies": ["user-service", "message-queue"],
      "integration_points": ["Event subscription from payment-service"]
    }
  ],
  "modified_services": [...],
  "integration_points": [...],
  "impact_analysis": {
    "risk_level": "low",
    "breaking_changes": false,
    "downtime_required": false
  }
}
```

### Integration Strategy

```json
{
  "phases": [
    {
      "phase": 1,
      "name": "Deploy New Services",
      "description": "Deploy new services without affecting existing functionality",
      "duration": "2-3 weeks",
      "services": ["notification-service"],
      "steps": [...],
      "rollback": "Remove new services",
      "testing": [...],
      "success_criteria": [...]
    }
  ],
  "testing_strategy": [...],
  "monitoring": [...],
  "rollback_plan": "Comprehensive rollback procedure",
  "risk_assessment": {
    "high_risk_services": [],
    "critical_dependencies": [...],
    "breaking_changes": false,
    "rollback_complexity": "low"
  }
}
```

### Implementation Plan

```json
{
  "project_overview": {
    "project_id": "project-123",
    "total_phases": 3,
    "estimated_duration": "6 weeks",
    "risk_level": "low"
  },
  "phases": [...],
  "testing_strategy": [...],
  "monitoring_setup": [...],
  "rollback_procedures": "...",
  "success_criteria": [...],
  "resource_requirements": {
    "development_team_size": 4,
    "estimated_effort_hours": 320,
    "infrastructure_requirements": {...}
  },
  "timeline": {
    "phases": [...],
    "milestones": [...],
    "dependencies": [...]
  },
  "risk_mitigation": {
    "risks": [...],
    "mitigation_strategies": [...],
    "rollback_procedures": "...",
    "monitoring_plan": [...]
  }
}
```

## Configuration

### Environment Variables

```bash
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/archmesh

# GitHub Configuration
GITHUB_TOKEN=your_github_token

# Knowledge Base Configuration
PINECONE_API_KEY=your_pinecone_key
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# LLM Configuration
ANTHROPIC_API_KEY=your_anthropic_key
OPENAI_API_KEY=your_openai_key
```

### Database Setup

The workflow uses PostgreSQL for checkpointing. Ensure the database is set up with the required tables:

```sql
-- The PostgresSaver will create the necessary tables automatically
-- when the workflow is first run
```

## Error Handling

### Graceful Degradation

The workflow includes comprehensive error handling:

1. **Agent Failures**: Individual agent failures don't stop the workflow
2. **Knowledge Base Issues**: Workflow continues even if knowledge base is unavailable
3. **Human Review Timeouts**: Configurable timeouts for human review steps
4. **Repository Access Issues**: Graceful handling of private repository access

### Error Recovery

- **Retry Logic**: Automatic retries for transient failures
- **Fallback Strategies**: Alternative approaches when primary methods fail
- **State Persistence**: Workflow state is saved at each step for recovery

## Monitoring and Observability

### Logging

The workflow provides comprehensive logging:

```python
# Structured logging with context
logger.info(
    "Workflow stage completed",
    extra={
        "session_id": session_id,
        "project_id": project_id,
        "stage": "analyze_existing",
        "duration": 45.2
    }
)
```

### Metrics

Key metrics tracked:
- **Stage Duration**: Time spent in each workflow stage
- **Success Rates**: Success rates for each stage
- **Error Rates**: Error frequencies and types
- **Quality Scores**: Architecture and requirements quality

### Status Checking

```python
# Check workflow status
status = await workflow.get_workflow_status("session-123")
print(f"Status: {status['status']}")
print(f"Current Stage: {status['current_stage']}")
```

## Testing

### Unit Tests

```python
import pytest
from app.workflows.brownfield_workflow import BrownfieldWorkflow

@pytest.mark.asyncio
async def test_workflow_initialization():
    workflow = BrownfieldWorkflow()
    assert workflow.graph is not None
    assert workflow.kb_service is not None

@pytest.mark.asyncio
async def test_workflow_info():
    workflow = BrownfieldWorkflow()
    info = workflow.get_workflow_info()
    assert "stages" in info
    assert "agents_used" in info
```

### Integration Tests

```python
@pytest.mark.asyncio
async def test_complete_workflow():
    workflow = BrownfieldWorkflow()
    
    # Mock the agents to avoid external dependencies
    with patch('app.workflows.brownfield_workflow.GitHubAnalyzerAgent') as mock_github:
        mock_github.return_value.execute.return_value = mock_analysis_result
        
        result = await workflow.run_workflow(
            session_id="test-session",
            project_id="test-project",
            repository_url="https://github.com/test/repo",
            document_path="test-requirements.txt"
        )
        
        assert result["current_stage"] == "completed"
```

## Best Practices

### Workflow Design

1. **Idempotent Operations**: Each stage can be safely re-run
2. **State Persistence**: All state changes are persisted
3. **Error Recovery**: Comprehensive error handling and recovery
4. **Human Integration**: Clear human review points

### Performance Optimization

1. **Parallel Processing**: Independent operations run in parallel
2. **Caching**: Knowledge base queries are cached
3. **Resource Management**: Proper cleanup of temporary resources
4. **Database Optimization**: Efficient checkpointing

### Security Considerations

1. **Token Management**: Secure handling of GitHub tokens
2. **Data Privacy**: Sensitive data is not logged
3. **Access Control**: Repository access is properly authenticated
4. **Audit Trail**: Complete audit trail of all operations

## Troubleshooting

### Common Issues

1. **Repository Access Denied**
   ```
   Solution: Ensure GitHub token has proper permissions
   ```

2. **Knowledge Base Connection Failed**
   ```
   Solution: Check Pinecone and Neo4j connection settings
   ```

3. **LLM API Rate Limits**
   ```
   Solution: Implement exponential backoff and retry logic
   ```

4. **Database Connection Issues**
   ```
   Solution: Verify PostgreSQL connection and permissions
   ```

### Debug Mode

```python
# Enable debug logging
import logging
logging.getLogger("app.workflows.brownfield_workflow").setLevel(logging.DEBUG)

# Run with debug information
result = await workflow.run_workflow(
    session_id="debug-session",
    project_id="debug-project",
    repository_url="https://github.com/debug/repo",
    document_path="debug-requirements.txt"
)
```

## Future Enhancements

### Planned Features

1. **Multi-Repository Support**: Analyze multiple related repositories
2. **Automated Testing**: Integration test generation
3. **Cost Analysis**: Technology cost estimation
4. **Compliance Checking**: Regulatory compliance validation
5. **Performance Prediction**: Architecture performance modeling

### Integration Opportunities

1. **CI/CD Integration**: Automated workflow triggers
2. **Monitoring Integration**: Real-time workflow monitoring
3. **Documentation Generation**: Automated documentation creation
4. **Code Generation**: Scaffold code from architecture design

## Contributing

### Development Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/workflows/test_brownfield_workflow.py

# Run demo
python demo_brownfield_workflow.py
```

### Code Style

- Follow PEP 8 guidelines
- Use type hints throughout
- Include comprehensive docstrings
- Write unit tests for new features

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions:
- Create GitHub issues
- Check documentation
- Review examples
- Test with sample data
