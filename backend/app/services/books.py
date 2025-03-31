from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.models.book import Book
from backend.app.database.db import engine
from backend.app.database.cache import redis_client
from backend.app.schemas.book import BookCreate
import json

# MOCK_BOOKS = {
#     "9780061120084": {
#         "title": "To Kill a Mockingbird",
#         "author": "Harper Lee",
#         "description": "A classic novel about racial inequality...",
#         "cover_url": "https://example.com/mockingbird.jpg"
#     }
# }


async def get_book_details(db: AsyncSession, isbn: str):
    # Check cache first
    cached_book = redis_client.get(f"book:{isbn}")
    if cached_book:
        cached_data = json.loads(cached_book)
        # Either create a Book instance manually:
        return Book(**cached_data)
    
    # Query database
    result = await db.execute(select(Book).where(Book.isbn == isbn))
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
    return book

async def create_book(db: AsyncSession, book: BookCreate):
    db_book = Book(**book)
    db.add(db_book)
    await db.commit()
    await db.refresh(db_book)
    return db_book