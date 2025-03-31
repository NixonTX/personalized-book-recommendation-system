from sqlalchemy import Column, String, Text
from backend.app.database.db import Base

class Book(Base):
    __tablename__ = "books"
    __table_args__ = {'schema': 'book_schema'}

    isbn = Column(String(20), primary_key=True)
    title = Column(String(100), nullable=False)
    author = Column(String(50))
    description = Column(Text)
    cover_url = Column(String(255))

    # class Config:
    #     from_attributes = True