import asyncio
from sqlalchemy import text
from backend.app.database.db import engine, Base, init_models

async def initialize_database():
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
        result = await conn.execute(text("""
            SELECT table_schema, table_name 
            FROM information_schema.tables 
            WHERE table_schema IN ('book_schema', 'user_schema')
        """))
        print("Existing tables:")
        for row in result.fetchall():
            print(f"- {row.table_schema}.{row.table_name}") 

if __name__ == "__main__":
    asyncio.run(initialize_database())