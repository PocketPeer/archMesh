"""
FastAPI application entry point.

This module creates and configures the FastAPI application with all
middleware, routers, and startup/shutdown events.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

from app.config import settings
from app.core.database import init_db, close_db
from app.core.redis_client import init_redis, close_redis
from app.core.logging_config import get_logger
from app.api.v1 import health, projects, workflows, brownfield

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager.
    
    Handles startup and shutdown events for the FastAPI application.
    
    Args:
        app: FastAPI application instance
        
    Yields:
        None: Control back to the application
    """
    # Startup
    logger.info("Starting ArchMesh PoC application...")
    
    try:
        # Initialize database
        await init_db()
        logger.info("Database initialized successfully")
        
        # Initialize Redis
        await init_redis()
        logger.info("Redis initialized successfully")
        
        logger.info("Application startup completed")
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down ArchMesh PoC application...")
    
    try:
        # Close Redis connections
        await close_redis()
        logger.info("Redis connections closed")
        
        # Close database connections
        await close_db()
        logger.info("Database connections closed")
        
        logger.info("Application shutdown completed")
        
    except Exception as e:
        logger.error(f"Error during application shutdown: {e}")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered architecture document analysis and processing",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    openapi_url="/openapi.json" if settings.debug else None,
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Custom exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    Handle request validation errors.
    
    Args:
        request: FastAPI request object
        exc: Validation exception
        
    Returns:
        JSONResponse: Error response with validation details
    """
    logger.warning(f"Validation error on {request.url}: {exc.errors()}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation error",
            "errors": exc.errors(),
            "body": exc.body,
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle general exceptions.
    
    Args:
        request: FastAPI request object
        exc: Exception instance
        
    Returns:
        JSONResponse: Error response
    """
    logger.error(f"Unhandled exception on {request.url}: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "message": "An unexpected error occurred" if settings.is_production else str(exc),
        },
    )


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Log all HTTP requests and responses.
    
    Args:
        request: FastAPI request object
        call_next: Next middleware/handler
        
    Returns:
        Response: HTTP response
    """
    # Log request
    logger.info(
        f"Request: {request.method} {request.url}",
        extra={
            "method": request.method,
            "url": str(request.url),
            "client_ip": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
        }
    )
    
    # Process request
    response = await call_next(request)
    
    # Log response
    logger.info(
        f"Response: {response.status_code}",
        extra={
            "status_code": response.status_code,
            "method": request.method,
            "url": str(request.url),
        }
    )
    
    return response


# Include API routers
app.include_router(
    health.router,
    prefix=settings.api_v1_prefix,
    tags=["health"],
)

app.include_router(
    projects.router,
    prefix=settings.api_v1_prefix,
    tags=["projects"],
)

app.include_router(
    workflows.router,
    prefix=settings.api_v1_prefix,
    tags=["workflows"],
)

app.include_router(
    brownfield.router,
    prefix=settings.api_v1_prefix,
    tags=["brownfield"],
)


# Root endpoint
@app.get("/", tags=["root"])
async def root() -> dict:
    """
    Root endpoint with application information.
    
    Returns:
        dict: Application metadata
    """
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "docs_url": "/docs" if settings.debug else None,
        "api_prefix": settings.api_v1_prefix,
    }


# Custom OpenAPI schema
def custom_openapi():
    """
    Generate custom OpenAPI schema.
    
    Returns:
        dict: OpenAPI schema
    """
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=settings.app_name,
        version=settings.app_version,
        description="AI-powered architecture document analysis and processing",
        routes=app.routes,
    )
    
    # Add custom tags
    openapi_schema["tags"] = [
        {
            "name": "health",
            "description": "Health check endpoints",
        },
        {
            "name": "projects",
            "description": "Project management endpoints",
        },
        {
            "name": "workflows",
            "description": "Workflow session management endpoints",
        },
        {
            "name": "brownfield",
            "description": "Brownfield analysis and knowledge base endpoints",
        },
        {
            "name": "root",
            "description": "Root endpoints",
        },
    ]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


# Development-only endpoints
if settings.debug:
    
    @app.get("/debug/info", tags=["debug"])
    async def debug_info() -> dict:
        """
        Debug information endpoint (development only).
        
        Returns:
            dict: Debug information
        """
        return {
            "debug": True,
            "environment": settings.environment,
            "database_url": settings.database_url.replace(settings.database_url.split("@")[0].split("//")[1], "***"),
            "redis_url": settings.redis_url.replace(settings.redis_url.split("@")[0].split("//")[1], "***"),
            "cors_origins": settings.cors_origins,
        }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
