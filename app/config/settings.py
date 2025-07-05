"""
Settings configuration for the Multi-Domain Research Agent.

This module handles all configuration settings using Pydantic Settings,
which automatically loads from environment variables.
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseModel):
    """Database configuration settings."""
    
    url: str = Field(
        default="postgresql+asyncpg://user:password@localhost:5432/research_agent",
        description="Database connection URL"
    )
    echo: bool = Field(
        default=False,
        description="Enable SQL query logging"
    )


class RedisSettings(BaseModel):
    """Redis configuration settings."""
    
    url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL"
    )


class OllamaSettings(BaseModel):
    """Ollama configuration settings."""
    
    base_url: str = Field(
        default="http://localhost:11434",
        description="Ollama base URL"
    )
    default_model: str = Field(
        default="llama3:8b",
        description="Default Ollama model"
    )
    timeout: int = Field(
        default=120,
        description="Request timeout in seconds"
    )


class GeminiSettings(BaseModel):
    """Gemini API configuration settings."""
    
    api_key: Optional[str] = Field(
        default=None,
        description="Gemini API key"
    )
    model: str = Field(
        default="gemini-1.5-flash",
        description="Gemini model to use"
    )
    rate_limit: int = Field(
        default=15,
        description="Rate limit per minute"
    )


class LLMSettings(BaseModel):
    """LLM router configuration settings."""
    
    budget_mode: bool = Field(
        default=True,
        description="Enable budget mode for 100% local processing"
    )
    complexity_threshold: float = Field(
        default=0.7,
        description="Complexity threshold for LLM routing"
    )
    max_tokens_local: int = Field(
        default=4096,
        description="Maximum tokens for local LLM"
    )
    max_tokens_cloud: int = Field(
        default=8192,
        description="Maximum tokens for cloud LLM"
    )


class APISettings(BaseModel):
    """API configuration settings."""
    
    host: str = Field(
        default="localhost",
        description="API host"
    )
    port: int = Field(
        default=8000,
        description="API port"
    )
    reload: bool = Field(
        default=True,
        description="Enable auto-reload in development"
    )
    rate_limit_requests: int = Field(
        default=100,
        description="Rate limit requests per window"
    )
    rate_limit_window: int = Field(
        default=60,
        description="Rate limit window in seconds"
    )


class CacheSettings(BaseModel):
    """Cache configuration settings."""
    
    ttl: int = Field(
        default=3600,
        description="Cache time-to-live in seconds"
    )
    max_size: int = Field(
        default=1000,
        description="Maximum cache size"
    )


class LoggingSettings(BaseModel):
    """Logging configuration settings."""
    
    level: str = Field(
        default="INFO",
        description="Log level"
    )
    format: str = Field(
        default="json",
        description="Log format"
    )
    file: str = Field(
        default="logs/research_agent.log",
        description="Log file path"
    )
    rotation: str = Field(
        default="10MB",
        description="Log rotation size"
    )
    retention: str = Field(
        default="30 days",
        description="Log retention period"
    )


class SecuritySettings(BaseModel):
    """Security configuration settings."""
    
    secret_key: str = Field(
        default="your_secret_key_here_change_in_production",
        description="Secret key for JWT tokens"
    )
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8501"],
        description="CORS allowed origins"
    )
    allowed_hosts: List[str] = Field(
        default=["localhost", "127.0.0.1"],
        description="Allowed hosts"
    )


class ResearchSettings(BaseModel):
    """Research configuration settings."""
    
    max_sources_per_query: int = Field(
        default=20,
        description="Maximum sources per query"
    )
    max_search_results: int = Field(
        default=50,
        description="Maximum search results"
    )
    source_timeout: int = Field(
        default=30,
        description="Source timeout in seconds"
    )
    parallel_search_limit: int = Field(
        default=5,
        description="Parallel search limit"
    )


class StreamlitSettings(BaseModel):
    """Streamlit configuration settings."""
    
    server_port: int = Field(
        default=8501,
        description="Streamlit server port"
    )
    server_address: str = Field(
        default="localhost",
        description="Streamlit server address"
    )


class Settings(BaseSettings):
    """Main settings class that loads all configuration."""
    
    # Environment
    environment: str = Field(
        default="development",
        description="Environment (development, staging, production)"
    )
    debug: bool = Field(
        default=True,
        description="Enable debug mode"
    )
    testing: bool = Field(
        default=False,
        description="Enable testing mode"
    )
    
    # Component settings
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    ollama: OllamaSettings = Field(default_factory=OllamaSettings)
    gemini: GeminiSettings = Field(default_factory=GeminiSettings)
    llm: LLMSettings = Field(default_factory=LLMSettings)
    api: APISettings = Field(default_factory=APISettings)
    cache: CacheSettings = Field(default_factory=CacheSettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    research: ResearchSettings = Field(default_factory=ResearchSettings)
    streamlit: StreamlitSettings = Field(default_factory=StreamlitSettings)
    
    # Convenience properties
    @property
    def DATABASE_URL(self) -> str:
        return self.database.url
    
    @property
    def REDIS_URL(self) -> str:
        return self.redis.url
    
    @property
    def OLLAMA_BASE_URL(self) -> str:
        return self.ollama.base_url
    
    @property
    def API_HOST(self) -> str:
        return self.api.host
    
    @property
    def API_PORT(self) -> int:
        return self.api.port
    
    @property
    def API_RELOAD(self) -> bool:
        return self.api.reload
    
    @property
    def LOG_LEVEL(self) -> str:
        return self.logging.level
    
    @property
    def ENVIRONMENT(self) -> str:
        return self.environment
    
    @property
    def CORS_ORIGINS(self) -> List[str]:
        return self.security.cors_origins
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        
        # Nested environment variables
        env_nested_delimiter = "__"
        
        # Allow extra fields
        extra = "allow"


# Create global settings instance
settings = Settings() 