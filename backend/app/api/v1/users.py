from fastapi import APIRouter, Depends, HTTPException
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.schemas.user import UserCreate
from app.services.users import get_user_by_email, create_user
from app.database.db import get_db

router = APIRouter()

@router.post("/users/", response_model=User, status_code=status.HTTP_201_CREATED,
             responses={400: {"description": "Email already registered"}})

async def register_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    db_user = await get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    return await create_user(db, user.model_dump())