#!/usr/bin/env python3
"""
Update environment variables to use Ollama for better stability.
"""

import os
from pathlib import Path

def update_env_file():
    """Update .env file to use Ollama as default LLM provider."""
    env_file = Path(".env")
    
    if not env_file.exists():
        print("No .env file found. Creating one...")
        env_content = """# ArchMesh Environment Configuration

# Application
APP_NAME=ArchMesh PoC
APP_VERSION=0.1.0
DEBUG=true
ENVIRONMENT=development

# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5433/archmesh

# Redis
REDIS_URL=redis://localhost:6380/0

# LLM Configuration - Using Ollama for stability
DEFAULT_LLM_PROVIDER=ollama
DEFAULT_LLM_MODEL=llama3.2:3b

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b

# Task-specific LLM providers (using Ollama for stability)
REQUIREMENTS_LLM_PROVIDER=ollama
REQUIREMENTS_LLM_MODEL=llama3.2:3b
ARCHITECTURE_LLM_PROVIDER=ollama
ARCHITECTURE_LLM_MODEL=llama3.2:3b
CODE_GENERATION_LLM_PROVIDER=ollama
CODE_GENERATION_LLM_MODEL=llama3.2:3b
GITHUB_ANALYSIS_LLM_PROVIDER=ollama
GITHUB_ANALYSIS_LLM_MODEL=llama3.2:3b
ADR_WRITING_LLM_PROVIDER=ollama
ADR_WRITING_LLM_MODEL=llama3.2:3b

# DeepSeek Configuration (fallback)
DEEPSEEK_BASE_URL=http://localhost:11434
DEEPSEEK_MODEL=deepseek-r1

# External API Keys (optional - Ollama doesn't need them)
OPENAI_API_KEY=
ANTHROPIC_API_KEY=

# Knowledge Base (optional)
PINECONE_API_KEY=
NEO4J_URL=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password123

# Logging
LOG_LEVEL=INFO
"""
        env_file.write_text(env_content)
        print("✅ Created .env file with Ollama configuration")
        return
    
    # Read existing .env file
    lines = env_file.read_text().split('\n')
    
    # Update or add Ollama configuration
    updated_lines = []
    ollama_configs = {
        'DEFAULT_LLM_PROVIDER': 'ollama',
        'DEFAULT_LLM_MODEL': 'llama3.2:3b',
        'OLLAMA_BASE_URL': 'http://localhost:11434',
        'OLLAMA_MODEL': 'llama3.2:3b',
        'REQUIREMENTS_LLM_PROVIDER': 'ollama',
        'REQUIREMENTS_LLM_MODEL': 'llama3.2:3b',
        'ARCHITECTURE_LLM_PROVIDER': 'ollama',
        'ARCHITECTURE_LLM_MODEL': 'llama3.2:3b',
        'CODE_GENERATION_LLM_PROVIDER': 'ollama',
        'CODE_GENERATION_LLM_MODEL': 'llama3.2:3b',
        'GITHUB_ANALYSIS_LLM_PROVIDER': 'ollama',
        'GITHUB_ANALYSIS_LLM_MODEL': 'llama3.2:3b',
        'ADR_WRITING_LLM_PROVIDER': 'ollama',
        'ADR_WRITING_LLM_MODEL': 'llama3.2:3b',
    }
    
    # Track which configs we've updated
    updated_configs = set()
    
    for line in lines:
        if '=' in line and not line.strip().startswith('#'):
            key = line.split('=')[0].strip()
            if key in ollama_configs:
                updated_lines.append(f"{key}={ollama_configs[key]}")
                updated_configs.add(key)
            else:
                updated_lines.append(line)
        else:
            updated_lines.append(line)
    
    # Add any missing configs
    for key, value in ollama_configs.items():
        if key not in updated_configs:
            updated_lines.append(f"{key}={value}")
    
    # Write updated .env file
    env_file.write_text('\n'.join(updated_lines))
    print("✅ Updated .env file with Ollama configuration")
    print("📋 Updated configurations:")
    for key in ollama_configs:
        print(f"   - {key}={ollama_configs[key]}")

if __name__ == "__main__":
    update_env_file()
    print("\n🚀 To use Ollama, make sure you have it running:")
    print("   ollama serve")
    print("   ollama pull llama3.2:3b")
    print("\n💡 Ollama provides more stable JSON responses than DeepSeek!")
