# backend/app/models/rating.py
from sqlalchemy import Column, Integer, ForeignKey, DateTime, String
from sqlalchemy.sql import func
from backend.app.database.db import Base
from sqlalchemy.orm import relationship

class Rating(Base):
    __tablename__ = 'ratings'
    __table_args__ = {'schema': 'user_schema'}
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('user_schema.users.id'), nullable=False)
    book_isbn = Column(String(20), ForeignKey('book_schema.books.isbn'), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="ratings")

    book = relationship("Book", back_populates="ratings")
