# backend/app/api/v1/bookmarks.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.schemas.bookmarks import (
    BookmarkCreate,
    Bookmark,
    PaginatedUserBookmarks
)
from backend.app.services.bookmarks import (
    bookmark_book,
    unbookmark_book,
    get_user_bookmarks
)
from backend.app.database.db import get_db
from backend.app.core.auth import get_current_user
from backend.app.models.user import User

router = APIRouter(tags=["User Bookmarks"])

@router.post("/bookmarks/", response_model=Bookmark, status_code=status.HTTP_201_CREATED)
async def create_bookmark(
    bookmark: BookmarkCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await bookmark_book(db, current_user.id, bookmark)

@router.delete("/bookmarks/{book_isbn}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bookmark(
    book_isbn: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    await unbookmark_book(db, current_user.id, book_isbn)
    return None

@router.get("/bookmarks/me/", response_model=PaginatedUserBookmarks)
async def get_my_bookmarks(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await get_user_bookmarks(db, current_user.id, page, per_page)