from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.auth import get_current_user
from backend.app.models.user import User
from backend.app.schemas.user import UserCreate, UserResponse
from backend.app.services.users import get_user_by_email, create_user
from backend.app.database.db import get_db

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/users/", response_model=UserResponse, status_code=201)
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    db_user = await get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    created_user = await create_user(db, user)  # Pass UserCreate object directly
    return UserResponse.model_validate(created_user)

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user