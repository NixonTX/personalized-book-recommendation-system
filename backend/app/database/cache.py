# backend/app/database/cache.py
import redis.asyncio as redis  # Changed to async Redis
from backend.utils.config import settings

redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=0,
    decode_responses=True
)

async def get_cache():
    return redis_client