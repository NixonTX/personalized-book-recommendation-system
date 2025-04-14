from contextlib import asynccontextmanager
from fastapi import FastAPI
# Import routers from api/v1
from .api.v1 import recommendations
from backend.app.api.v1 import books
from backend.app.api.v1 import users
from backend.app.api.v1 import ratings, bookmarks, reviews, search, auth
from backend.utils import refresh_popular_books
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncpg
from backend.utils.config import settings
from backend.app.database.db import init_models
from fastapi.middleware.cors import CORSMiddleware

print("🐛 DEBUG: Starting app.py")

try:
    from model.P_R_M.hybrid_model import recommend_books
    print("🐛 DEBUG: Imports successful")
except ImportError as e:
    print(f"❌ Import Error: {e}")
    raise


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

    await refresh_popular_books()  # Initial refresh
    
    # Setup scheduler
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        refresh_popular_books,
        'interval',
        hours=1  # Refresh every hour
    )
    scheduler.start()
    print("🐛 DEBUG: Scheduler started for popular books refresh")
    
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
    allow_origins=['http://localhost:5173'], # Your frontend URL
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PUT"],
    allow_headers=['*'],
)

# app = FastAPI()
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