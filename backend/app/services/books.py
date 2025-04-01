from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.models.book import Book as BookModel  # SQLAlchemy model
from backend.app.models.rating import Rating
from backend.app.database.cache import redis_client
from backend.app.schemas.book import Book as BookSchema  # Pydantic schema
from backend.app.schemas.book import BookCreate
import json

async def get_book_details(db: AsyncSession, isbn: str):
    # Check cache first
    cached_book = redis_client.get(f"book:{isbn}")
    if cached_book:
        cached_data = json.loads(cached_book)
        return BookSchema(**cached_data)  # Return Pydantic schema
    
    # Query database - use BookModel for SQLAlchemy query
    result = await db.execute(select(BookModel).where(BookModel.isbn == isbn))
    book = result.scalars().first()
    
    if book:
        # Cache for 1 hour (3600 seconds)
        redis_client.setex(
            f"book:{isbn}",
            3600,
            json.dumps({
                "isbn": book.isbn,
                "title": book.title,
                "author": book.author,
                "description": book.description,
                "cover_url": book.cover_url
            })
        )
        # Convert SQLAlchemy model to Pydantic schema
        return BookSchema(
            isbn=book.isbn,
            title=book.title,
            author=book.author,
            description=book.description,
            cover_url=book.cover_url
        )
    return None

async def create_book(db: AsyncSession, book: BookCreate):
    # Use BookModel for database operations
    db_book = BookModel(
        isbn=book.isbn,
        title=book.title,
        author=book.author,
        description=book.description,
        cover_url=book.cover_url
    )
    db.add(db_book)
    await db.commit()
    await db.refresh(db_book)
    return db_book

async def get_book_with_ratings(db: AsyncSession, isbn: str):
    """Get book details with average rating and rating count"""
    # Get base book details - returns Pydantic schema
    book = await get_book_details(db, isbn)
    if not book:
        return None
    
    # Calculate average rating and count
    result = await db.execute(
        select(
            func.avg(Rating.rating).label('average_rating'),
            func.count(Rating.rating).label('rating_count')
        )
        .where(Rating.book_isbn == isbn)
    )
    avg_rating, rating_count = result.first()
    
    # Update the Pydantic schema with rating data
    book_data = book.model_dump()
    book_data.update({
        "average_rating": round(float(avg_rating), 1) if avg_rating else None,
        "rating_count": rating_count or 0
    })
    
    return BookSchema(**book_data)