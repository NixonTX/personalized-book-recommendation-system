# backend/app/api/v1/reviews.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.schemas.review import (
    ReviewCreate,
    ReviewUpdate,
    ReviewOut,
    PaginatedReviews
)
from backend.app.services.reviews import (
    create_review,
    update_review,
    get_book_reviews,
    delete_review
)
from backend.app.database.db import get_db
from backend.app.core.auth import get_current_user
from backend.app.models.user import User

router = APIRouter(prefix="/reviews", tags=["Reviews"])

@router.post("/", response_model=ReviewOut, status_code=status.HTTP_201_CREATED)
async def create_new_review(
    review: ReviewCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await create_review(db, current_user.id, review)

@router.put("/{review_id}", response_model=ReviewOut)
async def update_existing_review(
    review_id: int,
    review: ReviewUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await update_review(db, current_user.id, review_id, review)

@router.get("/book/{book_isbn}", response_model=PaginatedReviews)
async def get_reviews_for_book(
    book_isbn: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    return await get_book_reviews(db, book_isbn, page, per_page)

@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_review(
    review_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    await delete_review(db, current_user.id, review_id)
    return None