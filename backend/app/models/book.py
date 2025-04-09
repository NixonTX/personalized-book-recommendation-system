# backend/app/models/book.py
from sqlalchemy import Column, Integer, String, Text, Float
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy import Index
from sqlalchemy.orm import relationship
from backend.app.database.db import Base

class Book(Base):
    __tablename__ = "books"
    __table_args__ = (
        Index('ix_book_genre', 'genre'),
        Index('ix_book_rating', 'average_rating'),
        Index('ix_book_page_count', 'page_count'),
        Index(
            'ix_book_author_ft', 
            'author',
            postgresql_using='gin',
            postgresql_ops={'author': 'gin_trgm_ops'}
        ),
        {'schema': 'book_schema'}  # Schema moved to the end of the tuple as a dict
    )

    isbn = Column(String(20), primary_key=True)
    title = Column(String(100), nullable=False)
    author = Column(String(50), nullable=False)
    genre = Column(String(30))
    description = Column(Text)
    cover_url = Column(String(255))
    page_count = Column(Integer)
    average_rating = Column(Float)
    search_vector = Column(TSVECTOR)

    ratings = relationship("Rating", back_populates="book")
    bookmarks = relationship("Bookmark", back_populates="book")
    reviews = relationship("Review", back_populates="book")