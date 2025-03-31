from sqlalchemy import Boolean, Column, Integer, String
from backend.app.database import Base

class User(Base):
    __tablename__ = "users"
    __table_args__ = {'schema': 'user_schema'}

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
