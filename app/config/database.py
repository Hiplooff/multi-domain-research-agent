"""
Database configuration for the Multi-Domain Research Agent.

This module sets up the SQLAlchemy async engine and session management.
"""

import logging
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
from sqlalchemy.pool import NullPool

from app.config.settings import settings

logger = logging.getLogger(__name__)

# For now, use synchronous PostgreSQL until asyncpg is compatible with Python 3.13
database_url = settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")

# Create engine
engine = create_engine(
    database_url,
    echo=settings.database.echo,
    poolclass=NullPool if settings.testing else None,
    future=True
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""
    pass


def init_db():
    """Initialize the database."""
    try:
        # Create tables
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for getting database session.
    
    Yields:
        Session: Database session
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def close_db():
    """Close database connections."""
    engine.dispose()
    logger.info("✅ Database connections closed") 