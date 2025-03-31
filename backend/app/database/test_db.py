# backend/app/database/test_db.py
import asyncio
from sqlalchemy import text
from app.database.db import engine

async def test_connection():
    async with engine.connect() as conn:
        # Set the search path to book_app
        await conn.execute(text("SET search_path TO book_app"))
        
        result = await conn.execute(text("SELECT current_user, current_schema()"))
        row = result.fetchone()
        print("Connection test successful. Current user and schema:")
        print(row)
        
        await conn.execute(text("CREATE TABLE IF NOT EXISTS test_table (id SERIAL PRIMARY KEY)"))
        print("Test table created successfully")
        await conn.execute(text("DROP TABLE IF EXISTS test_table"))
        print("Test table dropped successfully")
        await conn.commit()

if __name__ == "__main__":
    asyncio.run(test_connection())