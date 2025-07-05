"""
Research API routes for the Multi-Domain Research Agent.

This module provides the REST API endpoints for research functionality.
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.utils.monitoring import get_logger, metrics

logger = get_logger(__name__)
router = APIRouter()

# In-memory storage for development (replace with database later)
research_sessions: Dict[str, Dict[str, Any]] = {}


class ResearchRequest(BaseModel):
    """Request model for starting research."""
    
    query: str = Field(..., description="Research query", min_length=1, max_length=1000)
    max_sources: Optional[int] = Field(default=10, description="Maximum number of sources", ge=1, le=50)
    complexity: Optional[str] = Field(default="medium", description="Query complexity", pattern="^(simple|medium|complex)$")
    include_sources: Optional[bool] = Field(default=True, description="Include source details")


class ResearchResponse(BaseModel):
    """Response model for research results."""
    
    session_id: str = Field(..., description="Research session ID")
    status: str = Field(..., description="Research status")
    query: str = Field(..., description="Original query")
    message: str = Field(..., description="Status message")
    estimated_time: Optional[int] = Field(None, description="Estimated completion time in seconds")


class ResearchResult(BaseModel):
    """Model for research results."""
    
    session_id: str = Field(..., description="Research session ID")
    query: str = Field(..., description="Original query")
    status: str = Field(..., description="Research status")
    summary: Optional[str] = Field(None, description="Research summary")
    sources: Optional[list] = Field(None, description="Source information")
    confidence_score: Optional[float] = Field(None, description="Confidence score", ge=0.0, le=1.0)
    processing_time: Optional[float] = Field(None, description="Processing time in seconds")
    created_at: Optional[str] = Field(None, description="Creation timestamp")


@router.post("/start", response_model=ResearchResponse)
async def start_research(
    request: ResearchRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Start a new research session.
    
    Args:
        request: Research request parameters
        background_tasks: FastAPI background tasks
        db: Database session
    
    Returns:
        ResearchResponse: Research session information
    """
    try:
        # Generate session ID
        session_id = str(uuid4())
        
        # Store session information
        research_sessions[session_id] = {
            "session_id": session_id,
            "query": request.query,
            "status": "started",
            "max_sources": request.max_sources,
            "complexity": request.complexity,
            "include_sources": request.include_sources,
            "created_at": asyncio.get_event_loop().time()
        }
        
        # Start background research task
        background_tasks.add_task(
            execute_research_background,
            session_id,
            request.query,
            request.max_sources,
            request.complexity
        )
        
        # Update metrics
        metrics.increment_research_queries("started", request.complexity)
        
        logger.info(f"🔍 Research session started: {session_id}", query=request.query)
        
        return ResearchResponse(
            session_id=session_id,
            status="started",
            query=request.query,
            message="Research session started successfully",
            estimated_time=estimate_research_time(request.complexity)
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to start research session: {e}")
        metrics.increment_research_queries("failed", request.complexity)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start research session: {str(e)}"
        )


@router.get("/results/{session_id}", response_model=ResearchResult)
async def get_research_results(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    Get research results for a session.
    
    Args:
        session_id: Research session ID
        db: Database session
    
    Returns:
        ResearchResult: Research results
    """
    try:
        # Check if session exists
        if session_id not in research_sessions:
            raise HTTPException(
                status_code=404,
                detail="Research session not found"
            )
        
        session = research_sessions[session_id]
        
        # Return current session state
        return ResearchResult(
            session_id=session_id,
            query=session["query"],
            status=session["status"],
            summary=session.get("summary"),
            sources=session.get("sources"),
            confidence_score=session.get("confidence_score"),
            processing_time=session.get("processing_time"),
            created_at=session.get("created_at")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get research results: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get research results: {str(e)}"
        )


@router.get("/sessions", response_model=list[ResearchResult])
async def list_research_sessions(
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    List research sessions.
    
    Args:
        limit: Maximum number of sessions to return
        offset: Number of sessions to skip
        db: Database session
    
    Returns:
        list[ResearchResult]: List of research sessions
    """
    try:
        sessions = list(research_sessions.values())
        
        # Apply pagination
        paginated_sessions = sessions[offset:offset + limit]
        
        return [
            ResearchResult(
                session_id=session["session_id"],
                query=session["query"],
                status=session["status"],
                summary=session.get("summary"),
                sources=session.get("sources"),
                confidence_score=session.get("confidence_score"),
                processing_time=session.get("processing_time"),
                created_at=session.get("created_at")
            )
            for session in paginated_sessions
        ]
        
    except Exception as e:
        logger.error(f"❌ Failed to list research sessions: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list research sessions: {str(e)}"
        )


@router.delete("/sessions/{session_id}")
async def delete_research_session(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete a research session.
    
    Args:
        session_id: Research session ID
        db: Database session
    
    Returns:
        dict: Deletion confirmation
    """
    try:
        if session_id not in research_sessions:
            raise HTTPException(
                status_code=404,
                detail="Research session not found"
            )
        
        del research_sessions[session_id]
        
        logger.info(f"🗑️ Research session deleted: {session_id}")
        
        return {"message": "Research session deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to delete research session: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete research session: {str(e)}"
        )


async def execute_research_background(
    session_id: str,
    query: str,
    max_sources: int,
    complexity: str
):
    """
    Execute research in the background.
    
    This is a placeholder implementation that simulates research processing.
    In the actual implementation, this would orchestrate the research workflow.
    """
    try:
        # Update status to processing
        research_sessions[session_id]["status"] = "processing"
        
        # Simulate research processing
        processing_time = estimate_research_time(complexity)
        await asyncio.sleep(processing_time)
        
        # Simulate research results
        research_sessions[session_id].update({
            "status": "completed",
            "summary": f"Research completed for query: {query}",
            "sources": [
                {
                    "title": "Example Source 1",
                    "url": "https://example.com/source1",
                    "type": "web",
                    "relevance_score": 0.95
                },
                {
                    "title": "Example Source 2",
                    "url": "https://example.com/source2",
                    "type": "academic",
                    "relevance_score": 0.87
                }
            ],
            "confidence_score": 0.91,
            "processing_time": processing_time
        })
        
        metrics.increment_research_queries("completed", complexity)
        logger.info(f"✅ Research completed: {session_id}")
        
    except Exception as e:
        # Update status to failed
        research_sessions[session_id]["status"] = "failed"
        research_sessions[session_id]["error"] = str(e)
        
        metrics.increment_research_queries("failed", complexity)
        logger.error(f"❌ Research failed: {session_id}", error=str(e))


def estimate_research_time(complexity: str) -> int:
    """
    Estimate research processing time based on complexity.
    
    Args:
        complexity: Query complexity level
    
    Returns:
        int: Estimated time in seconds
    """
    complexity_times = {
        "simple": 10,
        "medium": 30,
        "complex": 60
    }
    
    return complexity_times.get(complexity, 30) 