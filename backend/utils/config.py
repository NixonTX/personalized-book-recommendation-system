# backend/utils/config.py
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://bookadmin:0123@localhost/book_recommendation")
    
    # Redis Configuration
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()