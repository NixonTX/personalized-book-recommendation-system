# backend/utils/config.py
import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://bookadmin:0123@localhost/book_recommendation")

    SECRET_KEY: str = "your-secure-secret-key"  # Replace with a strong key
    ALGORITHM: str = "HS256"
    ISSUER: str = "book_recommendation"
    AUDIENCE: str = "api"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))
    REDIS_DB: int = int(os.getenv("REDIS_DB", 0))
    REDIS_BLOCKLIST_PREFIX: str = "blocklist:"

    FRONTEND_URL: str = "http://localhost:5173"

    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str
    SMTP_PASSWORD: str
    EMAIL_SENDER: str

    ENVIRONMENT: str = "development"

    GOOGLE_BOOKS_API_KEY: str
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()