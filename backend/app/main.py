from contextlib import asynccontextmanager
from datetime import datetime, timezone
from fastapi import FastAPI
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models import user
from backend.app.models.user import Session
# Import routers from api/v1
from .api.v1 import recommendations
from backend.app.api.v1 import books, users, ratings, bookmarks, reviews, search, auth
from backend.utils import refresh_popular_books
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncpg
from backend.utils.config import settings
from backend.app.database.db import init_models, async_session, engine
from fastapi.middleware.cors import CORSMiddleware
import logging

logger = logging.getLogger(__name__)

print("🐛 DEBUG: Starting app.py")

try:
    from model.P_R_M.hybrid_model import recommend_books
    print("🐛 DEBUG: Imports successful")
except ImportError as e:
    print(f"❌ Import Error: {e}")
    raise

async def cleanup_expired_sessions():
    async with async_session() as db:  # Use async_session directly
        try:
            result = await db.execute(
                delete(Session).where(Session.expires_at < datetime.now(timezone.utc))
            )
            await db.commit()
            deleted_count = result.rowcount
            logger.info(f"Cleanup completed: deleted {deleted_count} expired sessions")
        except Exception as e:
            logger.error(f"Cleanup error: {e}")
            await db.rollback()

# Define lifespan handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    print("🐛 DEBUG: Starting up application")

    # Setup pg_trgm extension
    try:
        conn = await asyncpg.connect(dsn=settings.DATABASE_URL.replace("+asyncpg", ""))
        await conn.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
        await conn.close()
        print("🐛 DEBUG: pg_trgm extension setup complete")
    except Exception as e:
        print(f"❌ Error setting up pg_trgm extension: {e}")
        raise

    # Initialize database models
    async with engine.begin() as conn:
        await conn.run_sync(user.Base.metadata.create_all)
    
    # Setup schedulers
    scheduler = AsyncIOScheduler()
    
    # Popular books refresh
    await refresh_popular_books()  # Initial refresh
    scheduler.add_job(
        refresh_popular_books,
        'interval',
        hours=1
    )
    
    # Session cleanup
    scheduler.add_job(
        cleanup_expired_sessions,
        trigger="interval",
        hours=24,
        next_run_time=datetime.now(timezone.utc)
    )
    
    scheduler.start()
    print("🐛 DEBUG: All schedulers started")
    
    try:
        yield  # Application runs here
    finally:
        # Shutdown logic
        print("🐛 DEBUG: Shutting down application")
        scheduler.shutdown()
        print("🐛 DEBUG: Scheduler stopped")

# Create FastAPI app with lifespan
app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:5173'],  # Your frontend URL
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PUT"],
    allow_headers=['*'],
)

print("🐛 DEBUG: FastAPI app created")

# Include routers
app.include_router(recommendations.router, prefix="/api/v1")
app.include_router(books.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(ratings.router, prefix="/api/v1")
app.include_router(bookmarks.router, prefix="/api/v1")
app.include_router(reviews.router, prefix="/api/v1")
app.include_router(search.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Congrats, It Works!"}

if __name__ == "__main__":
    print("🐛 DEBUG: Starting Uvicorn")
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")