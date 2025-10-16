# ArchMesh PoC

AI-powered architecture document analysis and requirements extraction system.

## Features

- **Document Upload & Processing**: Support for PDF, DOCX, PPTX, and TXT files
- **Requirements Extraction**: AI-powered analysis of requirements documents
- **Architecture Analysis**: Intelligent parsing of architecture documents
- **Multiple LLM Providers**: Support for OpenAI, Anthropic, and local DeepSeek models
- **Cost-Free Development**: Local DeepSeek LLM integration for development

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL
- Redis
- Docker & Docker Compose (optional)

### 1. Clone and Setup

```bash
git clone <repository-url>
cd archmesh-poc
```

### 2. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Database Setup

```bash
# Start PostgreSQL and Redis (using Docker)
docker-compose up -d postgres redis

# Run migrations
alembic upgrade head
```

### 4. LLM Configuration

#### Option A: Local DeepSeek (Recommended for Development)

For cost-free development, use the local DeepSeek LLM:

```bash
# Run the setup script
./setup-deepseek.sh
```

This script will:
- Install and configure Ollama
- Download the DeepSeek R1 model
- Create a `.env` file with DeepSeek configuration
- Test the setup

#### Option B: Cloud LLM Providers

For production or if you prefer cloud providers:

1. Create a `.env` file in the `backend` directory:

```bash
# For OpenAI
OPENAI_API_KEY="your-openai-api-key"
DEFAULT_LLM_PROVIDER="openai"
DEFAULT_LLM_MODEL="gpt-4"

# For Anthropic
ANTHROPIC_API_KEY="your-anthropic-api-key"
DEFAULT_LLM_PROVIDER="anthropic"
DEFAULT_LLM_MODEL="claude-3-5-sonnet-20241022"
```

### 5. Start the Backend

```bash
cd backend
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### 6. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Local DeepSeek LLM Setup

### Why Use Local DeepSeek?

- **Zero API Costs**: No charges for model usage
- **Data Privacy**: All processing happens locally
- **Offline Capability**: Works without internet connection
- **Full Control**: Customize model behavior and parameters

### Manual Setup

If you prefer to set up DeepSeek manually:

1. **Install Ollama**:
   ```bash
   # macOS
   brew install ollama
   
   # Linux
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Windows
   # Download from https://ollama.ai/download
   ```

2. **Start Ollama Service**:
   ```bash
   ollama serve
   ```

3. **Download DeepSeek Model**:
   ```bash
   ollama pull deepseek-r1
   ```

4. **Configure Environment**:
   ```bash
   # In backend/.env
   DEFAULT_LLM_PROVIDER="deepseek"
   DEEPSEEK_BASE_URL="http://localhost:11434"
   DEEPSEEK_MODEL="deepseek-r1"
   ```

### Available DeepSeek Models

- `deepseek-r1`: Reasoning model, great for complex analysis
- `deepseek-coder`: Specialized for code-related tasks
- `deepseek-chat`: General-purpose conversational model

### Testing DeepSeek Setup

```bash
# Test if Ollama is running
curl http://localhost:11434/api/tags

# Test DeepSeek model
curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{"model": "deepseek-r1", "prompt": "Hello, are you working?", "stream": false}'
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DEFAULT_LLM_PROVIDER` | LLM provider (openai, anthropic, deepseek) | `openai` |
| `DEEPSEEK_BASE_URL` | DeepSeek server URL | `http://localhost:11434` |
| `DEEPSEEK_MODEL` | DeepSeek model name | `deepseek-r1` |
| `OPENAI_API_KEY` | OpenAI API key | - |
| `ANTHROPIC_API_KEY` | Anthropic API key | - |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://postgres:postgres@localhost:5433/archmesh` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6380/0` |

### LLM Provider Switching

You can switch between LLM providers by changing the `DEFAULT_LLM_PROVIDER` environment variable:

```bash
# Use DeepSeek (local, free)
DEFAULT_LLM_PROVIDER="deepseek"

# Use OpenAI (cloud, paid)
DEFAULT_LLM_PROVIDER="openai"

# Use Anthropic (cloud, paid)
DEFAULT_LLM_PROVIDER="anthropic"
```

## API Documentation

Once the backend is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Development

### Running Tests

```bash
cd backend
pytest
```

### Code Quality

```bash
cd backend
black .
isort .
flake8 .
mypy .
```

### Database Migrations

```bash
cd backend
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head
```

## Troubleshooting

### DeepSeek Issues

1. **Ollama not starting**:
   ```bash
   # Check if port 11434 is available
   lsof -i :11434
   
   # Kill existing processes
   pkill ollama
   
   # Restart Ollama
   ollama serve
   ```

2. **Model not found**:
   ```bash
   # List available models
   ollama list
   
   # Pull the model
   ollama pull deepseek-r1
   ```

3. **Connection refused**:
   - Ensure Ollama is running: `ollama serve`
   - Check the base URL in your `.env` file
   - Verify the port (default: 11434)

### General Issues

1. **Database connection errors**:
   - Ensure PostgreSQL is running
   - Check connection string in `.env`
   - Run migrations: `alembic upgrade head`

2. **Redis connection errors**:
   - Ensure Redis is running
   - Check Redis URL in `.env`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.
