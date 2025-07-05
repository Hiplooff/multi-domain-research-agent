"""
Monitoring utilities for the Multi-Domain Research Agent.

This module provides logging setup and metrics collection functionality.
"""

import logging
import logging.handlers
import os
from pathlib import Path
from typing import Optional

import structlog
from prometheus_client import Counter, Histogram
from rich.console import Console
from rich.logging import RichHandler

from app.config.settings import settings

console = Console()

# Prometheus metrics
request_count = Counter(
    'research_agent_requests_total',
    'Total number of requests',
    ['method', 'endpoint', 'status_code']
)

request_duration = Histogram(
    'research_agent_request_duration_seconds',
    'Request duration in seconds',
    ['method', 'endpoint']
)

research_queries = Counter(
    'research_agent_queries_total',
    'Total number of research queries',
    ['status', 'complexity']
)

source_requests = Counter(
    'research_agent_source_requests_total',
    'Total number of source requests',
    ['source_type', 'status']
)

llm_requests = Counter(
    'research_agent_llm_requests_total',
    'Total number of LLM requests',
    ['model', 'provider', 'status']
)


def setup_logging():
    """Set up logging configuration."""
    
    # Create logs directory if it doesn't exist
    log_file_path = Path(settings.logging.file)
    log_file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer() if settings.logging.format == "json" else structlog.dev.ConsoleRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configure standard logging
    logging.basicConfig(
        level=getattr(logging, settings.logging.level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            RichHandler(console=console, rich_tracebacks=True),
            logging.handlers.RotatingFileHandler(
                filename=settings.logging.file,
                maxBytes=_parse_size(settings.logging.rotation),
                backupCount=5
            )
        ]
    )
    
    # Set specific loggers
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    
    logger = logging.getLogger(__name__)
    logger.info("🔧 Logging configured successfully")


def _parse_size(size_str: str) -> int:
    """Parse size string (e.g., '10MB') to bytes."""
    size_str = size_str.upper()
    
    if size_str.endswith('KB'):
        return int(size_str[:-2]) * 1024
    elif size_str.endswith('MB'):
        return int(size_str[:-2]) * 1024 * 1024
    elif size_str.endswith('GB'):
        return int(size_str[:-2]) * 1024 * 1024 * 1024
    else:
        return int(size_str)


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)


class MetricsCollector:
    """Utility class for collecting application metrics."""
    
    @staticmethod
    def increment_request_count(method: str, endpoint: str, status_code: int):
        """Increment request counter."""
        request_count.labels(
            method=method,
            endpoint=endpoint,
            status_code=status_code
        ).inc()
    
    @staticmethod
    def observe_request_duration(method: str, endpoint: str, duration: float):
        """Observe request duration."""
        request_duration.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)
    
    @staticmethod
    def increment_research_queries(status: str, complexity: str):
        """Increment research query counter."""
        research_queries.labels(
            status=status,
            complexity=complexity
        ).inc()
    
    @staticmethod
    def increment_source_requests(source_type: str, status: str):
        """Increment source request counter."""
        source_requests.labels(
            source_type=source_type,
            status=status
        ).inc()
    
    @staticmethod
    def increment_llm_requests(model: str, provider: str, status: str):
        """Increment LLM request counter."""
        llm_requests.labels(
            model=model,
            provider=provider,
            status=status
        ).inc()


# Create global metrics collector instance
metrics = MetricsCollector() 