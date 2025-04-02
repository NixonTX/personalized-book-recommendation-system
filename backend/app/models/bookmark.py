# backend/app/models/bookmark.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from backend.app.database.db import Base

class Bookmark(Base):
    __tablename__ = 'bookmarks'
    __table_args__ = {'schema': 'user_schema'}
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('user_schema.users.id'), nullable=False)
    book_isbn = Column(String(20), ForeignKey('book_schema.books.isbn'), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="bookmarks")
    book = relationship("Book", back_populates="bookmarks")