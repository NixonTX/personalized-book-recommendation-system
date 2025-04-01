# backend/app/services/ratings.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from backend.app.models.rating import Rating
from backend.app.schemas.rating import RatingCreate

async def rate_book(db: AsyncSession, user_id: int, rating_data: RatingCreate):
    # Check if rating exists
    result = await db.execute(
        select(Rating)
        .where(Rating.user_id == user_id)
        .where(Rating.book_isbn == rating_data.book_isbn)
    )
    existing = result.scalars().first()
    
    if existing:
        # Update existing rating
        await db.execute(
            update(Rating)
            .where(Rating.id == existing.id)
            .values(rating=rating_data.rating)
        )
    else:
        # Create new rating
        db_rating = Rating(
            user_id=user_id,
            book_isbn=rating_data.book_isbn,
            rating=rating_data.rating
        )
        db.add(db_rating)
    
    await db.commit()
    return db_rating