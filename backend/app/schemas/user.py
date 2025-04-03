from pydantic import BaseModel, ConfigDict, Field, EmailStr
from typing import Optional

class UserBase(BaseModel):
    id: int  # Added to match User model
    username: str = Field(..., min_length=3, max_length=50, example="johndoe")
    email: EmailStr = Field(..., example="user@example.com")
    
    model_config = ConfigDict(
        from_attributes=True,  # Replaces old Config class
        populate_by_name=True  # Allows alias mapping
    )

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, example="securepassword123")

class UserResponse(UserBase):  # Renamed from 'User'
    id: int
    is_active: bool
    hashed_password: str  # Add if you need to expose it

    model_config = ConfigDict(
        from_attributes=True,
        extra="ignore"  # Ignores extra fields from ORM
    )