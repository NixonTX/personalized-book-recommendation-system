from sqlalchemy.orm import Session
from sqlalchemy import select
from backend.app.models.user import User
from backend.app.database.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.schemas.user import UserCreate
import bcrypt

async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(User).where(User.email == email))
    return result.scalars().first()

async def create_user(db: AsyncSession, user: UserCreate):
    hashed_password = bcrypt.hashpw(
        user.password.encode('utf-8'),
        bcrypt.gensalt()
    ).decode('utf-8')
    
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user