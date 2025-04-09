# backend/app/api/v1/search.py
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.services.search import get_search_suggestions, search_books
from backend.app.schemas.search import SearchRequest, SearchResponse, SuggestionResponse, SearchHistoryResponse, DeleteHistoryResponse
from backend.app.database.db import get_db
from backend.app.core.auth import get_current_user
from backend.app.database.cache import redis_client
from backend.app.services.search_history import SearchHistoryService

router = APIRouter(tags=["Search"])

@router.get("/search", response_model=SearchResponse)
async def search(
    q: str = Query(..., min_length=2),
    genre: Optional[List[str]] = Query(None),
    min_rating: Optional[float] = Query(None, ge=1, le=5),
    max_pages: Optional[int] = Query(None, gt=0),
    author: Optional[str] = Query(None, min_length=2),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    try:
        filters = None
        if any([genre, min_rating, max_pages, author]):
            filters = {
                "genres": genre,
                "min_rating": min_rating,
                "max_pages": max_pages,
                "author": author
            }
        
        search_request = SearchRequest(
            query=q,
            filters=filters,
            page=page,
            per_page=per_page
        )
        results = await search_books(db, search_request)
        
        # Log successful searches (only if we got results)
        if results["meta"]["total"] > 0:
            await SearchHistoryService.log_search(db, current_user.id, q)
        
        return results
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )

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