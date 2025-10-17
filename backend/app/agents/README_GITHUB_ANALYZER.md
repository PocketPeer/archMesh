# GitHub Analyzer Agent

The GitHub Analyzer Agent is a comprehensive tool for analyzing GitHub repositories to extract architecture information, technology stacks, and provide actionable recommendations.

## Overview

The GitHubAnalyzerAgent automatically clones repositories, analyzes their structure, extracts technology information, and uses AI to provide detailed architecture analysis and recommendations.

## Features

### 🔍 **Comprehensive Repository Analysis**
- **File Structure Analysis**: Identifies key files, directories, and project organization
- **Technology Stack Detection**: Automatically detects programming languages, frameworks, and tools
- **Configuration Parsing**: Analyzes Docker Compose, Kubernetes, CI/CD, and other config files
- **Dependency Analysis**: Extracts and analyzes external dependencies and versions
- **API Contract Extraction**: Identifies OpenAPI/Swagger specifications and API interfaces

### 🏗️ **Architecture Analysis**
- **Architecture Pattern Recognition**: Identifies monolith, microservices, serverless, etc.
- **Service Identification**: Maps services, components, and their relationships
- **Communication Patterns**: Analyzes how services communicate (REST, GraphQL, events, etc.)
- **Data Storage Analysis**: Identifies databases, caches, and storage patterns
- **Deployment Strategy**: Analyzes containerization, orchestration, and deployment approaches

### 📊 **Code Quality Assessment**
- **Test Coverage Analysis**: Identifies test files and testing frameworks
- **Documentation Assessment**: Evaluates README files and documentation quality
- **Code Style Analysis**: Detects linting configurations and code quality tools
- **Security Analysis**: Identifies security configurations and potential issues

### 🎯 **Actionable Recommendations**
- **Architecture Improvements**: Specific suggestions for architectural enhancements
- **Technology Stack Optimization**: Recommendations for technology choices
- **Code Quality Improvements**: Suggestions for better testing, documentation, and practices
- **Security Enhancements**: Recommendations for security improvements

## LLM Integration

The agent uses the optimized LLM strategy:
- **Primary LLM**: DeepSeek R1 (Excellent for GitHub analysis)
- **Fallback**: Claude Sonnet or GPT-4
- **Environment-aware**: Uses cost-effective options in development

## Usage

### Basic Usage

```python
from app.agents.github_analyzer_agent import GitHubAnalyzerAgent

# Initialize agent
agent = GitHubAnalyzerAgent(github_token="your_token_here")

# Analyze a repository
result = await agent.execute({
    "repo_url": "https://github.com/user/repo",
    "branch": "main",
    "clone_depth": 1
})

# Access results
print(f"Architecture: {result['architecture']['architecture_style']}")
print(f"Services: {len(result['services'])}")
print(f"Tech Stack: {result['tech_stack']['languages']}")
```

### Advanced Usage

```python
# Analyze with additional options
result = await agent.execute({
    "repo_url": "https://github.com/user/repo",
    "branch": "develop",
    "clone_depth": 5,
    "analyze_private": True,
    "include_commits": True,
    "session_id": "analysis_001"
})

# Get comprehensive analysis
architecture = result['architecture']
tech_stack = result['tech_stack']
recommendations = result['recommendations']
```

## Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `repo_url` | string | ✅ | GitHub repository URL |
| `branch` | string | ❌ | Git branch to analyze (default: "main") |
| `clone_depth` | integer | ❌ | Clone depth for shallow clone (default: 1) |
| `analyze_private` | boolean | ❌ | Whether to analyze private repos (default: False) |
| `include_commits` | boolean | ❌ | Whether to analyze recent commits (default: False) |
| `session_id` | string | ❌ | Workflow session ID for logging |

## Output Structure

```json
{
  "repository_info": {
    "url": "https://github.com/user/repo",
    "branch": "main",
    "analyzed_at": "2024-01-01T00:00:00Z",
    "name": "repository-name",
    "description": "Repository description",
    "language": "JavaScript",
    "stars": 100,
    "forks": 20
  },
  "tech_stack": {
    "languages": {
      "JavaScript": 150,
      "TypeScript": 75,
      "Python": 25
    },
    "frameworks": ["React", "Express.js", "FastAPI"],
    "databases": ["PostgreSQL", "Redis"],
    "infrastructure": ["Docker", "Kubernetes"],
    "tools": ["Webpack", "Jest", "ESLint"]
  },
  "architecture": {
    "architecture_style": "microservices",
    "services": [
      {
        "name": "api-gateway",
        "type": "gateway",
        "technology": "Node.js + Express",
        "responsibility": "Route requests to backend services"
      }
    ],
    "communication_patterns": ["REST API", "Event-driven"],
    "data_storage": {
      "primary": "PostgreSQL",
      "cache": "Redis"
    },
    "deployment": {
      "strategy": "Kubernetes",
      "infrastructure": ["Docker", "Kubernetes"]
    }
  },
  "services": [...],
  "dependencies": {...},
  "api_contracts": [...],
  "configurations": {...},
  "code_quality": {...},
  "recommendations": [
    {
      "category": "Architecture",
      "priority": "Medium",
      "recommendation": "Add API versioning",
      "rationale": "Identified during architecture analysis"
    }
  ]
}
```

## Supported Technologies

### Programming Languages
- **Frontend**: JavaScript, TypeScript, React, Vue.js, Angular, Svelte
- **Backend**: Python, Node.js, Java, Go, Rust, Ruby, PHP, C#
- **Mobile**: Swift, Kotlin, React Native, Flutter
- **Data**: R, SQL, Shell scripting

### Frameworks & Libraries
- **Web**: React, Vue.js, Angular, Next.js, Express.js, FastAPI, Django, Spring Boot
- **Mobile**: React Native, Flutter, Ionic
- **Testing**: Jest, Mocha, pytest, JUnit, Cypress, Playwright

### Infrastructure & DevOps
- **Containers**: Docker, Docker Compose, Kubernetes
- **CI/CD**: GitHub Actions, GitLab CI, Jenkins, Azure DevOps
- **Cloud**: AWS, Azure, GCP, Terraform, Ansible
- **Monitoring**: Prometheus, Grafana, ELK Stack

### Databases & Storage
- **Relational**: PostgreSQL, MySQL, SQLite, Oracle
- **NoSQL**: MongoDB, Redis, Cassandra, Elasticsearch
- **Cloud**: DynamoDB, Cosmos DB, Cloud Firestore

## Configuration Files Supported

- **Package Managers**: package.json, requirements.txt, pom.xml, go.mod, Cargo.toml
- **Containerization**: Dockerfile, docker-compose.yml
- **Orchestration**: Kubernetes manifests, Helm charts
- **CI/CD**: .github/workflows, .gitlab-ci.yml, Jenkinsfile
- **Infrastructure**: Terraform files, Ansible playbooks
- **API Documentation**: OpenAPI/Swagger specifications

## Error Handling

The agent includes comprehensive error handling:

- **Repository Cloning**: Graceful handling of clone failures with cleanup
- **File Parsing**: Safe parsing of configuration files with fallbacks
- **LLM Communication**: Retry logic and fallback providers
- **Resource Cleanup**: Automatic cleanup of temporary files and directories

## Performance Considerations

- **Shallow Cloning**: Uses shallow clones by default for faster analysis
- **Selective Analysis**: Focuses on key files and directories
- **Caching**: Can be extended with caching for repeated analyses
- **Parallel Processing**: Can analyze multiple repositories concurrently

## Security Features

- **Token Management**: Secure handling of GitHub tokens
- **Temporary Files**: Automatic cleanup of cloned repositories
- **Access Control**: Respects repository visibility and permissions
- **Data Privacy**: No persistent storage of repository data

## Integration with ArchMesh

The GitHub Analyzer Agent integrates seamlessly with the ArchMesh ecosystem:

- **LLM Strategy**: Uses optimized LLM selection for GitHub analysis
- **Base Agent**: Inherits from BaseAgent for consistent behavior
- **Logging**: Comprehensive logging for monitoring and debugging
- **Error Handling**: Consistent error handling and reporting
- **Configuration**: Environment-aware configuration management

## Example Analysis Results

### Microservices Architecture
```json
{
  "architecture_style": "microservices",
  "services": [
    {
      "name": "user-service",
      "type": "service",
      "technology": "Node.js + Express",
      "responsibility": "User management and authentication"
    },
    {
      "name": "product-service",
      "type": "service", 
      "technology": "Python + FastAPI",
      "responsibility": "Product catalog and inventory"
    }
  ],
  "communication_patterns": ["REST API", "Message Queue"],
  "deployment": {
    "strategy": "Kubernetes",
    "infrastructure": ["Docker", "Kubernetes", "AWS"]
  }
}
```

### Monolithic Architecture
```json
{
  "architecture_style": "monolith",
  "services": [
    {
      "name": "web-application",
      "type": "service",
      "technology": "Django + PostgreSQL",
      "responsibility": "Full-stack web application"
    }
  ],
  "communication_patterns": ["Internal function calls"],
  "deployment": {
    "strategy": "Traditional",
    "infrastructure": ["Docker", "AWS EC2"]
  }
}
```

## Best Practices

1. **Use Shallow Clones**: For faster analysis, use `clone_depth: 1`
2. **Provide GitHub Token**: For private repositories and enhanced metadata
3. **Specify Branch**: Analyze specific branches for focused results
4. **Review Recommendations**: Always review and validate AI recommendations
5. **Combine with Manual Review**: Use as a starting point for deeper analysis

## Troubleshooting

### Common Issues

1. **Clone Failures**: Check repository URL and access permissions
2. **Large Repositories**: Use shallow clones and consider repository size
3. **Private Repositories**: Ensure GitHub token has appropriate permissions
4. **Parse Errors**: Some configuration files may have syntax issues

### Debug Mode

Enable debug logging to see detailed analysis steps:

```python
import logging
logging.getLogger("app.agents.github_analyzer_agent").setLevel(logging.DEBUG)
```

## Future Enhancements

- **Commit Analysis**: Analyze recent commits for change patterns
- **Dependency Vulnerability Scanning**: Security analysis of dependencies
- **Performance Metrics**: Code complexity and performance indicators
- **Architecture Evolution**: Track architecture changes over time
- **Team Analysis**: Analyze contributor patterns and expertise

## Conclusion

The GitHub Analyzer Agent provides comprehensive repository analysis capabilities that help understand existing architectures, identify improvement opportunities, and make informed decisions about technology choices and architectural patterns.
