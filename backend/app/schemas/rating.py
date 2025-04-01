# backend/app/schemas/rating.py
from datetime import datetime
from pydantic import BaseModel, Field

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