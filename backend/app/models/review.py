# backend/app/models/review.py
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import ENUM
from backend.app.database.db import Base
from sqlalchemy.orm import relationship

class Review(Base):
    __tablename__ = 'reviews'
    __table_args__ = {'schema': 'user_schema'}
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('user_schema.users.id'), nullable=False)
    book_isbn = Column(String(20), ForeignKey('book_schema.books.isbn'), nullable=False)
    content = Column(Text, nullable=False)
    rating = Column(Integer, nullable=True)  # Optional but recommended
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_edited = Column(Boolean, default=False)
    status = Column(
        ENUM('pending', 'approved', 'rejected', name='review_status'),
        default='pending'
    )

    # Relationships
    user = relationship("User", back_populates="reviews")
    book = relationship("Book", back_populates="reviews")