# backend/app/core/auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from ..schemas.auth import TokenData
from ..models.user import User
from ..database.db import get_db
from backend.utils.config import settings

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
            raise credentials_exception
        token_data = TokenData(email=email, session_id=session_id)
    except JWTError:
        raise credentials_exception

    # Check if token is blacklisted
    from backend.app.services.auth import is_token_blacklisted
    if await is_token_blacklisted(session_id):
        raise credentials_exception

    # Fetch user
    from sqlalchemy import select
    result = await db.execute(select(User).where(User.email == token_data.email))
    user = result.scalars().first()
    if user is None or not user.is_active:
        raise credentials_exception

    return user