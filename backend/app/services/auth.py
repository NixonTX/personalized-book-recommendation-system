# backend/app/services/auth.py
from datetime import datetime, timedelta, timezone
from jose import jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..models.user import User, Session
from ..schemas.auth import UserCreate, Token
from ..database.cache import redis_client
from backend.utils.config import settings
import uuid

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

async def authenticate_user(db: AsyncSession, email: str, password: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account not activated")
    return user

async def create_access_token(data: dict, expires_delta: timedelta) -> str:
    to_encode = data.copy()
    to_encode.update({"exp": datetime.now(timezone.utc) + expires_delta, "jti": str(uuid.uuid4())})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

async def create_session(
    db: AsyncSession, user_id: int, ip_address: str, user_agent: str
) -> str:
    session_id = str(uuid.uuid4())
    session = Session(
        id=session_id,
        user_id=user_id,
        ip_address=ip_address,
        user_agent=user_agent,
        created_at=datetime.now(timezone.utc),
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),  # 7-day session
    )
    db.add(session)
    await db.commit()
    return session_id

async def blacklist_token(session_id: str, expiry: int = 86400) -> None:
    """
    Blacklist a token in Redis with a default TTL of 24 hours.
    """
    await redis_client.setex(f"blacklist:{session_id}", expiry, "1")

async def is_token_blacklisted(session_id: str) -> bool:
    """
    Check if a token is blacklisted in Redis.
    """
    return await redis_client.exists(f"blacklist:{session_id}")

async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
    result = await db.execute(
        select(User).where((User.email == user_data.email) | (User.username == user_data.username))
    )
    if result.scalars().first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email or username already exists")

    hashed_password = get_password_hash(user_data.password)
    user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        is_active=False,  # Requires activation (e.g., email verification)
        created_at=datetime.now(timezone.utc),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

async def revoke_session(db: AsyncSession, session_id: str) -> None:
    result = await db.execute(select(Session).where(Session.id == session_id))
    session = result.scalars().first()
    if session:
        await db.delete(session)
        await db.commit()
    await blacklist_token(session_id)