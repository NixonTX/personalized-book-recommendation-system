# backend/app/services/verification.py
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from ..models.verification import VerificationToken
from ..models.user import User
from fastapi import HTTPException, status
import uuid

async def create_verification_token(db: AsyncSession, user_id: int) -> str:
    token = str(uuid.uuid4())
    expires_at = datetime.now(timezone.utc) + timedelta(hours=24)  # 24-hour expiration
    verification_token = VerificationToken(
        user_id=user_id,
        token=token,
        expires_at=expires_at
    )
    db.add(verification_token)
    await db.commit()
    return token

async def verify_token(db: AsyncSession, token: str) -> User:
    # Find token
    result = await db.execute(
        select(VerificationToken).where(VerificationToken.token == token)
    )
    verification_token = result.scalars().first()
    if not verification_token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid or expired token")

    # Check expiration
    if verification_token.expires_at < datetime.now(timezone.utc):
        await db.delete(verification_token)
        await db.commit()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token has expired")

    # Find user
    result = await db.execute(
        select(User).where(User.id == verification_token.user_id)
    )
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Activate user
    user.is_active = True
    await db.delete(verification_token)  # Remove token after use
    await db.commit()
    return user