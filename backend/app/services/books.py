from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.models.book import Book as BookModel  # SQLAlchemy model
from backend.app.models.rating import Rating
from backend.app.database.cache import redis_client
from backend.app.schemas.book import Book as BookSchema  # Pydantic schema
from backend.app.schemas.book import BookCreate
import json
import aiohttp
import os
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
GOOGLE_BOOKS_API_KEY = os.getenv("GOOGLE_BOOKS_API_KEY")

async def get_book_details(db: AsyncSession, isbn: str):
    # Check cache first
    cached_book = await redis_client.get(f"book:{isbn}")
    if cached_book:
        # Handle bytes or str from Redis
        cached_book_str = cached_book.decode('utf-8') if isinstance(cached_book, bytes) else cached_book
        cached_data = json.loads(cached_book_str)
        return BookSchema(**cached_data)  # Return Pydantic schema
    
    # Query database - use BookModel for SQLAlchemy query
    result = await db.execute(select(BookModel).where(BookModel.isbn == isbn))
    book = result.scalars().first()
    
    if book:
        book_data = {
            "isbn": book.isbn,
            "title": book.title,
            "author": book.author,
            "description": book.description,
            "cover_url": book.cover_url,
            "genre": book.genre or "",
            "page_count": book.page_count or 0,
            "average_rating": book.average_rating or None
        }
        await redis_client.setex(f"book:{isbn}", 3600, json.dumps(book_data))
        return BookSchema(**book_data)
    
    # Fetch Google Books API
    async with aiohttp.ClientSession() as session:
        url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}&key={GOOGLE_BOOKS_API_KEY}"
        async with session.get(url) as response:
            logger.info(f"Google Books API request for ISBN {isbn}: {response.status}")
            if response.status != 200:
                logger.error(f"API error: {response.status} - {await response.text()}")
                return None
            data = await response.json()
            logger.info(f"API response: {data}")
            items = data.get("items", [])
            if not items:
                logger.warning(f"No items found for ISBN {isbn}")
                return None
            
            volume_info = items[0].get("volumeInfo", {})
            book_data = {
                "isbn": isbn,
                "title": volume_info.get("title", "Unknown Title"),
                "author": ", ".join(volume_info.get("authors", ["Unknown Author"])),
                "description": volume_info.get("description", ""),
                "cover_url": volume_info.get("imageLinks", {}).get("thumbnail", ""),
                "genre": ", ".join(volume_info.get("categories", [""])),
                "page_count": volume_info.get("pageCount", 0),
                "average_rating": volume_info.get("averageRating", None)
            }
            
            db_book = BookModel(
                isbn=book_data["isbn"],
                title=book_data["title"],
                author=book_data["author"],
                description=book_data["description"],
                cover_url=book_data["cover_url"],
                genre=book_data["genre"],
                page_count=book_data["page_count"],
                average_rating=book_data["average_rating"]
            )
            db.add(db_book)
            await db.commit()
            
            await redis_client.setex(f"book:{isbn}", 604800, json.dumps(book_data))
            return BookSchema(**book_data)

async def create_book(db: AsyncSession, book: BookCreate):
    db_book = BookModel(
        isbn=book.isbn,
        title=book.title,
        author=book.author,
        description=book.description,
        cover_url=book.cover_url,
        genre=book.genre or "",
        page_count=book.page_count or 0,
        average_rating=book.average_rating or None
    )
    db.add(db_book)
    await db.commit()
    await db.refresh(db_book)
    return db_book

async def get_book_with_ratings(db: AsyncSession, isbn: str):
    book = await get_book_details(db, isbn)
    if not book:
        return None
    
    result = await db.execute(
        select(
            func.avg(Rating.rating).label('average_rating'),
            func.count(Rating.rating).label('rating_count')
        )
        .where(Rating.book_isbn == isbn)
    )
    avg_rating, rating_count = result.first()
    
    book_data = book.model_dump()
    book_data.update({
        "average_rating": round(float(avg_rating), 1) if avg_rating else book_data["average_rating"],
        "rating_count": rating_count or 0
    })
    
    return BookSchema(**book_data)