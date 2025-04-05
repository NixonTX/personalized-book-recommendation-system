# backend/app/schemas/search.py
from pydantic import BaseModel, Field
from typing import Optional

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=2)
    author: Optional[str] = None
    genre: Optional[str] = None
    min_rating: Optional[float] = Field(None, ge=1, le=5)
    max_pages: Optional[int] = Field(None, gt=0)
    page: int = Field(1, ge=1)
    per_page: int = Field(10, ge=1, le=100)

class SearchResult(BaseModel):
    isbn: str
    title: str
    author: str
    genre: Optional[str]
    page_count: Optional[int]
    average_rating: Optional[float]
    cover_url: Optional[str]

class SearchResponse(BaseModel):
    results: list[SearchResult]
    meta: dict