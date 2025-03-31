import asyncio
import sys
from pathlib import Path
from sqlalchemy import text

sys.path.append(str(Path(__file__).parent.parent.parent))

from app.database.db import engine, Base

async def initialize_database():
    from backend.app.database.db import init_models
    init_models()
    
    async with engine.begin() as conn:
        # Ensure schema exists
        await conn.execute(text("CREATE SCHEMA IF NOT EXISTS book_schema"))
        await conn.execute(text("CREATE SCHEMA IF NOT EXISTS user_schema"))

        # Grant permissions
        await conn.execute(text("GRANT ALL PRIVILEGES ON SCHEMA book_schema TO bookadmin"))
        await conn.execute(text("GRANT ALL PRIVILEGES ON SCHEMA user_schema TO bookadmin"))

        # Create all tables
        await conn.run_sync(Base.metadata.create_all)

        # Set search path for this session
        await conn.execute(text("SET search_path TO book_schema"))
        # # Create tables
        # await conn.run_sync(Base.metadata.create_all)
        result = await conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'book_schema'"))
        print("Book schema tables:", [row[0] for row in result.fetchall()])

if __name__ == "__main__":
    asyncio.run(initialize_database())