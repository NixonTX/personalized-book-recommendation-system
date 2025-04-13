# backend/app/models/verification.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from backend.app.database.base import Base

class VerificationToken(Base):
    __tablename__ = "verification_tokens"
    __table_args__ = {'schema': 'user_schema'}

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('user_schema.users.id'), nullable=False)
    token = Column(String(36), unique=True, nullable=False)  # UUID as string
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)