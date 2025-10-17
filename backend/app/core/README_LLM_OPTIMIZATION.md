# LLM Optimization Strategy for ArchMesh PoC

This document describes the intelligent LLM selection strategy implemented in ArchMesh to optimize performance and cost-effectiveness based on task-specific requirements.

## Overview

The ArchMesh system uses different LLMs for different tasks based on performance analysis and cost considerations. This approach ensures optimal results while managing costs effectively.

## Task-Specific LLM Mapping

Based on performance analysis, the following LLM assignments have been implemented:

| Task | Primary LLM | Performance | Reasoning |
|------|-------------|-------------|-----------|
| **Requirements Parsing** | DeepSeek R1 | ✅ Excellent | Superior at understanding and structuring requirements |
| **Architecture Design** | Claude Opus | ✅ Best | Best-in-class architectural reasoning and design |
| **Code Generation** | GPT-4 | ✅ Best | Superior code generation capabilities |
| **GitHub Analysis** | DeepSeek R1 | ✅ Excellent | Excellent at code analysis and repository understanding |
| **ADR Writing** | Claude Sonnet | ✅ Best | Best for structured technical writing |
| **Development/Testing** | DeepSeek R1 | ✅ Best (Free) | Free and capable for development tasks |

## Environment-Specific Strategy

### Development Environment
- **Strategy**: Cost-optimized with DeepSeek preference
- **Reasoning**: Prioritizes cost-effectiveness while maintaining quality
- **Primary Provider**: DeepSeek (free)
- **Fallback**: OpenAI GPT-4

### Production Environment
- **Strategy**: Performance-optimized with task-specific selection
- **Reasoning**: Prioritizes best-in-class performance for each task
- **Primary Provider**: Varies by task (see mapping above)
- **Fallback**: DeepSeek R1

## Implementation

### Configuration

The system uses task-specific configuration in `app/config.py`:

```python
# Task-specific LLM configurations
requirements_llm_provider: str = "deepseek"
requirements_llm_model: str = "deepseek-r1"

architecture_llm_provider: str = "anthropic"
architecture_llm_model: str = "claude-3-5-opus-20241022"

code_generation_llm_provider: str = "openai"
code_generation_llm_model: str = "gpt-4"
```

### LLM Strategy Module

The `app/core/llm_strategy.py` module provides:

- **TaskType Enum**: Defines all supported task types
- **LLMStrategy Class**: Implements intelligent LLM selection
- **Environment-aware selection**: Different strategies for dev/prod
- **Fallback handling**: Graceful degradation when providers are unavailable

### Agent Integration

Agents automatically use the optimal LLM for their task:

```python
# RequirementsAgent automatically uses DeepSeek R1
requirements_agent = RequirementsAgent()

# ArchitectureAgent automatically uses Claude Opus
architecture_agent = ArchitectureAgent()
```

## Usage Examples

### Basic Usage

```python
from app.core.llm_strategy import get_optimal_llm_for_task

# Get optimal LLM for requirements parsing
provider, model = get_optimal_llm_for_task("requirements")
print(f"Using {provider}/{model}")  # Output: deepseek/deepseek-r1
```

### Advanced Usage

```python
from app.core.llm_strategy import LLMStrategy, TaskType

# Get LLM for specific task and environment
provider, model = LLMStrategy.get_llm_for_task(
    TaskType.ARCHITECTURE_DESIGN,
    environment="production"
)
print(f"Using {provider}/{model}")  # Output: anthropic/claude-3-5-opus-20241022
```

### Getting Recommendations

```python
from app.core.llm_strategy import LLMStrategy

# Get all task recommendations
recommendations = LLMStrategy.get_task_recommendations()
for task, config in recommendations.items():
    print(f"{task}: {config['primary']}")
```

## Benefits

### Performance Benefits
- **Task-optimized**: Each task uses the LLM that performs best for that specific task
- **Quality improvement**: Better results for requirements parsing, architecture design, etc.
- **Consistency**: Reliable performance across different task types

### Cost Benefits
- **Development cost savings**: DeepSeek is free for development tasks
- **Production optimization**: Only use expensive models when they provide significant value
- **Fallback efficiency**: Graceful degradation to cost-effective alternatives

### Operational Benefits
- **Environment awareness**: Different strategies for dev vs production
- **Automatic selection**: No manual LLM selection required
- **Fallback handling**: System continues to work even if primary LLM is unavailable

## Configuration

### Environment Variables

Set the following environment variables to configure LLM providers:

```bash
# OpenAI
OPENAI_API_KEY=your_openai_key

# Anthropic
ANTHROPIC_API_KEY=your_anthropic_key

# DeepSeek (local)
DEEPSEEK_BASE_URL=http://localhost:11434
DEEPSEEK_MODEL=deepseek-r1

# Environment
ENVIRONMENT=development  # or production
```

### Custom Configuration

You can override the default task-specific LLM assignments:

```python
# In your .env file
REQUIREMENTS_LLM_PROVIDER=anthropic
REQUIREMENTS_LLM_MODEL=claude-3-5-sonnet-20241022

ARCHITECTURE_LLM_PROVIDER=openai
ARCHITECTURE_LLM_MODEL=gpt-4
```

## Monitoring and Logging

The system provides comprehensive logging for LLM selection:

```python
# Logs include:
# - Selected LLM for each task
# - Environment context
# - Fallback usage
# - Performance metrics
```

## Future Enhancements

### Planned Features
- **Dynamic performance monitoring**: Track actual performance metrics
- **Cost tracking**: Monitor LLM usage costs
- **A/B testing**: Compare different LLM configurations
- **Auto-optimization**: Automatically adjust based on performance data

### Extensibility
- **New task types**: Easy to add new task-specific LLM mappings
- **New providers**: Support for additional LLM providers
- **Custom strategies**: Implement custom selection logic

## Troubleshooting

### Common Issues

1. **Provider unavailable**: System automatically falls back to available providers
2. **API key missing**: Check environment variables and API key configuration
3. **Model not found**: Verify model names and provider compatibility

### Debug Mode

Enable debug logging to see LLM selection decisions:

```python
import logging
logging.getLogger("app.core.llm_strategy").setLevel(logging.DEBUG)
```

## Conclusion

The LLM optimization strategy in ArchMesh provides:

- **Optimal performance** for each task type
- **Cost-effective** operation in development
- **Production-ready** performance optimization
- **Flexible configuration** for different environments
- **Robust fallback** handling

This approach ensures that ArchMesh delivers the best possible results while maintaining cost efficiency and operational reliability.
