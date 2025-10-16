# ArchMesh PoC Backend

AI-powered architecture document analysis and processing backend built with FastAPI.

## 🚀 Features

- **FastAPI 0.109+** with async/await support
- **SQLAlchemy 2.0+** with async engine and connection pooling
- **Alembic** for database migrations
- **Redis** for caching and session management
- **Pydantic v2** for data validation and serialization
- **Structured logging** with loguru
- **CORS middleware** for cross-origin requests
- **Health check endpoints** for monitoring
- **API versioning** (v1)
- **Environment-based configuration** using pydantic-settings
- **Comprehensive testing** with pytest
- **AI/LLM integration** with LangChain and LangGraph
- **Document parsing** support for PDF, DOCX, PPTX, and TXT files

## 📋 Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker and Docker Compose (optional)

## 🛠️ Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd archmesh-poc/backend
```

### 2. Create and activate virtual environment

```bash
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment configuration

Create a `.env` file in the backend directory:

```bash
# Application
APP_NAME="ArchMesh PoC"
APP_VERSION="0.1.0"
DEBUG=true
ENVIRONMENT=development

# API
API_V1_PREFIX="/api/v1"
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8080"]

# Database
DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5433/archmesh"
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20

# Redis
REDIS_URL="redis://localhost:6380/0"
REDIS_MAX_CONNECTIONS=10

# Logging
LOG_LEVEL="INFO"

# AI/LLM (optional)
OPENAI_API_KEY="your-openai-api-key"
ANTHROPIC_API_KEY="your-anthropic-api-key"
DEFAULT_LLM_PROVIDER="openai"
DEFAULT_LLM_MODEL="gpt-4"

# File Processing
MAX_FILE_SIZE=52428800  # 50MB
ALLOWED_FILE_TYPES=[".pdf", ".docx", ".pptx", ".txt"]
```

### 5. Database setup

Make sure PostgreSQL is running and create the database:

```bash
# Using Docker Compose (recommended)
cd ..  # Go to archmesh-poc directory
docker-compose up -d postgres

# Or manually
createdb archmesh
```

### 6. Initialize database

```bash
# Initialize Alembic (first time only)
alembic init alembic

# Create initial migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

## 🏃‍♂️ Running the Application

### Development mode

```bash
# Using uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or using the main module
python -m app.main
```

### Production mode

```bash
# Using gunicorn with uvicorn workers
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Using Docker Compose

```bash
# From the archmesh-poc directory
docker-compose up -d
```

## 📚 API Documentation

Once the application is running, you can access:

- **Swagger UI**: http://localhost:8000/docs (development only)
- **ReDoc**: http://localhost:8000/redoc (development only)
- **OpenAPI Schema**: http://localhost:8000/openapi.json (development only)

## 🧪 Testing

### Run all tests

```bash
pytest
```

### Run tests with coverage

```bash
pytest --cov=app --cov-report=html --cov-report=term-missing
```

### Run specific test file

```bash
pytest tests/test_health.py -v
```

### Run tests with different markers

```bash
# Run only fast tests
pytest -m "not slow"

# Run only integration tests
pytest -m "integration"
```

## 🔧 Development

### Code formatting

```bash
# Format code with black
black app tests

# Sort imports with isort
isort app tests

# Check code style with flake8
flake8 app tests
```

### Type checking

```bash
# Run mypy type checker
mypy app
```

### Database migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Downgrade migrations
alembic downgrade -1
```

## 📊 Health Checks

The application provides several health check endpoints:

- **GET /api/v1/health** - Comprehensive health check
- **GET /api/v1/health/ready** - Readiness check (for Kubernetes)
- **GET /api/v1/health/live** - Liveness check (for Kubernetes)
- **GET /api/v1/health/version** - Version information

Example health check response:

```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "version": "0.1.0",
  "environment": "development",
  "checks": {
    "database": {
      "status": "healthy",
      "details": {
        "connection": "active",
        "query_time": "< 1ms"
      }
    },
    "redis": {
      "status": "healthy",
      "details": {
        "connection": "active",
        "ping": "pong"
      }
    }
  }
}
```

## 🏗️ Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI app entry point
│   ├── config.py                # Settings with pydantic-settings
│   ├── dependencies.py          # Dependency injection
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── database.py         # SQLAlchemy setup
│   │   ├── redis_client.py     # Redis connection
│   │   └── logging_config.py   # Structured logging
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── health.py       # Health check endpoint
│   │
│   ├── models/                 # SQLAlchemy models
│   ├── schemas/                # Pydantic schemas
│   ├── agents/                 # AI agents
│   └── workflows/              # Workflow orchestration
│
├── tests/                      # Test modules
├── alembic/                    # Database migrations
├── requirements.txt            # Python dependencies
├── pyproject.toml             # Project configuration
└── README.md                  # This file
```

## 🔐 Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `APP_NAME` | Application name | "ArchMesh PoC" | No |
| `APP_VERSION` | Application version | "0.1.0" | No |
| `DEBUG` | Debug mode | false | No |
| `ENVIRONMENT` | Environment (development/staging/production) | "development" | No |
| `DATABASE_URL` | Database connection URL | postgresql+asyncpg://... | Yes |
| `REDIS_URL` | Redis connection URL | redis://localhost:6380/0 | Yes |
| `LOG_LEVEL` | Log level | "INFO" | No |
| `OPENAI_API_KEY` | OpenAI API key | None | No |
| `ANTHROPIC_API_KEY` | Anthropic API key | None | No |

## 🚀 Deployment

### Docker

```bash
# Build image
docker build -t archmesh-poc-backend .

# Run container
docker run -p 8000:8000 --env-file .env archmesh-poc-backend
```

### Kubernetes

See the `k8s/` directory for Kubernetes deployment manifests.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support, email team@archmesh.com or create an issue in the repository.

## 🔄 Changelog

### v0.1.0 (2024-01-15)
- Initial release
- FastAPI application setup
- Database and Redis integration
- Health check endpoints
- Basic testing framework
- AI/LLM integration foundation
