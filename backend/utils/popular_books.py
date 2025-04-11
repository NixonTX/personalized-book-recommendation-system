# backend/app/utils/popular_books.py
from sqlalchemy import text
from backend.app.database.db import async_session

async def refresh_popular_books():
    async with async_session() as db:
        await db.execute(text("""
            REFRESH MATERIALIZED VIEW CONCURRENTLY 
            book_schema.popular_books
        """))
        await db.commit()