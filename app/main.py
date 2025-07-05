"""
Multi-Domain Research Agent - FastAPI Application

This is the main entry point for the FastAPI application that provides
the REST API for the research agent.
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Any, Dict

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from prometheus_client import Counter, Histogram, generate_latest

from app.config.settings import settings
from app.config.database import init_db
from app.api.routes import research, sources, users
from app.utils.monitoring import setup_logging, request_count, request_duration, MetricsCollector

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Import metrics from monitoring module to avoid duplicates


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    logger.info("🚀 Starting Multi-Domain Research Agent")
    
    # Initialize database
    init_db()
    
    # Additional startup tasks
    logger.info("✅ Database initialized")
    logger.info("✅ Research Agent is ready!")
    
    yield
    
    # Cleanup
    logger.info("🔄 Shutting down Research Agent")


# Create FastAPI application
app = FastAPI(
    title="Multi-Domain Research Agent",
    description="A sophisticated, 100% free and open-source research agent using modern Python frameworks",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add process time header and metrics collection."""
    import time
    
    start_time = time.time()
    
    # Process request
    response = await call_next(request)
    
    # Calculate process time
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    # Collect metrics
    MetricsCollector.increment_request_count(
        method=request.method,
        endpoint=request.url.path,
        status_code=response.status_code
    )
    
    MetricsCollector.observe_request_duration(
        method=request.method,
        endpoint=request.url.path,
        duration=process_time
    )
    
    return response


# Include routers
app.include_router(research.router, prefix="/research", tags=["research"])
app.include_router(sources.router, prefix="/sources", tags=["sources"])
app.include_router(users.router, prefix="/users", tags=["users"])


@app.get("/", response_model=Dict[str, Any])
async def root():
    """Root endpoint with basic information."""
    return {
        "message": "Multi-Domain Research Agent API",
        "version": "0.1.0",
        "status": "healthy",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health", response_model=Dict[str, Any])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "0.1.0",
        "timestamp": asyncio.get_event_loop().time(),
        "environment": settings.ENVIRONMENT
    }


@app.get("/metrics")
async def get_metrics():
    """Prometheus metrics endpoint."""
    return JSONResponse(
        content=generate_latest().decode('utf-8'),
        media_type="text/plain"
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Global exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "type": type(exc).__name__
        }
    )


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_RELOAD,
        log_level=settings.LOG_LEVEL.lower()
    ) 