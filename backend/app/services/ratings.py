# backend/app/services/ratings.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from backend.app.models.rating import Rating
from backend.app.schemas.rating import RatingCreate
from fastapi import HTTPException, status


async def rate_book(db: AsyncSession, user_id: int, rating_data: RatingCreate):
    # Check if rating exists
    result = await db.execute(
        select(Rating)
        .where(Rating.user_id == user_id)
        .where(Rating.book_isbn == rating_data.book_isbn)
    )
    existing = result.scalars().first()
    
    if existing:
        await db.execute(
            update(Rating)
            .where(Rating.id == existing.id)
            .values(rating=rating_data.rating)
        )
    else:
        db_rating = Rating(
            user_id=user_id,
            book_isbn=rating_data.book_isbn,
            rating=rating_data.rating
        )
        db.add(db_rating)

    await db.commit()
    await db.refresh(db_rating if not existing else existing)

    return db_rating if not existing else existing

async def delete_rating(db: AsyncSession, user_id: int, book_isbn: str):
    # Check if rating exists
    result = await db.execute(
        select(Rating)
        .where(Rating.user_id == user_id)
        .where(Rating.book_isbn == book_isbn)
    )
    rating = result.scalars().first()
    
    if not rating:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rating not found"
        )
    
    await db.delete(rating)
    await db.commit()
    return True