# backend/app/api/v1/auth.py
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.schemas.auth import Token, UserAuth, UserCreate, UserResponse
from backend.app.services.auth import (
    authenticate_user,
    create_access_token,
    create_session,
    blacklist_token,
    create_user,
    is_token_blacklisted,
)
from backend.app.database.db import get_db
from backend.app.core.auth import get_current_user
from backend.app.models.user import User
from backend.utils.config import settings
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from backend.app.services.verification import create_verification_token, verify_token
from backend.app.services.email import send_verification_email

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    user = await create_user(db, user_data)
    # Generate and send verification email
    token = await create_verification_token(db, user.id)
    try:
        await send_verification_email(user.email, user.username, token)
    except Exception as e:
        # Log error but don't fail registration
        print(f"Failed to send verification email: {e}")
    return user

@router.post("/login", response_model=Token)
async def login(
    form_data: UserAuth,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    user = await authenticate_user(db, form_data.email, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    session_id = await create_session(
        db, user.id, request.client.host, request.headers.get("User-Agent", "")
    )
    access_token = await create_access_token(
        data={"sub": user.email, "jti": session_id}, expires_delta=access_token_expires
    )
    refresh_token = await create_access_token(
        data={"sub": user.email, "jti": session_id},
        expires_delta=timedelta(days=7),  # Longer-lived refresh token
    )

    # Update last login
    user.last_login = datetime.now(timezone.utc)
    await db.commit()

    return Token(access_token=access_token, refresh_token=refresh_token)

@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        session_id = payload.get("jti")
        if session_id:
            await blacklist_token(session_id)
    except jwt.JWTError:
        pass
    return {"message": "Successfully logged out"}

@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str,
    db: AsyncSession = Depends(get_db),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired refresh token",
    )
    try:
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email = payload.get("sub")
        session_id = payload.get("jti")
        if email is None or session_id is None:
            raise credentials_exception
        if await is_token_blacklisted(session_id):
            raise credentials_exception
    except jwt.JWTError:
        raise credentials_exception

    # Verify user
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    if user is None or not user.is_active:
        raise credentials_exception

    # Create new access token
    access_token = await create_access_token(
        data={"sub": user.email, "jti": session_id},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return Token(access_token=access_token, refresh_token=refresh_token)

@router.get("/verify-email/{token}", response_model=UserResponse)
async def verify_email(token: str, db: AsyncSession = Depends(get_db)):
    user = await verify_token(db, token)
    return user