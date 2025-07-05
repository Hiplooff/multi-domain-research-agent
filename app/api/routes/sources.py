"""
Sources API routes for the Multi-Domain Research Agent.

This module provides the REST API endpoints for source management functionality.
"""

import logging
from typing import Dict, Any, List, Optional

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.utils.monitoring import get_logger, metrics

logger = get_logger(__name__)
router = APIRouter()

# In-memory storage for development (replace with database later)
sources_registry: Dict[str, Dict[str, Any]] = {}


class SourceInfo(BaseModel):
    """Model for source information."""
    
    source_id: str = Field(..., description="Source ID")
    title: str = Field(..., description="Source title")
    url: str = Field(..., description="Source URL")
    type: str = Field(..., description="Source type")
    description: Optional[str] = Field(None, description="Source description")
    credibility_score: Optional[float] = Field(None, description="Credibility score", ge=0.0, le=1.0)
    last_accessed: Optional[str] = Field(None, description="Last access timestamp")
    status: str = Field(default="active", description="Source status")


class SourceStats(BaseModel):
    """Model for source statistics."""
    
    total_sources: int = Field(..., description="Total number of sources")
    active_sources: int = Field(..., description="Number of active sources")
    source_types: Dict[str, int] = Field(..., description="Source types count")
    average_credibility: float = Field(..., description="Average credibility score")


@router.get("/", response_model=List[SourceInfo])
async def list_sources(
    source_type: Optional[str] = Query(None, description="Filter by source type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, description="Maximum number of sources", ge=1, le=100),
    offset: int = Query(0, description="Number of sources to skip", ge=0),
    db: Session = Depends(get_db)
):
    """
    List available sources.
    
    Args:
        source_type: Filter by source type
        status: Filter by status
        limit: Maximum number of sources to return
        offset: Number of sources to skip
        db: Database session
    
    Returns:
        List[SourceInfo]: List of sources
    """
    try:
        sources = list(sources_registry.values())
        
        # Apply filters
        if source_type:
            sources = [s for s in sources if s.get("type") == source_type]
        
        if status:
            sources = [s for s in sources if s.get("status") == status]
        
        # Apply pagination
        paginated_sources = sources[offset:offset + limit]
        
        return [
            SourceInfo(
                source_id=source["source_id"],
                title=source["title"],
                url=source["url"],
                type=source["type"],
                description=source.get("description"),
                credibility_score=source.get("credibility_score"),
                last_accessed=source.get("last_accessed"),
                status=source.get("status", "active")
            )
            for source in paginated_sources
        ]
        
    except Exception as e:
        logger.error(f"❌ Failed to list sources: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list sources: {str(e)}"
        )


@router.get("/{source_id}", response_model=SourceInfo)
async def get_source(
    source_id: str,
    db: Session = Depends(get_db)
):
    """
    Get source information by ID.
    
    Args:
        source_id: Source ID
        db: Database session
    
    Returns:
        SourceInfo: Source information
    """
    try:
        if source_id not in sources_registry:
            raise HTTPException(
                status_code=404,
                detail="Source not found"
            )
        
        source = sources_registry[source_id]
        
        return SourceInfo(
            source_id=source["source_id"],
            title=source["title"],
            url=source["url"],
            type=source["type"],
            description=source.get("description"),
            credibility_score=source.get("credibility_score"),
            last_accessed=source.get("last_accessed"),
            status=source.get("status", "active")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get source: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get source: {str(e)}"
        )


@router.get("/stats/summary", response_model=SourceStats)
async def get_source_stats(
    db: Session = Depends(get_db)
):
    """
    Get source statistics.
    
    Args:
        db: Database session
    
    Returns:
        SourceStats: Source statistics
    """
    try:
        sources = list(sources_registry.values())
        
        # Calculate statistics
        total_sources = len(sources)
        active_sources = len([s for s in sources if s.get("status") == "active"])
        
        # Count by type
        source_types = {}
        for source in sources:
            source_type = source.get("type", "unknown")
            source_types[source_type] = source_types.get(source_type, 0) + 1
        
        # Calculate average credibility
        credibility_scores = [s.get("credibility_score", 0) for s in sources if s.get("credibility_score")]
        average_credibility = sum(credibility_scores) / len(credibility_scores) if credibility_scores else 0.0
        
        return SourceStats(
            total_sources=total_sources,
            active_sources=active_sources,
            source_types=source_types,
            average_credibility=average_credibility
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to get source stats: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get source stats: {str(e)}"
        )


@router.post("/register", response_model=SourceInfo)
async def register_source(
    source: SourceInfo,
    db: Session = Depends(get_db)
):
    """
    Register a new source.
    
    Args:
        source: Source information
        db: Database session
    
    Returns:
        SourceInfo: Registered source information
    """
    try:
        # Check if source already exists
        if source.source_id in sources_registry:
            raise HTTPException(
                status_code=409,
                detail="Source already exists"
            )
        
        # Register the source
        sources_registry[source.source_id] = {
            "source_id": source.source_id,
            "title": source.title,
            "url": source.url,
            "type": source.type,
            "description": source.description,
            "credibility_score": source.credibility_score,
            "last_accessed": source.last_accessed,
            "status": source.status
        }
        
        logger.info(f"📝 Source registered: {source.source_id}")
        
        return source
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to register source: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to register source: {str(e)}"
        )


@router.put("/{source_id}", response_model=SourceInfo)
async def update_source(
    source_id: str,
    source_update: SourceInfo,
    db: Session = Depends(get_db)
):
    """
    Update source information.
    
    Args:
        source_id: Source ID
        source_update: Updated source information
        db: Database session
    
    Returns:
        SourceInfo: Updated source information
    """
    try:
        if source_id not in sources_registry:
            raise HTTPException(
                status_code=404,
                detail="Source not found"
            )
        
        # Update the source
        sources_registry[source_id].update({
            "title": source_update.title,
            "url": source_update.url,
            "type": source_update.type,
            "description": source_update.description,
            "credibility_score": source_update.credibility_score,
            "last_accessed": source_update.last_accessed,
            "status": source_update.status
        })
        
        logger.info(f"📝 Source updated: {source_id}")
        
        return source_update
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to update source: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update source: {str(e)}"
        )


@router.delete("/{source_id}")
async def delete_source(
    source_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete a source.
    
    Args:
        source_id: Source ID
        db: Database session
    
    Returns:
        dict: Deletion confirmation
    """
    try:
        if source_id not in sources_registry:
            raise HTTPException(
                status_code=404,
                detail="Source not found"
            )
        
        del sources_registry[source_id]
        
        logger.info(f"🗑️ Source deleted: {source_id}")
        
        return {"message": "Source deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to delete source: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete source: {str(e)}"
        ) 