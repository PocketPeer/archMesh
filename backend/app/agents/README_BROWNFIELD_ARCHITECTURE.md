# Architecture Agent - Brownfield Support

The Architecture Agent has been enhanced to support both **greenfield** and **brownfield** architecture design with RAG (Retrieval Augmented Generation) context integration for existing systems.

## Overview

The updated Architecture Agent provides comprehensive architecture design capabilities for both new projects and integration with existing systems, leveraging knowledge base context to make informed decisions about technology choices, integration strategies, and migration plans.

## Key Features

### 🆕 **Brownfield Architecture Design**
- **RAG Context Integration**: Leverages existing architecture knowledge from the knowledge base
- **Technology Stack Consistency**: Prefers existing technologies and patterns
- **Integration Strategy**: Generates detailed integration plans with existing services
- **Migration Planning**: Provides phased migration strategies with rollback plans
- **Impact Analysis**: Assesses impact on existing systems and services

### 🔄 **Dual Mode Support**
- **Greenfield Mode**: Traditional architecture design for new projects
- **Brownfield Mode**: Integration-focused design for existing systems
- **Automatic Routing**: Intelligently routes to appropriate execution method

### 🧠 **RAG-Enhanced Context**
- **Similar Feature Detection**: Finds similar features in existing systems
- **Service Dependencies**: Analyzes existing service relationships
- **Technology Patterns**: Identifies existing technology usage patterns
- **Integration Points**: Suggests optimal integration strategies

## Architecture

### Class Structure

```python
class ArchitectureAgent(BaseAgent):
    def __init__(self, knowledge_base_service: Optional[KnowledgeBaseService] = None):
        # Initialize with optional knowledge base service for brownfield context
        
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        # Routes to greenfield or brownfield execution based on mode
        
    async def _execute_greenfield(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        # Traditional greenfield architecture design
        
    async def _execute_brownfield(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        # Brownfield architecture design with RAG context
        
    async def _get_brownfield_context(self, project_id: str, requirements: Dict, existing_architecture: Optional[Dict] = None) -> Dict[str, Any]:
        # Retrieves relevant context from knowledge base
        
    def get_brownfield_system_prompt(self) -> str:
        # Specialized system prompt for brownfield design
        
    def _build_brownfield_prompt(self, requirements: Dict, constraints: Dict, preferences: List, domain: str, context: Dict) -> str:
        # Builds enhanced prompt with existing architecture context
        
    async def _generate_integration_strategy(self, existing_services: List[Dict], proposed_architecture: Dict) -> Dict:
        # Generates detailed integration strategy with phases and rollback plans
        
    async def _generate_brownfield_c4_diagram(self, architecture_data: Dict, context: Dict) -> str:
        # Generates C4 diagram showing integration with existing system
```

## Usage Examples

### Greenfield Architecture Design

```python
from app.agents.architecture_agent import ArchitectureAgent

# Initialize agent for greenfield design
agent = ArchitectureAgent()

# Define requirements
requirements = {
    "structured_requirements": {
        "business_goals": ["Build modern e-commerce platform"],
        "functional_requirements": ["User authentication", "Product catalog"],
        "non_functional_requirements": {
            "performance": ["Page load < 2 seconds"],
            "security": ["HTTPS encryption"]
        }
    }
}

# Execute greenfield design
input_data = {
    "requirements": requirements,
    "mode": "greenfield",
    "domain": "e-commerce"
}

result = await agent.execute(input_data)
```

### Brownfield Architecture Design

```python
from app.agents.architecture_agent import ArchitectureAgent
from app.services.knowledge_base_service import KnowledgeBaseService

# Initialize with knowledge base service
kb_service = KnowledgeBaseService()
agent = ArchitectureAgent(knowledge_base_service=kb_service)

# Define new requirements for existing system
requirements = {
    "structured_requirements": {
        "business_goals": ["Add real-time notifications"],
        "functional_requirements": ["Push notifications", "Email alerts"],
        "constraints": ["No breaking changes", "Use existing tech stack"]
    }
}

# Execute brownfield design
input_data = {
    "requirements": requirements,
    "mode": "brownfield",
    "project_id": "existing-project-123",
    "existing_architecture": existing_arch_data,  # Optional
    "domain": "e-commerce"
}

result = await agent.execute(input_data)
```

## Input Parameters

### Common Parameters
- **requirements**: Structured requirements from RequirementsAgent
- **constraints**: Organizational constraints and limitations
- **preferences**: Architecture style preferences
- **domain**: Project domain (e-commerce, fintech, etc.)
- **session_id**: Optional workflow session ID

### Brownfield-Specific Parameters
- **mode**: "brownfield" (required for brownfield mode)
- **project_id**: UUID of existing project (required for brownfield)
- **existing_architecture**: Optional existing architecture data

## Output Structure

### Greenfield Output
```json
{
  "architecture_overview": {
    "style": "microservices",
    "rationale": "Chosen for scalability and team independence",
    "key_principles": ["separation of concerns", "loose coupling"]
  },
  "components": [
    {
      "name": "User Service",
      "type": "service",
      "description": "Handles user authentication and profiles",
      "technology": "Node.js + Express",
      "dependencies": ["user-database"]
    }
  ],
  "technology_stack": {
    "backend": {
      "language": "Node.js",
      "framework": "Express",
      "rationale": "Fast development and large ecosystem"
    }
  },
  "alternatives": [...],
  "implementation_plan": {...},
  "c4_diagram_context": "mermaid diagram code"
}
```

### Brownfield Output
```json
{
  "architecture_overview": {
    "style": "microservices",
    "integration_approach": "Event-driven integration with existing services",
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
  "modified_services": [
    {
      "name": "User Service",
      "modifications": ["Add notification preferences endpoint"],
      "new_endpoints": ["/api/users/preferences"],
      "breaking_changes": false,
      "migration_required": false
    }
  ],
  "integration_points": [
    {
      "from_service": "payment-service",
      "to_service": "notification-service",
      "type": "Event",
      "protocol": "AMQP",
      "description": "Payment completion notifications"
    }
  ],
  "migration_strategy": {
    "phases": [
      {
        "phase": 1,
        "name": "Deploy New Services",
        "duration": "2-3 weeks",
        "steps": ["Deploy notification service", "Set up message queue"],
        "rollback": "Remove new services"
      }
    ],
    "testing_strategy": ["Integration testing", "Performance testing"],
    "monitoring": ["Set up alerts for new services"]
  },
  "impact_analysis": {
    "affected_services": ["user-service", "payment-service"],
    "breaking_changes": false,
    "downtime_required": false,
    "risk_level": "low"
  },
  "integration_strategy": {
    "phases": [...],
    "testing_strategy": [...],
    "monitoring": [...],
    "rollback_plan": "Comprehensive rollback procedure"
  }
}
```

## RAG Context Integration

### Context Retrieval Process

1. **Similar Feature Search**: Queries knowledge base for similar features
2. **Service Dependencies**: Retrieves existing service relationships
3. **Technology Patterns**: Analyzes existing technology usage
4. **Integration Points**: Identifies optimal integration strategies

### Context Quality Assessment

The agent assesses context quality based on:
- **Existing Services Count**: Number of existing services found
- **Similar Features**: Number of similar features identified
- **Technology Stack Size**: Diversity of existing technologies

Quality levels: `high`, `medium`, `low`, `unknown`

## Integration Strategy Generation

### Phase-Based Approach

1. **Phase 1: Deploy New Services**
   - Deploy new services without affecting existing functionality
   - Set up monitoring and logging
   - Perform integration testing

2. **Phase 2: Update Existing Services**
   - Update existing services to integrate with new functionality
   - Deploy with feature flags
   - Monitor system performance

3. **Phase 3: Full Integration**
   - Enable all feature flags
   - Optimize system performance
   - Complete documentation

### Risk Assessment

- **High Risk Services**: Services with breaking changes
- **Critical Dependencies**: Dependencies on existing services
- **Breaking Changes**: Whether any breaking changes are required
- **Data Migration**: Whether data migration is needed
- **Downtime Required**: Whether system downtime is needed

## C4 Diagram Generation

### Greenfield Diagrams
- Standard C4 Context diagrams
- Focus on new system components
- Technology stack visualization

### Brownfield Diagrams
- Integration-focused diagrams
- Shows existing vs new services
- Color-coded for different service types:
  - **Blue**: Existing services
  - **Green**: New services
  - **Orange**: Modified services
  - **Purple**: Infrastructure components

## Best Practices

### For Greenfield Projects
1. **Start with Business Requirements**: Focus on business goals first
2. **Consider Team Expertise**: Choose technologies the team knows
3. **Plan for Scale**: Design for future growth
4. **Security First**: Include security considerations from the start

### For Brownfield Projects
1. **Analyze Existing Architecture**: Understand current system thoroughly
2. **Minimize Disruption**: Avoid changes to stable services
3. **Use Existing Patterns**: Follow established architectural patterns
4. **Plan Incremental Rollout**: Support phased deployment
5. **Ensure Backwards Compatibility**: Don't break existing clients

## Error Handling

### Graceful Degradation
- **Knowledge Base Unavailable**: Falls back to provided existing architecture
- **Context Retrieval Failure**: Uses limited context with warnings
- **LLM Response Parsing**: Validates and enhances responses
- **Integration Strategy Generation**: Provides basic strategy as fallback

### Logging and Monitoring
- **Structured Logging**: Comprehensive logging with context
- **Performance Metrics**: Track execution time and success rates
- **Error Tracking**: Detailed error information for debugging

## Configuration

### Environment Variables
```bash
# LLM Configuration
ANTHROPIC_API_KEY=your_anthropic_key
OPENAI_API_KEY=your_openai_key

# Knowledge Base Configuration
PINECONE_API_KEY=your_pinecone_key
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# Agent Configuration
ARCHITECTURE_AGENT_TEMPERATURE=0.5
ARCHITECTURE_AGENT_MAX_TOKENS=6000
ARCHITECTURE_AGENT_TIMEOUT=180
```

### Agent Initialization
```python
# With knowledge base service
kb_service = KnowledgeBaseService()
agent = ArchitectureAgent(knowledge_base_service=kb_service)

# Without knowledge base service (greenfield only)
agent = ArchitectureAgent()
```

## Testing

### Unit Tests
```python
import pytest
from app.agents.architecture_agent import ArchitectureAgent

@pytest.mark.asyncio
async def test_greenfield_architecture():
    agent = ArchitectureAgent()
    result = await agent.execute({
        "requirements": sample_requirements,
        "mode": "greenfield"
    })
    assert result["architecture_overview"]["style"] is not None
    assert len(result["components"]) > 0

@pytest.mark.asyncio
async def test_brownfield_architecture():
    kb_service = MockKnowledgeBaseService()
    agent = ArchitectureAgent(knowledge_base_service=kb_service)
    result = await agent.execute({
        "requirements": sample_requirements,
        "mode": "brownfield",
        "project_id": "test-project"
    })
    assert "integration_strategy" in result
    assert "new_services" in result
```

### Integration Tests
```python
@pytest.mark.asyncio
async def test_brownfield_with_real_kb():
    kb_service = KnowledgeBaseService()
    agent = ArchitectureAgent(knowledge_base_service=kb_service)
    
    # Test with real project data
    result = await agent.execute({
        "requirements": real_requirements,
        "mode": "brownfield",
        "project_id": "real-project-123"
    })
    
    assert result["metadata"]["context_quality"] in ["high", "medium", "low"]
```

## Performance Considerations

### Optimization Strategies
- **Context Caching**: Cache knowledge base queries
- **Parallel Processing**: Execute multiple queries in parallel
- **Response Streaming**: Stream LLM responses for large outputs
- **Memory Management**: Clean up large context objects

### Scalability
- **Horizontal Scaling**: Multiple agent instances
- **Load Balancing**: Distribute requests across instances
- **Caching**: Redis cache for frequent queries
- **Database Optimization**: Optimize knowledge base queries

## Troubleshooting

### Common Issues

1. **Knowledge Base Connection Failed**
   ```
   Solution: Check connection settings and fallback to existing architecture
   ```

2. **Context Quality Low**
   ```
   Solution: Provide more detailed existing architecture data
   ```

3. **Integration Strategy Generation Failed**
   ```
   Solution: Check service dependencies and provide fallback strategy
   ```

4. **LLM Response Parsing Error**
   ```
   Solution: Validate JSON response and enhance with defaults
   ```

### Debug Mode
```python
# Enable debug logging
import logging
logging.getLogger("app.agents.architecture_agent").setLevel(logging.DEBUG)

# Run with debug flag
result = await agent.execute(input_data, debug=True)
```

## Future Enhancements

### Planned Features
- **Multi-Project Context**: Cross-project architecture patterns
- **Automated Testing**: Integration test generation
- **Cost Optimization**: Technology cost analysis
- **Compliance Checking**: Regulatory compliance validation
- **Performance Prediction**: Architecture performance modeling

### Integration Opportunities
- **CI/CD Integration**: Automated architecture validation
- **Monitoring Integration**: Real-time architecture health
- **Documentation Generation**: Automated architecture documentation
- **Code Generation**: Scaffold code from architecture design

## Contributing

### Development Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/agents/test_architecture_agent.py

# Run demo
python demo_brownfield_architecture.py
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
