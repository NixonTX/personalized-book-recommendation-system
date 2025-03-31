# backend/app/api/v1/books.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.models.book import Book as BookModel
from backend.app.schemas.book import Book, BookCreate
from backend.app.database.db import get_db
from backend.app.services.books import get_book_details, create_book


router = APIRouter()

@router.get("/books/{isbn}", response_model=Book, responses={404: {"description": "Book not found"}})
async def read_book(isbn: str, db: AsyncSession = Depends(get_db)):
    book = await get_book_details(db, isbn)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@router.post("/books/", response_model=Book, status_code=status.HTTP_201_CREATED)
async def add_book(book: BookCreate, db: AsyncSession = Depends(get_db)):
    return await create_book(db, book.model_dump())