# Pydantic schemas (API validation)
from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, example="johndoe")
    email: EmailStr = Field(..., example="user@example.com")

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, example="securepassword123")

class User(UserBase):
    id: int
    is_active: bool = True

    class Config:
        from_attributes = True