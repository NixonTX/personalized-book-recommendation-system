# backend/app/api/v1/ratings.py
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.schemas.rating import RatingCreate, Rating
from backend.app.services.ratings import delete_rating, rate_book
from backend.app.database.db import get_db
from backend.app.core.auth import get_current_user
from backend.app.models.user import User

router = APIRouter(tags=["Ratings"])

@router.post("/ratings/", response_model=Rating)
async def create_rating(
    rating: RatingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await rate_book(db, current_user.id, rating)

# DELETE /api/v1/ratings/{isbn}
@router.delete("/{isbn}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_rating(  # Renamed to avoid conflict
    isbn: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    await delete_rating(db, current_user.id, isbn)
    return Response(status_code=status.HTTP_204_NO_CONTENT)