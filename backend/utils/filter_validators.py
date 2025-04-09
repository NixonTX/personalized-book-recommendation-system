# backend/app/utils/filter_validators.py
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from sqlalchemy import select
from backend.app.models.book import Book

async def validate_filters(db: AsyncSession, filters: dict):
    """Validate filter values against database"""
    if filters.get('genres'):
        existing_genres = await db.execute(
            select(Book.genre.distinct())
        )
        valid_genres = {g[0].lower() for g in existing_genres if g[0]}
        invalid = set(g.lower() for g in filters['genres']) - valid_genres
        if invalid:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid genres: {', '.join(invalid)}"
            )