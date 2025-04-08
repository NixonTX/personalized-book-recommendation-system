# backend/app/api/v1/search.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.services.search import get_search_suggestions, search_books
from backend.app.schemas.search import SearchRequest, SearchResponse, SuggestionResponse
from backend.app.database.db import get_db
from backend.app.core.auth import get_current_user
from backend.app.database.cache import redis_client

router = APIRouter(tags=["Search"])

# @router.get("/redis-test")
# async def redis_test():
#     try:
#         await redis_client.ping()
#         return {"status": "Redis connected"}
#     except Exception as e:
#         return {"status": f"Redis error: {str(e)}"}

@router.get("/search", response_model=SearchResponse)
async def search(
    query: str = Query(..., min_length=2),
    author: str = Query(None),
    genre: str = Query(None),
    min_rating: float = Query(None, ge=1, le=5),
    max_pages: int = Query(None, gt=0),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user)  # Auth required but not used
):
    return await search_books(
        db=db,
        query=query,
        author=author,
        genre=genre,
        min_rating=min_rating,
        max_pages=max_pages,
        page=page,
        per_page=per_page
    )

@router.get("/search/suggestions", response_model=SuggestionResponse)
async def get_suggestions(
    q: str = Query(..., min_length=2, max_length=50),
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user)  # Auth required
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