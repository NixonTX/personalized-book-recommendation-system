# backend/app/core/auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.models.user import User
from backend.app.database.db import get_db

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_current_user(
    api_key: str = Depends(api_key_header),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Mock authentication - replace with real auth later"""
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API Key"
        )
    
    # In a real system, you'd verify the key against your auth system
    # For now, we'll just return a mock user
    result = await db.execute(select(User).where(User.id == int(api_key)))
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
        
    return user