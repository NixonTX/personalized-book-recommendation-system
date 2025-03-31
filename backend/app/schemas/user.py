from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, example="johndoe")
    email: EmailStr = Field(..., example="user@example.com")

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, example="securepassword123")

class UserResponse(UserBase):  # Renamed from 'User'
    id: int
    is_active: bool
    hashed_password: str  # Add if you need to expose it

    class Config:
        from_attributes = True  # Enables ORM mode