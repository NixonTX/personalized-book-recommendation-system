# backend/app/models/book.py
from sqlalchemy import Column, Integer, String, Text, Float
from sqlalchemy.dialects.postgresql import TSVECTOR
from backend.app.database.db import Base
from sqlalchemy.orm import relationship

class Book(Base):
    __tablename__ = "books"
    __table_args__ = {'schema': 'book_schema'}

    isbn = Column(String(20), primary_key=True)
    title = Column(String(100), nullable=False)
    author = Column(String(50))
    genre = Column(String(30))
    description = Column(Text)
    cover_url = Column(String(255))
    page_count = Column(Integer)
    average_rating = Column(Float)
    search_vector = Column(TSVECTOR)  # for full-text search

    ratings = relationship("Rating", back_populates="book")
    bookmarks = relationship("Bookmark", back_populates="book")
    reviews = relationship("Review", back_populates="book")