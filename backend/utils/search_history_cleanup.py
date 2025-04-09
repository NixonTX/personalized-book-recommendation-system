# backend/app/utils/search_history_cleanup.py
from datetime import datetime, timedelta
from backend.app.database.cache import redis_client

async def cleanup_old_search_history():
    """Remove search history older than 30 days"""
    # Redis automatically expires keys, but we'll clean up very old ones
    cursor = '0'
    while cursor != 0:
        cursor, keys = await redis_client.scan(
            cursor=cursor,
            match="user:*:search_history"
        )
        for key in keys:
            # Remove items older than 35 days (buffer)
            oldest_allowed = (datetime.now() - timedelta(days=35)).timestamp()
            await redis_client.zremrangebyscore(key, 0, oldest_allowed)