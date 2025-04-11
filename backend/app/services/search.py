# backend/app/services/search.py
import asyncio
import re
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, or_, select, func, text
from fastapi import HTTPException

from backend.app.database.db import async_session
from backend.app.schemas.search import SearchRequest
from ..models.book import Book
from ..database.cache import redis_client
from backend.utils.popular_books import refresh_popular_books
import json
import hashlib
import sqlalchemy as sa

async def search_books(
    db: AsyncSession,
    search: SearchRequest
):
    # Create consistent cache key
    cache_key = f"search:{hashlib.md5(json.dumps(search.dict(), sort_keys=True).encode()).hexdigest()}"
    
    # Check cache
    try:
        if cached := await redis_client.get(cache_key):
            return json.loads(cached)
    except Exception as e:
        print(f"Cache error: {e}")

    # Get suggestions for query boosting
    suggestions = await get_search_suggestions(
        db, 
        search.query, 
        limit_titles=0,
        limit_popular=0
    )
    
    # Base query
    base_query = select(Book)
    
    # Text search conditions
    conditions = []
    if search.query:
        conditions.append(
            Book.search_vector.op("@@")(func.plainto_tsquery('english', search.query))
        )
    
    # Apply query boost from suggestions
    if suggestions.get("authors"):
        author_names = [a["name"] for a in suggestions["authors"]]
        conditions.append(Book.author.in_(author_names))
    
    # Apply filters
    filter_conditions = []
    if search.filters:
        if search.filters.genres:
            genre_conditions = [Book.genre.ilike(genre) for genre in search.filters.genres]
            filter_conditions.append(or_(*genre_conditions))
        
        if search.filters.min_rating is not None:
            filter_conditions.append(Book.average_rating >= search.filters.min_rating)
        
        if search.filters.max_pages is not None:
            filter_conditions.append(or_(
                Book.page_count <= search.filters.max_pages,
                Book.page_count == None
            ))
        
        if search.filters.author:
            filter_conditions.append(Book.author.ilike(f"%{search.filters.author}%"))
    
    # Combine all conditions
    if conditions:
        base_query = base_query.where(and_(*conditions))
    if filter_conditions:
        base_query = base_query.where(and_(*filter_conditions))
    
    # Get total count
    total = await db.scalar(
        select(func.count()).select_from(base_query.subquery())
    )
    
    # Determine ordering
    order_criteria = (
        Book.average_rating.desc() 
        if search.filters and search.filters.min_rating is not None 
        else None
    )
    
    query_exec = base_query
    if order_criteria is not None:
        query_exec = query_exec.order_by(order_criteria)
    
    query_exec = query_exec.offset((search.page - 1) * search.per_page).limit(search.per_page)
    
    results = await db.execute(query_exec)
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
            "page": search.page,
            "per_page": search.per_page,
            "filters": {
                "applied": search.filters.dict() if search.filters else None,
                "available": await get_available_filters(db, base_query)
            }
        }
    }
    
    # Cache results
    try:
        await redis_client.set(cache_key, json.dumps(response), ex=3600)
    except Exception as e:
        print(f"Cache set error: {e}")
    
    return response


async def get_available_filters(db: AsyncSession, base_query):
    """Get available filter values for the current result set"""
    subq = base_query.subquery()
    
    # Get available genres
    genres_result = await db.execute(
        select(subq.c.genre).distinct().where(subq.c.genre != None)
    )
    genres = [g for g, in genres_result.all()]
    
    # Get rating range
    rating_stats = await db.execute(
        select(
            func.min(subq.c.average_rating),
            func.max(subq.c.average_rating)
        )
    )
    rating_min, rating_max = rating_stats.one_or_none() or (None, None)
    
    # Get page count range
    page_stats = await db.execute(
        select(
            func.min(subq.c.page_count),
            func.max(subq.c.page_count)
        ).where(subq.c.page_count != None)
    )
    pages_min, pages_max = page_stats.one_or_none() or (None, None)
    
    return {
        "genres": genres,
        "rating_min": rating_min,
        "rating_max": rating_max,
        "pages_min": pages_min,
        "pages_max": pages_max
    }

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
    async with async_session() as title_session, \
              async_session() as author_session, \
              async_session() as popular_session:
        
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