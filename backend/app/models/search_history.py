from sqlalchemy import Column, Index, Integer, String, DateTime
from sqlalchemy.sql import func
from backend.app.database.base import Base

class SearchHistory(Base):
    __tablename__ = "search_history"
    __table_args__ = (
        Index('ix_search_history_user_id', 'user_id'),
        Index('ix_search_history_created_at', 'created_at'),
        {'schema': 'user_schema'}
    )
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    query = Column(String(200), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())