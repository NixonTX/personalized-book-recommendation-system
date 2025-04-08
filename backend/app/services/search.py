# backend/app/services/search.py
import asyncio
import re
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_, select, func, text
from fastapi import HTTPException

from backend.app.database.db import AsyncSessionLocal
from ..models.book import Book
from ..database.cache import redis_client
from backend.utils.popular_books import refresh_popular_books
import json
import hashlib
import sqlalchemy as sa

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
    suggestions = await get_search_suggestions(
        db, 
        query, 
        limit_titles=0,  # We only want author suggestions here
        limit_popular=0
    )
    
    # Build boosted query conditions
    boosted_conditions = []
    if suggestions["authors"]:
        author_names = [a["name"] for a in suggestions["authors"]]
        boosted_conditions.append(Book.author.in_(author_names))
    
    # Add to your existing text_conditions
    if boosted_conditions:
        text_conditions.append(or_(*boosted_conditions))

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

async def get_search_suggestions(
    db: AsyncSession,
    query: str,
    limit_titles: int = 5,
    limit_authors: int = 3,
    limit_popular: int = 2
):
    # Validate and sanitize input
    if len(query) < 2:
        raise HTTPException(
            status_code=400,
            detail="Query must be at least 2 characters"
        )
    
    if not re.match(r'^[\w\s\-]+$', query):
        raise HTTPException(
            status_code=400,
            detail="Invalid characters in query"
        )
    
    cache_key = f"suggest:{query.lower()}"
    
    # Try cache first
    if cached := await redis_client.get(cache_key):
        return json.loads(cached)
    
    # Create new sessions for each query
    async with AsyncSessionLocal() as title_session, \
              AsyncSessionLocal() as author_session, \
              AsyncSessionLocal() as popular_session:
        
        # Fetch title suggestions
        title_query = select(
            Book.isbn,
            Book.title,
            Book.author,
            func.similarity(func.lower(Book.title), func.lower(query)).label("score")
        ).where(
            Book.title.ilike(f"{query}%")
        ).order_by(
            text("score DESC")
        ).limit(limit_titles)
        
        # Fetch author suggestions
        author_query = select(
            Book.author,
            func.count(Book.isbn).label("book_count")
        ).where(
            Book.author.ilike(f"{query}%")
        ).group_by(
            Book.author
        ).order_by(
            text("book_count DESC")
        ).limit(limit_authors)
        
        # Fetch popular books (fallback)
        popular_query = text("""
    SELECT isbn, title, author, avg_rating 
    FROM book_schema.popular_books
    ORDER BY rating_count DESC
    LIMIT :limit
""").columns(
    isbn=sa.String,
    title=sa.String,
    author=sa.String,
    avg_rating=sa.Float
)
        
        # Execute all queries
        title_results = await title_session.execute(title_query)
        author_results = await author_session.execute(author_query)
        popular_results = await popular_session.execute(
            popular_query, {"limit": limit_popular}
        )
        
        # Commit sessions (not strictly necessary for read-only queries)
        await title_session.commit()
        await author_session.commit()
        await popular_session.commit()
        
        # Format response
        suggestions = {
    "titles": [
        {"text": r.title, "isbn": r.isbn, "score": float(r.score)} 
        for r in title_results
    ],
    "authors": [
        {"name": r.author, "book_count": r.book_count}
        for r in author_results
    ],
    "popular": [
        {"title": r.title, "isbn": r.isbn, "rating": float(r.avg_rating)}
        for r in popular_results
    ]
}
        
        # Cache results
        await redis_client.set(
            cache_key,
            json.dumps(suggestions),
            ex=3600  # 1 hour
        )
        
        return suggestions