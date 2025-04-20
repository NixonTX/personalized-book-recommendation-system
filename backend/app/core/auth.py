# backend/app/core/auth.py
from datetime import datetime, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from ..schemas.auth import TokenData
from ..models.user import Session, User
from ..database.db import get_db
from backend.utils.config import settings
import logging

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        session_id: str = payload.get("jti")
        if email is None or session_id is None:
            logger.error("Missing email or session_id in token")
            raise credentials_exception
        token_data = TokenData(email=email, session_id=session_id)
    except JWTError as e:
        logger.error(f"JWT decode error: {str(e)}")
        raise credentials_exception

    # Check if token is blacklisted
    from backend.app.services.auth import is_token_blacklisted
    if await is_token_blacklisted(session_id):
        logger.error(f"Token blacklisted: {session_id}")
        raise credentials_exception

    # Check if session exists
    from sqlalchemy import select
    result = await db.execute(
        select(Session).where(Session.id == session_id, Session.expires_at > datetime.now(timezone.utc))
    )
    session = result.scalars().first()
    if not session:
        logger.error(f"Session not found or expired: {session_id}")
        raise credentials_exception

    # Fetch user
    result = await db.execute(select(User).where(User.email == token_data.email))
    user = result.scalars().first()
    if user is None or not user.is_active:
        logger.error(f"User not found or inactive: {token_data.email}")
        raise credentials_exception

    return user