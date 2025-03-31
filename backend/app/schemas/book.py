from pydantic import BaseModel, Field
from typing import Optional

class BookBase(BaseModel):
    isbn: str = Field(..., min_length=10, max_length=20, example="9780061120084")
    title: str = Field(..., min_length=1, max_length=100, example="To Kill a Mockingbird")
    author: str = Field(..., max_length=50, example="Harper Lee")
    description: Optional[str] = Field(None, example="A classic novel about racial inequality...")
    cover_url: Optional[str] = Field(None, max_length=255, example="https://example.com/cover.jpg")

class BookCreate(BookBase):
    pass

class Book(BookBase):
    class Config:
        from_attributes = True  # Allows ORM mode (formerly ORM_mode)