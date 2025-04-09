# backend/app/schemas/search.py
from pydantic import BaseModel, Field
from typing import Optional, List


class SearchFilters(BaseModel):
    genres: Optional[List[str]] = Field(
        None, 
        description="Filter by genre (exact match)"
    )
    min_rating: Optional[float] = Field(
        None, ge=1, le=5, 
        description="Minimum average rating (1-5)"
    )
    max_pages: Optional[int] = Field(
        None, gt=0, 
        description="Maximum page count"
    )
    author: Optional[str] = Field(
        None, min_length=2, 
        description="Partial author name match"
    )

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=2)
    filters: Optional[SearchFilters] = None
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

class TitleSuggestion(BaseModel):
    text: str
    isbn: str
    score: float

class AuthorSuggestion(BaseModel):
    name: str
    book_count: int

class PopularSuggestion(BaseModel):
    title: str
    isbn: str
    rating: float

class SuggestionResponse(BaseModel):
    titles: List[TitleSuggestion] = Field(default_factory=list)
    authors: List[AuthorSuggestion] = Field(default_factory=list)
    popular: List[PopularSuggestion] = Field(default_factory=list)