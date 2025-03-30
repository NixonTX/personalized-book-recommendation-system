# backend/app/api/v1/books.py
from fastapi import APIRouter, HTTPException
from backend.app.services.books import get_book_details
from backend.app.models.book import Book

router = APIRouter()

@router.get("/books/{isbn}", response_model=Book)
async def read_book(isbn: str):
    book = get_book_details(isbn)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book