# backend/app/services/search.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_, select, func
from fastapi import HTTPException
from ..models.book import Book
from ..database.cache import redis_client
import json
import hashlib

async def search_books(
    db: AsyncSession,
    query: str,
    author: str = None,
    genre: str = None,
    min_rating: float = None,
    max_pages: int = None,
    page: int = 1,
    per_page: int = 10
):
    # Create consistent cache key
    params = {
        "query": query,
        "author": author,
        "genre": genre,
        "min_rating": min_rating,
        "max_pages": max_pages,
        "page": page,
        "per_page": per_page
    }
    cache_key = f"search:{hashlib.md5(json.dumps(params).encode()).hexdigest()}"
    
    # Check cache
    try:
        if cached := await redis_client.get(cache_key):
            return json.loads(cached)
    except Exception as e:
        print(f"Cache error: {e}")  # Log but continue
    
    # Build query
    base_query = select(Book)
    
    # Text search conditions
    text_conditions = []
    if query:
        text_conditions.append(
            Book.search_vector.op("@@")(func.to_tsquery('english', query))
        )
    
    # Apply filters
    if author:
        base_query = base_query.where(Book.author.ilike(f"%{author}%"))
    if genre:
        base_query = base_query.where(Book.genre.ilike(f"%{genre}%"))
    if min_rating is not None:
        base_query = base_query.where(Book.average_rating >= min_rating)
    if max_pages is not None:
        base_query = base_query.where(Book.page_count <= max_pages)
    if text_conditions:
        base_query = base_query.where(or_(*text_conditions))
    
    # Get total count
    total = await db.scalar(select(func.count()).select_from(base_query.subquery()))
    
    # Get paginated results
    results = await db.execute(
        base_query.order_by(Book.average_rating.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    
    books = results.scalars().all()
    response = {
        "results": [{
            "isbn": book.isbn,
            "title": book.title,
            "author": book.author,
            "genre": book.genre,
            "page_count": book.page_count,
            "average_rating": book.average_rating,
            "cover_url": book.cover_url
        } for book in books],
        "meta": {
            "total": total,
            "page": page,
            "per_page": per_page
        }
    }
    
    # Cache results (with error handling)
    try:
        await redis_client.set(cache_key, json.dumps(response), ex=3600)
    except Exception as e:
        print(f"Cache set error: {e}")
    
    return response