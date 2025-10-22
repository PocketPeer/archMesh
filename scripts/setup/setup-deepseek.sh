#!/bin/bash

# ArchMesh PoC - DeepSeek Local LLM Setup Script
# This script helps set up a local DeepSeek LLM for cost-free development

set -e

echo "🚀 Setting up DeepSeek Local LLM for ArchMesh PoC..."

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama is not installed. Please install Ollama first:"
    echo "   Visit: https://ollama.ai/download"
    echo "   Or run: curl -fsSL https://ollama.ai/install.sh | sh"
    exit 1
fi

echo "✅ Ollama is installed"

# Check if Ollama service is running
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "🔄 Starting Ollama service..."
    ollama serve &
    sleep 5
fi

echo "✅ Ollama service is running"

# Pull DeepSeek model
echo "📥 Downloading DeepSeek R1 model (this may take a while)..."
ollama pull deepseek-r1

echo "✅ DeepSeek R1 model downloaded"

# Create .env file if it doesn't exist
if [ ! -f "backend/.env" ]; then
    echo "📝 Creating .env file with DeepSeek configuration..."
    cat > backend/.env << EOF
# ArchMesh PoC Environment Configuration

# Application Settings
APP_NAME="ArchMesh PoC"
APP_VERSION="0.1.0"
DEBUG=true
ENVIRONMENT=development

# API Settings
API_V1_PREFIX="/api/v1"
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8080"]

# Database Configuration
DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5433/archmesh"
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20

# Redis Configuration
REDIS_URL="redis://localhost:6380/0"
REDIS_MAX_CONNECTIONS=10

# Logging Configuration
LOG_LEVEL="INFO"

# AI/LLM Configuration
# DeepSeek Local LLM Configuration (for cost-free development)
DEEPSEEK_BASE_URL="http://localhost:11434"
DEEPSEEK_MODEL="deepseek-r1"

# Default LLM Provider (openai, anthropic, or deepseek)
DEFAULT_LLM_PROVIDER="deepseek"
DEFAULT_LLM_MODEL="deepseek-r1"

# File Processing Configuration
MAX_FILE_SIZE=52428800
ALLOWED_FILE_TYPES=[".pdf", ".docx", ".pptx", ".txt"]
EOF
    echo "✅ .env file created with DeepSeek configuration"
else
    echo "⚠️  .env file already exists. Please manually update it to use DeepSeek:"
    echo "   DEFAULT_LLM_PROVIDER=deepseek"
    echo "   DEEPSEEK_BASE_URL=http://localhost:11434"
    echo "   DEEPSEEK_MODEL=deepseek-r1"
fi

# Test the setup
echo "🧪 Testing DeepSeek setup..."
if curl -s -X POST http://localhost:11434/api/generate \
    -H "Content-Type: application/json" \
    -d '{"model": "deepseek-r1", "prompt": "Hello, are you working?", "stream": false}' \
    | grep -q "response"; then
    echo "✅ DeepSeek is working correctly!"
else
    echo "❌ DeepSeek test failed. Please check the setup."
    exit 1
fi

echo ""
echo "🎉 DeepSeek Local LLM setup complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Install Python dependencies: cd backend && pip install -r requirements.txt"
echo "   2. Start the backend: cd backend && uvicorn app.main:app --reload"
echo "   3. The application will now use DeepSeek locally (no API costs!)"
echo ""
echo "💡 Tips:"
echo "   - DeepSeek R1 is a reasoning model, great for complex tasks"
echo "   - You can also try 'deepseek-coder' for code-related tasks"
echo "   - Run 'ollama list' to see available models"
echo "   - Run 'ollama pull <model-name>' to download other models"
