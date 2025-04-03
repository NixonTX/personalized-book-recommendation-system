# backend/app/services/reviews.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, desc
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from ..models.review import Review
from ..models.book import Book
from ..schemas.review import ReviewCreate, ReviewUpdate, ReviewStatus
from ..database.cache import redis_client

async def create_review(
    db: AsyncSession, 
    user_id: int, 
    review_data: ReviewCreate
):
    # Check if book exists
    book = await db.execute(
        select(Book).where(Book.isbn == review_data.book_isbn))
    if not book.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    
    # Check for existing review
    existing = await db.execute(
        select(Review)
        .where(Review.user_id == user_id)
        .where(Review.book_isbn == review_data.book_isbn)
    )
    if existing.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You've already reviewed this book"
        )
    
    # Create review
    db_review = Review(
        user_id=user_id,
        book_isbn=review_data.book_isbn,
        content=review_data.content,
        rating=review_data.rating,
        status=ReviewStatus.pending
    )
    
    db.add(db_review)
    await db.commit()
    await db.refresh(db_review)
    
    # Invalidate cache
    redis_client.delete(f"book:{review_data.book_isbn}:reviews")
    return db_review

async def update_review(
    db: AsyncSession,
    user_id: int,
    review_id: int,
    review_data: ReviewUpdate
):
    # Get existing review
    result = await db.execute(
        select(Review).where(Review.id == review_id))
    review = result.scalars().first()
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    if review.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only edit your own reviews"
        )
    
    # Update review
    review.content = review_data.content
    review.rating = review_data.rating
    review.is_edited = True
    
    await db.commit()
    await db.refresh(review)
    
    # Invalidate cache
    redis_client.delete(f"book:{review.book_isbn}:reviews")
    return review

async def get_book_reviews(
    db: AsyncSession,
    book_isbn: str,
    page: int = 1,
    per_page: int = 10,
    approved_only: bool = True
):
    # Calculate offset
    offset = (page - 1) * per_page
    
    # Base query
    query = select(Review).where(Review.book_isbn == book_isbn)
    
    if approved_only:
        query = query.where(Review.status == ReviewStatus.approved)
    
    # Get total count
    total = (await db.execute(
        select(func.count()).select_from(query.subquery())
    )).scalar_one()
    
    # Get paginated results
    result = await db.execute(
        query.options(selectinload(Review.user))
        .order_by(desc(Review.created_at))
        .offset(offset)
        .limit(per_page)
    )
    
    return {
        "reviews": result.scalars().all(),
        "total": total,
        "page": page,
        "per_page": per_page
    }

async def delete_review(
    db: AsyncSession,
    user_id: int,
    review_id: int
):
    # Get review
    result = await db.execute(
        select(Review).where(Review.id == review_id))
    review = result.scalars().first()
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    if review.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own reviews"
        )
    
    await db.delete(review)
    await db.commit()
    
    # Invalidate cache
    redis_client.delete(f"book:{review.book_isbn}:reviews")
    return True