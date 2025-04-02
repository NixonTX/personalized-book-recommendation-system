from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select, delete, desc
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from backend.app.models.bookmark import Bookmark
from backend.app.models.book import Book
from backend.app.schemas.bookmarks import BookmarkCreate
from backend.app.database.cache import redis_client

async def bookmark_book(db: AsyncSession, user_id: int, bookmark_data: BookmarkCreate):
    # Check if book exists
    book_result = await db.execute(select(Book).where(Book.isbn == bookmark_data.book_isbn))
    if not book_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    
    # Check if already bookmarked
    existing_result = await db.execute(
        select(Bookmark)
        .where(Bookmark.user_id == user_id)
        .where(Bookmark.book_isbn == bookmark_data.book_isbn)
    )
    if existing_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Book already bookmarked"
        )
    
    # Create new bookmark
    db_bookmark = Bookmark(
        user_id=user_id,
        book_isbn=bookmark_data.book_isbn
    )
    db.add(db_bookmark)
    await db.commit()
    await db.refresh(db_bookmark)
    
    # Clear relevant caches
    redis_client.delete(f"user:{user_id}:bookmarks")
    return db_bookmark

async def unbookmark_book(db: AsyncSession, user_id: int, book_isbn: str):
    # Check if bookmark exists
    result = await db.execute(
        select(Bookmark)
        .where(Bookmark.user_id == user_id)
        .where(Bookmark.book_isbn == book_isbn)
    )
    bookmark = result.scalar_one_or_none()
    
    if not bookmark:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bookmark not found"
        )
    
    await db.delete(bookmark)
    await db.commit()
    
    # Clear relevant caches
    redis_client.delete(f"user:{user_id}:bookmarks")
    redis_client.delete(f"book:{book_isbn}")
    return True

async def get_user_bookmarks(
    db: AsyncSession, 
    user_id: int, 
    page: int = 1, 
    per_page: int = 10
):
    # Calculate offset
    offset = (page - 1) * per_page

    # Get total count
    total = (await db.execute(
        select(func.count()).select_from(Bookmark).where(Bookmark.user_id == user_id)
    )).scalar_one()
    
    # Get paginated bookmarks with book details
    result = await db.execute(
        select(Bookmark)
        .options(selectinload(Bookmark.book))
        .where(Bookmark.user_id == user_id)
        .order_by(desc(Bookmark.created_at))
        .offset(offset)
        .limit(per_page)
    )
    
    return {
        "bookmarks": result.scalars().all(),
        "total": total,
        "page": page,
        "per_page": per_page
    }
