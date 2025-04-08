# backend/app/utils/popular_books.py
from sqlalchemy import text
from backend.app.database.db import AsyncSessionLocal

async def refresh_popular_books():
    async with AsyncSessionLocal() as db:
        await db.execute(text("""
            REFRESH MATERIALIZED VIEW CONCURRENTLY 
            book_schema.popular_books
        """))
        await db.commit()

# Add this to your Celery beat schedule or FastAPI startup events