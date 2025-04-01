# backend/app/api/v1/ratings.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.schemas.rating import RatingCreate, Rating
from backend.app.services.ratings import rate_book
from backend.app.database.db import get_db
from backend.app.core.auth import get_current_user
from backend.app.models.user import User

router = APIRouter()

@router.post("/", response_model=Rating)
async def create_rating(
    rating: RatingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await rate_book(db, current_user.id, rating)