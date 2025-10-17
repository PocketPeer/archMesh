# Knowledge Base Service

The Knowledge Base Service provides RAG (Retrieval-Augmented Generation) capabilities for storing and retrieving architecture context using vector embeddings, graph databases, and structured metadata storage.

## Overview

The Knowledge Base Service combines multiple storage technologies to provide comprehensive architecture knowledge management:

- **Vector Search (Pinecone)**: Semantic search across architecture descriptions
- **Graph Database (Neo4j)**: Relationship mapping between services and components  
- **Relational Database (PostgreSQL)**: Structured metadata and project information
- **Embeddings (Sentence Transformers)**: Text-to-vector conversion for similarity

## Features

### 🔍 **Vector-Based Semantic Search**
- Store architecture descriptions as vector embeddings
- Search for similar architectures using natural language queries
- Filter results by project, type, or other metadata
- High-dimensional similarity matching for complex architectural concepts

### 🕸️ **Graph-Based Relationship Queries**
- Model services, components, and their dependencies as a graph
- Query service relationships and dependencies
- Analyze architecture patterns and connections
- Navigate complex service architectures

### 📊 **Multi-Modal Knowledge Storage**
- Store structured metadata alongside vector embeddings
- Link graph relationships to vector search results
- Maintain consistency across different storage systems
- Support for complex architectural data structures

### 🎯 **RAG Context Generation**
- Generate relevant context for new feature development
- Retrieve similar patterns and architectural decisions
- Provide technology recommendations based on existing projects
- Support informed architectural decision-making

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Pinecone      │    │     Neo4j       │    │   PostgreSQL    │
│  (Vector DB)    │    │  (Graph DB)     │    │ (Metadata DB)   │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ • Embeddings    │    │ • Services      │    │ • Projects      │
│ • Similarity    │    │ • Dependencies  │    │ • Analysis      │
│ • Search        │    │ • Patterns      │    │ • History       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │ Knowledge Base  │
                    │    Service      │
                    ├─────────────────┤
                    │ • Indexing      │
                    │ • Retrieval     │
                    │ • RAG Context   │
                    │ • Management    │
                    └─────────────────┘
```

## Configuration

### Environment Variables

```bash
# Pinecone Configuration
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_ENVIRONMENT=your_pinecone_environment

# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password123

# Embedding Model
KNOWLEDGE_BASE_EMBEDDING_MODEL=all-MiniLM-L6-v2
```

### Service Initialization

```python
from app.services.knowledge_base_service import KnowledgeBaseService

# Initialize with default configuration
kb_service = KnowledgeBaseService()

# Initialize with custom configuration
kb_service = KnowledgeBaseService(
    pinecone_api_key="your_key",
    pinecone_environment="your_env",
    neo4j_uri="bolt://localhost:7687",
    neo4j_user="neo4j",
    neo4j_password="password123",
    embedding_model="all-MiniLM-L6-v2"
)
```

## Usage

### Indexing Repository Analysis

```python
# Index a repository analysis
result = await kb_service.index_repository_analysis(
    project_id="project_001",
    repository_url="https://github.com/user/repo",
    analysis={
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
    }
)

print(f"Indexed {result['vector_chunks']} chunks and {result['graph_nodes']} nodes")
```

### Semantic Search

```python
# Search for similar architectures
results = await kb_service.search_similar_architectures(
    query="microservices with user authentication",
    project_id="project_001",  # Optional filter
    top_k=5,
    filter_types=["service", "architecture_overview"]  # Optional filter
)

for result in results:
    print(f"Score: {result['score']}")
    print(f"Content: {result['content']}")
    print(f"Type: {result['type']}")
```

### Graph Queries

```python
# Get service dependencies
dependencies = await kb_service.get_service_dependencies(
    project_id="project_001",
    service_name="user-service"  # Optional specific service
)

# Get architecture patterns
patterns = await kb_service.get_architecture_patterns(
    project_id="project_001",
    pattern_type="microservices"  # Optional filter
)
```

### RAG Context Generation

```python
# Get context for new feature development
context = await kb_service.get_context_for_new_feature(
    project_id="project_001",
    feature_description="Add payment processing functionality",
    context_types=["service", "architecture_overview"]
)

print("Similar patterns:", context["similar_patterns"])
print("Existing services:", context["existing_services"])
print("Recommendations:", context["recommendations"])
```

## Data Models

### Vector Embeddings (Pinecone)

```json
{
  "id": "project_001_abc123_0",
  "values": [0.1, 0.2, 0.3, ...],
  "metadata": {
    "project_id": "project_001",
    "repository_url": "https://github.com/user/repo",
    "chunk_type": "service",
    "content": "Service Name: user-service...",
    "indexed_at": "2024-01-01T00:00:00Z",
    "service_name": "user-service",
    "service_type": "service",
    "technology": "Node.js + Express"
  }
}
```

### Graph Nodes (Neo4j)

```cypher
// Project Node
(:Project {
  id: "project_001",
  repository_url: "https://github.com/user/repo",
  name: "my-project",
  description: "A microservices project"
})

// Service Node
(:Service {
  project_id: "project_001",
  name: "user-service",
  type: "service",
  technology: "Node.js + Express",
  responsibility: "User management"
})

// Architecture Node
(:Architecture {
  project_id: "project_001",
  style: "microservices",
  patterns: ["microservices", "event-driven"],
  communication_patterns: ["REST API", "Message Queue"]
})

// Technology Nodes
(:Language {project_id: "project_001", name: "JavaScript", file_count: 150})
(:Framework {project_id: "project_001", name: "Express.js"})
(:Database {project_id: "project_001", name: "PostgreSQL"})
```

### Relationships (Neo4j)

```cypher
// Project relationships
(Project)-[:HAS_ARCHITECTURE]->(Architecture)
(Project)-[:HAS_SERVICE]->(Service)
(Project)-[:USES_LANGUAGE]->(Language)
(Project)-[:USES_FRAMEWORK]->(Framework)
(Project)-[:USES_DATABASE]->(Database)

// Service relationships
(Service)-[:PART_OF_ARCHITECTURE]->(Architecture)
(Service)-[:DEPENDS_ON]->(Service)
```

## API Reference

### Core Methods

#### `index_repository_analysis(project_id, repository_url, analysis, metadata=None)`
Index repository analysis results into the knowledge base.

**Parameters:**
- `project_id` (str): Unique project identifier
- `repository_url` (str): Repository URL
- `analysis` (Dict): Complete repository analysis results
- `metadata` (Dict, optional): Additional metadata

**Returns:** Dictionary with indexing results

#### `search_similar_architectures(query, project_id=None, top_k=5, filter_types=None)`
Search for similar architectures using semantic search.

**Parameters:**
- `query` (str): Natural language query
- `project_id` (str, optional): Filter by project
- `top_k` (int): Number of results to return
- `filter_types` (List[str], optional): Filter by chunk types

**Returns:** List of similar architecture results

#### `get_service_dependencies(project_id, service_name=None)`
Query Neo4j for service dependencies and relationships.

**Parameters:**
- `project_id` (str): Project identifier
- `service_name` (str, optional): Specific service name

**Returns:** List of service dependency information

#### `get_context_for_new_feature(project_id, feature_description, context_types=None)`
Get relevant context for adding a new feature to existing project.

**Parameters:**
- `project_id` (str): Project identifier
- `feature_description` (str): Description of the new feature
- `context_types` (List[str], optional): Types of context to retrieve

**Returns:** Dictionary with relevant context for feature development

### Utility Methods

#### `delete_project_data(project_id)`
Delete all data for a project from the knowledge base.

#### `get_service_status()`
Get the status of all knowledge base services.

#### `get_service_capabilities()`
Get service capabilities and configuration.

## Integration with ArchMesh

### Agent Integration

The Knowledge Base Service integrates with ArchMesh agents:

```python
# In GitHubAnalyzerAgent
from app.services.knowledge_base_service import KnowledgeBaseService

class GitHubAnalyzerAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.kb_service = KnowledgeBaseService()
    
    async def execute(self, input_data):
        # Analyze repository
        analysis = await self._analyze_repository(input_data)
        
        # Index in knowledge base
        await self.kb_service.index_repository_analysis(
            project_id=input_data["project_id"],
            repository_url=input_data["repo_url"],
            analysis=analysis
        )
        
        return analysis
```

### API Integration

```python
# In FastAPI routes
from app.services.knowledge_base_service import KnowledgeBaseService

@app.post("/api/v1/knowledge/search")
async def search_architectures(query: str, project_id: Optional[str] = None):
    kb_service = KnowledgeBaseService()
    results = await kb_service.search_similar_architectures(
        query=query,
        project_id=project_id
    )
    return {"results": results}
```

## Performance Considerations

### Vector Search
- **Embedding Model**: Uses `all-MiniLM-L6-v2` (384 dimensions) for balance of quality and speed
- **Index Size**: Pinecone handles large-scale vector storage efficiently
- **Query Performance**: Sub-second response times for most queries

### Graph Queries
- **Neo4j Performance**: Optimized for relationship traversal
- **Indexing**: Automatic indexing on node properties
- **Query Optimization**: Cypher queries optimized for common patterns

### Memory Usage
- **Embedding Model**: Loaded once and reused for all operations
- **Batch Processing**: Efficient batch processing for large datasets
- **Connection Pooling**: Reused connections to external services

## Error Handling

The service includes comprehensive error handling:

```python
try:
    result = await kb_service.index_repository_analysis(...)
except Exception as e:
    logger.error(f"Knowledge base indexing failed: {str(e)}")
    # Graceful degradation - continue without knowledge base
```

### Fallback Strategies
- **Pinecone Unavailable**: Skip vector indexing, continue with graph storage
- **Neo4j Unavailable**: Skip graph creation, continue with vector storage
- **Embedding Model Error**: Use fallback text processing
- **Partial Failures**: Return partial results with error information

## Monitoring and Logging

### Service Status
```python
status = kb_service.get_service_status()
# Returns: {"pinecone": True, "neo4j": True, "embedder": True, "overall": True}
```

### Comprehensive Logging
- **Indexing Operations**: Track successful and failed indexing operations
- **Search Queries**: Log query performance and result quality
- **Error Tracking**: Detailed error logging with context
- **Performance Metrics**: Track response times and resource usage

## Security Considerations

### Data Privacy
- **No Persistent Storage**: Repository data not permanently stored
- **Secure Connections**: Encrypted connections to all external services
- **Access Control**: Respects repository visibility and permissions

### API Security
- **Token Management**: Secure handling of API keys and tokens
- **Input Validation**: Comprehensive input validation and sanitization
- **Rate Limiting**: Built-in rate limiting for external API calls

## Future Enhancements

### Planned Features
- **Multi-Modal Embeddings**: Support for code, diagrams, and documentation
- **Real-Time Updates**: Live updates when repositories change
- **Advanced Analytics**: Architecture evolution tracking and insights
- **Collaborative Features**: Team-based knowledge sharing and annotations

### Scalability Improvements
- **Distributed Storage**: Support for multiple Pinecone indexes
- **Caching Layer**: Redis-based caching for frequent queries
- **Batch Processing**: Efficient batch operations for large datasets
- **Auto-Scaling**: Dynamic scaling based on usage patterns

## Troubleshooting

### Common Issues

1. **Pinecone Connection Issues**
   - Verify API key and environment
   - Check network connectivity
   - Ensure index exists and is accessible

2. **Neo4j Connection Issues**
   - Verify connection URI and credentials
   - Check Neo4j server status
   - Ensure database is running and accessible

3. **Embedding Model Issues**
   - Check model availability and download
   - Verify sufficient memory for model loading
   - Consider using smaller models for resource-constrained environments

### Debug Mode

Enable debug logging for detailed troubleshooting:

```python
import logging
logging.getLogger("app.services.knowledge_base_service").setLevel(logging.DEBUG)
```

## Conclusion

The Knowledge Base Service provides a powerful foundation for architecture knowledge management in ArchMesh, enabling:

- **Intelligent Search**: Find similar architectures and patterns
- **Relationship Analysis**: Understand service dependencies and connections
- **Context Generation**: Get relevant context for new feature development
- **Scalable Storage**: Handle large-scale architecture knowledge efficiently

This service forms the backbone of ArchMesh's RAG capabilities, enabling informed architectural decision-making based on accumulated knowledge and best practices.
