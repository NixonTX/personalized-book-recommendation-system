# backend/app/models/book.py
from pydantic import BaseModel

class BookBase(BaseModel):
    isbn: str
    title: str
    author: str
    description: str | None = None
    cover_url: str | None = None

class BookCreate(BookBase):
    pass

class Book(BookBase):
    class Config:
        from_attributes = True  # For ORM compatibility (future DB use)