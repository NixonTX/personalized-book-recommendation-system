from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from ..models.verification import VerificationToken
from urllib.parse import quote_plus

# SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://bookadmin:0123@localhost/book_recommendation"

DB_USER = "bookadmin"
DB_PASS = "0123"
DB_HOST = "localhost"
DB_NAME = "book_recommendation"

SQLALCHEMY_DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)
Base = declarative_base()

async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def get_db():
    async with async_session() as session:
        yield session

def init_models():
    from backend.app.models.rating import Rating
    from backend.app.models.book import Book
    from backend.app.models.user import User
    from backend.app.models.bookmark import Bookmark
