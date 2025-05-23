from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.schemas.auth import Token, UserAuth, UserCreate, UserResponse, RefreshTokenRequest

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
from backend.app.models.user import Session, User
from backend.utils.config import settings
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from backend.app.services.verification import create_verification_token, verify_token
from backend.app.services.email import send_verification_email

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

class RevokeSessionRequest(BaseModel):
    session_id: Optional[str] = None
    
router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    user = await create_user(db, user_data)
    token = await create_verification_token(db, user.id)
    try:
        await send_verification_email(user.email, user.username, token)
    except Exception as e:
        print(f"Failed to send verification email: {e}")
    return user

@router.post("/login", response_model=Token)
async def login(
    response: Response,
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

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    session_id = await create_session(
        db, user.id, request.client.host, request.headers.get("User-Agent", "")
    )
    result = await db.execute(select(Session).where(Session.id == session_id))
    session = result.scalars().first()
    if not session:
        logger.error(f"Session {session_id} not found after creation for user {user.email}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Session creation failed")

    access_token = await create_access_token(
        data={"sub": user.email, "jti": session_id}, expires_delta=access_token_expires
    )
    refresh_token = await create_access_token(
        data={"sub": user.email, "jti": session_id},
        expires_delta=timedelta(days=7),
    )

    access_payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    refresh_payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    logger.info(f"Generated tokens - access_jti: {access_payload['jti']}, refresh_jti: {refresh_payload['jti']}")

    response.set_cookie(
        key="accessToken",
        value=access_token,
        httponly=True,
        secure=False,  # Set to False for local testing
        samesite="strict",
        max_age=int(access_token_expires.total_seconds())
    )
    response.set_cookie(
        key="refreshToken",
        value=refresh_token,
        httponly=True,
        secure=False,  # Set to False for local testing
        samesite="strict",
        max_age=7 * 24 * 3600
    )

    user.last_login = datetime.now(timezone.utc)
    await db.commit()
    logger.info(f"Login successful for {user.email}, session: {session_id}, expires_at: {session.expires_at}, ip: {session.ip_address}")

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "username": user.username
    }

@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    response: Response,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        session_id = current_user.session_id
        user_id = current_user.id

        result = await db.execute(
            select(Session).where(Session.id == session_id, Session.user_id == user_id)
        )
        session = result.scalars().first()
        if not session:
            logger.warning(f"Session {session_id} not found for user {current_user.email}")
            response.delete_cookie("accessToken", httponly=True, secure=False, samesite="strict")
            response.delete_cookie("refreshToken", httponly=True, secure=False, samesite="strict")
            logger.info(f"Cleared cookies for user {current_user.email} due to missing session")
            return {"message": "Session already invalid or logged out"}

        await blacklist_token(session_id, expiry=7*24*3600)
        logger.info(f"Blacklisted session {session_id} for user {current_user.email}")
        await db.delete(session)
        await db.commit()
        logger.info(f"Logged out user {current_user.email}, session: {session_id}")

        response.delete_cookie("accessToken", httponly=True, secure=False, samesite="strict")
        response.delete_cookie("refreshToken", httponly=True, secure=False, samesite="strict")
        logger.info(f"Cleared cookies for user {current_user.email} after logout")
        return {"message": "Logged out successfully"}
    except Exception as e:
        logger.error(f"Logout error for user {current_user.email}: {str(e)}")
        await db.rollback()
        response.delete_cookie("accessToken", httponly=True, secure=False, samesite="strict")
        response.delete_cookie("refreshToken", httponly=True, secure=False, samesite="strict")
        logger.info(f"Cleared cookies for user {current_user.email} due to error")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )

@router.post("/refresh", response_model=Token)
async def refresh_token(
    response: Response,
    request: RefreshTokenRequest,
    req: Request,
    db: AsyncSession = Depends(get_db),
):
    refresh_token = request.refresh_token
    logger.info(f"Received refresh request with token: {refresh_token[:10]}...")
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired refresh token",
    )
    try:
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email = payload.get("sub")
        session_id = payload.get("jti")
        iat = payload.get("iat")
        iat_str = datetime.fromtimestamp(iat, timezone.utc).isoformat() if iat else "not set"
        logger.info(f"Decoded payload - email: {email}, session_id: {session_id}, issued_at: {iat_str}")
        if email is None or session_id is None:
            logger.error("Missing email or session_id in token")
            raise credentials_exception
        if await is_token_blacklisted(session_id):
            logger.error(f"Token blacklisted: {session_id}")
            raise credentials_exception
    except JWTError as e:
        logger.error(f"JWT decode error: {e}")
        raise credentials_exception

    result = await db.execute(select(Session).where(Session.id == session_id))
    session = result.scalars().first()
    if not session:
        logger.error(f"Session not found: {session_id}")
        raise credentials_exception
    if session.expires_at < datetime.now(timezone.utc):
        logger.error(f"Session expired: {session_id}, Expires_at: {session.expires_at}")
        await db.delete(session)
        await db.commit()
        raise credentials_exception

    current_ip = req.client.host
    current_user_agent = req.headers.get("User-Agent", "")
    if session.ip_address != current_ip:
        logger.info(f"IP changed for session {session_id}: stored {session.ip_address}, current {current_ip}")
    if session.user_agent != current_user_agent:
        logger.info(f"User-agent changed for session {session_id}: stored {session.user_agent}, current {current_user_agent}")

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    if user is None or not user.is_active:
        logger.error(f"User not found or inactive: {email}")
        await db.delete(session)
        await db.commit()
        raise credentials_exception

    new_session_id = await create_session(db, user.id, current_ip, current_user_agent)
    access_token = await create_access_token(
        data={"sub": user.email, "jti": new_session_id},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    new_refresh_token = await create_access_token(
        data={"sub": user.email, "jti": new_session_id},
        expires_delta=timedelta(days=7),
    )

    try:
        await db.delete(session)
        await db.commit()
        logger.info(f"Deleted old session: {session_id}")
    except Exception as e:
        logger.error(f"Error deleting old session {session_id}: {e}")
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Session update failed")

    response.set_cookie(
        key="accessToken",
        value=access_token,
        httponly=True,
        secure=False,  # Set to False for local testing
        samesite="strict",
        max_age=int(timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES).total_seconds())
    )
    response.set_cookie(
        key="refreshToken",
        value=new_refresh_token,
        httponly=True,
        secure=False,  # Set to False for local testing
        samesite="strict",
        max_age=7 * 24 * 3600
    )

    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
        "username": user.username
    }

@router.post("/sessions/revoke")
async def revoke_session(
    request: RevokeSessionRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    logger.info(f"Revoke request for user {user.email}, session_id: {request.session_id}")
    try:
        if request.session_id:
            result = await db.execute(
                select(Session).where(Session.id == request.session_id, Session.user_id == user.id)
            )
            session = result.scalars().first()
            if not session:
                logger.warning(f"Session {request.session_id} not found for user {user.id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Session not found"
                )
            await blacklist_token(str(session.id), expiry=7*24*3600)
            logger.info(f"Blacklisted session {request.session_id} for user {user.email}")
            await db.delete(session)
            await db.commit()
            logger.info(f"Revoked session {request.session_id} for user {user.email}")
            return {"detail": "Session revoked", "count": 1}
        else:
            current_session_id = user.session_id
            result = await db.execute(
                select(Session).where(Session.user_id == user.id, Session.id != current_session_id)
            )
            sessions = result.scalars().all()
            count = len(sessions)
            for session in sessions:
                await blacklist_token(str(session.id), expiry=7*24*3600)
                logger.info(f"Blacklisted session {session.id} for user {user.email}")
                await db.delete(session)
            await db.commit()
            logger.info(f"Revoked {count} sessions for user {user.email}, kept {current_session_id}")
            return {"detail": "Sessions revoked", "count": count}
    except Exception as e:
        logger.error(f"Revoke error for user {user.email}: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to revoke sessions"
        )

@router.get("/sessions")
async def list_sessions(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    logger.info(f"Listing sessions for user {user.email}")
    try:
        result = await db.execute(
            select(Session).where(
                Session.user_id == user.id,
                Session.expires_at > datetime.now(timezone.utc)
            )
        )
        sessions = result.scalars().all()
        logger.debug(f"Found {len(sessions)} active sessions for user {user.email}")
        return {
            "sessions": [
                {
                    "id": str(session.id),
                    "ip_address": session.ip_address,
                    "user_agent": session.user_agent,
                    "created_at": session.created_at.isoformat(),
                }
                for session in sessions
            ]
        }
    except Exception as e:
        logger.error(f"Error listing sessions for user {user.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list sessions"
        )

@router.get("/verify-email/{token}", response_model=UserResponse)
async def verify_email(token: str, db: AsyncSession = Depends(get_db)):
    user = await verify_token(db, token)
    return user

@router.get("/debug/session/{session_id}")
async def debug_session(session_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Session).where(Session.id == session_id))
    session = result.scalars().first()
    if not session:
        return {"status": "not found", "session_id": session_id}
    return {
        "status": "found",
        "session_id": session_id,
        "user_id": session.user_id,
        "ip_address": session.ip_address,
        "created_at": session.created_at,
        "expires_at": session.expires_at
    }

@router.get("/status")
async def auth_status(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "is_active": current_user.is_active
    }