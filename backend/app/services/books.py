# backend/app/services/books.py
from backend.app.models.book import Book

# Mock data (replace with DB queries later)
MOCK_BOOKS = {
    "9780061120084": {
        "title": "To Kill a Mockingbird",
        "author": "Harper Lee",
        "description": "A classic novel about racial inequality...",
        "cover_url": "https://example.com/mockingbird.jpg"
    }
}

def get_book_details(isbn: str) -> Book | None:
    if isbn in MOCK_BOOKS:
        return Book(isbn=isbn, **MOCK_BOOKS[isbn])
    return None