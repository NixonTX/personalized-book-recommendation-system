from sqlalchemy import Boolean, Column, Integer, String
from backend.app.database import Base
from backend.app.models.rating import Rating
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"
    __table_args__ = {'schema': 'user_schema'}

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)

    ratings = relationship("Rating", back_populates="user", cascade="all, delete")
    bookmarks = relationship("Bookmark", back_populates="user")
    reviews = relationship("Review", back_populates="user")