# backend/app/schemas/rating.py
from datetime import datetime
from pydantic import BaseModel, Field
from backend.app.schemas.book import Book

class RatingBase(BaseModel):
    book_isbn: str = Field(..., min_length=10, max_length=20)
    rating: int = Field(..., ge=1, le=5)

class RatingCreate(RatingBase):
    pass

class Rating(RatingBase):
    user_id: int
    created_at: datetime
    updated_at: datetime | None
    
    class Config:
        from_attributes = True

class UserRatingOut(BaseModel):
    book: Book
    rating: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class PaginatedUserRatings(BaseModel):
    ratings: list[UserRatingOut]
    total: int
    page: int
    per_page: int