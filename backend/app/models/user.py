# backend/app/models/user.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey  # Added ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship  # Make sure this is imported
from backend.app.database.base import Base

class User(Base):
    __tablename__ = "users"
    __table_args__ = {'schema': 'user_schema'}

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True))
    
    # Relationships
    ratings = relationship("Rating", back_populates="user", cascade="all, delete")
    bookmarks = relationship("Bookmark", back_populates="user")
    reviews = relationship("Review", back_populates="user")
    sessions = relationship("Session", back_populates="user", cascade="all, delete")

class Session(Base):
    __tablename__ = "sessions"
    __table_args__ = {'schema': 'user_schema'}
    
    id = Column(UUID(as_uuid=True), primary_key=True)
    user_id = Column(Integer, ForeignKey('user_schema.users.id'))  # Now ForeignKey is defined
    ip_address = Column(String(45))
    user_agent = Column(String)  # Changed from Text to String
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True))
    
    user = relationship("User", back_populates="sessions")