# backend/app/api/v1/books.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.models.book import Book as BookModel
from backend.app.schemas.book import Book as BookSchema, BookCreate
from backend.app.database.db import get_db
from backend.app.services.books import get_book_details, create_book,  get_book_with_ratings


router = APIRouter()

@router.get("/books/{isbn}", response_model=BookSchema)
async def read_book(isbn: str, db: AsyncSession = Depends(get_db)):
    book = await get_book_with_ratings(db, isbn)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@router.post("/books/", response_model=BookSchema, status_code=status.HTTP_201_CREATED)
async def create_book_endpoint(book: BookCreate, db: AsyncSession = Depends(get_db)):
    db_book = await create_book(db, book)
    return BookSchema(
        isbn=db_book.isbn,
        title=db_book.title,
        author=db_book.author,
        description=db_book.description,
        cover_url=db_book.cover_url,
        genre=db_book.genre,
        page_count=db_book.page_count,
        average_rating=db_book.average_rating
    )