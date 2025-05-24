# backend/app/api/v1/search.py
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from services.books import GOOGLE_BOOKS_API_KEY, get_book_details
from sqlalchemy.ext.asyncio import AsyncSession
import aiohttp
from backend.app.services.search import get_search_suggestions, search_books
from backend.app.schemas.search import SearchRequest, SearchResponse, SuggestionResponse, SearchHistoryResponse, DeleteHistoryResponse
from backend.app.database.db import get_db
from backend.app.core.auth import get_current_user
from backend.app.database.cache import redis_client
from backend.app.services.search_history import SearchHistoryService

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(tags=["Search"])

@router.get("/search", response_model=SearchResponse)
async def search_books(
    q: str,
    page: int = 1,
    per_page: int = 10,
    db: AsyncSession = Depends(get_db)
):
    if not q or len(q) < 2:
        raise HTTPException(status_code=400, detail="Query must be at least 2 characters")
    
    # Calculate pagination
    start = (page - 1) * per_page
    max_results = per_page
    
    # Query Google Books API
    async with aiohttp.ClientSession() as session:
        url = f"https://www.googleapis.com/books/v1/volumes?q={q}&key={GOOGLE_BOOKS_API_KEY}&startIndex={start}&maxResults={max_results}"
        async with session.get(url) as response:
            logger.info(f"Google Books API search for query '{q}': {response.status}")
            if response.status == 403:
                error_data = await response.json()
                logger.error(f"API error: {response.status} - {error_data}")
                raise HTTPException(
                    status_code=502,
                    detail="Google Books API access denied. Check API key restrictions."
                )
            if response.status != 200:
                error_text = await response.text()
                logger.error(f"API error: {response.status} - {error_text}")
                raise HTTPException(
                    status_code=502,
                    detail="Failed to fetch books from Google Books API"
                )
            
            data = await response.json()
            logger.info(f"API response: {data}")
            
            total_items = data.get("totalItems", 0)
            items = data.get("items", [])
            
            results = []
            for item in items:
                volume_info = item.get("volumeInfo", {})
                isbn_list = volume_info.get("industryIdentifiers", [])
                isbn = next((i["identifier"] for i in isbn_list if i["type"] == "ISBN_13"), None)
                if not isbn:
                    continue
                
                # Use get_book_details to normalize and cache book data
                book = await get_book_details(db, isbn)
                if book:
                    results.append({
                        "isbn": book.isbn,
                        "title": book.title,
                        "author": book.author
                    })
            
            # Construct response
            response = {
                "results": results,
                "meta": {
                    "total": total_items,
                    "page": page,
                    "per_page": per_page
                }
            }
            
            return response

@router.get("/search/suggestions", response_model=SuggestionResponse)
async def get_suggestions(
    q: str = Query(..., min_length=2, max_length=50),
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    try:
        return await get_search_suggestions(db, q)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get suggestions: {str(e)}"
        )
    
# Search history
@router.get("/search/history", response_model=SearchHistoryResponse)
async def get_search_history(
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    return {
        "recent_searches": await SearchHistoryService.get_search_history(db, current_user.id)
    }

@router.delete("/search/history/{query}", response_model=DeleteHistoryResponse)
async def delete_search_history_item(
    query: str,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    return await SearchHistoryService.clear_search_history(
        db, current_user.id, query
    )

@router.delete("/search/history", response_model=DeleteHistoryResponse)
async def clear_search_history(
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    return await SearchHistoryService.clear_search_history(
        db, current_user.id
    )