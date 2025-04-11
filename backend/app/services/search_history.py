# backend/app/services/search_history.py
from datetime import datetime, timedelta
from fastapi import HTTPException
from ..database.cache import redis_client
from ..models.search_history import SearchHistory
from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy as sa
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timezone

class SearchHistoryService:
    @staticmethod
    def _normalize_query(query: str) -> str:
        """Normalize search query for storage"""
        return query.strip().lower()[:200]  # Truncate to 200 chars

    @staticmethod
    async def log_search(
        db: AsyncSession,
        user_id: int,
        query: str
    ):
        """Log a search query to history"""
        if not query or len(query) < 2:
            return
        
        normalized = SearchHistoryService._normalize_query(query)
        now = datetime.now(timezone.utc).timestamp()
        
        # Redis operations
        pipe = redis_client.pipeline()
        pipe.zadd(f"user:{user_id}:search_history", {normalized: now})
        pipe.zremrangebyrank(f"user:{user_id}:search_history", 0, -11)  # Keep last 10
        pipe.expire(f"user:{user_id}:search_history", 30 * 24 * 3600)  # 30 days TTL
        await pipe.execute()
        
        # Async DB backup with better error handling
        try:
            db.add(SearchHistory(
                user_id=user_id,
                query=normalized
            ))
            await db.commit()
        except SQLAlchemyError as e:
            await db.rollback()
            # Log the error but don't fail the request
            print(f"Failed to log search history: {str(e)}")

    @staticmethod
    async def get_search_history(
        db: AsyncSession,
        user_id: int
    ):
        """Get user's search history"""
        # Get from Redis first
        history = await redis_client.zrevrange(
            f"user:{user_id}:search_history",
            0, 9,
            withscores=True
        )
        
        # Mark recent searches (last 24h)
        one_day_ago = (datetime.now(timezone.utc) - timedelta(days=1)).timestamp()
        return [
            {
                "query": item[0],
                "timestamp": datetime.fromtimestamp(item[1]),
                "is_recent": item[1] > one_day_ago
            }
            for item in history
        ]

    @staticmethod
    async def clear_search_history(
        db: AsyncSession,
        user_id: int,
        query: str = None
    ):
        """Clear all or specific search history"""
        try:
            if query:
                normalized = SearchHistoryService._normalize_query(query)
                # Redis delete
                await redis_client.zrem(
                    f"user:{user_id}:search_history",
                    normalized
                )
                # Database delete
                await db.execute(
                    sa.delete(SearchHistory.__table__)
                    .where(SearchHistory.user_id == user_id)
                    .where(SearchHistory.query == normalized)
                )
            else:
                # Redis clear all
                await redis_client.delete(f"user:{user_id}:search_history")
                # Database clear all
                await db.execute(
                    sa.delete(SearchHistory.__table__)
                    .where(SearchHistory.user_id == user_id)
                )
            
            await db.commit()
            return {"success": True, "message": "Search history cleared successfully"}
        
        except SQLAlchemyError as e:
            await db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Database error while clearing history: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to clear search history: {str(e)}"
            )