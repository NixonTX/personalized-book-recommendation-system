# backend/app/schemas/bookmark.py
from datetime import datetime
from pydantic import BaseModel, Field
from backend.app.schemas.book import Book

class BookmarkBase(BaseModel):
    book_isbn: str = Field(..., min_length=10, max_length=20)

class BookmarkCreate(BookmarkBase):
    pass

class Bookmark(BookmarkBase):
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserBookmarkOut(BaseModel):
    book: Book
    created_at: datetime
    
    class Config:
        from_attributes = True

class PaginatedUserBookmarks(BaseModel):
    bookmarks: list[UserBookmarkOut]
    total: int
    page: int
    per_page: int