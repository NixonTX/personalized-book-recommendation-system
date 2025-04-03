# backend/app/schemas/review.py
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, validator
from typing import Optional

from backend.app.schemas.user import UserBase

class ReviewStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"

class ReviewBase(BaseModel):
    book_isbn: str = Field(..., min_length=10, max_length=20)
    content: str = Field(..., min_length=50, max_length=2000)
    rating: Optional[int] = Field(None, ge=1, le=5)

    @validator('content')
    def validate_content(cls, v):
        if len(v.strip()) < 50:
            raise ValueError("Review must be at least 50 characters")
        return v.strip()

class ReviewCreate(ReviewBase):
    pass

class ReviewUpdate(BaseModel):
    content: str = Field(..., min_length=50, max_length=2000)
    rating: Optional[int] = Field(None, ge=1, le=5)

class Review(ReviewBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    is_edited: bool
    status: ReviewStatus
    
    class Config:
        from_attributes = True
        use_enum_values = True

class ReviewOut(Review):
    user: 'UserBase'  # Assuming you have a UserBase schema
    
    class Config:
        from_attributes = True

class PaginatedReviews(BaseModel):
    reviews: list[ReviewOut]
    total: int
    page: int
    per_page: int