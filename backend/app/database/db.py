from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://bookadmin:0123@localhost/book_recommendation"

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)
Base = declarative_base()

AsyncSessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

def init_models():
    from app.models.book import Book
    from app.models.user import User

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session