# Brownfield Analysis API

The Brownfield Analysis API provides comprehensive endpoints for analyzing existing codebases, extracting architecture information, and leveraging knowledge base queries for informed architectural decision-making.

## Overview

The Brownfield API enables:
- **Repository Analysis**: Extract architecture from existing GitHub repositories
- **Knowledge Base Queries**: Search for similar patterns and solutions
- **Architecture Visualization**: Get graph data for interactive diagrams
- **Feature Context**: Generate relevant context for new feature development
- **Project Management**: Track analysis status and project metadata

## API Endpoints

### Base URL
```
/api/v1/brownfield
```

### Authentication
All endpoints require proper authentication (implementation depends on your auth strategy).

## Endpoints

### 1. Analyze Repository

**POST** `/analyze-repository`

Analyze a GitHub repository to extract comprehensive architecture information.

#### Request Body
```json
{
  "project_id": "my-ecommerce-project",
  "repository_url": "https://github.com/user/ecommerce-platform",
  "branch": "main",
  "clone_depth": 1,
  "analyze_private": false,
  "include_commits": false,
  "github_token": "optional_token_for_private_repos",
  "session_id": "analysis_001"
}
```

#### Response
```json
{
  "project_id": "my-ecommerce-project",
  "repository_url": "https://github.com/user/ecommerce-platform",
  "status": "completed",
  "analysis": {
    "architecture": {
      "architecture_style": "microservices",
      "services": [
        {
          "name": "user-service",
          "type": "service",
          "technology": "Node.js + Express",
          "responsibility": "User management"
        }
      ]
    },
    "tech_stack": {
      "languages": {"JavaScript": 150, "TypeScript": 75},
      "frameworks": ["Express.js", "React"]
    }
  },
  "processing_time_seconds": 45.2,
  "metadata": {
    "services_count": 5,
    "languages_count": 3,
    "architecture_style": "microservices"
  }
}
```

#### Features
- Supports public and private repositories
- Configurable clone depth for faster analysis
- Background indexing for large repositories
- Comprehensive technology stack detection
- Architecture pattern recognition

### 2. Search Knowledge Base

**POST** `/search-knowledge`

Search the knowledge base for relevant architecture patterns using semantic search.

#### Request Body
```json
{
  "query": "microservices with user authentication and payment processing",
  "project_id": "my-ecommerce-project",
  "top_k": 5,
  "filter_types": ["service", "architecture_overview"],
  "min_score": 0.7
}
```

#### Response
```json
{
  "query": "microservices with user authentication",
  "results": [
    {
      "score": 0.95,
      "content": "Service Name: user-service...",
      "type": "service",
      "project_id": "project_001",
      "repository_url": "https://github.com/user/repo",
      "metadata": {
        "service_name": "user-service",
        "technology": "Node.js + Express"
      }
    }
  ],
  "total_results": 5,
  "search_time_ms": 150.5,
  "filters_applied": {
    "project_id": "my-ecommerce-project",
    "filter_types": ["service", "architecture_overview"],
    "min_score": 0.7
  }
}
```

#### Features
- Natural language queries
- Semantic similarity matching
- Filtering by project, type, and score
- Rich metadata in results
- Fast sub-second response times

### 3. Get Architecture Graph

**GET** `/project/{project_id}/architecture-graph`

Get architecture graph data for visualization.

#### Response
```json
{
  "project_id": "my-ecommerce-project",
  "nodes": [
    {
      "id": "user-service",
      "label": "User Service",
      "type": "service",
      "technology": "Node.js + Express",
      "properties": {
        "responsibility": "User management",
        "interfaces": ["REST API"],
        "scalability": "Horizontal scaling"
      }
    }
  ],
  "edges": [
    {
      "source": "user-service",
      "target": "user-database",
      "relationship_type": "depends_on",
      "properties": {
        "description": "user-service depends on user-database"
      }
    }
  ],
  "metadata": {
    "nodes_count": 5,
    "edges_count": 8,
    "architecture_patterns": [
      {
        "style": "microservices",
        "patterns": ["microservices", "event-driven"]
      }
    ]
  }
}
```

#### Features
- Service and component nodes
- Dependency relationships
- Technology stack information
- Graph statistics
- Optimized for frontend visualization

### 4. Get Feature Context

**GET** `/project/{project_id}/context`

Get relevant context for adding a new feature to an existing project.

#### Query Parameters
- `feature_description`: Description of the new feature (required)
- `context_types`: Types of context to retrieve (optional)
- `include_recommendations`: Whether to include AI recommendations (default: true)

#### Example Request
```
GET /project/my-ecommerce-project/context?feature_description=Add payment processing functionality&context_types=service,architecture_overview
```

#### Response
```json
{
  "project_id": "my-ecommerce-project",
  "feature_description": "Add payment processing functionality",
  "similar_patterns": [
    {
      "score": 0.9,
      "content": "Payment service with Stripe integration...",
      "type": "service",
      "project_id": "project_001"
    }
  ],
  "existing_services": [
    {
      "name": "user-service",
      "type": "service",
      "technology": "Node.js + Express"
    }
  ],
  "architecture_patterns": [
    {
      "style": "microservices",
      "patterns": ["microservices", "event-driven"]
    }
  ],
  "technology_context": {
    "languages": ["JavaScript", "TypeScript"],
    "frameworks": ["Express.js", "React"],
    "databases": ["PostgreSQL", "Redis"]
  },
  "recommendations": {
    "reuse_patterns": ["Consider using existing payment patterns"],
    "integration_points": ["Integrate with user-service for authentication"],
    "technology_suggestions": ["Leverage existing Node.js stack"],
    "architecture_considerations": [
      "Ensure consistency with existing architecture patterns",
      "Consider service boundaries and responsibilities"
    ]
  },
  "generated_at": "2024-01-01T00:00:00Z"
}
```

#### Features
- Semantic search for similar features
- Analysis of existing services
- Technology recommendations
- Integration point suggestions
- AI-generated architectural guidance

### 5. Get Project Status

**GET** `/project/{project_id}/status`

Get the current status of a project's analysis and knowledge base indexing.

#### Response
```json
{
  "project_id": "my-ecommerce-project",
  "repository_url": "https://github.com/user/ecommerce-platform",
  "analysis_status": "completed",
  "indexed_in_knowledge_base": true,
  "last_analyzed": "2024-01-01T00:00:00Z",
  "services_count": 5,
  "technologies_count": 8,
  "architecture_style": "microservices"
}
```

#### Features
- Analysis completion status
- Knowledge base indexing status
- Project statistics
- Last analysis timestamp

## Data Models

### RepositoryAnalysisRequest
```python
{
  "project_id": str,                    # Required: Project identifier
  "repository_url": HttpUrl,            # Required: GitHub repository URL
  "branch": Optional[str],              # Optional: Git branch (default: "main")
  "clone_depth": Optional[int],         # Optional: Clone depth (default: 1)
  "analyze_private": Optional[bool],    # Optional: Analyze private repos (default: False)
  "include_commits": Optional[bool],    # Optional: Include commit analysis (default: False)
  "github_token": Optional[str],        # Optional: GitHub token for private repos
  "session_id": Optional[str]           # Optional: Session ID for logging
}
```

### KnowledgeSearchRequest
```python
{
  "query": str,                         # Required: Natural language query
  "project_id": Optional[str],          # Optional: Filter by project
  "top_k": Optional[int],               # Optional: Number of results (default: 5)
  "filter_types": Optional[List[str]],  # Optional: Filter by chunk types
  "min_score": Optional[float]          # Optional: Minimum similarity score
}
```

### ArchitectureGraphNode
```python
{
  "id": str,                            # Node identifier
  "label": str,                         # Display label
  "type": str,                          # Node type (service, database, etc.)
  "technology": Optional[str],          # Technology stack
  "properties": Optional[Dict]          # Additional properties
}
```

### ArchitectureGraphEdge
```python
{
  "source": str,                        # Source node ID
  "target": str,                        # Target node ID
  "relationship_type": str,             # Relationship type
  "properties": Optional[Dict]          # Additional properties
}
```

## Error Handling

### Standard Error Response
```json
{
  "error": "Repository analysis failed",
  "detail": "Failed to clone repository: Repository not found",
  "error_code": "REPO_CLONE_FAILED",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### Common Error Codes
- `REPO_CLONE_FAILED`: Repository cloning failed
- `ANALYSIS_FAILED`: Repository analysis failed
- `SEARCH_FAILED`: Knowledge base search failed
- `GRAPH_RETRIEVAL_FAILED`: Architecture graph retrieval failed
- `CONTEXT_GENERATION_FAILED`: Feature context generation failed
- `PROJECT_NOT_FOUND`: Project not found in knowledge base

## Usage Examples

### 1. Analyze a Repository
```bash
curl -X POST "http://localhost:8000/api/v1/brownfield/analyze-repository" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "my-project",
    "repository_url": "https://github.com/user/repo",
    "branch": "main"
  }'
```

### 2. Search for Similar Architectures
```bash
curl -X POST "http://localhost:8000/api/v1/brownfield/search-knowledge" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "microservices with authentication",
    "top_k": 5
  }'
```

### 3. Get Architecture Graph
```bash
curl -X GET "http://localhost:8000/api/v1/brownfield/project/my-project/architecture-graph"
```

### 4. Get Feature Context
```bash
curl -X GET "http://localhost:8000/api/v1/brownfield/project/my-project/context?feature_description=Add payment processing"
```

### 5. Check Project Status
```bash
curl -X GET "http://localhost:8000/api/v1/brownfield/project/my-project/status"
```

## Integration with Frontend

### Architecture Visualization
The architecture graph endpoint provides data optimized for frontend visualization libraries:

```javascript
// Example with D3.js or similar
const response = await fetch('/api/v1/brownfield/project/my-project/architecture-graph');
const graphData = await response.json();

// Render nodes and edges
graphData.nodes.forEach(node => {
  // Create node visualization
});

graphData.edges.forEach(edge => {
  // Create edge visualization
});
```

### Real-time Updates
Use WebSocket connections for real-time updates during analysis:

```javascript
// Example WebSocket integration
const ws = new WebSocket('ws://localhost:8000/ws/project/my-project');
ws.onmessage = (event) => {
  const update = JSON.parse(event.data);
  // Update UI with analysis progress
};
```

## Performance Considerations

### Repository Analysis
- **Small repositories** (< 1000 files): ~30-60 seconds
- **Medium repositories** (1000-10000 files): ~2-5 minutes
- **Large repositories** (> 10000 files): ~5-15 minutes (background processing)

### Knowledge Base Search
- **Simple queries**: < 100ms
- **Complex queries**: < 500ms
- **Filtered queries**: < 200ms

### Architecture Graph
- **Small projects** (< 10 services): < 50ms
- **Medium projects** (10-50 services): < 200ms
- **Large projects** (> 50 services): < 500ms

## Security Considerations

### Repository Access
- **Public repositories**: No authentication required
- **Private repositories**: GitHub token required
- **Token security**: Tokens are not stored, only used for analysis

### Data Privacy
- **No persistent storage**: Repository data not permanently stored
- **Secure connections**: All API calls use HTTPS
- **Input validation**: Comprehensive input validation and sanitization

## Monitoring and Logging

### Request Logging
All API requests are logged with:
- Request method and URL
- Client IP and user agent
- Response status code
- Processing time

### Error Tracking
Errors are logged with:
- Error message and stack trace
- Request context
- User information (if available)
- Timestamp and correlation ID

### Performance Metrics
Track key metrics:
- Request latency
- Success/failure rates
- Repository analysis times
- Knowledge base search performance

## Future Enhancements

### Planned Features
- **Real-time analysis progress**: WebSocket updates during analysis
- **Batch analysis**: Analyze multiple repositories simultaneously
- **Custom analysis rules**: User-defined analysis patterns
- **Export capabilities**: Export analysis results in various formats

### API Versioning
- **Current version**: v1
- **Backward compatibility**: Maintained for at least 6 months
- **Version deprecation**: 3-month notice period

## Conclusion

The Brownfield Analysis API provides comprehensive capabilities for understanding existing codebases and making informed architectural decisions. It combines repository analysis, knowledge base queries, and visualization to support brownfield development and modernization efforts.

Key benefits:
- **Comprehensive Analysis**: Extract detailed architecture information
- **Intelligent Search**: Find similar patterns and solutions
- **Visual Understanding**: Interactive architecture diagrams
- **Context-Aware Development**: Get relevant context for new features
- **Scalable Performance**: Handle repositories of any size
