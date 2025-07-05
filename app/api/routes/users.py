"""
Users API routes for the Multi-Domain Research Agent.

This module provides the REST API endpoints for user management functionality.
"""

import logging
from typing import Dict, Any, List, Optional

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field, EmailStr
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.utils.monitoring import get_logger, metrics

logger = get_logger(__name__)
router = APIRouter()

# In-memory storage for development (replace with database later)
users_registry: Dict[str, Dict[str, Any]] = {}


class UserInfo(BaseModel):
    """Model for user information."""
    
    user_id: str = Field(..., description="User ID")
    username: str = Field(..., description="Username", min_length=3, max_length=50)
    email: EmailStr = Field(..., description="Email address")
    full_name: Optional[str] = Field(None, description="Full name")
    is_active: bool = Field(default=True, description="User active status")
    research_count: int = Field(default=0, description="Number of research queries")
    created_at: Optional[str] = Field(None, description="Creation timestamp")
    last_login: Optional[str] = Field(None, description="Last login timestamp")


class UserStats(BaseModel):
    """Model for user statistics."""
    
    total_users: int = Field(..., description="Total number of users")
    active_users: int = Field(..., description="Number of active users")
    total_research_queries: int = Field(..., description="Total research queries")
    average_queries_per_user: float = Field(..., description="Average queries per user")


@router.get("/", response_model=List[UserInfo])
async def list_users(
    is_active: Optional[bool] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    List users.
    
    Args:
        is_active: Filter by active status
        limit: Maximum number of users to return
        offset: Number of users to skip
        db: Database session
    
    Returns:
        List[UserInfo]: List of users
    """
    try:
        users = list(users_registry.values())
        
        # Apply filters
        if is_active is not None:
            users = [u for u in users if u.get("is_active") == is_active]
        
        # Apply pagination
        paginated_users = users[offset:offset + limit]
        
        return [
            UserInfo(
                user_id=user["user_id"],
                username=user["username"],
                email=user["email"],
                full_name=user.get("full_name"),
                is_active=user.get("is_active", True),
                research_count=user.get("research_count", 0),
                created_at=user.get("created_at"),
                last_login=user.get("last_login")
            )
            for user in paginated_users
        ]
        
    except Exception as e:
        logger.error(f"❌ Failed to list users: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list users: {str(e)}"
        )


@router.get("/{user_id}", response_model=UserInfo)
async def get_user(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Get user information by ID.
    
    Args:
        user_id: User ID
        db: Database session
    
    Returns:
        UserInfo: User information
    """
    try:
        if user_id not in users_registry:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )
        
        user = users_registry[user_id]
        
        return UserInfo(
            user_id=user["user_id"],
            username=user["username"],
            email=user["email"],
            full_name=user.get("full_name"),
            is_active=user.get("is_active", True),
            research_count=user.get("research_count", 0),
            created_at=user.get("created_at"),
            last_login=user.get("last_login")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get user: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get user: {str(e)}"
        )


@router.get("/stats/summary", response_model=UserStats)
async def get_user_stats(
    db: Session = Depends(get_db)
):
    """
    Get user statistics.
    
    Args:
        db: Database session
    
    Returns:
        UserStats: User statistics
    """
    try:
        users = list(users_registry.values())
        
        # Calculate statistics
        total_users = len(users)
        active_users = len([u for u in users if u.get("is_active", True)])
        
        # Calculate research statistics
        total_research_queries = sum(u.get("research_count", 0) for u in users)
        average_queries_per_user = total_research_queries / total_users if total_users > 0 else 0.0
        
        return UserStats(
            total_users=total_users,
            active_users=active_users,
            total_research_queries=total_research_queries,
            average_queries_per_user=average_queries_per_user
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to get user stats: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get user stats: {str(e)}"
        )


@router.post("/", response_model=UserInfo)
async def create_user(
    user: UserInfo,
    db: Session = Depends(get_db)
):
    """
    Create a new user.
    
    Args:
        user: User information
        db: Database session
    
    Returns:
        UserInfo: Created user information
    """
    try:
        # Check if user already exists
        if user.user_id in users_registry:
            raise HTTPException(
                status_code=409,
                detail="User already exists"
            )
        
        # Check if username is taken
        for existing_user in users_registry.values():
            if existing_user["username"] == user.username:
                raise HTTPException(
                    status_code=409,
                    detail="Username already taken"
                )
        
        # Create the user
        users_registry[user.user_id] = {
            "user_id": user.user_id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "research_count": user.research_count,
            "created_at": user.created_at,
            "last_login": user.last_login
        }
        
        logger.info(f"👤 User created: {user.user_id}")
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to create user: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create user: {str(e)}"
        )


@router.put("/{user_id}", response_model=UserInfo)
async def update_user(
    user_id: str,
    user_update: UserInfo,
    db: Session = Depends(get_db)
):
    """
    Update user information.
    
    Args:
        user_id: User ID
        user_update: Updated user information
        db: Database session
    
    Returns:
        UserInfo: Updated user information
    """
    try:
        if user_id not in users_registry:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )
        
        # Update the user
        users_registry[user_id].update({
            "username": user_update.username,
            "email": user_update.email,
            "full_name": user_update.full_name,
            "is_active": user_update.is_active,
            "research_count": user_update.research_count,
            "last_login": user_update.last_login
        })
        
        logger.info(f"👤 User updated: {user_id}")
        
        return user_update
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to update user: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update user: {str(e)}"
        )


@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete a user.
    
    Args:
        user_id: User ID
        db: Database session
    
    Returns:
        dict: Deletion confirmation
    """
    try:
        if user_id not in users_registry:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )
        
        del users_registry[user_id]
        
        logger.info(f"🗑️ User deleted: {user_id}")
        
        return {"message": "User deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to delete user: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete user: {str(e)}"
        ) 